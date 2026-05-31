"""Sensor platform for Smart Irrigation integration."""

import logging

from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import slugify

from . import const
from .performance import async_timer

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
    """Set up the SmartIrrigation sensor entities."""

    @callback
    def async_add_sensor_entity(config: dict):
        """Add each zone as Sensor entity (duration) and bucket sensor."""
        entity_id = "{}.{}".format(
            PLATFORM, const.DOMAIN + "_" + slugify(config["name"])
        )

        sensor_entity = SmartIrrigationZoneEntity(
            hass=hass,
            entity_id=entity_id,
            name=config[const.ZONE_NAME],
            id=config[const.ZONE_ID],
            size=config[const.ZONE_SIZE],
            throughput=config[const.ZONE_THROUGHPUT],
            state=config[const.ZONE_STATE],
            duration=config[const.ZONE_DURATION],
            bucket=config[const.ZONE_BUCKET],
            last_updated=config[const.ZONE_LAST_UPDATED],
            last_calculated=config[const.ZONE_LAST_CALCULATED],
            number_of_data_points=config[const.ZONE_NUMBER_OF_DATA_POINTS],
            delta=config[const.ZONE_DELTA],
            drainage_rate=config[const.ZONE_DRAINAGE_RATE],
            current_drainage=config[const.ZONE_CURRENT_DRAINAGE],
            multiplier=config.get(const.ZONE_MULTIPLIER, 1.0),
            lead_time=config.get(const.ZONE_LEAD_TIME, 0),
            maximum_duration=config.get(const.ZONE_MAXIMUM_DURATION, 0),
            maximum_bucket=config.get(const.ZONE_MAXIMUM_BUCKET),
        )
        bucket_entity_id = "{}.{}_bucket".format(
            PLATFORM, const.DOMAIN + "_" + slugify(config["name"])
        )
        bucket_entity = SmartIrrigationZoneBucketEntity(
            hass=hass,
            entity_id=bucket_entity_id,
            zone_id=config[const.ZONE_ID],
            zone_name=config[const.ZONE_NAME],
            bucket=config[const.ZONE_BUCKET],
        )
        if const.DOMAIN in hass.data:
            if not check_zone_entity_in_hass_data(hass, entity_id):
                hass.data[const.DOMAIN]["zones"][config["id"]] = sensor_entity
                hass.data[const.DOMAIN].setdefault("bucket_sensors", {})[config["id"]] = bucket_entity
                async_add_devices([sensor_entity, bucket_entity])

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass, const.DOMAIN + "_register_entity", async_add_sensor_entity
        )
    )
    async_dispatcher_send(hass, const.DOMAIN + "_platform_loaded")

    # register services if any here


def check_zone_entity_in_hass_data(hass: HomeAssistant | None, entity_id: str) -> bool:
    """Check if the entity_id is already in hass data."""
    return (
        hass
        and const.DOMAIN in hass.data
        and "zones" in hass.data[const.DOMAIN]
        and entity_id
        in [z.entity_id for z in hass.data[const.DOMAIN]["zones"].values()]
    )


