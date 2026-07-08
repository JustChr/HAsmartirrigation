"""The manual-run websocket handlers must not block on the run.

A distributor member's "irrigate now (X min)" drives a full distributor cycle
(open inlet, sleep the window, close, advance, ...), which can take minutes. The
old handlers ``await``ed that whole run before sending the websocket result, so
the panel's START button hung until the cycle finished. These tests pin the
fire-and-forget contract: schedule the run as a background task and ack the
websocket immediately (progress then shows live via the _update_frontend
refresh). The scheduled-vs-awaited ordering is asserted so the test fails on the
old blocking code without hanging (the run bodies complete instantly here).
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.websockets import (
    websocket_irrigate_now,
    websocket_run_zone,
)


def _ws_env(coordinator):
    """A hass/connection pair whose async_create_task actually schedules, and a
    shared ``events`` list capturing ack + run order."""
    scheduled = []
    events = []

    def _create_task(coro):
        task = asyncio.ensure_future(coro)
        scheduled.append(task)
        return task

    hass = SimpleNamespace(
        data={const.DOMAIN: {"coordinator": coordinator}},
        async_create_task=_create_task,
    )
    connection = Mock()
    connection.send_result = Mock(
        side_effect=lambda mid, payload: events.append(("ack", payload))
    )
    return hass, connection, events, scheduled


async def test_run_zone_ws_acks_before_running():
    events = []

    async def run(zone_id, duration):
        events.append(("run", zone_id, duration))

    coordinator = SimpleNamespace(async_run_zone=run)
    hass, connection, ev, scheduled = _ws_env(coordinator)
    # single ordered log across ack + run
    connection.send_result = Mock(
        side_effect=lambda mid, payload: events.append(("ack", payload))
    )

    await websocket_run_zone.__wrapped__(
        hass, connection, {"id": 7, "zone_id": 3, "duration": 2.0}
    )

    # ack fires FIRST — the run was scheduled, not awaited inline (the old code
    # awaited the whole cycle, so "run" landed before "ack").
    assert events[0][0] == "ack"
    assert events[0][1]["success"] is True
    assert scheduled, "the run must be handed to a background task"

    await asyncio.gather(*scheduled)
    assert ("run", 3, 2.0) in events


async def test_irrigate_now_ws_acks_before_running():
    events = []

    async def run(zone_id=None):
        events.append(("run", zone_id))

    coordinator = SimpleNamespace(async_irrigate_now=run)
    hass, connection, _ev, scheduled = _ws_env(coordinator)
    connection.send_result = Mock(
        side_effect=lambda mid, payload: events.append(("ack", payload))
    )

    await websocket_irrigate_now.__wrapped__(
        hass, connection, {"id": 9, "zone_id": "2"}
    )

    assert events[0][0] == "ack"
    assert events[0][1]["success"] is True
    assert scheduled

    await asyncio.gather(*scheduled)
    assert ("run", "2") in events


async def test_run_zone_ws_still_reports_bad_input():
    # A malformed duration is a synchronous error and must still ack failure
    # (the fire-and-forget only defers the RUN, not input validation).
    coordinator = SimpleNamespace(async_run_zone=Mock())
    hass, connection, _ev, scheduled = _ws_env(coordinator)
    sent = {}
    connection.send_result = Mock(side_effect=lambda mid, payload: sent.update(payload))

    await websocket_run_zone.__wrapped__(
        hass, connection, {"id": 1, "zone_id": 3, "duration": "not-a-number"}
    )

    assert sent["success"] is False
    assert not scheduled  # nothing scheduled on a bad request
