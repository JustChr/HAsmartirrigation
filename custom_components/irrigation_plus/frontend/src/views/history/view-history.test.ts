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

type Mod = typeof import("./view-history");
let SmartIrrigationViewHistory: Mod["SmartIrrigationViewHistory"];

beforeAll(async () => {
  ({ SmartIrrigationViewHistory } = await import("./view-history"));
});

function flatten(node: any): { text: string; values: any[] } {
  const out = { text: "", values: [] as any[] };
  const walk = (n: any) => {
    if (n == null || typeof n === "boolean") return;
    if (Array.isArray(n)) return n.forEach(walk);
    if (n && Array.isArray(n.strings) && "values" in n) {
      out.text += n.strings.join("");
      return walk(n.values);
    }
    out.values.push(n);
    out.text += String(n);
  };
  walk(node);
  return out;
}

function makeView(zones: any[]) {
  const el: any = new SmartIrrigationViewHistory();
  el.hass = { language: "en" };
  el._config = { units: "metric" };
  el._zones = zones;
  el._isLoading = false; // the loaded state; the loading gate has its own test
  return el;
}

describe("view-history", () => {
  it("defaults the selected zone to the first zone and renders its history", () => {
    const el = makeView([
      { id: 1, name: "Front", run_log: [], water_used_total: 0 },
      { id: 2, name: "Back", run_log: [], water_used_total: 0 },
    ]);
    expect(el._effectiveZone().id).toBe(1);
    const { text } = flatten(el.render());
    expect(text).toContain("<ip-zone-history");
    expect(text).toContain("<select");
  });

  it("renders the chosen zone after the selector changes", () => {
    const el = makeView([
      { id: 1, name: "Front", run_log: [], water_used_total: 0 },
      { id: 2, name: "Back", run_log: [], water_used_total: 0 },
    ]);
    el._selectedZoneId = 2;
    expect(el._effectiveZone().id).toBe(2);
  });

  it("falls back to the first zone when the selected zone no longer exists", () => {
    const el = makeView([
      { id: 1, name: "Front", run_log: [], water_used_total: 0 },
      { id: 2, name: "Back", run_log: [], water_used_total: 0 },
    ]);
    el._selectedZoneId = 999; // a zone that was deleted
    expect(el._effectiveZone().id).toBe(1);
  });

  it("opens the zone a deep link names", () => {
    const el = makeView([
      { id: 1, name: "Front", run_log: [], water_used_total: 0 },
      { id: 2, name: "Back", run_log: [], water_used_total: 0 },
    ]);
    el.path = { page: "history", params: { zone: "2" } };
    expect(el._effectiveZone().id).toBe(2);
  });

  it("honours a deep link to zone 0", () => {
    // Zone ids start at 0 in this integration, so the id must be tested for
    // null-ness, not for truthiness.
    const el = makeView([
      { id: 0, name: "Front", run_log: [], water_used_total: 0 },
      { id: 1, name: "Back", run_log: [], water_used_total: 0 },
    ]);
    el._selectedZoneId = 1;
    expect(el._effectiveZone().id).toBe(1);
    el._selectedZoneId = 0;
    expect(el._effectiveZone().id).toBe(0);
  });

  it("ignores a deep link to a zone that does not exist", () => {
    const el = makeView([
      { id: 1, name: "Front", run_log: [], water_used_total: 0 },
    ]);
    el.path = { page: "history", params: { zone: "999" } };
    expect(el._effectiveZone().id).toBe(1);
  });

  it("lets an explicit selection win over the deep link", () => {
    // Otherwise the picker would snap back to the linked zone on every render.
    const el = makeView([
      { id: 1, name: "Front", run_log: [], water_used_total: 0 },
      { id: 2, name: "Back", run_log: [], water_used_total: 0 },
    ]);
    el.path = { page: "history", params: { zone: "2" } };
    el._selectedZoneId = 1;
    expect(el._effectiveZone().id).toBe(1);
  });

  it("binds the option's selected PROPERTY, not the attribute", () => {
    // `?selected` sets defaultSelected, which stops tracking once the control
    // is dirty — so a selection made in code (the deep link above) would not
    // move the picker. Pinned here for the same reason ip-schedule-dialog pins
    // it (f446bd62), because the attribute form is still the convention in
    // most of this panel and gets copied back in.
    const el = makeView([
      { id: 1, name: "Front", run_log: [], water_used_total: 0 },
      { id: 2, name: "Back", run_log: [], water_used_total: 0 },
    ]);
    const { text } = flatten(el.render());
    expect(text).not.toContain("?selected=");
    expect(text).toContain(".selected=");
  });

  it("waits for the first fetch before claiming there are no zones", () => {
    // _zones starts empty, so without a loading gate the very first paint
    // asserts "No zones configured yet." at a moment when nothing is known —
    // and a failed fetch would leave that claim standing. Every other
    // self-fetching view in the panel gates its empty state the same way.
    const el: any = new SmartIrrigationViewHistory();
    el.hass = { language: "en" };
    const { text } = flatten(el.render());
    expect(text).toContain("Loading...");
    expect(text).not.toContain("No zones configured yet.");
  });

  it("shows the no-zones note when there are no zones", () => {
    const el = makeView([]);
    const { text } = flatten(el.render());
    expect(text).toContain("No zones configured yet.");
    expect(text).not.toContain("<ip-zone-history");
  });
});
