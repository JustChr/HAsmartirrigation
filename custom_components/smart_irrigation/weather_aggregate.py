"""Pure, side-effect-free aggregation of a per-zone window of mapping data.

Weather readings are stored as a shared rolling buffer on the *mapping*
(``MAPPING_DATA``), but each zone consumes its own window of that buffer up to
its ``last_consumed_at`` watermark (multiple zones can share one mapping). This
module turns ``(readings, watermark, mapping_config)`` into the aggregated
weather dict the calculation modules expect — with no store writes and no
dependence on the (now retired) per-mapping ``MAPPING_DATA_LAST_CALCULATION``.

The window is ``readings with RETRIEVED_AT > watermark`` plus a synthetic
*boundary* = the last reading at-or-before the watermark, re-stamped to the
watermark time. The boundary is the first element of the effective series, which
makes it the DELTA baseline and the RIEMANNSUM integration start — exactly what
the previous "keep one anchor after clearing" scheme produced for a single
consumer, so single-consumer behaviour is preserved.
"""

import datetime
import logging
import statistics

from . import const
from .helpers import parse_datetime

_LOGGER = logging.getLogger(__name__)


def _parse(value):
    """Parse a stored RETRIEVED_AT (datetime or ISO string) to datetime/None."""
    if isinstance(value, datetime.datetime):
        return value
    if value is None:
        return None
    return parse_datetime(value)


def select_window(readings, watermark):
    """Split ``readings`` around ``watermark``.

    Returns ``(boundary, window)`` where ``boundary`` is the latest reading at or
    before the watermark (or None) and ``window`` is the readings strictly after
    it. With ``watermark`` None (never-consumed zone) the whole buffer is the
    window and there is no boundary.
    """
    if watermark is None:
        return None, [r for r in readings if isinstance(r, dict)]
    boundary = None
    boundary_dt = None
    window = []
    for r in readings:
        if not isinstance(r, dict):
            continue
        rdt = _parse(r.get(const.RETRIEVED_AT))
        if rdt is not None and rdt <= watermark:
            if boundary_dt is None or rdt >= boundary_dt:
                boundary, boundary_dt = r, rdt
        else:
            window.append(r)
    return boundary, window


def _group_by_sensor(readings):
    """Group reading dicts into ``{sensor_key: [values...]}`` (parallel lists).

    Mirrors the previous ``_group_data_by_sensor``: skips None values, drops the
    derived MAX/MIN temp and the non-numeric observation time, but keeps
    RETRIEVED_AT (the Riemann sum needs its timestamps).
    """
    by_sensor = {}
    for d in readings:
        if isinstance(d, dict):
            for key, val in d.items():
                if val is not None:
                    by_sensor.setdefault(key, []).append(val)
    by_sensor.pop(const.MAPPING_MAX_TEMP, None)
    by_sensor.pop(const.MAPPING_MIN_TEMP, None)
    by_sensor.pop(const.OBSERVATION_TIME, None)
    return by_sensor


def _hour_multiplier(window, watermark, now):
    """Elapsed window length as a fraction of a day (ET is a daily quantity).

    Anchored to the watermark when present, else to the span of the window's
    own RETRIEVED_ATs (a never-consumed zone), matching the previous logic.
    """
    diff = None
    if watermark is not None:
        diff = now - watermark
    else:
        times = [t for r in window if (t := _parse(r.get(const.RETRIEVED_AT)))]
        if not times:
            return 0
        diff = max(times) - min(times)
    return abs(diff.total_seconds() / 3600) / 24


def aggregate_window(
    readings, watermark, mappings_config, *, now=None, last_entry=None
):
    """Aggregate one zone's window of mapping readings.

    Args:
        readings: the mapping's full ``MAPPING_DATA`` list (shared buffer).
        watermark: the zone's ``last_consumed_at`` (datetime) or None.
        mappings_config: the mapping's ``MAPPING_MAPPINGS`` dict (sources +
            per-sensor aggregate overrides).
        now: override for "now" (testing); defaults to ``datetime.now()``.
        last_entry: optional ``MAPPING_DATA_LAST_ENTRY`` used to backfill missing
            sensors for continuous-update mappings.

    Returns:
        The aggregated weather dict (including ``MAPPING_DATA_MULTIPLIER``), or
        None when there is nothing to aggregate.
    """
    if now is None:
        now = datetime.datetime.now()
    mappings_config = mappings_config or {}

    boundary, window = select_window(readings, watermark)
    if boundary is None and not window:
        return None

    # Effective series = the carried-forward boundary (re-stamped to the
    # watermark so it acts as the anchor) followed by the new readings.
    effective = []
    if boundary is not None:
        effective.append({**boundary, const.RETRIEVED_AT: watermark})
    effective.extend(window)

    by_sensor = _group_by_sensor(effective)
    if last_entry:
        for key, val in last_entry.items():
            if key not in by_sensor and val is not None:
                by_sensor[key] = [val]

    resultdata = {}
    resultdata[const.MAPPING_DATA_MULTIPLIER] = _hour_multiplier(window, watermark, now)
    _aggregate(by_sensor, mappings_config, resultdata)
    return resultdata


