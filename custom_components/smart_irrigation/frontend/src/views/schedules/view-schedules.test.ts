import { describe, it, expect, vi, beforeAll } from "vitest";

// Same DOM-free shim as si-schedule-dialog.test.ts: just enough for the
// LitElement subclass to be defined and instantiated without a real
// customElement registry or shadow DOM.
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

type ViewModule = typeof import("./view-schedules");
let SmartIrrigationViewSchedules: ViewModule["SmartIrrigationViewSchedules"];

beforeAll(async () => {
  ({ SmartIrrigationViewSchedules } = await import("./view-schedules"));
});

function makeView(callWS: (msg: any) => Promise<any>) {
  const el: any = new SmartIrrigationViewSchedules();
  el.hass = { language: "en", callWS };
  return el;
}

describe("smart-irrigation-view-schedules nominal demand preview", () => {
  it("fetches a preview for the default all-zones selection when Add is opened", async () => {
    const calls: any[] = [];
    const el = makeView(async (msg: any) => {
      calls.push(msg);
      return { nominal_demand_seconds: 4200 };
    });

    (el as any)._openAdd();
    await Promise.resolve();
    await Promise.resolve();

    expect(calls).toEqual([
      { type: "smart_irrigation/schedule_nominal_demand", zones: "all" },
    ]);
    expect((el as any)._editingSchedule.nominal_demand_seconds).toBe(4200);
  });

  it("refetches when the zone selection changes", async () => {
    const calls: any[] = [];
    const el = makeView(async (msg: any) => {
      calls.push(msg);
      return { nominal_demand_seconds: msg.zones === "all" ? 100 : 200 };
    });

    (el as any)._openAdd();
    await Promise.resolve();
    await Promise.resolve();

    (el as any)._onScheduleChanged({
      detail: { value: { ...(el as any)._editingSchedule, zones: ["1", "2"] } },
    });
    await Promise.resolve();
    await Promise.resolve();

    expect(calls).toHaveLength(2);
    expect(calls[1]).toEqual({
      type: "smart_irrigation/schedule_nominal_demand",
      zones: ["1", "2"],
    });
    expect((el as any)._editingSchedule.nominal_demand_seconds).toBe(200);
  });

  it("does not refetch when an unrelated field (e.g. name) changes", async () => {
    const calls: any[] = [];
    const el = makeView(async (msg: any) => {
      calls.push(msg);
      return { nominal_demand_seconds: 4200 };
    });

    (el as any)._openAdd();
    await Promise.resolve();
    await Promise.resolve();
    expect(calls).toHaveLength(1);

    (el as any)._onScheduleChanged({
      detail: {
        value: { ...(el as any)._editingSchedule, name: "Front lawn" },
      },
    });
    await Promise.resolve();
    await Promise.resolve();

    expect(calls).toHaveLength(1);
    expect((el as any)._editingSchedule.name).toBe("Front lawn");
  });
});
