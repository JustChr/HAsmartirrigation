"""Day-level inputs for a window that is only part-way through.

The daily FAO-56 equation takes whole-window quantities, so it cannot be
evaluated half-way through a window as it stands: at mid-morning the temperature
extremes are the morning's, and on a zone that estimates solar radiation from
them ``sol_rad_from_t`` is proportional to ``sqrt(Tmax - Tmin)``, so the
shortfall is charged twice over.

The construction is the composed window. The hours already observed stand as they
are; the hours still to come are filled in, and the extremes are read off the
composition. The observation overtakes the filled-in part hour by hour, so the
inputs converge on exactly what the commit will see once the window closes --
with no blend rule and no gate times, and no residual left standing at the moment
of commit the way a decaying weight or a plain envelope leaves one.

Two sources for the remainder, in a fixed order:

* **the configured weather service's own hourly temperatures** (:func:`forecast_remainder`).
  Measured over a year of windows, this lands the range within 0.9 C MAE through
  the morning at a small-hours anchor and 1.3 C at a late-evening one, against
  7.9 C for reading the extremes off the observation alone.
* **the site's solar geometry, scaled by the amplitude of the windows already
  committed** (:func:`diurnal_remainder`), for an install with no service.
  2.5 C and 2.7 C on the same two anchors. Weaker, and it says so through the
  tier it publishes.

The shape is deliberately canonical rather than fitted to today. Fitting the
amplitude to the observed part was measured and rejected: at a late-evening
anchor the observed part is all night, the amplitude comes out of a division by
nearly nothing, and the p95 error goes ABOVE reading the extremes off the
observation alone. Nothing about today's amplitude is inferred from a partial
day; only its shape is, and that comes from geometry.
"""

import datetime
import functools
import math

from .et_hourly import solar_elevation_sin

# Which source filled in the unobserved hours. Published as an entity attribute
# rather than a localized string, for the same reason the balance form is: a
# user cannot act on it, but an operator diagnosing a gap and a live check both
# need it, and it carries no obligation to translate.
TIER_SERVICE = "service"
# A Home Assistant weather entity's hourly forecast composes directly and is the
# next tier down. It needs an entity to be configured and is not built here; when
# it lands it takes the name "entity", which is reserved by this comment rather
# than by an unused constant.
TIER_SELF_CONTAINED = "self_contained"
# Nothing was projected: the extremes are the observed ones. Either the window
# has closed, in which case this is the exact answer, or no source could fill it.
TIER_OBSERVED = "observed"

# Thermal lag from solar noon to the day's warmest moment. The air lags the
# radiation; the same 2.5 h places the peak where the phase gate of the
# construction this replaces placed it, so the two agree on when the day turns.
_PEAK_LAG_H = 2.5
# Decay constant of the falling limb, in units of the night's length. 2.2 gives
# the concave evening cooling that a clear night actually follows; the curve is
# renormalised so it reaches exactly 0 at the next sunrise rather than the 0.11
# the bare exponential would leave, which would put a floor under every
# projected low.
_NIGHT_B = 2.2
_NIGHT_FLOOR = math.exp(-_NIGHT_B)

# Resolution of the sunrise/peak scan. Five minutes is finer than the hourly
# grid the remainder is evaluated on, so the marks are never the limiting error.
_SCAN_STEPS = 24 * 12

# Longest remainder that will be built. A window is a day; anything past this is
# a zone whose watermark has not moved in a long time, where projecting is
# meaningless and the hour walk should not run away.
_MAX_REMAINDER_HOURS = 48

# Longest step a forecast series may take and still be trusted to place a
# window's extremes. Admits a three-hourly product (OpenWeatherMap's free
# forecast); refuses a daily one, whose extremes are attached to a calendar day
# rather than to the window and do not converge on it.
_MAX_FORECAST_GAP_H = 3.5


@functools.lru_cache(maxsize=64)
def _marks(latitude, longitude, doy, tz_offset_h):
    """``(sunrise, peak)`` as local clock hours, or ``(None, None)`` in polar day/night.

    Cached because this runs every minute per zone and the answer only changes
    with the date. Keyed on the rounded site so a coordinate that jitters in the
    last decimal cannot evict the whole table.
    """
    grid = [i * 24.0 / _SCAN_STEPS for i in range(_SCAN_STEPS + 1)]
    elevations = [
        solar_elevation_sin(latitude, longitude, doy, h, tz_offset_h) for h in grid
    ]
    noon = grid[max(range(len(grid)), key=elevations.__getitem__)]
    sunrise = None
    for i in range(1, len(grid)):
        if elevations[i - 1] <= 0 < elevations[i]:
            sunrise = grid[i]
            break
    if sunrise is None:
        # The sun never crosses the horizon on this date: no trough and no peak
        # to hang a shape on. The caller falls back to the observation.
        return None, None
    return sunrise, noon + _PEAK_LAG_H


def _offset(geometry, when):
    """This instant's UTC offset, preferring the site's own timezone.

    A window reaches a day and can straddle a DST transition, where one offset
    for the whole of it puts every hour past the transition an hour out in solar
    time -- which moves the trough and the peak with it.
    """
    tz = getattr(geometry, "tz", None)
    if tz is not None:
        resolved = tz.utcoffset(when)
        if resolved is not None:
            return resolved.total_seconds() / 3600.0
    return geometry.tz_offset_h


