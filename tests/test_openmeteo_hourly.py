"""Tests for OpenMeteoClient.get_hourly_data (intra-day rows for the estimate)."""

import datetime
import math

from custom_components.smart_irrigation.weathermodules.OpenMeteoClient import (
    OpenMeteoClient,
)

_WIND_10M_TO_2M = 4.87 / math.log((67.8 * 10) - 5.42)


def _fake_doc():
    """Build a today doc (tz=UTC) with hours 00:00..current + one future hour."""
    now = datetime.datetime.utcnow()
    today = now.date()
    times, temp, rh, wind, rad, precip = [], [], [], [], [], []
    for hr in range(0, now.hour + 2):  # +2 => include one future hour
        dt = datetime.datetime(today.year, today.month, today.day, hr)
        times.append(dt.strftime("%Y-%m-%dT%H:%M"))
        temp.append(20.0)
        rh.append(50.0)
        wind.append(10.0)
        rad.append(500.0)
        precip.append(0.2)
    return {
        "utc_offset_seconds": 0,
        "hourly": {
            "time": times,
            "temperature_2m": temp,
            "relative_humidity_2m": rh,
            "wind_speed_10m": wind,
            "shortwave_radiation": rad,
            "precipitation": precip,
        },
    }


def test_get_hourly_data_parses_today_and_excludes_future(monkeypatch):
    client = OpenMeteoClient(latitude=48.39, longitude=16.23, elevation=180)
    monkeypatch.setattr(client, "_fetch", _fake_doc)

    rows, tz = client.get_hourly_data()
    now = datetime.datetime.utcnow()

    assert tz == 0.0
    # hours 00:00..current inclusive; the future hour is excluded
    assert len(rows) == now.hour + 1
    assert max(r["hour"] for r in rows) <= now.hour + 0.5

    r = rows[0]
    assert r["hour"] == 0.5
    assert r["temperature"] == 20.0
    assert r["humidity"] == 50.0
    assert abs(r["wind_2m"] - 10.0 * _WIND_10M_TO_2M) < 1e-9
    assert abs(r["solar_mj_h"] - 500.0 * 0.0036) < 1e-9  # 1.8 MJ/m2/h
    assert r["precipitation"] == 0.2
    assert r["doy"] == now.timetuple().tm_yday


def _fake_doc_with_past():
    """Doc (tz=UTC) spanning yesterday 00:00 .. today current hour + 1 future."""
    now = datetime.datetime.utcnow()
    today = now.date()
    yesterday = today - datetime.timedelta(days=1)
    times, temp, rh, wind, rad, precip = [], [], [], [], [], []

    def add(d, hr):
        dt = datetime.datetime(d.year, d.month, d.day, hr)
        times.append(dt.strftime("%Y-%m-%dT%H:%M"))
        temp.append(20.0)
        rh.append(50.0)
        wind.append(10.0)
        rad.append(500.0)
        precip.append(0.2)

    for hr in range(24):  # all of yesterday
        add(yesterday, hr)
    for hr in range(0, now.hour + 2):  # today + one future hour
        add(today, hr)
    return {
        "utc_offset_seconds": 0,
        "hourly": {
            "time": times,
            "temperature_2m": temp,
            "relative_humidity_2m": rh,
            "wind_speed_10m": wind,
            "shortwave_radiation": rad,
            "precipitation": precip,
        },
    }


def test_url_requests_one_past_day():
    client = OpenMeteoClient(latitude=48.39, longitude=16.23)
    assert "past_days=1" in client.url


def test_get_hourly_data_includes_past_day(monkeypatch):
    """Rows reach back into the previous day so the window can anchor to a calc
    that ran the evening before — not just since local midnight."""
    client = OpenMeteoClient(latitude=48.39, longitude=16.23, elevation=180)
    monkeypatch.setattr(client, "_fetch", _fake_doc_with_past)

    rows, tz = client.get_hourly_data()
    now = datetime.datetime.utcnow()
    yesterday = now.date() - datetime.timedelta(days=1)

    assert tz == 0.0
    # yesterday's 24 hours + today's 00:00..current inclusive; future excluded
    assert len(rows) == 24 + now.hour + 1
    assert rows[0]["time"].startswith(yesterday.isoformat())
    assert all(datetime.datetime.fromisoformat(r["time"]) <= now for r in rows)


def test_get_hourly_data_handles_empty(monkeypatch):
    client = OpenMeteoClient(latitude=48.39, longitude=16.23)
    monkeypatch.setattr(client, "_fetch", lambda: {"hourly": {"time": []}})
    rows, tz = client.get_hourly_data()
    assert rows is None and tz is None
