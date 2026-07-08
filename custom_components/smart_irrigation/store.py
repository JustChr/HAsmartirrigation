"""Storage and management for Smart Irrigation configuration, zones, modules, and mappings."""

import datetime
import logging
import uuid
from collections import OrderedDict
from collections.abc import MutableMapping
from typing import cast

import attr
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.loader import bind_hass
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import (
    ATTR_NEW_BUCKET_VALUE,
    ATTR_NEW_MULTIPLIER_VALUE,
    CONF_AUTO_CALC_ENABLED,
    CONF_AUTO_UPDATE_DELAY,
    CONF_AUTO_UPDATE_ENABLED,
    CONF_AUTO_UPDATE_INTERVAL,
    CONF_AUTO_UPDATE_SCHEDULE,
    CONF_CALC_TIME,
    CONF_DAYS_BETWEEN_IRRIGATION,
    CONF_DAYS_SINCE_LAST_IRRIGATION,
    CONF_DEFAULT_AUTO_CALC_ENABLED,
    CONF_DEFAULT_AUTO_UPDATE_DELAY,
    CONF_DEFAULT_AUTO_UPDATE_ENABLED,
    CONF_DEFAULT_AUTO_UPDATE_INTERVAL,
    CONF_DEFAULT_AUTO_UPDATE_SCHEDULE,
    CONF_DEFAULT_BUCKET_THRESHOLD,
    CONF_DEFAULT_CALC_TIME,
    CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
    CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
    CONF_DEFAULT_DISTRIBUTORS_ENABLED,
    CONF_DEFAULT_DRAINAGE_RATE,
    CONF_DEFAULT_FORECAST_WEIGHTING_ENABLED,
    CONF_DEFAULT_FREEZE_THRESHOLD,
    CONF_DEFAULT_KC,
    CONF_DEFAULT_LIVE_ESTIMATE_ENABLED,
    CONF_DEFAULT_MANUAL_COORDINATES_ENABLED,
    CONF_DEFAULT_MAXIMUM_BUCKET,
    CONF_DEFAULT_MAXIMUM_DURATION,
    CONF_DEFAULT_OBSERVED_WATERING_ENABLED,
    CONF_DEFAULT_PLANT_TYPE,
    CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS,
    CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM,
    CONF_DEFAULT_RAIN_DELAY_UNTIL,
    CONF_DEFAULT_RAIN_SENSOR,
    CONF_DEFAULT_RECURRING_SCHEDULES,
    CONF_DEFAULT_SKIP_FREEZE_ENABLED,
    CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION,
    CONF_DEFAULT_SKIP_TEMP_ENABLED,
    CONF_DEFAULT_SKIP_WIND_ENABLED,
    CONF_DEFAULT_TEMP_THRESHOLD,
    CONF_DEFAULT_USE_WEATHER_SERVICE,
    CONF_DEFAULT_WEATHER_SERVICE,
    CONF_DEFAULT_WIND_THRESHOLD,
    CONF_DEFAULT_ZONE_SEQUENCING,
    CONF_DEFAULT_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION,
    CONF_DEFAULT_ZONE_SEQUENCING_MIN_ABSORPTION_TIME,
    CONF_DISTRIBUTORS_ENABLED,
    CONF_FORECAST_WEIGHTING_ENABLED,
    CONF_FREEZE_THRESHOLD,
    CONF_IMPERIAL,
    CONF_LEGACY_FRESH_DURATION_ENABLED,
    CONF_LEGACY_LIVE_DURATION_ENABLED,
    CONF_LIVE_ESTIMATE_ENABLED,
    CONF_METRIC,
    CONF_OBSERVED_WATERING_ENABLED,
    CONF_PRECIPITATION_FORECAST_DAYS,
    CONF_PRECIPITATION_THRESHOLD_MM,
    CONF_RAIN_DELAY_UNTIL,
    CONF_RAIN_SENSOR,
    CONF_RECURRING_SCHEDULES,
    CONF_SKIP_FREEZE_ENABLED,
    CONF_SKIP_IRRIGATION_ON_PRECIPITATION,
    CONF_SKIP_TEMP_ENABLED,
    CONF_SKIP_WIND_ENABLED,
    CONF_TEMP_THRESHOLD,
    CONF_UNITS,
    CONF_USE_WEATHER_SERVICE,
    CONF_WEATHER_SERVICE,
    CONF_WEATHER_SERVICE_OWM,
    CONF_WIND_THRESHOLD,
    CONF_ZONE_SEQUENCING,
    CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION,
    CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME,
    DOMAIN,
    MAPPING_CONF_SENSOR,
    MAPPING_CONF_SOURCE,
    MAPPING_CONF_SOURCE_NONE,
    MAPPING_CONF_SOURCE_SENSOR,
    MAPPING_CONF_SOURCE_WEATHER_SERVICE,
    MAPPING_CONF_UNIT,
    MAPPING_CURRENT_PRECIPITATION,
    MAPPING_DATA,
    MAPPING_DATA_LAST_CALCULATION,
    MAPPING_DATA_LAST_ENTRY,
    MAPPING_DATA_LAST_UPDATED,
    MAPPING_DEWPOINT,
    MAPPING_EVAPOTRANSPIRATION,
    MAPPING_HUMIDITY,
    MAPPING_ID,
    MAPPING_MAPPINGS,
    MAPPING_MAX_TEMP,
    MAPPING_MIN_TEMP,
    MAPPING_NAME,
    MAPPING_PRECIPITATION,
    MAPPING_PRESSURE,
    MAPPING_SOLRAD,
    MAPPING_TEMPERATURE,
    MAPPING_WINDSPEED,
    MODULE_CONFIG,
    MODULE_DESCRIPTION,
    MODULE_DIR,
    MODULE_ID,
    MODULE_NAME,
    MODULE_SCHEMA,
    SCHEDULE_CONF_ACTION,
    ZONE_BUCKET,
    ZONE_BUCKET_THRESHOLD,
    ZONE_CURRENT_DRAINAGE,
    ZONE_DELTA,
    ZONE_DRAINAGE_RATE,
    ZONE_DURATION,
    ZONE_FLOW_SENSOR,
    ZONE_ID,
    ZONE_IRRIGATION_TARGET_BUCKET,
    ZONE_KC,
    ZONE_LAST_CALCULATED,
    ZONE_LAST_CONSUMED,
    ZONE_LAST_IRRIGATION,
    ZONE_LAST_UPDATED,
    ZONE_LEAD_TIME,
    ZONE_LINKED_ENTITY,
    ZONE_MAPPING,
    ZONE_MAXIMUM_BUCKET,
    ZONE_MAXIMUM_DURATION,
    ZONE_MODULE,
    ZONE_MULTIPLIER,
    ZONE_NAME,
    ZONE_NUMBER_OF_DATA_POINTS,
    ZONE_PLANT_TYPE,
    ZONE_RUN_LOG,
    ZONE_SIZE,
    ZONE_STATE,
    ZONE_STATE_AUTOMATIC,
    ZONE_THROUGHPUT,
    ZONE_WATER_USED_TOTAL,
)
from .helpers import loadModules
from .localize import localize

_LOGGER = logging.getLogger(__name__)

