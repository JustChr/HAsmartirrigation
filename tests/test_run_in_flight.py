"""One in-flight-run lookup, used by the calculation gate and the dispatch gate.

Two defects share the same missing primitive (see run_state.RunStateMixin):

* a calculation landing inside a run was erased, because every run path settles
  the bucket absolutely from an anchor captured before the valve opened;
* nothing refused to dispatch a zone that already had a run in flight.

The dispatch tests here deliberately hold the bucket BELOW ``bucket_threshold``
so the demand gate (``duration > 0 AND bucket < bucket_threshold``) cannot be
what rejects the second dispatch. Without that, the tests would pass whether or
not the guard exists.

Coordinators are built with ``__new__`` so only the touched attributes are wired.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time
from homeassistant.const import EVENT_CALL_SERVICE
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM
from pytest_homeassistant_custom_component.common import (
    async_capture_events,
    async_fire_time_changed,
)

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from tests.test_service_watch import _coord as _service_coord
from tests.test_service_watch import _dispatch as _service_dispatch
from tests.test_service_watch import _the_real_backstop_from_here
from tests.test_service_watch import _zone as _service_zone


class _FakeStore:
    """Minimal store with real read/write semantics for zones + config."""

    def __init__(self, zones=None, distributors=None, **config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}
        self.distributors = {int(k): v for k, v in (distributors or {}).items()}
        self.config = SimpleNamespace(
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
            live_estimate_enabled=False,
            log_no_demand=False,
            **config,
        )

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    def get_distributor(self, distributor_id):
        d = self.distributors.get(int(distributor_id))
        return dict(d) if d is not None else None

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(
            changes
        )
        return dict(self.zones[int(zone_id)])


def _zone(**over):
    """A zone that is due: duration > 0 and bucket BELOW the threshold."""
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_BUCKET: -20.0,
        const.ZONE_BUCKET_THRESHOLD: -5.0,
        const.ZONE_DURATION: 300,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MAXIMUM_DURATION: 36000,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_MAPPING: 0,
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


def _coord(monkeypatch, zones=None, distributors=None, **config):
    for module in ("irrigation", "calculation"):
        monkeypatch.setattr(
            f"custom_components.irrigation_plus.{module}.async_dispatcher_send",
            Mock(),
        )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.services = Mock()
    hass.services.async_call = AsyncMock()
    hass.states = Mock()
    hass.states.get = Mock(return_value=None)
    hass.async_create_task = Mock()
    coord.hass = hass
    coord.store = _FakeStore(zones or [_zone()], distributors, **config)
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord.async_master_acquire = AsyncMock()
    coord.async_master_release = AsyncMock()
    coord._dispatch_distributor_cycles = AsyncMock(return_value=False)
    coord._apply_live_durations = AsyncMock(side_effect=lambda z: z)
    coord._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    coord._rain_delay_active = Mock(return_value=False)
    coord._dispatch_sequencing = AsyncMock()
    coord._irrigate_zones_parallel = AsyncMock()
    coord.async_update_zone_config = AsyncMock()
    return coord


def _sc_run(zone_id=1, planned=600, started=None):
    return {
        const.RUN_ZONE_ID: zone_id,
        const.RUN_PLANNED_SECONDS: planned,
        const.RUN_STARTED: (started or dt_util.utcnow()).isoformat(),
        const.RUN_PRE_BUCKET: -20.0,
    }


# --------------------------------------------------------------------------- #
# The lookup itself
# --------------------------------------------------------------------------- #
def test_no_run_anywhere_is_not_in_flight(monkeypatch):
    assert _coord(monkeypatch).zone_run_in_flight(1) is False


def test_classic_registry_counts(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}
    assert coord.zone_run_in_flight(1) is True
    assert coord.zone_run_in_flight(2) is False


def test_self_closing_record_inside_its_window_counts(monkeypatch):
    coord = _coord(monkeypatch)
    coord.store.config.active_valve_runs = [_sc_run()]
    assert coord.zone_run_in_flight(1) is True


def test_self_closing_record_past_its_window_does_not_count(monkeypatch):
    """The hardware owns the close, so an overdue record is a finaliser that has
    not run yet — not an open valve. Counting it would let one record that
    outlived its finaliser block the zone's runs forever."""
    coord = _coord(monkeypatch)
    stale = _sc_run(
        planned=60, started=dt_util.utcnow() - dt_util.dt.timedelta(hours=2)
    )
    coord.store.config.active_valve_runs = [stale]
    assert coord.zone_run_in_flight(1) is False


