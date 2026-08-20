"""Observe a run that hardware owns: when it starts watering, and when it stops.

Some watering modes hand the run to a controller that owns both the queue and
the valve. Nothing about such a run may be measured from the moment it was
dispatched — a queued zone would finalise, credit its usage and release its
accounting long before its water flowed. The run is driven by an entity that is
on while that zone is actually watering, and the dispatch time is used for
exactly one thing: deciding when to give up waiting.

That lifecycle was written for OpenSprinkler stations (v2026.08.06) and is
almost entirely generic. This module is the generic part; a mode supplies the
handful of things that really differ as a :class:`WatchPolicy`:

* how the controller *acknowledges* a run it has queued, if it does at all;
* what timestamp to record as the moment watering began;
* how long to wait before writing the run off.

``OpenSprinklerMixin`` keeps its ``_os_*`` spellings as delegates onto this
engine, so its behaviour is unchanged and its tests remain the oracle for that.

Extracted for issue #88 (batch/queue dispatch), whose mode needs the same
observation lifecycle with a different dispatch and a different watch entity.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.core import Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util

from . import const

_LOGGER = logging.getLogger(__name__)

# States that carry no attributes: HA drops an entity's extra_state_attributes
# while it is unavailable, so an acknowledgement reads as absent rather than as
# withdrawn. Never mistake "cannot see the controller" for "the controller
# dropped the run" — the first is transient, the second finalises the run.
NO_INFO_STATES = ("unavailable", "unknown")
# The watch entity is a binary_sensor / switch / valve; these are its "watering"
# states.
RUNNING_STATES = ("on", "open", "opening")
# The modes whose runs sit in a controller's QUEUE between dispatch and water.
# For these, and only these, RUN_STARTED bounds nothing: a zone behind three
# others opens hours after it was dispatched, so anything measured from dispatch
# would finalise a run that has not started. Every other mode opens its valve as
# it dispatches, so the two instants coincide.
QUEUE_BOUND_MODES = (
    const.WATERING_MODE_OPENSPRINKLER,
    const.WATERING_MODE_BATCH,
)


def run_is_queue_bound(run: dict) -> bool:
    """True while a run is still waiting its turn in a controller's queue."""
    return (
        isinstance(run, dict)
        and run.get(const.RUN_OBSERVED_START) is None
        and run.get(const.RUN_MODE) in QUEUE_BOUND_MODES
    )


def run_is_segmented(run: dict) -> bool:
    """True if this run records its watering as segments rather than a stretch.

    The same test ``_sc_run_elapsed`` uses to decide which timing a run gets,
    named once so the panel's countdown cannot answer it differently from the
    accounting — which is exactly how the two came apart (issue #88): the
    accounting summed the segments while the countdown still ran from the
    observed start, so a pause was displayed as if it were water.

    Keyed on the record carrying the fields rather than on the mode, so a run
    dispatched before this mode existed, or under a mode this build no longer
    knows, is timed the way it was actually recorded.
    """
    return isinstance(run, dict) and (
        const.RUN_WATERED_SECONDS in run
        or run.get(const.RUN_SEGMENT_STARTED) is not None
    )


def run_is_paused(run: dict) -> bool:
    """True while this run's controller is holding it PAUSED.

    A segmented run that has started watering but has no segment open is, by
    definition of the segment model, not watering right now — and the only way
    a started run stops without ending is a pause (``_watch_pause`` closes the
    segment; ``_watch_resume`` opens the next one).

    Derived from the record rather than re-read from the paused indicator on
    purpose. The indicator answers "is the CONTROLLER paused", which is one
    answer for the whole queue, while this answers "is THIS zone's water on
    hold" — and those differ for every zone the controller has not reached yet.
    A queued zone is not paused, it is queued, and reading the indicator would
    label all of them paused the moment the controller pauses.
    """
    return (
        run_is_segmented(run)
        and run.get(const.RUN_OBSERVED_START) is not None
        and not run.get(const.RUN_SEGMENT_STARTED)
    )


