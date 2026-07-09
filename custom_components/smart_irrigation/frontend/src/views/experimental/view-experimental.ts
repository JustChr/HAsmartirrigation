import { CSSResultGroup, LitElement, css, html, TemplateResult } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../../types";
import { UnsubscribeFunc } from "home-assistant-js-websocket";

import { fetchConfig, saveConfig } from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";
import { localize } from "../../../localize/localize";
import { showErrorToast } from "../../helpers";
import { SmartIrrigationConfig } from "../../types";
import { globalStyle } from "../../styles/global-style";
import {
  CONF_OBSERVED_WATERING_ENABLED,
  CONF_LIVE_ESTIMATE_ENABLED,
  CONF_DISTRIBUTORS_ENABLED,
  DOMAIN,
} from "../../const";

// Note: forecast-weighted durations moved out of this tab into the unified
// "When rain is forecast" control on the When-to-Water tab (WS-6). The backend
// flag (forecast_weighting_enabled) is unchanged; it's just surfaced there now.
type ExperimentalFlag =
  | typeof CONF_OBSERVED_WATERING_ENABLED
  | typeof CONF_LIVE_ESTIMATE_ENABLED
  | typeof CONF_DISTRIBUTORS_ENABLED;

/**
 * Setup → Experimental: opt-in features that change how the bucket is filled.
 * Each is a single switch with a thorough description so users understand the
 * behaviour (and its caveats) before turning it on. Both default to off; the
 * backend merges these partial config saves, so toggling one never clobbers the
 * other settings.
 */
@customElement("smart-irrigation-view-experimental")
export class SmartIrrigationViewExperimental extends SubscribeMixin(
  LitElement,
) {
  hass?: HomeAssistant;
  @property() narrow!: boolean;

  @state() private config?: SmartIrrigationConfig;
  @state() private _saving = false;

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._fetchData().catch((error) => {
      console.error("Failed to fetch experimental config:", error);
    });
    return [
      this.hass!.connection.subscribeMessage(
        () => {
          this._fetchData().catch((error) => {
            console.error("Failed to refresh experimental config:", error);
          });
        },
        { type: DOMAIN + "_config_updated" },
      ),
    ];
  }

  private async _fetchData(): Promise<void> {
    if (!this.hass) return;
    try {
      this.config = await fetchConfig(this.hass);
    } catch (error) {
      console.error("Error fetching config:", error);
      showErrorToast(this, this.hass, "common.errors.load_failed", error);
    }
  }

  private async _toggle(
    field: ExperimentalFlag,
    value: boolean,
  ): Promise<void> {
    if (!this.hass || !this.config) return;
    // Optimistic update so the switch reflects intent immediately.
    this.config = { ...this.config, [field]: value } as SmartIrrigationConfig;
    this._saving = true;
    try {
      await saveConfig(this.hass, { [field]: value });
    } catch (error) {
      console.error("Error saving experimental config:", error);
      showErrorToast(this, this.hass, "common.errors.save_failed", error);
      await this._fetchData();
    } finally {
      this._saving = false;
    }
  }

  render() {
    if (!this.hass || !this.config) {
      return html`<div class="loading-indicator">
        ${localize(
          "common.loading-messages.configuration",
          this.hass?.language ?? "en",
        )}
      </div>`;
    }
    return html`
      ${this._renderIntro()}
      ${this._renderToggleCard(
        "observed_watering",
        CONF_OBSERVED_WATERING_ENABLED,
        this.config.observed_watering_enabled,
      )}
      ${this._renderToggleCard(
        "live_estimate",
        CONF_LIVE_ESTIMATE_ENABLED,
        this.config.live_estimate_enabled,
      )}
      ${this._renderToggleCard(
        "distributors",
        CONF_DISTRIBUTORS_ENABLED,
        this.config.distributors_enabled,
      )}
    `;
  }

  private _renderIntro(): TemplateResult {
    if (!this.hass) return html``;
    return html`
      <div class="experimental-banner">
        <ha-icon icon="mdi:flask-outline"></ha-icon>
        <div>
          <div class="experimental-banner-title">
            ${localize("panels.experimental.title", this.hass.language)}
          </div>
          <div class="experimental-banner-text">
            ${localize("panels.experimental.warning", this.hass.language)}
          </div>
        </div>
      </div>
    `;
  }

  private _renderToggleCard(
    key: string,
    field: ExperimentalFlag,
    checked: boolean,
  ): TemplateResult {
    if (!this.hass) return html``;
    const base = `panels.experimental.${key}`;
    return html`
      <ha-card header="${localize(`${base}.title`, this.hass.language)}">
        <div class="card-content description-text">
          ${localize(`${base}.description`, this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${localize(`${base}.label`, this.hass.language)}</label>
            <ha-switch
              .checked="${checked}"
              ?disabled="${this._saving}"
              @change="${(e: Event) =>
                this._toggle(field, (e.target as HTMLInputElement).checked)}"
            ></ha-switch>
          </div>
          <div class="setting-note">
            ${localize(`${base}.note`, this.hass.language)}
          </div>
        </div>
      </ha-card>
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      .experimental-banner {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 8px;
        background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.12);
        color: var(--primary-text-color);
      }

      .experimental-banner ha-icon {
        color: var(--warning-color, #ff9800);
        --mdc-icon-size: 24px;
        flex-shrink: 0;
      }

      .experimental-banner-title {
        font-weight: 600;
        margin-bottom: 2px;
      }

      .experimental-banner-text {
        font-size: 0.875rem;
        color: var(--secondary-text-color);
      }

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
        gap: 16px;
      }

      .setting-row label {
        flex: 1;
        color: var(--primary-text-color);
        font-size: 0.9375rem;
      }

      .setting-note {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        font-style: italic;
        padding-top: 4px;
        border-top: 1px solid var(--divider-color);
      }
    `;
  }
}
