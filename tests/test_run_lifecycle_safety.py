"""Lifecycle safety for schedules and in-progress valve runs (review 2026-07-31).

Three independent defects, all in the "what happens when something ends
unexpectedly" seam that the feature tests never exercise:

R1  ``RecurringScheduleManager`` had no teardown and ``coordinator.async_unload``
    never cancelled its trackers. HA listeners registered by the OLD manager
    survived a config-entry reload still bound to the OLD coordinator, so every
    reload added a second armed copy of every schedule -> N reloads, N+1 firings
    of each schedule (each driving its own coordinator).

R2  No valve-open path guaranteed the valve was closed again. ``turn_off`` sat on
    the happy path inside ``try`` whose ``finally`` only cleared the run marker,
    so any exception (store write, flow-meter arithmetic) or a ``CancelledError``
    at shutdown left the valve PHYSICALLY OPEN with nothing scheduled to close
    it. There is no other net: ``async_unload`` does not stop runs.

R3  Irrigation was dispatched with bare ``asyncio.create_task``. The event loop
    keeps only a weak reference to a task, so a run could be garbage-collected
    mid-execution, and the tasks were invisible to HA's shutdown handling.
    ``hass.async_create_task`` is tracked, cancelled on shutdown and logs
    exceptions.

Coordinators are built with ``__new__`` so only the touched attributes are wired,
matching tests/test_stop_zone.py and tests/test_rain_delay.py.
"""

import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.scheduler import RecurringScheduleManager


