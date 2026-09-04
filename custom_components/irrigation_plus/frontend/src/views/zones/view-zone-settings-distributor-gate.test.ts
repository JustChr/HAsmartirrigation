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

type ViewModule = typeof import("./view-zone-settings");
let View: ViewModule["SmartIrrigationViewZoneSettings"];
beforeAll(async () => {
  ({ SmartIrrigationViewZoneSettings: View } =
    await import("./view-zone-settings"));
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

function make(distributorsEnabled: boolean) {
  const el: any = new View();
  el.hass = { language: "en" };
  el.config = { distributors_enabled: distributorsEnabled };
  el.distributors = [];
  return el;
}

const ZONE = { id: 1, name: "Lawn", distributor_id: null };

describe("view-zone-settings distributor selector gating", () => {
  it("hides the distributor selector when the feature is off", () => {
    const el = make(false);
    const text = flatten(el._renderDistributorSelector(ZONE, 0));
    expect(text).not.toContain("Water distributor");
  });

  it("shows the distributor selector when the feature is on", () => {
    const el = make(true);
    const text = flatten(el._renderDistributorSelector(ZONE, 0));
    expect(text).toContain("Water distributor");
  });
});
