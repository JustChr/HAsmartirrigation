import { LitElement, html, CSSResultGroup, css } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";

import "../general/view-general.ts";
import "../modules/view-modules.ts";
import "../mappings/view-mappings.ts";
import "../schedules/view-schedules.ts";
import "../wizard/si-setup-wizard.ts";

import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import { ISSUES_URL } from "../../const";

const DOCS_URL = "https://justchr.github.io/HAsmartirrigation/";

enum ESetupTab {
  General = "general",
  Modules = "modules",
  Mappings = "mappings",
  Schedules = "schedules",
  Help = "help",
}

const SETUP_TAB_LABELS: Record<ESetupTab, string> = {
  [ESetupTab.General]: "panels.general.title",
  [ESetupTab.Modules]: "panels.modules.title",
  [ESetupTab.Mappings]: "panels.mappings.title",
  [ESetupTab.Schedules]: "panels.schedules.title",
  [ESetupTab.Help]: "panels.help.title",
};

@customElement("smart-irrigation-view-setup")
export class SmartIrrigationViewSetup extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public narrow!: boolean;

  @property()
  private _activeTab: ESetupTab = ESetupTab.General;

  @state() private _wizardOpen = false;

  private _openWizard() {
    this._wizardOpen = true;
  }

  private _onWizardClose() {
    this._wizardOpen = false;
  }

  private _onWizardNavigate(e: CustomEvent) {
    const { page } = e.detail as { page: string };
    this.dispatchEvent(
      new CustomEvent("wizard-navigate", {
        detail: { page },
        bubbles: true,
        composed: true,
      }),
    );
    this._wizardOpen = false;
  }

  render() {
    if (!this.hass) return html``;

    return html`
      ${this._wizardOpen
        ? html`
            <si-setup-wizard
              .hass="${this.hass}"
              @wizard-close="${this._onWizardClose}"
              @wizard-navigate="${this._onWizardNavigate}"
            ></si-setup-wizard>
          `
        : ""}
      <div class="setup-container">
        <nav class="setup-nav">
          ${Object.values(ESetupTab).map(
            (tab) => html`
              <button
                class="setup-nav-btn ${this._activeTab === tab ? "active" : ""}"
                @click="${() => {
                  this._activeTab = tab;
                }}"
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
            ✦ ${localize("wizard.open_button", this.hass.language)}
          </button>
        </nav>
        <div class="setup-content">${this._renderContent()}</div>
      </div>
    `;
  }

  private _renderContent() {
    if (!this.hass) return html``;
    switch (this._activeTab) {
      case ESetupTab.General:
        return html`<smart-irrigation-view-general
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-general>`;
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
