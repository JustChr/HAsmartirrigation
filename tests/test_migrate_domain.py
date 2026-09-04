"""Tests for the #120 domain migration (smart_irrigation -> irrigation_plus).

The point of these is the seam that is easy to get wrong: the weather API key
lives in the CONFIG ENTRY, not in the storage file, so a migration that copies
the store and stops silently loses the user's credentials.
"""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.migrate_domain import (
    async_import_legacy_store,
    find_legacy_entry,
    legacy_config_seed,
    legacy_install_present,
    legacy_storage_path,
    storage_path,
)


def _hass(tmp_path, legacy_entries=()):
    """A hass double with a real .storage directory and a config-entry stub."""
    storage = tmp_path / ".storage"
    storage.mkdir(parents=True, exist_ok=True)

    async def _executor(func, *args):
        return func(*args)

    return SimpleNamespace(
        config=SimpleNamespace(path=lambda *parts: str(tmp_path.joinpath(*parts))),
        config_entries=SimpleNamespace(
            async_entries=lambda domain: (
                list(legacy_entries) if domain == const.LEGACY_DOMAIN else []
            )
        ),
        async_add_executor_job=_executor,
    )


def _entry(data=None, options=None):
    return SimpleNamespace(
        entry_id="legacy1", data=dict(data or {}), options=dict(options or {})
    )


class TestStorageImport:
    """The storage file copy."""

    async def test_imports_the_legacy_store_verbatim(self, tmp_path):
        hass = _hass(tmp_path)
        payload = {"version": 9, "data": {"zones": {"1": {"name": "Lawn"}}}}
        legacy_storage_path(hass).write_text(json.dumps(payload), encoding="utf-8")

        assert await async_import_legacy_store(hass) is True

        # Byte-for-byte, so the stored `version` survives and MigratableStore
        # migrates it exactly as it would on an in-place upgrade.
        assert json.loads(storage_path(hass).read_text(encoding="utf-8")) == payload
        # The original is left alone: the user can still go back.
        assert legacy_storage_path(hass).is_file()

    async def test_never_overwrites_our_own_storage(self, tmp_path):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text('{"version": 9, "data": {}}', "utf-8")
        storage_path(hass).write_text('{"version": 14, "data": {"mine": 1}}', "utf-8")

        assert await async_import_legacy_store(hass) is False
        assert "mine" in storage_path(hass).read_text(encoding="utf-8")

    async def test_no_legacy_file_is_not_an_error(self, tmp_path):
        hass = _hass(tmp_path)
        assert await async_import_legacy_store(hass) is False
        assert not storage_path(hass).exists()

    async def test_an_unreadable_legacy_file_does_not_fail_setup(self, tmp_path):
        """A failed import must never take the integration down with it."""
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text('{"version": 9}', encoding="utf-8")

        def _boom(func, *args):
            raise OSError("permission denied")

        hass.async_add_executor_job = _boom
        assert await async_import_legacy_store(hass) is False


