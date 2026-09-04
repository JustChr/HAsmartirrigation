"""Panel registration for the Smart Irrigation integration."""

import logging
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import (
    CARD_FILENAME,
    CARD_URL,
    CUSTOM_COMPONENTS,
    DOMAIN,
    FULL_CARD_FILENAME,
    FULL_CARD_URL,
    INTEGRATION_FOLDER,
    LANG_FOLDER,
    LANG_URL,
    PANEL_FILENAME,
    PANEL_FOLDER,
    PANEL_ICON,
    PANEL_NAME,
    PANEL_TITLE,
    PANEL_URL,
)

_LOGGER = logging.getLogger(__name__)

# hass.data key guarding the one-shot static-path registration. Top-level on
# purpose so it survives async_remove_entry deleting hass.data[DOMAIN] — see
# async_register_panel.
_STATIC_PATHS_REGISTERED = f"{DOMAIN}_static_paths_registered"


async def async_register_panel(hass: HomeAssistant):
    """Register the custom panel for the Smart Irrigation integration."""
    root_dir = Path(hass.config.path(CUSTOM_COMPONENTS)) / INTEGRATION_FOLDER
    panel_dir = root_dir / PANEL_FOLDER
    view_url = panel_dir / PANEL_FILENAME
    card_url = panel_dir / CARD_FILENAME
    full_card_url = panel_dir / FULL_CARD_FILENAME
    lang_dir = panel_dir / LANG_FOLDER

    # Once per HA PROCESS, not once per setup. HA's
    # _async_register_static_paths appends to the aiohttp router with no dedup,
    # and aiohttp routes cannot be removed again — so every reload (and an
    # options change triggers one, via options_update_listener) permanently
    # added four more routes for the same four URLs. Only the first ever
    # matched; the rest were dead weight that accumulated for the lifetime of
    # the process.
    #
    # The flag deliberately does NOT live in hass.data[DOMAIN], which
    # async_remove_entry deletes: the routes outlive an uninstall, so
    # re-registering after a reinstall in the same process would duplicate them
    # again. The paths are version-independent (cache-busting is done with a
    # ?v= query string, which does not affect routing), so the routes a
    # previous setup registered stay correct after an update.
    if not hass.data.get(_STATIC_PATHS_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(PANEL_URL, str(view_url), cache_headers=False),
                StaticPathConfig(CARD_URL, str(card_url), cache_headers=False),
                # Heavy card implementation, lazy-imported by the stub on first render.
                StaticPathConfig(
                    FULL_CARD_URL, str(full_card_url), cache_headers=False
                ),
                # Per-language translation JSON (only en is bundled into the
                # frontend; the rest are fetched on demand from here).
                StaticPathConfig(LANG_URL, str(lang_dir), cache_headers=False),
            ]
        )
        hass.data[_STATIC_PATHS_REGISTERED] = True

    # Make the Lovelace card bundle available to every user (the admin panel is
    # admin-only, but the card lets non-admins add a zones dashboard).
    #
    # Prefer a real Lovelace resource: a storage-mode dashboard *awaits* its
    # registered resources before rendering custom cards, so the card element is
    # defined in time. add_extra_js_url loads in parallel and Lovelace does NOT
    # wait for it, which races the dashboard render and intermittently yields a
    # "Custom element doesn't exist" / config error on the card. Fall back to
    # add_extra_js_url only for YAML-mode dashboards (no writable resource store).
    try:
        version = int(card_url.stat().st_mtime)  # cache-bust on a HACS update
    except OSError:
        version = 0
    if not await _async_register_card_resource(hass, version):
        frontend.add_extra_js_url(hass, f"{CARD_URL}?v={version}")

    try:
        panel_version = int(
            view_url.stat().st_mtime
        )  # cache-bust the panel module on update
    except OSError:
        panel_version = 0

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_NAME,
        frontend_url_path=DOMAIN,
        module_url=f"{PANEL_URL}?v={panel_version}",
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=True,
        config={},
    )


