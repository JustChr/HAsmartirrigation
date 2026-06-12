"""Tests for the start/finish time anchor + sequencing-aware duration + bucket
reset introduced for the irrigation-timer work."""

import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def _sched(**kw):
    base = {
        const.SCHEDULE_CONF_ID: "s1",
        const.SCHEDULE_CONF_NAME: "x",
        const.SCHEDULE_CONF_TYPE: const.SCHEDULE_TYPE_DAILY,
    }
    base.update(kw)
    return base


class TestTimeAnchor:
    """`_time_anchor` resolves explicit value, else the legacy flag."""

    def test_explicit_wins(self):
        assert (
            RecurringScheduleManager._time_anchor(_sched(time_anchor="finish"))
            == const.SCHEDULE_TIME_ANCHOR_FINISH
        )
        assert (
            RecurringScheduleManager._time_anchor(_sched(time_anchor="start"))
            == const.SCHEDULE_TIME_ANCHOR_START
        )

    def test_legacy_solar_account_for_duration(self):
        finish = _sched(type=const.SCHEDULE_TYPE_SUNRISE, account_for_duration=True)
        start = _sched(type=const.SCHEDULE_TYPE_SUNSET, account_for_duration=False)
        assert (
            RecurringScheduleManager._time_anchor(finish)
            == const.SCHEDULE_TIME_ANCHOR_FINISH
        )
        assert (
            RecurringScheduleManager._time_anchor(start)
            == const.SCHEDULE_TIME_ANCHOR_START
        )

    def test_legacy_clock_always_start(self):
        # Clock types never honored account_for_duration, so they stay "start"
        # even with the legacy flag set, to preserve existing behavior.
        s = _sched(type=const.SCHEDULE_TYPE_DAILY, account_for_duration=True)
        assert (
            RecurringScheduleManager._time_anchor(s) == const.SCHEDULE_TIME_ANCHOR_START
        )


class TestClockDayMatches:
    def test_daily_always(self):
        dt = datetime.datetime(2026, 6, 10)
        assert RecurringScheduleManager._clock_day_matches(
            _sched(type=const.SCHEDULE_TYPE_DAILY), dt
        )

    def test_weekly(self):
        dt = datetime.datetime(2026, 6, 10)
        today = WEEKDAYS[dt.weekday()]
        other = WEEKDAYS[(dt.weekday() + 1) % 7]
        assert RecurringScheduleManager._clock_day_matches(
            _sched(type=const.SCHEDULE_TYPE_WEEKLY, days_of_week=[today]), dt
        )
        assert not RecurringScheduleManager._clock_day_matches(
            _sched(type=const.SCHEDULE_TYPE_WEEKLY, days_of_week=[other]), dt
        )

    def test_monthly(self):
        dt = datetime.datetime(2026, 6, 10)
        assert RecurringScheduleManager._clock_day_matches(
            _sched(type=const.SCHEDULE_TYPE_MONTHLY, day_of_month=10), dt
        )
        assert not RecurringScheduleManager._clock_day_matches(
            _sched(type=const.SCHEDULE_TYPE_MONTHLY, day_of_month=11), dt
        )


@pytest.fixture
def coordinator(hass, mock_store):
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    entry = Mock()
    entry.unique_id = "test_entry"
    entry.data = {}
    entry.options = {}
    coord = SmartIrrigationCoordinator(hass, None, entry, mock_store)
    coord.store = mock_store
    return coord


def _zones():
    return [
        {
            const.ZONE_ID: 1,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_DURATION: 300,
        },
        {
            const.ZONE_ID: 2,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_DURATION: 600,
        },
        {
            const.ZONE_ID: 3,
            const.ZONE_STATE: const.ZONE_STATE_DISABLED,
            const.ZONE_DURATION: 999,
        },
    ]


class TestSequencingAwareDuration:
    @pytest.mark.asyncio
    async def test_sequential_sum(self, coordinator, mock_store):
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration() == 900

    @pytest.mark.asyncio
    async def test_parallel_max(self, coordinator, mock_store):
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL)
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration() == 600

    @pytest.mark.asyncio
    async def test_rotating_sums(self, coordinator, mock_store):
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_ROTATING)
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration() == 900

    @pytest.mark.asyncio
    async def test_target_zone_filter(self, coordinator, mock_store):
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration([1]) == 300
        assert await coordinator.get_total_irrigation_duration([1, 2]) == 900


class TestBucketResetAfterRun:
    @pytest.mark.asyncio
    async def test_resets_to_zero(self, coordinator, mock_store):
        mock_store.async_update_zone = AsyncMock()
        # No forecast-weighting target on the zone → full replenish to 0.
        mock_store.get_zone = Mock(return_value={})
        await coordinator._reset_zone_bucket_after_run(5)
        # Resets the bucket to 0 and records the irrigation time (dynamic value).
        mock_store.async_update_zone.assert_awaited_once()
        zone_id_arg, changes = mock_store.async_update_zone.await_args[0]
        assert zone_id_arg == 5
        assert changes[const.ZONE_BUCKET] == 0.0
        assert const.ZONE_LAST_IRRIGATION in changes
