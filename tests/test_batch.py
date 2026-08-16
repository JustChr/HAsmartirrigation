"""Batch/queue dispatch mode (issue #88).

One service call carrying the whole irrigation, run from the controller's own
queue. Driven against the real ``hass`` fixture rather than a double, for the
same reason the OpenSprinkler tests are: the mode is built out of a state
subscription that has to survive the gap between dispatch and a zone's turn, and
a double replaces exactly the thing under test.

These carry more weight than usual. Nobody on this side has the hardware, so the
suite is the only place this mode is exercised before it reaches the one person
who can actually run it.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock

from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.batch import batch_watch_entity, is_batch_zone
from custom_components.smart_irrigation.self_closing import is_self_closing_zone

VALVE_A = "switch.valve_front"
VALVE_B = "switch.valve_back"
PAUSED = "binary_sensor.controller_paused"


def _coord(hass, **config):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = hass
    c.store = Mock()
    c._runs = []
    c._zones = {}
    cfg = {
        const.CONF_BATCH_RUN_SERVICE: "script.run_irrigation",
        const.CONF_BATCH_STOP_SERVICE: "script.stop_irrigation",
    }
    cfg.update(config)
    c._cfg = cfg
    c.store.async_get_config = AsyncMock(side_effect=lambda: dict(c._cfg))
    c.store.async_update_zone = AsyncMock()
    c.store.async_update_config = AsyncMock()
    c.store.get_zone = Mock(side_effect=lambda zid: c._zones.get(int(zid)))
    c._record_run = AsyncMock()
    c._set_zone_fault = Mock()
    c._fire_zone_problem = Mock()
    c._si_driven_until = {}
    c._note_si_valve = Mock()
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c.async_run_deferred_calculation = AsyncMock()
    c.async_write_watered_bucket = AsyncMock()
    c._stamp_run_finalized = AsyncMock()
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    c._flow_calibration_check = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._sc_schedule_cleanup = Mock()
    c._sc_cancel_cleanup = Mock()
    c._os_cancel_watch = Mock()
    c._os_chain_advance = AsyncMock()
    c._os_drop_from_cycle = Mock()
    c._sc_active_runs = AsyncMock(side_effect=lambda: [dict(r) for r in c._runs])

    c.store.config = Mock()
    c.store.config.active_valve_runs = c._runs
    for key, value in cfg.items():
        setattr(c.store.config, key, value)
    # A Mock answers every attribute, so the paused entity has to be explicit.
    if const.CONF_BATCH_PAUSED_ENTITY not in cfg:
        c.store.config.batch_paused_entity = None

    async def _persist(runs):
        c._runs = [dict(r) for r in runs]
        c.store.config.active_valve_runs = c._runs

    c._sc_persist_runs = AsyncMock(side_effect=_persist)
    c._calls = {
        "run": async_mock_service(hass, "script", "run_irrigation"),
        "stop": async_mock_service(hass, "script", "stop_irrigation"),
        "timeout": async_mock_service(hass, "script", "on_pause_timeout"),
    }
    return c


def _zone(zone_id=1, valve=VALVE_A, duration=600, **kw):
    z = {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: f"Zone {zone_id}",
        const.ZONE_WATERING_MODE: const.WATERING_MODE_BATCH,
        const.ZONE_CONFIRM_ENTITY: valve,
        const.ZONE_DURATION: duration,
        const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
        const.ZONE_BUCKET: -20.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
    }
    z.update(kw)
    return z


def _register(c, *zones):
    for z in zones:
        c._zones[int(z[const.ZONE_ID])] = z
    return list(zones)


async def _set(hass, entity, state):
    hass.states.async_set(entity, state)
    await hass.async_block_till_done()


async def _advance(hass, seconds):
    """Move the clock on so pending async_call_later timers actually fire."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=seconds))
    await hass.async_block_till_done()


async def _settle(hass):
    """Run out the window a valve-off is held open in as possibly-a-pause.

    Assertions about a pause are only meaningful once this has passed: before it,
    a run is un-settled whether the pause was recognised or not.
    """
    await _advance(hass, const.BATCH_PAUSE_SETTLE_SECONDS + 1)


