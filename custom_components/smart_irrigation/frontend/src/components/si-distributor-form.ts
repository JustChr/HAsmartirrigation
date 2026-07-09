import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { live } from "lit/directives/live.js";
import { HomeAssistant, SmartIrrigationDistributor } from "../types";
import { localize } from "../../localize/localize";
import {
  UNIT_SECONDS,
  DISTRIBUTOR_NAME,
  DISTRIBUTOR_WATERING_MODE,
  DISTRIBUTOR_INLET_ENTITY,
  DISTRIBUTOR_WATCH_MODE,
  DISTRIBUTOR_WATCH_MODES,
  DISTRIBUTOR_RUN_SERVICE,
  DISTRIBUTOR_STOP_SERVICE,
  DISTRIBUTOR_DURATION_FIELD,
  DISTRIBUTOR_DURATION_UNIT,
  DISTRIBUTOR_CONFIRM_ENTITY,
  DISTRIBUTOR_FLOW_SENSOR,
  DISTRIBUTOR_PAUSE_SECONDS,
  DISTRIBUTOR_SKIP_PULSE_SECONDS,
  DISTRIBUTOR_NOTIFY_TARGET,
  WATERING_MODE_CLASSIC,
  WATERING_MODE_SERVICE,
  DISTRIBUTOR_MIN_PAUSE_SECONDS,
  DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS,
} from "../const";
import { globalStyle } from "../styles/global-style";
import "./si-field";

/**
 * Controlled configuration form for one Gardena water distributor. Mirrors the
 * zone-settings row language (`<ha-settings-row>` + `.settings-input`) so it
 * blends into the existing Setup look (spec §8). The parent (the distributor
 * settings view) owns the value and the debounced persistence; this component
 * only renders the current distributor and emits the edited copy.
 *
 * Event (bubbles + composed):
 *   - "distributor-changed"  detail: { value: SmartIrrigationDistributor }
 *
 * `pause_seconds` / `skip_pulse_seconds` show a live below-floor warning; the
 * backend re-floors to 10 s regardless, this just tells the user why.
 */
