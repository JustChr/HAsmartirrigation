"""Client for Open-Meteo API (free, no API key required)."""

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
    MAPPING_SOLRAD,
    MAPPING_TEMPERATURE,
    MAPPING_WINDSPEED,
    OBSERVATION_TIME,
    W_TO_MJ_DAY_FACTOR,
)

_LOGGER = logging.getLogger(__name__)

# Shared session so repeated calls reuse the TCP connection and don't re-resolve
# the API hostname on every request.
_SESSION = requests.Session()

# Floor for how long a fetched response is reused, even when the caller's
# configured cache window is shorter (e.g. auto-update disabled → 0s). Open-Meteo
# returns current + forecast + hourly in one document, so caching it here collapses
# the burst of get_data/get_forecast_data/get_hourly_data lookups (skip checks, the
# dashboard outlook, the intra-day estimate) onto a single network/DNS call.
_MIN_CACHE_SECONDS = 60

OPENMETEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,precipitation"
    ",wind_speed_10m,shortwave_radiation,pressure_msl"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
    ",wind_speed_10m_max,shortwave_radiation_sum"
    "&timezone=auto"
    "&wind_speed_unit=ms"
    "&forecast_days=7"
    # One past day so the intra-day estimate's window can reach back to a daily
    # calc that ran the previous evening (anchored to last_calculated, not local
    # midnight). get_hourly_data() then windows these rows to the calc time.
    "&past_days=1"
)

# Wind height correction factor: 10 m → 2 m (Allen et al. FAO-56)
_WIND_10M_TO_2M = 4.87 / math.log((67.8 * 10) - 5.42)

# W m-2 → MJ m-2 hour-1 (×3600 s / 1e6 J). Open-Meteo's hourly
# shortwave_radiation is the preceding-hour mean in W m-2.
_W_TO_MJ_HOUR = 0.0036


