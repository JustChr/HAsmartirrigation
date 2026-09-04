"""Shared base + pure helpers for per-distributor entities.

Distributor entities mirror the zone entities: they group under a per-distributor
device (``entity.distributor_device_info``), read the store directly, and refresh
on the ``DOMAIN + "_distributor_updated"`` dispatcher signal. The variable number
of per-outlet sensors is reconciled with ``outlet_reconcile_diff``.
"""

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import const
from .entity import distributor_device_info


def _store(hass: HomeAssistant):
    """The store, or None when the integration is not (yet) set up."""
    try:
        return hass.data[const.DOMAIN]["coordinator"].store
    except (KeyError, AttributeError):
        return None


def _member_zones(hass: HomeAssistant, distributor_id) -> list:
    """Member zone dicts of a distributor (snapshot from the store)."""
    store = _store(hass)
    if store is None:
        return []
    zones = store.get_zones()
    return [z for z in zones if z.get(const.ZONE_DISTRIBUTOR_ID) == distributor_id]


def used_outlets(hass: HomeAssistant, distributor_id) -> set:
    """Outlet numbers that currently have a member zone assigned."""
    return {
        int(z[const.ZONE_OUTLET_NUMBER])
        for z in _member_zones(hass, distributor_id)
        if z.get(const.ZONE_OUTLET_NUMBER) is not None
    }


def outlet_reconcile_diff(used: set, existing: set):
    """(outlets_to_add, outlets_to_remove) to make ``existing`` match ``used``."""
    return (used - existing, existing - used)


def zone_on_outlet(hass: HomeAssistant, distributor_id, outlet_number):
    """The member zone dict on a given outlet, or None."""
    # Plan I review (2026-07-05): coerce to int to match used_outlets, which
    # already does int(z[ZONE_OUTLET_NUMBER]). A legacy / hand-edited .storage
    # can persist outlet_number as a string ("2"), and a raw == comparison
    # ("2" == 2) never matches — the outlet-zone sensor would then read None
    # permanently. siehe test_distributor_entities.py::
    # test_zone_on_outlet_coerces_str_outlet_number.
    target = int(outlet_number)
    for z in _member_zones(hass, distributor_id):
        n = z.get(const.ZONE_OUTLET_NUMBER)
        if n is not None and int(n) == target:
            return z
    return None


class DistributorEntityBase:
    """Base for per-distributor entities (distributor device + store refresh)."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    suffix = ""

    def __init__(self, hass: HomeAssistant, entity_id: str, distributor: dict) -> None:
        """Initialize from a distributor dict."""
        self._hass = hass
        self.entity_id = entity_id
        self._distributor_id = distributor["id"]
        self._distributor_name = (
            distributor.get("name") or f"Distributor {self._distributor_id}"
        )
        self._distributor = distributor
        self._refresh(distributor)
        async_dispatcher_connect(
            hass, const.DOMAIN + "_distributor_updated", self._async_distributor_updated
        )

    def _refresh(self, distributor: dict) -> None:
        """Pull this entity's value(s) from the distributor dict (override)."""

    @callback
    def _async_distributor_updated(self, distributor_id=None):
        """Refresh from the store when this distributor changes."""
        if self._distributor_id != distributor_id or not (self.hass and self.hass.data):
            return
        store = _store(self.hass)
        dist = store.get_distributor(self._distributor_id) if store else None
        if dist:
            self._distributor_name = dist.get("name", self._distributor_name)
            self._distributor = dist
            self._refresh(dist)
            self.async_schedule_update_ha_state()

    @property
    def unique_id(self) -> str:
        return f"{const.DOMAIN}_distributor_{self._distributor_id}_{self.suffix}"

    @property
    def device_info(self) -> dict:
        return distributor_device_info(
            self._hass, self._distributor_id, self._distributor_name
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state()
