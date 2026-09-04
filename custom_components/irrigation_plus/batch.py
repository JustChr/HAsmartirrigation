"""Batch/queue dispatch: one service call for a whole irrigation (issue #88).

Hand a controller the entire irrigation as an ordered list of (zone, duration)
and let it run that list from its own queue, instead of firing one service call
per zone and hoping they do not collide.

The motivating hardware is the ESPHome sprinkler component, but **nothing here is
ESPHome-specific**. The mode is a contract about what each configured entity must
MEAN — a switch that is on while this zone waters, an indicator that is on while
the controller is paused — so ordinary Home Assistant helpers satisfy it just as
well as a purpose-built controller does.

What this mode is, structurally: the OpenSprinkler lifecycle with a different
dispatch and a different watch entity. The run is persisted, credited
optimistically, timed from the moment its own valve is seen running (never from
dispatch, because a queued zone's water can be hours away), settled against what
it actually delivered, given up on a bounded deadline, and re-adopted rather than
re-dispatched after a restart. All of that is ``run_watch.RunWatchMixin`` and
``SelfClosingMixin``; this module supplies only what is genuinely different.

Three things really are different, and each is here because real hardware
behaves that way (@pnaklicki tested every one of them against a controller):

* **The controller can PAUSE.** The valve switch goes off while the controller
  keeps the remaining time, so a valve-off is not automatically the end of a run
  and run time must be the sum of watering segments. See ``const.RUN_WATERED_
  SECONDS`` and the ``segmented`` watch policy.
* **Stopping is not per-zone, and the queue outlives the stop.** Stopping one
  zone stops the whole cycle, but zones already queued stay queued and will water
  on a later manual start. So a stop must settle EVERY batch run in flight and
  must clear the queue, or those zones water later with nothing supervising them.
* **The controller may manage its own pump.** Then a Irrigation Plus master
  entity must NOT also be configured — that gives one pump two independent
  owners, which is exactly what the master refcounting model exists to prevent.
  Documented rather than enforced; the integration cannot detect it.
"""

from __future__ import annotations

import logging

from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util

from . import const
from .run_watch import (
    NO_INFO_STATES,
    RUNNING_STATES,
    WatchPolicy,
    planned_seconds,
    register_watch_policy,
    run_is_queue_bound,
)

_LOGGER = logging.getLogger(__name__)

# What batch mode contributes to the shared observation lifecycle.
#
# ``acknowledges=False``: a controller handed the whole queue in one call has
# accepted it by the time that call returns, so there is no separate
# acknowledgement to wait for and none to be withdrawn. That makes the
# queue-derived deadline the ONLY backstop, which is why it has to be armed at
# dispatch rather than after an acknowledgement that never comes.
#
# ``segmented=True``: this controller can pause. See the module docstring.
WATCH_POLICY = WatchPolicy(
    mode=const.WATERING_MODE_BATCH,
    acknowledges=False,
    give_up_problem=const.PROBLEM_ZONE_NEVER_RAN,
    queue_deadline_at_start=True,
    segmented=True,
    # Written after the engine was extracted, so it does not inherit the
    # OpenSprinkler mode's preserved defect: a resumed run that is already
    # watering is bounded by its finish backstop, not by a give-up timer that
    # nothing would take back down.
    arm_give_up_after_start=False,
)
register_watch_policy(WATCH_POLICY)

__all__ = ["BatchMixin", "is_batch_zone"]


def is_batch_zone(zone) -> bool:
    """True if this zone is watered through a batch/queue controller."""
    return (
        isinstance(zone, dict)
        and zone.get(const.ZONE_WATERING_MODE) == const.WATERING_MODE_BATCH
    )


def batch_watch_entity(zone) -> str | None:
    """The entity whose on/off state IS this zone's run.

    The zone's ``confirm_entity``, whose documented meaning is already "the real
    valve/switch state the run_service drives". In every other mode it is an
    optional extra confirmation; in batch mode it is promoted to required,
    because it is the only thing that can start or end the run.
    """
    return (zone or {}).get(const.ZONE_CONFIRM_ENTITY) or None


