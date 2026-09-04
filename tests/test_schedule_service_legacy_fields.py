"""The create/update-schedule services still publish `type` and `time`.

`services.yaml` has always exposed those two names, and v14 storage has
neither, so the service boundary translates. What makes this worth its own
file is that `time` is published as `required: false`: on the old shape an
omitted `time` still fired at 06:00, supplied by the resolver's own
`schedule.get(time, "06:00")` default rather than by anything stored.

v14's resolver has no such default, so the value that default produced has to
be written out at every path a schedule can be created through. There are
three of them, and each carries the same 06:00: the storage migration, the
panel dialog's `toStored`, and this one. A schedule that reaches storage with
a Start bound in `time` mode and no time is not a bound at all, and the
schedule silently never fires.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.scheduler import RecurringScheduleManager
from custom_components.irrigation_plus.services import (
    _translate_legacy_schedule_fields,
)

# Matches tests/test_schedule_migration_v14.py: the harness runs on US/Pacific,
# so 06:00 local is 13:00Z on this date.
_FROZEN = "2026-06-10 12:00:00"
_SIX_AM_UTC = "2026-06-10T13:00:00+00:00"


def _documented_call(**extra):
    """The service call as `services.yaml` documents it, `time` omitted.

    `time` is `required: false` there, so this is a valid call against the
    published contract and not a degenerate one.
    """
    data = {"name": "Morning", "type": "daily", "zones": "all"}
    data.update(extra)
    return data


class TestTheOptionalTimeStillMeansOhSixHundred:
    def test_a_call_without_a_time_is_given_one(self):
        translated = _translate_legacy_schedule_fields(_documented_call())
        assert translated[const.SCHEDULE_CONF_RECURRENCE] == "daily"
        assert (
            translated[const.SCHEDULE_CONF_START_MODE] == const.SCHEDULE_BOUND_MODE_TIME
        )
        assert translated[const.SCHEDULE_CONF_START_TIME] == "06:00"

    def test_a_call_with_a_time_keeps_it(self):
        translated = _translate_legacy_schedule_fields(_documented_call(time="21:15"))
        assert translated[const.SCHEDULE_CONF_START_TIME] == "21:15"

    def test_the_translated_call_passes_validation(self, hass):
        """The regression itself. A Start bound in `time` mode with no time
        raised `Invalid start time: None` and the documented call failed
        outright, where before v14 it succeeded."""
        mgr = RecurringScheduleManager(hass, Mock())
        mgr._validate_schedule_data(
            _translate_legacy_schedule_fields(_documented_call())
        )

    @pytest.mark.asyncio
    @freeze_time(_FROZEN)
    async def test_the_translated_call_resolves_to_0600(self, hass):
        """Composed end to end: the published call shape resolves to the same
        instant it fired at before the reshape."""
        mgr = RecurringScheduleManager(hass, Mock())
        mgr.coordinator.get_total_irrigation_duration = AsyncMock(return_value=0)
        schedule = _translate_legacy_schedule_fields(_documented_call())
        schedule[const.SCHEDULE_CONF_ID] = "s1"
        schedule[const.SCHEDULE_CONF_ENABLED] = True
        mgr._schedules = [schedule]

        runs = await mgr.async_get_upcoming_runs()
        assert runs[0]["next_run_utc"] == _SIX_AM_UTC


class TestTheRestOfTheContract:
    def test_an_interval_call_gets_no_window_bound(self):
        """An interval has no time of day, so it must not pick up a Start
        bound on the way through."""
        translated = _translate_legacy_schedule_fields(
            {"name": "Every 6h", "type": "interval", "interval_hours": 6}
        )
        assert translated[const.SCHEDULE_CONF_RECURRENCE] == "interval"
        assert const.SCHEDULE_CONF_START_MODE not in translated

    def test_a_call_already_in_the_new_shape_is_left_alone(self):
        """Only `type` triggers the translation, so a caller sending v14
        fields directly passes through untouched."""
        native = {
            "name": "Native",
            const.SCHEDULE_CONF_RECURRENCE: "daily",
            const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_SUNRISE,
            const.SCHEDULE_CONF_FINISH_OFFSET: -30,
        }
        assert _translate_legacy_schedule_fields(dict(native)) == native

    def test_the_caller_s_dict_is_not_mutated(self):
        """The handlers pass `dict(call.data)`, but a translation that edited
        in place would still be surprising to anything reusing the payload."""
        original = _documented_call()
        snapshot = dict(original)
        _translate_legacy_schedule_fields(original)
        assert original == snapshot

    @pytest.mark.parametrize("recurrence", ["daily", "weekly", "monthly"])
    def test_every_clock_type_the_service_publishes_translates(self, recurrence):
        """`services.yaml`'s `type` selector offers exactly these plus
        interval, so this is the whole surface that can carry a retired name.
        """
        translated = _translate_legacy_schedule_fields(
            _documented_call(type=recurrence)
        )
        assert translated[const.SCHEDULE_CONF_RECURRENCE] == recurrence
        assert translated[const.SCHEDULE_CONF_START_TIME] == "06:00"
        assert "type" not in translated
        assert "time" not in translated


def test_the_three_write_paths_agree_on_the_default():
    """The service boundary, the storage migration and the panel dialog are
    the three ways a schedule is created, and all three have to supply the
    same value for an omitted time. Two of them already did; this is the one
    that did not, so pin them together rather than in isolation.
    """
    from custom_components.irrigation_plus.store import _migrate_schedule_to_v14

    from_service = _translate_legacy_schedule_fields(_documented_call())
    from_migration = _migrate_schedule_to_v14(
        {"id": "s1", "name": "Morning", "type": "daily"}
    )
    assert (
        from_service[const.SCHEDULE_CONF_START_TIME]
        == from_migration[const.SCHEDULE_CONF_START_TIME]
        == "06:00"
    )
    # The panel's toStored is TypeScript; its half is asserted in
    # frontend/src/common/schedule-shape.test.ts, which pins the same literal.
