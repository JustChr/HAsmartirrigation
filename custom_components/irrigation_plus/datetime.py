"""DateTime platform for Smart Irrigation integration.

A single hub-level "Pause until" control (WS-5): the rain-delay / vacation hold.
Setting it pauses all AUTOMATIC/scheduled irrigation until the chosen moment;
clearing it (or letting it pass) resumes. Explicit manual runs always bypass it.
"""

import logging
from datetime import datetime

import homeassistant.util.dt as dt_util
from homeassistant.components.datetime import DOMAIN as PLATFORM
from homeassistant.components.datetime import DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import const
from .entity import hub_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the Smart Irrigation datetime entities."""
    async_add_devices([SmartIrrigationRainDelayDateTime(hass)])


def _coordinator(hass: HomeAssistant):
    """The coordinator, or None when the integration is not (yet) set up."""
    try:
        return hass.data[const.DOMAIN]["coordinator"]
    except (KeyError, AttributeError):
        return None


class SmartIrrigationRainDelayDateTime(DateTimeEntity):
    """Pause all automatic irrigation until this moment (rain delay / hold)."""

    _attr_has_entity_name = True
    _attr_translation_key = "rain_delay"
    _attr_should_poll = False
    _attr_icon = "mdi:pause-circle-outline"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the hub-level rain-delay control."""
        self._hass = hass
        self.entity_id = f"{PLATFORM}.{const.DOMAIN}_rain_delay"

    async def async_added_to_hass(self) -> None:
        """Refresh whenever the config (and thus the hold) changes."""
        self.async_on_remove(
            async_dispatcher_connect(
                self._hass, const.DOMAIN + "_config_updated", self._async_updated
            )
        )

    @callback
    def _async_updated(self, *_args) -> None:
        self.async_schedule_update_ha_state()

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{const.DOMAIN}_rain_delay_until"

    @property
    def device_info(self) -> dict:
        """Group under the hub device."""
        return hub_device_info(self._hass)

    @property
    def native_value(self) -> datetime | None:
        """The instant automatic irrigation resumes, or None when not held."""
        coordinator = _coordinator(self._hass)
        if coordinator is None:
            return None
        raw = getattr(coordinator.store.config, "rain_delay_until", None)
        if not raw:
            return None
        parsed = dt_util.parse_datetime(raw)
        if parsed is None:
            return None
        # HA DateTimeEntity requires an aware datetime (it normalises to UTC).
        return dt_util.as_local(parsed) if parsed.tzinfo is None else parsed

    async def async_set_value(self, value: datetime) -> None:
        """Set the hold to the chosen moment."""
        coordinator = _coordinator(self._hass)
        if coordinator is None:
            _LOGGER.warning("Rain delay: coordinator not available")
            return
        await coordinator.async_set_rain_delay(value.isoformat())
