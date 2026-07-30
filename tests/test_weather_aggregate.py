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


class TestContinuousUpdateRows:
    """The shape event-driven ingestion appends: SPARSE single-key rows.

    ContinuousUpdateMixin appends one row per sensor state change, carrying only
    the key that changed plus RETRIEVED_AT — unlike the interval poll, which
    writes every mapped field in one row. These are the regression guard for
    that ingestion path: if _group_by_sensor ever stopped building per-key
    parallel lists (or last_entry stopped backfilling), a continuous-update
    sensor group would silently aggregate the wrong window and mis-water.
    """

    def test_sparse_single_key_rows_aggregate_per_key(self):
        readings = [
            _r(0, Temperature=10),
            _r(1, Humidity=50),
            _r(2, Temperature=20),
            _r(3, Humidity=70),
        ]
        out = aggregate_window(readings, None, {}, now=T0 + datetime.timedelta(hours=3))
        # Each key averages over only its OWN rows — a row missing a key must
        # not be read as a zero (that would halve the mean and under-water).
        assert out[const.MAPPING_TEMPERATURE] == 15.0
        assert out[const.MAPPING_HUMIDITY] == 60.0
        # Daily min/max span the temperature rows the event path actually saw.
        assert out[const.MAPPING_MAX_TEMP] == 20.0
        assert out[const.MAPPING_MIN_TEMP] == 10.0

    def test_last_entry_backfills_sensor_absent_from_window(self):
        # Slow-moving sensor (humidity) produced no event inside this window;
        # without the carry-forward the calc module would get no humidity at all.
        readings = [_r(0, Temperature=10), _r(1, Temperature=20)]
        out = aggregate_window(
            readings,
            None,
            {},
            now=T0 + datetime.timedelta(hours=1),
            last_entry={const.MAPPING_HUMIDITY: 42},
        )
        assert out[const.MAPPING_HUMIDITY] == 42
        assert out[const.MAPPING_TEMPERATURE] == 15.0

    def test_last_entry_does_not_override_sensor_present_in_window(self):
        # Fresh readings always win: the carry-forward is a fallback, never a
        # value that competes with (or dilutes) the real window.
        readings = [_r(0, Humidity=50), _r(1, Humidity=70)]
        out = aggregate_window(
            readings,
            None,
            {},
            now=T0 + datetime.timedelta(hours=1),
            last_entry={const.MAPPING_HUMIDITY: 42},
        )
        assert out[const.MAPPING_HUMIDITY] == 60.0

    def test_last_entry_none_values_are_ignored(self):
        # A None carry-forward means "never had a reading"; injecting it would
        # blow up float() in _aggregate.
        readings = [_r(0, Temperature=10)]
        out = aggregate_window(
            readings,
            None,
            {},
            now=T0,
            last_entry={const.MAPPING_HUMIDITY: None},
        )
        assert const.MAPPING_HUMIDITY not in out
        assert out[const.MAPPING_TEMPERATURE] == 10

    def test_last_entry_never_backfills_an_integrating_aggregate(self):
        """A carry-forward must not become fabricated accumulation.

        A sensor-sourced precipitation field overridden to riemannsum takes the
        single-value path, which returns the rate verbatim — as if it had rained
        at that rate for a full hour. Backfilling it would invent rain from a
        stale reading, and invented rain suppresses irrigation (under-watering).
        """
        config = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                const.MAPPING_CONF_AGGREGATE: (
                    const.MAPPING_CONF_AGGREGATE_RIEMANNSUM
                ),
            }
        }
        out = aggregate_window(
            [_r(0, Temperature=10)],
            None,
            config,
            now=T0 + datetime.timedelta(hours=1),
            last_entry={const.MAPPING_PRECIPITATION: 2.5},
        )
        assert const.MAPPING_PRECIPITATION not in out

    def test_last_entry_still_backfills_a_delta_rain_gauge(self):
        """DELTA is a counter difference, so a single value is a correct 0.

        No change in a cumulative rain gauge genuinely means no rain, and an
        explicit 0 is more useful to the calc module than a missing field — so
        this one must NOT be caught by the integral-aggregate guard above.
        """
        config = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
            }
        }
        out = aggregate_window(
            [_r(0, Temperature=10)],
            None,
            config,
            now=T0 + datetime.timedelta(hours=1),
            last_entry={const.MAPPING_PRECIPITATION: 2.5},
        )
        assert out[const.MAPPING_PRECIPITATION] == 0

    def test_weather_service_precip_is_unaffected_by_the_guard(self):
        # Weather-service precip defaults to RIEMANNSUM and its groups keep
        # polling, so it always has real rows — but assert the guard does not
        # disturb that path either.
        config = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: (
                    const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
                ),
            }
        }
        readings = [_r(0, Precipitation=1.0), _r(1, Precipitation=1.0)]
        out = aggregate_window(
            readings, None, config, now=T0 + datetime.timedelta(hours=1)
        )
        assert out[const.MAPPING_PRECIPITATION] == 1.0  # 1 mm/h over 1 h
