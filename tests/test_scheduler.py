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
async def test_calculate_all_passes_delete_weather_data():
    manager, coordinator = _make_manager()
    await manager._perform_schedule_action("calculate", "all", "sched")
    coordinator._async_calculate_all.assert_awaited_once_with(delete_weather_data=True)


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
