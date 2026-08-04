"""Storage and management for Smart Irrigation configuration, zones, modules, and mappings."""

import datetime
import logging
import uuid
from collections import OrderedDict
from collections.abc import MutableMapping
from typing import cast

import attr
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.loader import bind_hass
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import (
    ATTR_NEW_BUCKET_VALUE,
    ATTR_NEW_MULTIPLIER_VALUE,
    CONF_ACTIVE_VALVE_RUNS,
    CONF_AUTO_CALC_ENABLED,
    CONF_AUTO_UPDATE_DELAY,
    CONF_AUTO_UPDATE_ENABLED,
    CONF_AUTO_UPDATE_INTERVAL,
    CONF_AUTO_UPDATE_SCHEDULE,
    CONF_CALC_TIME,
    CONF_CONTINUOUS_UPDATES,
    CONF_DAYS_BETWEEN_IRRIGATION,
    CONF_DAYS_SINCE_LAST_IRRIGATION,
    CONF_DEFAULT_AUTO_CALC_ENABLED,
    CONF_DEFAULT_AUTO_UPDATE_DELAY,
    CONF_DEFAULT_AUTO_UPDATE_ENABLED,
    CONF_DEFAULT_AUTO_UPDATE_INTERVAL,
    CONF_DEFAULT_AUTO_UPDATE_SCHEDULE,
    CONF_DEFAULT_BUCKET_THRESHOLD,
    CONF_DEFAULT_CALC_TIME,
    CONF_DEFAULT_CONTINUOUS_UPDATES,
    CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
    CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
    CONF_DEFAULT_DISTRIBUTORS_ENABLED,
    CONF_DEFAULT_DRAINAGE_RATE,
    CONF_DEFAULT_FORECAST_WEIGHTING_ENABLED,
    CONF_DEFAULT_FREEZE_THRESHOLD,
    CONF_DEFAULT_HOURLY_CALCULATION,
    CONF_DEFAULT_KC,
    CONF_DEFAULT_LIVE_ESTIMATE_ENABLED,
    CONF_DEFAULT_LOG_NO_DEMAND,
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
    CONF_DEFAULT_SENSOR_DEBOUNCE,
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
    CONF_HOURLY_CALCULATION,
    CONF_IMPERIAL,
    CONF_LEGACY_FRESH_DURATION_ENABLED,
    CONF_LEGACY_LIVE_DURATION_ENABLED,
    CONF_LIVE_ESTIMATE_ENABLED,
    CONF_LOG_NO_DEMAND,
    CONF_METRIC,
    CONF_OBSERVED_WATERING_ENABLED,
    CONF_PRECIPITATION_FORECAST_DAYS,
    CONF_PRECIPITATION_THRESHOLD_MM,
    CONF_RAIN_DELAY_UNTIL,
    CONF_RAIN_SENSOR,
    CONF_RECURRING_SCHEDULES,
    CONF_SENSOR_DEBOUNCE,
    CONF_SKIP_FREEZE_ENABLED,
    CONF_SKIP_IRRIGATION_ON_PRECIPITATION,
    CONF_SKIP_TEMP_ENABLED,
    CONF_SKIP_WIND_ENABLED,
    CONF_STORED_UNIT_SYSTEM,
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
    UNIT_SYSTEM_METRIC,
    UNIT_SYSTEM_US_CUSTOMARY,
    ZONE_BUCKET,
    ZONE_BUCKET_THRESHOLD,
    ZONE_CURRENT_DRAINAGE,
    ZONE_DELTA,
    ZONE_DRAINAGE_RATE,
    ZONE_DURATION,
    ZONE_FLOW_CAL_ADVISED,
    ZONE_FLOW_CAL_SAMPLES,
    ZONE_FLOW_COUNTER_TYPE,
    ZONE_FLOW_LAST_END,
    ZONE_FLOW_RESET_STREAK,
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
    ZONE_OBSERVED_ENTITY,
    ZONE_PLANT_TYPE,
    ZONE_RUN_LOG,
    ZONE_SIZE,
    ZONE_STATE,
    ZONE_STATE_AUTOMATIC,
    ZONE_THROUGHPUT,
    ZONE_WATER_USED_TOTAL,
)
from .helpers import loadModules, zone_depth_default
from .localize import localize

