"""The bridge release: the announcement, and staging the API key (#120).

The key copy is the part that can lose something. The weather credential lives in
the CONFIG ENTRY, not the storage file, and removing this integration through the
UI deletes that entry — so a user who removes it before adding Irrigation Plus
loses a key they may not have written down anywhere. Copying it into the store
here is what makes the order stop mattering.

Which is also why the diagnostics redaction is tested in the same file: putting a
live credential into the store is only safe if the dump that our issue template
REQUIRES on every public bug report cannot print it.
"""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.diagnostics import _SECRET_CONFIG_KEYS
from custom_components.smart_irrigation.rename_notice import (
    _API_KEY_SLOTS,
    async_stash_api_keys,
    plan_api_key_copy,
)


class TestPlanApiKeyCopy:
    def test_copies_a_key_that_lives_only_in_the_entry(self):
        planned = plan_api_key_copy({const.CONF_OWM_API_KEY: "abc"}, {}, {})
        assert planned == {const.CONF_OWM_API_KEY: "abc"}

    def test_options_win_over_data(self):
        # Mirrors resolve_weather_config: a user who ever changed their key in
        # the panel has the new one in options. Copying data over it would
        # migrate them onto a credential they had already replaced.
        planned = plan_api_key_copy(
            {const.CONF_OWM_API_KEY: "old"},
            {const.CONF_OWM_API_KEY: "new"},
            {},
        )
        assert planned == {const.CONF_OWM_API_KEY: "new"}

    def test_never_overwrites_a_key_already_in_the_store(self):
        # This runs on EVERY setup. The store is the thing being protected.
        planned = plan_api_key_copy(
            {const.CONF_OWM_API_KEY: "from-entry"},
            {},
            {const.CONF_OWM_API_KEY: "already-there"},
        )
        assert planned == {}

    def test_an_empty_value_never_clobbers_a_real_one(self):
        planned = plan_api_key_copy(
            {const.CONF_OWM_API_KEY: ""}, {}, {const.CONF_OWM_API_KEY: "real"}
        )
        assert planned == {}

    def test_all_four_slots_are_carried_not_just_one(self):
        # Missing a slot means that service's users hand-migrate their key.
        entry = {slot: f"key-{i}" for i, slot in enumerate(_API_KEY_SLOTS)}
        planned = plan_api_key_copy(entry, {}, {})
        assert set(planned) == set(_API_KEY_SLOTS)

    def test_an_install_with_no_key_writes_nothing(self):
        assert plan_api_key_copy({}, {}, {}) == {}


class TestStashApiKeys:
    @pytest.mark.asyncio
    async def test_writes_the_planned_slots_to_the_store(self):
        store = SimpleNamespace(
            async_get_config=AsyncMock(return_value={}),
            async_update_config=AsyncMock(),
        )
        entry = SimpleNamespace(data={const.CONF_PW_API_KEY: "pw"}, options={})

        written = await async_stash_api_keys(None, entry, store)

        assert written == [const.CONF_PW_API_KEY]
        store.async_update_config.assert_awaited_once_with(
            {const.CONF_PW_API_KEY: "pw"}
        )

    @pytest.mark.asyncio
    async def test_a_store_failure_never_breaks_setup(self):
        # A failure here costs a re-typed API key. An exception costs the whole
        # integration, on the last release before a migration.
        store = SimpleNamespace(
            async_get_config=AsyncMock(side_effect=RuntimeError("store is gone")),
            async_update_config=AsyncMock(),
        )
        entry = SimpleNamespace(data={const.CONF_OWM_API_KEY: "k"}, options={})

        assert await async_stash_api_keys(None, entry, store) == []
        store.async_update_config.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_nothing_to_stage_does_not_touch_the_store(self):
        store = SimpleNamespace(
            async_get_config=AsyncMock(return_value={}),
            async_update_config=AsyncMock(),
        )
        entry = SimpleNamespace(data={}, options={})

        assert await async_stash_api_keys(None, entry, store) == []
        store.async_update_config.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_the_log_line_never_carries_the_key_value(self, caplog):
        store = SimpleNamespace(
            async_get_config=AsyncMock(return_value={}),
            async_update_config=AsyncMock(),
        )
        entry = SimpleNamespace(
            data={const.CONF_OWM_API_KEY: "SUPERSECRET"}, options={}
        )

        await async_stash_api_keys(None, entry, store)

        assert "SUPERSECRET" not in caplog.text


class TestTheRedactionPrerequisite:
    """Staging a credential into the store is only safe if the dump hides it.

    `_SECRET_DATA_KEYS` redacts `hass.data`, which is a DIFFERENT dict from the
    store dump. Extending it would not have covered this.
    """

    @pytest.mark.parametrize("slot", _API_KEY_SLOTS)
    def test_every_staged_slot_is_redacted_from_the_store_dump(self, slot):
        assert slot in _SECRET_CONFIG_KEYS, (
            f"{slot} is copied into the storage file but not redacted from "
            f"diagnostics, and the issue template requires a diagnostics file "
            f"on public bug reports"
        )

    def test_the_home_coordinates_are_still_redacted(self):
        # The pre-existing reason this set exists; extending it must not have
        # displaced anything.
        for key in ("manual_latitude", "manual_longitude", "manual_elevation"):
            assert key in _SECRET_CONFIG_KEYS


class TestTheAnnouncementStrings:
    def test_all_eight_catalogues_carry_the_issue(self):
        import glob
        import os

        for path in sorted(
            glob.glob("custom_components/smart_irrigation/translations/*.json")
        ):
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            issue = data.get("issues", {}).get("renamed_to_irrigation_plus")
            assert issue, f"{os.path.basename(path)} is missing the announcement"
            # The placeholders the code supplies, and no others.
            for field in ("title", "description"):
                assert "{new_name}" in issue[field] or field == "description"
            assert "{new_domain}" in issue["description"]

    def test_the_guide_url_points_at_a_page_that_exists_in_this_tree(self):
        # The Repairs issue's learn-more link. Pages publishes ./docs from
        # master, so the page has to ship in the same release or the link 404s.
        from pathlib import Path

        slug = const.MIGRATION_GUIDE_URL.rstrip("/").rsplit("/", 1)[-1]
        page = Path(__file__).resolve().parents[1] / "docs" / f"{slug}.md"
        assert page.is_file(), f"{const.MIGRATION_GUIDE_URL} has no page at {page}"

    def test_the_guide_names_both_the_old_and_the_new_identity(self):
        from pathlib import Path

        slug = const.MIGRATION_GUIDE_URL.rstrip("/").rsplit("/", 1)[-1]
        text = (Path(__file__).resolve().parents[1] / "docs" / f"{slug}.md").read_text(
            encoding="utf-8"
        )
        assert const.NEW_NAME in text
        assert const.NEW_DOMAIN in text
        assert const.DOMAIN in text
