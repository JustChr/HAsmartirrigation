"""A confirmed service valve is watched for the rest of its run (issue #88).

``confirm_entity`` used to be read exactly once, at open, and nothing subscribed
to it afterwards. So a valve that shut mid-run -- a Zigbee dropout, a hardware
fault, someone closing it by hand -- left the wall clock running: the run was
recorded as ``actual_s == planned_s``, ``completed``, with its full optimistic
credit standing, and the next calculation went on believing the zone had been
watered. Reported by Eifel-Joe, who runs three service zones on a cistern pump.

Batch mode already had this accounting, because it promotes the same entity to a
watch entity. Service mode now registers its own ``WatchPolicy`` on the shared
engine rather than growing a second copy of the lifecycle.

Driven against the real ``hass`` fixture, for the reason the batch and
OpenSprinkler suites are: the feature IS a state subscription, and a double
replaces exactly the thing under test.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time
from homeassistant.util import dt as dt_util

from custom_components.irrigation_plus.run_watch import (
    run_finish_grace_seconds,
)
from pytest_homeassistant_custom_component.common import (
    async_capture_events,
    async_fire_time_changed,
    async_mock_service,
)

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const

VALVE = "binary_sensor.beet_valve"


def _coord(hass):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = hass
    c.store = Mock()
    c._cfg = {}
    c._zones = {}
    c.store.async_get_config = AsyncMock(side_effect=lambda: dict(c._cfg))
    c.store.async_update_config = AsyncMock(side_effect=c._cfg.update)
    c.store.async_update_zone = AsyncMock()
    c.store.get_zone = Mock(side_effect=lambda zid: c._zones.get(int(zid)))
    c.store.config = Mock()
    c.store.config.master_entity = None
    c._record_run = AsyncMock()
    c._set_zone_fault = Mock()
    c._fire_zone_problem = Mock()
    c._note_si_valve = Mock()
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c.async_run_deferred_calculation = AsyncMock()
    c.async_write_watered_bucket = AsyncMock()
    c._stamp_run_finalized = AsyncMock()
    c._timed_volume_l = Mock(return_value=100.0)
    c._credited_depth_native = Mock(return_value=20.0)
    c._flow_calibration_check = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._sc_schedule_cleanup = Mock()
    c._sc_cancel_cleanup = Mock()
    c._os_cancel_watch = Mock()
    c._os_chain_advance = AsyncMock()
    async_mock_service(hass, "script", "irrigation_beet")
    async_mock_service(hass, "script", "stop_irrigation_beet")
    return c


def _zone(zone_id=2, confirm=VALVE, duration=600, **kw):
    z = {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: "Beet",
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        const.ZONE_RUN_SERVICE: "script.irrigation_beet",
        const.ZONE_STOP_SERVICE: "script.stop_irrigation_beet",
        const.ZONE_DURATION_FIELD: "dauer",
        const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
        const.ZONE_DURATION: duration,
        const.ZONE_BUCKET: -20.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
    }
    if confirm is not None:
        z[const.ZONE_CONFIRM_ENTITY] = confirm
    z.update(kw)
    return z


async def _set(hass, entity, state):
    hass.states.async_set(entity, state)
    await hass.async_block_till_done()


async def _settle(hass):
    """Run out the window a valve-off is held open in, in case it was a blip.

    Assertions about the end of a run are only meaningful once this has passed:
    before it, the run is un-settled whether the off was real or not.
    """
    async_fire_time_changed(
        hass,
        dt_util.utcnow() + timedelta(seconds=const.SERVICE_WATCH_SETTLE_SECONDS + 1),
    )
    await hass.async_block_till_done()


async def _off(hass):
    """The valve stops, and stays stopped."""
    await _set(hass, VALVE, "off")
    await _settle(hass)


async def _dispatch(hass, c, zone, *, valve_state="on"):
    c._zones[int(zone[const.ZONE_ID])] = zone
    if zone.get(const.ZONE_CONFIRM_ENTITY):
        await _set(hass, zone[const.ZONE_CONFIRM_ENTITY], valve_state)
    ok = await c.async_run_self_closing(zone, trigger="schedule")
    await hass.async_block_till_done()
    return ok


class TestAValveThatShutsMidRunEndsTheRun:
    async def test_the_run_is_recorded_for_what_it_actually_watered(self, hass):
        c = _coord(hass)
        started = dt_util.utcnow()
        await _dispatch(hass, c, _zone())

        # 100 s in, the valve drops out
        with freeze_time(started + timedelta(seconds=100)):
            await _off(hass)

        c._record_run.assert_awaited()
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["planned_s"] == 600
        assert 90 <= kw["actual_s"] <= 110  # not the full window

    async def test_the_optimistic_credit_is_reconciled_down(self, hass):
        c = _coord(hass)
        started = dt_util.utcnow()
        await _dispatch(hass, c, _zone())

        with freeze_time(started + timedelta(seconds=300)):
            await _off(hass)

        # 20 mm was credited at dispatch from a -20 mm bucket; half the window ran,
        # so half of it has to come back off.
        written = [ck.args[1] for ck in c.async_write_watered_bucket.await_args_list]
        # approx: the elapsed is real wall clock, so the dispatch's own microseconds
        # are in it. The point is the half, not the millisecond.
        assert written[-1] == pytest.approx(-10.0, abs=0.01)

    async def test_the_run_no_longer_holds_the_zone(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        assert await c._sc_find_run(2) is not None

        await _off(hass)

        assert await c._sc_find_run(2) is None

    async def test_the_master_hold_is_dropped_with_it(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c.async_master_release.reset_mock()

        await _off(hass)

        c.async_master_release.assert_awaited()


class TestAFullRunIsStillAFullRun:
    async def test_a_valve_off_at_the_planned_end_completes(self, hass):
        """Completed, and recorded for the window the valve reported (#139).

        actual_s is now the off report minus the on report rather than planned_s.
        The dispatch runs under the same frozen clock as the close, so the on
        report (clamped to the dispatch) is ``started`` exactly and a close at
        the planned end is a window of exactly 600 s.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())

            frozen.tick(timedelta(seconds=600))
            await _off(hass)

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 600

    async def test_the_observed_start_is_the_dispatch_instant(self, hass):
        """Not the moment the observation arrived.

        The confirm poll runs BEFORE the watcher is armed, so anchoring the run to
        when the subscription first saw the valve would shorten every run by that
        poll -- and settle a full one as a partial, with its credit reversed.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        run = await c._sc_find_run(2)
        assert run[const.RUN_OBSERVED_START] == run[const.RUN_STARTED]

    async def test_the_flow_meter_is_not_re_seeded_by_the_observation(self, hass):
        """It was started at dispatch, for the window that actually began.

        Re-seeding it at the observed start would throw away everything sampled
        since. The engine does that because a QUEUED run's dispatch precedes its
        water by hours -- which is not true of a valve that opens as it is told.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        c._sc_start_flow_sampling.assert_awaited_once()

    async def test_the_finish_backstop_is_armed_once(self, hass):
        """Re-arming it from the observation would push it past the real close.

        Armed once, at dispatch, and already carrying a confirmed run's finish
        grace: the planned 600 s plus the 5 s debounce plus the default 4 s
        latency margin (#139). Armed at exactly the window, it beat the valve's
        own off report on every normal run.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        assert c._sc_schedule_cleanup.call_count == 1
        assert c._sc_schedule_cleanup.call_args.args == (2, 609)


class TestAConfirmedRunFreezesItsMarginAtDispatch:
    """The margin a run waits for is the one it was dispatched under (#139).

    Frozen into the record, so a margin edited mid-run cannot move a backstop
    that is already armed, and so a record without it (write-only, unverifiable,
    or persisted before this change) keeps the timing it started with.
    """

    async def test_the_default_margin_is_frozen_into_the_record(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        run = await c._sc_find_run(2)
        assert run[const.RUN_LATENCY_MARGIN] == 4

    async def test_the_zones_own_margin_is_frozen_into_the_record(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 7}))

        run = await c._sc_find_run(2)
        assert run[const.RUN_LATENCY_MARGIN] == 7

    async def test_a_write_only_run_carries_neither_margin_nor_valve_on(self, hass):
        """No confirm_entity: nothing reports the valve, nothing to wait for."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone(confirm=None))

        run = await c._sc_find_run(2)
        assert const.RUN_LATENCY_MARGIN not in run
        assert const.RUN_VALVE_ON not in run

    async def test_an_unverifiable_run_carries_neither_margin_nor_valve_on(self, hass):
        """A confirm of None is "cannot verify": the run stays write-only."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone(), valve_state="unavailable")

        run = await c._sc_find_run(2)
        assert const.RUN_LATENCY_MARGIN not in run
        assert const.RUN_VALVE_ON not in run


class TestTheValveOnReportIsClampedToTheDispatch:
    """RUN_VALVE_ON is the valve's own on report, never older than the dispatch.

    RUN_STARTED is stamped after the confirm poll returns, up to a poll after
    the water started. The valve's last_changed is closer, but a valve that was
    already open before the dispatch would drag the anchor back by however long
    it had been open, so the report is clamped to [dispatch, confirm return].
    """

    async def test_a_valve_already_open_is_anchored_at_the_dispatch(self, hass):
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started):
            c = _coord(hass)
            zone = _zone()
            c._zones[2] = zone
            # on for an hour already: the confirm poll accepts it at first read
            hass.states.async_set(
                VALVE, "on", timestamp=(started - timedelta(hours=1)).timestamp()
            )
            await hass.async_block_till_done()

            assert await c.async_run_self_closing(zone, trigger="schedule")
            await hass.async_block_till_done()

        run = await c._sc_find_run(2)
        assert run[const.RUN_VALVE_ON] == started.isoformat()

    async def test_a_valve_reporting_on_after_the_dispatch_is_anchored_at_its_report(
        self, hass
    ):
        started = dt_util.utcnow().replace(microsecond=0)
        reported = started + timedelta(seconds=0.4)
        with freeze_time(started) as frozen:
            c = _coord(hass)
            zone = _zone()

            async def _slow_confirm(zone_id, entity_id, retry=True):
                # the valve reports on 0.4 s after the dispatch, and the poll
                # that sees it returns a whole second after the dispatch
                hass.states.async_set(entity_id, "on", timestamp=reported.timestamp())
                frozen.tick(timedelta(seconds=1))
                return True

            c._confirm_valve_running = AsyncMock(side_effect=_slow_confirm)
            await _dispatch(hass, c, zone, valve_state="off")

        run = await c._sc_find_run(2)
        assert run[const.RUN_VALVE_ON] == reported.isoformat()
        assert run[const.RUN_STARTED] == (started + timedelta(seconds=1)).isoformat()

    async def test_a_report_stamped_after_the_confirm_returned_is_clamped_to_it(
        self, hass
    ):
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            c = _coord(hass)
            zone = _zone()

            async def _skewed_confirm(zone_id, entity_id, retry=True):
                stamp = (started + timedelta(seconds=5)).timestamp()
                hass.states.async_set(entity_id, "on", timestamp=stamp)
                frozen.tick(timedelta(seconds=1))
                return True

            c._confirm_valve_running = AsyncMock(side_effect=_skewed_confirm)
            await _dispatch(hass, c, zone, valve_state="off")

        run = await c._sc_find_run(2)
        assert run[const.RUN_VALVE_ON] == (started + timedelta(seconds=1)).isoformat()


class TestTheBackstopWaitsOnlyForAConfirmedValve:
    async def test_a_margin_of_zero_still_waits_out_the_debounce(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 0}))

        assert c._sc_schedule_cleanup.call_args.args == (2, 605)

    async def test_a_write_only_run_is_backstopped_at_exactly_its_window(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone(confirm=None))

        assert c._sc_schedule_cleanup.call_args.args == (2, 600)

    async def test_an_unverifiable_run_is_backstopped_at_exactly_its_window(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone(), valve_state="unavailable")

        assert c._sc_schedule_cleanup.call_args.args == (2, 600)


def _finished(hass):
    """Capture the irrigation_finished events the coordinator fires."""
    return async_capture_events(hass, f"{const.DOMAIN}_{const.EVENT_IRRIGATE_FINISHED}")


def _the_real_backstop_from_here(c):
    """Swap _coord's backstop double for the real timer, its calls still recorded.

    With the double a test reads the delay the backstop is armed with but never
    sees it fire, so it cannot show whether the backstop or a debounce comes
    first, nor what the backstop settles when it does. Dropping the instance
    doubles falls back to the coordinator's own _sc_schedule_cleanup and
    _sc_cancel_cleanup; wrapping the first keeps its calls assertable. Only a
    backstop armed after the call is real, so it is called before the dispatch
    (or the restart) whose backstop the test is about.
    """
    del c._sc_schedule_cleanup
    del c._sc_cancel_cleanup
    c._sc_schedule_cleanup = Mock(wraps=c._sc_schedule_cleanup)


class TestAMissedCloseStillSettlesViaTheBackstop:
    """A close the valve never reports is still finished, by the backstop (#139).

    The watcher settles a confirmed run on the valve's own reports. When the
    off report never comes (the close was missed, or its report was lost), the
    backstop is what ends the run, as it always was, only now at the end of the
    finish grace, planned + debounce + margin, rather than at the planned end.
    The delay it is armed with is pinned above on the double; here it is the
    real timer, so the test sees when it fires and what it settles.
    """

    async def test_a_valve_that_never_reports_off_is_finished_when_the_grace_is_out(
        self, hass
    ):
        c = _coord(hass)
        _the_real_backstop_from_here(c)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 4}))

            frozen.tick(timedelta(seconds=608))
            async_fire_time_changed(hass, dt_util.utcnow())
            await hass.async_block_till_done()

            # 608 s: past the plan, a second short of the grace (600 + 5 + 4)
            assert await c._sc_find_run(2) is not None
            c._record_run.assert_not_awaited()
            assert not finished
            c.async_master_release.assert_not_awaited()

            frozen.tick(timedelta(seconds=2))
            async_fire_time_changed(hass, dt_util.utcnow())
            await hass.async_block_till_done()

        # 610 s: the backstop, due at 609, has finished the run for its plan
        assert await c._sc_find_run(2) is None
        c._record_run.assert_awaited_once()
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 600
        assert len(finished) == 1
        c.async_master_release.assert_awaited_once()
        assert not c._sc_cleanup_timers()  # nothing left armed


class TestTheWatcherNeverWritesAWateringRunOff:
    async def test_an_unavailable_valve_does_not_end_the_run(self, hass):
        """No information is not "the run stopped"."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _set(hass, VALVE, "unavailable")

        assert await c._sc_find_run(2) is not None
        c._record_run.assert_not_awaited()

    async def test_no_give_up_clock_is_armed(self, hass):
        """A service run has no queue to wait behind -- nothing to give up on.

        A give-up clock here could only ever fire against a run that IS watering,
        reversing its credit and raising a fault while the water flowed. That is
        the defect ``arm_give_up_after_start`` documents, reached by a different
        door.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        await _set(hass, VALVE, "unavailable")

        async_fire_time_changed(
            hass,
            dt_util.utcnow()
            + timedelta(seconds=const.SERVICE_WATCH_GIVE_UP_SECONDS + 30),
        )
        await hass.async_block_till_done()

        assert await c._sc_find_run(2) is not None
        c._set_zone_fault.assert_not_called()


class TestOneOffSampleIsNotEvidenceTheWaterStopped:
    """These are the valves ``_confirm_valve_running`` is written around.

    Its own docstring: sleepy Zigbee/Tuya timers "actuate but report their new
    state back slowly, or silently drop the first command". Ending a run on the
    first `off` would settle those as partials and reverse the credit for water
    that never stopped flowing — trading the defect this feature fixes for a
    worse one on the same hardware.
    """

    async def test_a_valve_that_blips_off_and_back_on_keeps_its_run(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _set(hass, VALVE, "off")
        await _set(hass, VALVE, "on")  # back before the window is out
        await _settle(hass)

        assert await c._sc_find_run(2) is not None
        c._record_run.assert_not_awaited()

    async def test_the_run_is_not_settled_before_the_window_is_out(self, hass):
        """Held open, not finished — the decision is genuinely deferred."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _set(hass, VALVE, "off")

        assert await c._sc_find_run(2) is not None
        c._record_run.assert_not_awaited()

    async def test_a_valve_that_stays_off_still_ends_the_run(self, hass):
        """The debounce is a debounce, not a licence to ignore the valve."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _off(hass)

        assert await c._sc_find_run(2) is None


async def _report(hass, state, when, attributes=None):
    """The valve reports ``state``, stamped ``when`` (the state's last_changed)."""
    hass.states.async_set(VALVE, state, attributes, timestamp=when.timestamp())
    await hass.async_block_till_done()


class TestTheWatcherRecordsTheValvesOwnOffReport:
    """RUN_VALVE_OFF is the first off report since the last on (#139).

    Read off the event's state.last_changed rather than stamped when the
    watcher gets round to it: the evaluate runs as a task, a poll or more after
    the report, and every later off update of the same valve (an attribute
    refresh, a link-quality tick) is an event of its own that would move a
    clock-stamped value. Recorded only from an event whose previous state was
    running: an off that follows unavailable, unknown or no state the watcher
    saw carries the entity's return in its last_changed, not the close. Each
    test asserts before the debounce runs out: the report is recorded at the
    event, not when the run is settled.
    """

    async def test_an_off_event_records_the_states_last_changed(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        closed = dt_util.utcnow().replace(microsecond=0) + timedelta(seconds=2.5)

        await _report(hass, "off", closed)

        run = await c._sc_find_run(2)
        assert run[const.RUN_VALVE_OFF] == closed.isoformat()
        c._record_run.assert_not_awaited()
        await _settle(hass)

    async def test_an_attribute_only_update_does_not_move_the_off_report(self, hass):
        """HA keeps last_changed while the state text stays the same."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        closed = dt_util.utcnow().replace(microsecond=0) + timedelta(seconds=2.5)

        await _report(hass, "off", closed)
        await _report(hass, "off", closed + timedelta(seconds=3), {"linkquality": 42})

        state = hass.states.get(VALVE)
        assert state.last_changed == closed
        assert state.last_updated == closed + timedelta(seconds=3)
        run = await c._sc_find_run(2)
        assert run[const.RUN_VALVE_OFF] == closed.isoformat()
        await _settle(hass)

    async def test_an_off_after_an_unavailable_spell_keeps_the_first_off_report(
        self, hass
    ):
        """unavailable is no information, not an on: the valve closed at the first.

        The first off follows the on and is the close. The off after the spell
        follows unavailable, not a running state, and moves nothing.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        closed = dt_util.utcnow().replace(microsecond=0) + timedelta(seconds=2.5)

        await _report(hass, "off", closed)
        await _report(hass, "unavailable", closed + timedelta(seconds=1))
        await _report(hass, "off", closed + timedelta(seconds=2))

        assert hass.states.get(VALVE).last_changed == closed + timedelta(seconds=2)
        run = await c._sc_find_run(2)
        assert run[const.RUN_VALVE_OFF] == closed.isoformat()
        await _settle(hass)

    async def test_an_off_after_an_unavailable_mid_run_records_nothing(self, hass):
        """on -> unavailable -> off: the off does not follow a running state.

        Its last_changed is when the entity came back, which can be any time
        after the valve really closed. Nothing is recorded, and the run is
        settled like any close nobody reported (accepted trade-off, #139).
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        now = dt_util.utcnow().replace(microsecond=0)

        await _report(hass, "unavailable", now + timedelta(seconds=1))
        await _report(hass, "off", now + timedelta(seconds=3))

        # the off was evaluated: the debounce is running
        assert c._watchers()[2].finish_cancel is not None
        run = await c._sc_find_run(2)
        assert not run.get(const.RUN_VALVE_OFF)
        await _settle(hass)

    async def test_an_on_inside_the_debounce_clears_the_off_report(self, hass):
        """A blip is not a close: the next off starts a fresh window end."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        closed = dt_util.utcnow().replace(microsecond=0) + timedelta(seconds=2.5)
        await _report(hass, "off", closed)
        assert (await c._sc_find_run(2))[const.RUN_VALVE_OFF] == closed.isoformat()

        await _report(hass, "on", closed + timedelta(seconds=1))

        run = await c._sc_find_run(2)
        assert run is not None
        assert not run.get(const.RUN_VALVE_OFF)
        await _settle(hass)
        assert await c._sc_find_run(2) is not None
        c._record_run.assert_not_awaited()

    async def test_a_re_adopted_run_does_not_record_the_initial_off(self, hass):
        """After a restart last_changed is the entity's return, not the close.

        The watcher re-adopting the run evaluates the valve once, and finds it
        off. That evaluation must not stamp RUN_VALVE_OFF: the state it reads
        was restored when the entity came back, so its last_changed can be any
        time after the real close.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c._run_watchers = {}  # the subscription lived in memory only
        await _report(
            hass, "off", dt_util.utcnow().replace(microsecond=0) + timedelta(seconds=2)
        )

        await c.async_resume_self_closing_runs()
        await hass.async_block_till_done()

        # the initial evaluate did see the off: the debounce is running
        assert c._watchers()[2].finish_cancel is not None
        run = await c._sc_find_run(2)
        assert not run.get(const.RUN_VALVE_OFF)
        await _settle(hass)

    async def test_a_re_adopted_run_does_not_record_an_off_after_unavailable(
        self, hass
    ):
        """The valve is unavailable when the run is re-adopted, then reports off.

        After a restart a Zigbee valve comes back as unavailable first. The off
        that follows is the first report the new subscription sees, but its
        previous state is unavailable: its last_changed is the entity's return,
        not the close.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c._watch_cancel(2)  # the subscription lived in memory only
        now = dt_util.utcnow().replace(microsecond=0)
        await _report(hass, "unavailable", now + timedelta(seconds=1))

        await c.async_resume_self_closing_runs()
        await hass.async_block_till_done()
        assert c._watchers()[2].finish_cancel is None  # unavailable: no information

        await _report(hass, "off", now + timedelta(seconds=3))

        # the off was evaluated: the debounce is running
        assert c._watchers()[2].finish_cancel is not None
        run = await c._sc_find_run(2)
        assert not run.get(const.RUN_VALVE_OFF)
        await _settle(hass)

    async def test_a_record_from_before_the_update_records_nothing(self, hass):
        """No frozen margin, no finish grace: the run keeps the timing it had."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        for record in c._cfg[const.CONF_ACTIVE_VALVE_RUNS]:
            del record[const.RUN_LATENCY_MARGIN]

        await _report(
            hass, "off", dt_util.utcnow().replace(microsecond=0) + timedelta(seconds=2)
        )

        assert c._watchers()[2].finish_cancel is not None
        run = await c._sc_find_run(2)
        assert const.RUN_LATENCY_MARGIN not in run
        assert not run.get(const.RUN_VALVE_OFF)
        await _settle(hass)


async def _advance(hass, frozen, seconds):
    """Move the frozen clock on by ``seconds`` and fire every timer now due."""
    frozen.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()


async def _run_until_the_valve_closes(hass, c, zone, closed_after, *, before=None):
    """Dispatch, report the valve off ``closed_after`` s later, run out the debounce.

    All under one frozen clock: RUN_VALVE_ON is then the dispatch instant
    exactly, and the debounce timer is armed on the clock it is advanced on.
    The clock stands AT the close when the off is reported (stamped with that
    instant explicitly) and is moved PAST the debounce before the timer fires,
    so a run measured when the decision is taken, rather than at the off
    report, comes out visibly longer. ``before`` runs after the dispatch and
    before the close.
    """
    started = dt_util.utcnow().replace(microsecond=0)
    with freeze_time(started) as frozen:
        await _dispatch(hass, c, zone)
        if before is not None:
            before()
        frozen.tick(timedelta(seconds=closed_after))
        await _report(hass, "off", started + timedelta(seconds=closed_after))
        await _advance(hass, frozen, const.SERVICE_WATCH_SETTLE_SECONDS + 1)


class TestAConfirmedRunIsSettledOnItsValveWindow:
    """The debounce decides WHETHER the run ended; the reports say how long (#139).

    actual_s is the valve's off report minus its on report, and a close within
    the zone's latency margin of the planned end still completes. Before, the
    elapsed time was read when the debounce expired, 5 s after the close, and a
    completed run discarded it for planned_s, so neither the late Tuya close nor
    an early one was ever recorded as what the valve did.

    Only a close the valve reported is settled that way. With no off report on
    record the one clock left is read after the debounce, and the margin as a
    tolerance on it would let a close nobody reported complete up to debounce +
    margin short of the plan; such a run keeps the old rule.
    """

    async def test_a_close_just_after_the_window_completes_on_the_reported_window(
        self, hass
    ):
        """The Beet valve: it reports its close 2-3 s after the planned end."""
        c = _coord(hass)

        await _run_until_the_valve_closes(hass, c, _zone(), 602)

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["planned_s"] == 600
        assert kw["actual_s"] == pytest.approx(602, abs=0.01)  # not 608, not 600
        # The timed volume stays on the window the run was credited and sized
        # for; the calibration sample is priced on the window its litres were
        # measured over, which for a reported close is the reported window.
        assert c._timed_volume_l.call_args.args[1] == 600
        c._flow_calibration_check.assert_awaited_once()
        seconds = c._flow_calibration_check.await_args.args[2]
        assert seconds == pytest.approx(602, abs=0.01)  # not the 600 s plan

    async def test_the_watcher_settles_it_before_the_real_backstop_fires(self, hass):
        """The same close with the backstop's real timer armed, not its double.

        The test above settles against _coord's backstop double, which never
        fires, so on its own it cannot show that the watcher gets there first.
        Here the backstop is the real timer, due at 609 (600 + 5 + 4): the
        debounce, due at 607, settles the run on the reported window, and the
        backstop, cancelled with the run, never settles it a second time.

        The clock is walked past the planned end before the close is reported,
        not jumped over it: a timer that falls due inside a jump is only
        queued, and the time fired next runs the debounce ahead of it, whose
        settle cancels it unrun. A backstop armed at the plan would so never
        get its live turn at 600, and the test could not tell it from one
        armed at 609.
        """
        c = _coord(hass)
        _the_real_backstop_from_here(c)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 4}))
            await _advance(hass, frozen, 601)  # past the plan, the valve still on
            frozen.tick(timedelta(seconds=1))
            await _report(hass, "off", started + timedelta(seconds=602))

            await _advance(hass, frozen, 6)  # 608: the debounce (607) is out

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == pytest.approx(602, abs=0.01)  # not 600, not 608
            assert len(finished) == 1

            await _advance(hass, frozen, 2)  # 610: past where the backstop was due

            c._record_run.assert_awaited_once()  # no second settle
            assert len(finished) == 1
            c.async_master_release.assert_awaited_once()
            watcher = c._watchers().get(2)
            assert watcher is None or watcher.finish_cancel is None  # none pending
            assert not c._sc_cleanup_timers()  # the backstop went with the run

    async def test_a_close_inside_the_margin_completes_on_the_reported_window(
        self, hass
    ):
        """3 s short with the default 4 s margin: a normal end, not a stop."""
        c = _coord(hass)

        await _run_until_the_valve_closes(hass, c, _zone(), 597)

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == pytest.approx(597, abs=0.01)

    async def test_a_close_beyond_the_margin_is_a_partial_credited_for_its_window(
        self, hass
    ):
        c = _coord(hass)

        await _run_until_the_valve_closes(hass, c, _zone(), 590)

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(590, abs=0.01)  # not 596
        # 20 mm credited at dispatch from -20 mm; 590 of 600 s were delivered
        written = [ck.args[1] for ck in c.async_write_watered_bucket.await_args_list]
        assert written[-1] == pytest.approx(-20 + 20 * 590 / 600, abs=0.001)

    async def test_a_margin_of_zero_still_tolerates_one_second(self, hass):
        """max(1, margin): the old one-second slack is the floor, not the margin."""
        c = _coord(hass)

        await _run_until_the_valve_closes(
            hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 0}), 599.5
        )

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == pytest.approx(599.5, abs=0.01)

    async def test_a_margin_of_zero_settles_a_close_beyond_that_second_as_partial(
        self, hass
    ):
        c = _coord(hass)

        await _run_until_the_valve_closes(
            hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 0}), 598.5
        )

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(598.5, abs=0.01)

    async def test_an_off_after_an_unavailable_mid_run_keeps_the_old_rule(self, hass):
        """on -> unavailable -> off mid-run: no off report, so the old rule settles.

        The off at +302 s follows unavailable, so its last_changed is the
        entity's return and not the close, and nothing is recorded. The run is
        settled like any close nobody reported: on its elapsed time since the
        observed start, read when the debounce decides (+308 s), and not on the
        302 s a recorded off would have given.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=300))
            await _report(hass, "unavailable", started + timedelta(seconds=300))
            frozen.tick(timedelta(seconds=2))
            await _report(hass, "off", started + timedelta(seconds=302))

            run = await c._sc_find_run(2)
            assert not run.get(const.RUN_VALVE_OFF)
            observed = dt_util.parse_datetime(run[const.RUN_OBSERVED_START])

            await _advance(hass, frozen, const.SERVICE_WATCH_SETTLE_SECONDS + 1)
            decided = dt_util.utcnow()

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(
            (decided - observed).total_seconds(), abs=0.01
        )  # 308 s, not 302

    async def test_an_unreported_close_seven_seconds_early_stays_partial(self, hass):
        """No off report: the margin is not added to a clock that holds the debounce.

        The valve drops out at +590 s and comes back off at +593 s, so nothing
        is recorded and the debounce decides at +598 s, exactly as it would
        live. The old rule reads that clock: 598 + 1 < 600 is a partial. The
        margin as tolerance on the same clock (598 + 4 >= 600) would complete
        it, and with it any close nobody reported up to 9 s short of the plan.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=590))
            await _report(hass, "unavailable", started + timedelta(seconds=590))
            frozen.tick(timedelta(seconds=3))
            await _report(hass, "off", started + timedelta(seconds=593))
            assert not (await c._sc_find_run(2)).get(const.RUN_VALVE_OFF)

            await _advance(hass, frozen, const.SERVICE_WATCH_SETTLE_SECONDS)  # 598

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(598, abs=0.01)
        c._flow_calibration_check.assert_not_awaited()

    async def test_an_unreported_close_inside_the_old_second_completes_for_its_plan(
        self, hass
    ):
        """No off report, decided at +599.5 s: completed and recorded for the plan.

        599.5 + 1 >= 600 completes under the old rule, through the finish that
        has no reported window to record, so actual_s is planned_s and not the
        599.5 s the clock read after the debounce.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=592))
            await _report(hass, "unavailable", started + timedelta(seconds=592))
            frozen.tick(timedelta(seconds=2.5))
            await _report(hass, "off", started + timedelta(seconds=594.5))
            assert not (await c._sc_find_run(2)).get(const.RUN_VALVE_OFF)

            await _advance(hass, frozen, const.SERVICE_WATCH_SETTLE_SECONDS)  # 599.5

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 600

    async def test_a_record_from_before_the_update_keeps_the_old_rule(self, hass):
        """No frozen margin: elapsed at the decision + 1 >= planned, planned_s kept.

        Closed at 593.5 s, so the debounce decides at 599.5 s. The old rule
        completes that with actual_s == planned_s; the window rule would have
        recorded 599.5 s, so this pins that such a record is not routed there.
        """
        c = _coord(hass)

        def _strip_the_new_keys():
            for record in c._cfg[const.CONF_ACTIVE_VALVE_RUNS]:
                del record[const.RUN_LATENCY_MARGIN]
                del record[const.RUN_VALVE_ON]

        await _run_until_the_valve_closes(
            hass, c, _zone(), 593.5, before=_strip_the_new_keys
        )

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 600


class TestACloseReportedPastTheMarginIsKnownAndDeliberatelyUnchanged:
    """A close reported later than the margin is still finished for its plan (#139).

    Known and deliberately unchanged, as agreed on #139 (2026-09-16). With the
    off reported at +606 and a margin of 4 s the debounce would decide at +611,
    but the backstop is due at +609 (600 + 5 + 4) and comes first. It finishes
    the run for planned_s, as the backstop always has, and the off report
    already on the record is not used. Settling that run on the reported
    window instead would only make its record better than it is today, not
    close a hole the grace opens, so it waits. Pinned so it reads as a
    decision, not an oversight, and so changing it is a decision too.
    """

    async def test_the_backstop_finishes_it_for_the_plan_before_the_debounce(
        self, hass
    ):
        c = _coord(hass)
        _the_real_backstop_from_here(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 4}))
            frozen.tick(timedelta(seconds=606))
            await _report(hass, "off", started + timedelta(seconds=606))

            run = await c._sc_find_run(2)
            reported = (started + timedelta(seconds=606)).isoformat()
            assert run[const.RUN_VALVE_OFF] == reported
            assert c._watchers()[2].finish_cancel is not None  # due at 611

            await _advance(hass, frozen, 4)  # 610: the backstop (609) is out

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == kw["planned_s"] == 600  # not the reported 606

            await _advance(hass, frozen, 2)  # 612: where the debounce was due

            c._record_run.assert_awaited_once()  # no second settle
            watcher = c._watchers().get(2)
            assert watcher is None or watcher.finish_cancel is None  # none pending
            assert not c._sc_cleanup_timers()


