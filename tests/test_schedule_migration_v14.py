"""v13 -> v14: the old `type` field conflated recurrence with time-of-day and
could only bound whichever end `time_anchor` pointed at. v14 replaces it with
an independent `recurrence` and two first-class Start/Finish bounds. This is
a destructive migration — retired keys must be gone afterward — so every shape
the old fields could express is exercised here.
"""

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation.store import (
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


class TestFullMigrationPipeline:
    """Through `_async_migrate_func`, not just the pure per-schedule helper."""

    def _store(self, hass):
        return MigratableStore(hass, STORAGE_VERSION, "smart_irrigation.storage")

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
