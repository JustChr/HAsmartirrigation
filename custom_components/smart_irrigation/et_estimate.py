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


def rigorous_et_since(
    rows: list[dict],
    latitude_deg: float,
    longitude_deg: float,
    tz_offset_h: float,
    elevation_m: float = 0.0,
) -> float:
    """Sum hourly FAO-56 ETo over ``rows`` (each one elapsed hour).

    Each row needs: ``hour`` (local clock midpoint), ``doy``, ``temperature``,
    ``humidity``, ``wind_2m`` and ``solar_mj_h``.
    """
    total = 0.0
    for r in rows:
        total += eto_hourly(
            t_c=r["temperature"],
            rh_pct=r["humidity"],
            wind_2m=r["wind_2m"],
            solar_rad_hr=r["solar_mj_h"],
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            doy=r["doy"],
            hour_mid=r["hour"],
            tz_offset_h=tz_offset_h,
            elevation_m=elevation_m,
        )
    return total


def live_deficit(
    bucket: float,
    et_since: float,
    precip_since: float,
    maximum_bucket: float | None = None,
) -> float:
    """Estimated current bucket = bucket − ET_so_far + precip_so_far (clamped).

    Mirrors the daily bucket update's field-capacity cap. Drainage (which only
    reduces a surplus) is intentionally not modelled here — this is an estimate
    of the deficit, and the daily calculation remains the source of truth.
    """
    value = bucket - et_since + precip_since
    if maximum_bucket is not None and value > maximum_bucket:
        return float(maximum_bucket)
    return value
