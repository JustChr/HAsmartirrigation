"""Hourly rows of a pausing sensor group: each hour books only its measured time.

A blocked field is averaged over its own valid time in the hour, never held into a
span, and after one the value from before holds again. The hour is charged for the
time in which every field the hourly equation needs was measured at once
(``coverage_h``); an hour without such time stays a row with no ET, so neither the
hourly form nor the replayed balance falls over. Fields without spans go through
the tables they always did, so rows of a group that keeps are unchanged.
"""

import datetime
from datetime import timedelta

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.et_estimate import (
    SiteGeometry,
    eto_hourly_series,
    hourly_eto_priced,
)
from custom_components.irrigation_plus.weather_aggregate import (
    HOURLY_ROW_REQUIRED,
    aggregate_window,
    build_hourly_rows,
)

T0 = datetime.datetime(2026, 6, 21, 0, 0, 0)
H = timedelta(hours=1)
M = timedelta(minutes=1)
LAT, LON, ELEV = 50.0, 7.0, 300.0
T = const.MAPPING_TEMPERATURE
RH = const.MAPPING_HUMIDITY
WIND = const.MAPPING_WINDSPEED
SUN = const.MAPPING_SOLRAD
P = const.MAPPING_PRESSURE
RAIN = const.MAPPING_PRECIPITATION
W_TO_MJ_DAY = 0.0864


def _sun(stamp):
    """Daylight in W/m2 as MJ/day/m2, flat within each hour."""
    hour = stamp.hour
    return (600.0 if 6 <= hour < 20 else 0.0) * W_TO_MJ_DAY


def _dense(hours=24, *, temp=lambda s: 10.0 + s.hour, skip=()):
    """A poll buffer: every field on every row, every 10 minutes.

    ``skip`` lists ``(field, from, to)`` stretches in which that field writes no
    row, as a deadband does for a value that does not move.
    """
    readings = []
    stamp = T0
    while stamp < T0 + hours * H:
        row = {
            const.RETRIEVED_AT: stamp,
            T: temp(stamp),
            RH: 60.0,
            WIND: 2.0,
            SUN: _sun(stamp),
            P: 1000.0,
        }
        for field, lo, hi in skip:
            if lo <= stamp < hi:
                row.pop(field)
        readings.append(row)
        stamp += 10 * M
    return readings


def _rows(readings, *, hours=24, blocked=None, **kwargs):
    return build_hourly_rows(
        readings,
        T0,
        kwargs.pop("mappings_config", {}),
        now=T0 + hours * H,
        latitude=LAT,
        longitude=LON,
        elevation=ELEV,
        tz_offset_h=2.0,
        blocked=blocked,
        **kwargs,
    )


def _by_hour(rows):
    return {row["hour_start"]: row for row in rows}


class TestFieldsWithoutSpans:
    def test_no_spans_an_empty_dict_and_a_foreign_field_give_the_same_rows(self):
        readings = _dense()
        plain = _rows(readings)
        assert _rows(readings, blocked={}) == plain
        assert _rows(
            readings, blocked={const.MAPPING_DEWPOINT: ((T0, T0 + 5 * H),)}
        ) == (plain)

    def test_the_required_fields_are_public(self):
        assert HOURLY_ROW_REQUIRED == (T, RH, WIND, SUN)


class TestABlockedHourBooksNothing:
    def test_hours_inside_a_span_stay_as_rows_without_et(self):
        rows = _by_hour(_rows(_dense(), blocked={T: ((T0 + 10 * H, T0 + 12 * H),)}))
        assert len(rows) == 24
        for hour in (10, 11):
            row = rows[T0 + hour * H]
            assert row["coverage_h"] == 0.0
            assert "temperature" not in row
            assert "solar_mj_h" not in row
        assert rows[T0 + 9 * H]["coverage_h"] == 1.0
        assert rows[T0 + 12 * H]["coverage_h"] == 1.0

    def test_the_series_charges_such_a_row_nothing(self):
        rows = _rows(_dense(), blocked={T: ((T0 + 10 * H, T0 + 12 * H),)})
        series = eto_hourly_series(rows, LAT, LON, 2.0, ELEV)
        by_hour = dict(zip([r["hour_start"] for r in rows], series, strict=True))
        assert by_hour[T0 + 10 * H] == 0.0
        assert by_hour[T0 + 11 * H] == 0.0
        assert by_hour[T0 + 12 * H] > 0.0

    def test_a_partly_blocked_hour_is_charged_its_measured_part(self):
        rows = _by_hour(
            _rows(_dense(), blocked={T: ((T0 + 10 * H, T0 + 11 * H + 15 * M),)})
        )
        assert rows[T0 + 11 * H]["coverage_h"] == pytest.approx(0.75)

    def test_hours_outside_the_spans_match_the_unblocked_rows(self):
        readings = _dense()
        plain = _by_hour(_rows(readings))
        cut = _by_hour(_rows(readings, blocked={T: ((T0 + 10 * H, T0 + 12 * H),)}))
        for hour in (*range(10), *range(12, 24)):
            for key in ("temperature", "humidity", "wind_2m", "pressure_kpa"):
                assert cut[T0 + hour * H][key] == pytest.approx(
                    plain[T0 + hour * H][key]
                )