def _service_run(started, *, watch_entity=None, margin=None):
    """A 600 s service record as dispatch persists it.

    A confirmed run carries RUN_WATCH_ENTITY and, since #139, the zone's
    latency margin frozen at dispatch; a write-only run carries neither, and a
    confirmed run persisted before the margin existed carries only the entity.
    """
    run = _sc_run(planned=600, started=started)
    run[const.RUN_MODE] = const.WATERING_MODE_SERVICE
    if watch_entity is not None:
        run[const.RUN_WATCH_ENTITY] = watch_entity
    if margin is not None:
        run[const.RUN_LATENCY_MARGIN] = margin
    return run


def test_a_confirmed_service_run_stays_in_flight_through_its_finish_grace(
    monkeypatch,
):
    """Past its plan, inside planned + debounce 5 + margin 4 = 609 (#139).

    The record, its watcher and its backstop all live through that grace; a
    zone reported idle inside it could be dispatched again, replacing the
    record that has not settled or having the old run finalised mid-confirm
    with the new run's pump hold and meter.
    """
    coord = _coord(monkeypatch)
    now = dt_util.utcnow()

    coord.store.config.active_valve_runs = [
        _service_run(
            now - dt_util.dt.timedelta(seconds=605),
            watch_entity="binary_sensor.flowing",
            margin=4,
        )
    ]
    assert coord.zone_run_in_flight(1) is True

    coord.store.config.active_valve_runs = [
        _service_run(
            now - dt_util.dt.timedelta(seconds=610),
            watch_entity="binary_sensor.flowing",
            margin=4,
        )
    ]
    assert coord.zone_run_in_flight(1) is False


def test_a_write_only_service_run_gets_no_finish_grace(monkeypatch):
    """Nothing watches a write-only valve close: its window is the plan."""
    coord = _coord(monkeypatch)
    coord.store.config.active_valve_runs = [
        _service_run(dt_util.utcnow() - dt_util.dt.timedelta(seconds=605))
    ]
    assert coord.zone_run_in_flight(1) is False


def test_a_service_run_persisted_before_the_margin_keeps_its_window(monkeypatch):
    """Confirmed, but dispatched by a build without the margin: no grace."""
    coord = _coord(monkeypatch)
    coord.store.config.active_valve_runs = [
        _service_run(
            dt_util.utcnow() - dt_util.dt.timedelta(seconds=605),
            watch_entity="binary_sensor.flowing",
        )
    ]
    assert coord.zone_run_in_flight(1) is False


def test_a_confirmed_run_waits_out_its_own_frozen_margin(monkeypatch):
    """Frozen at 10: in flight until 600 + 5 + 10 = 615 (#139).

    The grace is priced from the margin dispatch froze into the record, as
    the backstop is, and not from the zone, whose own margin now reads the
    default 4. The cases above all carry that default, so a window priced
    from the default or from the zone would pass every one of them.
    """
    zone = _zone(
        **{
            const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
            const.ZONE_RUN_SERVICE: "script.valve",
            const.ZONE_CONFIRM_ENTITY: "binary_sensor.flowing",
            const.ZONE_LATENCY_MARGIN: const.DEFAULT_LATENCY_MARGIN_SECONDS,
        }
    )
    coord = _coord(monkeypatch, zones=[zone])
    now = dt_util.utcnow()

    coord.store.config.active_valve_runs = [
        _service_run(
            now - dt_util.dt.timedelta(seconds=614),
            watch_entity="binary_sensor.flowing",
            margin=10,
        )
    ]
    assert coord.zone_run_in_flight(1) is True

    coord.store.config.active_valve_runs = [
        _service_run(
            now - dt_util.dt.timedelta(seconds=616),
            watch_entity="binary_sensor.flowing",
            margin=10,
        )
    ]
    assert coord.zone_run_in_flight(1) is False


