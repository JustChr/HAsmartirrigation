"""Store schema for the self-closing valve mode."""

from unittest.mock import AsyncMock

import attr

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.store import (
    STORAGE_VERSION,
    Config,
    SmartIrrigationStorage,
    ZoneEntry,
    async_get_registry,
)


def test_storage_version_is_10():
    assert STORAGE_VERSION == 10


def test_zone_entry_has_self_closing_fields():
    z = ZoneEntry()
    assert z.watering_mode == const.WATERING_MODE_CLASSIC
    assert z.run_service is None
    # Defaults to "duration" so the shipped blueprints work out of the box.
    assert z.duration_field == "duration"
    assert z.duration_unit == const.DURATION_UNIT_SECONDS
    assert z.run_data == {}
    assert z.stop_service is None
    assert z.stop_data == {}
    assert z.confirm_entity is None


def test_config_has_active_valve_runs():
    c = Config()
    assert c.active_valve_runs == []


async def test_create_zone_ignores_unknown_keys(hass):
    reg = await async_get_registry(hass)
    created = await reg.async_create_zone(
        {
            "name": "Garden",
            "size": 100.0,
            "throughput": 10.0,
            "not_a_zone_field": "bogus",
        }
    )
    assert "not_a_zone_field" not in created
    assert created["name"] == "Garden"


async def test_self_closing_fields_survive_reload(hass):
    """Regression: watering_mode/run_service must be hydrated on load."""
    reg = await async_get_registry(hass)
    created = await reg.async_create_zone(
        {
            "name": "Beet",
            "size": 10.0,
            "throughput": 5.0,
            "watering_mode": const.WATERING_MODE_SERVICE,
            "run_service": "script.irrigation_beet",
            "duration_field": "dauer",
            "duration_unit": const.DURATION_UNIT_MINUTES,
            "confirm_entity": "valve.beet",
        }
    )
    zone_id = created["id"]

    # Round-trip through the store's own persisted format and reload.
    data = {
        "config": attr.asdict(reg.config),
        "zones": [attr.asdict(z) for z in reg.zones.values()],
        "modules": [],
        "mappings": [],
    }
    reg._store.async_load = AsyncMock(return_value=data)
    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=data)
    await fresh.async_load()

    z = fresh.get_zone(zone_id)
    assert z["watering_mode"] == const.WATERING_MODE_SERVICE
    assert z["run_service"] == "script.irrigation_beet"
    assert z["duration_field"] == "dauer"
    assert z["duration_unit"] == const.DURATION_UNIT_MINUTES
    assert z["confirm_entity"] == "valve.beet"
