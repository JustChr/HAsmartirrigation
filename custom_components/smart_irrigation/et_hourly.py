"""Hourly reference evapotranspiration (ETo) — FAO-56 Penman-Monteith Eq. 53.

The vendored PyETO module implements the *daily* FAO-56 equation (numerator
coefficient 900, denominator 0.34, daily Stefan-Boltzmann constant 4.903e-9,
soil heat flux G ~ 0). Running that on hourly data is physically wrong, so this
module implements the dedicated hourly form (Allen et al. 1998, Eq. 53):

    ETo = [0.408 Δ (Rn − G) + γ (37/(T+273)) u2 (e°(T) − ea)]
          / [Δ + γ (1 + 0.34 u2)]

with the hourly adjustments:
  * numerator wind coefficient 37 (vs 900 daily),
  * soil heat flux G = 0.1·Rn daytime (Rn > 0), 0.5·Rn nighttime,
  * net long-wave radiation using the **hourly** Stefan-Boltzmann constant
    (2.043e-10 MJ K⁻⁴ m⁻² h⁻¹) and the hourly mean temperature,
  * saturation/actual vapour pressure from the hourly mean temperature & RH,
  * extraterrestrial radiation integrated over the hour via the solar time
    angles ω1, ω2 (Eq. 28 with Eq. 29/31/32/33).

This is a standalone, dependency-free helper (math only). It deliberately does
NOT modify the vendored PyETO. It is used by the read-only intra-day "live
status" estimate; the stored bucket and daily calculation are unchanged.
"""

import math

# Solar constant [MJ m-2 min-1].
SOLAR_CONSTANT = 0.0820
# Stefan-Boltzmann constant for an HOURLY time step [MJ K-4 m-2 h-1].
# (The daily value used by PyETO is 4.903e-9 MJ K-4 m-2 day-1.)
STEFAN_BOLTZMANN_HOURLY = 2.043e-10
# Canopy reflection coefficient for the grass reference surface.
ALBEDO = 0.23
# Hourly numerator wind coefficient for the short (grass) reference (Eq. 53).
CN_HOURLY = 37.0


def svp_from_t(t_c: float) -> float:
    """Saturation vapour pressure e°(T) [kPa] from air temperature [°C]."""
    return 0.6108 * math.exp((17.27 * t_c) / (t_c + 237.3))


def delta_svp(t_c: float) -> float:
    """Slope of the saturation vapour pressure curve Δ [kPa °C-1]."""
    return (4098 * svp_from_t(t_c)) / math.pow(t_c + 237.3, 2)


def psy_const(pressure_kpa: float) -> float:
    """Psychrometric constant γ [kPa °C-1] from atmospheric pressure [kPa]."""
    return 0.000665 * pressure_kpa


def atm_pressure(elevation_m: float) -> float:
    """Atmospheric pressure [kPa] from elevation [m] (FAO-56 Eq. 7)."""
    return 101.3 * math.pow((293.0 - 0.0065 * elevation_m) / 293.0, 5.26)


def extraterrestrial_radiation_hourly(
    latitude_deg: float,
    longitude_deg: float,
    doy: int,
    hour_mid: float,
    tz_offset_h: float,
) -> float:
    """Extraterrestrial radiation Ra for a one-hour period [MJ m-2 h-1].

    FAO-56 Eq. 28 with the solar time-angle integration (Eq. 29, 31-33).

    ``longitude_deg`` / ``tz_offset_h`` use the usual east-positive convention
    (e.g. Vienna +16.23°, UTC+2); they are converted internally to FAO's
    west-of-Greenwich convention. ``hour_mid`` is the midpoint of the period in
    local standard clock time (e.g. 14:00-15:00 → 14.5).
    """
    lat = math.radians(latitude_deg)
    # Solar declination [rad] and inverse relative Earth-Sun distance.
    sol_dec = 0.409 * math.sin((2 * math.pi / 365) * doy - 1.39)
    dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * doy)
    # Seasonal correction for solar time [hour].
    b = (2 * math.pi * (doy - 81)) / 364
    sc = 0.1645 * math.sin(2 * b) - 0.1255 * math.cos(b) - 0.025 * math.sin(b)
    # Longitudes of the time-zone centre (Lz) and the site (Lm), degrees WEST.
    lz_west = -15.0 * tz_offset_h
    lm_west = -longitude_deg
    # Solar time angle at the midpoint of the period and the hour bounds.
    omega = (math.pi / 12) * ((hour_mid + 0.06667 * (lz_west - lm_west) + sc) - 12)
    omega1 = omega - math.pi / 24
    omega2 = omega + math.pi / 24
    ra = (
        ((12 * 60) / math.pi)
        * SOLAR_CONSTANT
        * dr
        * (
            (omega2 - omega1) * math.sin(lat) * math.sin(sol_dec)
            + math.cos(lat) * math.cos(sol_dec) * (math.sin(omega2) - math.sin(omega1))
        )
    )
    return max(0.0, ra)


