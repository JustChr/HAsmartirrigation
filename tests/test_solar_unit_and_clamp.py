"""Solar-radiation unit auto-detection and the FAO-56 clear-sky clamp.

Regression coverage for the issue where a Solar Radiation sensor reporting
W/m2 but configured as MJ/day/m2 fed ~101 MJ/day/m2 into PyETO, inflating ETo
to ~18 mm/day and crashing the bucket.
"""

from types import SimpleNamespace

from homeassistant.const import (
    PERCENTAGE,
    UnitOfIrradiance,
    UnitOfSpeed,
    UnitOfTemperature,
)

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.calcmodules.pyeto import PyETO, SOLRAD_behavior
from custom_components.smart_irrigation.helpers import (
    convert_mapping_to_metric,
    ha_unit_to_internal_unit,
)


class TestHaUnitResolution:
    """`ha_unit_to_internal_unit` maps HA units and rejects mismatches."""

    def test_irradiance_resolves_for_solrad(self) -> None:
        assert (
            ha_unit_to_internal_unit(
                UnitOfIrradiance.WATTS_PER_SQUARE_METER, const.MAPPING_SOLRAD
            )
            == const.UNIT_W_M2
        )

    def test_temperature_resolves(self) -> None:
        assert (
            ha_unit_to_internal_unit(
                UnitOfTemperature.CELSIUS, const.MAPPING_TEMPERATURE
            )
            == UnitOfTemperature.CELSIUS
        )

    def test_speed_resolves(self) -> None:
        assert (
            ha_unit_to_internal_unit(
                UnitOfSpeed.METERS_PER_SECOND, const.MAPPING_WINDSPEED
            )
            == const.UNIT_MS
        )

    def test_percentage_for_humidity(self) -> None:
        assert (
            ha_unit_to_internal_unit(PERCENTAGE, const.MAPPING_HUMIDITY)
            == const.UNIT_PERCENT
        )

    def test_unit_meaningless_for_field_is_rejected(self) -> None:
        # A °C sensor mistakenly mapped to Solar Radiation must not be used.
        assert (
            ha_unit_to_internal_unit(UnitOfTemperature.CELSIUS, const.MAPPING_SOLRAD)
            is None
        )

    def test_unknown_or_missing_unit(self) -> None:
        assert ha_unit_to_internal_unit(None, const.MAPPING_SOLRAD) is None
        assert ha_unit_to_internal_unit("lx", const.MAPPING_SOLRAD) is None


class TestSolarConversion:
    """W/m2 → MJ/day/m2 conversion keeps solar in a physical range."""

    def test_wm2_average_converts_to_sane_mj(self) -> None:
        # ~100 W/m2 daily-average irradiance -> ~8.6 MJ/day/m2 (well under the
        # ~31 clear-sky ceiling), instead of being read as "100 MJ/day/m2".
        out = convert_mapping_to_metric(
            101.235, const.MAPPING_SOLRAD, const.UNIT_W_M2, True
        )
        assert 8.0 < out < 9.5


def _make_pyeto(solrad_behavior: str) -> PyETO:
    hass = SimpleNamespace(
        config=SimpleNamespace(as_dict=lambda: {"latitude": 49.0, "elevation": 300.0})
    )
    return PyETO(
        hass,
        "",
        {const.CONF_PYETO_SOLRAD_BEHAVIOR: solrad_behavior},
    )


_DONT_ESTIMATE = SOLRAD_behavior.DontEstimate.value


def _summer_weatherdata(sol_rad: float) -> dict:
    return {
        const.MAPPING_DEWPOINT: 14.0,
        const.MAPPING_MIN_TEMP: 15.0,
        const.MAPPING_MAX_TEMP: 29.0,
        const.MAPPING_WINDSPEED: 2.0,
        const.MAPPING_PRESSURE: 1013.0,
        const.MAPPING_SOLRAD: sol_rad,
    }


class TestClearSkyClamp:
    """An out-of-range measured solar value is clamped to clear-sky."""

    def test_absurd_solrad_is_clamped(self) -> None:
        pyeto = _make_pyeto(_DONT_ESTIMATE)
        # 101 MJ/day/m2 is ~3x the clear-sky maximum; ETo must not explode.
        absurd = pyeto.calculate_et_for_day(_summer_weatherdata(101.235))
        # A clamped clear-sky day yields a high-but-physical ETo (well under the
        # ~18 mm the uncapped value produced in the bug report).
        assert -12.0 < absurd < 0.0

    def test_clamped_matches_clearsky_input(self) -> None:
        pyeto = _make_pyeto(_DONT_ESTIMATE)
        # Feeding exactly the clear-sky value should give ~the same ETo as the
        # clamped absurd value (both end up at Rs = Rso).
        clamped = pyeto.calculate_et_for_day(_summer_weatherdata(101.235))
        clearsky = pyeto.calculate_et_for_day(_summer_weatherdata(31.0))
        assert abs(clamped - clearsky) < 1.0
