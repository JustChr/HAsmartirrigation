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

import json
import logging
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import const

_LOGGER = logging.getLogger(__name__)

# Identifies a pre-#120 manifest as belonging to THIS fork rather than upstream.
_OUR_MARKER = "justchr"

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


def legacy_install_is_ours(hass: HomeAssistant) -> bool:
    """Whether the surviving ``smart_irrigation`` install is THIS project's.

    Both this project and its upstream shipped ``domain: smart_irrigation``, and
    both install into ``custom_components/smart_irrigation/`` — so only one can
    exist on a machine, but it may be either one. That matters because their
    entities carry ``platform == "smart_irrigation"`` exactly like our old ones
    did: migrating an upstream install would copy a storage file written by
    different code and rename the history of an integration that is still
    running.

    HACS leaves the old directory in place on a domain change (it extracts over
    the computed path and never clears the previous one), so the old manifest is
    normally still there to be read. When it is not, we cannot tell — and answer
    True, because by far the likeliest reason for a legacy install to be present
    at all is that it is the one we are replacing.
    """
    manifest = (
        Path(hass.config.path("custom_components"))
        / const.LEGACY_DOMAIN
        / "manifest.json"
    )
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True
    documentation = str(data.get("documentation", ""))
    codeowners = " ".join(data.get("codeowners") or [])
    return _OUR_MARKER in f"{documentation} {codeowners}".lower()


def legacy_install_present(hass: HomeAssistant) -> bool:
    """Whether there is anything from a pre-#120 install to migrate.

    True when either the old storage file or the old config entry survives; the
    two are independent, because uninstalling the old integration deletes the
    entry but leaves the storage file behind.
    """
    if not legacy_install_is_ours(hass):
        return False
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


# ---------------------------------------------------------------------------
# History and statistics (#120 step 3b)
# ---------------------------------------------------------------------------
#
# Renaming the domain rewrites every entity id, so a user's dashboards, history
# graphs and long-term statistics would all point at ids nothing produces any
# more. The recorder can follow a rename, and neither API needs a live registry
# entry -- both key on the entity_id STRING:
#
#   Recorder.async_update_states_metadata(old, new)        -> history follows
#   statistics.async_update_statistics_metadata(hass, old,
#                                    new_statistic_id=new) -> statistics follow
#
# This MUST run before our entities are added. If a new entity records a state
# first there are two states_meta rows for one entity_id, and the rename hits a
# unique constraint.
#
# It also needs the OLD entity registry entries to still exist, which is why the
# migration guide asks users to add this integration BEFORE removing the old
# one. That single rule buys them both their API key and their history; neither
# is recoverable once the old config entry is gone.

MIGRATION_STORE_KEY = f"{const.DOMAIN}.migration"
_MIGRATION_STORE_VERSION = 1
_HISTORY_MIGRATED = "history_migrated"


def _migration_store(hass: HomeAssistant):
    """A private store for one-shot migration markers.

    Deliberately NOT the integration's own config: the panel POSTs the whole
    config object back, so a stale page could reset a flag kept there and let
    the rename run a second time -- which, against a still-installed old
    integration, would steal the history it had since started recording again.
    """
    from homeassistant.helpers.storage import Store

    return Store(hass, _MIGRATION_STORE_VERSION, MIGRATION_STORE_KEY)


async def async_history_migrated(hass: HomeAssistant) -> bool:
    """Whether the one-shot history/statistics rename has already run."""
    data = await _migration_store(hass).async_load()
    return bool((data or {}).get(_HISTORY_MIGRATED))


async def _async_mark_history_migrated(hass: HomeAssistant, summary: dict) -> None:
    store = _migration_store(hass)
    data = await store.async_load() or {}
    data[_HISTORY_MIGRATED] = True
    data["summary"] = summary
    await store.async_save(data)


