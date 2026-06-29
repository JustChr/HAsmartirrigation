"""Sensor platform for Smart Irrigation integration."""

import datetime
import logging

import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import slugify
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .entity import zone_device_info
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

        def child_id(suffix: str) -> str:
            return "{}.{}_{}".format(
                PLATFORM, const.DOMAIN + "_" + slugify(config["name"]), suffix
            )

        extra_entities = [
            SmartIrrigationZoneETSensor(hass, child_id("et"), config),
            SmartIrrigationZoneLiveDeficitSensor(
                hass, child_id("live_deficit"), config
            ),
            SmartIrrigationZoneLastIrrigationSensor(
                hass, child_id("last_irrigation"), config
            ),
            SmartIrrigationZoneNextIrrigationSensor(
                hass, child_id("next_irrigation"), config
            ),
            SmartIrrigationZoneWaterUsageSensor(hass, child_id("water_used"), config),
            SmartIrrigationZoneLastWaterUsageSensor(
                hass, child_id("last_water_used"), config
            ),
        ]
        extra_entities.extend(
            SmartIrrigationZoneDiagnosticSensor(hass, child_id(spec[1]), config, *spec)
            for spec in ZONE_DIAGNOSTIC_SENSORS
        )

        if const.DOMAIN in hass.data:
            if not check_zone_entity_in_hass_data(hass, entity_id):
                hass.data[const.DOMAIN]["zones"][config["id"]] = sensor_entity
                hass.data[const.DOMAIN].setdefault("bucket_sensors", {})[
                    config["id"]
                ] = bucket_entity
                hass.data[const.DOMAIN].setdefault("zone_extra_sensors", {})[
                    config["id"]
                ] = extra_entities
                async_add_devices([sensor_entity, bucket_entity, *extra_entities])

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass, const.DOMAIN + "_register_entity", async_add_sensor_entity
        )
    )
    # The existing-zone replay (`_platform_loaded`) is fired once from
    # __init__.async_setup_entry AFTER all per-zone platforms have subscribed,
    # so every platform receives it — not just this one.

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
    """Sensor entity representing a Smart Irrigation zone (irrigation duration)."""

    _attr_has_entity_name = True
    _attr_translation_key = "duration"

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
        """Return info for device registry (per-zone device)."""
        return zone_device_info(self._hass, self._id, self._name)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity.

        Migrated from the legacy entity-id-based id to the per-zone scheme
        ``smart_irrigation_<zone_id>_duration`` (matches every other entity).
        The one-time registry migration in ``__init__`` rewrites existing
        installs so the entity_id and history carry over.
        """
        return f"{const.DOMAIN}_{self._id}_duration"

    @property
    def icon(self):
        """Return icon."""
        return const.SENSOR_ICON

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

    _attr_has_entity_name = True
    _attr_translation_key = "bucket"

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
        return zone_device_info(self._hass, self._zone_id, self._zone_name)

    async def async_added_to_hass(self):
        """Restore previous state if available."""
        _LOGGER.debug("%s is added to hass", self.entity_id)
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_will_remove_from_hass(self):
        """Handle removal."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("%s is removed from hass", self.entity_id)


