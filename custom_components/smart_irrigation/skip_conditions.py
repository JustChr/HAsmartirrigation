"""Irrigation skip-condition checks and days-between tracking.

Extracted from __init__.py (Phase C5). Methods live on a mixin the coordinator
inherits; bodies unchanged (still use ``self``). Covers the pre-irrigation
decision logic: skip on precipitation forecast / temperature / wind / rain
sensor, the days-between-irrigation counter, and the total-duration query used
by the scheduler and websockets.
"""

import logging

from . import const

_LOGGER = logging.getLogger(__name__)


class SkipConditionsMixin:
    """Skip-condition checks for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    async def _check_skip_conditions(self) -> bool:
        """Return True if irrigation should be skipped (any condition is met)."""
        if await self._check_precipitation_forecast():
            _LOGGER.info("Irrigation skipped: forecasted precipitation")
            return True
        if await self._check_days_between_irrigation():
            _LOGGER.info("Irrigation skipped: insufficient days since last irrigation")
            return True
        if await self._check_temp_threshold():
            return True
        if await self._check_wind_threshold():
            return True
        return bool(await self._check_rain_sensor())

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

            # Check precipitation for today and tomorrow
            total_precipitation = 0.0
            for day_data in forecast_data[:2]:  # Check today and tomorrow only
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
