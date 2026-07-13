import pkg from "../package.json";
export const VERSION = `v${pkg.version}`;
export const REPO = "https://github.com/JustChr/HAsmartirrigation";
export const ISSUES_URL = REPO + "/issues";

export const PLATFORM = "smart-irrigation";
export const DOMAIN = "smart_irrigation";

// Localization: only en.json is bundled (built-in fallback); the other
// languages are served as static JSON and fetched on demand. Keep
// AVAILABLE_LANGUAGES in sync with localize/languages/*.json and LANG_BASE_URL
// in sync with LANG_URL in const.py.
export const LANG_BASE_URL = "/smart_irrigation_static/languages";

// The zones card is served as a tiny stub (auto-loaded on every page) that
// lazy-imports this heavy implementation bundle only when a card renders.
// Keep in sync with FULL_CARD_URL in const.py.
export const FULL_CARD_URL =
  "/smart_irrigation_card/smart-irrigation-card-impl.js";
export const AVAILABLE_LANGUAGES = [
  "de",
  "en",
  "es",
  "fr",
  "it",
  "nl",
  "no",
  "sk",
];

export const CONF_CALC_TIME = "calctime";
export const CONF_AUTO_CALC_ENABLED = "autocalcenabled";
export const CONF_AUTO_UPDATE_ENABLED = "autoupdateenabled";
export const CONF_AUTO_UPDATE_SCHEDULE = "autoupdateschedule";
export const CONF_AUTO_UPDATE_TIME = "autoupdatefirsttime";
export const CONF_AUTO_UPDATE_INTERVAL = "autoupdateinterval";

// Weather-based skip configuration
export const CONF_PRECIPITATION_THRESHOLD_MM = "precipitation_threshold_mm";

// Experimental, opt-in features (Setup → Experimental)
export const CONF_FORECAST_WEIGHTING_ENABLED = "forecast_weighting_enabled";
export const CONF_OBSERVED_WATERING_ENABLED = "observed_watering_enabled";
export const CONF_LIVE_ESTIMATE_ENABLED = "live_estimate_enabled";
export const CONF_DISTRIBUTORS_ENABLED = "distributors_enabled";

// Days between irrigation configuration
export const CONF_DAYS_BETWEEN_IRRIGATION = "days_between_irrigation";

// Weather service configuration
export const CONF_WEATHER_SERVICE_OWM = "Open Weather Map";
export const CONF_WEATHER_SERVICE_PW = "Pirate Weather";
export const CONF_WEATHER_SERVICE_OPENMETEO = "Open-Meteo";
export const CONF_WEATHER_SERVICE_MET = "Met Office";

export const AUTO_UPDATE_SCHEDULE_MINUTELY = "minutes";
export const AUTO_UPDATE_SCHEDULE_HOURLY = "hours";
export const AUTO_UPDATE_SCHEDULE_DAILY = "days";
export const CONF_IMPERIAL = "imperial";
export const CONF_METRIC = "metric";

export const MAPPING_DEWPOINT = "Dewpoint";
export const MAPPING_EVAPOTRANSPIRATION = "Evapotranspiration";
export const MAPPING_HUMIDITY = "Humidity";
export const MAPPING_PRECIPITATION = "Precipitation";
export const MAPPING_CURRENT_PRECIPITATION = "Current Precipitation";
export const MAPPING_PRESSURE = "Pressure";
export const MAPPING_SOLRAD = "Solar Radiation";
export const MAPPING_TEMPERATURE = "Temperature";
export const MAPPING_WINDSPEED = "Windspeed";

export const MAPPING_CONF_SOURCE_WEATHER_SERVICE = "weather_service";
export const MAPPING_CONF_SOURCE_SENSOR = "sensor";
export const MAPPING_CONF_SOURCE_STATIC_VALUE = "static";
export const MAPPING_CONF_PRESSURE_TYPE = "pressure_type";
export const MAPPING_CONF_PRESSURE_ABSOLUTE = "absolute";
export const MAPPING_CONF_PRESSURE_RELATIVE = "relative";
export const MAPPING_CONF_SOURCE_NONE = "none";
export const MAPPING_CONF_SOURCE = "source";
export const MAPPING_CONF_SENSOR = "sensorentity";
export const MAPPING_CONF_STATIC_VALUE = "static_value";
export const MAPPING_CONF_UNIT = "unit";
export const MAPPING_CONF_AGGREGATE = "aggregate";
export const MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT = "average";
export const MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT_PRECIPITATION = "delta";
export const MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT_CURRENT_PRECIPITATION =
  "average";
