"""Repairs raised by the #120 domain rename.

Two things the rename leaves behind that we can detect but must not silently
act on:

* the old ``custom_components/smart_irrigation/`` directory, which HACS does
  NOT remove when the domain changes — it recomputes the install path from the
  manifest and extracts there, leaving the previous directory untouched. Home
  Assistant then loads both, and the user gets duplicate entities.
* dashboards still referencing the pre-#120 card type.

Neither is fixed behind the user's back. The directory belongs to a different
integration's namespace and may be loaded, so we describe it and let them
delete it. The dashboards are theirs, so the rewrite is offered as a repair
they confirm.
"""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from . import const
from .lovelace_cards import async_count_legacy_cards, async_rewrite_legacy_cards
from .migrate_domain import legacy_directory, legacy_install_is_ours

_LOGGER = logging.getLogger(__name__)

ISSUE_LEFTOVER_DIRECTORY = "leftover_legacy_directory"
ISSUE_FOREIGN_INSTALL = "foreign_legacy_install"
ISSUE_LEGACY_CARDS = "legacy_dashboard_cards"


async def async_check_issues(hass: HomeAssistant) -> None:
    """Raise or clear every rename-related repair. Safe to call on each setup."""
    from homeassistant.helpers import issue_registry as ir

    directory = legacy_directory(hass)
    present = await hass.async_add_executor_job(directory.is_dir)

    if not present:
        ir.async_delete_issue(hass, const.DOMAIN, ISSUE_LEFTOVER_DIRECTORY)
        ir.async_delete_issue(hass, const.DOMAIN, ISSUE_FOREIGN_INSTALL)
    elif await hass.async_add_executor_job(legacy_install_is_ours, hass):
        # OUR own previous release, left behind by the HACS update. This one
        # matters: Home Assistant will load it as a second integration and the
        # user ends up with two of every entity.
        ir.async_delete_issue(hass, const.DOMAIN, ISSUE_FOREIGN_INSTALL)
        ir.async_create_issue(
            hass,
            const.DOMAIN,
            ISSUE_LEFTOVER_DIRECTORY,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_LEFTOVER_DIRECTORY,
            translation_placeholders={"path": str(directory)},
            learn_more_url=const.MIGRATION_GUIDE_URL,
        )
    else:
        # A DIFFERENT project owns that directory. Running both side by side is
        # the supported outcome of this rename, so this is information, not a
        # problem — but it explains why the old card type keeps working there.
        ir.async_delete_issue(hass, const.DOMAIN, ISSUE_LEFTOVER_DIRECTORY)
        ir.async_create_issue(
            hass,
            const.DOMAIN,
            ISSUE_FOREIGN_INSTALL,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_FOREIGN_INSTALL,
            translation_placeholders={"path": str(directory)},
            learn_more_url=const.MIGRATION_GUIDE_URL,
        )

    count = await async_count_legacy_cards(hass)
    if count:
        ir.async_create_issue(
            hass,
            const.DOMAIN,
            ISSUE_LEGACY_CARDS,
            is_fixable=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_LEGACY_CARDS,
            translation_placeholders={"count": str(count)},
            learn_more_url=const.MIGRATION_GUIDE_URL,
        )
    else:
        ir.async_delete_issue(hass, const.DOMAIN, ISSUE_LEGACY_CARDS)


class LegacyCardsRepairFlow(RepairsFlow):
    """Offer to repoint dashboards at the renamed card type.

    Deliberately a confirmation rather than something the integration does on
    its own: these are the user's dashboards, and rewriting them is a change to
    another integration's stored configuration.
    """

    async def async_step_init(self, user_input=None) -> FlowResult:
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> FlowResult:
        if user_input is not None:
            changed, skipped = await async_rewrite_legacy_cards(self.hass)
            _LOGGER.info(
                "Repointed the zones card in %s dashboard(s); %s could not be "
                "written",
                changed,
                len(skipped),
            )
            return self.async_create_entry(title="", data={})

        count = await async_count_legacy_cards(self.hass)
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders={"count": str(count)},
        )


async def async_create_fix_flow(hass, issue_id, data):
    """Return the repair flow for a fixable issue."""
    if issue_id == ISSUE_LEGACY_CARDS:
        return LegacyCardsRepairFlow()
    return None
