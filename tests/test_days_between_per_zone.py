"""The days-between-irrigation wait is counted per zone, not per install.

One global counter was reset by ANY watered run, so a run that reached only the
first few zones still told the guard that everything had watered. The next
night was then skipped whole, and the zones at the tail of the priority order
were never reached at all - each night's run resetting the counter on behalf of
zones it never opened a valve for. The counter has to live where the water
lands.

Two properties follow, and both are asserted against the real entry points
rather than against the helpers, because the helpers being right is not the
part that failed:

- a zone that has served its wait waters even while a zone watered more
  recently is still held, and
- a zone's counter is reset only by water actually credited to that zone.
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import homeassistant.util.dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import (
    SmartIrrigationCoordinator,
    const,
    skip_conditions,
)
from custom_components.smart_irrigation.store import (
    STORAGE_KEY,
    SmartIrrigationStorage,
)


class _FakeStore:
    def __init__(self, zones, config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.config = config

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zone_id, changes):
        self.zones[int(zone_id)].update(changes)
        return dict(self.zones[int(zone_id)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_get_distributors(self):
        return []

    async def async_get_config(self):
        return dict(self.config.__dict__)

    async def async_update_config(self, changes):
        for k, v in changes.items():
            setattr(self.config, k, v)


def _cfg(days_between=0, **over):
    base = dict(
        rain_delay_until=None,
        zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
        zone_sequencing_max_consecutive_duration=5,
        zone_sequencing_min_absorption_time=0,
        live_estimate_enabled=False,
        log_no_demand=False,
        days_between_irrigation=days_between,
        days_since_last_irrigation=0,
    )
    base.update(over)
    return SimpleNamespace(**base)


def _zone(zone_id, days_since=None):
    z = {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: f"Zone {zone_id}",
        const.ZONE_LINKED_ENTITY: f"switch.valve_{zone_id}",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 300,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_BUCKET_THRESHOLD: -1.0,
        const.ZONE_RUN_LOG: [],
    }
    if days_since is not None:
        z[const.ZONE_DAYS_SINCE_IRRIGATION] = days_since
    return z


def _coord(monkeypatch, zones, config):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    coord.hass = hass
    coord.store = _FakeStore(zones, config)
    return coord


def _capture(monkeypatch, coord):
    watered = []

    async def _fake(zones, *, trigger, **kw):
        watered.extend(int(z[const.ZONE_ID]) for z in zones)

    monkeypatch.setattr(coord, "_dispatch_by_mode", _fake)
    return watered


class TestTheGuardIsPerZone:
    """Driven through ``_irrigate_linked_entities``, the real dispatch entry."""

    async def test_a_zone_still_in_its_wait_is_held_and_the_others_water(
        self, monkeypatch
    ):
        """The whole point. Under the global counter this run watered either
        every zone or none of them."""
        zones = [_zone(1, days_since=0), _zone(2, days_since=3), _zone(3, days_since=5)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=3))
        watered = _capture(monkeypatch, coord)

        assert await coord._irrigate_linked_entities("all") is True
        assert watered == [2, 3]

    async def test_the_guard_is_off_by_default(self, monkeypatch):
        zones = [_zone(1, days_since=0), _zone(2, days_since=0)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=0))
        watered = _capture(monkeypatch, coord)

        assert await coord._irrigate_linked_entities("all") is True
        assert watered == [1, 2]

    async def test_a_run_with_every_zone_held_dispatches_nothing(self, monkeypatch):
        zones = [_zone(1, days_since=0), _zone(2, days_since=1)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=3))
        watered = _capture(monkeypatch, coord)

        assert await coord._irrigate_linked_entities("all") is False
        assert watered == []

    async def test_a_zone_with_no_counter_yet_is_not_held(self, monkeypatch):
        """Hydrated before the counter existed and not through a midnight
        since. Erring towards watering is the safe direction for a guard whose
        failure mode is stranding a dry zone."""
        coord = _coord(monkeypatch, [_zone(1)], _cfg(days_between=3))
        watered = _capture(monkeypatch, coord)

        assert await coord._irrigate_linked_entities("all") is True
        assert watered == [1]

    async def test_an_unreadable_setting_leaves_the_guard_off(self, monkeypatch):
        """Read off the runner's hot path: raising here would cancel the
        night's watering outright."""
        zones = [_zone(1, days_since=0)]
        coord = _coord(monkeypatch, zones, _cfg(days_between="not a number"))
        watered = _capture(monkeypatch, coord)

        assert await coord._irrigate_linked_entities("all") is True
        assert watered == [1]


