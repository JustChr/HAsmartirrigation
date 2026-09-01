"""The two-stage arm, the paired Start bound, and the fitted selection.

Covers the scheduling half of a bounded run window: deciding late enough that
the demand is current, refusing to start before the Start bound, and handing
the runner the zones that fit before the Finish bound. Fitting is derived from
both ends being bounded rather than configured, so reaching ``_decide_and_arm``
at all implies it and no test opts into it separately.
"""

import datetime
import logging
import math
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import homeassistant.util.dt as dt_util
import pytest
from freezegun import freeze_time
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
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


def _run(zone_id, duration, ratio=2.0, maximum=None, track=TRACK_CLASSIC, confirm=0.0):
    return ZoneRun(
        zone_id=zone_id,
        duration=duration,
        depletion_ratio=ratio,
        maximum_duration=maximum,
        track=track,
        confirm_seconds=confirm,
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
        # Wired to a Start bound whenever it is paired against a Finish,
        # but exercised directly here too so the seam is proven
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

    Only reached when both ends are bounded, so — unlike before the reshape —
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
    async def test_the_start_reserves_the_valve_confirm_too(self):
        """The chain polls each valve for its on-state before that zone's water
        starts. Priced on water alone the run has no room for those polls, and
        since the finish reaches the runner as a hard deadline they come out of
        the tail."""
        mgr = _manager(plan=[_run(0, 1800, confirm=30), _run(1, 1800, confirm=30)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(_schedule(), target, None, commit=True)
        # 3600 s of water plus a 30 s poll per zone: the start moves back by the
        # 60 s the run really spends on them, and the finish still holds.
        assert track.call_args[0][2] == datetime.datetime(
            2026, 6, 21, 4, 59, tzinfo=UTC
        )

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_a_dispatch_that_never_polls_costs_nothing_extra(self):
        """A station is opened by the controller and a self-closing valve with
        no confirm entity is credited optimistically. Neither polls, so neither
        moves the start."""
        mgr = _manager(plan=[_run(0, 1800), _run(1, 1800)])
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
        # Nothing was fitted (no due zone), so the run carries no order.
        assert kwargs["order"] is None
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


class TestAnInvertedPairingIsAnnouncedOncePerPairing:
    """The re-arm fan-out repeats every warning it passes through.

    ``_config_updated`` fires on every config and zone write and re-arms every
    schedule, so a warning raised unconditionally inside the resolution path
    reports one misconfigured schedule several times per save. Observed at eight
    identical lines from a single save on a live instance.
    """

    @staticmethod
    def _inverted():
        # A Start bound resolving to the same clock time as the Finish it is
        # supposed to precede leaves no window at all.
        return _schedule(
            **{
                const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
                const.SCHEDULE_CONF_START_TIME: "06:00",
                const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_TIME,
                const.SCHEDULE_CONF_FINISH_TIME: "06:00",
            }
        )

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_repeating_the_same_pairing_drops_to_debug(self, caplog):
        mgr = _manager()
        sched = self._inverted()
        target = _local(2026, 6, 21, 6, 0)
        caplog.set_level(logging.DEBUG)

        for _ in range(3):
            assert (
                await mgr._paired_bound_time(sched, const.SCHEDULE_ANCHOR_START, target)
                is None
            )

        levels = [
            r.levelno for r in caplog.records if "does not precede/follow" in r.message
        ]
        assert levels == [logging.WARNING, logging.DEBUG, logging.DEBUG]

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_a_different_pairing_is_announced_again(self, caplog):
        mgr = _manager()
        sched = self._inverted()
        caplog.set_level(logging.DEBUG)

        await mgr._paired_bound_time(
            sched, const.SCHEDULE_ANCHOR_START, _local(2026, 6, 21, 6, 0)
        )
        await mgr._paired_bound_time(
            sched, const.SCHEDULE_ANCHOR_START, _local(2026, 6, 22, 6, 0)
        )

        levels = [
            r.levelno for r in caplog.records if "does not precede/follow" in r.message
        ]
        assert levels == [logging.WARNING, logging.WARNING]

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_the_selection_log_and_the_pairing_log_do_not_evict_each_other(
        self, caplog
    ):
        # One slot per schedule would have each announcement reset the other's
        # memo, and both would go on repeating.
        mgr = _manager(plan=[_run(0, 7200, ratio=3.0), _run(1, 7200, ratio=1.1)])
        sched = self._inverted()
        target = _local(2026, 6, 21, 6, 0)
        caplog.set_level(logging.DEBUG)

        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ):
            for _ in range(3):
                await mgr._paired_bound_time(sched, const.SCHEDULE_ANCHOR_START, target)
                await mgr._decide_and_arm(sched, target, None, commit=False)

        pairing = [
            r.levelno for r in caplog.records if "does not precede/follow" in r.message
        ]
        armed = [r.levelno for r in caplog.records if "demand" in r.message]
        assert pairing == [logging.WARNING, logging.DEBUG, logging.DEBUG]
        assert armed == [logging.INFO, logging.DEBUG, logging.DEBUG]


class TestAnUnboundedZoneHasNoDecisionPoint:
    """``bound_wall_clock`` answers ``math.inf`` for a zone the configuration
    never caps, and the arm has to notice rather than subtract it.

    Nothing in the runner caps a timed zone, and ``maximum_bucket`` clamps the
    bucket's surplus side rather than the deficit that sizes a run, so such a
    zone can drift arbitrarily dry and its run length has no ceiling derived
    from configuration. One of them makes the whole schedule's bound infinite.
    """

    @pytest.mark.asyncio
    async def test_the_bound_is_infinite_when_one_zone_has_no_maximum(self):
        mgr = _manager(plan=[_run(0, 60, maximum=4800), _run(1, 60, maximum=None)])
        assert await mgr._duration_bound(_schedule()) == math.inf

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_an_infinite_bound_falls_back_to_the_single_stage_arm(self):
        # No paired Start bound resolves here, so the decision point would have
        # to come from the duration bound - and there is not one. Arming on the
        # running estimate is weaker than a decision point but is an answer,
        # where substituting a number for the infinity would be a confident
        # wrong one.
        mgr = _manager(plan=[_run(0, 60, maximum=None)])
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(return_value=3600)
        mgr._paired_bound_time = AsyncMock(return_value=None)
        target = _local(2026, 6, 21, 6, 0)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            tracker = await mgr._setup_fitted_tracker(_schedule(), target)
        assert tracker is not None
        # target - estimate, which is the single-stage arm: not a decision
        # point, and not an OverflowError.
        assert track.call_args[0][2] == target - datetime.timedelta(seconds=3600)

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_an_infinite_bound_leaves_the_run_flagged_estimated(self):
        # The single-stage arm re-reads its estimate on every re-arm, so the
        # reported start keeps moving right up to the run. There is no moment
        # after which it is a fact, and the panel has to say so.
        mgr = _manager(plan=[_run(0, 3600, maximum=None)])
        mgr._schedules = [
            _schedule(start_mode=const.SCHEDULE_BOUND_MODE_TIME, start_time="22:00")
        ]
        mgr._next_governing_time = AsyncMock(return_value=_local(2026, 6, 21, 6, 0))
        mgr._paired_bound_time = AsyncMock(return_value=None)
        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["estimated"] is True


class TestThePlanIsAskedForWhatTheBoundNeeds:
    """``async_plan_zone_runs`` grew ``runnable_only`` and ``ignore_demand``
    for this unit's two callers, so the flags are driven against the real
    method here rather than against a double of it.

    The two callers want different sets. Fitting may only drop zones this
    integration is actually going to run, so it sets ``runnable_only``. The
    duration bound additionally has to cover every zone the schedule could
    water by the time the decision point arrives, so it sets ``ignore_demand``
    as well: pricing only the currently-due zones would move the decision point
    every time a zone crossed its threshold.
    """

    @staticmethod
    def _zone(zone_id, **over):
        z = {
            const.ZONE_ID: zone_id,
            const.ZONE_NAME: "Zone " + str(zone_id),
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_DURATION: 600,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_BUCKET_THRESHOLD: -1.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_LEAD_TIME: 0,
            const.ZONE_MAXIMUM_DURATION: 600,
            const.ZONE_MAXIMUM_BUCKET: 24,
            const.ZONE_LINKED_ENTITY: "switch.zone",
        }
        z.update(over)
        return z

    @classmethod
    def _coordinator(cls, zones):
        coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
        hass = Mock()
        hass.config = Mock()
        hass.config.units = METRIC_SYSTEM
        coord.hass = hass
        coord.store = Mock()
        coord.store.config = SimpleNamespace(live_estimate_enabled=False)
        coord.store.async_get_zones = AsyncMock(return_value=[dict(z) for z in zones])
        coord.store.async_get_distributors = AsyncMock(return_value=[])
        coord._sc_is_self_closing = Mock(return_value=False)
        return coord

    @pytest.mark.asyncio
    async def test_runnable_only_drops_a_zone_the_runner_could_not_actuate(self):
        coord = self._coordinator(
            [self._zone(0), self._zone(1, **{const.ZONE_LINKED_ENTITY: None})]
        )
        both = await coord.async_plan_zone_runs()
        runnable = await coord.async_plan_zone_runs(runnable_only=True)
        assert sorted(p.zone_id for p in both) == [0, 1]
        assert [p.zone_id for p in runnable] == [0]

    @pytest.mark.asyncio
    async def test_ignore_demand_keeps_a_satisfied_zone_at_zero_duration(self):
        # Satisfied now, so the plain plan drops it; the bound still has to
        # price its ceiling, and a zero duration keeps it out of any wall-clock
        # sum taken over the live durations.
        coord = self._coordinator(
            [self._zone(0), self._zone(1, **{const.ZONE_BUCKET: 5.0})]
        )
        due = await coord.async_plan_zone_runs(runnable_only=True)
        every = await coord.async_plan_zone_runs(runnable_only=True, ignore_demand=True)
        assert [p.zone_id for p in due] == [0]
        assert sorted(p.zone_id for p in every) == [0, 1]
        satisfied = next(p for p in every if p.zone_id == 1)
        assert satisfied.duration == 0.0
        assert satisfied.maximum_duration == 600


class TestTheSelectionReachesTheRunner:
    """The zones the decision point picked, in the order it picked them."""

    @pytest.mark.asyncio
    async def test_the_order_is_handed_to_the_runner(self):
        mgr = _manager()
        coord = mgr.coordinator
        coord._check_skip_conditions = AsyncMock(return_value=False)
        coord._irrigate_linked_entities = AsyncMock(return_value=True)
        coord._dispatch_distributor_cycles = AsyncMock(return_value=False)
        coord._reset_days_since_irrigation = AsyncMock()
        await mgr._perform_scheduled_irrigation(
            "all", "overnight", order=[2, 1], pre_committed=True
        )
        coord._irrigate_linked_entities.assert_awaited_once_with(
            "all", order=[2, 1], deadline=None
        )
        # Already committed at the decision point; committing again here would
        # re-book the same window every time anything touched the config.
        coord.async_commit_pre_run_calculation.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_the_success_line_names_the_selection_not_the_target(self, caplog):
        # "irrigated zones [0, 2, 3]" after a run that watered two of them is a
        # false claim about where the water went, and it is the only line a user
        # reading the log has to go on.
        mgr = _manager()
        coord = mgr.coordinator
        coord._check_skip_conditions = AsyncMock(return_value=False)
        coord._irrigate_linked_entities = AsyncMock(return_value=True)
        coord._dispatch_distributor_cycles = AsyncMock(return_value=False)
        coord._reset_days_since_irrigation = AsyncMock()
        caplog.set_level(logging.INFO)

        await mgr._perform_scheduled_irrigation(
            [0, 2, 3], "overnight", order=[3, 2], pre_committed=True
        )

        line = next(r for r in caplog.records if "Successfully irrigated" in r.message)
        assert "[3, 2]" in line.message

    @pytest.mark.asyncio
    async def test_an_empty_selection_is_not_reported_as_the_whole_target(self, caplog):
        # The truthiness test would fall back to the target list here, which is
        # the same false claim in its worst form: nothing was watered at all.
        mgr = _manager()
        coord = mgr.coordinator
        coord._check_skip_conditions = AsyncMock(return_value=False)
        coord._irrigate_linked_entities = AsyncMock(return_value=False)
        coord._dispatch_distributor_cycles = AsyncMock(return_value=False)
        coord._reset_days_since_irrigation = AsyncMock()
        caplog.set_level(logging.INFO)

        await mgr._perform_scheduled_irrigation(
            [0, 2, 3], "overnight", order=[], pre_committed=True
        )

        line = next(r for r in caplog.records if "Successfully irrigated" in r.message)
        assert "[]" in line.message

    @pytest.mark.asyncio
    async def test_an_unfitted_run_still_names_the_target(self, caplog):
        mgr = _manager()
        coord = mgr.coordinator
        coord._check_skip_conditions = AsyncMock(return_value=False)
        coord._irrigate_linked_entities = AsyncMock(return_value=True)
        coord._dispatch_distributor_cycles = AsyncMock(return_value=False)
        coord._reset_days_since_irrigation = AsyncMock()
        caplog.set_level(logging.INFO)

        await mgr._perform_scheduled_irrigation("all", "overnight")

        line = next(r for r in caplog.records if "Successfully irrigated" in r.message)
        assert "all" in line.message

    @pytest.mark.asyncio
    async def test_an_order_restricts_the_run_and_sequences_it(self):
        # The order supersedes the schedule's zone target rather than
        # intersecting with it: the selection was computed from that same
        # target to begin with.
        coord = TestThePlanIsAskedForWhatTheBoundNeeds._coordinator(
            [TestThePlanIsAskedForWhatTheBoundNeeds._zone(i) for i in (0, 1, 2)]
        )
        seen = {}

        async def dispatch(zones, *, trigger, **kw):
            seen["ids"] = [int(z[const.ZONE_ID]) for z in zones]
            return True

        coord._dispatch_by_mode = dispatch
        coord._rain_delay_active = Mock(return_value=False)
        assert await coord._irrigate_linked_entities("all", order=[2, 0]) is True
        assert seen["ids"] == [2, 0]