class BatchMixin:
    """Batch/queue dispatch. Mixed into SmartIrrigationCoordinator."""

    # --- configuration ------------------------------------------------------

    async def _batch_config(self) -> dict:
        """The instance-level batch settings."""
        return await self.store.async_get_config()

    def _batch_paused_entity_sync(self) -> str | None:
        """The paused indicator, read from the live Config object.

        Synchronous because the state-change callback path needs it without an
        await. The isinstance guard matters for the same reason it does in
        ``_persisted_self_closing_runs``: a test double's config is often a bare
        ``Mock()``, whose every attribute answers with another Mock.
        """
        value = getattr(
            getattr(self.store, "config", None), const.CONF_BATCH_PAUSED_ENTITY, None
        )
        return value if isinstance(value, str) and value else None

    # --- dispatch -----------------------------------------------------------

    def _warn_sequencing_ignored(self, zones: list) -> None:
        """Say, once, that ``rotating`` does not reach batch zones.

        ``rotating`` is the only sequencing mode whose loss is worth a line in
        the log. ``sequential`` is what a queue already does, and ``parallel``
        is the DEFAULT (``CONF_DEFAULT_ZONE_SEQUENCING``) — warning about it
        would fire on every batch install that never touched the setting, which
        is noise, not information. ``rotating`` is different: it is chosen
        deliberately, for runoff on a slope or a slow-draining soil, and it
        carries real behaviour (cap each pass, soak, interleave) that the queue
        drops entirely. A user who set it is watching for split passes that will
        never come, and today nothing anywhere says so — see issue #98.

        Once per sequencing value, not once per dispatch: this fires from the
        scheduled irrigation, so a per-dispatch warning would repeat every day
        for as long as the setting stands.
        """
        # Positive match rather than `!= sequential`, which also covers the two
        # ways this can be read without a real value: a config that has no
        # sequencing attribute answers None, and a test double's bare Mock
        # answers another Mock. Neither equals `rotating`, so neither warns, and
        # no isinstance guard is needed to keep them quiet.
        sequencing = getattr(
            getattr(self.store, "config", None), const.CONF_ZONE_SEQUENCING, None
        )
        if sequencing != const.CONF_ZONE_SEQUENCING_ROTATING:
            return
        if getattr(self, "_batch_sequencing_warned", None) == sequencing:
            return
        self._batch_sequencing_warned = sequencing
        _LOGGER.warning(
            "Zone sequencing is set to '%s', which does not apply to the %s "
            "batch zone(s) in this irrigation: the controller runs its own "
            "queue, so their passes are not capped, interleaved or given "
            "absorption time. They are dispatched as one ordered plan and each "
            "zone waters its full duration in one go. See issue #98",
            sequencing,
            len(zones),
        )

    async def async_dispatch_batch_zones(self, zones: list, *, trigger: str) -> None:
        """Hand the whole plan to the controller in one call.

        Order is the order of ``zones``: a queue runs one valve at a time, so
        this mode is inherently sequential and expresses ordering through the
        list rather than through ``zone_sequencing`` (whose ``parallel`` setting
        simply cannot be represented in a queue, and whose ``rotating`` setting
        is dropped — said out loud in ``_warn_sequencing_ignored``).
        """
        if not zones:
            return
        self._warn_sequencing_ignored(zones)
        config = await self._batch_config()
        run_service = config.get(const.CONF_BATCH_RUN_SERVICE)
        if not run_service:
            for zone in zones:
                zone_id = zone.get(const.ZONE_ID)
                self._set_zone_fault(zone_id, const.PROBLEM_BATCH_NOT_CONFIGURED)
                self._fire_zone_problem(
                    zone_id,
                    zone,
                    None,
                    const.PROBLEM_BATCH_NOT_CONFIGURED,
                )
            _LOGGER.warning(
                "Batch mode: %s zone(s) are due but no batch run service is "
                "configured; nothing was dispatched",
                len(zones),
            )
            return

        prepared = []
        plan = []
        for zone in zones:
            zone_id = zone.get(const.ZONE_ID)
            seconds = float(zone.get(const.ZONE_DURATION) or 0)
            if seconds <= 0:
                continue
            watch_entity = batch_watch_entity(zone)
            if not watch_entity:
                # Refused rather than dispatched. Without a watch entity the run
                # could be started but never observed: it would credit the bucket
                # at dispatch and then sit in flight until its deadline expired,
                # blocking the zone the whole time.
                _LOGGER.warning(
                    "Zone %s is in batch mode but has no confirm_entity, which is "
                    "the valve switch this mode observes the run on; not "
                    "dispatching it",
                    zone_id,
                )
                self._set_zone_fault(zone_id, const.PROBLEM_BATCH_NO_WATCH_ENTITY)
                self._fire_zone_problem(
                    zone_id, zone, None, const.PROBLEM_BATCH_NO_WATCH_ENTITY
                )
                continue
            # Single-flight backstop, exactly as async_run_self_closing keeps:
            # every caller filters in-flight zones out first, but a second
            # dispatch reaching here would credit the bucket twice and orphan the
            # first run's record.
            if self.zone_run_in_flight(zone_id):
                _LOGGER.info(
                    "Zone %s already has a run in flight; leaving it out of the "
                    "batch",
                    zone_id,
                )
                continue
            unit = zone.get(const.ZONE_DURATION_UNIT, const.DURATION_UNIT_SECONDS)
            prepared.append((zone, watch_entity, seconds))
            plan.append(
                {
                    "zone_id": zone_id,
                    "zone_name": zone.get(const.ZONE_NAME),
                    "duration": self._sc_convert(seconds, unit),
                }
            )

        if not plan:
            return

        # Master (pump) up before the first valve, and held for the whole queue —
        # which is what a pump needs anyway. One hold per zone, released as each
        # run finalises, so the cycle ends when the last zone does.
        for zone, *_ in prepared:
            await self.async_master_acquire(
                self._sc_master_token(zone.get(const.ZONE_ID))
            )

        domain, service = self._sc_split_service(run_service)
        try:
            await self.hass.services.async_call(
                domain, service, {const.BATCH_FIELD_ZONES: plan}
            )
        except Exception:
            # The plan never reached the controller, so nothing is watering and
            # nothing has been recorded yet. Drop the holds or the pump stays on
            # with no run behind it.
            for zone, *_ in prepared:
                await self.async_master_release(
                    self._sc_master_token(zone.get(const.ZONE_ID))
                )
            raise

        for zone, watch_entity, seconds in prepared:
            zone_id = zone.get(const.ZONE_ID)
            try:
                await self._batch_record_run(zone, watch_entity, seconds)
            except Exception:  # noqa: BLE001 — one zone must not sink the rest
                # A batch zone's master hold has exactly one release: its run
                # finalising. A zone whose record never landed has no run, so
                # nothing will ever take its hold down and the pump stays on for
                # good. _batch_record_run awaits three store writes, and a failure
                # part-way can still leave a persisted run behind — so ask whether
                # this zone actually has one rather than assuming from the raise,
                # or a zone that WILL finalise gets its hold dropped twice.
                #
                # The plan already reached the controller, so this zone is very
                # likely watering with nothing tracking it. Dropping the hold can
                # cut the pump under it, which is the lesser of the two: an
                # untracked run is bounded by the controller's own timer, a stuck
                # pump by nothing at all.
                if await self._sc_find_run(zone_id) is None:
                    await self.async_master_release(self._sc_master_token(zone_id))
                    self._set_zone_fault(zone_id, const.PROBLEM_BATCH_RUN_NOT_RECORDED)
                    self._fire_zone_problem(
                        zone_id,
                        zone,
                        watch_entity,
                        const.PROBLEM_BATCH_RUN_NOT_RECORDED,
                    )
                _LOGGER.exception(
                    "Batch irrigation: zone %s was handed to the controller but "
                    "its run could not be recorded; it is watering untracked",
                    zone_id,
                )
                # And on to the next zone: the rest of the plan is watering too,
                # and abandoning them here would leak exactly the holds this
                # branch exists to prevent.
                continue

        await self._batch_subscribe_paused()
        _LOGGER.info(
            "Batch irrigation: handed %s zone(s) to %s as one queue",
            len(plan),
            run_service,
        )

    async def _batch_record_run(self, zone: dict, watch_entity: str, seconds: float):
        """Credit, persist and start observing one zone of a dispatched batch."""
        zone_id = zone.get(const.ZONE_ID)

        # Observed-watering (opt-in) may watch this same valve. Mark the window as
        # SI-driven so the observer does not also credit it as an external run.
        # Re-taken at the observed start for the real window, since the one taken
        # here is measured from dispatch and a queued zone's water may be hours
        # away.
        self._note_si_valve(int(zone_id), seconds)

        volume_l = self._timed_volume_l(zone, seconds)
        depth = self._credited_depth_native(zone, volume_l)
        pre_bucket = float(zone.get(const.ZONE_BUCKET) or 0)
        # Clamp at the RUN's ceiling, not at maximum_bucket: a timed duration is
        # lead_time + water_time but the credit prices the whole open window, so
        # every timed run over-credits by the lead time's flow and relies on the
        # target to absorb it — exactly as _run_valve_metered does. maximum_bucket
        # is the live-estimate surplus allowance, which _run_ceiling still returns
        # for a live-estimate run. See tests/test_credit_ceiling.py (issue #88).
        # Captured, not just applied: _run_ceiling consumes the live-estimate
        # marker, so the finish paths read it back off the run record instead of
        # re-deriving one (run_credit_ceiling).
        ceiling = self._run_ceiling(zone)
        new_bucket = min(ceiling, pre_bucket + depth)
        await self.async_write_watered_bucket(zone_id, new_bucket)

        await self._sc_add_run(
            {
                const.RUN_ZONE_ID: zone_id,
                const.RUN_ENTITY_ID: watch_entity,
                const.RUN_STARTED: dt_util.utcnow().isoformat(),
                const.RUN_PLANNED_SECONDS: seconds,
                const.RUN_PLANNED_MM: depth,
                const.RUN_PRE_BUCKET: pre_bucket,
                const.RUN_CEILING: ceiling,
                const.RUN_MODE: const.WATERING_MODE_BATCH,
                const.RUN_CREDITED: True,
                const.RUN_WATCH_ENTITY: watch_entity,
            }
        )
        self._sc_fire(
            const.EVENT_IRRIGATE_STARTED,
            {
                "zones": [
                    {
                        "zone_id": zone_id,
                        "zone": zone.get(const.ZONE_NAME),
                        "seconds": int(seconds),
                    }
                ],
            },
        )
        # The valve switch drives the rest: the observed start, the pause and
        # resume, the finish, and giving up on a zone the controller never reaches.
        await self._watch_start(zone_id, watch_entity, seconds, accepted=True)

    # --- pause --------------------------------------------------------------

    def _batch_pause_timers(self) -> dict:
        """Lazy {zone_id: cancel_cb} of pending pause bounds."""
        timers = getattr(self, "_batch_pause_handles", None)
        if timers is None:
            timers = self._batch_pause_handles = {}
        return timers

    def _batch_cancel_pause_timer(self, zone_id) -> None:
        cancel = self._batch_pause_timers().pop(int(zone_id), None)
        if cancel is not None:
            cancel()

    async def _watch_paused(self, zone_id, run: dict) -> bool:
        """True while the controller reports the irrigation paused.

        Gated on the RUN's mode rather than the zone's: the run carries the mode
        it was dispatched under and is still right when the zone has since been
        edited or deleted.

        An indicator that carries NO INFORMATION reads as paused, not as
        running. This is the same rule ``_watch_evaluate`` already applies to the
        watch entity — never mistake "cannot see the controller" for a state
        change — and it was missing here, which is what a restart mid-pause
        walked straight into (issue #88, reported from the field against
        v2026.08.13). The indicator is unavailable for as long as its controller
        takes to reconnect, and reading that as "not paused" settled the run,
        reversed its credit, and left nothing watching the valve for the water
        the controller then went on to deliver.

        Answering "paused" is the recoverable direction and is not open-ended:
        the moment the indicator publishes anything the subscription re-evaluates
        the run against it (``_batch_reevaluate_runs``), and a pause that never
        resolves is ended by its bound like any other. A run wrongly settled has
        no such second chance.
        """
        if run.get(const.RUN_MODE) != const.WATERING_MODE_BATCH:
            return await super()._watch_paused(zone_id, run)
        entity = self._batch_paused_entity_sync()
        if not entity:
            return False
        state = self.hass.states.get(entity)
        if state is None or state.state in NO_INFO_STATES:
            _LOGGER.debug(
                "Zone %s: the paused indicator %s is not reporting, so the run "
                "is held open as paused rather than settled",
                zone_id,
                entity,
            )
            return True
        return state.state in RUNNING_STATES

    async def _watch_finish_delay(self, zone_id, run: dict) -> float:
        """Hold a valve-off open briefly, but only when a pause is possible.

        With no paused indicator configured there is nothing that could arrive
        late, so the run finishes on the transition exactly as the other modes do
        and no user waits five seconds for a stop they can see.
        """
        if run.get(const.RUN_MODE) != const.WATERING_MODE_BATCH:
            return await super()._watch_finish_delay(zone_id, run)
        if not self._batch_paused_entity_sync():
            return 0.0
        return const.BATCH_PAUSE_SETTLE_SECONDS

    async def _watch_pause_started(self, zone_id, run: dict, watered: float) -> None:
        """Bound the pause.

        A pause EXTENDS the give-up deadline rather than removing it. The
        original deadline was cancelled when the run was observed to start, so
        this timer is what keeps a paused run from becoming an endless one — see
        ``const.BATCH_PAUSE_BACKSTOP_SECONDS`` for why unbounded is not an option
        even though the controller tolerates it.
        """
        if run.get(const.RUN_MODE) != const.WATERING_MODE_BATCH:
            return await super()._watch_pause_started(zone_id, run, watered)
        zid = int(zone_id)
        self._batch_cancel_pause_timer(zid)
        # A pause stops the whole queue, not just the zone that was watering.
        await self._batch_freeze_queued_deadlines(True)
        config = await self._batch_config()
        try:
            timeout = float(config.get(const.CONF_BATCH_PAUSE_TIMEOUT) or 0)
        except (TypeError, ValueError):
            timeout = 0.0
        if timeout <= 0:
            timeout = const.BATCH_PAUSE_BACKSTOP_SECONDS
            _LOGGER.debug(
                "Zone %s paused with no configured pause timeout; using the "
                "%.0fs backstop",
                zid,
                timeout,
            )

        async def _expired(_now):
            await self._batch_pause_expired(zid)

        self._batch_pause_timers()[zid] = async_call_later(self.hass, timeout, _expired)

    async def _watch_pause_ended(self, zone_id, run: dict) -> None:
        """The pause ended within its bound; drop the bound."""
        if run.get(const.RUN_MODE) != const.WATERING_MODE_BATCH:
            return await super()._watch_pause_ended(zone_id, run)
        self._batch_cancel_pause_timer(zone_id)
        await self._batch_freeze_queued_deadlines(False)

    async def _batch_freeze_queued_deadlines(self, frozen: bool) -> None:
        """Stop (or restart) the give-up clock of every zone still queued.

        A queued run's only backstop is a deadline derived from the watering time
        of the zones ahead of it (``queue_deadline_seconds``). That budget is
        spent in wall-clock time, and it assumes the controller is spending that
        time watering — which is exactly what a PAUSE suspends.

        So an ordinary in-bounds pause used to write off every zone behind it:
        the runs were dropped, their optimistic bucket credit reversed and a
        ``zone_never_ran`` fault raised, and then the controller resumed and
        watered them with nothing left watching the valve. The user sees a zone
        water for precisely the duration Irrigation Plus asked for, and a bucket
        that never moves. Reported from the field against v2026.08.14 (#88).

        Applied to queue-bound runs only: a run that has started watering is
        bounded by its own finish backstop and, while paused, by the pause bound,
        and neither of those is a give-up timer. Every exit from a pause restarts
        these — a resume, and the pause outliving its bound — so a suspension
        cannot outlast the pause that caused it.
        """
        for run in await self._sc_active_runs():
            if not isinstance(run, dict):
                continue
            if run.get(const.RUN_MODE) != const.WATERING_MODE_BATCH:
                continue
            if not run_is_queue_bound(run):
                continue
            zone_id = run.get(const.RUN_ZONE_ID)
            if zone_id is None:
                continue
            if frozen:
                if self._watch_suspend_timer(zone_id):
                    _LOGGER.debug(
                        "Zone %s: the controller is paused, so its wait for the "
                        "queue is not counting down",
                        zone_id,
                    )
            elif self._watch_resume_timer(zone_id):
                _LOGGER.debug(
                    "Zone %s: the controller resumed; its wait for the queue is "
                    "counting down again",
                    zone_id,
                )

    async def _batch_pause_expired(self, zone_id) -> None:
        """A pause outlived its bound: hand over, then settle for what was given."""
        zid = int(zone_id)
        self._batch_pause_timers().pop(zid, None)
        run = await self._sc_find_run(zid)
        if run is None:
            return
        config = await self._batch_config()
        handler = config.get(const.CONF_BATCH_PAUSE_TIMEOUT_SERVICE)
        if handler:
            # The user decides what giving up means on their hardware — resume,
            # shut down, clear the queue. Best-effort: their script failing must
            # not stop the run being settled, or the bookkeeping this bound exists
            # to protect stays broken anyway.
            domain, service = self._sc_split_service(handler)
            try:
                await self.hass.services.async_call(domain, service, {"zone_id": zid})
            except Exception:  # noqa: BLE001 - the settle below matters more
                _LOGGER.exception(
                    "Zone %s: the pause-timeout service %s failed", zid, handler
                )
        _LOGGER.warning(
            "Zone %s: the controller stayed paused past its bound; the run is "
            "settled for the %.0fs it actually delivered",
            zid,
            self._sc_run_elapsed(run),
        )
        await self.async_stop_self_closing(
            zid, close_valve=False, detail=const.RUN_DETAIL_BATCH_PAUSE_TIMEOUT
        )
        # The pause is over as far as this integration is concerned, however it
        # ended. Restart the queued zones' clocks or a suspension taken at the
        # start of the pause would outlive it and hold them indefinitely.
        await self._batch_freeze_queued_deadlines(False)

    async def _batch_subscribe_paused(self) -> None:
        """Subscribe to the paused indicator, once, while batch runs are live."""
        entity = self._batch_paused_entity_sync()
        if not entity:
            return
        current = getattr(self, "_batch_paused_watch", None)
        if current is not None and current[0] == entity:
            return
        self._batch_unsubscribe_paused()
        unsub = async_track_state_change_event(
            self.hass, [entity], self._batch_paused_changed
        )
        self._batch_paused_watch = (entity, unsub)

    def _batch_unsubscribe_paused(self) -> None:
        current = getattr(self, "_batch_paused_watch", None)
        if current is not None:
            current[1]()
            self._batch_paused_watch = None

    @callback
    def _batch_paused_changed(self, event) -> None:
        """The controller's paused indicator moved."""
        self.hass.async_create_task(self._batch_reevaluate_runs())

    async def _batch_reevaluate_runs(self) -> None:
        """Re-read every in-flight batch run against its valve's current state.

        Deliberately routed back through the shared engine rather than deciding
        here. ``_watch_evaluate`` already knows every combination of (valve on or
        off) x (paused or not) x (segment open or not), and re-deriving that
        second time is how the two would drift apart:

        * paused and the valve off  -> pause, bank the segment, bound the pause
        * unpaused and the valve on -> resume, open the next segment
        * unpaused and the valve off -> the controller ended the run, so settle it
        """
        for run in await self._sc_active_runs():
            if not isinstance(run, dict):
                continue
            if run.get(const.RUN_MODE) != const.WATERING_MODE_BATCH:
                continue
            zone_id = run.get(const.RUN_ZONE_ID)
            entity = run.get(const.RUN_WATCH_ENTITY)
            if zone_id is None or not entity:
                continue
            await self._watch_evaluate(zone_id, self.hass.states.get(entity))

    # --- stopping -----------------------------------------------------------

    async def _batch_dispatch_stop(self) -> bool:
        """Fire the user's stop-and-clear-the-queue script. True if it was sent."""
        config = await self._batch_config()
        stop_service = config.get(const.CONF_BATCH_STOP_SERVICE)
        if not stop_service:
            _LOGGER.warning(
                "Batch mode: no batch stop service is configured, so the "
                "controller cannot be stopped and its queue cannot be cleared. "
                "The accounting is corrected, but any zone still queued will "
                "water unsupervised"
            )
            return False
        domain, service = self._sc_split_service(stop_service)
        await self.hass.services.async_call(domain, service, {})
        return True

    async def async_stop_batch(self, zone_id=None, *, detail: str | None = None) -> int:
        """Stop the batch cycle and settle every run it had in flight.

        Stopping is not a per-zone action on this hardware and pretending
        otherwise would be worse than admitting it: stopping one zone ends the
        cycle, and the zones still queued behind it stay queued. So the stop
        script clears the queue, and every in-flight run is settled here — a run
        left open would hold its zone and its share of the pump for a cycle that
        is no longer running.

        ``zone_id`` is only used to order the settling, so the zone the user
        actually pressed Stop on is dealt with first.
        """
        await self._batch_dispatch_stop()
        runs = [
            r
            for r in await self._sc_active_runs()
            if isinstance(r, dict)
            and r.get(const.RUN_MODE) == const.WATERING_MODE_BATCH
        ]
        targets = [r.get(const.RUN_ZONE_ID) for r in runs]
        targets = [z for z in targets if z is not None]
        # The zone the user actually pressed Stop on settles first, so the run
        # they were looking at is the one that clears immediately.
        order = sorted(targets, key=lambda z: zone_id is None or int(z) != int(zone_id))
        stopped = 0
        for zid in order:
            self._batch_cancel_pause_timer(zid)
            try:
                # close_valve=False: the stop script above has already dealt with
                # the hardware for the whole cycle, and this mode has no per-zone
                # close to send.
                if await self.async_stop_self_closing(
                    zid, close_valve=False, detail=detail
                ):
                    stopped += 1
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Zone %s: could not settle its batch run", zid)
        self._batch_unsubscribe_paused()
        return stopped

    async def async_abort_batch_runs(self, reason: str, *, settle=True) -> bool:
        """Stop the controller on teardown, and settle what was in flight.

        The same requirement #85 established for OpenSprinkler, and it is sharper
        here: the controller keeps its queue across a stop, so teardown that only
        drops the watchers leaves both the running zone AND every zone still
        queued to water with nothing supervising them.

        Deliberately NOT called on a plain reload or restart — those re-adopt the
        runs seconds later through ``_batch_resume_run``.
        """
        runs = [
            r
            for r in await self._sc_active_runs()
            if isinstance(r, dict)
            and r.get(const.RUN_MODE) == const.WATERING_MODE_BATCH
        ]
        if not runs:
            return False
        _LOGGER.warning(
            "Batch mode: stopping the controller and clearing its queue (%s)", reason
        )
        if settle:
            await self.async_stop_batch()
        else:
            await self._batch_dispatch_stop()
            self._batch_unsubscribe_paused()
        return True

    def async_teardown_batch_watchers(self) -> None:
        """Drop the paused subscription and every pending pause bound."""
        self._batch_unsubscribe_paused()
        for zone_id in list(self._batch_pause_timers()):
            self._batch_cancel_pause_timer(zone_id)

    # --- restart ------------------------------------------------------------

    async def _batch_resume_run(self, run: dict) -> None:
        """Re-adopt one persisted batch run after a restart.

        Never re-dispatches, for the same reason the OpenSprinkler mode does not:
        the controller owns both the queue and the valve, so an interrupted run is
        either still queued, still watering, paused, or gone — and every one of
        those is an observation rather than an action. Re-sending the plan would
        queue the whole irrigation a second time.
        """
        zone_id = run.get(const.RUN_ZONE_ID)
        planned = planned_seconds(run)
        watch_entity = run.get(const.RUN_WATCH_ENTITY)
        if not watch_entity:
            zone = self.store.get_zone(zone_id) or {}
            watch_entity = batch_watch_entity(zone)
        if not watch_entity:
            await self._watch_give_up(zone_id, const.PROBLEM_BATCH_NO_WATCH_ENTITY)
            return

        # Master holds lived in memory only, so the restart dropped them. Re-take
        # for whatever is left of this run.
        await self.async_master_acquire(self._sc_master_token(zone_id))
        await self._batch_subscribe_paused()

        if run.get(const.RUN_OBSERVED_START) is None:
            # Still waiting its turn in the queue, as far as anything here knows.
            # The deadline restarts from now rather than from dispatch: the
            # controller's own integration may not have finished loading, and its
            # valve would then read as off purely because nothing has published it.
            await self._watch_start(zone_id, watch_entity, planned, accepted=True)
            return

        # A segment left open across the restart is kept open, deliberately. It
        # records that this zone was watering when Home Assistant lost sight of
        # it, and the hardware owns the close — so the water very probably kept
        # flowing, exactly as the other self-closing modes assume. Discarding the
        # segment would under-credit every ordinary restart.
        #
        # What makes that safe is the other half of the model: a PAUSE closes the
        # segment before it starts, so a pause spanning an outage accrues
        # nothing. The open-segment case is the one where watering really was in
        # progress, and it is bounded anyway — a run can never be credited for
        # more than its planned window.
        if self._sc_run_elapsed(run) >= planned:
            await self._sc_finish_run(zone_id)
            return

        await self._watch_start(zone_id, watch_entity, planned, accepted=True)
