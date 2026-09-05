"""Removing the pre-#120 install for the user: the repair behind #120's cleanup.

The order is the whole design, and it is not cosmetic. Home Assistant can only
run an integration's own `async_remove_entry` while it can still import it, so
the config entry has to go BEFORE the directory. Reversed, the entry becomes
something Home Assistant cannot clean up -- an orphaned entry beside an orphaned
storage file, which is exactly the state that made v2026.09.07's failed setups
unrecoverable.
"""

import json
from types import SimpleNamespace

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.migrate_domain import (
    async_cleanup_is_safe,
    async_delete_legacy_directory,
    async_remove_legacy_entry,
    cleanup_is_safe,
    legacy_directory,
    storage_path,
)
from custom_components.irrigation_plus.repairs import LeftoverInstallRepairFlow

OUR_MANIFEST = {
    "domain": const.LEGACY_DOMAIN,
    "documentation": "https://github.com/JustChr/HAsmartirrigation",
    "codeowners": ["@JustChr"],
}
THEIR_MANIFEST = {
    "domain": const.LEGACY_DOMAIN,
    "documentation": "https://github.com/altmenorg/HAsmartirrigation",
    "codeowners": ["@altmenorg"],
}


def _hass(tmp_path, entries=(), removed=None):
    """A hass double with a real config dir and a recording entry remover."""
    (tmp_path / ".storage").mkdir(parents=True, exist_ok=True)

    async def _executor(func, *args):
        return func(*args)

    async def _async_remove(entry_id):
        if removed is not None:
            removed.append(entry_id)

    return SimpleNamespace(
        config=SimpleNamespace(path=lambda *parts: str(tmp_path.joinpath(*parts))),
        config_entries=SimpleNamespace(
            async_entries=lambda domain: (
                list(entries) if domain == const.LEGACY_DOMAIN else []
            ),
            async_remove=_async_remove,
        ),
        async_add_executor_job=_executor,
    )


def _install(tmp_path, manifest=OUR_MANIFEST):
    directory = tmp_path / "custom_components" / const.LEGACY_DOMAIN
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (directory / "__init__.py").write_text("# code\n", encoding="utf-8")
    return directory


def _our_store(hass, zones):
    storage_path(hass).write_text(
        json.dumps({"version": 14, "data": {"config": {}, "zones": zones}}),
        encoding="utf-8",
    )


class TestCleanupIsSafe:
    """Both gates guard something irreplaceable."""

    def test_ours_with_zones_is_safe(self):
        assert cleanup_is_safe(True, 3) is True

    def test_a_foreign_install_is_never_touched(self):
        """That directory is a different, working integration."""
        assert cleanup_is_safe(False, 3) is False

    def test_no_zones_means_the_migration_did_not_land(self):
        """Removing the old entry deletes the only full copy of their config."""
        assert cleanup_is_safe(True, 0) is False

    def test_an_unknown_zone_count_is_refused(self):
        """None is 'unreadable', not 'empty' -- refuse, as the import does."""
        assert cleanup_is_safe(True, None) is False

    async def test_against_the_live_filesystem(self, tmp_path):
        hass = _hass(tmp_path)
        _install(tmp_path)
        _our_store(hass, {"1": {"name": "Lawn"}})
        assert await async_cleanup_is_safe(hass) is True

    async def test_against_the_live_filesystem_when_empty(self, tmp_path):
        hass = _hass(tmp_path)
        _install(tmp_path)
        _our_store(hass, {})
        assert await async_cleanup_is_safe(hass) is False


class TestRemovingTheEntry:
    async def test_removes_the_legacy_entry(self, tmp_path):
        removed = []
        entry = SimpleNamespace(entry_id="legacy1", data={}, options={})
        hass = _hass(tmp_path, entries=[entry], removed=removed)

        assert await async_remove_legacy_entry(hass) is True
        assert removed == ["legacy1"]

    async def test_no_entry_is_not_an_error(self, tmp_path):
        removed = []
        hass = _hass(tmp_path, removed=removed)

        assert await async_remove_legacy_entry(hass) is False
        assert removed == []


