"""Unit tests for the pure FlowMeter engine + learning functions (no Home Assistant)."""

import pytest

from custom_components.irrigation_plus.flow_metering import (
    FlowMeter,
    flow_is_totalizer,
    flow_learn_next_streak,
    flow_learn_resolve,
    flow_litres_from_total,
    flow_rate_to_l_per_min,
)


def _feed(meter, series):
    for value, unit, state_class, at in series:
        meter.sample(value, unit, state_class, at)
    return meter.delivered()


# --- rate ---
def test_rate_sensor_integrates_over_time():
    m = FlowMeter()
    assert _feed(m, [(6.0, "L/min", None, float(t)) for t in range(0, 121, 15)]) == 12.0


def test_rate_gpm_is_not_a_totalizer():
    assert flow_is_totalizer("gpm", None) is False
    m = FlowMeter()
    assert _feed(m, [(1.0, "gpm", None, 0.0), (1.0, "gpm", None, 60.0)]) == 3.785411784


def test_rate_non_monotonic_at_does_not_double_count():
    m = FlowMeter()
    series = [
        (6.0, "L/min", None, 0.0),
        (6.0, "L/min", None, 60.0),
        (6.0, "L/min", None, 30.0),  # backward -> skipped, no double count
        (6.0, "L/min", None, 90.0),
    ]
    assert _feed(m, series) == 9.0


# --- per_run (explicit) ---
def test_per_run_reset_at_open_credits_final():
    m = FlowMeter("per_run")
    series = [
        (62.0, "L", None, 0.0),
        (0.0, "L", None, 15.0),
        (3.0, "L", None, 30.0),
        (6.0, "L", None, 45.0),
        (9.0, "L", None, 60.0),
        (12.0, "L", None, 75.0),
        (12.0, "L", None, 120.0),
    ]
    assert _feed(m, series) == 12.0


def test_per_run_already_reset_at_open():
    m = FlowMeter("per_run")
    assert (
        _feed(
            m, [(0.0, "L", None, 0.0), (5.0, "L", None, 30.0), (12.0, "L", None, 90.0)]
        )
        == 12.0
    )


def test_per_run_coarse_reset_credits_full():
    m = FlowMeter("per_run")
    assert (
        _feed(
            m, [(62.0, "L", None, 0.0), (0.0, "L", None, 15.0), (12.0, "L", None, 30.0)]
        )
        == 12.0
    )


def test_per_run_reseeds_once_later_glitch_kept():
    m = FlowMeter("per_run")
    series = [
        (62.0, "L", None, 0.0),
        (0.0, "L", None, 15.0),
        (3.0, "L", None, 30.0),
        (6.0, "L", None, 45.0),
        (0.1, "L", None, 60.0),  # later near-zero dip -> glitch (already reseeded)
        (9.0, "L", None, 75.0),
        (12.0, "L", None, 90.0),
    ]
    assert _feed(m, series) == 12.0


def test_per_run_delayed_reset_any_time():
    m = FlowMeter("per_run")
    series = [
        (62.0, "L", None, 0.0),
        (62.0, "L", None, 20.0),
        (0.0, "L", None, 90.0),
        (4.0, "L", None, 120.0),
    ]
    assert _feed(m, series) == 4.0


# --- lifetime (explicit) ---
def test_lifetime_credits_end_minus_start():
    m = FlowMeter("lifetime")
    assert (
        _feed(
            m,
            [
                (1000.0, "L", "total_increasing", 0.0),
                (1012.0, "L", "total_increasing", 90.0),
            ],
        )
        == 12.0
    )


def test_lifetime_glitch_low_keeps_baseline():
    m = FlowMeter("lifetime")
    series = [
        (1000.0, "L", "total_increasing", 0.0),
        (1005.0, "L", "total_increasing", 40.0),
        (2.0, "L", "total_increasing", 55.0),
        (1006.0, "L", "total_increasing", 70.0),
    ]
    assert _feed(m, series) == 6.0


def test_lifetime_partial_rebound_no_over_credit():
    # THE adversarial case: glitch to near-zero then partial recovery must credit only
    # the true delta above baseline (1 L), never the phantom climb from the low.
    m = FlowMeter("lifetime")
    series = [
        (1000.0, "L", None, 0.0),
        (0.5, "L", None, 10.0),
        (800.0, "L", None, 20.0),
        (1001.0, "L", None, 30.0),
    ]
    assert _feed(m, series) == 1.0


