"""Intra-day ET accumulation for the read-only "live status" estimate.

Builds on :mod:`et_hourly`. Two ways to estimate how much reference ET has
occurred *so far today* (since the last daily calculation):

* **rigorous** — sum the hourly FAO-56 ETo over the elapsed hours, when hourly
  weather incl. solar radiation is available (Open-Meteo, partly Pirate);
* **proxy** — distribute an estimated *daily* ETo across the elapsed hours
  weighted by the hourly extraterrestrial radiation Ra (the clean physical
  "potential solar energy this hour"), for providers without hourly radiation.

The result feeds ``live_deficit`` = bucket − ET_so_far + precip_so_far, mirroring
the daily bucket update (``bucket += −ET + precip``) but with *measured* hourly
ET rather than a daily rate scaled by elapsed time. This is display-only; the
stored bucket and the daily calculation are untouched.
"""

import math

from .calcmodules.pyeto.pyeto import (
    et_rad,
    hargreaves,
    inv_rel_dist_earth_sun,
    sol_dec,
    sunset_hour_angle,
)
from .et_hourly import eto_hourly, extraterrestrial_radiation_hourly


def estimate_daily_et0_hargreaves(
    tmin_c: float, tmax_c: float, latitude_deg: float, doy: int
) -> float:
    """Rough daily reference ETo [mm/day] from temperature extremes only.

    Hargreaves equation (needs just tmin/tmax + extraterrestrial radiation), used
    to seed the proxy intra-day distribution for providers without hourly solar
    radiation. Less accurate than Penman-Monteith but universally computable.
    """
    lat = math.radians(latitude_deg)
    sd = sol_dec(doy)
    sha = sunset_hour_angle(lat, sd)
    ird = inv_rel_dist_earth_sun(doy)
    ra = et_rad(lat, sd, sha, ird)
    tmean = (tmin_c + tmax_c) / 2
    return max(0.0, hargreaves(tmin_c, tmax_c, tmean, ra))


def proxy_et_since(
    daily_et0: float,
    latitude_deg: float,
    longitude_deg: float,
    doy: int,
    tz_offset_h: float,
    elapsed_hours: list[float],
) -> float:
    """Estimate ET accumulated over ``elapsed_hours`` from a daily ETo total.

    Distributes ``daily_et0`` (mm/day) across the day weighted by each hour's
    extraterrestrial radiation Ra; returns the share for the elapsed hours.
    """
    if daily_et0 <= 0 or not elapsed_hours:
        return 0.0

    def ra(h: float) -> float:
        return extraterrestrial_radiation_hourly(
            latitude_deg, longitude_deg, doy, h, tz_offset_h
        )

    all_day = sum(ra(h + 0.5) for h in range(24))
    if all_day <= 0:
        return 0.0
    elapsed = sum(ra(h) for h in elapsed_hours)
    return daily_et0 * (elapsed / all_day)


def eto_hourly_series(
    rows: list[dict],
    latitude_deg: float,
    longitude_deg: float,
    tz_offset_h: float,
    elevation_m: float = 0.0,
) -> list[float]:
    """Per-row FAO-56 hourly ETo [mm], one entry per row, in row order.

    Each row needs: ``hour`` (local clock midpoint), ``doy``, ``temperature``,
    ``humidity``, ``wind_2m`` and ``solar_mj_h``. Two optional keys:

    * ``pressure_kpa`` — a measured barometer, used in place of the
      elevation-derived standard atmosphere. The psychrometric constant is
      linear in it, so a station 3 kPa off standard shifts ETo by ~1%.
    * ``coverage_h`` — the fraction of the hour the row actually covers,
      defaulting to a whole hour. The partial hours at the ends of a
      calculation window are charged their real share this way rather than a
      full hour of ET.
    * ``tz_offset_h`` — this row's OWN UTC offset, overriding the argument. A
      window can span up to seven days and therefore a DST transition, after
      which one offset for the whole window puts the rows on the far side of it
      an hour out in solar time. ``build_hourly_rows`` sets it when it is given
      a timezone; rows from elsewhere (the live estimate's Open-Meteo series)
      carry no such key and keep the argument.
    """
    out = []
    for r in rows:
        eto = eto_hourly(
            t_c=r["temperature"],
            rh_pct=r["humidity"],
            wind_2m=r["wind_2m"],
            solar_rad_hr=r["solar_mj_h"],
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            doy=r["doy"],
            hour_mid=r["hour"],
            tz_offset_h=r.get("tz_offset_h", tz_offset_h),
            elevation_m=elevation_m,
            pressure_kpa=r.get("pressure_kpa"),
        )
        out.append(eto * r.get("coverage_h", 1.0))
    return out


