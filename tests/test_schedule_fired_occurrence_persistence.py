"""A fired occurrence must survive the manager that fired it.

A finish-anchored schedule fires at target - estimated_duration and records the
occurrence, so the re-arm advances to the next day instead of re-deriving the
same target. That record used to live only in
``RecurringScheduleManager._finish_last_target``. A config entry reload builds a
new coordinator and a new manager, so inside the start->finish window the fresh
manager resolved the same occurrence, found its start already past, took the
catch-up branch and watered a second time in full.

The tests below are written around the *restart* reason specifically: a test
that only checks the marker is written passes against the broken tree.
"""

import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation import scheduler as scheduler_module
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager
from custom_components.smart_irrigation.store import Config


def _finish_sched(sid="s1", time="06:00"):
    return {
        const.SCHEDULE_CONF_ID: sid,
        const.SCHEDULE_CONF_NAME: "restart probe",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_NONE,
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_FINISH_TIME: time,
        const.SCHEDULE_CONF_ANCHOR: const.SCHEDULE_ANCHOR_FINISH,
        const.SCHEDULE_CONF_ACTION: "irrigate",
        const.SCHEDULE_CONF_ZONES: "all",
        const.SCHEDULE_CONF_ENABLED: True,
    }


class _ConfigDocument:
    """The half of the store this fix depends on.

    Mirrors the real semantics that make the reload case work without a disk
    round-trip: ``async_update_config`` evolves the in-memory ``Config``
    immediately and only *schedules* the save, and the ``Store`` is cached for
    the lifetime of ``hass``, so a new manager reads back what the old one
    wrote even though nothing has been flushed.
    """

    def __init__(self, schedules):
        self.config = Config(recurring_schedules=schedules)

    async def async_get_config(self):
        import attr

        return attr.asdict(self.config)

    async def async_update_config(self, changes: dict):
        import attr

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


def _capture_arms(monkeypatch):
    """Record every (fire_time, callback) a tracker arms, arming nothing real."""
    arms: list = []
    monkeypatch.setattr(
        scheduler_module,
        "async_track_point_in_utc_time",
        lambda hass, cb, when: arms.append((when, cb)) or Mock(),
    )
    return arms


async def _fire(hass, mgr, arms, monkeypatch):
    """Invoke the armed callback the way HA would, without irrigating."""
    monkeypatch.setattr(mgr, "_execute_schedule", Mock())
    monkeypatch.setattr(mgr, "_reregister_tracker", AsyncMock())
    _when, cb = arms[-1]
    cb(scheduler_module.dt_util.utcnow())
    await hass.async_block_till_done()


class TestMarkerSurvivesANewManager:
    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_reload_inside_the_window_does_not_water_twice(
        self, hass, coordinator, monkeypatch
    ):
        """The reproduction from the report, as a test.

        Finish 30 min out with a 2h duration, so the ideal start is ~90 min in
        the past and a *fresh* manager takes the catch-up branch. Fire it, throw
        the manager away, build a new one against the same store: it must arm
        tomorrow's start, not another ASAP catch-up.
        """
        import homeassistant.util.dt as dt_util

        finish = dt_util.now() + datetime.timedelta(minutes=30)
        sched = _finish_sched(time=f"{finish.hour:02d}:{finish.minute:02d}")
        store = _ConfigDocument([sched])
        coordinator.store = store

        arms = _capture_arms(monkeypatch)

        mgr = RecurringScheduleManager(hass, coordinator)
        await mgr.async_load_schedules()
        # Precondition: this really is the catch-up branch, or the test proves
        # nothing about the branch the bug lived in.
        assert arms[-1][0] == dt_util.utcnow() + datetime.timedelta(seconds=2)

        await _fire(hass, mgr, arms, monkeypatch)
        await mgr.async_unload()

        fresh = RecurringScheduleManager(hass, coordinator)
        await fresh.async_load_schedules()

        armed = arms[-1][0]
        assert armed != dt_util.utcnow() + datetime.timedelta(seconds=2)
        # Tomorrow's occurrence, minus the 2h duration.
        assert armed > dt_util.utcnow() + datetime.timedelta(hours=12)

    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_dispatch_records_the_marker_in_the_config_document(
        self, hass, coordinator, monkeypatch
    ):
        sched = _finish_sched()
        store = _ConfigDocument([sched])
        coordinator.store = store

        arms = _capture_arms(monkeypatch)
        mgr = RecurringScheduleManager(hass, coordinator)
        await mgr.async_load_schedules()
        await _fire(hass, mgr, arms, monkeypatch)

        target = await mgr._next_governing_time(sched, const.SCHEDULE_ANCHOR_FINISH)
        assert store.config.fired_occurrences == {"s1": target.isoformat()}

    @pytest.mark.asyncio
    async def test_unload_does_not_clear_the_marker(self, hass, coordinator):
        """Teardown must leave the record alone.

        It is no longer per-manager memory a fresh manager re-derives, and a
        persistence task created just before teardown would otherwise write an
        emptied map back over it.
        """
        coordinator.store = _ConfigDocument([])
        mgr = RecurringScheduleManager(hass, coordinator)
        mgr._finish_last_target["s1"] = "2026-06-11T04:00:00+00:00"
        await mgr.async_unload()
        assert mgr._finish_last_target == {"s1": "2026-06-11T04:00:00+00:00"}


class TestPruning:
    @pytest.mark.asyncio
    @freeze_time("2026-06-10 18:00:00")
    async def test_a_recreated_id_still_fires_its_first_occurrence(
        self, hass, coordinator, monkeypatch
    ):
        """The direction where this fix could cost a watering rather than save
        one: a schedule deleted and recreated under the same id must not inherit
        the old one's "already fired" marker."""
        import homeassistant.util.dt as dt_util

        store = _ConfigDocument([])
        store.config = store.config.__class__(
            recurring_schedules=[],
            fired_occurrences={"s1": "2026-06-11T04:00:00+00:00"},
        )
        coordinator.store = store

        # Load with the id absent: the marker is pruned, in memory and on disk.
        mgr = RecurringScheduleManager(hass, coordinator)
        await mgr.async_load_schedules()
        assert mgr._finish_last_target == {}
        assert store.config.fired_occurrences == {}

        # Same id, new schedule: it arms its own next occurrence.
        finish = dt_util.now() + datetime.timedelta(minutes=30)
        sched = _finish_sched(time=f"{finish.hour:02d}:{finish.minute:02d}")
        store.config = store.config.__class__(
            recurring_schedules=[sched],
            fired_occurrences=store.config.fired_occurrences,
        )
        arms = _capture_arms(monkeypatch)
        fresh = RecurringScheduleManager(hass, coordinator)
        await fresh.async_load_schedules()
        assert arms, "recreated schedule armed nothing"


class TestStoreSchema:
    def test_config_has_fired_occurrences(self):
        assert Config().fired_occurrences == {}

    @pytest.mark.asyncio
    async def test_marker_round_trips_through_the_real_store(self, hass):
        """Not the mock: the migration filters ``data["config"]`` against
        ``attr.fields_dict(Config)``, so a key hydrated without an attribute is
        silently dropped on load."""
        from custom_components.smart_irrigation.store import async_get_registry

        reg = await async_get_registry(hass)
        await reg.async_update_config(
            {const.CONF_FIRED_OCCURRENCES: {"s1": "2026-06-11T04:00:00+00:00"}}
        )
        cfg = await reg.async_get_config()
        assert cfg[const.CONF_FIRED_OCCURRENCES] == {"s1": "2026-06-11T04:00:00+00:00"}
