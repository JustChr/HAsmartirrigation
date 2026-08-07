"""A clamp warning has to keep meaning something.

PyETO clamps incoming solar radiation against the clear-sky maximum and warns
once, because the usual cause is a sensor configured in the wrong unit. The
daily calculation avoids tripping it spuriously by structure: it skips the daily
equation entirely whenever it will not use the answer.

The live estimate cannot do that -- mirroring the commit means running the daily
equation, every minute per zone, over a window that may be entirely daylight and
therefore legitimately above a DAILY ceiling. Left alone it would warn about a
sensor on every refresh.

Suppressing the log is only half of it. The estimate and the calculation share
one cached module instance, and the warning is once-only, so an estimate that
tripped the flag would silence the calculation's warning permanently -- turning a
noisy bug into a silent one.
"""

import logging

from custom_components.smart_irrigation.calcmodules.pyeto import (
    PyETO,
    SOLRAD_behavior,
)
from custom_components.smart_irrigation.const import (
    CONF_PYETO_FORECAST_DAYS,
    CONF_PYETO_SOLRAD_BEHAVIOR,
)

# Far above any clear-sky maximum: a W/m2 sensor read as MJ/day/m2, which is the
# mistake the warning exists to surface.
ABSURD_SOLRAD = 900.0


def _module(hass):
    return PyETO(
        hass,
        description="",
        config={
            # Measured radiation, so the value handed in is the one used and the
            # clamp is reachable at all.
            CONF_PYETO_SOLRAD_BEHAVIOR: SOLRAD_behavior.DontEstimate.value,
            CONF_PYETO_FORECAST_DAYS: 0,
        },
    )


def _weather():
    return {
        "Dewpoint": 12.0,
        "Minimum Temperature": 14.0,
        "Maximum Temperature": 28.0,
        "Windspeed": 1.5,
        "Pressure": 977.0,
        "Solar Radiation": ABSURD_SOLRAD,
    }


def _clamp_warnings(records):
    return [r for r in records if "clear-sky maximum" in r.getMessage()]


class TestTheEstimatePath:
    def test_it_does_not_warn(self, hass, caplog):
        modinst = _module(hass)

        with caplog.at_level(logging.WARNING):
            modinst.calculate(_weather(), None, warn_on_clamp=False)

        assert _clamp_warnings(caplog.records) == []

    def test_it_still_clamps(self, hass):
        """Only the warning is suppressed. An unclamped absurd radiation would
        blow the net radiation up several-fold and with it the live bucket."""
        modinst = _module(hass)

        suppressed = modinst.calculate(_weather(), None, warn_on_clamp=False)
        warned = modinst.calculate(_weather(), None)

        assert suppressed == warned

    def test_it_leaves_the_calculation_s_warning_intact(self, hass, caplog):
        """The two share one cached module instance and the warning is
        once-only. This is the assertion that matters: an estimate refreshing
        every minute would otherwise consume the flag long before the nightly
        calculation ever reached it."""
        modinst = _module(hass)

        for _ in range(5):
            modinst.calculate(_weather(), None, warn_on_clamp=False)
        with caplog.at_level(logging.WARNING):
            modinst.calculate(_weather(), None)

        assert len(_clamp_warnings(caplog.records)) == 1


class TestTheCalculationPath:
    def test_it_warns_once(self, hass, caplog):
        modinst = _module(hass)

        with caplog.at_level(logging.WARNING):
            modinst.calculate(_weather(), None)
            modinst.calculate(_weather(), None)

        assert len(_clamp_warnings(caplog.records)) == 1

    def test_a_plausible_reading_warns_about_nothing(self, hass, caplog):
        modinst = _module(hass)
        weather = _weather()
        weather["Solar Radiation"] = 20.0

        with caplog.at_level(logging.WARNING):
            modinst.calculate(weather, None)

        assert _clamp_warnings(caplog.records) == []
