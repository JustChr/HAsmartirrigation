"""Diagnostics support for Irrigation Plus."""

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
# private. The API keys are here because of #120: the bridge release copies the
# four weather key slots OUT of the config entry and INTO the storage file, so
# that the migration stops depending on whether the user removes the old
# integration before or after adding this one. That store is what this function
# dumps, and our issue template REQUIRES a diagnostics file on a public issue.
#
# _SECRET_DATA_KEYS below redacts hass.data, which is a different dict. Adding a
# key there does not cover the store, and this was verified rather than assumed.
_SECRET_CONFIG_KEYS = (
    "manual_latitude",
    "manual_longitude",
    "manual_elevation",
    const.CONF_WEATHER_SERVICE_API_KEY,
    const.CONF_OWM_API_KEY,
    const.CONF_PW_API_KEY,
    const.CONF_MET_API_KEY,
    # The pre-v2026.05.14 spelling, still migrated by resolve_weather_config and
    # therefore still capable of reaching a store written by an old install.
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

    # The #120 old -> new entity id table, when there is one. Entity ids are not
    # secret, and having the exact mapping in the dump is what lets a rename
    # question be answered from the issue rather than from a guess.
    #
    # Guarded, because this is the only part of the dump that reads a store the
    # caller did not hand us. Diagnostics is the support path: a dump that
    # raises leaves a user unable to file the issue at all, which is a worse
    # outcome than a dump missing one optional table.
    try:
        from .migrate_domain import async_rename_report

        renamed = await async_rename_report(hass)
    except Exception as err:  # noqa: BLE001 - diagnostics must always produce a dump
        _LOGGER.debug("Could not read the rename report for diagnostics: %s", err)
    else:
        if renamed:
            data["renamed_entity_ids"] = renamed

    return data
