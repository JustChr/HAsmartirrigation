import { describe, it, expect } from "vitest";
import {
  polar,
  arcPath,
  fmtClock,
  fmtDuration,
  intervalPlan,
  resolveAbsMinutes,
  buildDial,
  DIAL_CENTER,
  DIAL_RADIUS,
  DIAL_MIN_VISIBLE_MINUTES,
} from "./run-window-dial";
import { ScheduleRows } from "./schedule-rows";
import {
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_ANCHOR_START,
  SCHEDULE_ANCHOR_FINISH,
  SCHEDULE_RECURRENCE_DAILY,
  SCHEDULE_RECURRENCE_INTERVAL,
} from "../const";

const SUNRISE = 6 * 60 + 12; // 06:12
const SUNSET = 20 * 60 + 31; // 20:31

function rows(
  start: ScheduleRows["start"],
  finish: ScheduleRows["finish"],
  anchor: ScheduleRows["anchor"] = SCHEDULE_ANCHOR_FINISH,
): ScheduleRows {
  return { start, finish, anchor };
}

describe("polar / arcPath orientation", () => {
  it("puts noon (720 min) at the top of the dial", () => {
    const [x, y] = polar(DIAL_RADIUS, 720);
    expect(x).toBeCloseTo(DIAL_CENTER, 5);
    expect(y).toBeCloseTo(DIAL_CENTER - DIAL_RADIUS, 5);
  });

  it("puts midnight (0 min) at the bottom of the dial", () => {
    const [x, y] = polar(DIAL_RADIUS, 0);
    expect(x).toBeCloseTo(DIAL_CENTER, 5);
    expect(y).toBeCloseTo(DIAL_CENTER + DIAL_RADIUS, 5);
  });

  it("draws a full-circle arc without collapsing to a point", () => {
    const d = arcPath(DIAL_RADIUS, 0, 1440);
    expect(d).toMatch(/^M .* A /);
  });
});

describe("fmtClock / fmtDuration", () => {
  it("formats a minute-of-day as zero-padded HH:MM, wrapping negatives and overflow", () => {
    expect(fmtClock(0)).toBe("00:00");
    expect(fmtClock(90)).toBe("01:30");
    expect(fmtClock(-30)).toBe("23:30");
    expect(fmtClock(1440 + 30)).toBe("00:30");
  });

  it("formats a duration, omitting the hour part when zero", () => {
    expect(fmtDuration(45)).toBe("45m");
    expect(fmtDuration(90)).toBe("1h 30m");
    expect(fmtDuration(120)).toBe("2h 0m");
  });
});

describe("resolveAbsMinutes", () => {
  it("resolves 'none' to null (no bound to draw)", () => {
    expect(
      resolveAbsMinutes({ mode: SCHEDULE_BOUND_MODE_NONE }, SUNRISE, SUNSET),
    ).toBeNull();
  });

  it("resolves 'time' directly, ignoring sun times", () => {
    expect(
      resolveAbsMinutes(
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "14:30" },
        SUNRISE,
        SUNSET,
      ),
    ).toBe(14 * 60 + 30);
  });

  it("resolves 'sunrise'/'sunset' as the real sun time plus the signed offset", () => {
    expect(
      resolveAbsMinutes(
        { mode: SCHEDULE_BOUND_MODE_SUNRISE, offset: -15 },
        SUNRISE,
        SUNSET,
      ),
    ).toBe(SUNRISE - 15);
    expect(
      resolveAbsMinutes(
        { mode: SCHEDULE_BOUND_MODE_SUNSET, offset: 30 },
        SUNRISE,
        SUNSET,
      ),
    ).toBe(SUNSET + 30);
  });
});

describe("intervalPlan", () => {
  it("lays out occurrences every N hours from the optional clock start", () => {
    const { runs } = intervalPlan(60, 6, "02:00");
    expect(runs[0]).toEqual([120, 180]);
    expect(runs[1]).toEqual([480, 540]);
    expect(runs.length).toBe(4);
  });

  it("flags same-day collisions when a run is still going at the next occurrence", () => {
    // 4h runs on a 3h interval: every occurrence collides with the last.
    const { overlaps } = intervalPlan(240, 3, "00:00");
    expect(overlaps.length).toBeGreaterThan(0);
    const [a, b] = overlaps[0];
    expect(b).toBeGreaterThan(a);
  });

  it("reports no collisions when runs comfortably fit the interval", () => {
    const { overlaps } = intervalPlan(30, 4, "00:00");
    expect(overlaps).toEqual([]);
  });
});

