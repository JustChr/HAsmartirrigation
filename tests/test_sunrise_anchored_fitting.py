"""The two-stage arm, the paired Start bound, and deadline truncation.

Covers the scheduling half of a bounded run window: deciding late enough that
the demand is current, refusing to start before the Start bound, and cutting a
run at its Finish bound rather than watering past it. Fitting is derived from
both ends being bounded rather than configured (GitLab #27), so reaching
``_decide_and_arm`` at all implies it and no test opts into it separately.
"""

import datetime
from unittest.mock import AsyncMock, Mock, patch

import homeassistant.util.dt as dt_util
import pytest
from freezegun import freeze_time

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.run_window import (
    TRACK_CLASSIC,
    TRACK_SELF_CLOSING,
    ZoneRun,
)
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager

UTC = datetime.timezone.utc


def _local(*args):
    """A local wall-clock moment as UTC.

    The floor is a LOCAL clock time, and the test suite does not run in UTC, so
    expectations written as bare UTC would encode the offset by accident.
    """
    return dt_util.as_utc(datetime.datetime(*args, tzinfo=dt_util.DEFAULT_TIME_ZONE))


def _schedule(**kw):
    base = {
        const.SCHEDULE_CONF_ID: "s1",
        const.SCHEDULE_CONF_NAME: "overnight",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_SUNRISE,
        const.SCHEDULE_CONF_ACTION: "irrigate",
        const.SCHEDULE_CONF_ZONES: "all",
    }
    base.update(kw)
    return base


def _manager(plan=(), sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL):
    mgr = RecurringScheduleManager(Mock(), Mock())
    coord = mgr.coordinator
    coord.async_plan_zone_runs = AsyncMock(return_value=list(plan))
    coord.sequencing_timing = Mock(return_value=(sequencing, 300.0, 0.0))
    coord.async_commit_pre_run_calculation = AsyncMock()
    coord.get_total_irrigation_duration = AsyncMock(return_value=0)
    return mgr


def _run(zone_id, duration, ratio=2.0, maximum=None, track=TRACK_CLASSIC):
    return ZoneRun(
        zone_id=zone_id,
        duration=duration,
        depletion_ratio=ratio,
        maximum_duration=maximum,
        track=track,
    )


class TestBoundedEndsNeedTwoStages:
    """Neither end bounded beyond the governing one means the arm is
    untouched; both bounded always needs a decision point."""

    def test_plain_finish_schedule_keeps_the_single_stage_arm(self):
        governing, paired = RecurringScheduleManager._bounded_ends(_schedule())
        assert governing == const.SCHEDULE_ANCHOR_FINISH
        assert paired is None

    def test_a_bounded_start_alongside_the_finish_needs_a_decision_point(self):
        governing, paired = RecurringScheduleManager._bounded_ends(
            _schedule(
                start_mode=const.SCHEDULE_BOUND_MODE_TIME,
                start_time="22:00",
            )
        )
        assert governing == const.SCHEDULE_ANCHOR_FINISH
        assert paired == const.SCHEDULE_ANCHOR_START


