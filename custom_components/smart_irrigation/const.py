"""Store constants."""


class SmartIrrigationError(Exception):
    """Exception raised for errors in the Smart Irrigation integration."""


VERSION = "v2026.07.04"
NAME = "Smart Irrigation"
MANUFACTURER = "@JustChr"

DOMAIN = "smart_irrigation"
CUSTOM_COMPONENTS = "custom_components"

LANGUAGE_FILES_DIR = "frontend/localize/languages"
SUPPORTED_LANGUAGES = ["de", "en", "es", "fr", "it", "nl", "no", "sk"]

START_EVENT_FIRED_TODAY = "starteventfiredtoday"

# Irrigation start trigger configuration
CONF_IRRIGATION_START_TRIGGERS = "irrigation_start_triggers"

# Weather-based skip configuration
CONF_SKIP_IRRIGATION_ON_PRECIPITATION = "skip_irrigation_on_precipitation"
CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION = False
CONF_PRECIPITATION_THRESHOLD_MM = "precipitation_threshold_mm"
CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM = 2.0  # 2mm threshold
# How many forecast days to sum when checking precipitation. The weather clients
# return future days only (today is excluded), so 1 = the next forecast day.
CONF_PRECIPITATION_FORECAST_DAYS = "precipitation_forecast_days"
CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS = 1

CONF_SKIP_TEMP_ENABLED = "skip_on_temp_enabled"
CONF_TEMP_THRESHOLD = "temp_threshold"  # °C — skip if temperature is BELOW this
CONF_DEFAULT_SKIP_TEMP_ENABLED = False
CONF_DEFAULT_TEMP_THRESHOLD = 5.0  # °C

CONF_SKIP_WIND_ENABLED = "skip_on_wind_enabled"
CONF_WIND_THRESHOLD = "wind_threshold"  # m/s — skip if wind is ABOVE this
CONF_DEFAULT_SKIP_WIND_ENABLED = False
CONF_DEFAULT_WIND_THRESHOLD = 6.9  # m/s (~25 km/h)

CONF_RAIN_SENSOR = "rain_sensor"  # entity_id of a binary_sensor; None = disabled
CONF_DEFAULT_RAIN_SENSOR = None

# Freeze guard (WS-4): skip irrigation when frost is expected, to protect pipes
# and plants. Distinct from the low-temperature guard above — frost-specific and
# evaluated against the forecast minimum (the coming night), not just the current
# reading. Default OFF so existing installs are unaffected.
CONF_SKIP_FREEZE_ENABLED = "skip_on_freeze_enabled"
CONF_FREEZE_THRESHOLD = "freeze_threshold"  # °C — skip if min temp is BELOW this
CONF_DEFAULT_SKIP_FREEZE_ENABLED = False
CONF_DEFAULT_FREEZE_THRESHOLD = 1.0  # °C — frost forms near 0 °C

# Experimental features (opt-in, surfaced on the Setup → Experimental tab).
# Forecast weighting: water LESS (shorter durations) when rain is forecast,
# folding the look-ahead precipitation into the deficit used for the duration
# while leaving the true deficit in the bucket for the real rain to fill. Reuses
# the precipitation look-ahead window (CONF_PRECIPITATION_FORECAST_DAYS).
CONF_FORECAST_WEIGHTING_ENABLED = "forecast_weighting_enabled"
CONF_DEFAULT_FORECAST_WEIGHTING_ENABLED = False
# Observed watering: credit the bucket whenever a zone's linked valve runs,
# including manual/automation runs outside Smart Irrigation, estimated from the
# run time and configured throughput.
CONF_OBSERVED_WATERING_ENABLED = "observed_watering_enabled"
CONF_DEFAULT_OBSERVED_WATERING_ENABLED = False
# Live-estimate watering: at scheduled run time, both TRIGGER and SIZE each
# zone's run from the live intra-day deficit (drainage-aware ET/precip since the
# last daily calc, the same quantity behind the "Live bucket" sensor) instead of
# the once-daily bucket. This can start a run the daily calc didn't approve (the
# point — sub-daily watering between daily calcs) and resize/cancel one it did.
# The daily ledger is unchanged; the post-run reset credits the actually-
# delivered water so the next daily calc does not double-subtract the intra-day
# ET. Trigger gate honours each zone's bucket threshold (minimum deficit).
CONF_LIVE_ESTIMATE_ENABLED = "live_estimate_enabled"
CONF_DEFAULT_LIVE_ESTIMATE_ENABLED = False
# Mechanical water distributors (Gardena-style indexing distributor): opt-in,
# experimental. Off by default. UI-visibility gate only — the distributor engine
# is already inert unless distributors are configured, so this flag never stops an
# existing cycle; it just hides the Distributors tab + the zone-side selector.
CONF_DISTRIBUTORS_ENABLED = "distributors_enabled"
CONF_DEFAULT_DISTRIBUTORS_ENABLED = False
# Legacy keys read as a fallback on load so an early opt-in survives the
# renames: v2026.06.28 shipped "fresh_duration_enabled"; it was then
# "live_duration_enabled" while the feature only *resized* a daily-approved run.
# It now also *triggers* runs from the live deficit, hence "live_estimate".
CONF_LEGACY_LIVE_DURATION_ENABLED = "live_duration_enabled"
CONF_LEGACY_FRESH_DURATION_ENABLED = "fresh_duration_enabled"
# Drift guard for live-estimate watering: with multiple runs/day the stored
# bucket must bank a full day's delivered water until the nightly calc subtracts
# the day's ET once. The post-run credit is clamped at maximum_bucket; if that is
# smaller than ~a day's ET, banked water is clipped and the daily calc drifts
# drier. The 24 mm default is safe; warn (don't block) below this floor.
LIVE_MIN_MAXIMUM_BUCKET_MM = 10.0

