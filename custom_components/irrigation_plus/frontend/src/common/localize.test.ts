import { describe, it, expect, vi, afterEach } from "vitest";
import { ensureTranslations, localize } from "../../localize/localize";
import { LANG_BASE_URL, VERSION } from "../const";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ensureTranslations", () => {
  it("cache-busts the runtime language fetch with the build version", async () => {
    // A non-English, not-yet-loaded language triggers the runtime fetch.
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: () => Promise.resolve({}) });
    vi.stubGlobal("fetch", fetchMock);

    await ensureTranslations("de");

    // Without a version query the browser/service worker can keep serving a
    // stale language JSON across updates, so freshly added keys fall back to
    // bundled English (see the panel module cache-bust in PR #30).
    expect(fetchMock).toHaveBeenCalledWith(
      `${LANG_BASE_URL}/de.json?v=${VERSION}`,
    );
  });
});

describe("localize with a key deeper than the catalogue", () => {
  // Issue #87. Callers interpolate runtime values into keys (a fault code, a
  // skip reason, a run-log detail) and such a value can carry full stops of its
  // own. The lookup used to walk off the end of the object and then dereference
  // undefined on the NEXT segment, throwing a TypeError out of localize and
  // taking the surrounding Lit render down with it — which is why a zone simply
  // would not expand, with nothing in the UI to say why.
  it("returns undefined instead of throwing for an over-deep key", () => {
    expect(() =>
      localize("panels.zones.fault.a.b.c.d.e.f", "en"),
    ).not.toThrow();
    expect(localize("panels.zones.fault.a.b.c.d.e.f", "en")).toBeUndefined();
  });

  it("survives a prose detail interpolated into a key", () => {
    // The exact shape that broke it: a calculation explanation, which is what
    // the run log carries in `detail` for a completed run.
    const explanation =
      "Verwendet , als Dezimalzeichen und zeigt gerundete Werte. ETo 3.2 mm.";
    expect(() =>
      localize(`panels.zones.fault.${explanation}`, "de"),
    ).not.toThrow();
  });

  it("still resolves a real key", () => {
    expect(localize("panels.zones.title", "en")).toBeTruthy();
  });

  it("falls back to English for an unknown language rather than throwing", () => {
    expect(localize("panels.zones.title", "zz")).toBeTruthy();
  });
});
