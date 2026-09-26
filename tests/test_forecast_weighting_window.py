"""The forecast weighting prices the run's own window (Eifel-Joe#21).

The weighting summed get_forecast_data by position, and that list starts tomorrow
by contract, so it priced calendar days from tomorrow whatever day and hour the
run fell on. Measured on 10bb8077: a zone whose run is the day after tomorrow
watered its full 10 mm deficit the night before 8 mm of rain -- 6 mm over-watered
on that one forecast.

Seven dated days in every fixture: see _days in test_experimental_features.
"""

import datetime

import pytest

from custom_components.irrigation_plus import const

from .test_experimental_features import _calc_coordinator, _days, _weather, _zone

UTC = datetime.timezone.utc


def _run_at(coord, when):
    coord.recurring_schedule_manager.async_next_run_start_for_zone.return_value = when


async def test_rain_inside_the_runs_window_is_weighted():
    """8 mm falls on the run's own day, which is position 1 of the list."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    # Run at 06:00 on the second forecast day, so its first 24 h is 18/24 of that
    # day plus 6/24 of the next: 8 mm * 18/24 = 6 mm.
    _run_at(coord, datetime.datetime(2026, 9, 28, 6, 0, tzinfo=UTC))

    data = await coord.calculate_module(_zone(), _weather(10.0), _days(0.0, 8.0))

    assert data[const.ZONE_BUCKET] == pytest.approx(-10.0)
    # 10 mm deficit less 6 mm expected rain, at 60 mm/h -> 4 mm -> 240 s.
    assert data[const.ZONE_DURATION] == 240
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(-6.0)


async def test_rain_outside_the_runs_window_is_not_weighted():
    """The mirror: rain on the list's first day, run two days later."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    _run_at(coord, datetime.datetime(2026, 9, 29, 6, 0, tzinfo=UTC))

    data = await coord.calculate_module(_zone(), _weather(10.0), _days(8.0))

    # Position 0 carried the rain, and master would have weighted on it.
    assert data[const.ZONE_DURATION] == 600
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)


async def test_a_zone_with_no_resolvable_run_is_not_weighted(caplog):
    """No enabled schedule names it, so there is no window to price."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    _run_at(coord, None)

    data = await coord.calculate_module(_zone(), _weather(10.0), _days(8.0))

    assert data[const.ZONE_DURATION] == 600
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)
    assert any(
        "no scheduled run" in r.getMessage() and "zone 1" in r.getMessage()
        for r in caplog.records
    ), caplog.text


async def test_a_window_the_forecast_does_not_cover_is_not_weighted(caplog):
    """Mirrors the skip guard, which refuses to decide on an uncovered first 24 h.

    Two dated days only, so the run's block is 18/24 covered. Abstaining means
    watering the full amount, which is the safe direction for a feature whose job
    is to water less.
    """
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=1)
    _run_at(coord, datetime.datetime(2026, 9, 28, 6, 0, tzinfo=UTC))
    short = _days(0.0, 8.0)[:2]

    data = await coord.calculate_module(_zone(), _weather(10.0), short)

    assert data[const.ZONE_DURATION] == 600
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)
    assert any(
        "does not cover" in r.getMessage() for r in caplog.records
    ), caplog.text
