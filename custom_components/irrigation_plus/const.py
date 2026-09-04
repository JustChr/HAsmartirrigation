"""Store constants."""


class SmartIrrigationError(Exception):
    """Exception raised for errors in the Irrigation Plus integration."""


VERSION = "v2026.09.05"
NAME = "Irrigation Plus"
MANUFACTURER = "@JustChr"

DOMAIN = "irrigation_plus"

# The identity this integration shipped under until the #120 rename. These are
# HISTORICAL FACTS about existing installs, not aliases of DOMAIN/NAME — they
# must never be derived from them. Used by the storage-key migration, the
# leftover-directory Repair, the legacy Lovelace card alias, and the legacy
# duration unique_id migration below.
LEGACY_DOMAIN = "smart_irrigation"
LEGACY_NAME = "Smart Irrigation"

# Set in the new config entry's data when the user accepted the import of a
# pre-#120 install. Gates the storage copy, so declining the offer really does
# give a clean install even though the old storage file is still on disk.
CONF_MIGRATED_FROM_LEGACY = "migrated_from_legacy"
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
# including manual/automation runs outside Irrigation Plus, estimated from the
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
# Continuous updates: ingest sensor-sourced weather values when the entity
# CHANGES instead of sampling them on the auto-update timer. The default hourly
# poll misses the real daily min/max and makes a Riemann-summed field (solar
# radiation) coarse — an ET accuracy loss, not a cosmetic one. Key name is
# deliberately altmenorg's ("continuousupdates") so an install that had the
# option enabled there keeps it after switching forks (both forks share the
# storage file). Off by default.
CONF_CONTINUOUS_UPDATES = "continuousupdates"
CONF_DEFAULT_CONTINUOUS_UPDATES = False
# Hourly calculation: sum FAO-56 hourly ETo over the window and replay the water
# balance hour by hour, instead of running the daily equation on window-mean
# weather. Its own switch rather than riding on continuousupdates, for two
# reasons pulling the same way: an install that enabled continuous updates asked
# for denser ingestion and would otherwise get a change of up to 12% in its ET,
# structured by cloudiness, with no further opt-in; and an hourly-POLLED install
# runs this form within 8.4% of dense truth with no systematic bias, so there is
# no technical reason to withhold it there. Off by default.
CONF_HOURLY_CALCULATION = "hourlycalculation"
CONF_DEFAULT_HOURLY_CALCULATION = False
# Debounce (milliseconds) coalescing a burst of sensor changes into one
# post-append update per sensor group. altmenorg defaulted to 100 ms, which is
# effectively no debounce for a chatty sensor; 5 s costs nothing in ET accuracy
# (readings are appended immediately either way — only the follow-up work is
# delayed) and collapses bursts. 0 disables the debounce entirely.
CONF_SENSOR_DEBOUNCE = "sensor_debounce"
CONF_DEFAULT_SENSOR_DEBOUNCE = 5000
# Which unit system the ZONE values currently on disk were written under.
#
# Zone depths, size and throughput are stored in the user's DISPLAY units, so
# the digits are meaningless without knowing which system produced them. HA's
# own `hass.config.units` only says what is configured NOW, and the coordinator's
# in-memory `previous_unit_system` is re-seeded from it on every start — so a
# unit change made in configuration.yaml plus a restart is invisible. Persisting
# it is what makes the flip detectable across a restart, and what makes the
# conversion idempotent (the guard is stored-vs-current, not an event). Issue #67.
CONF_STORED_UNIT_SYSTEM = "stored_unit_system"
UNIT_SYSTEM_METRIC = "metric"
UNIT_SYSTEM_US_CUSTOMARY = "us_customary"
# Opt-in run-history transparency (2026-07-11): when on, a scheduled run that
# does NOT water a zone/member purely because it has no water demand (bucket
# satisfied / duration 0) leaves one "skipped: no_demand" run-log entry instead
# of vanishing silently. Default off so existing installs stay byte-identical.
CONF_LOG_NO_DEMAND = "log_no_demand"
CONF_DEFAULT_LOG_NO_DEMAND = False
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
# One-shot latch: has this store's solar_azimuth schedules had their bearings
# repaired after the issue #81 sign fix? See coordinator
# async_correct_solar_azimuth_bearings.
CONF_AZIMUTH_BEARING_CORRECTED = "azimuth_bearing_corrected"
# One-shot latch: has this store had its legacy calculate/update recurring
# schedules removed? See coordinator async_drop_legacy_schedule_actions.
CONF_LEGACY_SCHEDULE_ACTIONS_REMOVED = "legacy_schedule_actions_removed"
# Run-log / skip detail token recorded when a scheduled run is held back by the
# rain delay (surfaced in the run history + outlook like the other skip ids).
SKIP_REASON_PAUSED = "paused"
# Run-log / skip token recorded when a zone is skipped because its soil-moisture
# sensor reads wetter than the zone's threshold (per-zone, automatic path only).
SKIP_REASON_SOIL_MOISTURE = "soil_moisture"
# No-demand skip (opt-in, CONF_LOG_NO_DEMAND): the zone/member simply had no
# deficit this run. Localized in the run-log via panels.zones.outlook.checks.
SKIP_REASON_NO_DEMAND = "no_demand"
# Run-log / skip token recorded when the per-zone days-between guard holds a
# zone back. Must stay equal to skip_conditions.SKIP_DAYS_BETWEEN: both name the
# same panels.zones.outlook.checks key, and a mismatch renders the history entry
# as a raw code. Pinned by
# test_days_between_per_zone.py::test_the_detail_matches_the_id_the_frontend_localizes
SKIP_REASON_DAYS_BETWEEN = "days_between"