DATA_REGISTRY = f"{DOMAIN}_storage"
STORAGE_KEY = f"{DOMAIN}.storage"
STORAGE_VERSION = 11
SAVE_DELAY = 0


@attr.s(slots=True, frozen=True)
class ZoneEntry:
    """Zone storage Entry."""

    id = attr.ib(type=int, default=None)
    name = attr.ib(type=str, default=None)
    size = attr.ib(type=float, default=0.0)
    throughput = attr.ib(type=float, default=0.0)
    state = attr.ib(type=str, default="automatic")
    bucket = attr.ib(type=float, default=0)
    delta = attr.ib(type=float, default=0)
    duration = attr.ib(type=float, default=0)
    module = attr.ib(type=str, default=None)
    multiplier = attr.ib(type=float, default=1)
    explanation = attr.ib(type=str, default=None)
    mapping = attr.ib(type=str, default=None)
    lead_time = attr.ib(type=float, default=None)
    maximum_duration = attr.ib(type=float, default=CONF_DEFAULT_MAXIMUM_DURATION)
    maximum_bucket = attr.ib(type=float, default=CONF_DEFAULT_MAXIMUM_BUCKET)
    last_calculated = attr.ib(type=datetime, default=None)
    # Per-zone consumption watermark for the shared mapping weather buffer.
    last_consumed_at = attr.ib(type=datetime, default=None)
    last_updated = attr.ib(type=datetime, default=None)
    # When this zone last actually irrigated (set by the runner). Persisted so
    # the "Last irrigation" sensor survives restarts.
    last_irrigation = attr.ib(type=datetime, default=None)
    number_of_data_points = attr.ib(type=int, default=0)
    drainage_rate = attr.ib(type=float, default=CONF_DEFAULT_DRAINAGE_RATE)
    current_drainage = attr.ib(type=float, default=0)
    # Crop coefficient (WS-4): scales the ET0 term only at calc time; default 1.0
    # = reference grass ET (behaviour identical). plant_type is the preset that
    # seeded kc ("custom" once the number is hand-edited).
    kc = attr.ib(type=float, default=CONF_DEFAULT_KC)
    plant_type = attr.ib(type=str, default=CONF_DEFAULT_PLANT_TYPE)
    linked_entity = attr.ib(type=str, default=None)
    bucket_threshold = attr.ib(type=float, default=CONF_DEFAULT_BUCKET_THRESHOLD)
    flow_sensor = attr.ib(type=str, default=None)
    # Bucket level a complete run should leave the zone at (default 0.0 = full
    # replenish). Only non-zero while experimental forecast weighting is on.
    irrigation_target_bucket = attr.ib(type=float, default=0.0)
    # Cumulative water delivered (litres), monotonic; backs the total_increasing
    # usage sensor so it survives restarts (WS-2).
    water_used_total = attr.ib(type=float, default=0.0)
    # Bounded rolling run/skip log (newest first); see const.ZONE_RUN_LOG (WS-2).
    run_log = attr.ib(type=list, factory=list)
    # Self-closing valve mode (per-zone actuation adapter). "classic" = the
    # historic open->sleep->close; "service" = fire run_service, valve self-closes.
    watering_mode = attr.ib(type=str, default="classic")
    run_service = attr.ib(type=str, default=None)
    # Defaults to "duration" so the shipped valve blueprints (whose script field
    # is "duration") work with no extra config.
    duration_field = attr.ib(type=str, default="duration")
    duration_unit = attr.ib(type=str, default="seconds")
    stop_service = attr.ib(type=str, default=None)
    # Optional entity reflecting the real valve/switch state for liveness confirm
    # (poll-only); None = write-only service run, credited optimistically.
    confirm_entity = attr.ib(type=str, default=None)
    # Optional per-zone soil-moisture wet-veto: sensor entity (% moisture, higher
    # = wetter) + threshold. Both None = feature off. See _apply_soil_moisture_veto.
    soil_moisture_sensor = attr.ib(type=str, default=None)
    soil_moisture_threshold = attr.ib(type=float, default=None)
    # Gardena distributor membership. None = a normal, independently-valved zone.
    # A member zone has no own valve/schedule; the distributor owns actuation.
    distributor_id = attr.ib(type=int, default=None)
    outlet_number = attr.ib(type=int, default=None)


@attr.s(slots=True, frozen=True)
class ModuleEntry:
    """Module storage Entry."""

    id = attr.ib(type=int, default=None)
    name = attr.ib(type=str, default=None)
    description = attr.ib(type=str, default=None)
    config = attr.ib(type=str, default=None)
    schema = attr.ib(type=str, default=None)


@attr.s(slots=True, frozen=True)
class MappingEntry:
    """Mapping storage Entry."""

    id = attr.ib(type=int, default=None)
    name = attr.ib(type=str, default=None)
    mappings = attr.ib(type=str, default=None)
    data = attr.ib(type=str, default="[]")
    data_last_updated = attr.ib(type=datetime, default=None)
    data_last_entry = attr.ib(type=str, default={})
    data_last_calculation = attr.ib(type=str, default={})


