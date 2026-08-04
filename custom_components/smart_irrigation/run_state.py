"""One answer to "does this zone have a run in flight right now?".

The state exists per actuation mode and nowhere together: ``_active_runs`` for
classic linked-entity runs (in memory), ``CONF_ACTIVE_VALVE_RUNS`` for
self-closing runs (persisted), and the owning distributor's ``active_cycle`` for
a member zone. Two separate defects need exactly this lookup, so it lives here
once:

* **Calculation vs run.** Every run path settles the bucket from an anchor taken
  before the valve opened - ``original_bucket`` in ``_run_valve_metered``,
  ``RUN_PRE_BUCKET`` in the self-closing record, the member snapshot the
  distributor sweep iterates. That absolute reconcile is deliberate (a delta
  correction would over-/under-shoot whenever the optimistic credit clamped at
  ``maximum_bucket``), but it means a calculation landing mid-run is overwritten
  and that window's evapotranspiration is lost. So the calculation gives way:
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
            started = dt_util.parse_datetime(run.get(const.RUN_STARTED) or "")
            if started is None:
                return True
            return (dt_util.utcnow() - started).total_seconds() < planned
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

    def zone_run_in_flight(self, zone_id) -> bool:
        """True while ANY actuation path is watering this zone."""
        try:
            zid = int(zone_id)
        except (TypeError, ValueError):
            return False
        return (
            self._classic_run_in_flight(zid)
            or self._self_closing_run_in_flight(zid)
            or self._distributor_run_in_flight(zid)
        )

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
