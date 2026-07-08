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

type ViewModule = typeof import("./view-setup");
let View: ViewModule["SmartIrrigationViewSetup"];
beforeAll(async () => {
  ({ SmartIrrigationViewSetup: View } = await import("./view-setup"));
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

function make(distributorsEnabled: boolean | undefined) {
  const el: any = new View();
  el.hass = { language: "en" };
  el.config =
    distributorsEnabled === undefined
      ? undefined
      : { distributors_enabled: distributorsEnabled };
  return el;
}

describe("view-setup distributors tab gating", () => {
  it("hides the Distributors nav tab when the flag is off", () => {
    const text = flatten(make(false).render());
    expect(text).not.toContain("Distributors");
  });

  it("shows the Distributors nav tab when the flag is on", () => {
    const text = flatten(make(true).render());
    expect(text).toContain("Distributors");
  });

  it("hides the tab while config is still loading (flag unknown)", () => {
    const text = flatten(make(undefined).render());
    expect(text).not.toContain("Distributors");
  });
});
