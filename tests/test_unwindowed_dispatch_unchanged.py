"""The ordering engine changes nothing on a run that has no window.

``run_window.rank`` and ``run_window.select`` decide the priority order and the
membership of a *fitted* run. Neither is consulted anywhere else: the ordinary
dispatch path walks the zones in store order and waters every one that is due,
exactly as it did before the engine existed.

That is a property, not a detail of how the gate is spelled, so the tests below
assert it against the real dispatch entry point rather than against the call
graph. Each fixture is built so that ``rank``/``select`` would give a visibly
different answer, and asserts that difference first: without that guard a
degenerate fixture (one zone, equal ratios, a window nothing is cut by) would
let these pass while the engine quietly reordered every install.
"""

from types import SimpleNamespace
from unittest.mock import Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.run_window import rank, select


class _FakeStore:
    def __init__(self, zones, config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.config = config

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zone_id, changes):
        self.zones[int(zone_id)].update(changes)
        return dict(self.zones[int(zone_id)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_get_distributors(self):
        return []


def _cfg(**over):
    base = dict(
        rain_delay_until=None,
        zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
        zone_sequencing_max_consecutive_duration=5,
        zone_sequencing_min_absorption_time=0,
        live_estimate_enabled=False,
        log_no_demand=False,
    )
    base.update(over)
    return SimpleNamespace(**base)


def _zone(zone_id, duration, bucket):
    """A due, linked, classic zone. ``bucket`` alone sets its depletion ratio."""
    return {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: f"Zone {zone_id}",
        const.ZONE_LINKED_ENTITY: f"switch.valve_{zone_id}",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: duration,
        const.ZONE_BUCKET: bucket,
        const.ZONE_BUCKET_THRESHOLD: -1.0,
        const.ZONE_RUN_LOG: [],
    }


# Store order 1, 2, 3; depletion ratios 1.2, 2.0, 5.0. Ranking is driest first,
# so it inverts the store order outright rather than merely permuting it.
def _zones():
    return [
        _zone(1, 300, -1.2),
        _zone(2, 600, -2.0),
        _zone(3, 900, -5.0),
    ]


def _coord(monkeypatch, zones, config=None):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    coord.hass = hass
    coord.store = _FakeStore(zones, config or _cfg())
    return coord


def _capture_dispatch(monkeypatch, coord):
    """Replace the dispatcher with a recorder, returning the captured ids."""
    dispatched = []

    async def _fake(zones, *, trigger, **kw):
        dispatched.extend(int(z[const.ZONE_ID]) for z in zones)

    monkeypatch.setattr(coord, "_dispatch_by_mode", _fake)
    return dispatched


async def test_the_run_keeps_store_order_and_the_ranking_would_not(monkeypatch):
    coord = _coord(monkeypatch, _zones())
    plan = await coord.async_plan_zone_runs()

    # The engine's answer for this fixture, so the assertion below is a real
    # difference rather than a coincidence.
    assert [r.zone_id for r in rank(plan)] == [3, 2, 1]

    dispatched = _capture_dispatch(monkeypatch, coord)
    assert await coord._irrigate_linked_entities("all") is True
    assert dispatched == [1, 2, 3]


async def test_the_run_drops_no_zone_that_selection_would_have_cut(monkeypatch):
    coord = _coord(monkeypatch, _zones())
    plan = await coord.async_plan_zone_runs()

    # A window that fits only the driest zone. Sequential, so the three zones
    # need 1800 s of wall clock between them and 900 s admits exactly one.
    chosen = select(
        plan,
        window_seconds=900,
        sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
        max_slot_seconds=300,
        min_absorption_seconds=0,
    )
    assert [r.zone_id for r in chosen] == [3]

    dispatched = _capture_dispatch(monkeypatch, coord)
    assert await coord._irrigate_linked_entities("all") is True
    assert dispatched == [1, 2, 3]


async def test_a_schedules_zone_target_still_decides_membership(monkeypatch):
    """The one thing that does restrict an unwindowed run is the schedule's own
    zone list, and it restricts it without reordering what is left."""
    coord = _coord(monkeypatch, _zones())
    dispatched = _capture_dispatch(monkeypatch, coord)
    assert await coord._irrigate_linked_entities([3, 1]) is True
    assert dispatched == [1, 3]