class TestEachFieldIsAveragedOverItsOwnValidTime:
    def test_two_fields_silent_in_different_parts_of_one_hour(self):
        """Temperature 20 + minute/10 every ten minutes in hour 10; it is blocked
        10:00-10:20 and humidity 10:40-11:00. The hour books 10:20-10:40, the
        intersection, but temperature averages its own 10:20-11:00:
        (22 + 23 + 24 + 25) / 4 = 23.5, not (22 + 23) / 2 over the intersection."""

        def temp(stamp):
            return 20.0 + stamp.minute / 10 if stamp.hour == 10 else 15.0

        blocked = {
            T: ((T0 + 10 * H, T0 + 10 * H + 20 * M),),
            RH: ((T0 + 10 * H + 40 * M, T0 + 11 * H),),
        }
        row = _by_hour(_rows(_dense(temp=temp), blocked=blocked))[T0 + 10 * H]
        assert row["coverage_h"] == pytest.approx(20 / 60)
        assert row["temperature"] == pytest.approx(23.5)

    def test_a_frozen_value_stamped_inside_a_span_is_not_used(self):
        """A poll keeps stamping the dead sensor's value fresh. Temperature is
        13 until 03:20, frozen at 99 through the span 03:30-05:00 and reports
        again (16) only from 05:20. Hour 5 holds the value from before the span,
        13, until 05:20: (13 * 20 + 16 * 40) / 60 = 15.0."""

        def temp(stamp):
            if T0 + 3 * H + 30 * M <= stamp < T0 + 5 * H:
                return 99.0
            return 13.0 if stamp < T0 + 5 * H else 16.0

        readings = _dense(temp=temp, skip=[(T, T0 + 5 * H, T0 + 5 * H + 20 * M)])
        rows = _by_hour(
            _rows(readings, blocked={T: ((T0 + 3 * H + 30 * M, T0 + 5 * H),)})
        )
        assert rows[T0 + 5 * H]["temperature"] == pytest.approx(15.0)
        assert rows[T0 + 3 * H]["temperature"] == pytest.approx(13.0)
        assert rows[T0 + 3 * H]["coverage_h"] == pytest.approx(0.5)


class TestAWindowThatStartsInsideASpan:
    def test_the_dead_sensors_boundary_value_is_never_priced(self):
        """Silent since before the window: the boundary row carries the frozen 99,
        and so does every poll row until the sensor is back at 03:00 with 20."""

        def temp(stamp):
            return 99.0 if stamp < T0 + 3 * H else 20.0

        rows = _by_hour(
            _rows(_dense(temp=temp), blocked={T: ((T0 - 2 * H, T0 + 3 * H),)})
        )
        for hour in (0, 1, 2):
            assert rows[T0 + hour * H]["coverage_h"] == 0.0
        assert rows[T0 + 3 * H]["coverage_h"] == 1.0
        assert rows[T0 + 3 * H]["temperature"] == pytest.approx(20.0)


class TestARequiredFieldBlockedThroughout:
    def test_the_rows_stay_and_book_nothing(self):
        rows = _rows(_dense(), blocked={SUN: ((T0, T0 + 24 * H),)})
        assert rows is not None
        assert len(rows) == 24
        assert all(row["coverage_h"] == 0.0 for row in rows)
        assert sum(eto_hourly_series(rows, LAT, LON, 2.0, ELEV)) == 0.0

    def test_a_field_whose_every_reading_is_inside_a_span_books_nothing(self):
        readings = _dense(hours=24)
        for row in readings:
            if row[const.RETRIEVED_AT] < T0 + 8 * H:
                row.pop(T)
        rows = _rows(readings, blocked={T: ((T0 + 8 * H, T0 + 24 * H),)})
        assert rows is not None
        assert all(row["coverage_h"] == 0.0 for row in rows)

    def test_a_field_never_read_still_falls_back(self):
        readings = _dense()
        for row in readings:
            row.pop(T)
        assert _rows(readings, blocked={SUN: ((T0, T0 + 2 * H),)}) is None


