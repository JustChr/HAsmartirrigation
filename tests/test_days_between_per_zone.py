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

from types import SimpleNamespace
from unittest.mock import Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
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
