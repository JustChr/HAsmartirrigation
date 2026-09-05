"""The bridge release: announce the rename, and make the migration order-proof.

This module only exists on the final `smart_irrigation` release. The project is
becoming **Irrigation Plus** on the `irrigation_plus` domain (#120), because this
fork and its upstream both declared `smart_irrigation` and could not coexist:
same install folder, same entity ids, same Lovelace card type, so whichever
loaded second silently lost.

Two jobs, and they are separate for a reason.

**Announce it.** Release notes reach the people who read release notes. A Repairs
issue reaches everyone else, which on a HACS integration is most of them. It is
informational and not fixable -- there is nothing to do from inside Home
Assistant, and offering a button that only opens a web page is worse than a
sentence that says where to go.

**Make the order stop mattering.** The migration is the part that can lose data,
and the losable thing is the weather API key. It lives in the CONFIG ENTRY, not
in the storage file: `websockets.save_weather_config` persists the key to
`entry.options` and deliberately writes only the `use_weather_service` flag and
the service name to the store. So the new integration, which imports the storage
file, would import everything EXCEPT the credentials -- and removing the old
integration through the UI deletes the entry, and the key with it, before the
new one ever runs.

Copying the four key slots into the store here closes that window. Whichever
order the user does it in, the key travels with the configuration.

That copy is why `diagnostics._SECRET_CONFIG_KEYS` had to grow the same four
constants in the same change: `_SECRET_DATA_KEYS` redacts `hass.data`, which is a
DIFFERENT dict from the store dump, and our issue template requires a
diagnostics file on every public bug report. Putting a live credential in the
store without extending that set would publish it.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from . import const

_LOGGER = logging.getLogger(__name__)

ISSUE_RENAME_ANNOUNCEMENT = "renamed_to_irrigation_plus"

# Every slot a weather credential can occupy. Four, not one: the three
# per-service keys the panel writes, plus the legacy single-key slot that
# `resolve_weather_config` still migrates for very old installs. Missing one
# means that service's users hand-migrate their key.
_API_KEY_SLOTS = (
    const.CONF_WEATHER_SERVICE_API_KEY,
    const.CONF_OWM_API_KEY,
    const.CONF_PW_API_KEY,
    const.CONF_MET_API_KEY,
)


def plan_api_key_copy(entry_data, entry_options, stored) -> dict:
    """Which key slots to write into the store, as ``{key: value}``.

    Pure, so the precedence can be exercised without a running Home Assistant.

    ``entry.options`` beats ``entry.data``, mirroring
    ``config_resolver.resolve_weather_config`` ("options always win"): a user who
    ever changed their key in the panel has the new one in options, and copying
    data over it would migrate them onto a credential they replaced.

    A slot already present in the store is left alone, and an empty value never
    overwrites a real one -- this runs on every setup, and the store is the
    thing being protected, not refreshed.
    """
    merged = {**dict(entry_data or {}), **dict(entry_options or {})}
    out = {}
    for key in _API_KEY_SLOTS:
        value = merged.get(key)
        if not value:
            continue
        if (stored or {}).get(key):
            continue
        out[key] = value
    return out


async def async_stash_api_keys(hass: HomeAssistant, entry, store) -> list:
    """Copy the weather API keys into the storage file. Returns the slots written.

    Never raises: a failure here costs the user a re-typed API key after the
    migration, while an exception costs them the integration.
    """
    try:
        stored = await store.async_get_config()
        planned = plan_api_key_copy(entry.data, entry.options, stored)
        if not planned:
            return []
        await store.async_update_config(planned)
    except Exception as err:  # noqa: BLE001 - must never break setup
        _LOGGER.warning(
            "Could not stage the weather API key for the Irrigation Plus "
            "migration: %s. Your key still works; you may have to re-enter it "
            "after migrating",
            err,
        )
        return []

    # The NAMES only. Never the values -- this line goes to a log users paste
    # into public issues.
    _LOGGER.info(
        "Staged %s weather credential slot(s) so they survive the move to %s",
        len(planned),
        const.NEW_DOMAIN,
    )
    return sorted(planned)


async def async_announce_rename(hass: HomeAssistant) -> None:
    """Raise the informational Repairs issue about the rename.

    Idempotent -- ``async_create_issue`` on an existing id is a no-op update, so
    this is safe on every setup. Not dismissible on our side by design: it stays
    until the user moves, which is when the integration stops running at all.
    """
    from homeassistant.helpers import issue_registry as ir

    ir.async_create_issue(
        hass,
        const.DOMAIN,
        ISSUE_RENAME_ANNOUNCEMENT,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_RENAME_ANNOUNCEMENT,
        translation_placeholders={
            "new_name": const.NEW_NAME,
            "new_domain": const.NEW_DOMAIN,
        },
        learn_more_url=const.MIGRATION_GUIDE_URL,
    )
