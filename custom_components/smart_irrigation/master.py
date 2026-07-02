"""Master switch / pump control.

Turns a shared master (pump / main valve) on before the first zone of a watering
cycle and optionally off after the last zone's planned end. Fully optional: with
no ``master_entity`` configured every method is a no-op, so existing behaviour is
byte-identical. The master is actuated via ``homeassistant.turn_on`` /
``turn_off`` (works for switch / valve / input_boolean).

Kicker (optional): a pressure-controlled pump may not restart promptly when it is
merely powered; pulsing it off -> pause -> on forces it to run. Then a settle
delay lets pressure build before the first valve opens.
"""

from __future__ import annotations

import asyncio
import datetime
import logging

from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

from . import const

_LOGGER = logging.getLogger(__name__)


class MasterMixin:
    """Master (pump) sequencing. Mixed into SmartIrrigationCoordinator."""

    def _master_now(self) -> datetime.datetime:
        return dt_util.utcnow()

    async def _master_sleep(self, seconds) -> None:
        await asyncio.sleep(max(0.0, float(seconds or 0)))

    def _master_cfg(self):
        return self.store.config

    def _master_entity(self):
        return getattr(self._master_cfg(), const.CONF_MASTER_ENTITY, None)

    def _master_configured(self) -> bool:
        # A valid master is a string entity_id; anything else (None, or a test
        # double's Mock attribute) means "not configured" -> every hook no-ops.
        entity = self._master_entity()
        return isinstance(entity, str) and bool(entity)

    async def _master_turn(self, on: bool) -> None:
        entity = self._master_entity()
        if not isinstance(entity, str) or not entity:
            return
        # valve.* entities use open_valve / close_valve, NOT turn_on / turn_off:
        # homeassistant.turn_on does no domain mapping and would silently no-op on
        # a valve, leaving the master closed while zones water.
        if entity.split(".", 1)[0] == "valve":
            await self.hass.services.async_call(
                "valve",
                "open_valve" if on else "close_valve",
                {"entity_id": entity},
            )
            return
        await self.hass.services.async_call(
            "homeassistant",
            "turn_on" if on else "turn_off",
            {"entity_id": entity},
        )

    async def async_master_begin_cycle(self) -> None:
        """Ensure the master is on before the first zone fires.

        Idempotent within a cycle: a second call while already on does nothing
        (no re-kick, no re-settle). The on-flag is cleared at the cycle end so the
        next cycle re-arms — a stay-on pump is re-kicked every cycle.
        """
        if not self._master_configured() or getattr(self, "_master_on", False):
            return
        # Set BEFORE the awaits below so a concurrent begin_cycle can't double-kick.
        self._master_on = True
        cfg = self._master_cfg()
        if getattr(cfg, const.CONF_MASTER_KICK_ENABLED, False):
            await self._master_turn(False)
            await self._master_sleep(
                getattr(cfg, const.CONF_MASTER_KICK_PAUSE_SECONDS, 1.0)
            )
        await self._master_turn(True)
        settle = getattr(cfg, const.CONF_MASTER_SETTLE_SECONDS, 10)
        if float(settle or 0) > 0:
            await self._master_sleep(settle)

    def _master_note_run(self, seconds: float) -> None:
        """Record the latest expected cycle end (now + seconds)."""
        if not self._master_configured():
            return
        deadline = self._master_now() + datetime.timedelta(
            seconds=max(0.0, float(seconds or 0))
        )
        cur = getattr(self, "_master_off_deadline", None)
        if cur is None or deadline > cur:
            self._master_off_deadline = deadline

    async def async_master_schedule_off(self) -> None:
        """Schedule the cycle end: clear the on-flag (so the next cycle re-arms /
        re-kicks) and, iff master_off_after is set, power the master off.

        Overlap-safe: fires only when the (possibly extended) deadline has passed;
        a later run pushes the deadline out and the timer reschedules instead of
        ending the cycle under an active run.
        """
        if not self._master_configured():
            return
        deadline = getattr(self, "_master_off_deadline", None)
        if deadline is None:
            return
        cancel = getattr(self, "_master_off_cancel", None)
        if cancel:
            cancel()
            self._master_off_cancel = None
        delay = max(0.0, (deadline - self._master_now()).total_seconds())

        async def _fire(_now=None):
            self._master_off_cancel = None
            dl = getattr(self, "_master_off_deadline", None)
            if dl is not None and self._master_now() < dl:
                # A later run extended the cycle — reschedule, don't end it yet.
                await self.async_master_schedule_off()
                return
            # Cycle end: power the master off only if configured to; always clear
            # the on-flag so the next cycle re-arms (and re-kicks a stay-on pump).
            if getattr(self._master_cfg(), const.CONF_MASTER_OFF_AFTER, False):
                await self._master_turn(False)
            self._master_on = False
            self._master_off_deadline = None

        self._master_off_cancel = async_call_later(self.hass, delay, _fire)
