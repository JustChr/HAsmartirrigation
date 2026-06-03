"""Weather-service config resolution for the Smart Irrigation integration.

Extracted from async_setup_entry (Phase C8, scoped). The reconciliation of the
weather-service settings — stored config defaults, then the config entry's
``data``, then its ``options`` ("options always win", issue #683), plus the
use_owm and legacy-single-key migrations — was ~80 lines of imperative
hass.data writes. Pulling it into one pure function makes it unit-testable and a
single source of truth.

This intentionally does NOT change where the result is stored (still
hass.data[const.DOMAIN]); a full move to entry.runtime_data is a separate,
larger step.
"""

from . import const


def resolve_weather_config(
    store_config: dict, entry, existing: dict | None = None
) -> dict:
    """Resolve the effective weather-service config for a config entry.

    Precedence (lowest to highest): stored config defaults -> entry.data ->
    entry.options. Returns a dict of the weather-service config keys to apply to
    hass.data[const.DOMAIN] (caller does ``.update(...)``).

    Args:
        store_config: the dict from ``store.async_get_config()``.
        entry: the config entry (uses ``.data`` and ``.options`` mappings).
        existing: the current hass.data[const.DOMAIN] (optional). Only consulted
            for the legacy-key "is the per-service slot already set?" check, to
            preserve the original behavior across reloads where hass.data
            persists. Defaults to empty.

    """
    existing = existing or {}
    data = entry.data
    options = entry.options

    result: dict = {
        const.CONF_USE_WEATHER_SERVICE: store_config.get(
            const.CONF_USE_WEATHER_SERVICE, const.CONF_DEFAULT_USE_WEATHER_SERVICE
        ),
        const.CONF_WEATHER_SERVICE: store_config.get(
            const.CONF_WEATHER_SERVICE, const.CONF_DEFAULT_WEATHER_SERVICE
        ),
    }

    # entry.data overrides stored defaults
    if const.CONF_USE_WEATHER_SERVICE in data:
        result[const.CONF_USE_WEATHER_SERVICE] = data.get(
            const.CONF_USE_WEATHER_SERVICE
        )
        if result[const.CONF_USE_WEATHER_SERVICE]:
            if const.CONF_WEATHER_SERVICE in data:
                result[const.CONF_WEATHER_SERVICE] = data.get(
                    const.CONF_WEATHER_SERVICE
                )
            if const.CONF_WEATHER_SERVICE_API_KEY in data:
                result[const.CONF_WEATHER_SERVICE_API_KEY] = data.get(
                    const.CONF_WEATHER_SERVICE_API_KEY
                ).strip()
            result[const.CONF_WEATHER_SERVICE_API_VERSION] = data.get(
                const.CONF_WEATHER_SERVICE_API_VERSION
            )

    # legacy OWM config migration
    if data.get("use_owm") and "owm_api_key" in data:
        result[const.CONF_WEATHER_SERVICE_API_KEY] = data["owm_api_key"]

    # entry.options always win (most recent user-configured values; issue #683)
    if const.CONF_USE_WEATHER_SERVICE in options:
        result[const.CONF_USE_WEATHER_SERVICE] = options.get(
            const.CONF_USE_WEATHER_SERVICE
        )
        if result[const.CONF_USE_WEATHER_SERVICE]:
            if const.CONF_WEATHER_SERVICE in options:
                result[const.CONF_WEATHER_SERVICE] = options.get(
                    const.CONF_WEATHER_SERVICE
                )
            # per-service API keys
            for key_const in (const.CONF_OWM_API_KEY, const.CONF_PW_API_KEY):
                if key_const in options:
                    stored = options.get(key_const)
                    result[key_const] = stored.strip() if stored else None
            # promote a legacy single-slot key to the per-service slot
            if const.CONF_WEATHER_SERVICE_API_KEY in options:
                legacy_key = options.get(const.CONF_WEATHER_SERVICE_API_KEY)
                if legacy_key:
                    legacy_key = legacy_key.strip()
                    result[const.CONF_WEATHER_SERVICE_API_KEY] = legacy_key
                    svc = result.get(const.CONF_WEATHER_SERVICE)
                    if svc == const.CONF_WEATHER_SERVICE_OWM and not (
                        result.get(const.CONF_OWM_API_KEY)
                        or existing.get(const.CONF_OWM_API_KEY)
                    ):
                        result[const.CONF_OWM_API_KEY] = legacy_key
                    elif svc == const.CONF_WEATHER_SERVICE_PW and not (
                        result.get(const.CONF_PW_API_KEY)
                        or existing.get(const.CONF_PW_API_KEY)
                    ):
                        result[const.CONF_PW_API_KEY] = legacy_key
            if const.CONF_WEATHER_SERVICE_API_VERSION in options:
                result[const.CONF_WEATHER_SERVICE_API_VERSION] = options.get(
                    const.CONF_WEATHER_SERVICE_API_VERSION
                )
        else:
            result[const.CONF_WEATHER_SERVICE] = None
            result[const.CONF_WEATHER_SERVICE_API_KEY] = None
            result[const.CONF_WEATHER_SERVICE_API_VERSION] = None

    return result
