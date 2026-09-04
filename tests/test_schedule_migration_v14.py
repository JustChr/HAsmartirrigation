"""v13 -> v14: the old `type` field conflated recurrence with time-of-day and
could only bound whichever end `time_anchor` pointed at. v14 replaces it with
an independent `recurrence` and two first-class Start/Finish bounds. This is
a destructive migration — retired keys must be gone afterward — so every shape
the old fields could express is exercised here.
"""

import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus.scheduler import RecurringScheduleManager
from custom_components.irrigation_plus.store import (
    STORAGE_VERSION,
    MigratableStore,
    _migrate_schedule_to_v14,
)

RETIRED_KEYS = {
    "type",
    "time",
    "offset_minutes",
    "account_for_duration",
    "azimuth_angle",
    "time_anchor",
}


def _assert_no_retired_keys(schedule: dict) -> None:
    leaked = RETIRED_KEYS & schedule.keys()
    assert not leaked, f"retired keys survived migration: {leaked}"


class TestDailyWeeklyMonthlyClockTypes:
    """Plain clock-time schedules: `type` splits into recurrence + a bound."""

    @pytest.mark.parametrize("old_type", ["daily", "weekly", "monthly"])
    def test_default_anchor_becomes_a_bounded_start(self, old_type):
        old = {
            "id": "s1",
            "name": "Morning",
            "type": old_type,
            "time": "06:00",
            "enabled": True,
            "action": "irrigate",
            "zones": "all",
        }
        new = _migrate_schedule_to_v14(old)

        assert new["recurrence"] == old_type
        assert new["start_mode"] == "time"
        assert new["start_time"] == "06:00"
        assert new["finish_mode"] == "none"
        assert new["anchor"] == "start"
        _assert_no_retired_keys(new)

    @pytest.mark.parametrize("old_type", ["daily", "weekly", "monthly"])
    def test_explicit_finish_anchor_becomes_a_bounded_finish(self, old_type):
        old = {
            "id": "s1",
            "name": "Evening",
            "type": old_type,
            "time": "20:00",
            "time_anchor": "finish",
            "enabled": True,
            "action": "irrigate",
            "zones": "all",
        }
        new = _migrate_schedule_to_v14(old)

        assert new["recurrence"] == old_type
        assert new["finish_mode"] == "time"
        assert new["finish_time"] == "20:00"
        assert new["start_mode"] == "none"
        assert new["anchor"] == "finish"
        _assert_no_retired_keys(new)

    def test_explicit_start_anchor_is_preserved(self):
        old = {
            "id": "s1",
            "name": "Explicit",
            "type": "weekly",
            "time": "07:30",
            "time_anchor": "start",
            "days_of_week": ["monday"],
        }
        new = _migrate_schedule_to_v14(old)

        assert new["start_mode"] == "time"
        assert new["start_time"] == "07:30"
        assert new["anchor"] == "start"
        assert new["days_of_week"] == ["monday"]  # untouched, non-retired field

    def test_weekly_day_of_week_field_survives_untouched(self):
        old = {
            "id": "s1",
            "name": "W",
            "type": "weekly",
            "time": "06:00",
            "days_of_week": ["tuesday", "thursday"],
        }
        new = _migrate_schedule_to_v14(old)
        assert new["days_of_week"] == ["tuesday", "thursday"]

    def test_monthly_day_of_month_field_survives_untouched(self):
        old = {
            "id": "s1",
            "name": "M",
            "type": "monthly",
            "time": "06:00",
            "day_of_month": 15,
        }
        new = _migrate_schedule_to_v14(old)
        assert new["day_of_month"] == 15

    @pytest.mark.parametrize("old_type", ["daily", "weekly", "monthly"])
    def test_missing_time_materialises_the_old_implicit_default(self, old_type):
        """`time` was optional and the v13 resolver read it as `get(time,
        "06:00")`, so a schedule stored without one fires at 06:00. The v14
        resolver has no such default and would treat the missing time as an
        unresolvable bound, stopping the schedule from ever firing, so the
        migration writes the value the old default produced."""
        old = {"id": "s1", "name": "NoTime", "type": old_type}
        new = _migrate_schedule_to_v14(old)
        assert new["start_mode"] == "time"
        assert new["start_time"] == "06:00"
        _assert_no_retired_keys(new)