# Days between irrigation configuration
CONF_DAYS_BETWEEN_IRRIGATION = "days_between_irrigation"
CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION = 0  # 0 = no restriction (default behavior)
CONF_DAYS_SINCE_LAST_IRRIGATION = "days_since_last_irrigation"
CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION = 0

# Enhanced Scheduling Configuration
CONF_RECURRING_SCHEDULES = "recurring_schedules"
CONF_DEFAULT_RECURRING_SCHEDULES = []

# schedule id -> ISO-8601 target of the occurrence that schedule last fired for.
# Runtime state rather than configuration, kept in the config document for the
# same reason as CONF_ACTIVE_VALVE_RUNS: it is a fact about a run that has to
# outlive the object holding it. See RecurringScheduleManager.
CONF_FIRED_OCCURRENCES = "fired_occurrences"

# Recurring Schedule Keys
SCHEDULE_CONF_ID = "id"
SCHEDULE_CONF_NAME = "name"
SCHEDULE_CONF_ENABLED = "enabled"
SCHEDULE_CONF_DAYS_OF_WEEK = "days_of_week"
SCHEDULE_CONF_DAY_OF_MONTH = "day_of_month"
SCHEDULE_CONF_INTERVAL_HOURS = "interval_hours"
SCHEDULE_CONF_START_TIME = "start_time"  # Optional HH:MM clock anchor for interval
SCHEDULE_CONF_START_DATE = "start_date"
SCHEDULE_CONF_END_DATE = "end_date"
SCHEDULE_CONF_ZONES = "zones"  # List of zone IDs or "all"
SCHEDULE_CONF_ACTION = "action"
SCHEDULE_ACTION_IRRIGATE = "irrigate"
# The only action a recurring schedule may carry. "calculate" and "update" were
# retired when the global daily settings took over deciding when a calculation
# runs; two independent things owning that produced duplicated work. The store
# has never kept them, so a schedule carrying one is refused on the way in
# rather than accepted and dropped later. See
# RecurringScheduleManager._validate_schedule_data and
# SmartIrrigationCoordinator.async_drop_legacy_schedule_actions.
SCHEDULE_SUPPORTED_ACTIONS = (SCHEDULE_ACTION_IRRIGATE,)

# Recurrence: how often a schedule comes round. Independent of where in the
# day it lands — that is the Start/Finish bound below. Closes the old gap
# where a sun-relative schedule could not be restricted to weekdays.
SCHEDULE_RECURRENCE_DAILY = "daily"
SCHEDULE_RECURRENCE_WEEKLY = "weekly"
SCHEDULE_RECURRENCE_MONTHLY = "monthly"
SCHEDULE_RECURRENCE_INTERVAL = "interval"
SCHEDULE_RECURRENCES = [
    SCHEDULE_RECURRENCE_DAILY,
    SCHEDULE_RECURRENCE_WEEKLY,
    SCHEDULE_RECURRENCE_MONTHLY,
    SCHEDULE_RECURRENCE_INTERVAL,
]
SCHEDULE_CONF_RECURRENCE = "recurrence"

# A run's window is two bounded ends, Start and Finish, each independently
# "none" (unbounded) or one of a clock time / sunrise / sunset / solar
# azimuth. Not meaningful for an interval recurrence, which has no time of
# day and therefore no window.
SCHEDULE_BOUND_MODE_NONE = "none"
SCHEDULE_BOUND_MODE_TIME = "time"
SCHEDULE_BOUND_MODE_SUNRISE = "sunrise"
SCHEDULE_BOUND_MODE_SUNSET = "sunset"
SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH = "solar_azimuth"
SCHEDULE_BOUND_MODES = [
    SCHEDULE_BOUND_MODE_NONE,
    SCHEDULE_BOUND_MODE_TIME,
    SCHEDULE_BOUND_MODE_SUNRISE,
    SCHEDULE_BOUND_MODE_SUNSET,
    SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
]
SCHEDULE_DEFAULT_BOUND_MODE = SCHEDULE_BOUND_MODE_NONE

