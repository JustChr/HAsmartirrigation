"""Replayed water balance of a pausing sensor group: ET lands only in measured time.

The sub-steps place the window's ET by measured sun. Where a field the calculation
needs was silent nothing is booked, so nothing is placed there either; a blocked
rain rate adds only its measured rain, so the steps still reconcile with the
aggregate. Only the placement moves -- the weights still sum to one.
"""

import datetime
from datetime import timedelta

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.weather_aggregate import (
    HOURLY_ROW_REQUIRED,
    aggregate_window,
    build_substeps,
)

T0 = datetime.datetime(2026, 6, 21, 0, 0, 0)
NOW = T0 + timedelta(hours=24)
H = timedelta(hours=1)
M = timedelta(minutes=1)
T = const.MAPPING_TEMPERATURE
SUN = const.MAPPING_SOLRAD
RAIN = const.MAPPING_PRECIPITATION
RATE = {RAIN: {const.MAPPING_CONF_AGGREGATE: const.MAPPING_CONF_AGGREGATE_RIEMANNSUM}}
DAILY = (const.MAPPING_DEWPOINT, T, const.MAPPING_WINDSPEED, const.MAPPING_PRESSURE)


def _sun(stamp):
    hour = stamp.hour + stamp.minute / 60
    return max(0.0, 700.0 * (1 - abs(hour - 13) / 7)) * 0.0864


def _readings(*, rain=None):
    """Every 10 minutes: temperature and sun; ``rain`` maps a stamp to a rate."""
    out = []
    stamp = T0
    while stamp < NOW:
        row = {const.RETRIEVED_AT: stamp, T: 18.0, SUN: _sun(stamp)}
        if rain is not None:
            row[RAIN] = rain(stamp)
        out.append(row)
        stamp += 10 * M
    return out


def _steps(readings, **kwargs):
    config = kwargs.pop("mappings_config", {})
    return build_substeps(readings, T0, config, now=NOW, **kwargs)


def _span_of(steps, lo, hi):
    """Indices of the steps lying inside ``[lo, hi)``."""
    out, t = [], T0
    for i, step in enumerate(steps):
        end = t + timedelta(hours=step.dt_hours)
        if lo <= t and end <= hi:
            out.append(i)
        t = end
    return out


class TestWithoutSpans:
    def test_no_spans_an_empty_dict_and_a_foreign_field_give_the_same_steps(self):
        readings = _readings()
        plain = _steps(readings)
        assert _steps(readings, blocked={}, required=DAILY) == plain
        assert (
            _steps(
                readings,
                blocked={const.MAPPING_HUMIDITY: ((T0 + 10 * H, T0 + 12 * H),)},
                required=DAILY,
            )
            == plain
        )


