import { describe, it, expect } from "vitest";
import {
  governingEnd,
  toEditable,
  toStored,
  StoredSchedule,
} from "./schedule-shape";

/**
 * The stored shape carries a recurrence plus two independently bounded ends;
 * the dialog edits one time source. These cover the translation both ways,
 * for every shape the storage migration produces.
 */

const RETIRED = [
  "type",
  "time",
  "offset_minutes",
  "account_for_duration",
  "azimuth_angle",
  "time_anchor",
];

function expectNoRetiredKeys(s: StoredSchedule) {
  for (const k of RETIRED) expect(s).not.toHaveProperty(k);
}

describe("governingEnd", () => {
  it("is the only bounded end when one is bounded", () => {
    expect(governingEnd({ start_mode: "time", finish_mode: "none" })).toBe(
      "start",
    );
    expect(governingEnd({ start_mode: "none", finish_mode: "time" })).toBe(
      "finish",
    );
  });

  it("follows the anchor when both are bounded", () => {
    const both = { start_mode: "sunset", finish_mode: "sunrise" };
    expect(governingEnd({ ...both, anchor: "start" })).toBe("start");
    expect(governingEnd({ ...both, anchor: "finish" })).toBe("finish");
    // Finish is the default the backend applies when the anchor is missing.
    expect(governingEnd(both)).toBe("finish");
  });

  it("reads an unbounded schedule as start, so the dialog has a row to show", () => {
    expect(governingEnd({})).toBe("start");
  });
});

describe("toEditable", () => {
  it("shows a time-bounded start as a clock schedule on its recurrence", () => {
    const e = toEditable({
      recurrence: "weekly",
      start_mode: "time",
      start_time: "22:00",
      finish_mode: "none",
      anchor: "start",
      days_of_week: ["monday"],
    });
    expect(e.type).toBe("weekly");
    expect(e.time).toBe("22:00");
    expect(e.time_anchor).toBe("start");
    expect(e.days_of_week).toEqual(["monday"]);
  });

  it("shows a sun-bounded end as that sun event, not as its recurrence", () => {
    const e = toEditable({
      recurrence: "daily",
      start_mode: "none",
      finish_mode: "sunrise",
      finish_offset: -30,
      anchor: "finish",
    });
    expect(e.type).toBe("sunrise");
    expect(e.offset_minutes).toBe(-30);
    expect(e.time_anchor).toBe("finish");
    expect(e.azimuth_angle).toBeUndefined();
  });

  it("carries the azimuth of an azimuth-bounded end", () => {
    const e = toEditable({
      recurrence: "daily",
      start_mode: "solar_azimuth",
      start_azimuth: 100,
      start_offset: 15,
      finish_mode: "none",
      anchor: "start",
    });
    expect(e.type).toBe("solar_azimuth");
    expect(e.azimuth_angle).toBe(100);
    expect(e.offset_minutes).toBe(15);
  });

  it("does not read an interval's own anchor as a window bound", () => {
    // start_time is the interval's clock anchor here, not a bounded Start.
    const e = toEditable({
      recurrence: "interval",
      interval_hours: 6,
      start_time: "03:00",
    });
    expect(e.type).toBe("interval");
    expect(e.time).toBeUndefined();
    expect(e.start_time).toBe("03:00");
  });
});

