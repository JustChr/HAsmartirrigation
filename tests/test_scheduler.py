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

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, create_autospec

import homeassistant.util.dt as dt_util
import pytest

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager

# Reuse the __new__-built coordinator fixture from the rain-delay suite to
# exercise the real _irrigate_linked_entities bool contract without re-wiring a
# full coordinator here (review finding A).
from tests.test_rain_delay import _coord, _eligible_zone


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
    # review finding A: the reset is now gated on water actually being delivered,
    # so the linked-entity dispatch must report True for the reset to fire.
    coordinator._irrigate_linked_entities = AsyncMock(return_value=True)
    await manager._perform_schedule_action("irrigate", "all", "sched")
    coordinator._irrigate_linked_entities.assert_awaited_once()
    coordinator._reset_days_since_irrigation.assert_awaited_once()


@pytest.mark.asyncio
async def test_irrigate_does_not_reset_counter_when_no_water_delivered():
    """review finding A: a scheduled 'irrigate' whose dispatch helpers deliver no
    water (rain-delay / all-vetoed / nothing due) must NOT reset the days-since
    counter — otherwise the days_between_irrigation guard skips the next due run
    and strands the garden dry."""
    manager, coordinator = _make_manager()
    coordinator._check_skip_conditions = AsyncMock(return_value=False)
    coordinator._irrigate_linked_entities = AsyncMock(return_value=False)
    coordinator._dispatch_distributor_cycles = AsyncMock(return_value=False)
    await manager._perform_schedule_action("irrigate", "all", "sched")
    coordinator._irrigate_linked_entities.assert_awaited_once()
    coordinator._dispatch_distributor_cycles.assert_awaited_once()
    coordinator._reset_days_since_irrigation.assert_not_awaited()


@pytest.mark.asyncio
async def test_irrigate_linked_entities_returns_false_on_rain_delay(monkeypatch):
    """The bool contract: while a rain delay is active the scheduled path
    delivers no water and reports False so the caller can skip the reset."""
    future = (dt_util.now() + timedelta(hours=6)).isoformat()
    coord = _coord(
        monkeypatch,
        zones=[_eligible_zone()],
        config=SimpleNamespace(
            rain_delay_until=future,
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        ),
    )
    assert await coord._irrigate_linked_entities() is False


@pytest.mark.asyncio
async def test_irrigate_linked_entities_returns_true_on_normal_dispatch(monkeypatch):
    """A normal dispatch of an eligible zone reports True (water delivered)."""
    coord = _coord(monkeypatch, zones=[_eligible_zone()])
    coord._apply_live_durations = AsyncMock(side_effect=lambda zs: zs)
    coord._irrigate_zones_parallel = AsyncMock()
    assert await coord._irrigate_linked_entities() is True
    coord._irrigate_zones_parallel.assert_awaited_once()


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
