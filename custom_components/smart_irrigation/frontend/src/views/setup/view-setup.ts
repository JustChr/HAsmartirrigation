import { LitElement, html, CSSResultGroup, css } from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../../types";

import "../general/view-general.ts";
import "../zones/view-zone-settings.ts";
import "../modules/view-modules.ts";
import "../mappings/view-mappings.ts";
import "../schedules/view-schedules.ts";

import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import { ISSUES_URL } from "../../const";
import { navigate } from "../../helpers";
import { exportPath, Path } from "../../common/navigation";

const DOCS_URL = "https://justchr.github.io/HAsmartirrigation/";

enum ESetupTab {
  General = "general",
  Zones = "zones",
  Modules = "modules",
  Mappings = "mappings",
  Schedules = "schedules",
  Help = "help",
}

const SETUP_TAB_LABELS: Record<ESetupTab, string> = {
  [ESetupTab.General]: "panels.general.title",
  [ESetupTab.Zones]: "panels.zones.title",
  [ESetupTab.Modules]: "panels.modules.title",
  [ESetupTab.Mappings]: "panels.mappings.title",
  [ESetupTab.Schedules]: "panels.schedules.title",
  [ESetupTab.Help]: "panels.help.title",
};

@customElement("smart-irrigation-view-setup")
export class SmartIrrigationViewSetup extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public narrow!: boolean;

  @property({ attribute: false }) public path?: Path;

  // Active sub-tab is derived from the URL subpage so it is deep-linkable and
  // survives in-session back/forward. Falls back to General for unknown values.
  private get _activeTab(): ESetupTab {
    const sub = this.path?.subpage;
    return (Object.values(ESetupTab) as string[]).includes(sub ?? "")
      ? (sub as ESetupTab)
      : ESetupTab.General;
  }

  private _selectTab(tab: ESetupTab) {
    navigate(this, exportPath("setup", tab));
  }

  private _openWizard() {
    // The panel shell owns the single wizard instance.
    this.dispatchEvent(
      new CustomEvent("open-wizard", { bubbles: true, composed: true }),
    );
  }

  render() {
    if (!this.hass) return html``;

    const activeTab = this._activeTab;
    return html`
      <div class="setup-container">
        <nav class="setup-nav">
          ${Object.values(ESetupTab).map(
            (tab) => html`
              <button
                class="setup-nav-btn ${activeTab === tab ? "active" : ""}"
                @click="${() => this._selectTab(tab)}"
              >
                ${localize(SETUP_TAB_LABELS[tab], this.hass.language)}
              </button>
            `,
          )}
          <button
            class="setup-nav-btn wizard-btn"
            @click="${this._openWizard}"
            title="${localize("wizard.title", this.hass.language)}"
          >
            <ha-icon icon="mdi:creation"></ha-icon>
            ${localize("wizard.open_button", this.hass.language)}
          </button>
        </nav>
        <div class="setup-content">${this._renderContent(activeTab)}</div>
      </div>
    `;
  }

  private _renderContent(activeTab: ESetupTab) {
    if (!this.hass) return html``;
    switch (activeTab) {
      case ESetupTab.General:
        return html`<smart-irrigation-view-general
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-general>`;
      case ESetupTab.Zones:
        return html`<smart-irrigation-view-zone-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-zone-settings>`;
      case ESetupTab.Modules:
        return html`<smart-irrigation-view-modules
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-modules>`;
      case ESetupTab.Mappings:
        return html`<smart-irrigation-view-mappings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-mappings>`;
      case ESetupTab.Schedules:
        return html`<smart-irrigation-view-schedules
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-schedules>`;
      case ESetupTab.Help:
        return this._renderHelp();
    }
  }

  private _renderHelp() {
    if (!this.hass) return html``;
    return html`
      <ha-card
        header="${localize(
          "panels.help.cards.how-to-get-help.title",
          this.hass.language,
        )}"
      >
        <div class="card-content">
          ${localize(
            "panels.help.cards.how-to-get-help.first-read-the",
            this.hass.language,
          )}
          <a href="${DOCS_URL}"
            >${localize(
              "panels.help.cards.how-to-get-help.wiki",
              this.hass.language,
            )}</a
          >.
          ${localize(
            "panels.help.cards.how-to-get-help.if-you-still-need-help",
            this.hass.language,
          )}
          <a
            href="https://community.home-assistant.io/t/smart-irrigation-save-water-by-precisely-watering-your-lawn-garden"
            >${localize(
              "panels.help.cards.how-to-get-help.community-forum",
              this.hass.language,
            )}</a
          >
          ${localize(
            "panels.help.cards.how-to-get-help.or-open-a",
            this.hass.language,
          )}
          <a href="${ISSUES_URL}"
            >${localize(
              "panels.help.cards.how-to-get-help.github-issue",
              this.hass.language,
            )}</a
          >
          (${localize(
            "panels.help.cards.how-to-get-help.english-only",
            this.hass.language,
          )}).
        </div>
      </ha-card>
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      :host {
        display: block;
        width: 100%;
      }

      .setup-container {
        display: flex;
        flex-direction: column;
        width: 100%;
      }

      .setup-nav {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        padding: 8px 16px 0;
        border-bottom: 1px solid var(--divider-color);
        background: var(--card-background-color);
        position: sticky;
        top: 0;
        z-index: 1;
      }

      .setup-nav-btn {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        color: var(--secondary-text-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.8125rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        padding: 8px 12px;
        text-transform: uppercase;
        transition:
          color 0.15s,
          border-color 0.15s;
        white-space: nowrap;
        margin-bottom: -1px;
      }

      .setup-nav-btn:hover {
        color: var(--primary-text-color);
      }

      .setup-nav-btn.active {
        border-bottom-color: var(--primary-color);
        color: var(--primary-color);
      }

      .setup-nav-btn.wizard-btn {
        margin-left: auto;
        color: var(--primary-color);
        border-bottom-color: transparent;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        --mdc-icon-size: 18px;
      }

      .setup-nav-btn.wizard-btn:hover {
        color: var(--primary-color);
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
      }

      .setup-content {
        padding-top: 4px;
      }

      .setup-content > * {
        display: block;
        width: 100%;
      }
    `;
  }
}
