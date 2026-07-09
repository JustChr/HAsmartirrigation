import { TemplateResult, LitElement, html, CSSResultGroup, css } from "lit";
import { property, state } from "lit/decorators.js";
import { HomeAssistant } from "../../types";
import { loadHaForm } from "../../load-ha-elements";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { mdiCog, mdiClose } from "@mdi/js";
import {
  fetchConfig,
  fetchZones,
  fetchIrrigationOutlook,
  calculateZone,
  updateZone,
  calculateAllZones,
  updateAllZones,
  irrigateNow,
  setRainDelayHours,
  clearRainDelay,
  runZone,
  stopZone,
  fetchDistributors,
} from "../../data/websockets";
import { SubscribeMixin } from "../../subscribe-mixin";

import {
  SmartIrrigationConfig,
  SmartIrrigationZone,
  SmartIrrigationZoneState,
  SmartIrrigationDistributor,
  IrrigationOutlook,
  UpcomingRun,
  SkipCheck,
  ZoneEstimate,
  ZoneFault,
  ZoneSkip,
  ActiveRun,
} from "../../types";
import {
  output_unit,
  extractErrorMessage,
  showToast,
  showErrorToast,
  navigate,
  formatDuration,
} from "../../helpers";
import { exportPath } from "../../common/navigation";
import { globalStyle } from "../../styles/global-style";
import { localize } from "../../../localize/localize";
import { DOMAIN, ZONE_BUCKET } from "../../const";
import {
  addDays,
  formatDateTime,
  formatTime,
  formatWeekdayTime,
  fromNow,
  isSameDay,
} from "../../common/datetime";

/**
 * Everyday dashboard for zones: at-a-glance decision + status, and the
 * operational actions (update / calculate / irrigate). Zone configuration,
 * reporting and management live in Setup → Zones; a gear icon on each card
 * deep-links there. (UX restructure N2/N3.)
 */
class SmartIrrigationViewZones extends SubscribeMixin(LitElement) {
  hass?: HomeAssistant;
  @property() config?: SmartIrrigationConfig;

  /**
   * Hide admin-only deep links (per-zone settings gear, "set up a schedule",
   * the first-run wizard banner). Set by the Lovelace card so non-admin users
   * see a clean operational view. (Default false = full admin panel.)
   */
  @property({ type: Boolean }) hideSettingsLinks = false;

  /**
   * Which action buttons to expose. "full" = update/calculate/irrigate (panel),
   * "irrigate" = irrigate only (card), "none" = read-only.
   */
  @property({ attribute: false }) actionsMode: "full" | "irrigate" | "none" =
    "full";

  @property({ type: Array })
  private zones: SmartIrrigationZone[] = [];

  @state() private _outlook?: IrrigationOutlook;

  // Distributors, fetched so a member zone's custom-run control can be gated on
  // its distributor's live `active_cycle` (Plan F busy-hint). Empty until the
  // first fetch resolves; a member with no matching distributor stays enabled.
  @state() private _distributors: SmartIrrigationDistributor[] = [];

  @property({ type: Boolean })
  private isLoading = true;

  private _initialLoadDone = false;

  @property({ type: Boolean })
  private isSaving = false;

  @state() private _operationError: string | null = null;

  // Pending irrigate confirmation: "all", a zone id (string), or null.
  @state() private _confirmIrrigate: string | null = null;

  // Whether the "why won't it run" skip reasons are expanded (tap-friendly).
  @state() private _skipDetailsOpen = false;

  // Per-zone custom-run duration (minutes), keyed by zone id. Defaults to 10.
  @state() private _runMinutes: Record<string, number> = {};

  // Current epoch ms, ticked once a second while a run is in progress so the
  // countdown re-renders. Null when no ticker is running.
  @state() private _now = Date.now();
  private _countdownTimer: number | null = null;

  private _updateScheduled = false;
  private _scheduleUpdate() {
    if (this._updateScheduled) return;
    this._updateScheduled = true;
    requestAnimationFrame(() => {
      this._updateScheduled = false;
      this.requestUpdate();
    });
  }

  firstUpdated() {
    loadHaForm()
      .then(() => this._scheduleUpdate())
      .catch((error) => {
        console.error("Failed to load HA form:", error);
        this._scheduleUpdate();
      });
  }

  public disconnectedCallback(): void {
    super.disconnectedCallback();
    this._stopCountdownTicker();
  }

  /** Run a 1s ticker only while at least one zone has an in-progress run. */
  private _syncCountdownTicker(): void {
    const hasActive = Object.keys(this._outlook?.active_runs ?? {}).length > 0;
    if (hasActive && this._countdownTimer === null) {
      this._countdownTimer = window.setInterval(() => {
        this._now = Date.now();
      }, 1000);
    } else if (!hasActive) {
      this._stopCountdownTicker();
    }
  }

  private _stopCountdownTicker(): void {
    if (this._countdownTimer !== null) {
      window.clearInterval(this._countdownTimer);
      this._countdownTimer = null;
    }
  }

