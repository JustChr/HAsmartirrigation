"""The "reset all weather data" action must leave nothing behind.

Emptying the buffers is only half of it. Each zone carries state *derived* from
those buffers — its watermark (``last_consumed_at``) and its data-point count —
and both have to be reset with them.

The watermark already was: a zone left pointing at a window that no longer exists
would try to consume it. The count was not, so the zone's "Weather data points"
diagnostic sensor kept reporting the pre-reset number until some later poll or
calculation happened to overwrite it. Cosmetic, but it reads as "the reset did
nothing" — the one thing a reset action must never look like.

Resetting the stored value is only half of THAT, in turn: the zone sensors keep
their values in memory and re-read the store only when ``_config_updated`` fires
for their zone. This path never dispatched it, so a live instance kept showing the
old count even once the store said 0 — caught by running the service against a
real config, not by asserting the store write.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


def _coordinator(mappings, zones):
    coordinator = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coordinator.hass = Mock()
    store = Mock()
    store.async_get_mappings = AsyncMock(return_value=mappings)
    store.async_get_zones = AsyncMock(return_value=zones)
    store.async_update_mapping = AsyncMock()
    store.async_update_zone = AsyncMock()
    coordinator.store = store
    return coordinator, store


class TestClearAllWeatherData:
    async def test_buffers_emptied_and_zone_state_reset(self):
        coordinator, store = _coordinator(
            mappings=[{const.MAPPING_ID: 0}, {const.MAPPING_ID: 1}],
            zones=[
                {const.ZONE_ID: 0, const.ZONE_NUMBER_OF_DATA_POINTS: 42},
                {const.ZONE_ID: 1, const.ZONE_NUMBER_OF_DATA_POINTS: 7},
            ],
        )

        with patch(
            "custom_components.smart_irrigation.calculation.async_dispatcher_send"
        ):
            await coordinator._async_clear_all_weatherdata()

        # Every sensor group's buffer is emptied.
        assert store.async_update_mapping.await_count == 2
        for call in store.async_update_mapping.await_args_list:
            _mapping_id, changes = call.args
            assert changes[const.MAPPING_DATA] == []

        # Every zone is re-anchored AND its derived count cleared.
        assert store.async_update_zone.await_count == 2
        seen = set()
        for call in store.async_update_zone.await_args_list:
            zone_id, changes = call.args
            seen.add(zone_id)
            assert isinstance(changes[const.ZONE_LAST_CONSUMED], datetime)
            assert changes[const.ZONE_NUMBER_OF_DATA_POINTS] == 0
        assert seen == {0, 1}

    async def test_each_zone_is_told_to_refresh(self):
        """The store write alone leaves the entity showing the old count.

        Zone sensors cache their values and re-read only on ``_config_updated``
        for their own zone id, so a reset that skips the signal is invisible in
        the UI until something unrelated updates or HA restarts.
        """
        coordinator, _store = _coordinator(
            mappings=[{const.MAPPING_ID: 0}],
            zones=[{const.ZONE_ID: 0}, {const.ZONE_ID: 1}],
        )

        with patch(
            "custom_components.smart_irrigation.calculation.async_dispatcher_send"
        ) as dispatch:
            await coordinator._async_clear_all_weatherdata()

        signalled = {
            call.args[2]
            for call in dispatch.call_args_list
            if call.args[1] == const.DOMAIN + "_config_updated"
        }
        assert signalled == {0, 1}
        # …and the panel is told too, like every other writer of zone state.
        assert any(
            call.args[1] == const.DOMAIN + "_update_frontend"
            for call in dispatch.call_args_list
        )

    async def test_no_zones_is_not_an_error(self):
        coordinator, store = _coordinator(mappings=[{const.MAPPING_ID: 0}], zones=[])

        with patch(
            "custom_components.smart_irrigation.calculation.async_dispatcher_send"
        ):
            await coordinator._async_clear_all_weatherdata()

        assert store.async_update_mapping.await_count == 1
        store.async_update_zone.assert_not_called()
