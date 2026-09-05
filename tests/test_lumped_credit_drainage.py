"""Drainage on the lumped water balance is cut at the irrigation credit times.

The lumped form integrates drainage from the window start. A mid-window
irrigation credit is already in the stored bucket by the time the calculation
runs, so a surplus that existed for six hours was charged the whole window's
Brooks-Corey drainage, read the zone drier than it was, and froze in once the
bucket returned to deficit and drainage stopped acting. Splitting the integral
at the credit times places each credit on the timeline it arrived on.

What these pin, in order of what a change is most likely to break: a window with
no credits is the arithmetic it always was, a credited window drains exactly the
segments it walked and no more, and the replayed arm never reaches this code.

Segment drainage is asserted against ``drained_over_window`` itself rather than
against a second spelling of Brooks-Corey. Re-deriving the formula here would
only prove the test agrees with itself.
"""

import datetime
import re
from unittest.mock import Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.et_estimate import (
    drained_over_window,
    lumped_water_balance,
    replay_water_balance,
)
from custom_components.irrigation_plus.weather_aggregate import WaterStep

# A real zone's geometry: a 25.4 mm bucket draining at 33.02 mm/h when saturated.
MAXIMUM_BUCKET = 25.4
DRAINAGE_RATE = 33.02
WINDOW = 24.0

NOW = datetime.datetime(2026, 5, 22, 18, 0, 0)


def _make_coordinator():
    """A coordinator carrying only what calculate_module reads."""
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)

    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"

    async def run_executor(func, *args):
        return func(*args)

    hass.async_add_executor_job = run_executor
    coord.hass = hass

    store = Mock()
    store.get_module = Mock(
        return_value={const.MODULE_NAME: "Passthrough", "description": "", "config": {}}
    )
    coord.store = store
    return coord


def _zone(**overrides):
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Garden",
        const.ZONE_MODULE: 10,
        const.ZONE_BUCKET: 0.0,
        const.ZONE_MAXIMUM_BUCKET: MAXIMUM_BUCKET,
        const.ZONE_DRAINAGE_RATE: DRAINAGE_RATE,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_MAXIMUM_DURATION: 3600,
        const.ZONE_LEAD_TIME: 0,
    }
    zone.update(overrides)
    return zone


def _weather(et, multiplier=1.0):
    return {
        const.MAPPING_EVAPOTRANSPIRATION: et,
        const.MAPPING_DATA_MULTIPLIER: multiplier,
    }


def _credit(hours_before_now, mm):
    """A pending bucket event as the runner stores it: a stamp and mm."""
    return {
        "ts": (NOW - datetime.timedelta(hours=hours_before_now)).isoformat(),
        "mm": mm,
    }


def _single_shot(
    bucket,
    delta,
    hours=WINDOW,
    maximum_bucket=MAXIMUM_BUCKET,
    drainage_rate=DRAINAGE_RATE,
):
    """The whole-window integration the lumped path ran for every window.

    Transcribed from the code it replaces, including which of the two ceilings
    reaches ``drained_over_window``: the clamp uses ``maximum_bucket`` and the
    Brooks-Corey scale uses it only when positive.
    """
    level = bucket + delta
    if maximum_bucket is not None and level > maximum_bucket:
        level = float(maximum_bucket)
    drain_maximum = maximum_bucket if maximum_bucket else None
    drained = drained_over_window(level, drainage_rate, hours, drain_maximum)
    return level - drained, drained


# --------------------------------------------------------------------------
# The arithmetic
# --------------------------------------------------------------------------


