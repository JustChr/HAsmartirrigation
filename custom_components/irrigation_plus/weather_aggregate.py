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

Level fields (AVERAGE) can be aggregated **over time** rather than over stored
rows: on a sparse buffer a row exists because a value moved, so row density is a
property of the field rather than of the clock, and a plain mean of the rows
weights a jittery field's readings the same as a still one's. See
``_time_weighted_mean``.

That is opt-in via ``time_weighted``, which callers drive from the
``continuousupdates`` config flag. A poll-only install's rows are evenly spaced
by the update timer — the regime where a plain mean is already right — so
turning it on there would move existing users' ET for no benefit. With the flag
off this module is byte-identical to the poll-only behaviour that shipped before
continuous updates existed.
"""

import bisect
import datetime
import logging
import statistics
from typing import NamedTuple

from . import const
from .et_hourly import (
    atm_pressure,
    clear_sky_radiation_hourly_eq36,
    extraterrestrial_radiation_hourly,
    solar_elevation_sin,
    svp_from_t,
)
from .helpers import parse_datetime

_LOGGER = logging.getLogger(__name__)

# Ceiling on how long one water-balance sub-step may run. Sub-steps are aligned
# to wall-clock hours rather than to "every N hours from the window start" so
# that they coincide with the hour FAO-56 hourly ETo is defined on — the ET
# quantum a later change can hand this loop without re-cutting the steps.
_SUBSTEP_MAX_HOURS = 1.0

# Backstop on the hour-boundary walk. A zone whose watermark is absurdly far in
# the past (a corrupted store, a clock jump) would otherwise spin building
# millions of boundaries. Past this the precipitation event times still cut the
# window; only the idle-hours ceiling is dropped.
_SUBSTEP_MAX_HOUR_BOUNDARIES = 24 * 62

# Longest window ``build_hourly_rows`` will reduce. Matches the buffer retention
# cap: beyond it the buffer cannot hold readings for most of the window, so every
# extra hour would be pure carry-forward from one stale sample. Summing a
# fabricated series is worse than the daily form, so the caller falls back.
_HOURLY_ROWS_MAX_HOURS = 24 * 7

# Fields an hourly FAO-56 row cannot be built without. Pressure is optional (the
# ETo helper derives it from elevation when absent) and precipitation is carried
# for the row consumers rather than for the ET itself.
_HOURLY_ROW_REQUIRED = (
    const.MAPPING_TEMPERATURE,
    const.MAPPING_HUMIDITY,
    const.MAPPING_WINDSPEED,
    const.MAPPING_SOLRAD,
)

# Buffer solar radiation is stored as MJ/day/m2; FAO-56 hourly wants MJ/m2/h.
# 1 W/m2 = 0.0864 MJ/day/m2 = 0.0036 MJ/m2/h, so the ratio is exactly 24.
# Worked case: 800 W/m2 -> 69.12 MJ/day/m2 -> 2.88 MJ/m2/h. Omitting this hands
# the ETo helper ~12x the solar constant and the day's ET goes with it.
_MJ_DAY_TO_MJ_HOUR = 1.0 / 24.0

# Stored pressure is absolute hPa (both ingestion paths correct relative
# readings before the buffer); FAO-56 takes kPa.
_HPA_TO_KPA = 1.0 / 10.0

# Smallest clear-sky radiation [MJ/m2/h] a clearness ratio may be divided by.
# Within a few minutes of sunrise Rso is near zero, so an unguarded division
# turns sensor noise into an enormous ratio that would then be carried into the
# whole of the following gap. Below this the hour simply contributes no ratio.
_RSO_RATIO_FLOOR = 0.02

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


def merge_latest_per_field(fields, timestamp, row, *, keep_row):
    """Fold ``row``'s non-null fields into ``fields`` (key -> (timestamp, payload)).

    Keeps only the latest-stamped payload per field, ties won by the later
    call (``>=``) — the same per-field latest-wins rule both ``select_window``'s
    boundary merge and ``calculation._prune_mapping_buffer``'s per-field prune
    need, shared so it can't drift between the two copies. ``keep_row``
    chooses the payload: ``select_window`` wants the field's own value (it is
    building a synthetic boundary reading), ``_prune_mapping_buffer`` wants
    the row it came from (it is deciding what stays in the stored buffer).
    """
    for key, val in row.items():
        if val is None or key == const.RETRIEVED_AT:
            continue
        prev = fields.get(key)
        if prev is None or timestamp >= prev[0]:
            fields[key] = (timestamp, row if keep_row else val)


def select_window(readings, watermark):
    """Split ``readings`` around ``watermark``.

    Returns ``(boundary, window)`` where ``boundary`` carries, for each field,
    its latest value at or before the watermark (or None when nothing precedes
    it) and ``window`` is the readings strictly after it. With ``watermark``
    None (never-consumed zone) the whole buffer is the window and there is no
    boundary.

    The boundary is merged PER FIELD, not taken as the single latest row: the
    event-driven ingestion path writes sparse rows (one field per event), so
    the latest pre-watermark row only carries whichever field moved last. Every
    other field's carried value — the DELTA baseline for a cumulative rain
    gauge, the RIEMANN integration start — lives in an earlier row, and taking
    one row silently zeroed a gauge rise that straddled the watermark. Full
    (polled) rows carry every field, so for them the merge degenerates to the
    latest row and nothing moves.
    """
    if watermark is None:
        return None, [r for r in readings if isinstance(r, dict)]
    fields = {}  # key -> (stamp, value): latest pre-watermark value per field
    boundary_dt = None
    window = []
    for r in readings:
        if not isinstance(r, dict):
            continue
        rdt = _parse(r.get(const.RETRIEVED_AT))
        if rdt is not None and rdt <= watermark:
            if boundary_dt is None or rdt >= boundary_dt:
                boundary_dt = rdt
            merge_latest_per_field(fields, rdt, r, keep_row=False)
        else:
            window.append(r)
    if boundary_dt is None:
        return None, window
    boundary = {key: val for key, (_, val) in fields.items()}
    boundary[const.RETRIEVED_AT] = boundary_dt
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
    readings,
    watermark,
    mappings_config,
    *,
    now=None,
    last_entry=None,
    time_weighted=False,
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
        time_weighted: aggregate AVERAGE fields over time instead of over stored
            rows. Only correct for the sparse buffers the event-driven path
            produces; defaults to False so poll-only installs keep the plain
            mean they have always had.

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
            if effective_aggregate(key, mappings_config) in _INTEGRAL_AGGREGATES:
                continue
            # No stamp: a carry-forward is a single value, which every aggregate
            # resolves without needing to know when it was read.
            by_sensor[key] = [(None, val)]

    resultdata = {}
    resultdata[const.MAPPING_DATA_MULTIPLIER] = _hour_multiplier(window, watermark, now)
    window_start, window_end = _window_bounds(effective, watermark, now)
    _aggregate(
        by_sensor,
        mappings_config,
        resultdata,
        window_start,
        window_end,
        time_weighted=time_weighted,
    )
    return resultdata


def effective_aggregate(key, mappings_config):
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


def _aggregate(
    by_sensor,
    mappings_config,
    resultdata,
    window_start,
    window_end,
    time_weighted=False,
):
    """Apply each sensor's aggregate to its ``(timestamp, value)`` samples."""
    for key, raw in by_sensor.items():
        if key == const.RETRIEVED_AT:
            continue
        times = [t for t, _ in raw]
        d = [float(v) for _, v in raw]

        if key == const.MAPPING_TEMPERATURE:
            resultdata[const.MAPPING_MAX_TEMP] = max(d)
            resultdata[const.MAPPING_MIN_TEMP] = min(d)
        aggregate = effective_aggregate(key, mappings_config)

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
            # Time-weighting is opt-in with continuous updates. A sparse buffer
            # NEEDS it — a row exists because a value moved, so a plain mean
            # weights a jittery field's readings the same as a still one's, and
            # solar radiation (no rows overnight) becomes a daylight-only mean.
            # But a polled install's rows are evenly spaced by the timer, where
            # the two agree closely, so applying it there would silently move
            # every existing user's ET. Off => byte-identical to the poll-only
            # behaviour that shipped before continuous updates existed.
            weighted = (
                _time_weighted_mean(times, d, window_start, window_end)
                if time_weighted
                else None
            )
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


