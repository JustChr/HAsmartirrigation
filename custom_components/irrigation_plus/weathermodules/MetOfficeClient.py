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
    FORECAST_DAY_END,
    FORECAST_DAY_START,
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
from ..pressure import relative_to_absolute_pressure
from . import fetch_gate

_LOGGER = logging.getLogger(__name__)

# Shared session so repeated calls reuse the TCP connection and don't re-resolve
# the API hostname on every request.
_SESSION = requests.Session()

# The three-hourly product's step: the most the hourly document may lag behind it
# and still be read in its place, whatever the cache lifetime (_forecast_document).
_THREE_HOURLY_STEP = datetime.timedelta(hours=3)

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


def _is_aware_instant(value) -> bool:
    """Whether ``value`` is a datetime carrying a time zone.

    A coverage target without one cannot be compared with a document's stamps,
    which are aware UTC, so it is passed over rather than read as UTC -- the rule
    ``forecast_window.day_span`` already applies to a daily entry's span.
    """
    return isinstance(value, datetime.datetime) and value.utcoffset() is not None


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
        self._hourly_gate = fetch_gate.FetchGate(self, "_cached_hourly_at")
        self._three_hourly_gate = fetch_gate.FetchGate(self, "_cached_three_hourly_at")

    # ------------------------------------------------------------------ helpers

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

    @classmethod
    def _series_reach(cls, doc):
        """How far a document's hourly series runs, or None where that cannot be told.

        Wurzel: the two products reach differently -- the hourly one about 48
          hours from its own FETCH, the three-hourly one about seven days -- and
          only ``get_data`` refreshes the hourly document, so its reach ages with
          it. "48 hours" written into the code would be a guess about the product
          and about when it was fetched, and a caller cannot check either.
        Fix-Logik: read it off the document. The accessors stamp each sample at
          ``when + span``, so a document reaches its last step's time plus that
          step's span, and the last step's span is the spacing before it -- an
          hour for a lone sample, exactly as
          ``get_hourly_precipitation_forecast`` reads one. None where the series
          is empty, holds no usable stamp or does not run forwards; the caller
          then keeps its other rule rather than guessing.
        NOT-TO-DO: do not measure this over the steps carrying precipitation only.
          It is the document's reach, and the chooser it serves answers for both
          accessors. A document whose last steps carry no amount therefore reads
          as reaching further than its precipitation series does, which keeps the
          finer product -- what happens today, and bounded by one step.
        siehe tests/test_met_office_forecast_document.py
        """
        stamps = []
        for step in cls._time_series(doc):
            ts = step.get("time")
            if not ts:
                continue
            try:
                stamps.append(cls._parse_time(ts))
            except (AttributeError, TypeError, ValueError):
                continue
        if not stamps:
            return None
        if len(stamps) > 1:
            span = stamps[-1] - stamps[-2]
        else:
            span = datetime.timedelta(hours=1)
        if span <= datetime.timedelta(0):
            return None
        return stamps[-1] + span

    def _wind_2m(self, wind_10m):
        return wind_10m * _WIND_10M_TO_2M

    def _abs_pressure_from_pa(self, mslp_pa):
        """Convert MSL pressure in Pa to station (absolute) pressure in hPa."""
        return relative_to_absolute_pressure(mslp_pa / 100.0, self.elevation)

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
        return self._hourly_gate.run(self._fetch_hourly_doc)

    def _fetch_hourly_doc(self):
        """Body of ``_fetch_hourly``, run inside ``_hourly_gate``."""
        if fetch_gate.is_fresh(
            self._cached_hourly_at, self.cache_seconds, self.override_cache
        ):
            return self._cached_hourly
        doc = self._request(self._hourly_url)
        self._cached_hourly = doc
        self._cached_hourly_at = datetime.datetime.now()
        return doc

    def _fetch_three_hourly(self):
        return self._three_hourly_gate.run(self._fetch_three_hourly_doc)

    def _fetch_three_hourly_doc(self):
        """Body of ``_fetch_three_hourly``, run inside ``_three_hourly_gate``."""
        if fetch_gate.is_fresh(
            self._cached_three_hourly_at, self.cache_seconds, self.override_cache
        ):
            return self._cached_three_hourly
        doc = self._request(self._three_hourly_url)
        self._cached_three_hourly = doc
        self._cached_three_hourly_at = datetime.datetime.now()
        return doc

    def _forecast_document(self, covering_until=None):
        """The fetched document the hourly accessors read, or None.

        ``covering_until`` is how far the caller needs the series to reach; a
        caller with nothing to cover names none.

        Wurzel: both accessors took the hourly document whenever one existed. Only
          ``get_data`` refreshes it, and the precipitation skip guard runs before
          any ``get_data`` of a dispatch, so an install whose sensors take nothing
          from Met Office read the hourly forecast of an earlier run beside a
          three-hourly document ``get_forecast_data`` had just fetched. A tolerance
          of one cache lifetime alone did not end it on a daily or two-day
          auto-update: the lifetime is then a day or two, so an hourly document
          fetched the evening before a fresh three-hourly one still won, and its
          T..T+48 h series can end before the run's local date does. The guard
          then found the run date uncovered and did not decide, although the
          three-hourly document covered it. Fetch times alone cannot close that
          either: an hourly document too young to lose the comparison below can
          still stop inside the window, and nothing fills the gap afterwards --
          ``forecast_window._entries_behind`` admits a daily entry only where its
          span starts after the series ends.
        Fix-Logik: two rules, because two different questions are being asked.
          Which document is more CURRENT: prefer the hourly product, the finer of
          the two, unless the three-hourly one was fetched more than one cache
          lifetime, at most three hours, after it. Three hours is the three-hourly
          product's own step: a three-hourly document newer than the hourly one by
          more than one of its steps is the more current forecast, and the cap
          bounds how far behind the hourly series can fall whatever the update
          interval. Within an hourly update cycle the lifetime is below the cap
          and nothing changes: a document younger than that is as current as the
          cache allows. Which document REACHES far enough: where the caller names
          a ``covering_until`` the hourly series stops before and the three-hourly
          one attains, the coarser product serves whatever the fetch times say --
          a finer series ending inside the window cannot answer what is being
          asked of it, while resolution is worth keeping everywhere else. Where
          neither reaches the target, or both do, that swap buys no coverage and
          the fetch times decide alone.
          The price of that rule, recorded so it can be overruled: the guard's
          target is the WHOLE window, the run's start plus the look-ahead times
          24 h, while only the FIRST of those 24-hour blocks gates its decision.
          The hourly product runs 48 h from its own fetch and is read up to one
          cache lifetime later, so from a look-ahead of 2 it essentially never
          attains that target while the three-hourly one does -- the coarser
          document then serves the decisive first block as well, all but always.
          Its three-hour buckets place rain only to within a step, and a bucket
          straddling the run's start or the window's end is counted by overlap,
          so up to one step's rain can move across either edge. Kept because the
          threshold compares a TOTAL over the whole window, not a first block:
          covering the later blocks is what makes that total right, and a target
          of only the first block would buy the finer placing back at the cost
          of a total summed over hours no series reached.
        NOT-TO-DO: do not fetch here; the accessors read already-fetched documents
          only. And do not simply take the later fetch: the calculation's forecast
          fetch follows the update cycle by minutes and would swap the finer
          product out of the intra-day estimate after every calculation. Do not
          hand ``get_hourly_temperature_forecast`` a target: the intra-day
          estimate reads short spans, where the finer product's placing matters
          and its reach does not. And do not take a product's reach as given
          ("48 hours") -- it is measured off the document, see ``_series_reach``.
        siehe tests/test_met_office_forecast_document.py
        """
        hourly, three_hourly = self._cached_hourly, self._cached_three_hourly
        if not hourly or not three_hourly:
            return hourly or three_hourly
        if _is_aware_instant(covering_until):
            hourly_reach = self._series_reach(hourly)
            three_hourly_reach = self._series_reach(three_hourly)
            if (
                hourly_reach is not None
                and three_hourly_reach is not None
                and hourly_reach < covering_until <= three_hourly_reach
            ):
                return three_hourly
        if self._cached_hourly_at is None or self._cached_three_hourly_at is None:
            return hourly
        lifetime = datetime.timedelta(
            seconds=fetch_gate.cache_lifetime(self.cache_seconds)
        )
        tolerance = min(lifetime, _THREE_HOURLY_STEP)
        if self._cached_three_hourly_at - self._cached_hourly_at > tolerance:
            return three_hourly
        return hourly

    def get_hourly_temperature_forecast(self):
        """``[(aware UTC datetime, temperature C)]`` from the hourly product.

        The hourly endpoint runs T to T+48, which covers a calculation window's
        remaining hours with room to spare. Falls back to the three-hourly
        product where only that has been fetched, or where the hourly document
        is more than one cache lifetime, at most three hours, older
        (``_forecast_document``) -- coarser, but it still places the window's
        extremes far better than reading them off the observation. It names no
        coverage target: this reads short spans, where the finer product's
        placing matters and how far it runs does not.

        Reads an already-fetched document only; see
        ``OpenMeteoClient.get_hourly_temperature_forecast`` for why.
        """
        doc = self._forecast_document()
        if not doc:
            return None
        out = []
        for step in self._time_series(doc):
            temp = step.get("screenTemperature")
            ts = step.get("time")
            if temp is None or not ts:
                continue
            try:
                out.append((self._parse_time(ts), float(temp)))
            except (TypeError, ValueError):
                continue
        return out or None

    def get_hourly_precipitation_forecast(self, covering_until=None):
        """``[(aware UTC datetime, mm/h)]`` from the hourly product.

        ``totalPrecipAmount`` is the accumulation over the period FOLLOWING each
        step, so the stamp is advanced by that period to give the rate over the
        interval ENDING at it -- the convention every client hands back, and the
        one the consumer integrates. The step length is taken from the series
        itself, so the three-hourly product stands in where only it was fetched
        or the hourly document is more than one cache lifetime, at most three
        hours, older (``_forecast_document``), and its samples are divided back
        to a rate rather than counted as an hour's worth.

        ``covering_until`` is a HINT about how far the caller needs coverage, and
        the one thing it changes is WHICH of the two documents is read: the
        three-hourly one stands in where the hourly series stops before that
        moment and it does not. The series is never truncated, padded or
        otherwise cut to the hint -- whichever document is chosen is handed back
        whole, and the caller windows it as it sees fit.

        Reads only the already-fetched document and never issues a request of its
        own, for the same reason the temperature accessor does not.
        """
        doc = self._forecast_document(covering_until)
        if not doc:
            return None
        stamps = []
        for step in self._time_series(doc):
            amount = step.get("totalPrecipAmount")
            ts = step.get("time")
            if amount is None or not ts:
                continue
            try:
                stamps.append((self._parse_time(ts), float(amount)))
            except (TypeError, ValueError):
                continue
        if not stamps:
            return None
        out = []
        previous_span = None
        for i, (when, amount) in enumerate(stamps):
            if i + 1 < len(stamps):
                span = stamps[i + 1][0] - when
            else:
                # The last sample has nothing after it to measure against, so it
                # keeps the spacing the series has been using. An hour stands in
                # only for a lone sample: it is the finer of the two products and
                # the conservative reading of a total.
                span = previous_span or datetime.timedelta(hours=1)
            hours = span.total_seconds() / 3600.0
            if hours <= 0:
                continue
            previous_span = span
            out.append((when + span, amount / hours))
        return out or None

    def get_data(self):
        """Return current conditions mapped to MAPPING_* constants."""
        try:
            steps = self._time_series(self._fetch_hourly())
            if not steps:
                _LOGGER.warning("Met Office get_data: empty time series")
                return None

            now = datetime.datetime.now(datetime.UTC)
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
            _LOGGER.log(
                fetch_gate.failure_log_level(ex), "Met Office get_data error: %s", ex
            )
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

            today = datetime.datetime.now(datetime.UTC).date()
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

                # day is the UTC calendar date the steps were grouped by. When the
                # product ends mid-day the last entry still spans the whole date,
                # but its precipitation holds only the steps that exist, so that
                # day's total is short.
                day_start = datetime.datetime(
                    day.year, day.month, day.day, tzinfo=datetime.UTC
                )

                day_data = {
                    MAPPING_TEMPERATURE: mean_temp,
                    MAPPING_MAX_TEMP: max_temp,
                    MAPPING_MIN_TEMP: min_temp,
                    MAPPING_WINDSPEED: self._wind_2m(mean_wind),
                    MAPPING_PRECIPITATION: precip,
                    FORECAST_DAY_START: day_start,
                    FORECAST_DAY_END: day_start + datetime.timedelta(days=1),
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
            _LOGGER.log(
                fetch_gate.failure_log_level(ex),
                "Met Office get_forecast_data error: %s",
                ex,
            )
            return None
