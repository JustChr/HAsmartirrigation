"""Helpers for the Smart Irrigation integration."""

import importlib
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from homeassistant import exceptions
from homeassistant.const import (
    PERCENTAGE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfIrradiance,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumetricFlux,
)
from homeassistant.core import HomeAssistant

from .const import (
    CONF_WEATHER_SERVICE_MET,
    CONF_WEATHER_SERVICE_OPENMETEO,
    CONF_WEATHER_SERVICE_OWM,
    CONF_WEATHER_SERVICE_PW,
    CUSTOM_COMPONENTS,
    DOMAIN,
    GALLON_TO_LITER_FACTOR,
    INCH_TO_MM_FACTOR,
    INHG_TO_HPA_FACTOR,
    INHG_TO_PSI_FACTOR,
    K_TO_C_FACTOR,
    KMH_TO_MILESH_FACTOR,
    KMH_TO_MS_FACTOR,
    LITER_TO_GALLON_FACTOR,
    M2_TO_SQ_FT_FACTOR,
    MAPPING_CONF_PRESSURE_RELATIVE,
    MAPPING_CONF_PRESSURE_TYPE,
    MAPPING_CURRENT_PRECIPITATION,
    MAPPING_DEWPOINT,
    MAPPING_EVAPOTRANSPIRATION,
    MAPPING_HUMIDITY,
    MAPPING_MAX_TEMP,
    MAPPING_MIN_TEMP,
    MAPPING_PRECIPITATION,
    MAPPING_PRESSURE,
    MAPPING_SOLRAD,
    MAPPING_TEMPERATURE,
    MAPPING_WINDSPEED,
    MBAR_TO_INHG_FACTOR,
    MBAR_TO_PSI_FACTOR,
    MILESH_TO_KMH_FACTOR,
    MILESH_TO_MS_FACTOR,
    MM_TO_INCH_FACTOR,
    MS_TO_KMH_FACTOR,
    MS_TO_MILESH_FACTOR,
    PSI_TO_HPA_FACTOR,
    PSI_TO_INHG_FACTOR,
    SOLAR_CLEAR_SKY_TOLERANCE,
    SOLAR_PLAUSIBILITY_FLOOR_W_M2,
    SQ_FT_TO_M2_FACTOR,
    UNIT_GPM,
    UNIT_HPA,
    UNIT_INCH,
    UNIT_INCHH,
    UNIT_INHG,
    UNIT_KMH,
    UNIT_LPM,
    UNIT_M2,
    UNIT_MBAR,
    UNIT_MH,
    UNIT_MILLIBAR,
    UNIT_MJ_DAY_M2,
    UNIT_MJ_DAY_SQFT,
    UNIT_MM,
    UNIT_MMH,
    UNIT_MS,
    UNIT_PERCENT,
    UNIT_PSI,
    UNIT_SECONDS,
    UNIT_SQ_FT,
    UNIT_W_M2,
    UNIT_W_SQFT,
    W_M2_TO_W_SQ_FT_FACTOR,
    W_SQ_FT_TO_W_M2_FACTOR,
    W_TO_MJ_DAY_FACTOR,
)
from .et_hourly import (
    clear_sky_radiation_hourly,
    extraterrestrial_radiation_hourly,
)
from .pressure import relative_to_absolute_pressure
from .weathermodules.MetOfficeClient import MetOfficeClient
from .weathermodules.OWMClient import OWMClient
from .weathermodules.PirateWeatherClient import PirateWeatherClient

_LOGGER = logging.getLogger(__name__)


def check_time(itime):
    """Check time."""
    # Add type safety for None and non-string inputs
    if not isinstance(itime, str):
        return False

    try:
        timesplit = itime.split(":")
        if len(timesplit) != 2:
            return False

        hours = int(timesplit[0])
        minutes = int(timesplit[1])
        if hours in range(24) and minutes in range(
            60
        ):  # range does not include upper bound
            return True
    except (ValueError, AttributeError):
        return False

    return False


