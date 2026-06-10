"""Irrigation skip-condition checks and days-between tracking.

Extracted from __init__.py (Phase C5). Methods live on a mixin the coordinator
inherits; bodies unchanged (still use ``self``). Covers the pre-irrigation
decision logic: skip on precipitation forecast / temperature / wind / rain
sensor, the days-between-irrigation counter, and the total-duration query used
by the scheduler and websockets.
"""

import logging

import homeassistant.util.dt as dt_util

from . import const

_LOGGER = logging.getLogger(__name__)

# Stable ids for each skip guard; mirrored by the frontend localization keys.
SKIP_PRECIPITATION = "precipitation"
SKIP_DAYS_BETWEEN = "days_between"
SKIP_TEMPERATURE = "temperature"
SKIP_WIND = "wind"
SKIP_RAIN_SENSOR = "rain_sensor"


class SkipConditionsMixin:
    """Skip-condition checks for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    async def _check_skip_conditions(self) -> bool:
        """Return True if irrigation should be skipped (any condition is met).

        Evaluates every guard (rather than short-circuiting) so the result can be
        persisted as the dashboard's "last run" explanation; the return value is
        unchanged (skip if any enabled guard is met).
        """
        evaluation = await self.async_evaluate_skip_conditions()
        self._last_skip_evaluation = {
            "timestamp": dt_util.utcnow().isoformat(),
            "would_skip": evaluation["would_skip"],
            "checks": evaluation["checks"],
        }
        if evaluation["would_skip"]:
            reasons = [
                c["id"]
                for c in evaluation["checks"]
                if c["enabled"] and c["would_skip"]
            ]
            _LOGGER.info("Irrigation skipped due to conditions: %s", ", ".join(reasons))
        return evaluation["would_skip"]

    # --- structured (no-side-effect) evaluation for the dashboard outlook ----

    async def async_evaluate_skip_conditions(self) -> dict:
        """Evaluate every skip guard and return structured results.

        Unlike the boolean ``_check_*`` helpers this does not log skip decisions;
        it is safe to call for a live preview. Each check is a dict with keys
        ``id``, ``enabled``, ``would_skip``, ``available`` (could it be
        evaluated), ``observed`` and ``threshold``. Precipitation/temperature/
        wind reuse the in-memory weather-client cache, so this is normally cheap.
        """
        config = await self.store.async_get_config()
        checks = [
            await self._eval_precipitation(config),
            await self._eval_days_between(config),
            await self._eval_temp(config),
            await self._eval_wind(config),
            await self._eval_rain_sensor(config),
        ]
        would_skip = any(c["enabled"] and c["would_skip"] for c in checks)
        return {"would_skip": would_skip, "checks": checks}

    async def async_get_irrigation_outlook(self) -> dict:
        """Assemble the dashboard outlook: next runs + skip preview + last run.

        ``skip_preview`` is evaluated live (as of now — forecasts may change
        before the run). ``last_skip_evaluation`` is the persisted result of the
        most recent real scheduled-irrigate decision (None until one has run, or
        after a restart).
        """
        config = await self.store.async_get_config()
        skip_preview = await self.async_evaluate_skip_conditions()
        upcoming = await self.recurring_schedule_manager.async_get_upcoming_runs()
        try:
            # Served from the cache maintained by the update/calc cycles
            # (computed once on demand if no cycle has run yet).
            zone_estimates = await self.async_get_cached_zone_estimates()
        except Exception as e:  # noqa: BLE001 — outlook must not fail on the estimate
            _LOGGER.debug("Intra-day estimates unavailable: %s", e)
            zone_estimates = {}
        return {
            "weather_service_enabled": bool(
                config.get(
                    const.CONF_USE_WEATHER_SERVICE,
                    const.CONF_DEFAULT_USE_WEATHER_SERVICE,
                )
            ),
            "skip_preview": skip_preview,
            "last_skip_evaluation": getattr(self, "_last_skip_evaluation", None),
            "upcoming_runs": upcoming,
            "zone_estimates": zone_estimates,
        }

    async def _eval_precipitation(self, config) -> dict:
        """Structured precipitation-forecast guard (today+tomorrow vs threshold)."""
        threshold = config.get(
            const.CONF_PRECIPITATION_THRESHOLD_MM,
            const.CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM,
        )
        result = {
            "id": SKIP_PRECIPITATION,
            "enabled": bool(
                config.get(
                    const.CONF_SKIP_IRRIGATION_ON_PRECIPITATION,
                    const.CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION,
                )
            ),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": threshold,
        }
        if not result["enabled"]:
            return result
        use_weather_service = config.get(
            const.CONF_USE_WEATHER_SERVICE, const.CONF_DEFAULT_USE_WEATHER_SERVICE
        )
        if not use_weather_service or self._WeatherServiceClient is None:
            return result
        try:
            forecast_data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_forecast_data
            )
            if not forecast_data:
                return result
            days = max(
                1,
                config.get(
                    const.CONF_PRECIPITATION_FORECAST_DAYS,
                    const.CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS,
                ),
            )
            total = 0.0
            for day_data in forecast_data[:days]:
                if const.MAPPING_PRECIPITATION in day_data:
                    total += day_data[const.MAPPING_PRECIPITATION]
            result["available"] = True
            result["observed"] = round(total, 2)
            result["would_skip"] = total >= threshold
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: precipitation eval failed: %s", e)
        return result

    async def _eval_days_between(self, config) -> dict:
        """Structured days-between-irrigation guard (pure config math)."""
        days_between = config.get(
            const.CONF_DAYS_BETWEEN_IRRIGATION,
            const.CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
        )
        days_since = config.get(
            const.CONF_DAYS_SINCE_LAST_IRRIGATION,
            const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
        )
        enabled = days_between > 0
        return {
            "id": SKIP_DAYS_BETWEEN,
            "enabled": enabled,
            "would_skip": enabled and days_since < days_between,
            "available": True,
            "observed": days_since,
            "threshold": days_between,
        }

    async def _eval_temp(self, config) -> dict:
        """Structured low-temperature guard (current conditions)."""
        threshold = config.get(
            const.CONF_TEMP_THRESHOLD, const.CONF_DEFAULT_TEMP_THRESHOLD
        )
        result = {
            "id": SKIP_TEMPERATURE,
            "enabled": bool(
                config.get(
                    const.CONF_SKIP_TEMP_ENABLED, const.CONF_DEFAULT_SKIP_TEMP_ENABLED
                )
            ),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": threshold,
        }
        if not result["enabled"] or self._WeatherServiceClient is None:
            return result
        try:
            data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_data
            )
            temp = (data or {}).get(const.MAPPING_TEMPERATURE)
            if temp is not None:
                result["available"] = True
                result["observed"] = round(temp, 1)
                result["would_skip"] = temp < threshold
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: temperature eval failed: %s", e)
        return result

    async def _eval_wind(self, config) -> dict:
        """Structured high-wind guard (current conditions)."""
        threshold = config.get(
            const.CONF_WIND_THRESHOLD, const.CONF_DEFAULT_WIND_THRESHOLD
        )
        result = {
            "id": SKIP_WIND,
            "enabled": bool(
                config.get(
                    const.CONF_SKIP_WIND_ENABLED, const.CONF_DEFAULT_SKIP_WIND_ENABLED
                )
            ),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": threshold,
        }
        if not result["enabled"] or self._WeatherServiceClient is None:
            return result
        try:
            data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_data
            )
            wind = (data or {}).get(const.MAPPING_WINDSPEED)
            if wind is not None:
                result["available"] = True
                result["observed"] = round(wind, 2)
                result["would_skip"] = wind > threshold
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: wind eval failed: %s", e)
        return result

    async def _eval_rain_sensor(self, config) -> dict:
        """Structured rain-sensor guard (live HA entity state)."""
        sensor = config.get(const.CONF_RAIN_SENSOR, const.CONF_DEFAULT_RAIN_SENSOR)
        result = {
            "id": SKIP_RAIN_SENSOR,
            "enabled": bool(sensor),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": None,
            "entity_id": sensor or None,
        }
        if not sensor:
            return result
        state = self.hass.states.get(sensor)
        if state is None:
            return result
        result["available"] = True
        result["observed"] = state.state
        result["would_skip"] = state.state == "on"
        return result

    async def get_total_duration_all_enabled_zones(self):
        """Calculate the total duration for all enabled (automatic or manual) zones.

        Returns:
            int: The sum of durations for all enabled zones.

        """
        total_duration = 0
        zones = await self.store.async_get_zones()
        for zone in zones:
            if (
                zone.get(const.ZONE_STATE) == const.ZONE_STATE_AUTOMATIC
                or zone.get(const.ZONE_STATE) == const.ZONE_STATE_MANUAL
            ):
                total_duration += zone.get(const.ZONE_DURATION, 0)
        return total_duration

    async def get_total_irrigation_duration(self, zone_ids=None) -> int:
        """Estimate the wall-clock irrigation time (seconds) for the given zones.

        Sequencing-aware, used to anchor "finish at time" schedules:
          - parallel:              max(duration) — all valves run at once
          - sequential / rotating: sum(duration) — one after another
            (rotating's absorption gaps are intentionally not modelled; it is
            anchored as the sequential sum by design)

        ``zone_ids`` is an iterable of zone ids to include, or None/"all" for
        every enabled (automatic/manual) zone. Only zones with a positive
        duration count.
        """
        zones = await self.store.async_get_zones()
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}

        durations = []
        for zone in zones:
            if zone.get(const.ZONE_STATE) not in (
                const.ZONE_STATE_AUTOMATIC,
                const.ZONE_STATE_MANUAL,
            ):
                continue
            if target is not None and int(zone.get(const.ZONE_ID)) not in target:
                continue
            duration = zone.get(const.ZONE_DURATION, 0) or 0
            if duration > 0:
                durations.append(duration)

        if not durations:
            return 0

        if self.store.config.zone_sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL:
            return int(max(durations))
        return int(sum(durations))

    async def _check_precipitation_forecast(self) -> bool:
        """Check if precipitation is forecasted and should skip irrigation.

        Returns:
            bool: True if irrigation should be skipped due to precipitation, False otherwise.

        """
        config = await self.store.async_get_config()

        # Check if precipitation skip is enabled
        skip_on_precipitation = config.get(
            const.CONF_SKIP_IRRIGATION_ON_PRECIPITATION,
            const.CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION,
        )
        if not skip_on_precipitation:
            return False

        # Check if weather service is being used
        use_weather_service = config.get(
            const.CONF_USE_WEATHER_SERVICE, const.CONF_DEFAULT_USE_WEATHER_SERVICE
        )
        if not use_weather_service:
            _LOGGER.debug(
                "Weather service not enabled, cannot check precipitation forecast"
            )
            return False

        # Get precipitation threshold
        threshold_mm = config.get(
            const.CONF_PRECIPITATION_THRESHOLD_MM,
            const.CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM,
        )

        try:
            # Get weather service
            weather_service = config.get(
                const.CONF_WEATHER_SERVICE, const.CONF_DEFAULT_WEATHER_SERVICE
            )
            if weather_service is None:
                _LOGGER.debug("No weather service configured")
                return False

            weather_client = self._WeatherServiceClient

            if weather_client is None:
                _LOGGER.debug("Weather client not available")
                return False

            # Get forecast data (today and tomorrow)
            forecast_data = await self.hass.async_add_executor_job(
                weather_client.get_forecast_data
            )
            if not forecast_data:
                _LOGGER.debug("No forecast data available")
                return False

            # Sum precipitation across the configured look-ahead window. Weather
            # clients return future days only (today excluded), so days=1 means
            # the next forecast day.
            days = max(
                1,
                config.get(
                    const.CONF_PRECIPITATION_FORECAST_DAYS,
                    const.CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS,
                ),
            )
            total_precipitation = 0.0
            for day_data in forecast_data[:days]:
                if const.MAPPING_PRECIPITATION in day_data:
                    total_precipitation += day_data[const.MAPPING_PRECIPITATION]

            _LOGGER.debug(
                "Forecast precipitation: %.1f mm (threshold: %.1f mm)",
                total_precipitation,
                threshold_mm,
            )

            if total_precipitation >= threshold_mm:
                _LOGGER.info(
                    "Skipping irrigation due to forecasted precipitation: %.1f mm (threshold: %.1f mm)",
                    total_precipitation,
                    threshold_mm,
                )
                return True

        except Exception as e:
            _LOGGER.warning("Error checking precipitation forecast: %s", e)

        return False

    async def _check_days_between_irrigation(self) -> bool:
        """Check if enough days have passed since the last irrigation event.

        Returns:
            bool: True if irrigation should be skipped due to insufficient days passed, False otherwise.
        """
        config = await self.store.async_get_config()

        # Get the configured minimum days between irrigation
        days_between = config.get(
            const.CONF_DAYS_BETWEEN_IRRIGATION,
            const.CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
        )

        # If days_between is 0, no restriction (always allow irrigation)
        if days_between <= 0:
            return False

        # Get days since last irrigation
        days_since_last = config.get(
            const.CONF_DAYS_SINCE_LAST_IRRIGATION,
            const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
        )

        if days_since_last < days_between:
            _LOGGER.info(
                "Skipping irrigation: only %d days since last irrigation, need %d days minimum",
                days_since_last,
                days_between,
            )
            return True

        return False

    async def _check_temp_threshold(self) -> bool:
        """Return True if temperature is below the configured threshold (skip irrigation)."""
        config = await self.store.async_get_config()
        if not config.get(
            const.CONF_SKIP_TEMP_ENABLED, const.CONF_DEFAULT_SKIP_TEMP_ENABLED
        ):
            return False
        threshold = config.get(
            const.CONF_TEMP_THRESHOLD, const.CONF_DEFAULT_TEMP_THRESHOLD
        )
        if self._WeatherServiceClient is None:
            _LOGGER.debug("No weather client — skipping temperature check")
            return False
        try:
            data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_data
            )
            if not data:
                return False
            temp = data.get(const.MAPPING_TEMPERATURE)
            if temp is None:
                return False
            if temp < threshold:
                _LOGGER.info(
                    "Skipping irrigation: temperature %.1f°C < threshold %.1f°C",
                    temp,
                    threshold,
                )
                return True
        except Exception as e:
            _LOGGER.warning("Error checking temperature threshold: %s", e)
        return False

    async def _check_wind_threshold(self) -> bool:
        """Return True if wind speed is above the configured threshold (skip irrigation)."""
        config = await self.store.async_get_config()
        if not config.get(
            const.CONF_SKIP_WIND_ENABLED, const.CONF_DEFAULT_SKIP_WIND_ENABLED
        ):
            return False
        threshold = config.get(
            const.CONF_WIND_THRESHOLD, const.CONF_DEFAULT_WIND_THRESHOLD
        )
        if self._WeatherServiceClient is None:
            _LOGGER.debug("No weather client — skipping wind check")
            return False
        try:
            data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_data
            )
            if not data:
                return False
            wind = data.get(const.MAPPING_WINDSPEED)
            if wind is None:
                return False
            if wind > threshold:
                _LOGGER.info(
                    "Skipping irrigation: wind %.2f m/s > threshold %.2f m/s",
                    wind,
                    threshold,
                )
                return True
        except Exception as e:
            _LOGGER.warning("Error checking wind threshold: %s", e)
        return False

    async def _check_rain_sensor(self) -> bool:
        """Return True if the configured rain sensor reports rain (skip irrigation)."""
        config = await self.store.async_get_config()
        rain_sensor = config.get(const.CONF_RAIN_SENSOR, const.CONF_DEFAULT_RAIN_SENSOR)
        if not rain_sensor:
            return False
        state = self.hass.states.get(rain_sensor)
        if state is None:
            _LOGGER.warning(
                "Rain sensor entity '%s' not found in HA states", rain_sensor
            )
            return False
        if state.state == "on":
            _LOGGER.info("Skipping irrigation: rain sensor '%s' is on", rain_sensor)
            return True
        return False

    async def _increment_days_since_irrigation(self):
        """Increment the counter for days since last irrigation."""
        config = await self.store.async_get_config()
        current_days = config.get(
            const.CONF_DAYS_SINCE_LAST_IRRIGATION,
            const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
        )

        new_days = current_days + 1
        await self.store.async_update_config(
            {const.CONF_DAYS_SINCE_LAST_IRRIGATION: new_days}
        )

        _LOGGER.debug("Incremented days since last irrigation to %d", new_days)

    async def _reset_days_since_irrigation(self):
        """Reset the counter for days since last irrigation to 0."""
        await self.store.async_update_config({const.CONF_DAYS_SINCE_LAST_IRRIGATION: 0})

        _LOGGER.debug("Reset days since last irrigation to 0")
