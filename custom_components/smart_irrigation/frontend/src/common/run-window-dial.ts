import {
  SCHEDULE_BOUND_MODE_NONE,
  SCHEDULE_BOUND_MODE_TIME,
  SCHEDULE_BOUND_MODE_SUNRISE,
  SCHEDULE_BOUND_MODE_SUNSET,
  SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
  SCHEDULE_ANCHOR_FINISH,
  SCHEDULE_RECURRENCE_INTERVAL,
} from "../const";
import { DEFAULT_AZIMUTH, EndRow, ScheduleRows } from "./schedule-rows";

/**
 * Pure geometry + planning for the WHEN section's 24-hour dial (GitLab #31).
 * No Lit, no DOM: every function here returns plain numbers, path-data
 * strings or descriptor objects, so the exact numeric/geometric acceptance
 * criteria (15-degree minimum arc, butt-cap fades, wrap fade, centre value
 * per state) are checkable in schedule-rows.test.ts style tests rather than
 * by eyeballing rendered SVG. The Lit component (si-run-window-dial.ts) only
 * wraps this module's output in svg/html templates and localizes copy.
 *
 * Ported from the throwaway prototype at
 * plans/prototypes/schedule-ui.html (design/schedule-ui-prototype), which
 * settled every visual constant below. Two differences from the prototype,
 * both because the real data shape differs from its mock:
 *  - The prototype fed the run bar from a mock "tonight" plan. Here the run
 *    length always comes from nominal demand (GitLab #26), independent of
 *    any zone's live bucket, per the ticket's explicit requirement that a
 *    long-lived schedule not be visualized from a one-night sample.
 *  - The prototype's FLIP toggle (an earlier iteration that could render
 *    either orientation) is gone — noon-at-top is now the only orientation,
 *    so it is baked directly into the angle formula rather than kept as a
 *    runtime switch.
 */

const MINUTES_PER_DAY = 1440;

// Dial geometry, in the SVG's own 132x132 viewBox units. Settled by the
// prototype; do not change without re-checking the prototype render.
export const DIAL_CENTER = 66;
export const DIAL_RADIUS = 44;
export const DIAL_RING = 10;
export const DIAL_ICON_RADIUS = 57;
export const DIAL_RUN_HALF_WIDTH = 5;
export const DIAL_CAP_RADIUS = 1.8;
// Below this an arc is shorter than the stroke is wide (10 units at r=44 is
// ~52 minutes) and reads as a dot rather than a span. Also exactly the
// ticket's "15 degree minimum" (1440 minutes / 24 = 60 minutes per 15deg).
export const DIAL_MIN_VISIBLE_MINUTES = 60;
// How far an open (unbounded) end's fade extends past the run it borders.
const FADE_MINUTES = 260;

function clampMinutes(m: number): number {
  return ((m % MINUTES_PER_DAY) + MINUTES_PER_DAY) % MINUTES_PER_DAY;
}

export function fmtClock(mins: number): string {
  const m = Math.round(clampMinutes(mins));
  const h = Math.floor(m / 60);
  const mm = m % 60;
  return `${String(h).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

export function fmtDuration(mins: number): string {
  const h = Math.floor(mins / 60);
  const m = Math.round(mins % 60);
  return h ? `${h}h ${m}m` : `${m}m`;
}

/**
 * Minute-of-day -> dial coordinates. Noon at the top, midnight at the
 * bottom: at mins=0 the angle points straight down (below center, since SVG
 * y grows downward); at mins=720 it points straight up. This is the
 * prototype's `polar()` with FLIP permanently folded in (see module doc).
 */
export function polar(rad: number, mins: number): [number, number] {
  const ang = (mins / MINUTES_PER_DAY) * 2 * Math.PI + Math.PI / 2;
  return [DIAL_CENTER + rad * Math.cos(ang), DIAL_CENTER + rad * Math.sin(ang)];
}

/** SVG arc path `d` from `from` to `to` (minutes-of-day, `to` may exceed
 * 1440 to sweep across midnight). A full-circle sweep is nudged just short
 * of closing, since a single `A` command cannot draw one. */
export function arcPath(rad: number, from: number, to: number): string {
  const sweep = to - from;
  const end = sweep >= MINUTES_PER_DAY ? from + MINUTES_PER_DAY - 0.5 : to;
  const [x1, y1] = polar(rad, from);
  const [x2, y2] = polar(rad, end);
  const largeArc = end - from > MINUTES_PER_DAY / 2 ? 1 : 0;
  return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${rad} ${rad} 0 ${largeArc} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`;
}