class _FakeStore:
    def __init__(self, zones=None, config=None):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}
        self.config = config or SimpleNamespace(
            rain_delay_until=None,
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
            live_estimate_enabled=False,
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

    async def async_get_distributors(self):
        return []


def _coord(monkeypatch, zones=None, config=None, units=METRIC_SYSTEM):
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
    # Swallow the coroutine so an un-awaited-coroutine warning can't mask a failure.
    hass.async_create_task = Mock(side_effect=lambda coro, *a, **k: coro.close())
    coord.hass = hass
    coord.store = _FakeStore(zones, config)
    coord._live_run_zones = set()
    return coord


def _timed_zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 300,
        const.ZONE_SIZE: 100.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_BUCKET_THRESHOLD: 0.0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


def _turn_off_calls(hass):
    return [
        c
        for c in hass.services.async_call.call_args_list
        if len(c.args) >= 2 and c.args[1] == "turn_off"
    ]


# --------------------------------------------------------------------------- #
# R1 — scheduler teardown on unload
# --------------------------------------------------------------------------- #
def _unloadable_coord():
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.data = {const.DOMAIN: {}}
    coord.hass = hass
    coord._pending_track_update_unsub = None
    coord._track_auto_update_time_unsub = None
    coord._track_auto_calc_time_unsub = None
    coord._track_midnight_time_unsub = None
    coord._track_buffer_flush_unsub = None
    coord.async_teardown_observed_watering = Mock()
    coord._dist_inlet_watchers = {}
    coord._subscriptions = []
    return coord


@pytest.mark.asyncio
async def test_manager_unload_cancels_every_tracker_and_the_rearm():
    """The manager must release every HA listener it registered."""
    manager = RecurringScheduleManager(Mock(), Mock())
    daily, sunrise = Mock(), Mock()
    manager._schedule_trackers = {"daily": daily, "sunrise": sunrise}
    manager._unsub_rearm = Mock()
    manager._finish_last_target = {"daily": "2026-07-31T06:00:00+00:00"}
    rearm = manager._unsub_rearm

    await manager.async_unload()

    daily.assert_called_once_with()
    sunrise.assert_called_once_with()
    rearm.assert_called_once_with()
    assert manager._schedule_trackers == {}
    assert manager._unsub_rearm is None
    # Everything else is released; the fired-occurrence record is deliberately
    # NOT. It is what stops a reload inside a finish schedule's start->finish
    # window from watering the same occurrence a second time, and clearing it
    # here would also let a persistence task created just before teardown write
    # an emptied map back to the store. See
    # tests/test_schedule_fired_occurrence_persistence.py.
    assert manager._finish_last_target == {"daily": "2026-07-31T06:00:00+00:00"}


@pytest.mark.asyncio
async def test_manager_unload_tolerates_none_trackers():
    """A tracker slot can legitimately hold None (setup returned no handle)."""
    manager = RecurringScheduleManager(Mock(), Mock())
    manager._schedule_trackers = {"broken": None}
    manager._unsub_rearm = None
    await manager.async_unload()  # must not raise
    assert manager._schedule_trackers == {}


@pytest.mark.asyncio
async def test_coordinator_unload_tears_down_the_schedule_manager():
    """R1 regression: without this, a reload leaves the old trackers armed and
    every schedule fires once per surviving manager."""
    coord = _unloadable_coord()
    manager = RecurringScheduleManager(Mock(), coord)
    tracker = Mock()
    manager._schedule_trackers = {"daily": tracker}
    manager._unsub_rearm = Mock()
    rearm = manager._unsub_rearm
    coord.recurring_schedule_manager = manager

    await coord.async_unload()

    tracker.assert_called_once_with()
    rearm.assert_called_once_with()


@pytest.mark.asyncio
async def test_coordinator_unload_survives_a_missing_schedule_manager():
    """Unload must never fail the config-entry unload (failed_unload is only
    recoverable by a full HA restart)."""
    coord = _unloadable_coord()
    await coord.async_unload()  # no recurring_schedule_manager attribute at all


# --------------------------------------------------------------------------- #
# R2 — the valve is always closed
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_metered_run_closes_valve_when_the_loop_raises(monkeypatch):
    """R2 regression: an exception mid-run must not strand the valve open."""
    coord = _coord(monkeypatch, zones=[_timed_zone()])
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord._sleep_or_stopped = AsyncMock(side_effect=RuntimeError("store exploded"))

    with pytest.raises(RuntimeError):
        await coord._run_valve_metered(_timed_zone(), "switch.valve", real_flow=False)

    assert _turn_off_calls(coord.hass), "valve was left open after a mid-run error"


@pytest.mark.asyncio
async def test_metered_run_closes_valve_on_cancellation(monkeypatch):
    """Shutdown/reload cancels the run task; the valve must still close."""
    coord = _coord(monkeypatch, zones=[_timed_zone()])
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord._sleep_or_stopped = AsyncMock(side_effect=asyncio.CancelledError())

    with pytest.raises(asyncio.CancelledError):
        await coord._run_valve_metered(_timed_zone(), "switch.valve", real_flow=False)

    assert _turn_off_calls(coord.hass), "valve was left open after cancellation"


@pytest.mark.asyncio
async def test_metered_run_closes_the_valve_exactly_once_on_the_happy_path(
    monkeypatch,
):
    """Guard against the obvious fix regressing into a double turn_off."""
    coord = _coord(monkeypatch, zones=[_timed_zone(**{const.ZONE_DURATION: 1})])
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord._sleep_or_stopped = AsyncMock(return_value=False)

    await coord._run_valve_metered(
        _timed_zone(**{const.ZONE_DURATION: 1}), "switch.valve", real_flow=False
    )

    assert len(_turn_off_calls(coord.hass)) == 1


@pytest.mark.asyncio
async def test_flow_slot_closes_valve_when_the_loop_raises(monkeypatch):
    """The rotating path's flow slot has the same exposure."""
    zone = _timed_zone(**{const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, zones=[zone])
    coord._read_flow_sample = Mock(side_effect=RuntimeError("sensor exploded"))

    with pytest.raises(RuntimeError):
        await coord._irrigate_zone_flow_slot(zone, "switch.valve", 60.0, 10.0)

    assert _turn_off_calls(coord.hass), "flow slot left the valve open"


# --------------------------------------------------------------------------- #
# R3 — irrigation runs are tracked tasks
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_sequential_dispatch_uses_a_tracked_task(monkeypatch):
    """R3 regression: a bare asyncio.create_task is GC-able mid-run and invisible
    to HA shutdown."""
    config = SimpleNamespace(
        rain_delay_until=None,
        zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
        live_estimate_enabled=False,
    )
    coord = _coord(monkeypatch, zones=[_timed_zone()], config=config)
    coord._apply_live_durations = AsyncMock(side_effect=lambda zs: zs)
    coord._apply_soil_moisture_veto = AsyncMock(side_effect=lambda zs: zs)
    coord._sc_is_self_closing = Mock(return_value=False)
    coord.async_master_begin_cycle = AsyncMock()
    coord.async_master_schedule_off = AsyncMock()
    coord._master_note_run = Mock()

    assert await coord._irrigate_linked_entities() is True
    coord.hass.async_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_parallel_dispatch_uses_tracked_tasks(monkeypatch):
    coord = _coord(monkeypatch, zones=[_timed_zone()])
    await coord._irrigate_zones_parallel([_timed_zone()])
    coord.hass.async_create_task.assert_called_once()


# --------------------------------------------------------------------------- #
# R4 — master/pump stays on for the whole cycle
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_sequential_dispatch_leaves_a_master_hold_behind(monkeypatch):
    """The scheduled path must hand the run a master HOLD, not a predicted window.

    The dispatcher's own cycle hold is released when it returns; the sequencing
    task's hold must outlive it, or the pump would switch off the moment dispatch
    finished — regardless of how long the zones actually take.
    """
    config = SimpleNamespace(
        rain_delay_until=None,
        zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
        live_estimate_enabled=False,
        master_entity="switch.pump",
        master_off_after=True,
        master_settle_seconds=0,
        master_kick_enabled=False,
        master_kick_pause_seconds=0,
    )
    zones = [
        _timed_zone(**{const.ZONE_ID: 1, const.ZONE_DURATION: 300}),
        _timed_zone(**{const.ZONE_ID: 2, const.ZONE_DURATION: 300}),
        _timed_zone(**{const.ZONE_ID: 3, const.ZONE_DURATION: 300}),
    ]
    coord = _coord(monkeypatch, zones=zones, config=config)
    coord._apply_live_durations = AsyncMock(side_effect=lambda zs: zs)
    coord._apply_soil_moisture_veto = AsyncMock(side_effect=lambda zs: zs)
    coord._sc_is_self_closing = Mock(return_value=False)
    coord.async_master_schedule_off = AsyncMock()

    await coord._irrigate_linked_entities()

    holds = coord.master_holds()
    assert any(
        t.startswith("seq:") for t in holds
    ), f"sequencing task holds no master token: {holds}"
    assert not any(
        t.startswith("cycle:") for t in holds
    ), "dispatch hold should be released once the work holds its own"


@pytest.mark.asyncio
async def test_master_stays_up_while_any_hold_remains(monkeypatch):
    """The off-timer firing early is now harmless — the whole point of holds."""
    coord = _coord(monkeypatch)
    coord.store.config.master_entity = "switch.pump"
    coord.store.config.master_off_after = True
    coord._master_holds = {"zone:1"}
    coord._master_turn = AsyncMock()
    coord._master_off_deadline = coord._master_now() - timedelta(seconds=1)
    captured = {}

    def _capture(hass, delay, cb):
        captured["cb"] = cb
        return lambda: None

    monkeypatch.setattr(
        "custom_components.irrigation_plus.master.async_call_later", _capture
    )

    await coord.async_master_schedule_off()
    # Deadline is already in the past: without holds this would power the master
    # off. The hold must veto it.
    await captured["cb"](None)

    coord._master_turn.assert_not_awaited()


@pytest.mark.asyncio
async def test_releasing_the_last_hold_collapses_a_stale_prediction(monkeypatch):
    """A leftover over-long deadline must not keep the pump running once nothing
    holds the master — collapsing it is what fixes the dead-heading."""
    coord = _coord(monkeypatch)
    coord.store.config.master_entity = "switch.pump"
    coord.store.config.master_off_after = True
    coord._master_holds = {"zone:1"}
    coord.async_master_schedule_off = AsyncMock()
    far_future = coord._master_now() + timedelta(hours=4)
    coord._master_off_deadline = far_future

    await coord.async_master_release("zone:1")

    assert coord._master_off_deadline < far_future
    assert coord._master_off_deadline <= coord._master_now() + timedelta(
        seconds=const.MASTER_RELEASE_GRACE_SECONDS + 1
    )


@pytest.mark.asyncio
async def test_release_with_other_holds_outstanding_keeps_the_deadline(monkeypatch):
    """Only the LAST release may collapse; otherwise a finishing zone would cut
    the pump under a zone still running."""
    coord = _coord(monkeypatch)
    coord.store.config.master_entity = "switch.pump"
    coord._master_holds = {"zone:1", "zone:2"}
    coord.async_master_schedule_off = AsyncMock()
    far_future = coord._master_now() + timedelta(hours=4)
    coord._master_off_deadline = far_future

    await coord.async_master_release("zone:1")

    assert coord._master_off_deadline == far_future
    coord.async_master_schedule_off.assert_not_awaited()
