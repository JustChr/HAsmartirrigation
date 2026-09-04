"""A schedule whose numeric fields are stored as ``null``.

Found auditing the #107 schedule dialog. The panel's day-of-month and
interval-hours inputs read their value with ``parseInt``, and clearing a
number input gives ``""`` — so ``parseInt`` returned ``NaN``, which
``JSON.stringify`` writes as ``null`` on the wire. Nothing between the input
and the store rejected it: ``_validate_schedule_data`` returns early for an
interval recurrence and never looks at ``interval_hours`` at all.

Both read sites used the get-default form (``schedule.get(key, 24)``), which
returns ``None`` when the key is PRESENT and null — the default only applies
to a missing key. ``distributor.py`` already documents the fix as a house
rule ("``or default`` (not the get-default) so a persisted None can't
raise"); the scheduler had not applied it.

These tests drive the two real entry points rather than the guards, because
the guards are the thing under test: what matters is that a store carrying a
null still arms, since a store already in that state cannot be repaired
through a panel whose integration will not load.
"""

import datetime
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.scheduler import RecurringScheduleManager


def _manager():
    coordinator = create_autospec(SmartIrrigationCoordinator, instance=True)
    manager = RecurringScheduleManager(MagicMock(), coordinator)
    manager.coordinator = MagicMock()
    manager.coordinator.store.async_get_config = AsyncMock(return_value={})
    manager._persist_fired_occurrences = AsyncMock()
    return manager


def _interval_schedule(**kw):
    """An un-anchored interval schedule: no start_time, so it takes the
    free-running branch of _setup_interval_tracker rather than the anchored
    one, which already guarded None."""
    s = {
        const.SCHEDULE_CONF_ID: "bad",
        const.SCHEDULE_CONF_NAME: "hours cleared",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_INTERVAL,
        const.SCHEDULE_CONF_ENABLED: True,
        const.SCHEDULE_CONF_INTERVAL_HOURS: None,
        const.SCHEDULE_CONF_ZONES: "all",
    }
    s.update(kw)
    return s


def _daily_schedule(schedule_id="good"):
    return {
        const.SCHEDULE_CONF_ID: schedule_id,
        const.SCHEDULE_CONF_NAME: "healthy daily",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_ENABLED: True,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_START_TIME: "06:00",
        const.SCHEDULE_CONF_ZONES: "all",
    }


class TestANullIntervalStillArms:
    """The severe one: this used to raise out of async_setup_entry."""

    @pytest.mark.asyncio
    async def test_a_null_interval_does_not_raise(self):
        # timedelta(hours=None) raises TypeError, and nothing on the path from
        # async_setup_entry down to here catches it.
        tracker = await _manager()._setup_interval_tracker(_interval_schedule())
        assert tracker is not None

    @pytest.mark.asyncio
    async def test_a_null_interval_falls_back_to_24_hours(self):
        """Not just "does not raise" — it has to arm on a sane period.

        Asserted through the real ``async_track_time_interval`` argument
        rather than by re-reading the schedule dict, since the dict is
        exactly what is wrong.
        """
        manager = _manager()
        seen = {}

        def _capture(hass, action, interval):
            seen["interval"] = interval
            return lambda: None

        import custom_components.irrigation_plus.scheduler as scheduler_module

        original = scheduler_module.async_track_time_interval
        scheduler_module.async_track_time_interval = _capture
        try:
            await manager._setup_interval_tracker(_interval_schedule())
        finally:
            scheduler_module.async_track_time_interval = original

        assert seen["interval"] == datetime.timedelta(hours=24)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("stored", [None, 0, -5, "", "abc"])
    async def test_every_unusable_interval_arms_on_the_fallback(self, stored):
        """A null is what the panel produced, but it is not the only way the
        field can be unusable, and a zero or negative period would spin
        async_track_time_interval rather than merely raise."""
        manager = _manager()
        seen = {}

        def _capture(hass, action, interval):
            seen["interval"] = interval
            return lambda: None

        import custom_components.irrigation_plus.scheduler as scheduler_module

        original = scheduler_module.async_track_time_interval
        scheduler_module.async_track_time_interval = _capture
        try:
            await manager._setup_interval_tracker(
                _interval_schedule(**{const.SCHEDULE_CONF_INTERVAL_HOURS: stored})
            )
        finally:
            scheduler_module.async_track_time_interval = original

        assert seen["interval"] == datetime.timedelta(hours=24)

    @pytest.mark.asyncio
    async def test_a_usable_interval_is_still_honoured(self):
        """The guard must not flatten a real setting to the fallback."""
        manager = _manager()
        seen = {}

        def _capture(hass, action, interval):
            seen["interval"] = interval
            return lambda: None

        import custom_components.irrigation_plus.scheduler as scheduler_module

        original = scheduler_module.async_track_time_interval
        scheduler_module.async_track_time_interval = _capture
        try:
            await manager._setup_interval_tracker(
                _interval_schedule(**{const.SCHEDULE_CONF_INTERVAL_HOURS: 6})
            )
        finally:
            scheduler_module.async_track_time_interval = original

        assert seen["interval"] == datetime.timedelta(hours=6)


class TestTheBlastRadius:
    """What made this worth a hotfix rather than a note: it was never
    confined to the schedule carrying the bad value."""

    @pytest.mark.asyncio
    async def test_one_bad_schedule_does_not_disarm_the_others(self):
        # _setup_schedule_trackers loops with no try/except, so the raise
        # aborted the whole loop: every schedule ordered AFTER the bad one
        # got no tracker either, and async_load_schedules propagated the
        # error into async_setup_entry.
        manager = _manager()
        manager._schedules = [_interval_schedule(), _daily_schedule()]

        await manager._setup_schedule_trackers()

        assert "good" in manager._schedule_trackers
        assert "bad" in manager._schedule_trackers


class TestANullDayOfMonthStillMatches:
    """The quiet one: no crash, the schedule simply never fired again."""

    @staticmethod
    def _monthly(day):
        return {
            const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_MONTHLY,
            const.SCHEDULE_CONF_DAY_OF_MONTH: day,
        }

    def test_a_null_day_of_month_matches_the_first(self):
        # `dt_local.day == None` is False for every one of the 367 candidates
        # _next_governing_time tries, so the schedule never armed at all.
        first = datetime.datetime(2026, 9, 1, 6, 0)
        assert RecurringScheduleManager._recurrence_day_matches(
            self._monthly(None), first
        )

    def test_a_null_day_of_month_does_not_match_every_day(self):
        """The failure mode of an over-broad fix: falling back to "always
        true" would water a monthly schedule daily, which is worse than not
        watering it."""
        second = datetime.datetime(2026, 9, 2, 6, 0)
        assert not RecurringScheduleManager._recurrence_day_matches(
            self._monthly(None), second
        )

    def test_a_real_day_of_month_is_unaffected(self):
        assert RecurringScheduleManager._recurrence_day_matches(
            self._monthly(14), datetime.datetime(2026, 9, 14, 6, 0)
        )
        assert not RecurringScheduleManager._recurrence_day_matches(
            self._monthly(14), datetime.datetime(2026, 9, 15, 6, 0)
        )
