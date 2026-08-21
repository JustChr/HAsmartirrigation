"""websocket_get_schedules must publish each schedule's nominal demand.

Nominal demand (run_window.nominal_demand_seconds) is the wall clock a
schedule's run takes on a typical night, computed independently of any zone's
live bucket. This pins that the websocket handler attaches it per schedule
without mutating the recurring-schedule manager's own stored dicts.
"""

from types import SimpleNamespace
from unittest.mock import Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.websockets import websocket_get_schedules


def _ws_env(coordinator):
    hass = SimpleNamespace(data={const.DOMAIN: {"coordinator": coordinator}})
    connection = Mock()
    sent = {}
    connection.send_result = Mock(
        side_effect=lambda mid, payload: sent.update(result=payload)
    )
    return hass, connection, sent


async def test_attaches_nominal_demand_seconds_per_schedule():
    schedules = [
        {const.SCHEDULE_CONF_ID: "a", const.SCHEDULE_CONF_ZONES: "all"},
        {const.SCHEDULE_CONF_ID: "b", const.SCHEDULE_CONF_ZONES: [1, 2]},
    ]
    calls = []

    async def nominal(zone_ids=None):
        calls.append(zone_ids)
        return 42.0 if zone_ids == "all" else 99.0

    coordinator = SimpleNamespace(
        recurring_schedule_manager=SimpleNamespace(get_schedules=lambda: schedules),
        async_nominal_demand_seconds=nominal,
    )
    hass, connection, sent = _ws_env(coordinator)

    await websocket_get_schedules.__wrapped__(hass, connection, {"id": 1})

    result = sent["result"]
    assert result[0]["nominal_demand_seconds"] == 42.0
    assert result[1]["nominal_demand_seconds"] == 99.0
    assert calls == ["all", [1, 2]]


async def test_does_not_mutate_the_managers_own_schedule_dicts():
    # get_schedules() returns a shallow copy of the list, not of each entry —
    # the handler must not write the new field into the manager's own dict,
    # or it would leak into whatever later persists that schedule.
    original = {const.SCHEDULE_CONF_ID: "a", const.SCHEDULE_CONF_ZONES: "all"}
    schedules = [original]

    async def nominal(zone_ids=None):
        return 7.0

    coordinator = SimpleNamespace(
        recurring_schedule_manager=SimpleNamespace(get_schedules=lambda: schedules),
        async_nominal_demand_seconds=nominal,
    )
    hass, connection, sent = _ws_env(coordinator)

    await websocket_get_schedules.__wrapped__(hass, connection, {"id": 1})

    assert "nominal_demand_seconds" not in original