@pytest.mark.parametrize("maximum_bucket", [MAXIMUM_BUCKET, None, 0.0])
@pytest.mark.parametrize(
    ("bucket", "delta", "hours"),
    [
        (0.0, -5.0, WINDOW),  # dry window, never reaches drainage at all
        (20.0, -3.0, WINDOW),  # surplus that survives the window's ET
        (24.0, 8.0, WINDOW),  # surplus that clamps at the maximum bucket
        (2.0, -2.0, WINDOW),  # lands exactly on field capacity
        (19.37, -3.42, 23.87),  # the shape a real window has: nothing whole
        (6.5, -0.25, 0.0),  # a window with no elapsed time
    ],
)
def test_a_window_without_credits_is_the_single_shot_balance(
    bucket, delta, hours, maximum_bucket
):
    """The property that bounds what this change can move.

    With no credits there is one segment over the whole window, so the answer has
    to be the number the shipped code produced, not merely close to it. Driven
    over both ceilings that behave differently -- no maximum bucket at all, and a
    maximum bucket of 0, which clamps but has no field capacity to scale against.
    """
    expected_bucket, expected_drainage = _single_shot(
        bucket, delta, hours, maximum_bucket
    )

    new, drainage, runoff, segments = lumped_water_balance(
        bucket,
        delta,
        [],
        hours,
        DRAINAGE_RATE,
        maximum_bucket,
        maximum_bucket if maximum_bucket else None,
    )

    assert new == expected_bucket
    assert drainage == expected_drainage
    assert len(segments) == 1
    assert segments[0].hours == hours
    assert segments[0].credit_mm == 0.0
    expected_runoff = 0.0
    if maximum_bucket is not None:
        expected_runoff = max(0.0, bucket + delta - maximum_bucket)
    assert runoff == pytest.approx(expected_runoff)


def test_a_late_credit_is_drained_only_for_the_hours_it_was_there():
    """The defect: 20 mm credited six hours ago paid for twenty-four.

    Both segments are priced by calling ``drained_over_window`` on the levels the
    window actually walked, which is the shipped primitive rather than a second
    copy of its formula.
    """
    bucket, delta, credit, hours_after = 18.0, -4.0, 20.0, 6.0

    new, drainage, runoff, segments = lumped_water_balance(
        bucket,
        delta,
        [(WINDOW - hours_after, credit)],
        WINDOW,
        DRAINAGE_RATE,
        MAXIMUM_BUCKET,
        MAXIMUM_BUCKET,
    )

    level_before = bucket - credit + delta
    first = drained_over_window(
        level_before, DRAINAGE_RATE, WINDOW - hours_after, MAXIMUM_BUCKET
    )
    after_credit = min(level_before - first + credit, MAXIMUM_BUCKET)
    second = drained_over_window(
        after_credit, DRAINAGE_RATE, hours_after, MAXIMUM_BUCKET
    )

    assert [s.hours for s in segments] == [WINDOW - hours_after, hours_after]
    assert drainage == pytest.approx(first + second)
    assert new == pytest.approx(after_credit - second)

    # Water the clamp took off the credit is reported rather than discarded.
    assert runoff == pytest.approx(
        max(0.0, level_before - first + credit - MAXIMUM_BUCKET)
    )

    # And it is strictly wetter than charging the credit the whole window.
    old_bucket, old_drainage = _single_shot(bucket, delta)
    assert drainage < old_drainage
    assert new > old_bucket
    assert new - old_bucket > 0.5


def test_a_fractional_window_and_a_fractional_credit_time():
    """Nothing here arrives whole.

    ``elapsed_hours`` is a fraction of a day scaled by 24, and a credit offset is
    a timedelta in seconds divided by 3600, so integers are the case that never
    occurs. Two credits also share an instant here, which is a zero-length
    segment the walk has to survive.
    """
    bucket, delta, hours = 21.73, -4.61, 23.8642

    new, drainage, runoff, segments = lumped_water_balance(
        bucket,
        delta,
        [(11.2519, 3.87), (11.2519, 1.44), (22.9083, 6.05)],
        hours,
        DRAINAGE_RATE,
        MAXIMUM_BUCKET,
        MAXIMUM_BUCKET,
    )

    assert [round(s.hours, 4) for s in segments] == [11.2519, 0.0, 11.6564, 0.9559]
    assert [s.credit_mm for s in segments] == [1.44, 3.87, 6.05, 0.0]

    level = bucket - (3.87 + 1.44 + 6.05) + delta
    expected_drainage = 0.0
    for span, credit in ((11.2519, 1.44), (0.0, 3.87), (11.6564, 6.05), (0.9559, 0.0)):
        drained = drained_over_window(level, DRAINAGE_RATE, span, MAXIMUM_BUCKET)
        expected_drainage += drained
        level = min(level - drained + credit, MAXIMUM_BUCKET)

    assert drainage == pytest.approx(expected_drainage)
    assert new == pytest.approx(level)
    assert new == pytest.approx(bucket + delta - drainage - runoff)


