"""Store schema for the self-closing valve mode."""

from unittest.mock import AsyncMock

import attr

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.store import (
    STORAGE_VERSION,
    Config,
    SmartIrrigationStorage,
    ZoneEntry,
    async_get_registry,
)


def test_storage_version_is_14():
    # v14 reshapes recurring schedules: the old `type` field is split into
    # `recurrence` plus independent Start/Finish bounds (see
    # tests/test_schedule_migration_v14.py).
    assert STORAGE_VERSION == 14


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


def _reload_payload(reg):
    """The store's own persisted format, as async_load reads it back."""
    return {
        "config": attr.asdict(reg.config),
        "zones": [attr.asdict(z) for z in reg.zones.values()],
        "modules": [],
        "mappings": [],
    }


async def _reloaded(hass, data):
    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=data)
    await fresh.async_load()
    return fresh


async def test_latency_margin_survives_reload(hass):
    """Regression guard: the margin must be hydrated on load (#139).

    Without the zone.get(...) line in the load block the attr default wins and a
    margin the user set silently reverts to 4 s on every restart.
    """
    reg = await async_get_registry(hass)
    created = await reg.async_create_zone(
        {
            "name": "Beet",
            "size": 10.0,
            "throughput": 5.0,
            "watering_mode": const.WATERING_MODE_SERVICE,
            "run_service": "script.irrigation_beet",
            "confirm_entity": "valve.beet",
            const.ZONE_LATENCY_MARGIN: 7,
        }
    )
    zone_id = created["id"]
    assert created[const.ZONE_LATENCY_MARGIN] == 7

    fresh = await _reloaded(hass, _reload_payload(reg))

    assert fresh.get_zone(zone_id)[const.ZONE_LATENCY_MARGIN] == 7


async def test_zone_stored_without_latency_margin_loads_the_default(hass):
    """A zone persisted before #139 has no key and loads with 4 s, no migration."""
    reg = await async_get_registry(hass)
    created = await reg.async_create_zone(
        {
            "name": "Front",
            "size": 10.0,
            "throughput": 5.0,
            "watering_mode": const.WATERING_MODE_SERVICE,
            "run_service": "script.irrigation_front",
            "confirm_entity": "valve.front",
        }
    )
    zone_id = created["id"]
    data = _reload_payload(reg)
    for stored in data["zones"]:
        stored.pop(const.ZONE_LATENCY_MARGIN, None)
    assert all(const.ZONE_LATENCY_MARGIN not in z for z in data["zones"])

    fresh = await _reloaded(hass, data)

    assert const.DEFAULT_LATENCY_MARGIN_SECONDS == 4
    assert fresh.get_zone(zone_id)[const.ZONE_LATENCY_MARGIN] == 4


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
