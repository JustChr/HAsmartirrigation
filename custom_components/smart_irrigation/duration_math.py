"""Deficit-to-duration pricing, shared by the calculation and the wall-clock model.

Pure arithmetic — no Home Assistant import — so :mod:`run_window` (also HA-free)
can price a zone's duration without pulling in the coordinator's import graph.
``calculation.py`` imports these two names for its existing callers (the
runner's live-estimate gate, the finish-anchor estimate); this module is the
one place the deficit math lives, not a second copy of it.

The three unit conversions below (length, volume, area) are inlined rather
than routed through ``helpers.convert_between``, because that helper's module
sits behind ``homeassistant.core``/``homeassistant.exceptions`` imports at
load time — importing it here would undo the point of keeping this pure. Each
inlined conversion is the exact arithmetic ``convert_between`` performs for
these specific unit pairs (see ``helpers.convert_length`` /
``convert_volume`` / ``convert_area``), using the same factor constants from
``const.py``, so there is nothing here to drift out of step with.
"""

from __future__ import annotations

from . import const


def duration_from_deficit(
    deficit,
    throughput,
    size,
    multiplier,
    maximum_duration,
    lead_time,
    metric,
):
    """Irrigation run time (seconds) needed to replenish ``deficit``.

    A pure mirror of the duration math in :meth:`CalculationMixin.calculate_module`
    (precipitation-rate → raw seconds → multiplier → maximum-duration clamp →
    lead time) so the irrigation runner can recompute a duration from the live
    intra-day deficit at run time without duplicating — or drifting from — that
    logic. ``deficit`` / ``throughput`` / ``size`` are in the user's display
    units (mm, L/min, m² when metric; in, gal/min, ft² when imperial). Returns 0
    when no irrigation is needed (``deficit`` >= 0) or the zone lacks a usable
    throughput / size. ``test_live_duration`` pins this against
    ``calculate_module`` to guard against drift.
    """
    if deficit is None or deficit >= 0:
        return 0
    tput = throughput or 0.0
    sz = size or 0.0
    deficit_mm = deficit
    if not metric:
        tput = tput * const.GALLON_TO_LITER_FACTOR  # gal/min -> l/min
        sz = sz * const.SQ_FT_TO_M2_FACTOR  # sq ft -> m2
        deficit_mm = deficit * const.INCH_TO_MM_FACTOR  # in -> mm
    if not tput or not sz:
        return 0
    precipitation_rate = (tput * 60) / sz
    duration = abs(deficit_mm) / precipitation_rate * 3600
    duration = (multiplier if multiplier is not None else 1) * duration
    if (
        maximum_duration is not None
        and maximum_duration >= 0
        and duration > maximum_duration
    ):
        duration = maximum_duration
    if duration > 0.0:
        return round((lead_time or 0) + duration)
    return round(duration)


def zone_run_duration(zone, deficit, metric, *, capped=True):
    """``duration_from_deficit`` with the arguments packed from ``zone``.

    The single place a zone dict is unpacked into the duration math. Two
    callers: the runner's sizing in ``irrigation._duration_for_deficit``,
    which asks for both forms so it can tell that the cap bit, and the
    wall-clock model's nominal pricing in ``run_window.nominal_zone_seconds``.
    ``capped=False`` ignores ``maximum_duration``, for callers measuring how
    much the cap cut.
    """
    return duration_from_deficit(
        deficit,
        zone.get(const.ZONE_THROUGHPUT),
        zone.get(const.ZONE_SIZE),
        zone.get(const.ZONE_MULTIPLIER),
        zone.get(const.ZONE_MAXIMUM_DURATION) if capped else None,
        zone.get(const.ZONE_LEAD_TIME),
        metric,
    )
