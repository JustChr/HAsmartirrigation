"""Run time as the sum of watering segments (issue #88, stage 2).

A controller that can PAUSE turns the valve off and keeps the remaining time, so
a run's length stops being "now minus the observed start". These pin the segment
arithmetic itself and — just as importantly — that a run which carries no segment
fields is timed exactly as it always was, which is what keeps the OpenSprinkler
mode on its original behaviour.
"""

import datetime

from homeassistant.util import dt as dt_util

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.run_watch import RunWatchMixin, watch_policy_for
from custom_components.smart_irrigation.self_closing import SelfClosingMixin


class _Host(SelfClosingMixin, RunWatchMixin):
    """Just enough coordinator to exercise the run-record arithmetic."""

    def __init__(self, runs=None):
        self._runs = list(runs or [])

    async def _sc_active_runs(self):
        return [dict(r) for r in self._runs]

    async def _sc_persist_runs(self, runs):
        self._runs = [dict(r) for r in runs]


def _ago(seconds):
    return (dt_util.utcnow() - datetime.timedelta(seconds=seconds)).isoformat()


class TestARunWithoutSegmentsIsTimedExactlyAsBefore:
    """The regression guard for every mode that cannot pause."""

    def test_an_observed_run_still_measures_from_its_observed_start(self):
        host = _Host()
        run = {const.RUN_OBSERVED_START: _ago(120)}
        assert 119 <= host._sc_run_elapsed(run) <= 122

    def test_a_queued_opensprinkler_run_still_reports_zero(self):
        host = _Host()
        run = {
            const.RUN_STARTED: _ago(3600),
            const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER,
        }
        assert host._sc_run_elapsed(run) == 0.0

    def test_a_service_run_still_measures_from_dispatch(self):
        host = _Host()
        run = {
            const.RUN_STARTED: _ago(60),
            const.RUN_MODE: const.WATERING_MODE_SERVICE,
        }
        assert 59 <= host._sc_run_elapsed(run) <= 62


class TestASegmentedRunSumsItsWateringSegments:
    def test_an_open_segment_is_added_to_the_banked_total(self):
        host = _Host()
        run = {
            const.RUN_WATERED_SECONDS: 300.0,
            const.RUN_SEGMENT_STARTED: _ago(60),
        }
        assert 359 <= host._sc_run_elapsed(run) <= 362

    def test_a_paused_run_reports_only_what_it_delivered(self):
        """The whole point: a pause must not be charged as water.

        The observed start is deliberately far in the past — under the old
        contiguous rule this run would read as an hour of watering.
        """
        host = _Host()
        run = {
            const.RUN_OBSERVED_START: _ago(3600),
            const.RUN_WATERED_SECONDS: 300.0,
            const.RUN_SEGMENT_STARTED: None,
        }
        assert host._sc_run_elapsed(run) == 300.0

    def test_a_freshly_opened_segment_with_nothing_banked_reads_near_zero(self):
        host = _Host()
        run = {
            const.RUN_WATERED_SECONDS: 0.0,
            const.RUN_SEGMENT_STARTED: dt_util.utcnow().isoformat(),
        }
        assert host._sc_run_elapsed(run) < 2

    def test_a_malformed_accumulator_settles_the_run_rather_than_raising(self):
        """A run that cannot compute its length would never finalise at all.

        It would hold its zone against re-dispatch and hold the pump, so this
        fails towards "delivered nothing" — which reverses the optimistic credit
        — rather than towards an exception in run teardown.
        """
        host = _Host()
        run = {const.RUN_WATERED_SECONDS: "not a number"}
        assert host._sc_run_elapsed(run) == 0.0


class TestOpeningAndClosingSegments:
    async def test_closing_banks_the_open_segment(self):
        host = _Host([{const.RUN_ZONE_ID: 1, const.RUN_SEGMENT_STARTED: _ago(90)}])
        total = await host._watch_segment_close(1)
        assert 89 <= total <= 92
        run = host._runs[0]
        assert run[const.RUN_SEGMENT_STARTED] is None
        assert 89 <= run[const.RUN_WATERED_SECONDS] <= 92

    async def test_closing_twice_does_not_bank_the_same_seconds_twice(self):
        """Home Assistant can replay a state change; a pause must be idempotent."""
        host = _Host([{const.RUN_ZONE_ID: 1, const.RUN_SEGMENT_STARTED: _ago(90)}])
        first = await host._watch_segment_close(1)
        second = await host._watch_segment_close(1)
        assert second == first

    async def test_reopening_accumulates_across_segments(self):
        host = _Host([{const.RUN_ZONE_ID: 1, const.RUN_SEGMENT_STARTED: _ago(100)}])
        await host._watch_segment_close(1)
        await host._watch_segment_open(1)
        host._runs[0][const.RUN_SEGMENT_STARTED] = _ago(50)
        assert 149 <= host._sc_run_elapsed(host._runs[0]) <= 152

    async def test_closing_a_run_that_is_gone_is_a_no_op(self):
        host = _Host([])
        assert await host._watch_segment_close(1) == 0.0

    async def test_an_update_leaves_other_zones_runs_alone(self):
        host = _Host(
            [
                {const.RUN_ZONE_ID: 1, const.RUN_PLANNED_SECONDS: 60},
                {const.RUN_ZONE_ID: 2, const.RUN_PLANNED_SECONDS: 90},
            ]
        )
        await host._watch_update_run(1, {const.RUN_WATERED_SECONDS: 5.0})
        by_zone = {r[const.RUN_ZONE_ID]: r for r in host._runs}
        assert by_zone[1][const.RUN_WATERED_SECONDS] == 5.0
        assert const.RUN_WATERED_SECONDS not in by_zone[2]
        assert by_zone[2][const.RUN_PLANNED_SECONDS] == 90


class TestTheEngineOnlySegmentsModesThatCanPause:
    def test_opensprinkler_is_not_segmented(self):
        """Its controller has no pause, and its observed start is the
        controller's own reported one — segmenting it would replace that with
        the instant the transition was seen."""
        assert watch_policy_for(const.WATERING_MODE_OPENSPRINKLER).segmented is False

    async def test_a_mode_with_nothing_to_settle_never_defers_a_finish(self):
        """Zero is the engine's default, and OpenSprinkler keeps it.

        Deferring is not a property of "cannot pause" any more: service mode
        cannot pause either and still defers, because the thing it is waiting on
        is a valve that reports its own state unreliably rather than a pause
        indicator arriving late. Both are asked through the same policy field.
        """
        host = _Host()
        delay = await host._watch_finish_delay(
            1, {const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER}
        )
        assert delay == 0.0
        assert (
            watch_policy_for(const.WATERING_MODE_OPENSPRINKLER).finish_settle_seconds
            == 0.0
        )

    async def test_service_defers_a_finish_without_being_segmented(self):
        """It waits on its valve, not on a pause — so it defers but never segments."""
        policy = watch_policy_for(const.WATERING_MODE_SERVICE)
        assert policy.segmented is False
        assert policy.finish_settle_seconds == const.SERVICE_WATCH_SETTLE_SECONDS

    async def test_a_mode_that_cannot_pause_is_never_paused(self):
        host = _Host()
        assert await host._watch_paused(1, {}) is False
