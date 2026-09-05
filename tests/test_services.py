"""Test Irrigation Plus services are registered.

Revived in Phase C/A6: updated to the current service layer — registration is
async_register_services (renamed + moved to services.py in C1), and the dead
ServiceCall() constructions (unused objects built with the pre-2024.8 signature)
were removed. These verify the services exist on hass after registration; the
handler wiring itself is covered by tests/test_services_registration.py.
"""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import yaml
from homeassistant.core import HomeAssistant

from custom_components.irrigation_plus import async_register_services, const


class TestSmartIrrigationServices:
    """Test Irrigation Plus service registration."""

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


class TestServicesYamlMatchesReality:
    """`services.yaml` is the contract Home Assistant shows the user.

    A name in that file with no handler behind it is advertised in the service
    picker, autocompletes in an automation, and fails with `ServiceNotFound`
    when it finally runs. Nothing warns about it: hassfest checks that the file
    parses and that the strings are translated, not that anything implements it.

    `set_state` sat there for over a year after upstream's `c3fdbf5` folded it
    into the generalised `set_zone` (which takes `new_state_value`), removed the
    handler and the registration, and left the declaration behind.
    """

    @pytest.fixture
    def declared(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "custom_components"
            / "irrigation_plus"
            / "services.yaml"
        )
        return set(yaml.safe_load(path.read_text(encoding="utf-8")))

    def _registered(self, hass, mock_coordinator):
        hass.data[const.DOMAIN] = {"coordinator": mock_coordinator}
        async_register_services(hass)
        return set(hass.services.async_services().get(const.DOMAIN, {}))

    async def test_every_declared_service_is_registered(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock, declared
    ) -> None:
        missing = declared - self._registered(hass, mock_coordinator)
        assert not missing, (
            f"services.yaml declares {sorted(missing)}, which nothing registers. "
            "Home Assistant will offer them and the call will raise "
            "ServiceNotFound"
        )

    async def test_every_registered_service_is_declared(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock, declared
    ) -> None:
        # The other direction: an undeclared service has no name, no
        # description and no field hints in the UI.
        undeclared = self._registered(hass, mock_coordinator) - declared
        assert not undeclared, (
            f"{sorted(undeclared)} is registered but absent from services.yaml, "
            "so it appears in the UI with no description or fields"
        )

    async def test_set_zone_is_what_replaced_set_state(
        self, hass: HomeAssistant, mock_coordinator: AsyncMock, declared
    ) -> None:
        # Guards the reason set_state was dropped rather than implemented: the
        # capability still exists, on set_zone.
        assert "set_state" not in declared
        assert const.ATTR_NEW_STATE_VALUE in const.LIST_SET_ZONE_ALLOWED_ARGS
        assert hass.services.has_service(
            const.DOMAIN, const.SERVICE_SET_ZONE
        ) or const.SERVICE_SET_ZONE in self._registered(hass, mock_coordinator)


class TestServiceTranslations:
    """Every declared service needs a name/description in all 8 catalogues.

    Removing a service means removing its strings too, or the catalogues keep an
    orphan nobody can reach.
    """

    def test_no_orphan_service_strings(self):
        root = (
            Path(__file__).resolve().parents[1]
            / "custom_components"
            / "irrigation_plus"
        )
        import json

        declared = set(yaml.safe_load((root / "services.yaml").read_text("utf-8")))
        for path in sorted((root / "translations").glob("*.json")):
            translated = set(
                json.loads(path.read_text(encoding="utf-8")).get("services", {})
            )
            assert not translated - declared, (
                f"{path.name} still translates {sorted(translated - declared)}, "
                "which services.yaml no longer declares"
            )
