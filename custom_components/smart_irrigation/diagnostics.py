"""Diagnostics support for Smart Irrigation."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import const

_LOGGER = logging.getLogger(__name__)

_REDACTED = "[redacted]"

# Every hass.data[DOMAIN] slot that may hold a weather-service API key. The panel
# writes keys to the per-service slots (owm_api_key / pw_api_key / met_api_key);
# only the legacy CONF_WEATHER_SERVICE_API_KEY was redacted before, so live keys
# leaked into diagnostics dumps that users routinely attach to public issues.
_SECRET_DATA_KEYS = (
    const.CONF_WEATHER_SERVICE_API_KEY,
    const.CONF_OWM_API_KEY,
    const.CONF_PW_API_KEY,
    const.CONF_MET_API_KEY,
)

# Store-config fields that must never appear in a shared dump.
#
# The coordinates are here because the maintainer treats a real home location as
# private. The API keys are here because of #120: `rename_notice` copies the four
# weather key slots OUT of the config entry and INTO the storage file, so that
# the move to Irrigation Plus stops depending on whether the user removes this
# integration before or after adding that one. This function dumps that store,
# and the issue template REQUIRES a diagnostics file on a public bug report.
#
# _SECRET_DATA_KEYS above redacts hass.data, which is a DIFFERENT dict. Adding a
# key there does not cover the store; this was checked rather than assumed.
_SECRET_CONFIG_KEYS = (
    "manual_latitude",
    "manual_longitude",
    "manual_elevation",
    const.CONF_WEATHER_SERVICE_API_KEY,
    const.CONF_OWM_API_KEY,
    const.CONF_PW_API_KEY,
    const.CONF_MET_API_KEY,
    # The pre-v2026.05.14 spelling, still migrated by resolve_weather_config and
    # therefore still able to reach a store written by a very old install.
    "owm_api_key",
)


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
    # The config entry carries entry.data / entry.options — the API key AND the
    # manual coordinates — so drop it wholesale rather than trying to redact it
    # field-by-field. Nothing else in the dump needs the raw entry.
    data.pop("entry", None)
    if coordinator is not None:
        store = coordinator.store
        if store is not None:
            # async_get_config returns a fresh attr.asdict copy, so redacting the
            # coordinate fields in place cannot affect live store state.
            config = await store.async_get_config()
            for key in _SECRET_CONFIG_KEYS:
                if config.get(key) is not None:
                    config[key] = _REDACTED
            data["store"] = {
                "config": config,
                "mappings": await store.async_get_mappings(),
                "modules": await store.async_get_modules(),
                "zones": await store.async_get_zones(),
                "distributors": await store.async_get_distributors(),
            }
        else:
            _LOGGER.warning("Store is not available")
    else:
        _LOGGER.warning("Coordinator is not available")
    for key in _SECRET_DATA_KEYS:
        if data.get(key) is not None:
            data[key] = _REDACTED
    return data