# Rain delay / vacation hold (WS-5): a user-initiated, time-boxed pause of all
# AUTOMATIC/scheduled irrigation until a future datetime. Distinct from skip
# conditions (which are weather-driven). Stored as an ISO-8601 string or None;
# default None ⇒ no hold ⇒ behaviour unchanged. Explicit manual runs bypass it.
CONF_RAIN_DELAY_UNTIL = "rain_delay_until"
CONF_DEFAULT_RAIN_DELAY_UNTIL = None
# Run-log / skip detail token recorded when a scheduled run is held back by the
# rain delay (surfaced in the run history + outlook like the other skip ids).
SKIP_REASON_PAUSED = "paused"
# Run-log / skip token recorded when a zone is skipped because its soil-moisture
# sensor reads wetter than the zone's threshold (per-zone, automatic path only).
SKIP_REASON_SOIL_MOISTURE = "soil_moisture"

# Days between irrigation configuration
CONF_DAYS_BETWEEN_IRRIGATION = "days_between_irrigation"
CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION = 0  # 0 = no restriction (default behavior)
CONF_DAYS_SINCE_LAST_IRRIGATION = "days_since_last_irrigation"
CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION = 0

# Enhanced Scheduling Configuration
CONF_RECURRING_SCHEDULES = "recurring_schedules"
CONF_DEFAULT_RECURRING_SCHEDULES = []

# Recurring Schedule Configuration
SCHEDULE_TYPE_DAILY = "daily"
SCHEDULE_TYPE_WEEKLY = "weekly"
SCHEDULE_TYPE_MONTHLY = "monthly"
SCHEDULE_TYPE_INTERVAL = "interval"
SCHEDULE_TYPE_SUNRISE = "sunrise"
SCHEDULE_TYPE_SUNSET = "sunset"
SCHEDULE_TYPE_SOLAR_AZIMUTH = "solar_azimuth"
SCHEDULE_TYPES = [
    SCHEDULE_TYPE_DAILY,
    SCHEDULE_TYPE_WEEKLY,
    SCHEDULE_TYPE_MONTHLY,
    SCHEDULE_TYPE_INTERVAL,
    SCHEDULE_TYPE_SUNRISE,
    SCHEDULE_TYPE_SUNSET,
    SCHEDULE_TYPE_SOLAR_AZIMUTH,
]

# Recurring Schedule Keys
SCHEDULE_CONF_ID = "id"
SCHEDULE_CONF_NAME = "name"
SCHEDULE_CONF_TYPE = "type"
SCHEDULE_CONF_ENABLED = "enabled"
SCHEDULE_CONF_TIME = "time"
SCHEDULE_CONF_DAYS_OF_WEEK = "days_of_week"
SCHEDULE_CONF_DAY_OF_MONTH = "day_of_month"
SCHEDULE_CONF_INTERVAL_HOURS = "interval_hours"
SCHEDULE_CONF_START_TIME = "start_time"  # Optional HH:MM clock anchor for interval
SCHEDULE_CONF_START_DATE = "start_date"
SCHEDULE_CONF_END_DATE = "end_date"
SCHEDULE_CONF_ZONES = "zones"  # List of zone IDs or "all"
SCHEDULE_CONF_ACTION = "action"  # "calculate", "update", or "irrigate"
SCHEDULE_CONF_OFFSET_MINUTES = "offset_minutes"
SCHEDULE_CONF_ACCOUNT_FOR_DURATION = "account_for_duration"  # legacy; see time_anchor
SCHEDULE_CONF_AZIMUTH_ANGLE = "azimuth_angle"
# Whether the schedule's time marks when irrigation STARTS or when it FINISHES.
# "finish" fires early enough (time − estimated duration) that the run ends at
# the configured time. Supersedes account_for_duration for all schedule types.
SCHEDULE_CONF_TIME_ANCHOR = "time_anchor"
SCHEDULE_TIME_ANCHOR_START = "start"
SCHEDULE_TIME_ANCHOR_FINISH = "finish"

