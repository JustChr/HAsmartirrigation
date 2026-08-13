import { describe, it, expect } from "vitest";
import {
  azimuthBoundMinutes,
  azimuthCrossedTarget,
  findNextSolarAzimuthWallClock,
  normalizeAzimuthAngle,
  solarAzimuthDegrees,
  wallClockNowInZone,
  wallClockToBrowserMinutes,
} from "./solar-azimuth";

/**
 * Golden values generated from the BACKEND functions themselves
 * (`helpers.calculate_solar_azimuth` / `find_next_solar_azimuth_time`), not
 * from an astronomical reference. That is deliberate: the dial's contract is
 * to draw the bound the scheduler will fire on, and the backend's formula is
 * a rough approximation of the real sun (see solar-azimuth.ts). Checking this
 * port against a real ephemeris would assert the wrong thing.
 *
 * To regenerate after a backend change, in the hasi-test container:
 *   from custom_components.smart_irrigation.helpers import (
 *       calculate_solar_azimuth, find_next_solar_azimuth_time)
 * called with naive datetimes at the inputs below.
 */
const AZIMUTH_GOLDENS = [
  ["phoenix_summer_noon", 33.45, -112.07, "2026-06-21T12:00:00", 301.551060579],
  [
    "phoenix_summer_morning",
    33.45,
    -112.07,
    "2026-06-21T07:30:00",
    267.490753157,
  ],
  [
    "phoenix_winter_afternoon",
    33.45,
    -112.07,
    "2026-12-21T15:45:00",
    311.303008771,
  ],
  ["london_equinox", 51.51, -0.13, "2026-03-20T09:00:00", 128.614563467],
  ["sydney_south", -33.87, 151.21, "2026-01-15T10:20:00", 175.701001957],
  [
    "wellington_south_winter",
    -41.29,
    174.78,
    "2026-07-04T13:05:00",
    129.046135794,
  ],
  ["equator", 0.0, 0.0, "2026-09-10T06:00:00", 85.784473565],
  ["high_north", 64.13, -21.9, "2026-05-01T18:40:00", 304.869874151],
] as const;

const FIND_GOLDENS = [
  ["phoenix_east_90", 33.45, -112.07, 90, "2026-06-21T00:00:00", "01:15:00"],
  [
    "phoenix_south_180",
    33.45,
    -112.07,
    180,
    "2026-06-21T00:00:00",
    "04:30:56.250",
  ],
  [
    "phoenix_west_270",
    33.45,
    -112.07,
    270,
    "2026-06-21T00:00:00",
    "07:46:52.500",
  ],
  [
    "phoenix_winter_east_90",
    33.45,
    -112.07,
    90,
    "2026-12-21T00:00:00",
    "19:46:52.500",
  ],
  ["london_240", 51.51, -0.13, 240, "2026-03-20T00:00:00", "15:35:37.500"],
  [
    "sydney_south_hemisphere_45",
    -33.87,
    151.21,
    45,
    "2026-01-15T00:00:00",
    "21:13:07.500",
  ],
  [
    "sydney_south_hemisphere_300",
    -33.87,
    151.21,
    300,
    "2026-01-15T00:00:00",
    "23:25:18.750",
  ],
  [
    "wellington_south_winter_120",
    -41.29,
    174.78,
    120,
    "2026-07-04T00:00:00",
    "13:29:03.750",
  ],
  ["equator_0", 0.0, 0.0, 0, "2026-09-10T00:00:00", "11:59:03.750"],
  ["high_north_150", 64.13, -21.9, 150, "2026-05-01T00:00:00", "08:55:18.750"],
  [
    "wrap_near_north_355",
    33.45,
    -112.07,
    355,
    "2026-06-21T00:00:00",
    "16:13:07.500",
  ],
] as const;

/** A naive wall clock, carried in a Date's UTC fields. */
const wall = (iso: string) => new Date(`${iso}Z`);

describe("solarAzimuthDegrees", () => {
  it.each(AZIMUTH_GOLDENS)(
    "matches the Python resolver at %s",
    (_label, lat, lon, at, expected) => {
      expect(solarAzimuthDegrees(lat, lon, wall(at))).toBeCloseTo(expected, 6);
    },
  );

  it("ignores sub-second precision, as the Python does", () => {
    const whole = solarAzimuthDegrees(
      33.45,
      -112.07,
      wall("2026-06-21T04:30:56"),
    );
    const fractional = solarAzimuthDegrees(
      33.45,
      -112.07,
      new Date(wall("2026-06-21T04:30:56").getTime() + 250),
    );
    expect(fractional).toBe(whole);
  });
});