def test_the_grace_counts_from_the_dispatch_not_the_valve_on_report(monkeypatch):
    """Still in flight a second before the backstop is due, as it must be.

    The backstop is armed for planned + grace right after RUN_STARTED is
    stamped, and a restart re-arms it from RUN_STARTED too. RUN_VALVE_ON is
    earlier: clamped to [dispatch, confirm return], it can precede RUN_STARTED
    by up to a confirm poll and the bucket write in between. Counted from it,
    the zone would read idle while its backstop and its watcher were still
    waiting for the valve's close.
    """
    coord = _coord(monkeypatch)
    now = dt_util.utcnow().replace(microsecond=0)
    started = now - dt_util.dt.timedelta(seconds=608)
    run = _service_run(started, watch_entity="binary_sensor.flowing", margin=4)
    run[const.RUN_OBSERVED_START] = run[const.RUN_STARTED]  # as the watcher sets it
    run[const.RUN_VALVE_ON] = (
        started - dt_util.dt.timedelta(seconds=const.VALVE_CONFIRM_POLL)
    ).isoformat()
    coord.store.config.active_valve_runs = [run]

    with freeze_time(now):
        assert coord.zone_run_in_flight(1) is True


def test_the_grace_ends_exactly_when_the_backstop_is_due(monkeypatch):
    """At 609 s the zone is free again; a millisecond before, it is not.

    Frozen, because a real clock never lands on the boundary itself.
    """
    coord = _coord(monkeypatch)
    now = dt_util.utcnow().replace(microsecond=0)

    with freeze_time(now):
        for elapsed, in_flight in ((608.999, True), (609.0, False)):
            coord.store.config.active_valve_runs = [
                _service_run(
                    now - dt_util.dt.timedelta(seconds=elapsed),
                    watch_entity="binary_sensor.flowing",
                    margin=4,
                )
            ]
            assert coord.zone_run_in_flight(1) is in_flight, elapsed


def test_distributor_cycle_counts_for_its_members(monkeypatch):
    coord = _coord(
        monkeypatch,
        zones=[_zone(**{const.ZONE_DISTRIBUTOR_ID: 0})],
        distributors={0: {"id": 0, "active_cycle": {"outlet": 1, "phase": "watering"}}},
    )
    assert coord.zone_run_in_flight(1) is True
    coord.store.distributors[0]["active_cycle"] = {}
    assert coord.zone_run_in_flight(1) is False


# --------------------------------------------------------------------------- #
# The calculation gives way
# --------------------------------------------------------------------------- #
async def test_calculation_is_deferred_and_consumes_nothing(monkeypatch):
    """The gate must return BEFORE the window is aggregated: last_consumed_at is
    only advanced on the write path, so an untouched watermark is what makes the
    deferral lossless."""
    coord = _coord(monkeypatch)
    coord._aggregate_for_zone = AsyncMock()
    coord.calculate_module = AsyncMock()
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_calculate_zone(1)

    coord._aggregate_for_zone.assert_not_awaited()
    coord.calculate_module.assert_not_awaited()
    assert const.ZONE_LAST_CONSUMED not in coord.store.zones[1]
    assert coord.store.zones[1][const.ZONE_BUCKET] == -20.0
    assert coord._deferred_calc_zones == {1}


async def test_calculation_runs_normally_with_no_run_in_flight(monkeypatch):
    coord = _coord(monkeypatch)
    coord._aggregate_for_zone = AsyncMock(return_value=({"x": 1}, 3))
    coord.calculate_module = AsyncMock(return_value={const.ZONE_BUCKET: -1.0})
    coord._prune_mapping_buffer = AsyncMock()

    await coord.async_calculate_zone(1)

    coord.calculate_module.assert_awaited_once()
    assert coord.store.zones[1][const.ZONE_BUCKET] == -1.0
    assert not getattr(coord, "_deferred_calc_zones", set())


async def test_deferred_calculation_runs_once_the_run_ends(monkeypatch):
    coord = _coord(monkeypatch)
    coord.defer_zone_calculation(1)

    await coord.async_run_deferred_calculation(1)

    coord.async_update_zone_config.assert_awaited_once()
    kwargs = coord.async_update_zone_config.await_args.kwargs
    assert kwargs["zone_id"] == 1
    assert kwargs["data"] == {const.ATTR_CALCULATE: True}
    assert coord._deferred_calc_zones == set()


async def test_deferred_calculation_stays_deferred_under_a_new_run(monkeypatch):
    coord = _coord(monkeypatch)
    coord.defer_zone_calculation(1)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_run_deferred_calculation(1)

    coord.async_update_zone_config.assert_not_awaited()
    assert coord._deferred_calc_zones == {1}


async def test_deferred_calculation_is_a_noop_when_nothing_was_deferred(monkeypatch):
    coord = _coord(monkeypatch)
    await coord.async_run_deferred_calculation(1)
    coord.async_update_zone_config.assert_not_awaited()