def _to_aware_datetime(value):
    """Parse a stored timestamp (datetime or ISO string) to an aware datetime.

    The store writes naive local datetimes (``datetime.now()``) for
    last_calculated/last_updated and aware ones (``dt_util.now()``) for
    last_irrigation; naive values are interpreted as local time.
    """
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except ValueError:
            return None
    if not isinstance(value, datetime.datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
    return value


class SmartIrrigationZoneChildSensor(SensorEntity):
    """Base for the additional per-zone sensors.

    Holds zone identity, groups under the per-zone device and refreshes from
    the store when the zone's ``_config_updated`` signal fires.
    """

    _attr_has_entity_name = True
    _attr_should_poll = False
    suffix = ""

    def __init__(self, hass: HomeAssistant, entity_id: str, zone: dict) -> None:
        """Initialize from the zone config dict."""
        self._hass = hass
        self.entity_id = entity_id
        self._zone_id = zone[const.ZONE_ID]
        self._zone_name = zone[const.ZONE_NAME]
        self._update_from_zone(zone)

        async_dispatcher_connect(
            hass, const.DOMAIN + "_config_updated", self._async_zone_updated
        )

    def _update_from_zone(self, zone: dict) -> None:
        """Pull this sensor's value(s) from the zone dict (override)."""

    @callback
    def _async_zone_updated(self, zone_id=None):
        """Refresh from the store when this zone changes."""
        if self._zone_id != zone_id or not (self.hass and self.hass.data):
            return
        zone = self.hass.data[const.DOMAIN]["coordinator"].store.get_zone(self._zone_id)
        if zone:
            self._zone_name = zone.get(const.ZONE_NAME, self._zone_name)
            self._update_from_zone(zone)
            self.async_schedule_update_ha_state(force_refresh=True)

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{const.DOMAIN}_{self._zone_id}_{self.suffix}"

    @property
    def device_info(self) -> dict:
        """Group under the per-zone device."""
        return zone_device_info(self._hass, self._zone_id, self._zone_name)

    @property
    def extra_state_attributes(self) -> dict:
        """Return zone identification attributes."""
        return {
            "zone_id": self._zone_id,
            "zone_name": self._zone_name,
        }

    @property
    def _depth_unit(self) -> str:
        """Stored water-depth values are in the display unit system."""
        return "mm" if self._hass.config.units is METRIC_SYSTEM else "in"

    async def async_added_to_hass(self):
        """Push the initial state."""
        _LOGGER.debug("%s is added to hass", self.entity_id)
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(force_refresh=True)


class SmartIrrigationZoneETSensor(SmartIrrigationZoneChildSensor):
    """The zone's last calculated bucket delta (net daily change; data key et_value)."""

    suffix = "et"
    _attr_translation_key = "bucket_delta"
    _attr_icon = "mdi:waves-arrow-up"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _update_from_zone(self, zone: dict) -> None:
        self._delta = zone.get(const.ZONE_DELTA)

    @property
    def native_unit_of_measurement(self) -> str:
        """Depth per day in the display unit system."""
        return self._depth_unit

    @property
    def native_value(self):
        """Return the last calculated delta."""
        return round(self._delta, 2) if self._delta is not None else None


class SmartIrrigationZoneLiveDeficitSensor(SmartIrrigationZoneChildSensor):
    """Intra-day live deficit estimate, served from the coordinator's cache.

    The cache is refreshed by the weather-update and daily-calculation cycles
    (see LiveEstimateMixin.async_refresh_zone_estimates) — the same data the
    panel outlook shows.
    """

    suffix = "live_deficit"
    _attr_translation_key = "live_bucket"
    _attr_icon = "mdi:water-minus"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass: HomeAssistant, entity_id: str, zone: dict) -> None:
        """Initialize and listen for estimate-cache refreshes."""
        super().__init__(hass, entity_id, zone)
        async_dispatcher_connect(
            hass, const.DOMAIN + "_estimates_updated", self._async_estimates_updated
        )

    @callback
    def _async_estimates_updated(self):
        """The estimate cache was refreshed — re-read it."""
        if self.hass:
            self.async_schedule_update_ha_state(force_refresh=True)

    def _estimate(self) -> dict:
        """This zone's entry in the coordinator's estimate cache."""
        try:
            coordinator = self._hass.data[const.DOMAIN]["coordinator"]
            cache = coordinator._zone_estimates_cache or {}  # noqa: SLF001
            return cache.get(str(self._zone_id)) or {}
        except (KeyError, AttributeError, TypeError):
            return {}

    @property
    def native_unit_of_measurement(self) -> str:
        """Estimates are reported in the display unit system."""
        return self._depth_unit

    @property
    def native_value(self):
        """Return the cached live deficit (None until a cycle has run)."""
        return self._estimate().get("live_deficit")

    @property
    def extra_state_attributes(self) -> dict:
        """Zone identity plus how/when the estimate was computed."""
        est = self._estimate()
        return {
            **super().extra_state_attributes,
            "method": est.get("method"),
            "et_since_calculation": est.get("et_since"),
            "precipitation_since_calculation": est.get("precip_since"),
            "as_of": est.get("as_of"),
        }