def _zone_id_from_unique_id(unique_id: str) -> str | None:
    """Zone id out of a legacy per-zone unique_id, or None for a hub entity.

    Per-zone ids are ``<legacy domain>_<zone id>_<suffix>`` with a numeric zone
    id; hub ids are ``<legacy domain>_<suffix>``. The suffix may itself contain
    underscores, so match on the zone id being numeric rather than on position.
    """
    prefix = f"{const.LEGACY_DOMAIN}_"
    if not unique_id.startswith(prefix):
        return None
    head = unique_id[len(prefix) :].split("_", 1)[0]
    return head if head.isdigit() else None


def build_entity_id_map(hass: HomeAssistant, zones: dict | None = None) -> dict:
    """Map surviving legacy entity ids onto the ids this integration will create.

    Returns ``{old_entity_id: new_entity_id}``.

    The naive substitution -- swap the domain prefix in the object id -- is
    right only while a zone still carries the name it had when its entities were
    created. Entity ids are assigned once, at creation, and are NOT rewritten
    when a zone is renamed, so a renamed zone's OLD ids keep the original slug
    while our fresh entities take the CURRENT one. Where the original slug can
    be recovered (from the duration sensor, the one entity whose object id is
    exactly ``<domain>_<slug>``), both halves are rewritten; otherwise this
    falls back to swapping the prefix, which is right for the common case.
    """
    from homeassistant.helpers import entity_registry as er
    from homeassistant.util import slugify

    registry = er.async_get(hass)
    return plan_entity_id_map(list(registry.entities.values()), zones, slugify)


def plan_entity_id_map(entries, zones: dict | None, slugify) -> dict:
    """The pure half of :func:`build_entity_id_map`.

    Split out so it can be exercised against plain objects. ``conftest``
    replaces ``homeassistant.helpers`` with a MagicMock when it has not already
    been imported, so whether ``patch()`` on a registry reaches the same object
    the code resolves depends on test collection order -- which made the same
    test pass alone and fail in the full suite. Pure in, pure out, no patching.
    """
    legacy = [e for e in entries if e.platform == const.LEGACY_DOMAIN]
    if not legacy:
        return {}

    zones = zones or {}
    old_prefix = f"{const.LEGACY_DOMAIN}_"
    new_prefix = f"{const.DOMAIN}_"

    # zone id -> the slug baked into that zone's entity ids, read off the
    # duration sensor whose object id is exactly "<legacy domain>_<slug>".
    old_slugs: dict[str, str] = {}
    for entry in legacy:
        unique_id = entry.unique_id or ""
        zone_id = _zone_id_from_unique_id(unique_id)
        if zone_id is None or not unique_id.endswith("_duration"):
            continue
        object_id = entry.entity_id.partition(".")[2]
        if object_id.startswith(old_prefix):
            old_slugs[zone_id] = object_id[len(old_prefix) :]

    def _zone_name(zone):
        """Zone name from either a dict or the store's ZoneEntry attrs object.

        The store keeps attrs objects and hands out dicts, and the partial-mixin
        test doubles use plain dicts, so accept both rather than making the
        caller remember which it holds.
        """
        if zone is None:
            return None
        if isinstance(zone, dict):
            return zone.get(const.ZONE_NAME)
        return getattr(zone, const.ZONE_NAME, None)

    def _zone(zone_id):
        if zone_id is None:
            return None
        zone = zones.get(zone_id)
        if zone is None and zone_id.isdigit():
            zone = zones.get(int(zone_id))
        return zone

    mapping: dict[str, str] = {}
    for entry in legacy:
        platform_domain, _, object_id = entry.entity_id.partition(".")
        if not object_id.startswith(old_prefix):
            # A user-renamed entity id. Our new entity takes the standard id and
            # there is no defensible mapping from an arbitrary one, so skip it
            # rather than guess.
            continue

        zone_id = _zone_id_from_unique_id(entry.unique_id or "")
        old_slug = old_slugs.get(zone_id) if zone_id else None
        new_name = _zone_name(_zone(zone_id))

        if old_slug and new_name and object_id.startswith(old_prefix + old_slug):
            tail = object_id[len(old_prefix + old_slug) :]
            new_object_id = f"{new_prefix}{slugify(new_name)}{tail}"
        else:
            new_object_id = new_prefix + object_id[len(old_prefix) :]

        mapping[entry.entity_id] = f"{platform_domain}.{new_object_id}"
    return mapping