def net_radiation_hourly(
    solar_rad_hr: float,
    ra_hr: float,
    t_c: float,
    ea_kpa: float,
    elevation_m: float,
) -> float:
    """Net radiation Rn [MJ m-2 h-1] from measured solar radiation [MJ m-2 h-1].

    Uses the hourly Stefan-Boltzmann constant and the hourly mean temperature
    for the net long-wave term (FAO-56 Eq. 38-40, hourly).
    """
    rns = (1 - ALBEDO) * solar_rad_hr
    rso = (0.75 + 2e-5 * elevation_m) * ra_hr
    # Cloudiness function fcd = 1.35 Rs/Rso − 0.35, bounded to [0.05, 1.0].
    # At night (Rso ≈ 0) the ratio is undefined; fall back to the lower bound,
    # which keeps the (small) night-time Rnl reasonable for a status estimate.
    if rso > 0:
        ratio = min(1.0, max(0.0, solar_rad_hr / rso))
        fcd = max(0.05, min(1.0, 1.35 * ratio - 0.35))
    else:
        fcd = 0.05
    t_k = t_c + 273.16
    rnl = (
        STEFAN_BOLTZMANN_HOURLY
        * math.pow(t_k, 4)
        * (0.34 - 0.14 * math.sqrt(max(0.0, ea_kpa)))
        * fcd
    )
    return rns - rnl


def penman_monteith_hourly(
    net_rad: float,
    soil_heat_flux: float,
    t_c: float,
    wind_2m: float,
    svp: float,
    avp: float,
    slope_svp: float,
    psy: float,
) -> float:
    """FAO-56 Eq. 53 hourly ETo [mm h-1] from already-computed components.

    Negative results (possible at night) are clamped to 0.
    """
    t_k = t_c + 273.0
    numerator = 0.408 * slope_svp * (net_rad - soil_heat_flux) + psy * (
        CN_HOURLY / t_k
    ) * wind_2m * (svp - avp)
    denominator = slope_svp + psy * (1 + 0.34 * wind_2m)
    return max(0.0, numerator / denominator)


def eto_hourly(
    *,
    t_c: float,
    rh_pct: float,
    wind_2m: float,
    solar_rad_hr: float,
    latitude_deg: float,
    longitude_deg: float,
    doy: int,
    hour_mid: float,
    tz_offset_h: float,
    elevation_m: float = 0.0,
    pressure_kpa: float | None = None,
) -> float:
    """Hourly reference ETo [mm h-1] (FAO-56 Eq. 53) from hourly weather.

    Requires hourly solar radiation (``solar_rad_hr`` [MJ m-2 h-1]); providers
    without it use the proxy path instead (handled by the caller).
    """
    if pressure_kpa is None:
        pressure_kpa = atm_pressure(elevation_m)
    svp = svp_from_t(t_c)
    avp = svp * max(0.0, min(100.0, rh_pct)) / 100.0
    slope = delta_svp(t_c)
    gamma = psy_const(pressure_kpa)
    ra = extraterrestrial_radiation_hourly(
        latitude_deg, longitude_deg, doy, hour_mid, tz_offset_h
    )
    rn = net_radiation_hourly(solar_rad_hr, ra, t_c, avp, elevation_m)
    # Soil heat flux: 0.1·Rn during daytime (Rn > 0), 0.5·Rn at night.
    g = 0.1 * rn if rn > 0 else 0.5 * rn
    return penman_monteith_hourly(rn, g, t_c, wind_2m, svp, avp, slope, gamma)
