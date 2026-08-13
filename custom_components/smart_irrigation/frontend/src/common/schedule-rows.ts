import {
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_ANCHOR_START,
  SCHEDULE_ANCHOR_FINISH,
} from "../const";

/**
 * Pure mapping between a schedule's Start/Finish window as it is stored
 * (GitLab #27's independent start_mode/start_time/start_offset/
 * start_azimuth/finish_.../anchor fields) and as the dialog's Start/Finish
 * rows render it (GitLab #29): one control per row, whose kind matches the
 * quantity that row's mode carries. No Lit, no DOM, no localize — this
 * module never renders anything and returns semantic help-state keys
 * rather than copy, so the rendering layer owns all text.
 *
 * This is the piece most likely to lose a setting silently when a mode
 * changes, which is why every direction is covered by
 * schedule-rows.test.ts, including a rows -> fields -> rows identity check.
 *
 * The migration that landed #27 was destructive, so this module only ever
 * has to understand the new shape — there is no older layout to translate.
 */

export type BoundMode =
  | typeof SCHEDULE_BOUND_MODE_NONE
  | typeof SCHEDULE_BOUND_MODE_TIME
  | typeof SCHEDULE_BOUND_MODE_SUNRISE
  | typeof SCHEDULE_BOUND_MODE_SUNSET
  | typeof SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH;

export type Anchor =
  | typeof SCHEDULE_ANCHOR_START
  | typeof SCHEDULE_ANCHOR_FINISH;

/**
 * One end of the run's window, in row-shaped form: the mode plus whichever
 * single quantity that mode's row carries. Only one of time/offset/azimuth
 * is ever populated for a given mode — solar_azimuth carries degrees alone
 * (no separate offset), matching the row's one-stepper-per-row layout, and
 * "time" carries an absolute HH:MM rather than an offset because it has no
 * event to offset from.
 */
export interface EndRow {
  mode: BoundMode;
  time?: string; // HH:MM — mode "time" only
  offset?: number; // signed minutes — mode "sunrise" | "sunset" only
  azimuth?: number; // degrees — mode "solar_azimuth" only
}

export interface ScheduleRows {
  start: EndRow;
  finish: EndRow;
  /** Which end the run is pinned to. Only meaningful — and only rendered —
   * when both ends are bounded; carried unconditionally so bounding the
   * second end later doesn't lose a previously chosen anchor. */
  anchor: Anchor;
}

/**
 * The subset of the dialog's Schedule interface (si-schedule-dialog.ts)
 * this module reads and writes. Declared locally, rather than imported,
 * so this module has zero dependency on the rendering layer.
 */
export interface ScheduleWindowFields {
  start_mode?: string;
  start_time?: string;
  start_offset?: number;
  start_azimuth?: number;
  finish_mode?: string;
  finish_time?: string;
  finish_offset?: number;
  finish_azimuth?: number;
  anchor?: string;
}

const DEFAULT_TIME = "06:00";
const DEFAULT_OFFSET = 0;
export const DEFAULT_AZIMUTH = 90;

function isBoundMode(mode: string | undefined): mode is BoundMode {
  return (
    mode === SCHEDULE_BOUND_MODE_NONE ||
    mode === SCHEDULE_BOUND_MODE_TIME ||
    mode === SCHEDULE_BOUND_MODE_SUNRISE ||
    mode === SCHEDULE_BOUND_MODE_SUNSET ||
    mode === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH
  );
}

/** The row a freshly chosen mode starts out as — the sensible default value
 * for whichever quantity that mode carries. Used both to fill in a legacy/
 * missing stored value and to populate a row the instant its mode changes,
 * so the displayed default is never out of sync with what would be saved. */
export function defaultRowForMode(mode: BoundMode): EndRow {
  switch (mode) {
    case SCHEDULE_BOUND_MODE_TIME:
      return { mode, time: DEFAULT_TIME };
    case SCHEDULE_BOUND_MODE_SUNRISE:
    case SCHEDULE_BOUND_MODE_SUNSET:
      return { mode, offset: DEFAULT_OFFSET };
    case SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH:
      return { mode, azimuth: DEFAULT_AZIMUTH };
    default:
      return { mode: SCHEDULE_BOUND_MODE_NONE };
  }
}

