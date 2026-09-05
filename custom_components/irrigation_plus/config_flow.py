"""Config flow for the Irrigation Plus integration."""

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from . import const
from .helpers import CannotConnect, InvalidAuth, validate_api_key
from .migrate_domain import async_legacy_config_seed, async_legacy_install_present
from .options_flow import SmartIrrigationOptionsFlowHandler


class SmartIrrigationConfigFlow(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Config flow for SmartIrrigation."""

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialize the SmartIrrigationConfigFlow instance."""
        self._errors = {}
        self._name = ""
        self._use_weather_service = False
        self._weather_service_api_key = ""
        self._weather_service = ""
        self._migrate_offered = False
        # not needed anymore because versions are hardcoded
        # self._forecasting_api_version = 3.0

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        self._errors = {}
        # Only a single instance of the integration
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # Offer to import a pre-#120 "Smart Irrigation" install before asking
        # the user to configure anything from scratch (#120). Only on the first
        # pass: once they have answered the migrate step it must not reappear.
        if user_input is None and not self._migrate_offered:
            self._migrate_offered = True
            if await async_legacy_install_present(self.hass):
                return await self.async_step_migrate()

        if user_input is not None:
            try:
                await self._check_unique(user_input[const.CONF_INSTANCE_NAME])
                self._name = user_input[const.CONF_INSTANCE_NAME]
                self._use_weather_service = user_input[const.CONF_USE_WEATHER_SERVICE]
                if not self._use_weather_service:
                    # else create the entry right away
                    return self.async_create_entry(title=const.NAME, data=user_input)
                return await self._show_step_1(user_input)
            except NotUnique:
                self._errors["base"] = "name"
        return await self._show_step_user(user_input)

    async def async_step_migrate(self, user_input=None):
        """Offer to carry a pre-#120 Smart Irrigation install over (#120).

        Seeds the weather settings and the API key into the new entry's data AT
        CREATION. Merging them afterwards with ``async_update_entry`` triggers a
        reload that drops them — altmenorg hit exactly that doing this rename,
        and said so on #120.
        """
        if user_input is not None:
            if not user_input.get(const.CONF_MIGRATED_FROM_LEGACY, True):
                # Declined: fall through to a normal, empty set-up. The old
                # storage file stays on disk, untouched and unused.
                return await self._show_step_user(None)

            seed = await async_legacy_config_seed(self.hass)
            seed[const.CONF_MIGRATED_FROM_LEGACY] = True
            seed.setdefault(const.CONF_INSTANCE_NAME, const.NAME)
            seed.setdefault(const.CONF_USE_WEATHER_SERVICE, False)
            await self._check_unique(seed[const.CONF_INSTANCE_NAME])
            return self.async_create_entry(title=const.NAME, data=seed)

        return self.async_show_form(
            step_id="migrate",
            data_schema=vol.Schema(
                {
                    vol.Required(const.CONF_MIGRATED_FROM_LEGACY, default=True): bool,
                }
            ),
            errors=self._errors,
        )

    async def _show_step_user(self, user_input):
        return self.async_show_form(
            step_id="user",
            description_placeholders={"docs": const.DOCUMENTATION_URL},
            data_schema=vol.Schema(
                {
                    vol.Required(const.CONF_INSTANCE_NAME, default=const.NAME): str,
                    vol.Required(const.CONF_USE_WEATHER_SERVICE, default=True): bool,
                }
            ),
            errors=self._errors,
        )

    async def async_step_step1(self, user_input=None):
        """Handle a step 1."""

        self._errors = {}
        if user_input is not None:
            try:
                self._weather_service = user_input[const.CONF_WEATHER_SERVICE].strip()
                raw_key = user_input.get(const.CONF_WEATHER_SERVICE_API_KEY) or ""
                self._weather_service_api_key = raw_key.strip()
                user_input[const.CONF_USE_WEATHER_SERVICE] = self._use_weather_service
                user_input[const.CONF_INSTANCE_NAME] = self._name
                user_input[const.CONF_WEATHER_SERVICE_API_KEY] = (
                    self._weather_service_api_key
                )
                await validate_api_key(
                    self.hass, self._weather_service, self._weather_service_api_key
                )
                return self.async_create_entry(title=const.NAME, data=user_input)

            except InvalidAuth:
                self._errors["base"] = "auth"
            except CannotConnect:
                self._errors["base"] = "auth"

            return await self._show_step_1(user_input)
        return await self._show_step_1(user_input)

    async def _show_step_1(self, user_input):
        return self.async_show_form(
            step_id="step1",
            description_placeholders={"docs": const.DOCUMENTATION_URL},
            data_schema=vol.Schema(
                {
                    vol.Required(const.CONF_WEATHER_SERVICE): selector(
                        {"select": {"options": const.CONF_WEATHER_SERVICES}}
                    ),
                    vol.Optional(const.CONF_WEATHER_SERVICE_API_KEY, default=""): str,
                }
            ),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return SmartIrrigationOptionsFlowHandler(config_entry)

    async def _check_unique(self, thename):
        """Test if the specified name is not already claimed."""
        await self.async_set_unique_id(thename)
        self._abort_if_unique_id_configured()


class NotUnique(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
