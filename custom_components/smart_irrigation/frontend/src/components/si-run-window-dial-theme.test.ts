import { describe, it, expect, beforeAll } from "vitest";

// Same DOM-free shim used by si-run-window-dial.test.ts.
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

type DialModule = typeof import("./si-run-window-dial");
let SiRunWindowDial: DialModule["SiRunWindowDial"];
let cssText: string;

beforeAll(async () => {
  ({ SiRunWindowDial } = await import("./si-run-window-dial"));
  cssText = (SiRunWindowDial.styles as any).cssText as string;
});

/**
 * "Colors resolve correctly in both light and dark themes, verified by
 * reading computed values rather than by eye" is the acceptance criterion
 * here. vitest runs in a bare-node environment with no real CSSOM
 * — there is no `getComputedStyle` that can actually resolve `color-mix()`
 * against a `--card-background-color` custom property the way a browser
 * would, so a literal "render once per theme, read the resolved pixel"
 * check isn't available in this repo's test setup (see si-schedule-dialog's
 * own tests, which take the same DOM-free approach for the same reason).
 *
 * What IS mechanically checkable, and what actually caused the real bug the
 * ticket describes ("one alpha over two backgrounds"): a color defined as a
 * fixed alpha (`rgba(...)`, or a hex/hsl with an alpha channel) resolves to
 * a DIFFERENT actual color depending on what's behind it, so it is only
 * correct against one specific background. `color-mix(in srgb, X%, var(
 * --card-background-color))` mixes toward the CSS custom property directly,
 * so it recomputes correctly whichever theme sets that property. This test
 * asserts, from the actual stylesheet source (not a hand-copied string),
 * that every dial ring/track/tick color depends on
 * `var(--card-background-color)` through `color-mix()`, and that none of
 * them is a hex-with-alpha or rgba/hsla value — which is the property that
 * would silently break across themes.
 */
describe("si-run-window-dial: ring colors resolve per-theme, not via a fixed alpha", () => {
  it("mixes every themed ring/track/tick color against var(--card-background-color) or var(--...) directly", () => {
    // The three colors that vary with the card background per the ticket:
    // the window band, the idle track, and the hour ticks. Each must be
    // `color-mix(in srgb, <opaque color/percent>, var(--card-background-color)
    // | transparent)`, never a value with a baked-in alpha.
    const declarations = [
      { selector: ".d-win", prop: "stroke" },
      { selector: ".d-track", prop: "stroke" },
      { selector: ".d-tick", prop: "stroke" },
    ];
    for (const { selector, prop } of declarations) {
      const re = new RegExp(
        `\\.viz-dial ${selector.replace(".", "\\.")}\\s*\\{[^}]*${prop}:\\s*([^;]+);`,
      );
      const match = cssText.match(re);
      expect(match, `${selector} should declare ${prop}`).not.toBeNull();
      const value = match![1].trim();
      expect(
        value.startsWith("color-mix(") || value.startsWith("var(--dial-"),
        `${selector}'s ${prop} ("${value}") should resolve through color-mix(), not a fixed value`,
      ).toBe(true);
    }
    // The two custom properties consumed above must themselves mix against
    // the card background, not hardcode one theme's color.
    expect(cssText).toMatch(
      /--dial-win:\s*color-mix\(\s*in srgb,[\s\S]*?var\(--card-background-color\)\s*\)/,
    );
    expect(cssText).toMatch(
      /--dial-track:\s*color-mix\(\s*in srgb,[\s\S]*?var\(--card-background-color\)\s*\)/,
    );
  });

  it("never expresses a themed ring color as rgba()/hsla()/8-digit-hex, which would carry one fixed alpha across both themes", () => {
    // Scan only the ring/track/tick/dotted declarations (not e.g. the plain
    // #f6b21b sun-glyph fill, which is intentionally theme-invariant per the
    // prototype and isn't a "ring color mixed against the background").
    const themedBlockNames = [
      "d-win",
      "d-track",
      "d-tick",
      "dial-win",
      "dial-track",
    ];
    for (const name of themedBlockNames) {
      const re = new RegExp(`--?${name}[^;]*;`, "g");
      const matches = cssText.match(re) ?? [];
      for (const m of matches) {
        expect(m).not.toMatch(/rgba\(/);
        expect(m).not.toMatch(/hsla\(/);
        expect(m).not.toMatch(/#[0-9a-fA-F]{8}\b/); // 8-digit hex carries alpha
      }
    }
  });
});
