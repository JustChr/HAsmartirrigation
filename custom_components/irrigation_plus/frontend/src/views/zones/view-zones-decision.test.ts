import { describe, it, expect, beforeAll } from "vitest";

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

type ViewModule = typeof import("./view-zones");
let View: ViewModule["SmartIrrigationViewZones"];
beforeAll(async () => {
  ({ SmartIrrigationViewZones: View } = await import("./view-zones"));
});

function flatten(node: any): string {
  let text = "";
  const walk = (n: any) => {
    if (n == null || typeof n === "boolean") return;
    if (Array.isArray(n)) return n.forEach(walk);
    if (n && Array.isArray(n.strings) && "values" in n) {
      text += n.strings.join("");
      return walk(n.values);
    }
    if (typeof n === "function") return;
    text += String(n);
  };
  walk(node);
  return text;
}

// Committed duration 0 with a deficit the daily calc has already satisfied:
// exactly the case where the two paths disagree.
const ZONE = {
  id: 1,
  name: "Lawn",
  state: "automatic",
  last_calculated: "2026-08-06T23:00:00",
  duration: 0,
  bucket: 0,
  bucket_threshold: -1,
};

function estimate(overrides: Record<string, unknown> = {}) {
  return {
    available: true,
    method: "hourly_sensor",
    et_since: 5,
    precip_since: 0,
    drainage_since: 0,
    live_deficit: -5,
    live_duration: 600,
    as_of: null,
    ...overrides,
  };
}

function make(liveEnabled: boolean, est?: Record<string, unknown>) {
  const el: any = new View();
  el.hass = { language: "en" };
  el.config = { live_estimate_enabled: liveEnabled };
  el._outlook = {
    skip_preview: { would_skip: false, checks: [] },
    upcoming_runs: [],
    zone_estimates: est ? { "1": est } : {},
  };
  return el;
}

describe("view-zones decision line", () => {
  it("sizes the run from the live bucket when live-estimate watering is on", () => {
    const text = flatten(make(true, estimate())._renderZoneDecision(ZONE));
    // 600 s from the live deficit, not the committed 0 s.
    expect(text).toContain("10 min");
    expect(text).not.toContain("No watering needed");
  });

  it("does not report 'no water' for a zone whose committed duration is zero", () => {
    const text = flatten(make(true, estimate())._renderZoneDecision(ZONE));
    expect(text).toContain("Deficit ~10 min");
  });

  it("keeps the committed duration and decision when the feature is off", () => {
    const text = flatten(make(false, estimate())._renderZoneDecision(ZONE));
    expect(text).toContain("No watering needed");
    expect(text).not.toContain("10 min");
  });

  it("still waters on the committed figures when the feature is off", () => {
    const zone = { ...ZONE, duration: 300, bucket: -5 };
    const text = flatten(make(false, estimate())._renderZoneDecision(zone));
    expect(text).toContain("5 min");
  });

  it("falls back to the committed figures when no live bucket is available", () => {
    const zone = { ...ZONE, duration: 300, bucket: -5 };
    const text = flatten(make(true)._renderZoneDecision(zone));
    expect(text).toContain("5 min");
  });

  it("falls back to the committed figures for a zone with no live duration", () => {
    // Flow-metered zones keep the daily gate, so the backend publishes none.
    const zone = { ...ZONE, duration: 300, bucket: -5 };
    const est = estimate({ live_duration: null });
    const text = flatten(make(true, est)._renderZoneDecision(zone));
    expect(text).toContain("5 min");
  });

  it("drops the zone when intra-day rain has covered the live deficit", () => {
    const zone = { ...ZONE, duration: 300, bucket: -5 };
    const est = estimate({ live_deficit: 2, live_duration: 0 });
    const text = flatten(make(true, est)._renderZoneDecision(zone));
    expect(text).toContain("No watering needed");
  });
});
