import { localize } from "../../localize/localize";
import {
  SCHEDULE_RECURRENCE_WEEKLY,
  SCHEDULE_RECURRENCE_MONTHLY,
  SCHEDULE_RECURRENCE_INTERVAL,
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_ANCHOR_FINISH,
} from "../const";
import {
  scheduleToRows,
  DEFAULT_AZIMUTH,
  EndRow,
  ScheduleWindowFields,
} from "./schedule-rows";

/**
 * The subset of a schedule this module reads to build the read-only summary
 * sentence. Declared locally rather than imported from
 * si-schedule-dialog.ts, matching schedule-rows.ts's own zero-dependency-on-
 * the-rendering-layer convention.
 */
export interface SummarySchedule extends ScheduleWindowFields {
  recurrence: string;
  zones: string | string[];
  days_of_week?: string[];
  day_of_month?: number;
  interval_hours?: number;
}

export interface ScheduleSummary {
  text: string;
  /** True only when the schedule has neither a start nor a finish bound
   * (and isn't interval, which has no window) — the one combination that
   * describes no time at all. Mirrors describeWindow's `valid` flag. */
  isError: boolean;
}

/** A configuration that makes the schedule unable to do anything, in the
 * order they are reported. Each maps to `panels.schedules.summary.<key>`. */
export type ScheduleProblem = "no_days" | "no_window" | "no_zones";

/**
 * The reason this schedule can never do anything, or null if it can.
 *
 * The single source of truth for that question: the dialog's Save button and
 * the summary sentence both ask it here, so the button cannot be enabled
 * while the sentence says the schedule never runs, or the reverse. Every one
 * of these saved happily before — the schedule was accepted, listed, and
 * shown as enabled, and simply never watered.
 *
 * Reported "when" before "what", since a schedule with no time at all is
 * broken more fundamentally than one with a time and nothing to water:
 *
 *  - `no_days` — weekly with no weekday ticked. `_recurrence_day_matches`
 *    answers `any([])`, false for every one of the 367 candidates
 *    `_next_governing_time` tries. This is the state a schedule is in the
 *    MOMENT its recurrence is switched to weekly, since nothing populates
 *    `days_of_week`, so it is the default path rather than an edge case.
 *    Absent and empty are the same condition.
 *  - `no_window` — neither Start nor Finish bounded, which describes no time
 *    whatsoever. Interval is exempt: it has no window, it free-runs.
 *  - `no_zones` — "specific zones" with none ticked. This one stores an
 *    empty LIST, which `normalize_zone_selection` returns as `[]` rather
 *    than the `None` that means "all", so the run targets nothing and
 *    waters nothing. Applies to interval too, which has zones like any
 *    other recurrence.
 *
 * A missing NAME is deliberately not here. It blocks saving (see the
 * dialog's `_canSave`) but it is not a behavioural fault, and this function
 * also feeds the read-only sentence heading every card in the list view —
 * where flagging an unnamed schedule as broken would misdescribe it.
 */
export function scheduleProblem(s: SummarySchedule): ScheduleProblem | null {
  if (
    s.recurrence === SCHEDULE_RECURRENCE_WEEKLY &&
    (s.days_of_week || []).length === 0
  ) {
    return "no_days";
  }
  if (s.recurrence !== SCHEDULE_RECURRENCE_INTERVAL) {
    const rows = scheduleToRows(s);
    if (
      rows.start.mode === SCHEDULE_BOUND_MODE_NONE &&
      rows.finish.mode === SCHEDULE_BOUND_MODE_NONE
    ) {
      return "no_window";
    }
  }
  if (Array.isArray(s.zones) && s.zones.length === 0) return "no_zones";
  return null;
}

/**
 * Builds the plain-language sentence restating a schedule end to end: the
 * summary at the top of the dialog and the one heading each card in the
 * schedule list are both this same sentence, so there is only
 * one place that can get the wording wrong.
 *
 * Deliberately describes the schedule's own configuration only — recurrence,
 * zones, and the Start/Finish window (../common/schedule-rows.ts) — never
 * live bucket/weather state. A schedule is a long-lived object; a sentence
 * that changed because tonight's forecast changed would be describing
 * something the user never configured.
 */
