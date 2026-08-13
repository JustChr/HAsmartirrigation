import { describe, it, expect } from "vitest";
import {
  scheduleToRows,
  rowsToSchedule,
  describeWindow,
  isWarningHelp,
  HelpKey,
  defaultRowForMode,
  BoundMode,
  Anchor,
  EndRow,
  ScheduleRows,
} from "./schedule-rows";
import {
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_ANCHOR_START,
  SCHEDULE_ANCHOR_FINISH,
} from "../const";

const ALL_MODES: BoundMode[] = [
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
];
const ALL_ANCHORS: Anchor[] = [SCHEDULE_ANCHOR_START, SCHEDULE_ANCHOR_FINISH];

describe("scheduleToRows", () => {
  it("reads a 'none' end from a missing/undefined mode", () => {
    const rows = scheduleToRows({});
    expect(rows.start).toEqual({ mode: SCHEDULE_BOUND_MODE_NONE });
    expect(rows.finish).toEqual({ mode: SCHEDULE_BOUND_MODE_NONE });
  });

  it("reads a 'time' end, defaulting a missing time to 06:00", () => {
    expect(
      scheduleToRows({ start_mode: "time", start_time: "14:30" }).start,
    ).toEqual({
      mode: "time",
      time: "14:30",
    });
    expect(scheduleToRows({ start_mode: "time" }).start).toEqual({
      mode: "time",
      time: "06:00",
    });
  });

  it("reads sunrise/sunset ends, defaulting a missing offset to 0", () => {
    expect(
      scheduleToRows({ start_mode: "sunrise", start_offset: -15 }).start,
    ).toEqual({ mode: "sunrise", offset: -15 });
    expect(scheduleToRows({ finish_mode: "sunset" }).finish).toEqual({
      mode: "sunset",
      offset: 0,
    });
    // Signed: a positive offset (after the event) round-trips too.
    expect(
      scheduleToRows({ finish_mode: "sunset", finish_offset: 45 }).finish,
    ).toEqual({ mode: "sunset", offset: 45 });
  });

  it("reads a solar_azimuth end, defaulting a missing azimuth to 90 and ignoring any stray offset", () => {
    expect(
      scheduleToRows({
        start_mode: "solar_azimuth",
        start_azimuth: 210,
        start_offset: 30, // stray field from a prior mode — must not leak into the row
      }).start,
    ).toEqual({ mode: "solar_azimuth", azimuth: 210 });
    expect(scheduleToRows({ start_mode: "solar_azimuth" }).start).toEqual({
      mode: "solar_azimuth",
      azimuth: 90,
    });
  });

  it("falls back to 'none' for an unrecognized mode string", () => {
    expect(scheduleToRows({ start_mode: "bogus" }).start).toEqual({
      mode: SCHEDULE_BOUND_MODE_NONE,
    });
  });

  it("defaults anchor to finish unless it is exactly 'start'", () => {
    expect(scheduleToRows({}).anchor).toBe(SCHEDULE_ANCHOR_FINISH);
    expect(scheduleToRows({ anchor: "start" }).anchor).toBe(
      SCHEDULE_ANCHOR_START,
    );
    expect(scheduleToRows({ anchor: "bogus" }).anchor).toBe(
      SCHEDULE_ANCHOR_FINISH,
    );
  });
});

describe("rowsToSchedule", () => {
  it("writes only the field(s) the row's mode owns, clearing the others", () => {
    const patch = rowsToSchedule({
      start: { mode: "sunrise", offset: -20 },
      finish: { mode: "none" },
      anchor: SCHEDULE_ANCHOR_FINISH,
    });
    expect(patch.start_mode).toBe("sunrise");
    expect(patch.start_offset).toBe(-20);
    expect(patch.start_time).toBeUndefined();
    expect(patch.start_azimuth).toBeUndefined();
    expect(patch.finish_mode).toBe("none");
    expect(patch.finish_time).toBeUndefined();
    expect(patch.finish_offset).toBeUndefined();
    expect(patch.finish_azimuth).toBeUndefined();
  });

  it("clears a stale azimuth when a row switches away from solar_azimuth", () => {
    // Simulates: schedule already has start_azimuth on disk, user switches
    // Start to "At sunrise" — the patch must null the azimuth out, not
    // leave it hanging off a mode that no longer uses it.
    const rows: ScheduleRows = {
      start: { mode: "sunrise", offset: 10 },
      finish: { mode: "none" },
      anchor: SCHEDULE_ANCHOR_FINISH,
    };
    const patch = rowsToSchedule(rows);
    expect(patch.start_azimuth).toBeUndefined();
  });
});

