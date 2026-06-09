"""Unit tests for the pure per-zone weather-window aggregation."""

import datetime

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.weather_aggregate import (
    aggregate_window,
    select_window,
)

T0 = datetime.datetime(2026, 6, 8, 6, 0, 0)


def _r(offset_h, **vals):
    """Build a reading dict at T0 + offset hours."""
    return {const.RETRIEVED_AT: T0 + datetime.timedelta(hours=offset_h), **vals}


class TestSelectWindow:
    def test_none_watermark_returns_all_as_window(self):
        readings = [_r(0, Temperature=10), _r(1, Temperature=12)]
        boundary, window = select_window(readings, None)
        assert boundary is None
        assert len(window) == 2

    def test_boundary_is_last_reading_at_or_before_watermark(self):
        wm = T0 + datetime.timedelta(hours=2)
        readings = [_r(0, Temperature=10), _r(1, Temperature=11), _r(3, Temperature=20)]
        boundary, window = select_window(readings, wm)
        assert boundary[const.MAPPING_TEMPERATURE] == 11  # the t=1 reading
        assert len(window) == 1 and window[0][const.MAPPING_TEMPERATURE] == 20


class TestMultiplier:
    def test_multiplier_from_watermark(self):
        now = T0 + datetime.timedelta(hours=12)
        wm = T0
        out = aggregate_window([_r(6, Temperature=15)], wm, {}, now=now)
        assert out[const.MAPPING_DATA_MULTIPLIER] == 0.5  # 12h / 24

    def test_multiplier_from_span_when_no_watermark(self):
        now = T0 + datetime.timedelta(hours=99)
        readings = [_r(0, Temperature=10), _r(6, Temperature=12)]
        out = aggregate_window(readings, None, {}, now=now)
        assert out[const.MAPPING_DATA_MULTIPLIER] == 0.25  # 6h span / 24


class TestAggregates:
    def test_average_includes_boundary(self):
        wm = T0
        readings = [_r(0, Temperature=10), _r(1, Temperature=20)]
        out = aggregate_window(readings, wm, {}, now=T0 + datetime.timedelta(hours=1))
        # boundary (10) + window (20) -> mean 15, and temp min/max span both
        assert out[const.MAPPING_TEMPERATURE] == 15
        assert out[const.MAPPING_MAX_TEMP] == 20
        assert out[const.MAPPING_MIN_TEMP] == 10

    def test_delta_accumulates_increments_from_boundary(self):
        wm = T0
        readings = [
            _r(0, Precipitation=5),  # boundary baseline
            _r(1, Precipitation=8),
            _r(2, Precipitation=10),
        ]
        out = aggregate_window(readings, wm, {}, now=T0 + datetime.timedelta(hours=2))
        assert out[const.MAPPING_PRECIPITATION] == 5  # (8-5) + (10-8)

    def test_delta_handles_midnight_reset_to_zero(self):
        wm = T0
        readings = [
            _r(0, Precipitation=5),
            _r(1, Precipitation=7),
            _r(2, Precipitation=0),  # reset
            _r(3, Precipitation=2),
        ]
        out = aggregate_window(readings, wm, {}, now=T0 + datetime.timedelta(hours=3))
        assert out[const.MAPPING_PRECIPITATION] == 4  # 2 before + 2 after reset

    def test_weather_service_precip_uses_riemann_sum(self):
        wm = T0
        readings = [_r(0, Precipitation=2), _r(1, Precipitation=4)]
        cfg = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
            }
        }
        out = aggregate_window(readings, wm, cfg, now=T0 + datetime.timedelta(hours=1))
        # boundary@wm (2) -> t1 (4): trapezoid (2+4)/2 * 1h = 3
        assert out[const.MAPPING_PRECIPITATION] == 3.0

    def test_empty_returns_none(self):
        assert aggregate_window([], T0, {}, now=T0) is None
        # watermark in the future of all readings -> boundary only, no window
        future = T0 + datetime.timedelta(days=1)
        out = aggregate_window([_r(0, Temperature=10)], future, {}, now=future)
        # single boundary reading still aggregates (carried-forward anchor)
        assert out[const.MAPPING_TEMPERATURE] == 10