class TestAWriteOnlyValveIsUntouched:
    async def test_a_zone_with_no_confirm_entity_is_not_watched(self, hass):
        """Nothing to subscribe to, and the hardware still owns the close."""
        c = _coord(hass)

        await _dispatch(hass, c, _zone(confirm=None))

        run = await c._sc_find_run(2)
        assert const.RUN_WATCH_ENTITY not in run
        assert const.RUN_OBSERVED_START not in run
        assert not c._watchers()

    async def test_an_unreadable_confirm_entity_is_not_watched(self, hass):
        """``None`` from the confirm poll means "cannot verify", not "confirmed"."""
        c = _coord(hass)

        await _dispatch(hass, c, _zone(), valve_state="unavailable")

        run = await c._sc_find_run(2)
        assert const.RUN_WATCH_ENTITY not in run
        assert not c._watchers()


def _stops_seen_by_the_record(hass, c):
    """The stop script's calls, and how many had been sent when the run was recorded.

    A stop closes the valve first and settles the run second, whichever way it
    settles; the count read from inside _record_run pins that order.
    """
    stops = async_mock_service(hass, "script", "stop_irrigation_beet")
    seen = []
    c._record_run = AsyncMock(side_effect=lambda *a, **kw: seen.append(len(stops)))
    return stops, seen


