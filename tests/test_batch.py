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

from freezegun import freeze_time
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


class TestSequencingIsNotSilentlyDropped:
    """`rotating` does not reach batch zones, and the log has to say so (#98).

    The queue runs each zone's full duration in one go, so the cap/soak/
    interleave a user chose `rotating` FOR never happens. Before this, nothing
    anywhere said that: the setting sat in the panel looking applied.
    """

    def _seq(self, c, value):
        """Give the coordinator a real string sequencing value.

        `_coord` leaves `store` a bare Mock, so `store.config.zone_sequencing`
        answers with another Mock — the case the last test here pins.
        """
        c.store.config = Mock()
        c.store.config.zone_sequencing = value

    async def test_rotating_is_reported_with_the_zone_count(self, hass, caplog):
        c = _coord(hass)
        self._seq(c, const.CONF_ZONE_SEQUENCING_ROTATING)
        zones = _register(c, _zone(1, VALVE_A, 600), _zone(2, VALVE_B, 900))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        warnings = [r for r in caplog.records if r.levelname == "WARNING"]
        assert len(warnings) == 1
        msg = warnings[0].getMessage()
        assert "rotating" in msg
        assert "2 batch zone(s)" in msg
        assert "#98" in msg

    async def test_it_is_said_once_not_every_irrigation(self, hass, caplog):
        """This runs from the daily scheduled dispatch; a per-dispatch warning
        would repeat for as long as the setting stands."""
        c = _coord(hass)
        self._seq(c, const.CONF_ZONE_SEQUENCING_ROTATING)
        zones = _register(c, _zone(1, VALVE_A, 600))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert len([r for r in caplog.records if r.levelname == "WARNING"]) == 1

    async def test_the_dispatch_itself_is_unchanged(self, hass):
        """A warning, not a refusal: the plan still goes out exactly as before."""
        c = _coord(hass)
        self._seq(c, const.CONF_ZONE_SEQUENCING_ROTATING)
        zones = _register(c, _zone(1, VALVE_A, 600), _zone(2, VALVE_B, 900))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert len(c._calls["run"]) == 1
        plan = c._calls["run"][0].data[const.BATCH_FIELD_ZONES]
        assert [p["zone_id"] for p in plan] == [1, 2]
        assert [p["duration"] for p in plan] == [600, 900]

    async def test_the_default_parallel_says_nothing(self, hass, caplog):
        """`parallel` is CONF_DEFAULT_ZONE_SEQUENCING. Warning on it would fire
        on every batch install that never touched the setting — noise, not
        information, and the reason this guard is not `!= sequential`."""
        assert const.CONF_DEFAULT_ZONE_SEQUENCING == const.CONF_ZONE_SEQUENCING_PARALLEL
        c = _coord(hass)
        self._seq(c, const.CONF_ZONE_SEQUENCING_PARALLEL)
        zones = _register(c, _zone(1, VALVE_A, 600))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert [r for r in caplog.records if r.levelname == "WARNING"] == []

    async def test_sequential_says_nothing_because_a_queue_already_is(
        self, hass, caplog
    ):
        c = _coord(hass)
        self._seq(c, const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        zones = _register(c, _zone(1, VALVE_A, 600))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert [r for r in caplog.records if r.levelname == "WARNING"] == []

    async def test_a_config_with_no_real_value_says_nothing(self, hass, caplog):
        """The bare-Mock config every other test in this file runs with, and the
        reason the check is a positive match on `rotating` rather than
        `!= sequential`: a Mock (and a missing attribute, which reads None) is
        not equal to `rotating`, so both stay quiet without a type guard."""
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A, 600))
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        assert [r for r in caplog.records if r.levelname == "WARNING"] == []


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


