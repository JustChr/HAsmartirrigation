"""Irrigation execution for the Smart Irrigation integration.

Extracted from __init__.py (Phase C2). The runner methods live on a mixin the
SmartIrrigationCoordinator inherits, so their bodies are unchanged — they still
use ``self`` to reach coordinator state (store, hass, skip-condition checks,
duration helpers). ``async_irrigate_now`` is the entry point that dispatches to
the rotating / sequential / parallel strategies based on config.
"""

import asyncio
import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .calculation import duration_from_deficit
from .helpers import convert_between

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

    async def _confirm_valve_running(self, zone_id, entity_id):
        """Confirm a freshly-opened linked entity actually reports an on-state.

        Returns True if confirmed on within the grace window, False if it stayed
        off (a fault), or None when the entity is not readable (unknown /
        unavailable / missing) so verification cannot be performed — write-only
        valves are never penalised. Behaviour is unchanged for callers that
        treat None/True identically (only an explicit False aborts a run).
        """
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unavailable", "unknown"):
            return None  # not verifiable — don't fault write-only valves
        waited = 0.0
        while True:
            state = self.hass.states.get(entity_id)
            if state is not None and state.state in _VALVE_ON_STATES:
                return True
            if waited >= const.VALVE_CONFIRM_TIMEOUT:
                return False
            await asyncio.sleep(const.VALVE_CONFIRM_POLL)
            waited += const.VALVE_CONFIRM_POLL

    @callback
    async def _irrigate_linked_entities(self, zone_ids=None):
        """Directly control linked valve/switch entities for zones needing irrigation.

        ``zone_ids`` optionally restricts to a schedule's target zones (an
        iterable of ids, or None/"all" for every eligible zone).
        """
        zones = await self.store.async_get_zones()
        sequencing = self.store.config.zone_sequencing
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}

        zones_to_irrigate = [
            z
            for z in zones
            if z.get(const.ZONE_LINKED_ENTITY)
            and (z.get(const.ZONE_DURATION) or 0) > 0
            and z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
            and (z.get(const.ZONE_BUCKET) or 0)
            < (z.get(const.ZONE_BUCKET_THRESHOLD) or 0)
            and (target is None or int(z.get(const.ZONE_ID)) in target)
        ]

        if not zones_to_irrigate:
            _LOGGER.debug(
                "No zones with linked entities and duration > 0 to irrigate directly"
            )
            return

        # Rain delay / vacation hold (WS-5): a user-set, time-boxed pause of all
        # AUTOMATIC irrigation. Explicit manual runs (async_irrigate_now /
        # async_run_zone) bypass this on purpose; only the scheduled path is gated.
        if self._rain_delay_active():
            _LOGGER.info(
                "Irrigation paused (rain delay until %s); skipping scheduled run",
                self._rain_delay_until_dt(),
            )
            await self._record_skipped_run(zone_ids, const.SKIP_REASON_PAUSED)
            return

        zones_to_irrigate = await self._apply_live_durations(zones_to_irrigate)
        if not zones_to_irrigate:
            _LOGGER.debug("Live-estimate duration left no zones needing water")
            return

        if sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL:
            asyncio.create_task(self._irrigate_zones_sequential(zones_to_irrigate))
        elif sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            asyncio.create_task(self._irrigate_zones_rotating(zones_to_irrigate))
        else:
            await self._irrigate_zones_parallel(zones_to_irrigate)

    @staticmethod
    def _flow_rate_to_l_per_min(value: float, unit: str) -> float:
        """Convert a flow sensor reading to L/min for volume accumulation."""
        u = (unit or "").lower().strip()
        if u in ("l/h", "liter/h", "liter/hour", "liters/hour", "liters/h"):
            return value / 60.0
        if u in ("m³/h", "m3/h", "m³/hour", "m3/hour"):
            return value * 1000.0 / 60.0
        if u in ("m³/min", "m3/min"):
            return value * 1000.0
        if u in ("gal/min", "gpm", "gallon/min", "gallons/min"):
            return value * 3.785411784
        if u in ("gal/h", "gal/hour", "gallon/h", "gallons/h"):
            return value * 3.785411784 / 60.0
        return value  # assume L/min

    async def _irrigate_zone_with_flow_meter(self, zone: dict, entity_id: str) -> None:
        """Irrigate a zone using a flow sensor: stop when target volume is delivered."""
        zone_id = zone[const.ZONE_ID]
        size = zone.get(const.ZONE_SIZE) or 0.0
        bucket = zone.get(const.ZONE_BUCKET) or 0.0

        # Post-run target (display units, normally 0). Forecast weighting can set
        # a rain-covered remainder; we then deliver only down to that floor.
        floor_display = self._zone_target_bucket(zone)
        floor_mm = floor_display

        ha_config_is_metric = self.hass.config.units is METRIC_SYSTEM
        if not ha_config_is_metric:
            size = convert_between(const.UNIT_SQ_FT, const.UNIT_M2, size)
            bucket = convert_between(const.UNIT_INCH, const.UNIT_MM, bucket)
            floor_mm = convert_between(const.UNIT_INCH, const.UNIT_MM, floor_display)

        target_volume = size * max(0.0, floor_mm - bucket)
        safety_timeout = zone.get(const.ZONE_MAXIMUM_DURATION) or 14400

        _LOGGER.info(
            "Flow meter irrigation: zone %s target %.1f L (sensor: %s)",
            zone_id,
            target_volume,
            zone[const.ZONE_FLOW_SENSOR],
        )

        accumulated = await self._irrigate_zone_flow_slot(
            zone, entity_id, safety_timeout, target_volume
        )
        timed_out = accumulated < target_volume

        if timed_out:
            _LOGGER.warning(
                "Zone %s: safety timeout %ss reached (%.2f / %.1f L delivered)",
                zone_id,
                safety_timeout,
                accumulated,
                target_volume,
            )
        else:
            _LOGGER.info(
                "Zone %s: target %.1f L reached (%.2f L delivered)",
                zone_id,
                target_volume,
                accumulated,
            )

        if target_volume > 0 and accumulated <= 0:
            # The valve was told to open but the flow sensor never registered any
            # flow — treat as a failed run: do NOT credit the bucket, flag a fault
            # so the deficit (and the problem sensor) persist.
            self._set_zone_fault(zone_id, const.FAULT_FLOW_NEVER_STARTED)
            await self._record_run(
                zone_id,
                result=const.RUN_RESULT_FAILED,
                detail=const.FAULT_FLOW_NEVER_STARTED,
            )
            return

        if size > 0:
            actual_mm = accumulated / size
            if not ha_config_is_metric:
                actual_mm = convert_between(const.UNIT_MM, const.UNIT_INCH, actual_mm)
            self._clear_zone_fault(zone_id)
            original_bucket = zone.get(const.ZONE_BUCKET) or 0.0
            new_bucket = min(floor_display, original_bucket + actual_mm)
            await self.store.async_update_zone(
                zone_id,
                {
                    const.ZONE_BUCKET: new_bucket,
                    const.ZONE_LAST_IRRIGATION: dt_util.now(),
                },
            )
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
            _LOGGER.info(
                "Zone %s: bucket updated %.3f → %.3f (%s%.2f mm delivered%s)",
                zone_id,
                original_bucket,
                new_bucket,
                "" if not timed_out else "partial, ",
                actual_mm,
                "" if not timed_out else " — timeout",
            )
            await self._record_run(
                zone_id,
                result=(
                    const.RUN_RESULT_PARTIAL
                    if timed_out
                    else const.RUN_RESULT_COMPLETED
                ),
                volume_l=accumulated,
                detail=(
                    "safety_timeout" if timed_out else zone.get(const.ZONE_EXPLANATION)
                ),
            )

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
        flow_sensor = zone[const.ZONE_FLOW_SENSOR]
        zone_id = zone[const.ZONE_ID]
        domain = entity_id.split(".")[0]

        self._note_si_valve(zone_id, max_seconds)
        await self.hass.services.async_call(domain, "turn_on", {"entity_id": entity_id})

        accumulated = 0.0
        elapsed = 0.0

        while elapsed < max_seconds and accumulated < remaining_volume:
            await asyncio.sleep(const.FLOW_POLL_INTERVAL)
            elapsed += const.FLOW_POLL_INTERVAL

            state = self.hass.states.get(flow_sensor)
            if state is None or state.state in ("unavailable", "unknown"):
                _LOGGER.warning(
                    "Flow sensor '%s' unavailable during rotating slot of zone %s",
                    flow_sensor,
                    zone_id,
                )
                continue
            try:
                raw = float(state.state)
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "Flow sensor '%s' non-numeric state '%s'", flow_sensor, state.state
                )
                continue

            unit = state.attributes.get("unit_of_measurement", "L/min")
            rate = self._flow_rate_to_l_per_min(raw, unit)
            accumulated += rate * const.FLOW_POLL_INTERVAL / 60.0
            _LOGGER.debug(
                "Zone %s slot: %.2f L/min → %.2f / %.2f L",
                zone_id,
                rate,
                accumulated,
                remaining_volume,
            )

        await self.hass.services.async_call(
            domain, "turn_off", {"entity_id": entity_id}
        )
        return accumulated

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

        ha_metric = self.hass.config.units is METRIC_SYSTEM
        flow_target: dict = {}
        flow_delivered: dict = {}
        flow_elapsed: dict = {}
        flow_size_m2: dict = {}
        flow_bucket: dict = {}
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
            flow_size_m2[zid] = s_m2
            flow_bucket[zid] = raw_bucket
            flow_floor[zid] = raw_floor
            flow_by_id[zid] = z
            _LOGGER.info(
                "Rotating irrigation: flow zone %s target %.1f L", zid, flow_target[zid]
            )

        zone_order = [z[const.ZONE_ID] for z in timed_zones + flow_zones]
        last_finish: dict = {}
        loop = asyncio.get_running_loop()

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
                    _LOGGER.info(
                        "Rotating irrigation: flow zone %s slot done — %.1f/%.1f L total",
                        zid,
                        flow_delivered[zid],
                        flow_target[zid],
                    )
                    if flow_size_m2[zid] > 0:
                        slot_mm = delivered / flow_size_m2[zid]
                        slot_native = (
                            slot_mm
                            if ha_metric
                            else convert_between(
                                const.UNIT_MM, const.UNIT_INCH, slot_mm
                            )
                        )
                        prev_bucket = flow_bucket[zid]
                        new_bucket = min(flow_floor[zid], prev_bucket + slot_native)
                        flow_bucket[zid] = new_bucket
                        await self.store.async_update_zone(
                            zid, {const.ZONE_BUCKET: new_bucket}
                        )
                        _LOGGER.info(
                            "Rotating irrigation: flow zone %s bucket %.3f → %.3f"
                            " (%.2f L this slot)",
                            zid,
                            prev_bucket,
                            new_bucket,
                            delivered,
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
                        # Valve never opened — drop this zone from the rotation
                        # without replenishing its bucket; the fault persists.
                        self._set_zone_fault(zid, const.FAULT_VALVE_NO_RESPONSE)
                        await self.hass.services.async_call(
                            domain, "turn_off", {"entity_id": entity_id}
                        )
                        timed_remaining[zid] = 0
                        last_finish[zid] = loop.time()
                        await self._record_run(
                            zid,
                            result=const.RUN_RESULT_FAILED,
                            detail=const.FAULT_VALVE_NO_RESPONSE,
                        )
                        continue
                    await asyncio.sleep(slot)
                    await self.hass.services.async_call(
                        domain, "turn_off", {"entity_id": entity_id}
                    )
                    timed_remaining[zid] -= slot
                    _LOGGER.info("Rotating irrigation: finished slot for %s", entity_id)
                    if timed_remaining[zid] <= 0:
                        # Zone fully irrigated across its slots — replenish bucket.
                        self._clear_zone_fault(zid)
                        planned = float(z[const.ZONE_DURATION])
                        await self._reset_zone_bucket_after_run(
                            zid, ran_seconds=planned
                        )
                        await self._record_run(
                            zid,
                            result=const.RUN_RESULT_COMPLETED,
                            volume_l=self._timed_volume_l(z, planned),
                            planned_s=planned,
                            actual_s=planned,
                            detail=z.get(const.ZONE_EXPLANATION),
                        )

                last_finish[zid] = loop.time()

    # --- Live-estimate run durations from the live deficit (WS-3, experimental)

    async def _apply_live_durations(self, zones: list) -> list:
        """Recompute timed-zone run durations from the live intra-day deficit.

        Experimental, opt-in (Setup → Experimental). When the flag is off this
        returns ``zones`` unchanged. When on, it refreshes the live estimates and
        replaces each timed zone's frozen daily ``ZONE_DURATION`` with one
        computed from the drainage-aware ``live_deficit`` (intra-day ET/precip
        since the last daily calc, the same quantity behind the "Live bucket"
        sensor) — answering "is the duration frozen hours ago still right at water
        time?". Zones whose live deficit is non-negative (intra-day rain already
        covered them) are dropped from the run.

        The daily ledger is untouched: only the *duration of this run* changes.
        Flow-meter zones are left alone — they already deliver to a measured
        volume and credit the bucket from it. Recomputed zones are marked in
        ``_live_run_zones`` so :meth:`_reset_zone_bucket_after_run` credits the
        actually-delivered water (``bucket += delivered``, capped) instead of
        forcing the bucket to its target; the live deficit can exceed the stored
        daily bucket, so crediting (not zeroing) keeps the next daily calc from
        double-subtracting the intra-day ET.
        """
        if self.store.config.live_duration_enabled is not True:
            self._live_run_zones = set()
            return zones

        estimates = await self.async_refresh_zone_estimates()
        self._live_run_zones = set()
        metric = self.hass.config.units is METRIC_SYSTEM
        out = []
        for z in zones:
            if z.get(const.ZONE_FLOW_SENSOR):
                out.append(z)  # flow path already credits measured volume
                continue
            est = estimates.get(str(z.get(const.ZONE_ID)))
            deficit = est.get("live_deficit") if est else None
            if deficit is None:
                out.append(z)  # no live estimate — keep the daily duration
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
                _LOGGER.info(
                    "Live-estimate duration: zone %s no longer needs water "
                    "(live deficit %.2f) — skipping this run",
                    z.get(const.ZONE_ID),
                    deficit,
                )
                continue
            zid = int(z.get(const.ZONE_ID))
            self._live_run_zones.add(zid)
            _LOGGER.info(
                "Live-estimate duration: zone %s %ss → %ss (live deficit %.2f)",
                zid,
                z.get(const.ZONE_DURATION),
                live,
                deficit,
            )
            out.append({**z, const.ZONE_DURATION: live})
        return out

    def _delivered_depth_native(self, zone: dict, seconds: float) -> float:
        """Depth (display units) a timed run of ``seconds`` applied to ``zone``.

        volume = run minutes × throughput; depth = volume / area. Mirrors the
        observed-watering crediting math so a live-estimate run credits the
        bucket by what it actually delivered.
        """
        size = zone.get(const.ZONE_SIZE) or 0.0
        if size <= 0 or not seconds or seconds <= 0:
            return 0.0
        volume_l = self._timed_volume_l(zone, seconds)
        if self.hass.config.units is METRIC_SYSTEM:
            return volume_l / size  # litres / m² == mm
        size_m2 = convert_between(const.UNIT_SQ_FT, const.UNIT_M2, size)
        applied_mm = volume_l / size_m2
        return convert_between(const.UNIT_MM, const.UNIT_INCH, applied_mm)

    async def _reset_zone_bucket_after_run(self, zone_id, ran_seconds=None) -> None:
        """Replenish a zone's bucket after a completed timed run.

        Normal runs: the duration was computed to deliver exactly the accumulated
        deficit (|bucket|), so the bucket returns to its post-run target —
        normally 0, or the rain-covered remainder when forecast weighting trimmed
        this run. The flow-meter path does the equivalent from measured volume.

        Live-estimate runs (WS-3, marked in ``_live_run_zones``): the duration
        came from the live intra-day deficit, which can exceed the stored daily
        bucket. Forcing the bucket to its target would discard the credit for the
        extra intra-day water and the next daily calc would re-subtract that ET.
        Instead credit the actually-delivered depth (``bucket += delivered``,
        capped at maximum_bucket) so the leftover deficit persists honestly.
        """
        zone = self.store.get_zone(zone_id) or {}
        if int(zone_id) in getattr(self, "_live_run_zones", set()):
            delivered = self._delivered_depth_native(zone, ran_seconds)
            new_bucket = (zone.get(const.ZONE_BUCKET) or 0.0) + delivered
            max_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
            if max_bucket is not None and new_bucket > max_bucket:
                new_bucket = float(max_bucket)
            self._live_run_zones.discard(int(zone_id))
        else:
            new_bucket = self._zone_target_bucket(zone)
        await self.store.async_update_zone(
            zone_id,
            {const.ZONE_BUCKET: new_bucket, const.ZONE_LAST_IRRIGATION: dt_util.now()},
        )
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
        _LOGGER.info(
            "Zone %s: bucket set to %.3f after irrigation run", zone_id, new_bucket
        )

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
    ) -> None:
        """Append a run-log entry and add delivered water to the usage total.

        The run log is a bounded list (newest first, capped at
        ``RUN_LOG_MAX_ENTRIES``) persisted on the zone; ``water_used_total`` is a
        monotonic litre counter backing the usage statistics sensor. Both live in
        the store so they survive restarts.
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
        if volume_l and volume_l > 0:
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
            domain = entity_id.split(".")[0]
            if zone.get(const.ZONE_FLOW_SENSOR):
                _LOGGER.info(
                    "Sequential irrigation: zone %s using flow meter",
                    zone[const.ZONE_ID],
                )
                await self._irrigate_zone_with_flow_meter(zone, entity_id)
            else:
                duration = zone[const.ZONE_DURATION]
                _LOGGER.info(
                    "Sequential irrigation: turning on %s for %s seconds",
                    entity_id,
                    duration,
                )
                self._note_si_valve(zone[const.ZONE_ID], duration)
                await self.hass.services.async_call(
                    domain, "turn_on", {"entity_id": entity_id}
                )
                if (
                    await self._confirm_valve_running(zone[const.ZONE_ID], entity_id)
                    is False
                ):
                    # Valve never opened — abort this zone without replenishing
                    # the bucket so the deficit (and the fault) persist.
                    self._set_zone_fault(
                        zone[const.ZONE_ID], const.FAULT_VALVE_NO_RESPONSE
                    )
                    await self.hass.services.async_call(
                        domain, "turn_off", {"entity_id": entity_id}
                    )
                    await self._record_run(
                        zone[const.ZONE_ID],
                        result=const.RUN_RESULT_FAILED,
                        detail=const.FAULT_VALVE_NO_RESPONSE,
                    )
                    continue
                await asyncio.sleep(duration)
                await self.hass.services.async_call(
                    domain, "turn_off", {"entity_id": entity_id}
                )
                self._clear_zone_fault(zone[const.ZONE_ID])
                await self._reset_zone_bucket_after_run(
                    zone[const.ZONE_ID], ran_seconds=duration
                )
                await self._record_run(
                    zone[const.ZONE_ID],
                    result=const.RUN_RESULT_COMPLETED,
                    volume_l=self._timed_volume_l(zone, duration),
                    planned_s=duration,
                    actual_s=duration,
                    detail=zone.get(const.ZONE_EXPLANATION),
                )
            _LOGGER.info("Sequential irrigation: finished %s", entity_id)

    async def _irrigate_zones_parallel(self, zones: list):
        """Start all zone entities simultaneously, each turning off after its own duration."""
        for zone in zones:
            entity_id = zone[const.ZONE_LINKED_ENTITY]
            domain = entity_id.split(".")[0]
            if zone.get(const.ZONE_FLOW_SENSOR):
                _LOGGER.info(
                    "Parallel irrigation: zone %s using flow meter", zone[const.ZONE_ID]
                )
                asyncio.create_task(
                    self._irrigate_zone_with_flow_meter(zone, entity_id)
                )
            else:
                duration = zone[const.ZONE_DURATION]
                _LOGGER.info(
                    "Parallel irrigation: turning on %s for %s seconds",
                    entity_id,
                    duration,
                )
                self._note_si_valve(zone[const.ZONE_ID], duration)
                trigger = self._run_trigger(zone[const.ZONE_ID])
                await self.hass.services.async_call(
                    domain, "turn_on", {"entity_id": entity_id}
                )

                async def _turn_off(
                    eid=entity_id,
                    dom=domain,
                    dur=duration,
                    zid=zone[const.ZONE_ID],
                    trig=trigger,
                ):
                    if await self._confirm_valve_running(zid, eid) is False:
                        # Valve never opened — abort without replenishing the
                        # bucket so the deficit and fault persist.
                        self._set_zone_fault(zid, const.FAULT_VALVE_NO_RESPONSE)
                        await self.hass.services.async_call(
                            dom, "turn_off", {"entity_id": eid}
                        )
                        await self._record_run(
                            zid,
                            result=const.RUN_RESULT_FAILED,
                            detail=const.FAULT_VALVE_NO_RESPONSE,
                            trigger=trig,
                        )
                        return
                    await asyncio.sleep(dur)
                    await self.hass.services.async_call(
                        dom, "turn_off", {"entity_id": eid}
                    )
                    _LOGGER.info("Parallel irrigation: turned off %s", eid)
                    self._clear_zone_fault(zid)
                    await self._reset_zone_bucket_after_run(zid, ran_seconds=dur)
                    run_zone = self.store.get_zone(zid) or {}
                    await self._record_run(
                        zid,
                        result=const.RUN_RESULT_COMPLETED,
                        volume_l=self._timed_volume_l(run_zone, dur),
                        planned_s=dur,
                        actual_s=dur,
                        detail=run_zone.get(const.ZONE_EXPLANATION),
                        trigger=trig,
                    )

                asyncio.create_task(_turn_off())

    async def async_irrigate_now(self, zone_id: str | None = None):
        """Immediately irrigate — bypasses all skip conditions.

        If zone_id is provided, only irrigate that zone.
        Otherwise irrigate all zones that have a linked entity and duration > 0.
        """
        zones = await self.store.async_get_zones()

        if zone_id is not None:
            zones = [z for z in zones if str(z.get(const.ZONE_ID)) == str(zone_id)]

        zones_to_irrigate = [
            z
            for z in zones
            if z.get(const.ZONE_LINKED_ENTITY)
            and (z.get(const.ZONE_DURATION) or 0) > 0
            and z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
        ]

        if not zones_to_irrigate:
            _LOGGER.info("irrigate_now: no zones with linked entity and duration > 0")
            return

        sequencing = self.store.config.zone_sequencing
        if sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL:
            asyncio.create_task(self._irrigate_zones_sequential(zones_to_irrigate))
        elif sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            asyncio.create_task(self._irrigate_zones_rotating(zones_to_irrigate))
        else:
            await self._irrigate_zones_parallel(zones_to_irrigate)

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
        if not zone.get(const.ZONE_LINKED_ENTITY):
            _LOGGER.warning("run_zone: zone %s has no linked entity", zone_id)
            return
        if zone.get(const.ZONE_STATE) == const.ZONE_STATE_DISABLED:
            _LOGGER.info("run_zone: zone %s is disabled, ignoring", zone_id)
            return

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
