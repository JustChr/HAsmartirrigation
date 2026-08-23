"""Fitting an irrigation run into the window before its finish anchor.

Pure arithmetic — no Home Assistant, no coordinator, no store — so the
sequencing model can be tested directly against hand-computed clocks. The
scheduler and the runner supply the zone facts; everything here is a function
of them.

The one non-obvious piece is the rotating model. ``sum(durations)`` is watering
time, not wall clock: a single zone needing 600 s, sliced into 300 s slots with
a 600 s absorption pause between them, occupies 1200 s of night. Sizing a
finish-anchored run by the sum therefore starts it far too late, which is how a
predicted deadline came to cut the pump mid-rotation. :func:`simulate_wall_clock`
replays the runner's own loop instead, and :func:`concurrent_wall_clock` — what
every caller outside this module reaches for — applies it per dispatch track.
"""

from __future__ import annotations

import datetime
import math
from dataclasses import dataclass

from . import const
from .batch import is_batch_zone
from .duration_math import zone_run_duration
from .opensprinkler import is_opensprinkler_zone
from .self_closing import is_self_closing_zone

# Which dispatch track a zone runs on. ``_dispatch_by_mode`` starts each track
# and returns without awaiting it, so the tracks run CONCURRENTLY and the wall
# clock is the longest of them rather than their total. zone_sequencing governs
# only the classic track; the other two have a fixed reduction of their own.
TRACK_CLASSIC = "classic"
TRACK_SELF_CLOSING = "service"
TRACK_STATION = "station"
TRACK_BATCH = "batch"

# The sequencing each non-classic track behaves as, whatever zone_sequencing
# says. Expressed as a sequencing rather than as max()/sum() so all four tracks
# price through the one simulate_wall_clock, including its rotating model.
#
#   service  — parallel. _dispatch_by_mode fires every service-mode zone in a
#     single loop and the hardware owns each close, so they open together.
#   station  — sequential. Under sequential/rotating Smart Irrigation chains the
#     stations itself; under parallel it hands the controller everything at once
#     and the controller's own grouping decides. Where that grouping can be read
#     off the station entities :func:`_grouped_station_wall_clock` prices it
#     exactly; this is what the track falls back to when it cannot, because only
#     the longer of the possible orderings is safe to anchor on — an
#     under-estimate finishes the irrigation after the requested time.
#   batch    — sequential, and the one track whose serialisation is a property
#     of the mode rather than of a setting or a controller flag: the whole
#     irrigation is handed over as one queue, and a queue waters one valve at a
#     time. There is nothing to hedge and nothing to read off the hardware.
#
#     Sequential rather than rotating even when zone_sequencing says rotating: a
#     rotation is only expressible in a queue by listing a zone repeatedly with a
#     slice of its duration, which is a change to the PLAN and not just to its
#     pricing. Until the dispatcher emits that, pricing a rotation the queue will
#     not perform would size the window for absorption pauses that never happen.
#
#     A batch zone is also self-closing by ``is_self_closing_zone``, so this
#     track only takes effect because :func:`track_for_zone` tests it first —
#     falling through to ``service`` would price a queue as PARALLEL, i.e. the
#     longest zone rather than all of them, and anchor a finish-governed run
#     hours late.
_TRACK_SEQUENCING = {
    TRACK_SELF_CLOSING: const.CONF_ZONE_SEQUENCING_PARALLEL,
    TRACK_STATION: const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
    TRACK_BATCH: const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
}

# A zone with no ``maximum_duration`` has NO configuration-derived ceiling, and
# there is no constant that can stand in for one. Every `or 14400` in
# irrigation.py is a flow-zone safety timeout, so nothing caps a timed zone's
# length; and the deficit that sizes it is not capped either, because
# ``maximum_bucket`` clamps the bucket's SURPLUS side only (``calculation.py``:
# `if bucket_plus_delta_capped > maximum_bucket`) and nothing clamps the
# deficit side. A number here would be a policy cap wearing a bound's name,
# which is the mistake this module already made once.
# The station group id meaning "runs alongside everything". Below it, an id is a
# sequential group: stations sharing one are serialised with each other, and
# different groups run concurrently with each other. Per the controller's own
# API reference; the ids are not the A-D labels its interface shows.
PARALLEL_STATION_GROUP = 255

