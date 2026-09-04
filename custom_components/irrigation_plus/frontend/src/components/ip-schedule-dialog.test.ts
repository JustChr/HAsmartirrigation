import { describe, it, expect, beforeAll } from "vitest";

// Same DOM-free shim as ip-distributor-form.test.ts: just enough for the
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

type DialogModule = typeof import("./ip-schedule-dialog");
let SiScheduleDialog: DialogModule["SiScheduleDialog"];
let emptySchedule: DialogModule["emptySchedule"];

beforeAll(async () => {
  ({ SiScheduleDialog, emptySchedule } = await import("./ip-schedule-dialog"));
});

type Handler = (e: any) => unknown;

/**
 * Flatten a lit TemplateResult tree into concatenated static HTML plus the
 * list of dynamic values/handlers, mirroring ip-distributor-form.test.ts's
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

describe("ip-schedule-dialog", () => {
  it("renders the ha-dialog with the given heading and the schedule's name", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), name: "Front lawn" },
      heading: "Edit schedule",
    });
    const { text } = flatten(el.render());
    expect(text).toContain("<ha-dialog");
    expect(text).toContain("Edit schedule");
    expect(text).toContain("Front lawn");
    // The title goes through ha-dialog's own heading attribute rather than a
    // custom "heading" slot: markup of ours in that slot sits inside the
    // dialog's padding box and runs under both top corners.
    expect(text).toContain("heading=");
    expect(text).not.toContain('slot="heading"');
  });

  it("puts the enabled toggle in the actions row, not the heading", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), enabled: true },
    });
    const { text } = flatten(el.render());
    expect(text).toContain('class="enabled-toggle"');
    expect(text).toContain("<ha-switch");
    // Not in the heading slot -- see the sibling test above for why.
    expect(text).not.toContain('slot="heading"');
  });

  // #117: HA 2026.8 swapped ha-dialog's Material internals for a Web Awesome
  // wa-dialog and dropped the primaryAction/secondaryAction slots for a single
  // `footer`. Content in a slot that does not exist is not rendered at all --
  // no error, no fallback -- so Cancel, Save and the Enabled toggle silently
  // vanished and no schedule could be saved. hacs.json still declares a floor
  // of HA 2025.5.0, so BOTH shapes have to work and the slot is detected.
  describe("the actions row targets the slot the running dialog actually has", () => {
    const actionsOf = (slot: "footer" | "material" | "content") => {
      const { el } = makeDialog({ schedule: emptySchedule() });
      (el as any)._actionSlot = slot;
      return flatten(el.render()).text;
    };

    it("uses the footer slot on a Web Awesome ha-dialog", () => {
      const text = actionsOf("footer");
      expect(text).toContain('slot="footer"');
      expect(text).not.toContain('slot="primaryAction"');
      expect(text).not.toContain('slot="secondaryAction"');
    });

    it("uses the Material action slots when there is no footer slot", () => {
      const text = actionsOf("material");
      expect(text).toContain('slot="primaryAction"');
      expect(text).toContain('slot="secondaryAction"');
      expect(text).not.toContain('slot="footer"');
    });

    // The fallback, and the reason it exists: a dialog we cannot classify must
    // still be saveable. The default slot is projected by every generation, so
    // the row names no slot at all rather than one that may not be there.
    it("falls back to the default slot when neither shape is detected", () => {
      const text = actionsOf("content");
      expect(text).not.toContain('slot="footer"');
      expect(text).not.toContain('slot="primaryAction"');
      expect(text).not.toContain('slot="secondaryAction"');
      expect(text).toContain("dialog-footer-inline");
    });

    it("is what the component starts on, so the buttons are never missing", () => {
      const { el } = makeDialog({ schedule: emptySchedule() });
      expect((el as any)._actionSlot).toBe("content");
    });

    it("renders exactly one Save and one Cancel in every shape", () => {
      for (const slot of ["footer", "material", "content"] as const) {
        const text = actionsOf(slot);
        const saves = text.match(/dialog-btn-primary/g) || [];
        const rows = text.match(/class="dialog-buttons"/g) || [];
        const toggles = text.match(/class="enabled-toggle"/g) || [];
        expect(saves.length, slot).toBe(1);
        expect(rows.length, slot).toBe(1);
        expect(toggles.length, slot).toBe(1);
      }
    });
  });

  // The detection itself, which the first #117 fix shipped with NO test at all
  // -- the tests above set the flag by hand, so they passed while the thing
  // that sets it never worked. `ha-dialog` attaches its shadow root
  // synchronously on connect and renders into it a microtask later, so a
  // detection that reads it during firstUpdated sees an EMPTY root and
  // concludes "no footer slot". These fakes reproduce that ordering.
  describe("detecting the slot", () => {
    /** A stand-in ha-dialog whose shadow root fills in only after its own
     * first render resolves -- the real HA 2026.8 ordering, measured. */
    const fakeDialog = (slotNames: string[], opts: { lit?: boolean } = {}) => {
      const nodes: { name: string }[] = [];
      const shadowRoot = {
        querySelector: (sel: string) => {
          if (sel === "slot") return nodes[0] ?? null;
          const m = /^slot\[name="(.+)"\]$/.exec(sel);
          return nodes.find((n) => m && n.name === m[1]) ?? null;
        },
      };
      const fill = () => slotNames.forEach((name) => nodes.push({ name }));
      const dialog: any = { shadowRoot };
      if (opts.lit !== false) {
        dialog.updateComplete = Promise.resolve().then(fill);
      } else {
        // Not a Lit element: nothing to await, the slots simply turn up on a
        // later task and only the poll can catch them.
        setTimeout(fill, 0);
      }
      return dialog;
    };

    const detect = async (dialog: any) => {
      const { el } = makeDialog({ schedule: emptySchedule() });
      (el as any).renderRoot = { querySelector: () => dialog };
      await (el as any)._detectActionSlot();
      return (el as any)._actionSlot;
    };

    it("finds the footer slot even though the shadow root is empty at first", async () => {
      expect(
        await detect(
          fakeDialog(["header", "headerTitle", "(default)", "footer"]),
        ),
      ).toBe("footer");
    });

    it("finds the Material slots on an older ha-dialog", async () => {
      expect(
        await detect(fakeDialog(["primaryAction", "secondaryAction"])),
      ).toBe("material");
    });

    it("polls on past a dialog that is not a Lit element", async () => {
      expect(await detect(fakeDialog(["footer"], { lit: false }))).toBe(
        "footer",
      );
    });

    it("stays on the always-projected default slot when nothing is found", async () => {
      const dialog = { shadowRoot: { querySelector: () => null } };
      expect(await detect(dialog)).toBe("content");
    });

    it("stays on the default slot when there is no dialog to inspect", async () => {
      const { el } = makeDialog({ schedule: emptySchedule() });
      (el as any).renderRoot = { querySelector: () => null };
      await (el as any)._detectActionSlot();
      expect((el as any)._actionSlot).toBe("content");
    });
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

