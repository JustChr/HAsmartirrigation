"""Unit tests for the coordinator service handlers (ServiceHandlersMixin).

These call the real handler methods (bound to a controlled mock ``self``) and
assert the behaviour that matters: the entity -> zone_id resolution, the payload
built for ``async_update_zone_config``, and the guard branches. The mixin's
collaborators (``async_update_zone_config`` / ``_async_set_all_buckets``) are the
unit boundary and are mocked; their own behaviour is covered elsewhere.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.services import ServiceHandlersMixin


def _make_coordinator():
    """Build a mock standing in for the coordinator the mixin runs on."""
    coord = MagicMock()
    coord.async_update_zone_config = AsyncMock()
    coord._async_set_all_buckets = AsyncMock()
    return coord


async def test_handle_reset_bucket_sets_bucket_to_zero():
    """A reset for a known zone resolves the zone_id and sets the bucket to 0."""
    coord = _make_coordinator()
    state = MagicMock()
    state.attributes = {const.ZONE_ID: 3}
    coord.hass.states.get.return_value = state

    call = MagicMock()
    call.data = {const.SERVICE_ENTITY_ID: "sensor.smart_irrigation_test_zone"}

    await ServiceHandlersMixin.handle_reset_bucket(coord, call)

    coord.async_update_zone_config.assert_awaited_once()
    kwargs = coord.async_update_zone_config.await_args.kwargs
    assert kwargs["zone_id"] == 3
    assert const.ATTR_SET_BUCKET in kwargs["data"]
    assert kwargs["data"][const.ATTR_NEW_BUCKET_VALUE] == 0


async def test_handle_reset_bucket_accepts_entity_id_list():
    """A list of entity_ids resets every resolvable zone."""
    coord = _make_coordinator()
    states = {
        "sensor.zone_a": MagicMock(attributes={const.ZONE_ID: 1}),
        "sensor.zone_b": MagicMock(attributes={const.ZONE_ID: 2}),
    }
    coord.hass.states.get.side_effect = states.get

    call = MagicMock()
    call.data = {const.SERVICE_ENTITY_ID: ["sensor.zone_a", "sensor.zone_b"]}

    await ServiceHandlersMixin.handle_reset_bucket(coord, call)

    assert coord.async_update_zone_config.await_count == 2
    reset_zone_ids = {
        c.kwargs["zone_id"] for c in coord.async_update_zone_config.await_args_list
    }
    assert reset_zone_ids == {1, 2}


async def test_handle_reset_bucket_no_entity_id_is_noop():
    """Without an entity_id the handler must not touch any zone."""
    coord = _make_coordinator()
    call = MagicMock()
    call.data = {}

    await ServiceHandlersMixin.handle_reset_bucket(coord, call)

    coord.async_update_zone_config.assert_not_awaited()


async def test_handle_reset_bucket_unknown_entity_is_noop():
    """An entity_id with no matching HA state resolves to nothing."""
    coord = _make_coordinator()
    coord.hass.states.get.return_value = None
    call = MagicMock()
    call.data = {const.SERVICE_ENTITY_ID: "sensor.does_not_exist"}

    await ServiceHandlersMixin.handle_reset_bucket(coord, call)

    coord.async_update_zone_config.assert_not_awaited()


async def test_handle_run_zone_resolves_id_attribute():
    """run_zone resolves the zone from a sensor's "id" attribute (issue #36)."""
    coord = _make_coordinator()
    coord.async_run_zone = AsyncMock()
    state = MagicMock()
    state.attributes = {const.ZONE_ID: 7}
    coord.hass.states.get.return_value = state

    call = MagicMock()
    call.data = {
        const.SERVICE_ENTITY_ID: "sensor.smart_irrigation_lawn",
        const.ATTR_DURATION_MINUTES: 5,
    }

    await ServiceHandlersMixin.handle_run_zone(coord, call)

    coord.async_run_zone.assert_awaited_once_with(7, 5.0)


async def test_handle_run_zone_resolves_zone_id_attribute():
    """A button / binary_sensor exposes the id as "zone_id" — also accepted."""
    coord = _make_coordinator()
    coord.async_run_zone = AsyncMock()
    state = MagicMock()
    state.attributes = {"zone_id": 4, "zone_name": "Lawn"}
    coord.hass.states.get.return_value = state

    call = MagicMock()
    call.data = {
        const.SERVICE_ENTITY_ID: "button.smart_irrigation_lawn_irrigate_now",
        const.ATTR_DURATION_MINUTES: 10,
    }

    await ServiceHandlersMixin.handle_run_zone(coord, call)

    coord.async_run_zone.assert_awaited_once_with(4, 10.0)


async def test_handle_run_zone_non_zone_entity_raises():
    """An entity with neither id nor zone_id is rejected, not silently run."""
    from custom_components.smart_irrigation.services import SmartIrrigationError

    coord = _make_coordinator()
    coord.async_run_zone = AsyncMock()
    state = MagicMock()
    state.attributes = {"some_other_attr": 1}
    coord.hass.states.get.return_value = state

    call = MagicMock()
    call.data = {
        const.SERVICE_ENTITY_ID: "sensor.unrelated",
        const.ATTR_DURATION_MINUTES: 5,
    }

    with pytest.raises(SmartIrrigationError):
        await ServiceHandlersMixin.handle_run_zone(coord, call)
    coord.async_run_zone.assert_not_awaited()


async def test_handle_reset_all_buckets_zeroes_everything():
    """Reset-all delegates to _async_set_all_buckets(0)."""
    coord = _make_coordinator()

    await ServiceHandlersMixin.handle_reset_all_buckets(coord, MagicMock())

    coord._async_set_all_buckets.assert_awaited_once_with(0)


async def test_handle_set_all_buckets_uses_provided_value():
    """Set-all passes the requested value through."""
    coord = _make_coordinator()
    call = MagicMock()
    call.data = {const.ATTR_NEW_BUCKET_VALUE: -12.5}

    await ServiceHandlersMixin.handle_set_all_buckets(coord, call)

    coord._async_set_all_buckets.assert_awaited_once_with(-12.5)


async def test_handle_set_all_buckets_without_value_is_noop():
    """Set-all with no value is a no-op (no accidental reset)."""
    coord = _make_coordinator()
    call = MagicMock()
    call.data = {}

    await ServiceHandlersMixin.handle_set_all_buckets(coord, call)

    coord._async_set_all_buckets.assert_not_awaited()
