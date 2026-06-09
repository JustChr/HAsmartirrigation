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

    # Load the Lovelace card bundle for every user (admin panel is admin-only,
    # but the card lets non-admins add a zones dashboard). add_extra_js_url is
    # idempotent, so this is safe across reloads.
    frontend.add_extra_js_url(hass, CARD_URL)

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_NAME,
        frontend_url_path=DOMAIN,
        module_url=PANEL_URL,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=True,
        config={},
    )


def remove_panel(hass: HomeAssistant):
    """Unregister the custom panel for the Smart Irrigation integration."""
    frontend.async_remove_panel(hass, DOMAIN)
    _LOGGER.debug("Removing panel")