CONF_WEATHER_SERVICE = "weather_service"
CONF_WEATHER_SERVICE_API_KEY = (
    "weather_service_api_key"  # legacy single-key slot (kept for migration)
)
CONF_OWM_API_KEY = "owm_api_key"
CONF_PW_API_KEY = "pw_api_key"
CONF_MET_API_KEY = "met_api_key"
CONF_WEATHER_SERVICE_API_VERSION = "weather_service_api_version"
CONF_INSTANCE_NAME = "name"

# Manual coordinate configuration
CONF_MANUAL_COORDINATES_ENABLED = "manual_coordinates_enabled"
CONF_MANUAL_LATITUDE = "manual_latitude"
CONF_MANUAL_LONGITUDE = "manual_longitude"
CONF_MANUAL_ELEVATION = "manual_elevation"
CONF_DEFAULT_MANUAL_COORDINATES_ENABLED = False
# Weather Services

CONF_WEATHER_SERVICE_OWM = "Open Weather Map"
CONF_WEATHER_SERVICE_PW = "Pirate Weather"
CONF_WEATHER_SERVICE_OPENMETEO = "Open-Meteo"
CONF_WEATHER_SERVICE_MET = "Met Office"
CONF_WEATHER_SERVICES = [
    CONF_WEATHER_SERVICE_OPENMETEO,
    CONF_WEATHER_SERVICE_OWM,
    CONF_WEATHER_SERVICE_PW,
    CONF_WEATHER_SERVICE_MET,
]
# Services that do not require an API key
CONF_WEATHER_SERVICES_NO_API_KEY = [CONF_WEATHER_SERVICE_OPENMETEO]

CONF_DEFAULT_USE_WEATHER_SERVICE = False
CONF_DEFAULT_WEATHER_SERVICE = None
CONF_CALC_TIME = "calctime"
CONF_DEFAULT_CALC_TIME = "23:00"
CONF_AUTO_CALC_ENABLED = "autocalcenabled"
CONF_DEFAULT_AUTO_CALC_ENABLED = True
CONF_AUTO_UPDATE_ENABLED = "autoupdateenabled"
CONF_AUTO_UPDATE_SCHEDULE = "autoupdateschedule"
CONF_AUTO_UPDATE_MINUTELY = "minutes"
CONF_AUTO_UPDATE_HOURLY = "hours"
CONF_AUTO_UPDATE_DAILY = "days"
CONF_DEFAULT_AUTO_UPDATE_SCHEDULE = CONF_AUTO_UPDATE_HOURLY
CONF_DEFAULT_AUTO_UPDATE_ENABLED = True
CONF_AUTO_UPDATE_DELAY = "autoupdatedelay"
CONF_DEFAULT_AUTO_UPDATE_DELAY = "0"
CONF_AUTO_UPDATE_INTERVAL = "autoupdateinterval"
CONF_DEFAULT_AUTO_UPDATE_INTERVAL = "1"
CONF_UNITS = "units"
CONF_IMPERIAL = "imperial"
CONF_METRIC = "metric"
CONF_USE_WEATHER_SERVICE = "use_weather_service"
CONF_DEFAULT_MAXIMUM_DURATION = (
    3600  # default maximum duration to one hour == 3600 seconds
)
CONF_DEFAULT_MAXIMUM_BUCKET = 24  # mm default maximum bucket of 24mm
# mm/hour at saturation. 20 suits medium/loam soil; lower for heavy clay
# (~2-10), higher for sand. Was 50.8 (2 in/h, sandy) — too fast for most.
CONF_DEFAULT_DRAINAGE_RATE = 20.0

# PyETO specific config consts
CONF_PYETO_COASTAL = "coastal"
CONF_PYETO_SOLRAD_BEHAVIOR = "solrad_behavior"
CONF_PYETO_FORECAST_DAYS = "forecast_days"

INTEGRATION_FOLDER = DOMAIN
PANEL_FOLDER = "frontend"
PANEL_FILENAME = "dist/smart-irrigation.js"

PANEL_URL = "/api/panel_custom/smart-irrigation"
PANEL_TITLE = NAME
PANEL_ICON = "mdi:sprinkler"
PANEL_NAME = "smart-irrigation"

# Lovelace custom card: a second bundle served to all users (not just admins)
# and auto-loaded via add_extra_js_url, so non-admins can add the zones card to
# their own dashboards.
CARD_FILENAME = "dist/smart-irrigation-card.js"
CARD_URL = "/smart_irrigation_card/smart-irrigation-card.js"

# The card file above is a tiny stub auto-loaded on every page; it lazy-imports
# this heavy implementation bundle only when a card actually renders (keep
# FULL_CARD_URL in sync with const.ts).
FULL_CARD_FILENAME = "dist/smart-irrigation-card-impl.js"
FULL_CARD_URL = "/smart_irrigation_card/smart-irrigation-card-impl.js"

# Localization static files: only en.json is bundled into the frontend
# bundles; the other languages are served from here and fetched on demand by
# the frontend (keep LANG_URL in sync with LANG_BASE_URL in frontend const.ts).
LANG_FOLDER = "localize/languages"
LANG_URL = "/smart_irrigation_static/languages"

