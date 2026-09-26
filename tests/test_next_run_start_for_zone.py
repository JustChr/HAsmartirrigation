"""RecurringScheduleManager.async_next_run_start_for_zone (Eifel-Joe#21).

The forecast weighting runs inside calculate_module, so anything it calls that
reads a zone's bucket or duration closes a loop around the number being
computed. async_get_next_run_projection is therefore unusable there: it sizes
every zone from the bucket at the decision point. This resolver exists to answer
the one question the weighting needs -- when does the next run begin -- while
touching recurrence resolution only.

The recurrence math is tested in test_scheduler.py and the schedule-anchor
suites. These tests patch _next_governing_time so they exercise the resolver's
own decisions instead of re-testing its dependency.
"""

import datetime

import pytest

from custom_components.irrigation_plus import const

from tests.test_scheduler import _make_manager

UTC = datetime.timezone.utc
TARGET = datetime.datetime(2026, 9, 28, 6, 0, tzinfo=UTC)


def _schedule(sid="s1", zones="all", enabled=True):
    return {
        const.SCHEDULE_CONF_ID: sid,
        const.SCHEDULE_CONF_ENABLED: enabled,
        const.SCHEDULE_CONF_ZONES: zones,
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_NONE,
    }


def _fixed_target(manager, target=TARGET):
    """Stand in for the clock/sun resolution, which has its own tests."""

    async def _governing(schedule, end, reference_utc=None):
        return target

    async def _advance(schedule, end, t, *, quiet=False):
        return t

    manager._next_governing_time = _governing
    manager._advance_past_fired_occurrence = _advance


@pytest.mark.asyncio
async def test_a_schedule_naming_all_zones_answers_for_any_zone():
    manager, _ = _make_manager()
    manager._schedules = [_schedule()]
    _fixed_target(manager)

    assert await manager.async_next_run_start_for_zone(1) == TARGET


@pytest.mark.asyncio
async def test_a_schedule_naming_the_zone_answers_for_it():
    manager, _ = _make_manager()
    manager._schedules = [_schedule(zones=[2, 3])]
    _fixed_target(manager)

    assert await manager.async_next_run_start_for_zone(3) == TARGET


@pytest.mark.asyncio
async def test_a_schedule_not_naming_the_zone_answers_nothing():
    manager, _ = _make_manager()
    manager._schedules = [_schedule(zones=[2, 3])]
    _fixed_target(manager)

    assert await manager.async_next_run_start_for_zone(1) is None


@pytest.mark.asyncio
async def test_a_disabled_schedule_does_not_answer():
    manager, _ = _make_manager()
    manager._schedules = [_schedule(enabled=False)]
    _fixed_target(manager)

    assert await manager.async_next_run_start_for_zone(1) is None


@pytest.mark.asyncio
async def test_no_schedules_at_all_answers_nothing():
    manager, _ = _make_manager()
    manager._schedules = []

    assert await manager.async_next_run_start_for_zone(1) is None


@pytest.mark.asyncio
async def test_a_non_numeric_zone_id_answers_nothing():
    manager, _ = _make_manager()
    manager._schedules = [_schedule()]
    _fixed_target(manager)

    assert await manager.async_next_run_start_for_zone(None) is None


ARMED_START = datetime.datetime(2026, 9, 28, 5, 30, tzinfo=UTC)


@pytest.mark.asyncio
async def test_an_armed_run_supplies_the_exact_start():
    """The arm computed the real start earlier, and reading it costs nothing.

    For a Finish-anchored schedule the start is otherwise the target minus an
    estimated duration, and that estimate reads every zone's bucket -- the one
    call this resolver must not make.
    """
    manager, _ = _make_manager()
    manager._schedules = [_schedule()]
    _fixed_target(manager)
    manager._armed_runs = {"s1": {"target": TARGET, "start_utc": ARMED_START}}

    assert await manager.async_next_run_start_for_zone(1) == ARMED_START


@pytest.mark.asyncio
async def test_an_arm_for_another_occurrence_is_ignored():
    """Proximity, not equality: a solar bound answers seconds apart each time."""
    manager, _ = _make_manager()
    manager._schedules = [_schedule()]
    _fixed_target(manager)
    manager._armed_runs = {
        "s1": {
            "target": TARGET + datetime.timedelta(days=1),
            "start_utc": ARMED_START,
        }
    }

    assert await manager.async_next_run_start_for_zone(1) == TARGET


@pytest.mark.asyncio
async def test_an_arm_without_a_start_falls_back_to_the_target():
    manager, _ = _make_manager()
    manager._schedules = [_schedule()]
    _fixed_target(manager)
    manager._armed_runs = {"s1": {"target": TARGET, "start_utc": None}}

    assert await manager.async_next_run_start_for_zone(1) == TARGET


@pytest.mark.asyncio
async def test_the_earliest_of_several_schedules_wins():
    """Two schedules name the zone; the sooner run is the one being priced."""
    manager, _ = _make_manager()
    manager._schedules = [_schedule("late", zones=[1]), _schedule("soon", zones=[1])]
    later = TARGET + datetime.timedelta(hours=8)

    async def _governing(schedule, end, reference_utc=None):
        return TARGET if schedule[const.SCHEDULE_CONF_ID] == "soon" else later

    async def _advance(schedule, end, t, *, quiet=False):
        return t

    manager._next_governing_time = _governing
    manager._advance_past_fired_occurrence = _advance

    assert await manager.async_next_run_start_for_zone(1) == TARGET


@pytest.mark.asyncio
async def test_a_schedule_that_resolves_nothing_does_not_hide_one_that_does():
    """The unresolvable one is listed first, so a short-circuit would lose the other."""
    manager, _ = _make_manager()
    manager._schedules = [_schedule("dead", zones=[1]), _schedule("live", zones=[1])]

    async def _governing(schedule, end, reference_utc=None):
        return None if schedule[const.SCHEDULE_CONF_ID] == "dead" else TARGET

    async def _advance(schedule, end, t, *, quiet=False):
        return t

    manager._next_governing_time = _governing
    manager._advance_past_fired_occurrence = _advance

    assert await manager.async_next_run_start_for_zone(1) == TARGET


@pytest.mark.asyncio
async def test_the_resolver_never_prices_a_zone():
    """The cycle pin, and the reason this method exists at all.

    calculate_module calls this while computing the very bucket that
    get_total_irrigation_duration reads. Any path from here to that call is a
    loop, so it is made to raise: the resolver still has to answer.
    """
    manager, coordinator = _make_manager()
    manager._schedules = [_schedule()]
    _fixed_target(manager)

    def _explode(*args, **kwargs):
        raise AssertionError(
            "the resolver reached a zone duration, which closes the cycle "
            "calculate_module calls it from"
        )

    coordinator.get_total_irrigation_duration = _explode
    manager._estimate_duration = _explode
    manager._duration_bound = _explode
    manager._decision_point = _explode

    assert await manager.async_next_run_start_for_zone(1) == TARGET