export const MAPPING_CONF_AGGREGATE_OPTIONS = [
  "average",
  "first",
  "last",
  "maximum",
  "median",
  "minimum",
  "riemannsum",
  "sum",
  "delta",
];

export const UNIT_M2 = "m<sup>2</sup>";
export const UNIT_SQ_FT = "sq ft";
export const UNIT_LPM = "l/minute";
export const UNIT_GPM = "gal/minute";
export const UNIT_SECONDS = "s";
export const UNIT_DEGREES_C = "°C";
export const UNIT_DEGREES_F = "°F";
export const UNIT_MM = "mm";
export const UNIT_INCH = "in";
export const UNIT_PERCENT = "%";
export const UNIT_MBAR = "millibar";
export const UNIT_HPA = "hPa";
export const UNIT_PSI = "psi";
export const UNIT_INHG = "inch Hg";
export const UNIT_KMH = "km/h";
export const UNIT_MH = "mile/h";
export const UNIT_MS = "meter/s";
export const UNIT_W_M2 = "W/m2";
export const UNIT_W_SQFT = "W/sq ft";
export const UNIT_MJ_DAY_M2 = "MJ/day/m2";
export const UNIT_MJ_DAY_SQFT = "MJ/day/sq ft";
export const UNIT_MMH = "mm/h";
export const UNIT_INCHH = "in/h";

export const ZONE_NAME = "name";
export const ZONE_SIZE = "size";
export const ZONE_THROUGHPUT = "throughput";
export const ZONE_STATE = "state";
export const ZONE_DURATION = "duration";
export const ZONE_MODULE = "module";
export const ZONE_BUCKET = "bucket";
export const ZONE_MULTIPLIER = "multiplier";
export const ZONE_MAPPING = "mapping";
export const ZONE_LEAD_TIME = "lead_time";
export const ZONE_MAXIMUM_DURATION = "maximum_duration";
export const ZONE_MAXIMUM_BUCKET = "maximum_bucket";
export const ZONE_DRAINAGE_RATE = "drainage_rate";
export const ZONE_KC = "kc";
export const ZONE_PLANT_TYPE = "plant_type";
export const ZONE_LINKED_ENTITY = "linked_entity";
export const ZONE_BUCKET_THRESHOLD = "bucket_threshold";
export const ZONE_FLOW_SENSOR = "flow_sensor";
export const ZONE_FLOW_COUNTER_TYPE = "flow_counter_type";
export const ZONE_WATERING_MODE = "watering_mode";
export const ZONE_RUN_SERVICE = "run_service";
export const ZONE_DURATION_FIELD = "duration_field";
export const ZONE_DURATION_UNIT = "duration_unit";
export const ZONE_STOP_SERVICE = "stop_service";
export const ZONE_CONFIRM_ENTITY = "confirm_entity";
export const ZONE_OBSERVED_ENTITY = "observed_entity";
export const ZONE_SOIL_MOISTURE_SENSOR = "soil_moisture_sensor";
export const ZONE_SOIL_MOISTURE_THRESHOLD = "soil_moisture_threshold";

// Plant-type presets → mid-season Kc (relative to grass reference ET0). The
// stored value is still the plain ``kc`` number; "custom" lets it be hand-set.
export const PLANT_TYPE_KC: Record<string, number> = {
  lawn: 0.8,
  vegetables: 1.0,
  flowers: 0.9,
  shrubs: 0.5,
  trees: 0.7,
  xeriscape: 0.3,
};

// Soil-type presets → drainage rate above field capacity (mm/h). Saves the
// "adjust 5 mm/h by trial and error" guesswork; the stored value is still the
// plain ``drainage_rate`` number, so "custom" leaves whatever was hand-set.
// Coarse, well-drained soils shed surplus fast; clay holds it.
export const SOIL_TYPE_DRAINAGE: Record<string, number> = {
  sand: 35,
  loam: 20,
  silt: 10,
  clay: 5,
};

