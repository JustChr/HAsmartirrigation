"""Websocket and HTTP API views for Smart Irrigation integration."""

import datetime
import logging

import voluptuous as vol
from dateutil import parser as dateutil_parser
from homeassistant.components import websocket_api
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.components.websocket_api import (
    async_register_command,
    async_response,
    decorators,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .const import SmartIrrigationError
from .helpers import CannotConnect, InvalidAuth, validate_api_key

_LOGGER = logging.getLogger(__name__)


def _safe_parse_datetime(value):
    """Safely parse a datetime value, returning datetime.min as fallback."""
    if isinstance(value, datetime.datetime):
        # Convert timezone-aware datetime to naive UTC for consistent comparison
        if value.tzinfo is not None:
            return value.astimezone(datetime.UTC).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        try:
            parsed = dateutil_parser.isoparse(value)
            # Convert timezone-aware datetime to naive UTC for consistent comparison
            if parsed.tzinfo is not None:
                return parsed.astimezone(datetime.UTC).replace(tzinfo=None)
            return parsed
        except (ValueError, TypeError):
            _LOGGER.warning("Failed to parse datetime string: %s", value)
            return datetime.datetime.min
    return datetime.datetime.min


@decorators.websocket_command(
    {
        vol.Required("type"): const.DOMAIN + "_config_updated",
    }
)
@decorators.async_response
async def handle_subscribe_updates(hass: HomeAssistant, connection, msg):
    """Handle subscribe updates."""

    @callback
    def async_handle_event():
        """Forward events to websocket."""
        connection.send_message(
            {
                "id": msg["id"],
                "type": "event",
            }
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, const.DOMAIN + "_update_frontend", async_handle_event
    )
    connection.send_result(msg["id"])


class SmartIrrigationConfigView(HomeAssistantView):
    """View to handle Smart Irrigation configuration updates via HTTP API."""

    url = "/api/" + const.DOMAIN + "/config"
    name = "api:" + const.DOMAIN + ":config"

    @RequestDataValidator(
        vol.Schema(
            {
                vol.Optional(const.CONF_CALC_TIME): cv.string,
                vol.Optional(const.CONF_UNITS): cv.string,
                vol.Optional(const.CONF_AUTO_CALC_ENABLED): cv.boolean,
                vol.Optional(const.CONF_AUTO_UPDATE_ENABLED): cv.boolean,
                vol.Optional(const.CONF_AUTO_UPDATE_SCHEDULE): cv.string,
                vol.Optional(const.CONF_AUTO_UPDATE_DELAY): cv.string,
                vol.Optional(const.CONF_AUTO_UPDATE_INTERVAL): cv.string,
                vol.Optional(const.CONF_USE_WEATHER_SERVICE): cv.boolean,
                vol.Optional(const.CONF_WEATHER_SERVICE): cv.string,
                vol.Optional(const.CONF_IRRIGATION_START_TRIGGERS): vol.Coerce(list),
                vol.Optional(const.CONF_SKIP_IRRIGATION_ON_PRECIPITATION): cv.boolean,
                vol.Optional(const.CONF_PRECIPITATION_THRESHOLD_MM): vol.Coerce(float),
                vol.Optional(const.CONF_PRECIPITATION_FORECAST_DAYS): vol.Coerce(int),
                vol.Optional(const.CONF_DAYS_BETWEEN_IRRIGATION): vol.Coerce(int),
                vol.Optional(const.CONF_SKIP_TEMP_ENABLED): cv.boolean,
                vol.Optional(const.CONF_TEMP_THRESHOLD): vol.Coerce(float),
                vol.Optional(const.CONF_SKIP_WIND_ENABLED): cv.boolean,
                vol.Optional(const.CONF_WIND_THRESHOLD): vol.Coerce(float),
                vol.Optional(const.CONF_SKIP_FREEZE_ENABLED): cv.boolean,
                vol.Optional(const.CONF_FREEZE_THRESHOLD): vol.Coerce(float),
                vol.Optional(const.CONF_RAIN_SENSOR): vol.Or(str, None),
                vol.Optional(const.CONF_ZONE_SEQUENCING): cv.string,
                vol.Optional(
                    const.CONF_ZONE_SEQUENCING_MAX_CONSECUTIVE_DURATION
                ): vol.Coerce(int),
                vol.Optional(
                    const.CONF_ZONE_SEQUENCING_MIN_ABSORPTION_TIME
                ): vol.Coerce(int),
                vol.Optional(const.CONF_FORECAST_WEIGHTING_ENABLED): cv.boolean,
                vol.Optional(const.CONF_OBSERVED_WATERING_ENABLED): cv.boolean,
                vol.Optional(const.CONF_LIVE_ESTIMATE_ENABLED): cv.boolean,
                vol.Optional(const.CONF_RAIN_DELAY_UNTIL): vol.Or(str, None),
                vol.Optional(const.CONF_MANUAL_COORDINATES_ENABLED): cv.boolean,
                vol.Optional(const.CONF_MANUAL_LATITUDE): vol.Or(float, int, None),
                vol.Optional(const.CONF_MANUAL_LONGITUDE): vol.Or(float, int, None),
                vol.Optional(const.CONF_MANUAL_ELEVATION): vol.Or(float, int, None),
            },
            extra=vol.ALLOW_EXTRA,
        )
    )
    async def post(self, request, data):
        """Handle config update request."""
        _LOGGER.debug("[websocket]: request: %s %s", request, data)
        hass = request.app["hass"]
        coordinator = hass.data[const.DOMAIN]["coordinator"]
        await coordinator.async_update_config(data)
        async_dispatcher_send(hass, const.DOMAIN + "_update_frontend")
        return self.json({"success": True})


class SmartIrrigationModuleView(HomeAssistantView):
    """View to handle Smart Irrigation module configuration via HTTP API."""

    url = "/api/" + const.DOMAIN + "/modules"
    name = "api:" + const.DOMAIN + ":modules"

    @RequestDataValidator(
        vol.Schema(
            {
                vol.Optional(const.MODULE_ID): vol.Coerce(int),
                vol.Optional(const.MODULE_NAME): cv.string,
                vol.Optional(const.MODULE_DESCRIPTION): vol.Or(None, cv.string),
                vol.Optional(const.MODULE_CONFIG): vol.Coerce(dict),
                vol.Optional(const.MODULE_SCHEMA): vol.Coerce(list),
                vol.Optional(const.ATTR_REMOVE): cv.boolean,
            },
        )
    )
    async def post(self, request, data):
        """Handle config update request."""
        _LOGGER.debug("[websocket]: request: %s %s", request, data)
        hass = request.app["hass"]
        coordinator = hass.data[const.DOMAIN]["coordinator"]
        module = int(data[const.MODULE_ID]) if const.MODULE_ID in data else None
        result = await coordinator.async_update_module_config(module, data)
        async_dispatcher_send(hass, const.DOMAIN + "_update_frontend")
        response = {"success": True}
        if isinstance(result, dict) and result.get(const.MODULE_ID) is not None:
            response["id"] = result[const.MODULE_ID]
        return self.json(response)


class SmartIrrigationAllModuleView(HomeAssistantView):
    """View to handle retrieval of all Smart Irrigation modules via HTTP API."""

    url = "/api/" + const.DOMAIN + "/allmodules"
    name = "api:" + const.DOMAIN + ":allmodules"


class SmartIrrigationMappingView(HomeAssistantView):
    """View to handle Smart Irrigation mapping configuration via HTTP API."""

    url = "/api/" + const.DOMAIN + "/mappings"
    name = "api:" + const.DOMAIN + ":mapping"

    @RequestDataValidator(
        vol.Schema(
            {
                vol.Optional(const.MAPPING_ID): vol.Coerce(int),
                vol.Optional(const.MAPPING_NAME): cv.string,
                vol.Optional(const.MAPPING_MAPPINGS): vol.Coerce(dict),
                vol.Optional(const.ATTR_REMOVE): cv.boolean,
                # Accept but ignore server-computed fields so older frontends
                # don't fail schema validation; they are stripped below.
                vol.Optional(const.MAPPING_DATA): object,
                vol.Optional(const.MAPPING_DATA_LAST_UPDATED): object,
                vol.Optional(const.MAPPING_DATA_LAST_ENTRY): object,
                vol.Optional(const.MAPPING_DATA_LAST_CALCULATION): object,
            }
        )
    )
    async def post(self, request, data):
        """Handle config update request."""
        _LOGGER.debug("[websocket]: request: %s %s", request, data)
        hass = request.app["hass"]
        coordinator = hass.data[const.DOMAIN]["coordinator"]
        mapping = int(data[const.MAPPING_ID]) if const.MAPPING_ID in data else None
        sanitized = {
            key: value
            for key, value in data.items()
            if key
            not in (
                const.MAPPING_DATA,
                const.MAPPING_DATA_LAST_UPDATED,
                const.MAPPING_DATA_LAST_ENTRY,
                const.MAPPING_DATA_LAST_CALCULATION,
            )
        }
        result = await coordinator.async_update_mapping_config(mapping, sanitized)
        async_dispatcher_send(hass, const.DOMAIN + "_update_frontend")
        response = {"success": True}
        if isinstance(result, dict) and result.get(const.MAPPING_ID) is not None:
            response["id"] = result[const.MAPPING_ID]
        return self.json(response)


class SmartIrrigationZoneView(HomeAssistantView):
    """View to handle Smart Irrigation zone configuration via HTTP API."""

    url = "/api/" + const.DOMAIN + "/zones"
    name = "api:" + const.DOMAIN + ":zones"

    @RequestDataValidator(
        vol.Schema(
            {
                vol.Optional(const.ZONE_ID): vol.Coerce(int),
                vol.Optional(const.ZONE_NAME): cv.string,
                vol.Optional(const.ZONE_SIZE): cv.positive_float,
                vol.Optional(const.ZONE_THROUGHPUT): cv.positive_float,
                vol.Optional(const.ZONE_STATE): vol.In(const.ZONE_STATES),
                vol.Optional(const.ZONE_DURATION): vol.Or(float, int, str, None),
                vol.Optional(const.ZONE_BUCKET): vol.Or(float, int, str, None),
                vol.Optional(const.ZONE_DELTA): vol.Or(float, int, str, None),
                vol.Optional(const.ZONE_MODULE): vol.Or(int, str, None),
                vol.Optional(const.ATTR_REMOVE): cv.boolean,
                vol.Optional(const.ATTR_CALCULATE): cv.boolean,
                vol.Optional(const.ATTR_CALCULATE_ALL): cv.boolean,
                vol.Optional(const.ATTR_UPDATE): cv.boolean,
                vol.Optional(const.ATTR_UPDATE_ALL): cv.boolean,
                vol.Optional(const.ATTR_RESET_ALL_BUCKETS): cv.boolean,
                vol.Optional(const.ATTR_OVERRIDE_CACHE): cv.boolean,
                vol.Optional(const.ZONE_EXPLANATION): vol.Coerce(str),
                vol.Optional(const.ZONE_MULTIPLIER): vol.Coerce(float),
                vol.Optional(const.ZONE_MAPPING): vol.Or(int, str, None),
                vol.Optional(const.ZONE_LEAD_TIME): vol.Coerce(float),
                vol.Optional(const.ZONE_MAXIMUM_DURATION): vol.Coerce(float),
                vol.Optional(const.ZONE_MAXIMUM_BUCKET): vol.Or(float, int, None),
                vol.Optional(const.ZONE_LAST_CALCULATED): vol.Or(
                    None, str, datetime.datetime
                ),
                vol.Optional(const.ZONE_LAST_UPDATED): vol.Or(
                    None, str, datetime.datetime
                ),
                vol.Optional(const.ZONE_NUMBER_OF_DATA_POINTS): vol.Or(int, None),
                vol.Optional(const.ATTR_CLEAR_ALL_WEATHERDATA): cv.boolean,
                vol.Optional(const.ZONE_DRAINAGE_RATE): vol.Or(float, int, None),
                vol.Optional(const.ZONE_CURRENT_DRAINAGE): vol.Or(float, int, None),
                vol.Optional(const.ZONE_KC): vol.Or(float, int, None),
                vol.Optional(const.ZONE_PLANT_TYPE): vol.Or(str, None),
                vol.Optional(const.ZONE_LINKED_ENTITY): vol.Or(str, None),
                vol.Optional(const.ZONE_BUCKET_THRESHOLD): vol.Or(float, int, None),
                vol.Optional(const.ZONE_FLOW_SENSOR): vol.Or(str, None),
            },
            extra=vol.ALLOW_EXTRA,
        )
    )
    async def post(self, request, data):
        """Handle config update request."""
        _LOGGER.debug("[websocket]: request: %s %s", request, data)
        hass = request.app["hass"]
        coordinator = hass.data[const.DOMAIN]["coordinator"]
        zone = int(data[const.ZONE_ID]) if const.ZONE_ID in data else None
        try:
            await coordinator.async_update_zone_config(zone, data)
        except SmartIrrigationError as err:
            _LOGGER.warning("[zone POST] Rejected: %s", err)
            return self.json({"success": False, "message": str(err)}, status_code=400)
        async_dispatcher_send(hass, const.DOMAIN + "_update_frontend")
        return self.json({"success": True})


@async_response
async def websocket_get_config(hass: HomeAssistant, connection, msg):
    """Publish config data."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    config = await coordinator.store.async_get_config()

    # Convert precipitation threshold from internal mm to user's preferred units
    if (
        const.CONF_PRECIPITATION_THRESHOLD_MM in config
        and config[const.CONF_PRECIPITATION_THRESHOLD_MM] is not None
    ):
        threshold_mm = config[const.CONF_PRECIPITATION_THRESHOLD_MM]
        ha_config_is_metric = hass.config.units is METRIC_SYSTEM

        if not ha_config_is_metric:
            # Convert from mm to inches for imperial users
            from .helpers import convert_between

            threshold_inches = convert_between(
                const.UNIT_MM, const.UNIT_INCH, threshold_mm
            )
            config = config.copy()  # Make a copy to avoid modifying the stored config
            config[const.CONF_PRECIPITATION_THRESHOLD_MM] = threshold_inches
            _LOGGER.debug(
                "Converted precipitation threshold from %.2f mm to %.2f inches for frontend (imperial mode)",
                threshold_mm,
                threshold_inches,
            )
        else:
            _LOGGER.debug(
                "Precipitation threshold %.2f mm sent directly to frontend (metric mode)",
                threshold_mm,
            )

    connection.send_result(msg["id"], config)


@async_response
async def websocket_get_zones(hass: HomeAssistant, connection, msg):
    """Publish zone data."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    zones = await coordinator.store.async_get_zones()
    connection.send_result(msg["id"], zones)


@async_response
async def websocket_get_modules(hass: HomeAssistant, connection, msg):
    """Publish module data."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    modules = await coordinator.store.async_get_modules()
    connection.send_result(msg["id"], modules)


@async_response
async def websocket_get_all_modules(hass: HomeAssistant, connection, msg):
    """Publish all module data. This is not retrieved from the store."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    modules = await coordinator.async_get_all_modules()
    connection.send_result(msg["id"], modules)


@async_response
async def websocket_get_mappings(hass: HomeAssistant, connection, msg):
    """Publish mapping data."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    _LOGGER.debug("websocket_get_mappings called")
    mappings = await coordinator.store.async_get_mappings()
    connection.send_result(msg["id"], mappings)


@async_response
async def websocket_get_weather_records(hass: HomeAssistant, connection, msg):
    """Publish weather records for a mapping."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    mapping_id = msg.get("mapping_id")
    limit = msg.get("limit", 10)

    _LOGGER.debug(
        "websocket_get_weather_records called for mapping %s with limit %s",
        mapping_id,
        limit,
    )

    try:
        # Get the mapping from the store
        mapping = coordinator.store.get_mapping(int(mapping_id))

        if not mapping:
            _LOGGER.warning("Mapping with ID %s not found", mapping_id)
            connection.send_result(msg["id"], [])
            return

        # Get weather data from the mapping
        mapping_data = mapping.get(const.MAPPING_DATA, [])

        if not mapping_data or not isinstance(mapping_data, list):
            _LOGGER.debug("No weather data found for mapping %s", mapping_id)
            connection.send_result(msg["id"], [])
            return

        # Process and format the weather records
        records = []
        # Remove all non-dicts
        mapping_data = [d for d in mapping_data if isinstance(d, dict)]

        # Sort by timestamp (most recent first) and limit
        sorted_data = sorted(
            mapping_data,
            key=lambda x: _safe_parse_datetime(x.get(const.RETRIEVED_AT)),
            reverse=True,
        )
        limited_data = sorted_data if limit == 0 else sorted_data[:limit]

        for data_point in limited_data:
            if not isinstance(data_point, dict):
                continue

            retrieval_time = data_point.get(const.RETRIEVED_AT)
            observation_time = data_point.get(const.OBSERVATION_TIME)

            def _to_iso(val):
                if isinstance(val, datetime.datetime):
                    return val.isoformat()
                if isinstance(val, str):
                    return val
                return None

            # "timestamp" = when the station measured it (API dt); falls back to retrieval time
            timestamp_str = _to_iso(observation_time) or _to_iso(retrieval_time)
            retrieval_time_str = _to_iso(retrieval_time)

            # Extract weather values
            record = {
                "timestamp": timestamp_str,
                "temperature": data_point.get(const.MAPPING_TEMPERATURE),
                "humidity": data_point.get(const.MAPPING_HUMIDITY),
                "precipitation": data_point.get(const.MAPPING_PRECIPITATION),
                "pressure": data_point.get(const.MAPPING_PRESSURE),
                "wind_speed": data_point.get(const.MAPPING_WINDSPEED),
                "solar_radiation": data_point.get(const.MAPPING_SOLRAD),
                "dewpoint": data_point.get(const.MAPPING_DEWPOINT),
                "evapotranspiration": data_point.get(const.MAPPING_EVAPOTRANSPIRATION),
                "max_temperature": data_point.get(const.MAPPING_MAX_TEMP),
                "min_temperature": data_point.get(const.MAPPING_MIN_TEMP),
                "current_precipitation": data_point.get(
                    const.MAPPING_CURRENT_PRECIPITATION
                ),
                "retrieval_time": retrieval_time_str,
            }

            # Only include records that have at least some weather data
            if any(
                value is not None
                for key, value in record.items()
                if key not in ["timestamp", "retrieval_time"]
            ):
                records.append(record)

        _LOGGER.debug(
            "Retrieved %d weather records for mapping %s", len(records), mapping_id
        )

    except Exception as e:
        _LOGGER.error(
            "Error retrieving weather records for mapping %s: %s", mapping_id, e
        )
        records = []
    connection.send_result(msg["id"], records)


@async_response
async def websocket_get_watering_calendar(hass: HomeAssistant, connection, msg):
    """Get 12-month watering calendar for zone(s)."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    zone_id = msg.get("zone_id")

    _LOGGER.debug("websocket_get_watering_calendar called for zone %s", zone_id)
    try:
        # Convert zone_id to int if provided
        if zone_id is not None:
            zone_id = int(zone_id)

        calendar_data = await coordinator.async_generate_watering_calendar(zone_id)
        connection.send_result(msg["id"], calendar_data)

    except Exception as e:
        _LOGGER.error("Error generating watering calendar for zone %s: %s", zone_id, e)
        connection.send_error(msg["id"], "calendar_generation_failed", str(e))


class SmartIrrigationWateringCalendarView(HomeAssistantView):
    """View to handle watering calendar requests via HTTP API."""

    url = "/api/" + const.DOMAIN + "/watering_calendar"
    name = "api:" + const.DOMAIN + ":watering_calendar"

    async def get(self, request):
        """Handle watering calendar request."""
        hass = request.app["hass"]
        coordinator = hass.data[const.DOMAIN]["coordinator"]

        # Get zone_id from query parameters
        zone_id = request.query.get("zone_id")

        _LOGGER.debug("HTTP watering calendar request for zone %s", zone_id)

        try:
            # Convert zone_id to int if provided
            if zone_id is not None:
                zone_id = int(zone_id)

            calendar_data = await coordinator.async_generate_watering_calendar(zone_id)
            return self.json(calendar_data)

        except Exception as e:
            _LOGGER.error(
                "Error generating watering calendar for zone %s: %s", zone_id, e
            )
            return self.json({"error": str(e)}, status_code=500)


@async_response
async def websocket_get_schedules(hass: HomeAssistant, connection, msg):
    """Return all recurring schedules."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    schedules = coordinator.recurring_schedule_manager.get_schedules()
    connection.send_result(msg["id"], schedules)


@async_response
async def websocket_save_schedule(hass: HomeAssistant, connection, msg):
    """Create or update a recurring schedule."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    schedule_data = dict(msg.get("schedule", {}))
    schedule_id = schedule_data.get(const.SCHEDULE_CONF_ID)
    try:
        if schedule_id:
            await coordinator.recurring_schedule_manager.async_update_schedule(
                schedule_id, schedule_data
            )
        else:
            await coordinator.recurring_schedule_manager.async_create_schedule(
                schedule_data
            )
        connection.send_result(msg["id"], {"success": True})
    except Exception as e:
        _LOGGER.error("Error saving schedule: %s", e)
        connection.send_result(msg["id"], {"success": False, "error": str(e)})


@async_response
async def websocket_delete_schedule(hass: HomeAssistant, connection, msg):
    """Delete a recurring schedule by id."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    schedule_id = msg.get("schedule_id")
    try:
        await coordinator.recurring_schedule_manager.async_delete_schedule(schedule_id)
        connection.send_result(msg["id"], {"success": True})
    except Exception as e:
        _LOGGER.error("Error deleting schedule: %s", e)
        connection.send_result(msg["id"], {"success": False, "error": str(e)})


@async_response
async def websocket_get_irrigation_outlook(hass: HomeAssistant, connection, msg):
    """Return the dashboard irrigation outlook: upcoming runs + skip preview."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    try:
        outlook = await coordinator.async_get_irrigation_outlook()
        connection.send_result(msg["id"], outlook)
    except Exception as e:
        _LOGGER.error("Error building irrigation outlook: %s", e)
        connection.send_result(
            msg["id"],
            {
                "weather_service_enabled": False,
                "skip_preview": {"would_skip": False, "checks": []},
                "last_skip_evaluation": None,
                "upcoming_runs": [],
            },
        )


@async_response
async def websocket_irrigate_now(hass: HomeAssistant, connection, msg):
    """Trigger immediate irrigation for all zones or a single zone, bypassing skip conditions."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    zone_id = msg.get("zone_id")
    try:
        await coordinator.async_irrigate_now(zone_id=zone_id)
        connection.send_result(msg["id"], {"success": True})
    except Exception as e:
        _LOGGER.error("Error triggering irrigate now: %s", e)
        connection.send_result(msg["id"], {"success": False, "error": str(e)})


@async_response
async def websocket_run_zone(hass: HomeAssistant, connection, msg):
    """Run a single zone for a custom duration (minutes), bypassing the calc."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    try:
        await coordinator.async_run_zone(msg["zone_id"], float(msg["duration"]))
        connection.send_result(msg["id"], {"success": True})
    except Exception as e:
        _LOGGER.error("Error running zone: %s", e)
        connection.send_result(msg["id"], {"success": False, "error": str(e)})


@async_response
async def websocket_stop_zone(hass: HomeAssistant, connection, msg):
    """Stop an in-progress run for a single zone immediately."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    try:
        await coordinator.async_stop_zone(msg["zone_id"])
        connection.send_result(msg["id"], {"success": True})
    except Exception as e:
        _LOGGER.error("Error stopping zone: %s", e)
        connection.send_result(msg["id"], {"success": False, "error": str(e)})


@async_response
async def websocket_set_rain_delay(hass: HomeAssistant, connection, msg):
    """Pause automatic irrigation: for ``hours`` from now, or until ``until``."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    try:
        if msg.get("hours") is not None:
            await coordinator.async_delay_hours(float(msg["hours"]))
        elif msg.get("until") is not None:
            await coordinator.async_set_rain_delay(str(msg["until"]))
        else:
            await coordinator.async_clear_rain_delay()
        connection.send_result(msg["id"], {"success": True})
    except Exception as e:
        _LOGGER.error("Error setting rain delay: %s", e)
        connection.send_result(msg["id"], {"success": False, "error": str(e)})


@async_response
async def websocket_clear_rain_delay(hass: HomeAssistant, connection, msg):
    """Resume automatic irrigation (clear any active rain delay)."""
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    try:
        await coordinator.async_clear_rain_delay()
        connection.send_result(msg["id"], {"success": True})
    except Exception as e:
        _LOGGER.error("Error clearing rain delay: %s", e)
        connection.send_result(msg["id"], {"success": False, "error": str(e)})


@async_response
async def websocket_get_weather_config(hass: HomeAssistant, connection, msg):
    """Return the current weather service configuration (without exposing the API key)."""
    use_weather_service = hass.data[const.DOMAIN].get(
        const.CONF_USE_WEATHER_SERVICE, False
    )
    weather_service = hass.data[const.DOMAIN].get(const.CONF_WEATHER_SERVICE)
    # Report per-service configured status so the frontend can show the right badge
    has_owm_api_key = bool(
        hass.data[const.DOMAIN].get(const.CONF_OWM_API_KEY)
        # also accept legacy slot as fallback during migration
        or (
            weather_service == const.CONF_WEATHER_SERVICE_OWM
            and hass.data[const.DOMAIN].get(const.CONF_WEATHER_SERVICE_API_KEY)
        )
    )
    has_pw_api_key = bool(
        hass.data[const.DOMAIN].get(const.CONF_PW_API_KEY)
        or (
            weather_service == const.CONF_WEATHER_SERVICE_PW
            and hass.data[const.DOMAIN].get(const.CONF_WEATHER_SERVICE_API_KEY)
        )
    )
    has_met_api_key = bool(
        hass.data[const.DOMAIN].get(const.CONF_MET_API_KEY)
        or (
            weather_service == const.CONF_WEATHER_SERVICE_MET
            and hass.data[const.DOMAIN].get(const.CONF_WEATHER_SERVICE_API_KEY)
        )
    )
    connection.send_result(
        msg["id"],
        {
            "use_weather_service": use_weather_service,
            "weather_service": weather_service,
            "has_owm_api_key": has_owm_api_key,
            "has_pw_api_key": has_pw_api_key,
            "has_met_api_key": has_met_api_key,
            "available_services": const.CONF_WEATHER_SERVICES,
            "no_api_key_services": const.CONF_WEATHER_SERVICES_NO_API_KEY,
        },
    )


@async_response
async def websocket_test_weather_config(hass: HomeAssistant, connection, msg):
    """Test the weather service API key without saving it."""
    weather_service = msg.get("weather_service")
    api_key = msg.get("api_key") or None

    # Fall back to the per-service stored key when the caller doesn't supply one
    if not api_key:
        if weather_service == const.CONF_WEATHER_SERVICE_OWM:
            api_key = hass.data[const.DOMAIN].get(const.CONF_OWM_API_KEY) or hass.data[
                const.DOMAIN
            ].get(const.CONF_WEATHER_SERVICE_API_KEY)
        elif weather_service == const.CONF_WEATHER_SERVICE_PW:
            api_key = hass.data[const.DOMAIN].get(const.CONF_PW_API_KEY) or hass.data[
                const.DOMAIN
            ].get(const.CONF_WEATHER_SERVICE_API_KEY)
        elif weather_service == const.CONF_WEATHER_SERVICE_MET:
            api_key = hass.data[const.DOMAIN].get(const.CONF_MET_API_KEY) or hass.data[
                const.DOMAIN
            ].get(const.CONF_WEATHER_SERVICE_API_KEY)

    if not weather_service:
        connection.send_result(msg["id"], {"success": False, "error": "no_service"})
        return

    try:
        await validate_api_key(hass, weather_service, api_key)
        connection.send_result(msg["id"], {"success": True})
    except InvalidAuth:
        connection.send_result(msg["id"], {"success": False, "error": "invalid_auth"})
    except CannotConnect:
        connection.send_result(msg["id"], {"success": False, "error": "cannot_connect"})
    except Exception as exc:  # noqa: BLE001
        _LOGGER.warning("Weather config test failed: %s", exc)
        connection.send_result(msg["id"], {"success": False, "error": "unknown"})


@async_response
async def websocket_save_weather_config(hass: HomeAssistant, connection, msg):
    """Save weather service configuration to config entry options and in-memory state."""
    use_weather_service: bool = msg["use_weather_service"]
    weather_service: str | None = msg.get("weather_service")
    api_key: str | None = msg.get("api_key") or None

    # Map the selected service to its per-service key constant
    _service_key_map = {
        const.CONF_WEATHER_SERVICE_OWM: const.CONF_OWM_API_KEY,
        const.CONF_WEATHER_SERVICE_PW: const.CONF_PW_API_KEY,
        const.CONF_WEATHER_SERVICE_MET: const.CONF_MET_API_KEY,
    }
    service_key_const = (
        _service_key_map.get(weather_service) if weather_service else None
    )

    # Update in-memory state immediately
    hass.data[const.DOMAIN][const.CONF_USE_WEATHER_SERVICE] = use_weather_service
    if use_weather_service and weather_service:
        hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE] = weather_service
        if api_key and service_key_const:
            hass.data[const.DOMAIN][service_key_const] = api_key.strip()
    elif not use_weather_service:
        hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE] = None

    # Persist to config entry options so settings survive HA restarts
    entry = hass.data[const.DOMAIN].get("entry")
    if entry is not None:
        new_options = dict(entry.options)
        new_options[const.CONF_USE_WEATHER_SERVICE] = use_weather_service
        if use_weather_service and weather_service:
            new_options[const.CONF_WEATHER_SERVICE] = weather_service
            if api_key and service_key_const:
                new_options[service_key_const] = api_key.strip()
        elif not use_weather_service:
            new_options[const.CONF_WEATHER_SERVICE] = None
        hass.config_entries.async_update_entry(entry, options=new_options)

    # Also update store config for use_weather_service flag
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    await coordinator.store.async_update_config(
        {
            const.CONF_USE_WEATHER_SERVICE: use_weather_service,
            const.CONF_WEATHER_SERVICE: (
                weather_service if use_weather_service else None
            ),
        }
    )

    async_dispatcher_send(hass, const.DOMAIN + "_config_updated")
    connection.send_result(msg["id"], {"success": True})


@async_response
async def websocket_get_coordinates(hass: HomeAssistant, connection, msg):
    """Return the configured manual coordinates plus HA's coordinates for display.

    Manual coordinates are the source of truth in the config-entry options (read
    by the coordinator at setup); this exposes them to the panel so the Location
    card can show + edit the same values the calculation actually uses.
    """
    entry = hass.data[const.DOMAIN].get("entry")
    options = dict(entry.options) if entry is not None else {}
    data = dict(entry.data) if entry is not None else {}

    def _resolve(key, default=None):
        # options win over entry.data (matches resolve_weather_config precedence)
        if key in options:
            return options.get(key)
        if key in data:
            return data.get(key)
        return default

    ha = hass.config.as_dict()
    connection.send_result(
        msg["id"],
        {
            "manual_coordinates_enabled": bool(
                _resolve(const.CONF_MANUAL_COORDINATES_ENABLED, False)
            ),
            "manual_latitude": _resolve(const.CONF_MANUAL_LATITUDE),
            "manual_longitude": _resolve(const.CONF_MANUAL_LONGITUDE),
            "manual_elevation": _resolve(const.CONF_MANUAL_ELEVATION),
            "ha_latitude": ha.get("latitude"),
            "ha_longitude": ha.get("longitude"),
            "ha_elevation": ha.get("elevation"),
        },
    )


@async_response
async def websocket_save_coordinates(hass: HomeAssistant, connection, msg):
    """Persist manual coordinates to the config-entry options (single source of truth).

    Writing the options fires the entry update listener, which reloads the
    integration so the new coordinates are picked up — they are baked into the
    weather clients and cached on the coordinator at setup time, so a reload is
    required for a change to take effect.
    """
    entry = hass.data[const.DOMAIN].get("entry")
    if entry is None:
        connection.send_result(msg["id"], {"success": False, "error": "no_entry"})
        return

    enabled = bool(msg["manual_coordinates_enabled"])
    new_options = dict(entry.options)
    new_options[const.CONF_MANUAL_COORDINATES_ENABLED] = enabled
    if enabled:
        new_options[const.CONF_MANUAL_LATITUDE] = msg.get("manual_latitude")
        new_options[const.CONF_MANUAL_LONGITUDE] = msg.get("manual_longitude")
        new_options[const.CONF_MANUAL_ELEVATION] = msg.get("manual_elevation")
    else:
        for key in (
            const.CONF_MANUAL_LATITUDE,
            const.CONF_MANUAL_LONGITUDE,
            const.CONF_MANUAL_ELEVATION,
        ):
            new_options.pop(key, None)

    hass.config_entries.async_update_entry(entry, options=new_options)
    connection.send_result(msg["id"], {"success": True})


@async_response
async def websocket_get_weather_forecast(hass: HomeAssistant, connection, msg):
    """Return the weather service's daily forecast (one entry per upcoming day).

    Reuses the coordinator's weather client (the same forecast already used for
    the precip look-ahead skip). The clients return a normalized list of per-day
    dicts starting tomorrow, with no date field, so we attach the date here.
    Values are metric (the frontend labels units; value conversion is the
    separate H7-units follow-up).
    """
    use_weather_service = hass.data[const.DOMAIN].get(
        const.CONF_USE_WEATHER_SERVICE, False
    )
    coordinator = hass.data[const.DOMAIN].get("coordinator")
    client = getattr(coordinator, "_WeatherServiceClient", None)
    if not use_weather_service or client is None:
        connection.send_result(msg["id"], {"available": False, "days": []})
        return

    try:
        raw = await hass.async_add_executor_job(client.get_forecast_data)
    except Exception as exc:  # noqa: BLE001
        _LOGGER.warning("Weather forecast fetch failed: %s", exc)
        connection.send_result(msg["id"], {"available": False, "days": []})
        return

    if not raw:
        connection.send_result(msg["id"], {"available": False, "days": []})
        return

    today = dt_util.now().date()
    days = []
    for i, day in enumerate(raw):
        days.append(
            {
                # All clients skip "today" and start at tomorrow.
                "date": (today + datetime.timedelta(days=i + 1)).isoformat(),
                "temp_min": day.get(const.MAPPING_MIN_TEMP),
                "temp_max": day.get(const.MAPPING_MAX_TEMP),
                "precipitation": day.get(const.MAPPING_PRECIPITATION),
                "windspeed": day.get(const.MAPPING_WINDSPEED),
            }
        )

    connection.send_result(msg["id"], {"available": True, "days": days})


async def async_register_websockets(hass: HomeAssistant):
    """Register Smart Irrigation HTTP views and websocket commands."""
    hass.http.register_view(SmartIrrigationConfigView)
    hass.http.register_view(SmartIrrigationZoneView)
    hass.http.register_view(SmartIrrigationModuleView)
    hass.http.register_view(SmartIrrigationAllModuleView)
    hass.http.register_view(SmartIrrigationMappingView)
    hass.http.register_view(SmartIrrigationWateringCalendarView)

    async_register_command(hass, handle_subscribe_updates)

    async_register_command(
        hass,
        const.DOMAIN + "/config",
        websocket_get_config,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/config"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/zones",
        websocket_get_zones,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/zones"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/modules",
        websocket_get_modules,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/modules"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/allmodules",
        websocket_get_all_modules,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/allmodules"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/mappings",
        websocket_get_mappings,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/mappings"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/weather_records",
        websocket_get_weather_records,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/weather_records",
                vol.Required("mapping_id"): vol.Coerce(str),
                vol.Optional("limit", default=10): vol.Coerce(int),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/watering_calendar",
        websocket_get_watering_calendar,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/watering_calendar",
                vol.Optional("zone_id"): vol.Coerce(str),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/schedules",
        websocket_get_schedules,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/schedules"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/schedule_save",
        websocket_save_schedule,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/schedule_save",
                vol.Required("schedule"): dict,
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/schedule_delete",
        websocket_delete_schedule,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/schedule_delete",
                vol.Required("schedule_id"): str,
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/irrigation_outlook",
        websocket_get_irrigation_outlook,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/irrigation_outlook"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/irrigate_now",
        websocket_irrigate_now,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/irrigate_now",
                vol.Optional("zone_id"): vol.Coerce(str),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/run_zone",
        websocket_run_zone,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/run_zone",
                vol.Required("zone_id"): vol.Coerce(str),
                vol.Required("duration"): vol.Coerce(float),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/stop_zone",
        websocket_stop_zone,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/stop_zone",
                vol.Required("zone_id"): vol.Coerce(str),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/set_rain_delay",
        websocket_set_rain_delay,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/set_rain_delay",
                vol.Optional("hours"): vol.Coerce(float),
                vol.Optional("until"): vol.Any(str, None),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/clear_rain_delay",
        websocket_clear_rain_delay,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/clear_rain_delay"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/weather_config",
        websocket_get_weather_config,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/weather_config"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/weather_config_save",
        websocket_save_weather_config,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/weather_config_save",
                vol.Required("use_weather_service"): bool,
                vol.Optional("weather_service"): vol.Any(str, None),
                vol.Optional("api_key"): vol.Any(str, None),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/weather_config_test",
        websocket_test_weather_config,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/weather_config_test",
                vol.Optional("weather_service"): vol.Any(str, None),
                vol.Optional("api_key"): vol.Any(str, None),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/coordinates",
        websocket_get_coordinates,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/coordinates"}
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/coordinates_save",
        websocket_save_coordinates,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): const.DOMAIN + "/coordinates_save",
                vol.Required("manual_coordinates_enabled"): bool,
                vol.Optional("manual_latitude"): vol.Any(float, int, None),
                vol.Optional("manual_longitude"): vol.Any(float, int, None),
                vol.Optional("manual_elevation"): vol.Any(float, int, None),
            }
        ),
    )
    async_register_command(
        hass,
        const.DOMAIN + "/weather_forecast",
        websocket_get_weather_forecast,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): const.DOMAIN + "/weather_forecast"}
        ),
    )
