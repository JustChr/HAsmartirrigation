"""Self-closing valve mode: delegate the valve close to self-closing hardware.

A zone in WATERING_MODE_SERVICE is run by firing a configured service with the
run duration; the valve owns the close (a hardware countdown), so an HA outage
mid-run cannot cause continuous irrigation. The bucket is credited optimistically
at start and the in-flight run is persisted for restart reconciliation.
"""

from __future__ import annotations

import logging
import math
from datetime import timedelta

from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.util import dt as dt_util

from . import const

_LOGGER = logging.getLogger(__name__)


class SelfClosingMixin:
    """Self-closing actuation lifecycle. Mixed into SmartIrrigationCoordinator."""

    @staticmethod
    def _sc_convert(seconds: float, unit: str) -> int:
        """Convert a run duration (seconds) to the hardware's unit, rounding up."""
        seconds = float(seconds or 0)
        if unit == const.DURATION_UNIT_MINUTES:
            return max(1, math.ceil(seconds / 60.0)) if seconds > 0 else 0
        return int(round(seconds))

    def _sc_split_service(self, dotted: str):
        """'domain.service' -> (domain, service)."""
        domain, _, service = (dotted or "").partition(".")
        return domain, service

    async def _sc_dispatch_open(self, zone: dict) -> None:
        """Open the valve for its run by firing the run_service."""
        seconds = float(zone.get(const.ZONE_DURATION) or 0)
        unit = zone.get(const.ZONE_DURATION_UNIT, const.DURATION_UNIT_SECONDS)
        duration = self._sc_convert(seconds, unit)
        await self._sc_service_open(zone, duration)

    async def _sc_service_open(self, zone: dict, duration: int) -> None:
        """'service' adapter: call the run_service with the duration."""
        domain, service = self._sc_split_service(zone.get(const.ZONE_RUN_SERVICE))
        data = {}
        # Empty/None duration_field falls back to "duration" — the field name the
        # shipped valve blueprints use — so a blueprint zone works with no extra
        # config. Without this, an unset field would send NO duration at all.
        field = zone.get(const.ZONE_DURATION_FIELD) or "duration"
        data[field] = duration
        data["zone_id"] = zone.get(const.ZONE_ID)
        data["zone_name"] = zone.get(const.ZONE_NAME)
        await self.hass.services.async_call(domain, service, data)

    def _sc_fire(self, event: str, data: dict) -> None:
        """Fire a domain-prefixed bus event."""
        self.hass.bus.async_fire(f"{const.DOMAIN}_{event}", data)

    async def _sc_active_runs(self) -> list:
        """Return the persisted list of in-flight self-closing runs."""
        cfg = await self.store.async_get_config()
        return list(cfg.get(const.CONF_ACTIVE_VALVE_RUNS, []) or [])

    async def _sc_persist_runs(self, runs: list) -> None:
        await self.store.async_update_config({const.CONF_ACTIVE_VALVE_RUNS: runs})

    async def _sc_add_run(self, record: dict) -> None:
        runs = [
            r
            for r in await self._sc_active_runs()
            if r.get(const.RUN_ZONE_ID) != record[const.RUN_ZONE_ID]
        ]
        runs.append(record)
        await self._sc_persist_runs(runs)

    async def _sc_remove_run(self, zone_id) -> None:
        runs = [
            r
            for r in await self._sc_active_runs()
            if r.get(const.RUN_ZONE_ID) != zone_id
        ]
        await self._sc_persist_runs(runs)

    def _sc_meters(self) -> dict:
        """Lazy {zone_id: (FlowMeter, cancel_cb, open_start_l, started)} of in-flight
        self-closing flow meters (open_start_l + started drive run-end learning/finalize).
        """
        meters = getattr(self, "_sc_flow_meters", None)
        if meters is None:
            meters = self._sc_flow_meters = {}
        return meters

    async def _sc_start_flow_sampling(self, zone: dict) -> None:
        """Start NON-blocking interval sampling of a self-closing zone's flow_sensor.

        No-op when the zone has no flow_sensor. Feeds a per-zone FlowMeter (counter type
        resolved from the per-zone override / learned streak) that _sc_finish_run /
        async_stop_self_closing finalize into the measured volume. The run itself stays
        fire-and-forget (the hardware owns the close); a mid-run HA restart loses the
        in-memory meter and the caller falls back to the time-based volume (safe).
        See test_self_closing.
        """
        sensor = zone.get(const.ZONE_FLOW_SENSOR)
        if not sensor:
            return
        zone_id = zone.get(const.ZONE_ID)
        # Never orphan a prior in-flight interval for this zone (e.g. a manual run fired
        # during a scheduled run): cancel-and-pop before installing the new sampler.
        # _sc_finish_flow tolerates a missing entry (returns (None, {})).
        self._sc_finish_flow(zone_id)
        sample = self._read_flow_sample(sensor)
        meter, open_start_l = self._flow_build_meter(zone, sample)  # seeds at open
        started = dt_util.utcnow()

        async def _tick(now):
            self._sc_sample_flow(zone_id, (now - started).total_seconds())

        cancel = async_track_time_interval(
            self.hass, _tick, timedelta(seconds=const.FLOW_POLL_INTERVAL)
        )
        self._sc_meters()[zone_id] = (meter, cancel, open_start_l, started)

    def _sc_sample_flow(self, zone_id, at: float) -> None:
        """Feed the zone's in-flight meter one reading at monotonic ``at`` (also the test
        seam so a test can drive sampling deterministically)."""
        entry = self._sc_meters().get(zone_id)
        if not entry:
            return
        meter = entry[0]
        zone = self.store.get_zone(zone_id) or {}
        sample = self._read_flow_sample(zone.get(const.ZONE_FLOW_SENSOR))
        if sample is not None:
            meter.sample(*sample, at=at)

    def _sc_finish_flow(self, zone_id):
        """Cancel a zone's sampling and return (measured_l | None, end_changes). measured
        is None when there is no sensor, the meter was lost to a restart, or no positive
        flow was seen (caller then keeps its time-based volume). Takes ONE final reading
        at close so a totalizer's last (up to a poll interval) of climb isn't dropped.
        """
        entry = self._sc_meters().pop(zone_id, None)
        if not entry:
            return None, {}
        meter, cancel, open_start_l, started = entry
        cancel()
        zone = self.store.get_zone(zone_id) or {}
        sensor = zone.get(const.ZONE_FLOW_SENSOR)
        final = self._read_flow_sample(sensor)
        if final is not None:
            meter.sample(*final, at=(dt_util.utcnow() - started).total_seconds())
        d = meter.delivered()
        if d is None and sensor:
            # The per-tick reads are DEBUG (they poll every 15 s), so a persistently
            # dead/misconfigured sensor would otherwise degrade to time-based SILENTLY.
            # Surface it ONCE per run at finalize (the fire-and-forget run has no dry
            # fault to raise). See Fix FM-6.
            _LOGGER.warning(
                "Self-closing zone %s flow sensor '%s' produced no readings this run; "
                "recording the time-based volume estimate instead",
                zone_id,
                sensor,
            )
        measured = d if (d is not None and d > 0) else None
        return measured, self._flow_learn_end_changes(zone, meter, open_start_l)

    async def _sc_finish_run(self, zone_id) -> None:
        """Finalise a completed run: record actual usage, clear, fire finished.

        Idempotent: a no-op if the run is no longer active (e.g. the cleanup
        timer fires after an early stop already removed it), so usage is never
        double-counted.
        """
        run = await self._sc_find_run(zone_id)
        if run is None:
            return
        await self._sc_remove_run(zone_id)
        zone = self.store.get_zone(zone_id) or {}
        # Count usage once, at completion, for the actual delivered volume (the
        # run ran for its full planned duration).
        planned_s = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
        # Iter FM-5: prefer the measured volume from the non-blocking sampler over the
        # open-time time-based estimate. Cancel the sampler + persist the totalizer end
        # for cross-run learning. measured is None when the zone has no flow_sensor, the
        # meter was lost to a restart, or no positive flow was seen -> time-based volume.
        measured, end_changes = self._sc_finish_flow(zone_id)
        if end_changes:
            await self.store.async_update_zone(zone_id, end_changes)
        if measured is not None:
            # Reconcile the bucket ABSOLUTELY from the pre-run level: the optimistic open
            # credit was time-based (and may have clamped at the ceiling), so a delta
            # correction would over-/under-shoot. Recompute measured credit from B0 and
            # clamp once — correct in every quadrant. See test_self_closing.
            pre_bucket = float(run.get(const.RUN_PRE_BUCKET) or 0)
            nb = pre_bucket + self._credited_depth_native(zone, measured)
            ceiling = zone.get(const.ZONE_MAXIMUM_BUCKET)
            if ceiling is not None and nb > float(ceiling):
                nb = float(ceiling)
            await self.store.async_update_zone(zone_id, {const.ZONE_BUCKET: nb})
            zone = self.store.get_zone(zone_id) or zone
            volume_l = measured
        else:
            volume_l = self._timed_volume_l(zone, planned_s)
        await self._record_run(
            zone_id,
            result=const.RUN_RESULT_COMPLETED,
            volume_l=volume_l,
            planned_s=planned_s,
            actual_s=planned_s,
            trigger=const.RUN_TRIGGER_SELF_CLOSING,
            add_to_total=True,
        )
        self._sc_fire(
            const.EVENT_IRRIGATE_FINISHED,
            {
                "zones": [
                    {
                        "zone_id": zone_id,
                        "zone": zone.get(const.ZONE_NAME),
                        "bucket": zone.get(const.ZONE_BUCKET),
                    }
                ],
                "problems": [],
            },
        )
        # A self-closing zone can't stop early, so it gets the same calibration advisory
        # (shared base helper) as a can't-stop distributor member (FM-7).
        await self._flow_calibration_check(zone, measured, planned_s)

    def _sc_schedule_cleanup(self, zone_id, delay_seconds: float) -> None:
        """Schedule the cosmetic finish after the run's planned duration."""

        async def _done(_now):
            await self._sc_finish_run(zone_id)

        async_call_later(self.hass, max(0.0, delay_seconds), _done)

    async def async_run_self_closing(
        self, zone: dict, *, trigger: str = "schedule"
    ) -> bool:
        """Fire a self-closing run for one zone. Returns True if started."""
        zone_id = zone.get(const.ZONE_ID)
        planned_seconds = float(zone.get(const.ZONE_DURATION) or 0)
        if planned_seconds <= 0:
            return False

        # Observed-watering (opt-in) may watch this zone's observed_entity, which
        # our own run_service opens. Mark the run window as SI-driven so the
        # observer does not double-credit it (the run already credits the bucket).
        self._note_si_valve(int(zone.get(const.ZONE_ID)), planned_seconds)

        await self._sc_dispatch_open(zone)

        # Iter FM-5 (unified flow engine): measure delivered volume across the fixed
        # self-closing window via NON-blocking interval sampling — the run stays
        # fire-and-forget (the hardware owns the close); finalized in _sc_finish_run /
        # async_stop_self_closing. See test_self_closing.
        await self._sc_start_flow_sampling(zone)
        # M-1: sampling is now live (an interval is registered). Wrap the remaining
        # fire-and-forget setup so an unexpected exception can't leak the interval —
        # finalize the meter and re-raise. The confirm-fail branch below finalizes on
        # its own normal-return path; this only guards against surprise exceptions.
        try:
            # Confirm the open BEFORE crediting, but ONLY against an optional
            # confirm_entity — the real valve/switch the run_service drives, which
            # carries a persistent on-state. The run_service itself is a momentary
            # fire-and-forget script.* (back to "off" in ms), so confirming against
            # it misfires: it polls "off" the whole window, spuriously reports a
            # zone_problem, skips the credit, and (worse) re-runs the blueprint at
            # the retry, resetting the valve's hardware countdown. So with no
            # confirm_entity the run is write-only (confirmed = None) and credited
            # optimistically — the hardware owns the close. The confirm is poll-only
            # (retry=False): HA must never re-actuate a self-closing valve mid-run.
            confirm_target = zone.get(const.ZONE_CONFIRM_ENTITY)
            confirmed = (
                await self._confirm_valve_running(zone_id, confirm_target, retry=False)
                if confirm_target
                else None
            )
            if confirmed is False:
                # The valve never opened -> abort the run. Cancel the just-started
                # sampling (discard the measurement) so the aborted run leaks no
                # interval/meter.
                self._sc_finish_flow(zone_id)
                self._sc_fire(
                    const.EVENT_ZONE_PROBLEM,
                    {
                        "zone_id": zone_id,
                        "zone": zone.get(const.ZONE_NAME),
                        "entity_id": confirm_target,
                        "reason": const.PROBLEM_VALVE_DID_NOT_OPEN,
                    },
                )
                return False

            # Optimistic bucket credit (the valve owns the close -> assume completion).
            volume_l = self._timed_volume_l(zone, planned_seconds)
            depth = self._credited_depth_native(zone, volume_l)
            ceiling = zone.get(const.ZONE_MAXIMUM_BUCKET)
            # Stash the pre-run bucket so the finish can reconcile the measured credit
            # ABSOLUTELY from B0 (this optimistic credit may clamp at the ceiling; a
            # delta correction at finish would then over-/under-shoot). See _sc_finish_run.
            pre_bucket = float(zone.get(const.ZONE_BUCKET) or 0)
            new_bucket = pre_bucket + depth
            if ceiling and new_bucket > ceiling:
                new_bucket = float(ceiling)
            await self.store.async_update_zone(zone_id, {const.ZONE_BUCKET: new_bucket})
            # NB: water_used_total is NOT counted here — it is recorded once at the
            # run's actual end (_sc_finish_run / async_stop_self_closing) for the
            # delivered volume, so an early stop can't over-report usage. The bucket,
            # however, IS credited optimistically above (the crash-safe model state).

            # Persist the in-flight run for restart reconciliation.
            await self._sc_add_run(
                {
                    const.RUN_ZONE_ID: zone_id,
                    const.RUN_ENTITY_ID: zone.get(const.ZONE_RUN_SERVICE),
                    const.RUN_STARTED: dt_util.utcnow().isoformat(),
                    const.RUN_PLANNED_SECONDS: planned_seconds,
                    const.RUN_PLANNED_MM: depth,
                    const.RUN_PRE_BUCKET: pre_bucket,
                    const.RUN_MODE: zone.get(const.ZONE_WATERING_MODE),
                    const.RUN_CREDITED: True,
                }
            )

            self._sc_fire(
                const.EVENT_IRRIGATE_STARTED,
                {
                    "zones": [
                        {
                            "zone_id": zone_id,
                            "zone": zone.get(const.ZONE_NAME),
                            "seconds": int(planned_seconds),
                        }
                    ],
                },
            )
            self._sc_schedule_cleanup(zone_id, planned_seconds)
            return True
        except Exception:
            self._sc_finish_flow(zone_id)  # don't leak the interval on a setup failure
            raise

    def _sc_elapsed(self, started_iso: str) -> float:
        """Wall-clock seconds since the run started (includes downtime)."""
        started = dt_util.parse_datetime(started_iso)
        if started is None:
            return 0.0
        return max(0.0, (dt_util.utcnow() - started).total_seconds())

    async def _sc_find_run(self, zone_id):
        for r in await self._sc_active_runs():
            if r.get(const.RUN_ZONE_ID) == zone_id:
                return r
        return None

    async def async_stop_self_closing(self, zone_id) -> bool:
        """Stop a self-closing run early: close the valve + correct the bucket."""
        run = await self._sc_find_run(zone_id)
        if run is None:
            return False
        zone = self.store.get_zone(zone_id) or {}

        # Close the valve (best-effort): call the configured stop_service.
        stop_svc = zone.get(const.ZONE_STOP_SERVICE)
        if stop_svc:
            domain, service = self._sc_split_service(stop_svc)
            data = {}
            data["zone_id"] = zone_id
            await self.hass.services.async_call(domain, service, data)
        else:
            _LOGGER.warning(
                "Zone %s stopped in self-closing mode without a stop_service; "
                "cannot close the valve, correcting accounting only",
                zone_id,
            )

        # Correct the bucket for the undelivered portion of the optimistic open credit.
        planned = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
        planned_mm = float(run.get(const.RUN_PLANNED_MM) or 0)
        elapsed = self._sc_elapsed(run.get(const.RUN_STARTED))
        delivered_frac = min(elapsed / planned, 1.0) if planned > 0 else 1.0
        # Reconcile ABSOLUTELY from the pre-run level (RUN_PRE_BUCKET) when we have it: the
        # optimistic open credit may have CLAMPED at the ceiling, so subtracting the
        # undelivered mm from the (clamped) current bucket would over-/under-shoot — the
        # same clamp-then-delta trap _sc_finish_run reconciles from B0 to avoid. Identical
        # to the delta when the open credit did not clamp. Legacy delta fallback for a run
        # persisted before RUN_PRE_BUCKET existed (upgrade mid-run). See test_self_closing.
        pre_bucket = run.get(const.RUN_PRE_BUCKET)
        if pre_bucket is not None:
            nb = float(pre_bucket) + planned_mm * delivered_frac
            ceiling = zone.get(const.ZONE_MAXIMUM_BUCKET)
            if ceiling is not None and nb > float(ceiling):
                nb = float(ceiling)
            await self.store.async_update_zone(zone_id, {const.ZONE_BUCKET: nb})
        else:
            undelivered_mm = planned_mm * (1.0 - delivered_frac)
            if undelivered_mm:
                new_bucket = float(zone.get(const.ZONE_BUCKET) or 0) - undelivered_mm
                await self.store.async_update_zone(
                    zone_id, {const.ZONE_BUCKET: new_bucket}
                )

        await self._sc_remove_run(zone_id)
        # Count usage once, for what was actually delivered. Iter FM-5: the sampler ran
        # until now — prefer its measured litres over the time-based estimate, and persist
        # the totalizer end for cross-run learning. The bucket correction above stays
        # time-based (partial semantics); measured only refines the recorded usage.
        # measured is None (no sensor / dead meter / no flow) -> time-based.
        measured, end_changes = self._sc_finish_flow(zone_id)
        if end_changes:
            await self.store.async_update_zone(zone_id, end_changes)
        delivered_l = (
            measured if measured is not None else self._timed_volume_l(zone, elapsed)
        )
        await self._record_run(
            zone_id,
            result=const.RUN_RESULT_PARTIAL,
            volume_l=delivered_l,
            planned_s=planned,
            actual_s=elapsed,
            detail=const.RUN_DETAIL_SELF_CLOSING_STOPPED,
            trigger=const.RUN_TRIGGER_SELF_CLOSING,
            add_to_total=True,
        )
        return True

    async def async_resume_self_closing_runs(self) -> None:
        """Reconcile persisted in-flight runs after a restart.

        Self-closing hardware closes on its own, so we NEVER re-open: if the run
        is overdue it has already closed (finalise); if it is still within its
        window the hardware countdown is still running (reschedule the cosmetic
        cleanup for the remainder). The bucket was credited at start
        (credited=True), so it is never re-credited here.
        """
        for run in await self._sc_active_runs():
            zone_id = run.get(const.RUN_ZONE_ID)
            planned = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
            elapsed = self._sc_elapsed(run.get(const.RUN_STARTED))
            if elapsed >= planned:
                await self._sc_finish_run(zone_id)
            else:
                self._sc_schedule_cleanup(zone_id, planned - elapsed)

    @staticmethod
    def _sc_is_self_closing(zone: dict) -> bool:
        """True if the zone delegates its run to a self-closing target."""
        return zone.get(const.ZONE_WATERING_MODE) == const.WATERING_MODE_SERVICE

    async def _sc_maybe_stop(self, zone_id) -> bool:
        """Stop a self-closing zone here; return True if it was handled."""
        zone = self.store.get_zone(zone_id) or {}
        if not self._sc_is_self_closing(zone):
            return False
        await self.async_stop_self_closing(zone_id)
        return True
