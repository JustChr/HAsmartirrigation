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
from functools import lru_cache
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from . import const

_LOGGER = logging.getLogger(__name__)

# Identifies a pre-#120 manifest as belonging to THIS project's lineage rather
# than to upstream. Kept as a constant AND combined with whatever this build's
# own manifest says -- see `plan_owner_markers` for why both halves are needed.
_UPSTREAM_MARKER = "justchr"

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


async def async_legacy_config_seed(hass: HomeAssistant) -> dict:
    """The weather seed for a new config entry, out of the old config entry.

    **There is no fallback, and there cannot be one.** The bridge release
    (v2026.09.06) was supposed to leave a copy of the credentials in the
    storage file so the key survived in either order, and this function used to
    read it back. It never wrote anything: ``Store.async_update_config``
    filters incoming changes against ``attr.fields_dict(Config)``, and ``Config``
    has no credential attribute -- so ``attr.evolve`` wrote an unchanged config
    while the module logged the success it had planned rather than the one it
    made (#128, Eifel-Joe, confirmed against a live install's diagnostics).

    The read side is deleted rather than kept as an inert fallback: it fooled
    our own documentation into promising a recovery that has never once
    happened, and a reader who finds it will believe the key is safe when it is
    not. The write side cannot be repaired -- it lives in a tagged release, in a
    tree whose domain now belongs to upstream again (#120).

    So the key survives ONLY while the old config entry does, which makes the
    documented order mandatory rather than merely convenient: removing Smart
    Irrigation through the UI first deletes that entry, and takes the
    credentials with it. ``async_config_flow_credential_warning`` is what tells
    the user when that has happened, at the moment it still means something to
    them.
    """
    return legacy_config_seed(hass)


def read_legacy_weather_profile(path: Path) -> dict:
    """Which weather service the old install used, out of its storage file.

    NOT a credential read -- that is the path #128 deleted, and it could only
    ever return empty. These two fields are different in kind: they are real
    ``Config`` attributes, so the old store genuinely holds them, and neither
    is a secret.

    That split is the whole reason the warning can work at all. The key lived
    in the config entry; the service NAME lives in the store. An install that
    removed Smart Irrigation through the UI first has lost the former and kept
    the latter -- which is precisely the population that needs telling, and the
    only reason we can name their provider while doing it.

    Blocking read; hand it to an executor. Never raises.
    """
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        _LOGGER.debug(
            "Could not read the previous weather profile from %s: %s", path, err
        )
        return {}
    config = (document or {}).get("data", {}).get("config")
    if not isinstance(config, dict):
        return {}
    return {
        key: config[key]
        for key in (const.CONF_USE_WEATHER_SERVICE, const.CONF_WEATHER_SERVICE)
        if key in config
    }


async def async_legacy_weather_profile(hass: HomeAssistant) -> dict:
    """``read_legacy_weather_profile`` off the event loop."""
    return await hass.async_add_executor_job(
        read_legacy_weather_profile, legacy_storage_path(hass)
    )


def plan_credential_warning(
    seed: dict | None, profile: dict | None = None
) -> str | None:
    """Which weather credential the user will have to re-enter, if any. Pure.

    Returns the name of the weather service whose key could not be carried
    across, or None when there is nothing to warn about -- either the seed has
    its key, or the old install was not using a weather service that needs one.

    ``profile`` is the old STORE's view of the same two settings, and is only
    consulted where the seed is silent. The seed comes from the config entry
    and is authoritative when it exists; when it does not, the entry is gone --
    and that is exactly the case where the key is unrecoverable, so falling
    back here is what lets the warning reach the users who need it.

    Answering "nothing to warn about" for an install with weather switched off
    matters: an unnecessary warning about a key they never had is how a user
    learns to skip the ones that count.
    """
    seed = seed or {}
    profile = profile or {}

    def _setting(key):
        return seed[key] if key in seed else profile.get(key)

    if not _setting(const.CONF_USE_WEATHER_SERVICE):
        return None
    service = _setting(const.CONF_WEATHER_SERVICE)
    if not service:
        return None
    # Derived, never restated: a provider that needs no credential cannot have
    # lost one, and a missing key there is the expected state rather than a loss.
    if service in const.CONF_WEATHER_SERVICES_NO_API_KEY:
        return None
    if any(seed.get(slot) for slot in _API_KEY_SLOTS):
        return None
    return str(service)


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
    return manifest_is_ours(data, our_owner_markers())


