"""Behavioral tests for RecurringScheduleManager._perform_schedule_action.

Locks the fix for the scheduler signature bug. The 'calculate' action used to
call coordinator methods with the wrong arguments:
  - ``_async_calculate_all()`` with no ``delete_weather_data`` (required), and
  - ``async_calculate_zone(zone_id)`` with no ``weatherdata`` (required),
which raised ``TypeError`` at runtime — silently swallowed by the surrounding
try/except, so scheduled calculations never ran.

These tests use ``create_autospec`` so the mock enforces the *real* method
signatures; a regression to the broken call shape raises ``TypeError`` inside
``_perform_schedule_action`` (which re-raises) and fails the test.
"""

from unittest.mock import MagicMock, create_autospec

import pytest

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager


def _make_manager():
    coordinator = create_autospec(SmartIrrigationCoordinator, instance=True)
    manager = RecurringScheduleManager(MagicMock(), coordinator)
    return manager, coordinator


@pytest.mark.asyncio
async def test_calculate_all_calls_calculate_all():
    manager, coordinator = _make_manager()
    await manager._perform_schedule_action("calculate", "all", "sched")
    # Per-zone consumption: no wholesale clear flag any more.
    coordinator._async_calculate_all.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_calculate_specific_zones_routes_through_aggregation():
    manager, coordinator = _make_manager()
    await manager._perform_schedule_action("calculate", ["1", "2"], "sched")
    assert coordinator.async_update_zone_config.await_count == 2
    coordinator.async_update_zone_config.assert_any_await(
        "1", {const.ATTR_CALCULATE: True}
    )
    coordinator.async_update_zone_config.assert_any_await(
        "2", {const.ATTR_CALCULATE: True}
    )
    # the broken direct-calc path must not be used
    coordinator.async_calculate_zone.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_all_calls_update_all():
    manager, coordinator = _make_manager()
    await manager._perform_schedule_action("update", "all", "sched")
    coordinator._async_update_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_specific_zones_calls_update_zone():
    manager, coordinator = _make_manager()
    await manager._perform_schedule_action("update", ["3"], "sched")
    coordinator._async_update_zone.assert_awaited_once_with("3")


@pytest.mark.asyncio
async def test_irrigate_skips_when_conditions_met():
    manager, coordinator = _make_manager()
    coordinator._check_skip_conditions.return_value = True
    await manager._perform_schedule_action("irrigate", "all", "sched")
    coordinator._irrigate_linked_entities.assert_not_awaited()


@pytest.mark.asyncio
async def test_irrigate_runs_and_resets_counter_when_not_skipped():
    manager, coordinator = _make_manager()
    coordinator._check_skip_conditions.return_value = False
    await manager._perform_schedule_action("irrigate", "all", "sched")
    coordinator._irrigate_linked_entities.assert_awaited_once()
    coordinator._reset_days_since_irrigation.assert_awaited_once()


@pytest.mark.asyncio
async def test_upcoming_runs_resolves_clock_and_marks_interval():
    """Upcoming-runs computes a clock target, skips disabled, flags interval."""
    manager, _ = _make_manager()
    manager._schedules = [
        {
            const.SCHEDULE_CONF_ID: "a",
            const.SCHEDULE_CONF_NAME: "Morning",
            const.SCHEDULE_CONF_TYPE: const.SCHEDULE_TYPE_DAILY,
            const.SCHEDULE_CONF_TIME: "06:00",
            const.SCHEDULE_CONF_ACTION: "irrigate",
            const.SCHEDULE_CONF_ZONES: "all",
            const.SCHEDULE_CONF_ENABLED: True,
        },
        {
            const.SCHEDULE_CONF_ID: "b",
            const.SCHEDULE_CONF_NAME: "Every 6h",
            const.SCHEDULE_CONF_TYPE: const.SCHEDULE_TYPE_INTERVAL,
            const.SCHEDULE_CONF_INTERVAL_HOURS: 6,
            const.SCHEDULE_CONF_ACTION: "update",
            const.SCHEDULE_CONF_ENABLED: True,
        },
        {
            const.SCHEDULE_CONF_ID: "c",
            const.SCHEDULE_CONF_NAME: "Off",
            const.SCHEDULE_CONF_TYPE: const.SCHEDULE_TYPE_DAILY,
            const.SCHEDULE_CONF_TIME: "07:00",
            const.SCHEDULE_CONF_ENABLED: False,
        },
    ]

    runs = await manager.async_get_upcoming_runs()
    by_id = {r["schedule_id"]: r for r in runs}

    assert set(by_id) == {"a", "b"}  # disabled schedule excluded
    assert by_id["a"]["next_run_utc"] is not None
    assert by_id["a"]["action"] == "irrigate"
    assert by_id["a"]["time_anchor"] == const.SCHEDULE_TIME_ANCHOR_START
    assert by_id["b"]["next_run_utc"] is None  # interval has no fixed clock target
    assert by_id["b"]["interval_hours"] == 6
