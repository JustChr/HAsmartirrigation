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

// #139: the latency margin only shapes runs the watcher can confirm, so the row
// is shown ONLY for a service zone with a confirm_entity. These tests cover the
// two methods the row is built on: the gate _showLatencyMargin and the input
// clamp _clampLatencyMargin. They do not render the template, so they do not
// prove that render() wires both into the service block; that is checked by
// hand in the panel.
function make() {
  const el: any = new View();
  el.hass = { language: "en", states: {} };
  return el;
}

describe("view-zone-settings latency_margin visibility gate", () => {
  it("shows when a confirm_entity is set", () => {
    const el = make();
    expect(
      el._showLatencyMargin({ confirm_entity: "binary_sensor.valve_flowing" }),
    ).toBe(true);
  });

  it("hides when confirm_entity is null", () => {
    const el = make();
    expect(el._showLatencyMargin({ confirm_entity: null })).toBe(false);
  });

  it("hides when confirm_entity is an empty string", () => {
    const el = make();
    expect(el._showLatencyMargin({ confirm_entity: "" })).toBe(false);
  });

  it("hides when confirm_entity is missing", () => {
    const el = make();
    expect(el._showLatencyMargin({})).toBe(false);
    expect(el._showLatencyMargin({ confirm_entity: undefined })).toBe(false);
  });
});

describe("view-zone-settings latency_margin input clamp", () => {
  it("keeps a whole number inside the range", () => {
    const el = make();
    expect(el._clampLatencyMargin(4)).toBe(4);
    expect(el._clampLatencyMargin(0)).toBe(0);
    expect(el._clampLatencyMargin(30)).toBe(30);
  });

  it("rounds to whole seconds", () => {
    const el = make();
    expect(el._clampLatencyMargin(2.6)).toBe(3);
    expect(el._clampLatencyMargin(2.4)).toBe(2);
  });

  it("clamps below 0 and above 30", () => {
    const el = make();
    expect(el._clampLatencyMargin(-3)).toBe(0);
    expect(el._clampLatencyMargin(45)).toBe(30);
  });

  it("ignores an empty or invalid input (NaN)", () => {
    const el = make();
    expect(el._clampLatencyMargin(NaN)).toBeNull();
  });
});
