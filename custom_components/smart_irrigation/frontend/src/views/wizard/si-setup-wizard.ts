import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../../types";

import {
  fetchAllModules,
  fetchModules,
  fetchMappings,
  fetchConfig,
  saveModule,
  saveMapping,
  saveZone,
  saveSchedule,
  fetchWeatherConfig,
  saveWeatherConfig,
  WeatherConfig,
  SaveResult,
} from "../../data/websockets";
import {
  SmartIrrigationConfig,
  SmartIrrigationModule,
  SmartIrrigationMapping,
  SmartIrrigationZoneState,
} from "../../types";
import { localize } from "../../../localize/localize";
import { globalStyle } from "../../styles/global-style";
import { extractErrorMessage } from "../../helpers";
import {
  CONF_WEATHER_SERVICE_OPENMETEO,
  MAPPING_TEMPERATURE,
  MAPPING_HUMIDITY,
  MAPPING_PRECIPITATION,
  MAPPING_CONF_SOURCE,
  MAPPING_CONF_SOURCE_WEATHER_SERVICE,
  MAPPING_CONF_SOURCE_NONE,
} from "../../const";
import "../../components/si-field";
import "../../components/si-weather-source-config";
import "../../components/si-zone-form";

enum WizardStep {
  Welcome = 0,
  Weather = 1,
  Module = 2,
  Mapping = 3,
  Zone = 4,
  Done = 5,
}

const TOTAL_STEPS = 5; // steps 1..5, step 0 is welcome (not counted)

/**
 * Guided setup wizard displayed as a full-page overlay.
 * Emits "wizard-close" custom event when the user finishes or closes.
 * Emits "wizard-navigate" with { page: "zones"|"setup" } on done.
 */