class TestWhatTheFieldTestFound:
    """The two things a real controller did that the suite had not.

    @pnaklicki ran v2026.08.13 against an ESPHome sprinkler — the first time this
    mode touched hardware. Dispatch, stopping and the bucket arithmetic held.
    These two did not, and neither was reachable through the assertions above:
    one lives in the panel payload rather than in the engine, and the other only
    appears while the controller's own entities are still reconnecting.
    """

    async def _paused_mid_run(self, hass):
        """A run that watered for a minute and is now paused."""
        c = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        zones = _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await _set(hass, VALVE_A, "on")
        await _advance(hass, 60)
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        assert c._runs, "precondition: the pause did not settle the run"
        return c

    async def test_the_countdown_stops_when_the_controller_pauses(self, hass):
        """A pause was charged to the panel as if it were water.

        The accounting had always been segment-based; the panel's ``ends_at`` was
        still observed_start + planned, so the number the user watches kept
        counting down through a pause and came back from it ahead of the
        controller by the whole length of the pause. Asserted on the payload
        rather than on the run record, because the record was never wrong.

        The clock is frozen and stepped rather than merely fired, which the rest
        of this file does not need to do. ``async_fire_time_changed`` runs due
        timers without moving ``utcnow``, so a run "watered" that way banks zero
        seconds — and against a zero-length segment the broken projection and the
        correct one give the same answer. Real watering time is the whole point
        of the assertion.
        """
        with freeze_time("2026-08-19 06:00:00") as frozen:
            c = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
            zones = _register(c, _zone(1, VALVE_A, 600))
            await _set(hass, PAUSED, "off")
            await _set(hass, VALVE_A, "off")
            await c.async_dispatch_batch_zones(zones, trigger="schedule")
            await _set(hass, VALVE_A, "on")

            frozen.tick(60)  # a minute of actual water
            await _set(hass, PAUSED, "on")
            await _set(hass, VALVE_A, "off")
            frozen.tick(const.BATCH_PAUSE_SETTLE_SECONDS + 1)
            async_fire_time_changed(hass, dt_util.utcnow())
            await hass.async_block_till_done()

            assert c._runs, "precondition: the pause did not settle the run"
            banked = c._runs[0][const.RUN_WATERED_SECONDS]
            assert 59 <= banked <= 61, f"expected ~60s banked, got {banked}"

            assert c.get_active_runs()["1"]["ends_at"] is None, (
                "a paused run has no predictable finish — the controller decides "
                "when it hands the remaining time back"
            )
            frozen.tick(300)
            assert (
                c.get_active_runs()["1"]["ends_at"] is None
            ), "five minutes of pause moved the finish"

            # On resume the countdown is the REMAINDER, not the original window.
            await _set(hass, PAUSED, "off")
            await _set(hass, VALVE_A, "on")
            await hass.async_block_till_done()
            ends = dt_util.parse_datetime(c.get_active_runs()["1"]["ends_at"])
            left = (ends - dt_util.now()).total_seconds()
            assert (
                535 <= left <= 545
            ), f"expected ~540s left (600 planned - 60 watered), got {left:.0f}s"

    async def test_an_indicator_that_is_not_reporting_does_not_settle_the_run(
        self, hass
    ):
        """A restart mid-pause lost the run, and with it the rest of the water.

        The engine's rule for the watch entity — no information is never a state
        change — was not applied to the paused indicator, and a restart is
        exactly when that indicator is unavailable: its controller is still
        reconnecting. Reading that as "not paused" settled the run, reversed the
        credit for water the controller then went on to deliver, and left nothing
        watching the valve when it reopened.
        """
        c = await self._paused_mid_run(hass)
        persisted = [dict(r) for r in c._runs]

        # Home Assistant comes back up. Its own state survives; the controller's
        # entities do not, until the device reconnects.
        c2 = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        c2._runs = persisted
        c2.store.config.active_valve_runs = c2._runs
        c2._sc_active_runs = AsyncMock(side_effect=lambda: [dict(r) for r in c2._runs])
        _register(c2, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "unavailable")
        await _set(hass, PAUSED, "unavailable")

        await c2.async_resume_self_closing_runs()
        # The valve reports first; the indicator is still catching up.
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        assert c2._runs, "the run was settled while the indicator was silent"
        assert c2._record_run.await_count == 0

        # The controller resumes: the water must be picked back up.
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "on")
        await hass.async_block_till_done()
        assert c2._runs[0].get(
            const.RUN_SEGMENT_STARTED
        ), "the valve is open again and nothing is recording it"

    async def test_a_silent_indicator_still_settles_a_run_that_really_ended(self, hass):
        """The counterfactual: holding the run open must not become never ending.

        Once the indicator reports and says the controller is NOT paused, the
        valve-off it was covering for is read as the end of the run after all.
        """
        c = await self._paused_mid_run(hass)
        persisted = [dict(r) for r in c._runs]
        c2 = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        c2._runs = persisted
        c2.store.config.active_valve_runs = c2._runs
        c2._sc_active_runs = AsyncMock(side_effect=lambda: [dict(r) for r in c2._runs])
        _register(c2, _zone(1, VALVE_A, 600))
        await _set(hass, VALVE_A, "unavailable")
        await _set(hass, PAUSED, "unavailable")
        await c2.async_resume_self_closing_runs()
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        assert c2._runs

        # The controller is back and the cycle is over, not paused.
        await _set(hass, PAUSED, "off")
        await _settle(hass)
        assert c2._runs == [], "the ended run was held open indefinitely"
        assert c2._record_run.await_count == 1


