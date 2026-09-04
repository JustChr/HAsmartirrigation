"""Time-weighted AVERAGE must stay behind the continuous-updates flag.

Event-driven ingestion writes a SPARSE buffer, where a plain mean over stored
rows is wrong: a row exists because a value moved, so row density is a property
of the field. Time-weighting fixes that — but it is not free to apply
everywhere. A poll-only install's rows are evenly spaced by the update timer,
and switching it on there would silently move the ET of every existing user who
never opted into the feature.

These tests pin the default (flag off) to the plain mean that shipped before
continuous updates existed.
"""

import datetime
import statistics

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.weather_aggregate import aggregate_window

T0 = datetime.datetime(2026, 6, 8, 6, 0, 0)


def _r(offset_h, **vals):
    return {const.RETRIEVED_AT: T0 + datetime.timedelta(hours=offset_h), **vals}


# An UNEVEN series, so the plain mean and the time-weighted mean genuinely
# disagree: 10 stands for one hour, 20 stands for five.
_UNEVEN = [_r(0, Temperature=10), _r(1, Temperature=20)]
_NOW = T0 + datetime.timedelta(hours=6)


def test_default_is_the_plain_mean_over_stored_rows():
    """The pre-#66 behaviour, which every poll-only install must keep."""
    out = aggregate_window(_UNEVEN, T0, {}, now=_NOW)
    assert out[const.MAPPING_TEMPERATURE] == statistics.mean([10, 20])


def test_opting_in_switches_to_the_time_weighted_mean():
    out = aggregate_window(_UNEVEN, T0, {}, now=_NOW, time_weighted=True)
    # 10 holds T0->T0+1h, 20 holds T0+1h->now(T0+6h): (10*1 + 20*5) / 6
    assert out[const.MAPPING_TEMPERATURE] == (10 * 1 + 20 * 5) / 6


def test_the_two_modes_actually_differ_on_this_fixture():
    """Guards the test itself: a fixture where they agree would prove nothing."""
    off = aggregate_window(_UNEVEN, T0, {}, now=_NOW)[const.MAPPING_TEMPERATURE]
    on = aggregate_window(_UNEVEN, T0, {}, now=_NOW, time_weighted=True)[
        const.MAPPING_TEMPERATURE
    ]
    assert off != on


def test_evenly_spaced_polling_is_close_either_way():
    """Why gating is safe rather than merely conservative.

    On the regime a poll-only install actually produces — one row per tick —
    the two means agree closely, so opting in later is not a cliff.
    """
    evenly = [_r(i, Temperature=10 + i) for i in range(7)]
    now = T0 + datetime.timedelta(hours=6)
    off = aggregate_window(evenly, T0, {}, now=now)[const.MAPPING_TEMPERATURE]
    on = aggregate_window(evenly, T0, {}, now=now, time_weighted=True)[
        const.MAPPING_TEMPERATURE
    ]
    assert abs(off - on) < 1.0


def test_min_and_max_are_unaffected_by_the_flag():
    """Only AVERAGE is time-weighted; the extremes span every sample either way."""
    for flag in (False, True):
        out = aggregate_window(_UNEVEN, T0, {}, now=_NOW, time_weighted=flag)
        assert out[const.MAPPING_MIN_TEMP] == 10
        assert out[const.MAPPING_MAX_TEMP] == 20
