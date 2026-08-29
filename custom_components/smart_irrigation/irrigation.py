"""Irrigation execution for the Smart Irrigation integration.

Extracted from __init__.py (Phase C2). The runner methods live on a mixin the
SmartIrrigationCoordinator inherits, so their bodies are unchanged — they still
use ``self`` to reach coordinator state (store, hass, skip-condition checks,
duration helpers). ``async_irrigate_now`` is the entry point that dispatches to
the rotating / sequential / parallel strategies based on config.
"""

import asyncio
import logging
import math
import uuid
from dataclasses import dataclass
from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .batch import is_batch_zone
from .duration_math import calibrated_flow_seconds, zone_run_duration
from .flow_metering import (
    FlowMeter,
    flow_is_totalizer,
    flow_learn_next_streak,
    flow_learn_resolve,
    flow_litres_from_total,
)
from .helpers import convert_between, normalize_zone_selection
from .localize import localize
from .opensprinkler import (
    entity_is_station,
    is_opensprinkler_zone,
    station_facts,
    station_facts_by_zone,
)
from .run_watch import run_is_paused, run_is_queue_bound, run_is_segmented
from .run_window import (
    TRACK_STATION,
    ZoneRun,
    nominal_demand_seconds,
    track_for_zone,
    zone_eligible_for_demand,
)

_LOGGER = logging.getLogger(__name__)

# Skip markers the bounded run log may sacrifice to keep a real run. Both
# repeat on a schedule the user did not ask to read about - the zone had no
# deficit, or it is still inside its days-between wait - so one of each is as
# informative as fifty. A skip carrying a FAULT is not here: that is a real
# event and is bounded like a run. siehe _record_run.
_EVICTABLE_SKIP_DETAILS = frozenset(
    {const.SKIP_REASON_NO_DEMAND, const.SKIP_REASON_DAYS_BETWEEN}
)

# How long (seconds) a zone stays flagged as "Smart Irrigation is driving this
# valve" after the runner opens it, so the experimental observed-watering
# observer does not also credit the bucket for a run SI already accounts for.
# Grace added on top of the run's own length: covers valve-confirm lag before
# the first "open" event and the final "close" event. The window must span the
# WHOLE run (not a fixed 30s) or a mid-run valve flap re-opening after it lapsed
# would be mistaken for external watering and double-credit the bucket.
SI_VALVE_SUPPRESS_MARGIN = 30

# Linked-entity states that count as "the valve actually opened" (switch on,
# valve open/opening). Mirrors binary_sensor._WATERING_STATES.
_VALVE_ON_STATES = ("on", "open", "opening")


@dataclass(frozen=True)
class _ZoneRunDecision:
    """One zone's answer to "do you water now, and for how long".

    ``resized`` distinguishes a duration recomputed from the live intra-day
    deficit from the stored daily one — only the former may credit above the
    daily target (see ``_run_ceiling``).
    """

    duration: float
    deficit: float
    ratio: float
    resized: bool


def _depletion_ratio(bucket: float, threshold: float) -> float:
    """``bucket / bucket_threshold`` — how far past its allowed depletion a zone is.

    Dimensionless, so zones with different allowed depletions compare correctly,
    and exactly 1.0 is the due line: the ranking key and the demand gate are the
    same quantity.

    A threshold of 0 or above configures no depletion allowance at all, so there
    is no scale to rank on; those zones all return 1.0 and are separated by the
    last-irrigation tie-break instead of by a fabricated number.
    """
    try:
        if threshold < 0:
            return float(bucket) / float(threshold)
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return 1.0