@attr.s(slots=True, frozen=True)
class Config:
    """(General) Config storage Entry."""

    calctime = attr.ib(type=str, default=CONF_DEFAULT_CALC_TIME)
    units = attr.ib(type=str, default=None)
    use_weather_service = attr.ib(type=bool, default=CONF_DEFAULT_WEATHER_SERVICE)
    weather_service = attr.ib(type=str, default=None)
    autocalcenabled = attr.ib(type=bool, default=CONF_AUTO_CALC_ENABLED)
    autoupdateenabled = attr.ib(type=bool, default=CONF_AUTO_UPDATE_ENABLED)
    autoupdateschedule = attr.ib(type=str, default=CONF_DEFAULT_AUTO_UPDATE_SCHEDULE)
    autoupdatedelay = attr.ib(type=str, default=CONF_DEFAULT_AUTO_UPDATE_DELAY)
    autoupdateinterval = attr.ib(type=str, default=CONF_DEFAULT_AUTO_UPDATE_INTERVAL)
    skip_irrigation_on_precipitation = attr.ib(
        type=bool, default=CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION
    )
    precipitation_threshold_mm = attr.ib(
        type=float, default=CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM
    )
    precipitation_forecast_days = attr.ib(
        type=int, default=CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS
    )
    days_between_irrigation = attr.ib(
        type=int, default=CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION
    )
    days_since_last_irrigation = attr.ib(
        type=int, default=CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION
    )
    recurring_schedules = attr.ib(type=list, default=CONF_DEFAULT_RECURRING_SCHEDULES)
    zone_sequencing = attr.ib(type=str, default=CONF_DEFAULT_ZONE_SEQUENCING)
    zone_sequencing_max_consecutive_duration = attr.ib(
        type=int, default=CONF_DEFAULT_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION
    )
    zone_sequencing_min_absorption_time = attr.ib(
        type=int, default=CONF_DEFAULT_ZONE_SEQUENCING_MIN_ABSORPTION_TIME
    )
    skip_on_temp_enabled = attr.ib(type=bool, default=CONF_DEFAULT_SKIP_TEMP_ENABLED)
    temp_threshold = attr.ib(type=float, default=CONF_DEFAULT_TEMP_THRESHOLD)
    skip_on_wind_enabled = attr.ib(type=bool, default=CONF_DEFAULT_SKIP_WIND_ENABLED)
    wind_threshold = attr.ib(type=float, default=CONF_DEFAULT_WIND_THRESHOLD)
    skip_on_freeze_enabled = attr.ib(
        type=bool, default=CONF_DEFAULT_SKIP_FREEZE_ENABLED
    )
    freeze_threshold = attr.ib(type=float, default=CONF_DEFAULT_FREEZE_THRESHOLD)
    rain_sensor = attr.ib(type=str, default=CONF_DEFAULT_RAIN_SENSOR)
    manual_coordinates_enabled = attr.ib(
        type=bool, default=CONF_DEFAULT_MANUAL_COORDINATES_ENABLED
    )
    manual_latitude = attr.ib(type=float, default=None)
    manual_longitude = attr.ib(type=float, default=None)
    manual_elevation = attr.ib(type=float, default=None)
    # Experimental, opt-in (Setup → Experimental). Off by default.
    forecast_weighting_enabled = attr.ib(
        type=bool, default=CONF_DEFAULT_FORECAST_WEIGHTING_ENABLED
    )
    observed_watering_enabled = attr.ib(
        type=bool, default=CONF_DEFAULT_OBSERVED_WATERING_ENABLED
    )
    live_estimate_enabled = attr.ib(
        type=bool, default=CONF_DEFAULT_LIVE_ESTIMATE_ENABLED
    )
    distributors_enabled = attr.ib(
        type=bool, default=CONF_DEFAULT_DISTRIBUTORS_ENABLED
    )
    # Rain delay / vacation hold (WS-5): ISO-8601 datetime string or None.
    rain_delay_until = attr.ib(type=str, default=CONF_DEFAULT_RAIN_DELAY_UNTIL)
    # Persisted in-flight self-closing valve runs (reboot resilience); list of
    # dicts, see const.CONF_ACTIVE_VALVE_RUNS.
    active_valve_runs = attr.ib(type=list, factory=list)
    # Master switch / pump control (instance-level, fully optional). No entity =
    # HASI never touches the master. off_after=False leaves it powered.
    master_entity = attr.ib(type=str, default=None)
    master_settle_seconds = attr.ib(type=int, default=10)
    master_kick_enabled = attr.ib(type=bool, default=False)
    master_kick_pause_seconds = attr.ib(type=float, default=1.0)
    master_off_after = attr.ib(type=bool, default=False)


@attr.s(slots=True, frozen=True)
class DistributorEntry:
    """Gardena distributor storage Entry (a shared, pressure-driven outlet ring).

    The inlet valve is actuated like a zone (classic / service). ``current_outlet``
    is counted open-loop and persisted after every advance; ``position_state`` and
    ``commissioning_confirmed`` gate whether a scheduled cycle may run. ``active_cycle``
    holds the in-flight-cycle record for restart reconciliation (empty when idle).
    """

    id = attr.ib(type=int, default=None)
    name = attr.ib(type=str, default=None)
    # Inlet-valve actuation, mirroring the zone watering-mode shapes.
    watering_mode = attr.ib(type=str, default="classic")
    inlet_entity = attr.ib(type=str, default=None)
    run_service = attr.ib(type=str, default=None)
    stop_service = attr.ib(type=str, default=None)
    duration_field = attr.ib(type=str, default="duration")
    duration_unit = attr.ib(type=str, default="seconds")
    # Shared sensors, physically on the distributor inlet.
    confirm_entity = attr.ib(type=str, default=None)
    flow_sensor = attr.ib(type=str, default=None)
    # Timing (seconds); hard floor enforced by the engine (spec 4.5).
    pause_seconds = attr.ib(type=int, default=300)
    skip_pulse_seconds = attr.ib(type=int, default=30)
    # Open-loop position + trust state. Fresh distributors start uncertain (4.2).
    current_outlet = attr.ib(type=int, default=1)
    position_state = attr.ib(type=str, default="uncertain")
    notify_target = attr.ib(type=str, default=None)
    use_master = attr.ib(type=bool, default=True)
    # Opt-in: watch the inlet valve for foreign pulses (early-stop + inlet-watch,
    # E3). Default off so existing distributors keep their current behaviour; the
    # watcher is wired up in a later task.
    watch_inlet = attr.ib(type=bool, default=False)
    # Inlet-watch reaction to a foreign inlet pulse (E4): count/warn/ignore.
    # Legacy watch_inlet is derived into this in the load path below.
    watch_mode = attr.ib(type=str, default="ignore")
    # Commissioning gate: no scheduled watering until confirmed (5.1); the single
    # "armed" switch, auto-cleared on any transition to uncertain (7).
    commissioning_confirmed = attr.ib(type=bool, default=False)
    # Distributor-local recurring schedules (wired in Plan B).
    schedules = attr.ib(type=list, factory=list)
    # In-flight cycle record for restart reconciliation (empty = idle).
    active_cycle = attr.ib(type=dict, factory=dict)