class SmartIrrigationZoneLastIrrigationSensor(SmartIrrigationZoneChildSensor):
    """When this zone last completed an irrigation run."""

    suffix = "last_irrigation"
    _attr_translation_key = "last_irrigation"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def _update_from_zone(self, zone: dict) -> None:
        self._last_irrigation = _to_aware_datetime(zone.get(const.ZONE_LAST_IRRIGATION))

    @property
    def native_value(self):
        """Return the last run-completion time (None until the zone waters)."""
        return self._last_irrigation


class SmartIrrigationZoneNextIrrigationSensor(SmartIrrigationZoneChildSensor):
    """The next scheduled irrigation run that targets this zone.

    Computed from the recurring schedules (start/finish anchor math included);
    interval schedules have no fixed clock target and are not considered. None
    when no enabled irrigation schedule targets the zone.
    """

    suffix = "next_irrigation"
    _attr_translation_key = "next_irrigation"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, hass: HomeAssistant, entity_id: str, zone: dict) -> None:
        """Initialize and recompute when schedules change."""
        self._next_run = None
        super().__init__(hass, entity_id, zone)
        async_dispatcher_connect(
            hass, const.DOMAIN + "_schedules_updated", self._async_schedules_updated
        )

    @callback
    def _async_schedules_updated(self):
        """Schedules changed — recompute the upcoming run."""
        if self.hass:
            self.async_schedule_update_ha_state(force_refresh=True)

    async def async_update(self):
        """Recompute the next irrigation run targeting this zone."""
        try:
            coordinator = self._hass.data[const.DOMAIN]["coordinator"]
            runs = (
                await coordinator.recurring_schedule_manager.async_get_upcoming_runs()
            )
        except (KeyError, AttributeError):
            return
        next_run = None
        for run in runs:
            if run.get("action") != "irrigate" or not run.get("next_run_utc"):
                continue
            zones = run.get("zones", "all")
            if zones != "all":
                try:
                    if int(self._zone_id) not in {int(z) for z in zones}:
                        continue
                except (TypeError, ValueError):
                    continue
            when = _to_aware_datetime(run["next_run_utc"])
            if when and (next_run is None or when < next_run):
                next_run = when
        self._next_run = next_run

    @property
    def native_value(self):
        """Return the next scheduled run (None when nothing is scheduled)."""
        return self._next_run


class SmartIrrigationZoneWaterUsageSensor(SmartIrrigationZoneChildSensor):
    """Cumulative water delivered by this zone (WS-2).

    Backed by the persisted ``water_used_total`` store field (litres), so it is
    monotonic and survives restarts. ``device_class: water`` +
    ``state_class: total_increasing`` lets HA build long-term statistics and an
    Energy-style usage dashboard for free, and converts L → gal on imperial.
    """

    suffix = "water_used"
    _attr_translation_key = "water_used"
    _attr_icon = "mdi:water-pump"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def _update_from_zone(self, zone: dict) -> None:
        self._total = zone.get(const.ZONE_WATER_USED_TOTAL) or 0.0

    @property
    def native_unit_of_measurement(self) -> str:
        """Stored canonically in litres; HA converts for imperial users."""
        return "L"

    @property
    def native_value(self) -> float:
        """Return the cumulative litres delivered."""
        return round(self._total, 2)

    @property
    def suggested_display_precision(self) -> int:
        """One decimal place is plenty for a running total."""
        return 1