# A rotating slot of zero would divide a zone into zero-length slots and never
# terminate. The runner floors the configured minutes at 1 (`max(1, ...)`); this
# floors the seconds, which is the same guarantee one level down.
MIN_SLOT_SECONDS = 1.0

# Depletion ratios equal to this many decimals are one tie group. A ratio
# difference below 0.01 — 0.006 in of bucket at a -0.6 in threshold — is not a
# meaningful dryness distinction, just measurement and rounding residue, and
# letting it order the night would defeat the packing this grouping exists for.
RATIO_TIE_DECIMALS = 2

# Past this many tied zones the subset search (2^k simulations) falls back to
# greedy add-in-rank-order. Real installs run single digits of zones; this is a
# backstop, not a tuning knob.
MAX_TIE_GROUP_EXHAUSTIVE = 12


@dataclass(frozen=True)
class StationFacts:
    """What the CONTROLLER says about one station, read off its entity.

    ``group`` is the raw station group id (see :data:`PARALLEL_STATION_GROUP`),
    or None when it cannot be read — a controller that is unavailable, a
    firmware below v2.2.0(1), an OpenSprinkler integration too old to publish
    it. None is the honest answer and is treated as such: it is never mistaken
    for group 0, which would claim a chain the controller may not run.

    ``delay_seconds`` is the controller-wide gap it inserts between two stations
    that do run back to back, negative when they are deliberately overlapped. It
    rides on the run rather than on the reduction's signature so that an install
    with two controllers takes each station's delay from its own.

    ``controller_id`` identifies which controller answered. Group ids are
    numbered per controller, so two controllers each have a group 0 that have
    nothing to do with each other; without this they would partition into one
    chain and the run would be priced as twice as long as it is.
    """

    group: int | None = None
    delay_seconds: float = 0.0
    controller_id: str | None = None


@dataclass(frozen=True)
class ZoneRun:
    """One zone's candidacy for tonight's run.

    ``duration`` is the seconds of watering the zone needs *now* — under the
    live-estimate gate that is sized from the intra-day deficit, not from the
    stored daily duration.

    ``depletion_ratio`` is ``bucket / bucket_threshold``. It is dimensionless,
    so it compares zones with different allowed depletions correctly, and
    exactly 1.0 is the due line — the sort key and the gate are the same
    quantity. Callers pass only zones that are genuinely due (ratio >= 1).

    ``maximum_duration`` is configuration, never a live value, which is what
    makes :func:`bound_wall_clock` knowable days ahead.

    ``track`` is which of the concurrent dispatch tracks the zone runs on — see
    :func:`track_for_zone`. It defaults to classic so a caller that builds a run
    without one prices it exactly as before.

    ``lead_time`` is the zone's configured pre-roll. It is carried separately
    because ``duration_from_deficit`` clamps to ``maximum_duration`` and adds
    the lead time AFTER, so the cap alone under-states what the zone occupies
    by exactly this much — see :func:`bound_wall_clock`.

    ``ceiling`` is an upper bound on this zone's run length for a zone with no
    ``maximum_duration``, supplied by a caller that has one to give. Nothing in
    this integration does today, so it is normally absent and such a zone is
    reported as unbounded. It is NOT derivable from ``maximum_bucket``: that
    clamps the bucket's surplus side, not the deficit that sizes the run.

    ``flow`` marks a zone that delivers to a measured volume. It changes no
    arithmetic here, only the order: ``_run_rotation`` serves flow zones after
    the timed ones whatever order the plan arrives in.
    ``station`` carries the controller's own answer for a station-track zone —
    see :class:`StationFacts`. Absent means unread, which prices the track the
    way it was priced before any of it could be read.
    """

    zone_id: int
    duration: float
    depletion_ratio: float
    last_irrigation: datetime.datetime | str | None = None
    maximum_duration: float | None = None
    track: str = TRACK_CLASSIC
    lead_time: float = 0.0
    ceiling: float | None = None
    flow: bool = False
    station: StationFacts | None = None


