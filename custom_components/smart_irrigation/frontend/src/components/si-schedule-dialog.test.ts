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