class WaterStep(NamedTuple):
    """One sub-step of the water balance over a calculation window.

    ``et_weight`` is this step's share of the window's total ET and the weights
    sum to 1.0, so the window's ET is exactly conserved however it is split.
    ``precip_mm`` is the rain that landed at the END of the step: a rain-gauge
    increment read at time t fell during the interval ending at t.

    ``applied_mm`` is irrigation credited to the bucket during the step, booked
    by the same end-of-step rule. Kept apart from ``precip_mm`` because that one
    has to reconcile against the window's precipitation aggregate — the two are
    the same water to the balance and different water to the ledger.
    """

    dt_hours: float
    et_weight: float
    precip_mm: float
    applied_mm: float = 0.0


def _clamped_samples(samples, start, end):
    """``[(time, value)]`` clamped into the window, stamps required.

    Returns None if any stamp is missing, which is the signal to fall back: a
    value with no time cannot be placed on a timeline.
    """
    out = []
    for t, v in samples:
        if t is None:
            return None
        out.append((min(max(t, start), end), float(v)))
    return out


def _hold_integral_table(samples, start, end):
    """Cumulative zero-order-hold integral of a level field over the window.

    Same hold rules as ``_time_weighted_mean`` — first sample held back to the
    window start, last held forward to the end — but retained as a cumulative
    table so an arbitrary sub-interval's integral is two lookups rather than a
    re-scan. Returns ``(points, values, cumulative)`` where ``values[i]`` is in
    force on ``[points[i], points[i + 1]]``.
    """
    points = [start]
    values = []
    prev_v = samples[0][1]
    for t, v in samples:
        if t > points[-1]:
            points.append(t)
            values.append(prev_v)
        prev_v = v
    if end > points[-1]:
        points.append(end)
        values.append(prev_v)
    cumulative = [0.0]
    for i, v in enumerate(values):
        cumulative.append(
            cumulative[-1] + v * (points[i + 1] - points[i]).total_seconds()
        )
    return points, values, cumulative


