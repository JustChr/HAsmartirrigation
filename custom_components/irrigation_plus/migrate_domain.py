"""Migration from the pre-#120 ``smart_irrigation`` domain.

Both this project and its upstream declared ``domain: smart_irrigation``, so
HACS installed one over the other in place and both produced the same
``sensor.smart_irrigation_*`` entity ids (#120). Renaming to ``irrigation_plus``
fixes that, at the cost of moving the storage key and every entity id.

This module exists to make that cost as close to invisible as we can:

* ``async_import_legacy_store`` copies the old storage file to the new key, so
  zones, buckets, schedules, run logs and flow-learning state all survive.
* ``legacy_config_seed`` hands the config flow the old config entry's weather
  settings **including the API key**, which is the one thing the storage file
  does NOT contain.

The API key point is worth stating plainly, because it is easy to get wrong:
``websockets.save_weather_config`` persists the key to ``entry.options`` and
deliberately writes only the ``use_weather_service`` flag and the service name
to the store. So a migration that copies the storage file and stops has quietly
dropped the user's weather credentials. All four slots move here — the three
per-service ones and the legacy single-key slot.

Ordering matters and is the reverse of what HACS guidance implies. Removing the
old integration through the UI deletes its config entry, and the key with it;
deleting only the directory leaves the entry intact. The migration is therefore
best-effort by design: it takes what is still there and never fails setup over
what is not.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import const

_LOGGER = logging.getLogger(__name__)

# Weather keys that live ONLY in the config entry, never in the storage file.
# Losing any of these means the user has to go and find their API key again.
_WEATHER_SEED_KEYS = (
    const.CONF_USE_WEATHER_SERVICE,
    const.CONF_WEATHER_SERVICE,
    const.CONF_WEATHER_SERVICE_API_KEY,
    const.CONF_WEATHER_SERVICE_API_VERSION,
    const.CONF_OWM_API_KEY,
    const.CONF_PW_API_KEY,
    const.CONF_MET_API_KEY,
    # The pre-v2026.05.14 spellings. resolve_weather_config still migrates
    # these, so carrying them keeps that path working for very old installs.
    "use_owm",
    "owm_api_key",
)


def _storage_file(hass: HomeAssistant, key: str) -> Path:
    """Return the path of a ``.storage`` file for a storage key."""
    return Path(hass.config.path(".storage", key))


def legacy_storage_path(hass: HomeAssistant) -> Path:
    """Path of the storage file written by pre-#120 releases."""
    return _storage_file(hass, f"{const.LEGACY_DOMAIN}.storage")


def storage_path(hass: HomeAssistant) -> Path:
    """Path of this integration's storage file."""
    return _storage_file(hass, f"{const.DOMAIN}.storage")


def find_legacy_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Return the old integration's config entry, if it is still present.

    Present when the user has updated but not yet removed the old integration —
    which is the order the migration guide asks for, precisely because removing
    it first destroys the API key below.
    """
    entries = hass.config_entries.async_entries(const.LEGACY_DOMAIN)
    return entries[0] if entries else None


def legacy_config_seed(hass: HomeAssistant) -> dict:
    """Weather settings to seed a NEW config entry's ``data`` with.

    Returns ``{}`` when there is nothing to import.

    ``entry.options`` wins over ``entry.data``, mirroring the precedence in
    ``config_resolver.resolve_weather_config`` ("options always win", #683) —
    otherwise a user who had ever changed their key in the panel would be
    migrated back onto the original one from the config flow.

    This is deliberately fed to ``async_create_entry(data=...)`` rather than
    merged afterwards with ``async_update_entry``: updating an entry during
    setup triggers a reload that drops the data. (Thanks to altmenorg on #120,
    who hit exactly that.)
    """
    entry = find_legacy_entry(hass)
    if entry is None:
        return {}

    merged = {**dict(entry.data), **dict(entry.options)}
    seed = {k: merged[k] for k in _WEATHER_SEED_KEYS if k in merged}
    if seed:
        # Never log the values — these are live credentials.
        _LOGGER.debug(
            "Seeding new config entry from legacy entry %s with keys: %s",
            entry.entry_id,
            sorted(seed),
        )
    return seed


def legacy_install_present(hass: HomeAssistant) -> bool:
    """Whether there is anything from a pre-#120 install to migrate.

    True when either the old storage file or the old config entry survives; the
    two are independent, because uninstalling the old integration deletes the
    entry but leaves the storage file behind.
    """
    return legacy_storage_path(hass).is_file() or find_legacy_entry(hass) is not None


async def async_import_legacy_store(hass: HomeAssistant) -> bool:
    """Copy the pre-#120 storage file onto this integration's storage key.

    Returns True when a copy was made.

    Copies the RAW bytes rather than load-and-rewrite so the stored ``version``
    field travels untouched and ``MigratableStore`` then migrates it exactly as
    it would have for an in-place upgrade. That keeps this module out of the
    business of knowing anything about the schema.

    Refuses to overwrite an existing file: once this integration has its own
    storage, that is the truth and a stale legacy file must never clobber it.
    Callers must therefore treat this as a one-shot that silently does nothing
    on every later run.
    """
    src = legacy_storage_path(hass)
    dst = storage_path(hass)

    def _copy() -> bool:
        if dst.exists() or not src.is_file():
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return True

    try:
        copied = await hass.async_add_executor_job(_copy)
    except OSError as err:
        # Never fail setup over the migration: a fresh install is a worse
        # outcome than a failed import, but a broken one is worse than both.
        _LOGGER.error(
            "Could not import the previous Smart Irrigation storage from %s: %s. "
            "Starting with an empty configuration; the original file is untouched",
            src,
            err,
        )
        return False

    if copied:
        _LOGGER.info(
            "Imported the previous Smart Irrigation configuration from %s. "
            "The original file is left in place and can be deleted once you are "
            "satisfied with the migration",
            src,
        )
    return copied
