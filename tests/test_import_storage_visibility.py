"""The imported storage file has to be visible to the store that reads it.

Every other test of the #120 import asserts on the FILE: the bytes landed, the
version travelled, the backup exists. All of that was true of the migration
that shipped, and it still produced an empty install, because Home Assistant
decides whether a storage key exists from a directory listing taken once during
startup -- before the file the import writes.

Two things follow for the tests here. They drive Home Assistant's own ``Store``
and ``_StoreManager`` rather than a double, since a double would be written
from the same understanding as the code and this defect lives exactly where
that understanding was wrong. And they have to put back Home Assistant's real
read path first: ``enable_custom_integrations`` is autouse across this suite
and brings ``hass_storage`` with it, which replaces ``Store._async_load`` with
an in-memory dict for every test in the file. Under that replacement no test
can tell a readable storage file from an unreadable one.
"""

import asyncio
import json
from types import SimpleNamespace

import pytest
from homeassistant.helpers import storage as ha_storage

from custom_components.irrigation_plus.migrate_domain import (
    async_import_legacy_store,
    legacy_storage_path,
    storage_path,
)
from custom_components.irrigation_plus.store import STORAGE_KEY, STORAGE_VERSION

# Captured at import, which happens during collection and so before any fixture
# has had the chance to replace it.
REAL_STORE_LOAD = ha_storage.Store._async_load

# A pre-#120 document, at the storage version the oldest installs still carry.
LEGACY_DOCUMENT = {
    "version": 5,
    "minor_version": 1,
    "key": "smart_irrigation",
    "data": {
        "config": {"units": "imperial"},
        "zones": [
            {"id": 0, "name": "Front South"},
            {"id": 1, "name": "Back"},
        ],
        "modules": [],
        "mappings": [],
    },
}


@pytest.fixture(autouse=True)
def real_storage_reads(hass_storage):
    """Undo the suite-wide in-memory storage mock for this module.

    Requests ``hass_storage`` so this runs after the mock is installed rather
    than before it, and assigns rather than monkeypatching: monkeypatch would
    restore the mock at teardown, and the next test's mock cannot be built from
    another mock.
    """
    ha_storage.Store._async_load = REAL_STORE_LOAD
    yield
    ha_storage.Store._async_load = REAL_STORE_LOAD


class _PassthroughStore(ha_storage.Store):
    """Home Assistant's real Store, minus a schema this test does not care about.

    Only ``_async_migrate_func`` is supplied. Everything that decides whether
    the file is read at all -- the manager, the cache, the path -- is Home
    Assistant's own.
    """

    async def _async_migrate_func(self, old_major, old_minor, data):
        return data


def _hass(tmp_path):
    """A hass double real enough for Home Assistant's storage layer."""

    async def _executor(func, *args):
        return func(*args)

    (tmp_path / ".storage").mkdir(parents=True, exist_ok=True)
    return SimpleNamespace(
        config=SimpleNamespace(
            config_dir=str(tmp_path),
            path=lambda *parts: str(tmp_path.joinpath(*parts)),
            components=set(),
        ),
        data={},
        loop=asyncio.get_running_loop(),
        bus=SimpleNamespace(async_listen_once=lambda *args, **kwargs: None),
        async_add_executor_job=_executor,
        state=None,
    )


async def _start_home_assistant(hass):
    """Take the startup listing of .storage, as Home Assistant does on boot."""
    manager = ha_storage.get_internal_store_manager(hass)
    await manager.async_initialize()
    return manager


async def _load_our_store(hass):
    return await _PassthroughStore(hass, STORAGE_VERSION, STORAGE_KEY).async_load()


class TestImportedStoreIsReadable:
    @pytest.mark.asyncio
    async def test_the_import_is_read_back_in_the_same_run(self, tmp_path):
        """The reported failure: an empty panel from a byte-perfect copy.

        The user adds this integration to a Home Assistant that started without
        an ``irrigation_plus.storage``, so the key is absent from the startup
        listing. Nothing here is specific to storage version 5 or to the data:
        the copy is simply never read.
        """
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text(
            json.dumps(LEGACY_DOCUMENT), encoding="utf-8"
        )
        await _start_home_assistant(hass)

        assert await async_import_legacy_store(hass) is True
        assert storage_path(hass).is_file()

        loaded = await _load_our_store(hass)
        assert loaded is not None, "the file on disk was reported as missing"
        assert len(loaded["zones"]) == 2

    @pytest.mark.asyncio
    async def test_an_import_that_copied_nothing_changes_nothing(self, tmp_path):
        """A fresh install must not be told a file it never wrote now exists."""
        hass = _hass(tmp_path)
        manager = await _start_home_assistant(hass)

        assert await async_import_legacy_store(hass) is False
        # Still answered from the startup listing, which is the cheap answer.
        assert manager.async_fetch(STORAGE_KEY) == (False, None)

    @pytest.mark.asyncio
    async def test_a_store_that_predates_startup_still_loads(self, tmp_path):
        """The path that already worked: our file present when the listing ran.

        This is what a restart gives, and it is why the reported failure
        recovers on its own. It has to keep working.
        """
        hass = _hass(tmp_path)
        document = dict(LEGACY_DOCUMENT, version=STORAGE_VERSION)
        storage_path(hass).write_text(json.dumps(document), encoding="utf-8")
        await _start_home_assistant(hass)

        loaded = await _load_our_store(hass)
        assert loaded is not None
        assert len(loaded["zones"]) == 2

    @pytest.mark.asyncio
    async def test_the_import_survives_a_home_assistant_without_the_cache(
        self, tmp_path, monkeypatch
    ):
        """Reaching into an undocumented cache must not be able to fail setup."""
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text(
            json.dumps(LEGACY_DOCUMENT), encoding="utf-8"
        )
        monkeypatch.delattr(ha_storage, "STORAGE_MANAGER")

        assert await async_import_legacy_store(hass) is True
        assert storage_path(hass).is_file()