SCHEDULE_CONF_START_MODE = "start_mode"
# SCHEDULE_CONF_START_TIME (above) doubles as the HH:MM value when
# start_mode = "time" — the same key an interval schedule's own optional
# clock anchor already used, which never collides since a schedule is never
# both interval and start/finish-bounded at once.
SCHEDULE_CONF_START_OFFSET = "start_offset"  # signed minutes, sun-relative modes
SCHEDULE_CONF_START_AZIMUTH = "start_azimuth"  # degrees, start_mode = solar_azimuth

SCHEDULE_CONF_FINISH_MODE = "finish_mode"
SCHEDULE_CONF_FINISH_TIME = "finish_time"  # HH:MM, finish_mode = "time"
SCHEDULE_CONF_FINISH_OFFSET = "finish_offset"  # signed minutes, sun-relative modes
SCHEDULE_CONF_FINISH_AZIMUTH = "finish_azimuth"  # degrees, finish_mode = solar_azimuth

# Which end the run is pinned to. Only meaningful when both Start and Finish
# are bounded — with a single bound, that bound is unambiguously the anchor.
SCHEDULE_CONF_ANCHOR = "anchor"
SCHEDULE_ANCHOR_START = "start"
SCHEDULE_ANCHOR_FINISH = "finish"
SCHEDULE_ANCHORS = [SCHEDULE_ANCHOR_START, SCHEDULE_ANCHOR_FINISH]
SCHEDULE_DEFAULT_ANCHOR = SCHEDULE_ANCHOR_FINISH

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
# When the automatic calculation runs. "fixed_time" keeps calctime's original
# meaning; "before_run" calculates when each irrigate schedule plans its run, so
# the run is sized from a ledger minutes old rather than one committed hours
# earlier. Existing installs migrate to fixed_time with their current calctime.
CONF_AUTO_CALC_MODE = "autocalcmode"
CONF_AUTO_CALC_MODE_FIXED_TIME = "fixed_time"
CONF_AUTO_CALC_MODE_BEFORE_RUN = "before_run"
CONF_AUTO_CALC_MODES = [CONF_AUTO_CALC_MODE_FIXED_TIME, CONF_AUTO_CALC_MODE_BEFORE_RUN]
CONF_DEFAULT_AUTO_CALC_MODE = CONF_AUTO_CALC_MODE_FIXED_TIME
# Under "before_run" a night with no run commits nothing, and after seven days
# the replay window outruns BUFFER_RETENTION and the live estimate silently
# falls back to a week-old bucket. The midnight tracker holds the invariant
# instead of guarding the cases: the ledger is never more than this stale.
AUTO_CALC_MAX_LEDGER_AGE_HOURS = 24
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
# NOTE: this and the two depth defaults below are authored in MILLIMETRES, but the
# zone fields they seed are stored in the user's DISPLAY units. Always materialise
# them through helpers.zone_depth_default(); see that docstring for why.
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

# The panel's custom-element name and every served path are DERIVED from DOMAIN,
# never written out. Both projects shipped a hardcoded
# "/api/panel_custom/smart-irrigation", so the renamed integration went on
# serving the ORIGINAL project's bundle at a path it did not own (altmenorg hit
# exactly this, #120). Deriving makes that class of collision impossible.
PANEL_SLUG = DOMAIN.replace("_", "-")  # "irrigation-plus"
PANEL_NAME = PANEL_SLUG
PANEL_FILENAME = f"dist/{PANEL_SLUG}.js"
PANEL_URL = f"/api/panel_custom/{PANEL_SLUG}"
PANEL_TITLE = NAME
PANEL_ICON = "mdi:sprinkler"

# Lovelace custom card: a second bundle served to all users (not just admins)
# and auto-loaded via add_extra_js_url, so non-admins can add the zones card to
# their own dashboards.
CARD_STATIC_ROOT = f"/{DOMAIN}_card"
CARD_FILENAME = f"dist/{PANEL_SLUG}-card.js"
CARD_URL = f"{CARD_STATIC_ROOT}/{PANEL_SLUG}-card.js"

# The card file above is a tiny stub auto-loaded on every page; it lazy-imports
# this heavy implementation bundle only when a card actually renders (keep
# FULL_CARD_URL in sync with const.ts).
FULL_CARD_FILENAME = f"dist/{PANEL_SLUG}-card-impl.js"
FULL_CARD_URL = f"{CARD_STATIC_ROOT}/{PANEL_SLUG}-card-impl.js"

# Localization static files: only en.json is bundled into the frontend
# bundles; the other languages are served from here and fetched on demand by
# the frontend (keep LANG_URL in sync with LANG_BASE_URL in frontend const.ts).
LANG_FOLDER = "localize/languages"
LANG_URL = f"/{DOMAIN}_static/languages"

# The paths the pre-#120 releases served. The stale-resource cleanup and the
# legacy card alias need these; they are historical facts, not aliases.
LEGACY_PANEL_SLUG = LEGACY_DOMAIN.replace("_", "-")  # "smart-irrigation"
LEGACY_CARD_STATIC_ROOT = f"/{LEGACY_DOMAIN}_card"
LEGACY_CARD_URL = f"{LEGACY_CARD_STATIC_ROOT}/{LEGACY_PANEL_SLUG}-card.js"