def _writable_resource_store(hass: HomeAssistant):
    """Return Lovelace's resource collection if we can write to it, else None.

    This used to test ``type(resources).__name__ == "ResourceStorageCollection"``.
    That is a private-API name: if HA ever renames or subclasses that class, the
    check fails CLOSED and we silently fall back to ``add_extra_js_url``, which
    Lovelace does NOT await — which is the race behind the recurring
    "Custom element doesn't exist" / config-error reports on the card. A support
    issue caused by a class rename we would never see in our own logs is the
    worst possible failure mode, so ask about CAPABILITIES instead of identity.

    YAML-mode Lovelace exposes a read-only collection with no mutators, so the
    duck-type check still separates the two modes correctly — and keeps working
    if the storage-backed class is ever renamed.
    """
    resources = getattr(hass.data.get("lovelace"), "resources", None)
    if resources is None:
        return None
    required = ("async_items", "async_create_item", "async_update_item", "loaded")
    if not all(hasattr(resources, attr) for attr in required):
        return None
    return resources


async def _async_register_card_resource(hass: HomeAssistant, version: int) -> bool:
    """Register the card as a storage-mode Lovelace resource (deduped/updated).

    Lovelace awaits its registered resources before rendering custom cards, so
    this guarantees the card element is defined in time (unlike add_extra_js_url,
    which races the dashboard render). Returns True when handled, False when there
    is no writable resource store (e.g. YAML-mode Lovelace), so the caller can
    fall back to add_extra_js_url.
    """
    resources = _writable_resource_store(hass)
    if resources is None:
        return False

    if not resources.loaded:
        await resources.async_load()

    target = f"{CARD_URL}?v={version}"
    for item in resources.async_items():
        if item.get("url", "").split("?")[0] == CARD_URL:
            if item.get("url") != target:  # bump the cache-bust after an update
                await resources.async_update_item(
                    item["id"], {"res_type": "module", "url": target}
                )
            return True

    await resources.async_create_item({"res_type": "module", "url": target})
    return True


def remove_panel(hass: HomeAssistant):
    """Unregister the custom panel for the Smart Irrigation integration.

    Called on RELOAD as well as uninstall, so it must not touch anything that
    setup does not recreate. The Lovelace card resource is deliberately left
    alone here — see ``async_remove_card_resource``.
    """
    frontend.async_remove_panel(hass, DOMAIN)
    _LOGGER.debug("Removing panel")


async def async_remove_card_resource(hass: HomeAssistant) -> bool:
    """Delete the Lovelace resource this integration created. UNINSTALL ONLY.

    ``_async_register_card_resource`` writes a permanent entry into Lovelace's
    storage-mode resource collection, and nothing ever removed it: uninstalling
    Smart Irrigation left a resource pointing at
    ``/smart_irrigation_static/…`` that no longer exists, so every dashboard
    load fetched a 404 forever after.

    Must NOT be called from ``async_unload_entry`` — that runs on every reload
    (including any options change, via ``options_update_listener``), and
    dropping the resource there would deregister the card mid-session and
    re-add it a moment later, racing any open dashboard. Uninstall is the only
    correct trigger, which is why this is separate from ``remove_panel``.

    Only removes an entry whose URL matches CARD_URL, so a resource a user
    added by hand pointing somewhere else is never touched.
    """
    resources = _writable_resource_store(hass)
    if resources is None or not hasattr(resources, "async_delete_item"):
        return False

    if not resources.loaded:
        await resources.async_load()

    removed = False
    # Snapshot first: async_items() is a live view of the collection we mutate.
    for item in list(resources.async_items()):
        if item.get("url", "").split("?")[0] == CARD_URL:
            await resources.async_delete_item(item["id"])
            removed = True
    if removed:
        _LOGGER.debug("Removed the Smart Irrigation Lovelace card resource")
    return removed