ATTR_REMOVE = "remove"
ATTR_CALCULATE = "calculate"
ATTR_CALCULATE_ALL = "calculate_all"
ATTR_SET_BUCKET = "set_bucket"
ATTR_NEW_BUCKET_VALUE = "new_bucket_value"
ATTR_SET_MULTIPLIER = "set_multiplier"
ATTR_NEW_MULTIPLIER_VALUE = "new_multiplier_value"
ATTR_NEW_THROUGHPUT_VALUE = "new_throughput_value"
ATTR_UPDATE = "update"
ATTR_UPDATE_ALL = "update_all"
ATTR_OVERRIDE_CACHE = "override_cache"
ATTR_RESET_ALL_BUCKETS = "reset_all_buckets"
ATTR_CLEAR_ALL_WEATHERDATA = "clear_all_weatherdata"
ATTR_NEW_STATE_VALUE = "new_state_value"
ATTR_NEW_DURATION_VALUE = "new_duration_value"
ATTR_DELETE_WEATHER_DATA = "delete_weather_data"

LIST_SET_ZONE_ALLOWED_ARGS = [
    ATTR_NEW_BUCKET_VALUE,
    ATTR_NEW_MULTIPLIER_VALUE,
    ATTR_NEW_DURATION_VALUE,
    ATTR_NEW_STATE_VALUE,
    ATTR_NEW_THROUGHPUT_VALUE,
]

ZONE_ID = "id"
ZONE_NAME = "name"
ZONE_SIZE = "size"
ZONE_THROUGHPUT = "throughput"
ZONE_STATE = "state"
ZONE_DURATION = "duration"
ZONE_STATE_DISABLED = "disabled"
ZONE_STATE_MANUAL = "manual"
ZONE_STATE_AUTOMATIC = "automatic"
ZONE_STATES = [ZONE_STATE_DISABLED, ZONE_STATE_MANUAL, ZONE_STATE_AUTOMATIC]
ZONE_MODULE = "module"
ZONE_BUCKET = "bucket"
ZONE_DELTA = "delta"
ZONE_EXPLANATION = "explanation"
ZONE_MULTIPLIER = "multiplier"
ZONE_MAPPING = "mapping"
ZONE_LEAD_TIME = "lead_time"
ZONE_MAXIMUM_DURATION = "maximum_duration"
ZONE_MAXIMUM_BUCKET = "maximum_bucket"
ZONE_LAST_CALCULATED = "last_calculated"
# Internal per-zone watermark: the instant up to which this zone has already
# folded shared mapping weather data into its bucket. Separate from the
# user-facing last_calculated so each zone consumes its own window of the shared
# buffer (multiple zones can use the same mapping). See calculation.py.
ZONE_LAST_CONSUMED = "last_consumed_at"
ZONE_LAST_UPDATED = "last_updated"
ZONE_LAST_IRRIGATION = "last_irrigation"
ZONE_NUMBER_OF_DATA_POINTS = "number_of_data_points"
ZONE_DRAINAGE_RATE = "drainage_rate"
ZONE_CURRENT_DRAINAGE = "current_drainage"
# Crop coefficient (Kc, WS-4): scales the ET0 (reference-grass) term ONLY at
# calculation time so the deficit reflects the zone's actual plant water use.
# Precipitation is NOT scaled. Default 1.0 ⇒ behaviour identical to reference ET.
ZONE_KC = "kc"
CONF_DEFAULT_KC = 1.0
# Optional plant-type preset that seeds a sensible Kc (the stored value is still
# the plain ``kc`` number, so power users can override it = "custom"). Mid-season
# FAO-56-style coefficients relative to grass reference ET0.
ZONE_PLANT_TYPE = "plant_type"
PLANT_TYPE_CUSTOM = "custom"
CONF_DEFAULT_PLANT_TYPE = PLANT_TYPE_CUSTOM
PLANT_TYPE_KC = {
    "lawn": 0.8,
    "vegetables": 1.0,
    "flowers": 0.9,
    "shrubs": 0.5,
    "trees": 0.7,
    "xeriscape": 0.3,
}
ZONE_LINKED_ENTITY = "linked_entity"
ZONE_BUCKET_THRESHOLD = "bucket_threshold"
# mm; new zones require a 10 mm deficit before irrigating (bucket < -10).
# Stored 0-or-negative; 0 = irrigate on any deficit. Existing zones keep their
# stored value — this only seeds newly created zones.
CONF_DEFAULT_BUCKET_THRESHOLD = -10.0
ZONE_FLOW_SENSOR = "flow_sensor"
FLOW_POLL_INTERVAL = 15  # seconds between flow meter readings
# Seconds between mid-run bucket/water-usage commits. Watering is accounted
# continuously (water flows over the whole run), but we only persist + dispatch
# progress on this coarse cadence — not every poll — so the store write and the
# _config_updated fan-out stay to ≤1/min. Runs shorter than this commit exactly
# once, at turn-off (no extra writes vs. a single end-of-run commit).
RUN_COMMIT_INTERVAL = 60
# Bucket level a *complete* irrigation run should leave the zone at (display
# units, 0-or-negative). Default 0.0 = a run replenishes the full deficit
# (bucket → 0). When the experimental forecast-weighting feature reduces a run
# because rain is coming, this carries the leftover deficit so the forecast rain
# fills the rest instead of the run pretending the deficit is gone. Recomputed
# every calculation; only ever non-zero while forecast weighting is enabled.
ZONE_IRRIGATION_TARGET_BUCKET = "irrigation_target_bucket"

