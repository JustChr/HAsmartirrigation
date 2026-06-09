import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { UnsubscribeFunc } from "home-assistant-js-websocket";

import { HomeAssistant, SmartIrrigationMapping } from "../../types";
import { SubscribeMixin } from "../../subscribe-mixin";
import { localize } from "../../../localize/localize";
import { globalStyle } from "../../styles/global-style";
import { DOMAIN } from "../../const";
import {
  fetchWeatherForecast,
  WeatherForecast,
  fetchMappings,
  fetchMappingWeatherRecords,
} from "../../data/websockets";
import { formatMonthDayTime, isValidDate } from "../../common/datetime";

/**
 * Read-only weather display for the Weather & Location tab: the forward-looking
 * service forecast plus the collected weather records. Records are shown per
 * sensor group (mapping) — that's their real key — instead of repeated under
 * every zone. For the common single-source setup that's one table.
 */
@customElement("smart-irrigation-view-weather-data")
export class SmartIrrigationViewWeatherData extends SubscribeMixin(LitElement) {
  hass?: HomeAssistant;
  @property() narrow!: boolean;

  @state() private _forecast: WeatherForecast | null = null;
  @state() private _mappings: SmartIrrigationMapping[] = [];
  @state() private _records: Map<number, any[]> = new Map();
  @state() private _loading = true;

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._fetch();
    return [
      this.hass!.connection.subscribeMessage(() => this._fetch(), {
        type: DOMAIN + "_config_updated",
      }),
    ];
  }

  private async _fetch(): Promise<void> {
    if (!this.hass) return;
    try {
      const [forecast, mappings] = await Promise.all([
        fetchWeatherForecast(this.hass),
        fetchMappings(this.hass),
      ]);
      this._forecast = forecast;
      this._mappings = mappings || [];

      const records = new Map<number, any[]>();
      await Promise.all(
        this._mappings.map(async (m) => {
          if (m.id === undefined) return;
          try {
            records.set(
              m.id,
              (await fetchMappingWeatherRecords(
                this.hass!,
                m.id.toString(),
                0,
              )) || [],
            );
          } catch {
            /* skip a single mapping's records on error */
          }
        }),
      );
      this._records = records;
    } catch (e) {
      console.error("Failed to fetch weather data", e);
    } finally {
      this._loading = false;
    }
  }

  render(): TemplateResult {
    if (!this.hass) return html``;
    return html`${this._renderForecast()} ${this._renderRecords()}`;
  }

  private _renderForecast(): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;
    const fc = this._forecast;
    return html`
      <ha-card
        header="${localize("panels.setup.weather_data.forecast_title", lang)}"
      >
        <div class="card-content">
          ${!fc || !fc.available || fc.days.length === 0
            ? html`<div class="weather-note">
                ${localize("panels.setup.weather_data.forecast_none", lang)}
              </div>`
            : html`
                <div class="forecast-row">
                  ${fc.days.map((d) => this._renderForecastDay(d, lang))}
                </div>
              `}
        </div>
      </ha-card>
    `;
  }

  private _renderForecastDay(
    d: WeatherForecast["days"][number],
    lang: string,
  ): TemplateResult {
    const label = (() => {
      try {
        return new Intl.DateTimeFormat(lang, {
          weekday: "short",
          month: "short",
          day: "numeric",
        }).format(new Date(d.date + "T00:00:00"));
      } catch {
        return d.date;
      }
    })();
    const num = (v: number | null, unit: string, decimals = 1) =>
      v !== null && v !== undefined ? v.toFixed(decimals) + unit : "-";
    return html`
      <div class="forecast-day">
        <div class="forecast-date">${label}</div>
        <div class="forecast-temps">
          <span class="hi">${num(d.temp_max, "°")}</span>
          <span class="lo">${num(d.temp_min, "°")}</span>
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>${num(
            d.precipitation,
            " mm",
          )}
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-windy"></ha-icon>${num(
            d.windspeed,
            " m/s",
          )}
        </div>
      </div>
    `;
  }

  private _renderRecords(): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;
    if (this._loading && this._mappings.length === 0) {
      return html`<ha-card
        header="${localize("panels.mappings.weather-records.title", lang)}"
      >
        <div class="card-content">
          <div class="loading-indicator">
            ${localize("common.loading-messages.general", lang)}
          </div>
        </div>
      </ha-card>`;
    }
    if (this._mappings.length === 0) {
      return html`<ha-card
        header="${localize("panels.mappings.weather-records.title", lang)}"
      >
        <div class="card-content">
          <div class="weather-note">
            ${localize("panels.mappings.no_items", lang)}
          </div>
        </div>
      </ha-card>`;
    }
    return html`${this._mappings.map((m) =>
      this._renderMappingRecords(m, lang),
    )}`;
  }

  private _renderMappingRecords(
    mapping: SmartIrrigationMapping,
    lang: string,
  ): TemplateResult {
    const records =
      mapping.id !== undefined ? this._records.get(mapping.id) || [] : [];
    const title = `${localize("panels.mappings.weather-records.title", lang)} — ${mapping.name}`;
    const fmt = (ts: any) => {
      try {
        return isValidDate(ts) ? formatMonthDayTime(ts) : "-";
      } catch {
        return "-";
      }
    };
    const n = (v: any, unit: string, decimals = 1) =>
      v !== null && v !== undefined ? v.toFixed(decimals) + unit : "-";

    return html`
      <ha-card header="${title}">
        <div class="card-content">
          ${records.length === 0
            ? html`<div class="weather-note">
                ${localize("panels.mappings.weather-records.no-data", lang)}
              </div>`
            : html`
                <div class="weather-table">
                  <div class="weather-header">
                    <span
                      >${localize(
                        "panels.mappings.weather-records.timestamp",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize(
                        "panels.mappings.weather-records.temperature",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize(
                        "panels.mappings.weather-records.humidity",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize(
                        "panels.mappings.weather-records.dewpoint",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize(
                        "panels.mappings.weather-records.wind",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize(
                        "panels.mappings.weather-records.pressure",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize(
                        "panels.mappings.weather-records.precipitation",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize(
                        "panels.mappings.weather-records.retrieval-time",
                        lang,
                      )}</span
                    >
                  </div>
                  ${records.map(
                    (record) => html`
                      <div class="weather-row">
                        <span>${fmt(record.timestamp)}</span>
                        <span>${n(record.temperature, "°C")}</span>
                        <span>${n(record.humidity, "%")}</span>
                        <span>${n(record.dewpoint, "°C")}</span>
                        <span>${n(record.wind_speed, "m/s")}</span>
                        <span>${n(record.pressure, "hPa", 0)}</span>
                        <span>${n(record.precipitation, "mm")}</span>
                        <span>${fmt(record.retrieval_time)}</span>
                      </div>
                    `,
                  )}
                </div>
              `}
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

      .forecast-row {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 4px;
      }

      .forecast-day {
        flex: 0 0 auto;
        min-width: 92px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 10px 12px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        background: var(--secondary-background-color);
      }

      .forecast-date {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--primary-text-color);
      }

      .forecast-temps {
        display: flex;
        gap: 8px;
        align-items: baseline;
      }

      .forecast-temps .hi {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--primary-text-color);
      }

      .forecast-temps .lo {
        font-size: 0.9rem;
        color: var(--secondary-text-color);
      }

      .forecast-meta {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 0.8rem;
        color: var(--secondary-text-color);
      }

      .forecast-meta ha-icon {
        --mdc-icon-size: 16px;
        color: var(--secondary-text-color);
      }
    `;
  }
}
