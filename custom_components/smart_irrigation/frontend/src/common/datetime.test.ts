import { describe, it, expect } from "vitest";
import { isValidDate, isSameDay, addDays, formatDateTime } from "./datetime";

describe("datetime", () => {
  it("isValidDate distinguishes real from bogus dates", () => {
    expect(isValidDate("2026-06-17T12:00:00")).toBe(true);
    expect(isValidDate(0)).toBe(true);
    expect(isValidDate("not-a-date")).toBe(false);
  });

  it("isSameDay compares local calendar day", () => {
    expect(
      isSameDay(new Date(2026, 5, 17, 1, 0), new Date(2026, 5, 17, 23, 0)),
    ).toBe(true);
    expect(
      isSameDay(new Date(2026, 5, 17, 23, 0), new Date(2026, 5, 18, 0, 0)),
    ).toBe(false);
  });

  it("addDays shifts whole days and is non-mutating", () => {
    const base = new Date(2026, 5, 17, 9, 30);
    const next = addDays(base, 1);
    expect(next.getDate()).toBe(18);
    expect(base.getDate()).toBe(17); // original untouched
    expect(addDays(base, -17).getMonth()).toBe(4); // crosses into May
  });

  it("formatDateTime zero-pads", () => {
    expect(formatDateTime(new Date(2026, 0, 3, 4, 5))).toBe("2026-01-03 04:05");
  });
});
