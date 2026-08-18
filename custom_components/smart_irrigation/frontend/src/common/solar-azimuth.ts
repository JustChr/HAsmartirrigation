/**
 * Solar azimuth resolution for the run-window dial.
 *
 * ⚠️ This is a deliberate line-by-line port of the backend's
 * `calculate_solar_azimuth` / `find_next_solar_azimuth_time` /
 * `_azimuth_crossed_target` / `_refine_azimuth_time` in
 * `custom_components/smart_irrigation/helpers.py`. A change to either side
 * must be made to both, or the dial silently draws a bound at a different
 * time than the scheduler fires on. The Python definitions carry a matching
 * cross-reference comment. `solar-azimuth.test.ts` pins this port against
 * values generated from the Python functions themselves.
 *
 * ⚠️ The formula it reproduces is NOT an accurate ephemeris, and this module
 * does not try to fix that. It uses Cooper's declination approximation, no
 * equation-of-time term, and applies its longitude correction with the
 * opposite sign to conventional local-solar-time (so at Phoenix the sun is
 * "at" 301 degrees at 12:00 local, not 180). The dial's job is to show where
 * the scheduler will actually put the bound, so matching the backend is the
 * requirement and a "correction" here would put the drawing out of step with
 * the run. Fixing the underlying math is a backend change with real user
 * impact - it moves when existing azimuth-bounded schedules fire.
 *
 * UTC INSTANTS. `calculate_solar_azimuth` reads UTC and takes a naive value AS
 * UTC, and `scheduler.py`'s `_resolve_event_instant` hands it aware UTC in both
 * directions, so a crossing is a real instant rather than a wall clock in
 * anyone's zone. This module resolves in that same frame and converts only at
 * the edge: `azimuthBoundMinutes` starts from the instant Home Assistant's
 * local midnight falls on and renders the crossing it finds back into Home
 * Assistant's zone, which is what puts an azimuth bound on the same clock as
 * the dial's sunrise/sunset glyphs.
 */

/** Mirrors helpers.py's `normalize_azimuth_angle`, but non-negative for a
 * negative input - JS `%` keeps the sign of the dividend where Python's does
 * not, and a bearing of -30 has to mean 330 on both sides. */
export function normalizeAzimuthAngle(angle: number): number {
  return ((angle % 360) + 360) % 360;
}

function dayOfYear(wall: Date): number {
  const start = Date.UTC(wall.getUTCFullYear(), 0, 1);
  const today = Date.UTC(
    wall.getUTCFullYear(),
    wall.getUTCMonth(),
    wall.getUTCDate(),
  );
  return Math.floor((today - start) / 86400000) + 1;
}

const RAD = Math.PI / 180;

/**
 * Solar azimuth in degrees (0=N, 90=E, 180=S, 270=W) at a UTC instant.
 * Port of `helpers.calculate_solar_azimuth`.
 *
 * Sub-second precision is dropped on purpose: Python reads `timestamp.second`
 * and never `.microsecond`, and `_refine_azimuth_time` hands it instants with
 * fractional seconds, so keeping milliseconds here would diverge from the
 * backend on exactly the values the refinement produces.
 */
export function solarAzimuthDegrees(
  latitude: number,
  longitude: number,
  wall: Date,
): number {
  const latRad = latitude * RAD;
  const declination =
    23.45 * Math.sin(((360 * (284 + dayOfYear(wall))) / 365) * RAD) * RAD;

  const timeDecimal =
    wall.getUTCHours() +
    wall.getUTCMinutes() / 60 +
    wall.getUTCSeconds() / 3600;
  // ADDED, not subtracted: east-positive longitude runs AHEAD of UTC, so local
  // solar time is UTC + longitude/15. The backend subtracted it until issue
  // #81, which is why an older version of this port did too.
  const solarTime = timeDecimal + longitude / 15;
  const hourAngle = (solarTime - 12) * 15 * RAD;

  const azimuth = Math.atan2(
    Math.sin(hourAngle),
    Math.cos(hourAngle) * Math.sin(latRad) -
      Math.tan(declination) * Math.cos(latRad),
  );
  return normalizeAzimuthAngle(azimuth / RAD + 180);
}

