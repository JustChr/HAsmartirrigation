import { describe, it, expect, beforeAll } from "vitest";

// Same DOM-free shim as si-distributor-form.test.ts: just enough for the
// LitElement subclass to be defined and instantiated without a real
// customElement registry or shadow DOM. We call render() directly and
// introspect the returned lit TemplateResult tree.
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

type DialogModule = typeof import("./si-schedule-dialog");
let SiScheduleDialog: DialogModule["SiScheduleDialog"];
let emptySchedule: DialogModule["emptySchedule"];

beforeAll(async () => {
  ({ SiScheduleDialog, emptySchedule } = await import("./si-schedule-dialog"));
});

type Handler = (e: any) => unknown;

/**
 * Flatten a lit TemplateResult tree into concatenated static HTML plus the
 * list of dynamic values/handlers, mirroring si-distributor-form.test.ts's
 * helper — the dialog markup nests templates the same way.
 */
function flatten(node: any): {
  text: string;
  values: any[];
  handlers: Handler[];
} {
  const out = { text: "", values: [] as any[], handlers: [] as Handler[] };
  const walk = (n: any) => {
    if (n == null || typeof n === "boolean") return;
    if (Array.isArray(n)) {
      n.forEach(walk);
      return;
    }
    if (n && Array.isArray(n.strings) && "values" in n) {
      out.text += n.strings.join("");
      walk(n.values);
      return;
    }
    if (typeof n === "function") {
      out.handlers.push(n);
      out.values.push(n);
      return;
    }
    out.values.push(n);
    out.text += String(n);
  };
  walk(node);
  return out;
}

function makeDialog(overrides: Partial<Record<string, any>> = {}) {
  const el: any = new SiScheduleDialog();
  el.hass = { language: "en" };
  el.schedule = overrides.schedule ?? emptySchedule();
  el.zones = overrides.zones ?? [];
  el.heading = overrides.heading ?? "Add schedule";
  const emitted: any[] = [];
  el.dispatchEvent = (ev: any) => {
    emitted.push(ev);
    return true;
  };
  return { el, emitted };
}

describe("si-schedule-dialog", () => {
  it("renders the ha-dialog with the given heading and the schedule's name", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), name: "Front lawn" },
      heading: "Edit schedule",
    });
    const { text } = flatten(el.render());
    expect(text).toContain("<ha-dialog");
    expect(text).toContain("Edit schedule");
    expect(text).toContain("Front lawn");
  });

  it("emits schedule-changed with the patched schedule when the name field changes", () => {
    const { el, emitted } = makeDialog({
      schedule: { ...emptySchedule(), name: "old" },
    });
    const { handlers } = flatten(el.render());
    let sawPatch = false;
    for (const h of handlers) {
      emitted.length = 0;
      try {
        h({ target: { value: "new name" } });
      } catch {
        continue;
      }
      const evt = emitted.find((e) => e.type === "schedule-changed");
      if (evt && evt.detail.value.name === "new name") {
        sawPatch = true;
        // The emitted value carries the rest of the schedule forward too.
        expect(evt.detail.value.recurrence).toBe("daily");
      }
    }
    expect(sawPatch).toBe(true);
  });

  it("emits save with the current schedule when the primaryAction button is clicked", () => {
    const schedule = { ...emptySchedule(), name: "Back yard" };
    const { el, emitted } = makeDialog({ schedule });
    const { handlers } = flatten(el.render());
    // The primaryAction button's @click is bound to the same function
    // reference as the component's private _save — find it by identity in
    // the rendered tree and invoke it as the browser would (via the click),
    // rather than calling the private method by name.
    const clickSave = handlers.find((h) => h === (el as any)._save);
    expect(clickSave).toBeDefined();
    clickSave!({});
    expect(emitted).toHaveLength(1);
    expect(emitted[0].type).toBe("save");
    expect(emitted[0].detail.value).toEqual(schedule);
  });

  it("emits cancel from both the secondaryAction button and the host ha-dialog's own closed event", () => {
    // Both the explicit Cancel button and the ha-dialog's native "closed"
    // event (Escape / backdrop click) must drive the same cancel path, never
    // save. The rendered tree binds both @click (secondaryAction button) and
    // @closed (ha-dialog) to the identical _cancel function reference, so
    // finding that reference twice in the handler list confirms both wiring
    // points, and invoking it exercises the actual bound handler.
    const { el, emitted } = makeDialog();
    const { text, handlers } = flatten(el.render());
    expect(text).toContain("<ha-dialog");
    const cancelHandlers = handlers.filter((h) => h === (el as any)._cancel);
    expect(cancelHandlers).toHaveLength(2);
    cancelHandlers[0]({});
    expect(emitted).toHaveLength(1);
    expect(emitted[0].type).toBe("cancel");
  });

  it("does not render when schedule is not set", () => {
    const el: any = new SiScheduleDialog();
    el.hass = { language: "en" };
    const { text } = flatten(el.render());
    expect(text).toBe("");
  });
});