  public hassSubscribe(): Promise<UnsubscribeFunc>[] {
    this._fetchData().catch((error) => {
      console.error("Failed to fetch initial data:", error);
    });

    return [
      this.hass!.connection.subscribeMessage(
        () => {
          this._fetchData().catch((error) => {
            console.error("Failed to fetch data on config update:", error);
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

      const [config, zones, outlook, distributors] = await Promise.all([
        fetchConfig(this.hass),
        fetchZones(this.hass),
        fetchIrrigationOutlook(this.hass).catch((e) => {
          // Outlook is supplementary — never block the dashboard on it.
          console.error("Failed to fetch irrigation outlook:", e);
          return undefined;
        }),
        fetchDistributors(this.hass).catch((e) => {
          // Distributors only gate the member busy-hint — never block the
          // dashboard on them; treat a failure as "none known" (control stays
          // enabled, the backend still rejects a run while a cycle is active).
          console.error("Failed to fetch distributors:", e);
          return [] as SmartIrrigationDistributor[];
        }),
      ]);

      this.config = config;
      this.zones = zones;
      this._outlook = outlook;
      this._distributors = distributors;
      this._initialLoadDone = true;
      this._syncCountdownTicker();
    } catch (error) {
      console.error("Error fetching data:", error);
      showErrorToast(this, this.hass, "common.errors.load_failed", error);
    } finally {
      if (isInitial) this.isLoading = false;
      this._scheduleUpdate();
    }
  }

  private handleCalculateAllZones(): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    calculateAllZones(this.hass)
      .catch((error) => {
        console.error("Failed to calculate all zones:", error);
        showErrorToast(this, this.hass, "common.errors.action_failed", error);
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after calc-all:", e),
        );
      });
  }

  private handleUpdateAllZones(): void {
    if (!this.hass) return;
    this.isSaving = true;
    this._scheduleUpdate();
    updateAllZones(this.hass)
      .catch((error) => {
        console.error("Failed to update all zones:", error);
        showErrorToast(this, this.hass, "common.errors.action_failed", error);
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after update-all:", e),
        );
      });
  }

  /** Whether a zone can be actuated manually: a classic zone needs a linked
   * switch/valve; a self-closing service zone needs its run_service set; a
   * distributor member has neither of its own — it is watered through the
   * distributor outlet, so membership (`distributor_id`) makes it actuatable
   * and the backend routes the run to the distributor (Plan F). */
  private _canActuate(zone: SmartIrrigationZone): boolean {
    return !!(
      zone.linked_entity ||
      (zone.watering_mode === "service" && zone.run_service) ||
      zone.distributor_id != null
    );
  }

  // Number of zones an "irrigate all" would actually start (actuatable + duration).
  private get _linkedZoneCount(): number {
    return this.zones.filter(
      (z) => this._canActuate(z) && (z.duration ?? 0) > 0,
    ).length;
  }

  private async _doIrrigate(): Promise<void> {
    const target = this._confirmIrrigate;
    this._confirmIrrigate = null;
    if (target === null || !this.hass) return;

    const isAll = target === "all";
    const zone = isAll
      ? undefined
      : this.zones.find((z) => z.id?.toString() === target);
    const label = isAll
      ? `(${this._linkedZoneCount})`
      : `: ${zone?.name ?? target}`;

    try {
      await irrigateNow(this.hass, isAll ? undefined : target);
      showToast(
        this,
        `${localize("panels.zones.confirm_irrigate.toast_started", this.hass.language)} ${label}`,
      );
    } catch (err) {
      const msg = extractErrorMessage(err);
      console.error("irrigate_now failed", err);
      showToast(
        this,
        `${localize("panels.zones.confirm_irrigate.toast_failed", this.hass.language)}: ${msg}`,
      );
    }
  }

  // --- rain delay / vacation hold (WS-5) -----------------------------------

  /** The active hold's resume time (Date) when in the future, else null. */
  private get _rainDelayUntil(): Date | null {
    const raw = this._outlook?.rain_delay_until;
    if (!raw) return null;
    const d = new Date(raw);
    return d.getTime() > Date.now() ? d : null;
  }

  private async _setRainDelay(hours: number): Promise<void> {
    if (!this.hass) return;
    try {
      await setRainDelayHours(this.hass, hours);
      await this._fetchData();
    } catch (err) {
      console.error("set_rain_delay failed", err);
      showErrorToast(this, this.hass, "common.errors.action_failed", err);
    }
  }

  private async _clearRainDelay(): Promise<void> {
    if (!this.hass) return;
    try {
      await clearRainDelay(this.hass);
      await this._fetchData();
    } catch (err) {
      console.error("clear_rain_delay failed", err);
      showErrorToast(this, this.hass, "common.errors.action_failed", err);
    }
  }

  // --- custom-duration manual run (WS-5) -----------------------------------

  private _zoneRunMinutes(zone: SmartIrrigationZone): number {
    const key = String(zone.id ?? "");
    return this._runMinutes[key] ?? 10;
  }

  /**
   * The distributor a member zone belongs to (by `distributor_id`), or
   * undefined for a standalone zone or when the distributor list hasn't loaded.
   */
  private _zoneDistributor(
    zone: SmartIrrigationZone,
  ): SmartIrrigationDistributor | undefined {
    if (zone.distributor_id == null) return undefined;
    return this._distributors.find((d) => d.id === zone.distributor_id);
  }

  /**
   * True when this zone is a distributor member whose distributor is mid-cycle.
   * The backend rejects a member run while `active_cycle` is non-empty; we
   * mirror that here to disable the control and show a wait-for-home hint,
   * preferring the distributor object over any entity state for consistency.
   */
  private _distributorBusy(zone: SmartIrrigationZone): boolean {
    const dist = this._zoneDistributor(zone);
    return !!dist && Object.keys(dist.active_cycle ?? {}).length > 0;
  }

  private async _runZoneFor(zone: SmartIrrigationZone): Promise<void> {
    if (!this.hass || !this._canActuate(zone) || zone.id === undefined) return;
    // Don't even fire while the member's distributor is running — the backend
    // rejects it, but skipping the round-trip keeps the toast honest.
    if (this._distributorBusy(zone)) return;
    const minutes = this._zoneRunMinutes(zone);
    if (!(minutes > 0)) return;
    try {
      await runZone(this.hass, zone.id.toString(), minutes);
      showToast(
        this,
        `${localize("panels.zones.run_zone.toast_started", this.hass.language)}: ${zone.name} (${minutes} min)`,
      );
    } catch (err) {
      const msg = extractErrorMessage(err);
      console.error("run_zone failed", err);
      showToast(
        this,
        `${localize("panels.zones.confirm_irrigate.toast_failed", this.hass.language)}: ${msg}`,
      );
    }
  }

  /** The in-progress run for this zone, or undefined when it is idle. */
  private _activeRun(zone: SmartIrrigationZone): ActiveRun | undefined {
    if (zone.id === undefined) return undefined;
    return this._outlook?.active_runs?.[String(zone.id)];
  }

  /** Seconds remaining for a time-bounded run, or null (no/unknown end). */
  private _runSecondsLeft(run: ActiveRun): number | null {
    if (!run.ends_at) return null;
    const left = Math.round(
      (new Date(run.ends_at).getTime() - this._now) / 1000,
    );
    return left > 0 ? left : 0;
  }

  private async _stopZone(zone: SmartIrrigationZone): Promise<void> {
    if (!this.hass || zone.id === undefined) return;
    try {
      await stopZone(this.hass, zone.id.toString());
      showToast(
        this,
        `${localize("panels.zones.stop_zone.toast_stopped", this.hass.language)}: ${zone.name}`,
      );
      await this._fetchData();
    } catch (err) {
      const msg = extractErrorMessage(err);
      console.error("stop_zone failed", err);
      showToast(
        this,
        `${localize("panels.zones.confirm_irrigate.toast_failed", this.hass.language)}: ${msg}`,
      );
    }
  }

  private handleCalculateZone(index: number): void {
    const zone = this.zones[index];
    if (!zone || zone.id == undefined || !this.hass) return;
    this._operationError = null;
    this.isSaving = true;
    this._scheduleUpdate();
    calculateZone(this.hass, zone.id.toString())
      .catch((err) => {
        const msg = extractErrorMessage(err);
        console.error("calculateZone failed:", err);
        this._operationError = msg;
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after calc:", e),
        );
      });
  }

