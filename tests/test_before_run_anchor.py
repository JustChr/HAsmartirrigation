"""The pre-run calculation prices the run it is part of, not the one after it.

Under autocalcmode "before each irrigation run" the calculation that runs the
forecast weighting is reached from inside the run's own dispatch. Two independent
mechanisms then make the run-start resolver answer for the FOLLOWING run:

  (A) the fire callback writes _finish_last_target and pops _armed_runs before it
      calls _execute_schedule, so _advance_past_fired_occurrence treats this run's
      own target as already fired;
  (B) _next_governing_time resolves strictly after its reference, which defaults
      to now -- and at dispatch now IS the occurrence.

Measured before the fix: +1 day for both, on a daily schedule. These tests
therefore stand in ONLY for the clock/sun layer (_resolve_bound) and run
_next_governing_time and _advance_past_fired_occurrence for real. The resolver
suite (test_next_run_start_for_zone.py) stubs both and cannot see any of this,
which is why it stayed green.
"""

import datetime
from unittest.mock import AsyncMock

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus import scheduler as scheduler_module

from .test_scheduler import _make_manager

UTC = datetime.timezone.utc
SID = "s1"
# The run being dispatched, on a daily 06:00 UTC bound.
TODAY_RUN = datetime.datetime(2026, 9, 28, 6, 0, tzinfo=UTC)
TOMORROW_RUN = TODAY_RUN + datetime.timedelta(days=1)


def _schedule():
    return {
        const.SCHEDULE_CONF_ID: SID,
        const.SCHEDULE_CONF_ENABLED: True,
        const.SCHEDULE_CONF_ZONES: "all",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_NONE,
    }


def _daily_0600_bound(manager):
    """The clock/sun layer only. Everything above it stays real."""

    async def _resolve(schedule, end, reference_utc, *, direction):
        candidate = reference_utc.replace(hour=6, minute=0, second=0, microsecond=0)
        while candidate <= reference_utc:
            candidate += datetime.timedelta(days=1)
        return candidate

    manager._resolve_bound = _resolve


@pytest.fixture
def at_dispatch(monkeypatch):
    """Freeze the scheduler's clock at the dispatch moment."""
    monkeypatch.setattr(scheduler_module.dt_util, "utcnow", lambda: TODAY_RUN)


@pytest.mark.asyncio
async def test_the_resolver_answers_for_the_next_run_at_dispatch(at_dispatch):
    """Mechanism (A): not what we want, and the reason the anchor is passed in.

    Pinned so that anyone removing the explicit run start can read what they are
    falling back to.
    """
    manager, _ = _make_manager()
    manager._schedules = [_schedule()]
    _daily_0600_bound(manager)
    # Verbatim what the finish callback does before _execute_schedule
    # (scheduler.py:1656-1657).
    manager._finish_last_target[SID] = TODAY_RUN.isoformat()
    manager._armed_runs.pop(SID, None)

    assert await manager.async_next_run_start_for_zone(1) == TOMORROW_RUN


@pytest.mark.asyncio
async def test_a_plain_start_time_schedule_needs_no_fired_marker(at_dispatch):
    """Mechanism (B) alone: nothing recorded a fired occurrence here.

    This is why "return an occurrence fired within SAME_OCCURRENCE of now" does
    not fix it -- there is no fired occurrence to return, and the answer is still
    a day late.
    """
    manager, _ = _make_manager()
    manager._schedules = [_schedule()]
    _daily_0600_bound(manager)
    assert not manager._finish_last_target

    assert await manager.async_next_run_start_for_zone(1) == TOMORROW_RUN


@pytest.mark.asyncio
async def test_the_start_pinned_decide_and_run_names_the_run_start():
    """It commits AT THE FIRE, by its own docstring, not at a decision point.

    The review sorted this under the pre_committed=True paths that commit ahead of
    the run. It does not: run_callback sets _finish_last_target and hands straight
    to it. It leaves _armed_runs in place, but that arm carries TODAY's target
    while the resolver has advanced to tomorrow's, so the SAME_OCCURRENCE
    proximity test rejects it and mechanism (B) stands alone.
    """
    manager, _ = _make_manager()
    manager.coordinator.async_commit_pre_run_calculation = AsyncMock()
    manager.coordinator.async_plan_zone_runs = AsyncMock(return_value=[])

    # _decide_and_run_start_pinned(schedule, now, target, finish)
    await manager._decide_and_run_start_pinned(_schedule(), TODAY_RUN, TODAY_RUN, None)

    manager.coordinator.async_commit_pre_run_calculation.assert_awaited_once_with(
        "all", run_start=TODAY_RUN
    )
