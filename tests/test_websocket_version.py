"""Tests for the version field in the config websocket payload.

Task V-BE (b9 plan): the panel must be able to read the installed backend
version at runtime from the config websocket payload, so the displayed version
never drifts from the built frontend bundle. This exercises
``websocket_get_config`` and asserts the sent payload carries
``const.VERSION``.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.websockets import websocket_get_config


async def test_get_config_payload_includes_version():
    """websocket_get_config must send const.VERSION in the config payload."""
    # Stored config as returned by the coordinator's store. Metric path (no
    # precipitation-threshold conversion needed) keeps the mock minimal.
    stored_config = {"foo": "bar"}
    store = Mock()
    store.async_get_config = AsyncMock(return_value=stored_config)
    coordinator = SimpleNamespace(store=store)

    # Metric units so the handler takes the non-converting branch.
    from homeassistant.util.unit_system import METRIC_SYSTEM

    hass = SimpleNamespace(
        data={const.DOMAIN: {"coordinator": coordinator}},
        config=SimpleNamespace(units=METRIC_SYSTEM),
    )

    sent = {}

    def _send_result(msg_id, payload):
        sent["id"] = msg_id
        sent["payload"] = payload

    connection = Mock()
    connection.send_result = Mock(side_effect=_send_result)

    msg = {"id": 42}

    # async_response wraps the handler with @wraps(func); the original coroutine
    # is reachable via __wrapped__ and can be awaited directly in isolation.
    await websocket_get_config.__wrapped__(hass, connection, msg)

    assert sent["id"] == 42
    assert sent["payload"]["version"] == const.VERSION

    # The persisted store dict must not be mutated by the handler.
    assert "version" not in stored_config