  private handleUpdateZone(index: number): void {
    const zone = this.zones[index];
    if (!zone || zone.id == undefined || !this.hass) return;
    this._operationError = null;
    this.isSaving = true;
    this._scheduleUpdate();
    updateZone(this.hass, zone.id.toString())
      .catch((err) => {
        const msg = extractErrorMessage(err);
        console.error("updateZone failed:", err);
        this._operationError = msg;
      })
      .finally(() => {
        this.isSaving = false;
        this._fetchData().catch((e) =>
          console.error("fetchData after update:", e),
        );
      });
  }

  /** Open this zone's settings in the Setup → Zones tab. */
  private _openZoneSettings(zone: SmartIrrigationZone): void {
    const params =
      zone.id !== undefined ? { params: { zone: String(zone.id) } } : undefined;
    navigate(
      this,
      params
        ? exportPath("setup", "zones", params)
        : exportPath("setup", "zones"),
    );
  }

  // --- outlook helpers -----------------------------------------------------

  /** Whether an upcoming run targets this zone ("all" or its id in the list). */
  private _runTargetsZone(
    run: UpcomingRun,
    zone: SmartIrrigationZone,
  ): boolean {
    if (run.zones === "all") return true;
    if (Array.isArray(run.zones) && zone.id !== undefined) {
      return run.zones.map((z) => Number(z)).includes(Number(zone.id));
    }
    return false;
  }

  /** Soonest scheduled *irrigate* run with a known clock time (overall). */
  private get _nextIrrigateRun(): UpcomingRun | undefined {
    return this._outlook?.upcoming_runs.find(
      (r) => r.action === "irrigate" && r.next_run_utc,
    );
  }

  /** Soonest scheduled irrigate run with a known time that targets this zone. */
  private _nextIrrigateRunForZone(
    zone: SmartIrrigationZone,
  ): UpcomingRun | undefined {
    return this._outlook?.upcoming_runs.find(
      (r) =>
        r.action === "irrigate" &&
        r.next_run_utc &&
        this._runTargetsZone(r, zone),
    );
  }

  /** Skip guards that are enabled (active), regardless of current verdict. */
  private get _activeGuards(): SkipCheck[] {
    return this._outlook?.skip_preview.checks.filter((c) => c.enabled) ?? [];
  }

  /** Enabled guards that would currently skip the next run. */
  private get _triggeredGuards(): SkipCheck[] {
    return this._activeGuards.filter((c) => c.would_skip);
  }

  /**
   * Per-zone irrigation gate. Mirrors the backend runner, but prefers the live
   * intra-day deficit estimate over the once-daily calc's stored bucket when
   * available — it reflects ET/rain since the last calc, so the "watering
   * needed?" verdict stays current (e.g. flips to "no" after rain). Falls back
   * to the stored bucket when no estimate exists.
   */
  private _zoneHasDeficit(zone: SmartIrrigationZone): boolean {
    const duration = zone.duration ?? 0;
    const threshold = Number(zone.bucket_threshold ?? 0);
    const est = this._zoneEstimate(zone);
    const deficit =
      est && est.available && est.live_deficit != null
        ? est.live_deficit
        : Number(zone.bucket ?? 0);
    return duration > 0 && deficit < threshold;
  }

  /** Compact local time for a run, e.g. "today 06:00" / "tomorrow 06:00". */
  private _formatRunTime(utc: string): string {
    if (!this.hass) return "";
    const lang = this.hass.language;
    const d = new Date(utc);
    const time = formatTime(d);
    const now = new Date();
    if (isSameDay(d, now)) {
      return `${localize("panels.zones.outlook.today", lang)} ${time}`;
    }
    if (isSameDay(d, addDays(now, 1))) {
      return `${localize("panels.zones.outlook.tomorrow", lang)} ${time}`;
    }
    return formatWeekdayTime(d, lang);
  }

  private _guardLabel(check: SkipCheck): string {
    return localize(
      `panels.zones.outlook.checks.${check.id}`,
      this.hass!.language,
    );
  }

  /** Short observed-vs-threshold detail for a guard chip, or "" if unavailable. */
  private _guardDetail(check: SkipCheck): string {
    if (!check.available || check.observed === null) return "";
    return localize(
      `panels.zones.outlook.check_detail.${check.id}`,
      this.hass!.language,
      "{observed}",
      String(check.observed),
      "{threshold}",
      String(check.threshold ?? ""),
    );
  }

  /** Expandable "why the next run will skip" reasons (tap-friendly on mobile). */
  private _renderSkipReasons(): TemplateResult {
    const lang = this.hass!.language;
    return html`
      <div class="outlook-line outlook-skip-reasons">
        <ul class="skip-reasons">
          ${this._triggeredGuards.map((c) => {
            const detail = this._guardDetail(c);
            return html`<li>
              ${this._guardLabel(c)}${detail ? html` — ${detail}` : ""}
            </li>`;
          })}
        </ul>
      </div>
      <div class="outlook-line outlook-dim skip-reasons-note">
        ${localize("panels.zones.outlook.provisional", lang)}
      </div>
    `;
  }

  private _openSchedules(): void {
    // Schedules now live under the task-shaped "When to Water" Setup tab.
    navigate(this, exportPath("setup", "when-to-water"));
  }

  /** Human label for a run's action verb (Water / Recalculate / Refresh data). */
  private _runActionLabel(run: UpcomingRun): string {
    return localize(
      `panels.zones.outlook.actions.${run.action}`,
      this.hass!.language,
    );
  }

