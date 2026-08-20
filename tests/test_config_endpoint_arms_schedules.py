"""A schedule written through the config endpoint must arm, and be visible.

``recurring_schedules`` reaches the config document from more than one writer.
The panel is not one of them: ``saveSchedule`` calls ``schedule_save``, which
routes to ``async_create_schedule`` / ``async_update_schedule``, and both
register their own tracker. But the REST and websocket config endpoints write
the key straight to the store, and the manager was never told. The write was
accepted, the stored document was correct, and yet no tracker existed so the
schedule never fired, while ``get_schedules()`` -- which backs the
``smart_irrigation/schedules`` command -- did not list it either. Silent in both
directions until a config entry reload rebuilt the manager.

The two halves failed independently, so every test here asserts both.

The negative matters as much as the positive: ``_config_updated`` fires on every
calculate, so a rebuild that does not diff first would re-arm every tracker on
that cadence, and re-arming a finish tracker is the operation that can re-fire an
occurrence.
"""

from unittest.mock import AsyncMock, Mock

import attr
import pytest
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager
from custom_components.smart_irrigation.store import Config


def _sched(sid="s1", name="cfg probe", time="22:00"):
    """A start-anchored daily schedule: a plain time-change tracker.

    Deliberately not finish-anchored, so that the tracker identity assertions
    below cannot be satisfied by ``async_rearm_finish_schedules`` skipping it for
    some reason other than the diff.
    """
    return {
        const.SCHEDULE_CONF_ID: sid,
        const.SCHEDULE_CONF_NAME: name,
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_START_TIME: time,
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_NONE,
        const.SCHEDULE_CONF_ACTION: "irrigate",
        const.SCHEDULE_CONF_ZONES: "all",
        const.SCHEDULE_CONF_ENABLED: True,
    }


class _ConfigDocument:
    """The half of the store these paths depend on.

    ``async_update_config`` evolves the in-memory ``Config`` and only schedules
    the save, and ``async_get_config`` returns ``attr.asdict`` of it -- a deep
    copy, which is why comparing the stored list against the manager's own is a
    real comparison rather than an object identity that can never differ.
    """

    def __init__(self, schedules):
        self.config = Config(recurring_schedules=schedules)

    async def async_get_config(self):
        return attr.asdict(self.config)

    async def async_update_config(self, changes: dict):
        valid = set(attr.fields_dict(Config).keys())
        self.config = attr.evolve(
            self.config, **{k: v for k, v in changes.items() if k in valid}
        )
        return attr.asdict(self.config)


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
    coord.get_total_irrigation_duration = AsyncMock(return_value=7200)
    return coord


@pytest.fixture
async def armed(hass, coordinator):
    """A manager loaded against an empty schedule list, subscribed and live."""
    coordinator.store = _ConfigDocument([])
    mgr = RecurringScheduleManager(hass, coordinator)
    coordinator.recurring_schedule_manager = mgr
    await mgr.async_load_schedules()
    yield mgr
    await mgr.async_unload()


class TestAConfigEndpointWriteArms:
    @pytest.mark.asyncio
    async def test_write_through_the_config_path_both_arms_and_appears(
        self, hass, coordinator, armed
    ):
        """The reproduction from the report.

        ``coordinator.async_update_config`` is the shared handler behind both
        the REST view and the websocket config command, so this is the endpoint's
        own path, not a shortcut to the store.
        """
        await coordinator.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched()]}
        )
        await hass.async_block_till_done()

        # Half one: the panel and the schedules command can see it.
        assert [s[const.SCHEDULE_CONF_NAME] for s in armed.get_schedules()] == [
            "cfg probe"
        ]
        # Half two: something will actually fire it. Asserting only the first
        # would pass against a fix that never arms anything.
        assert armed._schedule_trackers.get("s1") is not None

    @pytest.mark.asyncio
    async def test_a_schedule_removed_through_the_config_path_is_disarmed(
        self, hass, coordinator, armed
    ):
        """The same divergence in the other direction: a tracker left armed for
        a schedule the stored document no longer has would keep watering."""
        await coordinator.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched()]}
        )
        await hass.async_block_till_done()
        assert "s1" in armed._schedule_trackers

        await coordinator.async_update_config({const.CONF_RECURRING_SCHEDULES: []})
        await hass.async_block_till_done()

        assert armed.get_schedules() == []
        assert armed._schedule_trackers == {}

    @pytest.mark.asyncio
    async def test_the_next_irrigation_sensors_are_told(self, hass, coordinator, armed):
        """``_save_schedules`` sends this so the next-irrigation sensors
        recompute. A writer that bypassed the manager did not, which left those
        sensors reading against a schedule set they could not see."""
        seen = Mock()
        unsub = async_dispatcher_connect(
            hass, const.DOMAIN + "_schedules_updated", seen
        )
        try:
            await coordinator.async_update_config(
                {const.CONF_RECURRING_SCHEDULES: [_sched()]}
            )
            await hass.async_block_till_done()
        finally:
            unsub()

        assert seen.called


class TestAnUnrelatedWriteRebuildsNothing:
    """The property the diff exists to preserve, and the one a later refactor is
    most likely to drop."""

    @pytest.mark.asyncio
    async def test_unrelated_config_write_leaves_the_trackers_alone(
        self, hass, coordinator, armed
    ):
        await coordinator.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched()]}
        )
        await hass.async_block_till_done()
        before = armed._schedule_trackers["s1"]

        # A calculate dispatches this signal with no schedule change at all.
        await coordinator.async_update_config(
            {const.CONF_DAYS_SINCE_LAST_IRRIGATION: 1}
        )
        await hass.async_block_till_done()

        # Identity, not equality: a rebuild would produce a new unsub callable
        # for an unchanged schedule.
        assert armed._schedule_trackers["s1"] is before

    @pytest.mark.asyncio
    async def test_rewriting_the_same_schedules_is_not_a_change(
        self, hass, coordinator, armed
    ):
        """A caller that replays the whole configuration document unchanged --
        provisioning and restore tooling does exactly this -- must not tear down
        and re-arm every tracker for it."""
        await coordinator.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched()]}
        )
        await hass.async_block_till_done()
        before = armed._schedule_trackers["s1"]

        await coordinator.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched()]}
        )
        await hass.async_block_till_done()

        assert armed._schedule_trackers["s1"] is before


class TestTheAzimuthRewriteIsNotObserved:
    @pytest.mark.asyncio
    async def test_a_direct_store_write_does_not_reach_the_hook(
        self, hass, coordinator, armed
    ):
        """``async_correct_solar_azimuth_bearings`` rewrites the stored schedule
        list wholesale through ``store.async_update_config``.

        It is safe today because it is ordered before ``async_load_schedules`` in
        ``async_setup_entry``, so the manager loads the already-corrected list --
        but that ordering is invisible from where this hook sits, so pin the
        structural reason instead: the store's own update does not dispatch
        ``_config_updated``, so no write on that path can be observed here at
        all, whatever the ordering.
        """
        await coordinator.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched()]}
        )
        await hass.async_block_till_done()
        before = armed._schedule_trackers["s1"]

        await coordinator.store.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched(name="azimuth corrected")]}
        )
        await hass.async_block_till_done()

        assert armed._schedule_trackers["s1"] is before
        assert [s[const.SCHEDULE_CONF_NAME] for s in armed.get_schedules()] == [
            "cfg probe"
        ]