class TestPairedBoundTime:
    """Resolving the paired Start bound against the governing Finish
    instant, not against now."""

    @pytest.mark.asyncio
    async def test_fixed_time_floor_lands_on_the_previous_evening(self):
        # An overnight window: the run finishes at 06:00 local and must not
        # start before 22:00 the PREVIOUS evening. Resolving the floor forward
        # instead would put it 16 hours past the finish and disable it — which
        # is the whole failure this control exists to prevent.
        mgr = _manager()
        target = _local(2026, 6, 21, 6, 0)
        floor = await mgr._paired_bound_time(
            _schedule(start_mode=const.SCHEDULE_BOUND_MODE_TIME, start_time="22:00"),
            const.SCHEDULE_ANCHOR_START,
            target,
        )
        assert floor == _local(2026, 6, 20, 22, 0)

    @pytest.mark.asyncio
    async def test_fixed_time_floor_the_same_day_is_kept(self):
        mgr = _manager()
        target = _local(2026, 6, 21, 23, 0)
        floor = await mgr._paired_bound_time(
            _schedule(start_mode=const.SCHEDULE_BOUND_MODE_TIME, start_time="20:00"),
            const.SCHEDULE_ANCHOR_START,
            target,
        )
        assert floor == _local(2026, 6, 21, 20, 0)

    @pytest.mark.asyncio
    async def test_no_mode_means_no_floor(self):
        mgr = _manager()
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        assert (
            await mgr._paired_bound_time(
                _schedule(), const.SCHEDULE_ANCHOR_START, target
            )
            is None
        )

    @pytest.mark.asyncio
    async def test_an_unparseable_time_disables_the_floor_rather_than_the_run(self):
        mgr = _manager()
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        assert (
            await mgr._paired_bound_time(
                _schedule(
                    start_mode=const.SCHEDULE_BOUND_MODE_TIME,
                    start_time="not a time",
                ),
                const.SCHEDULE_ANCHOR_START,
                target,
            )
            is None
        )

    @pytest.mark.asyncio
    async def test_a_floor_at_or_after_the_finish_is_ignored(self):
        # Leaves no window at all. Honour the finish time rather than never run.
        mgr = _manager()
        target = _local(2026, 6, 21, 6, 0)
        assert (
            await mgr._paired_bound_time(
                _schedule(
                    start_mode=const.SCHEDULE_BOUND_MODE_TIME, start_time="06:00"
                ),
                const.SCHEDULE_ANCHOR_START,
                target,
            )
            is None
        )

    @pytest.mark.asyncio
    async def test_sunset_floor_takes_the_sunset_before_the_target(self):
        mgr = _manager()
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        sunsets = {
            datetime.date(2026, 6, 21): datetime.datetime(
                2026, 6, 21, 21, 7, tzinfo=UTC
            ),
            datetime.date(2026, 6, 20): datetime.datetime(
                2026, 6, 20, 21, 7, tzinfo=UTC
            ),
        }
        with patch(
            "custom_components.smart_irrigation.scheduler.get_astral_event_date",
            side_effect=lambda hass, event, date: sunsets.get(date),
        ):
            floor = await mgr._paired_bound_time(
                _schedule(
                    start_mode=const.SCHEDULE_BOUND_MODE_SUNSET,
                    start_offset=120,
                ),
                const.SCHEDULE_ANCHOR_START,
                target,
            )
        # 2026-06-20 sunset 21:07 + 2 h, not the 21st's sunset which is AFTER
        # the target and would have left no window.
        assert floor == datetime.datetime(2026, 6, 20, 23, 7, tzinfo=UTC)