class TestAManualStopMeasuresFromTheValvesOnReport:
    """A manual stop of a confirmed run is measured on the valve's reports (#139).

    async_stop_self_closing read the clock from RUN_OBSERVED_START, which for a
    service run is RUN_STARTED, stamped when the confirm poll returned. So a
    stopped run was measured from a later instant than a watcher-settled one.
    A stop that closes the valve itself is now measured from RUN_VALVE_ON.
    Before the planned end it books the time to the stop, capped at the plan,
    and never a stored off report. Past the planned end the run is only waiting
    in its finish grace, and a stop there used to book the grace as watering;
    it now settles the run by the watcher's rule on the same reports: completed
    within the tolerance, else a partial on the window. Every stop happens
    under the dispatch's frozen clock, so the anchors are exact.
    """

    async def test_a_stop_mid_run_is_measured_from_the_valve_on_report(self, hass):
        """The valve was on before the dispatch: anchored at the dispatch."""
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            run = await c._sc_find_run(2)
            assert run[const.RUN_VALVE_ON] == started.isoformat()

            frozen.tick(timedelta(seconds=100))
            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["planned_s"] == 600
        assert kw["actual_s"] == pytest.approx(100, abs=0.01)
        written = [ck.args[1] for ck in c.async_write_watered_bucket.await_args_list]
        assert written[-1] == pytest.approx(-20 + 20 * 100 / 600, abs=0.001)

    async def test_a_valve_reporting_on_after_the_dispatch_is_measured_from_its_report(
        self, hass
    ):
        """On reported 0.4 s after the dispatch, the confirm returning at 1 s.

        RUN_STARTED (and so RUN_OBSERVED_START) is the confirm return; measured
        from there the stop would book 99.0 s, 0.6 s less than the valve ran.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        reported = started + timedelta(seconds=0.4)
        with freeze_time(started) as frozen:

            async def _slow_confirm(zone_id, entity_id, retry=True):
                hass.states.async_set(entity_id, "on", timestamp=reported.timestamp())
                frozen.tick(timedelta(seconds=1))
                return True

            c._confirm_valve_running = AsyncMock(side_effect=_slow_confirm)
            await _dispatch(hass, c, _zone(), valve_state="off")
            run = await c._sc_find_run(2)
            assert run[const.RUN_VALVE_ON] == reported.isoformat()
            assert (
                run[const.RUN_OBSERVED_START]
                == (started + timedelta(seconds=1)).isoformat()
            )

            frozen.tick(timedelta(seconds=99))  # 100 s after the dispatch
            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(99.6, abs=0.01)  # not 99.0

    async def test_a_stop_before_the_planned_end_is_not_booked_on_an_off_report(
        self, hass
    ):
        """Off reported at +300, stopped at +302: 302 s, not 300.

        Before the planned end the stop is the end of the run, as it always was.
        The off report is still inside its debounce, which has not decided
        whether it was the close or a blip, so it is not taken as the end.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=300))
            await _report(hass, "off", started + timedelta(seconds=300))
            frozen.tick(timedelta(seconds=2))  # 302: the debounce (305) not fired

            run = await c._sc_find_run(2)
            assert (
                run[const.RUN_VALVE_OFF]
                == (started + timedelta(seconds=300)).isoformat()
            )

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_PARTIAL
            assert kw["actual_s"] == pytest.approx(302, abs=0.01)  # not 300
            written = [
                ck.args[1] for ck in c.async_write_watered_bucket.await_args_list
            ]
            assert written[-1] == pytest.approx(-20 + 20 * 302 / 600, abs=0.001)

            # _coord's _os_cancel_watch is a double, so the debounce is still
            # armed; run it out against the removed run, which it leaves alone.
            await _advance(hass, frozen, 4)  # 306

        c._record_run.assert_awaited_once()

    async def test_a_stop_just_before_the_planned_end_is_capped_at_the_plan(self, hass):
        """On reported 0.6 s before the confirm return, stopped 0.2 s before the end.

        The stop comes 599.8 s after RUN_STARTED, where the backstop is anchored,
        so before the planned end, but 600.4 s after the valve's on report. It
        books the plan, not more.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        reported = started + timedelta(seconds=0.4)
        with freeze_time(started) as frozen:

            async def _slow_confirm(zone_id, entity_id, retry=True):
                hass.states.async_set(entity_id, "on", timestamp=reported.timestamp())
                frozen.tick(timedelta(seconds=1))
                return True

            c._confirm_valve_running = AsyncMock(side_effect=_slow_confirm)
            await _dispatch(hass, c, _zone(), valve_state="off")

            frozen.tick(timedelta(seconds=599.8))  # 600.8 s after the dispatch
            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == 600  # not 599.8, not 600.4
        assert c._timed_volume_l.call_args.args[1] == 600

    async def test_a_stop_in_the_grace_after_an_off_report_inside_the_tolerance_completes(
        self, hass
    ):
        """Off at +597 (3 s short, default 4 s margin), stopped at +601.

        Past the planned end the run is only waiting for its debounce, which
        would complete it on this window at +602. The stop settles it the same
        way, after closing the valve as any stop does: completed on 597 s, with
        one finished event and the calibration sample priced on that window.
        """
        c = _coord(hass)
        stops, seen = _stops_seen_by_the_record(hass, c)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=597))
            await _report(hass, "off", started + timedelta(seconds=597))
            frozen.tick(timedelta(seconds=4))  # 601: the debounce (602) not fired

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

            assert await c._sc_find_run(2) is None
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["planned_s"] == 600
            assert kw["actual_s"] == pytest.approx(597, abs=0.01)  # not 601
            assert seen == [1]  # the valve was closed before the run was settled
            assert stops[0].data == {"zone_id": 2, "dauer": 0}

            await _advance(hass, frozen, 2)  # 603: the debounce, against no run

        c._record_run.assert_awaited_once()
        assert len(finished) == 1
        c._flow_calibration_check.assert_awaited_once()
        seconds = c._flow_calibration_check.await_args.args[2]
        assert seconds == pytest.approx(597, abs=0.01)  # not the 600 s plan

    async def test_a_stop_in_the_grace_after_a_late_off_report_completes_on_it(
        self, hass
    ):
        """Off reported at 601, stopped at 604 while the debounce still decides.

        The watcher would complete this run on 601 s when its debounce ran out
        at 606; the stop settles it on the same window. The valve closed a
        second late, and a completed run records the 601 s it reported.
        """
        c = _coord(hass)
        stops, seen = _stops_seen_by_the_record(hass, c)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=601))
            await _report(hass, "off", started + timedelta(seconds=601))
            frozen.tick(timedelta(seconds=3))  # 604: the debounce (606) not fired

            run = await c._sc_find_run(2)
            assert (
                run[const.RUN_VALVE_OFF]
                == (started + timedelta(seconds=601)).isoformat()
            )
            c._record_run.assert_not_awaited()

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == pytest.approx(601, abs=0.01)  # not 604
            assert seen == [1]

            # _coord's _os_cancel_watch is a double, so the debounce is still
            # armed; run it out against the removed run, which it leaves alone.
            await _advance(hass, frozen, 3)  # 607

        c._record_run.assert_awaited_once()
        assert len(finished) == 1

    async def test_a_stop_in_the_grace_after_an_off_report_beyond_the_tolerance_is_partial(
        self, hass
    ):
        """Margin 0: off at +598 is 2 s short, beyond the 1 s floor; stopped at +601.

        The watcher would settle that as a partial on 598 s at +603, and so does
        the stop: the credit is reconciled to what the window delivered, and no
        finished event is fired.
        """
        c = _coord(hass)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone(**{const.ZONE_LATENCY_MARGIN: 0}))
            frozen.tick(timedelta(seconds=598))
            await _report(hass, "off", started + timedelta(seconds=598))
            frozen.tick(timedelta(seconds=3))  # 601: the debounce (603) not fired

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_PARTIAL
            assert kw["actual_s"] == pytest.approx(598, abs=0.01)  # not 601
            written = [
                ck.args[1] for ck in c.async_write_watered_bucket.await_args_list
            ]
            assert written[-1] == pytest.approx(-20 + 20 * 598 / 600, abs=0.001)

            await _advance(hass, frozen, 3)  # 604: the debounce, against no run

        c._record_run.assert_awaited_once()
        assert not finished
        c._flow_calibration_check.assert_not_awaited()

    async def test_a_stop_in_the_grace_with_the_valve_still_on_completes_for_the_plan(
        self, hass
    ):
        """No off report yet at 604: the run ran its plan and is settled as such.

        The watcher's rule on the same reports: while the valve still reports on
        the window is bounded by the plan, so the run completes on 600 s, with
        the finished event, after the stop has closed the valve. Not a partial
        for 604 s: the grace is waiting for a report, not watering.
        """
        c = _coord(hass)
        stops, seen = _stops_seen_by_the_record(hass, c)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=604))
            assert not (await c._sc_find_run(2)).get(const.RUN_VALVE_OFF)

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 600  # not 604
        assert c._timed_volume_l.call_args.args[1] == 600  # not 604
        assert seen == [1]
        assert stops[0].data == {"zone_id": 2, "dauer": 0}
        assert len(finished) == 1

    async def test_a_stop_exactly_at_the_planned_end_is_settled_in_the_grace(
        self, hass
    ):
        """600 s after RUN_STARTED the plan is out and the grace has begun.

        With the valve still on, the watcher's rule completes the run for its
        plan; before the end the same stop would be a partial.
        """
        c = _coord(hass)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=600))

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 600
        assert len(finished) == 1

    async def test_a_stop_all_in_the_grace_settles_the_run_the_same_way(self, hass):
        """Stop all reaches the run in its grace and settles it as a single stop."""
        c = _coord(hass)
        stops, seen = _stops_seen_by_the_record(hass, c)
        finished = _finished(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=601))
            await _report(hass, "off", started + timedelta(seconds=601))
            frozen.tick(timedelta(seconds=3))  # 604: the debounce (606) not fired
            # get_active_runs reads the persisted runs off the live config.
            c.store.config.active_valve_runs = c._cfg[const.CONF_ACTIVE_VALVE_RUNS]
            assert "2" in c.get_active_runs()

            await c.async_stop_all_zones()
            await hass.async_block_till_done()

            assert await c._sc_find_run(2) is None
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == pytest.approx(601, abs=0.01)
            assert seen == [1]

            await _advance(hass, frozen, 3)  # 607: the debounce, against no run

        c._record_run.assert_awaited_once()
        assert len(finished) == 1

    async def test_a_completing_stop_books_exactly_what_the_watcher_would(self, hass):
        """The same late close settled twice: by the debounce, and by a stop at +604.

        With a measured volume, so both paths reconcile the bucket from it.
        Everything the run books must come out the same and once: the record,
        the bucket, the meter and what it learned, the stamp, the finished
        event, the calibration sample, the deferred calculation and the master
        hold (released by the stop before its close and again, a no-op, by the
        finish).
        """

        async def _close_late(by_stop):
            c = _coord(hass)
            c._sc_finish_flow = Mock(return_value=(90.0, {"flow_learned": 1}))
            finished = _finished(hass)
            started = dt_util.utcnow().replace(microsecond=0)
            with freeze_time(started) as frozen:
                await _dispatch(hass, c, _zone())
                frozen.tick(timedelta(seconds=601))
                await _report(hass, "off", started + timedelta(seconds=601))
                if by_stop:
                    frozen.tick(timedelta(seconds=3))
                    assert await c.async_stop_self_closing(2)
                    await hass.async_block_till_done()
                await _advance(hass, frozen, const.SERVICE_WATCH_SETTLE_SECONDS + 1)
            assert await c._sc_find_run(2) is None
            return {
                "record": c._record_run.await_args_list,
                "bucket": c.async_write_watered_bucket.await_args_list,
                "meter": c._sc_finish_flow.call_count,
                "learned": c.store.async_update_zone.await_args_list,
                "stamp": c._stamp_run_finalized.await_args_list,
                "finished": [event.data for event in finished],
                "calibration": c._flow_calibration_check.await_args_list,
                "deferred": c.async_run_deferred_calculation.await_count,
                "released": {ck.args for ck in c.async_master_release.await_args_list},
            }

        watched = await _close_late(by_stop=False)
        stopped = await _close_late(by_stop=True)

        assert stopped == watched
        assert len(watched["record"]) == 1
        kw = watched["record"][0].kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == pytest.approx(601, abs=0.01)
        assert kw["volume_l"] == 90.0
        assert watched["meter"] == 1
        assert len(watched["finished"]) == 1
        assert len(watched["calibration"]) == 1

    async def test_the_watchers_own_partial_keeps_its_observed_start(self, hass):
        """The watcher's partial for a close nobody reported is not a stop.

        on -> unavailable -> off records no off report, so the watcher settles
        the run on its elapsed time since RUN_OBSERVED_START when the debounce
        decides (+308 s) and hands async_stop_self_closing no actual_s. Its
        completion was decided on that clock, so the partial is booked on it
        too: 307 s from the confirm return, not 307.6 s from the on report
        0.6 s earlier, which only a stop that closes the valve is measured from.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        reported = started + timedelta(seconds=0.4)
        with freeze_time(started) as frozen:

            async def _slow_confirm(zone_id, entity_id, retry=True):
                hass.states.async_set(entity_id, "on", timestamp=reported.timestamp())
                frozen.tick(timedelta(seconds=1))
                return True

            c._confirm_valve_running = AsyncMock(side_effect=_slow_confirm)
            await _dispatch(hass, c, _zone(), valve_state="off")
            frozen.tick(timedelta(seconds=299))  # 300 s after the dispatch
            await _report(hass, "unavailable", started + timedelta(seconds=300))
            frozen.tick(timedelta(seconds=2))
            await _report(hass, "off", started + timedelta(seconds=302))
            assert not (await c._sc_find_run(2)).get(const.RUN_VALVE_OFF)

            await _advance(hass, frozen, const.SERVICE_WATCH_SETTLE_SECONDS + 1)

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(307, abs=0.01)  # not 307.6

    async def test_a_write_only_run_keeps_the_elapsed_since_its_start(self, hass):
        """No valve reports, no finish grace: measured from RUN_STARTED as before."""
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone(confirm=None))
            run = await c._sc_find_run(2)
            assert run[const.RUN_STARTED] == started.isoformat()
            assert const.RUN_VALVE_ON not in run

            frozen.tick(timedelta(seconds=100))
            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(100, abs=0.01)