def test_lifetime_drop_and_stay_credits_zero():
    m = FlowMeter("lifetime")
    assert (
        _feed(
            m,
            [
                (1000.0, "L", None, 0.0),
                (0.5, "L", None, 10.0),
                (800.0, "L", None, 20.0),
            ],
        )
        == 0.0
    )


# --- default / auto string is lifetime-safe ---
def test_default_counter_type_is_lifetime_safe():
    m = FlowMeter()
    assert (
        _feed(
            m, [(62.0, "L", None, 0.0), (0.0, "L", None, 15.0), (12.0, "L", None, 30.0)]
        )
        == 0.0
    )


def test_auto_string_treated_as_lifetime_safe():
    m = FlowMeter("auto")
    assert (
        _feed(
            m, [(62.0, "L", None, 0.0), (0.0, "L", None, 15.0), (12.0, "L", None, 30.0)]
        )
        == 0.0
    )


# --- guards ---
def test_no_numeric_reading_returns_none():
    m = FlowMeter()
    m.sample(None, "L/min", None, 0.0)
    m.sample("unavailable", "L/min", None, 15.0)
    assert m.delivered() is None


def test_dry_meter_returns_zero_not_none():
    m = FlowMeter("lifetime")
    assert _feed(m, [(5.0, "L", None, 0.0), (5.0, "L", None, 60.0)]) == 0.0


def test_nan_reading_ignored():
    m = FlowMeter("lifetime")
    assert (
        _feed(
            m,
            [
                (1000.0, "L", None, 0.0),
                (float("nan"), "L", None, 10.0),
                (1005.0, "L", None, 20.0),
            ],
        )
        == 5.0
    )


def test_last_total_reports_end_value():
    m = FlowMeter("lifetime")
    _feed(m, [(1000.0, "L", None, 0.0), (1005.0, "L", None, 20.0)])
    assert m.last_total() == 1005.0
    r = FlowMeter()
    _feed(r, [(6.0, "L/min", None, 0.0), (6.0, "L/min", None, 60.0)])
    assert r.last_total() is None


def test_unit_conversions():
    assert flow_litres_from_total(2.0, "m³") == 2000.0
    assert flow_litres_from_total(1.0, "gal") == 3.785411784
    assert flow_rate_to_l_per_min(60.0, "L/h") == 1.0
    assert flow_is_totalizer("L", None) is True
    assert flow_is_totalizer("L/min", None) is False
    assert flow_is_totalizer("", "total_increasing") is True


# --- learning functions ---
def test_learn_next_streak_no_usable_prior():
    assert flow_learn_next_streak(None, 5.0, 0) == 0
    assert flow_learn_next_streak(0.5, 0.1, 3) == 3  # prev_end <= 1.0 -> unchanged


def test_learn_next_streak_reset_increments():
    assert flow_learn_next_streak(62.0, 0.4, 1) == 2  # 0.4 < 0.5*62 -> reset


def test_learn_next_streak_monotonic_zeroes():
    assert flow_learn_next_streak(62.0, 62.0, 3) == 0
    assert flow_learn_next_streak(1000.0, 1002.0, 2) == 0


def test_learn_resolve_override_wins():
    assert flow_learn_resolve("per_run", 0) == "per_run"
    assert flow_learn_resolve("lifetime", 5) == "lifetime"


def test_learn_resolve_auto_by_streak():
    assert flow_learn_resolve("auto", 0) == "lifetime"
    assert flow_learn_resolve("auto", 1) == "lifetime"
    assert flow_learn_resolve("auto", 2) == "per_run"
    assert flow_learn_resolve(None, 2) == "per_run"


def test_per_run_post_reset_seed_midrun_glitch_no_over_credit():
    # Seeded at the post-reset value (0), the per_run reseed budget must NOT be spent by
    # a mid-run near-zero glitch after volume was credited. Regression for the CRITICAL
    # review finding: 0->3->6->9->12->0.1(glitch)->15 must credit 15, not 26.9.
    m = FlowMeter("per_run")
    series = [
        (0.0, "L", None, 0.0),
        (3.0, "L", None, 15.0),
        (6.0, "L", None, 30.0),
        (9.0, "L", None, 45.0),
        (12.0, "L", None, 60.0),
        (
            0.1,
            "L",
            None,
            75.0,
        ),  # mid-run glitch AFTER credit -> must be kept, not reset
        (15.0, "L", None, 90.0),
    ]
    assert _feed(m, series) == 15.0


def test_rate_lph_gph_conversion():
    # gph/lph are rate units (not totalizers) and must convert, not pass through as L/min.
    assert flow_is_totalizer("lph", None) is False
    assert flow_is_totalizer("gph", None) is False
    assert flow_rate_to_l_per_min(60.0, "lph") == 1.0
    assert flow_rate_to_l_per_min(60.0, "gph") == 3.785411784


