"""Intra-day "live status" estimate orchestration.

Read-only: estimates how much each zone's bucket has drifted *since its last
calculation* using hourly ET (rigorous, where the weather client exposes hourly
solar radiation) or a Hargreaves-seeded proxy (everywhere else). Does NOT touch
the stored bucket, the daily calculation, or irrigation.

Window correctness: the deficit is anchored to the zone's ``last_calculated``,
NOT to local midnight. The daily calculation already folds today's ET into the
bucket, so a since-midnight window would double-count ET once the daily calc has
run. See ``_rows_since`` / the proxy elapsed-hours logic.
"""

import datetime
import logging

import homeassistant.util.dt as dt_util
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .et_estimate import (
    estimate_daily_et0_hargreaves,
    live_deficit,
    proxy_et_since,
    rigorous_et_since,
)
from .helpers import convert_between
from .weather_aggregate import _parse as _wa_parse
from .weather_aggregate import aggregate_window

_LOGGER = logging.getLogger(__name__)


def _parse_utc_naive(value):
    """Parse a stored datetime/ISO string to a naive-UTC datetime, or None."""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except ValueError:
            return None
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None:
            return value.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return value
    return None


class LiveEstimateMixin:
    """Per-zone intra-day ET estimate for the dashboard (read-only)."""

    async def _fetch_intraday_inputs(self):
        """Fetch the shared hourly (and forecast) inputs once for all zones."""
        client = getattr(self, "_WeatherServiceClient", None)
        if client is None:
            return None
        rows = tz = None
        if hasattr(client, "get_hourly_data"):
            try:
                rows, tz = await self.hass.async_add_executor_job(
                    client.get_hourly_data
                )
            except Exception as e:  # noqa: BLE001 — estimate must never raise
                _LOGGER.debug("intraday: get_hourly_data failed: %s", e)
        forecast = None
        if not rows:
            try:
                forecast = await self.hass.async_add_executor_job(
                    client.get_forecast_data
                )
            except Exception as e:  # noqa: BLE001
                _LOGGER.debug("intraday: get_forecast_data failed: %s", e)
        return {"client": client, "rows": rows, "tz": tz, "forecast": forecast}

    def _observed_precip_since_mm(self, zone):
        """Observed precipitation (mm) collected for the zone's sensor group
        since its last calculation.

        Used by the proxy path (OWM / PirateWeather), where there's no hourly
        precip series — so intraday rain would otherwise be ignored. Delegates
        to the same ``aggregate_window`` the daily calc uses, over the zone's
        un-consumed window, so precipitation is aggregated correctly per source:
        weather-service precip is a rate (mm/h) integrated by RIEMANN sum
        (time-weighted), and a cumulative rain-gauge sensor is summed by DELTA.
        A plain sum would over-count sub-hourly rate readings. Read-only — never
        advances the consume watermark. Includes snow as water-equivalent.
        """
        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is None:
            return 0.0
        mapping = self.store.get_mapping(mapping_id)
        if not mapping:
            return 0.0
        readings = mapping.get(const.MAPPING_DATA) or []
        if not readings:
            return 0.0
        watermark = _wa_parse(zone.get(const.ZONE_LAST_CONSUMED))
        agg = aggregate_window(
            readings, watermark, mapping.get(const.MAPPING_MAPPINGS) or {}
        )
        if not agg:
            return 0.0
        return agg.get(const.MAPPING_PRECIPITATION, 0.0) or 0.0

    @staticmethod
    def _rows_since(rows, last_calc_utc, tz_offset_h):
        """Hourly rows whose hour ends after ``last_calc`` (window = since calc).

        ``rows`` are local (location tz); ``last_calc_utc`` is naive UTC.
        """
        if not last_calc_utc:
            return rows
        last_local = last_calc_utc + datetime.timedelta(hours=tz_offset_h)
        out = []
        for r in rows:
            try:
                rdt = datetime.datetime.fromisoformat(r["time"])
            except (ValueError, KeyError):
                continue
            if rdt + datetime.timedelta(hours=1) > last_local:
                out.append(r)
        return out

    def _intraday_for_zone(self, zone, inputs) -> dict:
        """Compute one zone's estimate from pre-fetched inputs (sync, defensive)."""
        result = {
            "available": False,
            "method": None,
            "et_since": None,
            "precip_since": None,
            "live_deficit": None,
            "as_of": None,
        }
        try:
            client = inputs["client"]
            lat = getattr(client, "latitude", None)
            lon = getattr(client, "longitude", None)
            elevation = getattr(client, "elevation", 0) or 0
            if lat is None or lon is None:
                return result
            bucket = zone.get(const.ZONE_BUCKET)
            if bucket is None:
                return result
            max_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
            metric = self.hass.config.units is METRIC_SYSTEM

            def to_mm(v):
                if v is None:
                    return None
                return (
                    v if metric else convert_between(const.UNIT_INCH, const.UNIT_MM, v)
                )

            def from_mm(v):
                return (
                    v if metric else convert_between(const.UNIT_MM, const.UNIT_INCH, v)
                )

            bucket_mm = to_mm(bucket)
            max_bucket_mm = to_mm(max_bucket)
            last_calc = _parse_utc_naive(zone.get(const.ZONE_LAST_CALCULATED))
            # A never-calculated zone has no anchor for the "since calc" window;
            # showing a whole-day estimate would be misleading (and looks like a
            # shared, un-anchored value). Offer no estimate until the first calc.
            if last_calc is None:
                return result

            rows = inputs["rows"]
            if rows:
                tz = inputs["tz"] or 0.0
                window = self._rows_since(rows, last_calc, tz)
                et_mm = rigorous_et_since(window, lat, lon, tz, elevation)
                precip_mm = sum(r.get("precipitation", 0.0) for r in window)
                method = "hourly"
                as_of = window[-1]["time"] if window else None
            else:
                forecast = inputs["forecast"]
                if not forecast:
                    return result
                day0 = forecast[0]
                tmin = day0.get(const.MAPPING_MIN_TEMP)
                tmax = day0.get(const.MAPPING_MAX_TEMP)
                if tmin is None or tmax is None:
                    return result
                local = dt_util.now()
                tz = (
                    local.utcoffset().total_seconds() / 3600.0
                    if local.utcoffset()
                    else 0.0
                )
                doy = local.timetuple().tm_yday
                start_hour = 0
                if last_calc is not None:
                    last_local = dt_util.as_local(
                        last_calc.replace(tzinfo=datetime.timezone.utc)
                    )
                    if last_local.date() == local.date():
                        start_hour = last_local.hour
                elapsed = [h + 0.5 for h in range(start_hour, local.hour + 1)]
                daily = estimate_daily_et0_hargreaves(tmin, tmax, lat, doy)
                et_mm = proxy_et_since(daily, lat, lon, doy, tz, elapsed)
                # No hourly precip series on this source — use the precipitation
                # actually collected into the sensor group since the last calc,
                # aggregated the same way the daily calc does (rate->Riemann /
                # gauge->delta), so it's time-weighted. 0 when nothing collected.
                precip_mm = self._observed_precip_since_mm(zone)
                method = "proxy"
                as_of = local.isoformat()

            live_mm = live_deficit(bucket_mm, et_mm, precip_mm, max_bucket_mm)
            ndigits = 2 if metric else 3
            result.update(
                available=True,
                method=method,
                et_since=round(from_mm(et_mm), ndigits),
                precip_since=round(from_mm(precip_mm), ndigits),
                live_deficit=round(from_mm(live_mm), ndigits),
                as_of=as_of,
            )
        except Exception as e:  # noqa: BLE001 — estimate must never raise
            _LOGGER.debug("intraday estimate failed for a zone: %s", e)
        return result

    async def async_get_zone_estimates(self) -> dict:
        """Return ``{zone_id: estimate}`` for every zone with an available value."""
        inputs = await self._fetch_intraday_inputs()
        if inputs is None:
            return {}
        zones = await self.store.async_get_zones()
        out = {}
        for zone in zones:
            est = self._intraday_for_zone(zone, inputs)
            if est["available"]:
                out[str(zone.get(const.ZONE_ID))] = est
        return out

    async def async_refresh_zone_estimates(self) -> dict:
        """Recompute the estimates, cache them, and notify the live sensors.

        Called from the existing weather-update and daily-calculation cycles —
        deliberately NOT a separate timer. Both the per-zone live-deficit
        sensors and the panel outlook are served from this one cache so the
        weather client is only hit once per cycle.
        """
        estimates = await self.async_get_zone_estimates()
        self._zone_estimates_cache = estimates
        async_dispatcher_send(self.hass, const.DOMAIN + "_estimates_updated")
        return estimates

    async def async_get_cached_zone_estimates(self) -> dict:
        """Serve the cached estimates, computing them once if not cached yet."""
        cache = getattr(self, "_zone_estimates_cache", None)
        if cache is None:
            return await self.async_refresh_zone_estimates()
        return cache
