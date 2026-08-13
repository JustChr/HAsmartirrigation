import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant, SmartIrrigationZone } from "../types";
import { localize } from "../../localize/localize";
import { globalStyle } from "../styles/global-style";
import {
  SCHEDULE_RECURRENCES,
  SCHEDULE_RECURRENCE_INTERVAL,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_BOUND_MODES,
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_ANCHOR_START,
  SCHEDULE_ANCHOR_FINISH,
} from "../const";
import {
  EndRow,
  ScheduleRows,
  scheduleToRows,
  rowsToSchedule,
  describeWindow,
  isWarningHelp,
  HelpKey,
  UnresolvableEnds,
  defaultRowForMode,
  DEFAULT_AZIMUTH,
  BoundMode,
  Anchor,
} from "../common/schedule-rows";
import { summarizeSchedule } from "../common/schedule-summary";
import { azimuthResolverFromLocation } from "../common/solar-azimuth";
import "./si-run-window-dial";

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
  // Populated by the schedules websocket response (GitLab #26) — total
  // seconds the schedule's zones nominally demand under normal sequencing,
  // independent of any zone's live bucket. Absent on a not-yet-saved
  // schedule (the dial then simply has nothing to draw a run bar from).
  nominal_demand_seconds?: number;
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
 * plus independent Start/Finish bounds) through the two Start/Finish rows
 * plus their help text and the pinned-end row (GitLab #29) — all sourced
 * from the pure mapping in ../common/schedule-rows.ts, which is also where
 * the rows<->fields round trip is tested. Fields are grouped into WHEN/
 * ZONES/SEASON cards with a read-only summary sentence at the top (GitLab
 * #30, ../common/schedule-summary.ts — the same sentence heads each card in
 * view-schedules.ts's list). The 24-hour run-window dial is a later ticket
 * (GitLab #31).
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

  /** The row's single stepper: the one control whose kind matches the
   * quantity the current mode carries (time picker / signed minutes /
   * degrees) — never more than one, and never a before/after dropdown next
   * to a magnitude. "none" carries nothing, so it renders no stepper at
   * all. */
  private _renderRowStepper(row: EndRow, onChange: (row: EndRow) => void) {
    const lang = this.hass.language;
    switch (row.mode) {
      case SCHEDULE_BOUND_MODE_TIME:
        return html`
          <input
            type="time"
            .value="${row.time ?? "06:00"}"
            @change=${(e: Event) =>
              onChange({
                ...row,
                time: (e.target as HTMLInputElement).value,
              })}
          />
        `;
      case SCHEDULE_BOUND_MODE_SUNRISE:
      case SCHEDULE_BOUND_MODE_SUNSET:
        return html`
          <span class="row-inline"
            >${localize("panels.schedules.fields.offset_by", lang)}</span
          >
          <input
            type="number"
            step="1"
            .value="${String(row.offset ?? 0)}"
            @input=${(e: Event) => {
              const v = parseInt((e.target as HTMLInputElement).value);
              onChange({ ...row, offset: isNaN(v) ? 0 : v });
            }}
          />
          <span class="row-inline"
            >${localize("panels.schedules.minutes", lang)}</span
          >
        `;
      case SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH:
        // No "offset by" prefix here, unlike sunrise/sunset: azimuth is an
        // absolute compass bearing, not an offset from an event, so the row
        // reads as "At solar azimuth [90] °" rather than misnaming a bearing
        // as an offset.
        return html`
          <input
            type="number"
            min="0"
            max="359"
            step="1"
            .value="${String(row.azimuth ?? DEFAULT_AZIMUTH)}"
            @input=${(e: Event) => {
              const v = parseInt((e.target as HTMLInputElement).value);
              onChange({
                ...row,
                azimuth: isNaN(v) ? (row.azimuth ?? DEFAULT_AZIMUTH) : v,
              });
            }}
          />
          <span class="row-inline">°</span>
        `;
      default:
        return html``;
    }
  }

  /** One row — Start, Finish, or (see `_renderAnchorRow`) the pinned-end
   * choice: a mode picker, that mode's single stepper, and a help line
   * rendered as its indented child. `onChange` receives the row's full new
   * value (mode change included) so the caller can fold it back into the
   * pair and re-derive both fields and help in one place. */
  private _renderWindowRow(
    end: BoundEnd,
    row: EndRow,
    helpKey: HelpKey,
    onChange: (row: EndRow) => void,
  ) {
    const lang = this.hass.language;
    return html`
      <div class="window-row">
        <label>${localize(`panels.schedules.fields.${end}_mode`, lang)}</label>
        <select
          @change=${(e: Event) =>
            onChange(
              defaultRowForMode(
                (e.target as HTMLSelectElement).value as BoundMode,
              ),
            )}
        >
          ${SCHEDULE_BOUND_MODES.map(
            (m) => html`
              <option value="${m}" ?selected="${row.mode === m}">
                ${localize(`panels.schedules.bound_mode.${m}`, lang)}
              </option>
            `,
          )}
        </select>
        ${this._renderRowStepper(row, onChange)}
      </div>
      <div
        class="window-row-help ${helpKey === "error"
          ? "is-error"
          : isWarningHelp(helpKey)
            ? "is-warning"
            : ""}"
      >
        <span class="help-arrow" aria-hidden="true">↳</span>
        <span class="help-text"
          >${localize(`panels.schedules.help.${helpKey}`, lang)}</span
        >
      </div>
    `;
  }

  /** The third row: which end the run is pinned to, water as late (pinned
   * to Finish) or as early (pinned to Start) as possible in the window.
   * Only rendered once both ends carry a bound — with a single bound that
   * bound is unambiguously the anchor and there is nothing to choose. */
  private _renderAnchorRow(
    rows: ScheduleRows,
    patch: (rows: ScheduleRows) => void,
  ) {
    const lang = this.hass.language;
    return html`
      <div class="window-row">
        <label>${localize("panels.schedules.fields.anchor", lang)}</label>
        <select
          @change=${(e: Event) =>
            patch({
              ...rows,
              anchor: (e.target as HTMLSelectElement).value as Anchor,
            })}
        >
          ${[SCHEDULE_ANCHOR_START, SCHEDULE_ANCHOR_FINISH].map(
            (a) => html`
              <option value="${a}" ?selected="${rows.anchor === a}">
                ${localize(`panels.schedules.anchor.${a}`, lang)}
              </option>
            `,
          )}
        </select>
      </div>
    `;
  }

  /** Start row, Finish row, and (only when both are bounded) the pinned-end
   * row — all three sourced from the one pure rows<->fields mapping
   * (../common/schedule-rows.ts). Interval has no time of day and
   * therefore no window: none of these rows apply to it. */
  /**
   * Which bounded ends name a bearing the sun never reaches at this location
   * (GitLab #34). Resolved through the same module the dial draws with, so
   * the faded end and the amber help text can never disagree about it.
   *
   * Only solar_azimuth ends can be unresolvable; every other mode always has
   * a time. An unknown location yields no resolver, and an unknown answer is
   * not a warning, so nothing is flagged in that case.
   */
  private _unresolvableEnds(rows: ScheduleRows): UnresolvableEnds {
    const resolve = azimuthResolverFromLocation(this.hass?.config, new Date());
    if (!resolve) return {};
    const unreachable = (row: EndRow) =>
      row.mode === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH &&
      resolve(row.azimuth ?? DEFAULT_AZIMUTH) === null;
    return {
      start: unreachable(rows.start),
      finish: unreachable(rows.finish),
    };
  }

  private _renderWindowRows() {
    const s = this.schedule;
    if (s.recurrence === SCHEDULE_RECURRENCE_INTERVAL) return html``;
    const rows = scheduleToRows(s);
    const help = describeWindow(rows, this._unresolvableEnds(rows));
    const patch = (next: ScheduleRows) =>
      this._emitChanged(rowsToSchedule(next));
    const bothBounded =
      rows.start.mode !== SCHEDULE_BOUND_MODE_NONE &&
      rows.finish.mode !== SCHEDULE_BOUND_MODE_NONE;
    return html`
      ${this._renderWindowRow("start", rows.start, help.start, (row) =>
        patch({ ...rows, start: row }),
      )}
      ${this._renderWindowRow("finish", rows.finish, help.finish, (row) =>
        patch({ ...rows, finish: row }),
      )}
      ${bothBounded ? this._renderAnchorRow(rows, patch) : ""}
    `;
  }

  /** Blocks Save when the window describes no time at all — both Start and
   * Finish unbounded. Interval has no window, so it is exempt. */
  private _canSave(): boolean {
    const s = this.schedule;
    if (s.recurrence === SCHEDULE_RECURRENCE_INTERVAL) return true;
    return describeWindow(scheduleToRows(s)).valid;
  }

  /** One bordered card: a small-caps heading (also the label for whatever
   * unlabeled control sits directly under it, e.g. the recurrence select
   * and the zone picker's radios) plus its body. */
  private _renderSection(titleKey: string, body: TemplateResult) {
    return html`
      <div class="sect-card">
        <h4>
          ${localize(
            `panels.schedules.sections.${titleKey}`,
            this.hass.language,
          )}
        </h4>
        ${body}
      </div>
    `;
  }

  /** The read-only sentence restating the whole schedule — same wording as
   * the one heading this schedule's card in the list view. Built purely
   * from the stored schedule (../common/schedule-summary.ts), never from
   * live bucket/weather state. */
  private _renderSummary() {
    const summary = summarizeSchedule(this.schedule, this.hass.language);
    return html`
      <div class="summary ${summary.isError ? "is-error" : ""}">
        ${summary.text}
      </div>
    `;
  }

  private _renderSeasonSection() {
    const s = this.schedule;
    const lang = this.hass.language;
    return html`
      <div class="field">
        <label>${localize("panels.schedules.season.label", lang)}</label>
        <div class="rowfields">
          <input
            type="date"
            .value="${s.start_date || ""}"
            @change=${(e: Event) =>
              this._emitChanged({
                start_date: (e.target as HTMLInputElement).value || undefined,
              })}
          />
          <span class="suffix"
            >${localize("panels.schedules.season.to", lang)}</span
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
        <span class="field-help"
          >${localize("panels.schedules.season.note", lang)}</span
        >
      </div>
    `;
  }

  render(): TemplateResult {
    if (!this.hass || !this.schedule) return html``;
    const s = this.schedule;
    const lang = this.hass.language;

    return html`
      <ha-dialog open @closed=${this._cancel}>
        <div slot="heading" class="dialog-heading-row">
          <span>${this.heading}</span>
          <label class="enabled-toggle">
            <input
              type="checkbox"
              ?checked="${s.enabled}"
              @change=${(e: Event) =>
                this._emitChanged({
                  enabled: (e.target as HTMLInputElement).checked,
                })}
            />
            ${localize("panels.schedules.fields.enabled", lang)}
          </label>
        </div>
        <div class="dialog-content">
          ${this._renderSummary()}

          <div class="field">
            <label>${localize("panels.schedules.fields.name", lang)}</label>
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

          ${this._renderSection(
            "when",
            html`
              <div class="field">
                <select
                  aria-label="${localize(
                    "panels.schedules.fields.recurrence",
                    lang,
                  )}"
                  @change=${(e: Event) =>
                    this._emitChanged({
                      recurrence: (e.target as HTMLSelectElement).value,
                    })}
                >
                  ${SCHEDULE_RECURRENCES.map(
                    (r) => html`
                      <option value="${r}" ?selected="${s.recurrence === r}">
                        ${recurrenceLabel(r, lang)}
                      </option>
                    `,
                  )}
                </select>
              </div>
              ${this._renderRecurrenceFields()}
              <div class="when-row">
                <div class="when-rows-col">${this._renderWindowRows()}</div>
                <si-run-window-dial
                  .hass="${this.hass}"
                  .rows="${scheduleToRows(s)}"
                  .recurrence="${s.recurrence}"
                  .intervalHours="${s.interval_hours}"
                  .intervalStartTime="${s.start_time}"
                  .nominalDemandSeconds="${s.nominal_demand_seconds ?? 0}"
                ></si-run-window-dial>
              </div>
            `,
          )}
          ${this._renderSection("zones", this._renderZonePicker())}
          ${this._renderSection("season", this._renderSeasonSection())}
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
          ?disabled="${!this._canSave()}"
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
        .field label {
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
        /* Dialog heading: the title plus the Enabled toggle (GitLab #30) —
           it reads as a property of the schedule, not of the date range it
           used to sit beside. */
        .dialog-heading-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          width: 100%;
        }
        .enabled-toggle {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          font-weight: 400;
          color: var(--secondary-text-color);
          cursor: pointer;
        }
        .enabled-toggle input[type="checkbox"] {
          width: 16px;
          height: 16px;
          accent-color: var(--primary-color);
        }
        /* The read-only summary sentence (GitLab #30): describes the
           schedule's own configuration only, never live bucket/weather
           state — see schedule-summary.ts. */
        .summary {
          border-left: 3px solid var(--primary-color);
          background: color-mix(in srgb, var(--primary-color) 7%, transparent);
          border-radius: 0 8px 8px 0;
          padding: 11px 14px;
          font-size: 0.90625rem;
          line-height: 1.6;
          margin-bottom: 18px;
          color: var(--primary-text-color);
        }
        .summary.is-error {
          border-left-color: var(--error-color, #db4437);
          background: color-mix(
            in srgb,
            var(--error-color, #db4437) 8%,
            transparent
          );
        }
        /* WHEN/ZONES/SEASON cards (GitLab #30): the heading is small-caps
           and doubles as the label for whatever unlabeled control sits
           directly under it. */
        .sect-card {
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 10px;
          padding: 14px 14px 2px;
          margin-bottom: 14px;
        }
        .sect-card > h4 {
          margin: 0 0 12px;
          font-size: 0.71875rem;
          letter-spacing: 0.09em;
          text-transform: uppercase;
          color: var(--secondary-text-color);
          font-weight: 500;
        }
        .rowfields {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
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
        /* Start/Finish/pinned-end rows (GitLab #29): a mode select plus at
           most one stepper, all inline, so the pair reads as one control
           rather than a stack of unrelated fields. */
        .window-row {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
        }
        .window-row > label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--secondary-text-color);
          min-width: 44px;
        }
        .window-row select,
        .window-row input[type="time"],
        .window-row input[type="number"] {
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 1rem;
          font-family: inherit;
          box-sizing: border-box;
        }
        .window-row input[type="number"] {
          width: 76px;
        }
        /* Part of the row rather than chrome, so these read as primary text
           rather than a muted label. */
        .row-inline {
          color: var(--primary-text-color);
          font-size: 0.9375rem;
        }
        /* Help is a child of its row: indented, with an arrow glyph in the
           gap pointing back up at the control it explains. */
        .window-row-help {
          display: flex;
          align-items: baseline;
          gap: 6px;
          padding-left: 20px;
          margin-top: -4px;
        }
        .help-arrow {
          opacity: 0.5;
        }
        .window-row-help .help-text {
          font-size: 0.8125rem;
          line-height: 1.35;
          color: var(--secondary-text-color);
        }
        .window-row-help.is-error .help-text {
          color: var(--error-color, #db4437);
        }
        /* Amber, not red: an unreachable bearing still saves and the backend
           still accepts it — the schedule just will not behave the way the
           row reads. See describeWindow's unresolvable handling. */
        .window-row-help.is-warning .help-text {
          color: var(--warning-color, #ffa600);
        }
        /* Two-column layout inside the WHEN card (GitLab #31): the
           Start/Finish/pinned-end rows on the left, the run-window dial in
           a fixed-width right column, collapsing to one column on narrow
           dialogs. */
        .when-row {
          display: flex;
          flex-wrap: wrap;
          gap: 16px;
          align-items: flex-start;
        }
        .when-rows-col {
          flex: 1 1 240px;
          display: flex;
          flex-direction: column;
          gap: 14px;
          min-width: 0;
        }
        .when-row si-run-window-dial {
          flex: 0 0 156px;
        }
      `,
    ];
  }
}