class TestTheModeIsRecognisedEverywhereItMustBe:
    def test_a_batch_zone_is_a_self_closing_zone(self):
        """Which is what keeps the classic runner away from its valve.

        The metered runner, the sequencing dispatch and async_stop_zone's
        turn_off all branch on this predicate; a batch zone reaching any of them
        would be driven directly instead of through its controller.
        """
        assert is_self_closing_zone(_zone()) is True
        assert is_batch_zone(_zone()) is True

    def test_other_modes_are_not_batch_zones(self):
        for mode in (
            const.WATERING_MODE_CLASSIC,
            const.WATERING_MODE_SERVICE,
            const.WATERING_MODE_OPENSPRINKLER,
        ):
            assert is_batch_zone(_zone(**{const.ZONE_WATERING_MODE: mode})) is False

    def test_the_watch_entity_is_the_zones_confirm_entity(self):
        assert batch_watch_entity(_zone(valve=VALVE_B)) == VALVE_B
        assert batch_watch_entity({const.ZONE_CONFIRM_ENTITY: ""}) is None
        assert batch_watch_entity({}) is None


class TestTheRunnerRoutesBatchZonesToTheBatchDispatcher:
    """The wiring, which the direct-dispatch tests below cannot see.

    ``_dispatch_by_mode`` is where a due zone is sent down the path its mode
    needs, and a batch zone reaching any of the other branches would be actuated
    one call at a time or driven directly.
    """

    async def test_a_batch_zone_reaches_the_batch_dispatcher(self, hass):
        c = _coord(hass)
        c.async_dispatch_batch_zones = AsyncMock()
        c.async_run_self_closing = AsyncMock()
        c.async_dispatch_opensprinkler_zones = AsyncMock()
        c._dispatch_sequencing = AsyncMock()

        zones = _register(c, _zone(1, VALVE_A), _zone(2, VALVE_B))
        await c._dispatch_by_mode(zones, trigger="schedule")

        c.async_dispatch_batch_zones.assert_awaited_once()
        sent = c.async_dispatch_batch_zones.await_args.args[0]
        assert [z[const.ZONE_ID] for z in sent] == [1, 2]
        # And down none of the other paths.
        c.async_run_self_closing.assert_not_awaited()
        c._dispatch_sequencing.assert_not_awaited()

    async def test_an_install_with_no_batch_zones_never_enters_the_mode(self, hass):
        """Which is every install today, so this is the regression guard."""
        c = _coord(hass)
        c.async_dispatch_batch_zones = AsyncMock()
        c.async_run_self_closing = AsyncMock()
        c.async_dispatch_opensprinkler_zones = AsyncMock()
        c._dispatch_sequencing = AsyncMock()

        classic = {
            const.ZONE_ID: 9,
            const.ZONE_NAME: "Lawn",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
            const.ZONE_LINKED_ENTITY: "switch.lawn",
            const.ZONE_DURATION: 300,
        }
        await c._dispatch_by_mode([classic], trigger="schedule")

        c.async_dispatch_batch_zones.assert_not_awaited()
        c._dispatch_sequencing.assert_awaited_once()

    async def test_batch_and_classic_zones_go_their_separate_ways(self, hass):
        c = _coord(hass)
        c.async_dispatch_batch_zones = AsyncMock()
        c.async_run_self_closing = AsyncMock()
        c.async_dispatch_opensprinkler_zones = AsyncMock()
        c._dispatch_sequencing = AsyncMock()

        batch_zone = _zone(1, VALVE_A)
        classic = {
            const.ZONE_ID: 9,
            const.ZONE_NAME: "Lawn",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
            const.ZONE_LINKED_ENTITY: "switch.lawn",
            const.ZONE_DURATION: 300,
        }
        _register(c, batch_zone)
        await c._dispatch_by_mode([batch_zone, classic], trigger="schedule")

        assert [
            z[const.ZONE_ID] for z in c.async_dispatch_batch_zones.await_args.args[0]
        ] == [1]
        assert [
            z[const.ZONE_ID] for z in c._dispatch_sequencing.await_args.args[0]
        ] == [9]


