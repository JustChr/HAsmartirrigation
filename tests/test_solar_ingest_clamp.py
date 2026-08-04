"""Plausibility ceiling on ingested solar radiation.

Once ET is summed hour by hour it tracks the pyranometer directly: the residual
against a model reference correlates with the site-vs-model solar ratio at
r = 0.746 for the hourly form against 0.220 for the daily one. The pyranometer on
this install misbehaves -- 4 of 423 recorded days show a clearness index above
0.85, one of them stuck at a constant 722 W/m2 for 19 hours including the whole
night (an impossible 10.8 mm/day of ETo), and peak instantaneous readings reach
1488 W/m2.

Clamped to clear sky rather than rejected: rejecting leaves the carry-forward
holding the last accepted value, which for a sensor stuck at a daytime level is
exactly the 19-hour case. And reported at WARNING every hour it keeps firing,
because a clamp that hides a broken sensor is how a solar aggregation bug stayed
invisible for months.
"""

import datetime
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import (
    SOLAR_CLAMP_WARN_INTERVAL,
    SmartIrrigationCoordinator,
    const,
)
from custom_components.smart_irrigation.helpers import clamp_solar_to_clear_sky
from custom_components.smart_irrigation.store import SmartIrrigationStorage

LAT, LON, ELEV, TZ = 39.68987, -84.07865, 311.0, -4.0
# The buffer stores MJ/day/m2; readings are quoted in W/m2 throughout.
F = const.W_TO_MJ_DAY_FACTOR

SUMMER_NOON = datetime.datetime(2026, 6, 21, 13, 30)
SUMMER_NIGHT = datetime.datetime(2026, 6, 21, 2, 0)


def _clamp(w_m2, when):
    """Clamp a W/m2 reading and hand the answer back in W/m2."""
    return clamp_solar_to_clear_sky(w_m2 * F, when, LAT, LON, ELEV, TZ) / F


class TestCeiling:
    def test_a_plausible_summer_noon_reading_passes(self):
        """Clear-sky noon here is ~950 W/m2 and broken cloud can lift it further."""
        assert _clamp(900.0, SUMMER_NOON) == pytest.approx(900.0)
        assert _clamp(1100.0, SUMMER_NOON) == pytest.approx(1100.0)

    def test_the_records_peak_reading_is_clamped(self):
        assert _clamp(1488.0, SUMMER_NOON) < 1300.0

    def test_a_stuck_daytime_value_is_killed_at_night_and_kept_by_day(self):
        """The 19-hour case. At night clear sky is 0, so the floor is all that is left."""
        night = _clamp(722.0, SUMMER_NIGHT)
        assert night == pytest.approx(const.SOLAR_PLAUSIBILITY_FLOOR_W_M2)
        # The same value in the middle of the day is entirely plausible, and the
        # clamp is not in the business of guessing which day was stuck.
        assert _clamp(722.0, SUMMER_NOON) == pytest.approx(722.0)

    def test_deadband_noise_at_night_is_not_clamped(self):
        """Clear sky is exactly 0 at night; without the floor every row would clamp."""
        assert _clamp(6.0, SUMMER_NIGHT) == pytest.approx(6.0)

    def test_the_sunrise_ramp_is_not_over_tight(self):
        """A reading minutes after sunrise must not be judged against a dark hour."""
        just_after_sunrise = datetime.datetime(2026, 6, 21, 6, 30)
        assert _clamp(40.0, just_after_sunrise) == pytest.approx(40.0)

    def test_no_coordinates_means_no_clamp(self):
        value = 5000.0 * F
        assert (
            clamp_solar_to_clear_sky(value, SUMMER_NIGHT, None, LON, ELEV, TZ) == value
        )

    def test_none_passes_through(self):
        assert clamp_solar_to_clear_sky(None, SUMMER_NOON, LAT, LON, ELEV, TZ) is None


@pytest.fixture
async def coordinator(hass):
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    c._effective_latitude = LAT
    c._effective_longitude = LON
    c._effective_elevation = ELEV
    return c