def test_two_credits_cut_the_window_into_three_segments():
    """k credits are k+1 segments, in time order however they arrive."""
    bucket, delta = 24.0, -6.0
    credits = [(18.0, 4.0), (6.0, 5.0)]

    new, drainage, _runoff, segments = lumped_water_balance(
        bucket, delta, credits, WINDOW, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
    )

    assert [s.hours for s in segments] == [6.0, 12.0, 6.0]
    assert [s.credit_mm for s in segments] == [5.0, 4.0, 0.0]

    level = bucket - 9.0 + delta
    expected_drainage = 0.0
    for hours, credit in ((6.0, 5.0), (12.0, 4.0), (6.0, 0.0)):
        drained = drained_over_window(level, DRAINAGE_RATE, hours, MAXIMUM_BUCKET)
        expected_drainage += drained
        level = min(level - drained + credit, MAXIMUM_BUCKET)

    assert drainage == pytest.approx(expected_drainage)
    assert new == pytest.approx(level)


def test_a_credit_still_in_deficit_after_et_drains_nothing():
    """Drainage acts on surplus only, so a deficit window is untouched."""
    new, drainage, runoff, segments = lumped_water_balance(
        -2.0, -6.0, [(12.0, 5.0)], WINDOW, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
    )

    assert drainage == 0.0
    assert runoff == 0.0
    assert new == pytest.approx(-8.0)
    assert len(segments) == 2


def test_a_credit_stamped_outside_the_window_is_clamped_onto_an_end():
    """The stored bucket already holds it, so it is placed, never dropped."""
    early, *_ = lumped_water_balance(
        18.0,
        -4.0,
        [(-9.0, 20.0)],
        WINDOW,
        DRAINAGE_RATE,
        MAXIMUM_BUCKET,
        MAXIMUM_BUCKET,
    )
    at_start, *_ = lumped_water_balance(
        18.0, -4.0, [(0.0, 20.0)], WINDOW, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
    )
    assert early == at_start

    late, *_ = lumped_water_balance(
        18.0,
        -4.0,
        [(99.0, 20.0)],
        WINDOW,
        DRAINAGE_RATE,
        MAXIMUM_BUCKET,
        MAXIMUM_BUCKET,
    )
    at_end, *_ = lumped_water_balance(
        18.0,
        -4.0,
        [(WINDOW, 20.0)],
        WINDOW,
        DRAINAGE_RATE,
        MAXIMUM_BUCKET,
        MAXIMUM_BUCKET,
    )
    assert late == at_end
    assert late > early


@pytest.mark.parametrize(
    ("bucket", "delta", "credits"),
    [
        (18.0, -4.0, [(18.0, 20.0)]),
        (24.0, -6.0, [(6.0, 5.0), (18.0, 4.0)]),
        (-2.0, -6.0, [(12.0, 5.0)]),
        (20.0, -3.0, []),
    ],
)
def test_the_balance_closes(bucket, delta, credits):
    """Water in minus water out, which is what the explanation claims."""
    new, drainage, runoff, _segments = lumped_water_balance(
        bucket, delta, credits, WINDOW, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
    )
    assert new == pytest.approx(bucket + delta - drainage - runoff)


def test_without_a_maximum_bucket_drainage_stays_constant_rate():
    """No field capacity to scale against, so the fallback rate still applies."""
    new, drainage, runoff, segments = lumped_water_balance(
        30.0, -2.0, [(20.0, 10.0)], WINDOW, 0.5, None, None
    )

    level = 30.0 - 10.0 - 2.0
    first = drained_over_window(level, 0.5, 20.0, None)
    level = level - first + 10.0
    second = drained_over_window(level, 0.5, 4.0, None)

    assert runoff == 0.0
    assert drainage == pytest.approx(first + second)
    assert new == pytest.approx(level - second)
    assert len(segments) == 2


# --------------------------------------------------------------------------
# Through calculate_module
# --------------------------------------------------------------------------