def _hold_integral_upto(points, values, cumulative, t):
    """Integral of the held step function from the window start to ``t``."""
    if t <= points[0]:
        return 0.0
    if t >= points[-1]:
        return cumulative[-1]
    i = bisect.bisect_right(points, t) - 1
    return cumulative[i] + values[i] * (t - points[i]).total_seconds()


def _precip_increments(samples, aggregate):
    """``[(time, mm)]`` whose sum is exactly what ``_aggregate`` reports.

    The two halves of the calculation have to agree to the last decimal: the
    aggregate's total becomes ZONE_DELTA while these increments drive the bucket,
    and a mismatch would surface as a ledger that does not add up. So this
    mirrors the arithmetic in ``_aggregate`` rather than re-deriving it.

    Returns None when the field has no time structure to sub-step, which is the
    signal to keep the single-shot path.
    """
    if aggregate == const.MAPPING_CONF_AGGREGATE_DELTA:
        # Cumulative counter: the first sample is the baseline (contributing 0),
        # and a drop to zero is a midnight rollover rather than negative rain.
        out = []
        prev = samples[0][1]
        for t, val in samples:
            if val < prev:
                prev = 0.0 if val == 0 else val
            out.append((t, val - prev))
            prev = val
        return out
    if aggregate == const.MAPPING_CONF_AGGREGATE_RIEMANNSUM:
        if len(samples) < 2:
            # A lone rate sample takes _aggregate's single-value path, which
            # reports the rate verbatim. There is no interval to attribute it to.
            return None
        out = []
        for i in range(len(samples) - 1):
            t0, v0 = samples[i]
            t1, v1 = samples[i + 1]
            dt_hours = max((t1 - t0).total_seconds() / 3600, 0)
            out.append((t1, (v0 + v1) / 2 * dt_hours))
        return out
    return None


def _substep_boundaries(start, end, event_times):
    """Sorted cut points for the window: every event, plus the hourly ceiling.

    Rain events are where sub-stepping earns its keep; wall-clock hour boundaries
    bound how long a single step can run when nothing is happening.
    """
    cuts = {start, end}
    for t in event_times:
        if start < t < end:
            cuts.add(t)
    step = datetime.timedelta(hours=_SUBSTEP_MAX_HOURS)
    boundary = start.replace(minute=0, second=0, microsecond=0) + step
    added = 0
    while boundary < end and added < _SUBSTEP_MAX_HOUR_BOUNDARIES:
        if boundary > start:
            cuts.add(boundary)
        boundary += step
        added += 1
    return sorted(cuts)