describe("si-schedule-dialog: Start/Finish rows (GitLab #29)", () => {
  it("offers all five modes on both the Start and Finish rows", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), start_mode: "none", finish_mode: "none" },
    });
    const { text } = flatten(el.render());
    for (const label of [
      "No limit",
      "At sunrise",
      "At sunset",
      "At solar azimuth",
      "At a time",
    ]) {
      // Once per row (Start, Finish) — two <option> labels each.
      const count = text.split(label).length - 1;
      expect(count, `"${label}" should appear on both rows`).toBe(2);
    }
  });

  it("renders a degrees stepper (not minutes) when a row's mode is solar_azimuth", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        start_mode: "solar_azimuth",
        start_azimuth: 120,
        finish_mode: "none",
      },
    });
    const { text } = flatten(el.render());
    expect(text).toContain("°");
    // The azimuth input carries a literal min="0"/max="359" attribute pair
    // (bearing bounds, not the minutes suffix), so a bare toContain("min")
    // would false-positive on that attribute name — exclude it with a
    // negative lookahead on "=" and require the localized minutes suffix
    // never renders as text content instead.
    expect(text).not.toMatch(/\bmin\b(?!=)/);
  });

  it("renders a signed minutes stepper for sunrise/sunset", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        start_mode: "sunrise",
        start_offset: -15,
        finish_mode: "none",
      },
    });
    const { text } = flatten(el.render());
    expect(text).toContain("offset by");
    expect(text).toContain("min");
  });

  it("does not render the pinned-end row when only one end is bounded", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), start_mode: "time", finish_mode: "none" },
    });
    const { text } = flatten(el.render());
    expect(text).not.toContain("Pinned to");
  });

  it("renders the pinned-end row only once both ends are bounded", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        start_mode: "time",
        start_time: "06:00",
        finish_mode: "time",
        finish_time: "20:00",
      },
    });
    const { text } = flatten(el.render());
    expect(text).toContain("Pinned to");
    expect(text).toContain("As early as possible within the window");
    expect(text).toContain("As late as possible within the window");
  });

  it("shows the error help on both rows and disables Save when both ends are unbounded", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), start_mode: "none", finish_mode: "none" },
    });
    const { text } = flatten(el.render());
    const errorCount =
      text.split("Must set either a start or finish condition").length - 1;
    expect(errorCount).toBe(2);
    expect((el as any)._canSave()).toBe(false);
  });

  it("help text matches the table for all five start/finish states", () => {
    const lang = "en";
    const cases: Array<[Partial<Record<string, any>>, string, string]> = [
      [
        { start_mode: "none", finish_mode: "time", finish_time: "20:00" },
        "Set by demand. All zones run to completion.",
        "Exact.",
      ],
      [
        { start_mode: "time", start_time: "06:00", finish_mode: "none" },
        "Exact.",
        "Set by demand. All zones run to completion.",
      ],
      [
        {
          start_mode: "time",
          start_time: "06:00",
          finish_mode: "time",
          finish_time: "20:00",
          anchor: "finish",
        },
        "Set by demand, but never before this.",
        "Exact. Zones that don't fit are deferred.",
      ],
      [
        {
          start_mode: "time",
          start_time: "06:00",
          finish_mode: "time",
          finish_time: "20:00",
          anchor: "start",
        },
        "Exact.",
        "Set by demand, but never later than this. Zones that don't fit are deferred.",
      ],
    ];
    for (const [patch, startHelp, finishHelp] of cases) {
      const { el } = makeDialog({
        schedule: { ...emptySchedule(), ...patch },
      });
      el.hass = { language: lang };
      const { text } = flatten(el.render());
      expect(text, JSON.stringify(patch)).toContain(startHelp);
      expect(text, JSON.stringify(patch)).toContain(finishHelp);
    }
  });

  it("leaves every mode functionally selectable on every recurrence, including weekly/monthly with a sun-relative finish", () => {
    // "No option is disabled" is checked behaviorally here rather than by
    // scanning rendered markup for a `disabled` attribute: the flatten()
    // helper only walks the tagged-template AST, so a literal "disabled"
    // substring from the unrelated Save button's `?disabled` binding is
    // always present in the raw static strings regardless of its runtime
    // value, making a text-search assertion meaningless. Instead, drive the
    // Start mode <select>'s own change handler with every mode and confirm
    // each one actually reaches a schedule-changed patch — which is exactly
    // what "not disabled" means for a <select>.
    for (const recurrence of ["daily", "weekly", "monthly"]) {
      const { el, emitted } = makeDialog({
        schedule: {
          ...emptySchedule(),
          recurrence,
          days_of_week: ["monday"],
          day_of_month: 1,
          start_mode: "none",
          finish_mode: "sunset",
          finish_offset: 0,
        },
      });
      const { handlers } = flatten(el.render());
      for (const mode of [
        "none",
        "time",
        "sunrise",
        "sunset",
        "solar_azimuth",
      ]) {
        let reached = false;
        for (const h of handlers) {
          emitted.length = 0;
          try {
            h({ target: { value: mode } });
          } catch {
            continue;
          }
          const evt = emitted.find((e) => e.type === "schedule-changed");
          if (
            evt &&
            (evt.detail.value.start_mode === mode ||
              evt.detail.value.finish_mode === mode)
          ) {
            reached = true;
          }
        }
        expect(
          reached,
          `${recurrence}: mode "${mode}" should be reachable`,
        ).toBe(true);
      }
    }
  });

  it("hides the Start, Finish and pinned-end rows for an interval recurrence", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        recurrence: "interval",
        interval_hours: 6,
        start_mode: "time",
        start_time: "06:00",
        finish_mode: "time",
        finish_time: "20:00",
        anchor: "finish",
      },
    });
    const { text } = flatten(el.render());
    expect(text).not.toContain("Pinned to");
    expect(text).not.toContain("At sunrise");
    expect(text).not.toContain("At solar azimuth");
    // Interval always allows saving — it has no window to be unbounded.
    expect((el as any)._canSave()).toBe(true);
  });
});

