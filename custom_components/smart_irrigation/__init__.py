"""The Smart Irrigation Integration."""

import asyncio
import logging

# NB: alias the stdlib datetime class. This package ships a ``datetime.py``
# platform module (the rain-delay DateTimeEntity); importing that platform sets
# the ``datetime`` attribute on this package — which IS this module's global
# namespace — clobbering a global literally named ``datetime`` and breaking
# ``dt_datetime.now()`` at runtime. The alias keeps our global name collision-free.
from datetime import datetime as dt_datetime
from datetime import timedelta
from functools import partial

import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
)
from homeassistant.core import HomeAssistant, callback
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
from .continuous_update import ContinuousUpdateMixin
from .distributor import DistributorMixin
from .helpers import (
    altitudeToPressure,
    check_time,
    clamp_solar_to_clear_sky,
    convert_between,
    convert_mapping_to_metric,
    loadModules,
    resolve_sensor_unit,
    solar_reading_is_rate,
    to_absolute_pressure,
)
from .irrigation import IrrigationRunnerMixin
from .live_estimate import LiveEstimateMixin
from .master import MasterMixin
from .observed_watering import ObservedWateringMixin
from .panel import async_register_panel, async_remove_card_resource, remove_panel
from .scheduler import RecurringScheduleManager
from .self_closing import SelfClosingMixin
from .services import ServiceHandlersMixin, async_register_services
from .skip_conditions import SkipConditionsMixin
from .store import BUFFER_FLUSH_INTERVAL, SmartIrrigationStorage, async_get_registry
from .unit_system import convert_zone_values, unit_system_name
from .watering_calendar import WateringCalendarMixin
from .weathermodules.MetOfficeClient import MetOfficeClient
from .weathermodules.OpenMeteoClient import OpenMeteoClient
from .weathermodules.OWMClient import OWMClient
from .weathermodules.PirateWeatherClient import PirateWeatherClient
from .websockets import async_register_websockets

_LOGGER = logging.getLogger(__name__)

# How often a still-firing solar clamp is re-reported. Long enough not to spam a
# log, short enough that a sensor stuck for a day cannot pass unnoticed.
SOLAR_CLAMP_WARN_INTERVAL = timedelta(hours=1)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(const.DOMAIN)


async def async_setup(hass: HomeAssistant, config):
    """Track states and offer events for sensors."""
    # Ship the self-closing valve script blueprints into the user's blueprint
    # folder (copy-if-missing; never overwrites the user's own copies). Runs off
    # the event loop; failures are non-fatal.
    from pathlib import Path

    from .blueprint_install import install_bundled_blueprints

    src = Path(__file__).parent / "blueprints" / "script"
    dst = Path(hass.config.path("blueprints", "script", const.DOMAIN))
    await hass.async_add_executor_job(install_bundled_blueprints, src, dst)
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

    # Issue #67: convert stored zone values if HA's unit system changed while we
    # were not running (a configuration.yaml edit plus a restart fires no
    # core_config_updated event, so this is the ONLY place that path is caught).
    # Must precede the timers and both resume steps — every one of them reads
    # zone depths, and reading them under the wrong unit is the whole bug.
    await coordinator.async_reconcile_stored_unit_system()

    # Set up the auto update/calc/clear timers (awaited, not fire-and-forget).
    await coordinator.async_setup_timers()

    # Reconcile any self-closing runs that were in flight across a restart.
    await coordinator.async_resume_self_closing_runs()

    # Reconcile any in-flight distributor cycles across a restart (before any
    # schedule can dispatch a new one).
    await coordinator.async_resume_distributor_cycles()

    # Bug 2 (2026-07-06): defensively kill an orphaned master left on across a restart
    # (its off-timer is in-memory only and gone after the reboot). One-shot, gated on
    # master_off_after; defers to any still-running self-closing run. Runs AFTER both
    # resume steps so crashed cycles are already reconciled. See master.py.
    await coordinator.async_reconcile_master_after_restart()

    coordinator.previous_unit_system = hass.config.units
    hass.bus.async_listen(
        "core_config_updated", partial(async_handle_core_config_change, hass)
    )
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