class TestTheEtLandsInMeasuredTime:
    def test_a_required_field_silent_places_no_et_there(self):
        readings = _readings()
        span = (T0 + 10 * H, T0 + 12 * H)
        plain = _steps(readings)
        cut = _steps(readings, blocked={T: (span,)}, required=DAILY)
        inside = _span_of(cut, *span)
        assert inside
        assert all(cut[i].et_weight == 0.0 for i in inside)
        assert sum(s.et_weight for s in cut) == pytest.approx(1.0)
        # Outside the span the sun shapes it as before, renormalised.
        lost = sum(plain[i].et_weight for i in inside)
        for i, step in enumerate(cut):
            if i not in inside:
                assert step.et_weight == pytest.approx(plain[i].et_weight / (1 - lost))

    def test_a_field_the_form_does_without_moves_nothing(self):
        readings = _readings()
        span = (T0 + 10 * H, T0 + 12 * H)
        assert _steps(
            readings, blocked={const.MAPPING_HUMIDITY: (span,)}, required=DAILY
        ) == _steps(readings)

    def test_the_spans_of_several_fields_are_taken_in_time_order(self):
        """Five fields, each silent for an hour of its own. The fields are
        gathered from a set, so the order they come in is not the order of time.
        No sun sensor, so the measured time alone places the ET."""
        readings = [{k: v for k, v in row.items() if k != SUN} for row in _readings()]
        spans = {
            SUN: (T0 + 2 * H, T0 + 3 * H),
            const.MAPPING_DEWPOINT: (T0 + 4 * H, T0 + 5 * H),
            T: (T0 + 6 * H, T0 + 7 * H),
            const.MAPPING_WINDSPEED: (T0 + 8 * H, T0 + 9 * H),
            const.MAPPING_PRESSURE: (T0 + 10 * H, T0 + 11 * H),
        }
        cut = _steps(
            readings,
            blocked={field: (span,) for field, span in spans.items()},
            required=DAILY,
        )
        for span in spans.values():
            inside = _span_of(cut, *span)
            assert inside
            assert all(cut[i].et_weight == 0.0 for i in inside)
        assert sum(s.et_weight for s in cut) == pytest.approx(1.0)

    def test_silent_sun_places_no_et_in_its_span_either(self):
        """The sun's own frozen value must not weight its silent time."""
        readings = _readings()
        span = (T0 + 10 * H, T0 + 12 * H)
        cut = _steps(readings, blocked={SUN: (span,)}, required=DAILY)
        assert all(cut[i].et_weight == 0.0 for i in _span_of(cut, *span))

    def test_inside_an_hour_the_quantum_goes_to_its_measured_part(self):
        """Hour 11 is cut by a rain event at 11:10; temperature is silent until
        11:15. The step 11:00-11:10 gets nothing of the hour's quantum."""

        def rain(stamp):
            return 3.0 if T0 + 11 * H <= stamp <= T0 + 11 * H + 10 * M else 0.0

        readings = _readings(rain=rain)
        hourly_et = {T0 + h * H: (0.2 if 6 <= h < 20 else 0.01) for h in range(24)}
        cut = _steps(
            readings,
            mappings_config=RATE,
            hourly_et=hourly_et,
            blocked={T: ((T0 + 9 * H, T0 + 11 * H + 15 * M),)},
            required=HOURLY_ROW_REQUIRED,
        )
        first = _span_of(cut, T0 + 11 * H, T0 + 11 * H + 10 * M)
        assert len(first) == 1
        assert cut[first[0]].et_weight == 0.0

    def test_a_dark_hour_spreads_its_quantum_over_its_measured_time(self):
        """Hour 2 is dark and cut by rain at 02:10, 02:20 and 02:30; temperature
        is silent until 02:30. The steps before 02:30 get none of the hour's ET,
        02:30-03:00 all of it -- what the whole hour gets without the span."""

        def rain(stamp):
            return 3.0 if T0 + 2 * H + 10 * M <= stamp <= T0 + 2 * H + 20 * M else 0.0

        readings = _readings(rain=rain)
        hourly_et = {T0 + h * H: 0.01 for h in range(24)}
        args = {"mappings_config": RATE, "hourly_et": hourly_et}
        plain = _steps(readings, **args)
        cut = _steps(
            readings,
            **args,
            blocked={T: ((T0 + 2 * H, T0 + 2 * H + 30 * M),)},
            required=HOURLY_ROW_REQUIRED,
        )
        silent = _span_of(cut, T0 + 2 * H, T0 + 2 * H + 30 * M)
        measured = _span_of(cut, T0 + 2 * H + 30 * M, T0 + 3 * H)
        hour = _span_of(plain, T0 + 2 * H, T0 + 3 * H)
        assert len(silent) == 3
        assert all(cut[i].et_weight == 0.0 for i in silent)
        assert len(measured) == 1
        assert cut[measured[0]].et_weight == pytest.approx(
            sum(plain[i].et_weight for i in hour)
        )

    def test_a_window_with_no_measured_time_still_steps(self):
        """Nothing is booked, so the ET to place is 0 -- the rain still replays."""
        readings = _readings(rain=lambda stamp: 1.0)
        steps = _steps(
            readings,
            mappings_config=RATE,
            blocked={T: ((T0, NOW),)},
            required=DAILY,
        )
        assert steps is not None
        assert sum(s.et_weight for s in steps) == pytest.approx(1.0)


class TestTheRainStillReconciles:
    def test_a_blocked_rain_rate_adds_only_its_measured_rain(self):
        readings = _readings(rain=lambda stamp: 2.0)
        blocked = {RAIN: ((T0 + 10 * H, T0 + 12 * H),)}
        steps = _steps(readings, mappings_config=RATE, blocked=blocked, required=DAILY)
        total = aggregate_window(readings, T0, RATE, now=NOW, blocked=blocked)[RAIN]
        assert sum(s.precip_mm for s in steps) == pytest.approx(total, rel=1e-9)
        assert sum(s.precip_mm for s in _steps(readings, mappings_config=RATE)) > total

    def test_rain_just_before_a_span_lands_before_it(self):
        """The reading of 10:00 lies on the span's start and is dropped; the rain
        of 09:50-10:00 still lands at 10:00, not at the next reading."""
        readings = _readings(rain=lambda stamp: 2.0)
        blocked = {RAIN: ((T0 + 10 * H, T0 + 12 * H),)}
        steps = _steps(readings, mappings_config=RATE, blocked=blocked, required=DAILY)
        before = _span_of(steps, T0 + 9 * H, T0 + 10 * H)
        assert sum(steps[i].precip_mm for i in before) == pytest.approx(2.0)
