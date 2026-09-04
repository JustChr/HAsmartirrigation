import { LitElement, html, css, CSSResultGroup } from "lit";
import { property, state, customElement } from "lit/decorators.js";

/**
 * Reusable form field wrapper that adds a label, optional unit badge,
 * and a collapsible help text to any input element placed in its slot.
 *
 * Usage:
 *   <ip-field label="Size" unit="m²" help="The irrigated area..." required>
 *     <input type="number" ... />
 *   </ip-field>
 */
@customElement("ip-field")
export class SiField extends LitElement {
  @property() label = "";
  @property() unit = "";
  @property() help = "";
  @property({ type: Boolean }) required = false;

  @state() private _helpOpen = false;

  private _toggleHelp() {
    this._helpOpen = !this._helpOpen;
  }

  render() {
    return html`
      <div class="ip-field">
        <div class="ip-field-header">
          <span class="ip-field-label">
            ${this.label}${this.required
              ? html`<span class="ip-field-required" aria-label="required">
                  *</span
                >`
              : ""}
          </span>
          <span class="ip-field-meta">
            ${this.unit
              ? html`<span class="ip-field-unit">${this.unit}</span>`
              : ""}
            ${this.help
              ? html`
                  <button
                    class="ip-field-help-btn ${this._helpOpen ? "open" : ""}"
                    type="button"
                    aria-label="Toggle help"
                    @click="${this._toggleHelp}"
                  >
                    ⓘ
                  </button>
                `
              : ""}
          </span>
        </div>
        <slot></slot>
        ${this._helpOpen && this.help
          ? html`<div class="ip-field-help-text">${this.help}</div>`
          : ""}
      </div>
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      :host {
        display: block;
      }

      .ip-field {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin: 6px 0;
      }

      .ip-field-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
      }

      .ip-field-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .ip-field-required {
        color: var(--error-color, #b00020);
        font-weight: 700;
      }

      .ip-field-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-shrink: 0;
      }

      .ip-field-unit {
        font-size: 0.78rem;
        font-weight: 500;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border: 1px solid var(--divider-color);
        border-radius: 3px;
        padding: 1px 5px;
        white-space: nowrap;
      }

      .ip-field-help-btn {
        background: none;
        border: none;
        cursor: pointer;
        color: var(--secondary-text-color);
        font-size: 0.95rem;
        padding: 0 2px;
        line-height: 1;
        transition: color 0.15s;
        user-select: none;
      }

      .ip-field-help-btn:hover,
      .ip-field-help-btn.open {
        color: var(--primary-color);
      }

      .ip-field-help-text {
        font-size: 0.82rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-left: 3px solid var(--primary-color);
        border-radius: 0 3px 3px 0;
        padding: 6px 10px;
        line-height: 1.45;
        margin-top: 2px;
      }
    `;
  }
}