def track_for_zone(zone: dict) -> str:
    """Which dispatch track ``zone`` runs on.

    Station and batch first: both are self-closing too, and their own tracks are
    the more specific answer. Order matters — see :data:`_TRACK_SEQUENCING` for
    what a batch zone falling through to ``service`` would cost.
    """
    if is_opensprinkler_zone(zone):
        return TRACK_STATION
    if is_batch_zone(zone):
        return TRACK_BATCH
    if is_self_closing_zone(zone):
        return TRACK_SELF_CLOSING
    return TRACK_CLASSIC


def _epoch(moment: datetime.datetime | str | None) -> float:
    """Sort value for a last-irrigation stamp, oldest first, never watered first.

    Stamps reach us in three shapes. The runner writes ``dt_util.now()``
    (aware); a zone hydrated from older storage can carry a naive one; and
    ``store.async_get_zones`` returns ``attr.asdict`` of an entry loaded from
    JSON, so every zone carries an ISO **string** until something rewrites the
    field in the running process. Comparing those raises TypeError, which here
    would abort the whole night's run — so all three are reduced to a float.

    The string shape is the one worth naming, because letting it fall through to
    the never-watered value is silent rather than loud: it is what a restarted
    install hands over for every zone, so the whole tie-break would collapse to
    zone id exactly where it is supposed to be doing the work. A naive stamp is
    read as local time, which is what wrote it.
    """
    if moment is None:
        return float("-inf")
    if isinstance(moment, str):
        try:
            moment = datetime.datetime.fromisoformat(moment)
        except ValueError:
            return float("-inf")
    try:
        return moment.timestamp()
    except (AttributeError, ValueError, OverflowError, OSError):
        return float("-inf")


def rank(runs: list[ZoneRun]) -> list[ZoneRun]:
    """Priority order: driest first, then longest since last watered.

    The tie-break is load-bearing rather than an edge case. The bucket is
    depth-based — it depends on ET, precipitation, drainage and Kc, and *not* on
    zone size or throughput — so zones sharing a sensor group with equal
    thresholds converge to identical buckets after any night where they all run
    to 0, and stay identical. Ranking then decides nothing and
    ``last_irrigation`` decides the entire rotation. Zone id settles the
    remaining case so the order is deterministic across restarts.
    """
    return sorted(
        runs,
        key=lambda r: (-r.depletion_ratio, _epoch(r.last_irrigation), r.zone_id),
    )


def _budget(run: ZoneRun, durations: dict[int, float] | None) -> float:
    """The watering seconds ``run`` is priced with: the caller's override for
    that zone if it gave one, otherwise the run's own duration."""
    return float((durations or {}).get(run.zone_id, run.duration) or 0.0)


def simulate_wall_clock(
    runs: list[ZoneRun],
    *,
    sequencing: str,
    max_slot_seconds: float,
    min_absorption_seconds: float,
    durations: dict[int, float] | None = None,
) -> float:
    """Wall-clock seconds ``runs`` occupy, in the order given.

    ``durations`` overrides each zone's watering budget by id (used by
    :func:`bound_wall_clock` to price the configured maximums instead of the
    live durations); by default each zone's own ``duration`` is used.
    """
    # Flow zones last, whatever order the caller passed. ``_run_rotation``
    # builds its ring from ``timed_zones + flow_zones``, so a flow zone is
    # always served after the timed ones; pricing the caller's order instead
    # moves the rotating clock by an absorption pause or more, and that clock
    # is what a finish anchor is worked back from.
    ordered = [r for r in runs if not r.flow] + [r for r in runs if r.flow]
    # Positional, not keyed by zone_id: two runs sharing an id used to collapse
    # into one and the clock came out short, which is the unsafe direction.
    budgets = [_budget(r, durations) for r in ordered]
    work = [b for b in budgets if b > 0]
    if not work:
        return 0.0

    if sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL:
        return max(work)
    if sequencing != const.CONF_ZONE_SEQUENCING_ROTATING:
        return sum(work)

    # Rotating: replay irrigation._run_rotation's loop. A zone that is finished
    # is skipped BEFORE its absorption wait is considered, exactly as there, so
    # a completed zone never charges a trailing pause.
    #
    # An unbounded zone is priced as math.inf (bound_wall_clock's "no fixed
    # point exists here"), and the replay cannot converge on one: a slot takes
    # a finite bite out of an infinite budget and leaves it infinite, so the
    # loop below never exits. The rotation really has no end in that case, so
    # answer with the infinity rather than hang on it. Only this branch needs
    # the guard; parallel takes a max and sequential a sum, both of which
    # propagate the infinity on their own.
    if any(math.isinf(v) for v in work):
        return math.inf

    slot_cap = max(MIN_SLOT_SECONDS, float(max_slot_seconds or 0.0))
    absorption = max(0.0, float(min_absorption_seconds or 0.0))
    remaining = [b for b in budgets if b > 0]
    last_finish: dict[int, float] = {}
    clock = 0.0

    while any(v > 0 for v in remaining):
        for i in range(len(remaining)):
            if remaining[i] <= 0:
                continue
            if absorption > 0 and i in last_finish:
                wait = absorption - (clock - last_finish[i])
                if wait > 0:
                    clock += wait
            slot = min(remaining[i], slot_cap)
            clock += slot
            remaining[i] -= slot
            last_finish[i] = clock
    return clock