class TestTheSubscriptionSurvivesARestart:
    async def test_a_run_still_inside_its_window_is_re_adopted(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c._run_watchers = {}  # the subscription lived in memory only

        await c.async_resume_self_closing_runs()
        await hass.async_block_till_done()

        assert 2 in c._watchers()

    async def test_and_it_still_ends_the_run_on_a_valve_off(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c._run_watchers = {}
        await c.async_resume_self_closing_runs()
        await hass.async_block_till_done()

        await _off(hass)

        assert await c._sc_find_run(2) is None


def _ha_goes_down(c):
    """HA stops: everything but the persisted run record lived in memory.

    _watch_cancel drops each watcher with its subscription and a pending
    debounce, as the process dying would; left armed, that debounce would fire
    into the watcher re-adopted after the restart and settle the run itself.
    The backstop and master doubles are reset so the restart's own calls are
    the only ones seen.
    """
    for zone_id in list(c._watchers()):
        c._watch_cancel(zone_id)
    c._run_watchers = {}
    c._sc_schedule_cleanup.reset_mock()
    c.async_master_acquire.reset_mock()


async def _ha_comes_back(hass, c):
    await c.async_resume_self_closing_runs()
    await hass.async_block_till_done()


class TestARestartCarriesTheFinishGrace:
    """A confirmed service run re-adopted after a restart keeps its grace (#139).

    The backstop is re-armed for planned + debounce + margin minus the time
    already elapsed since RUN_STARTED (downtime included), and a run is
    finished outright only once that whole grace is out, then for its plan
    whatever its record holds. Past the plan the master is not requested
    again: the valve's own countdown is over. Dispatch, downtime and restart
    happen under one frozen clock. The backstop stays _coord's double, so the
    delay it is armed with is asserted directly and the re-adopted watcher's
    own decision is seen even where the real backstop would come first; for a
    close nobody reported, both settle the run the same way, for its plan.
    """

    async def test_a_run_inside_its_window_re_arms_the_backstop_with_the_grace(
        self, hass
    ):
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=100))

            await _ha_comes_back(hass, c)

            c._sc_schedule_cleanup.assert_called_once_with(2, 509.0)  # 600 + 9 - 100
            c.async_master_acquire.assert_awaited_once()
            assert 2 in c._watchers()
            assert c._watchers()[2].finish_cancel is None
            assert await c._sc_find_run(2) is not None
            c._record_run.assert_not_awaited()

    async def test_a_restart_exactly_at_the_plan_takes_no_master_hold(self, hass):
        """The plan is out, the grace is not: waited out, but without the pump.

        The valve's own countdown has ended, so the master is not switched on
        again for it; the backstop and the watcher are re-armed as inside the
        window.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=600))

            await _ha_comes_back(hass, c)

            c.async_master_acquire.assert_not_awaited()
            c._sc_schedule_cleanup.assert_called_once_with(2, 9.0)
            assert 2 in c._watchers()
            assert await c._sc_find_run(2) is not None
            c._record_run.assert_not_awaited()

    async def test_a_restart_inside_the_grace_does_not_finish_a_valve_still_on(
        self, hass
    ):
        """+604 is past the plan but not past the grace: the close may still come.

        The pump is not brought back up for a valve whose own countdown is over.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=604))

            await _ha_comes_back(hass, c)

            assert await c._sc_find_run(2) is not None
            c._record_run.assert_not_awaited()
            c._sc_schedule_cleanup.assert_called_once_with(2, 5.0)
            c.async_master_acquire.assert_not_awaited()
            assert 2 in c._watchers()

    async def test_a_valve_found_off_inside_the_grace_completes_for_its_plan(
        self, hass
    ):
        """Closed while HA was down: no off report, so the old rule settles it.

        The re-adopted watcher's first evaluate sees the off but does not store
        it (its last_changed is the entity's return, not the close). After the
        debounce the run is settled like any close nobody reported: 610 s since
        its start plus the one second reach the plan, so it completes for its
        plan.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=604))
            await _report(hass, "off", started + timedelta(seconds=604))

            await _ha_comes_back(hass, c)

            assert await c._sc_find_run(2) is not None  # not finished outright
            c._record_run.assert_not_awaited()
            c._sc_schedule_cleanup.assert_called_once_with(2, 5.0)
            c.async_master_acquire.assert_not_awaited()
            assert not (await c._sc_find_run(2)).get(const.RUN_VALVE_OFF)
            assert c._watchers()[2].finish_cancel is not None  # debounce due at 609

            await _advance(hass, frozen, 6)  # 610

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == kw["planned_s"] == 600

    async def test_a_valve_back_from_unavailable_completes_for_its_plan(self, hass):
        """Restart at +604 with the valve unavailable; it reports off at +606.

        That off follows unavailable, not a running state: its last_changed is
        the valve's return, so it is not stored as the close, and the run is
        settled like any close nobody reported: completed for its plan, not on
        606.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=604))
            await _report(hass, "unavailable", started + timedelta(seconds=604))

            await _ha_comes_back(hass, c)

            assert await c._sc_find_run(2) is not None  # not finished outright
            c._sc_schedule_cleanup.assert_called_once_with(2, 5.0)
            c.async_master_acquire.assert_not_awaited()
            assert c._watchers()[2].finish_cancel is None  # no information yet

            frozen.tick(timedelta(seconds=2))
            await _report(hass, "off", started + timedelta(seconds=606))

            assert not (await c._sc_find_run(2)).get(const.RUN_VALVE_OFF)
            assert c._watchers()[2].finish_cancel is not None  # debounce due at 611

            await _advance(hass, frozen, 6)  # 612

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == kw["planned_s"] == 600  # not 606

    async def test_a_valve_found_off_mid_run_is_a_partial_up_to_the_decision(
        self, hass
    ):
        """Closed while HA was down, 400 s short: a partial up to the decision.

        The close itself was never reported, so the run is settled like any
        close nobody reported, on its elapsed time when the debounce decides:
        restart at +200 plus the 5 s debounce. Still inside the plan, the
        master hold is taken again.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=200))
            await _report(hass, "off", started + timedelta(seconds=150))

            await _ha_comes_back(hass, c)

            c._sc_schedule_cleanup.assert_called_once_with(2, 409.0)  # 600 + 9 - 200
            c.async_master_acquire.assert_awaited_once()
            assert c._watchers()[2].finish_cancel is not None  # debounce due at 205

            await _advance(hass, frozen, 5)  # 205

            assert await c._sc_find_run(2) is None
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_PARTIAL
            assert kw["actual_s"] == pytest.approx(205, abs=0.01)
            written = [
                ck.args[1] for ck in c.async_write_watered_bucket.await_args_list
            ]
            assert written[-1] == pytest.approx(-20 + 20 * 205 / 600, abs=0.001)

    async def test_a_stored_off_report_inside_the_grace_settles_on_its_window(
        self, hass
    ):
        """Off reported at +601, HA gone before the debounce decided (606).

        Back at +602, the re-adopted watcher's debounce (due 607) comes before
        the re-armed backstop (due 609) and settles the run on the stored
        report. The backstop is the real timer here, so the order is the one a
        live restart has: from +604 on it is re-armed for no more than the
        debounce and, armed first, would finish the run for its plan.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=601))
            await _report(hass, "off", started + timedelta(seconds=601))
            assert c._watchers()[2].finish_cancel is not None  # due at 606
            _ha_goes_down(c)  # the pending debounce dies with the process
            _the_real_backstop_from_here(c)  # the restart arms the only real timer
            frozen.tick(timedelta(seconds=1))

            await _ha_comes_back(hass, c)  # +602

            run = await c._sc_find_run(2)
            assert (
                run[const.RUN_VALVE_OFF]
                == (started + timedelta(seconds=601)).isoformat()
            )
            c._record_run.assert_not_awaited()
            c._sc_schedule_cleanup.assert_called_once_with(2, 7.0)  # 609 - 602
            c.async_master_acquire.assert_not_awaited()
            assert c._watchers()[2].finish_cancel is not None  # due at 607

            await _advance(hass, frozen, 6)  # 608: the debounce out, the backstop not

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == pytest.approx(601, abs=0.01)  # not 600, not 608
            assert not c._sc_cleanup_timers()  # the backstop went with the run

    async def test_a_restart_exactly_at_the_end_of_the_grace_finishes_the_run(
        self, hass
    ):
        """At planned + grace the whole grace is out: finished outright, for its plan."""
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=609))

            await _ha_comes_back(hass, c)

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == kw["planned_s"] == 600
            assert 2 not in c._watchers()
            c._sc_schedule_cleanup.assert_not_called()
            c.async_master_acquire.assert_not_awaited()

    async def test_a_stored_off_report_past_the_grace_is_finished_for_the_plan(
        self, hass
    ):
        """A pin of a known case, deliberately left as it was.

        The watcher stored the valve's off report (+601) before HA went down,
        and the restart comes after the whole grace (+700). The run is finished
        for its plan, as the backstop finishes such a run. Settling it on the
        reported 601 instead would make the record better than it has been,
        not close a hole the grace opens.
        """
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            frozen.tick(timedelta(seconds=601))
            await _report(hass, "off", started + timedelta(seconds=601))
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=99))

            await _ha_comes_back(hass, c)  # +700

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == kw["planned_s"] == 600  # not 601
            assert 2 not in c._watchers()
            c._sc_schedule_cleanup.assert_not_called()
            c.async_master_acquire.assert_not_awaited()

    async def test_no_off_report_past_the_grace_completes_for_the_plan_at_once(
        self, hass
    ):
        """Nothing observed the close: completed for its plan, as before."""
        c = _coord(hass)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _dispatch(hass, c, _zone())
            _ha_goes_down(c)
            frozen.tick(timedelta(seconds=700))
            await _report(hass, "off", started + timedelta(seconds=650))

            await _ha_comes_back(hass, c)

            assert await c._sc_find_run(2) is None
            c._record_run.assert_awaited_once()
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == kw["planned_s"] == 600
            assert 2 not in c._watchers()
            c._sc_schedule_cleanup.assert_not_called()
            c.async_master_acquire.assert_not_awaited()


