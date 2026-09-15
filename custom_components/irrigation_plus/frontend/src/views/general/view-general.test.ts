import { describe, it, expect, beforeAll, vi } from "vitest";

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

describe("view-general: a failed zones fetch does not take the page down", () => {
  it("still renders the settings, with the batch note simply absent", async () => {
    // The zones are read only to decide whether the sequencing card mentions
    // queue-driven zones. Joined into the same rejection as the config, a
    // failure here would leave `config` unassigned and render the whole view as
    // a load error -- a settings page lost to an advisory line.
    const websockets = await import("../../data/websockets");
    const config = { zone_sequencing: "rotating" };

    vi.spyOn(websockets, "fetchConfig").mockResolvedValue(config as any);
    vi.spyOn(websockets, "fetchWeatherConfig").mockResolvedValue({
      use_weather_service: false,
    } as any);
    vi.spyOn(websockets, "fetchCoordinates").mockResolvedValue({} as any);
    vi.spyOn(websockets, "fetchZones").mockRejectedValue(
      new Error("zones unavailable"),
    );

    const el: any = new View();
    el.hass = { language: "en" };
    el.requestUpdate = () => {};
    el._applyCoordinates = () => {};
    // showErrorToast dispatches on the element, so a stub without this turns
    // the load-error path into a TypeError and hides which failure occurred.
    const toasts: string[] = [];
    el.dispatchEvent = (event: any) => {
      toasts.push(event?.detail?.message ?? String(event?.type));
      return true;
    };

    await el._fetchData();

    // The page loaded: the config landed and no load-error toast was raised.
    expect(el.config).toBe(config);
    expect(el._initialLoadDone).toBe(true);
    expect(toasts).toEqual([]);
    // And the only thing lost is the note.
    expect(el._zones).toEqual([]);
    const text = flatten(el._renderZoneSequencingCard());
    expect(text).toContain("Zone Sequencing");
    expect(text).not.toContain("Batch zones are not included");

    vi.restoreAllMocks();
  });
});

describe("view-general: the look-ahead help follows the rain mode", () => {
  // The same setting serves two modes that count from different days: the skip
  // guard from the run's own date, forecast weighting from the day after the
  // calculation. One help text was wrong for one of them.
  function weatherView(config: any) {
    const el: any = new View();
    el.hass = { language: "en" };
    el.config = { precipitation_forecast_days: 1, ...config };
    el.data = {};
    el.requestUpdate = () => {};
    return el;
  }

  it("counts from the run's own date when the run is skipped on rain", () => {
    const text = flatten(
      weatherView({
        skip_irrigation_on_precipitation: true,
      })._renderWeatherSkipCard(),
    );
    expect(text).toContain("starting with the day the run takes place");
    expect(text).not.toContain("starting with the day after the calculation");
  });

  it("counts from the day after the calculation when rain only shortens the run", () => {
    const text = flatten(
      weatherView({
        skip_irrigation_on_precipitation: false,
        forecast_weighting_enabled: true,
      })._renderWeatherSkipCard(),
    );
    expect(text).toContain("starting with the day after the calculation");
    expect(text).not.toContain("starting with the day the run takes place");
  });
});
