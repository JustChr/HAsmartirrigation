import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, state, customElement } from "lit/decorators.js";
import { UnsubscribeFunc } from "home-assistant-js-websocket";

import { HomeAssistant, SmartIrrigationMapping } from "../../types";
import { SubscribeMixin } from "../../subscribe-mixin";
import { localize } from "../../../localize/localize";
import { globalStyle } from "../../styles/global-style";
import { DOMAIN, CONF_IMPERIAL } from "../../const";
import {
  fetchConfig,
  fetchWeatherForecast,
  WeatherForecast,
  fetchMappings,
  fetchMappingWeatherRecords,
  fetchWateringCalendar,
} from "../../data/websockets";
import { formatMonthDayTime, isValidDate } from "../../common/datetime";
import { convertWeather, formatWeather } from "../../common/units";

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
  // Display unit system (false = imperial). Backend values are always metric.
  @state() private _metric = true;
  // Monthly climate estimates (ET/precip/temp) — location-global, same for all
  // zones, so shown once here. Per-zone watering volume stays in My Zones.
  @state() private _climate: any[] = [];

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
      const [forecast, mappings, config, calendar] = await Promise.all([
        fetchWeatherForecast(this.hass),
        fetchMappings(this.hass),
        fetchConfig(this.hass),
        fetchWateringCalendar(this.hass),
      ]);
      this._forecast = forecast;
      this._mappings = mappings || [];
      this._metric = config?.units !== CONF_IMPERIAL;
      // Calendar is keyed by zone id; the climate columns are identical across
      // zones, so take the first zone's monthly estimates.
      const calZones = calendar ? Object.values(calendar) : [];
      this._climate =
        calZones.length > 0
          ? (calZones[0] as any)?.monthly_estimates || []
          : [];

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
    return html`${this._renderForecast()} ${this._renderRecords()}
    ${this._renderSeasonal()}`;
  }

  private _renderSeasonal(): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;
    return html`
      <ha-card
        header="${localize("panels.setup.weather_data.seasonal_title", lang)}"
      >
        <div class="card-content">
          ${this._climate.length === 0
            ? html`<div class="weather-note">
                ${localize("panels.zones.calendar.no_data", lang)}
              </div>`
            : html`
                <div class="seasonal-table">
                  <div class="weather-header">
                    <span
                      >${localize("panels.zones.calendar.month", lang)}</span
                    >
                    <span>${localize("panels.zones.calendar.et", lang)}</span>
                    <span
                      >${localize(
                        "panels.zones.calendar.precipitation",
                        lang,
                      )}</span
                    >
                    <span
                      >${localize("panels.zones.calendar.avg_temp", lang)}</span
                    >
                  </div>
                  ${this._climate.map(
                    (m: any) => html`
                      <div class="weather-row">
                        <span
                          >${m.month_name || `Month ${m.month}` || "-"}</span
                        >
                        <span
                          >${formatWeather(
                            m.estimated_et_mm,
                            "precipitation",
                            this._metric,
                          )}</span
                        >
                        <span
                          >${formatWeather(
                            m.average_precipitation_mm,
                            "precipitation",
                            this._metric,
                          )}</span
                        >
                        <span
                          >${formatWeather(
                            m.average_temperature_c,
                            "temperature",
                            this._metric,
                          )}</span
                        >
                      </div>
                    `,
                  )}
                </div>
              `}
        </div>
      </ha-card>
    `;
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
    const deg = (v: number | null) => {
      const c = convertWeather(v, "temperature", this._metric);
      return c ? `${Math.round(c.value)}°` : "-";
    };
    return html`
      <div class="forecast-day">
        <div class="forecast-date">${label}</div>
        <div class="forecast-temps">
          <span class="hi">${deg(d.temp_max)}</span>
          <span class="lo">${deg(d.temp_min)}</span>
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>${formatWeather(
            d.precipitation,
            "precipitation",
            this._metric,
          )}
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-windy"></ha-icon>${formatWeather(
            d.windspeed,
            "windspeed",
            this._metric,
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
    const pct = (v: any) =>
      v !== null && v !== undefined ? v.toFixed(1) + " %" : "-";

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
                        <span
                          >${formatWeather(
                            record.temperature,
                            "temperature",
                            this._metric,
                          )}</span
                        >
                        <span>${pct(record.humidity)}</span>
                        <span
                          >${formatWeather(
                            record.dewpoint,
                            "temperature",
                            this._metric,
                          )}</span
                        >
                        <span
                          >${formatWeather(
                            record.wind_speed,
                            "windspeed",
                            this._metric,
                          )}</span
                        >
                        <span
                          >${formatWeather(
                            record.pressure,
                            "pressure",
                            this._metric,
                          )}</span
                        >
                        <span
                          >${formatWeather(
                            record.precipitation,
                            "precipitation",
                            this._metric,
                          )}</span
                        >
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

      /* 4-column seasonal/climate table (month + ET + precip + temp). Reuses the
         globalStyle .weather-header / .weather-row (display:contents) cells. */
      .seasonal-table {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 8px;
        font-size: 0.85em;
      }
    `;
  }
}
