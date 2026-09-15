"""Expected precipitation over a run's calendar days.

Pure arithmetic -- no Home Assistant import -- so the window can be checked
against hand-computed numbers. The precipitation skip guard hands it the
configured client's hourly precipitation series and its dated daily entries,
and Home Assistant's own time zone decides which calendar days a run covers.

The window starts at the run's own local DATE and spans ``days`` calendar days
from there. The guard used to sum whole days out of ``get_forecast_data``,
which by contract starts tomorrow; evaluated at dispatch on the morning of a
run, that put the first day of the window one day AFTER the run, so the day it
rained was never examined (#137). Hours before the evaluation are cut off, so a
run that starts in the evening with a one-day window sees only the rest of its
own day.

Known imprecisions, each bounded:

* Pirate Weather's hourly points are read as ending at their stamp, which its
  client marks as assumed; if they begin there, the run date's total is off by
  one hour of rain at each end. Its daily spans run from one block's time to
  the next, read as local midnight as the API documentation describes it --
  taken from the documentation, not measured against a live response.
* Open-Meteo converts its local stamps with the document's single
  ``utc_offset_seconds``, so hours after a daylight-saving change inside the
  document sit an hour off.
* Met Office groups its three-hourly product by UTC date, and the entry for
  the product's last date spans the whole day although its total holds only
  the steps up to where the product ends. When the hourly document serves the
  series, that entry lies behind it and counts as covering its whole day, so
  the total is short while the day reports as complete. It under-counts, which
  errs towards watering, and only a window reaching that date sees it.
* Pirate Weather's hourly block, fetched without ``extend=hourly``, and Met
  Office's hourly document reach 48 hours. The daily entry for the day such a
  series ends in starts before that end and is left out, so the rest of that
  day is uncovered. Checked on the run's date, a window of three or more days
  loses most of its third day while the first two are complete; a preview the
  evening before loses a few hours of the second. It under-counts, which errs
  towards watering. OWM (five days, three-hourly) and Open-Meteo (seven days)
  are not affected.
* ``day_projection.forecast_rain_mm`` integrates the same series for the
  next-run projection but declines when the series starts after the span. Here
  the first sample reaches back one step, which is what lets a three-hourly
  series cover the hours just after a fetch. The two can disagree on whether a
  span is covered; the difference is deliberate, do not fix one side only.
"""

from __future__ import annotations

import datetime
import math
from typing import NamedTuple

from .const import FORECAST_DAY_END, FORECAST_DAY_START, MAPPING_PRECIPITATION

_UTC = datetime.timezone.utc
_SECONDS_PER_HOUR = 3600.0
# A covered span within this many seconds of the requested one counts as whole.
_COVERAGE_TOLERANCE_SECONDS = 1.0


class ExpectedRain(NamedTuple):
    """Forecast rain over a run's window, and how much of the window was covered."""

    mm: float
    # The run's own date was fully covered by the hourly series or daily entries.
    run_date_covered: bool
    # Every day of the window was fully covered.
    complete: bool


def day_span(entry):
    """``(start, end)`` in UTC of the day a daily forecast entry covers, or None.

    The one reader of ``FORECAST_DAY_START``/``FORECAST_DAY_END``: the panel
    labels a day from it and the skip guard weighs a day with it, so the two
    cannot disagree about which entries carry a usable span. The rules they apply
    to a span differ on purpose -- the panel names the local date holding its
    middle, the guard counts it by overlap. None unless both ends are present,
    carry a time zone, and the end lies after the start.
    """
    start = entry.get(FORECAST_DAY_START)
    end = entry.get(FORECAST_DAY_END)
    if not isinstance(start, datetime.datetime) or not isinstance(
        end, datetime.datetime
    ):
        return None
    if start.utcoffset() is None or end.utcoffset() is None:
        return None
    start, end = start.astimezone(_UTC), end.astimezone(_UTC)
    if end <= start:
        return None
    return start, end


def _local_midnight_utc(day: datetime.date, tz) -> datetime.datetime:
    # Built in the zone, then converted: subtracting two datetimes that share one
    # ZoneInfo is wall-clock arithmetic and would give a 25-hour day 24 hours.
    return datetime.datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(_UTC)


def window_intervals(run_start, days, tz, evaluated_at):
    """``[(index, start, end)]`` in UTC for the run's local date and the days after it.

    Each day runs from local midnight to the next, so a daylight-saving change
    gives it 23 or 25 hours. The part before ``evaluated_at`` is cut off, because
    a forecast says nothing about hours that have already passed; a day that is
    entirely past is left out. ``index`` 0 is the run's own date.
    """
    run_date = run_start.astimezone(tz).date()
    evaluated = evaluated_at.astimezone(_UTC)
    out = []
    for index in range(max(1, int(days))):
        day = run_date + datetime.timedelta(days=index)
        start = max(_local_midnight_utc(day, tz), evaluated)
        end = _local_midnight_utc(day + datetime.timedelta(days=1), tz)
        if start < end:
            out.append((index, start, end))
    return out