# Valve-run verification (WS-1 "close the loop"). After the runner opens a zone's
# linked valve it confirms the entity actually reports an on-state; if it does
# not the run is treated as failed — the bucket is NOT replenished and the zone
# is flagged with a fault so a single automation can alert on it. Faults are held
# in memory on the coordinator (like the skip evaluation), not persisted.
# Seconds to wait for a freshly-opened valve to report on before declaring it
# unconfirmed, and how often to re-check within that window. Sleepy Zigbee/Tuya
# valves can take >10s to report their new state, so the window is generous.
VALVE_CONFIRM_TIMEOUT = 30
VALVE_CONFIRM_POLL = 1
# Re-send the open command once, this many seconds into the confirm window, to
# recover a command silently dropped by a sleepy valve.
VALVE_CONFIRM_RETRY_AT = 15
# Fault reason codes (also i18n keys under panels.zones.fault.*).
FAULT_VALVE_NO_RESPONSE = "valve_no_response"
FAULT_FLOW_NEVER_STARTED = "flow_never_started"

# History / water usage (WS-2 "trust via hindsight").
# Cumulative water delivered per zone, persisted in litres (the canonical
# volume); the usage sensor exposes device_class:water + state_class:
# total_increasing so HA charts it for free and converts to gal on imperial.
ZONE_WATER_USED_TOTAL = "water_used_total"
# Bounded rolling per-zone run log. Each entry:
#   {ts, trigger, planned_s, actual_s, volume_l, result, detail}
# result is one of RUN_RESULT_*; detail carries the skip-reason / fault code /
# calculation explanation depending on the result. Capped at RUN_LOG_MAX_ENTRIES
# (newest first) so the store never grows unbounded.
ZONE_RUN_LOG = "run_log"
RUN_LOG_MAX_ENTRIES = 50
RUN_RESULT_COMPLETED = "completed"
RUN_RESULT_PARTIAL = "partial"
RUN_RESULT_FAILED = "failed"
RUN_RESULT_SKIPPED = "skipped"
# External run credited by observed watering (opt-in): the zone's valve ran
# outside Smart Irrigation and its estimated volume was credited to the bucket.
RUN_RESULT_OBSERVED = "observed"

CONF_ZONE_SEQUENCING = "zone_sequencing"
CONF_ZONE_SEQUENCING_SEQUENTIAL = "sequential"
CONF_ZONE_SEQUENCING_PARALLEL = "parallel"
CONF_ZONE_SEQUENCING_ROTATING = "rotating"
CONF_DEFAULT_ZONE_SEQUENCING = CONF_ZONE_SEQUENCING_PARALLEL
CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION = (
    "zone_sequencing_max_consecutive_duration"
)
CONF_DEFAULT_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION = 5  # minutes
CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME = "zone_sequencing_min_absorption_time"
CONF_DEFAULT_ZONE_SEQUENCING_MIN_ABSORPTION_TIME = 0  # minutes (0 = disabled)

MODULE_DIR = "calcmodules"
MODULE_ID = "id"
MODULE_NAME = "name"
MODULE_DESCRIPTION = "description"
MODULE_CONFIG = "config"
MODULE_SCHEMA = "schema"

MAPPING_ID = "id"
MAPPING_NAME = "name"
MAPPING_DATA = "data"
MAPPING_DATA_LAST_UPDATED = "data_last_updated"
MAPPING_DATA_LAST_ENTRY = "data_last_entry"
MAPPING_DATA_LAST_CALCULATION = "data_last_calculation"
MAPPING_DATA_MULTIPLIER = "data_multiplier"
MAPPING_MAPPINGS = "mappings"
MAPPING_DEWPOINT = "Dewpoint"
MAPPING_EVAPOTRANSPIRATION = "Evapotranspiration"
MAPPING_HUMIDITY = "Humidity"
MAPPING_MAX_TEMP = "Maximum Temperature"
MAPPING_MIN_TEMP = "Minimum Temperature"
MAPPING_PRECIPITATION = "Precipitation"
MAPPING_CURRENT_PRECIPITATION = "Current Precipitation"
MAPPING_PRESSURE = "Pressure"
MAPPING_SOLRAD = "Solar Radiation"
MAPPING_TEMPERATURE = "Temperature"
MAPPING_WINDSPEED = "Windspeed"

MAPPING_CONF_SOURCE_WEATHER_SERVICE = "weather_service"
MAPPING_CONF_SOURCE_SENSOR = "sensor"
MAPPING_CONF_SOURCE_NONE = "none"
MAPPING_CONF_SOURCE_STATIC_VALUE = "static"

