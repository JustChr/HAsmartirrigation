import { LitElement, html, css, CSSResultGroup } from "lit";
import { property, customElement, state } from "lit/decorators.js";
import { HomeAssistant } from "../types";
import { mdiClose } from "@mdi/js";
import { localize } from "../../localize/localize";
import { IrrigationStartTrigger, TriggerType } from "../types";
import { dialogStyle } from "../styles/global-style";
import {
  TRIGGER_TYPE_SUNRISE,
  TRIGGER_TYPE_SUNSET,
  TRIGGER_TYPE_SOLAR_AZIMUTH,
} from "../const";

export interface TriggerDialogParams {
  trigger?: IrrigationStartTrigger;
  createTrigger?: boolean;
  triggerIndex?: number;
}

@customElement("trigger-dialog")
export class TriggerDialog extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ attribute: false }) public params?: TriggerDialogParams;
  @state() private _trigger?: IrrigationStartTrigger;

  public async showDialog(params: TriggerDialogParams): Promise<void> {
    this.params = params;

    if (params.createTrigger) {
      this._trigger = {
        type: TRIGGER_TYPE_SUNRISE,
        name: "",
        enabled: true,
        offset_minutes: 0,
        azimuth_angle: 90,
        account_for_duration: true,
      };
    } else if (params.trigger) {
      const t = params.trigger;
      this._trigger =
        t.type === TRIGGER_TYPE_SOLAR_AZIMUTH
          ? {
              type: t.type,
              name: t.name ?? "",
              enabled: t.enabled ?? true,
              offset_minutes: t.offset_minutes ?? 0,
              azimuth_angle: t.azimuth_angle ?? 90,
              account_for_duration: t.account_for_duration ?? true,
            }
          : {
              type: t.type,
              name: t.name ?? "",
              enabled: t.enabled ?? true,
              offset_minutes: t.offset_minutes ?? 0,
              account_for_duration: t.account_for_duration ?? true,
            };
    } else {
      this._trigger = undefined;
    }

    await this.updateComplete;
  }

  private _closeDialog() {
    this.params = undefined;
    this._trigger = undefined;
  }

  private _saveTrigger() {
    if (!this._trigger || !this.params) return;

    if (!this._trigger.name?.trim()) {
      alert(
        localize(
          "irrigation_start_triggers.validation.name_required",
          this.hass.language,
        ),
      );
      return;
    }

    if (this._trigger.type === TRIGGER_TYPE_SOLAR_AZIMUTH) {
      if (
        this._trigger.azimuth_angle === undefined ||
        isNaN(this._trigger.azimuth_angle)
      ) {
        alert(
          localize(
            "irrigation_start_triggers.validation.azimuth_invalid",
            this.hass.language,
          ),
        );
        return;
      }
      let angle = this._trigger.azimuth_angle % 360;
      if (angle < 0) angle += 360;
      this._trigger.azimuth_angle = angle;
    }

    this.dispatchEvent(
      new CustomEvent("trigger-save", {
        detail: {
          trigger: this._trigger,
          isNew: this.params!.createTrigger,
          index: this.params!.triggerIndex,
        },
        bubbles: true,
        composed: true,
      }),
    );

    this._closeDialog();
  }

  private _deleteTrigger() {
    if (!this.params || this.params.createTrigger) return;

    this.dispatchEvent(
      new CustomEvent("trigger-delete", {
        detail: { index: this.params.triggerIndex },
        bubbles: true,
        composed: true,
      }),
    );

    this._closeDialog();
  }

  private _updateTrigger(changes: Partial<IrrigationStartTrigger>) {
    if (!this._trigger) return;
    this._trigger = { ...this._trigger, ...changes };
    this.requestUpdate();
  }

  render() {
    if (!this.params || !this._trigger) return html``;

    const isCreate = this.params.createTrigger;
    const title = isCreate
      ? localize(
          "irrigation_start_triggers.dialog.add_title",
          this.hass.language,
        )
      : localize(
          "irrigation_start_triggers.dialog.edit_title",
          this.hass.language,
        );

    return html`
      <ha-dialog
        open
        .heading=${true}
        @closed=${this._closeDialog}
        @close-dialog=${this._closeDialog}
      >
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button
              slot="navigationIcon"
              dialogAction="cancel"
              .path=${mdiClose}
            ></ha-icon-button>
            <span slot="title">${title}</span>
          </ha-header-bar>
        </div>

        <div class="wrapper">
          <div class="field">
            <label
              >${localize(
                "irrigation_start_triggers.fields.name.name",
                this.hass.language,
              )}</label
            >
            <input
              type="text"
              .value=${this._trigger.name || ""}
              @input=${this._nameChanged}
              required
            />
          </div>

          <div class="field">
            <label
              >${localize(
                "irrigation_start_triggers.fields.type.name",
                this.hass.language,
              )}</label
            >
            <select @change=${this._typeChanged}>
              <option
                value=${TRIGGER_TYPE_SUNRISE}
                ?selected=${this._trigger.type === TRIGGER_TYPE_SUNRISE}
              >
                ${localize(
                  "irrigation_start_triggers.trigger_types.sunrise",
                  this.hass.language,
                )}
              </option>
              <option
                value=${TRIGGER_TYPE_SUNSET}
                ?selected=${this._trigger.type === TRIGGER_TYPE_SUNSET}
              >
                ${localize(
                  "irrigation_start_triggers.trigger_types.sunset",
                  this.hass.language,
                )}
              </option>
              <option
                value=${TRIGGER_TYPE_SOLAR_AZIMUTH}
                ?selected=${this._trigger.type === TRIGGER_TYPE_SOLAR_AZIMUTH}
              >
                ${localize(
                  "irrigation_start_triggers.trigger_types.solar_azimuth",
                  this.hass.language,
                )}
              </option>
            </select>
          </div>

          <div class="field-row">
            <label
              >${localize(
                "irrigation_start_triggers.fields.enabled.name",
                this.hass.language,
              )}</label
            >
            <input
              type="checkbox"
              ?checked=${this._trigger.enabled}
              @change=${this._enabledChanged}
            />
          </div>

          <div class="field">
            <label
              >${localize(
                "irrigation_start_triggers.fields.offset_minutes.name",
                this.hass.language,
              )}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                .value=${this._trigger.offset_minutes?.toString() || "0"}
                min="-1440"
                max="1440"
                step="1"
                @input=${this._offsetChanged}
              />
              <span class="suffix">min</span>
            </div>
          </div>

          <div class="field-row">
            <label
              >${localize(
                "irrigation_start_triggers.fields.account_for_duration.name",
                this.hass.language,
              )}</label
            >
            <input
              type="checkbox"
              ?checked=${this._trigger.account_for_duration}
              @change=${this._accountForDurationChanged}
            />
          </div>

          ${this._trigger.type === TRIGGER_TYPE_SOLAR_AZIMUTH
            ? html`
                <div class="field">
                  <label
                    >${localize(
                      "irrigation_start_triggers.fields.azimuth_angle.name",
                      this.hass.language,
                    )}</label
                  >
                  <div class="input-suffix-row">
                    <input
                      type="number"
                      .value=${this._trigger.azimuth_angle?.toString() || "90"}
                      min="0"
                      max="359"
                      step="1"
                      @input=${this._azimuthChanged}
                    />
                    <span class="suffix">°</span>
                  </div>
                </div>
              `
            : ""}
        </div>

        <ha-dialog-footer slot="footer">
          <ha-button
            slot="secondaryAction"
            appearance="plain"
            @click=${this._closeDialog}
            dialogAction="cancel"
          >
            ${localize(
              "irrigation_start_triggers.dialog.cancel",
              this.hass.language,
            )}
          </ha-button>
          ${!isCreate
            ? html`
                <ha-button
                  slot="secondaryAction"
                  appearance="plain"
                  @click=${this._deleteTrigger}
                  dialogAction="close"
                >
                  ${localize(
                    "irrigation_start_triggers.dialog.delete",
                    this.hass.language,
                  )}
                </ha-button>
              `
            : ""}
          <ha-button
            slot="primaryAction"
            appearance="accent"
            @click=${this._saveTrigger}
            dialogAction="close"
          >
            ${localize(
              "irrigation_start_triggers.dialog.save",
              this.hass.language,
            )}
          </ha-button>
        </ha-dialog-footer>
      </ha-dialog>
    `;
  }

  private _nameChanged(event: Event) {
    this._updateTrigger({ name: (event.target as HTMLInputElement).value });
  }

  private _typeChanged(event: Event) {
    const newType = (event.target as HTMLSelectElement).value as TriggerType;
    if (!newType) return;

    if (newType === TRIGGER_TYPE_SOLAR_AZIMUTH) {
      this._trigger = {
        type: TRIGGER_TYPE_SOLAR_AZIMUTH,
        name: this._trigger?.name ?? "",
        enabled: this._trigger?.enabled ?? true,
        offset_minutes: this._trigger?.offset_minutes ?? 0,
        azimuth_angle: this._trigger?.azimuth_angle ?? 90,
        account_for_duration: this._trigger?.account_for_duration ?? true,
      };
    } else {
      this._trigger = {
        type: newType,
        name: this._trigger?.name ?? "",
        enabled: this._trigger?.enabled ?? true,
        offset_minutes: this._trigger?.offset_minutes ?? 0,
        account_for_duration: this._trigger?.account_for_duration ?? true,
      };
    }
    this.requestUpdate();
  }

  private _enabledChanged(event: Event) {
    this._updateTrigger({
      enabled: (event.target as HTMLInputElement).checked,
    });
  }

  private _offsetChanged(event: Event) {
    this._updateTrigger({
      offset_minutes: parseInt((event.target as HTMLInputElement).value) || 0,
    });
  }

  private _accountForDurationChanged(event: Event) {
    this._updateTrigger({
      account_for_duration: (event.target as HTMLInputElement).checked,
    });
  }

  private _azimuthChanged(event: Event) {
    if (this._trigger?.type !== TRIGGER_TYPE_SOLAR_AZIMUTH) return;
    let value = parseInt((event.target as HTMLInputElement).value, 10);
    if (isNaN(value)) value = 90;
    this._updateTrigger({ azimuth_angle: value });
  }

  static get styles(): CSSResultGroup {
    return [
      dialogStyle,
      css`
        .wrapper {
          color: var(--primary-text-color);
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .field {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .field label,
        .field-row label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--secondary-text-color);
        }

        .field input[type="text"],
        .field input[type="number"],
        .field select {
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 1rem;
          font-family: inherit;
          width: 100%;
          box-sizing: border-box;
        }

        .field input[type="text"]:focus,
        .field input[type="number"]:focus,
        .field select:focus {
          outline: none;
          border-color: var(--primary-color);
        }

        .field-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          min-height: 40px;
        }

        .field-row label {
          flex: 1;
          font-size: 1rem;
          color: var(--primary-text-color);
          font-weight: normal;
        }

        .field-row input[type="checkbox"] {
          width: 18px;
          height: 18px;
          cursor: pointer;
          accent-color: var(--primary-color);
        }

        .input-suffix-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .input-suffix-row input {
          flex: 1;
        }

        .suffix {
          color: var(--secondary-text-color);
          font-size: 0.875rem;
          white-space: nowrap;
        }
      `,
    ];
  }
}
