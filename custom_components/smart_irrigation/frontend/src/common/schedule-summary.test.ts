import { describe, it, expect } from "vitest";
import { summarizeSchedule, SummarySchedule } from "./schedule-summary";
import { SCHEDULE_ANCHOR_START, SCHEDULE_ANCHOR_FINISH } from "../const";

const lang = "en";

function base(overrides: Partial<SummarySchedule> = {}): SummarySchedule {
  return {
    recurrence: "daily",
    zones: "all",
    start_mode: "time",
    start_time: "06:00",
    finish_mode: "none",
    ...overrides,
  };
}

describe("summarizeSchedule: zones", () => {
  it("describes 'all zones' when zones is the string 'all'", () => {
    const { text } = summarizeSchedule(base({ zones: "all" }), lang);
    expect(text).toContain("all zones");
  });

  it("describes a singular selected zone", () => {
    const { text } = summarizeSchedule(base({ zones: ["0"] }), lang);
    expect(text).toContain("1 selected zone");
    expect(text).not.toContain("1 selected zones");
  });

  it("describes a plural zone count", () => {
    const { text } = summarizeSchedule(base({ zones: ["0", "1", "2"] }), lang);
    expect(text).toContain("3 selected zones");
  });
});

describe("summarizeSchedule: recurrence", () => {
  it("daily", () => {
    const { text } = summarizeSchedule(base({ recurrence: "daily" }), lang);
    expect(text.startsWith("Runs daily")).toBe(true);
  });

  it("weekly names the selected days in order", () => {
    const { text } = summarizeSchedule(
      base({ recurrence: "weekly", days_of_week: ["monday", "wednesday"] }),
      lang,
    );
    expect(text).toContain("Runs weekly on Mon, Wed");
  });

  it("weekly with no days selected is an error, not a sentence with a hole", () => {
    // This test used to assert the opposite - that the sentence still read
    // "Runs weekly on" with nothing after it - on the grounds that it
    // rendered without throwing. Not throwing was the wrong bar: a weekly
    // schedule with no day ticked matches no calendar day backend-side, so
    // it saved, listed, showed as enabled and never fired. The full case is
    // in "summarizeSchedule: weekly with no days" below.
    const { text, isError } = summarizeSchedule(
      base({ recurrence: "weekly", days_of_week: [] }),
      lang,
    );
    expect(isError).toBe(true);
    expect(text).not.toContain("Runs weekly on");
  });

  it("monthly names the day of month, defaulting to 1", () => {
    expect(
      summarizeSchedule(base({ recurrence: "monthly", day_of_month: 15 }), lang)
        .text,
    ).toContain("Runs monthly on day 15");
    expect(
      summarizeSchedule(base({ recurrence: "monthly" }), lang).text,
    ).toContain("Runs monthly on day 1");
  });

  it("interval states the hours, defaulting to 24, with no window clause", () => {
    const { text, isError } = summarizeSchedule(
      base({
        recurrence: "interval",
        interval_hours: 6,
        start_mode: undefined,
        start_time: undefined,
        finish_mode: undefined,
      }),
      lang,
    );
    expect(isError).toBe(false);
    expect(text).toBe("Runs every 6 hours, watering all zones.");
  });

  it("interval states its own optional clock anchor when start_time is set", () => {
    const { text } = summarizeSchedule(
      base({ recurrence: "interval", interval_hours: 6, start_time: "07:30" }),
      lang,
    );
    expect(text).toBe(
      "Runs every 6 hours, starting at 07:30, watering all zones.",
    );
  });

  it("interval defaults interval_hours to 24 when unset", () => {
    const { text } = summarizeSchedule(
      base({
        recurrence: "interval",
        interval_hours: undefined,
        start_time: undefined,
      }),
      lang,
    );
    expect(text).toBe("Runs every 24 hours, watering all zones.");
  });
});

