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

// FM-8: the flow_counter_type select row is shown ONLY when the selected
// flow_sensor's unit indicates a totalizer (cumulative counter). A rate sensor
// (L/min) or no sensor hides it. _flowSensorIsTotalizer is the sole gate that
// determines whether the row renders (the template is `${gate ? html`...` : ""}`
// inline in render()), so exercising it here fully covers the visibility rule.
function make(states: Record<string, any>) {
  const el: any = new View();
  el.hass = { language: "en", states };
  return el;
}

const ENTITY = "sensor.zone_flow";

describe("view-zone-settings flow_counter_type visibility gate", () => {
  it("shows for a volume totalizer unit (e.g. L)", () => {
    const el = make({ [ENTITY]: { attributes: { unit_of_measurement: "L" } } });
    expect(el._flowSensorIsTotalizer({ flow_sensor: ENTITY })).toBe(true);
  });

  it("shows for a cubic-metre totalizer unit (m³)", () => {
    const el = make({
      [ENTITY]: { attributes: { unit_of_measurement: "m³" } },
    });
    expect(el._flowSensorIsTotalizer({ flow_sensor: ENTITY })).toBe(true);
  });

  it("shows when state_class is total_increasing regardless of unit", () => {
    const el = make({
      [ENTITY]: {
        attributes: {
          unit_of_measurement: "L/min",
          state_class: "total_increasing",
        },
      },
    });
    expect(el._flowSensorIsTotalizer({ flow_sensor: ENTITY })).toBe(true);
  });

  it("hides for an instantaneous rate unit (L/min)", () => {
    const el = make({
      [ENTITY]: { attributes: { unit_of_measurement: "L/min" } },
    });
    expect(el._flowSensorIsTotalizer({ flow_sensor: ENTITY })).toBe(false);
  });

  it("hides for a known flow-rate unit without a slash (gpm)", () => {
    const el = make({
      [ENTITY]: { attributes: { unit_of_measurement: "gpm" } },
    });
    expect(el._flowSensorIsTotalizer({ flow_sensor: ENTITY })).toBe(false);
  });

  it("hides when no flow_sensor is set", () => {
    const el = make({});
    expect(el._flowSensorIsTotalizer({ flow_sensor: null })).toBe(false);
    expect(el._flowSensorIsTotalizer({})).toBe(false);
  });

  it("hides when the flow_sensor entity is not in hass.states", () => {
    const el = make({});
    expect(el._flowSensorIsTotalizer({ flow_sensor: ENTITY })).toBe(false);
  });

  it("hides when the sensor reports no unit and no total_increasing", () => {
    const el = make({ [ENTITY]: { attributes: {} } });
    expect(el._flowSensorIsTotalizer({ flow_sensor: ENTITY })).toBe(false);
  });
});
