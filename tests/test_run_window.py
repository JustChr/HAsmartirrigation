"""Fitting a run into the window before its finish anchor (run_window.py).

Pure arithmetic — no Home Assistant, no coordinator, no store. Every expected
wall clock below is hand-computed against the rotating runner's own loop
(``irrigation._run_rotation``), because that arithmetic is the whole reason
this module exists: under rotating, ``sum(durations)`` is not the wall clock.
"""

import datetime

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.run_window import (
    RUN_CEILING_SECONDS,
    ZoneRun,
    bound_wall_clock,
    nominal_demand_seconds,
    nominal_zone_duration,
    rank,
    select,
    simulate_wall_clock,
    zone_eligible_for_demand,
)

SEQUENTIAL = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
PARALLEL = const.CONF_ZONE_SEQUENCING_PARALLEL
ROTATING = const.CONF_ZONE_SEQUENCING_ROTATING


def _run(zone_id, duration, ratio=1.0, last=None, maximum=None):
    return ZoneRun(
        zone_id=zone_id,
        duration=duration,
        depletion_ratio=ratio,
        last_irrigation=last,
        maximum_duration=maximum,
    )


def _sim(runs, sequencing, slot=300.0, absorb=0.0):
    return simulate_wall_clock(
        runs,
        sequencing=sequencing,
        max_slot_seconds=slot,
        min_absorption_seconds=absorb,
    )


class TestSimulateWallClock:
    """The sequencing-aware wall-clock model."""

    def test_sequential_sums(self):
        runs = [_run(0, 300), _run(1, 600), _run(2, 120)]
        assert _sim(runs, SEQUENTIAL) == 1020

    def test_parallel_takes_the_longest(self):
        runs = [_run(0, 300), _run(1, 600), _run(2, 120)]
        assert _sim(runs, PARALLEL) == 600

    def test_empty_selection_is_zero(self):
        for sequencing in (SEQUENTIAL, PARALLEL, ROTATING):
            assert _sim([], sequencing) == 0

    def test_rotating_without_absorption_sums(self):
        # No pauses, so slicing into slots reorders the water but not the clock.
        runs = [_run(0, 900), _run(1, 600)]
        assert _sim(runs, ROTATING, slot=300, absorb=0) == 1500

    def test_rotating_charges_the_absorption_pause(self):
        # One zone, 600 s in two 300 s slots, 600 s absorption between them:
        # slot 0-300, wait 300-900, slot 900-1200. sum(durations) says 600.
        runs = [_run(0, 600)]
        assert _sim(runs, ROTATING, slot=300, absorb=600) == 1200

    def test_rotating_ring_partially_fills_the_pause(self):
        # A 0-300; B 300-600 (done); A waits until 300+600=900, runs 900-1200.
        # B's slot is free — it happened inside A's pause.
        runs = [_run(0, 600), _run(1, 300)]
        assert _sim(runs, ROTATING, slot=300, absorb=600) == 1200

    def test_rotating_two_full_zones_leave_one_residual_pause(self):
        # A 0-300, B 300-600, A waits to 900 then 900-1200 (done),
        # B's pause has already elapsed so B runs 1200-1500.
        runs = [_run(0, 600), _run(1, 600)]
        assert _sim(runs, ROTATING, slot=300, absorb=600) == 1500

    def test_rotating_a_longer_ring_pushes_the_dominant_zone_out(self):
        # A needs 4 slots; B, C, D need one each. The ring is long enough that
        # A's first pause is fully absorbed, but the extra zones delay A's
        # second slot past where it would have started alone: 3300 vs 3000.
        # This is why a running subtraction cannot size a rotating run.
        big = [_run(0, 1200), _run(1, 300), _run(2, 300), _run(3, 300)]
        assert _sim(big, ROTATING, slot=300, absorb=600) == 3300
        assert _sim([_run(0, 1200)], ROTATING, slot=300, absorb=600) == 3000

    def test_rotating_never_shortens_when_a_zone_is_added(self):
        # Each zone's slot start is max(loop arrival, own finish + absorption),
        # and both only move later as work is added — so the simulated clock is
        # monotonic in the selection. Selection may therefore stop growing at
        # the first prefix that overruns, and the deadline stays a safety net
        # rather than a routine cut.
        base = [_run(0, 900), _run(1, 450)]
        grown = [*base, _run(2, 700)]
        assert _sim(grown, ROTATING, slot=300, absorb=600) >= _sim(
            base, ROTATING, slot=300, absorb=600
        )

    def test_rotating_slot_floor_of_one_second(self):
        # A zero/negative configured slot would divide the run into zero-length
        # slots and spin forever; the model floors it exactly as the runner does.
        assert _sim([_run(0, 5)], ROTATING, slot=0, absorb=0) == 5