function fieldsToEndRow(
  mode: string | undefined,
  time: string | undefined,
  offset: number | undefined,
  azimuth: number | undefined,
): EndRow {
  const m: BoundMode = isBoundMode(mode) ? mode : SCHEDULE_BOUND_MODE_NONE;
  const row = defaultRowForMode(m);
  if (m === SCHEDULE_BOUND_MODE_TIME && time !== undefined) row.time = time;
  if (
    (m === SCHEDULE_BOUND_MODE_SUNRISE || m === SCHEDULE_BOUND_MODE_SUNSET) &&
    offset !== undefined
  )
    row.offset = offset;
  if (m === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH && azimuth !== undefined)
    row.azimuth = azimuth;
  return row;
}

function endRowToFields(row: EndRow): {
  mode: BoundMode;
  time?: string;
  offset?: number;
  azimuth?: number;
} {
  return {
    mode: row.mode,
    time:
      row.mode === SCHEDULE_BOUND_MODE_TIME
        ? (row.time ?? DEFAULT_TIME)
        : undefined,
    offset:
      row.mode === SCHEDULE_BOUND_MODE_SUNRISE ||
      row.mode === SCHEDULE_BOUND_MODE_SUNSET
        ? (row.offset ?? DEFAULT_OFFSET)
        : undefined,
    azimuth:
      row.mode === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH
        ? (row.azimuth ?? DEFAULT_AZIMUTH)
        : undefined,
  };
}

/** Schedule fields -> rows. */
export function scheduleToRows(s: ScheduleWindowFields): ScheduleRows {
  return {
    start: fieldsToEndRow(
      s.start_mode,
      s.start_time,
      s.start_offset,
      s.start_azimuth,
    ),
    finish: fieldsToEndRow(
      s.finish_mode,
      s.finish_time,
      s.finish_offset,
      s.finish_azimuth,
    ),
    anchor:
      s.anchor === SCHEDULE_ANCHOR_START
        ? SCHEDULE_ANCHOR_START
        : SCHEDULE_ANCHOR_FINISH,
  };
}

/** Rows -> schedule fields. Always returns every field (some as `undefined`)
 * so applying the result as a patch clears whatever the previous mode left
 * behind — e.g. switching Start from "solar_azimuth" to "time" must drop
 * the stale start_azimuth, not leave it hanging off an unrelated mode. */
export function rowsToSchedule(rows: ScheduleRows): ScheduleWindowFields {
  const start = endRowToFields(rows.start);
  const finish = endRowToFields(rows.finish);
  return {
    start_mode: start.mode,
    start_time: start.time,
    start_offset: start.offset,
    start_azimuth: start.azimuth,
    finish_mode: finish.mode,
    finish_time: finish.time,
    finish_offset: finish.offset,
    finish_azimuth: finish.azimuth,
    anchor: rows.anchor,
  };
}

/**
 * Help-state keys for the Start/Finish help cells (GitLab #29's table).
 * These are semantic tokens, not copy — the rendering layer maps each to
 * `panels.schedules.help.<key>` via localize().
 */
export type HelpKey =
  | "error"
  | "demand_open"
  | "exact"
  | "demand_floored"
  | "exact_deferred"
  | "demand_capped_deferred";

export interface WindowHelp {
  start: HelpKey;
  finish: HelpKey;
  /** False only when both ends are unbounded — the one combination that
   * describes no time at all and must block saving. */
  valid: boolean;
}

/**
 * Derive both help cells (and overall validity) from the two rows' bounded
 * state and, when both are bounded, which end is pinned. See GitLab #29's
 * table: "Exact." vs "Set by demand, but never before this." is the pair
 * doing the real work, and the "Zones that don't fit are deferred." note
 * always lands on the Finish cell — that's the end the window actually
 * closes on, whether Finish is the exact/pinned end or the flexible one.
 */
export function describeWindow(rows: ScheduleRows): WindowHelp {
  const startBounded = rows.start.mode !== SCHEDULE_BOUND_MODE_NONE;
  const finishBounded = rows.finish.mode !== SCHEDULE_BOUND_MODE_NONE;

  if (!startBounded && !finishBounded) {
    return { start: "error", finish: "error", valid: false };
  }
  if (!startBounded) {
    return { start: "demand_open", finish: "exact", valid: true };
  }
  if (!finishBounded) {
    return { start: "exact", finish: "demand_open", valid: true };
  }
  if (rows.anchor === SCHEDULE_ANCHOR_FINISH) {
    return { start: "demand_floored", finish: "exact_deferred", valid: true };
  }
  return { start: "exact", finish: "demand_capped_deferred", valid: true };
}
