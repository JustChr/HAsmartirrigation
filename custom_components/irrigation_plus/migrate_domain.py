"""Migration from the pre-#120 ``smart_irrigation`` domain.

Both this project and its upstream declared ``domain: smart_irrigation``, so
HACS installed one over the other in place and both produced the same
``sensor.smart_irrigation_*`` entity ids (#120). Renaming to ``irrigation_plus``
fixes that, at the cost of moving the storage key and every entity id.

This module exists to make that cost as close to invisible as we can:

* ``async_import_legacy_store`` copies the old storage file to the new key, so
  zones, buckets, schedules, run logs and flow-learning state all survive.
* ``async_legacy_config_seed`` hands the config flow the old config entry's
  weather settings **including the API key**, which pre-bridge releases did not
  write to the storage file at all — falling back to the copy the bridge release
  staged there when the entry is already gone.

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

# Every slot a weather credential can occupy. This restates
# `rename_notice._API_KEY_SLOTS` from the bridge release (v2026.09.06), which is
# what wrote these into the storage file read back below -- that module does not
# exist on this domain, and the release it shipped in is tagged and immutable,
# so the list can be pinned here rather than derived. A LEGACY_* case: it
# describes a historical fact, not a live contract.
_API_KEY_SLOTS = (
    const.CONF_WEATHER_SERVICE_API_KEY,
    const.CONF_OWM_API_KEY,
    const.CONF_PW_API_KEY,
    const.CONF_MET_API_KEY,
)

# Weather keys that live in the config entry rather than the storage file.
# Losing any of these means the user has to go and find their API key again.
_WEATHER_SEED_KEYS = (
    const.CONF_USE_WEATHER_SERVICE,
    const.CONF_WEATHER_SERVICE,
    const.CONF_WEATHER_SERVICE_API_VERSION,
    *_API_KEY_SLOTS,
    # The pre-v2026.05.14 spellings. resolve_weather_config still migrates
    # these, so carrying them keeps that path working for very old installs.
    # (`owm_api_key` is already CONF_OWM_API_KEY above; `use_owm` is not.)
    "use_owm",
)

# What the bridge release staged into the storage file, and therefore all this
# module can recover once the config entry is gone. The two flags matter as much
# as the keys: without them the new entry is created with weather switched off,
# and a recovered credential sits unused behind a disabled service.
_STAGED_SEED_KEYS = (
    const.CONF_USE_WEATHER_SERVICE,
    const.CONF_WEATHER_SERVICE,
    *_API_KEY_SLOTS,
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


def legacy_backup_path(hass: HomeAssistant) -> Path:
    """Where the pre-#120 storage file is copied for safekeeping.

    Removing the old integration through the UI does not merely forget it: its
    ``async_remove_entry`` calls ``store.async_delete()``, which DELETES
    ``.storage/smart_irrigation.storage``. So the file this migration reads
    stops existing the moment the user follows the last step of the guide, and
    a migration that turns out to have gone wrong has nothing left to re-read.

    The backup is written at import time, never touched again, and never read
    by this integration -- it exists purely so a user (or we, on an issue) can
    recover the original by hand.
    """
    return _storage_file(hass, f"{const.LEGACY_DOMAIN}.storage.pre-{const.DOMAIN}.bak")


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


def plan_staged_seed(stored: dict | None, seed: dict | None) -> dict:
    """What the staged storage config can add to a config-entry ``seed``.

    Pure, so the precedence can be exercised without a running Home Assistant.

    The config entry always wins: it is the live value the old integration was
    actually running on, while the store holds a copy the bridge release took at
    some earlier setup. So this only ever FILLS what the entry could not supply
    — which in practice means the entry is gone entirely.

    An empty value never counts as supplied, in either direction: a seed that
    carries ``owm_api_key: None`` has told us nothing.
    """
    stored = stored or {}
    seed = seed or {}
    out = {}
    for key in _STAGED_SEED_KEYS:
        if seed.get(key) is not None and seed.get(key) != "":
            continue
        value = stored.get(key)
        if value is None or value == "":
            continue
        out[key] = value
    return out


def _read_staged_config(path: Path) -> dict:
    """The ``config`` dict out of a Home Assistant storage file. Never raises.

    Best-effort by design, like everything else here: an unreadable or
    hand-edited legacy store costs the user a re-typed API key, and must not
    cost them the config flow.
    """
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        _LOGGER.debug("Could not read staged weather settings from %s: %s", path, err)
        return {}
    config = (document or {}).get("data", {}).get("config")
    return config if isinstance(config, dict) else {}


async def async_legacy_config_seed(hass: HomeAssistant) -> dict:
    """The weather seed for a new config entry: config entry first, store second.

    The config entry is the whole story whenever it is still there, which is the
    order the migration guide asks for. The fallback covers the one way it can
    be gone while the data is not: deleting the old integration's DIRECTORY and
    then removing the now-broken entry. Home Assistant cannot run a missing
    integration's ``async_remove_entry``, so ``store.async_delete()`` never
    fires and ``smart_irrigation.storage`` outlives the entry — carrying the
    credentials the bridge release (v2026.09.06) staged into it.

    Nothing here can recover a key from an install that removed the old
    integration through the UI in working order: that deletes the storage file
    along with the entry, and takes every zone with it.
    """
    seed = legacy_config_seed(hass)
    if all(seed.get(key) for key in _STAGED_SEED_KEYS):
        return seed

    stored = await hass.async_add_executor_job(
        _read_staged_config, legacy_storage_path(hass)
    )
    staged = plan_staged_seed(stored, seed)
    if staged:
        # The NAMES only — these are live credentials.
        _LOGGER.info(
            "Recovered %s weather setting(s) staged in the previous storage file: %s",
            len(staged),
            sorted(staged),
        )
        seed.update(staged)
    return seed


def legacy_directory(hass: HomeAssistant) -> Path:
    """Where a pre-#120 install (ours or upstream's) lives on disk."""
    return Path(hass.config.path("custom_components")) / const.LEGACY_DOMAIN