# The compatibility shim that re-registers the pre-#120 card tag. Served from
# OUR static root (the legacy one belongs to the other project now) and only
# when no foreign smart_irrigation integration is installed.
LEGACY_ALIAS_FILENAME = f"dist/{PANEL_SLUG}-card-legacy.js"
LEGACY_ALIAS_URL = f"{CARD_STATIC_ROOT}/{PANEL_SLUG}-card-legacy.js"

MIGRATION_GUIDE_URL = (
    "https://justchr.github.io/HAsmartirrigation/installation-migration"
)

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
# Per-zone days-between-irrigation counter. The global counter it replaces was
# reset by ANY watered run, so a run that only reached the first few zones still
# told the guard everything had watered and the next night was skipped whole —
# the tail of the priority order could never come up. Bumped at local midnight,
# reset only for zones that actually received water.
ZONE_DAYS_SINCE_IRRIGATION = "days_since_irrigation"
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
# MILLIMETRES, like the other depth defaults — materialise via
# helpers.zone_depth_default(). Irrigation gates on `bucket < bucket_threshold`,
# so seeding an imperial zone with the raw mm number means -254 mm and silently
# suppresses every run.
# New zones require a 10 mm deficit before irrigating (bucket < -10).
# Stored 0-or-negative; 0 = irrigate on any deficit. Existing zones keep their
# stored value — this only seeds newly created zones.
CONF_DEFAULT_BUCKET_THRESHOLD = -10.0
ZONE_FLOW_SENSOR = "flow_sensor"
FLOW_POLL_INTERVAL = 15  # seconds between flow meter readings
# Rate sensors: the widest inter-sample gap a FlowMeter still integrates across (4 polls).
# A wider gap means the sensor went 'unavailable' and samples were dropped; integrating
# the recovered rate over it would over-credit. See FlowMeter(max_gap_s=...).
FLOW_MAX_GAP_SECONDS = FLOW_POLL_INTERVAL * 4
# Unified flow-measurement engine (flow_metering.FlowMeter). Per-zone override for how a
# totalizer flow sensor is read; 'auto' learns per_run vs lifetime across runs. See the
# flow_metering module docstring and flow_learn_next_streak / flow_learn_resolve.
ZONE_FLOW_COUNTER_TYPE = "flow_counter_type"
FLOW_COUNTER_AUTO = "auto"
FLOW_COUNTER_PER_RUN = "per_run"
FLOW_COUNTER_LIFETIME = "lifetime"
FLOW_NEAR_ZERO_FRAC = 0.1  # per_run "near zero" reset floor = max(FLOOR, FRAC x last)
FLOW_NEAR_ZERO_FLOOR = 1.0
# Cross-run learning state (auto mode): previous run's end litres + consecutive-open-reset
# streak. Internal (not user-set). See flow_metering.flow_learn_next_streak / _resolve.
ZONE_FLOW_LAST_END = "flow_last_end"
ZONE_FLOW_RESET_STREAK = "flow_reset_streak"
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
# How long a confirmed-open service valve may read "off" before its run is written
# off. The confirm poll above has already seen the valve on, so this covers only
# the gap between that and the subscription landing; anything longer than a poll
# or two means the valve shut immediately and the run delivered nothing. Far
# shorter than OPENSPRINKLER_ACCEPT_SECONDS, which waits on a controller's queue —
# a service zone has no queue to wait behind.
SERVICE_WATCH_GIVE_UP_SECONDS = 60
# How long a confirmed service valve must stay off before that is read as the end
# of its run. These are the valves _confirm_valve_running is written around --
# sleepy Zigbee/Tuya timers that "actuate but report their new state back slowly,
# or silently drop the first command" -- so a single off sample is not evidence
# the water stopped. Without this debounce one late or spurious report settles a
# run as a partial and reverses the credit for water that never stopped flowing.
SERVICE_WATCH_SETTLE_SECONDS = 5
VALVE_CONFIRM_POLL = 1
# Re-send the open command once, this many seconds into the confirm window, to
# recover a command silently dropped by a sleepy valve.
VALVE_CONFIRM_RETRY_AT = 15
# How long a flow zone with no maximum_duration is allowed to run before its
# safety timeout closes it. A flow run is volume-targeted, so unlike a timed run
# nothing else bounds it. Named rather than repeated inline because the pricing
# in duration_math has to clamp to the same ceiling the run stops at, and two
# copies of a number are two numbers.
FLOW_SAFETY_TIMEOUT = 14400
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
# outside Irrigation Plus and its estimated volume was credited to the bucket.
RUN_RESULT_OBSERVED = "observed"