def convert_mapping_to_metric(val, mapping, unit, system_is_metric):
    """Convert a value to its metric equivalent based on mapping, unit, and system settings.

    Args:
        val: The value to convert.
        mapping: The type of measurement being converted.
        unit: The current unit of the value.
        system_is_metric: Whether the system is using metric units.

    Returns:
        The value converted to metric units, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if mapping == MAPPING_HUMIDITY:
        # humidity unit is same in metric and imperial: %
        return val
    if mapping in [
        MAPPING_DEWPOINT,
        MAPPING_TEMPERATURE,
        MAPPING_MAX_TEMP,
        MAPPING_MIN_TEMP,
    ]:
        # either Celsius or F. If celsius, no need to convert.
        if unit:
            # a unit was set, convert it
            return convert_between(
                from_unit=unit, to_unit=UnitOfTemperature.CELSIUS, val=val
            )
        # no unit was set, so it's dependent on system_is_metric if we need to convert
        if system_is_metric:
            return val
        # assume the unit is in F
        return convert_between(
            from_unit=UnitOfTemperature.FAHRENHEIT,
            to_unit=UnitOfTemperature.CELSIUS,
            val=val,
        )
    if mapping in [MAPPING_PRECIPITATION, MAPPING_EVAPOTRANSPIRATION]:
        # either mm or inch. If mm no need to convert.
        if unit:
            return convert_between(from_unit=unit, to_unit=UNIT_MM, val=val)
        if system_is_metric:
            return val
        # assume the unit is in inch
        return convert_between(from_unit=UNIT_INCH, to_unit=UNIT_MM, val=val)
    if mapping == MAPPING_CURRENT_PRECIPITATION:
        # either mm/h or inch/h. If mm/h no need to convert.
        if unit:
            return convert_between(from_unit=unit, to_unit=UNIT_MMH, val=val)
        if system_is_metric:
            return val
        # assume the unit is in inch/h
        return convert_between(from_unit=UNIT_INCHH, to_unit=UNIT_MMH, val=val)
    if mapping == MAPPING_PRESSURE:
        # either: mbar, hpa (default for metric), psi or inhg (default for imperial)
        if unit:
            return convert_between(from_unit=unit, to_unit=UNIT_HPA, val=val)
        if system_is_metric:
            return val
        # assume it's inHG
        return convert_between(from_unit=UNIT_INHG, to_unit=UNIT_HPA, val=val)
    if mapping == MAPPING_SOLRAD:
        # either: assume w/m2 for metric, w/sqft for imperial
        if unit:
            _LOGGER.debug(
                "[convert_mapping_to_metric]: unit set, converting %s from %s to %s",
                val,
                unit,
                UNIT_MJ_DAY_M2,
            )
            return convert_between(from_unit=unit, to_unit=UNIT_MJ_DAY_M2, val=val)
        if system_is_metric:
            # assume it's w/m2
            _LOGGER.debug(
                "[convert_mapping_to_metric]: since system is metric and unit was not set, converting %s from W/m2 to MJ/day/m2",
                val,
            )
            return convert_between(from_unit=UNIT_W_M2, to_unit=UNIT_MJ_DAY_M2, val=val)
        # assume it's w/sqft
        _LOGGER.debug(
            "[convert_mapping_to_metric]: since system is imperial and unit was not set, converting %s from W/sq ft to MJ/day/m2",
            val,
        )
        return convert_between(from_unit=UNIT_W_SQFT, to_unit=UNIT_MJ_DAY_M2, val=val)
    if mapping == MAPPING_WINDSPEED:
        # either UNIT_KMH, unit: UNIT_MS (Default for metric), m/h (imperial)
        if unit:
            return convert_between(from_unit=unit, to_unit=UNIT_MS, val=val)
        if system_is_metric:
            return val
        # assume it's m/h
        return convert_between(from_unit=UNIT_MH, to_unit=UNIT_MS, val=val)
    return None


# Home Assistant exposes an entity's unit in its ``unit_of_measurement``
# attribute. Map those native HA unit strings onto this integration's internal
# unit constants so a sensor's *actual* unit drives the conversion, instead of a
# unit hand-picked in the sensor-group config that can silently disagree with
# the entity (e.g. a W/m2 solar sensor configured as MJ/day/m2 → ET blows up).
_HA_UNIT_TO_INTERNAL = {
    UnitOfTemperature.CELSIUS: UnitOfTemperature.CELSIUS,
    UnitOfTemperature.FAHRENHEIT: UnitOfTemperature.FAHRENHEIT,
    UnitOfPressure.HPA: UNIT_HPA,
    UnitOfPressure.MBAR: UNIT_MBAR,
    UnitOfPressure.PSI: UNIT_PSI,
    UnitOfPressure.INHG: UNIT_INHG,
    UnitOfSpeed.METERS_PER_SECOND: UNIT_MS,
    UnitOfSpeed.KILOMETERS_PER_HOUR: UNIT_KMH,
    UnitOfSpeed.MILES_PER_HOUR: UNIT_MH,
    UnitOfPrecipitationDepth.MILLIMETERS: UNIT_MM,
    UnitOfPrecipitationDepth.INCHES: UNIT_INCH,
    UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR: UNIT_MMH,
    UnitOfVolumetricFlux.INCHES_PER_HOUR: UNIT_INCHH,
    UnitOfIrradiance.WATTS_PER_SQUARE_METER: UNIT_W_M2,
    PERCENTAGE: UNIT_PERCENT,
}

# Internal units that are meaningful for each mapping field — guards against a
# mis-assigned entity (e.g. a °C sensor mapped to Solar Radiation) feeding a
# nonsensical-but-recognised unit into the conversion.
_MAPPING_ALLOWED_UNITS = {
    MAPPING_TEMPERATURE: {UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT},
    MAPPING_MAX_TEMP: {UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT},
    MAPPING_MIN_TEMP: {UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT},
    MAPPING_DEWPOINT: {UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT},
    MAPPING_PRESSURE: {UNIT_HPA, UNIT_MBAR, UNIT_MILLIBAR, UNIT_PSI, UNIT_INHG},
    MAPPING_WINDSPEED: {UNIT_MS, UNIT_KMH, UNIT_MH},
    MAPPING_PRECIPITATION: {UNIT_MM, UNIT_INCH},
    MAPPING_EVAPOTRANSPIRATION: {UNIT_MM, UNIT_INCH},
    MAPPING_CURRENT_PRECIPITATION: {UNIT_MMH, UNIT_INCHH},
    MAPPING_SOLRAD: {UNIT_W_M2, UNIT_W_SQFT, UNIT_MJ_DAY_M2, UNIT_MJ_DAY_SQFT},
    MAPPING_HUMIDITY: {UNIT_PERCENT},
}


def ha_unit_to_internal_unit(ha_unit, mapping_key):
    """Resolve a Home Assistant entity unit to this integration's internal unit.

    Returns the internal unit string when ``ha_unit`` is a recognised unit that
    is also meaningful for ``mapping_key`` (so ``convert_mapping_to_metric`` can
    convert from it), else None — in which case the caller falls back to the unit
    configured in the sensor group.
    """
    if not ha_unit:
        return None
    internal = _HA_UNIT_TO_INTERNAL.get(ha_unit)
    if internal is None:
        return None
    allowed = _MAPPING_ALLOWED_UNITS.get(mapping_key)
    if allowed is not None and internal not in allowed:
        return None
    return internal


def zone_depth_default(mm_value, metric):
    """Materialise a depth-valued zone default in the zone's STORED units.

    Depth-valued zone fields — ``bucket``, ``maximum_bucket``, ``drainage_rate``,
    ``bucket_threshold`` — are stored in the user's DISPLAY units (mm when metric,
    inches when imperial); ``calculate_module`` converts them to mm for the maths and
    back before storing.

    This integration has two unit conventions, distinguished by the field NAME:

      * ``*_mm`` (only ``precipitation_threshold_mm`` today) is stored canonically in
        millimetres and converted at the backend boundary — ``websocket_get_config``
        on read, ``async_update_config`` on write.
      * everything else, including all four depth fields, is stored in display units.
        ``websocket_get_zones`` is a pure passthrough with no conversion.

    Note the UI label proves nothing either way: ``precipitation_threshold_mm`` and
    ``bucket_threshold`` are both rendered with ``output_unit(config, ...)``, one over
    canonical mm and one over display units. The suffix is the signal.

    Their default CONSTANTS, however, are authored in millimetres. Handing a raw mm
    constant to an imperial zone stores it verbatim and therefore means inches — 24
    becomes 610 mm, 20 becomes 508 mm/h, and -10 becomes -254 mm. The last one is the
    damaging case: irrigation gates on ``bucket < bucket_threshold``, so no realistic
    bucket ever passes and every deficit-gated run is silently suppressed.

    Call this at every point a default is materialised for a zone (store hydration,
    zone creation) so the authored intent survives into either unit system.
    """
    if mm_value is None:
        return None
    if metric:
        return mm_value
    return convert_between(UNIT_MM, UNIT_INCH, mm_value)


def resolve_sensor_unit(mapping_key, configured_unit, ha_unit, sensor_id=None):
    """Pick the unit a sensor state should be converted FROM.

    Prefers the entity's *own* reported unit over the unit hand-picked in the
    sensor group: HA knows the sensor's real unit, and a mismatch there silently
    corrupts the value (e.g. a W/m2 solar sensor configured as MJ/day/m2 inflates
    ET ~12x). Falls back to the configured unit when the entity reports no unit
    or one we don't recognise for this field.

    Shared by both ingestion paths — the interval poll
    (``build_sensor_values_for_mapping``) and the event-driven appends in
    ``ContinuousUpdateMixin`` — so the two can never disagree about a value's
    unit and write mutually inconsistent rows into the same buffer.
    """
    detected_unit = ha_unit_to_internal_unit(ha_unit, mapping_key)
    if detected_unit and configured_unit and detected_unit != configured_unit:
        _LOGGER.info(
            "Sensor %s reports unit '%s' for %s; using it instead of the "
            "configured '%s'.",
            sensor_id,
            detected_unit,
            mapping_key,
            configured_unit,
        )
    return detected_unit or configured_unit


def convert_between(from_unit, to_unit, val):
    """Convert a value from one unit to another based on the provided units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    _LOGGER.debug(
        "[convert_between]: Converting %s from %s to %s", val, from_unit, to_unit
    )
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        _LOGGER.debug(
            ["[convert_between]: Value is None, Unknown or Unavailable, returning None"]
        )
        return None
    if from_unit == to_unit or from_unit in [UNIT_PERCENT, UNIT_SECONDS]:
        # no conversion necessary here!
        _LOGGER.debug(
            "[convert_between]: No conversion necessary, returning value %s", val
        )
        return val
    # convert temperatures
    if from_unit in [
        UnitOfTemperature.CELSIUS,
        UnitOfTemperature.FAHRENHEIT,
        UnitOfTemperature.KELVIN,
    ]:
        _LOGGER.debug("[convert_between]: Converting temperatures")
        return convert_temperatures(from_unit, to_unit, val)
    # convert lengths
    if from_unit in [UNIT_MM, UNIT_INCH]:
        _LOGGER.debug("[convert_between]: Converting lengths")
        return convert_length(from_unit, to_unit, val)
    # convert precip rates
    if from_unit in [UNIT_MMH, UNIT_INCHH]:
        _LOGGER.debug("[convert_between]: Converting precip rates")
        return convert_precip_rate(from_unit, to_unit, val)
    # convert volumes
    if from_unit in [UNIT_LPM, UNIT_GPM]:
        _LOGGER.debug("[convert_between]: Converting volumes")
        return convert_volume(from_unit, to_unit, val)
    # convert areas
    if from_unit in [UNIT_M2, UNIT_SQ_FT]:
        _LOGGER.debug("[convert_between]: Converting areas")
        return convert_area(from_unit, to_unit, val)
    # convert pressures
    if from_unit in [UNIT_MBAR, UNIT_MILLIBAR, UNIT_HPA, UNIT_PSI, UNIT_INHG]:
        _LOGGER.debug("[convert_between]: Converting pressures")
        return convert_pressure(from_unit, to_unit, val)
    # convert speeds
    if from_unit in [UNIT_KMH, UNIT_MS, UNIT_MH]:
        _LOGGER.debug("[convert_between]: Converting speeds")
        return convert_speed(from_unit, to_unit, val)
    # convert production/area
    if from_unit in [UNIT_W_M2, UNIT_MJ_DAY_M2, UNIT_W_SQFT, UNIT_MJ_DAY_SQFT]:
        _LOGGER.debug("[convert_between]: Converting production/area")
        return convert_production(from_unit, to_unit, val)
    # unexpected from_unit
    _LOGGER.warning(
        "Unexpected conversion of %s from %s to %s", val, from_unit, to_unit
    )
    return None


