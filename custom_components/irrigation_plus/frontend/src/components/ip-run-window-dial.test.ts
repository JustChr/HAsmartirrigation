import {
  describe,
  it,
  expect,
  beforeAll,
  beforeEach,
  afterEach,
  vi,
} from "vitest";

// Same DOM-free shim as ip-schedule-dialog.test.ts / ip-distributor-form.test.ts:
// enough for the LitElement subclass to be defined and instantiated without a
// real custom-element registry or shadow DOM. render() is called directly and
// the returned lit TemplateResult tree is introspected.
beforeAll(() => {
  (globalThis as any).HTMLElement = class {};
  (globalThis as any).customElements = {
    define() {},
    get() {
      return undefined;
    },
    whenDefined: () => Promise.resolve(),
  };
  (globalThis as any).window = globalThis;
});

type DialModule = typeof import("./ip-run-window-dial");
let SiRunWindowDial: DialModule["SiRunWindowDial"];

beforeAll(async () => {
  ({ SiRunWindowDial } = await import("./ip-run-window-dial"));
});

/** Flattens a lit TemplateResult (svg or html) tree into concatenated static
 * markup plus dynamic values, mirroring ip-schedule-dialog.test.ts's helper —
 * the dial nests `svg` templates inside an `html` template the same way.
 * NOTE: statics and values are concatenated in two separate passes (all of a
 * template's static strings, then all of its values), not interleaved at
 * each placeholder — so `text` is only safe for substring checks on content
 * that is unique across the whole tree; anything that could collide with
 * unrelated copy (e.g. a short label like "run") should be asserted via the
 * `values` array instead, which holds each dynamic leaf exactly as rendered. */
function flatten(node: any): { text: string; values: any[] } {
  const out = { text: "", values: [] as any[] };
  const walk = (n: any) => {
    if (n == null || typeof n === "boolean") return;
    if (Array.isArray(n)) {
      n.forEach(walk);
      return;
    }
    if (n && Array.isArray(n.strings) && "values" in n) {
      out.text += n.strings.join("");
      walk(n.values);
      return;
    }
    if (typeof n === "function") return;
    out.values.push(n);
    out.text += String(n);
  };
  walk(node);
  return out;
}

function makeDial(overrides: Partial<Record<string, any>> = {}) {
  const el: any = new SiRunWindowDial();
  el.hass = {
    language: "en",
    states: {
      "sun.sun": {
        attributes: {
          next_rising: "2026-08-10T10:12:00Z",
          next_setting: "2026-08-10T20:31:00Z",
        },
      },
      ...(overrides.states ?? {}),
    },
    config:
      "config" in overrides
        ? overrides.config
        : {
            latitude: 33.45,
            longitude: -112.07,
            time_zone: "America/Phoenix",
          },
  };
  el.rows = overrides.rows ?? {
    start: { mode: "time", time: "06:00" },
    finish: { mode: "time", time: "20:00" },
    anchor: "finish",
  };
  el.recurrence = overrides.recurrence ?? "daily";
  el.intervalHours = overrides.intervalHours;
  el.intervalStartTime = overrides.intervalStartTime;
  el.nominalDemandSeconds = overrides.nominalDemandSeconds ?? 1800;
  return el;
}

describe("ip-run-window-dial", () => {
  it("renders an SVG carrying its documented aria-label", () => {
    const el = makeDial();
    const { text } = flatten(el.render());
    expect(text).toContain("<svg");
    expect(text).toContain("Run window on a 24 hour dial");
  });

  it("renders sun/moon glyph hover text on Home Assistant's clock", () => {
    const el = makeDial();
    const { text } = flatten(el.render());
    // Home Assistant is in Phoenix (UTC-7, no DST), so 10:12Z is 03:12 and
    // 20:31Z is 13:31 there. Hardcoded rather than derived from the runner's
    // own zone on purpose: the dial must read the same wherever it is viewed
    // from, because the schedule fires on Home Assistant's clock.
    expect(text).toContain("Sunrise 03:12");
    expect(text).toContain("Sunset 13:31");
  });

  it("renders one drop with hover text per run occurrence", () => {
    const el = makeDial({
      recurrence: "interval",
      intervalHours: 6,
      intervalStartTime: "00:00",
      nominalDemandSeconds: 1800,
    });
    const { text } = flatten(el.render());
    // 4 occurrences across the day (00:00, 06:00, 12:00, 18:00).
    expect(text.split("<title>").length - 1).toBeGreaterThanOrEqual(4 + 2); // +sun +moon
    expect(text).toContain("Run 00:00 to 00:30");
  });

  it("reports window duration in the centre for a fully bounded window", () => {
    const el = makeDial();
    const { values } = flatten(el.render());
    expect(values).toContain("14h 0m");
    expect(values).toContain("window");
  });

  it("reports run duration in the centre when one end is open", () => {
    const el = makeDial({
      rows: {
        start: { mode: "time", time: "06:00" },
        finish: { mode: "none" },
        anchor: "finish",
      },
      nominalDemandSeconds: 45 * 60,
    });
    const { values } = flatten(el.render());
    expect(values).toContain("45m");
    expect(values).toContain("run");
  });

  it("renders a bare dash with no label when both ends are open", () => {
    const el = makeDial({
      rows: {
        start: { mode: "none" },
        finish: { mode: "none" },
        anchor: "finish",
      },
    });
    const { values } = flatten(el.render());
    expect(values).toContain("—");
    expect(values).not.toContain("window");
    expect(values).not.toContain("run");
    expect(values).toContain(""); // the empty label
  });

  it("draws unserved demand as a dotted arc, and fade segments with an inline butt-cap style", () => {
    const el = makeDial({
      rows: {
        start: { mode: "time", time: "06:00" },
        finish: { mode: "time", time: "07:00" },
        anchor: "finish",
      },
      nominalDemandSeconds: 2 * 3600, // twice the 1h window
    });
    const { text } = flatten(el.render());
    expect(text).toContain('class="d-dotted"');
    // Fade / wrap segments (and the solid window arc's own butt style, when
    // present) must set the linecap as an inline style attribute, never rely
    // on a class — a presentation attribute loses to CSS, but an inline
    // style wins over any class rule.
    expect(text).toContain('style="stroke-linecap:butt"');
  });

  it("marks same-day interval collisions and captions them as skipping zones still watering", () => {
    const el = makeDial({
      recurrence: "interval",
      intervalHours: 3,
      intervalStartTime: "00:00",
      nominalDemandSeconds: 4 * 3600, // 4h runs every 3h: guaranteed collision
    });
    const { text } = flatten(el.render());
    expect(text).toContain('class="d-overlap"');
    expect(text).toContain("zones still watering are skipped");
  });

  it("renders run-bar ends as filled cap geometry (cap-run), not a rounded stroke", () => {
    const el = makeDial();
    const { text } = flatten(el.render());
    expect(text).toContain('class="cap-run"');
  });

  it("renders nothing when hass or rows are not set", () => {
    const el: any = new SiRunWindowDial();
    const { text } = flatten(el.render());
    expect(text).toBe("");
  });
});

