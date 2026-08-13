"""Tests for the Start/Finish bound reshape (GitLab #27) + sequencing-aware
duration + bucket reset introduced for the irrigation-timer work."""

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
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
    }
    base.update(kw)
    return base


class TestBoundedEnds:
    """`_bounded_ends` resolves which end(s) of the window are bounded, and
    which one governs when both are."""

    def test_only_finish_bounded_is_governing(self):
        governing, paired = RecurringScheduleManager._bounded_ends(
            _sched(finish_mode=const.SCHEDULE_BOUND_MODE_TIME, finish_time="06:00")
        )
        assert governing == const.SCHEDULE_ANCHOR_FINISH
        assert paired is None

    def test_only_start_bounded_is_governing(self):
        governing, paired = RecurringScheduleManager._bounded_ends(
            _sched(start_mode=const.SCHEDULE_BOUND_MODE_TIME, start_time="06:00")
        )
        assert governing == const.SCHEDULE_ANCHOR_START
        assert paired is None

    def test_both_bounded_explicit_anchor_wins(self):
        governing, paired = RecurringScheduleManager._bounded_ends(
            _sched(
                start_mode=const.SCHEDULE_BOUND_MODE_SUNSET,
                finish_mode=const.SCHEDULE_BOUND_MODE_SUNRISE,
                anchor=const.SCHEDULE_ANCHOR_START,
            )
        )
        assert governing == const.SCHEDULE_ANCHOR_START
        assert paired == const.SCHEDULE_ANCHOR_FINISH

    def test_both_bounded_default_anchor_is_finish(self):
        governing, paired = RecurringScheduleManager._bounded_ends(
            _sched(
                start_mode=const.SCHEDULE_BOUND_MODE_SUNSET,
                finish_mode=const.SCHEDULE_BOUND_MODE_SUNRISE,
            )
        )
        assert governing == const.SCHEDULE_ANCHOR_FINISH
        assert paired == const.SCHEDULE_ANCHOR_START

    def test_neither_bounded_returns_none_none(self):
        assert RecurringScheduleManager._bounded_ends(_sched()) == (None, None)