async def async_handle_core_config_change(hass: HomeAssistant, event) -> None:
    """React to a live unit-system change made in the Home Assistant UI.

    This is the second of the two entry points for issue #67; the first is
    ``async_setup_entry``, which catches a ``configuration.yaml`` edit plus a
    restart (that path fires no ``core_config_updated`` event at all).

    Promoted out of ``async_setup_entry`` on 2026-08-03. As a nested closure it
    was unreachable from the tests — the one test that covered it had been
    skipped as "not importable" — and that is how an ``AttributeError`` in its
    own log line survived: ``UnitSystem`` has no public ``name``, so the
    handler died before it could dispatch, and a UI flip did nothing at all,
    not even refresh the displayed units. Reported by clarejor against
    v2026.07.11. Keep this a module-level function so it stays testable.
    """
    _LOGGER.debug("Core_config_updated fired: %s", event.data)
    domain_data = hass.data.get(const.DOMAIN)
    if not domain_data or "coordinator" not in domain_data:
        return

    coordinator = domain_data["coordinator"]
    current_unit_system = hass.config.units
    previous_unit_system = getattr(coordinator, "previous_unit_system", None)

    if previous_unit_system == current_unit_system:
        _LOGGER.debug("Core config updated but unit system unchanged")
        return

    _LOGGER.info(
        "Home Assistant unit system changed from %s to %s, updating Smart Irrigation",
        unit_system_name(previous_unit_system),
        unit_system_name(current_unit_system),
    )
    coordinator.previous_unit_system = current_unit_system

    # Safe even if we get here spuriously (a missing attribute, a duplicate
    # event): the conversion downstream is guarded by the PERSISTED unit
    # system, not by this comparison, so a redundant call converts nothing.
    await coordinator.async_handle_unit_system_change()


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
    # Harden against a missing coordinator so a config-entry reload can still
    # unload cleanly if the coordinator is gone from hass.data. Without this an
    # unguarded KeyError fails the unload (failed_unload) and only a full Home
    # Assistant restart can recover. Mirrors the guarded access in
    # async_remove_entry below.
    coordinator = hass.data[const.DOMAIN].get("coordinator")
    if coordinator is not None:
        await coordinator.async_unload()
    return True