def _effective_series(readings, watermark, now):
    """``(effective_rows, start, end)`` for a zone's window, or ``(None, ...)``.

    The same window ``aggregate_window`` reduces, so anything derived from it
    agrees with the aggregate by construction rather than by coincidence.
    """
    boundary, window = select_window(readings, watermark)
    if boundary is None and not window:
        return None, None, None
    effective = []
    if boundary is not None:
        effective.append({**boundary, const.RETRIEVED_AT: watermark})
    effective.extend(window)
    start, end = _window_bounds(effective, watermark, now)
    if start is None:
        return None, None, None
    return effective, start, end


def _hourly_mean(table, a, b):
    """Mean of a held level field over ``[a, b]`` from a cumulative table."""
    span = (b - a).total_seconds()
    if span <= 0:
        return None
    return (_hold_integral_upto(*table, b) - _hold_integral_upto(*table, a)) / span


def _row_rso_eq36(row, hour, doy, latitude, longitude, elevation, tz_offset_h):
    """Clear-sky radiation [MJ/m2/h] for ``hour`` using this row's own air state.

    Every Eq. 36 input is already on the row: temperature and humidity give the
    actual vapour pressure, and pressure is the measured barometer when the
    mapping has one, else derived from elevation the same way the ETo helper
    derives it.

    ``tz_offset_h`` is the caller's window-wide fallback; a row that carries its
    own ``tz_offset_h`` wins. Rso is the DENOMINATOR of the clearness ratio, so
    an hour of solar-time error here moves the refilled radiation by +23.5% /
    -16.0%, two orders of magnitude more than the same error costs on the ETo
    path.
    """
    tz_offset_h = row.get("tz_offset_h", tz_offset_h)
    ra = extraterrestrial_radiation_hourly(latitude, longitude, doy, hour, tz_offset_h)
    if ra <= 0:
        return 0.0
    sin_beta = solar_elevation_sin(latitude, longitude, doy, hour, tz_offset_h)
    pressure_kpa = row.get("pressure_kpa")
    if pressure_kpa is None:
        pressure_kpa = atm_pressure(elevation)
    avp = svp_from_t(row["temperature"]) * max(0.0, min(100.0, row["humidity"])) / 100.0
    return clear_sky_radiation_hourly_eq36(ra, sin_beta, pressure_kpa, avp)


