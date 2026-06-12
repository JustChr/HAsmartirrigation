"""Weather-data aggregation and ET/bucket calculation for Smart Irrigation.

Extracted from __init__.py (Phase C4). Methods live on a mixin the coordinator
inherits; bodies unchanged (still use ``self``). Covers the weather->calculation
pipeline: merging weather + sensor values, aggregating mapping data, loading the
calculation module, and computing the ET delta / bucket / duration per zone.
Protected by tests/test_calculate_module.py (calculate_module characterization).
"""

import logging
from datetime import datetime, timedelta

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .et_estimate import drained_over_window
from .helpers import convert_between, loadModules, parse_datetime
from .localize import localize
from .weather_aggregate import aggregate_window, select_window

_LOGGER = logging.getLogger(__name__)

# How long a reading may linger in the shared mapping buffer before it is pruned
# regardless of zone watermarks (bounds storage if a zone stops consuming).
BUFFER_RETENTION = timedelta(days=7)


def _as_datetime(value):
    """Coerce a stored watermark/timestamp (datetime or ISO string) to datetime."""
    if isinstance(value, datetime):
        return value
    if value is None:
        return None
    return parse_datetime(value)


class CalculationMixin:
    """Aggregation + ET/bucket calculation for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    async def merge_weatherdata_and_sensor_values(self, wd, sv):
        """Merge weather data and sensor values dictionaries, giving precedence to sensor values.

        Args:
            wd: The weather data dictionary or None.
            sv: The sensor values dictionary or None.

        Returns:
            dict: A merged dictionary with sensor values overriding weather data where keys overlap.

        """
        if wd is None:
            return sv
        if sv is None:
            return wd
        retval = wd
        for key, val in sv.items():
            if key in retval:
                _LOGGER.debug(
                    "merge_weatherdata_and_sensor_values, overriding %s value %s from OWM with %s from sensors",
                    key,
                    retval[key],
                    val,
                )
            else:
                _LOGGER.debug(
                    "merge_weatherdata_and_sensor_values, adding %s value %s from sensors",
                    key,
                    val,
                )
            retval[key] = val

        return retval

    async def _async_clear_all_weatherdata(self, *args):
        """Wipe every mapping's weather buffer and re-anchor zone watermarks.

        The manual "reset all weather data" action. Resetting each zone's
        last_consumed_at to now keeps the per-zone watermarks consistent with the
        now-empty buffer (otherwise a zone would try to consume a window that no
        longer exists).
        """
        _LOGGER.info("Clearing all weatherdata")
        now = datetime.now()
        mappings = await self.store.async_get_mappings()
        for mapping in mappings:
            await self.store.async_update_mapping(
                mapping.get(const.MAPPING_ID), {const.MAPPING_DATA: []}
            )
        for zone in await self.store.async_get_zones():
            await self.store.async_update_zone(
                zone.get(const.ZONE_ID), {const.ZONE_LAST_CONSUMED: now}
            )

    async def _aggregate_for_zone(self, zone, *, now):
        """Aggregate this zone's window of its mapping's shared buffer.

        Returns ``(weatherdata, n_points)`` where ``n_points`` is the number of
        new readings in the zone's window, or ``(None, 0)`` when there is nothing
        to consume (no mapping/data).
        """
        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is None:
            return None, 0
        mapping = self.store.get_mapping(mapping_id)
        if not mapping:
            return None, 0
        readings = mapping.get(const.MAPPING_DATA) or []
        watermark = _as_datetime(zone.get(const.ZONE_LAST_CONSUMED))
        _, window = select_window(readings, watermark)
        weatherdata = aggregate_window(
            readings,
            watermark,
            mapping.get(const.MAPPING_MAPPINGS) or {},
            now=now,
        )
        return weatherdata, len(window)

    async def _prune_mapping_buffer(self, mapping_id, *, now=None):
        """Drop buffer readings no enabled zone needs any more.

        Keeps everything after the oldest enabled-zone watermark (so no zone
        loses unconsumed data) plus the single boundary reading just before it
        (each zone's delta/Riemann baseline), and hard-drops anything older than
        the retention cap. Disabled zones do not hold the buffer.
        """
        if mapping_id is None:
            return
        if now is None:
            now = datetime.now()
        mapping = self.store.get_mapping(mapping_id)
        if not mapping:
            return
        readings = mapping.get(const.MAPPING_DATA) or []
        if not readings:
            return

        cap_cutoff = now - BUFFER_RETENTION
        watermarks = []
        any_unconsumed = False
        for zid in await self._get_zones_that_use_this_mapping(mapping_id):
            z = self.store.get_zone(zid)
            if z is None or z.get(const.ZONE_STATE) == const.ZONE_STATE_DISABLED:
                continue
            wm = _as_datetime(z.get(const.ZONE_LAST_CONSUMED))
            if wm is None:
                any_unconsumed = True
            else:
                watermarks.append(wm)
        if any_unconsumed or not watermarks:
            cutoff = cap_cutoff
        else:
            cutoff = max(cap_cutoff, min(watermarks))

        kept = []
        boundary = None
        boundary_dt = None
        for r in readings:
            rt = (
                _as_datetime(r.get(const.RETRIEVED_AT)) if isinstance(r, dict) else None
            )
            if rt is None or rt > cutoff:
                kept.append(r)
            elif boundary_dt is None or rt >= boundary_dt:
                boundary, boundary_dt = r, rt
        if boundary is not None:
            kept.insert(0, boundary)
        if len(kept) != len(readings):
            _LOGGER.debug(
                "[_prune_mapping_buffer] mapping %s: %s -> %s readings (cutoff %s)",
                mapping_id,
                len(readings),
                len(kept),
                cutoff,
            )
            await self.store.async_update_mapping(
                mapping_id, {const.MAPPING_DATA: kept}
            )

    async def _async_calculate_all(self, *args):
        """Calculate every automatic zone, each over its own consumption window.

        Each zone consumes ``(last_consumed_at, now]`` of its mapping's shared
        buffer and advances its own watermark; the buffer is pruned once per
        touched mapping at the end (never cleared wholesale, so zones sharing a
        mapping keep their independent history).
        """
        _LOGGER.info("Calculating all automatic zones")
        zones = await self.store.async_get_zones()

        now = datetime.now()
        forecastdata = None
        touched_mappings = set()
        for zone in zones:
            if zone.get(const.ZONE_STATE) != const.ZONE_STATE_AUTOMATIC:
                continue
            # fetch forecast once if any PyETO-with-forecast zone needs it
            modinst = await self.getModuleInstanceByID(zone.get(const.ZONE_MODULE))
            if modinst and modinst.name == "PyETO" and modinst.forecast_days > 0:
                if self.use_weather_service:
                    if forecastdata is None:
                        forecastdata = await self.hass.async_add_executor_job(
                            self._WeatherServiceClient.get_forecast_data
                        )
                else:
                    _LOGGER.error(
                        "Error calculating zone %s: forecasting configured but no weather service API is set",
                        zone.get(const.ZONE_NAME),
                    )
                    continue
            await self.async_calculate_zone(
                zone.get(const.ZONE_ID), forecastdata, now=now, prune=False
            )
            touched_mappings.add(zone.get(const.ZONE_MAPPING))

        # Prune each touched mapping once all its zones have advanced.
        for mapping_id in touched_mappings:
            await self._prune_mapping_buffer(mapping_id, now=now)

        # Buckets just changed → the cached intraday estimates are stale
        # (they are anchored to last_calculated). Refresh once for everyone.
        await self.async_refresh_zone_estimates()

    async def async_calculate_zone(
        self, zone_id, forecastdata=None, *, now=None, prune=True
    ):
        """Calculate one zone from its own window of the shared mapping buffer.

        The zone consumes ``(last_consumed_at, now]`` of its mapping's readings
        and advances its watermark. The shared buffer is NOT cleared here (other
        zones may still need it) — it is pruned by ``_prune_mapping_buffer``.

        Args:
            zone_id: the zone to calculate.
            forecastdata: optional pre-fetched forecast for PyETO-with-forecast.
            now: shared "now" so the watermark and multiplier agree (calc-all).
            prune: prune the buffer afterwards (False for calc-all, which prunes
                once at the end).
        """
        _LOGGER.debug("async_calculate_zone: Calculating zone %s", zone_id)
        if now is None:
            now = datetime.now()
        zone = self.store.get_zone(zone_id)
        if zone is None:
            return

        weatherdata, n_points = await self._aggregate_for_zone(zone, now=now)
        if weatherdata is None:
            _LOGGER.debug(
                "async_calculate_zone: no weather data to consume for zone %s",
                zone_id,
            )
            return

        calc_data = await self.calculate_module(zone, weatherdata, forecastdata)
        if calc_data is None:
            _LOGGER.error(
                "async_calculate_zone: calculation returned no result for zone %s "
                "(module missing or not configured?)",
                zone_id,
            )
            return

        calc_data[const.ZONE_LAST_CALCULATED] = now
        calc_data[const.ZONE_LAST_UPDATED] = now
        # Advance this zone's watermark so it never re-consumes this window.
        calc_data[const.ZONE_LAST_CONSUMED] = now
        calc_data[const.ZONE_NUMBER_OF_DATA_POINTS] = n_points

        await self.store.async_update_zone(zone.get(const.ZONE_ID), calc_data)
        if prune:
            await self._prune_mapping_buffer(zone.get(const.ZONE_MAPPING), now=now)
        async_dispatcher_send(
            self.hass,
            const.DOMAIN + "_config_updated",
            zone.get(const.ZONE_ID),
        )
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")

    async def getModuleInstanceByID(self, module_id):
        """Retrieve and instantiate a module by its ID.

        Args:
            module_id: The ID of the module to retrieve.

        Returns:
            The instantiated module object, or None if not found.

        """
        m = self.store.get_module(module_id)
        if m is None:
            return None
        # load the module dynamically
        mods = await self.hass.async_add_executor_job(loadModules, const.MODULE_DIR)
        modinst = None
        for mod in mods:
            if mods[mod]["class"] == m[const.MODULE_NAME]:
                themod = getattr(mods[mod]["module"], mods[mod]["class"])
                modinst = themod(
                    self.hass, description=m["description"], config=m["config"]
                )
                break
        # Honor manually-configured coordinates. Calc modules that derive solar
        # radiation from latitude/elevation (e.g. PyETO) build those from
        # hass.config at construction; override with the integration's effective
        # coordinates so manual coordinates are respected here too — previously
        # they only reached the weather client, not the PyETO solar-radiation math.
        if modinst is not None:
            eff_lat = getattr(self, "_effective_latitude", None)
            eff_elev = getattr(self, "_effective_elevation", None)
            if eff_lat is not None and hasattr(modinst, "_latitude"):
                modinst._latitude = eff_lat
            if eff_elev is not None and hasattr(modinst, "_elevation"):
                modinst._elevation = eff_elev
        return modinst

    async def calculate_module(self, zone, weatherdata, forecastdata):
        """Calculate irrigation values for a zone using the specified weather and forecast data.

        Args:
            zone: The zone dictionary containing configuration and state.
            weatherdata: Aggregated weather data for the calculation.
            forecastdata: Forecast data if required by the module.

        Returns:
            dict: Updated zone data including calculation results and explanation.

        """
        _LOGGER.debug("calculate_module for zone: %s", zone)
        # _LOGGER.debug("[calculate_module] for zone: %s, weatherdata: %s, forecastdata: %s", zone, weatherdata, forecastdata)
        mod_id = zone.get(const.ZONE_MODULE)
        m = self.store.get_module(mod_id)
        if m is None:
            return None
        modinst = await self.getModuleInstanceByID(mod_id)
        if not modinst:
            _LOGGER.error("Unknown module for zone %s", zone.get(const.ZONE_NAME))
            return None
        # precip = 0
        ha_config_is_metric = self.hass.config.units is METRIC_SYSTEM
        bucket = zone.get(const.ZONE_BUCKET)
        maximum_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
        if not ha_config_is_metric:
            bucket = convert_between(const.UNIT_INCH, const.UNIT_MM, bucket)
            if zone.get(const.ZONE_MAXIMUM_BUCKET) is not None:
                maximum_bucket = convert_between(
                    const.UNIT_INCH, const.UNIT_MM, zone.get(const.ZONE_MAXIMUM_BUCKET)
                )
        data = {}
        old_bucket = bucket
        explanation = ""

        precip = 0
        if m[const.MODULE_NAME] == "PyETO":
            # pyeto expects pressure in hpa, solar radiation in mj/m2/day and wind speed in m/s
            delta = modinst.calculate(
                weather_data=weatherdata, forecast_data=forecastdata
            )
            # only PyETO uses precipitation
            precip = weatherdata.get(const.MAPPING_PRECIPITATION, 0)
            _LOGGER.debug("[calculate-module]: precip: %s", precip)
        elif m[const.MODULE_NAME] == "Static":
            delta = modinst.calculate()
        elif m[const.MODULE_NAME] == "Passthrough":
            if const.MAPPING_EVAPOTRANSPIRATION in weatherdata:
                delta = 0 - modinst.calculate(
                    et_data=weatherdata[const.MAPPING_EVAPOTRANSPIRATION]
                )
            else:
                _LOGGER.error(
                    "No evapotranspiration value provided for Passthrough module for zone %s",
                    zone.get(const.ZONE_NAME),
                )
                return None
        # Scale module ET value by interval (hour_multiplier = fractional days)
        _LOGGER.debug("[calculate-module]: retrieved from module: %s", delta)
        hour_multiplier = weatherdata.get(const.MAPPING_DATA_MULTIPLIER, 1.0)
        _LOGGER.debug("[calculate-module]: hour_multiplier: %s", hour_multiplier)
        delta = delta * hour_multiplier + precip
        data[const.ZONE_DELTA] = delta
        _LOGGER.debug("[calculate-module]: new delta: %s", delta)
        newbucket = bucket + delta

        # if maximum bucket configured, limit bucket with that.
        # any water above maximum is removed with runoff / bypass flow.
        if maximum_bucket is not None and newbucket > maximum_bucket:
            newbucket = float(maximum_bucket)
            _LOGGER.debug(
                "[calculate-module]: capped new bucket because of maximum bucket: %s",
                newbucket,
            )
        bucket_plus_delta_capped = newbucket

        # take drainage rate into account
        drainage_rate = zone.get(const.ZONE_DRAINAGE_RATE, 0.0)
        if drainage_rate is None:
            drainage_rate = 0.0
        if not ha_config_is_metric:
            # drainage_rate is in inch/h since HA is not in metric, so we need to adjust those first!
            # using inch and mm here since both are per hour
            drainage_rate = convert_between(
                const.UNIT_INCH, const.UNIT_MM, drainage_rate
            )
        _LOGGER.debug("[calculate-module]: drainage_rate: %s", drainage_rate)
        # Drainage only acts on water above field capacity (surplus > 0) and is
        # integrated analytically over the elapsed window (see
        # ``drained_over_window``). This replaces the previous single
        # explicit-Euler step, which over-drained because the rate was sampled
        # once at the end-of-window surplus and charged for the whole window.
        elapsed_hours = hour_multiplier * 24
        drainage = drained_over_window(
            bucket_plus_delta_capped,
            drainage_rate,
            elapsed_hours,
            maximum_bucket if maximum_bucket and maximum_bucket > 0 else None,
        )
        newbucket = bucket_plus_delta_capped - drainage
        _LOGGER.debug("[calculate-module]: current_drainage: %s", drainage)

        data[const.ZONE_CURRENT_DRAINAGE] = drainage
        _LOGGER.debug("[calculate-module]: newbucket: %s", newbucket)

        # Experimental forecast weighting: when rain is forecast, water LESS by
        # folding the look-ahead precipitation into the deficit used for the
        # *duration* — but keep the true deficit in the bucket so the real rain
        # fills the rest (folding it into the bucket itself would double-count
        # the forecasted rain once it is actually collected). ``effective_bucket``
        # drives the duration; ``newbucket`` (unchanged) stays the persisted
        # bucket. ``irrigation_target_bucket`` carries the leftover deficit for
        # the runner so a completed run leaves the zone at that level, not 0.
        effective_bucket = newbucket
        if (
            newbucket < 0
            and getattr(self, "use_weather_service", False)
            and self.store.config.forecast_weighting_enabled
        ):
            fd = forecastdata
            if fd is None and self._WeatherServiceClient is not None:
                fd = await self.hass.async_add_executor_job(
                    self._WeatherServiceClient.get_forecast_data
                )
            if fd:
                config = await self.store.async_get_config()
                days = max(
                    1,
                    config.get(
                        const.CONF_PRECIPITATION_FORECAST_DAYS,
                        const.CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS,
                    ),
                )
                forecast_precip = sum(
                    day_data.get(const.MAPPING_PRECIPITATION, 0.0)
                    for day_data in fd[:days]
                )
                if forecast_precip > 0:
                    effective_bucket = min(0.0, newbucket + forecast_precip)
                    _LOGGER.debug(
                        "[calculate-module]: forecast weighting %.2f mm rain → "
                        "effective bucket %.2f (true %.2f)",
                        forecast_precip,
                        effective_bucket,
                        newbucket,
                    )

        explanation = (
            await localize(
                "module.calculation.explanation.module-returned-evapotranspiration-deficiency",
                self.hass.config.language,
            )
            + f" {data[const.ZONE_DELTA]:.2f}."
        )
        explanation += (
            await localize(
                "module.calculation.explanation.bucket-was", self.hass.config.language
            )
            + f" {old_bucket:.2f}"
        )
        explanation += (
            ".<br/>"
            + await localize(
                "module.calculation.explanation.maximum-bucket-is",
                self.hass.config.language,
            )
            + f" {float(maximum_bucket):.1f}"
        )
        explanation += (
            ".<br/>"
            + await localize(
                "module.calculation.explanation.drainage-rate-is",
                self.hass.config.language,
            )
            + f" {float(drainage_rate):.1f}.<br/>"
        )

        # Define some localized strings here for cleaner code below
        hours_loc = await localize(
            "module.calculation.explanation.hours", self.hass.config.language
        )
        drainage_loc = await localize(
            "module.calculation.explanation.drainage", self.hass.config.language
        )
        drainage_rate_loc = await localize(
            "module.calculation.explanation.drainage-rate", self.hass.config.language
        )
        delta_loc = await localize(
            "module.calculation.explanation.delta", self.hass.config.language
        )
        old_bucket_loc = await localize(
            "module.calculation.explanation.old-bucket-variable",
            self.hass.config.language,
        )
        max_bucket_loc = await localize(
            "module.calculation.explanation.max-bucket-variable",
            self.hass.config.language,
        )

        if bucket_plus_delta_capped <= 0:
            explanation += (
                await localize(
                    "module.calculation.explanation.no-drainage",
                    self.hass.config.language,
                )
                + f" [{old_bucket_loc}] + [{delta_loc}] <= 0 ({old_bucket:.2f}{data[const.ZONE_DELTA]:+.2f} = {bucket_plus_delta_capped:.2f})"
            )
        else:
            explanation += await localize(
                "module.calculation.explanation.current-drainage-is",
                self.hass.config.language,
            )
            if maximum_bucket is None or maximum_bucket <= 0:
                # constant-rate drainage, capped at the available surplus
                explanation += f" min([{old_bucket_loc}] + [{delta_loc}], [{drainage_rate_loc}] * [{hours_loc}]) = min({bucket_plus_delta_capped:.2f}, {drainage_rate:.1f} * {elapsed_hours:.2f}) = {drainage:.2f}"
            else:
                # closed-form Brooks-Corey decay integrated over the window;
                # report the surplus before/after and the water actually drained
                explanation += await localize(
                    "module.calculation.explanation.drainage-integrated",
                    self.hass.config.language,
                )
                explanation += f" ([{drainage_rate_loc}] * (W/[{max_bucket_loc}])^4, {elapsed_hours:.2f} [{hours_loc}]): W = {bucket_plus_delta_capped:.2f} &rarr; {newbucket:.2f}, [{drainage_loc}] = {drainage:.2f}"
        explanation += ".<br/>" + await localize(
            "module.calculation.explanation.new-bucket-values-is",
            self.hass.config.language,
        )

        if maximum_bucket is not None and maximum_bucket > 0:
            explanation += f" min([{old_bucket_loc}] + [{delta_loc}], {max_bucket_loc}) - [{drainage_loc}] = min({old_bucket:.2f}{data[const.ZONE_DELTA]:+.2f}, {maximum_bucket:.1f}) - {drainage:.2f} = {newbucket:.2f}.<br/>"
        else:
            explanation += f" [{old_bucket_loc}] + [{delta_loc}] - [{drainage_loc}] = {old_bucket:.2f} + {data[const.ZONE_DELTA]:.2f} - {drainage:.2f} = {newbucket:.2f}.<br/>"

        if effective_bucket < 0:
            # calculate duration (from the effective deficit — equal to the true
            # bucket unless forecast weighting trimmed it for expected rain)

            tput = zone.get(const.ZONE_THROUGHPUT)
            sz = zone.get(const.ZONE_SIZE)
            if not ha_config_is_metric:
                # throughput is in gpm and size is in sq ft since HA is not in metric, so we need to adjust those first!
                tput = convert_between(const.UNIT_GPM, const.UNIT_LPM, tput)
                sz = convert_between(const.UNIT_SQ_FT, const.UNIT_M2, sz)
            precipitation_rate = (tput * 60) / sz
            duration = abs(effective_bucket) / precipitation_rate * 3600
            if effective_bucket != newbucket:
                explanation += (
                    await localize(
                        "module.calculation.explanation.forecast-weighting-applied",
                        self.hass.config.language,
                    )
                    + f" ({newbucket:.2f} &rarr; {effective_bucket:.2f}).<br/>"
                )
            explanation += (
                await localize(
                    "module.calculation.explanation.bucket-less-than-zero-irrigation-necessary",
                    self.hass.config.language,
                )
                + ".<br/>"
                + await localize(
                    "module.calculation.explanation.steps-taken-to-calculate-duration",
                    self.hass.config.language,
                )
                + ":<br/>"
            )
            explanation += (
                "<ol><li>"
                + await localize(
                    "module.calculation.explanation.precipitation-rate-defined-as",
                    self.hass.config.language,
                )
                + " ["
                + await localize(
                    "common.attributes.throughput", self.hass.config.language
                )
                + "] * 60 / ["
                + await localize("common.attributes.size", self.hass.config.language)
                + f"] = {tput:.1f} * 60 / {sz:.1f} = {precipitation_rate:.1f}.</li>"
            )
            explanation += (
                "<li>"
                + await localize(
                    "module.calculation.explanation.duration-is-calculated-as",
                    self.hass.config.language,
                )
                + " abs(["
                + await localize(
                    "module.calculation.explanation.bucket", self.hass.config.language
                )
                + "]) / ["
                + await localize(
                    "module.calculation.explanation.precipitation-rate-variable",
                    self.hass.config.language,
                )
                + f"] * 3600 = {abs(effective_bucket):.2f} / {precipitation_rate:.1f} * 3600 = {duration:.0f}.</li>"
            )
            duration = zone.get(const.ZONE_MULTIPLIER) * duration
            explanation += (
                "<li>"
                + await localize(
                    "module.calculation.explanation.multiplier-is-applied",
                    self.hass.config.language,
                )
                + f" {zone.get(const.ZONE_MULTIPLIER)}, "
            )
            explanation += (
                await localize(
                    "module.calculation.explanation.duration-after-multiplier-is",
                    self.hass.config.language,
                )
                + f" {round(duration)}.</li>"
            )

            # get maximum duration if set and >=0 and override duration if it's higher than maximum duration
            explanation += (
                "<li>"
                + await localize(
                    "module.calculation.explanation.maximum-duration-is-applied",
                    self.hass.config.language,
                )
                + f" {zone.get(const.ZONE_MAXIMUM_DURATION):.0f}"
            )
            if (
                zone.get(const.ZONE_MAXIMUM_DURATION) is not None
                and zone.get(const.ZONE_MAXIMUM_DURATION) >= 0
                and duration > zone.get(const.ZONE_MAXIMUM_DURATION)
            ):
                duration = zone.get(const.ZONE_MAXIMUM_DURATION)
                explanation += (
                    ", "
                    + await localize(
                        "module.calculation.explanation.duration-after-maximum-duration-is",
                        self.hass.config.language,
                    )
                    + f" {duration:.0f}"
                )
            explanation += ".</li>"

            # add the lead time but only if duration is > 0 at this point
            if duration > 0.0:
                duration = round(zone.get(const.ZONE_LEAD_TIME) + duration)
                explanation += (
                    "<li>"
                    + await localize(
                        "module.calculation.explanation.lead-time-is-applied",
                        self.hass.config.language,
                    )
                    + f" {zone.get(const.ZONE_LEAD_TIME)}, "
                )
                explanation += (
                    await localize(
                        "module.calculation.explanation.duration-after-lead-time-is",
                        self.hass.config.language,
                    )
                    + f" {duration}</li></ol>"
                )
                explanation += (
                    await localize(
                        "module.calculation.explanation.duration-after-lead-time-is",
                        self.hass.config.language,
                    )
                    + f" {duration}.</li></ol>"
                )

                # _LOGGER.debug("[calculate-module]: explanation: %s", explanation)
        else:
            # no need to irrigate, set duration to 0
            duration = 0
            explanation += (
                await localize(
                    "module.calculation.explanation.bucket-larger-than-or-equal-to-zero-no-irrigation-necessary",
                    self.hass.config.language,
                )
                + f" {duration}"
            )

        data[const.ZONE_BUCKET] = newbucket
        # Leftover deficit a completed run should stop at: 0.0 normally (run
        # replenishes the full deficit), or the rain-covered remainder when
        # forecast weighting trimmed this run. Stored in display units like the
        # bucket so the runner can apply it directly. No irrigation ⇒ no target.
        target_bucket = (newbucket - effective_bucket) if duration else 0.0
        data[const.ZONE_IRRIGATION_TARGET_BUCKET] = target_bucket
        if not ha_config_is_metric:
            data[const.ZONE_BUCKET] = convert_between(
                const.UNIT_MM, const.UNIT_INCH, data[const.ZONE_BUCKET]
            )
            data[const.ZONE_IRRIGATION_TARGET_BUCKET] = convert_between(
                const.UNIT_MM, const.UNIT_INCH, target_bucket
            )
        data[const.ZONE_DURATION] = duration
        data[const.ZONE_EXPLANATION] = explanation
        return data
