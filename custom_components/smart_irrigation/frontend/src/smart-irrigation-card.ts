import { LitElement, html, TemplateResult } from "lit";
import { property, state } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";
import { SmartIrrigationViewZones } from "./views/zones/view-zones";
import { VERSION } from "./const";

/**
 * Lovelace card that mirrors the everyday Zones dashboard for non-admin users.
 *
 * The full Smart Irrigation panel is admin-only (panel_custom require_admin),
 * but the underlying websocket/HTTP endpoints are available to any authenticated
 * user. This card reuses the panel's zone view with the admin-only deep links
 * hidden (settings gear, schedule setup, first-run wizard) and, by default, only
 * the manual "Irrigate" actions exposed — so household members can see status
 * and water on demand without touching configuration.
 *
 * Config:
 *   type: custom:smart-irrigation-zones-card
 *   actions: irrigate | none | full   # optional, default "irrigate"
 */
interface ZonesCardConfig {
  type: string;
  actions?: "irrigate" | "none" | "full";
}

// Pull the shared view in so it is registered in this bundle too (its own
// define is guarded, so loading alongside the admin panel bundle is safe).
void SmartIrrigationViewZones;

export class SmartIrrigationZonesCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;
  @state() private _config?: ZonesCardConfig;

  public setConfig(config: ZonesCardConfig): void {
    this._config = config;
  }

  public getCardSize(): number {
    return 6;
  }

  static getStubConfig(): Record<string, unknown> {
    return {};
  }

  protected render(): TemplateResult {
    if (!this.hass || !this._config) return html``;
    const mode = this._config.actions ?? "irrigate";
    return html`
      <smart-irrigation-view-zones
        .hass=${this.hass}
        .hideSettingsLinks=${true}
        .actionsMode=${mode}
      ></smart-irrigation-view-zones>
    `;
  }
}

// Guarded define so a duplicate load (e.g. add_extra_js_url + a manual resource)
// does not throw.
if (!customElements.get("smart-irrigation-zones-card")) {
  customElements.define(
    "smart-irrigation-zones-card",
    SmartIrrigationZonesCard,
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
  // the release verification (each bundle must embed the version) holds.
  console.info(
    `%c smart-irrigation-zones-card %c ${VERSION} `,
    "color: white; background: #3949ab; font-weight: 700;",
    "color: #3949ab; background: white; font-weight: 700;",
  );
}
