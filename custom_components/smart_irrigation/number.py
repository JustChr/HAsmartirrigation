"""Number platform for Smart Irrigation integration — exposes per-zone multiplier."""

import contextlib
import logging

from homeassistant.components.number import DOMAIN as NUMBER_PLATFORM
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import slugify

from . import const

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up Smart Irrigation number entities (multiplier per zone)."""

    @callback
    def async_add_number_entity(config: dict) -> None:
        """Add multiplier number entity for each zone."""
        entity_id = "{}.{}_multiplier".format(
            NUMBER_PLATFORM,
            const.DOMAIN + "_" + slugify(config["name"]),
        )
        number_entity = SmartIrrigationZoneMultiplierEntity(
            hass=hass,
            entity_id=entity_id,
            zone_id=config[const.ZONE_ID],
            zone_name=config[const.ZONE_NAME],
            multiplier=config.get(const.ZONE_MULTIPLIER, 1.0),
        )
        if const.DOMAIN in hass.data:
            hass.data[const.DOMAIN].setdefault("multiplier_numbers", {})[
                config["id"]
            ] = number_entity
            async_add_devices([number_entity])

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass, const.DOMAIN + "_register_entity", async_add_number_entity
        )
    )
    async_dispatcher_send(hass, const.DOMAIN + "_number_platform_loaded")


class SmartIrrigationZoneMultiplierEntity(NumberEntity, RestoreEntity):
    """Number entity exposing the per-zone irrigation multiplier."""

    _attr_native_min_value = 0.0
    _attr_native_max_value = 10.0
    _attr_native_step = 0.1
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        hass: HomeAssistant,
        entity_id: str,
        zone_id: int,
        zone_name: str,
        multiplier: float,
    ) -> None:
        """Initialize the multiplier number entity."""
        self._hass = hass
        self.entity_id = entity_id
        self._zone_id = zone_id
        self._zone_name = zone_name
        self._multiplier = multiplier

        async_dispatcher_connect(
            hass, const.DOMAIN + "_config_updated", self._async_update_multiplier
        )

    @callback
    def _async_update_multiplier(self, zone_id=None) -> None:
        """Refresh multiplier value when zone config changes."""
        if self._zone_id == zone_id and self.hass and self.hass.data:
            zone = self.hass.data[const.DOMAIN]["coordinator"].store.get_zone(
                self._zone_id
            )
            if zone:
                self._multiplier = zone.get(const.ZONE_MULTIPLIER, self._multiplier)
                self._zone_name = zone.get(const.ZONE_NAME, self._zone_name)
                self.async_schedule_update_ha_state(force_refresh=True)

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{const.DOMAIN}_{self._zone_id}_multiplier"

    @property
    def name(self) -> str:
        """Return friendly name."""
        return f"{self._zone_name} Multiplier"

    @property
    def icon(self) -> str:
        """Return icon."""
        return "mdi:multiplication"

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def native_value(self) -> float:
        """Return current multiplier."""
        return round(self._multiplier, 2)

    async def async_set_native_value(self, value: float) -> None:
        """Persist new multiplier to the zone store and notify."""
        value = round(value, 2)
        await self.hass.data[const.DOMAIN]["coordinator"].store.async_update_zone(
            self._zone_id, {const.ZONE_MULTIPLIER: value}
        )
        self._multiplier = value
        self.async_write_ha_state()
        async_dispatcher_send(
            self.hass, const.DOMAIN + "_config_updated", self._zone_id
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return zone identification attributes."""
        return {
            "zone_id": self._zone_id,
            "zone_name": self._zone_name,
        }

    @property
    def device_info(self) -> dict:
        """Return device info matching the zone duration sensor."""
        coordinator_id = "smart_irrigation"
        if (
            hasattr(self, "hass")
            and self.hass is not None
            and hasattr(self.hass, "data")
            and const.DOMAIN in self.hass.data
        ):
            try:
                coordinator = self.hass.data[const.DOMAIN].get("coordinator")
                if coordinator and hasattr(coordinator, "id"):
                    coordinator_id = coordinator.id
            except (KeyError, AttributeError, RuntimeError):
                pass

        return {
            "identifiers": {(const.DOMAIN, coordinator_id)},
            "name": const.NAME,
            "model": const.NAME,
            "sw_version": const.VERSION,
            "manufacturer": const.MANUFACTURER,
        }

    async def async_added_to_hass(self) -> None:
        """Restore previous state if available."""
        _LOGGER.debug("%s is added to hass", self.entity_id)
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (
            "unknown",
            "unavailable",
        ):
            with contextlib.suppress(ValueError, TypeError):
                self._multiplier = float(last_state.state)
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_will_remove_from_hass(self) -> None:
        """Handle removal."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("%s is removed from hass", self.entity_id)