class TestResolveEventInstant:
    """``_resolve_event_instant`` is the shared seam every Start/Finish bound
    resolves through: same per-kind math (clock time, sunrise, sunset, solar
    azimuth), walked forward or backward. Exercised directly here rather than
    only through its callers, so a regression in the seam itself fails here
    even if a caller's own tests happen not to reach the broken branch.
    """

    @pytest.mark.asyncio
    async def test_clock_backward_wraps_to_the_previous_evening(self):
        # The defining property of the "backward" direction: the latest
        # occurrence of the clock time AT OR BEFORE the reference. A resolver
        # that searched forward instead would land 16 hours past the
        # reference, which is the exact failure the overnight floor exists to
        # prevent (see TestPairedBoundTime.test_fixed_time_floor_lands_on_the_
        # previous_evening, the same case through _paired_bound_time).
        mgr = _manager()
        reference = _local(2026, 6, 21, 6, 0)
        resolved = await mgr._resolve_event_instant(
            "clock", reference, direction="backward", hour=22, minute=0
        )
        assert resolved == _local(2026, 6, 20, 22, 0)

    @pytest.mark.asyncio
    async def test_clock_backward_same_day_is_kept(self):
        mgr = _manager()
        reference = _local(2026, 6, 21, 23, 0)
        resolved = await mgr._resolve_event_instant(
            "clock", reference, direction="backward", hour=20, minute=0
        )
        assert resolved == _local(2026, 6, 21, 20, 0)

    @pytest.mark.asyncio
    async def test_clock_forward_jumps_to_the_next_day_once_passed(self):
        mgr = _manager()
        reference = _local(2026, 6, 21, 23, 0)
        resolved = await mgr._resolve_event_instant(
            "clock", reference, direction="forward", hour=20, minute=0
        )
        assert resolved == _local(2026, 6, 22, 20, 0)

    @pytest.mark.asyncio
    async def test_clock_forward_same_day_when_still_ahead(self):
        mgr = _manager()
        reference = _local(2026, 6, 21, 6, 0)
        resolved = await mgr._resolve_event_instant(
            "clock", reference, direction="forward", hour=22, minute=0
        )
        assert resolved == _local(2026, 6, 21, 22, 0)

    @pytest.mark.asyncio
    async def test_sunset_backward_takes_the_sunset_before_the_reference(self):
        mgr = _manager()
        reference = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        sunsets = {
            datetime.date(2026, 6, 21): datetime.datetime(
                2026, 6, 21, 21, 7, tzinfo=UTC
            ),
            datetime.date(2026, 6, 20): datetime.datetime(
                2026, 6, 20, 21, 7, tzinfo=UTC
            ),
        }
        with patch(
            "custom_components.smart_irrigation.scheduler.get_astral_event_date",
            side_effect=lambda hass, event, date: sunsets.get(date),
        ):
            resolved = await mgr._resolve_event_instant(
                "sunset",
                reference,
                direction="backward",
                offset=datetime.timedelta(minutes=120),
            )
        # 2026-06-20 sunset 21:07 + 2h, not the 21st's (after the reference).
        assert resolved == datetime.datetime(2026, 6, 20, 23, 7, tzinfo=UTC)

    @pytest.mark.asyncio
    async def test_sunset_backward_exhausted_returns_none(self):
        mgr = _manager()
        reference = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler.get_astral_event_date",
            return_value=None,
        ):
            assert (
                await mgr._resolve_event_instant(
                    "sunset", reference, direction="backward"
                )
                is None
            )

    @pytest.mark.asyncio
    async def test_solar_azimuth_backward_is_reachable(self):
        # Wired to a Start bound whenever it is paired against a Finish
        # (GitLab #27), but exercised directly here too so the seam is proven
        # to work in both directions. A clear day near the summer solstice
        # guarantees the sun crosses 90 degrees (due east) sometime that
        # morning, so a backward search from local noon must find it rather
        # than return None.
        mgr = _manager()
        mgr.hass.config.as_dict = Mock(
            return_value={"latitude": 45.0, "longitude": 0.0}
        )
        reference = datetime.datetime(2026, 6, 21, 12, 0, tzinfo=UTC)
        resolved = await mgr._resolve_event_instant(
            "solar_azimuth", reference, direction="backward", angle=90
        )
        assert resolved is not None
        assert resolved <= reference

    @pytest.mark.asyncio
    async def test_unknown_kind_returns_none(self):
        mgr = _manager()
        reference = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        assert (
            await mgr._resolve_event_instant(
                "not-a-kind", reference, direction="forward"
            )
            is None
        )


class TestDurationBound:
    """The decision point's duration-independent fixed point."""

    @pytest.mark.asyncio
    async def test_prices_configured_maximums_not_current_demand(self):
        mgr = _manager(
            plan=[_run(0, 60, maximum=4800), _run(1, 60, maximum=3000)],
        )
        assert await mgr._duration_bound(_schedule()) == 7800

    @pytest.mark.asyncio
    async def test_prices_every_eligible_zone_not_only_the_due_ones(self):
        # The bound must cover every zone the schedule could water by the time
        # the decision point arrives, not the ones that happen to be due while
        # it is being armed. Pricing only the due ones would move the decision
        # point each time a zone crossed its threshold, which is exactly the
        # demand-dependence the bound exists to remove.
        mgr = _manager()
        coord = mgr.coordinator
        seen = {}

        async def plan(zones, *, runnable_only=False, ignore_demand=False):
            seen["ignore_demand"] = ignore_demand
            return [_run(0, 0, maximum=4800), _run(1, 0, maximum=3000)]

        coord.async_plan_zone_runs = AsyncMock(side_effect=plan)
        assert await mgr._duration_bound(_schedule()) == 7800
        assert seen["ignore_demand"] is True