class TestDispatch:
    async def test_the_whole_plan_goes_out_as_one_call_in_order(self, hass):
        c = _coord(hass)
        zones = _register(
            c,
            _zone(1, VALVE_A, 600),
            _zone(2, VALVE_B, 900),
        )
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert len(c._calls["run"]) == 1, "a batch must be ONE call, not one per zone"
        plan = c._calls["run"][0].data[const.BATCH_FIELD_ZONES]
        assert [p["zone_id"] for p in plan] == [1, 2]
        assert [p["duration"] for p in plan] == [600, 900]
        assert [p["zone_name"] for p in plan] == ["Zone 1", "Zone 2"]

    async def test_durations_are_converted_to_each_zones_own_unit(self, hass):
        c = _coord(hass)
        zones = _register(
            c,
            _zone(1, VALVE_A, 600),
            _zone(
                2,
                VALVE_B,
                630,
                **{const.ZONE_DURATION_UNIT: const.DURATION_UNIT_MINUTES},
            ),
        )
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        plan = c._calls["run"][0].data[const.BATCH_FIELD_ZONES]
        # 630 s rounds UP to 11 minutes: under-watering a zone is the worse
        # direction, and the shared converter already makes that choice.
        assert [p["duration"] for p in plan] == [600, 11]

    async def test_every_dispatched_zone_gets_a_persisted_run_record(self, hass):
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A, 600), _zone(2, VALVE_B, 900))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert len(c._runs) == 2
        for run in c._runs:
            assert run[const.RUN_MODE] == const.WATERING_MODE_BATCH
            assert run[const.RUN_CREDITED] is True
            assert run[const.RUN_WATCH_ENTITY] in (VALVE_A, VALVE_B)
            assert run[const.RUN_PRE_BUCKET] == -20.0
            # The whole point of the mode: nothing is timed from dispatch.
            assert const.RUN_OBSERVED_START not in run

    async def test_the_bucket_is_credited_optimistically_at_dispatch(self, hass):
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A, 600))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        c.async_write_watered_bucket.assert_awaited_once_with(1, -16.0)

    async def test_a_zone_with_no_confirm_entity_is_refused_not_dispatched(self, hass):
        """It could be started but never observed.

        The run would credit the bucket at dispatch and then sit in flight until
        its deadline expired, blocking the zone the whole time — so the honest
        outcome is to refuse it and say why.
        """
        c = _coord(hass)
        zones = _register(c, _zone(1, valve=None), _zone(2, VALVE_B, 900))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        plan = c._calls["run"][0].data[const.BATCH_FIELD_ZONES]
        assert [p["zone_id"] for p in plan] == [2]
        assert [r[const.RUN_ZONE_ID] for r in c._runs] == [2]
        c._set_zone_fault.assert_any_call(1, const.PROBLEM_BATCH_NO_WATCH_ENTITY)

    async def test_nothing_is_dispatched_without_a_run_service(self, hass):
        c = _coord(hass, **{const.CONF_BATCH_RUN_SERVICE: None})
        zones = _register(c, _zone(1, VALVE_A))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert c._calls["run"] == []
        assert c._runs == []
        c._set_zone_fault.assert_any_call(1, const.PROBLEM_BATCH_NOT_CONFIGURED)

    async def test_a_zone_already_running_is_left_out_of_the_batch(self, hass):
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A), _zone(2, VALVE_B))
        c._runs.append(
            {
                const.RUN_ZONE_ID: 1,
                const.RUN_MODE: const.WATERING_MODE_BATCH,
                const.RUN_PLANNED_SECONDS: 600,
                const.RUN_STARTED: dt_util.utcnow().isoformat(),
            }
        )
        c.store.config.active_valve_runs = c._runs
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        plan = c._calls["run"][0].data[const.BATCH_FIELD_ZONES]
        assert [p["zone_id"] for p in plan] == [2]

    async def test_the_master_hold_is_taken_before_the_call(self, hass):
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A), _zone(2, VALVE_B))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        assert c.async_master_acquire.await_count == 2


