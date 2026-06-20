"""Client to talk to Open Weather Map API."""  # pylint: disable=invalid-name

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
# lookups — skip-condition checks, the dashboard outlook, the intra-day estimate —
# would otherwise each hit the network (and a DNS lookup); this caps them to at
# most one call per method per minute.
_MIN_CACHE_SECONDS = 60

# OWM free-tier endpoints (2.5 — no paid subscription required)
OWM_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather?units=metric&lat={}&lon={}&appid={}"
OWM_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?units=metric&lat={}&lon={}&appid={}"

# OWM reports wind at 10 m; ET calculations need 2 m height
_WIND_HEIGHT_CORRECTION = 4.87 / math.log((67.8 * 10) - 5.42)


def _compute_dew_point(temp_c: float, humidity: float) -> float:
    """Magnus formula: dew point (°C) from temperature (°C) and relative humidity (%)."""
    a, b = 17.625, 243.04
    gamma = math.log(max(humidity, 0.01) / 100.0) + (a * temp_c) / (b + temp_c)
    return (b * gamma) / (a - gamma)


class OWMClient:  # pylint: disable=invalid-name
    """Open Weather Map Client using free-tier 2.5 endpoints."""

    def __init__(
        self,
        api_key,
        api_version=None,  # ignored — kept for backwards-compatibility
        latitude=None,
        longitude=None,
        elevation=0,
        cache_seconds=0,
        override_cache=False,
    ) -> None:
        """Init."""
        self.api_key = api_key.strip().replace(" ", "")
        self.api_version = "2.5"
        self.longitude = longitude
        self.latitude = latitude
        self.elevation = elevation
        self.cache_seconds = cache_seconds
        self.override_cache = override_cache
        self._cached_data = None
        self._cached_data_at = None
        self._cached_forecast_data = None
        self._cached_forecast_at = None

    def _is_fresh(self, fetched_at) -> bool:
        """Whether a result fetched at ``fetched_at`` may still be served cached."""
        if fetched_at is None or self.override_cache:
            return False
        ttl = max(self.cache_seconds, _MIN_CACHE_SECONDS)
        return datetime.datetime.now() < fetched_at + datetime.timedelta(seconds=ttl)

    def validate_key(self):
        """Test the API key using /data/2.5/weather (works on all OWM plans).

        Raises OSError on 401 (invalid key).
        """
        url = OWM_CURRENT_URL.format(self.latitude, self.longitude, self.api_key)
        req = _SESSION.get(url, timeout=30)
        if req.status_code == 401:
            raise OSError("OWM API key is invalid (HTTP 401)")
        if req.status_code not in (200, 403):
            raise OSError(f"OWM validation failed with HTTP {req.status_code}")

    def get_data(self):
        """Fetch and return current weather data from /data/2.5/weather."""
        if not self._is_fresh(self._cached_data_at):
            url = OWM_CURRENT_URL.format(self.latitude, self.longitude, self.api_key)
            try:
                req = _SESSION.get(url, timeout=60)
                doc = json.loads(req.text)
                _LOGGER.debug(
                    "OWMClient get_data called API %s and received %s", url, doc
                )

                if doc.get("cod") not in (200, "200"):
                    self.raiseHTTPError()

                main = doc.get("main", {})
                wind = doc.get("wind", {})
                rain = doc.get("rain", {})
                snow = doc.get("snow", {})

                temp = main["temp"]
                humidity = main["humidity"]
                pressure = self.relative_to_absolute_pressure(
                    main["pressure"], self.elevation
                )
                wind_speed = wind.get("speed", 0.0) * _WIND_HEIGHT_CORRECTION
                dew_point = _compute_dew_point(temp, humidity)
                current_precip = rain.get("1h", 0.0) + snow.get("1h", 0.0)

                _LOGGER.debug(
                    "OWMCLIENT actual precipitation (rain.1h + snow.1h): %s",
                    current_precip,
                )

                observation_dt = doc.get("dt")
                parsed_data = {
                    MAPPING_TEMPERATURE: temp,
                    MAPPING_HUMIDITY: humidity,
                    MAPPING_PRESSURE: pressure,
                    MAPPING_WINDSPEED: wind_speed,
                    MAPPING_DEWPOINT: dew_point,
                    MAPPING_CURRENT_PRECIPITATION: current_precip,
                    MAPPING_PRECIPITATION: current_precip,
                    OBSERVATION_TIME: (
                        datetime.datetime.fromtimestamp(
                            observation_dt, tz=datetime.timezone.utc
                        )
                        if observation_dt
                        else None
                    ),
                }
                self._cached_data = parsed_data
                self._cached_data_at = datetime.datetime.now()
                return parsed_data
            except Exception as ex:
                _LOGGER.warning(ex)
                raise
        else:
            _LOGGER.debug("Returning cached OWM data")
            return self._cached_data

    def get_forecast_data(self):
        """Fetch and return daily forecast data from /data/2.5/forecast.

        The 3-hourly entries are aggregated into calendar days.
        Today's partial data is excluded; up to 4 complete future days are returned.
        """
        if not self._is_fresh(self._cached_forecast_at):
            url = OWM_FORECAST_URL.format(self.latitude, self.longitude, self.api_key)
            try:
                req = _SESSION.get(url, timeout=60)
                doc = json.loads(req.text)
                _LOGGER.debug(
                    "OWMClient get_forecast_data called API %s and received %s",
                    url,
                    doc,
                )

                if doc.get("cod") not in (200, "200"):
                    self.raiseHTTPError()

                entries = doc.get("list", [])
                if not entries:
                    _LOGGER.warning(
                        "Ignoring OWM input: missing or empty 'list' in forecast response"
                    )
                    return None

                today = datetime.datetime.utcnow().date()
                daily_buckets: dict = {}
                for entry in entries:
                    day = datetime.datetime.utcfromtimestamp(entry["dt"]).date()
                    if day == today:
                        continue
                    daily_buckets.setdefault(day, []).append(entry)

                parsed_data_total = []
                for day in sorted(daily_buckets.keys()):
                    slots = daily_buckets[day]
                    mains = [s["main"] for s in slots]
                    temps = [m["temp"] for m in mains]
                    humidities = [m["humidity"] for m in mains]
                    pressures = [m["pressure"] for m in mains]
                    wind_speeds = [s.get("wind", {}).get("speed", 0.0) for s in slots]

                    avg_temp = sum(temps) / len(temps)
                    avg_humidity = sum(humidities) / len(humidities)
                    avg_pressure = sum(pressures) / len(pressures)
                    avg_wind = sum(wind_speeds) / len(wind_speeds)
                    min_temp = min(m.get("temp_min", m["temp"]) for m in mains)
                    max_temp = max(m.get("temp_max", m["temp"]) for m in mains)
                    rain = sum(s.get("rain", {}).get("3h", 0.0) for s in slots)
                    snow_mm = sum(s.get("snow", {}).get("3h", 0.0) for s in slots)

                    parsed_data_total.append(
                        {
                            MAPPING_TEMPERATURE: avg_temp,
                            MAPPING_MIN_TEMP: min_temp,
                            MAPPING_MAX_TEMP: max_temp,
                            MAPPING_HUMIDITY: avg_humidity,
                            MAPPING_PRESSURE: self.relative_to_absolute_pressure(
                                avg_pressure, self.elevation
                            ),
                            MAPPING_WINDSPEED: avg_wind * _WIND_HEIGHT_CORRECTION,
                            MAPPING_DEWPOINT: _compute_dew_point(
                                avg_temp, avg_humidity
                            ),
                            MAPPING_PRECIPITATION: rain + snow_mm,
                        }
                    )

                self._cached_forecast_data = parsed_data_total
                self._cached_forecast_at = datetime.datetime.now()
                return parsed_data_total
            except (requests.RequestException, json.JSONDecodeError) as ex:
                _LOGGER.error("Error reading from OWM forecast: %s", ex)
            else:
                return None
        else:
            _LOGGER.debug("Returning cached OWM forecastdata")
            return self._cached_forecast_data

    def relative_to_absolute_pressure(self, pressure, height):
        """Convert sea-level pressure (hPa) to station pressure at the given elevation (m)."""
        g = 9.80665
        M = 0.0289644
        R = 8.31447
        T0 = 288.15
        temperature = T0 - (g * M * height) / (R * T0)
        return pressure * (T0 / temperature) ** (g * M / (R * 287))

    def raiseHTTPError(self):
        """Raise an OSError when the OWM API returns an HTTP error."""
        raise OSError(
            "Cannot interact with OWM API, check API key is valid and has not maxed out the allowed requests. If it is a new key, wait at least a day before reporting an issue."
        )

    def validationError(self, key, value, minval, maxval):
        """Raise a ValueError if the value for a key is outside the expected range."""
        raise ValueError(
            f"Value {value} is not valid for {key}. Excepted range: {minval}-{maxval}"
        )