class TestRank:
    """Priority order: depletion ratio, then longest since last watered."""

    def test_orders_by_depletion_ratio_descending(self):
        runs = [_run(0, 300, ratio=1.2), _run(1, 300, ratio=2.0), _run(2, 300, ratio=1.5)]
        assert [r.zone_id for r in rank(runs)] == [1, 2, 0]

    def test_ties_break_on_oldest_last_irrigation(self):
        # Ties are the steady state here: zones sharing a sensor group with
        # equal thresholds converge to identical buckets, so the tie-break
        # decides the whole rotation.
        old = datetime.datetime(2026, 8, 1, 6, 0)
        recent = datetime.datetime(2026, 8, 5, 6, 0)
        runs = [_run(0, 300, ratio=1.5, last=recent), _run(1, 300, ratio=1.5, last=old)]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_a_never_watered_zone_leads_its_tie(self):
        watered = datetime.datetime(2026, 8, 1, 6, 0)
        runs = [_run(0, 300, ratio=1.5, last=watered), _run(1, 300, ratio=1.5, last=None)]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_aware_and_naive_timestamps_compare(self):
        # last_irrigation is written with dt_util.now() (aware), but a zone
        # hydrated from older storage can carry a naive one. Mixing them must
        # not raise — a TypeError here would abort the whole run.
        aware = datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.timezone.utc)
        naive = datetime.datetime(2026, 8, 4, 6, 0)
        runs = [_run(0, 300, ratio=1.5, last=naive), _run(1, 300, ratio=1.5, last=aware)]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_a_stored_iso_stamp_orders_like_a_datetime(self):
        # store.async_get_zones returns attr.asdict of an entry hydrated from
        # JSON, so after any restart last_irrigation is an ISO STRING; only a
        # stamp written in the current process is still a datetime. Reading the
        # string shape as "never watered" is quieter than raising and worse: it
        # collapses this tie-break to zone id on every install that has been
        # restarted, which is all of them.
        old = "2026-08-01T06:00:00-04:00"
        recent = "2026-08-05T06:00:00-04:00"
        runs = [_run(0, 300, ratio=1.5, last=recent), _run(1, 300, ratio=1.5, last=old)]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_a_stored_string_and_a_live_datetime_compare(self):
        # The mix is the normal state mid-run: the zone the runner just watered
        # carries a datetime while every other zone still carries its string.
        stored = "2026-08-01T06:00:00+00:00"
        live = datetime.datetime(2026, 8, 5, 6, 0, tzinfo=datetime.timezone.utc)
        runs = [_run(0, 300, ratio=1.5, last=live), _run(1, 300, ratio=1.5, last=stored)]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_an_unparseable_stamp_reads_as_never_watered(self):
        runs = [
            _run(0, 300, ratio=1.5, last="2026-08-05T06:00:00+00:00"),
            _run(1, 300, ratio=1.5, last="not a timestamp"),
        ]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_zone_id_is_the_final_tie_break(self):
        runs = [_run(2, 300, ratio=1.5), _run(0, 300, ratio=1.5), _run(1, 300, ratio=1.5)]
        assert [r.zone_id for r in rank(runs)] == [0, 1, 2]

    def test_does_not_mutate_the_input(self):
        runs = [_run(0, 300, ratio=1.0), _run(1, 300, ratio=9.0)]
        rank(runs)
        assert [r.zone_id for r in runs] == [0, 1]


