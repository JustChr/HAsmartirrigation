import { TemplateResult, LitElement, html, CSSResultGroup, css } from "lit";
import { unsafeHTML } from "lit/directives/unsafe-html.js";
import { property, customElement } from "lit/decorators.js";
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
  DOMAIN,
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

  @property()
  private _confirmDeleteZoneId: number | null = null;

  @property()
  private _newZoneName = "";

  @property()
  private _newZoneSize = "";

  @property()
  private _newZoneThroughput = "";

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
    loadHaForm().catch((error) => {
      console.error("Failed to load HA form:", error);
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
    calculateAllZones(this.hass)
      .catch((error) => console.error("Failed to calculate all zones:", error))
      .finally(() => {
        this.isSaving = false;
        this._scheduleUpdate();
      });
  }

  private handleUpdateAllZones(): void {
    if (!this.hass) return;
    this.isSaving = true;
    updateAllZones(this.hass)
      .catch((error) => console.error("Failed to update all zones:", error))
      .finally(() => {
        this.isSaving = false;
        this._scheduleUpdate();
      });
  }

  private handleResetAllBuckets(): void {
    if (!this.hass) return;
    this.isSaving = true;
    resetAllBuckets(this.hass)
      .catch((error) => console.error("Failed to reset all buckets:", error))
      .finally(() => {
        this.isSaving = false;
        this._scheduleUpdate();
      });
  }

  private handleClearAllWeatherdata(): void {
    if (!this.hass) return;
    this.isSaving = true;
    clearAllWeatherdata(this.hass)
      .catch((error) =>
        console.error("Failed to clear all weather data:", error),
      )
      .finally(() => {
        this.isSaving = false;
        this._scheduleUpdate();
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

    this.zones[index] = updatedZone;

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
    void calculateZone(this.hass, zone.id.toString());
  }

  private handleUpdateZone(index: number): void {
    const zone = this.zones[index];
    if (!zone || zone.id == undefined || !this.hass) return;
    void updateZone(this.hass, zone.id.toString());
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

  private _renderModuleOptions(): TemplateResult {
    if (!this.hass) return html``;
    return html`
      <mwc-list-item value="">
        ---${localize("common.labels.select", this.hass.language)}---
      </mwc-list-item>
      ${this.modules.map(
        (m) => html`
          <mwc-list-item value="${m.id}">${m.id}: ${m.name}</mwc-list-item>
        `,
      )}
    `;
  }

  private _renderMappingOptions(): TemplateResult {
    if (!this.hass) return html``;
    return html`
      <mwc-list-item value="">
        ---${localize("common.labels.select", this.hass.language)}---
      </mwc-list-item>
      ${this.mappings.map(
        (m) => html`
          <mwc-list-item value="${m.id}">${m.id}: ${m.name}</mwc-list-item>
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
                <ha-button
                  @click="${() => this.handleCalculateZone(index)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon slot="icon" icon="mdi:calculator"></ha-icon>
                  ${localize(
                    "panels.zones.actions.calculate",
                    this.hass.language,
                  )}
                </ha-button>
                <ha-button
                  @click="${() => this.handleUpdateZone(index)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon slot="icon" icon="mdi:update"></ha-icon>
                  ${localize("panels.zones.actions.update", this.hass.language)}
                </ha-button>
              `
            : ""}
          ${zone.linked_entity && (zone.duration ?? 0) > 0
            ? html`
                <ha-button
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
                    "panels.zones.actions.irrigate_now",
                    this.hass.language,
                  )}
                </ha-button>
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
            <ha-textfield
              .value="${zone.name}"
              @input="${(e: Event) =>
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_NAME]: (e.target as HTMLInputElement).value,
                })}"
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.size", this.hass.language)}
              (${output_unit(this.config, ZONE_SIZE)})</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${String(parseFloat(zone.size.toFixed(2)))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, { ...zone, [ZONE_SIZE]: v });
              }}"
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.throughput", this.hass.language)}
              (${output_unit(this.config, ZONE_THROUGHPUT)})</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${String(parseFloat(zone.throughput.toFixed(2)))}"
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
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.drainage_rate",
                this.hass.language,
              )}
              (${output_unit(this.config, ZONE_DRAINAGE_RATE)})</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${String(
                parseFloat((zone.drainage_rate ?? 0).toFixed(2)),
              )}"
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
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.state",
                this.hass.language,
              )}</span
            >
            <ha-select
              .value="${zone.state}"
              @selected="${(e: CustomEvent) =>
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_STATE]: e.detail.value as SmartIrrigationZoneState,
                  [ZONE_DURATION]: 0,
                })}"
              @closed="${(e: Event) => e.stopPropagation()}"
            >
              <mwc-list-item value="${SmartIrrigationZoneState.Automatic}">
                ${localize(
                  "panels.zones.labels.states.automatic",
                  this.hass.language,
                )}
              </mwc-list-item>
              <mwc-list-item value="${SmartIrrigationZoneState.Manual}">
                ${localize(
                  "panels.zones.labels.states.manual",
                  this.hass.language,
                )}
              </mwc-list-item>
              <mwc-list-item value="${SmartIrrigationZoneState.Disabled}">
                ${localize(
                  "panels.zones.labels.states.disabled",
                  this.hass.language,
                )}
              </mwc-list-item>
            </ha-select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("common.labels.module", this.hass.language)}</span
            >
            <ha-select
              .value="${zone.module !== undefined ? String(zone.module) : ""}"
              @selected="${(e: CustomEvent) => {
                const v = e.detail.value;
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_MODULE]: v ? parseInt(v) : undefined,
                });
              }}"
              @closed="${(e: Event) => e.stopPropagation()}"
            >
              ${this._renderModuleOptions()}
            </ha-select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.mapping",
                this.hass.language,
              )}</span
            >
            <ha-select
              .value="${zone.mapping !== undefined ? String(zone.mapping) : ""}"
              @selected="${(e: CustomEvent) => {
                const v = e.detail.value;
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_MAPPING]: v ? parseInt(v) : undefined,
                });
              }}"
              @closed="${(e: Event) => e.stopPropagation()}"
            >
              ${this._renderMappingOptions()}
            </ha-select>
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
            <ha-textfield
              type="number"
              class="shortfield"
              step="0.1"
              inputmode="decimal"
              .value="${String(parseFloat(Number(zone.bucket).toFixed(2)))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, { ...zone, [ZONE_BUCKET]: v });
              }}"
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.maximum-bucket",
                this.hass.language,
              )}
              (${output_unit(this.config, ZONE_BUCKET)})</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${String(
                parseFloat(Number(zone.maximum_bucket).toFixed(2)),
              )}"
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
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.multiplier",
                this.hass.language,
              )}</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${String(parseFloat(zone.multiplier.toFixed(2)))}"
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
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.lead-time", this.hass.language)}
              (s)</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${String(zone.lead_time ?? 0)}"
              @input="${(e: Event) => {
                const v = (e.target as HTMLInputElement).valueAsNumber;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_LEAD_TIME]: Math.round(v),
                  });
              }}"
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.maximum-duration",
                this.hass.language,
              )}
              (s)</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${String(zone.maximum_duration ?? "")}"
              @input="${(e: Event) => {
                const v = (e.target as HTMLInputElement).valueAsNumber;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_MAXIMUM_DURATION]: Math.round(v),
                  });
              }}"
            ></ha-textfield>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.bucket_threshold",
                this.hass.language,
              )}
              (${output_unit(this.config, ZONE_BUCKET)})</span
            >
            <ha-textfield
              type="number"
              class="shortfield"
              step="0.5"
              max="0"
              inputmode="decimal"
              .value="${String(
                parseFloat((zone.bucket_threshold ?? 0).toFixed(1)),
              )}"
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
            ></ha-textfield>
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
                  <ha-textfield
                    type="number"
                    class="shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${String(zone.duration ?? 0)}"
                    @input="${(e: Event) => {
                      const v = (e.target as HTMLInputElement).valueAsNumber;
                      if (!isNaN(v))
                        this.handleEditZone(index, {
                          ...zone,
                          [ZONE_DURATION]: Math.round(v),
                        });
                    }}"
                  ></ha-textfield>
                </ha-settings-row>
              `
            : ""}

          <!-- Danger row -->
          <div class="settings-danger-row">
            <ha-button
              @click="${() =>
                this.handleEditZone(index, { ...zone, [ZONE_BUCKET]: 0.0 })}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.actions.reset-bucket",
                this.hass.language,
              )}
            </ha-button>
            <ha-button
              class="danger-button"
              @click="${() =>
                this.handleRemoveZone(zone.id !== undefined ? zone.id : -1)}"
              ?disabled="${this.isSaving || zone.id === undefined}"
            >
              <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
              ${localize("common.actions.delete", this.hass.language)}
            </ha-button>
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

    return html`
      <!-- Zones header card with + button -->
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
        <div class="card-content">
          ${localize("panels.zones.description", this.hass.language)}
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
          <ha-textfield
            label="${localize("panels.zones.labels.name", this.hass.language)}"
            .value="${this._newZoneName}"
            @input="${(e: Event) => {
              this._newZoneName = (e.target as HTMLInputElement).value;
            }}"
          ></ha-textfield>
          <ha-textfield
            label="${localize("panels.zones.labels.size", this.hass.language)}"
            type="number"
            step="0.1"
            min="0"
            inputmode="decimal"
            .value="${this._newZoneSize}"
            @input="${(e: Event) => {
              this._newZoneSize = (e.target as HTMLInputElement).value;
            }}"
          ></ha-textfield>
          <ha-textfield
            label="${localize(
              "panels.zones.labels.throughput",
              this.hass.language,
            )}"
            type="number"
            step="0.1"
            min="0"
            inputmode="decimal"
            .value="${this._newZoneThroughput}"
            @input="${(e: Event) => {
              this._newZoneThroughput = (e.target as HTMLInputElement).value;
            }}"
          ></ha-textfield>
        </div>
        <ha-button
          slot="secondaryAction"
          @click="${() => {
            this._showAddZone = false;
          }}"
        >
          ${localize("common.actions.cancel", this.hass.language)}
        </ha-button>
        <ha-button
          slot="primaryAction"
          raised
          @click="${this.handleAddZone}"
          ?disabled="${!this._newZoneName.trim() || this.isSaving}"
        >
          ${this.isSaving
            ? localize("common.saving-messages.adding", this.hass.language)
            : localize(
                "panels.zones.cards.add-zone.actions.add",
                this.hass.language,
              )}
        </ha-button>
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
              <ha-button
                slot="secondaryAction"
                @click="${() => {
                  this._confirmDeleteZoneId = null;
                }}"
              >
                ${localize("common.actions.cancel", this.hass.language)}
              </ha-button>
              <ha-button
                slot="primaryAction"
                class="danger-button"
                @click="${this._confirmDelete}"
              >
                ${localize("common.actions.delete", this.hass.language)}
              </ha-button>
            </ha-dialog>
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
            <ha-button
              @click="${this.handleCalculateAllZones}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.calculate-all",
                this.hass.language,
              )}
            </ha-button>
            <ha-button
              @click="${this.handleUpdateAllZones}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.update-all",
                this.hass.language,
              )}
            </ha-button>
            <ha-button
              @click="${this.handleResetAllBuckets}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.reset-all-buckets",
                this.hass.language,
              )}
            </ha-button>
            <ha-button
              @click="${this.handleClearAllWeatherdata}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.cards.zone-actions.actions.clear-all-weatherdata",
                this.hass.language,
              )}
            </ha-button>
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

      /* Add zone dialog form */
      .add-zone-form {
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding: 8px 0;
        min-width: 300px;
      }

      .add-zone-form ha-textfield {
        width: 100%;
      }

      /* Bulk actions */
      .bulk-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
    `;
  }
}
