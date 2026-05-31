import { LitElement, html, CSSResultGroup, css } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";
import { loadHaForm } from "./load-ha-elements";
import { navigate } from "./helpers";

import "./views/zones/view-zones.ts";
import "./views/setup/view-setup.ts";
import "./views/wizard/si-setup-wizard.ts";

import { commonStyle } from "./styles";
import { VERSION, PLATFORM, ISSUES_URL } from "./const";
const DOCS_URL = "https://justchr.github.io/HAsmartirrigation/";
import { localize } from "../localize/localize";
import { exportPath, getPath, Path } from "./common/navigation";

enum EMenuItems {
  Zones = "zones",
  Setup = "setup",
}

@customElement("smart-irrigation")
export class SmartIrrigationPanel extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean, reflect: true }) public narrow!: boolean;

  @state() private _wizardOpen = false;

  private _updateScheduled = false;
  private _lastNavigationTime = 0;
  private _navigationThrottleDelay = 100; // Prevent too rapid navigation updates

  private _scheduleUpdate() {
    if (this._updateScheduled) return;
    this._updateScheduled = true;
    requestAnimationFrame(() => {
      this._updateScheduled = false;
      this.requestUpdate();
    });
  }

  async firstUpdated() {
    // Always land on Zones when the panel first mounts
    navigate(this, exportPath(EMenuItems.Zones));

    window.addEventListener("location-changed", () => {
      if (!window.location.pathname.includes(PLATFORM)) return;

      // Throttle navigation updates to prevent browser throttling
      const now = performance.now();
      if (now - this._lastNavigationTime < this._navigationThrottleDelay) {
        return; // Skip this update if too soon
      }
      this._lastNavigationTime = now;

      this._scheduleUpdate();
    });

    // Load HA form elements in background without blocking initial render
    loadHaForm()
      .then(() => {
        // Trigger re-render once HA elements are loaded for better UX
        this._scheduleUpdate();
      })
      .catch((error) => {
        console.error("Failed to load HA form elements:", error);
        // Still trigger update to show whatever we can
        this._scheduleUpdate();
      });
  }

  render() {
    const path = getPath();

    // Check what tab components are available
    const hasTabGroup = !!customElements.get("ha-tab-group");
    const hasTabGroupTab = !!customElements.get("ha-tab-group-tab");

    return html`
      <div class="header">
        <div class="toolbar">
          <ha-menu-button
            .hass=${this.hass}
            .narrow=${this.narrow}
          ></ha-menu-button>
          <div class="main-title">${localize("title", this.hass.language)}</div>
          <div class="version">${VERSION}</div>
        </div>

        ${hasTabGroup && hasTabGroupTab
          ? html`
              <ha-tab-group @wa-tab-show=${this.handlePageSelected}>
                ${Object.values(EMenuItems).map(
                  (e) => html`
                    <ha-tab-group-tab
                      slot="nav"
                      panel="${e}"
                      .active=${path.page === e}
                    >
                      ${localize(`panels.${e}.title`, this.hass.language)}
                    </ha-tab-group-tab>
                  `,
                )}
              </ha-tab-group>
            `
          : html`
              <div class="custom-tabs">
                ${Object.values(EMenuItems).map(
                  (e) => html`
                    <button
                      class="custom-tab ${path.page === e ? "active" : ""}"
                      @click=${() => this.navigateToPage(e)}
                    >
                      ${localize(`panels.${e}.title`, this.hass.language)}
                    </button>
                  `,
                )}
              </div>
            `}
      </div>
      <div class="view">${this.getView(path)}</div>
      ${this._wizardOpen
        ? html`
            <si-setup-wizard
              .hass="${this.hass}"
              @wizard-close="${() => {
                this._wizardOpen = false;
              }}"
              @wizard-navigate="${(e: CustomEvent) => {
                const page = e.detail?.page ?? "zones";
                this._wizardOpen = false;
                this.navigateToPage(page);
              }}"
            ></si-setup-wizard>
          `
        : ""}
    `;
  }

  getView(path: Path) {
    const page = path.page;
    switch (page) {
      case "zones":
        return html`
          <smart-irrigation-view-zones
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${path}
            @open-wizard="${() => {
              this._wizardOpen = true;
            }}"
          ></smart-irrigation-view-zones>
        `;
      case "setup":
        return html`
          <smart-irrigation-view-setup
            .hass=${this.hass}
            .narrow=${this.narrow}
            @wizard-navigate="${(e: CustomEvent) => {
              const pg = e.detail?.page ?? "zones";
              this.navigateToPage(pg);
            }}"
          ></smart-irrigation-view-setup>
        `;
      default:
        return html`
          <smart-irrigation-view-zones
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${path}
            @open-wizard="${() => {
              this._wizardOpen = true;
            }}"
          ></smart-irrigation-view-zones>
        `;
    }
  }

  navigateToPage(page: string) {
    if (page !== getPath().page) {
      const newPath = exportPath(page);
      navigate(this, newPath);
      this.requestUpdate();
    } else {
      scrollTo(0, 0);
    }
  }

  handlePageSelected(ev: CustomEvent) {
    const newPage = ev.detail.name;
    if (newPage !== getPath().page) {
      const newPath = exportPath(newPage);
      navigate(this, newPath);
      this.requestUpdate();
    } else {
      scrollTo(0, 0);
    }
  }

  static get styles(): CSSResultGroup {
    return [
      commonStyle,
      css`
        :host {
          color: var(--primary-text-color);
          --paper-card-header-color: var(--primary-text-color);
        }
        .header {
          background-color: var(--app-header-background-color);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
        }
        .toolbar {
          height: var(--header-height);
          display: flex;
          align-items: center;
          font-size: 20px;
          padding: 0 16px;
          font-weight: 400;
          box-sizing: border-box;
        }
        .main-title {
          margin: 0 0 0 24px;
          line-height: 20px;
          flex-grow: 1;
        }
        ha-tab-group {
          margin-left: max(env(safe-area-inset-left), 24px);
          margin-right: max(env(safe-area-inset-right), 24px);
          --ha-tab-active-text-color: var(--app-header-text-color, white);
          --ha-tab-indicator-color: var(--app-header-text-color, white);
          --ha-tab-track-color: transparent;
        }

        .custom-tabs {
          display: flex;
          margin-left: max(env(safe-area-inset-left), 24px);
          margin-right: max(env(safe-area-inset-right), 24px);
          border-bottom: 1px solid
            rgba(
              var(--rgb-app-header-text-color, var(--rgb-text-primary-color)),
              0.12
            );
          overflow-x: auto;
        }

        .custom-tab {
          background: transparent;
          border: none;
          color: rgba(
            var(--rgb-app-header-text-color, var(--rgb-text-primary-color)),
            0.7
          );
          cursor: pointer;
          font-family: inherit;
          font-size: 14px;
          font-weight: 500;
          line-height: 48px;
          margin: 0;
          min-width: 72px;
          outline: none;
          padding: 0 12px;
          position: relative;
          text-transform: uppercase;
          transition: color 0.15s ease-in-out;
          white-space: nowrap;
          letter-spacing: 0.1em;
        }

        .custom-tab:hover {
          color: var(--app-header-text-color, white);
          background-color: rgba(
            var(--rgb-app-header-text-color, var(--rgb-text-primary-color)),
            0.04
          );
        }

        .custom-tab.active {
          color: var(--app-header-text-color, white);
        }

        .custom-tab.active::after {
          background-color: var(--app-header-text-color, white);
          bottom: 0;
          content: "";
          height: 2px;
          left: 0;
          position: absolute;
          right: 0;
        }

        .view {
          height: calc(100vh - 112px);
          display: flex;
          justify-content: center;
          overflow-y: auto;
        }

        .view > * {
          width: 600px;
          max-width: 600px;
        }

        .view > *:last-child {
          margin-bottom: 20px;
        }

        .version {
          font-size: 14px;
          font-weight: 500;
          color: rgba(var(--rgb-text-primary-color), 0.9);
        }
      `,
    ];
  }
}