class TestSelect:
    """Largest fitting prefix, then gap-fill."""

    def _select(self, runs, window, sequencing=SEQUENTIAL, slot=300.0, absorb=0.0):
        return select(
            runs,
            window_seconds=window,
            sequencing=sequencing,
            max_slot_seconds=slot,
            min_absorption_seconds=absorb,
        )

    def test_everything_fits(self):
        runs = [_run(0, 300, ratio=2.0), _run(1, 600, ratio=1.5)]
        assert [r.zone_id for r in self._select(runs, 3600)] == [0, 1]

    def test_truncates_to_the_largest_fitting_prefix(self):
        runs = [
            _run(0, 600, ratio=3.0),
            _run(1, 600, ratio=2.0),
            _run(2, 600, ratio=1.5),
        ]
        assert [r.zone_id for r in self._select(runs, 1300)] == [0, 1]

    def test_gap_fill_takes_a_lower_ranked_zone_that_still_fits(self):
        # Zone 1 (600 s) overruns the 900 s window after zone 0, but zone 2
        # (200 s) fits in the residual gap. The skipped zone is drier tomorrow
        # and sorts ahead, so nothing starves.
        runs = [
            _run(0, 600, ratio=3.0),
            _run(1, 600, ratio=2.0),
            _run(2, 200, ratio=1.5),
        ]
        assert [r.zone_id for r in self._select(runs, 900)] == [0, 2]

    def test_gap_fill_preserves_priority_order_of_what_it_adds(self):
        runs = [
            _run(0, 600, ratio=4.0),
            _run(1, 900, ratio=3.0),
            _run(2, 150, ratio=2.0),
            _run(3, 150, ratio=1.5),
        ]
        assert [r.zone_id for r in self._select(runs, 900)] == [0, 2, 3]

    def test_the_driest_zone_is_never_excluded_outright(self):
        # A zone whose full duration exceeds the entire window still runs; the
        # deadline truncates it where it stands and the residual carries.
        # Excluding it instead would starve it every single night.
        runs = [_run(0, 9000, ratio=3.0), _run(1, 300, ratio=1.5)]
        assert [r.zone_id for r in self._select(runs, 600)] == [0]

    def test_no_due_zones_selects_nothing(self):
        assert self._select([], 3600) == []

    def test_parallel_fits_on_the_longest_zone(self):
        runs = [_run(0, 900, ratio=3.0), _run(1, 800, ratio=2.0)]
        assert [r.zone_id for r in self._select(runs, 850, PARALLEL)] == [0]

    def test_rotating_selection_is_sized_by_simulation_not_by_sum(self):
        # sum(durations) is 600 and would "fit" a 900 s window; the real
        # rotating clock is 1200 s because of the absorption pause, so only
        # the leader is selected and the deadline handles the rest.
        runs = [_run(0, 600, ratio=3.0), _run(1, 600, ratio=2.0)]
        chosen = self._select(runs, 900, ROTATING, slot=300, absorb=600)
        assert [r.zone_id for r in chosen] == [0]

    def test_window_of_zero_still_returns_the_leader(self):
        runs = [_run(0, 300, ratio=3.0), _run(1, 300, ratio=2.0)]
        assert [r.zone_id for r in self._select(runs, 0)] == [0]