def plan_owner_markers(codeowners) -> tuple:
    """Who this build counts as "us", lower-cased, from its own codeowners.

    Derived rather than listed. A downstream fork rebrands its manifest as a
    matter of course, and the pre-rename release it published carried the same
    owner -- so its old install answers `legacy_install_is_ours` with the FORK's
    name, matched nothing, and the user was never offered the import at all.
    Nothing said why: an unrecognised install is indistinguishable from no
    install. Listing the forks here instead would mean this project shipping a
    register of its own forks and updating it whenever someone else renames.

    The upstream marker stays in the set rather than being replaced, because the
    two halves can legitimately disagree: a fork that rebranded only after the
    rename has an old manifest that still names upstream, and one that rebranded
    before it has an old manifest that does not.

    For this repository the result is exactly ``("justchr",)`` -- the value the
    constant used to hold on its own. That equality is pinned, because a change
    here that altered who UPSTREAM counts as its own would be a regression
    wearing the clothes of a fix.

    Note the matching stays a substring test, as it was: `documentation` is a
    URL and has to be. A fork whose owner name is a substring of another
    project's is therefore matching loosely -- but it is the fork's own manifest
    that decides, which is the same trust boundary as before.
    """
    owners = {_UPSTREAM_MARKER}
    for owner in codeowners or []:
        cleaned = str(owner).lstrip("@").strip().lower()
        if cleaned:
            owners.add(cleaned)
    return tuple(sorted(owners))


@lru_cache(maxsize=1)
def our_owner_markers() -> tuple:
    """:func:`plan_owner_markers` against this component's own manifest.

    Cached: the file cannot change while Home Assistant is running, and this is
    reached from `panel.py` and `repairs.py` on the event loop as well as from
    the executor, so it should not become a per-call read.

    Falls back to the upstream marker alone if our own manifest is unreadable --
    the same answer as before this was derived at all.
    """
    manifest = Path(__file__).parent / "manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return (_UPSTREAM_MARKER,)
    return plan_owner_markers(data.get("codeowners"))


def manifest_is_ours(data, markers) -> bool:
    """Whether a manifest document names any of ``markers``.

    Pure, so the ownership decision can be exercised for a fork's configuration
    without writing that fork's manifest to disk first.
    """
    documentation = str((data or {}).get("documentation", ""))
    codeowners = " ".join((data or {}).get("codeowners") or [])
    haystack = f"{documentation} {codeowners}".lower()
    return any(marker in haystack for marker in markers)


def legacy_install_present(hass: HomeAssistant) -> bool:
    """Whether there is anything from a pre-#120 install to migrate.

    True when either the old storage file or the old config entry survives; the
    two are independent, because uninstalling the old integration deletes the
    entry but leaves the storage file behind.
    """
    if not legacy_install_is_ours(hass):
        return False
    return legacy_storage_path(hass).is_file() or find_legacy_entry(hass) is not None


async def async_legacy_install_present(hass: HomeAssistant) -> bool:
    """:func:`legacy_install_present`, off the event loop.

    The config flow runs inside the loop, and this reads two files: the legacy
    manifest and the legacy storage path. Home Assistant detects that and logs
    a "blocking call inside the event loop ... please create a bug report"
    warning naming us, which is both true and ours to fix.

    ``find_legacy_entry`` touches no disk, so the whole predicate can go to the
    executor without splitting it.
    """
    return await hass.async_add_executor_job(legacy_install_present, hass)


def stored_zone_count(path: Path) -> int | None:
    """How many zones a storage document holds, or ``None`` if that is unknowable.

    Reads the raw file rather than a loaded store, because this has to answer
    the question BEFORE anything is loaded. ``None`` and ``0`` are deliberately
    different answers: "unreadable" must never be treated as "empty", or a
    corrupt file would license overwriting a good one.
    """
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(document, dict):
        return None
    data = document.get("data")
    if not isinstance(data, dict):
        return None
    zones = data.get("zones")
    if zones is None:
        return 0
    try:
        return len(zones)
    except TypeError:
        return None