def _ratio_hold_solar(rows, solar_samples, latitude, longitude, elevation, tz_offset_h):
    """Refill the solar of hours that saw no reading from a held clearness ratio.

    The zero-order hold every other field uses is right for a **deadband gap**
    (solar sits pinned at 0 all night, emits no rows, and holding 0 is the true
    answer) and a fabrication for an **outage gap**, where the value moved and
    nobody looked. Holding the last absolute reading flat across a midday outage
    charges every silent hour full noon sun; holding a dawn reading flat charges
    the whole day dawn light. Measured on nine recorded days across six gap
    shapes, flat hold lands 77.4% from dense truth on average, and a held
    clearness ratio 15.7%.

    So carry ``Rs/Rso`` instead of ``Rs``, and let each gap hour supply its own
    Rso: **sky condition persists, solar geometry does not**. A midday ratio
    carried into the night lands at zero by construction because Rso is zero
    there, which is why this needs no separate night case and why it does not
    disturb the deadband gap it must not "fix".

    Only hours with no reading at all are touched, so a densely sampled buffer
    comes out byte-identical. The ratio is capped at
    ``SOLAR_CLEAR_SKY_TOLERANCE`` for the same reason the ingest clamp is: a
    physically impossible reading must not be projected forward across a gap.
    That ingest clamp stays — it guards readings, this guards fabricated hours.
    """
    if latitude is None or longitude is None:
        return
    # Newest reading within each clock hour: the freshest evidence of the sky
    # state, and the sample whose own timestamp the ratio's Rso is taken at.
    # Taking Rso at the hour midpoint instead would mis-scale a reading made
    # near the edge of an hour, which is precisely the dawn case Eq. 36 is here
    # to get right.
    newest = {}
    for stamp, value in solar_samples:
        hour_start = stamp.replace(minute=0, second=0, microsecond=0)
        current = newest.get(hour_start)
        if current is None or stamp >= current[0]:
            newest[hour_start] = (stamp, float(value))

    measured = {}
    for row in rows:
        sample = newest.get(row["hour_start"])
        if sample is None:
            continue
        stamp, value = sample
        rso = _row_rso_eq36(
            row,
            stamp.hour + stamp.minute / 60 + stamp.second / 3600,
            stamp.timetuple().tm_yday,
            latitude,
            longitude,
            elevation,
            tz_offset_h,
        )
        if rso > _RSO_RATIO_FLOOR:
            # Floored at 0 as well as capped: a pyranometer with a negative zero
            # offset would otherwise project *negative* radiation across every
            # hour of the gap, which raises net longwave loss and suppresses
            # irrigation.
            measured[row["hour_start"]] = min(
                max(0.0, value * _MJ_DAY_TO_MJ_HOUR / rso),
                const.SOLAR_CLEAR_SKY_TOLERANCE,
            )

    if not measured:
        # No hour in the window was bright enough to measure a ratio from (a
        # night-only window, or a window with no readings at all). There is
        # nothing to hold, so leave the flat hold exactly as it was.
        return

    # Forward-fill, then back-fill the leading gap with the first ratio measured
    # — the same "first sample held backwards to the window start" rule
    # ``_hold_integral_table`` applies to every other field, expressed in ratio
    # space. Leaving the leading gap unfilled would zero out real morning sun on
    # a window whose first reading arrives after sunrise.
    held = []
    current = None
    for row in rows:
        if row["hour_start"] in measured:
            current = measured[row["hour_start"]]
        held.append(current)
    first = next(r for r in held if r is not None)

    for row, ratio in zip(rows, held, strict=True):
        if row["hour_start"] in newest:
            # This hour has a measurement; its own mean stands. Includes the
            # dark hours that produced a reading but no usable Rso.
            continue
        row["solar_mj_h"] = (first if ratio is None else ratio) * _row_rso_eq36(
            row,
            row["hour"],
            row["doy"],
            latitude,
            longitude,
            elevation,
            tz_offset_h,
        )


