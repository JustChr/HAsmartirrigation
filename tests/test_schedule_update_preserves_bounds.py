"""An update service call must not move a schedule it never mentioned.

`update_recurring_schedule` merges its payload into the stored schedule, and
`_validate_schedule_data` has always required `name` plus the recurrence — so
every legacy automation's update call carries `type`, and every one of them
therefore goes through `_translate_legacy_schedule_fields`. When that
translation materialised the 06:00 default unconditionally, the ordinary
"disable this schedule" call rewrote a 21:15 start time on its way through.

The other half is that validating the fragment cannot work: a payload of
{name, recurrence, enabled} carries no bound at all, and the shape rules
reject an unbounded schedule. So the update path validates the MERGED
schedule, which is what makes an omitted bound legal.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager
from custom_components.smart_irrigation.services import (
    _translate_legacy_schedule_fields,
)


def _stored(**extra):
    schedule = {
        const.SCHEDULE_CONF_ID: "s1",
        const.SCHEDULE_CONF_NAME: "Evening",
        const.SCHEDULE_CONF_ENABLED: True,
        const.SCHEDULE_CONF_RECURRENCE: "daily",
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_START_TIME: "21:15",
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_NONE,
    }
    schedule.update(extra)
    return schedule


def _manager(hass, stored):
    mgr = RecurringScheduleManager(hass, Mock())
    mgr._save_schedules = AsyncMock()
    mgr._remove_schedule_tracker = AsyncMock()
    mgr._setup_schedule_tracker = AsyncMock()
    mgr._schedules = [stored]
    return mgr


class TestTheUpdateServiceCall:
    """The legacy payload shape, translated on the update boundary."""

    def test_an_update_without_a_time_writes_no_bound(self):
        translated = _translate_legacy_schedule_fields(
            {"name": "Evening", "type": "daily", "enabled": False},
            materialize_time=False,
        )
        assert translated[const.SCHEDULE_CONF_RECURRENCE] == "daily"
        assert const.SCHEDULE_CONF_START_TIME not in translated
        assert const.SCHEDULE_CONF_START_MODE not in translated

    def test_an_update_carrying_a_time_still_sets_the_bound(self):
        # Passing `time` is how the legacy call moves a schedule, so that has
        # to keep working — this is not "the update path ignores time".
        translated = _translate_legacy_schedule_fields(
            {"name": "Evening", "type": "daily", "time": "05:30"},
            materialize_time=False,
        )
        assert translated[const.SCHEDULE_CONF_START_MODE] == (
            const.SCHEDULE_BOUND_MODE_TIME
        )
        assert translated[const.SCHEDULE_CONF_START_TIME] == "05:30"

    def test_creating_still_materialises_the_default(self):
        # The create path is unchanged: an omitted time still means 06:00.
        translated = _translate_legacy_schedule_fields(
            {"name": "Morning", "type": "daily"}
        )
        assert translated[const.SCHEDULE_CONF_START_TIME] == "06:00"

    @pytest.mark.asyncio
    async def test_disabling_a_schedule_leaves_its_start_time_alone(self, hass):
        """The defect itself, end to end through the manager."""
        stored = _stored()
        mgr = _manager(hass, stored)
        payload = _translate_legacy_schedule_fields(
            {"name": "Evening", "type": "daily", "enabled": False},
            materialize_time=False,
        )
        await mgr.async_update_schedule("s1", payload)
        assert mgr._schedules[0][const.SCHEDULE_CONF_START_TIME] == "21:15"
        assert mgr._schedules[0][const.SCHEDULE_CONF_ENABLED] is False

    @pytest.mark.asyncio
    async def test_an_update_carrying_a_time_moves_the_schedule(self, hass):
        mgr = _manager(hass, _stored())
        payload = _translate_legacy_schedule_fields(
            {"name": "Evening", "type": "daily", "time": "05:30"},
            materialize_time=False,
        )
        await mgr.async_update_schedule("s1", payload)
        assert mgr._schedules[0][const.SCHEDULE_CONF_START_TIME] == "05:30"


class TestValidationOnTheMergedSchedule:
    def test_a_partial_payload_cannot_validate_on_its_own(self, hass):
        """Why the merge is required rather than merely tidier.

        This is the shape an update payload has once the translation stops
        inventing a bound, and in isolation it describes no time whatsoever.
        """
        mgr = RecurringScheduleManager(hass, Mock())
        with pytest.raises(ValueError, match="Start or a Finish bound"):
            mgr._validate_schedule_data(
                {
                    const.SCHEDULE_CONF_NAME: "Evening",
                    const.SCHEDULE_CONF_RECURRENCE: "daily",
                    const.SCHEDULE_CONF_ENABLED: False,
                }
            )

    @pytest.mark.asyncio
    async def test_the_merged_schedule_is_what_gets_validated(self, hass):
        mgr = _manager(hass, _stored())
        mgr._validate_schedule_data = Mock()
        await mgr.async_update_schedule(
            "s1",
            {
                const.SCHEDULE_CONF_NAME: "Evening",
                const.SCHEDULE_CONF_RECURRENCE: "daily",
                const.SCHEDULE_CONF_ENABLED: False,
            },
        )
        validated = mgr._validate_schedule_data.call_args.args[0]
        assert validated[const.SCHEDULE_CONF_START_TIME] == "21:15"
        assert validated[const.SCHEDULE_CONF_ENABLED] is False

    @pytest.mark.asyncio
    async def test_an_update_that_breaks_the_shape_is_still_refused(self, hass):
        """The merge must not become a way to smuggle a bad value past the
        validator — the stored schedule supplies the missing keys, not an
        excuse for the ones that are present."""
        mgr = _manager(hass, _stored())
        with pytest.raises(ValueError, match="Invalid start time format"):
            await mgr.async_update_schedule(
                "s1", {const.SCHEDULE_CONF_START_TIME: "4:5pm"}
            )
        assert mgr._schedules[0][const.SCHEDULE_CONF_START_TIME] == "21:15"
