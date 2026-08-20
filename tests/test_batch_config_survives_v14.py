"""The v14 schedule reshape must not strip upstream's batch config keys.

The migration filters data["config"] against attr.fields_dict(Config) and drops
the rest. Batch config arrived at storage version 13 with no version bump of its
own, so it is only carried through v14 by virtue of being on Config. A batch
install that upgrades would otherwise lose its run service, its stop service and
its paused indicator silently, and the mode would fall back to "not configured".
"""

import pytest

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.store import MigratableStore


def _v13_doc():
    return {
        "config": {
            const.CONF_BATCH_RUN_SERVICE: "script.irrigation_run_batch",
            const.CONF_BATCH_STOP_SERVICE: "script.irrigation_stop_batch",
            const.CONF_BATCH_PAUSED_ENTITY: "binary_sensor.controller_paused",
            const.CONF_BATCH_PAUSE_TIMEOUT: 1800,
            const.CONF_BATCH_PAUSE_TIMEOUT_SERVICE: "script.give_up",
            const.CONF_FIRED_OCCURRENCES: {"s1": "2026-06-11T04:00:00+00:00"},
            "recurring_schedules": [
                {
                    "id": "s1",
                    "name": "overnight",
                    "type": "daily",
                    "time": "06:00",
                    "time_anchor": "finish",
                    "action": "irrigate",
                    "zones": "all",
                    "enabled": True,
                }
            ],
        },
        "zones": [],
        "mappings": [],
        "modules": [],
    }


class TestBatchConfigSurvivesV14:
    @pytest.mark.asyncio
    async def test_every_batch_key_is_still_there(self, hass):
        store = MigratableStore(hass, 14, "smart_irrigation.storage")
        out = await store._async_migrate_func(13, _v13_doc())
        cfg = out["config"]
        assert cfg[const.CONF_BATCH_RUN_SERVICE] == "script.irrigation_run_batch"
        assert cfg[const.CONF_BATCH_STOP_SERVICE] == "script.irrigation_stop_batch"
        assert cfg[const.CONF_BATCH_PAUSED_ENTITY] == "binary_sensor.controller_paused"
        assert cfg[const.CONF_BATCH_PAUSE_TIMEOUT] == 1800
        assert cfg[const.CONF_BATCH_PAUSE_TIMEOUT_SERVICE] == "script.give_up"

    @pytest.mark.asyncio
    async def test_the_fired_marker_survives_too(self, hass):
        """Upstream's reload guard, carried across the reshape."""
        store = MigratableStore(hass, 14, "smart_irrigation.storage")
        out = await store._async_migrate_func(13, _v13_doc())
        assert out["config"][const.CONF_FIRED_OCCURRENCES] == {
            "s1": "2026-06-11T04:00:00+00:00"
        }

    @pytest.mark.asyncio
    async def test_and_the_schedule_was_actually_reshaped(self, hass):
        """Guards against the assertions above passing on an untouched document."""
        store = MigratableStore(hass, 14, "smart_irrigation.storage")
        out = await store._async_migrate_func(13, _v13_doc())
        sched = out["config"]["recurring_schedules"][0]
        assert sched[const.SCHEDULE_CONF_RECURRENCE] == const.SCHEDULE_RECURRENCE_DAILY
        assert sched[const.SCHEDULE_CONF_FINISH_MODE] == const.SCHEDULE_BOUND_MODE_TIME
        assert sched[const.SCHEDULE_CONF_FINISH_TIME] == "06:00"
        assert "type" not in sched
