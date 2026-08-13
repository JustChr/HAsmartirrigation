import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant, SmartIrrigationZone } from "../types";
import { localize } from "../../localize/localize";
import { globalStyle } from "../styles/global-style";
import {
  SCHEDULE_TYPE_SUNRISE,
  SCHEDULE_TYPE_SUNSET,
  SCHEDULE_TYPE_SOLAR_AZIMUTH,
  SCHEDULE_TIME_ANCHOR_START,
  SCHEDULE_TIME_ANCHOR_FINISH,
  SCHEDULE_EARLIEST_START_NONE,
  SCHEDULE_EARLIEST_START_TIME,
  SCHEDULE_EARLIEST_START_SUNSET,
  SCHEDULE_EARLIEST_START_MODES,
  SCHEDULE_DEFAULT_EARLIEST_START_TIME,
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
  earliest_start_mode?: string; // "none" | "time" | "sunset"
  earliest_start_time?: string; // HH:MM, "time" mode only
  earliest_start_offset_minutes?: number; // "sunset" mode only
  fit_to_window?: boolean;
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
 * why it lives here rather than as a private method on either — a single
 * fallback-to-raw-type behavior instead of two copies that could drift.
 */
export function typeLabel(type: string, language: string): string {
  return localize(`panels.schedules.types.${type}`, language) || type;
}

/**
 * Add/edit dialog for a single schedule. The parent (the schedules view) owns
 * which schedule is open, the edit-vs-add distinction (via `heading`), and all
 * backend/websocket communication (load, save, delete) — this component only
 * renders the given `schedule` and emits events, never talks to `hass` beyond
 * localization.
 *
 * Events (bubble + composed):
 *   - "schedule-changed"  detail: { value: Schedule } — fired on every field
 *     edit, mirroring the *-changed convention used by si-distributor-form /
 *     si-zone-form. The parent is expected to store the patched value back
 *     onto the `schedule` property.
 *   - "save"    detail: { value: Schedule } — Save button clicked.
 *   - "cancel"  — Cancel button clicked, or the host ha-dialog's own "closed"
 *     event fired (Escape / backdrop click).
 *
 * Visibility is entirely parent-owned: the parent only renders this element
 * while the dialog should be open, and un-renders it to close. A backend
 * validation failure on save is therefore already handled correctly by the
 * parent simply not un-rendering this element on failure — see
 * view-schedules.ts's `_save`, which only closes the dialog after a
 * successful `saveSchedule` result.
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
   * Resolved start/finish anchor. Mirrors the backend's legacy resolution: only
   * solar schedules ever honored account_for_duration (True => finish);
   * everything else defaults to start.
   */
  private _timeAnchor(s: Schedule): string {
    const isSolar = [
      SCHEDULE_TYPE_SUNRISE,
      SCHEDULE_TYPE_SUNSET,
      SCHEDULE_TYPE_SOLAR_AZIMUTH,
    ].includes(s.type);
    const legacyFinish = isSolar && s.account_for_duration !== false;
    return (
      s.time_anchor ??
      (legacyFinish ? SCHEDULE_TIME_ANCHOR_FINISH : SCHEDULE_TIME_ANCHOR_START)
    );
  }

  /**
   * Whether the run-window controls apply. They only bound a finish anchor: a
   * start-anchored schedule's configured time IS its start, so there is nothing
   * to floor and nothing to fit between.
   */
  private _hasRunWindow(s: Schedule): boolean {
    return (
      s.action === "irrigate" &&
      s.type !== "interval" &&
      this._timeAnchor(s) === SCHEDULE_TIME_ANCHOR_FINISH
    );
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
    const current = this._timeAnchor(s);
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

  /**
   * Earliest start + fit-to-window, the two controls that bound a
   * finish-anchored run. Both default to off, so a schedule nobody edits keeps
   * starting wherever target - demand lands and watering every due zone.
   */
  private _renderRunWindowFields() {
    const s = this.schedule;
    if (!this._hasRunWindow(s)) return html``;
    const lang = this.hass.language;
    const mode = SCHEDULE_EARLIEST_START_MODES.includes(
      s.earliest_start_mode ?? "",
    )
      ? (s.earliest_start_mode as string)
      : SCHEDULE_EARLIEST_START_NONE;
    return html`
      <div class="field">
        <label
          >${localize("panels.schedules.fields.earliest_start", lang)}</label
        >
        <select
          @change=${(e: Event) => {
            const next = (e.target as HTMLSelectElement).value;
            this._emitChanged({
              earliest_start_mode: next,
              // The backend rejects a null/malformed HH:MM outright, so a floor
              // switched on from the picker has to arrive with a usable time.
              earliest_start_time:
                next === SCHEDULE_EARLIEST_START_TIME
                  ? s.earliest_start_time ||
                    SCHEDULE_DEFAULT_EARLIEST_START_TIME
                  : s.earliest_start_time,
            });
          }}
        >
          ${SCHEDULE_EARLIEST_START_MODES.map(
            (m) => html`
              <option value="${m}" ?selected="${mode === m}">
                ${localize(`panels.schedules.earliest_start.${m}`, lang)}
              </option>
            `,
          )}
        </select>
        <span class="field-help"
          >${localize("panels.schedules.help.earliest_start", lang)}</span
        >
      </div>

      ${mode === SCHEDULE_EARLIEST_START_TIME
        ? html`
            <div class="field">
              <label
                >${localize(
                  "panels.schedules.fields.earliest_start_time",
                  lang,
                )}</label
              >
              <input
                type="time"
                .value="${s.earliest_start_time ||
                SCHEDULE_DEFAULT_EARLIEST_START_TIME}"
                @change=${(e: Event) =>
                  this._emitChanged({
                    earliest_start_time: (e.target as HTMLInputElement).value,
                  })}
              />
            </div>
          `
        : ""}
      ${mode === SCHEDULE_EARLIEST_START_SUNSET
        ? html`
            <div class="field">
              <label
                >${localize(
                  "panels.schedules.fields.earliest_start_offset",
                  lang,
                )}</label
              >
              <div class="input-suffix-row">
                <input
                  type="number"
                  step="1"
                  .value="${String(s.earliest_start_offset_minutes ?? 0)}"
                  @input=${(e: Event) => {
                    const v = parseInt((e.target as HTMLInputElement).value);
                    this._emitChanged({
                      earliest_start_offset_minutes: isNaN(v) ? 0 : v,
                    });
                  }}
                />
                <span class="suffix"
                  >${localize("panels.schedules.minutes", lang)}</span
                >
              </div>
            </div>
          `
        : ""}

      <div class="field">
        <div class="field-row">
          <label
            >${localize("panels.schedules.fields.fit_to_window", lang)}</label
          >
          <input
            type="checkbox"
            ?checked="${s.fit_to_window === true}"
            @change=${(e: Event) =>
              // A real boolean, not the input's string value: the backend
              // validates this strictly and rejects "false".
              this._emitChanged({
                fit_to_window: (e.target as HTMLInputElement).checked,
              })}
          />
        </div>
        <span class="field-help"
          >${localize("panels.schedules.help.fit_to_window", lang)}</span
        >
      </div>
    `;
  }

  render(): TemplateResult {
    if (!this.hass || !this.schedule) return html``;
    const s = this.schedule;

    return html`
      <ha-dialog open heading="${this.heading}" @closed=${this._cancel}>
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
          ${this._renderRunWindowFields()} ${this._renderZonePicker()}

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

        <button
          slot="secondaryAction"
          class="dialog-btn"
          @click=${this._cancel}
        >
          ${localize("common.actions.cancel", this.hass.language)}
        </button>
        <button
          slot="primaryAction"
          class="dialog-btn dialog-btn-primary"
          @click=${this._save}
        >
          ${localize("common.actions.save", this.hass.language)}
        </button>
      </ha-dialog>
    `;
  }

  static get styles(): CSSResultGroup {
    return [
      globalStyle,
      css`
        /* The buttons sit in ha-dialog's own action slots rather than in a
           footer inside the content, so the actions bar it always renders is
           the one holding them instead of an empty 52px strip below them. */
        .dialog-content {
          display: flex;
          flex-direction: column;
          gap: 14px;
          padding: 4px 0 8px;
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
        .field-help {
          font-size: 0.8125rem;
          line-height: 1.35;
          color: var(--secondary-text-color);
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
