"""The run's start reaches the precipitation guard from every place that asks.

The guard's window starts at the run's local date, so each caller has to say
which run it is asking about: dispatch (now, by naming none), the schedule
projection (its planned start) and the dashboard outlook (the next scheduled
irrigate run). A preview always names a moment, because the guard reads a
missing start as dispatch and logs at INFO there.
"""

import datetime
from unittest.mock import AsyncMock, Mock, call

import homeassistant.util.dt as dt_util
from freezegun import freeze_time

from custom_components.irrigation_plus import SmartIrrigationCoordinator
from custom_components.irrigation_plus.scheduler import RecurringScheduleManager

UTC = datetime.timezone.utc
START = datetime.datetime(2026, 9, 13, 4, 20, tzinfo=UTC)
CALCULATE = {"action": "calculate", "next_run_utc": "2026-09-12T21:00:00+00:00"}
FROZEN = datetime.datetime(2026, 9, 15, 7, 10, tzinfo=UTC)
# A finish-anchored run that is still watering stays in the upcoming list at
# its start, which by now lies in the past.
WATERING = {
    "action": "irrigate",
    "next_run_utc": (FROZEN - datetime.timedelta(minutes=30)).isoformat(),
}
LATER_TODAY = datetime.datetime(2026, 9, 15, 20, 0, tzinfo=UTC)


def _off(check_id):
    return {"id": check_id, "enabled": False, "would_skip": False}


def _outlook_coordinator(upcoming):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.store = Mock()
    coord.store.async_get_config = AsyncMock(return_value={})
    coord.recurring_schedule_manager = Mock()
    coord.recurring_schedule_manager.async_get_upcoming_runs = AsyncMock(
        return_value=upcoming
    )
    coord.async_evaluate_skip_conditions = AsyncMock(
        return_value={"would_skip": False, "checks": []}
    )
    coord.async_get_cached_zone_estimates = AsyncMock(return_value={})
    coord.get_zone_faults = Mock(return_value={})
    coord.get_zone_skips = Mock(return_value={})
    coord.get_active_runs = Mock(return_value={})
    return coord


def _projection_manager():
    manager = RecurringScheduleManager.__new__(RecurringScheduleManager)
    manager.coordinator = Mock()
    manager.coordinator.async_evaluate_skip_conditions = AsyncMock(
        return_value={"would_skip": False, "checks": []}
    )
    manager.coordinator._project_days_between_to_next_run = Mock()
    manager.coordinator._rain_delay_until_dt = Mock(return_value=None)
    return manager


async def test_evaluation_hands_the_run_start_to_the_precipitation_guard():
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.store = Mock()
    coord.store.async_get_config = AsyncMock(return_value={})
    coord._eval_precipitation = AsyncMock(return_value=_off("precipitation"))
    coord._eval_days_between = AsyncMock(return_value=_off("days_between"))
    coord._eval_temp = AsyncMock(return_value=_off("temperature"))
    coord._eval_wind = AsyncMock(return_value=_off("wind"))
    coord._eval_freeze = AsyncMock(return_value=_off("freeze"))
    coord._eval_rain_sensor = AsyncMock(return_value=_off("rain_sensor"))

    await coord.async_evaluate_skip_conditions(run_start=START)

    assert coord._eval_precipitation.await_args.args == ({}, START)


async def test_the_schedule_projection_asks_about_its_planned_start():
    manager = _projection_manager()

    await manager._projected_skip(START)

    assert manager.coordinator.async_evaluate_skip_conditions.await_args.kwargs == {
        "run_start": START
    }


async def test_a_projection_without_a_start_still_names_a_moment():
    manager = _projection_manager()

    with freeze_time(FROZEN):
        await manager._projected_skip(None)

    kwargs = manager.coordinator.async_evaluate_skip_conditions.await_args.kwargs
    assert kwargs["run_start"] == FROZEN
    assert kwargs["run_start"].utcoffset() == datetime.timedelta(0)


async def test_the_outlook_asks_about_the_next_irrigate_run():
    coord = _outlook_coordinator(
        [CALCULATE, {"action": "irrigate", "next_run_utc": START.isoformat()}]
    )

    with freeze_time(START - datetime.timedelta(hours=8)):
        await coord.async_get_irrigation_outlook()

    assert coord.async_evaluate_skip_conditions.await_args.kwargs == {
        "run_start": dt_util.parse_datetime(START.isoformat())
    }


async def test_with_no_irrigate_run_the_outlook_still_names_a_moment():
    coord = _outlook_coordinator([CALCULATE])

    with freeze_time(FROZEN):
        await coord.async_get_irrigation_outlook()

    kwargs = coord.async_evaluate_skip_conditions.await_args.kwargs
    assert kwargs["run_start"] == FROZEN
    assert kwargs["run_start"].utcoffset() == datetime.timedelta(0)


async def test_the_outlook_passes_over_a_run_that_is_already_watering():
    coord = _outlook_coordinator(
        [WATERING, {"action": "irrigate", "next_run_utc": LATER_TODAY.isoformat()}]
    )

    with freeze_time(FROZEN):
        await coord.async_get_irrigation_outlook()

    kwargs = coord.async_evaluate_skip_conditions.await_args.kwargs
    assert kwargs["run_start"] == LATER_TODAY


async def test_with_only_a_run_already_watering_the_outlook_names_now():
    coord = _outlook_coordinator([WATERING])

    with freeze_time(FROZEN):
        await coord.async_get_irrigation_outlook()

    kwargs = coord.async_evaluate_skip_conditions.await_args.kwargs
    assert kwargs["run_start"] == FROZEN
    assert kwargs["run_start"].utcoffset() == datetime.timedelta(0)


async def test_dispatch_names_no_run_start():
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.async_evaluate_skip_conditions = AsyncMock(
        return_value={"would_skip": False, "checks": []}
    )

    assert await coord._check_skip_conditions() is False

    assert coord.async_evaluate_skip_conditions.await_args == call()
