"""Unit tests for the pure per-zone weather-window aggregation."""

import datetime

import pytest

from custom_components.irrigation_plus import const, helpers
from custom_components.irrigation_plus.weather_aggregate import (
    aggregate_window,
    build_hourly_rows,
    build_substeps,
    select_window,
    weather_day,
)

T0 = datetime.datetime(2026, 6, 8, 6, 0, 0)
UTC = datetime.timezone.utc


def _r(offset_h, **vals):
    """Build a reading dict at T0 + offset hours."""
    return {const.RETRIEVED_AT: T0 + datetime.timedelta(hours=offset_h), **vals}


class TestSelectWindowAcceptsBothTimestampForms:
    """An AWARE stamp must not detonate here, and must land where its naive twin does.

    Every stamp in the buffer is naive today, so these tests add a case rather than
    change one. They exist because the write side is about to start producing aware
    stamps: without them, the first aware value reaching this function raises
    ``can't compare offset-naive and offset-aware datetimes`` inside a blanket
    ``except``, which does not crash anything -- it silently switches the live
    estimate off with a plausible "last calculated" still on display.

    A stored stamp's naive form is the PROCESS's zone, so an aware one is read there.
    The process zone is substituted rather than set, because ``time.tzset()`` does not
    exist on Windows.
    """

    @staticmethod
    def _aware(offset_h, tz, **vals):
        naive = T0 + datetime.timedelta(hours=offset_h)
        return {const.RETRIEVED_AT: naive.replace(tzinfo=tz), **vals}

    def test_an_aware_retrieved_at_splits_where_its_naive_twin_does(self, monkeypatch):
        monkeypatch.setattr(helpers, "_process_timezone", lambda: UTC)
        wm = T0 + datetime.timedelta(hours=2)
        naive_rows = [_r(h, Temperature=10 + h) for h in (0, 1, 2, 3, 4)]
        aware_rows = [self._aware(h, UTC, Temperature=10 + h) for h in (0, 1, 2, 3, 4)]

        n_boundary, n_window = select_window(naive_rows, wm)
        a_boundary, a_window = select_window(aware_rows, wm)

        assert len(a_window) == len(n_window)
        assert [r["Temperature"] for r in a_window] == [
            r["Temperature"] for r in n_window
        ]
        assert (a_boundary is None) == (n_boundary is None)
        assert a_boundary["Temperature"] == n_boundary["Temperature"]

    def test_an_aware_watermark_splits_where_its_naive_twin_does(self, monkeypatch):
        monkeypatch.setattr(helpers, "_process_timezone", lambda: UTC)
        rows = [_r(h, Temperature=10 + h) for h in (0, 1, 2, 3, 4)]
        naive_wm = T0 + datetime.timedelta(hours=2)

        _, n_window = select_window(rows, naive_wm)
        _, a_window = select_window(rows, naive_wm.replace(tzinfo=UTC))

        assert [r["Temperature"] for r in a_window] == [
            r["Temperature"] for r in n_window
        ]

    def test_an_aware_stamp_is_read_in_the_process_zone_not_has(self, monkeypatch):
        """The provenance is what decides, and it is the store's here.

        With the container at UTC+2, an 06:00 UTC stamp is 08:00 on the process clock,
        so it falls AFTER an 07:00 watermark rather than before it. Reading it as
        HA-local would put it on the other side of the split.
        """
        plus_two = datetime.timezone(datetime.timedelta(hours=2))
        monkeypatch.setattr(helpers, "_process_timezone", lambda: plus_two)
        rows = [self._aware(0, UTC, Temperature=10)]  # 06:00 UTC == 08:00 process
        wm = T0 + datetime.timedelta(hours=1)  # 07:00 naive process time

        boundary, window = select_window(rows, wm)

        assert boundary is None, "08:00 is not at or before 07:00"
        assert len(window) == 1