# Bucket movements that happened part-way through the current calculation
# window: irrigation credits, and the reconciles that correct them. Each entry
# is {ts: iso, mm: float}, newest last.
#
# The replayed water balance takes the stored bucket as the level at the window
# START, so without these a credit deposited at 10:00 in a window that opened at
# 02:00 is charged the whole window's drainage instead of the hours it was
# actually there. Drainage only acts on a surplus, so the error needs a run that
# overshoots the deficit (a manual run at a chosen duration, a multiplier above
# 1, observed watering) — but when it lands it is worth multiple mm of bucket,
# it does not wash out at the next calculation, and it always reads the zone as
# drier than it is. See calculation.calculate_module.
#
# Held in mm regardless of the display unit system, unlike the bucket they
# describe: a list cannot be listed in unit_system.ZONE_DEPTH_FIELDS, so storing
# them in display units would leave them silently reinterpreted by a metric/
# imperial flip.
ZONE_PENDING_BUCKET_EVENTS = "pending_bucket_events"
# Consumed by every calculation, so reaching this cap means calculation has been
# failing for a long time; the oldest are dropped rather than growing the store.
# Sized so a single longest-possible run cannot truncate itself: a metered run
# commits its progress every RUN_COMMIT_INTERVAL, which over the default
# maximum_duration of 4 h is 240 entries. Dropping the oldest is safe either way
# -- water is still conserved, because the replay starts from the bucket minus
# only what it kept -- but a dropped credit is back to being charged the whole
# window, which is the thing this exists to avoid.
PENDING_BUCKET_EVENTS_MAX = 500

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

