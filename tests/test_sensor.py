"""Test Smart Irrigation sensor platform."""

from unittest.mock import AsyncMock, Mock, patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.sensor import (
    SmartIrrigationZoneEntity,
    _to_aware_datetime,
    async_setup_entry,
)


class TestSensorPlatform:
    """Test sensor platform setup."""

    async def test_async_setup_entry(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
    ) -> None:
        """Test sensor platform setup."""
        mock_add_entities = Mock(spec=AddEntitiesCallback)

        # Set up coordinator in hass data
        mock_coordinator = AsyncMock()
        hass.data[const.DOMAIN] = {
            "coordinator": mock_coordinator,
            "zones": {},
        }

        with patch(
            "custom_components.smart_irrigation.sensor.async_dispatcher_connect"
        ) as mock_connect:
            await async_setup_entry(hass, mock_config_entry, mock_add_entities)

            # Verify dispatcher connection was set up
            mock_connect.assert_called()


class TestSmartIrrigationZoneEntity:
    """Test SmartIrrigationZoneEntity.

    Rewritten in A6 for the current constructor (individual args, not a config
    dict) and the current entity behavior (attributes come from constructor args;
    device_info is per-integration; native_value is the duration).
    """

    @staticmethod
    def _make_entity(hass, **overrides):
        args = {
            "hass": hass,
            "id": "1",
            "name": "Test Zone",
            "entity_id": f"{SENSOR_DOMAIN}.{const.DOMAIN}_test_zone",
            "size": 100.0,
            "throughput": 10.0,
            "state": "automatic",
            "duration": 300,
            "bucket": 5.5,
            "last_updated": None,
            "last_calculated": None,
            "number_of_data_points": 3,
            "delta": 2.3,
            "drainage_rate": 0.0,
            "current_drainage": 0.0,
            "multiplier": 1.0,
            "lead_time": 0,
            "maximum_duration": 3600,
            "maximum_bucket": 10.0,
        }
        args.update(overrides)
        return SmartIrrigationZoneEntity(**args)

    def test_entity_creation(self, hass: HomeAssistant) -> None:
        """Construction sets identity from the constructor args."""
        entity = self._make_entity(hass)
        assert entity.entity_id == f"{SENSOR_DOMAIN}.{const.DOMAIN}_test_zone"
        assert entity.name == "Test Zone"
        assert entity.unique_id == entity.entity_id

    def test_basic_properties(self, hass: HomeAssistant) -> None:
        """should_poll/native_value/device_class reflect the duration sensor."""
        entity = self._make_entity(hass, duration=420)
        assert entity.should_poll is False
        assert entity.native_value == 420
        assert entity.device_class == SensorDeviceClass.DURATION

    def test_extra_state_attributes(self, hass: HomeAssistant) -> None:
        """Attributes reflect the constructor args."""
        entity = self._make_entity(
            hass,
            bucket=7.2,
            size=150.0,
            throughput=12.0,
            multiplier=1.5,
            lead_time=30,
            maximum_duration=1800,
        )
        attrs = entity.extra_state_attributes
        assert attrs["bucket"] == 7.2
        assert attrs["size"] == 150.0
        assert attrs["throughput"] == 12.0
        assert attrs["multiplier"] == 1.5
        assert attrs["lead_time"] == 30
        assert attrs["maximum_duration"] == 1800
        assert attrs["state"] == "automatic"

    def test_device_info(self, hass: HomeAssistant) -> None:
        """device_info is a per-zone device hanging off the hub via via_device."""
        info = self._make_entity(hass).device_info
        assert info["identifiers"] == {(const.DOMAIN, "smart_irrigation_zone_1")}
        assert info["name"] == f"{const.NAME}: Test Zone"
        assert info["model"] == "Irrigation zone"
        assert info["manufacturer"] == const.MANUFACTURER
        assert info["via_device"] == (const.DOMAIN, "smart_irrigation")

    def test_to_aware_datetime(self) -> None:
        """Naive stored timestamps become local-aware; garbage becomes None."""
        import datetime

        import homeassistant.util.dt as dt_util

        naive = _to_aware_datetime("2026-06-10 21:00:00")
        assert naive is not None
        assert naive.tzinfo == dt_util.DEFAULT_TIME_ZONE

        aware_src = datetime.datetime(2026, 6, 10, 19, tzinfo=datetime.timezone.utc)
        assert _to_aware_datetime(aware_src.isoformat()) == aware_src
        assert _to_aware_datetime(aware_src) == aware_src

        assert _to_aware_datetime(None) is None
        assert _to_aware_datetime("not-a-date") is None
        assert _to_aware_datetime(42) is None

    def test_async_handle_unit_system_change(self, hass: HomeAssistant) -> None:
        """The unit-system-change handler schedules a forced state refresh."""
        entity = self._make_entity(hass)
        entity.async_schedule_update_ha_state = Mock()

        entity.async_handle_unit_system_change()

        entity.async_schedule_update_ha_state.assert_called_once_with(
            force_refresh=True
        )
