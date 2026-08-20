import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant, SmartIrrigationZone } from "../types";
import { localize } from "../../localize/localize";
import { globalStyle } from "../styles/global-style";
import {
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
} from "../const";

const DAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

export interface Schedule {
  id?: string;
  name: string;
  type: string;
  enabled: boolean;
  time?: string;
  days_of_week?: string[];
  day_of_month?: number;
  interval_hours?: number;
  start_time?: string; // optional HH:MM clock anchor for interval schedules
  offset_minutes?: number;
  account_for_duration?: boolean; // legacy; superseded by time_anchor
  time_anchor?: string; // "start" | "finish"
  azimuth_angle?: number;
  action: string;
  zones: string | string[];
  start_date?: string;
  end_date?: string;
}

export function emptySchedule(): Schedule {
  return {
    name: "",
    type: "daily",
    enabled: true,
    time: "06:00",
    action: "irrigate",
    zones: "all",
  };
}

/**
 * Human-readable label for a schedule type. Shared between this dialog's own
 * type `<select>` and the schedule-list cards in view-schedules.ts, which is
 * why it lives here rather than as a private method on either - a single
 * fallback-to-raw-type behaviour instead of two copies that could drift.
 */
export function typeLabel(type: string, language: string): string {
  return localize(`panels.schedules.types.${type}`, language) || type;
}

/**
 * Add/edit dialog for a single schedule. The parent (the schedules view) owns
 * which schedule is open, the edit-vs-add distinction (via `heading`), and all
 * backend/websocket communication (load, save, delete) - this component only
 * renders the given `schedule` and emits events, never talks to `hass` beyond
 * localization.
 *
 * Events (bubble + composed):
 *   - "schedule-changed"  detail: { value: Schedule } - fired on every field
 *     edit, mirroring the *-changed convention used by si-distributor-form /
 *     si-zone-form. The parent is expected to store the patched value back
 *     onto the `schedule` property.
 *   - "save"    detail: { value: Schedule } - Save button clicked.
 *   - "cancel"  - Cancel button clicked, or the host ha-dialog's own "closed"
 *     event fired (Escape / backdrop click).
 *
 * Visibility is entirely parent-owned: the parent only renders this element
 * while the dialog should be open, and un-renders it to close. Keeping the
 * open/closed decision on the parent is what lets a save the backend rejects
 * leave the dialog standing, since the parent simply does not un-render it.
 */
