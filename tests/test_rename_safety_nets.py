"""The #120 safety nets: service aliases, the rename report, migration hardening.

These cover the things that are invisible when they break. A missing service
alias does not raise anywhere the user looks -- their automation simply stops
half way through. A recorder rename that aborts on one bad row costs every
entity after it its history, silently and in registry order. So each test drives
the failure, not just the happy path.
"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.irrigation_plus import const, legacy_services
from custom_components.irrigation_plus.legacy_services import (
    async_register_legacy_service_aliases,
    async_remove_legacy_service_aliases,
    plan_service_aliases,
)
from custom_components.irrigation_plus.migrate_domain import (
    RENAME_REPORT_FILENAME,
    apply_recorder_renames,
    async_acknowledge_rename_report,
    async_capture_rename_report,
    async_import_legacy_store,
    async_rename_report_acknowledged,
    async_verify_import,
    legacy_backup_path,
    legacy_storage_path,
    render_rename_report,
    storage_path,
)
from custom_components.irrigation_plus.repairs import (
    _render_examples,
    should_raise_rename_issue,
)


@pytest.fixture(autouse=True)
def _clean_alias_state():
    """Reset the module-level alias bookkeeping around every test.

    Without this, one test's aliases decide what the next test's unload
    removes, and a genuine bug can be hidden -- or invented -- by ordering.
    """
    legacy_services._ALIASED.clear()
    legacy_services._WARNED.clear()
    yield
    legacy_services._ALIASED.clear()
    legacy_services._WARNED.clear()


class _Services:
    """A hass.services double that behaves like the real registry.

    Registering over an existing (domain, service) overwrites silently, exactly
    as Home Assistant does -- which is the whole reason the alias code has to
    ask before it registers.
    """

    def __init__(self, registry=None):
        self._registry = {d: dict(s) for d, s in (registry or {}).items()}
        self.calls = []

    def async_services(self):
        return {d: dict(s) for d, s in self._registry.items()}

    def has_service(self, domain, service):
        return service in self._registry.get(domain, {})

    def async_register(self, domain, service, handler):
        self._registry.setdefault(domain, {})[service] = handler

    def async_remove(self, domain, service):
        self._registry.get(domain, {}).pop(service, None)

    async def async_call(self, domain, service, data, blocking=False, context=None):
        self.calls.append((domain, service, data, blocking, context))


def _hass(tmp_path, services=None, legacy_dir=None, manifest=None):
    """A hass double with a real config directory on disk.

    ``legacy_dir`` creates ``custom_components/smart_irrigation/``; ``manifest``
    writes a manifest.json into it, which is how ownership is decided.
    """
    (tmp_path / ".storage").mkdir(parents=True, exist_ok=True)
    if legacy_dir:
        directory = tmp_path / "custom_components" / const.LEGACY_DOMAIN
        directory.mkdir(parents=True, exist_ok=True)
        if manifest is not None:
            (directory / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

    async def _executor(func, *args):
        return func(*args)

    return SimpleNamespace(
        config=SimpleNamespace(
            path=lambda *parts: str(tmp_path.joinpath(*parts)),
            components=set(),
        ),
        services=services if services is not None else _Services(),
        async_add_executor_job=_executor,
    )


# ---------------------------------------------------------------------------
# Service aliases
# ---------------------------------------------------------------------------


class TestPlanServiceAliases:
    def test_mirrors_every_service_we_registered(self):
        assert plan_service_aliases(["reset_bucket", "calculate_zone"], []) == [
            "calculate_zone",
            "reset_bucket",
        ]

    def test_never_claims_a_name_the_old_domain_already_has(self):
        # async_register overwrites silently, so the loser of this collision
        # would be whoever actually owns the name -- with no error anywhere.
        assert plan_service_aliases(
            ["reset_bucket", "calculate_zone"], ["reset_bucket"]
        ) == ["calculate_zone"]

    def test_nothing_to_alias_on_a_fresh_install(self):
        assert plan_service_aliases([], []) == []


class TestRegisterAliases:
    @pytest.mark.asyncio
    async def test_aliases_every_service_onto_the_old_domain(self, tmp_path):
        services = _Services({const.DOMAIN: {"reset_bucket": Mock()}})
        hass = _hass(tmp_path, services=services)

        aliased = await async_register_legacy_service_aliases(hass)

        assert aliased == ["reset_bucket"]
        assert services.has_service(const.LEGACY_DOMAIN, "reset_bucket")

    @pytest.mark.asyncio
    async def test_the_alias_forwards_the_call_to_the_real_service(self, tmp_path):
        services = _Services({const.DOMAIN: {"reset_bucket": Mock()}})
        hass = _hass(tmp_path, services=services)
        await async_register_legacy_service_aliases(hass)

        handler = services.async_services()[const.LEGACY_DOMAIN]["reset_bucket"]
        await handler(SimpleNamespace(data={"entity_id": "sensor.x"}, context="ctx"))

        assert services.calls == [
            (const.DOMAIN, "reset_bucket", {"entity_id": "sensor.x"}, True, "ctx")
        ]

    @pytest.mark.asyncio
    async def test_skipped_entirely_when_another_project_owns_the_domain(
        self, tmp_path
    ):
        # A foreign smart_irrigation install: claiming its service names is the
        # collision the rename existed to remove.
        services = _Services({const.DOMAIN: {"reset_bucket": Mock()}})
        hass = _hass(
            tmp_path,
            services=services,
            legacy_dir=True,
            manifest={
                "documentation": "https://github.com/altmenorg/HAsmartirrigation"
            },
        )

        assert await async_register_legacy_service_aliases(hass) == []
        assert not services.has_service(const.LEGACY_DOMAIN, "reset_bucket")

    @pytest.mark.asyncio
    async def test_our_own_leftover_directory_does_not_block_aliasing(self, tmp_path):
        # HACS leaves our previous install behind on a domain change. That is
        # not a foreign install, and it must not cost the user their aliases.
        services = _Services({const.DOMAIN: {"reset_bucket": Mock()}})
        hass = _hass(
            tmp_path,
            services=services,
            legacy_dir=True,
            manifest={"documentation": "https://github.com/JustChr/HAsmartirrigation"},
        )

        assert await async_register_legacy_service_aliases(hass) == ["reset_bucket"]

    @pytest.mark.asyncio
    async def test_unload_removes_only_the_aliases_we_registered(self, tmp_path):
        # Both projects publish reset_bucket, so "we have one by that name" does
        # NOT identify ours. Removing on that basis would tear down a foreign
        # integration's service on our unload.
        foreign = Mock()
        services = _Services(
            {
                const.DOMAIN: {"reset_bucket": Mock(), "calculate_zone": Mock()},
                const.LEGACY_DOMAIN: {"reset_bucket": foreign},
            }
        )
        hass = _hass(tmp_path, services=services)

        await async_register_legacy_service_aliases(hass)
        async_remove_legacy_service_aliases(hass)

        assert not services.has_service(const.LEGACY_DOMAIN, "calculate_zone")
        assert services.async_services()[const.LEGACY_DOMAIN]["reset_bucket"] is foreign

    @pytest.mark.asyncio
    async def test_a_name_taken_over_since_we_aliased_it_is_left_alone(self, tmp_path):
        # async_register overwrites silently, so the thing sitting under a name
        # we once aliased may no longer be the thing we put there. Removing by
        # name would then delete somebody else's service.
        services = _Services({const.DOMAIN: {"reset_bucket": Mock()}})
        hass = _hass(tmp_path, services=services)
        await async_register_legacy_service_aliases(hass)

        someone_else = Mock()
        services.async_register(const.LEGACY_DOMAIN, "reset_bucket", someone_else)

        async_remove_legacy_service_aliases(hass)

        assert (
            services.async_services()[const.LEGACY_DOMAIN]["reset_bucket"]
            is someone_else
        )

    @pytest.mark.asyncio
    async def test_the_deprecation_warning_is_logged_once_per_service(
        self, tmp_path, caplog
    ):
        # A scheduled run calls these every day; one warning per call would
        # bury the log the user is meant to read it from.
        services = _Services({const.DOMAIN: {"reset_bucket": Mock()}})
        hass = _hass(tmp_path, services=services)
        await async_register_legacy_service_aliases(hass)
        handler = services.async_services()[const.LEGACY_DOMAIN]["reset_bucket"]

        await handler(SimpleNamespace(data={}, context=None))
        await handler(SimpleNamespace(data={}, context=None))

        warnings = [r for r in caplog.records if r.levelname == "WARNING"]
        assert len(warnings) == 1
        assert f"{const.DOMAIN}.reset_bucket" in warnings[0].getMessage()


# ---------------------------------------------------------------------------
# The rename report
# ---------------------------------------------------------------------------


class TestRenameReport:
    def test_renders_every_pair_as_a_table_row(self):
        out = render_rename_report(
            {
                "sensor.smart_irrigation_lawn": "sensor.irrigation_plus_lawn",
                "sensor.smart_irrigation_beds": "sensor.irrigation_plus_beds",
            }
        )
        assert (
            "| `sensor.smart_irrigation_lawn` | `sensor.irrigation_plus_lawn` |" in out
        )
        assert (
            "| `sensor.smart_irrigation_beds` | `sensor.irrigation_plus_beds` |" in out
        )

    def test_says_that_service_calls_still_work(self):
        # The report has to distinguish what we DID fix from what the user must
        # fix, or it reads as "everything is broken".
        out = render_rename_report({"a": "b"})
        assert f"{const.LEGACY_DOMAIN}.*" in out
        assert f"{const.DOMAIN}.*" in out

    def test_examples_are_truncated_so_the_dialog_stays_readable(self):
        mapping = {f"sensor.old_{i}": f"sensor.new_{i}" for i in range(9)}
        rendered = _render_examples(mapping, limit=3)
        assert rendered.count("->") == 3
        assert "and 6 more" in rendered

    def test_examples_are_empty_when_there_is_nothing_to_show(self):
        assert _render_examples({}) == ""


class TestCaptureRenameReport:
    @pytest.mark.asyncio
    async def test_persists_the_mapping_and_writes_the_table(
        self, tmp_path, monkeypatch
    ):
        hass = _hass(tmp_path)
        saved = {}

        store = SimpleNamespace(
            async_load=AsyncMock(return_value=None),
            async_save=AsyncMock(side_effect=lambda d: saved.update(d)),
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain._migration_store",
            lambda h: store,
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain.build_entity_id_map",
            lambda h, z=None: {"sensor.old": "sensor.new"},
        )

        mapping = await async_capture_rename_report(hass)

        assert mapping == {"sensor.old": "sensor.new"}
        assert saved["entity_id_map"] == {"sensor.old": "sensor.new"}
        report = Path(hass.config.path(RENAME_REPORT_FILENAME))
        assert "sensor.old" in report.read_text(encoding="utf-8")

    @pytest.mark.asyncio
    async def test_a_second_run_never_overwrites_a_good_report_with_nothing(
        self, tmp_path, monkeypatch
    ):
        # By the next setup the OLD registry entries are gone, so the map would
        # come back empty -- and re-saving it would destroy the only record.
        hass = _hass(tmp_path)
        store = SimpleNamespace(
            async_load=AsyncMock(return_value={"entity_id_map": {"a": "b"}}),
            async_save=AsyncMock(),
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain._migration_store",
            lambda h: store,
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain.build_entity_id_map",
            lambda h, z=None: {},
        )

        assert await async_capture_rename_report(hass) == {"a": "b"}
        store.async_save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_an_unwritable_config_directory_still_persists_the_mapping(
        self, tmp_path, monkeypatch
    ):
        # The file is a convenience; the stored map is what the repair reads.
        hass = _hass(tmp_path)
        saved = {}
        store = SimpleNamespace(
            async_load=AsyncMock(return_value=None),
            async_save=AsyncMock(side_effect=lambda d: saved.update(d)),
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain._migration_store",
            lambda h: store,
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain.build_entity_id_map",
            lambda h, z=None: {"sensor.old": "sensor.new"},
        )

        async def _boom(func, *args):
            raise OSError("read-only config directory")

        hass.async_add_executor_job = _boom

        assert await async_capture_rename_report(hass) == {"sensor.old": "sensor.new"}
        assert saved["entity_id_map"] == {"sensor.old": "sensor.new"}


# ---------------------------------------------------------------------------
# Migration hardening
# ---------------------------------------------------------------------------


class TestLegacyBackup:
    @pytest.mark.asyncio
    async def test_the_import_leaves_a_safety_copy(self, tmp_path):
        # Removing the old integration through the UI calls its
        # store.async_delete(), which DELETES the file this migration read. The
        # backup is the only thing left to recover from.
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text('{"version": 9}', encoding="utf-8")

        assert await async_import_legacy_store(hass) is True

        backup = legacy_backup_path(hass)
        assert backup.is_file()
        assert backup.read_text(encoding="utf-8") == '{"version": 9}'

    @pytest.mark.asyncio
    async def test_a_later_run_never_replaces_the_original_backup(self, tmp_path):
        # The first import is the one taken against untouched data.
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text('{"version": 9}', encoding="utf-8")
        await async_import_legacy_store(hass)

        storage_path(hass).unlink()
        legacy_storage_path(hass).write_text('{"version": 99}', encoding="utf-8")
        await async_import_legacy_store(hass)

        assert legacy_backup_path(hass).read_text(encoding="utf-8") == '{"version": 9}'

    @pytest.mark.asyncio
    async def test_no_backup_when_there_was_nothing_to_import(self, tmp_path):
        hass = _hass(tmp_path)
        assert await async_import_legacy_store(hass) is False
        assert not legacy_backup_path(hass).exists()


class TestVerifyImport:
    @pytest.mark.asyncio
    async def test_a_copy_that_produced_no_zones_is_reported(self, tmp_path, caplog):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text("{}", encoding="utf-8")

        assert await async_verify_import(hass, SimpleNamespace(zones={})) is False
        assert "produced NO zones" in caplog.text
        # It must name the backup, or the advice is unactionable.
        assert str(legacy_backup_path(hass)) in caplog.text

    @pytest.mark.asyncio
    async def test_a_healthy_import_is_quiet(self, tmp_path, caplog):
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text("{}", encoding="utf-8")

        assert await async_verify_import(hass, SimpleNamespace(zones={1: {}})) is True
        assert "produced NO zones" not in caplog.text

    @pytest.mark.asyncio
    async def test_a_fresh_install_is_not_a_failed_migration(self, tmp_path):
        # No legacy file at all: an empty store is simply correct here, and
        # crying about it would alarm every new user.
        hass = _hass(tmp_path)
        assert await async_verify_import(hass, SimpleNamespace(zones={})) is True


class TestMigrationGuideUrl:
    """Every rename repair carries MIGRATION_GUIDE_URL as its learn-more link.

    It pointed at `installation-migration` -- which exists, and is the unrelated
    V1 (0.0.x) -> V2 page from 2022. A wrong-but-live URL is the worst kind:
    nothing 404s, so nothing complains, and the user reading a repair about the
    domain rename lands on advice for a different upgrade entirely.
    """

    def test_the_url_resolves_to_a_docs_page_that_exists(self):
        slug = const.MIGRATION_GUIDE_URL.rstrip("/").rsplit("/", 1)[-1]
        page = Path(__file__).resolve().parents[1] / "docs" / f"{slug}.md"
        assert page.is_file(), f"{const.MIGRATION_GUIDE_URL} has no page at {page}"

    def test_the_page_is_about_this_rename(self):
        # Existing is not enough -- the previous target existed too.
        slug = const.MIGRATION_GUIDE_URL.rstrip("/").rsplit("/", 1)[-1]
        page = Path(__file__).resolve().parents[1] / "docs" / f"{slug}.md"
        text = page.read_text(encoding="utf-8")
        assert const.LEGACY_NAME in text
        assert const.NAME in text
        assert const.DOMAIN in text


class TestApplyRecorderRenames:
    """The loop used to be one try/except around the whole thing.

    One bad row then cost every entity AFTER it its history -- silently, and in
    registry order, so which zones lost their graphs depended on nothing the
    user could see.
    """

    def _ok(self):
        seen = []
        return seen, lambda old, new: seen.append((old, new))

    def test_renames_every_id(self):
        states, rename_states = self._ok()
        stats, rename_stats = self._ok()

        renamed, failed = apply_recorder_renames(
            {"sensor.a": "sensor.x", "sensor.b": "sensor.y"},
            rename_states,
            rename_stats,
        )

        assert (renamed, failed) == (2, [])
        assert states == [("sensor.a", "sensor.x"), ("sensor.b", "sensor.y")]
        assert stats == states

    def test_one_bad_id_does_not_cost_the_others_their_history(self):
        stats, rename_stats = self._ok()
        done = []

        def rename_states(old, new):
            if old == "sensor.bad":
                raise RuntimeError("UNIQUE constraint failed: states_meta.entity_id")
            done.append(old)

        renamed, failed = apply_recorder_renames(
            {
                "sensor.bad": "sensor.bad_new",
                "sensor.good": "sensor.good_new",
                "sensor.also_good": "sensor.also_good_new",
            },
            rename_states,
            rename_stats,
        )

        assert renamed == 2
        assert failed == ["sensor.bad"]
        # The entities AFTER the failure are the ones the old code lost.
        assert done == ["sensor.good", "sensor.also_good"]

    def test_a_statistics_failure_is_caught_too(self):
        # Statistics and states are separate calls; either can raise on its own.
        _, rename_states = self._ok()

        def rename_stats(old, new):
            raise RuntimeError("no such statistic")

        renamed, failed = apply_recorder_renames(
            {"sensor.a": "sensor.x"}, rename_states, rename_stats
        )
        assert (renamed, failed) == (0, ["sensor.a"])

    def test_the_failure_is_named_so_the_user_can_see_which(self, caplog):
        def rename_states(old, new):
            raise RuntimeError("boom")

        apply_recorder_renames(
            {"sensor.lawn_bucket": "sensor.new"}, rename_states, lambda o, n: None
        )
        assert "sensor.lawn_bucket" in caplog.text

    def test_an_unexpected_exception_type_is_still_contained(self):
        # What the recorder raises here is not a documented set. Narrowing the
        # catch to a known list is the mutation that must not survive.
        def rename_states(old, new):
            if old == "sensor.bad":
                raise ZeroDivisionError("something nobody predicted")

        renamed, failed = apply_recorder_renames(
            {"sensor.bad": "a", "sensor.good": "b"}, rename_states, lambda o, n: None
        )
        assert renamed == 1
        assert failed == ["sensor.bad"]

    def test_nothing_to_rename_is_not_a_failure(self):
        assert apply_recorder_renames({}, None, None) == (0, [])


class TestShouldRaiseRenameIssue:
    def test_raised_when_there_is_a_report_and_it_is_unacknowledged(self):
        assert should_raise_rename_issue({"a": "b"}, False) is True

    def test_stays_dismissed_once_acknowledged(self):
        # Repairs are re-raised on every setup. Without this the notice comes
        # back after each restart, which is worse than never showing it.
        assert should_raise_rename_issue({"a": "b"}, True) is False

    def test_never_raised_on_an_install_that_was_not_migrated(self):
        assert should_raise_rename_issue({}, False) is False


class TestAcknowledgementPersistence:
    @pytest.mark.asyncio
    async def test_the_acknowledgement_survives_and_keeps_the_mapping(
        self, tmp_path, monkeypatch
    ):
        # The mapping must NOT be discarded when the notice is dismissed: a user
        # part-way through repointing their automations still needs the table.
        hass = _hass(tmp_path)
        data = {"entity_id_map": {"sensor.old": "sensor.new"}}

        store = SimpleNamespace(
            async_load=AsyncMock(side_effect=lambda: dict(data)),
            async_save=AsyncMock(side_effect=lambda d: data.update(d)),
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.migrate_domain._migration_store",
            lambda h: store,
        )

        assert await async_rename_report_acknowledged(hass) is False
        await async_acknowledge_rename_report(hass)
        assert await async_rename_report_acknowledged(hass) is True
        assert data["entity_id_map"] == {"sensor.old": "sensor.new"}