def build_hourly_rows(
    readings,
    watermark,
    mappings_config,
    *,
    now=None,
    last_entry=None,
    latitude=None,
    longitude=None,
    elevation=0.0,
    tz_offset_h=0.0,
    tz=None,
):
    """Reduce a zone's window of the shared buffer to hourly FAO-56 rows, or None.

    One row per wall-clock hour the window touches, carrying the row shape the
    hourly ETo helpers consume: ``hour`` (local clock midpoint), ``doy``,
    ``temperature``, ``humidity``, ``wind_2m``, ``solar_mj_h``, ``time``, plus
    ``precipitation``, ``pressure_kpa`` and ``coverage_h``.

    Each field's hourly value is the zero-order-hold mean over the part of that
    hour inside the window — the same rule ``_time_weighted_mean`` applies to the
    whole window, reused rather than re-derived so the two cannot drift. That is
    also the missing-hour policy: a field that produced no reading during an hour
    is still reading its last value, which is what carry-forward means. Solar
    radiation is the case that makes it necessary, because it emits no rows at
    all overnight.

    **Solar radiation is the one exception**: an hour with no reading at all
    takes the last *clearness ratio* against its own clear-sky radiation rather
    than the last absolute value. See ``_ratio_hold_solar``. That needs the site
    coordinates, so ``latitude`` / ``longitude`` (east-positive degrees),
    ``elevation`` (m) and ``tz_offset_h`` (the local UTC offset the naive buffer
    stamps are in) are taken here. Without coordinates the flat hold stands,
    which is what every caller that has none would have got anyway.

    ``tz`` is the site's ``tzinfo``. Given one, each row resolves its own UTC
    offset from its own naive stamp and carries it as ``tz_offset_h``, and both
    the ETo series and the Eq. 36 ratio denominator prefer that to the scalar. A
    window can reach seven days and therefore span a DST transition, where one
    offset for the whole window puts every row on the far side an hour out in
    solar time. That is worth 0.26-0.74% on daily ETo but +23.5% / -16.0% on the
    radiation the clearness-ratio hold refills, because there Rso is a
    denominator. Ambiguous fall-back hours resolve ``fold=0``; the repeated hour
    is genuinely indistinguishable in a naive stamp.

    ``coverage_h`` is the fraction of the hour the window actually covers, so the
    partial hours at each end of the window are charged their real share rather
    than a whole hour of ET.

    Returns None whenever the window cannot support hourly rows — no readings, a
    zero-length window, an absurdly long one, or any required field missing from
    both the window and the carry-forward. The caller then keeps the daily form,
    so the failure mode is today's behaviour rather than a fabricated series.
    """
    if now is None:
        now = datetime.datetime.now()

    effective, start, end = _effective_series(readings, watermark, now)
    if effective is None:
        return None
    if (end - start).total_seconds() > _HOURLY_ROWS_MAX_HOURS * 3600:
        return None

    by_sensor = _group_by_sensor(effective)
    tables = {}
    solar_samples = None
    for key in (*_HOURLY_ROW_REQUIRED, const.MAPPING_PRESSURE):
        samples = by_sensor.get(key)
        if samples:
            samples = _clamped_samples(samples, start, end)
        elif last_entry and last_entry.get(key) is not None:
            # Sparse (continuous-update) buffers append one field per event, so a
            # slow-moving field can have no row inside this zone's window at all.
            # The mapping's last-seen value is what it was reading throughout —
            # the same fallback aggregate_window uses, held from the window start.
            samples = [(start, float(last_entry[key]))]
        else:
            samples = None
        if samples is None:
            if key in _HOURLY_ROW_REQUIRED:
                return None
            continue
        if key == const.MAPPING_SOLRAD:
            # Retained so the ratio hold can tell an hour that saw a reading
            # from one that did not. The clamped copy, so the boundary and the
            # carry-forward count as readings at the window start exactly as
            # they do for the integral table.
            solar_samples = samples
        tables[key] = _hold_integral_table(samples, start, end)

    # Precipitation is not part of the ET, but the row shape carries it for the
    # consumers that read a window as a series. Omitted entirely rather than
    # zero-filled when the field has no time structure: an absent key is honest,
    # a 0.0 is a claim that it did not rain.
    rain_by_hour = None
    precip_samples = by_sensor.get(const.MAPPING_PRECIPITATION)
    if precip_samples:
        precip_samples = _clamped_samples(precip_samples, start, end)
        if precip_samples is not None:
            increments = _precip_increments(
                precip_samples,
                effective_aggregate(const.MAPPING_PRECIPITATION, mappings_config),
            )
            if increments is not None:
                rain_by_hour = {}
                for t, mm in increments:
                    hour_start = t.replace(minute=0, second=0, microsecond=0)
                    rain_by_hour[hour_start] = rain_by_hour.get(hour_start, 0.0) + mm

    rows = []
    hour_start = start.replace(minute=0, second=0, microsecond=0)
    step = datetime.timedelta(hours=1)
    while hour_start < end:
        a = max(hour_start, start)
        b = min(hour_start + step, end)
        coverage = (b - a).total_seconds() / 3600
        if coverage <= 0:
            # Unreachable: the loop only visits hours that overlap the window.
            # Bail rather than silently drop an hour's ET if it ever is not.
            return None
        row = {
            "time": hour_start.isoformat(),
            "hour_start": hour_start,
            # Midpoint of the WHOLE clock hour even for a partial one: Ra is
            # integrated over the hour's solar-time angles and the partial
            # coverage is charged through coverage_h instead.
            "hour": hour_start.hour + 0.5,
            "doy": hour_start.timetuple().tm_yday,
            "coverage_h": coverage,
        }
        if tz is not None:
            # Resolved from THIS row's stamp, not once for the window: the
            # window can straddle a DST transition and the rows on either side
            # of it are in different offsets.
            row_offset = tz.utcoffset(hour_start)
            if row_offset is not None:
                row["tz_offset_h"] = row_offset.total_seconds() / 3600.0
        means = {key: _hourly_mean(table, a, b) for key, table in tables.items()}
        if any(v is None for v in means.values()):
            return None
        row["temperature"] = means[const.MAPPING_TEMPERATURE]
        row["humidity"] = means[const.MAPPING_HUMIDITY]
        # Sensor wind speed is handed to FAO-56 as u2 exactly as the daily path
        # does: the integration has never modelled the anemometer's height, and
        # rescaling here only for the hourly form would make the two disagree.
        row["wind_2m"] = means[const.MAPPING_WINDSPEED]
        row["solar_mj_h"] = means[const.MAPPING_SOLRAD] * _MJ_DAY_TO_MJ_HOUR
        if const.MAPPING_PRESSURE in means:
            row["pressure_kpa"] = means[const.MAPPING_PRESSURE] * _HPA_TO_KPA
        if rain_by_hour is not None:
            row["precipitation"] = rain_by_hour.get(hour_start, 0.0)
        rows.append(row)
        hour_start += step

    if not rows:
        return None
    if solar_samples:
        _ratio_hold_solar(
            rows, solar_samples, latitude, longitude, elevation or 0.0, tz_offset_h
        )
    return rows


