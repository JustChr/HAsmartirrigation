"""A cumulative rain gauge that revises DOWN must not be credited twice for the
climb back (#149, Megalos).

The reporter's gauge is an API-backed "precipitation today" total, the kind that
restates its figure as the upstream service corrects it. Their live bucket rose
~7.5 mm against 4.3 mm of measured rain, in visible steps, because every recovery
after a revision was credited as fresh rain.

The daily calculation reduces the same buffer through the same aggregate, so this
was never display-only: over-credited rain leaves a fuller bucket and waters less
than the plants need.
"""

import datetime

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.weather_aggregate import (
    _aggregate,
    _precip_increments,
    cumulative_delta_total,
    cumulative_reset_threshold,
)

SENSOR_MAPPINGS = {const.MAPPING_PRECIPITATION: {const.MAPPING_CONF_SOURCE: "sensor"}}


def _credit_through_aggregate(values):
    """The mm the REAL aggregate books for a gauge reading ``values`` hourly."""
    t0 = datetime.datetime(2026, 9, 20, 8, 0, tzinfo=datetime.timezone.utc)
    samples = [(t0 + datetime.timedelta(hours=i), v) for i, v in enumerate(values)]
    out = {}
    _aggregate(
        {const.MAPPING_PRECIPITATION: samples},
        SENSOR_MAPPINGS,
        out,
        samples[0][0],
        samples[-1][0],
    )
    return out[const.MAPPING_PRECIPITATION]


class TestTheClimbOfAWellBehavedGauge:
    """The cases that already worked keep working."""

    def test_a_monotone_gauge_is_credited_exactly_its_climb(self):
        assert _credit_through_aggregate([0.0, 1.0, 2.0, 3.0, 4.3]) == pytest.approx(
            4.3
        )

    def test_a_gauge_that_never_moves_credits_nothing(self):
        assert _credit_through_aggregate([2.5, 2.5, 2.5]) == pytest.approx(0.0)

    def test_the_first_reading_is_the_baseline_not_rain(self):
        """The carried-forward boundary row opens the window; it already fell."""
        assert _credit_through_aggregate([4.0, 4.0]) == pytest.approx(0.0)

    def test_a_midnight_rollover_to_zero_rebases(self):
        assert _credit_through_aggregate([4.3, 0.0, 0.5]) == pytest.approx(0.5)


class TestADownwardRevisionIsNotRain:
    """The defect. Each case fails on the pre-#149 rule."""

    def test_a_revision_and_recovery_credits_only_the_new_water(self):
        """4.3 -> 3.0 -> 5.0 is 0.7 mm of new rain. The old rule booked 2.0."""
        assert _credit_through_aggregate([4.3, 3.0, 5.0]) == pytest.approx(0.7)

    def test_a_gauge_that_dips_through_a_wet_day_matches_its_own_total(self):
        """It starts at 0 and ends at 4.3, so 4.3 mm fell. The old rule booked 5.5."""
        assert _credit_through_aggregate(
            [0.0, 1.0, 0.8, 2.0, 1.5, 3.0, 2.5, 4.3]
        ) == pytest.approx(4.3)

    def test_a_revision_that_is_never_recovered_credits_nothing(self):
        assert _credit_through_aggregate([4.3, 3.0, 3.0]) == pytest.approx(0.0)

    def test_a_recovery_that_falls_short_of_the_mark_credits_nothing(self):
        """Back up to 4.0 from 3.0 is still below the 4.3 already booked."""
        assert _credit_through_aggregate([4.3, 3.0, 4.0]) == pytest.approx(0.0)

    def test_repeated_revisions_cannot_accumulate(self):
        """The mark is monotone, so sawtoothing below it books nothing at all."""
        assert _credit_through_aggregate(
            [5.0, 4.0, 5.0, 4.0, 5.0, 4.0, 5.0]
        ) == pytest.approx(0.0)