def _grouped_station_wall_clock(
    members: list[ZoneRun],
    *,
    durations: dict[int, float] | None = None,
) -> float | None:
    """Wall clock of the station track under the CONTROLLER's own grouping.

    Returns None when the grouping cannot be applied, which the caller reads as
    "price this track the old way". That is all-or-nothing on purpose: with one
    member's group unknown, putting it in a unit of its own would let the track
    come out SHORTER than the controller may run it, and short is the direction
    that finishes after the deadline. Every other unknown here — an unavailable
    entity, old firmware, an OpenSprinkler integration that does not publish the
    attribute — arrives as the same None and takes the same branch.

    Within a sequential group the stations chain, and the controller inserts its
    station delay at each boundary — one fewer than the group has members, never
    after the last one. Groups run alongside each other, so the track is the
    longest of them. Members of :data:`PARALLEL_STATION_GROUP` serialise with
    nothing, so each is a unit by itself.
    """
    units: dict[object, list[float]] = {}
    delays: dict[object, float] = {}
    for index, run in enumerate(members):
        facts = run.station
        if facts is None or facts.group is None:
            return None
        budget = _budget(run, durations)
        if budget <= 0:
            # Carries no water, so it occupies no slot in the controller's queue
            # and adds no boundary for the delay to land on. ignore_demand plans
            # are built entirely of these.
            continue
        # Keyed by controller as well as group: the ids are numbered per
        # controller, so two controllers' group 0 are different groups and
        # merging them would price two concurrent chains as one long one.
        key = (
            (facts.controller_id, "parallel", index)
            if facts.group == PARALLEL_STATION_GROUP
            else (facts.controller_id, "sequential", facts.group)
        )
        units.setdefault(key, []).append(budget)
        # One controller per unit by construction of the key, so its members
        # agree on the delay and the first is the unit's.
        delays.setdefault(key, float(facts.delay_seconds or 0.0))

    longest = 0.0
    for key, work in units.items():
        clock = sum(work) + delays[key] * (len(work) - 1)
        longest = max(longest, max(0.0, clock))
    return longest


def concurrent_wall_clock(
    runs: list[ZoneRun],
    *,
    sequencing: str,
    max_slot_seconds: float,
    min_absorption_seconds: float,
    durations: dict[int, float] | None = None,
) -> float:
    """Wall-clock seconds ``runs`` occupy once split across dispatch tracks.

    :func:`simulate_wall_clock` answers for one track: it applies a single
    sequencing to everything handed to it. That is the right model only where
    every zone reaches its valve the same way. It is not, once a zone can be
    dispatched as a service call the hardware closes by itself or as a station
    the controller queues, because zone_sequencing does not govern either — see
    :data:`_TRACK_SEQUENCING`.

    Each track is reduced under its own sequencing and the answer is the LONGEST
    of them, because the tracks are started without being waited on. An install
    whose zones are all classic — the default, and everything predating the
    self-closing modes — has one track and collapses to the plain simulation, so
    its anchor times do not move.
    """
    tracks: dict[str, list[ZoneRun]] = {}
    for run in runs:
        tracks.setdefault(run.track or TRACK_CLASSIC, []).append(run)
    if not tracks:
        return 0.0

    clocks = []
    for track, members in tracks.items():
        clock = None
        if track == TRACK_STATION and sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL:
            # Only parallel hands the controller a queue to schedule. Under
            # sequential and rotating Smart Irrigation dispatches one station and
            # holds the rest until it finalises — see
            # ``async_dispatch_opensprinkler_zones`` — so the chain below is not
            # an assumption there, it is what runs, and the grouping cannot
            # change it.
            clock = _grouped_station_wall_clock(members, durations=durations)
        if clock is None:
            clock = simulate_wall_clock(
                members,
                sequencing=_TRACK_SEQUENCING.get(track, sequencing),
                max_slot_seconds=max_slot_seconds,
                min_absorption_seconds=min_absorption_seconds,
                durations=durations,
            )
        clocks.append(clock)
    return max(clocks)