class TestSolarReferenceTypes:
    """sunrise / sunset / solar_azimuth: always recurrence=daily, plus a bound."""

    @pytest.mark.parametrize("old_type", ["sunrise", "sunset", "solar_azimuth"])
    def test_becomes_daily_recurrence(self, old_type):
        old = {"id": "s1", "name": "Sun", "type": old_type}
        new = _migrate_schedule_to_v14(old)
        assert new["recurrence"] == "daily"

    @pytest.mark.parametrize("old_type", ["sunrise", "sunset"])
    def test_start_anchor_and_offset_becomes_bounded_start(self, old_type):
        old = {
            "id": "s1",
            "name": "Sun",
            "type": old_type,
            "time_anchor": "start",
            "offset_minutes": -15,
        }
        new = _migrate_schedule_to_v14(old)

        assert new["start_mode"] == old_type
        assert new["start_offset"] == -15
        assert new["finish_mode"] == "none"
        assert new["anchor"] == "start"
        _assert_no_retired_keys(new)

    @pytest.mark.parametrize("old_type", ["sunrise", "sunset"])
    def test_finish_anchor_and_offset_becomes_bounded_finish(self, old_type):
        old = {
            "id": "s1",
            "name": "Sun",
            "type": old_type,
            "time_anchor": "finish",
            "offset_minutes": 30,
        }
        new = _migrate_schedule_to_v14(old)

        assert new["finish_mode"] == old_type
        assert new["finish_offset"] == 30
        assert new["start_mode"] == "none"
        assert new["anchor"] == "finish"
        _assert_no_retired_keys(new)

    @pytest.mark.parametrize(
        "account_for_duration,expected_anchor",
        [
            (True, "finish"),
            (False, "start"),
            (None, "finish"),  # unset defaults True per the legacy fallback
        ],
    )
    def test_legacy_account_for_duration_flag_sets_the_anchor(
        self, account_for_duration, expected_anchor
    ):
        old = {"id": "s1", "name": "Sun", "type": "sunset"}
        if account_for_duration is not None:
            old["account_for_duration"] = account_for_duration
        new = _migrate_schedule_to_v14(old)

        assert new["anchor"] == expected_anchor
        bound_prefix = expected_anchor
        assert new[f"{bound_prefix}_mode"] == "sunset"
        _assert_no_retired_keys(new)

    def test_explicit_time_anchor_overrides_the_legacy_flag(self):
        """time_anchor supersedes account_for_duration when both are present."""
        old = {
            "id": "s1",
            "name": "Sun",
            "type": "sunrise",
            "time_anchor": "start",
            "account_for_duration": True,  # would say "finish" alone
        }
        new = _migrate_schedule_to_v14(old)
        assert new["anchor"] == "start"

    @pytest.mark.parametrize("offset", [15, -15, None])
    def test_offset_positive_negative_or_absent(self, offset):
        old = {"id": "s1", "name": "Sun", "type": "sunset", "time_anchor": "start"}
        if offset is not None:
            old["offset_minutes"] = offset
        new = _migrate_schedule_to_v14(old)

        if offset is None:
            assert "start_offset" not in new
        else:
            assert new["start_offset"] == offset

    @pytest.mark.parametrize("angle", [90, 45.5, None])
    def test_azimuth_with_and_without_explicit_angle(self, angle):
        old = {
            "id": "s1",
            "name": "Az",
            "type": "solar_azimuth",
            "time_anchor": "finish",
        }
        if angle is not None:
            old["azimuth_angle"] = angle
        new = _migrate_schedule_to_v14(old)

        assert new["finish_mode"] == "solar_azimuth"
        if angle is None:
            assert "finish_azimuth" not in new
        else:
            assert new["finish_azimuth"] == angle
        _assert_no_retired_keys(new)

    def test_azimuth_offset_and_angle_both_carry_over(self):
        """offset_minutes still applies to azimuth targets, alongside the angle."""
        old = {
            "id": "s1",
            "name": "Az",
            "type": "solar_azimuth",
            "time_anchor": "start",
            "azimuth_angle": 120,
            "offset_minutes": -10,
        }
        new = _migrate_schedule_to_v14(old)

        assert new["start_azimuth"] == 120
        assert new["start_offset"] == -10

    def test_non_azimuth_solar_type_never_gets_an_azimuth_field(self):
        old = {"id": "s1", "name": "Rise", "type": "sunrise", "azimuth_angle": 90}
        new = _migrate_schedule_to_v14(old)
        assert "start_azimuth" not in new
        assert "finish_azimuth" not in new