class OpenMeteoClient:
    """Open-Meteo weather client. No API key required."""

    def __init__(
        self,
        api_key=None,
        api_version=None,
        latitude=None,
        longitude=None,
        elevation=0,
        cache_seconds=0,
        override_cache=False,
    ) -> None:
        """Init."""
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation or 0
        self.url = OPENMETEO_URL.format(lat=latitude, lon=longitude)
        self.override_cache = override_cache
        self.cache_seconds = cache_seconds
        self._cached_doc = None
        self._cached_doc_at = None

    def _fetch(self):
        """Return the (cached) Open-Meteo response document.

        The whole response — current, daily forecast and hourly series — comes
        from one URL, so a single cached document serves every accessor. Within
        the cache window repeated callers reuse it instead of each hitting the
        network (and a DNS lookup).
        """
        if self._cached_doc is not None and not self.override_cache:
            ttl = max(self.cache_seconds, _MIN_CACHE_SECONDS)
            if datetime.datetime.now() < self._cached_doc_at + datetime.timedelta(
                seconds=ttl
            ):
                _LOGGER.debug("Returning cached Open-Meteo document")
                return self._cached_doc
        req = _SESSION.get(self.url, timeout=60)
        req.raise_for_status()
        doc = json.loads(req.text)
        self._cached_doc = doc
        self._cached_doc_at = datetime.datetime.now()
        return doc

    def _current_hour_index(self, time_list):
        """Return the index of the current UTC hour in the hourly time list."""
        now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        prefix = now.strftime("%Y-%m-%dT%H:")
        for i, t in enumerate(time_list):
            if t.startswith(prefix):
                return i
        # Fall back: most recent past entry
        return max(0, len(time_list) - 1)

    def _wind_2m(self, wind_10m):
        return wind_10m * _WIND_10M_TO_2M

    def _abs_pressure(self, pressure_msl):
        """Convert MSL pressure to station (absolute) pressure at elevation."""
        g, M, R, T0 = 9.80665, 0.0289644, 8.31447, 288.15
        temp = T0 - (g * M * self.elevation) / (R * T0)
        return pressure_msl * (T0 / temp) ** (g * M / (R * 287))

    def get_data(self):
        """Return current conditions mapped to MAPPING_* constants."""
        try:
            doc = self._fetch()
            hourly = doc.get("hourly", {})
            times = hourly.get("time", [])
            idx = self._current_hour_index(times)

            def h(key):
                vals = hourly.get(key, [])
                return vals[idx] if idx < len(vals) else None

            temperature = h("temperature_2m")
            humidity = h("relative_humidity_2m")
            dewpoint = h("dew_point_2m")
            precipitation = h("precipitation") or 0.0
            wind_speed = h("wind_speed_10m")
            radiation = h("shortwave_radiation")
            pressure = h("pressure_msl")

            if None in (temperature, humidity, dewpoint, wind_speed, pressure):
                _LOGGER.warning(
                    "Open-Meteo: missing required hourly values at index %s", idx
                )
                return None

            obs_time_str = times[idx] if idx < len(times) else None
            parsed = {
                MAPPING_TEMPERATURE: temperature,
                MAPPING_HUMIDITY: humidity,
                MAPPING_DEWPOINT: dewpoint,
                MAPPING_WINDSPEED: self._wind_2m(wind_speed),
                MAPPING_PRESSURE: self._abs_pressure(pressure),
                MAPPING_CURRENT_PRECIPITATION: precipitation,
                MAPPING_PRECIPITATION: precipitation,
                OBSERVATION_TIME: (
                    datetime.datetime.fromisoformat(obs_time_str).replace(
                        tzinfo=datetime.timezone.utc
                    )
                    if obs_time_str
                    else None
                ),
            }
            if radiation is not None:
                parsed[MAPPING_SOLRAD] = radiation * W_TO_MJ_DAY_FACTOR

            _LOGGER.debug("Open-Meteo get_data: %s", parsed)
            return parsed

        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            IndexError,
        ) as ex:
            _LOGGER.error("Open-Meteo get_data error: %s", ex)
            return None

    def get_forecast_data(self):
        """Return daily forecast mapped to MAPPING_* constants (list, one dict per day)."""
        try:
            doc = self._fetch()
            daily = doc.get("daily", {})
            n_days = len(daily.get("time", []))

            result = []
            # Skip index 0 (today); iterate the remaining forecast days
            for i in range(1, n_days):
                max_temp = (
                    (daily.get("temperature_2m_max") or [])[i]
                    if i < len(daily.get("temperature_2m_max", []))
                    else None
                )
                min_temp = (
                    (daily.get("temperature_2m_min") or [])[i]
                    if i < len(daily.get("temperature_2m_min", []))
                    else None
                )
                precip = (
                    (daily.get("precipitation_sum") or [])[i]
                    if i < len(daily.get("precipitation_sum", []))
                    else 0.0
                )
                wind = (
                    (daily.get("wind_speed_10m_max") or [])[i]
                    if i < len(daily.get("wind_speed_10m_max", []))
                    else None
                )
                radiation_sum = (
                    (daily.get("shortwave_radiation_sum") or [])[i]
                    if i < len(daily.get("shortwave_radiation_sum", []))
                    else None
                )

                if None in (max_temp, min_temp, wind):
                    continue

                day = {
                    MAPPING_TEMPERATURE: (max_temp + min_temp) / 2.0,
                    MAPPING_MAX_TEMP: max_temp,
                    MAPPING_MIN_TEMP: min_temp,
                    MAPPING_PRECIPITATION: precip or 0.0,
                    MAPPING_WINDSPEED: self._wind_2m(wind),
                }
                if radiation_sum is not None:
                    day[MAPPING_SOLRAD] = radiation_sum

                result.append(day)

            _LOGGER.debug("Open-Meteo get_forecast_data: %s", result)
            return result

        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            IndexError,
        ) as ex:
            _LOGGER.error("Open-Meteo get_forecast_data error: %s", ex)
            return None

    def get_hourly_data(self):
        """Return elapsed hourly rows (local) for the intra-day estimate.

        Returns ``(rows, tz_offset_h)`` or ``(None, None)`` on failure. Each row:
        ``{time, hour, doy, temperature, humidity, wind_2m, solar_mj_h,
        precipitation}`` with the hour midpoint in local clock time. Rows cover
        the past day plus today up to (and including) the current hour — the
        caller windows them to the last daily calc, which may have run the
        previous evening, so a since-midnight slice would truncate the window.
        """
        try:
            doc = self._fetch()
            hourly = doc.get("hourly", {})
            times = hourly.get("time", [])
            if not times:
                return None, None
            tz_offset_h = doc.get("utc_offset_seconds", 0) / 3600.0
            # 'time' entries are local (timezone=auto in the request URL).
            now_local = datetime.datetime.utcnow() + datetime.timedelta(
                hours=tz_offset_h
            )

            temp = hourly.get("temperature_2m", [])
            rh = hourly.get("relative_humidity_2m", [])
            wind = hourly.get("wind_speed_10m", [])
            rad = hourly.get("shortwave_radiation", [])
            precip = hourly.get("precipitation", [])

            rows = []
            for i, tstr in enumerate(times):
                dt = datetime.datetime.fromisoformat(tstr)
                if dt > now_local:
                    continue

                def g(arr, idx=i):
                    return arr[idx] if idx < len(arr) else None

                t, h, w = g(temp), g(rh), g(wind)
                if None in (t, h, w):
                    continue
                rows.append(
                    {
                        "time": tstr,
                        "hour": dt.hour + 0.5,
                        "doy": dt.timetuple().tm_yday,
                        "temperature": t,
                        "humidity": h,
                        "wind_2m": self._wind_2m(w),
                        "solar_mj_h": (g(rad) or 0.0) * _W_TO_MJ_HOUR,
                        "precipitation": g(precip) or 0.0,
                    }
                )
            return rows, tz_offset_h

        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            ValueError,
        ) as ex:
            _LOGGER.error("Open-Meteo get_hourly_data error: %s", ex)
            return None, None
