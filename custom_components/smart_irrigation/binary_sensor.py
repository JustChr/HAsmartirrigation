"""Binary sensor platform for Smart Irrigation integration.

Per zone (on the zone's device):
- irrigation needed: mirrors the runner's deficit gate (enabled, duration > 0,
  bucket below the threshold) — "would this zone water if a run started now".
- watering now: mirrors the zone's linked valve/switch state.

Global (on the hub device):
- irrigation needed: any zone needs irrigation.
"""

import logging

from homeassistant.components.binary_sensor import DOMAIN as PLATFORM
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import slugify

from . import const
from .entity import hub_device_info, zone_device_info

_LOGGER = logging.getLogger(__name__)

# Linked-entity states that count as actively watering (switch on, valve open).
_WATERING_STATES = ("on", "open", "opening")


def _zone_needs_irrigation(zone: dict) -> bool:
    """The runner's deficit gate: enabled, duration > 0, bucket below threshold."""
    if not zone or zone.get(const.ZONE_STATE) == const.ZONE_STATE_DISABLED:
        return False
    if (zone.get(const.ZONE_DURATION) or 0) <= 0:
        return False
    return (zone.get(const.ZONE_BUCKET) or 0) < (
        zone.get(const.ZONE_BUCKET_THRESHOLD) or 0
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up Smart Irrigation binary sensor entities."""

    @callback
    def async_add_binary_sensor_entities(config: dict) -> None:
        """Add the per-zone binary sensors for each registered zone."""
        base = "{}.{}".format(PLATFORM, const.DOMAIN + "_" + slugify(config["name"]))
        if const.DOMAIN not in hass.data:
            return
        registered = hass.data[const.DOMAIN].setdefault("zone_binary_sensors", {})
        if config["id"] in registered:
            return
        entities = [
            SmartIrrigationZoneIrrigationNeededSensor(
                hass, f"{base}_irrigation_needed", config
            ),
            SmartIrrigationZoneWateringNowSensor(hass, f"{base}_watering_now", config),
        ]
        registered[config["id"]] = entities
        async_add_devices(entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass, const.DOMAIN + "_register_entity", async_add_binary_sensor_entities
        )
    )

    # The global any-zone sensor lives on the hub device and exists once.
    async_add_devices([SmartIrrigationGlobalIrrigationNeededSensor(hass)])


class SmartIrrigationZoneBinarySensor(BinarySensorEntity):
    """Base for per-zone binary sensors (zone device + store refresh)."""

    _attr_should_poll = False
    suffix = ""

    def __init__(self, hass: HomeAssistant, entity_id: str, zone: dict) -> None:
        """Initialize from the zone config dict."""
        self._hass = hass
        self.entity_id = entity_id
        self._zone_id = zone[const.ZONE_ID]
        self._zone_name = zone[const.ZONE_NAME]
        self._update_from_zone(zone)

        async_dispatcher_connect(
            hass, const.DOMAIN + "_config_updated", self._async_zone_updated
        )

    def _update_from_zone(self, zone: dict) -> None:
        """Pull this sensor's value(s) from the zone dict (override)."""

    @callback
    def _async_zone_updated(self, zone_id=None):
        """Refresh from the store when this zone changes."""
        if self._zone_id != zone_id or not (self.hass and self.hass.data):
            return
        zone = self.hass.data[const.DOMAIN]["coordinator"].store.get_zone(self._zone_id)
        if zone:
            self._zone_name = zone.get(const.ZONE_NAME, self._zone_name)
            self._update_from_zone(zone)
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

    async def async_added_to_hass(self):
        """Push the initial state."""
        _LOGGER.debug("%s is added to hass", self.entity_id)
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state()


class SmartIrrigationZoneIrrigationNeededSensor(SmartIrrigationZoneBinarySensor):
    """On when the zone would water if a run started now (deficit gate)."""

    suffix = "irrigation_needed"
    _attr_icon = "mdi:water-alert"

    def _update_from_zone(self, zone: dict) -> None:
        self._needed = _zone_needs_irrigation(zone)

    @property
    def name(self) -> str:
        """Return friendly name."""
        return f"{self._zone_name} Irrigation needed"

    @property
    def is_on(self) -> bool:
        """Return True when the deficit gate is met."""
        return self._needed


class SmartIrrigationZoneWateringNowSensor(SmartIrrigationZoneBinarySensor):
    """On while the zone's linked valve/switch is actually running."""

    suffix = "watering_now"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, hass: HomeAssistant, entity_id: str, zone: dict) -> None:
        """Initialize and prepare the linked-entity subscription."""
        self._unsub_linked = None
        super().__init__(hass, entity_id, zone)

    def _update_from_zone(self, zone: dict) -> None:
        linked = zone.get(const.ZONE_LINKED_ENTITY) or None
        if linked != getattr(self, "_linked_entity", None):
            self._linked_entity = linked
            self._resubscribe()

    def _resubscribe(self) -> None:
        """(Re)subscribe to the linked entity's state changes."""
        if self._unsub_linked:
            self._unsub_linked()
            self._unsub_linked = None
        # Only subscribe once we're registered with HA (hass set by HA core).
        if self._linked_entity and self.hass:
            self._unsub_linked = async_track_state_change_event(
                self.hass, [self._linked_entity], self._async_linked_state_changed
            )

    @callback
    def _async_linked_state_changed(self, _event) -> None:
        """The valve/switch changed state — mirror it."""
        self.async_schedule_update_ha_state()

    @property
    def name(self) -> str:
        """Return friendly name."""
        return f"{self._zone_name} Watering now"

    @property
    def is_on(self) -> bool:
        """True while the linked entity reports on/open."""
        if not self._linked_entity or not self.hass:
            return False
        state = self.hass.states.get(self._linked_entity)
        return state is not None and state.state in _WATERING_STATES

    @property
    def extra_state_attributes(self) -> dict:
        """Zone identity plus the mirrored entity."""
        return {
            **super().extra_state_attributes,
            "linked_entity": self._linked_entity,
        }

    async def async_added_to_hass(self):
        """Subscribe to the linked entity once registered."""
        await super().async_added_to_hass()
        self._resubscribe()

    async def async_will_remove_from_hass(self):
        """Drop the linked-entity subscription."""
        if self._unsub_linked:
            self._unsub_linked()
            self._unsub_linked = None
        await super().async_will_remove_from_hass()


