"""Fitting a run into the window before its finish anchor (run_window.py).

Pure arithmetic — no Home Assistant, no coordinator, no store. Every expected
wall clock below is hand-computed against the rotating runner's own loop
(``irrigation._run_rotation``), because that arithmetic is the whole reason
this module exists: under rotating, ``sum(durations)`` is not the wall clock.
"""

import datetime

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.run_window import (
    PARALLEL_STATION_GROUP,
    RUN_CEILING_SECONDS,
    TRACK_CLASSIC,
    TRACK_SELF_CLOSING,
    TRACK_STATION,
    StationFacts,
    ZoneRun,
    bound_wall_clock,
    concurrent_wall_clock,
    rank,
    select,
    simulate_wall_clock,
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
    station=None,
):
    return ZoneRun(
        zone_id=zone_id,
        duration=duration,
        depletion_ratio=ratio,
        last_irrigation=last,
        maximum_duration=maximum,
        track=track,
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

    def test_service_zones_open_together_even_under_sequential(self):
        runs = [
            _run(0, 300, track=TRACK_SELF_CLOSING),
            _run(1, 600, track=TRACK_SELF_CLOSING),
        ]
        assert self._conc(runs, SEQUENTIAL) == 600

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

    def test_service_zones_are_not_under_admitted_under_sequential(self):
        # The wasteful direction: the hardware closes each valve itself, so
        # these open together and 900 s covers both.
        runs = [
            _run(0, 900, ratio=3.0, track=TRACK_SELF_CLOSING),
            _run(1, 800, ratio=2.0, track=TRACK_SELF_CLOSING),
        ]
        assert [r.zone_id for r in self._select(runs, 1000)] == [0, 1]

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

    def test_ceilings_are_reduced_per_track_too(self):
        # Same ceilings as the sequential case above, but the second zone is a
        # service zone: it opens alongside the classic one rather than after it,
        # so the bound is the longer of the two, not their sum. Over-stating it
        # would move the decision point earlier than the arm needs.
        runs = [
            _run(0, 100, maximum=4800),
            _run(1, 100, maximum=3000, track=TRACK_SELF_CLOSING),
        ]
        assert bound_wall_clock(
            runs,
            sequencing=SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        ) == 4800

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
