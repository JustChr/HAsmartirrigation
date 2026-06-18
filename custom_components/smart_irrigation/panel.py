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


async def async_register_panel(hass: HomeAssistant):
    """Register the custom panel for the Smart Irrigation integration."""
    root_dir = Path(hass.config.path(CUSTOM_COMPONENTS)) / INTEGRATION_FOLDER
    panel_dir = root_dir / PANEL_FOLDER
    view_url = panel_dir / PANEL_FILENAME
    card_url = panel_dir / CARD_FILENAME
    full_card_url = panel_dir / FULL_CARD_FILENAME
    lang_dir = panel_dir / LANG_FOLDER

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(PANEL_URL, str(view_url), cache_headers=False),
            StaticPathConfig(CARD_URL, str(card_url), cache_headers=False),
            # Heavy card implementation, lazy-imported by the stub on first render.
            StaticPathConfig(FULL_CARD_URL, str(full_card_url), cache_headers=False),
            # Per-language translation JSON (only en is bundled into the
            # frontend; the rest are fetched on demand from here).
            StaticPathConfig(LANG_URL, str(lang_dir), cache_headers=False),
        ]
    )

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
        panel_version = int(view_url.stat().st_mtime)  # cache-bust the panel module on update
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


async def _async_register_card_resource(hass: HomeAssistant, version: int) -> bool:
    """Register the card as a storage-mode Lovelace resource (deduped/updated).

    Lovelace awaits its registered resources before rendering custom cards, so
    this guarantees the card element is defined in time (unlike add_extra_js_url,
    which races the dashboard render). Returns True when handled, False when there
    is no writable resource store (e.g. YAML-mode Lovelace), so the caller can
    fall back to add_extra_js_url.
    """
    lovelace = hass.data.get("lovelace")
    resources = getattr(lovelace, "resources", None)
    # Only the storage-backed collection is writable; YAML mode is read-only.
    if resources is None or type(resources).__name__ != "ResourceStorageCollection":
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
    """Unregister the custom panel for the Smart Irrigation integration."""
    frontend.async_remove_panel(hass, DOMAIN)
    _LOGGER.debug("Removing panel")