def convert_production(from_unit, to_unit, val):
    """Convert production/area values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    _LOGGER.debug(
        "[convert production]: converting %s from %s to %s", val, from_unit, to_unit
    )
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        _LOGGER.debug("[convert production]: Value is None, Unknown or Unavailable")
        return None
    if to_unit == from_unit:
        _LOGGER.debug("[convert production]: No conversion necessary")
        return val
    if to_unit == UNIT_MJ_DAY_M2:
        _LOGGER.debug("[convert production]: Converting to MJ/day/m2")
        if from_unit == UNIT_W_M2:
            outval = float(float(val) * W_TO_MJ_DAY_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from W/m2 to MJ/day/m2. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_W_SQFT:
            outval = float((float(val) * W_SQ_FT_TO_W_M2_FACTOR) * W_TO_MJ_DAY_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from W/sq ft to MJ/day/m2. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_MJ_DAY_SQFT:
            outval = float(float(val) * SQ_FT_TO_M2_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from MJ/day/sq ft to MJ/day/m2. Result: %s",
                val,
                outval,
            )
            return outval
    elif to_unit == UNIT_MJ_DAY_SQFT:
        _LOGGER.debug("[convert production]: Converting to MJ/day/sq ft")
        if from_unit == UNIT_W_M2:
            outval = float((float(val) * W_M2_TO_W_SQ_FT_FACTOR) * W_TO_MJ_DAY_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from W/m2 to MJ/day/sq ft. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_W_SQFT:
            outval = float(float(val) * W_TO_MJ_DAY_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from W/sq ft to MJ/day/sq ft. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_MJ_DAY_M2:
            outval = float(float(val) * M2_TO_SQ_FT_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from MJ/day/m2 to MJ/day/sq ft. Result: %s",
                val,
                outval,
            )
            return outval
    elif to_unit == UNIT_W_M2:
        _LOGGER.debug("[convert production]: Converting to W/m2")
        if from_unit == UNIT_W_SQFT:
            outval = float(float(val) * W_SQ_FT_TO_W_M2_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from W/sq ft to W/m2. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_MJ_DAY_SQFT:
            outval = float((float(val) / W_TO_MJ_DAY_FACTOR) * W_SQ_FT_TO_W_M2_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from MJ/day/sq ft to W/m2. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_MJ_DAY_M2:
            outval = float(float(val) / W_TO_MJ_DAY_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from MJ/day/m2 to W/m2. Result: %s",
                val,
                outval,
            )
            return outval
    elif to_unit == UNIT_W_SQFT:
        _LOGGER.debug("[convert production]: Converting to W/sq ft")
        if from_unit == UNIT_W_M2:
            outval = float(float(val) * W_M2_TO_W_SQ_FT_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from W/m2 to W/sq ft. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_MJ_DAY_M2:
            outval = float((float(val) / W_TO_MJ_DAY_FACTOR) * W_M2_TO_W_SQ_FT_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from MJ/day/m2 to W/sq ft. Result: %s",
                val,
                outval,
            )
            return outval
        if from_unit == UNIT_MJ_DAY_SQFT:
            outval = float(float(val) / W_TO_MJ_DAY_FACTOR)
            _LOGGER.debug(
                "[convert production]: Converting %s from MJ/day/sq ft to W/sq ft. Result: %s",
                val,
                outval,
            )
            return outval
    # unknown conversion
    return None


def convert_speed(from_unit, to_unit, val):
    """Convert speed values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if to_unit == from_unit:
        return val
    if to_unit == UNIT_KMH:
        if from_unit == UNIT_MS:
            return float(float(val) * MS_TO_KMH_FACTOR)
        if from_unit == UNIT_MH:
            return float(float(val) * MILESH_TO_KMH_FACTOR)
    elif to_unit == UNIT_MS:
        if from_unit == UNIT_KMH:
            return float(float(val) * KMH_TO_MS_FACTOR)
        if from_unit == UNIT_MH:
            return float(float(val) * MILESH_TO_MS_FACTOR)
    elif to_unit == UNIT_MH:
        if from_unit == UNIT_KMH:
            return float(float(val) * KMH_TO_MILESH_FACTOR)
        if from_unit == UNIT_MS:
            return float(float(val) * MS_TO_MILESH_FACTOR)
    # unknown conversion
    return None