def _sensor_mapping(unit, sensor_id="sensor.pyranometer"):
    """A sensor group whose Solar Radiation comes from an HA entity."""
    return {
        const.MAPPING_MAPPINGS: {
            const.MAPPING_SOLRAD: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                const.MAPPING_CONF_SENSOR: sensor_id,
                const.MAPPING_CONF_UNIT: unit,
            }
        }
    }


class TestBothIngestionPaths:
    """Both writers of the field have to agree, or the buffer aggregates a mix."""

    def test_the_polled_reading_is_clamped(self, coordinator, hass):
        hass.states.async_set(
            "sensor.pyranometer", "5000.0", {"unit_of_measurement": "W/m²"}
        )
        values = coordinator.build_sensor_values_for_mapping(
            _sensor_mapping(const.UNIT_W_M2)
        )
        assert values[const.MAPPING_SOLRAD] < 5000.0 * F

    def test_the_event_driven_reading_is_clamped_too(self, coordinator):
        """The continuous-update path writes the same field, one event at a time.

        Asserted with a value no clear sky can produce at any hour, because this
        entry point clamps against the real clock: what counts as plausible
        depends on the time of day, so a mid-range reading would pass or clamp
        depending on when the suite runs.
        """
        value = coordinator._continuous_metric_value(
            5000.0, const.MAPPING_SOLRAD, {}, "W/m²", "sensor.pyranometer", True
        )
        assert value < 5000.0 * F

    def test_a_non_solar_field_is_not_touched_by_the_clamp(self, coordinator):
        """Only Solar Radiation routes through the ceiling."""
        assert coordinator._continuous_metric_value(
            25.0, const.MAPPING_TEMPERATURE, {}, "°C", "sensor.temp", True
        ) == pytest.approx(25.0)

    def test_a_plausible_reading_passes_through_untouched(self, coordinator):
        """Same path, with the clock pinned so the ceiling is deterministic."""
        assert coordinator._clamp_solar_reading(
            300.0 * F, now=SUMMER_NOON
        ) == pytest.approx(300.0 * F)