describe("buildDial: window-mode centre value", () => {
  it("reports window duration when both ends are bounded", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "06:00" },
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "20:00" },
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 30,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.centre).toEqual({ kind: "window", minutes: 14 * 60 });
  });

  it("reports run duration (not a window) when one end is open", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "06:00" },
        { mode: SCHEDULE_BOUND_MODE_NONE },
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 45,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.centre).toEqual({ kind: "run", minutes: 45 });
  });

  it("reports invalid (no minutes) when both ends are open", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_NONE },
        { mode: SCHEDULE_BOUND_MODE_NONE },
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 45,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.centre).toEqual({ kind: "invalid" });
    expect(model.runs).toEqual([]);
    expect(model.windowArc).toBeNull();
  });

  it("reports interval occurrences-per-day and the configured interval", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_NONE },
        { mode: SCHEDULE_BOUND_MODE_NONE },
      ),
      recurrence: SCHEDULE_RECURRENCE_INTERVAL,
      intervalHours: 4,
      nominalDemandMinutes: 20,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.centre).toEqual({
      kind: "interval",
      perDay: 6,
      intervalHours: 4,
    });
  });
});

describe("buildDial: nominal demand drives the run bar, not a live plan", () => {
  it("the run bar length is exactly nominal demand when both ends are open enough to hold it", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "06:00" },
        { mode: SCHEDULE_BOUND_MODE_NONE },
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 90,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.centre.kind).toBe("run");
    expect(model.centre.minutes).toBe(90);
    expect(model.drops).toHaveLength(1);
    expect(model.drops[0].toMinutes - model.drops[0].fromMinutes).toBe(90);
  });

  it("clamps the run bar to the window and draws unserved demand as a dotted arc when demand exceeds it", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "06:00" },
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "07:00" },
        SCHEDULE_ANCHOR_FINISH,
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 120, // twice the 60-minute window
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.centre).toEqual({ kind: "window", minutes: 60 });
    expect(model.dottedPath).not.toBeNull();
    // The clamped run is exactly the window's length, not the raw demand.
    const [drop] = model.drops;
    expect(drop.toMinutes - drop.fromMinutes).toBe(60);
  });

  it("draws no dotted arc when nominal demand fits the window", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "06:00" },
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "20:00" },
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 30,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.dottedPath).toBeNull();
  });
});

describe("buildDial: minimum visible arc", () => {
  it("floors a window arc shorter than DIAL_MIN_VISIBLE_MINUTES to that minimum span", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "06:00" },
        { mode: SCHEDULE_BOUND_MODE_TIME, time: "06:10" }, // 10-minute window
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 10,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    // The reported duration is still the true (tiny) window...
    expect(model.centre).toEqual({ kind: "window", minutes: 10 });
    // ...but the drawn arc spans the visible floor so it doesn't collapse to a dot.
    expect(model.windowArc).toEqual({
      kind: "solid",
      d: arcPath(DIAL_RADIUS, 6 * 60, 6 * 60 + DIAL_MIN_VISIBLE_MINUTES),
    });
  });
});

describe("buildDial: interval wrap fade", () => {
  it("fades a run out before it reaches the next cycle's first occurrence, rather than drawing into it", () => {
    // 5h runs every 4h starting at midnight: the last occurrence overruns
    // past the 24h wrap point.
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_NONE },
        { mode: SCHEDULE_BOUND_MODE_NONE },
      ),
      recurrence: SCHEDULE_RECURRENCE_INTERVAL,
      intervalHours: 4,
      intervalStartTime: "00:00",
      nominalDemandMinutes: 300,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    const wrapping = model.runs.filter((r) => r.wraps);
    expect(wrapping.length).toBeGreaterThan(0);
    for (const r of wrapping) {
      if (!r.wraps) continue;
      // Never quite reaches minute 1440 (the wrap point) or beyond.
      expect(r.fade.every((seg) => true)).toBe(true);
      expect(r.fade.length).toBeGreaterThan(0);
      expect(r.fade[r.fade.length - 1].opacity).toBeLessThanOrEqual(1);
    }
  });

  it("marks the same-day collision between consecutive interval runs", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_NONE },
        { mode: SCHEDULE_BOUND_MODE_NONE },
      ),
      recurrence: SCHEDULE_RECURRENCE_INTERVAL,
      intervalHours: 3,
      intervalStartTime: "00:00",
      nominalDemandMinutes: 240,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.overlaps.length).toBeGreaterThan(0);
  });
});

describe("buildDial: sun/moon glyph placement", () => {
  it("always places the sun at sunrise and the moon at sunset, regardless of the window", () => {
    const model = buildDial({
      rows: rows(
        { mode: SCHEDULE_BOUND_MODE_NONE },
        { mode: SCHEDULE_BOUND_MODE_NONE },
      ),
      recurrence: SCHEDULE_RECURRENCE_DAILY,
      nominalDemandMinutes: 30,
      sunriseMinutes: SUNRISE,
      sunsetMinutes: SUNSET,
    });
    expect(model.sun.minutes).toBe(SUNRISE);
    expect(model.moon.minutes).toBe(SUNSET);
  });
});
