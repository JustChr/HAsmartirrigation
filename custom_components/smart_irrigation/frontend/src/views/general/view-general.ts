import { CSSResultGroup, LitElement, css, html, TemplateResult } from "lit";
import { live } from "lit/directives/live.js";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";
import { UnsubscribeFunc } from "home-assistant-js-websocket";

import {
  fetchConfig,
  saveConfig,
  fetchWeatherConfig,
  saveWeatherConfig,
  testWeatherConfig,
  WeatherConfig,
} from "../../data/websockets";
import "../../components/si-field";
import { SubscribeMixin } from "../../subscribe-mixin";
import { localize } from "../../../localize/localize";
import { output_unit, pick, handleError } from "../../helpers";
import { loadHaForm } from "../../load-ha-elements";
import { SmartIrrigationConfig } from "../../types";
import { globalStyle } from "../../styles/global-style";
import { Path } from "../../common/navigation";
import {
  AUTO_UPDATE_SCHEDULE_DAILY,
  AUTO_UPDATE_SCHEDULE_HOURLY,
  AUTO_UPDATE_SCHEDULE_MINUTELY,
  CONF_AUTO_CALC_ENABLED,
  CONF_AUTO_CLEAR_ENABLED,
  CONF_AUTO_UPDATE_ENABLED,
  CONF_AUTO_UPDATE_INTERVAL,
  CONF_AUTO_UPDATE_SCHEDULE,
  CONF_AUTO_UPDATE_TIME,
  CONF_CALC_TIME,
  CONF_CLEAR_TIME,
  CONF_CONTINUOUS_UPDATES,
  CONF_SENSOR_DEBOUNCE,
  CONF_PRECIPITATION_THRESHOLD_MM,
  CONF_MANUAL_COORDINATES_ENABLED,
  CONF_MANUAL_LATITUDE,
  CONF_MANUAL_LONGITUDE,
  CONF_MANUAL_ELEVATION,
  CONF_DAYS_BETWEEN_IRRIGATION,
  CONF_ZONE_SEQUENCING,
  CONF_ZONE_SEQUENCING_SEQUENTIAL,
  CONF_ZONE_SEQUENCING_PARALLEL,
  CONF_ZONE_SEQUENCING_ROTATING,
  CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION,
  CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME,
  CONF_WEATHER_SERVICE_OWM,
  CONF_WEATHER_SERVICE_PW,
  CONF_WEATHER_SERVICE_OPENMETEO,
  DOMAIN,
} from "../../const";

@customElement("smart-irrigation-view-general")
export class SmartIrrigationViewGeneral extends SubscribeMixin(LitElement) {
  hass?: HomeAssistant;
  @property() narrow!: boolean;
  @property() path!: Path;

  @property() data?: Partial<SmartIrrigationConfig>;
  @property() config?: SmartIrrigationConfig;

  @property({ type: Boolean })
  private isLoading = true;

  @property({ type: Boolean })
  private isSaving = false;

  @property()
  private _weatherConfig: WeatherConfig | null = null;

  @property()
  private _weatherService: string | null = null;

  @property({ type: Boolean })
  private _useWeatherService = false;

  @property()
  private _newApiKey = "";

  @property({ type: Boolean })
  private _weatherSaving = false;

  @state() private _testingApi = false;
  @state() private _testResult: { success: boolean; error?: string } | null =
    null;
  private _testResultTimer: number | null = null;

  private _updateScheduled = false;
  private _scheduleUpdate() {
    if (this._updateScheduled) return;
    this._updateScheduled = true;
    requestAnimationFrame(() => {
      this._updateScheduled = false;
      this.requestUpdate();
    });
  }

