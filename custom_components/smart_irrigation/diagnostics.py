"""Diagnostics support for Smart Irrigation."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import const

_LOGGER = logging.getLogger(__name__)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    # Work on a shallow copy: the subsequent pop()/redaction must not mutate the
    # live integration state. Popping "coordinator" off the real hass.data dict
    # removed the running coordinator and was never written back, killing the
    # integration until the next restart.
    data = dict(hass.data[const.DOMAIN])
    coordinator = data.pop("coordinator", None)
    data.pop("zones", None)
    if coordinator is not None:
        store = coordinator.store
        if store is not None:
            data["store"] = {
                "config": await store.async_get_config(),
                "mappings": await store.async_get_mappings(),
                "modules": await store.async_get_modules(),
                "zones": await store.async_get_zones(),
            }
        else:
            _LOGGER.warning("Store is not available")
    else:
        _LOGGER.warning("Coordinator is not available")
    if const.CONF_WEATHER_SERVICE_API_KEY in data:
        data[const.CONF_WEATHER_SERVICE_API_KEY] = "[redacted]"
    return data
