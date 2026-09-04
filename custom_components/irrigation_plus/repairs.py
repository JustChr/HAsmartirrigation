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
from .lovelace_cards import (
    CARD_TYPE,
    LEGACY_CARD_TYPE,
    async_count_legacy_cards,
    async_rewrite_legacy_cards,
)
from .migrate_domain import (
    RENAME_REPORT_FILENAME,
    async_acknowledge_rename_report,
    async_rename_report,
    async_rename_report_acknowledged,
    legacy_directory,
    legacy_install_is_ours,
)

_LOGGER = logging.getLogger(__name__)

ISSUE_LEFTOVER_DIRECTORY = "leftover_legacy_directory"
ISSUE_FOREIGN_INSTALL = "foreign_legacy_install"
ISSUE_LEGACY_CARDS = "legacy_dashboard_cards"
ISSUE_RENAMED_ENTITY_IDS = "renamed_entity_ids"


def should_raise_rename_issue(renamed, acknowledged) -> bool:
    """Whether the renamed-entity-ids repair belongs on screen.

    Pure, for the reason ``plan_entity_id_map`` and ``plan_service_aliases`` are:
    ``async_check_issues`` reaches into the issue registry through the
    ``homeassistant.helpers`` package that ``conftest`` may have replaced with a
    mock, so the decision cannot be asserted where it is used.

    The acknowledgement half is the half that matters. Repairs are re-raised on
    every setup, so without it a user who has worked through their entity ids
    gets the same notice back after each restart, and a repair that will not
    stay dismissed is worse than no repair at all.
    """
    return bool(renamed) and not acknowledged


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

    # Entity ids the user has written into their OWN automations, templates and
    # dashboards. We cannot rewrite those and Home Assistant will not warn about
    # them -- a template pointing at a dead id renders `unknown` for ever. The
    # exact mapping is knowable only here, so hand it over.
    renamed = await async_rename_report(hass)
    if should_raise_rename_issue(renamed, await async_rename_report_acknowledged(hass)):
        ir.async_create_issue(
            hass,
            const.DOMAIN,
            ISSUE_RENAMED_ENTITY_IDS,
            is_fixable=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_RENAMED_ENTITY_IDS,
            translation_placeholders={
                "count": str(len(renamed)),
                "path": str(hass.config.path(RENAME_REPORT_FILENAME)),
            },
            learn_more_url=const.MIGRATION_GUIDE_URL,
        )
    else:
        ir.async_delete_issue(hass, const.DOMAIN, ISSUE_RENAMED_ENTITY_IDS)

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

    A YAML-mode dashboard cannot be written at all -- ``async_save`` raises for
    those -- so a run can succeed for some dashboards and not others. The flow
    therefore has a second step: when anything was skipped it NAMES the
    dashboards and shows the exact replacement, instead of closing as though it
    had swept the lot. Telling the user to go and read the log is not reporting.
    """

    def __init__(self) -> None:
        self._skipped: list[str] = []
        self._changed = 0

    async def async_step_init(self, user_input=None) -> FlowResult:
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> FlowResult:
        if user_input is not None:
            self._changed, self._skipped = await async_rewrite_legacy_cards(self.hass)
            _LOGGER.info(
                "Repointed the zones card in %s dashboard(s); %s could not be "
                "written: %s",
                self._changed,
                len(self._skipped),
                ", ".join(self._skipped) or "none",
            )
            if self._skipped:
                return await self.async_step_manual()
            return self.async_create_entry(title="", data={})

        count = await async_count_legacy_cards(self.hass)
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders={"count": str(count)},
        )

    async def async_step_manual(self, user_input=None) -> FlowResult:
        """Name the dashboards that have to be edited by hand.

        This issue is re-raised on the next setup for as long as those cards
        exist, which is correct but would otherwise look like the repair simply
        did not work. Saying so here is what makes that recurrence legible.
        """
        if user_input is not None:
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({}),
            description_placeholders={
                "changed": str(self._changed),
                "dashboards": _render_dashboards(self._skipped),
                "old_type": LEGACY_CARD_TYPE,
                "new_type": CARD_TYPE,
            },
        )


def _render_dashboards(skipped, limit: int = 10) -> str:
    """The skipped dashboard list for the dialog. Pure, so it is testable.

    Capped for the same reason the entity examples are: a dialog is not a place
    for an unbounded list, and the log already holds every one of them.
    """
    names = list(skipped)
    lines = [f"- {name}" for name in names[:limit]]
    if len(names) > limit:
        lines.append(f"- ... and {len(names) - limit} more (see the log)")
    return "\n".join(lines)


class RenamedEntityIdsRepairFlow(RepairsFlow):
    """Show the old -> new entity id table and let the user dismiss it.

    Confirming records an acknowledgement in the migration store rather than
    only deleting the issue: repairs are re-raised on every setup, so an issue
    that cannot be made to stay dismissed is worse than no issue at all. The
    report file and the stored mapping survive -- they cost nothing, and a user
    part-way through repointing their automations will want them again.
    """

    async def async_step_init(self, user_input=None) -> FlowResult:
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> FlowResult:
        renamed = await async_rename_report(self.hass)
        if user_input is not None:
            await async_acknowledge_rename_report(self.hass)
            _LOGGER.info(
                "The rename report for %s entity ids was acknowledged; the "
                "table stays at %s",
                len(renamed),
                self.hass.config.path(RENAME_REPORT_FILENAME),
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders={
                "count": str(len(renamed)),
                "path": str(self.hass.config.path(RENAME_REPORT_FILENAME)),
                "examples": _render_examples(renamed),
            },
        )


def _render_examples(mapping: dict, limit: int = 5) -> str:
    """A few old -> new lines for the dialog. The file holds the full table.

    A repair dialog is not a place to print eighty rows: a seven-zone install
    renames ~60 entities, and a wall of them buries the one instruction that
    matters. Pure, so the truncation is testable.
    """
    if not mapping:
        return ""
    items = sorted(mapping.items())
    lines = [f"{old} -> {new}" for old, new in items[:limit]]
    if len(items) > limit:
        lines.append(f"... and {len(items) - limit} more")
    return "\n".join(lines)


async def async_create_fix_flow(hass, issue_id, data):
    """Return the repair flow for a fixable issue."""
    if issue_id == ISSUE_LEGACY_CARDS:
        return LegacyCardsRepairFlow()
    if issue_id == ISSUE_RENAMED_ENTITY_IDS:
        return RenamedEntityIdsRepairFlow()
    return None