async def test_a_stock_install_credits_a_run_onto_the_drainage_timeline():
    """Reachable with nothing enabled: Irrigate now, then the daily calculation.

    Passthrough keeps the ET deterministic and hourly calculation is off, so this
    is the lumped path a shipped install runs.
    """
    coord = _make_coordinator()
    zone = _zone(
        **{
            const.ZONE_BUCKET: 18.0,
            const.ZONE_PENDING_BUCKET_EVENTS: [_credit(6.0, 20.0)],
        }
    )

    data = await coord.calculate_module(zone, _weather(4.0), None, now=NOW)

    # Priced here from the drainage primitive over the two spans the window has,
    # so this pins the arithmetic and not merely the wiring: an expectation built
    # by calling the helper the code under test calls would survive that helper
    # drifting.
    level = 18.0 - 20.0 - 4.0
    first = drained_over_window(level, DRAINAGE_RATE, 18.0, MAXIMUM_BUCKET)
    level = min(level - first + 20.0, MAXIMUM_BUCKET)
    second = drained_over_window(level, DRAINAGE_RATE, 6.0, MAXIMUM_BUCKET)

    assert data[const.ZONE_BUCKET] == pytest.approx(level - second)
    assert data[const.ZONE_CURRENT_DRAINAGE] == pytest.approx(first + second)

    # Consumed, so a later window cannot replay the same water.
    assert data[const.ZONE_PENDING_BUCKET_EVENTS] == []

    # And wetter than the window-start form the same zone used to get.
    without_credit = await coord.calculate_module(
        _zone(**{const.ZONE_BUCKET: 18.0}), _weather(4.0), None, now=NOW
    )
    assert data[const.ZONE_BUCKET] > without_credit[const.ZONE_BUCKET]


async def test_the_window_opens_at_the_consume_watermark():
    """The credit is placed against the anchor the replayed arm is handed.

    Deriving the window start from the elapsed hours instead agrees exactly while
    a watermark exists, so a zone whose watermark disagrees with the aggregate's
    reported elapsed time is the case that separates the two. Here the watermark
    is six hours further back, which moves the credit six hours later in the
    window and therefore drains it less.
    """
    coord = _make_coordinator()
    zone = _zone(
        **{
            const.ZONE_BUCKET: 18.0,
            const.ZONE_LAST_CONSUMED: (NOW - datetime.timedelta(hours=30)).isoformat(),
            const.ZONE_PENDING_BUCKET_EVENTS: [_credit(6.0, 20.0)],
        }
    )

    data = await coord.calculate_module(zone, _weather(4.0), None, now=NOW)

    # The aggregate still reports a 24 h window, so only the placement moves.
    level = 18.0 - 20.0 - 4.0
    first = drained_over_window(level, DRAINAGE_RATE, 24.0, MAXIMUM_BUCKET)
    level = min(level - first + 20.0, MAXIMUM_BUCKET)

    assert data[const.ZONE_BUCKET] == pytest.approx(level)
    assert data[const.ZONE_CURRENT_DRAINAGE] == pytest.approx(first)


async def test_a_window_with_no_credits_is_untouched_end_to_end():
    """The same zone with no pending events keeps the shipped numbers."""
    coord = _make_coordinator()
    data = await coord.calculate_module(
        _zone(**{const.ZONE_BUCKET: 20.0}), _weather(3.0), None, now=NOW
    )

    expected_bucket, expected_drainage = _single_shot(20.0, -3.0)
    assert data[const.ZONE_BUCKET] == expected_bucket
    assert data[const.ZONE_CURRENT_DRAINAGE] == expected_drainage
    # The single-shot wording, not the segmented one.
    assert "&rarr;(" not in data[const.ZONE_EXPLANATION]


def _chain(explanation):
    """The printed drainage walk as ``[(level_in, span, level_out, credit)]``."""
    body = explanation.split("W = ")[1].split(", [")[0]
    steps = re.findall(
        r"([-\d.]+)\s*&rarr;\(([\d.]+) \[hours\]\) ([-\d.]+)(?: \+ ([\d.]+) = )?",
        "W = " + body,
    )
    return [
        (float(a), float(b), float(c), float(d) if d else 0.0) for a, b, c, d in steps
    ]


