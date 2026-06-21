"""Tests for WS-5: custom-duration manual run (``run_zone``).

``async_run_zone`` waters one zone for an explicit number of minutes, bypassing
the calculation, the deficit gate and any rain delay. The delivered water is
credited to the bucket via the WS-3 live-run path (marked in ``_live_run_zones``)
rather than zeroed, and the run is logged with ``trigger="manual"``. Coordinators
are built with ``__new__`` so only the touched attributes are wired up.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


class _FakeStore:
    def __init__(self, zones=None):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}
        self.config = SimpleNamespace(
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL
        )

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(
            changes
        )
        return dict(self.zones[int(zone_id)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]


def _coord(monkeypatch, zones=None, units=METRIC_SYSTEM):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = units
    coord.hass = hass
    coord.store = _FakeStore(zones)
    return coord


def _zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 0,
        const.ZONE_BUCKET: -2.0,
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


# --------------------------------------------------------------------------- #
# happy path: override duration, mark for credit, run via parallel
# --------------------------------------------------------------------------- #
async def test_run_zone_overrides_duration_and_marks_credit(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord._irrigate_zones_parallel = AsyncMock()

    await coord.async_run_zone(1, 5)  # 5 minutes

    coord._irrigate_zones_parallel.assert_awaited_once()
    run_list = coord._irrigate_zones_parallel.await_args.args[0]
    assert len(run_list) == 1
    assert run_list[0][const.ZONE_DURATION] == 300  # 5 min -> seconds
    # marked so _reset_zone_bucket_after_run credits delivered depth (not zero)
    assert 1 in coord._live_run_zones
    assert 1 in coord._manual_run_zones
    # original stored zone is untouched (ran a copy)
    assert coord.store.zones[1][const.ZONE_DURATION] == 0


async def test_run_zone_logs_manual_trigger(monkeypatch):
    """The parallel runner logs the run with trigger=manual via _run_trigger."""
    coord = _coord(monkeypatch, zones=[_zone()])
    coord._irrigate_zones_parallel = AsyncMock()

    await coord.async_run_zone(1, 2)
    # _run_trigger consumes the manual marker and reports "manual" once.
    assert coord._run_trigger(1) == "manual"
    # marker is one-shot: a subsequent (scheduled) run reverts to "schedule".
    assert coord._run_trigger(1) == "schedule"


# --------------------------------------------------------------------------- #
# guards: no-op cases
# --------------------------------------------------------------------------- #
async def test_run_zone_zero_duration_noop(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord._irrigate_zones_parallel = AsyncMock()
    await coord.async_run_zone(1, 0)
    coord._irrigate_zones_parallel.assert_not_awaited()


async def test_run_zone_missing_zone_noop(monkeypatch):
    coord = _coord(monkeypatch, zones=[])
    coord._irrigate_zones_parallel = AsyncMock()
    await coord.async_run_zone(99, 5)
    coord._irrigate_zones_parallel.assert_not_awaited()


async def test_run_zone_no_linked_entity_noop(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone(**{const.ZONE_LINKED_ENTITY: None})])
    coord._irrigate_zones_parallel = AsyncMock()
    await coord.async_run_zone(1, 5)
    coord._irrigate_zones_parallel.assert_not_awaited()


async def test_run_zone_disabled_noop(monkeypatch):
    coord = _coord(
        monkeypatch, zones=[_zone(**{const.ZONE_STATE: const.ZONE_STATE_DISABLED})]
    )
    coord._irrigate_zones_parallel = AsyncMock()
    await coord.async_run_zone(1, 5)
    coord._irrigate_zones_parallel.assert_not_awaited()


# --------------------------------------------------------------------------- #
# bucket credit: marked zone gets bucket += delivered (not zeroed)
# --------------------------------------------------------------------------- #
async def test_reset_credits_manual_run(monkeypatch):
    """A manual run credits the delivered depth instead of forcing target."""
    zone = _zone(
        **{
            const.ZONE_BUCKET: -10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 10.0,  # 10 L/min over 10 m^2
            const.ZONE_MAXIMUM_BUCKET: 100.0,
            const.ZONE_DURATION: 300,
        }
    )
    coord = _coord(monkeypatch, zones=[zone])
    coord._live_run_zones = {1}
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord.hass.services = Mock()
    coord.hass.services.async_call = AsyncMock()
    coord.hass.states = Mock()
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    # 5 min * 10 L/min = 50 L over 10 m^2 = 5 mm delivered -> -10 + 5 = -5
    await coord._run_valve_metered(dict(zone), "switch.valve", real_flow=False)
    assert coord.store.zones[1][const.ZONE_BUCKET] == -5.0
