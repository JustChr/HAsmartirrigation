import type {
  Connection,
  HassConfig,
  HassEntities,
  MessageBase,
} from "home-assistant-js-websocket";

export interface Dictionary<TValue> {
  [id: string]: TValue;
}

/**
 * Minimal Home Assistant frontend object — the subset of properties this
 * integration actually reads. Replaces the `HomeAssistant` type formerly
 * imported from `custom-card-helpers` (now removed). If a future view needs
 * another `hass.*` field, add it here.
 */
export interface HomeAssistant {
  language: string;
  states: HassEntities;
  config: HassConfig;
  connection: Connection;
  panels: Record<string, { config: Record<string, any> | null }>;
  localize: (key: string, ...args: any[]) => string;
  callApi: <T>(
    method: string,
    path: string,
    parameters?: Record<string, any>,
    headers?: Record<string, string>,
  ) => Promise<T>;
  callWS: <T>(msg: MessageBase | Record<string, any>) => Promise<T>;
}

/*export interface AlarmEntity extends HassEntity {
  attributes: HassEntityAttributeBase & {
    code_format: 'number' | 'text';
    code_arm_required: boolean;
    code_disarm_required: boolean;
    disarm_after_trigger: boolean;
    supported_features: number;
    sensors: Dictionary<number>;
    delays: Dictionary<number>;
    users: Dictionary<number>;
    config: number;
    push_target?: string;
    siren_entity?: string;
  };
}*/

export class SmartIrrigationConfig {
  calctime: string;
  use_weather_service: boolean;
  units: string;
  autocalcenabled: boolean;
  autoupdateenabled: boolean;
  autoupdateschedule: string;
  autoupdatedelay: number;
  autoupdateinterval: number;
  cleardatatime: string;
  autoclearenabled: boolean;
  continuousupdates: boolean;
  sensor_debounce: number;
  skip_irrigation_on_precipitation: boolean;
  precipitation_threshold_mm: number;
  precipitation_forecast_days: number;
  manual_coordinates_enabled: boolean;
  manual_latitude?: number;
  manual_longitude?: number;
  manual_elevation?: number;
  days_between_irrigation: number;
  zone_sequencing: string;
  zone_sequencing_max_consecutive_duration: number;
  zone_sequencing_min_absorption_time: number;
  skip_on_temp_enabled: boolean;
  temp_threshold: number;
  skip_on_wind_enabled: boolean;
  wind_threshold: number;
  skip_on_freeze_enabled: boolean;
  freeze_threshold: number;
  rain_sensor?: string | null;
  forecast_weighting_enabled: boolean;
  observed_watering_enabled: boolean;
  live_estimate_enabled: boolean;

  constructor() {
    this.calctime = "23:00";
    this.use_weather_service = false;
    this.units = "";
    this.autocalcenabled = true;
    this.autoupdateenabled = true;
    this.autoupdateschedule = "";
    this.autoupdatedelay = 0;
    this.autoupdateinterval = 0;
    this.autoclearenabled = true;
    this.cleardatatime = "23:59";
    // continuousupdates are disabled by default
    this.continuousupdates = false;
    this.sensor_debounce = 100;
    this.skip_irrigation_on_precipitation = false;
    this.precipitation_threshold_mm = 2.0;
    this.precipitation_forecast_days = 1;
    this.manual_coordinates_enabled = false;
    this.manual_latitude = undefined;
    this.manual_longitude = undefined;
    this.manual_elevation = undefined;
    this.days_between_irrigation = 0;
    this.zone_sequencing = "parallel";
    this.zone_sequencing_max_consecutive_duration = 5;
    this.zone_sequencing_min_absorption_time = 0;
    this.skip_on_temp_enabled = false;
    this.temp_threshold = 5.0;
    this.skip_on_wind_enabled = false;
    this.wind_threshold = 6.9;
    this.skip_on_freeze_enabled = false;
    this.freeze_threshold = 1.0;
    this.rain_sensor = null;
    this.forecast_weighting_enabled = false;
    this.observed_watering_enabled = false;
    this.live_estimate_enabled = false;
  }
}

/** One skip-condition guard, evaluated either live (preview) or at run time. */
export interface SkipCheck {
  id:
    | "precipitation"
    | "days_between"
    | "temperature"
    | "wind"
    | "rain_sensor"
    | string;
  enabled: boolean;
  would_skip: boolean;
  available: boolean;
  observed: number | string | null;
  threshold: number | null;
  entity_id?: string | null;
}

export interface SkipPreview {
  would_skip: boolean;
  checks: SkipCheck[];
}

