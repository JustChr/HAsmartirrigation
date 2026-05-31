import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement, state } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { mdiDelete, mdiPencil, mdiPlus } from "@mdi/js";

import {
  fetchAdjustments,
  saveAdjustment,
  deleteAdjustment,
  fetchZones,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";
import { localize } from "../../../localize/localize";
import { globalStyle } from "../../styles/global-style";
import { DOMAIN } from "../../const";
import { SmartIrrigationZone } from "../../types";

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

interface Adjustment {
  id?: string;
  name: string;
  enabled: boolean;
  month_start: number;
  month_end: number;
  multiplier_adjustment: number;
  threshold_adjustment: number;
  zones: string | string[];
}

function emptyAdjustment(): Adjustment {
  return {
    name: "",
    enabled: true,
    month_start: 1,
    month_end: 12,
    multiplier_adjustment: 1.0,
    threshold_adjustment: 0.0,
    zones: "all",
  };
}

@customElement("smart-irrigation-view-adjustments")
class SmartIrrigationViewAdjustments extends SubscribeMixin(LitElement) {
  @property({ attribute: false }) public hass!: HomeAssistant;

  @state() private _adjustments: Adjustment[] = [];
  @state() private _zones: SmartIrrigationZone[] = [];
  @state() private _isLoading = true;
  @state() private _showDialog = false;
  @state() private _editing: Adjustment = emptyAdjustment();
  @state() private _editingId: string | null = null;

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._load();
    return [
      this.hass!.connection.subscribeMessage(() => this._load(), {
        type: DOMAIN + "_config_updated",
      }),
    ];
  }

  private async _load() {
    if (!this.hass) return;
    try {
      const [adjustments, zones] = await Promise.all([
        fetchAdjustments(this.hass),
        fetchZones(this.hass),
      ]);
      this._adjustments = adjustments || [];
      this._zones = zones || [];
    } catch (e) {
      console.error("Failed to load adjustments", e);
    } finally {
      this._isLoading = false;
    }
  }

  private _openAdd() {
    this._editing = emptyAdjustment();
    this._editingId = null;
    this._showDialog = true;
  }

  private _openEdit(a: Adjustment) {
    this._editing = { ...a };
    this._editingId = a.id ?? null;
    this._showDialog = true;
  }

  private _closeDialog() {
    this._showDialog = false;
  }

  private async _save() {
    const adj = { ...this._editing };
    if (this._editingId) adj.id = this._editingId;
    try {
      await saveAdjustment(this.hass, adj);
      this._closeDialog();
      await this._load();
    } catch (e) {
      console.error("Failed to save adjustment", e);
    }
  }

  private async _delete(id: string) {
    try {
      await deleteAdjustment(this.hass, id);
      await this._load();
    } catch (e) {
      console.error("Failed to delete adjustment", e);
    }
  }

  private _update(changes: Partial<Adjustment>) {
    this._editing = { ...this._editing, ...changes };
  }

  private _monthName(m: number) {
    return MONTH_NAMES[m - 1] || String(m);
  }

  private _zonesLabel(zones: string | string[]) {
    if (zones === "all")
      return localize("panels.adjustments.zones_all", this.hass.language);
    if (Array.isArray(zones)) {
      const names = zones
        .map((id) => {
          const z = this._zones.find((z) => String(z.id) === String(id));
          return z ? z.name : id;
        })
        .join(", ");
      return names || zones.join(", ");
    }
    return String(zones);
  }

  private _renderZonePicker() {
    const allSelected =
      this._editing.zones === "all" || !Array.isArray(this._editing.zones);
    const selectedIds: string[] = allSelected
      ? []
      : (this._editing.zones as string[]).map(String);

    return html`
      <div class="field">
        <label
          >${localize(
            "panels.adjustments.fields.zones",
            this.hass.language,
          )}</label
        >
        <div class="switch-container">
          <input
            type="radio"
            id="adj_zones_all"
            name="adj_zones_mode"
            ?checked="${allSelected}"
            @change=${() => this._update({ zones: "all" })}
          />
          <label for="adj_zones_all"
            >${localize(
              "panels.adjustments.zones_all",
              this.hass.language,
            )}</label
          >
          <input
            type="radio"
            id="adj_zones_specific"
            name="adj_zones_mode"
            ?checked="${!allSelected}"
            @change=${() => this._update({ zones: [] })}
          />
          <label for="adj_zones_specific"
            >${localize(
              "panels.adjustments.zones_specific",
              this.hass.language,
            )}</label
          >
        </div>
        ${!allSelected
          ? html`
              <div class="zone-checkboxes">
                ${this._zones.map(
                  (z) => html`
                    <label class="zone-check">
                      <input
                        type="checkbox"
                        ?checked="${selectedIds.includes(String(z.id))}"
                        @change=${(e: Event) => {
                          const checked = (e.target as HTMLInputElement)
                            .checked;
                          const id = String(z.id);
                          const cur = Array.isArray(this._editing.zones)
                            ? [...(this._editing.zones as string[])]
                            : [];
                          const next = checked
                            ? [...cur, id]
                            : cur.filter((x) => x !== id);
                          this._update({ zones: next });
                        }}
                      />
                      ${z.name}
                    </label>
                  `,
                )}
              </div>
            `
          : ""}
      </div>
    `;
  }

  private _renderDialog() {
    if (!this._showDialog) return html``;
    const a = this._editing;
    const title = this._editingId
      ? localize("panels.adjustments.dialog.edit_title", this.hass.language)
      : localize("panels.adjustments.dialog.add_title", this.hass.language);

    return html`
      <ha-dialog open .heading=${true} @closed=${this._closeDialog}>
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button
              slot="navigationIcon"
              dialogAction="cancel"
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
            ></ha-icon-button>
            <span slot="title">${title}</span>
          </ha-header-bar>
        </div>

        <div class="dialog-content">
          <div class="field">
            <label
              >${localize(
                "panels.adjustments.fields.name",
                this.hass.language,
              )}</label
            >
            <input
              type="text"
              .value="${a.name}"
              @input=${(e: Event) =>
                this._update({ name: (e.target as HTMLInputElement).value })}
              required
            />
          </div>

          <div class="field">
            <label
              >${localize(
                "panels.adjustments.fields.month_start",
                this.hass.language,
              )}</label
            >
            <select
              @change=${(e: Event) =>
                this._update({
                  month_start: parseInt((e.target as HTMLSelectElement).value),
                })}
            >
              ${MONTH_NAMES.map(
                (m, i) => html`
                  <option
                    value="${i + 1}"
                    ?selected="${a.month_start === i + 1}"
                  >
                    ${m}
                  </option>
                `,
              )}
            </select>
          </div>

          <div class="field">
            <label
              >${localize(
                "panels.adjustments.fields.month_end",
                this.hass.language,
              )}</label
            >
            <select
              @change=${(e: Event) =>
                this._update({
                  month_end: parseInt((e.target as HTMLSelectElement).value),
                })}
            >
              ${MONTH_NAMES.map(
                (m, i) => html`
                  <option value="${i + 1}" ?selected="${a.month_end === i + 1}">
                    ${m}
                  </option>
                `,
              )}
            </select>
          </div>

          <div class="field">
            <label
              >${localize(
                "panels.adjustments.fields.multiplier_adjustment",
                this.hass.language,
              )}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="0.1"
                max="5.0"
                step="0.1"
                .value="${String(a.multiplier_adjustment)}"
                @input=${(e: Event) =>
                  this._update({
                    multiplier_adjustment: parseFloat(
                      (e.target as HTMLInputElement).value,
                    ),
                  })}
              />
              <span class="suffix">×</span>
            </div>
            <span class="hint"
              >${localize(
                "panels.adjustments.multiplier_hint",
                this.hass.language,
              )}</span
            >
          </div>

          <div class="field">
            <label
              >${localize(
                "panels.adjustments.fields.threshold_adjustment",
                this.hass.language,
              )}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="-50"
                max="50"
                step="0.5"
                .value="${String(a.threshold_adjustment)}"
                @input=${(e: Event) =>
                  this._update({
                    threshold_adjustment: parseFloat(
                      (e.target as HTMLInputElement).value,
                    ),
                  })}
              />
              <span class="suffix">mm</span>
            </div>
            <span class="hint"
              >${localize(
                "panels.adjustments.threshold_hint",
                this.hass.language,
              )}</span
            >
          </div>

          ${this._renderZonePicker()}

          <div class="field-row">
            <label
              >${localize(
                "panels.adjustments.fields.enabled",
                this.hass.language,
              )}</label
            >
            <input
              type="checkbox"
              ?checked="${a.enabled}"
              @change=${(e: Event) =>
                this._update({
                  enabled: (e.target as HTMLInputElement).checked,
                })}
            />
          </div>
        </div>

        <ha-dialog-footer slot="footer">
          <ha-button
            slot="secondaryAction"
            appearance="plain"
            @click=${this._closeDialog}
            dialogAction="cancel"
          >
            ${localize("common.actions.cancel", this.hass.language)}
          </ha-button>
          <ha-button
            slot="primaryAction"
            appearance="accent"
            @click=${this._save}
            dialogAction="close"
          >
            ${localize("common.actions.save", this.hass.language)}
          </ha-button>
        </ha-dialog-footer>
      </ha-dialog>
    `;
  }

  render(): TemplateResult {
    if (!this.hass) return html``;

    if (this._isLoading) {
      return html`
        <ha-card
          header="${localize("panels.adjustments.title", this.hass.language)}"
        >
          <div class="card-content">
            ${localize("common.loading", this.hass.language)}...
          </div>
        </ha-card>
      `;
    }

    return html`
      ${this._renderDialog()}

      <ha-card
        header="${localize("panels.adjustments.title", this.hass.language)}"
      >
        <div class="card-content">
          ${localize("panels.adjustments.description", this.hass.language)}
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${mdiPlus}" />
            </svg>
            ${localize("panels.adjustments.add", this.hass.language)}
          </button>
        </div>
      </ha-card>

      ${this._adjustments.length === 0
        ? html`
            <ha-card>
              <div class="card-content">
                ${localize("panels.adjustments.no_items", this.hass.language)}
              </div>
            </ha-card>
          `
        : this._adjustments.map(
            (a) => html`
              <ha-card header="${a.name}">
                <div class="card-content">
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.adjustments.fields.month_start",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${this._monthName(a.month_start)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.adjustments.fields.month_end",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${this._monthName(a.month_end)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.adjustments.fields.multiplier_adjustment",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${a.multiplier_adjustment}×</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.adjustments.fields.threshold_adjustment",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${a.threshold_adjustment} mm</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.adjustments.fields.zones",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${this._zonesLabel(a.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.adjustments.fields.enabled",
                        this.hass.language,
                      )}:</span
                    >
                    <span
                      >${a.enabled
                        ? localize("common.labels.yes", this.hass.language)
                        : localize(
                            "common.labels.no",
                            this.hass.language,
                          )}</span
                    >
                  </div>
                </div>
                <div class="card-content action-buttons">
                  <div class="action-buttons-left">
                    <div
                      class="action-button-left"
                      @click=${() => this._openEdit(a)}
                    >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${mdiPencil}" />
                      </svg>
                      <span class="action-button-label"
                        >${localize(
                          "common.actions.edit",
                          this.hass.language,
                        )}</span
                      >
                    </div>
                  </div>
                  <div class="action-buttons-right">
                    <div
                      class="action-button-right"
                      @click=${() => a.id && this._delete(a.id)}
                    >
                      <span class="action-button-label"
                        >${localize(
                          "common.actions.delete",
                          this.hass.language,
                        )}</span
                      >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${mdiDelete}" />
                      </svg>
                    </div>
                  </div>
                </div>
              </ha-card>
            `,
          )}
    `;
  }

  static get styles(): CSSResultGroup {
    return [
      globalStyle,
      css`
        .dialog-content {
          display: flex;
          flex-direction: column;
          gap: 14px;
          padding: 4px 0;
          color: var(--primary-text-color);
        }
        .field {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        .field label,
        .field-row label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--secondary-text-color);
        }
        .field input[type="text"],
        .field input[type="number"],
        .field select {
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 1rem;
          font-family: inherit;
          box-sizing: border-box;
        }
        .field-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          min-height: 36px;
        }
        .field-row input[type="checkbox"] {
          width: 18px;
          height: 18px;
          accent-color: var(--primary-color);
        }
        .zone-checkboxes {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 4px;
        }
        .zone-check {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.875rem;
          cursor: pointer;
        }
        .input-suffix-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .input-suffix-row input {
          flex: 1;
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 1rem;
          font-family: inherit;
        }
        .suffix {
          color: var(--secondary-text-color);
          font-size: 0.875rem;
        }
        .hint {
          font-size: 0.8rem;
          color: var(--secondary-text-color);
        }
        .info-row {
          display: flex;
          gap: 8px;
          margin-bottom: 4px;
          font-size: 0.9rem;
        }
        .info-label {
          font-weight: 500;
          color: var(--secondary-text-color);
          min-width: 100px;
        }
        .add-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: var(--primary-color);
          color: var(--text-primary-color, #fff);
          border: none;
          border-radius: 4px;
          font-size: 0.95rem;
          cursor: pointer;
        }
      `,
    ];
  }
}
