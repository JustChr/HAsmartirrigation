import { describe, it, expect, beforeAll } from "vitest";
import { localize } from "../../localize/localize";

// DOM-free shim, same as si-schedule-dialog.test.ts: define + instantiate the
// LitElement subclass without a real registry, call render() and introspect
// the returned template tree.
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

type Mod = typeof import("./si-zone-history");
let SiZoneHistory: Mod["SiZoneHistory"];

beforeAll(async () => {
  ({ SiZoneHistory } = await import("./si-zone-history"));
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

function makeEl(zone: any, config: any = { units: "metric" }) {
  const el: any = new SiZoneHistory();
  el.hass = { language: "en" };
  el.zone = zone;
  el.config = config;
  return el;
}

describe("si-zone-history", () => {
  it("renders the cumulative usage and a runs table for a zone with runs", () => {
    const el = makeEl({
      id: 1,
      name: "Front",
      water_used_total: 42,
      run_log: [{ ts: 1000, result: "completed", volume_l: 12, detail: "" }],
    });
    const { text, values } = flatten(el.render());
    expect(text).toContain('class="history-usage"');
    expect(text).toContain('class="history-table"');
    // The result token is interpolated, so flatten() appends it to `values`
    // rather than inline in `text` (same convention as si-schedule-dialog.test.ts).
    expect(text).toContain('class="history-chip history-');
    expect(values).toContain("completed");
    expect(text).not.toContain('class="weather-note"');
  });

  it("renders the empty note and no table when the run log is empty", () => {
    const el = makeEl({
      id: 1,
      name: "Front",
      water_used_total: 0,
      run_log: [],
    });
    const { text } = flatten(el.render());
    expect(text).toContain('class="weather-note"');
    expect(text).not.toContain('class="history-table"');
  });

  it("renders one row per log entry", () => {
    const el = makeEl({
      id: 1,
      name: "Front",
      water_used_total: 5,
      run_log: [
        { ts: 1000, result: "completed", volume_l: 3, detail: "" },
        { ts: 2000, result: "skipped", volume_l: 0, detail: "rain" },
      ],
    });
    const chips = (flatten(el.render()).text.match(/history-chip/g) || [])
      .length;
    expect(chips).toBe(2);
  });
});

describe("history tab strings exist", () => {
  it("has the tab title, selector label and no-zones note in English", () => {
    expect(localize("panels.history.title", "en")).toBe("History");
    expect(localize("panels.history.select_zone", "en")).toBe("Select zone");
    expect(localize("panels.history.no_zones", "en")).toBe(
      "No zones configured yet.",
    );
  });
});
