"""One answer to "does this zone have a run in flight right now?".

The state exists per actuation mode and nowhere together: ``_active_runs`` for
classic linked-entity runs (in memory), ``CONF_ACTIVE_VALVE_RUNS`` for
self-closing runs (persisted), the owning distributor's ``active_cycle`` for a
member zone, and ``_observed_on_since`` for a run nothing in here started (in
memory, no record at all). Two separate defects need exactly this lookup, so it
lives here once:

* **Calculation vs run.** Every run path settles the bucket from an anchor taken
  before the valve opened - ``original_bucket`` in ``_run_valve_metered``,
  ``RUN_PRE_BUCKET`` in the self-closing record, the member snapshot the
  distributor sweep iterates. That absolute reconcile is deliberate (a delta
  correction would over-/under-shoot whenever the optimistic credit clamped at
  ``maximum_bucket``), but it means a calculation landing mid-run is overwritten
  and that window's evapotranspiration is lost.
  The observed path inverts this rather than sharing it: it credits a delta read
  at the close, so nothing of its own is clobbered - but a calculation that read
  the zone before that credit landed and wrote afterwards would erase it, because
  the calculation's own bucket write is absolute.
  So the calculation gives way:
  ``async_calculate_zone`` returns before consuming anything and the zone is
  marked for a recalculation once the run finalises. Nothing is lost by waiting -
  ``last_consumed_at`` is only advanced on the write path, so the readings stay
  in the buffer and the later calculation folds in the whole window.

* **Duplicate dispatch.** Nothing refused to start a zone that was already
  running, except for distributors. The demand gate (``duration > 0 AND bucket <
  bucket_threshold``) masked it only because both paths credit the bucket early
  enough to fail it - an accident, not a guard, and it does not apply at all
  within the first ``RUN_COMMIT_INTERVAL`` of a classic run or on any path that
  bypasses the gate (Irrigate-now, run_zone). Live: two Irrigate-now dispatches
  10 s apart delivered two full runs, 102.43 L each, credited once.
"""

from __future__ import annotations

import logging

from homeassistant.util import dt as dt_util

from . import const
from .opensprinkler import queue_deadline_seconds
from .run_watch import run_finish_grace_seconds, run_is_queue_bound

_LOGGER = logging.getLogger(__name__)