describe("findNextSolarAzimuthWallClock", () => {
  it.each(FIND_GOLDENS)(
    "matches the Python resolver for %s",
    (_label, lat, lon, target, from, expectedTime) => {
      const found = findNextSolarAzimuthWallClock(lat, lon, target, wall(from));
      expect(found).not.toBeNull();
      const day = from.slice(0, 10);
      const expectedMs = Date.parse(`${day}T${expectedTime}Z`);
      // The resolver's own contract is minute precision (its binary search
      // stops at a 60s bracket), and Math.sin is allowed to differ from C
      // libm in the last ULP, so agreement is asserted at the precision the
      // value actually carries rather than to the millisecond.
      expect(
        Math.abs((found as Date).getTime() - expectedMs),
      ).toBeLessThanOrEqual(1000);
    },
  );

  it("returns null for a bearing the sun never reaches", () => {
    // Due east on the equator: the backend's azimuth curve never crosses it,
    // and the scheduler treats that as an unresolvable bound.
    expect(
      findNextSolarAzimuthWallClock(0, 0, 90, wall("2026-09-10T00:00:00")),
    ).toBeNull();
  });

  it("finds the following day's crossing when today's has passed", () => {
    const found = findNextSolarAzimuthWallClock(
      33.45,
      -112.07,
      270,
      wall("2026-06-21T12:00:00"),
    );
    expect(found).not.toBeNull();
    expect((found as Date).getUTCDate()).toBe(22);
    expect((found as Date).getUTCHours()).toBe(7);
  });
});

describe("azimuthCrossedTarget", () => {
  it("detects an ordinary crossing in either direction", () => {
    expect(azimuthCrossedTarget(80, 100, 90)).toBe(true);
    expect(azimuthCrossedTarget(100, 80, 90)).toBe(true);
    expect(azimuthCrossedTarget(80, 89, 90)).toBe(false);
  });

  it("detects a crossing through the 360/0 wrap", () => {
    expect(azimuthCrossedTarget(359, 1, 0)).toBe(true);
    expect(azimuthCrossedTarget(359, 1, 180)).toBe(false);
    expect(azimuthCrossedTarget(1, 359, 0)).toBe(true);
  });
});

describe("normalizeAzimuthAngle", () => {
  it("wraps into 0-360, including negatives Python's modulo would keep", () => {
    expect(normalizeAzimuthAngle(450)).toBe(90);
    expect(normalizeAzimuthAngle(-30)).toBe(330);
    expect(normalizeAzimuthAngle(365)).toBe(5);
    expect(normalizeAzimuthAngle(90)).toBe(90);
  });
});

describe("zone bridging", () => {
  it("is an identity when Home Assistant and the browser share a zone", () => {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const w = wallClockNowInZone(tz, new Date("2026-06-21T18:00:00Z"));
    expect(wallClockToBrowserMinutes(w, tz)).toBe(
      w.getUTCHours() * 60 + w.getUTCMinutes(),
    );
  });

  it("shifts a wall clock from another zone onto the browser's clock", () => {
    // 09:00 in Tokyo is 00:00 UTC; the assertion is written against whatever
    // the test runner's own zone makes of that instant, so it holds anywhere.
    const tokyoWall = wall("2026-06-21T09:00:00");
    const instant = new Date("2026-06-21T00:00:00Z");
    expect(wallClockToBrowserMinutes(tokyoWall, "Asia/Tokyo")).toBe(
      instant.getHours() * 60 + instant.getMinutes(),
    );
  });

  it("falls back to the browser zone for a missing or bogus zone", () => {
    const instant = new Date("2026-06-21T18:34:00Z");
    const expected = new Date(
      Date.UTC(
        instant.getFullYear(),
        instant.getMonth(),
        instant.getDate(),
        instant.getHours(),
        instant.getMinutes(),
        instant.getSeconds(),
      ),
    ).getTime();
    expect(wallClockNowInZone(undefined, instant).getTime()).toBe(expected);
    expect(wallClockNowInZone("Not/AZone", instant).getTime()).toBe(expected);
  });

  it("keeps midnight on the day it starts, not the next one", () => {
    // An h24 hour cycle renders midnight as "24" on the outgoing day; rolled
    // forward by Date.UTC that would put the whole resolution a day out.
    const midnightTokyo = wallClockNowInZone(
      "Asia/Tokyo",
      new Date("2026-06-20T15:00:00Z"), // 00:00 on the 21st in Tokyo
    );
    expect(midnightTokyo.getUTCDate()).toBe(21);
    expect(midnightTokyo.getUTCHours()).toBe(0);
  });
});

describe("azimuthBoundMinutes", () => {
  it("resolves from midnight of the current day, not from now", () => {
    // Same answer whether asked in the morning or the evening: the dial draws
    // the schedule's shape, not the next firing.
    const morning = azimuthBoundMinutes(
      33.45,
      -112.07,
      270,
      "UTC",
      new Date("2026-06-21T02:00:00Z"),
    );
    const evening = azimuthBoundMinutes(
      33.45,
      -112.07,
      270,
      "UTC",
      new Date("2026-06-21T22:00:00Z"),
    );
    expect(morning).toBe(evening);
  });

  it("returns null for an unreachable bearing", () => {
    expect(
      azimuthBoundMinutes(0, 0, 90, "UTC", new Date("2026-09-10T12:00:00Z")),
    ).toBeNull();
  });

  it("normalizes an out-of-range bearing before resolving", () => {
    const at450 = azimuthBoundMinutes(
      33.45,
      -112.07,
      450,
      "UTC",
      new Date("2026-06-21T12:00:00Z"),
    );
    const at90 = azimuthBoundMinutes(
      33.45,
      -112.07,
      90,
      "UTC",
      new Date("2026-06-21T12:00:00Z"),
    );
    expect(at450).toBe(at90);
  });
});