class TestDeletingTheDirectory:
    async def test_deletes_our_own_leftover(self, tmp_path):
        hass = _hass(tmp_path)
        directory = _install(tmp_path)

        assert await async_delete_legacy_directory(hass) is True
        assert not directory.exists()

    async def test_refuses_a_foreign_install(self, tmp_path):
        """The gate is re-checked here, not trusted from the caller."""
        hass = _hass(tmp_path)
        directory = _install(tmp_path, THEIR_MANIFEST)

        assert await async_delete_legacy_directory(hass) is False
        assert (directory / "__init__.py").is_file()

    async def test_a_missing_directory_is_not_an_error(self, tmp_path):
        assert await async_delete_legacy_directory(_hass(tmp_path)) is False

    async def test_a_permission_error_does_not_raise(self, tmp_path):
        hass = _hass(tmp_path)
        _install(tmp_path)

        async def _boom(func, *args):
            raise OSError("permission denied")

        hass.async_add_executor_job = _boom
        assert await async_delete_legacy_directory(hass) is False


class TestTheRepairFlow:
    def _flow(self, hass):
        flow = LeftoverInstallRepairFlow()
        flow.hass = hass
        return flow

    def _ready(self, tmp_path, removed):
        entry = SimpleNamespace(entry_id="legacy1", data={}, options={})
        hass = _hass(tmp_path, entries=[entry], removed=removed)
        _install(tmp_path)
        _our_store(hass, {"1": {"name": "Lawn"}})
        return hass

    async def test_the_confirm_step_names_what_will_be_deleted(self, tmp_path):
        hass = self._ready(tmp_path, [])
        result = await self._flow(hass).async_step_confirm()

        assert result["type"] == "form"
        assert result["step_id"] == "confirm"
        placeholders = result["description_placeholders"]
        assert placeholders["path"] == str(legacy_directory(hass))
        assert placeholders["name"] == const.LEGACY_NAME

    async def test_the_entry_goes_before_the_directory(self, tmp_path):
        """The invariant. Reversed, Home Assistant cannot tear the old one down.

        Recorded as one ordered list so the assertion is about SEQUENCE, not
        merely about both things having happened.
        """
        order = []
        entry = SimpleNamespace(entry_id="legacy1", data={}, options={})
        hass = _hass(tmp_path, entries=[entry])
        directory = _install(tmp_path)
        _our_store(hass, {"1": {"name": "Lawn"}})

        async def _remove(entry_id):
            order.append(f"entry:{entry_id}")

        hass.config_entries.async_remove = _remove

        inner = hass.async_add_executor_job

        async def _watch(func, *args):
            result = await inner(func, *args)
            if not directory.exists() and "directory" not in "".join(order):
                order.append("directory")
            return result

        hass.async_add_executor_job = _watch

        result = await self._flow(hass).async_step_confirm(user_input={})

        assert order == ["entry:legacy1", "directory"]
        assert result["step_id"] == "done"
        assert not directory.exists()

    async def test_a_surviving_directory_is_reported_not_celebrated(
        self, tmp_path, monkeypatch
    ):
        """A flow that closes on a success it did not earn leaves duplicates.

        The cleanup is safe and the entry DOES go; only the delete fails, which
        in the field means a file permission the container cannot get past.
        """
        removed = []
        hass = self._ready(tmp_path, removed)

        def _denied(path):
            raise OSError("permission denied")

        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain.shutil.rmtree", _denied
        )

        result = await self._flow(hass).async_step_confirm(user_input={})

        assert result["step_id"] == "partial"
        assert result["description_placeholders"]["path"] == str(legacy_directory(hass))
        # The entry still went: that half succeeded and must not be re-run.
        assert removed == ["legacy1"]

    async def test_it_refuses_when_the_migration_no_longer_looks_complete(
        self, tmp_path
    ):
        """Re-checked at execution: the issue was raised at setup, long before."""
        removed = []
        entry = SimpleNamespace(entry_id="legacy1", data={}, options={})
        hass = _hass(tmp_path, entries=[entry], removed=removed)
        directory = _install(tmp_path)
        _our_store(hass, {})  # emptied since the issue was raised

        result = await self._flow(hass).async_step_confirm(user_input={})

        assert result["step_id"] == "unsafe"
        assert removed == []
        assert (directory / "__init__.py").is_file()

    @pytest.mark.parametrize("step", ["done", "partial", "unsafe"])
    async def test_every_outcome_step_can_be_closed(self, tmp_path, step):
        hass = self._ready(tmp_path, [])
        flow = self._flow(hass)
        result = await getattr(flow, f"async_step_{step}")(user_input={})
        assert result["type"] == "create_entry"