def _weights_from_hourly_et(weights, hours, dt_hours, hourly_et):
    """Rescale intra-hour weights so each hour carries its own ET, or None.

    ``weights`` shape the ET *within* an hour; ``hourly_et`` sets how much ET
    that hour gets. Multiplying the two gives a weight set whose per-hour sums
    are proportional to the hourly ETo series, which is what makes the window
    total a sum of hourly quanta rather than one daily number spread out.

    Returns None when a step's hour is absent from ``hourly_et``: the two are
    derived from the same window, so a gap means an assumption broke, and
    charging that hour zero ET would silently under-water.
    """
    per_hour_weight = {}
    for hour, weight in zip(hours, weights, strict=True):
        if hour not in hourly_et:
            return None
        per_hour_weight[hour] = per_hour_weight.get(hour, 0.0) + weight
    out = []
    for hour, weight, dt in zip(hours, weights, dt_hours, strict=True):
        share = per_hour_weight[hour]
        if share > 0:
            fraction = weight / share
        else:
            # This hour is entirely dark (or has no usable radiation) but still
            # has ET to place: fall back to elapsed time WITHIN the hour, so the
            # hour's own total is preserved rather than leaking to a bright one.
            hour_seconds = sum(
                d for h, d in zip(hours, dt_hours, strict=True) if h == hour
            )
            fraction = dt / hour_seconds if hour_seconds > 0 else 0.0
        out.append(fraction * hourly_et[hour])
    return out


