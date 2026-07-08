"""Store schema and CRUD for the Gardena distributor collection."""

from unittest.mock import AsyncMock

import attr

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.store import (
    STORAGE_VERSION,
    DistributorEntry,
    MigratableStore,
    SmartIrrigationStorage,
    ZoneEntry,
    async_get_registry,
)


def test_distributor_entry_defaults():
    d = DistributorEntry()
    assert d.id is None
    assert d.name is None
    assert d.watering_mode == "classic"
    assert d.inlet_entity is None
    assert d.run_service is None
    assert d.stop_service is None
    assert d.duration_field == "duration"
    assert d.duration_unit == "seconds"
    assert d.confirm_entity is None
    assert d.flow_sensor is None
    assert d.pause_seconds == 300
    assert d.skip_pulse_seconds == 30
    assert d.current_outlet == 1
    # Fresh distributor is NEVER trusted as synced (spec 4.2).
    assert d.position_state == const.POSITION_STATE_UNCERTAIN
    assert d.notify_target is None
    assert d.use_master is True
    assert d.commissioning_confirmed is False
    assert d.schedules == []
    assert d.active_cycle == {}


def test_zone_entry_has_membership_fields():
    z = ZoneEntry()
    assert z.distributor_id is None
    assert z.outlet_number is None


async def test_zone_membership_survives_reload(hass):
    """Regression: distributor_id/outlet_number must be hydrated on load."""
    reg = await async_get_registry(hass)
    created = await reg.async_create_zone(
        {
            "name": "Ring-Zone",
            "size": 10.0,
            "throughput": 5.0,
            "distributor_id": 0,
            "outlet_number": 3,
        }
    )
    zone_id = created["id"]

    data = {
        "config": attr.asdict(reg.config),
        "zones": [attr.asdict(z) for z in reg.zones.values()],
        "modules": [],
        "mappings": [],
        "distributors": [],
    }
    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=data)
    await fresh.async_load()

    z = fresh.get_zone(zone_id)
    assert z["distributor_id"] == 0
    assert z["outlet_number"] == 3


def test_storage_version_is_11():
    assert STORAGE_VERSION == 11


async def test_migration_v10_adds_distributors_and_zone_fields(hass):
    store = MigratableStore(hass, STORAGE_VERSION, "smart_irrigation.storage")
    old = {
        "config": {},
        "zones": [{"id": 0, "name": "A"}, {"id": 1, "name": "B"}],
        "modules": [],
        "mappings": [],
    }
    migrated = await store._async_migrate_func(10, old)
    assert migrated["distributors"] == []
    for z in migrated["zones"]:
        assert z["distributor_id"] is None
        assert z["outlet_number"] is None


async def test_distributor_collection_round_trip(hass):
    """A distributor placed in the collection survives a save/load round-trip."""
    reg = await async_get_registry(hass)
    reg.distributors[0] = DistributorEntry(
        id=0,
        name="Garten",
        watering_mode="service",
        run_service="script.distributor_inlet",
        pause_seconds=120,
        skip_pulse_seconds=20,
        current_outlet=2,
        position_state=const.POSITION_STATE_SYNCED,
        commissioning_confirmed=True,
    )

    data = reg._data_to_save()
    assert "distributors" in data
    assert data["distributors"][0]["name"] == "Garten"

    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=data)
    await fresh.async_load()

    d = fresh.distributors[0]
    assert d.name == "Garten"
    assert d.watering_mode == "service"
    assert d.run_service == "script.distributor_inlet"
    assert d.pause_seconds == 120
    assert d.skip_pulse_seconds == 20
    assert d.current_outlet == 2
    assert d.position_state == const.POSITION_STATE_SYNCED
    assert d.commissioning_confirmed is True


async def test_create_distributor_assigns_id_and_defaults_uncertain(hass):
    reg = await async_get_registry(hass)
    created = await reg.async_create_distributor({"name": "Garten"})
    assert created["id"] == 0
    assert created["name"] == "Garten"
    # A freshly created distributor is never trusted (spec 4.2).
    assert created["position_state"] == const.POSITION_STATE_UNCERTAIN
    assert created["commissioning_confirmed"] is False

    second = await reg.async_create_distributor({"name": "Vorgarten"})
    assert second["id"] == 1