def foreign_legacy_install(hass: HomeAssistant) -> bool:
    """Whether a DIFFERENT project owns the ``smart_irrigation`` domain here.

    True only when the directory is actually present and its manifest says it is
    not ours. This is the one condition under which we must not touch anything
    named ``smart_irrigation`` — the card tag, the static paths, a dashboard.

    Deliberately filesystem-based rather than ``hass.config.components``:
    integration setup order is not guaranteed, so asking whether the other
    integration has loaded yet gives a different answer depending on timing. The
    directory either exists or it does not.
    """
    return legacy_directory(hass).is_dir() and not legacy_install_is_ours(hass)


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
    manifest = legacy_directory(hass) / "manifest.json"
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
    backup = legacy_backup_path(hass)

    def _copy() -> bool:
        if dst.exists() or not src.is_file():
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        # Second copy, kept for the user rather than for us. Taken in the same
        # executor job so it cannot be skipped by a later failure, and never
        # overwritten: the first import is the one made against untouched
        # data, and a re-run must not replace it with something later.
        if not backup.exists():
            try:
                shutil.copyfile(src, backup)
            except OSError as err:  # a lost backup must not lose the migration
                _LOGGER.warning(
                    "Could not write the safety copy of %s to %s: %s",
                    src,
                    backup,
                    err,
                )
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
            "The original file is left in place, and a safety copy was written "
            "to %s -- keep that until you are satisfied with the migration, "
            "because removing the old integration deletes the original",
            src,
            legacy_backup_path(hass),
        )
    return copied