class TestTheEntryPointsSurviveAnAwareNow:
    """An aware ``now`` must not detonate either, and must land in the rows' frame.

    ``now`` is the one input on these three functions whose provenance depends on the
    CALLER: the daily calculation passes its own process clock, the live estimate
    passes HA-local, and one live-estimate call site passes nothing at all and takes
    the default. Nothing in the signature says which, and that is what makes this
    input the fragile one.

    The entry point cannot know, so it reads an unnamed aware ``now`` in the frame of
    the rows it is about to be compared against -- the only frame in which that
    comparison means anything. Naive values, which is all of them today, are untouched.
    """

    def test_aggregate_window_accepts_an_aware_now(self, monkeypatch):
        monkeypatch.setattr(helpers, "_process_timezone", lambda: UTC)
        rows = [_r(0, Temperature=10), _r(1, Temperature=12)]
        cfg = {}
        naive_now = T0 + datetime.timedelta(hours=2)

        plain = aggregate_window(rows, None, cfg, now=naive_now)
        aware = aggregate_window(rows, None, cfg, now=naive_now.replace(tzinfo=UTC))

        assert aware == plain

    def test_build_substeps_accepts_an_aware_now(self, monkeypatch):
        monkeypatch.setattr(helpers, "_process_timezone", lambda: UTC)
        rows = [_r(0, Precipitation=0.0), _r(1, Precipitation=1.0)]
        cfg = {}
        naive_now = T0 + datetime.timedelta(hours=2)

        plain = build_substeps(rows, None, cfg, now=naive_now)
        aware = build_substeps(rows, None, cfg, now=naive_now.replace(tzinfo=UTC))

        assert aware == plain

    def test_build_hourly_rows_accepts_an_aware_now(self, monkeypatch):
        monkeypatch.setattr(helpers, "_process_timezone", lambda: UTC)
        rows = [_r(0, Temperature=10), _r(1, Temperature=12)]
        cfg = {}
        naive_now = T0 + datetime.timedelta(hours=2)

        plain = build_hourly_rows(rows, None, cfg, now=naive_now)
        aware = build_hourly_rows(rows, None, cfg, now=naive_now.replace(tzinfo=UTC))

        assert aware == plain


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
        out = aggregate_window(readings, wm, {}, now=T0 + datetime.timedelta(hours=2))
        # Boundary (10) holds from the watermark to t=1h, then 20 holds to now
        # at t=2h: one hour each, so the time-weighted mean is 15. Min/max still
        # span every sample regardless of how long each one stood.
        assert out[const.MAPPING_TEMPERATURE] == 15
        assert out[const.MAPPING_MAX_TEMP] == 20
        assert out[const.MAPPING_MIN_TEMP] == 10

    def test_average_weights_by_dwell_time_not_sample_count(self):
        """The bug this aggregate exists to prevent, in miniature.

        Three readings, but the first value stood for three quarters of the
        window. A plain mean returns 30; the window really averaged 17.5.
        """
        wm = T0
        readings = [
            _r(0, Temperature=10),  # boundary, holds 0h -> 3h
            _r(3, Temperature=30),  # holds 3h -> 3.5h
            _r(3.5, Temperature=50),  # holds 3.5h -> now (4h)
        ]
        out = aggregate_window(
            readings, wm, {}, now=T0 + datetime.timedelta(hours=4), time_weighted=True
        )
        # (10*3 + 30*0.5 + 50*0.5) / 4
        assert out[const.MAPPING_TEMPERATURE] == 17.5

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
        out = aggregate_window(
            readings, None, {}, now=T0 + datetime.timedelta(hours=4), time_weighted=True
        )
        # Each key averages over only its OWN rows — a row missing a key must
        # not be read as a zero (that would halve the mean and under-water) —
        # and each value is weighted by how long it stood, not by how many rows
        # its field happened to produce.
        # Temperature: 10 for 0h->2h, 20 for 2h->4h.
        assert out[const.MAPPING_TEMPERATURE] == 15.0
        # Humidity: first sample held back to the window start, so 50 for
        # 0h->3h and 70 for 3h->4h.
        assert out[const.MAPPING_HUMIDITY] == 55.0
        # Daily min/max span the temperature rows the event path actually saw.
        assert out[const.MAPPING_MAX_TEMP] == 20.0
        assert out[const.MAPPING_MIN_TEMP] == 10.0

    def test_average_of_a_field_constant_for_part_of_the_window(self):
        """Solar radiation over a day, in miniature — the shipped-bug shape.

        Solar only produces rows while it is changing, and it is pinned at 0 all
        night, so a day's buffer holds a dense daylight cluster and nothing else.
        A plain mean of the stored rows is then a mean over daylight only. On
        nine days of production data that read 2.02-2.78x the true 24 h mean, and
        PyETO's clear-sky clamp masked it by pinning Rs at Rso.

        Here: 12 h of night at 0, then six hourly daylight rows, then night
        again. The true 24 h mean is 15; the plain mean of the stored rows is
        45 — 3x over, the same shape and direction as the production numbers.
        """
        sun = const.MAPPING_SOLRAD
        readings = [
            _r(0, **{sun: 0}),  # dusk the evening before
            _r(12, **{sun: 20}),
            _r(13, **{sun: 40}),
            _r(14, **{sun: 60}),
            _r(15, **{sun: 80}),
            _r(16, **{sun: 100}),
            _r(17, **{sun: 60}),
            _r(18, **{sun: 0}),  # dusk: back to 0 for the rest of the day
        ]
        out = aggregate_window(
            readings, T0, {}, now=T0 + datetime.timedelta(hours=24), time_weighted=True
        )
        # (20+40+60+80+100+60) MJ/day/m2 x 1 h each = 360, over a 24 h window.
        assert out[const.MAPPING_SOLRAD] == 15.0

    def test_riemannsum_uses_per_key_stamps_on_a_sparse_buffer(self):
        """RETRIEVED_AT is on every row; a sparse field is on only a few.

        Reading one parallel stamp list meant the lengths never matched on a
        continuous-update buffer, and the integral silently fell back to a flat
        1 h per interval. Latent rather than shipped — weather-service groups do
        not use the event path — but the same root cause as the mean above.
        """
        config = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
            }
        }
        readings = [
            _r(0, Precipitation=2.0),
            _r(1, Temperature=10),  # interleaved sparse row for another field
            _r(2, Precipitation=2.0),
            _r(3, Temperature=12),
        ]
        out = aggregate_window(
            readings, T0, config, now=T0 + datetime.timedelta(hours=3)
        )
        # 2 mm/h held across the 2 h between its own two rows. Falling back to
        # dt = 1 h would have returned 2.0.
        assert out[const.MAPPING_PRECIPITATION] == 4.0

    def test_last_entry_backfills_sensor_absent_from_window(self):
        # Slow-moving sensor (humidity) produced no event inside this window;
        # without the carry-forward the calc module would get no humidity at all.
        readings = [_r(0, Temperature=10), _r(1, Temperature=20)]
        out = aggregate_window(
            readings,
            None,
            {},
            now=T0 + datetime.timedelta(hours=2),
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
            now=T0 + datetime.timedelta(hours=2),
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
                const.MAPPING_CONF_AGGREGATE: (const.MAPPING_CONF_AGGREGATE_RIEMANNSUM),
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
                const.MAPPING_CONF_SOURCE: (const.MAPPING_CONF_SOURCE_WEATHER_SERVICE),
            }
        }
        readings = [_r(0, Precipitation=1.0), _r(1, Precipitation=1.0)]
        out = aggregate_window(
            readings, None, config, now=T0 + datetime.timedelta(hours=1)
        )
        assert out[const.MAPPING_PRECIPITATION] == 1.0  # 1 mm/h over 1 h


