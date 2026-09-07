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
  // _scheduleUpdate() schedules through rAF, which the node environment lacks.
  (globalThis as any).requestAnimationFrame = () => 0;
});

type ViewModule = typeof import("./view-general");
let View: ViewModule["SmartIrrigationViewGeneral"];

beforeAll(async () => {
  ({ SmartIrrigationViewGeneral: View } = await import("./view-general"));
});

function flatten(node: any): string {
  let out = "";
  const walk = (n: any) => {
    if (n == null || typeof n === "boolean") return;
    if (Array.isArray(n)) return n.forEach(walk);
    if (n && Array.isArray(n.strings) && "values" in n) {
      out += n.strings.join("");
      return walk(n.values);
    }
    out += String(n);
  };
  walk(node);
  return out;
}

function makeView(zones: any[], sequencing = "rotating") {
  const el: any = new View();
  el.hass = { language: "en" };
  el.config = { zone_sequencing: sequencing };
  el.data = {};
  el._zones = zones;
  el.requestUpdate = () => {};
  return el;
}

const CLASSIC = { id: 1, name: "Front", watering_mode: "classic" };
const SERVICE = { id: 2, name: "Beet", watering_mode: "service" };
const BATCH = { id: 3, name: "Queue", watering_mode: "batch" };

describe("view-general: the sequencing card's batch note", () => {
  it("stays silent when no zone is on a queue controller", () => {
    // The setting DOES reach classic, self-closing and OpenSprinkler zones
    // since the run chain was extracted (#98), so a note about them would be
    // wrong. Only a queue controller is exempt.
    const text = flatten(
      makeView([CLASSIC, SERVICE])._renderZoneSequencingCard(),
    );
    expect(text).toContain("Zone Sequencing");
    expect(text).not.toContain("Batch zones are not included");
  });

  it("shows the note as soon as one zone is on a queue controller", () => {
    const text = flatten(
      makeView([CLASSIC, BATCH])._renderZoneSequencingCard(),
    );
    expect(text).toContain("Batch zones are not included");
  });

  it("shows the note under every sequencing mode, not just rotating", () => {
    // Sequential is dropped by a queue too: the controller decides the order.
    const text = flatten(
      makeView([BATCH], "sequential")._renderZoneSequencingCard(),
    );
    expect(text).toContain("Batch zones are not included");
  });

  it("says the setting governs the other modes rather than promising it flatly", () => {
    const text = flatten(makeView([CLASSIC])._renderZoneSequencingCard());
    expect(text).toContain("classic, self-closing and OpenSprinkler zones");
  });
});