# Plausibility ceiling on an ingested solar-radiation reading, as a multiple of
# the clear-sky maximum for that moment. Broken-cloud edge enhancement really can
# push a pyranometer above clear sky for short stretches, so the ceiling has
# headroom; nothing physical stays there.
SOLAR_CLEAR_SKY_TOLERANCE = 1.3
# Absolute floor on that ceiling, in W/m2 before conversion. Clear sky is exactly
# 0 at night and near 0 around sunrise and sunset, and a pyranometer's deadband
# noise sits at a few W/m2, so without this every night reading would clamp.
SOLAR_PLAUSIBILITY_FLOOR_W_M2 = 10.0
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
# A run cut short because it reached its schedule's finish target. The water it
# did deliver is credited; the residual carries to the next run.
RUN_DETAIL_DEADLINE = "deadline"
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
# OpenSprinkler station: dispatch opensprinkler.run_station and observe the
# station's own running sensor. A variant of the self-closing contract (the
# controller owns the close), but the run is QUEUED — the controller waters one
# station at a time — so nothing about the run may be timed from dispatch.
WATERING_MODE_OPENSPRINKLER = "opensprinkler"
# Batch/queue dispatch (issue #88): hand a controller ONE service call carrying
# the whole irrigation as an ordered list of (zone, duration), and let it run the
# list from its own queue. The motivating hardware is the ESPHome sprinkler
# component, but nothing here is ESPHome-specific — the mode is a contract about
# what each configured entity must MEAN, so plain Home Assistant helpers serve
# just as well.
#
# Like OpenSprinkler this is a self-closing contract with a queue, so nothing
# about a run may be timed from dispatch. Unlike OpenSprinkler the controller can
# PAUSE, which is why runs in this mode are timed as segments
# (see RUN_WATERED_SECONDS) and why a valve going off is not automatically the
# end of a run.
#
# A queue runs one valve at a time, so this mode is inherently SEQUENTIAL:
# ``parallel`` cannot be expressed in it. Order comes from the order of the list,
# and a rotation is expressed by listing a zone more than once with a slice of
# its duration.
WATERING_MODE_BATCH = "batch"

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
# An observed (external) run can credit no more water than SI itself would ever
# run this valve for: cap its counted seconds at the zone's maximum_duration plus
# a small margin so a legitimate external run finishing just past the cap is not
# clipped. Guards non-flow zones (no sensor to contradict a stuck-open valve).
# NOT a ceiling on measured flow: since #102/#111 a flow sensor's reading is the
# authority and is credited as-is. See ObservedWateringMixin.
OBSERVED_CAP_MARGIN_SECONDS = 30
# Shortest external run that may feed the flow-calibration advisory (#111 follow-up).
# The advisory samples an observed RATE (litres / minutes), so a short run divides a
# coarsely-quantised volume by a very small number. Residential meters commonly pulse
# at 1 L: a 6 s open on a 3.1 L/min zone registers either 0 L (already gated out by
# `measured_l > 0`) or one 1 L pulse, reading as 10 L/min — a +223% deviation on a
# CORRECTLY configured zone. Three of those fill FLOW_CAL_MIN_SAMPLES, fire a
# persistent notification recommending a throughput that was never wrong, AND evict
# the healthy samples that real runs contributed to the 5-deep window.
# Sized so one pulse of quantisation stays inside FLOW_CAL_DEVIATION: at 3.1 L/min a
# 1 L error is 15% of the reading only once the run exceeds ~130 s, so 300 s leaves
# room for a slower zone. Erring strict is deliberate — a missed sample only makes the
# advisory less eager, while a false one tells the user to break a working setting.
# Unlike self-closing and the distributor, which sample SI's OWN planned runs, the
# observed path sees any external valve open, including a few seconds of hand-testing.
OBSERVED_FLOW_CAL_MIN_SECONDS = 300
# Per-member flow-calibration advisory (distributor can't-stop members only). A
# member whose valve can't early-stop runs a fixed window; if the configured
# throughput is wrong it silently over/under-waters. We keep a rolling list of
# measured-vs-target volume samples and a one-shot "advised" marker so a single HA
# persistent notification recommends a corrected throughput once the mean signed
# deviation over >= FLOW_CAL_MIN_SAMPLES runs exceeds FLOW_CAL_DEVIATION. Advisory
# only — nothing is auto-applied. See DistributorMixin._dist_flow_calibration_check.
ZONE_FLOW_CAL_SAMPLES = "flow_calibration_samples"
ZONE_FLOW_CAL_ADVISED = "flow_calibration_advised"
FLOW_CAL_MIN_SAMPLES = 3
FLOW_CAL_MAX_SAMPLES = 5
FLOW_CAL_DEVIATION = 0.15
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
RUN_PRE_BUCKET = "pre_bucket"  # zone bucket BEFORE the optimistic self-closing credit
# The bucket level this run's credit may reach, decided ONCE at dispatch.
# _run_ceiling consumes the live-estimate marker, so it answers correctly exactly
# once; every later write for the same run (the measured reconcile at finish, an
# early stop's correction) has to clamp against this recorded number instead of
# re-deriving one, or it undoes the dispatch clamp and settles the run at
# maximum_bucket again -- the surplus issue #88 reports. Absent on a run
# persisted before this field existed (upgrade mid-run), which falls back to the
# old maximum_bucket clamp.
RUN_CEILING = "ceiling"
# ISO-8601 UTC instant the hardware was OBSERVED to start watering, absent until
# it does. RUN_STARTED is the DISPATCH time, which for a queued OpenSprinkler run
# can precede the water by hours; timing anything from it would finalise a zone
# still sitting in the controller's queue. Two consumers read this: the run's own
# finalisation (planned window, delivered fraction) and
# RunStateMixin._self_closing_run_in_flight.
RUN_OBSERVED_START = "observed_start"
# Entity whose on/off state IS the run, resolved once at dispatch and persisted so
# restart reconciliation can re-subscribe without re-deriving it. Re-derivation
# reads state attributes, and the integration that owns them may not have loaded
# yet when Irrigation Plus reconciles.
RUN_WATCH_ENTITY = "watch_entity"
# --- Segmented run time (issue #88) ----------------------------------------
# A run is normally one contiguous stretch of watering, so its length is simply
# "now minus the observed start". That breaks for a controller that can PAUSE:
# the ESPHome sprinkler component turns the valve switch off on a pause and keeps
# the remaining time itself, so a twenty-minute pause inside a run would be
# charged as twenty minutes of water — over-crediting the bucket and finishing
# the run early.
#
# So a run in a mode that can pause records the SUM OF ITS WATERING SEGMENTS
# instead: RUN_WATERED_SECONDS accumulates the segments that have closed, and
# RUN_SEGMENT_STARTED holds the start of the one currently open (absent while
# paused). Both are persisted, so a restart mid-pause still adds up.
#
# Written ONLY by a mode whose WatchPolicy is ``segmented``, and read only when
# present — so the OpenSprinkler mode, whose controller has no pause, keeps the
# contiguous-window timing it has always had, down to preferring the
# controller's own reported start over the observation instant.
RUN_WATERED_SECONDS = "watered_seconds"
RUN_SEGMENT_STARTED = "segment_started"

# Per-run events (new in this feature)
EVENT_IRRIGATE_STARTED = "irrigation_started"
EVENT_IRRIGATE_FINISHED = "irrigation_finished"
EVENT_ZONE_PROBLEM = "zone_problem"
EVENT_ZONE_SKIPPED = "zone_skipped"  # per-zone soil-moisture veto (carries
# zone_id, zone, entity_id, reason, observed, threshold)