class TestSelectTiePacking:
    """Within a ratio tie, pack the window instead of following rotation order.

    Ties are the steady state here (identical buckets under a shared sensor
    group), and among equally-due zones there is no dryness argument for one
    over another — so the subset that wastes the least window wins. A tied zone
    skipped tonight dries past its group, becomes the strict leader, and the
    always-include-the-leader rule then guarantees it water; utilization never
    overrides dryness ACROSS groups.
    """

    def _select(self, runs, window, sequencing=SEQUENTIAL, slot=300.0, absorb=0.0):
        return select(
            runs,
            window_seconds=window,
            sequencing=sequencing,
            max_slot_seconds=slot,
            min_absorption_seconds=absorb,
        )

    def _tied(self, zone_id, duration, last_days_ago):
        return _run(
            zone_id,
            duration,
            ratio=1.2,
            last=datetime.datetime(2026, 8, 1) - datetime.timedelta(last_days_ago),
        )

    def test_tied_pair_that_packs_the_window_beats_the_rotation_leader(self):
        # A (2400) cannot fit at all, B (1700) wastes 300, C+D (1900) waste
        # 100. Rotation order alone would pick A and hand the whole night to a
        # partial fill; packing picks C+D.
        runs = [
            self._tied(0, 2400, last_days_ago=4),  # A - rotation leader
            self._tied(1, 1700, last_days_ago=3),  # B
            self._tied(2, 1000, last_days_ago=2),  # C
            self._tied(3, 900, last_days_ago=1),  # D
        ]
        assert [r.zone_id for r in self._select(runs, 2000)] == [2, 3]

    def test_equal_utilization_prefers_the_longest_unwatered(self):
        runs = [
            self._tied(0, 1000, last_days_ago=1),
            self._tied(1, 1000, last_days_ago=5),
        ]
        assert [r.zone_id for r in self._select(runs, 1000)] == [1]

    def test_a_drier_group_still_owns_the_window(self):
        # The strictly driest zone does not fit; a wetter zone would. Dryness
        # priority holds: the leader runs and the deadline truncates it —
        # otherwise the driest zone starves forever behind fitting wet ones.
        runs = [
            _run(0, 2400, ratio=1.5),
            _run(1, 500, ratio=1.2),
        ]
        assert [r.zone_id for r in self._select(runs, 2000)] == [0]

    def test_packing_is_constrained_by_the_rotating_simulation(self):
        # Sum of the tied pair (1200) fits 1400, but the rotating clock is
        # 1500 (residual absorption pause), so only one fits — the older.
        runs = [
            self._tied(0, 600, last_days_ago=1),
            self._tied(1, 600, last_days_ago=3),
        ]
        chosen = self._select(runs, 1400, ROTATING, slot=300, absorb=600)
        assert [r.zone_id for r in chosen] == [1]

    def test_near_ties_within_rounding_noise_pack_too(self):
        # Ratios differing past the second decimal are the same dryness — not
        # a meaningful distinction, just rounding residue — so they pack
        # rather than letting float noise decide the night.
        runs = [
            _run(0, 2400, ratio=1.203),
            _run(1, 1000, ratio=1.201),
            _run(2, 900, ratio=1.202),
        ]
        assert [r.zone_id for r in self._select(runs, 2000)] == [1, 2]

    def test_distinct_ratios_keep_prefix_and_gap_fill_semantics(self):
        # No ties -> identical behaviour to the prefix + gap-fill rule.
        runs = [
            _run(0, 600, ratio=3.0),
            _run(1, 600, ratio=2.0),
            _run(2, 200, ratio=1.5),
        ]
        assert [r.zone_id for r in self._select(runs, 900)] == [0, 2]

    def test_lower_group_fills_what_the_packed_tie_leaves(self):
        # After the tied pair packs 1900 of 2300, a wetter singleton (400)
        # still gap-fills the residual.
        runs = [
            self._tied(0, 2400, last_days_ago=4),
            self._tied(2, 1000, last_days_ago=2),
            self._tied(3, 900, last_days_ago=1),
            _run(5, 400, ratio=1.05),
        ]
        assert [r.zone_id for r in self._select(runs, 2300)] == [2, 3, 5]