@customElement("si-setup-wizard")
export class SiSetupWizard extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;

  @state() private _step: WizardStep = WizardStep.Welcome;
  @state() private _saving = false;
  @state() private _error = "";
  // Confirm-before-close when the user clicks the backdrop mid-flow (UX N4).
  @state() private _confirmClose = false;

  @state() private _siConfig: SmartIrrigationConfig | null = null;

  // Step 2 — Weather
  @state() private _useWeather = false;
  @state() private _weatherService: string = CONF_WEATHER_SERVICE_OPENMETEO;
  @state() private _apiKey = "";
  @state() private _weatherConfig: WeatherConfig | null = null;

  // Step 3 — Module
  @state() private _availableModules: SmartIrrigationModule[] = [];
  @state() private _selectedModuleIndex = 0;
  @state() private _moduleConfig: Record<string, unknown> = {};
  private _savedModuleId: number | undefined;

  // Step 4 — Mapping
  @state() private _mappingName = "My Sensor Group";
  @state() private _tempSource: string = MAPPING_CONF_SOURCE_WEATHER_SERVICE;
  @state() private _humiditySource: string =
    MAPPING_CONF_SOURCE_WEATHER_SERVICE;
  @state() private _precipSource: string = MAPPING_CONF_SOURCE_WEATHER_SERVICE;
  private _savedMappingId: number | undefined;

  // Step 5 — Zone
  @state() private _zoneName = "My Zone";
  @state() private _zoneSize = "";
  @state() private _zoneThroughput = "";
  @state() private _zoneEntity = "";

  // Done step — offer a default daily schedule (the biggest first-run cliff: a
  // fully-configured system never waters until a schedule exists).
  @state() private _scheduleTime = "06:00";
  @state() private _scheduleCreated = false;
  @state() private _creatingSchedule = false;

  async connectedCallback() {
    super.connectedCallback();
    await this._loadInitialData();
  }

  private async _loadInitialData() {
    if (!this.hass) return;
    try {
      const [allModules, weatherCfg, siCfg] = await Promise.all([
        fetchAllModules(this.hass),
        fetchWeatherConfig(this.hass),
        fetchConfig(this.hass),
      ]);
      this._availableModules = allModules;
      this._weatherConfig = weatherCfg;
      this._siConfig = siCfg;
      this._useWeather = weatherCfg.use_weather_service;
      this._weatherService =
        weatherCfg.weather_service ?? CONF_WEATHER_SERVICE_OPENMETEO;
    } catch (e) {
      console.error("Wizard: failed to load initial data", e);
      this._error = extractErrorMessage(e);
    }
    this.requestUpdate();
  }

  private _close() {
    this.dispatchEvent(
      new CustomEvent("wizard-close", { bubbles: true, composed: true }),
    );
  }

  private _navigate(page: "zones" | "setup") {
    this.dispatchEvent(
      new CustomEvent("wizard-navigate", {
        detail: { page },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private async _next() {
    this._error = "";
    try {
      this._saving = true;
      switch (this._step) {
        case WizardStep.Welcome:
          this._step = WizardStep.Weather;
          break;
        case WizardStep.Weather:
          await this._saveWeather();
          this._step = WizardStep.Module;
          break;
        case WizardStep.Module:
          await this._saveModule();
          this._step = WizardStep.Mapping;
          break;
        case WizardStep.Mapping:
          await this._saveMapping();
          this._step = WizardStep.Zone;
          break;
        case WizardStep.Zone:
          await this._saveZone();
          this._step = WizardStep.Done;
          break;
        case WizardStep.Done:
          this._close();
          break;
      }
    } catch (e: unknown) {
      this._error = e instanceof Error ? e.message : String(e);
    } finally {
      this._saving = false;
      this.requestUpdate();
    }
  }

  private _back() {
    if (this._step > WizardStep.Welcome) {
      this._step = (this._step - 1) as WizardStep;
      this._error = "";
    }
  }

  // Only the Weather step is genuinely optional (a setup can rely on sensors
  // or static values instead). Module, Sensor Group and Zone are required —
  // skipping them produces a zone that can never calculate, so they are not
  // skippable. See UX review C2.
  private get _canSkipCurrentStep(): boolean {
    return this._step === WizardStep.Weather;
  }

  private _skipStep() {
    if (this._canSkipCurrentStep && this._step < WizardStep.Done) {
      this._step = (this._step + 1) as WizardStep;
      this._error = "";
    }
  }

  // ---- save helpers ----

  private async _saveWeather() {
    await saveWeatherConfig(
      this.hass,
      this._useWeather,
      this._useWeather ? this._weatherService : null,
      this._apiKey || null,
    );
  }

  /**
   * Resolve the id of an entry the wizard just created. The POST endpoint
   * returns it directly; if an older backend omits it, fall back to fetching
   * the list and taking the highest id (the wizard only ever *creates*, so the
   * newest entry is the one we just saved).
   */
  private async _resolveSavedId(
    result: SaveResult,
    fetcher: () => Promise<{ id?: number }[]>,
  ): Promise<number | undefined> {
    if (typeof result?.id === "number") return result.id;
    try {
      const items = await fetcher();
      const ids = items
        .map((i) => i.id)
        .filter((id): id is number => typeof id === "number");
      return ids.length ? Math.max(...ids) : undefined;
    } catch {
      return undefined;
    }
  }

  private async _saveModule() {
    if (this._availableModules.length === 0) {
      throw new Error(
        "No calculation module is available to configure. Cannot continue.",
      );
    }
    const template = this._availableModules[this._selectedModuleIndex];
    const result = await saveModule(this.hass, {
      name: template.name,
      description: template.description,
      config: { ...template.config, ...this._moduleConfig },
      schema: template.schema,
    });
    this._savedModuleId = await this._resolveSavedId(result, () =>
      fetchModules(this.hass),
    );
    if (this._savedModuleId === undefined) {
      throw new Error(
        "The calculation module was saved but could not be linked. Please try again.",
      );
    }
  }

  private async _saveMapping() {
    const defaultSource = this._useWeather
      ? MAPPING_CONF_SOURCE_WEATHER_SERVICE
      : MAPPING_CONF_SOURCE_NONE;

    const mappings: Record<string, Record<string, string>> = {
      [MAPPING_TEMPERATURE]: { [MAPPING_CONF_SOURCE]: this._tempSource },
      [MAPPING_HUMIDITY]: { [MAPPING_CONF_SOURCE]: this._humiditySource },
      [MAPPING_PRECIPITATION]: { [MAPPING_CONF_SOURCE]: this._precipSource },
    };

    // Fill remaining parameters with default source
    const allParams = [
      "Dewpoint",
      "Evapotranspiration",
      "Maximum Temperature",
      "Minimum Temperature",
      "Current Precipitation",
      "Pressure",
      "Solar Radiation",
      "Windspeed",
    ];
    for (const param of allParams) {
      mappings[param] = { [MAPPING_CONF_SOURCE]: defaultSource };
    }

    const result = await saveMapping(this.hass, {
      name: this._mappingName,
      mappings,
    });
    this._savedMappingId = await this._resolveSavedId(result, () =>
      fetchMappings(this.hass),
    );
    if (this._savedMappingId === undefined) {
      throw new Error(
        "The sensor group was saved but could not be linked. Please try again.",
      );
    }
  }

  private async _saveZone() {
    if (!this._zoneName.trim()) throw new Error("Zone name is required");
    const size = parseFloat(this._zoneSize);
    const throughput = parseFloat(this._zoneThroughput);
    if (!(size > 0)) {
      throw new Error("Zone size must be greater than 0.");
    }
    if (!(throughput > 0)) {
      throw new Error(
        "Throughput must be greater than 0 (zones can't water otherwise).",
      );
    }
    await saveZone(this.hass, {
      name: this._zoneName.trim(),
      size,
      throughput,
      state: SmartIrrigationZoneState.Automatic,
      duration: 0,
      bucket: 0,
      delta: 0,
      explanation: "",
      multiplier: 1,
      module: this._savedModuleId,
      mapping: this._savedMappingId,
      lead_time: 0,
      linked_entity: this._zoneEntity || undefined,
    });
  }

  /**
   * Create a daily irrigate schedule covering all zones at the chosen time.
   * Mirrors the shape produced by the Schedules view's emptySchedule() so the
   * entry is identical to a hand-made one.
   */
  private async _createDefaultSchedule() {
    if (this._scheduleCreated || this._creatingSchedule) return;
    this._error = "";
    this._creatingSchedule = true;
    try {
      const lang = this.hass?.language ?? "en";
      await saveSchedule(this.hass, {
        name: localize("wizard.steps.done.schedule_name", lang) || "Daily",
        type: "daily",
        enabled: true,
        time: this._scheduleTime || "06:00",
        action: "irrigate",
        zones: "all",
      });
      this._scheduleCreated = true;
    } catch (e: unknown) {
      this._error = e instanceof Error ? e.message : String(e);
    } finally {
      this._creatingSchedule = false;
      this.requestUpdate();
    }
  }

  // ---- render ----

  render() {
    const lang = this.hass?.language ?? "en";
    return html`
      <div class="wizard-overlay" @click="${this._onOverlayClick}">
        <div
          class="wizard-dialog"
          @click="${(e: Event) => e.stopPropagation()}"
        >
          <div class="wizard-header">
            <span class="wizard-title">${localize("wizard.title", lang)}</span>
            <button
              class="wizard-close-btn"
              @click="${this._close}"
              title="${localize("wizard.close", lang)}"
              aria-label="${localize("wizard.close", lang)}"
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>
          ${this._step !== WizardStep.Welcome && this._step !== WizardStep.Done
            ? html`<div class="wizard-stepper">${this._renderStepper()}</div>`
            : ""}
          <div class="wizard-body">
            ${this._renderStep(lang)}
            ${this._error
              ? html`<div class="wizard-error">${this._error}</div>`
              : ""}
          </div>
          <div class="wizard-footer">${this._renderFooter(lang)}</div>
          ${this._confirmClose
            ? html`
                <div class="wizard-confirm-close">
                  <div class="wizard-confirm-box">
                    <p>${localize("wizard.confirm_close.body", lang)}</p>
                    <div class="wizard-confirm-actions">
                      <button
                        class="wizard-btn secondary"
                        @click="${() => {
                          this._confirmClose = false;
                        }}"
                      >
                        ${localize("wizard.confirm_close.keep", lang)}
                      </button>
                      <button
                        class="wizard-btn primary"
                        @click="${() => {
                          this._confirmClose = false;
                          this._close();
                        }}"
                      >
                        ${localize("wizard.confirm_close.close", lang)}
                      </button>
                    </div>
                  </div>
                </div>
              `
            : ""}
        </div>
      </div>
    `;
  }

  private _onOverlayClick(e: Event) {
    if (e.target !== e.currentTarget) return;
    // Mid-flow, confirm before discarding the in-progress setup. Steps save as
    // they go, but an accidental backdrop click shouldn't drop the user out.
    if (this._step > WizardStep.Welcome && this._step < WizardStep.Done) {
      this._confirmClose = true;
    } else {
      this._close();
    }
  }

  private _renderStepper(): TemplateResult {
    const lang = this.hass?.language ?? "en";
    const stepLabels = [
      localize("wizard.stepper.weather", lang),
      localize("wizard.stepper.module", lang),
      localize("wizard.stepper.mapping", lang),
      localize("wizard.stepper.zone", lang),
    ];
    return html`
      ${stepLabels.map((label, i) => {
        const stepNum = i + 1;
        const active = this._step === stepNum;
        const done = this._step > stepNum;
        return html`
          <div
            class="stepper-step ${active ? "active" : ""} ${done ? "done" : ""}"
          >
            <div class="stepper-circle">${done ? "✓" : stepNum}</div>
            <span class="stepper-label">${label}</span>
          </div>
          ${i < stepLabels.length - 1
            ? html`<div class="stepper-line ${done ? "done" : ""}"></div>`
            : ""}
        `;
      })}
    `;
  }

  private _renderStep(lang: string): TemplateResult {
    switch (this._step) {
      case WizardStep.Welcome:
        return this._renderWelcome(lang);
      case WizardStep.Weather:
        return this._renderWeather(lang);
      case WizardStep.Module:
        return this._renderModule(lang);
      case WizardStep.Mapping:
        return this._renderMapping(lang);
      case WizardStep.Zone:
        return this._renderZone(lang);
      case WizardStep.Done:
        return this._renderDone(lang);
      default:
        return html``;
    }
  }

  private _renderFooter(lang: string): TemplateResult {
    if (this._step === WizardStep.Done) return html``;
    return html`
      <div class="footer-left">
        ${this._step > WizardStep.Welcome
          ? html`<button
              class="wizard-btn secondary"
              @click="${this._back}"
              ?disabled="${this._saving}"
            >
              ${localize("wizard.back", lang)}
            </button>`
          : ""}
        ${this._canSkipCurrentStep
          ? html`<button
              class="wizard-btn ghost"
              @click="${this._skipStep}"
              ?disabled="${this._saving}"
            >
              ${localize("wizard.skip_step", lang)}
            </button>`
          : ""}
      </div>
      <button
        class="wizard-btn primary"
        @click="${this._next}"
        ?disabled="${this._saving}"
      >
        ${this._saving
          ? localize("common.saving-messages.saving", lang)
          : this._step === WizardStep.Welcome
            ? localize("wizard.next", lang)
            : this._step < WizardStep.Zone
              ? localize("wizard.next", lang)
              : localize("wizard.finish", lang)}
      </button>
    `;
  }

  // ---- step renders ----

  private _renderWelcome(lang: string): TemplateResult {
    return html`
      <h2 class="step-title">
        ${localize("wizard.steps.welcome.title", lang)}
      </h2>
      <p class="step-desc">${localize("wizard.steps.welcome.intro", lang)}</p>
      <ul class="step-list">
        <li>① ${localize("wizard.steps.welcome.step1_label", lang)}</li>
        <li>② ${localize("wizard.steps.welcome.step2_label", lang)}</li>
        <li>③ ${localize("wizard.steps.welcome.step3_label", lang)}</li>
        <li>④ ${localize("wizard.steps.welcome.step4_label", lang)}</li>
      </ul>
      <p class="step-tip">${localize("wizard.steps.welcome.tip", lang)}</p>
    `;
  }

  private _renderWeather(lang: string): TemplateResult {
    return html`
      <h2 class="step-title">
        ${localize("wizard.steps.weather.title", lang)}
      </h2>
      <p class="step-desc">
        ${localize("wizard.steps.weather.description", lang)}
      </p>

      <si-weather-source-config
        .hass="${this.hass}"
        .useWeather="${this._useWeather}"
        .service="${this._weatherService}"
        .apiKey="${this._apiKey}"
        .weatherConfig="${this._weatherConfig}"
        @useweather-changed="${(e: CustomEvent) => {
          this._useWeather = e.detail.value;
        }}"
        @service-changed="${(e: CustomEvent) => {
          this._weatherService = e.detail.value;
        }}"
        @apikey-changed="${(e: CustomEvent) => {
          this._apiKey = e.detail.value;
        }}"
      ></si-weather-source-config>
    `;
  }

  private _renderModule(lang: string): TemplateResult {
    if (this._availableModules.length === 0) {
      return html`
        <h2 class="step-title">
          ${localize("wizard.steps.module.title", lang)}
        </h2>
        <p class="step-desc">
          ${localize("wizard.steps.module.no_modules", lang)}
        </p>
      `;
    }
    const selected = this._availableModules[this._selectedModuleIndex];
    return html`
      <h2 class="step-title">${localize("wizard.steps.module.title", lang)}</h2>
      <p class="step-desc">
        ${localize("wizard.steps.module.description", lang)}
      </p>

      <si-field
        label="${localize("wizard.steps.module.pick_label", lang)}"
        required
      >
        <select
          class="wizard-input"
          @change="${(e: Event) => {
            this._selectedModuleIndex = parseInt(
              (e.target as HTMLSelectElement).value,
            );
            this._moduleConfig = {};
          }}"
        >
          ${this._availableModules.map(
            (m, i) => html`
              <option
                value="${i}"
                ?selected="${i === this._selectedModuleIndex}"
              >
                ${m.name}
              </option>
            `,
          )}
        </select>
      </si-field>

      ${selected?.description
        ? html`<p class="module-desc">${selected.description}</p>`
        : ""}
      ${selected?.schema &&
      Array.isArray(selected.schema) &&
      selected.schema.length > 0
        ? html`
            <div class="schema-fields">
              ${(selected.schema as any[]).map((def: any) =>
                this._renderModuleField(def.name, def),
              )}
            </div>
          `
        : ""}
    `;
  }

  private _renderModuleField(key: string, def: any): TemplateResult {
    // Convert snake_case key to Title Case label
    const label = key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
    const value = this._moduleConfig[key] ?? def.default ?? "";
    const help: string | undefined = def.description;

    if (def.type === "boolean") {
      return html`
        <si-field label="${label}" help="${help ?? ""}">
          <ha-switch
            .checked="${Boolean(value)}"
            @change="${(e: Event) => {
              this._moduleConfig = {
                ...this._moduleConfig,
                [key]: (e.target as HTMLInputElement).checked,
              };
            }}"
          ></ha-switch>
        </si-field>
      `;
    }
    if (def.type === "select" && def.options) {
      // options come as [[value, label], ...] tuples from voluptuous_serialize
      return html`
        <si-field label="${label}" help="${help ?? ""}">
          <select
            class="wizard-input"
            @change="${(e: Event) => {
              this._moduleConfig = {
                ...this._moduleConfig,
                [key]: (e.target as HTMLSelectElement).value,
              };
            }}"
          >
            ${(def.options as [string, string][]).map(
              ([optVal, optLabel]) =>
                html`<option
                  value="${optVal}"
                  ?selected="${optVal === String(value)}"
                >
                  ${optLabel}
                </option>`,
            )}
          </select>
        </si-field>
      `;
    }
    return html`
      <si-field label="${label}" help="${help ?? ""}">
        <input
          type="${def.type === "float" || def.type === "integer"
            ? "number"
            : "text"}"
          class="wizard-input"
          step="${def.type === "float" ? "0.01" : "1"}"
          .value="${String(value)}"
          @input="${(e: Event) => {
            const raw = (e.target as HTMLInputElement).value;
            const parsed =
              def.type === "float"
                ? parseFloat(raw)
                : def.type === "integer"
                  ? parseInt(raw)
                  : raw;
            this._moduleConfig = { ...this._moduleConfig, [key]: parsed };
          }}"
        />
      </si-field>
    `;
  }

  private _renderMapping(lang: string): TemplateResult {
    const sourceOpts = [
      {
        value: MAPPING_CONF_SOURCE_WEATHER_SERVICE,
        label: localize("wizard.steps.mapping.use_weather_service", lang),
      },
      {
        value: "sensor",
        label: localize("wizard.steps.mapping.use_sensor", lang),
      },
      {
        value: "static",
        label: localize("wizard.steps.mapping.use_static", lang),
      },
      {
        value: MAPPING_CONF_SOURCE_NONE,
        label: localize("wizard.steps.mapping.use_none", lang),
      },
    ];

    const renderSourceSelect = (
      paramLabel: string,
      value: string,
      onChange: (v: string) => void,
    ) => html`
      <si-field
        label="${localize(
          "wizard.steps.mapping.source_label",
          lang,
        )} ${paramLabel}"
      >
        <select
          class="wizard-input"
          @change="${(e: Event) =>
            onChange((e.target as HTMLSelectElement).value)}"
        >
          ${sourceOpts.map(
            (o) =>
              html`<option value="${o.value}" ?selected="${o.value === value}">
                ${o.label}
              </option>`,
          )}
        </select>
      </si-field>
    `;

    return html`
      <h2 class="step-title">
        ${localize("wizard.steps.mapping.title", lang)}
      </h2>
      <p class="step-desc">
        ${localize("wizard.steps.mapping.description", lang)}
      </p>

      <si-field
        label="${localize("wizard.steps.mapping.name_label", lang)}"
        required
      >
        <input
          type="text"
          class="wizard-input"
          .value="${this._mappingName}"
          @input="${(e: Event) => {
            this._mappingName = (e.target as HTMLInputElement).value;
          }}"
        />
      </si-field>

      ${renderSourceSelect(
        localize("panels.mappings.cards.mapping.items.temperature", lang) ||
          "Temperature",
        this._tempSource,
        (v) => {
          this._tempSource = v;
          this.requestUpdate();
        },
      )}
      ${renderSourceSelect(
        localize("panels.mappings.cards.mapping.items.humidity", lang) ||
          "Humidity",
        this._humiditySource,
        (v) => {
          this._humiditySource = v;
          this.requestUpdate();
        },
      )}
      ${renderSourceSelect(
        localize("panels.mappings.cards.mapping.items.precipitation", lang) ||
          "Precipitation",
        this._precipSource,
        (v) => {
          this._precipSource = v;
          this.requestUpdate();
        },
      )}

      <p class="step-tip">
        ${localize("wizard.steps.mapping.description", lang)}
      </p>
    `;
  }

  private _renderZone(lang: string): TemplateResult {
    const isMetric = this._siConfig?.units !== "imperial";
    return html`
      <h2 class="step-title">${localize("wizard.steps.zone.title", lang)}</h2>
      <p class="step-desc">
        ${localize("wizard.steps.zone.description", lang)}
      </p>

      <si-zone-form
        .hass="${this.hass}"
        .metric="${isMetric}"
        .name="${this._zoneName}"
        .size="${this._zoneSize}"
        .throughput="${this._zoneThroughput}"
        .linkedEntity="${this._zoneEntity}"
        showEntity
        @name-changed="${(e: CustomEvent) => {
          this._zoneName = e.detail.value;
        }}"
        @size-changed="${(e: CustomEvent) => {
          this._zoneSize = e.detail.value;
        }}"
        @throughput-changed="${(e: CustomEvent) => {
          this._zoneThroughput = e.detail.value;
        }}"
        @entity-changed="${(e: CustomEvent) => {
          this._zoneEntity = e.detail.value;
        }}"
      ></si-zone-form>
    `;
  }

  private _renderDone(lang: string): TemplateResult {
    return html`
      <div class="done-wrapper">
        <div class="done-icon">
          <ha-icon icon="mdi:check-circle"></ha-icon>
        </div>
        <h2 class="step-title">${localize("wizard.steps.done.title", lang)}</h2>
        <p class="step-desc">
          ${localize("wizard.steps.done.description", lang)}
        </p>
        <ul class="step-list">
          <li>${localize("wizard.steps.done.tip1", lang)}</li>
          <li>${localize("wizard.steps.done.tip2", lang)}</li>
          <li>${localize("wizard.steps.done.tip3", lang)}</li>
        </ul>

        <div class="schedule-offer">
          ${this._scheduleCreated
            ? html`
                <div class="schedule-created">
                  <ha-icon icon="mdi:calendar-check"></ha-icon>
                  <span
                    >${localize(
                      "wizard.steps.done.schedule_created",
                      lang,
                    )}</span
                  >
                </div>
              `
            : html`
                <p class="schedule-offer-title">
                  ${localize("wizard.steps.done.schedule_title", lang)}
                </p>
                <p class="schedule-offer-desc">
                  ${localize("wizard.steps.done.schedule_desc", lang)}
                </p>
                <div class="schedule-offer-row">
                  <input
                    type="time"
                    class="wizard-input"
                    .value="${this._scheduleTime}"
                    @change="${(e: Event) => {
                      this._scheduleTime = (e.target as HTMLInputElement).value;
                    }}"
                  />
                  <button
                    class="wizard-btn primary"
                    @click="${this._createDefaultSchedule}"
                    ?disabled="${this._creatingSchedule}"
                  >
                    ${this._creatingSchedule
                      ? localize("common.saving-messages.saving", lang)
                      : localize("wizard.steps.done.schedule_create", lang)}
                  </button>
                </div>
              `}
        </div>

        <div class="done-actions">
          <button
            class="wizard-btn primary"
            @click="${() => {
              this._close();
              this._navigate("zones");
            }}"
          >
            ${localize("wizard.steps.done.go_zones", lang)}
          </button>
          <button
            class="wizard-btn secondary"
            @click="${() => {
              this._close();
              this._navigate("setup");
            }}"
          >
            ${localize("wizard.steps.done.go_setup", lang)}
          </button>
        </div>
      </div>
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      :host {
        display: block;
      }

      /* Full-screen overlay */
      .wizard-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.55);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 16px;
        box-sizing: border-box;
      }

      /* Dialog box */
      .wizard-dialog {
        position: relative;
        background: var(--card-background-color);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
        max-height: 90vh;
        width: 100%;
        max-width: 540px;
        overflow: hidden;
      }

      /* Header */
      .wizard-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid var(--divider-color);
        flex-shrink: 0;
      }

      .wizard-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .wizard-close-btn {
        background: none;
        border: none;
        cursor: pointer;
        color: var(--secondary-text-color);
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        border-radius: 4px;
        transition: background 0.15s;
        --mdc-icon-size: 20px;
      }

      .wizard-close-btn:hover {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
      }

      /* Confirm-before-close overlay (UX N4) */
      .wizard-confirm-close {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.45);
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        padding: 16px;
        box-sizing: border-box;
      }

      .wizard-confirm-box {
        background: var(--card-background-color);
        border-radius: 10px;
        padding: 20px;
        max-width: 360px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      }

      .wizard-confirm-box p {
        margin: 0 0 16px;
        font-size: 0.9rem;
        color: var(--primary-text-color);
        line-height: 1.5;
      }

      .wizard-confirm-actions {
        display: flex;
        gap: 12px;
        justify-content: flex-end;
      }

      /* Stepper */
      .wizard-stepper {
        display: flex;
        align-items: center;
        padding: 12px 20px;
        border-bottom: 1px solid var(--divider-color);
        flex-shrink: 0;
        overflow-x: auto;
      }

      .stepper-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        flex-shrink: 0;
      }

      .stepper-circle {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        border: 2px solid var(--divider-color);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--secondary-text-color);
        background: var(--card-background-color);
        transition: all 0.2s;
      }

      .stepper-step.active .stepper-circle {
        border-color: var(--primary-color);
        color: var(--primary-color);
      }

      .stepper-step.done .stepper-circle {
        border-color: var(--primary-color);
        background: var(--primary-color);
        color: white;
      }

      .stepper-label {
        font-size: 0.68rem;
        color: var(--secondary-text-color);
        white-space: nowrap;
      }

      .stepper-step.active .stepper-label {
        color: var(--primary-color);
        font-weight: 600;
      }

      .stepper-line {
        flex: 1;
        height: 2px;
        background: var(--divider-color);
        min-width: 16px;
        margin-bottom: 18px;
        transition: background 0.2s;
      }

      .stepper-line.done {
        background: var(--primary-color);
      }

      /* Body */
      .wizard-body {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
      }

      .step-title {
        margin: 0 0 8px;
        font-size: 1.05rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .step-desc {
        margin: 0 0 16px;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        line-height: 1.5;
      }

      .step-list {
        margin: 0 0 16px;
        padding-left: 20px;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        line-height: 1.8;
      }

      .step-tip {
        font-size: 0.8rem;
        color: var(--secondary-text-color);
        font-style: italic;
        margin: 8px 0 0;
      }

      .module-desc {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-radius: 4px;
        padding: 8px 12px;
        margin: 8px 0;
        line-height: 1.45;
      }

      .schema-fields {
        margin-top: 8px;
      }

      /* Common input */
      .wizard-input {
        width: 100%;
        background: var(--input-fill-color, var(--secondary-background-color));
        border: 1px solid var(--input-ink-color, var(--secondary-text-color));
        border-radius: 4px;
        color: var(--primary-text-color);
        padding: 6px 10px;
        font-family: inherit;
        font-size: 0.9375rem;
        box-sizing: border-box;
        height: 36px;
      }

      .wizard-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }

      .wizard-input.flex1 {
        flex: 1;
      }

      select.wizard-input {
        cursor: pointer;
      }

      /* API key row */
      .api-row {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 4px;
      }

      .api-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 4px;
      }

      .api-badge.configured {
        background: rgba(76, 175, 80, 0.15);
        color: #2e7d32;
      }

      .test-result {
        font-size: 0.83rem;
        font-weight: 500;
        margin-top: 6px;
        padding: 5px 10px;
        border-radius: 4px;
      }

      .test-result.success {
        background: rgba(76, 175, 80, 0.12);
        color: #2e7d32;
      }

      .test-result.error {
        background: rgba(176, 0, 32, 0.1);
        color: var(--error-color, #b00020);
      }

      .info-note {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-radius: 4px;
        padding: 8px 12px;
        margin-top: 8px;
      }

      /* Done step */
      .done-wrapper {
        text-align: center;
        padding: 8px 0;
      }

      .done-icon {
        color: #4caf50;
        margin-bottom: 12px;
        --mdc-icon-size: 56px;
      }

      .done-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 24px;
      }

      /* Default-schedule offer on the Done step */
      .schedule-offer {
        text-align: left;
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 14px 16px;
        margin-top: 8px;
      }

      .schedule-offer-title {
        margin: 0 0 4px;
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--primary-text-color);
      }

      .schedule-offer-desc {
        margin: 0 0 12px;
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        line-height: 1.45;
      }

      .schedule-offer-row {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
      }

      .schedule-offer-row .wizard-input {
        width: auto;
        flex: 0 0 auto;
      }

      .schedule-created {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #2e7d32;
        font-weight: 500;
        font-size: 0.9rem;
      }

      .schedule-created ha-icon {
        --mdc-icon-size: 22px;
      }

      /* Error */
      .wizard-error {
        background: rgba(176, 0, 32, 0.1);
        color: var(--error-color, #b00020);
        border-radius: 4px;
        padding: 8px 12px;
        font-size: 0.875rem;
        margin-top: 12px;
      }

      /* Footer */
      .wizard-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        border-top: 1px solid var(--divider-color);
        flex-shrink: 0;
        gap: 8px;
      }

      .footer-left {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      /* Buttons */
      .wizard-btn {
        background: var(--primary-color);
        border: none;
        border-radius: 4px;
        color: var(--text-primary-color, white);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        padding: 8px 18px;
        text-transform: uppercase;
        transition: opacity 0.15s;
        white-space: nowrap;
      }

      .wizard-btn:hover {
        opacity: 0.9;
      }

      .wizard-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }

      .wizard-btn.secondary {
        background: transparent;
        border: 1px solid var(--primary-color);
        color: var(--primary-color);
      }

      .wizard-btn.secondary:hover {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
        opacity: 1;
      }

      .wizard-btn.ghost {
        background: transparent;
        border: none;
        color: var(--secondary-text-color);
        font-size: 0.8rem;
        text-transform: none;
        letter-spacing: 0;
        padding: 8px 10px;
      }

      .wizard-btn.ghost:hover {
        color: var(--primary-text-color);
        background: var(--secondary-background-color);
        opacity: 1;
      }
    `;
  }
}
