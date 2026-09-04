"""Keep pre-#120 service calls working after the domain rename (#120).

The rename moves every service from ``smart_irrigation.*`` to
``irrigation_plus.*``. Storage, history and statistics are carried across, but a
service name is not data we own — it is baked into the user's own automations,
scripts and blueprints, and there is nothing in Home Assistant that rewrites
those. Without an alias, upgrade day silently breaks every automation that calls
``smart_irrigation.reset_bucket``: the call raises ``ServiceNotFound``, the
automation aborts mid-sequence, and the only evidence is a log line.

So each of our services is also registered under the old domain, forwarding to
the real one. Two rules make that safe:

* **Never claim a name somebody else owns.** If a DIFFERENT project holds the
  ``smart_irrigation`` domain on this machine, aliasing is exactly the collision
  the rename was meant to remove, so it is skipped entirely — the same gate,
  and for the same reason, as the legacy card shim in ``panel.py``. A service
  already registered under the old domain is left alone even then, because
  ``async_register`` overwrites silently and the loser would be the integration
  that actually owns the name.
* **Aliases are removed on unload**, so a disabled or removed integration does
  not leave phantom services behind.

The alias list is READ BACK from what we registered rather than restated here.
A hand-maintained second list would drift the first time somebody adds a
service and forgets, and the failure would be invisible until a user's
automation hit the missing name.

Deprecation is logged once per service, on first use, at WARNING — enough for a
user to find and fix their automations, quiet enough not to spam a log every
time a schedule fires.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from . import const

_LOGGER = logging.getLogger(__name__)

# Services we have already warned about, so the warning is one per service per
# Home Assistant run rather than one per call.
_WARNED: set[str] = set()

# The forwarders WE registered under the old domain, name -> handler.
#
# The handler, not just the name: "it exists under the old domain and we have
# one by that name" is a different question, and answering it that way would
# tear down a foreign integration's own services on our unload -- both projects
# publish `reset_bucket`. Keeping the object lets removal check identity, so a
# name that has since been taken over by somebody else is left alone.
_ALIASED: dict[str, object] = {}


def plan_service_aliases(ours, existing_legacy) -> list[str]:
    """Which of our service names should be mirrored onto the old domain.

    Pure so it can be exercised without a running Home Assistant. ``ours`` and
    ``existing_legacy`` are the service names registered under the new and the
    old domain respectively.

    A name already present under the old domain is skipped: registering over it
    would silently replace whatever owns it (an upstream install, or our own
    alias from a previous setup) and there is no error to notice.
    """
    return sorted(set(ours) - set(existing_legacy))


def _service_names(hass: HomeAssistant, domain: str) -> list[str]:
    """Service names registered under ``domain``, or [] if there are none."""
    return list((hass.services.async_services() or {}).get(domain, {}) or {})


async def async_register_legacy_service_aliases(hass: HomeAssistant) -> list[str]:
    """Mirror ``irrigation_plus.*`` onto ``smart_irrigation.*``.

    Returns the aliased service names. Never raises: a missing alias costs a
    user their automations, but failing setup over one costs them the whole
    integration.
    """
    from .migrate_domain import foreign_legacy_install

    if await hass.async_add_executor_job(foreign_legacy_install, hass):
        _LOGGER.debug(
            "A different %s integration is installed; not aliasing its services",
            const.LEGACY_DOMAIN,
        )
        return []

    aliased = plan_service_aliases(
        _service_names(hass, const.DOMAIN),
        _service_names(hass, const.LEGACY_DOMAIN),
    )
    for name in aliased:
        handler = _make_forwarder(hass, name)
        hass.services.async_register(const.LEGACY_DOMAIN, name, handler)
        _ALIASED[name] = handler

    if aliased:
        _LOGGER.info(
            "Registered %s compatibility service(s) under %s.* so automations "
            "written before the rename keep working. Repoint them at %s.* — the "
            "aliases will be removed in a future release",
            len(aliased),
            const.LEGACY_DOMAIN,
            const.DOMAIN,
        )
    return aliased


def _make_forwarder(hass: HomeAssistant, name: str):
    """Build the handler that forwards one legacy service call to the real one."""

    async def _forward(call: ServiceCall) -> None:
        if name not in _WARNED:
            _WARNED.add(name)
            _LOGGER.warning(
                "%s.%s is the pre-rename name and is kept only for "
                "compatibility. Update your automations and scripts to call "
                "%s.%s instead",
                const.LEGACY_DOMAIN,
                name,
                const.DOMAIN,
                name,
            )
        # blocking=True so a caller that sequences on this service still gets
        # the ordering it had before the rename, and so an error raised by the
        # real handler propagates to the automation instead of vanishing into a
        # background task.
        await hass.services.async_call(
            const.DOMAIN,
            name,
            dict(call.data),
            blocking=True,
            context=call.context,
        )

    return _forward


def async_remove_legacy_service_aliases(hass: HomeAssistant) -> None:
    """Drop the aliases again on unload.

    Only the forwarders this module registered are removed, matched by identity
    rather than by name. A service under the old domain that belongs to a real
    integration must survive our unload — it was never ours, and removing it
    would break the OTHER project rather than tidy up after this one. Name is
    not enough to tell them apart: both projects publish ``reset_bucket``, and
    ``async_register`` overwrites silently, so the thing sitting under a name we
    once aliased may no longer be the thing we put there.
    """
    registered = (hass.services.async_services() or {}).get(const.LEGACY_DOMAIN, {})
    for name, handler in sorted(_ALIASED.items()):
        if registered.get(name) is handler:
            hass.services.async_remove(const.LEGACY_DOMAIN, name)
    _ALIASED.clear()
    _WARNED.clear()
