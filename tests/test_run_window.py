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
    rank,
    select,
    simulate_wall_clock,
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