class TestSpansOfDifferentFieldsAreTakenInTimeOrder:
    def test_a_late_field_with_an_early_span_is_not_overlooked(self):
        """The sun comes after the temperature among the required fields, yet its
        span lies before the temperature's: 08:00-10:00 for the sun, 12:00-14:00
        for the temperature. Each holds back the hours it covers, and no others."""
        blocked = {
            SUN: ((T0 + 8 * H, T0 + 10 * H),),
            T: ((T0 + 12 * H, T0 + 14 * H),),
        }
        rows = _by_hour(_rows(_dense(), blocked=blocked))
        silent = {
            hour for hour in range(24) if rows[T0 + hour * H]["coverage_h"] == 0.0
        }
        assert silent == {8, 9, 12, 13}
        assert all(
            rows[T0 + hour * H]["coverage_h"] == 1.0
            for hour in range(24)
            if hour not in silent
        )


class TestPressureIsNotRequired:
    def test_an_hour_without_valid_pressure_takes_the_elevation(self):
        rows = _by_hour(_rows(_dense(), blocked={P: ((T0 + 10 * H, T0 + 12 * H),)}))
        assert "pressure_kpa" not in rows[T0 + 10 * H]
        assert rows[T0 + 10 * H]["coverage_h"] == 1.0
        assert "temperature" in rows[T0 + 10 * H]
        assert rows[T0 + 12 * H]["pressure_kpa"] == pytest.approx(100.0)


class TestTheClearnessRatio:
    """Solar readings inside a span are neither an hour's own reading nor the
    source of a ratio; after the span the ratio from before it holds."""

    @staticmethod
    def _frozen(readings, lo, hi, value):
        for row in readings:
            if lo <= row[const.RETRIEVED_AT] < hi:
                row[SUN] = value
        return readings

    def test_frozen_solar_inside_a_span_changes_no_row(self):
        """Silent from 11:30, the sun is frozen at 999 until 13:00 and writes
        nothing more until 15:00. Hour 11 has its own reading before the span;
        the frozen ones must not become its ratio, carried on to 13 and 14."""
        span = (T0 + 11 * H + 30 * M, T0 + 13 * H)
        quiet = (SUN, T0 + 13 * H, T0 + 15 * H)
        clean = _dense(skip=[(SUN, *span), quiet])
        frozen = self._frozen(_dense(skip=[quiet]), *span, 999.0)
        assert _rows(frozen, blocked={SUN: (span,)}) == _rows(
            clean, blocked={SUN: (span,)}
        )

    def test_after_the_span_the_ratio_from_before_holds(self):
        """No solar reading from 11:00 to 15:00, the sensor back without a row.
        Hours 13 and 14 take the ratio measured before the span -- what the
        unblocked rows give for a buffer without the silent readings."""
        silent = (T0 + 11 * H, T0 + 15 * H)
        span = (T0 + 11 * H, T0 + 13 * H)
        readings = _dense(skip=[(SUN, *silent)])
        cut = _by_hour(_rows(readings, blocked={SUN: (span,)}))
        plain = _by_hour(_rows(readings))
        for hour in (13, 14):
            assert cut[T0 + hour * H]["solar_mj_h"] == pytest.approx(
                plain[T0 + hour * H]["solar_mj_h"]
            )


class TestRain:
    def test_a_blocked_rain_rate_is_bucketed_over_its_valid_time_only(self):
        """The rows carry the same rain the aggregate books for the window."""
        readings = _dense()
        for row in readings:
            row[RAIN] = 2.0
        config = {
            RAIN: {
                const.MAPPING_CONF_AGGREGATE: const.MAPPING_CONF_AGGREGATE_RIEMANNSUM
            }
        }
        blocked = {RAIN: ((T0 + 10 * H, T0 + 12 * H),)}
        rows = _rows(readings, blocked=blocked, mappings_config=config)
        by_hour = _by_hour(rows)
        # Rain lands at the end of its interval: 09:50-10:00 is hour 10's, and
        # nothing after it until the span ends.
        assert by_hour[T0 + 10 * H]["precipitation"] == pytest.approx(2.0 / 6)
        assert by_hour[T0 + 11 * H]["precipitation"] == 0.0
        total = aggregate_window(
            readings, T0, config, now=T0 + 24 * H, blocked=blocked
        )[RAIN]
        assert sum(row["precipitation"] for row in rows) == pytest.approx(total)
        # The rate integrates up to the last reading (23:50), less the span.
        assert total == pytest.approx(2.0 * (21 + 50 / 60))


class TestPricing:
    def test_hourly_eto_priced_passes_the_spans_on(self):
        geometry = SiteGeometry(LAT, LON, ELEV, 2.0, None)
        args = (_dense(), T0, {})
        kwargs = {"now": T0 + 24 * H, "last_entry": None, "geometry": geometry}
        _rows_plain, plain = hourly_eto_priced(*args, **kwargs)
        rows, cut = hourly_eto_priced(
            *args, **kwargs, blocked={T: ((T0 + 10 * H, T0 + 12 * H),)}
        )
        assert sum(cut) < sum(plain)
        hours = [row["hour_start"] for row in rows]
        assert cut[hours.index(T0 + 10 * H)] == 0.0