class TestTheCounterFollowsTheWater:
    async def test_a_credited_zone_is_reset_and_its_neighbour_is_not(self, monkeypatch):
        zones = [_zone(1, days_since=4), _zone(2, days_since=4)]
        coord = _coord(monkeypatch, zones, _cfg())

        await coord.async_write_watered_bucket(1, -1.0)

        assert coord.store.zones[1][const.ZONE_DAYS_SINCE_IRRIGATION] == 0
        assert coord.store.zones[2][const.ZONE_DAYS_SINCE_IRRIGATION] == 4

    async def test_a_write_that_moved_no_water_does_not_reset_it(self, monkeypatch):
        zones = [_zone(1, days_since=4)]
        coord = _coord(monkeypatch, zones, _cfg())

        await coord.async_write_watered_bucket(1, -5.0)

        assert coord.store.zones[1][const.ZONE_DAYS_SINCE_IRRIGATION] == 4

    async def test_a_bucket_that_fell_does_not_reset_it(self, monkeypatch):
        """Only a credit is water. Drainage moves the bucket the other way."""
        zones = [_zone(1, days_since=4)]
        coord = _coord(monkeypatch, zones, _cfg())

        await coord.async_write_watered_bucket(1, -9.0)

        assert coord.store.zones[1][const.ZONE_DAYS_SINCE_IRRIGATION] == 4

    async def test_midnight_bumps_every_zone(self, monkeypatch):
        zones = [_zone(1, days_since=0), _zone(2, days_since=2), _zone(3)]
        coord = _coord(monkeypatch, zones, _cfg())

        await coord._increment_days_since_irrigation()

        assert coord.store.zones[1][const.ZONE_DAYS_SINCE_IRRIGATION] == 1
        assert coord.store.zones[2][const.ZONE_DAYS_SINCE_IRRIGATION] == 3
        assert coord.store.zones[3][const.ZONE_DAYS_SINCE_IRRIGATION] == 1

    async def test_the_global_reset_leaves_the_per_zone_counters_alone(
        self, monkeypatch
    ):
        """A sequential run can still be watering hours after this returns, so
        resetting per-zone counters here would clear them for zones the run
        never reaches."""
        zones = [_zone(1, days_since=4)]
        coord = _coord(monkeypatch, zones, _cfg())

        await coord._reset_days_since_irrigation()

        assert coord.store.config.days_since_last_irrigation == 0
        assert coord.store.zones[1][const.ZONE_DAYS_SINCE_IRRIGATION] == 4


class TestItSurvivesAStoreRoundTrip:
    async def test_the_counter_is_persisted(self, hass, hass_storage):
        store = SmartIrrigationStorage(hass)
        await store.async_load()
        zone = await store.async_create_zone({const.ZONE_NAME: "Front"})
        await store.async_update_zone(
            zone[const.ZONE_ID], {const.ZONE_DAYS_SINCE_IRRIGATION: 4}
        )
        await store.async_save()

        reloaded = SmartIrrigationStorage(hass)
        await reloaded.async_load()
        assert (
            reloaded.get_zone(zone[const.ZONE_ID])[const.ZONE_DAYS_SINCE_IRRIGATION]
            == 4
        )

    async def test_an_existing_zone_inherits_the_global_counter(
        self, hass, hass_storage
    ):
        """An install part-way through a days-between wait keeps waiting rather
        than being handed a fresh 0 and watering a day early."""
        store = SmartIrrigationStorage(hass)
        await store.async_load()
        zone = await store.async_create_zone({const.ZONE_NAME: "Front"})
        await store.async_update_config({const.CONF_DAYS_SINCE_LAST_IRRIGATION: 6})
        await store.async_save()

        # Strip the per-zone key the way a store written before it existed
        # would have been.
        for stored in hass_storage[STORAGE_KEY]["data"]["zones"]:
            stored.pop(const.ZONE_DAYS_SINCE_IRRIGATION, None)

        reloaded = SmartIrrigationStorage(hass)
        await reloaded.async_load()
        assert (
            reloaded.get_zone(zone[const.ZONE_ID])[const.ZONE_DAYS_SINCE_IRRIGATION]
            == 6
        )