class TestDecideAndArm:
    """The second stage: read demand, select, arm the real start.

    Only reached when both ends are bounded, so — unlike before GitLab #27 —
    a schedule need not opt into anything extra to exercise this: reaching
    ``_decide_and_arm`` at all already implies fitting.
    """

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_start_is_the_target_minus_demand_when_everything_fits(self):
        mgr = _manager(plan=[_run(0, 1800), _run(1, 1800)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, None, commit=True)
        # 3600 s of demand, so the slack sits before the start and the run
        # still ends exactly on the target.
        assert track.call_args[0][2] == datetime.datetime(2026, 6, 21, 5, 0, tzinfo=UTC)

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_demand_is_the_longest_track_not_the_sum_of_all_of_them(self):
        # The service zone's valve closes itself, so it opens alongside the
        # classic zone rather than after it: 3600 s of wall clock, not 5400.
        # Sizing the fire time on the sum starts the run 30 minutes early and
        # arms on a length neither the estimate nor the dial reports.
        mgr = _manager(
            plan=[_run(0, 3600), _run(1, 1800, track=TRACK_SELF_CLOSING)],
        )
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, None, commit=True)
        assert track.call_args[0][2] == datetime.datetime(2026, 6, 21, 5, 0, tzinfo=UTC)

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_the_floor_pins_the_start_when_demand_outruns_the_window(self):
        # 5 h of demand against a 4 h window: the start is pinned at the floor
        # and both ends of the window are fixed. The run cannot begin earlier
        # than the floor no matter how much water is owed.
        mgr = _manager(plan=[_run(0, 18000)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        floor = datetime.datetime(2026, 6, 21, 2, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, floor, commit=True)
        assert track.call_args[0][2] == floor

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_a_commit_is_requested_only_when_asked_for(self):
        mgr = _manager(plan=[_run(0, 600)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ):
            await mgr._decide_and_arm(_schedule(), target, None, commit=False)
        # Restarting inside the window must NOT re-commit: the ledger for this
        # run was already committed at the decision point.
        mgr.coordinator.async_commit_pre_run_calculation.assert_not_awaited()

        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ):
            await mgr._decide_and_arm(_schedule(), target, None, commit=True)
        mgr.coordinator.async_commit_pre_run_calculation.assert_awaited_once()

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_fitting_drops_what_will_not_fit_and_orders_the_rest(self):
        # A 4 h window against 5 h of demand across three zones. Zone 2 is the
        # driest and leads; zone 0 is the least depleted and is dropped.
        mgr = _manager(
            plan=[
                _run(0, 7200, ratio=1.1),
                _run(1, 7200, ratio=1.5),
                _run(2, 7200, ratio=3.0),
            ]
        )
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        floor = datetime.datetime(2026, 6, 21, 2, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, floor, commit=True)
        callback = track.call_args[0][1]
        mgr._execute_schedule = Mock()
        callback(datetime.datetime(2026, 6, 21, 2, 0, tzinfo=UTC))
        kwargs = mgr._execute_schedule.call_args.kwargs
        assert kwargs["order"] == [2, 1]
        assert kwargs["deadline"] == target
        assert kwargs["pre_committed"] is True

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_no_due_zone_arms_a_pass_through_not_nothing(self):
        # A finish schedule only re-arms from its own fire callback, so arming
        # nothing at all would leave it dormant until the next restart.
        mgr = _manager(plan=[])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            tracker = await mgr._decide_and_arm(_schedule(), target, None, commit=True)
        assert tracker is not None
        assert track.call_args[0][2] == target
        # And firing it records the occurrence so the re-arm advances past it.
        mgr.hass.loop.call_soon_threadsafe = Mock()
        mgr._execute_schedule = Mock()
        track.call_args[0][1](target)
        assert mgr._finish_last_target["s1"] == target.isoformat()

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_a_pass_through_still_runs_the_schedule_action(self):
        # An empty plan is not the same claim as "there is no water to
        # deliver": async_plan_zone_runs excludes distributor members by
        # construction, because a member waters through its distributor's
        # shared inlet rather than its own valve. A schedule whose targets are
        # all members therefore plans nothing while still having a cycle to
        # run, and _execute_schedule is that cycle's sole automatic driver. A
        # pass-through that only lapsed left those members dry.
        mgr = _manager(plan=[])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, None, commit=True)
        mgr.hass.loop.call_soon_threadsafe = Mock()
        mgr._execute_schedule = Mock()
        track.call_args[0][1](target)
        mgr._execute_schedule.assert_called_once()
        kwargs = mgr._execute_schedule.call_args.kwargs
        # Nothing was fitted (no due zone), so the run carries neither an
        # order nor a deadline.
        assert kwargs["order"] is None
        assert kwargs["deadline"] is None
        assert kwargs["pre_committed"] is True

    @pytest.mark.asyncio
    @freeze_time("2026-06-21 05:30:00")
    async def test_a_start_already_in_the_past_fires_almost_immediately(self):
        mgr = _manager(plan=[_run(0, 18000)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, None, commit=False)
        fire = track.call_args[0][2]
        assert fire == datetime.datetime(2026, 6, 21, 5, 30, 2, tzinfo=UTC)

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_the_occurrence_is_recorded_at_the_run_not_at_the_decision(self):
        # Recording it at the decision point would make any config change
        # inside the window re-arm onto the NEXT occurrence and skip tonight.
        mgr = _manager(plan=[_run(0, 600)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, None, commit=True)
        assert "s1" not in mgr._finish_last_target
        mgr._execute_schedule = Mock()
        mgr.hass.loop.call_soon_threadsafe = Mock()
        track.call_args[0][1](target)
        assert mgr._finish_last_target["s1"] == target.isoformat()


class TestScheduleValidation:
    """Bad Start/Finish settings are rejected, not silently dropped."""

    def test_an_unknown_start_mode_is_rejected(self):
        mgr = _manager()
        with pytest.raises(ValueError, match="start mode"):
            mgr._validate_schedule_data(_schedule(start_mode="whenever"))

    def test_a_malformed_start_time_is_rejected(self):
        mgr = _manager()
        with pytest.raises(ValueError, match="start time"):
            mgr._validate_schedule_data(
                _schedule(
                    start_mode=const.SCHEDULE_BOUND_MODE_TIME,
                    start_time="25:99",
                )
            )

    def test_a_valid_floor_passes(self):
        mgr = _manager()
        mgr._validate_schedule_data(
            _schedule(
                start_mode=const.SCHEDULE_BOUND_MODE_SUNSET,
                start_offset=120,
            )
        )

    def test_both_ends_unbounded_is_rejected(self):
        mgr = _manager()
        with pytest.raises(ValueError, match="Start or a Finish"):
            mgr._validate_schedule_data(
                _schedule(finish_mode=const.SCHEDULE_BOUND_MODE_NONE)
            )


class TestUpcomingRunsEstimatedFlag:
    """The dashboard has to be able to say "this start will still move"."""

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 12:00:00")
    async def test_estimated_before_the_decision_point(self):
        mgr = _manager(plan=[_run(0, 3600, maximum=4800)])
        mgr._schedules = [
            _schedule(start_mode=const.SCHEDULE_BOUND_MODE_TIME, start_time="22:00")
        ]
        mgr._next_governing_time = AsyncMock(return_value=_local(2026, 6, 21, 6, 0))
        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["estimated"] is True
        assert runs[0]["start_bound_utc"] == _local(2026, 6, 20, 22, 0).isoformat()

    @pytest.mark.asyncio
    @freeze_time("2026-06-21 08:00:00")
    async def test_not_estimated_once_the_decision_point_has_passed(self):
        # Past the decision point the start is armed and no longer drifts, so
        # the number is a fact rather than a projection.
        mgr = _manager(plan=[_run(0, 3600, maximum=4800)])
        mgr._schedules = [
            _schedule(start_mode=const.SCHEDULE_BOUND_MODE_TIME, start_time="22:00")
        ]
        mgr._next_governing_time = AsyncMock(return_value=_local(2026, 6, 21, 6, 0))
        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["estimated"] is False

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 12:00:00")
    async def test_a_plain_finish_schedule_is_never_flagged_estimated(self):
        mgr = _manager()
        mgr._schedules = [_schedule()]
        mgr._next_governing_time = AsyncMock(return_value=_local(2026, 6, 21, 6, 0))
        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["estimated"] is False