describe("ip-run-window-dial: run bar is fed from nominal demand, not a live plan", () => {
  it("changing nominalDemandSeconds alone changes the run/centre — there is no bucket-derived input at all", () => {
    const short = makeDial({
      rows: {
        start: { mode: "time", time: "06:00" },
        finish: { mode: "none" },
        anchor: "finish",
      },
      nominalDemandSeconds: 10 * 60,
    });
    const long = makeDial({
      rows: {
        start: { mode: "time", time: "06:00" },
        finish: { mode: "none" },
        anchor: "finish",
      },
      nominalDemandSeconds: 40 * 60,
    });
    const shortText = flatten(short.render()).text;
    const longText = flatten(long.render()).text;
    expect(shortText).toContain("10m");
    expect(longText).toContain("40m");
    // The component's public props (see class body) are exactly:
    // hass, rows, recurrence, intervalHours, intervalStartTime,
    // nominalDemandSeconds — no zone/bucket field exists to feed instead.
    expect(Object.keys(short)).not.toContain("bucket");
    expect(Object.keys(short)).not.toContain("zones");
  });
});

describe("ip-run-window-dial: solar-azimuth bounds", () => {
  const azimuthRows = (azimuth: number) => ({
    start: { mode: "solar_azimuth", azimuth },
    finish: { mode: "time", time: "20:00" },
    anchor: "finish",
  });

  // A solar bound depends on the day it is resolved on, so the clock is
  // pinned to the date the goldens in solar-azimuth.test.ts were generated
  // for. Home Assistant sits in Phoenix throughout; the browser stays in
  // whatever zone the runner uses, which is the point of the frame test.
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-06-21T12:00:00Z"));
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("draws an azimuth-bounded end as a hard edge, not an open one", () => {
    const el = makeDial({ rows: azimuthRows(270) });
    const { values } = flatten(el.render());
    // A resolved window reports its duration in the centre; an unresolved end
    // would leave the run duration there instead.
    expect(values).toContain("window");
  });

  it("puts an azimuth bound on Home Assistant's clock, like the sun glyph", () => {
    // The backend resolver puts 270 degrees at 22:44 UTC on this date (see
    // solar-azimuth.test.ts's goldens), which is 15:44 in Phoenix, and the
    // finish bound is 20:00 on that same clock, so the window is 4h 16m.
    // Independent of the runner's own zone, which is the whole point: one
    // dial, one clock.
    const el = makeDial({ rows: azimuthRows(270) });
    const { values } = flatten(el.render());
    expect(values).toContain("4h 16m"); // the centre's window duration
  });

  it("moves the bound with Home Assistant's zone, not the browser's", () => {
    const phoenix = flatten(makeDial({ rows: azimuthRows(270) }).render()).text;
    const tokyo = flatten(
      makeDial({
        rows: azimuthRows(270),
        config: {
          latitude: 33.45,
          longitude: -112.07,
          time_zone: "Asia/Tokyo",
        },
      }).render(),
    ).text;
    // Same bearing, same coordinates, same viewer: only the zone the wall
    // clock belongs to differs, so the drawn bound must differ too.
    expect(tokyo).not.toBe(phoenix);
  });

  it("draws the end open when a bearing the sun never reaches is set", () => {
    const el = makeDial({
      rows: azimuthRows(90),
      config: { latitude: 0, longitude: 0, time_zone: "UTC" },
    });
    const { values } = flatten(el.render());
    expect(values).toContain("run");
  });

  it("draws the end open when hass carries no location", () => {
    const el = makeDial({ rows: azimuthRows(270), config: undefined });
    const { values } = flatten(el.render());
    expect(values).toContain("run");
  });
});
