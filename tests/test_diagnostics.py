"""Test the Smart Irrigation diagnostics."""

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.smart_irrigation.const import (
    CONF_WEATHER_SERVICE_API_KEY,
    DOMAIN,
)
from custom_components.smart_irrigation.diagnostics import (
    async_get_config_entry_diagnostics,
)


class TestSmartIrrigationDiagnostics:
    """Test Smart Irrigation diagnostics."""

    @pytest.fixture
    def mock_hass(self):
        """Return a mock Home Assistant instance."""
        hass = Mock()
        hass.data = {DOMAIN: {}}
        return hass

    @pytest.fixture
    def mock_config_entry(self):
        """Return a mock config entry."""
        return Mock()

    @pytest.fixture
    def mock_store(self):
        """Return a mock store exposing the real (async) store getters.

        The store only has async plural getters (``async_get_mappings`` /
        ``async_get_modules`` / ``async_get_zones``); the previous fixture mocked
        non-existent sync names (``get_mappings`` ...), which let the diagnostics
        bug pass review.
        """
        store = Mock()
        store.async_get_config = AsyncMock(return_value={"test_config": "value"})
        store.async_get_mappings = AsyncMock(return_value={"test_mapping": "value"})
        store.async_get_modules = AsyncMock(return_value={"test_module": "value"})
        store.async_get_zones = AsyncMock(return_value={"test_zone": "value"})
        return store

    @pytest.fixture
    def mock_coordinator(self, mock_store):
        """Return a mock coordinator."""
        coordinator = Mock()
        coordinator.store = mock_store
        return coordinator

    @pytest.fixture
    def real_api_store(self):
        """Return a store mock that exposes ONLY the real (async) store API.

        ``spec`` makes any access to a method that does not exist on the real
        store raise ``AttributeError`` — mirroring production, where
        ``get_mappings``/``get_modules``/``get_zones`` do not exist (the store
        only has ``async_get_*`` plural getters and ``get_*`` singular getters).
        """
        store = Mock(
            spec=[
                "async_get_config",
                "async_get_mappings",
                "async_get_modules",
                "async_get_zones",
            ]
        )
        store.async_get_config = AsyncMock(return_value={"test_config": "value"})
        store.async_get_mappings = AsyncMock(return_value={"test_mapping": "value"})
        store.async_get_modules = AsyncMock(return_value={"test_module": "value"})
        store.async_get_zones = AsyncMock(return_value={"test_zone": "value"})
        return store

    async def test_async_get_config_entry_diagnostics_with_coordinator(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics with coordinator available."""
        mock_hass.data[DOMAIN] = {
            "coordinator": mock_coordinator,
            "zones": {"zone1": "data"},
            "test_data": "value",
        }

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        assert "store" in result
        assert result["store"]["config"] == {"test_config": "value"}
        assert result["store"]["mappings"] == {"test_mapping": "value"}
        assert result["store"]["modules"] == {"test_module": "value"}
        assert result["store"]["zones"] == {"test_zone": "value"}
        assert result["test_data"] == "value"
        assert "coordinator" not in result
        assert "zones" not in result

    async def test_async_get_config_entry_diagnostics_with_api_key_redaction(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics with API key redaction."""
        mock_hass.data[DOMAIN] = {
            "coordinator": mock_coordinator,
            CONF_WEATHER_SERVICE_API_KEY: "secret_api_key",
            "other_data": "value",
        }

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        assert result[CONF_WEATHER_SERVICE_API_KEY] == "[redacted]"
        assert result["other_data"] == "value"

    async def test_async_get_config_entry_diagnostics_no_coordinator(
        self, mock_hass, mock_config_entry, caplog
    ):
        """Test diagnostics without coordinator."""
        mock_hass.data[DOMAIN] = {
            "test_data": "value",
        }

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        assert result["test_data"] == "value"
        assert "Coordinator is not available" in caplog.text

    async def test_async_get_config_entry_diagnostics_no_store(
        self, mock_hass, mock_config_entry, caplog
    ):
        """Test diagnostics with coordinator but no store."""
        mock_coordinator = Mock()
        mock_coordinator.store = None

        mock_hass.data[DOMAIN] = {
            "coordinator": mock_coordinator,
            "test_data": "value",
        }

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        assert result["test_data"] == "value"
        assert "Store is not available" in caplog.text

    async def test_async_get_config_entry_diagnostics_empty_data(
        self, mock_hass, mock_config_entry
    ):
        """Test diagnostics with empty data."""
        mock_hass.data[DOMAIN] = {}

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        assert result == {}

    async def test_async_get_config_entry_diagnostics_does_not_mutate_live_state(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Building diagnostics must NOT mutate the live integration state.

        Regression guard: previously the function popped ``coordinator`` and
        ``zones`` straight out of ``hass.data[DOMAIN]`` (a reference) and never
        wrote them back, so every diagnostics download silently killed the
        running coordinator until the next Home Assistant restart.
        """
        live = {
            "coordinator": mock_coordinator,
            "zones": {"zone1": "data"},
            CONF_WEATHER_SERVICE_API_KEY: "secret_api_key",
            "test_data": "value",
        }
        mock_hass.data[DOMAIN] = live

        await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # The live state object and all of its entries must be untouched.
        assert mock_hass.data[DOMAIN] is live
        assert live["coordinator"] is mock_coordinator
        assert live["zones"] == {"zone1": "data"}
        # The real API key in the live state must not be redacted in place.
        assert live[CONF_WEATHER_SERVICE_API_KEY] == "secret_api_key"

    async def test_async_get_config_entry_diagnostics_uses_real_async_store_api(
        self, mock_hass, mock_config_entry, real_api_store
    ):
        """Diagnostics must use the real async store getters.

        Regression guard: previously it called ``store.get_mappings()`` /
        ``get_modules()`` / ``get_zones()`` which do not exist on the store and
        raised ``AttributeError`` (HTTP 500). ``real_api_store`` is spec'd to the
        real API, so any call to a non-existent method fails the test.
        """
        coordinator = Mock()
        coordinator.store = real_api_store
        mock_hass.data[DOMAIN] = {"coordinator": coordinator}

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        assert result["store"] == {
            "config": {"test_config": "value"},
            "mappings": {"test_mapping": "value"},
            "modules": {"test_module": "value"},
            "zones": {"test_zone": "value"},
        }
        real_api_store.async_get_config.assert_awaited_once()
        real_api_store.async_get_mappings.assert_awaited_once()
        real_api_store.async_get_modules.assert_awaited_once()
        real_api_store.async_get_zones.assert_awaited_once()