/** Port of `helpers._azimuth_crossed_target`. */
export function azimuthCrossedTarget(
  prevAzimuth: number,
  currentAzimuth: number,
  target: number,
): boolean {
  if (Math.abs(prevAzimuth - currentAzimuth) > 180) {
    if (prevAzimuth > currentAzimuth) {
      return target >= prevAzimuth || target <= currentAzimuth;
    }
    return target <= prevAzimuth || target >= currentAzimuth;
  }
  return (
    Math.min(prevAzimuth, currentAzimuth) <= target &&
    target <= Math.max(prevAzimuth, currentAzimuth)
  );
}

const SEARCH_INTERVAL_MS = 15 * 60 * 1000;

/** Port of `helpers._refine_azimuth_time` - binary search to the minute. */
function refineAzimuthTime(
  latitude: number,
  longitude: number,
  targetAzimuth: number,
  startMs: number,
  endMs: number,
): Date {
  let lo = startMs;
  let hi = endMs;
  while (hi - lo > 60000) {
    const mid = lo + (hi - lo) / 2;
    const midAzimuth = solarAzimuthDegrees(latitude, longitude, new Date(mid));
    const loAzimuth = solarAzimuthDegrees(latitude, longitude, new Date(lo));
    if (azimuthCrossedTarget(loAzimuth, midAzimuth, targetAzimuth)) {
      hi = mid;
    } else {
      lo = mid;
    }
  }
  return new Date(lo);
}

/**
 * The next instant at or after `from` when the sun reaches `targetAzimuth`, or
 * null if it does not within `maxDays`. Port of
 * `helpers.find_next_solar_azimuth_time`.
 *
 * Null is a real outcome, not just an error path: with this formula there are
 * latitude/target pairs the azimuth curve never crosses (the equator against
 * a due-east target is one), and the backend treats that as "no bound".
 */
export function findNextSolarAzimuthInstant(
  latitude: number,
  longitude: number,
  targetAzimuth: number,
  from: Date,
  maxDays = 1,
): Date | null {
  const startMs = from.getTime();
  const maxMs = startMs + maxDays * 86400000;

  let currentMs = startMs;
  let prevAzimuth = solarAzimuthDegrees(latitude, longitude, from);

  while (currentMs < maxMs) {
    currentMs += SEARCH_INTERVAL_MS;
    const currentAzimuth = solarAzimuthDegrees(
      latitude,
      longitude,
      new Date(currentMs),
    );
    if (azimuthCrossedTarget(prevAzimuth, currentAzimuth, targetAzimuth)) {
      return refineAzimuthTime(
        latitude,
        longitude,
        targetAzimuth,
        currentMs - SEARCH_INTERVAL_MS,
        currentMs,
      );
    }
    prevAzimuth = currentAzimuth;
  }
  return null;
}

/* ------------------------------------------------------------------ *
 * Frame bridging: wall clock in a zone <-> real instants.             *
 * ------------------------------------------------------------------ */

const ZONE_PART_FORMAT: Intl.DateTimeFormatOptions = {
  hour12: false,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
};

/** `instant` as a wall clock in `timeZone`, carried in a Date's UTC fields.
 * Falls back to the browser's own zone when the zone is missing or rejected
 * by Intl, which collapses to an identity for the ordinary case where Home
 * Assistant and the browser agree. */
export function wallClockNowInZone(
  timeZone: string | undefined,
  instant: Date,
): Date {
  if (!timeZone) return browserWallClock(instant);
  let parts: Intl.DateTimeFormatPart[];
  try {
    parts = new Intl.DateTimeFormat("en-US", {
      ...ZONE_PART_FORMAT,
      timeZone,
    }).formatToParts(instant);
  } catch {
    return browserWallClock(instant);
  }
  const get = (type: string) =>
    parseInt(parts.find((p) => p.type === type)?.value ?? "0", 10);
  // hourCycle h24 renders midnight as hour "24" on the day it starts, which
  // Date.UTC would roll forward into the NEXT day — a whole day out, and only
  // in the hour either side of midnight.
  const hour = get("hour") % 24;
  return new Date(
    Date.UTC(
      get("year"),
      get("month") - 1,
      get("day"),
      hour,
      get("minute"),
      get("second"),
    ),
  );
}