class TestConfigSeed:
    """Carrying the weather settings, which the storage file does NOT hold."""

    def test_carries_every_api_key_slot(self, tmp_path):
        entry = _entry(
            data={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_OWM_API_KEY: "owm-secret",
                const.CONF_PW_API_KEY: "pw-secret",
                const.CONF_MET_API_KEY: "met-secret",
                const.CONF_WEATHER_SERVICE_API_KEY: "legacy-secret",
            }
        )
        seed = legacy_config_seed(_hass(tmp_path, [entry]))

        # All four, not just the one the active service happens to use: the user
        # may switch services later and would otherwise silently lose the key.
        assert seed[const.CONF_OWM_API_KEY] == "owm-secret"
        assert seed[const.CONF_PW_API_KEY] == "pw-secret"
        assert seed[const.CONF_MET_API_KEY] == "met-secret"
        assert seed[const.CONF_WEATHER_SERVICE_API_KEY] == "legacy-secret"

    def test_options_win_over_data(self, tmp_path):
        """Mirrors resolve_weather_config: "options always win" (#683).

        A user who ever changed their key in the panel has the current one in
        options and a stale one in data; picking data would migrate them back
        onto a key they replaced.
        """
        entry = _entry(
            data={const.CONF_OWM_API_KEY: "stale-from-config-flow"},
            options={const.CONF_OWM_API_KEY: "current-from-panel"},
        )
        seed = legacy_config_seed(_hass(tmp_path, [entry]))
        assert seed[const.CONF_OWM_API_KEY] == "current-from-panel"

    def test_carries_the_pre_2026_05_14_spellings(self, tmp_path):
        entry = _entry(data={"use_owm": True, "owm_api_key": "ancient"})
        seed = legacy_config_seed(_hass(tmp_path, [entry]))
        assert seed["use_owm"] is True
        assert seed["owm_api_key"] == "ancient"

    def test_no_legacy_entry_yields_nothing(self, tmp_path):
        assert legacy_config_seed(_hass(tmp_path)) == {}

    def test_unrelated_keys_are_not_dragged_along(self, tmp_path):
        entry = _entry(data={"something_else": "x", const.CONF_OWM_API_KEY: "k"})
        seed = legacy_config_seed(_hass(tmp_path, [entry]))
        assert "something_else" not in seed


class TestDetection:
    """Either half of a legacy install is enough to offer the migration."""

    def test_storage_file_alone_counts(self, tmp_path):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text("{}", encoding="utf-8")
        assert legacy_install_present(hass) is True
        assert find_legacy_entry(hass) is None

    def test_config_entry_alone_counts(self, tmp_path):
        # Uninstalling the old integration deletes the entry but leaves the
        # storage file; deleting the folder does the opposite. Either way there
        # is something worth importing.
        hass = _hass(tmp_path, [_entry()])
        assert legacy_install_present(hass) is True

    def test_a_clean_machine_is_not_offered_a_migration(self, tmp_path):
        assert legacy_install_present(_hass(tmp_path)) is False


class TestWeatherKeyGuard:
    """A keyed service with no key must not build a client (setup would crash)."""

    def _coord(self, service, data):
        from custom_components.irrigation_plus import SmartIrrigationCoordinator

        hass = Mock()
        hass.data = {const.DOMAIN: data}
        coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
        coord.weather_service = service
        return coord, hass

    @pytest.mark.parametrize(
        ("service", "slot"),
        [
            (const.CONF_WEATHER_SERVICE_OWM, const.CONF_OWM_API_KEY),
            (const.CONF_WEATHER_SERVICE_PW, const.CONF_PW_API_KEY),
            (const.CONF_WEATHER_SERVICE_MET, const.CONF_MET_API_KEY),
        ],
    )
    def test_per_service_key_satisfies_the_guard(self, service, slot):
        coord, hass = self._coord(service, {slot: "key"})
        assert coord._weather_service_key_available(hass) is True

    @pytest.mark.parametrize(
        "service",
        [
            const.CONF_WEATHER_SERVICE_OWM,
            const.CONF_WEATHER_SERVICE_PW,
            const.CONF_WEATHER_SERVICE_MET,
        ],
    )
    def test_missing_key_is_refused(self, service):
        coord, hass = self._coord(service, {})
        assert coord._weather_service_key_available(hass) is False

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_blank_keys_count_as_missing(self, value):
        # `api_key.strip()` in every client turns None into AttributeError and
        # "" into a guaranteed auth failure. Neither should reach a client.
        coord, hass = self._coord(
            const.CONF_WEATHER_SERVICE_OWM, {const.CONF_OWM_API_KEY: value}
        )
        assert coord._weather_service_key_available(hass) is False

    def test_legacy_single_key_slot_is_accepted(self, tmp_path):
        coord, hass = self._coord(
            const.CONF_WEATHER_SERVICE_OWM,
            {const.CONF_WEATHER_SERVICE_API_KEY: "legacy"},
        )
        assert coord._weather_service_key_available(hass) is True

    def test_open_meteo_needs_no_key(self):
        coord, hass = self._coord(const.CONF_WEATHER_SERVICE_OPENMETEO, {})
        assert coord._weather_service_key_available(hass) is True