async def test_a_failing_deferred_calculation_is_swallowed_and_re_queued(monkeypatch):
    """It is called from run teardown (including a ``finally``); a zone whose
    mapping has no data raises. The window is still unconsumed either way."""
    coord = _coord(monkeypatch)
    coord.async_update_zone_config = AsyncMock(side_effect=RuntimeError("no data"))
    coord.defer_zone_calculation(1)

    await coord.async_run_deferred_calculation(1)

    assert coord._deferred_calc_zones == {1}


async def test_classic_run_defers_the_calculation_and_runs_it_at_the_end(monkeypatch):
    """End to end on the path that reproduced the erasure: a calculation fired
    mid-run leaves the bucket alone, and lands after the run's final commit."""
    monkeypatch.setattr(
        "custom_components.irrigation_plus.irrigation.asyncio.sleep", AsyncMock()
    )
    coord = _coord(monkeypatch)
    coord._live_run_zones = set()
    coord._aggregate_for_zone = AsyncMock()
    coord._record_run = AsyncMock()
    calls = []

    real_sleep_or_stopped = coord._sleep_or_stopped

    async def _tick(zone_id, seconds):
        calls.append(seconds)
        if len(calls) == 1:
            await coord.async_calculate_zone(1)  # the daily calc lands mid-run
        return await real_sleep_or_stopped(zone_id, seconds)

    coord._sleep_or_stopped = _tick

    await coord._run_valve_metered(_zone(), "switch.valve", real_flow=False)

    # nothing was consumed while the valve was open ...
    coord._aggregate_for_zone.assert_not_awaited()
    # ... the run settled the bucket on its own (300 s @ 10 L/min over 10 m²) ...
    assert coord.store.zones[1][const.ZONE_BUCKET] == pytest.approx(-15.0)
    # ... and the displaced calculation ran once the run finalised.
    coord.async_update_zone_config.assert_awaited_once()
    assert coord.async_update_zone_config.await_args.kwargs["data"] == {
        const.ATTR_CALCULATE: True
    }


