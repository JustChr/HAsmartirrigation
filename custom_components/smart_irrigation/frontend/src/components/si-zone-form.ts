import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../types";
import { localize } from "../../localize/localize";
import { UNIT_SQ_FT, UNIT_LPM, UNIT_GPM } from "../const";
import "./si-field";

/**
 * Shared "basic zone" form fields: name, size, throughput and (optionally) the
 * linked switch/valve entity. Used by the first-run wizard's Zone step and the
 * Add-Zone dialog so the two collect the same fields with identical units and
 * help text and can never drift.
 *
 * Controlled component — the parent owns the values and the persistence. size
 * and throughput are passed/emitted as raw strings (the parent parses + floors).
 *
 * Events (all bubble + composed, detail: { value }):
 *   - "name-changed"       value: string
 *   - "size-changed"       value: string
 *   - "throughput-changed" value: string
 *   - "entity-changed"     value: string  (only when showEntity)
 */
@customElement("si-zone-form")
export class SiZoneForm extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;

  /** Metric vs imperial — drives the unit badges. Parent derives from config. */
  @property({ type: Boolean }) metric = true;

  @property() name = "";
  @property() size = "";
  @property() throughput = "";
  @property() linkedEntity = "";

  /** Whether to show the linked-entity picker (wizard does; add-dialog doesn't). */
  @property({ type: Boolean }) showEntity = false;

  private _emit(name: string, value: unknown) {
    this.dispatchEvent(
      new CustomEvent(name, {
        detail: { value },
        bubbles: true,
        composed: true,
      }),
    );
  }

  render(): TemplateResult {
    const lang = this.hass?.language ?? "en";
    const sizeUnit = this.metric ? "m²" : UNIT_SQ_FT;
    const throughputUnit = this.metric ? UNIT_LPM : UNIT_GPM;

    return html`
      <si-field label="${localize("panels.zones.labels.name", lang)}" required>
        <input
          type="text"
          class="si-input"
          .value="${this.name}"
          @input="${(e: Event) =>
            this._emit("name-changed", (e.target as HTMLInputElement).value)}"
        />
      </si-field>

      <si-field
        label="${localize("panels.zones.labels.size", lang)}"
        unit="${sizeUnit}"
        help="${localize("field_help.zone_size", lang)}"
      >
        <input
          type="number"
          class="si-input"
          min="0"
          step="0.1"
          inputmode="decimal"
          .value="${this.size}"
          @input="${(e: Event) =>
            this._emit("size-changed", (e.target as HTMLInputElement).value)}"
        />
      </si-field>

      <si-field
        label="${localize("panels.zones.labels.throughput", lang)}"
        unit="${throughputUnit}"
        help="${localize("field_help.zone_throughput", lang)}"
      >
        <input
          type="number"
          class="si-input"
          min="0"
          step="0.1"
          inputmode="decimal"
          .value="${this.throughput}"
          @input="${(e: Event) =>
            this._emit(
              "throughput-changed",
              (e.target as HTMLInputElement).value,
            )}"
        />
      </si-field>

      ${this.showEntity
        ? html`
            <si-field
              label="${localize("panels.zones.labels.linked_entity", lang)}"
              help="${localize("field_help.zone_linked_entity", lang)}"
            >
              <ha-entity-picker
                .hass="${this.hass}"
                .value="${this.linkedEntity}"
                .includeDomains="${["switch", "valve", "input_boolean"]}"
                allow-custom-entity
                @value-changed="${(e: CustomEvent) =>
                  this._emit("entity-changed", e.detail.value || "")}"
              ></ha-entity-picker>
            </si-field>
          `
        : ""}
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
    `;
  }
}
