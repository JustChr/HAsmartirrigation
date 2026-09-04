"""Pricing the batch/queue dispatch track in the run window.

A batch controller is handed the whole irrigation as one ordered queue and runs
it one valve at a time, so the track's wall clock is the SUM of its zones. That
is the opposite of the self-closing service track, which is priced as the
longest zone because those all open together — and a batch zone satisfies
``is_self_closing_zone`` as well, so the only thing keeping it off that track is
the order of the tests in ``track_for_zone``. Getting that wrong is silent: a
six-zone queue would be priced at one zone's length and a finish-governed run
anchored hours late, with nothing raising an error.
"""

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.run_window import (
    TRACK_BATCH,
    TRACK_CLASSIC,
    TRACK_SELF_CLOSING,
    TRACK_STATION,
    ZoneRun,
    bound_wall_clock,
    concurrent_wall_clock,
    track_for_zone,
)

SEQUENTIAL = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
PARALLEL = const.CONF_ZONE_SEQUENCING_PARALLEL
ROTATING = const.CONF_ZONE_SEQUENCING_ROTATING


def _run(zone_id, duration, track=TRACK_BATCH, ratio=1.0, maximum=None):
    return ZoneRun(
        zone_id=zone_id,
        duration=duration,
        depletion_ratio=ratio,
        maximum_duration=maximum,
        track=track,
    )


def _clock(runs, sequencing=PARALLEL):
    return concurrent_wall_clock(
        runs,
        sequencing=sequencing,
        max_slot_seconds=300.0,
        min_absorption_seconds=600.0,
    )


def _zone(zid, mode, **kw):
    z = {const.ZONE_ID: zid, const.ZONE_WATERING_MODE: mode}
    z.update(kw)
    return z


class TestTrackForZone:
    """A batch zone gets its own track, not the service one it also qualifies
    for."""

    def test_a_batch_zone_is_the_batch_track(self):
        assert track_for_zone(_zone(0, const.WATERING_MODE_BATCH)) == TRACK_BATCH

    def test_the_other_modes_are_unmoved(self):
        assert track_for_zone(_zone(1, const.WATERING_MODE_SERVICE)) == (
            TRACK_SELF_CLOSING
        )
        assert track_for_zone(_zone(2, const.WATERING_MODE_OPENSPRINKLER)) == (
            TRACK_STATION
        )
        assert track_for_zone(_zone(3, const.WATERING_MODE_CLASSIC)) == TRACK_CLASSIC

    def test_a_zone_with_no_mode_at_all_is_classic(self):
        assert track_for_zone({const.ZONE_ID: 4}) == TRACK_CLASSIC


class TestTheQueueIsSummed:
    """The regression this track exists to prevent."""

    def test_three_zones_cost_all_three(self):
        runs = [_run(0, 600), _run(1, 900), _run(2, 300)]
        assert _clock(runs) == pytest.approx(1800)

    def test_it_is_not_priced_as_the_longest_zone(self):
        """Explicitly: the service-track reduction would answer 900 here.

        Left as its own assertion because that is the exact wrong answer a
        fall-through to ``service`` produces, and it is a plausible-looking one.
        """
        runs = [_run(0, 600), _run(1, 900), _run(2, 300)]
        assert _clock(runs) == pytest.approx(1800)

    @pytest.mark.parametrize("sequencing", [PARALLEL, SEQUENTIAL, ROTATING])
    def test_zone_sequencing_does_not_reach_it(self, sequencing):
        """A queue is sequential by construction, whatever the setting says.

        Rotating in particular: a rotation is only expressible in a queue by
        sending a zone repeatedly with a slice of its duration, which the
        dispatcher does not do. Pricing the absorption pauses of a rotation the
        controller will never perform would oversize the window.
        """
        runs = [_run(0, 600), _run(1, 900)]
        assert _clock(runs, sequencing=sequencing) == pytest.approx(1500)

    def test_one_zone_is_just_that_zone(self):
        assert _clock([_run(0, 450)]) == pytest.approx(450)

    def test_no_batch_zones_is_zero(self):
        assert _clock([]) == 0.0