@customElement("si-distributor-form")
export class SiDistributorForm extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ attribute: false }) distributor!: SmartIrrigationDistributor;

  private _emit(patch: Partial<SmartIrrigationDistributor>) {
    this.dispatchEvent(
      new CustomEvent("distributor-changed", {
        detail: { value: { ...this.distributor, ...patch } },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private _onNumber(field: string, e: Event): void {
    const v = (e.target as HTMLInputElement).valueAsNumber;
    if (isNaN(v)) return;
    // Store what the user typed; the backend floors it. min= on the input
    // discourages sub-floor values, the hint (below) explains the clamp.
    this._emit({
      [field]: Math.max(0, Math.round(v)),
    } as Partial<SmartIrrigationDistributor>);
  }

  render(): TemplateResult {
    if (!this.hass || !this.distributor) return html``;
    const lang = this.hass.language;
    const d = this.distributor;
    const isService = d.watering_mode === WATERING_MODE_SERVICE;

    return html`
      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.name", lang)}</span
        >
        <input
          type="text"
          class="settings-input"
          .value="${d.name ?? ""}"
          @input="${(e: Event) =>
            this._emit({
              [DISTRIBUTOR_NAME]: (e.target as HTMLInputElement).value,
            })}"
        />
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.zones.labels.watering_mode", lang)}</span
        >
        <span slot="description"
          >${localize(
            "panels.distributors.labels.watering_mode_help",
            lang,
          )}</span
        >
        <select
          class="settings-input"
          .value="${live(d.watering_mode ?? WATERING_MODE_CLASSIC)}"
          @change="${(e: Event) =>
            this._emit({
              [DISTRIBUTOR_WATERING_MODE]: (e.target as HTMLSelectElement)
                .value,
            })}"
        >
          <option
            value="${WATERING_MODE_CLASSIC}"
            ?selected="${(d.watering_mode ?? WATERING_MODE_CLASSIC) ===
            WATERING_MODE_CLASSIC}"
          >
            ${localize("panels.zones.labels.watering_modes.classic", lang)}
          </option>
          <option
            value="${WATERING_MODE_SERVICE}"
            ?selected="${d.watering_mode === WATERING_MODE_SERVICE}"
          >
            ${localize("panels.zones.labels.watering_modes.service", lang)}
          </option>
        </select>
      </ha-settings-row>

      ${isService ? this._renderServiceRows(lang) : ""}
      ${this._renderInletWatchRows(lang)} ${this._renderSensorRows(lang)}
      ${this._renderTimingRows(lang)}

      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.notify_target", lang)}</span
        >
        <span slot="description"
          >${localize(
            "panels.distributors.labels.notify_target_help",
            lang,
          )}</span
        >
        <input
          type="text"
          class="settings-input"
          placeholder="${localize(
            "panels.distributors.labels.notify_target_placeholder",
            lang,
          )}"
          .value="${d.notify_target ?? ""}"
          @input="${(e: Event) =>
            this._emit({
              [DISTRIBUTOR_NOTIFY_TARGET]:
                (e.target as HTMLInputElement).value || null,
            })}"
        />
      </ha-settings-row>
    `;
  }

  /**
   * Shared inlet-watch section, rendered in BOTH watering modes (E4,
   * 2026-07-07): the `inlet_entity` ring-valve picker + the tri-state
   * `watch_mode` select. In classic mode Home Assistant both actuates and (per
   * watch_mode) watches the inlet; in service mode the run/stop scripts actuate
   * and this field is watch-ONLY — the help text switches to make that explicit
   * (and that it is NOT the flow/confirm sensor). Replaces the old binary
   * `watch_inlet` toggle; emits the same "distributor-changed" event as every
   * other field so the parent persists `watch_mode` through _configPayload.
   */
  private _renderInletWatchRows(lang: string): TemplateResult {
    const d = this.distributor;
    const isService = d.watering_mode === WATERING_MODE_SERVICE;
    const inletHelpKey = isService
      ? "panels.distributors.labels.inlet_entity_help_service"
      : "panels.distributors.labels.inlet_entity_help";
    const mode = d.watch_mode ?? "ignore";
    return html`
      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.inlet_entity", lang)}</span
        >
        <span slot="description">${localize(inletHelpKey, lang)}</span>
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${d.inlet_entity || ""}"
          .includeDomains="${["switch", "valve", "input_boolean"]}"
          allow-custom-entity
          @value-changed="${(e: CustomEvent) =>
            this._emit({ [DISTRIBUTOR_INLET_ENTITY]: e.detail.value || null })}"
        ></ha-entity-picker>
      </ha-settings-row>

      <!-- No inlet_entity => nothing to watch => the watch_mode row is hidden. -->
      ${d.inlet_entity
        ? html`
            <ha-settings-row>
              <span slot="heading"
                >${localize(
                  "panels.distributors.labels.watch_mode",
                  lang,
                )}</span
              >
              <span slot="description"
                >${localize(
                  "panels.distributors.labels.watch_mode_help",
                  lang,
                )}</span
              >
              <select
                class="settings-input"
                .value="${live(mode)}"
                @change="${(e: Event) =>
                  this._emit({
                    [DISTRIBUTOR_WATCH_MODE]: (e.target as HTMLSelectElement)
                      .value as SmartIrrigationDistributor["watch_mode"],
                  })}"
              >
                ${DISTRIBUTOR_WATCH_MODES.map(
                  (m) => html`
                    <option value="${m}" ?selected="${mode === m}">
                      ${localize(
                        `panels.distributors.labels.watch_mode_${m}`,
                        lang,
                      )}
                    </option>
                  `,
                )}
              </select>
            </ha-settings-row>
          `
        : ""}
    `;
  }

  private _renderServiceRows(lang: string): TemplateResult {
    const d = this.distributor;
    return html`
      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.run_service", lang)}</span
        >
        <span slot="description"
          >${localize(
            "panels.distributors.labels.run_service_help",
            lang,
          )}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${d.run_service || ""}"
          .includeDomains="${["script"]}"
          allow-custom-entity
          @value-changed="${(e: CustomEvent) =>
            this._emit({ [DISTRIBUTOR_RUN_SERVICE]: e.detail.value || null })}"
        ></ha-entity-picker>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.duration_field", lang)}</span
        >
        <span slot="description"
          >${localize(
            "panels.distributors.labels.duration_field_help",
            lang,
          )}</span
        >
        <input
          type="text"
          class="settings-input"
          placeholder="${localize(
            "panels.distributors.labels.duration_field_placeholder",
            lang,
          )}"
          .value="${d.duration_field || "duration"}"
          @input="${(e: Event) =>
            this._emit({
              [DISTRIBUTOR_DURATION_FIELD]:
                (e.target as HTMLInputElement).value || "duration",
            })}"
        />
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.duration_unit", lang)}</span
        >
        <select
          class="settings-input"
          .value="${live(d.duration_unit ?? "seconds")}"
          @change="${(e: Event) =>
            this._emit({
              [DISTRIBUTOR_DURATION_UNIT]: (e.target as HTMLSelectElement)
                .value,
            })}"
        >
          <option
            value="seconds"
            ?selected="${(d.duration_unit ?? "seconds") === "seconds"}"
          >
            ${localize(
              "panels.distributors.labels.duration_units.seconds",
              lang,
            )}
          </option>
          <option value="minutes" ?selected="${d.duration_unit === "minutes"}">
            ${localize(
              "panels.distributors.labels.duration_units.minutes",
              lang,
            )}
          </option>
        </select>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.stop_service", lang)}</span
        >
        <span slot="description"
          >${localize(
            "panels.distributors.labels.stop_service_help",
            lang,
          )}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${d.stop_service || ""}"
          .includeDomains="${["script"]}"
          allow-custom-entity
          @value-changed="${(e: CustomEvent) =>
            this._emit({ [DISTRIBUTOR_STOP_SERVICE]: e.detail.value || null })}"
        ></ha-entity-picker>
      </ha-settings-row>
    `;
  }

  private _renderSensorRows(lang: string): TemplateResult {
    const d = this.distributor;
    return html`
      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.confirm_entity", lang)}</span
        >
        <span slot="description"
          >${localize(
            "panels.distributors.labels.confirm_entity_help",
            lang,
          )}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${d.confirm_entity || ""}"
          .includeDomains="${[
            "binary_sensor",
            "sensor",
            "switch",
            "valve",
            "input_boolean",
          ]}"
          allow-custom-entity
          @value-changed="${(e: CustomEvent) =>
            this._emit({
              [DISTRIBUTOR_CONFIRM_ENTITY]: e.detail.value || null,
            })}"
        ></ha-entity-picker>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.flow_sensor", lang)}</span
        >
        <span slot="description"
          >${localize(
            "panels.distributors.labels.flow_sensor_help",
            lang,
          )}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${d.flow_sensor || ""}"
          .includeDomains="${["sensor"]}"
          allow-custom-entity
          @value-changed="${(e: CustomEvent) =>
            this._emit({ [DISTRIBUTOR_FLOW_SENSOR]: e.detail.value || null })}"
        ></ha-entity-picker>
      </ha-settings-row>
    `;
  }

  private _renderTimingRows(lang: string): TemplateResult {
    const d = this.distributor;
    const pauseLow = (d.pause_seconds ?? 0) < DISTRIBUTOR_MIN_PAUSE_SECONDS;
    const skipLow =
      (d.skip_pulse_seconds ?? 0) < DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS;
    return html`
      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.pause_seconds", lang)}
          (${UNIT_SECONDS})</span
        >
        <span slot="description"
          >${localize("field_help.distributor_pause_seconds", lang)}</span
        >
        <input
          type="number"
          class="settings-input shortfield"
          step="1"
          min="${DISTRIBUTOR_MIN_PAUSE_SECONDS}"
          inputmode="numeric"
          .value="${d.pause_seconds ?? ""}"
          @input="${(e: Event) => this._onNumber(DISTRIBUTOR_PAUSE_SECONDS, e)}"
        />
      </ha-settings-row>
      ${pauseLow
        ? html`<div class="timing-warning">
            ${localize("panels.distributors.hints.below_floor_pause", lang)}
          </div>`
        : ""}

      <ha-settings-row>
        <span slot="heading"
          >${localize("panels.distributors.labels.skip_pulse_seconds", lang)}
          (${UNIT_SECONDS})</span
        >
        <span slot="description"
          >${localize("field_help.distributor_skip_pulse_seconds", lang)}</span
        >
        <input
          type="number"
          class="settings-input shortfield"
          step="1"
          min="${DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS}"
          inputmode="numeric"
          .value="${d.skip_pulse_seconds ?? ""}"
          @input="${(e: Event) =>
            this._onNumber(DISTRIBUTOR_SKIP_PULSE_SECONDS, e)}"
        />
      </ha-settings-row>
      ${skipLow
        ? html`<div class="timing-warning">
            ${localize("panels.distributors.hints.below_floor_skip", lang)}
          </div>`
        : ""}
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      :host {
        display: block;
      }

      ha-settings-row {
        padding: 0 16px;
      }

      .settings-input {
        height: 36px;
      }

      .json-input {
        width: 100%;
        min-width: 220px;
        height: auto;
        font-family: var(--code-font-family, monospace);
        font-size: 0.85rem;
        resize: vertical;
      }

      .json-input.invalid {
        border-color: var(--error-color);
      }

      .json-error {
        color: var(--error-color);
        font-size: 0.8rem;
        padding: 0 16px 6px;
      }

      /* Live "below the enforced floor" note under a timing field. */
      .timing-warning {
        color: var(--warning-color, #f9a825);
        background: var(--secondary-background-color);
        border-left: 3px solid var(--warning-color, #f9a825);
        border-radius: 0 3px 3px 0;
        font-size: 0.82rem;
        line-height: 1.45;
        margin: 0 16px 6px;
        padding: 6px 10px;
      }
    `;
  }
}
