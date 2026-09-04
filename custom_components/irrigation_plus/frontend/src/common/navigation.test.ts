import { describe, it, expect } from "vitest";
import { isOwnPath } from "./navigation";
import { DOMAIN, PLATFORM } from "../const";

describe("isOwnPath", () => {
  it("matches this integration's own panel paths", () => {
    expect(isOwnPath(`/${DOMAIN}`)).toBe(true);
    expect(isOwnPath(`/${DOMAIN}/zones`)).toBe(true);
    expect(isOwnPath(`/${DOMAIN}/setup/zones/zone/3`)).toBe(true);
  });

  it("rejects another integration's panel", () => {
    // The #120 collision: upstream keeps the smart_irrigation domain, and both
    // panels can be visited in one SPA session without a page load.
    expect(isOwnPath("/smart_irrigation/zones")).toBe(false);
    expect(isOwnPath("/lovelace/0")).toBe(false);
    expect(isOwnPath("/config/integrations")).toBe(false);
  });

  it("does not match the ELEMENT spelling of the domain", () => {
    // The bug this replaced: the guard compared the URL path against PLATFORM
    // ("irrigation-plus", hyphens) instead of DOMAIN ("irrigation_plus",
    // underscores), so it never matched and back/forward stopped refreshing
    // the panel. Pin the two spellings apart so they cannot be confused again.
    expect(PLATFORM).not.toBe(DOMAIN);
    expect(isOwnPath(`/${PLATFORM}/zones`)).toBe(false);
  });

  it("is anchored to the first segment, not a substring", () => {
    // A substring test would pass here; ours must not.
    expect(isOwnPath(`/lovelace/${DOMAIN}`)).toBe(false);
    expect(isOwnPath(`/not_${DOMAIN}/zones`)).toBe(false);
  });
});