class TestTellingARestartFromARevision:
    def test_a_restart_to_a_small_non_zero_value_still_rebases(self):
        """Rain falling at midnight: the first reading of the new day is 0.2.

        An exactly-zero rule would read this as a revision and then credit
        nothing until the new day beat the old day's 4.3 mm.
        """
        assert _credit_through_aggregate([4.3, 0.2, 0.9]) == pytest.approx(0.9)

    def test_a_drop_just_above_the_threshold_is_a_revision(self):
        assert cumulative_reset_threshold(4.3) == pytest.approx(0.43)
        # 0.6 is above the threshold, so the climb back to 4.3 is not new rain.
        assert _credit_through_aggregate([4.3, 0.6, 4.3]) == pytest.approx(0.0)

    def test_a_drop_to_the_threshold_itself_is_a_restart(self):
        assert _credit_through_aggregate([4.0, 0.4, 1.0]) == pytest.approx(1.0)

    def test_the_threshold_scales_with_the_counter(self):
        """A season-total gauge: 8 of 100 is a restart, not an 8 mm revision."""
        assert cumulative_reset_threshold(100.0) == pytest.approx(10.0)
        assert _credit_through_aggregate([100.0, 8.0, 12.0]) == pytest.approx(12.0)

    def test_a_negative_mark_cannot_lower_the_threshold(self):
        assert cumulative_reset_threshold(-50.0) == pytest.approx(0.0)

    def test_a_reset_gauge_does_not_read_its_own_jitter_as_another_reset(self):
        """The small-value regime right after a real midnight rollover (#149).

        An absolute near-zero floor would call 0.4 -> 0.2 a restart and credit
        the 0.2 twice, which is the very defect this fix removes. The true climb
        across the new day here is 1.0 mm.
        """
        assert _credit_through_aggregate(
            [5.0, 4.0, 3.0, 0.0, 0.4, 0.2, 1.0]
        ) == pytest.approx(1.0)


class TestTheIncrementsAgreeWithTheTotal:
    """``_precip_increments`` drives the bucket while the total becomes ZONE_DELTA.

    live_estimate reconciles the two and logs when they disagree, so they must be
    the same arithmetic rather than two copies of it.
    """

    @pytest.mark.parametrize(
        "values",
        [
            [0.0, 1.0, 2.0, 3.0, 4.3],
            [4.3, 3.0, 5.0],
            [0.0, 1.0, 0.8, 2.0, 1.5, 3.0, 2.5, 4.3],
            [4.3, 0.0, 0.5],
            [4.3, 0.2, 0.9],
            [5.0, 4.0, 5.0, 4.0, 5.0],
            [2.5, 2.5, 2.5],
        ],
    )
    def test_the_increments_sum_to_the_window_total(self, values):
        t0 = datetime.datetime(2026, 9, 20, 8, 0, tzinfo=datetime.timezone.utc)
        samples = [(t0 + datetime.timedelta(hours=i), v) for i, v in enumerate(values)]
        increments = _precip_increments(samples, const.MAPPING_CONF_AGGREGATE_DELTA)
        assert sum(mm for _, mm in increments) == pytest.approx(
            _credit_through_aggregate(values)
        )

    def test_no_increment_is_ever_negative(self):
        """A revision must book zero, never negative rain out of the bucket."""
        t0 = datetime.datetime(2026, 9, 20, 8, 0, tzinfo=datetime.timezone.utc)
        samples = [
            (t0 + datetime.timedelta(hours=i), v)
            for i, v in enumerate([5.0, 4.0, 3.0, 0.0, 0.4, 0.2, 1.0])
        ]
        increments = _precip_increments(samples, const.MAPPING_CONF_AGGREGATE_DELTA)
        assert [mm for _, mm in increments] == [
            pytest.approx(v) for v in (0.0, 0.0, 0.0, 0.0, 0.4, 0.0, 0.6)
        ]
        assert all(mm >= 0.0 for _, mm in increments)

    def test_an_increment_is_emitted_for_every_sample(self):
        t0 = datetime.datetime(2026, 9, 20, 8, 0, tzinfo=datetime.timezone.utc)
        samples = [
            (t0 + datetime.timedelta(hours=i), v)
            for i, v in enumerate([0.0, 1.0, 0.5, 2.0])
        ]
        increments = _precip_increments(samples, const.MAPPING_CONF_AGGREGATE_DELTA)
        assert [t for t, _ in increments] == [t for t, _ in samples]


class TestTheHelperItself:
    def test_an_empty_window_credits_nothing(self):
        assert cumulative_delta_total([]) == pytest.approx(0.0)

    def test_a_single_reading_is_a_baseline_and_credits_nothing(self):
        assert cumulative_delta_total([3.7]) == pytest.approx(0.0)

    def test_string_readings_are_coerced(self):
        """The buffer hands the aggregate whatever the sensor reported."""
        assert cumulative_delta_total(["0.0", "1.5"]) == pytest.approx(1.5)