def build_substeps(
    readings, watermark, mappings_config, *, now=None, hourly_et=None, applied=None
):
    """Cut a zone's window into ordered water-balance sub-steps, or None.

    The single-shot form collapses a whole window to one ``(delta, elapsed)``
    pair: every drop of the window's rain lands at the window start, is clamped
    against ``maximum_bucket`` there, and whatever survives then drains for the
    full window. Both errors run one way. Late rain is over-drained (a downpour
    at :55 is charged a full hour of drainage), and rain spread through the day
    is over-clamped, because the drainage that would have made room between the
    bursts never happens. Measured across 140 real rain days, that booked
    186 mm/year as runoff that never occurred and cost up to 12.7 mm of bucket,
    which is 88 minutes of runtime on the slowest zone here.

    Replaying the window at its own event times removes both, and it is exact
    rather than approximate: ``drained_over_window`` is the closed-form solution
    of the drainage ODE at any dt, so irregular steps introduce no error.

    ``hourly_et`` turns the window's ET into a **per-hour quantum**: given
    ``{hour_start: eto_mm}`` each hour's own ET is distributed across the steps
    inside that hour, instead of one window total being spread across every step.
    The cuts already fall on wall-clock hour boundaries, so every step lies in
    exactly one hour and no re-cutting is needed. The returned weights still sum
    to 1 and are still applied to a single window total by the caller, so this
    only changes how that total is shaped.

    ``applied`` is ``[(datetime, mm)]`` of irrigation credited to the bucket
    inside the window. Each one earns a cut and is booked on the step it ends,
    exactly as rain is; the caller must then start the replay from the level
    BEFORE those credits, since the stored bucket already contains them.

    Returns None whenever the window cannot be sub-stepped faithfully — no
    timestamps, a zero-length window, a precipitation aggregate with no time
    structure, or a step whose hour is missing from ``hourly_et``. The caller
    then keeps the single-shot behaviour, so the failure mode is the status quo
    rather than a fabricated series.
    """
    if now is None:
        now = datetime.datetime.now()

    effective, start, end = _effective_series(readings, watermark, now)
    if effective is None:
        return None

    by_sensor = _group_by_sensor(effective)

    increments = []
    precip_samples = by_sensor.get(const.MAPPING_PRECIPITATION)
    if precip_samples:
        precip_samples = _clamped_samples(precip_samples, start, end)
        if precip_samples is None:
            return None
        increments = _precip_increments(
            precip_samples,
            effective_aggregate(const.MAPPING_PRECIPITATION, mappings_config),
        )
        if increments is None:
            return None

    # Only rain that actually fell earns a cut. A cumulative gauge reports on
    # every reading, so a dry day would otherwise be sliced into one step per
    # reading for no gain: the interval that matters is the one the rain landed
    # in, not the one the gauge happened to be read in.
    increments = [(t, mm) for t, mm in increments if mm]
    applied = [(t, mm) for t, mm in (applied or []) if mm and t is not None]
    cuts = _substep_boundaries(
        start, end, [t for t, _ in increments] + [t for t, _ in applied]
    )
    if len(cuts) < 2:
        return None

    # Rain is booked against the step it ends, and every increment time is one of
    # the cuts -- except one landing exactly on the window start, which belongs
    # to the first step rather than to a step that does not exist before it.
    def _book(events):
        at = {}
        for t, mm in events:
            idx = min(max(bisect.bisect_left(cuts, t), 1), len(cuts) - 1)
            at[cuts[idx]] = at.get(cuts[idx], 0.0) + mm
        return at

    rain_at = _book(increments)
    # A credit stamped outside the window is clamped onto the nearest end step by
    # the same rule rather than dropped: the stored bucket already contains it,
    # so losing it here would silently delete that water from the balance.
    applied_at = _book(applied)

    # ET is apportioned by measured solar radiation rather than evenly by elapsed
    # time. Both conserve the window total and the two differ by <= 0.004 mm on
    # the bucket, but ETo is ~93% radiation-driven at this site, so the
    # solar-weighted curve tracks a true per-minute evaluation to 0.006 mm/day
    # against 0.039 for the flat one, with an hour-boundary jump smaller than a
    # typical within-hour step. That is what keeps the intra-day shape honest for
    # anything that later publishes it.
    solar = by_sensor.get(const.MAPPING_SOLRAD)
    table = None
    if solar:
        solar = _clamped_samples(solar, start, end)
        if solar is not None:
            points, values, cumulative = _hold_integral_table(solar, start, end)
            if cumulative[-1] > 0:
                table = (points, values, cumulative)

    steps = []
    weights = []
    hours = []
    for i in range(len(cuts) - 1):
        a, b = cuts[i], cuts[i + 1]
        dt_hours = (b - a).total_seconds() / 3600
        if table is None:
            # No usable radiation (unmapped, or a window entirely after dark):
            # fall back to elapsed time, which is the same total spread flat.
            weight = dt_hours
        else:
            weight = max(
                0.0,
                _hold_integral_upto(*table, b) - _hold_integral_upto(*table, a),
            )
        weights.append(weight)
        hours.append(a.replace(minute=0, second=0, microsecond=0))
        steps.append((dt_hours, rain_at.get(b, 0.0), applied_at.get(b, 0.0)))

    if hourly_et is not None:
        weights = _weights_from_hourly_et(
            weights, hours, [dt for dt, _, _ in steps], hourly_et
        )
        if weights is None:
            return None

    total = sum(weights)
    if total <= 0:
        # Night-only window under solar weighting. ET over such a window is
        # <= 0.017 mm/day, but it still has to go somewhere: spread it by time.
        weights = [dt for dt, _, _ in steps]
        total = sum(weights)
        if total <= 0:
            return None

    return [
        WaterStep(dt_hours, weight / total, precip_mm, applied_mm)
        for (dt_hours, precip_mm, applied_mm), weight in zip(
            steps, weights, strict=True
        )
    ]