class TestRecurrenceDayMatches:
    def test_daily_always(self):
        dt = datetime.datetime(2026, 6, 10)
        assert RecurringScheduleManager._recurrence_day_matches(
            _sched(recurrence=const.SCHEDULE_RECURRENCE_DAILY), dt
        )

    def test_weekly(self):
        dt = datetime.datetime(2026, 6, 10)
        today = WEEKDAYS[dt.weekday()]
        other = WEEKDAYS[(dt.weekday() + 1) % 7]
        assert RecurringScheduleManager._recurrence_day_matches(
            _sched(recurrence=const.SCHEDULE_RECURRENCE_WEEKLY, days_of_week=[today]),
            dt,
        )
        assert not RecurringScheduleManager._recurrence_day_matches(
            _sched(recurrence=const.SCHEDULE_RECURRENCE_WEEKLY, days_of_week=[other]),
            dt,
        )

    def test_monthly(self):
        dt = datetime.datetime(2026, 6, 10)
        assert RecurringScheduleManager._recurrence_day_matches(
            _sched(recurrence=const.SCHEDULE_RECURRENCE_MONTHLY, day_of_month=10), dt
        )
        assert not RecurringScheduleManager._recurrence_day_matches(
            _sched(recurrence=const.SCHEDULE_RECURRENCE_MONTHLY, day_of_month=11), dt
        )

    def test_weekly_with_a_sun_relative_bound_still_matches_by_day(self):
        """The gap GitLab #27 closes: recurrence and time-of-day are
        independent, so weekday filtering applies no matter which bound mode
        produced the candidate instant — a sun-relative Finish on a weekly
        recurrence is restricted to its chosen days exactly like a clock time
        would be."""
        dt = datetime.datetime(2026, 6, 10)  # a Wednesday
        today = WEEKDAYS[dt.weekday()]
        other = WEEKDAYS[(dt.weekday() + 1) % 7]
        sched = _sched(
            recurrence=const.SCHEDULE_RECURRENCE_WEEKLY,
            finish_mode=const.SCHEDULE_BOUND_MODE_SUNRISE,
            days_of_week=[today],
        )
        assert RecurringScheduleManager._recurrence_day_matches(sched, dt)
        sched[const.SCHEDULE_CONF_DAYS_OF_WEEK] = [other]
        assert not RecurringScheduleManager._recurrence_day_matches(sched, dt)


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
    # The buckets matter: the anchor estimate now prices only the zones the run
    # would actually water, so a zone whose bucket sits above its threshold
    # contributes nothing. Zone 4 is exactly that case.
    return [
        {
            const.ZONE_ID: 1,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_DURATION: 300,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_BUCKET_THRESHOLD: -1.0,
        },
        {
            const.ZONE_ID: 2,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_DURATION: 600,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_BUCKET_THRESHOLD: -1.0,
        },
        {
            const.ZONE_ID: 3,
            const.ZONE_STATE: const.ZONE_STATE_DISABLED,
            const.ZONE_DURATION: 999,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_BUCKET_THRESHOLD: -1.0,
        },
        {
            const.ZONE_ID: 4,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_DURATION: 450,
            const.ZONE_BUCKET: 0.0,
            const.ZONE_BUCKET_THRESHOLD: -1.0,
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
    async def test_rotating_without_absorption_sums(self, coordinator, mock_store):
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_ROTATING)
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration() == 900

    @pytest.mark.asyncio
    async def test_rotating_counts_the_absorption_pauses(self, coordinator, mock_store):
        # 300 s + 600 s of watering, but 5-minute slots with a 10-minute
        # absorption pause stretch it to 1500 s of wall clock. Anchoring on the
        # 900 s sum starts the run ten minutes late and the deadline then cuts
        # the pump mid-rotation.
        mock_store.config = Mock(
            zone_sequencing=const.CONF_ZONE_SEQUENCING_ROTATING,
            zone_sequencing_max_consecutive_duration=5,
            zone_sequencing_min_absorption_time=10,
        )
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration() == 1500

    @pytest.mark.asyncio
    async def test_a_satisfied_zone_is_not_priced(self, coordinator, mock_store):
        # Zone 4 has a duration but its bucket is above threshold, so the run
        # would skip it. Counting it would start the run 450 s too early.
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration([4]) == 0
        assert await coordinator.get_total_irrigation_duration() == 900

    @pytest.mark.asyncio
    async def test_target_zone_filter(self, coordinator, mock_store):
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(return_value=_zones())
        assert await coordinator.get_total_irrigation_duration([1]) == 300
        assert await coordinator.get_total_irrigation_duration([1, 2]) == 900


def _mode_zones(mode):
    """The same two 300s/600s zones, in one non-classic watering mode."""
    return [dict(z, **{const.ZONE_WATERING_MODE: mode}) for z in _zones()]


class TestTheEstimateFollowsHowEachModeIsActuallyDispatched:
    """zone_sequencing does not govern every mode, so one global reduction is wrong.

    `_dispatch_by_mode` starts three independent tracks and waits for none of
    them, so the cycle lasts as long as the LONGEST, and each track is reduced
    by how that mode is really dispatched — not by the setting alone.
    """

    @pytest.mark.asyncio
    async def test_self_closing_zones_are_concurrent_under_sequential(
        self, coordinator, mock_store
    ):
        """The defect: service zones were SUMMED under sequential.

        `_dispatch_by_mode` fires every service zone in one loop and the
        hardware owns each close, so nothing serialises them — they open
        together and the cycle is the longest of them, not their total. The
        over-estimate started a finish-anchored schedule 300 s too early here.
        """
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(
            return_value=_mode_zones(const.WATERING_MODE_SERVICE)
        )
        assert await coordinator.get_total_irrigation_duration() == 600

    @pytest.mark.asyncio
    async def test_self_closing_zones_are_concurrent_under_rotating(
        self, coordinator, mock_store
    ):
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_ROTATING)
        mock_store.async_get_zones = AsyncMock(
            return_value=_mode_zones(const.WATERING_MODE_SERVICE)
        )
        assert await coordinator.get_total_irrigation_duration() == 600

    @pytest.mark.asyncio
    async def test_self_closing_zones_are_concurrent_under_parallel(
        self, coordinator, mock_store
    ):
        """Guard, not a change: parallel already reduced with max."""
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL)
        mock_store.async_get_zones = AsyncMock(
            return_value=_mode_zones(const.WATERING_MODE_SERVICE)
        )
        assert await coordinator.get_total_irrigation_duration() == 600

    @pytest.mark.asyncio
    async def test_stations_are_summed_under_parallel(self, coordinator, mock_store):
        """Under parallel the controller owns the order, so assume serialised.

        Whether a station waits for the ones queued before it is a flag in the
        controller's own configuration that this integration cannot read, so
        both orderings are possible. Only the longer one is safe to anchor on:
        an under-estimate finishes the irrigation AFTER the requested time.
        """
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL)
        mock_store.async_get_zones = AsyncMock(
            return_value=_mode_zones(const.WATERING_MODE_OPENSPRINKLER)
        )
        assert await coordinator.get_total_irrigation_duration() == 900

    @pytest.mark.asyncio
    async def test_stations_are_summed_under_sequential(self, coordinator, mock_store):
        """Guard, not a change: Smart Irrigation chains stations itself here."""
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(
            return_value=_mode_zones(const.WATERING_MODE_OPENSPRINKLER)
        )
        assert await coordinator.get_total_irrigation_duration() == 900

    @pytest.mark.asyncio
    async def test_the_tracks_do_not_add_up(self, coordinator, mock_store):
        """Mixed install: the tracks overlap in time, so take the longest.

        Two classic zones chaining for 900 s alongside one 600 s service zone
        is a 900 s cycle, not a 1500 s one.
        """
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(
            return_value=_zones()
            + [
                {
                    const.ZONE_ID: 4,
                    const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
                    const.ZONE_DURATION: 600,
                    const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
                }
            ]
        )
        assert await coordinator.get_total_irrigation_duration() == 900

    @pytest.mark.asyncio
    async def test_a_service_zone_can_still_be_the_longest_track(
        self, coordinator, mock_store
    ):
        """Non-vacuity: the service track is not simply being dropped."""
        mock_store.config = Mock(zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
        mock_store.async_get_zones = AsyncMock(
            return_value=_zones()
            + [
                {
                    const.ZONE_ID: 4,
                    const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
                    const.ZONE_DURATION: 4000,
                    const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
                }
            ]
        )
        assert await coordinator.get_total_irrigation_duration() == 4000

    @pytest.mark.asyncio
    async def test_a_classic_only_install_is_unchanged(self, coordinator, mock_store):
        """The default, and every install predating the self-closing modes."""
        for sequencing, expected in (
            (const.CONF_ZONE_SEQUENCING_SEQUENTIAL, 900),
            (const.CONF_ZONE_SEQUENCING_ROTATING, 900),
            (const.CONF_ZONE_SEQUENCING_PARALLEL, 600),
        ):
            mock_store.config = Mock(zone_sequencing=sequencing)
            mock_store.async_get_zones = AsyncMock(return_value=_zones())
            assert await coordinator.get_total_irrigation_duration() == expected


class TestFinishTrackerAdvance:
    """The self-rescheduling finish tracker must advance past an occurrence it
    already fired, instead of re-deriving the same still-future target and
    busy-looping the "run ASAP" branch every ~2s for the whole start→finish
    window (which re-fired irrigation thousands of times and ballooned the
    water-usage total)."""

    @staticmethod
    def _finish_sched():
        return _sched(
            recurrence=const.SCHEDULE_RECURRENCE_DAILY,
            finish_mode=const.SCHEDULE_BOUND_MODE_TIME,
            finish_time="06:00",
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
        target1 = await mgr._next_governing_time(sched, const.SCHEDULE_ANCHOR_FINISH)
        target2 = await mgr._next_governing_time(
            sched, const.SCHEDULE_ANCHOR_FINISH, reference_utc=target1
        )
        assert target2 - target1 == datetime.timedelta(days=1)

        mgr._finish_last_target[sid] = target1.isoformat()
        await mgr._setup_finish_tracker(sched, fitted=False)
        assert captured[-1] == target2 - datetime.timedelta(seconds=7200)
        assert captured[-1] > dt_util.utcnow()  # future, not a busy-loop catch-up

        # Re-arming again at the same instant stays stable on that next
        # occurrence — it does not fall back into the now+2s catch-up loop (the
        # bug re-fired every ~2s here).
        await mgr._setup_finish_tracker(sched, fitted=False)
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
        sched[const.SCHEDULE_CONF_FINISH_TIME] = (
            f"{finish.hour:02d}:{finish.minute:02d}"
        )
        sid = sched[const.SCHEDULE_CONF_ID]

        captured: list = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: captured.append(when) or Mock(),
        )

        # Missed start → catch up ASAP (now + 2s), not skipped.
        await mgr._setup_finish_tracker(sched, fitted=False)
        assert captured[-1] == dt_util.utcnow() + datetime.timedelta(seconds=2)

        # After the catch-up fires, the re-arm advances to the next occurrence
        # instead of scheduling another ASAP catch-up (the busy loop).
        target = await mgr._next_governing_time(sched, const.SCHEDULE_ANCHOR_FINISH)
        mgr._finish_last_target[sid] = target.isoformat()
        await mgr._setup_finish_tracker(sched, fitted=False)
        assert captured[-1] > dt_util.utcnow() + datetime.timedelta(hours=1)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_rearm_advances_for_negative_offset_sunrise(
        self, coordinator, monkeypatch
    ):
        """Regression (live 2026-07-04): a SUNRISE/SUNSET finish schedule with a
        NEGATIVE offset must also advance past the fired occurrence. The offset is
        applied *after* get_astral_event_next, so re-deriving with
        reference_utc=target (which sits |offset| *before* the sun event) returned
        the same event -> the same target, defeating the guard and busy-looping the
        ~2s "run ASAP" branch for the whole |offset| window."""
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(return_value=300)
        sched = _sched(
            recurrence=const.SCHEDULE_RECURRENCE_DAILY,
            finish_mode=const.SCHEDULE_BOUND_MODE_SUNRISE,
            finish_offset=-30,
            action="irrigate",
            zones="all",
        )

        # The core regression: advancing past the fired occurrence must land on
        # the NEXT sunrise (~1 day later), never re-derive the same target.
        target1 = await mgr._next_governing_time(sched, const.SCHEDULE_ANCHOR_FINISH)
        target2 = await mgr._next_governing_time(
            sched, const.SCHEDULE_ANCHOR_FINISH, reference_utc=target1
        )
        assert target2 > target1
        assert (
            datetime.timedelta(hours=20)
            < target2 - target1
            < datetime.timedelta(hours=28)
        )

        # And the tracker, re-armed for the just-fired occurrence, must schedule a
        # future start (not the now+2s catch-up that busy-loops every ~2s).
        captured: list = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: captured.append(when) or Mock(),
        )
        mgr._finish_last_target[sched[const.SCHEDULE_CONF_ID]] = target1.isoformat()
        await mgr._setup_finish_tracker(sched, fitted=False)
        assert captured[-1] > dt_util.utcnow() + datetime.timedelta(hours=1)