class SmartIrrigationZoneEntity(SensorEntity, RestoreEntity):
    """Sensor entity representing a Smart Irrigation zone."""

    def __init__(
        self,
        hass: HomeAssistant,
        id: str,
        name: str,
        entity_id: str,
        size: float,
        throughput: float,
        state: str,
        duration: int,
        bucket: float,
        last_updated: str,
        last_calculated: str,
        number_of_data_points: int,
        delta: float,
        drainage_rate: float,
        current_drainage: float,
        multiplier: float = 1.0,
        lead_time: int = 0,
        maximum_duration: int = 0,
        maximum_bucket: float | None = None,
    ) -> None:
        """Initialize the sensor entity."""
        self._hass = hass
        self.entity_id = entity_id
        self._id = id
        self._name = name
        self._size = size
        self._throughput = throughput
        self._state = state
        self._duration = duration
        self._bucket = bucket
        self._last_updated = last_updated
        self._last_calculated = last_calculated
        self._number_of_data_points = number_of_data_points
        self._delta = delta
        self._drainage_rate = drainage_rate
        self._current_drainage = current_drainage
        self._multiplier = multiplier
        self._lead_time = lead_time
        self._maximum_duration = maximum_duration
        self._maximum_bucket = maximum_bucket
        self._last_updated_formatted = self._format_timestamp(self._last_updated)
        self._last_calculated_formatted = self._format_timestamp(self._last_calculated)

        async_dispatcher_connect(
            hass, const.DOMAIN + "_config_updated", self.async_update_sensor_entity
        )

        # Listen for unit system changes
        async_dispatcher_connect(
            hass,
            const.DOMAIN + "_unit_system_changed",
            self.async_handle_unit_system_change,
        )

    def _format_timestamp(self, val):
        """Format timestamp for display - cached for performance."""
        if val is None:
            return None

        outputformat = "%Y-%m-%d %H:%M:%S"

        # Optimize timestamp formatting to avoid string parsing
        if isinstance(val, str):
            try:
                # Try direct parsing without calling convert_timestamp
                from datetime import datetime

                return datetime.fromisoformat(val).strftime(outputformat)
            except (ValueError, TypeError):
                return val
        elif hasattr(val, "strftime"):
            try:
                return val.strftime(outputformat)
            except (ValueError, TypeError):
                return str(val)
        return str(val)

    @async_timer("async_update_sensor_entity")
    @callback
    def async_update_sensor_entity(self, id=None):
        """Update each zone as Sensor entity."""
        if self._id == id and self.hass and self.hass.data:
            _LOGGER.debug("[async_update_sensor_entity]: updating zone %s", id)

            # get the new values from store and update sensor state
            zone = self.hass.data[const.DOMAIN]["coordinator"].store.get_zone(id)
            self._name = zone["name"]
            self._size = zone["size"]
            self._throughput = zone["throughput"]
            self._state = zone["state"]
            self._duration = zone["duration"]
            self._bucket = zone["bucket"]
            self._last_updated = zone["last_updated"]
            self._last_calculated = zone["last_calculated"]
            self._number_of_data_points = zone["number_of_data_points"]
            self._delta = zone["delta"]
            self._drainage_rate = zone["drainage_rate"]
            self._current_drainage = zone["current_drainage"]
            self._multiplier = zone.get(const.ZONE_MULTIPLIER, 1.0)
            self._lead_time = zone.get(const.ZONE_LEAD_TIME, 0)
            self._maximum_duration = zone.get(const.ZONE_MAXIMUM_DURATION, 0)
            self._maximum_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)

            # Update cached formatted timestamps for performance
            self._last_updated_formatted = self._format_timestamp(self._last_updated)
            self._last_calculated_formatted = self._format_timestamp(
                self._last_calculated
            )

            # Ensure state change notification is properly sent
            self.async_schedule_update_ha_state(force_refresh=True)

    @callback
    def async_handle_unit_system_change(self):
        """Handle unit system changes by refreshing the entity state."""
        _LOGGER.debug("[async_handle_unit_system_change]: refreshing zone %s", self._id)

        # Force a state update to refresh any unit-dependent attributes
        # The actual unit conversions are handled in the attribute display logic
        self.async_schedule_update_ha_state(force_refresh=True)

    @property
    def device_info(self) -> dict:
        """Return info for device registry."""
        # Use a safe approach to get coordinator ID without blocking
        coordinator_id = "smart_irrigation"  # Default fallback

        # Only access hass.data if we're certain it's available and won't block
        if (
            hasattr(self, "hass")
            and self.hass is not None
            and hasattr(self.hass, "data")
            and const.DOMAIN in self.hass.data
        ):
            try:
                coordinator = self.hass.data[const.DOMAIN].get("coordinator")
                if coordinator and hasattr(coordinator, "id"):
                    coordinator_id = coordinator.id
            except (KeyError, AttributeError, RuntimeError):
                # Fall back to default if anything goes wrong
                pass

        return {
            "identifiers": {(const.DOMAIN, coordinator_id)},
            "name": const.NAME,
            "model": const.NAME,
            "sw_version": const.VERSION,
            "manufacturer": const.MANUFACTURER,
        }

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""

        return f"{self.entity_id}"

    @property
    def icon(self):
        """Return icon."""
        return const.SENSOR_ICON

    @property
    def name(self):
        """Return the friendly name to use for this entity."""
        return self._name

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return False

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SensorDeviceClass.DURATION

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement for this sensor."""
        return "s"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._duration

    @property
    def suggested_display_precision(self):
        """Return the suggested display precision for this sensor."""
        return 0

    @property
    def suggested_unit_of_measurement(self):
        """Return the suggested unit of measurement for this sensor."""
        return "s"

    @property
    def extra_state_attributes(self):
        """Return the data of the entity."""
        # Ensure cached timestamps are available
        if (
            not hasattr(self, "_last_updated_formatted")
            or self._last_updated_formatted is None
        ):
            self._last_updated_formatted = self._format_timestamp(self._last_updated)
        if (
            not hasattr(self, "_last_calculated_formatted")
            or self._last_calculated_formatted is None
        ):
            self._last_calculated_formatted = self._format_timestamp(
                self._last_calculated
            )

        return {
            "id": self._id,
            "size": self._size,
            "throughput": self._throughput,
            "drainage_rate": self._drainage_rate,
            "current_drainage": self._current_drainage,
            "state": self._state,
            "bucket": self._bucket,
            "last_updated": self._last_updated_formatted,
            "last_calculated": self._last_calculated_formatted,
            "number_of_data_points": self._number_of_data_points,
            "et_value": self._delta,
            "multiplier": self._multiplier,
            "lead_time": self._lead_time,
            "maximum_duration": self._maximum_duration,
            "maximum_bucket": self._maximum_bucket,
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        _LOGGER.debug("%s is added to hass", self.entity_id)
        await super().async_added_to_hass()

        # Restore previous state if available
        last_state = await self.async_get_last_state()
        if last_state is not None:
            # Entity was previously known, restore some state if needed
            _LOGGER.debug("Restored state for %s: %s", self.entity_id, last_state.state)

        # Force initial state update to ensure UI shows current data
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_will_remove_from_hass(self):
        """Handle removal of the entity from Home Assistant."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("%s is removed from hass", self.entity_id)