async def async_verify_import(hass: HomeAssistant, store) -> bool:
    """Sanity-check what the import actually produced.

    Returns True when the result looks right.

    A copy that succeeds byte-for-byte and still yields nothing is the failure
    mode worth catching: the file was written by a schema this build cannot
    migrate, or by a different project entirely. The user sees an empty panel
    and no error, concludes the migration "just didn't work", and by then the
    old integration may already be gone. Say it loudly instead, and point at
    the backup that still holds their data.
    """
    if not await hass.async_add_executor_job(legacy_storage_path(hass).is_file):
        return True  # nothing was imported, so there is nothing to verify

    try:
        zone_count = len(list(getattr(store, "zones", None) or []))
    except TypeError:  # a partially initialised or mocked store
        return True

    if zone_count:
        _LOGGER.info("Carried %s zone(s) across the domain rename", zone_count)
        return True

    _LOGGER.error(
        "The previous configuration at %s was imported but produced NO zones. "
        "Do not remove the old integration yet -- removing it deletes that "
        "file. A safety copy is at %s. Please open an issue with both",
        legacy_storage_path(hass),
        legacy_backup_path(hass),
    )
    return False


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
_ENTITY_ID_MAP = "entity_id_map"
_REPORT_ACKNOWLEDGED = "rename_report_acknowledged"

# Where the human-readable old -> new table is written, next to configuration.yaml.
RENAME_REPORT_FILENAME = f"{const.DOMAIN}_renamed_entities.md"


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


def apply_recorder_renames(mapping, rename_states, rename_statistics):
    """Rename each id in turn. Returns ``(renamed count, failed ids)``.

    Per entity, not per batch. One bad row -- a states_meta collision on an id
    something has already recorded, a statistic that no longer exists -- used to
    abort the whole loop, so a single unlucky sensor cost every entity AFTER it
    its history, silently and in registry order.

    Split out and given the two rename calls as arguments so the failure path is
    testable without a recorder. ``conftest`` swaps whole Home Assistant modules
    for mocks depending on import order, so reaching in to make one call raise is
    exactly the kind of patching that passes alone and fails in the suite --
    the same reason ``plan_entity_id_map`` exists.

    Catches ``Exception`` deliberately: what the recorder raises here is not a
    documented set, and the entire point is that an unexpected one costs a
    single id rather than all of them.
    """
    renamed = 0
    failed: list[str] = []
    for old_id, new_id in mapping.items():
        try:
            rename_states(old_id, new_id)
            rename_statistics(old_id, new_id)
        except Exception as err:  # noqa: BLE001 - one id must not sink the rest
            failed.append(old_id)
            _LOGGER.warning(
                "Could not move the recorded history of %s onto %s: %s",
                old_id,
                new_id,
                err,
            )
            continue
        renamed += 1
    return renamed, failed


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
    except (ImportError, KeyError, AttributeError, RuntimeError) as err:
        summary["reason"] = f"recorder_error: {err}"
        _LOGGER.error(
            "Could not move recorded history onto the new entity ids: %s. The "
            "integration works, but graphs and statistics from before the rename "
            "stay under the old ids",
            err,
        )
        return summary

    renamed, failed = apply_recorder_renames(
        mapping,
        lambda old_id, new_id: instance.async_update_states_metadata(old_id, new_id),
        lambda old_id, new_id: async_update_statistics_metadata(
            hass, old_id, new_statistic_id=new_id
        ),
    )
    summary["renamed"] = renamed

    if failed:
        summary["failed"] = failed
        _LOGGER.error(
            "%s of %s entities kept their history under the old id: %s. The "
            "integration works; those graphs start from scratch",
            len(failed),
            len(mapping),
            ", ".join(sorted(failed)),
        )

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


# ---------------------------------------------------------------------------
# The rename report (#120)
# ---------------------------------------------------------------------------
#
# History and statistics follow an entity id. The id WRITTEN IN A USER'S OWN
# YAML does not: an automation trigger, a template sensor, a REST call, a
# dashboard on another Home Assistant instance. Nothing in Home Assistant can
# rewrite those and nothing warns about them -- a template referencing a dead
# entity id just renders `unknown` for ever.
#
# We cannot fix that, but we are the only party that will ever know the exact
# mapping, and only for as long as the OLD registry entries survive. So it is
# captured on the one setup where it is still computable, persisted, and handed
# back as a table the user can work through.


