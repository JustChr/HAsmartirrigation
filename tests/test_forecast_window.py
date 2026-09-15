"""Expected precipitation over a run's calendar days.

Every number below is hand-computed. Series follow the clients' convention: a
rate in mm/h covering the interval that ENDS at its stamp. Time zones are passed
explicitly; nothing here reads Home Assistant's.
"""

import datetime
import math
import zoneinfo

import pytest

from custom_components.irrigation_plus.const import (
    FORECAST_DAY_END,
    FORECAST_DAY_START,
    MAPPING_PRECIPITATION,
)
from custom_components.irrigation_plus.forecast_window import day_span, expected_rain

UTC = datetime.timezone.utc
PLUS2 = datetime.timezone(datetime.timedelta(hours=2))
BERLIN = zoneinfo.ZoneInfo("Europe/Berlin")


def _utc(*args):
    return datetime.datetime(*args, tzinfo=UTC)


def _hourly(first_hour_start, hours, rate):
    """``hours`` samples of ``rate``, stamped at the END of each hour."""
    return [
        (first_hour_start + datetime.timedelta(hours=i + 1), rate) for i in range(hours)
    ]


def _day(start, mm):
    return {
        FORECAST_DAY_START: start,
        FORECAST_DAY_END: start + datetime.timedelta(days=1),
        MAPPING_PRECIPITATION: mm,
    }


def test_the_rest_of_the_run_day_counts_from_the_evaluation():
    # 06:00 local (+02) on the 13th is 04:00 UTC; the local 13th ends 22:00 UTC.
    at = _utc(2026, 9, 13, 4, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=PLUS2,
        hourly=_hourly(_utc(2026, 9, 12, 22, 0), 24, 1.0),
        daily=[],
    )
    assert rain.mm == pytest.approx(18.0)
    assert rain.run_date_covered is True
    assert rain.complete is True


def test_the_evening_before_looks_at_the_run_date():
    # Evaluated 20:00 local on the 12th for a run at 06:00 local on the 13th.
    # Heavy rain late on the 12th is not on the run's date and must not count.
    hourly = _hourly(_utc(2026, 9, 12, 18, 0), 4, 5.0) + _hourly(
        _utc(2026, 9, 12, 22, 0), 24, 1.0
    )
    rain = expected_rain(
        run_start=_utc(2026, 9, 13, 4, 0),
        evaluated_at=_utc(2026, 9, 12, 18, 0),
        days=1,
        tz=PLUS2,
        hourly=hourly,
        daily=[],
    )
    assert rain.mm == pytest.approx(24.0)


def test_a_three_hourly_slot_across_midnight_is_split():
    # Local 13th (+02) is 12th 22:00Z .. 13th 22:00Z. The slot stamped 14th 00:00Z
    # covers 21:00Z .. 00:00Z, so one of its three hours falls inside.
    stamps = [
        _utc(2026, 9, 13, 0, 0) + datetime.timedelta(hours=3 * k) for k in range(9)
    ]
    hourly = [(s, 0.0) for s in stamps[:-1]] + [(stamps[-1], 3.0)]
    at = _utc(2026, 9, 12, 22, 0)
    rain = expected_rain(
        run_start=at, evaluated_at=at, days=1, tz=PLUS2, hourly=hourly, daily=[]
    )
    assert rain.mm == pytest.approx(3.0)
    assert rain.complete is True


def test_a_day_with_the_clocks_going_back_has_25_hours():
    # Local midnight of 2026-10-25 is 24th 22:00Z; the next local midnight is
    # 25th 23:00Z, because the clocks go back an hour that night.
    at = _utc(2026, 10, 24, 22, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=BERLIN,
        hourly=_hourly(at, 30, 1.0),
        daily=[],
    )
    assert rain.mm == pytest.approx(25.0)
    assert rain.complete is True


def test_24_hours_of_forecast_do_not_cover_a_25_hour_day():
    # The series stops at 25th 22:00Z, an hour before the local day ends. Measured
    # in wall-clock time the day would look like 24 hours and the missing hour
    # would pass unnoticed.
    at = _utc(2026, 10, 24, 22, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=BERLIN,
        hourly=_hourly(at, 24, 1.0),
        daily=[],
    )
    assert rain.mm == pytest.approx(24.0)
    assert rain.run_date_covered is False
    assert rain.complete is False


def test_a_day_with_the_clocks_going_forward_has_23_hours():
    # Local midnight of 2026-03-29 is 28th 23:00Z; the next is 29th 22:00Z.
    at = _utc(2026, 3, 28, 23, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=BERLIN,
        hourly=_hourly(at, 30, 1.0),
        daily=[],
    )
    assert rain.mm == pytest.approx(23.0)
    assert rain.complete is True


