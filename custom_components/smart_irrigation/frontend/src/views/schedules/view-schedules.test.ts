import { describe, it, expect, beforeAll } from "vitest";

// Same DOM-free shim as the other view tests: enough for the LitElement
// subclass to be defined and instantiated without a real customElement
// registry or shadow DOM. render() is called directly and the returned lit
// TemplateResult tree introspected.
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
let View: ViewModule["SmartIrrigationViewSchedules"];
type DialogModule = typeof import("../../components/si-schedule-dialog");
let emptySchedule: DialogModule["emptySchedule"];

beforeAll(async () => {
  ({ SmartIrrigationViewSchedules: View } = await import("./view-schedules"));
  ({ emptySchedule } = await import("../../components/si-schedule-dialog"));
});

/**
 * Flatten a lit TemplateResult tree into concatenated static HTML plus the
 * dynamic values and handlers, mirroring the helper in the other component
 * tests. The bound property values matter here as much as the markup: the
 * whole point is that the view still hands the dialog its inputs.
 */
function flatten(node: any): { text: string; values: any[] } {
  const out = { text: "", values: [] as any[] };
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
    out.values.push(n);
    if (typeof n === "function") return;
    out.text += String(n);
  };
  walk(node);
  return out;
}

function makeView(open: boolean) {
  const el: any = new View();
  el.hass = { language: "en" };
  el._isLoading = false;
  el._schedules = [];
  el._zones = [{ id: 1, name: "Front lawn" }];
  el._showDialog = open;
  el._editingSchedule = { ...emptySchedule(), name: "Back yard" };
  el._editingId = null;
  return el;
}

describe("view-schedules dialog host", () => {
  // The dialog markup lives in si-schedule-dialog now, so nothing in this
  // view's own output would change if it stopped rendering the element at
  // all. These assertions are what keeps the extracted component reachable
  // from the panel rather than only from its own unit test.
  it("renders si-schedule-dialog while the dialog is open", () => {
    const { text } = flatten(makeView(true).render());
    expect(text).toContain("<si-schedule-dialog");
  });

  it("renders no dialog element while the dialog is closed", () => {
    const { text } = flatten(makeView(false).render());
    expect(text).not.toContain("<si-schedule-dialog");
  });

  it("passes the schedule under edit, the zones and hass to the dialog", () => {
    const el = makeView(true);
    const { values } = flatten(el.render());
    expect(values).toContain(el._editingSchedule);
    expect(values).toContain(el.hass);
    // The walker cannot tell a bound array from a template's child list, so
    // it flattens both; the zone object's identity is what survives, and the
    // dialog binding is the only place a zone reaches this render while the
    // schedule list is empty.
    expect(values).toContain(el._zones[0]);
  });

  it("titles the dialog for adding when no schedule id is being edited", () => {
    const el = makeView(true);
    el._editingId = null;
    const addTitle = el._dialogTitle();
    el._editingId = "abc";
    expect(el._dialogTitle()).not.toBe(addTitle);
    // Both titles reach the rendered element, so a regression in either
    // branch is visible from the view's own output.
    expect(flatten(el.render()).values).toContain(el._dialogTitle());
  });

  it("binds the dialog's save, cancel and change events to the view's own handlers", () => {
    const el = makeView(true);
    const { values } = flatten(el.render());
    // Identity, not shape: a handler that merely looks similar would let the
    // wiring rot silently. These are the three events si-schedule-dialog
    // emits, and each has to land on the method that already implemented it
    // before the extraction.
    for (const method of ["_save", "_closeDialog", "_onScheduleChanged"]) {
      expect(
        values.some((v) => typeof v === "function" && v === el[method]),
        `${method} is not bound to the dialog`,
      ).toBe(true);
    }
  });

  it("stores the dialog's patched schedule back onto the view", () => {
    const el = makeView(true);
    const patched = { ...el._editingSchedule, name: "renamed" };
    el._onScheduleChanged({ detail: { value: patched } } as any);
    expect(el._editingSchedule).toBe(patched);
  });
});
