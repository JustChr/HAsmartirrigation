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

    # --- Consumer holds (refcounting) ---------------------------------------
    #
    # The master is a SHARED resource with several independent consumers
    # (scheduled linked-entity runs, irrigate-now, run_zone, self-closing runs,
    # distributor sweeps). Historically the only coordination was one
    # monotonically-extending timestamp (``_master_off_deadline``): every
    # consumer had to PREDICT its own release time up front, and because
    # ``_master_note_run`` can only extend, a consumer that guessed long poisoned
    # the shared deadline for everyone while one that guessed short got its pump
    # cut mid-run. Every measured error in the 2026-07-31 review (valve-confirm
    # polling, rotating absorption waits, flow zones finishing on volume rather
    # than ZONE_DURATION) was a prediction error.
    #
    # A hold is the observation instead of the guess: a consumer takes one for as
    # long as it actually needs the master, and the cycle ends when the last one
    # is dropped. The deadline still exists as a floor so any consumer not yet
    # converted keeps working unchanged.

    def _master_hold_set(self) -> set:
        """Lazily-created set of tokens for consumers holding the master."""
        holds = getattr(self, "_master_holds", None)
        if holds is None:
            holds = self._master_holds = set()
        return holds

    def master_holds(self) -> set:
        """Read-only view of the current holds (diagnostics / tests)."""
        return set(self._master_hold_set())

    async def async_master_acquire(self, token: str) -> None:
        """Take a hold and bring the master up. Safe to call repeatedly.

        Cancels any pending off-timer: a new consumer arriving during the release
        grace must keep the master up rather than let the timer end the cycle.
        """
        if not self._master_configured():
            return
        self._master_hold_set().add(token)
        cancel = getattr(self, "_master_off_cancel", None)
        if cancel:
            cancel()
            self._master_off_cancel = None
        await self.async_master_begin_cycle()

    async def async_master_release(self, token: str) -> None:
        """Drop a hold; end the cycle once it was the last one.

        Releasing the last hold COLLAPSES any leftover predicted deadline down to
        a short grace window — that is the whole point, since the prediction is
        exactly what used to over-run. Collapsing is safe only because it happens
        when nothing holds the master any more; while any consumer still holds
        one, this returns early and leaves the deadline untouched.
        """
        if not self._master_configured():
            return
        holds = self._master_hold_set()
        holds.discard(token)
        if holds:
            return
        grace = datetime.timedelta(seconds=const.MASTER_RELEASE_GRACE_SECONDS)
        collapsed = self._master_now() + grace
        current = getattr(self, "_master_off_deadline", None)
        if current is None or current > collapsed:
            self._master_off_deadline = collapsed
        await self.async_master_schedule_off()

    def _master_release_all(self) -> None:
        """Drop every hold without touching the hardware (unload/reset only)."""
        self._master_hold_set().clear()

    def _master_note_run(self, seconds: float):
        """Record the latest expected cycle end (now + seconds).

        Returns the deadline THIS note computes (``now + seconds``) — the caller's own
        contribution — regardless of whether it raised the shared
        ``_master_off_deadline`` (which only ever grows via ``max``). The distributor
        uses the return to track its sweep's own-notes ceiling, so the terminal can tell
        its own inflation apart from a foreign consumer's later note (Bug 1 hardening,
        2026-07-06). Returns ``None`` when no master is configured. Existing callers that
        ignore the return are unaffected."""
        if not self._master_configured():
            return None
        deadline = self._master_now() + datetime.timedelta(
            seconds=max(0.0, float(seconds or 0))
        )
        cur = getattr(self, "_master_off_deadline", None)
        if cur is None or deadline > cur:
            self._master_off_deadline = deadline
        return deadline

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
            if self._master_hold_set():
                # A consumer is still actually running. Do NOT end the cycle on a
                # timer that only ever encoded a guess — the release of the last
                # hold re-schedules this. This is what makes an under-estimated
                # deadline harmless (it used to cut the pump mid-cycle).
                return
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

    async def async_reconcile_master_after_restart(self) -> None:
        """One-shot boot normalization: kill an orphaned master left on across a
        restart. NOT a runtime watchdog.

        Iter (2026-07-06, Bug 2 — orphaned master): the master-off deadline + timer
        live only in memory and are lost on ANY restart (clean or crash); HA
        restore_state may also bring the master entity back to `on`. A narrow "mirror
        the inlet-close in async_resume_distributor_cycles" fix would MISS the observed
        clean-restart case — the `finally` in async_run_distributor_cycle self-clears
        `active_cycle`, so reconciliation is a no-op there. So key the shut-off on the
        master state + config, not on a surviving cycle record.

        Fires iff ALL hold: a master is configured AND `master_off_after` is enabled
        (the user opted into auto-off — else HASI never auto-shuts the master, so it
        must not at boot either) AND nothing HASI-driven is still running: no
        distributor `active_cycle` and no in-window self-closing run (those legitimately
        need the master — defer to them). NB the `active_cycle` gate is belt-and-
        suspenders: async_resume_distributor_cycles just before ALWAYS clears the
        record (crashed or clean), so in practice the effective gates are
        `master_off_after` + no self-closing run. Covers BOTH restart flavours because
        it does not depend on a surviving `active_cycle`.
        Called from __init__ AFTER async_resume_self_closing_runs and
        async_resume_distributor_cycles.
        siehe test_master.py::test_reconcile_master_off_when_off_after_and_idle
        """
        if not self._master_configured():
            return
        if not getattr(self._master_cfg(), const.CONF_MASTER_OFF_AFTER, False):
            return
        for dist in await self.store.async_get_distributors():
            if dist.get("active_cycle"):
                return
        if await self._sc_active_runs():
            return
        # Holds live only in memory, so a restart necessarily clears them; this
        # boot path is what re-derives "nothing is running" from persisted state.
        self._master_release_all()
        await self._master_turn(False)
        self._master_on = False
        self._master_off_deadline = None