_LOGGER = logging.getLogger(__name__)

DATA_REGISTRY = f"{DOMAIN}_storage"
STORAGE_KEY = f"{DOMAIN}.storage"
STORAGE_VERSION = 13
# Coalescing window (seconds) for the whole-document store write. Every
# async_schedule_save() reserializes the ENTIRE store — config, zones, modules
# and every sensor group's reading buffer — and replaces the file, so at 0 a
# burst of writes becomes one full-file rewrite each (an SD-card killer).
# HA's Store.async_delay_save re-evaluates the data callback at write time, so a
# delayed save is never stale; it keeps the earliest pending timer rather than
# resetting it, so continuous churn cannot postpone the write indefinitely; and
# it flushes on EVENT_HOMEASSISTANT_FINAL_WRITE, so a clean restart loses
# nothing. Only a hard crash can lose up to this window.
SAVE_DELAY = 30

# How often (seconds) unpersisted sensor readings are written out when nothing
# else happens to write. Appends go to SmartIrrigationStorage.buffers and do NOT
# schedule a save of their own (that is the whole point — see .buffers), so
# without this timer a quiet install could hold hours of readings in memory only.
# A clean shutdown flushes regardless (the EVENT_HOMEASSISTANT_STOP listener), so
# this bounds the hard-crash loss window, not the normal one.
BUFFER_FLUSH_INTERVAL = 600


