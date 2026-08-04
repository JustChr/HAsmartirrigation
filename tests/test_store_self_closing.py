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


def test_storage_version_is_13():
    # v13 records which unit system the stored zone values were written under,
    # so a metric<->imperial flip is detectable across a restart (issue #67, see
    # tests/test_unit_system_migration.py).
    assert STORAGE_VERSION == 13


def test_zone_entry_has_self_closing_fields():
    z = ZoneEntry()
    assert z.watering_mode == const.WATERING_MODE_CLASSIC
    assert z.run_service is None
    # Defaults to "duration" so the shipped blueprints work out of the box.
    assert z.duration_field == "duration"
    assert z.duration_unit == const.DURATION_UNIT_SECONDS
    assert z.stop_service is None
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


async def test_active_valve_runs_survive_reload(hass):
    """Regression: an in-flight self-closing run must be hydrated on load.

    The attr.ib and the migration setdefault existed without a hydration line, so
    the list came back EMPTY on every restart: async_resume_self_closing_runs had
    nothing to reconcile, a run interrupted by a restart was never finalised, and
    the next config write dropped the persisted record. It is also what tells the
    calculation gate the zone is still being watered (run_state.RunStateMixin).
    """
    reg = await async_get_registry(hass)
    run = {
        const.RUN_ZONE_ID: 3,
        const.RUN_ENTITY_ID: "script.irrigation_beet",
        const.RUN_STARTED: "2026-08-03T21:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_PLANNED_MM: 4.0,
        const.RUN_PRE_BUCKET: -12.0,
        const.RUN_MODE: const.WATERING_MODE_SERVICE,
        const.RUN_CREDITED: True,
    }
    await reg.async_update_config({const.CONF_ACTIVE_VALVE_RUNS: [run]})

    data = {
        "config": attr.asdict(reg.config),
        "zones": [],
        "modules": [],
        "mappings": [],
    }
    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=data)
    await fresh.async_load()

    assert fresh.config.active_valve_runs == [run]
