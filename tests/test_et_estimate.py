"""Tests for the intra-day ET accumulation / proxy (et_estimate)."""

from custom_components.smart_irrigation.et_estimate import (
    estimate_daily_et0_hargreaves,
    live_deficit,
    proxy_et_since,
    rigorous_et_since,
)
from custom_components.smart_irrigation.et_hourly import eto_hourly

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