class MigratableStore(Store):
    """Store subclass that supports migration for Smart Irrigation storage."""

    async def _async_migrate_func(self, old_version, data: dict):
        """Migration function for Smart Irrigation storage.

        This function ALWAYS runs on version mismatch to ensure config compatibility.
        It performs critical tasks:
        1. Migrates old config keys to new format
        2. Adds missing required fields with defaults
        3. Strips unrecognized config keys to prevent TypeError on Config initialization

        The stripping step is essential because old versions or corrupted configs
        may contain keys that don't match the current Config class attributes,
        which would cause TypeError during Config(**config_data) calls.
        """
        if old_version == 3:
            if "config" in data:
                if "use_owm" in data["config"]:
                    data["config"]["use_weather_service"] = data["config"].pop(
                        "use_owm"
                    )
                if data["config"]["use_weather_service"]:
                    data["config"]["weather_service"] = CONF_WEATHER_SERVICE_OWM
        if old_version <= 4:
            if "config" in data:
                # Add weather skip configuration if missing
                if CONF_SKIP_IRRIGATION_ON_PRECIPITATION not in data["config"]:
                    data["config"][
                        CONF_SKIP_IRRIGATION_ON_PRECIPITATION
                    ] = CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION
                if CONF_PRECIPITATION_THRESHOLD_MM not in data["config"]:
                    data["config"][
                        CONF_PRECIPITATION_THRESHOLD_MM
                    ] = CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM
                if CONF_DAYS_BETWEEN_IRRIGATION not in data["config"]:
                    data["config"][
                        CONF_DAYS_BETWEEN_IRRIGATION
                    ] = CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION
                if CONF_DAYS_SINCE_LAST_IRRIGATION not in data["config"]:
                    data["config"][
                        CONF_DAYS_SINCE_LAST_IRRIGATION
                    ] = CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION

        if old_version <= 6:
            # v6→v7: migrate irrigation_start_triggers to recurring_schedules
            if "config" in data:
                triggers = data["config"].pop("irrigation_start_triggers", [])
                existing_schedules = data["config"].get("recurring_schedules", [])
                for t in triggers:
                    schedule = {
                        "id": f"schedule_{uuid.uuid4().hex[:8]}",
                        "name": t.get("name", "Migrated trigger"),
                        "type": t.get("type", "sunrise"),
                        "enabled": t.get("enabled", True),
                        "action": "irrigate",
                        "zones": "all",
                        "offset_minutes": t.get("offset_minutes", 0),
                        "account_for_duration": t.get("account_for_duration", True),
                    }
                    if t.get("type") == "solar_azimuth":
                        schedule["azimuth_angle"] = t.get("azimuth_angle", 90)
                    existing_schedules.append(schedule)
                data["config"]["recurring_schedules"] = existing_schedules

        if old_version <= 8:
            # v9: self-closing valve mode. Default every zone to classic and seed
            # the empty in-flight-run list. Additive only — no data moves.
            for zone in data.get("zones", []):
                zone.setdefault("watering_mode", "classic")
                zone.setdefault("duration_unit", "seconds")
            data.setdefault("config", {}).setdefault("active_valve_runs", [])

        if old_version <= 9:
            # v10: optional master switch / pump control (all off by default).
            cfg = data.setdefault("config", {})
            cfg.setdefault("master_entity", None)
            cfg.setdefault("master_settle_seconds", 10)
            cfg.setdefault("master_kick_enabled", False)
            cfg.setdefault("master_kick_pause_seconds", 1.0)
            cfg.setdefault("master_off_after", False)

        if old_version <= 10:
            # v11: Gardena distributor support. Additive only — create the empty
            # distributors collection and the zone membership fields. No config
            # keys are added (distributors are a top-level collection), so the
            # config-allowlist strip below leaves them untouched.
            data.setdefault("distributors", [])
            for zone in data.get("zones", []):
                zone.setdefault("distributor_id", None)
                zone.setdefault("outlet_number", None)

        # CRITICAL: Always ensure required fields are present and strip unrecognized keys
        # This prevents TypeError when Config(**config_data) is called
        if "config" in data:
            # Ensure all required fields are present with defaults
            if CONF_SKIP_IRRIGATION_ON_PRECIPITATION not in data["config"]:
                data["config"][
                    CONF_SKIP_IRRIGATION_ON_PRECIPITATION
                ] = CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION
            if CONF_PRECIPITATION_THRESHOLD_MM not in data["config"]:
                data["config"][
                    CONF_PRECIPITATION_THRESHOLD_MM
                ] = CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM
            if CONF_PRECIPITATION_FORECAST_DAYS not in data["config"]:
                data["config"][
                    CONF_PRECIPITATION_FORECAST_DAYS
                ] = CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS
            if CONF_DAYS_BETWEEN_IRRIGATION not in data["config"]:
                data["config"][
                    CONF_DAYS_BETWEEN_IRRIGATION
                ] = CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION
            if CONF_DAYS_SINCE_LAST_IRRIGATION not in data["config"]:
                data["config"][
                    CONF_DAYS_SINCE_LAST_IRRIGATION
                ] = CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION
            if CONF_ZONE_SEQUENCING not in data["config"]:
                data["config"][CONF_ZONE_SEQUENCING] = CONF_DEFAULT_ZONE_SEQUENCING
            if CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION not in data["config"]:
                data["config"][
                    CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION
                ] = CONF_DEFAULT_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION
            if CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME not in data["config"]:
                data["config"][
                    CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME
                ] = CONF_DEFAULT_ZONE_SEQUENCING_MIN_ABSORPTION_TIME
            if CONF_SKIP_TEMP_ENABLED not in data["config"]:
                data["config"][CONF_SKIP_TEMP_ENABLED] = CONF_DEFAULT_SKIP_TEMP_ENABLED
            if CONF_TEMP_THRESHOLD not in data["config"]:
                data["config"][CONF_TEMP_THRESHOLD] = CONF_DEFAULT_TEMP_THRESHOLD
            if CONF_SKIP_WIND_ENABLED not in data["config"]:
                data["config"][CONF_SKIP_WIND_ENABLED] = CONF_DEFAULT_SKIP_WIND_ENABLED
            if CONF_WIND_THRESHOLD not in data["config"]:
                data["config"][CONF_WIND_THRESHOLD] = CONF_DEFAULT_WIND_THRESHOLD
            if CONF_RAIN_SENSOR not in data["config"]:
                data["config"][CONF_RAIN_SENSOR] = CONF_DEFAULT_RAIN_SENSOR

            # Get valid field names from Config class to filter out unrecognized keys
            valid_fields = set(attr.fields_dict(Config).keys())
            original_keys = set(data["config"].keys())

            # Filter config to only include recognized fields
            filtered_config = {
                k: v for k, v in data["config"].items() if k in valid_fields
            }
            removed_keys = original_keys - set(filtered_config.keys())

            if removed_keys:
                _LOGGER.warning(
                    "Removed unrecognized config keys during migration: %s",
                    list(removed_keys),
                )

            data["config"] = filtered_config

        return data


