"""The Smart Irrigation Integration."""

import logging

# NB: alias the stdlib datetime class. This package ships a ``datetime.py``
# platform module (the rain-delay DateTimeEntity); importing that platform sets
# the ``datetime`` attribute on this package — which IS this module's global
# namespace — clobbering a global literally named ``datetime`` and breaking
# ``dt_datetime.now()`` at runtime. The alias keeps our global name collision-free.
from datetime import datetime as dt_datetime
from datetime import timedelta

from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
)
from homeassistant.core import HomeAssistant, asyncio, callback
from homeassistant.helpers import (
    config_validation as cv,
)
from homeassistant.helpers import (
    device_registry as dr,
)
from homeassistant.helpers import (
    entity_registry as er,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.event import (
    async_call_later,
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .calculation import CalculationMixin
from .config_resolver import resolve_weather_config
from .helpers import (
    altitudeToPressure,
    check_time,
    convert_between,
    convert_mapping_to_metric,
    ha_unit_to_internal_unit,
    loadModules,
    relative_to_absolute_pressure,
)
from .irrigation import IrrigationRunnerMixin
from .live_estimate import LiveEstimateMixin
from .observed_watering import ObservedWateringMixin
from .panel import async_register_panel, remove_panel
from .scheduler import RecurringScheduleManager
from .services import ServiceHandlersMixin, async_register_services
from .skip_conditions import SkipConditionsMixin
from .store import SmartIrrigationStorage, async_get_registry
from .watering_calendar import WateringCalendarMixin
from .weathermodules.MetOfficeClient import MetOfficeClient
from .weathermodules.OpenMeteoClient import OpenMeteoClient
from .weathermodules.OWMClient import OWMClient
from .weathermodules.PirateWeatherClient import PirateWeatherClient
from .websockets import async_register_websockets

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(const.DOMAIN)


async def async_setup(hass: HomeAssistant, config):
    """Track states and offer events for sensors."""
    return True


async def _migrate_duration_unique_ids(hass: HomeAssistant, entry, store) -> None:
    """Migrate the zone duration sensor's legacy unique_id.

    The duration sensor historically used its own entity_id as unique_id
    (``sensor.smart_irrigation_<slug>`` — the only entity that did). Rewrite it
    to ``smart_irrigation_<zone_id>_duration`` to match every other entity. The
    registry entry (hence the entity_id + recorded history) carries over.

    Idempotent: already-migrated ids don't start with ``sensor.`` so they're
    skipped. The ``sensor.`` prefix uniquely identifies the legacy duration ids
    (bucket/et/etc. use ``smart_irrigation_<id>_<suffix>`` without it).
    """
    from homeassistant.util import slugify

    legacy_prefix = f"{PLATFORM}.{const.DOMAIN}_"  # "sensor.smart_irrigation_"
    try:
        zone_ids = list(getattr(store, "zones", None) or [])
    except TypeError:  # store not fully initialized (e.g. mocked) — nothing to migrate
        zone_ids = []
    slug_to_zone_id = {}
    for zone_id in zone_ids:
        zone = store.get_zone(zone_id)
        name = zone.get(const.ZONE_NAME) if zone else None
        if name:
            slug_to_zone_id.setdefault(slugify(name), zone.get(const.ZONE_ID, zone_id))

    @callback
    def _migrator(reg_entry):
        uid = reg_entry.unique_id
        if (
            reg_entry.domain != PLATFORM
            or not isinstance(uid, str)
            or not uid.startswith(legacy_prefix)
        ):
            return None
        zone_id = slug_to_zone_id.get(uid[len(legacy_prefix) :])
        if zone_id is None:
            return None
        return {"new_unique_id": f"{const.DOMAIN}_{zone_id}_duration"}

    await er.async_migrate_entries(hass, entry.entry_id, _migrator)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Smart Irrigation from a config entry."""

    _LOGGER.info("async_setup_entry called for %s", entry.entry_id)

    session = async_get_clientsession(hass)

    store = await async_get_registry(hass)
    # store Weather Service info in hass.data
    hass.data.setdefault(const.DOMAIN, {})
    hass.data[const.DOMAIN]["entry"] = entry
    # Resolve the effective weather-service config (store defaults -> entry.data
    # -> entry.options, with the use_owm / legacy-key migrations). See
    # config_resolver.resolve_weather_config — extracted so this reconciliation
    # lives in one tested place instead of ~80 inline lines (issue #683).
    config = await store.async_get_config()
    hass.data[const.DOMAIN].update(
        resolve_weather_config(config, entry, existing=hass.data[const.DOMAIN])
    )

    coordinator = SmartIrrigationCoordinator(hass, session, entry, store)

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(const.DOMAIN, coordinator.id)},
        name=const.NAME,
        model=const.NAME,
        sw_version=const.VERSION,
        manufacturer=const.MANUFACTURER,
    )

    hass.data[const.DOMAIN]["coordinator"] = coordinator
    hass.data[const.DOMAIN]["zones"] = {}

    # Set up the auto update/calc/clear timers (awaited, not fire-and-forget).
    await coordinator.async_setup_timers()

    # Set up unit system change listener
    async def handle_core_config_change(event):
        """Handle Home Assistant core configuration changes, specifically unit system changes."""
        _LOGGER.debug("Core_config_updated fired: %s", event.data)
        if (
            const.DOMAIN not in hass.data
            or "coordinator" not in hass.data[const.DOMAIN]
        ):
            return

        # Check if unit system has changed by comparing current vs coordinator's cached unit system
        coordinator = hass.data[const.DOMAIN]["coordinator"]
        current_unit_system = hass.config.units

        # Store the previous unit system in coordinator if not already stored
        if not hasattr(coordinator, "_previous_unit_system"):
            coordinator.previous_unit_system = current_unit_system
            return

        # Check if unit system actually changed
        if coordinator.previous_unit_system != current_unit_system:
            _LOGGER.info(
                "Home Assistant unit system changed from %s to %s, updating Smart Irrigation",
                coordinator.previous_unit_system.name,
                current_unit_system.name,
            )

            # Update coordinator's cached unit system
            coordinator.previous_unit_system = current_unit_system

            # Trigger unit system update
            await coordinator.async_handle_unit_system_change()
        else:
            _LOGGER.debug("Core config updated but unit system unchanged")

    coordinator.previous_unit_system = hass.config.units
    # hass.bus.async_listen(
    #    "core_config_updated", core_config_updated_listener_factory(hass)
    # )
    hass.bus.async_listen("core_config_updated", handle_core_config_change)
    _LOGGER.info(
        "Registered listener for Home Assistant core config changes (unit system)"
    )

    # make sure we capture the use_owm state
    await store.async_update_config(
        {const.CONF_USE_WEATHER_SERVICE: coordinator.use_weather_service}
    )

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=coordinator.id, data={})

    # One-time entity-registry migration: the zone duration sensor used to set
    # its unique_id to its own entity_id (sensor.smart_irrigation_<slug>). Rewrite
    # it to the per-zone scheme smart_irrigation_<zone_id>_duration so it matches
    # every other entity; existing entity_ids + history carry over. Idempotent.
    await _migrate_duration_unique_ids(hass, entry, store)

    _LOGGER.info("Calling async_forward_entry_setups")
    await hass.config_entries.async_forward_entry_setups(
        entry, [PLATFORM, "number", "binary_sensor", "button", "datetime"]
    )
    _LOGGER.info("Finished calling async_forward_entry_setups")

    # Replay existing zones to all per-zone platforms now that EVERY platform has
    # finished async_setup_entry and subscribed to `_register_entity`. Firing this
    # from a single platform (sensor) raced the others' subscriptions under
    # concurrent setup, so only sensors got per-zone entities — buttons, numbers
    # and per-zone binary_sensors were silently missing. One fire here reaches all.
    async_dispatcher_send(hass, const.DOMAIN + "_platform_loaded")
    # update listener for options flow
    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    # Register the panel (frontend)
    await async_register_panel(hass)

    # Websocket support
    await async_register_websockets(hass)

    # Register custom services
    async_register_services(hass)

    # Finish up by setting factory defaults if needed for zones, mappings and modules
    await store.set_up_factory_defaults()

    # Initialize enhanced scheduling managers
    await coordinator.recurring_schedule_manager.async_load_schedules()

    return True


async def options_update_listener(hass: HomeAssistant, config_entry):
    """Handle options update."""
    # copy the api key and version to the hass data
    if const.DOMAIN in hass.data:
        hass.data[const.DOMAIN][const.CONF_USE_WEATHER_SERVICE] = (
            config_entry.options.get(const.CONF_USE_WEATHER_SERVICE)
        )
        if hass.data[const.DOMAIN][const.CONF_USE_WEATHER_SERVICE]:
            if const.CONF_WEATHER_SERVICE in config_entry.options:
                hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE] = (
                    config_entry.options.get(const.CONF_WEATHER_SERVICE)
                )
            if const.CONF_WEATHER_SERVICE_API_KEY in config_entry.options:
                hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE_API_KEY] = (
                    config_entry.options.get(const.CONF_WEATHER_SERVICE_API_KEY).strip()
                )
            hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE_API_VERSION] = (
                config_entry.options.get(const.CONF_WEATHER_SERVICE_API_VERSION)
            )
        else:
            hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE] = None
            hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE_API_KEY] = None
            hass.data[const.DOMAIN][const.CONF_WEATHER_SERVICE_API_VERSION] = None
        await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload Smart Irrigation config entry."""
    unload_ok = all(
        await asyncio.gather(
            hass.config_entries.async_forward_entry_unload(entry, PLATFORM),
            hass.config_entries.async_forward_entry_unload(entry, "number"),
            hass.config_entries.async_forward_entry_unload(entry, "binary_sensor"),
            hass.config_entries.async_forward_entry_unload(entry, "button"),
            hass.config_entries.async_forward_entry_unload(entry, "datetime"),
        )
    )
    if not unload_ok:
        return False

    remove_panel(hass)
    coordinator = hass.data[const.DOMAIN]["coordinator"]
    await coordinator.async_unload()
    return True


async def async_remove_entry(hass: HomeAssistant, entry):
    """Remove Smart Irrigation config entry."""
    remove_panel(hass)
    if const.DOMAIN in hass.data:
        if "coordinator" in hass.data[const.DOMAIN]:
            coordinator = hass.data[const.DOMAIN]["coordinator"]
            await coordinator.async_delete_config()
        del hass.data[const.DOMAIN]


SmartIrrigationError = const.SmartIrrigationError  # re-exported for backward compat


class SmartIrrigationCoordinator(
    ServiceHandlersMixin,
    WateringCalendarMixin,
    IrrigationRunnerMixin,
    CalculationMixin,
    SkipConditionsMixin,
    LiveEstimateMixin,
    ObservedWateringMixin,
):
    """Define an object to hold Smart Irrigation device.

    This is a plain coordinator: it does all its own scheduling (auto
    update/calc/clear timers, midnight tracking, debounced updates) and uses none
    of DataUpdateCoordinator's polling API (no update_interval, no
    _async_update_data, no listeners), so it does not inherit it.
    """

    def __init__(
        self, hass: HomeAssistant, session, entry, store: SmartIrrigationStorage
    ) -> None:
        """Initialize."""
        self.hass = hass
        self.id = entry.unique_id
        self.entry = entry
        self.store = store
        self.previous_unit_system = hass.config.units
        self.use_weather_service = hass.data[const.DOMAIN][
            const.CONF_USE_WEATHER_SERVICE
        ]

        self.weather_service = hass.data[const.DOMAIN].get(
            const.CONF_WEATHER_SERVICE, None
        )
        self._WeatherServiceClient = None
        # Per-zone intraday estimates, refreshed on the update/calc cycles
        # (see LiveEstimateMixin.async_refresh_zone_estimates).
        self._zone_estimates_cache = None
        if self.use_weather_service:
            # Get effective coordinates before creating weather service clients
            effective_lat, effective_lon, effective_elev = (
                self._get_effective_coordinates()
            )

            if self.weather_service == const.CONF_WEATHER_SERVICE_OWM:
                # Prefer the per-service key (stored since v2026.05.14);
                # fall back to the legacy single-key slot for compatibility.
                owm_key = hass.data[const.DOMAIN].get(
                    const.CONF_OWM_API_KEY
                ) or hass.data[const.DOMAIN].get(const.CONF_WEATHER_SERVICE_API_KEY)
                self._WeatherServiceClient = OWMClient(
                    api_key=owm_key,
                    api_version=hass.data[const.DOMAIN].get(
                        const.CONF_WEATHER_SERVICE_API_VERSION
                    ),
                    latitude=effective_lat,
                    longitude=effective_lon,
                    elevation=effective_elev,
                )
            elif self.weather_service == const.CONF_WEATHER_SERVICE_PW:
                pw_key = hass.data[const.DOMAIN].get(
                    const.CONF_PW_API_KEY
                ) or hass.data[const.DOMAIN].get(const.CONF_WEATHER_SERVICE_API_KEY)
                self._WeatherServiceClient = PirateWeatherClient(
                    api_key=pw_key,
                    api_version="1",
                    latitude=effective_lat,
                    longitude=effective_lon,
                    elevation=effective_elev,
                )
            elif self.weather_service == const.CONF_WEATHER_SERVICE_MET:
                met_key = hass.data[const.DOMAIN].get(
                    const.CONF_MET_API_KEY
                ) or hass.data[const.DOMAIN].get(const.CONF_WEATHER_SERVICE_API_KEY)
                self._WeatherServiceClient = MetOfficeClient(
                    api_key=met_key,
                    latitude=effective_lat,
                    longitude=effective_lon,
                    elevation=effective_elev,
                )
            elif self.weather_service == const.CONF_WEATHER_SERVICE_OPENMETEO:
                self._WeatherServiceClient = OpenMeteoClient(
                    latitude=effective_lat,
                    longitude=effective_lon,
                    elevation=effective_elev,
                )

        # Initialize coordinates for weather services and other features
        (
            self._effective_latitude,
            self._effective_longitude,
            self._effective_elevation,
        ) = self._get_effective_coordinates()

        # Keep latitude and elevation properties for backward compatibility
        self._latitude = self._effective_latitude
        self._elevation = self._effective_elevation

        self._subscriptions = []

        self._subscriptions.append(
            async_dispatcher_connect(
                hass,
                const.DOMAIN + "_platform_loaded",
                self.setup_SmartIrrigation_entities,
            )
        )

        # Experimental observed-watering state (ObservedWateringMixin). Off until
        # async_setup_observed_watering() subscribes. ``_si_driven_until`` maps a
        # zone id → loop time the runner's valve-open suppression expires, so the
        # observer doesn't double-credit Smart Irrigation's own runs.
        self._observed_unsub = None
        self._observed_on_since = {}
        self._observed_entities = frozenset()
        self._observed_zone_by_entity = {}
        self._si_driven_until = {}
        # Re-evaluate the observed-watering subscription whenever config or zones
        # change (cheap no-op unless the tracked valve set actually changes).
        self._subscriptions.append(
            async_dispatcher_connect(
                hass,
                const.DOMAIN + "_config_updated",
                self._schedule_observed_watering_setup,
            )
        )
        self._track_auto_calc_time_unsub = None
        self._track_auto_update_time_unsub = None
        self._track_midnight_time_unsub = None
        self._pending_track_update_unsub = None  # cancel handle for async_call_later
        # Auto update/calc timers are set up by async_setup_timers(), which
        # async_setup_entry awaits after construction — see that method. Doing it
        # here previously required fire-and-forget tasks (unawaited, errors lost).

        # Most recent persisted skip-condition decision (structured), surfaced as
        # the dashboard's "last run" explanation. Reset on restart.
        self._last_skip_evaluation = None

        # Initialize enhanced scheduling managers
        self.recurring_schedule_manager = RecurringScheduleManager(hass, self)

        # set up midnight tracking
        self._track_midnight_time_unsub = async_track_time_change(
            hass, self._reset_event_fired_today, 0, 0, 0
        )

    async def async_setup_timers(self):
        """Set up the auto update/calc/clear timers from stored config.

        Called (awaited) from async_setup_entry after the coordinator is
        constructed. Previously this ran in __init__ via fire-and-forget
        hass.loop.create_task(...), which left timer-setup errors unretrieved and
        timing nondeterministic. The unsub handles are cancelled in async_unload.
        """
        the_config = self.store.get_config()
        the_config[const.CONF_USE_WEATHER_SERVICE] = self.use_weather_service
        the_config[const.CONF_WEATHER_SERVICE] = self.weather_service
        if the_config[const.CONF_AUTO_UPDATE_ENABLED]:
            await self.set_up_auto_update_time(the_config)
        if the_config[const.CONF_AUTO_CALC_ENABLED]:
            await self.set_up_auto_calc_time(the_config)
        # Experimental observed-watering observer (no-op unless enabled).
        await self.async_setup_observed_watering()

    @callback
    def _schedule_observed_watering_setup(self, *args) -> None:
        """Re-evaluate the observed-watering subscription after a config change."""
        self.hass.async_create_task(self.async_setup_observed_watering())

    def _get_config_value(self, key: str, default_value):
        """Get configuration value from Home Assistant config, entry data, or options with fallback to default.

        Args:
            key: Configuration key to look up (e.g., CONF_LATITUDE, CONF_ELEVATION)
            default_value: Default value to use if not found anywhere

        Returns:
            The configuration value or default_value if not found

        """
        # Try Home Assistant config first (most reliable)
        value = self.hass.config.as_dict().get(key)
        if value is not None:
            return value

        # Try config entry data
        if hasattr(self.entry, "data") and key in self.entry.data:
            return self.entry.data[key]

        # Try config entry options
        if hasattr(self.entry, "options") and key in self.entry.options:
            return self.entry.options[key]

        # Fall back to default
        return default_value

    def _get_effective_coordinates(self):
        """Get the effective coordinates to use for weather services and calculations.

        Returns manual coordinates if enabled, otherwise falls back to Home Assistant config.

        Returns:
            tuple: (latitude, longitude, elevation)

        """
        # Check if manual coordinates are enabled
        manual_enabled = self._get_config_value(
            const.CONF_MANUAL_COORDINATES_ENABLED, False
        )

        if manual_enabled:
            # Use manual coordinates
            latitude = self._get_config_value(const.CONF_MANUAL_LATITUDE, None)
            longitude = self._get_config_value(const.CONF_MANUAL_LONGITUDE, None)
            elevation = self._get_config_value(const.CONF_MANUAL_ELEVATION, 0)

            if latitude is not None and longitude is not None:
                _LOGGER.info(
                    "Using manual coordinates: lat=%.6f, lon=%.6f, elevation=%sm",
                    latitude,
                    longitude,
                    elevation,
                )
                return latitude, longitude, elevation
            _LOGGER.warning(
                "Manual coordinates enabled but latitude or longitude not set, falling back to Home Assistant config"
            )

        # Fall back to Home Assistant configuration
        ha_lat = self.hass.config.as_dict().get(CONF_LATITUDE, 45.0)
        ha_lon = self.hass.config.as_dict().get(CONF_LONGITUDE, 0.0)
        ha_elev = self.hass.config.as_dict().get(CONF_ELEVATION, 0)

        _LOGGER.info(
            "Using Home Assistant coordinates: lat=%.6f, lon=%.6f, elevation=%sm",
            ha_lat,
            ha_lon,
            ha_elev,
        )

        # Log warnings for default coordinates
        if ha_lat == 45.0 and self.hass.config.as_dict().get(CONF_LATITUDE) is None:
            _LOGGER.warning(
                "Latitude not configured in Home Assistant, using default latitude of 45.0"
            )
        if ha_elev == 0 and self.hass.config.as_dict().get(CONF_ELEVATION) is None:
            _LOGGER.warning(
                "Elevation not configured in Home Assistant, using default elevation of 0m"
            )

        return ha_lat, ha_lon, ha_elev

    async def setup_SmartIrrigation_entities(self):  # noqa: D102
        zones = await self.store.async_get_zones()

        for zone in zones:
            # self.async_create_zone(zone)
            async_dispatcher_send(self.hass, const.DOMAIN + "_register_entity", zone)

    async def async_handle_unit_system_change(self):
        """Handle changes to the Home Assistant unit system."""
        _LOGGER.info("Processing unit system change for Smart Irrigation")

        # Update sensor entities to refresh their unit display
        async_dispatcher_send(self.hass, const.DOMAIN + "_unit_system_changed")

        # Update frontend/websocket clients
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")

        _LOGGER.info("Unit system change processing complete")

    async def async_update_config(self, data):  # noqa: D102
        _LOGGER.debug("[async_update_config]: config changed: %s", data)

        # Handle precipitation threshold unit conversion
        # Always store internally in mm, but convert from user units if needed
        if const.CONF_PRECIPITATION_THRESHOLD_MM in data:
            threshold_value = data[const.CONF_PRECIPITATION_THRESHOLD_MM]
            if threshold_value is not None:
                # Check if HA is in metric or imperial mode
                ha_config_is_metric = self.hass.config.units is METRIC_SYSTEM
                if not ha_config_is_metric:
                    # User is in imperial mode, so convert from inches to mm for internal storage
                    threshold_mm = convert_between(
                        const.UNIT_INCH, const.UNIT_MM, threshold_value
                    )
                    data[const.CONF_PRECIPITATION_THRESHOLD_MM] = threshold_mm
                    _LOGGER.debug(
                        "Converted precipitation threshold from %.2f inches to %.2f mm for internal storage",
                        threshold_value,
                        threshold_mm,
                    )
                else:
                    # User is in metric mode, value is already in mm
                    _LOGGER.debug(
                        "Precipitation threshold %.2f mm stored directly (metric mode)",
                        threshold_value,
                    )

        # handle auto calc changes (only when the save actually touches them —
        # partial saves, e.g. the Experimental tab, omit these keys)
        if const.CONF_AUTO_CALC_ENABLED in data:
            await self.set_up_auto_calc_time(data)
        # handle auto update changes, includings updating OWMClient cache settings
        if const.CONF_AUTO_UPDATE_ENABLED in data:
            await self.set_up_auto_update_time(data)
        await self.store.async_update_config(data)
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated")

    async def set_up_auto_update_time(self, data):  # noqa: D102
        if data[const.CONF_AUTO_UPDATE_ENABLED]:
            # Cancel any previous pending async_call_later before scheduling a new one
            if self._pending_track_update_unsub:
                self._pending_track_update_unsub()
                self._pending_track_update_unsub = None
            delay = 0
            if const.CONF_AUTO_UPDATE_DELAY in data:
                if int(data[const.CONF_AUTO_UPDATE_DELAY]) > 0:
                    delay = int(data[const.CONF_AUTO_UPDATE_DELAY])
                    _LOGGER.info("Delaying auto update with %s seconds", delay)
            self._pending_track_update_unsub = async_call_later(
                self.hass, timedelta(seconds=delay), self.track_update_time
            )
        elif self._track_auto_update_time_unsub:
            self._track_auto_update_time_unsub()
            self._track_auto_update_time_unsub = None
            await self.store.async_update_config(data)

    async def set_up_auto_calc_time(self, data):
        """Set up the automatic calculation time for Smart Irrigation based on configuration data."""
        # unsubscribe from any existing track_time_changes
        if self._track_auto_calc_time_unsub:
            self._track_auto_calc_time_unsub()
            self._track_auto_calc_time_unsub = None
        if data[const.CONF_AUTO_CALC_ENABLED]:
            # make sure to unsub any existing and add for calc time
            if check_time(data[const.CONF_CALC_TIME]):
                # make sure we track this time and at that moment trigger the refresh of all modules of all zones that are on automatic
                timesplit = data[const.CONF_CALC_TIME].split(":")
                self._track_auto_calc_time_unsub = async_track_time_change(
                    self.hass,
                    self._async_calculate_all,
                    hour=timesplit[0],
                    minute=timesplit[1],
                    second=0,
                )
                _LOGGER.info(
                    "Scheduled auto calculate for %s", data[const.CONF_CALC_TIME]
                )
            else:
                _LOGGER.warning(
                    "Scheduled auto calculate time is not valid: %s",
                    data[const.CONF_CALC_TIME],
                )
                # raise ValueError("Time is not a valid time")
        else:
            # set OWM client cache to 0
            if self._WeatherServiceClient:
                self._WeatherServiceClient.cache_seconds = 0
            # remove all time trackers
            if self._track_auto_calc_time_unsub:
                self._track_auto_calc_time_unsub()
                self._track_auto_calc_time_unsub = None
            await self.store.async_update_config(data)

    async def track_update_time(self, *args):
        """Track and schedule periodic updates for Smart Irrigation based on configuration."""
        # The async_call_later that scheduled us has now fired — clear the handle
        self._pending_track_update_unsub = None
        # perform update once
        # Fire-and-forget: trigger immediate update in background
        self.hass.async_create_task(self._async_update_all())
        # use async_track_time_interval
        data = await self.store.async_get_config()
        the_time_delta = None
        interval = int(data[const.CONF_AUTO_UPDATE_INTERVAL])
        if data[const.CONF_AUTO_UPDATE_SCHEDULE] == const.CONF_AUTO_UPDATE_DAILY:
            # track time X days
            the_time_delta = timedelta(days=interval)
        elif data[const.CONF_AUTO_UPDATE_SCHEDULE] == const.CONF_AUTO_UPDATE_HOURLY:
            # track time X hours
            the_time_delta = timedelta(hours=interval)
        elif data[const.CONF_AUTO_UPDATE_SCHEDULE] == const.CONF_AUTO_UPDATE_MINUTELY:
            # track time X minutes
            the_time_delta = timedelta(minutes=interval)
        # update cache for OWMClient to time delta in seconds -1
        if self._WeatherServiceClient:
            self._WeatherServiceClient.cache_seconds = (
                the_time_delta.total_seconds() - 1
            )

        if self._track_auto_update_time_unsub:
            self._track_auto_update_time_unsub()
            self._track_auto_update_time_unsub = None
        self._track_auto_update_time_unsub = async_track_time_interval(
            self.hass, self._async_update_all, the_time_delta
        )
        _LOGGER.info("Scheduled auto update time interval for each %s", the_time_delta)

    async def _get_unique_mappings_for_automatic_zones(self, zones):
        mappings = [
            zone.get(const.ZONE_MAPPING)
            for zone in zones
            if zone.get(const.ZONE_STATE) == const.ZONE_STATE_AUTOMATIC
        ]
        # remove duplicates
        return list(set(mappings))

    async def _get_zones_that_use_this_mapping(self, mapping):
        """Return a list of zone IDs that use the specified mapping."""
        return [
            z.get(const.ZONE_ID)
            for z in await self.store.async_get_zones()
            if z.get(const.ZONE_MAPPING) == mapping
        ]

    async def _async_update_zone(self, zone_id):
        # update the weather data for the mapping for the zone
        _LOGGER.info("Updating weather data for zone %s", zone_id)
        zone = self.store.get_zone(zone_id)
        if not zone:
            raise SmartIrrigationError(f"Zone {zone_id} not found")
        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is not None:
            mapping = self.store.get_mapping(mapping_id)
            (
                owm_in_mapping,
                sensor_in_mapping,
                static_in_mapping,
            ) = self.check_mapping_sources(mapping_id=mapping_id)
            weatherdata = None
            if self.use_weather_service and owm_in_mapping:
                # retrieve data from weather service
                try:
                    weatherdata = await self.hass.async_add_executor_job(
                        self._WeatherServiceClient.get_data
                    )
                except OSError as err:
                    raise SmartIrrigationError(
                        f"Weather service error while updating zone: {err}"
                    ) from err
                if weatherdata is None:
                    raise SmartIrrigationError(
                        "Weather service returned no data — check your API key and subscription."
                    )

            if sensor_in_mapping:
                sensor_values = self.build_sensor_values_for_mapping(mapping)
                weatherdata = await self.merge_weatherdata_and_sensor_values(
                    weatherdata, sensor_values
                )
            if static_in_mapping:
                static_values = self.build_static_values_for_mapping(mapping)
                weatherdata = await self.merge_weatherdata_and_sensor_values(
                    weatherdata, static_values
                )
            if sensor_in_mapping or static_in_mapping:
                # convert relative pressure to absolute if configured
                mapping_mappings = mapping.get(const.MAPPING_MAPPINGS) or {}
                pressure_map = mapping_mappings.get(const.MAPPING_PRESSURE) or {}
                if (
                    pressure_map.get(const.MAPPING_CONF_PRESSURE_TYPE)
                    == const.MAPPING_CONF_PRESSURE_RELATIVE
                ):
                    if const.MAPPING_PRESSURE in weatherdata:
                        weatherdata[const.MAPPING_PRESSURE] = (
                            relative_to_absolute_pressure(
                                weatherdata[const.MAPPING_PRESSURE],
                                self.hass.config.as_dict().get(CONF_ELEVATION),
                            )
                        )
                    else:
                        weatherdata[const.MAPPING_PRESSURE] = altitudeToPressure(
                            self.hass.config.as_dict().get(CONF_ELEVATION)
                        )

            # add the weatherdata value to the mappings sensor values
            if mapping is not None and weatherdata is not None:
                weatherdata[const.RETRIEVED_AT] = dt_datetime.now()
                mapping_data = mapping[const.MAPPING_DATA]
                if isinstance(mapping_data, list):
                    mapping_data.append(weatherdata)
                elif isinstance(mapping_data, str):
                    mapping_data = [weatherdata]
                else:
                    _LOGGER.error(
                        "[async_update_all]: sensor group is unexpected type: %s",
                        mapping_data,
                    )
                _LOGGER.debug(
                    "async_update_all for mapping %s new weatherdata: %s",
                    mapping_id,
                    weatherdata,
                )
                changes = {
                    "data": mapping_data,
                    const.MAPPING_DATA_LAST_UPDATED: dt_datetime.now(),
                }
                await self.store.async_update_mapping(mapping_id, changes)
                # store last updated and number of data points in the zone here.
                changes_to_zone = {
                    const.ZONE_LAST_UPDATED: changes[const.MAPPING_DATA_LAST_UPDATED],
                    const.ZONE_NUMBER_OF_DATA_POINTS: len(mapping_data) - 1,
                }
                await self.store.async_update_zone(zone_id, changes_to_zone)
                async_dispatcher_send(
                    self.hass,
                    const.DOMAIN + "_config_updated",
                    zone,
                )
            else:
                if mapping is None:
                    _LOGGER.warning(
                        "[async_update_all] Unable to find sensor group with id: %s",
                        mapping_id,
                    )
                if weatherdata is None:
                    _LOGGER.warning(
                        "[async_update_all] No weather data to parse for sensor group %s",
                        mapping_id,
                    )

    async def _async_update_all(self, *args):
        # update the weather data for all mappings for all zones that are automatic here and store it.
        # in _async_calculate_all we need to read that data back and if there is none, we log an error, otherwise apply aggregate and use data
        # this should skip any pure sensor zones if continuous updates is enabled, otherwise it should include them
        _LOGGER.info("Updating weather data for all automatic zones")
        zones = await self.store.async_get_zones()
        mappings = await self._get_unique_mappings_for_automatic_zones(zones)
        # loop over the mappings and store sensor data
        for mapping_id in mappings:
            (
                owm_in_mapping,
                sensor_in_mapping,
                static_in_mapping,
            ) = self.check_mapping_sources(mapping_id=mapping_id)
            mapping = self.store.get_mapping(mapping_id)
            weatherdata = None
            if self.use_weather_service and owm_in_mapping:
                # retrieve data from weather service; log and skip on failure
                try:
                    weatherdata = await self.hass.async_add_executor_job(
                        self._WeatherServiceClient.get_data
                    )
                except OSError as err:
                    _LOGGER.error(
                        "[async_update_all] Weather service error for mapping %s: %s",
                        mapping_id,
                        err,
                    )
                    continue
                if weatherdata is None:
                    _LOGGER.warning(
                        "[async_update_all] No weather data to parse for sensor group %s",
                        mapping_id,
                    )
                    continue

            if sensor_in_mapping:
                sensor_values = self.build_sensor_values_for_mapping(mapping)
                weatherdata = await self.merge_weatherdata_and_sensor_values(
                    weatherdata, sensor_values
                )
            if static_in_mapping:
                static_values = self.build_static_values_for_mapping(mapping)
                weatherdata = await self.merge_weatherdata_and_sensor_values(
                    weatherdata, static_values
                )
            if sensor_in_mapping or static_in_mapping:
                # convert relative pressure to absolute if configured
                mapping_mappings = mapping.get(const.MAPPING_MAPPINGS) or {}
                pressure_map = mapping_mappings.get(const.MAPPING_PRESSURE) or {}
                if (
                    pressure_map.get(const.MAPPING_CONF_PRESSURE_TYPE)
                    == const.MAPPING_CONF_PRESSURE_RELATIVE
                ):
                    if const.MAPPING_PRESSURE in weatherdata:
                        weatherdata[const.MAPPING_PRESSURE] = (
                            relative_to_absolute_pressure(
                                weatherdata[const.MAPPING_PRESSURE],
                                self.hass.config.as_dict().get(CONF_ELEVATION),
                            )
                        )
                    else:
                        weatherdata[const.MAPPING_PRESSURE] = altitudeToPressure(
                            self.hass.config.as_dict().get(CONF_ELEVATION)
                        )

            # add the weatherdata value to the mappings sensor values
            if mapping is not None and weatherdata is not None:
                weatherdata[const.RETRIEVED_AT] = dt_datetime.now()
                mapping_data = mapping[const.MAPPING_DATA]
                if isinstance(mapping_data, list):
                    mapping_data.append(weatherdata)
                elif isinstance(mapping_data, str):
                    mapping_data = [weatherdata]
                else:
                    _LOGGER.error(
                        "[async_update_all]: sensor group is unexpected type: %s",
                        mapping_data,
                    )
                _LOGGER.debug(
                    "async_update_all for mapping %s new weatherdata: %s",
                    mapping_id,
                    weatherdata,
                )
                changes = {
                    "data": mapping_data,
                }
                await self.store.async_update_mapping(mapping_id, changes)
                # store last updated and number of data points in the zone here.
                changes_to_zone = {
                    const.ZONE_LAST_UPDATED: dt_datetime.now(),
                    const.ZONE_NUMBER_OF_DATA_POINTS: len(mapping_data) - 1,
                }
                zones_to_loop = await self._get_zones_that_use_this_mapping(mapping_id)
                for z in zones_to_loop:
                    await self.store.async_update_zone(z, changes_to_zone)
                    async_dispatcher_send(
                        self.hass,
                        const.DOMAIN + "_config_updated",
                        z,
                    )
            else:
                if mapping is None:
                    _LOGGER.warning(
                        "[async_update_all] Unable to find sensor group with id: %s",
                        mapping_id,
                    )
                if weatherdata is None:
                    _LOGGER.warning(
                        "[async_update_all] No weather data to parse for sensor group %s",
                        mapping_id,
                    )

        # Fresh weather data in → refresh the cached intraday estimates once
        # for everyone (live-deficit sensors + panel outlook).
        await self.async_refresh_zone_estimates()

    async def async_update_module_config(
        self, module_id: int | None = None, data: dict | None = None
    ):
        """Update, create, or delete a module configuration.

        Args:
            module_id: The ID of the module to update or delete.
            data: The configuration data for the module.

        """
        if data is None:
            data = {}
        if module_id is not None:
            module_id = int(module_id)
        if const.ATTR_REMOVE in data:
            # delete a module
            module = self.store.get_module(module_id)
            if not module:
                return
            await self.store.async_delete_module(module_id)
        elif module_id is not None and self.store.get_module(module_id):
            # modify a module
            await self.store.async_update_module(module_id, data)
            async_dispatcher_send(
                self.hass, const.DOMAIN + "_config_updated", module_id
            )
        else:
            # create a module
            entry = await self.store.async_create_module(data)
            await self.store.async_get_config()
            return entry
        return None

    async def async_update_mapping_config(
        self, mapping_id: int | None = None, data: dict | None = None
    ):
        """Update, create, or delete a mapping configuration.

        Args:
            mapping_id: The ID of the mapping to update or delete.
            data: The configuration data for the mapping.

        """
        _LOGGER.debug(
            "[async_update_mapping_config]: update for mapping %s, data: %s",
            mapping_id,
            data,
        )
        if data is None:
            data = {}
        if mapping_id is not None:
            mapping_id = int(mapping_id)
        created = None
        if const.ATTR_REMOVE in data:
            # delete a mapping
            res = self.store.get_mapping(mapping_id)
            if not res:
                return None
            await self.store.async_delete_mapping(mapping_id)
        elif mapping_id is not None and self.store.get_mapping(mapping_id):
            # modify a mapping
            await self.store.async_update_mapping(mapping_id, data)
            async_dispatcher_send(
                self.hass, const.DOMAIN + "_config_updated", mapping_id
            )
        else:
            # create a mapping
            created = await self.store.async_create_mapping(data)
            await self.store.async_get_config()

        return created

    def check_mapping_sources(self, mapping_id):
        """Check which data sources (weather service, sensor, static value) are present in a mapping.

        Args:
            mapping_id: The ID of the mapping to check.

        Returns:
            Tuple of booleans: (owm_in_mapping, sensor_in_mapping, static_in_mapping)

        """
        owm_in_mapping = False
        sensor_in_mapping = False
        static_in_mapping = False
        if mapping_id is not None:
            mapping = self.store.get_mapping(mapping_id)
            if mapping is not None:
                for the_map in mapping[const.MAPPING_MAPPINGS].values():
                    if not isinstance(the_map, str):
                        if (
                            the_map.get(const.MAPPING_CONF_SOURCE)
                            == const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
                        ):
                            owm_in_mapping = True
                        if (
                            the_map.get(const.MAPPING_CONF_SOURCE)
                            == const.MAPPING_CONF_SOURCE_SENSOR
                        ):
                            sensor_in_mapping = True
                        if (
                            the_map.get(const.MAPPING_CONF_SOURCE)
                            == const.MAPPING_CONF_SOURCE_STATIC_VALUE
                        ):
                            static_in_mapping = True
            else:
                _LOGGER.debug(
                    "[check_mapping_sources] sensor group %s is None", mapping_id
                )
            _LOGGER.debug(
                "check_mapping_sources for mapping_id %s returns OWM: %s, sensor: %s, static: %s",
                mapping_id,
                owm_in_mapping,
                sensor_in_mapping,
                static_in_mapping,
            )
        return owm_in_mapping, sensor_in_mapping, static_in_mapping

    def build_sensor_values_for_mapping(self, mapping):
        """Build a dictionary of sensor values for a given mapping by retrieving and converting sensor states from Home Assistant.

        Args:
            mapping: The mapping dictionary containing sensor configuration.

        Returns:
            dict: A dictionary of sensor keys and their corresponding metric values.

        """
        sensor_values = {}
        for key, the_map in mapping[const.MAPPING_MAPPINGS].items():
            if not isinstance(the_map, str):
                if the_map.get(
                    const.MAPPING_CONF_SOURCE
                ) == const.MAPPING_CONF_SOURCE_SENSOR and the_map.get(
                    const.MAPPING_CONF_SENSOR
                ):
                    # this mapping maps to a sensor, so retrieve its value from HA
                    sensor_id = the_map.get(const.MAPPING_CONF_SENSOR)
                    state = self.hass.states.get(sensor_id)
                    if state:
                        try:
                            val = float(state.state)
                            # Prefer the entity's *own* reported unit over the
                            # unit hand-picked in the sensor group: HA knows the
                            # sensor's real unit, and a mismatch there silently
                            # corrupts the value (e.g. a W/m2 solar sensor
                            # configured as MJ/day/m2 inflates ET ~12x). Fall
                            # back to the configured unit when the entity reports
                            # no unit or one we don't recognise for this field.
                            configured_unit = the_map.get(const.MAPPING_CONF_UNIT)
                            detected_unit = ha_unit_to_internal_unit(
                                state.attributes.get(ATTR_UNIT_OF_MEASUREMENT), key
                            )
                            unit = detected_unit or configured_unit
                            if (
                                detected_unit
                                and configured_unit
                                and detected_unit != configured_unit
                            ):
                                _LOGGER.info(
                                    "Sensor %s reports unit '%s' for %s; using it "
                                    "instead of the configured '%s'.",
                                    sensor_id,
                                    detected_unit,
                                    key,
                                    configured_unit,
                                )
                            # make sure to store the val as metric and do necessary conversions along the way
                            val = convert_mapping_to_metric(
                                val,
                                key,
                                unit,
                                self.hass.config.units is METRIC_SYSTEM,
                            )
                            # add val to sensor values
                            sensor_values[key] = val
                        except (ValueError, TypeError):
                            _LOGGER.debug(
                                "No / unknown value for sensor %s",
                                sensor_id,
                            )

        return sensor_values

    def build_static_values_for_mapping(self, mapping):
        """Build a dictionary of static values for a given mapping by retrieving and converting static values.

        Args:
            mapping: The mapping dictionary containing static value configuration.

        Returns:
            dict: A dictionary of sensor keys and their corresponding static metric values.

        """
        static_values = {}
        for key, the_map in mapping[const.MAPPING_MAPPINGS].items():
            if not isinstance(the_map, str):
                if (
                    the_map.get(const.MAPPING_CONF_SOURCE)
                    == const.MAPPING_CONF_SOURCE_STATIC_VALUE
                    and the_map.get(const.MAPPING_CONF_STATIC_VALUE) is not None
                ):
                    # this mapping maps to a static value, so return its value
                    val = float(the_map.get(const.MAPPING_CONF_STATIC_VALUE))
                    # first check we are not in metric mode already.
                    if self.hass.config.units is not METRIC_SYSTEM:
                        val = convert_mapping_to_metric(
                            val, key, the_map.get(const.MAPPING_CONF_UNIT), False
                        )
                    # add val to sensor values
                    static_values[key] = val
        return static_values

    async def async_update_zone_config(
        self, zone_id: int | None = None, data: dict | None = None
    ):
        """Update, create, or delete a zone configuration.

        Args:
            zone_id: The ID of the zone to update or delete.
            data: The configuration data for the mapping.

        """
        _LOGGER.debug("[async_update_zone_config]: updating zone %s", zone_id)
        if data is None:
            data = {}
        if zone_id is not None:
            zone_id = int(zone_id)
        if const.ATTR_REMOVE in data:
            # delete a zone
            zone = self.store.get_zone(zone_id)
            if not zone:
                return
            await self.store.async_delete_zone(zone_id)
            await self.async_remove_entity(zone_id)
            # Drop this zone's valve from the observed-watering watch list.
            self._schedule_observed_watering_setup()

        elif const.ATTR_CALCULATE in data:
            # calculate a specific zone
            _LOGGER.info("Calculating zone %s", zone_id)
            data.pop(const.ATTR_CALCULATE, None)
            # Obsolete: the shared buffer is consumed per-zone and pruned, never
            # cleared by a single zone's calculation.
            data.pop(const.ATTR_DELETE_WEATHER_DATA, None)

            zone = self.store.get_zone(zone_id)
            if zone is None:
                raise SmartIrrigationError(f"Zone {zone_id} not found")
            zone_name = zone.get(const.ZONE_NAME, str(zone_id))
            mapping_id = zone.get(const.ZONE_MAPPING)
            mapping = (
                self.store.get_mapping(mapping_id) if mapping_id is not None else None
            )
            if mapping is None or not mapping.get(const.MAPPING_DATA):
                if mapping_id is None:
                    msg = f"Zone '{zone_name}' has no mapping configured. Assign a mapping with sensor data before calculating."
                else:
                    msg = f"Zone '{zone_name}' has no sensor data yet. Wait for sensors to report values or check mapping '{mapping_id}'."
                _LOGGER.error("[async_update_zone_config] %s", msg)
                raise SmartIrrigationError(msg)

            # get forecast data if needed
            forecastdata = None
            modinst = await self.getModuleInstanceByID(zone.get(const.ZONE_MODULE))
            if modinst is None:
                msg = f"Zone '{zone_name}' has no calculation module configured. Assign a module before calculating."
                _LOGGER.error("[async_update_zone_config] %s", msg)
                raise SmartIrrigationError(msg)
            if modinst.name == "PyETO" and modinst.forecast_days > 0:
                if self.use_weather_service:
                    # get forecast info from OWM
                    forecastdata = await self.hass.async_add_executor_job(
                        self._WeatherServiceClient.get_forecast_data
                    )
                else:
                    msg = (
                        f"Zone '{zone_name}': PyETO is configured to use forecast data "
                        "but no weather service API is configured. "
                        "Either configure a weather service or set forecast_days to 0."
                    )
                    _LOGGER.error("[async_update_zone_config] %s", msg)
                    raise SmartIrrigationError(msg)

            # async_calculate_zone aggregates this zone's own window internally.
            await self.async_calculate_zone(zone_id, forecastdata)
        elif const.ATTR_CALCULATE_ALL in data:
            # calculate all zones
            _LOGGER.info("Calculating all zones")
            data.pop(const.ATTR_CALCULATE_ALL)
            await self._async_calculate_all()

        elif const.ATTR_UPDATE in data:
            _LOGGER.info("Updating zone %s", zone_id)
            await self._async_update_zone(zone_id)
        elif const.ATTR_UPDATE_ALL in data:
            _LOGGER.info("Updating all zones")
            await self._async_update_all()
        elif const.ATTR_RESET_ALL_BUCKETS in data:
            # reset all buckets
            _LOGGER.info("Resetting all buckets")
            data.pop(const.ATTR_RESET_ALL_BUCKETS)
            await self.handle_reset_all_buckets(None)
        elif const.ATTR_CLEAR_ALL_WEATHERDATA in data:
            # clear all weatherdata
            _LOGGER.info("Clearing all weatherdata")
            data.pop(const.ATTR_CLEAR_ALL_WEATHERDATA)
            await self.handle_clear_weatherdata(None)
        elif zone_id is not None and self.store.get_zone(zone_id):
            # modify a zone
            entry = await self.store.async_update_zone(zone_id, data)
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
            # make sure to update the HA entity here by listening to this in sensor.py.
            # this should be called by changes from the UI (by user) or by a calculation module (updating a duration), which should be done in python
        else:
            # create a zone
            entry = await self.store.async_create_zone(data)

            async_dispatcher_send(self.hass, const.DOMAIN + "_register_entity", entry)
            # Pick up the new zone's linked valve in the observed-watering watch.
            self._schedule_observed_watering_setup()

            await self.store.async_get_config()

    @callback
    def _reset_event_fired_today(self, *args):
        """Midnight callback: increment the days-since-irrigation counter."""
        self.hass.async_create_task(self._increment_days_since_irrigation())

    async def async_get_all_modules(self):
        """Get all ModuleEntries."""
        res = []
        mods = await self.hass.async_add_executor_job(loadModules, const.MODULE_DIR)
        for mod in mods:
            m = getattr(mods[mod]["module"], mods[mod]["class"])
            s = m(self.hass, None, {})
            res.append(
                {
                    "name": s.name,
                    "description": s.description,
                    "config": s.config,
                    "schema": s.schema_serialized(),
                }
            )
        return res

    async def async_remove_entity(self, zone_id: str):
        """Remove all entities (and the device) of the given zone from HA.

        Args:
            zone_id: The ID of the zone whose entities should be removed.

        """
        entity_registry = er.async_get(self.hass)
        zone_id = int(zone_id)
        data = self.hass.data[const.DOMAIN]
        trackers = (
            "zones",
            "bucket_sensors",
            "multiplier_numbers",
            "zone_extra_sensors",
            "zone_binary_sensors",
            "zone_buttons",
        )
        for key in trackers:
            tracked = data.get(key, {}).pop(zone_id, None)
            if tracked is None:
                continue
            entities = tracked if isinstance(tracked, list) else [tracked]
            for entity in entities:
                if entity_registry.async_get(entity.entity_id):
                    entity_registry.async_remove(entity.entity_id)
        # Drop the zone's device as well (it would linger empty otherwise).
        device_registry = dr.async_get(self.hass)
        device = device_registry.async_get_device(
            identifiers={(const.DOMAIN, f"{self.id}_zone_{zone_id}")}
        )
        if device:
            device_registry.async_remove_device(device.id)

    async def async_unload(self):
        """Remove all Smart Irrigation objects."""

        # Cancel all periodic timers so a reloaded coordinator doesn't ghost-write
        for unsub in [
            self._pending_track_update_unsub,
            self._track_auto_update_time_unsub,
            self._track_auto_calc_time_unsub,
            self._track_midnight_time_unsub,
        ]:
            if unsub:
                unsub()
        self._pending_track_update_unsub = None
        self._track_auto_update_time_unsub = None
        self._track_auto_calc_time_unsub = None
        self._track_midnight_time_unsub = None

        # Cancel the experimental observed-watering valve subscription.
        self.async_teardown_observed_watering()

        # Clear the in-memory per-zone entity trackers; the entity platform
        # manages entity state on unload. Registry entries are preserved so user
        # customizations (friendly names, areas) survive disable/re-enable cycles
        # (issue #506) — clearing these dicts only drops the live object refs.
        #
        # ALL trackers must be cleared, not just "zones": on a reload the replay
        # (`_register_entity`) re-adds a platform's entities only if it doesn't
        # think they already exist. The sensor platform keys that check on the
        # "zones" dict, so clearing only "zones" let sensors re-add while the
        # binary_sensor / button platforms (which dedup on their own tracker
        # dict) skipped the re-add — leaving those per-zone entities orphaned and
        # "unavailable" after every reload (issue #36).
        data = self.hass.data[const.DOMAIN]
        for key in (
            "zones",
            "bucket_sensors",
            "multiplier_numbers",
            "zone_extra_sensors",
            "zone_binary_sensors",
            "zone_buttons",
        ):
            tracker = data.get(key)
            if isinstance(tracker, dict):
                tracker.clear()

        # remove subscriptions for coordinator
        while self._subscriptions:
            self._subscriptions.pop()()

    async def async_delete_config(self):
        """Wipe Smart Irrigation storage."""
        await self.store.async_delete()

    async def _async_set_all_buckets(self, val=0):
        """Set all buckets to val."""
        zones = await self.store.async_get_zones()
        data = {}
        data[const.ATTR_SET_BUCKET] = {}
        data[const.ATTR_NEW_BUCKET_VALUE] = val

        for zone in zones:
            await self.async_update_zone_config(
                zone_id=zone.get(const.ZONE_ID), data=data
            )

    async def _async_set_all_multipliers(self, val=0):
        """Set all multipliers to val."""
        zones = await self.store.async_get_zones()
        data = {}
        data[const.ATTR_SET_MULTIPLIER] = {}
        data[const.ATTR_NEW_MULTIPLIER_VALUE] = val

        for zone in zones:
            await self.async_update_zone_config(
                zone_id=zone.get(const.ZONE_ID), data=data
            )
