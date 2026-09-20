"""The finish grace of a confirmed service run, as pure arithmetic (issue #139).

A confirmed service valve reports its own close a few seconds after its window,
and the watcher debounces that report for SERVICE_WATCH_SETTLE_SECONDS. These
helpers decide who gets the extra wait (a confirmed SERVICE run only, never a
batch or OpenSprinkler record that happens to carry the same keys), how long it
is, how short of the window still counts as completed, and how long the valve
was actually open. No coordinator and no hass: every answer is read off a zone
dict or a run record, which is what keeps the dispatch, the backstop and the
restart paths from answering differently.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from homeassistant.util import dt as dt_util

# Importing self_closing registers the service policy (and, through its own
# imports, the batch and OpenSprinkler ones) before watch_policy_for is asked.
import custom_components.irrigation_plus.self_closing  # noqa: F401
from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.batch import WATCH_POLICY as BATCH_POLICY
from custom_components.irrigation_plus.opensprinkler import (
    WATCH_POLICY as OPENSPRINKLER_POLICY,
)
from custom_components.irrigation_plus.run_watch import (
    RunWatchMixin,
    run_completion_tolerance,
    run_finish_grace_seconds,
    run_has_finish_grace,
    run_latency_margin,
    valve_window_seconds,
    watch_policy_for,
    zone_latency_margin,
)
from custom_components.irrigation_plus.self_closing import (
    SERVICE_WATCH_POLICY,
    SelfClosingMixin,
)

VALVE = "binary_sensor.valve_flowing"
T0 = datetime(2026, 1, 10, 10, 0, 0, tzinfo=dt_util.UTC)


def _iso(offset_s: float) -> str:
    return (T0 + timedelta(seconds=offset_s)).isoformat()


def _service_zone(**kw) -> dict:
    zone = {
        const.ZONE_ID: 2,
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        const.ZONE_CONFIRM_ENTITY: VALVE,
    }
    zone.update(kw)
    return zone


def _confirmed_run(mode=const.WATERING_MODE_SERVICE, **kw) -> dict:
    run = {
        const.RUN_ZONE_ID: 2,
        const.RUN_MODE: mode,
        const.RUN_PLANNED_SECONDS: 600,
        const.RUN_STARTED: _iso(0),
        const.RUN_WATCH_ENTITY: VALVE,
        const.RUN_LATENCY_MARGIN: 4,
    }
    run.update(kw)
    return run


class TestZoneLatencyMargin:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("7", 7),
            (7.6, 8),
            (-3, 0),
            (99, 30),
            ("x", 4),
        ],
    )
    def test_the_margin_is_whole_seconds_clamped_to_its_bounds(self, raw, expected):
        zone = _service_zone(**{const.ZONE_LATENCY_MARGIN: raw})
        assert zone_latency_margin(zone) == expected

    def test_a_zone_stored_without_a_margin_gets_the_default(self):
        assert zone_latency_margin(_service_zone()) == 4
        assert zone_latency_margin(None) == const.DEFAULT_LATENCY_MARGIN_SECONDS


class TestRunLatencyMargin:
    def test_the_frozen_margin_is_read_back_as_seconds(self):
        assert run_latency_margin(_confirmed_run()) == 4.0
        assert (
            run_latency_margin(_confirmed_run(**{const.RUN_LATENCY_MARGIN: "6"})) == 6.0
        )

    def test_a_record_without_a_margin_answers_none(self):
        run = _confirmed_run()
        del run[const.RUN_LATENCY_MARGIN]
        assert run_latency_margin(run) is None
        assert run_latency_margin(None) is None

    def test_a_negative_margin_reads_as_zero_and_garbage_as_none(self):
        assert (
            run_latency_margin(_confirmed_run(**{const.RUN_LATENCY_MARGIN: -2})) == 0.0
        )
        assert (
            run_latency_margin(_confirmed_run(**{const.RUN_LATENCY_MARGIN: "x"}))
            is None
        )


class TestRunHasFinishGrace:
    def test_a_confirmed_service_run_with_a_margin_has_it(self):
        assert run_has_finish_grace(_confirmed_run()) is True

    def test_a_record_from_before_the_update_has_none(self):
        """No margin frozen at dispatch: the run keeps the formula it started with."""
        run = _confirmed_run()
        del run[const.RUN_LATENCY_MARGIN]
        assert run_has_finish_grace(run) is False

    def test_an_unconfirmed_run_has_none(self):
        run = _confirmed_run()
        del run[const.RUN_WATCH_ENTITY]
        assert run_has_finish_grace(run) is False

    def test_a_batch_record_carrying_both_keys_has_none(self):
        """RUN_WATCH_ENTITY alone is not the gate: batch records carry it too."""
        run = _confirmed_run(mode=const.WATERING_MODE_BATCH)
        assert run_has_finish_grace(run) is False

    def test_an_opensprinkler_record_carrying_both_keys_has_none(self):
        run = _confirmed_run(mode=const.WATERING_MODE_OPENSPRINKLER)
        assert run_has_finish_grace(run) is False


class TestRunFinishGraceAndTolerance:
    def test_the_grace_is_settle_plus_the_frozen_margin(self):
        assert run_finish_grace_seconds(_confirmed_run()) == 9.0

    def test_a_run_without_grace_waits_nothing_extra(self):
        run = _confirmed_run()
        del run[const.RUN_WATCH_ENTITY]
        assert run_finish_grace_seconds(run) == 0.0

    def test_the_completion_tolerance_is_the_margin(self):
        assert run_completion_tolerance(_confirmed_run()) == 4.0

    def test_the_completion_tolerance_never_drops_below_one_second(self):
        run = _confirmed_run(**{const.RUN_LATENCY_MARGIN: 0})
        assert run_completion_tolerance(run) == 1.0

    def test_a_run_without_grace_keeps_the_one_second_slack(self):
        run = _confirmed_run(mode=const.WATERING_MODE_BATCH)
        assert run_completion_tolerance(run) == 1.0


class TestValveWindowSeconds:
    def test_the_window_is_the_off_report_minus_the_on_report(self):
        run = _confirmed_run(
            **{const.RUN_VALVE_ON: _iso(0.5), const.RUN_VALVE_OFF: _iso(420.5)}
        )
        now = T0 + timedelta(seconds=2000)
        assert valve_window_seconds(run, now) == pytest.approx(420.0)

    def test_an_off_report_before_the_on_report_is_a_zero_window(self):
        run = _confirmed_run(
            **{const.RUN_VALVE_ON: _iso(10), const.RUN_VALVE_OFF: _iso(5)}
        )
        assert valve_window_seconds(run, T0 + timedelta(seconds=20)) == 0.0

    def test_without_an_off_report_the_window_is_the_time_since_on(self):
        run = _confirmed_run(**{const.RUN_VALVE_ON: _iso(0)})
        assert valve_window_seconds(run, T0 + timedelta(seconds=300)) == 300.0

    def test_without_an_off_report_the_window_is_bounded_by_the_plan(self):
        """Past the plan with no off report: waiting for the report is not watering."""
        run = _confirmed_run(**{const.RUN_VALVE_ON: _iso(0)})
        assert valve_window_seconds(run, T0 + timedelta(seconds=900)) == 600.0

    def test_the_anchor_falls_back_to_the_observed_start(self):
        run = _confirmed_run(
            **{
                const.RUN_STARTED: _iso(-50),
                const.RUN_OBSERVED_START: _iso(0),
                const.RUN_VALVE_OFF: _iso(120),
            }
        )
        assert valve_window_seconds(run, T0 + timedelta(seconds=500)) == 120.0

    def test_the_anchor_falls_back_to_the_dispatch_instant(self):
        run = _confirmed_run(
            **{const.RUN_STARTED: _iso(-50), const.RUN_VALVE_OFF: _iso(120)}
        )
        assert valve_window_seconds(run, T0 + timedelta(seconds=500)) == 170.0

    def test_a_record_with_no_anchor_answers_the_plan(self):
        run = _confirmed_run(**{const.RUN_VALVE_OFF: _iso(120)})
        del run[const.RUN_STARTED]
        assert valve_window_seconds(run, T0 + timedelta(seconds=500)) == 600.0


class TestOnlyTheServicePolicySettlesOnTheValveWindow:
    def test_the_service_policy_settles_on_the_valve_window(self):
        assert SERVICE_WATCH_POLICY.settles_on_valve_window is True
        assert (
            watch_policy_for(const.WATERING_MODE_SERVICE).settles_on_valve_window
            is True
        )

    def test_the_batch_policy_does_not(self):
        assert BATCH_POLICY.settles_on_valve_window is False
        assert (
            watch_policy_for(const.WATERING_MODE_BATCH).settles_on_valve_window is False
        )

    def test_the_opensprinkler_policy_does_not(self):
        assert OPENSPRINKLER_POLICY.settles_on_valve_window is False
        assert (
            watch_policy_for(const.WATERING_MODE_OPENSPRINKLER).settles_on_valve_window
            is False
        )


class _Host(SelfClosingMixin, RunWatchMixin):
    """Just enough coordinator to exercise _watch_resume on a run record."""

    def __init__(self, runs=None):
        self._runs = list(runs or [])
        self._sc_schedule_cleanup = Mock()

    async def _sc_active_runs(self):
        return [dict(r) for r in self._runs]

    async def _sc_persist_runs(self, runs):
        self._runs = [dict(r) for r in runs]


class TestABatchResumeArmsExactlyTheRemainder:
    async def test_resume_re_arms_the_backstop_for_the_remaining_window_only(self):
        """The pause/resume half of #139's test list, pinned where it really applies.

        _watch_resume is reached only for a segmented policy, and service is not
        segmented: a margin added there would change batch and nothing else. So
        the pin is the opposite one: a paused BATCH run whose record carries the
        same keys a confirmed service run does still re-arms its backstop for
        planned minus watered, with no settle and no margin on top.
        """
        run = _confirmed_run(
            mode=const.WATERING_MODE_BATCH,
            **{
                const.RUN_ZONE_ID: 1,
                const.RUN_OBSERVED_START: _iso(0),
                const.RUN_WATERED_SECONDS: 60.0,
                const.RUN_SEGMENT_STARTED: None,
            },
        )
        host = _Host([run])

        await host._watch_resume(1, dict(run))

        assert host._sc_schedule_cleanup.call_count == 1
        assert host._sc_schedule_cleanup.call_args.args == (1, 540.0)
        assert host._runs[0][const.RUN_SEGMENT_STARTED] is not None