/**
 * One end-cap of the run bar, as filled geometry rather than a stroke cap —
 * a stroke cap grows ALONG the arc by half the stroke width (5 units, ~26
 * minutes at this radius), so at this dial's scale a round linecap on a
 * short bar would swallow most of it. Built in unrolled (arc-length, radial)
 * space and mapped back through `polar`, so `q` is a genuine corner radius:
 * q = hw gives the semicircle a round linecap would, q < hw gives a flat end
 * with softened corners that no linecap value can express. Extends only away
 * from the bar (toward `dir`), never back into it.
 */
export function capFill(
  r: number,
  mins: number,
  hw: number,
  q: number,
  dir: -1 | 1,
): string {
  const per = (2 * Math.PI * r) / MINUTES_PER_DAY; // arc units per minute
  const toM = (x: number) => mins - (dir * x) / per;
  const pts: [number, number][] = [[0, hw]];
  const N = 10;
  for (let i = 0; i <= N; i++) {
    const th = Math.PI / 2 + (i / N) * (Math.PI / 2);
    pts.push([q * Math.cos(th), hw - q + q * Math.sin(th)]);
  }
  for (let i = 0; i <= N; i++) {
    const th = Math.PI + (i / N) * (Math.PI / 2);
    pts.push([q * Math.cos(th), -(hw - q) + q * Math.sin(th)]);
  }
  pts.push([0, -hw]);
  return (
    pts
      .map(([x, y], i) => {
        const [px, py] = polar(r + y, toM(x));
        return `${i ? "L" : "M"} ${px.toFixed(2)} ${py.toFixed(2)}`;
      })
      .join(" ") + " Z"
  );
}

export interface FadeSegment {
  d: string;
  opacity: number;
}

/**
 * An arc broken into many short butt-capped segments with per-segment
 * opacity, so an unbounded end (or a wrap-crossing run) trails off instead
 * of ending on a hard edge. MUST be rendered with an inline
 * `style="stroke-linecap:butt"` on each segment, never a CSS class or
 * presentation attribute — an SVG presentation attribute loses to any CSS
 * rule that sets `stroke-linecap`, so a class-level round linecap would
 * silently win while `stroke-linecap="butt"` read back correctly and did
 * nothing. Round caps would also turn each short segment into a full-width
 * blob (10 units wide against a ~0.2-unit-long segment), and 48 stacked
 * blobs read as one solid lump rather than a fade.
 */
export function fadedArc(
  from: number,
  to: number,
  fadeFrom: number,
  fadeTo: number,
  rad: number,
): FadeSegment[] {
  const STEPS = 48;
  const w = (to - from) / STEPS;
  const out: FadeSegment[] = [];
  for (let i = 0; i < STEPS; i++) {
    const a = from + i * w;
    const mid = a + w / 2;
    let op = 1;
    if (fadeFrom > 0) op = Math.min(op, (mid - from) / fadeFrom);
    if (fadeTo > 0) op = Math.min(op, (to - mid) / fadeTo);
    op = Math.max(0, Math.min(1, op));
    out.push({ d: arcPath(rad, a, a + w * 1.25), opacity: op });
  }
  return out;
}

function parseHM(hm: string): number {
  const [h, m] = hm.split(":").map((n) => parseInt(n, 10));
  return (h || 0) * 60 + (m || 0);
}

/** Resolves a solar-azimuth bearing to a clock-minute. Supplied by the
 * caller rather than imported here so this module stays free of Date and
 * timezone handling: si-run-window-dial.ts owns every conversion between a
 * real instant and the minute-of-day this module draws in, for the sun glyph
 * and an azimuth bound alike. `null` for a bearing the sun never reaches. */
