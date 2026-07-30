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

Level fields (AVERAGE) are aggregated **over time**, not over stored rows: a row
exists because a value moved, so row density is a property of the field rather
than of the clock, and a plain mean of the rows weights a jittery field's
readings the same as a still one's. See ``_time_weighted_mean``.
"""

import datetime
import logging
import statistics

from . import const
from .helpers import parse_datetime

_LOGGER = logging.getLogger(__name__)

# Aggregates that ACCUMULATE over the window (area under a rate curve, or a
# running total) rather than summarising level samples. A carried-forward value
# must never be backfilled into one of these — see aggregate_window.
_INTEGRAL_AGGREGATES = (
    const.MAPPING_CONF_AGGREGATE_RIEMANNSUM,
    const.MAPPING_CONF_AGGREGATE_SUM,
)


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
    """Group reading dicts into ``{sensor_key: [(timestamp, value), ...]}``.

    Each value carries its OWN timestamp rather than the key sharing one parallel
    RETRIEVED_AT list. The continuous-update path appends a sparse row per field
    change, so a field's samples are a subset of the window's rows: a shared list
    does not line up with them, and both time-weighted AVERAGE and RIEMANNSUM
    need to know when each individual value was read.

    Skips None values, drops the derived MAX/MIN temp and the non-numeric
    observation time.
    """
    by_sensor = {}
    for d in readings:
        if not isinstance(d, dict):
            continue
        stamp = _parse(d.get(const.RETRIEVED_AT))
        for key, val in d.items():
            if val is None or key == const.RETRIEVED_AT:
                continue
            by_sensor.setdefault(key, []).append((stamp, val))
    by_sensor.pop(const.MAPPING_MAX_TEMP, None)
    by_sensor.pop(const.MAPPING_MIN_TEMP, None)
    by_sensor.pop(const.OBSERVATION_TIME, None)
    return by_sensor


def _window_bounds(effective, watermark, now):
    """The interval a time-weighted aggregate averages over, or ``(None, None)``.

    Start is the watermark when there is one: the boundary reading is re-stamped
    to it, so the window genuinely begins there. A never-consumed zone has no
    watermark, and then the earliest reading is the only defensible start.

    End is ``now``, not the last reading. A field that stopped producing rows has
    not stopped existing, and for solar radiation "produced no rows" is precisely
    what a night looks like. Clamped past any reading stamped after ``now`` so a
    clock skew cannot yield a negative-length window.
    """
    stamps = [t for r in effective if (t := _parse(r.get(const.RETRIEVED_AT)))]
    start = watermark if watermark is not None else (min(stamps) if stamps else None)
    end = max([now, *stamps]) if stamps else now
    if start is None or end is None or end <= start:
        return None, None
    return start, end


def _time_weighted_mean(times, values, start, end):
    """Carry-forward integral over ``[start, end]`` divided by the window length.

    A plain mean of the stored rows assumes evenly spaced samples, and neither
    ingestion path produces those. The continuous path appends a row only when a
    field MOVES, so how often a field is sampled depends on the field's own
    behaviour. Solar radiation is the pathological case and the reason this
    exists: it is pinned at 0 all night, so it emits no night rows at all, and
    the "daily mean" became a mean over daylight samples only — measured at
    2.02-2.78x the true 24 h mean on nine days of production data. PyETO's
    clear-sky clamp then pinned Rs at Rso and hid it, computing ET roughly as if
    every day were cloudless (over-watering on overcast days).

    Zero-order hold, not trapezoid: with a deadband, "no reading" means "the
    value has not moved past the threshold", so the stored series really is a
    step function. On real solar the two rules agree to ~0.1% anyway.

    Returns None when the samples cannot support it (an unparseable stamp, or a
    zero-length window), so the caller falls back to the plain mean.
    """
    if start is None or end is None or any(t is None for t in times):
        return None
    span = (end - start).total_seconds()
    if span <= 0:
        return None

    # The first sample is held BACKWARDS to the window start. Its field may have
    # produced no row before then, and the buffer retains only a single
    # pre-watermark row, so there is no per-key history to reach for. Residual on
    # the worst field: solar's first row of the day sits at the deadband (~6
    # W/m2), so a 7 h pre-dawn stretch costs ~0.7% of the daily mean, against the
    # ~122% the plain mean was overstating it by.
    prev_t, prev_v = start, values[0]
    integral = 0.0
    for t, v in zip(times, values, strict=True):
        t = min(max(t, start), end)
        if t > prev_t:
            integral += prev_v * (t - prev_t).total_seconds()
            prev_t = t
        # Out-of-order or duplicate stamps contribute zero width rather than a
        # negative one; the later value still wins from here on.
        prev_v = v
    # The last sample is held FORWARDS to the window end for the same reason: a
    # field that stopped changing is still reading that value.
    integral += prev_v * (end - prev_t).total_seconds()
    return integral / span


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
            if key in by_sensor or val is None:
                continue
            # RETRIEVED_AT is a stamp, not a reading: _group_by_sensor no longer
            # carries it as a key, so without this it would be backfilled and
            # then float()ed as if it were a measurement.
            if key == const.RETRIEVED_AT:
                continue
            # Never backfill a field whose aggregate INTEGRATES the window: one
            # carried-forward sample would be read as real accumulation rather
            # than as a level. Concretely, a sensor-sourced precipitation field
            # overridden to riemannsum takes the single-value path and returns
            # the rate verbatim — as if it had rained at that rate for an hour —
            # so a stale carry-forward fabricates rain, and fabricated rain
            # suppresses irrigation (under-watering).
            #
            # DELTA is deliberately NOT excluded: it is a counter difference, so a
            # single value yields 0, which is exactly right — no change in a
            # cumulative rain gauge means no rain, and an explicit 0 is better for
            # the calc module than a missing field.
            if _effective_aggregate(key, mappings_config) in _INTEGRAL_AGGREGATES:
                continue
            # No stamp: a carry-forward is a single value, which every aggregate
            # resolves without needing to know when it was read.
            by_sensor[key] = [(None, val)]

    resultdata = {}
    resultdata[const.MAPPING_DATA_MULTIPLIER] = _hour_multiplier(window, watermark, now)
    window_start, window_end = _window_bounds(effective, watermark, now)
    _aggregate(by_sensor, mappings_config, resultdata, window_start, window_end)
    return resultdata


def _effective_aggregate(key, mappings_config):
    """Resolve which aggregate applies to ``key``.

    Single source of truth for the rule, so the backfill guard in
    ``aggregate_window`` and the arithmetic in ``_aggregate`` cannot drift apart.
    """
    aggregate = const.MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT
    if key == const.MAPPING_PRECIPITATION:
        # Cumulative rain-gauge sensors count up and reset at midnight (DELTA);
        # weather-service precip is a rate (mm/h) integrated by RIEMANNSUM so
        # the result is correct at any update frequency.
        precip_source = (
            (mappings_config.get(const.MAPPING_PRECIPITATION) or {}).get(
                const.MAPPING_CONF_SOURCE
            )
            if mappings_config
            else None
        )
        if precip_source == const.MAPPING_CONF_SOURCE_WEATHER_SERVICE:
            aggregate = const.MAPPING_CONF_AGGREGATE_RIEMANNSUM
        else:
            aggregate = const.MAPPING_CONF_AGGREGATE_OPTIONS_DEFAULT_PRECIPITATION
    if mappings_config and key in mappings_config:
        field_config = mappings_config[key]
        # Legacy stored shape: a bare string instead of a config dict.
        if isinstance(field_config, dict):
            aggregate = field_config.get(const.MAPPING_CONF_AGGREGATE, aggregate)
    return aggregate


def _aggregate(by_sensor, mappings_config, resultdata, window_start, window_end):
    """Apply each sensor's aggregate to its ``(timestamp, value)`` samples."""
    for key, raw in by_sensor.items():
        if key == const.RETRIEVED_AT:
            continue
        times = [t for t, _ in raw]
        d = [float(v) for _, v in raw]

        if key == const.MAPPING_TEMPERATURE:
            resultdata[const.MAPPING_MAX_TEMP] = max(d)
            resultdata[const.MAPPING_MIN_TEMP] = min(d)
        aggregate = _effective_aggregate(key, mappings_config)

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
            weighted = _time_weighted_mean(times, d, window_start, window_end)
            resultdata[key] = statistics.mean(d) if weighted is None else weighted
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
            # Trapezoidal integral of rate x dt over each field's OWN stamps; the
            # boundary point (at the watermark) makes the first interval span
            # "since last consumed". Deliberately NOT extended to the window end
            # the way the time-weighted mean is: holding a RATE forward past its
            # last reading fabricates accumulation, and fabricated rain suppresses
            # irrigation.
            #
            # Per-key stamps are what make this correct on a sparse buffer. The
            # earlier form read one parallel RETRIEVED_AT list and fell back to
            # dt = 1 h per interval whenever the lengths disagreed - which is
            # every continuous-update buffer, where RETRIEVED_AT is on every row
            # and the field itself is on only a few.
            riemann = 0.0
            for i in range(len(d) - 1):
                if times[i] is not None and times[i + 1] is not None:
                    dt_hours = max((times[i + 1] - times[i]).total_seconds() / 3600, 0)
                else:
                    dt_hours = 1.0
                riemann += ((d[i] + d[i + 1]) / 2) * dt_hours
            resultdata[key] = riemann
