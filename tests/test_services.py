"""Test Smart Irrigation services are registered.

Revived in Phase C/A6: updated to the current service layer — registration is
async_register_services (renamed + moved to services.py in C1), and the dead
ServiceCall() constructions (unused objects built with the pre-2024.8 signature)
were removed. These verify the services exist on hass after registration; the
handler wiring itself is covered by tests/test_services_registration.py.
"""

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.smart_irrigation import async_register_services, const


class TestSmartIrrigationServices:
    """Test Smart Irrigation service registration."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator (handlers auto-mocked)."""
        return AsyncMock()

    def _register(self, hass, mock_coordinator):
        hass.data[const.DOMAIN] = {"coordinator": mock_coordinator}
        async_register_services(hass)

    async def test_calculate_zone_service(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock
    ) -> None:
        self._register(hass, mock_coordinator)
        assert hass.services.has_service(const.DOMAIN, const.SERVICE_CALCULATE_ZONE)

    async def test_calculate_all_zones_service(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock
    ) -> None:
        self._register(hass, mock_coordinator)
        assert hass.services.has_service(
            const.DOMAIN, const.SERVICE_CALCULATE_ALL_ZONES
        )

    async def test_update_zone_service(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock
    ) -> None:
        self._register(hass, mock_coordinator)
        assert hass.services.has_service(const.DOMAIN, const.SERVICE_UPDATE_ZONE)

    async def test_update_all_zones_service(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock
    ) -> None:
        self._register(hass, mock_coordinator)
        assert hass.services.has_service(const.DOMAIN, const.SERVICE_UPDATE_ALL_ZONES)

    async def test_set_bucket_service(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock
    ) -> None:
        self._register(hass, mock_coordinator)
        assert hass.services.has_service(const.DOMAIN, const.SERVICE_SET_BUCKET)
