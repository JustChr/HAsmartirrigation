import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant, SmartIrrigationZone } from "../types";
import { localize } from "../../localize/localize";
import { globalStyle } from "../styles/global-style";
import {
  SCHEDULE_RECURRENCES,
  SCHEDULE_RECURRENCE_INTERVAL,
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_BOUND_MODES,
  SCHEDULE_ANCHOR_START,
  SCHEDULE_ANCHOR_FINISH,
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

// A run's window is two independently bounded ends — see GitLab #27. `recurrence`
// (daily/weekly/monthly/interval) is independent of where in the day it lands,
// which is the Start/Finish bound below. `anchor` only matters when both ends
// are bounded, naming which one the run is pinned to.
export interface Schedule {
  id?: string;
  name: string;
  recurrence: string;
  enabled: boolean;
  days_of_week?: string[];
  day_of_month?: number;
  interval_hours?: number;
  start_time?: string; // HH:MM — start_mode = "time", or interval's own optional clock anchor
  start_mode?: string; // "none" | "time" | "sunrise" | "sunset" | "solar_azimuth"
  start_offset?: number; // signed minutes, sun-relative start modes
  start_azimuth?: number; // degrees, start_mode = "solar_azimuth"
  finish_mode?: string; // "none" | "time" | "sunrise" | "sunset" | "solar_azimuth"
  finish_time?: string; // HH:MM, finish_mode = "time"
  finish_offset?: number; // signed minutes, sun-relative finish modes
  finish_azimuth?: number; // degrees, finish_mode = "solar_azimuth"
  anchor?: string; // "start" | "finish" — only meaningful when both ends bounded
  action: string;
  zones: string | string[];
  start_date?: string;
  end_date?: string;
}

export function emptySchedule(): Schedule {
  return {
    name: "",
    recurrence: "daily",
    enabled: true,
    start_mode: SCHEDULE_BOUND_MODE_TIME,
    start_time: "06:00",
    finish_mode: SCHEDULE_BOUND_MODE_NONE,
    action: "irrigate",
    zones: "all",
  };
}

/**
 * Human-readable label for a schedule's recurrence. Shared between this
 * dialog's own recurrence `<select>` and the schedule-list cards in
 * view-schedules.ts, which is why it lives here rather than as a private
 * method on either — a single fallback-to-raw-value behavior instead of two
 * copies that could drift.
 */
export function recurrenceLabel(recurrence: string, language: string): string {
  return (
    localize(`panels.schedules.types.${recurrence}`, language) || recurrence
  );
}

type BoundEnd = "start" | "finish";

interface BoundFieldConfig {
  end: BoundEnd;
  mode: string;
  time?: string;
  offset?: number;
  azimuth?: number;
  emitMode: (v: string) => void;
  emitTime: (v: string) => void;
  emitOffset: (v: number) => void;
  emitAzimuth: (v: number) => void;
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
 *
 * This reads and writes the reshaped storage fields (GitLab #27: recurrence
 * plus independent Start/Finish bounds) but keeps the prior flat layout — the
 * grouped WHEN/ZONES/SEASON redesign and the run-window dial are a later
 * ticket.
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

  /** Recurrence-specific fields: weekday picker, day-of-month, or the
   * interval's own hours + optional clock anchor. Daily needs nothing here —
   * its only configuration is the Start/Finish bound below. */
  private _renderRecurrenceFields() {
    const s = this.schedule;
    const lang = this.hass.language;
    switch (s.recurrence) {
      case "weekly":
        return html`
          <div class="field">
            <label
              >${localize("panels.schedules.fields.days_of_week", lang)}</label
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
                    ${localize(`panels.schedules.days.${day}`, lang)}
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
              >${localize("panels.schedules.fields.day_of_month", lang)}</label
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
                lang,
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
                >${localize("panels.schedules.hours", lang)}</span
              >
            </div>
          </div>
          <div class="field">
            <label
              >${localize("panels.schedules.fields.start_time", lang)}</label
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
      default:
        return html``;
    }
  }

  /** One end (Start or Finish) of the run's window: a mode picker plus
   * whichever of time/offset/azimuth that mode needs. */
  private _renderBoundFields(config: BoundFieldConfig) {
    const {
      end,
      mode,
      time,
      offset,
      azimuth,
      emitMode,
      emitTime,
      emitOffset,
      emitAzimuth,
    } = config;
    const lang = this.hass.language;
    return html`
      <div class="field">
        <label>${localize(`panels.schedules.fields.${end}_mode`, lang)}</label>
        <select
          @change=${(e: Event) =>
            emitMode((e.target as HTMLSelectElement).value)}
        >
          ${SCHEDULE_BOUND_MODES.map(
            (m) => html`
              <option value="${m}" ?selected="${mode === m}">
                ${localize(`panels.schedules.bound_mode.${m}`, lang)}
              </option>
            `,
          )}
        </select>
      </div>
      ${mode === SCHEDULE_BOUND_MODE_TIME
        ? html`
            <div class="field">
              <label
                >${localize(`panels.schedules.fields.${end}_time`, lang)}</label
              >
              <input
                type="time"
                .value="${time || "06:00"}"
                @change=${(e: Event) =>
                  emitTime((e.target as HTMLInputElement).value)}
              />
            </div>
          `
        : ""}
      ${mode === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH
        ? html`
            <div class="field">
              <label
                >${localize(
                  "panels.schedules.fields.azimuth_angle",
                  lang,
                )}</label
              >
              <div class="input-suffix-row">
                <input
                  type="number"
                  min="0"
                  max="359"
                  step="1"
                  .value="${String(azimuth ?? 90)}"
                  @input=${(e: Event) =>
                    emitAzimuth(parseInt((e.target as HTMLInputElement).value))}
                />
                <span class="suffix">°</span>
              </div>
            </div>
          `
        : ""}
      ${mode === SCHEDULE_BOUND_MODE_SUNRISE ||
      mode === SCHEDULE_BOUND_MODE_SUNSET ||
      mode === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH
        ? html`
            <div class="field">
              <label
                >${localize(
                  "panels.schedules.fields.offset_minutes",
                  lang,
                )}</label
              >
              <div class="input-suffix-row">
                <input
                  type="number"
                  step="1"
                  .value="${String(offset ?? 0)}"
                  @input=${(e: Event) => {
                    const v = parseInt((e.target as HTMLInputElement).value);
                    emitOffset(isNaN(v) ? 0 : v);
                  }}
                />
                <span class="suffix"
                  >${localize("panels.schedules.minutes", lang)}</span
                >
              </div>
            </div>
          `
        : ""}
    `;
  }

  private _bothBounded(s: Schedule): boolean {
    return (
      (s.start_mode ?? SCHEDULE_BOUND_MODE_NONE) !== SCHEDULE_BOUND_MODE_NONE &&
      (s.finish_mode ?? SCHEDULE_BOUND_MODE_NONE) !== SCHEDULE_BOUND_MODE_NONE
    );
  }

  /** Which end the run is pinned to. Only shown once both ends carry a bound
   * — with a single bound that bound is unambiguously the anchor. */
  private _renderAnchorField() {
    const s = this.schedule;
    if (!this._bothBounded(s)) return html``;
    const lang = this.hass.language;
    const current =
      s.anchor === SCHEDULE_ANCHOR_START
        ? SCHEDULE_ANCHOR_START
        : SCHEDULE_ANCHOR_FINISH;
    return html`
      <div class="field">
        <label>${localize("panels.schedules.fields.anchor", lang)}</label>
        <select
          @change=${(e: Event) =>
            this._emitChanged({
              anchor: (e.target as HTMLSelectElement).value,
            })}
        >
          ${[SCHEDULE_ANCHOR_START, SCHEDULE_ANCHOR_FINISH].map(
            (a) => html`
              <option value="${a}" ?selected="${current === a}">
                ${localize(`panels.schedules.anchor.${a}`, lang)}
              </option>
            `,
          )}
        </select>
      </div>
    `;
  }

  private _renderStartFinishFields() {
    const s = this.schedule;
    if (s.recurrence === SCHEDULE_RECURRENCE_INTERVAL) return html``;
    return html`
      ${this._renderBoundFields({
        end: "start",
        mode: s.start_mode ?? SCHEDULE_BOUND_MODE_NONE,
        time: s.start_time,
        offset: s.start_offset,
        azimuth: s.start_azimuth,
        emitMode: (v) => this._emitChanged({ start_mode: v }),
        emitTime: (v) => this._emitChanged({ start_time: v }),
        emitOffset: (v) => this._emitChanged({ start_offset: v }),
        emitAzimuth: (v) => this._emitChanged({ start_azimuth: v }),
      })}
      ${this._renderBoundFields({
        end: "finish",
        mode: s.finish_mode ?? SCHEDULE_BOUND_MODE_NONE,
        time: s.finish_time,
        offset: s.finish_offset,
        azimuth: s.finish_azimuth,
        emitMode: (v) => this._emitChanged({ finish_mode: v }),
        emitTime: (v) => this._emitChanged({ finish_time: v }),
        emitOffset: (v) => this._emitChanged({ finish_offset: v }),
        emitAzimuth: (v) => this._emitChanged({ finish_azimuth: v }),
      })}
      ${this._renderAnchorField()}
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
                "panels.schedules.fields.recurrence",
                this.hass.language,
              )}</label
            >
            <select
              @change=${(e: Event) =>
                this._emitChanged({
                  recurrence: (e.target as HTMLSelectElement).value,
                })}
            >
              ${SCHEDULE_RECURRENCES.map(
                (r) => html`
                  <option value="${r}" ?selected="${s.recurrence === r}">
                    ${recurrenceLabel(r, this.hass.language)}
                  </option>
                `,
              )}
            </select>
          </div>

          ${this._renderRecurrenceFields()} ${this._renderStartFinishFields()}
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