@customElement("si-schedule-dialog")
export class SiScheduleDialog extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ attribute: false }) schedule!: Schedule;
  @property({ attribute: false }) zones: SmartIrrigationZone[] = [];
  @property({ attribute: false }) heading = "";

  private _emitChanged(patch: Partial<Schedule>) {
    this.dispatchEvent(
      new CustomEvent("schedule-changed", {
        detail: { value: { ...this.schedule, ...patch } },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private _save = () => {
    this.dispatchEvent(
      new CustomEvent("save", {
        detail: { value: this.schedule },
        bubbles: true,
        composed: true,
      }),
    );
  };

  private _cancel = () => {
    this.dispatchEvent(
      new CustomEvent("cancel", { bubbles: true, composed: true }),
    );
  };

  private _renderZonePicker() {
    const allSelected =
      this.schedule.zones === "all" || !Array.isArray(this.schedule.zones);
    const selectedIds: string[] = allSelected
      ? []
      : (this.schedule.zones as string[]).map(String);

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
            @change=${() => this._emitChanged({ zones: "all" })}
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
            @change=${() => this._emitChanged({ zones: [] })}
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
                ${this.zones.map(
                  (z) => html`
                    <label class="zone-check">
                      <input
                        type="checkbox"
                        ?checked="${selectedIds.includes(String(z.id))}"
                        @change=${(e: Event) => {
                          const checked = (e.target as HTMLInputElement)
                            .checked;
                          const id = String(z.id);
                          const cur = Array.isArray(this.schedule.zones)
                            ? [...(this.schedule.zones as string[])]
                            : [];
                          const next = checked
                            ? [...cur, id]
                            : cur.filter((x) => x !== id);
                          this._emitChanged({ zones: next });
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
    const s = this.schedule;
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
                this._emitChanged({
                  time: (e.target as HTMLInputElement).value,
                })}
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
                this._emitChanged({
                  time: (e.target as HTMLInputElement).value,
                })}
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
                        this._emitChanged({ days_of_week: next });
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
                this._emitChanged({
                  time: (e.target as HTMLInputElement).value,
                })}
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
                this._emitChanged({
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
                  this._emitChanged({
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
          <div class="field">
            <label
              >${localize(
                "panels.schedules.fields.start_time",
                this.hass.language,
              )}</label
            >
            <input
              type="time"
              .value="${s.start_time || ""}"
              @change=${(e: Event) =>
                this._emitChanged({
                  start_time: (e.target as HTMLInputElement).value || undefined,
                })}
            />
          </div>
        `;
      case SCHEDULE_BOUND_MODE_SUNRISE:
      case SCHEDULE_BOUND_MODE_SUNSET:
        return html`${this._renderSunOffsetFields()}`;
      case SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH:
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
                  this._emitChanged({
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
    const s = this.schedule;
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
              this._emitChanged({
                offset_minutes: parseInt((e.target as HTMLInputElement).value),
              })}
          />
          <span class="suffix"
            >${localize("panels.schedules.minutes", this.hass.language)}</span
          >
        </div>
      </div>
    `;
  }

  /**
   * Start-vs-finish anchor. Only meaningful for an irrigate action on a type
   * with a fixed target time (everything except interval). "Finish" fires the
   * run early enough that it ends at the configured time, using the live
   * estimated duration.
   */
  private _renderTimeAnchorField() {
    const s = this.schedule;
    if (s.action !== "irrigate" || s.type === "interval") return html``;
    // Mirror the backend's legacy resolution: only solar schedules ever honored
    // account_for_duration (True => finish); everything else defaults to start.
    const isSolar = ["sunrise", "sunset", "solar_azimuth"].includes(s.type);
    const legacyFinish = isSolar && s.account_for_duration !== false;
    const current = s.time_anchor ?? (legacyFinish ? "finish" : "start");
    return html`
      <div class="field">
        <label
          >${localize(
            "panels.schedules.fields.time_anchor",
            this.hass.language,
          )}</label
        >
        <select
          @change=${(e: Event) =>
            this._emitChanged({
              time_anchor: (e.target as HTMLSelectElement).value,
            })}
        >
          ${["start", "finish"].map(
            (a) => html`
              <option value="${a}" ?selected="${current === a}">
                ${localize(
                  `panels.schedules.time_anchor.${a}`,
                  this.hass.language,
                )}
              </option>
            `,
          )}
        </select>
      </div>
    `;
  }

  render(): TemplateResult {
    if (!this.hass || !this.schedule) return html``;
    const s = this.schedule;

    return html`
      <ha-dialog open .heading=${true} @closed=${this._cancel}>
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button
              slot="navigationIcon"
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
            ></ha-icon-button>
            <span slot="title">${this.heading}</span>
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
                this._emitChanged({
                  name: (e.target as HTMLInputElement).value,
                })}
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
                this._emitChanged({
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
                    ${typeLabel(t, this.hass.language)}
                  </option>
                `,
              )}
            </select>
          </div>

          ${this._renderTypeFields()} ${this._renderTimeAnchorField()}
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
                this._emitChanged({
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
                this._emitChanged({
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
                this._emitChanged({
                  end_date: (e.target as HTMLInputElement).value || undefined,
                })}
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button class="dialog-btn" @click=${this._cancel}>
            ${localize("common.actions.cancel", this.hass.language)}
          </button>
          <button class="dialog-btn dialog-btn-primary" @click=${this._save}>
            ${localize("common.actions.save", this.hass.language)}
          </button>
        </div>
      </ha-dialog>
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
      `,
    ];
  }
}
