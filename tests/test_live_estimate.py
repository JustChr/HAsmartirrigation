"""Tests for the intra-day live-estimate orchestration (live_estimate).

Focus on the parts that can't be validated against live weather data: the
since-last-calc window (the double-count fix) and the imperial unit conversion.
"""

import datetime
from types import SimpleNamespace

from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.et_estimate import (
    estimate_daily_et0_hargreaves,
    proxy_et_since,
    rigorous_et_since,
)
from custom_components.smart_irrigation.live_estimate import (
    LiveEstimateMixin,
    _parse_local_naive,
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


def test_parse_local_naive():
    import homeassistant.util.dt as dt_util

    # naive (the store's convention) is returned unchanged — interpreted local
    assert _parse_local_naive("2026-06-07T12:00:00") == datetime.datetime(
        2026, 6, 7, 12
    )
    # an aware value (shouldn't occur for these fields) is converted to local
    aware = datetime.datetime(2026, 6, 7, 12, tzinfo=datetime.timezone.utc)
    assert _parse_local_naive(aware) == dt_util.as_local(aware).replace(tzinfo=None)
    assert _parse_local_naive(None) is None
    assert _parse_local_naive("not-a-date") is None


def test_rows_since_filters_to_after_last_calc():
    rows = _rows()  # hours 10..13 local
    # last calc today 11:00 LOCAL — compared directly to the (local) rows
    last_calc_local = datetime.datetime.combine(
        datetime.date.today(), datetime.time(11, 0)
    )
    window = LiveEstimateMixin._rows_since(rows, last_calc_local)
    hours = [r["hour"] for r in window]
    # hours whose end (>hour+1) is after 11:00 local -> 11,12,13 (the 11:00 row
    # ends at 12:00 > 11:00). The 10:00 row (ends 11:00) is excluded.
    assert hours == [11.5, 12.5, 13.5]


def test_rows_since_none_returns_all():
    rows = _rows()
    assert LiveEstimateMixin._rows_since(rows, None) == rows


# A last-calc early enough today that the whole _rows() window is "since calc"
# (00:00 local, before the 10:00 first row).
_EARLY_TODAY = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))


def test_intraday_metric_hourly_balance():
    coord = _Coord(METRIC_SYSTEM)
    inputs = {"client": _client(), "rows": _rows(), "tz": 2.0, "forecast": None}
    zone = {"bucket": -2.0, "maximum_bucket": 24, "last_calculated": _EARLY_TODAY}
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
    zone = {"bucket": -0.1, "maximum_bucket": 1.0, "last_calculated": _EARLY_TODAY}
    est = coord._intraday_for_zone(zone, inputs)

    et_mm = rigorous_et_since(_rows(), 48.39, 16.23, 2.0, 180)
    bucket_mm = -0.1 * 25.4
    expected_live_in = (bucket_mm - et_mm) / 25.4
    assert est["available"] is True
    # result is reported in inches; ET is positive, so deficit grows (more negative)
    assert est["live_deficit"] < -0.1
    assert abs(est["live_deficit"] - round(expected_live_in, 3)) < 1e-3


def test_intraday_proxy_no_spurious_et_right_after_calc(monkeypatch):
    """Regression: last_calculated is naive LOCAL. Reading it as UTC used to
    shove the proxy anchor onto the next calendar day (a +tz day-boundary jump),
    so a whole day's ET got subtracted the instant the daily calc ran — the
    yellow "live" line dropping ~a day's ET below the bucket. Immediately after a
    calc the window is ~0, so live_deficit must ~= bucket regardless of offset.
    """
    import custom_components.smart_irrigation.live_estimate as le

    # "now" == the calc instant; local tz +2 (the offset that exposed the bug).
    tz = datetime.timezone(datetime.timedelta(hours=2))
    now_local = datetime.datetime(2026, 6, 11, 23, 31, tzinfo=tz)
    monkeypatch.setattr(le.dt_util, "now", lambda: now_local)

    coord = _Coord(METRIC_SYSTEM)
    coord.store = SimpleNamespace(get_mapping=lambda _mid: None)  # no precip
    forecast = [{const.MAPPING_MIN_TEMP: 14.0, const.MAPPING_MAX_TEMP: 28.0}]
    inputs = {"client": _client(), "rows": None, "tz": None, "forecast": forecast}
    zone = {
        "bucket": -2.0,
        "maximum_bucket": 24,
        # stored as the store does: naive LOCAL, the same instant as "now"
        "last_calculated": now_local.replace(tzinfo=None),
    }
    est = coord._intraday_for_zone(zone, inputs)

    assert est["available"] is True
    assert est["method"] == "proxy"
    # essentially no time elapsed -> ET ~ 0 -> live ~ bucket (not bucket - a day)
    assert abs(est["et_since"]) < 1e-6
    assert abs(est["live_deficit"] - (-2.0)) < 1e-6


