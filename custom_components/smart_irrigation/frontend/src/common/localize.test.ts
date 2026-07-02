import { describe, it, expect, vi, afterEach } from "vitest";
import { ensureTranslations } from "../../localize/localize";
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