describe("ip-schedule-dialog: Start/Finish rows", () => {
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
    // The azimuth input has no min/max (a bearing wraps rather than clamps —
    // see the wraparound test below), so this only needs to confirm the
    // localized minutes suffix never renders as text content here.
    expect(text).not.toMatch(/\bmin\b(?!=)/);
  });

  it.each([
    ["past the top", "400", 40],
    ["past the bottom", "-10", 350],
  ])(
    "wraps the solar-azimuth stepper %s instead of clamping",
    (_label, typed, wrapped) => {
      const { el, emitted } = makeDialog({
        schedule: {
          ...emptySchedule(),
          start_mode: "solar_azimuth",
          start_azimuth: 120,
          finish_mode: "none",
        },
      });
      const { handlers } = flatten(el.render());
      let sawWrap = false;
      for (const h of handlers) {
        emitted.length = 0;
        try {
          h({ target: { value: typed } });
        } catch {
          continue;
        }
        const evt = emitted.find((e) => e.type === "schedule-changed");
        if (evt && evt.detail.value.start_azimuth === wrapped) {
          sawWrap = true;
        }
      }
      expect(sawWrap).toBe(true);
    },
  );

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
    expect(text).toContain("offset");
    expect(text).toContain("min");
  });

  it("does not render the pinned-end row when only one end is bounded", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), start_mode: "time", finish_mode: "none" },
    });
    const { text } = flatten(el.render());
    expect(text).not.toContain("Water as");
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
    expect(text).toContain("Water as");
    expect(text).toContain("as possible in the window");
    expect(text).toContain("late");
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
        name: "Named",
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
    expect(text).not.toContain("Water as");
    expect(text).not.toContain("At sunrise");
    expect(text).not.toContain("At solar azimuth");
    // Interval always allows saving — it has no window to be unbounded.
    expect((el as any)._canSave()).toBe(true);
  });
});

/**
 * Regression cover for the recurrence-specific fields, which had none.
 *
 * Clearing a `<input type="number">` yields "", and `parseInt("")` is NaN.
 * NaN survives into the schedule object, and `JSON.stringify` writes it to
 * the wire as `null` — which the backend stored, because a schedule has no
 * voluptuous schema and `_validate_schedule_data` returns early for an
 * interval recurrence without ever looking at `interval_hours`.
 *
 * The consequences were not symmetric. A null `day_of_month` matched no
 * calendar day, so the schedule silently stopped arming. A null
 * `interval_hours` reached `datetime.timedelta(hours=None)` inside
 * `_setup_schedule_trackers`, which `async_setup_entry` awaits unguarded —
 * so it stopped the whole integration loading and took every other
 * schedule's tracker with it. See tests/test_schedule_numeric_nulls.py for
 * the backend half; these keep the NaN from being emitted in the first
 * place.
 */
