"""The config flow's #120 migrate step, end to end over the seed.

`tests/test_config_flow.py` is quarantined (it drives a real flow, which needs
panel_custom -> frontend -> websocket_api), so the migrate step had no coverage
at all -- and it is the step that decides what a migrated install is created
with. These drive the handler directly and assert on the data it would create
the entry from: `_check_unique` and `async_create_entry` are Home Assistant's,
not ours, and are stubbed.
"""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.config_flow import SmartIrrigationConfigFlow
from custom_components.irrigation_plus.migrate_domain import legacy_storage_path


def _hass(tmp_path, legacy_entries=()):
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


def _flow(hass):
    """A flow whose entry creation is captured rather than performed."""
    flow = SmartIrrigationConfigFlow()
    flow.hass = hass
    flow._check_unique = AsyncMock()
    created = {}

    def _create_entry(title=None, data=None, **kwargs):
        created["title"] = title
        created["data"] = data
        return {"type": "create_entry", "title": title, "data": data}

    flow.async_create_entry = _create_entry
    return flow, created


class TestMigrateStep:
    async def test_carries_the_key_from_a_surviving_config_entry(self, tmp_path):
        entry = SimpleNamespace(
            entry_id="legacy1",
            data={const.CONF_WEATHER_SERVICE_API_KEY: "original"},
            options={
                const.CONF_USE_WEATHER_SERVICE: True,
                const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
                const.CONF_OWM_API_KEY: "current",
            },
        )
        flow, created = _flow(_hass(tmp_path, [entry]))

        await flow.async_step_migrate({const.CONF_MIGRATED_FROM_LEGACY: True})

        assert created["data"][const.CONF_OWM_API_KEY] == "current"
        assert created["data"][const.CONF_USE_WEATHER_SERVICE] is True
        assert created["data"][const.CONF_MIGRATED_FROM_LEGACY] is True

    async def test_falls_back_to_the_key_the_bridge_staged(self, tmp_path):
        """Entry already removed, storage file left behind with the staged key."""
        hass = _hass(tmp_path)
        legacy_storage_path(hass).write_text(
            json.dumps(
                {
                    "version": 9,
                    "data": {
                        "config": {
                            const.CONF_USE_WEATHER_SERVICE: True,
                            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_PW,
                            const.CONF_PW_API_KEY: "staged-by-the-bridge",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        flow, created = _flow(hass)

        await flow.async_step_migrate({const.CONF_MIGRATED_FROM_LEGACY: True})

        assert created["data"][const.CONF_PW_API_KEY] == "staged-by-the-bridge"
        # Not left switched off by the setdefault below it, which is what makes
        # the recovered key actually reach a weather client.
        assert created["data"][const.CONF_USE_WEATHER_SERVICE] is True

    async def test_nothing_recoverable_still_creates_a_usable_entry(self, tmp_path):
        """A pre-bridge install with its entry gone: empty, but weather off, not broken."""
        flow, created = _flow(_hass(tmp_path))

        await flow.async_step_migrate({const.CONF_MIGRATED_FROM_LEGACY: True})

        assert created["data"][const.CONF_USE_WEATHER_SERVICE] is False
        assert created["data"][const.CONF_INSTANCE_NAME] == const.NAME

    async def test_declining_does_not_seed_anything(self, tmp_path):
        entry = SimpleNamespace(
            entry_id="legacy1",
            data={},
            options={const.CONF_OWM_API_KEY: "current"},
        )
        flow, created = _flow(_hass(tmp_path, [entry]))

        result = await flow.async_step_migrate({const.CONF_MIGRATED_FROM_LEGACY: False})

        assert created == {}
        assert result["step_id"] == "user"
