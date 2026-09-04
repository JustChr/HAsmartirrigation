import { TemplateResult, LitElement, html, css, CSSResultGroup } from "lit";
import { live } from "lit/directives/live.js";
import { query } from "lit/decorators.js";
import { property, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../../types";
import { loadHaForm } from "../../load-ha-elements";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import {
  deleteModule,
  fetchConfig,
  fetchAllModules,
  fetchModules,
  saveModule,
  fetchZones,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";

import {
  SmartIrrigationConfig,
  SmartIrrigationZone,
  SmartIrrigationModule,
} from "../../types";
import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import { DOMAIN } from "../../const";
import { prettyPrint, getPart, showErrorToast } from "../../helpers";

@customElement("smart-irrigation-view-modules")
class SmartIrrigationViewModules extends SubscribeMixin(LitElement) {
  hass?: HomeAssistant;
  @property() config?: SmartIrrigationConfig;

  @property({ type: Array })
  private zones: SmartIrrigationZone[] = [];
  @property({ type: Array })
  private modules: SmartIrrigationModule[] = [];
  @property({ type: Array })
  private allmodules: SmartIrrigationModule[] = [];

  @property({ type: Boolean })
  private isLoading = true;

  private _initialLoadDone = false;

  @property({ type: Boolean })
  private isSaving = false;

  // Prevent excessive re-renders
  private _updateScheduled = false;
  private _scheduleUpdate() {
    if (this._updateScheduled) return;
    this._updateScheduled = true;
    requestAnimationFrame(() => {
      this._updateScheduled = false;
      this.requestUpdate();
    });
  }

  // Global debounce timer for better performance
  private globalDebounceTimer: number | null = null;

  // Cache for rendered module cards
  private moduleCache = new Map<string, TemplateResult>();

  @query("#moduleInput")
  private moduleInput!: HTMLSelectElement;

  firstUpdated() {
    // Load HA form elements in background without blocking UI
    loadHaForm().catch((error) => {
      console.error("Failed to load HA form:", error);
    });
  }

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    // Initial data fetch for UI setup with proper error handling
    this._fetchData().catch((error) => {
      console.error("Failed to fetch initial data:", error);
    });

    return [
      this.hass!.connection.subscribeMessage(
        () => {
          // Update data when notified of changes with proper error handling
          this._fetchData().catch((error) => {
            console.error("Failed to fetch data on config update:", error);
          });
        },
        {
          type: DOMAIN + "_config_updated",
        },
      ),
    ];
  }

  private async _fetchData(): Promise<void> {
    if (!this.hass) {
      return;
    }

    const isInitial = !this._initialLoadDone;

    if (isInitial) {
      this.isLoading = true;
      this._scheduleUpdate();
    }

    try {
      const [config, zones, modules, allmodules] = await Promise.all([
        fetchConfig(this.hass),
        fetchZones(this.hass),
        fetchModules(this.hass),
        fetchAllModules(this.hass),
      ]);

      this.config = config;
      this.zones = zones;
      this.modules = modules;
      this.allmodules = allmodules;
      this._initialLoadDone = true;

      this.moduleCache.clear();
    } catch (error) {
      console.error("Error fetching data:", error);
      showErrorToast(this, this.hass, "common.errors.load_failed", error);
    } finally {
      if (isInitial) this.isLoading = false;
      this._scheduleUpdate();
    }
  }

  // Debounced save operation for better performance
  private debouncedSave = (() => {
    let timeoutId: number | null = null;
    return (module: SmartIrrigationModule) => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = window.setTimeout(() => {
        this.saveToHA(module);
        timeoutId = null;
      }, 500); // 500ms debounce
    };
  })();

  private async handleAddModule(): Promise<void> {
    if (!this.moduleInput?.selectedOptions?.[0] || this.isSaving) {
      return;
    }

    this.isSaving = true;
    this._scheduleUpdate();

    try {
      const selectedText = this.moduleInput.selectedOptions[0].text;
      const m = this.allmodules.find((o) => o.name === selectedText);

      if (!m) {
        return;
      }

      const newModule: SmartIrrigationModule = {
        name: selectedText,
        description: m.description,
        config: m.config,
        schema: m.schema,
      };

      // Optimistic update
      this.modules = [...this.modules, newModule];
      this.moduleCache.clear(); // Clear cache when modules change
      this._scheduleUpdate();

      // Save to backend
      await this.saveToHA(newModule);

      // Refresh data to get the new module with ID
      await this._fetchData();
    } catch (error) {
      console.error("Error adding module:", error);
      // Rollback optimistic update on error
      await this._fetchData();
    } finally {
      this.isSaving = false;
      this._scheduleUpdate();
    }
  }

  private async handleRemoveModule(ev: Event, index: number): Promise<void> {
    if (this.isSaving) {
      return;
    }

    this.isSaving = true;
    this._scheduleUpdate();

    try {
      const moduleToRemove = this.modules[index];
      const moduleid = moduleToRemove?.id;

      // Optimistic update
      const originalModules = this.modules;
      this.modules = this.modules.filter((_, i) => i !== index);
      this.moduleCache.clear(); // Clear cache when modules change
      this._scheduleUpdate();

      if (this.hass && moduleid !== undefined) {
        await deleteModule(this.hass, moduleid.toString());
      } else {
        // If no ID, just remove from local state (not saved yet)
      }
    } catch (error) {
      console.error("Error removing module:", error);
      showErrorToast(this, this.hass, "common.errors.delete_failed", error);
      // Rollback optimistic update on error
      await this._fetchData();
    } finally {
      this.isSaving = false;
      this._scheduleUpdate();
    }
  }

  private async saveToHA(module: SmartIrrigationModule): Promise<void> {
    if (!this.hass) {
      return;
    }

    try {
      await saveModule(this.hass, module);
      // Data will be updated via WebSocket subscription
    } catch (error) {
      console.error("Error saving module:", error);
      showErrorToast(this, this.hass, "common.errors.save_failed", error);
      throw error; // Re-throw to handle in calling function
    }
  }
  private renderModule(
    module: SmartIrrigationModule,
    index: number,
  ): TemplateResult {
    if (!this.hass) {
      return html``;
    }

    const numberofzonesusingthismodule = this.zones.filter(
      (o) => o.module === module.id,
    ).length;

    // Use cache for better performance (usage count affects the header chip)
    const cacheKey = `module-${module.id || index}-${numberofzonesusingthismodule}-${JSON.stringify(module)}`;
    if (this.moduleCache.has(cacheKey)) {
      return this.moduleCache.get(cacheKey)!;
    }

    const result = html`
      <ha-card>
        <div class="card-header">
          <div class="name">${module.name}</div>
          ${this.renderUsageChip(numberofzonesusingthismodule)}
        </div>
        <div class="card-content">
          <div class="item-description">${module.description}</div>
          <div class="moduleconfig">
            <label class="subheader"
              >${localize(
                "panels.modules.cards.module.labels.configuration",
                this.hass.language,
              )}
              (*
              ${localize(
                "panels.modules.cards.module.labels.required",
                this.hass.language,
              )})</label
            >
            ${module.schema
              ? Object.entries(module.schema).map(([value]) =>
                  this.renderConfig(index, value),
                )
              : null}
          </div>
          <div class="card-footer">
            ${numberofzonesusingthismodule
              ? html`<div class="weather-note">
                  ${localize(
                    "panels.modules.cards.module.errors.cannot-delete-module-because-zones-use-it",
                    this.hass.language,
                  )}
                </div>`
              : html`<button
                  class="action-btn danger"
                  @click="${(e: Event) => this.handleRemoveModule(e, index)}"
                >
                  <ha-icon icon="mdi:delete"></ha-icon>
                  ${localize("common.actions.delete", this.hass.language)}
                </button>`}
          </div>
        </div>
      </ha-card>
    `;

    this.moduleCache.set(cacheKey, result);
    return result;
  }

  private renderUsageChip(count: number): TemplateResult {
    if (!this.hass) return html``;
    return count
      ? html`<span class="usage-chip"
          >${localize(
            "panels.setup.advanced.used_by_zones",
            this.hass.language,
            "{count}",
            count,
          )}</span
        >`
      : html`<span class="usage-chip unused"
          >${localize(
            "panels.setup.advanced.not_used",
            this.hass.language,
          )}</span
        >`;
  }

  /*
  : html`<div class="schemaline">
                    <input
                      id="moduleconfigInput${index}"
                      type="text"
                      .value=${JSON.stringify(module.config)}
                    />
                  </div>`
                  */
  renderConfig(index: number, value: string): any {
    const mod = Object.values(this.modules).at(index);
    if (!mod || !this.hass) {
      return;
    }
    //loop over items in schema and output the right UI
    const schemaline = mod.schema[value];
    const name = schemaline["name"];
    // Safe localize lookup: returns undefined for missing keys so we can fall
    // back to the prettified key / backend-provided string.
    const tr = (key: string): string | undefined => {
      try {
        const v = localize(key, this.hass!.language);
        return v === undefined || v === null ? undefined : v;
      } catch {
        return undefined;
      }
    };
    const fieldKey = "panels.modules.cards.module.fields." + name;
    const prettyName = tr(fieldKey + ".name") ?? prettyPrint(name);
    const fieldDescription =
      tr(fieldKey + ".description") ?? schemaline["description"];
    let val = "";
    if (mod.config == null) {
      mod.config = [];
    }
    if (name in mod.config) {
      val = mod.config[name];
    }
    let control = html``;
    if (schemaline["type"] == "boolean") {
      control = html`<input
        type="checkbox"
        id="${name + index}"
        .checked=${val}
        @input="${(e: Event) =>
          this.handleEditConfig(index, {
            ...mod,
            config: {
              ...mod.config,
              [name]: (e.target as HTMLInputElement).checked,
            },
          })}"
      />`;
    } else if (
      schemaline["type"] == "float" ||
      schemaline["type"] == "integer"
    ) {
      control = html`<input
        type="number"
        class="settings-input shortfield"
        id="${schemaline["name"] + index}"
        .value="${mod.config[schemaline["name"]]}"
        @input="${(e: Event) =>
          this.handleEditConfig(index, {
            ...mod,
            config: {
              ...mod.config,
              [name]: (e.target as HTMLInputElement).value,
            },
          })}"
      />`;
    } else if (schemaline["type"] == "string") {
      control = html`<input
        type="text"
        class="settings-input"
        id="${name + index}"
        .value="${val}"
        @input="${(e: Event) =>
          this.handleEditConfig(index, {
            ...mod,
            config: {
              ...mod.config,
              [name]: (e.target as HTMLInputElement).value,
            },
          })}"
      />`;
    } else if (schemaline["type"] == "select") {
      const hasslanguage = this.hass.language;
      //@change
      control = html`<select
        class="settings-input"
        id="${name + index}"
        .value="${live(val)}"
        @change="${(e: Event) =>
          this.handleEditConfig(index, {
            ...mod,
            config: {
              ...mod.config,
              [name]: (e.target as HTMLSelectElement).value,
            },
          })}"
      >
        ${Object.entries(schemaline["options"]).map(
          ([key, value]) =>
            html`<option
              value="${getPart(value, 0)}"
              ?selected="${val === getPart(value, 0)}"
            >
              ${localize(
                "panels.modules.cards.module.translated-options." +
                  getPart(value, 1),
                hasslanguage,
              )}
            </option>`,
        )}
      </select>`;
    }

    return html`<ha-settings-row>
      <span slot="heading"
        >${prettyName}${schemaline["required"] ? " *" : ""}</span
      >
      ${fieldDescription
        ? html`<span slot="description">${fieldDescription}</span>`
        : ""}
      ${control}
    </ha-settings-row>`;
  }

  handleEditConfig(index: number, updatedModule: SmartIrrigationModule) {
    // Optimistic update for responsive UI
    this.modules = Object.values(this.modules).map((module, i) =>
      i === index ? updatedModule : module,
    );

    // Clear cache for this module
    this.moduleCache.clear();
    this._scheduleUpdate();

    // Debounced save to reduce backend calls
    this.debouncedSave(updatedModule);
  }

  render(): TemplateResult {
    if (!this.hass) {
      return html``;
    }

    return html`
      <ha-card header="${localize("panels.modules.title", this.hass.language)}">
        <div class="card-content">
          ${localize("panels.modules.description", this.hass.language)}
          ${this.isLoading
            ? html`<div class="loading-indicator">
                ${localize(
                  "common.loading-messages.general",
                  this.hass.language,
                )}
              </div>`
            : html`
                <div class="add-row">
                  <select
                    id="moduleInput"
                    class="settings-input"
                    aria-label="${localize(
                      "common.labels.module",
                      this.hass.language,
                    )}"
                    ?disabled="${this.isSaving}"
                  >
                    ${Object.entries(this.allmodules).map(
                      ([key, value]) =>
                        html`<option value="${value.id}">
                          ${value.name}
                        </option>`,
                    )}
                  </select>
                  <button
                    @click="${this.handleAddModule}"
                    ?disabled="${this.isSaving}"
                    class="action-btn ${this.isSaving ? "saving" : ""}"
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                    ${this.isSaving
                      ? localize(
                          "common.saving-messages.adding",
                          this.hass.language,
                        )
                      : localize(
                          "panels.modules.cards.add-module.actions.add",
                          this.hass.language,
                        )}
                  </button>
                </div>
              `}
        </div>
      </ha-card>

      ${this.isLoading
        ? html``
        : Object.entries(this.modules).map(([key, value]) =>
            this.renderModule(value, parseInt(key)),
          )}
    `;
  }

  disconnectedCallback() {
    super.disconnectedCallback();

    // Clean up timers and caches
    if (this.globalDebounceTimer) {
      clearTimeout(this.globalDebounceTimer);
      this.globalDebounceTimer = null;
    }

    this.moduleCache.clear();
  }

  /*
   ${Object.entries(this.modules).map(([key, value]) =>
          this.renderModule(value, value["id"])
        )}
        */

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      .field-hint {
        font-size: 0.8rem;
        color: var(--secondary-text-color);
        line-height: 1.4;
        margin-top: 3px;
        padding-left: 2px;
      }
    `;
  }
}