class SmartIrrigationZoneBucketEntity(SensorEntity, RestoreEntity):
    """Sensor showing the current bucket value (mm) for a Smart Irrigation zone."""

    def __init__(
        self,
        hass: HomeAssistant,
        entity_id: str,
        zone_id: int,
        zone_name: str,
        bucket: float,
    ) -> None:
        """Initialize the bucket sensor."""
        self._hass = hass
        self.entity_id = entity_id
        self._zone_id = zone_id
        self._zone_name = zone_name
        self._bucket = bucket

        async_dispatcher_connect(
            hass, const.DOMAIN + "_config_updated", self._async_update_bucket
        )

    @callback
    def _async_update_bucket(self, zone_id=None):
        """Update bucket value when zone config changes."""
        if self._zone_id == zone_id and self.hass and self.hass.data:
            zone = self.hass.data[const.DOMAIN]["coordinator"].store.get_zone(
                self._zone_id
            )
            if zone:
                self._bucket = zone.get(const.ZONE_BUCKET, self._bucket)
                self._zone_name = zone.get(const.ZONE_NAME, self._zone_name)
                self.async_schedule_update_ha_state(force_refresh=True)

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{const.DOMAIN}_{self._zone_id}_bucket"

    @property
    def name(self) -> str:
        """Return friendly name."""
        return f"{self._zone_name} Bucket"

    @property
    def icon(self) -> str:
        """Return icon."""
        return "mdi:bucket"

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def device_class(self):
        """No standard device class for bucket depth."""
        return None

    @property
    def state_class(self) -> str:
        """Return state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return mm as unit."""
        return "mm"

    @property
    def native_value(self) -> float:
        """Return current bucket value."""
        return round(self._bucket, 2)

    @property
    def suggested_display_precision(self) -> int:
        """Two decimal places."""
        return 2

    @property
    def extra_state_attributes(self) -> dict:
        """Return zone identification attributes."""
        return {
            "zone_id": self._zone_id,
            "zone_name": self._zone_name,
        }

    @property
    def device_info(self) -> dict:
        """Return device info matching the zone duration sensor."""
        coordinator_id = "smart_irrigation"
        if (
            hasattr(self, "hass")
            and self.hass is not None
            and hasattr(self.hass, "data")
            and const.DOMAIN in self.hass.data
        ):
            try:
                coordinator = self.hass.data[const.DOMAIN].get("coordinator")
                if coordinator and hasattr(coordinator, "id"):
                    coordinator_id = coordinator.id
            except (KeyError, AttributeError, RuntimeError):
                pass

        return {
            "identifiers": {(const.DOMAIN, coordinator_id)},
            "name": const.NAME,
            "model": const.NAME,
            "sw_version": const.VERSION,
            "manufacturer": const.MANUFACTURER,
        }

    async def async_added_to_hass(self):
        """Restore previous state if available."""
        _LOGGER.debug("%s is added to hass", self.entity_id)
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_will_remove_from_hass(self):
        """Handle removal."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("%s is removed from hass", self.entity_id)