describe("ip-schedule-dialog: numeric recurrence fields never emit NaN", () => {
  /** Fire every handler with `value`, returning the patches that came back. */
  function patchesFor(el: any, emitted: any[], value: string) {
    const { handlers } = flatten(el.render());
    const patches: any[] = [];
    for (const h of handlers) {
      emitted.length = 0;
      try {
        h({ target: { value } });
      } catch {
        continue;
      }
      for (const e of emitted) {
        if (e.type === "schedule-changed") patches.push(e.detail.value);
      }
    }
    return patches;
  }

  it("emits nothing for day_of_month when the field is cleared", () => {
    const { el, emitted } = makeDialog({
      schedule: { ...emptySchedule(), recurrence: "monthly", day_of_month: 14 },
    });
    for (const p of patchesFor(el, emitted, "")) {
      expect(Number.isNaN(p.day_of_month)).toBe(false);
    }
  });

  it("emits nothing for interval_hours when the field is cleared", () => {
    const { el, emitted } = makeDialog({
      schedule: {
        ...emptySchedule(),
        recurrence: "interval",
        interval_hours: 6,
      },
    });
    for (const p of patchesFor(el, emitted, "")) {
      expect(Number.isNaN(p.interval_hours)).toBe(false);
    }
  });

  it("survives the parent's write-back, so a save is never a null", () => {
    // The property that actually matters end to end, and the reason this is
    // asserted through a write-back rather than off `el.schedule` directly:
    // the dialog never mutates its own property. view-schedules.ts's
    // `_onScheduleChanged` stores each emitted patch back onto it, and it is
    // THAT object `_save` hands to the websocket. Without the write-back the
    // assertion holds whether or not NaN was emitted, and proves nothing.
    const { el, emitted } = makeDialog({
      schedule: {
        ...emptySchedule(),
        recurrence: "interval",
        interval_hours: 6,
      },
    });
    const { handlers } = flatten(el.render());
    for (const h of handlers) {
      emitted.length = 0;
      try {
        h({ target: { value: "" } });
      } catch {
        continue;
      }
      for (const e of emitted) {
        // Exactly what the parent does with the event.
        if (e.type === "schedule-changed") el.schedule = e.detail.value;
      }
    }
    const wire = JSON.parse(JSON.stringify(el.schedule));
    expect(wire.interval_hours).toBe(6);
  });

  it("still emits a real edit", () => {
    // The guard must reject NaN without swallowing ordinary typing.
    const { el, emitted } = makeDialog({
      schedule: {
        ...emptySchedule(),
        recurrence: "interval",
        interval_hours: 6,
      },
    });
    const patches = patchesFor(el, emitted, "12");
    expect(patches.some((p) => p.interval_hours === 12)).toBe(true);
  });

  it("still emits a real day-of-month edit", () => {
    const { el, emitted } = makeDialog({
      schedule: { ...emptySchedule(), recurrence: "monthly", day_of_month: 14 },
    });
    const patches = patchesFor(el, emitted, "3");
    expect(patches.some((p) => p.day_of_month === 3)).toBe(true);
  });
});

describe("ip-schedule-dialog: Save is blocked on a schedule that can never fire", () => {
  it("blocks Save on a weekly schedule with no weekday ticked", () => {
    // The state a schedule is in the moment its recurrence is switched to
    // weekly, since nothing populates days_of_week. Backend-side this
    // matches no calendar day, so the schedule saved and never fired.
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), recurrence: "weekly" },
    });
    expect((el as any)._canSave()).toBe(false);
  });

  it("blocks Save when the weekday list is explicitly emptied", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), recurrence: "weekly", days_of_week: [] },
    });
    expect((el as any)._canSave()).toBe(false);
  });

  it("allows Save once a weekday is ticked", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        name: "Named",
        recurrence: "weekly",
        days_of_week: ["tuesday"],
      },
    });
    expect((el as any)._canSave()).toBe(true);
  });

  it("shows the reason in the summary rather than only greying the button", () => {
    // A disabled Save with no explanation is its own trap.
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), recurrence: "weekly" },
    });
    const { text } = flatten(el.render());
    expect(text).toContain("never runs");
  });

  it("still allows Save for the other recurrences with no day set", () => {
    // Only weekly is unsatisfiable this way; blocking the others would stop
    // ordinary schedules saving.
    for (const recurrence of ["daily", "monthly", "interval"]) {
      const { el } = makeDialog({
        schedule: { ...emptySchedule(), name: "Named", recurrence },
      });
      expect((el as any)._canSave()).toBe(true);
    }
  });
});

