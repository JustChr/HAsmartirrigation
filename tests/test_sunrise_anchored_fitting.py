"""The two-stage arm, the earliest-start floor, and deadline truncation.

Covers the scheduling half of sunrise-anchored irrigation: deciding late enough
that the demand is current, refusing to start before a floor, and cutting a run
at its finish target rather than watering past it.
"""

import datetime
from unittest.mock import AsyncMock, Mock, patch

import homeassistant.util.dt as dt_util
import pytest
from freezegun import freeze_time

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.run_window import ZoneRun
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager

UTC = datetime.timezone.utc


def _local(*args):
    """A local wall-clock moment as UTC.

    The floor is a LOCAL clock time, and the test suite does not run in UTC, so
    expectations written as bare UTC would encode the offset by accident.
    """
    return dt_util.as_utc(
        datetime.datetime(*args, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    )


def _schedule(**kw):
    base = {
        const.SCHEDULE_CONF_ID: "s1",
        const.SCHEDULE_CONF_NAME: "overnight",
        const.SCHEDULE_CONF_TYPE: const.SCHEDULE_TYPE_SUNRISE,
        const.SCHEDULE_CONF_ACTION: "irrigate",
        const.SCHEDULE_CONF_TIME_ANCHOR: const.SCHEDULE_TIME_ANCHOR_FINISH,
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


def _run(zone_id, duration, ratio=2.0, maximum=None):
    return ZoneRun(
        zone_id=zone_id,
        duration=duration,
        depletion_ratio=ratio,
        maximum_duration=maximum,
    )


class TestUsesTwoStageArm:
    """Neither control set means the arm is untouched."""

    def test_plain_finish_schedule_keeps_the_single_stage_arm(self):
        mgr = _manager()
        assert mgr._uses_two_stage_arm(_schedule()) is False

    def test_fitting_needs_a_decision_point(self):
        mgr = _manager()
        assert mgr._uses_two_stage_arm(_schedule(fit_to_window=True)) is True

    def test_an_earliest_start_alone_needs_a_decision_point(self):
        mgr = _manager()
        assert (
            mgr._uses_two_stage_arm(
                _schedule(
                    earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                    earliest_start_time="22:00",
                )
            )
            is True
        )

    def test_an_unrecognised_mode_falls_back_to_no_floor(self):
        mgr = _manager()
        assert mgr._uses_two_stage_arm(_schedule(earliest_start_mode="whenever")) is False


class TestEarliestStart:
    """Resolving the floor against the occurrence, not against now."""

    @pytest.mark.asyncio
    async def test_fixed_time_floor_lands_on_the_previous_evening(self):
        # An overnight window: the run finishes at 06:00 local and must not
        # start before 22:00 the PREVIOUS evening. Resolving the floor forward
        # instead would put it 16 hours past the finish and disable it — which
        # is the whole failure this control exists to prevent.
        mgr = _manager()
        target = _local(2026, 6, 21, 6, 0)
        floor = await mgr._earliest_start(
            _schedule(
                earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                earliest_start_time="22:00",
            ),
            target,
        )
        assert floor == _local(2026, 6, 20, 22, 0)

    @pytest.mark.asyncio
    async def test_fixed_time_floor_the_same_day_is_kept(self):
        mgr = _manager()
        target = _local(2026, 6, 21, 23, 0)
        floor = await mgr._earliest_start(
            _schedule(
                earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                earliest_start_time="20:00",
            ),
            target,
        )
        assert floor == _local(2026, 6, 21, 20, 0)

    @pytest.mark.asyncio
    async def test_no_mode_means_no_floor(self):
        mgr = _manager()
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        assert await mgr._earliest_start(_schedule(), target) is None

    @pytest.mark.asyncio
    async def test_an_unparseable_time_disables_the_floor_rather_than_the_run(self):
        mgr = _manager()
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        assert (
            await mgr._earliest_start(
                _schedule(
                    earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                    earliest_start_time="not a time",
                ),
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
            await mgr._earliest_start(
                _schedule(
                    earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                    earliest_start_time="06:00",
                ),
                target,
            )
            is None
        )

    @pytest.mark.asyncio
    async def test_sunset_floor_takes_the_sunset_before_the_target(self):
        mgr = _manager()
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        sunsets = {
            datetime.date(2026, 6, 21): datetime.datetime(2026, 6, 21, 21, 7, tzinfo=UTC),
            datetime.date(2026, 6, 20): datetime.datetime(2026, 6, 20, 21, 7, tzinfo=UTC),
        }
        with patch(
            "custom_components.smart_irrigation.scheduler.get_astral_event_date",
            side_effect=lambda hass, event, date: sunsets.get(date),
        ):
            floor = await mgr._earliest_start(
                _schedule(
                    earliest_start_mode=const.SCHEDULE_EARLIEST_START_SUNSET,
                    earliest_start_offset_minutes=120,
                ),
                target,
            )
        # 2026-06-20 sunset 21:07 + 2 h, not the 21st's sunset which is AFTER
        # the target and would have left no window.
        assert floor == datetime.datetime(2026, 6, 20, 23, 7, tzinfo=UTC)


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
    """The second stage: read demand, select, arm the real start."""

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_start_is_the_target_minus_demand_when_everything_fits(self):
        mgr = _manager(plan=[_run(0, 1800), _run(1, 1800)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, None, commit=True
            )
        # 3600 s of demand, so the slack sits before the start and the run
        # still ends exactly on the target.
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
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, floor, commit=True
            )
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
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, None, commit=False
            )
        # Restarting inside the window must NOT re-commit: the ledger for this
        # run was already committed at the decision point.
        mgr.coordinator.async_commit_pre_run_calculation.assert_not_awaited()

        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ):
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, None, commit=True
            )
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
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, floor, commit=True
            )
        callback = track.call_args[0][1]
        mgr._execute_schedule = Mock()
        callback(datetime.datetime(2026, 6, 21, 2, 0, tzinfo=UTC))
        kwargs = mgr._execute_schedule.call_args.kwargs
        assert kwargs["order"] == [2, 1]
        assert kwargs["deadline"] == target
        assert kwargs["pre_committed"] is True

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_a_floor_without_fitting_passes_no_order_or_deadline(self):
        # Ordering, selection and the deadline are ONE opt-in. A floor alone
        # bounds the start and changes nothing else about the run.
        mgr = _manager(plan=[_run(0, 600, ratio=1.1), _run(1, 600, ratio=3.0)])
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
        assert kwargs["order"] is None
        assert kwargs["deadline"] is None

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
            tracker = await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, None, commit=True
            )
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
        # pass-through that only lapsed left those members dry for as long as
        # either new control was set on the schedule.
        mgr = _manager(plan=[])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        with patch(
            "custom_components.smart_irrigation.scheduler."
            "async_track_point_in_utc_time"
        ) as track:
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, None, commit=True
            )
        mgr.hass.loop.call_soon_threadsafe = Mock()
        mgr._execute_schedule = Mock()
        track.call_args[0][1](target)
        mgr._execute_schedule.assert_called_once()
        kwargs = mgr._execute_schedule.call_args.kwargs
        # Nothing was fitted, so the run carries neither an order nor a
        # deadline, exactly as the same schedule does with neither control set.
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
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, None, commit=False
            )
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
            await mgr._decide_and_arm(
                _schedule(fit_to_window=True), target, None, commit=True
            )
        assert "s1" not in mgr._finish_last_target
        mgr._execute_schedule = Mock()
        mgr.hass.loop.call_soon_threadsafe = Mock()
        track.call_args[0][1](target)
        assert mgr._finish_last_target["s1"] == target.isoformat()


