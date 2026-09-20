"""Self-closing valve mode: delegate the valve close to self-closing hardware.

A zone in WATERING_MODE_SERVICE is run by firing a configured service with the
run duration; the valve owns the close (a hardware countdown), so an HA outage
mid-run cannot cause continuous irrigation. The bucket is credited optimistically
at start and the in-flight run is persisted for restart reconciliation.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.util import dt as dt_util

from . import const
from .batch import is_batch_zone
from .duration_math import hardware_window, opensprinkler_window
from .opensprinkler import is_opensprinkler_zone
from .run_chain import ChainPolicy, register_chain_policy
from .run_watch import (
    WatchPolicy,
    register_watch_policy,
    run_completion_tolerance,
    run_credit_ceiling,
    run_finish_grace_seconds,
    run_has_finish_grace,
    run_is_queue_bound,
    run_is_segmented,
    zone_latency_margin,
)

_LOGGER = logging.getLogger(__name__)

# What SERVICE mode contributes to the shared observation lifecycle.
#
# Unlike the queue modes this engine was written for, a service valve opens as it
# is dispatched: there is no queue, and by the time a watcher is armed the confirm
# poll has already seen the valve on. So the watcher exists for one question only
# — did the valve go off BEFORE the run's planned end? It used to have no way to
# ask. ``confirm_entity`` was read exactly once, at open, and nothing subscribed
# to it afterwards, so a valve that shut mid-run (a Zigbee dropout, a hardware
# fault, someone closing it by hand) left the wall clock running and the run was
# recorded as ``actual_s == planned_s``, completed, with the full optimistic
# credit standing. Reported on issue #88 by Eifel-Joe, who runs three such zones.
#
# ``acknowledges=False``: nothing queues the run, so there is no acknowledgement
# to wait for and none that can be withdrawn.
# ``segmented=False``: a self-closing valve cannot be paused and resumed; off is
# the end of the run.
# ``arm_give_up_after_start=False``: written after the engine was extracted, so it
# does not inherit the OpenSprinkler mode's preserved defect.
SERVICE_WATCH_POLICY = WatchPolicy(
    mode=const.WATERING_MODE_SERVICE,
    acknowledges=False,
    give_up_problem=const.PROBLEM_VALVE_DID_NOT_OPEN,
    accept_seconds=const.SERVICE_WATCH_GIVE_UP_SECONDS,
    queue_deadline_at_start=False,
    segmented=False,
    arm_give_up_after_start=False,
    opens_at_dispatch=True,
    # A service valve reports its own state, and these are exactly the valves
    # _confirm_valve_running is written around. One off sample is not evidence
    # the water stopped, so look again before settling the run.
    finish_settle_seconds=const.SERVICE_WATCH_SETTLE_SECONDS,
    # The valve reports both ends of the run itself, so actual_s is the window
    # between those reports and a close that arrives within the zone's latency
    # margin of the planned end still settles through the watcher (#139). The
    # backstop, armed at exactly the window, used to beat that report on every
    # normal run.
    settles_on_valve_window=True,
)
register_watch_policy(SERVICE_WATCH_POLICY)

# And its dispatch chain. Service zones used to be fired in a single loop by
# _dispatch_by_mode, so `zone_sequencing` never reached them: `sequential` and
# `rotating` were both dropped and the valves opened together whatever the
# setting said, while the setting's own help text promised the opposite without
# qualification. That is worse than the batch case, where `sequential` is at
# least what a queue does anyway — a user who chose `sequential` because their
# pump can only feed one zone was getting all of them at once. Issue #98.
CHAIN_POLICY = ChainPolicy(
    mode=const.WATERING_MODE_SERVICE,
    label="Service",
    token_prefix="service-chain:",
)
register_chain_policy(CHAIN_POLICY)


def is_self_closing_zone(zone: dict) -> bool:
    """True if the zone delegates its run to a self-closing target.

    Module level, and the single source of truth for "which modes are these",
    so a consumer that is not the coordinator — the finish-time estimate in
    skip_conditions — can ask without needing this mixin. ``_sc_is_self_closing``
    is the in-coordinator spelling and delegates here.
    """
    return isinstance(zone, dict) and zone.get(const.ZONE_WATERING_MODE) in (
        const.WATERING_MODE_SERVICE,
        const.WATERING_MODE_OPENSPRINKLER,
        const.WATERING_MODE_BATCH,
    )


class SelfClosingMixin:
    """Self-closing actuation lifecycle. Mixed into SmartIrrigationCoordinator."""

    @staticmethod
    def _sc_convert(seconds: float, unit: str) -> int:
        """Convert a run duration (seconds) to the hardware's unit, rounding up.

        The rounding itself lives in :func:`duration_math.hardware_window`, which
        answers the same question in both directions at once. The distributor's
        inlet asked it too and carried a byte-identical copy of these four lines;
        two copies of one rule is what let the window a valve runs drift from the
        window the books reserved for it. Kept as a name because it reads well at
        the dispatch, where only the value sent matters.
        """
        return hardware_window(seconds, unit)[0]

    @staticmethod
    def _sc_effective_seconds(seconds: float, unit: str) -> float:
        """How long the valve is really open, given the duration _sc_convert sends.

        A minute-unit controller cannot be told a partial minute, so _sc_convert
        rounds UP: a 263 s plan opens the valve for 300 s. Everything downstream of
        the dispatch — the run record, the bucket credit, the flow-calibration
        sample and the finish backstop — has to price THAT window and not the
        un-rounded plan, or it books a run the hardware never made.

        Measured on real valves by Eifel-Joe (#88), against the recorder: 502 -> 540,
        265 -> 300, 263 -> 300 seconds of open valve, i.e. 7.6-14.1% more water than
        the run log recorded, on every run. Two consequences beyond the miscount:
        the finish backstop was armed on the SHORT window and so settled the run
        36-40 s before the valve actually closed, which is why _watch_finish was
        unreachable on that zone; and the flow-calibration advisory divides the
        metered litres by the SHORT window, inflating the observed rate by the same
        ratio (a 70 s plan becomes a 120 s open, reading +71% on a correctly
        configured zone — enough to fire a false advisory, since the self-closing
        caller has no duration gate of its own; see #133).

        Both answers come from one call to :func:`duration_math.hardware_window`,
        so the window priced here cannot drift from the duration dispatched even
        by an edit that changes the rounding: they are the two halves of a single
        return value, not two derivations of one rule.
        """
        return hardware_window(seconds, unit)[1]

    def _sc_planned_window(self, zone: dict) -> float:
        """The seconds the hardware will hold this zone's valve open for its run.

        The single source for the run's planned window: the dispatch derives the
        duration it sends from the same two helpers, so the two cannot disagree.
        """
        seconds = float(zone.get(const.ZONE_DURATION) or 0)
        if seconds <= 0:
            return 0.0
        if is_opensprinkler_zone(zone):
            # run_station takes whole seconds and nothing else (see _sc_dispatch_open).
            # The ceiling is named in duration_math so the finish anchor can reserve
            # the same window this books, rather than a second copy of the rule.
            return float(opensprinkler_window(seconds))
        unit = zone.get(const.ZONE_DURATION_UNIT, const.DURATION_UNIT_SECONDS)
        return self._sc_effective_seconds(seconds, unit)

    def _sc_split_service(self, dotted: str):
        """'domain.service' -> (domain, service)."""
        domain, _, service = (dotted or "").partition(".")
        return domain, service

    async def _sc_dispatch_open(self, zone: dict) -> None:
        """Open the valve for its run by firing the run_service."""
        seconds = float(zone.get(const.ZONE_DURATION) or 0)
        if is_opensprinkler_zone(zone):
            # run_station takes whole seconds and nothing else; the duration unit
            # is a property of a user's own run_service script, not of this API.
            await self._os_dispatch_open(zone, int(self._sc_planned_window(zone)))
            return
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

    @staticmethod
    def _sc_master_token(zone_id) -> str:
        """Master-hold token for a self-closing zone's in-flight run.

        Deterministic (not a uuid) because the run is fire-and-forget: whoever
        finalises it — the cleanup timer, an early stop, or restart reconciliation
        — must be able to release the hold without having the original token.
        """
        return f"sc:{zone_id}"

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

    def _sc_cleanup_timers(self) -> dict:
        """Lazy {zone_id: cancel_cb} of scheduled self-closing cleanup timers.

        review finding D (sister of the I-1 interval overlap fix): the interval sampler
        and the cosmetic-finish timer are the two per-zone handles a run owns. Both must
        be cancel-and-replaced on an overlapping run and cancel-and-popped at finalize —
        otherwise a stale cleanup timer fires _sc_finish_run against a NEWER run and
        finalizes it early. Mirrors _sc_meters().
        """
        timers = getattr(self, "_sc_cleanup_handles", None)
        if timers is None:
            timers = self._sc_cleanup_handles = {}
        return timers

    def _sc_cancel_cleanup(self, zone_id) -> None:
        """Cancel-and-pop a zone's pending cleanup timer (no-op if none is stored).

        Cancelling an already-fired async_call_later handle (a TimerHandle.cancel) is
        safe, so this is called both when a run finalizes and before scheduling a new one.
        """
        cancel = self._sc_cleanup_timers().pop(zone_id, None)
        if cancel is not None:
            cancel()

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

    def _sc_finish_flow(self, zone_id, run: dict | None = None):
        """Cancel a zone's sampling and return (measured_l | None, end_changes). measured
        is None when there is no sensor, the meter was lost to a restart, or no positive
        flow was seen (caller then keeps its time-based volume). Takes ONE final reading
        at close so a totalizer's last (up to a poll interval) of climb isn't dropped.

        ``run`` is the record being finalised; the callers that only discard a meter
        pass none. When it carries the valve's off report, a rate sensor is metered to
        that report and not to this read (#139).
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
        off = dt_util.parse_datetime((run or {}).get(const.RUN_VALVE_OFF) or "")
        if off is not None:
            # A rate meter credits each interval at the rate read at its end. A run
            # whose valve reported its close is finalised after it: by the watcher,
            # the debounce later, or by the backstop at planned + grace. Before the
            # finish grace a normal end was the backstop's read at the planned end,
            # with the valve still open (#139). Now this read, or a 15 s tick before
            # it, ends the interval spanning the close with the water already
            # stopped, and up to a poll of flow the valve reported open is credited
            # at 0 (a sensor holding its last value credits the seconds after the
            # close instead). The report is when the water stopped, so the
            # integration ends there, the last interval at its last measured rate
            # (FlowMeter.end_rate_at), bounded by ONE poll — the cadence just
            # above — because the far end of that last interval is this report and
            # not a reading: a sensor that died mid-run credits nothing past its
            # last mark. Read first, cut after: a totalizer ignores the cut and
            # keeps this read, whose climb is water that flowed. A run without the
            # report (write-only, unverifiable, a close nobody reported, a backstop
            # that beat the report) is metered to this read as before.
            meter.end_rate_at(
                (off - started).total_seconds(), poll_s=const.FLOW_POLL_INTERVAL
            )
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

    async def _sc_finish_run(self, zone_id, *, actual_s: float | None = None) -> None:
        """Finalise a completed run: record actual usage, clear, fire finished.

        Idempotent: a no-op if the run is no longer active (e.g. the cleanup
        timer fires after an early stop already removed it), so usage is never
        double-counted.

        ``actual_s`` is the window the valve itself reported open, passed by the
        watcher when it settles a confirmed service run on its stored off report
        (#139), and by a manual stop that settles such a run inside its finish
        grace by the same rule (see async_stop_self_closing), where a valve still
        reporting on makes it the plan. Without it the run is recorded for its
        plan, as it is for every caller with no reported close to go on (the
        backstop, the watcher's rule for a close nobody reported, OpenSprinkler,
        batch).
        """
        run = await self._sc_find_run(zone_id)
        if run is None:
            return
        await self._sc_remove_run(zone_id)
        # review finding D: pop this run's cleanup handle as it finalizes so a stale
        # timer can't linger (the firing timer itself lands here; cancel is a safe no-op).
        self._sc_cancel_cleanup(zone_id)
        # Same for the station subscription, which reaches here via the +planned
        # backstop when a station's "off" transition is missed.
        self._os_cancel_watch(zone_id)
        # The hardware has closed the valve — drop the master hold taken at open.
        await self.async_master_release(self._sc_master_token(zone_id))
        zone = self.store.get_zone(zone_id) or {}
        # Count usage once, at completion, for the actual delivered volume.
        # planned_s is what the run was sized and credited for; it no longer
        # implies the run ran that long — actual_s below may record a shorter
        # or longer reported window (#139).
        planned_s = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
        # Iter FM-5: prefer the measured volume from the non-blocking sampler over the
        # open-time time-based estimate. Cancel the sampler + persist the totalizer end
        # for cross-run learning. measured is None when the zone has no flow_sensor, the
        # meter was lost to a restart, or no positive flow was seen -> time-based volume.
        measured, end_changes = self._sc_finish_flow(zone_id, run)
        if end_changes:
            await self.store.async_update_zone(zone_id, end_changes)
        if measured is not None:
            # Reconcile the bucket ABSOLUTELY from the pre-run level: the optimistic open
            # credit was time-based (and may have clamped at the ceiling), so a delta
            # correction would over-/under-shoot. Recompute measured credit from B0 and
            # clamp once — correct in every quadrant. See test_self_closing.
            pre_bucket = float(run.get(const.RUN_PRE_BUCKET) or 0)
            nb = pre_bucket + self._credited_depth_native(zone, measured)
            # Against the ceiling the DISPATCH decided, not a fresh maximum_bucket:
            # clamping this reconcile at maximum_bucket undid the dispatch clamp
            # and settled a completed run at the surplus again — the flow-sensor
            # half of issue #88, which the no-sensor path never showed.
            nb = min(nb, run_credit_ceiling(run, zone))
            await self.async_write_watered_bucket(zone_id, nb)
            zone = self.store.get_zone(zone_id) or zone
            volume_l = measured
        else:
            volume_l = self._timed_volume_l(zone, planned_s)
        await self._stamp_run_finalized(zone_id, volume_l)
        await self._record_run(
            zone_id,
            result=const.RUN_RESULT_COMPLETED,
            volume_l=volume_l,
            planned_s=planned_s,
            # The observed window when there is one (#139): a completed run used
            # to discard it for planned_s, so a valve closing 2-3 s late, or up
            # to its margin early, was recorded as exactly on time. It is also
            # what the calibration probe below prices its litres over; the timed
            # volume above stays on planned_s, the window the run was credited
            # and sized for.
            actual_s=planned_s if actual_s is None else actual_s,
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
        # Root: the advisory reads litres / minutes as the zone's observed rate, and
        #   since the meter is cut at the valve's off report (#139) those litres span
        #   the REPORTED window. Divided by the plan, a 60 s run whose close is reported
        #   4 s late reads 6.7 % fast on every run, in a band judged at 15 %.
        # Fix: divide by the window the litres were measured over. A run with no report
        #   (the backstop, write-only, OpenSprinkler, batch) has only its plan, as it
        #   has for actual_s above.
        # NOT-TO-DO: do not move the timed volume above onto actual_s as well — it
        #   prices the water the run was CREDITED for, which stays the plan.
        # See test_service_watch.py::TestTheAdvisoryIsPricedOnTheWindowItMeasured.
        await self._flow_calibration_check(
            zone, measured, planned_s if actual_s is None else actual_s
        )
        # Ordered AFTER _sc_remove_run above so the calculation no longer sees a run
        # in flight. No-op unless this run displaced one.
        await self.async_run_deferred_calculation(zone_id)
        # Likewise ordered after the removal: the chain only starts the next
        # zone once nothing of its mode is in flight. Keyed on the RUN's mode, so
        # a station run advances the station chain and a service run the service
        # one. No-op unless a chain of that mode is pending.
        await self._chain_advance_for_run(zone_id, run)

    def _sc_schedule_cleanup(self, zone_id, delay_seconds: float) -> None:
        """Schedule the cosmetic finish after the given delay.

        The caller decides what that delay covers — the run's planned
        duration, or, for a confirmed service run waiting out its finish
        grace (#139), planned + grace minus what has already elapsed.
        """

        async def _done(_now):
            await self._sc_finish_run(zone_id)

        # review finding D (sister of the I-1 interval overlap fix): a manual run that
        # overlaps an active scheduled run on the SAME zone replaces the persisted record
        # (_sc_add_run) and the interval sampler (_sc_start_flow_sampling), but the PRIOR
        # cleanup timer would otherwise linger and fire _sc_finish_run against the NEW run
        # — finalizing it early (false COMPLETED, actual_s=planned_s, dropped flow tail).
        # Cancel-and-replace the prior handle, exactly as the interval half does.
        self._sc_cancel_cleanup(zone_id)
        self._sc_cleanup_timers()[zone_id] = async_call_later(
            self.hass, max(0.0, delay_seconds), _done
        )

    def _sc_valve_on_instant(self, entity_id, lower, upper) -> str:
        """The instant a confirmed valve reported itself on, as ISO-8601 UTC.

        Its state's last_changed, clamped to [lower, upper] = [dispatch, confirm
        return] (#139). RUN_STARTED is stamped after the confirm poll returns, up
        to a poll later than the water, so measuring the valve window from it
        would shorten every run by that poll. But last_changed alone is not safe
        either: _confirm_valve_running accepts a valve that was ALREADY on at its
        first read, whose last_changed can be hours old, and a report can never
        precede the command that caused it. Without a state (nothing to read) the
        confirm return is the only instant known to be on.
        """
        state = self.hass.states.get(entity_id)
        reported = state.last_changed if state else upper
        return min(max(reported, lower), upper).isoformat()

    async def async_run_self_closing(
        self, zone: dict, *, trigger: str = "schedule"
    ) -> bool:
        """Fire a self-closing run for one zone. Returns True if started."""
        zone_id = zone.get(const.ZONE_ID)
        # The window the HARDWARE will run, not the un-rounded plan: a minute-unit
        # controller rounds a 263 s plan up to 300 s, and the record, the credit,
        # the flow sample and the backstop all have to price what the valve does.
        # See _sc_effective_seconds (#88).
        planned_seconds = self._sc_planned_window(zone)
        if planned_seconds <= 0:
            return False

        # OpenSprinkler: resolve the station's running sensor BEFORE anything is
        # actuated. It is the only thing that can end this run — the controller
        # queues the station, so there is no window measurable from here — and a
        # run dispatched without it would credit the bucket and never finalise.
        # Resolution is deliberately at dispatch, not at config time, so a
        # controller that was offline when the zone was set up still works.
        is_opensprinkler = is_opensprinkler_zone(zone)
        watch_entity = None
        if is_opensprinkler:
            station, watch_entity = self._os_resolve(zone)
            if not station or not watch_entity:
                _LOGGER.warning(
                    "Zone %s: cannot resolve the running sensor for OpenSprinkler "
                    "station '%s' (is the controller reachable?); not dispatching",
                    zone_id,
                    station or zone.get(const.ZONE_LINKED_ENTITY),
                )
                self._set_zone_fault(zone_id, const.PROBLEM_STATION_UNRESOLVED)
                self._fire_zone_problem(
                    zone_id,
                    zone,
                    zone.get(const.ZONE_LINKED_ENTITY),
                    const.PROBLEM_STATION_UNRESOLVED,
                )
                return False

        # Single-flight backstop. Every caller filters in-flight zones out first,
        # but _sc_add_run silently REPLACES an existing record for the same zone
        # rather than rejecting — so a second dispatch that reached here would
        # open the valve again, credit the bucket a second time, and orphan the
        # first run's record. Mirrors the distributor's busy check (irrigation.py
        # async_run_zone). See tests/test_run_in_flight.py.
        if self.zone_run_in_flight(zone_id):
            _LOGGER.info(
                "Zone %s already has a run in flight; ignoring the self-closing "
                "dispatch",
                zone_id,
            )
            return False

        # Observed-watering (opt-in) may watch this zone's observed_entity, which
        # our own run_service opens. Mark the run window as SI-driven so the
        # observer does not double-credit it (the run already credits the bucket).
        self._note_si_valve(int(zone.get(const.ZONE_ID)), planned_seconds)

        # Master (pump): hold it up BEFORE the valve opens, and keep the hold for
        # the whole fire-and-forget window — the hardware owns the close, so the
        # release happens in _sc_finish_run / async_stop_self_closing rather than
        # here. Token is keyed on the zone so those paths can release it without
        # threading a value through the persisted run record.
        await self.async_master_acquire(self._sc_master_token(zone_id))

        # The earliest instant the valve can have opened BECAUSE of this run: the
        # lower bound of RUN_VALVE_ON (#139). Taken immediately before the open
        # is fired, so a valve that was already on before the dispatch is
        # anchored here and not at its hours-old last_changed.
        dispatched_at = dt_util.utcnow()
        await self._sc_dispatch_open(zone)

        # Iter FM-5 (unified flow engine): measure delivered volume across the fixed
        # self-closing window via NON-blocking interval sampling — the run stays
        # fire-and-forget (the hardware owns the close); finalized in _sc_finish_run /
        # async_stop_self_closing. See test_self_closing.
        #
        # NOT for a queued OpenSprinkler run: the meter is seeded at open, and a
        # station behind three others opens hours later, so the sampled window
        # would mostly precede the water. _os_observed_start starts it instead.
        if not is_opensprinkler:
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
            #
            # Never on the OpenSprinkler path. _confirm_valve_running polls for
            # VALVE_CONFIRM_TIMEOUT seconds and self-closing mode treats False as
            # fatal, but a queued station is not running at +30s — so every zone
            # behind the first would abort here, after the controller had already
            # accepted its run: Irrigation Plus would believe it watered nothing
            # while the controller watered everything. The station subscription
            # replaces both the poll and its abort branch.
            confirm_target = (
                None if is_opensprinkler else zone.get(const.ZONE_CONFIRM_ENTITY)
            )
            confirmed = (
                await self._confirm_valve_running(zone_id, confirm_target, retry=False)
                if confirm_target
                else None
            )
            # The upper bound of RUN_VALVE_ON (#139): the poll that saw the valve
            # on has just returned, so it cannot have reported on any later.
            # Stamped here and not at RUN_STARTED below, which follows the bucket
            # write and is later still. _confirm_valve_running keeps its boolean
            # return: three other callers compare it with `is False`.
            confirmed_at = dt_util.utcnow()
            if confirmed is False:
                # The valve never opened -> abort the run. Cancel the just-started
                # sampling (discard the measurement) so the aborted run leaks no
                # interval/meter, and drop the master hold: no run means nothing
                # needs the pump, and a leaked hold would keep it on forever.
                self._sc_finish_flow(zone_id)
                await self.async_master_release(self._sc_master_token(zone_id))
                # Nor the live-run marker: this run credited nothing, so the
                # ceiling it was granted must not be inherited by the next one.
                self._drop_live_run_marker(zone_id)
                self._fire_zone_problem(
                    zone_id, zone, confirm_target, const.PROBLEM_VALVE_DID_NOT_OPEN
                )
                return False

            # Optimistic bucket credit (the valve owns the close -> assume completion).
            volume_l = self._timed_volume_l(zone, planned_seconds)
            depth = self._credited_depth_native(zone, volume_l)
            # Stash the pre-run bucket so the finish can reconcile the measured credit
            # ABSOLUTELY from B0 (this optimistic credit may clamp at the ceiling; a
            # delta correction at finish would then over-/under-shoot). See _sc_finish_run.
            pre_bucket = float(zone.get(const.ZONE_BUCKET) or 0)
            # Clamp at the RUN's ceiling, not at maximum_bucket — see the same fix
            # in batch._batch_record_run and tests/test_credit_ceiling.py (issue #88).
            # Captured into the run record below: _run_ceiling consumes the
            # live-estimate marker, so this is the one moment it can be asked, and
            # the finish paths have to clamp against this same number or they put
            # the surplus back (run_credit_ceiling).
            ceiling = self._run_ceiling(zone)
            new_bucket = min(ceiling, pre_bucket + depth)
            await self.async_write_watered_bucket(zone_id, new_bucket)
            # NB: water_used_total is NOT counted here — it is recorded once at the
            # run's actual end (_sc_finish_run / async_stop_self_closing) for the
            # delivered volume, so an early stop can't over-report usage. The bucket,
            # however, IS credited optimistically above (the crash-safe model state).

            # Persist the in-flight run for restart reconciliation. RUN_STARTED is
            # the DISPATCH time; for an OpenSprinkler run that is when the station
            # joined the controller's queue, not when it waters, so the watch
            # entity is persisted alongside it and RUN_OBSERVED_START stays absent
            # until the station is seen running.
            record = {
                const.RUN_ZONE_ID: zone_id,
                const.RUN_ENTITY_ID: (
                    zone.get(const.ZONE_LINKED_ENTITY)
                    if is_opensprinkler
                    else zone.get(const.ZONE_RUN_SERVICE)
                ),
                const.RUN_STARTED: dt_util.utcnow().isoformat(),
                const.RUN_PLANNED_SECONDS: planned_seconds,
                const.RUN_PLANNED_MM: depth,
                const.RUN_PRE_BUCKET: pre_bucket,
                const.RUN_CEILING: ceiling,
                const.RUN_MODE: zone.get(const.ZONE_WATERING_MODE),
                const.RUN_CREDITED: True,
            }
            if is_opensprinkler:
                record[const.RUN_WATCH_ENTITY] = watch_entity
            elif confirmed:
                # A service valve confirmed open is observable for the rest of its
                # run: persisted so a restart can re-adopt the subscription rather
                # than fall back to the clock. Only when it was actually confirmed
                # — a write-only run (no confirm_entity) has nothing to watch, and
                # the hardware still owns its close.
                record[const.RUN_WATCH_ENTITY] = confirm_target
                # And the two things its finish is settled on (#139): the zone's
                # latency margin, frozen so a margin edited mid-run cannot move a
                # backstop that is already armed (and whose presence is what gives
                # this record a finish grace at all), and the valve's own on
                # report, the anchor of the window actual_s is measured over. Only
                # here: a write-only or unverifiable run has no valve reports, so
                # it keeps the backstop at exactly its window, as before.
                record[const.RUN_LATENCY_MARGIN] = zone_latency_margin(zone)
                record[const.RUN_VALVE_ON] = self._sc_valve_on_instant(
                    confirm_target, dispatched_at, confirmed_at
                )
            await self._sc_add_run(record)

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
            if is_opensprinkler:
                # The station's own sensor drives the rest of the lifecycle: the
                # observed start, the finish, and giving up on a run the
                # controller never ran. A timer from here would measure the queue.
                await self._os_start_watch(
                    zone_id, watch_entity, planned_seconds, accepted=False
                )
            else:
                # The backstop is armed FIRST and stays the mode's own: the valve
                # is already open and its window already running, so the watcher
                # below must not re-arm it (WatchPolicy.opens_at_dispatch).
                #
                # For a confirmed run it waits the finish grace past the window:
                # the debounce plus the frozen latency margin (#139). Armed at
                # exactly the window it fired before the valve's off report on
                # every normal run (measured 2-3 s late on Tuya valves) or inside
                # the debounce, cancelling the watcher, so the run was never
                # settled on what the valve did. Added HERE and not inside
                # _sc_schedule_cleanup, which batch and OpenSprinkler share; a
                # record without the margin gets 0 and the window as before.
                self._sc_schedule_cleanup(
                    zone_id, planned_seconds + run_finish_grace_seconds(record)
                )
                if confirmed:
                    # And now watch the valve for the rest of the run. Only a
                    # CONFIRMED run: without a confirm_entity there is nothing to
                    # subscribe to, and the run stays write-only exactly as before.
                    # accepted=True — nothing acknowledges a service run, and the
                    # confirm poll has already seen this valve on.
                    await self._watch_start(
                        zone_id, confirm_target, planned_seconds, accepted=True
                    )
            return True
        except Exception:
            self._os_cancel_watch(zone_id)  # nor the station subscription
            self._sc_finish_flow(zone_id)  # don't leak the interval on a setup failure
            # Nor the master hold — otherwise the pump stays on with no run behind it.
            await self.async_master_release(self._sc_master_token(zone_id))
            # Nor the live-run marker, if the failure landed before it was consumed.
            self._drop_live_run_marker(zone_id)
            raise

    def _sc_elapsed(self, started_iso: str | None) -> float:
        """Wall-clock seconds since the run started (includes downtime)."""
        started = dt_util.parse_datetime(started_iso or "")
        if started is None:
            return 0.0
        return max(0.0, (dt_util.utcnow() - started).total_seconds())

    def _sc_run_elapsed(self, run: dict) -> float:
        """Seconds this run has been WATERING, which is not always since dispatch.

        An OpenSprinkler run sits in the controller's queue between the two, so
        for it RUN_STARTED bounds nothing: before the station is observed running
        the delivered volume is zero, however long ago the run was dispatched.
        Every other mode opens its valve at dispatch, so the two coincide.

        A run that can be PAUSED is not one contiguous stretch at all, and those
        record their watering as segments instead (see RUN_WATERED_SECONDS). The
        segment fields are consulted only when the run actually carries them, so
        every mode that cannot pause keeps the contiguous timing below unchanged
        — which for OpenSprinkler matters beyond tidiness, because its observed
        start is the controller's own reported one rather than the instant the
        transition was seen.
        """
        if run_is_segmented(run):
            return self._sc_segmented_elapsed(run)
        observed = run.get(const.RUN_OBSERVED_START)
        if observed:
            return self._sc_elapsed(observed)
        if run_is_queue_bound(run):
            return 0.0
        return self._sc_elapsed(run.get(const.RUN_STARTED))

    def _sc_segmented_elapsed(self, run: dict) -> float:
        """Watering seconds for a run recorded as segments.

        The segments that have closed, plus the one currently open if there is
        one. While the controller is paused no segment is open, so the total
        simply stops advancing — which is the whole point of the model.

        Tolerant of a malformed accumulator rather than raising: this feeds run
        finalisation, and a run that cannot compute its own length would other-
        wise never settle, holding its zone and the pump indefinitely. A bad
        value reads as zero, which settles the run as having delivered nothing
        and reverses its optimistic credit — the safe direction.
        """
        try:
            total = float(run.get(const.RUN_WATERED_SECONDS) or 0)
        except (TypeError, ValueError):
            total = 0.0
        segment = run.get(const.RUN_SEGMENT_STARTED)
        if segment:
            total += self._sc_elapsed(segment)
        return max(0.0, total)

    async def _sc_find_run(self, zone_id):
        for r in await self._sc_active_runs():
            if r.get(const.RUN_ZONE_ID) == zone_id:
                return r
        return None

    async def async_stop_self_closing(
        self,
        zone_id,
        *,
        close_valve: bool = True,
        detail: str | None = None,
        actual_s: float | None = None,
    ) -> bool:
        """Stop a self-closing run early: close the valve + correct the bucket.

        ``close_valve=False`` settles the accounting without touching the
        hardware, for the case where the hardware has already ended the run
        itself — an OpenSprinkler station that stopped short of its window, or
        one that never opened at all. ``detail`` overrides the run-log marker.
        ``actual_s`` is the delivered window when the caller measured it from
        the valve's own reports (#139). Without it, a stop that closes a
        confirmed service run's valve is measured from the valve's on report,
        and one past the planned end, inside the run's finish grace, is settled
        by the watcher's rule, which may complete the run; every other call
        reads the run's elapsed time, as before.
        """
        run = await self._sc_find_run(zone_id)
        if run is None:
            return False
        zone = self.store.get_zone(zone_id) or {}
        # Whatever ends the run, the station subscription has nothing left to
        # observe — and left armed it would fire against the NEXT run.
        self._os_cancel_watch(zone_id)
        # The run is ending here regardless of how the close goes — release the
        # master hold taken at open so the pump is not stranded on.
        await self.async_master_release(self._sc_master_token(zone_id))

        # Close the valve (best-effort). Skipped entirely when the hardware has
        # already ended the run itself, which is every OpenSprinkler finish
        # except a user-initiated stop.
        if close_valve:
            if is_opensprinkler_zone(zone):
                # opensprinkler.stop is entity-targeted; the stop_service adapter
                # below sends a zone_id that its schema rejects.
                await self._os_dispatch_stop(zone)
            elif stop_svc := zone.get(const.ZONE_STOP_SERVICE):
                domain, service = self._sc_split_service(stop_svc)
                data = {}
                data["zone_id"] = zone_id
                # A zero duration IS the stop instruction for the shipped
                # blueprints, which run one script for both directions and
                # branch on it. It was documented but never actually sent, so
                # the script received no `duration` at all and a template
                # reading it raised instead of closing the valve — the call is
                # not blocking, so that surfaced only in the log while the run
                # was settled as stopped and the valve went on watering to the
                # end of its hardware countdown. Sent under the zone's own
                # duration field, the same key the open uses.
                field = zone.get(const.ZONE_DURATION_FIELD) or "duration"
                data[field] = 0
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
        # A caller that measured the window at the valve's off report passes it
        # (#139). Reading the clock here instead puts the debounce into a
        # watcher-settled partial: this runs 5 s after the close, and those 5 s
        # are credited, volumed and recorded as delivered. The watcher accepts
        # that only for a close nobody reported, which has no other end (see
        # _watch_finish). One value feeds all three below, so the bucket, the
        # volume and actual_s agree.
        if actual_s is not None:
            elapsed = actual_s
        elif close_valve and run_has_finish_grace(run):
            # A stop that closes a confirmed service run's valve is measured from
            # the valve's own on report, the anchor the watcher settles on:
            # RUN_OBSERVED_START is the confirm return, up to a poll after that
            # report, so a stopped run would be measured shorter than a settled
            # one. Only such a stop. A caller passing close_valve=False saw the
            # hardware end the run and keeps its own clock: the watcher decided
            # its partial for a close nobody reported on the elapsed time below,
            # so it is booked on it too. And _sc_run_elapsed stays for every run
            # without a frozen margin (write-only, batch, OpenSprinkler, a
            # pre-update service record), whose queue-bound and segmented timing
            # the window does not know.
            if self._sc_elapsed(run.get(const.RUN_STARTED)) < planned:
                # Before the planned end (from RUN_STARTED, where the backstop is
                # anchored) the run is not in its finish grace, and the stop is
                # its end, as it always was: measured to the stop and capped at
                # the plan, even with an off report stored, whose debounce has
                # not decided yet whether it was the close or a blip.
                elapsed = self._watch_valve_window({**run, const.RUN_VALVE_OFF: None})
            else:
                # Past the planned end the run is only waiting in its finish
                # grace for the valve to report the close. Before the grace the
                # backstop finished it at the planned end for its plan; measured
                # to the stop, the grace would now be booked as watering, a
                # partial for more than the plan. So it is settled by the
                # watcher's rule (_watch_settle_by_window) on the same reports:
                # the window to the stored off report, or the plan while the
                # valve still reports on, completes within the tolerance, with
                # the finished event and the calibration sample as the watcher
                # would, and a shorter window is a partial on it below. The
                # valve was closed above first, as by any stop. _sc_finish_run
                # cancels the subscription and releases the master hold again:
                # the subscription is already gone, and releasing a dropped
                # token only re-arms the pump's off timer for the deadline it
                # already has.
                elapsed = self._watch_valve_window(run)
                if elapsed + run_completion_tolerance(run) >= planned:
                    await self._sc_finish_run(zone_id, actual_s=elapsed)
                    return True
        else:
            elapsed = self._sc_run_elapsed(run)
        delivered_frac = min(elapsed / planned, 1.0) if planned > 0 else 1.0
        # Iter FM-5: finalize the flow sampler UP FRONT — the measured litres both refine
        # the recorded usage below AND (review finding F) reconcile the bucket. Cancels the
        # sampler and persists the totalizer end for cross-run learning. measured is None
        # when there is no sensor, the meter was lost to a restart, or no positive flow was
        # seen. See test_self_closing.
        measured, end_changes = self._sc_finish_flow(zone_id, run)
        if end_changes:
            await self.store.async_update_zone(zone_id, end_changes)
        # Reconcile ABSOLUTELY from the pre-run level (RUN_PRE_BUCKET) when we have it: the
        # optimistic open credit may have CLAMPED at the ceiling, so subtracting the
        # undelivered mm from the (clamped) current bucket would over-/under-shoot — the
        # same clamp-then-delta trap _sc_finish_run reconciles from B0 to avoid. Legacy
        # delta fallback for a run persisted before RUN_PRE_BUCKET existed (upgrade mid-run).
        pre_bucket = run.get(const.RUN_PRE_BUCKET)
        if pre_bucket is not None:
            # The dispatch's ceiling, not a fresh maximum_bucket — same reason as
            # the completion twin above (issue #88).
            ceiling = run_credit_ceiling(run, zone)
            if measured is not None:
                # review finding F: match the completion twin's measured reconcile — when a
                # flow sensor produced a valid measurement, credit the bucket from the
                # MEASURED delivered depth (pre_bucket + credited_depth), exactly like
                # _sc_finish_run, instead of the time-based planned_mm * delivered_frac.
                # Under a miscalibrated throughput the time-based partial over-/under-credits
                # the bucket; the measured volume is ground truth. Time-based stays the
                # no-measurement fallback below.
                nb = float(pre_bucket) + self._credited_depth_native(zone, measured)
            else:
                nb = float(pre_bucket) + planned_mm * delivered_frac
            nb = min(nb, ceiling)
            await self.async_write_watered_bucket(zone_id, nb)
        else:
            # No pre-run anchor -> no absolute measured reconcile is possible; keep the
            # time-based undelivered subtraction (measured only refines the usage log).
            undelivered_mm = planned_mm * (1.0 - delivered_frac)
            if undelivered_mm:
                new_bucket = float(zone.get(const.ZONE_BUCKET) or 0) - undelivered_mm
                await self.async_write_watered_bucket(zone_id, new_bucket)

        await self._sc_remove_run(zone_id)
        # review finding D: cancel-and-pop the original run's pending cleanup timer so it
        # can't fire _sc_finish_run after this early stop already removed the run.
        self._sc_cancel_cleanup(zone_id)
        # Count usage once, for what was actually delivered: the measured litres (finalized
        # above) or the time-based estimate when there was no measurement.
        delivered_l = (
            measured if measured is not None else self._timed_volume_l(zone, elapsed)
        )
        await self._stamp_run_finalized(zone_id, delivered_l)
        await self._record_run(
            zone_id,
            result=const.RUN_RESULT_PARTIAL,
            volume_l=delivered_l,
            planned_s=planned,
            actual_s=elapsed,
            detail=detail or const.RUN_DETAIL_SELF_CLOSING_STOPPED,
            trigger=const.RUN_TRIGGER_SELF_CLOSING,
            add_to_total=True,
        )
        # Ordered AFTER _sc_remove_run above so the calculation no longer sees a run
        # in flight. No-op unless this run displaced one.
        await self.async_run_deferred_calculation(zone_id)
        # A stopped, dropped or short run ends the chain's turn exactly as a
        # completed one does, so the next zone must start from here too.
        await self._chain_advance_for_run(zone_id, run)
        return True

    async def async_resume_self_closing_runs(self) -> None:
        """Reconcile persisted in-flight runs after a restart.

        Self-closing hardware closes on its own, so we NEVER re-open: overdue
        now means past its plan AND its finish grace (#139) — only then has
        the run definitely closed, so it is finalised. Anything short of
        that — still running, or past the plan but still waiting out the
        grace for its close to be reported — reschedules the cosmetic
        cleanup for the remainder instead. The bucket was credited at start
        (credited=True), so it is never re-credited here.
        """
        for run in await self._sc_active_runs():
            zone_id = run.get(const.RUN_ZONE_ID)
            planned = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
            # An OpenSprinkler run measured from RUN_STARTED would finalise early
            # whenever the restart caught it in the controller's queue: elapsed
            # there is queue time, not watering time. It reconciles against the
            # station's own state instead — and, like every branch here, never
            # re-opens anything.
            if run.get(const.RUN_MODE) == const.WATERING_MODE_OPENSPRINKLER:
                await self._os_resume_run(run)
                continue
            # Same reasoning for a batch run, which is also queued: its elapsed
            # is segment-based and its valve, not the clock, says whether it is
            # still watering. It is re-adopted, never re-dispatched.
            if run.get(const.RUN_MODE) == const.WATERING_MODE_BATCH:
                await self._batch_resume_run(run)
                continue
            elapsed = self._sc_elapsed(run.get(const.RUN_STARTED))
            # A confirmed service run waits planned + debounce + margin for its
            # valve to report the close (#139), and a restart must not take that
            # away: finishing it at planned, or re-arming the backstop for
            # planned - elapsed, would settle a run inside its grace for its plan
            # before a late close had the chance to be seen, which is the defect
            # the grace exists to fix. 0 for every record without a frozen margin
            # (write-only, pre-update), which keeps the formula it had.
            grace = run_finish_grace_seconds(run)
            if elapsed >= planned + grace:
                # Past the whole grace the run is finished for its plan, as it
                # was past the plan before, even with the valve's off report on
                # record: the backstop finishes such a run for its plan too.
                # Settling it on the reported window instead would improve a
                # record the grace does not make worse, so it is left as it was.
                await self._sc_finish_run(zone_id)
            else:
                # Not yet overdue: the backstop is re-armed for the remainder,
                # inside the plan or inside the grace alike, and the watcher is
                # re-adopted below without retaking the master in the grace.
                # Master holds live only in memory and did not survive the
                # restart, so it is re-taken for the remainder — but only
                # while the valve is still running (elapsed < planned). Past
                # the plan but inside the grace, the valve's own countdown is
                # over and the run only waits for the report of its close: a
                # hold taken for that would switch the pump on, kick it and wait
                # the master settle for a valve that has closed, where a restart
                # past the plan used to finish the run without starting the
                # pump. Settling the run then releases a token that is not held,
                # as finishing it outright above always has.
                if elapsed < planned:
                    await self.async_master_acquire(self._sc_master_token(zone_id))
                    # Re-read: that await is not free. With a master configured
                    # and the pump off it waits the kick pause and then the
                    # master settle, so the instant the timer below is created
                    # is about a settle later than the one `elapsed` was read
                    # at. Arming from the stale value makes the backstop due
                    # that much after the anchor it is meant to sit on, while
                    # the in-flight predicate — which counts from RUN_STARTED
                    # and knows nothing of the sleep — has already ended: the
                    # gap between the two is a window in which a second
                    # dispatch for this zone passes the guard and the old
                    # record then finalises over it (#152). A remainder that
                    # has gone negative meanwhile is clamped by
                    # _sc_schedule_cleanup, which fires it at once — correct,
                    # since such a run is past its whole grace.
                    elapsed = self._sc_elapsed(run.get(const.RUN_STARTED))
                self._sc_schedule_cleanup(zone_id, planned + grace - elapsed)
                # The valve subscription did not survive either, and without it
                # the rest of this run is back to being timed blind. Re-adopt it
                # for the runs that recorded one (a confirmed service run). A
                # valve that closed while HA was down is found off by the
                # watcher's first evaluate, or reports off after coming back as
                # unavailable; neither is stored as the off report (its
                # last_changed is the entity's return, not the close), so the
                # run is settled like any close nobody reported (_watch_finish).
                # An off report stored before HA went down stays on the record
                # and settles the run on its window, provided the debounce
                # decides before the backstop re-armed above.
                watch_entity = run.get(const.RUN_WATCH_ENTITY)
                if watch_entity:
                    await self._watch_start(
                        zone_id, watch_entity, planned, accepted=True
                    )

    @staticmethod
    def _sc_is_self_closing(zone: dict) -> bool:
        """True if the zone delegates its run to a self-closing target.

        Covers OpenSprinkler too, and that is what keeps a station switch away
        from every path that would drive linked_entity directly — the metered
        runner, the rotating/sequential/parallel dispatch, and async_stop_zone's
        turn_off. Turning a station switch on rewrites controller configuration
        and does not water; see opensprinkler.py.
        """
        return is_self_closing_zone(zone)

    async def _sc_maybe_stop(self, zone_id) -> bool:
        """Stop a self-closing zone here; return True if it was handled."""
        zone = self.store.get_zone(zone_id) or {}
        if not self._sc_is_self_closing(zone):
            return False
        if is_batch_zone(zone):
            # Batch stopping is not a per-zone action and cannot be made into
            # one: the controller stops the whole cycle, and the zones still
            # queued behind this one stay queued. So the stop clears the queue
            # and every run in flight is settled. See batch.async_stop_batch.
            await self.async_stop_batch(zone_id)
            return True
        await self.async_stop_self_closing(zone_id)
        return True
