import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement, state } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { mdiDelete, mdiPencil, mdiPlus } from "@mdi/js";

import {
  fetchSchedules,
  saveSchedule,
  deleteSchedule,
  fetchZones,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";
import { localize } from "../../../localize/localize";
import { globalStyle } from "../../styles/global-style";
import {
  DOMAIN,
  SCHEDULE_TYPE_SUNRISE,
  SCHEDULE_TYPE_SUNSET,
  SCHEDULE_TYPE_SOLAR_AZIMUTH,
} from "../../const";
import { SmartIrrigationZone } from "../../types";
import { showErrorToast } from "../../helpers";

const DAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];
const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

interface Schedule {
  id?: string;
  name: string;
  type: string;
  enabled: boolean;
  time?: string;
  days_of_week?: string[];
  day_of_month?: number;
  interval_hours?: number;
  offset_minutes?: number;
  account_for_duration?: boolean;
  azimuth_angle?: number;
  action: string;
  zones: string | string[];
  start_date?: string;
  end_date?: string;
}

function emptySchedule(): Schedule {
  return {
    name: "",
    type: "daily",
    enabled: true,
    time: "06:00",
    action: "irrigate",
    zones: "all",
  };
}

@customElement("smart-irrigation-view-schedules")
class SmartIrrigationViewSchedules extends SubscribeMixin(LitElement) {
  @property({ attribute: false }) public hass!: HomeAssistant;