class IrrigationRunnerMixin:
    """Irrigation execution strategies for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    def _note_si_valve(self, zone_id, run_seconds: float = 0.0) -> None:
        """Flag that SI itself is opening this zone's valve.

        The observed-watering observer (ObservedWateringMixin) checks this so it
        only credits the bucket for runs SI did NOT start (manual taps,
        automations). No-op unless that experimental feature is wired up.

        ``run_seconds`` is how long this run/slot will hold the valve open; the
        suppression window spans that plus a fixed grace, so a valve that flaps
        (on → unavailable → on) or reports "open" slowly mid-run stays suppressed
        for the entire run instead of only the first 30s.
        """
        until = getattr(self, "_si_driven_until", None)
        if until is not None:
            window = (run_seconds or 0.0) + SI_VALVE_SUPPRESS_MARGIN
            until[int(zone_id)] = self.hass.loop.time() + window

    @staticmethod
    def _zone_target_bucket(zone: dict) -> float:
        """Bucket level (display units) a completed run should leave the zone at.

        0.0 normally (full replenish); the rain-covered remainder when the
        experimental forecast-weighting feature trimmed the last calculation.
        """
        return zone.get(const.ZONE_IRRIGATION_TARGET_BUCKET) or 0.0

    # --- Rain delay / vacation hold (WS-5) ----------------------------------

    def _rain_delay_until_dt(self):
        """Parse the configured hold into an aware datetime, or None if unset."""
        raw = getattr(self.store.config, "rain_delay_until", None)
        if not raw:
            return None
        parsed = dt_util.parse_datetime(raw)
        if parsed is None:
            return None
        return dt_util.as_local(parsed) if parsed.tzinfo is None else parsed

    def _rain_delay_active(self) -> bool:
        """True when a hold is set and still in the future."""
        until = self._rain_delay_until_dt()
        return until is not None and until > dt_util.now()

    async def async_set_rain_delay(self, until_iso: str | None) -> None:
        """Set (or clear, when None) the rain-delay / vacation hold."""
        await self.store.async_update_config({const.CONF_RAIN_DELAY_UNTIL: until_iso})
        _LOGGER.info("Rain delay set until %s", until_iso)
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated")
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")

    async def async_clear_rain_delay(self) -> None:
        """Resume automatic irrigation (clear any active hold)."""
        await self.async_set_rain_delay(None)

    async def async_delay_hours(self, hours: float) -> None:
        """Quick-hold: pause automatic irrigation for ``hours`` from now."""
        until = dt_util.now() + timedelta(hours=hours)
        await self.async_set_rain_delay(until.isoformat())

    def _run_trigger(self, zone_id) -> str:
        """Run-log trigger for a zone: ``manual`` for a custom run, else schedule.

        Consumes the one-shot marker set by ``async_run_zone`` so the next
        scheduled run of the same zone is logged as a schedule again.
        """
        manual = getattr(self, "_manual_run_zones", None)
        if manual and int(zone_id) in manual:
            manual.discard(int(zone_id))
            return "manual"
        return "schedule"

    # --- In-progress run tracking + stop action -----------------------------

    def _active_run_registry(self) -> dict:
        """Lazily-created ``{zone_id: {stop, started_at, ends_at}}`` map.

        Tracks the zones with a valve currently held open by the runner so a
        user can stop a run mid-way and the dashboard can show a live countdown.
        """
        reg = getattr(self, "_active_runs", None)
        if reg is None:
            reg = self._active_runs = {}
        return reg

    def _register_active_run(
        self, zone_id, duration_seconds, *, has_end: bool, queued: bool = False
    ):
        """Mark a zone's run as in-progress; return its stop ``asyncio.Event``.

        ``has_end`` is True for time-bounded (synthetic / manual) runs, so the
        dashboard can render a countdown to ``ends_at``; flow-metered runs are
        volume-bounded (unknown finish time) and register without an end.
        Dispatches ``_config_updated`` so the panel surfaces the Stop control.

        ``queued`` marks an entry that a chain has claimed but whose valve is not
        open yet, so the panel can say so instead of claiming water is flowing.
        The default is False because every caller that opens a valve wants the
        entry to read as watering, including the one overwriting a claim.

        A zone claimed by a chain (:meth:`_claim_chain_zones`) is already in the
        registry when its own turn comes, so the existing stop event is carried
        over rather than replaced. Minting a fresh one here would discard a stop
        the user requested while the zone was still queued, and the valve would
        then open anyway.
        """
        reg = self._active_run_registry()
        zid = int(zone_id)
        existing = reg.get(zid)
        event = existing["stop"] if existing else asyncio.Event()
        now = dt_util.now()
        ends_at = (
            (now + timedelta(seconds=duration_seconds)).isoformat()
            if has_end and duration_seconds
            else None
        )
        reg[zid] = {
            "stop": event,
            "started_at": now.isoformat(),
            "ends_at": ends_at,
            "queued": queued,
        }
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zid)
        return event

    def _set_run_queued(self, zone_id, queued: bool) -> None:
        """Flip a tracked run between claimed-and-waiting and valve-open.

        A rotation returns to the same zone for slot after slot, so its entry
        alternates rather than being registered once. Mutates in place — going
        through :meth:`_register_active_run` would restamp ``started_at`` on
        every slot boundary and the panel would show the run beginning again.
        Only dispatches on a real change, so an unchanged state costs nothing.
        """
        reg = getattr(self, "_active_runs", None) or {}
        entry = reg.get(int(zone_id))
        if entry is None or bool(entry.get("queued")) is queued:
            return
        entry["queued"] = queued
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", int(zone_id))

    def _claim_chain_zones(self, zones: list) -> list:
        """Register every zone a chain is about to walk, and return their ids.

        ``_active_runs`` answers "does this zone have a run in flight?" for the
        duplicate-dispatch guard, and a sequential (or rotating) chain only ever
        holds ONE valve open. Registering at valve-open therefore made the zones
        queued behind the open one invisible to that guard: a second dispatch
        arriving mid-chain skipped only the zone currently watering and started a
        second concurrent chain over all the rest, watering each of them twice.

        So the registry means "claimed by an in-flight run", not "valve open
        now". Each zone clears as it completes (``_run_valve_metered``'s finally,
        or the rotation's own per-zone clears); the chain sweeps the remainder,
        so a chain cut short or one that raises leaves nothing claimed.

        Claims register as ``queued``. The registry drives the panel as well as
        the guard, and there it had always meant "valve open now" — without the
        distinction a seven-zone sequential chain shows all seven zones watering
        from the moment it starts.
        """
        claimed = []
        for zone in zones:
            zid = int(zone[const.ZONE_ID])
            self._register_active_run(zid, 0, has_end=False, queued=True)
            claimed.append(zid)
        return claimed

    async def _release_chain_zones(self, zone_ids) -> None:
        """Clear any claim a chain still holds (already-finished zones are gone).

        A claimed zone defers its calculation (``async_calculate_zone`` gives way
        to a run in flight), and for a zone the chain reaches the run's own
        teardown picks that deferral back up. A zone the chain never reaches — a
        stop, or an exception — has no teardown, so the deferral is run here once
        the claim is gone. Skipping it left the zone's duration stale until the
        next scheduled calculate.
        """
        for zid in zone_ids:
            self._unregister_active_run(zid)
        for zid in zone_ids:
            await self.async_run_deferred_calculation(zid)

    def _unregister_active_run(self, zone_id) -> None:
        """Clear a zone's in-progress marker (run finished or was stopped)."""
        reg = getattr(self, "_active_runs", None)
        if reg and int(zone_id) in reg:
            del reg[int(zone_id)]
            async_dispatcher_send(
                self.hass, const.DOMAIN + "_config_updated", int(zone_id)
            )

    def _persisted_self_closing_runs(self) -> list:
        """The in-flight self-closing runs, read synchronously.

        ``self_closing._sc_active_runs`` is async because it goes through
        ``async_get_config``; this reads the live ``Config`` object instead so
        the synchronous dashboard payload can include them. The isinstance
        guard matters: a test double's config is often a bare ``Mock()``, whose
        every attribute answers with another Mock that would then be iterated
        as if it were the list.
        """
        runs = getattr(getattr(self.store, "config", None), "active_valve_runs", None)
        return runs if isinstance(runs, list) else []

    def _self_closing_run_window(self, record: dict):
        """``(started_at, ends_at)`` ISO strings for one persisted run.

        Mirrors ``_sc_run_elapsed``'s rule for when a run is actually watering:
        an OpenSprinkler run sits in the controller's queue between dispatch
        and its first observed second, so until the station is seen running
        there is no finish to count down to. ``ends_at`` is None there, which
        the panel already renders as a Stop control without a countdown — the
        same shape a volume-bounded flow run registers with.

        A run recorded as SEGMENTS is not one contiguous stretch, so its finish
        cannot be worked out from its start either. Counting down from the
        observed start charged a pause to the user as if it were water: the
        panel kept ticking while the valve was shut, and after a resume it was
        ahead of the controller by the whole length of the pause. Reported from
        the field against v2026.08.13 (issue #88). The accounting was always
        right — ``_sc_run_elapsed`` sums the watering segments — and only this,
        the number the user actually looks at, was still contiguous.
        """
        observed = record.get(const.RUN_OBSERVED_START)
        started_raw = observed or record.get(const.RUN_STARTED)
        started = dt_util.parse_datetime(started_raw) if started_raw else None
        if started is None:
            return None, None
        started = dt_util.as_local(started)
        queued = run_is_queue_bound(record)
        planned = float(record.get(const.RUN_PLANNED_SECONDS) or 0)
        if planned <= 0 or queued:
            return started.isoformat(), None
        if run_is_segmented(record):
            if not record.get(const.RUN_SEGMENT_STARTED):
                # Paused: no segment is open, the controller is holding the
                # remaining time, and nothing here can say when it will hand it
                # back. No countdown rather than a wrong one — the same shape a
                # queued run and a volume-bounded run already register with.
                return started.isoformat(), None
            # Watering: the finish is whatever is LEFT, measured from now. The
            # segments already banked are behind us in wall-clock terms, so they
            # cannot be projected forward from the observed start.
            remaining = max(0.0, planned - self._sc_run_elapsed(record))
            return (
                started.isoformat(),
                (dt_util.now() + timedelta(seconds=remaining)).isoformat(),
            )
        return started.isoformat(), (started + timedelta(seconds=planned)).isoformat()

    def get_active_runs(self) -> dict:
        """Return ``{zone_id: {started_at, ends_at, queued}}`` for runs in progress.

        TWO registries feed this, and for a long time only one of them did. The
        metered/classic runner tracks its zones in the in-memory
        ``_active_runs`` map, but a self-closing zone never enters it: its run
        is fire-and-forget and lives in the persisted ``CONF_ACTIVE_VALVE_RUNS``
        list instead (``self_closing._sc_add_run``). The panel drives BOTH the
        Stop control and the live countdown off this dict, so omitting the
        persisted half made a watering self-closing zone look completely idle —
        no Stop button, no remaining duration — while the valve was open, even
        though ``binary_sensor.<zone>_watering_now`` (which watches the linked
        entity directly) correctly read on. See issue #83.

        The ``queued`` flag separates the two things the in-memory registry has
        held since a chain started claiming its whole zone list up front: a zone
        whose valve is open, and one waiting its turn behind it. Both must be in
        here — the guard reads this and so does ``async_stop_all_zones``, which
        has to reach a queued zone — but the panel renders them differently.

        A persisted run carries the same two states, plus a third. It is
        ``queued`` while its controller has taken the run on but not reached the
        zone (``run_is_queue_bound``), and ``paused`` while the controller has
        started it and is holding the remaining time (``run_is_paused``). Both
        were reported here as plain watering until issue #97: a batch dispatch
        records a run for EVERY zone at once, so a seven-zone irrigation read as
        seven zones watering simultaneously from the moment the plan was sent,
        and a paused zone was indistinguishable from a watering one.

        All three states are stoppable and all three still hold the zone against
        a second dispatch — this changes what the panel is told, not what any
        guard does with it.
        """
        reg = getattr(self, "_active_runs", None) or {}
        runs = {
            str(zid): {
                "started_at": d["started_at"],
                "ends_at": d["ends_at"],
                "queued": bool(d.get("queued")),
                # The in-memory runner owns its own valve, so it has no pause to
                # report: only a controller that keeps the remaining time can
                # pause, and those runs live in the persisted list below.
                "paused": False,
            }
            for zid, d in reg.items()
        }
        for record in self._persisted_self_closing_runs():
            zone_id = record.get(const.RUN_ZONE_ID)
            # The in-memory entry is the live one; a persisted record must never
            # shadow it (a distributor member can hold both).
            if zone_id is None or str(zone_id) in runs:
                continue
            started_at, ends_at = self._self_closing_run_window(record)
            if started_at is None:
                continue
            runs[str(zone_id)] = {
                "started_at": started_at,
                "ends_at": ends_at,
                "queued": run_is_queue_bound(record),
                "paused": run_is_paused(record),
            }
        return runs

    def _run_stopped(self, zone_id) -> bool:
        """True if a stop was requested for this zone's in-progress run."""
        reg = getattr(self, "_active_runs", None) or {}
        d = reg.get(int(zone_id))
        return bool(d and d["stop"].is_set())

    async def _sleep_or_stopped(self, zone_id, seconds: float) -> bool:
        """Sleep for ``seconds``; return True if a stop was requested.

        A stop is detected before and after the sleep. The valve is turned off
        immediately by :meth:`async_stop_zone`, so this only governs how soon the
        run loop notices and settles the accounting — within one poll interval.
        Implemented with a plain sleep (not ``wait_for``) so it stays cheap and
        unit-testable when ``asyncio.sleep`` is patched out.
        """
        reg = getattr(self, "_active_runs", None) or {}
        d = reg.get(int(zone_id))
        if d is not None and d["stop"].is_set():
            return True
        await asyncio.sleep(seconds)
        return bool(d is not None and d["stop"].is_set())

    async def async_stop_zone(self, zone_id) -> None:
        """Stop an in-progress run for a zone immediately.

        Signals the run loop to break (so it commits the water delivered so far
        and logs a partial run) and, as a safety net, turns the linked valve off
        directly — covering the case where no run is tracked (e.g. an externally
        opened valve, or a run started before a restart).
        """
        zid = int(zone_id)
        # Before the run in flight is finalised, or the finalisation advances the
        # cycle straight back onto this zone.
        self._os_drop_from_cycle(zid)
        if await self._sc_maybe_stop(zid):
            return
        reg = getattr(self, "_active_runs", None) or {}
        tracked = reg.get(zid)
        if tracked is not None:
            tracked["stop"].set()
        zone = self.store.get_zone(zid) or {}
        entity_id = zone.get(const.ZONE_LINKED_ENTITY)
        if entity_id:
            domain = entity_id.split(".")[0]
            await self.hass.services.async_call(
                domain, "turn_off", {"entity_id": entity_id}
            )
        _LOGGER.info("Stop requested for zone %s", zid)

    async def async_stop_all_zones(self) -> None:
        """Stop every zone with an in-progress run.

        Sourced from ``get_active_runs`` rather than ``_active_runs`` directly,
        so self-closing zones are covered too. The in-memory registry alone
        silently skipped every one of them — the second symptom of the same
        omission behind issue #83, and the worse one: "stop all zones" reported
        success while leaving those valves open.
        """
        for zid in list(self.get_active_runs()):
            await self.async_stop_zone(int(zid))

    # --- Valve-run verification + per-zone fault state (WS-1) ---------------

    def _set_zone_fault(self, zone_id, reason: str) -> None:
        """Record that a run for this zone failed (in-memory, like skip eval).

        Dispatches ``_faults_updated`` so the per-zone / hub "problem" binary
        sensors refresh. The fault clears on the next successful run.
        """
        faults = getattr(self, "_zone_faults", None)
        if faults is None:
            faults = self._zone_faults = {}
        faults[int(zone_id)] = {
            "reason": reason,
            "timestamp": dt_util.now().isoformat(),
        }
        _LOGGER.warning("Zone %s irrigation fault: %s", zone_id, reason)
        self._notify_fault_listeners(int(zone_id))

    def _fire_zone_problem(self, zone_id, zone: dict, entity_id, reason: str) -> None:
        """Announce a zone's run failure on the bus.

        The payload is what user automations bind to, so its shape lives in one
        place rather than being rebuilt at each site that can fail a run.
        """
        self.hass.bus.async_fire(
            f"{const.DOMAIN}_{const.EVENT_ZONE_PROBLEM}",
            {
                "zone_id": zone_id,
                "zone": (zone or {}).get(const.ZONE_NAME),
                "entity_id": entity_id,
                "reason": reason,
            },
        )

    def _clear_zone_fault(self, zone_id) -> None:
        """Clear any recorded fault for this zone (a run just succeeded)."""
        faults = getattr(self, "_zone_faults", None)
        if faults and int(zone_id) in faults:
            del faults[int(zone_id)]
            self._notify_fault_listeners(int(zone_id))

    def _notify_fault_listeners(self, zone_id: int) -> None:
        """Refresh the problem binary sensors AND the dashboard outlook.

        ``_faults_updated`` drives the per-zone / hub problem sensors;
        ``_update_frontend`` is the signal the panel's subscription re-fetches
        on (the outlook now carries ``zone_faults``), so the fault chip appears
        and clears live without a dedicated WS command.
        """
        async_dispatcher_send(self.hass, const.DOMAIN + "_faults_updated", zone_id)
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")

    def get_zone_fault(self, zone_id):
        """Return ``{reason, timestamp}`` for a faulted zone, else None."""
        return (getattr(self, "_zone_faults", None) or {}).get(int(zone_id))

    def get_zone_faults(self) -> dict:
        """Return the full ``{zone_id: {reason, timestamp}}`` fault map."""
        return dict(getattr(self, "_zone_faults", None) or {})

    # --- Per-zone soil-moisture wet-veto (skip condition) ------------------

    def _set_zone_skip(self, zone_id, entity_id, observed, threshold) -> None:
        """Record that a zone was skipped this run because it read wet.

        In-memory, mirroring ``_zone_faults``; surfaced in the outlook so the
        dashboard can show *why* the zone did not water. Dispatches
        ``_update_frontend`` so the panel refreshes without a dedicated WS call.
        """
        skips = getattr(self, "_zone_skips", None)
        if skips is None:
            skips = self._zone_skips = {}
        skips[int(zone_id)] = {
            "reason": const.SKIP_REASON_SOIL_MOISTURE,
            "observed": observed,
            "threshold": threshold,
            "entity_id": entity_id,
            "timestamp": dt_util.now().isoformat(),
        }
        self._notify_skip_listeners(int(zone_id))

    def _clear_zone_skip(self, zone_id) -> None:
        """Clear any recorded soil-moisture skip for this zone."""
        skips = getattr(self, "_zone_skips", None)
        if skips and int(zone_id) in skips:
            del skips[int(zone_id)]
            self._notify_skip_listeners(int(zone_id))

    def _notify_skip_listeners(self, zone_id: int) -> None:
        """Refresh the dashboard outlook after a skip record changes."""
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")

    def get_zone_skips(self) -> dict:
        """Return the full ``{zone_id: {reason, observed, threshold, ...}}`` map."""
        return dict(getattr(self, "_zone_skips", None) or {})

    async def _apply_soil_moisture_veto(self, zones: list) -> list:
        """Skip zones whose soil-moisture sensor reads wetter than the threshold.

        Per-zone, AUTOMATIC-path only (the sole caller, ``_irrigate_linked_entities``,
        is only reached from the scheduler; manual runs bypass it). For each zone
        with BOTH a configured ``soil_moisture_sensor`` and a numeric
        ``soil_moisture_threshold``: read the sensor; when the reading is a finite
        number strictly greater than the threshold (moister than), the zone is
        vetoed — bucket reset to 0 (re-anchored to field capacity so the open-loop
        model doesn't later over-water to chase a phantom deficit), a
        ``zone_skipped`` event fired, the per-zone skip recorded, and the zone
        dropped from this run. Missing sensor, missing threshold, or an
        unavailable/non-numeric reading FAIL OPEN (kept, waters per ET): a dead
        sensor must never silently stop irrigation.
        """
        out = []
        for z in zones:
            sensor = z.get(const.ZONE_SOIL_MOISTURE_SENSOR)
            threshold = z.get(const.ZONE_SOIL_MOISTURE_THRESHOLD)
            if not sensor or threshold is None:
                out.append(z)  # feature off for this zone
                continue
            state = self.hass.states.get(sensor)
            observed = None
            if state is not None and state.state not in (
                "unavailable",
                "unknown",
                None,
                "",
            ):
                try:
                    observed = float(state.state)
                except (ValueError, TypeError):
                    observed = None
            if observed is None or not math.isfinite(observed):
                # fail-open: unreadable OR non-finite (inf/nan) — a broken sensor
                # must never veto forever (that would be the fail-closed trap).
                out.append(z)
                continue
            if observed > float(threshold):
                await self._veto_zone_soil_moisture(
                    z, sensor, observed, float(threshold)
                )
                continue  # dropped from this run
            self._clear_zone_skip(z.get(const.ZONE_ID))
            out.append(z)  # dry enough -> water
        return out

    async def _veto_zone_soil_moisture(self, zone, sensor, observed, threshold) -> None:
        """Re-anchor the vetoed zone's bucket, fire the event, record the skip."""
        zone_id = zone.get(const.ZONE_ID)
        # Reset the bucket to 0 (deficit -> 0, field-capacity anchor) via the same
        # path as the reset_bucket service; respects maximum_bucket clamping.
        await self.async_update_zone_config(
            zone_id=zone_id,
            data={const.ATTR_SET_BUCKET: {}, const.ATTR_NEW_BUCKET_VALUE: 0},
        )
        self._set_zone_skip(zone_id, sensor, observed, threshold)
        self.hass.bus.async_fire(
            f"{const.DOMAIN}_{const.EVENT_ZONE_SKIPPED}",
            {
                "zone_id": zone_id,
                "zone": zone.get(const.ZONE_NAME),
                "entity_id": sensor,
                "reason": const.SKIP_REASON_SOIL_MOISTURE,
                "observed": observed,
                "threshold": threshold,
            },
        )
        _LOGGER.info(
            "Zone %s skipped: soil moisture %.1f > threshold %.1f; bucket reset to 0",
            zone_id,
            observed,
            threshold,
        )
        # Persist a per-zone "skipped" entry in the run history (Recent runs list),
        # so the veto is visible and survives restarts — the same run-log mechanism
        # the rain-delay skip uses. The detail is the reason code, localized by the
        # frontend history card via panels.zones.outlook.checks.<reason>.
        await self._record_run(
            zone_id,
            result=const.RUN_RESULT_SKIPPED,
            detail=const.SKIP_REASON_SOIL_MOISTURE,
        )

    async def _confirm_valve_running(self, zone_id, entity_id, retry: bool = True):
        """Confirm a freshly-opened linked entity actually reports an on-state.

        Returns True if confirmed on within the grace window, False if it stayed
        off the whole time, or None when the entity is not readable (unknown /
        unavailable / missing) so verification cannot be performed — write-only
        valves are never penalised.

        Many valves (sleepy Zigbee/Tuya timers) actuate but report their new
        state back slowly, or silently drop the first command. To cope we (a)
        poll for a generous ``VALVE_CONFIRM_TIMEOUT`` window and (b) re-send the
        open once, ``VALVE_CONFIRM_RETRY_AT`` seconds in, if still unconfirmed.
        A False result no longer aborts the run — the valve may well be open, so
        callers proceed and just surface it.

        ``retry=False`` polls without ever re-sending the open. Self-closing mode
        passes this: HA must not re-actuate a self-closing valve mid-run, or it
        would reset the hardware countdown to a fresh full duration.
        """
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unavailable", "unknown"):
            return None  # not verifiable — don't fault write-only valves
        domain = entity_id.split(".")[0]
        retried = False
        waited = 0.0
        while True:
            state = self.hass.states.get(entity_id)
            if state is not None and state.state in _VALVE_ON_STATES:
                return True
            if waited >= const.VALVE_CONFIRM_TIMEOUT:
                return False
            if retry and not retried and waited >= const.VALVE_CONFIRM_RETRY_AT:
                retried = True
                _LOGGER.debug(
                    "Valve '%s' not confirmed after %.0fs — re-sending open",
                    entity_id,
                    waited,
                )
                await self.hass.services.async_call(
                    domain, "turn_on", {"entity_id": entity_id}
                )
            await asyncio.sleep(const.VALVE_CONFIRM_POLL)
            waited += const.VALVE_CONFIRM_POLL

    # NB: no @callback here. It used to carry one, which is wrong on a coroutine
    # function — @callback marks a SYNCHRONOUS function as safe to invoke
    # directly in the event loop, and HA's job-scheduling helpers read that flag
    # to decide not to await. It was inert only because the single caller
    # (scheduler.py) awaits this directly; routing it through async_add_job would
    # have had HA call it and drop the coroutine on the floor, silently skipping
    # every irrigation.
    async def _irrigate_linked_entities(
        self, zone_ids=None, *, order=None, deadline=None
    ) -> bool:
        """Directly control linked valve/switch entities for zones needing irrigation.

        ``zone_ids`` optionally restricts to a schedule's target zones (an
        iterable of ids, or None/"all" for every eligible zone).

        ``order`` is a fitted run's priority order: an explicit list of zone ids
        that both restricts the run to those zones and waters them in that
        sequence. Without it the run keeps store order and every due zone, which
        is the unfitted behaviour. ``deadline`` is the UTC moment the run must
        be finished by; it truncates whatever is still running rather than
        selecting, and both are None unless a schedule opted into fitting.

        Returns ``True`` iff at least one real run was dispatched (self-closing
        service and/or the sequencing task), ``False`` on every no-water path
        (no candidates, rain delay, all soil-vetoed, live-estimate left nothing).
        The scheduled caller gates ``_reset_days_since_irrigation`` on this so a
        dry run doesn't fool the days-between guard (review finding A).
        """
        zones = await self.store.async_get_zones()
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}
        if order is not None:
            # A fitted run has already decided both the membership and the
            # sequence, so it supersedes the schedule's zone target rather than
            # intersecting with it — the selection was computed from that same
            # target to begin with.
            rank_of = {int(zid): i for i, zid in enumerate(order)}
            target = set(rank_of)
            zones = sorted(
                (z for z in zones if int(z.get(const.ZONE_ID)) in rank_of),
                key=lambda z: rank_of[int(z.get(const.ZONE_ID))],
            )

        # Live-estimate watering (experimental): when on, the per-zone trigger is
        # the intra-day live deficit (decided in _apply_live_durations), so the
        # frozen daily duration + stored daily bucket are NOT pre-filters here —
        # a run the daily calc didn't approve can still start on intra-day demand.
        # When off, the classic daily gate (duration > 0 AND bucket below
        # threshold) selects candidates, byte-identical to before.
        live_gate = getattr(self.store.config, "live_estimate_enabled", False) is True
        # Iter ND-3 (Plan Task 3): targeted + automatic-eligible zones this
        # scheduled run is responsible for, BEFORE the demand gate. Splitting the
        # old single comprehension in two lets the no-demand transparency log
        # (below) name exactly the zones that were evaluated but had no deficit.
        # Same predicate as before, minus the demand clause.
        #
        # Iter Task 2 (Plan D): a distributor member zone (distributor_id
        # set, including 0 — hence `is None`, not `not z.get(...)`, since
        # `not 0` is truthy and would wrongly re-include distributor 0's
        # members) is watered exclusively by its distributor's own cycle
        # (shared inlet valve). Excluding it here prevents the normal
        # linked-entity path from double-driving a member zone in
        # parallel with the distributor engine.
        targeted_eligible = [
            z
            for z in zones
            if z.get(const.ZONE_DISTRIBUTOR_ID) is None
            and (z.get(const.ZONE_LINKED_ENTITY) or self._sc_is_self_closing(z))
            and z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
            and (target is None or int(z.get(const.ZONE_ID)) in target)
        ]
        # Single-flight: a zone already being watered is not a candidate. Dropped
        # HERE rather than after the demand gate so the no-demand transparency log
        # below does not report a running zone as having had no deficit. The demand
        # gate is NOT a substitute — it only rejects a second dispatch once the
        # first run has credited the bucket, which a classic run does not do until
        # its first RUN_COMMIT_INTERVAL tick and Irrigate-now / run_zone never
        # consult at all. See tests/test_run_in_flight.py.
        targeted_eligible = self._drop_zones_already_running(targeted_eligible)
        zones_to_irrigate = [
            z
            for z in targeted_eligible
            if live_gate
            or (
                (z.get(const.ZONE_DURATION) or 0) > 0
                and (z.get(const.ZONE_BUCKET) or 0)
                < (z.get(const.ZONE_BUCKET_THRESHOLD) or 0)
            )
        ]

        # Iter ND-3: opt-in transparency (classic gate). Every targeted-eligible
        # zone that is NOT due had no demand. Log it here — BEFORE the "nothing
        # due" return below — so the satisfied-bucket case leaves a trace. The
        # helper is gated on config + rain-delay + same-day dedup, so paused runs
        # never double-log. Under live_gate the demand decision is deferred to
        # _apply_live_durations, so that set is logged there instead (see below).
        # N1: gate the whole computation on the flag so the off-path (the default)
        # never builds these sets — the helper is a no-op when off, but its
        # arguments are evaluated regardless.
        if not live_gate and getattr(self.store.config, "log_no_demand", False):
            _watered_ids = {int(z.get(const.ZONE_ID)) for z in zones_to_irrigate}
            await self._record_no_demand_skips(
                [
                    int(z.get(const.ZONE_ID))
                    for z in targeted_eligible
                    if int(z.get(const.ZONE_ID)) not in _watered_ids
                ]
            )

        if not zones_to_irrigate:
            _LOGGER.debug(
                "No zones with linked entities and duration > 0 to irrigate directly"
            )
            return False

        # Rain delay / vacation hold (WS-5): a user-set, time-boxed pause of all
        # AUTOMATIC irrigation. Explicit manual runs (async_irrigate_now /
        # async_run_zone) bypass this on purpose; only the scheduled path is gated.
        if self._rain_delay_active():
            _LOGGER.info(
                "Irrigation paused (rain delay until %s); skipping scheduled run",
                self._rain_delay_until_dt(),
            )
            await self._record_skipped_run(zone_ids, const.SKIP_REASON_PAUSED)
            return False

        # Per-zone soil-moisture wet-veto: drop zones already wet enough (and
        # re-anchor their bucket). Automatic path only — manual runs never reach
        # here. Fail-open on an unreadable sensor.
        zones_to_irrigate = await self._apply_soil_moisture_veto(zones_to_irrigate)
        if not zones_to_irrigate:
            _LOGGER.debug("Soil-moisture veto left no zones needing water")
            return False

        zones_to_irrigate = await self._apply_live_durations(zones_to_irrigate)

        # Iter ND-3: opt-in transparency (live-estimate gate). The zones the live
        # estimate dropped for no live deficit. Exclude soil-vetoed zones — they
        # already logged soil_moisture at _apply_soil_moisture_veto above.
        if live_gate and getattr(self.store.config, "log_no_demand", False):
            _vetoed_ids = set(self.get_zone_skips().keys())
            _watered_ids = {int(z.get(const.ZONE_ID)) for z in zones_to_irrigate}
            await self._record_no_demand_skips(
                [
                    int(z.get(const.ZONE_ID))
                    for z in targeted_eligible
                    if int(z.get(const.ZONE_ID)) not in _watered_ids
                    and int(z.get(const.ZONE_ID)) not in _vetoed_ids
                ]
            )

        if not zones_to_irrigate:
            _LOGGER.debug("Live-estimate duration left no zones needing water")
            return False

        # Days-between guard, per zone. Evaluated here rather than as a
        # whole-run skip so a zone that has served its wait still waters when a
        # zone watered more recently has not. Off by default
        # (days_between_irrigation = 0), and the setting is read first so the
        # default path costs nothing.
        days_between = self._days_between_setting()
        if days_between > 0:
            held = [
                z
                for z in zones_to_irrigate
                if self._zone_days_between_blocked(z, days_between)
            ]
            if held:
                _LOGGER.info(
                    "Days-between guard (%s days) holds zones %s back this run",
                    days_between,
                    [z.get(const.ZONE_ID) for z in held],
                )
                held_ids = {int(z.get(const.ZONE_ID)) for z in held}
                # Before the filter below drops them: past this point the run
                # has no record that these zones ever wanted water, and every
                # zone being held returns out of the guard entirely.
                await self._record_days_between_skips(sorted(held_ids))
                zones_to_irrigate = [
                    z
                    for z in zones_to_irrigate
                    if int(z.get(const.ZONE_ID)) not in held_ids
                ]
            if not zones_to_irrigate:
                _LOGGER.debug("Days-between guard left no zones needing water")
                return False

        await self._dispatch_by_mode(
            zones_to_irrigate, trigger="schedule", deadline=deadline
        )
        # Past the veto+live gates with a non-empty set: at least one real run
        # (self-closing and/or the sequencing task) was dispatched.
        return True

    async def _dispatch_by_mode(
        self, zones: list, *, trigger: str, deadline=None
    ) -> None:
        """Start a set of zones, each by the path its actuation mode needs.

        Master (pump): the hold is taken for the DISPATCH itself. It brings the
        master up before the first valve and, crucially, keeps it up in the
        window between dispatching work and that work taking its own holds —
        otherwise a release could land in the gap and end the cycle under a
        starting run.

        Self-closing zones delegate the run to their own service (the valve owns
        the close), so they bypass the linked-entity sequencing; each takes its
        own hold, released when its run finalises. Stations go through their own
        dispatcher because one controller can run several at once, so
        zone_sequencing has to be applied there rather than left to the hardware.

        ``deadline`` is the UTC moment a fitted run must be finished by. Only
        the sequencing path can honour it, under all three of its modes, because
        it is the only one that still holds the run when the deadline arrives.
        Self-closing zones and stations have handed the close to their own
        hardware by then, so a run of theirs that the selection could not fit
        runs to its full length and finishes past the target.
        """
        cycle_token = f"cycle:{uuid.uuid4().hex[:8]}"
        await self.async_master_acquire(cycle_token)
        try:
            self_closing = [z for z in zones if self._sc_is_self_closing(z)]
            for z in self_closing:
                if is_opensprinkler_zone(z) or is_batch_zone(z):
                    continue
                await self.async_run_self_closing(z, trigger=trigger)
            await self.async_dispatch_opensprinkler_zones(
                [z for z in self_closing if is_opensprinkler_zone(z)],
                trigger=trigger,
            )
            # Batch zones go out as ONE call carrying the whole ordered plan, so
            # they are handed over as a set rather than looped over here. Guarded
            # on the set being non-empty, like the linked-entity branch below: an
            # install with no batch zones — which is every install today — never
            # enters this mode's code at all.
            batched = [z for z in self_closing if is_batch_zone(z)]
            if batched:
                await self.async_dispatch_batch_zones(batched, trigger=trigger)
            linked = [z for z in zones if not self._sc_is_self_closing(z)]
            if linked:
                await self._dispatch_sequencing(linked, deadline=deadline)
        finally:
            await self.async_master_release(cycle_token)

    def _drop_zones_already_running(self, zones: list) -> list:
        """Filter out zones that already have a run in flight.

        Shared by the scheduled dispatch and Irrigate-now. A duplicate dispatch is
        honoured, not merged: live, two Irrigate-now presses 10 s apart ran two
        full concurrent loops on one zone, delivered twice the water, and credited
        the bucket once (both loops write the same absolute anchor + credit).
        """
        out = []
        for z in zones:
            zone_id = z.get(const.ZONE_ID)
            if self.zone_run_in_flight(zone_id):
                _LOGGER.info(
                    "Zone %s already has a run in flight; not dispatching another",
                    zone_id,
                )
                continue
            out.append(z)
        return out

    def _zone_links_a_station(self, zone: dict) -> bool:
        """This zone would drive an OpenSprinkler station from the classic path.

        ``turn_on`` on a station switch calls ``station.enable()``: it rewrites
        the station's enabled flag on the controller and opens nothing. The run
        would therefore rewrite configuration, deliver no water, and still
        confirm itself as running, because the switch does go on — silent
        wrong-watering. The watering-mode predicate keeps a zone configured for
        OpenSprinkler off this path entirely; the remaining way in is a zone left
        in classic mode with a station in its ``linked_entity``, which is the one
        new mistake sharing the field permits. Refuse the run and say so.
        """
        entity_id = zone.get(const.ZONE_LINKED_ENTITY)
        if not entity_is_station(self.hass, entity_id):
            return False
        zone_id = zone.get(const.ZONE_ID)
        _LOGGER.error(
            "Zone %s is in '%s' mode with OpenSprinkler station '%s' as its "
            "linked entity. Turning that switch on would rewrite the "
            "controller's configuration without watering, so the run is "
            "refused; set the zone's watering mode to '%s'",
            zone_id,
            zone.get(const.ZONE_WATERING_MODE) or const.WATERING_MODE_CLASSIC,
            entity_id,
            const.WATERING_MODE_OPENSPRINKLER,
        )
        self._set_zone_fault(zone_id, const.PROBLEM_STATION_WRONG_MODE)
        self._fire_zone_problem(
            zone_id, zone, entity_id, const.PROBLEM_STATION_WRONG_MODE
        )
        return True

    async def _dispatch_sequencing(self, zones: list, *, deadline=None) -> None:
        """Start the linked-entity zones under the configured sequencing.

        Acquires the master hold HERE, before the task exists, and hands the token
        to the worker to release in its ``finally``. Acquiring inside the task
        instead would race the dispatcher's own release.

        hass.async_create_task (not bare asyncio.create_task): the event loop keeps
        only a WEAK reference to a bare task, so a long irrigation run — which holds
        valves open — can be garbage-collected mid-execution. A tracked task is also
        cancelled on shutdown and has its exceptions logged.
        See tests/test_run_lifecycle_safety.py.
        """
        # Every classic run reaches a valve through here, so this is where a zone
        # pointing at an OpenSprinkler station is refused (async_run_zone reaches
        # _irrigate_zones_parallel directly and checks for itself).
        zones = [z for z in zones if not self._zone_links_a_station(z)]
        if not zones:
            return
        sequencing = self.store.config.zone_sequencing
        if sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL:
            token = f"seq:{uuid.uuid4().hex[:8]}"
            await self.async_master_acquire(token)
            self.hass.async_create_task(
                self._irrigate_zones_sequential(
                    zones, master_token=token, deadline=deadline
                )
            )
        elif sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            token = f"rot:{uuid.uuid4().hex[:8]}"
            await self.async_master_acquire(token)
            self.hass.async_create_task(
                self._irrigate_zones_rotating(
                    zones, master_token=token, deadline=deadline
                )
            )
        else:
            # Parallel: every zone opens at once, so there is no ORDER to
            # truncate — but there is still a run to cut. The selection does not
            # guarantee the set fits: when nothing in the driest group fits,
            # `select` keeps the leader on purpose and leaves the deadline to
            # cut it. Parallel holds that run in the same task the other two
            # modes do, so it cuts it the same way, by the length it dispatches.
            await self._irrigate_zones_parallel(zones, deadline=deadline)

    def _read_flow_sample(self, flow_sensor: str):
        """Current (value, unit, state_class) of a flow sensor, or None when it is
        unavailable/unknown/non-numeric (a flaky tick the FlowMeter simply skips)."""
        state = self.hass.states.get(flow_sensor)
        if state is None or state.state in ("unavailable", "unknown"):
            # DEBUG (not WARNING): FM-5 polls this every 15 s across the whole
            # self-closing window, so a flaky/misconfigured sensor would spam the log.
            # A skipped tick is handled safely by the FlowMeter; a persistently dead
            # sensor surfaces via the dry-fault (linked path) / time-based fallback.
            _LOGGER.debug("Flow sensor '%s' unavailable", flow_sensor)
            return None
        try:
            value = float(state.state)
        except (ValueError, TypeError):
            _LOGGER.debug(
                "Flow sensor '%s' non-numeric state '%s'", flow_sensor, state.state
            )
            return None
        attrs = state.attributes or {}
        return (
            value,
            attrs.get("unit_of_measurement", "L/min"),
            attrs.get("state_class"),
        )

    def _flow_build_meter(self, cfg: dict, sample):
        """Build a run's FlowMeter with the counter type resolved from the per-zone
        override or the STORED cross-run streak; return ``(meter, open_start_l)`` where
        ``open_start_l`` is the valve-open reading in litres (a totalizer only, else None)
        for the run-end reset check. ``sample`` is the valve-open (value, unit,
        state_class) read or None. The streak is NOT advanced here — learning is resolved
        at run END from the meter's actual reset observation (``_flow_learn_end_changes``),
        which sees a hold-until-reset counter's mid-run zeroing that the open read misses.
        Seeds the meter with the open read.
        """
        override = cfg.get(const.ZONE_FLOW_COUNTER_TYPE, "auto")
        streak = int(cfg.get(const.ZONE_FLOW_RESET_STREAK) or 0)
        open_start_l = None
        if sample is not None and flow_is_totalizer(sample[1], sample[2]):
            open_start_l = flow_litres_from_total(sample[0], sample[1])
        resolved = flow_learn_resolve(override, streak)
        meter = FlowMeter(
            resolved,
            near_zero_frac=const.FLOW_NEAR_ZERO_FRAC,
            near_zero_floor=const.FLOW_NEAR_ZERO_FLOOR,
            max_gap_s=const.FLOW_MAX_GAP_SECONDS,
        )
        if sample is not None:
            meter.sample(*sample, at=0.0)  # valve-open seed
        return meter, open_start_l

    def _flow_learn_end_changes(self, cfg: dict, meter, open_start_l) -> dict:
        """Store dict persisting this run's end value (litres) AND the updated cross-run
        reset streak, or {} for a rate sensor / no totalizer reading. The streak advances
        on either reset signal — a near-zero open read (reset-at-open) or a mid-run
        near-zero drop the meter observed (``saw_reset``; a hold-until-reset counter) —
        and resets to 0 for a monotonic lifetime totalizer. See flow_learn_next_streak.
        """
        end = meter.last_total()
        if end is None:
            return {}
        streak = int(cfg.get(const.ZONE_FLOW_RESET_STREAK) or 0)
        return {
            const.ZONE_FLOW_LAST_END: end,
            const.ZONE_FLOW_RESET_STREAK: flow_learn_next_streak(
                cfg.get(const.ZONE_FLOW_LAST_END),
                open_start_l,
                streak,
                within_run_reset=meter.saw_reset(),
            ),
        }

    def _metered_target_volume(self, zone: dict, floor: float) -> float:
        """Litres a real-flow zone must deliver to reach its post-run ``floor``.

        ``floor`` is the post-run target bucket (display units, normally 0.0, or
        the forecast-weighting remainder) — never the live-estimate surplus
        ceiling, so a flow run tops up to the deficit and does not overfill.
        """
        size = zone.get(const.ZONE_SIZE) or 0.0
        bucket = zone.get(const.ZONE_BUCKET) or 0.0
        floor_mm = floor
        if self.hass.config.units is not METRIC_SYSTEM:
            size = convert_between(const.UNIT_SQ_FT, const.UNIT_M2, size)
            bucket = convert_between(const.UNIT_INCH, const.UNIT_MM, bucket)
            floor_mm = convert_between(const.UNIT_INCH, const.UNIT_MM, floor)
        return size * max(0.0, floor_mm - bucket)

    async def _flow_calibration_check(
        self, zone: dict, measured_l: float, seconds: float
    ) -> None:
        """Advisory for a can't-stop measured run: sample the OBSERVED flow rate
        (measured_l / minutes) — immune to the zone multiplier, manual overrides and
        the duration clamp, unlike a volume deviation — and, once >= FLOW_CAL_MIN_SAMPLES
        are collected, raise (and refresh on each subsequent out-of-band run) an HA
        persistent notification when the mean observed rate differs from the configured
        throughput by more than FLOW_CAL_DEVIATION, with a recommended throughput = the
        mean observed rate (in the user's unit). Self-clears (dismiss + reset) once back
        within band. Advisory-only: the notification service
        call is wrapped in try/except so it cannot propagate out of the sweep (the
        trailing store write is as safe as the credit write just before it)."""
        if measured_l is None or seconds <= 0:
            return
        cfg_lpm = self._throughput_lpm(zone)
        if not cfg_lpm or cfg_lpm <= 0:
            return
        zone_id = zone.get(const.ZONE_ID)
        observed_lpm = float(measured_l) / (float(seconds) / 60.0)
        samples = list(zone.get(const.ZONE_FLOW_CAL_SAMPLES) or [])
        samples.append(round(observed_lpm, 4))
        samples = samples[-const.FLOW_CAL_MAX_SAMPLES :]
        advised = bool(zone.get(const.ZONE_FLOW_CAL_ADVISED))
        changes = {const.ZONE_FLOW_CAL_SAMPLES: samples}
        notif_id = f"smart_irrigation_flow_cal_{zone_id}"
        try:
            if len(samples) >= const.FLOW_CAL_MIN_SAMPLES:
                mean_obs = sum(samples) / len(samples)
                deviation = (mean_obs - cfg_lpm) / cfg_lpm
                # Iter (advisory re-arm, 2026-07-13): fire on EVERY out-of-band
                # evaluation, not only the first. The old `and not advised` gate
                # latched the advisory shut for as long as the zone stayed out of
                # band and re-armed ONLY on a return within band — and dismissing
                # the notification does NOT reset `advised` (the latch lives in the
                # store, not the UI). So a user who dismissed it while still
                # miscalibrated was never reminded (live: Kirschlorbeer, 6 L/min
                # configured vs ~3.5 L/min observed, ~-40% over many runs, no repeat
                # notice). The stable notification_id makes HA UPDATE the single
                # notification in place (no stacking/spam) and re-raise it if the
                # user dismissed it; the elif below still dismisses + clears advised
                # on a return within band. NOT-TO-DO: gate on a "is the notification
                # still shown?" state lookup — modern HA (>=2023.8) removed
                # persistent_notification from the state machine, so that check is
                # not reliably available; re-firing on the stable id is the robust,
                # HA-version-independent equivalent.
                # siehe test_flow_calibration.py::test_readvises_while_out_of_band_after_dismiss
                if abs(deviation) > const.FLOW_CAL_DEVIATION:
                    metric = self.hass.config.units is METRIC_SYSTEM
                    rec = (
                        mean_obs
                        if metric
                        else convert_between(const.UNIT_LPM, const.UNIT_GPM, mean_obs)
                    )
                    unit = "L/min" if metric else "gal/min"
                    # Localized calibration advisory: the advisory used to be
                    # hardcoded English (wrong on non-English HA
                    # systems) and gave no path to the zone. Build title + message
                    # from the backend localize() helper (flow_calibration.* keys in
                    # all 8 language files) and append a Markdown deep-link to the
                    # zone's settings — the same target as the dashboard gear icon
                    # (path segments per exportPath, NOT a ?query). Direction:
                    # deviation > 0 -> over-watering, else under.
                    lang = self.hass.config.language
                    title = await localize("flow_calibration.title", lang)
                    key = (
                        "flow_calibration.message_over"
                        if deviation > 0
                        else "flow_calibration.message_under"
                    )
                    body = (await localize(key, lang)).format(
                        zone=zone.get(const.ZONE_NAME),
                        percent=f"{abs(deviation) * 100:.0f}",
                        runs=len(samples),
                        rate=f"{rec:.1f}",
                        unit=unit,
                        current=f"{float(zone.get(const.ZONE_THROUGHPUT) or 0):.1f}",
                    )
                    link_label = await localize("flow_calibration.open_settings", lang)
                    message = (
                        f"{body}\n\n[{link_label}]"
                        f"(/smart_irrigation/setup/zones/zone/{zone_id})"
                    )
                    await self.hass.services.async_call(
                        "persistent_notification",
                        "create",
                        {
                            "notification_id": notif_id,
                            "title": title,
                            "message": message,
                        },
                    )
                    changes[const.ZONE_FLOW_CAL_ADVISED] = True
                elif abs(deviation) <= const.FLOW_CAL_DEVIATION and advised:
                    await self.hass.services.async_call(
                        "persistent_notification",
                        "dismiss",
                        {"notification_id": notif_id},
                    )
                    changes[const.ZONE_FLOW_CAL_ADVISED] = False
        except Exception:  # noqa: BLE001 - advisory must never strand the inlet/master
            _LOGGER.warning(
                "Flow calibration advisory failed for zone %s", zone_id, exc_info=True
            )
        await self.store.async_update_zone(zone_id, changes)

    async def _run_valve_metered(
        self,
        zone: dict,
        entity_id: str,
        *,
        real_flow: bool,
        trigger: str = "schedule",
        master_token=None,
        deadline_cut_from: float | None = None,
    ) -> None:
        """Open a zone's valve and account for the water continuously until done.

        One primitive for both run kinds: a real-flow zone integrates its sensor
        each poll; a throughput-only zone synthesizes a constant ``throughput``
        L/min rate (mimicking a flow meter). Either way the bucket and the
        ``water_used_total`` counter are credited *while the valve is open*, on a
        coarse ``RUN_COMMIT_INTERVAL`` cadence, instead of one binary write at the
        end — so a mid-run restart keeps the partial progress.

        Stop condition: a real-flow run stops at its target volume or the
        ``maximum_duration`` safety timeout; a synthetic run stops at its
        ``ZONE_DURATION``. The final bucket is identical to the old end-of-run
        behaviour because the duration always delivers at least the deficit, so
        crediting the delivered depth clamps at the same target ``ceiling``.

        ``deadline_cut_from`` is the duration the zone was planned for when its
        caller shortened it to fit the run deadline. Without it the dispatch
        paths that truncate a zone in place — sequential and parallel — record
        an ordinary completed run of exactly the length they cut it to, and the
        run log says nothing about why the zone got less water than it needed.
        The rotation records its own partial, so it does not pass this.
        """
        zone_id = zone[const.ZONE_ID]
        domain = entity_id.split(".")[0]
        original_bucket = zone.get(const.ZONE_BUCKET) or 0.0

        if real_flow:
            # Flow zones deliver to the measured target *floor* and credit the
            # bucket from the metered volume. The live-estimate surplus ceiling
            # (maximum_bucket) must NOT apply here — it would balloon the target
            # volume and overfill the zone (e.g. a manual run_zone marks the zone
            # in _live_run_zones). Consume any stray marker so it can't leak.
            live = getattr(self, "_live_run_zones", None)
            if live:
                live.discard(int(zone_id))
            ceiling = self._zone_target_bucket(zone)
            target_volume = self._metered_target_volume(zone, ceiling)
            max_seconds = float(
                zone.get(const.ZONE_MAXIMUM_DURATION) or const.FLOW_SAFETY_TIMEOUT
            )
            rate_lpm = 0.0
            _LOGGER.info(
                "Metered (flow) irrigation: zone %s target %.1f L (sensor: %s)",
                zone_id,
                target_volume,
                zone[const.ZONE_FLOW_SENSOR],
            )
        else:
            # Synthetic (throughput) run: a live-estimate run may credit a surplus
            # up to maximum_bucket, otherwise it replenishes to the target floor.
            ceiling = self._run_ceiling(zone)
            target_volume = float("inf")
            max_seconds = float(zone.get(const.ZONE_DURATION) or 0)
            rate_lpm = self._throughput_lpm(zone)
            _LOGGER.info(
                "Metered (timed) irrigation: zone %s for %.0fs @ %.2f L/min",
                zone_id,
                max_seconds,
                rate_lpm,
            )

        self._note_si_valve(zone_id, max_seconds)
        await self.hass.services.async_call(domain, "turn_on", {"entity_id": entity_id})
        if await self._confirm_valve_running(zone_id, entity_id) is False:
            # The valve never reported an on-state within the grace window. Many
            # valves actuate but report back slowly (or not at all), so closing
            # it here would guarantee no watering — instead we proceed with the
            # run and just surface that it could not be confirmed.
            _LOGGER.warning(
                "Zone %s valve '%s' did not confirm an on-state within %ss; "
                "proceeding with the run (valve may be slow to report state)",
                zone_id,
                entity_id,
                const.VALVE_CONFIRM_TIMEOUT,
            )

        delivered = 0.0
        water_committed = 0.0
        elapsed = 0.0
        last_commit = 0.0
        stopped = False

        # Iter FM-3 (unified flow engine + cross-run learning): a real-flow run feeds one
        # shared FlowMeter (rate / per-run counter / lifetime totalizer). The counter type
        # is the per-zone override or the learned cross-run classification; the valve-open
        # read seeds the meter (so a per-run reset is observed). The learning streak is
        # advanced at run END (_flow_learn_end_changes) from the meter's actual reset
        # observation. See flow_metering.FlowMeter and test_metered_run.
        meter = None
        open_start_l = None
        if real_flow:
            sample = self._read_flow_sample(zone[const.ZONE_FLOW_SENSOR])
            meter, open_start_l = self._flow_build_meter(zone, sample)

        # Flow runs are volume-targeted (no multiplier) → credit gross depth.
        # Timed runs inflate the duration by the multiplier → divide it back out
        # so a full run lands at the target for any multiplier.
        credit_depth = (
            self._depth_from_volume_native if real_flow else self._credited_depth_native
        )

        def _bucket_for(total_l: float) -> float:
            return min(ceiling, original_bucket + credit_depth(zone, total_l))

        # Register the run so the dashboard can show a Stop control / countdown
        # and a user-issued stop can interrupt the sleep below. Flow runs are
        # volume-bounded (unknown finish) → no end time for the countdown.
        self._register_active_run(zone_id, max_seconds, has_end=not real_flow)
        loop = asyncio.get_running_loop()
        # The valve is open from here on. Every exit path — normal, exception, or
        # CancelledError at shutdown/reload — MUST close it again, so the close is
        # mirrored in the finally below and this flag keeps the happy path from
        # closing twice. See tests/test_run_lifecycle_safety.py.
        valve_closed = False
        try:
            while elapsed < max_seconds and delivered < target_volume:
                step = min(const.FLOW_POLL_INTERVAL, max_seconds - elapsed)
                if step <= 0:
                    break
                t0 = loop.time()
                if await self._sleep_or_stopped(zone_id, step):
                    # Stopped early: count only the time actually waited so the
                    # delivered volume (and credited bucket) stay honest.
                    stopped = True
                    step = min(step, loop.time() - t0)
                elapsed += step
                if real_flow:
                    sample = self._read_flow_sample(zone[const.ZONE_FLOW_SENSOR])
                    if sample is not None:
                        meter.sample(*sample, at=elapsed)
                    measured = meter.delivered() or 0.0
                    if measured <= 0 and meter.saw_reset():
                        # A totalizer that reset but whose type is still being learned:
                        # the over-credit-safe 'lifetime' mode keeps the pre-reset
                        # baseline, so it cannot yet measure the climb. Credit a
                        # time-based estimate so this VOLUME-targeted run still terminates
                        # at its target instead of running to the safety maximum; the
                        # streak advanced this run (saw_reset), so cross-run learning
                        # converges it to per_run within a couple of runs — then it
                        # measures exactly. See test_metered_zone_auto_hold_until_reset*.
                        delivered = self._timed_volume_l(zone, elapsed)
                    else:
                        delivered = measured
                else:
                    delivered += rate_lpm * step / 60.0
                if stopped:
                    break
                if elapsed - last_commit >= const.RUN_COMMIT_INTERVAL:
                    await self._commit_run_progress(
                        zone_id,
                        new_bucket=_bucket_for(delivered),
                        volume_delta_l=delivered - water_committed,
                        dispatch=True,
                    )
                    water_committed = delivered
                    last_commit = elapsed

            await self.hass.services.async_call(
                domain, "turn_off", {"entity_id": entity_id}
            )
            valve_closed = True
            if real_flow:
                # review finding G: a volume-bounded (real_flow) run opened with the
                # ~maximum_duration safety window as its SI-driven suppression (the finish
                # is unknown at open, so _note_si_valve above used max_seconds ~= 14400).
                # It actually closes after a few minutes; without re-noting, the
                # observed-watering observer stays suppressed for the multi-hour tail and a
                # genuine external watering after the run is silently NOT credited. The valve
                # is now closed -> tighten the window to now + margin (~30 s) so suppression
                # ends with the run. A timed run's max_seconds already equals its real length
                # (so its open window is correct) — hence gate strictly on real_flow.
                self._note_si_valve(zone_id, 0)

            if real_flow and meter is not None:
                end_changes = self._flow_learn_end_changes(zone, meter, open_start_l)
                if end_changes:
                    await self.store.async_update_zone(zone_id, end_changes)

            if not stopped and real_flow and target_volume > 0 and delivered <= 0:
                # Valve opened but the flow sensor never registered any flow — failed
                # run: do not credit the bucket, flag a fault so the deficit persists. (A
                # totalizer that MOVED but couldn't be measured yet is already credited
                # time-based in the loop above via meter.saw_reset(), so it does not reach
                # here — only a genuinely dry run does.)
                self._set_zone_fault(zone_id, const.FAULT_FLOW_NEVER_STARTED)
                await self._record_run(
                    zone_id,
                    result=const.RUN_RESULT_FAILED,
                    detail=const.FAULT_FLOW_NEVER_STARTED,
                    trigger=trigger,
                )
                return

            await self._commit_run_progress(
                zone_id,
                new_bucket=_bucket_for(delivered),
                volume_delta_l=delivered - water_committed,
                dispatch=True,
            )
            self._clear_zone_fault(zone_id)
            timed_out = real_flow and delivered < target_volume
            _LOGGER.info(
                "Metered irrigation: zone %s %s — %.2f L in %.0fs%s",
                zone_id,
                "stopped" if stopped else "done",
                delivered,
                elapsed,
                " (safety timeout)" if timed_out else "",
            )
            await self._record_run(
                zone_id,
                result=(
                    const.RUN_RESULT_PARTIAL
                    if (stopped or timed_out or deadline_cut_from)
                    else const.RUN_RESULT_COMPLETED
                ),
                volume_l=delivered,
                add_to_total=False,  # already streamed in via _commit_run_progress
                # The cut zone reports the length it was PLANNED for, not the
                # length it was cut to, so planned-against-actual reads as the
                # shortfall it is instead of as a run that got everything it
                # asked for.
                planned_s=(None if real_flow else (deadline_cut_from or max_seconds)),
                actual_s=elapsed,
                detail=(
                    const.RUN_DETAIL_STOPPED
                    if stopped
                    else (
                        "safety_timeout"
                        if timed_out
                        else (
                            const.RUN_DETAIL_DEADLINE
                            if deadline_cut_from
                            else zone.get(const.ZONE_EXPLANATION)
                        )
                    )
                ),
                trigger=trigger,
            )
        finally:
            # Safety net: if we never reached the normal close (exception, or a
            # CancelledError from HA shutting down / reloading mid-run) the valve
            # is still physically open and nothing else will close it — unload
            # does not stop runs. Best-effort, and never allowed to mask the
            # original failure; the nested finally keeps the run marker cleanup
            # reachable even if the close itself is cancelled.
            try:
                if not valve_closed:
                    _LOGGER.warning(
                        "Zone %s run ended without closing valve '%s' — closing it now",
                        zone_id,
                        entity_id,
                    )
                    await self.hass.services.async_call(
                        domain, "turn_off", {"entity_id": entity_id}
                    )
            except Exception:  # noqa: BLE001 - cleanup must not mask the real error
                _LOGGER.exception(
                    "Zone %s: failed to close valve '%s' during run cleanup",
                    zone_id,
                    entity_id,
                )
            finally:
                self._unregister_active_run(zone_id)
                # The valve is shut; drop the master hold. Last one out ends the
                # cycle (master.py async_master_release).
                if master_token:
                    await self.async_master_release(master_token)
                # Ordered AFTER _unregister_active_run so the calculation no
                # longer sees a run in flight and actually runs. No-op unless a
                # calculation was displaced by this run.
                await self.async_run_deferred_calculation(zone_id)

    async def _irrigate_zone_flow_slot(
        self,
        zone: dict,
        entity_id: str,
        max_seconds: float,
        remaining_volume: float,
    ) -> float:
        """Open a flow-meter zone for up to max_seconds or until remaining_volume is reached.

        Returns litres delivered during this slot.
        """
        zone_id = zone[const.ZONE_ID]
        domain = entity_id.split(".")[0]

        self._note_si_valve(zone_id, max_seconds)
        await self.hass.services.async_call(domain, "turn_on", {"entity_id": entity_id})

        accumulated = 0.0
        # Valve is open — see _run_valve_metered: every exit path must close it,
        # including a raise from the meter seed below (a flaky flow sensor) or a
        # CancelledError at shutdown. The try starts immediately after the open.
        valve_closed = False
        try:
            # Iter FM-4 (unified flow engine, REGEL-8 sister path to _run_valve_metered):
            # each rotating slot is its own valve-open window, so it gets its own FlowMeter
            # seeded at the open read (rate / per-run counter / lifetime totalizer — the type
            # resolved from the per-zone override or the already-learned streak). Replaces the
            # retired _read_flow_increment / _flow_last_total delta baseline; also captures the
            # slot's first interval (the old path lost it). The rotating path does not
            # self-update the cross-run streak (its multi-window structure has no single open
            # to observe); it honours an explicit override or a streak learned elsewhere.
            # See test_metered_run rotating coverage.
            resolved = flow_learn_resolve(
                zone.get(const.ZONE_FLOW_COUNTER_TYPE, "auto"),
                int(zone.get(const.ZONE_FLOW_RESET_STREAK) or 0),
            )
            meter = FlowMeter(
                resolved,
                near_zero_frac=const.FLOW_NEAR_ZERO_FRAC,
                near_zero_floor=const.FLOW_NEAR_ZERO_FLOOR,
                max_gap_s=const.FLOW_MAX_GAP_SECONDS,
            )
            open_sample = self._read_flow_sample(zone[const.ZONE_FLOW_SENSOR])
            if open_sample is not None:
                meter.sample(*open_sample, at=0.0)  # valve-open seed

            elapsed = 0.0

            while elapsed < max_seconds and accumulated < remaining_volume:
                stopped = await self._sleep_or_stopped(
                    zone_id, const.FLOW_POLL_INTERVAL
                )
                elapsed += const.FLOW_POLL_INTERVAL
                sample = self._read_flow_sample(zone[const.ZONE_FLOW_SENSOR])
                if sample is not None:
                    meter.sample(*sample, at=elapsed)
                accumulated = meter.delivered() or 0.0
                _LOGGER.debug(
                    "Zone %s slot: %.2f / %.2f L delivered",
                    zone_id,
                    accumulated,
                    remaining_volume,
                )
                if stopped:
                    break

            await self.hass.services.async_call(
                domain, "turn_off", {"entity_id": entity_id}
            )
            valve_closed = True
            # Review finding G (REGEL-8 sister path to _run_valve_metered): the open
            # noted the full slot cap, but a volume-bounded slot usually
            # closes early — shrink the observed-watering suppression window to
            # now+margin at slot close so a genuine external run of this zone's
            # observed_entity in the tail is not silently un-credited. A rotating slot
            # is always a flow slot, so this is unconditional.
            # siehe test_metered_run.py::test_flow_slot_tightens_si_window_on_close
            self._note_si_valve(zone_id, 0)
            if meter.delivered() is None:
                # A configured flow sensor that produced NO readings this slot degraded
                # silently to time-based crediting (per-tick reads are DEBUG). Surface it
                # once so a dead/misconfigured sensor isn't invisible. See Fix FM-6.
                _LOGGER.warning(
                    "Rotating zone %s flow sensor '%s' produced no readings this slot; "
                    "the slot volume falls back to a time-based estimate",
                    zone_id,
                    zone[const.ZONE_FLOW_SENSOR],
                )
            return accumulated
        finally:
            if not valve_closed:
                try:
                    _LOGGER.warning(
                        "Zone %s slot ended without closing valve '%s' — closing it now",
                        zone_id,
                        entity_id,
                    )
                    await self.hass.services.async_call(
                        domain, "turn_off", {"entity_id": entity_id}
                    )
                except Exception:  # noqa: BLE001 - must not mask the real error
                    _LOGGER.exception(
                        "Zone %s: failed to close valve '%s' during slot cleanup",
                        zone_id,
                        entity_id,
                    )

    async def _record_rotating_stop(self, zid, volume_l: float, elapsed_s: float):
        """Log a user-stopped rotating run as a partial (water kept, fault cleared)."""
        self._clear_zone_fault(zid)
        await self._record_run(
            zid,
            result=const.RUN_RESULT_PARTIAL,
            volume_l=volume_l,
            add_to_total=False,
            actual_s=elapsed_s,
            detail=const.RUN_DETAIL_STOPPED,
            trigger=self._run_trigger(zid),
        )

    async def _irrigate_zones_rotating(
        self, zones: list, *, master_token=None, deadline=None
    ):
        """Irrigate all zones (timed and flow-meter) in a unified rotation.

        Each zone gets at most max_consecutive_duration per turn.
        When min_absorption_time > 0, the loop waits before returning to a zone.

        Holds the master for the whole rotation, which is what makes
        ``min_absorption_time`` safe: the waits stretch the cycle far past any
        naive ``sum(durations)`` (2×600 s with a 10 min absorption really ends at
        1920 s, not 1200 s), which is how a predicted deadline once cut the pump
        mid-rotation. A ``deadline`` passed in here is safe because the anchor
        that produced it was itself sized by ``run_window.concurrent_wall_clock``,
        whose classic track replays this loop's absorption structure rather than
        summing.
        """
        claimed = self._claim_chain_zones(zones)
        try:
            await self._run_rotation(zones, deadline=deadline)
        finally:
            await self._release_chain_zones(claimed)
            if master_token:
                await self.async_master_release(master_token)

    async def _run_rotation(self, zones: list, *, deadline=None):
        """The rotation itself (master hold is managed by the caller)."""
        max_slot = (
            max(1, (self.store.config.zone_sequencing_max_consecutive_duration or 5))
            * 60
        )
        min_absorption = (
            self.store.config.zone_sequencing_min_absorption_time or 0
        ) * 60

        timed_zones = [z for z in zones if not z.get(const.ZONE_FLOW_SENSOR)]
        flow_zones = [z for z in zones if z.get(const.ZONE_FLOW_SENSOR)]

        timed_remaining = {
            z[const.ZONE_ID]: float(z[const.ZONE_DURATION]) for z in timed_zones
        }
        timed_by_id = {z[const.ZONE_ID]: z for z in timed_zones}
        # Per-zone accounting state (native display units / litres). The bucket is
        # an idempotent absolute recompute from the original level + cumulative
        # delivered depth (so each commit is safe); water usage is credited by the
        # per-slot delta only. ``_run_ceiling`` consumes the live-estimate marker
        # once per zone here.
        timed_orig_bucket = {
            z[const.ZONE_ID]: (z.get(const.ZONE_BUCKET) or 0.0) for z in timed_zones
        }
        timed_ceiling = {z[const.ZONE_ID]: self._run_ceiling(z) for z in timed_zones}
        timed_delivered_l = {z[const.ZONE_ID]: 0.0 for z in timed_zones}

        ha_metric = self.hass.config.units is METRIC_SYSTEM
        flow_target: dict = {}
        flow_delivered: dict = {}
        flow_elapsed: dict = {}
        flow_orig_bucket: dict = {}
        flow_floor: dict = {}
        flow_by_id: dict = {}

        for z in flow_zones:
            zid = z[const.ZONE_ID]
            raw_size = z.get(const.ZONE_SIZE) or 0.0
            raw_bucket = z.get(const.ZONE_BUCKET) or 0.0
            raw_floor = self._zone_target_bucket(z)
            s_m2 = (
                raw_size
                if ha_metric
                else convert_between(const.UNIT_SQ_FT, const.UNIT_M2, raw_size)
            )
            b_mm = (
                raw_bucket
                if ha_metric
                else convert_between(const.UNIT_INCH, const.UNIT_MM, raw_bucket)
            )
            floor_mm = (
                raw_floor
                if ha_metric
                else convert_between(const.UNIT_INCH, const.UNIT_MM, raw_floor)
            )
            flow_target[zid] = s_m2 * max(0.0, floor_mm - b_mm)
            flow_delivered[zid] = 0.0
            flow_elapsed[zid] = 0.0
            flow_orig_bucket[zid] = raw_bucket
            flow_floor[zid] = raw_floor
            flow_by_id[zid] = z
            _LOGGER.info(
                "Rotating irrigation: flow zone %s target %.1f L", zid, flow_target[zid]
            )

        zone_order = [z[const.ZONE_ID] for z in timed_zones + flow_zones]
        last_finish: dict = {}
        recorded: set = set()  # zones whose completion has been logged once
        loop = asyncio.get_running_loop()

        # Every zone is already claimed by the caller (_irrigate_zones_rotating),
        # which is what lets a Stop interrupt the rotation, surfaces the control
        # on the dashboard, and keeps a second dispatch off the whole plan rather
        # than off the one zone currently open. A rotation has no single finish
        # time, so no countdown end is set. Markers are cleared as each zone
        # finishes and the caller sweeps the remainder.

        def _timed_done(zid):
            return timed_remaining.get(zid, 0) <= 0

        def _flow_done(zid):
            safety = (
                flow_by_id[zid].get(const.ZONE_MAXIMUM_DURATION)
                or const.FLOW_SAFETY_TIMEOUT
            )
            return (
                flow_delivered[zid] >= flow_target[zid] or flow_elapsed[zid] >= safety
            )

        def _all_done():
            return all(_timed_done(z) for z in timed_by_id) and all(
                _flow_done(z) for z in flow_by_id
            )

        def _remaining_window():
            """Seconds left before the run deadline, or None when unbounded."""
            if deadline is None:
                return None
            return (deadline - dt_util.utcnow()).total_seconds()

        async def _reprice(zid) -> bool:
            """Re-price a timed zone against the live deficit.

            False means the zone is finished here — either it no longer needs
            water, or what it still owes has been delivered. A zone that has
            already received water this run is re-priced as ``started``, so it
            refills to capacity instead of stopping at its trigger threshold
            (see :meth:`_zone_run_decision`).
            """
            repriced = await self._resize_queued_zone(
                {**timed_by_id[zid], const.ZONE_DURATION: timed_remaining[zid]},
                ha_metric,
                started=timed_delivered_l[zid] > 0,
            )
            if repriced is None:
                _LOGGER.info(
                    "Rotating irrigation: zone %s no longer needs water; "
                    "finishing it here with what it has already received",
                    zid,
                )
                if zid not in recorded:
                    recorded.add(zid)
                    planned = float(timed_by_id[zid][const.ZONE_DURATION])
                    self._clear_zone_fault(zid)
                    await self._record_run(
                        zid,
                        result=const.RUN_RESULT_PARTIAL,
                        volume_l=timed_delivered_l[zid],
                        add_to_total=False,
                        planned_s=planned,
                        actual_s=planned - timed_remaining[zid],
                        detail=const.SKIP_REASON_NO_DEMAND,
                        trigger=self._run_trigger(zid),
                    )
                timed_remaining[zid] = 0
                self._unregister_active_run(zid)
                return False
            timed_remaining[zid] = min(
                timed_remaining[zid],
                float(repriced.get(const.ZONE_DURATION) or 0),
            )
            if timed_remaining[zid] <= 0:
                self._unregister_active_run(zid)
                return False
            return True

        out_of_time = False
        while not _all_done() and not out_of_time:
            for zid in zone_order:
                is_flow = zid in flow_by_id
                if is_flow and _flow_done(zid):
                    continue
                if not is_flow and _timed_done(zid):
                    continue

                # Deadline check goes BEFORE the absorption wait: sleeping out a
                # 10-minute pause only to find the window gone would hold the
                # master pump for that whole pause with no water to show for it.
                window = _remaining_window()
                if window is not None and window <= 0:
                    _LOGGER.warning(
                        "Rotating irrigation: run deadline %s reached; stopping "
                        "with zone %s (and any other unfinished zone) short. "
                        "Their residual deficit carries to the next run",
                        deadline,
                        zid,
                    )
                    out_of_time = True
                    break

                # Re-price a timed zone before returning to it. A rotation with
                # absorption pauses can span hours, so rain part-way through
                # should stop the zones that have not finished rather than keep
                # refilling a profile that is already full. Timed zones only: a
                # flow zone delivers to a measured volume whose target was fixed
                # in litres when the rotation started.
                if not is_flow and not await _reprice(zid):
                    continue

                # A user stopped this zone — log a partial (keeping the water
                # already credited), force it "done" so the rotation moves on,
                # and clear its in-progress marker.
                if self._run_stopped(zid):
                    if zid not in recorded:
                        recorded.add(zid)
                        if is_flow:
                            await self._record_rotating_stop(
                                zid, flow_delivered[zid], flow_elapsed[zid]
                            )
                        else:
                            planned = float(timed_by_id[zid][const.ZONE_DURATION])
                            await self._record_rotating_stop(
                                zid,
                                timed_delivered_l[zid],
                                planned - timed_remaining[zid],
                            )
                    if is_flow:
                        flow_delivered[zid] = max(flow_delivered[zid], flow_target[zid])
                        flow_elapsed[zid] = max(
                            flow_elapsed[zid],
                            flow_by_id[zid].get(const.ZONE_MAXIMUM_DURATION)
                            or const.FLOW_SAFETY_TIMEOUT,
                        )
                    else:
                        timed_remaining[zid] = 0
                    self._unregister_active_run(zid)
                    continue

                if min_absorption > 0 and zid in last_finish:
                    wait = min_absorption - (loop.time() - last_finish[zid])
                    if wait > 0:
                        if window is not None and wait >= window:
                            # The pause alone outlasts the window. Waiting it out
                            # would spend every remaining minute on a sleep.
                            _LOGGER.warning(
                                "Rotating irrigation: zone %s needs a %.0fs "
                                "absorption pause but only %.0fs of the window "
                                "remain; stopping short of the deadline %s",
                                zid,
                                wait,
                                window,
                                deadline,
                            )
                            out_of_time = True
                            break
                        _LOGGER.info(
                            "Rotating irrigation: zone %s absorbing, waiting %.0fs",
                            zid,
                            wait,
                        )
                        await asyncio.sleep(wait)
                        window = _remaining_window()
                        # And re-price again now the pause is over. The
                        # re-price above has to come first so a deadline is
                        # never slept out, but on its own it reads the deficit
                        # from before a pause that can be tens of minutes long
                        # — so rain landing inside it went unseen until the
                        # zone's next lap, and the zone watered a full slot it
                        # no longer owed. Timed zones only, as above: a flow
                        # zone's target was fixed in litres at dispatch.
                        if not is_flow and not await _reprice(zid):
                            continue

                # This zone's slot starts here, so it stops reading as queued
                # until the slot ends. A rotation holds a zone's claim across the
                # whole cycle, and most of that time its valve is shut: between
                # slots, and through every absorption wait above.
                self._set_run_queued(zid, False)

                if is_flow:
                    z = flow_by_id[zid]
                    entity_id = z[const.ZONE_LINKED_ENTITY]
                    safety = (
                        z.get(const.ZONE_MAXIMUM_DURATION) or const.FLOW_SAFETY_TIMEOUT
                    )
                    slot = min(max_slot, safety - flow_elapsed[zid])
                    if window is not None:
                        slot = min(slot, window)
                    rem_vol = flow_target[zid] - flow_delivered[zid]
                    _LOGGER.info(
                        "Rotating irrigation: flow zone %s slot %.0fs (%.1f/%.1f L)",
                        zid,
                        slot,
                        flow_delivered[zid],
                        flow_target[zid],
                    )
                    delivered = await self._irrigate_zone_flow_slot(
                        z, entity_id, slot, rem_vol
                    )
                    flow_delivered[zid] += delivered
                    flow_elapsed[zid] += slot
                    # Credit the bucket (absolute recompute) + this slot's litres.
                    new_bucket = min(
                        flow_floor[zid],
                        flow_orig_bucket[zid]
                        + self._depth_from_volume_native(z, flow_delivered[zid]),
                    )
                    await self._commit_run_progress(
                        zid,
                        new_bucket=new_bucket,
                        volume_delta_l=delivered,
                        dispatch=True,
                    )
                    _LOGGER.info(
                        "Rotating irrigation: flow zone %s slot done — %.1f/%.1f L total",
                        zid,
                        flow_delivered[zid],
                        flow_target[zid],
                    )
                    if _flow_done(zid) and zid not in recorded:
                        recorded.add(zid)
                        if flow_target[zid] > 0 and flow_delivered[zid] <= 0:
                            # Valve cycled but the sensor never registered flow.
                            self._set_zone_fault(zid, const.FAULT_FLOW_NEVER_STARTED)
                            await self._record_run(
                                zid,
                                result=const.RUN_RESULT_FAILED,
                                detail=const.FAULT_FLOW_NEVER_STARTED,
                                trigger=self._run_trigger(zid),
                            )
                        else:
                            self._clear_zone_fault(zid)
                            timed_out = flow_delivered[zid] < flow_target[zid]
                            await self._record_run(
                                zid,
                                result=(
                                    const.RUN_RESULT_PARTIAL
                                    if timed_out
                                    else const.RUN_RESULT_COMPLETED
                                ),
                                volume_l=flow_delivered[zid],
                                add_to_total=False,
                                actual_s=flow_elapsed[zid],
                                detail=(
                                    "safety_timeout"
                                    if timed_out
                                    else z.get(const.ZONE_EXPLANATION)
                                ),
                                trigger=self._run_trigger(zid),
                            )
                else:
                    z = timed_by_id[zid]
                    entity_id = z[const.ZONE_LINKED_ENTITY]
                    domain = entity_id.split(".")[0]
                    rem = timed_remaining[zid]
                    slot = min(rem, max_slot)
                    if window is not None and slot > window:
                        # The zone keeps whatever this shortened slot delivers;
                        # the loop then finds the window gone and stops.
                        slot = window
                    _LOGGER.info(
                        "Rotating irrigation: %s for %.0fs (%.0fs remaining after slot)",
                        entity_id,
                        slot,
                        rem - slot,
                    )
                    self._note_si_valve(zid, slot)
                    await self.hass.services.async_call(
                        domain, "turn_on", {"entity_id": entity_id}
                    )
                    # Valve open — mirror the close in a finally so a raise from
                    # the confirm poll or a CancelledError at shutdown cannot
                    # strand it open (see _run_valve_metered).
                    slot_valve_closed = False
                    try:
                        if await self._confirm_valve_running(zid, entity_id) is False:
                            # Unconfirmed valve: water the slot anyway rather than
                            # dropping the zone — the valve may be open but slow to
                            # report. Surface it as a warning only.
                            _LOGGER.warning(
                                "Zone %s valve '%s' did not confirm an on-state "
                                "within %ss; watering the rotation slot anyway",
                                zid,
                                entity_id,
                                const.VALVE_CONFIRM_TIMEOUT,
                            )
                        t0 = loop.time()
                        slot_stopped = await self._sleep_or_stopped(zid, slot)
                        if slot_stopped:
                            # Count only the time actually waited so the credited
                            # water stays honest.
                            slot = min(slot, loop.time() - t0)
                        await self.hass.services.async_call(
                            domain, "turn_off", {"entity_id": entity_id}
                        )
                        slot_valve_closed = True
                    finally:
                        if not slot_valve_closed:
                            try:
                                _LOGGER.warning(
                                    "Zone %s rotation slot ended without closing "
                                    "valve '%s' — closing it now",
                                    zid,
                                    entity_id,
                                )
                                await self.hass.services.async_call(
                                    domain, "turn_off", {"entity_id": entity_id}
                                )
                            except Exception:  # noqa: BLE001 - must not mask the error
                                _LOGGER.exception(
                                    "Zone %s: failed to close valve '%s' during "
                                    "rotation-slot cleanup",
                                    zid,
                                    entity_id,
                                )
                    timed_remaining[zid] -= slot
                    # Credit this slot's water continuously (absolute bucket
                    # recompute + per-slot litre delta).
                    slot_volume = self._timed_volume_l(z, slot)
                    timed_delivered_l[zid] += slot_volume
                    new_bucket = min(
                        timed_ceiling[zid],
                        timed_orig_bucket[zid]
                        + self._credited_depth_native(z, timed_delivered_l[zid]),
                    )
                    await self._commit_run_progress(
                        zid,
                        new_bucket=new_bucket,
                        volume_delta_l=slot_volume,
                        dispatch=True,
                    )
                    _LOGGER.info("Rotating irrigation: finished slot for %s", entity_id)
                    if slot_stopped:
                        # User stopped mid-slot: log a partial and finish the zone.
                        planned = float(z[const.ZONE_DURATION])
                        if zid not in recorded:
                            recorded.add(zid)
                            await self._record_rotating_stop(
                                zid,
                                timed_delivered_l[zid],
                                planned - timed_remaining[zid],
                            )
                        timed_remaining[zid] = 0
                        self._unregister_active_run(zid)
                    elif timed_remaining[zid] <= 0:
                        # Zone fully irrigated across its slots — log completion.
                        self._clear_zone_fault(zid)
                        planned = float(z[const.ZONE_DURATION])
                        await self._record_run(
                            zid,
                            result=const.RUN_RESULT_COMPLETED,
                            volume_l=timed_delivered_l[zid],
                            add_to_total=False,
                            planned_s=planned,
                            actual_s=planned,
                            detail=z.get(const.ZONE_EXPLANATION),
                            trigger=self._run_trigger(zid),
                        )

                # Slot over, valve shut: back to queued until the zone's next
                # turn. A no-op for a zone whose marker was just cleared, and for
                # a finished one it only holds until the caller's sweep.
                self._set_run_queued(zid, True)
                last_finish[zid] = loop.time()

        if out_of_time:
            # A zone the deadline cut mid-rotation has NOT been recorded: the
            # loop only logs a zone when it finishes its whole duration or a user
            # stops it, and the deadline is a third way out. Its water was
            # credited as each slot committed, so without this the bucket, the
            # usage total and "last irrigation" all move while the run history
            # shows nothing at all — the run simply vanishes from the log.
            for zid in zone_order:
                if zid in recorded:
                    continue
                is_flow = zid in flow_by_id
                if is_flow:
                    if flow_delivered[zid] <= 0:
                        continue
                    volume, actual, planned = (
                        flow_delivered[zid],
                        flow_elapsed[zid],
                        None,
                    )
                else:
                    if timed_delivered_l[zid] <= 0:
                        continue
                    planned = float(timed_by_id[zid][const.ZONE_DURATION])
                    volume = timed_delivered_l[zid]
                    actual = planned - timed_remaining[zid]
                recorded.add(zid)
                await self._record_run(
                    zid,
                    result=const.RUN_RESULT_PARTIAL,
                    volume_l=volume,
                    add_to_total=False,
                    planned_s=planned,
                    actual_s=actual,
                    detail=const.RUN_DETAIL_DEADLINE,
                    trigger=self._run_trigger(zid),
                )

        # Remaining in-progress markers (zones that finished normally, or a stop
        # during an absorption wait) are swept by the caller's finally, so they
        # are cleared on the exception path too.

    # --- Live-estimate watering: trigger + size from the live deficit
    #     (experimental, opt-in)

    async def _apply_live_durations(self, zones: list) -> list:
        """Trigger and size each zone's run from the live intra-day deficit.

        Experimental, opt-in (Setup → Experimental). When the flag is off this
        returns ``zones`` unchanged (the caller has already applied the classic
        daily gate). When on, the caller passes *all* eligible zones — including
        ones the daily calc said 0 — and this method is the trigger gate: it
        refreshes the live estimates and, per timed zone, waters only when the
        drainage-aware ``live_deficit`` (intra-day ET/precip since the last daily
        calc, the same quantity behind the "Live bucket" sensor) is below the
        zone's bucket threshold (minimum deficit), with the run sized from that
        deficit. Zones whose live deficit hasn't crossed the threshold (intra-day
        rain covered them, or too small to bother) are dropped.

        The daily ledger is untouched: only this run's start + duration come from
        the live estimate. Flow-meter zones keep the daily gate (they deliver to
        a measured volume, not a recomputed duration). A zone with no live
        estimate falls back to the daily gate so it neither regresses nor waters
        blind. Recomputed zones are marked in ``_live_run_zones`` so
        :meth:`_run_ceiling` lets the run credit up to ``maximum_bucket`` (a
        surplus) rather than clamping at the daily target; the live deficit can
        exceed the stored daily bucket, so crediting the actually-delivered water
        (not zeroing) keeps the next daily calc from double-subtracting the
        intra-day ET.
        """
        if getattr(self.store.config, "live_estimate_enabled", False) is not True:
            self._live_run_zones = set()
            return zones

        estimates = await self.async_refresh_zone_estimates()
        self._live_run_zones = set()
        metric = self.hass.config.units is METRIC_SYSTEM
        out = []
        for z in zones:
            decision = self._zone_run_decision(z, estimates, metric)
            if decision is None:
                continue
            if not decision.resized:
                out.append(z)
                continue
            zid = int(z.get(const.ZONE_ID))
            self._live_run_zones.add(zid)
            self._warn_if_low_maximum_bucket(z, metric)
            _LOGGER.info(
                "Live-estimate watering: zone %s %ss → %ss (live deficit %.2f)",
                zid,
                z.get(const.ZONE_DURATION),
                decision.duration,
                decision.deficit,
            )
            out.append({**z, const.ZONE_DURATION: decision.duration})
        return out

    def _zone_run_decision(
        self,
        zone: dict,
        estimates: dict,
        metric: bool,
        *,
        started: bool = False,
        quiet: bool = False,
    ):
        """Whether ``zone`` waters now, for how long, and how depleted it is.

        The single place the demand gate and the run length are decided, shared
        by the run itself (:meth:`_apply_live_durations`), the finish-anchor
        duration estimate and the fitting decision point. They used to answer
        this question three different ways: the estimate read the stored daily
        ``duration`` while the run under the live gate used
        ``duration_from_deficit(live_deficit)`` over a different zone set, so the
        anchor was wrong in both directions at once.

        No side effects — no markers, no writes, no estimate refresh — so the
        estimator can call it as often as it likes. ``estimates`` is the already
        refreshed map; pass ``{}`` to evaluate on the daily ledger alone.
        ``quiet`` goes with that: a projection re-prices every zone on every
        estimate refresh, and narrating each one produced bursts of identical
        lines about a run that was not happening. Only a caller that is really
        about to water leaves it off.

        ``started`` marks a zone this run has ALREADY watered, which drops the
        trigger threshold and leaves only the sizing. A rotation commits every
        slot's water, so a started zone's own credits lift its live deficit
        towards the threshold: re-applying the trigger there would end the zone
        the moment it crossed, refilling it to its threshold rather than to
        capacity and leaving the rest of a planned run undelivered. Capacity is
        the only gate that belongs to a started zone, and it arrives on its own
        as a re-priced duration of 0 (``duration_from_deficit`` is 0 at
        ``deficit >= 0``). Rain still shortens and still drops it — through the
        sizing, which is untouched.

        Returns None when the zone does not water.
        """
        threshold = zone.get(const.ZONE_BUCKET_THRESHOLD) or 0
        bucket = zone.get(const.ZONE_BUCKET) or 0
        daily_needs = (zone.get(const.ZONE_DURATION) or 0) > 0 and (
            started or bucket < threshold
        )

        def _daily():
            if not daily_needs:
                return None
            return _ZoneRunDecision(
                duration=float(zone.get(const.ZONE_DURATION) or 0),
                deficit=bucket,
                ratio=_depletion_ratio(bucket, threshold),
                resized=False,
            )

        live_gate = getattr(self.store.config, "live_estimate_enabled", False) is True
        if not live_gate or zone.get(const.ZONE_FLOW_SENSOR):
            # Flow zones deliver to a measured volume, not a recomputed
            # duration — keep the daily deficit gate for them even under the
            # live gate.
            return _daily()

        est = estimates.get(str(zone.get(const.ZONE_ID)))
        deficit = est.get("live_deficit") if est else None
        if deficit is None:
            # No live estimate — fall back to the daily gate rather than
            # watering blind.
            return _daily()
        if deficit >= threshold and not started:
            if not quiet:
                _LOGGER.debug(
                    "Live-estimate watering: zone %s live deficit %.2f hasn't "
                    "crossed the threshold %.2f — not watering this run",
                    zone.get(const.ZONE_ID),
                    deficit,
                    threshold,
                )
            return None
        live = self._duration_for_deficit(zone, deficit, metric)
        if live <= 0:
            return None
        return _ZoneRunDecision(
            duration=float(live),
            deficit=deficit,
            ratio=_depletion_ratio(deficit, threshold),
            resized=True,
        )

    def _duration_for_deficit(self, zone: dict, deficit: float, metric: bool) -> int:
        """``duration_from_deficit`` for this zone, warning when the cap bites.

        A ``maximum_duration`` clamp emits nothing at all: the shortfall simply
        never gets watered, so deepening ``bucket_threshold`` past what the caps
        can deliver is silently ignored and the zone drifts drier every cycle.
        Surface it instead of letting the zone quietly under-water.
        """
        duration = zone_run_duration(zone, deficit, metric)
        uncapped = zone_run_duration(zone, deficit, metric, capped=False)
        if uncapped > duration:
            self._warn_duration_clamped(zone, duration, uncapped)
        return duration

    def _warn_duration_clamped(self, zone: dict, capped: float, wanted: float) -> None:
        """Warn once per zone that its maximum_duration is cutting the run."""
        warned = getattr(self, "_duration_clamp_warned", None)
        if warned is None:
            warned = self._duration_clamp_warned = set()
        zid = int(zone.get(const.ZONE_ID))
        if zid in warned:
            return
        warned.add(zid)
        _LOGGER.warning(
            "Zone %s needs %ss of watering but its maximum duration caps the run "
            "at %ss, so %ss of the deficit goes unwatered every run. Raise the "
            "zone's maximum duration, or the cap — not the bucket threshold — is "
            "what decides how much this zone ever receives",
            zone.get(const.ZONE_ID),
            round(wanted),
            round(capped),
            round(wanted - capped),
        )

    def sequencing_timing(self) -> tuple[str, float, float]:
        """``(sequencing, slot_seconds, absorption_seconds)`` for the wall-clock model.

        Read defensively: this feeds the finish-anchor estimate and the fitting
        decision point, both of which run while arming a schedule. An unreadable
        setting there would raise inside a tracker setup and leave the schedule
        silently unarmed, so a bad value degrades to the runner's own defaults
        instead — the same ``or``-fallbacks ``_run_rotation`` applies.
        """

        def _number(value, default):
            try:
                return float(value)
            except (TypeError, ValueError):
                return float(default)

        config = self.store.config
        sequencing = getattr(config, "zone_sequencing", None)
        if sequencing not in (
            const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
            const.CONF_ZONE_SEQUENCING_PARALLEL,
            const.CONF_ZONE_SEQUENCING_ROTATING,
        ):
            # Sequential, not CONF_DEFAULT_ZONE_SEQUENCING. The default is
            # parallel, i.e. max(), the SHORTEST reduction, and this module's
            # rule is that only an over-estimate is safe because an
            # under-estimate finishes the irrigation after the requested time.
            sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
        slot_minutes = _number(
            getattr(config, "zone_sequencing_max_consecutive_duration", None) or 5, 5
        )
        absorption_minutes = _number(
            getattr(config, "zone_sequencing_min_absorption_time", None) or 0, 0
        )
        return (
            sequencing,
            max(1.0, slot_minutes) * 60,
            max(0.0, absorption_minutes) * 60,
        )

    async def async_plan_zone_runs(
        self, zone_ids=None, *, runnable_only=False, ignore_demand=False
    ) -> list:
        """The zones a scheduled run would water right now, and for how long.

        Read-only: the demand and sizing rules :meth:`_irrigate_linked_entities`
        applies, evaluated without touching anything. Feeds the finish-anchor
        duration estimate and the fitting decision point, so both agree on the
        zone set and the durations by construction.

        ``runnable_only`` adds the runner's own actuation requirement — a linked
        entity or a self-closing service. Fitting sets it, because it may only
        drop zones this integration is actually going to run. The finish-anchor
        estimate does NOT: an install that drives its valves externally (no
        linked entity anywhere) still watches the schedule's start event and
        still spends that time watering, so requiring an entity there would
        collapse its anchor to zero and fire every run at the target instead of
        a run-length before it.

        Distributor members are excluded — they water through their
        distributor's own cycle, which is estimated on its own track. The
        soil-moisture veto and the rain delay are NOT applied: both read live
        sensor state and the veto re-anchors buckets, so they belong to the run
        path, not to a projection that may be evaluated hours ahead.
        """
        zones = await self.store.async_get_zones()
        selection = normalize_zone_selection(zone_ids)
        target = None if selection is None else {int(z) for z in selection}

        eligible = [
            z
            for z in zones
            # Shared with the nominal projection rather than restated, so the
            # two cannot drift into planning over different zone sets.
            if zone_eligible_for_demand(z)
            and (target is None or int(z.get(const.ZONE_ID)) in target)
            and (
                not runnable_only
                or z.get(const.ZONE_LINKED_ENTITY)
                or self._sc_is_self_closing(z)
            )
        ]
        if not eligible:
            return []

        estimates = {}
        if getattr(self.store.config, "live_estimate_enabled", False) is True:
            try:
                estimates = await self.async_get_cached_zone_estimates()
            except Exception as e:  # noqa: BLE001 — a projection must not raise
                _LOGGER.debug("Run plan: live estimates unavailable: %s", e)
                estimates = {}

        metric = self.hass.config.units is METRIC_SYSTEM
        planned = []
        for zone in eligible:
            decision = self._zone_run_decision(zone, estimates, metric, quiet=True)
            if decision is None or decision.duration <= 0:
                if not ignore_demand:
                    continue
                # ignore_demand: the caller wants the shape of the run rather
                # than tonight's demand — it is pricing configured ceilings for
                # a decision point that may be hours away, by which time a zone
                # that is satisfied now can be due. Duration 0 keeps it out of
                # any wall-clock sum that uses the live durations.
                decision = None
            duration = decision.duration if decision else 0.0
            if duration > 0 and zone.get(const.ZONE_FLOW_SENSOR):
                # The decision priced this zone's volume at its CONFIGURED
                # throughput, the way a timed zone is priced. Its own runs have
                # measured what the plumbing actually delivers.
                duration = calibrated_flow_seconds(zone, duration, metric)
            planned.append(
                ZoneRun(
                    zone_id=int(zone.get(const.ZONE_ID)),
                    duration=duration,
                    depletion_ratio=decision.ratio if decision else 0.0,
                    last_irrigation=zone.get(const.ZONE_LAST_IRRIGATION),
                    maximum_duration=zone.get(const.ZONE_MAXIMUM_DURATION),
                    track=track_for_zone(zone),
                    lead_time=zone.get(const.ZONE_LEAD_TIME) or 0.0,
                    flow=bool(zone.get(const.ZONE_FLOW_SENSOR)),
                    confirm_seconds=self._zone_confirm_seconds(zone),
                    station=station_facts(self.hass, zone),
                )
            )
        self._log_station_grouping(planned)
        return planned

    def _zone_confirm_seconds(self, zone: dict) -> float:
        """Seconds this zone's dispatch may spend confirming its valve opened.

        Paid before any water flows and modelled nowhere:
        ``_run_valve_metered`` sets ``elapsed = 0`` only once
        ``_confirm_valve_running`` has returned, so on a chain the whole poll
        lands between one zone's water and the next. Reported at the poll's
        ceiling because the only caller is an arm reserving room for it -- a
        valve that reports back promptly simply leaves the run finishing early.

        Zero for the dispatches that never poll: a station, where the controller
        owns the open and a queued station is not running at +30s anyway, and a
        self-closing valve with no confirm entity, which is credited
        optimistically.
        """
        if self._sc_is_self_closing(zone):
            confirm = zone.get(const.ZONE_CONFIRM_ENTITY)
            if not confirm or is_opensprinkler_zone(zone):
                return 0.0
            return float(const.VALVE_CONFIRM_TIMEOUT)
        if is_opensprinkler_zone(zone) or not zone.get(const.ZONE_LINKED_ENTITY):
            return 0.0
        return float(const.VALVE_CONFIRM_TIMEOUT)

    def _log_station_grouping(self, planned: list) -> None:
        """Say, once, whether the controller's grouping priced the station track.

        A run length nobody expected is usually the fallback: without the group
        the track is priced as a chain, which is the longer answer, and nothing
        else a user can read says which of the two they got.

        Logged on change rather than per call because the plan is rebuilt on
        every estimate refresh and every re-arm. The controller going
        unavailable and coming back is exactly the transition worth an INFO
        line.
        """
        stations = [p for p in planned if p.track == TRACK_STATION]
        if not stations:
            return
        unread = [p for p in stations if p.station is None or p.station.group is None]
        state = (len(stations), len(unread))
        repeat = getattr(self, "_station_grouping_logged", None) == state
        self._station_grouping_logged = state
        log = _LOGGER.debug if repeat else _LOGGER.info
        if unread:
            log(
                "Run window: the controller's station grouping is unavailable "
                "for %d of %d station zone(s); pricing the station track as a "
                "chain",
                len(unread),
                len(stations),
            )
        else:
            log(
                "Run window: pricing %d station zone(s) from the controller's "
                "own station groups",
                len(stations),
            )

    async def async_nominal_demand_seconds(self, zone_ids=None) -> float:
        """Wall-clock seconds a schedule's run takes on a typical night.

        Unlike :meth:`async_plan_zone_runs`, this never reads a zone's live
        bucket or the live-estimate deficit — every eligible zone is priced as
        if it had just crossed its own threshold (see
        :func:`run_window.nominal_zone_duration`), so the answer holds steady
        across calc cycles and is safe to publish before a schedule's own
        estimate has ever run. ``zone_ids`` is the schedule's own ``zones``
        selection (``"all"`` or a list), normalized the same way the run
        planner normalizes it.
        """
        zones = await self.store.async_get_zones()
        selection = normalize_zone_selection(zone_ids)
        target = None if selection is None else {int(z) for z in selection}
        in_scope = [
            z for z in zones if target is None or int(z.get(const.ZONE_ID)) in target
        ]
        sequencing, slot_seconds, absorption_seconds = self.sequencing_timing()
        metric = self.hass.config.units is METRIC_SYSTEM
        # The projection module cannot read an entity, so the controller's own
        # grouping is gathered here — without it the dial would draw a station
        # chain the controller does not run.
        return nominal_demand_seconds(
            in_scope,
            sequencing=sequencing,
            max_slot_seconds=slot_seconds,
            min_absorption_seconds=absorption_seconds,
            metric=metric,
            station_facts=station_facts_by_zone(self.hass, in_scope),
        )

    def _warn_if_low_maximum_bucket(self, zone: dict, metric: bool) -> None:
        """Warn once per zone when live-estimate watering runs against a small
        ``maximum_bucket`` that can clip banked intra-day water and drift the
        daily ledger drier (see ``LIVE_MIN_MAXIMUM_BUCKET_MM``)."""
        max_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
        if max_bucket is None:
            return
        max_bucket_mm = (
            float(max_bucket)
            if metric
            else convert_between(const.UNIT_INCH, const.UNIT_MM, float(max_bucket))
        )
        if max_bucket_mm >= const.LIVE_MIN_MAXIMUM_BUCKET_MM:
            return
        warned = getattr(self, "_live_low_max_warned", None)
        if warned is None:
            warned = self._live_low_max_warned = set()
        zid = int(zone.get(const.ZONE_ID))
        if zid in warned:
            return
        warned.add(zid)
        _LOGGER.warning(
            "Live-estimate watering is on but zone %s has a small maximum bucket "
            "(%.1f mm < %.1f mm). Watering more than once a day can bank more "
            "water than that ceiling holds, so it gets clipped and the daily "
            "calculation may drift drier over time. Raise the maximum bucket to "
            "at least a day's ET to be safe.",
            zone.get(const.ZONE_ID),
            max_bucket_mm,
            const.LIVE_MIN_MAXIMUM_BUCKET_MM,
        )

    def _depth_from_volume_native(self, zone: dict, volume_l: float) -> float:
        """Depth (display units) that ``volume_l`` litres applies to ``zone``.

        Metric: litres / m² == mm. Imperial: convert area to m², then mm → inch.
        Shared by every metered run path so the bucket is credited by the volume
        actually delivered — synthetic ``throughput × time`` or a real flow
        sensor — exactly as the observed-watering crediting does.
        """
        size = zone.get(const.ZONE_SIZE) or 0.0
        if size <= 0 or not volume_l or volume_l <= 0:
            return 0.0
        if self.hass.config.units is METRIC_SYSTEM:
            return volume_l / size  # litres / m² == mm
        size_m2 = convert_between(const.UNIT_SQ_FT, const.UNIT_M2, size)
        applied_mm = volume_l / size_m2
        return convert_between(const.UNIT_MM, const.UNIT_INCH, applied_mm)

    def _credited_depth_native(self, zone: dict, volume_l: float) -> float:
        """Bucket depth credited for a *timed* run delivering ``volume_l``.

        A timed run's duration is inflated by the zone multiplier (the multiplier
        is part of the computed need — ``duration = multiplier × base``), so the
        gross delivered depth is divided by the multiplier before crediting. This
        lands a full run's bucket exactly at its target for ANY multiplier —
        faithfully generalising the old unconditional reset-to-target, and
        crediting partial/crashed runs proportionally. Flow zones are
        volume-targeted (no multiplier) and credit the gross depth directly via
        :meth:`_depth_from_volume_native`.
        """
        depth = self._depth_from_volume_native(zone, volume_l)
        mult = zone.get(const.ZONE_MULTIPLIER) or 1.0
        return depth / mult if mult > 0 else depth

    def _run_ceiling(self, zone: dict) -> float:
        """Bucket level (display units) a run may credit *up to*.

        Normal / real-flow runs replenish only to the post-run target floor
        (0.0, or the forecast-weighting remainder). Live-estimate runs (WS-3,
        marked in ``_live_run_zones``) came from the intra-day deficit, which can
        exceed the stored daily bucket — so they may credit up to ``maximum_bucket``
        (a surplus), matching the live-estimate crediting that used to live in
        ``_reset_zone_bucket_after_run``. The marker is consumed here.
        """
        zid = int(zone.get(const.ZONE_ID))
        live = getattr(self, "_live_run_zones", None)
        if live and zid in live:
            live.discard(zid)
            max_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
            return float(max_bucket) if max_bucket is not None else float("inf")
        return self._zone_target_bucket(zone)

    async def async_write_watered_bucket(
        self, zone_id, new_bucket: float, extra_changes: dict | None = None
    ) -> None:
        """Write a bucket level that moved because water was applied JUST NOW.

        Every credit path writes the bucket absolutely (``pre_bucket + depth``,
        or a reconcile back to ``pre_bucket + measured``), so the water this
        write represents is the difference against the level currently stored.
        Booking that difference on ``ZONE_PENDING_BUCKET_EVENTS`` with its
        timestamp is what lets the next calculation replay it at the moment it
        happened rather than at the window start, where it would be charged
        drainage for hours it was not in the soil.

        Deliberately NOT hooked into ``store.async_update_zone``, which every
        bucket write funnels through: that would also book the writes where no
        water moved — a metric/imperial flip rewrites the bucket by 25.4, and
        booking that as ~19 mm of irrigation would wreck the balance far worse
        than the drainage error this fixes. Only water calls here.

        The bucket is stored in display units; the ledger is mm (see
        ``const.ZONE_PENDING_BUCKET_EVENTS``).
        """
        zone = self.store.get_zone(zone_id) or {}
        changes = dict(extra_changes or {})
        changes[const.ZONE_BUCKET] = new_bucket
        try:
            delta = float(new_bucket) - float(zone.get(const.ZONE_BUCKET) or 0)
        except (TypeError, ValueError):
            delta = 0.0
        if delta:
            if self.hass.config.units is not METRIC_SYSTEM:
                delta = convert_between(const.UNIT_INCH, const.UNIT_MM, delta)
            events = list(zone.get(const.ZONE_PENDING_BUCKET_EVENTS) or [])
            events.append({"ts": dt_util.now().isoformat(), "mm": delta})
            changes[const.ZONE_PENDING_BUCKET_EVENTS] = events[
                -const.PENDING_BUCKET_EVENTS_MAX :
            ]
        if delta > 0:
            # This zone just received water, so its days-between wait restarts —
            # here, in the same write as the credit, because this is the only
            # place that knows it happened. The dispatcher cannot: a sequential
            # or rotating run is a background task that can still be watering
            # hours later, so anything reset at dispatch time is reset for zones
            # a mid-run re-price will never actually water. That is precisely
            # the starvation the per-zone counter exists to stop. Every credit
            # path funnels through here (timed, flow, distributor, self-closing,
            # and observed external runs), so all of them count.
            changes[const.ZONE_DAYS_SINCE_IRRIGATION] = 0
        await self.store.async_update_zone(zone_id, changes)

    async def _commit_run_progress(
        self, zone_id, *, new_bucket: float, volume_delta_l: float, dispatch: bool
    ) -> None:
        """Persist mid-run progress: bucket level + incremental water usage.

        ``new_bucket`` is an absolute, idempotent recompute
        (``min(ceiling, original + cumulative_delivered_depth)``) so re-writing it
        is always safe. ``volume_delta_l`` is the litres delivered *since the last
        commit* — only ever the increment, never the cumulative, so the monotonic
        ``water_used_total`` counter can never double-count (the failure mode
        behind the v2026.06.36 runaway total). The caller gates ``dispatch`` to a
        coarse cadence so the ``_config_updated`` weather fan-out stays cheap.
        """
        zone = self.store.get_zone(zone_id) or {}
        changes = {}
        if volume_delta_l and volume_delta_l > 0:
            # Only stamp "last irrigation" + the usage counter when water actually
            # flowed this commit, so a failed / never-started run (which still
            # commits an unchanged bucket) does not claim it just watered.
            changes[const.ZONE_LAST_IRRIGATION] = dt_util.now()
            changes[const.ZONE_WATER_USED_TOTAL] = (
                zone.get(const.ZONE_WATER_USED_TOTAL) or 0.0
            ) + volume_delta_l
        await self.async_write_watered_bucket(zone_id, new_bucket, changes)
        if dispatch:
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)

    # --- Run history + cumulative water usage (WS-2) ------------------------

    def _throughput_lpm(self, zone: dict) -> float:
        """The zone's configured throughput in L/min (volume accounting unit)."""
        throughput = zone.get(const.ZONE_THROUGHPUT) or 0.0
        if self.hass.config.units is METRIC_SYSTEM:
            return throughput
        return convert_between(const.UNIT_GPM, const.UNIT_LPM, throughput)

    def _timed_volume_l(self, zone: dict, seconds: float) -> float:
        """Litres a timed run delivers: run minutes × throughput."""
        if not seconds or seconds <= 0:
            return 0.0
        return self._throughput_lpm(zone) * (seconds / 60.0)

    async def _stamp_run_finalized(self, zone_id, volume_l) -> None:
        """Stamp the post-run bookkeeping a driven (metered) run gets for free.

        Self-closing runs (``_sc_finish_run`` / ``async_stop_self_closing``) and
        distributor-member runs (``_dist_credit_zone``) credit the bucket DIRECTLY
        and never pass through ``_commit_run_progress`` — the only run-path that
        stamps ``ZONE_LAST_IRRIGATION`` when water flows. So without this the
        "Last irrigation" sensor never advances for those zones. And the store's
        ``bucket == 0 -> duration 0`` shortcut also misses, because a MEASURED run
        lands the bucket slightly POSITIVE (measured overshoot), never exactly 0 —
        leaving the displayed "Duration" stale too. Mirror both here: stamp
        ``last_irrigation`` when water was delivered, and zero the duration once an
        automatic zone is left satisfied (bucket >= 0), matching the store
        shortcut's intent (no deficit -> nothing to water).
        siehe test_self_closing.py::test_finish_stamps_last_irrigation_and_zeroes_duration_when_satisfied
        """
        changes = {}
        if volume_l and volume_l > 0:
            changes[const.ZONE_LAST_IRRIGATION] = dt_util.now()
        zone = self.store.get_zone(zone_id) or {}
        if (
            zone.get(const.ZONE_STATE) == const.ZONE_STATE_AUTOMATIC
            and float(zone.get(const.ZONE_BUCKET) or 0) >= 0
        ):
            changes[const.ZONE_DURATION] = 0
        if changes:
            await self.store.async_update_zone(zone_id, changes)

    async def _record_run(
        self,
        zone_id,
        *,
        result: str,
        volume_l: float = 0.0,
        planned_s: float | None = None,
        actual_s: float | None = None,
        detail: str | None = None,
        trigger: str = "schedule",
        add_to_total: bool = True,
    ) -> None:
        """Append a run-log entry and add delivered water to the usage total.

        The run log is a bounded list (newest first, capped at
        ``RUN_LOG_MAX_ENTRIES``) persisted on the zone; ``water_used_total`` is a
        monotonic litre counter backing the usage statistics sensor. Both live in
        the store so they survive restarts.

        ``add_to_total`` controls whether ``volume_l`` is added to the cumulative
        counter. Metered runs credit the counter *incrementally* while the valve
        is open (:meth:`_commit_run_progress`), so their final completion record
        passes ``add_to_total=False`` — the log row still shows the total volume
        for display, but it is not double-counted into ``water_used_total``.
        """
        zone = self.store.get_zone(zone_id) or {}
        entry = {
            "ts": dt_util.now().isoformat(),
            "trigger": trigger,
            "planned_s": round(planned_s) if planned_s is not None else None,
            "actual_s": round(actual_s) if actual_s is not None else None,
            "volume_l": round(volume_l, 2) if volume_l else 0.0,
            "result": result,
            "detail": detail,
        }
        log = list(zone.get(const.ZONE_RUN_LOG) or [])
        log.insert(0, entry)
        # Bound the log, but never let a routine skip marker evict a REAL run
        # (Option C, review of the no-demand feature): a zone that rarely waters
        # would otherwise fill its whole history with marker rows and push the
        # real runs — the very thing the user is trying to understand — out. Drop
        # the OLDEST marker entries first; only if none remain do we fall back
        # to trimming the oldest overall. siehe
        # test_no_demand_logging.py::test_real_run_evicts_oldest_no_demand_before_a_real_run
        # Stop at index 1, NOT 0: index 0 is the entry we just inserted. Scanning
        # it too meant that on a log already full of REAL runs — the steady state
        # for any established zone, and one that never drains on its own because
        # a zone that stopped watering records no new real runs — an incoming
        # no_demand entry was the only no_demand the scan could find, so it
        # deleted itself. Measured: 0 no_demand entries after 30 days. The
        # feature then does nothing for exactly the case it exists to answer
        # ("this zone used to water and now it doesn't"). Excluding the new entry
        # softens the invariant to "no_demand never occupies more than one slot
        # once the log is full" — 49 real + 1 no_demand, indefinitely.
        # siehe test_no_demand_logging.py::test_a_full_log_of_real_runs_still_shows_no_demand
        overflow = len(log) - const.RUN_LOG_MAX_ENTRIES
        if overflow > 0:
            for i in range(len(log) - 1, 0, -1):
                if overflow <= 0:
                    break
                e = log[i]
                if (
                    e.get("result") == const.RUN_RESULT_SKIPPED
                    and e.get("detail") in _EVICTABLE_SKIP_DETAILS
                ):
                    del log[i]
                    overflow -= 1
            del log[const.RUN_LOG_MAX_ENTRIES :]
        changes = {const.ZONE_RUN_LOG: log}
        if add_to_total and volume_l and volume_l > 0:
            changes[const.ZONE_WATER_USED_TOTAL] = (
                zone.get(const.ZONE_WATER_USED_TOTAL) or 0.0
            ) + volume_l
        await self.store.async_update_zone(zone_id, changes)
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)

    async def async_reset_water_usage(self, zone_id) -> None:
        """Zero a zone's cumulative water-usage total and clear its run log.

        Recovery action (per-zone "reset usage" button) for when the counter
        gets corrupted; both fields back the usage sensor and the history card.
        """
        zid = int(zone_id)
        if self.store.get_zone(zid) is None:
            _LOGGER.warning("Reset water usage: zone %s not found", zid)
            return
        await self.store.async_update_zone(
            zid,
            {const.ZONE_WATER_USED_TOTAL: 0.0, const.ZONE_RUN_LOG: []},
        )
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zid)
        _LOGGER.info("Reset water-usage total + run log for zone %s", zid)

    async def _record_skipped_run(
        self, zone_ids, detail: str | None, trigger: str = "schedule"
    ) -> None:
        """Log a skipped scheduled irrigation for each (enabled) targeted zone."""
        zones = await self.store.async_get_zones()
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}
        for z in zones:
            if z.get(const.ZONE_STATE) == const.ZONE_STATE_DISABLED:
                continue
            zid = int(z.get(const.ZONE_ID))
            if target is not None and zid not in target:
                continue
            await self._record_run(
                zid,
                result=const.RUN_RESULT_SKIPPED,
                detail=detail,
                trigger=trigger,
            )

    def _skip_logged_today(self, zone_id: int, detail: str) -> bool:
        """Whether this zone already has a ``detail`` skip dated today.

        Review finding H: dedup by SCANNING the log rather than checking log[0].
        An intervening same-day run (e.g. a manual completed run between two
        schedules) displaces the earlier marker out of the newest slot, so a
        head-only check missed it and wrote a second entry the same calendar
        day. Entries are newest-first, so stop at the first older-than-today ts.
        siehe test_no_demand_logging.py::test_helper_dedups_same_day_with_intervening_run
        """
        today = dt_util.now().date().isoformat()
        zone = self.store.get_zone(int(zone_id)) or {}
        for entry in zone.get(const.ZONE_RUN_LOG) or []:
            ts = str(entry.get("ts") or "")[:10]
            if ts and ts < today:
                break
            if (
                ts == today
                and entry.get("result") == const.RUN_RESULT_SKIPPED
                and entry.get("detail") == detail
            ):
                return True
        return False

    async def _record_once_daily_skips(self, zone_ids, detail: str) -> None:
        """Record a routine skip marker for each zone, once per calendar day.

        Shared by the two markers a schedule can repeat every night without the
        zone's situation changing. Their gating differs and stays with the
        caller; the dedup and the write are the same either way.

        ``add_to_total=False`` — a skip delivers no water.
        """
        for zid in zone_ids:
            if self._skip_logged_today(int(zid), detail):
                continue
            await self._record_run(
                int(zid),
                result=const.RUN_RESULT_SKIPPED,
                detail=detail,
                trigger="schedule",
                add_to_total=False,
            )

    async def _record_days_between_skips(self, zone_ids) -> None:
        """Record a per-zone days-between hold in the run history.

        Not opt-in, unlike the no-demand marker: the guard itself is off by
        default, so only an install that asked for the wait sees these at all,
        and there the hold is the answer to "why did this zone not water".

        One entry per zone per calendar day. A zone at ``days_between = 3`` is
        held on every run for two days running, so an install with several
        schedules a day would otherwise bury its real runs under repeats of the
        same fact.
        """
        await self._record_once_daily_skips(zone_ids, const.SKIP_REASON_DAYS_BETWEEN)

    async def _record_no_demand_skips(self, zone_ids) -> None:
        """Record a per-zone "no demand" skip in the run history, if opted in.

        Opt-in via ``config.log_no_demand`` (default off, so existing installs
        are byte-identical). Suppressed while a rain delay is active — that path
        already logs ``paused`` for the targeted zones and would otherwise
        double-log. De-duplicated to at most one ``no_demand`` entry per zone per
        calendar day, so multiple schedules in a day do not spam the run log.

        ``add_to_total=False`` — a skip delivers no water.
        siehe test_no_demand_logging.py::test_helper_records_when_enabled et al.
        """
        if not getattr(self.store.config, "log_no_demand", False):
            return
        if self._rain_delay_active():
            return
        await self._record_once_daily_skips(zone_ids, const.SKIP_REASON_NO_DEMAND)

    async def _irrigate_zones_sequential(
        self, zones: list, *, master_token=None, deadline=None
    ):
        """Irrigate zones one after another, skipping zones with no duration.

        Holds the master for the WHOLE chain, so the pump covers every zone plus
        the per-zone valve-confirm polling and any flow zone that outruns its
        nominal duration — none of which a predicted deadline could size.

        With a ``deadline`` each zone runs for ``min(duration, remaining)`` and
        the chain stops once the window is spent. A cut zone keeps the water it
        received: ``_commit_run_progress`` recomputes the bucket from the volume
        actually delivered, so the residual simply carries to the next run and
        sorts that zone ahead of everything.
        """
        claimed = self._claim_chain_zones(zones)
        try:
            metric = self.hass.config.units is METRIC_SYSTEM
            for queued in zones:
                if self._run_stopped(queued[const.ZONE_ID]):
                    # Stopped while it was still queued. The claim carries the
                    # stop event, so honour it here rather than opening the valve
                    # and closing it again one poll later. Checked before the
                    # re-price, which would otherwise refresh estimates for a
                    # zone that is not going to run.
                    _LOGGER.info(
                        "Sequential irrigation: zone %s was stopped before its "
                        "turn came; skipping it",
                        queued[const.ZONE_ID],
                    )
                    self._unregister_active_run(queued[const.ZONE_ID])
                    continue
                zone = await self._resize_queued_zone(queued, metric)
                if zone is None:
                    continue
                entity_id = zone[const.ZONE_LINKED_ENTITY]
                real_flow = bool(zone.get(const.ZONE_FLOW_SENSOR))
                cut_from = None
                if deadline is not None:
                    remaining = (deadline - dt_util.utcnow()).total_seconds()
                    if remaining <= 0:
                        _LOGGER.warning(
                            "Sequential irrigation: run deadline %s reached with "
                            "zone %s (and any after it) unwatered; their deficit "
                            "carries and they lead the next run",
                            deadline,
                            zone[const.ZONE_ID],
                        )
                        break
                    if (zone.get(const.ZONE_DURATION) or 0) > remaining:
                        _LOGGER.warning(
                            "Sequential irrigation: zone %s cut from %ss to %ss "
                            "by the run deadline %s",
                            zone[const.ZONE_ID],
                            round(zone.get(const.ZONE_DURATION) or 0),
                            round(remaining),
                            deadline,
                        )
                        # A flow zone delivers to a measured volume and reads
                        # its safety timeout from maximum_duration, so cutting
                        # ZONE_DURATION does not shorten its run and must not be
                        # logged as though it had.
                        if not real_flow:
                            cut_from = float(zone.get(const.ZONE_DURATION) or 0)
                        zone = {**zone, const.ZONE_DURATION: remaining}
                _LOGGER.info(
                    "Sequential irrigation: zone %s (%s)",
                    zone[const.ZONE_ID],
                    "flow meter" if real_flow else "timed",
                )
                await self._run_valve_metered(
                    zone,
                    entity_id,
                    real_flow=real_flow,
                    trigger=self._run_trigger(zone[const.ZONE_ID]),
                    deadline_cut_from=cut_from,
                )
                _LOGGER.info("Sequential irrigation: finished %s", entity_id)
        finally:
            # Zones the chain never reached (a stop, or an exception) are still
            # claimed; drop them or they block that zone's runs for good.
            await self._release_chain_zones(claimed)
            if master_token:
                await self.async_master_release(master_token)

    async def _resize_queued_zone(self, zone: dict, metric: bool, *, started=False):
        """Re-price a zone that has been waiting its turn, or drop it.

        A sequential chain can be hours long, and the zone dict was sized when
        the run was dispatched. Rain three hours into it should shorten — or
        cancel — the zones that have not started yet, rather than watering a
        soil profile that has already been refilled.

        Read-only by construction: it re-reads the stored zone and refreshes the
        live estimate cache, but commits nothing, so it neither writes a bucket
        mid-run nor collides with the calculation's mid-run deferral.

        Only ever shortens. A grown deficit is left alone: the run was dispatched
        against a window, and silently extending a zone past the length the
        selection was sized on would push the whole chain out. Returns None when
        the zone should now be skipped; falls back to the queued zone unchanged
        if anything about the re-derivation is unavailable.

        ``started`` is for the rotation, which returns to a zone it has already
        watered: see :meth:`_zone_run_decision` for why that zone is gated on
        capacity rather than on its trigger threshold.
        """
        config = getattr(self.store, "config", None)
        if getattr(config, "live_estimate_enabled", False) is not True:
            return zone
        zid = int(zone.get(const.ZONE_ID))
        planned = zone.get(const.ZONE_DURATION) or 0
        try:
            fresh = self.store.get_zone(zid)
            # Throttled, not the bare refresh: this runs once per zone in a
            # chain and once per zone per lap in a rotation, plus again after
            # every absorption pause, and each bare call recomputes every zone
            # and fires _estimates_updated. Not the plain cache either — the
            # whole point is to see rain that fell since dispatch, which a cache
            # with no floor on its age cannot show.
            await self.async_refresh_zone_estimates_throttled()
            estimates = await self.async_get_cached_zone_estimates()
        except Exception as e:  # noqa: BLE001 — never abort a run over a re-price
            _LOGGER.debug("Zone %s: could not re-price before its turn: %s", zid, e)
            return zone
        if not fresh:
            return zone
        decision = self._zone_run_decision(fresh, estimates, metric, started=started)
        if decision is None or decision.duration <= 0:
            _LOGGER.info(
                "Zone %s no longer needs water by the time its turn came "
                "(rain or an earlier credit); skipping the rest of its run",
                zid,
            )
            # Release the live-crediting marker the dispatch took for this zone,
            # or the next run to credit it would be handed a ceiling meant for a
            # run that never happened.
            live = getattr(self, "_live_run_zones", None)
            if live:
                live.discard(zid)
            return None
        if decision.duration >= planned:
            return zone
        _LOGGER.info(
            "Zone %s re-priced from %ss to %ss before its turn (live deficit %.2f)",
            zid,
            round(planned),
            round(decision.duration),
            decision.deficit,
        )
        return {**zone, const.ZONE_DURATION: decision.duration}

    async def _irrigate_zones_parallel(self, zones: list, *, deadline=None):
        """Start all zone entities simultaneously, each accounting for its own run.

        One master hold per zone, taken here (before the task exists) and released
        by that zone's runner — see _dispatch_sequencing on why acquiring inside
        the task would race.

        ``deadline`` is the UTC moment a fitted run must be finished by. Every
        zone opens now, so one remaining window applies to all of them and each
        is dispatched for ``min(duration, remaining)``: a zone the selection
        could not fit is cut where the target falls instead of watering past it,
        and a zone already inside the window is untouched.
        """
        remaining = None
        if deadline is not None:
            remaining = (deadline - dt_util.utcnow()).total_seconds()
            if remaining <= 0:
                _LOGGER.warning(
                    "Parallel irrigation: run deadline %s reached before any zone "
                    "opened; zones %s stay unwatered and their deficit carries",
                    deadline,
                    [z[const.ZONE_ID] for z in zones],
                )
                return
        for zone in zones:
            entity_id = zone[const.ZONE_LINKED_ENTITY]
            real_flow = bool(zone.get(const.ZONE_FLOW_SENSOR))
            cut_from = None
            if remaining is not None and (zone.get(const.ZONE_DURATION) or 0) > (
                remaining
            ):
                _LOGGER.warning(
                    "Parallel irrigation: zone %s cut from %ss to %ss by the run "
                    "deadline %s",
                    zone[const.ZONE_ID],
                    round(zone.get(const.ZONE_DURATION) or 0),
                    round(remaining),
                    deadline,
                )
                # See _irrigate_zones_sequential: a flow zone's run is not
                # actually shortened by cutting ZONE_DURATION.
                if not real_flow:
                    cut_from = float(zone.get(const.ZONE_DURATION) or 0)
                zone = {**zone, const.ZONE_DURATION: remaining}
            _LOGGER.info(
                "Parallel irrigation: zone %s (%s)",
                zone[const.ZONE_ID],
                "flow meter" if real_flow else "timed",
            )
            token = f"zone:{zone[const.ZONE_ID]}:{uuid.uuid4().hex[:8]}"
            await self.async_master_acquire(token)
            # Tracked task — see _dispatch_sequencing: a bare task holding a
            # valve open is GC-able mid-run and invisible to HA shutdown.
            self.hass.async_create_task(
                self._run_valve_metered(
                    zone,
                    entity_id,
                    real_flow=real_flow,
                    trigger=self._run_trigger(zone[const.ZONE_ID]),
                    master_token=token,
                    deadline_cut_from=cut_from,
                )
            )

    async def async_irrigate_now(self, zone_id: str | None = None):
        """Immediately irrigate — bypasses all skip conditions.

        If zone_id is provided, only irrigate that zone.
        Otherwise irrigate all zones that have a linked entity and duration > 0.
        """
        zones = await self.store.async_get_zones()

        if zone_id is not None:
            zones = [z for z in zones if str(z.get(const.ZONE_ID)) == str(zone_id)]

        # Distributor members are excluded from the direct linked-entity drive: a
        # member waters via its distributor's shared inlet, not its own valve, so a
        # stray linked_entity must not run it directly (review #9). Their
        # distributor(s) are dispatched separately below.
        zones_to_irrigate = [
            z
            for z in zones
            if (z.get(const.ZONE_LINKED_ENTITY) or self._sc_is_self_closing(z))
            and (z.get(const.ZONE_DURATION) or 0) > 0
            and z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
            and z.get(const.ZONE_DISTRIBUTOR_ID) is None
        ]
        # Single-flight, same as the scheduled path. Irrigate-now consults no
        # demand gate at all, so without this a second press simply starts a
        # second concurrent run on the same zone.
        zones_to_irrigate = self._drop_zones_already_running(zones_to_irrigate)

        target = "all" if zone_id is None else [zone_id]
        if zones_to_irrigate:
            await self._dispatch_by_mode(zones_to_irrigate, trigger="manual")
        else:
            _LOGGER.info("irrigate_now: no zones with linked entity and duration > 0")
        # Distributor member zones are excluded from the linked-entity path, so
        # dispatch their distributor(s) too (manual dispatch respects rain delay,
        # consistent with the distributor_run_now service).
        await self._dispatch_distributor_cycles(target)

    async def async_run_zone(self, zone_id, duration_minutes: float) -> None:
        """Run one zone for an explicit duration, decoupled from the calc (WS-5).

        Bypasses skip conditions, the deficit gate and the rain-delay hold (an
        explicit manual action). The delivered water is credited to the bucket
        via the WS-3 live-run path (``bucket += delivered``, capped) rather than
        zeroed, so a custom run honestly reduces the deficit and the next daily
        calc does not double-subtract.
        """
        seconds = round((duration_minutes or 0) * 60)
        if seconds <= 0:
            _LOGGER.warning("run_zone: non-positive duration, ignoring")
            return
        zone = self.store.get_zone(zone_id)
        if not zone:
            _LOGGER.warning("run_zone: zone %s not found", zone_id)
            return
        if zone.get(const.ZONE_STATE) == const.ZONE_STATE_DISABLED:
            _LOGGER.info("run_zone: zone %s is disabled, ignoring", zone_id)
            return
        # Single-flight, matching the distributor-busy rejection below: a custom
        # run must not interleave with a run already holding this zone's valve.
        if self.zone_run_in_flight(zone_id):
            _LOGGER.info(
                "run_zone: zone %s already has a run in flight, ignoring", zone_id
            )
            return
        # Self-closing zones run via their own service for the requested duration.
        # async_run_self_closing takes (and later releases) its own master hold.
        if self._sc_is_self_closing(zone):
            run_zone = dict(zone)
            run_zone[const.ZONE_DURATION] = seconds
            await self.async_run_self_closing(run_zone, trigger="manual")
            return
        if zone.get(const.ZONE_DISTRIBUTOR_ID) is not None:
            # M-BE: a member zone waters via its distributor's shared inlet, not its
            # own valve, so route the manual run through the ring — but now honour the
            # requested custom duration (passed as duration_override to the single-
            # outlet cycle) instead of the member's stored daily duration. Single-
            # flight guard: if the distributor already has a cycle in progress,
            # reject the manual run rather than interleaving a second sweep on the
            # shared inlet (mutual exclusion on the physical valve).
            # siehe test_distributor_dispatch.py::test_dispatch_passes_duration_override
            dist = self.store.get_distributor(zone.get(const.ZONE_DISTRIBUTOR_ID))
            if dist and dist.get("active_cycle"):
                _LOGGER.info(
                    "run_zone: distributor %s busy, ignoring member run for zone %s",
                    dist.get("id"),
                    zone_id,
                )
                return
            await self._dispatch_distributor_cycles(
                [zone_id], duration_override=float(seconds)
            )
            return
        if not zone.get(const.ZONE_LINKED_ENTITY):
            _LOGGER.warning("run_zone: zone %s has no linked entity", zone_id)
            return
        if self._zone_links_a_station(zone):
            return

        # Master (pump): _irrigate_zones_parallel below acquires the hold before it
        # spawns the run and the runner releases it when the valve shuts, so the
        # pump covers the real run length even if it overshoots `seconds`.

        # Override the duration on a copy and credit the bucket by what we deliver.
        run_zone = dict(zone)
        run_zone[const.ZONE_DURATION] = seconds
        live = getattr(self, "_live_run_zones", None)
        if live is None:
            live = self._live_run_zones = set()
        live.add(int(zone_id))
        manual = getattr(self, "_manual_run_zones", None)
        if manual is None:
            manual = self._manual_run_zones = set()
        manual.add(int(zone_id))
        _LOGGER.info(
            "run_zone: watering zone %s for %s seconds (manual)", zone_id, seconds
        )
        await self._irrigate_zones_parallel([run_zone])