# --- Batch/queue dispatch, instance-level config (issue #88) ----------------
# The service handed the whole plan. Receives one key, BATCH_FIELD_ZONES, whose
# value is the ordered list of {zone_id, zone_name, duration} the controller
# should queue and run.
CONF_BATCH_RUN_SERVICE = "batch_run_service"
# The service that stops the irrigation AND CLEARS THE QUEUE. Both halves are
# required and it is deliberately ONE user-supplied script rather than a
# hard-coded pair: the ESPHome spelling is sprinkler.shutdown +
# sprinkler.clear_queued_valves, but the mode must not know that.
#
# Clearing the queue is a safety requirement, not tidiness. Stopping one zone
# stops the cycle but LEAVES THE QUEUE INTACT, so zones already queued would
# start watering later with nothing supervising them — the same unsupervised-run
# failure the OpenSprinkler teardown was fixed for.
CONF_BATCH_STOP_SERVICE = "batch_stop_service"
# Optional. ONE indicator per controller that reads on while the irrigation is
# paused. A queue waters one valve at a time, so the paused zone is unambiguously
# the one with an observed start and no finish — no per-zone sensor is needed.
# Without it a pause is indistinguishable from the controller ending the run.
CONF_BATCH_PAUSED_ENTITY = "batch_paused_entity"
# Optional bound on a pause, in seconds, and an optional service called when it
# expires so the user decides what giving up means on their hardware (resume,
# shut down, clear the queue). Irrigation Plus settles the run for what was
# actually delivered either way.
CONF_BATCH_PAUSE_TIMEOUT = "batch_pause_timeout"
CONF_BATCH_PAUSE_TIMEOUT_SERVICE = "batch_pause_timeout_service"
# Key the plan is passed under in the run service's data.
BATCH_FIELD_ZONES = "zones"
# What an UNSET pause timeout means. Deliberately a generous bounded backstop
# rather than "no bound at all": an unbounded pause is harmless to the controller
# but not to this integration's bookkeeping, where a run that never ends holds
# its zone against re-dispatch, holds the master, and keeps an optimistic bucket
# credit for water that never fell — so the zone reads as watered while it is
# dry, indefinitely. Pause deliberately for an hour and nothing happens; leave it
# paused for a week and the integration eventually stops believing the zone was
# watered.
BATCH_PAUSE_BACKSTOP_SECONDS = 6 * 3600
# How long a valve going off is held open as possibly-a-pause before it is
# treated as the end of the run. A pause turns the valve off and raises the
# paused indicator, and nothing orders those two updates; without this the
# ordering decides whether a paused run is resumed or settled as a partial with
# its credit already reversed. Only applied when a paused entity is configured.
BATCH_PAUSE_SETTLE_SECONDS = 5

# --- Master switch / pump control (instance-level, fully optional) ----------
CONF_MASTER_ENTITY = "master_entity"  # switch/valve/input_boolean, or None
CONF_MASTER_SETTLE_SECONDS = "master_settle_seconds"  # wait after on before zone 1
CONF_MASTER_KICK_ENABLED = "master_kick_enabled"  # pulse off->pause->on first
CONF_MASTER_KICK_PAUSE_SECONDS = "master_kick_pause_seconds"  # the off<->on gap
CONF_MASTER_OFF_AFTER = "master_off_after"  # turn off after cycle (else stay on)
CONF_DEFAULT_MASTER_SETTLE_SECONDS = 10
CONF_DEFAULT_MASTER_KICK_PAUSE_SECONDS = 1.0
# Grace between the LAST consumer releasing its master hold and the cycle ending.
# Absorbs the gap between two back-to-back consumers (so a pump does not flap
# off/on between them) without meaningfully dead-heading it. Only ever applies
# once nothing holds the master any more — see MasterMixin.async_master_release.
MASTER_RELEASE_GRACE_SECONDS = 5

# Run-log tags
RUN_TRIGGER_SELF_CLOSING = "self_closing"
RUN_DETAIL_SELF_CLOSING_STOPPED = "self_closing_stopped"
PROBLEM_VALVE_DID_NOT_OPEN = "valve_did_not_open"

# --- OpenSprinkler station mode ---------------------------------------------
# The station entity (switch.<station>_station_enabled) goes in the zone's
# linked_entity; everything else is derived from its state attributes, which the
# integration builds in OpenSprinklerStationEntity.extra_state_attributes.
OPENSPRINKLER_DOMAIN = "opensprinkler"
OPENSPRINKLER_SERVICE_RUN_STATION = "run_station"
OPENSPRINKLER_SERVICE_STOP = "stop"
OPENSPRINKLER_FIELD_RUN_SECONDS = "run_seconds"
OPENSPRINKLER_FIELD_QUEUE_OPTION = "queue_option"
# Append: never pre-empt whatever the controller is already running, whether that
# is another Irrigation Plus zone or one of the controller's own programs.
OPENSPRINKLER_QUEUE_APPEND = "append"
OPENSPRINKLER_ATTR_TYPE = "opensprinkler_type"
OPENSPRINKLER_ATTR_INDEX = "index"
OPENSPRINKLER_ATTR_IS_MASTER = "is_master"
# 0 means the controller holds no run for this station. Non-zero means it has one
# — queued if the station is not running yet, live if it is. pyopensprinkler:
# "If a station is not running (sbit is 0) but has a non-zero pid, that means the
# station is in the queue waiting to run."
OPENSPRINKLER_ATTR_PROGRAM_ID = "running_program_id"
# ISO-8601 UTC instant the CONTROLLER says the station started watering, which is
# not the instant Home Assistant noticed: the integration polls, so the "on" and
# the "off" transitions are each seen up to one poll late. Measuring a run between
# the two sightings gives a window that is short as often as it is long, and a
# short one records a run the controller completed in full as an early stop. The
# controller's own start removes half of that error and all of its bias.
OPENSPRINKLER_ATTR_START_TIME = "start_time"
OPENSPRINKLER_TYPE_STATION = "station"
OPENSPRINKLER_TYPE_CONTROLLER = "controller"
# The station's sequential group id, and the controller-wide gap it inserts
# between two stations that run back to back (negative = they overlap). Both
# published from hass-opensprinkler v2.0.0; absent on anything older, and the
# group is absent below controller firmware v2.2.0(1).
OPENSPRINKLER_ATTR_GROUP = "group"
OPENSPRINKLER_ATTR_STATION_DELAY = "station_delay"
# How far the controller's reported start may sit outside the window the run
# could plausibly occupy before it is discarded for dt_util.utcnow(). It is
# derived from the controller's clock and its configured timezone offset, so a
# mis-set clock must not be able to invent a run that began in the future or
# hours ago; falling back only costs the accuracy this constant exists to gain.
OPENSPRINKLER_START_TIME_SLACK_SECONDS = 60

