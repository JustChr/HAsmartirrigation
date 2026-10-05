"""Tests for the Irrigation Plus 12-month watering calendar feature."""

import json
import math
import pathlib
from datetime import date
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.irrigation_plus import SmartIrrigationCoordinator
from custom_components.irrigation_plus.const import (
    MODULE_NAME,
    ZONE_ID,
    ZONE_KC,
    ZONE_MAPPING,
    ZONE_MODULE,
    ZONE_MULTIPLIER,
    ZONE_NAME,
    ZONE_SIZE,
    ZONE_STATE,
    ZONE_STATE_AUTOMATIC,
    ZONE_STATE_DISABLED,
    ZONE_THROUGHPUT,
)


@pytest.fixture
def mock_store():
    """Create a mock store instance."""
    # Use regular Mock to avoid coroutine issues with sync methods
    from unittest.mock import Mock

    from custom_components.irrigation_plus.const import (
        CONF_AUTO_CALC_ENABLED,
        CONF_AUTO_UPDATE_ENABLED,
        CONF_USE_WEATHER_SERVICE,
        CONF_WEATHER_SERVICE,
        START_EVENT_FIRED_TODAY,
    )

    store = Mock()

    # Configure synchronous get_config() to return proper dict
    store.get_config.return_value = {
        CONF_USE_WEATHER_SERVICE: False,
        CONF_WEATHER_SERVICE: None,
        CONF_AUTO_UPDATE_ENABLED: False,
        CONF_AUTO_CALC_ENABLED: False,
        START_EVENT_FIRED_TODAY: False,
    }

    # Mock zone data
    test_zone = {
        ZONE_ID: 1,
        ZONE_NAME: "Test Zone",
        ZONE_SIZE: 100.0,  # m²
        ZONE_THROUGHPUT: 10.0,  # l/m
        ZONE_STATE: ZONE_STATE_AUTOMATIC,
        ZONE_MAPPING: 1,
        ZONE_MODULE: 1,
        ZONE_MULTIPLIER: 1.0,
    }

    disabled_zone = {
        ZONE_ID: 2,
        ZONE_NAME: "Disabled Zone",
        ZONE_SIZE: 50.0,
        ZONE_THROUGHPUT: 5.0,
        ZONE_STATE: ZONE_STATE_DISABLED,
        ZONE_MAPPING: 1,
        ZONE_MODULE: 1,
        ZONE_MULTIPLIER: 1.0,
    }

    # Configure async methods separately
    store.async_get_zones = AsyncMock(return_value=[test_zone, disabled_zone])
    store.async_get_config = AsyncMock(
        return_value={
            CONF_USE_WEATHER_SERVICE: False,
            CONF_WEATHER_SERVICE: None,
            CONF_AUTO_UPDATE_ENABLED: False,
            CONF_AUTO_CALC_ENABLED: False,
            START_EVENT_FIRED_TODAY: False,
        }
    )

    store.get_zone.return_value = test_zone

    # Mock module data
    test_module = {
        "id": 1,
        MODULE_NAME: "PyETO",
        "description": "Test PyETO Module",
        "config": {},
    }

    store.get_module.return_value = test_module

    return store


@pytest.fixture
def mock_pyeto_module():
    """Create a mock PyETO module instance."""
    from unittest.mock import Mock

    module = Mock()
    module.name = "PyETO"
    module.calculate_et_for_day = Mock(
        return_value=-2.5
    )  # Negative indicates water deficit
    return module


@pytest.fixture
async def coordinator(hass, mock_store):
    """Create a SmartIrrigationCoordinator instance for testing."""
    from custom_components.irrigation_plus.const import (
        CONF_USE_WEATHER_SERVICE,
        CONF_WEATHER_SERVICE,
        DOMAIN,
    )

    hass.data[DOMAIN] = {
        CONF_USE_WEATHER_SERVICE: False,
        CONF_WEATHER_SERVICE: None,
    }

    entry = Mock()
    entry.unique_id = "test_entry"
    entry.data = {}
    entry.options = {}

    coord = SmartIrrigationCoordinator(hass, None, entry, mock_store)
    coord.store = mock_store

    return coord


