import { LitElement, html, TemplateResult } from "lit";
import { property, state } from "lit/decorators.js";
import { HomeAssistant } from "./types";
import { SmartIrrigationViewZones } from "./views/zones/view-zones";
import { ensureTranslations, isTranslationLoaded } from "../localize/localize";

/**
 * Heavy implementation of the Smart Irrigation zones card. This bundle is
 * lazy-loaded by the tiny `smart-irrigation-card.ts` stub the first time a card
 * actually renders, so the ~180 KB of view code is NOT loaded into the HA app
 * shell on every page (only the stub is, via add_extra_js_url).
 *
 * It registers `<smart-irrigation-zones-card-impl>`; the public card type
 * (`smart-irrigation-zones-card`) is owned by the stub, which instantiates this
 * element and forwards hass/config to it. See the stub for the user-facing
 * config contract.
 */
interface ZonesCardConfig {
  type: string;
  actions?: "irrigate" | "none" | "full";
}

// Pull the shared view in so it is registered in this bundle (its own define is
// guarded, so loading alongside the admin panel bundle is safe).
void SmartIrrigationViewZones;

export class SmartIrrigationZonesCardImpl extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;
  @state() private _config?: ZonesCardConfig;

  public setConfig(config: ZonesCardConfig): void {
    this._config = config;
  }

  public getCardSize(): number {
    return 6;
  }

  protected render(): TemplateResult {
    if (!this.hass || !this._config) return html``;
    // Only English is bundled; fetch the active language on demand and hold
    // rendering until it is in (sub-second) to avoid an English flash.
    if (!isTranslationLoaded(this.hass.language)) {
      ensureTranslations(this.hass.language).then(() => this.requestUpdate());
      return html``;
    }
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

if (!customElements.get("smart-irrigation-zones-card-impl")) {
  customElements.define(
    "smart-irrigation-zones-card-impl",
    SmartIrrigationZonesCardImpl,
  );
}