async def test_the_credited_explanation_reports_the_walk_it_actually_took():
    """The printed walk has to be arithmetic a reader can follow and check.

    Substrings would pass on a chain whose levels do not join up. These assert
    the two claims the wording makes: every step's drop is the drainage the step
    charged, and the credits carry the level from one step into the next.
    """
    coord = _make_coordinator()
    zone = _zone(
        **{
            const.ZONE_BUCKET: 24.0,
            const.ZONE_PENDING_BUCKET_EVENTS: [_credit(18.0, 4.0), _credit(6.0, 5.0)],
        }
    )

    data = await coord.calculate_module(zone, _weather(6.0), None, now=NOW)
    explanation = data[const.ZONE_EXPLANATION]
    walk = _chain(explanation)

    assert [span for _, span, _, _ in walk] == [6.0, 12.0, 6.0]
    assert [credit for _, _, _, credit in walk] == [4.0, 5.0, 0.0]

    # Each step drops by the drainage that step is charged, and the credit hands
    # the level to the step after it.
    for index, (level_in, span, level_out, credit) in enumerate(walk):
        drained = drained_over_window(level_in, DRAINAGE_RATE, span, MAXIMUM_BUCKET)
        assert level_out == pytest.approx(level_in - drained, abs=0.005)
        if index + 1 < len(walk):
            assert walk[index + 1][0] == pytest.approx(
                min(level_out + credit, MAXIMUM_BUCKET), abs=0.005
            )

    assert walk[-1][2] == pytest.approx(data[const.ZONE_BUCKET], abs=0.005)
    assert f"[drainage] = {data[const.ZONE_CURRENT_DRAINAGE]:.2f}" in explanation


async def test_a_credited_window_that_never_drains_says_so():
    """A credit landing on a zone still in deficit renders no false arithmetic.

    The single-shot drainage sentences are written around ``bucket + delta``,
    which is the level AFTER the credit went back in. On a window whose every
    segment sat in deficit that is not the level anything was tested against, and
    the sentence and the summary below it would contradict each other.
    """
    coord = _make_coordinator()
    zone = _zone(
        **{
            const.ZONE_BUCKET: 5.0,
            const.ZONE_MAXIMUM_BUCKET: None,
            const.ZONE_DRAINAGE_RATE: 1.0,
            const.ZONE_PENDING_BUCKET_EVENTS: [_credit(0.0, 10.0)],
        }
    )

    data = await coord.calculate_module(zone, _weather(1.0), None, now=NOW)
    explanation = data[const.ZONE_EXPLANATION]

    assert data[const.ZONE_CURRENT_DRAINAGE] == 0.0
    assert data[const.ZONE_BUCKET] == pytest.approx(4.0)
    # The walk, and no sentence describing a surplus draining, because none did.
    assert "W = -6.00 &rarr;(24.00 [hours]) -6.00 + 10.00 = 4.00" in explanation
    assert "[drainage] = 0.00" in explanation
    assert "drains continuously over the window" not in explanation
    # Nothing claiming a computation that did not run.
    assert "min([old_bucket]" not in explanation
    assert "Current drainage is 0 because" not in explanation


async def test_the_replayed_arm_never_reaches_the_lumped_split(monkeypatch):
    """Hourly calculation on is still the replay, asserted rather than assumed."""
    from custom_components.irrigation_plus import calculation

    def _refuse(*args, **kwargs):
        raise AssertionError("the replayed arm must not lump the balance")

    monkeypatch.setattr(calculation, "lumped_water_balance", _refuse)

    steps = [
        WaterStep(dt_hours=18.0, et_weight=0.75, precip_mm=0.0, applied_mm=0.0),
        WaterStep(dt_hours=6.0, et_weight=0.25, precip_mm=0.0, applied_mm=20.0),
    ]
    coord = _make_coordinator()
    coord._substeps_for_zone = lambda *args, **kwargs: steps

    zone = _zone(
        **{
            const.ZONE_BUCKET: 18.0,
            const.ZONE_PENDING_BUCKET_EVENTS: [_credit(6.0, 20.0)],
        }
    )
    data = await coord.calculate_module(zone, _weather(4.0), None, now=NOW)

    expected, drainage, _runoff = replay_water_balance(
        18.0 - 20.0,
        -4.0,
        steps,
        DRAINAGE_RATE,
        MAXIMUM_BUCKET,
        MAXIMUM_BUCKET,
    )
    assert data[const.ZONE_BUCKET] == pytest.approx(expected)
    assert data[const.ZONE_CURRENT_DRAINAGE] == pytest.approx(drainage)