def test_learn_next_streak_boundary_is_strict():
    # start == 0.5*prev_end is NOT a reset (strict <); just below IS.
    assert flow_learn_next_streak(62.0, 31.0, 0) == 0
    assert flow_learn_next_streak(62.0, 30.9, 0) == 1


def test_learn_resolve_unknown_or_empty_override_is_auto():
    # An unknown/typo/empty override falls back to the safe learned (auto) path.
    assert flow_learn_resolve("perrun", 0) == "lifetime"
    assert flow_learn_resolve("", 2) == "per_run"


# --- within-run reset signal (hold-until-reset counters) ---
def test_learn_next_streak_within_run_reset_advances():
    # A mid-run reset the meter observed advances the streak even when the OPEN read
    # looked monotonic (a hold-until-reset counter still held its prior total at open).
    assert flow_learn_next_streak(62.0, 62.0, 1, within_run_reset=True) == 2
    assert flow_learn_next_streak(None, None, 0, within_run_reset=True) == 1


def test_learn_next_streak_none_start_is_safe():
    # A None open reading (rate/no read) with no within-run reset -> unchanged/zeroed,
    # never a crash.
    assert flow_learn_next_streak(62.0, None, 3) == 0  # usable prior, no open reset
    assert flow_learn_next_streak(None, None, 3) == 3  # no usable prior -> unchanged


def test_saw_reset_true_on_per_run_open_reset():
    m = FlowMeter("per_run")
    _feed(m, [(62.0, "L", None, 0.0), (0.0, "L", None, 15.0), (5.0, "L", None, 30.0)])
    assert m.saw_reset() is True


def test_saw_reset_true_on_lifetime_glitch():
    # A lifetime totalizer that glitches to near-zero credits nothing (keep-baseline) but
    # the drop IS observed as cross-run reset evidence.
    m = FlowMeter("lifetime")
    assert _feed(m, [(100.0, "L", None, 0.0), (0.0, "L", None, 15.0)]) == 0.0
    assert m.saw_reset() is True


def test_saw_reset_false_when_monotonic_or_rate():
    m = FlowMeter("lifetime")
    _feed(m, [(100.0, "L", None, 0.0), (110.0, "L", None, 15.0)])
    assert m.saw_reset() is False
    r = FlowMeter()
    _feed(r, [(6.0, "L/min", None, 0.0), (6.0, "L/min", None, 60.0)])
    assert r.saw_reset() is False


def test_rate_gap_bridging_capped_does_not_over_credit():
    # A rate sensor that went unavailable for a long stretch (a wide sample gap) must NOT
    # credit the recovered rate across the whole gap. With max_gap_s=45, the 600 s jump
    # contributes nothing; the two in-window steps credit normally.
    m = FlowMeter(max_gap_s=45.0)
    series = [
        (6.0, "L/min", None, 0.0),
        (6.0, "L/min", None, 30.0),  # 30 s gap <= 45 -> credit 3.0 L
        (6.0, "L/min", None, 630.0),  # 600 s gap > 45 -> credited nothing
        (6.0, "L/min", None, 645.0),  # 15 s gap <= 45 -> credit 1.5 L
    ]
    assert _feed(m, series) == 4.5


def test_rate_gap_uncapped_by_default_bridges():
    # Default (no cap) preserves the original bridge-across-gap behaviour.
    m = FlowMeter()
    assert _feed(m, [(6.0, "L/min", None, 0.0), (6.0, "L/min", None, 600.0)]) == 60.0


# --- end_rate_at: a rate integration ended at a known close ---
# A self-closing run whose valve reported its close is finalised seconds after it, and
# the reads by then find the water stopped. end_rate_at ends the integration at the
# report: the last interval runs on at the last measured rate, later samples are taken
# back out. See test_service_watch.TestAConfirmedRunsFlowEndsAtItsOffReport.
def test_end_rate_at_holds_the_last_rate_to_the_cut_and_drops_later_samples():
    m = FlowMeter()
    series = [
        (10.0, "L/min", None, 0.0),
        (10.0, "L/min", None, 15.0),
        (0.0, "L/min", None, 30.0),  # (15, 30] credited at the 0 read at its end
        (0.0, "L/min", None, 45.0),
    ]
    assert _feed(m, series) == 2.5
    m.end_rate_at(20.0)
    assert m.delivered() == pytest.approx(10.0 * 20 / 60)