class TestWateringCalendar:
    """Test class for watering calendar functionality."""

    @pytest.mark.asyncio
    async def test_generate_monthly_climate_data(self, coordinator):
        """Test generation of monthly climate data."""
        monthly_data = coordinator._generate_monthly_climate_data()

        # Should have 12 months of data
        assert len(monthly_data) == 12

        # Each month should have required fields
        for month_data in monthly_data:
            assert "month" in month_data
            assert "avg_temp" in month_data
            assert "min_temp" in month_data
            assert "max_temp" in month_data
            assert "precipitation" in month_data
            assert "humidity" in month_data
            assert "wind_speed" in month_data
            assert "pressure" in month_data
            assert "dewpoint" in month_data

        # Verify seasonal variation (summer should be warmer than winter)
        summer_temp = monthly_data[6]["avg_temp"]
        winter_temp = monthly_data[0]["avg_temp"]
        assert summer_temp > winter_temp

    @pytest.mark.asyncio
    async def test_calculate_monthly_watering_volume(self, coordinator):
        """Test calculation of monthly watering volume."""
        test_zone = {
            ZONE_SIZE: 100.0,  # 100 m²
            ZONE_MULTIPLIER: 1.0,
            ZONE_MODULE: 1,  # PyETO: the module rain is booked for
        }

        et_mm = 60.0  # 60mm ET for the month
        month_data = {"precipitation": 20.0}  # 20mm precipitation

        volume = coordinator._calculate_monthly_watering_volume(
            test_zone, et_mm, month_data
        )

        # Net water need = 60 - 20 = 40mm
        # 40mm over 100m² = 4000 liters
        expected_volume = 40.0 * 100.0  # mm * m² = liters
        assert volume == expected_volume

    @pytest.mark.asyncio
    async def test_calculate_monthly_watering_volume_no_irrigation_needed(
        self, coordinator
    ):
        """Test that no irrigation is calculated when precipitation exceeds ET."""
        test_zone = {
            ZONE_SIZE: 100.0,
            ZONE_MULTIPLIER: 1.0,
            ZONE_MODULE: 1,  # PyETO: the module rain is booked for
        }

        et_mm = 30.0  # 30mm ET
        month_data = {"precipitation": 50.0}  # 50mm precipitation (exceeds ET)

        volume = coordinator._calculate_monthly_watering_volume(
            test_zone, et_mm, month_data
        )

        # No irrigation needed when precipitation > ET
        assert volume == 0.0

    @pytest.mark.asyncio
    async def test_get_zone_calculation_method(self, coordinator):
        """Test getting zone calculation method description."""
        test_zone = {ZONE_MODULE: 1}

        method = coordinator._get_zone_calculation_method(test_zone)
        assert "PyETO" in method
        assert "FAO-56" in method

    @pytest.mark.asyncio
    async def test_generate_watering_calendar_single_zone(
        self, coordinator, mock_pyeto_module
    ):
        """Test generating watering calendar for a single zone."""
        with patch.object(
            coordinator,
            "getModuleInstanceByID",
            new=AsyncMock(return_value=mock_pyeto_module),
        ):
            calendar_data = await coordinator.async_generate_watering_calendar(
                zone_id=1
            )

        # Should return data for the requested zone
        assert 1 in calendar_data
        zone_data = calendar_data[1]

        assert zone_data["zone_name"] == "Test Zone"
        assert zone_data["zone_id"] == 1
        assert "monthly_estimates" in zone_data
        assert "generated_at" in zone_data
        assert "calculation_method" in zone_data

        # Should have 12 monthly estimates
        monthly_estimates = zone_data["monthly_estimates"]
        assert len(monthly_estimates) == 12

        # Each estimate should have required fields
        for estimate in monthly_estimates:
            assert "month" in estimate
            assert "month_name" in estimate
            assert "estimated_et_mm" in estimate
            assert "estimated_watering_volume_liters" in estimate
            assert "average_temperature_c" in estimate
            assert "average_precipitation_mm" in estimate

    @pytest.mark.asyncio
    async def test_generate_watering_calendar_all_zones(
        self, coordinator, mock_pyeto_module
    ):
        """Test generating watering calendar for all zones."""
        with patch.object(
            coordinator,
            "getModuleInstanceByID",
            new=AsyncMock(return_value=mock_pyeto_module),
        ):
            calendar_data = await coordinator.async_generate_watering_calendar()

        # Should return data for the enabled zone (1) but not disabled zone (2)
        assert 1 in calendar_data
        assert 2 not in calendar_data  # Disabled zones are skipped

    @pytest.mark.asyncio
    async def test_generate_watering_calendar_zone_not_found(
        self, coordinator, mock_pyeto_module
    ):
        """Test graceful handling when zone is not found."""
        with patch.object(
            coordinator,
            "getModuleInstanceByID",
            new=AsyncMock(return_value=mock_pyeto_module),
        ):
            calendar_data = await coordinator.async_generate_watering_calendar(
                zone_id=999
            )

        # Should return empty data for non-existent zone (graceful handling)
        assert isinstance(calendar_data, dict)
        assert 999 not in calendar_data

    @pytest.mark.asyncio
    async def test_generate_watering_calendar_missing_module(self, coordinator):
        """Test handling of zones with missing calculation modules."""
        # Mock store to return a zone without a module
        coordinator.store.get_zone.return_value = {
            ZONE_ID: 1,
            ZONE_NAME: "Test Zone",
            ZONE_STATE: ZONE_STATE_AUTOMATIC,
            ZONE_MAPPING: None,  # Missing mapping
            ZONE_MODULE: None,  # Missing module
        }

        calendar_data = await coordinator.async_generate_watering_calendar(zone_id=1)

        # Should return error data for the zone
        assert 1 in calendar_data
        zone_data = calendar_data[1]
        assert "error" in zone_data
        assert zone_data["monthly_estimates"] == []

    @pytest.mark.asyncio
    async def test_calculate_monthly_et_pyeto(self, coordinator, mock_pyeto_module):
        """Test monthly ET calculation using PyETO."""
        month_data = {
            "avg_temp": 25.0,
            "min_temp": 15.0,
            "max_temp": 35.0,
            "precipitation": 50.0,
            "humidity": 65.0,
            "wind_speed": 3.0,
            "pressure": 1013.25,
            "dewpoint": 18.0,
        }

        # Mock PyETO to return a consistent daily ET deficit
        mock_pyeto_module.calculate_et_for_day = Mock(
            return_value=-2.0
        )  # 2mm deficit per day

        monthly_et = coordinator._calculate_monthly_et_pyeto(
            month_data, mock_pyeto_module, 7
        )  # July

        # Should calculate monthly ET based on daily values
        assert monthly_et > 0

        # Verify the module was called with weather data
        mock_pyeto_module.calculate_et_for_day.assert_called_once()
        # Check that function was called (argument structure may have changed)
        assert mock_pyeto_module.calculate_et_for_day.call_count == 1

    @pytest.mark.asyncio
    async def test_generate_watering_calendar_prices_each_month_at_its_15th(
        self, coordinator, mock_pyeto_module
    ):
        """Each month's equation runs for the 15th of that month, in order."""
        with patch.object(
            coordinator,
            "getModuleInstanceByID",
            new=AsyncMock(return_value=mock_pyeto_module),
        ):
            await coordinator.async_generate_watering_calendar(zone_id=1)

        priced_days = [
            call.kwargs.get("day")
            for call in mock_pyeto_module.calculate_et_for_day.call_args_list
        ]
        assert priced_days == [date(2024, month, 15) for month in range(1, 13)]

    @pytest.mark.asyncio
    async def test_identical_weather_prices_july_above_january(self, hass, coordinator):
        """With the same weather, July's longer days give more ET than January's.

        Both months have 31 days, so any difference comes from the day of year
        the equation is priced at.
        """
        from custom_components.irrigation_plus.calcmodules.pyeto import PyETO

        hass.config.latitude = 32.87336  # northern hemisphere: July has the longer days
        modinst = PyETO(hass, description="", config={})
        month_data = {
            "avg_temp": 20.0,
            "min_temp": 15.0,
            "max_temp": 25.0,
            "precipitation": 50.0,
            "humidity": 65.0,
            "wind_speed": 3.0,
            "pressure": 1013.25,
            "dewpoint": 12.0,
        }

        january = coordinator._calculate_monthly_et_pyeto(month_data, modinst, 1)
        july = coordinator._calculate_monthly_et_pyeto(month_data, modinst, 7)

        assert july > january