def convert_pressure(from_unit, to_unit, val):
    """Convert pressure values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if to_unit == from_unit:
        return val
    if to_unit in [UNIT_MBAR, UNIT_HPA]:
        if from_unit in [UNIT_HPA, UNIT_MBAR]:
            # 1 mbar = 1hpa
            return val
        if from_unit == UNIT_PSI:
            return float(float(val) * PSI_TO_HPA_FACTOR)
        if from_unit == UNIT_INHG:
            return float(float(val) * INHG_TO_HPA_FACTOR)
    if to_unit == UNIT_PSI:
        if from_unit in [UNIT_HPA, UNIT_MBAR]:
            return float(float(val) * MBAR_TO_PSI_FACTOR)
        if from_unit == UNIT_INHG:
            return float(float(val) * INHG_TO_PSI_FACTOR)
    if to_unit == UNIT_INHG:
        if from_unit in [UNIT_HPA, UNIT_MBAR]:
            return float(float(val) * MBAR_TO_INHG_FACTOR)
        if from_unit == UNIT_PSI:
            return float(float(val) * PSI_TO_INHG_FACTOR)
    # unknown conversion
    return None


def convert_area(from_unit, to_unit, val):
    """Convert area values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if to_unit == from_unit:
        return val
    if to_unit == UNIT_M2:
        if from_unit == UNIT_SQ_FT:
            return float(float(val) * SQ_FT_TO_M2_FACTOR)
    elif to_unit == UNIT_SQ_FT:
        if from_unit == UNIT_M2:
            return float(float(val) * M2_TO_SQ_FT_FACTOR)
    # unexpected conversion
    return None


