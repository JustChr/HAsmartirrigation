from unittest.mock import AsyncMock, Mock

from custom_components.smart_irrigation.scheduler import RecurringScheduleManager


def _sched():
    """A schedule manager with a fully-mocked hass + coordinator."""
    return RecurringScheduleManager(Mock(), Mock())


async def test_scheduled_irrigate_orders_linked_then_dispatch_then_reset():
    """H6 (review #15): enforce the scheduled-irrigate call ORDER.

    The existing dispatches-even-when-no-normal-zone test only asserts two
    independent assert_awaited_once calls, which do NOT prove ordering. Attach
    the three coordinator methods to a single parent manager mock and assert
    the recorded order is linked-entities -> dispatch -> reset (scheduler.py
    lines 782/787/788). Fails if those lines were reordered.
    """
    sched = _sched()
    coord = sched.coordinator
    coord._check_skip_conditions = AsyncMock(return_value=False)
    # A single parent records the child awaits in call order.
    manager = Mock()
    manager.attach_mock(AsyncMock(), "linked")
    manager.attach_mock(AsyncMock(), "dispatch")
    manager.attach_mock(AsyncMock(), "reset")
    coord._irrigate_linked_entities = manager.linked
    coord._dispatch_distributor_cycles = manager.dispatch
    coord._reset_days_since_irrigation = manager.reset
    await sched._perform_schedule_action("irrigate", "all", "test")
    names = [
        c[0] for c in manager.mock_calls if c[0] in ("linked", "dispatch", "reset")
    ]
    assert names == ["linked", "dispatch", "reset"]


async def test_scheduled_irrigate_dispatches_distributors_even_when_no_normal_zone():
    sched = _sched()
    coord = sched.coordinator
    coord._check_skip_conditions = AsyncMock(return_value=False)
    coord._irrigate_linked_entities = AsyncMock()  # no-op: no normal zones due
    coord._dispatch_distributor_cycles = AsyncMock()
    coord._reset_days_since_irrigation = AsyncMock()
    await sched._perform_schedule_action("irrigate", "all", "test")
    coord._dispatch_distributor_cycles.assert_awaited_once_with("all")
    # ordering: dispatch runs after linked-entities
    coord._irrigate_linked_entities.assert_awaited_once_with("all")


async def test_weather_skip_blocks_distributor_dispatch():
    sched = _sched()
    coord = sched.coordinator
    coord._check_skip_conditions = AsyncMock(return_value=True)
    coord._last_skip_evaluation = {"checks": []}
    coord._record_skipped_run = AsyncMock()
    coord._dispatch_distributor_cycles = AsyncMock()
    await sched._perform_schedule_action("irrigate", "all", "test")
    coord._dispatch_distributor_cycles.assert_not_awaited()  # returns at the skip branch
    coord._record_skipped_run.assert_awaited_once()
