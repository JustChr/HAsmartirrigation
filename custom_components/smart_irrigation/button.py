"""Button platform for Smart Irrigation integration.

Per zone (on the zone's device): irrigate this zone now (bypasses skip
conditions, like the panel's button / the irrigate_now service).

Global (on the hub device): irrigate all zones now, recalculate all zones,
refresh weather data — mirroring the three global dashboard actions.
"""

import logging

from homeassistant.components.button import DOMAIN as PLATFORM
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from . import const
from .entity import hub_device_info, zone_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up Smart Irrigation button entities."""

    @callback
    def async_add_button_entity(config: dict) -> None:
        """Add the per-zone irrigate-now button for each registered zone."""
        if const.DOMAIN not in hass.data:
            return
        registered = hass.data[const.DOMAIN].setdefault("zone_buttons", {})
        if config["id"] in registered:
            return
        base = const.DOMAIN + "_" + slugify(config["name"])
        entities = [
            SmartIrrigationZoneIrrigateNowButton(
                hass, f"{PLATFORM}.{base}_irrigate_now", config
            ),
            SmartIrrigationZoneResetUsageButton(
                hass, f"{PLATFORM}.{base}_reset_usage", config
            ),
        ]
        registered[config["id"]] = entities
        async_add_devices(entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass, const.DOMAIN + "_register_entity", async_add_button_entity
        )
    )

    # Global actions live on the hub device and exist once.
    async_add_devices(
        [
            SmartIrrigationIrrigateAllButton(hass),
            SmartIrrigationCalculateAllButton(hass),
            SmartIrrigationUpdateWeatherButton(hass),
            SmartIrrigationDelay24hButton(hass),
            SmartIrrigationDelay48hButton(hass),
            SmartIrrigationResumeButton(hass),
        ]
    )


def _coordinator(hass: HomeAssistant):
    """The coordinator, or None when the integration is not (yet) set up."""
    try:
        return hass.data[const.DOMAIN]["coordinator"]
    except (KeyError, AttributeError):
        return None


class SmartIrrigationZoneButton(ButtonEntity):
    """Base for per-zone action buttons (grouped on the zone's device).

    ``suffix`` is the unique_id / entity_id suffix and the entity
    translation_key (they match for the per-zone buttons).
    """

    _attr_has_entity_name = True
    _attr_should_poll = False
    suffix = ""

    def __init__(self, hass: HomeAssistant, entity_id: str, zone: dict) -> None:
        """Initialize from the zone config dict."""
        self._hass = hass
        self.entity_id = entity_id
        self._zone_id = zone[const.ZONE_ID]
        self._zone_name = zone[const.ZONE_NAME]
        self._attr_translation_key = self.suffix

        async_dispatcher_connect(
            hass, const.DOMAIN + "_config_updated", self._async_zone_updated
        )

    @callback
    def _async_zone_updated(self, zone_id=None):
        """Track zone renames so the friendly name stays current."""
        if self._zone_id != zone_id or not (self.hass and self.hass.data):
            return
        zone = self.hass.data[const.DOMAIN]["coordinator"].store.get_zone(self._zone_id)
        if zone:
            self._zone_name = zone.get(const.ZONE_NAME, self._zone_name)
            self.async_schedule_update_ha_state()

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{const.DOMAIN}_{self._zone_id}_{self.suffix}"

    @property
    def device_info(self) -> dict:
        """Group under the per-zone device."""
        return zone_device_info(self._hass, self._zone_id, self._zone_name)

    @property
    def extra_state_attributes(self) -> dict:
        """Return zone identification attributes."""
        return {
            "zone_id": self._zone_id,
            "zone_name": self._zone_name,
        }


class SmartIrrigationZoneIrrigateNowButton(SmartIrrigationZoneButton):
    """Start an immediate irrigation run for one zone."""

    suffix = "irrigate_now"
    _attr_icon = "mdi:sprinkler"

    async def async_press(self) -> None:
        """Irrigate this zone now (skip conditions bypassed)."""
        coordinator = _coordinator(self._hass)
        if coordinator is None:
            _LOGGER.warning("Irrigate now: coordinator not available")
            return
        await coordinator.async_irrigate_now(str(self._zone_id))


class SmartIrrigationZoneResetUsageButton(SmartIrrigationZoneButton):
    """Zero this zone's cumulative water-usage total and clear its run log."""

    suffix = "reset_usage"
    _attr_icon = "mdi:restart"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    async def async_press(self) -> None:
        """Reset the zone's water-usage counter and run history."""
        coordinator = _coordinator(self._hass)
        if coordinator is None:
            _LOGGER.warning("Reset usage: coordinator not available")
            return
        await coordinator.async_reset_water_usage(self._zone_id)


class SmartIrrigationHubButton(ButtonEntity):
    """Base for the global hub-device action buttons.

    ``suffix`` is both the unique_id/entity_id suffix and the entity
    translation_key (they match for the hub buttons).
    """

    _attr_has_entity_name = True
    _attr_should_poll = False
    suffix = ""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the hub button."""
        self._hass = hass
        self.entity_id = f"{PLATFORM}.{const.DOMAIN}_{self.suffix}"
        self._attr_translation_key = self.suffix

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{const.DOMAIN}_{self.suffix}"

    @property
    def device_info(self) -> dict:
        """Group under the hub device."""
        return hub_device_info(self._hass)


class SmartIrrigationIrrigateAllButton(SmartIrrigationHubButton):
    """Water all zones now (bypasses skip conditions)."""

    suffix = "irrigate_all"
    _attr_icon = "mdi:sprinkler-variant"

    async def async_press(self) -> None:
        """Irrigate all eligible zones now."""
        coordinator = _coordinator(self._hass)
        if coordinator is not None:
            await coordinator.async_irrigate_now()


class SmartIrrigationCalculateAllButton(SmartIrrigationHubButton):
    """Recalculate the durations of all automatic zones."""

    suffix = "calculate_all"
    _attr_icon = "mdi:calculator"

    async def async_press(self) -> None:
        """Run the daily calculation for all automatic zones."""
        coordinator = _coordinator(self._hass)
        if coordinator is not None:
            await coordinator._async_calculate_all()  # noqa: SLF001


class SmartIrrigationUpdateWeatherButton(SmartIrrigationHubButton):
    """Collect fresh weather data for all automatic zones."""

    suffix = "update_weather"
    _attr_icon = "mdi:weather-cloudy-arrow-right"

    async def async_press(self) -> None:
        """Fetch and store fresh weather data."""
        coordinator = _coordinator(self._hass)
        if coordinator is not None:
            await coordinator._async_update_all()  # noqa: SLF001


class SmartIrrigationDelay24hButton(SmartIrrigationHubButton):
    """Pause all automatic irrigation for 24 hours (rain delay)."""

    suffix = "delay_24h"
    _attr_icon = "mdi:weather-rainy"

    async def async_press(self) -> None:
        """Hold automatic irrigation for 24 hours from now."""
        coordinator = _coordinator(self._hass)
        if coordinator is not None:
            await coordinator.async_delay_hours(24)


class SmartIrrigationDelay48hButton(SmartIrrigationHubButton):
    """Pause all automatic irrigation for 48 hours (rain delay)."""

    suffix = "delay_48h"
    _attr_icon = "mdi:weather-pouring"

    async def async_press(self) -> None:
        """Hold automatic irrigation for 48 hours from now."""
        coordinator = _coordinator(self._hass)
        if coordinator is not None:
            await coordinator.async_delay_hours(48)


class SmartIrrigationResumeButton(SmartIrrigationHubButton):
    """Resume automatic irrigation (clear any active rain delay)."""

    suffix = "resume_irrigation"
    _attr_icon = "mdi:play-circle-outline"

    async def async_press(self) -> None:
        """Clear the rain-delay hold."""
        coordinator = _coordinator(self._hass)
        if coordinator is not None:
            await coordinator.async_clear_rain_delay()
