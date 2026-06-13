"""Tests for the watering-calendar HTTP API view.

These exercise the real logic of ``SmartIrrigationWateringCalendarView.get``:
resolving the coordinator, parsing/`int`-converting the ``zone_id`` query
param, the success path (coordinator result handed to ``json``) and the error
path (HTTP 500). ``view.json`` is overridden per-instance to capture what the
view emits — independent of HA's real ``HomeAssistantView`` base.

Note: the WebSocket twin (``websocket_get_watering_calendar``) shares the same
coordinator call but is ``@async_response``-decorated; under this test suite's
global ``websocket_api`` mock that decorator yields a Mock, so the WS handler is
not unit-testable here (the HTTP view covers the equivalent logic).
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from custom_components.smart_irrigation.const import DOMAIN
from custom_components.smart_irrigation.websockets import (
    SmartIrrigationWateringCalendarView,
)

CALENDAR_DATA = {
    1: {
        "zone_name": "Test Zone",
        "zone_id": 1,
        "monthly_estimates": [{"month": m} for m in range(1, 13)],
    }
}


def _make_request(coordinator, query):
    """Build a fake aiohttp request wired to a coordinator."""
    hass = SimpleNamespace(data={DOMAIN: {"coordinator": coordinator}})
    request = MagicMock()
    request.app = {"hass": hass}
    request.query = query
    return request


def _make_view(json_return="RESPONSE"):
    """Instantiate the view with json() captured on the instance."""
    view = SmartIrrigationWateringCalendarView()
    view.json = MagicMock(return_value=json_return)
    return view


async def test_get_all_zones_passes_result_to_json():
    """No zone_id -> coordinator called with None, result handed to json()."""
    coordinator = AsyncMock()
    coordinator.async_generate_watering_calendar.return_value = CALENDAR_DATA
    view = _make_view()

    result = await view.get(_make_request(coordinator, {}))

    coordinator.async_generate_watering_calendar.assert_awaited_once_with(None)
    view.json.assert_called_once_with(CALENDAR_DATA)
    assert result == "RESPONSE"


async def test_get_specific_zone_converts_id_to_int():
    """A string zone_id from the query is converted to int for the coordinator."""
    coordinator = AsyncMock()
    coordinator.async_generate_watering_calendar.return_value = CALENDAR_DATA
    view = _make_view()

    await view.get(_make_request(coordinator, {"zone_id": "1"}))

    coordinator.async_generate_watering_calendar.assert_awaited_once_with(1)


async def test_get_coordinator_error_returns_500():
    """A coordinator failure is caught and returned as HTTP 500 with the message."""
    coordinator = AsyncMock()
    coordinator.async_generate_watering_calendar.side_effect = RuntimeError("boom")
    view = _make_view()

    await view.get(_make_request(coordinator, {"zone_id": "999"}))

    view.json.assert_called_once()
    args, kwargs = view.json.call_args
    assert args[0] == {"error": "boom"}
    assert kwargs.get("status_code") == 500


async def test_get_invalid_zone_id_returns_500_without_calling_coordinator():
    """A non-numeric zone_id fails int() before the coordinator is ever called."""
    coordinator = AsyncMock()
    view = _make_view()

    await view.get(_make_request(coordinator, {"zone_id": "not_a_number"}))

    coordinator.async_generate_watering_calendar.assert_not_called()
    view.json.assert_called_once()
    assert view.json.call_args.kwargs.get("status_code") == 500