MAPPING_CONF_SOURCE = "source"
MAPPING_CONF_SENSOR = "sensorentity"
MAPPING_CONF_STATIC_VALUE = "static_value"
MAPPING_CONF_UNIT = "unit"
MAPPING_CONF_PRESSURE_TYPE = "pressure_type"
MAPPING_CONF_PRESSURE_RELATIVE = "relative"
MAPPING_CONF_AGGREGATE = "aggregate"
MAPPING_CONF_AGGREGATE_AVERAGE = "average"
MAPPING_CONF_AGGREGATE_FIRST = "first"
MAPPING_CONF_AGGREGATE_LAST = "last"
MAPPING_CONF_AGGREGATE_MAXIMUM = "maximum"
MAPPING_CONF_AGGREGATE_MEDIAN = "median"
MAPPING_CONF_AGGREGATE_MINIMUM = "minimum"
MAPPING_CONF_AGGREGATE_SUM = "sum"
MAPPING_CONF_AGGREGATE_RIEMANNSUM = "riemannsum"
MAPPING_CONF_AGGREGATE_DELTA = "delta"
MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT = MAPPING_CONF_AGGREGATE_AVERAGE
MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT_PRECIPITATION = MAPPING_CONF_AGGREGATE_DELTA

# For timestamps
RETRIEVED_AT = "retrieved"  # when HA fetched the data (datetime.now())
OBSERVATION_TIME = "observed"  # when the weather station measured it (API dt)

EVENT_IRRIGATE_START = "start_irrigation_all_zones"

UNIT_M2 = "m<sup>2</sup>"
UNIT_SQ_FT = "sq ft"
UNIT_LPM = "l/m"
UNIT_GPM = "gal/m"
UNIT_SECONDS = "s"
UNIT_MM = "mm"
UNIT_INCH = "in"
UNIT_PERCENT = "%"
UNIT_MBAR = "mbar"
UNIT_MILLIBAR = "millibar"
UNIT_HPA = "hPa"
UNIT_PSI = "psi"
UNIT_INHG = "inch Hg"
UNIT_KMH = "km/h"
UNIT_MH = "mile/h"
UNIT_MS = "meter/s"
UNIT_W_M2 = "W/m2"
UNIT_W_SQFT = "W/sq ft"
UNIT_MJ_DAY_M2 = "MJ/day/m2"
UNIT_MJ_DAY_SQFT = "MJ/day/sq ft"
UNIT_MMH = "mm/h"
UNIT_INCHH = "in/h"

# METRIC TO IMPERIAL (US) FACTORS
MM_TO_INCH_FACTOR = 0.03937008  # mm * factor = inch
LITER_TO_GALLON_FACTOR = 0.26417205  # l * factor = gal
M2_TO_SQ_FT_FACTOR = 10.7639104  # m2 * factor = sq ft
MBAR_TO_PSI_FACTOR = 0.01450377  # mbar = hpa * factor = psi
MBAR_TO_INHG_FACTOR = 0.029529983071445  # mbar = hpa * factor = inhg
KMH_TO_MILESH_FACTOR = 0.62137119  # kmh * factor = mph
MS_TO_MILESH_FACTOR = 2.23693629  # ms * factor = mph
W_M2_TO_W_SQ_FT_FACTOR = 0.09290304  # w/m2 * factor = w/sqft

# IMPERIAL (US) TO METRIC FACTORS
INCH_TO_MM_FACTOR = 25.4  # inch * factor = mm
GALLON_TO_LITER_FACTOR = 3.78541178  # gal * factor = l
SQ_FT_TO_M2_FACTOR = 0.0929030401442212  # sq ft * factor = m2
MILESH_TO_MS_FACTOR = 0.4470400004105615  # m/h * factor = ms
MILESH_TO_KMH_FACTOR = 1.609344  # m/h * factor = kmh
PSI_TO_HPA_FACTOR = 68.9475729  # psi * factor = hpa = mbar
INHG_TO_HPA_FACTOR = 33.8639  # inhg * factor = hpa = mbar
W_SQ_FT_TO_W_M2_FACTOR = 10.76391042  # w/sqft * factor = w/m2

# OTHER FACTORS
KMH_TO_MS_FACTOR = 0.277777777777778  # kmh * factor = ms
MS_TO_KMH_FACTOR = 3.6  # m/s * factor = kmh
W_TO_MJ_DAY_FACTOR = 0.0864  # w * factor = mj/day, same for w/m2 to mj/day/m2
K_TO_C_FACTOR = 273.15  # K-factor = C, C+factor=K
INHG_TO_PSI_FACTOR = 0.49115420057253  # inhg * factor = PSI
PSI_TO_INHG_FACTOR = 2.0360206576012  # psi * factor = inhg

SENSOR_ICON = "mdi:sprinkler"

