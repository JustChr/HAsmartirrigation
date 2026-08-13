import { LitElement, html, css, CSSResultGroup, TemplateResult } from "lit";
import { property, customElement, state } from "lit/decorators.js";
import { HomeAssistant } from "../../types";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { mdiDelete, mdiPencil, mdiPlus } from "@mdi/js";

import {
  fetchSchedules,
  saveSchedule,
  deleteSchedule,
  fetchZones,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";
import { localize } from "../../../localize/localize";
import { globalStyle } from "../../styles/global-style";
import { DOMAIN } from "../../const";
import { SmartIrrigationZone } from "../../types";
import { showErrorToast } from "../../helpers";
import {
  Schedule,
  emptySchedule,
  recurrenceLabel,
} from "../../components/si-schedule-dialog";

const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

@customElement("smart-irrigation-view-schedules")
class SmartIrrigationViewSchedules extends SubscribeMixin(LitElement) {
  @property({ attribute: false }) public hass!: HomeAssistant;

  @state() private _schedules: Schedule[] = [];
  @state() private _zones: SmartIrrigationZone[] = [];
  @state() private _isLoading = true;
  @state() private _showDialog = false;
  @state() private _editingSchedule: Schedule = emptySchedule();
  @state() private _editingId: string | null = null;

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._load();
    return [
      this.hass!.connection.subscribeMessage(() => this._load(), {
        type: DOMAIN + "_config_updated",
      }),
    ];
  }

  private async _load() {
    if (!this.hass) return;
    try {
      const [schedules, zones] = await Promise.all([
        fetchSchedules(this.hass),
        fetchZones(this.hass),
      ]);
      this._schedules = schedules || [];
      this._zones = zones || [];
    } catch (e) {
      console.error("Failed to load schedules", e);
      showErrorToast(this, this.hass, "common.errors.load_failed", e);
    } finally {
      this._isLoading = false;
    }
  }

  private _openAdd() {
    this._editingSchedule = emptySchedule();
    this._editingId = null;
    this._showDialog = true;
  }

  private _openEdit(s: Schedule) {
    this._editingSchedule = { ...s };
    this._editingId = s.id ?? null;
    this._showDialog = true;
  }

  private _closeDialog() {
    this._showDialog = false;
  }

  private async _save() {
    const schedule = { ...this._editingSchedule };
    if (this._editingId) schedule.id = this._editingId;
    // Convert zones: if "all" keep as string, else keep as array
    try {
      // The backend answers a rejected schedule with a *successful* websocket
      // result carrying {success: false, error}, not an exception — so without
      // this the dialog would close on a validation failure and the edit would
      // silently vanish on the next reload.
      const result = await saveSchedule(this.hass, schedule);
      if (result && result.success === false) {
        throw new Error(result.error || "");
      }
      this._closeDialog();
      await this._load();
    } catch (e) {
      console.error("Failed to save schedule", e);
      showErrorToast(this, this.hass, "common.errors.save_failed", e);
    }
  }

  private async _delete(id: string) {
    try {
      await deleteSchedule(this.hass, id);
      await this._load();
    } catch (e) {
      console.error("Failed to delete schedule", e);
      showErrorToast(this, this.hass, "common.errors.delete_failed", e);
    }
  }

  private _onScheduleChanged(e: CustomEvent) {
    this._editingSchedule = e.detail.value;
  }

  private _zonesLabel(zones: string | string[]) {
    if (zones === "all")
      return localize("panels.schedules.zones_all", this.hass.language);
    if (Array.isArray(zones)) {
      const names = zones
        .map((id) => {
          const z = this._zones.find((z) => String(z.id) === String(id));
          return z ? z.name : id;
        })
        .join(", ");
      return names || zones.join(", ");
    }
    return String(zones);
  }

  private _dialogTitle(): string {
    return this._editingId
      ? localize("panels.schedules.dialog.edit_title", this.hass.language)
      : localize("panels.schedules.dialog.add_title", this.hass.language);
  }

  render(): TemplateResult {
    if (!this.hass) return html``;

    if (this._isLoading) {
      return html`
        <ha-card
          header="${localize("panels.schedules.title", this.hass.language)}"
        >
          <div class="card-content">
            ${localize("common.loading", this.hass.language)}...
          </div>
        </ha-card>
      `;
    }

    return html`
      ${this._showDialog
        ? html`
            <si-schedule-dialog
              .hass=${this.hass}
              .schedule=${this._editingSchedule}
              .zones=${this._zones}
              .heading=${this._dialogTitle()}
              @schedule-changed=${this._onScheduleChanged}
              @save=${this._save}
              @cancel=${this._closeDialog}
            ></si-schedule-dialog>
          `
        : ""}

      <ha-card
        header="${localize("panels.schedules.title", this.hass.language)}"
      >
        <div class="card-content">
          ${localize("panels.schedules.description", this.hass.language)}
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${mdiPlus}" />
            </svg>
            ${localize("panels.schedules.add", this.hass.language)}
          </button>
        </div>
      </ha-card>

      ${this._schedules.length === 0
        ? html`
            <ha-card>
              <div class="card-content">
                ${localize("panels.schedules.no_items", this.hass.language)}
              </div>
            </ha-card>
          `
        : this._schedules.map(
            (s) => html`
              <ha-card header="${s.name}">
                <div class="card-content">
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.schedules.fields.recurrence",
                        this.hass.language,
                      )}:</span
                    >
                    <span
                      >${recurrenceLabel(
                        s.recurrence,
                        this.hass.language,
                      )}</span
                    >
                  </div>
                  ${s.recurrence !== "interval" &&
                  s.start_mode === "time" &&
                  s.start_time
                    ? html`
                        <div class="info-row">
                          <span class="info-label"
                            >${localize(
                              "panels.schedules.fields.start_time",
                              this.hass.language,
                            )}:</span
                          >
                          <span>${s.start_time}</span>
                        </div>
                      `
                    : ""}
                  ${s.recurrence !== "interval" &&
                  s.finish_mode === "time" &&
                  s.finish_time
                    ? html`
                        <div class="info-row">
                          <span class="info-label"
                            >${localize(
                              "panels.schedules.fields.finish_time",
                              this.hass.language,
                            )}:</span
                          >
                          <span>${s.finish_time}</span>
                        </div>
                      `
                    : ""}
                  ${s.interval_hours
                    ? html`
                        <div class="info-row">
                          <span class="info-label"
                            >${localize(
                              "panels.schedules.fields.interval_hours",
                              this.hass.language,
                            )}:</span
                          >
                          <span
                            >${s.interval_hours}
                            ${localize(
                              "panels.schedules.hours",
                              this.hass.language,
                            )}</span
                          >
                        </div>
                      `
                    : ""}
                  ${s.recurrence === "interval" && s.start_time
                    ? html`
                        <div class="info-row">
                          <span class="info-label"
                            >${localize(
                              "panels.schedules.fields.start_time",
                              this.hass.language,
                            )}:</span
                          >
                          <span>${s.start_time}</span>
                        </div>
                      `
                    : ""}
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.schedules.fields.zones",
                        this.hass.language,
                      )}:</span
                    >
                    <span>${this._zonesLabel(s.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${localize(
                        "panels.schedules.fields.enabled",
                        this.hass.language,
                      )}:</span
                    >
                    <span
                      >${s.enabled
                        ? localize("common.labels.yes", this.hass.language)
                        : localize(
                            "common.labels.no",
                            this.hass.language,
                          )}</span
                    >
                  </div>
                </div>
                <div class="card-content action-buttons">
                  <div class="action-buttons-left">
                    <div
                      class="action-button-left"
                      @click=${() => this._openEdit(s)}
                    >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${mdiPencil}" />
                      </svg>
                      <span class="action-button-label"
                        >${localize(
                          "common.actions.edit",
                          this.hass.language,
                        )}</span
                      >
                    </div>
                  </div>
                  <div class="action-buttons-right">
                    <div
                      class="action-button-right"
                      @click=${() => s.id && this._delete(s.id)}
                    >
                      <span class="action-button-label"
                        >${localize(
                          "common.actions.delete",
                          this.hass.language,
                        )}</span
                      >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${mdiDelete}" />
                      </svg>
                    </div>
                  </div>
                </div>
              </ha-card>
            `,
          )}
    `;
  }

  static get styles(): CSSResultGroup {
    return [
      globalStyle,
      css`
        .info-row {
          display: flex;
          gap: 8px;
          margin-bottom: 4px;
          font-size: 0.9rem;
        }
        .info-label {
          font-weight: 500;
          color: var(--secondary-text-color);
          min-width: 80px;
        }
        .add-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: var(--primary-color);
          color: var(--text-primary-color, #fff);
          border: none;
          border-radius: 4px;
          font-size: 0.95rem;
          cursor: pointer;
        }
      `,
    ];
  }
}