def bound_wall_clock(
    runs: list[ZoneRun],
    *,
    sequencing: str,
    max_slot_seconds: float,
    min_absorption_seconds: float,
) -> float:
    """Longest wall clock the given zones could possibly occupy.

    Priced from each zone's configured ``maximum_duration`` — configuration,
    not a derived value — so ``target - bound`` is a fixed point the scheduler
    can arm days ahead, before any deficit is known. That is what gives the
    two-stage arm somewhere to stand when no earliest-start floor is set.

    The ceilings are combined through :func:`concurrent_wall_clock`, so the
    reduction is the same one the run itself is priced by. Being an
    over-estimate does not excuse the wrong rule: summing service zones that
    open together moves the decision point hours earlier than the arm needs,
    and taking the longest of stations the controller may chain moves it later
    than it can afford.
    """
    ceilings = {}
    for r in runs:
        cap = r.maximum_duration
        try:
            cap = float(cap) if cap is not None else 0.0
        except (TypeError, ValueError):
            cap = 0.0
        if cap > 0:
            # duration_from_deficit clamps to maximum_duration and adds the
            # lead time AFTER the clamp, so the cap alone under-states the
            # zone by exactly its lead time. An under-estimate here finishes
            # the irrigation after the requested time.
            # A caller-supplied ceiling already folds the lead time in, so
            # only this branch has to add it back.
            try:
                lead = float(r.lead_time or 0.0)
            except (TypeError, ValueError):
                lead = 0.0
            cap += max(0.0, lead)
        else:
            # No configured cap, so this zone is genuinely unbounded unless the
            # caller can supply a ceiling from somewhere this module cannot
            # see. Infinity rather than a stand-in number: a caller arming a
            # run against `target - bound` has to be able to tell "no fixed
            # point exists here" from "the fixed point is 4 hours back", and a
            # constant collapses those two into a wrong answer that looks fine.
            try:
                derived = float(r.ceiling) if r.ceiling is not None else 0.0
            except (TypeError, ValueError):
                derived = 0.0
            cap = derived if derived > 0 else math.inf
        # Keyed by zone id because that is ``durations``' contract, so two
        # runs sharing an id land on one entry. Take the longer rather than
        # letting the last one win: a collision that shortens the bound is
        # the direction that overruns the finish.
        ceilings[r.zone_id] = max(ceilings.get(r.zone_id, 0.0), cap)
    return concurrent_wall_clock(
        runs,
        sequencing=sequencing,
        max_slot_seconds=max_slot_seconds,
        min_absorption_seconds=min_absorption_seconds,
        durations=ceilings,
    )