# Services
SERVICE_CALCULATE_ALL_ZONES = "calculate_all_zones"
SERVICE_CALCULATE_ZONE = "calculate_zone"
SERVICE_UPDATE_ALL_ZONES = "update_all_zones"
SERVICE_UPDATE_ZONE = "update_zone"
SERVICE_RESET_BUCKET = "reset_bucket"
SERVICE_RESET_ALL_BUCKETS = "reset_all_buckets"
SERVICE_SET_BUCKET = "set_bucket"
SERVICE_SET_ALL_BUCKETS = "set_all_buckets"
SERVICE_SET_MULTIPLIER = "set_multiplier"
SERVICE_SET_ALL_MULTIPLIERS = "set_all_multipliers"
SERVICE_SET_ZONE = "set_zone"
SERVICE_ENTITY_ID = "entity_id"
SERVICE_CLEAR_WEATHERDATA = "clear_all_weather_data"
SERVICE_GENERATE_WATERING_CALENDAR = "generate_watering_calendar"
SERVICE_CREATE_RECURRING_SCHEDULE = "create_recurring_schedule"
SERVICE_UPDATE_RECURRING_SCHEDULE = "update_recurring_schedule"
SERVICE_DELETE_RECURRING_SCHEDULE = "delete_recurring_schedule"
# Operational controls (WS-5)
SERVICE_SET_RAIN_DELAY = "set_rain_delay"
SERVICE_CLEAR_RAIN_DELAY = "clear_rain_delay"
SERVICE_RUN_ZONE = "run_zone"
SERVICE_STOP_ZONE = "stop_zone"
# Gardena distributor services
SERVICE_DISTRIBUTOR_SET_OUTLET = "distributor_set_outlet"
SERVICE_DISTRIBUTOR_RESYNC_HOME = "distributor_resync_home"
SERVICE_DISTRIBUTOR_TEST_RUN = "distributor_test_run"
SERVICE_DISTRIBUTOR_RUN_NOW = "distributor_run_now"
ATTR_DISTRIBUTOR_ID = "distributor_id"
ATTR_OUTLET = "outlet"
# Run-log detail marker for a run a user stopped early.
RUN_DETAIL_STOPPED = "stopped"
# run_zone / set_rain_delay call params
ATTR_DURATION_MINUTES = "duration"  # whole minutes for a custom manual run
ATTR_RAIN_DELAY_UNTIL = "until"  # ISO datetime to hold until
ATTR_RAIN_DELAY_HOURS = "hours"  # convenience: hold for N hours from now
# Events
EVENT_RECURRING_SCHEDULE_TRIGGERED = "recurring_schedule_triggered"

# --- Self-closing valve mode (Phase 1) -------------------------------------
ZONE_WATERING_MODE = "watering_mode"  # per-zone actuation adapter
WATERING_MODE_CLASSIC = "classic"  # default: open -> sleep -> close
WATERING_MODE_SERVICE = "service"  # fire a service, valve self-closes

# 'service' adapter per-zone config. Device specifics live in the run_service
# script (see the shipped valve blueprints), not here.
ZONE_RUN_SERVICE = "run_service"  # "domain.service" e.g. "script.irrigation_beet"
ZONE_DURATION_FIELD = "duration_field"  # data key the duration is passed under
ZONE_DURATION_UNIT = "duration_unit"  # DURATION_UNIT_SECONDS | DURATION_UNIT_MINUTES
ZONE_STOP_SERVICE = "stop_service"  # optional "domain.service" for early stop
# Optional entity that reflects the real valve/switch state the run_service drives
# (e.g. "valve.beet"). When set, the open is confirmed against it (poll-only, no
# re-actuation); when unset, the service run is treated as write-only and credited
# optimistically. The momentary run_service script is NOT a valid liveness signal.
ZONE_CONFIRM_ENTITY = "confirm_entity"
# Observed-watering (opt-in): the physical valve/switch to watch for EXTERNAL
# runs of a service/self-closing zone (which has no linked_entity). Distinct from
# confirm_entity (run confirmation). Only consulted when observed_watering_enabled.
ZONE_OBSERVED_ENTITY = "observed_entity"
# Optional soil-moisture sensor (per zone) + wet threshold. When both are set,
# an AUTOMATIC run skips the zone while the sensor reads strictly above the
# threshold (higher % = wetter), and resets the zone's bucket to 0. Skip-only:
# soil moisture is never an ET input. Unavailable/non-numeric reading = fail-open.
ZONE_SOIL_MOISTURE_SENSOR = "soil_moisture_sensor"
ZONE_SOIL_MOISTURE_THRESHOLD = "soil_moisture_threshold"

DURATION_UNIT_SECONDS = "seconds"
DURATION_UNIT_MINUTES = "minutes"

# Persisted in-flight self-closing runs (reboot resilience) — on Config
CONF_ACTIVE_VALVE_RUNS = "active_valve_runs"
RUN_ZONE_ID = "zone_id"
RUN_ENTITY_ID = "entity_id"  # the run_service string (for logging/identity)
RUN_STARTED = "started"  # ISO-8601 UTC
RUN_PLANNED_SECONDS = "planned_seconds"
RUN_PLANNED_MM = "planned_mm"
RUN_MODE = "mode"
RUN_CREDITED = "credited"