class SmartIrrigationStorage:
    """Class to hold Smart Irrigation configuration data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        self.hass = hass
        self.config: Config = Config()
        self.zones: MutableMapping[ZoneEntry] = {}
        self.modules: MutableMapping[ModuleEntry] = {}
        self.mappings: MutableMapping[MappingEntry] = {}
        self.distributors: MutableMapping[DistributorEntry] = {}
        self._store = MigratableStore(hass, STORAGE_VERSION, STORAGE_KEY)

    async def async_load(self) -> None:
        """Load the registry of schedule entries."""
        data = await self._store.async_load()
        config: Config = Config(
            calctime=CONF_DEFAULT_CALC_TIME,
            units=(
                CONF_METRIC
                if self.hass.config.units is METRIC_SYSTEM
                else CONF_IMPERIAL
            ),
            use_weather_service=CONF_DEFAULT_USE_WEATHER_SERVICE,
            weather_service=CONF_DEFAULT_WEATHER_SERVICE,
            autocalcenabled=CONF_DEFAULT_AUTO_CALC_ENABLED,
            autoupdateenabled=CONF_DEFAULT_AUTO_UPDATE_ENABLED,
            autoupdateschedule=CONF_DEFAULT_AUTO_UPDATE_SCHEDULE,
            autoupdatedelay=CONF_DEFAULT_AUTO_UPDATE_DELAY,
            autoupdateinterval=CONF_DEFAULT_AUTO_UPDATE_INTERVAL,
        )
        zones: OrderedDict[str, ZoneEntry] = OrderedDict()
        modules: OrderedDict[str, ModuleEntry] = OrderedDict()
        mappings: OrderedDict[str, MappingEntry] = OrderedDict()
        distributors: OrderedDict[str, DistributorEntry] = OrderedDict()

        if data is not None:
            config = Config(
                calctime=data["config"].get(CONF_CALC_TIME, CONF_DEFAULT_CALC_TIME),
                units=data["config"].get(
                    CONF_UNITS,
                    (
                        CONF_METRIC
                        if self.hass.config.units is METRIC_SYSTEM
                        else CONF_IMPERIAL
                    ),
                ),
                use_weather_service=data["config"].get(
                    CONF_USE_WEATHER_SERVICE, CONF_DEFAULT_USE_WEATHER_SERVICE
                ),
                weather_service=data["config"].get(
                    CONF_WEATHER_SERVICE, CONF_DEFAULT_WEATHER_SERVICE
                ),
                autocalcenabled=data["config"].get(
                    CONF_AUTO_CALC_ENABLED, CONF_DEFAULT_AUTO_CALC_ENABLED
                ),
                autoupdateenabled=data["config"].get(
                    CONF_AUTO_UPDATE_ENABLED, CONF_DEFAULT_AUTO_UPDATE_ENABLED
                ),
                autoupdateschedule=data["config"].get(
                    CONF_AUTO_UPDATE_SCHEDULE, CONF_DEFAULT_AUTO_UPDATE_SCHEDULE
                ),
                autoupdatedelay=data["config"].get(
                    CONF_AUTO_UPDATE_DELAY, CONF_DEFAULT_AUTO_UPDATE_DELAY
                ),
                autoupdateinterval=data["config"].get(
                    CONF_AUTO_UPDATE_INTERVAL, CONF_DEFAULT_AUTO_UPDATE_INTERVAL
                ),
                skip_irrigation_on_precipitation=data["config"].get(
                    CONF_SKIP_IRRIGATION_ON_PRECIPITATION,
                    CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION,
                ),
                precipitation_threshold_mm=data["config"].get(
                    CONF_PRECIPITATION_THRESHOLD_MM,
                    CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM,
                ),
                precipitation_forecast_days=data["config"].get(
                    CONF_PRECIPITATION_FORECAST_DAYS,
                    CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS,
                ),
                days_between_irrigation=data["config"].get(
                    CONF_DAYS_BETWEEN_IRRIGATION,
                    CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
                ),
                days_since_last_irrigation=data["config"].get(
                    CONF_DAYS_SINCE_LAST_IRRIGATION,
                    CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
                ),
                zone_sequencing=data["config"].get(
                    CONF_ZONE_SEQUENCING,
                    CONF_DEFAULT_ZONE_SEQUENCING,
                ),
                zone_sequencing_max_consecutive_duration=data["config"].get(
                    CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION,
                    CONF_DEFAULT_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION,
                ),
                zone_sequencing_min_absorption_time=data["config"].get(
                    CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME,
                    CONF_DEFAULT_ZONE_SEQUENCING_MIN_ABSORPTION_TIME,
                ),
                skip_on_temp_enabled=data["config"].get(
                    CONF_SKIP_TEMP_ENABLED,
                    CONF_DEFAULT_SKIP_TEMP_ENABLED,
                ),
                temp_threshold=data["config"].get(
                    CONF_TEMP_THRESHOLD,
                    CONF_DEFAULT_TEMP_THRESHOLD,
                ),
                skip_on_wind_enabled=data["config"].get(
                    CONF_SKIP_WIND_ENABLED,
                    CONF_DEFAULT_SKIP_WIND_ENABLED,
                ),
                wind_threshold=data["config"].get(
                    CONF_WIND_THRESHOLD,
                    CONF_DEFAULT_WIND_THRESHOLD,
                ),
                skip_on_freeze_enabled=data["config"].get(
                    CONF_SKIP_FREEZE_ENABLED,
                    CONF_DEFAULT_SKIP_FREEZE_ENABLED,
                ),
                freeze_threshold=data["config"].get(
                    CONF_FREEZE_THRESHOLD,
                    CONF_DEFAULT_FREEZE_THRESHOLD,
                ),
                rain_sensor=data["config"].get(
                    CONF_RAIN_SENSOR,
                    CONF_DEFAULT_RAIN_SENSOR,
                ),
                forecast_weighting_enabled=data["config"].get(
                    CONF_FORECAST_WEIGHTING_ENABLED,
                    CONF_DEFAULT_FORECAST_WEIGHTING_ENABLED,
                ),
                observed_watering_enabled=data["config"].get(
                    CONF_OBSERVED_WATERING_ENABLED,
                    CONF_DEFAULT_OBSERVED_WATERING_ENABLED,
                ),
                live_estimate_enabled=data["config"].get(
                    CONF_LIVE_ESTIMATE_ENABLED,
                    # Fall back through the earlier key names so an existing
                    # opt-in survives: live_duration → fresh_duration.
                    data["config"].get(
                        CONF_LEGACY_LIVE_DURATION_ENABLED,
                        data["config"].get(
                            CONF_LEGACY_FRESH_DURATION_ENABLED,
                            CONF_DEFAULT_LIVE_ESTIMATE_ENABLED,
                        ),
                    ),
                ),
                distributors_enabled=data["config"].get(
                    CONF_DISTRIBUTORS_ENABLED,
                    CONF_DEFAULT_DISTRIBUTORS_ENABLED,
                ),
                rain_delay_until=data["config"].get(
                    CONF_RAIN_DELAY_UNTIL, CONF_DEFAULT_RAIN_DELAY_UNTIL
                ),
                # Recurring schedules are irrigation-only now; calculate/update
                # are handled by the global daily settings. Drop any legacy
                # calculate/update schedules on load (they would just duplicate
                # the global tasks).
                recurring_schedules=[
                    s
                    for s in data["config"].get(
                        CONF_RECURRING_SCHEDULES, CONF_DEFAULT_RECURRING_SCHEDULES
                    )
                    if s.get(SCHEDULE_CONF_ACTION) == "irrigate"
                ],
                master_entity=data["config"].get("master_entity", None),
                master_settle_seconds=data["config"].get("master_settle_seconds", 10),
                master_kick_enabled=data["config"].get("master_kick_enabled", False),
                master_kick_pause_seconds=data["config"].get(
                    "master_kick_pause_seconds", 1.0
                ),
                master_off_after=data["config"].get("master_off_after", False),
            )

            if "zones" in data:
                for zone in data["zones"]:
                    zones[zone[ZONE_ID]] = ZoneEntry(
                        id=zone[ZONE_ID],
                        name=zone[ZONE_NAME],
                        size=zone[ZONE_SIZE],
                        throughput=zone[ZONE_THROUGHPUT],
                        state=zone[ZONE_STATE],
                        delta=zone[ZONE_DELTA],
                        bucket=zone[ZONE_BUCKET],
                        duration=zone[ZONE_DURATION],
                        module=zone[ZONE_MODULE],
                        multiplier=zone[ZONE_MULTIPLIER],
                        mapping=zone[ZONE_MAPPING],
                        lead_time=zone[ZONE_LEAD_TIME],
                        maximum_duration=zone.get(
                            ZONE_MAXIMUM_DURATION, CONF_DEFAULT_MAXIMUM_DURATION
                        ),
                        maximum_bucket=zone.get(
                            ZONE_MAXIMUM_BUCKET, CONF_DEFAULT_MAXIMUM_BUCKET
                        ),
                        last_calculated=zone.get(ZONE_LAST_CALCULATED, None),
                        # Migration: existing zones (pre last_consumed_at) inherit
                        # their last_calculated as the consumption watermark; None
                        # falls back to the buffer span at calc time.
                        last_consumed_at=zone.get(
                            ZONE_LAST_CONSUMED,
                            zone.get(ZONE_LAST_CALCULATED, None),
                        ),
                        last_updated=zone.get(ZONE_LAST_UPDATED, None),
                        # Migration: existing zones have no recorded last
                        # irrigation until they next water.
                        last_irrigation=zone.get(ZONE_LAST_IRRIGATION, None),
                        number_of_data_points=zone.get(
                            ZONE_NUMBER_OF_DATA_POINTS, None
                        ),
                        drainage_rate=zone.get(ZONE_DRAINAGE_RATE, None),
                        current_drainage=zone.get(ZONE_CURRENT_DRAINAGE, None),
                        # Migration: pre-WS-4 zones default to Kc 1.0 (reference
                        # ET, behaviour unchanged) with no plant-type preset.
                        kc=zone.get(ZONE_KC, CONF_DEFAULT_KC),
                        plant_type=zone.get(ZONE_PLANT_TYPE, CONF_DEFAULT_PLANT_TYPE),
                        linked_entity=zone.get(ZONE_LINKED_ENTITY, None),
                        bucket_threshold=zone.get(
                            ZONE_BUCKET_THRESHOLD, CONF_DEFAULT_BUCKET_THRESHOLD
                        ),
                        flow_sensor=zone.get(ZONE_FLOW_SENSOR, None),
                        irrigation_target_bucket=zone.get(
                            ZONE_IRRIGATION_TARGET_BUCKET, 0.0
                        ),
                        # Migration: pre-WS-2 zones start with no usage history.
                        water_used_total=zone.get(ZONE_WATER_USED_TOTAL, 0.0),
                        run_log=zone.get(ZONE_RUN_LOG, []) or [],
                        # Self-closing valve mode config — must be hydrated here
                        # or it silently reverts to classic on every reload.
                        watering_mode=zone.get("watering_mode", "classic"),
                        run_service=zone.get("run_service", None),
                        duration_field=zone.get("duration_field", "duration"),
                        duration_unit=zone.get("duration_unit", "seconds"),
                        stop_service=zone.get("stop_service", None),
                        confirm_entity=zone.get("confirm_entity", None),
                        soil_moisture_sensor=zone.get("soil_moisture_sensor", None),
                        soil_moisture_threshold=zone.get(
                            "soil_moisture_threshold", None
                        ),
                        distributor_id=zone.get("distributor_id", None),
                        outlet_number=zone.get("outlet_number", None),
                    )
            if "modules" in data:
                for module in data["modules"]:
                    schema_from_code = None
                    modconfig = None
                    if MODULE_CONFIG in module:
                        modconfig = module[MODULE_CONFIG]
                    # load the calc modules and set up the schema
                    mods = await self.hass.async_add_executor_job(
                        loadModules, MODULE_DIR
                    )
                    for mod in mods:
                        if mods[mod]["class"] == module[MODULE_NAME]:
                            m = getattr(mods[mod]["module"], mods[mod]["class"])
                            inst = m(self.hass, module[MODULE_DESCRIPTION], modconfig)
                            schema_from_code = inst.schema_serialized()
                            break
                    modules[module[MODULE_ID]] = ModuleEntry(
                        id=module[MODULE_ID],
                        name=module[MODULE_NAME],
                        description=module[MODULE_DESCRIPTION],
                        config=modconfig,
                        schema=schema_from_code,
                    )
            if "mappings" in data:
                for mapping in data["mappings"]:
                    the_map = mapping.get(MAPPING_MAPPINGS)
                    # remove max and min temp is present in mapping, they should only be there for old versions.
                    if MAPPING_MAX_TEMP in the_map:
                        the_map.pop(MAPPING_MAX_TEMP)
                    if MAPPING_MIN_TEMP in the_map:
                        the_map.pop(MAPPING_MIN_TEMP)
                    if MAPPING_CURRENT_PRECIPITATION not in the_map:
                        the_map[MAPPING_CURRENT_PRECIPITATION] = {}
                    mappings[mapping[MAPPING_ID]] = MappingEntry(
                        id=mapping[MAPPING_ID],
                        name=mapping[MAPPING_NAME],
                        mappings=the_map,
                        data=mapping.get(MAPPING_DATA),
                        data_last_updated=mapping.get(MAPPING_DATA_LAST_UPDATED, None),
                        data_last_entry=mapping.get(MAPPING_DATA_LAST_ENTRY, {}),
                        data_last_calculation=mapping.get(
                            MAPPING_DATA_LAST_CALCULATION, {}
                        ),
                    )
            if "distributors" in data:
                for dist in data["distributors"]:
                    distributors[dist["id"]] = DistributorEntry(
                        id=dist["id"],
                        name=dist.get("name"),
                        watering_mode=dist.get("watering_mode", "classic"),
                        inlet_entity=dist.get("inlet_entity", None),
                        run_service=dist.get("run_service", None),
                        stop_service=dist.get("stop_service", None),
                        duration_field=dist.get("duration_field", "duration"),
                        duration_unit=dist.get("duration_unit", "seconds"),
                        confirm_entity=dist.get("confirm_entity", None),
                        flow_sensor=dist.get("flow_sensor", None),
                        pause_seconds=dist.get("pause_seconds", 300),
                        skip_pulse_seconds=dist.get("skip_pulse_seconds", 30),
                        current_outlet=dist.get("current_outlet", 1),
                        position_state=dist.get("position_state", "uncertain"),
                        notify_target=dist.get("notify_target", None),
                        use_master=dist.get("use_master", True),
                        # E3: older records predate watch_inlet -> default off.
                        watch_inlet=dist.get("watch_inlet", False),
                        # E4: derive watch_mode from legacy watch_inlet when absent.
                        watch_mode=dist.get("watch_mode")
                        or ("count" if dist.get("watch_inlet") else "ignore"),
                        commissioning_confirmed=dist.get(
                            "commissioning_confirmed", False
                        ),
                        schedules=dist.get("schedules", []) or [],
                        active_cycle=dist.get("active_cycle", {}) or {},
                    )

        self.config = config
        self.zones = zones
        self.modules = modules
        self.mappings = mappings
        self.distributors = distributors

    async def set_up_factory_defaults(self):
        """Set up factory default zones, modules, and mappings if they do not exist."""
        if not self.zones:
            await self.async_factory_default_zones()
        if not self.modules:
            await self.async_factory_default_modules()
        if not self.mappings:
            await self.async_factory_default_mappings()

    async def async_factory_default_zones(self):
        """Set up factory default zones if none exist."""
        return

    async def async_factory_default_modules(self):
        """Set up factory default modules if none exist."""
        schema_from_code = None
        module0schema = None
        module1schema = None
        mods = await self.hass.async_add_executor_job(loadModules, MODULE_DIR)
        for mod in mods:
            if mods[mod]["class"] in ["PyETO", "Static"]:
                m = getattr(mods[mod]["module"], mods[mod]["class"])
                inst = m(self.hass, {}, {})
                schema_from_code = inst.schema_serialized()
                if mods[mod]["class"] == "PyETO":
                    module0schema = schema_from_code
                elif mods[mod]["class"] == "Static":
                    module1schema = schema_from_code
        module0 = ModuleEntry(
            **{
                MODULE_ID: 0,
                MODULE_NAME: "PyETO",
                MODULE_DESCRIPTION: await localize(
                    "calcmodules.pyeto.description", self.hass.config.language
                )
                + ".",
                MODULE_SCHEMA: module0schema,
            }
        )
        module1 = ModuleEntry(
            **{
                MODULE_ID: 1,
                MODULE_NAME: "Static",
                MODULE_DESCRIPTION: await localize(
                    "calcmodules.static.description", self.hass.config.language
                )
                + ".",
                MODULE_SCHEMA: module1schema,
            }
        )
        self.modules[0] = module0
        self.modules[1] = module1
        self.async_schedule_save()

    async def async_factory_default_mappings(self):
        """Set up factory default mappings if none exist."""
        # this should be Weather Service mapping if a weather service is defined
        mapping_source = ""
        if self.config.use_weather_service:
            # we're using a weather service
            mapping_source = MAPPING_CONF_SOURCE_WEATHER_SERVICE
        else:
            mapping_source = MAPPING_CONF_SOURCE_SENSOR
        mappings = [
            MAPPING_DEWPOINT,
            MAPPING_EVAPOTRANSPIRATION,
            MAPPING_HUMIDITY,
            MAPPING_PRECIPITATION,
            MAPPING_CURRENT_PRECIPITATION,
            MAPPING_PRESSURE,
            MAPPING_SOLRAD,
            MAPPING_TEMPERATURE,
            MAPPING_WINDSPEED,
        ]
        conf = {}
        for mapping_key in mappings:
            map_source = mapping_source
            # evapotranspiration and solrad can only come from a sensor or none
            if mapping_key in [MAPPING_EVAPOTRANSPIRATION, MAPPING_SOLRAD]:
                if self.config.use_weather_service:
                    map_source = MAPPING_CONF_SOURCE_NONE
                else:
                    map_source = MAPPING_CONF_SOURCE_SENSOR
            conf[mapping_key] = {
                MAPPING_CONF_SOURCE: map_source,
                MAPPING_CONF_SENSOR: "",
                MAPPING_CONF_UNIT: "",
            }
        new_mapping1 = MappingEntry(
            **{
                MAPPING_ID: 0,
                MAPPING_NAME: await localize(
                    "defaults.default-mapping", self.hass.config.language
                ),
                MAPPING_MAPPINGS: conf,
            }
        )
        self.mappings[0] = new_mapping1
        self.async_schedule_save()

    @callback
    def async_schedule_save(self) -> None:
        """Schedule saving the registry of Smart Irrigation."""
        self._store.async_delay_save(self._data_to_save, SAVE_DELAY)

    async def async_save(self) -> None:
        """Save the registry of Smart Irrigation."""
        await self._store.async_save(self._data_to_save())

    @callback
    def _data_to_save(self) -> dict:
        """Return data for the registry for Smart Irrigation to store in a file."""
        store_data = {
            "config": attr.asdict(self.config),
        }

        store_data["zones"] = [attr.asdict(entry) for entry in self.zones.values()]
        store_data["modules"] = [attr.asdict(entry) for entry in self.modules.values()]
        store_data["mappings"] = [
            attr.asdict(entry) for entry in self.mappings.values()
        ]
        store_data["distributors"] = [
            attr.asdict(entry) for entry in self.distributors.values()
        ]
        return store_data

    async def async_delete(self):
        """Delete config."""
        _LOGGER.warning("Removing Smart Irrigation configuration data!")
        await self._store.async_remove()
        # self.config = Config()
        # await self.async_factory_default_zones()
        # await self.async_factory_default_modules()

    @callback
    def get_config(self):
        """Return the current configuration as a dictionary."""
        return attr.asdict(self.config)

    async def async_get_config(self):
        """Return the current configuration as a dictionary asynchronously."""
        return attr.asdict(self.config)

    async def async_update_config(self, changes: dict):
        """Update existing config."""

        old = self.config
        changes.pop("id", None)
        # Only pass fields that Config actually knows about; extra keys from the
        # frontend (e.g. manual_coordinates_enabled) cause TypeError in attr.evolve.
        valid_fields = set(attr.fields_dict(type(old)).keys())
        filtered = {k: v for k, v in changes.items() if k in valid_fields}
        new = self.config = attr.evolve(old, **filtered)
        self.async_schedule_save()
        return attr.asdict(new)

    @callback
    def get_zone(self, zone_id: int) -> ZoneEntry:
        """Get an existing ZoneEntry by id."""
        res = self.zones.get(int(zone_id))
        return attr.asdict(res) if res else None

    @callback
    def get_zones(self):
        """Sync snapshot of all zones (dicts), for entity reads."""
        return [attr.asdict(z) for z in self.zones.values()]

    async def async_get_zones(self):
        """Get all ZoneEntries."""
        return [attr.asdict(val) for val in self.zones.values()]

    async def async_create_zone(self, data: dict) -> ZoneEntry:
        """Create a new ZoneEntry."""
        # Drop unknown keys (an older or forward client may send a field this
        # version doesn't have) so a stray key can't raise TypeError on construction.
        valid_fields = set(attr.fields_dict(ZoneEntry).keys())
        new_zone = ZoneEntry(**{k: v for k, v in data.items() if k in valid_fields})
        if not new_zone.id:
            zones = await self.async_get_zones()
            new_zone = attr.evolve(new_zone, id=self.generate_next_id(zones))
        # Anchor the consumption watermark at creation time so a brand-new zone's
        # first calculation only covers weather data collected from now on (not a
        # backlog of up to the 7-day buffer).
        if new_zone.last_consumed_at is None:
            new_zone = attr.evolve(new_zone, last_consumed_at=datetime.datetime.now())
        self.zones[int(new_zone.id)] = new_zone
        self.async_schedule_save()
        return attr.asdict(new_zone)

    async def async_delete_zone(self, zone_id: int) -> None:
        """Delete ZoneEntry."""
        zone_id = int(zone_id)
        if zone_id in self.zones:
            del self.zones[zone_id]
            self.async_schedule_save()
            return True
        return False

    async def async_update_zone(self, zone_id: int, changes: dict) -> ZoneEntry:
        """Update existing zone."""
        zone_id = int(zone_id)
        old = self.zones[zone_id]
        if changes:
            # handle multiplier value change
            if ATTR_NEW_MULTIPLIER_VALUE in changes:
                changes[ZONE_MULTIPLIER] = changes[ATTR_NEW_MULTIPLIER_VALUE]
                changes.pop(ATTR_NEW_MULTIPLIER_VALUE)
            # handle bucket value change
            if ATTR_NEW_BUCKET_VALUE in changes:
                changes[ZONE_BUCKET] = changes[ATTR_NEW_BUCKET_VALUE]
                changes.pop(ATTR_NEW_BUCKET_VALUE)
            # apply maximum bucket value
            if (
                ZONE_MAXIMUM_BUCKET in changes
                and changes[ZONE_MAXIMUM_BUCKET] is not None
                and changes[ZONE_BUCKET] is not None
                and changes[ZONE_BUCKET] > changes[ZONE_MAXIMUM_BUCKET]
            ):
                changes[ZONE_BUCKET] = changes[ZONE_MAXIMUM_BUCKET]
            # if bucket on zone is 0, then duration should be 0, but only if zone is automatic
            if (
                ZONE_BUCKET in changes
                and changes[ZONE_BUCKET] == 0
                and old.state == ZONE_STATE_AUTOMATIC
            ):
                changes[ZONE_DURATION] = 0
            changes.pop("id", None)
            # Only keep changes that are valid attributes of the ZoneEntry
            valid_fields = set(attr.fields_dict(type(old)).keys())
            filtered_changes = {k: v for k, v in changes.items() if k in valid_fields}
            new = self.zones[zone_id] = attr.evolve(old, **filtered_changes)
        else:
            new = old
        self.async_schedule_save()
        return attr.asdict(new)

    @callback
    def get_distributor(self, distributor_id) -> "DistributorEntry":
        """Get an existing DistributorEntry by id."""
        if distributor_id is not None:
            res = self.distributors.get(int(distributor_id))
            return attr.asdict(res) if res else None
        return None

    async def async_get_distributors(self):
        """Get all DistributorEntries."""
        return [attr.asdict(val) for val in self.distributors.values()]

    async def async_create_distributor(self, data: dict) -> "DistributorEntry":
        """Create a new DistributorEntry (unknown keys dropped)."""
        valid_fields = set(attr.fields_dict(DistributorEntry).keys())
        new_dist = DistributorEntry(
            **{k: v for k, v in data.items() if k in valid_fields}
        )
        if not new_dist.id:
            distributors = await self.async_get_distributors()
            new_dist = attr.evolve(new_dist, id=self.generate_next_id(distributors))
        self.distributors[int(new_dist.id)] = new_dist
        self.async_schedule_save()
        return attr.asdict(new_dist)

    async def async_delete_distributor(self, distributor_id) -> bool:
        """Delete a DistributorEntry."""
        distributor_id = int(distributor_id)
        if distributor_id in self.distributors:
            del self.distributors[distributor_id]
            self.async_schedule_save()
            return True
        return False

    async def async_update_distributor(
        self, distributor_id, changes: dict
    ) -> "DistributorEntry":
        """Update an existing distributor (unknown keys dropped)."""
        distributor_id = int(distributor_id)
        old = self.distributors[distributor_id]
        changes.pop("id", None)
        valid_fields = set(attr.fields_dict(type(old)).keys())
        filtered = {k: v for k, v in changes.items() if k in valid_fields}
        new = self.distributors[distributor_id] = attr.evolve(old, **filtered)
        self.async_schedule_save()
        return attr.asdict(new)

    @callback
    def get_module(self, module_id: int) -> ModuleEntry:
        """Get an existing ModuleEntry by id."""
        if module_id is not None:
            res = self.modules.get(int(module_id))
            return attr.asdict(res) if res else None
        return None

    async def async_get_modules(self):
        """Get all ModuleEntries."""
        return [attr.asdict(val) for val in self.modules.values()]

    async def async_create_module(self, data: dict) -> ModuleEntry:
        """Create a new ModuleEntry."""
        new_module = ModuleEntry(**data)
        if not new_module.id:
            modules = await self.async_get_modules()
            new_module = attr.evolve(new_module, id=self.generate_next_id(modules))
        self.modules[int(new_module.id)] = new_module
        self.async_schedule_save()
        return attr.asdict(new_module)

    async def async_delete_module(self, module_id: int) -> None:
        """Delete ModuleEntry."""
        if int(module_id) in self.modules:
            del self.modules[int(module_id)]
            self.async_schedule_save()
            return True
        return False

    async def async_update_module(self, module_id: int, changes: dict) -> ModuleEntry:
        """Update existing module."""
        module_id = int(module_id)
        old = self.modules[module_id]
        changes.pop("id", None)
        new = self.modules[module_id] = attr.evolve(old, **changes)
        self.async_schedule_save()
        return attr.asdict(new)

    @callback
    def get_mapping(self, mapping_id: int) -> MappingEntry:
        """Get an existing MappingEntry by id."""
        if mapping_id is not None:
            res = self.mappings.get(int(mapping_id))
            return attr.asdict(res) if res else None
        return None

    async def async_get_mappings(self):
        """Get all MappingEntries."""
        return [attr.asdict(val) for val in self.mappings.values()]

    async def async_create_mapping(self, data: dict) -> MappingEntry:
        """Create a new MappingEntry."""
        new_mapping = MappingEntry(**data)
        if not new_mapping.id:
            mappings = await self.async_get_mappings()
            new_mapping = attr.evolve(new_mapping, id=self.generate_next_id(mappings))
        self.mappings[int(new_mapping.id)] = new_mapping
        self.async_schedule_save()
        return attr.asdict(new_mapping)

    async def async_delete_mapping(self, mapping_id: str) -> None:
        """Delete MappingEntry."""
        mapping_id = int(mapping_id)
        if mapping_id in self.mappings:
            del self.mappings[mapping_id]
            self.async_schedule_save()
            return True
        return False

    async def async_update_mapping(
        self, mapping_id: int, changes: dict
    ) -> MappingEntry:
        """Update existing mapping."""
        mapping_id = int(mapping_id)
        old = self.mappings[mapping_id]
        # make sure we don't override the ID
        changes.pop("id", None)
        if old is not None:
            if old.data_last_entry is not None and len(old.data_last_entry) > 0:
                if MAPPING_DATA_LAST_ENTRY not in changes:
                    changes[MAPPING_DATA_LAST_ENTRY] = {}
                for key in old.data_last_entry:
                    if key not in changes[MAPPING_DATA_LAST_ENTRY]:
                        changes[MAPPING_DATA_LAST_ENTRY][key] = old.data_last_entry[key]
            if (
                old.data_last_calculation is not None
                and len(old.data_last_calculation) > 0
            ):
                if MAPPING_DATA_LAST_CALCULATION not in changes:
                    changes[MAPPING_DATA_LAST_CALCULATION] = {}
                for key in old.data_last_calculation:
                    if key not in changes[MAPPING_DATA_LAST_CALCULATION]:
                        changes[MAPPING_DATA_LAST_CALCULATION][key] = (
                            old.data_last_calculation[key]
                        )
        new = self.mappings[mapping_id] = attr.evolve(old, **changes)
        self.async_schedule_save()
        return attr.asdict(new)

    def generate_next_id(self, the_list):
        """Generate a next id for the_list."""
        if the_list is None or len(the_list) == 0:
            return 0
        ids = [the_list[i]["id"] for i in range(len(the_list))]
        if ids is None:
            return 0
        return max(ids) + 1


@bind_hass
async def async_get_registry(hass: HomeAssistant) -> SmartIrrigationStorage:
    """Return Smart Irrigation storage instance."""
    task = hass.data.get(DATA_REGISTRY)

    if task is None:

        async def _load_reg() -> SmartIrrigationStorage:
            registry = SmartIrrigationStorage(hass)
            await registry.async_load()
            return registry

        # Create task to load registry asynchronously - will be awaited below
        task = hass.data[DATA_REGISTRY] = hass.async_create_task(_load_reg())

    data = await task
    return cast(SmartIrrigationStorage, data)
