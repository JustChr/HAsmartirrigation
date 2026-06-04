"""Regression test for UX review finding C1.

The setup wizard links a freshly-created module/mapping to the new zone using
the id returned by the create POST. Previously the coordinator's create
branches returned ``None`` and the HTTP views returned only
``{"success": True}``, so the wizard built a zone with ``module=None`` /
``mapping=None`` that could never calculate. These tests pin the contract that
creating a module/mapping returns the stored entry (including its id).
"""

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


@pytest.fixture
def coordinator(hass, mock_store):
    """Build a real coordinator wired to the mock store."""
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }

    entry = Mock()
    entry.unique_id = "test_entry"
    entry.data = {}
    entry.options = {}

    coord = SmartIrrigationCoordinator(hass, None, entry, mock_store)
    coord.store = mock_store
    # update_subscriptions touches HA internals not needed for this contract.
    coord.update_subscriptions = AsyncMock()
    return coord


class TestCreateReturnsId:
    """Create paths must surface the new entry's id (UX review C1)."""

    @pytest.mark.asyncio
    async def test_create_mapping_returns_entry_with_id(self, coordinator, mock_store):
        mock_store.get_mapping = Mock(return_value=None)
        mock_store.async_create_mapping = AsyncMock(
            return_value={"id": 7, "name": "Sensors"}
        )
        mock_store.async_get_config = AsyncMock(return_value={})

        result = await coordinator.async_update_mapping_config(
            None, {"name": "Sensors", "mappings": {}}
        )

        assert isinstance(result, dict)
        assert result.get(const.MAPPING_ID) == 7

    @pytest.mark.asyncio
    async def test_create_module_returns_entry_with_id(self, coordinator, mock_store):
        mock_store.get_module = Mock(return_value=None)
        mock_store.async_create_module = AsyncMock(
            return_value={"id": 3, "name": "PyETO"}
        )
        mock_store.async_get_config = AsyncMock(return_value={})

        result = await coordinator.async_update_module_config(None, {"name": "PyETO"})

        assert isinstance(result, dict)
        assert result.get(const.MODULE_ID) == 3