# Per-run events (new in this feature)
EVENT_IRRIGATE_STARTED = "irrigation_started"
EVENT_IRRIGATE_FINISHED = "irrigation_finished"
EVENT_ZONE_PROBLEM = "zone_problem"
EVENT_ZONE_SKIPPED = "zone_skipped"  # per-zone soil-moisture veto (carries
# zone_id, zone, entity_id, reason, observed, threshold)

# --- Master switch / pump control (instance-level, fully optional) ----------
CONF_MASTER_ENTITY = "master_entity"  # switch/valve/input_boolean, or None
CONF_MASTER_SETTLE_SECONDS = "master_settle_seconds"  # wait after on before zone 1
CONF_MASTER_KICK_ENABLED = "master_kick_enabled"  # pulse off->pause->on first
CONF_MASTER_KICK_PAUSE_SECONDS = "master_kick_pause_seconds"  # the off<->on gap
CONF_MASTER_OFF_AFTER = "master_off_after"  # turn off after cycle (else stay on)
CONF_DEFAULT_MASTER_SETTLE_SECONDS = 10
CONF_DEFAULT_MASTER_KICK_PAUSE_SECONDS = 1.0

# Run-log tags
RUN_TRIGGER_SELF_CLOSING = "self_closing"
RUN_DETAIL_SELF_CLOSING_STOPPED = "self_closing_stopped"
PROBLEM_VALVE_DID_NOT_OPEN = "valve_did_not_open"

# --- Gardena Wasserverteiler automatic (distributor) -------------------------
# Position-state of the open-loop outlet counter. A distributor only waters via
# a schedule when synced AND commissioning-confirmed (see store/engine).
POSITION_STATE_SYNCED = "synced"
POSITION_STATE_UNCERTAIN = "uncertain"

# Zone membership (a zone behind a distributor has no own valve/schedule).
ZONE_DISTRIBUTOR_ID = "distributor_id"
ZONE_OUTLET_NUMBER = "outlet_number"

# Hard floor for the pressure-bleed pause and the skip-pulse (spec 4.5): below
# this the device may silently fail to advance (undetectable open-loop desync).
DISTRIBUTOR_MIN_PAUSE_SECONDS = 10
DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS = 10
DISTRIBUTOR_DEFAULT_PAUSE_SECONDS = 300
DISTRIBUTOR_DEFAULT_SKIP_PULSE_SECONDS = 30
# Fixed watering window per outlet during a commissioning test-run (spec 10).
DISTRIBUTOR_TEST_RUN_SECONDS = 30

# Fired when a distributor halts on doubtful sync (carries distributor_id + reason).
EVENT_DISTRIBUTOR_HALTED = "distributor_halted"
# Wall-clock safety margin added to a finish-anchored cycle estimate (spec §5.5).
DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS = 30
DISTRIBUTOR_PHASE_WATERING = "watering"
DISTRIBUTOR_PHASE_PAUSING = "pausing"
# b14: transient busy marker set the instant a cycle claims the distributor —
# before the slower master-start — so the panel gates the other members fast.
# Overwritten by the first outlet's real WATERING persist; never actuates.
DISTRIBUTOR_PHASE_STARTING = "starting"
DISTRIBUTOR_REASON_RESTART_MID_ADVANCE = "restart_mid_advance"
# Run-log trigger tag for distributor-delivered watering.
RUN_TRIGGER_DISTRIBUTOR = "distributor"
# Run-log trigger tag for observed (externally run) watering (opt-in): the valve
# ran outside Smart Irrigation and its estimated volume was credited.
RUN_TRIGGER_OBSERVED = "observed"

# Distributor inlet-watch reaction to a foreign inlet pulse (E4).
DISTRIBUTOR_WATCH_MODE_COUNT = "count"  # advance the tracked position
DISTRIBUTOR_WATCH_MODE_WARN = "warn"  # mark uncertain (de-arm + notify)
DISTRIBUTOR_WATCH_MODE_IGNORE = "ignore"  # do not observe
DISTRIBUTOR_REASON_FOREIGN_PULSE = "foreign_inlet_pulse"

# Distributor flow-metering poll interval (seconds) for volume measurement (Part A).
DISTRIBUTOR_FLOW_POLL_SECONDS = 5
# Feature flag (Part A ships RATE-ONLY, matching JustChr's existing zone flow code):
# cumulative (total) counters are NOT armed for distributor measurement yet. When a
# distributor's flow_sensor is a cumulative counter, measurement degrades to
# time-based crediting. The cumulative branch in _dist_measure_window is retained and
# unit-tested (with this flag on) so a later JOINT zone+member cumulative rollout only
# has to flip this to True. Do NOT arm without also arming the zone path: cumulative
# should be enabled for zones and distributor member zones together, otherwise the two
# crediting paths (measured vs time-based) could double-count against a shared bucket.
DISTRIBUTOR_CUMULATIVE_METERING_ENABLED = False