class TestObservationDrivesTheRun:
    async def _dispatch(self, hass, **config):
        c = _coord(hass, **config)
        zones = _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        return c

    async def test_the_run_starts_when_its_own_valve_opens(self, hass):
        c = await self._dispatch(hass)
        assert const.RUN_OBSERVED_START not in c._runs[0]

        await _set(hass, VALVE_A, "on")
        run = c._runs[0]
        assert run[const.RUN_OBSERVED_START] is not None
        # A segmented mode opens its first watering segment at the same instant.
        assert run[const.RUN_SEGMENT_STARTED] == run[const.RUN_OBSERVED_START]
        assert run[const.RUN_WATERED_SECONDS] == 0.0

    async def test_a_queued_run_reports_no_watering_however_long_it_waits(self, hass):
        c = await self._dispatch(hass)
        run = dict(c._runs[0])
        run[const.RUN_STARTED] = "2020-01-01T00:00:00+00:00"
        assert c._sc_run_elapsed(run) == 0.0

    async def test_the_valve_closing_finishes_the_run(self, hass):
        c = await self._dispatch(hass)
        await _set(hass, VALVE_A, "on")
        await _set(hass, VALVE_A, "off")
        # Settled and removed from the in-flight list either way; short of its
        # planned window, so it settles as a partial.
        assert c._runs == []
        assert c._record_run.await_count == 1
        assert c._record_run.await_args.kwargs["result"] == const.RUN_RESULT_PARTIAL

    async def test_with_no_paused_entity_the_finish_is_not_deferred(self, hass):
        """Nothing could arrive late, so nobody waits for a stop they can see."""
        c = await self._dispatch(hass)
        run = c._runs[0]
        assert await c._watch_finish_delay(1, run) == 0.0

    async def test_with_a_paused_entity_the_finish_is_deferred(self, hass):
        c = await self._dispatch(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        run = c._runs[0]
        assert await c._watch_finish_delay(1, run) == const.BATCH_PAUSE_SETTLE_SECONDS

    async def test_another_modes_run_is_untouched_by_the_batch_hooks(self, hass):
        """Every override is gated on the RUN's mode, not the zone's."""
        c = await self._dispatch(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        foreign = {const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER}
        assert await c._watch_finish_delay(1, foreign) == 0.0
        assert await c._watch_paused(1, foreign) is False


class TestPause:
    async def _running(self, hass, **config):
        config.setdefault(const.CONF_BATCH_PAUSED_ENTITY, PAUSED)
        c = _coord(hass, **config)
        _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "off")
        await c.async_dispatch_batch_zones(list(c._zones.values()), trigger="schedule")
        await _set(hass, VALVE_A, "on")
        return c

    async def test_a_pause_does_not_finish_the_run(self, hass):
        """The failure this whole design exists to prevent.

        Without it the pause reads as the controller cutting the run short: it
        would be settled as a partial with its credit reversed, and the
        controller would then resume watering a zone already closed out.

        The clock is advanced past the settle window deliberately. Merely
        asserting "not settled yet" would pass against a broken pause check too,
        because the deferred finish has not fired at that point either — the
        assertion only means anything once that timer has come and gone.
        """
        c = await self._running(hass)
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)

        assert len(c._runs) == 1, "the paused run was settled"
        assert c._record_run.await_count == 0

    async def test_the_same_stop_without_a_pause_does_settle(self, hass):
        """The counterfactual, so the test above cannot pass for free."""
        c = await self._running(hass)
        await _set(hass, VALVE_A, "off")
        await _settle(hass)

        assert c._runs == [], "an unpaused stop should have settled the run"
        assert c._record_run.await_count == 1

    async def test_a_pause_banks_the_segment_and_stops_the_clock(self, hass):
        c = await self._running(hass)
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)

        run = c._runs[0]
        assert run[const.RUN_SEGMENT_STARTED] is None
        banked = run[const.RUN_WATERED_SECONDS]
        # The elapsed no longer advances, however long the pause lasts.
        assert c._sc_run_elapsed(run) == banked

    async def test_resuming_opens_a_new_segment_and_accumulates(self, hass):
        c = await self._running(hass)
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        banked = c._runs[0][const.RUN_WATERED_SECONDS]

        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "on")

        run = c._runs[0]
        assert run[const.RUN_SEGMENT_STARTED] is not None
        assert run[const.RUN_WATERED_SECONDS] == banked
        assert c._sc_run_elapsed(run) >= banked

    async def test_the_valve_may_go_off_before_the_indicator_catches_up(self, hass):
        """Nothing orders the two updates, so the run must survive either order.

        With the valve-off arriving first the run is held open rather than
        settled, and the indicator arriving a moment later confirms the pause.
        """
        c = await self._running(hass)
        await _set(hass, VALVE_A, "off")
        assert len(c._runs) == 1, "settled before the pause indicator could arrive"

        # The indicator catches up INSIDE the settle window, which is the whole
        # point of that window existing.
        await _set(hass, PAUSED, "on")
        await _settle(hass)
        assert len(c._runs) == 1
        assert c._runs[0][const.RUN_SEGMENT_STARTED] is None

    async def test_the_pause_bound_is_armed_and_settles_the_run_when_it_expires(
        self, hass
    ):
        """Driven by the real timer rather than by calling the handler."""
        c = await self._running(hass, **{const.CONF_BATCH_PAUSE_TIMEOUT: 60})
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        assert len(c._runs) == 1

        await _advance(hass, 61)
        assert c._runs == []
        assert (
            c._record_run.await_args.kwargs["detail"]
            == const.RUN_DETAIL_BATCH_PAUSE_TIMEOUT
        )

    async def test_a_pause_that_outlives_its_bound_settles_the_run(self, hass):
        c = await self._running(hass, **{const.CONF_BATCH_PAUSE_TIMEOUT: 60})
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)

        await c._batch_pause_expired(1)
        assert c._runs == []
        assert (
            c._record_run.await_args.kwargs["detail"]
            == const.RUN_DETAIL_BATCH_PAUSE_TIMEOUT
        )

    async def test_the_users_timeout_script_runs_before_the_run_is_settled(self, hass):
        c = await self._running(
            hass,
            **{
                const.CONF_BATCH_PAUSE_TIMEOUT: 60,
                const.CONF_BATCH_PAUSE_TIMEOUT_SERVICE: "script.on_pause_timeout",
            },
        )
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")

        await c._batch_pause_expired(1)
        assert len(c._calls["timeout"]) == 1
        assert c._calls["timeout"][0].data["zone_id"] == 1
        assert c._runs == []