class TestIntervalSchedules:
    """Interval has no time of day and therefore no window: no start/finish."""

    def test_becomes_interval_recurrence_with_no_bounds(self):
        old = {
            "id": "s1",
            "name": "Every 6h",
            "type": "interval",
            "interval_hours": 6,
        }
        new = _migrate_schedule_to_v14(old)

        assert new["recurrence"] == "interval"
        assert "start_mode" not in new
        assert "finish_mode" not in new
        assert "anchor" not in new
        _assert_no_retired_keys(new)

    def test_own_start_time_anchor_is_untouched(self):
        """Interval's own optional clock anchor keeps the `start_time` key,
        distinct from (and never colliding with) start_mode='time' bounds,
        since an interval schedule never has a start_mode at all."""
        old = {
            "id": "s1",
            "name": "Anchored",
            "type": "interval",
            "interval_hours": 4,
            "start_time": "05:00",
        }
        new = _migrate_schedule_to_v14(old)

        assert new["recurrence"] == "interval"
        assert new["start_time"] == "05:00"
        assert "start_mode" not in new

    def test_interval_hours_survives_untouched(self):
        old = {"id": "s1", "name": "I", "type": "interval", "interval_hours": 8}
        new = _migrate_schedule_to_v14(old)
        assert new["interval_hours"] == 8

    def test_stray_solar_keys_on_an_interval_schedule_are_still_dropped(self):
        """Defensive: retired keys never survive, even on a shape they should
        never appear on."""
        old = {
            "id": "s1",
            "name": "I",
            "type": "interval",
            "interval_hours": 6,
            "offset_minutes": 10,
            "account_for_duration": True,
            "azimuth_angle": 90,
            "time_anchor": "finish",
        }
        new = _migrate_schedule_to_v14(old)
        _assert_no_retired_keys(new)


class TestSharedFieldsAreNeverTouched:
    """id/name/enabled/action/zones/dates are not part of the reshape."""

    def test_all_survive_a_migration_untouched(self):
        old = {
            "id": "abc123",
            "name": "Keep me",
            "type": "daily",
            "time": "06:00",
            "enabled": False,
            "action": "calculate",
            "zones": [1, 2, 3],
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        }
        new = _migrate_schedule_to_v14(old)
        for key in (
            "id",
            "name",
            "enabled",
            "action",
            "zones",
            "start_date",
            "end_date",
        ):
            assert new[key] == old[key]


class TestMissingOrMalformedType:
    def test_missing_type_entirely_leaves_recurrence_unset_not_crashed(self):
        old = {"id": "s1", "name": "Garbage"}
        new = _migrate_schedule_to_v14(old)
        assert "recurrence" not in new
        _assert_no_retired_keys(new)

    def test_unrecognized_type_leaves_recurrence_unset_not_crashed(self):
        old = {"id": "s1", "name": "Garbage", "type": "whenever"}
        new = _migrate_schedule_to_v14(old)
        assert "recurrence" not in new
        _assert_no_retired_keys(new)