# How long after dispatch the controller has to acknowledge the run by putting a
# non-zero program id on the station. The integration refreshes immediately after
# run_station returns and then polls every 5 s, so this only has to absorb a
# transient communication failure (it tolerates 3 in a row before the entity goes
# unavailable) — not any part of the queue wait, which is unbounded by design.
OPENSPRINKLER_ACCEPT_SECONDS = 300
# Backstop for a run the controller acknowledged and then never started: added to
# the total planned time of the OTHER runs already in flight, because those are
# exactly what this one is queued behind. Only reached when the station entity
# stops reporting (unavailable, removed, controller offline) — a run the
# controller drops is seen within one poll as its program id returning to 0.
OPENSPRINKLER_QUEUE_MARGIN_SECONDS = 1800
# Run ended with the station never having watered.
PROBLEM_STATION_NEVER_RAN = "station_never_ran"
# The station entity, or its running sensor, could not be resolved at dispatch.
PROBLEM_STATION_UNRESOLVED = "station_unresolved"
# A station entity is linked to a zone that is NOT in OpenSprinkler mode, so the
# classic runner would have turned the station's enabled flag on instead of
# watering. The run is refused rather than performed.
PROBLEM_STATION_WRONG_MODE = "station_wrong_mode"
# Same string as PROBLEM_STATION_NEVER_RAN and deliberately a separate name: the
# two are read by different panel lookups (panels.zones.fault.* for a problem, the
# run-log detail for this), so they are free to diverge without one silently
# changing the other's copy.
RUN_DETAIL_STATION_NEVER_RAN = "station_never_ran"

# --- Batch mode fault + run-log codes (issue #88) ---------------------------
# The controller never watered this zone: it was queued, its turn never came (or
# the queue was cleared under it), and the give-up deadline expired.
PROBLEM_ZONE_NEVER_RAN = "zone_never_ran"
# The zone has no confirm_entity, which in batch mode is the valve switch and the
# ONLY thing that can start or end the run. Refused rather than dispatched: a run
# with nothing to observe would credit the bucket and never finalise.
PROBLEM_BATCH_NO_WATCH_ENTITY = "batch_no_watch_entity"
# No batch run service is configured, so there is nothing to hand the plan to.
PROBLEM_BATCH_NOT_CONFIGURED = "batch_not_configured"
# The controller took the plan but this zone's run record could not be written, so
# the zone is watering with nothing tracking it: no credit, no finish, and no
# release for the master hold taken at dispatch.
PROBLEM_BATCH_RUN_NOT_RECORDED = "batch_run_not_recorded"
# Run-log details. Separate names from the problem codes above for the same
# reason RUN_DETAIL_STATION_NEVER_RAN is: different panel lookups read them.
RUN_DETAIL_ZONE_NEVER_RAN = "zone_never_ran"
# The controller stayed paused past its bound, so the run was settled for what it
# had actually delivered.
RUN_DETAIL_BATCH_PAUSE_TIMEOUT = "batch_pause_timeout"

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
# ran outside Irrigation Plus and its estimated volume was credited.
RUN_TRIGGER_OBSERVED = "observed"

# Distributor inlet-watch reaction to a foreign inlet pulse (E4).
DISTRIBUTOR_WATCH_MODE_COUNT = "count"  # advance the tracked position
DISTRIBUTOR_WATCH_MODE_WARN = "warn"  # mark uncertain (de-arm + notify)
DISTRIBUTOR_WATCH_MODE_IGNORE = "ignore"  # do not observe
DISTRIBUTOR_REASON_FOREIGN_PULSE = "foreign_inlet_pulse"

# Distributor flow-metering poll interval (seconds) for volume measurement (Part A).
DISTRIBUTOR_FLOW_POLL_SECONDS = 5