export type AzimuthResolver = (azimuth: number) => number | null;

/**
 * A row's absolute clock-minute, given real sunrise/sunset. `null` means
 * "no bound to draw" — either the row is genuinely unbounded (mode "none"),
 * or it is azimuth-bounded and no resolver was supplied, or the resolver
 * reported a bearing the sun never reaches (which is what the scheduler
 * makes of it too: `_resolve_event_instant` returns None and the bound goes
 * unresolved). Such a row renders the same way an open end does: faded
 * rather than a hard edge. This only affects the dial's drawing, not save
 * validity (describeWindow in schedule-rows.ts, which drives the Save
 * button, treats azimuth as bounded regardless).
 */
export function resolveAbsMinutes(
  row: EndRow,
  sunriseMinutes: number,
  sunsetMinutes: number,
  azimuthResolver?: AzimuthResolver,
): number | null {
  switch (row.mode) {
    case SCHEDULE_BOUND_MODE_TIME:
      return clampMinutes(parseHM(row.time ?? "06:00"));
    case SCHEDULE_BOUND_MODE_SUNRISE:
      return clampMinutes(sunriseMinutes + (row.offset ?? 0));
    case SCHEDULE_BOUND_MODE_SUNSET:
      return clampMinutes(sunsetMinutes + (row.offset ?? 0));
    case SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH: {
      if (!azimuthResolver) return null;
      const minutes = azimuthResolver(row.azimuth ?? DEFAULT_AZIMUTH);
      return minutes === null ? null : clampMinutes(minutes);
    }
    case SCHEDULE_BOUND_MODE_NONE:
    default:
      return null;
  }
}

export interface IntervalPlan {
  runs: [number, number][];
  overlaps: [number, number][];
  wrapAt: number;
}

/**
 * Interval occurrences across one day, plus any that collide. The run
 * length is not clamped to the gap between occurrences: a run that is still
 * going when the next occurrence is due IS the thing worth flagging.
 * Nothing overlaps and nothing queues in the real scheduler — a zone with a
 * run in flight is dropped from the second dispatch and the rest of that
 * occurrence proceeds — so a collision costs a zone, not a delay. Only
 * same-day collisions are computed here; the last occurrence spilling past
 * midnight into tomorrow's first is a different thing, handled by the
 * caller via `fadedArc`/wrapAt.
 */
export function intervalPlan(
  needMinutes: number,
  intervalHours: number | undefined,
  intervalStartTime: string | undefined,
): IntervalPlan {
  const every = Math.max(1, Number(intervalHours) || 24) * 60;
  const first = intervalStartTime ? parseHM(intervalStartTime) : 0;
  const runs: [number, number][] = [];
  for (
    let t = first;
    t < first + MINUTES_PER_DAY && runs.length < 24;
    t += every
  ) {
    runs.push([t, t + needMinutes]);
  }
  const overlaps: [number, number][] = [];
  for (let i = 0; i + 1 < runs.length; i++) {
    if (runs[i][1] > runs[i + 1][0]) {
      overlaps.push([runs[i + 1][0], Math.min(runs[i][1], runs[i + 1][1])]);
    }
  }
  return { runs, overlaps, wrapAt: first + MINUTES_PER_DAY };
}

export type CentreKind = "window" | "run" | "interval" | "invalid";

export interface CentreInfo {
  kind: CentreKind;
  minutes?: number; // "window" | "run"
  perDay?: number; // "interval"
  intervalHours?: number; // "interval"
}

export type RunBar =
  | { wraps: false; arc: string; capStart: string; capEnd: string }
  | { wraps: true; capStart: string; fade: FadeSegment[] };

export interface DialModel {
  trackPath: string;
  windowArc:
    | { kind: "solid"; d: string }
    | { kind: "faded"; segments: FadeSegment[] }
    | null;
  dottedPath: string | null;
  runs: RunBar[];
  overlaps: { d: string; fromMinutes: number; toMinutes: number }[];
  ticks: { x1: number; y1: number; x2: number; y2: number }[];
  sun: { x: number; y: number; minutes: number };
  moon: { x: number; y: number; minutes: number };
  drops: { x: number; y: number; fromMinutes: number; toMinutes: number }[];
  centre: CentreInfo;
}