describe("defaultRowForMode", () => {
  it("returns the sensible seed value for every mode", () => {
    expect(defaultRowForMode(SCHEDULE_BOUND_MODE_NONE)).toEqual({
      mode: "none",
    });
    expect(defaultRowForMode(SCHEDULE_BOUND_MODE_TIME)).toEqual({
      mode: "time",
      time: "06:00",
    });
    expect(defaultRowForMode(SCHEDULE_BOUND_MODE_SUNRISE)).toEqual({
      mode: "sunrise",
      offset: 0,
    });
    expect(defaultRowForMode(SCHEDULE_BOUND_MODE_SUNSET)).toEqual({
      mode: "sunset",
      offset: 0,
    });
    expect(defaultRowForMode(SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH)).toEqual({
      mode: "solar_azimuth",
      azimuth: 90,
    });
  });
});

/** Every legal EndRow value for a given mode — one representative row per
 * mode, exercising a non-default value so the round trip isn't trivially
 * passing on defaults alone. */
function legalRowsForMode(mode: BoundMode): EndRow[] {
  switch (mode) {
    case SCHEDULE_BOUND_MODE_TIME:
      return [
        { mode, time: "06:00" },
        { mode, time: "23:59" },
        { mode, time: "00:00" },
      ];
    case SCHEDULE_BOUND_MODE_SUNRISE:
    case SCHEDULE_BOUND_MODE_SUNSET:
      return [
        { mode, offset: 0 },
        { mode, offset: -45 },
        { mode, offset: 30 },
      ];
    case SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH:
      return [
        { mode, azimuth: 90 },
        { mode, azimuth: 0 },
        { mode, azimuth: 359 },
      ];
    default:
      return [{ mode: SCHEDULE_BOUND_MODE_NONE }];
  }
}

describe("round trip: rows -> fields -> rows is identity, over every legal combination", () => {
  for (const startMode of ALL_MODES) {
    for (const finishMode of ALL_MODES) {
      for (const anchor of ALL_ANCHORS) {
        for (const start of legalRowsForMode(startMode)) {
          for (const finish of legalRowsForMode(finishMode)) {
            const rows: ScheduleRows = { start, finish, anchor };
            it(`start=${JSON.stringify(start)} finish=${JSON.stringify(
              finish,
            )} anchor=${anchor}`, () => {
              const roundTripped = scheduleToRows(rowsToSchedule(rows));
              expect(roundTripped).toEqual(rows);
            });
          }
        }
      }
    }
  }
});

describe("round trip: fields -> rows -> fields is identity for a fully-populated schedule", () => {
  it("daily/weekly-shaped schedule, both ends bounded, anchor finish", () => {
    const fields = {
      start_mode: "sunrise",
      start_offset: -30,
      finish_mode: "time",
      finish_time: "20:00",
      anchor: "finish",
    };
    expect(rowsToSchedule(scheduleToRows(fields))).toEqual({
      start_mode: "sunrise",
      start_time: undefined,
      start_offset: -30,
      start_azimuth: undefined,
      finish_mode: "time",
      finish_time: "20:00",
      finish_offset: undefined,
      finish_azimuth: undefined,
      anchor: "finish",
    });
  });
});

