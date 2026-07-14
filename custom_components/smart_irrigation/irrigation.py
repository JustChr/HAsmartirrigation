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
from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .calculation import duration_from_deficit
from .flow_metering import (
    FlowMeter,
    flow_is_totalizer,
    flow_learn_next_streak,
    flow_learn_resolve,
    flow_litres_from_total,
)
from .helpers import convert_between
from .localize import localize

_LOGGER = logging.getLogger(__name__)

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

    def _register_active_run(self, zone_id, duration_seconds, *, has_end: bool):
        """Mark a zone's run as in-progress; return its stop ``asyncio.Event``.

        ``has_end`` is True for time-bounded (synthetic / manual) runs, so the
        dashboard can render a countdown to ``ends_at``; flow-metered runs are
        volume-bounded (unknown finish time) and register without an end.
        Dispatches ``_config_updated`` so the panel surfaces the Stop control.
        """
        reg = self._active_run_registry()
        zid = int(zone_id)
        event = asyncio.Event()
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
        }
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zid)
        return event

    def _unregister_active_run(self, zone_id) -> None:
        """Clear a zone's in-progress marker (run finished or was stopped)."""
        reg = getattr(self, "_active_runs", None)
        if reg and int(zone_id) in reg:
            del reg[int(zone_id)]
            async_dispatcher_send(
                self.hass, const.DOMAIN + "_config_updated", int(zone_id)
            )

    def get_active_runs(self) -> dict:
        """Return ``{zone_id: {started_at, ends_at}}`` for runs in progress."""
        reg = getattr(self, "_active_runs", None) or {}
        return {
            str(zid): {"started_at": d["started_at"], "ends_at": d["ends_at"]}
            for zid, d in reg.items()
        }

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
        """Stop every zone with an in-progress run."""
        reg = getattr(self, "_active_runs", None) or {}
        for zid in list(reg.keys()):
            await self.async_stop_zone(zid)

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

    @callback
    async def _irrigate_linked_entities(self, zone_ids=None) -> bool:
        """Directly control linked valve/switch entities for zones needing irrigation.

        ``zone_ids`` optionally restricts to a schedule's target zones (an
        iterable of ids, or None/"all" for every eligible zone).

        Returns ``True`` iff at least one real run was dispatched (self-closing
        service and/or the sequencing task), ``False`` on every no-water path
        (no candidates, rain delay, all soil-vetoed, live-estimate left nothing).
        The scheduled caller gates ``_reset_days_since_irrigation`` on this so a
        dry run doesn't fool the days-between guard (review finding A).
        """
        zones = await self.store.async_get_zones()
        sequencing = self.store.config.zone_sequencing
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}

        # Live-estimate watering (experimental): when on, the per-zone trigger is
        # the intra-day live deficit (decided in _apply_live_durations), so the
        # frozen daily duration + stored daily bucket are NOT pre-filters here —
        # a run the daily calc didn't approve can still start on intra-day demand.
        # When off, the classic daily gate (duration > 0 AND bucket below
        # threshold) selects candidates, byte-identical to before.
        live_gate = getattr(self.store.config, "live_estimate_enabled", False) is True
        zones_to_irrigate = [
            z
            for z in zones
            # Iter Task 2 (Plan D): a distributor member zone (distributor_id
            # set, including 0 — hence `is None`, not `not z.get(...)`, since
            # `not 0` is truthy and would wrongly re-include distributor 0's
            # members) is watered exclusively by its distributor's own cycle
            # (shared inlet valve). Excluding it here prevents the normal
            # linked-entity path from double-driving a member zone in
            # parallel with the distributor engine.
            if z.get(const.ZONE_DISTRIBUTOR_ID) is None
            and (z.get(const.ZONE_LINKED_ENTITY) or self._sc_is_self_closing(z))
            and z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
            and (target is None or int(z.get(const.ZONE_ID)) in target)
            and (
                live_gate
                or (
                    (z.get(const.ZONE_DURATION) or 0) > 0
                    and (z.get(const.ZONE_BUCKET) or 0)
                    < (z.get(const.ZONE_BUCKET_THRESHOLD) or 0)
                )
            )
        ]

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
        if not zones_to_irrigate:
            _LOGGER.debug("Live-estimate duration left no zones needing water")
            return False

        # Master (pump): power on before the first zone; record each run's end so
        # master_off (if enabled) can fire after the last zone completes.
        await self.async_master_begin_cycle()
        for z in zones_to_irrigate:
            self._master_note_run(float(z.get(const.ZONE_DURATION) or 0))
        await self.async_master_schedule_off()

        # Self-closing zones delegate the run to their own service (the valve
        # owns the close); they bypass the linked-entity sequencing below.
        for z in [z for z in zones_to_irrigate if self._sc_is_self_closing(z)]:
            await self.async_run_self_closing(z, trigger="schedule")
        zones_to_irrigate = [
            z for z in zones_to_irrigate if not self._sc_is_self_closing(z)
        ]
        if not zones_to_irrigate:
            # Self-closing zones were dispatched above => water WAS delivered.
            return True

        if sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL:
            asyncio.create_task(self._irrigate_zones_sequential(zones_to_irrigate))
        elif sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            asyncio.create_task(self._irrigate_zones_rotating(zones_to_irrigate))
        else:
            await self._irrigate_zones_parallel(zones_to_irrigate)
        # Past the veto+live gates with a non-empty set: at least one real run
        # (self-closing and/or the sequencing task) was dispatched.
        return True

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
        self, zone: dict, entity_id: str, *, real_flow: bool, trigger: str = "schedule"
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
            max_seconds = float(zone.get(const.ZONE_MAXIMUM_DURATION) or 14400)
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
                    if (stopped or timed_out)
                    else const.RUN_RESULT_COMPLETED
                ),
                volume_l=delivered,
                add_to_total=False,  # already streamed in via _commit_run_progress
                planned_s=None if real_flow else max_seconds,
                actual_s=elapsed,
                detail=(
                    const.RUN_DETAIL_STOPPED
                    if stopped
                    else (
                        "safety_timeout"
                        if timed_out
                        else zone.get(const.ZONE_EXPLANATION)
                    )
                ),
                trigger=trigger,
            )
        finally:
            self._unregister_active_run(zone_id)

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

        accumulated = 0.0
        elapsed = 0.0

        while elapsed < max_seconds and accumulated < remaining_volume:
            stopped = await self._sleep_or_stopped(zone_id, const.FLOW_POLL_INTERVAL)
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
        # Review finding G (REGEL-8 sister path to _run_valve_metered): the open
        # noted the full slot cap (line 978), but a volume-bounded slot usually
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

    async def _irrigate_zones_rotating(self, zones: list):
        """Irrigate all zones (timed and flow-meter) in a unified rotation.

        Each zone gets at most max_consecutive_duration per turn.
        When min_absorption_time > 0, the loop waits before returning to a zone.
        """
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

        # Register every zone so a Stop can interrupt the rotation and the
        # dashboard surfaces the control. A rotation has no single finish time,
        # so no countdown end is set (has_end=False). Markers are cleared as each
        # zone finishes and swept at the end.
        for zid in zone_order:
            self._register_active_run(zid, 0, has_end=False)

        def _timed_done(zid):
            return timed_remaining.get(zid, 0) <= 0

        def _flow_done(zid):
            safety = flow_by_id[zid].get(const.ZONE_MAXIMUM_DURATION) or 14400
            return (
                flow_delivered[zid] >= flow_target[zid] or flow_elapsed[zid] >= safety
            )

        def _all_done():
            return all(_timed_done(z) for z in timed_by_id) and all(
                _flow_done(z) for z in flow_by_id
            )

        while not _all_done():
            for zid in zone_order:
                is_flow = zid in flow_by_id
                if is_flow and _flow_done(zid):
                    continue
                if not is_flow and _timed_done(zid):
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
                            flow_by_id[zid].get(const.ZONE_MAXIMUM_DURATION) or 14400,
                        )
                    else:
                        timed_remaining[zid] = 0
                    self._unregister_active_run(zid)
                    continue

                if min_absorption > 0 and zid in last_finish:
                    wait = min_absorption - (loop.time() - last_finish[zid])
                    if wait > 0:
                        _LOGGER.info(
                            "Rotating irrigation: zone %s absorbing, waiting %.0fs",
                            zid,
                            wait,
                        )
                        await asyncio.sleep(wait)

                if is_flow:
                    z = flow_by_id[zid]
                    entity_id = z[const.ZONE_LINKED_ENTITY]
                    safety = z.get(const.ZONE_MAXIMUM_DURATION) or 14400
                    slot = min(max_slot, safety - flow_elapsed[zid])
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

                last_finish[zid] = loop.time()

        # Clear any remaining in-progress markers (zones that finished normally,
        # or a stop during an absorption wait).
        for zid in zone_order:
            self._unregister_active_run(zid)

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
            threshold = z.get(const.ZONE_BUCKET_THRESHOLD) or 0
            daily_needs = (z.get(const.ZONE_DURATION) or 0) > 0 and (
                z.get(const.ZONE_BUCKET) or 0
            ) < threshold
            if z.get(const.ZONE_FLOW_SENSOR):
                # Flow zones deliver to a measured volume, not a recomputed
                # duration — keep the daily deficit gate for them.
                if daily_needs:
                    out.append(z)
                continue
            est = estimates.get(str(z.get(const.ZONE_ID)))
            deficit = est.get("live_deficit") if est else None
            if deficit is None:
                # No live estimate — fall back to the daily gate.
                if daily_needs:
                    out.append(z)
                continue
            if deficit >= threshold:
                _LOGGER.info(
                    "Live-estimate watering: zone %s live deficit %.2f hasn't "
                    "crossed the threshold %.2f — not watering this run",
                    z.get(const.ZONE_ID),
                    deficit,
                    threshold,
                )
                continue
            live = duration_from_deficit(
                deficit,
                z.get(const.ZONE_THROUGHPUT),
                z.get(const.ZONE_SIZE),
                z.get(const.ZONE_MULTIPLIER),
                z.get(const.ZONE_MAXIMUM_DURATION),
                z.get(const.ZONE_LEAD_TIME),
                metric,
            )
            if live <= 0:
                continue
            zid = int(z.get(const.ZONE_ID))
            self._live_run_zones.add(zid)
            self._warn_if_low_maximum_bucket(z, metric)
            _LOGGER.info(
                "Live-estimate watering: zone %s %ss → %ss (live deficit %.2f)",
                zid,
                z.get(const.ZONE_DURATION),
                live,
                deficit,
            )
            out.append({**z, const.ZONE_DURATION: live})
        return out

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
        changes = {const.ZONE_BUCKET: new_bucket}
        if volume_delta_l and volume_delta_l > 0:
            # Only stamp "last irrigation" + the usage counter when water actually
            # flowed this commit, so a failed / never-started run (which still
            # commits an unchanged bucket) does not claim it just watered.
            changes[const.ZONE_LAST_IRRIGATION] = dt_util.now()
            changes[const.ZONE_WATER_USED_TOTAL] = (
                zone.get(const.ZONE_WATER_USED_TOTAL) or 0.0
            ) + volume_delta_l
        await self.store.async_update_zone(zone_id, changes)
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

    async def _irrigate_zones_sequential(self, zones: list):
        """Irrigate zones one after another, skipping zones with no duration."""
        for zone in zones:
            entity_id = zone[const.ZONE_LINKED_ENTITY]
            real_flow = bool(zone.get(const.ZONE_FLOW_SENSOR))
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
            )
            _LOGGER.info("Sequential irrigation: finished %s", entity_id)

    async def _irrigate_zones_parallel(self, zones: list):
        """Start all zone entities simultaneously, each accounting for its own run."""
        for zone in zones:
            entity_id = zone[const.ZONE_LINKED_ENTITY]
            real_flow = bool(zone.get(const.ZONE_FLOW_SENSOR))
            _LOGGER.info(
                "Parallel irrigation: zone %s (%s)",
                zone[const.ZONE_ID],
                "flow meter" if real_flow else "timed",
            )
            asyncio.create_task(
                self._run_valve_metered(
                    zone,
                    entity_id,
                    real_flow=real_flow,
                    trigger=self._run_trigger(zone[const.ZONE_ID]),
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

        target = "all" if zone_id is None else [zone_id]
        if zones_to_irrigate:
            # Master (pump): power on before the first zone; record each run's end.
            await self.async_master_begin_cycle()
            for z in zones_to_irrigate:
                self._master_note_run(float(z.get(const.ZONE_DURATION) or 0))
            await self.async_master_schedule_off()
            for z in [z for z in zones_to_irrigate if self._sc_is_self_closing(z)]:
                await self.async_run_self_closing(z, trigger="manual")
            remaining = [
                z for z in zones_to_irrigate if not self._sc_is_self_closing(z)
            ]
            if remaining:
                sequencing = self.store.config.zone_sequencing
                if sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL:
                    asyncio.create_task(self._irrigate_zones_sequential(remaining))
                elif sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
                    asyncio.create_task(self._irrigate_zones_rotating(remaining))
                else:
                    await self._irrigate_zones_parallel(remaining)
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
        # Self-closing zones run via their own service for the requested duration.
        if self._sc_is_self_closing(zone):
            await self.async_master_begin_cycle()
            self._master_note_run(float(seconds))
            await self.async_master_schedule_off()
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

        # Master (pump): power on before opening the valve.
        await self.async_master_begin_cycle()
        self._master_note_run(float(seconds))
        await self.async_master_schedule_off()

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