@freeze_time("2026-06-21 02:00:00")
class TestOnlyRatesAreCeilinged:
    """The ceiling is an hourly clear-sky reference, so only a rate can meet it.

    Every case here is asserted in the middle of the night, which is where a
    ceiling applied to something that is not an instantaneous rate does its
    damage: clear sky is 0 then, so the reading lands on the plausibility floor.
    """

    def test_a_daily_total_sensor_survives_the_night_on_the_poll_path(
        self, coordinator, hass
    ):
        """MJ/day/m2 is a selectable unit and passes through conversion unchanged.

        A daily total reads the same at 02:00 as at noon. Floored every dark
        hour, a 20 MJ/day/m2 total loses 36% of the day's radiation on 21 June
        and 72% on 21 December, which under-waters every zone in the group.
        """
        # No unit on the entity, so the sensor group's own MJ/day/m2 is what the
        # value is converted from -- the ordinary shape for this configuration,
        # since HA has no unit class for a daily radiation total.
        hass.states.async_set("sensor.daily_total", "20.0", {})
        values = coordinator.build_sensor_values_for_mapping(
            _sensor_mapping(const.UNIT_MJ_DAY_M2, "sensor.daily_total")
        )
        assert values[const.MAPPING_SOLRAD] == pytest.approx(20.0)

    def test_a_daily_total_sensor_survives_the_night_on_the_event_path(
        self, coordinator
    ):
        value = coordinator._continuous_metric_value(
            20.0,
            const.MAPPING_SOLRAD,
            {const.MAPPING_CONF_UNIT: const.UNIT_MJ_DAY_M2},
            None,
            "sensor.daily_total",
            True,
        )
        assert value == pytest.approx(20.0)

    def test_a_rate_sensor_is_still_clamped_at_night_on_both_paths(
        self, coordinator, hass
    ):
        """The stuck-pyranometer case the ceiling exists for is unaffected."""
        hass.states.async_set(
            "sensor.pyranometer", "722.0", {"unit_of_measurement": "W/m²"}
        )
        polled = coordinator.build_sensor_values_for_mapping(
            _sensor_mapping(const.UNIT_W_M2)
        )
        assert polled[const.MAPPING_SOLRAD] == pytest.approx(
            const.SOLAR_PLAUSIBILITY_FLOOR_W_M2 * F
        )
        event = coordinator._continuous_metric_value(
            722.0,
            const.MAPPING_SOLRAD,
            {const.MAPPING_CONF_UNIT: const.UNIT_W_M2},
            "W/m²",
            "sensor.pyranometer",
            True,
        )
        assert event == pytest.approx(const.SOLAR_PLAUSIBILITY_FLOOR_W_M2 * F)

    def test_the_entitys_own_unit_decides_not_the_configured_one(
        self, coordinator, hass
    ):
        """resolve_sensor_unit prefers the entity's unit, so the ceiling must too.

        A sensor mis-configured as MJ/day/m2 that actually reports W/m2 is a
        rate, and a guard reading the sensor-group config alone would exempt it.
        """
        hass.states.async_set(
            "sensor.pyranometer", "722.0", {"unit_of_measurement": "W/m²"}
        )
        polled = coordinator.build_sensor_values_for_mapping(
            _sensor_mapping(const.UNIT_MJ_DAY_M2)
        )
        assert polled[const.MAPPING_SOLRAD] == pytest.approx(
            const.SOLAR_PLAUSIBILITY_FLOOR_W_M2 * F
        )
        event = coordinator._continuous_metric_value(
            722.0,
            const.MAPPING_SOLRAD,
            {const.MAPPING_CONF_UNIT: const.UNIT_MJ_DAY_M2},
            "W/m²",
            "sensor.pyranometer",
            True,
        )
        assert event == pytest.approx(const.SOLAR_PLAUSIBILITY_FLOOR_W_M2 * F)

    def test_a_static_value_is_never_ceilinged(self, coordinator):
        """A static radiation value is the same at 02:00 as at noon by definition.

        It never passes through either conversion site, so its exemption is
        structural rather than a check that has to be kept in step.
        """
        static = coordinator.build_static_values_for_mapping(
            {
                const.MAPPING_MAPPINGS: {
                    const.MAPPING_SOLRAD: {
                        const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_STATIC_VALUE,
                        const.MAPPING_CONF_STATIC_VALUE: 300.0 * F,
                        const.MAPPING_CONF_UNIT: const.UNIT_W_M2,
                    }
                }
            }
        )
        assert static[const.MAPPING_SOLRAD] == pytest.approx(300.0 * F)

    async def test_weather_service_radiation_in_a_mixed_group_is_untouched(
        self, coordinator, hass
    ):
        """A modelled value cannot exceed clear sky, and is not ours to second-guess.

        The group is mixed, which is what used to leak: the clamp hung off
        "does this group have any sensor", not "did this field come from one".
        """
        hass.states.async_set("sensor.temp", "25.0", {"unit_of_measurement": "°C"})
        mapping = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_SOLRAD: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE,
                },
                const.MAPPING_TEMPERATURE: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.temp",
                    const.MAPPING_CONF_UNIT: "°C",
                },
            }
        }
        weatherdata = {const.MAPPING_SOLRAD: 900.0 * F}
        merged = await coordinator.merge_weatherdata_and_sensor_values(
            weatherdata, coordinator.build_sensor_values_for_mapping(mapping)
        )
        assert merged[const.MAPPING_SOLRAD] == pytest.approx(900.0 * F)


