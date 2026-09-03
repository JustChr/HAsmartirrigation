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
    expect(text).toContain("<si-zone-history");
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

  it("shows the no-zones note when there are no zones", () => {
    const el = makeView([]);
    const { text } = flatten(el.render());
    expect(text).toContain("No zones configured yet.");
    expect(text).not.toContain("<si-zone-history");
  });
});