class RunStateMixin:
    """In-flight run lookup + deferred-calculation bookkeeping.

    Mixed into SmartIrrigationCoordinator.
    """

    # --- "is this zone running?" -------------------------------------------

    def _classic_run_in_flight(self, zone_id: int) -> bool:
        """A linked-entity run loop currently holds this zone's valve open."""
        return zone_id in (getattr(self, "_active_runs", None) or {})

    def _self_closing_run_in_flight(self, zone_id: int) -> bool:
        """A persisted self-closing run for this zone is still inside its window.

        Bounded by the run's OWN planned window rather than by the record's mere
        existence: the hardware owns the close, so past ``planned_seconds`` the
        valve is shut and only the cosmetic finalisation is outstanding. Treating
        an overdue record as "running" would let one that outlived its finaliser
        (a crash before ``async_resume_self_closing_runs`` reconciles it) block
        every future run of that zone with no way out.

        Which instant that window is measured from is the whole difficulty for an
        OpenSprinkler run. ``RUN_STARTED`` is the dispatch, and the controller
        waters one station at a time, so a zone queued behind three others would
        stop counting as in flight ``planned_seconds`` after dispatch while its
        station had not yet opened - dropping the duplicate-dispatch guard and the
        calculation deferral in the middle of the queue, which is exactly when a
        second dispatch would re-queue a whole cycle the controller has already
        accepted. So it measures from ``RUN_OBSERVED_START`` once the station is
        seen running, and until then treats the run as in flight for as long as it
        could plausibly still be waiting (:func:`queue_deadline_seconds`).

        A confirmed service run stays in flight past its plan for its finish
        grace (debounce + frozen latency margin, :func:`run_finish_grace_seconds`,
        #139), because the run is not over when the window is: its record, its
        watcher and its backstop all live through that grace, waiting for the
        valve's own off report. A second dispatch inside it would replace the
        record that has not settled yet, or let the old run's backstop or
        debounce finalise it mid-confirm with the new run's pump hold and meter.
        Every other record (write-only, pre-update, batch, OpenSprinkler) has a
        grace of 0 and keeps its plain window.
        """
        config = getattr(self.store, "config", None)
        runs = getattr(config, const.CONF_ACTIVE_VALVE_RUNS, None)
        if not isinstance(runs, list):
            return False
        for run in runs:
            if not isinstance(run, dict):
                continue
            try:
                if int(run.get(const.RUN_ZONE_ID)) != zone_id:
                    continue
            except (TypeError, ValueError):
                continue
            planned = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
            if planned <= 0:
                return True
            observed = run.get(const.RUN_OBSERVED_START)
            queued = run_is_queue_bound(run)
            window = (
                queue_deadline_seconds(runs, run)
                if queued
                else planned + run_finish_grace_seconds(run)
            )
            anchor = dt_util.parse_datetime(
                (observed or run.get(const.RUN_STARTED)) or ""
            )
            if anchor is None:
                return True
            return (dt_util.utcnow() - anchor).total_seconds() < window
        return False

    def _distributor_run_in_flight(self, zone_id: int) -> bool:
        """This zone's distributor is mid-sweep (so its member snapshot is live)."""
        zone = self.store.get_zone(zone_id)
        if not isinstance(zone, dict):
            return False
        distributor_id = zone.get(const.ZONE_DISTRIBUTOR_ID)
        if distributor_id is None:
            return False
        get_distributor = getattr(self.store, "get_distributor", None)
        if get_distributor is None:
            return False
        distributor = get_distributor(distributor_id)
        if not isinstance(distributor, dict):
            return False
        return bool(distributor.get("active_cycle"))

    def _observed_run_in_flight(self, zone_id: int) -> bool:
        """An external open this integration did not drive is holding the zone.

        The fourth actuation path, and the only one with no record of its own: observed
        watering credits an external run at its close and registers nothing, so the
        guard at a zone's turn answered False while the valve was open and the cycle
        watered it a second time. It needs no new store -- ``_observed_on_since``
        already holds the instant the external valve opened, which is exactly what "in
        flight" means here.

        Bounded, for the same reason :meth:`_self_closing_run_in_flight` is bounded: an
        entry that outlives its close edge must not block the zone for ever. Unbounded,
        one valve stuck reporting ``open`` would drop the zone from every cycle AND park
        its calculation (which gives way to a run in flight) with no way out. The bound
        is the zone's own external-run ceiling -- the same number its credit is capped
        at -- so a valve still reporting open past the longest plausible run for that
        zone reads as a broken report rather than as water.

        The comparison reads wall-clock time, so a backwards system-clock jump holds
        the zone until the clock passes the ceiling again, and a forward one releases
        a genuinely open run early. :meth:`_self_closing_run_in_flight` has carried
        the same exposure since it was written.

        The reads are defensive because this runs on every ``zone_run_in_flight`` call,
        including on coordinators built with ``__new__`` in tests, where the attribute
        may be absent and ``store`` is often a Mock whose every attribute answers with
        another Mock.
        """
        since = getattr(self, "_observed_on_since", None)
        if not isinstance(since, dict):
            return False
        started = since.get(zone_id)
        if started is None:
            return False
        zone = self.store.get_zone(zone_id)
        ceiling, _substituted = self._observed_run_ceiling_seconds(
            zone if isinstance(zone, dict) else {}
        )
        return (dt_util.utcnow() - started).total_seconds() < ceiling

    def _si_run_in_flight(self, zone_id) -> bool:
        """True while a run THIS INTEGRATION dispatched is holding the zone.

        Split out of :meth:`zone_run_in_flight` when external runs joined that answer.
        The two had been the same question, and one caller only ever meant this
        narrower one: observed watering asks, at a valve's open edge, whether the
        integration opened it, so it can leave its own runs to the runner. Pointed at
        the wider answer it would suppress the tracking of the very runs it is there to
        track, the moment its own tracking fed that answer.
        """
        try:
            zid = int(zone_id)
        except (TypeError, ValueError):
            return False
        return (
            self._classic_run_in_flight(zid)
            or self._self_closing_run_in_flight(zid)
            or self._distributor_run_in_flight(zid)
        )

    def zone_run_in_flight(self, zone_id) -> bool:
        """True while ANY actuation path is watering this zone, ours or not."""
        try:
            zid = int(zone_id)
        except (TypeError, ValueError):
            return False
        return self._si_run_in_flight(zid) or self._observed_run_in_flight(zid)

    # --- deferred calculations ---------------------------------------------

    def _deferred_calc_zone_ids(self) -> set:
        """Lazily-created set of zones whose calculation a run displaced."""
        pending = getattr(self, "_deferred_calc_zones", None)
        if pending is None:
            pending = self._deferred_calc_zones = set()
        return pending

    def defer_zone_calculation(self, zone_id) -> None:
        """Mark a zone for recalculation as soon as its run finalises."""
        try:
            self._deferred_calc_zone_ids().add(int(zone_id))
        except (TypeError, ValueError):
            return

    async def async_run_deferred_calculation(self, zone_id) -> None:
        """Run a calculation this zone's run displaced, now that the run is over.

        Called from every run-finalise path. A no-op unless the zone actually has
        one pending, and re-deferred if another run started in the meantime.
        Routed through ``async_update_zone_config`` rather than
        ``async_calculate_zone`` so a PyETO-with-forecast zone still gets its
        forecast fetched, exactly as a scheduled per-zone calculate does.

        Never allowed to propagate: the callers are run teardown (including a
        ``finally``), and a zone whose mapping has no data raises from
        ``async_update_zone_config``. Missing the recalculation only leaves the
        duration stale until the next scheduled calculate - the weather window is
        still unconsumed, so no evapotranspiration is lost either way.
        """
        pending = getattr(self, "_deferred_calc_zones", None)
        try:
            zid = int(zone_id)
        except (TypeError, ValueError):
            return
        if not pending or zid not in pending:
            return
        pending.discard(zid)
        if self.zone_run_in_flight(zid):
            pending.add(zid)  # a new run took over; try again when that one ends
            return
        _LOGGER.debug("Running the calculation deferred by zone %s's run", zid)
        try:
            await self.async_update_zone_config(
                zone_id=zid, data={const.ATTR_CALCULATE: True}
            )
        except Exception:  # noqa: BLE001 - teardown must not fail on this
            pending.add(zid)
            _LOGGER.warning(
                "Deferred calculation for zone %s failed; it will be picked up by "
                "the next calculation (its weather window is still unconsumed)",
                zid,
                exc_info=True,
            )