def _as_int(value, default):
    """Coerce a stored value to int, falling back to ``default``.

    Stored config can hold a numeric setting as a string (older frontends POST
    text-input values verbatim) or as None. Passing that straight through would
    surface far from here — e.g. a str reaching timedelta(milliseconds=...).
    """
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
    # Observed-watering (opt-in): physical valve/switch watched for EXTERNAL runs
    # of a service/self-closing zone (no linked_entity). See ZONE_OBSERVED_ENTITY.
    observed_entity = attr.ib(type=str, default=None)
    # Unified flow engine (opt override): how a totalizer flow_sensor is read
    # ('auto' | 'per_run' | 'lifetime'). Default 'auto'. Additive (no schema bump).
    flow_counter_type = attr.ib(type=str, default="auto")
    # Cross-run flow-counter learning (auto mode): the previous run's end value (litres)
    # and the consecutive-open-reset streak. Additive. See flow_metering.flow_learn_*.
    flow_last_end = attr.ib(type=float, default=None)
    flow_reset_streak = attr.ib(type=int, default=0)
    # Per-member flow-calibration advisory (distributor can't-stop members): rolling
    # measured-vs-target volume samples + a one-shot "advised" marker so the
    # persistent notification is raised once, not every run. See ZONE_FLOW_CAL_*.
    flow_calibration_samples = attr.ib(type=list, factory=list)
    flow_calibration_advised = attr.ib(type=bool, default=False)
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
    """Mapping storage Entry.

    The reading buffer is deliberately NOT a field here: it lives in
    ``SmartIrrigationStorage.buffers`` so that appending a reading neither drags
    the whole configuration through a serialize+replace nor deep-copies the
    buffer on every ``attr.asdict`` of this entry. It is still persisted into the
    same document under the same ``data`` key — see ``_data_to_save_full``.
    """

    id = attr.ib(type=int, default=None)
    name = attr.ib(type=str, default=None)
    mappings = attr.ib(type=str, default=None)
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
    distributors_enabled = attr.ib(type=bool, default=CONF_DEFAULT_DISTRIBUTORS_ENABLED)
    # Continuous (event-driven) sensor ingestion + its per-sensor-group debounce
    # in milliseconds. Both MUST also be setdefault'ed in _async_migrate_func:
    # that function ends by filtering data["config"] against
    # attr.fields_dict(Config), so an attribute without a migration default is
    # simply absent (and a stored value for a key with no attribute is dropped).
    continuousupdates = attr.ib(type=bool, default=CONF_DEFAULT_CONTINUOUS_UPDATES)
    sensor_debounce = attr.ib(type=int, default=CONF_DEFAULT_SENSOR_DEBOUNCE)
    # Summed-hourly ETo + the replayed water balance. Same migration obligation
    # as the two above.
    hourlycalculation = attr.ib(type=bool, default=CONF_DEFAULT_HOURLY_CALCULATION)
    # The unit system the stored zone values were written under. Seeded by the
    # v13 migration and rewritten whenever the coordinator reconciles a flip;
    # None only on a store that predates the key. See unit_system.py, issue #67.
    stored_unit_system = attr.ib(type=str, default=None)
    log_no_demand = attr.ib(type=bool, default=CONF_DEFAULT_LOG_NO_DEMAND)
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

        if old_version <= 11:
            # v12: repair depth-valued zone defaults that were seeded with the raw
            # MILLIMETRE constants on an IMPERIAL install, where the field is stored
            # in inches (see helpers.zone_depth_default).
            #
            # This is not cosmetic. Every existing install already has these values
            # persisted: the fields were absent before they shipped, hydration filled
            # them from the constants, and the whole store is then written back — so
            # fixing only the default helps nobody who has already started the
            # integration. bucket_threshold is the damaging one; irrigation gates on
            # `bucket < bucket_threshold`, and -10 INCHES (-254 mm) is a deficit no
            # bucket reaches, so every deficit-gated run was silently suppressed.
            #
            # Scoped deliberately tight: only on an imperial install, and only when the
            # stored number is EXACTLY the raw mm constant, which no one would choose
            # in inches (a 610 mm ceiling, 508 mm/h drainage, a 254 mm trigger). A
            # deliberate metric value is untouched because metric needs no conversion,
            # and the rewrite is idempotent — the converted value no longer matches.
            if self.hass.config.units is not METRIC_SYSTEM:
                for zone in data.get("zones", []):
                    for key, mm_default in (
                        (ZONE_MAXIMUM_BUCKET, CONF_DEFAULT_MAXIMUM_BUCKET),
                        (ZONE_DRAINAGE_RATE, CONF_DEFAULT_DRAINAGE_RATE),
                        (ZONE_BUCKET_THRESHOLD, CONF_DEFAULT_BUCKET_THRESHOLD),
                    ):
                        if zone.get(key) == mm_default:
                            zone[key] = zone_depth_default(mm_default, False)
                            _LOGGER.info(
                                "Migration v12: zone %s %s was the unconverted %s mm "
                                "default; stored as %.4f in",
                                zone.get(ZONE_ID),
                                key,
                                mm_default,
                                zone[key],
                            )

        if old_version <= 12:
            # v13: record which unit system the stored zone values were written
            # under, so a later flip is DETECTABLE (issue #67).
            #
            # Seeding from the CURRENT unit system is correct by construction:
            # whatever is on disk right now was written by this install under
            # the system it is configured with right now. Nothing is converted
            # here — this migration only starts the bookkeeping. The first real
            # conversion happens the next time the coordinator sees stored and
            # current disagree.
            data.setdefault("config", {})
            data["config"].setdefault(
                CONF_STORED_UNIT_SYSTEM,
                (
                    UNIT_SYSTEM_METRIC
                    if self.hass.config.units is METRIC_SYSTEM
                    else UNIT_SYSTEM_US_CUSTOMARY
                ),
            )

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
            # Continuous updates: MANDATORY here, not merely nice to have. The
            # allowlist strip below drops any key absent from Config, and a key
            # absent from the stored config is simply never hydrated — so without
            # these two setdefaults the toggle silently vanishes on every load.
            # Note `continuousupdates` is altmenorg's key: a stored True from
            # that fork survives the strip because Config now declares it.
            if CONF_CONTINUOUS_UPDATES not in data["config"]:
                data["config"][
                    CONF_CONTINUOUS_UPDATES
                ] = CONF_DEFAULT_CONTINUOUS_UPDATES
            if CONF_SENSOR_DEBOUNCE not in data["config"]:
                data["config"][CONF_SENSOR_DEBOUNCE] = CONF_DEFAULT_SENSOR_DEBOUNCE
            # Same obligation as the two above: no setdefault here and the
            # hourly-calculation toggle is stripped on every load.
            if CONF_HOURLY_CALCULATION not in data["config"]:
                data["config"][
                    CONF_HOURLY_CALCULATION
                ] = CONF_DEFAULT_HOURLY_CALCULATION

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