def test_intraday_proxy_window_spans_midnight(monkeypatch):
    """The proxy window must follow last_calc across midnight, not reset at 00:00.

    Calc ran yesterday 18:00 local; "now" is today 06:30. The window is the
    remaining hours of the calc day (18..23) plus today's elapsed (00..06), not
    just today since midnight.
    """
    import custom_components.smart_irrigation.live_estimate as le

    tz = datetime.timezone(datetime.timedelta(hours=2))
    now_local = datetime.datetime(2026, 6, 12, 6, 30, tzinfo=tz)
    monkeypatch.setattr(le.dt_util, "now", lambda: now_local)

    coord = _Coord(METRIC_SYSTEM)
    coord.store = SimpleNamespace(get_mapping=lambda _mid: None)
    tmin, tmax = 14.0, 30.0
    forecast = [{const.MAPPING_MIN_TEMP: tmin, const.MAPPING_MAX_TEMP: tmax}]
    inputs = {"client": _client(), "rows": None, "tz": None, "forecast": forecast}
    zone = {
        "bucket": 5.0,
        "maximum_bucket": 24,
        "last_calculated": datetime.datetime(2026, 6, 11, 18, 0),  # naive local
    }
    est = coord._intraday_for_zone(zone, inputs)

    lat, lon = 48.39, 16.23
    doy = now_local.timetuple().tm_yday
    elapsed = [h + 0.5 for h in range(18, 24)] + [h + 0.5 for h in range(0, 7)]
    expected = proxy_et_since(
        estimate_daily_et0_hargreaves(tmin, tmax, lat, doy), lat, lon, doy, 2.0, elapsed
    )
    assert est["method"] == "proxy"
    assert abs(est["et_since"] - round(expected, 2)) < 1e-9
    assert est["et_since"] > 0  # daytime hours of both sides contribute


def test_observed_precip_is_time_weighted_not_plain_sum():
    """Weather-service precip is a rate (mm/h), so it must be integrated by time
    (Riemann), not plain-summed. The helper delegates to the same
    aggregate_window the daily calc uses.
    """
    from custom_components.smart_irrigation.weather_aggregate import (
        _parse,
        aggregate_window,
    )

    coord = _Coord(METRIC_SYSTEM)
    readings = [
        {
            const.RETRIEVED_AT: "2026-06-07T10:00:00.000000",
            const.MAPPING_PRECIPITATION: 4.0,
        },
        {
            const.RETRIEVED_AT: "2026-06-07T10:30:00.000000",
            const.MAPPING_PRECIPITATION: 4.0,
        },
    ]
    mappings_config = {
        const.MAPPING_PRECIPITATION: {
            const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
        }
    }
    mapping = {const.MAPPING_DATA: readings, const.MAPPING_MAPPINGS: mappings_config}
    coord.store = SimpleNamespace(get_mapping=lambda _mid: mapping)
    watermark = "2026-06-07T09:00:00.000000"
    zone = {const.ZONE_MAPPING: 0, const.ZONE_LAST_CONSUMED: watermark}

    result = coord._observed_precip_since_mm(zone)
    expected = aggregate_window(readings, _parse(watermark), mappings_config).get(
        const.MAPPING_PRECIPITATION
    )
    assert result == expected
    # Two 4 mm/h rates 30 min apart integrate to far less than their plain sum (8).
    assert 0 < result < 8.0


def test_observed_precip_handles_no_mapping():
    coord = _Coord(METRIC_SYSTEM)
    coord.store = SimpleNamespace(get_mapping=lambda _mid: None)
    assert coord._observed_precip_since_mm({}) == 0.0
    assert coord._observed_precip_since_mm({const.ZONE_MAPPING: 7}) == 0.0


def test_intraday_unavailable_until_first_calc():
    """A never-calculated zone (last_calculated None) gets no estimate."""
    coord = _Coord(METRIC_SYSTEM)
    inputs = {"client": _client(), "rows": _rows(), "tz": 2.0, "forecast": None}
    zone = {"bucket": -2.0, "maximum_bucket": 24, "last_calculated": None}
    assert coord._intraday_for_zone(zone, inputs)["available"] is False


async def test_estimate_cache_lazy_compute_and_refresh(monkeypatch):
    """The cached getter computes once on demand; refresh recomputes + notifies."""
    coord = _Coord(METRIC_SYSTEM)
    dispatched = []
    monkeypatch.setattr(
        "custom_components.smart_irrigation.live_estimate.async_dispatcher_send",
        lambda *args: dispatched.append(args),
    )
    computed = {"count": 0}

    async def fake_get():
        computed["count"] += 1
        return {"1": {"available": True, "live_deficit": -1.0}}

    coord.async_get_zone_estimates = fake_get

    # no cache yet -> first cached request computes (and notifies)
    out = await coord.async_get_cached_zone_estimates()
    assert out == {"1": {"available": True, "live_deficit": -1.0}}
    assert computed["count"] == 1
    assert dispatched and dispatched[0][1] == const.DOMAIN + "_estimates_updated"

    # second request is served from the cache (no recompute)
    assert await coord.async_get_cached_zone_estimates() is out
    assert computed["count"] == 1

    # explicit refresh (update/calc cycle) recomputes and re-notifies
    await coord.async_refresh_zone_estimates()
    assert computed["count"] == 2
    assert len(dispatched) == 2


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