class TestAnUnrecognizedTimeAnchor:
    """v13 read `time_anchor` through a membership test and fell back when it
    matched neither value, and nothing on the write side ever validated it:
    the panel sent it, the service schema did not expose it, and
    `_validate_schedule_data` did not check it. So a stored v13 schedule can
    carry any string there, and it fired perfectly well.

    The migration has to reproduce that tolerance, because the alternative is
    not an error. Taking the raw value as the bound prefix writes keys like
    `middle_mode`, leaves both real ends unbounded, and the schedule is then
    dropped at arm time with a warning nobody reads. That is the exact failure
    this reshape exists to prevent, arriving through the migration meant to
    prevent it.
    """

    @pytest.mark.parametrize("junk", ["middle", "", "START", 0, True, None])
    def test_a_clock_type_falls_back_to_a_bounded_start(self, junk):
        new = _migrate_schedule_to_v14(
            {
                "id": "s1",
                "name": "x",
                "type": "daily",
                "time": "06:00",
                "time_anchor": junk,
            }
        )
        assert new["start_mode"] == "time"
        assert new["start_time"] == "06:00"
        assert new["finish_mode"] == "none"
        assert new["anchor"] == "start"
        _assert_no_retired_keys(new)

    @pytest.mark.parametrize("junk", ["middle", "", "FINISH", 0, True, None])
    def test_a_solar_type_falls_back_to_the_legacy_flag(self, junk):
        """Not to start: on the solar types the fallback v13 applied was
        `account_for_duration`, which defaults to a finish anchor."""
        new = _migrate_schedule_to_v14(
            {"id": "s1", "name": "x", "type": "sunrise", "time_anchor": junk}
        )
        assert new["finish_mode"] == "sunrise"
        assert new["start_mode"] == "none"
        assert new["anchor"] == "finish"
        _assert_no_retired_keys(new)

    def test_a_solar_type_with_the_flag_off_falls_back_to_start(self):
        new = _migrate_schedule_to_v14(
            {
                "id": "s1",
                "name": "x",
                "type": "sunset",
                "time_anchor": "middle",
                "account_for_duration": False,
            }
        )
        assert new["start_mode"] == "sunset"
        assert new["finish_mode"] == "none"
        assert new["anchor"] == "start"

    @pytest.mark.parametrize("junk", ["middle", 0, None])
    def test_no_bound_key_is_named_after_the_junk_value(self, junk):
        """The property underneath all of the above, stated directly: only
        `start_` and `finish_` keys are ever written."""
        for old_type in ("daily", "sunrise", "solar_azimuth"):
            new = _migrate_schedule_to_v14(
                {
                    "id": "s1",
                    "name": "x",
                    "type": old_type,
                    "time": "06:00",
                    "time_anchor": junk,
                }
            )
            stray = [
                k
                for k in new
                if k.endswith(("_mode", "_time", "_offset", "_azimuth"))
                and not k.startswith(("start_", "finish_"))
            ]
            assert not stray, f"{old_type}: migration invented {stray}"