def _as_buffer(value) -> list:
    """Coerce a stored ``data`` value into a reading buffer.

    Anything that is not a list is treated as "no readings": the field's legacy
    attrs default was the string ``"[]"``, and one 2026.05 test fixture stores a
    dict there.
    """
    if isinstance(value, list):
        return value
    if value not in (None, "", "[]", {}):
        _LOGGER.warning(
            "Sensor group reading buffer has unexpected type %s — starting empty",
            type(value).__name__,
        )
    return []


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
        # mapping id -> that sensor group's rolling reading buffer. Held apart
        # from MappingEntry so appends cost nothing on disk: they mutate the list
        # in place, mark it dirty, and let the flush timer (or the next write
        # somebody else triggers) carry it out. Configuration remains the thing
        # that gets written promptly.
        self.buffers: dict[int, list] = {}
        # True when self.buffers holds rows that are not in the file yet. Read at
        # write time to decide which payload to emit; see _data_to_save_scheduled.
        self._buffers_dirty = False
        self._unsub_stop = None
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
        buffers: dict[int, list] = {}

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
                continuousupdates=data["config"].get(
                    CONF_CONTINUOUS_UPDATES,
                    CONF_DEFAULT_CONTINUOUS_UPDATES,
                ),
                hourlycalculation=data["config"].get(
                    CONF_HOURLY_CALCULATION,
                    CONF_DEFAULT_HOURLY_CALCULATION,
                ),
                # Coerced: altmenorg's frontend could store this as a string, and
                # a str would reach timedelta(milliseconds=...) unconverted.
                stored_unit_system=data["config"].get(CONF_STORED_UNIT_SYSTEM),
                sensor_debounce=_as_int(
                    data["config"].get(CONF_SENSOR_DEBOUNCE),
                    CONF_DEFAULT_SENSOR_DEBOUNCE,
                ),
                log_no_demand=data["config"].get(
                    CONF_LOG_NO_DEMAND,
                    CONF_DEFAULT_LOG_NO_DEMAND,
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
                # In-flight self-closing runs. The attr.ib and the migration
                # setdefault existed without this line, so the list was rebuilt
                # EMPTY on every load: async_resume_self_closing_runs saw nothing
                # to reconcile, a run interrupted by a restart was never finalised
                # (no run-log row, no water_used_total, no master re-hold, no
                # bucket correction), and the next config write dropped the
                # persisted record. See tests/test_store_self_closing.py.
                active_valve_runs=data["config"].get(CONF_ACTIVE_VALVE_RUNS, []),
            )

            if "zones" in data:
                # Depth-valued defaults below are authored in mm but stored in the
                # zone's display units — see helpers.zone_depth_default.
                is_metric = self.hass.config.units is METRIC_SYSTEM
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
                            ZONE_MAXIMUM_BUCKET,
                            zone_depth_default(CONF_DEFAULT_MAXIMUM_BUCKET, is_metric),
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
                            ZONE_BUCKET_THRESHOLD,
                            zone_depth_default(
                                CONF_DEFAULT_BUCKET_THRESHOLD, is_metric
                            ),
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
                        observed_entity=zone.get(ZONE_OBSERVED_ENTITY, None),
                        # Migration: pre-FM zones have no counter override / learning
                        # state; default to auto and a clean streak (additive).
                        flow_counter_type=zone.get(ZONE_FLOW_COUNTER_TYPE, "auto")
                        or "auto",
                        flow_last_end=zone.get(ZONE_FLOW_LAST_END, None),
                        flow_reset_streak=zone.get(ZONE_FLOW_RESET_STREAK, 0) or 0,
                        # Migration: pre-calibration zones start with no samples and
                        # no advisory raised (additive, .get default like above).
                        flow_calibration_samples=zone.get(ZONE_FLOW_CAL_SAMPLES, [])
                        or [],
                        flow_calibration_advised=zone.get(ZONE_FLOW_CAL_ADVISED, False),
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
                    # The buffer is stored inside the mapping record but lives
                    # apart from it at runtime (see MappingEntry). Tolerates both
                    # shapes without a migration: absent (a routine save wrote
                    # this document) or present (a flush did), plus the legacy
                    # default of the *string* "[]".
                    buffers[int(mapping[MAPPING_ID])] = _as_buffer(
                        mapping.get(MAPPING_DATA)
                    )
                    mappings[mapping[MAPPING_ID]] = MappingEntry(
                        id=mapping[MAPPING_ID],
                        name=mapping[MAPPING_NAME],
                        mappings=the_map,
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
        self.buffers = buffers
        # Everything just loaded is by definition already on disk.
        self._buffers_dirty = False
        self.async_ensure_stop_listener()

    @callback
    def async_ensure_stop_listener(self) -> None:
        """Arm the shutdown flush if it is not already armed. Idempotent.

        A clean shutdown must not lose the buffered readings, which no append ever
        scheduled a write for. HA's own Store only flushes a save that is already
        PENDING, so this listener is what makes "a restart loses nothing" true for
        the buffer: it makes one pending, which Store then writes on
        EVENT_HOMEASSISTANT_FINAL_WRITE.

        STOP, not FINAL_WRITE: hass is already `stopping` here, so
        async_delay_save records the payload and arms Store's own final-write
        listener instead of a loop timer that may never fire. Writing the file
        ourselves during FINAL_WRITE would instead race that listener — the first
        of the two to run tears down a one-time subscription HA has already
        consumed, which logs a core error on every shutdown.

        Called from ``async_load`` and again from ``async_get_registry`` on every
        setup. The second call is the one that matters: ``async_delete`` drops the
        listener, but the storage instance is cached in ``hass.data`` for the
        lifetime of hass and ``async_load`` never runs twice — so re-adding the
        integration without restarting HA would otherwise leave it permanently
        unarmed, silently downgrading "a clean restart loses nothing" to "loses up
        to BUFFER_FLUSH_INTERVAL". The ``is None`` guard keeps repeat calls from
        stacking duplicate subscriptions.
        """
        if self._unsub_stop is None:
            self._unsub_stop = self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STOP, self._async_flush_on_stop
            )

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
        self._store.async_delay_save(self._data_to_save_scheduled, SAVE_DELAY)

    async def async_save(self) -> None:
        """Save the registry of Smart Irrigation, buffers included."""
        await self._store.async_save(self._data_to_save_full())

    @callback
    def async_flush_buffers(self) -> None:
        """Schedule a write if the reading buffers are not on disk yet.

        The periodic backstop for appends, which never schedule a write of their
        own. A no-op when nothing has been appended since the last write, so a
        polled install (one reading an hour) does not turn this into an extra
        write cadence of its own.
        """
        if not self._buffers_dirty:
            return
        self.async_schedule_save()

    @callback
    def _async_flush_on_stop(self, _event) -> None:
        """Queue the buffered readings for HA's shutdown write."""
        self._unsub_stop = None
        if not self._buffers_dirty:
            return
        _LOGGER.debug("Queueing buffered sensor readings for the shutdown write")
        self.async_schedule_save()

    @callback
    def _data_to_save_scheduled(self) -> dict:
        """Payload for a *scheduled* save, chosen when the write actually happens.

        The buffer-less payload is emitted ONLY when there are no buffered
        readings at all, because writing it is not merely "omitting" the buffer —
        it REMOVES it from the document on disk.

        ⚠️ Do not narrow this to ``self._buffers_dirty``. That was the original
        form and it silently lost data: the flag means "there are appends not yet
        written", not "the buffer is in the file". Once a full write cleared it,
        the next unrelated write (a zone's last_updated, a config change) emitted
        the buffer-less payload and erased every buffered reading from the file —
        while leaving the flag clean, so neither ``async_flush_buffers`` nor the
        shutdown listener would ever put them back. A clean restart then loaded an
        empty buffer: a whole calculation window of ET gone, silently, which shows
        up as one under-watered day rather than as an error. Verified against a
        real config: 305 readings lost across a clean restart.

        Keeping the buffer in every write costs O(buffer) per WRITE, which is fine
        — Step 4's win is that an append schedules no write at all, so writes stay
        far rarer than readings. It also restores the invariant the rest of this
        class depends on: **if the buffer is non-empty and not dirty, it is in the
        file.**
        """
        if self._buffers_dirty or any(self.buffers.values()):
            return self._data_to_save_full()
        return self._data_to_save()

    @callback
    def _data_to_save(self) -> dict:
        """Return data for the registry for Smart Irrigation to store in a file.

        WITHOUT the sensor-group reading buffers. ``async_load`` treats a missing
        ``data`` key as an empty buffer, so this shape needs no migration.

        ⚠️ Writing this payload DELETES the buffer from the stored document — the
        key is absent, not merely stale. It must therefore only ever be the
        payload when there are no buffered readings to lose; ``_data_to_save_full``
        calls it as a base, and ``_data_to_save_scheduled`` owns that decision.
        """
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

    @callback
    def _data_to_save_full(self) -> dict:
        """The routine payload plus each sensor group's reading buffer.

        Marks the buffers clean: HA evaluates this callback at write time (in the
        event loop), so by the time it returns, these rows are what is about to
        hit the file.
        """
        store_data = self._data_to_save()
        for mapping in store_data["mappings"]:
            mapping[MAPPING_DATA] = self.buffers.get(int(mapping[MAPPING_ID]), [])
        self._buffers_dirty = False
        return store_data

    async def async_delete(self):
        """Delete config."""
        _LOGGER.warning("Removing Smart Irrigation configuration data!")
        await self._store.async_remove()
        # async_remove() cancels HA's own pending/shutdown writes so the deleted
        # file cannot come back. Ours has to go the same way: a buffer left dirty
        # would otherwise resurrect the whole document — with the configuration
        # the user just deleted — at the next HA shutdown.
        if self._unsub_stop is not None:
            self._unsub_stop()
            self._unsub_stop = None
        self.buffers = {}
        self._buffers_dirty = False
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
        data = {k: v for k, v in data.items() if k in valid_fields}
        # The attrs defaults for the depth fields are the raw MILLIMETRE constants,
        # and attrs cannot know the unit system — so seed them here instead, in the
        # units the zone is stored in. Only when the caller omitted them: an explicit
        # value from the panel is already in display units.
        is_metric = self.hass.config.units is METRIC_SYSTEM
        for key, mm_default in (
            (ZONE_MAXIMUM_BUCKET, CONF_DEFAULT_MAXIMUM_BUCKET),
            (ZONE_DRAINAGE_RATE, CONF_DEFAULT_DRAINAGE_RATE),
            (ZONE_BUCKET_THRESHOLD, CONF_DEFAULT_BUCKET_THRESHOLD),
        ):
            if data.get(key) is None:
                data[key] = zone_depth_default(mm_default, is_metric)
        new_zone = ZoneEntry(**data)
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
            # review finding J: guard changes[ZONE_BUCKET] presence like the
            # sibling block below (partial POST may omit bucket -> KeyError/500)
            if (
                ZONE_BUCKET in changes
                and ZONE_MAXIMUM_BUCKET in changes
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
        """Get all MappingEntries.

        Buffer-free, like ``get_mapping``: use ``get_mapping_buffer`` for readings.
        """
        return [attr.asdict(val) for val in self.mappings.values()]

    # ------------------------------------------------------------------
    # Buffer-aware fast paths.
    #
    # get_mapping()/async_get_mappings() return attr.asdict() DEEP COPIES of the
    # MappingEntry — its field-config dict, both carry-forward dicts, the lot.
    # That is fine for the hourly poll but not for anything running per sensor
    # event, and the copy is pure waste when the caller only wants a row count or
    # the field configs. The helpers below give the hot paths what they need
    # without copying anything.
    #
    # The readings themselves are no longer part of that copy at all — they live
    # in self.buffers rather than on the entry — which is what makes an append
    # O(1) in buffer length instead of O(n).
    # ------------------------------------------------------------------

    @callback
    def get_mapping_field_configs(self) -> list[tuple[int, dict]]:
        """Return ``(mapping_id, MAPPING_MAPPINGS)`` for every sensor group.

        Read-only view for the continuous-update subscription rebuild, which runs
        on every ``_config_updated`` signal — including the ones ingestion itself
        emits. The returned field-config dicts are the LIVE objects, not copies —
        callers must treat them as immutable. That is safe because every writer
        goes through ``async_update_mapping``, which ``attr.evolve``s a
        replacement rather than mutating in place, so a held reference can only
        ever go stale (and the ``_config_updated`` signal re-reads it), never be
        corrupted underneath.
        """
        return [
            (int(entry.id), entry.mappings or {})
            for entry in self.mappings.values()
            if entry.id is not None
        ]

    @callback
    def get_mapping_buffer(self, mapping_id: int) -> list:
        """Return a sensor group's reading buffer — the LIVE list, not a copy.

        Callers read it (aggregation, the panel's weather-records table). To
        change it use ``append_mapping_reading`` / ``set_mapping_buffer``, which
        also mark it for persistence; mutating the returned list directly leaves
        the change unwritten.
        """
        if mapping_id is None:
            return []
        return self.buffers.get(int(mapping_id), [])

    @callback
    def get_mapping_row_count(self, mapping_id: int) -> int | None:
        """Number of buffered readings, or None if the sensor group is unknown.

        Cheap: never materializes the buffer, so it is safe on hot paths (the
        zone data-point count, "has this group any data at all" checks).
        """
        if mapping_id is None:
            return None
        mapping_id = int(mapping_id)
        if mapping_id not in self.mappings:
            return None
        return len(self.buffers.get(mapping_id, []))

    @callback
    def append_mapping_reading(self, mapping_id: int, reading: dict) -> bool:
        """Append one reading to a sensor group's buffer. O(1), no disk write.

        Deliberately does NOT schedule a save — that is what keeps ingestion off
        the disk. The row reaches the file via the flush timer
        (``async_flush_buffers``), the next write anything else triggers, or the
        shutdown flush. Returns False if the sensor group is unknown.
        """
        if mapping_id is None:
            return False
        mapping_id = int(mapping_id)
        if mapping_id not in self.mappings:
            return False
        self.buffers.setdefault(mapping_id, []).append(reading)
        self._buffers_dirty = True
        return True

    @callback
    def set_mapping_buffer(self, mapping_id: int, readings) -> None:
        """Replace a sensor group's buffer (prune, clear, source change).

        Unlike an append this DOES schedule a save: these are rare, and a prune
        that only ever lived in memory would be re-done from the same rows after
        a restart.
        """
        if mapping_id is None:
            return
        mapping_id = int(mapping_id)
        if mapping_id not in self.mappings:
            return
        self.buffers[mapping_id] = _as_buffer(readings)
        self._buffers_dirty = True
        self.async_schedule_save()

    @callback
    def set_mapping_last_entry_value(self, mapping_id: int, key: str, value) -> None:
        """Refresh one carry-forward field WITHOUT scheduling a save.

        The companion to ``append_mapping_reading`` for the event-driven ingestion
        path: every reading also updates ``data_last_entry`` (the value
        ``aggregate_window`` falls back to for a field with no row in a zone's
        window), and scheduling a write for that would put ingestion straight back
        on the disk — reintroducing per-reading whole-document saves through the
        one field of MappingEntry that an append touches.

        So it rides along on the next write like the buffers do. Unlike them it
        needs no dirty flag: ``data_last_entry`` is a MappingEntry field, so it is
        in the routine payload and ANY subsequent write carries it. Losing it to a
        hard crash is recoverable — it is derivable from the buffer, being simply
        the newest value seen per field.

        Deliberately NOT mutated in place: the attrs default for
        ``data_last_entry`` is a bare ``{}``, i.e. ONE dict object shared by every
        MappingEntry constructed without an explicit value, so writing into it
        would leak carry-forward values between unrelated sensor groups. Evolving
        a fresh dict costs one small copy (a handful of fields, never the buffer)
        and is safe.
        """
        if mapping_id is None:
            return
        mapping_id = int(mapping_id)
        entry = self.mappings.get(mapping_id)
        if entry is None:
            return
        last_entry = entry.data_last_entry
        last_entry = dict(last_entry) if isinstance(last_entry, dict) else {}
        last_entry[key] = value
        self.mappings[mapping_id] = attr.evolve(entry, data_last_entry=last_entry)

    async def async_create_mapping(self, data: dict) -> MappingEntry:
        """Create a new MappingEntry."""
        # Readings are not a MappingEntry field; accept them in the incoming dict
        # (stored records and the API carry the key) and route them to the buffer.
        readings = data.pop(MAPPING_DATA, None)
        new_mapping = MappingEntry(**data)
        if not new_mapping.id:
            mappings = await self.async_get_mappings()
            new_mapping = attr.evolve(new_mapping, id=self.generate_next_id(mappings))
        self.mappings[int(new_mapping.id)] = new_mapping
        if readings is not None:
            self.buffers[int(new_mapping.id)] = _as_buffer(readings)
            self._buffers_dirty = True
        self.async_schedule_save()
        return attr.asdict(new_mapping)

    async def async_delete_mapping(self, mapping_id: str) -> None:
        """Delete MappingEntry."""
        mapping_id = int(mapping_id)
        if mapping_id in self.mappings:
            del self.mappings[mapping_id]
            # Drop the buffer too, or it leaks for the lifetime of hass and gets
            # re-adopted by whatever mapping is next assigned this id.
            self.buffers.pop(mapping_id, None)
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
        # Same as in async_create_mapping: `data` is a buffer write, not a field.
        if MAPPING_DATA in changes:
            self.set_mapping_buffer(mapping_id, changes.pop(MAPPING_DATA))
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
    registry = cast(SmartIrrigationStorage, data)
    # Re-arm the shutdown flush. This instance is cached above for the lifetime of
    # hass, so on the second and later setups async_load (and its own arming) does
    # not run — and async_delete unregisters the listener. Re-adding the
    # integration without an HA restart would otherwise leave the buffer with no
    # shutdown flush at all. Idempotent, so the common path is a no-op.
    registry.async_ensure_stop_listener()
    return registry