FLOW = "sensor.zone_flow"
RATE = 10.0  # L/min from the open: 2.5 L a poll, 1/6 L a second
COUNTER = {"unit": "L", "state_class": "total_increasing"}


def _metered(c):
    """Swap _coord's flow doubles for the real sampler and its finish.

    _coord stubs both, because the watcher tests are not about litres. These
    are, so the meter, its 15 s interval and its final read are real. The timed
    volume becomes 1 L, which none of these runs meters, so a run that lost its
    measurement cannot pass for one that kept it.
    """
    del c._sc_start_flow_sampling
    del c._sc_finish_flow
    c._timed_volume_l = Mock(return_value=1.0)


def _metered_zone(duration, **kw):
    return _zone(duration=duration, **{const.ZONE_FLOW_SENSOR: FLOW}, **kw)


async def _flow(hass, value, unit="L/min", state_class="measurement"):
    """The flow sensor reads ``value``."""
    hass.states.async_set(
        FLOW, str(value), {"unit_of_measurement": unit, "state_class": state_class}
    )
    await hass.async_block_till_done()


async def _walk(hass, frozen, seconds):
    """Walk the clock on ``seconds`` in steps of at most one poll.

    The sampler's interval re-arms itself a poll after it fires, so a jump
    fires one late tick for several and shifts every later one. Walked from
    the dispatch, each tick fires on time, at a multiple of the poll.
    """
    while seconds > 0:
        step = min(seconds, const.FLOW_POLL_INTERVAL)
        await _advance(hass, frozen, step)
        seconds -= step


