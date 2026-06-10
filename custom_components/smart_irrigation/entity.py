"""Shared device-registry helpers.

Every entity groups under a per-zone device, and the per-zone devices hang off a
single hub device (via_device). Returns plain dicts (HA accepts these for
``device_info``) to avoid importing DeviceInfo from the test-mocked
device_registry module.
"""

from homeassistant.core import HomeAssistant

from . import const


def coordinator_id(hass: HomeAssistant) -> str:
    """Best-effort stable coordinator id used as the device identifier."""
    try:
        coordinator = hass.data[const.DOMAIN].get("coordinator")
        if coordinator and getattr(coordinator, "id", None):
            return coordinator.id
    except (KeyError, AttributeError, RuntimeError):
        pass
    return const.DOMAIN


def hub_device_info(hass: HomeAssistant) -> dict:
    """The top-level Smart Irrigation device (hosts global entities)."""
    return {
        "identifiers": {(const.DOMAIN, coordinator_id(hass))},
        "name": const.NAME,
        "model": const.NAME,
        "manufacturer": const.MANUFACTURER,
        "sw_version": const.VERSION,
    }


def zone_device_info(hass: HomeAssistant, zone_id, zone_name: str) -> dict:
    """A per-zone device, parented to the hub via ``via_device``."""
    cid = coordinator_id(hass)
    return {
        "identifiers": {(const.DOMAIN, f"{cid}_zone_{zone_id}")},
        "name": f"{const.NAME}: {zone_name}",
        "model": "Irrigation zone",
        "manufacturer": const.MANUFACTURER,
        "via_device": (const.DOMAIN, cid),
    }