@dataclass
class Watcher:
    """One zone's live subscription, plus at most one pending timer.

    ``accepted`` is the reconciliation state: for a mode whose controller
    acknowledges its queue it starts False, and once the acknowledgement has
    been seen its withdrawal means the run was dropped. A mode that has no
    acknowledgement signal starts accepted (see ``WatchPolicy.acknowledges``).
    """

    entity: str
    accepted: bool = False
    unsub: object | None = None
    cancel: object | None = None
    # A pending "the valve went off — is this a pause or the end?" timer, kept
    # apart from ``cancel`` because that one arms giving up on a run that never
    # watered, and the two can never be confused for one another safely.
    finish_cancel: object | None = None
    # When ``cancel`` is due to fire, and what it would raise. Kept so the
    # give-up clock can be STOPPED and restarted with the time it had left
    # rather than a fresh full deadline — see ``_watch_suspend_timer``.
    deadline_at: object | None = None
    deadline_reason: str | None = None
    deadline_left: float | None = None


@dataclass(frozen=True)
class WatchPolicy:
    """What one watering mode contributes to the shared observation lifecycle.

    ``acknowledges`` says whether the controller reports having taken the run on
    before it runs it. OpenSprinkler does, via a non-zero program id on the
    station, and that is what distinguishes "queued behind four other zones"
    from "silently discarded". A controller handed a whole queue in one call has
    accepted it by the time the call returns and has no such signal, so the run
    starts accepted and the give-up deadline is the only backstop.

    ``give_up_problem`` is the fault code raised against a zone whose run never
    watered.
    """

    mode: str
    acknowledges: bool = False
    give_up_problem: str = const.PROBLEM_STATION_NEVER_RAN
    # Seconds to allow for an acknowledgement before writing the run off.
    accept_seconds: float = const.OPENSPRINKLER_ACCEPT_SECONDS
    # Whether a freshly armed watcher waits the whole queue-derived deadline
    # instead of ``accept_seconds``. An acknowledging mode uses the short grace
    # first and re-arms to the long one once the controller has answered; a mode
    # with no acknowledgement has nothing to wait for, so its only backstop must
    # be long enough to cover the zones queued ahead of this one.
    queue_deadline_at_start: bool = False
    # Whether this mode's controller can PAUSE a run — turning the valve off
    # while keeping the remaining time — so the run has to be timed as the sum of
    # its watering segments rather than as one stretch from the observed start.
    # See const.RUN_WATERED_SECONDS. Off for every mode that cannot pause, which
    # keeps their runs on the contiguous timing they were written with.
    segmented: bool = False
    # Whether a watcher armed for a run that ALREADY has an observed start still
    # arms the give-up timer.
    #
    # It should not: the give-up timer exists to end a run that never watered,
    # and a run with an observed start has watered. Only ``_watch_observed_start``
    # cancels it, and that is skipped on this path, so nothing takes it back down
    # — a resumed run with more time left than the deadline is written off while
    # its valve is still open, its credit reversed and a fault raised.
    #
    # It defaults to True regardless, because that is what the OpenSprinkler mode
    # did before this engine was extracted from it and its timing is deliberately
    # preserved byte-for-byte (the defect is real, reproduced against the
    # pre-extraction code, and is being fixed separately rather than smuggled in
    # here). A mode written after the extraction should set this False.
    arm_give_up_after_start: bool = True


def is_acknowledged(state) -> bool:
    """True if this observation carries a controller acknowledgement.

    OpenSprinkler's is a non-zero program id on the station. Kept here rather
    than as a policy callable because it is the only acknowledgement shape any
    mode currently has, and a mode that does not acknowledge never asks.
    """
    return bool(state.attributes.get(const.OPENSPRINKLER_ATTR_PROGRAM_ID))


def planned_seconds(run: dict) -> float:
    """The run's planned window, clamped non-negative, never raising."""
    try:
        return max(0.0, float(run.get(const.RUN_PLANNED_SECONDS) or 0))
    except (TypeError, ValueError):
        return 0.0


def queue_deadline_seconds(runs: list, run: dict, *, mode: str | None = None) -> float:
    """Seconds after dispatch at which a run that never watered is written off.

    Derived rather than fixed, because what a queued run waits for is the runs
    ahead of it: a four-zone cycle on real deficits is around 288 minutes and a
    seven-zone one considerably longer, so any single constant is either far too
    short for a full cycle or far too long for one zone. The margin absorbs the
    controller's own inter-zone delays.

    This is only a backstop. A run a controller explicitly drops is seen within
    a poll; this bound is what ends a run whose watch entity stopped reporting
    altogether.

    ``mode`` defaults to the run's own, so the zones counted as "ahead" are the
    ones sharing its controller rather than every in-flight run.
    """
    planned = planned_seconds(run)
    want_mode = mode if mode is not None else run.get(const.RUN_MODE)
    ahead = 0.0
    for other in runs or []:
        if not isinstance(other, dict) or other is run:
            continue
        if other.get(const.RUN_MODE) != want_mode:
            continue
        if other.get(const.RUN_ZONE_ID) == run.get(const.RUN_ZONE_ID):
            continue
        ahead += planned_seconds(other)
    return (
        const.OPENSPRINKLER_ACCEPT_SECONDS
        + ahead
        + planned
        + const.OPENSPRINKLER_QUEUE_MARGIN_SECONDS
    )


