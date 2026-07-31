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
from unittest.mock import Mock

import pytest
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


class TestBothIngestionPaths:
    """Both writers of the field have to agree, or the buffer aggregates a mix."""

    def test_the_polled_row_is_clamped_in_place(self, coordinator):
        weatherdata = {
            const.MAPPING_TEMPERATURE: 25.0,
            const.MAPPING_SOLRAD: 5000.0 * F,
        }
        coordinator._apply_solar_clamp(weatherdata)
        assert weatherdata[const.MAPPING_SOLRAD] < 5000.0 * F
        assert weatherdata[const.MAPPING_TEMPERATURE] == 25.0

    def test_a_row_without_radiation_is_untouched(self, coordinator):
        weatherdata = {const.MAPPING_TEMPERATURE: 25.0}
        coordinator._apply_solar_clamp(weatherdata)
        assert weatherdata == {const.MAPPING_TEMPERATURE: 25.0}

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
