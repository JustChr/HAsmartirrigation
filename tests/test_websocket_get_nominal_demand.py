"""websocket_get_nominal_demand must preview demand for an unsaved schedule.

The Add Schedule dialog has no schedule id yet, so it cannot go through
websocket_get_schedules's per-schedule enrichment. This command exposes the
same coordinator.async_nominal_demand_seconds computation directly, keyed off
whatever zone selection the dialog currently holds.
"""

from types import SimpleNamespace
from unittest.mock import Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.websockets import (
    websocket_get_nominal_demand,
)


def _ws_env(coordinator):
    hass = SimpleNamespace(data={const.DOMAIN: {"coordinator": coordinator}})
    connection = Mock()
    sent = {}
    connection.send_result = Mock(side_effect=lambda mid, payload: sent.update(result=payload))
    return hass, connection, sent


async def test_defaults_to_all_zones_when_zones_is_omitted():
    calls = []

    async def nominal(zone_ids=None):
        calls.append(zone_ids)
        return 123.0

    coordinator = SimpleNamespace(async_nominal_demand_seconds=nominal)
    hass, connection, sent = _ws_env(coordinator)

    await websocket_get_nominal_demand.__wrapped__(hass, connection, {"id": 1})

    assert sent["result"] == {"nominal_demand_seconds": 123.0}
    assert calls == ["all"]


async def test_passes_a_specific_zone_selection_through():
    calls = []

    async def nominal(zone_ids=None):
        calls.append(zone_ids)
        return 456.0

    coordinator = SimpleNamespace(async_nominal_demand_seconds=nominal)
    hass, connection, sent = _ws_env(coordinator)

    await websocket_get_nominal_demand.__wrapped__(
        hass, connection, {"id": 1, "zones": ["1", "2"]}
    )

    assert sent["result"] == {"nominal_demand_seconds": 456.0}
    assert calls == [["1", "2"]]