class TestFullMigrationPipeline:
    """Through `_async_migrate_func`, not just the pure per-schedule helper."""

    def _store(self, hass):
        return MigratableStore(hass, STORAGE_VERSION, "irrigation_plus.storage")

    async def test_every_schedule_in_the_collection_is_translated(self, hass):
        hass.config.units = METRIC_SYSTEM
        data = {
            "config": {
                "recurring_schedules": [
                    {"id": "a", "name": "A", "type": "daily", "time": "06:00"},
                    {"id": "b", "name": "B", "type": "interval", "interval_hours": 6},
                    {
                        "id": "c",
                        "name": "C",
                        "type": "sunrise",
                        "time_anchor": "finish",
                        "offset_minutes": 10,
                    },
                ]
            },
            "zones": [],
            "mappings": [],
            "modules": [],
        }

        migrated = await self._store(hass)._async_migrate_func(13, data)
        schedules = {s["id"]: s for s in migrated["config"]["recurring_schedules"]}

        assert schedules["a"]["recurrence"] == "daily"
        assert schedules["b"]["recurrence"] == "interval"
        assert schedules["c"]["finish_mode"] == "sunrise"
        for s in schedules.values():
            _assert_no_retired_keys(s)

    async def test_a_store_with_no_schedules_migrates_cleanly(self, hass):
        hass.config.units = METRIC_SYSTEM
        data = {"config": {}, "zones": [], "mappings": [], "modules": []}
        migrated = await self._store(hass)._async_migrate_func(13, data)
        assert migrated["config"].get("recurring_schedules", []) == []

    async def test_distributor_local_schedules_are_migrated_too(self, hass):
        """Vestigial today (nothing reads DistributorEntry.schedules), but the
        stored shape should stay consistent rather than leaking a v13 dict."""
        hass.config.units = METRIC_SYSTEM
        data = {
            "config": {},
            "zones": [],
            "mappings": [],
            "modules": [],
            "distributors": [
                {
                    "id": "dist1",
                    "schedules": [
                        {"id": "d1", "name": "D", "type": "daily", "time": "06:00"}
                    ],
                }
            ],
        }
        migrated = await self._store(hass)._async_migrate_func(13, data)
        dist_schedule = migrated["distributors"][0]["schedules"][0]
        assert dist_schedule["recurrence"] == "daily"
        _assert_no_retired_keys(dist_schedule)


# --- migration + resolver, composed -----------------------------------------

# Frozen so every expected instant below is a fixed number rather than a
# re-derivation of the code under test. The test harness's Home Assistant runs
# on US/Pacific at San Diego's coordinates, which is where the local-to-UTC
# offsets and the sun events come from.
_FROZEN = "2026-06-10 12:00:00"


def _v13(**kw):
    base = {
        "id": "s1",
        "name": "probe",
        "enabled": True,
        "action": "irrigate",
        "zones": "all",
    }
    base.update(kw)
    return base