describe("describeWindow", () => {
  it("both unbounded: error on both cells, invalid", () => {
    const rows: ScheduleRows = {
      start: { mode: "none" },
      finish: { mode: "none" },
      anchor: SCHEDULE_ANCHOR_FINISH,
    };
    expect(describeWindow(rows)).toEqual({
      start: "error",
      finish: "error",
      valid: false,
    });
  });

  it("start unbounded, finish bounded: start is set-by-demand, finish is exact", () => {
    const rows: ScheduleRows = {
      start: { mode: "none" },
      finish: { mode: "time", time: "20:00" },
      anchor: SCHEDULE_ANCHOR_FINISH,
    };
    expect(describeWindow(rows)).toEqual({
      start: "demand_open",
      finish: "exact",
      valid: true,
    });
  });

  it("start bounded, finish unbounded: start is exact, finish is set-by-demand", () => {
    const rows: ScheduleRows = {
      start: { mode: "sunrise", offset: 0 },
      finish: { mode: "none" },
      anchor: SCHEDULE_ANCHOR_START,
    };
    expect(describeWindow(rows)).toEqual({
      start: "exact",
      finish: "demand_open",
      valid: true,
    });
  });

  it("both bounded, pinned to finish (late): start is floored, finish is exact+deferred", () => {
    const rows: ScheduleRows = {
      start: { mode: "sunrise", offset: 0 },
      finish: { mode: "time", time: "20:00" },
      anchor: SCHEDULE_ANCHOR_FINISH,
    };
    expect(describeWindow(rows)).toEqual({
      start: "demand_floored",
      finish: "exact_deferred",
      valid: true,
    });
  });

  it("both bounded, pinned to start (early): start is exact, finish is capped+deferred", () => {
    const rows: ScheduleRows = {
      start: { mode: "time", time: "06:00" },
      finish: { mode: "sunset", offset: 0 },
      anchor: SCHEDULE_ANCHOR_START,
    };
    expect(describeWindow(rows)).toEqual({
      start: "exact",
      finish: "demand_capped_deferred",
      valid: true,
    });
  });

  it("unreachable bearing on the governing end: that end warns the run will not happen", () => {
    // Only one end bounded, so it governs. The scheduler cannot compute an
    // occurrence and declines to arm the schedule at all.
    const rows: ScheduleRows = {
      start: { mode: SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH, azimuth: 90 },
      finish: { mode: "none" },
      anchor: SCHEDULE_ANCHOR_START,
    };
    expect(describeWindow(rows, { start: true })).toEqual({
      start: "unreachable_no_run",
      finish: "demand_open",
      valid: true,
    });
  });

  it("unreachable bearing on the paired end: that limit is reported as ignored", () => {
    const rows: ScheduleRows = {
      start: { mode: SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH, azimuth: 90 },
      finish: { mode: "time", time: "20:00" },
      anchor: SCHEDULE_ANCHOR_FINISH,
    };
    expect(describeWindow(rows, { start: true })).toEqual({
      start: "unreachable_ignored",
      finish: "exact_deferred",
      valid: true,
    });
  });

  it("follows the anchor when both ends are bounded and the anchored one is unreachable", () => {
    const rows: ScheduleRows = {
      start: { mode: "time", time: "06:00" },
      finish: { mode: SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH, azimuth: 90 },
      anchor: SCHEDULE_ANCHOR_FINISH,
    };
    expect(describeWindow(rows, { finish: true }).finish).toBe(
      "unreachable_no_run",
    );
    expect(
      describeWindow(
        { ...rows, anchor: SCHEDULE_ANCHOR_START },
        { finish: true },
      ).finish,
    ).toBe("unreachable_ignored");
  });

  it("still allows saving an unreachable bearing", () => {
    // The backend accepts it and warns, and a bearing unreachable here can be
    // reachable elsewhere or later in the year — a warning, not a rejection.
    const rows: ScheduleRows = {
      start: { mode: SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH, azimuth: 90 },
      finish: { mode: "none" },
      anchor: SCHEDULE_ANCHOR_START,
    };
    expect(describeWindow(rows, { start: true }).valid).toBe(true);
  });

  it("is unchanged when nothing is unresolvable", () => {
    const rows: ScheduleRows = {
      start: { mode: SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH, azimuth: 90 },
      finish: { mode: "time", time: "20:00" },
      anchor: SCHEDULE_ANCHOR_FINISH,
    };
    expect(describeWindow(rows, {})).toEqual(describeWindow(rows));
    expect(describeWindow(rows, { start: false, finish: false })).toEqual(
      describeWindow(rows),
    );
  });

  it("marks exactly the two unreachable states as warnings", () => {
    expect(isWarningHelp("unreachable_no_run")).toBe(true);
    expect(isWarningHelp("unreachable_ignored")).toBe(true);
    for (const key of [
      "error",
      "exact",
      "demand_open",
      "demand_floored",
      "exact_deferred",
      "demand_capped_deferred",
    ] as HelpKey[]) {
      expect(isWarningHelp(key)).toBe(false);
    }
  });

  it("covers all five states across every non-none mode pairing", () => {
    const boundedModes: BoundMode[] = [
      SCHEDULE_BOUND_MODE_TIME,
      SCHEDULE_BOUND_MODE_SUNRISE,
      SCHEDULE_BOUND_MODE_SUNSET,
      SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
    ];
    for (const startMode of boundedModes) {
      for (const finishMode of boundedModes) {
        for (const anchor of ALL_ANCHORS) {
          const rows: ScheduleRows = {
            start: defaultRowForMode(startMode),
            finish: defaultRowForMode(finishMode),
            anchor,
          };
          const help = describeWindow(rows);
          expect(help.valid).toBe(true);
          if (anchor === SCHEDULE_ANCHOR_FINISH) {
            expect(help.start).toBe("demand_floored");
            expect(help.finish).toBe("exact_deferred");
          } else {
            expect(help.start).toBe("exact");
            expect(help.finish).toBe("demand_capped_deferred");
          }
        }
      }
    }
  });
});