  private debouncedSave = (() => {
    let timeoutId: number | null = null;
    return (changes: Partial<SmartIrrigationConfig>) => {
      if (timeoutId) clearTimeout(timeoutId);
      timeoutId = window.setTimeout(() => {
        this.saveData(changes);
        timeoutId = null;
      }, 500);
    };
  })();

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
    this.isLoading = true;
    this._scheduleUpdate();
    try {
      const [configResult, weatherConfigResult] = await Promise.all([
        fetchConfig(this.hass),
        fetchWeatherConfig(this.hass),
      ]);
      this.config = configResult;
      this._weatherConfig = weatherConfigResult;
      this._useWeatherService = weatherConfigResult.use_weather_service;
      this._weatherService =
        weatherConfigResult.weather_service ?? CONF_WEATHER_SERVICE_OPENMETEO;
      this.data = pick(this.config, [
        CONF_CALC_TIME,
        CONF_AUTO_CALC_ENABLED,
        CONF_AUTO_UPDATE_ENABLED,
        CONF_AUTO_UPDATE_SCHEDULE,
        CONF_AUTO_UPDATE_TIME,
        CONF_AUTO_UPDATE_INTERVAL,
        CONF_AUTO_CLEAR_ENABLED,
        CONF_CLEAR_TIME,
        CONF_CONTINUOUS_UPDATES,
        CONF_SENSOR_DEBOUNCE,
        CONF_MANUAL_COORDINATES_ENABLED,
        CONF_MANUAL_LATITUDE,
        CONF_MANUAL_LONGITUDE,
        CONF_MANUAL_ELEVATION,
        CONF_DAYS_BETWEEN_IRRIGATION,
      ]);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      this.isLoading = false;
      this._scheduleUpdate();
    }
  }

  firstUpdated() {
    loadHaForm()
      .then(() => this._scheduleUpdate())
      .catch((error) => {
        console.error("Failed to load HA form:", error);
        this._scheduleUpdate();
      });
  }

  render() {
    if (!this.hass || !this.config || !this.data) {
      return html`<div class="loading-indicator">
        ${localize(
          "common.loading-messages.configuration",
          this.hass?.language ?? "en",
        )}
      </div>`;
    }
    if (this.isLoading) {
      return html`<div class="loading-indicator">
        ${localize("common.loading-messages.general", this.hass.language)}
      </div>`;
    }
    return html`
      ${this._renderWeatherServiceCard()} ${this._renderAutoUpdateCard()}
      ${this._renderAutoCalcCard()} ${this._renderAutoClearCard()}
      ${this._renderContinuousUpdatesCard()} ${this._renderWeatherSkipCard()}
      ${this._renderCoordinateCard()} ${this._renderDaysBetweenIrrigationCard()}
      ${this._renderZoneSequencingCard()}
    `;
  }

  private async _saveWeatherConfig(): Promise<void> {
    if (!this.hass) return;
    this._weatherSaving = true;
    this._scheduleUpdate();
    try {
      await saveWeatherConfig(
        this.hass,
        this._useWeatherService,
        this._useWeatherService ? this._weatherService : null,
        this._newApiKey || null,
      );
      this._newApiKey = "";
      await this._fetchData();
    } catch (error) {
      console.error("Failed to save weather config:", error);
    } finally {
      this._weatherSaving = false;
      this._scheduleUpdate();
    }
  }

  private async _testWeatherConfig(): Promise<void> {
    if (!this.hass || this._testingApi) return;
    this._testingApi = true;
    this._testResult = null;
    if (this._testResultTimer) {
      clearTimeout(this._testResultTimer);
      this._testResultTimer = null;
    }
    this._scheduleUpdate();
    try {
      const result = await testWeatherConfig(
        this.hass,
        this._weatherService,
        this._newApiKey || null,
      );
      this._testResult = result;
      // Auto-clear after 12 s
      this._testResultTimer = window.setTimeout(() => {
        this._testResult = null;
        this._testResultTimer = null;
        this._scheduleUpdate();
      }, 12000);
    } catch (e) {
      this._testResult = { success: false, error: "unknown" };
    } finally {
      this._testingApi = false;
      this._scheduleUpdate();
    }
  }

  private _renderWeatherServiceCard(): TemplateResult {
    if (!this.hass) return html``;
    const noApiKeyServices = this._weatherConfig?.no_api_key_services ?? [
      CONF_WEATHER_SERVICE_OPENMETEO,
    ];
    const needsApiKey =
      this._useWeatherService &&
      this._weatherService &&
      !noApiKeyServices.includes(this._weatherService);

    return html`
      <ha-card
        header="${localize("weather_service_config.title", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${localize("weather_service_config.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize(
                "weather_service_config.enabled_label",
                this.hass.language,
              )}
            </label>
            <ha-switch
              .checked="${this._useWeatherService}"
              @change="${(e: Event) => {
                this._useWeatherService = (
                  e.target as HTMLInputElement
                ).checked;
              }}"
            ></ha-switch>
          </div>
          ${this._useWeatherService
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "weather_service_config.service_label",
                      this.hass.language,
                    )}
                  </label>
                  <select
                    class="settings-input"
                    .value="${live(
                      this._weatherService || CONF_WEATHER_SERVICE_OPENMETEO,
                    )}"
                    @change="${(e: Event) => {
                      this._weatherService = (
                        e.target as HTMLSelectElement
                      ).value;
                    }}"
                  >
                    <option
                      value="${CONF_WEATHER_SERVICE_OPENMETEO}"
                      ?selected="${(this._weatherService ||
                        CONF_WEATHER_SERVICE_OPENMETEO) ===
                      CONF_WEATHER_SERVICE_OPENMETEO}"
                    >
                      ${localize(
                        "weather_service_config.openmeteo",
                        this.hass.language,
                      )}
                    </option>
                    <option
                      value="${CONF_WEATHER_SERVICE_OWM}"
                      ?selected="${this._weatherService ===
                      CONF_WEATHER_SERVICE_OWM}"
                    >
                      ${localize(
                        "weather_service_config.owm",
                        this.hass.language,
                      )}
                    </option>
                    <option
                      value="${CONF_WEATHER_SERVICE_PW}"
                      ?selected="${this._weatherService ===
                      CONF_WEATHER_SERVICE_PW}"
                    >
                      ${localize(
                        "weather_service_config.pw",
                        this.hass.language,
                      )}
                    </option>
                  </select>
                </div>
                ${needsApiKey
                  ? html`
                      <si-field
                        label="${localize(
                          "weather_service_config.api_key_label",
                          this.hass.language,
                        )}"
                        help="${localize(
                          "weather_service_config.api_key_help",
                          this.hass.language,
                        )}"
                      >
                        <div class="api-key-status">
                          ${(() => {
                            const svc = this._weatherService;
                            const cfg = this._weatherConfig;
                            const hasKey =
                              svc === CONF_WEATHER_SERVICE_OWM
                                ? cfg?.has_owm_api_key
                                : svc === CONF_WEATHER_SERVICE_PW
                                  ? cfg?.has_pw_api_key
                                  : false;
                            return hasKey
                              ? html`<span class="api-key-badge configured"
                                  >${localize(
                                    "weather_service_config.api_key_configured",
                                    this.hass.language,
                                  )}</span
                                >`
                              : html`<span class="api-key-badge missing"
                                  >${localize(
                                    "weather_service_config.api_key_not_configured",
                                    this.hass.language,
                                  )}</span
                                >`;
                          })()}
                        </div>
                        <div class="api-key-row">
                          <input
                            type="password"
                            class="settings-input api-key-input"
                            placeholder="${localize(
                              "weather_service_config.api_key_placeholder",
                              this.hass.language,
                            )}"
                            .value="${this._newApiKey}"
                            @input="${(e: Event) => {
                              this._newApiKey = (
                                e.target as HTMLInputElement
                              ).value;
                              this._testResult = null;
                            }}"
                          />
                          <button
                            class="action-btn secondary test-btn"
                            type="button"
                            ?disabled="${this._testingApi ||
                            (!this._newApiKey &&
                              !(this._weatherService ===
                              CONF_WEATHER_SERVICE_OWM
                                ? this._weatherConfig?.has_owm_api_key
                                : this._weatherService ===
                                    CONF_WEATHER_SERVICE_PW
                                  ? this._weatherConfig?.has_pw_api_key
                                  : false))}"
                            @click="${this._testWeatherConfig}"
                          >
                            ${this._testingApi
                              ? localize(
                                  "weather_service_config.test_button_testing",
                                  this.hass.language,
                                )
                              : localize(
                                  "weather_service_config.test_button",
                                  this.hass.language,
                                )}
                          </button>
                        </div>
                        ${this._testResult !== null
                          ? html`
                              <div
                                class="test-result ${this._testResult.success
                                  ? "success"
                                  : "error"}"
                              >
                                ${this._testResult.success
                                  ? localize(
                                      "weather_service_config.test_success",
                                      this.hass.language,
                                    )
                                  : localize(
                                      "weather_service_config.test_error_" +
                                        (this._testResult.error ?? "unknown"),
                                      this.hass.language,
                                    )}
                              </div>
                            `
                          : ""}
                      </si-field>
                    `
                  : html`
                      <div class="description-text" style="padding: 8px 0;">
                        ${localize(
                          "weather_service_config.no_api_key_needed",
                          this.hass.language,
                        )}
                      </div>
                    `}
              `
            : ""}
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._weatherSaving}"
              @click="${this._saveWeatherConfig}"
            >
              ${this._weatherSaving
                ? localize("common.saving-messages.saving", this.hass.language)
                : localize(
                    "weather_service_config.save_button",
                    this.hass.language,
                  )}
            </button>
          </div>
        </div>
      </ha-card>
    `;
  }

  private _renderAutoUpdateCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card
        header="${localize(
          "panels.general.cards.automatic-update.header",
          this.hass.language,
        )}"
      >
        <div class="card-content description-text">
          ${localize(
            "panels.general.cards.automatic-update.description",
            this.hass.language,
          )}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize(
                "panels.general.cards.automatic-update.labels.auto-update-enabled",
                this.hass.language,
              )}
            </label>
            <ha-switch
              .checked="${this.config.autoupdateenabled}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  autoupdateenabled: (e.target as HTMLInputElement).checked,
                })}"
            ></ha-switch>
          </div>
          ${this.data.autoupdateenabled
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "panels.general.cards.automatic-update.labels.auto-update-interval",
                      this.hass.language,
                    )}
                  </label>
                  <div class="inline-row">
                    <input
                      type="number"
                      class="settings-input shortfield"
                      min="1"
                      step="1"
                      inputmode="numeric"
                      .value="${this.data.autoupdateinterval ?? 1}"
                      @input="${(e: Event) => {
                        const v = parseInt(
                          (e.target as HTMLInputElement).value,
                        );
                        if (!isNaN(v))
                          this.handleConfigChange({ autoupdateinterval: v });
                      }}"
                    />
                    <select
                      class="settings-input"
                      .value="${live(
                        this.data.autoupdateschedule ||
                          AUTO_UPDATE_SCHEDULE_HOURLY,
                      )}"
                      @change="${(e: Event) =>
                        this.handleConfigChange({
                          autoupdateschedule: (e.target as HTMLSelectElement)
                            .value,
                        })}"
                    >
                      <option
                        value="${AUTO_UPDATE_SCHEDULE_MINUTELY}"
                        ?selected="${(this.data.autoupdateschedule ||
                          AUTO_UPDATE_SCHEDULE_HOURLY) ===
                        AUTO_UPDATE_SCHEDULE_MINUTELY}"
                      >
                        ${localize(
                          "panels.general.cards.automatic-update.options.minutes",
                          this.hass.language,
                        )}
                      </option>
                      <option
                        value="${AUTO_UPDATE_SCHEDULE_HOURLY}"
                        ?selected="${(this.data.autoupdateschedule ||
                          AUTO_UPDATE_SCHEDULE_HOURLY) ===
                        AUTO_UPDATE_SCHEDULE_HOURLY}"
                      >
                        ${localize(
                          "panels.general.cards.automatic-update.options.hours",
                          this.hass.language,
                        )}
                      </option>
                      <option
                        value="${AUTO_UPDATE_SCHEDULE_DAILY}"
                        ?selected="${this.data.autoupdateschedule ===
                        AUTO_UPDATE_SCHEDULE_DAILY}"
                      >
                        ${localize(
                          "panels.general.cards.automatic-update.options.days",
                          this.hass.language,
                        )}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="setting-row">
                  <label>
                    ${localize(
                      "panels.general.cards.automatic-update.labels.auto-update-delay",
                      this.hass.language,
                    )}
                    (s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="1"
                    inputmode="numeric"
                    .value="${this.config.autoupdatedelay ?? 0}"
                    @input="${(e: Event) => {
                      const v = parseInt((e.target as HTMLInputElement).value);
                      if (!isNaN(v))
                        this.handleConfigChange({ autoupdatedelay: v });
                    }}"
                  />
                </div>
              `
            : ""}
        </div>
      </ha-card>
    `;
  }

  private _renderAutoCalcCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card
        header="${localize(
          "panels.general.cards.automatic-duration-calculation.header",
          this.hass.language,
        )}"
      >
        <div class="card-content description-text">
          ${localize(
            "panels.general.cards.automatic-duration-calculation.description",
            this.hass.language,
          )}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize(
                "panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled",
                this.hass.language,
              )}
            </label>
            <ha-switch
              .checked="${this.config.autocalcenabled}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  autocalcenabled: (e.target as HTMLInputElement).checked,
                })}"
            ></ha-switch>
          </div>
          ${this.data.autocalcenabled
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "panels.general.cards.automatic-duration-calculation.labels.calc-time",
                      this.hass.language,
                    )}
                  </label>
                  <input
                    type="text"
                    class="settings-input shortfield"
                    .value="${this.config.calctime}"
                    @input="${(e: Event) =>
                      this.handleConfigChange({
                        calctime: (e.target as HTMLInputElement).value,
                      })}"
                  />
                </div>
              `
            : ""}
        </div>
      </ha-card>
    `;
  }

  private _renderAutoClearCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card
        header="${localize(
          "panels.general.cards.automatic-clear.header",
          this.hass.language,
        )}"
      >
        <div class="card-content description-text">
          ${localize(
            "panels.general.cards.automatic-clear.description",
            this.hass.language,
          )}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize(
                "panels.general.cards.automatic-clear.labels.automatic-clear-enabled",
                this.hass.language,
              )}
            </label>
            <ha-switch
              .checked="${this.config.autoclearenabled}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  autoclearenabled: (e.target as HTMLInputElement).checked,
                })}"
            ></ha-switch>
          </div>
          ${this.data.autoclearenabled
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "panels.general.cards.automatic-clear.labels.automatic-clear-time",
                      this.hass.language,
                    )}
                  </label>
                  <input
                    type="text"
                    class="settings-input shortfield"
                    .value="${this.config.cleardatatime}"
                    @input="${(e: Event) =>
                      this.handleConfigChange({
                        cleardatatime: (e.target as HTMLInputElement).value,
                      })}"
                  />
                </div>
              `
            : ""}
        </div>
      </ha-card>
    `;
  }

  private _renderContinuousUpdatesCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card
        header="${localize(
          "panels.general.cards.continuousupdates.header",
          this.hass.language,
        )}"
      >
        <div class="card-content description-text">
          ${localize(
            "panels.general.cards.continuousupdates.description",
            this.hass.language,
          )}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize(
                "panels.general.cards.continuousupdates.labels.continuousupdates",
                this.hass.language,
              )}
            </label>
            <ha-switch
              .checked="${this.config.continuousupdates}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  continuousupdates: (e.target as HTMLInputElement).checked,
                })}"
            ></ha-switch>
          </div>
          ${this.data.continuousupdates
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "panels.general.cards.continuousupdates.labels.sensor_debounce",
                      this.hass.language,
                    )}
                    (ms)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="1"
                    inputmode="numeric"
                    .value="${this.config.sensor_debounce ?? 100}"
                    @input="${(e: Event) => {
                      const v = parseInt((e.target as HTMLInputElement).value);
                      if (!isNaN(v))
                        this.handleConfigChange({ sensor_debounce: v });
                    }}"
                  />
                </div>
              `
            : ""}
        </div>
      </ha-card>
    `;
  }

  private _renderWeatherSkipCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card header="${localize("weather_skip.title", this.hass.language)}">
        <div class="card-content description-text">
          ${localize("weather_skip.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize("weather_skip.threshold_label", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_irrigation_on_precipitation}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  skip_irrigation_on_precipitation: (
                    e.target as HTMLInputElement
                  ).checked,
                })}"
            ></ha-switch>
          </div>
          ${this.config.skip_irrigation_on_precipitation
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "weather_skip.threshold_label",
                      this.hass.language,
                    )}
                    (${output_unit(
                      this.config,
                      CONF_PRECIPITATION_THRESHOLD_MM,
                    )})
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${this.config.precipitation_threshold_mm ?? 2}"
                    @input="${(e: Event) => {
                      const v = parseFloat(
                        (e.target as HTMLInputElement).value,
                      );
                      if (!isNaN(v))
                        this.handleConfigChange({
                          precipitation_threshold_mm: v,
                        });
                    }}"
                  />
                </div>
              `
            : ""}

          <div class="section-divider">
            ${localize("weather_skip.temp_section_title", this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${localize("weather_skip.temp_section_title", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_temp_enabled}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  skip_on_temp_enabled: (e.target as HTMLInputElement).checked,
                })}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_temp_enabled
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "weather_skip.temp_threshold_label",
                      this.hass.language,
                    )}
                    (°C)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    .value="${this.config.temp_threshold ?? 5}"
                    @input="${(e: Event) => {
                      const v = parseFloat(
                        (e.target as HTMLInputElement).value,
                      );
                      if (!isNaN(v))
                        this.handleConfigChange({ temp_threshold: v });
                    }}"
                  />
                </div>
              `
            : ""}

          <div class="section-divider">
            ${localize("weather_skip.wind_section_title", this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${localize("weather_skip.wind_section_title", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_wind_enabled}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  skip_on_wind_enabled: (e.target as HTMLInputElement).checked,
                })}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_wind_enabled
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "weather_skip.wind_threshold_label",
                      this.hass.language,
                    )}
                    (m/s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${this.config.wind_threshold ?? 6.9}"
                    @input="${(e: Event) => {
                      const v = parseFloat(
                        (e.target as HTMLInputElement).value,
                      );
                      if (!isNaN(v))
                        this.handleConfigChange({ wind_threshold: v });
                    }}"
                  />
                </div>
              `
            : ""}

          <div class="section-divider">
            ${localize(
              "weather_skip.rain_sensor_section_title",
              this.hass.language,
            )}
          </div>
          <div class="setting-row">
            <label>
              ${localize("weather_skip.rain_sensor_label", this.hass.language)}
            </label>
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${this.config.rain_sensor || ""}"
              .includeDomains="${["binary_sensor"]}"
              allow-custom-entity
              @value-changed="${(e: CustomEvent) =>
                this.handleConfigChange({
                  rain_sensor: e.detail.value || null,
                })}"
            ></ha-entity-picker>
          </div>
        </div>
      </ha-card>
    `;
  }

  private _renderCoordinateCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;

    const haCoords = this.hass.config as any;
    const haLatitude = haCoords?.latitude || 0;
    const haLongitude = haCoords?.longitude || 0;
    const haElevation = haCoords?.elevation || 0;

    return html`
      <ha-card
        header="${localize("coordinate_config.title", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${localize("coordinate_config.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize(
                "coordinate_config.manual_enabled",
                this.hass.language,
              )}
            </label>
            <ha-switch
              .checked="${this.config.manual_coordinates_enabled}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  manual_coordinates_enabled: (e.target as HTMLInputElement)
                    .checked,
                })}"
            ></ha-switch>
          </div>
          ${this.config.manual_coordinates_enabled
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "coordinate_config.latitude",
                      this.hass.language,
                    )}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-90"
                    max="90"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${this.config.manual_latitude ?? haLatitude}"
                    @input="${(e: Event) => {
                      const v = parseFloat(
                        (e.target as HTMLInputElement).value,
                      );
                      if (!isNaN(v))
                        this.handleConfigChange({ manual_latitude: v });
                    }}"
                  />
                </div>
                <div class="setting-row">
                  <label>
                    ${localize(
                      "coordinate_config.longitude",
                      this.hass.language,
                    )}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-180"
                    max="180"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${this.config.manual_longitude ?? haLongitude}"
                    @input="${(e: Event) => {
                      const v = parseFloat(
                        (e.target as HTMLInputElement).value,
                      );
                      if (!isNaN(v))
                        this.handleConfigChange({ manual_longitude: v });
                    }}"
                  />
                </div>
                <div class="setting-row">
                  <label>
                    ${localize(
                      "coordinate_config.elevation",
                      this.hass.language,
                    )}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-1000"
                    max="9000"
                    step="1"
                    inputmode="numeric"
                    .value="${this.config.manual_elevation ?? haElevation}"
                    @input="${(e: Event) => {
                      const v = parseFloat(
                        (e.target as HTMLInputElement).value,
                      );
                      if (!isNaN(v))
                        this.handleConfigChange({ manual_elevation: v });
                    }}"
                  />
                </div>
              `
            : html`
                <div
                  class="card-content"
                  style="color: var(--secondary-text-color); font-style: italic;"
                >
                  ${localize(
                    "coordinate_config.current_ha_coords",
                    this.hass.language,
                  )}:
                  ${localize("coordinate_config.latitude", this.hass.language)}:
                  ${haLatitude},
                  ${localize(
                    "coordinate_config.longitude",
                    this.hass.language,
                  )}:
                  ${haLongitude},
                  ${localize(
                    "coordinate_config.elevation",
                    this.hass.language,
                  )}:
                  ${haElevation}m
                </div>
              `}
        </div>
      </ha-card>
    `;
  }

  private _renderDaysBetweenIrrigationCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card
        header="${localize(
          "days_between_irrigation.title",
          this.hass.language,
        )}"
      >
        <div class="card-content description-text">
          ${localize("days_between_irrigation.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize("days_between_irrigation.label", this.hass.language)}
              <div class="setting-description">
                ${localize(
                  "days_between_irrigation.help_text",
                  this.hass.language,
                )}
              </div>
            </label>
            <input
              type="number"
              class="settings-input shortfield"
              min="0"
              max="365"
              step="1"
              inputmode="numeric"
              .value="${this.config.days_between_irrigation ?? 0}"
              @input="${(e: Event) => {
                const v = (e.target as HTMLInputElement).valueAsNumber;
                if (!isNaN(v))
                  this.handleConfigChange({
                    days_between_irrigation: Math.round(v),
                  });
              }}"
            />
          </div>
        </div>
      </ha-card>
    `;
  }

  private _renderZoneSequencingCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    const isRotating =
      (this.config.zone_sequencing || CONF_ZONE_SEQUENCING_PARALLEL) ===
      CONF_ZONE_SEQUENCING_ROTATING;
    return html`
      <ha-card
        header="${localize("zone_sequencing.title", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${localize("zone_sequencing.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${localize("zone_sequencing.title", this.hass.language)}
            </label>
            <select
              class="settings-input"
              .value="${live(
                this.config.zone_sequencing || CONF_ZONE_SEQUENCING_PARALLEL,
              )}"
              @change="${(e: Event) =>
                this.handleConfigChange({
                  [CONF_ZONE_SEQUENCING]: (e.target as HTMLSelectElement).value,
                })}"
            >
              <option
                value="${CONF_ZONE_SEQUENCING_PARALLEL}"
                ?selected="${(this.config.zone_sequencing ||
                  CONF_ZONE_SEQUENCING_PARALLEL) ===
                CONF_ZONE_SEQUENCING_PARALLEL}"
              >
                ${localize("zone_sequencing.parallel", this.hass.language)}
              </option>
              <option
                value="${CONF_ZONE_SEQUENCING_SEQUENTIAL}"
                ?selected="${this.config.zone_sequencing ===
                CONF_ZONE_SEQUENCING_SEQUENTIAL}"
              >
                ${localize("zone_sequencing.sequential", this.hass.language)}
              </option>
              <option
                value="${CONF_ZONE_SEQUENCING_ROTATING}"
                ?selected="${this.config.zone_sequencing ===
                CONF_ZONE_SEQUENCING_ROTATING}"
              >
                ${localize("zone_sequencing.rotating", this.hass.language)}
              </option>
            </select>
          </div>
          ${isRotating
            ? html`
                <div class="setting-row">
                  <label>
                    ${localize(
                      "zone_sequencing.max_consecutive_duration_label",
                      this.hass.language,
                    )}
                  </label>
                  <input
                    type="number"
                    min="1"
                    class="settings-input"
                    .value="${live(
                      this.config.zone_sequencing_max_consecutive_duration ?? 5,
                    )}"
                    @change="${(e: Event) =>
                      this.handleConfigChange({
                        [CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION]:
                          parseInt((e.target as HTMLInputElement).value, 10) ||
                          5,
                      })}"
                  />
                  <span class="unit-label">
                    ${localize(
                      "zone_sequencing.max_consecutive_duration_unit",
                      this.hass.language,
                    )}
                  </span>
                </div>
                <div class="setting-row">
                  <label>
                    ${localize(
                      "zone_sequencing.min_absorption_time_label",
                      this.hass.language,
                    )}
                  </label>
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${live(
                      this.config.zone_sequencing_min_absorption_time ?? 0,
                    )}"
                    @change="${(e: Event) =>
                      this.handleConfigChange({
                        [CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME]:
                          parseInt((e.target as HTMLInputElement).value, 10) ||
                          0,
                      })}"
                  />
                  <span class="unit-label">
                    ${localize(
                      "zone_sequencing.min_absorption_time_unit",
                      this.hass.language,
                    )}
                  </span>
                </div>
              `
            : ""}
        </div>
      </ha-card>
    `;
  }

  private async saveData(
    changes: Partial<SmartIrrigationConfig>,
  ): Promise<void> {
    if (!this.hass || !this.data) return;
    this.isSaving = true;
    this._scheduleUpdate();
    try {
      this.data = { ...this.data, ...changes };
      this._scheduleUpdate();
      await saveConfig(this.hass, this.data);
    } catch (error) {
      console.error("Error saving config:", error);
      handleError(
        error,
        this.shadowRoot!.querySelector("ha-card") as HTMLElement,
      );
      await this._fetchData();
    } finally {
      this.isSaving = false;
      this._scheduleUpdate();
    }
  }

  private handleConfigChange(changes: Partial<SmartIrrigationConfig>): void {
    this.debouncedSave(changes);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      .description-text {
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        padding-bottom: 4px;
      }

      .setting-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid var(--divider-color);
        gap: 16px;
      }

      .setting-row:last-child {
        border-bottom: none;
      }

      .setting-row label {
        flex: 1;
        color: var(--primary-text-color);
        font-size: 0.9375rem;
      }

      .setting-description {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        margin-top: 2px;
      }

      .inline-row {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      .section-divider {
        padding: 12px 0 4px;
        font-weight: 500;
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
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

      /* API key test UI */
      .api-key-status {
        margin-bottom: 4px;
      }

      .api-key-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
      }

      .api-key-badge.configured {
        background: rgba(76, 175, 80, 0.15);
        color: #2e7d32;
      }

      .api-key-badge.missing {
        background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.15);
        color: var(--warning-color);
      }

      .api-key-row {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
      }

      .api-key-input {
        flex: 1;
        min-width: 180px;
      }

      .test-btn {
        white-space: nowrap;
        flex-shrink: 0;
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
        background: rgba(var(--rgb-error-color, 176, 0, 32), 0.1);
        color: var(--error-color, #b00020);
      }
    `;
  }
}