class TestScheduleValidation:
    """Bad floor settings are rejected, not silently dropped."""

    def test_an_unknown_earliest_start_mode_is_rejected(self):
        mgr = _manager()
        with pytest.raises(ValueError, match="earliest start mode"):
            mgr._validate_schedule_data(_schedule(earliest_start_mode="whenever"))

    def test_a_malformed_earliest_start_time_is_rejected(self):
        mgr = _manager()
        with pytest.raises(ValueError, match="earliest start time"):
            mgr._validate_schedule_data(
                _schedule(
                    earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                    earliest_start_time="25:99",
                )
            )

    def test_a_valid_floor_passes(self):
        mgr = _manager()
        mgr._validate_schedule_data(
            _schedule(
                earliest_start_mode=const.SCHEDULE_EARLIEST_START_SUNSET,
                earliest_start_offset_minutes=120,
                fit_to_window=True,
            )
        )


class TestUpcomingRunsEstimatedFlag:
    """The dashboard has to be able to say "this start will still move"."""

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 12:00:00")
    async def test_estimated_before_the_decision_point(self):
        mgr = _manager(plan=[_run(0, 3600, maximum=4800)])
        mgr._schedules = [
            _schedule(
                earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                earliest_start_time="22:00",
            )
        ]
        mgr._next_target_time = AsyncMock(
            return_value=_local(2026, 6, 21, 6, 0)
        )
        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["estimated"] is True
        assert runs[0]["earliest_start_utc"] == _local(2026, 6, 20, 22, 0).isoformat()

    @pytest.mark.asyncio
    @freeze_time("2026-06-21 08:00:00")
    async def test_not_estimated_once_the_decision_point_has_passed(self):
        # Past the decision point the start is armed and no longer drifts, so
        # the number is a fact rather than a projection.
        mgr = _manager(plan=[_run(0, 3600, maximum=4800)])
        mgr._schedules = [
            _schedule(
                earliest_start_mode=const.SCHEDULE_EARLIEST_START_TIME,
                earliest_start_time="22:00",
            )
        ]
        mgr._next_target_time = AsyncMock(
            return_value=_local(2026, 6, 21, 6, 0)
        )
        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["estimated"] is False

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 12:00:00")
    async def test_a_plain_finish_schedule_is_never_flagged_estimated(self):
        mgr = _manager()
        mgr._schedules = [_schedule()]
        mgr._next_target_time = AsyncMock(
            return_value=_local(2026, 6, 21, 6, 0)
        )
        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["estimated"] is False