class TestAMigratedScheduleStillFiresWhenItUsedTo:
    """The property an existing install actually cares about, which neither
    half of the suite covers on its own.

    The migration tests above assert the stored SHAPE is right. The resolver
    tests in test_schedule_time_anchor assert the tracker behaves correctly on
    hand-authored v14 shapes. Nothing else composes the two, so a migration
    that produced a well-formed schedule pointing at the wrong moment would
    pass both and still move every existing install's watering.

    Each case here starts from a v13 dict, runs the real migration, and
    resolves the result through the real tracker path
    (``async_get_upcoming_runs`` -> ``_governing_end`` -> ``_next_governing_time``
    -> ``_resolve_bound`` -> ``_resolve_event_instant``), then asserts the UTC
    instant v13 would have produced.

    Clock cases are asserted exactly. Sun-relative cases are asserted to within
    a minute, because their sub-second value comes from astral and would
    otherwise re-pin on an unrelated library upgrade. A minute is far tighter
    than any failure this guards against: a dropped offset moves the instant by
    30 minutes, a flipped anchor by the run duration, a lost recurrence by a
    day.
    """

    DURATION = 1800

    async def _resolve(self, hass, *v13_schedules):
        mgr = RecurringScheduleManager(hass, Mock())
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(
            return_value=self.DURATION
        )
        mgr._schedules = [_migrate_schedule_to_v14(s) for s in v13_schedules]
        return {r["schedule_id"]: r for r in await mgr.async_get_upcoming_runs()}

    @staticmethod
    def _close(iso, expected, tolerance_seconds=60):
        actual = datetime.datetime.fromisoformat(iso)
        want = datetime.datetime.fromisoformat(expected)
        assert (
            abs((actual - want).total_seconds()) < tolerance_seconds
        ), f"resolved {actual}, expected within {tolerance_seconds}s of {want}"

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_a_clock_start_fires_at_the_same_local_time(self, hass):
        runs = await self._resolve(
            hass, _v13(type="daily", time="06:00", time_anchor="start")
        )
        # 06:00 local, and the run begins there.
        assert runs["s1"]["anchor"] == "start"
        assert runs["s1"]["target_utc"] == "2026-06-10T13:00:00+00:00"
        assert runs["s1"]["next_run_utc"] == "2026-06-10T13:00:00+00:00"

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_a_clock_finish_still_starts_a_run_length_early(self, hass):
        runs = await self._resolve(
            hass, _v13(type="daily", time="05:30", time_anchor="finish")
        )
        # 05:30 local is the moment watering ENDS, so the run begins
        # DURATION earlier. An anchor lost in migration shows up here as
        # next_run == target.
        assert runs["s1"]["anchor"] == "finish"
        assert runs["s1"]["target_utc"] == "2026-06-10T12:30:00+00:00"
        assert runs["s1"]["next_run_utc"] == "2026-06-10T12:00:00+00:00"
        assert runs["s1"]["duration_seconds"] == self.DURATION

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_a_schedule_stored_without_a_time_still_fires_at_0600(self, hass):
        """The highest-value case here. `time` was optional and v13 supplied
        06:00 from the resolver; v14 has no such default, so if the migration
        stopped materialising it this schedule would silently never fire again
        rather than failing loudly."""
        runs = await self._resolve(hass, _v13(type="daily"))
        assert runs["s1"]["next_run_utc"] == "2026-06-10T13:00:00+00:00"

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_a_weekly_schedule_still_lands_on_its_own_weekday(self, hass):
        """Recurrence and time-of-day are separate fields now, so a lost
        recurrence would resolve this to tonight instead of Thursday."""
        runs = await self._resolve(
            hass,
            _v13(type="weekly", time="22:00", days_of_week=["thursday"]),
        )
        # 22:00 local on Thursday 2026-06-11.
        assert runs["s1"]["next_run_utc"] == "2026-06-12T05:00:00+00:00"

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_a_sunrise_schedule_keeps_its_implicit_finish_anchor(self, hass):
        """`account_for_duration` absent meant a finish anchor on the solar
        types, so this must still end at sunrise minus 30, not begin there."""
        runs = await self._resolve(hass, _v13(type="sunrise", offset_minutes=-30))
        assert runs["s1"]["anchor"] == "finish"
        self._close(runs["s1"]["target_utc"], "2026-06-10T12:10:20+00:00")
        self._close(runs["s1"]["next_run_utc"], "2026-06-10T11:40:20+00:00")

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_an_explicit_account_for_duration_false_still_means_start(self, hass):
        """The other half of the legacy fallback: explicitly False meant the
        run BEGINS at the event, so next_run must equal target."""
        runs = await self._resolve(
            hass,
            _v13(type="sunset", offset_minutes=15, account_for_duration=False),
        )
        assert runs["s1"]["anchor"] == "start"
        self._close(runs["s1"]["target_utc"], "2026-06-11T03:11:42+00:00")
        assert runs["s1"]["next_run_utc"] == runs["s1"]["target_utc"]

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_an_interval_schedule_keeps_its_anchored_phase(self, hass):
        """An interval's `start_time` is its own clock anchor, not a window
        bound, and the migration leaves it alone."""
        runs = await self._resolve(
            hass, _v13(type="interval", interval_hours=6, start_time="03:00")
        )
        assert runs["s1"]["recurrence"] == "interval"
        assert runs["s1"]["interval_hours"] == 6
        # 03:00 local phase-locked every 6h; the next occurrence after
        # 05:00 local is 09:00 local.
        assert runs["s1"]["next_run_utc"] == "2026-06-10T16:00:00+00:00"