class TestWhatThePanelIsToldAboutEachZone:
    """Issue #97: queued, watering and paused are three different things.

    Batch dispatch records a run for EVERY zone the moment the plan is sent,
    because a queued zone's water may be hours away and the run has to hold the
    zone until then. ``get_active_runs`` reported all of them as plain watering,
    so a five-zone irrigation read as five zones watering at once — and a zone
    the controller had paused was indistinguishable from one that was flowing.

    Asserted on the payload, which is the only place the distinction exists: the
    accounting has always known which zone is which, and none of these flags
    changes it. All three states stay stoppable and all three still hold the zone
    against a second dispatch.
    """

    async def test_only_the_zone_the_controller_reached_reads_as_watering(self, hass):
        c = _coord(hass)
        zones = _register(c, _zone(1, VALVE_A, 600), _zone(2, VALVE_B, 600))
        await _set(hass, VALVE_A, "off")
        await _set(hass, VALVE_B, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")

        runs = c.get_active_runs()
        assert set(runs) == {"1", "2"}, "both zones must stay in flight"
        assert runs["1"]["queued"] is True, "nothing is watering yet"
        assert runs["2"]["queued"] is True

        await _set(hass, VALVE_A, "on")
        runs = c.get_active_runs()
        assert runs["1"]["queued"] is False, "this zone's valve is open"
        assert runs["1"]["paused"] is False
        assert runs["2"]["queued"] is True, (
            "zone 2 is waiting its turn behind zone 1; reporting it as watering "
            "is what made a whole batch read as watering at once"
        )
        assert runs["1"]["ends_at"] is not None, "a watering zone counts down"
        assert runs["2"]["ends_at"] is None, "a queued zone has nothing to count"

    async def test_a_paused_zone_is_paused_and_not_queued(self, hass):
        """The state a chain does not have, and the one pnaklicki asked for.

        A paused run is neither watering nor waiting its turn: the controller
        started it and is holding the rest of its time. Distinguishing it from
        queued matters because the two mean opposite things about what the user
        should do — a queued zone is fine, a paused one may need attention.
        """
        c = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        zones = _register(c, _zone(1, VALVE_A, 600))
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await _set(hass, VALVE_A, "on")
        assert c.get_active_runs()["1"]["paused"] is False

        await _advance(hass, 60)
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        assert c._runs, "precondition: the pause settled the run"

        runs = c.get_active_runs()
        assert runs["1"]["paused"] is True, (
            "a paused zone read as watering, with no countdown and nothing "
            "saying why — the gap reported from the field"
        )
        assert runs["1"]["queued"] is False, "it has watered; it is not queued"

        # And it goes back to watering on resume, rather than sticking.
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "on")
        await hass.async_block_till_done()
        runs = c.get_active_runs()
        assert runs["1"]["paused"] is False
        assert runs["1"]["ends_at"] is not None, "the countdown is back"

    async def test_a_queued_zone_is_not_reported_as_paused(self, hass):
        """The discrimination the naive implementation gets wrong.

        "Paused" is one answer for the whole controller, so reading the paused
        indicator to answer it per zone labels every queued zone paused the
        moment the controller pauses. The run record is what actually knows: a
        zone with no observed start has not begun, whatever the controller is
        doing.
        """
        c = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        zones = _register(c, _zone(1, VALVE_A, 600), _zone(2, VALVE_B, 600))
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "off")
        await _set(hass, VALVE_B, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await _set(hass, VALVE_A, "on")
        await _advance(hass, 60)
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)

        runs = c.get_active_runs()
        assert runs["1"]["paused"] is True
        assert runs["2"]["paused"] is False, (
            "zone 2 never started, so it is queued behind a paused controller "
            "rather than paused itself"
        )
        assert runs["2"]["queued"] is True