class TestEndToEndFromZoneDicts:
    """Zone dict to wall clock, the way a caller actually reaches it.

    The pricing tests above build ``ZoneRun``s with the track already set, so
    they cannot see a routing mistake. This one derives the track from the zone
    the way ``async_plan_zone_runs`` does, and is the test that fails if the
    ``is_batch_zone`` check is ever dropped or moved below ``is_self_closing``.
    """

    def test_six_batch_zones_are_priced_as_all_six(self):
        zones = [_zone(i, const.WATERING_MODE_BATCH) for i in range(6)]
        runs = [
            ZoneRun(
                zone_id=z[const.ZONE_ID],
                duration=1200,
                depletion_ratio=1.0,
                track=track_for_zone(z),
            )
            for z in zones
        ]
        # 6 x 20 min of queue. Priced as the service track it also qualifies for,
        # this would answer 1200 - twenty minutes for a two-hour irrigation.
        assert _clock(runs) == pytest.approx(7200)


class TestAgainstTheOtherTracks:
    """Tracks are started without being awaited, so the answer is the longest."""

    def test_a_long_queue_beats_a_longer_single_service_zone(self):
        runs = [
            _run(0, 600),
            _run(1, 600),
            _run(2, 600),
            _run(3, 900, track=TRACK_SELF_CLOSING),
        ]
        # Batch track 1800, service track 900 (they open together).
        assert _clock(runs) == pytest.approx(1800)

    def test_a_longer_classic_chain_beats_the_queue(self):
        runs = [
            _run(0, 300),
            _run(1, 300),
            _run(2, 1200, track=TRACK_CLASSIC),
            _run(3, 1200, track=TRACK_CLASSIC),
        ]
        # Batch track 600, classic sequential track 2400.
        assert _clock(runs, sequencing=SEQUENTIAL) == pytest.approx(2400)

    def test_a_classic_parallel_track_does_not_absorb_the_queue(self):
        """The two are concurrent with each other but summed within the queue."""
        runs = [
            _run(0, 600),
            _run(1, 600),
            _run(2, 800, track=TRACK_CLASSIC),
        ]
        assert _clock(runs, sequencing=PARALLEL) == pytest.approx(1200)


class TestTheBound:
    """``bound_wall_clock`` prices configuration, so it is knowable days out."""

    def test_the_queue_bound_sums_the_configured_maxima(self):
        runs = [_run(0, 60, maximum=600), _run(1, 60, maximum=900)]
        bound = bound_wall_clock(
            runs,
            sequencing=PARALLEL,
            max_slot_seconds=300.0,
            min_absorption_seconds=600.0,
        )
        assert bound == pytest.approx(1500)

    def test_the_bound_is_never_below_the_clock(self):
        runs = [_run(0, 600, maximum=900), _run(1, 300, maximum=900)]
        assert bound_wall_clock(
            runs,
            sequencing=PARALLEL,
            max_slot_seconds=300.0,
            min_absorption_seconds=600.0,
        ) >= _clock(runs)


class TestPausesAreNotPriced:
    """A pause is not something the fit can anticipate.

    Irrigation Plus has no pause service: the config surface is a run service,
    a stop service, a paused indicator and a timeout. A pause therefore
    originates at the controller or the user, at an unknowable moment, for an
    unknowable length. Reserving the six-hour backstop against that possibility
    would make almost every window unfittable and drop batch zones from runs
    that would have completed fine, so the window is sized for the plan and a
    pause simply overruns it.
    """

    def test_the_clock_is_the_plan_not_the_backstop(self):
        runs = [_run(0, 600), _run(1, 600)]
        assert _clock(runs) == pytest.approx(1200)
        assert _clock(runs) < const.BATCH_PAUSE_BACKSTOP_SECONDS

    def test_the_price_carries_no_slack_for_a_pause(self):
        """A queue can be paused, and a give-up timeout governs how long the
        controller waits. None of that is time the schedule reserves, so the
        price is the durations and nothing else: exactly their sum, and adding
        a zone moves it by exactly that zone's length."""
        two = _clock([_run(0, 600), _run(1, 600)])
        three = _clock([_run(0, 600), _run(1, 600), _run(2, 450)])
        assert two == 1200.0
        assert three - two == 450.0


class TestPricingIsPureArithmetic:
    """The batch track adds no reads of anything outside its arguments."""

    def test_the_answer_is_fixed_by_the_durations_alone(self):
        """Calling twice and comparing the two would pass for any
        implementation, cached or clock-driven alike. The expected value is
        hand-computed instead: three queued zones, one after another."""
        assert _clock([_run(0, 600), _run(1, 900), _run(2, 450)]) == 1950.0
