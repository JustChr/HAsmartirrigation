"""A ``valve.*`` entity is opened with ``open_valve``, never ``turn_on`` (#170).

Home Assistant's ``valve`` domain registers ``open_valve`` / ``close_valve`` /
``toggle`` and nothing else, so the ``<domain>.turn_on`` the zone runner used to
build raised ``ServiceNotFound`` and a classic zone linked to a valve never
watered. The zone form offers ``valve`` in its entity picker, so this was every
such zone, on every path.

The service double below is built from the actions HA actually registers, not
from what the runner calls: an actuation that picks the wrong action raises
``ServiceNotFound`` exactly as it did on the reporter's install, instead of being
recorded by a permissive ``AsyncMock`` and passing. Each runner path that opens
or closes a zone valve has its own test here.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.exceptions import ServiceNotFound
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.actuate import actuation_service

from .test_distributor import _host as _dist_host
from .test_master import _mcoord

VALVE = "valve.gardena_ventil_1"

# What Home Assistant registers for each domain Irrigation Plus actuates.
_HA_SERVICES = {
    "switch": {"turn_on", "turn_off", "toggle"},
    "input_boolean": {"turn_on", "turn_off", "toggle"},
    "valve": {
        "open_valve",
        "close_valve",
        "set_valve_position",
        "stop_valve",
        "toggle",
    },
}


class _Services:
    """``hass.services`` that only knows the actions HA really registers."""

    def __init__(self, on_call=None):
        self.calls = []
        self._on_call = on_call

    async def async_call(self, domain, service, data=None, **_kw):
        if service not in _HA_SERVICES.get(domain, ()):
            raise ServiceNotFound(domain, service)
        self.calls.append((domain, service, (data or {}).get("entity_id")))
        if self._on_call is not None:
            self._on_call(domain, service)


class _FakeStore:
    def __init__(self, zones):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.config = SimpleNamespace(
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
            zone_sequencing_max_consecutive_duration=5,
            zone_sequencing_min_absorption_time=0,
        )

    def get_zone(self, zid):
        z = self.zones.get(int(zid))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zid, changes):
        self.zones.setdefault(int(zid), {const.ZONE_ID: int(zid)}).update(changes)
        return dict(self.zones[int(zid)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]


def _zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Rasen",
        const.ZONE_LINKED_ENTITY: VALVE,
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,  # 10 L/min over 10 m² == 1 mm/min
        const.ZONE_DURATION: 300,
        const.ZONE_MAXIMUM_DURATION: 36000,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


def _coord(monkeypatch, zones, *, flow_rate=None):
    monkeypatch.setattr(
        "custom_components.irrigation_plus.irrigation.async_dispatcher_send", Mock()
    )
    monkeypatch.setattr(
        "custom_components.irrigation_plus.irrigation.asyncio.sleep", AsyncMock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.loop = asyncio.get_event_loop()
    hass.services = _Services()
    hass.states = Mock()
    if flow_rate is None:
        hass.states.get = Mock(return_value=None)
    else:
        state = Mock()
        state.state = str(flow_rate)
        state.attributes = {"unit_of_measurement": "L/min"}
        hass.states.get = Mock(return_value=state)
    coord.hass = hass
    coord.store = _FakeStore(zones)
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord._live_run_zones = set()
    return coord


def _valve_calls(coord):
    return [c for c in coord.hass.services.calls if c[2] == VALVE]


_OPEN_CLOSE = [("valve", "open_valve", VALVE), ("valve", "close_valve", VALVE)]


# --------------------------------------------------------------------------- #
# The rule
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("entity", "on", "expected"),
    [
        ("valve.v", True, ("valve", "open_valve")),
        ("valve.v", False, ("valve", "close_valve")),
        ("switch.v", True, ("switch", "turn_on")),
        ("switch.v", False, ("switch", "turn_off")),
        ("input_boolean.v", True, ("input_boolean", "turn_on")),
        ("input_boolean.v", False, ("input_boolean", "turn_off")),
    ],
)
def test_actuation_service_per_domain(entity, on, expected):
    assert actuation_service(entity, on) == expected
    # Every answer is an action HA actually registers for that domain.
    domain, service = expected
    assert service in _HA_SERVICES[domain]


# --------------------------------------------------------------------------- #
# Zone runner paths
# --------------------------------------------------------------------------- #
async def test_timed_run_opens_and_closes_a_valve(monkeypatch):
    """The reporter's case: a classic timed zone on a valve waters to target."""
    coord = _coord(monkeypatch, [_zone()])
    await coord._run_valve_metered(_zone(), VALVE, real_flow=False)
    assert _valve_calls(coord) == _OPEN_CLOSE
    assert coord.store.zones[1][const.ZONE_BUCKET] == pytest.approx(0.0)


