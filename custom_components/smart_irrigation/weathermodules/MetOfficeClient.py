"""Client to talk to the Met Office Weather DataHub site-specific API.

Uses the deterministic "Global Spot" site-specific point forecast (GeoJSON):

* hourly endpoint (T to T+48) → current conditions (:meth:`get_data`)
* three-hourly endpoint (T to T+168) → 7-day daily forecast
  (:meth:`get_forecast_data`)

The free "Global Spot" plan allows up to 360 calls/day, which is comfortably
more than this integration needs (one hourly + one three-hourly fetch per
refresh, cached for at least a minute). Requires a Weather DataHub API key,
passed in the ``apikey`` request header.

Notable Met Office quirks handled here:

* Pressure (``mslp``) is mean-sea-level pressure in **Pa** — converted to hPa
  and then to absolute (station) pressure at the configured elevation, matching
  the other clients.
* Wind (``windSpeed10m``) is the 10 m wind — corrected to the 2 m height the ET
  calculation expects (FAO-56).
* There is **no dew point in the three-hourly product** and **no solar
  radiation in any product**. Forecast dew point is derived from temperature and
  relative humidity (Magnus formula); solar radiation is left unset so PyETO
  estimates it from temperature, exactly as it already does for OWM and Pirate
  Weather.
"""  # pylint: disable=invalid-name

import datetime
import json
import logging
import math

import requests

from ..const import (
    MAPPING_CURRENT_PRECIPITATION,
    MAPPING_DEWPOINT,
    MAPPING_HUMIDITY,
    MAPPING_MAX_TEMP,
    MAPPING_MIN_TEMP,
    MAPPING_PRECIPITATION,
    MAPPING_PRESSURE,
    MAPPING_TEMPERATURE,
    MAPPING_WINDSPEED,
    OBSERVATION_TIME,
)

_LOGGER = logging.getLogger(__name__)

# Shared session so repeated calls reuse the TCP connection and don't re-resolve
# the API hostname on every request.
_SESSION = requests.Session()

# Floor for how long a fetched result is reused, even when the caller's configured
# cache window is shorter (e.g. auto-update disabled → 0s). Repeated weather
# lookups — skip-condition checks, the dashboard outlook — would otherwise each
# hit the network (and a DNS lookup); this caps them to at most one call per
# endpoint per minute, which also keeps us well under the free-tier daily quota.
_MIN_CACHE_SECONDS = 60

_BASE_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point"
_HOURLY_URL = (
    _BASE_URL + "/hourly?excludeParameterMetadata=true"
    "&includeLocationName=false&latitude={lat}&longitude={lon}"
)
_THREE_HOURLY_URL = (
    _BASE_URL + "/three-hourly?excludeParameterMetadata=true"
    "&includeLocationName=false&latitude={lat}&longitude={lon}"
)

# Met Office reports wind at 10 m; ET calculations need 2 m height (FAO-56).
_WIND_10M_TO_2M = 4.87 / math.log((67.8 * 10) - 5.42)


def _compute_dew_point(temp_c: float, humidity: float) -> float:
    """Magnus formula: dew point (°C) from temperature (°C) and relative humidity (%)."""
    a, b = 17.625, 243.04
    gamma = math.log(max(humidity, 0.01) / 100.0) + (a * temp_c) / (b + temp_c)
    return (b * gamma) / (a - gamma)


