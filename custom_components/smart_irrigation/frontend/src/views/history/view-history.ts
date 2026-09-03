import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import {
  HomeAssistant,
  SmartIrrigationConfig,
  SmartIrrigationZone,
} from "../../types";
import { SubscribeMixin } from "../../subscribe-mixin";
import { fetchConfig, fetchZones } from "../../data/websockets";
import { Path } from "../../common/navigation";
import { DOMAIN } from "../../const";
import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import "../../components/si-zone-history";

@customElement("smart-irrigation-view-history")
export class SmartIrrigationViewHistory extends SubscribeMixin(LitElement) {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public narrow!: boolean;
  @property({ attribute: false }) public path?: Path;

  @state() private _zones: SmartIrrigationZone[] = [];
  @state() private _config?: SmartIrrigationConfig;
  @state() private _selectedZoneId?: number;

  // Same self-fetch pattern as view-zone-settings.ts (hassSubscribe ~line 252):
  // fetch on connect and re-fetch on the domain's config-updated message.
  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._fetchData().catch(() => {});
    return [
      this.hass!.connection.subscribeMessage(
        () => this._fetchData().catch(() => {}),
        { type: DOMAIN + "_config_updated" },
      ),
    ];
  }

  private async _fetchData(): Promise<void> {
    if (!this.hass) return;
    const [config, zones] = await Promise.all([
      fetchConfig(this.hass),
      fetchZones(this.hass),
    ]);
    this._config = config;
    this._zones = zones;
  }

  /** The zone whose history is shown: the explicit selection if it still
   * exists, otherwise the first zone. */
  private _effectiveZone(): SmartIrrigationZone | undefined {
    if (!this._zones.length) return undefined;
    return (
      this._zones.find((z) => z.id === this._selectedZoneId) ?? this._zones[0]
    );
  }

  render(): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;

    if (!this._zones.length) {
      return html`
        <ha-card header="${localize("panels.history.title", lang)}">
          <div class="card-content">
            <div class="weather-note">
              ${localize("panels.history.no_zones", lang)}
            </div>
          </div>
        </ha-card>
      `;
    }

    const zone = this._effectiveZone()!;
    return html`
      <ha-card header="${localize("panels.history.title", lang)}">
        <div class="card-content">
          <div class="zone-picker">
            <label for="zone-select"
              >${localize("panels.history.select_zone", lang)}</label
            >
            <select
              id="zone-select"
              @change=${(e: Event) => {
                this._selectedZoneId = Number(
                  (e.target as HTMLSelectElement).value,
                );
              }}
            >
              ${this._zones.map(
                (z) => html`
                  <option value="${z.id}" ?selected=${z.id === zone.id}>
                    ${z.name}
                  </option>
                `,
              )}
            </select>
          </div>
          <si-zone-history
            .hass=${this.hass}
            .zone=${zone}
            .config=${this._config}
          ></si-zone-history>
        </div>
      </ha-card>
    `;
  }

  static get styles(): CSSResultGroup {
    return [
      globalStyle,
      css`
        .zone-picker {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 16px;
        }
        .zone-picker select {
          flex: 1;
        }
      `,
    ];
  }
}
