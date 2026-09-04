"""Tests for the Stop action (issue #36 follow-up).

``async_stop_zone`` interrupts an in-progress run immediately: it sets the run's
stop event (so the metered/rotating loop breaks, commits the water delivered so
far and logs a *partial* run) and turns the linked valve off directly as a
safety net. ``get_active_runs`` exposes the in-progress runs (with a countdown
end for time-bounded runs) so the dashboard can show a Stop control + countdown.

Coordinators are built with ``__new__`` so only the touched attributes are wired.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from homeassistant.util import dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const


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
        "custom_components.irrigation_plus.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = units
    hass.loop = asyncio.get_event_loop()
    hass.services = Mock()
    hass.services.async_call = AsyncMock()
    hass.states = Mock()
    coord.hass = hass
    coord.store = _FakeStore(zones)
    return coord


def _zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 300,
        const.ZONE_BUCKET: -2.0,
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


# --------------------------------------------------------------------------- #
# active-run registry
# --------------------------------------------------------------------------- #
def test_register_active_run_exposes_countdown_end(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord._register_active_run(1, 600, has_end=True)
    runs = coord.get_active_runs()
    assert "1" in runs
    assert runs["1"]["ends_at"] is not None  # time-bounded → countdown
    assert runs["1"]["started_at"] is not None


def test_flow_run_has_no_countdown_end(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord._register_active_run(1, 0, has_end=False)
    assert coord.get_active_runs()["1"]["ends_at"] is None


def test_unregister_active_run_clears_marker(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord._register_active_run(1, 600, has_end=True)
    coord._unregister_active_run(1)
    assert coord.get_active_runs() == {}


# --------------------------------------------------------------------------- #
# async_stop_zone
# --------------------------------------------------------------------------- #
async def test_stop_zone_sets_event_and_turns_off(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    event = coord._register_active_run(1, 600, has_end=True)

    await coord.async_stop_zone(1)

    assert event.is_set()  # loop will notice and finish the run
    coord.hass.services.async_call.assert_awaited_once_with(
        "switch", "turn_off", {"entity_id": "switch.valve"}
    )


async def test_stop_zone_without_tracked_run_still_turns_off(monkeypatch):
    """Safety net: an untracked valve (e.g. opened pre-restart) is still closed."""
    coord = _coord(monkeypatch, zones=[_zone()])
    await coord.async_stop_zone(1)
    coord.hass.services.async_call.assert_awaited_once_with(
        "switch", "turn_off", {"entity_id": "switch.valve"}
    )


async def test_stop_all_zones_stops_each(monkeypatch):
    coord = _coord(
        monkeypatch,
        zones=[
            _zone(),
            _zone(**{const.ZONE_ID: 2, const.ZONE_LINKED_ENTITY: "switch.v2"}),
        ],
    )
    e1 = coord._register_active_run(1, 600, has_end=True)
    e2 = coord._register_active_run(2, 600, has_end=True)
    await coord.async_stop_all_zones()
    assert e1.is_set() and e2.is_set()


# --------------------------------------------------------------------------- #
# issue #83: a self-closing run is invisible to the dashboard
#
# A self-closing run never enters the in-memory _active_runs registry — it is
# fire-and-forget and lives in the persisted CONF_ACTIVE_VALVE_RUNS list. The
# panel drives the Stop control AND the countdown off get_active_runs(), so
# leaving the persisted half out made a watering zone look completely idle.
# --------------------------------------------------------------------------- #
def _sc_record(**over):
    rec = {
        const.RUN_ZONE_ID: 1,
        const.RUN_STARTED: "2026-08-12T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_MODE: const.WATERING_MODE_SERVICE,
    }
    rec.update(over)
    return rec


def test_self_closing_run_is_reported_with_a_countdown(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord.store.config.active_valve_runs = [_sc_record()]

    runs = coord.get_active_runs()

    assert "1" in runs, "a running self-closing zone must reach the dashboard"
    assert runs["1"]["started_at"].startswith("2026-08-12T")
    # 600 s after the start, so the panel can count down.
    assert runs["1"]["ends_at"] is not None
    assert runs["1"]["ends_at"] > runs["1"]["started_at"]


def test_queued_opensprinkler_run_has_no_countdown_but_is_still_listed(monkeypatch):
    """RUN_STARTED is the DISPATCH time for an OpenSprinkler run, and the
    controller may not have started the station yet, so there is no finish to
    count down to — but the zone must still offer Stop. Mirrors the rule in
    _sc_run_elapsed."""
    coord = _coord(monkeypatch, zones=[_zone()])
    coord.store.config.active_valve_runs = [
        _sc_record(**{const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER})
    ]

    runs = coord.get_active_runs()

    assert "1" in runs
    assert runs["1"]["ends_at"] is None


def test_observed_start_wins_over_dispatch_for_an_opensprinkler_run(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord.store.config.active_valve_runs = [
        _sc_record(
            **{
                const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER,
                const.RUN_OBSERVED_START: "2026-08-12T08:30:00+00:00",
            }
        )
    ]

    runs = coord.get_active_runs()

    # Instant-equality, not string matching: the payload is rendered local.
    assert dt_util.parse_datetime(runs["1"]["started_at"]) == dt_util.parse_datetime(
        "2026-08-12T08:30:00+00:00"
    )
    assert runs["1"]["ends_at"] is not None  # the station is watering now


def test_live_registry_entry_is_not_shadowed_by_a_persisted_record(monkeypatch):
    coord = _coord(monkeypatch, zones=[_zone()])
    coord._register_active_run(1, 600, has_end=True)
    live = coord.get_active_runs()["1"]["started_at"]
    coord.store.config.active_valve_runs = [_sc_record()]

    assert coord.get_active_runs()["1"]["started_at"] == live


def test_a_mock_config_does_not_leak_into_the_payload(monkeypatch):
    """A test double's bare Mock() answers every attribute with another Mock;
    iterating that as the run list would blow up the whole dashboard payload."""
    coord = _coord(monkeypatch, zones=[_zone()])
    coord.store.config = Mock()

    assert coord.get_active_runs() == {}


async def test_stop_all_zones_reaches_a_self_closing_zone(monkeypatch):
    """The second symptom of #83, and the worse one: "stop all" iterated the
    in-memory registry only, so it reported success while leaving every
    self-closing valve open."""
    coord = _coord(
        monkeypatch,
        zones=[_zone(**{const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE})],
    )
    coord.store.config.active_valve_runs = [_sc_record()]
    coord.async_stop_self_closing = AsyncMock(return_value=True)
    coord._os_drop_from_cycle = Mock()

    await coord.async_stop_all_zones()

    coord.async_stop_self_closing.assert_awaited_once_with(1)


# --------------------------------------------------------------------------- #
# stopping interrupts a metered run → partial + delivered water credited
# --------------------------------------------------------------------------- #
async def test_metered_run_stops_early_records_partial(monkeypatch):
    zone = _zone(
        **{
            const.ZONE_BUCKET: -10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_MAXIMUM_BUCKET: 100.0,
            const.ZONE_DURATION: 600,
        }
    )
    coord = _coord(monkeypatch, zones=[zone])
    coord._confirm_valve_running = AsyncMock(return_value=True)
    monkeypatch.setattr(
        "custom_components.irrigation_plus.irrigation.asyncio.sleep", AsyncMock()
    )

    # Stop as soon as the run registers its marker: the first poll then reports
    # stopped and the loop breaks.
    orig_register = coord._register_active_run

    def _register_then_stop(zid, dur, *, has_end):
        ev = orig_register(zid, dur, has_end=has_end)
        ev.set()
        return ev

    coord._register_active_run = _register_then_stop

    await coord._run_valve_metered(dict(zone), "switch.valve", real_flow=False)

    # Run was logged as a partial with the "stopped" detail.
    log = coord.store.zones[1][const.ZONE_RUN_LOG]
    assert log[0]["result"] == const.RUN_RESULT_PARTIAL
    assert log[0]["detail"] == const.RUN_DETAIL_STOPPED
    # The in-progress marker is cleared once the run finishes.
    assert coord.get_active_runs() == {}
