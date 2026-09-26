"""Open or close an on/off entity the way its domain expects (#170).

Every entity Irrigation Plus switches itself — a zone's linked entity, the
master / pump, a distributor inlet — can be a ``switch``, an ``input_boolean``
or a ``valve``. The first two take ``turn_on`` / ``turn_off``; the ``valve``
domain has no such actions, only ``open_valve`` / ``close_valve``, so
``valve.turn_on`` raises ``ServiceNotFound`` and the zone never waters.

One rule, one place. The master and the distributor each carried their own
copy of the valve branch while the zone runner built ``<domain>.turn_on`` at
ten call sites with none, which is how every classic zone linked to a
``valve.*`` entity came to fail. Anything that actuates an entity goes through
here.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant

VALVE_DOMAIN = "valve"


def actuation_service(entity_id: str, on: bool) -> tuple[str, str]:
    """``(domain, service)`` that opens (``on``) or closes the entity."""
    domain = entity_id.split(".", 1)[0]
    if domain == VALVE_DOMAIN:
        return domain, "open_valve" if on else "close_valve"
    return domain, "turn_on" if on else "turn_off"


async def async_actuate(hass: HomeAssistant, entity_id: str, on: bool) -> None:
    """Open (``on``) or close the entity with its domain's own action."""
    domain, service = actuation_service(entity_id, on)
    await hass.services.async_call(domain, service, {"entity_id": entity_id})
