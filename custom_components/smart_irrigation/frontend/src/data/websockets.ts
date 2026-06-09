import { HomeAssistant } from "../types";
import {
  SmartIrrigationConfig,
  SmartIrrigationZone,
  SmartIrrigationModule,
  SmartIrrigationMapping,
  IrrigationOutlook,
} from "../types";
import { DOMAIN } from "../const";

export const fetchConfig = (
  hass: HomeAssistant,
): Promise<SmartIrrigationConfig> =>
  hass.callWS({
    type: DOMAIN + "/config",
  });

export const saveConfig = (
  hass: HomeAssistant,
  config: Partial<SmartIrrigationConfig>,
): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/config", config);
};

/*export const fetchZones = (
  hass: HomeAssistant
): Promise<Dictionary<SmartIrrigationZone>> =>*/
export const fetchZones = (
  hass: HomeAssistant,
): Promise<SmartIrrigationZone[]> =>
  hass.callWS({
    type: DOMAIN + "/zones",
  });

export const saveZone = (
  hass: HomeAssistant,
  config: Partial<SmartIrrigationZone>,
): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", config);
};

export const calculateZone = (
  hass: HomeAssistant,
  zone_id: string,
): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", {
    id: zone_id,
    calculate: true,
    override_cache: true,
  });
};

export const updateZone = (
  hass: HomeAssistant,
  zone_id: string,
): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", {
    id: zone_id,
    update: true,
  });
};
export const calculateAllZones = (hass: HomeAssistant): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", {
    calculate_all: true,
  });
};

export const updateAllZones = (hass: HomeAssistant): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", {
    update_all: true,
  });
};

export const resetAllBuckets = (hass: HomeAssistant): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", {
    reset_all_buckets: true,
  });
};

export const clearAllWeatherdata = (hass: HomeAssistant): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", {
    clear_all_weatherdata: true,
  });
};

export const deleteZone = (
  hass: HomeAssistant,
  zone_id: string,
): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/zones", {
    id: zone_id,
    remove: true,
  });
};

export const fetchModules = (
  hass: HomeAssistant,
): Promise<SmartIrrigationModule[]> =>
  hass.callWS({
    type: DOMAIN + "/modules",
  });

export const fetchAllModules = (
  hass: HomeAssistant,
): Promise<SmartIrrigationModule[]> =>
  hass.callWS({
    type: DOMAIN + "/allmodules",
  });

/** POST response for create/update endpoints. `id` is present on create. */
export interface SaveResult {
  success: boolean;
  id?: number;
}

export const saveModule = (
  hass: HomeAssistant,
  config: Partial<SmartIrrigationModule>,
): Promise<SaveResult> => {
  return hass.callApi("POST", DOMAIN + "/modules", config);
};

export const deleteModule = (
  hass: HomeAssistant,
  module_id: string,
): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/modules", {
    id: module_id,
    remove: true,
  });
};

export const fetchMappings = (
  hass: HomeAssistant,
): Promise<SmartIrrigationMapping[]> =>
  hass.callWS({
    type: DOMAIN + "/mappings",
  });
export const saveMapping = (
  hass: HomeAssistant,
  config: Partial<SmartIrrigationMapping>,
): Promise<SaveResult> => {
  return hass.callApi("POST", DOMAIN + "/mappings", config);
};

export const deleteMapping = (
  hass: HomeAssistant,
  mapping_id: string,
): Promise<boolean> => {
  return hass.callApi("POST", DOMAIN + "/mappings", {
    id: mapping_id,
    remove: true,
  });
};

// Backend API for weather records for a mapping
export const fetchMappingWeatherRecords = (
  hass: HomeAssistant,
  mapping_id: string,
  limit: number = 10,
): Promise<any[]> =>
  hass.callWS({
    type: DOMAIN + "/weather_records",
    mapping_id: mapping_id,
    limit: limit,
  });

// Weather service daily forecast (forward-looking; one entry per upcoming day)
export interface ForecastDay {
  date: string;
  temp_min: number | null;
  temp_max: number | null;
  precipitation: number | null;
  windspeed: number | null;
}

