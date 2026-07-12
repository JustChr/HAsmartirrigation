"""Gardena Wasserverteiler automatic: outlet-ring cycle engine (primitives).

A distributor waters 2..6 outlets one at a time through a single shared inlet
valve, behind the one global master. HASI is open-loop: it counts advances and
persists the position, it can never measure it. These are the low-level building
blocks (inlet actuation, position advance, uncertain/de-arm, master window
control, duration estimate); the cycle loop + recovery that orchestrate them
live in the coordinator (later plan). Mixed into SmartIrrigationCoordinator.

Distributor dicts are attr.asdict(DistributorEntry); fields are accessed by their
literal attr-name keys.
"""

from __future__ import annotations

import asyncio
import logging
import math

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event

from . import const
from .localize import localize

_LOGGER = logging.getLogger(__name__)


class DistributorMixin:
    """Distributor outlet-ring primitives. Mixed into SmartIrrigationCoordinator."""

    # --- inlet actuation ---------------------------------------------------

    async def _dist_domain_turn(self, entity: str, on: bool) -> None:
        """Open/close an inlet entity, domain-aware. valve.* needs open_valve/
        close_valve (homeassistant.turn_on silently no-ops on a valve); switch /
        input_boolean use turn_on/turn_off. Mirrors MasterMixin._master_turn."""
        if not isinstance(entity, str) or not entity:
            return
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

    @staticmethod
    def _dist_split_service(dotted: str):
        """'domain.service' -> (domain, service)."""
        domain, _, service = (dotted or "").partition(".")
        return domain, service

    @staticmethod
    def _dist_convert(seconds: float, unit: str) -> int:
        """Convert a window (seconds) to the inlet hardware's unit, rounding up."""
        seconds = float(seconds or 0)
        if unit == const.DURATION_UNIT_MINUTES:
            return max(1, math.ceil(seconds / 60.0)) if seconds > 0 else 0
        return int(round(seconds))

    async def _dist_open_inlet(self, distributor: dict, seconds: float) -> None:
        """Open the inlet for a window. classic: domain-aware open (the loop owns
        the timed close). service (self-closing): fire the run_service with the
        converted duration; the hardware owns the close."""
        if distributor.get("watering_mode") == const.WATERING_MODE_SERVICE:
            domain, service = self._dist_split_service(distributor.get("run_service"))
            data = {}
            unit = distributor.get("duration_unit", const.DURATION_UNIT_SECONDS)
            field = distributor.get("duration_field") or "duration"
            data[field] = self._dist_convert(seconds, unit)
            data["distributor_id"] = distributor.get("id")
            await self.hass.services.async_call(domain, service, data)
            return
        await self._dist_domain_turn(distributor.get("inlet_entity"), True)

    async def _dist_close_inlet(self, distributor: dict) -> None:
        """Close the inlet. classic: domain-aware close. service: fire stop_service
        if configured, else rely on the hardware self-close (no-op)."""
        if distributor.get("watering_mode") == const.WATERING_MODE_SERVICE:
            stop = distributor.get("stop_service")
            if stop:
                domain, service = self._dist_split_service(stop)
                data = {}
                data["distributor_id"] = distributor.get("id")
                await self.hass.services.async_call(domain, service, data)
            return
        await self._dist_domain_turn(distributor.get("inlet_entity"), False)

    # --- position advance --------------------------------------------------

    async def _dist_advance(
        self, distributor_id, current_outlet: int, outlet_count: int
    ) -> int:
        """Advance the ring by one and persist the new position immediately.

        For a blind device an "advance" is only ever "the pause timer elapsed" —
        there is no confirmation signal (spec §7). Position is written after each
        step so a crash never loses more than the in-flight step. Wraps n -> 1.
        """
        nxt = (int(current_outlet) % int(outlet_count)) + 1
        await self._dist_store_update(distributor_id, {"current_outlet": nxt})
        return nxt

    # --- notify + fail-safe de-arm ----------------------------------------

    async def _dist_notify(self, distributor: dict, message: str) -> None:
        """Surface a halt to the user. Always creates a Home Assistant
        persistent notification (the bell / Notifications panel), keyed per
        distributor so a repeat replaces rather than piles up, and additionally
        forwards to an optional 'domain.service' notify target when one is set
        (test feedback FB4: the panel notification is unconditional, the notify
        target is an extra, optional channel)."""
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Smart Irrigation",
                "message": message,
                "notification_id": (
                    f"{const.DOMAIN}_distributor_{distributor.get('id')}"
                ),
            },
        )
        target = distributor.get("notify_target")
        if not target:
            return
        domain, service = self._dist_split_service(target)
        if domain and service:
            await self.hass.services.async_call(domain, service, {"message": message})

    async def _dist_mark_uncertain(self, distributor: dict, reason: str) -> None:
        """Fail-safe: mark the position uncertain AND clear commissioning_confirmed
        (the single de-arm path, spec §7), persist both in one write, fire the
        halted event, and notify. An uncertain distributor is blocked from
        scheduled watering until the user re-syncs and re-confirms."""
        await self._dist_store_update(
            distributor["id"],
            {
                "position_state": const.POSITION_STATE_UNCERTAIN,
                "commissioning_confirmed": False,
            },
        )
        self.hass.bus.async_fire(
            f"{const.DOMAIN}_{const.EVENT_DISTRIBUTOR_HALTED}",
            {
                "distributor_id": distributor.get("id"),
                "distributor": distributor.get("name"),
                "reason": reason,
            },
        )
        # Localized halt notification (mirrors calculation.py's localize() usage):
        # fetch the message template + a localized reason phrase for the user's HA
        # language, then fill {name}/{reason} by replace() so a translation can never
        # inject a str.format field. Unknown reason/lang fall back via localize().
        lang = self.hass.config.language
        reason_text = await localize(
            f"panels.distributors.notify.reason.{reason}", lang
        )
        template = await localize("panels.distributors.notify.halted", lang)
        message = template.replace("{name}", str(distributor.get("name"))).replace(
            "{reason}", reason_text
        )
        await self._dist_notify(distributor, message)

    # --- global-master window control -------------------------------------
    # The distributor drives the ONE global master synchronously inside its own
    # atomic cycle: on at start, (optionally) off during each pause + on before
    # the next window, off at the end. Per-window cycling is gated on the existing
    # master_off_after setting. NOT-TO-DO: never toggle the master while the inlet
    # is open (the caller closes the inlet BEFORE calling _dist_master_window_off,
    # and opens it AFTER _dist_master_window_on) — else the distributor sees an
    # extra pressure edge and advances unintentionally. `concurrent` suppresses
    # per-window off in parallel mode (other zones may need the master on).

    def _dist_uses_master(self, distributor: dict) -> bool:
        return bool(distributor.get("use_master", True)) and self._master_configured()

    def _dist_master_off_after(self) -> bool:
        return bool(getattr(self._master_cfg(), const.CONF_MASTER_OFF_AFTER, False))

    def _distributor_concurrent(self) -> bool:
        """True when the distributor must keep the shared master powered through its
        pauses: parallel zone_sequencing (other zones run at once), OR a normal-zone
        run has already claimed the master (a future off-deadline is set), i.e. a
        mixed scheduled run. False for a solo sequential/rotating distributor run,
        where per-pause master cycling is the configured behaviour."""
        if self.store.config.zone_sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL:
            return True
        deadline = getattr(self, "_master_off_deadline", None)
        return deadline is not None and self._master_now() < deadline

    async def _dist_master_start(self, distributor: dict) -> None:
        """Bring the global master up for the cycle (idempotent on+kick+settle)."""
        if not self._dist_uses_master(distributor):
            return
        await self.async_master_begin_cycle()

    async def _dist_master_window_off(
        self, distributor: dict, concurrent: bool
    ) -> None:
        """Power the master off during a pause, iff master_off_after and the
        distributor runs exclusively (not concurrent)."""
        if not self._dist_uses_master(distributor) or concurrent:
            return
        if not self._dist_master_off_after():
            return
        await self._master_turn(False)

    async def _dist_master_window_on(self, distributor: dict, concurrent: bool) -> None:
        """Bring the master back up (+ settle) before the next window, iff it was
        powered down in the pause."""
        if not self._dist_uses_master(distributor) or concurrent:
            return
        if not self._dist_master_off_after():
            return
        await self._master_turn(True)
        settle = getattr(self._master_cfg(), const.CONF_MASTER_SETTLE_SECONDS, 10)
        if float(settle or 0) > 0:
            await self._master_sleep(settle)

    async def _dist_master_end(
        self, distributor: dict, *, pre_deadline=None, own_deadline=None
    ) -> None:
        """End of cycle. Decide synchronous shutdown vs. deferral by whether a master
        consumer OTHER than this just-finished sweep still needs the master — keyed on
        live deadlines, NOT the static parallel flag.

        Iter (2026-07-06, Bug 1 — master over-run ~80 s): the old `concurrent` branch
        keyed the terminal collapse on `_distributor_concurrent()` == parallel, True on
        EVERY real run under the default sequencing. It always deferred
        (`_master_note_run(0)` + schedule_off), and since `_master_note_run` only EXTENDS
        (max), that `note(0)` could never collapse the sweep's rolling over-estimate
        deadline (window+pause+settle+buffer+confirm, noted at each window START) -> the
        pump dead-headed ~80 s past the last valve close on every real run.

        Two live signals decide the terminal now:
        - `pre_deadline`: `_master_off_deadline` snapshotted in `_dist_run_sweep` BEFORE
          the sweep began noting -> a consumer that pre-existed the sweep (scenario 6:
          a parallel normal-zone run). Future -> defer to it.
        - `own_deadline`: the ceiling of THIS sweep's OWN rolling notes. If the shared
          `_master_off_deadline` now exceeds it, a FOREIGN consumer noted a later
          deadline DURING the sweep (a manual normal-zone run fired mid-sweep) -> defer
          to that, so we never hard-cut its pump (hardening added after code review).
        If neither external signal holds, the shared deadline is purely OUR inflation ->
        finalize synchronously (solo) so a back-to-back sibling re-arms the master.

        NOT-TO-DO: do not read `_distributor_concurrent()`/`zone_sequencing` here — the
        static flag is exactly what mis-fired; the live deadlines are the truth. The
        per-pause master cycling (`_dist_master_window_off/on`) still keys on the
        `concurrent` flag — only the TERMINAL collapse moved to the live signals.
        RESIDUAL LIMITATION (rare, accepted): a foreign note whose deadline falls BELOW
        our own inflated ceiling `own_deadline` (a SHORT manual run fired near the sweep
        end) is still not distinguished and would be cut. Much narrower than the pre-
        hardening "cut every mid-sweep manual run"; a fully general fix needs per-
        consumer refcounting on the shared master (out of scope, REGEL 3).
        siehe test_distributor_dispatch.py::test_master_end_defers_to_foreign_mid_sweep_note_even_when_solo
        and ::test_master_end_collapses_when_deadline_is_only_our_own_notes
        """
        if not self._dist_uses_master(distributor):
            self._master_on = False
            return
        now = self._master_now()
        current = getattr(self, "_master_off_deadline", None)
        external = None
        if pre_deadline is not None and now < pre_deadline:
            external = pre_deadline
        if (
            current is not None
            and now < current
            and own_deadline is not None
            and current > own_deadline
        ):
            # A foreign consumer noted a later deadline during the sweep.
            external = current if external is None else max(external, current)
        if external is not None:
            # A consumer other than this sweep still holds the master: defer to the
            # furthest such external deadline, collapsing only our own inflation.
            self._master_off_deadline = external
            await self.async_master_schedule_off()
            return
        if self._dist_master_off_after():
            await self._master_turn(False)
        self._master_on = False
        self._master_off_deadline = None
        cancel = getattr(self, "_master_off_cancel", None)
        if cancel:
            cancel()
            self._master_off_cancel = None

    # --- scheduled dispatch -----------------------------------------------

    def _dist_eligible_for_run(
        self, distributor: dict, members: list, require_due: bool = True
    ) -> bool:
        """Static + demand gates shared by the dispatcher and the finish-anchor
        estimate, so both agree on whether a distributor will actually sweep.

        b10 (live 2026-07-05): a manual custom-duration member run
        (``_dispatch_distributor_cycles(duration_override=...)``) must arm the
        distributor even when NO member is currently due — the user explicitly
        asked to irrigate now, mirroring how a normal zone's ``run_zone`` bypasses
        the deficit gate. ``require_due=False`` skips ONLY the
        ``any(_dist_needs_water)`` demand check; the four static gates (synced /
        commissioning_confirmed / not active_cycle / members-non-empty) still hold.
        Default ``True`` keeps the scheduled dispatch AND the finish-anchor estimate
        caller (skip_conditions.get_total_irrigation_duration) due-gated, unchanged.
        siehe test_distributor_dispatch.py::test_dispatch_manual_bypasses_due_gate
        and ::test_scheduled_run_still_due_gated."""
        if distributor.get("position_state") != const.POSITION_STATE_SYNCED:
            return False
        if not distributor.get("commissioning_confirmed"):
            return False
        if distributor.get("active_cycle"):
            return False
        if not members:
            return False
        if not require_due:
            return True
        return any(self._dist_needs_water(m) for m in members)

    async def _dispatch_distributor_cycles(
        self, zone_ids=None, duration_override=None
    ) -> None:
        """Plan G: run each qualifying distributor's cycle on a scheduled irrigate.
        Member zones were excluded from the normal linked-entity path
        (irrigation.py: distributor_id is None), so this is their sole automatic
        driver, and it runs even when no non-member zone is due. Pre-guards avoid
        arming the master for a distributor that would immediately no-op; the cycle's
        own guards (synced / commissioning_confirmed / no members / rain-delay /
        no due members) remain authoritative."""
        if self._rain_delay_active():
            # H4 (review #3): on a rain-delayed mixed-target schedule the
            # linked-entity path already records a skipped run for the non-member
            # zones. Record here only for the in-scope distributor member zones we
            # own, so a targeted zone doesn't get a duplicate "paused" entry.
            # (want_all/target are recomputed locally because this branch returns
            # before the non-rain path below computes them.)
            want_all = zone_ids is None or zone_ids == "all"
            target = None if want_all else {int(z) for z in zone_ids}
            member_ids = []
            for dist in await self.store.async_get_distributors():
                for m in await self._dist_members(dist.get("id")):
                    zid = int(m.get(const.ZONE_ID))
                    if target is None or zid in target:
                        member_ids.append(zid)
            if member_ids:
                await self._record_skipped_run(member_ids, const.SKIP_REASON_PAUSED)
            return
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}
        # b10 (live 2026-07-05): a duration_override is only ever set by a manual
        # "irrigate now (X min)" member run (b9). Scheduled dispatch never carries
        # one. A manual run must water the targeted outlet regardless of due-ness,
        # so drop the demand gate here (require_due=False) and tell the cycle to
        # force-water the target (force_water=True). See _dist_eligible_for_run and
        # async_run_distributor_cycle.
        manual = duration_override is not None
        for dist in await self.store.async_get_distributors():
            members = await self._dist_members(dist.get("id"))
            if target is not None and not any(
                int(m.get(const.ZONE_ID)) in target for m in members
            ):
                continue
            # H2 (review #11): the four static gates (position_state /
            # commissioning_confirmed / active_cycle / members-empty) plus the
            # any(_dist_needs_water) demand gate are now a single shared predicate,
            # so get_total_irrigation_duration's finish-anchor estimate counts
            # exactly the distributors this dispatcher will actually sweep. b10: a
            # manual run skips only the demand gate (require_due=False).
            if not self._dist_eligible_for_run(dist, members, require_due=not manual):
                continue
            await self.async_run_distributor_cycle(
                dist,
                concurrent=self._distributor_concurrent(),
                only_zone_ids=None if target is None else list(target),
                duration_override=duration_override,
                force_water=manual,
            )

    # --- finish-anchor duration estimate ----------------------------------

    def distributor_cycle_estimate(
        self, distributor: dict, member_zones: list, only_zone_ids=None
    ) -> float:
        """E2: deterministic wall-clock seconds for the early-stop sweep (E1) from
        the current position THROUGH the last WILL-WATER outlet, for finish-anchored
        schedules (spec §5.5). Leading non-watering outlets are skip-pulsed to reach a
        later watering one; trailing ones are never visited. So the estimate is
        windows + (k-1) pauses + per-gap master settle (if the master cycles) + a
        safety buffer, where k is the number of outlets swept. Pause/skip are
        floored (spec §4.5); a ring with no will-water outlet sweeps nothing -> 0.0.

        ``only_zone_ids`` restricts which outlets actually water, mirroring
        ``async_run_distributor_cycle(only_zone_ids=...)``: a schedule targeting a
        zone subset waters ONLY those members, but the mechanical ring still has to
        skip-pulse EVERY non-targeted outlet between ``current`` and the last
        targeted one to reach it. So ``member_zones`` must be the FULL physical
        member ring, not a target-compacted subset — otherwise those leading skip
        windows + their pauses are lost and the estimate under-counts the real
        sweep (review I-1). None => every due (duration>0) member waters (the
        legacy full-ring, all-due behaviour used by non-subset callers).

        NOT the old full-ring formula (n outlets + n pauses): that over-estimated
        the sweep whenever the last watering outlet was not the ring's tail, pushing
        a finish-anchored start time earlier than the real (shorter) sweep needs.
        See test_estimate_truncates_to_last_due_outlet. And NOT the pre-I-1 form
        that pre-compacted ``member_zones`` to the target: that dropped the leading
        skip-pulses of a subset sweep. See
        test_estimate_models_full_ring_for_subset_target."""
        n = len(member_zones)
        if n == 0:
            return 0.0
        # `or default` (not the get-default) so a persisted None can't raise.
        pause = max(
            int(distributor.get("pause_seconds") or 300),
            const.DISTRIBUTOR_MIN_PAUSE_SECONDS,
        )
        skip = max(
            int(distributor.get("skip_pulse_seconds") or 30),
            const.DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS,
        )
        # Rotate the member ring so index 0 is the current outlet, mirroring the
        # cycle's own sweep order (E1). current_outlet is 1-based; wrap defensively.
        current = ((int(distributor.get("current_outlet") or 1) - 1) % n) + 1
        order = [member_zones[(current - 1 + k) % n] for k in range(n)]
        allow = None if only_zone_ids is None else {int(x) for x in only_zone_ids}

        def _will_water(z: dict) -> bool:
            # Mirrors the cycle's to_water gate: due (duration>0) AND (no subset OR
            # in the subset). Kept as "duration>0" (NOT _dist_needs_water) so the
            # arm-time estimate stays stable; a duration>0-but-satisfied outlet is
            # an accepted upper bound (review I-2).
            if float(z.get(const.ZONE_DURATION) or 0) <= 0:
                return False
            return allow is None or int(z.get(const.ZONE_ID)) in allow

        water_idx = [i for i in range(n) if _will_water(order[i])]
        if not water_idx:
            return 0.0
        k = water_idx[-1] + 1  # outlets visited: up to & incl. the last will-water
        windows = 0.0
        for z in order[:k]:
            # Leading non-targeted / non-due outlets before the last watering one
            # are physically skip-pulsed to reach it, so they cost the skip window.
            windows += (
                float(z.get(const.ZONE_DURATION) or 0) if _will_water(z) else skip
            )
        total = windows + (k - 1) * pause
        if self._dist_uses_master(distributor) and self._dist_master_off_after():
            settle = float(
                getattr(self._master_cfg(), const.CONF_MASTER_SETTLE_SECONDS, 10) or 0
            )
            total += (k - 1) * settle
        return total + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS

    # --- cycle orchestration: helpers -------------------------------------

    async def _dist_sleep(self, seconds) -> None:
        """Awaitable sleep wrapper (isolated/overridable in unit tests)."""
        await asyncio.sleep(max(0.0, float(seconds or 0)))

    # --- flow metering (Phase 4 Part A): measure litres delivered per outlet
    # window from the distributor's shared inlet flow_sensor and credit that
    # instead of the time estimate. Wired into the sweep (_dist_run_sweep) and
    # _dist_credit_zone. No early stop — the full window always elapses (early
    # stop by target volume is Part B). ------------------------------------

    @staticmethod
    def _dist_flow_unit_is_rate(unit: str) -> bool:
        """A flow unit is a RATE (per-time) iff it contains '/'; else a cumulative
        total counter."""
        return "/" in (unit or "")

    @staticmethod
    def _dist_flow_litres_from_total(value: float, unit: str) -> float:
        """Convert a cumulative flow-counter reading to litres. Mirrors
        _flow_rate_to_l_per_min's unit strings/factors (totals, not rates)."""
        u = (unit or "").lower().strip()
        if u in ("m³", "m3", "cubic meter", "cubic meters"):
            return float(value) * 1000.0
        if u in ("gal", "gallon", "gallons"):
            return float(value) * 3.785411784
        return float(value)  # L / l / liter(s) / unknown -> assume litres

    def _dist_read_flow(self, sensor: str):
        """Read a flow sensor -> (value, unit) or None when unavailable/non-numeric
        (fail-safe: the caller then degrades to time-based crediting)."""
        state = self.hass.states.get(sensor)
        if state is None or getattr(state, "state", None) in (
            "unavailable",
            "unknown",
            None,
            "",
        ):
            return None
        try:
            value = float(state.state)
        except (ValueError, TypeError):
            return None
        unit = (
            state.attributes.get("unit_of_measurement", "") if state.attributes else ""
        )
        return value, unit

    async def _dist_measure_window(
        self, distributor: dict, window: float, *, cap=None, target=None
    ):
        """Sleep the outlet's window (or up to ``cap`` when early-stopping) and, if the
        distributor has a rate flow_sensor, meter the delivered litres. Returns a tuple
        ``(delivered, actual_seconds, stopped_early)``:

        - ``delivered`` — measured litres, or None to fall back to time-based crediting
          (no sensor / unreliable / a cumulative counter while metering is dormant).
        - ``actual_seconds`` — time actually elapsed (== ``window`` on any non-metering
          path; < ``cap`` when a ``target`` is hit; == ``cap`` at the safety cap).
        - ``stopped_early`` — True iff ``target`` was reached before ``cap`` elapsed.

        ``cap`` (defaults to ``window``) is the metering time bound: the classic-extend
        path passes the member's safety maximum_duration so a slow flow can still reach
        the target past the nominal window. Every NON-metering path sleeps only
        ``window`` (never ``cap``), so a dead / cumulative meter never extends the run.
        Part A behaviour is preserved when ``target`` is None (full ``cap`` elapses).
        """
        window = float(window or 0)
        cap = float(cap) if cap else window
        sensor = distributor.get("flow_sensor")
        if not sensor:
            await self._dist_sleep(window)
            return None, window, False
        reading = self._dist_read_flow(sensor)
        if reading is None:
            await self._dist_sleep(window)  # dead meter -> full window, time-based
            return None, window, False
        _, unit = reading
        is_rate = self._dist_flow_unit_is_rate(unit)
        # b23 ships RATE-ONLY: a cumulative counter is dormant behind the flag and gets
        # no metering (hence no early stop) — sleep the window, credit time-based.
        if not is_rate and not const.DISTRIBUTOR_CUMULATIVE_METERING_ENABLED:
            await self._dist_sleep(window)
            return None, window, False
        last = None if is_rate else self._dist_flow_litres_from_total(reading[0], unit)
        delivered = 0.0
        reliable = True
        elapsed = 0.0
        while elapsed < cap:
            if target is not None and delivered >= target:
                break  # early stop: reached the target volume
            step = min(float(const.DISTRIBUTOR_FLOW_POLL_SECONDS), cap - elapsed)
            await self._dist_sleep(step)
            elapsed += step
            r = self._dist_read_flow(sensor)
            if r is None:
                reliable = False
                continue
            val, u = r
            if is_rate:
                delivered += self._flow_rate_to_l_per_min(val, u) * step / 60.0
            else:
                cur = self._dist_flow_litres_from_total(val, u)
                if cur < last:  # counter reset / rollover -> unreliable
                    reliable = False
                else:
                    delivered += cur - last
                last = cur
        stopped_early = target is not None and delivered >= target and elapsed < cap
        # Part B fail-safe: a valve that stayed open but registered NO flow (a live but
        # dry meter — stuck valve, air-lock, pressure loss) delivered 0 L. Crediting 0
        # would leave the member in permanent deficit; instead treat it as unreliable so
        # the caller falls back to time-based crediting (spec: delivered <= 0 -> None).
        reliable = reliable and delivered > 0
        return (delivered if reliable else None), elapsed, stopped_early

    async def _dist_members(self, distributor_id) -> list:
        """This distributor's member zones (dicts), ordered by outlet 1..n."""
        zones = await self.store.async_get_zones()
        members = [z for z in zones if z.get("distributor_id") == distributor_id]
        return sorted(members, key=lambda z: z.get("outlet_number") or 0)

    def _dist_needs_water(self, zone: dict) -> bool:
        """Classic daily gate: automatic-eligible, calculated duration > 0, and
        the bucket still below its threshold. (Live-estimate gating is out of
        MVP scope — the distributor uses the daily gate.)"""
        return (
            zone.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
            and (zone.get(const.ZONE_DURATION) or 0) > 0
            and (zone.get(const.ZONE_BUCKET) or 0)
            < (zone.get(const.ZONE_BUCKET_THRESHOLD) or 0)
        )

    async def _dist_store_update(self, distributor_id, changes: dict):
        """Persist a distributor change AND notify its HA entities + the panel.

        ``_distributor_updated`` refreshes the per-distributor HA entities;
        ``_update_frontend`` is the signal the panel's ``_config_updated``
        subscription re-fetches on, so a cycle start (block other members) / end
        (unblock) / outlet advance shows live in the UI instead of only after F5.
        """
        res = await self.store.async_update_distributor(distributor_id, changes)
        async_dispatcher_send(
            self.hass, const.DOMAIN + "_distributor_updated", int(distributor_id)
        )
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")
        return res

    # --- inlet watch (E4): foreign-pulse resync ---------------------------

    def _dist_observed_open_map(self) -> dict:
        """Per-distributor record of an in-progress FOREIGN inlet open, for observed
        member crediting (Phase 2). Lazily created so no coordinator __init__ change
        is needed. Maps distributor_id -> {"t": open_time, "outlet": ring index
        (1-based) BEFORE the open-edge advance = the outlet flowing during the open}."""
        m = getattr(self, "_dist_observed_open", None)
        if m is None:
            m = self._dist_observed_open = {}
        return m

    async def _dist_on_inlet_pulse(self, distributor_id) -> None:
        """A foreign inlet off->on pulse touched the physical ring. Only acted on
        when no HASI cycle is active (HASI pulses the inlet only within a cycle,
        which always has a non-empty active_cycle). Partial mitigation: catches
        only HA-observable actuation. Reaction depends on watch_mode:
        - warn: mark the distributor uncertain (de-arm + notify) instead of
          silently advancing, since we can't be sure the ring is still in sync.
        - count (or legacy watch_inlet=True derive): advance the tracked position,
          as before.
        `ignore` never reaches here — _dist_refresh_inlet_watch registers no
        listener for it."""
        dist = self.store.get_distributor(distributor_id)
        if dist is None or dist.get("active_cycle"):
            return
        mode = self._dist_watch_mode(dist)
        if mode == const.DISTRIBUTOR_WATCH_MODE_WARN:
            await self._dist_mark_uncertain(
                dist, reason=const.DISTRIBUTOR_REASON_FOREIGN_PULSE
            )
            return
        if mode != const.DISTRIBUTOR_WATCH_MODE_COUNT:
            # ignore (defensive): the user opted out of inlet tracking, so a stray
            # call must never touch the position. In practice unreachable — no
            # listener is registered for ignore.
            return
        members = await self._dist_members(distributor_id)
        n = len(members)
        if n == 0:
            return
        cur = int(dist.get("current_outlet") or 1)
        # Phase 2 (observed watering): remember which outlet is flowing NOW (the
        # pre-advance ring index) and when this foreign open started, so the close
        # edge can credit this member if the open lasts long enough to be real
        # watering rather than a short advance pulse. Gated on the opt-in so count
        # users who don't use observed watering never grow the map.
        if getattr(self.store.config, "observed_watering_enabled", False):
            self._dist_observed_open_map()[distributor_id] = {
                "t": self.hass.loop.time(),
                "outlet": cur,
            }
        await self._dist_store_update(distributor_id, {"current_outlet": (cur % n) + 1})

    async def _dist_on_inlet_close(self, distributor_id) -> None:
        """A foreign inlet on->off edge closed. If observed watering is enabled and
        the open lasted long enough to be real watering (>= 2 * skip_pulse_seconds),
        credit the member zone that was flowing during the open (the pre-advance ring
        index stashed on the open edge) and write an `observed` run-log entry. Short
        opens are advance pulses -> not credited (the ring already advanced on open).

        Only foreign, count-mode opens ever leave a stash (see _dist_on_inlet_pulse),
        so warn/ignore modes and SI's own cycles no-op here. A race guard additionally
        drops the credit if an SI cycle claimed the inlet between open and close."""
        open_rec = self._dist_observed_open_map().pop(distributor_id, None)
        if open_rec is None:
            return
        dist = self.store.get_distributor(distributor_id)
        if dist is None or dist.get("active_cycle"):
            # An SI cycle claimed the inlet between open and close -> not foreign.
            return
        if not getattr(self.store.config, "observed_watering_enabled", False):
            return
        duration = self.hass.loop.time() - float(open_rec.get("t") or 0)
        skip_pulse = max(
            int(dist.get("skip_pulse_seconds") or 30),
            const.DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS,
        )
        if duration < 2 * skip_pulse:
            return  # short advance pulse, not watering
        members = await self._dist_members(distributor_id)
        n = len(members)
        if n == 0:
            return
        outlet = int(open_rec.get("outlet") or 1)
        member = members[(outlet - 1) % n]
        if member.get(const.ZONE_STATE) == const.ZONE_STATE_DISABLED:
            return
        await self._dist_credit_zone(
            member,
            duration,
            result=const.RUN_RESULT_OBSERVED,
            trigger=const.RUN_TRIGGER_OBSERVED,
        )

    def _dist_inlet_state_handler(self, distributor_id):
        """Build a state-change handler that decodes an off->on edge and defers to
        _dist_on_inlet_pulse."""
        off_states = {"off", "closed"}
        on_states = {"on", "open", "opening"}

        @callback
        def _handler(event):
            old = event.data.get("old_state")
            new = event.data.get("new_state")
            if old is None or new is None:
                return
            if old.state in off_states and new.state in on_states:
                self.hass.async_create_task(self._dist_on_inlet_pulse(distributor_id))

        return _handler

    @staticmethod
    def _dist_watch_mode(distributor: dict) -> str:
        """The inlet-watch reaction mode, deriving from the legacy `watch_inlet`
        bool when `watch_mode` is absent (True -> count, else -> ignore) so existing
        distributors keep today's behaviour."""
        mode = distributor.get("watch_mode")
        if mode in (
            const.DISTRIBUTOR_WATCH_MODE_COUNT,
            const.DISTRIBUTOR_WATCH_MODE_WARN,
            const.DISTRIBUTOR_WATCH_MODE_IGNORE,
        ):
            return mode
        return (
            const.DISTRIBUTOR_WATCH_MODE_COUNT
            if distributor.get("watch_inlet")
            else const.DISTRIBUTOR_WATCH_MODE_IGNORE
        )

    def _dist_refresh_inlet_watch(self, distributor: dict) -> None:
        """(Re)register the inlet-state listener for one distributor per watch_mode.
        Gate is mode-agnostic (count or warn both listen) so self-closing
        distributors can watch their ring valve too; only `ignore` registers
        nothing."""
        did = int(distributor.get("id"))
        watchers = getattr(self, "_dist_inlet_watchers", None)
        if watchers is None:
            watchers = self._dist_inlet_watchers = {}
        unsub = watchers.pop(did, None)
        if unsub:
            unsub()
        inlet = distributor.get("inlet_entity")
        if (
            self._dist_watch_mode(distributor) != const.DISTRIBUTOR_WATCH_MODE_IGNORE
            and isinstance(inlet, str)
            and inlet
        ):
            watchers[did] = async_track_state_change_event(
                self.hass, [inlet], self._dist_inlet_state_handler(did)
            )

    async def _dist_persist_cycle(
        self, distributor_id, outlet: int, phase: str
    ) -> None:
        """Persist the in-flight cycle record (phase-based, for restart recon)."""
        await self._dist_store_update(
            distributor_id, {"active_cycle": {"outlet": outlet, "phase": phase}}
        )

    async def _dist_clear_cycle(self, distributor_id) -> None:
        """Clear the in-flight cycle record (cycle finished / aborted)."""
        await self._dist_store_update(distributor_id, {"active_cycle": {}})

    async def _dist_credit_zone(
        self,
        zone: dict,
        seconds: float,
        measured_l: float | None = None,
        planned_seconds: float | None = None,
        *,
        result: str = const.RUN_RESULT_COMPLETED,
        trigger: str = const.RUN_TRIGGER_DISTRIBUTOR,
    ) -> None:
        """Credit a watered member zone's bucket and log the run.

        A metered (flow) volume credits the GROSS depth (_depth_from_volume_native),
        exactly like JustChr's real-flow zone runs — a measured volume carries no
        multiplier to divide out. The time-based fallback credits _timed_volume_l via
        _credited_depth_native (which divides out the zone multiplier that inflated the
        timed duration). ``seconds`` is the ACTUAL elapsed watering time (a Part B early
        stop can run less than the window, or a classic extend more); ``planned_seconds``
        (defaults to ``seconds``) is the originally planned window for the run log.
        """
        zone_id = zone.get(const.ZONE_ID)
        if measured_l is not None:
            volume_l = measured_l
            depth = self._depth_from_volume_native(zone, volume_l)
        else:
            # Time-based fallback estimates from the PLANNED window, not the actual
            # elapsed seconds: an unreliable meter on a classic-extend outlet can run to
            # the safety cap (up to maximum_duration), and crediting that elapsed time
            # would book hours of water that never flowed. The run log still records the
            # true actual_s below.
            planned = planned_seconds if planned_seconds is not None else seconds
            volume_l = self._timed_volume_l(zone, planned)
            depth = self._credited_depth_native(zone, volume_l)
        new_bucket = float(zone.get(const.ZONE_BUCKET) or 0) + depth
        ceiling = zone.get(const.ZONE_MAXIMUM_BUCKET)
        if ceiling is not None and new_bucket > float(ceiling):
            new_bucket = float(ceiling)
        await self.store.async_update_zone(zone_id, {const.ZONE_BUCKET: new_bucket})
        await self._record_run(
            zone_id,
            result=result,
            volume_l=volume_l,
            planned_s=planned_seconds if planned_seconds is not None else seconds,
            actual_s=seconds,
            trigger=trigger,
            add_to_total=True,
        )

    # --- cycle loop --------------------------------------------------------

    def _dist_inflight_ids(self) -> set:
        """Ids of distributors whose cycle is currently claimed (in-flight).

        Lazily created so no coordinator __init__ change is needed."""
        ids = getattr(self, "_dist_inflight", None)
        if ids is None:
            ids = self._dist_inflight = set()
        return ids

    async def async_run_distributor_cycle(
        self,
        distributor: dict,
        *,
        concurrent: bool = False,
        test_run: bool = False,
        only_zone_ids=None,
        duration_override=None,
        force_water: bool = False,
    ) -> bool:
        """Run one distributor cycle under a synchronous single-flight lock.

        b14 (live test 2026-07-06): ``active_cycle`` — the busy flag the run_zone
        guard and the panel both read to block a second member run — is only set
        once the sweep reaches its first outlet, AFTER dispatch + master-start. That
        left a ~seconds window in which a second fire-and-forget manual run (b13)
        would pass the guard and start a COLLIDING cycle on the shared inlet +
        position counter (interleaved actuation, position desync, double credit).
        Fix: (1) claim the distributor HERE with no ``await`` between the check and
        the add, so two concurrently-scheduled runs can never both pass — the only
        real correctness guarantee, at one point covering every entry (manual,
        irrigate_now, test-run, scheduler). (2) Publish a ``STARTING`` busy marker at
        once (before the slower master-start) so the panel gates the other members
        within one refresh instead of after 2-3s. Release the lock and clear any
        lingering marker in the ``finally`` on every path (early return, error,
        success). NOT-TO-DO: don't gate on ``active_cycle`` alone — it is set too
        late; the in-memory claim is what closes the window.
        siehe test_distributor_cycle.py::test_second_concurrent_cycle_rejected_by_single_flight_lock
        """
        dist_id = distributor.get("id")
        if distributor.get("position_state") != const.POSITION_STATE_SYNCED:
            return False
        if not test_run and not distributor.get("commissioning_confirmed"):
            return False
        inflight = self._dist_inflight_ids()
        if dist_id in inflight:
            return False
        inflight.add(dist_id)
        # (2026-07-08, live-test finding) Preserve active_cycle across a graceful
        # interruption. HA shutdown / integration reload cancels this awaited task,
        # raising CancelledError; the old finally ALWAYS cleared active_cycle, so on the
        # next setup async_resume_distributor_cycles read an empty marker and skipped —
        # the inlet-close (mid-watering) and uncertain (mid-pause) reconcile never fired
        # on a graceful restart (only a hard crash, where finally never runs, worked).
        # Keep the last-persisted marker (already on disk, SAVE_DELAY=0) on cancellation
        # so the boot reconcile acts on the interrupted phase; the boot reconcile clears
        # it. A normal return or an in-process error still clears it here (no restart to
        # reconcile). NOT-TO-DO: don't await _dist_close_inlet here — awaiting during
        # cancellation is fragile; the boot reconcile owns the inlet close.
        # siehe test_distributor_cycle.py::test_cancelled_cycle_preserves_active_cycle_marker
        interrupted = False
        try:
            await self._dist_persist_cycle(
                dist_id,
                int(distributor.get("current_outlet") or 1),
                const.DISTRIBUTOR_PHASE_STARTING,
            )
            return await self._dist_run_sweep(
                distributor,
                concurrent=concurrent,
                test_run=test_run,
                only_zone_ids=only_zone_ids,
                duration_override=duration_override,
                force_water=force_water,
            )
        except asyncio.CancelledError:
            interrupted = True
            raise
        finally:
            inflight.discard(dist_id)
            if not interrupted:
                await self._dist_clear_cycle(dist_id)

    async def _dist_run_sweep(
        self,
        distributor: dict,
        *,
        concurrent: bool = False,
        test_run: bool = False,
        only_zone_ids=None,
        duration_override=None,
        force_water: bool = False,
    ) -> bool:
        """Run one distributor cycle. Returns True if a sweep ran.

        Guard (§5.1): a scheduled cycle runs only when synced AND commissioning-
        confirmed; a test-run bypasses the confirm gate but still needs synced.
        Rule B: a rain delay, or no member needing water, does nothing (no
        switching, no advance). Rule A: sweep all n outlets in physical order
        from the persisted position — water the due ones, skip-pulse the rest —
        advancing (and persisting) after each. A configured flow sensor that
        reports no flow during a watering window triggers a safety-halt (§7).
        """
        dist_id = distributor.get("id")
        if distributor.get("position_state") != const.POSITION_STATE_SYNCED:
            return False
        if not test_run and not distributor.get("commissioning_confirmed"):
            return False

        members = await self._dist_members(dist_id)
        n = len(members)
        if n == 0:
            return False

        if test_run:
            to_water = set()
            fixed = const.DISTRIBUTOR_TEST_RUN_SECONDS
        elif force_water:
            # b10 (live 2026-07-05): a manual "irrigate now (X min)" member run
            # (force_water, set only by _dispatch_distributor_cycles when
            # duration_override is present) must water the TARGETED outlet
            # regardless of due-ness. Build `to_water` straight from the targeted
            # members, bypassing the soil-veto AND the _dist_needs_water demand gate
            # AND the rain-delay guard below — mirroring how a normal zone's
            # run_zone bypasses the deficit gate and skip conditions. Without this,
            # a member whose bucket is satisfied would produce an empty to_water and
            # the cycle would silently return False, dropping the manual run.
            # siehe test_distributor_dispatch.py::test_manual_run_waters_non_due_member
            allow = None if only_zone_ids is None else {int(z) for z in only_zone_ids}
            to_water = {
                int(m.get(const.ZONE_ID))
                for m in members
                if allow is None or int(m.get(const.ZONE_ID)) in allow
            }
            if not to_water:
                return False
        else:
            # b10: the rain-delay guard lives in the scheduled (non-force) branch
            # ONLY — a forced manual run bypasses rain delay too, matching run_zone.
            if self._rain_delay_active():
                return False
            # Soil-veto scope (2026-07-06 design): apply the veto ONLY to the members
            # this cycle would actually water — due, intersected with the target subset
            # (only_zone_ids). A wet member that isn't this cycle's target OR isn't due
            # is left untouched (re-anchored on its OWN cycle), matching the normal-zone
            # path (_irrigate_linked_entities vetoes only due zones). This folds in the
            # old H5 subset filter: a subset run waters ONLY the targeted members; the
            # non-targeted-but-due members are then skip-pulsed in the sweep (the ring
            # must still advance through every outlet). Empty candidates / all-vetoed ->
            # return False cleanly before the master is armed.
            # siehe test_distributor_dispatch.py::test_soil_veto_scoped_to_target_subset
            allow = None if only_zone_ids is None else {int(z) for z in only_zone_ids}
            candidates = [
                m
                for m in members
                if self._dist_needs_water(m)
                and (allow is None or int(m.get(const.ZONE_ID)) in allow)
            ]
            survivors = await self._apply_soil_moisture_veto(candidates)
            to_water = {m.get(const.ZONE_ID) for m in survivors}
            if not to_water:
                return False

        # `or default` (not the get-default) so a persisted None can't crash the
        # cycle after the master is already armed.
        pause = max(
            int(distributor.get("pause_seconds") or 300),
            const.DISTRIBUTOR_MIN_PAUSE_SECONDS,
        )
        skip = max(
            int(distributor.get("skip_pulse_seconds") or 30),
            const.DISTRIBUTOR_MIN_SKIP_PULSE_SECONDS,
        )
        confirm_entity = distributor.get("confirm_entity")
        # Normalise the persisted position into 1..n, then sweep in PHYSICAL order
        # STARTING at the current outlet — the device flows on `current` first.
        # Members are sorted 1..n (contiguous, enforced by the mapping validation),
        # so members[current-1] is the outlet flowing now; `current` and `order[i]`
        # stay in lockstep as we advance.
        current = ((int(distributor.get("current_outlet") or 1) - 1) % n) + 1
        order = [members[(current - 1 + k) % n] for k in range(n)]

        # E1 (early-stop): the mechanical ring only advances forward and cannot
        # skip, so LEADING non-due outlets between `current` and a later due one
        # must still be skip-pulsed to physically reach it. But once the LAST due
        # outlet in the swept order has watered, there is nothing left to reach:
        # sweeping the TRAILING non-due outlets only wastes water/time. So bound the
        # sweep to the prefix ending at the last due outlet and let the next cycle
        # continue from where the ring rests. NOTE (b12): the ring rests ONE past
        # the last watered outlet — that outlet's own watering pulse advances the
        # mechanism (booked as the terminal _dist_advance after the loop) — so
        # `current_outlet` ends at last-due + 1, never on the last watered outlet.
        # A test-run is exempt from the early stop — it must visit EVERY outlet so
        # the user can watch each one advance (§commissioning).
        if test_run:
            sweep_len = n
        else:
            last_due = max(
                i for i in range(n) if order[i].get(const.ZONE_ID) in to_water
            )
            sweep_len = last_due + 1

        # Bug 1 (2026-07-06): snapshot the master-off deadline that pre-existed this
        # sweep. A genuine concurrent consumer (a parallel normal-zone run) sets it
        # BEFORE _dispatch_distributor_cycles runs (scheduler.py:782-787 /
        # irrigation.py:1468-1490 note the normal zones first). The terminal
        # _dist_master_end keys its synchronous-vs-defer decision on THIS snapshot, not
        # on the static parallel flag, so a solo run collapses the master at the last
        # valve close instead of dead-heading ~80 s on the inflated rolling deadline.
        pre_deadline = getattr(self, "_master_off_deadline", None)
        # Track the ceiling of THIS sweep's OWN rolling notes so the terminal can tell
        # our own inflation apart from a foreign consumer that claims the master
        # mid-sweep (a manual normal-zone run) — Bug 1 hardening (2026-07-06, post-review).
        own_deadline = None
        await self._dist_master_start(distributor)
        for i, zone in enumerate(order[:sweep_len]):
            zid = zone.get(const.ZONE_ID)
            if test_run:
                water = False
                window = fixed
            else:
                water = zid in to_water
                window = float(zone.get(const.ZONE_DURATION) or 0) if water else skip
                # M-BE: a manual member run_zone routes through this cycle with a
                # single targeted outlet (only_zone_ids filters to_water), so exactly
                # the requested member is water=True. Honour the caller's custom
                # duration for that outlet instead of its stored daily duration; the
                # non-targeted outlets keep their skip window (they never enter this
                # branch as water=True). siehe
                # test_distributor_dispatch.py::test_cycle_duration_override_sets_target_window
                if duration_override is not None and water:
                    window = float(duration_override)

            # Part B (early stop): a watered member with a rate flow meter and a
            # positive volume target stops at the target instead of running the full
            # window. classic (we hold the inlet) may run up to the safety
            # maximum_duration to reach the target — past the nominal window when the
            # real flow is slower than the configured throughput. A self-closing valve
            # can only be stopped EARLY within its passed window (extension impossible),
            # and only when a stop_service is configured. The master note below uses
            # `cap` so the pump covers the (possibly extended) run; the terminal
            # _dist_master_end collapses it to the real close. `cap == window` for every
            # non-extend path, so the master note is byte-for-byte b23 there.
            # siehe docs/superpowers/specs/2026-07-07-distributor-flow-volume-part-b-design.md
            target = None
            cap = window
            if water:
                mode = distributor.get("watering_mode")
                can_stop = mode == const.WATERING_MODE_CLASSIC or (
                    mode == const.WATERING_MODE_SERVICE
                    and bool(distributor.get("stop_service"))
                )
                tv = self._metered_target_volume(zone, self._zone_target_bucket(zone))
                if distributor.get("flow_sensor") and tv > 0 and can_stop:
                    target = tv
                    if mode == const.WATERING_MODE_CLASSIC:
                        cap = max(
                            window,
                            float(zone.get(const.ZONE_MAXIMUM_DURATION) or 14400),
                        )

            # H7 (live test 2026-07-05): rolling per-outlet master-off note.
            # Root cause of the ~9 min over-run: H1 noted ONE upfront
            # distributor_cycle_estimate(ALL members), which assumes every member
            # waters its FULL duration; skip-pulsed members (soil-veto / not-due)
            # make the real sweep far shorter, so on the concurrent path the master
            # rode the over-estimated deadline long past the last outlet's close.
            # Fix: hold the shared master-off deadline just far enough ahead to
            # cover THIS outlet's confirm + window + pause (+ margin), re-noted each
            # iteration. _master_note_run only ever EXTENDS (max()), so a concurrent
            # normal-zone run's longer deadline still wins (see
            # test_concurrent_longer_normal_zone_deadline_wins); the deadline
            # collapses to the real sweep end (the terminal _dist_master_end notes
            # 0), so the pump no longer over-runs.
            # `pause` is INCLUDED (not just window): after the window closes there is
            # a `pause` sleep before we advance and re-note the next outlet, so the
            # deadline must survive window + pause to avoid lapsing mid-sweep — the
            # plan's "+skip only" draft bound omitted this. distributor_cycle_estimate
            # is left intact — still used by skip_conditions.get_total_irrigation_duration.
            # siehe test_distributor_dispatch.py::test_master_note_is_rolling_not_upfront_estimate
            if not test_run and self._dist_uses_master(distributor):
                settle = float(
                    getattr(self._master_cfg(), const.CONF_MASTER_SETTLE_SECONDS, 10)
                    or 0
                )
                note = (
                    cap + pause + settle + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS
                )
                # If a confirm_entity is set, _confirm_valve_running polls for up to
                # VALVE_CONFIRM_TIMEOUT (30s) BETWEEN open-inlet and the window
                # sleep. That poll is bounded, but a slow confirm could exceed the
                # safety buffer alone and lapse the deadline before the window even
                # starts — so add the bounded confirm timeout to the note when a
                # confirm target exists. (No confirm target -> the buffer is the
                # documented margin; leave it as-is.)
                if confirm_entity:
                    note += float(const.VALVE_CONFIRM_TIMEOUT)
                note_deadline = self._master_note_run(note)
                # Track only genuine datetime returns (a unit test may mock
                # _master_note_run to return a Mock). The datetime class is taken from
                # `_master_now()` — NOT `import datetime` — because this package ships a
                # sibling `datetime.py` platform that shadows a plain `datetime` import
                # here (see __init__.py). own_deadline is the EXACT deadline our notes
                # set, so a no-foreign terminal sees current == own_deadline and
                # collapses; only a foreign later note makes current > own_deadline.
                if isinstance(note_deadline, type(self._master_now())) and (
                    own_deadline is None or note_deadline > own_deadline
                ):
                    own_deadline = note_deadline
                await self.async_master_schedule_off()

            await self._dist_persist_cycle(
                dist_id, current, const.DISTRIBUTOR_PHASE_WATERING
            )
            await self._dist_open_inlet(distributor, window)

            if confirm_entity:
                # Poll the shared inlet flow sensor across its grace window
                # (_confirm_valve_running polls until VALVE_CONFIRM_TIMEOUT — NOT
                # a single poll). retry=False = poll-only: the confirm target is a
                # flow sensor, which must never be re-actuated. None (unreadable)
                # fails open (only a definite False halts).
                confirmed = await self._confirm_valve_running(
                    zid, confirm_entity, retry=False
                )
                if confirmed is False:
                    await self._dist_close_inlet(distributor)
                    await self._dist_master_end(
                        distributor,
                        pre_deadline=pre_deadline,
                        own_deadline=own_deadline,
                    )
                    await self._dist_clear_cycle(dist_id)
                    await self._dist_mark_uncertain(
                        distributor, reason=const.PROBLEM_VALVE_DID_NOT_OPEN
                    )
                    return False

            measured, actual_seconds, _ = await self._dist_measure_window(
                distributor, window, cap=cap, target=target
            )
            if water:
                await self._dist_credit_zone(
                    zone, actual_seconds, measured_l=measured, planned_seconds=window
                )
            await self._dist_close_inlet(distributor)

            # E1 (early-stop): the inter-outlet pause + master re-arm run only
            # BETWEEN swept outlets. After the last swept outlet (i == sweep_len - 1)
            # there is no trailing pause and no master re-window. The last outlet's
            # OWN advance (its watering pulse steps the ring forward — the mechanism
            # indexes on the valve OFF edge, so it cannot stay on the outlet it just
            # watered) is booked once AFTER the loop instead (see the terminal
            # _dist_advance below). The old `if i < n - 1: window_on` guard folds
            # into this same "not the last swept outlet" condition.
            if i < sweep_len - 1:
                await self._dist_persist_cycle(
                    dist_id, current, const.DISTRIBUTOR_PHASE_PAUSING
                )
                await self._dist_master_window_off(distributor, concurrent)
                await self._dist_sleep(pause)
                current = await self._dist_advance(dist_id, current, n)
                await self._dist_master_window_on(distributor, concurrent)

        # b12 (live test 2026-07-05): book the LAST watered outlet's own advance.
        # A Gardena-style distributor indexes on every valve OFF / pressure-drop
        # edge, so the terminal outlet's watering pulse (open inlet -> close inlet
        # above) physically steps the ring one outlet forward — the mechanism can
        # NEVER rest on the outlet it just watered. The in-loop _dist_advance is
        # booked at the inter-outlet PAUSE and is suppressed after the last swept
        # outlet (`if i < sweep_len - 1`), so without this the stored position ends
        # one outlet BEHIND the hardware.
        # Root: the advance was tied to the PAUSE, not to the valve OFF edge; the
        # terminal pulse has no trailing pause, so its advance was never counted.
        # Symptom (live): a manual single-outlet run left current_outlet on the
        # just-watered outlet (before=2, one 120s pulse on outlet 2, stayed 2 while
        # the ring physically stepped to 3); a full sweep ended on the last outlet
        # instead of returning home; the desync then accumulates every cycle so the
        # next sweep skip-pulses/waters the WRONG physical outlets.
        # Fix: after any completed sweep, advance once more so current_outlet == the
        # outlet the ring now rests on == what the NEXT pulse will water. Same
        # per-pulse semantic _dist_on_inlet_pulse already uses for foreign pulses
        # ((cur % n) + 1), so the cycle and the inlet-watch now agree. For a full
        # ring (test-run or all-due) this wraps back to the start outlet (a full
        # loop physically returns home). Reached only after >=1 pulse — every
        # empty/rain/veto/confirm-fail path returns earlier, so it never fires on a
        # no-op cycle. Ordered BEFORE _dist_clear_cycle so active_cycle is still set
        # (the inlet-watch ignores in-cycle edges); the advance is a store write,
        # not a valve actuation, so it fakes no foreign pulse.
        # NOT-TO-DO: do not instead drop the `i < sweep_len - 1` guard to advance
        # in-loop after the last outlet — that would also re-arm the master window
        # and emit a spurious pause for a sweep that has already finished. Book the
        # terminal advance here, exactly once.
        # siehe test_distributor_cycle.py::test_manual_single_target_advances_past_watered_outlet
        current = await self._dist_advance(dist_id, current, n)

        await self._dist_master_end(
            distributor, pre_deadline=pre_deadline, own_deadline=own_deadline
        )
        await self._dist_clear_cycle(dist_id)
        return True

    async def async_run_distributor_test(self, distributor: dict) -> bool:
        """Commissioning test-run: sweep EVERY outlet for a fixed short window
        (DISTRIBUTOR_TEST_RUN_SECONDS) regardless of due/skip, so the user can
        watch that each zone waters in order and the device advances reliably.
        Requires synced but is exempt from the commissioning-confirmed gate
        (§10); never credits a bucket."""
        return await self.async_run_distributor_cycle(distributor, test_run=True)

    # --- manual re-sync (recovery) ----------------------------------------

    async def async_distributor_set_outlet(self, distributor_id, outlet: int) -> None:
        """Re-sync: the user read the physical window and sets the current outlet.
        Marks the position synced. Does NOT re-arm commissioning_confirmed — the
        user re-confirms that separately (spec §7)."""
        await self._dist_store_update(
            distributor_id,
            {
                "current_outlet": int(outlet),
                "position_state": const.POSITION_STATE_SYNCED,
            },
        )

    async def async_distributor_resync_home(self, distributor_id) -> None:
        """Convenience re-sync to outlet 1."""
        await self.async_distributor_set_outlet(distributor_id, 1)

    # --- restart reconciliation -------------------------------------------

    async def async_resume_distributor_cycles(self) -> None:
        """Reconcile in-flight distributor cycles after a restart (spec §7).

        crashed mid-watering (before the advance) -> the position is still known
        (current_outlet == the watered outlet): defensively close the inlet and
        clear the in-flight record, staying synced.
        crashed mid-pausing (the advance may or may not have completed on the
        blind device) -> mark uncertain (de-arm) and require a re-sync.
        """
        for dist in await self.store.async_get_distributors():
            cycle = dist.get("active_cycle") or {}
            if not cycle:
                continue
            await self._dist_close_inlet(dist)
            await self._dist_clear_cycle(dist.get("id"))
            if cycle.get("phase") == const.DISTRIBUTOR_PHASE_PAUSING:
                await self._dist_mark_uncertain(
                    dist, reason=const.DISTRIBUTOR_REASON_RESTART_MID_ADVANCE
                )

    # --- service handlers -------------------------------------------------

    def _dist_from_call(self, call) -> dict:
        """Resolve the distributor dict from a service call's distributor_id."""
        did = call.data.get(const.ATTR_DISTRIBUTOR_ID)
        if did is None:
            raise const.SmartIrrigationError("distributor_id is required")
        dist = self.store.get_distributor(did)
        if dist is None:
            raise const.SmartIrrigationError(f"No distributor with id {did}")
        return dist

    async def handle_distributor_set_outlet(self, call) -> None:
        """Service: re-sync the current outlet (user read the physical window)."""
        dist = self._dist_from_call(call)
        outlet = call.data.get(const.ATTR_OUTLET)
        if outlet is None:
            raise const.SmartIrrigationError("outlet is required")
        await self.async_distributor_set_outlet(dist["id"], int(outlet))

    async def handle_distributor_resync_home(self, call) -> None:
        """Service: re-sync to outlet 1."""
        dist = self._dist_from_call(call)
        await self.async_distributor_resync_home(dist["id"])

    async def handle_distributor_test_run(self, call) -> None:
        """Service: commissioning test-run (fixed short window per outlet)."""
        dist = self._dist_from_call(call)
        await self.async_run_distributor_test(dist)

    async def handle_distributor_run_now(self, call) -> None:
        """Service: run one full cycle now (manual, exclusive). Best-effort
        single-flight: rejected if a cycle is already in progress — a snapshot
        check on the persisted active_cycle at call time, adequate for a
        manually-invoked service (true locking is deferred to the scheduler plan)."""
        dist = self._dist_from_call(call)
        if dist.get("active_cycle"):
            raise const.SmartIrrigationError(
                f"Distributor {dist['id']} already has a cycle in progress"
            )
        await self.async_run_distributor_cycle(dist, concurrent=False)

    # --- config CRUD (frontend POST) --------------------------------------

    async def async_upsert_distributor(self, data: dict):
        """Create / update / delete a distributor from a frontend config POST.

        Routing mirrors the zone config POST: ``remove: true`` deletes; an ``id``
        that is present (INCLUDING 0 — a valid distributor id) updates; otherwise
        it creates. Unknown keys are dropped by the store CRUD (attrs allowlist).

        Update/delete of a missing id raises SmartIrrigationError (→ a clean 400
        in the view) instead of letting the store's KeyError surface as a 500 —
        a stale / duplicate / delete-then-edit form submit must fail gracefully,
        mirroring the zone config path's existence guard."""
        data = dict(data)
        remove = bool(data.get(const.ATTR_REMOVE))
        did = data.get("id")
        if remove or did is not None:
            if did is None or self.store.get_distributor(did) is None:
                raise const.SmartIrrigationError(f"Distributor {did} not found")
            if remove:
                res = await self.store.async_delete_distributor(did)
                async_dispatcher_send(
                    self.hass, const.DOMAIN + "_distributor_removed", int(did)
                )
                # Plan I review (2026-07-05): the dispatcher above makes the
                # platforms drop this distributor's ENTITIES, but nothing removed
                # the per-distributor DEVICE — an empty device lingered in the
                # registry across create/delete cycles. Mirror the zone-delete
                # cleanup (__init__.py async_remove_zone, ~L1415): look the device
                # up by its distributor identifier (self.id == coordinator_id) and
                # remove it. siehe test_distributor_entities.py::
                # test_upsert_delete_removes_device.
                registry = dr.async_get(self.hass)
                device = registry.async_get_device(
                    identifiers={(const.DOMAIN, f"{self.id}_distributor_{int(did)}")}
                )
                if device:
                    registry.async_remove_device(device.id)
                # E4: drop this distributor's inlet-watch listener on delete.
                w = getattr(self, "_dist_inlet_watchers", {}).pop(int(did), None)
                if w:
                    w()
                return res
            data.pop("id")
            data.pop(const.ATTR_REMOVE, None)
            updated = await self._dist_store_update(did, data)
            # E4: re-arm the inlet-watch listener per the new watch_inlet /
            # inlet_entity values (handles toggling watch on or off).
            self._dist_refresh_inlet_watch(updated)
            return updated
        created = await self.store.async_create_distributor(data)
        async_dispatcher_send(
            self.hass, const.DOMAIN + "_distributor_register_entity", created
        )
        # E4: arm the inlet-watch listener for the freshly created distributor.
        self._dist_refresh_inlet_watch(created)
        return created