async def test_flow_run_opens_and_closes_a_valve(monkeypatch):
    z = _zone(**{const.ZONE_BUCKET: -2.0, const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, [z], flow_rate=20)
    await coord._run_valve_metered(dict(z), VALVE, real_flow=True)
    assert _valve_calls(coord) == _OPEN_CLOSE


async def test_a_run_that_raises_after_the_open_still_closes_the_valve(monkeypatch):
    """The cleanup close uses the valve's own action too, or it strands the valve
    open exactly when the run has already gone wrong."""
    coord = _coord(monkeypatch, [_zone()])
    coord._confirm_valve_running = AsyncMock(side_effect=RuntimeError("boom"))
    with pytest.raises(RuntimeError):
        await coord._irrigate_zones_rotating([_zone()])
    assert _valve_calls(coord) == _OPEN_CLOSE


async def test_rotating_timed_slot_opens_and_closes_a_valve(monkeypatch):
    coord = _coord(monkeypatch, [_zone()])
    await coord._irrigate_zones_rotating([_zone()])
    calls = _valve_calls(coord)
    assert calls and calls[0] == _OPEN_CLOSE[0] and calls[-1] == _OPEN_CLOSE[1]
    assert {c[1] for c in calls} == {"open_valve", "close_valve"}


async def test_rotating_flow_slot_opens_and_closes_a_valve(monkeypatch):
    z = _zone(**{const.ZONE_BUCKET: -2.0, const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, [z], flow_rate=20)
    await coord._irrigate_zones_rotating([dict(z)])
    calls = _valve_calls(coord)
    assert calls and calls[0] == _OPEN_CLOSE[0] and calls[-1] == _OPEN_CLOSE[1]
    assert {c[1] for c in calls} == {"open_valve", "close_valve"}


async def test_confirm_retry_resends_open_valve(monkeypatch):
    monkeypatch.setattr(const, "VALVE_CONFIRM_TIMEOUT", 4)
    monkeypatch.setattr(const, "VALVE_CONFIRM_RETRY_AT", 2)
    coord = _coord(monkeypatch, [_zone()])
    del coord._confirm_valve_running  # the real poll, not the stub
    state = SimpleNamespace(state="closed", attributes={})
    coord.hass.states.get = lambda eid: state if eid == VALVE else None

    def _opens(domain, service):
        if service == "open_valve":
            state.state = "open"

    coord.hass.services = _Services(on_call=_opens)
    assert await coord._confirm_valve_running(1, VALVE) is True
    assert _valve_calls(coord) == [_OPEN_CLOSE[0]]


async def test_stop_zone_closes_a_valve(monkeypatch):
    coord = _coord(monkeypatch, [_zone()])
    await coord.async_stop_zone(1)
    assert _valve_calls(coord) == [_OPEN_CLOSE[1]]


# --------------------------------------------------------------------------- #
# Master and distributor inlet (they carried their own copy of the rule)
# --------------------------------------------------------------------------- #
async def test_master_valve_opens_and_closes():
    c = _mcoord(master_entity=VALVE)
    c.hass.services = _Services()
    await c._master_turn(True)
    await c._master_turn(False)
    assert c.hass.services.calls == _OPEN_CLOSE


async def test_distributor_valve_inlet_opens_and_closes():
    c = _dist_host()
    c.hass.services = _Services()
    await c._dist_domain_turn(VALVE, True)
    await c._dist_domain_turn(VALVE, False)
    assert c.hass.services.calls == _OPEN_CLOSE
