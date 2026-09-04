import { TemplateResult, LitElement, html, CSSResultGroup, css } from "lit";
import { live } from "lit/directives/live.js";
import { property, state, customElement } from "lit/decorators.js";
import { HomeAssistant } from "../../types";
import { loadHaForm } from "../../load-ha-elements";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { mdiPlus } from "@mdi/js";
import {
  fetchConfig,
  fetchZones,
  fetchDistributors,
  saveZone,
  saveDistributor,
  deleteDistributor,
  distributorTestRun,
  distributorSetOutlet,
  distributorResyncHome,
  distributorRunNow,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";
import {
  SmartIrrigationConfig,
  SmartIrrigationDistributor,
  SmartIrrigationZone,
} from "../../types";
import { showErrorToast } from "../../helpers";
import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import { Path } from "../../common/navigation";
import {
  DOMAIN,
  POSITION_STATE_SYNCED,
  DISTRIBUTOR_MIN_OUTLETS,
  DISTRIBUTOR_MAX_OUTLETS,
  DISTRIBUTOR_COMMISSIONING_CONFIRMED,
  ZONE_DISTRIBUTOR_ID,
  ZONE_OUTLET_NUMBER,
  CONF_ZONE_SEQUENCING_PARALLEL,
  CONF_ZONE_SEQUENCING_SEQUENTIAL,
  CONF_ZONE_SEQUENCING_ROTATING,
} from "../../const";
import "../../components/si-field";
import "../../components/si-distributor-form";

/**
 * Setup → Distributors: configure Gardena-style water distributors and walk the
 * commissioning flow. Mirrors the zone-settings view (collapsible cards, add
 * dialog, delete-confirm, 500 ms debounced auto-save) so it blends into the
 * existing look (spec §8).
 *
 * Config edits POST only the config subset (name…use_master); the runtime
 * fields (position_state, current_outlet, commissioning_confirmed, active_cycle)
 * are backend-owned and changed only by the operation services / the arm
 * switch, so a debounced config save can never clobber a mid-commissioning
 * position update. The backend update is an attr.evolve merge, so a partial
 * POST is safe.
 */
@customElement("smart-irrigation-view-distributor-settings")
class SmartIrrigationViewDistributorSettings extends SubscribeMixin(
  LitElement,
) {
  hass?: HomeAssistant;
  @property() config?: SmartIrrigationConfig;
  @property({ attribute: false }) public path?: Path;

  @property({ type: Array })
  private distributors: SmartIrrigationDistributor[] = [];
  @property({ type: Array })
  private zones: SmartIrrigationZone[] = [];

  @property({ type: Boolean })
  private isLoading = true;
  @property({ type: Boolean })
  private isSaving = false;

  private _initialLoadDone = false;
  // Distributor id a deep link (from a zone's "configure on distributor") has
  // already expanded + scrolled to, so it happens once.
  private _scrolledToDist: number | null = null;

  // Distributor ids whose card is expanded (default all collapsed).
  @state() private _expanded = new Set<number>();

  @property({ type: Boolean })
  private _showAdd = false;
  @property()
  private _newName = "";

  @property()
  private _confirmDeleteId: number | null = null;

  // Distributor id whose arm switch was just turned on, awaiting the popup.
  @state() private _armConfirmId: number | null = null;

  // Distributor id awaiting the "reset to outlet 1" safety confirmation — a
  // one-click resync to 1 that falsely marks synced if the device isn't
  // physically at outlet 1, so it must be confirmed.
  @state() private _confirmResyncHomeId: number | null = null;

  // Distributor id awaiting the "set current outlet" safety confirmation — a
  // stray click writes position_state=synced at the entered outlet, so if the
  // device's window isn't physically at that outlet it silently waters the
  // wrong outlets; mirrors the resync-home confirm (b18).
  @state() private _confirmSetOutletId: number | null = null;

  // Per-card "set current outlet" draft value.
  @state() private _outletDraft: Record<number, number> = {};

  // Per-card visible outlet-slot count (>= assigned; user can grow/shrink it).
  @state() private _outletRows: Record<number, number> = {};

  // Debounced auto-save feedback (mirrors zone settings).
  @state() private _saveStatus: "idle" | "saving" | "saved" = "idle";
  private _savedResetTimer: number | null = null;
  private globalDebounceTimer: number | null = null;

  private _updateScheduled = false;
  private _scheduleUpdate() {
    if (this._updateScheduled) return;
    this._updateScheduled = true;
    requestAnimationFrame(() => {
      this._updateScheduled = false;
      this.requestUpdate();
    });
  }

  private _isExpanded(d: SmartIrrigationDistributor): boolean {
    return d.id !== undefined && this._expanded.has(d.id);
  }

  private _toggle(id: number): void {
    const next = new Set(this._expanded);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    this._expanded = next;
  }

  firstUpdated() {
    loadHaForm()
      .then(() => this._scheduleUpdate())
      .catch((error) => {
        console.error("Failed to load HA form:", error);
        this._scheduleUpdate();
      });
  }

  updated() {
    // Deep link from a zone's "configure on distributor" button: expand the
    // targeted distributor and scroll to it, once (mirrors the zone view).
    const target = this.path?.params?.distributor;
    if (target == null || target === "" || this.isLoading) return;
    const id = Number(target);
    if (Number.isNaN(id) || this._scrolledToDist === id) return;
    if (!this._expanded.has(id)) {
      this._expanded = new Set(this._expanded).add(id);
      return;
    }
    const el = this.shadowRoot?.querySelector(`#distributor-${id}`);
    if (el) {
      this._scrolledToDist = id;
      requestAnimationFrame(() =>
        el.scrollIntoView({ behavior: "smooth", block: "start" }),
      );
    }
  }

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._fetchData().catch((error) => {
      console.error("Failed to fetch initial distributor data:", error);
    });

    return [
      this.hass!.connection.subscribeMessage(
        () => {
          this._fetchData().catch((error) => {
            console.error("Failed to refetch on config update:", error);
          });
        },
        { type: DOMAIN + "_config_updated" },
      ),
    ];
  }

  private async _fetchData(): Promise<void> {
    if (!this.hass) return;
    const isInitial = !this._initialLoadDone;
    try {
      if (isInitial) this.isLoading = true;
      const [config, distributors, zones] = await Promise.all([
        fetchConfig(this.hass),
        fetchDistributors(this.hass),
        fetchZones(this.hass),
      ]);
      this.config = config;
      this.distributors = distributors;
      this.zones = zones;
      this._initialLoadDone = true;
    } catch (error) {
      console.error("Error fetching distributor data:", error);
      showErrorToast(this, this.hass, "common.errors.load_failed", error);
    } finally {
      if (isInitial) this.isLoading = false;
      this._scheduleUpdate();
    }
  }

  // --- create / edit / delete ---------------------------------------------

  private handleAdd(): void {
    if (!this.hass || !this._newName.trim()) return;
    this.isSaving = true;
    this._showAdd = false;
    // The backend fills every other field from DistributorEntry defaults.
    saveDistributor(this.hass, { name: this._newName.trim() })
      .then(() => {
        this._newName = "";
        return this._fetchData();
      })
      .catch((error) => {
        console.error("Failed to add distributor:", error);
        showErrorToast(this, this.hass, "common.errors.save_failed", error);
      })
      .finally(() => {
        this.isSaving = false;
        this._scheduleUpdate();
      });
  }

  /** Only the user-editable config fields — never the backend runtime state. */
  private _configPayload(
    d: SmartIrrigationDistributor,
  ): Partial<SmartIrrigationDistributor> {
    return {
      id: d.id,
      name: d.name,
      watering_mode: d.watering_mode,
      inlet_entity: d.inlet_entity ?? null,
      // E4 (2026-07-07): persist the tri-state inlet-watch reaction (default
      // "ignore" = no listener). Replaces the legacy watch_inlet bool; the
      // backend still derives watch_mode from watch_inlet for older records.
      watch_mode: d.watch_mode ?? "ignore",
      run_service: d.run_service ?? null,
      stop_service: d.stop_service ?? null,
      duration_field: d.duration_field,
      duration_unit: d.duration_unit,
      confirm_entity: d.confirm_entity ?? null,
      flow_sensor: d.flow_sensor ?? null,
      pause_seconds: d.pause_seconds,
      skip_pulse_seconds: d.skip_pulse_seconds,
      notify_target: d.notify_target ?? null,
      use_master: d.use_master,
    };
  }

  private handleEditDistributor(
    index: number,
    updated: SmartIrrigationDistributor,
  ): void {
    if (!this.hass) return;
    this.distributors = this.distributors.map((d, i) =>
      i === index ? updated : d,
    );

    if (this.globalDebounceTimer) clearTimeout(this.globalDebounceTimer);
    this.globalDebounceTimer = window.setTimeout(() => {
      this.isSaving = true;
      this._saveStatus = "saving";
      saveDistributor(this.hass!, this._configPayload(updated))
        .then(() => this._markSaved())
        .catch((error) => {
          console.error("Failed to save distributor:", error);
          this._saveStatus = "idle";
          showErrorToast(this, this.hass, "common.errors.save_failed", error);
        })
        .finally(() => {
          this.isSaving = false;
          this._scheduleUpdate();
        });
      this.globalDebounceTimer = null;
    }, 500);
    this._scheduleUpdate();
  }

  private _confirmDelete(): void {
    const id = this._confirmDeleteId;
    if (id === null || !this.hass) return;
    const original = [...this.distributors];
    this.distributors = this.distributors.filter((d) => d.id !== id);
    this._confirmDeleteId = null;
    this.isSaving = true;
    deleteDistributor(this.hass, id)
      .catch((error) => {
        console.error("Failed to delete distributor:", error);
        showErrorToast(this, this.hass, "common.errors.delete_failed", error);
        this.distributors = original;
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch(() => undefined);
      });
  }

  // --- commissioning actions ----------------------------------------------

  private _callAction(action: Promise<any>): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    action
      .catch((error) => {
        console.error("Distributor action failed:", error);
        showErrorToast(this, this.hass, "common.errors.action_failed", error);
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch(() => undefined);
      });
  }

  private _testRun(id: number): void {
    this._callAction(distributorTestRun(this.hass!, id));
  }

  private _setOutlet(id: number, currentOutlet: number): void {
    const outlet = this._outletDraft[id] ?? currentOutlet;
    this._callAction(distributorSetOutlet(this.hass!, id, outlet));
  }

  /** Set-current-outlet goes through a confirm popup (mirrors resync-home): a
   * stray click would falsely mark the blind distributor synced at the entered
   * outlet, silently watering the wrong outlets. The draft value still wins
   * inside _setOutlet; current_outlet is only the fallback. */
  private _confirmSetOutlet(): void {
    const id = this._confirmSetOutletId;
    this._confirmSetOutletId = null;
    if (id === null) return;
    const d = this.distributors.find((dist) => dist.id === id);
    if (d) this._setOutlet(id, d.current_outlet);
  }

  private _resyncHome(id: number): void {
    this._callAction(distributorResyncHome(this.hass!, id));
  }

  /** Reset-to-1 goes through a confirm popup (mirrors the arm popup): a stray
   * click would falsely mark the distributor synced at outlet 1. */
  private _confirmResyncHome(): void {
    const id = this._confirmResyncHomeId;
    this._confirmResyncHomeId = null;
    if (id !== null) this._resyncHome(id);
  }

  private _runNow(id: number): void {
    this._callAction(distributorRunNow(this.hass!, id));
  }

  /** Arm/disarm. Arming goes through the confirm popup; disarming is direct. */
  private _setArmed(id: number, armed: boolean): void {
    if (!this.hass) return;
    this._armConfirmId = null;
    this.distributors = this.distributors.map((d) =>
      d.id === id ? { ...d, commissioning_confirmed: armed } : d,
    );
    this.isSaving = true;
    saveDistributor(this.hass, {
      id,
      [DISTRIBUTOR_COMMISSIONING_CONFIRMED]: armed,
    })
      .catch((error) => {
        console.error("Failed to set commissioning state:", error);
        showErrorToast(this, this.hass, "common.errors.save_failed", error);
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch(() => undefined);
      });
  }

  private _onArmToggle(d: SmartIrrigationDistributor, checked: boolean): void {
    if (d.id === undefined) return;
    if (checked) {
      // Show the confirm popup; the switch reverts if the user cancels.
      this._armConfirmId = d.id;
    } else {
      this._setArmed(d.id, false);
    }
  }

  private _markSaved(): void {
    this._saveStatus = "saved";
    if (this._savedResetTimer) clearTimeout(this._savedResetTimer);
    this._savedResetTimer = window.setTimeout(() => {
      this._saveStatus = "idle";
      this._scheduleUpdate();
    }, 2000);
    this._scheduleUpdate();
  }

  private _renderSaveStatus(): TemplateResult {
    if (!this.hass || this._saveStatus === "idle") return html``;
    const saving = this._saveStatus === "saving";
    return html`
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${saving ? "mdi:content-save-outline" : "mdi:check-circle"}"
        ></ha-icon>
        ${localize(
          saving
            ? "common.saving-messages.saving"
            : "panels.distributors.status.saved",
          this.hass.language,
        )}
      </span>
    `;
  }

  // --- rendering -----------------------------------------------------------

  /**
   * A zone has its own actuation when a linked valve/switch or a run/stop
   * script is configured. Such a zone waters itself, so it must not also be
   * assignable to a distributor outlet (test feedback: either own valve or the
   * distributor, never both).
   */
  private _hasOwnActuation(z: SmartIrrigationZone): boolean {
    return !!(z.linked_entity || z.run_service || z.stop_service);
  }

  /** outlet number -> the member zone assigned to it, for this distributor. */
  private _membersByOutlet(
    distributorId?: number,
  ): Map<number, SmartIrrigationZone> {
    const map = new Map<number, SmartIrrigationZone>();
    if (distributorId === undefined) return map;
    for (const z of this.zones) {
      if (
        z.distributor_id === distributorId &&
        z.outlet_number != null &&
        z.id !== undefined
      ) {
        map.set(z.outlet_number, z);
      }
    }
    return map;
  }

  /**
   * Visible number of outlet slots for a distributor. The backend has no stored
   * outlet count — n is simply the number of assigned member zones — so this is
   * max(2, highest assigned outlet) with the user's UI choice layered on top,
   * capped at the physical max (6).
   */
  private _outletCount(d: SmartIrrigationDistributor): number {
    const members = this._membersByOutlet(d.id);
    const maxAssigned = members.size ? Math.max(...members.keys()) : 0;
    const base = Math.max(DISTRIBUTOR_MIN_OUTLETS, maxAssigned);
    const ui = d.id !== undefined ? this._outletRows[d.id] : undefined;
    return Math.min(DISTRIBUTOR_MAX_OUTLETS, Math.max(base, ui ?? base));
  }

  /** POST a zone's distributor membership (partial update; backend merges). */
  private _assignZone(
    zone: SmartIrrigationZone,
    distributorId: number | null,
    outlet: number | null,
  ): Promise<boolean> {
    return saveZone(this.hass!, {
      id: zone.id,
      [ZONE_DISTRIBUTOR_ID]: distributorId,
      [ZONE_OUTLET_NUMBER]: outlet,
    });
  }

  /**
   * Optimistically reflect a membership change in the local zone list so the
   * zone disappears from the other outlet pickers immediately, before the save
   * + refetch round-trip (test feedback: a zone assigned to one outlet must not
   * stay selectable on another). The refetch in _runAssign reconciles, and
   * reverts on error.
   */
  private _optimisticZone(
    zoneId: number | undefined,
    distributorId: number | null,
    outlet: number | null,
  ): void {
    if (zoneId === undefined) return;
    this.zones = this.zones.map((z) =>
      z.id === zoneId
        ? { ...z, distributor_id: distributorId, outlet_number: outlet }
        : z,
    );
  }

  private _runAssign(ops: Promise<unknown>[]): void {
    if (!ops.length) return;
    this.isSaving = true;
    this._saveStatus = "saving";
    this._scheduleUpdate();
    Promise.all(ops)
      .then(() => this._markSaved())
      .catch((error) => {
        console.error("Failed to assign zone to outlet:", error);
        this._saveStatus = "idle";
        showErrorToast(this, this.hass, "common.errors.save_failed", error);
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch(() => undefined);
      });
  }

  private _setOutletCount(d: SmartIrrigationDistributor, count: number): void {
    if (d.id === undefined) return;
    // Shrinking below an assigned outlet unassigns those zones (keep 1..n).
    const members = this._membersByOutlet(d.id);
    const toClear: SmartIrrigationZone[] = [];
    for (const [outlet, zone] of members)
      if (outlet > count) toClear.push(zone);
    this._outletRows = { ...this._outletRows, [d.id]: count };
    if (toClear.length) {
      toClear.forEach((z) => this._optimisticZone(z.id, null, null));
      this._runAssign(toClear.map((z) => this._assignZone(z, null, null)));
    } else {
      this._scheduleUpdate();
    }
  }

  private _onOutletZoneChange(
    d: SmartIrrigationDistributor,
    outlet: number,
    e: Event,
  ): void {
    const val = (e.target as HTMLSelectElement).value;
    const newId = val ? parseInt(val) : null;
    const prev = this._membersByOutlet(d.id).get(outlet);
    const z = newId !== null ? this.zones.find((zn) => zn.id === newId) : null;
    const ops: Promise<unknown>[] = [];
    if (prev && prev.id !== newId) {
      ops.push(this._assignZone(prev, null, null));
      this._optimisticZone(prev.id, null, null);
    }
    if (z) {
      ops.push(this._assignZone(z, d.id!, outlet));
      this._optimisticZone(z.id, d.id!, outlet);
    }
    this._runAssign(ops);
  }

  /**
   * Distributor-side outlet -> zone mapping (test feedback FB5). The backend
   * derives the ring size from the member zones, so "how many outlets" is set
   * by assigning that many zones here, contiguously from 1.
   */
  private _renderOutletConfig(d: SmartIrrigationDistributor): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;
    const members = this._membersByOutlet(d.id);
    const count = this._outletCount(d);
    // Zones assignable to an outlet: not yet on a distributor AND without their
    // own valve/service (a zone is either on a distributor or has its own valve,
    // never both), plus the one already on this outlet (so it stays selected).
    const unassigned = this.zones.filter(
      (z) =>
        z.id !== undefined &&
        z.distributor_id == null &&
        !this._hasOwnActuation(z),
    );

    // Contiguity check: assigned outlets should be exactly 1..m with no gap.
    const assigned = [...members.keys()].sort((a, b) => a - b);
    const hasGap = assigned.some((n, i) => n !== i + 1);

    const rows: TemplateResult[] = [];
    for (let i = 1; i <= count; i++) {
      const cur = members.get(i);
      const options = cur ? [...unassigned, cur] : [...unassigned];
      options.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
      rows.push(html`
        <div class="outlet-row">
          <span class="outlet-label"
            >${localize("panels.distributors.commissioning.outlet", lang)}
            ${i}</span
          >
          <select
            class="settings-input"
            .value="${live(cur?.id != null ? String(cur.id) : "")}"
            @change="${(e: Event) => this._onOutletZoneChange(d, i, e)}"
            ?disabled="${this.isSaving}"
          >
            <option value="" ?selected="${!cur}">
              ${localize("panels.distributors.outlets.none", lang)}
            </option>
            ${options.map(
              (z) => html`
                <option value="${z.id}" ?selected="${cur?.id === z.id}">
                  ${z.name}
                </option>
              `,
            )}
          </select>
        </div>
      `);
    }

    return html`
      <div class="outlet-config">
        <div class="commissioning-head">
          <span class="section-title"
            >${localize("panels.distributors.outlets.title", lang)}</span
          >
        </div>
        <div class="item-description">
          ${localize("panels.distributors.outlets.help", lang)}
        </div>
        ${this.zones.length === 0
          ? html`<div class="weather-note">
              ${localize("panels.distributors.outlets.no_zones", lang)}
            </div>`
          : html`
              <ha-settings-row>
                <span slot="heading"
                  >${localize("panels.distributors.outlets.count", lang)}</span
                >
                <select
                  class="settings-input shortfield"
                  .value="${live(String(count))}"
                  @change="${(e: Event) =>
                    this._setOutletCount(
                      d,
                      parseInt((e.target as HTMLSelectElement).value),
                    )}"
                  ?disabled="${this.isSaving}"
                >
                  ${Array.from(
                    {
                      length:
                        DISTRIBUTOR_MAX_OUTLETS - DISTRIBUTOR_MIN_OUTLETS + 1,
                    },
                    (_, k) => DISTRIBUTOR_MIN_OUTLETS + k,
                  ).map(
                    (n) =>
                      html`<option value="${n}" ?selected="${n === count}">
                        ${n}
                      </option>`,
                  )}
                </select>
              </ha-settings-row>
              <div class="outlet-rows">${rows}</div>
              ${hasGap
                ? html`<div class="timing-warning">
                    ${localize("panels.distributors.outlets.gap_warning", lang)}
                  </div>`
                : ""}
              <div class="commissioning-note">
                ${localize("panels.distributors.hints.outlet_change", lang)}
              </div>
            `}
      </div>
    `;
  }

  /**
   * Instance-level safety advisories (spec §8). Pressure/flow is always shown;
   * the sequencing notes are gated on the instance's zone-sequencing / master
   * settings because they only apply then.
   */
  private _renderAdvisories(): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;
    const seq = this.config?.zone_sequencing;
    const parallel = seq === CONF_ZONE_SEQUENCING_PARALLEL;
    const seqRotating =
      seq === CONF_ZONE_SEQUENCING_SEQUENTIAL ||
      seq === CONF_ZONE_SEQUENCING_ROTATING;
    const masterOffAfter = !!this.config?.master_off_after;
    return html`
      <div class="advisories">
        <div class="advisory">
          <ha-icon icon="mdi:flask-outline"></ha-icon>
          <span
            >${localize("panels.distributors.hints.experimental", lang)}</span
          >
        </div>
        <div class="advisory">
          <ha-icon icon="mdi:water-alert-outline"></ha-icon>
          <span>${localize("panels.distributors.hints.pressure", lang)}</span>
        </div>
        ${parallel
          ? html`<div class="advisory">
              <ha-icon icon="mdi:information-outline"></ha-icon>
              <span
                >${localize(
                  "panels.distributors.hints.parallel_draw",
                  lang,
                )}</span
              >
            </div>`
          : ""}
        ${seqRotating && masterOffAfter
          ? html`<div class="advisory">
              <ha-icon icon="mdi:information-outline"></ha-icon>
              <span
                >${localize(
                  "panels.distributors.hints.master_off_after",
                  lang,
                )}</span
              >
            </div>`
          : ""}
      </div>
    `;
  }

  private _renderCommissioning(d: SmartIrrigationDistributor): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;
    const synced = d.position_state === POSITION_STATE_SYNCED;
    const confirmed = !!d.commissioning_confirmed;
    const cycleActive =
      !!d.active_cycle && Object.keys(d.active_cycle).length > 0;
    const id = d.id!;

    return html`
      <div class="commissioning">
        <div class="commissioning-head">
          <span class="section-title"
            >${localize("panels.distributors.commissioning.title", lang)}</span
          >
          <span class="pos-badge pos-${d.position_state}">
            ${localize("panels.distributors.commissioning.outlet", lang)}
            ${d.current_outlet} ·
            ${localize(
              `panels.distributors.commissioning.states.${d.position_state}`,
              lang,
            )}
          </span>
        </div>

        <!-- Re-sync controls -->
        <ha-settings-row>
          <span slot="heading"
            >${localize(
              "panels.distributors.commissioning.set_outlet",
              lang,
            )}</span
          >
          <span slot="description"
            >${localize(
              "panels.distributors.commissioning.set_outlet_help",
              lang,
            )}</span
          >
          <div class="inline-controls">
            <input
              type="number"
              class="settings-input shortfield"
              min="1"
              max="${DISTRIBUTOR_MAX_OUTLETS}"
              step="1"
              .value="${live(
                String(this._outletDraft[id] ?? d.current_outlet),
              )}"
              @input="${(e: Event) => {
                const v = (e.target as HTMLInputElement).valueAsNumber;
                if (!isNaN(v))
                  this._outletDraft = { ...this._outletDraft, [id]: v };
              }}"
            />
            <button
              class="action-btn secondary"
              ?disabled="${this.isSaving}"
              @click="${() => {
                this._confirmSetOutletId = id;
              }}"
            >
              ${localize("panels.distributors.commissioning.set_outlet", lang)}
            </button>
            <button
              class="action-btn secondary"
              ?disabled="${this.isSaving}"
              @click="${() => {
                this._confirmResyncHomeId = id;
              }}"
            >
              ${localize("panels.distributors.commissioning.resync_home", lang)}
            </button>
          </div>
        </ha-settings-row>
        <div class="commissioning-note">
          ${localize("panels.distributors.hints.undetectable", lang)}
        </div>

        <!-- Test run -->
        <ha-settings-row>
          <span slot="heading"
            >${localize(
              "panels.distributors.commissioning.test_run",
              lang,
            )}</span
          >
          <span slot="description"
            >${localize(
              "panels.distributors.commissioning.test_run_help",
              lang,
            )}</span
          >
          <button
            class="action-btn secondary"
            ?disabled="${this.isSaving || !synced}"
            @click="${() => this._testRun(id)}"
          >
            <ha-icon icon="mdi:play-circle-outline"></ha-icon>
            ${localize("panels.distributors.commissioning.test_run", lang)}
          </button>
        </ha-settings-row>

        <!-- Arm switch -->
        <ha-settings-row>
          <span slot="heading"
            >${localize(
              "panels.distributors.commissioning.confirmed",
              lang,
            )}</span
          >
          <span slot="description"
            >${synced
              ? localize(
                  "panels.distributors.commissioning.confirmed_help",
                  lang,
                )
              : localize(
                  "panels.distributors.commissioning.needs_sync",
                  lang,
                )}</span
          >
          <ha-switch
            .checked="${live(confirmed)}"
            .disabled="${this.isSaving || (!synced && !confirmed)}"
            @change="${(e: Event) =>
              this._onArmToggle(d, (e.target as HTMLInputElement).checked)}"
          ></ha-switch>
        </ha-settings-row>

        <!-- Run now -->
        <div class="run-now-row">
          <button
            class="action-btn"
            ?disabled="${this.isSaving || !synced || !confirmed || cycleActive}"
            @click="${() => this._runNow(id)}"
          >
            <ha-icon icon="mdi:play"></ha-icon>
            ${localize("panels.distributors.commissioning.run_now", lang)}
          </button>
          <span class="run-now-hint">
            ${cycleActive
              ? localize(
                  "panels.distributors.commissioning.run_now_active",
                  lang,
                )
              : localize(
                  "panels.distributors.commissioning.run_now_help",
                  lang,
                )}
          </span>
        </div>
      </div>
    `;
  }

  private renderDistributor(
    d: SmartIrrigationDistributor,
    index: number,
  ): TemplateResult {
    if (!this.hass) return html``;
    const expanded = this._isExpanded(d);
    const lang = this.hass.language;

    return html`
      <ha-card id="distributor-${d.id ?? "new"}">
        <div
          class="card-header dist-toggle"
          role="button"
          tabindex="0"
          aria-expanded="${expanded ? "true" : "false"}"
          @click="${() => d.id !== undefined && this._toggle(d.id)}"
          @keydown="${(e: KeyboardEvent) => {
            if ((e.key === "Enter" || e.key === " ") && d.id !== undefined) {
              e.preventDefault();
              this._toggle(d.id);
            }
          }}"
        >
          <div class="name">${d.name}</div>
          <span class="pos-badge pos-${d.position_state}">
            ${localize(
              `panels.distributors.commissioning.states.${d.position_state}`,
              lang,
            )}
          </span>
          <ha-icon
            class="dist-chevron"
            icon="${expanded ? "mdi:chevron-up" : "mdi:chevron-down"}"
          ></ha-icon>
        </div>
        ${expanded
          ? html`
              <div class="card-content">
                <si-distributor-form
                  .hass="${this.hass}"
                  .distributor="${d}"
                  @distributor-changed="${(e: CustomEvent) =>
                    this.handleEditDistributor(index, e.detail.value)}"
                ></si-distributor-form>

                ${this._renderOutletConfig(d)} ${this._renderCommissioning(d)}

                <div class="settings-danger-row">
                  <button
                    class="action-btn danger"
                    ?disabled="${this.isSaving || d.id === undefined}"
                    @click="${() => {
                      this._confirmDeleteId = d.id ?? null;
                    }}"
                  >
                    <ha-icon icon="mdi:delete"></ha-icon>
                    ${localize("common.actions.delete", lang)}
                  </button>
                </div>
              </div>
            `
          : ""}
      </ha-card>
    `;
  }

  render(): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;

    if (this.isLoading) {
      return html`
        <ha-card header="${localize("panels.distributors.title", lang)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${localize("common.loading-messages.general", lang)}
            </div>
          </div>
        </ha-card>
      `;
    }

    const confirmDist =
      this._confirmDeleteId !== null
        ? this.distributors.find((d) => d.id === this._confirmDeleteId)
        : null;
    const armDist =
      this._armConfirmId !== null
        ? this.distributors.find((d) => d.id === this._armConfirmId)
        : null;
    const resyncDist =
      this._confirmResyncHomeId !== null
        ? this.distributors.find((d) => d.id === this._confirmResyncHomeId)
        : null;
    const setOutletDist =
      this._confirmSetOutletId !== null
        ? this.distributors.find((d) => d.id === this._confirmSetOutletId)
        : null;
    // Target outlet the user is about to mark synced at (draft wins, else the
    // currently tracked outlet) — shown in the confirm body so a wrong value is
    // caught before it silently rewrites the position.
    const setOutletTarget =
      setOutletDist && setOutletDist.id !== undefined
        ? (this._outletDraft[setOutletDist.id] ?? setOutletDist.current_outlet)
        : null;

    return html`
      <ha-card>
        <div class="card-header">
          <div class="name">${localize("panels.distributors.title", lang)}</div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${mdiPlus}"
            title="${localize("panels.distributors.add.header", lang)}"
            @click="${() => {
              this._showAdd = true;
            }}"
          ></ha-icon-button>
        </div>
        <div class="card-content">
          <div class="item-description">
            ${localize("panels.distributors.description", lang)}
          </div>
          ${this._renderAdvisories()}
          ${this.distributors.length === 0
            ? html`<div class="weather-note">
                ${localize("panels.distributors.no_items", lang)}
              </div>`
            : ""}
        </div>
      </ha-card>

      <!-- Add dialog -->
      <ha-dialog
        .open="${this._showAdd}"
        @closed="${() => {
          this._showAdd = false;
        }}"
        heading="${localize("panels.distributors.add.header", lang)}"
      >
        <div class="add-form">
          <si-field
            label="${localize("panels.distributors.labels.name", lang)}"
            required
          >
            <input
              type="text"
              class="settings-input"
              placeholder="${localize(
                "panels.distributors.add.name_placeholder",
                lang,
              )}"
              .value="${this._newName}"
              @input="${(e: Event) => {
                this._newName = (e.target as HTMLInputElement).value;
              }}"
            />
          </si-field>
        </div>
        <div class="dialog-footer">
          <button
            class="dialog-btn"
            @click="${() => {
              this._showAdd = false;
            }}"
          >
            ${localize("common.actions.cancel", lang)}
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            ?disabled="${!this._newName.trim() || this.isSaving}"
            @click="${this.handleAdd}"
          >
            ${this.isSaving
              ? localize("common.saving-messages.adding", lang)
              : localize("panels.distributors.add.actions.add", lang)}
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirm -->
      ${confirmDist
        ? html`
            <ha-dialog
              open
              @closed="${() => {
                this._confirmDeleteId = null;
              }}"
              heading="${localize("common.actions.confirm_delete", lang)}"
            >
              <p>${localize("panels.distributors.confirm_delete", lang)}</p>
              <p><strong>${confirmDist.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
                    this._confirmDeleteId = null;
                  }}"
                >
                  ${localize("common.actions.cancel", lang)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
                  ${localize("common.actions.delete", lang)}
                </button>
              </div>
            </ha-dialog>
          `
        : ""}

      <!-- Arm confirm -->
      ${armDist
        ? html`
            <ha-dialog
              open
              @closed="${() => {
                this._armConfirmId = null;
              }}"
              heading="${localize(
                "panels.distributors.commissioning.confirm_dialog.title",
                lang,
              )}"
            >
              <p>
                ${localize(
                  "panels.distributors.commissioning.confirm_dialog.body",
                  lang,
                )}
              </p>
              <p><strong>${armDist.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
                    this._armConfirmId = null;
                  }}"
                >
                  ${localize("common.actions.cancel", lang)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${() =>
                    armDist.id !== undefined &&
                    this._setArmed(armDist.id, true)}"
                >
                  ${localize(
                    "panels.distributors.commissioning.confirm_dialog.confirm",
                    lang,
                  )}
                </button>
              </div>
            </ha-dialog>
          `
        : ""}

      <!-- Reset-to-outlet-1 confirm (safety: a stray click would falsely mark synced) -->
      ${resyncDist
        ? html`
            <ha-dialog
              open
              @closed="${() => {
                this._confirmResyncHomeId = null;
              }}"
              heading="${localize(
                "panels.distributors.commissioning.confirm_resync.title",
                lang,
              )}"
            >
              <p>
                ${localize(
                  "panels.distributors.commissioning.confirm_resync.body",
                  lang,
                )}
              </p>
              <p><strong>${resyncDist.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
                    this._confirmResyncHomeId = null;
                  }}"
                >
                  ${localize("common.actions.cancel", lang)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._confirmResyncHome}"
                >
                  ${localize(
                    "panels.distributors.commissioning.resync_home",
                    lang,
                  )}
                </button>
              </div>
            </ha-dialog>
          `
        : ""}

      <!-- Set-current-outlet confirm (safety: a stray click would falsely mark synced at the entered outlet) -->
      ${setOutletDist
        ? html`
            <ha-dialog
              open
              @closed="${() => {
                this._confirmSetOutletId = null;
              }}"
              heading="${localize(
                "panels.distributors.commissioning.confirm_set_outlet.title",
                lang,
              )}"
            >
              <p>
                ${localize(
                  "panels.distributors.commissioning.confirm_set_outlet.body",
                  lang,
                )}
              </p>
              <p>
                <strong
                  >${setOutletDist.name} ·
                  ${localize("panels.distributors.commissioning.outlet", lang)}
                  ${setOutletTarget}</strong
                >
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
                    this._confirmSetOutletId = null;
                  }}"
                >
                  ${localize("common.actions.cancel", lang)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._confirmSetOutlet}"
                >
                  ${localize(
                    "panels.distributors.commissioning.set_outlet",
                    lang,
                  )}
                </button>
              </div>
            </ha-dialog>
          `
        : ""}
      ${this.distributors.map((d, i) => this.renderDistributor(d, i))}
    `;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.globalDebounceTimer) {
      clearTimeout(this.globalDebounceTimer);
      this.globalDebounceTimer = null;
    }
    if (this._savedResetTimer) {
      clearTimeout(this._savedResetTimer);
      this._savedResetTimer = null;
    }
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      .card-header.dist-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        user-select: none;
      }
      .card-header.dist-toggle:hover {
        background: var(--secondary-background-color);
      }
      .card-header.dist-toggle .name {
        flex: 1 1 auto;
      }
      .dist-chevron {
        color: var(--secondary-text-color);
        flex: 0 0 auto;
      }

      ha-settings-row {
        padding: 0 16px;
      }

      .settings-input {
        height: 36px;
      }

      /* Position / state badge */
      .pos-badge {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
        color: #fff;
        background: var(--secondary-text-color);
        flex: 0 0 auto;
      }
      .pos-badge.pos-synced {
        background: var(--success-color, #2e7d32);
      }
      .pos-badge.pos-uncertain {
        background: var(--warning-color, #f9a825);
      }

      .commissioning {
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
        padding-top: 8px;
      }
      .commissioning-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        padding: 0 16px 4px;
      }
      .section-title {
        font-weight: 600;
        color: var(--primary-text-color);
      }

      /* Outlet -> zone assignment (FB5) */
      .outlet-config {
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
        padding-top: 8px;
      }
      .outlet-config .item-description {
        padding: 0 16px;
      }
      .outlet-rows {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 4px 16px 8px;
      }
      .outlet-row {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .outlet-label {
        flex: 0 0 90px;
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      .outlet-row select {
        flex: 1 1 auto;
        min-width: 140px;
      }

      .inline-controls {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
      }

      .run-now-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 12px;
        padding: 12px 16px 4px;
      }
      .run-now-hint {
        color: var(--secondary-text-color);
        font-size: 0.82rem;
      }

      /* Instance-level safety advisories in the intro card. */
      .advisories {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin: 8px 0 4px;
      }
      .advisory {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-size: 0.85rem;
        line-height: 1.45;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-left: 3px solid var(--primary-color);
        border-radius: 0 3px 3px 0;
        padding: 6px 10px;
      }
      .advisory ha-icon {
        --mdc-icon-size: 18px;
        flex: 0 0 auto;
        color: var(--primary-color);
      }

      /* Muted one-liner under the re-sync controls. */
      .commissioning-note {
        color: var(--secondary-text-color);
        font-size: 0.8rem;
        line-height: 1.4;
        padding: 2px 16px 6px;
      }

      .save-status {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-left: auto;
        margin-right: 8px;
        font-size: 0.8125rem;
        font-weight: 500;
      }
      .save-status ha-icon {
        --mdc-icon-size: 18px;
      }
      .save-status.saving {
        color: var(--secondary-text-color);
      }
      .save-status.saved {
        color: var(--success-color, #2e7d32);
      }

      .settings-danger-row {
        display: flex;
        justify-content: flex-end;
        padding: 12px 16px;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }

      .add-form {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 8px 0;
        min-width: 300px;
      }
      .add-form .settings-input {
        width: 100%;
        height: 36px;
      }
    `;
  }
}

export { SmartIrrigationViewDistributorSettings };