def _litres(c):
    """The litres the finished run was recorded with."""
    return c._record_run.await_args.kwargs["volume_l"]


class TestAConfirmedRunsFlowEndsAtItsOffReport:
    """A rate sensor is metered to the valve's off report, not to the settle (#139).

    The flow meter credits each interval at the rate read at its end. Before
    the finish grace the backstop read the sensor at the planned end, with the
    valve still open. A confirmed run is now finalised after its close, by the
    watcher the debounce later or by the backstop at the end of the grace, so
    the read that ends the interval spanning the close, a tick after it or the
    final read, finds the water stopped and credits that whole interval, up to
    a poll of flow the valve reported, at nothing. A sensor that holds its
    last value credits the seconds after the close instead. With the off
    report on the record the integration ends there, the last interval at its
    last measured rate. A run without the report and a totalizer are metered
    as before.

    The sensor reads 10 L/min from the open, the clock is walked so every tick
    fires on time, and the expected litres are 10 L/min over the seconds from
    the open to the close.
    """

    async def test_a_close_settled_by_the_watcher_is_metered_to_its_off_report(
        self, hass
    ):
        """612 s plan, closed at +614, settled at +619: 614 s of flow.

        The tick at +615 reads the water stopped and used to credit (600, 615]
        at nothing, 14 s the valve reported open; so did the read at +619.
        """
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(612))
            await _walk(hass, frozen, 614)
            await _flow(hass, 0)
            await _report(hass, "off", started + timedelta(seconds=614))
            await _advance(hass, frozen, 1)  # 615: the tick reads nothing
            await _advance(hass, frozen, 4)  # 619: the debounce settles the run

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == pytest.approx(614, abs=0.01)
        assert _litres(c) == pytest.approx(RATE * 614 / 60, abs=0.01)  # not 100
        assert 2 not in c._sc_meters()

    async def test_a_sensor_that_holds_its_last_value_is_not_metered_past_it(
        self, hass
    ):
        """The same close with a sensor still reading 10 L/min after it.

        Its reads at +615 and +619 used to credit the 5 s after the close as
        water: 619 s of flow for a valve that reported 614.
        """
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(612))
            await _walk(hass, frozen, 614)
            await _report(hass, "off", started + timedelta(seconds=614))
            await _advance(hass, frozen, 1)  # 615: the tick still reads 10
            await _advance(hass, frozen, 4)  # 619: the debounce settles the run

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert _litres(c) == pytest.approx(RATE * 614 / 60, abs=0.01)  # not 619 s

    async def test_a_partial_settled_on_its_window_is_metered_to_its_off_report(
        self, hass
    ):
        """Off at +598 on a 612 s plan: a partial on its window, settled at +603.

        async_stop_self_closing books the partial and finalises the meter
        itself; the tick at +600 used to credit (585, 600] at nothing.
        """
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(612))
            await _walk(hass, frozen, 598)
            await _flow(hass, 0)
            await _report(hass, "off", started + timedelta(seconds=598))
            await _advance(hass, frozen, 2)  # 600: the tick reads nothing
            await _advance(hass, frozen, 3)  # 603: the debounce settles the run

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["actual_s"] == pytest.approx(598, abs=0.01)
        assert _litres(c) == pytest.approx(RATE * 598 / 60, abs=0.01)  # not 585 s

    async def test_a_stop_in_the_grace_is_metered_to_the_off_report(self, hass):
        """(d): off at +614, stopped at +616, completed on the reported window."""
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(612))
            await _walk(hass, frozen, 614)
            await _flow(hass, 0)
            await _report(hass, "off", started + timedelta(seconds=614))
            await _advance(hass, frozen, 1)  # 615: the tick reads nothing
            frozen.tick(timedelta(seconds=1))  # 616: the debounce (619) not fired

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == pytest.approx(614, abs=0.01)
            assert _litres(c) == pytest.approx(RATE * 614 / 60, abs=0.01)

            # _coord's _os_cancel_watch is a double, so the debounce is still
            # armed; run it out against the removed run, which it leaves alone.
            await _advance(hass, frozen, 4)  # 620

        c._record_run.assert_awaited_once()

    async def test_a_stop_before_the_plan_is_metered_to_a_stored_off_report(self, hass):
        """(c): off stored at +298, stopped at +301 while its debounce is pending.

        The stop keeps its own clock, 301 s, as (c) has it. The litres are a
        measurement, and the record holds the off only while it is the valve's
        latest report, so the flow ends there: 298 s, not the 285 s the tick at
        +300 left.
        """
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(612))
            await _walk(hass, frozen, 298)
            await _flow(hass, 0)
            await _report(hass, "off", started + timedelta(seconds=298))
            await _advance(hass, frozen, 2)  # 300: the tick reads nothing
            frozen.tick(timedelta(seconds=1))  # 301: the debounce (303) not fired

            assert await c.async_stop_self_closing(2)
            await hass.async_block_till_done()

            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_PARTIAL
            assert kw["actual_s"] == pytest.approx(301, abs=0.01)
            assert _litres(c) == pytest.approx(RATE * 298 / 60, abs=0.01)

            await _advance(hass, frozen, 3)  # 304: run the debounce out

        c._record_run.assert_awaited_once()

    async def test_the_backstop_meters_to_an_off_report_it_beat_to_the_settle(
        self, hass
    ):
        """605 s plan, off at +611, backstop at +614, debounce due at +616.

        The backstop finishes the run for its plan, as agreed on #139 (see
        TestACloseReportedPastTheMarginIsKnownAndDeliberatelyUnchanged). The
        water still stopped at the report on the record, and the backstop's
        read at +614 comes after it just like the watcher's: 611 s of flow,
        not the 600 s the read at +614 left.
        """
        c = _coord(hass)
        _metered(c)
        _the_real_backstop_from_here(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(
                hass, c, _metered_zone(605, **{const.ZONE_LATENCY_MARGIN: 4})
            )
            await _walk(hass, frozen, 611)
            await _flow(hass, 0)
            await _report(hass, "off", started + timedelta(seconds=611))
            await _advance(hass, frozen, 3)  # 614: the backstop (605 + 5 + 4)

            assert await c._sc_find_run(2) is None
            kw = c._record_run.await_args.kwargs
            assert kw["result"] == const.RUN_RESULT_COMPLETED
            assert kw["actual_s"] == kw["planned_s"] == 605
            assert _litres(c) == pytest.approx(RATE * 611 / 60, abs=0.01)

            await _advance(hass, frozen, 3)  # 617: past where the debounce was due

            c._record_run.assert_awaited_once()
            assert not c._sc_cleanup_timers()
            assert 2 not in c._sc_meters()

    async def test_a_close_nobody_reported_is_metered_as_before(self, hass):
        """on -> unavailable -> off: no off report on the record, nothing is cut.

        The watcher settles it by its base rule at +619, for its plan, and the
        meter keeps every read it took: the interval spanning the close is
        still credited at the nothing read after it, 600 s of flow.
        """
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(612))
            await _walk(hass, frozen, 613)
            await _flow(hass, 0)
            await _report(hass, "unavailable", started + timedelta(seconds=613))
            await _advance(hass, frozen, 1)  # 614
            await _report(hass, "off", started + timedelta(seconds=614))
            assert not (await c._sc_find_run(2)).get(const.RUN_VALVE_OFF)
            await _advance(hass, frozen, 1)  # 615: the tick reads nothing
            await _advance(hass, frozen, 4)  # 619: the debounce decides

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 612
        assert _litres(c) == pytest.approx(RATE * 600 / 60, abs=0.01)

    async def test_a_totalizer_keeps_the_climb_it_reports_after_the_close(self, hass):
        """A counter only climbs for water that flowed, so a late read still counts.

        Lifetime counter at 1000 L on open, 2.5 L a poll; the valve reports off
        at +614 and the counter's last climb arrives at +617. The final read at
        +619 credits it, off report or not: 614 s of flow.
        """
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, 1000, **COUNTER)
            await _dispatch(hass, c, _metered_zone(612))
            for poll in range(1, 41):  # the ticks at +15 .. +600
                await _flow(hass, 1000 + 2.5 * poll, **COUNTER)
                await _advance(hass, frozen, 15)
            await _advance(hass, frozen, 14)  # 614
            await _report(hass, "off", started + timedelta(seconds=614))
            await _advance(hass, frozen, 3)  # 617: the tick at 615 read 1100 L
            await _flow(hass, 1000 + RATE * 614 / 60, **COUNTER)
            await _advance(hass, frozen, 2)  # 619: the debounce settles the run

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert (await c._sc_find_run(2)) is None
        assert _litres(c) == pytest.approx(RATE * 614 / 60, abs=0.01)


