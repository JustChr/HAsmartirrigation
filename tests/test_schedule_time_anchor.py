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


class TestIntervalStartTime:
    """An interval schedule with a start_time anchor is phase-locked to that
    clock time (carsten12 / discussion #31): fires at start_time and every
    interval_hours after, exposes a real next_run_utc, and re-arms onto the next
    occurrence (no double-fire). Without a start_time it free-runs as before."""

    @staticmethod
    def _sched(**kw):
        base = {
            const.SCHEDULE_CONF_ID: "i1",
            const.SCHEDULE_CONF_NAME: "pots",
            const.SCHEDULE_CONF_TYPE: const.SCHEDULE_TYPE_INTERVAL,
            const.SCHEDULE_CONF_INTERVAL_HOURS: 12,
            const.SCHEDULE_CONF_ACTION: "irrigate",
            const.SCHEDULE_CONF_ZONES: "all",
        }
        base.update(kw)
        return base

    @pytest.fixture(autouse=True)
    def _utc_tz(self):
        """Pin HA's default timezone to UTC so local == UTC and the anchored
        clock assertions below are tz-independent (the test env otherwise
        defaults to a Pacific zone from the HA coordinates)."""
        import homeassistant.util.dt as dt_util

        original = dt_util.DEFAULT_TIME_ZONE
        dt_util.set_default_time_zone(dt_util.UTC)
        yield
        dt_util.set_default_time_zone(original)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_anchor_same_day_step(self, coordinator):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        sched = self._sched(start_time="07:00")
        target = mgr._next_interval_target(sched, dt_util.utcnow())
        # 07:00 already passed → +12h → 19:00 today (local == UTC in tests).
        assert dt_util.as_local(target).hour == 19
        assert dt_util.as_local(target).date() == datetime.date(2026, 6, 10)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 06:00:00")
    async def test_anchor_before_first(self, coordinator):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        target = mgr._next_interval_target(
            self._sched(start_time="07:00"), dt_util.utcnow()
        )
        assert dt_util.as_local(target).hour == 7
        assert dt_util.as_local(target).date() == datetime.date(2026, 6, 10)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 20:00:00")
    async def test_anchor_rolls_across_midnight(self, coordinator):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        # 07:00 and 19:00 both passed → next is 07:00 tomorrow (phase-locked).
        target = mgr._next_interval_target(
            self._sched(start_time="07:00"), dt_util.utcnow()
        )
        assert dt_util.as_local(target).hour == 7
        assert dt_util.as_local(target).date() == datetime.date(2026, 6, 11)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_no_start_time_returns_none(self, coordinator):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        assert mgr._next_interval_target(self._sched(), dt_util.utcnow()) is None

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_invalid_inputs_return_none(self, coordinator):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        now = dt_util.utcnow()
        assert (
            mgr._next_interval_target(self._sched(start_time="nonsense"), now) is None
        )
        assert (
            mgr._next_interval_target(
                self._sched(start_time="07:00", interval_hours=0), now
            )
            is None
        )

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_rearm_advances_not_double_fire(self, coordinator):
        """Re-arming from the just-fired target must jump to the next occurrence,
        not re-derive the same time (which would immediately re-fire)."""
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        sched = self._sched(start_time="07:00")
        target1 = await mgr._next_target_time(sched)
        target2 = await mgr._next_target_time(sched, reference_utc=target1)
        assert target2 - target1 == datetime.timedelta(hours=12)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_tracker_uses_point_in_time_when_anchored(
        self, coordinator, monkeypatch
    ):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        point_calls: list = []
        interval_calls: list = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: point_calls.append(when) or Mock(),
        )
        monkeypatch.setattr(
            scheduler_module,
            "async_track_time_interval",
            lambda hass, cb, delta: interval_calls.append(delta) or Mock(),
        )

        await mgr._setup_interval_tracker(self._sched(start_time="07:00"))
        assert len(point_calls) == 1 and not interval_calls
        assert dt_util.as_local(point_calls[0]).hour == 19

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_tracker_free_runs_without_anchor(self, coordinator, monkeypatch):
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        point_calls: list = []
        interval_calls: list = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: point_calls.append(when) or Mock(),
        )
        monkeypatch.setattr(
            scheduler_module,
            "async_track_time_interval",
            lambda hass, cb, delta: interval_calls.append(delta) or Mock(),
        )

        await mgr._setup_interval_tracker(self._sched())
        assert interval_calls == [datetime.timedelta(hours=12)] and not point_calls

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_upcoming_runs_anchored_vs_free(self, coordinator):
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        mgr._schedules = [
            self._sched(id="anchored", start_time="07:00"),
            self._sched(id="free"),
        ]
        runs = {r["schedule_id"]: r for r in await mgr.async_get_upcoming_runs()}
        assert runs["anchored"]["next_run_utc"] is not None
        assert runs["anchored"]["interval_hours"] == 12
        assert runs["free"]["next_run_utc"] is None
        assert runs["free"]["interval_hours"] == 12

    def test_validate_rejects_bad_start_time(self, coordinator):
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        with pytest.raises(ValueError, match="start time"):
            mgr._validate_schedule_data(self._sched(start_time="25:99"))
        # A valid anchor passes.
        mgr._validate_schedule_data(self._sched(start_time="07:00"))


class TestBucketResetAfterRun:
    @pytest.mark.asyncio
    async def test_commit_progress_writes_bucket_and_time(
        self, coordinator, mock_store
    ):
        mock_store.async_update_zone = AsyncMock()
        mock_store.get_zone = Mock(return_value={})
        # No forecast-weighting target on the zone → run may replenish to 0.
        assert coordinator._run_ceiling({const.ZONE_ID: 5}) == 0.0
        # A commit that delivered water writes the bucket, the usage total and
        # the irrigation time.
        await coordinator._commit_run_progress(
            5, new_bucket=0.0, volume_delta_l=5.0, dispatch=False
        )
        mock_store.async_update_zone.assert_awaited_once()
        zone_id_arg, changes = mock_store.async_update_zone.await_args[0]
        assert zone_id_arg == 5
        assert changes[const.ZONE_BUCKET] == 0.0
        assert const.ZONE_LAST_IRRIGATION in changes

    @pytest.mark.asyncio
    async def test_commit_progress_no_water_skips_irrigation_time(
        self, coordinator, mock_store
    ):
        """A commit that delivered no water (a failed run) must not stamp the
        last-irrigation time or the usage counter."""
        mock_store.async_update_zone = AsyncMock()
        mock_store.get_zone = Mock(return_value={})
        await coordinator._commit_run_progress(
            5, new_bucket=-3.0, volume_delta_l=0.0, dispatch=False
        )
        _, changes = mock_store.async_update_zone.await_args[0]
        assert changes[const.ZONE_BUCKET] == -3.0
        assert const.ZONE_LAST_IRRIGATION not in changes
        assert const.ZONE_WATER_USED_TOTAL not in changes