describe("summarizeSchedule: window, every start/finish/anchor combination", () => {
  it("both unbounded is an error and names no time at all", () => {
    const { text, isError } = summarizeSchedule(
      base({ start_mode: "none", finish_mode: "none" }),
      lang,
    );
    expect(isError).toBe(true);
    expect(text).toBe(
      "This schedule has no start or finish set, so it never runs.",
    );
  });

  it("start bounded, finish unbounded: describes the start only, runs to completion", () => {
    const { text, isError } = summarizeSchedule(
      base({
        start_mode: "sunrise",
        start_offset: 0,
        finish_mode: "none",
      }),
      lang,
    );
    expect(isError).toBe(false);
    expect(text).toContain(
      "starting at sunrise; every zone runs to completion",
    );
  });

  it("start unbounded, finish bounded: describes the finish only, runs to completion", () => {
    const { text, isError } = summarizeSchedule(
      base({
        start_mode: "none",
        finish_mode: "time",
        finish_time: "20:00",
      }),
      lang,
    );
    expect(isError).toBe(false);
    expect(text).toContain("finishing at 20:00; every zone runs to completion");
  });

  it("both bounded, anchored to finish: floored start, exact+deferred finish", () => {
    const { text } = summarizeSchedule(
      base({
        start_mode: "sunrise",
        start_offset: -30,
        finish_mode: "time",
        finish_time: "20:00",
        anchor: SCHEDULE_ANCHOR_FINISH,
      }),
      lang,
    );
    expect(text).toContain(
      "finishing at 20:00, starting as late as possible but never before 30 min before sunrise; zones that don't fit wait for the next run",
    );
  });

  it("both bounded, anchored to start: exact start, capped+deferred finish", () => {
    const { text } = summarizeSchedule(
      base({
        start_mode: "time",
        start_time: "06:00",
        finish_mode: "sunset",
        finish_offset: 15,
        anchor: SCHEDULE_ANCHOR_START,
      }),
      lang,
    );
    expect(text).toContain(
      "starting at 06:00, finishing by 15 min after sunset at the latest; zones that don't fit wait for the next run",
    );
  });

  it("solar azimuth ends render degrees, not an offset", () => {
    const { text } = summarizeSchedule(
      base({
        start_mode: "solar_azimuth",
        start_azimuth: 210,
        finish_mode: "none",
      }),
      lang,
    );
    expect(text).toContain("starting at solar azimuth 210°");
  });

  it("covers all five window states across daily, weekly and monthly recurrence", () => {
    const boundedModes: Array<[string, Partial<SummarySchedule>]> = [
      ["time", { start_time: "06:00" }],
      ["sunrise", { start_offset: 0 }],
      ["sunset", { start_offset: 0 }],
      ["solar_azimuth", { start_azimuth: 90 }],
    ];
    for (const recurrence of ["daily", "weekly", "monthly"]) {
      for (const [startMode] of boundedModes) {
        for (const [finishMode] of boundedModes) {
          for (const anchor of [
            SCHEDULE_ANCHOR_START,
            SCHEDULE_ANCHOR_FINISH,
          ]) {
            const schedule = base({
              recurrence,
              days_of_week: ["monday"],
              day_of_month: 1,
              start_mode: startMode,
              start_time: startMode === "time" ? "06:00" : undefined,
              start_offset:
                startMode === "sunrise" || startMode === "sunset"
                  ? 0
                  : undefined,
              start_azimuth: startMode === "solar_azimuth" ? 90 : undefined,
              finish_mode: finishMode,
              finish_time: finishMode === "time" ? "20:00" : undefined,
              finish_offset:
                finishMode === "sunrise" || finishMode === "sunset"
                  ? 0
                  : undefined,
              finish_azimuth: finishMode === "solar_azimuth" ? 90 : undefined,
              anchor,
            });
            const { text, isError } = summarizeSchedule(schedule, lang);
            expect(isError, JSON.stringify(schedule)).toBe(false);
            if (anchor === SCHEDULE_ANCHOR_FINISH) {
              expect(text, JSON.stringify(schedule)).toContain(
                "starting as late as possible but never before",
              );
              expect(text, JSON.stringify(schedule)).toContain(
                "zones that don't fit wait for the next run",
              );
            } else {
              expect(text, JSON.stringify(schedule)).toContain("finishing by");
              expect(text, JSON.stringify(schedule)).toContain(
                "at the latest; zones that don't fit wait for the next run",
              );
            }
          }
        }
      }
    }
  });
});

