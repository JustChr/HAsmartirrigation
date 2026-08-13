import { describe, it, expect, beforeAll } from "vitest";

// Same DOM-free shim as si-schedule-dialog.test.ts / si-distributor-form.test.ts:
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

type DialModule = typeof import("./si-run-window-dial");
let SiRunWindowDial: DialModule["SiRunWindowDial"];

beforeAll(async () => {
  ({ SiRunWindowDial } = await import("./si-run-window-dial"));
});

/** Flattens a lit TemplateResult (svg or html) tree into concatenated static
 * markup plus dynamic values, mirroring si-schedule-dialog.test.ts's helper —
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

describe("si-run-window-dial", () => {
  it("renders an SVG with the ticket's aria-label", () => {
    const el = makeDial();
    const { text } = flatten(el.render());
    expect(text).toContain("<svg");
    expect(text).toContain("Run window on a 24 hour dial");
  });

  it("renders sun/moon glyph hover text with the resolved sunrise/sunset clock time", () => {
    const el = makeDial();
    const { text } = flatten(el.render());
    // Resolved through the local timezone the test runs in (same conversion
    // the component itself does), not hardcoded to the fixture's UTC value.
    const rising = new Date("2026-08-10T10:12:00Z");
    const setting = new Date("2026-08-10T20:31:00Z");
    const pad = (n: number) => String(n).padStart(2, "0");
    expect(text).toContain(
      `Sunrise ${pad(rising.getHours())}:${pad(rising.getMinutes())}`,
    );
    expect(text).toContain(
      `Sunset ${pad(setting.getHours())}:${pad(setting.getMinutes())}`,
    );
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

describe("si-run-window-dial: run bar is fed from nominal demand, not a live plan", () => {
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
