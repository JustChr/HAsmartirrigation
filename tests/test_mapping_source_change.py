"""Bug 2: switching a mapping's source must invalidate the shared buffer.

The mapping owns a single shared reading buffer (``MAPPING_DATA``) that each zone
consumes over its own ``(last_consumed_at, now]`` window. When a quantity's
source or sensor entity changes, the buffered readings come from the *old*
source. A delta / Riemann-sum aggregate then reads the discontinuity as a huge
jump (the real incident: switching a rain sensor from a rate to a cumulative
total produced a ~3202 mm "rainfall"). Saving a source change must therefore
clear the buffer and re-anchor the consuming zones' watermarks to now.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


def _make_coordinator(store):
    """Build a coordinator without running __init__ (only store/hass needed)."""
    coordinator = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coordinator.store = store
    coordinator.hass = Mock()
    return coordinator


def _store_with_mapping(mapping):
    store = Mock()
    store.get_mapping = Mock(return_value=mapping)
    store.async_update_mapping = AsyncMock()
    store.async_update_zone = AsyncMock()
    return store


def _mapping(sensor_entity):
    return {
        const.MAPPING_ID: 0,
        const.MAPPING_NAME: "Test mapping",
        const.MAPPING_MAPPINGS: {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                const.MAPPING_CONF_SENSOR: sensor_entity,
            },
        },
        const.MAPPING_DATA: [{"x": 1}, {"x": 2}],
    }


class TestMappingSourceChangeInvalidatesBuffer:
    """async_update_mapping_config must invalidate the buffer on a source switch."""

    async def test_sensor_change_clears_buffer_and_reanchors_zones(self):
        store = _store_with_mapping(_mapping("sensor.rain_rate"))
        coordinator = _make_coordinator(store)
        coordinator._get_zones_that_use_this_mapping = AsyncMock(return_value=[1, 2])

        new_data = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_PRECIPITATION: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    # sensor entity switched rate -> cumulative counter
                    const.MAPPING_CONF_SENSOR: "sensor.total_rain",
                },
            },
        }

        with patch(
            "custom_components.smart_irrigation.async_dispatcher_send"
        ) as dispatch:
            await coordinator.async_update_mapping_config(0, new_data)

        # Each consuming zone must be told to refresh, not just the mapping: the
        # zone sensors re-read only on a signal carrying their OWN id, so a single
        # mapping-scoped dispatch leaves every zone whose id != mapping_id showing
        # counts for readings that no longer exist.
        signalled = {
            call.args[2]
            for call in dispatch.call_args_list
            if call.args[1] == const.DOMAIN + "_config_updated"
        }
        assert {1, 2} <= signalled

        # The mapping must be updated with an emptied buffer.
        args, _ = store.async_update_mapping.call_args
        assert args[0] == 0
        assert args[1].get(const.MAPPING_DATA) == []
        # Every consuming zone is re-anchored to "now".
        assert store.async_update_zone.await_count == 2
        anchored = set()
        for call in store.async_update_zone.await_args_list:
            zone_id, changes = call.args
            anchored.add(zone_id)
            assert const.ZONE_LAST_CONSUMED in changes
            assert isinstance(changes[const.ZONE_LAST_CONSUMED], datetime)
            # The data-point count is derived from the buffer that was just
            # emptied; leaving it stale reports readings that no longer exist.
            assert changes[const.ZONE_NUMBER_OF_DATA_POINTS] == 0
        assert anchored == {1, 2}

    async def test_source_type_change_clears_buffer(self):
        store = _store_with_mapping(_mapping("sensor.rain_rate"))
        coordinator = _make_coordinator(store)
        coordinator._get_zones_that_use_this_mapping = AsyncMock(return_value=[1])

        new_data = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_PRECIPITATION: {
                    # source type switched sensor -> weather service
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE,
                    const.MAPPING_CONF_SENSOR: "",
                },
            },
        }

        with patch("custom_components.smart_irrigation.async_dispatcher_send"):
            await coordinator.async_update_mapping_config(0, new_data)

        args, _ = store.async_update_mapping.call_args
        assert args[1].get(const.MAPPING_DATA) == []
        assert store.async_update_zone.await_count == 1

    async def test_no_source_change_keeps_buffer(self):
        store = _store_with_mapping(_mapping("sensor.rain_rate"))
        coordinator = _make_coordinator(store)
        coordinator._get_zones_that_use_this_mapping = AsyncMock(return_value=[1, 2])

        # Only the name changes — the buffer must be left intact.
        new_data = {const.MAPPING_NAME: "Renamed mapping"}

        with patch("custom_components.smart_irrigation.async_dispatcher_send"):
            await coordinator.async_update_mapping_config(0, new_data)

        args, _ = store.async_update_mapping.call_args
        assert const.MAPPING_DATA not in args[1]
        store.async_update_zone.assert_not_called()

    async def test_legacy_string_old_mapping_value_does_not_crash(self):
        """A legacy bare-string value in the stored mapping must not crash.

        Older / migrated installs may store a quantity's config as a bare string
        in MAPPING_MAPPINGS instead of a dict; the rest of the integration guards
        this with isinstance(..., str) (e.g. check_mapping_sources). Defining a
        real source for such a quantity must invalidate the buffer, not raise
        AttributeError inside the source-change diff.
        """
        old_mapping = {
            const.MAPPING_ID: 0,
            const.MAPPING_NAME: "Test mapping",
            const.MAPPING_MAPPINGS: {
                # legacy bare-string value (not a dict)
                const.MAPPING_PRECIPITATION: const.MAPPING_PRECIPITATION,
            },
            const.MAPPING_DATA: [{"x": 1}],
        }
        store = _store_with_mapping(old_mapping)
        coordinator = _make_coordinator(store)
        coordinator._get_zones_that_use_this_mapping = AsyncMock(return_value=[1])

        new_data = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_PRECIPITATION: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.rain_rate",
                },
            },
        }

        with patch("custom_components.smart_irrigation.async_dispatcher_send"):
            await coordinator.async_update_mapping_config(0, new_data)

        # Defining a real source for the legacy quantity invalidates the buffer.
        args, _ = store.async_update_mapping.call_args
        assert args[1].get(const.MAPPING_DATA) == []
        assert store.async_update_zone.await_count == 1

    async def test_source_change_also_neutralises_the_carry_forward(self):
        """Clearing MAPPING_DATA alone is not enough any more.

        aggregate_window is now given MAPPING_DATA_LAST_ENTRY as a carry-forward
        for continuous-update sensor groups, so a value captured from the OLD
        source would survive the buffer wipe and re-introduce exactly the
        discontinuity this invalidation exists to prevent. The keys can't be
        deleted (async_update_mapping merges omitted keys back in), so they are
        set to None — which aggregate_window ignores.
        """
        mapping = _mapping("sensor.rain_rate")
        mapping[const.MAPPING_DATA_LAST_ENTRY] = {const.MAPPING_PRECIPITATION: 3202.0}
        store = _store_with_mapping(mapping)
        coordinator = _make_coordinator(store)
        coordinator._get_zones_that_use_this_mapping = AsyncMock(return_value=[1])

        new_data = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_PRECIPITATION: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.total_rain",
                },
            },
        }

        with patch("custom_components.smart_irrigation.async_dispatcher_send"):
            await coordinator.async_update_mapping_config(0, new_data)

        args, _ = store.async_update_mapping.call_args
        assert args[1][const.MAPPING_DATA] == []
        assert args[1][const.MAPPING_DATA_LAST_ENTRY] == {
            const.MAPPING_PRECIPITATION: None
        }

    async def test_same_sources_resave_keeps_buffer(self):
        store = _store_with_mapping(_mapping("sensor.rain_rate"))
        coordinator = _make_coordinator(store)
        coordinator._get_zones_that_use_this_mapping = AsyncMock(return_value=[1, 2])

        # Re-save with identical source config — no invalidation.
        new_data = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_PRECIPITATION: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.rain_rate",
                },
            },
        }

        with patch("custom_components.smart_irrigation.async_dispatcher_send"):
            await coordinator.async_update_mapping_config(0, new_data)

        args, _ = store.async_update_mapping.call_args
        assert const.MAPPING_DATA not in args[1]
        store.async_update_zone.assert_not_called()
