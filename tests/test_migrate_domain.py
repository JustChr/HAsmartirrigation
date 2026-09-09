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
    async_legacy_config_seed,
    async_legacy_install_present,
    find_legacy_entry,
    legacy_config_seed,
    legacy_install_present,
    legacy_storage_path,
    plan_credential_warning,
    read_legacy_weather_profile,
    storage_path,
    stored_zone_count,
)


def _hass(tmp_path, legacy_entries=()):
    """A hass double with a real .storage directory and a config-entry stub."""
    storage = tmp_path / ".storage"
    storage.mkdir(parents=True, exist_ok=True)

    async def _executor(func, *args):
        return func(*args)

    return SimpleNamespace(
        config=SimpleNamespace(path=lambda *parts: str(tmp_path.joinpath(*parts))),
        data={},
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


class TestLegacyOwnership:
    """Only migrate an install that is actually ours.

    Upstream ships the same domain and installs into the same directory, so the
    surviving smart_irrigation install may be theirs. Copying its storage and
    renaming its history would break an integration that is still running.
    """

    def _write_manifest(self, tmp_path, payload):
        d = tmp_path / "custom_components" / const.LEGACY_DOMAIN
        d.mkdir(parents=True, exist_ok=True)
        (d / "manifest.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_our_own_previous_release_is_recognised(self, tmp_path):
        from custom_components.irrigation_plus.migrate_domain import (
            legacy_install_is_ours,
        )

        self._write_manifest(
            tmp_path,
            {"documentation": "https://github.com/JustChr/HAsmartirrigation"},
        )
        assert legacy_install_is_ours(_hass(tmp_path)) is True

    def test_upstreams_install_is_refused(self, tmp_path):
        from custom_components.irrigation_plus.migrate_domain import (
            legacy_install_is_ours,
            legacy_install_present,
        )

        self._write_manifest(
            tmp_path,
            {
                "documentation": "https://github.com/altmenorg/HAsmartirrigation",
                "codeowners": ["@altmenorg"],
            },
        )
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text("{}", encoding="utf-8")
        assert legacy_install_is_ours(hass) is False
        # ...and the migration is therefore never offered.
        assert legacy_install_present(hass) is False

    def test_an_absent_manifest_is_assumed_to_be_ours(self, tmp_path):
        # We cannot tell, and the overwhelmingly likely reason a legacy install
        # exists at all is that it is the one being replaced.
        from custom_components.irrigation_plus.migrate_domain import (
            legacy_install_is_ours,
        )

        assert legacy_install_is_ours(_hass(tmp_path)) is True

    def test_codeowners_alone_is_enough(self, tmp_path):
        from custom_components.irrigation_plus.migrate_domain import (
            legacy_install_is_ours,
        )

        self._write_manifest(tmp_path, {"codeowners": ["@JustChr"]})
        assert legacy_install_is_ours(_hass(tmp_path)) is True

    def test_this_repository_derives_exactly_the_upstream_marker(self):
        """The widening must be a no-op for upstream itself.

        The marker set is now read from this build's own manifest instead of a
        constant, so for this repository it has to come back as the one value
        the constant used to hold. If it ever does not, "widening" has quietly
        changed who upstream counts as its own.
        """
        from custom_components.irrigation_plus.migrate_domain import (
            our_owner_markers,
        )

        assert our_owner_markers() == ("justchr",)

    def test_a_rebranded_fork_recognises_its_own_previous_release(self):
        """The case the hard-coded marker got wrong.

        A downstream fork rebrands its manifest, and its pre-rename release
        carried the same owner -- so its old install answers this question with
        the fork's name and never matched. The user was not offered the import
        at all, and nothing said why.
        """
        from custom_components.irrigation_plus.migrate_domain import (
            manifest_is_ours,
            plan_owner_markers,
        )

        markers = plan_owner_markers(["@Eifel-Joe"])
        assert manifest_is_ours(
            {
                "documentation": "https://github.com/Eifel-Joe/HAsmartirrigation",
                "codeowners": ["@Eifel-Joe"],
            },
            markers,
        )

    def test_a_fork_still_recognises_an_unbranded_previous_release(self):
        # A fork that rebranded only after the rename has an old manifest that
        # still names upstream. That is why the upstream marker is kept in the
        # set rather than replaced by the fork's own.
        from custom_components.irrigation_plus.migrate_domain import (
            manifest_is_ours,
            plan_owner_markers,
        )

        markers = plan_owner_markers(["@Eifel-Joe"])
        assert manifest_is_ours({"codeowners": ["@JustChr"]}, markers)

    def test_upstreams_install_is_refused_by_a_fork_too(self):
        # The whole point of the predicate, and the thing the widening must not
        # cost: a fork must not migrate altmenorg's install either.
        from custom_components.irrigation_plus.migrate_domain import (
            manifest_is_ours,
            plan_owner_markers,
        )

        markers = plan_owner_markers(["@Eifel-Joe"])
        assert not manifest_is_ours(
            {
                "documentation": "https://altmenorg.github.io/HAsmartirrigation/",
                "codeowners": ["@altmenorg", "@jeroenterheerdt"],
            },
            markers,
        )


def _write_legacy_store(hass, config):
    """A legacy storage file whose `data.config` holds `config`."""
    legacy_storage_path(hass).write_text(
        json.dumps({"version": 9, "data": {"config": config, "zones": {}}}),
        encoding="utf-8",
    )


class TestCredentialWarningPlanning:
    """`plan_credential_warning` — is the user about to lose their API key?

    Replaces the staged-seed suite. The bridge release was supposed to leave a
    copy of the credentials in the storage file so this module could recover
    them once the config entry was gone, and it never wrote one: the store
    filters every incoming change against `attr.fields_dict(Config)`, and
    `Config` has no credential attribute (#128). The read path is deleted --
    it could only ever return empty, and it was inert code that had already
    talked our own documentation into promising a recovery that never happened.

    What is left is telling the user, at the moment it still means something.
    """

    def test_names_the_service_whose_key_did_not_survive(self):
        seed = {
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
        }
        assert plan_credential_warning(seed) == const.CONF_WEATHER_SERVICE_OWM

    def test_silent_when_the_key_came_across(self):
        for slot in (
            const.CONF_WEATHER_SERVICE_API_KEY,
            const.CONF_OWM_API_KEY,
            const.CONF_PW_API_KEY,
            const.CONF_MET_API_KEY,
        ):
            seed = {
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                slot: "recovered",
            }
            assert plan_credential_warning(seed) is None, slot

    def test_silent_when_the_old_install_used_no_weather_service(self):
        # Warning about a key they never had is how a user learns to skip the
        # warnings that count.
        assert plan_credential_warning({const.CONF_USE_WEATHER_SERVICE: False}) is None
        assert plan_credential_warning({}) is None
        assert plan_credential_warning(None) is None

    def test_silent_for_a_provider_that_needs_no_key(self):
        # Open-Meteo cannot lose a credential it never uses. Derived from
        # CONF_WEATHER_SERVICES_NO_API_KEY rather than restated, so adding a
        # second free provider cannot leave a stale copy of the list here.
        for service in const.CONF_WEATHER_SERVICES_NO_API_KEY:
            seed = {
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: service,
            }
            assert plan_credential_warning(seed) is None, service

    def test_silent_when_the_service_itself_is_unknown(self):
        # Nothing useful to name, and "your  API key" reads as a bug.
        seed = {const.CONF_USE_WEATHER_SERVICE: True, const.CONF_WEATHER_SERVICE: ""}
        assert plan_credential_warning(seed) is None

    def test_the_store_answers_when_the_config_entry_is_gone(self):
        # THE case this warning exists for: removing Smart Irrigation through
        # the UI first deletes the entry and the key with it, so the seed is
        # empty. Without the store there is nothing to warn about and nothing
        # to name, and the only users who lost a key get no warning at all.
        profile = {
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_MET,
        }
        assert plan_credential_warning({}, profile) == const.CONF_WEATHER_SERVICE_MET

    def test_the_config_entry_still_wins_over_the_store(self):
        # The entry is what the old integration was actually running on; the
        # store can be an older copy. A stale "true" there must not manufacture
        # a warning for an install that had already switched weather off.
        seed = {const.CONF_USE_WEATHER_SERVICE: False}
        profile = {
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
        }
        assert plan_credential_warning(seed, profile) is None

    def test_the_store_alone_cannot_invent_a_service(self):
        assert plan_credential_warning({}, {}) is None
        assert plan_credential_warning({}, None) is None
        assert (
            plan_credential_warning({}, {const.CONF_USE_WEATHER_SERVICE: True}) is None
        )

    def test_an_empty_key_does_not_count_as_supplied(self):
        seed = {
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_PW,
            const.CONF_PW_API_KEY: "",
        }
        assert plan_credential_warning(seed) == const.CONF_WEATHER_SERVICE_PW


class TestReadLegacyWeatherProfile:
    """The store answers WHICH service, never the key (#128).

    The split is the point: the credential lived in the config entry, the
    service name is a real `Config` attribute and is genuinely in the store.
    That is what lets the warning name a provider for the one population whose
    entry is already gone.
    """

    def test_reads_the_two_settings_it_is_allowed_to(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text(
            json.dumps(
                {
                    "version": 9,
                    "data": {
                        "config": {
                            const.CONF_USE_WEATHER_SERVICE: True,
                            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_MET,
                            "days_between_irrigation": 3,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        assert read_legacy_weather_profile(p) == {
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_MET,
        }

    def test_never_returns_a_credential_even_if_one_is_somehow_there(self, tmp_path):
        # A hand-edited store, or a downstream fork that added the attribute.
        # Reading it back would resurrect the promise #128 removed, and put a
        # secret into a code path whose whole justification is that it handles
        # none.
        p = tmp_path / "s.json"
        p.write_text(
            json.dumps(
                {
                    "version": 9,
                    "data": {
                        "config": {
                            const.CONF_USE_WEATHER_SERVICE: True,
                            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                            const.CONF_OWM_API_KEY: "should-never-be-read",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        assert const.CONF_OWM_API_KEY not in read_legacy_weather_profile(p)

    def test_unreadable_and_missing_files_are_empty_not_fatal(self, tmp_path):
        missing = tmp_path / "nope.json"
        assert read_legacy_weather_profile(missing) == {}
        corrupt = tmp_path / "c.json"
        corrupt.write_text("{not json", encoding="utf-8")
        assert read_legacy_weather_profile(corrupt) == {}
        empty = tmp_path / "e.json"
        empty.write_text('{"version": 9, "data": {}}', encoding="utf-8")
        assert read_legacy_weather_profile(empty) == {}


class TestLegacyConfigSeed:
    """The seed comes from the old config entry, and from nowhere else (#128)."""

    async def test_the_entry_supplies_the_key(self, tmp_path):
        entry = _entry(options={const.CONF_OWM_API_KEY: "live-key"})
        hass = _hass(tmp_path, [entry])

        seed = await async_legacy_config_seed(hass)

        assert seed[const.CONF_OWM_API_KEY] == "live-key"

    async def test_a_storage_file_is_never_read_for_credentials(self, tmp_path):
        """The staged copy the guide used to promise does not exist.

        No release ever wrote one, so a store that appears to hold a key is
        either hand-edited or from a downstream fork -- and reading it back
        would resurrect the promise this issue removed. Pinned so the fallback
        cannot quietly return.
        """
        hass = _hass(tmp_path)
        _write_legacy_store(
            hass,
            {
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_OWM_API_KEY: "not-a-real-staging-slot",
            },
        )

        seed = await async_legacy_config_seed(hass)

        assert const.CONF_OWM_API_KEY not in seed
        assert seed == {}

    async def test_no_entry_and_no_store_is_simply_empty(self, tmp_path):
        assert await async_legacy_config_seed(_hass(tmp_path)) == {}

    async def test_a_corrupt_store_does_not_break_the_config_flow(self, tmp_path):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text("{not json", encoding="utf-8")
        assert await async_legacy_config_seed(hass) == {}


def _store_doc(zones):
    return {"version": 9, "data": {"config": {}, "zones": zones}}


class TestStoredZoneCount:
    """`stored_zone_count` — 'unreadable' and 'empty' must not be the same answer."""

    def test_counts_the_zones(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text(json.dumps(_store_doc({"1": {}, "2": {}})), encoding="utf-8")
        assert stored_zone_count(p) == 2

    def test_no_zones_key_is_zero(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text(json.dumps({"version": 9, "data": {}}), encoding="utf-8")
        assert stored_zone_count(p) == 0

    def test_empty_zones_is_zero(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text(json.dumps(_store_doc({})), encoding="utf-8")
        assert stored_zone_count(p) == 0

    def test_unreadable_is_none_not_zero(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text("{not json", encoding="utf-8")
        assert stored_zone_count(p) is None

    def test_a_missing_file_is_none(self, tmp_path):
        assert stored_zone_count(tmp_path / "nope.json") is None

    def test_a_non_dict_document_is_none(self, tmp_path):
        p = tmp_path / "s.json"
        p.write_text("[1, 2, 3]", encoding="utf-8")
        assert stored_zone_count(p) is None


class TestReimportOverAnEmptyStore:
    """The state a crashed setup leaves behind, and how a retry escapes it.

    A setup that fails after the store is created leaves an EMPTY
    irrigation_plus.storage; `async_remove_entry` then skips deleting it
    (no coordinator on a failed setup), so the plain refuse-to-overwrite rule
    made that file permanent and every later import silently did nothing.
    """

    async def test_reimports_when_ours_holds_no_zones(self, tmp_path):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text(
            json.dumps(_store_doc({"1": {"name": "Lawn"}})), encoding="utf-8"
        )
        storage_path(hass).write_text(json.dumps(_store_doc({})), encoding="utf-8")

        assert await async_import_legacy_store(hass) is True
        assert stored_zone_count(storage_path(hass)) == 1
        # The discarded file is kept, never silently destroyed.
        superseded = (
            tmp_path / ".storage" / f"{const.DOMAIN}.storage.empty-before-import.bak"
        )
        assert superseded.is_file()
        assert stored_zone_count(superseded) == 0

    async def test_never_overwrites_a_store_that_has_zones(self, tmp_path):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text(
            json.dumps(_store_doc({"1": {"name": "Legacy"}})), encoding="utf-8"
        )
        storage_path(hass).write_text(
            json.dumps(_store_doc({"7": {"name": "Ours"}})), encoding="utf-8"
        )

        assert await async_import_legacy_store(hass) is False
        assert "Ours" in storage_path(hass).read_text(encoding="utf-8")

    async def test_an_unreadable_store_of_ours_is_never_overwritten(self, tmp_path):
        """Corrupt is not empty: refuse, or a bad parse licenses data loss."""
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text(
            json.dumps(_store_doc({"1": {}})), encoding="utf-8"
        )
        storage_path(hass).write_text("{not json", encoding="utf-8")

        assert await async_import_legacy_store(hass) is False
        assert storage_path(hass).read_text(encoding="utf-8") == "{not json"

    async def test_an_empty_legacy_store_does_not_replace_ours(self, tmp_path):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text(
            json.dumps(_store_doc({})), encoding="utf-8"
        )
        storage_path(hass).write_text(json.dumps(_store_doc({})), encoding="utf-8")

        assert await async_import_legacy_store(hass) is False

    async def test_the_superseded_backup_is_never_overwritten(self, tmp_path):
        hass = _hass(tmp_path)
        superseded = (
            tmp_path / ".storage" / f"{const.DOMAIN}.storage.empty-before-import.bak"
        )
        superseded.write_text('{"first": true}', encoding="utf-8")
        legacy_storage_path(hass).write_text(
            json.dumps(_store_doc({"1": {}})), encoding="utf-8"
        )
        storage_path(hass).write_text(json.dumps(_store_doc({})), encoding="utf-8")

        assert await async_import_legacy_store(hass) is True
        assert "first" in superseded.read_text(encoding="utf-8")


class TestLegacyPresenceOffTheLoop:
    """The config flow must not stat/read files on the event loop.

    Home Assistant detects it and logs "blocking call ... inside the event loop
    ... please create a bug report", naming us. It fired on the live instance
    from `async_step_user` -> `legacy_install_present` -> `legacy_install_is_ours`.
    """

    async def test_goes_through_the_executor(self, tmp_path):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text('{"version": 9, "data": {}}', "utf-8")

        calls = []
        inner = hass.async_add_executor_job

        async def _counting(func, *args):
            calls.append(getattr(func, "__name__", str(func)))
            return await inner(func, *args)

        hass.async_add_executor_job = _counting

        assert await async_legacy_install_present(hass) is True
        assert calls == ["legacy_install_present"]

    async def test_agrees_with_the_synchronous_version(self, tmp_path):
        hass = _hass(tmp_path)
        assert await async_legacy_install_present(hass) is legacy_install_present(hass)
        legacy_storage_path(hass).write_text('{"version": 9, "data": {}}', "utf-8")
        assert await async_legacy_install_present(hass) is legacy_install_present(hass)
