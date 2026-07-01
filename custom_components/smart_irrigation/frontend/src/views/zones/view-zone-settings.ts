import { TemplateResult, LitElement, html, CSSResultGroup, css } from "lit";
import { unsafeHTML } from "lit/directives/unsafe-html.js";
import { live } from "lit/directives/live.js";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../../types";
import { loadHaForm } from "../../load-ha-elements";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { mdiDelete, mdiPlus } from "@mdi/js";
import {
  deleteZone,
  fetchConfig,
  fetchZones,
  saveZone,
  fetchModules,
  fetchMappings,
  resetAllBuckets,
  clearAllWeatherdata,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";

import {
  SmartIrrigationConfig,
  SmartIrrigationZone,
  SmartIrrigationZoneState,
  SmartIrrigationModule,
  SmartIrrigationMapping,
  RunLogEntry,
} from "../../types";
import { output_unit, showErrorToast } from "../../helpers";
import { formatVolume } from "../../common/units";
import { formatDateTime } from "../../common/datetime";
import { Path } from "../../common/navigation";
import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import {
  CONF_METRIC,
  DOMAIN,
  UNIT_SECONDS,
  ZONE_BUCKET,
  ZONE_DRAINAGE_RATE,
  ZONE_KC,
  ZONE_PLANT_TYPE,
  PLANT_TYPE_KC,
  SOIL_TYPE_DRAINAGE,
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
  ZONE_WATERING_MODE,
  ZONE_RUN_SERVICE,
  ZONE_DURATION_FIELD,
  ZONE_DURATION_UNIT,
  ZONE_STOP_SERVICE,
} from "../../const";
import "../../components/si-field";
import "../../components/si-zone-form";

/**
 * Setup → Zones: full zone configuration, reporting (weather / calendar) and
 * management (add / edit / delete / reset). The everyday dashboard lives in the
 * top-level Zones tab; its gear icon deep-links here with a `zone` URL param
 * that auto-expands and scrolls to the matching zone. (UX restructure N2/N3.)
 */
@customElement("smart-irrigation-view-zone-settings")
class SmartIrrigationViewZoneSettings extends SubscribeMixin(LitElement) {
  hass?: HomeAssistant;
  @property() config?: SmartIrrigationConfig;
  @property({ attribute: false }) public path?: Path;

  @property({ type: Array })
  private zones: SmartIrrigationZone[] = [];
  @property({ type: Array })
  private modules: SmartIrrigationModule[] = [];
  @property({ type: Array })
  private mappings: SmartIrrigationMapping[] = [];

  @property({ type: Boolean })
  private isLoading = true;

  private _initialLoadDone = false;
  private _scrolledToTarget = false;

  @property({ type: Boolean })
  private isSaving = false;

  @property({ type: Boolean })
  private _showAddZone = false;

  // Generic confirmation for destructive actions (reset bucket(s), clear data).
  @state() private _pendingConfirm: {
    title: string;
    body: string;
    confirmLabel: string;
    onConfirm: () => void;
  } | null = null;

  // Transient feedback for debounced auto-save of zone settings (UX H3).
  @state() private _saveStatus: "idle" | "saving" | "saved" = "idle";
  private _savedResetTimer: number | null = null;

  @property()
  private _confirmDeleteZoneId: number | null = null;

  @property()
  private _newZoneName = "";

  @property()
  private _newZoneSize = "";

  @property()
  private _newZoneThroughput = "";

  @property()
  private _newZoneEntity = "";

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

  /** Zone id targeted by a deep link from the dashboard gear icon. */
  private get _targetZoneId(): number | null {
    const z = this.path?.params?.zone;
    return z != null && z !== "" ? Number(z) : null;
  }

  firstUpdated() {
    loadHaForm()
      .then(() => this._scheduleUpdate())
      .catch((error) => {
        console.error("Failed to load HA form:", error);
        this._scheduleUpdate();
      });
  }

  updated() {
    // Scroll to the deep-linked zone once, after it has rendered.
    if (this._scrolledToTarget || this.isLoading) return;
    const target = this._targetZoneId;
    if (target === null) return;
    const el = this.shadowRoot?.querySelector(`#zone-${target}`);
    if (el) {
      this._scrolledToTarget = true;
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
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

    const isInitial = !this._initialLoadDone;

    try {
      if (isInitial) this.isLoading = true;

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
      this._initialLoadDone = true;
    } catch (error) {
      console.error("Error fetching data:", error);
      showErrorToast(this, this.hass, "common.errors.load_failed", error);
    } finally {
      if (isInitial) this.isLoading = false;
      this._scheduleUpdate();
    }
  }

  private handleResetAllBuckets(): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    resetAllBuckets(this.hass)
      .catch((error) => {
        console.error("Failed to reset all buckets:", error);
        showErrorToast(this, this.hass, "common.errors.action_failed", error);
      })
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
      .catch((error) => {
        console.error("Failed to clear all weather data:", error);
        showErrorToast(this, this.hass, "common.errors.action_failed", error);
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after clear-weather:", e),
        );
      });
  }

  private handleAddZone(): void {
    if (!this._newZoneName.trim()) return;

    // Link the new zone to the standard calculation module + sensor group so it
    // can calculate out of the box (a zone with no module/mapping never does).
    // Prefer the factory-default PyETO module; fall back to the first available.
    // The default sensor group is the first mapping.
    const stdModule =
      this.modules.find((m) => m.name === "PyETO") ?? this.modules[0];
    const stdMapping = this.mappings[0];

    const newZone: SmartIrrigationZone = {
      name: this._newZoneName.trim(),
      size: Math.round((parseFloat(this._newZoneSize) || 0) * 100) / 100,
      throughput:
        Math.round((parseFloat(this._newZoneThroughput) || 0) * 100) / 100,
      state: SmartIrrigationZoneState.Automatic,
      duration: 0,
      bucket: 0,
      module: stdModule?.id,
      delta: 0,
      explanation: "",
      multiplier: 1,
      mapping: stdMapping?.id,
      lead_time: 0,
      maximum_duration: undefined,
      maximum_bucket: undefined,
      drainage_rate: undefined,
      current_drainage: 0,
      linked_entity: this._newZoneEntity || undefined,
    };

    this.zones = [...this.zones, newZone];
    this.isSaving = true;
    this._showAddZone = false;

    this.saveToHA(newZone)
      .then(() => {
        this._newZoneName = "";
        this._newZoneSize = "";
        this._newZoneThroughput = "";
        this._newZoneEntity = "";
        return this._fetchData();
      })
      .catch((error) => {
        console.error("Failed to add zone:", error);
        this.zones = this.zones.slice(0, -1);
        showErrorToast(this, this.hass, "common.errors.save_failed", error);
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
      this._saveStatus = "saving";
      this.saveToHA(updatedZone)
        .then(() => this._markSaved())
        .catch((error) => {
          console.error("Failed to save zone:", error);
          this._saveStatus = "idle";
          showErrorToast(this, this.hass, "common.errors.save_failed", error);
        })
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
        showErrorToast(this, this.hass, "common.errors.delete_failed", error);
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

  private _runPendingConfirm(): void {
    const c = this._pendingConfirm;
    this._pendingConfirm = null;
    c?.onConfirm();
  }

  /** Flash a "Saved" chip, then fade back to idle. */
  private _markSaved(): void {
    this._saveStatus = "saved";
    if (this._savedResetTimer) clearTimeout(this._savedResetTimer);
    this._savedResetTimer = window.setTimeout(() => {
      this._saveStatus = "idle";
      this._scheduleUpdate();
    }, 2000);
    this._scheduleUpdate();
  }

  private _renderSaveStatus(): TemplateResult {
    if (!this.hass || this._saveStatus === "idle") return html``;
    const saving = this._saveStatus === "saving";
    return html`
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${saving ? "mdi:content-save-outline" : "mdi:check-circle"}"
        ></ha-icon>
        ${localize(
          saving
            ? "common.saving-messages.saving"
            : "panels.zones.status.saved",
          this.hass.language,
        )}
      </span>
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

    return html`
      <ha-card id="zone-${zone.id ?? "new"}">
        <div class="card-header">
          <div class="name">${zone.name}</div>
        </div>

        <!-- Settings shown directly (no longer collapsible — the calendar that
             used to sit alongside it moved to the Weather & Location tab). -->
        <div class="card-content zone-settings">
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
                "panels.zones.labels.soil_type",
                this.hass.language,
              )}</span
            >
            <span slot="description"
              >${localize(
                "field_help.zone_soil_type",
                this.hass.language,
              )}</span
            >
            <select
              class="settings-input"
              .value="${live(
                Object.keys(SOIL_TYPE_DRAINAGE).find(
                  (s) => SOIL_TYPE_DRAINAGE[s] === zone.drainage_rate,
                ) ?? "custom",
              )}"
              @change="${(e: Event) => {
                const st = (e.target as HTMLSelectElement).value;
                if (st !== "custom" && SOIL_TYPE_DRAINAGE[st] !== undefined)
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_DRAINAGE_RATE]: SOIL_TYPE_DRAINAGE[st],
                  });
              }}"
            >
              <option
                value="custom"
                ?selected="${!Object.values(SOIL_TYPE_DRAINAGE).includes(
                  zone.drainage_rate ?? -1,
                )}"
              >
                ${localize(
                  "panels.zones.labels.soil_types.custom",
                  this.hass.language,
                )}
              </option>
              ${Object.keys(SOIL_TYPE_DRAINAGE).map(
                (st) => html`
                  <option
                    value="${st}"
                    ?selected="${SOIL_TYPE_DRAINAGE[st] === zone.drainage_rate}"
                  >
                    ${localize(
                      `panels.zones.labels.soil_types.${st}`,
                      this.hass!.language,
                    )}
                  </option>
                `,
              )}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize(
                "panels.zones.labels.drainage_rate",
                this.hass.language,
              )}
              (${output_unit(this.config, ZONE_DRAINAGE_RATE)})</span
            >
            <span slot="description"
              >${localize(
                "field_help.zone_drainage_rate",
                this.hass.language,
              )}</span
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
                "panels.zones.labels.plant_type",
                this.hass.language,
              )}</span
            >
            <span slot="description"
              >${localize(
                "field_help.zone_plant_type",
                this.hass.language,
              )}</span
            >
            <select
              class="settings-input"
              .value="${live(zone.plant_type ?? "custom")}"
              @change="${(e: Event) => {
                const pt = (e.target as HTMLSelectElement).value;
                const next: Partial<SmartIrrigationZone> = {
                  [ZONE_PLANT_TYPE]: pt,
                };
                if (pt !== "custom" && PLANT_TYPE_KC[pt] !== undefined)
                  next[ZONE_KC] = PLANT_TYPE_KC[pt];
                this.handleEditZone(index, { ...zone, ...next });
              }}"
            >
              <option
                value="custom"
                ?selected="${(zone.plant_type ?? "custom") === "custom"}"
              >
                ${localize(
                  "panels.zones.labels.plant_types.custom",
                  this.hass.language,
                )}
              </option>
              ${Object.keys(PLANT_TYPE_KC).map(
                (pt) => html`
                  <option value="${pt}" ?selected="${zone.plant_type === pt}">
                    ${localize(
                      `panels.zones.labels.plant_types.${pt}`,
                      this.hass!.language,
                    )}
                  </option>
                `,
              )}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${localize("panels.zones.labels.kc", this.hass.language)}</span
            >
            <span slot="description"
              >${localize("field_help.zone_kc", this.hass.language)}</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.05"
              min="0"
              inputmode="decimal"
              .value="${parseFloat((zone.kc ?? 1).toFixed(2))}"
              @input="${(e: Event) => {
                const v =
                  Math.round(
                    (e.target as HTMLInputElement).valueAsNumber * 100,
                  ) / 100;
                if (!isNaN(v))
                  this.handleEditZone(index, {
                    ...zone,
                    [ZONE_KC]: v,
                    [ZONE_PLANT_TYPE]: "custom",
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
                "panels.zones.labels.watering_mode",
                this.hass.language,
              )}</span
            >
            <span slot="description"
              >${localize(
                "panels.zones.labels.watering_mode_description",
                this.hass.language,
              )}</span
            >
            <select
              class="settings-input"
              .value="${live(zone.watering_mode ?? "classic")}"
              @change="${(e: Event) =>
                this.handleEditZone(index, {
                  ...zone,
                  [ZONE_WATERING_MODE]: (e.target as HTMLSelectElement).value,
                })}"
            >
              <option
                value="classic"
                ?selected="${(zone.watering_mode ?? "classic") === "classic"}"
              >
                ${localize(
                  "panels.zones.labels.watering_modes.classic",
                  this.hass.language,
                )}
              </option>
              <option
                value="service"
                ?selected="${zone.watering_mode === "service"}"
              >
                ${localize(
                  "panels.zones.labels.watering_modes.service",
                  this.hass.language,
                )}
              </option>
            </select>
          </ha-settings-row>

          ${zone.watering_mode === "service"
            ? html`
                <ha-settings-row>
                  <span slot="heading"
                    >${localize(
                      "panels.zones.labels.run_service",
                      this.hass.language,
                    )}</span
                  >
                  <span slot="description"
                    >${localize(
                      "panels.zones.labels.run_service_help",
                      this.hass.language,
                    )}</span
                  >
                  <ha-entity-picker
                    .hass="${this.hass}"
                    .value="${zone.run_service || ""}"
                    .includeDomains="${["script"]}"
                    allow-custom-entity
                    @value-changed="${(e: CustomEvent) =>
                      this.handleEditZone(index, {
                        ...zone,
                        [ZONE_RUN_SERVICE]: e.detail.value || null,
                      })}"
                  ></ha-entity-picker>
                </ha-settings-row>
                <ha-settings-row>
                  <span slot="heading"
                    >${localize(
                      "panels.zones.labels.duration_field",
                      this.hass.language,
                    )}</span
                  >
                  <span slot="description"
                    >${localize(
                      "panels.zones.labels.duration_field_help",
                      this.hass.language,
                    )}</span
                  >
                  <input
                    type="text"
                    class="settings-input"
                    placeholder="${localize(
                      "panels.zones.labels.duration_field_placeholder",
                      this.hass.language,
                    )}"
                    .value="${zone.duration_field || "duration"}"
                    @input="${(e: Event) =>
                      this.handleEditZone(index, {
                        ...zone,
                        [ZONE_DURATION_FIELD]:
                          (e.target as HTMLInputElement).value || undefined,
                      })}"
                  />
                </ha-settings-row>
                <ha-settings-row>
                  <span slot="heading"
                    >${localize(
                      "panels.zones.labels.duration_unit",
                      this.hass.language,
                    )}</span
                  >
                  <span slot="description"
                    >${localize(
                      "panels.zones.labels.duration_unit_help",
                      this.hass.language,
                    )}</span
                  >
                  <select
                    class="settings-input"
                    .value="${live(zone.duration_unit ?? "seconds")}"
                    @change="${(e: Event) =>
                      this.handleEditZone(index, {
                        ...zone,
                        [ZONE_DURATION_UNIT]: (e.target as HTMLSelectElement)
                          .value,
                      })}"
                  >
                    <option
                      value="seconds"
                      ?selected="${(zone.duration_unit ?? "seconds") ===
                      "seconds"}"
                    >
                      ${localize(
                        "panels.zones.labels.duration_units.seconds",
                        this.hass.language,
                      )}
                    </option>
                    <option
                      value="minutes"
                      ?selected="${zone.duration_unit === "minutes"}"
                    >
                      ${localize(
                        "panels.zones.labels.duration_units.minutes",
                        this.hass.language,
                      )}
                    </option>
                  </select>
                </ha-settings-row>
                <ha-settings-row>
                  <span slot="heading"
                    >${localize(
                      "panels.zones.labels.stop_service",
                      this.hass.language,
                    )}</span
                  >
                  <span slot="description"
                    >${localize(
                      "panels.zones.labels.stop_service_help",
                      this.hass.language,
                    )}</span
                  >
                  <ha-entity-picker
                    .hass="${this.hass}"
                    .value="${zone.stop_service || ""}"
                    .includeDomains="${["script"]}"
                    allow-custom-entity
                    @value-changed="${(e: CustomEvent) =>
                      this.handleEditZone(index, {
                        ...zone,
                        [ZONE_STOP_SERVICE]: e.detail.value || null,
                      })}"
                  ></ha-entity-picker>
                </ha-settings-row>
              `
            : ""}
          ${zone.watering_mode !== "service"
            ? html`
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
                    .includeDomains="${["switch", "valve", "input_boolean"]}"
                    allow-custom-entity
                    @value-changed="${(e: CustomEvent) =>
                      this.handleEditZone(index, {
                        ...zone,
                        [ZONE_LINKED_ENTITY]: e.detail.value || undefined,
                      })}"
                  ></ha-entity-picker>
                </ha-settings-row>
              `
            : ""}

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
              (${UNIT_SECONDS})</span
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
              (${UNIT_SECONDS})</span
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
              @click="${() => {
                this._pendingConfirm = {
                  title: localize(
                    "panels.zones.confirm_action.reset_bucket_title",
                    this.hass!.language,
                  ),
                  body: localize(
                    "panels.zones.confirm_action.reset_bucket_body",
                    this.hass!.language,
                  ),
                  confirmLabel: localize(
                    "panels.zones.actions.reset-bucket",
                    this.hass!.language,
                  ),
                  onConfirm: () =>
                    this.handleEditZone(index, {
                      ...zone,
                      [ZONE_BUCKET]: 0.0,
                    }),
                };
              }}"
              ?disabled="${this.isSaving}"
            >
              ${localize(
                "panels.zones.actions.reset-bucket",
                this.hass.language,
              )}
            </button>
            <button
              class="action-btn danger-button"
              @click="${() =>
                this.handleRemoveZone(zone.id !== undefined ? zone.id : -1)}"
              ?disabled="${this.isSaving || zone.id === undefined}"
            >
              <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
              ${localize("common.actions.delete", this.hass.language)}
            </button>
          </div>
        </div>

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

        <!-- Run history + cumulative water usage (WS-2) -->
        ${this._renderRunHistory(zone)}

        <!-- Weather records + the watering/seasonal calendar now live on the
             Weather & Location tab (climate is the same for every zone). -->
      </ha-card>
    `;
  }

  /** Cumulative water usage + a bounded "Recent runs" list for one zone. */
  private _renderRunHistory(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass) return html``;
    const metric = this.config?.units === CONF_METRIC;
    const log = zone.run_log ?? [];
    const lang = this.hass.language;

    return html`
      <ha-expansion-panel
        .header="${localize("panels.zones.history.title", lang)}"
      >
        <div class="card-content">
          <div class="history-usage">
            <span class="history-usage-label"
              >${localize("panels.zones.history.total_used", lang)}</span
            >
            <span class="history-usage-value"
              >${formatVolume(zone.water_used_total ?? 0, metric)}</span
            >
          </div>
          ${log.length === 0
            ? html`<div class="weather-note">
                ${localize("panels.zones.history.empty", lang)}
              </div>`
            : html`
                <table class="history-table">
                  <thead>
                    <tr>
                      <th>${localize("panels.zones.history.when", lang)}</th>
                      <th>${localize("panels.zones.history.result", lang)}</th>
                      <th class="num">
                        ${localize("panels.zones.history.volume", lang)}
                      </th>
                      <th>${localize("panels.zones.history.detail", lang)}</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${log.map((entry) => this._renderRunLogRow(entry, metric))}
                  </tbody>
                </table>
              `}
        </div>
      </ha-expansion-panel>
    `;
  }

  private _renderRunLogRow(
    entry: RunLogEntry,
    metric: boolean,
  ): TemplateResult {
    const lang = this.hass!.language;
    const resultLabel = localize(
      `panels.zones.history.results.${entry.result}`,
      lang,
    );
    // The detail field carries a skip-reason code, a fault code, or the
    // calculation explanation (HTML). Reason/fault codes get a friendly
    // localized label; the explanation is rendered as-is.
    let detail = "";
    if (entry.detail) {
      if (entry.result === "skipped") {
        detail = entry.detail
          .split(",")
          .map((r) => localize(`panels.zones.outlook.checks.${r}`, lang) || r)
          .join(", ");
      } else if (entry.result === "failed") {
        detail =
          localize(`panels.zones.fault.${entry.detail}`, lang) || entry.detail;
      } else {
        detail = entry.detail;
      }
    }
    return html`
      <tr>
        <td>${formatDateTime(entry.ts)}</td>
        <td>
          <span class="history-chip history-${entry.result}"
            >${resultLabel || entry.result}</span
          >
        </td>
        <td class="num">
          ${entry.volume_l > 0 ? formatVolume(entry.volume_l, metric) : "-"}
        </td>
        <td class="history-detail">${unsafeHTML(detail)}</td>
      </tr>
    `;
  }

  render(): TemplateResult {
    if (!this.hass) return html``;

    if (this.isLoading) {
      return html`
        <ha-card header="${localize("panels.zones.title", this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${localize("common.loading-messages.general", this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;
    }

    const confirmZone =
      this._confirmDeleteZoneId !== null
        ? this.zones.find((z) => z.id === this._confirmDeleteZoneId)
        : null;

    return html`
      <!-- Header: title + save chip + add zone -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${localize("panels.zones.title", this.hass.language)}
          </div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${mdiPlus}"
            title="${localize(
              "panels.zones.cards.add-zone.header",
              this.hass.language,
            )}"
            @click="${() => {
              this._showAddZone = true;
            }}"
          ></ha-icon-button>
        </div>
        ${this.zones.length === 0
          ? html`<div class="card-content">
              <div class="weather-note">
                ${localize("panels.zones.no_items", this.hass.language)}
              </div>
            </div>`
          : ""}
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
          <si-zone-form
            .hass="${this.hass}"
            .metric="${this.config?.units === CONF_METRIC}"
            .name="${this._newZoneName}"
            .size="${this._newZoneSize}"
            .throughput="${this._newZoneThroughput}"
            .linkedEntity="${this._newZoneEntity}"
            showEntity
            @name-changed="${(e: CustomEvent) => {
              this._newZoneName = e.detail.value;
            }}"
            @size-changed="${(e: CustomEvent) => {
              this._newZoneSize = e.detail.value;
            }}"
            @throughput-changed="${(e: CustomEvent) => {
              this._newZoneThroughput = e.detail.value;
            }}"
            @entity-changed="${(e: CustomEvent) => {
              this._newZoneEntity = e.detail.value;
            }}"
          ></si-zone-form>
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

      <!-- Generic destructive-action confirmation dialog -->
      ${this._pendingConfirm
        ? html`
            <ha-dialog
              open
              @closed="${() => {
                this._pendingConfirm = null;
              }}"
              heading="${this._pendingConfirm.title}"
            >
              <p>${this._pendingConfirm.body}</p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
                    this._pendingConfirm = null;
                  }}"
                >
                  ${localize("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._runPendingConfirm}"
                >
                  ${this._pendingConfirm.confirmLabel}
                </button>
              </div>
            </ha-dialog>
          `
        : ""}

      <!-- Zone cards -->
      ${this.zones.map((zone, index) => this.renderZone(zone, index))}

      <!-- Maintenance (destructive) -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${localize("common.labels.bulk_actions", this.hass.language)}
          </div>
        </div>
        <div class="card-content bulk-actions">
          <button
            class="action-btn danger-button"
            @click="${() => {
              this._pendingConfirm = {
                title: localize(
                  "panels.zones.confirm_action.reset_all_buckets_title",
                  this.hass!.language,
                ),
                body: localize(
                  "panels.zones.confirm_action.reset_all_buckets_body",
                  this.hass!.language,
                ),
                confirmLabel: localize(
                  "panels.zones.cards.zone-actions.actions.reset-all-buckets",
                  this.hass!.language,
                ),
                onConfirm: () => this.handleResetAllBuckets(),
              };
            }}"
            ?disabled="${this.isSaving}"
          >
            ${localize(
              "panels.zones.cards.zone-actions.actions.reset-all-buckets",
              this.hass.language,
            )}
          </button>
          <button
            class="action-btn danger-button"
            @click="${() => {
              this._pendingConfirm = {
                title: localize(
                  "panels.zones.confirm_action.clear_weather_title",
                  this.hass!.language,
                ),
                body: localize(
                  "panels.zones.confirm_action.clear_weather_body",
                  this.hass!.language,
                ),
                confirmLabel: localize(
                  "panels.zones.cards.zone-actions.actions.clear-all-weatherdata",
                  this.hass!.language,
                ),
                onConfirm: () => this.handleClearAllWeatherdata(),
              };
            }}"
            ?disabled="${this.isSaving}"
          >
            ${localize(
              "panels.zones.cards.zone-actions.actions.clear-all-weatherdata",
              this.hass.language,
            )}
          </button>
        </div>
      </ha-card>
    `;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.globalDebounceTimer) {
      clearTimeout(this.globalDebounceTimer);
      this.globalDebounceTimer = null;
    }
    if (this._savedResetTimer) {
      clearTimeout(this._savedResetTimer);
      this._savedResetTimer = null;
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

      /* Run history (WS-2) */
      .history-usage {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 12px;
      }
      .history-usage-value {
        font-size: 1.25rem;
        font-weight: 600;
      }
      .history-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
      }
      .history-table th,
      .history-table td {
        text-align: left;
        padding: 4px 8px;
        border-bottom: 1px solid var(--divider-color);
        vertical-align: top;
      }
      .history-table th.num,
      .history-table td.num {
        text-align: right;
        white-space: nowrap;
      }
      .history-detail {
        color: var(--secondary-text-color);
      }
      .history-chip {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
        color: #fff;
        background: var(--secondary-text-color);
      }
      .history-completed {
        background: var(--success-color, #2e7d32);
      }
      .history-partial {
        background: var(--warning-color, #f9a825);
      }
      .history-failed {
        background: var(--error-color, #c62828);
      }
      .history-skipped {
        background: var(--info-color, #0277bd);
      }

      /* Auto-save status chip */
      .save-status {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-left: auto;
        margin-right: 8px;
        font-size: 0.8125rem;
        font-weight: 500;
      }

      .save-status ha-icon {
        --mdc-icon-size: 18px;
      }

      .save-status.saving {
        color: var(--secondary-text-color);
      }

      .save-status.saved {
        color: var(--success-color, #2e7d32);
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

      .action-btn.danger-button {
        color: var(--error-color);
        border-color: var(--error-color);
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
    `;
  }
}

export { SmartIrrigationViewZoneSettings };
