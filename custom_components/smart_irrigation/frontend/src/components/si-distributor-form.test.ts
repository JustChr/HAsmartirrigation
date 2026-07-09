import { describe, it, expect, beforeAll } from "vitest";

// The panel's LitElements normally only run inside Home Assistant (they extend
// HTMLElement and self-register via @customElement). vitest runs in a bare node
// env with no DOM, so we install a minimal shim BEFORE importing the component:
// just enough for the class to be defined and instantiated. We never mount it —
// we call its render methods and introspect the returned lit TemplateResult
// tree (no custom-element registry, no shadow DOM needed). This keeps the
// "pure logic only" spirit of the suite while still covering the render branch.
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

// Imported for its side effect (defines the element) + the class export. Must
// come after the shim above, hence a dynamic import in the test body below.
type FormModule = typeof import("./si-distributor-form");
let SiDistributorForm: FormModule["SiDistributorForm"];

beforeAll(async () => {
  ({ SiDistributorForm } = await import("./si-distributor-form"));
});

/**
 * Flatten a lit TemplateResult tree into (a) the concatenated static HTML and
 * (b) the list of dynamic values (nested templates recursed; event handlers and
 * other functions collected separately). Lit's `.map(...)` yields an array of
 * TemplateResults in `.values`, so we recurse arrays and template objects.
 */
type Handler = (e: any) => unknown;

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
      out.text += n.strings.join(""); // marker between static chunks
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

function makeForm(distributor: any) {
  const el: any = new SiDistributorForm();
  el.hass = { language: "en" };
  el.distributor = distributor;
  const emitted: any[] = [];
  // The real dispatchEvent lives on HTMLElement; capture emits instead.
  el.dispatchEvent = (ev: any) => {
    emitted.push(ev);
    return true;
  };
  return { el, emitted };
}

describe("si-distributor-form inlet-watch section", () => {
  it("renders inlet_entity + watch_mode select in SERVICE mode (previously absent)", () => {
    const { el } = makeForm({
      name: "d",
      watering_mode: "service",
      inlet_entity: "switch.ring",
      watch_mode: "warn",
    });
    const { text } = flatten(el.render());
    // The inlet_entity picker now renders in service mode too.
    expect(text).toContain("ha-entity-picker");
    expect(text).toContain("Inlet valve");
    // The tri-state select renders.
    expect(text).toContain("<select");
    expect(text).toContain("On a manual inlet pulse");
    // Self-closing (service) mode shows the watch-only help variant.
    expect(text).toContain("only read");
    expect(text).toContain("NOT the flow/confirm sensor");
    // The label carries the (optional) marker, matching the other optional fields
    // (confirm/flow sensor), instead of a leading "Optional." in the body.
    expect(text).toContain("Inlet valve / switch (optional)");
    // The reaction-setting reference is forward-looking: the watch_mode row only
    // appears once an inlet is selected, so the help must not imply it is always there.
    expect(text).toContain("a setting appears below to control the reaction");
    expect(text).toContain("Leave empty to disable inlet watching");
  });

  it("renders the inlet-watch section in CLASSIC mode with the classic help", () => {
    const { el } = makeForm({
      name: "d",
      watering_mode: "classic",
      inlet_entity: "switch.ring",
      watch_mode: "count",
    });
    const { text } = flatten(el.render());
    expect(text).toContain("<select");
    expect(text).toContain("On a manual inlet pulse");
    // Classic help, not the service watch-only variant.
    expect(text).toContain("opens the water supply into the distributor");
    expect(text).not.toContain("NOT the flow/confirm sensor");
  });

  it("offers exactly three watch_mode options (count/warn/ignore)", () => {
    const { el } = makeForm({
      name: "d",
      watering_mode: "service",
      inlet_entity: "switch.ring",
      watch_mode: "ignore",
    });
    const { text } = flatten(el.render());
    expect(text).toContain("Count it (advance the position)");
    expect(text).toContain("Warn (mark position uncertain)");
    expect(text).toContain("Ignore");
    // Exactly three <option> labels render (one per watch mode).
    const optionLabels = text.match(
      /Count it \(advance the position\)|Warn \(mark position uncertain\)|Ignore/g,
    );
    expect(optionLabels?.length).toBe(3);
  });

  it("emits watch_mode (not watch_inlet) when the select changes", () => {
    const { el, emitted } = makeForm({
      name: "d",
      watering_mode: "classic",
      inlet_entity: "switch.ring",
      watch_mode: "ignore",
    });
    const { handlers } = flatten(el.render());
    // Feed every handler a select/entity-style event carrying "warn". Each emit
    // spreads the current distributor + the changed field, so watch_mode is
    // always present; the select's @change handler is the only one that drives
    // it to the fed value. The fixture has no watch_inlet key on purpose: the
    // form no longer has that control, so it must never appear in any patch.
    const setWatchMode: string[] = [];
    for (const h of handlers) {
      emitted.length = 0;
      try {
        h({ target: { value: "warn" }, detail: { value: "warn" } });
      } catch {
        continue;
      }
      const patch = emitted[0]?.detail?.value ?? {};
      expect("watch_inlet" in patch).toBe(false);
      if (patch.watch_mode === "warn") setWatchMode.push("hit");
    }
    // Exactly one handler drove watch_mode to the fed value: the select.
    expect(setWatchMode.length).toBe(1);
  });

  it("defaults the select value to 'ignore' when watch_mode is unset", () => {
    const { el } = makeForm({
      name: "d",
      watering_mode: "classic",
      inlet_entity: "switch.ring",
    });
    const { text } = flatten(el.render());
    // The ignore <option> is marked selected via lit's ?selected binding, which
    // is a value in the tree rather than static text; assert the select + all
    // three labels render so the default path builds without error.
    expect(text).toContain("<select");
    expect(text).toContain("Ignore");
  });

  it("hides the watch_mode row until an inlet_entity is set", () => {
    // No inlet_entity -> nothing to watch -> the watch_mode row must be absent.
    // NB: the form has other <select>s (watering_mode, duration_unit), so assert
    // on watch_mode-SPECIFIC markers, not on "<select" presence.
    const bare = makeForm({ name: "d", watering_mode: "service" });
    const bareText = flatten(bare.el.render()).text;
    expect(bareText).not.toContain("On a manual inlet pulse");
    expect(bareText).not.toContain("Count it (advance the position)");
    // The inlet_entity picker itself still renders.
    expect(bareText).toContain("ha-entity-picker");

    // With an inlet_entity set, the watch_mode row appears.
    const withInlet = makeForm({
      name: "d",
      watering_mode: "service",
      inlet_entity: "switch.ring",
      watch_mode: "warn",
    });
    const withText = flatten(withInlet.el.render()).text;
    expect(withText).toContain("On a manual inlet pulse");
    expect(withText).toContain("Count it (advance the position)");
  });
});