def test_end_rate_at_holds_the_converted_rate():
    m = FlowMeter()
    _feed(m, [(600.0, "L/h", None, 0.0), (0.0, "L/h", None, 60.0)])
    m.end_rate_at(30.0)
    assert m.delivered() == pytest.approx(5.0)  # 10 L/min for 30 s


def test_end_rate_at_bridges_no_wider_gap_than_one_poll():
    # The tail's far end is a valve REPORT, not a flow sample: max_gap_s (4 polls) is
    # the bound for an interval with a live reading at BOTH ends. Told the sampler's
    # cadence, the tail is bridged one poll and no further -- past that the sensor may
    # have been gone since the mark.
    series = [(10.0, "L/min", None, 0.0), (10.0, "L/min", None, 15.0)]
    bridged = FlowMeter(max_gap_s=60.0)
    _feed(bridged, series)
    bridged.end_rate_at(30.0, poll_s=15.0)
    assert bridged.delivered() == pytest.approx(2.5 + 2.5)
    too_wide = FlowMeter(max_gap_s=60.0)
    _feed(too_wide, series)
    too_wide.end_rate_at(30.5, poll_s=15.0)
    assert too_wide.delivered() == pytest.approx(2.5)


def test_end_rate_at_without_a_poll_keeps_the_max_gap_bound():
    # No cadence given: the meter has nothing tighter to go on and bounds the tail as
    # it bounds any interval. Unchanged for every caller that passes no poll.
    series = [(10.0, "L/min", None, 0.0), (10.0, "L/min", None, 15.0)]
    bridged = FlowMeter(max_gap_s=60.0)
    _feed(bridged, series)
    bridged.end_rate_at(75.0)
    assert bridged.delivered() == pytest.approx(2.5 + 10.0)
    too_wide = FlowMeter(max_gap_s=60.0)
    _feed(too_wide, series)
    too_wide.end_rate_at(75.5)
    assert too_wide.delivered() == pytest.approx(2.5)


def test_end_rate_at_credits_no_tail_from_a_sensor_dead_since_the_mark():
    # A 612 s run at 10 L/min whose sensor goes 'unavailable' at +570 -- every later
    # tick and the final read return None -- and whose valve reports off at +614. The
    # 4-poll bound bridged 44 s x 10 L/min = 7.3 L no sensor measured, and
    # _sc_finish_run reconciles the bucket from those litres absolutely, so the surplus
    # would be carried into the next run's deficit. Nothing past the last mark is known.
    m = FlowMeter(max_gap_s=60.0)
    _feed(m, [(10.0, "L/min", None, float(t)) for t in range(0, 571, 15)])
    m.sample(None, "L/min", None, 585.0)  # unavailable: nothing is fed
    m.sample(None, "L/min", None, 600.0)
    m.end_rate_at(614.0, poll_s=15.0)
    assert m.delivered() == pytest.approx(10.0 * 570 / 60)  # 95 L, not 102.3


def test_end_rate_at_a_sample_keeps_that_samples_credit():
    m = FlowMeter()
    series = [
        (10.0, "L/min", None, 0.0),
        (20.0, "L/min", None, 15.0),
        (0.0, "L/min", None, 30.0),
    ]
    _feed(m, series)
    m.end_rate_at(15.0)
    assert m.delivered() == pytest.approx(5.0)  # (0, 15] at the 20 read at 15


def test_end_rate_at_before_any_reading_credits_nothing():
    # Every reading came after the close: nothing is known of the flow before it.
    m = FlowMeter()
    _feed(m, [(10.0, "L/min", None, 30.0), (10.0, "L/min", None, 45.0)])
    m.end_rate_at(20.0)
    assert m.delivered() == 0.0


def test_end_rate_at_without_any_reading_stays_none():
    m = FlowMeter()
    m.end_rate_at(20.0)
    assert m.delivered() is None


def test_end_rate_at_ignores_a_sample_that_did_not_advance():
    m = FlowMeter()
    series = [
        (10.0, "L/min", None, 0.0),
        (10.0, "L/min", None, 60.0),
        (50.0, "L/min", None, 30.0),  # backward -> skipped, as by the integration
    ]
    _feed(m, series)
    m.end_rate_at(45.0)
    assert m.delivered() == pytest.approx(7.5)


def test_end_rate_at_leaves_a_totalizer_alone():
    # A counter only climbs for water that flowed, so a read after the close counts.
    m = FlowMeter("lifetime")
    _feed(
        m, [(100.0, "L", None, 0.0), (105.0, "L", None, 15.0), (110.0, "L", None, 30.0)]
    )
    m.end_rate_at(10.0)
    assert m.delivered() == 10.0