class TestAPauseStopsTheWholeQueue:
    """Issue #88, reported from the field against v2026.08.14.

    "Valve run for exact time calculated by integration, but bucket still showed
    -7 mm." A queued run's only backstop is a deadline derived from the watering
    time of the zones ahead of it, and that budget is spent in wall-clock time —
    which assumes the controller is spending that time watering. A pause is
    exactly the case where it is not.

    So an in-bounds pause wrote off every zone queued behind it: run dropped,
    optimistic credit reversed, ``zone_never_ran`` raised. Then the controller
    resumed and watered them anyway, with nothing left watching the valve. The
    water is delivered and never credited, which is precisely what that bucket
    reading is.
    """

    async def _paused_with_one_queued(self, hass):
        """Zone 1 watering then paused; zone 2 still waiting its turn."""
        c = _coord(hass, **{const.CONF_BATCH_PAUSED_ENTITY: PAUSED})
        zones = _register(c, _zone(1, VALVE_A, 600), _zone(2, VALVE_B, 600))
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "off")
        await _set(hass, VALVE_B, "off")
        await c.async_dispatch_batch_zones(zones, trigger="schedule")
        await _set(hass, VALVE_A, "on")
        await _advance(hass, 60)
        await _set(hass, PAUSED, "on")
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        assert [r[const.RUN_ZONE_ID] for r in c._runs] == [1, 2]
        return c

    async def test_a_queued_zone_is_not_written_off_during_a_pause(self, hass):
        c = await self._paused_with_one_queued(hass)

        # An hour of pause — well inside BATCH_PAUSE_BACKSTOP_SECONDS, and past
        # zone 2's whole queue deadline (accept + 600 ahead + 600 own + margin).
        await _advance(hass, 3600)

        assert any(r[const.RUN_ZONE_ID] == 2 for r in c._runs), (
            "zone 2 was written off while the controller was paused and its turn "
            "could not possibly have come"
        )
        assert const.PROBLEM_ZONE_NEVER_RAN not in [
            call.args[1] for call in c._set_zone_fault.call_args_list
        ], "a paused controller is not a controller that never watered the zone"

    async def test_the_zone_still_waters_and_credits_after_the_pause(self, hass):
        """The consequence the user actually sees, end to end."""
        c = await self._paused_with_one_queued(hass)
        await _advance(hass, 3600)

        # The controller comes back and works through the rest of the queue.
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "on")
        await hass.async_block_till_done()
        await _set(hass, VALVE_A, "off")
        await _settle(hass)
        await _set(hass, VALVE_B, "on")
        await hass.async_block_till_done()

        run = next(r for r in c._runs if r[const.RUN_ZONE_ID] == 2)
        assert run.get(const.RUN_OBSERVED_START) is not None, (
            "nothing was watching zone 2's valve, so its water is delivered and "
            "never accounted for"
        )

    async def test_the_clock_is_stopped_rather_than_the_deadline_extended(self, hass):
        """A pause must not buy a queued run an unbounded new wait.

        The deadline resumes with the time it had LEFT, so the total wait is the
        original budget plus the pauses actually sat through — not a fresh full
        deadline for every pause a controller takes.
        """
        c = await self._paused_with_one_queued(hass)
        watcher = c._watchers()[2]
        assert watcher.cancel is None, "the clock is not stopped"
        left = watcher.deadline_left
        assert left is not None and left > 0

        await _advance(hass, 3600)
        await _set(hass, PAUSED, "off")
        await _set(hass, VALVE_A, "on")
        await hass.async_block_till_done()
        assert c._watchers()[2].cancel is not None, "the clock never restarted"

        # And it is still the ORIGINAL remainder, so it can still expire.
        await _advance(hass, left + 60)
        assert not any(r[const.RUN_ZONE_ID] == 2 for r in c._runs), (
            "a zone the controller never reaches must still be written off; "
            "suspending the clock must not become never ending"
        )