class TestAHeldZoneSaysSoInItsHistory:
    """The hold was only ever an INFO log line, so from the panel a held zone
    was indistinguishable from one that simply had nothing to do. It is
    recorded as a skip so the zone's run history names the guard that held it.
    """

    def test_the_detail_matches_the_id_the_frontend_localizes(self):
        """The run history renders a skip ``detail`` through
        ``panels.zones.outlook.checks.<detail>``, and the guard already owns a
        key there under the id in ``skip_conditions``. The two literals are
        separate, so pin them together here rather than discovering the drift
        as a raw code in the panel."""
        assert const.SKIP_REASON_DAYS_BETWEEN == skip_conditions.SKIP_DAYS_BETWEEN

    async def test_a_held_zone_records_a_skip_and_a_watered_zone_does_not(
        self, monkeypatch
    ):
        zones = [_zone(1, days_since=0), _zone(2, days_since=3)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=3))
        watered = _capture(monkeypatch, coord)

        assert await coord._irrigate_linked_entities("all") is True

        assert watered == [2]
        held_log = coord.store.zones[1][const.ZONE_RUN_LOG]
        assert len(held_log) == 1
        assert held_log[0]["result"] == const.RUN_RESULT_SKIPPED
        assert held_log[0]["detail"] == const.SKIP_REASON_DAYS_BETWEEN
        assert coord.store.zones[2][const.ZONE_RUN_LOG] == []

    async def test_every_zone_held_still_records_each_one(self, monkeypatch):
        """The run returns False from inside the guard, so the record has to be
        written before that return rather than after the dispatch."""
        zones = [_zone(1, days_since=0), _zone(2, days_since=1)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=3))
        _capture(monkeypatch, coord)

        assert await coord._irrigate_linked_entities("all") is False

        for zid in (1, 2):
            log = coord.store.zones[zid][const.ZONE_RUN_LOG]
            assert [e["detail"] for e in log] == [const.SKIP_REASON_DAYS_BETWEEN]

    async def test_the_guard_being_off_records_nothing(self, monkeypatch):
        zones = [_zone(1, days_since=0)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=0))
        _capture(monkeypatch, coord)

        await coord._irrigate_linked_entities("all")

        assert coord.store.zones[1][const.ZONE_RUN_LOG] == []

    async def test_a_second_run_the_same_day_does_not_log_the_hold_twice(
        self, monkeypatch
    ):
        """A zone held at ``days_between = 3`` is held on every run for two
        days running, so an install with several schedules a day would bury its
        real runs. One entry per zone per calendar day, as the no-demand path
        does."""
        zones = [_zone(1, days_since=0)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=3))
        _capture(monkeypatch, coord)

        await coord._irrigate_linked_entities("all")
        await coord._irrigate_linked_entities("all")

        assert len(coord.store.zones[1][const.ZONE_RUN_LOG]) == 1

    async def test_a_hold_on_a_later_day_is_logged_again(self, monkeypatch):
        """Dedup is per calendar day, not once ever - otherwise the second day
        of a three-day wait would show nothing at all."""
        zones = [_zone(1, days_since=0)]
        yesterday = (dt_util.now() - timedelta(days=1)).isoformat()
        zones[0][const.ZONE_RUN_LOG] = [
            {
                "ts": yesterday,
                "result": const.RUN_RESULT_SKIPPED,
                "detail": const.SKIP_REASON_DAYS_BETWEEN,
            }
        ]
        coord = _coord(monkeypatch, zones, _cfg(days_between=3))
        _capture(monkeypatch, coord)

        await coord._irrigate_linked_entities("all")

        assert len(coord.store.zones[1][const.ZONE_RUN_LOG]) == 2

    async def test_a_same_day_run_between_two_holds_does_not_defeat_the_dedup(
        self, monkeypatch
    ):
        """Entries are newest-first, so a manual run recorded between the two
        holds displaces the marker out of the newest slot. The scan has to walk
        past it rather than only checking the head."""
        zones = [_zone(1, days_since=0)]
        coord = _coord(monkeypatch, zones, _cfg(days_between=3))
        _capture(monkeypatch, coord)

        await coord._irrigate_linked_entities("all")
        await coord._record_run(1, result=const.RUN_RESULT_COMPLETED, trigger="manual")
        await coord._irrigate_linked_entities("all")

        details = [e["detail"] for e in coord.store.zones[1][const.ZONE_RUN_LOG]]
        assert details.count(const.SKIP_REASON_DAYS_BETWEEN) == 1

    async def test_a_hold_is_evicted_before_a_real_run(self, monkeypatch):
        """A zone at ``days_between = 7`` records six holds a week against one
        run, so without the same protection the no-demand marker already has,
        adding these would push the real runs out of the bounded log - the very
        entries the history exists for."""
        log = [
            {"ts": f"2026-08-{i:02d}", "result": const.RUN_RESULT_COMPLETED}
            for i in range(1, const.RUN_LOG_MAX_ENTRIES + 1)
        ]
        log[-1]["ts"] = "oldest-real"
        log[25] = {
            "ts": "2026-08-26",
            "result": const.RUN_RESULT_SKIPPED,
            "detail": const.SKIP_REASON_DAYS_BETWEEN,
        }
        coord = _coord(monkeypatch, [_zone(1)], _cfg())
        coord.store.zones[1][const.ZONE_RUN_LOG] = log

        await coord._record_run(1, result=const.RUN_RESULT_COMPLETED)

        out = coord.store.zones[1][const.ZONE_RUN_LOG]
        assert len(out) == const.RUN_LOG_MAX_ENTRIES
        assert any(e["ts"] == "oldest-real" for e in out)
        assert not any(e.get("detail") == const.SKIP_REASON_DAYS_BETWEEN for e in out)
