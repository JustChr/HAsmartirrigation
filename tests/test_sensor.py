"""Test Smart Irrigation sensor platform."""

from unittest.mock import AsyncMock, Mock, patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.sensor import (
    SmartIrrigationZoneBucketEntity,
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
            "custom_components.irrigation_plus.sensor.async_dispatcher_connect"
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
        # has_entity_name: the friendly name is composed by HA from the zone
        # device name + the "duration" translation key (no manual name).
        assert entity.has_entity_name is True
        assert entity.translation_key == "duration"
        # unique_id migrated to the per-zone scheme (was the entity_id).
        assert entity.unique_id == f"{const.DOMAIN}_1_duration"

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
        assert info["identifiers"] == {(const.DOMAIN, f"{const.DOMAIN}_zone_1")}
        assert info["name"] == "Test Zone"
        assert info["model"] == "Irrigation zone"
        assert info["manufacturer"] == const.MANUFACTURER
        assert info["via_device"] == (const.DOMAIN, const.DOMAIN)

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


class TestZoneBucketSensorUnit:
    """Issue #72: the bucket sensor labelled a display-unit value as mm.

    `native_value` is the STORED bucket, and stored zone depths are in the
    user's display units (see unit_system.py). Hardcoding "mm" therefore
    published an inch value as millimetres on every imperial install — a factor
    of 25.4 — while every sibling zone sensor already resolved it correctly.
    """

    @staticmethod
    def _entity(hass, bucket=-0.8063):
        return SmartIrrigationZoneBucketEntity(
            hass, "sensor.si_test_bucket", 1, "Front South", bucket
        )

    def test_metric_is_unchanged(self, hass: HomeAssistant) -> None:
        """Metric installs must be byte-identical — they were never wrong."""
        hass.config.units = METRIC_SYSTEM
        assert self._entity(hass).native_unit_of_measurement == "mm"

    def test_imperial_reports_inches(self, hass: HomeAssistant) -> None:
        hass.config.units = US_CUSTOMARY_SYSTEM
        assert self._entity(hass).native_unit_of_measurement == "in"

    def test_the_label_matches_the_value_it_labels(self, hass: HomeAssistant) -> None:
        """The reporter's case: stored -0.8063 in, published as -0.81 mm."""
        hass.config.units = US_CUSTOMARY_SYSTEM
        entity = self._entity(hass)

        assert entity.native_value == -0.81
        assert entity.native_unit_of_measurement != "mm"

    def test_a_unit_flip_republishes_the_state(self, hass: HomeAssistant) -> None:
        """Otherwise the label lags until something else touches the zone."""
        hass.config.units = METRIC_SYSTEM
        entity = self._entity(hass)
        entity.hass = hass
        entity.async_schedule_update_ha_state = Mock()

        entity._async_unit_system_changed()

        entity.async_schedule_update_ha_state.assert_called_once_with(
            force_refresh=True
        )

    def test_the_flip_signal_alone_does_not_refresh_the_value(
        self, hass: HomeAssistant
    ) -> None:
        """Issue #67 follow-up: the label moves, the number does not.

        There is no `async_update` on this class, so `force_refresh=True`
        re-renders the CACHED `_bucket`. That is why the conversion loop has to
        dispatch `_config_updated` as well — this signal is the label half only.
        """
        hass.config.units = METRIC_SYSTEM
        entity = self._entity(hass, bucket=-0.8063)
        entity.hass = hass
        entity.async_schedule_update_ha_state = Mock()

        entity._async_unit_system_changed()

        assert entity._bucket == -0.8063

    def test_the_zone_signal_re_reads_the_converted_value(
        self, hass: HomeAssistant
    ) -> None:
        """`_config_updated` with the zone id is what actually heals it."""
        hass.config.units = METRIC_SYSTEM
        entity = self._entity(hass, bucket=-0.8063)
        entity.hass = hass
        entity.async_schedule_update_ha_state = Mock()
        store = Mock()
        store.get_zone.return_value = {const.ZONE_BUCKET: -20.4800}
        hass.data[const.DOMAIN] = {"coordinator": Mock(store=store)}

        entity._async_update_bucket(1)

        assert entity._bucket == -20.48