class TestSolarScheduleMatrix:
    """Full matrix: the three solar bound modes x {zero, negative, positive}
    offset x {finish, start} anchor = 18 cases. Guards the negative-offset
    busy-loop regression (live 2026-07-04) across every combination and confirms
    each one advances past a fired occurrence and arms a single FUTURE run — no
    ~2s "run ASAP" catch-up loop.

    Anchor dispatch (scheduler.py):
      - finish (all three modes) -> _setup_finish_tracker (point-in-time,
        _next_governing_time + _finish_last_target guard);
      - start sunrise/sunset     -> async_track_sunrise/sunset (offset-based HA
        primitive, structurally loop-free);
      - start azimuth            -> the resolver-driven one-shot
        (_setup_resolved_one_shot, _next_governing_time-based, so the same fix
        protects it).
    """

    SOLAR_MODES = [
        const.SCHEDULE_BOUND_MODE_SUNRISE,
        const.SCHEDULE_BOUND_MODE_SUNSET,
        const.SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
    ]
    OFFSETS = [0, -30, 45]
    ANCHORS = [
        const.SCHEDULE_ANCHOR_FINISH,
        const.SCHEDULE_ANCHOR_START,
    ]

    @staticmethod
    def _solar_sched(mode, anchor, offset):
        end_prefix = "start" if anchor == const.SCHEDULE_ANCHOR_START else "finish"
        other_prefix = "finish" if end_prefix == "start" else "start"
        sched = _sched(
            recurrence=const.SCHEDULE_RECURRENCE_DAILY,
            action="irrigate",
            zones="all",
        )
        sched[f"{end_prefix}_mode"] = mode
        sched[f"{end_prefix}_offset"] = offset
        if mode == const.SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH:
            sched[f"{end_prefix}_azimuth"] = 90
        sched[f"{other_prefix}_mode"] = const.SCHEDULE_BOUND_MODE_NONE
        return sched

    @pytest.mark.parametrize("mode", SOLAR_MODES)
    @pytest.mark.parametrize("offset", OFFSETS)
    @pytest.mark.parametrize("anchor", ANCHORS)
    @pytest.mark.asyncio
    @freeze_time("2026-06-10 06:00:00")
    async def test_solar_matrix_no_busy_loop(
        self, coordinator, monkeypatch, mode, offset, anchor
    ):
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(return_value=300)
        sched = self._solar_sched(mode, anchor, offset)

        # (1) Advance invariant — the root of the busy-loop. Re-arming past the
        # occurrence just fired must land on the NEXT one (~1 day later), never
        # re-derive the same target. A negative offset defeated this before the
        # fix (target2 == target1 -> now+2s loop).
        t1 = await mgr._next_governing_time(sched, anchor)
        t2 = await mgr._next_governing_time(sched, anchor, reference_utc=t1)
        assert t2 > t1, f"{mode}/{offset}/{anchor}: no advance -> busy-loop"
        assert (
            datetime.timedelta(hours=20) < t2 - t1 < datetime.timedelta(hours=28)
        ), f"{mode}/{offset}/{anchor}: advance {t2 - t1} not ~1 day"

        # (2) The anchor's tracker is armed once, at a FUTURE time — never an
        # immediate/now+2s catch-up.
        point: list = []
        sunrise: list = []
        sunset: list = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: point.append(when) or Mock(),
        )
        monkeypatch.setattr(
            scheduler_module,
            "async_track_sunrise",
            lambda hass, cb, off: sunrise.append(off) or Mock(),
        )
        monkeypatch.setattr(
            scheduler_module,
            "async_track_sunset",
            lambda hass, cb, off: sunset.append(off) or Mock(),
        )
        await mgr._setup_schedule_tracker(sched)

        off_delta = datetime.timedelta(minutes=offset)
        if anchor == const.SCHEDULE_ANCHOR_FINISH:
            # All three solar modes finish via the point-in-time finish tracker.
            assert len(point) == 1 and not sunrise and not sunset
            assert point[0] > dt_util.utcnow()  # future start, not now+2s
        elif mode == const.SCHEDULE_BOUND_MODE_SUNRISE:
            assert sunrise == [off_delta] and not point and not sunset
        elif mode == const.SCHEDULE_BOUND_MODE_SUNSET:
            assert sunset == [off_delta] and not point and not sunrise
        else:  # solar azimuth, start anchor -> self-rescheduling point-in-time
            assert len(point) == 1 and not sunrise and not sunset
            assert point[0] > dt_util.utcnow()

    @pytest.mark.parametrize(
        "mode,track_name",
        [
            (const.SCHEDULE_BOUND_MODE_SUNRISE, "async_track_sunrise"),
            (const.SCHEDULE_BOUND_MODE_SUNSET, "async_track_sunset"),
        ],
    )
    @pytest.mark.asyncio
    async def test_start_solar_callback_fires_with_no_args(
        self, coordinator, monkeypatch, mode, track_name
    ):
        """Regression: HA invokes the sunrise/sunset callback with NO arguments
        (Callable[[], None] via async_run_hass_job), unlike the point-in-time /
        time-change trackers which pass `now`. A one-arg callback raised
        TypeError at fire time and the schedule silently never ran (issue #32,
        AlessandroTischer). Capture the callback HA would register and invoke it
        the way HA does — with zero args — then assert the schedule executes."""
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)

        captured: dict = {}
        monkeypatch.setattr(
            scheduler_module,
            track_name,
            lambda hass, cb, off: captured.setdefault("cb", cb) or Mock(),
        )
        executed: list = []
        monkeypatch.setattr(
            mgr, "_execute_schedule", lambda s, now: executed.append((s, now))
        )

        sched = _sched(
            recurrence=const.SCHEDULE_RECURRENCE_DAILY,
            start_mode=mode,
            start_offset=60,
            finish_mode=const.SCHEDULE_BOUND_MODE_NONE,
            action="irrigate",
            zones="all",
        )
        await mgr._setup_schedule_tracker(sched)

        # HA calls the job with no positional args — this must not raise.
        captured["cb"]()
        assert len(executed) == 1
        assert executed[0][0] is sched