describe("toStored", () => {
  it("writes a clock time onto the anchored end and unbounds the other", () => {
    const s = toStored({
      type: "daily",
      time: "06:00",
      time_anchor: "start",
      name: "Morning",
    });
    expect(s).toMatchObject({
      recurrence: "daily",
      start_mode: "time",
      start_time: "06:00",
      finish_mode: "none",
      anchor: "start",
      name: "Morning",
    });
    expectNoRetiredKeys(s);
  });

  it("writes a finish-anchored clock time onto the finish bound", () => {
    const s = toStored({
      type: "monthly",
      time: "05:30",
      time_anchor: "finish",
    });
    expect(s).toMatchObject({
      recurrence: "monthly",
      finish_mode: "time",
      finish_time: "05:30",
      start_mode: "none",
      anchor: "finish",
    });
    expect(s.start_time).toBeUndefined();
  });

  it("leaves the recurrence daily for a sun-relative time of day", () => {
    const s = toStored({
      type: "sunset",
      offset_minutes: 15,
      time_anchor: "start",
    });
    expect(s).toMatchObject({
      recurrence: "daily",
      start_mode: "sunset",
      start_offset: 15,
      finish_mode: "none",
      anchor: "start",
    });
    expect(s.start_time).toBeUndefined();
  });

  it("writes an azimuth bound with its angle", () => {
    const s = toStored({
      type: "solar_azimuth",
      azimuth_angle: 100,
      offset_minutes: 0,
      time_anchor: "finish",
    });
    expect(s).toMatchObject({
      recurrence: "daily",
      finish_mode: "solar_azimuth",
      finish_azimuth: 100,
      finish_offset: 0,
      start_mode: "none",
      anchor: "finish",
    });
  });

  it("gives an interval no bounds and keeps its own anchor", () => {
    const s = toStored({
      type: "interval",
      interval_hours: 6,
      start_time: "03:00",
    });
    expect(s.recurrence).toBe("interval");
    expect(s.start_mode).toBeUndefined();
    expect(s.finish_mode).toBeUndefined();
    expect(s.start_time).toBe("03:00");
  });

  it("clears the bounds of a schedule switched to interval", () => {
    // An interval has no time of day, so a bound left behind by the shape it
    // used to have would be stored as an interval that still reads as bounded.
    const s = toStored({
      type: "interval",
      interval_hours: 6,
      start_mode: "sunset",
      start_offset: 15,
      finish_mode: "time",
      finish_time: "05:30",
      anchor: "finish",
    });
    expect(s.recurrence).toBe("interval");
    expect(s.start_mode).toBeUndefined();
    expect(s.start_offset).toBeUndefined();
    expect(s.finish_mode).toBeUndefined();
    expect(s.finish_time).toBeUndefined();
    expect(s.anchor).toBeUndefined();
  });

  it("defaults a missing time to the value the old resolver produced", () => {
    // A clock schedule stored without a time fired at 06:00 through a resolver
    // default that no longer exists, so the value has to be written out.
    expect(toStored({ type: "daily", time_anchor: "start" }).start_time).toBe(
      "06:00",
    );
  });

  it("clears the values of a bound that is being switched off", () => {
    // Editing a sunrise-finish schedule down to a plain clock start must not
    // leave the old finish offset behind for the resolver to read.
    const s = toStored({
      type: "daily",
      time: "07:00",
      time_anchor: "start",
      finish_mode: "sunrise",
      finish_offset: -30,
      finish_azimuth: 90,
    });
    expect(s.finish_mode).toBe("none");
    expect(s.finish_offset).toBeUndefined();
    expect(s.finish_azimuth).toBeUndefined();
  });
});

describe("round trip", () => {
  const CASES: StoredSchedule[] = [
    {
      recurrence: "daily",
      start_mode: "time",
      start_time: "06:00",
      finish_mode: "none",
      anchor: "start",
    },
    {
      recurrence: "weekly",
      start_mode: "time",
      start_time: "22:00",
      finish_mode: "none",
      anchor: "start",
      days_of_week: ["monday", "thursday"],
    },
    {
      recurrence: "monthly",
      finish_mode: "time",
      finish_time: "04:00",
      start_mode: "none",
      anchor: "finish",
      day_of_month: 15,
    },
    {
      recurrence: "daily",
      finish_mode: "sunrise",
      finish_offset: -30,
      start_mode: "none",
      anchor: "finish",
    },
    {
      recurrence: "daily",
      start_mode: "sunset",
      start_offset: 15,
      finish_mode: "none",
      anchor: "start",
    },
    {
      recurrence: "daily",
      finish_mode: "solar_azimuth",
      finish_azimuth: 100,
      finish_offset: 0,
      start_mode: "none",
      anchor: "finish",
    },
    { recurrence: "interval", interval_hours: 6, start_time: "03:00" },
  ];

  it.each(CASES)("survives editing and saving unchanged: %j", (stored) => {
    expect(toStored(toEditable(stored))).toEqual(stored);
  });
});
