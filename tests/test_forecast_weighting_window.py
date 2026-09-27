"""The forecast weighting prices the run's own window (#159).

The weighting summed get_forecast_data by position, and that list starts tomorrow
by contract, so it priced calendar days from tomorrow whatever day and hour the
run fell on. Measured before the fix: a zone whose run is the day after tomorrow
watered its full 10 mm deficit the night before 8 mm of rain -- 6 mm over-watered
on that one forecast.

Seven dated days in every fixture: see _days in test_experimental_features.
"""

import datetime

import pytest

from custom_components.irrigation_plus import const

from .test_experimental_features import (
    NOW,
    RUN_START,
    _calc_coordinator,
    _days,
    _pin_the_evaluation_moment,  # noqa: F401  autouse; applies by being imported
    _weather,
    _zone,
)

UTC = datetime.timezone.utc


def _run_at(coord, when):
    coord.recurring_schedule_manager.async_next_run_start_for_zone.return_value = when


async def test_rain_inside_the_runs_window_is_weighted():
    """8 mm falls on the run's own day, which is position 1 of the list."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    # Run at 06:00 on the second forecast day, so its first 24 h is 18/24 of that
    # day plus 6/24 of the next: 8 mm * 18/24 = 6 mm.
    _run_at(coord, RUN_START + datetime.timedelta(days=1, hours=6))

    data = await coord.calculate_module(_zone(), _weather(10.0), _days(0.0, 8.0))

    assert data[const.ZONE_BUCKET] == pytest.approx(-10.0)
    # 10 mm deficit less 6 mm expected rain, at 60 mm/h -> 4 mm -> 240 s.
    assert data[const.ZONE_DURATION] == 240
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(-6.0)


async def test_rain_outside_the_runs_window_is_not_weighted():
    """The mirror: rain on the list's first day, run two days later."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    _run_at(coord, RUN_START + datetime.timedelta(days=2, hours=6))

    data = await coord.calculate_module(_zone(), _weather(10.0), _days(8.0))

    # Position 0 carried the rain, and master would have weighted on it.
    assert data[const.ZONE_DURATION] == 600
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)


def _hourly_covering_the_first_block(mm_per_hour_for_first_three):
    """24 stamps at one-hour spacing from NOW, covering block 0 exactly.

    Each rate covers the hour ENDING at its stamp and the first reaches back one
    step, so 24 stamps span [NOW, NOW+24h) -- the whole first block.
    The series has to cover the block WHOLE rather than hand over to the dated
    dailies partway: _entries_behind leaves out any entry that overlaps the series
    or starts exactly at its end, so a seam would leave the block uncovered and the
    weighting would abstain for a reason that has nothing to do with the test.
    """
    return [
        (
            NOW + datetime.timedelta(hours=hour),
            mm_per_hour_for_first_three if hour <= 3 else 0.0,
        )
        for hour in range(1, 25)
    ]


async def test_a_zone_no_schedule_names_is_weighted_from_the_calculation():
    """No enabled schedule names it, so the window starts at the calculation.

    The precipitation skip guard -- the other half of this same Precipitation
    forecast days setting, and the module this reuses -- already anchors at the
    evaluation when no run start is named (skip_conditions.py:235). Abstaining here
    would leave the two halves of one dropdown diverged in a second place, which is
    the thing this change exists to end.
    Cost, stated: someone calculating at 03:00 and watering from an automation at
    20:00 gets a window anchored 17 h early -- bounded by one day, and the same
    trade the guard already makes.
    """
    coord = _calc_coordinator(
        forecast_weighting=True,
        use_weather_service=True,
        days=1,
        hourly=_hourly_covering_the_first_block(2.0),
    )
    _run_at(coord, None)

    data = await coord.calculate_module(_zone(), _weather(10.0), _days(0.0))

    # 2 mm/h over the first three hours -> 6 mm; a 10 mm deficit less 6 mm at
    # 60 mm/h -> 4 mm -> 240 s.
    assert data[const.ZONE_DURATION] == 240
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(-6.0)


async def test_a_zone_no_schedule_names_still_refuses_an_uncovered_window(caplog):
    """The first_24h_covered refusal survives the fallback, and bounds it.

    With no hourly series nothing forecasts the hours between the evaluation and
    the first dated day, so the block is not covered and the weighting still
    abstains. That is what the fallback actually buys: it reaches zones whose
    client serves an hourly series, which all four do.
    """
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    _run_at(coord, None)

    data = await coord.calculate_module(_zone(), _weather(10.0), _days(8.0))

    assert data[const.ZONE_DURATION] == 600
    assert any("does not cover" in r.getMessage() for r in caplog.records), caplog.text


async def test_a_window_the_forecast_does_not_cover_is_not_weighted(caplog):
    """Mirrors the skip guard, which refuses to decide on an uncovered first 24 h.

    Two dated days only, so the run's block is 18/24 covered. Abstaining means
    watering the full amount, which is the safe direction for a feature whose job
    is to water less.
    """
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    _run_at(coord, RUN_START + datetime.timedelta(days=1, hours=6))
    short = _days(0.0, 8.0)[:2]

    data = await coord.calculate_module(_zone(), _weather(10.0), short)

    assert data[const.ZONE_DURATION] == 600
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)
    assert any(
        "does not cover" in r.getMessage() for r in caplog.records
    ), caplog.text


async def test_a_caller_supplied_run_start_wins_over_the_resolver():
    """The run start the caller KNOWS beats the one the schedules imply.

    The resolver is made to raise rather than mocked quiet: inside a dispatch it
    answers for the FOLLOWING run, so a silent fallback would hide the very defect
    this parameter exists for.
    """
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    coord.recurring_schedule_manager.async_next_run_start_for_zone.side_effect = (
        AssertionError("the resolver must not be consulted when a start is given")
    )

    data = await coord.calculate_module(
        _zone(),
        _weather(10.0),
        _days(0.0, 8.0),
        run_start=RUN_START + datetime.timedelta(days=1, hours=6),
    )

    # Same window as test_rain_inside_the_runs_window_is_weighted: 8 mm * 18/24.
    assert data[const.ZONE_DURATION] == 240
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(-6.0)