class RunWatchMixin:
    """Observe hardware-owned runs. Mixed into SmartIrrigationCoordinator.

    Reuses ``SelfClosingMixin``'s persisted run record, optimistic bucket credit
    and restart contract wholesale; this adds only the part that decides *when*
    a run started and ended.
    """

    # --- registry -----------------------------------------------------------

    def _watchers(self) -> dict:
        """Lazy {zone_id: Watcher} of live subscriptions.

        A watcher owns a state subscription and at most one timer, and is the
        only thing that ends a queued run — so it must be re-created on restart
        for every persisted record or that record would block its zone until the
        deadline in the persisted list expires.
        """
        watchers = getattr(self, "_run_watchers", None)
        if watchers is None:
            watchers = self._run_watchers = {}
        return watchers

    def _watch_cancel(self, zone_id) -> None:
        """Cancel-and-pop a zone's subscription and timer (no-op if absent)."""
        watcher = self._watchers().pop(int(zone_id), None)
        if watcher is None:
            return
        unsub = watcher.unsub
        if unsub is not None:
            unsub()
        cancel = watcher.cancel
        if cancel is not None:
            cancel()
        finish_cancel = watcher.finish_cancel
        if finish_cancel is not None:
            finish_cancel()

    def _watch_arm_timer(self, zone_id, delay: float, reason: str) -> None:
        """(Re)arm the watcher's single timer."""
        watcher = self._watchers().get(int(zone_id))
        if watcher is None:
            return
        cancel = watcher.cancel
        if cancel is not None:
            cancel()

        async def _expired(_now):
            await self._watch_give_up(zone_id, reason)

        delay = max(0.0, delay)
        watcher.cancel = async_call_later(self.hass, delay, _expired)
        watcher.deadline_at = dt_util.utcnow() + timedelta(seconds=delay)
        watcher.deadline_reason = reason
        watcher.deadline_left = None

    def _watch_suspend_timer(self, zone_id) -> bool:
        """Stop the give-up clock, keeping the time it had left.

        The give-up timer measures how long a run may wait for its controller to
        reach it. That is wall-clock time only while the controller is actually
        working through its queue — a controller that has PAUSED is not making
        progress, so every zone still queued behind the pause is being charged
        for time in which its turn could not possibly have come.

        Left running, an ordinary in-bounds pause writes those zones off: the
        run is dropped, its optimistic bucket credit reversed and a fault raised,
        and then the controller resumes and waters them with nothing supervising
        the valve — so the water is delivered and never credited. Reported from
        the field against v2026.08.14 (issue #88).

        Stops the clock rather than extending the deadline, so a run cannot be
        held open longer than the pauses it actually sat through. Returns True if
        a timer was suspended.
        """
        watcher = self._watchers().get(int(zone_id))
        if watcher is None or watcher.cancel is None:
            return False
        watcher.cancel()
        watcher.cancel = None
        deadline = watcher.deadline_at
        if deadline is None:
            watcher.deadline_left = None
            return True
        watcher.deadline_left = max(0.0, (deadline - dt_util.utcnow()).total_seconds())
        return True

    def _watch_resume_timer(self, zone_id) -> bool:
        """Restart a suspended give-up clock with the time it had left.

        A no-op when the timer was never suspended, so a resume that arrives
        without a matching pause cannot hand a run a second full deadline.
        """
        watcher = self._watchers().get(int(zone_id))
        if watcher is None or watcher.cancel is not None:
            return False
        left = watcher.deadline_left
        if left is None or watcher.deadline_reason is None:
            return False
        self._watch_arm_timer(zone_id, left, watcher.deadline_reason)
        return True

    # --- policy -------------------------------------------------------------

    def _watch_policy(self, zone_id, run: dict | None = None) -> WatchPolicy:
        """The policy for whatever mode this zone's in-flight run belongs to.

        Resolved from the RUN record first, and only then from the zone. The run
        carries the mode it was dispatched under, survives a restart, and is
        still there when the zone has been deleted or edited mid-run — all three
        cases where the zone's current mode is either absent or no longer the one
        the hardware is acting on.
        """
        if isinstance(run, dict) and run.get(const.RUN_MODE):
            return watch_policy_for(run.get(const.RUN_MODE))
        zone = self.store.get_zone(int(zone_id)) or {}
        return watch_policy_for(zone.get(const.ZONE_WATERING_MODE))

    # --- persisted run edits + watering segments -----------------------------

    async def _watch_update_run(self, zone_id, changes: dict) -> dict | None:
        """Apply ``changes`` to one zone's persisted run record.

        Re-reads the list rather than editing a caller's copy, because the record
        is persisted config and several paths hold stale copies of it. Returns
        the updated record, or None if the run has already been finalised.
        """
        zid = int(zone_id)
        runs = await self._sc_active_runs()
        updated = None
        out = []
        for r in runs:
            if isinstance(r, dict) and r.get(const.RUN_ZONE_ID) == zid:
                updated = {**r, **changes}
                out.append(updated)
            else:
                out.append(r)
        if updated is None:
            return None
        await self._sc_persist_runs(out)
        return updated

    async def _watch_segment_open(self, zone_id, run: dict | None = None) -> None:
        """Start a watering segment (the run began, or resumed after a pause)."""
        await self._watch_update_run(
            zone_id, {const.RUN_SEGMENT_STARTED: dt_util.utcnow().isoformat()}
        )

    async def _watch_segment_close(self, zone_id) -> float:
        """Close the open watering segment, folding it into the accumulator.

        Returns the run's total watered seconds afterwards. A no-op returning the
        existing total when no segment is open, so a duplicate pause observation
        (HA can replay a state change) cannot bank the same seconds twice.
        """
        zid = int(zone_id)
        run = await self._sc_find_run(zid)
        if run is None:
            return 0.0
        try:
            total = float(run.get(const.RUN_WATERED_SECONDS) or 0)
        except (TypeError, ValueError):
            total = 0.0
        segment = run.get(const.RUN_SEGMENT_STARTED)
        if not segment:
            return total
        total += self._sc_elapsed(segment)
        await self._watch_update_run(
            zid,
            {
                const.RUN_WATERED_SECONDS: total,
                const.RUN_SEGMENT_STARTED: None,
            },
        )
        return total

    async def _watch_paused(self, zone_id, run: dict) -> bool:
        """True while this run's controller is paused.

        A paused controller turns the valve off and keeps the remaining time, so
        the valve going off must not be read as the end of the run. The default
        is False — a mode with no pause concept never asks the question.
        """
        return False

    async def _watch_observed_start_iso(self, zone_id, run: dict, entity: str) -> str:
        """When watering began, ISO-8601 UTC, for RUN_OBSERVED_START.

        The default is the moment the observation arrived. OpenSprinkler
        overrides this to prefer the controller's own reported start.
        """
        return dt_util.utcnow().isoformat()

    # --- lifecycle ----------------------------------------------------------

    async def _watch_start(
        self, zone_id, watch_entity: str, planned: float, *, accepted: bool
    ) -> None:
        """Watch an entity for a zone's run start and end.

        ``accepted`` seeds the reconciliation state: False right after dispatch
        for a mode whose controller acknowledges separately, True when resuming
        a record whose zone is already reporting a run, and True from the start
        for a mode with no acknowledgement signal.
        """
        zid = int(zone_id)
        self._watch_cancel(zid)
        watcher = Watcher(entity=watch_entity, accepted=bool(accepted))
        self._watchers()[zid] = watcher
        watcher.unsub = async_track_state_change_event(
            self.hass, [watch_entity], self._watch_state_changed
        )
        run = await self._sc_find_run(zid)
        policy = self._watch_policy(zid, run)
        # Deliberately keyed on the POLICY, not on ``accepted``. An acknowledging
        # mode arms the short grace here in both cases, including the resume path
        # — preserving the behaviour this engine was extracted from; see the
        # note on ``queue_deadline_at_start``.
        already_watering = (run or {}).get(const.RUN_OBSERVED_START) is not None
        if already_watering and not policy.arm_give_up_after_start:
            # Nothing to give up on — this run has watered. It is bounded by the
            # cosmetic-finish backstop (and, while paused, by the pause bound).
            pass
        elif policy.queue_deadline_at_start:
            runs = await self._sc_active_runs()
            self._watch_arm_timer(
                zid,
                queue_deadline_seconds(runs, run or {}, mode=policy.mode),
                policy.give_up_problem,
            )
        else:
            self._watch_arm_timer(zid, policy.accept_seconds, policy.give_up_problem)
        # The zone's own running sensor and the observed-watering map both derive
        # this same entity, and both may have been built before the controller
        # published it. Nudge them now that it is known to resolve.
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zid)
        # The controller may already have the run queued (or even running, on an
        # empty queue) before the subscription above exists. Evaluate the current
        # state once so that run is not missed entirely.
        await self._watch_evaluate(zid, self.hass.states.get(watch_entity))

    @callback
    def _watch_state_changed(self, event: Event) -> None:
        """A watched entity changed state."""
        entity_id = event.data.get("entity_id")
        for zone_id, watcher in list(self._watchers().items()):
            if watcher.entity != entity_id:
                continue
            self.hass.async_create_task(
                self._watch_evaluate(zone_id, event.data.get("new_state"))
            )

    async def _watch_evaluate(self, zone_id, state) -> None:
        """Advance a watched run from one observation of its entity."""
        zid = int(zone_id)
        watcher = self._watchers().get(zid)
        if watcher is None:
            return
        run = await self._sc_find_run(zid)
        if run is None:
            # The run was finalised by another path (a user stop, a restart
            # reconcile). Nothing left to observe.
            self._watch_cancel(zid)
            return

        if state is None or state.state in NO_INFO_STATES:
            # No information: the controller is unreachable or the entity has not
            # been created yet. Never read this as "the run was dropped" — the
            # deadline timer is what ends a run whose entity stops reporting.
            return

        running = state.state in RUNNING_STATES
        observed_start = run.get(const.RUN_OBSERVED_START)
        policy = self._watch_policy(zid, run)

        if running:
            if observed_start is None:
                await self._watch_observed_start(zid, run)
            elif policy.segmented and run.get(const.RUN_SEGMENT_STARTED) is None:
                # Watering again after a pause: open the next segment.
                await self._watch_resume(zid, run)
            return

        if observed_start is not None:
            if await self._watch_paused(zid, run):
                # A pause, not the end. The controller is holding the remaining
                # time; bank what has been delivered and wait.
                await self._watch_pause(zid, run)
                return
            # The zone stopped. The controller ended the run, on time or early;
            # either way it is over now — unless this mode's pause indicator may
            # simply not have caught up yet, in which case decide in a moment.
            delay = await self._watch_finish_delay(zid, run)
            if delay > 0:
                await self._watch_defer_finish(zid, run, delay)
            else:
                await self._watch_finish(zid, run)
            return

        if not policy.acknowledges:
            # Nothing to reconcile against: an entity that is simply off is a run
            # still waiting its turn. Only the deadline ends it.
            return

        if not watcher.accepted:
            if is_acknowledged(state):
                # The controller has acknowledged the run. From here on its
                # acknowledgement being withdrawn is meaningful.
                watcher.accepted = True
                runs = await self._sc_active_runs()
                # Measured from this acknowledgement rather than from dispatch.
                # Downtime would otherwise be spent out of the run's budget: an
                # outage longer than the deadline leaves nothing for a zone the
                # controller is still holding, and the run is written off and its
                # credit reversed a second after the resume, for water the
                # controller then goes on to deliver. Acknowledgement is normally
                # within a poll of dispatch, so this is the same bound in
                # ordinary operation.
                self._watch_arm_timer(
                    zid,
                    queue_deadline_seconds(runs, run, mode=policy.mode),
                    policy.give_up_problem,
                )
            return

        if not is_acknowledged(state):
            # Acknowledged, then dropped without ever watering: a controller-side
            # rain delay, a water level of 0, or a stop-all. The zone was credited
            # optimistically at dispatch, so this has to unwind that credit rather
            # than wait the deadline out.
            await self._watch_give_up(zid, policy.give_up_problem)

    async def _watch_observed_start(self, zone_id, run: dict) -> None:
        """Watering began: from here the run is a normal timed run."""
        zid = int(zone_id)
        watcher = self._watchers().get(zid)
        planned = planned_seconds(run)
        zone = self.store.get_zone(zid) or {}

        entity = (watcher.entity if watcher else None) or run.get(
            const.RUN_WATCH_ENTITY
        )
        started = await self._watch_observed_start_iso(zid, run, entity)
        changes = {const.RUN_OBSERVED_START: started}
        if self._watch_policy(zid, run).segmented:
            # Open the first watering segment. Anchored to the same instant as
            # the observed start, so an unpaused run's segment total and its
            # contiguous elapsed agree exactly.
            changes[const.RUN_WATERED_SECONDS] = 0.0
            changes[const.RUN_SEGMENT_STARTED] = started
        await self._watch_update_run(zid, changes)

        # The suppression window taken at dispatch is measured from dispatch, so
        # for a queued run it has already expired — and observed watching is now
        # pointed at this very entity. Re-take it for the real run window so the
        # zone's own run is not also credited as external.
        self._note_si_valve(zid, planned)
        # Flow sampling deliberately starts HERE, not at dispatch: a meter seeded
        # while the zone was still queued would sample a window that mostly
        # precedes the water.
        await self._sc_start_flow_sampling(zone)
        if watcher is not None:
            cancel = watcher.cancel
            if cancel is not None:
                cancel()
            watcher.cancel = None
            # And the clock is not merely stopped, it is gone: this run has
            # watered, so there is no longer anything to give up on. Leaving a
            # suspended deadline behind would let a later resume re-arm a
            # write-off against a run whose valve is open.
            watcher.deadline_at = None
            watcher.deadline_left = None
            watcher.deadline_reason = None
        # Backstop only. The entity going off is the primary finish signal; this
        # covers a missed transition.
        self._sc_schedule_cleanup(zid, planned)
        _LOGGER.info(
            "Zone %s: %s run started watering (planned %.0fs)",
            zid,
            self._watch_policy(zid, run).mode,
            planned,
        )

    # --- pause / resume ------------------------------------------------------

    async def _watch_finish_delay(self, zone_id, run: dict) -> float:
        """Seconds to wait before reading a valve-off as the end of the run.

        Zero for every mode that cannot pause, so their runs finish on the
        transition exactly as before. A mode that CAN pause has a race to settle:
        a pause turns the valve off and raises the paused indicator, and nothing
        orders those two updates. Waiting a moment lets the indicator catch up,
        which is the difference between resuming a run and having settled it as a
        partial with its credit already reversed.
        """
        return 0.0

    async def _watch_pause(self, zone_id, run: dict) -> None:
        """The controller paused: bank the segment, keep everything else."""
        zid = int(zone_id)
        watcher = self._watchers().get(zid)
        if watcher is not None and watcher.finish_cancel is not None:
            # A valve-off already started the "is this the end?" countdown and the
            # indicator has now answered it.
            watcher.finish_cancel()
            watcher.finish_cancel = None
        total = await self._watch_segment_close(zid)
        # The cosmetic-finish backstop was armed for a contiguous window that is
        # no longer running. It is re-armed for the remainder on resume.
        self._sc_cancel_cleanup(zid)
        await self._watch_pause_started(zid, run, total)
        _LOGGER.info(
            "Zone %s: the controller paused it after %.0fs of watering", zid, total
        )

    async def _watch_resume(self, zone_id, run: dict) -> None:
        """The controller resumed: open the next segment, re-arm the backstop."""
        zid = int(zone_id)
        watcher = self._watchers().get(zid)
        if watcher is not None and watcher.finish_cancel is not None:
            watcher.finish_cancel()
            watcher.finish_cancel = None
        # Measured BEFORE the new segment opens, so "delivered so far" is the
        # banked total and not that total plus a few microseconds of the segment
        # this method is about to start.
        remaining = max(0.0, planned_seconds(run) - self._sc_run_elapsed(run))
        await self._watch_segment_open(zid, run)
        # Re-armed for what is LEFT rather than the whole window: the backstop
        # exists to end a run whose off-transition is missed, and anchoring it to
        # the observed start again would push it out by the length of the pause
        # every time.
        self._sc_schedule_cleanup(zid, remaining)
        await self._watch_pause_ended(zid, run)
        _LOGGER.info("Zone %s: the controller resumed it (%.0fs left)", zid, remaining)

    async def _watch_pause_started(self, zone_id, run: dict, watered: float) -> None:
        """Hook: a pause began. Modes bound the pause from here."""
        return None

    async def _watch_pause_ended(self, zone_id, run: dict) -> None:
        """Hook: a pause ended. Modes drop their pause bound from here."""
        return None

    async def _watch_defer_finish(self, zone_id, run: dict, delay: float) -> None:
        """Hold a valve-off open briefly in case it turns out to be a pause.

        The segment is closed immediately — the water has stopped either way, and
        no run may be credited for the interval spent deciding what the stop
        meant.
        """
        zid = int(zone_id)
        await self._watch_segment_close(zid)
        watcher = self._watchers().get(zid)
        if watcher is None:
            return
        if watcher.finish_cancel is not None:
            watcher.finish_cancel()

        async def _decide(_now):
            w = self._watchers().get(zid)
            if w is not None:
                w.finish_cancel = None
            fresh = await self._sc_find_run(zid)
            if fresh is None:
                return
            if await self._watch_paused(zid, fresh):
                # The indicator caught up during the wait; treat it as the pause
                # it was, including the bookkeeping _watch_pause does.
                await self._watch_pause(zid, fresh)
                return
            if fresh.get(const.RUN_SEGMENT_STARTED):
                # It started watering again without ever reporting a pause, so
                # the stop was a blip rather than the end of the run.
                return
            await self._watch_finish(zid, fresh)

        watcher.finish_cancel = async_call_later(self.hass, max(0.0, delay), _decide)

    async def _watch_finish(self, zone_id, run: dict) -> None:
        """Watering stopped. Settle the run against what it actually delivered."""
        zid = int(zone_id)
        self._watch_cancel(zid)
        planned = planned_seconds(run)
        elapsed = self._sc_run_elapsed(run)
        # A zone that ran its full window is a completed run; one the controller
        # cut short settles like an early stop, which reconciles the optimistic
        # credit down to what was delivered. One second of slack keeps a run that
        # ended exactly on time out of the partial path.
        if elapsed + 1 >= planned:
            await self._sc_finish_run(zid)
        else:
            await self.async_stop_self_closing(zid, close_valve=False)

    async def _watch_give_up(self, zone_id, reason: str) -> None:
        """End a run that never watered, and undo its optimistic credit."""
        zid = int(zone_id)
        self._watch_cancel(zid)
        run = await self._sc_find_run(zid)
        if run is None:
            return
        zone = self.store.get_zone(zid) or {}
        # elapsed is 0 for a run with no observed start, so this reconciles the
        # bucket all the way back to RUN_PRE_BUCKET and logs a run that delivered
        # nothing. No stop is sent: the zone never opened, and stopping would only
        # affect whatever the controller is running right now.
        await self.async_stop_self_closing(
            zid, close_valve=False, detail=const.RUN_DETAIL_STATION_NEVER_RAN
        )
        self._set_zone_fault(zid, reason)
        self._fire_zone_problem(zid, zone, zone.get(const.ZONE_LINKED_ENTITY), reason)
        _LOGGER.warning(
            "Zone %s: the controller never watered it (%s); the run was written "
            "off and its bucket credit reversed",
            zid,
            reason,
        )


# Registered by each mode's module at import time, so a mode's policy lives next
# to the mode rather than in a table here that has to be kept in step.
_POLICIES: dict[str, WatchPolicy] = {}
# Conservative on both switches: wait for an acknowledgement rather than assume
# the run is live, and keep the short grace rather than the long queue backstop.
_DEFAULT_POLICY = WatchPolicy(
    mode=const.WATERING_MODE_OPENSPRINKLER,
    acknowledges=True,
    queue_deadline_at_start=False,
)


def register_watch_policy(policy: WatchPolicy) -> None:
    """Register a mode's observation policy."""
    _POLICIES[policy.mode] = policy


def watch_policy_for(mode) -> WatchPolicy:
    """The policy for a watering mode.

    Falls back to the OpenSprinkler policy rather than raising: a run persisted
    under a mode the current build no longer knows still has to be observed to
    an end, and the acknowledging policy is the conservative one — it waits for
    a signal instead of assuming the run is live.
    """
    return _POLICIES.get(mode, _DEFAULT_POLICY)