/** Next computed fire of a recurring schedule. */
export interface UpcomingRun {
  schedule_id: string;
  name: string;
  action: "irrigate" | "calculate" | "update" | string;
  zones: "all" | number[];
  type: string;
  time_anchor: "start" | "finish" | string;
  next_run_utc: string | null;
  target_utc: string | null;
  duration_seconds: number;
  interval_hours?: number;
}

/** Read-only intra-day "live status" estimate for one zone. */
export interface ZoneEstimate {
  available: boolean;
  method: "hourly" | "proxy" | string | null;
  et_since: number | null;
  precip_since: number | null;
  live_deficit: number | null;
  as_of: string | null;
}

/** A zone whose most recent irrigation run failed (e.g. the valve never opened). */
export interface ZoneFault {
  reason: string;
  timestamp: string;
}

/** One entry of a zone's bounded run history (newest first). */
export interface RunLogEntry {
  ts: string;
  trigger: string;
  planned_s: number | null;
  actual_s: number | null;
  volume_l: number;
  result: "completed" | "partial" | "failed" | "skipped" | string;
  detail: string | null;
}

/** A zone whose valve is currently being held open by the runner. */
export interface ActiveRun {
  started_at: string;
  // ISO datetime the run is expected to finish; null for flow-metered
  // (volume-bounded) runs whose finish time is unknown.
  ends_at: string | null;
}

export interface IrrigationOutlook {
  weather_service_enabled: boolean;
  skip_preview: SkipPreview;
  last_skip_evaluation: (SkipPreview & { timestamp: string }) | null;
  upcoming_runs: UpcomingRun[];
  zone_estimates?: Record<string, ZoneEstimate>;
  zone_faults?: Record<string, ZoneFault>;
  // In-progress runs keyed by zone id (string). Surfaces the Stop control +
  // a live countdown while a zone is watering.
  active_runs?: Record<string, ActiveRun>;
  // Rain delay / vacation hold (WS-5): ISO datetime automatic irrigation
  // resumes, or null/undefined when no hold is active.
  rain_delay_until?: string | null;
}

export interface IrrigationStartTrigger {
  type: string;
  name: string;
  enabled: boolean;
  offset_minutes: number;
  azimuth_angle?: number;
  account_for_duration: boolean;
}

export enum TriggerType {
  Sunrise = "sunrise",
  Sunset = "sunset",
  SolarAzimuth = "solar_azimuth",
}

export enum SmartIrrigationZoneState {
  Disabled = "disabled",
  Manual = "manual",
  Automatic = "automatic",
}

//export type SmartIrrigationZone = {
export class SmartIrrigationZone {
  id?: number;
  name: string;
  size: number;
  throughput: number;
  state: SmartIrrigationZoneState;
  duration: number;
  module?: number;
  bucket: number;
  delta: number;
  explanation: string;
  multiplier: number;
  mapping?: number;
  lead_time: number;
  maximum_duration?: number;
  maximum_bucket?: number;
  last_calculated?: Date;
  last_updated?: Date;
  number_of_data_points?: number;
  drainage_rate?: number;
  current_drainage?: number;
  kc?: number;
  plant_type?: string;
  linked_entity?: string;
  bucket_threshold?: number;
  flow_sensor?: string | null;
  water_used_total?: number;
  run_log?: RunLogEntry[];

  constructor(
    i: number,
    n: string,
    s: number,
    t: number,
    st: SmartIrrigationZoneState,
    d: number,
  ) {
    this.id = i;
    this.name = n;
    this.size = s;
    this.throughput = t;
    this.state = st;
    this.duration = d;
    this.module = undefined;
    this.bucket = 0;
    this.delta = 0;
    this.explanation = "";
    this.multiplier = 1.0;
    this.mapping = undefined;
    this.lead_time = 0;
    this.maximum_duration = 3600; //default maximum duration to one hour = 3600 seconds
    this.maximum_bucket = 50; //default maximum bucket size to 50 mm
    this.last_calculated = undefined;
    this.drainage_rate = 20; // default mm/hour at saturation (medium soil)
    this.current_drainage = 0;
    this.kc = 1.0; // crop coefficient: 1.0 = reference grass ET (no scaling)
    this.plant_type = "custom";
    this.bucket_threshold = -10; // require a 10 mm deficit before irrigating
  }
}

export class SmartIrrigationModule {
  id?: number;
  name: string;
  description: string;
  //duration: number;
  config: object;
  schema: object;
  constructor(i: number, n: string, d: string, c: object, s: object) {
    this.id = i;
    this.name = n;
    this.description = d;
    this.config = c;
    this.schema = s;
    //this.duration = dr;
    //this.module = m;
  }
}

export class SmartIrrigationMapping {
  id?: number;
  name: string;
  mappings: object;
  data?: any[];

  constructor(i: number, n: string, m: object) {
    this.id = i;
    this.name = n;
    this.mappings = m;
    this.data = undefined;
  }
}
