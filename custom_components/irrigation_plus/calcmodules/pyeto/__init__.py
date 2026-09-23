"""The PyETO module for Irrigation Plus Integration."""

import datetime
import logging
from enum import Enum
from statistics import mean

import voluptuous as vol
from homeassistant.const import CONF_ELEVATION, CONF_LATITUDE
from homeassistant.core import HomeAssistant

from custom_components.irrigation_plus.calcmodules.calcmodule import (
    SmartIrrigationCalculationModule,
)
from custom_components.irrigation_plus.const import (
    CONF_PYETO_COASTAL,
    CONF_PYETO_FORECAST_DAYS,
    CONF_PYETO_SOLRAD_BEHAVIOR,
)

from .pyeto import (
    avp_from_tdew,
    convert,
    cs_rad,
    daylight_hours,
    deg2rad,
    delta_svp,
    et_rad,
    fao56_penman_monteith,
    inv_rel_dist_earth_sun,
    net_in_sol_rad,
    net_out_lw_rad,
    net_rad,
    psy_const,
    sol_dec,
    sol_rad_from_sun_hours,
    sol_rad_from_t,
    sunset_hour_angle,
    svp_from_t,
)

_LOGGER = logging.getLogger(__name__)


class SOLRAD_behavior(Enum):
    """Enumeration of solar radiation estimation behaviors for PyETO."""

    EstimateFromTemp = "1"
    EstimateFromSunHours = "2"
    DontEstimate = "3"
    EstimateFromSunHoursAndTemperature = "4"


DEFAULT_COASTAL = False
DEFAULT_SOLRAD_BEHAVIOR = SOLRAD_behavior.EstimateFromTemp
DEFAULT_FORECAST_DAYS = 0


def solrad_behavior_value(raw) -> str:
    """The bare value string of a solrad behaviour, whatever form it arrives in.

    Wurzel: the setting reaches us as the bare value string when the panel's
    select wrote it, and as an enum MEMBER whenever the DEFAULT is used --
    ``DEFAULT_SOLRAD_BEHAVIOR`` is a member. Every comparison downstream tests
    against ``.value``, so a member matched NOTHING and fell through to the
    implicit else -- sun hours. Two ways in, both ordinary:
      * a fresh install, where the factory ``ModuleEntry`` carries no
        ``MODULE_CONFIG`` at all (``store.py``), so ``if config:`` never runs;
      * a config written by the panel for ``forecast_days`` or ``coastal``
        alone, where ``config.get(KEY, DEFAULT_SOLRAD_BEHAVIOR)`` hands the
        member back while the dropdown displays EstimateFromTemp.
    Either way the constant, the schema default and the dropdown all said
    EstimateFromTemp and the arithmetic used sun hours (#158).

    NOT the schema: ``CalcModule.__init__`` calls ``self._schema(config)`` and
    DISCARDS the result, so ``vol.Coerce(SOLRAD_behavior)`` validates but never
    rewrites the stored dict. The member form is handled here anyway because it
    costs nothing and the setting has two legal spellings either way -- but do
    not describe coercion as its source.

    Fix-Logik: normalise ONCE, here, so ``_solrad_behavior`` is always the bare
    value string. That is what makes the three comparison sites correct at the
    root rather than each guarding itself -- ``live_estimate`` had already grown
    its own ``getattr(x, "value", x)`` for the config dict, and its other site
    ``str(modinst._solrad_behavior)`` would have read a member as
    ``"SOLRAD_behavior.DontEstimate"`` and never matched ``"3"``.

    NOT-TO-DO: do not "fix" this by comparing against the members instead. The
    panel writes bare strings, so the comparisons would then fail for every
    install that HAS touched the dropdown -- the same defect from the other
    side.

    siehe tests/test_pyeto_solrad_default.py
    """
    value = getattr(raw, "value", raw)
    if value is None:
        return str(DEFAULT_SOLRAD_BEHAVIOR.value)
    return str(value)


MAPPING_DEWPOINT = "Dewpoint"
MAPPING_EVAPOTRANSPIRATION = "Evapotranspiration"
MAPPING_HUMIDITY = "Humidity"
MAPPING_MAX_TEMP = "Maximum Temperature"
MAPPING_MIN_TEMP = "Minimum Temperature"
MAPPING_PRECIPITATION = "Precipitation"
MAPPING_PRESSURE = "Pressure"
MAPPING_SOLRAD = "Solar Radiation"
MAPPING_TEMPERATURE = "Temperature"
MAPPING_WINDSPEED = "Windspeed"

# What ``calculate_et_for_day`` refuses a day without. The live estimate reads it
# too, to decline a forecast day this equation would book as zero loss.
DAILY_FORM_FIELDS = (
    MAPPING_DEWPOINT,
    MAPPING_MIN_TEMP,
    MAPPING_MAX_TEMP,
    MAPPING_WINDSPEED,
    MAPPING_PRESSURE,
)

SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_PYETO_COASTAL, default=DEFAULT_COASTAL): vol.Coerce(
            bool
        ),  # is really required, but otherwise the UI shows a * near the checkbox
        vol.Required(
            CONF_PYETO_SOLRAD_BEHAVIOR, default=DEFAULT_SOLRAD_BEHAVIOR
        ): vol.Coerce(SOLRAD_behavior),
        vol.Optional(
            CONF_PYETO_FORECAST_DAYS, default=DEFAULT_FORECAST_DAYS
        ): vol.Coerce(int),
    }
)


class PyETO(SmartIrrigationCalculationModule):
    """Calculation module for estimating evapotranspiration using the PyETO method."""

    def __init__(self, hass: HomeAssistant | None, description, config: dict) -> None:
        """Initialize the PyETO calculation module with Home Assistant context, description, and configuration.

        Args:
            hass: The Home Assistant instance or None.
            description: Description of the calculation module.
            config: Configuration dictionary for the module.

        """
        if config:
            if (
                CONF_PYETO_FORECAST_DAYS in config
                and not isinstance(config[CONF_PYETO_FORECAST_DAYS], int)
                and not config[CONF_PYETO_FORECAST_DAYS].isnumeric()
            ):
                config[CONF_PYETO_FORECAST_DAYS] = DEFAULT_FORECAST_DAYS

        super().__init__(
            name="PyETO",
            description=description,
            schema=SCHEMA,
            config=config,
        )
        self._hass = hass
        self._latitude = hass.config.as_dict().get(CONF_LATITUDE)
        self._elevation = hass.config.as_dict().get(CONF_ELEVATION)
        self._coastal = DEFAULT_COASTAL
        self.forecast_days = DEFAULT_FORECAST_DAYS
        self._solrad_behavior = solrad_behavior_value(DEFAULT_SOLRAD_BEHAVIOR)
        if config:
            self._coastal = config.get(CONF_PYETO_COASTAL, DEFAULT_COASTAL)
            self._solrad_behavior = solrad_behavior_value(
                config.get(CONF_PYETO_SOLRAD_BEHAVIOR, DEFAULT_SOLRAD_BEHAVIOR)
            )
            self.forecast_days = config.get(
                CONF_PYETO_FORECAST_DAYS, DEFAULT_FORECAST_DAYS
            )
            if not isinstance(self.forecast_days, int):
                try:
                    self.forecast_days = int(self.forecast_days)
                except ValueError:
                    self.forecast_days = DEFAULT_FORECAST_DAYS

    # Field descriptions shown as hints in the Modules settings UI
    _FIELD_DESCRIPTIONS = {
        CONF_PYETO_COASTAL: (
            "Enable if the weather station is located near a coast or large body of water. "
            "Affects how atmospheric humidity is estimated."
        ),
        CONF_PYETO_SOLRAD_BEHAVIOR: (
            "How solar radiation is estimated when it is not directly measured by a sensor."
        ),
        CONF_PYETO_FORECAST_DAYS: (
            "Number of future days to include in the ET calculation. "
            "0 = current weather only (recommended — no extra API calls). "
            "Values > 0 average today's ET with forecasted ET for upcoming days "
            "(up to 4 days via the OWM free tier)."
        ),
    }

    def schema_serialized(self):
        """Return serialized schema with field descriptions injected."""
        items = super().schema_serialized() or []
        for item in items:
            desc = self._FIELD_DESCRIPTIONS.get(item.get("name", ""))
            if desc:
                item["description"] = desc
        return items

    def calculate(
        self,
        weather_data,
        forecast_data,
        *,
        day=None,
        forecast_first_day=None,
        warn_on_clamp=True,
    ) -> float:
        """Calculate the average evapotranspiration delta for the given weather and forecast data.

        Args:
            weather_data: Dictionary containing the weather data for ``day``.
            forecast_data: List of dictionaries containing forecasted weather data for upcoming days.
            day: calendar day ``weather_data`` belongs to, as a ``datetime.date``.
                See :meth:`calculate_et_for_day`.
            forecast_first_day: calendar day of ``forecast_data[0]``; entry ``x``
                is priced ``x`` days later. Defaults to the day after ``day``,
                or to tomorrow when no ``day`` is given.
            warn_on_clamp: whether a solar-radiation clamp may warn the user.
                See :meth:`calculate_et_for_day`.

        Returns:
            The mean evapotranspiration delta as a float.

        """
        delta = 0.0
        deltas = []
        if forecast_data is None:
            forecast_data = []
        # Resolve the day once, so weather and forecast share one "today" even
        # if this call straddles midnight.
        if day is None:
            day = datetime.date.today()
        if forecast_first_day is None:
            forecast_first_day = day + datetime.timedelta(days=1)
        if weather_data:
            deltas.append(
                self.calculate_et_for_day(
                    weather_data, day=day, warn_on_clamp=warn_on_clamp
                )
            )
            # loop over the forecast days
            for x in range(self.forecast_days):
                _LOGGER.debug(
                    "[pyETO: calculate_et_for_day] calculating delta for forecast day: %s",
                    x,
                )
                if len(forecast_data) - 1 >= x:
                    deltas.append(
                        self.calculate_et_for_day(
                            forecast_data[x],
                            day=forecast_first_day + datetime.timedelta(days=x),
                            warn_on_clamp=warn_on_clamp,
                        )
                    )
        # return average of the collected deltas
        _LOGGER.debug("[pyETO: calculate_et_for_day] collected deltas: %s", deltas)
        if deltas:
            delta = mean(deltas)
            _LOGGER.debug("[pyETO: calculate]: mean of deltas returned: %s", delta)
        return delta

    def calculate_et_for_day(self, weather_data, *, day=None, warn_on_clamp=True):
        """Calculate the evapotranspiration delta for a single day's weather data.

        Args:
            weather_data: Dictionary containing weather data for the day..
            day: calendar day the weather belongs to, as a ``datetime.date``.
                Its day of the year sets the solar declination and with it the
                extraterrestrial and clear-sky radiation. Without a day the
                current date is used.
            warn_on_clamp: whether a solar-radiation clamp may warn the user.
                The clamp itself always applies; only the warning is suppressed.
                Off for the read-only live estimate, which runs this equation
                every minute per zone over a window that may be entirely daylight
                and would therefore warn about a sensor on every refresh. The
                once-only flag is deliberately left UNSET when this is off,
                because the estimate and the daily calculation share one cached
                module instance -- consuming it here would silence the
                calculation's own warning, which is the one that means something.

        Returns:
            The evapotranspiration delta as a float.

        """
        # _LOGGER.debug("[pyETO: calculate_et_for_day] weather_data: %s", weather_data)
        if weather_data:
            tdew = weather_data.get(MAPPING_DEWPOINT)
            temp_c_min = weather_data.get(MAPPING_MIN_TEMP)
            temp_c_max = weather_data.get(MAPPING_MAX_TEMP)
            wind_m_s = weather_data.get(MAPPING_WINDSPEED)
            atmos_pres = weather_data.get(MAPPING_PRESSURE)
            sol_rad = weather_data.get(MAPPING_SOLRAD)
            if all(weather_data.get(field) is not None for field in DAILY_FORM_FIELDS):
                if day is None:
                    day = datetime.date.today()
                day_of_year = day.timetuple().tm_yday

                sha = sunset_hour_angle(deg2rad(self._latitude), sol_dec(day_of_year))
                daylight_hoursvar = daylight_hours(sha)

                ird = inv_rel_dist_earth_sun(day_of_year)
                et_radvar = et_rad(
                    deg2rad(self._latitude), sol_dec(day_of_year), sha, ird
                )
                _LOGGER.debug("[pyETO: calculate_et_for_day] et_radvar: %s", et_radvar)
                cs_radvar = cs_rad(self._elevation, et_radvar)
                _LOGGER.debug("[pyETO: calculate_et_for_day] cs_radvar: %s", cs_radvar)
                _LOGGER.debug(
                    "[pyETO: calculate_et_for_day]: solrad_behavior: %s and sol_rad: %s",
                    self._solrad_behavior,
                    sol_rad,
                )
                # if we need to calculate solar_radiation we need to override the value passed in.
                if (
                    self._solrad_behavior != SOLRAD_behavior.DontEstimate.value
                    or sol_rad is None
                ):
                    if self._solrad_behavior == SOLRAD_behavior.EstimateFromTemp.value:
                        sol_rad = sol_rad_from_t(
                            et_radvar, cs_radvar, temp_c_min, temp_c_max, self._coastal
                        )
                        _LOGGER.debug(
                            "[pyETO: calculate_et_for_day] estimated sol_rad from temp: %s",
                            sol_rad,
                        )
                    elif (
                        self._solrad_behavior
                        == SOLRAD_behavior.EstimateFromSunHoursAndTemperature.value
                    ):
                        sol_rad = (
                            sol_rad_from_t(
                                et_radvar,
                                cs_radvar,
                                temp_c_min,
                                temp_c_max,
                                self._coastal,
                            )
                            + sol_rad_from_sun_hours(
                                daylight_hoursvar, 0.8 * daylight_hoursvar, et_radvar
                            )
                        ) / 2
                        _LOGGER.debug(
                            "[pyETO: calculate_et_for_day] estimated sol_rad from sunhours and temperature: %s",
                            sol_rad,
                        )
                    else:
                        # this is the default behavior for version < 0.0.50
                        sol_rad = sol_rad_from_sun_hours(
                            daylight_hoursvar, 0.8 * daylight_hoursvar, et_radvar
                        )
                        _LOGGER.debug(
                            "[pyETO: calculate_et_for_day] estimated sol_rad from sunhours: %s",
                            sol_rad,
                        )
                # FAO-56 safety clamp: incoming solar radiation can never exceed
                # clear-sky radiation (Rs <= Rso). A measured "Solar Radiation"
                # sensor in the wrong unit (e.g. W/m2 read as MJ/day/m2) would
                # otherwise blow the net radiation — and ET — up several-fold.
                # Clamp to clear-sky and warn once so the bad input is visible.
                if sol_rad is not None and cs_radvar and sol_rad > cs_radvar:
                    if warn_on_clamp and not getattr(
                        self, "_warned_solrad_clamp", False
                    ):
                        self._warned_solrad_clamp = True
                        _LOGGER.warning(
                            "Solar radiation %.1f MJ/day/m2 exceeds the physical "
                            "clear-sky maximum %.1f MJ/day/m2 and was clamped. "
                            "Check the Solar Radiation sensor's unit in the sensor "
                            "group (a W/m2 sensor configured as MJ/day/m2 is the "
                            "usual cause), or switch the PyETO solar-radiation "
                            "behaviour to an 'estimate' option.",
                            sol_rad,
                            cs_radvar,
                        )
                    sol_rad = cs_radvar
                _LOGGER.debug(
                    "[pyETO: calculate_et_for_day] sol_rad passed to net_in_sol_radvar: %s",
                    sol_rad,
                )
                net_in_sol_radvar = net_in_sol_rad(sol_rad=sol_rad, albedo=0.23)
                _LOGGER.debug(
                    "[pyETO: calculate_et_for_day] net_in_sol_radvar: %s",
                    net_in_sol_radvar,
                )
                avp = avp_from_tdew(tdew)
                _LOGGER.debug(
                    "[pyETO: calculate_et_for_day] avp_from_tdew: %s for tdew %s",
                    avp,
                    tdew,
                )
                net_out_lw_radvar = net_out_lw_rad(
                    convert.celsius2kelvin(temp_c_min),
                    convert.celsius2kelvin(temp_c_max),
                    sol_rad,
                    cs_radvar,
                    avp,
                )
                _LOGGER.debug(
                    "[pyETO: calculate_et_for_day] net_out_lw_radvar: %s",
                    net_out_lw_radvar,
                )
                net_radvar = net_rad(net_in_sol_radvar, net_out_lw_radvar)
                _LOGGER.debug(
                    "[pyETO: calculate_et_for_day] net_radvar: %s", net_radvar
                )
                # experiment in v0.0.71: do not pass in day temperature (temp_c) but instead the average of temp_max and temp_min
                # see https://github.com/jeroenterheerdt/HAsmartirrigation/issues/70
                temp_c = (temp_c_min + temp_c_max) / 2.0

                eto = fao56_penman_monteith(
                    net_rad=net_radvar,
                    t=convert.celsius2kelvin(temp_c),
                    ws=wind_m_s,
                    svp=svp_from_t(temp_c),
                    avp=avp,
                    delta_svp=delta_svp(temp_c),
                    psy=psy_const(
                        atmos_pres / 10
                    ),  # value stored is in hPa, but needs to be provided in kPa
                )
                _LOGGER.debug("[pyETO: calculate_et_for_day] eto: %s", eto)
                if eto is None:
                    eto = 0
                delta = -eto

                _LOGGER.debug("[pyETO: calculate_et_for_day] delta returned: %s", delta)
                return delta
            # some data is missing, let's check and log what is missing
            _LOGGER.warning(
                "[pyETO: calculate_et_for_day] cannot calculate as some data is missing!"
            )
            if tdew is None:
                _LOGGER.warning(
                    "[pyETO: calculate_et_for_day] missing %s", MAPPING_DEWPOINT
                )
            if temp_c_min is None:
                _LOGGER.warning(
                    "[pyETO: calculate_et_for_day] missing %s", MAPPING_MIN_TEMP
                )
            if temp_c_max is None:
                _LOGGER.warning(
                    "[pyETO: calculate_et_for_day] missing %s", MAPPING_MAX_TEMP
                )
            if wind_m_s is None:
                _LOGGER.warning(
                    "[pyETO: calculate_et_for_day] missing %s", MAPPING_WINDSPEED
                )
            if atmos_pres is None:
                _LOGGER.warning(
                    "[pyETO: calculate_et_for_day] missing %s", MAPPING_PRESSURE
                )
        _LOGGER.debug("[pyETO: calculate_et_for_day] returned: 0!")
        return 0