class TestTheAdvisoryIsPricedOnTheWindowItMeasured:
    """The advisory divides a run's litres by the window they were measured over.

    Its whole point is the observed rate, litres over minutes. A confirmed
    run's meter is cut at the valve's own off report (#139), so those litres
    span the REPORTED on-to-off window: priced over the plan, a valve that
    closes late reads as a zone flowing faster than it does. Short runs are
    where that bites -- 4 s late on a 60 s plan is 6.7 %, on a 612 s plan
    0.3 %, against FLOW_CAL_DEVIATION = 0.15. A run with no reported close has
    only its plan, and keeps it.
    """

    async def test_a_late_close_is_priced_on_the_reported_window(self, hass):
        """60 s plan (a minute-unit valve's smallest), closed at +64, settled at +69.

        10 L/min from the open, so the meter's litres span 64 s. Divided by the
        plan they read as 10.67 L/min: a zone whose throughput is configured
        correctly would be advised to raise it, on every run.
        """
        c = _coord(hass)
        _metered(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(60))
            await _walk(hass, frozen, 64)
            await _flow(hass, 0)
            await _report(hass, "off", started + timedelta(seconds=64))
            await _advance(hass, frozen, 1)  # 65: the tick reads nothing
            await _advance(hass, frozen, 4)  # 69: the debounce settles the run

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == pytest.approx(64, abs=0.01)
        c._flow_calibration_check.assert_awaited_once()
        _zone_arg, measured, seconds = c._flow_calibration_check.await_args.args
        assert measured == pytest.approx(RATE * 64 / 60, abs=0.01)
        assert seconds == pytest.approx(64, abs=0.01)  # not the 60 s plan
        # the rate the zone really ran at, not the 10.67 L/min the plan reads
        assert measured / (seconds / 60.0) == pytest.approx(RATE, abs=0.01)

    async def test_a_close_nobody_reported_keeps_the_plan(self, hass):
        """The same plan with no off report at all: the backstop settles it at +69.

        Without a reported window the litres are metered to the final read and
        the plan is the only window there is -- as it is for a write-only
        valve, OpenSprinkler and batch.
        """
        c = _coord(hass)
        _metered(c)
        _the_real_backstop_from_here(c)
        started = dt_util.utcnow().replace(microsecond=0)
        with freeze_time(started) as frozen:
            await _flow(hass, RATE)
            await _dispatch(hass, c, _metered_zone(60))
            await _walk(hass, frozen, 69)  # the backstop (60 + 5 + 4)

        assert await c._sc_find_run(2) is None
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 60
        c._flow_calibration_check.assert_awaited_once()
        assert c._flow_calibration_check.await_args.args[2] == 60


