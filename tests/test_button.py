"""Per-zone button registration.

Guards the fix where per-zone entities (buttons/numbers/binary_sensors) were
missing because the existing-zone `_platform_loaded` replay was fired by the
sensor platform before the others had subscribed. The button platform must add
BOTH per-zone buttons (irrigate-now + reset-usage) when a zone is registered.
"""

from unittest.mock import Mock

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.button import async_setup_entry


async def test_register_entity_adds_both_per_zone_buttons(hass: HomeAssistant) -> None:
    hass.data[const.DOMAIN] = {}
    entry = Mock()
    entry.async_on_unload = Mock()

    added: list = []
    await async_setup_entry(hass, entry, lambda ents: added.extend(ents))

    # A zone is registered (the `_platform_loaded` → `_register_entity` replay).
    async_dispatcher_send(
        hass,
        const.DOMAIN + "_register_entity",
        {const.ZONE_ID: 1, const.ZONE_NAME: "Garden"},
    )
    await hass.async_block_till_done()

    zone_button_suffixes = {
        e.suffix for e in added if getattr(e, "_zone_id", None) == 1
    }
    assert zone_button_suffixes == {"irrigate_now", "reset_usage"}


async def test_zone_registered_once_only(hass: HomeAssistant) -> None:
    """A second registration for the same zone id does not duplicate buttons."""
    hass.data[const.DOMAIN] = {}
    entry = Mock()
    entry.async_on_unload = Mock()

    added: list = []
    await async_setup_entry(hass, entry, lambda ents: added.extend(ents))

    zone = {const.ZONE_ID: 1, const.ZONE_NAME: "Garden"}
    async_dispatcher_send(hass, const.DOMAIN + "_register_entity", zone)
    async_dispatcher_send(hass, const.DOMAIN + "_register_entity", zone)
    await hass.async_block_till_done()

    zone_buttons = [e for e in added if getattr(e, "_zone_id", None) == 1]
    assert len(zone_buttons) == 2  # not 4
