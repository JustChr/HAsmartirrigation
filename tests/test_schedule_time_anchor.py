"""Tests for the start/finish time anchor + sequencing-aware duration + bucket
reset introduced for the irrigation-timer work."""

import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation import scheduler as scheduler_module
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


class TestFinishTrackerAdvance:
    """The self-rescheduling finish tracker must advance past an occurrence it
    already fired, instead of re-deriving the same still-future target and
    busy-looping the "run ASAP" branch every ~2s for the whole start→finish
    window (which re-fired irrigation thousands of times and ballooned the
    water-usage total)."""

    @staticmethod
    def _finish_sched():
        return _sched(
            type=const.SCHEDULE_TYPE_DAILY,
            time="06:00",
            time_anchor=const.SCHEDULE_TIME_ANCHOR_FINISH,
            action="irrigate",
            zones="all",
        )

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_rearm_advances_to_next_occurrence(self, coordinator, monkeypatch):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(return_value=7200)
        sid = self._finish_sched()[const.SCHEDULE_CONF_ID]
        sched = self._finish_sched()

        captured: list = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: captured.append(when) or Mock(),
        )

        # Re-arming for an occurrence we already fired must jump to the NEXT
        # occurrence's start (a future time), never the ~now+2s loop value.
        target1 = await mgr._next_target_time(sched)
        target2 = await mgr._next_target_time(sched, reference_utc=target1)
        assert target2 - target1 == datetime.timedelta(days=1)

        mgr._finish_last_target[sid] = target1.isoformat()
        await mgr._setup_finish_tracker(sched)
        assert captured[-1] == target2 - datetime.timedelta(seconds=7200)
        assert captured[-1] > dt_util.utcnow()  # future, not a busy-loop catch-up

        # Re-arming again at the same instant stays stable on that next
        # occurrence — it does not fall back into the now+2s catch-up loop (the
        # bug re-fired every ~2s here).
        await mgr._setup_finish_tracker(sched)
        assert captured[-1] == target2 - datetime.timedelta(seconds=7200)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_missed_start_catches_up_once(self, coordinator, monkeypatch):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(return_value=7200)

        # Finish 30 min from now with a 2h duration → ideal start is ~90 min in
        # the past, so a fresh arm is the "missed start" case (tz-agnostic).
        finish = dt_util.now() + datetime.timedelta(minutes=30)
        sched = self._finish_sched()
        sched[const.SCHEDULE_CONF_TIME] = f"{finish.hour:02d}:{finish.minute:02d}"
        sid = sched[const.SCHEDULE_CONF_ID]

        captured: list = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: captured.append(when) or Mock(),
        )

        # Missed start → catch up ASAP (now + 2s), not skipped.
        await mgr._setup_finish_tracker(sched)
        assert captured[-1] == dt_util.utcnow() + datetime.timedelta(seconds=2)

        # After the catch-up fires, the re-arm advances to the next occurrence
        # instead of scheduling another ASAP catch-up (the busy loop).
        target = await mgr._next_target_time(sched)
        mgr._finish_last_target[sid] = target.isoformat()
        await mgr._setup_finish_tracker(sched)
        assert captured[-1] > dt_util.utcnow() + datetime.timedelta(hours=1)


class TestBucketResetAfterRun:
    @pytest.mark.asyncio
    async def test_commit_progress_writes_bucket_and_time(
        self, coordinator, mock_store
    ):
        mock_store.async_update_zone = AsyncMock()
        mock_store.get_zone = Mock(return_value={})
        # No forecast-weighting target on the zone → run may replenish to 0.
        assert coordinator._run_ceiling({const.ZONE_ID: 5}) == 0.0
        await coordinator._commit_run_progress(
            5, new_bucket=0.0, volume_delta_l=0.0, dispatch=False
        )
        # Writes the bucket and records the irrigation time (dynamic value).
        mock_store.async_update_zone.assert_awaited_once()
        zone_id_arg, changes = mock_store.async_update_zone.await_args[0]
        assert zone_id_arg == 5
        assert changes[const.ZONE_BUCKET] == 0.0
        assert const.ZONE_LAST_IRRIGATION in changes