def _overlap_seconds(a_start, a_end, b_start, b_end) -> float:
    return max(0.0, (min(a_end, b_end) - max(a_start, b_start)).total_seconds())


def _hourly_segments(series):
    """``[(start, end, mm_per_hour)]`` in UTC from a client's ``[(stamp, rate)]``.

    Wurzel: a sample's length used to be the gap to the previous stamp. Open-Meteo
      and Pirate Weather drop a row without a value, so a missing hour stretched
      the next rate back across the gap: its water multiplied and the gap counted
      as forecast.
    Fix-Logik: each rate covers the interval ENDING at its stamp, the convention
      every client hands back, but never more than one step of the series, its
      smallest spacing. The first sample reaches back one step. A longer spacing
      is a hole the caller sees as uncovered. A duplicated stamp keeps its highest
      rate; a rate that is not a finite number is dropped, a negative one is dry.
    NOT-TO-DO: do not cap at a fixed length such as three hours: an hourly series
      with a two-hour hole would still stretch. Met Office already spreads its
      amounts over its own gaps, so capping under-counts there -- the direction
      that waters rather than skips. And check ``math.isfinite`` before any
      ``max``: ``max(0.0, nan)`` is ``0.0`` and would turn a hole into a dry hour.
    siehe tests/test_forecast_window.py
    """
    rates = {}
    for stamp, rate in series or []:
        if stamp is None or rate is None:
            continue
        try:
            value = float(rate)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(value):
            continue
        key = stamp.astimezone(_UTC)
        rates[key] = max(rates.get(key, 0.0), value, 0.0)
    stamps = sorted(rates)
    if not stamps:
        return []
    spacings = [
        later - earlier for earlier, later in zip(stamps, stamps[1:], strict=False)
    ]
    step = min(spacings) if spacings else datetime.timedelta(hours=1)
    return [(stamp - step, stamp, rates[stamp]) for stamp in stamps]


def _entries_behind(daily, series_end):
    """``[(start, end, mm)]`` for dated daily entries lying behind the hourly series.

    Wurzel: OWM builds its days from the same three-hourly list its hourly series
      comes from. Its last day holds only the slots up to the series' end while
      its span claims the whole day, and a slot stamped 00Z is filed under the new
      day although its rain fell in the three hours before. Filling from such an
      entry counted rain the series had already counted, and reported the day as
      complete.
    Fix-Logik: an entry fills in only where the series has nothing to say -- its
      span has to start AFTER the series' last stamp. An entry that overlaps the
      series, or starts exactly at its end, is left out whole, so the rest of its
      day is uncovered. That under-counts, which errs towards watering. Daily
      entries are assumed not to overlap each other, as every client builds
      them; overlapping ones would be counted twice.
    NOT-TO-DO: do not shorten the span in the client. The panel labels a day by
      the middle of that span, so the client's span has to stay the whole day.
    siehe tests/test_forecast_window.py::test_daily_entries_fill_in_only_behind_the_hourly_series
      und ::test_owm_s_last_day_starting_at_the_series_end_is_not_counted_again
    """
    out = []
    for entry in daily or []:
        if not isinstance(entry, dict):
            continue
        span = day_span(entry)
        if span is None:
            continue
        try:
            mm = float(entry.get(MAPPING_PRECIPITATION))
        except (TypeError, ValueError):
            continue
        if not math.isfinite(mm):
            continue
        start, end = span
        if series_end is not None and start <= series_end:
            continue
        out.append((start, end, max(0.0, mm)))
    return out


def expected_rain(*, run_start, evaluated_at, days, tz, hourly, daily) -> ExpectedRain:
    """Forecast precipitation on the run's local date and the ``days - 1`` after it.

    The hourly series is integrated wherever it reaches. Dated daily entries that
    start after it fill in, each counted by the share of its own span that falls
    inside the window -- a UTC-day entry thus contributes to a local date in
    proportion to their overlap. Coverage is reported per day so the caller can
    refuse to decide on a run date nothing forecast; a run date already past at
    the evaluation counts as uncovered.
    """
    intervals = window_intervals(run_start, days, tz, evaluated_at)
    segments = _hourly_segments(hourly)
    series_end = segments[-1][1] if segments else None
    pieces = [(start, end, rate / _SECONDS_PER_HOUR) for start, end, rate in segments]
    pieces += [
        (start, end, mm / (end - start).total_seconds())
        for start, end, mm in _entries_behind(daily, series_end)
    ]
    total = 0.0
    run_date_covered = bool(intervals) and intervals[0][0] == 0
    complete = run_date_covered
    for index, start, end in intervals:
        covered = 0.0
        for piece_start, piece_end, per_second in pieces:
            seconds = _overlap_seconds(start, end, piece_start, piece_end)
            total += per_second * seconds
            covered += seconds
        if covered < (end - start).total_seconds() - _COVERAGE_TOLERANCE_SECONDS:
            complete = False
            if index == 0:
                run_date_covered = False
    return ExpectedRain(total, run_date_covered, complete)