class TestStopping:
    async def _two_running(self, hass):
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A, 600), _zone(2, VALVE_B, 900))
        await _set(hass, VALVE_A, "off")
        await _set(hass, VALVE_B, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await _set(hass, VALVE_A, "on")
        return c

    async def test_stopping_one_zone_settles_every_run_in_the_cycle(self, hass):
        """Because that is what the hardware actually does.

        Stopping one zone ends the cycle and the queue survives it, so a run left
        open here would hold its zone and its share of the pump for a cycle that
        is no longer running.
        """
        c = await self._two_running(hass)
        await c.async_stop_batch(1)
        assert c._runs == []
        assert c._record_run.await_count == 2

    async def test_the_stop_script_is_sent_once_for_the_whole_cycle(self, hass):
        c = await self._two_running(hass)
        await c.async_stop_batch(1)
        assert len(c._calls["stop"]) == 1

    async def test_the_zone_the_user_pressed_stop_on_settles_first(self, hass):
        c = await self._two_running(hass)
        await c.async_stop_batch(2)
        settled = [call.args[0] for call in c._record_run.await_args_list]
        assert settled[0] == 2

    async def test_stop_zone_routes_a_batch_zone_through_the_cycle_stop(self, hass):
        """The panel's per-zone Stop must not drive the valve directly."""
        c = await self._two_running(hass)
        assert await c._sc_maybe_stop(1) is True
        assert len(c._calls["stop"]) == 1
        assert c._runs == []

    async def test_teardown_stops_the_controller_and_clears_its_queue(self, hass):
        """Sharper here than for stations: this controller KEEPS its queue.

        Teardown that only dropped the watchers would strand both the zone that
        is watering and every zone still queued behind it.
        """
        c = await self._two_running(hass)
        assert await c.async_abort_batch_runs("test") is True
        assert len(c._calls["stop"]) == 1
        assert c._runs == []

    async def test_teardown_is_a_no_op_with_nothing_in_flight(self, hass):
        c = _coord(hass)
        assert await c.async_abort_batch_runs("test") is False
        assert c._calls["stop"] == []

    async def test_a_missing_stop_service_still_corrects_the_accounting(self, hass):
        c = _coord(hass, **{const.CONF_BATCH_STOP_SERVICE: None})
        zones = _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await c.async_stop_batch(1)
        assert c._runs == []


class TestRestart:
    async def test_a_resumed_run_is_re_adopted_and_never_re_dispatched(self, hass):
        """Re-sending the plan would queue the whole irrigation a second time."""
        c = _coord(hass)
        _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "on")
        started = dt_util.utcnow().isoformat()
        c._runs = [
            {
                const.RUN_ZONE_ID: 1,
                const.RUN_MODE: const.WATERING_MODE_BATCH,
                const.RUN_PLANNED_SECONDS: 600,
                const.RUN_STARTED: started,
                const.RUN_OBSERVED_START: started,
                const.RUN_WATERED_SECONDS: 10.0,
                const.RUN_SEGMENT_STARTED: started,
                const.RUN_WATCH_ENTITY: VALVE_A,
                const.RUN_PRE_BUCKET: -20.0,
            }
        ]
        c.store.config.active_valve_runs = c._runs

        await c._batch_resume_run(dict(c._runs[0]))
        await hass.async_block_till_done()

        assert c._calls["run"] == [], "the plan was dispatched a second time"
        assert len(c._runs) == 1
        c.async_master_acquire.assert_awaited()

    async def test_a_restart_across_a_pause_accrues_no_watering(self, hass):
        """The property that makes keeping an open segment across a restart safe.

        A pause closes the segment before the outage begins, so however long Home
        Assistant is down while the controller sits paused, the run comes back
        crediting exactly what it had delivered. Without it, a pause spanning a
        restart would settle a barely-started run as complete.
        """
        c = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        long_ago = "2020-01-01T00:00:00+00:00"
        c._runs = [
            {
                const.RUN_ZONE_ID: 1,
                const.RUN_MODE: const.WATERING_MODE_BATCH,
                const.RUN_PLANNED_SECONDS: 600,
                const.RUN_STARTED: long_ago,
                const.RUN_OBSERVED_START: long_ago,
                # Paused when Home Assistant went down: 30 s banked, no open
                # segment.
                const.RUN_WATERED_SECONDS: 30.0,
                const.RUN_SEGMENT_STARTED: None,
                const.RUN_WATCH_ENTITY: VALVE_A,
                const.RUN_PRE_BUCKET: -20.0,
            }
        ]
        c.store.config.active_valve_runs = c._runs
        assert c._sc_run_elapsed(c._runs[0]) == 30.0

        await c._batch_resume_run(dict(c._runs[0]))
        await hass.async_block_till_done()

        # Still paused, so it is neither settled nor credited for the outage.
        assert len(c._runs) == 1
        assert c._runs[0][const.RUN_WATERED_SECONDS] == 30.0
        assert c._record_run.await_count == 0

    async def test_a_run_whose_window_has_long_since_passed_is_completed(self, hass):
        """The hardware owns the close, so a run this old finished on its own."""
        c = _coord(hass)
        _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "off")
        long_ago = "2020-01-01T00:00:00+00:00"
        c._runs = [
            {
                const.RUN_ZONE_ID: 1,
                const.RUN_MODE: const.WATERING_MODE_BATCH,
                const.RUN_PLANNED_SECONDS: 600,
                const.RUN_STARTED: long_ago,
                const.RUN_OBSERVED_START: long_ago,
                const.RUN_WATERED_SECONDS: 0.0,
                const.RUN_SEGMENT_STARTED: long_ago,
                const.RUN_WATCH_ENTITY: VALVE_A,
                const.RUN_PRE_BUCKET: -20.0,
            }
        ]
        c.store.config.active_valve_runs = c._runs
        await c._batch_resume_run(dict(c._runs[0]))
        await hass.async_block_till_done()

        assert c._runs == []
        assert c._record_run.await_args.kwargs["result"] == const.RUN_RESULT_COMPLETED

    async def test_a_run_still_queued_is_re_armed_without_being_re_sent(self, hass):
        c = _coord(hass)
        _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "off")
        c._runs = [
            {
                const.RUN_ZONE_ID: 1,
                const.RUN_MODE: const.WATERING_MODE_BATCH,
                const.RUN_PLANNED_SECONDS: 600,
                const.RUN_STARTED: dt_util.utcnow().isoformat(),
                const.RUN_WATCH_ENTITY: VALVE_A,
                const.RUN_PRE_BUCKET: -20.0,
            }
        ]
        c.store.config.active_valve_runs = c._runs
        await c._batch_resume_run(dict(c._runs[0]))
        await hass.async_block_till_done()

        assert c._calls["run"] == []
        assert len(c._runs) == 1
        assert const.RUN_OBSERVED_START not in c._runs[0]

    async def test_a_resumed_run_that_is_already_watering_is_not_written_off(
        self, hass
    ):
        """It is bounded by its finish backstop, not by a give-up timer.

        The engine arms the give-up deadline when a watcher starts, and only the
        observed-start path cancels it — which a resume skips. Batch mode opts out
        of that rather than inheriting the defect it causes.
        """
        from custom_components.smart_irrigation.run_watch import watch_policy_for

        policy = watch_policy_for(const.WATERING_MODE_BATCH)
        assert policy.arm_give_up_after_start is False
        assert policy.segmented is True
        assert policy.acknowledges is False
        assert policy.queue_deadline_at_start is True


class TestGivingUp:
    async def test_a_zone_the_controller_never_reaches_is_written_off(self, hass):
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        await c._watch_give_up(1, const.PROBLEM_ZONE_NEVER_RAN)
        assert c._runs == []
        # Credited nothing, so the optimistic credit is reversed all the way back
        # to the pre-run bucket.
        c.async_write_watered_bucket.assert_awaited_with(1, -20.0)
        c._set_zone_fault.assert_any_call(1, const.PROBLEM_ZONE_NEVER_RAN)