def select(
    runs: list[ZoneRun],
    *,
    window_seconds: float,
    sequencing: str,
    max_slot_seconds: float,
    min_absorption_seconds: float,
) -> list[ZoneRun]:
    """The zones to water tonight, in the order to water them.

    Take the largest ranked prefix whose *simulated* clock fits the window,
    then fill any residual gap with lower-ranked zones that still fit. Prefixes
    are simulated rather than subtracted because the clock is not a running sum
    of durations: under rotating it carries absorption pauses, and across
    dispatch tracks a zone costs only what it adds to its own — see
    :func:`concurrent_wall_clock`.

    Zones tied on depletion ratio (to :data:`RATIO_TIE_DECIMALS`) form one
    group, and within a group the subset that delivers the most watering
    seconds into the window wins — among equally-due zones there is no dryness
    argument for one over another, so rotation order deciding between a partial
    fill and a complete one was a coin flip paid in wasted window. Equal
    utilization falls back to the longest-unwatered members, so the rotation
    instinct survives as the final tie-break. With no ties every group is a
    singleton and this is exactly the old largest-prefix-plus-gap-fill rule.

    Dryness still owns the window ACROSS groups: when nothing in the driest
    group fits, its tie-broken leader runs anyway and the run deadline cuts it
    where it stands — a wetter zone must never water ahead of a drier one that
    could not fit, or the driest zone would starve forever. A *tied* zone that
    loses the packing tonight dries past its group, becomes that strict leader,
    and the same rule then guarantees it water. Selection excludes; the
    deadline truncates.

    Candidates are priced by :func:`concurrent_wall_clock`, so a zone costs
    only what it adds to its OWN dispatch track. A station sitting inside a
    longer classic track is therefore free, and is admitted: it genuinely does
    fit, and refusing it would idle capacity no other zone could have claimed.
    That reads as a wetter zone gaining on a drier one, and is not — the groups
    are still settled driest first, so a wetter zone only ever fills what the
    driest group left, and the leader rule above still hands the whole window
    to a strict leader that could not fit. The packing score stays total
    watering seconds for the same reason: with the fit already priced per
    track, the most water delivered into a fixed wall clock is what a subset
    should be judged on.
    """
    ranked = rank(runs)
    if not ranked:
        return []

    def fits(candidate: list[ZoneRun]) -> bool:
        return (
            concurrent_wall_clock(
                candidate,
                sequencing=sequencing,
                max_slot_seconds=max_slot_seconds,
                min_absorption_seconds=min_absorption_seconds,
            )
            <= window_seconds
        )

    # Contiguity needs no sort of its own: rounding is monotone, so zones
    # sharing a rounded ratio are adjacent in the exact-ratio ranking.
    groups: list[list[ZoneRun]] = []
    last_key = None
    for r in ranked:
        key = round(r.depletion_ratio, RATIO_TIE_DECIMALS)
        if groups and key == last_key:
            groups[-1].append(r)
        else:
            groups.append([r])
            last_key = key
    # Within a group the sub-quantum ratio difference is exactly the noise the
    # rounding neutralizes — order members by the tie-break alone, or float
    # residue would still decide the execution order.
    for group in groups:
        group.sort(key=lambda r: (_epoch(r.last_irrigation), r.zone_id))

    chosen: list[ZoneRun] = []
    for index, group in enumerate(groups):
        subset = _best_fitting_subset(chosen, group, fits)
        if index == 0 and not subset:
            # Nothing in the driest group fits at all — the leader runs anyway
            # and the deadline truncates it. Lower groups are NOT consulted.
            #
            # The group's own leader, not ``ranked[0]``. Members were re-sorted
            # by the tie-break a few lines above precisely so sub-quantum ratio
            # residue could not decide execution order, and ``ranked[0]`` is
            # that residue. This branch hands the entire window to one zone on
            # the tightest nights, so it is the last place that should be
            # settled by the noise the grouping exists to discard.
            return [groups[0][0]]
        chosen = [*chosen, *subset]
    return chosen


def nominal_zone_duration(zone: dict, metric: bool) -> float:
    """Seconds ``zone`` would need on a night it is exactly due (ratio 1.0).

    Prices the zone's own allowed depletion — its ``bucket_threshold``, the
    depth at which ``bucket / bucket_threshold`` reaches 1.0 and the zone
    triggers — through the same :func:`duration_math.zone_run_duration` a
    real run prices its live deficit with, so the precipitation-rate math and
    the maximum-duration cap are identical to what a real run applies, not a
    second guess at them. Unlike a real duration this never reads the zone's
    live ``bucket``: the threshold is configuration, so the answer does not
    move when the bucket does. Mirrors ``duration_from_deficit``'s own
    ``deficit >= 0`` guard for a non-negative (never-gating) threshold.
    """
    threshold = zone.get(const.ZONE_BUCKET_THRESHOLD) or 0
    return float(zone_run_duration(zone, threshold, metric))


