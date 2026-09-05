"""Weather-service config resolution for the Irrigation Plus integration.

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

# The per-service key slots, in the order the panel writes them. Named once so
# the ``data`` and ``options`` passes cannot drift apart — they did: only
# ``options`` read these, which meant a #120 migration seeded them into a new
# entry's ``data`` and this function then dropped them on the floor.
_PER_SERVICE_KEY_SLOTS = (
    const.CONF_OWM_API_KEY,
    const.CONF_PW_API_KEY,
    const.CONF_MET_API_KEY,
)

_SERVICE_KEY_SLOT = {
    const.CONF_WEATHER_SERVICE_OWM: const.CONF_OWM_API_KEY,
    const.CONF_WEATHER_SERVICE_PW: const.CONF_PW_API_KEY,
    const.CONF_WEATHER_SERVICE_MET: const.CONF_MET_API_KEY,
}


def _apply_api_keys(result: dict, source: dict, existing: dict) -> None:
    """Fold every API key slot present in ``source`` into ``result``, in place.

    Applied to ``entry.data`` and then to ``entry.options``, so the later call
    overrides the earlier one and "options always win" still holds.

    Promoting the legacy single-key slot into the per-service slot is part of
    this, not a separate step: ``result[const.CONF_WEATHER_SERVICE]`` is already
    resolved for whichever pass is running, so the promotion follows the service
    that pass selected. ``existing`` is consulted so a key already live in
    hass.data (a reload keeps it) is not overwritten by an older legacy value.
    """
    for slot in _PER_SERVICE_KEY_SLOTS:
        if slot in source:
            stored = source.get(slot)
            result[slot] = stored.strip() if stored else None

    if const.CONF_WEATHER_SERVICE_API_KEY not in source:
        return
    legacy_key = source.get(const.CONF_WEATHER_SERVICE_API_KEY)
    if not legacy_key:
        return
    legacy_key = legacy_key.strip()
    result[const.CONF_WEATHER_SERVICE_API_KEY] = legacy_key
    slot = _SERVICE_KEY_SLOT.get(result.get(const.CONF_WEATHER_SERVICE))
    if slot and not (result.get(slot) or existing.get(slot)):
        result[slot] = legacy_key


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
            # Reads the per-service slots too. A #120 migration seeds the old
            # entry's merged weather settings into the NEW entry's `data`, and
            # the panel only ever wrote the key to a per-service slot — so
            # without this the migrated user's key is silently dropped and
            # weather starts disabled.
            _apply_api_keys(result, data, existing)
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
            # per-service API keys, plus promotion of the legacy single slot
            _apply_api_keys(result, options, existing)
            if const.CONF_WEATHER_SERVICE_API_VERSION in options:
                result[const.CONF_WEATHER_SERVICE_API_VERSION] = options.get(
                    const.CONF_WEATHER_SERVICE_API_VERSION
                )
        else:
            result[const.CONF_WEATHER_SERVICE] = None
            result[const.CONF_WEATHER_SERVICE_API_KEY] = None
            result[const.CONF_WEATHER_SERVICE_API_VERSION] = None

    return result
