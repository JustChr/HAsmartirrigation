"""Tests for the intra-day live-estimate orchestration (live_estimate).

Focus on the parts that can't be validated against live weather data: the
since-last-calc window (the double-count fix) and the imperial unit conversion.
"""

import datetime
from types import SimpleNamespace

from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation.et_estimate import rigorous_et_since
from custom_components.smart_irrigation.live_estimate import (
    LiveEstimateMixin,
    _parse_utc_naive,
)


class _Coord(LiveEstimateMixin):
    def __init__(self, units):
        self.hass = SimpleNamespace(config=SimpleNamespace(units=units))


def _client():
    return SimpleNamespace(latitude=48.39, longitude=16.23, elevation=180)


def _rows():
    """A few daytime hours 'today' (local naive ISO strings)."""
    base = datetime.date.today()
    rows = []
    for hr, solar in ((10, 2.0), (11, 2.2), (12, 2.4), (13, 2.3)):
        rows.append(
            {
                "time": f"{base.isoformat()}T{hr:02d}:00",
                "hour": hr + 0.5,
                "doy": base.timetuple().tm_yday,
                "temperature": 26.0,
                "humidity": 45.0,
                "wind_2m": 2.0,
                "solar_mj_h": solar,
                "precipitation": 0.0,
            }
        )
    return rows


def test_parse_utc_naive():
    aware = datetime.datetime(2026, 6, 7, 12, tzinfo=datetime.timezone.utc)
    assert _parse_utc_naive(aware) == datetime.datetime(2026, 6, 7, 12)
    assert _parse_utc_naive("2026-06-07T12:00:00") == datetime.datetime(2026, 6, 7, 12)
    assert _parse_utc_naive(None) is None
    assert _parse_utc_naive("not-a-date") is None


def test_rows_since_filters_to_after_last_calc():
    rows = _rows()  # hours 10..13 local
    # last calc today 11:00 LOCAL -> with tz +2, that's 09:00 UTC naive
    last_calc_utc = datetime.datetime.combine(
        datetime.date.today(), datetime.time(9, 0)
    )
    window = LiveEstimateMixin._rows_since(rows, last_calc_utc, 2.0)
    hours = [r["hour"] for r in window]
    # hours whose end (>hour+1) is after 11:00 local -> 11,12,13 (the 11:00 row
    # ends at 12:00 > 11:00). The 10:00 row (ends 11:00) is excluded.
    assert hours == [11.5, 12.5, 13.5]


def test_rows_since_none_returns_all():
    rows = _rows()
    assert LiveEstimateMixin._rows_since(rows, None, 2.0) == rows


def test_intraday_metric_hourly_balance():
    coord = _Coord(METRIC_SYSTEM)
    inputs = {"client": _client(), "rows": _rows(), "tz": 2.0, "forecast": None}
    zone = {"bucket": -2.0, "maximum_bucket": 24, "last_calculated": None}
    est = coord._intraday_for_zone(zone, inputs)

    et = rigorous_et_since(_rows(), 48.39, 16.23, 2.0, 180)
    assert est["available"] is True
    assert est["method"] == "hourly"
    assert abs(est["et_since"] - round(et, 2)) < 1e-9
    assert abs(est["live_deficit"] - round(-2.0 - et, 2)) < 1e-9


def test_intraday_imperial_converts_units():
    coord = _Coord(US_CUSTOMARY_SYSTEM)
    inputs = {"client": _client(), "rows": _rows(), "tz": 2.0, "forecast": None}
    # bucket given in inches
    zone = {"bucket": -0.1, "maximum_bucket": 1.0, "last_calculated": None}
    est = coord._intraday_for_zone(zone, inputs)

    et_mm = rigorous_et_since(_rows(), 48.39, 16.23, 2.0, 180)
    bucket_mm = -0.1 * 25.4
    expected_live_in = (bucket_mm - et_mm) / 25.4
    assert est["available"] is True
    # result is reported in inches; ET is positive, so deficit grows (more negative)
    assert est["live_deficit"] < -0.1
    assert abs(est["live_deficit"] - round(expected_live_in, 3)) < 1e-3


def test_intraday_unavailable_without_bucket_or_coords():
    coord = _Coord(METRIC_SYSTEM)
    rows = _rows()
    # missing bucket
    inputs = {"client": _client(), "rows": rows, "tz": 2.0, "forecast": None}
    assert (
        coord._intraday_for_zone({"last_calculated": None}, inputs)["available"]
        is False
    )
    # missing coords
    bad = {
        "client": SimpleNamespace(latitude=None, longitude=None, elevation=0),
        "rows": rows,
        "tz": 2.0,
        "forecast": None,
    }
    zone = {"bucket": -1.0, "last_calculated": None}
    assert coord._intraday_for_zone(zone, bad)["available"] is False