@callback
def _async_forget_cached_absence(hass: HomeAssistant) -> None:
    """Tell Home Assistant that our storage file exists after all.

    Home Assistant lists ``.storage`` ONCE, during startup, and thereafter
    answers "that key does not exist" for anything missing from that listing
    without going near the disk. Our storage file is created by the copy below,
    long after startup, so ``Store.async_load`` returns ``None`` for a file
    sitting right there -- the store seeds itself empty and its first save
    overwrites the import. Invalidating the key is what ``Store`` itself does
    before every write, and it costs nothing when the key was already known.

    Imported here rather than at module scope, and tolerant of the name being
    gone: this reaches into a cache Home Assistant does not promise, and a
    migration must never be the reason setup fails.
    """
    try:
        from homeassistant.helpers.storage import STORAGE_MANAGER
    except ImportError:  # a future Home Assistant that moved or dropped it
        _LOGGER.debug("No storage manager to invalidate")
        return
    manager = hass.data.get(STORAGE_MANAGER)
    if manager is None:
        return
    try:
        manager.async_invalidate(storage_path(hass).name)
    except AttributeError as err:
        # The import guard above covers the name being gone; this covers its
        # SHAPE changing, which is the failure that actually bit this project:
        # `DeviceEntry.identifiers` was typed as a pair, was not enforced, and
        # crashed setup on a HomeKit bridge. An undocumented cache deserves the
        # same suspicion as an unenforced annotation.
        _LOGGER.debug("Storage manager has no async_invalidate: %s", err)