/**
 * The real instant whose `timeZone` wall clock is `wall` - the inverse of
 * `wallClockNowInZone`, needed to start a scan at a local midnight.
 *
 * Two passes: a zone's offset is itself a function of the instant, so the
 * first guess (the wall clock read as UTC) is refined once against the instant
 * it produces. Enough everywhere except inside a DST fold, where no answer is
 * right anyway.
 */
export function instantForWallClock(
  wall: Date,
  timeZone: string | undefined,
): Date {
  let instantMs = wall.getTime();
  for (let i = 0; i < 2; i++) {
    const offsetMs =
      wallClockNowInZone(timeZone, new Date(instantMs)).getTime() - instantMs;
    instantMs = wall.getTime() - offsetMs;
  }
  return new Date(instantMs);
}

function browserWallClock(instant: Date): Date {
  return new Date(
    Date.UTC(
      instant.getFullYear(),
      instant.getMonth(),
      instant.getDate(),
      instant.getHours(),
      instant.getMinutes(),
      instant.getSeconds(),
    ),
  );
}

/**
 * Minute-of-day of a wall clock produced by `wallClockNowInZone`, which
 * carries its hour and minute in the Date's UTC fields.
 *
 * The dial draws in HOME ASSISTANT's zone, not the browser's. That is not a
 * cosmetic choice: every other time in the dialog is a Home Assistant wall
 * clock (the Start/Finish clock inputs, the summary sentence, the times the
 * schedule actually fires at), so rendering the sun in the viewer's zone puts
 * two different clocks on one dial. A browser an hour off drew the window band
 * an hour from the times typed beside it, and a browser on UTC put a 20:42
 * sunset at 00:42 on the ring, moving the moon glyph most of the way round.
 */
export function wallClockMinutes(wall: Date): number {
  return wall.getUTCHours() * 60 + wall.getUTCMinutes();
}

/**
 * Minute-of-day, on the browser's clock, at which the sun next reaches
 * `azimuth` - the whole module in one call, for the dial. Null when the sun
 * never reaches that bearing.
 *
 * Resolution starts from midnight of the current day in Home Assistant's
 * zone rather than from "now", so the dial does not redraw a bound to
 * tomorrow's crossing as the day passes: the dial shows a schedule's shape,
 * not the next firing.
 */
/** The subset of `hass.config` this module reads. Declared structurally
 * rather than imported so the module keeps no dependency on the frontend's
 * types or on Lit. */
export interface SolarLocation {
  latitude?: number;
  longitude?: number;
  time_zone?: string;
}

/**
 * A resolver bound to one location and one moment, or undefined when the
 * location is unknown — never true on a live instance, possible mid-startup.
 * Callers treat undefined as "cannot resolve", which draws an end open rather
 * than pinning it to 0 degrees somewhere off the equator.
 *
 * Shared by the dial and the dialog's help text so the two cannot disagree
 * about whether a bearing resolves.
 */
export function azimuthResolverFromLocation(
  config: SolarLocation | undefined,
  now: Date,
): ((azimuth: number) => number | null) | undefined {
  if (
    typeof config?.latitude !== "number" ||
    typeof config?.longitude !== "number"
  )
    return undefined;
  const { latitude, longitude, time_zone: timeZone } = config;
  return (azimuth: number) =>
    azimuthBoundMinutes(latitude, longitude, azimuth, timeZone, now);
}

export function azimuthBoundMinutes(
  latitude: number,
  longitude: number,
  azimuth: number,
  timeZone: string | undefined,
  now: Date,
): number | null {
  // The DAY is Home Assistant's local one; the instants scanned across it are
  // UTC, because that is the frame the azimuth formula reads. Same split the
  // backend's own backward walk makes.
  const nowWall = wallClockNowInZone(timeZone, now);
  const midnightWall = new Date(
    Date.UTC(
      nowWall.getUTCFullYear(),
      nowWall.getUTCMonth(),
      nowWall.getUTCDate(),
    ),
  );
  const crossing = findNextSolarAzimuthInstant(
    latitude,
    longitude,
    normalizeAzimuthAngle(azimuth),
    instantForWallClock(midnightWall, timeZone),
  );
  if (crossing === null) return null;
  return wallClockMinutes(wallClockNowInZone(timeZone, crossing));
}
