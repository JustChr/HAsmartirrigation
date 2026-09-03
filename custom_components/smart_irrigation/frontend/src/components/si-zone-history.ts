import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement } from "lit/decorators.js";
import { unsafeHTML } from "lit/directives/unsafe-html.js";
import {
  HomeAssistant,
  SmartIrrigationConfig,
  SmartIrrigationZone,
  RunLogEntry,
} from "../types";
import { localize } from "../../localize/localize";
import { formatVolume } from "../common/units";
import { formatDateTime } from "../common/datetime";
import { globalStyle } from "../styles/global-style";
import { CONF_METRIC } from "../const";

/** Cumulative water usage + a bounded "Recent runs" list for ONE zone.
 * Pure presentation: extracted from view-zone-settings so it can live on the
 * History tab. Reuses the existing panels.zones.history.* strings. */
@customElement("si-zone-history")
export class SiZoneHistory extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ attribute: false }) zone!: SmartIrrigationZone;
  @property({ attribute: false }) config?: SmartIrrigationConfig;

  render(): TemplateResult {
    if (!this.hass || !this.zone) return html``;
    const metric = this.config?.units === CONF_METRIC;
    const log = this.zone.run_log ?? [];
    const lang = this.hass.language;

    return html`
      <div class="history-usage">
        <span class="history-usage-label"
          >${localize("panels.zones.history.total_used", lang)}</span
        >
        <span class="history-usage-value"
          >${formatVolume(this.zone.water_used_total ?? 0, metric)}</span
        >
      </div>
      ${log.length === 0
        ? html`<div class="weather-note">
            ${localize("panels.zones.history.empty", lang)}
          </div>`
        : html`
            <table class="history-table">
              <thead>
                <tr>
                  <th>${localize("panels.zones.history.when", lang)}</th>
                  <th>${localize("panels.zones.history.result", lang)}</th>
                  <th class="num">
                    ${localize("panels.zones.history.volume", lang)}
                  </th>
                  <th>${localize("panels.zones.history.detail", lang)}</th>
                </tr>
              </thead>
              <tbody>
                ${log.map((entry) => this._renderRow(entry, metric))}
              </tbody>
            </table>
          `}
    `;
  }

  private _renderRow(entry: RunLogEntry, metric: boolean): TemplateResult {
    const lang = this.hass.language;
    const resultLabel = localize(
      `panels.zones.history.results.${entry.result}`,
      lang,
    );
    let detail = "";
    if (entry.detail) {
      if (entry.result === "skipped") {
        detail = entry.detail
          .split(",")
          .map((r) => localize(`panels.zones.outlook.checks.${r}`, lang) || r)
          .join(", ");
      } else if (/^[A-Za-z0-9_-]+$/.test(entry.detail)) {
        detail =
          localize(`panels.zones.fault.${entry.detail}`, lang) || entry.detail;
      } else {
        detail = entry.detail;
      }
    }
    return html`
      <tr>
        <td>${formatDateTime(entry.ts)}</td>
        <td>
          <span class="history-chip history-${entry.result}"
            >${resultLabel || entry.result}</span
          >
        </td>
        <td class="num">
          ${entry.volume_l > 0 ? formatVolume(entry.volume_l, metric) : "-"}
        </td>
        <td class="history-detail">${unsafeHTML(detail)}</td>
      </tr>
    `;
  }

  static get styles(): CSSResultGroup {
    return [
      globalStyle,
      css`
        /* Moved verbatim from view-zone-settings.ts (lines 2237-2292). The
           empty-state .weather-note rule is NOT copied: it lives in
           globalStyle, which is already included above. */
        .history-usage {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 12px;
        }
        .history-usage-value {
          font-size: 1.25rem;
          font-weight: 600;
        }
        .history-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }
        .history-table th,
        .history-table td {
          text-align: left;
          padding: 4px 8px;
          border-bottom: 1px solid var(--divider-color);
          vertical-align: top;
        }
        .history-table th.num,
        .history-table td.num {
          text-align: right;
          white-space: nowrap;
        }
        .history-detail {
          color: var(--secondary-text-color);
        }
        .history-chip {
          display: inline-block;
          padding: 1px 8px;
          border-radius: 10px;
          font-size: 0.75rem;
          font-weight: 600;
          white-space: nowrap;
          color: #fff;
          background: var(--secondary-text-color);
        }
        .history-completed {
          background: var(--success-color, #2e7d32);
        }
        .history-partial {
          background: var(--warning-color, #f9a825);
        }
        .history-failed {
          background: var(--error-color, #c62828);
        }
        .history-skipped {
          background: var(--info-color, #0277bd);
        }
        .history-observed {
          background: #00897b;
        }
      `,
    ];
  }
}
