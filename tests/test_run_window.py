"""Fitting a run into the window before its finish anchor (run_window.py).

Pure arithmetic — no Home Assistant, no coordinator, no store. Every expected
wall clock below is hand-computed against the rotating runner's own loop
(``irrigation._run_rotation``), because that arithmetic is the whole reason
this module exists: under rotating, ``sum(durations)`` is not the wall clock.
"""

import datetime
import itertools
import math
import random

import pytest

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.duration_math import duration_from_deficit
from custom_components.smart_irrigation.run_window import (
    PARALLEL_STATION_GROUP,
    TRACK_CLASSIC,
    TRACK_SELF_CLOSING,
    TRACK_STATION,
    StationFacts,
    ZoneRun,
    bound_wall_clock,
    concurrent_wall_clock,
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


def _run(
    zone_id,
    duration,
    ratio=1.0,
    last=None,
    maximum=None,
    track=TRACK_CLASSIC,
    lead_time=0.0,
    ceiling=None,
    flow=False,
    station=None,
):
    return ZoneRun(
        zone_id=zone_id,
        duration=duration,
        depletion_ratio=ratio,
        last_irrigation=last,
        maximum_duration=maximum,
        track=track,
        lead_time=lead_time,
        ceiling=ceiling,
        flow=flow,
        station=station,
    )


def _station(
    zone_id, duration, group, delay=0.0, ratio=1.0, maximum=None, controller="os_1"
):
    """A station-track run whose controller facts are known."""
    return _run(
        zone_id,
        duration,
        ratio=ratio,
        maximum=maximum,
        track=TRACK_STATION,
        station=StationFacts(
            group=group, delay_seconds=delay, controller_id=controller
        ),
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


class TestConcurrentWallClock:
    """Splitting a run across the dispatch tracks that start together."""

    def _conc(self, runs, sequencing, slot=300.0, absorb=0.0):
        return concurrent_wall_clock(
            runs,
            sequencing=sequencing,
            max_slot_seconds=slot,
            min_absorption_seconds=absorb,
        )

    def test_a_classic_only_run_is_the_plain_simulation(self):
        # The default install, and everything predating the self-closing modes:
        # one track, so no anchor time may move.
        runs = [_run(0, 300), _run(1, 600), _run(2, 120)]
        assert self._conc(runs, SEQUENTIAL) == _sim(runs, SEQUENTIAL) == 1020

    def test_the_longest_track_wins_rather_than_the_total(self):
        runs = [_run(0, 600), _run(1, 900, track=TRACK_SELF_CLOSING)]
        assert self._conc(runs, SEQUENTIAL) == 900

    def test_stations_chain_even_under_parallel_sequencing(self):
        # zone_sequencing does not govern the controller's queue, and only the
        # longer of the two possible orderings is safe to anchor on.
        runs = [_run(0, 300, track=TRACK_STATION), _run(1, 600, track=TRACK_STATION)]
        assert self._conc(runs, PARALLEL) == 900

    def test_service_zones_chain_under_sequential(self):
        """They used to open together whatever the setting said (issue #98).

        The dispatch fired them in one loop, so the track was priced as parallel
        — the longest zone, not all of them. It now goes through the shared
        chain, and pricing it as parallel would anchor a finish-governed run 300 s
        early.
        """
        runs = [
            _run(0, 300, track=TRACK_SELF_CLOSING),
            _run(1, 600, track=TRACK_SELF_CLOSING),
        ]
        assert self._conc(runs, SEQUENTIAL) == 900

    def test_service_zones_still_open_together_under_parallel(self):
        """The default is unchanged: nothing chains, and the longest one wins."""
        runs = [
            _run(0, 300, track=TRACK_SELF_CLOSING),
            _run(1, 600, track=TRACK_SELF_CLOSING),
        ]
        assert self._conc(runs, PARALLEL) == 600

    def test_service_zones_price_their_rotation(self):
        """And rotating reaches them too, absorption pauses included.

        600 s in 300 s slots with a 600 s pause is not 600 s of night: the slot
        model has to be applied to this track exactly as it is to the classic
        one, or a rotation is sized by its watering time and cut off mid-cycle.
        """
        runs = [_run(0, 600, track=TRACK_SELF_CLOSING)]
        assert self._conc(runs, ROTATING, slot=300, absorb=600) == 1200

    def test_no_runs_is_zero(self):
        assert self._conc([], SEQUENTIAL) == 0.0


class TestStationGrouping:
    """Pricing the station track from the controller's own grouping.

    Every clock below is hand-computed. The grouping only applies under
    parallel: sequential and rotating are chains Smart Irrigation enforces
    itself, one station at a time, so the controller's queue never forms.
    """

    def _conc(self, runs, sequencing=None, slot=300.0, absorb=0.0):
        return concurrent_wall_clock(
            runs,
            sequencing=sequencing or PARALLEL,
            max_slot_seconds=slot,
            min_absorption_seconds=absorb,
        )

    def test_one_sequential_group_chains(self):
        runs = [_station(0, 300, group=0), _station(1, 600, group=0)]
        assert self._conc(runs) == 900

    def test_the_parallel_group_overlaps_entirely(self):
        # 255 serializes with nothing, so each member is its own unit and the
        # track costs the longest station rather than their sum.
        runs = [
            _station(0, 300, group=PARALLEL_STATION_GROUP),
            _station(1, 600, group=PARALLEL_STATION_GROUP),
        ]
        assert self._conc(runs) == 600

    def test_two_sequential_groups_run_alongside_each_other(self):
        # Group 0 chains to 900, group 1 chains to 700; they overlap, so 900.
        runs = [
            _station(0, 300, group=0),
            _station(1, 600, group=0),
            _station(2, 400, group=1),
            _station(3, 300, group=1),
        ]
        assert self._conc(runs) == 900

    def test_the_delay_lands_between_members_not_after_the_last(self):
        # Three in a chain is two boundaries: 300 + 600 + 120 + 2 * 15 = 1050.
        runs = [
            _station(0, 300, group=0, delay=15),
            _station(1, 600, group=0, delay=15),
            _station(2, 120, group=0, delay=15),
        ]
        assert self._conc(runs) == 1050

    def test_a_lone_station_is_charged_no_delay(self):
        assert self._conc([_station(0, 300, group=0, delay=15)]) == 300

    def test_the_delay_never_crosses_a_group_boundary(self):
        # One member each in two groups: no boundary anywhere, so no delay.
        runs = [
            _station(0, 300, group=0, delay=60),
            _station(1, 600, group=1, delay=60),
        ]
        assert self._conc(runs) == 600

    def test_a_negative_delay_overlaps_the_chain(self):
        # Stations deliberately overlapped: 300 + 600 - 30 = 870.
        runs = [
            _station(0, 300, group=0, delay=-30),
            _station(1, 600, group=0, delay=-30),
        ]
        assert self._conc(runs) == 870

    def test_a_negative_delay_cannot_drive_the_clock_below_zero(self):
        runs = [
            _station(0, 60, group=0, delay=-600),
            _station(1, 60, group=0, delay=-600),
        ]
        assert self._conc(runs) == 0.0

    def test_one_unreadable_group_reverts_the_whole_track(self):
        # A partial partition can only under-state the track, and under-stating
        # is the direction that overshoots a deadline — so the track falls back
        # to the chain it was priced as before any of this, delay included.
        runs = [
            _station(0, 300, group=PARALLEL_STATION_GROUP, delay=15),
            _run(1, 600, track=TRACK_STATION),
        ]
        assert self._conc(runs) == 900

    def test_facts_without_a_group_are_unreadable_too(self):
        # An unavailable station entity carries no attributes at all.
        runs = [
            _station(0, 300, group=PARALLEL_STATION_GROUP),
            _run(1, 600, track=TRACK_STATION, station=StationFacts()),
        ]
        assert self._conc(runs) == 900

    def test_sequential_sequencing_is_untouched(self):
        # Smart Irrigation holds each station back until the last finalises, so
        # the grouping cannot make them overlap.
        runs = [
            _station(0, 300, group=PARALLEL_STATION_GROUP, delay=15),
            _station(1, 600, group=PARALLEL_STATION_GROUP, delay=15),
        ]
        assert self._conc(runs, SEQUENTIAL) == 900

    def test_rotating_sequencing_is_untouched(self):
        # The station track already overrides rotating with its own chain, so
        # the absorption model never reaches it; the point here is that the
        # grouping does not reach it either.
        runs = [
            _station(0, 300, group=PARALLEL_STATION_GROUP, delay=15),
            _station(1, 600, group=PARALLEL_STATION_GROUP, delay=15),
        ]
        assert self._conc(runs, ROTATING, slot=300, absorb=600) == 900

    def test_a_zero_duration_member_charges_no_delay(self):
        # ignore_demand plans carry zero-duration runs; they occupy no slot in
        # the controller's queue, so they add no boundary either.
        runs = [
            _station(0, 300, group=0, delay=15),
            _station(1, 0, group=0, delay=15),
        ]
        assert self._conc(runs) == 300

    def test_two_controllers_do_not_share_a_group_number(self):
        # Group ids are numbered per controller, so these are two independent
        # chains of 900 running alongside each other, not one chain of 1800.
        runs = [
            _station(0, 300, group=0, controller="os_1"),
            _station(1, 600, group=0, controller="os_1"),
            _station(2, 400, group=0, controller="os_2"),
            _station(3, 500, group=0, controller="os_2"),
        ]
        assert self._conc(runs) == 900

    def test_the_longest_track_still_wins_across_tracks(self):
        # Stations collapse to 600 under the parallel group; the classic and
        # self-closing tracks are priced under their own rules, and the longest
        # of the three takes the answer rather than the three being added.
        runs = [
            _station(0, 300, group=PARALLEL_STATION_GROUP),
            _station(1, 600, group=PARALLEL_STATION_GROUP),
            _run(2, 900),
            _run(3, 300),
            _run(4, 700, track=TRACK_SELF_CLOSING),
            _run(5, 800, track=TRACK_SELF_CLOSING),
        ]
        assert self._conc(runs) == 900

    def test_grouping_reaches_the_bound(self):
        # Configured ceilings, priced through the same reduction: two stations
        # in the parallel group bound at the longer, not the sum.
        runs = [
            _station(0, 100, group=PARALLEL_STATION_GROUP, maximum=4800),
            _station(1, 100, group=PARALLEL_STATION_GROUP, maximum=3000),
        ]
        assert (
            bound_wall_clock(
                runs,
                sequencing=PARALLEL,
                max_slot_seconds=300,
                min_absorption_seconds=0,
            )
            == 4800
        )

    def test_grouping_admits_a_zone_the_chain_model_refused(self):
        # 900 s of window. Chained, the pair costs 900 and the third station
        # cannot fit; in the parallel group all three overlap and all three run.
        runs = [
            _station(0, 600, group=PARALLEL_STATION_GROUP, ratio=3.0),
            _station(1, 500, group=PARALLEL_STATION_GROUP, ratio=2.0),
            _station(2, 400, group=PARALLEL_STATION_GROUP, ratio=1.5),
        ]
        chosen = select(
            runs,
            window_seconds=900,
            sequencing=PARALLEL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        )
        assert [r.zone_id for r in chosen] == [0, 1, 2]


class TestRank:
    """Priority order: depletion ratio, then longest since last watered."""

    def test_orders_by_depletion_ratio_descending(self):
        runs = [
            _run(0, 300, ratio=1.2),
            _run(1, 300, ratio=2.0),
            _run(2, 300, ratio=1.5),
        ]
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
        runs = [
            _run(0, 300, ratio=1.5, last=watered),
            _run(1, 300, ratio=1.5, last=None),
        ]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_aware_and_naive_timestamps_compare(self):
        # last_irrigation is written with dt_util.now() (aware), but a zone
        # hydrated from older storage can carry a naive one. Mixing them must
        # not raise — a TypeError here would abort the whole run.
        aware = datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.timezone.utc)
        naive = datetime.datetime(2026, 8, 4, 6, 0)
        runs = [
            _run(0, 300, ratio=1.5, last=naive),
            _run(1, 300, ratio=1.5, last=aware),
        ]
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
        runs = [
            _run(0, 300, ratio=1.5, last=live),
            _run(1, 300, ratio=1.5, last=stored),
        ]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_an_unparseable_stamp_reads_as_never_watered(self):
        runs = [
            _run(0, 300, ratio=1.5, last="2026-08-05T06:00:00+00:00"),
            _run(1, 300, ratio=1.5, last="not a timestamp"),
        ]
        assert [r.zone_id for r in rank(runs)] == [1, 0]

    def test_zone_id_is_the_final_tie_break(self):
        runs = [
            _run(2, 300, ratio=1.5),
            _run(0, 300, ratio=1.5),
            _run(1, 300, ratio=1.5),
        ]
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

    def test_a_dropped_zone_leads_the_next_nights_selection(self):
        # No special-casing needed: a zone excluded tonight keeps draining
        # unwatered, so tomorrow it is due again at a HIGHER ratio, and
        # rank()/select() alone put it back at the front — even ahead of a
        # zone that only just crossed its own threshold overnight.
        night_one = [
            _run(0, 7200, ratio=1.1),
            _run(1, 7200, ratio=1.5),
            _run(2, 7200, ratio=3.0),
        ]
        chosen_one = self._select(night_one, 14400)
        assert [r.zone_id for r in chosen_one] == [2, 1]
        dropped = {r.zone_id for r in night_one} - {r.zone_id for r in chosen_one}
        assert dropped == {0}

        # Zones 1 and 2 watered to satisfaction and are no longer due; zone 0
        # went unwatered and its ratio grew; zone 3 is freshly due with a
        # smaller deficit than zone 0's accumulated one.
        night_two = [_run(0, 7200, ratio=1.3), _run(3, 7200, ratio=1.05)]
        chosen_two = self._select(night_two, 14400)
        assert [r.zone_id for r in chosen_two] == [0, 3]


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


class TestSelectAcrossTracks:
    """Fitting decisions priced per dispatch track rather than on one timeline.

    ``fits`` asks a yes/no question about a candidate set, and once the tracks
    start together the tracks-aware answer is the honest one. It moves the
    boundary in both directions: a station set that a single timeline called
    small enough really is not, and a service set it called too big really does
    fit.
    """

    def _select(self, runs, window, sequencing=SEQUENTIAL, slot=300.0, absorb=0.0):
        return select(
            runs,
            window_seconds=window,
            sequencing=sequencing,
            max_slot_seconds=slot,
            min_absorption_seconds=absorb,
        )

    def test_a_shadowed_zone_rides_along_for_free(self):
        # The station's 600 s sit entirely inside the classic track's 3600 s, so
        # admitting it costs no window at all. A single timeline would charge
        # 4200 against the 3600 s window and drop it, leaving capacity that
        # nothing else could have used.
        runs = [
            _run(0, 3600, ratio=3.0),
            _run(1, 600, ratio=1.5, track=TRACK_STATION),
        ]
        assert [r.zone_id for r in self._select(runs, 3600)] == [0, 1]

    def test_stations_are_not_over_admitted_under_parallel(self):
        # The dangerous direction: max(stations) under parallel says both fit,
        # but the controller may chain them, and a run sized on the shorter of
        # the two possible orderings finishes after its anchor.
        runs = [
            _run(0, 900, ratio=3.0, track=TRACK_STATION),
            _run(1, 800, ratio=2.0, track=TRACK_STATION),
        ]
        assert [r.zone_id for r in self._select(runs, 1000, PARALLEL)] == [0]

    def test_service_zones_are_not_over_admitted_under_sequential(self):
        # The dangerous direction, and the one this track changed sides on
        # (issue #98). They used to open together, so 1000 s admitted both; they
        # now chain, so admitting both would run 1700 s past a 1000 s anchor.
        runs = [
            _run(0, 900, ratio=3.0, track=TRACK_SELF_CLOSING),
            _run(1, 800, ratio=2.0, track=TRACK_SELF_CLOSING),
        ]
        assert [r.zone_id for r in self._select(runs, 1000)] == [0]

    def test_service_zones_are_not_under_admitted_under_parallel(self):
        # The wasteful direction, which survives where the setting still says
        # they open together: the hardware closes each valve itself and 900 s
        # covers both.
        runs = [
            _run(0, 900, ratio=3.0, track=TRACK_SELF_CLOSING),
            _run(1, 800, ratio=2.0, track=TRACK_SELF_CLOSING),
        ]
        assert [r.zone_id for r in self._select(runs, 1000, PARALLEL)] == [0, 1]

    def test_a_free_zone_never_displaces_a_drier_one(self):
        # Zone 0 is the strict leader and does not fit; the always-include-the
        # leader rule still returns it alone, and the shadowed station in the
        # wetter group is not consulted. Dryness owns the window across groups
        # whatever the tracks cost.
        runs = [
            _run(0, 2400, ratio=1.5),
            _run(1, 600, ratio=1.2, track=TRACK_STATION),
        ]
        assert [r.zone_id for r in self._select(runs, 2000)] == [0]

    def test_a_tie_group_packs_the_free_track_as_well(self):
        # Within a tie there is no dryness argument between members, so the
        # subset delivering the most watering seconds wins — and seconds on a
        # track the classic zone already shadows are pure gain.
        runs = [
            _run(0, 1800, ratio=1.2, last=datetime.datetime(2026, 7, 30)),
            _run(
                1,
                1500,
                ratio=1.2,
                last=datetime.datetime(2026, 7, 31),
                track=TRACK_STATION,
            ),
        ]
        assert [r.zone_id for r in self._select(runs, 1800)] == [0, 1]


class TestBoundWallClock:
    """The duration-independent ceiling that fixes the decision point."""

    def test_sums_configured_maximums_under_sequential(self):
        runs = [_run(0, 100, maximum=4800), _run(1, 100, maximum=3000)]
        assert (
            bound_wall_clock(
                runs,
                sequencing=SEQUENTIAL,
                max_slot_seconds=300,
                min_absorption_seconds=0,
            )
            == 7800
        )

    @pytest.mark.parametrize("sequencing", [SEQUENTIAL, PARALLEL, ROTATING])
    def test_an_unset_maximum_is_unbounded_rather_than_a_stand_in_number(
        self, sequencing
    ):
        # Under every sequencing: an infinite budget has to come back out as
        # one, including from the rotating replay, which cannot subtract its
        # way down to zero from it.
        runs = [_run(0, 100, maximum=None), _run(1, 100, maximum=0)]
        assert (
            bound_wall_clock(
                runs,
                sequencing=sequencing,
                max_slot_seconds=300,
                min_absorption_seconds=0,
            )
            == math.inf
        )

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

    def test_ceilings_are_reduced_per_track_too(self):
        # Same ceilings as the sequential case above, but the second zone is a
        # service zone: it opens alongside the classic one rather than after it,
        # so the bound is the longer of the two, not their sum. Over-stating it
        # would move the decision point earlier than the arm needs.
        runs = [
            _run(0, 100, maximum=4800),
            _run(1, 100, maximum=3000, track=TRACK_SELF_CLOSING),
        ]
        assert (
            bound_wall_clock(
                runs,
                sequencing=SEQUENTIAL,
                max_slot_seconds=300,
                min_absorption_seconds=0,
            )
            == 4800
        )

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


class TestSelectLeaderIsTieBroken:
    """When nothing in the driest group fits, WHICH zone gets the window."""

    def _r(self, zone_id, ratio, days_ago):
        return _run(
            zone_id,
            3600,
            ratio=ratio,
            last=datetime.datetime(2026, 8, 1) - datetime.timedelta(days=days_ago),
        )

    def test_leader_is_the_tie_broken_one_not_the_float_residue_one(self):
        # Both ratios round to 1.20, so they are one tie group. Zone 1 is the
        # longest unwatered and is therefore the group's tie-broken leader.
        # Zone 0 leads only on sub-quantum residue, which is exactly what the
        # rounding exists to discard.
        runs = [self._r(0, 1.203, 1), self._r(1, 1.201, 5)]
        assert [r.zone_id for r in rank(runs)] == [0, 1]
        chosen = select(
            runs,
            window_seconds=60,
            sequencing=SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        )
        assert [r.zone_id for r in chosen] == [1]

    def test_a_strict_leader_is_still_the_leader(self):
        # No tie: zone 0 is strictly driest, so it takes the window whatever
        # the last-irrigation order says.
        runs = [self._r(0, 5.0, 1), self._r(1, 1.2, 5)]
        chosen = select(
            runs,
            window_seconds=60,
            sequencing=SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        )
        assert [r.zone_id for r in chosen] == [0]


@pytest.mark.parametrize("sequencing", [SEQUENTIAL, PARALLEL, ROTATING])
class TestBoundIsAnUpperBound:
    """The bound has to cover what the runner would really do.

    Every other bound test prices from ``maximum_duration`` and compares the
    result against another expression of the same model. These drive the real
    ``duration_from_deficit`` on both sides, which is the only way a gap
    between the model and the runner shows up.

    Every case runs under all three sequencings. A single zone occupies the
    same wall clock under each of them with no absorption pause, so the
    expectations do not move; what does move is which branch of
    ``simulate_wall_clock`` answers. Pinning these to one sequencing hid a
    rotating replay that could not terminate on an unbounded zone, because the
    only assertions that reached an infinite budget took the sequential sum.
    """

    def _bound(self, run, sequencing):
        return bound_wall_clock(
            [run],
            sequencing=sequencing,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        )

    def test_the_bound_covers_the_lead_time_the_cap_does_not(self, sequencing):
        # duration_from_deficit clamps FIRST and adds lead_time after, so a
        # zone capped at 600 s with a 120 s lead time really occupies 720 s.
        real = duration_from_deficit(-100.0, 10, 10, 1, 600, 120, True)
        assert real == 720
        run = _run(1, real, ratio=5.0, maximum=600, lead_time=120)
        assert self._bound(run, sequencing) >= real

    def test_a_zone_with_no_configured_cap_is_reported_unbounded(self, sequencing):
        # Nothing caps a TIMED zone with no maximum_duration: the `or 14400`
        # sites are all flow-zone safety timeouts, and the deficit that sizes
        # the run is not capped either, because maximum_bucket clamps the
        # bucket's surplus side only. A plausible-looking number here would be
        # worse than none, because a caller arming on `target - bound` has to
        # tell "no fixed point exists" from "it is four hours back".
        run = _run(1, 300, ratio=5.0, maximum=None)
        assert self._bound(run, sequencing) == math.inf

    def test_a_caller_supplied_ceiling_bounds_an_uncapped_zone(self, sequencing):
        # 100 mm of deficit at a 60 mm/h precipitation rate.
        real = duration_from_deficit(-100.0, 10, 10, 1, None, 0, True)
        assert real == 6000
        bound = self._bound(
            _run(1, real, ratio=5.0, maximum=None, ceiling=7200), sequencing
        )
        assert bound == 7200
        assert bound >= real

    def test_one_unbounded_zone_makes_the_whole_bound_unbounded(self, sequencing):
        runs = [_run(1, 300, ratio=5.0, maximum=600), _run(2, 300, ratio=5.0)]
        assert (
            bound_wall_clock(
                runs,
                sequencing=sequencing,
                max_slot_seconds=300,
                min_absorption_seconds=0,
            )
            == math.inf
        )


class TestSimulateWallClockDuplicateIds:
    def test_two_runs_sharing_a_zone_id_are_not_collapsed(self):
        # Budget was keyed by zone_id, so a duplicate silently vanished and the
        # clock came out short. Short is the unsafe direction here.
        runs = [_run(1, 300), _run(1, 300)]
        assert _sim(runs, SEQUENTIAL) == 600

    def test_duplicate_ids_take_the_longer_ceiling_not_the_last(self):
        # The overrides are keyed by zone id, so a collision resolves to one
        # entry, while the runs themselves are priced positionally. Both are
        # counted, each at the LONGER cap: 2 x 600, not 600 + 60. Short is
        # the direction that overruns the finish.
        runs = [
            _run(1, 300, ratio=5.0, maximum=600),
            _run(1, 300, ratio=5.0, maximum=60),
        ]
        assert (
            bound_wall_clock(
                runs,
                sequencing=SEQUENTIAL,
                max_slot_seconds=300,
                min_absorption_seconds=0,
            )
            == 1200
        )


class TestPricedInDispatchOrder:
    """The model has to price the order the runner actually dispatches.

    ``_run_rotation`` builds its ring from ``timed_zones + flow_zones``, so a
    flow zone is always served last however the plan is ordered. Pricing the
    caller's order instead moves the rotating clock, and that clock is what a
    finish anchor is worked back from.
    """

    def test_a_flow_zone_is_priced_last_whatever_order_it_arrives_in(self):
        kw = dict(sequencing=ROTATING, max_slot_seconds=300, min_absorption_seconds=600)
        flow_first = [_run(0, 900, flow=True), _run(1, 300), _run(2, 300)]
        flow_last = [_run(1, 300), _run(2, 300), _run(0, 900, flow=True)]
        assert concurrent_wall_clock(flow_first, **kw) == concurrent_wall_clock(
            flow_last, **kw
        )


class TestPackingOptimality:
    """The packing claim, brute-forced rather than asserted on chosen cases.

    ``select``'s docstring says the subset of a tie group delivering the most
    watering seconds into the window wins. The existing tests demonstrate that
    on hand-built examples, which cannot distinguish "the rule holds" from
    "the rule holds on the examples someone thought of".
    """

    def _clock(self, subset, sequencing, absorb):
        return concurrent_wall_clock(
            subset,
            sequencing=sequencing,
            max_slot_seconds=300,
            min_absorption_seconds=absorb,
        )

    def _brute_force_best(self, runs, window, sequencing, absorb):
        """Most watering seconds any subset can deliver, priced the way the
        run would actually execute.

        Each candidate is ordered by the tie-break before pricing, because
        that is the order the run is committed to and under rotating the
        clock depends on it: the same three zones cost 1050 s in one order
        and 1650 s in another, so a brute force free to reorder would be
        measuring a packer this one deliberately is not.
        """
        best = 0.0
        for size in range(1, len(runs) + 1):
            for subset in itertools.combinations(runs, size):
                ordered = sorted(subset, key=lambda r: (r.last_irrigation, r.zone_id))
                if self._clock(ordered, sequencing, absorb) <= window:
                    best = max(best, sum(r.duration for r in subset))
        return best

    @pytest.mark.parametrize("seed", range(25))
    def test_one_tie_group_packs_the_window_optimally(self, seed):
        rng = random.Random(seed)
        runs = [
            _run(
                i,
                rng.choice([120, 300, 450, 600, 900]),
                ratio=1.5,
                last=datetime.datetime(2026, 8, 1) - datetime.timedelta(days=i),
            )
            for i in range(rng.randint(2, 6))
        ]
        window = rng.uniform(0.3, 0.9) * sum(r.duration for r in runs)

        for sequencing, absorb in (
            (SEQUENTIAL, 0.0),
            (PARALLEL, 0.0),
            (ROTATING, 600.0),
        ):
            chosen = select(
                runs,
                window_seconds=window,
                sequencing=sequencing,
                max_slot_seconds=300,
                min_absorption_seconds=absorb,
            )
            best = self._brute_force_best(runs, window, sequencing, absorb)
            delivered = sum(r.duration for r in chosen)
            if best == 0:
                # Nothing fits at all, so the leader runs anyway and the
                # deadline cuts it. That is the starvation-relief branch, not
                # a packing decision.
                assert len(chosen) == 1
            else:
                assert delivered == best


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
    watering_mode=None,
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
        const.ZONE_WATERING_MODE: watering_mode,
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
            nominal_demand_seconds(
                zones, **self._kwargs(ROTATING, slot=300, absorb=600)
            )
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

    def test_station_grouping_reaches_the_projection(self):
        # The dial draws this number, so it has to be the wall clock the run
        # really reserves: two stations in the parallel group overlap.
        zones = [
            _zone(0, threshold=-10.0, watering_mode=const.WATERING_MODE_OPENSPRINKLER),
            _zone(1, threshold=-5.0, watering_mode=const.WATERING_MODE_OPENSPRINKLER),
        ]
        facts = {
            0: StationFacts(group=PARALLEL_STATION_GROUP),
            1: StationFacts(group=PARALLEL_STATION_GROUP),
        }
        assert (
            nominal_demand_seconds(zones, station_facts=facts, **self._kwargs(PARALLEL))
            == 600.0
        )

    def test_the_projection_chains_stations_when_no_facts_are_supplied(self):
        # An install whose controller cannot answer keeps the pricing it had.
        zones = [
            _zone(0, threshold=-10.0, watering_mode=const.WATERING_MODE_OPENSPRINKLER),
            _zone(1, threshold=-5.0, watering_mode=const.WATERING_MODE_OPENSPRINKLER),
        ]
        assert nominal_demand_seconds(zones, **self._kwargs(PARALLEL)) == 900.0

    def test_independent_of_every_zones_live_bucket(self):
        dry = [
            _zone(0, threshold=-10.0, bucket=-9.9),
            _zone(1, threshold=-5.0, bucket=-4.9),
        ]
        wet = [
            _zone(0, threshold=-10.0, bucket=0.0),
            _zone(1, threshold=-5.0, bucket=0.0),
        ]
        for sequencing in (PARALLEL, SEQUENTIAL, ROTATING):
            kwargs = self._kwargs(sequencing, slot=300, absorb=600)
            assert nominal_demand_seconds(dry, **kwargs) == nominal_demand_seconds(
                wet, **kwargs
            )