describe("si-schedule-dialog: unreachable solar-azimuth bearings (GitLab #34)", () => {
  /** On the equator the backend's azimuth curve never crosses due east, so
   * 90 degrees is unresolvable there — the same case the dial draws open. */
  const atEquator = (schedule: Record<string, any>) => {
    const { el } = makeDialog({ schedule });
    el.hass = {
      language: "en",
      config: { latitude: 0, longitude: 0, time_zone: "UTC" },
    };
    return el;
  };

  it("warns that the schedule will not run when the governing end is unreachable", () => {
    const el = atEquator({
      ...emptySchedule(),
      start_mode: "solar_azimuth",
      start_azimuth: 90,
      finish_mode: "none",
    });
    const { text } = flatten(el.render());
    expect(text).toContain("so this schedule will not run");
    expect(text).toContain("is-warning");
  });

  it("warns that the limit is ignored when the paired end is unreachable", () => {
    const el = atEquator({
      ...emptySchedule(),
      start_mode: "solar_azimuth",
      start_azimuth: 90,
      finish_mode: "time",
      finish_time: "20:00",
      anchor: "finish",
    });
    const { text } = flatten(el.render());
    expect(text).toContain("so this limit is ignored");
  });

  it("still allows Save — an unreachable bearing is a warning, not an error", () => {
    const el = atEquator({
      ...emptySchedule(),
      start_mode: "solar_azimuth",
      start_azimuth: 90,
      finish_mode: "none",
    });
    expect((el as any)._canSave()).toBe(true);
    expect(flatten(el.render()).text).not.toContain("is-error");
  });

  it("says nothing for a bearing that does resolve", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        start_mode: "solar_azimuth",
        start_azimuth: 270,
        finish_mode: "none",
      },
    });
    el.hass = {
      language: "en",
      config: {
        latitude: 33.45,
        longitude: -112.07,
        time_zone: "America/Phoenix",
      },
    };
    const { text } = flatten(el.render());
    expect(text).not.toContain("The sun never reaches");
    expect(text).not.toContain("is-warning");
  });

  it("says nothing when the location is unknown, rather than guessing", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        start_mode: "solar_azimuth",
        start_azimuth: 90,
        finish_mode: "none",
      },
    });
    el.hass = { language: "en" }; // mid-startup: no config yet
    const { text } = flatten(el.render());
    expect(text).not.toContain("The sun never reaches");
  });
});