class TestBoundWallClock:
    """The duration-independent ceiling that fixes the decision point."""

    def test_sums_configured_maximums_under_sequential(self):
        runs = [_run(0, 100, maximum=4800), _run(1, 100, maximum=3000)]
        assert bound_wall_clock(
            runs,
            sequencing=SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        ) == 7800

    def test_an_unset_maximum_falls_back_to_the_runner_ceiling(self):
        runs = [_run(0, 100, maximum=None), _run(1, 100, maximum=0)]
        assert bound_wall_clock(
            runs,
            sequencing=SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        ) == 2 * RUN_CEILING_SECONDS

    def test_ignores_the_live_duration_entirely(self):
        # The bound must be knowable days ahead, so it reads configuration only.
        # Same maximums, wildly different current durations, same bound.
        lo = [_run(0, 1, maximum=4800)]
        hi = [_run(0, 4800, maximum=4800)]
        kwargs = {
            "sequencing": SEQUENTIAL,
            "max_slot_seconds": 300,
            "min_absorption_seconds": 0,
        }
        assert bound_wall_clock(lo, **kwargs) == bound_wall_clock(hi, **kwargs) == 4800

    def test_counts_rotating_absorption_structure(self):
        # 4800 s at 300 s slots with a 600 s pause is nothing like 4800 s.
        runs = [_run(0, 100, maximum=4800)]
        bound = bound_wall_clock(
            runs,
            sequencing=ROTATING,
            max_slot_seconds=300,
            min_absorption_seconds=600,
        )
        assert bound == 4800 + 15 * 600


def _zone(
    zone_id,
    *,
    threshold=-10.0,
    throughput=10.0,
    size=10.0,
    multiplier=1.0,
    maximum=None,
    lead_time=0,
    bucket=0.0,
    state=const.ZONE_STATE_AUTOMATIC,
    distributor_id=None,
):
    """A minimal zone dict — only the fields the duration math and the
    eligibility filter read. Precipitation rate is fixed at 60 mm/h
    (10 l/min over 10 m2) unless overridden, so a threshold of -N mm prices to
    N/60*3600 = N*60 seconds — the numbers below are chosen to land on the
    same wall-clock fixtures ``TestSimulateWallClock`` already pins by hand.
    """
    return {
        const.ZONE_ID: zone_id,
        const.ZONE_BUCKET_THRESHOLD: threshold,
        const.ZONE_THROUGHPUT: throughput,
        const.ZONE_SIZE: size,
        const.ZONE_MULTIPLIER: multiplier,
        const.ZONE_MAXIMUM_DURATION: maximum,
        const.ZONE_LEAD_TIME: lead_time,
        const.ZONE_BUCKET: bucket,
        const.ZONE_STATE: state,
        const.ZONE_DISTRIBUTOR_ID: distributor_id,
    }


class TestNominalZoneDuration:
    """Pricing a single zone's own allowed depletion at ratio 1.0."""

    def test_prices_the_threshold_like_a_real_deficit(self):
        # Same numbers as test_live_duration's duration_from_deficit(-10, 10,
        # 10, 1.0, 36000, 0, metric=True) == 600 — nominal pricing must not
        # diverge from the real duration math for the same deficit.
        zone = _zone(0, threshold=-10.0, maximum=36000, lead_time=0)
        assert nominal_zone_duration(zone, metric=True) == 600.0

    def test_the_cap_bites_when_the_uncapped_duration_exceeds_it(self):
        # Uncapped this threshold prices to 6000 s (100 mm at 60 mm/h); the
        # 300 s maximum_duration must cut it, exactly as a real run's cap does.
        zone = _zone(0, threshold=-100.0, maximum=300, lead_time=0)
        assert nominal_zone_duration(zone, metric=True) == 300.0

    def test_a_non_negative_threshold_never_gates(self):
        zone = _zone(0, threshold=0.0)
        assert nominal_zone_duration(zone, metric=True) == 0.0

    def test_independent_of_the_zones_live_bucket(self):
        # The property distinguishing nominal demand from demand: the same
        # configuration prices to the same duration no matter what the zone's
        # live bucket currently reads.
        dry = _zone(0, threshold=-10.0, bucket=-9.9)
        wet = _zone(0, threshold=-10.0, bucket=0.0)
        assert nominal_zone_duration(dry, metric=True) == nominal_zone_duration(
            wet, metric=True
        )


