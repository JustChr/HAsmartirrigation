import { VERSION, FULL_CARD_URL } from "./const";

/**
 * Tiny registration stub for the Smart Irrigation zones card.
 *
 * The full Smart Irrigation panel is admin-only (panel_custom require_admin),
 * but the underlying websocket/HTTP endpoints are available to any
 * authenticated user. This card reuses the panel's zone view with the
 * admin-only deep links hidden and, by default, only the manual "Irrigate"
 * actions exposed — so household members can see status and water on demand
 * without touching configuration.
 *
 * This file is auto-loaded into the HA app shell on EVERY page (via
 * add_extra_js_url), so it is deliberately tiny: it registers the element and
 * advertises the card in the picker, but defers the heavy view bundle
 * (`smart-irrigation-card-impl.js`) until a card is actually rendered.
 *
 * Config:
 *   type: custom:smart-irrigation-zones-card
 *   actions: irrigate | none | full   # optional, default "irrigate"
 */
interface ZonesCardConfig {
  type: string;
  actions?: "irrigate" | "none" | "full";
}

let implPromise: Promise<unknown> | undefined;

/**
 * Lazy-load the heavy implementation bundle. The URL is passed through a
 * function boundary so the bundler emits a real runtime import (a string
 * literal would be statically resolved/bundled, defeating the split).
 *
 * Crucially, a FAILED import is not cached: if the impl bundle can't be fetched
 * (e.g. its static path isn't registered yet during a HACS update / HA restart)
 * we clear the cache so a later attempt retries instead of the card staying
 * permanently broken until a full page reload.
 */
function loadImpl(): Promise<unknown> {
  if (!implPromise) {
    // Cache-bust per attempt: the browser's module map pins a URL that failed to
    // fetch, so a plain retry of the same URL would keep serving the cached
    // failure. A fresh query string forces a real re-fetch on retry. (The impl
    // is served no-cache anyway, so this adds no extra network cost.)
    const url: string = FULL_CARD_URL + "?v=" + Date.now();
    implPromise = import(/* @vite-ignore */ url).catch((e) => {
      implPromise = undefined;
      throw e;
    });
  }
  return implPromise;
}

class SmartIrrigationZonesCardStub extends HTMLElement {
  private _config?: ZonesCardConfig;
  private _hass?: unknown;
  private _mounting = false;
  private _inner?: HTMLElement & {
    hass?: unknown;
    setConfig?: (c: ZonesCardConfig) => void;
  };

  public setConfig(config: ZonesCardConfig): void {
    this._config = config;
    if (this._inner) {
      this._inner.setConfig?.(config);
    } else {
      void this._mount();
    }
  }

  // Lovelace assigns hass frequently; forward it to the inner element once it
  // exists. While it doesn't (impl still loading, or a previous load failed),
  // each hass update retries the mount so the card self-heals.
  set hass(hass: unknown) {
    this._hass = hass;
    if (this._inner) {
      this._inner.hass = hass;
    } else if (this._config) {
      void this._mount();
    }
  }

  public getCardSize(): number {
    return 6;
  }

  // Default to full width in the modern sections (grid) dashboard so the zone
  // list actually uses the space it is given. Users can still resize it.
  public getGridOptions(): Record<string, unknown> {
    return { columns: "full", rows: "auto", min_columns: 6 };
  }

  static getStubConfig(): Record<string, unknown> {
    return {};
  }

  private async _mount(): Promise<void> {
    if (this._mounting || this._inner) return;
    this._mounting = true;
    try {
      await loadImpl();
      if (!this._inner) {
        this._inner = document.createElement(
          "smart-irrigation-zones-card-impl",
        ) as HTMLElement & {
          hass?: unknown;
          setConfig?: (c: ZonesCardConfig) => void;
        };
        this.appendChild(this._inner);
      }
      if (this._hass) this._inner.hass = this._hass;
      if (this._config) this._inner.setConfig?.(this._config);
    } catch (e) {
      // Leave _inner unset so the next hass update (HA pushes them often)
      // retries — never get stuck on a transient load failure.
      console.error(
        "smart-irrigation-zones-card: failed to load card implementation, will retry",
        e,
      );
    } finally {
      this._mounting = false;
    }
  }
}

// Guarded define so a duplicate load (e.g. add_extra_js_url + a manual resource)
// does not throw.
if (!customElements.get("smart-irrigation-zones-card")) {
  customElements.define(
    "smart-irrigation-zones-card",
    SmartIrrigationZonesCardStub,
  );
}

// Advertise the card in the Lovelace "Add card" picker.
interface CustomCardEntry {
  type: string;
  name: string;
  description: string;
  preview?: boolean;
}
const w = window as unknown as { customCards?: CustomCardEntry[] };
w.customCards = w.customCards || [];
if (!w.customCards.some((c) => c.type === "smart-irrigation-zones-card")) {
  w.customCards.push({
    type: "smart-irrigation-zones-card",
    name: "Smart Irrigation Zones",
    description:
      "Everyday zone status and manual irrigation, usable by non-admin users.",
    preview: false,
  });
  // Conventional card banner; also pins the build version into this bundle so
  // the release verification (panel + card stub must embed the version) holds.
  console.info(
    `%c smart-irrigation-zones-card %c ${VERSION} `,
    "color: white; background: #3949ab; font-weight: 700;",
    "color: #3949ab; background: white; font-weight: 700;",
  );
}