export const CONF_ZONE_SEQUENCING = "zone_sequencing";
export const CONF_ZONE_SEQUENCING_SEQUENTIAL = "sequential";
export const CONF_ZONE_SEQUENCING_PARALLEL = "parallel";
export const CONF_ZONE_SEQUENCING_ROTATING = "rotating";
export const CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION =
  "zone_sequencing_max_consecutive_duration";
export const CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME =
  "zone_sequencing_min_absorption_time";

// Master switch / pump control (instance-level, all optional)
export const CONF_MASTER_ENTITY = "master_entity";
export const CONF_MASTER_SETTLE_SECONDS = "master_settle_seconds";
export const CONF_MASTER_KICK_ENABLED = "master_kick_enabled";
export const CONF_MASTER_KICK_PAUSE_SECONDS = "master_kick_pause_seconds";
export const CONF_MASTER_OFF_AFTER = "master_off_after";

export const SCHEDULE_TYPE_SUNRISE = "sunrise";
export const SCHEDULE_TYPE_SUNSET = "sunset";
export const SCHEDULE_TYPE_SOLAR_AZIMUTH = "solar_azimuth";

// ---------------------------------------------------------------------------
// Gardena water distributor (Plan F). Field keys mirror the backend
// DistributorEntry (store.py) / POST schema (websockets.py) exactly.
// ---------------------------------------------------------------------------
export const DISTRIBUTOR_NAME = "name";
export const DISTRIBUTOR_WATERING_MODE = "watering_mode";
export const DISTRIBUTOR_INLET_ENTITY = "inlet_entity";
export const DISTRIBUTOR_WATCH_MODE = "watch_mode";
export const DISTRIBUTOR_RUN_SERVICE = "run_service";
export const DISTRIBUTOR_STOP_SERVICE = "stop_service";
export const DISTRIBUTOR_DURATION_FIELD = "duration_field";
export const DISTRIBUTOR_DURATION_UNIT = "duration_unit";
export const DISTRIBUTOR_CONFIRM_ENTITY = "confirm_entity";
export const DISTRIBUTOR_FLOW_SENSOR = "flow_sensor";
export const DISTRIBUTOR_PAUSE_SECONDS = "pause_seconds";
export const DISTRIBUTOR_SKIP_PULSE_SECONDS = "skip_pulse_seconds";
export const DISTRIBUTOR_CURRENT_OUTLET = "current_outlet";
export const DISTRIBUTOR_POSITION_STATE = "position_state";
export const DISTRIBUTOR_NOTIFY_TARGET = "notify_target";
export const DISTRIBUTOR_USE_MASTER = "use_master";
export const DISTRIBUTOR_COMMISSIONING_CONFIRMED = "commissioning_confirmed";

// Inlet-watch reaction to a foreign inlet pulse (E4). Order = <select> order.
// Values match the backend DISTRIBUTOR_WATCH_MODE_* constants (const.py).
export const DISTRIBUTOR_WATCH_MODES = ["count", "warn", "ignore"] as const;

// watering_mode / position_state enum values (match const.py)
export const WATERING_MODE_CLASSIC = "classic";
export const WATERING_MODE_SERVICE = "service";
export const POSITION_STATE_SYNCED = "synced";
export const POSITION_STATE_UNCERTAIN = "uncertain";

// Timing floors / defaults (backend re-floors; the UI warns below these).
export const DISTRIBUTOR_MIN_PAUSE_SECONDS = 10;
export const DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS = 10;
export const DISTRIBUTOR_DEFAULT_PAUSE_SECONDS = 300;
export const DISTRIBUTOR_DEFAULT_SKIP_PULSE_SECONDS = 30;

// Outlet-count bounds for the physical device (spec §4.3).
export const DISTRIBUTOR_MIN_OUTLETS = 2;
export const DISTRIBUTOR_MAX_OUTLETS = 6;

// Operation services (Plan D) — call via hass.callService(DOMAIN, name, data).
export const SERVICE_DISTRIBUTOR_SET_OUTLET = "distributor_set_outlet";
export const SERVICE_DISTRIBUTOR_RESYNC_HOME = "distributor_resync_home";
export const SERVICE_DISTRIBUTOR_TEST_RUN = "distributor_test_run";
export const SERVICE_DISTRIBUTOR_RUN_NOW = "distributor_run_now";

// Zone → distributor membership (zone POST schema, websockets.py).
export const ZONE_DISTRIBUTOR_ID = "distributor_id";
export const ZONE_OUTLET_NUMBER = "outlet_number";