_ROOT = pathlib.Path(__file__).parent.parent / "custom_components" / "irrigation_plus"

# A month as the PyETO helper takes it. The helper reads every key, the mocked
# equation ignores the values, so one month serves for any month number.
_MONTH_WEATHER = {
    "avg_temp": 25.0,
    "min_temp": 15.0,
    "max_temp": 35.0,
    "precipitation": 50.0,
    "humidity": 65.0,
    "wind_speed": 3.0,
    "pressure": 1013.25,
    "dewpoint": 18.0,
}


def _module_instance(name, **attrs):
    """A calculation-module instance as the calendar sees it: a name and its call."""
    module = Mock()
    module.name = name
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


class TestAMonthIsPricedByTheCalculationsRules:
    """The calendar prices a month the way the calculation prices its days.

    Only PyETO books rain, Kc scales the ET term and not the rain, and a
    module's daily figure is scaled by the days of the month.
    """

    @pytest.mark.asyncio
    async def test_a_pyeto_month_carries_no_rain(self, coordinator, mock_pyeto_module):
        """The equation returns -ET0 with no rain in it; the month is ET0 x days.

        Adding the month's rain to it showed rain as ET, and subtracting it again
        later left the volume blind to rain.
        """
        mock_pyeto_module.calculate_et_for_day = Mock(return_value=-2.0)

        july = coordinator._calculate_monthly_et_pyeto(
            _MONTH_WEATHER, mock_pyeto_module, 7
        )
        february = coordinator._calculate_monthly_et_pyeto(
            _MONTH_WEATHER, mock_pyeto_module, 2
        )

        assert july == pytest.approx(62.0)  # 2.0 mm x 31 days
        assert february == pytest.approx(58.0)  # 2024, the reference year: 29 days

    @pytest.mark.asyncio
    async def test_a_pyeto_zone_has_the_rain_subtracted_once(
        self, coordinator, mock_pyeto_module
    ):
        """Through the whole calendar: ET without rain, the volume net of it once."""
        mock_pyeto_module.calculate_et_for_day = Mock(return_value=-2.0)

        with patch.object(
            coordinator,
            "getModuleInstanceByID",
            new=AsyncMock(return_value=mock_pyeto_module),
        ):
            calendar_data = await coordinator.async_generate_watering_calendar(
                zone_id=1
            )

        july = calendar_data[1]["monthly_estimates"][6]
        rain = july["average_precipitation_mm"]
        # The scene: some rain, but less than the month's ET, so subtracting it
        # once, twice or not at all gives three different volumes.
        assert 0.0 < rain < 62.0
        assert july["estimated_et_mm"] == pytest.approx(62.0)
        # The fixture zone: 100 m2, multiplier 1, no Kc (reads as 1.0).
        assert july["estimated_watering_volume_liters"] == pytest.approx(
            round(max(0.0, 62.0 - rain) * 100.0, 1)
        )

    @pytest.mark.asyncio
    async def test_kc_scales_the_et_term_and_not_the_rain(self, coordinator):
        """As in the calculation: et_delta = delta x kc, precipitation unscaled."""
        zone = {ZONE_SIZE: 10.0, ZONE_MULTIPLIER: 1.0, ZONE_MODULE: 1, ZONE_KC: 0.5}

        volume = coordinator._calculate_monthly_watering_volume(
            zone, 62.0, {"precipitation": 20.0}
        )

        assert volume == pytest.approx((62.0 * 0.5 - 20.0) * 10.0)  # 110 L

    @pytest.mark.asyncio
    async def test_a_zone_whose_kc_is_none_reads_as_the_default(self, coordinator):
        """A stored ``kc: None`` falls back to 1.0, as in the calculation.

        Only None does: a Kc of 0 is a valid setting and means no ET demand.
        """
        zone = {ZONE_SIZE: 10.0, ZONE_MULTIPLIER: 1.0, ZONE_MODULE: 1, ZONE_KC: None}
        zero = {**zone, ZONE_KC: 0.0}

        volume = coordinator._calculate_monthly_watering_volume(
            zone, 62.0, {"precipitation": 20.0}
        )
        no_demand = coordinator._calculate_monthly_watering_volume(
            zero, 62.0, {"precipitation": 20.0}
        )

        assert volume == pytest.approx((62.0 - 20.0) * 10.0)
        assert no_demand == 0.0

    @pytest.mark.asyncio
    async def test_a_module_without_rain_gets_none_subtracted(
        self, coordinator, mock_store
    ):
        """Static and Passthrough book no rain in the calculation, so here neither.

        Kc still scales their figure, as it scales every module's in the calculation.
        """
        mock_store.get_module.return_value = {"id": 1, MODULE_NAME: "Static"}
        zone = {ZONE_SIZE: 10.0, ZONE_MULTIPLIER: 1.0, ZONE_MODULE: 1, ZONE_KC: 0.8}

        volume = coordinator._calculate_monthly_watering_volume(
            zone, 93.0, {"precipitation": 60.0}
        )

        assert volume == pytest.approx(93.0 * 0.8 * 10.0)  # 744 L

    @pytest.mark.asyncio
    async def test_a_static_demand_becomes_a_monthly_volume(
        self, coordinator, mock_store
    ):
        """The static delta is a daily bucket change, negative for demand.

        Read as a month's ET it was a negative number, and max(0, ...) turned
        every demand into 0 L.
        """
        mock_store.get_module.return_value = {"id": 1, MODULE_NAME: "Static"}
        static = _module_instance("Static", calculate=Mock(return_value=-3.0))

        with patch.object(
            coordinator, "getModuleInstanceByID", new=AsyncMock(return_value=static)
        ):
            calendar_data = await coordinator.async_generate_watering_calendar(
                zone_id=1
            )

        july = calendar_data[1]["monthly_estimates"][6]
        february = calendar_data[1]["monthly_estimates"][1]
        assert july["estimated_et_mm"] == pytest.approx(93.0)  # 3.0 mm x 31 days
        assert february["estimated_et_mm"] == pytest.approx(87.0)  # 2024: 29 days
        # 100 m2, multiplier 1, Kc 1.0, and no rain subtracted for Static.
        assert july["estimated_watering_volume_liters"] == pytest.approx(9300.0)

    @pytest.mark.asyncio
    async def test_a_static_surplus_needs_nothing(self, coordinator, mock_store):
        """A positive static delta adds water every day: no demand, no volume."""
        mock_store.get_module.return_value = {"id": 1, MODULE_NAME: "Static"}
        static = _module_instance("Static", calculate=Mock(return_value=2.0))

        with patch.object(
            coordinator, "getModuleInstanceByID", new=AsyncMock(return_value=static)
        ):
            calendar_data = await coordinator.async_generate_watering_calendar(
                zone_id=1
            )

        july = calendar_data[1]["monthly_estimates"][6]
        assert july["estimated_et_mm"] == 0.0
        assert july["estimated_watering_volume_liters"] == 0.0

    @pytest.mark.asyncio
    async def test_a_passthrough_month_has_its_own_number_of_days(
        self, coordinator, mock_store
    ):
        """February 2024 has 29 days, July 31, and Passthrough books no rain."""
        mock_store.get_module.return_value = {"id": 1, MODULE_NAME: "Passthrough"}
        passthrough = _module_instance("Passthrough")

        with patch.object(
            coordinator,
            "getModuleInstanceByID",
            new=AsyncMock(return_value=passthrough),
        ):
            calendar_data = await coordinator.async_generate_watering_calendar(
                zone_id=1
            )

        climate = coordinator._generate_monthly_climate_data()
        feb_daily = climate[1]["average_daily_et"]
        july_daily = climate[6]["average_daily_et"]
        february = calendar_data[1]["monthly_estimates"][1]
        july = calendar_data[1]["monthly_estimates"][6]
        assert february["estimated_et_mm"] == pytest.approx(round(feb_daily * 29, 2))
        assert july["estimated_et_mm"] == pytest.approx(round(july_daily * 31, 2))
        # 100 m2, multiplier 1, Kc 1.0, and no rain: February's rain is above its
        # ET here, so subtracting it would leave 0 L.
        assert february["estimated_watering_volume_liters"] == pytest.approx(
            round(feb_daily * 29 * 100.0, 1)
        )