def solar_marks(geometry, day):
    """``(sunrise, peak)`` as local clock hours for ``day`` at this site."""
    when = datetime.datetime.combine(day, datetime.time(12))
    return _marks(
        round(geometry.latitude, 4),
        round(geometry.longitude, 4),
        day.timetuple().tm_yday,
        _offset(geometry, when),
    )


def diurnal_fraction(when, geometry):
    """Where ``when`` sits on the canonical day, 0 at the trough and 1 at the peak.

    Sine on the rising limb and a renormalised exponential on the falling one, so
    the curve is continuous at the peak and returns to exactly 0 at the following
    sunrise. Hours before today's sunrise are still on YESTERDAY's falling limb,
    which is what makes the small hours of a night-anchored window come out
    ordered rather than restarting at midnight.
    """
    day = when.date()
    hour = when.hour + when.minute / 60.0 + when.second / 3600.0
    sunrise, peak = solar_marks(geometry, day)
    if sunrise is None:
        return 0.0
    if hour <= peak and hour >= sunrise:
        span = peak - sunrise
        if span <= 0:
            return 0.0
        return math.sin(math.pi / 2 * (hour - sunrise) / span)
    if hour < sunrise:
        previous = day - datetime.timedelta(days=1)
        _prev_sunrise, prev_peak = solar_marks(geometry, previous)
        if prev_peak is None:
            return 0.0
        start, finish = prev_peak - 24.0, sunrise
    else:
        following = day + datetime.timedelta(days=1)
        next_sunrise, _next_peak = solar_marks(geometry, following)
        if next_sunrise is None:
            return 0.0
        start, finish = peak, next_sunrise + 24.0
    span = finish - start
    if span <= 0:
        return 0.0
    u = min(max((hour - start) / span, 0.0), 1.0)
    return (math.exp(-_NIGHT_B * u) - _NIGHT_FLOOR) / (1 - _NIGHT_FLOOR)


def remainder_hours(now, window_end):
    """The whole hours between ``now`` and the window's close, ``now`` excluded.

    Empty once the window has closed, which is what makes the composition
    collapse to the observation and the estimate land on the commit exactly.
    """
    if window_end <= now:
        return []
    first = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    out = []
    while first <= window_end and len(out) < _MAX_REMAINDER_HOURS:
        out.append(first)
        first += datetime.timedelta(hours=1)
    return out


def compose_extremes(observed_min, observed_max, remainder):
    """The window's extremes read off observed-so-far plus the projected hours."""
    if not remainder:
        return observed_min, observed_max
    return min(observed_min, *remainder), max(observed_max, *remainder)


def forecast_remainder(series, now, window_end):
    """The forecast's own temperatures over the window's remaining span, or None.

    ``series`` is ``[(naive local datetime, temperature C)]``, ascending. The
    extremes are read off the samples themselves rather than off an hourly grid,
    so a three-hourly product composes as readily as an hourly one and nothing
    has to be interpolated into existence.

    Refused whenever the series leaves a hole in the remaining span, including
    one at either end. A partial remainder would read the extremes off a window
    with a gap in it and present that as what the commit will see, which is worse
    than declining to a tier that at least covers the whole of it. The same guard
    is what refuses a DAILY forecast: substituting tomorrow's daily low for a
    window's post-midnight tail was measured and does not converge, because that
    low usually falls after the window closes, so the construction imports an
    extreme the commit never sees and never lets go of it.
    """
    if not series:
        return None
    hours = remainder_hours(now, window_end)
    if not hours:
        return []
    samples = sorted(
        (when, float(temp))
        for when, temp in series
        if when is not None and temp is not None
    )
    if not samples:
        return None
    # The series has to BRACKET the remaining span, not merely approach it. A
    # forecast that stops short leaves the window's last hours unprojected, and
    # for a night-anchored window those are exactly where its low lives. A real
    # product runs days ahead, so this only ever refuses a genuinely truncated
    # one.
    if samples[-1][0] < window_end:
        return None
    gap = datetime.timedelta(hours=_MAX_FORECAST_GAP_H)
    covered = now
    out = []
    for when, temp in samples:
        if when <= now:
            continue
        if when - covered > gap:
            return None
        covered = when
        if when > window_end:
            break
        out.append(temp)
    return out or None


def diurnal_remainder(now, latest_temperature, amplitude, geometry, window_end):
    """The remaining hours from the canonical shape, or None without an amplitude.

    Held so the curve passes through the reading the sensor is producing right
    now, and scaled by ``amplitude`` -- the mean ``Tmax - Tmin`` of the windows
    already committed for this sensor group. Re-anchoring on the current reading
    every refresh is what makes this improve as the day goes on rather than
    freezing a projection made hours ago.
    """
    if not amplitude or amplitude <= 0 or latest_temperature is None:
        return None
    hours = remainder_hours(now, window_end)
    if not hours:
        return []
    here = diurnal_fraction(now, geometry)
    return [
        latest_temperature + amplitude * (diurnal_fraction(hour, geometry) - here)
        for hour in hours
    ]
