"""Test the Smart Irrigation store (SmartIrrigationStorage).

Rewritten in A6 for the current store API: the registry is a
SmartIrrigationStorage backed by MigratableStore; CRUD is async_create_/
async_update_/async_delete_* (entries are attr dataclasses with int ids); writes
go through async_schedule_save(). The old tests patched the wrong class and used
async_add_/async_remove_ with string ids.
"""

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.store import (
    SmartIrrigationStorage,
    async_get_registry,
)


class TestSmartIrrigationStore:
    """CRUD + config behavior of SmartIrrigationStorage."""

    async def test_async_get_registry_returns_cached_storage(self, hass) -> None:
        reg = await async_get_registry(hass)
        assert isinstance(reg, SmartIrrigationStorage)
        # cached on hass.data: same instance on a second call
        assert await async_get_registry(hass) is reg

    async def test_config_get_and_update(self, hass) -> None:
        reg = await async_get_registry(hass)
        cfg = await reg.async_get_config()
        assert isinstance(cfg, dict)
        assert const.CONF_USE_WEATHER_SERVICE in cfg

        updated = await reg.async_update_config({const.CONF_USE_WEATHER_SERVICE: True})
        assert updated[const.CONF_USE_WEATHER_SERVICE] is True

        # unknown keys are filtered out (not raised)
        await reg.async_update_config({"definitely_not_a_config_field": 1})

    async def test_distributors_enabled_config_roundtrip(self, hass) -> None:
        reg = await async_get_registry(hass)
        cfg = await reg.async_get_config()
        # New experimental flag is present and defaults off.
        assert cfg.get(const.CONF_DISTRIBUTORS_ENABLED) is False
        # A partial update round-trips without clobbering other settings.
        updated = await reg.async_update_config({const.CONF_DISTRIBUTORS_ENABLED: True})
        assert updated[const.CONF_DISTRIBUTORS_ENABLED] is True
        assert const.CONF_USE_WEATHER_SERVICE in updated

    async def test_zone_crud(self, hass) -> None:
        reg = await async_get_registry(hass)
        created = await reg.async_create_zone(
            {"name": "Garden", "size": 100.0, "throughput": 10.0}
        )
        zone_id = created["id"]
        assert zone_id is not None
        assert created["name"] == "Garden"

        assert any(z["id"] == zone_id for z in await reg.async_get_zones())

        await reg.async_update_zone(zone_id, {"name": "Garden Updated"})
        assert reg.get_zone(zone_id)["name"] == "Garden Updated"

        await reg.async_delete_zone(zone_id)
        assert reg.get_zone(zone_id) is None

    async def test_zone_flow_counter_fields_roundtrip(self, hass) -> None:
        """flow_counter_type override + cross-run learning fields (FM-2).

        A freshly created zone defaults to auto / 0 / None; explicit values for
        the override and the internal learning state round-trip unchanged
        through create + update (attr.asdict).
        """
        reg = await async_get_registry(hass)

        # Defaults on a brand-new zone.
        created = await reg.async_create_zone({"name": "Beet"})
        zone_id = created["id"]
        assert created[const.ZONE_FLOW_COUNTER_TYPE] == "auto"
        assert created[const.ZONE_FLOW_RESET_STREAK] == 0
        assert created[const.ZONE_FLOW_LAST_END] is None

        # Explicit override + learning state round-trip through update + get_zone.
        await reg.async_update_zone(
            zone_id,
            {
                const.ZONE_FLOW_COUNTER_TYPE: "per_run",
                const.ZONE_FLOW_RESET_STREAK: 2,
                const.ZONE_FLOW_LAST_END: 12.0,
            },
        )
        stored = reg.get_zone(zone_id)
        assert stored[const.ZONE_FLOW_COUNTER_TYPE] == "per_run"
        assert stored[const.ZONE_FLOW_RESET_STREAK] == 2
        assert stored[const.ZONE_FLOW_LAST_END] == 12.0

    async def test_update_zone_maximum_bucket_without_bucket_no_keyerror(
        self, hass
    ) -> None:
        """Partial update with maximum_bucket but no bucket must not KeyError.

        Review finding J: the max-bucket clamp indexed changes[ZONE_BUCKET]
        without a presence guard. A partial zone POST like
        {"id": 0, "maximum_bucket": 30} (bucket absent) reached this branch and
        raised KeyError -> HTTP 500. The clamp must be skipped when bucket is
        not part of the update, and maximum_bucket must still be applied.
        """
        reg = await async_get_registry(hass)
        created = await reg.async_create_zone({"name": "Beet"})
        zone_id = created["id"]

        # bucket is intentionally NOT in the changes dict.
        await reg.async_update_zone(zone_id, {const.ZONE_MAXIMUM_BUCKET: 30})

        stored = reg.get_zone(zone_id)
        assert stored[const.ZONE_MAXIMUM_BUCKET] == 30

    async def test_module_crud(self, hass) -> None:
        reg = await async_get_registry(hass)
        created = await reg.async_create_module(
            {"name": "PyETO", "description": "test", "config": {}}
        )
        module_id = created["id"]
        assert module_id is not None
        assert any(m["id"] == module_id for m in await reg.async_get_modules())

        await reg.async_delete_module(module_id)
        assert all(m["id"] != module_id for m in await reg.async_get_modules())

    async def test_mapping_crud(self, hass) -> None:
        reg = await async_get_registry(hass)
        created = await reg.async_create_mapping(
            {"name": "Test Mapping", "mappings": {}}
        )
        mapping_id = created["id"]
        assert mapping_id is not None
        assert any(m["id"] == mapping_id for m in await reg.async_get_mappings())

        await reg.async_delete_mapping(mapping_id)
        assert all(m["id"] != mapping_id for m in await reg.async_get_mappings())