describe("ip-schedule-dialog: Save is blocked on an empty name or zone list", () => {
  const named = (extra: Record<string, unknown> = {}) => ({
    ...emptySchedule(),
    name: "Named",
    ...extra,
  });

  it("blocks Save on a schedule with no name", () => {
    // `<input required>` is inert outside a form, and the backend only
    // checks the key is PRESENT, not non-empty -- so a nameless schedule
    // saved and showed as a blank row in the list.
    const { el } = makeDialog({ schedule: { ...emptySchedule(), name: "" } });
    expect((el as any)._canSave()).toBe(false);
  });

  it("treats whitespace as no name", () => {
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), name: "   " },
    });
    expect((el as any)._canSave()).toBe(false);
  });

  it("says why, rather than only greying the button", () => {
    const { el } = makeDialog({ schedule: { ...emptySchedule(), name: "" } });
    const { text } = flatten(el.render());
    expect(text).toContain("Give the schedule a name");
  });

  it("stops saying so once a name is typed", () => {
    const { el } = makeDialog({ schedule: named() });
    const { text } = flatten(el.render());
    expect(text).not.toContain("Give the schedule a name");
    expect((el as any)._canSave()).toBe(true);
  });

  it("blocks Save when specific zones are chosen but none are ticked", () => {
    // Stores an empty LIST, which normalize_zone_selection returns as []
    // rather than the None that means "all" -- so the run targeted nothing
    // and watered nothing, silently.
    const { el } = makeDialog({ schedule: named({ zones: [] }) });
    expect((el as any)._canSave()).toBe(false);
    const { text } = flatten(el.render());
    expect(text).toContain("never waters anything");
  });

  it("allows Save with one zone ticked, and with 'all'", () => {
    for (const zones of [["1"], "all"]) {
      const { el } = makeDialog({ schedule: named({ zones }) });
      expect((el as any)._canSave()).toBe(true);
    }
  });

  it("blocks an empty zone list on an interval recurrence too", () => {
    // Interval is exempt from the WINDOW check, not from having zones.
    const { el } = makeDialog({
      schedule: named({ recurrence: "interval", interval_hours: 6, zones: [] }),
    });
    expect((el as any)._canSave()).toBe(false);
  });
});

describe("ip-schedule-dialog: form controls bind properties, not attributes", () => {
  it("uses .checked / .selected rather than ?checked / ?selected", () => {
    // `?checked` sets the ATTRIBUTE, which maps to defaultChecked and stops
    // tracking once the control is dirty, so a programmatic state change
    // could leave the control showing the old value. No concrete failure was
    // reproduced here -- the DOM is recreated in every transition that would
    // expose it -- so this is hardening, pinned so it is not undone by
    // copying the pattern back in from elsewhere in the codebase, where it
    // is still the prevailing convention.
    const { el } = makeDialog({
      schedule: { ...emptySchedule(), name: "Named", zones: ["1"] },
      zones: [{ id: 1, name: "Front" }],
    });
    const { text } = flatten(el.render());
    expect(text).not.toContain("?checked=");
    expect(text).not.toContain("?selected=");
    expect(text).toContain(".checked=");
    expect(text).toContain(".selected=");
  });
});

describe("ip-schedule-dialog: unreachable solar-azimuth bearings", () => {
  /** On the equator the backend's azimuth curve never crosses due east, so
   * 90 degrees is unresolvable there - the same case the dial draws open. */
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
      name: "Named",
      start_mode: "solar_azimuth",
      start_azimuth: 90,
      finish_mode: "none",
    });
    const { text, values } = flatten(el.render());
    expect(text).toContain("so this schedule will not run");
    expect(values).toContain("warn");
  });

  it("warns that the limit is ignored when the paired end is unreachable", () => {
    const el = atEquator({
      ...emptySchedule(),
      name: "Named",
      start_mode: "solar_azimuth",
      start_azimuth: 90,
      finish_mode: "time",
      finish_time: "20:00",
      anchor: "finish",
    });
    const { text } = flatten(el.render());
    expect(text).toContain("so this limit is ignored");
  });

  it("still allows Save - an unreachable bearing is a warning, not an error", () => {
    const el = atEquator({
      ...emptySchedule(),
      name: "Named",
      start_mode: "solar_azimuth",
      start_azimuth: 90,
      finish_mode: "none",
    });
    expect((el as any)._canSave()).toBe(true);
  });

  it("says nothing for a bearing that does resolve", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        name: "Named",
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
    const { text, values } = flatten(el.render());
    expect(text).not.toContain("The sun never reaches");
    expect(values).not.toContain("warn");
  });

  it("says nothing when the location is unknown, rather than guessing", () => {
    const { el } = makeDialog({
      schedule: {
        ...emptySchedule(),
        name: "Named",
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