def render_rename_report(mapping: dict) -> str:
    """The old -> new table, as Markdown. Pure, so it is testable as text."""
    lines = [
        f"# {const.NAME}: renamed entities",
        "",
        f"`{const.LEGACY_DOMAIN}` was renamed to `{const.DOMAIN}`, so every "
        "entity id changed.",
        "",
        "History, long-term statistics and your configuration were carried "
        "across automatically. Entity ids written into **your own** "
        "automations, scripts, templates and dashboards were not — nothing in "
        "Home Assistant can rewrite those, and a template pointing at an old "
        "id renders `unknown` without ever raising an error.",
        "",
        "Search your configuration for each id on the left and replace it with "
        "the one on the right.",
        "",
        "| Old entity id | New entity id |",
        "| --- | --- |",
    ]
    lines += [f"| `{old}` | `{new}` |" for old, new in sorted(mapping.items())]
    lines += [
        "",
        f"Service calls are the exception: `{const.LEGACY_DOMAIN}.*` still "
        f"works, forwarding to `{const.DOMAIN}.*`, so automations keep running "
        "while you migrate them. That compatibility layer will be removed in a "
        "future release.",
        "",
    ]
    return "\n".join(lines)


async def async_capture_rename_report(hass: HomeAssistant, zones: dict | None = None):
    """Compute, persist and write out the old -> new entity id table.

    Returns the mapping (possibly empty). Must run on the same setup as the
    history migration and for the same reason: it needs the OLD registry
    entries, which are gone once the user removes the old integration.

    One-shot. A second run would see only our own entities, produce an empty
    map, and overwrite a good report with nothing.
    """
    store = _migration_store(hass)
    data = await store.async_load() or {}
    if _ENTITY_ID_MAP in data:
        return data[_ENTITY_ID_MAP]

    mapping = build_entity_id_map(hass, zones)
    if not mapping:
        return {}

    data[_ENTITY_ID_MAP] = mapping
    await store.async_save(data)

    path = Path(hass.config.path(RENAME_REPORT_FILENAME))
    report = render_rename_report(mapping)

    def _write() -> None:
        path.write_text(report, encoding="utf-8")

    try:
        await hass.async_add_executor_job(_write)
    except OSError as err:
        # The mapping is safe in the store and surfaced in the repair either
        # way, so a read-only config directory costs formatting, not data.
        _LOGGER.warning("Could not write the rename report to %s: %s", path, err)
    else:
        _LOGGER.info(
            "Wrote a table of the %s renamed entity ids to %s", len(mapping), path
        )
    return mapping


async def async_rename_report(hass: HomeAssistant) -> dict:
    """The persisted old -> new mapping, or {} if there is none."""
    data = await _migration_store(hass).async_load()
    return dict((data or {}).get(_ENTITY_ID_MAP) or {})


async def async_rename_report_acknowledged(hass: HomeAssistant) -> bool:
    """Whether the user has said they are done with the rename report."""
    data = await _migration_store(hass).async_load()
    return bool((data or {}).get(_REPORT_ACKNOWLEDGED))


async def async_acknowledge_rename_report(hass: HomeAssistant) -> None:
    """Record that the user has worked through the report.

    Persisted rather than merely deleting the repair, because repairs are
    re-raised on every setup and an issue the user cannot make stay dismissed
    is worse than no issue at all. The report file and the stored mapping are
    left in place -- they cost nothing and the user may want them again.
    """
    store = _migration_store(hass)
    data = await store.async_load() or {}
    data[_REPORT_ACKNOWLEDGED] = True
    await store.async_save(data)