class TestTheClimateCurvesDoWhatTheirCommentsSay:
    """The synthetic climate is an illustration, but each curve keeps its word."""

    @pytest.mark.asyncio
    async def test_a_northern_winter_is_wetter_windier_and_more_humid(
        self, coordinator
    ):
        """Temperate north: humidity, wind and rain peak in January, ET in July."""
        coordinator._latitude = 50.0

        rows = coordinator._generate_monthly_climate_data()
        january, july = rows[0], rows[6]

        assert january["humidity"] == pytest.approx(80.0)
        assert july["humidity"] == pytest.approx(50.0)
        assert january["wind_speed"] == pytest.approx(4.0)
        assert july["wind_speed"] == pytest.approx(2.0)
        assert january["precipitation"] == pytest.approx(120.0)
        assert july["precipitation"] == pytest.approx(60.0)
        assert july["average_daily_et"] > january["average_daily_et"]
        assert july["avg_temp"] > january["avg_temp"]

    @pytest.mark.asyncio
    async def test_the_southern_hemisphere_mirrors_every_temperate_curve(
        self, coordinator
    ):
        """At 50° S July is winter for every curve, not just the heat."""
        coordinator._latitude = -50.0

        rows = coordinator._generate_monthly_climate_data()
        january, july = rows[0], rows[6]

        assert july["humidity"] == pytest.approx(80.0)
        assert january["humidity"] == pytest.approx(50.0)
        assert july["wind_speed"] == pytest.approx(4.0)
        assert july["precipitation"] == pytest.approx(120.0)
        assert january["average_daily_et"] > july["average_daily_et"]
        assert january["avg_temp"] > july["avg_temp"]

    @pytest.mark.asyncio
    async def test_tropical_rain_keeps_its_curve(self, coordinator):
        """Its comment names no season, so this curve stays as it was (a pin).

        The same in both hemispheres: it is not one of the curves that mirror.
        """
        expected = [
            round(60.0 * (1.0 + 0.3 * math.sin((m - 1) * math.pi / 6)), 6)
            for m in range(1, 13)
        ]

        for latitude in (10.0, -10.0):
            coordinator._latitude = latitude
            rows = coordinator._generate_monthly_climate_data()

            assert [round(r["precipitation"], 6) for r in rows] == expected, latitude