class MetOfficeClient:  # pylint: disable=invalid-name
    """Met Office Weather DataHub (Global Spot) client."""

    def __init__(
        self,
        api_key,
        api_version=None,  # ignored — kept for a consistent client signature
        latitude=None,
        longitude=None,
        elevation=0,
        cache_seconds=0,
        override_cache=False,
    ) -> None:
        """Init."""
        self.api_key = (api_key or "").strip().replace(" ", "")
        self.api_version = "v0"
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation or 0
        self.cache_seconds = cache_seconds
        self.override_cache = override_cache
        self._hourly_url = _HOURLY_URL.format(lat=latitude, lon=longitude)
        self._three_hourly_url = _THREE_HOURLY_URL.format(lat=latitude, lon=longitude)
        self._cached_hourly = None
        self._cached_hourly_at = None
        self._cached_three_hourly = None
        self._cached_three_hourly_at = None

    # ------------------------------------------------------------------ helpers

    def _is_fresh(self, fetched_at) -> bool:
        """Whether a result fetched at ``fetched_at`` may still be served cached."""
        if fetched_at is None or self.override_cache:
            return False
        ttl = max(self.cache_seconds, _MIN_CACHE_SECONDS)
        return datetime.datetime.now() < fetched_at + datetime.timedelta(seconds=ttl)

    def _request(self, url):
        """GET ``url`` with the API key header and return the parsed JSON document."""
        req = _SESSION.get(
            url,
            headers={"apikey": self.api_key, "accept": "application/json"},
            timeout=60,
        )
        req.raise_for_status()
        return json.loads(req.text)

    @staticmethod
    def _time_series(doc):
        """Extract the ``properties.timeSeries`` list from a Global Spot document."""
        features = doc.get("features") or []
        if not features:
            return []
        return features[0].get("properties", {}).get("timeSeries", []) or []

    def _wind_2m(self, wind_10m):
        return wind_10m * _WIND_10M_TO_2M

    def _abs_pressure_from_pa(self, mslp_pa):
        """Convert MSL pressure in Pa to station (absolute) pressure in hPa."""
        pressure_hpa = mslp_pa / 100.0
        g, M, R, T0 = 9.80665, 0.0289644, 8.31447, 288.15
        temp = T0 - (g * M * self.elevation) / (R * T0)
        return pressure_hpa * (T0 / temp) ** (g * M / (R * 287))

    @staticmethod
    def _parse_time(tstr):
        """Parse a Met Office ISO-8601 timestamp (``...Z``) to an aware UTC datetime."""
        return datetime.datetime.fromisoformat(tstr.replace("Z", "+00:00"))

    # ------------------------------------------------------------------ key test

    def validate_key(self):
        """Test the API key by requesting the hourly endpoint.

        Raises OSError on 401/403 (invalid / unauthorized key), and a generic
        Exception on other non-200 statuses.
        """
        req = _SESSION.get(
            self._hourly_url,
            headers={"apikey": self.api_key, "accept": "application/json"},
            timeout=30,
        )
        if req.status_code in (401, 403):
            raise OSError(
                f"Met Office API key is invalid or unauthorized (HTTP {req.status_code})"
            )
        if req.status_code != 200:
            raise Exception(f"Met Office validation failed with HTTP {req.status_code}")

    # --------------------------------------------------------------- public API

    def _fetch_hourly(self):
        if self._is_fresh(self._cached_hourly_at):
            return self._cached_hourly
        doc = self._request(self._hourly_url)
        self._cached_hourly = doc
        self._cached_hourly_at = datetime.datetime.now()
        return doc

    def _fetch_three_hourly(self):
        if self._is_fresh(self._cached_three_hourly_at):
            return self._cached_three_hourly
        doc = self._request(self._three_hourly_url)
        self._cached_three_hourly = doc
        self._cached_three_hourly_at = datetime.datetime.now()
        return doc

    def get_data(self):
        """Return current conditions mapped to MAPPING_* constants."""
        try:
            steps = self._time_series(self._fetch_hourly())
            if not steps:
                _LOGGER.warning("Met Office get_data: empty time series")
                return None

            now = datetime.datetime.now(datetime.timezone.utc)
            # Pick the most recent step at or before now; fall back to the first.
            chosen = steps[0]
            for step in steps:
                ts = step.get("time")
                if ts and self._parse_time(ts) <= now:
                    chosen = step
                else:
                    break

            temperature = chosen.get("screenTemperature")
            humidity = chosen.get("screenRelativeHumidity")
            dewpoint = chosen.get("screenDewPointTemperature")
            wind_speed = chosen.get("windSpeed10m")
            mslp = chosen.get("mslp")
            precipitation = chosen.get("totalPrecipAmount") or 0.0

            if None in (temperature, humidity, dewpoint, wind_speed, mslp):
                _LOGGER.warning(
                    "Met Office get_data: missing required value in step %s", chosen
                )
                return None

            obs_time = chosen.get("time")
            parsed = {
                MAPPING_TEMPERATURE: temperature,
                MAPPING_HUMIDITY: humidity,
                MAPPING_DEWPOINT: dewpoint,
                MAPPING_WINDSPEED: self._wind_2m(wind_speed),
                MAPPING_PRESSURE: self._abs_pressure_from_pa(mslp),
                MAPPING_CURRENT_PRECIPITATION: precipitation,
                MAPPING_PRECIPITATION: precipitation,
                OBSERVATION_TIME: self._parse_time(obs_time) if obs_time else None,
            }
            _LOGGER.debug("Met Office get_data: %s", parsed)
            return parsed

        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            ValueError,
        ) as ex:
            _LOGGER.error("Met Office get_data error: %s", ex)
            return None

    def get_forecast_data(self):
        """Return a daily forecast (one dict per day) from the three-hourly product.

        The three-hourly product has no dew point and no solar radiation, so dew
        point is derived from the day's mean temperature and humidity (Magnus)
        and solar radiation is left for PyETO to estimate from temperature. Today
        is skipped (its delta is already covered by the accumulated current data),
        matching the other clients.
        """
        try:
            steps = self._time_series(self._fetch_three_hourly())
            if not steps:
                return None

            today = datetime.datetime.now(datetime.timezone.utc).date()
            # Group 3-hourly steps by their UTC calendar date.
            by_day: dict[datetime.date, list[dict]] = {}
            for step in steps:
                ts = step.get("time")
                if not ts:
                    continue
                day = self._parse_time(ts).date()
                by_day.setdefault(day, []).append(step)

            result = []
            for day in sorted(by_day):
                if day <= today:
                    continue
                day_steps = by_day[day]

                max_temps = [
                    s["maxScreenAirTemp"]
                    for s in day_steps
                    if s.get("maxScreenAirTemp") is not None
                ]
                min_temps = [
                    s["minScreenAirTemp"]
                    for s in day_steps
                    if s.get("minScreenAirTemp") is not None
                ]
                winds = [
                    s["windSpeed10m"]
                    for s in day_steps
                    if s.get("windSpeed10m") is not None
                ]
                pressures = [s["mslp"] for s in day_steps if s.get("mslp") is not None]
                humidities = [
                    s["screenRelativeHumidity"]
                    for s in day_steps
                    if s.get("screenRelativeHumidity") is not None
                ]

                if not (max_temps and min_temps and winds):
                    continue

                max_temp = max(max_temps)
                min_temp = min(min_temps)
                mean_temp = (max_temp + min_temp) / 2.0
                mean_wind = sum(winds) / len(winds)
                precip = sum(s.get("totalPrecipAmount") or 0.0 for s in day_steps)

                day_data = {
                    MAPPING_TEMPERATURE: mean_temp,
                    MAPPING_MAX_TEMP: max_temp,
                    MAPPING_MIN_TEMP: min_temp,
                    MAPPING_WINDSPEED: self._wind_2m(mean_wind),
                    MAPPING_PRECIPITATION: precip,
                }
                if humidities:
                    mean_humidity = sum(humidities) / len(humidities)
                    day_data[MAPPING_HUMIDITY] = mean_humidity
                    day_data[MAPPING_DEWPOINT] = _compute_dew_point(
                        mean_temp, mean_humidity
                    )
                if pressures:
                    day_data[MAPPING_PRESSURE] = self._abs_pressure_from_pa(
                        sum(pressures) / len(pressures)
                    )
                result.append(day_data)

            _LOGGER.debug("Met Office get_forecast_data: %s", result)
            return result

        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            ValueError,
        ) as ex:
            _LOGGER.error("Met Office get_forecast_data error: %s", ex)
            return None
