import { describe, it, expect } from "vitest";
import {
  azimuthBoundMinutes,
  azimuthCrossedTarget,
  findNextSolarAzimuthInstant,
  normalizeAzimuthAngle,
  solarAzimuthDegrees,
  wallClockNowInZone,
  wallClockMinutes,
} from "./solar-azimuth";

/**
 * Golden values generated from the BACKEND functions themselves
 * (`helpers.calculate_solar_azimuth` / `find_next_solar_azimuth_time`), not
 * from an astronomical reference. That is deliberate: the dial's contract is
 * to draw the bound the scheduler will fire on, and the backend's formula is
 * a rough approximation of the real sun (see solar-azimuth.ts). Checking this
 * port against a real ephemeris would assert the wrong thing.
 *
 * To regenerate after a backend change, from a Python environment with the
 * integration importable:
 *   from custom_components.smart_irrigation.helpers import (
 *       calculate_solar_azimuth, find_next_solar_azimuth_time)
 * called at the inputs below. Those are UTC instants: the resolver reads UTC
 * and takes a naive datetime AS UTC, so the two sides agree on the frame
 * without either converting.
 */
const AZIMUTH_GOLDENS = [
  ["phoenix_summer_noon", 33.45, -112.07, "2026-06-21T12:00:00", 58.448939421],
  [
    "phoenix_summer_morning",
    33.45,
    -112.07,
    "2026-06-21T07:30:00",
    0.470899178,
  ],
  [
    "phoenix_winter_afternoon",
    33.45,
    -112.07,
    "2026-12-21T15:45:00",
    129.069984578,
  ],
  ["london_equinox", 51.51, -0.13, "2026-03-20T09:00:00", 128.363225344],
  ["sydney_south", -33.87, 151.21, "2026-01-15T10:20:00", 231.040265498],
  [
    "wellington_south_winter",
    -41.29,
    174.78,
    "2026-07-04T13:05:00",
    149.932383498,
  ],
  ["equator", 0.0, 0.0, "2026-09-10T06:00:00", 85.784473565],
  ["high_north", 64.13, -21.9, "2026-05-01T18:40:00", 265.94116189],
] as const;

const FIND_GOLDENS = [
  [
    "phoenix_east_90",
    33.45,
    -112.07,
    90,
    "2026-06-21T00:00:00",
    "16:12:11.250",
  ],
  [
    "phoenix_south_180",
    33.45,
    -112.07,
    180,
    "2026-06-21T00:00:00",
    "19:28:07.500",
  ],
  [
    "phoenix_west_270",
    33.45,
    -112.07,
    270,
    "2026-06-21T00:00:00",
    "22:44:03.750",
  ],
  [
    "phoenix_winter_east_90",
    33.45,
    -112.07,
    90,
    "2026-12-21T00:00:00",
    "10:44:03.750",
  ],
  ["london_240", 51.51, -0.13, 240, "2026-03-20T00:00:00", "15:36:33.750"],
  [
    "sydney_south_hemisphere_45",
    -33.87,
    151.21,
    45,
    "2026-01-15T00:00:00",
    "01:03:45.000",
  ],
  [
    "sydney_south_hemisphere_300",
    -33.87,
    151.21,
    300,
    "2026-01-15T00:00:00",
    "03:15:56.250",
  ],
  [
    "wellington_south_winter_120",
    -41.29,
    174.78,
    120,
    "2026-07-04T00:00:00",
    "14:11:15.000",
  ],
  ["equator_0", 0.0, 0.0, 0, "2026-09-10T00:00:00", "11:59:03.750"],
  ["high_north_150", 64.13, -21.9, 150, "2026-05-01T00:00:00", "11:50:37.500"],
  [
    "wrap_near_north_355",
    33.45,
    -112.07,
    355,
    "2026-06-21T00:00:00",
    "07:09:22.500",
  ],
] as const;

/** A UTC instant. */
const at = (iso: string) => new Date(`${iso}Z`);

describe("solarAzimuthDegrees", () => {
  it.each(AZIMUTH_GOLDENS)(
    "matches the Python resolver at %s",
    (_label, lat, lon, when, expected) => {
      expect(solarAzimuthDegrees(lat, lon, at(when))).toBeCloseTo(expected, 6);
    },
  );

  it("ignores sub-second precision, as the Python does", () => {
    const whole = solarAzimuthDegrees(
      33.45,
      -112.07,
      at("2026-06-21T04:30:56"),
    );
    const fractional = solarAzimuthDegrees(
      33.45,
      -112.07,
      new Date(at("2026-06-21T04:30:56").getTime() + 250),
    );
    expect(fractional).toBe(whole);
  });
});

describe("findNextSolarAzimuthInstant", () => {
  it.each(FIND_GOLDENS)(
    "matches the Python resolver for %s",
    (_label, lat, lon, target, from, expectedTime) => {
      const found = findNextSolarAzimuthInstant(lat, lon, target, at(from));
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
      findNextSolarAzimuthInstant(0, 0, 90, at("2026-09-10T00:00:00")),
    ).toBeNull();
  });

  it("finds the following day's crossing when today's has passed", () => {
    // Phoenix reaches 270 at 22:44 UTC on the 21st, so a search starting after
    // that has to roll into the 22nd rather than report the crossing it missed.
    const found = findNextSolarAzimuthInstant(
      33.45,
      -112.07,
      270,
      at("2026-06-21T23:00:00"),
    );
    expect(found).not.toBeNull();
    expect((found as Date).getUTCDate()).toBe(22);
    expect((found as Date).getUTCHours()).toBe(22);
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
  it("reads an instant on Home Assistant's clock, not the browser's", () => {
    // 00:00 UTC is 09:00 in Tokyo. The dial must say 09:00 wherever the
    // viewer happens to be sitting, because that is when the schedule fires.
    const instant = new Date("2026-06-21T00:00:00Z");
    expect(wallClockMinutes(wallClockNowInZone("Asia/Tokyo", instant))).toBe(
      9 * 60,
    );
    expect(
      wallClockMinutes(wallClockNowInZone("America/New_York", instant)),
    ).toBe(20 * 60);
  });

  it("puts an evening sunset in the evening half of the dial", () => {
    // The regression this exists for: 2026-08-10T00:42Z is a 20:42 sunset in
    // New York, and reading it on a UTC browser drew the moon at 00:42 -
    // most of the way round the ring from the run it was meant to bracket.
    const sunset = new Date("2026-08-10T00:42:14Z");
    expect(
      wallClockMinutes(wallClockNowInZone("America/New_York", sunset)),
    ).toBe(20 * 60 + 42);
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