export interface WeatherForecast {
  available: boolean;
  days: ForecastDay[];
}

export const fetchWeatherForecast = (
  hass: HomeAssistant,
): Promise<WeatherForecast> =>
  hass.callWS({ type: DOMAIN + "/weather_forecast" });

// Backend API for watering calendar for a zone
export const fetchWateringCalendar = (
  hass: HomeAssistant,
  zone_id?: string,
): Promise<any[]> =>
  hass.callWS({
    type: DOMAIN + "/watering_calendar",
    zone_id: zone_id,
  });

// Schedules
export const fetchSchedules = (hass: HomeAssistant): Promise<any[]> =>
  hass.callWS({ type: DOMAIN + "/schedules" });

export const saveSchedule = (
  hass: HomeAssistant,
  schedule: Record<string, any>,
): Promise<any> => hass.callWS({ type: DOMAIN + "/schedule_save", schedule });

export const deleteSchedule = (
  hass: HomeAssistant,
  schedule_id: string,
): Promise<any> =>
  hass.callWS({ type: DOMAIN + "/schedule_delete", schedule_id });

// Dashboard outlook: next scheduled runs + live skip-condition preview
export const fetchIrrigationOutlook = (
  hass: HomeAssistant,
): Promise<IrrigationOutlook> =>
  hass.callWS({ type: DOMAIN + "/irrigation_outlook" });

// Trigger immediate irrigation (bypasses all skip conditions)
export const irrigateNow = (
  hass: HomeAssistant,
  zone_id?: string,
): Promise<any> =>
  hass.callWS({
    type: DOMAIN + "/irrigate_now",
    ...(zone_id !== undefined ? { zone_id } : {}),
  });

export interface WeatherConfig {
  use_weather_service: boolean;
  weather_service: string | null;
  has_owm_api_key: boolean;
  has_pw_api_key: boolean;
  available_services: string[];
  no_api_key_services: string[];
}

export const fetchWeatherConfig = (
  hass: HomeAssistant,
): Promise<WeatherConfig> => hass.callWS({ type: DOMAIN + "/weather_config" });

export interface WeatherConfigTestResult {
  success: boolean;
  error?: "invalid_auth" | "cannot_connect" | "no_service" | "unknown";
}

export const testWeatherConfig = (
  hass: HomeAssistant,
  weather_service?: string | null,
  api_key?: string | null,
): Promise<WeatherConfigTestResult> =>
  hass.callWS({
    type: DOMAIN + "/weather_config_test",
    weather_service: weather_service ?? null,
    api_key: api_key ?? null,
  });

export const saveWeatherConfig = (
  hass: HomeAssistant,
  use_weather_service: boolean,
  weather_service?: string | null,
  api_key?: string | null,
): Promise<any> =>
  hass.callWS({
    type: DOMAIN + "/weather_config_save",
    use_weather_service,
    weather_service: weather_service ?? null,
    api_key: api_key ?? null,
  });

export interface CoordinatesConfig {
  manual_coordinates_enabled: boolean;
  manual_latitude: number | null;
  manual_longitude: number | null;
  manual_elevation: number | null;
  ha_latitude: number | null;
  ha_longitude: number | null;
  ha_elevation: number | null;
}

export const fetchCoordinates = (
  hass: HomeAssistant,
): Promise<CoordinatesConfig> => hass.callWS({ type: DOMAIN + "/coordinates" });

export const saveCoordinates = (
  hass: HomeAssistant,
  manual_coordinates_enabled: boolean,
  manual_latitude?: number | null,
  manual_longitude?: number | null,
  manual_elevation?: number | null,
): Promise<any> =>
  hass.callWS({
    type: DOMAIN + "/coordinates_save",
    manual_coordinates_enabled,
    manual_latitude: manual_latitude ?? null,
    manual_longitude: manual_longitude ?? null,
    manual_elevation: manual_elevation ?? null,
  });
