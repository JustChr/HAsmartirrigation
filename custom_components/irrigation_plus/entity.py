"""Shared device-registry helpers.

Every entity groups under a per-zone device, and the per-zone devices hang off a
single hub device (see ``hub_link``). The device-info helpers return plain dicts
(HA accepts these for ``device_info``) to avoid importing DeviceInfo from the
test-mocked device_registry module; ``hub_link_for`` and ``find_device`` ask the
registry itself what it offers.
"""

import inspect

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
    """The top-level Irrigation Plus device (hosts global entities)."""
    return {
        "identifiers": {(const.DOMAIN, coordinator_id(hass))},
        "name": const.NAME,
        "model": const.NAME,
        "manufacturer": const.MANUFACTURER,
        "sw_version": const.VERSION,
    }


def hub_link_for(registry, hub_device_id: str, cid: str) -> dict:
    """How a zone or distributor device names the hub as its parent.

    Home Assistant 2026.8 added ``via_device_id`` (the parent's registry id)
    to the device info and deprecated ``via_device`` (the parent's
    identifier), which goes in 2027.8. Before 2026.8 ``async_get_or_create``
    takes no ``via_device_id``: its keyword-only signature is fixed, and the
    ``TypeError`` would stop every zone and distributor entity from being
    added. So ask the registry which one it takes rather than branching on a
    version string; the question goes to the registry's class, as in
    ``find_device``. Once the declared floor is 2026.8 or later, return the id
    form outright.
    """
    method = getattr(type(registry), "async_get_or_create", None)
    try:
        takes_id = "via_device_id" in inspect.signature(method).parameters
    except Exception:  # noqa: BLE001 - unreadable means the identifier form
        # Home Assistant has needed Python 3.14 since 2026.3, and since 2026.6
        # its registry module has no "from __future__ import annotations", so
        # reading the signature evaluates the annotations: a name imported only
        # for type checking would raise NameError here and stop the setup.
        takes_id = False
    if takes_id:
        return {"via_device_id": hub_device_id}
    return {"via_device": (const.DOMAIN, cid)}


def hub_link(hass: HomeAssistant) -> dict:
    """The parent link for zone and distributor devices, as setup recorded it.

    ``async_setup_entry`` records it once the hub is registered (see
    ``hub_link_for``). Without a record, as for an entity built outside a
    set-up entry, the identifier form stands; Home Assistant takes it until
    2027.8 (from 2026.9 on with a deprecation warning). Once the declared floor
    is 2026.8 or later, that fallback goes as well: no record, no parent link.
    """
    try:
        link = hass.data[const.DOMAIN].get("hub_link")
    except (KeyError, AttributeError, RuntimeError):
        link = None
    if isinstance(link, dict) and link:
        return dict(link)
    return {"via_device": (const.DOMAIN, coordinator_id(hass))}


def zone_device_info(hass: HomeAssistant, zone_id, zone_name: str) -> dict:
    """A per-zone device, parented to the hub (see ``hub_link``).

    The device is named after the zone alone (e.g. "Front lawn"); with
    ``has_entity_name`` the entities compose as "<zone> <descriptor>". The hub
    device ("Irrigation Plus") supplies the integration-level grouping.
    """
    cid = coordinator_id(hass)
    return {
        "identifiers": {(const.DOMAIN, f"{cid}_zone_{zone_id}")},
        "name": zone_name,
        "model": "Irrigation zone",
        "manufacturer": const.MANUFACTURER,
        **hub_link(hass),
    }


def distributor_device_info(
    hass: HomeAssistant, distributor_id, distributor_name: str
) -> dict:
    """A per-distributor device, parented to the hub (see ``hub_link``)."""
    cid = coordinator_id(hass)
    return {
        "identifiers": {(const.DOMAIN, f"{cid}_distributor_{distributor_id}")},
        "name": distributor_name,
        "model": "Gardena water distributor",
        "manufacturer": const.MANUFACTURER,
        **hub_link(hass),
    }


def find_device(registry, identifier: tuple[str, str], config_entry_id: str | None):
    """The device registered under ``identifier``, or ``None``.

    Home Assistant 2026.9 deprecated ``async_get_device``, which goes in 2027.8,
    because identifiers are no longer unique across config entries; its
    replacement ``async_get_device_by_identifier`` exists from 2026.8 and looks
    up per config entry, and there an entry id of ``None`` finds nothing. Use it
    where the registry's class has it; the question goes to the class because a
    test double answers for any attribute on its instance, so a ``Mock``, even
    one with a ``spec``, takes the old way. Once the declared floor is 2026.8 or
    later, call it outright.
    """
    if callable(getattr(type(registry), "async_get_device_by_identifier", None)):
        return registry.async_get_device_by_identifier(identifier, config_entry_id)
    return registry.async_get_device(identifiers={identifier})