def test_a_gap_in_the_series_is_a_hole_not_a_stretch_of_the_next_rate():
    # Open-Meteo and Pirate Weather drop an hour without a value. The rows ending
    # 07:00..12:00 are missing; the 13:00 row forecasts 2 mm/h for 12:00-13:00.
    # Stretched back over the gap it would read as 14 mm, and the gap as forecast.
    at = _utc(2026, 9, 13, 0, 0)
    stamps = [at + datetime.timedelta(hours=h) for h in range(1, 25)]
    series = [
        (s, 2.0 if s.hour == 13 else 0.0) for s in stamps if not 7 <= s.hour <= 12
    ]
    rain = expected_rain(
        run_start=at, evaluated_at=at, days=1, tz=UTC, hourly=series, daily=[]
    )
    assert rain.mm == pytest.approx(2.0)
    assert rain.run_date_covered is False
    assert rain.complete is False


@pytest.mark.parametrize(
    "rates", [(4.0, 0.0), (0.0, 4.0)], ids=["high-first", "low-first"]
)
def test_a_duplicated_stamp_keeps_its_highest_rate(rates):
    # Whichever of the two rows a client lists last must not decide.
    at = _utc(2026, 9, 13, 0, 0)
    series = _hourly(at, 24, 0.0)
    stamp = series[5][0]
    series[5:6] = [(stamp, rates[0]), (stamp, rates[1])]
    rain = expected_rain(
        run_start=at, evaluated_at=at, days=1, tz=UTC, hourly=series, daily=[]
    )
    assert rain.mm == pytest.approx(4.0)
    assert rain.complete is True


def test_a_negative_rate_counts_as_a_dry_covered_hour():
    # A negative rate is a model artifact, not a missing hour: it must neither
    # subtract water nor leave a hole that stops the guard deciding.
    at = _utc(2026, 9, 13, 0, 0)
    series = _hourly(at, 24, 1.0)
    series[2] = (series[2][0], -5.0)  # 02:00-03:00 dry
    rain = expected_rain(
        run_start=at, evaluated_at=at, days=1, tz=UTC, hourly=series, daily=[]
    )
    assert rain.mm == pytest.approx(23.0)
    assert rain.run_date_covered is True
    assert rain.complete is True


def test_a_non_number_rate_counts_as_no_forecast():
    at = _utc(2026, 9, 13, 0, 0)
    series = _hourly(at, 24, 1.0)
    series[10] = (series[10][0], math.nan)  # 10:00-11:00 unknown
    rain = expected_rain(
        run_start=at, evaluated_at=at, days=1, tz=UTC, hourly=series, daily=[]
    )
    assert rain.mm == pytest.approx(23.0)
    assert rain.run_date_covered is False
    assert rain.complete is False


@pytest.mark.parametrize(("late", "covered"), [(0.5, True), (2.0, False)])
def test_a_series_starting_just_after_the_evaluation(late, covered):
    # The first sample reaches back one step. What is left before it counts as
    # covered within a second of the evaluation, and not beyond.
    at = _utc(2026, 9, 13, 0, 0)
    first = at + datetime.timedelta(seconds=late)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=UTC,
        hourly=_hourly(first, 25, 0.0),
        daily=[],
    )
    assert rain.run_date_covered is covered


def test_daily_entries_fill_in_only_behind_the_hourly_series():
    # OWM builds its days from the same three-hourly list as its series, and its
    # last day holds only the slots up to the series' end while claiming the whole
    # day. An entry that overlaps the series is therefore left out whole; the rest
    # of that day is reported uncovered rather than guessed.
    at = _utc(2026, 9, 13, 0, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=3,
        tz=UTC,
        # 36 hours of 1 mm/h: the whole 13th and the first half of the 14th
        hourly=_hourly(at, 36, 1.0),
        daily=[_day(_utc(2026, 9, 14), 12.0), _day(_utc(2026, 9, 15), 10.0)],
    )
    # 24 (13th) + 12 (14th, hourly only) + 10 (15th)
    assert rain.mm == pytest.approx(46.0)
    assert rain.run_date_covered is True
    assert rain.complete is False


def test_owm_s_last_day_starting_at_the_series_end_is_not_counted_again():
    # OWM files each three-hourly slot under the UTC date of its stamp and gives
    # the bucket the whole day. Fetched between 00Z and 03Z, the list's last slot
    # is stamped 00Z: its rain fell in the three hours BEFORE, which the series
    # already counts, yet its bucket's span starts exactly at the series' end.
    first = _utc(2026, 9, 13, 3, 0)
    stamps = [first + datetime.timedelta(hours=3 * k) for k in range(40)]
    assert stamps[-1] == _utc(2026, 9, 18, 0, 0)
    hourly = [(s, 1.0 if s == stamps[-1] else 0.0) for s in stamps]
    at = _utc(2026, 9, 17, 0, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=2,
        tz=UTC,
        hourly=hourly,
        # The bucket for the 18th holds that one slot: 3 mm.
        daily=[_day(_utc(2026, 9, 18), 3.0)],
    )
    assert rain.mm == pytest.approx(3.0)
    assert rain.run_date_covered is True
    assert rain.complete is False


def test_without_an_hourly_series_the_run_date_is_reported_uncovered():
    # At dispatch get_forecast_data holds no entry for today, so without an hourly
    # series nothing forecasts the run's own date.
    at = _utc(2026, 9, 13, 6, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=2,
        tz=UTC,
        hourly=[],
        daily=[_day(_utc(2026, 9, 14), 5.0)],
    )
    assert rain.mm == pytest.approx(5.0)
    assert rain.run_date_covered is False
    assert rain.complete is False