async def test_create_distributor_ignores_unknown_keys(hass):
    reg = await async_get_registry(hass)
    created = await reg.async_create_distributor(
        {"name": "Garten", "not_a_field": "bogus"}
    )
    assert "not_a_field" not in created
    assert created["name"] == "Garten"


async def test_update_and_get_distributor(hass):
    reg = await async_get_registry(hass)
    created = await reg.async_create_distributor({"name": "Garten"})
    did = created["id"]

    updated = await reg.async_update_distributor(
        did, {"current_outlet": 4, "position_state": const.POSITION_STATE_SYNCED}
    )
    assert updated["current_outlet"] == 4
    assert updated["position_state"] == const.POSITION_STATE_SYNCED

    got = reg.get_distributor(did)
    assert got["current_outlet"] == 4
    assert reg.get_distributor(999) is None


async def test_delete_distributor(hass):
    reg = await async_get_registry(hass)
    created = await reg.async_create_distributor({"name": "Garten"})
    did = created["id"]
    assert await reg.async_delete_distributor(did) is True
    assert reg.get_distributor(did) is None
    assert await reg.async_delete_distributor(did) is False


def test_distributor_entry_watch_inlet_defaults_false():
    """The opt-in inlet-watch flag defaults off (E3)."""
    assert DistributorEntry().watch_inlet is False


async def test_create_distributor_with_watch_inlet_round_trips(hass):
    """watch_inlet=True set at create time is returned by get/get_all (E3)."""
    reg = await async_get_registry(hass)
    created = await reg.async_create_distributor(
        {"name": "Garten", "watch_inlet": True}
    )
    did = created["id"]
    assert created["watch_inlet"] is True

    got = reg.get_distributor(did)
    assert got["watch_inlet"] is True

    all_dists = await reg.async_get_distributors()
    assert all_dists[0]["watch_inlet"] is True


async def test_create_distributor_defaults_watch_inlet_false(hass):
    """A distributor created without watch_inlet defaults to False (E3)."""
    reg = await async_get_registry(hass)
    created = await reg.async_create_distributor({"name": "Garten"})
    assert created["watch_inlet"] is False
    assert reg.get_distributor(created["id"])["watch_inlet"] is False


async def test_update_distributor_sets_watch_inlet(hass):
    """async_update_distributor toggles watch_inlet on (E3)."""
    reg = await async_get_registry(hass)
    created = await reg.async_create_distributor({"name": "Garten"})
    did = created["id"]

    updated = await reg.async_update_distributor(did, {"watch_inlet": True})
    assert updated["watch_inlet"] is True
    assert reg.get_distributor(did)["watch_inlet"] is True


async def test_watch_inlet_defaults_false_for_older_saved_distributor(hass):
    """A distributor persisted before watch_inlet existed loads as False (E3)."""
    reg = await async_get_registry(hass)
    # Simulate an older on-disk record that predates the watch_inlet key.
    saved = {
        "config": attr.asdict(reg.config),
        "zones": [],
        "modules": [],
        "mappings": [],
        "distributors": [{"id": 0, "name": "Legacy"}],
    }
    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=saved)
    await fresh.async_load()

    assert fresh.distributors[0].watch_inlet is False


async def test_watch_mode_derives_from_legacy_at_load(hass):
    """The load path derives watch_mode from the legacy watch_inlet when the
    persisted record predates watch_mode (True->count, else->ignore); an explicit
    watch_mode wins (E4)."""
    reg = await async_get_registry(hass)
    saved = {
        "config": attr.asdict(reg.config),
        "zones": [],
        "modules": [],
        "mappings": [],
        "distributors": [
            {"id": 0, "name": "LegacyOn", "watch_inlet": True},
            {"id": 1, "name": "LegacyOff", "watch_inlet": False},
            {"id": 2, "name": "Fresh"},
            {"id": 3, "name": "Explicit", "watch_inlet": True, "watch_mode": "warn"},
        ],
    }
    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=saved)
    await fresh.async_load()

    assert fresh.distributors[0].watch_mode == "count"  # legacy True -> count
    assert fresh.distributors[1].watch_mode == "ignore"  # legacy False -> ignore
    assert fresh.distributors[2].watch_mode == "ignore"  # absent -> ignore
    assert fresh.distributors[3].watch_mode == "warn"  # explicit wins
