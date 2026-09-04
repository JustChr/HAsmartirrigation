"""Finding and repointing pre-#120 zones cards in Lovelace dashboards.

Dashboards written before the rename say ``type: custom:smart-irrigation-zones-card``.
The compatibility shim in ``panel.py`` keeps those rendering where the old tag
is unowned, but it is a bridge, not a destination: while the old type is in a
dashboard, that dashboard breaks the day the user also installs the other
project.

Nothing here runs on its own. ``repairs.py`` counts, and rewrites only when the
user confirms — these are their dashboards, and this is another integration's
stored configuration.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from . import const

_LOGGER = logging.getLogger(__name__)

LEGACY_CARD_TYPE = f"custom:{const.LEGACY_PANEL_SLUG}-zones-card"
CARD_TYPE = f"custom:{const.PANEL_SLUG}-zones-card"


def _dashboards(hass: HomeAssistant):
    """Every Lovelace dashboard config object, or an empty list."""
    data = hass.data.get("lovelace")
    dashboards = getattr(data, "dashboards", None)
    if not dashboards:
        return []
    return list(dashboards.items())


def count_legacy_cards(config) -> int:
    """How many cards in one dashboard config use the pre-#120 type.

    Walks the whole structure rather than assuming views/cards: cards nest
    inside stacks, grids and conditionals, and a user's dashboard is under no
    obligation to be shallow.
    """
    found = 0
    stack = [config]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if node.get("type") == LEGACY_CARD_TYPE:
                found += 1
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return found


def rewrite_legacy_cards(config):
    """Return ``(new_config, count)`` with every legacy card type repointed.

    Rebuilds rather than mutating: the config handed back by ``async_load`` may
    be Lovelace's own cached object, and editing it in place would change what
    other consumers see even if the save is later refused.
    """
    if isinstance(config, dict):
        new = {}
        count = 0
        for key, value in config.items():
            if key == "type" and value == LEGACY_CARD_TYPE:
                new[key] = CARD_TYPE
                count += 1
            else:
                child, child_count = rewrite_legacy_cards(value)
                new[key] = child
                count += child_count
        return new, count
    if isinstance(config, list):
        items = [rewrite_legacy_cards(v) for v in config]
        return [i for i, _ in items], sum(c for _, c in items)
    return config, 0


async def _async_load(dashboard):
    """Load a dashboard config, or None when there is nothing stored."""
    try:
        return await dashboard.async_load(False)
    except Exception as err:  # noqa: BLE001 - HA raises ConfigNotFound and friends
        _LOGGER.debug("Skipping a dashboard that could not be loaded: %s", err)
        return None


async def async_count_legacy_cards(hass: HomeAssistant) -> int:
    """Total pre-#120 cards across every dashboard."""
    total = 0
    for _, dashboard in _dashboards(hass):
        config = await _async_load(dashboard)
        if config:
            total += count_legacy_cards(config)
    return total


async def async_rewrite_legacy_cards(hass: HomeAssistant) -> tuple[int, list]:
    """Repoint every legacy card. Returns ``(dashboards changed, skipped)``.

    ``skipped`` names the dashboards that contain legacy cards but could not be
    written — YAML-mode dashboards raise on save, and those have to be edited by
    hand. Reporting them is the point: claiming a clean sweep when some
    dashboards were untouched is worse than doing nothing.
    """
    changed = 0
    skipped: list[str] = []
    for url_path, dashboard in _dashboards(hass):
        config = await _async_load(dashboard)
        if not config:
            continue
        new_config, count = rewrite_legacy_cards(config)
        if not count:
            continue
        try:
            await dashboard.async_save(new_config)
            changed += 1
        except Exception as err:  # noqa: BLE001 - YAML mode raises HomeAssistantError
            skipped.append(url_path or "lovelace")
            _LOGGER.warning(
                "Dashboard %s still uses the old card type but could not be "
                "updated (%s). It has to be edited by hand: replace %s with %s",
                url_path or "lovelace",
                err,
                LEGACY_CARD_TYPE,
                CARD_TYPE,
            )
    return changed, skipped
