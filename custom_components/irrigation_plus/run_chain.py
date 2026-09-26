"""Serialise a set of self-closing runs: one at a time, optionally in slots.

``zone_sequencing`` promises that zones either run together, or one after
another, or take turns. For a zone whose valve Irrigation Plus holds open
itself that promise is kept by ``irrigation._run_rotation``, which simply sleeps
between opens. For a zone whose valve is owned by hardware there is nothing to
sleep on: the run is dispatched and returns immediately, and the only signal
that it is over is its own finalisation. So the sequencing has to be rebuilt as
a chain — dispatch one, wait to be told it finished, dispatch the next.

That chain was written for OpenSprinkler stations (v2026.07.x) and is almost
entirely generic: what it actually needs from a mode is that Irrigation Plus
decides when each run starts and is told when it ends, which is true of every
self-closing mode whose queue SI owns. This module is the generic part; a mode
supplies the little that differs as a :class:`ChainPolicy`.

``OpenSprinklerMixin`` keeps its ``_os_*`` spellings as delegates onto this
engine, including its master-hold token prefix, so its behaviour is unchanged
and its tests remain the oracle for it.

Chains are keyed by MODE, one per dispatch track. That is deliberate and it
matches how the tracks are priced (``run_window._TRACK_SEQUENCING``): a station
cycle and a service cycle are started by ``_dispatch_by_mode`` without either
being awaited, so they run concurrently with each other and the irrigation is
as long as the longer of them. Merging them into one chain would serialise the
tracks and make every finish-anchored estimate too short — the bug class of
``4d369eb``.

The one mode this engine cannot serve is batch. Its whole plan is handed to a
controller in a single call and the controller owns the queue from there, so
there is no per-zone dispatch for a chain to hold back. See issue #98.

Extracted for issue #98, whose service-mode row needs the same chain with a
different dispatch.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

from . import const

_LOGGER = logging.getLogger(__name__)


@dataclass
class Rotation:
    """A rotating cycle: what each zone has left, and when it last stopped.

    ``cursor`` indexes ``order`` at the zone dispatched last, so the next turn
    resumes after it instead of restarting at the top every time.
    """

    slot: float
    absorption: float
    order: list = field(default_factory=list)
    remaining: dict = field(default_factory=dict)
    last_finish: dict = field(default_factory=dict)
    cursor: int = -1


@dataclass(frozen=True)
class ZonePlan:
    """What the dispatching cycle decided for a zone still waiting its turn.

    The queue holds ids and the advance re-reads the store, which is right for
    everything that can legitimately change while a zone waits — its valve, its
    confirm entity, and above all its bucket, which is the absolute anchor the run
    reconciles from (``self_closing.async_run_self_closing``'s ``pre_bucket``). It
    is wrong for the one thing the cycle itself decided: how long this run is.
    ``_apply_live_durations`` prices that into a COPY that nothing stores, so
    without this the copy dies at the queue and the zone waters its stale daily
    duration.

    ``seconds`` therefore overrides the store only for a zone the estimate
    re-sized, i.e. only when ``live`` is set. A zone the estimate passed through
    follows the store at its turn exactly as it does without this class, because
    there the re-read is not a lost decision but the daily calculation re-pricing
    the zone. The consequence is worth stating plainly: a queued zone is deaf to
    rain falling mid-cycle **only when the live estimate sized it**, and for that
    zone deliberately so. Re-pricing a queued zone properly means porting
    ``_resize_queued_zone``, which is a feature and not this class.

    ``live`` carries two jobs, and the second is why it is not merely
    informational: it gates the duration overlay in ``_chain_advance``, and it
    restores the credit ceiling for the dispatch that follows. Both rest on the
    same fact -- that the estimate re-sized this zone -- and that fact cannot be
    recovered later, which is what the next paragraph is about.

    ``live`` is captured here because that is the only moment it exists:
    ``_apply_live_durations`` rebinds ``_live_run_zones`` wholesale on every
    scheduled call, on both its early-return and its main path, so a zone still
    waiting its turn when the next call lands would otherwise lose the membership
    its own cycle granted it. ``_chain_advance`` calls ``_mark_live_run`` to put
    the id back into ``_live_run_zones`` immediately before the dispatch that
    consumes it — never earlier, or a check that still drops the zone
    (``zone_run_in_flight``) would leak the marker into that zone's next,
    unrelated run — so ``_run_ceiling`` finds and consumes it there exactly as it
    would have on the first pass. The detour through a set is not incidental:
    ``_run_ceiling`` tests membership of that instance set by zone id, it does
    not read a field off the zone dict, so a flag on the plan has to be
    translated back rather than handed straight to the run.
    """

    seconds: float
    live: bool = False


@dataclass
class Chain:
    """The in-memory dispatch cycle and its master hold.

    ``zones`` carries the sequential chain (one dispatch per zone, in order);
    ``rotation`` carries the rotating one (many slot-sized dispatches per zone).
    Normally only one of the two is set — except across a mid-cycle
    ``zone_sequencing`` flip, which writes through without a reload and can
    leave the old geometry's state sitting behind the new one's; see
    ``_chain_forfeit_queue``. ``absorb`` is the pending absorption timer.

    ``planned`` maps a queued zone's id to its :class:`ZonePlan`. It is a sibling of
    ``zones`` rather than its element type because ``_chain_drop_zone`` compares
    ``int(z)`` against a zone id and that method is the first thing
    ``async_stop_zone`` calls. A missing entry means "use the stored duration" --
    and so does an entry whose ``live`` is unset, which is the ordinary case on an
    install without the live estimate. Both degrade to the old behaviour instead
    of dropping a run, so the two structures drifting apart cannot cost water.
    """

    zones: list = field(default_factory=list)
    planned: dict = field(default_factory=dict)
    trigger: object | None = None
    token: str | None = None
    rotation: Rotation | None = None
    absorb: object | None = None


@dataclass(frozen=True)
class ChainPolicy:
    """What one watering mode contributes to the shared chain.

    ``label`` prefixes this chain's log lines, so a two-track irrigation can be
    read apart in the log.

    ``token_prefix`` names its master hold. Per mode rather than shared because
    the two chains take a hold each and both may be up at once, and because
    OpenSprinkler's ``os-chain:`` predates this module — keeping it is what lets
    that mode's tests go on asserting the token they always did.
    """

    mode: str
    label: str
    token_prefix: str


_POLICIES: dict[str, ChainPolicy] = {}


def register_chain_policy(policy: ChainPolicy) -> None:
    """Register a mode's chain policy, from that mode's own module."""
    _POLICIES[policy.mode] = policy


def chain_policy_for(mode) -> ChainPolicy | None:
    """The policy for a watering mode, or None if that mode does not chain.

    None rather than a fallback: a mode with no policy is one whose runs this
    engine must not try to serialise, and guessing a policy for it would hold
    back dispatches nothing will ever release.
    """
    return _POLICIES.get(mode)


class RunChainMixin:
    """Serialise self-closing dispatches. Mixed into SmartIrrigationCoordinator.

    Reuses ``SelfClosingMixin``'s run record and finalisation wholesale; this
    adds only the part that decides *which zone goes next, and when*.
    """

    # --- state --------------------------------------------------------------

    def _chains(self) -> dict:
        """Lazy ``{mode: Chain}``, one chain per dispatch track.

        In memory only, deliberately. Persisting a chain would mean
        re-dispatching after a restart, and no self-closing mode may actuate
        hardware on the way back up (see ``_os_resume_run``). The cost is that a
        restart mid-cycle abandons whatever had not been dispatched yet, which
        is the trade sequential and rotating make: under ``parallel`` every run
        is already out and survives a crash, under the other two only the run
        that already started does.
        """
        chains = getattr(self, "_run_chains", None)
        if chains is None:
            chains = self._run_chains = {}
        return chains

    def _chain_state(self, mode) -> Chain:
        """This mode's chain, created empty on first use."""
        chains = self._chains()
        state = chains.get(mode)
        if state is None:
            state = chains[mode] = Chain()
        return state

    def _chain_zone_mode(self, zone: dict) -> str | None:
        """The chain a zone belongs to right now, or None."""
        return (zone or {}).get(const.ZONE_WATERING_MODE)

    # --- dispatch -----------------------------------------------------------

    async def async_dispatch_chained_zones(self, zones: list, *, mode, trigger) -> None:
        """Start ``zones`` under the configured zone sequencing.

        ``parallel`` dispatches them all and returns; the hardware owns every
        close and they water together. ``sequential`` dispatches one and holds
        the rest back until that run finalises. ``rotating`` is that same chain
        with each zone re-entering it until its duration is spent — see
        :meth:`_chain_start_rotation`.

        A single zone still goes through the rotation under ``rotating``:
        rotating is about runoff, not about order, so one zone's duration is
        split into slots just as four zones' are.
        """
        zones = [z for z in zones if self._chain_zone_mode(z) == mode]
        if not zones:
            return
        policy = chain_policy_for(mode)
        if policy is None:
            for zone in zones:
                await self.async_run_self_closing(zone, trigger=trigger)
            return
        sequencing = self.store.config.zone_sequencing
        if sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            await self._chain_start_rotation(zones, mode=mode, trigger=trigger)
            return
        if sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL or len(zones) == 1:
            for zone in zones:
                await self.async_run_self_closing(zone, trigger=trigger)
            return

        state = self._chain_state(mode)
        live_now = getattr(self, "_live_run_zones", None) or set()
        # Replaces both structures wholesale, in lockstep off one bound id per
        # zone — merging into what a previous cycle left behind is a later PR's
        # behaviour, not this one's.
        state.zones = []
        state.planned = {}
        for zone in zones[1:]:
            zid = int(zone.get(const.ZONE_ID))
            state.zones.append(zid)
            state.planned[zid] = ZonePlan(
                seconds=float(zone.get(const.ZONE_DURATION) or 0),
                live=zid in live_now,
            )
        state.trigger = trigger
        await self._chain_take_hold(state, policy)
        _LOGGER.info(
            "%s: dispatching zone %s, %s more chained behind it",
            policy.label,
            zones[0].get(const.ZONE_ID),
            len(state.zones),
        )
        if not await self.async_run_self_closing(zones[0], trigger=trigger):
            _LOGGER.warning(
                "%s: zone %s refused its dispatch, the cycle continues without it",
                policy.label,
                zones[0].get(const.ZONE_ID),
            )
            # async_run_self_closing self-cleans the marker on only one of its
            # four return-False paths (a confirm that came back false); a zero
            # window, an unresolvable OpenSprinkler station or an already
            # in-flight zone all leave it set. _chain_advance hands it back for
            # every zone behind this one on the same refusal — this call site
            # dispatches the cycle's first zone on its own, outside that loop,
            # so it needs the same hand-back.
            self._drop_live_run_marker(zones[0].get(const.ZONE_ID))
            # Refused; the chain must not stall on it.
            await self._chain_advance(mode)

    async def _chain_take_hold(self, state: Chain, policy: ChainPolicy) -> None:
        """One master hold for the whole cycle, taken once.

        The gaps between runs — and under rotating the absorption waits, which
        stretch a cycle far past any up-front estimate — are part of the cycle. A
        per-run hold would drop the master in every one of them.
        """
        if state.token is not None:
            return
        state.token = f"{policy.token_prefix}{uuid.uuid4().hex[:8]}"
        await self.async_master_acquire(state.token)

    async def _chain_advance(self, mode, finished_zone_id=None) -> None:
        """Start the next chained zone or rotation slot, or end the cycle.

        Safe to call from every finalisation path: it returns while any run of
        this chain's mode is still in flight, so whichever of them fires first
        advances once. ``finished_zone_id`` is the zone whose run just ended,
        which is what a rotation measures its absorption wait from; the
        sequential chain ignores it, and so does a zone that is not part of the
        current cycle.
        """
        state = self._chain_state(mode)
        if not state.zones and state.rotation is None and state.token is None:
            return
        rotation = state.rotation
        if rotation is not None and finished_zone_id is not None:
            # Stamped as the turn ends, not as the slot was dispatched: what the
            # soil is given to absorb is the water, so the wait runs from the
            # moment the valve stopped.
            zid = int(finished_zone_id)
            if zid in rotation.remaining:
                rotation.last_finish[zid] = dt_util.utcnow()
        for run in await self._sc_active_runs():
            if run.get(const.RUN_MODE) == mode:
                return
        if rotation is not None:
            await self._chain_rotation_advance(mode)
            return
        policy = chain_policy_for(mode)
        label = policy.label if policy else mode
        while state.zones:
            zone_id = state.zones.pop(0)
            plan = state.planned.pop(zone_id, None)
            zone = self.store.get_zone(zone_id) or {}
            if self._chain_zone_mode(zone) != mode:
                _LOGGER.info(
                    "%s: dropping zone %s from the cycle, its watering mode "
                    "changed or the zone is gone",
                    label,
                    zone_id,
                )
                # Hand back a marker this loop never set: _apply_live_durations
                # placed it before the cycle began and it has sat in
                # _live_run_zones since. Unconditional on purpose — the drop is
                # a discard, so a zone with no marker is left untouched.
                self._drop_live_run_marker(zone_id)
                continue
            if plan is not None and plan.live:
                # Gated on ``live``, not on merely having a plan. For a zone the
                # live estimate re-sized, the cycle made a decision that exists
                # nowhere else and the store re-read threw it away -- that is the
                # defect. For every other zone the re-read is the daily
                # calculation re-pricing the zone at its turn, which is not a lost
                # decision, so it stays: a mid-chain calculation can realistically
                # only move a stored duration DOWN, which makes a zone rewritten
                # while it waited a zone that got rained on. Freezing it would
                # also leave the run priced against the cycle-start bucket while
                # ``pre_bucket`` is the fresh one.
                # One field either way, never a snapshot: ZONE_BUCKET is the run's
                # absolute reconcile anchor and must be current, not as it stood
                # when the cycle began.
                zone = dict(zone, **{const.ZONE_DURATION: plan.seconds})
            if (zone.get(const.ZONE_DURATION) or 0) <= 0:
                _LOGGER.info(
                    "%s: dropping zone %s from the cycle, nothing left to water",
                    label,
                    zone_id,
                )
                self._drop_live_run_marker(zone_id)
                continue
            if self.zone_run_in_flight(zone_id):
                _LOGGER.info(
                    "%s: dropping zone %s from the cycle, another run took it "
                    "over while it waited",
                    label,
                    zone_id,
                )
                self._drop_live_run_marker(zone_id)
                continue
            if plan is not None and plan.live:
                # Textually the same test as the overlay above, and deliberately
                # not merged with it: the overlay has to land before the duration
                # check that can still drop this zone, while the marker must not be
                # set until every such check has passed, or it leaks into that
                # zone's next, unrelated run. Two sites, one condition, opposite
                # constraints on when they may run.
                # _apply_live_durations rebinds the whole set on every scheduled
                # call, so a zone queued across one loses the allowance its own
                # cycle granted it. Put it back for the dispatch; _run_ceiling
                # consumes it there as it would have on the first pass.
                self._mark_live_run(zone_id)
            if await self.async_run_self_closing(zone, trigger=state.trigger):
                return
            # A refusal is a warning, not an info line like the three drops
            # above: those are ordinary consequences of the configuration
            # moving under a running cycle, but a refusal means something the
            # user set up did not work.
            _LOGGER.warning(
                "%s: zone %s refused its dispatch, the cycle continues without it",
                label,
                zone_id,
            )
            # Refused: nothing consumed the marker armed above, so hand it back,
            # and fall through to the next rather than stalling the chain.
            self._drop_live_run_marker(zone_id)
        await self._chain_release(mode)

    async def _chain_advance_for_run(self, zone_id, run: dict) -> None:
        """Advance whichever chain the run that just ended belonged to.

        Keyed on the RUN's mode, not the zone's. The run carries the mode it was
        dispatched under, which is still the right chain when the zone has since
        been edited to another mode mid-cycle — and the zone's current mode
        would then advance a chain that never held it while leaving the one that
        did stalled behind a run it will never hear about again.
        """
        mode = (run or {}).get(const.RUN_MODE)
        if mode is None or mode not in self._chains():
            return
        self._chain_forget_finished(mode, zone_id)
        await self._chain_advance(mode, zone_id)

    def _chain_forget_finished(self, mode, zone_id) -> None:
        """Take a zone the chain still holds out of the queue once it has watered.

        A sequential cycle pops a zone BEFORE dispatching it, so a zone that is
        still queued when a run of it finalises was watered by something else —
        Irrigate-now, a service call, a run_zone. Neither that caller's guard nor
        this chain's could see it: both ask ``zone_run_in_flight``, and a merely
        queued zone answers False.

        Without this the chain pops it one finalisation later and waters it a
        second time, seconds after it stopped, crediting the bucket twice. The
        guard at the pop cannot catch that, because the finaliser removes the run
        record BEFORE advancing and that record is precisely what
        ``zone_run_in_flight`` reads. The ordering is deliberate — it exists so
        the deferred calculation no longer sees a run — so the fix belongs at
        this end instead.

        A rotation keeps ``zones`` empty, so it is unaffected; a rotating zone's
        turns are governed by ``remaining`` and may legitimately recur.
        """
        try:
            zid = int(zone_id)
        except (TypeError, ValueError):
            return
        state = self._chain_state(mode)
        if zid not in state.zones:
            return
        policy = chain_policy_for(mode)
        _LOGGER.info(
            "%s: taking zone %s out of the cycle, it was already watered by "
            "another run while it waited",
            policy.label if policy else mode,
            zid,
        )
        state.zones = [z for z in state.zones if int(z) != zid]
        state.planned.pop(zid, None)
        self._drop_live_run_marker(zid)

    def _chain_drop_zone(self, zone_id) -> None:
        """Take one zone out of whatever cycle holds it, leaving the rest alone.

        A stop has to reach the cycle as well as the run in flight. What a zone
        has left is held in memory rather than in its run record, so finalising
        only the run leaves the remainder there and the zone the user just
        stopped is dispatched again one absorption wait later.
        """
        zid = int(zone_id)
        for state in self._chains().values():
            rotation = state.rotation
            held = False
            if rotation is not None and zid in rotation.remaining:
                rotation.remaining[zid] = 0.0
                held = True
            if any(int(z) == zid for z in state.zones):
                held = True
            state.zones = [z for z in state.zones if int(z) != zid]
            state.planned.pop(zid, None)
            if held:
                # It was waiting in this cycle and now never will water, so hand
                # back the credit ceiling the cycle granted it. Gated on having
                # actually held it: this runs for EVERY stop, including classic
                # zones no chain ever queued, whose marker belongs to a run that
                # is still finishing.
                self._drop_live_run_marker(zid)

    def _chain_forfeit_queue(self, mode, why: str) -> None:
        """Report the zones a cycle is abandoning and hand back what they hold.

        A service chain never reaches ``async_abort_opensprinkler_runs`` — that
        path filters on the station mode and has no service twin — so this is the
        only place a shutdown mid-cycle can account for its queue. Silent on an
        idle chain, because unload runs for every install whether a cycle was up
        or not.

        A rotation's currently-dispatched zone can appear here too, alongside the
        zones that never started: ``rotation.remaining`` is deducted at dispatch,
        not on the way back (see ``_chain_rotation_advance``), so a zone whose
        slot is still running already shows only what is left of it AFTER that
        slot. That is correct, not a bug — the slot in flight is not this
        method's business, either the hardware finishes it or the caller stops
        it, but the slots still to come are exactly as abandoned as a zone that
        never got one.
        """
        state = self._chain_state(mode)
        waiting = [int(z) for z in state.zones]
        if state.rotation is not None:
            # Both can be populated at once, despite the Chain docstring's
            # "only one of the two is ever set": zone_sequencing lives in the
            # store, so flipping it mid-cycle writes through without a reload
            # (async_update_config only dispatches _config_updated), and the
            # new geometry's dispatch does not clear the old one's state.
            # Without the guard below a zone still held by both would be
            # named twice.
            waiting += [
                int(zid)
                for zid, left in state.rotation.remaining.items()
                if left > 0 and int(zid) not in waiting
            ]
        if not waiting:
            return
        policy = chain_policy_for(mode)
        _LOGGER.info(
            "%s: abandoning the rest of the cycle for %s %s — %s",
            policy.label if policy else mode,
            "zone" if len(waiting) == 1 else "zones",
            ", ".join(str(zid) for zid in waiting),
            why,
        )
        for zid in waiting:
            self._drop_live_run_marker(zid)

    async def _chain_release(self, mode) -> None:
        """Drop this chain and its master hold.

        Also names whatever the cycle still had queued or mid-rotation and
        hands back any live-estimate marker those zones hold — see
        :meth:`_chain_forfeit_queue`.
        """
        state = self._chain_state(mode)
        self._chain_cancel_absorption(mode)
        self._chain_forfeit_queue(mode, "the cycle was stopped")
        state.zones, state.trigger, state.rotation = [], None, None
        state.planned = {}
        token, state.token = state.token, None
        if token:
            await self.async_master_release(token)

    def _chain_teardown(self) -> None:
        """Drop every pending chain (called on unload).

        The chains live in memory only, so unload ends them. Each master hold
        goes with the coordinator; there is nothing left that could release it.
        Before dropping a chain it also names the queue it is abandoning and
        hands back any live-estimate marker those zones hold — see
        :meth:`_chain_forfeit_queue`.
        """
        for mode, state in list(self._chains().items()):
            self._chain_cancel_absorption(mode)
            self._chain_forfeit_queue(mode, "the integration is unloading")
            state.zones, state.trigger, state.token = [], None, None
            state.rotation = None
            state.planned = {}

    # --- rotating -----------------------------------------------------------

    async def _chain_start_rotation(self, zones: list, *, mode, trigger) -> None:
        """Split every zone's duration into slots and start the first one.

        A zone re-enters the chain for at most
        ``zone_sequencing_max_consecutive_duration`` minutes at a time until its
        duration is spent, and is not dispatched again until
        ``zone_sequencing_min_absorption_time`` has passed since its last slot
        stopped. That is what the setting is for: a long run on tight soil puts
        down more water than the soil can take, so the same total is delivered
        in slices.

        Slots are dispatched one at a time even where the hardware could run two
        zones concurrently, for the same reason ``sequential`` is: a mode that
        only sometimes governs is worse than none.
        """
        policy = chain_policy_for(mode)
        if policy is None:
            return
        state = self._chain_state(mode)
        rotation = Rotation(
            slot=max(
                1,
                (self.store.config.zone_sequencing_max_consecutive_duration or 5),
            )
            * 60.0,
            absorption=(self.store.config.zone_sequencing_min_absorption_time or 0)
            * 60.0,
        )
        for zone in zones:
            duration = float(zone.get(const.ZONE_DURATION) or 0)
            if duration <= 0:
                continue
            zone_id = int(zone.get(const.ZONE_ID))
            rotation.order.append(zone_id)
            rotation.remaining[zone_id] = duration
        if not rotation.order:
            return

        state.rotation = rotation
        state.zones = []
        # The two geometries are exclusive (see the Chain docstring); a sequential
        # plan left over from a cycle this one replaces must not outlive it.
        state.planned = {}
        state.trigger = trigger
        await self._chain_take_hold(state, policy)
        _LOGGER.info(
            "%s: rotating %s zones in slots of up to %.0fs with a %.0fs "
            "absorption wait",
            policy.label,
            len(rotation.order),
            rotation.slot,
            rotation.absorption,
        )
        await self._chain_rotation_advance(mode)

    def _chain_rotation_next(self, rotation: Rotation):
        """``((index, zone_id), None)`` for the zone whose turn it is.

        ``(None, seconds)`` when every zone with water left is still absorbing,
        and ``(None, None)`` when the rotation is finished. Zones are considered
        in order from the one after the last dispatch, so a zone still absorbing
        is passed over for the next one rather than holding the whole rotation.
        """
        order = rotation.order
        now = dt_util.utcnow()
        absorption = rotation.absorption
        soonest = None
        for offset in range(len(order)):
            index = (rotation.cursor + 1 + offset) % len(order)
            zone_id = order[index]
            if rotation.remaining.get(zone_id, 0) <= 0:
                continue
            last_finish = rotation.last_finish.get(zone_id)
            if absorption > 0 and last_finish is not None:
                wait = absorption - (now - last_finish).total_seconds()
                # A second of slack, because the timer that brings us back here
                # runs on the event loop's clock while the window is measured on
                # the wall clock. Live, the two disagreed by 2 ms at the boundary,
                # which without this arms a second, zero-length wait before every
                # single dispatch. A minutes-long window does not care about the
                # second; the log line and the extra round trip do.
                if wait > 1.0:
                    soonest = wait if soonest is None else min(soonest, wait)
                    continue
            return (index, zone_id), None
        return None, soonest

    async def _chain_rotation_advance(self, mode) -> None:
        """Dispatch the next slot, wait out an absorption window, or finish."""
        state = self._chain_state(mode)
        rotation = state.rotation
        if rotation is None:
            return
        policy = chain_policy_for(mode)
        label = policy.label if policy else mode
        self._chain_cancel_absorption(mode)
        while True:
            candidate, wait = self._chain_rotation_next(rotation)
            if candidate is None:
                if wait is None:
                    break
                self._chain_arm_absorption(mode, wait)
                return
            index, zone_id = candidate
            zone = self.store.get_zone(zone_id) or {}
            if self._chain_zone_mode(zone) != mode:
                # Reconfigured or gone while the rotation was waiting. Drop its
                # remainder rather than come back to it every turn for the rest
                # of the cycle.
                _LOGGER.info(
                    "%s rotation: writing off zone %s and its remaining %.0fs, "
                    "its watering mode changed or the zone is gone",
                    label,
                    zone_id,
                    rotation.remaining[zone_id],
                )
                rotation.remaining[zone_id] = 0.0
                self._drop_live_run_marker(zone_id)
                continue
            if self.zone_run_in_flight(zone_id):
                # Something else took the zone while the rotation was waiting, so
                # its remainder is written off the same way a reconfigured zone's
                # is. Handing the live marker back is safe even though that other
                # run is still going: a run's ceiling is decided once, at its own
                # dispatch, and frozen into its record (``run_watch``'s
                # ``run_credit_ceiling``). The marker it used is long consumed;
                # what this hands back is the rotation's own leftover.
                _LOGGER.info(
                    "%s rotation: writing off zone %s and its remaining %.0fs, "
                    "another run took it over while it waited",
                    label,
                    zone_id,
                    rotation.remaining[zone_id],
                )
                rotation.remaining[zone_id] = 0.0
                self._drop_live_run_marker(zone_id)
                continue
            slot = min(rotation.slot, rotation.remaining[zone_id])
            rotation.cursor = index
            # Deducted at dispatch, never on the way back. A slot the hardware
            # cuts short or drops has had its turn: re-queueing it would let a
            # controller-side rain delay, which drops every run it is given,
            # rotate for ever.
            rotation.remaining[zone_id] -= slot
            _LOGGER.info(
                "%s rotation: zone %s slot %.0fs, %.0fs left after it",
                label,
                zone_id,
                slot,
                rotation.remaining[zone_id],
            )
            # A copy, so the slot is what this run is dispatched, credited and
            # measured for while the zone's own stored duration — what the panel
            # shows and what the next rotation would be built from — is left
            # alone. Every slot is a run in its own right: its own record, its
            # own bucket credit, its own flow sampling, its own log line.
            if await self.async_run_self_closing(
                dict(zone, **{const.ZONE_DURATION: slot}), trigger=state.trigger
            ):
                return
            # Refused. Abandon the zone rather than retry it on every turn until
            # the rotation ends. Both numbers are named because the remainder
            # alone understates it: the slot was deducted before the dispatch was
            # attempted, so it is lost as well.
            _LOGGER.warning(
                "%s rotation: zone %s refused its %.0fs slot, writing off its "
                "remaining %.0fs too",
                label,
                zone_id,
                slot,
                rotation.remaining[zone_id],
            )
            rotation.remaining[zone_id] = 0.0
            self._drop_live_run_marker(zone_id)
        await self._chain_release(mode)

    def _chain_cancel_absorption(self, mode) -> None:
        """Cancel-and-drop a pending absorption wait (no-op if none is armed)."""
        state = self._chain_state(mode)
        cancel = state.absorb
        if cancel is not None:
            cancel()
        state.absorb = None

    def _chain_arm_absorption(self, mode, delay: float) -> None:
        """Wait ``delay`` before looking for the next slot.

        A timer, not a sleeping task: the rotation holds no coroutine between
        slots, so there is nothing to cancel at unload except this handle — which
        :meth:`_chain_teardown` does.
        """
        state = self._chain_state(mode)
        policy = chain_policy_for(mode)
        self._chain_cancel_absorption(mode)

        async def _absorbed(_now):
            state.absorb = None
            await self._chain_advance(mode)

        _LOGGER.info(
            "%s rotation: every zone is absorbing, next slot in %.0fs",
            policy.label if policy else mode,
            delay,
        )
        state.absorb = async_call_later(self.hass, max(0.0, delay), _absorbed)
