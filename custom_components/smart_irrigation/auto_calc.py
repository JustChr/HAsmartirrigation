"""When the automatic calculation runs.

A mixin on ``SmartIrrigationCoordinator``. The historic mode commits the
calculation at a fixed clock time (``calctime``), which leaves the ledger
progressively staler through the day: a run dispatched at 05:00 against a
ledger committed at 23:00 is sized from six hours of missing ET. The
"before each irrigation run" mode instead commits when a run is planned, so
the deficit driving the run is minutes old rather than hours.

That trade has one failure mode, and this module owns both halves of it: the
ledger only advances when runs happen, so a stretch with no runs freezes it,
and past ``BUFFER_RETENTION`` the replay window can no longer be rebuilt at
all. :meth:`AutoCalcMixin.async_guard_ledger_staleness` holds the invariant
rather than enumerating the ways a run can fail to happen.
"""

import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util

from . import const
from .helpers import normalize_zone_selection
from .live_estimate import _parse_local_naive

_LOGGER = logging.getLogger(__name__)


class AutoCalcMixin:
    """Automatic-calculation mode for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state
    (store, calculation entry points).
    """

    def _before_run_calc_active(self) -> bool:
        """Whether the calculation is driven by runs rather than by the clock."""
        config = getattr(self.store, "config", None)
        if (
            getattr(config, "autocalcmode", None)
            != const.CONF_AUTO_CALC_MODE_BEFORE_RUN
        ):
            return False
        return bool(getattr(config, "autocalcenabled", True))

    async def async_commit_pre_run_calculation(self, zones=None) -> None:
        """Commit a calculation immediately before a run, if the mode asks for it.

        Called from a schedule's decision point, or from the dispatch itself for
        a schedule that has no decision point. A no-op under the fixed-time
        mode, which keeps ``calctime``'s original meaning.

        Deliberately ahead of the skip evaluation, so a run that is then skipped
        for rain still leaves a fresh ledger behind rather than a stale one.
        """
        if not self._before_run_calc_active():
            return
        _LOGGER.info("Committing the pre-run calculation for zones: %s", zones)
        selection = normalize_zone_selection(zones)
        if selection is None:
            await self._async_calculate_all()
        else:
            for zone_id in selection:
                await self.async_update_zone_config(
                    zone_id, {const.ATTR_CALCULATE: True}
                )

    async def async_guard_ledger_staleness(self):
        """Commit a calculation if nothing has committed one in 24 hours.

        Rides the existing midnight tracker. Only relevant under the before-run
        mode, where the ledger is committed by runs rather than by a clock — so a
        stretch with no runs freezes it. No schedule needs deleting for that: a
        rain delay, a disabled schedule, an elapsed end_date, or every targeted
        zone disabled all produce zero runs just as effectively.

        After seven days the replay window outruns ``BUFFER_RETENTION``,
        ``build_hourly_rows`` refuses it, and the live estimate silently falls
        back to a week-old bucket. Rather than guard each of those cases, hold
        the invariant: the ledger is never more than a day stale. A no-op in
        normal operation, and it defers harmlessly if it lands mid-run.
        """
        if not self._before_run_calc_active():
            return
        # Naive local, because that is what the store holds: calculation.py
        # stamps last_calculated with a bare datetime.now(). Comparing in that
        # space is what _parse_local_naive exists for.
        cutoff = dt_util.now().replace(tzinfo=None) - timedelta(
            hours=const.AUTO_CALC_MAX_LEDGER_AGE_HOURS
        )
        # Only the zones the commit can actually advance. _async_calculate_all
        # skips anything not automatic, so counting a disabled or manual zone as
        # stale latches the guard permanently: its stamp is old, the calculation
        # never touches it, and every following midnight sees the same stale
        # stamp. The guard would then fire nightly forever whether or not the
        # ledger were rotting, which both makes the before-run mode a
        # midnight-calculation mode and destroys the guard's ability to observe
        # the condition it exists for.
        automatic = [
            zone
            for zone in await self.store.async_get_zones()
            if zone.get(const.ZONE_STATE) == const.ZONE_STATE_AUTOMATIC
        ]
        if not self._any_zone_ledger_older_than(automatic, cutoff):
            return
        _LOGGER.info(
            "No calculation committed in %sh under the before-run calculation "
            "mode; committing one now so the replay window stays inside the "
            "reading buffer's retention",
            const.AUTO_CALC_MAX_LEDGER_AGE_HOURS,
        )
        await self._async_calculate_all()

    @staticmethod
    def _any_zone_ledger_older_than(zones, cutoff) -> bool:
        """Whether any zone was last calculated before ``cutoff`` (or never).

        ``cutoff`` is naive local. The stamps arrive as ISO STRINGS, not
        datetimes — ``store.async_get_zones`` hands back ``attr.asdict`` of an
        entry hydrated from JSON — so they go through the same parser the live
        estimate uses rather than being treated as datetimes. A zone that has
        never been calculated, or whose stamp will not parse, counts as stale:
        the only consequence is committing a calculation that was not strictly
        due, and erring the other way is what leaves the ledger to rot.
        """
        for zone in zones:
            last = _parse_local_naive(zone.get(const.ZONE_LAST_CALCULATED))
            if last is None or last < cutoff:
                return True
        return False