class TestWeatherDay:
    """The calendar day a window's readings are priced as."""

    @pytest.mark.parametrize(
        ("start", "end", "expected"),
        [
            pytest.param(
                datetime.datetime(2026, 5, 21, 23, 0),
                datetime.datetime(2026, 5, 22, 23, 0),
                datetime.date(2026, 5, 22),
                id="starts-at-23-lands-on-the-next-day",
            ),
            pytest.param(
                datetime.datetime(2026, 5, 21, 23, 0),
                datetime.datetime(2026, 5, 21, 23, 30),
                datetime.date(2026, 5, 22),
                id="still-open-half-an-hour-after-a-late-start",
            ),
            pytest.param(
                datetime.datetime(2026, 5, 22, 6, 0),
                datetime.datetime(2026, 5, 23, 6, 0),
                datetime.date(2026, 5, 22),
                id="starts-at-06-keeps-its-day",
            ),
            pytest.param(
                datetime.datetime(2026, 5, 22, 2, 0),
                datetime.datetime(2026, 5, 23, 2, 0),
                datetime.date(2026, 5, 22),
                id="starts-at-02-keeps-its-day",
            ),
            pytest.param(
                datetime.datetime(2026, 5, 22, 11, 59),
                datetime.datetime(2026, 5, 23, 11, 59),
                datetime.date(2026, 5, 22),
                id="starts-just-before-noon-keeps-its-day",
            ),
            pytest.param(
                datetime.datetime(2026, 5, 22, 12, 0),
                datetime.datetime(2026, 5, 23, 12, 0),
                datetime.date(2026, 5, 23),
                id="starts-at-noon-goes-to-the-next-day",
            ),
        ],
    )
    def test_a_window_belongs_to_the_day_twelve_hours_after_its_start(
        self, start, end, expected
    ):
        assert weather_day(start, end) == expected

    def test_a_window_without_a_start_belongs_to_the_day_it_ends(self):
        end = datetime.datetime(2026, 5, 23, 2, 0)
        assert weather_day(None, end) == datetime.date(2026, 5, 23)
