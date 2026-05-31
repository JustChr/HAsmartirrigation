import { TemplateResult, LitElement, html, CSSResultGroup, css } from "lit";
import { unsafeHTML } from "lit/directives/unsafe-html.js";
import { live } from "lit/directives/live.js";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";
import { loadHaForm } from "../../load-ha-elements";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { mdiDelete, mdiCalculator, mdiUpdate, mdiPlus } from "@mdi/js";
import {
  deleteZone,
  fetchConfig,
  fetchZones,
  saveZone,
  calculateZone,
  updateZone,
  fetchModules,
  fetchMappings,
  calculateAllZones,
  updateAllZones,
  resetAllBuckets,
  clearAllWeatherdata,
  fetchWateringCalendar,
  fetchMappingWeatherRecords,
  irrigateNow,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";

import {
  SmartIrrigationConfig,
  SmartIrrigationZone,
  SmartIrrigationZoneState,
  SmartIrrigationModule,
  SmartIrrigationMapping,
  WeatherRecord,
} from "../../types";
import { output_unit } from "../../helpers";
import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import {
  CONF_METRIC,
  DOMAIN,
  UNIT_LPM,
  UNIT_GPM,
  UNIT_M2,
  UNIT_SQ_FT,
  UNIT_SECONDS,
  ZONE_BUCKET,
  ZONE_DRAINAGE_RATE,
  ZONE_DURATION,
  ZONE_LEAD_TIME,
  ZONE_MAPPING,
  ZONE_MAXIMUM_BUCKET,
  ZONE_MAXIMUM_DURATION,
  ZONE_MODULE,
  ZONE_MULTIPLIER,
  ZONE_NAME,
  ZONE_SIZE,
  ZONE_STATE,
  ZONE_THROUGHPUT,
  ZONE_LINKED_ENTITY,
  ZONE_BUCKET_THRESHOLD,
  ZONE_FLOW_SENSOR,
} from "../../const";
import moment from "moment";
import "../../components/si-field";

@customElement("smart-irrigation-view-zones")
class SmartIrrigationViewZones extends SubscribeMixin(LitElement) {
  hass?: HomeAssistant;
  @property() config?: SmartIrrigationConfig;

  @property({ type: Array })
  private zones: SmartIrrigationZone[] = [];
  @property({ type: Array })
  private modules: SmartIrrigationModule[] = [];
  @property({ type: Array })
  private mappings: SmartIrrigationMapping[] = [];

  @property({ type: Map })
  private wateringCalendars = new Map<number, any>();

  @property({ type: Map })
  private weatherRecords = new Map<number, WeatherRecord[]>();

  @property({ type: Boolean })
  private isLoading = true;

  @property({ type: Boolean })
  private isSaving = false;

  @property({ type: Boolean })
  private _showAddZone = false;

  @state() private _operationError: string | null = null;

  @property()
  private _confirmDeleteZoneId: number | null = null;

  @property()
  private _newZoneName = "";

  @property()
  private _newZoneSize = "";

  @property()
  private _newZoneThroughput = "";

  private _extractErrorMessage(err: unknown): string {
    if (!err) return "Unknown error";
    if (typeof err === "string") return err;
    const e = err as any;
    return e?.body?.message || e?.message || e?.error || JSON.stringify(err);
  }

  private _updateScheduled = false;
  private _scheduleUpdate() {
    if (this._updateScheduled) return;
    this._updateScheduled = true;
    requestAnimationFrame(() => {
      this._updateScheduled = false;
      this.requestUpdate();
    });
  }

  private globalDebounceTimer: number | null = null;

  firstUpdated() {
    loadHaForm()
      .then(() => this._scheduleUpdate())
      .catch((error) => {
        console.error("Failed to load HA form:", error);
        this._scheduleUpdate();
      });
  }

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._fetchData().catch((error) => {
      console.error("Failed to fetch initial data:", error);
    });

    return [
      this.hass!.connection.subscribeMessage(
        () => {
          this._fetchData().catch((error) => {
            console.error("Failed to fetch data on config update:", error);
          });
        },
        { type: DOMAIN + "_config_updated" },
      ),
    ];
  }

  private async _fetchData(): Promise<void> {
    if (!this.hass) return;

    try {
      this.isLoading = true;

      const [config, zones, modules, mappings] = await Promise.all([
        fetchConfig(this.hass),
        fetchZones(this.hass),
        fetchModules(this.hass),
        fetchMappings(this.hass),
      ]);

      this.config = config;
      this.zones = zones;
      this.modules = modules;
      this.mappings = mappings;

      this._fetchWateringCalendars();
      this._fetchWeatherRecords();
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      this.isLoading = false;
      this._scheduleUpdate();
    }
  }

  private handleCalculateAllZones(): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    calculateAllZones(this.hass)
      .catch((error) => console.error("Failed to calculate all zones:", error))
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after calc-all:", e),
        );
      });
  }

  private handleUpdateAllZones(): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    updateAllZones(this.hass)
      .catch((error) => console.error("Failed to update all zones:", error))
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after update-all:", e),
        );
      });
  }

  private handleResetAllBuckets(): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    resetAllBuckets(this.hass)
      .catch((error) => console.error("Failed to reset all buckets:", error))
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after reset:", e),
        );
      });
  }

  private handleClearAllWeatherdata(): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    clearAllWeatherdata(this.hass)
      .catch((error) =>
        console.error("Failed to clear all weather data:", error),
      )
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after clear-weather:", e),
        );
      });
  }

  private handleAddZone(): void {
    if (!this._newZoneName.trim()) return;

    const newZone: SmartIrrigationZone = {
      name: this._newZoneName.trim(),
      size: Math.round((parseFloat(this._newZoneSize) || 0) * 100) / 100,
      throughput:
        Math.round((parseFloat(this._newZoneThroughput) || 0) * 100) / 100,
      state: SmartIrrigationZoneState.Automatic,
      duration: 0,
      bucket: 0,
      module: undefined,
      delta: 0,
      explanation: "",
      multiplier: 1,
      mapping: undefined,
      lead_time: 0,
      maximum_duration: undefined,
      maximum_bucket: undefined,
      drainage_rate: undefined,
      current_drainage: 0,
    };

    this.zones = [...this.zones, newZone];
    this.isSaving = true;
    this._showAddZone = false;

    this.saveToHA(newZone)
      .then(() => {
        this._newZoneName = "";
        this._newZoneSize = "";
        this._newZoneThroughput = "";
        return this._fetchData();
      })
      .catch((error) => {
        console.error("Failed to add zone:", error);
        this.zones = this.zones.slice(0, -1);
      })
      .finally(() => {
        this.isSaving = false;
        this._scheduleUpdate();
      });
  }

  private handleEditZone(
    index: number,
    updatedZone: SmartIrrigationZone,
  ): void {
    if (!this.hass) return;

    // Replace the whole array so Lit's reactive system detects the change.
    this.zones = this.zones.map((z, i) => (i === index ? updatedZone : z));

    if (this.globalDebounceTimer) clearTimeout(this.globalDebounceTimer);

    this.globalDebounceTimer = window.setTimeout(() => {
      this.isSaving = true;
      this.saveToHA(updatedZone)
        .catch((error) => console.error("Failed to save zone:", error))
        .finally(() => {
          this.isSaving = false;
          this._scheduleUpdate();
        });
      this.globalDebounceTimer = null;
    }, 500);

    this._scheduleUpdate();
  }

  private handleRemoveZone(zoneId: number): void {
    this._confirmDeleteZoneId = zoneId;
  }

  private _confirmDelete(): void {
    const zoneId = this._confirmDeleteZoneId;
    if (zoneId === null || !this.hass) return;

    const index = this.zones.findIndex((z) => z.id === zoneId);
    if (index === -1) return;

    const originalZones = [...this.zones];
    this.zones = this.zones.filter((z) => z.id !== zoneId);
    this._confirmDeleteZoneId = null;
    this.isSaving = true;

    deleteZone(this.hass, zoneId.toString())
      .catch((error) => {
        console.error("Failed to delete zone:", error);
        this.zones = originalZones;
        this._fetchData().catch((e) =>
          console.error("Failed to refresh data after delete error:", e),
        );
      })
      .finally(() => {
        this.isSaving = false;
        this._scheduleUpdate();
      });
  }

  private handleCalculateZone(index: number): void {
    const zone = this.zones[index];
    if (!zone || zone.id == undefined || !this.hass) return;
    this._operationError = null;
    this.isSaving = true;
    this._scheduleUpdate();
    calculateZone(this.hass, zone.id.toString())
      .catch((err) => {
        const msg = this._extractErrorMessage(err);
        console.error("calculateZone failed:", err);
        this._operationError = msg;
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after calc:", e),
        );
      });
  }

  private handleUpdateZone(index: number): void {
    const zone = this.zones[index];
    if (!zone || zone.id == undefined || !this.hass) return;
    this._operationError = null;
    this.isSaving = true;
    this._scheduleUpdate();
    updateZone(this.hass, zone.id.toString())
      .catch((err) => {
        const msg = this._extractErrorMessage(err);
        console.error("updateZone failed:", err);
        this._operationError = msg;
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after update:", e),
        );
      });
  }

  private async _fetchWeatherRecords(): Promise<void> {
    if (!this.hass) return;
    for (const zone of this.zones) {
      if (zone.id !== undefined && zone.mapping !== undefined) {
        try {
          const records = await fetchMappingWeatherRecords(
            this.hass,
            zone.mapping.toString(),
            10,
          );
          this.weatherRecords.set(zone.id, records);
        } catch (error) {
          console.error(
            `Failed to fetch weather records for zone ${zone.id}:`,
            error,
          );
        }
      }
    }
    this._scheduleUpdate();
  }

  private async _fetchWateringCalendars(): Promise<void> {
    if (!this.hass) return;
    for (const zone of this.zones) {
      if (zone.id !== undefined) {
        try {
          const calendar = await fetchWateringCalendar(
            this.hass,
            zone.id.toString(),
          );
          this.wateringCalendars.set(zone.id, calendar);
        } catch (error) {
          console.error(
            `Failed to fetch watering calendar for zone ${zone.id}:`,
            error,
          );
        }
      }
    }
    this._scheduleUpdate();
  }

  private renderWeatherRecords(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass || typeof zone.id !== "number") return html``;

    const records = this.weatherRecords.get(zone.id) || [];

    return html`
      <div class="card-content">
        ${records.length === 0
          ? html`
              <div class="weather-note">
                ${localize(
                  "panels.mappings.weather-records.no-data",
                  this.hass.language,
                )}
              </div>
            `
          : html`
              <div class="weather-table">
                <div class="weather-header">
                  <span
                    >${localize(
                      "panels.mappings.weather-records.timestamp",
                      this.hass.language,
                    )}</span
                  >
                  <span
                    >${localize(
                      "panels.mappings.weather-records.temperature",
                      this.hass.language,
                    )}</span
                  >
                  <span
                    >${localize(
                      "panels.mappings.weather-records.humidity",
                      this.hass.language,
                    )}</span
                  >
                  <span
                    >${localize(
                      "panels.mappings.weather-records.precipitation",
                      this.hass.language,
                    )}</span
                  >
                  <span
                    >${localize(
                      "panels.mappings.weather-records.retrieval-time",
                      this.hass.language,
                    )}</span
                  >
                </div>
                ${records.slice(0, 10).map(
                  (record) => html`
                    <div class="weather-row">
                      <span
                        >${moment(record.timestamp).format("MM-DD HH:mm")}</span
                      >
                      <span
                        >${record.temperature
                          ? record.temperature.toFixed(1) + "°C"
                          : "-"}</span
                      >
                      <span
                        >${record.humidity
                          ? record.humidity.toFixed(1) + "%"
                          : "-"}</span
                      >
                      <span
                        >${record.precipitation
                          ? record.precipitation.toFixed(1) + "mm"
                          : "-"}</span
                      >
                      <span
                        >${record.retrieval_time
                          ? moment(record.retrieval_time).format("MM-DD HH:mm")
                          : "-"}</span
                      >
                    </div>
                  `,
                )}
              </div>
            `}
      </div>
    `;
  }

  private renderWateringCalendar(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass || typeof zone.id !== "number") return html``;
    const calendarData = this.wateringCalendars.get(zone.id);
    const zoneCalendar =
      calendarData && zone.id in calendarData ? calendarData[zone.id] : null;
    const monthlyEstimates = zoneCalendar?.monthly_estimates || [];

    return html`
      <div class="card-content">
        ${monthlyEstimates.length === 0
          ? html`
              <div class="calendar-note">
                ${zoneCalendar?.error
                  ? `Error generating calendar: ${zoneCalendar.error}`
                  : "No watering calendar data available for this zone"}
              </div>
            `
          : html`
              <div class="calendar-table">
                <div class="calendar-header">
                  <span>Month</span>
                  <span>ET (mm)</span>
                  <span>Precipitation (mm)</span>
                  <span>Watering (L)</span>
                  <span>Avg Temp (°C)</span>
                </div>
                ${monthlyEstimates.map(
                  (estimate) => html`
                    <div class="calendar-row">
                      <span
                        >${estimate.month_name ||
                        `Month ${estimate.month}` ||
                        "-"}</span
                      >
                      <span
                        >${estimate.estimated_et_mm
                          ? estimate.estimated_et_mm.toFixed(1)
                          : "-"}</span
                      >
                      <span
                        >${estimate.average_precipitation_mm
                          ? estimate.average_precipitation_mm.toFixed(1)
                          : "-"}</span
                      >
                      <span
                        >${estimate.estimated_watering_volume_liters
                          ? estimate.estimated_watering_volume_liters.toFixed(0)
                          : "-"}</span
                      >
                      <span
                        >${estimate.average_temperature_c
                          ? estimate.average_temperature_c.toFixed(1)
                          : "-"}</span
                      >
                    </div>
                  `,
                )}
              </div>
              ${zoneCalendar?.calculation_method
                ? html`
                    <div class="calendar-info">
                      Method: ${zoneCalendar.calculation_method}
                    </div>
                  `
                : ""}
            `}
      </div>
    `;
  }

  private async saveToHA(zone: SmartIrrigationZone): Promise<void> {
    if (!this.hass) throw new Error("Home Assistant connection not available");
    await saveZone(this.hass, zone);
  }

  private _renderModuleOptions(selected?: number | string): TemplateResult {
    if (!this.hass) return html``;
    const sel = selected != null ? String(selected) : "";
    return html`
      <option value="" ?selected="${sel === ""}">
        ---${localize("common.labels.select", this.hass.language)}---
      </option>
      ${this.modules.map(
        (m) => html`
          <option value="${m.id}" ?selected="${sel === String(m.id)}">
            ${m.id}: ${m.name}
          </option>
        `,
      )}
    `;
  }

  private _renderMappingOptions(selected?: number | string): TemplateResult {
    if (!this.hass) return html``;
    const sel = selected != null ? String(selected) : "";
    return html`
      <option value="" ?selected="${sel === ""}">
        ---${localize("common.labels.select", this.hass.language)}---
      </option>
      ${this.mappings.map(
        (m) => html`
          <option value="${m.id}" ?selected="${sel === String(m.id)}">
            ${m.id}: ${m.name}
          </option>
        `,
      )}
    `;
  }

  private renderZone(zone: SmartIrrigationZone, index: number): TemplateResult {
    if (!this.hass) return html``;

    const bucket = Number(zone.bucket ?? 0);
    const bucketColor =
      bucket < 0 ? "var(--warning-color)" : "var(--success-color)";
    const stateClass =
      zone.state === SmartIrrigationZoneState.Automatic
        ? "state-automatic"
        : zone.state === SmartIrrigationZoneState.Manual
          ? "state-manual"
          : "state-disabled";

    return html`
      <ha-card>
        <div class="card-header">
          <div class="name">${zone.name}</div>
          <span class="zone-state-badge ${stateClass}">
            ${localize(
              `panels.zones.labels.states.${zone.state}`,
              this.hass.language,
            )}
          </span>
        </div>

        <!-- STATUS -->
        <div class="card-content">
          <div class="zone-status-grid">
            <div class="status-item">
              <span class="status-label"
                >${localize(
                  "panels.zones.labels.bucket",
                  this.hass.language,
                )}</span
              >
              <span class="status-value" style="color: ${bucketColor}">
                ${bucket.toFixed(2)} ${output_unit(this.config, ZONE_BUCKET)}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label"
                >${localize(
                  "panels.zones.labels.duration",
                  this.hass.language,
                )}</span
              >
              <span class="status-value">
                ${(zone.duration ?? 0) > 0
                  ? `${zone.duration} ${UNIT_SECONDS}`
                  : "–"}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label"
                >${localize(
                  "panels.zones.labels.last_calculated",
                  this.hass.language,
                )}</span
              >
              <span class="status-value">
                ${zone.last_calculated
                  ? moment(zone.last_calculated).format("YYYY-MM-DD HH:mm")
                  : "–"}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label"
                >${localize(
                  "panels.zones.labels.data-number-of-data-points",
                  this.hass.language,
                )}</span
              >
              <span class="status-value"
                >${zone.number_of_data_points ?? 0}</span
              >
            </div>
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${zone.state === SmartIrrigationZoneState.Automatic
            ? html`
                <button
                  class="action-btn"
                  @click="${() => this.handleCalculateZone(index)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon slot="icon" icon="mdi:calculator"></ha-icon>
                  ${localize(
                    "panels.zones.actions.calculate",
                    this.hass.language,
                  )}
                </button>
                <button
                  class="action-btn"
                  @click="${() => this.handleUpdateZone(index)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon slot="icon" icon="mdi:update"></ha-icon>
                  ${localize("panels.zones.actions.update", this.hass.language)}
                </button>
              `
            : ""}
          ${zone.linked_entity && (zone.duration ?? 0) > 0
            ? html`
                <button
                  class="action-btn"
                  raised
                  @click="${() => {
                    if (!this.hass) return;
                    irrigateNow(
                      this.hass,
                      zone.id !== undefined ? zone.id.toString() : undefined,
                    ).catch((e) => console.error("irrigate_now failed", e));
                  }}"
                  ?disabled="${this.isSaving}"
                >
                  ${localize(
                    "panels.zones.labels.irrigate_now",
                    this.hass.language,
                  )}
                </button>
              `
            : ""}
        </div>

        <!-- SETTINGS EXPANSION -->
        <ha-expansion-panel
          .header="${localize("common.labels.settings", this.hass.language)}"
        >
          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.name", this.hass.language)}</span
            >
            <input
              type="text"
              class="settings-input"
              .value="${zone.name}"
              @input="${(e: Event) =>
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_NAME]: (e.target as HTMLInputElement).value,
                })}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.size", this.hass.language)}
              (${output_unit(this.config, ZONE_SIZE)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(zone.size.toFixed(2))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, { ...zone, [ZONE_SIZE]: v });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.throughput", this.hass.language)}
              (${output_unit(this.config, ZONE_THROUGHPUT)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(zone.throughput.toFixed(2))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_THROUGHPUT]: v,
                  });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.drainage_rate",
                this.hass.language,
              )}
              (${output_unit(this.config, ZONE_DRAINAGE_RATE)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat((zone.drainage_rate ?? 0).toFixed(2))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_DRAINAGE_RATE]: v,
                  });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.state",
                this.hass.language,
              )}</span
            >
            <select
              class="settings-input"
              .value="${live(zone.state)}"
              @change="${(e: Event) =>
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_STATE]: (e.target as HTMLSelectElement)
                    .value as SmartIrrigationZoneState,
                  [ZONE_DURATION]: 0,
                })}"
            >
              <option
                value="${SmartIrrigationZoneState.Automatic}"
                ?selected="${zone.state === SmartIrrigationZoneState.Automatic}"
              >
                ${localize(
                  "panels.zones.labels.states.automatic",
                  this.hass.language,
                )}
              </option>
              <option
                value="${SmartIrrigationZoneState.Manual}"
                ?selected="${zone.state === SmartIrrigationZoneState.Manual}"
              >
                ${localize(
                  "panels.zones.labels.states.manual",
                  this.hass.language,
                )}
              </option>
              <option
                value="${SmartIrrigationZoneState.Disabled}"
                ?selected="${zone.state === SmartIrrigationZoneState.Disabled}"
              >
                ${localize(
                  "panels.zones.labels.states.disabled",
                  this.hass.language,
                )}
              </option>
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("common.labels.module", this.hass.language)}</span
            >
            <select
              class="settings-input"
              .value="${live(
                zone.module !== undefined ? String(zone.module) : "",
              )}"
              @change="${(e: Event) => {
                const v = (e.target as HTMLSelectElement).value;
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_MODULE]: v ? parseInt(v) : undefined,
                });
              }}"
            >
              ${this._renderModuleOptions(zone.module)}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.mapping",
                this.hass.language,
              )}</span
            >
            <select
              class="settings-input"
              .value="${live(
                zone.mapping !== undefined ? String(zone.mapping) : "",
              )}"
              @change="${(e: Event) => {
                const v = (e.target as HTMLSelectElement).value;
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_MAPPING]: v ? parseInt(v) : undefined,
                });
              }}"
            >
              ${this._renderMappingOptions(zone.mapping)}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.linked_entity",
                this.hass.language,
              )}</span
            >
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${zone.linked_entity || ""}"
              .includeDomains="${["switch", "valve"]}"
              allow-custom-entity
              @value-changed="${(e: CustomEvent) =>
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_LINKED_ENTITY]: e.detail.value || undefined,
                })}"
            ></ha-entity-picker>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.flow_sensor",
                this.hass.language,
              )}</span
            >
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${zone.flow_sensor || ""}"
              .includeDomains="${["sensor"]}"
              allow-custom-entity
              @value-changed="${(e: CustomEvent) =>
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_FLOW_SENSOR]: e.detail.value || null,
                })}"
            ></ha-entity-picker>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.bucket", this.hass.language)}
              (${output_unit(this.config, ZONE_BUCKET)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              inputmode="decimal"
              .value="${parseFloat(Number(zone.bucket).toFixed(2))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, { ...zone, [ZONE_BUCKET]: v });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.maximum-bucket",
                this.hass.language,
              )}
              (${output_unit(this.config, ZONE_BUCKET)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(Number(zone.maximum_bucket).toFixed(2))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_MAXIMUM_BUCKET]: v,
                  });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.multiplier",
                this.hass.language,
              )}</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(zone.multiplier.toFixed(2))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_MULTIPLIER]: v,
                  });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.lead-time", this.hass.language)}
              (s)</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${zone.lead_time ?? 0}"
              @input="${(e: Event) => {
                const v = (e.target as HTMLInputElement).valueAsNumber;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_LEAD_TIME]: Math.round(v),
                  });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.maximum-duration",
                this.hass.language,
              )}
              (s)</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${zone.maximum_duration ?? ""}"
              @input="${(e: Event) => {
                const v = (e.target as HTMLInputElement).valueAsNumber;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_MAXIMUM_DURATION]: Math.round(v),
                  });
              }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.bucket_threshold",
                this.hass.language,
              )}
              (${output_unit(this.config, ZONE_BUCKET)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.5"
              max="0"
              inputmode="decimal"
              .value="${parseFloat((zone.bucket_threshold ?? 0).toFixed(1))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 10,
                  ) / 10;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_BUCKET_THRESHOLD]: Math.min(v, 0),
                  });
              }}"
            />
          </ha-settings-row>

          ${zone.state === SmartIrrigationZoneState.Manual
            ? html`
                <ha-settings-row>
                  <span slot="heading"
                    >${localize(
                      "panels.zones.labels.duration",
                      this.hass.language,
                    )}
                    (${UNIT_SECONDS})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${zone.duration ?? 0}"
                    @input="${(e: Event) => {
                      const v = (e.target as HTMLInputElement).valueAsNumber;
                      if (!isNaN(v))
                        this.handleEditZone(index, {
                          ...zone,
                          [ZONE_DURATION]: Math.round(v),
                        });
                    }}"
                  />
                </ha-settings-row>
              `
            : ""}

          <!-- Danger row -->
          <div class="settings-danger-row">
            <button
              class="action-btn"
              @click="${() =>
                this.handleEditZone(index, { ...zone, [ZONE_BUCKET]: 0.0 })}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.actions.reset-bucket",
                this.hass.language,
              )}
            </button>
            <button
              class="action-btn"
              class="danger-button"
              @click="${() =>
                this.handleRemoveZone(zone.id !== undefined ? zone.id : -1)}"
              ?disabled="${this.isSaving || zone.id === undefined}"
            >
              <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
              ${localize("common.actions.delete", this.hass.language)}
            </button>
          </div>
        </ha-expansion-panel>

        <!-- EXPLANATION EXPANSION -->
        ${zone.explanation && zone.explanation.length > 0
          ? html`
              <ha-expansion-panel
                .header="${localize(
                  "panels.zones.actions.information",
                  this.hass.language,
                )}"
              >
                <div class="card-content">${unsafeHTML(zone.explanation)}</div>
              </ha-expansion-panel>
            `
          : ""}

        <!-- WEATHER EXPANSION -->
        ${zone.mapping !== undefined
          ? html`
              <ha-expansion-panel
                .header="${localize(
                  "panels.zones.actions.view-weather-info",
                  this.hass.language,
                )}"
              >
                ${this.renderWeatherRecords(zone)}
              </ha-expansion-panel>
            `
          : ""}

        <!-- CALENDAR EXPANSION -->
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.view-watering-calendar",
            this.hass.language,
          )}"
        >
          ${this.renderWateringCalendar(zone)}
        </ha-expansion-panel>
      </ha-card>
    `;
  }

  render(): TemplateResult {
    if (!this.hass) return html``;

    if (this.isLoading) {
      return html`
        <ha-card header="${localize("panels.zones.title", this.hass.language)}">
          <div class="card-content">
            ${localize(
              "common.loading-messages.general",
              this.hass.language,
            )}...
          </div>
        </ha-card>
      `;
    }

    const confirmZone =
      this._confirmDeleteZoneId !== null
        ? this.zones.find((z) => z.id === this._confirmDeleteZoneId)
        : null;

    const hasLinkedZones = this.zones.some(
      (z) => z.linked_entity && (z.duration ?? 0) > 0,
    );

    // First-time setup banner: shown when nothing is configured yet
    const isFirstTime =
      this.zones.length === 0 &&
      this.modules.length === 0 &&
      this.mappings.length === 0;

    return html`
      ${isFirstTime
        ? html`
            <ha-card class="setup-banner-card">
              <div class="setup-banner">
                <div class="setup-banner-icon">🌱</div>
                <div class="setup-banner-content">
                  <div class="setup-banner-title">
                    ${localize("wizard.title", this.hass.language)}
                  </div>
                  <div class="setup-banner-desc">
                    ${localize(
                      "wizard.setup_complete_banner",
                      this.hass.language,
                    )}
                  </div>
                </div>
                <button
                  class="action-btn setup-banner-btn"
                  @click="${() => {
                    this.dispatchEvent(
                      new CustomEvent("open-wizard", {
                        bubbles: true,
                        composed: true,
                      }),
                    );
                  }}"
                >
                  ${localize("wizard.open_wizard", this.hass.language)}
                </button>
              </div>
            </ha-card>
          `
        : ""}
      <!-- Zones header card with + button and Irrigate All -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${localize("panels.zones.title", this.hass.language)}
          </div>
          <ha-icon-button
            .path="${mdiPlus}"
            @click="${() => {
              this._showAddZone = true;
            }}"
          ></ha-icon-button>
        </div>
        <div class="card-content zones-top-actions">
          <button
            class="action-btn"
            raised
            @click="${() => {
              if (!this.hass) return;
              irrigateNow(this.hass).catch((e) =>
                console.error("irrigate_now failed", e),
              );
            }}"
            ?disabled="${!hasLinkedZones || this.isSaving}"
          >
            ${localize("panels.zones.actions.irrigate_all", this.hass.language)}
          </button>
          ${!hasLinkedZones
            ? html`<span class="zones-top-note"
                >${localize(
                  "panels.info.cards.irrigate_now.no_linked_zones",
                  this.hass.language,
                )}</span
              >`
            : ""}
        </div>
      </ha-card>

      <!-- Add Zone dialog -->
      <ha-dialog
        .open="${this._showAddZone}"
        @closed="${() => {
          this._showAddZone = false;
        }}"
        heading="${localize(
          "panels.zones.cards.add-zone.header",
          this.hass.language,
        )}"
      >
        <div class="add-zone-form">
          <si-field
            label="${localize("panels.zones.labels.name", this.hass.language)}"
            required
          >
            <input
              type="text"
              class="settings-input add-zone-input"
              .value="${this._newZoneName}"
              @input="${(e: Event) => {
                this._newZoneName = (e.target as HTMLInputElement).value;
              }}"
            />
          </si-field>
          <si-field
            label="${localize("panels.zones.labels.size", this.hass.language)}"
            unit="${this.config?.units === CONF_METRIC ? "m²" : UNIT_SQ_FT}"
            help="${localize("field_help.zone_size", this.hass.language)}"
          >
            <input
              type="number"
              class="settings-input add-zone-input"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${this._newZoneSize}"
              @input="${(e: Event) => {
                this._newZoneSize = (e.target as HTMLInputElement).value;
              }}"
            />
          </si-field>
          <si-field
            label="${localize(
              "panels.zones.labels.throughput",
              this.hass.language,
            )}"
            unit="${this.config?.units === CONF_METRIC ? UNIT_LPM : UNIT_GPM}"
            help="${localize("field_help.zone_throughput", this.hass.language)}"
          >
            <input
              type="number"
              class="settings-input add-zone-input"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${this._newZoneThroughput}"
              @input="${(e: Event) => {
                this._newZoneThroughput = (e.target as HTMLInputElement).value;
              }}"
            />
          </si-field>
        </div>
        <div class="dialog-footer">
          <button
            class="dialog-btn"
            @click="${() => {
              this._showAddZone = false;
            }}"
          >
            ${localize("common.actions.cancel", this.hass.language)}
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            @click="${this.handleAddZone}"
            ?disabled="${!this._newZoneName.trim() || this.isSaving}"
          >
            ${this.isSaving
              ? localize("common.saving-messages.adding", this.hass.language)
              : localize(
                  "panels.zones.cards.add-zone.actions.add",
                  this.hass.language,
                )}
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirmation dialog -->
      ${confirmZone
        ? html`
            <ha-dialog
              open
              @closed="${() => {
                this._confirmDeleteZoneId = null;
              }}"
              heading="${localize(
                "common.actions.confirm_delete",
                this.hass.language,
              )}"
            >
              <p>
                ${localize(
                  "common.actions.confirm_delete_zone",
                  this.hass.language,
                )}
              </p>
              <p><strong>${confirmZone.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
                    this._confirmDeleteZoneId = null;
                  }}"
                >
                  ${localize("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
                  ${localize("common.actions.delete", this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          `
        : ""}

      <!-- Operation error banner -->
      ${this._operationError
        ? html`
            <ha-card class="error-banner-card">
              <div class="error-banner">
                <span class="error-banner-msg">${this._operationError}</span>
                <button
                  class="error-banner-close"
                  @click="${() => {
                    this._operationError = null;
                  }}"
                  aria-label="Dismiss"
                >
                  ✕
                </button>
              </div>
            </ha-card>
          `
        : ""}

      <!-- Zone cards -->
      ${this.zones.map((zone, index) => this.renderZone(zone, index))}

      <!-- Bulk actions card -->
      <ha-card>
        <ha-expansion-panel
          .header="${localize(
            "common.labels.bulk_actions",
            this.hass.language,
          )}"
        >
          <div class="card-content bulk-actions">
            <button
              class="action-btn"
              @click="${this.handleCalculateAllZones}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.calculate-all",
                this.hass.language,
              )}
            </button>
            <button
              class="action-btn"
              @click="${this.handleUpdateAllZones}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.update-all",
                this.hass.language,
              )}
            </button>
            <button
              class="action-btn"
              @click="${this.handleResetAllBuckets}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.reset-all-buckets",
                this.hass.language,
              )}
            </button>
            <button
              class="action-btn"
              @click="${this.handleClearAllWeatherdata}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.clear-all-weatherdata",
                this.hass.language,
              )}
            </button>
          </div>
        </ha-expansion-panel>
      </ha-card>
    `;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.globalDebounceTimer) {
      clearTimeout(this.globalDebounceTimer);
      this.globalDebounceTimer = null;
    }
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      ha-settings-row {
        padding: 0 16px;
      }

      ha-expansion-panel {
        border-top: 1px solid var(--divider-color);
      }

      .shortfield {
        width: 120px;
      }

      /* Zone status grid */
      .zone-status-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
      }

      .status-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 8px;
        background: var(--secondary-background-color);
        border-radius: 8px;
      }

      .status-label {
        font-size: 0.75rem;
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .status-value {
        font-size: 1rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      /* Action bar */
      .zone-action-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 0;
        padding-bottom: 8px;
      }

      /* State badge */
      .zone-state-badge {
        font-size: 0.75rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        align-self: center;
      }

      .state-automatic {
        background: var(--success-color, #4caf50);
        color: white;
      }

      .state-manual {
        background: var(--accent-color, var(--primary-color));
        color: white;
      }

      .state-disabled {
        background: var(--disabled-color, #bdbdbd);
        color: white;
      }

      /* Danger row in settings */
      .settings-danger-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 16px;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }

      .danger-button {
        --mdc-theme-primary: var(--error-color);
        color: var(--error-color);
      }

      /* Native input styled to match HA */
      .settings-input {
        background: var(--input-fill-color, var(--secondary-background-color));
        border: 1px solid var(--input-ink-color, var(--secondary-text-color));
        border-radius: 4px;
        color: var(--primary-text-color);
        padding: 6px 10px;
        font-family: var(
          --mdc-typography-body1-font-family,
          Roboto,
          sans-serif
        );
        font-size: 0.9375rem;
        box-sizing: border-box;
        height: 36px;
      }

      .settings-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }

      .settings-input.shortfield {
        width: 110px;
      }

      select.settings-input {
        cursor: pointer;
        min-width: 140px;
      }

      /* Add zone dialog form */
      .add-zone-form {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 8px 0;
        min-width: 300px;
      }

      .add-zone-input {
        width: 100%;
      }

      /* Zones top action bar */
      /* First-time setup banner */
      .setup-banner-card {
        border-left: 4px solid var(--primary-color);
      }

      .setup-banner {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        flex-wrap: wrap;
      }

      .setup-banner-icon {
        font-size: 2rem;
        flex-shrink: 0;
      }

      .setup-banner-content {
        flex: 1;
        min-width: 180px;
      }

      .setup-banner-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--primary-text-color);
        margin-bottom: 4px;
      }

      .setup-banner-desc {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
      }

      .setup-banner-btn {
        flex-shrink: 0;
      }

      .zones-top-actions {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
      }

      .zones-top-note {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        font-style: italic;
      }

      /* Dialog footer buttons */
      .dialog-footer {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        padding: 16px 0 8px;
        margin-top: 8px;
        border-top: 1px solid var(--divider-color);
      }

      .dialog-btn {
        background: transparent;
        border: 1px solid var(--primary-color);
        border-radius: 4px;
        color: var(--primary-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 8px 16px;
        transition: background 0.15s;
      }

      .dialog-btn:hover {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
      }

      .dialog-btn-primary {
        background: var(--primary-color);
        color: var(--text-primary-color, white);
      }

      .dialog-btn-primary:hover {
        opacity: 0.9;
        background: var(--primary-color);
      }

      .dialog-btn-primary:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .dialog-btn-danger {
        border-color: var(--error-color);
        color: var(--error-color);
      }

      .dialog-btn-danger:hover {
        background: rgba(var(--rgb-error-color, 244, 67, 54), 0.08);
      }

      /* Bulk actions */
      .bulk-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      /* Operation error banner */
      .error-banner-card {
        border-left: 4px solid var(--error-color, #f44336);
      }

      .error-banner {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
      }

      .error-banner-msg {
        flex: 1;
        color: var(--error-color, #f44336);
        font-size: 0.9rem;
        line-height: 1.4;
      }

      .error-banner-close {
        background: none;
        border: none;
        color: var(--secondary-text-color);
        cursor: pointer;
        font-size: 1rem;
        padding: 0 4px;
        flex-shrink: 0;
      }
    `;
  }
}