async def async_migrate_history(hass: HomeAssistant, zones: dict | None = None) -> dict:
    """Move recorded history and long-term statistics onto the new entity ids.

    Returns a summary. Never raises: losing history is bad, failing setup over
    it is worse.
    """
    summary = {"renamed": 0, "reason": None}

    if await async_history_migrated(hass):
        summary["reason"] = "already_migrated"
        return summary

    if "recorder" not in hass.config.components:
        # Nothing has been recorded yet, so there is nothing to carry over --
        # but do NOT mark it done, because the recorder may simply not be up.
        summary["reason"] = "no_recorder"
        return summary

    mapping = build_entity_id_map(hass, zones)
    if not mapping:
        summary["reason"] = "no_legacy_entities"
        _LOGGER.info(
            "No previous Smart Irrigation entities are registered, so history and "
            "statistics could not be carried over. This is what happens when the "
            "old integration was removed before this one was added"
        )
        return summary

    try:
        from homeassistant.components.recorder import get_instance
        from homeassistant.components.recorder.statistics import (
            async_update_statistics_metadata,
        )

        instance = get_instance(hass)
        for old_id, new_id in mapping.items():
            instance.async_update_states_metadata(old_id, new_id)
            async_update_statistics_metadata(hass, old_id, new_statistic_id=new_id)
            summary["renamed"] += 1
    except (ImportError, KeyError, AttributeError, RuntimeError) as err:
        summary["reason"] = f"recorder_error: {err}"
        _LOGGER.error(
            "Could not move recorded history onto the new entity ids: %s. The "
            "integration works, but graphs and statistics from before the rename "
            "stay under the old ids",
            err,
        )
        return summary

    await _async_mark_history_migrated(hass, summary)
    _LOGGER.info(
        "Moved history and long-term statistics for %s entities onto the new "
        "%s entity ids",
        summary["renamed"],
        const.DOMAIN,
    )
    return summary


async def async_migrate_device_areas(hass: HomeAssistant) -> int:
    """Copy each legacy zone device's area onto its replacement.

    Device identifiers are domain-scoped, so the rename creates NEW devices and
    orphans the old ones. The entity-id migration does not cover this: without
    it a user silently loses every per-device area assignment, and with it the
    zones land back in the rooms they were already in.

    Matches on the trailing ``_zone_<id>`` of the identifier rather than the
    whole string, because the identifier also embeds the config entry's unique
    id, which the rename changes. Runs AFTER the platforms are set up, because
    the new devices do not exist before that.
    """
    from homeassistant.helpers import device_registry as dr

    registry = dr.async_get(hass)
    moves = plan_device_area_moves(list(registry.devices.values()))
    for device_id, area_id in moves.items():
        registry.async_update_device(device_id, area_id=area_id)
    if moves:
        _LOGGER.info("Restored the area assignment for %s zone devices", len(moves))
    return len(moves)


def plan_device_area_moves(devices) -> dict:
    """The pure half of :func:`async_migrate_device_areas`.

    Returns ``{device_id: area_id}`` for the replacement devices that should
    inherit an area. Pure for the same reason as :func:`plan_entity_id_map`.
    """
    marker = "_zone_"

    def _zone_key(device) -> str | None:
        for namespace, ident in device.identifiers:
            if namespace in (const.DOMAIN, const.LEGACY_DOMAIN) and marker in ident:
                return ident.rsplit(marker, 1)[-1]
        return None

    legacy_areas: dict[str, str] = {}
    for device in devices:
        if not any(ns == const.LEGACY_DOMAIN for ns, _ in device.identifiers):
            continue
        key = _zone_key(device)
        if key and device.area_id:
            legacy_areas[key] = device.area_id
    if not legacy_areas:
        return {}

    moves: dict[str, str] = {}
    for device in devices:
        if not any(ns == const.DOMAIN for ns, _ in device.identifiers):
            continue
        if device.area_id:
            continue  # never overwrite a choice the user has already made
        key = _zone_key(device)
        area = legacy_areas.get(key) if key else None
        if area:
            moves[device.id] = area
    return moves
