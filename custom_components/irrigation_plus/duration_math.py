"""Deficit-to-duration pricing, shared by the calculation and the wall-clock model.

Pure arithmetic — no Home Assistant import — so a caller can price a zone's
duration without pulling in the coordinator's import graph. :mod:`run_window`
is the caller that was written for, and it is NOT itself HA-free, whatever this
sentence used to claim: ``run_window`` imports ``is_self_closing_zone`` from
``self_closing.py``, which imports ``homeassistant.helpers.event`` and
``homeassistant.util.dt``. Pre-existing and deliberate — a mode predicate lives
with its mode — but worth stating, because "run_window is HA-free" is exactly
the assumption under which someone plans a change to this file.

The constraint it was protecting still holds HERE, which is the half that
matters: this module's only imports are ``math`` and ``const``, and ``const``
imports nothing at all, so ``duration_math`` stays importable without Home
Assistant and its arithmetic stays testable on its own.

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

import math

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
    wall-clock model's nominal pricing in ``run_window.nominal_zone_duration``.
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


def calibrated_flow_seconds(zone, planned_seconds, metric):
    """``planned_seconds`` for a flow zone, re-priced at the rate it measured.

    Nothing in the planner knows a zone is flow-metered: a flow zone's duration
    is derived from its CONFIGURED throughput exactly as a timed zone's is, and
    is really ``target_volume / configured_rate``. The run then ignores that
    number entirely and delivers to the measured volume, so the two agree only
    where the configured throughput matches the plumbing. Where it does not,
    the error is systematic and one-directional per zone -- a zone plumbed
    slower than its setting overruns its estimate on every single run.

    ``_flow_calibration_check`` already measures the true rate, banking the
    observed litres-per-minute of each metered run in
    ``flow_calibration_samples`` in order to advise on the setting. Once there
    are enough samples to advise on, there are enough to price with, so the
    watering part of the estimate is scaled by
    ``configured_rate / observed_rate``. Nothing is invented: an install whose
    setting is right measures the same rate back and the estimate does not move.

    Only the watering scales. ``lead_time`` is a fixed cost of opening the zone
    and does not stretch with the flow. The result is clamped to the ceiling the
    run itself stops at (``maximum_duration``, or ``FLOW_SAFETY_TIMEOUT`` when
    unset), so a mis-scaled sensor cannot price a zone past the point its own
    safety timeout would close it.

    ``planned_seconds`` is returned unchanged for a zone with too few samples to
    advise on, or with either rate unreadable -- the configured throughput is
    the only answer available there.
    """
    planned = float(planned_seconds or 0.0)
    if planned <= 0:
        return planned
    samples = [s for s in (zone.get(const.ZONE_FLOW_CAL_SAMPLES) or []) if s]
    if len(samples) < const.FLOW_CAL_MIN_SAMPLES:
        return planned
    observed_lpm = sum(float(s) for s in samples) / len(samples)
    configured = float(zone.get(const.ZONE_THROUGHPUT) or 0.0)
    if not metric:
        # The samples are litres per minute whatever the install's units --
        # _flow_calibration_check divides measured litres by minutes. The
        # configured throughput is in the DISPLAY unit, so on an imperial
        # install the two are gal/min against L/min and the ratio would be out
        # by 3.785 in the direction that under-reserves.
        configured = configured * const.GALLON_TO_LITER_FACTOR
    if configured <= 0 or observed_lpm <= 0:
        return planned
    lead = float(zone.get(const.ZONE_LEAD_TIME) or 0.0)
    watering = max(0.0, planned - lead)
    corrected = lead + watering * (configured / observed_lpm)
    ceiling = float(zone.get(const.ZONE_MAXIMUM_DURATION) or const.FLOW_SAFETY_TIMEOUT)
    return min(corrected, ceiling)


def hardware_window(seconds, unit) -> tuple[int, float]:
    """``(value_for_the_hardware, seconds_that_value_means)``.

    A valve that owns its own close is told a duration in ITS unit. That
    instruction is not always the duration that was priced, and everything that
    books the run (the optimistic credit, the run record, the backstop, the
    observed-watering suppression window) must use the second value, or the
    zone silently receives more water than its bucket ever sees.

    The first value is an ``int`` because it lands in a service-call duration
    field, where ``5.0`` is not ``5`` for a Z2M/Tuya payload.

    Minute-granularity hardware is rounded UP -- rather slightly too much water
    than too little -- so the window the valve really runs is longer than the
    duration priced. Seconds hardware is rounded to the NEAREST whole second,
    in either direction, so 263.4 s is told 263; the second return value reports
    whichever way it went. The seconds branch deliberately has no floor of one,
    unlike the minutes branch: a request of 0.5 s or less commands nothing --
    ``round(0.5)`` is 0 under banker's rounding, and the boundary flips at 0.51.
    That is the behaviour of the helpers this replaces and is kept on purpose.

    Non-positive input -- zero, ``None``, or a negative -- commands nothing and
    is clamped here to ``(0, 0.0)``, so callers need no guard of their own.

    The rounding is otherwise unchanged from the two helpers this replaces:
    ``self_closing._sc_convert``, still there as a thin delegation to this, and
    ``distributor._dist_convert``, now deleted -- the distributor takes both
    values from here. Only the second return value is new.

    The OpenSprinkler ``run_station`` path is deliberately NOT covered here; it
    has :func:`opensprinkler_window` beside this one instead. Its unit is a
    property of the user's own run_service script rather than of the zone, and
    its rule is a ceiling with a floor of one rather than a round-to-nearest, so
    routing it through here would turn 263.4 into 263 instead of 264 and drop
    that floor.
    """
    seconds = float(seconds or 0)
    if seconds <= 0:
        return 0, 0.0
    if unit == const.DURATION_UNIT_MINUTES:
        minutes = max(1, math.ceil(seconds / 60.0))
        return minutes, float(minutes * 60)
    whole = int(round(seconds))
    return whole, float(whole)


def opensprinkler_window(seconds) -> int:
    """Whole seconds an OpenSprinkler station is told to run -- and really runs.

    A station's instruction is already in seconds, so the value sent and the
    seconds it means are one number; there is no second return value to give.

    The rule is NOT the one in :func:`hardware_window` and cannot be folded
    into it. ``run_station`` takes whole seconds and has no unit conversion at
    all, so there is nothing to branch on, and the rounding is a ceiling with a
    floor of one rather than a round-to-nearest: 263.4 s is told 264 here and
    would be told 263 there.

    Root: the rule was spelled out twice -- once where the station run is
    dispatched, once where its window is booked -- so the duration a station
    was given and the window the model reserved for it were two independent
    copies of one decision, free to drift at the next edit. Naming it once is
    what lets the finish anchor reserve exactly what the run books.

    Non-positive input commands nothing and returns 0, matching the guard the
    run path applies before it ever reaches a dispatch.

    NOT-TO-DO: do not "unify" this with :func:`hardware_window` on the grounds
    that both round a duration for hardware. They disagree by design at every
    fractional second, and at the step from zero to one.
    """
    seconds = float(seconds or 0)
    if seconds <= 0:
        return 0
    return max(1, math.ceil(seconds))
