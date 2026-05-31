import { CSSResultGroup, LitElement, css, html, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";
import { UnsubscribeFunc } from "home-assistant-js-websocket";

import { fetchConfig, saveConfig } from "../../data/websockets";
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
      this.config = await fetchConfig(this.hass);
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
    loadHaForm().catch((error) => {
      console.error("Failed to load HA form:", error);
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
      <ha-card header="${localize("panels.general.title", this.hass.language)}">
        <div class="card-content">
          ${localize("panels.general.description", this.hass.language)}
        </div>
      </ha-card>
      ${this._renderAutoUpdateCard()} ${this._renderAutoCalcCard()}
      ${this._renderAutoClearCard()} ${this._renderContinuousUpdatesCard()}
      ${this._renderWeatherSkipCard()} ${this._renderCoordinateCard()}
      ${this._renderDaysBetweenIrrigationCard()}
      ${this._renderZoneSequencingCard()}
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
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.information",
            this.hass.language,
          )}"
        >
          <div class="card-content">
            ${localize(
              "panels.general.cards.automatic-update.description",
              this.hass.language,
            )}
          </div>
        </ha-expansion-panel>
        <ha-settings-row>
          <span slot="heading">
            ${localize(
              "panels.general.cards.automatic-update.labels.auto-update-enabled",
              this.hass.language,
            )}
          </span>
          <ha-switch
            .checked="${this.config.autoupdateenabled}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                autoupdateenabled: (e.target as HTMLInputElement).checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.data.autoupdateenabled
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "panels.general.cards.automatic-update.labels.auto-update-interval",
                    this.hass.language,
                  )}
                </span>
                <div class="inline-row">
                  <ha-textfield
                    type="number"
                    class="shortfield"
                    min="1"
                    step="1"
                    .value="${String(this.data.autoupdateinterval ?? 1)}"
                    @input="${(e: Event) => {
                      const v = parseInt((e.target as HTMLInputElement).value);
                      if (!isNaN(v))
                        this.handleConfigChange({ autoupdateinterval: v });
                    }}"
                  ></ha-textfield>
                  <ha-select
                    .value="${this.data.autoupdateschedule ||
                    AUTO_UPDATE_SCHEDULE_HOURLY}"
                    @selected="${(e: CustomEvent) =>
                      this.handleConfigChange({
                        autoupdateschedule: e.detail.value,
                      })}"
                    @closed="${(e: Event) => e.stopPropagation()}"
                  >
                    <mwc-list-item value="${AUTO_UPDATE_SCHEDULE_MINUTELY}">
                      ${localize(
                        "panels.general.cards.automatic-update.options.minutes",
                        this.hass.language,
                      )}
                    </mwc-list-item>
                    <mwc-list-item value="${AUTO_UPDATE_SCHEDULE_HOURLY}">
                      ${localize(
                        "panels.general.cards.automatic-update.options.hours",
                        this.hass.language,
                      )}
                    </mwc-list-item>
                    <mwc-list-item value="${AUTO_UPDATE_SCHEDULE_DAILY}">
                      ${localize(
                        "panels.general.cards.automatic-update.options.days",
                        this.hass.language,
                      )}
                    </mwc-list-item>
                  </ha-select>
                </div>
              </ha-settings-row>
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "panels.general.cards.automatic-update.labels.auto-update-delay",
                    this.hass.language,
                  )}
                  (s)
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  min="0"
                  step="1"
                  .value="${String(this.config.autoupdatedelay ?? 0)}"
                  @input="${(e: Event) => {
                    const v = parseInt((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({ autoupdatedelay: v });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
            `
          : ""}
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
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.information",
            this.hass.language,
          )}"
        >
          <div class="card-content">
            ${localize(
              "panels.general.cards.automatic-duration-calculation.description",
              this.hass.language,
            )}
          </div>
        </ha-expansion-panel>
        <ha-settings-row>
          <span slot="heading">
            ${localize(
              "panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled",
              this.hass.language,
            )}
          </span>
          <ha-switch
            .checked="${this.config.autocalcenabled}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                autocalcenabled: (e.target as HTMLInputElement).checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.data.autocalcenabled
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "panels.general.cards.automatic-duration-calculation.labels.calc-time",
                    this.hass.language,
                  )}
                </span>
                <ha-textfield
                  class="shortfield"
                  .value="${this.config.calctime}"
                  @input="${(e: Event) =>
                    this.handleConfigChange({
                      calctime: (e.target as HTMLInputElement).value,
                    })}"
                ></ha-textfield>
              </ha-settings-row>
            `
          : ""}
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
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.information",
            this.hass.language,
          )}"
        >
          <div class="card-content">
            ${localize(
              "panels.general.cards.automatic-clear.description",
              this.hass.language,
            )}
          </div>
        </ha-expansion-panel>
        <ha-settings-row>
          <span slot="heading">
            ${localize(
              "panels.general.cards.automatic-clear.labels.automatic-clear-enabled",
              this.hass.language,
            )}
          </span>
          <ha-switch
            .checked="${this.config.autoclearenabled}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                autoclearenabled: (e.target as HTMLInputElement).checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.data.autoclearenabled
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "panels.general.cards.automatic-clear.labels.automatic-clear-time",
                    this.hass.language,
                  )}
                </span>
                <ha-textfield
                  class="shortfield"
                  .value="${this.config.cleardatatime}"
                  @input="${(e: Event) =>
                    this.handleConfigChange({
                      cleardatatime: (e.target as HTMLInputElement).value,
                    })}"
                ></ha-textfield>
              </ha-settings-row>
            `
          : ""}
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
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.information",
            this.hass.language,
          )}"
        >
          <div class="card-content">
            ${localize(
              "panels.general.cards.continuousupdates.description",
              this.hass.language,
            )}
          </div>
        </ha-expansion-panel>
        <ha-settings-row>
          <span slot="heading">
            ${localize(
              "panels.general.cards.continuousupdates.labels.continuousupdates",
              this.hass.language,
            )}
          </span>
          <ha-switch
            .checked="${this.config.continuousupdates}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                continuousupdates: (e.target as HTMLInputElement).checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.data.continuousupdates
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "panels.general.cards.continuousupdates.labels.sensor_debounce",
                    this.hass.language,
                  )}
                  (ms)
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  min="0"
                  step="1"
                  .value="${String(this.config.sensor_debounce ?? 100)}"
                  @input="${(e: Event) => {
                    const v = parseInt((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({ sensor_debounce: v });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
            `
          : ""}
      </ha-card>
    `;
  }

  private _renderWeatherSkipCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card header="${localize("weather_skip.title", this.hass.language)}">
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.information",
            this.hass.language,
          )}"
        >
          <div class="card-content">
            ${localize("weather_skip.description", this.hass.language)}
          </div>
        </ha-expansion-panel>

        <ha-settings-row>
          <span slot="heading">
            ${localize("weather_skip.threshold_label", this.hass.language)}
          </span>
          <span slot="description">
            ${localize(
              "weather_skip.threshold_description",
              this.hass.language,
            )}
          </span>
          <ha-switch
            .checked="${this.config.skip_irrigation_on_precipitation}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                skip_irrigation_on_precipitation: (e.target as HTMLInputElement)
                  .checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.config.skip_irrigation_on_precipitation
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "weather_skip.threshold_label",
                    this.hass.language,
                  )}
                  (${output_unit(this.config, CONF_PRECIPITATION_THRESHOLD_MM)})
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  min="0"
                  step="0.1"
                  .value="${String(
                    this.config.precipitation_threshold_mm ?? 2,
                  )}"
                  @input="${(e: Event) => {
                    const v = parseFloat((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({
                        precipitation_threshold_mm: v,
                      });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
            `
          : ""}

        <div class="section-divider">
          ${localize("weather_skip.temp_section_title", this.hass.language)}
        </div>
        <ha-settings-row>
          <span slot="heading">
            ${localize("weather_skip.temp_section_title", this.hass.language)}
          </span>
          <ha-switch
            .checked="${this.config.skip_on_temp_enabled}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                skip_on_temp_enabled: (e.target as HTMLInputElement).checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.config.skip_on_temp_enabled
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "weather_skip.temp_threshold_label",
                    this.hass.language,
                  )}
                  (°C)
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  step="0.5"
                  .value="${String(this.config.temp_threshold ?? 5)}"
                  @input="${(e: Event) => {
                    const v = parseFloat((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({ temp_threshold: v });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
            `
          : ""}

        <div class="section-divider">
          ${localize("weather_skip.wind_section_title", this.hass.language)}
        </div>
        <ha-settings-row>
          <span slot="heading">
            ${localize("weather_skip.wind_section_title", this.hass.language)}
          </span>
          <ha-switch
            .checked="${this.config.skip_on_wind_enabled}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                skip_on_wind_enabled: (e.target as HTMLInputElement).checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.config.skip_on_wind_enabled
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize(
                    "weather_skip.wind_threshold_label",
                    this.hass.language,
                  )}
                  (m/s)
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  min="0"
                  step="0.1"
                  .value="${String(this.config.wind_threshold ?? 6.9)}"
                  @input="${(e: Event) => {
                    const v = parseFloat((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({ wind_threshold: v });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
            `
          : ""}

        <div class="section-divider">
          ${localize(
            "weather_skip.rain_sensor_section_title",
            this.hass.language,
          )}
        </div>
        <ha-settings-row>
          <span slot="heading">
            ${localize("weather_skip.rain_sensor_label", this.hass.language)}
          </span>
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
        </ha-settings-row>
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
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.information",
            this.hass.language,
          )}"
        >
          <div class="card-content">
            ${localize("coordinate_config.description", this.hass.language)}
          </div>
        </ha-expansion-panel>
        <ha-settings-row>
          <span slot="heading">
            ${localize("coordinate_config.manual_enabled", this.hass.language)}
          </span>
          <ha-switch
            .checked="${this.config.manual_coordinates_enabled}"
            @change="${(e: Event) =>
              this.handleConfigChange({
                manual_coordinates_enabled: (e.target as HTMLInputElement)
                  .checked,
              })}"
          ></ha-switch>
        </ha-settings-row>
        ${this.config.manual_coordinates_enabled
          ? html`
              <ha-settings-row>
                <span slot="heading">
                  ${localize("coordinate_config.latitude", this.hass.language)}
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  min="-90"
                  max="90"
                  step="0.000001"
                  .value="${String(this.config.manual_latitude ?? haLatitude)}"
                  @input="${(e: Event) => {
                    const v = parseFloat((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({ manual_latitude: v });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
              <ha-settings-row>
                <span slot="heading">
                  ${localize("coordinate_config.longitude", this.hass.language)}
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  min="-180"
                  max="180"
                  step="0.000001"
                  .value="${String(
                    this.config.manual_longitude ?? haLongitude,
                  )}"
                  @input="${(e: Event) => {
                    const v = parseFloat((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({ manual_longitude: v });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
              <ha-settings-row>
                <span slot="heading">
                  ${localize("coordinate_config.elevation", this.hass.language)}
                </span>
                <ha-textfield
                  type="number"
                  class="shortfield"
                  min="-1000"
                  max="9000"
                  step="1"
                  .value="${String(
                    this.config.manual_elevation ?? haElevation,
                  )}"
                  @input="${(e: Event) => {
                    const v = parseFloat((e.target as HTMLInputElement).value);
                    if (!isNaN(v))
                      this.handleConfigChange({ manual_elevation: v });
                  }}"
                ></ha-textfield>
              </ha-settings-row>
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
                ${localize("coordinate_config.longitude", this.hass.language)}:
                ${haLongitude},
                ${localize("coordinate_config.elevation", this.hass.language)}:
                ${haElevation}m
              </div>
            `}
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
        <ha-expansion-panel
          .header="${localize(
            "panels.zones.actions.information",
            this.hass.language,
          )}"
        >
          <div class="card-content">
            ${localize(
              "days_between_irrigation.description",
              this.hass.language,
            )}
          </div>
        </ha-expansion-panel>
        <ha-settings-row>
          <span slot="heading">
            ${localize("days_between_irrigation.label", this.hass.language)}
          </span>
          <span slot="description">
            ${localize("days_between_irrigation.help_text", this.hass.language)}
          </span>
          <ha-textfield
            type="number"
            class="shortfield"
            min="0"
            max="365"
            step="1"
            inputmode="numeric"
            .value="${String(this.config.days_between_irrigation ?? 0)}"
            @input="${(e: Event) => {
              const v = (e.target as HTMLInputElement).valueAsNumber;
              if (!isNaN(v))
                this.handleConfigChange({
                  days_between_irrigation: Math.round(v),
                });
            }}"
          ></ha-textfield>
        </ha-settings-row>
      </ha-card>
    `;
  }

  private _renderZoneSequencingCard(): TemplateResult {
    if (!this.hass || !this.config || !this.data) return html``;
    return html`
      <ha-card
        header="${localize("zone_sequencing.title", this.hass.language)}"
      >
        <div class="card-content">
          ${localize("zone_sequencing.description", this.hass.language)}
        </div>
        <ha-settings-row>
          <span slot="heading">
            ${localize("zone_sequencing.title", this.hass.language)}
          </span>
          <ha-select
            .value="${this.config.zone_sequencing ||
            CONF_ZONE_SEQUENCING_PARALLEL}"
            @selected="${(e: CustomEvent) =>
              this.handleConfigChange({
                [CONF_ZONE_SEQUENCING]: e.detail.value,
              })}"
            @closed="${(e: Event) => e.stopPropagation()}"
          >
            <mwc-list-item value="${CONF_ZONE_SEQUENCING_PARALLEL}">
              ${localize("zone_sequencing.parallel", this.hass.language)}
            </mwc-list-item>
            <mwc-list-item value="${CONF_ZONE_SEQUENCING_SEQUENTIAL}">
              ${localize("zone_sequencing.sequential", this.hass.language)}
            </mwc-list-item>
          </ha-select>
        </ha-settings-row>
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

      ha-settings-row {
        padding: 0 16px;
      }

      ha-expansion-panel {
        margin: 8px 16px;
        border-radius: 4px;
        border: 1px solid var(--divider-color);
      }

      .shortfield {
        width: 120px;
      }

      .inline-row {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      .section-divider {
        padding: 12px 16px 4px;
        font-weight: 500;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }
    `;
  }
}
