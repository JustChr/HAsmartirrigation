"""Unit tests for resolve_weather_config (Phase C8).

The weather-config reconciliation used to be ~80 inline lines in
async_setup_entry. Now it is a pure function, so these tests pin its behavior
(store defaults -> data -> options, use_owm/legacy migrations) directly.
"""

from types import SimpleNamespace

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.config_resolver import resolve_weather_config


def _entry(data=None, options=None):
    return SimpleNamespace(data=data or {}, options=options or {})


def test_defaults_from_store_when_entry_empty():
    store = {const.CONF_USE_WEATHER_SERVICE: True, const.CONF_WEATHER_SERVICE: "OWM"}
    result = resolve_weather_config(store, _entry())
    assert result[const.CONF_USE_WEATHER_SERVICE] is True
    assert result[const.CONF_WEATHER_SERVICE] == "OWM"


def test_entry_data_overrides_store():
    store = {const.CONF_USE_WEATHER_SERVICE: False}
    entry = _entry(
        data={
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
            const.CONF_WEATHER_SERVICE_API_KEY: "  key123  ",
        }
    )
    result = resolve_weather_config(store, entry)
    assert result[const.CONF_USE_WEATHER_SERVICE] is True
    assert result[const.CONF_WEATHER_SERVICE] == const.CONF_WEATHER_SERVICE_OWM
    # api key is stripped
    assert result[const.CONF_WEATHER_SERVICE_API_KEY] == "key123"


def test_options_win_over_data():
    store = {}
    entry = _entry(
        data={
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
        },
        options={
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_PW,
            const.CONF_PW_API_KEY: "pw-key",
        },
    )
    result = resolve_weather_config(store, entry)
    assert result[const.CONF_WEATHER_SERVICE] == const.CONF_WEATHER_SERVICE_PW
    assert result[const.CONF_PW_API_KEY] == "pw-key"


def test_disabling_service_in_options_clears_keys():
    store = {const.CONF_USE_WEATHER_SERVICE: True}
    entry = _entry(
        data={const.CONF_USE_WEATHER_SERVICE: True},
        options={const.CONF_USE_WEATHER_SERVICE: False},
    )
    result = resolve_weather_config(store, entry)
    assert result[const.CONF_USE_WEATHER_SERVICE] is False
    assert result[const.CONF_WEATHER_SERVICE] is None
    assert result[const.CONF_WEATHER_SERVICE_API_KEY] is None
    assert result[const.CONF_WEATHER_SERVICE_API_VERSION] is None


def test_legacy_use_owm_migration_from_data():
    store = {}
    entry = _entry(data={"use_owm": True, "owm_api_key": "legacy-owm"})
    result = resolve_weather_config(store, entry)
    assert result[const.CONF_WEATHER_SERVICE_API_KEY] == "legacy-owm"


def test_legacy_single_key_promoted_to_per_service_slot():
    store = {}
    entry = _entry(
        options={
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
            const.CONF_WEATHER_SERVICE_API_KEY: "  legacy  ",
        }
    )
    result = resolve_weather_config(store, entry)
    # legacy key is stripped, stored in the single slot AND promoted to OWM slot
    assert result[const.CONF_WEATHER_SERVICE_API_KEY] == "legacy"
    assert result[const.CONF_OWM_API_KEY] == "legacy"


def test_legacy_promotion_skipped_when_per_service_slot_already_set():
    store = {}
    entry = _entry(
        options={
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
            const.CONF_OWM_API_KEY: "explicit-owm",
            const.CONF_WEATHER_SERVICE_API_KEY: "legacy",
        }
    )
    result = resolve_weather_config(store, entry)
    # explicit per-service key wins; legacy does not overwrite it
    assert result[const.CONF_OWM_API_KEY] == "explicit-owm"


def test_existing_per_service_key_blocks_legacy_promotion():
    """Across reloads hass.data persists; an existing OWM key blocks promotion."""
    store = {}
    entry = _entry(
        options={
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
            const.CONF_WEATHER_SERVICE_API_KEY: "legacy",
        }
    )
    existing = {const.CONF_OWM_API_KEY: "already-there"}
    result = resolve_weather_config(store, entry, existing=existing)
    # promotion is skipped because the slot is already set in existing state
    assert result.get(const.CONF_OWM_API_KEY) != "legacy"


class TestMigratedEntry:
    """The shape a #120 migration creates: everything in `data`, nothing in options.

    `legacy_config_seed` merges the old entry's data and options and hands the
    result to `async_create_entry(data=...)`, so a key the panel had written to
    `options[owm_api_key]` arrives in the NEW entry's `data`. The per-service
    slots used to be read from `options` only, which dropped it silently and
    started the migrated install with weather disabled.
    """

    def test_per_service_key_in_data_survives(self):
        entry = _entry(
            data={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_OWM_API_KEY: "  owm-from-panel  ",
            }
        )
        result = resolve_weather_config({}, entry)
        assert result[const.CONF_OWM_API_KEY] == "owm-from-panel"

    def test_the_current_key_beats_the_original_one(self):
        """The seam that made this worth fixing.

        A user who changed their key in the panel has the CURRENT one under the
        per-service slot and the ORIGINAL one under the legacy slot, both now in
        `data`. Reading only the legacy slot migrates them onto a credential
        they replaced — the exact outcome `legacy_config_seed` merges options
        over data to avoid.
        """
        entry = _entry(
            data={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_WEATHER_SERVICE_API_KEY: "original-from-setup",
                const.CONF_OWM_API_KEY: "current-from-panel",
            }
        )
        result = resolve_weather_config({}, entry)
        assert result[const.CONF_OWM_API_KEY] == "current-from-panel"

    def test_legacy_slot_in_data_still_promotes(self):
        """An install that never touched the panel has only the legacy slot."""
        entry = _entry(
            data={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_PW,
                const.CONF_WEATHER_SERVICE_API_KEY: " pw-key ",
            }
        )
        result = resolve_weather_config({}, entry)
        assert result[const.CONF_PW_API_KEY] == "pw-key"
        assert result[const.CONF_WEATHER_SERVICE_API_KEY] == "pw-key"

    def test_options_still_win_over_a_key_in_data(self):
        """Precedence is unchanged: a live options key beats the seeded one."""
        entry = _entry(
            data={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_OWM_API_KEY: "seeded",
            },
            options={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_OWM_API_KEY: "re-entered",
            },
        )
        result = resolve_weather_config({}, entry)
        assert result[const.CONF_OWM_API_KEY] == "re-entered"

    def test_a_none_key_in_data_does_not_crash(self):
        """`data[key] = None` used to raise AttributeError on .strip()."""
        entry = _entry(
            data={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_WEATHER_SERVICE_API_KEY: None,
                const.CONF_OWM_API_KEY: None,
            }
        )
        result = resolve_weather_config({}, entry)
        assert result.get(const.CONF_OWM_API_KEY) is None