def convert_volume(from_unit, to_unit, val):
    """Convert volume values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if to_unit == from_unit:
        return val
    if to_unit == UNIT_LPM:
        if from_unit == UNIT_GPM:
            return float(float(val) * GALLON_TO_LITER_FACTOR)
    elif to_unit == UNIT_GPM:
        if from_unit == UNIT_LPM:
            return float(float(val) * LITER_TO_GALLON_FACTOR)
    # unknown conversion
    return None


def convert_length(from_unit, to_unit, val):
    """Convert length values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if to_unit == from_unit:
        return val
    if to_unit == UNIT_MM:
        if from_unit == UNIT_INCH:
            return float(float(val) * INCH_TO_MM_FACTOR)
    elif to_unit == UNIT_INCH:
        if from_unit == UNIT_MM:
            return float(float(val) * MM_TO_INCH_FACTOR)
    # unknown conversion
    return None


def convert_precip_rate(from_unit, to_unit, val):
    """Convert precipitation rate values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if to_unit == from_unit:
        return val
    if to_unit == UNIT_MMH:
        if from_unit == UNIT_INCHH:
            return float(float(val) * INCH_TO_MM_FACTOR)
    elif to_unit == UNIT_INCHH:
        if from_unit == UNIT_MMH:
            return float(float(val) * MM_TO_INCH_FACTOR)
    # unknown conversion
    return None


def convert_temperatures(from_unit, to_unit, val):
    """Convert temperature values between different units.

    Args:
        from_unit: The unit of the input value.
        to_unit: The unit to convert the value to.
        val: The value to be converted.

    Returns:
        The converted value, or None if conversion is not possible.

    """
    if val in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
        return None
    if to_unit == from_unit:
        return val
    if to_unit == UnitOfTemperature.CELSIUS:
        if from_unit == UnitOfTemperature.FAHRENHEIT:
            return float((float(val) - 32.0) / 1.8)
        if from_unit == UnitOfTemperature.KELVIN:
            return val - K_TO_C_FACTOR
    elif to_unit == UnitOfTemperature.FAHRENHEIT:
        if from_unit == UnitOfTemperature.CELSIUS:
            return float((val * 1.8) + 32.0)
        if from_unit == UnitOfTemperature.KELVIN:
            return float(1.8 * (val - 273) + 32)
    elif to_unit == UnitOfTemperature.KELVIN:
        if from_unit == UnitOfTemperature.FAHRENHEIT:
            return (val + 459.67) * (5.0 / 9.0)
        if from_unit == UnitOfTemperature.CELSIUS:
            return val + K_TO_C_FACTOR
    # unable to do conversion because of unexpected to or from unit
    return None


def to_absolute_pressure(value, mapping, field_config, elevation):
    """Return a Pressure reading as ABSOLUTE (station) pressure.

    ``MAPPING_PRESSURE`` must hold one physical quantity, because the calc
    modules read it as station pressure (FAO-56 uses it for the psychrometric
    constant) and ``weather_aggregate`` means the buffer's rows together. A
    station reporting sea-level ("relative") pressure needs the elevation
    correction first; a buffer mixing corrected and uncorrected rows biases ET by
    however far apart the two writers' outputs are.

    Every writer of that field therefore funnels through here: the interval poll
    in ``__init__`` and the event-driven appends in ``continuous_update``. Takes
    the field's own sensor-group config (the dict that carries
    ``MAPPING_CONF_PRESSURE_TYPE``) so it can be called unconditionally in a loop
    over all mapping keys — anything that is not a relative-typed Pressure field
    is returned untouched.

    The correction itself is ``relative_to_absolute_pressure``, shared with the
    polled path so both writers of the field produce the same quantity.
    """
    if mapping != MAPPING_PRESSURE or value is None:
        return value
    # Legacy stored shape: a bare sensor id string instead of a config dict. No
    # pressure_type to read, so the value is taken as already absolute.
    if not isinstance(field_config, dict):
        return value
    if (
        field_config.get(MAPPING_CONF_PRESSURE_TYPE) != MAPPING_CONF_PRESSURE_RELATIVE
        or elevation is None
    ):
        return value
    return relative_to_absolute_pressure(value, elevation)


def solar_reading_is_rate(unit):
    """Return True when a Solar Radiation reading in ``unit`` is an instantaneous rate.

    ``clamp_solar_to_clear_sky`` measures a reading against the clear-sky
    radiation of the hour centred on the stamp, which is only meaningful for a
    rate. ``MJ/day/m2`` and ``MJ/day/sq ft`` are selectable units for this field
    and describe a DAILY TOTAL: a daily-total sensor reads the same at 02:00 as
    at noon, so ceilinging it against a nighttime clear sky floors the whole
    night away. Measured on a 20 MJ/day/m2 total, that destroyed 36% of the day's
    radiation on 21 June and 72% on 21 December, biasing every zone in the group
    towards under-watering.

    An unset unit means the value is taken as W/m2 (metric) or W/sq ft
    (imperial) by ``convert_mapping_to_metric``, i.e. a rate.

    Shared by both writers of the buffer's Solar Radiation field — the interval
    poll in ``build_sensor_values_for_mapping`` and the event-driven appends in
    ``_continuous_metric_value`` — the same way ``to_absolute_pressure`` is
    shared for Pressure, so the two cannot drift on which readings get a ceiling.
    """
    return unit not in (UNIT_MJ_DAY_M2, UNIT_MJ_DAY_SQFT)


def clamp_solar_to_clear_sky(value, when, latitude, longitude, elevation, tz_offset_h):
    """Ceiling a solar-radiation reading [MJ/day/m2] at clear sky for ``when``.

    ET quality tracks pyranometer quality directly once ET is summed hour by
    hour: the residual against a model reference correlates with the site-vs-model
    solar ratio at r = 0.746 for the hourly form against 0.220 for the daily one.
    This pyranometer misbehaves. Over 423 recorded days four report a clearness
    index above 0.85, one of them sitting at a constant 722 W/m2 for 19 hours
    INCLUDING the whole night (an impossible 10.8 mm/day of ETo), and peak
    instantaneous readings reach 1488 W/m2.

    Clamped to clear sky rather than rejected. Rejecting would leave the
    carry-forward holding the last accepted value, and the failure that matters
    is a sensor stuck at a daytime level: carrying that through the night is
    exactly the 19-hour case above, while clamping puts it at the floor there
    because clear sky at night is 0.

    The clear-sky reference is integrated over the hour CENTRED on ``when``, not
    over the clock hour, so a legitimate reading a few minutes after sunrise is
    not measured against an hour that is mostly dark.

    Returns the value unchanged when it is plausible or when the site has no
    coordinates. The caller decides how to report a clamp -- see
    ``SmartIrrigationCoordinator._clamp_solar_reading`` for why it must not be a
    once-per-lifetime warning.
    """
    if value is None or latitude is None or longitude is None:
        return value
    hour = when.hour + when.minute / 60 + when.second / 3600
    ra = extraterrestrial_radiation_hourly(
        latitude, longitude, when.timetuple().tm_yday, hour, tz_offset_h
    )
    rso = clear_sky_radiation_hourly(ra, elevation or 0.0)
    # Rso is MJ/m2/h and the buffer stores MJ/day/m2; the two differ by 24.
    ceiling = max(
        rso * 24 * SOLAR_CLEAR_SKY_TOLERANCE,
        SOLAR_PLAUSIBILITY_FLOOR_W_M2 * W_TO_MJ_DAY_FACTOR,
    )
    return min(float(value), ceiling)


def altitudeToPressure(alt):
    """Take altitude in meters and convert it to hPa = mbar."""
    return 100 * ((44331.514 - alt) / 11880.516) ** (1 / 0.1902632) / 100


async def validate_api_key(hass: HomeAssistant, weather_service, api_key):
    """Test access to Weather Service API here."""
    if weather_service == CONF_WEATHER_SERVICE_OPENMETEO:
        return  # Open-Meteo requires no API key — nothing to validate
    client = None
    test_lat = 52.353218
    test_lon = 5.0027695
    test_elev = 1
    if weather_service == CONF_WEATHER_SERVICE_OWM:
        client = OWMClient(
            api_key=api_key.strip(),
            latitude=test_lat,
            longitude=test_lon,
            elevation=test_elev,
        )
    elif weather_service == CONF_WEATHER_SERVICE_PW:
        client = PirateWeatherClient(
            api_key=api_key.strip(),
            api_version="1",
            latitude=test_lat,
            longitude=test_lon,
            elevation=test_elev,
        )
    elif weather_service == CONF_WEATHER_SERVICE_MET:
        client = MetOfficeClient(
            api_key=api_key.strip() if api_key else "",
            latitude=test_lat,
            longitude=test_lon,
            elevation=test_elev,
        )
    if client:
        # Use validate_key() when available (OWMClient uses a simpler endpoint
        # that works on all plans; get_data() requires One Call 3.0 subscription)
        validate_fn = getattr(client, "validate_key", None) or client.get_data
        try:
            await hass.async_add_executor_job(validate_fn)
        except OSError as err:
            raise InvalidAuth from err
        except Exception as err:
            raise CannotConnect from err


def loadModules(moduleDir=None):
    """Dynamically load modules from a given directory and return a dictionary of module and class information.

    Args:
        moduleDir: The directory containing modules to load.

    Returns:
        A dictionary mapping module names to their module and class information, or None if no directory is provided.

    """
    if moduleDir:
        res = {}
        moduleDirFullPath = str(Path(__file__).resolve().parent / moduleDir)
        if moduleDirFullPath not in sys.path:
            sys.path.append(moduleDirFullPath)
        # check subfolders
        module_path = Path(moduleDirFullPath)
        thedir = []
        for d in module_path.iterdir():
            s = d
            if s.is_dir() and (s / "__init__.py").exists():
                thedir.append(d.name)
        # load the detected modules

        def extract_classname(theclass):
            """Extract the class name from the __init__ method."""
            if "__init__" in theclass.__dict__:
                return (
                    str(theclass.__dict__["__init__"])
                    .split(".", maxsplit=1)[0]
                    .split(" ")[1]
                )
            return None

        for d in thedir:
            if moduleDirFullPath + os.sep + d not in sys.path:
                sys.path.append(moduleDirFullPath + os.sep + d)
            mod = importlib.import_module(
                "." + d, package=CUSTOM_COMPONENTS + "." + DOMAIN + "." + moduleDir
            )
            if not mod:
                continue
            theclasses = [
                mod.__dict__[c]
                for c in mod.__dict__
                if (
                    isinstance(mod.__dict__[c], type)
                    and mod.__dict__[c].__module__ == mod.__name__
                )
            ]
            for theclass in theclasses:
                classname = extract_classname(theclass)
                if classname:
                    res[d] = {"module": mod, "class": classname}
        return res
    return None


def parse_datetime(val) -> datetime | None:
    """Gets a datetime value or converts one from a string.

    Parsed with ``fromisoformat`` rather than a fixed ``strptime`` pattern.
    Stored timestamps are written by serialising a ``datetime`` with
    ``isoformat()``, which OMITS the fractional part when the microsecond field
    happens to be 0 -- so a pattern requiring ``.%f`` rejects a value this
    integration wrote itself, roughly once in a million writes.

    That is not a transient failure. The strings reaching here are the zone
    consumption watermark and each buffered reading's timestamp, and the
    watermark is only advanced at the END of a successful calculation. A
    watermark that cannot be parsed therefore aborts the calculation before it
    can be replaced, so the zone never calculates again until the value is
    edited by hand.

    ``fromisoformat`` accepts both forms, and matches the full-ISO parser
    ``websockets._safe_parse_datetime`` already uses on these same strings.
    """
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        return datetime.fromisoformat(val)
    _LOGGER.warning("[get_datetime]: value not instanceof datetime or string: %s", val)
    return None


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


def normalize_zone_selection(zone_ids):
    """Normalize a schedule's ``zones`` value to None (= all) or a list of ids.

    The stored contract is "a list of zone ids, or the literal ``all``"
    (const.py: SCHEDULE_CONF_ZONES), and the panel only ever writes those two
    shapes. Every consumer, though, did its own `if zones == "all"` check and
    then iterated the value directly — so a BARE STRING that is not "all"
    iterates its CHARACTERS. A schedule stored with ``zones: "12"`` would
    target zones 1 and 2 instead of zone 12, silently watering the wrong
    ground; a single-digit id happens to work by coincidence, which is what
    makes this the kind of bug that survives testing.

    Not reachable through the panel today. It is reachable through a
    hand-edited ``.storage`` file or a future API caller, and the cost of
    ruling it out permanently is this function.

    Returns None for "everything" so callers can keep one falsy check.
    """
    if zone_ids is None or zone_ids == "all":
        return None
    if isinstance(zone_ids, str):
        # A bare string is a single id, never a sequence of them.
        return [zone_ids]
    return list(zone_ids)


def normalize_azimuth_angle(angle: float) -> float:
    """Normalize any azimuth angle to 0-360 degree range.

    Args:
        angle: Input angle in degrees (can be any value)

    Returns:
        Normalized angle in 0-360 degree range

    Examples:
        normalize_azimuth_angle(450) -> 90
        normalize_azimuth_angle(-30) -> 330
        normalize_azimuth_angle(365) -> 5
    """
    return angle % 360


def calculate_solar_azimuth(
    latitude: float, longitude: float, timestamp: datetime
) -> float:
    """Calculate solar azimuth angle for a given location and time.

    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        timestamp: UTC datetime object

    Returns:
        Solar azimuth angle in degrees (0-360, 0=North, 90=East, 180=South, 270=West)
    """
    import math

    # Convert to radians
    lat_rad = math.radians(latitude)

    # Day of year
    day_of_year = timestamp.timetuple().tm_yday

    # Solar declination (simplified)
    declination = math.radians(
        23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
    )

    # Hour angle
    time_decimal = timestamp.hour + timestamp.minute / 60.0 + timestamp.second / 3600.0
    # Longitude correction for local solar time
    longitude_correction = longitude / 15.0
    solar_time = time_decimal - longitude_correction
    hour_angle = math.radians((solar_time - 12) * 15)

    # Solar elevation (calculated but not used in this function)
    # elevation = math.asin(
    #     math.sin(lat_rad) * math.sin(declination) +
    #     math.cos(lat_rad) * math.cos(declination) * math.cos(hour_angle)
    # )

    # Solar azimuth
    azimuth = math.atan2(
        math.sin(hour_angle),
        math.cos(hour_angle) * math.sin(lat_rad)
        - math.tan(declination) * math.cos(lat_rad),
    )

    # Convert to degrees and normalize to 0-360 (0=North, 90=East, 180=South, 270=West)
    azimuth_degrees = (math.degrees(azimuth) + 180) % 360

    return azimuth_degrees


def find_next_solar_azimuth_time(
    latitude: float,
    longitude: float,
    target_azimuth: float,
    start_time: datetime,
    max_days: int = 1,
) -> datetime | None:
    """Find the next time when the sun will be at a specific azimuth angle.

    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        target_azimuth: Target azimuth angle in degrees (0-360)
        start_time: Starting datetime to search from
        max_days: Maximum days to search ahead

    Returns:
        Next datetime when sun will be at target azimuth, or None if not found
    """
    from datetime import timedelta

    # Search in 15-minute intervals for the next 24 hours by default
    search_interval = timedelta(minutes=15)
    max_search_time = start_time + timedelta(days=max_days)

    current_time = start_time
    prev_azimuth = calculate_solar_azimuth(latitude, longitude, current_time)

    while current_time < max_search_time:
        current_time += search_interval
        current_azimuth = calculate_solar_azimuth(latitude, longitude, current_time)

        # Check if we've crossed the target azimuth
        if _azimuth_crossed_target(prev_azimuth, current_azimuth, target_azimuth):
            # Refine to minute precision
            return _refine_azimuth_time(
                latitude,
                longitude,
                target_azimuth,
                current_time - search_interval,
                current_time,
            )

        prev_azimuth = current_azimuth

    return None


def _azimuth_crossed_target(
    prev_azimuth: float, current_azimuth: float, target: float
) -> bool:
    """Check if azimuth crossed the target between two measurements."""
    # Handle wraparound case (359° -> 1°)
    if abs(prev_azimuth - current_azimuth) > 180:
        if prev_azimuth > current_azimuth:
            # Wrapped from 359 to small number
            return target >= prev_azimuth or target <= current_azimuth
        # Wrapped from small number to 359
        return target <= prev_azimuth or target >= current_azimuth
    # Normal case
    return (
        min(prev_azimuth, current_azimuth)
        <= target
        <= max(prev_azimuth, current_azimuth)
    )


def _refine_azimuth_time(
    latitude: float,
    longitude: float,
    target_azimuth: float,
    start_time: datetime,
    end_time: datetime,
) -> datetime:
    """Refine azimuth time to minute precision using binary search."""
    while (end_time - start_time).total_seconds() > 60:
        mid_time = start_time + (end_time - start_time) / 2
        mid_azimuth = calculate_solar_azimuth(latitude, longitude, mid_time)

        start_azimuth = calculate_solar_azimuth(latitude, longitude, start_time)

        if _azimuth_crossed_target(start_azimuth, mid_azimuth, target_azimuth):
            end_time = mid_time
        else:
            start_time = mid_time
    return start_time
