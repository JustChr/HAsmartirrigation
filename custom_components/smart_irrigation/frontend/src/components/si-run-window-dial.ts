import {
  LitElement,
  svg,
  html,
  css,
  CSSResultGroup,
  SVGTemplateResult,
} from "lit";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../types";
import { localize } from "../../localize/localize";
import { ScheduleRows } from "../common/schedule-rows";
import {
  buildDial,
  fmtClock,
  fmtDuration,
  AzimuthResolver,
  DialModel,
  RunBar,
} from "../common/run-window-dial";
import { azimuthResolverFromLocation } from "../common/solar-azimuth";

// Tiny glyphs, drawn in a 24x24 box and scaled onto the ring's outside —
// verbatim from the settled prototype (plans/prototypes/schedule-ui.html).
const SUN_PATH = svg`<circle cx="12" cy="12" r="4.4" />
  ${Array.from({ length: 8 }, (_, i) => {
    const a = (i * Math.PI) / 4;
    const x1 = (12 + 6.6 * Math.cos(a)).toFixed(1);
    const y1 = (12 + 6.6 * Math.sin(a)).toFixed(1);
    const x2 = (12 + 9.2 * Math.cos(a)).toFixed(1);
    const y2 = (12 + 9.2 * Math.sin(a)).toFixed(1);
    return svg`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" />`;
  })}`;
const MOON_PATH = svg`<path d="M13.5,2.5A9.5,9.5 0 1,0 21.5,14 7.6,7.6 0 0,1 13.5,2.5Z" />`;
const DROP_PATH = svg`<path d="M12,2.6C12,2.6 18.6,9.4 18.6,13.7A6.6,6.6 0 0,1 5.4,13.7C5.4,9.4 12,2.6 12,2.6Z" />`;

/**
 * The WHEN section's 24-hour dial (GitLab #31): a 156px SVG showing the
 * window a user is designing and whether the schedule's nominal demand fits
 * inside it. Self-contained and narrow-input on purpose — GitLab #30 is
 * concurrently restructuring si-schedule-dialog.ts's markup into WHEN/
 * ZONES/SEASON cards, so this element is written to be dropped into
 * whichever container that lands in with a single import + tag, rather than
 * inlined into either rewrite of the dialog's render method.
 *
 * All geometry/planning is delegated to ../common/run-window-dial.ts (pure,
 * unit-tested); this component's own job is only to turn `hass` into the
 * dial's minute-of-day frame — sunrise/sunset from `sun.sun`, solar-azimuth
 * bounds via ../common/solar-azimuth.ts — plus localizing hover text and the
 * centre label and wrapping the returned path data in svg/html templates.
 * Both conversions into that frame live here so they cannot drift apart.
 */
@customElement("si-run-window-dial")
export class SiRunWindowDial extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ attribute: false }) rows!: ScheduleRows;
  @property({ attribute: false }) recurrence = "daily";
  @property({ attribute: false }) intervalHours?: number;
  @property({ attribute: false }) intervalStartTime?: string;
  /** Nominal demand for the schedule's zones under normal sequencing
   * (GitLab #26's `nominal_demand_seconds`), never tonight's live plan — a
   * schedule is a long-lived object and one night is a sample of one. */
  @property({ attribute: false }) nominalDemandSeconds = 0;

  /** `sun.sun` always exists on a live HA instance; guarded defensively for
   * the brief window during startup where it may not have attributes yet. */
  private _sunTimes(): { sunrise: number; sunset: number } {
    const sun = this.hass?.states?.["sun.sun"];
    const rising = sun?.attributes?.next_rising as string | undefined;
    const setting = sun?.attributes?.next_setting as string | undefined;
    const toMinutes = (iso: string | undefined, fallback: number) => {
      if (!iso) return fallback;
      const d = new Date(iso);
      if (isNaN(d.getTime())) return fallback;
      return d.getHours() * 60 + d.getMinutes();
    };
    return {
      sunrise: toMinutes(rising, 6 * 60),
      sunset: toMinutes(setting, 20 * 60),
    };
  }

  /**
   * Resolves a solar-azimuth bound to the same minute-of-day frame the sun
   * glyph above uses (GitLab #34). The math lives in ../common/solar-azimuth
   * and is a port of the backend's own resolver, so the dial draws the bound
   * the scheduler will actually fire on rather than a second opinion about
   * where the sun is.
   *
   * Latitude/longitude come from `hass.config`, the same values
   * `_resolve_event_instant` reads server-side. Missing config (never true on
   * a live instance, possible mid-startup) yields no resolver at all, which
   * degrades to drawing that end open rather than to a bound at 0 degrees
   * somewhere off the equator.
   */
  private _azimuthResolver(): AzimuthResolver | undefined {
    return azimuthResolverFromLocation(this.hass?.config, new Date());
  }

  private _renderRun(run: RunBar, lang: string): SVGTemplateResult {
    if (!run.wraps) {
      return svg`
        <path d="${run.arc}" class="d-run" style="stroke-linecap:butt" />
        <path d="${run.capStart}" class="cap-run" />
        <path d="${run.capEnd}" class="cap-run" />
      `;
    }
    return svg`
      <path d="${run.capStart}" class="cap-run" />
      ${run.fade.map(
        (seg) => svg`
          <path
            d="${seg.d}"
            class="d-run"
            style="stroke-linecap:butt"
            stroke-opacity="${seg.opacity.toFixed(2)}"
          />
        `,
      )}
    `;
  }

  private _centreText(
    model: DialModel,
    lang: string,
  ): { val: string; lbl: string } {
    const c = model.centre;
    switch (c.kind) {
      case "invalid":
        return { val: "—", lbl: "" };
      case "interval":
        return {
          val: localize(
            "panels.schedules.dial.every_hours",
            lang,
            "{hours}",
            c.intervalHours,
          ),
          lbl: localize(
            "panels.schedules.dial.per_day",
            lang,
            "{count}",
            c.perDay,
          ),
        };
      case "run":
        return {
          val: fmtDuration(c.minutes ?? 0),
          lbl: localize("panels.schedules.dial.run_label", lang),
        };
      case "window":
      default:
        return {
          val: fmtDuration(c.minutes ?? 0),
          lbl: localize("panels.schedules.dial.window_label", lang),
        };
    }
  }

  render() {
    if (!this.hass || !this.rows) return html``;
    const lang = this.hass.language;
    const { sunrise, sunset } = this._sunTimes();
    const model = buildDial({
      rows: this.rows,
      recurrence: this.recurrence,
      intervalHours: this.intervalHours,
      intervalStartTime: this.intervalStartTime,
      nominalDemandMinutes: this.nominalDemandSeconds / 60,
      sunriseMinutes: sunrise,
      sunsetMinutes: sunset,
      azimuthResolver: this._azimuthResolver(),
    });
    const { val, lbl } = this._centreText(model, lang);

    return html`
      <div class="viz-dial">
        <div class="d-wrap">
          <svg
            viewBox="0 0 132 132"
            role="img"
            aria-label="${localize("panels.schedules.dial.aria_label", lang)}"
          >
            <path d="${model.trackPath}" class="d-track" />
            ${model.windowArc
              ? model.windowArc.kind === "solid"
                ? svg`<path d="${model.windowArc.d}" class="d-win" />`
                : model.windowArc.segments.map(
                    (seg) => svg`
                      <path
                        d="${seg.d}"
                        class="d-win"
                        style="stroke-linecap:butt"
                        stroke-opacity="${seg.opacity.toFixed(2)}"
                      />
                    `,
                  )
              : ""}
            ${model.dottedPath
              ? svg`<path d="${model.dottedPath}" class="d-dotted" />`
              : ""}
            ${model.runs.map((r) => this._renderRun(r, lang))}
            ${model.overlaps.map(
              (o) => svg`
                <path d="${o.d}" class="d-overlap">
                  <title>
                    ${localize(
                      "panels.schedules.dial.collision",
                      lang,
                      "{from}",
                      fmtClock(o.fromMinutes),
                      "{to}",
                      fmtClock(o.toMinutes),
                    )}
                  </title>
                </path>
              `,
            )}
            ${model.ticks.map(
              (t) => svg`
                <line
                  x1="${t.x1.toFixed(1)}"
                  y1="${t.y1.toFixed(1)}"
                  x2="${t.x2.toFixed(1)}"
                  y2="${t.y2.toFixed(1)}"
                  class="d-tick"
                />
              `,
            )}
            <g
              class="g-sun"
              transform="translate(${(model.sun.x - 12 * 0.42).toFixed(1)},${(
                model.sun.y -
                12 * 0.42
              ).toFixed(1)}) scale(0.42)"
            >
              <title>
                ${localize(
                  "panels.schedules.dial.sunrise",
                  lang,
                  "{time}",
                  fmtClock(model.sun.minutes),
                )}
              </title>
              ${SUN_PATH}
            </g>
            <g
              class="g-moon"
              transform="translate(${(model.moon.x - 12 * 0.42).toFixed(1)},${(
                model.moon.y -
                12 * 0.42
              ).toFixed(1)}) scale(0.42)"
            >
              <title>
                ${localize(
                  "panels.schedules.dial.sunset",
                  lang,
                  "{time}",
                  fmtClock(model.moon.minutes),
                )}
              </title>
              ${MOON_PATH}
            </g>
            ${model.drops.map(
              (d) => svg`
                <g
                  class="g-drop"
                  transform="translate(${(d.x - 12 * 0.38).toFixed(1)},${(
                    d.y -
                    12 * 0.38
                  ).toFixed(1)}) scale(0.38)"
                >
                  <title>
                    ${localize(
                      "panels.schedules.dial.run",
                      lang,
                      "{from}",
                      fmtClock(d.fromMinutes),
                      "{to}",
                      fmtClock(d.toMinutes),
                    )}
                  </title>
                  ${DROP_PATH}
                </g>
              `,
            )}
          </svg>
          <div class="d-centre">
            <div class="d-val">${val}</div>
            <div class="d-lbl">${lbl}</div>
          </div>
        </div>
      </div>
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      /* Ring colors are mixed against the card background rather than kept
         as a fixed alpha over an assumed background: an alpha-based color
         resolves to a different actual color per theme (light vs dark card
         background), which was a real bug in the prototype's first pass. */
      .viz-dial {
        text-align: center;
        --dial-win: color-mix(
          in srgb,
          var(--primary-color) 34%,
          var(--card-background-color)
        );
        --dial-track: color-mix(
          in srgb,
          var(--primary-text-color) 9%,
          var(--card-background-color)
        );
      }
      .viz-dial .d-wrap {
        position: relative;
        display: inline-block;
        width: 100%;
        max-width: 156px;
      }
      .viz-dial svg {
        width: 100%;
        height: auto;
        display: block;
      }
      .viz-dial .d-track {
        fill: none;
        stroke: var(--dial-track);
        stroke-width: 10;
      }
      .viz-dial .d-win {
        fill: none;
        stroke: var(--dial-win);
        stroke-width: 10;
      }
      .viz-dial .d-dotted {
        fill: none;
        stroke: var(--accent-color);
        stroke-width: 3.5;
        opacity: 0.7;
        stroke-dasharray: 0.1 5;
        stroke-linecap: round;
      }
      .viz-dial .d-run {
        fill: none;
        stroke: var(--primary-color);
        stroke-width: 10;
      }
      .viz-dial .d-overlap {
        fill: none;
        stroke: var(--accent-color);
        stroke-width: 10;
      }
      .viz-dial .cap-run {
        fill: var(--primary-color);
        stroke: none;
      }
      .viz-dial .d-tick {
        stroke: color-mix(in srgb, var(--primary-text-color) 22%, transparent);
        stroke-width: 1;
      }
      .viz-dial .g-sun {
        fill: none;
        stroke: #f6b21b;
        stroke-width: 1.7;
        stroke-linecap: round;
      }
      .viz-dial .g-sun circle {
        fill: #f6b21b;
      }
      .viz-dial .g-moon {
        fill: #7e8cc4;
        stroke: none;
      }
      .viz-dial .g-drop {
        fill: var(--primary-color);
        stroke: none;
      }
      .viz-dial g[class^="g-"] {
        cursor: help;
      }
      .viz-dial .d-centre {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        pointer-events: none;
      }
      .viz-dial .d-val {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 15px;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
        color: var(--primary-text-color);
      }
      .viz-dial .d-lbl {
        font-size: 9.5px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--secondary-text-color);
        margin-top: 1px;
      }
    `;
  }
}