def _aggregate(by_sensor, mappings_config, resultdata):
    """Apply each sensor's aggregate to its values (mirrors the old logic)."""
    for key, raw in by_sensor.items():
        if key == const.RETRIEVED_AT:
            continue
        d = [float(i) for i in raw]

        aggregate = const.MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT
        if key == const.MAPPING_PRECIPITATION:
            # Cumulative rain-gauge sensors count up and reset at midnight (DELTA);
            # weather-service precip is a rate (mm/h) integrated by RIEMANNSUM so
            # the result is correct at any update frequency.
            precip_source = (
                mappings_config.get(const.MAPPING_PRECIPITATION, {}).get(
                    const.MAPPING_CONF_SOURCE
                )
                if mappings_config
                else None
            )
            if precip_source == const.MAPPING_CONF_SOURCE_WEATHER_SERVICE:
                aggregate = const.MAPPING_CONF_AGGREGATE_RIEMANNSUM
            else:
                aggregate = const.MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT_PRECIPITATION
        elif key == const.MAPPING_TEMPERATURE:
            resultdata[const.MAPPING_MAX_TEMP] = max(d)
            resultdata[const.MAPPING_MIN_TEMP] = min(d)
        if key in mappings_config:
            aggregate = mappings_config[key].get(
                const.MAPPING_CONF_AGGREGATE, aggregate
            )

        if aggregate == const.MAPPING_CONF_AGGREGATE_DELTA:
            # Cumulative counter: sum positive increments, treating the first
            # value (the carried-forward boundary) as the baseline and resetting
            # on a drop to zero (midnight rollover).
            prev = d[0]
            result = 0
            for val in d:
                if val < prev:
                    # Reset to zero (midnight rollover) re-bases at 0; any other
                    # decrease is spurious and contributes nothing.
                    prev = 0 if val == 0 else val
                result += val - prev
                prev = val
            resultdata[key] = result
        elif len(d) < 2:
            if key == const.MAPPING_TEMPERATURE:
                resultdata[const.MAPPING_MAX_TEMP] = d[0]
                resultdata[const.MAPPING_MIN_TEMP] = d[0]
            resultdata[key] = d[0]
        elif aggregate == const.MAPPING_CONF_AGGREGATE_AVERAGE:
            resultdata[key] = statistics.mean(d)
        elif aggregate == const.MAPPING_CONF_AGGREGATE_FIRST:
            resultdata[key] = d[0]
        elif aggregate == const.MAPPING_CONF_AGGREGATE_LAST:
            resultdata[key] = d[-1]
        elif aggregate == const.MAPPING_CONF_AGGREGATE_MAXIMUM:
            resultdata[key] = max(d)
        elif aggregate == const.MAPPING_CONF_AGGREGATE_MINIMUM:
            resultdata[key] = min(d)
        elif aggregate == const.MAPPING_CONF_AGGREGATE_MEDIAN:
            resultdata[key] = statistics.median(d)
        elif aggregate == const.MAPPING_CONF_AGGREGATE_SUM:
            resultdata[key] = sum(d)
        elif aggregate == const.MAPPING_CONF_AGGREGATE_RIEMANNSUM:
            # Trapezoidal integral of rate x dt; the boundary point (at the
            # watermark) makes the first interval span "since last consumed".
            times = []
            if const.RETRIEVED_AT in by_sensor:
                stamps = by_sensor[const.RETRIEVED_AT]
                if len(stamps) == len(d):
                    for t in stamps:
                        if parsed := _parse(t):
                            times.append(parsed)
            if len(d) < 2:
                resultdata[key] = float(d[0]) * 1.0
            else:
                riemann = 0.0
                for i in range(len(d) - 1):
                    if len(times) == len(d):
                        dt_hours = max(
                            (times[i + 1] - times[i]).total_seconds() / 3600, 0
                        )
                    else:
                        dt_hours = 1.0
                    riemann += ((d[i] + d[i + 1]) / 2) * dt_hours
                resultdata[key] = riemann
