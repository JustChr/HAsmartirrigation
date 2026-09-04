"""Options flow handler for the Smart Irrigation integration.

Weather service and location are configured in the integration's own panel
(Setup → Weather & Location), which is the single source of truth — the panel
writes the config-entry options directly and reloads the integration. The HA
options flow no longer duplicates that configuration; it only points the user
to the panel.
"""

from homeassistant import config_entries


class SmartIrrigationOptionsFlowHandler(config_entries.OptionsFlow):
    """Minimal options flow — all configuration lives in the panel now."""

    def __init__(self, config_entry) -> None:  # noqa: D107
        # Nothing to store; configuration happens in the panel.
        pass

    async def async_step_init(self, user_input=None):  # noqa: D102
        return self.async_abort(reason="configure_in_panel")
