import {
  SCHEDULE_ANCHOR_FINISH,
  SCHEDULE_ANCHOR_START,
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_RECURRENCE_INTERVAL,
} from "../const";

/** A schedule as the store keeps it: a recurrence plus two bounded ends. */
export interface StoredSchedule {
  recurrence?: string;
  start_mode?: string;
  start_time?: string;
  start_offset?: number;
  start_azimuth?: number;
  finish_mode?: string;
  finish_time?: string;
  finish_offset?: number;
  finish_azimuth?: number;
  anchor?: string;
  [key: string]: unknown;
}

/**
 * A schedule as the dialog edits it: one recurrence-or-sun-event picker, one
 * time, one anchor. Narrower than what the store holds, which is why the two
 * functions below exist.
 */
export interface EditableSchedule {
  type: string;
  time?: string;
  offset_minutes?: number;
  azimuth_angle?: number;
  time_anchor?: string;
  [key: string]: unknown;
}

const SOLAR_MODES = [
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
];

/** Which end of the window a stored schedule is pinned to. */
export function governingEnd(s: StoredSchedule): string {
  const startBounded =
    (s.start_mode ?? SCHEDULE_BOUND_MODE_NONE) !== SCHEDULE_BOUND_MODE_NONE;
  const finishBounded =
    (s.finish_mode ?? SCHEDULE_BOUND_MODE_NONE) !== SCHEDULE_BOUND_MODE_NONE;
  if (startBounded && finishBounded)
    return s.anchor === SCHEDULE_ANCHOR_START
      ? SCHEDULE_ANCHOR_START
      : SCHEDULE_ANCHOR_FINISH;
  return finishBounded ? SCHEDULE_ANCHOR_FINISH : SCHEDULE_ANCHOR_START;
}

/**
 * Collapse the stored two-bound shape onto the single time source the dialog
 * edits, so the controls keep working against a schedule the store keeps in a
 * richer form than they can express. Only the governing bound is surfaced.
 */
export function toEditable(s: StoredSchedule): EditableSchedule {
  const end = governingEnd(s);
  const mode = (
    end === SCHEDULE_ANCHOR_FINISH ? s.finish_mode : s.start_mode
  ) as string | undefined;
  const time = end === SCHEDULE_ANCHOR_FINISH ? s.finish_time : s.start_time;
  const offset =
    end === SCHEDULE_ANCHOR_FINISH ? s.finish_offset : s.start_offset;
  const azimuth =
    end === SCHEDULE_ANCHOR_FINISH ? s.finish_azimuth : s.start_azimuth;
  const solar = mode !== undefined && SOLAR_MODES.includes(mode);
  const interval = s.recurrence === SCHEDULE_RECURRENCE_INTERVAL;
  return {
    ...s,
    type: interval
      ? SCHEDULE_RECURRENCE_INTERVAL
      : solar
        ? (mode as string)
        : (s.recurrence ?? "daily"),
    // An interval schedule keeps its own start_time anchor, which is the same
    // stored key a time-bounded Start uses; only the latter is a window bound,
    // so an interval must not have it read back as one.
    time: interval ? undefined : time,
    offset_minutes: solar ? offset : undefined,
    azimuth_angle:
      mode === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH ? azimuth : undefined,
    time_anchor: end,
  };
}

/**
 * The inverse: write the edited time source onto the governing bound and leave
 * the other end unbounded, which is the shape the storage migration produces
 * for every existing schedule.
 *
 * One bound in, one bound out: the dialog has a single time source, so saving
 * through it cannot express a second bound and does not try to preserve one.
 * Nothing reachable from here creates a two-bounded schedule, so there is none
 * to lose.
 */
export function toStored(s: EditableSchedule): StoredSchedule {
  const out: StoredSchedule = { ...s };
  delete out.type;
  delete out.time;
  delete out.offset_minutes;
  delete out.account_for_duration;
  delete out.azimuth_angle;
  delete out.time_anchor;

  if (s.type === SCHEDULE_RECURRENCE_INTERVAL) {
    out.recurrence = SCHEDULE_RECURRENCE_INTERVAL;
    // An interval has no time of day and therefore no window. Switching an
    // existing schedule to interval must clear the bounds it used to carry, or
    // it is stored as an interval that still reads as bounded at one end.
    // start_time is the exception: on an interval that key is its own clock
    // anchor, which the dialog still edits.
    for (const k of [
      "start_mode",
      "start_offset",
      "start_azimuth",
      "finish_mode",
      "finish_time",
      "finish_offset",
      "finish_azimuth",
      "anchor",
    ])
      delete out[k];
    return out;
  }

  const solar = SOLAR_MODES.includes(s.type);
  const end =
    s.time_anchor === SCHEDULE_ANCHOR_FINISH
      ? SCHEDULE_ANCHOR_FINISH
      : SCHEDULE_ANCHOR_START;
  const other =
    end === SCHEDULE_ANCHOR_START
      ? SCHEDULE_ANCHOR_FINISH
      : SCHEDULE_ANCHOR_START;

  // A sun-relative time of day is now a bound mode rather than a recurrence,
  // so it always leaves the recurrence daily.
  out.recurrence = solar ? "daily" : s.type;
  out[`${end}_mode`] = solar ? s.type : SCHEDULE_BOUND_MODE_TIME;
  out[`${other}_mode`] = SCHEDULE_BOUND_MODE_NONE;
  out.anchor = end;
  if (solar) {
    out[`${end}_offset`] = s.offset_minutes ?? 0;
    if (s.type === SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH)
      out[`${end}_azimuth`] = s.azimuth_angle ?? 90;
    delete out[`${end}_time`];
  } else {
    out[`${end}_time`] = s.time ?? "06:00";
    delete out[`${end}_offset`];
    delete out[`${end}_azimuth`];
  }
  // The unbounded end's stored values would be read against a "none" mode.
  // Drop them rather than leave a bound that no longer applies.
  delete out[`${other}_offset`];
  delete out[`${other}_azimuth`];
  delete out[`${other}_time`];
  return out;
}