def rigorous_et_since(
    rows: list[dict],
    latitude_deg: float,
    longitude_deg: float,
    tz_offset_h: float,
    elevation_m: float = 0.0,
) -> float:
    """Sum hourly FAO-56 ETo over ``rows`` (each one elapsed hour)."""
    return sum(
        eto_hourly_series(rows, latitude_deg, longitude_deg, tz_offset_h, elevation_m)
    )


def drained_over_window(
    surplus: float,
    drainage_rate: float,
    elapsed_hours: float,
    maximum_bucket: float | None = None,
) -> float:
    """Water [mm] drained from a surplus above field capacity over a window.

    Drainage only acts on water above field capacity (``surplus > 0``) and is
    integrated analytically over the whole window, so it's exact regardless of
    window length and never reports more than the available surplus:

    * with a maximum bucket, the rate follows Brooks-Corey relative conductivity
      ``dW/dt = -rate * (W/Wmax)^n`` (``n = (2+3*gamma)/gamma``, ``gamma = 2`` ->
      ``n = 4``), whose closed form is
      ``W(t) = W0 * (1 + (n-1)*rate*t*W0^(n-1)/Wmax^n)^(-1/(n-1))``;
    * without one, it's a constant rate clamped at the available surplus.

    Replaces the previous single explicit-Euler step (rate sampled once at the
    end-of-window surplus, then charged for the whole window), which
    systematically over-drained because the real rate falls as the surplus
    drains. Shared by the daily calculation and the intraday live estimate.
    """
    if surplus <= 0 or drainage_rate <= 0 or elapsed_hours <= 0:
        return 0.0
    if maximum_bucket is not None and maximum_bucket > 0:
        gamma = 2
        n = (2 + 3 * gamma) / gamma
        denom = 1 + (n - 1) * drainage_rate * elapsed_hours * (surplus ** (n - 1)) / (
            maximum_bucket**n
        )
        w_end = surplus / (denom ** (1 / (n - 1)))
    else:
        w_end = max(0.0, surplus - drainage_rate * elapsed_hours)
    return surplus - w_end


def replay_water_balance(
    bucket: float,
    et_total: float,
    steps,
    drainage_rate: float,
    maximum_bucket: float | None,
    drain_maximum: float | None = None,
) -> tuple[float, float, float]:
    """Step the window's water balance instead of lumping it into one update.

    ``et_total`` is the window's whole ET contribution (negative, already scaled
    by the crop coefficient and the window length) and ``steps`` are
    ``WaterStep``s whose ``et_weight`` sums to 1, so the same total ET is charged
    either way — only its interleaving with rain and drainage changes. Each step
    runs **ET share, then drainage, then rain, then the clamp**, which is the
    order the single-shot form applies over the whole window at once.

    Exact rather than approximate at any step length: ``drained_over_window`` is
    the closed-form solution of the drainage ODE, so cutting the window at
    irregular event times costs nothing in accuracy.

    ``drain_maximum`` is the field capacity Brooks-Corey scales against, which is
    ``maximum_bucket`` except when that is 0 — a bucket still clamps at 0 but has
    no capacity to scale by, so drainage falls back to a constant rate.

    Returns ``(bucket, drainage_total, runoff_total)``. The three conserve water
    against the inputs: ``bucket + et_total + rain - drainage - runoff``.
    """
    value = float(bucket)
    # The stored bucket is always the output of a previous clamp, so this is a
    # no-op in practice; it keeps the invariant if one was set externally. Not
    # counted as runoff — it is not this window's water.
    if maximum_bucket is not None and value > maximum_bucket:
        value = float(maximum_bucket)

    drainage_total = 0.0
    runoff_total = 0.0
    for step in steps:
        value += et_total * step.et_weight
        drained = drained_over_window(
            value, drainage_rate, step.dt_hours, drain_maximum
        )
        value -= drained
        drainage_total += drained
        value += step.precip_mm
        if maximum_bucket is not None and value > maximum_bucket:
            runoff_total += value - float(maximum_bucket)
            value = float(maximum_bucket)
    return value, drainage_total, runoff_total


def live_deficit(
    bucket: float,
    et_since: float,
    precip_since: float,
    maximum_bucket: float | None = None,
    drainage_rate: float = 0.0,
    elapsed_hours: float = 0.0,
) -> float:
    """Estimated current bucket = bucket − ET_so_far + precip_so_far (clamped).

    Mirrors the daily bucket update: cap any surplus at field capacity
    (``maximum_bucket``), then drain the remaining surplus over the elapsed
    window via :func:`drained_over_window`. With ``drainage_rate`` /
    ``elapsed_hours`` left at 0 (the default) drainage is skipped, so callers
    that only want the raw deficit are unaffected. The daily calculation
    remains the source of truth for the stored bucket.
    """
    value = bucket - et_since + precip_since
    if maximum_bucket is not None and value > maximum_bucket:
        value = float(maximum_bucket)
    if value > 0:
        value -= drained_over_window(
            value, drainage_rate, elapsed_hours, maximum_bucket
        )
    return value