def test_a_utc_day_entry_counts_against_a_local_date_by_overlap():
    # Local 13th (+02) is 12th 22:00Z .. 13th 22:00Z; the UTC-day entry for the
    # 13th overlaps it for 22 of its 24 hours. Counting the whole entry for the
    # local date holding its middle -- the panel's label rule -- would say 24.
    at = _utc(2026, 9, 12, 22, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=PLUS2,
        hourly=[],
        daily=[_day(_utc(2026, 9, 13), 24.0)],
    )
    assert rain.mm == pytest.approx(22.0)
    assert rain.run_date_covered is False


def test_an_entry_for_a_day_already_past_contributes_nothing():
    # A daily list parsed before midnight and served from cache afterwards still
    # holds yesterday's entry. Its span no longer meets the window, so it cannot
    # be mistaken for today by its position.
    at = _utc(2026, 9, 13, 6, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=UTC,
        hourly=[],
        daily=[_day(_utc(2026, 9, 12), 50.0)],
    )
    assert rain.mm == pytest.approx(0.0)
    assert rain.run_date_covered is False


def test_a_run_date_already_past_is_not_covered():
    # A projection may name a run that started before midnight. Nothing forecasts
    # its date any more, whatever the days after it hold.
    rain = expected_rain(
        run_start=_utc(2026, 9, 12, 21, 50),
        evaluated_at=_utc(2026, 9, 13, 6, 0),
        days=2,
        tz=UTC,
        hourly=_hourly(_utc(2026, 9, 13, 0, 0), 48, 1.0),
        daily=[],
    )
    assert rain.run_date_covered is False
    assert rain.complete is False


def test_a_one_day_window_on_a_run_date_already_past_is_empty():
    # With a one-day window nothing of the run's date is left at the evaluation,
    # so the window holds no day at all. The rain forecast for the day after must
    # not stand in for it, and an empty window must not break the evaluation.
    rain = expected_rain(
        run_start=_utc(2026, 9, 12, 21, 50),
        evaluated_at=_utc(2026, 9, 13, 6, 0),
        days=1,
        tz=UTC,
        hourly=_hourly(_utc(2026, 9, 13, 0, 0), 48, 1.0),
        daily=[],
    )
    assert rain == (0.0, False, False)


def test_a_daily_total_that_is_not_a_number_or_negative_adds_nothing():
    at = _utc(2026, 9, 13, 0, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=3,
        tz=UTC,
        hourly=[],
        daily=[
            _day(_utc(2026, 9, 13), -10.0),
            _day(_utc(2026, 9, 14), math.nan),
            _day(_utc(2026, 9, 15), 4.0),
        ],
    )
    assert rain.mm == pytest.approx(4.0)
    assert rain.run_date_covered is True
    assert rain.complete is False


def test_day_span_reads_an_aware_span_in_utc():
    start = datetime.datetime(2026, 9, 13, tzinfo=BERLIN)
    entry = {
        FORECAST_DAY_START: start,
        FORECAST_DAY_END: start + datetime.timedelta(days=1),
    }
    span = day_span(entry)
    assert span == (_utc(2026, 9, 12, 22, 0), _utc(2026, 9, 13, 22, 0))
    assert span[0].utcoffset() == datetime.timedelta(0)
    assert span[1].utcoffset() == datetime.timedelta(0)


@pytest.mark.parametrize(
    "entry",
    [
        pytest.param({FORECAST_DAY_END: _utc(2026, 9, 14)}, id="no-start"),
        pytest.param({FORECAST_DAY_START: _utc(2026, 9, 13)}, id="no-end"),
        pytest.param(
            {
                FORECAST_DAY_START: datetime.datetime(2026, 9, 13),
                FORECAST_DAY_END: _utc(2026, 9, 14),
            },
            id="naive",
        ),
        pytest.param(
            {
                FORECAST_DAY_START: _utc(2026, 9, 14),
                FORECAST_DAY_END: _utc(2026, 9, 13),
            },
            id="reversed",
        ),
        pytest.param(
            {
                FORECAST_DAY_START: _utc(2026, 9, 13),
                FORECAST_DAY_END: _utc(2026, 9, 13),
            },
            id="empty",
        ),
    ],
)
def test_day_span_refuses_a_span_it_cannot_place(entry):
    assert day_span(entry) is None


def test_a_single_sample_covers_one_hour():
    # With one stamp there is no spacing to take the step from, so the sample
    # reaches back one hour: 2 mm/h for 11:00-12:00. A longer default step would
    # multiply the water and claim hours nothing forecast.
    at = _utc(2026, 9, 13, 0, 0)
    rain = expected_rain(
        run_start=at,
        evaluated_at=at,
        days=1,
        tz=UTC,
        hourly=[(_utc(2026, 9, 13, 12, 0), 2.0)],
        daily=[],
    )
    assert rain.mm == pytest.approx(2.0)
    assert rain.run_date_covered is False
    assert rain.complete is False