def _replaces_an_empty_store(dst: Path, src: Path) -> bool:
    """Whether ``dst`` is a zone-less store that ``src`` can legitimately replace."""
    ours = stored_zone_count(dst)
    theirs = stored_zone_count(src)
    return ours == 0 and bool(theirs)


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

    **One exception, and it exists because of a real failure.** A setup that
    crashes after the store is created leaves an EMPTY storage file behind, and
    Home Assistant cannot delete it when the entry is removed -- our
    ``async_remove_entry`` skips the delete when there is no coordinator, which
    is exactly the state a failed setup leaves. The refusal above then makes
    that empty file permanent, and every later attempt imports nothing while
    the user's real configuration sits untouched next to it. So when OUR store
    holds no zones and the legacy one does, the copy goes ahead. Both counts
    must be known: an unreadable file on either side falls back to refusing.
    """
    src = legacy_storage_path(hass)
    dst = storage_path(hass)
    backup = legacy_backup_path(hass)
    superseded = _storage_file(hass, f"{const.DOMAIN}.storage.empty-before-import.bak")

    def _copy() -> bool:
        if not src.is_file():
            return False
        if dst.exists():
            if not _replaces_an_empty_store(dst, src):
                return False
            # Keep even the discarded file. It holds no zones by definition, but
            # it may hold settings made between the failed setup and now, and a
            # migration that deletes something unrecoverably is worse than one
            # that leaves a file behind.
            if not superseded.exists():
                try:
                    shutil.copyfile(dst, superseded)
                except OSError as err:
                    _LOGGER.warning(
                        "Could not set aside the empty store at %s: %s", dst, err
                    )
            _LOGGER.warning(
                "The existing %s holds no zones while %s does -- re-importing "
                "over it. This is the state a failed setup leaves behind; the "
                "discarded file is at %s",
                dst,
                src,
                superseded,
            )
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
        _async_forget_cached_absence(hass)
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
    moves = plan_device_area_moves(all_registry_devices(registry))
    for device_id, area_id in moves.items():
        registry.async_update_device(device_id, area_id=area_id)
    if moves:
        _LOGGER.info("Restored the area assignment for %s zone devices", len(moves))
    return len(moves)


# The last release on the `smart_irrigation` domain. It announced the rename and
# copied the four weather key slots into the storage file so the migration would
# stop depending on the order the user removed things in. A pre-#120 install that
# never ran it therefore has no staged credentials to fall back on -- which only
# bites when the old config entry is gone as well, but that is precisely the case
# that cannot be recovered afterwards.
BRIDGE_VERSION = "v2026.09.06"


def parse_version(value) -> tuple | None:
    """``vYYYY.MM.NN`` as a comparable tuple, or ``None`` if it is not one.

    Deliberately strict: anything that is not this project's scheme returns
    ``None`` (unknown) rather than a best guess, because the answer is used to
    decide what to tell a user about credentials they may have to re-enter.
    """
    if not isinstance(value, str):
        return None
    text = value.strip().lstrip("vV")
    parts = text.split(".")
    if len(parts) != 3:
        return None
    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        return None


def came_from_bridge(installed_version) -> bool | None:
    """Whether the pre-#120 install had reached the bridge release.

    ``True`` / ``False`` / ``None`` for "cannot tell", and the three are
    genuinely different: an install whose version cannot be read is not the same
    as one known to predate the bridge, and only the latter justifies telling a
    user their API key was never staged.
    """
    installed = parse_version(installed_version)
    if installed is None:
        return None
    return installed >= parse_version(BRIDGE_VERSION)


def legacy_manifest_version(hass: HomeAssistant) -> str | None:
    """The ``version`` recorded in the leftover pre-#120 manifest.

    HACS writes the release tag into the manifest it installs and leaves the
    whole directory behind on a domain change, so this is the most direct record
    of the last version that actually ran -- more reliable than inferring it from
    what the storage file happens to contain.
    """
    manifest = legacy_directory(hass) / "manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    version = data.get("version")
    return version if isinstance(version, str) else None


async def async_bridge_status(hass: HomeAssistant) -> dict:
    """What the previous install was, and whether it had the bridge release.

    ``{"legacy_version": str | None, "came_from_bridge": bool | None}``. Never
    raises: this is reporting, and it is read by diagnostics.
    """

    def _read() -> dict:
        version = legacy_manifest_version(hass)
        return {
            "legacy_version": version,
            "came_from_bridge": came_from_bridge(version),
        }

    try:
        return await hass.async_add_executor_job(_read)
    except OSError as err:  # pragma: no cover - reporting must not fail setup
        _LOGGER.debug("Could not read the previous install's version: %s", err)
        return {"legacy_version": None, "came_from_bridge": None}


async def async_report_bridge_status(hass: HomeAssistant) -> dict:
    """Log what the migration is working from. Returns the status.

    Says the useful thing in each case rather than one generic line: a user who
    skipped the bridge needs to know their weather credentials were never staged
    BEFORE they remove the old integration, because afterwards there is nothing
    left to recover from.
    """
    status = await async_bridge_status(hass)
    version, from_bridge = status["legacy_version"], status["came_from_bridge"]

    if from_bridge is None:
        _LOGGER.info(
            "Could not read the previous installation's version, so it is not "
            "known whether it included the %s preparation release. The migration "
            "carries on regardless",
            BRIDGE_VERSION,
        )
    elif from_bridge:
        _LOGGER.info(
            "The previous installation was %s, which includes the %s preparation "
            "release, so the weather credentials were staged for this migration",
            version,
            BRIDGE_VERSION,
        )
    else:
        _LOGGER.warning(
            "The previous installation was %s, which predates the %s preparation "
            "release, so no weather credentials were staged into the storage "
            "file. They are still carried across from the old integration's "
            "config entry -- so do NOT remove the old integration until this one "
            "is working, or the API key goes with it",
            version,
            BRIDGE_VERSION,
        )
    return status


def cleanup_is_safe(is_ours: bool, our_zone_count: int | None) -> bool:
    """Whether the leftover pre-#120 install may be removed for the user.

    Pure, so the decision can be exercised without a running Home Assistant.

    Two conditions, and both are about not destroying something irreplaceable:

    * **It has to be ours.** A ``smart_irrigation`` directory may belong to the
      upstream project, which is a different, working integration. Removing its
      config entry and its files would be deleting a stranger's install.
    * **Our own store has to hold zones.** Removing the old config entry runs
      the old integration's ``async_remove_entry``, which DELETES
      ``.storage/smart_irrigation.storage``. After a migration that silently
      imported nothing -- which happened in the field on v2026.09.07 -- that
      file is the user's only remaining copy. ``None`` (unknown) is refused for
      the same reason ``stored_zone_count`` distinguishes it from ``0``.
    """
    return bool(is_ours) and bool(our_zone_count)


async def async_cleanup_is_safe(hass: HomeAssistant) -> bool:
    """:func:`cleanup_is_safe` against the live filesystem, off the event loop."""

    def _check() -> bool:
        return cleanup_is_safe(
            legacy_install_is_ours(hass), stored_zone_count(storage_path(hass))
        )

    return await hass.async_add_executor_job(_check)


async def async_remove_legacy_entry(hass: HomeAssistant) -> bool:
    """Remove the pre-#120 config entry. Returns True when one was removed.

    MUST happen before the directory is deleted. Home Assistant can only run an
    integration's own ``async_remove_entry`` while it can still import it, and
    that teardown is what releases the panel, the Lovelace resource and the
    storage file. Delete the directory first and the entry becomes unremovable
    housekeeping instead: an orphaned entry beside an orphaned store, which is
    exactly the state that made v2026.09.07's failed setups unrecoverable.
    """
    entry = find_legacy_entry(hass)
    if entry is None:
        return False
    _LOGGER.info(
        "Removing the pre-rename %s config entry %s. Its storage file goes with "
        "it; the copy taken at import time remains at %s",
        const.LEGACY_DOMAIN,
        entry.entry_id,
        legacy_backup_path(hass),
    )
    await hass.config_entries.async_remove(entry.entry_id)
    return True


async def async_delete_legacy_directory(hass: HomeAssistant) -> bool:
    """Delete ``custom_components/smart_irrigation/``. Returns True when deleted.

    Gated on the directory being OURS, re-checked here rather than trusted from
    the caller: this is a recursive delete of a path outside our own namespace,
    and it is the one action in this module that cannot be undone from anything
    we keep. The path is always built by :func:`legacy_directory` and never
    taken from input.

    The running process keeps the module it has already imported, so nothing
    breaks until the restart this is expected to be followed by.
    """
    directory = legacy_directory(hass)

    def _delete() -> bool:
        if not directory.is_dir():
            return False
        if not legacy_install_is_ours(hass):
            _LOGGER.warning(
                "Refusing to delete %s: its manifest says it belongs to another "
                "project, not to this one",
                directory,
            )
            return False
        shutil.rmtree(directory)
        return True

    try:
        deleted = await hass.async_add_executor_job(_delete)
    except OSError as err:
        _LOGGER.error(
            "Could not delete the leftover %s: %s. Delete it by hand and "
            "restart Home Assistant",
            directory,
            err,
        )
        return False

    if deleted:
        _LOGGER.info("Deleted the leftover pre-rename directory at %s", directory)
    return deleted


def all_registry_devices(registry) -> list:
    """Every device entry, across Home Assistant's two registry APIs.

    Since 2026.9 ``DeviceRegistry.devices`` is a compatibility VIEW whose
    ``__iter__`` yields ``DeviceEntry`` objects, and whose ``.values()`` is
    deprecated and reported to the log (it breaks in 2027.9). Before that,
    ``devices`` was the raw mapping, where iterating yields device *ids*.

    Our declared floor is HA 2025.5, so both shapes are live. Detect rather than
    branch on a version string: ask for the entries and check what came back.
    """
    devices = list(registry.devices)
    if devices and isinstance(devices[0], str):
        return list(registry.devices.values())
    return devices


def identifier_pairs(device):
    """``(namespace, identifier)`` for each usable identifier on a device.

    Home Assistant TYPES ``DeviceEntry.identifiers`` as ``set[tuple[str, str]]``
    and does not enforce it. The HomeKit integration writes three-element
    identifiers -- ``("homekit", "<id>", "homekit.bridge")`` -- and this module
    walks the WHOLE device registry, not just ours. Unpacking every identifier
    as a pair therefore raised ``ValueError: too many values to unpack`` on any
    system with a HomeKit bridge, which aborted the migration and left the
    integration in ``setup_error`` with no panel (#120 follow-up).

    Anything that is not a sized sequence of at least two strings is skipped: it
    cannot be one of ours, and a foreign device's shape is not ours to police.
    """
    for identifier in device.identifiers or ():
        if isinstance(identifier, str) or not isinstance(identifier, (tuple, list)):
            continue
        if len(identifier) < 2:
            continue
        namespace, ident = identifier[0], identifier[1]
        if isinstance(namespace, str) and isinstance(ident, str):
            yield namespace, ident


def plan_device_area_moves(devices) -> dict:
    """The pure half of :func:`async_migrate_device_areas`.

    Returns ``{device_id: area_id}`` for the replacement devices that should
    inherit an area. Pure for the same reason as :func:`plan_entity_id_map`.
    """
    marker = "_zone_"

    def _zone_key(device) -> str | None:
        for namespace, ident in identifier_pairs(device):
            if namespace in (const.DOMAIN, const.LEGACY_DOMAIN) and marker in ident:
                return ident.rsplit(marker, 1)[-1]
        return None

    legacy_areas: dict[str, str] = {}
    for device in devices:
        if not any(ns == const.LEGACY_DOMAIN for ns, _ in identifier_pairs(device)):
            continue
        key = _zone_key(device)
        if key and device.area_id:
            legacy_areas[key] = device.area_id
    if not legacy_areas:
        return {}

    moves: dict[str, str] = {}
    for device in devices:
        if not any(ns == const.DOMAIN for ns, _ in identifier_pairs(device)):
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