class TestZoneEligibleForDemand:
    """Same exclusions ``async_plan_zone_runs`` applies."""

    def test_a_disabled_zone_is_excluded(self):
        zone = _zone(0, state=const.ZONE_STATE_DISABLED)
        assert zone_eligible_for_demand(zone) is False

    def test_a_distributor_member_is_excluded(self):
        zone = _zone(0, distributor_id="dist_1")
        assert zone_eligible_for_demand(zone) is False

    def test_an_ordinary_automatic_zone_is_included(self):
        zone = _zone(0, state=const.ZONE_STATE_AUTOMATIC)
        assert zone_eligible_for_demand(zone) is True


class TestNominalDemandSeconds:
    """Combining nominal per-zone durations under the schedule's sequencing."""

    def _kwargs(self, sequencing, slot=300.0, absorb=0.0):
        return {
            "sequencing": sequencing,
            "max_slot_seconds": slot,
            "min_absorption_seconds": absorb,
            "metric": True,
        }

    def test_parallel_takes_the_longest_nominal_duration(self):
        zones = [_zone(0, threshold=-10.0), _zone(1, threshold=-5.0)]
        # thresholds -10/-5 mm at 60 mm/h price to 600/300 s.
        assert nominal_demand_seconds(zones, **self._kwargs(PARALLEL)) == 600.0

    def test_sequential_sums_nominal_durations(self):
        zones = [_zone(0, threshold=-10.0), _zone(1, threshold=-5.0)]
        assert nominal_demand_seconds(zones, **self._kwargs(SEQUENTIAL)) == 900.0

    def test_rotating_replays_the_absorption_pause(self):
        # Same 600 s / 300 s pair as
        # TestSimulateWallClock.test_rotating_ring_partially_fills_the_pause:
        # A 0-300, B 300-600 (done), A waits to 900, A 900-1200. == 1200.
        zones = [_zone(0, threshold=-10.0), _zone(1, threshold=-5.0)]
        assert (
            nominal_demand_seconds(zones, **self._kwargs(ROTATING, slot=300, absorb=600))
            == 1200.0
        )

    def test_excludes_disabled_and_distributor_zones_from_the_total(self):
        zones = [
            _zone(0, threshold=-10.0),
            _zone(1, threshold=-5.0, state=const.ZONE_STATE_DISABLED),
            _zone(2, threshold=-5.0, distributor_id="dist_1"),
        ]
        # Only zone 0 counts — the disabled zone and the distributor member
        # are excluded on the same terms async_plan_zone_runs excludes them.
        assert nominal_demand_seconds(zones, **self._kwargs(PARALLEL)) == 600.0

    def test_the_cap_bites_inside_the_combined_total(self):
        zones = [
            _zone(0, threshold=-100.0, maximum=300),  # capped 6000 -> 300
            _zone(1, threshold=-5.0),  # 300, uncapped
        ]
        assert nominal_demand_seconds(zones, **self._kwargs(SEQUENTIAL)) == 600.0

    def test_independent_of_every_zones_live_bucket(self):
        dry = [_zone(0, threshold=-10.0, bucket=-9.9), _zone(1, threshold=-5.0, bucket=-4.9)]
        wet = [_zone(0, threshold=-10.0, bucket=0.0), _zone(1, threshold=-5.0, bucket=0.0)]
        for sequencing in (PARALLEL, SEQUENTIAL, ROTATING):
            kwargs = self._kwargs(sequencing, slot=300, absorb=600)
            assert nominal_demand_seconds(dry, **kwargs) == nominal_demand_seconds(
                wet, **kwargs
            )
