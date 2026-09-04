"""The Passthrough module for Irrigation Plus Integration."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant

from custom_components.irrigation_plus.calcmodules.calcmodule import (
    SmartIrrigationCalculationModule,
)

_LOGGER = logging.getLogger(__name__)
SCHEMA = vol.Schema({})


class Passthrough(SmartIrrigationCalculationModule):
    """Calculation module that returns the input evapotranspiration value unchanged."""

    def __init__(self, hass: HomeAssistant | None, description, config=None) -> None:
        """Initialize the Passthrough calculation module.

        Args:
            hass: Home Assistant instance or None.
            description: Description of the calculation module.
            config: Optional configuration dictionary.

        """
        if config is None:
            config = {}
        super().__init__(
            name="Passthrough", description=description, schema=SCHEMA, config=config
        )
        self._hass = hass

    def calculate(self, et_data=None):
        """Return the input evapotranspiration value unchanged as a float.

        Args:
            et_data: The evapotranspiration data to pass through.

        Returns:
            The evapotranspiration value as a float, or 0 if input is invalid or None.

        """
        # Fix: Check specifically for None, as 0.0 is valid data but evaluates to False
        if et_data is not None:
            # Ensure the value is a float before returning
            try:
                return float(et_data)
            except (ValueError, TypeError):
                _LOGGER.error(
                    "Invalid non-numeric Evapotranspiration data received by Passthrough module: %s",
                    et_data,
                )
                # Return 0 if conversion fails, consistent with the original else block's return
                return 0
        else:
            _LOGGER.error(
                "No Evapotranspiration data specified (et_data is None) for Passthrough module"
            )
            return 0
