import { defineConfig } from "vitest/config";

// Unit tests cover the pure, framework-free logic modules (date/number
// formatting, unit conversion, URL routing). Component rendering isn't tested
// here — the panel's LitElements depend on Home Assistant's frontend element
// registry, which only exists inside HA. Keep test files to pure modules.
export default defineConfig({
  test: {
    include: ["src/**/*.test.ts"],
    environment: "node",
  },
});