export function summarizeSchedule(
  s: SummarySchedule,
  language: string,
): ScheduleSummary {
  const problem = scheduleProblem(s);
  if (problem) {
    return {
      // `no_window` keeps the key it has always had; the sentence is
      // unchanged for the case that already reported it.
      text: localize(
        `panels.schedules.summary.${problem === "no_window" ? "invalid" : problem}`,
        language,
      ),
      isError: true,
    };
  }

  const zones = zonesText(s.zones, language);
  const recurrence = recurrenceText(s, language);

  if (s.recurrence === SCHEDULE_RECURRENCE_INTERVAL) {
    const watering = localize(
      "panels.schedules.summary.watering",
      language,
      "zones",
      zones,
    );
    return { text: `${recurrence}, ${watering}.`, isError: false };
  }

  // Both-unbounded is already handled above, by scheduleProblem.
  const rows = scheduleToRows(s);
  const startBounded = rows.start.mode !== SCHEDULE_BOUND_MODE_NONE;
  const finishBounded = rows.finish.mode !== SCHEDULE_BOUND_MODE_NONE;

  const watering = localize(
    "panels.schedules.summary.watering",
    language,
    "zones",
    zones,
  );

  let windowText: string;
  if (!startBounded) {
    windowText = localize(
      "panels.schedules.summary.finish_only",
      language,
      "when",
      describeEnd(rows.finish, language),
    );
  } else if (!finishBounded) {
    windowText = localize(
      "panels.schedules.summary.start_only",
      language,
      "when",
      describeEnd(rows.start, language),
    );
  } else if (rows.anchor === SCHEDULE_ANCHOR_FINISH) {
    windowText = localize(
      "panels.schedules.summary.anchor_finish",
      language,
      "finish",
      describeEnd(rows.finish, language),
      "start",
      describeEnd(rows.start, language),
    );
  } else {
    windowText = localize(
      "panels.schedules.summary.anchor_start",
      language,
      "start",
      describeEnd(rows.start, language),
      "finish",
      describeEnd(rows.finish, language),
    );
  }

  return {
    text: `${recurrence}, ${watering}, ${windowText}.`,
    isError: false,
  };
}

function zonesText(zones: string | string[], language: string): string {
  if (zones === "all" || !Array.isArray(zones)) {
    // A dedicated lowercase key rather than the fields-level "All zones"
    // (used capitalized on its own line elsewhere): this string sits
    // mid-sentence ("...watering all zones, finishing...") where a
    // capital A would misread as a typo.
    return localize("panels.schedules.summary.zones_all", language);
  }
  return localize(
    "panels.schedules.summary.zones_some",
    language,
    "count",
    zones.length,
  );
}

function recurrenceText(s: SummarySchedule, language: string): string {
  switch (s.recurrence) {
    case SCHEDULE_RECURRENCE_WEEKLY: {
      const days = (s.days_of_week || [])
        .map((d) => localize(`panels.schedules.days.${d}`, language))
        .join(", ");
      return localize(
        "panels.schedules.summary.recurrence_weekly",
        language,
        "days",
        days,
      );
    }
    case SCHEDULE_RECURRENCE_MONTHLY:
      return localize(
        "panels.schedules.summary.recurrence_monthly",
        language,
        "day",
        s.day_of_month || 1,
      );
    case SCHEDULE_RECURRENCE_INTERVAL: {
      const hours = s.interval_hours || 24;
      if (s.start_time) {
        return localize(
          "panels.schedules.summary.recurrence_interval_at",
          language,
          "hours",
          hours,
          "time",
          s.start_time,
        );
      }
      return localize(
        "panels.schedules.summary.recurrence_interval",
        language,
        "hours",
        hours,
      );
    }
    default:
      return localize("panels.schedules.summary.recurrence_daily", language);
  }
}

/** One end of the window in prose. Never carries its own leading
 * preposition ("at"/"by") — that lives in the sentence template that embeds
 * it, so the same description slots into "starting at X", "finishing at X",
 * "never before X", etc. without repeating "at" oddly. */
function describeEnd(row: EndRow, language: string): string {
  switch (row.mode) {
    case SCHEDULE_BOUND_MODE_TIME:
      return row.time ?? "";
    case SCHEDULE_BOUND_MODE_SUNRISE:
    case SCHEDULE_BOUND_MODE_SUNSET: {
      const event = localize(`panels.schedules.summary.${row.mode}`, language);
      const offset = row.offset ?? 0;
      if (offset === 0) return event;
      const key =
        offset < 0
          ? "panels.schedules.summary.offset_before"
          : "panels.schedules.summary.offset_after";
      return localize(
        key,
        language,
        "minutes",
        Math.abs(offset),
        "event",
        event,
      );
    }
    case SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH:
      return localize(
        "panels.schedules.summary.at_azimuth",
        language,
        "degrees",
        row.azimuth ?? DEFAULT_AZIMUTH,
      );
    default:
      return "";
  }
}