class SmartIrrigationZoneLastWaterUsageSensor(SmartIrrigationZoneChildSensor):
    """Water delivered by this zone's most recent watering cycle (issue #37).

    Derived from the newest run-log entry that actually delivered water
    (``volume_l > 0``), so skipped/failed cycles never overwrite it. Unlike the
    cumulative ``water_used`` total this is a per-cycle snapshot, handy as a
    notification trigger ("zone X used Y litres last run"). The run timestamp,
    duration, trigger and result are exposed as attributes for the message.

    No ``state_class`` is set: the ``WATER`` device class only permits
    ``total``/``total_increasing`` (or none), and this per-cycle value neither
    sums nor monotonically increases, so it must stay stateless (issue #39).
    """

    suffix = "last_water_used"
    _attr_translation_key = "last_water_used"
    _attr_icon = "mdi:water-sync"
    _attr_device_class = SensorDeviceClass.WATER

    def _update_from_zone(self, zone: dict) -> None:
        self._entry = self._latest_watering_entry(zone)

    @staticmethod
    def _latest_watering_entry(zone: dict) -> dict | None:
        """Return the newest run-log entry that delivered water (newest first)."""
        for entry in zone.get(const.ZONE_RUN_LOG) or []:
            if (entry.get("volume_l") or 0.0) > 0:
                return entry
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Stored canonically in litres; HA converts for imperial users."""
        return "L"

    @property
    def native_value(self) -> float | None:
        """Return the litres delivered by the last watering cycle (None if never)."""
        if not self._entry:
            return None
        return round(self._entry.get("volume_l") or 0.0, 2)

    @property
    def suggested_display_precision(self) -> int:
        """One decimal place matches the cumulative usage sensor."""
        return 1

    @property
    def extra_state_attributes(self) -> dict:
        """Zone identity plus when/how long/why the last cycle ran."""
        entry = self._entry or {}
        return {
            **super().extra_state_attributes,
            "timestamp": entry.get("ts"),
            "duration": entry.get("actual_s"),
            "trigger": entry.get("trigger"),
            "result": entry.get("result"),
        }


# (zone key, entity suffix (data key / unique_id), translation_key, kind)
ZONE_DIAGNOSTIC_SENSORS = (
    (const.ZONE_LAST_CALCULATED, "last_calculated", "last_calculated", "timestamp"),
    (const.ZONE_LAST_UPDATED, "last_updated", "last_weather_update", "timestamp"),
    (
        const.ZONE_NUMBER_OF_DATA_POINTS,
        "data_points",
        "weather_data_points",
        "number",
    ),
    (
        const.ZONE_CURRENT_DRAINAGE,
        "current_drainage",
        "drainage",
        "number",
    ),
)


class SmartIrrigationZoneDiagnosticSensor(SmartIrrigationZoneChildSensor):
    """Per-zone diagnostic sensor (default-disabled, diagnostic category)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        hass: HomeAssistant,
        entity_id: str,
        zone: dict,
        zone_key: str,
        suffix: str,
        translation_key: str,
        kind: str,
    ) -> None:
        """Initialize from the diagnostic spec tuple."""
        self._zone_key = zone_key
        self.suffix = suffix
        self._attr_translation_key = translation_key
        self._kind = kind
        super().__init__(hass, entity_id, zone)

    def _update_from_zone(self, zone: dict) -> None:
        value = zone.get(self._zone_key)
        if self._kind == "timestamp":
            self._value = _to_aware_datetime(value)
        else:
            self._value = value

    @property
    def device_class(self):
        """Timestamps get the timestamp device class."""
        return SensorDeviceClass.TIMESTAMP if self._kind == "timestamp" else None

    @property
    def state_class(self):
        """Numeric diagnostics are measurements."""
        return SensorStateClass.MEASUREMENT if self._kind == "number" else None

    @property
    def native_value(self):
        """Return the diagnostic value."""
        return self._value
