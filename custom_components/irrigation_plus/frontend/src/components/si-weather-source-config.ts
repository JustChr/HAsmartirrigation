import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { live } from "lit/directives/live.js";
import { HomeAssistant } from "../types";
import { WeatherConfig, testWeatherConfig } from "../data/websockets";
import { localize } from "../../localize/localize";
import {
  CONF_WEATHER_SERVICE_OPENMETEO,
  CONF_WEATHER_SERVICE_OWM,
  CONF_WEATHER_SERVICE_PW,
  CONF_WEATHER_SERVICE_MET,
} from "../const";
import "./si-field";

/**
 * Shared weather-source configuration block: the "use weather service" toggle,
 * the service picker, and (when the service needs one) the API-key field with
 * its Test button and result badge.
 *
 * This is a *controlled* component — the parent owns the values and persists
 * them. It only emits change events and runs the (stateless) key test itself.
 * Used by both the first-run wizard and the General settings view so the two
 * can never drift apart.
 *
 * Events (all bubble + composed):
 *   - "useweather-changed" detail:{ value: boolean }
 *   - "service-changed"    detail:{ value: string }
 *   - "apikey-changed"     detail:{ value: string }
 */
@customElement("si-weather-source-config")
export class SiWeatherSourceConfig extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;

  /** Whether the weather service is enabled. */
  @property({ type: Boolean }) useWeather = false;
  /** Currently selected weather service id. */
  @property() service: string = CONF_WEATHER_SERVICE_OPENMETEO;
  /** The newly typed API key (parent-owned; usually empty after a save). */
  @property() apiKey = "";
  /** Latest fetched weather config (for has_*_api_key / no_api_key_services). */
  @property({ attribute: false }) weatherConfig: WeatherConfig | null = null;

  @state() private _testing = false;
  @state() private _testResult: { success: boolean; error?: string } | null =
    null;
  private _testResultTimer: number | null = null;

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this._testResultTimer) {
      clearTimeout(this._testResultTimer);
      this._testResultTimer = null;
    }
  }

  private _emit(name: string, value: unknown) {
    this.dispatchEvent(
      new CustomEvent(name, {
        detail: { value },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private get _noApiKeyServices(): string[] {
    return (
      this.weatherConfig?.no_api_key_services ?? [
        CONF_WEATHER_SERVICE_OPENMETEO,
      ]
    );
  }

  private get _needsKey(): boolean {
    return (
      this.useWeather &&
      !!this.service &&
      !this._noApiKeyServices.includes(this.service)
    );
  }

  /** Does the backend already have a stored key for the selected service? */
  private get _hasStoredKey(): boolean {
    const cfg = this.weatherConfig;
    if (this.service === CONF_WEATHER_SERVICE_OWM)
      return !!cfg?.has_owm_api_key;
    if (this.service === CONF_WEATHER_SERVICE_PW) return !!cfg?.has_pw_api_key;
    if (this.service === CONF_WEATHER_SERVICE_MET)
      return !!cfg?.has_met_api_key;
    return false;
  }

  private async _testApiKey() {
    if (!this.hass || this._testing) return;
    this._testing = true;
    this._testResult = null;
    if (this._testResultTimer) {
      clearTimeout(this._testResultTimer);
      this._testResultTimer = null;
    }
    try {
      this._testResult = await testWeatherConfig(
        this.hass,
        this.service,
        this.apiKey || null,
      );
      this._testResultTimer = window.setTimeout(() => {
        this._testResult = null;
        this._testResultTimer = null;
      }, 12000);
    } catch {
      this._testResult = { success: false, error: "unknown" };
    } finally {
      this._testing = false;
    }
  }

  render(): TemplateResult {
    const lang = this.hass?.language ?? "en";
    return html`
      <si-field
        label="${localize("weather_service_config.enabled_label", lang)}"
      >
        <ha-switch
          .checked="${this.useWeather}"
          @change="${(e: Event) =>
            this._emit(
              "useweather-changed",
              (e.target as HTMLInputElement).checked,
            )}"
        ></ha-switch>
      </si-field>

      ${this.useWeather ? this._renderServiceAndKey(lang) : ""}
    `;
  }

  private _renderServiceAndKey(lang: string): TemplateResult {
    return html`
      <si-field
        label="${localize("weather_service_config.service_label", lang)}"
      >
        <select
          class="si-input"
          .value="${live(this.service || CONF_WEATHER_SERVICE_OPENMETEO)}"
          @change="${(e: Event) => {
            this._testResult = null;
            this._emit(
              "service-changed",
              (e.target as HTMLSelectElement).value,
            );
          }}"
        >
          <option
            value="${CONF_WEATHER_SERVICE_OPENMETEO}"
            ?selected="${(this.service || CONF_WEATHER_SERVICE_OPENMETEO) ===
            CONF_WEATHER_SERVICE_OPENMETEO}"
          >
            ${localize("weather_service_config.openmeteo", lang)}
          </option>
          <option
            value="${CONF_WEATHER_SERVICE_OWM}"
            ?selected="${this.service === CONF_WEATHER_SERVICE_OWM}"
          >
            ${localize("weather_service_config.owm", lang)}
          </option>
          <option
            value="${CONF_WEATHER_SERVICE_PW}"
            ?selected="${this.service === CONF_WEATHER_SERVICE_PW}"
          >
            ${localize("weather_service_config.pw", lang)}
          </option>
          <option
            value="${CONF_WEATHER_SERVICE_MET}"
            ?selected="${this.service === CONF_WEATHER_SERVICE_MET}"
          >
            ${localize("weather_service_config.met", lang)}
          </option>
        </select>
      </si-field>

      ${this._needsKey
        ? this._renderKeyField(lang)
        : html`<div class="info-note">
            ${localize("weather_service_config.no_api_key_needed", lang)}
          </div>`}
    `;
  }

  private _renderKeyField(lang: string): TemplateResult {
    const hasStored = this._hasStoredKey;
    return html`
      <si-field
        label="${localize("weather_service_config.api_key_label", lang)}"
        help="${localize("weather_service_config.api_key_help", lang)}"
      >
        <span class="api-badge ${hasStored ? "configured" : "missing"}"
          >${localize(
            hasStored
              ? "weather_service_config.api_key_configured"
              : "weather_service_config.api_key_not_configured",
            lang,
          )}</span
        >
        <div class="api-row">
          <input
            type="password"
            class="si-input flex1"
            placeholder="${localize(
              "weather_service_config.api_key_placeholder",
              lang,
            )}"
            .value="${this.apiKey}"
            @input="${(e: Event) => {
              this._testResult = null;
              this._emit(
                "apikey-changed",
                (e.target as HTMLInputElement).value,
              );
            }}"
          />
          <button
            class="test-btn"
            type="button"
            ?disabled="${this._testing || (!this.apiKey && !hasStored)}"
            @click="${this._testApiKey}"
          >
            ${this._testing
              ? localize("weather_service_config.test_button_testing", lang)
              : localize("weather_service_config.test_button", lang)}
          </button>
        </div>
        ${this._testResult !== null
          ? html`<div
              class="test-result ${this._testResult.success
                ? "success"
                : "error"}"
            >
              ${this._testResult.success
                ? localize("weather_service_config.test_success", lang)
                : localize(
                    "weather_service_config.test_error_" +
                      (this._testResult.error ?? "unknown"),
                    lang,
                  )}
            </div>`
          : ""}
      </si-field>
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      :host {
        display: block;
      }

      .si-input {
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

      .si-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }

      select.si-input {
        cursor: pointer;
      }

      .si-input.flex1 {
        flex: 1;
      }

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

      .api-badge.missing {
        background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.15);
        color: var(--warning-color, #ef6c00);
      }

      .test-btn {
        background: transparent;
        border: 1px solid var(--primary-color);
        border-radius: 4px;
        color: var(--primary-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 8px 14px;
        white-space: nowrap;
        flex-shrink: 0;
      }

      .test-btn:hover:not(:disabled) {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
      }

      .test-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
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

      .info-note {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-radius: 4px;
        padding: 8px 12px;
        margin-top: 8px;
      }
    `;
  }
}