@freeze_time("2026-06-21 02:00:00")
class TestTheRowThePollAppends:
    """The whole poll pipeline, because that is the level the ceiling used to sit at.

    It hung off "does this sensor group contain any sensor or static field",
    which is per GROUP and not per FIELD, so it reached three kinds of reading it
    has no reference for. Asserting on the merged row that reaches the buffer is
    what pins each of them.
    """

    def _poll_coord(self, hass, mapping, *, owm=False, static=False, weatherdata=None):
        coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
        coord.hass = hass
        coord.store = Mock()
        coord.store.config = SimpleNamespace(continuousupdates=False)
        coord.store.async_get_zones = AsyncMock(
            return_value=[
                {const.ZONE_ID: 1, const.ZONE_MAPPING: 1, const.ZONE_STATE: "automatic"}
            ]
        )
        coord.store.get_mapping = Mock(return_value=mapping)
        coord.store.async_update_mapping = AsyncMock()
        coord.store.async_update_zone = AsyncMock()
        coord.store.append_mapping_reading = Mock(return_value=True)
        coord.store.get_mapping_row_count = Mock(return_value=0)
        coord.check_mapping_sources = Mock(return_value=(owm, True, static))
        coord._get_zones_that_use_this_mapping = AsyncMock(return_value=[1])
        coord.async_refresh_zone_estimates = AsyncMock()
        coord.use_weather_service = owm
        coord._WeatherServiceClient = Mock(get_data=Mock(return_value=weatherdata))
        coord._effective_latitude = LAT
        coord._effective_longitude = LON
        coord._effective_elevation = ELEV
        return coord

    async def _appended_row(self, coord):
        await coord._async_update_all()
        coord.store.append_mapping_reading.assert_called_once()
        return coord.store.append_mapping_reading.call_args[0][1]

    async def test_a_daily_total_reaches_the_buffer_whole(self, hass):
        hass.states.async_set("sensor.daily_total", "20.0", {})
        row = await self._appended_row(
            self._poll_coord(
                hass, _sensor_mapping(const.UNIT_MJ_DAY_M2, "sensor.daily_total")
            )
        )
        assert row[const.MAPPING_SOLRAD] == pytest.approx(20.0)

    async def test_a_static_value_reaches_the_buffer_whole(self, hass):
        mapping = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_SOLRAD: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_STATIC_VALUE,
                    const.MAPPING_CONF_STATIC_VALUE: 300.0 * F,
                    const.MAPPING_CONF_UNIT: const.UNIT_W_M2,
                }
            }
        }
        row = await self._appended_row(self._poll_coord(hass, mapping, static=True))
        assert row[const.MAPPING_SOLRAD] == pytest.approx(300.0 * F)

    async def test_weather_service_radiation_survives_a_mixed_group(self, hass):
        hass.states.async_set("sensor.temp", "25.0", {"unit_of_measurement": "°C"})
        mapping = {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_SOLRAD: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE,
                },
                const.MAPPING_TEMPERATURE: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.temp",
                    const.MAPPING_CONF_UNIT: "°C",
                },
            }
        }
        row = await self._appended_row(
            self._poll_coord(
                hass,
                mapping,
                owm=True,
                weatherdata={const.MAPPING_SOLRAD: 900.0 * F},
            )
        )
        assert row[const.MAPPING_SOLRAD] == pytest.approx(900.0 * F)

    async def test_a_stuck_rate_sensor_is_still_floored_in_the_buffer(self, hass):
        hass.states.async_set(
            "sensor.pyranometer", "722.0", {"unit_of_measurement": "W/m²"}
        )
        row = await self._appended_row(
            self._poll_coord(hass, _sensor_mapping(const.UNIT_W_M2))
        )
        assert row[const.MAPPING_SOLRAD] == pytest.approx(
            const.SOLAR_PLAUSIBILITY_FLOOR_W_M2 * F
        )


class TestWarning:
    """A clamp that hides a broken sensor is worse than no clamp."""

    def test_it_warns_and_keeps_warning_hourly(self, coordinator, caplog):
        impossible = 5000.0 * F
        with caplog.at_level(logging.WARNING):
            t0 = datetime.datetime(2026, 6, 21, 2, 0)
            coordinator._clamp_solar_reading(impossible, now=t0)
            coordinator._clamp_solar_reading(
                impossible, now=t0 + SOLAR_CLAMP_WARN_INTERVAL / 2
            )
            first = [r for r in caplog.records if "clear-sky" in r.message]
            assert len(first) == 1

            coordinator._clamp_solar_reading(
                impossible, now=t0 + SOLAR_CLAMP_WARN_INTERVAL
            )
            again = [r for r in caplog.records if "clear-sky" in r.message]
            assert len(again) == 2

    def test_a_plausible_reading_says_nothing(self, coordinator, caplog):
        with caplog.at_level(logging.WARNING):
            coordinator._clamp_solar_reading(300.0 * F, now=SUMMER_NOON)
        assert not [r for r in caplog.records if "clear-sky" in r.message]