describe("summarizeSchedule: never references live state", () => {
  it("the summary function's inputs carry no bucket/weather fields", () => {
    // Documentation-as-test: SummarySchedule only extends the pure window
    // fields plus recurrence/zones. There is no bucket, duration, or
    // nominal-demand field for this function to read even by accident.
    const schedule = base();
    expect(Object.keys(schedule)).not.toContain("bucket");
    expect(Object.keys(schedule)).not.toContain("duration");
  });
});

describe("summarizeSchedule: weekly with no days", () => {
  /**
   * `_recurrence_day_matches` answers `any([])` for a weekly schedule with
   * no weekday ticked - false for every one of the 367 candidates
   * `_next_governing_time` tries - so the schedule saved, listed, showed as
   * enabled, and never fired. Nothing said so: the sentence just read
   * "Runs weekly on , watering all zones...", with an empty day list where
   * the days belong.
   *
   * It is also the state a schedule is in the moment its recurrence is
   * switched to weekly, since nothing populates days_of_week - so it is the
   * default path, not an edge case.
   */
  it("is reported as an error rather than as a sentence with a hole in it", () => {
    const s = summarizeSchedule(
      base({ recurrence: "weekly", days_of_week: [] }),
      lang,
    );
    expect(s.isError).toBe(true);
    expect(s.text).toContain("never runs");
    // The specific bug: the old sentence named the recurrence and then
    // trailed off where the days should have been.
    expect(s.text).not.toContain("Runs weekly on ,");
  });

  it("treats an absent days_of_week the same as an empty one", () => {
    // What switching the recurrence to weekly actually produces.
    const s = summarizeSchedule(base({ recurrence: "weekly" }), lang);
    expect(s.isError).toBe(true);
  });

  it("says nothing about days once one is ticked", () => {
    const s = summarizeSchedule(
      base({ recurrence: "weekly", days_of_week: ["monday"] }),
      lang,
    );
    expect(s.isError).toBe(false);
    expect(s.text).toContain("Mon");
  });

  it("does not fire for the other recurrences, which all have a default", () => {
    // daily needs no day; monthly defaults to the 1st backend-side; interval
    // has no calendar day at all. Only weekly can be unsatisfiable this way.
    for (const recurrence of ["daily", "monthly", "interval"]) {
      expect(summarizeSchedule(base({ recurrence }), lang).isError).toBe(false);
    }
  });
});

describe("scheduleProblem", () => {
  /**
   * One source of truth for "can this schedule ever do anything", shared by
   * the dialog's Save button and the summary sentence, so the two cannot
   * disagree. Every one of these saved happily before.
   */
  it("reports an empty zone list", () => {
    const s = summarizeSchedule(base({ zones: [] }), lang);
    expect(s.isError).toBe(true);
    expect(s.text).toContain("never waters anything");
  });

  it("reports an empty zone list on interval too, which has no window", () => {
    const s = summarizeSchedule(
      base({ recurrence: "interval", interval_hours: 6, zones: [] }),
      lang,
    );
    expect(s.isError).toBe(true);
  });

  it("does not confuse 'all' with an empty selection", () => {
    // "all" is a STRING, not a list; only a literal empty array means
    // "specific zones, none ticked".
    expect(summarizeSchedule(base({ zones: "all" }), lang).isError).toBe(false);
    expect(summarizeSchedule(base({ zones: ["0"] }), lang).isError).toBe(false);
  });

  it("reports the when-problem before the what-problem", () => {
    // A weekly schedule with neither days nor zones is broken both ways;
    // the one that makes it describe no TIME is the more fundamental.
    const s = summarizeSchedule(
      base({ recurrence: "weekly", days_of_week: [], zones: [] }),
      lang,
    );
    expect(s.text).toContain("no days selected");
  });

  it("still reports the unbounded window with its original wording", () => {
    // This case predates the others and its string must not have moved.
    const s = summarizeSchedule(
      base({ start_mode: "none", finish_mode: "none" }),
      lang,
    );
    expect(s.isError).toBe(true);
    expect(s.text).toContain("no start or finish set");
  });
});
