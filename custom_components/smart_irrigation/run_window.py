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
replays the runner's own loop instead.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from . import const
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

# The sequencing each non-classic track behaves as, whatever zone_sequencing
# says. Expressed as a sequencing rather than as max()/sum() so all three tracks
# price through the one simulate_wall_clock, including its rotating model.
#
#   service  — parallel. _dispatch_by_mode fires every service-mode zone in a
#     single loop and the hardware owns each close, so they open together.
#   station  — sequential. Under sequential/rotating Smart Irrigation chains the
#     stations itself; under parallel it hands the controller everything at once
#     and whether a station waits for the ones queued ahead of it is a flag in
#     the CONTROLLER's own configuration, which this integration cannot read.
#     Both orderings are possible, and only the longer is safe to anchor on: an
#     under-estimate finishes the irrigation after the requested time.
_TRACK_SEQUENCING = {
    TRACK_SELF_CLOSING: const.CONF_ZONE_SEQUENCING_PARALLEL,
    TRACK_STATION: const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
}

# The runner's own safety cap for a zone with no usable maximum_duration
# (irrigation.py applies `or 14400` in every slot/safety computation). Mirrored
# here so the bound below never under-states a zone the runner would still run.
RUN_CEILING_SECONDS = 14400

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
    """

    zone_id: int
    duration: float
    depletion_ratio: float
    last_irrigation: datetime.datetime | str | None = None
    maximum_duration: float | None = None
    track: str = TRACK_CLASSIC


def track_for_zone(zone: dict) -> str:
    """Which dispatch track ``zone`` runs on.

    Station first: an OpenSprinkler zone is self-closing too, and its own track
    is the more specific answer.
    """
    if is_opensprinkler_zone(zone):
        return TRACK_STATION
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
    budget = {
        r.zone_id: float((durations or {}).get(r.zone_id, r.duration) or 0.0)
        for r in runs
    }
    work = [b for b in budget.values() if b > 0]
    if not work:
        return 0.0

    if sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL:
        return max(work)
    if sequencing != const.CONF_ZONE_SEQUENCING_ROTATING:
        return sum(work)

    # Rotating: replay irrigation._run_rotation's loop. A zone that is finished
    # is skipped BEFORE its absorption wait is considered, exactly as there, so
    # a completed zone never charges a trailing pause.
    slot_cap = max(MIN_SLOT_SECONDS, float(max_slot_seconds or 0.0))
    absorption = max(0.0, float(min_absorption_seconds or 0.0))
    remaining = {zid: b for zid, b in budget.items() if b > 0}
    order = [r.zone_id for r in runs if remaining.get(r.zone_id, 0.0) > 0]
    last_finish: dict[int, float] = {}
    clock = 0.0

    while any(v > 0 for v in remaining.values()):
        for zid in order:
            if remaining[zid] <= 0:
                continue
            if absorption > 0 and zid in last_finish:
                wait = absorption - (clock - last_finish[zid])
                if wait > 0:
                    clock += wait
            slot = min(remaining[zid], slot_cap)
            clock += slot
            remaining[zid] -= slot
            last_finish[zid] = clock
    return clock


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
    return max(
        simulate_wall_clock(
            members,
            sequencing=_TRACK_SEQUENCING.get(track, sequencing),
            max_slot_seconds=max_slot_seconds,
            min_absorption_seconds=min_absorption_seconds,
            durations=durations,
        )
        for track, members in tracks.items()
    )


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
    """
    ceilings = {}
    for r in runs:
        cap = r.maximum_duration
        try:
            cap = float(cap) if cap is not None else 0.0
        except (TypeError, ValueError):
            cap = 0.0
        ceilings[r.zone_id] = cap if cap > 0 else float(RUN_CEILING_SECONDS)
    return simulate_wall_clock(
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
    are simulated rather than subtracted because the rotating clock is not a
    running sum of durations — see :func:`simulate_wall_clock`.

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
    """
    ranked = rank(runs)
    if not ranked:
        return []

    def fits(candidate: list[ZoneRun]) -> bool:
        return (
            simulate_wall_clock(
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
            return [ranked[0]]
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