async def async_remove_entry(hass: HomeAssistant, entry):
    """Remove Smart Irrigation config entry."""
    remove_panel(hass)
    # Uninstall only — never from async_unload_entry, which also runs on every
    # reload. Without this the Lovelace resource we registered outlived the
    # integration and every dashboard load 404'd on a card that was gone.
    try:
        await async_remove_card_resource(hass)
    except Exception:  # noqa: BLE001
        # Never let frontend cleanup block removal of the entry itself.
        _LOGGER.exception("Could not remove the Lovelace card resource")
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
    ContinuousUpdateMixin,
    SelfClosingMixin,
    MasterMixin,
    DistributorMixin,
):
    """Define an object to hold Smart Irrigation device.

    This is a plain coordinator: it does all its own scheduling (auto
    update/calc/clear timers, midnight tracking, and — when continuous updates
    are enabled — the per-sensor-group ingestion debounce in
    ContinuousUpdateMixin) and uses none of DataUpdateCoordinator's polling API
    (no update_interval, no _async_update_data, no listeners), so it does not
    inherit it.
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

        # Continuous (event-driven) sensor ingestion state (ContinuousUpdateMixin).
        # Off until async_setup_continuous_updates() subscribes. ``_targets`` maps
        # a sensor entity → the (sensor group, field) pairs it feeds,
        # ``_last_value`` holds the deadband reference per (group, field), and
        # ``_debounce_unsub`` the per-group cancel handles.
        self._continuous_unsub = None
        self._continuous_entities = frozenset()
        self._continuous_targets = {}
        self._continuous_debounce_unsub = {}
        self._continuous_last_value = {}
        self._continuous_flush_count = {}
        # Follow sensor-group edits: a changed sensor entity (or a toggled
        # feature flag) must re-target the subscription, exactly as above.
        self._subscriptions.append(
            async_dispatcher_connect(
                hass,
                const.DOMAIN + "_config_updated",
                self._schedule_continuous_updates_setup,
            )
        )
        self._track_auto_calc_time_unsub = None
        self._track_auto_update_time_unsub = None
        self._track_midnight_time_unsub = None
        self._pending_track_update_unsub = None  # cancel handle for async_call_later
        self._track_buffer_flush_unsub = None
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
        # Event-driven weather-sensor ingestion (no-op unless enabled).
        await self.async_setup_continuous_updates()
        # Reading appends deliberately schedule no store write (store.buffers), so
        # something has to. A no-op tick when nothing was appended.
        if self._track_buffer_flush_unsub is None:
            self._track_buffer_flush_unsub = async_track_time_interval(
                self.hass,
                self._flush_reading_buffers,
                timedelta(seconds=BUFFER_FLUSH_INTERVAL),
            )

    @callback
    def _flush_reading_buffers(self, *args) -> None:
        """Persist sensor readings that no other write has carried out yet."""
        self.store.async_flush_buffers()

    @callback
    def _schedule_observed_watering_setup(self, *args) -> None:
        """Re-evaluate the observed-watering subscription after a config change."""
        self.hass.async_create_task(self.async_setup_observed_watering())

    @callback
    def _schedule_continuous_updates_setup(self, *args) -> None:
        """Re-evaluate the weather-sensor subscription after a config change."""
        self.hass.async_create_task(self.async_setup_continuous_updates())

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

        for distributor in await self.store.async_get_distributors():
            async_dispatcher_send(
                self.hass, const.DOMAIN + "_distributor_register_entity", distributor
            )
            # E4: (re)arm the opt-in inlet-watch listener once per distributor on
            # setup, mirroring the entity replay above.
            self._dist_refresh_inlet_watch(distributor)

    def _current_unit_system_name(self):
        """The unit system stored zone values would be written under right now."""
        return unit_system_name(self.hass.config.units)

    async def async_reconcile_stored_unit_system(self):
        """Convert stored zone values when the unit system has changed (issue #67).

        Zone depths, size and throughput are stored in DISPLAY units, so a flip
        between metric and US customary reinterprets every one of them — by 25.4,
        10.764 and 3.785 respectively — with nothing logged and the same digits
        still shown in the panel. The worst of it is ``bucket_threshold``: a -10
        written as mm becomes -10 inches, a deficit no bucket reaches, and every
        deficit-gated run stops silently.

        Called from BOTH ends so neither path is missed:

        * ``async_setup_entry``, which catches a change made in
          ``configuration.yaml`` plus a restart. That path fires no
          ``core_config_updated`` event at all, and the in-memory
          ``previous_unit_system`` is re-seeded from ``hass.config.units`` on
          every start, so it cannot see the change. This is the case the issue
          was actually reproduced on.
        * ``async_handle_unit_system_change``, for a live change in the UI.

        Idempotent because the guard is the PERSISTED value, not an event: a
        second call finds stored == current and does nothing. That also makes it
        safe to run on every startup.
        """
        current = self._current_unit_system_name()
        stored = getattr(self.store.config, const.CONF_STORED_UNIT_SYSTEM, None)

        if stored is None:
            # Pre-v13 store that never got the migration (or a test double).
            # Record where we are; converting would be a guess.
            await self.store.async_update_config(
                {const.CONF_STORED_UNIT_SYSTEM: current}
            )
            return 0

        if stored == current:
            return 0

        _LOGGER.warning(
            "Home Assistant unit system changed from %s to %s — converting stored "
            "zone values so they keep their meaning (issue #67)",
            stored,
            current,
        )

        converted = 0
        for zone in await self.store.async_get_zones():
            changes = convert_zone_values(
                zone, to_metric=current == const.UNIT_SYSTEM_METRIC
            )
            if not changes:
                continue
            zone_id = zone.get(const.ZONE_ID)
            await self.store.async_update_zone(zone_id, changes)
            converted += 1
            _LOGGER.info(
                "Zone %s: converted %s to %s",
                zone_id,
                ", ".join(sorted(changes)),
                current,
            )
            # Tell the entities the zone changed underneath them. Reported by
            # clarejor against v2026.08.02: `async_update_zone` only schedules a
            # save, so after a live flip the store was right while the bucket
            # sensor and the duration sensor's attributes still showed the
            # PRE-conversion digits — now under the NEW unit label, so a factor
            # of 25.4 out and indistinguishable from a real reading. Their own
            # `_unit_system_changed` handlers cannot fix it: neither class
            # defines `async_update`, so `force_refresh=True` re-renders the
            # cached value. `_config_updated` with the zone id is the signal
            # they already re-read the store on. Sent AFTER the write, per zone,
            # and only when something actually converted.
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)

        # Persist LAST: if the loop raises partway, the stored system still says
        # the old one, so the next startup retries rather than leaving half the
        # zones converted and the bookkeeping claiming the job is done.
        await self.store.async_update_config({const.CONF_STORED_UNIT_SYSTEM: current})
        _LOGGER.warning(
            "Unit system conversion complete: %s zone(s) updated", converted
        )
        return converted

    async def async_handle_unit_system_change(self):
        """Handle changes to the Home Assistant unit system."""
        _LOGGER.info("Processing unit system change for Smart Irrigation")

        # Convert the stored zone values BEFORE anything re-reads them, so the
        # refreshed entities and panel show the converted numbers rather than
        # the old digits reinterpreted in the new unit.
        await self.async_reconcile_stored_unit_system()

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

    def _apply_pressure_type(self, mapping, weatherdata):
        """Normalise a polled row's Pressure to absolute, in place.

        Sensor/static sources report whatever the station is configured for, so
        a relative (sea-level) reading has to be corrected for elevation before
        it joins the buffer — see helpers.to_absolute_pressure for why the field
        must carry exactly one quantity. The event-driven path in
        continuous_update calls that same helper per reading.
        """
        if not weatherdata:
            return
        mapping_mappings = (mapping or {}).get(const.MAPPING_MAPPINGS) or {}
        pressure_map = mapping_mappings.get(const.MAPPING_PRESSURE) or {}
        elevation = self.hass.config.as_dict().get(CONF_ELEVATION)
        if const.MAPPING_PRESSURE in weatherdata:
            weatherdata[const.MAPPING_PRESSURE] = to_absolute_pressure(
                weatherdata[const.MAPPING_PRESSURE],
                const.MAPPING_PRESSURE,
                pressure_map,
                elevation,
            )
        elif (
            pressure_map.get(const.MAPPING_CONF_PRESSURE_TYPE)
            == const.MAPPING_CONF_PRESSURE_RELATIVE
        ):
            # Configured relative but the source produced nothing this tick:
            # standard-atmosphere pressure for the site is a better input to the
            # psychrometric constant than leaving the calc module short a field.
            weatherdata[const.MAPPING_PRESSURE] = altitudeToPressure(elevation)

    def _clamp_solar_reading(self, value, *, now=None):
        """Ceiling one ingested solar-radiation reading at clear sky.

        Shared by both writers of the buffer's Solar Radiation field, the same
        way ``to_absolute_pressure`` is shared for Pressure: a buffer holding
        clamped and unclamped rows would aggregate to a mix of the two.

        Called only where the reading's resolved unit is known and
        ``solar_reading_is_rate`` says it is one. Nothing else reaches here: a
        static value and a weather service's radiation both bypass the two
        conversion sites, so their exemption is structural rather than a check
        that has to be kept in step with them.

        The clamp is reported at WARNING and re-reported hourly for as long as it
        keeps firing. Deliberately not once per lifetime: PyETO's clear-sky clamp
        warns exactly once per module instance, and that is how a solar
        aggregation bug stayed hidden for months while its symptom was being
        clamped away every day. A sensor that needs clamping is a sensor to look
        at, so it has to stay visible.
        """
        if value is None:
            return value
        if now is None:
            now = dt_datetime.now()
        offset = dt_util.now().utcoffset()
        clamped = clamp_solar_to_clear_sky(
            value,
            now,
            getattr(self, "_effective_latitude", None),
            getattr(self, "_effective_longitude", None),
            getattr(self, "_effective_elevation", None),
            offset.total_seconds() / 3600.0 if offset else 0.0,
        )
        if clamped < value:
            last = getattr(self, "_solar_clamp_warned_at", None)
            if last is None or now - last >= SOLAR_CLAMP_WARN_INTERVAL:
                self._solar_clamp_warned_at = now
                _LOGGER.warning(
                    "Solar radiation reading %.2f MJ/day/m2 exceeds the clear-sky "
                    "maximum for %s and was clamped to %.2f. Check the Solar "
                    "Radiation sensor: a stuck or miscalibrated pyranometer reads "
                    "as extra evapotranspiration and under-waters every zone in "
                    "the sensor group.",
                    value,
                    now.isoformat(timespec="seconds"),
                    clamped,
                )
        return clamped

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
                self._apply_pressure_type(mapping, weatherdata)

            # add the weatherdata value to the mappings sensor values
            if mapping is not None and weatherdata is not None:
                weatherdata[const.RETRIEVED_AT] = dt_datetime.now()
                # Appends the row in place and schedules no write of its own; it
                # reaches disk with the zone bookkeeping below (or, failing that,
                # the buffer flush timer). See store.append_mapping_reading.
                self.store.append_mapping_reading(mapping_id, weatherdata)
                _LOGGER.debug(
                    "async_update_all for mapping %s new weatherdata: %s",
                    mapping_id,
                    weatherdata,
                )
                updated_at = dt_datetime.now()
                await self.store.async_update_mapping(
                    mapping_id, {const.MAPPING_DATA_LAST_UPDATED: updated_at}
                )
                # store last updated and number of data points in the zone here.
                # The oldest row is the carried-forward boundary reading, not a
                # new one, hence the -1.
                row_count = self.store.get_mapping_row_count(mapping_id) or 0
                changes_to_zone = {
                    const.ZONE_LAST_UPDATED: updated_at,
                    const.ZONE_NUMBER_OF_DATA_POINTS: max(row_count - 1, 0),
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
        # Strict identity check so a test double / absent attribute is a safe
        # "off" (same guard the mixin's setup uses).
        continuous_updates = (
            getattr(self.store.config, const.CONF_CONTINUOUS_UPDATES, False) is True
        )
        # loop over the mappings and store sensor data
        for mapping_id in mappings:
            (
                owm_in_mapping,
                sensor_in_mapping,
                static_in_mapping,
            ) = self.check_mapping_sources(mapping_id=mapping_id)
            if (
                continuous_updates
                and sensor_in_mapping
                and not owm_in_mapping
                and not static_in_mapping
            ):
                # PURE sensor group: the event path is its whole data path, so a
                # poll row here is duplication — extra buffer rows, extra store
                # writes, and a spot sample that pulls the aggregate toward
                # whatever the sensor happened to read on the tick.
                #
                # Both exclusions are required. A weather-service field only
                # arrives by API call and the event path never fetches it (one
                # call per sensor change could cost real money). A STATIC field is
                # only ever written by this poll — altmenorg's rule ignored that
                # because its debounced update re-appended static values; ours
                # doesn't, so skipping a mixed sensor+static group would drop the
                # static fields out of the buffer entirely and leave the calc
                # module short an input.
                _LOGGER.debug(
                    "[async_update_all] continuous updates on and sensor group %s "
                    "is sensor-only — already covered by the event path, skipping "
                    "the poll",
                    mapping_id,
                )
                continue
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
                self._apply_pressure_type(mapping, weatherdata)

            # add the weatherdata value to the mappings sensor values
            if mapping is not None and weatherdata is not None:
                weatherdata[const.RETRIEVED_AT] = dt_datetime.now()
                # See _async_update_zone: the append is O(1) and writes nothing;
                # the per-zone writes below are what carry it to disk.
                self.store.append_mapping_reading(mapping_id, weatherdata)
                _LOGGER.debug(
                    "async_update_all for mapping %s new weatherdata: %s",
                    mapping_id,
                    weatherdata,
                )
                # store last updated and number of data points in the zone here.
                row_count = self.store.get_mapping_row_count(mapping_id) or 0
                changes_to_zone = {
                    const.ZONE_LAST_UPDATED: dt_datetime.now(),
                    const.ZONE_NUMBER_OF_DATA_POINTS: max(row_count - 1, 0),
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

    def _mapping_source_changed(self, mapping_id: int, changes: dict) -> bool:
        """Return True if ``changes`` switches the source/sensor of any quantity.

        Only the per-quantity source config (``MAPPING_MAPPINGS``) is inspected:
        a change to a quantity's ``source`` type or ``sensorentity`` makes the
        buffered readings incomparable to the new ones. Name-only or other edits
        leave the buffer intact. A differing (or missing) source/sensor value
        within a sent quantity counts as changed, erring toward invalidation
        (safe — the buffer simply refills) rather than risking a mixed-source
        aggregate.
        """
        new_mappings = changes.get(const.MAPPING_MAPPINGS)
        if not isinstance(new_mappings, dict):
            return False
        old = self.store.get_mapping(mapping_id)
        if not old:
            return False
        old_mappings = old.get(const.MAPPING_MAPPINGS) or {}
        for quantity, new_cfg in new_mappings.items():
            if not isinstance(new_cfg, dict):
                continue
            # A quantity's stored value may be a legacy bare string rather than a
            # dict (the rest of the integration guards this the same way, e.g.
            # check_mapping_sources). Treat a non-dict old value as empty, which
            # makes the comparison report "changed" — the safe, invalidating side.
            old_cfg = old_mappings.get(quantity)
            if not isinstance(old_cfg, dict):
                old_cfg = {}
            if old_cfg.get(const.MAPPING_CONF_SOURCE) != new_cfg.get(
                const.MAPPING_CONF_SOURCE
            ) or old_cfg.get(const.MAPPING_CONF_SENSOR) != new_cfg.get(
                const.MAPPING_CONF_SENSOR
            ):
                return True
        return False

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
            # A source/sensor switch makes the buffered readings incomparable to
            # the new ones: a delta / Riemann-sum aggregate would read the
            # discontinuity as a huge jump (switching a rain sensor from a rate
            # to a cumulative total once produced a ~3202 mm "rainfall"). Clear
            # this mapping's shared buffer and re-anchor the consuming zones'
            # watermarks to now — a scoped variant of _async_clear_all_weatherdata.
            source_changed = self._mapping_source_changed(mapping_id, data)
            if source_changed:
                # Clearing MAPPING_DATA alone is no longer enough: the aggregation
                # now also reads MAPPING_DATA_LAST_ENTRY as a carry-forward, so a
                # value captured from the OLD sensor would survive the wipe and
                # re-introduce exactly the discontinuity described above. It can't
                # simply be dropped — async_update_mapping merges any key the
                # caller omits straight back in — so each stale key is overwritten
                # with None, which aggregate_window ignores. A fresh reading from
                # the new source replaces it.
                stale = (self.store.get_mapping(mapping_id) or {}).get(
                    const.MAPPING_DATA_LAST_ENTRY
                ) or {}
                data = {
                    **data,
                    const.MAPPING_DATA: [],
                    const.MAPPING_DATA_LAST_ENTRY: dict.fromkeys(stale),
                }
            await self.store.async_update_mapping(mapping_id, data)
            if source_changed:
                now = dt_datetime.now()
                for zone_id in await self._get_zones_that_use_this_mapping(mapping_id):
                    await self.store.async_update_zone(
                        zone_id,
                        {
                            const.ZONE_LAST_CONSUMED: now,
                            # Same reason as _async_clear_all_weatherdata: the
                            # count is derived from the buffer this just emptied,
                            # so leaving it would report data points that no
                            # longer exist.
                            const.ZONE_NUMBER_OF_DATA_POINTS: 0,
                        },
                    )
                    # Per ZONE, not just once per mapping. The zone sensors cache
                    # their values and re-read only when this signal carries their
                    # own id, so the mapping-scoped dispatch below refreshes at
                    # most the one zone whose id happens to equal mapping_id and
                    # leaves every other consumer showing counts for readings that
                    # no longer exist.
                    async_dispatcher_send(
                        self.hass, const.DOMAIN + "_config_updated", zone_id
                    )
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
                            # Effective unit = the entity's own reported unit when
                            # we recognise it, else the one configured in the
                            # sensor group (see resolve_sensor_unit for why). The
                            # rule is shared with the event-driven append path so
                            # both can't disagree about the same sensor's unit.
                            unit = resolve_sensor_unit(
                                key,
                                the_map.get(const.MAPPING_CONF_UNIT),
                                state.attributes.get(ATTR_UNIT_OF_MEASUREMENT),
                                sensor_id,
                            )
                            # make sure to store the val as metric and do necessary conversions along the way
                            val = convert_mapping_to_metric(
                                val,
                                key,
                                unit,
                                self.hass.config.units is METRIC_SYSTEM,
                            )
                            # Clamped here rather than on the merged row because
                            # this is where the reading's RESOLVED unit is known:
                            # a daily-total sensor must not be measured against
                            # an instantaneous clear sky, and a sensor configured
                            # MJ/day but actually reporting W/m2 must still be.
                            if key == const.MAPPING_SOLRAD and solar_reading_is_rate(
                                unit
                            ):
                                val = self._clamp_solar_reading(val)
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
            if mapping is None or not self.store.get_mapping_row_count(mapping_id):
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
            old_zone = self.store.get_zone(zone_id)
            entry = await self.store.async_update_zone(zone_id, data)
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
            for did in {
                old_zone.get(const.ZONE_DISTRIBUTOR_ID),
                entry.get(const.ZONE_DISTRIBUTOR_ID),
            }:
                if did is not None:
                    async_dispatcher_send(
                        self.hass, const.DOMAIN + "_distributor_updated", int(did)
                    )
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
            self._track_buffer_flush_unsub,
        ]:
            if unsub:
                unsub()
        self._pending_track_update_unsub = None
        self._track_auto_update_time_unsub = None
        self._track_auto_calc_time_unsub = None
        self._track_midnight_time_unsub = None
        self._track_buffer_flush_unsub = None

        # Cancel the experimental observed-watering valve subscription.
        self.async_teardown_observed_watering()

        # Cancel the continuous-update sensor subscription AND its pending
        # debounce timers — a surviving async_call_later would fire against this
        # dead coordinator and ghost-write to the store.
        self.async_teardown_continuous_updates()

        # Release the recurring-schedule listeners. These are plain HA event
        # listeners (not entry-scoped), so nothing else cancels them: a reload
        # would otherwise leave the previous manager armed against the previous
        # coordinator and fire every schedule twice. Guarded because a partially
        # constructed coordinator must still unload cleanly (a failed unload is
        # only recoverable by a full HA restart).
        manager = getattr(self, "recurring_schedule_manager", None)
        if manager is not None:
            await manager.async_unload()

        # Master holds are in-memory refcounts for runs this coordinator owns.
        # A reload builds a new coordinator, so carrying them over would strand
        # the pump on forever; the boot path re-derives real state from the
        # persisted self-closing / distributor records
        # (async_reconcile_master_after_restart).
        self._master_release_all()

        # E4: cancel all opt-in distributor inlet-watch listeners so a reloaded
        # coordinator doesn't leave stale state-change subscriptions behind.
        for unsub in getattr(self, "_dist_inlet_watchers", {}).values():
            unsub()
        if hasattr(self, "_dist_inlet_watchers"):
            self._dist_inlet_watchers.clear()

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