  @state() private _schedules: Schedule[] = [];
  @state() private _zones: SmartIrrigationZone[] = [];
  @state() private _isLoading = true;
  @state() private _showDialog = false;
  @state() private _editingSchedule: Schedule = emptySchedule();
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
      const [schedules, zones] = await Promise.all([
        fetchSchedules(this.hass),
        fetchZones(this.hass),
      ]);
      this._schedules = schedules || [];
      this._zones = zones || [];
    } catch (e) {
      console.error("Failed to load schedules", e);
      showErrorToast(this, this.hass, "common.errors.load_failed", e);
    } finally {
      this._isLoading = false;
    }
  }

  private _openAdd() {
    this._editingSchedule = emptySchedule();
    this._editingId = null;
    this._showDialog = true;
  }

  private _openEdit(s: Schedule) {
    this._editingSchedule = { ...s };
    this._editingId = s.id ?? null;
    this._showDialog = true;
  }

  private _closeDialog() {
    this._showDialog = false;
  }

  private async _save() {
    const schedule = { ...this._editingSchedule };
    if (this._editingId) schedule.id = this._editingId;
    // Convert zones: if "all" keep as string, else keep as array
    try {
      await saveSchedule(this.hass, schedule);
      this._closeDialog();
      await this._load();
    } catch (e) {
      console.error("Failed to save schedule", e);
      showErrorToast(this, this.hass, "common.errors.save_failed", e);
    }
  }

  private async _delete(id: string) {
    try {
      await deleteSchedule(this.hass, id);
      await this._load();
    } catch (e) {
      console.error("Failed to delete schedule", e);
      showErrorToast(this, this.hass, "common.errors.delete_failed", e);
    }
  }

  private _update(changes: Partial<Schedule>) {
    this._editingSchedule = { ...this._editingSchedule, ...changes };
  }

  private _typeLabel(type: string) {
    const l = localize(`panels.schedules.types.${type}`, this.hass.language);
    return l || type;
  }

  private _actionLabel(action: string) {
    const l = localize(
      `panels.schedules.actions.${action}`,
      this.hass.language,
    );
    return l || action;
  }

  private _zonesLabel(zones: string | string[]) {
    if (zones === "all")
      return localize("panels.schedules.zones_all", this.hass.language);
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
      this._editingSchedule.zones === "all" ||
      !Array.isArray(this._editingSchedule.zones);
    const selectedIds: string[] = allSelected
      ? []
      : (this._editingSchedule.zones as string[]).map(String);

    return html`
      <div class="field">
        <label
          >${localize(
            "panels.schedules.fields.zones",
            this.hass.language,
          )}</label
        >
        <div class="switch-container">
          <input
            type="radio"
            id="zones_all"
            name="zones_mode"
            ?checked="${allSelected}"
            @change=${() => this._update({ zones: "all" })}
          />
          <label for="zones_all"
            >${localize(
              "panels.schedules.zones_all",
              this.hass.language,
            )}</label
          >
          <input
            type="radio"
            id="zones_specific"
            name="zones_mode"
            ?checked="${!allSelected}"
            @change=${() => this._update({ zones: [] })}
          />
          <label for="zones_specific"
            >${localize(
              "panels.schedules.zones_specific",
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
                          const cur = Array.isArray(this._editingSchedule.zones)
                            ? [...(this._editingSchedule.zones as string[])]
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

  private _renderTypeFields() {
    const s = this._editingSchedule;
    switch (s.type) {
      case "daily":
        return html`
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.time",
                this.hass.language,
              )}</label
            >
            <input
              type="time"
              .value="${s.time || "06:00"}"
              @change=${(e: Event) =>
                this._update({ time: (e.target as HTMLInputElement).value })}
            />
          </div>
        `;
      case "weekly":
        return html`
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.time",
                this.hass.language,
              )}</label
            >
            <input
              type="time"
              .value="${s.time || "06:00"}"
              @change=${(e: Event) =>
                this._update({ time: (e.target as HTMLInputElement).value })}
            />
          </div>
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.days_of_week",
                this.hass.language,
              )}</label
            >
            <div class="day-checkboxes">
              ${DAYS.map(
                (day) => html`
                  <label class="day-check">
                    <input
                      type="checkbox"
                      ?checked="${(s.days_of_week || []).includes(day)}"
                      @change=${(e: Event) => {
                        const checked = (e.target as HTMLInputElement).checked;
                        const cur = s.days_of_week || [];
                        const next = checked
                          ? [...cur, day]
                          : cur.filter((d) => d !== day);
                        this._update({ days_of_week: next });
                      }}
                    />
                    ${localize(
                      `panels.schedules.days.${day}`,
                      this.hass.language,
                    )}
                  </label>
                `,
              )}
            </div>
          </div>
        `;
      case "monthly":
        return html`
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.time",
                this.hass.language,
              )}</label
            >
            <input
              type="time"
              .value="${s.time || "06:00"}"
              @change=${(e: Event) =>
                this._update({ time: (e.target as HTMLInputElement).value })}
            />
          </div>
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.day_of_month",
                this.hass.language,
              )}</label
            >
            <input
              type="number"
              min="1"
              max="31"
              .value="${String(s.day_of_month || 1)}"
              @input=${(e: Event) =>
                this._update({
                  day_of_month: parseInt((e.target as HTMLInputElement).value),
                })}
            />
          </div>
        `;
      case "interval":
        return html`
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.interval_hours",
                this.hass.language,
              )}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="1"
                .value="${String(s.interval_hours || 24)}"
                @input=${(e: Event) =>
                  this._update({
                    interval_hours: parseInt(
                      (e.target as HTMLInputElement).value,
                    ),
                  })}
              />
              <span class="suffix"
                >${localize("panels.schedules.hours", this.hass.language)}</span
              >
            </div>
          </div>
        `;
      case SCHEDULE_TYPE_SUNRISE:
      case SCHEDULE_TYPE_SUNSET:
        return html`${this._renderSunOffsetFields()}`;
      case SCHEDULE_TYPE_SOLAR_AZIMUTH:
        return html`
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.azimuth_angle",
                this.hass.language,
              )}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="0"
                max="359"
                step="1"
                .value="${String(s.azimuth_angle ?? 90)}"
                @input=${(e: Event) =>
                  this._update({
                    azimuth_angle: parseInt(
                      (e.target as HTMLInputElement).value,
                    ),
                  })}
              />
              <span class="suffix">°</span>
            </div>
          </div>
          ${this._renderSunOffsetFields()}
        `;
      default:
        return html``;
    }
  }

  private _renderSunOffsetFields() {
    const s = this._editingSchedule;
    return html`
      <div class="field">
        <label
          >${localize(
            "panels.schedules.fields.offset_minutes",
            this.hass.language,
          )}</label
        >
        <div class="input-suffix-row">
          <input
            type="number"
            step="1"
            .value="${String(s.offset_minutes ?? 0)}"
            @input=${(e: Event) =>
              this._update({
                offset_minutes: parseInt((e.target as HTMLInputElement).value),
              })}
          />
          <span class="suffix"
            >${localize("panels.schedules.minutes", this.hass.language)}</span
          >
        </div>
      </div>
      <div class="field-row">
        <label
          >${localize(
            "panels.schedules.fields.account_for_duration",
            this.hass.language,
          )}</label
        >
        <input
          type="checkbox"
          ?checked="${s.account_for_duration !== false}"
          @change=${(e: Event) =>
            this._update({
              account_for_duration: (e.target as HTMLInputElement).checked,
            })}
        />
      </div>
    `;
  }

  private _renderDialog() {
    if (!this._showDialog) return html``;
    const s = this._editingSchedule;
    const title = this._editingId
      ? localize("panels.schedules.dialog.edit_title", this.hass.language)
      : localize("panels.schedules.dialog.add_title", this.hass.language);

    return html`
      <ha-dialog open .heading=${true} @closed=${this._closeDialog}>
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button
              slot="navigationIcon"
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
            ></ha-icon-button>
            <span slot="title">${title}</span>
          </ha-header-bar>
        </div>

        <div class="dialog-content">
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.name",
                this.hass.language,
              )}</label
            >
            <input
              type="text"
              .value="${s.name}"
              @input=${(e: Event) =>
                this._update({ name: (e.target as HTMLInputElement).value })}
              required
            />
          </div>

          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.type",
                this.hass.language,
              )}</label
            >
            <select
              @change=${(e: Event) =>
                this._update({
                  type: (e.target as HTMLSelectElement).value,
                })}
            >
              ${[
                "daily",
                "weekly",
                "monthly",
                "interval",
                "sunrise",
                "sunset",
                "solar_azimuth",
              ].map(
                (t) => html`
                  <option value="${t}" ?selected="${s.type === t}">
                    ${this._typeLabel(t)}
                  </option>
                `,
              )}
            </select>
          </div>

          ${this._renderTypeFields()}

          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.action",
                this.hass.language,
              )}</label
            >
            <select
              @change=${(e: Event) =>
                this._update({
                  action: (e.target as HTMLSelectElement).value,
                })}
            >
              ${["calculate", "update", "irrigate"].map(
                (a) => html`
                  <option value="${a}" ?selected="${s.action === a}">
                    ${this._actionLabel(a)}
                  </option>
                `,
              )}
            </select>
          </div>

          ${this._renderZonePicker()}

          <div class="field-row">
            <label
              >${localize(
                "panels.schedules.fields.enabled",
                this.hass.language,
              )}</label
            >
            <input
              type="checkbox"
              ?checked="${s.enabled}"
              @change=${(e: Event) =>
                this._update({
                  enabled: (e.target as HTMLInputElement).checked,
                })}
            />
          </div>

          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.start_date",
                this.hass.language,
              )}</label
            >
            <input
              type="date"
              .value="${s.start_date || ""}"
              @change=${(e: Event) =>
                this._update({
                  start_date: (e.target as HTMLInputElement).value || undefined,
                })}
            />
          </div>

          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.end_date",
                this.hass.language,
              )}</label
            >
            <input
              type="date"
              .value="${s.end_date || ""}"
              @change=${(e: Event) =>
                this._update({
                  end_date: (e.target as HTMLInputElement).value || undefined,
                })}
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button class="dialog-btn" @click=${this._closeDialog}>
            ${localize("common.actions.cancel", this.hass.language)}
          </button>
          <button class="dialog-btn dialog-btn-primary" @click=${this._save}>
            ${localize("common.actions.save", this.hass.language)}
          </button>
        </div>
      </ha-dialog>
    `;
  }

  render(): TemplateResult {
    if (!this.hass) return html``;

    if (this._isLoading) {
      return html`
        <ha-card
          header="${localize("panels.schedules.title", this.hass.language)}"
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
        header="${localize("panels.schedules.title", this.hass.language)}"
      >
        <div class="card-content">
          ${localize("panels.schedules.description", this.hass.language)}
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${mdiPlus}" />
            </svg>
            ${localize("panels.schedules.add", this.hass.language)}
          </button>
        </div>
      </ha-card>

      ${this._schedules.length === 0
        ? html`
            <ha-card>
              <div class="card-content">
                ${localize("panels.schedules.no_items", this.hass.language)}
              </div>
            </ha-card>
          `
        : this._schedules.map(
            (s) => html`
              <ha-card header="${s.name}">
                <div class="card-content">
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.schedules.fields.type",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${this._typeLabel(s.type)}</span>
                  </div>
                  ${s.time && ["daily", "weekly", "monthly"].includes(s.type)
                    ? html`
                        <div class="info-row">
                          <span class="info-label"
                            >${localize(
                              "panels.schedules.fields.time",
                              this.hass.language,
                            )}:</span
                          >
                          <span>${s.time}</span>
                        </div>
                      `
                    : ""}
                  ${s.interval_hours
                    ? html`
                        <div class="info-row">
                          <span class="info-label"
                            >${localize(
                              "panels.schedules.fields.interval_hours",
                              this.hass.language,
                            )}:</span
                          >
                          <span
                            >${s.interval_hours}
                            ${localize(
                              "panels.schedules.hours",
                              this.hass.language,
                            )}</span
                          >
                        </div>
                      `
                    : ""}
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.schedules.fields.action",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${this._actionLabel(s.action)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.schedules.fields.zones",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${this._zonesLabel(s.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.schedules.fields.enabled",
                        this.hass.language,
                      )}:</span
                    >
                    <span
                      >${s.enabled
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
                      @click=${() => this._openEdit(s)}
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
                      @click=${() => s.id && this._delete(s.id)}
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
        .field input[type="time"],
        .field input[type="date"],
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
        .day-checkboxes,
        .zone-checkboxes {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 4px;
        }
        .day-check,
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
        .info-row {
          display: flex;
          gap: 8px;
          margin-bottom: 4px;
          font-size: 0.9rem;
        }
        .info-label {
          font-weight: 500;
          color: var(--secondary-text-color);
          min-width: 80px;
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