class SmartIrrigationGlobalIrrigationNeededSensor(BinarySensorEntity):
    """On when any zone needs irrigation (hub device)."""

    _attr_should_poll = False
    _attr_icon = "mdi:water-alert"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the global sensor."""
        self._hass = hass
        self.entity_id = f"{PLATFORM}.{const.DOMAIN}_irrigation_needed"
        self._needed_zones: list[str] = []
        self._recompute()

        async_dispatcher_connect(
            hass, const.DOMAIN + "_config_updated", self._async_any_zone_updated
        )

    def _recompute(self) -> None:
        """Recompute the needing-zones list from the store."""
        try:
            store = self._hass.data[const.DOMAIN]["coordinator"].store
            zones = [store.get_zone(zone_id) for zone_id in list(store.zones)]
            self._needed_zones = [
                zone.get(const.ZONE_NAME)
                for zone in zones
                if zone and _zone_needs_irrigation(zone)
            ]
        except (KeyError, AttributeError, TypeError):
            self._needed_zones = []

    @callback
    def _async_any_zone_updated(self, _zone_id=None):
        """Any zone changed — recompute."""
        self._recompute()
        if self.hass:
            self.async_schedule_update_ha_state()

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{const.DOMAIN}_irrigation_needed"

    @property
    def name(self) -> str:
        """Return friendly name."""
        return f"{const.NAME} Irrigation needed"

    @property
    def device_info(self) -> dict:
        """Group under the hub device."""
        return hub_device_info(self._hass)

    @property
    def is_on(self) -> bool:
        """True when at least one zone needs irrigation."""
        return bool(self._needed_zones)

    @property
    def extra_state_attributes(self) -> dict:
        """Expose which zones need irrigation."""
        return {"zones": self._needed_zones}

    async def async_added_to_hass(self):
        """Push the initial state."""
        await super().async_added_to_hass()
        self._recompute()
        self.async_schedule_update_ha_state()