export interface DialInput {
  rows: ScheduleRows;
  recurrence: string;
  intervalHours?: number;
  intervalStartTime?: string;
  /** Nominal demand, in minutes — already converted from
   * `nominal_demand_seconds` by the caller. Never a live plan; see module
   * doc. */
  nominalDemandMinutes: number;
  sunriseMinutes: number;
  sunsetMinutes: number;
  /** Optional; omitted, an azimuth-bounded end draws as an open one. */
  azimuthResolver?: AzimuthResolver;
}

function runBar(a: number, b: number): RunBar {
  return {
    wraps: false,
    arc: arcPath(DIAL_RADIUS, a, b),
    capStart: capFill(DIAL_RADIUS, a, DIAL_RUN_HALF_WIDTH, DIAL_CAP_RADIUS, -1),
    capEnd: capFill(DIAL_RADIUS, b, DIAL_RUN_HALF_WIDTH, DIAL_CAP_RADIUS, 1),
  };
}

export function buildDial(input: DialInput): DialModel {
  const {
    rows,
    recurrence,
    intervalHours,
    intervalStartTime,
    nominalDemandMinutes,
    sunriseMinutes,
    sunsetMinutes,
    azimuthResolver,
  } = input;

  const trackPath = arcPath(DIAL_RADIUS, 0, MINUTES_PER_DAY);
  const ticks = [0, 360, 720, 1080].map((m) => {
    const [x1, y1] = polar(DIAL_RADIUS - DIAL_RING / 2 - 1, m);
    const [x2, y2] = polar(DIAL_RADIUS + DIAL_RING / 2 + 1, m);
    return { x1, y1, x2, y2 };
  });
  const [sx, sy] = polar(DIAL_ICON_RADIUS, sunriseMinutes);
  const [mx, my] = polar(DIAL_ICON_RADIUS, sunsetMinutes);

  const interval = recurrence === SCHEDULE_RECURRENCE_INTERVAL;

  if (interval) {
    const { runs, overlaps, wrapAt } = intervalPlan(
      nominalDemandMinutes,
      intervalHours,
      intervalStartTime,
    );
    const runBars: RunBar[] = runs.map(([a, b]) => {
      if (b <= wrapAt) return runBar(a, b);
      // The overrun is shown by fading this run out before it reaches the
      // next occurrence rather than by drawing the part that belongs to
      // tomorrow: that part lands on exactly the arc tomorrow's first run
      // occupies, so at this radius it would be invisible (or, at any other
      // radius, a confusing second ring).
      const stop = wrapAt - 8; // never quite touches
      const span = stop - a;
      const tail = Math.min(span, 120);
      return {
        wraps: true,
        capStart: capFill(
          DIAL_RADIUS,
          a,
          DIAL_RUN_HALF_WIDTH,
          DIAL_CAP_RADIUS,
          -1,
        ),
        fade: fadedArc(a, stop, 0, tail, DIAL_RADIUS),
      };
    });
    return {
      trackPath,
      windowArc: null,
      dottedPath: null,
      runs: runBars,
      overlaps: overlaps.map(([a, b]) => ({
        d: arcPath(DIAL_RADIUS, a, b),
        fromMinutes: a,
        toMinutes: b,
      })),
      ticks,
      sun: { x: sx, y: sy, minutes: sunriseMinutes },
      moon: { x: mx, y: my, minutes: sunsetMinutes },
      drops: runs.map(([a, b]) => {
        const [x, y] = polar(DIAL_ICON_RADIUS, (a + b) / 2);
        return { x, y, fromMinutes: a, toMinutes: b };
      }),
      centre: {
        kind: "interval",
        perDay: runs.length,
        intervalHours: Math.max(1, Number(intervalHours) || 24),
      },
    };
  }

  const startAbs = resolveAbsMinutes(
    rows.start,
    sunriseMinutes,
    sunsetMinutes,
    azimuthResolver,
  );
  let finishAbs = resolveAbsMinutes(
    rows.finish,
    sunriseMinutes,
    sunsetMinutes,
    azimuthResolver,
  );
  // Unwrap the pair ONCE, here, so that every consumer downstream gets a
  // monotonically increasing span and none of them has to re-derive the wrap.
  // An overnight window's finish is a smaller minute-of-day than its start
  // (17:44 to 09:50), and handing that raw to arcPath makes the sweep negative:
  // its large-arc flag then reads 0, and SVG draws whichever of the two
  // candidate arcs is under 180 degrees, which is the COMPLEMENT of the window.
  // Invisible below a 12h span, because there the intended arc is the short one
  // anyway, and a band on the wrong side of the dial above it.
  if (startAbs !== null && finishAbs !== null && finishAbs <= startAbs) {
    finishAbs += MINUTES_PER_DAY;
  }
  const noEnds = startAbs === null && finishAbs === null;

  if (noEnds) {
    return {
      trackPath,
      windowArc: null,
      dottedPath: null,
      runs: [],
      overlaps: [],
      ticks,
      sun: { x: sx, y: sy, minutes: sunriseMinutes },
      moon: { x: mx, y: my, minutes: sunsetMinutes },
      drops: [],
      centre: { kind: "invalid" },
    };
  }

  // Already unwrapped above, so this is a plain span in 1..1440 rather than a
  // modular difference; equal ends mean a whole day, not an empty window.
  const windowMins =
    startAbs !== null && finishAbs !== null ? finishAbs - startAbs : null;

  let runStart: number;
  let runLen: number;
  let unserved = 0;
  if (startAbs !== null && finishAbs !== null) {
    const win = windowMins as number;
    runLen = Math.min(nominalDemandMinutes, win);
    unserved = Math.max(0, nominalDemandMinutes - win);
    runStart =
      rows.anchor === SCHEDULE_ANCHOR_FINISH ? finishAbs - runLen : startAbs;
  } else if (startAbs !== null) {
    runStart = startAbs;
    runLen = nominalDemandMinutes;
  } else {
    // finishAbs !== null
    runLen = nominalDemandMinutes;
    runStart = (finishAbs as number) - runLen;
  }
  const runEnd = runStart + runLen;

  let winA = startAbs ?? runStart;
  let winB = finishAbs ?? runEnd;
  let fadeA = 0;
  let fadeB = 0;
  if (startAbs === null) {
    winA = runStart - FADE_MINUTES;
    fadeA = FADE_MINUTES;
  }
  if (finishAbs === null) {
    winB = runEnd + FADE_MINUTES;
    fadeB = FADE_MINUTES;
  }

  const tiny = windowMins !== null && windowMins < DIAL_MIN_VISIBLE_MINUTES;
  const windowArc:
    | { kind: "solid"; d: string }
    | { kind: "faded"; segments: FadeSegment[] } =
    startAbs === null || finishAbs === null
      ? {
          kind: "faded",
          segments: fadedArc(winA, winB, fadeA, fadeB, DIAL_RADIUS),
        }
      : {
          kind: "solid",
          d: arcPath(
            DIAL_RADIUS,
            winA,
            tiny ? winA + DIAL_MIN_VISIBLE_MINUTES : winB,
          ),
        };

  // Unserved demand: everything the resolved window can't fit, laid back
  // from wherever the run itself starts, so the part sticking out past the
  // window's start is exactly what got cut.
  const dottedPath =
    unserved > 1 ? arcPath(DIAL_RADIUS, runStart - unserved, runStart) : null;

  const [dx, dy] = polar(DIAL_ICON_RADIUS, (runStart + runEnd) / 2);

  const centre: CentreInfo =
    windowMins === null
      ? { kind: "run", minutes: runLen }
      : { kind: "window", minutes: windowMins };

  return {
    trackPath,
    windowArc,
    dottedPath,
    runs: [runBar(runStart, runEnd)],
    overlaps: [],
    ticks,
    sun: { x: sx, y: sy, minutes: sunriseMinutes },
    moon: { x: mx, y: my, minutes: sunsetMinutes },
    drops: [{ x: dx, y: dy, fromMinutes: runStart, toMinutes: runEnd }],
    centre,
  };
}
