"""Tests for the intra-day ET accumulation / proxy (et_estimate)."""

import pytest

from custom_components.irrigation_plus.et_estimate import (
    drained_over_window,
    estimate_daily_et0_hargreaves,
    live_deficit,
    proxy_et_since,
    rigorous_et_since,
)
from custom_components.irrigation_plus.et_hourly import eto_hourly

LAT = 48.39
LON = 16.23
DOY = 180  # late June
TZ = 2.0


def test_proxy_full_day_returns_daily_total():
    """Distributing over every hour of the day recovers the daily ETo."""
    midpoints = [h + 0.5 for h in range(24)]
    got = proxy_et_since(5.0, LAT, LON, DOY, TZ, midpoints)
    assert abs(got - 5.0) < 1e-9


def test_proxy_partial_day_is_a_fraction():
    """Part of the day yields part of the daily ETo, and more hours -> more."""
    until_noon = [h + 0.5 for h in range(13)]  # through ~12:30 local
    until_evening = [h + 0.5 for h in range(19)]  # through ~18:30 local
    et_noon = proxy_et_since(5.0, LAT, LON, DOY, TZ, until_noon)
    et_evening = proxy_et_since(5.0, LAT, LON, DOY, TZ, until_evening)
    assert 0.0 < et_noon < et_evening < 5.0


def test_proxy_zero_daily_et_is_zero():
    assert proxy_et_since(0.0, LAT, LON, DOY, TZ, [12.5]) == 0.0
    assert proxy_et_since(5.0, LAT, LON, DOY, TZ, []) == 0.0


def test_rigorous_sums_hourly_eto():
    """rigorous_et_since equals the sum of eto_hourly over the rows."""
    rows = [
        {
            "hour": 12.5,
            "doy": DOY,
            "temperature": 28.0,
            "humidity": 45.0,
            "wind_2m": 2.0,
            "solar_mj_h": 2.6,
        },
        {
            "hour": 13.5,
            "doy": DOY,
            "temperature": 30.0,
            "humidity": 40.0,
            "wind_2m": 2.2,
            "solar_mj_h": 2.7,
        },
    ]
    expected = sum(
        eto_hourly(
            t_c=r["temperature"],
            rh_pct=r["humidity"],
            wind_2m=r["wind_2m"],
            solar_rad_hr=r["solar_mj_h"],
            latitude_deg=LAT,
            longitude_deg=LON,
            doy=r["doy"],
            hour_mid=r["hour"],
            tz_offset_h=TZ,
        )
        for r in rows
    )
    got = rigorous_et_since(rows, LAT, LON, TZ)
    assert abs(got - expected) < 1e-9
    assert got > 0.0


def test_hargreaves_daily_et0_is_plausible():
    """A warm summer day gives a sensible daily ETo (a few mm)."""
    et0 = estimate_daily_et0_hargreaves(15.0, 30.0, LAT, DOY)
    assert 2.0 < et0 < 8.0
    # a cold winter day should be much lower
    winter = estimate_daily_et0_hargreaves(-2.0, 4.0, LAT, 15)
    assert 0.0 <= winter < et0


def test_live_deficit_balance_and_cap():
    # bucket −2.0, lost 1.5 mm ET, gained 0.5 mm rain -> −3.0
    assert abs(live_deficit(-2.0, 1.5, 0.5) - (-3.0)) < 1e-9
    # capped at field capacity (maximum_bucket)
    assert live_deficit(20.0, 0.0, 10.0, maximum_bucket=24.0) == 24.0
    # below the cap it passes through
    assert abs(live_deficit(5.0, 0.0, 3.0, maximum_bucket=24.0) - 8.0) < 1e-9


def test_drained_over_window_noop_cases():
    # no surplus, no rate, or no elapsed time -> nothing drains
    assert drained_over_window(0.0, 1.0, 24.0, 10.0) == 0.0
    assert drained_over_window(-3.0, 1.0, 24.0, 10.0) == 0.0
    assert drained_over_window(5.0, 0.0, 24.0, 10.0) == 0.0
    assert drained_over_window(5.0, 1.0, 0.0, 10.0) == 0.0


def test_drained_over_window_brooks_corey_closed_form():
    # W0=5, rate=1, 24h, max=10, n=4:
    # denom = 1 + 3*1*24*5^3/10^4 = 1.9 ; W_end = 5/1.9^(1/3) = 4.0369
    drained = drained_over_window(5.0, 1.0, 24.0, 10.0)
    assert drained == pytest.approx(0.96306, abs=1e-4)
    # never drains more than the available surplus, even over a long window
    assert drained_over_window(5.0, 1.0, 100000.0, 10.0) < 5.0


def test_drained_over_window_constant_rate_without_max():
    # no maximum bucket -> constant rate, clamped at the surplus
    assert drained_over_window(5.0, 1.0, 3.0, None) == pytest.approx(3.0)
    assert drained_over_window(5.0, 1.0, 100.0, None) == pytest.approx(5.0)


def test_live_deficit_drains_surplus():
    # surplus 8 mm above field capacity drains over 24h (max 24)
    no_drain = live_deficit(5.0, 0.0, 3.0, maximum_bucket=24.0)
    drained = live_deficit(
        5.0, 0.0, 3.0, maximum_bucket=24.0, drainage_rate=1.0, elapsed_hours=24.0
    )
    assert 0.0 < drained < no_drain
    # a deficit (negative) is never touched by drainage
    assert live_deficit(-2.0, 1.0, 0.0, drainage_rate=5.0, elapsed_hours=24.0) == -3.0