def zone_eligible_for_demand(zone: dict) -> bool:
    """Whether ``zone`` counts toward nominal (or planned) demand.

    Mirrors the filter in ``IrrigationMixin.async_plan_zone_runs``: a
    disabled zone is never run, and a distributor member waters through its
    distributor's own cycle rather than directly, so neither belongs in a
    schedule's own wall clock. A standalone predicate rather than inlined
    into :func:`nominal_demand_seconds` so the live plan and the nominal
    projection apply literally the same test instead of two hand-written
    copies of it.
    """
    return (
        zone.get(const.ZONE_DISTRIBUTOR_ID) is None
        and zone.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
    )


def nominal_demand_seconds(
    zones: list[dict],
    *,
    sequencing: str,
    max_slot_seconds: float,
    min_absorption_seconds: float,
    metric: bool,
    station_facts: dict[int, StationFacts] | None = None,
) -> float:
    """Wall-clock seconds a schedule's run takes on a typical night.

    "Typical" means every eligible zone is priced as if it were exactly due
    (depletion ratio 1.0) rather than at its actual live bucket — see
    :func:`nominal_zone_duration`. The per-zone durations are combined exactly
    as a real run would combine them, through :func:`concurrent_wall_clock` —
    each dispatch track under its own sequencing, including rotating's
    absorption pauses, and the longest track winning. That is the same
    reduction the finish anchor uses, which is the point: the run length the
    dial draws is the wall clock the schedule actually reserves. The result
    never reads a live bucket, so it does not change when one does — that is
    the property distinguishing it from demand.

    Zones are ordered by id, not by :func:`rank`: rank's tie-break reads
    ``last_irrigation``, a live value, and this projection is meant to hold
    steady across anything except a configuration change.

    ``station_facts`` maps zone id to what the controller says about that
    zone's station — this module cannot read an entity, so its HA-side callers
    supply it. Omitted, every station is unread and the station track is priced
    as a chain, which is what it was priced as before any of it could be read.
    A controller's grouping is configuration too, so using it here does not
    make the projection any less steady than the sequencing already does.
    """
    eligible = sorted(
        (z for z in zones if zone_eligible_for_demand(z)),
        key=lambda z: int(z.get(const.ZONE_ID)),
    )
    runs = [
        ZoneRun(
            zone_id=int(z.get(const.ZONE_ID)),
            duration=nominal_zone_duration(z, metric),
            depletion_ratio=1.0,
            last_irrigation=None,
            maximum_duration=z.get(const.ZONE_MAXIMUM_DURATION),
            track=track_for_zone(z),
            station=(station_facts or {}).get(int(z.get(const.ZONE_ID))),
        )
        for z in eligible
    ]
    return concurrent_wall_clock(
        runs,
        sequencing=sequencing,
        max_slot_seconds=max_slot_seconds,
        min_absorption_seconds=min_absorption_seconds,
    )


def _best_fitting_subset(chosen, group, fits):
    """The subset of one tie group that best uses the remaining window.

    Most watering seconds first; among equals, the members longest unwatered
    (lexicographic on their sorted last-irrigation epochs — a never-watered
    zone reads oldest); zone ids settle the rest deterministically. Members
    keep their ranked order, so the execution order the caller accumulates is
    the ranking's.

    A group past :data:`MAX_TIE_GROUP_EXHAUSTIVE` falls back to greedy
    add-in-rank-order — 2^k simulations stop being cheap somewhere, and a
    single-figure zone count never gets there.
    """
    if len(group) == 1:
        return group if fits([*chosen, *group]) else []
    if len(group) > MAX_TIE_GROUP_EXHAUSTIVE:
        subset = []
        for member in group:
            if fits([*chosen, *subset, member]):
                subset.append(member)
        return subset

    best: list[ZoneRun] = []
    best_score = None
    for mask in range(1, 1 << len(group)):
        subset = [m for bit, m in enumerate(group) if mask >> bit & 1]
        if not fits([*chosen, *subset]):
            continue
        # Negated epochs/ids so that on equal watering seconds the plain
        # max() comparison prefers older members, then smaller zone ids.
        score = (
            sum(m.duration or 0.0 for m in subset),
            tuple(sorted((-_epoch(m.last_irrigation) for m in subset), reverse=True)),
            tuple(sorted((-m.zone_id for m in subset), reverse=True)),
        )
        if best_score is None or score > best_score:
            best, best_score = subset, score
    return best
