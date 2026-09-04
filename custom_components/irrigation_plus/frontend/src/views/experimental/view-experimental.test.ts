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

type ViewModule = typeof import("./view-experimental");
let View: ViewModule["SmartIrrigationViewExperimental"];
beforeAll(async () => {
  ({ SmartIrrigationViewExperimental: View } =
    await import("./view-experimental"));
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

function make(config: any) {
  const el: any = new View();
  el.hass = { language: "en" };
  el.config = config;
  return el;
}

describe("view-experimental distributors toggle", () => {
  it("renders the distributors toggle card", () => {
    const el = make({
      observed_watering_enabled: false,
      live_estimate_enabled: false,
      distributors_enabled: false,
    });
    const text = flatten(el.render());
    expect(text).toContain("Mechanical water distributors");
    expect(text).toContain("Enable mechanical water distributors");
    // The "watch the first days" advisory is present.
    expect(text).toContain("Watch the first days of use closely");
  });
});