class TestStartPinnedBothBounded:
    """Both ends bounded, anchor=start: a genuinely new combination no v13
    shape could ever express (only a Finish anchor could be fitted before
    GitLab #27), reached when the dialog's own anchor selector picks Start
    with both a Start and a Finish bound configured. Fires exactly at the
    Start bound (no decision-point wait, unlike the Finish-pinned arm) and
    passes the resolved Finish through as a hard deadline."""

    @staticmethod
    def _both_bounded_sched(**kw):
        base = _sched(
            recurrence=const.SCHEDULE_RECURRENCE_DAILY,
            start_mode=const.SCHEDULE_BOUND_MODE_TIME,
            start_time="22:00",
            finish_mode=const.SCHEDULE_BOUND_MODE_TIME,
            finish_time="06:00",
            anchor=const.SCHEDULE_ANCHOR_START,
            action="irrigate",
            zones="all",
        )
        base.update(kw)
        return base

    def test_bounded_ends_reports_start_governing_finish_paired(self):
        governing, paired = RecurringScheduleManager._bounded_ends(
            self._both_bounded_sched()
        )
        assert governing == const.SCHEDULE_ANCHOR_START
        assert paired == const.SCHEDULE_ANCHOR_FINISH

    @pytest.mark.asyncio
    async def test_setup_schedule_tracker_dispatches_to_start_pinned(
        self, coordinator, monkeypatch
    ):
        """End to end through the real dispatch, not just the bounded-ends
        helper: a both-bounded, anchor=start schedule must NOT go through the
        Finish two-stage arm (_setup_fitted_tracker/_decide_and_arm)."""
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        sched = self._both_bounded_sched()

        point_calls = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: point_calls.append(when) or Mock(),
        )
        fitted_called = []
        monkeypatch.setattr(
            mgr,
            "_setup_fitted_tracker",
            lambda *a, **kw: fitted_called.append(True),
        )

        await mgr._setup_schedule_tracker(sched)

        assert not fitted_called
        assert len(point_calls) == 1

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_fires_at_the_start_bound_not_target_minus_duration(
        self, coordinator, monkeypatch
    ):
        """Unlike the Finish-pinned arm, there is no decision point to wait
        for: the Start bound is a fixed, non-duration-dependent instant, so
        the tracker arms directly at it."""
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(return_value=7200)
        sched = self._both_bounded_sched()

        captured = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: captured.append(when) or Mock(),
        )

        await mgr._setup_start_pinned_tracker(sched)

        expected_start = await mgr._next_governing_time(
            self._both_bounded_sched(), const.SCHEDULE_ANCHOR_START
        )
        assert captured == [expected_start]

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_callback_passes_the_finish_bound_as_a_deadline_no_order(
        self, coordinator, monkeypatch
    ):
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        sched = self._both_bounded_sched()

        captured = {}

        def fake_track(hass, cb, when):
            captured["cb"] = cb
            captured["when"] = when
            return Mock()

        monkeypatch.setattr(
            scheduler_module, "async_track_point_in_utc_time", fake_track
        )
        monkeypatch.setattr(mgr, "_execute_schedule", Mock())
        # Stub _reregister_tracker with an AsyncMock (not a plain Mock) so
        # `self._reregister_tracker(s)` still returns a real, awaitable
        # coroutine — call_soon_threadsafe is NOT mocked here (unlike other
        # tests in this file that use a bare Mock coordinator): mgr.hass is
        # the real `hass` fixture's real event loop, and replacing its
        # call_soon_threadsafe breaks asyncio's own cross-thread executor
        # signaling, which manifests as a genuine ~300s stall at teardown
        # ("executor did not finish joining its threads"), not just a warning.
        monkeypatch.setattr(mgr, "_reregister_tracker", AsyncMock())

        await mgr._setup_start_pinned_tracker(sched)
        captured["cb"](captured["when"])

        kwargs = mgr._execute_schedule.call_args.kwargs
        assert kwargs["order"] is None
        assert kwargs["pre_committed"] is False
        # The deadline is the resolved Finish bound (06:00 local), strictly
        # after the Start bound (22:00 local the previous evening).
        assert kwargs["deadline"] is not None
        assert kwargs["deadline"] > captured["when"]

    @pytest.mark.asyncio
    @freeze_time("2026-06-20 20:00:00")
    async def test_rearm_advances_past_an_already_fired_occurrence(
        self, coordinator, monkeypatch
    ):
        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        sched = self._both_bounded_sched()
        sid = sched[const.SCHEDULE_CONF_ID]

        captured = []
        monkeypatch.setattr(
            scheduler_module,
            "async_track_point_in_utc_time",
            lambda hass, cb, when: captured.append(when) or Mock(),
        )

        target1 = await mgr._next_governing_time(sched, const.SCHEDULE_ANCHOR_START)
        mgr._finish_last_target[sid] = target1.isoformat()

        await mgr._setup_start_pinned_tracker(sched)

        assert captured[-1] > target1
        assert captured[-1] - target1 == datetime.timedelta(days=1)


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
            const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_INTERVAL,
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
        import homeassistant.util.dt as dt_util

        mgr = RecurringScheduleManager(coordinator.hass, coordinator)
        sched = self._sched(start_time="07:00")
        target1 = mgr._next_interval_target(sched, dt_util.utcnow())
        target2 = mgr._next_interval_target(sched, target1)
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