# --------------------------------------------------------------------------- #
# Nothing dispatches a zone that is already running
# --------------------------------------------------------------------------- #
async def test_scheduled_dispatch_skips_a_running_zone(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    watered = await coord._irrigate_linked_entities()

    assert watered is False
    coord._dispatch_sequencing.assert_not_awaited()


async def test_scheduled_dispatch_still_runs_an_idle_zone(monkeypatch):
    """The guard must not be what makes the previous test pass."""
    coord = _coord(monkeypatch)

    watered = await coord._irrigate_linked_entities()

    assert watered is True
    coord._dispatch_sequencing.assert_awaited_once()


async def test_irrigate_now_skips_a_running_zone(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_irrigate_now("1")

    coord._dispatch_sequencing.assert_not_awaited()


async def test_irrigate_now_still_runs_an_idle_zone(monkeypatch):
    coord = _coord(monkeypatch)
    await coord.async_irrigate_now("1")
    coord._dispatch_sequencing.assert_awaited_once()


async def test_run_zone_rejects_a_running_zone(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_run_zone(1, 5)

    coord._irrigate_zones_parallel.assert_not_awaited()


async def test_run_zone_still_runs_an_idle_zone(monkeypatch):
    coord = _coord(monkeypatch)
    await coord.async_run_zone(1, 5)
    coord._irrigate_zones_parallel.assert_awaited_once()


async def test_self_closing_dispatch_rejects_a_second_run(monkeypatch):
    """Backstop for _sc_add_run, which REPLACES an existing record for the same
    zone rather than rejecting — so a second dispatch reaching it would open the
    valve again, credit the bucket twice and orphan the first run."""
    zone = _zone(
        **{
            const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
            const.ZONE_RUN_SERVICE: "script.valve",
            const.ZONE_LINKED_ENTITY: None,
        }
    )
    coord = _coord(monkeypatch, zones=[zone])
    coord._note_si_valve = Mock()
    coord.store.config.active_valve_runs = [_sc_run()]

    started = await coord.async_run_self_closing(zone)

    assert started is False
    coord.hass.services.async_call.assert_not_awaited()


# --------------------------------------------------------------------------- #
# ... not even inside a confirmed run's finish grace (#139)
# --------------------------------------------------------------------------- #
def _service_coord_on_its_store(hass):
    """tests/test_service_watch.py's coordinator, its guard reading the store.

    There store.config is a bare Mock, so zone_run_in_flight never sees a
    persisted run and no dispatch guard can fire. The real store replaces its
    config on every async_update_config; mirrored here as tests/test_batch.py
    does, so the guard reads exactly what the first dispatch persisted. The
    backstop is the real timer, its calls still recorded.
    """
    c = _service_coord(hass)
    c.store.config.active_valve_runs = []

    def _update(changes):
        c._cfg.update(changes)
        c.store.config.active_valve_runs = c._cfg.get(const.CONF_ACTIVE_VALVE_RUNS, [])

    c.store.async_update_config = AsyncMock(side_effect=_update)
    _the_real_backstop_from_here(c)
    return c


def _valve_opens(calls):
    return [call for call in calls if call.data["service"] == "irrigation_beet"]


async def _into_the_grace(hass, c, frozen):
    """Dispatch a confirmed 600 s service run for real, then go to 603 s.

    Inside its grace (debounce 5 + default margin 4 = 609 s) and more than a
    second from both ends of it. Returns what a second dispatch must leave
    alone: a copy of the persisted record and the backstop's timer handle.
    """
    assert await _service_dispatch(hass, c, _service_zone()) is True
    first = dict(await c._sc_find_run(2))
    backstop = c._sc_cleanup_timers()[2]
    frozen.tick(dt_util.dt.timedelta(seconds=603))
    return first, backstop


async def _assert_the_first_run_is_untouched(c, calls, first, backstop):
    assert len(_valve_opens(calls)) == 1  # the valve is not opened again
    assert await c._sc_find_run(2) == first  # same record, same RUN_STARTED
    c._sc_start_flow_sampling.assert_awaited_once()  # the meter not re-seeded
    c._sc_finish_flow.assert_not_called()  # nor finalised
    c.async_master_acquire.assert_awaited_once()
    c.async_master_release.assert_not_awaited()
    c._sc_schedule_cleanup.assert_called_once()  # the backstop not re-armed
    assert c._sc_cleanup_timers()[2] is backstop


async def _settled_by_its_own_backstop(hass, c, frozen):
    """The backstop armed at dispatch, due at 609 s, settles the first run.

    Leaves no real timer armed, and shows the refused dispatch left that
    run's own finish intact: recorded once, its one master hold released once.
    """
    frozen.tick(dt_util.dt.timedelta(seconds=7))
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()

    assert await c._sc_find_run(2) is None
    c._record_run.assert_awaited_once()
    c.async_master_release.assert_awaited_once()


class TestASecondDispatchInsideTheFinishGraceIsRefused:
    """Past its plan, a confirmed run is not settled yet: nothing may replace it.

    The first run's record, watcher and backstop all live on through its
    grace, waiting for the valve's own off report. With the zone read as idle
    there, a second dispatch passed the guard: it opened the valve again,
    replaced the unsettled record, re-seeded the meter, took a second master
    hold and re-armed the backstop. Driven on the real hass, because the
    backstop is a real timer here and the watcher a real subscription.
    """

    async def test_a_second_self_closing_dispatch_is_refused(self, hass):
        c = _service_coord_on_its_store(hass)
        calls = async_capture_events(hass, EVENT_CALL_SERVICE)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            first, backstop = await _into_the_grace(hass, c, frozen)

            again = await c.async_run_self_closing(_service_zone(), trigger="manual")
            await hass.async_block_till_done()

            assert again is False
            await _assert_the_first_run_is_untouched(c, calls, first, backstop)
            await _settled_by_its_own_backstop(hass, c, frozen)

    async def test_a_manual_run_zone_is_refused_the_same_way(self, hass):
        """run_zone asks zone_run_in_flight before it routes a self-closing zone.

        Refused there, before it marks the run manual: a marker left behind
        would be inherited by the zone's next run (_mark_manual_run).
        """
        c = _service_coord_on_its_store(hass)
        calls = async_capture_events(hass, EVENT_CALL_SERVICE)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            first, backstop = await _into_the_grace(hass, c, frozen)

            await c.async_run_zone(2, 10)
            await hass.async_block_till_done()

            await _assert_the_first_run_is_untouched(c, calls, first, backstop)
            assert 2 not in (getattr(c, "_live_run_zones", None) or set())
            assert 2 not in (getattr(c, "_manual_run_zones", None) or set())
            await _settled_by_its_own_backstop(hass, c, frozen)
