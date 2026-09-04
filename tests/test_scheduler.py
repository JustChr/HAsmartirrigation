"""Behavioral tests for RecurringScheduleManager._perform_scheduled_irrigation.

A recurring schedule only ever irrigates, so this covers the one dispatch path
and the conditions under which it delivers no water.

These tests use ``create_autospec`` so the mock enforces the *real* coordinator
method signatures; a call built with the wrong arguments raises ``TypeError``
inside ``_perform_scheduled_irrigation`` (which re-raises) and fails the test,
rather than being swallowed by the surrounding try/except as it once was.
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, create_autospec

import homeassistant.util.dt as dt_util
import pytest

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.scheduler import RecurringScheduleManager

# Reuse the __new__-built coordinator fixture from the rain-delay suite to
# exercise the real _irrigate_linked_entities bool contract without re-wiring a
# full coordinator here (review finding A).
from tests.test_rain_delay import _coord, _eligible_zone


def _make_manager():
    coordinator = create_autospec(SmartIrrigationCoordinator, instance=True)
    manager = RecurringScheduleManager(MagicMock(), coordinator)
    return manager, coordinator


@pytest.mark.asyncio
async def test_irrigate_skips_when_conditions_met():
    manager, coordinator = _make_manager()
    coordinator._check_skip_conditions.return_value = True
    await manager._perform_scheduled_irrigation("all", "sched")
    coordinator._irrigate_linked_entities.assert_not_awaited()


@pytest.mark.asyncio
async def test_irrigate_runs_and_resets_counter_when_not_skipped():
    manager, coordinator = _make_manager()
    coordinator._check_skip_conditions.return_value = False
    # review finding A: the reset is now gated on water actually being delivered,
    # so the linked-entity dispatch must report True for the reset to fire.
    coordinator._irrigate_linked_entities = AsyncMock(return_value=True)
    await manager._perform_scheduled_irrigation("all", "sched")
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
    await manager._perform_scheduled_irrigation("all", "sched")
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
            const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
            const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
            const.SCHEDULE_CONF_START_TIME: "06:00",
            const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_NONE,
            const.SCHEDULE_CONF_ACTION: "irrigate",
            const.SCHEDULE_CONF_ZONES: "all",
            const.SCHEDULE_CONF_ENABLED: True,
        },
        {
            const.SCHEDULE_CONF_ID: "b",
            const.SCHEDULE_CONF_NAME: "Every 6h",
            const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_INTERVAL,
            const.SCHEDULE_CONF_INTERVAL_HOURS: 6,
            const.SCHEDULE_CONF_ACTION: "irrigate",
            const.SCHEDULE_CONF_ENABLED: True,
        },
        {
            const.SCHEDULE_CONF_ID: "c",
            const.SCHEDULE_CONF_NAME: "Off",
            const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
            const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
            const.SCHEDULE_CONF_START_TIME: "07:00",
            const.SCHEDULE_CONF_ENABLED: False,
        },
    ]

    runs = await manager.async_get_upcoming_runs()
    by_id = {r["schedule_id"]: r for r in runs}

    assert set(by_id) == {"a", "b"}  # disabled schedule excluded
    assert by_id["a"]["next_run_utc"] is not None
    assert by_id["a"]["action"] == "irrigate"
    assert by_id["a"]["anchor"] == const.SCHEDULE_ANCHOR_START
    assert by_id["b"]["next_run_utc"] is None  # interval has no fixed clock target
    assert by_id["b"]["interval_hours"] == 6