class TestARestartArmsTheBackstopWhereItBelongs:
    """Issue #152: the arming instant is not the instant elapsed was read at.

    ``async_resume_self_closing_runs`` reads ``elapsed`` once at the top of the
    loop body, then, for a run still inside its plan, awaits
    ``async_master_acquire``. With a master configured and the pump off, that
    await is not free: it waits the kick pause and then the master settle. The
    backstop armed afterwards from the earlier ``elapsed`` is therefore due that
    much later than the anchor it is meant to sit on, and the in-flight
    predicate -- which counts from ``RUN_STARTED`` and knows nothing of the
    sleep -- has already ended by then. That gap is the double-dispatch window.

    The acquire's sleep is modelled here by advancing the clock inside the stub;
    its real source is the kick pause plus the master settle in
    ``async_master_begin_cycle``.
    """

    async def test_the_backstop_is_due_at_start_plus_plan_plus_grace(self, hass):
        with freeze_time("2026-09-20 06:00:00") as frozen:
            c = _coord(hass)
            c.store.config.master_entity = "switch.zisterne"
            await _dispatch(hass, c, _zone())
            run = await c._sc_find_run(2)
            started = dt_util.parse_datetime(run[const.RUN_STARTED])
            grace = run_finish_grace_seconds(run)
            c._sc_schedule_cleanup.reset_mock()

            frozen.tick(100)  # HA was down for 100 s of a 600 s run
            c.async_master_acquire = AsyncMock(side_effect=lambda *_: frozen.tick(11))

            await c.async_resume_self_closing_runs()

            armed = c._sc_schedule_cleanup.call_args.args[1]
            elapsed_at_arm = (dt_util.utcnow() - started).total_seconds()
            # The run is due at start + plan + grace, whenever the timer is made.
            assert armed + elapsed_at_arm == pytest.approx(600 + grace, abs=0.5)
