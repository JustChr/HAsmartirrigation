import { describe, it, expect, beforeAll } from "vitest";

// The panel's LitElements normally only run inside Home Assistant (they extend
// HTMLElement and self-register via @customElement). vitest runs in a bare node
// env with no DOM, so we install a minimal shim BEFORE importing the component:
// just enough for the class to be defined and instantiated. We never mount it —
// we call its render methods and introspect the returned lit TemplateResult
// tree (no custom-element registry, no shadow DOM needed). Mirrors the harness
// in si-distributor-form.test.ts.
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
  // _scheduleUpdate() (via _callAction) schedules a repaint; the bare node env
  // has no rAF, so shim it to a no-op. We never assert on the scheduled repaint.
  (globalThis as any).requestAnimationFrame = () => 0;
});

// Imported for its side effect (defines the element) + the class export. Must
// come after the shim above, hence a dynamic import in the test body below.
type ViewModule = typeof import("./view-distributor-settings");
let SmartIrrigationViewDistributorSettings: ViewModule["SmartIrrigationViewDistributorSettings"];

beforeAll(async () => {
  ({ SmartIrrigationViewDistributorSettings } =
    await import("./view-distributor-settings"));
});

/**
 * Flatten a lit TemplateResult tree into (a) the concatenated static HTML and
 * (b) the list of dynamic values (nested templates recursed; event handlers and
 * other functions collected separately). Lit's `.map(...)` yields an array of
 * TemplateResults in `.values`, so we recurse arrays and template objects.
 * Copied from si-distributor-form.test.ts.
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
      out.text += n.strings.join(""); // marker between static chunks
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

/**
 * Build a view instance with one distributor, its commissioning section already
 * rendered, and hass.callService captured so we can assert whether a service
 * (the set-outlet action) actually fired.
 */
function makeView(distributor: any) {
  const el: any = new SmartIrrigationViewDistributorSettings();
  const calls: { domain: string; service: string; data: any }[] = [];
  el.hass = {
    language: "en",
    callService: (domain: string, service: string, data: any) => {
      calls.push({ domain, service, data });
      return Promise.resolve();
    },
  };
  el.distributors = [distributor];
  el.isSaving = false;
  el.isLoading = false;
  // requestUpdate/_scheduleUpdate touch the reactive layer; stub to a no-op so
  // pure-logic calls don't blow up without a mounted element.
  el.requestUpdate = () => {};
  return { el, calls };
}

const DIST = () => ({
  id: 7,
  name: "Front distributor",
  position_state: "synced",
  current_outlet: 3,
  commissioning_confirmed: false,
  active_cycle: {},
});

describe("view-distributor-settings set-current-outlet confirm", () => {
  it("clicking 'Set current outlet' does NOT act immediately — it sets _confirmSetOutletId", () => {
    const { el, calls } = makeView(DIST());
    const { handlers } = flatten(el._renderCommissioning(el.distributors[0]));

    // Drive every button handler in the commissioning section. The set-outlet
    // button's @click sets _confirmSetOutletId = id; it must NOT call the
    // set-outlet service directly (the whole point of the safety confirm). We
    // feed an empty event ({}); the @input handler reads e.target and throws
    // harmlessly, which we swallow.
    for (const h of handlers) {
      try {
        h({});
      } catch {
        /* input @input handlers want an event with a target; ignore */
      }
    }

    // The set-outlet service must not have fired from a mere button click.
    expect(calls.some((c) => c.service === "distributor_set_outlet")).toBe(
      false,
    );
    // Exactly one handler armed the confirm state to this distributor's id.
    expect(el._confirmSetOutletId).toBe(7);
  });

  it("renders the confirm popup (with the target outlet) only when _confirmSetOutletId is set", () => {
    const { el } = makeView(DIST());

    // Not armed: no set-outlet confirm dialog in the tree.
    let text = flatten(el.render()).text;
    expect(text).not.toContain("Set current outlet?");

    // Armed: the popup renders with title + body + the target outlet number.
    el._confirmSetOutletId = 7;
    text = flatten(el.render()).text;
    expect(text).toContain("Set current outlet?");
    expect(text).toContain("marks the distributor as synced");
    // Target outlet defaults to current_outlet (3) when no draft is entered.
    expect(text).toContain("Front distributor");
    expect(text).toContain("3");
  });

  it("popup shows the DRAFT outlet number when the user has typed one", () => {
    const { el } = makeView(DIST());
    el._outletDraft = { 7: 5 };
    el._confirmSetOutletId = 7;
    const text = flatten(el.render()).text;
    // The draft (5) wins over current_outlet (3) as the target shown.
    expect(text).toContain("5");
  });

  it("confirming calls the set-outlet action (draft outlet) and clears the state", () => {
    const { el, calls } = makeView(DIST());
    el._outletDraft = { 7: 5 };
    el._confirmSetOutletId = 7;
    el._confirmSetOutlet();

    expect(el._confirmSetOutletId).toBeNull();
    const call = calls.find((c) => c.service === "distributor_set_outlet");
    expect(call).toBeTruthy();
    expect(call!.data.distributor_id).toBe(7);
    expect(call!.data.outlet).toBe(5);
  });

  it("confirming with no draft falls back to current_outlet", () => {
    const { el, calls } = makeView(DIST());
    el._confirmSetOutletId = 7;
    el._confirmSetOutlet();

    const call = calls.find((c) => c.service === "distributor_set_outlet");
    expect(call).toBeTruthy();
    expect(call!.data.outlet).toBe(3);
  });

  it("cancelling clears _confirmSetOutletId without firing the action", () => {
    const { el, calls } = makeView(DIST());
    el._confirmSetOutletId = 7;
    // Find and run the cancel handler in the rendered popup.
    const { handlers } = flatten(el.render());
    // The cancel button and the dialog @closed both clear the state to null;
    // run every handler that clears it, then assert nothing acted.
    for (const h of handlers) {
      try {
        const before = el._confirmSetOutletId;
        h({});
        // A handler that set it back to null (cancel/close) is the one we want;
        // stop once one has cleared the armed state.
        if (el._confirmSetOutletId === null && before !== null) break;
      } catch {
        /* ignore */
      }
    }

    expect(el._confirmSetOutletId).toBeNull();
    expect(calls.some((c) => c.service === "distributor_set_outlet")).toBe(
      false,
    );
  });
});

describe("view-distributor-settings experimental banner", () => {
  it("renders the experimental advisory at the top of the advisories", () => {
    const el: any = new SmartIrrigationViewDistributorSettings();
    el.hass = { language: "en" };
    el.config = {};
    const text = flatten(el._renderAdvisories()).text;
    expect(text).toContain("not fully hardware-tested");
    expect(text).toContain("Watch the first days of use closely");
  });
});