  private _runTargetsLabel(run: UpcomingRun): string {
    const lang = this.hass!.language;
    if (run.zones === "all") {
      return localize("panels.zones.outlook.targets_all", lang);
    }
    const count = Array.isArray(run.zones) ? run.zones.length : 0;
    return localize(
      "panels.zones.outlook.targets_zones",
      lang,
      "{count}",
      String(count),
    );
  }

  /**
   * Global outlook banner: what runs next, whether it will be skipped, which
   * guards are active, and the most recent real run decision. Schedules and
   * skip conditions are global, so they live here rather than per card.
   */
  private _renderOutlookBanner(): TemplateResult {
    if (!this.hass || !this._outlook) return html``;
    const lang = this.hass.language;
    const nextRun = this._nextIrrigateRun;
    const triggered = this._triggeredGuards;
    const last = this._outlook.last_skip_evaluation;

    // No automatic irrigate schedule → make the manual-only reality explicit.
    if (!nextRun || !nextRun.next_run_utc) {
      return html`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
              <span>${localize("panels.zones.outlook.no_schedule", lang)}</span>
              ${this.hideSettingsLinks
                ? ""
                : html`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
                      ${localize("panels.zones.outlook.setup_schedule", lang)}
                    </button>
                  `}
            </div>
            ${last ? this._renderLastRunLine(last) : ""}
          </div>
        </ha-card>
      `;
    }

    return html`
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
                >${localize("panels.zones.outlook.next_run", lang)}:</strong
              >
              ${this._runActionLabel(nextRun)}
              ${this._formatRunTime(nextRun.next_run_utc)}
              <span class="outlook-dim"
                >· ${nextRun.name} · ${this._runTargetsLabel(nextRun)}</span
              >
            </span>
          </div>

          ${triggered.length > 0
            ? html`
                <div class="outlook-line outlook-skip">
                  <ha-icon icon="mdi:alert"></ha-icon>
                  <span
                    >${localize("panels.zones.outlook.will_skip", lang)}</span
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
                    title="${localize(
                      "panels.zones.outlook.why_skipped",
                      lang,
                    )}"
                    @click="${() => {
                      this._skipDetailsOpen = !this._skipDetailsOpen;
                    }}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen
                        ? "mdi:chevron-up"
                        : "mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
                      >${localize(
                        "panels.zones.outlook.why_skipped",
                        lang,
                      )}</span
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen ? this._renderSkipReasons() : ""}
              `
            : html`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
                    >${localize("panels.zones.outlook.will_run", lang)}</span
                  >
                </div>
              `}
          ${last ? this._renderLastRunLine(last) : ""}
        </div>
      </ha-card>
    `;
  }

  /**
   * Rain delay / vacation hold control. When a hold is active it shows a
   * prominent "Paused until …" banner with a Resume button; otherwise a compact
   * "Delay 24h / 48h" row so the user can pause without leaving the dashboard.
   * Automatic/scheduled runs are gated while paused — manual runs still work.
   */
  private _renderRainDelay(): TemplateResult {
    if (!this.hass || this.actionsMode === "none") return html``;
    const lang = this.hass.language;
    const until = this._rainDelayUntil;

    if (until) {
      return html`
        <ha-card class="rain-delay-card paused">
          <div class="rain-delay">
            <ha-icon icon="mdi:pause-circle"></ha-icon>
            <span class="rain-delay-msg">
              <strong
                >${localize("panels.zones.rain_delay.paused", lang)}</strong
              >
              ${localize("panels.zones.rain_delay.until", lang)}
              ${formatDateTime(until.toISOString())}
            </span>
            <button class="action-btn" @click="${() => this._clearRainDelay()}">
              <ha-icon icon="mdi:play"></ha-icon>
              ${localize("panels.zones.rain_delay.resume", lang)}
            </button>
          </div>
        </ha-card>
      `;
    }

    return html`
      <div class="rain-delay-row">
        <span class="rain-delay-label">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>
          ${localize("panels.zones.rain_delay.title", lang)}
        </span>
        <button class="action-btn" @click="${() => this._setRainDelay(24)}">
          ${localize("panels.zones.rain_delay.delay_24h", lang)}
        </button>
        <button class="action-btn" @click="${() => this._setRainDelay(48)}">
          ${localize("panels.zones.rain_delay.delay_48h", lang)}
        </button>
      </div>
    `;
  }

  private _renderLastRunLine(last: {
    timestamp: string;
    would_skip: boolean;
    checks: SkipCheck[];
  }): TemplateResult {
    const lang = this.hass!.language;
    const when = fromNow(last.timestamp, lang);
    const reasons = last.checks
      .filter((c) => c.enabled && c.would_skip)
      .map((c) => this._guardLabel(c).toLowerCase())
      .join(", ");
    const verdict = last.would_skip
      ? `${localize("panels.zones.outlook.last_run_skipped", lang)}${reasons ? ` (${reasons})` : ""}`
      : localize("panels.zones.outlook.last_run_ran", lang);
    return html`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${localize("panels.zones.outlook.last_run", lang)}:</span
        >
        <span>${verdict} · ${when}</span>
      </div>
    `;
  }

  /**
   * At-a-glance answer to "will this zone water, when, and if not why?" — the
   * daily question. Combines the per-zone deficit gate with the global skip
   * preview and the next scheduled run.
   */
  private _renderZoneDecision(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass) return html``;
    const lang = this.hass.language;
    const duration = zone.duration ?? 0;

    let text: string;
    let cls: string;
    let icon: string;

    if (zone.state === SmartIrrigationZoneState.Disabled) {
      text = localize("panels.zones.status.decision_disabled", lang);
      cls = "neutral";
      icon = "mdi:power-off";
    } else if (!zone.last_calculated) {
      text = localize("panels.zones.status.decision_unknown", lang);
      cls = "unknown";
      icon = "mdi:help-circle-outline";
    } else if (!this._zoneHasDeficit(zone)) {
      text = localize("panels.zones.status.decision_no_water", lang);
      cls = "ok";
      icon = "mdi:check-circle-outline";
    } else {
      // Deficit exists — but will the next run actually water it?
      const dur = formatDuration(duration);
      const triggered = this._triggeredGuards;
      const nextRun = this._nextIrrigateRunForZone(zone);
      if (triggered.length > 0) {
        text = localize(
          "panels.zones.status.decision_water_skip",
          lang,
          "{duration}",
          dur,
          "{reason}",
          this._guardLabel(triggered[0]).toLowerCase(),
        );
        cls = "skip";
        icon = "mdi:weather-rainy";
      } else if (nextRun && nextRun.next_run_utc) {
        text = localize(
          "panels.zones.status.decision_water_at",
          lang,
          "{duration}",
          dur,
          "{time}",
          this._formatRunTime(nextRun.next_run_utc),
        );
        cls = "water";
        icon = "mdi:water";
      } else {
        text = localize(
          "panels.zones.status.decision_water_no_schedule",
          lang,
          "{duration}",
          dur,
        );
        cls = "water";
        icon = "mdi:water-alert";
      }
    }

    return html`
      <div class="zone-decision ${cls}">
        <ha-icon icon="${icon}"></ha-icon>
        <span>${text}</span>
      </div>
    `;
  }

  private _zoneEstimate(zone: SmartIrrigationZone): ZoneEstimate | undefined {
    if (zone.id === undefined) return undefined;
    return this._outlook?.zone_estimates?.[String(zone.id)];
  }

  private _zoneFault(zone: SmartIrrigationZone): ZoneFault | undefined {
    if (zone.id === undefined) return undefined;
    return this._outlook?.zone_faults?.[String(zone.id)];
  }

  /**
   * Prominent banner when this zone's most recent run failed (e.g. the valve
   * never opened). The bucket was deliberately left unchanged, so the deficit
   * persists until the next successful run clears the fault.
   */
  private _renderZoneFault(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass) return html``;
    const fault = this._zoneFault(zone);
    if (!fault) return html``;
    const lang = this.hass.language;
    const detail =
      localize(`panels.zones.fault.${fault.reason}`, lang) ||
      localize("panels.zones.fault.generic", lang);
    const since = fault.timestamp ? formatDateTime(fault.timestamp) : "";
    return html`
      <div class="zone-fault" title="${since}">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <span>
          <strong>${localize("panels.zones.fault.title", lang)}</strong>
          — ${detail}
        </span>
      </div>
    `;
  }

  private _zoneSkip(zone: SmartIrrigationZone): ZoneSkip | undefined {
    if (zone.id === undefined) return undefined;
    return this._outlook?.zone_skips?.[String(zone.id)];
  }

  /**
   * Info chip when this zone was skipped on its last automatic run because its
   * soil-moisture sensor read wetter than the threshold. The bucket was reset
   * to 0 (re-anchored to field capacity) at the same time.
   */
  private _renderZoneSkip(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass) return html``;
    const skip = this._zoneSkip(zone);
    if (!skip) return html``;
    const lang = this.hass.language;
    const detail = localize(
      "panels.zones.skip.soil_moisture",
      lang,
      "{observed}",
      String(skip.observed),
      "{threshold}",
      String(skip.threshold),
    );
    const since = skip.timestamp ? formatDateTime(skip.timestamp) : "";
    return html`
      <div class="zone-skip" title="${since}">
        <ha-icon icon="mdi:water-off"></ha-icon>
        <span>
          <strong>${localize("panels.zones.skip.title", lang)}</strong>
          — ${detail}
        </span>
      </div>
    `;
  }

  /**
   * Read-only "live" deficit estimate chip for the status line. Distinct from
   * the official bucket (which drives irrigation) — this just shows the
   * estimated drift since the last calculation.
   */
  private _renderZoneEstimate(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass) return html``;
    const est = this._zoneEstimate(zone);
    if (!est || !est.available || est.live_deficit == null) return html``;
    const lang = this.hass.language;
    const unit = output_unit(this.config, ZONE_BUCKET);
    const color =
      est.live_deficit < 0 ? "var(--warning-color)" : "var(--success-color)";
    const methodKey = est.method === "proxy" ? "proxy" : "hourly";
    const detail =
      localize(`panels.zones.status.estimate_method.${methodKey}`, lang) +
      (est.as_of ? ` · ${formatTime(est.as_of)}` : "");
    return html`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${detail}">
        ${localize("panels.zones.status.estimate_now", lang)}
        <strong style="color: ${color}"
          >≈ ${est.live_deficit.toFixed(2)} ${unit}</strong
        >
        <span class="estimate-tag"
          >${localize("panels.zones.status.estimate_tag", lang)}</span
        >
      </span>
    `;
  }

  /** Per-zone "next run" fragment for the status line, when one is scheduled. */
  private _renderZoneNextRun(zone: SmartIrrigationZone): TemplateResult {
    if (!this.hass) return html``;
    const run = this._nextIrrigateRunForZone(zone);
    if (!run || !run.next_run_utc) return html``;
    // Avoid duplication: the "Will water … at <time>" decision line already
    // shows this time, so only add it here when the decision doesn't.
    const decisionShowsTime =
      zone.state !== SmartIrrigationZoneState.Disabled &&
      zone.last_calculated &&
      this._zoneHasDeficit(zone) &&
      this._triggeredGuards.length === 0;
    if (decisionShowsTime) return html``;
    return html`
      <span class="status-sep">·</span>
      <span>
        ${localize("panels.zones.outlook.next_run", this.hass.language)}:
        <strong>${this._formatRunTime(run.next_run_utc)}</strong>
      </span>
    `;
  }

  private renderZone(zone: SmartIrrigationZone, index: number): TemplateResult {
    if (!this.hass) return html``;

    const bucket = Number(zone.bucket ?? 0);
    const bucketColor =
      bucket < 0 ? "var(--warning-color)" : "var(--success-color)";
    const stateClass =
      zone.state === SmartIrrigationZoneState.Automatic
        ? "state-automatic"
        : zone.state === SmartIrrigationZoneState.Manual
          ? "state-manual"
          : "state-disabled";
    const lastChecked = zone.last_calculated
      ? formatDateTime(zone.last_calculated)
      : localize("panels.zones.status.never", this.hass.language);

    return html`
      <ha-card>
        <div class="card-header">
          <div class="name">${zone.name}</div>
          <span class="zone-state-badge ${stateClass}">
            ${localize(
              `panels.zones.labels.states.${zone.state}`,
              this.hass.language,
            )}
          </span>
          ${this.hideSettingsLinks
            ? ""
            : html`
                <ha-icon-button
                  .path="${mdiCog}"
                  title="${localize(
                    "panels.zones.actions.open_settings",
                    this.hass.language,
                  )}"
                  @click="${() => this._openZoneSettings(zone)}"
                ></ha-icon-button>
              `}
        </div>

        <!-- RUN FAULT (e.g. valve didn't open) -->
        ${this._renderZoneFault(zone)}

        <!-- SOIL-MOISTURE SKIP (wet-veto) -->
        ${this._renderZoneSkip(zone)}

        <!-- AT-A-GLANCE DECISION -->
        ${this._renderZoneDecision(zone)}

        <!-- COMPACT STATUS -->
        <div class="card-content">
          <div class="zone-status-line">
            <span
              title="${localize(
                "panels.zones.help.bucket",
                this.hass.language,
              )}"
            >
              ${localize("panels.zones.labels.bucket", this.hass.language)}:
              <strong style="color: ${bucketColor}"
                >${bucket.toFixed(2)}
                ${output_unit(this.config, ZONE_BUCKET)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
              ${localize(
                "panels.zones.status.last_checked",
                this.hass.language,
              )}:
              <strong>${lastChecked}</strong>
            </span>
            ${this._renderZoneEstimate(zone)} ${this._renderZoneNextRun(zone)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${this.actionsMode === "full" &&
          zone.state === SmartIrrigationZoneState.Automatic
            ? html`
                <button
                  class="action-btn"
                  title="${localize(
                    "panels.zones.help.update",
                    this.hass.language,
                  )}"
                  @click="${() => this.handleUpdateZone(index)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${localize("panels.zones.actions.update", this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${localize(
                    "panels.zones.help.calculate",
                    this.hass.language,
                  )}"
                  @click="${() => this.handleCalculateZone(index)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${localize(
                    "panels.zones.actions.calculate",
                    this.hass.language,
                  )}
                </button>
              `
            : ""}
          ${this.actionsMode !== "none" &&
          this._canActuate(zone) &&
          this._zoneHasDeficit(zone)
            ? html`
                <button
                  class="action-btn"
                  raised
                  @click="${() => {
                    if (zone.id !== undefined) {
                      this._confirmIrrigate = zone.id.toString();
                    }
                  }}"
                  ?disabled="${this.isSaving || this._distributorBusy(zone)}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${localize(
                    "panels.zones.labels.irrigate_now",
                    this.hass.language,
                  )}
                </button>
              `
            : !this._canActuate(zone)
              ? html`
                  <button
                    class="action-btn"
                    disabled
                    title="${localize(
                      "panels.zones.help.irrigate_link_entity",
                      this.hass.language,
                    )}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${localize(
                      "panels.zones.labels.irrigate_now",
                      this.hass.language,
                    )}
                  </button>
                  <span class="zones-top-note">
                    ${localize(
                      "panels.zones.help.irrigate_link_entity",
                      this.hass.language,
                    )}
                  </span>
                `
              : ""}
          ${this._renderRunZoneControl(zone)}
        </div>
      </ha-card>
    `;
  }

  /** "Run for N min" inline control — a custom-duration manual run (WS-5). */
  private _renderRunZoneControl(zone: SmartIrrigationZone): TemplateResult {
    if (
      !this.hass ||
      this.actionsMode === "none" ||
      !this._canActuate(zone) ||
      zone.id === undefined
    ) {
      return html``;
    }
    const lang = this.hass.language;
    const key = String(zone.id);

    // While a run is in progress, replace the duration picker + Run button with
    // a live countdown (or a "watering…" label for volume-bounded flow runs)
    // and a Stop button.
    const active = this._activeRun(zone);
    if (active) {
      const left = this._runSecondsLeft(active);
      return html`
        <div class="run-zone-control running">
          <span class="run-zone-countdown">
            <ha-icon icon="mdi:water-pump"></ha-icon>
            ${left === null
              ? localize("panels.zones.stop_zone.watering", lang)
              : this._formatCountdown(left)}
          </span>
          <button
            class="action-btn stop-btn"
            @click="${() => this._stopZone(zone)}"
          >
            <ha-icon icon="mdi:stop"></ha-icon>
            ${localize("panels.zones.stop_zone.stop", lang)}
          </button>
        </div>
      `;
    }

    // A distributor member is watered through its distributor. While that
    // distributor is mid-cycle the backend rejects a second run, so disable the
    // control and explain the wait rather than let the user fire a doomed run.
    const busy = this._distributorBusy(zone);

    return html`
      <div class="run-zone-control-wrap">
        <div
          class="run-zone-control"
          title="${localize("panels.zones.run_zone.help", lang)}"
        >
          <input
            class="run-zone-input"
            type="number"
            min="1"
            max="600"
            .value="${String(this._zoneRunMinutes(zone))}"
            ?disabled="${busy}"
            @input="${(e: Event) => {
              const v = Number((e.target as HTMLInputElement).value);
              this._runMinutes = { ...this._runMinutes, [key]: v };
            }}"
          />
          <span class="run-zone-unit"
            >${localize("panels.zones.run_zone.minutes", lang)}</span
          >
          <button
            class="action-btn"
            @click="${() => this._runZoneFor(zone)}"
            ?disabled="${this.isSaving || busy}"
          >
            <ha-icon icon="mdi:timer-play-outline"></ha-icon>
            ${localize("panels.zones.run_zone.run", lang)}
          </button>
        </div>
        ${busy
          ? html`<span class="run-zone-busy-hint">
              ${localize("panels.zones.run_zone.busy_hint", lang)}
            </span>`
          : ""}
      </div>
    `;
  }

  /** Format a remaining-seconds count as ``m:ss`` (or ``h:mm:ss``). */
  private _formatCountdown(totalSeconds: number): string {
    const s = Math.max(0, totalSeconds);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    const pad = (n: number) => String(n).padStart(2, "0");
    return h > 0 ? `${h}:${pad(m)}:${pad(sec)}` : `${m}:${pad(sec)}`;
  }

  render(): TemplateResult {
    if (!this.hass) return html``;

    if (this.isLoading) {
      return html`
        <ha-card header="${localize("panels.zones.title", this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${localize("common.loading-messages.general", this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;
    }

    const hasLinkedZones = this.zones.some(
      (z) => this._canActuate(z) && (z.duration ?? 0) > 0,
    );

    // First-time setup banner: shown when no zones exist yet.
    const isFirstTime = this.zones.length === 0;

    return html`
      ${isFirstTime
        ? this.hideSettingsLinks
          ? html`
              <ha-card>
                <div class="card-content description-text">
                  ${localize("panels.zones.no_items", this.hass.language)}
                </div>
              </ha-card>
            `
          : html`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
                      ${localize("wizard.title", this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${localize(
                        "wizard.setup_complete_banner",
                        this.hass.language,
                      )}
                    </div>
                  </div>
                  <button
                    class="action-btn setup-banner-btn"
                    @click="${() => {
                      this.dispatchEvent(
                        new CustomEvent("open-wizard", {
                          bubbles: true,
                          composed: true,
                        }),
                      );
                    }}"
                  >
                    ${localize("wizard.open_wizard", this.hass.language)}
                  </button>
                </div>
              </ha-card>
            `
        : ""}
      ${!isFirstTime ? this._renderOutlookBanner() : ""}
      ${!isFirstTime ? this._renderRainDelay() : ""}

      <!-- Zones header card: run-all operational actions -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${localize("panels.zones.title", this.hass.language)}
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${this.actionsMode === "full"
            ? html`
                <button
                  class="action-btn"
                  title="${localize(
                    "panels.zones.help.update_all",
                    this.hass.language,
                  )}"
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${localize(
                    "panels.zones.cards.zone-actions.actions.update-all",
                    this.hass.language,
                  )}
                </button>
                <button
                  class="action-btn"
                  title="${localize(
                    "panels.zones.help.calculate_all",
                    this.hass.language,
                  )}"
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${localize(
                    "panels.zones.cards.zone-actions.actions.calculate-all",
                    this.hass.language,
                  )}
                </button>
              `
            : ""}
          ${this.actionsMode !== "none"
            ? html`
                <button
                  class="action-btn"
                  raised
                  title="${localize(
                    "panels.zones.help.irrigate_all",
                    this.hass.language,
                  )}"
                  @click="${() => {
                    this._confirmIrrigate = "all";
                  }}"
                  ?disabled="${!hasLinkedZones || this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${localize(
                    "panels.zones.actions.irrigate_all",
                    this.hass.language,
                  )}
                </button>
              `
            : ""}
          ${!hasLinkedZones
            ? html`<span class="zones-top-note"
                >${localize(
                  "panels.info.cards.irrigate_now.no_linked_zones",
                  this.hass.language,
                )}</span
              >`
            : ""}
        </div>
      </ha-card>

      <!-- Irrigate confirmation dialog -->
      ${this._confirmIrrigate !== null
        ? html`
            <ha-dialog
              open
              @closed="${() => {
                this._confirmIrrigate = null;
              }}"
              heading="${localize(
                "panels.zones.confirm_irrigate.title",
                this.hass.language,
              )}"
            >
              <p>
                ${localize(
                  "panels.zones.confirm_irrigate.body",
                  this.hass.language,
                )}
              </p>
              <p>
                <strong>
                  ${this._confirmIrrigate === "all"
                    ? `${localize("panels.zones.confirm_irrigate.all_linked_zones", this.hass.language)} (${this._linkedZoneCount})`
                    : (this.zones.find(
                        (z) => z.id?.toString() === this._confirmIrrigate,
                      )?.name ?? this._confirmIrrigate)}
                </strong>
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
                    this._confirmIrrigate = null;
                  }}"
                >
                  ${localize("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${localize(
                    "panels.zones.labels.irrigate_now",
                    this.hass.language,
                  )}
                </button>
              </div>
            </ha-dialog>
          `
        : ""}

      <!-- Operation error banner -->
      ${this._operationError
        ? html`
            <ha-card class="error-banner-card">
              <div class="error-banner">
                <ha-icon
                  class="error-banner-icon"
                  icon="mdi:alert-circle-outline"
                ></ha-icon>
                <span class="error-banner-msg">${this._operationError}</span>
                <ha-icon-button
                  .path="${mdiClose}"
                  @click="${() => {
                    this._operationError = null;
                  }}"
                  aria-label="${localize(
                    "common.actions.cancel",
                    this.hass.language,
                  )}"
                ></ha-icon-button>
              </div>
            </ha-card>
          `
        : ""}

      <!-- Zone cards -->
      ${this.zones.map((zone, index) => this.renderZone(zone, index))}
    `;
  }

  static get styles(): CSSResultGroup {
    return css`
      ${globalStyle}

      /* At-a-glance decision line */
      .zone-decision {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 16px 12px;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1.35;
      }

      .zone-decision ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 22px;
      }

      .zone-decision.water {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
        color: var(--primary-color);
      }

      .zone-decision.ok {
        background: rgba(76, 175, 80, 0.12);
        color: var(--success-color, #2e7d32);
      }

      .zone-decision.neutral {
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
      }

      .zone-decision.unknown {
        background: rgba(255, 152, 0, 0.12);
        color: var(--warning-color, #ed6c02);
      }

      .zone-decision.skip {
        background: rgba(255, 152, 0, 0.12);
        color: var(--warning-color, #ed6c02);
      }

      /* Run fault — the strongest per-zone state (a run failed). */
      .zone-fault {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 16px 12px;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.35;
        background: rgba(244, 67, 54, 0.12);
        color: var(--error-color, #f44336);
        border-left: 4px solid var(--error-color, #f44336);
      }

      .zone-fault ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 22px;
      }

      /* Soil-moisture skip — informational, not an error. Same shape as the
         fault banner but a calm, muted blue tone (a skip is intended). */
      .zone-skip {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 16px 12px;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.35;
        background: rgba(var(--rgb-info-color, 3, 169, 244), 0.1);
        color: var(--info-color, var(--primary-color, #039be5));
        border-left: 4px solid var(--info-color, var(--primary-color, #039be5));
      }

      .zone-skip ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 22px;
      }

      /* Global outlook banner — tinted like the per-zone status banners so the
         two read at the same visual weight. */
      .outlook-card {
        border-left: 4px solid var(--primary-color);
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.06);
      }

      .outlook {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 14px 16px;
      }

      .outlook-line {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        font-size: 0.9rem;
        line-height: 1.35;
      }

      .outlook-line ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 20px;
      }

      .outlook-headline {
        font-size: 1rem;
        font-weight: 500;
      }

      .outlook-headline ha-icon {
        color: var(--primary-color);
      }

      .outlook-skip {
        color: var(--warning-color, #ed6c02);
      }

      .outlook-clear {
        color: var(--success-color, #2e7d32);
      }

      .outlook-dim {
        color: var(--secondary-text-color);
        font-weight: 400;
      }

      /* Tap-to-expand "why it will skip" toggle (works on touch + desktop) */
      .outlook-info-btn {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        background: transparent;
        border: none;
        color: var(--warning-color, #ed6c02);
        cursor: pointer;
        font: inherit;
        padding: 4px 6px;
        border-radius: 6px;
      }

      .outlook-info-btn:hover {
        background: rgba(255, 152, 0, 0.12);
      }

      .outlook-info-btn ha-icon {
        --mdc-icon-size: 18px;
      }

      .outlook-info-label {
        font-size: 0.8125rem;
        text-decoration: underline;
      }

      /* Expanded skip reasons */
      .outlook-skip-reasons {
        color: var(--warning-color, #ed6c02);
      }

      .skip-reasons {
        margin: 0;
        padding-left: 18px;
        font-size: 0.85rem;
      }

      .skip-reasons li {
        margin: 2px 0;
      }

      .skip-reasons-note {
        font-size: 0.8rem;
        font-style: italic;
      }

      .outlook-link {
        background: transparent;
        border: none;
        color: var(--primary-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0;
        text-decoration: underline;
      }

      /* Compact one-line status */
      .zone-status-line {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
      }

      .zone-status-line strong {
        color: var(--primary-text-color);
        font-weight: 500;
      }

      .status-sep {
        opacity: 0.5;
      }

      /* Read-only "live" estimate chip */
      .zone-estimate {
        cursor: help;
      }

      .estimate-tag {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.65;
      }

      /* Action bar */
      .zone-action-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 0;
        padding-bottom: 12px;
      }

      /* Custom-duration run control (WS-5) */
      .run-zone-control-wrap {
        display: inline-flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
        margin-left: auto;
      }

      .run-zone-control {
        display: inline-flex;
        align-items: center;
        gap: 6px;
      }

      /* The in-progress countdown branch isn't inside the wrap, so it keeps the
         right-alignment the wrap otherwise provides. */
      .run-zone-control.running {
        margin-left: auto;
      }

      /* Member busy-hint: the distributor is mid-cycle, so the run is blocked. */
      .run-zone-busy-hint {
        font-size: 0.8125rem;
        font-style: italic;
        color: var(--secondary-text-color);
        text-align: right;
        max-width: 320px;
        line-height: 1.3;
      }

      .run-zone-input {
        width: 56px;
        padding: 6px 8px;
        border: 1px solid var(--divider-color);
        border-radius: 6px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        font: inherit;
        text-align: right;
      }

      .run-zone-unit {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
      }

      /* In-progress run: countdown + Stop */
      .run-zone-countdown {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-variant-numeric: tabular-nums;
        font-weight: 600;
        color: var(--primary-color);
      }

      .run-zone-countdown ha-icon {
        --mdc-icon-size: 18px;
      }

      .action-btn.stop-btn {
        color: var(--error-color, #db4437);
        border-color: var(--error-color, #db4437);
      }

      /* Rain delay / vacation hold (WS-5) */
      .rain-delay-card.paused {
        border-left: 4px solid var(--warning-color, #ed6c02);
        background: rgba(255, 152, 0, 0.08);
      }

      .rain-delay {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        padding: 12px 16px;
      }

      .rain-delay ha-icon {
        flex-shrink: 0;
        color: var(--warning-color, #ed6c02);
        --mdc-icon-size: 22px;
      }

      .rain-delay-msg {
        flex: 1;
        font-size: 0.9rem;
        line-height: 1.35;
      }

      .rain-delay-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0 4px 4px;
        padding: 4px 0;
      }

      .rain-delay-label {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
      }

      .rain-delay-label ha-icon {
        --mdc-icon-size: 18px;
      }

      /* State badge */
      .zone-state-badge {
        font-size: 0.75rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        align-self: center;
        margin-left: auto;
      }

      .state-automatic {
        background: var(--success-color, #4caf50);
        color: white;
      }

      .state-manual {
        background: var(--accent-color, var(--primary-color));
        color: white;
      }

      .state-disabled {
        background: var(--disabled-color, #bdbdbd);
        color: white;
      }

      /* First-time setup banner */
      .setup-banner-card {
        border-left: 4px solid var(--primary-color);
      }

      .setup-banner {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        flex-wrap: wrap;
      }

      .setup-banner-icon {
        font-size: 2rem;
        flex-shrink: 0;
      }

      .setup-banner-content {
        flex: 1;
        min-width: 180px;
      }

      .setup-banner-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--primary-text-color);
        margin-bottom: 4px;
      }

      .setup-banner-desc {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
      }

      .setup-banner-btn {
        flex-shrink: 0;
      }

      .zones-top-actions {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
      }

      .zones-top-note {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        font-style: italic;
      }

      /* Dialog footer buttons */
      .dialog-footer {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        padding: 16px 0 8px;
        margin-top: 8px;
        border-top: 1px solid var(--divider-color);
      }

      .dialog-btn {
        background: transparent;
        border: 1px solid var(--primary-color);
        border-radius: 4px;
        color: var(--primary-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 8px 16px;
        transition: background 0.15s;
      }

      .dialog-btn:hover {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
      }

      .dialog-btn-primary {
        background: var(--primary-color);
        color: var(--text-primary-color, white);
      }

      .dialog-btn-primary:hover {
        opacity: 0.9;
        background: var(--primary-color);
      }

      /* Operation error banner */
      .error-banner-card {
        border-left: 4px solid var(--error-color, #f44336);
      }

      .error-banner {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 8px 8px 16px;
      }

      .error-banner-icon {
        color: var(--error-color, #f44336);
        flex-shrink: 0;
      }

      .error-banner-msg {
        flex: 1;
        color: var(--error-color, #f44336);
        font-size: 0.9rem;
        line-height: 1.4;
      }
    `;
  }
}

// Guarded define: both the admin panel bundle and the Lovelace card bundle
// register this element, and both can be loaded in the same document (panel +
// dashboard). Skip the second define instead of throwing.
if (!customElements.get("smart-irrigation-view-zones")) {
  customElements.define(
    "smart-irrigation-view-zones",
    SmartIrrigationViewZones,
  );
}

export { SmartIrrigationViewZones };
