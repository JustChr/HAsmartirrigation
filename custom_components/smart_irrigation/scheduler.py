"""Enhanced scheduling system for Smart Irrigation."""

import datetime
import logging
import uuid
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.event import (
    async_track_point_in_utc_time,
    async_track_sunrise,
    async_track_sunset,
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.helpers.sun import get_astral_event_date, get_astral_event_next

from . import const
from .helpers import (
    find_next_solar_azimuth_time,
    normalize_azimuth_angle,
    normalize_zone_selection,
)
from .run_window import bound_wall_clock, select, simulate_wall_clock

_LOGGER = logging.getLogger(__name__)

_BOUND_FIELDS = {
    const.SCHEDULE_ANCHOR_START: (
        const.SCHEDULE_CONF_START_MODE,
        const.SCHEDULE_CONF_START_TIME,
        const.SCHEDULE_CONF_START_OFFSET,
        const.SCHEDULE_CONF_START_AZIMUTH,
    ),
    const.SCHEDULE_ANCHOR_FINISH: (
        const.SCHEDULE_CONF_FINISH_MODE,
        const.SCHEDULE_CONF_FINISH_TIME,
        const.SCHEDULE_CONF_FINISH_OFFSET,
        const.SCHEDULE_CONF_FINISH_AZIMUTH,
    ),
}


class RecurringScheduleManager:
    """Manages recurring schedules for Smart Irrigation."""

    def __init__(self, hass: HomeAssistant, coordinator) -> None:
        """Initialize the recurring schedule manager."""
        self.hass = hass
        self.coordinator = coordinator
        self._schedule_trackers = {}
        self._schedules = []
        self._unsub_rearm = None
        # Per finish-governed schedule, the target occurrence we last fired for
        # (ISO string). Lets the self-rescheduling tracker advance past an
        # occurrence it already ran instead of busy-looping its window (which
        # re-fired irrigation every ~2s). Keyed by schedule id. Shared by
        # every governed-tracker flavour (finish-only, both-bounded pinned to
        # either end) since only one can be armed for a schedule at a time.
        #
        # Mirrored to const.CONF_FIRED_OCCURRENCES in the config document and
        # rehydrated in async_load_schedules. Holding it only here made the
        # tracker's own catch-up branch unsound: a config entry reload builds a
        # new manager, so a reload inside the window left the fresh manager
        # unable to tell "never ran this occurrence" from "ran it eleven minutes
        # ago", and it watered the occurrence a second time in full. This dict
        # stays the authority while the manager lives; the stored copy only has
        # to be right by the time a NEW manager reads it.
        self._finish_last_target: dict[str, str] = {}
        # Per finish-anchored schedule, the decision last written to the log at
        # INFO. Every config write re-arms the schedule, and past the decision
        # point that re-runs the whole selection — so an unconditional INFO per
        # arm reads as the schedule arming over and over while only one dispatch
        # ever fires. Keyed by schedule id; see _decision_is_new.
        self._decision_logged: dict[str, tuple] = {}

    async def async_load_schedules(self) -> None:
        """Load recurring schedules from configuration."""
        config = await self.coordinator.store.async_get_config()
        self._schedules = config.get(const.CONF_RECURRING_SCHEDULES, [])
        # Anything already in memory wins: a fire records its marker
        # synchronously and persists it in a task, so for a moment the stored
        # copy is behind. Stale ids are dropped by _setup_schedule_trackers.
        stored = config.get(const.CONF_FIRED_OCCURRENCES) or {}
        self._finish_last_target = {**stored, **self._finish_last_target}
        await self._setup_schedule_trackers()

        # Re-arm finish-governed schedules whenever durations may have changed
        # (a calculate dispatches _config_updated). This keeps the computed
        # start time (target − duration) fresh without polling.
        if getattr(self, "_unsub_rearm", None) is None:
            self._unsub_rearm = async_dispatcher_connect(
                self.hass,
                const.DOMAIN + "_config_updated",
                self._on_config_updated,
            )

    async def async_unload(self) -> None:
        """Release every HA listener this manager registered.

        MUST be called from ``SmartIrrigationCoordinator.async_unload``. The
        trackers below are HA event listeners (``async_track_time_change`` /
        ``async_track_sunrise`` / ``async_track_point_in_utc_time``) and a
        dispatcher connection; none of them are tied to the config entry, so
        nothing cancels them implicitly. A config-entry reload builds a NEW
        coordinator and a NEW manager, which arms a fresh set — so without this
        teardown the OLD manager's listeners stay live, still bound to the OLD
        coordinator, and every schedule fires once per surviving manager
        (N reloads => N+1 irrigation runs per schedule).
        See tests/test_run_lifecycle_safety.py.
        """
        for tracker in self._schedule_trackers.values():
            if tracker:
                tracker()
        self._schedule_trackers.clear()
        if self._unsub_rearm is not None:
            self._unsub_rearm()
            self._unsub_rearm = None
        # Deliberately NOT clearing _finish_last_target. It is no longer
        # per-manager memory a fresh manager can re-derive — it is the record
        # that stops a reload inside the start→finish window from watering the
        # same occurrence twice. Clearing it here would also let a persistence
        # task created just before teardown write an empty map back to the
        # store, which is precisely the state the fix exists to avoid.
        #
        # The decision log IS per-manager: it only suppresses repeated log lines
        # within one manager's life, so a fresh one starting from empty costs a
        # single duplicate line rather than a duplicate run.
        self._decision_logged.clear()

    @callback
    def _on_config_updated(self, *_args) -> None:
        """React to config/duration changes by re-arming finish schedules."""
        self.hass.async_create_task(self._async_handle_config_updated())

    async def _async_handle_config_updated(self) -> None:
        """Reload the schedules if the stored list changed, else just re-arm.

        ``self._schedules`` is in-memory state that only ``async_load_schedules``
        assigns from the store, and everything reads through it — including
        ``get_schedules()``, which backs the ``smart_irrigation/schedules``
        websocket command. A writer that puts ``recurring_schedules`` straight
        into the config document therefore left the store and the running
        manager disagreeing: the schedule was persisted and correct on disk, but
        no tracker was ever registered so it never fired, and it was absent from
        the panel until a config entry reload rebuilt the manager. Nothing
        errored in either direction. The panel is not such a writer — it calls
        ``schedule_save``, which routes to ``async_create_schedule`` /
        ``async_update_schedule`` and arms its own tracker — but the REST and
        websocket config endpoints are, and so is anything replaying a stored
        configuration document.

        The diff is a correctness requirement, not an optimisation. This handler
        is wired to ``_config_updated``, which fires on every calculate, and
        every few seconds when continuous updates are enabled. Rebuilding
        unconditionally would tear down and re-arm every tracker on that cadence,
        and re-arming a finish tracker is exactly the operation that can re-fire
        an occurrence. So an undiffed rebuild would not merely be wasteful.
        Same diff-then-rebuild shape as ObservedWateringMixin's tracked entity
        set.
        """
        config = await self.coordinator.store.async_get_config()
        stored = config.get(const.CONF_RECURRING_SCHEDULES) or []
        if stored == self._schedules:
            await self.async_rearm_finish_schedules()
            return

        _LOGGER.debug(
            "Recurring schedules changed outside the schedule manager "
            "(%s stored, %s armed); reloading",
            len(stored),
            len(self._schedules),
        )
        # Rebuilds every tracker, so no separate re-arm afterwards: a redundant
        # finish re-arm is the re-fire operation described above.
        await self.async_load_schedules()
        # schedule_save sends this so the next-irrigation sensors recompute; a
        # writer that bypassed the manager did not, leaving those sensors as
        # stale as the trackers were.
        async_dispatcher_send(self.hass, const.DOMAIN + "_schedules_updated")

    async def async_rearm_finish_schedules(self) -> None:
        """Recompute and re-arm start times for finish-governed schedules.

        A schedule's fire time depends on the estimated duration exactly when
        its Finish bound is the governing end (single-stage finish-only, or
        two-stage pinned to Finish) — the Start-pinned case fires at a fixed
        instant regardless of duration, so it does not need re-arming here.
        """
        for schedule in self._schedules:
            if not schedule.get(const.SCHEDULE_CONF_ENABLED, True):
                continue
            if (
                schedule.get(const.SCHEDULE_CONF_RECURRENCE)
                == const.SCHEDULE_RECURRENCE_INTERVAL
            ):
                continue
            governing, _paired = self._bounded_ends(schedule)
            if governing != const.SCHEDULE_ANCHOR_FINISH:
                continue
            await self._reregister_tracker(schedule)

    async def async_create_schedule(self, schedule_data: dict[str, Any]) -> None:
        """Create a new recurring schedule."""
        # Validate schedule data
        self._validate_schedule_data(schedule_data)

        # Add unique ID if not provided
        if const.SCHEDULE_CONF_ID not in schedule_data:
            schedule_data[const.SCHEDULE_CONF_ID] = self._generate_schedule_id()

        # Add to schedules list
        self._schedules.append(schedule_data)

        # Update configuration
        await self._save_schedules()

        # Set up tracker for this schedule
        await self._setup_schedule_tracker(schedule_data)

        _LOGGER.info(
            "Created recurring schedule: %s", schedule_data[const.SCHEDULE_CONF_NAME]
        )

    async def async_update_schedule(
        self, schedule_id: str, schedule_data: dict[str, Any]
    ) -> None:
        """Update an existing recurring schedule."""
        # Find the schedule
        schedule_index = None
        for i, schedule in enumerate(self._schedules):
            if schedule[const.SCHEDULE_CONF_ID] == schedule_id:
                schedule_index = i
                break

        if schedule_index is None:
            raise ValueError(f"Schedule with ID {schedule_id} not found")

        # Validate updated data
        self._validate_schedule_data(schedule_data)

        # Remove old tracker
        await self._remove_schedule_tracker(schedule_id)

        # Update schedule
        self._schedules[schedule_index].update(schedule_data)

        # Save configuration
        await self._save_schedules()

        # Set up new tracker
        await self._setup_schedule_tracker(self._schedules[schedule_index])

        _LOGGER.info(
            "Updated recurring schedule: %s",
            schedule_data.get(const.SCHEDULE_CONF_NAME, schedule_id),
        )

    async def async_delete_schedule(self, schedule_id: str) -> None:
        """Delete a recurring schedule."""
        # Remove tracker
        await self._remove_schedule_tracker(schedule_id)

        # Remove from schedules list
        self._schedules = [
            s for s in self._schedules if s[const.SCHEDULE_CONF_ID] != schedule_id
        ]

        # Save configuration
        await self._save_schedules()

        _LOGGER.info("Deleted recurring schedule: %s", schedule_id)

    async def _setup_schedule_trackers(self) -> None:
        """Set up all schedule trackers."""
        # Clear existing trackers
        for tracker in self._schedule_trackers.values():
            if tracker:
                tracker()
        self._schedule_trackers.clear()

        # Drop fired-occurrence markers for schedules that no longer exist. It
        # was only ever cleared wholesale on unload, so deleting a schedule left
        # its entry behind for the life of the manager. The key is the schedule
        # id: if an id is ever reused, a NEW finish-governed schedule would
        # inherit the old one's "already fired" marker and skip its first
        # occurrence, silently and once only — the worst kind of bug to
        # reproduce. Now that the map is persisted, pruning must reach the store
        # too, or a stale marker outlives every restart.
        live_ids = {
            s[const.SCHEDULE_CONF_ID]
            for s in self._schedules
            if const.SCHEDULE_CONF_ID in s
        }
        stale_ids = set(self._finish_last_target) - live_ids
        for stale in stale_ids:
            del self._finish_last_target[stale]
        if stale_ids:
            await self._persist_fired_occurrences(dict(self._finish_last_target))

        # Set up trackers for enabled schedules
        for schedule in self._schedules:
            if schedule.get(const.SCHEDULE_CONF_ENABLED, True):
                await self._setup_schedule_tracker(schedule)

    async def _setup_schedule_tracker(self, schedule: dict[str, Any]) -> None:
        """Set up a tracker for a single schedule.

        A run's window is two independently bounded ends, Start and Finish
        (GitLab #27/#21). Interval recurrence has neither — it free-runs on
        its own clock. Otherwise:

          - only one end bounded → that end IS the schedule's anchor; fires
            there directly (single-stage), unbounded on the other side.
          - Finish is that single bound, action is "irrigate" → the classic
            finish-anchored run: fires at (target − estimated duration).
          - both ends bounded, action is "irrigate" → a two-stage arm, pinned
            to whichever end `anchor` names.

        Only an irrigate action's fire time depends on estimated duration or
        truncation; calculate/update schedules always fire at the governing
        end's raw resolved instant, matching every recurrence/mode.
        """
        if not schedule.get(const.SCHEDULE_CONF_ENABLED, True):
            return

        schedule_id = schedule[const.SCHEDULE_CONF_ID]
        recurrence = schedule.get(const.SCHEDULE_CONF_RECURRENCE)

        if recurrence == const.SCHEDULE_RECURRENCE_INTERVAL:
            tracker = await self._setup_interval_tracker(schedule)
            self._schedule_trackers[schedule_id] = tracker
            return

        governing, paired = self._bounded_ends(schedule)
        if governing is None:
            _LOGGER.warning(
                "Schedule '%s': neither Start nor Finish is bounded; not armed",
                schedule.get(const.SCHEDULE_CONF_NAME),
            )
            return

        action = schedule.get(const.SCHEDULE_CONF_ACTION)
        if paired is not None and action == "irrigate":
            tracker = await self._setup_bounded_tracker(schedule, governing)
        elif governing == const.SCHEDULE_ANCHOR_FINISH and action == "irrigate":
            tracker = await self._setup_finish_tracker(schedule, fitted=False)
        else:
            tracker = await self._setup_governing_tracker(schedule, governing)

        self._schedule_trackers[schedule_id] = tracker

    # --- window bounds: which end(s), and resolving one -----------------------

    @staticmethod
    def _bounded_ends(schedule: dict[str, Any]) -> tuple[str | None, str | None]:
        """(governing_end, paired_end) — which end(s) of the window are bounded.

        With both ends bounded, ``anchor`` names the governing one (the run is
        pinned to it) and the other is the paired bound. With only one end
        bounded, that end IS the governing one and ``anchor`` is irrelevant.
        ``(None, None)`` means neither is bounded — invalid, rejected at save
        time by ``_validate_schedule_data``.
        """
        start_mode = schedule.get(
            const.SCHEDULE_CONF_START_MODE, const.SCHEDULE_DEFAULT_BOUND_MODE
        )
        finish_mode = schedule.get(
            const.SCHEDULE_CONF_FINISH_MODE, const.SCHEDULE_DEFAULT_BOUND_MODE
        )
        start_bounded = start_mode != const.SCHEDULE_BOUND_MODE_NONE
        finish_bounded = finish_mode != const.SCHEDULE_BOUND_MODE_NONE

        if start_bounded and finish_bounded:
            anchor = schedule.get(const.SCHEDULE_CONF_ANCHOR)
            if anchor not in const.SCHEDULE_ANCHORS:
                anchor = const.SCHEDULE_DEFAULT_ANCHOR
            paired = (
                const.SCHEDULE_ANCHOR_START
                if anchor == const.SCHEDULE_ANCHOR_FINISH
                else const.SCHEDULE_ANCHOR_FINISH
            )
            return anchor, paired
        if finish_bounded:
            return const.SCHEDULE_ANCHOR_FINISH, None
        if start_bounded:
            return const.SCHEDULE_ANCHOR_START, None
        return None, None

    async def _resolve_bound(
        self, schedule: dict[str, Any], end: str, reference_utc, *, direction: str
    ):
        """Resolve one end ('start' or 'finish') of a schedule's window.

        Thin adapter from a schedule's mode/time/offset/azimuth fields onto
        the shared ``_resolve_event_instant`` seam — the same one the run's
        target and its floor both went through before this ticket, now
        serving either end symmetrically.
        """
        mode_key, time_key, offset_key, azimuth_key = _BOUND_FIELDS[end]
        mode = schedule.get(mode_key, const.SCHEDULE_DEFAULT_BOUND_MODE)
        if mode == const.SCHEDULE_BOUND_MODE_NONE:
            return None

        hour = minute = angle = None
        if mode == const.SCHEDULE_BOUND_MODE_TIME:
            raw = schedule.get(time_key)
            try:
                hour, minute = (int(x) for x in str(raw).split(":"))
            except (ValueError, TypeError, AttributeError):
                _LOGGER.warning(
                    "Schedule '%s': %s time '%s' is not HH:MM; that bound is "
                    "unresolvable",
                    schedule.get(const.SCHEDULE_CONF_NAME),
                    end,
                    raw,
                )
                return None
        offset = datetime.timedelta(minutes=schedule.get(offset_key, 0) or 0)
        if mode == const.SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH:
            angle = schedule.get(azimuth_key, 90)

        kind = "clock" if mode == const.SCHEDULE_BOUND_MODE_TIME else mode
        return await self._resolve_event_instant(
            kind,
            reference_utc,
            direction=direction,
            hour=hour,
            minute=minute,
            angle=angle,
            offset=offset,
        )

    async def _paired_bound_time(
        self, schedule: dict[str, Any], paired_end: str, governing_instant
    ):
        """Resolve the non-governing end relative to the governing instant.

        A Start paired bound resolves BACKWARD from the governing Finish (the
        latest occurrence at or before it — the overnight wrap that keeps a
        22:00 floor on the previous evening against a 06:00 target); a Finish
        paired bound resolves FORWARD from the governing Start. No day-of-week
        filtering here: day-matching gates which occurrence of the *governing*
        end this window belongs to, and the paired bound is part of that same
        window, not a separate occurrence.
        """
        if governing_instant is None:
            return None
        direction = (
            "backward" if paired_end == const.SCHEDULE_ANCHOR_START else "forward"
        )
        resolved = await self._resolve_bound(
            schedule, paired_end, governing_instant, direction=direction
        )
        if resolved is None:
            return None
        # A degenerate pairing — the floor at/after the finish it should
        # precede, or the ceiling at/before the start it should follow —
        # leaves no real window. Honour the governing bound and log it,
        # rather than silently running with an inverted window.
        inverted = (
            resolved >= governing_instant
            if paired_end == const.SCHEDULE_ANCHOR_START
            else resolved <= governing_instant
        )
        if inverted:
            _LOGGER.warning(
                "Schedule '%s': resolved %s bound %s does not precede/follow "
                "its governing bound %s as required; ignoring it",
                schedule.get(const.SCHEDULE_CONF_NAME),
                paired_end,
                resolved,
                governing_instant,
            )
            return None
        return resolved

    async def _resolve_event_instant(
        self,
        kind: str,
        reference_utc,
        *,
        direction: str,
        hour: int | None = None,
        minute: int | None = None,
        angle: float | None = None,
        offset: datetime.timedelta = datetime.timedelta(0),
    ):
        """Resolve one occurrence of a schedule's time source relative to
        ``reference_utc`` — the shared seam every Start/Finish bound resolves
        through, in either direction.

        ``kind`` is one of "clock" (needs ``hour``/``minute``), "sunrise",
        "sunset", or "solar_azimuth" (needs ``angle``). ``offset`` shifts the
        resolved instant before it is compared against ``reference_utc`` — for
        "forward" that means retrying until the shifted instant is strictly
        after the reference (guards a negative offset landing on/before it);
        for "backward" it means walking further back until the shifted instant
        is at or before the reference. Same per-kind math either way, just
        walked in opposite directions.

        Returns None when the occurrence cannot be resolved — a polar sunset/
        sunrise, a malformed clock spec, an azimuth the sun never reaches, or a
        backward walk that exhausts its lookback window — rather than raising,
        matching every caller's "no bound" contract.
        """
        if kind == "clock":
            if hour is None or minute is None:
                return None
            local_ref = dt_util.as_local(reference_utc)
            candidate = local_ref.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            if direction == "forward":
                if candidate <= local_ref:
                    candidate += datetime.timedelta(days=1)
            else:
                # The latest occurrence at or before the reference, so an
                # overnight floor (22:00) resolved against a 06:00 target lands
                # on the PREVIOUS evening rather than jumping forward a day.
                if candidate > local_ref:
                    candidate -= datetime.timedelta(days=1)
            return dt_util.as_utc(candidate)

        if kind in ("sunrise", "sunset"):
            if direction == "forward":
                ev = get_astral_event_next(self.hass, kind, reference_utc)
                candidate = ev + offset
                # A NEGATIVE offset shifts the target before its sun event, so
                # it can land on/before the reference while the raw event is
                # still in the future. Advance to the following event until the
                # shifted candidate is strictly after the reference. Bounded so
                # a pathological offset can't spin. See
                # test_schedule_time_anchor::TestFinishTrackerAdvance.
                guard = 0
                while candidate <= reference_utc and guard < 8:
                    ev = get_astral_event_next(self.hass, kind, ev)
                    candidate = ev + offset
                    guard += 1
                return candidate
            # Backward: walk back across days looking for an occurrence whose
            # offset-adjusted instant lands at or before the reference.
            local_date = dt_util.as_local(reference_utc).date()
            for back in (0, 1):
                event = get_astral_event_date(
                    self.hass, kind, local_date - datetime.timedelta(days=back)
                )
                if event is None:
                    continue
                candidate = dt_util.as_utc(event) + offset
                if candidate <= reference_utc:
                    return candidate
            return None

        if kind == "solar_azimuth":
            if angle is None:
                return None
            ha_cfg = self.hass.config.as_dict()
            lat = ha_cfg.get(CONF_LATITUDE, 45.0)
            lon = ha_cfg.get(CONF_LONGITUDE, 0.0)
            norm_angle = normalize_azimuth_angle(angle)
            # UTC, aware, end to end, in BOTH directions. calculate_solar_azimuth
            # documents (and reads) UTC and takes a naive value AS UTC, so
            # handing it naive local time put the zone offset on top of the sign
            # error the helper itself had — see issue #81. dt_util.as_utc on an
            # already-UTC value is a no-op, so the offset arithmetic around each
            # crossing is unchanged.
            if direction == "forward":
                ref = reference_utc
                # Same negative-offset advance as sunrise/sunset above: step
                # past the found occurrence until the offset-shifted candidate
                # is strictly after the reference, so the finish tracker
                # doesn't busy-loop.
                guard = 0
                while True:
                    next_time = find_next_solar_azimuth_time(
                        lat, lon, norm_angle, ref
                    )
                    if next_time is None:
                        return None
                    candidate = dt_util.as_utc(next_time) + offset
                    if candidate > reference_utc or guard >= 8:
                        return candidate
                    # find_next_solar_azimuth_time samples in 15-min steps, so a
                    # tiny step re-detects the SAME crossing. Step past a full
                    # search interval so the next search lands on the following
                    # crossing.
                    ref = next_time + datetime.timedelta(minutes=16)
                    guard += 1
            # Backward: scan each local day, most recent first, from midnight,
            # keeping the latest crossing whose offset-adjusted instant is
            # still at or before the reference — mirrors the sunset walk.
            local_ref = dt_util.as_local(reference_utc)
            for back in (0, 1):
                day_start_local = local_ref.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) - datetime.timedelta(days=back)
                # The DAY is local; the instants scanned across it are UTC, per
                # the frame note on the forward branch.
                scan_from = dt_util.as_utc(day_start_local)
                day = day_start_local.date()
                found = None
                guard = 0
                while guard < 96:
                    crossing = find_next_solar_azimuth_time(
                        lat, lon, norm_angle, scan_from
                    )
                    if crossing is None or dt_util.as_local(crossing).date() != day:
                        break
                    candidate = dt_util.as_utc(crossing) + offset
                    if candidate > reference_utc:
                        break
                    found = candidate
                    scan_from = crossing + datetime.timedelta(minutes=16)
                    guard += 1
                if found is not None:
                    return found
            return None

        return None

    @staticmethod
    def _recurrence_day_matches(schedule: dict[str, Any], dt_local) -> bool:
        """Whether a daily/weekly/monthly schedule should run on dt_local's day.

        Switches on ``recurrence``, independent of which bound mode produced
        the candidate instant — this is what lets a weekly schedule carry a
        sun-relative bound: recurrence and time-of-day are orthogonal, so
        weekday filtering applies no matter which kind of bound is in play.
        """
        recurrence = schedule.get(const.SCHEDULE_CONF_RECURRENCE)
        if recurrence == const.SCHEDULE_RECURRENCE_DAILY:
            return True
        if recurrence == const.SCHEDULE_RECURRENCE_WEEKLY:
            day_map = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
            }
            days = [
                d.lower() for d in schedule.get(const.SCHEDULE_CONF_DAYS_OF_WEEK, [])
            ]
            return any(day_map.get(d) == dt_local.weekday() for d in days)
        if recurrence == const.SCHEDULE_RECURRENCE_MONTHLY:
            return dt_local.day == schedule.get(const.SCHEDULE_CONF_DAY_OF_MONTH, 1)
        return False

    async def _next_governing_time(
        self, schedule: dict[str, Any], end: str, reference_utc=None
    ):
        """Next UTC instant the schedule's governing ``end`` occurs.

        Honours day-matching for daily/weekly/monthly recurrence: the resolver
        gives the next raw occurrence of the bound; re-anchor on it and ask
        again until the day matches, so weekday/day-of-month filtering wraps
        the shared resolver rather than duplicating its clock/sun math. For a
        "daily" recurrence every candidate matches, so this returns the first
        one, same as calling the resolver directly.

        ``reference_utc`` is the moment the "next" occurrence must fall
        strictly after; defaults to now. Pass a prior target to get the
        occurrence *after* it (used to advance past one already fired).
        """
        now_utc = reference_utc or dt_util.utcnow()
        candidate_ref = now_utc
        for _ in range(367):
            candidate = await self._resolve_bound(
                schedule, end, candidate_ref, direction="forward"
            )
            if candidate is None:
                return None
            if self._recurrence_day_matches(schedule, dt_util.as_local(candidate)):
                return candidate
            candidate_ref = candidate
        return None

    async def _estimate_duration(self, schedule: dict[str, Any]) -> int:
        """Estimated wall-clock run length (seconds) for the schedule's zones."""
        zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")
        return await self.coordinator.get_total_irrigation_duration(zones)

    async def _duration_bound(self, schedule: dict[str, Any]) -> float:
        """Longest wall clock the schedule's zones could occupy, in seconds.

        Priced from each zone's configured ``maximum_duration``, so it is a
        function of configuration alone. That is the whole point: it gives
        ``target − bound`` a fixed point to arm on days ahead, before any
        deficit is known, when the paired Start bound can't supply one.
        """
        zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")
        # ignore_demand, unconditionally: the bound has to cover every zone this
        # schedule could water by the time the decision point arrives, not the
        # ones that happen to be due while it is being armed. Pricing only the
        # currently-due zones would move the decision point every time a zone
        # crossed its threshold — the exact demand-dependence the bound exists
        # to remove.
        plan = await self.coordinator.async_plan_zone_runs(
            zones, runnable_only=True, ignore_demand=True
        )
        sequencing, slot, absorption = self.coordinator.sequencing_timing()
        return bound_wall_clock(
            plan,
            sequencing=sequencing,
            max_slot_seconds=slot,
            min_absorption_seconds=absorption,
        )

    def _next_interval_target(self, schedule: dict[str, Any], reference_utc):
        """Next UTC fire time for an interval schedule anchored to ``start_time``.

        Occurrences are the local ``start_time`` clock and every
        ``interval_hours`` after it, phase-locked to that anchor (the candidate
        rolls naturally across midnight). Returns None when there is no
        ``start_time`` (un-anchored interval), an invalid time, or a
        non-positive interval — in those cases the schedule free-runs via
        ``async_track_time_interval`` and has no derivable clock target.
        """
        start_time_str = schedule.get(const.SCHEDULE_CONF_START_TIME)
        if not start_time_str:
            return None
        try:
            hour, minute = (int(x) for x in str(start_time_str).split(":"))
        except (ValueError, TypeError):
            return None
        interval_hours = schedule.get(const.SCHEDULE_CONF_INTERVAL_HOURS, 24)
        if interval_hours is None:
            interval_hours = 24
        try:
            interval_hours = int(interval_hours)
        except (ValueError, TypeError):
            return None
        if interval_hours <= 0:
            return None

        local_now = dt_util.as_local(reference_utc)
        candidate = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        step = datetime.timedelta(hours=interval_hours)
        # Advance from today's anchor until strictly after the reference. Bounded
        # by a full day's worth of steps plus slack, so it can never spin.
        for _ in range(int(24 / max(1, interval_hours)) + 48):
            if candidate > local_now:
                return dt_util.as_utc(candidate)
            candidate += step
        return None

    async def async_get_upcoming_runs(self) -> list[dict[str, Any]]:
        """Compute the next fire time for each enabled schedule (for the dashboard).

        Reuses the same bound/anchor math the trackers use. Interval schedules
        with a ``start_time`` report the next anchored clock target;
        un-anchored intervals have no fixed target (phase depends on when HA
        started), so they report ``next_run_utc=None`` plus ``interval_hours``.
        Sorted soonest-first; entries that can't be resolved are dropped.
        """
        runs: list[dict[str, Any]] = []
        for schedule in self._schedules:
            if not schedule.get(const.SCHEDULE_CONF_ENABLED, True):
                continue
            recurrence = schedule.get(const.SCHEDULE_CONF_RECURRENCE)
            action = schedule.get(const.SCHEDULE_CONF_ACTION, "calculate")
            zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")

            entry = {
                "schedule_id": schedule[const.SCHEDULE_CONF_ID],
                "name": schedule.get(const.SCHEDULE_CONF_NAME),
                "action": action,
                "zones": zones,
                "recurrence": recurrence,
                "next_run_utc": None,
                "target_utc": None,
                "duration_seconds": 0,
                # Whether the start above is a projection rather than an armed
                # moment. A two-stage schedule does not know its real start
                # until its decision point, so before then this number moves as
                # deficits grow through the day — which reads as a defect unless
                # the UI can say it is an estimate.
                "estimated": False,
                "start_bound_utc": None,
            }

            if recurrence == const.SCHEDULE_RECURRENCE_INTERVAL:
                entry["interval_hours"] = schedule.get(
                    const.SCHEDULE_CONF_INTERVAL_HOURS, 24
                )
                target = self._next_interval_target(schedule, dt_util.utcnow())
                if target is not None:
                    entry["next_run_utc"] = target.isoformat()
                    entry["target_utc"] = target.isoformat()
                runs.append(entry)
                continue

            governing, paired = self._bounded_ends(schedule)
            if governing is None:
                continue
            entry["anchor"] = governing

            target = await self._next_governing_time(schedule, governing)
            if target is None:
                continue

            next_run = target
            if governing == const.SCHEDULE_ANCHOR_FINISH and action == "irrigate":
                duration = await self._estimate_duration(schedule)
                entry["duration_seconds"] = int(duration)
                next_run = target - datetime.timedelta(seconds=duration)
                if paired is not None:
                    floor = await self._paired_bound_time(
                        schedule, const.SCHEDULE_ANCHOR_START, target
                    )
                    if floor is not None:
                        entry["start_bound_utc"] = floor.isoformat()
                        next_run = max(next_run, floor)
                        decision_point = floor
                    else:
                        decision_point = target - datetime.timedelta(
                            seconds=await self._duration_bound(schedule)
                        )
                    # True only until the decision point: the number above is
                    # the CURRENT demand projected forward, and demand grows all
                    # day, so it drifts through the evening. Past the decision
                    # point the start is armed and no longer moves. Without
                    # marking the difference the drift reads as a defect.
                    entry["estimated"] = dt_util.utcnow() < decision_point
            elif (
                governing == const.SCHEDULE_ANCHOR_START
                and paired is not None
                and action == "irrigate"
            ):
                finish = await self._paired_bound_time(
                    schedule, const.SCHEDULE_ANCHOR_FINISH, target
                )
                if finish is not None:
                    entry["start_bound_utc"] = target.isoformat()
                    entry["target_utc"] = finish.isoformat()

            entry["next_run_utc"] = next_run.isoformat()
            if entry["target_utc"] is None:
                entry["target_utc"] = target.isoformat()
            runs.append(entry)

        runs.sort(key=lambda r: r["next_run_utc"] or "9999")
        return runs

    # --- single bound: fire exactly there ------------------------------------

    async def _setup_governing_tracker(self, schedule: dict[str, Any], end: str) -> Any:
        """Fire exactly at ``end``'s resolved instant; no truncation, whatever
        is due runs to completion (or, for calculate/update, the action just
        fires). Uses HA's own native tracker wherever the old code did —
        unchanged mechanism for every combination this ticket must not change
        the behaviour of — and a resolver-driven one-shot only where no native
        tracker could ever express it: a sun-relative bound on a weekly or
        monthly recurrence, which is the exact gap GitLab #27 closes.
        """
        mode_key, time_key, offset_key, _azimuth_key = _BOUND_FIELDS[end]
        mode = schedule.get(mode_key)
        recurrence = schedule.get(const.SCHEDULE_CONF_RECURRENCE)
        name = schedule.get(const.SCHEDULE_CONF_NAME)

        if mode == const.SCHEDULE_BOUND_MODE_TIME:
            time_str = schedule.get(time_key, "06:00")
            try:
                hour, minute = map(int, time_str.split(":"))
            except (ValueError, TypeError, AttributeError):
                _LOGGER.warning(
                    "Schedule '%s': %s time '%s' is not HH:MM; not armed",
                    name,
                    end,
                    time_str,
                )
                return None

            if recurrence == const.SCHEDULE_RECURRENCE_DAILY:
                return async_track_time_change(
                    self.hass,
                    lambda now: self._execute_schedule(schedule, now),
                    hour=hour,
                    minute=minute,
                    second=0,
                )
            if recurrence in (
                const.SCHEDULE_RECURRENCE_WEEKLY,
                const.SCHEDULE_RECURRENCE_MONTHLY,
            ):

                def check_and_execute(now, s=schedule):
                    if self._recurrence_day_matches(s, now):
                        self._execute_schedule(s, now)

                return async_track_time_change(
                    self.hass, check_and_execute, hour=hour, minute=minute, second=0
                )
            return None

        if (
            mode
            in (const.SCHEDULE_BOUND_MODE_SUNRISE, const.SCHEDULE_BOUND_MODE_SUNSET)
            and recurrence == const.SCHEDULE_RECURRENCE_DAILY
        ):
            offset_minutes = schedule.get(offset_key, 0) or 0
            _LOGGER.info(
                "Registered %s schedule '%s' (%s, offset %s min)",
                mode,
                name,
                end,
                offset_minutes,
            )
            track_fn = (
                async_track_sunrise
                if mode == const.SCHEDULE_BOUND_MODE_SUNRISE
                else async_track_sunset
            )
            # HA invokes the sunrise/sunset callback with NO arguments
            # (async_run_hass_job on a Callable[[], None]), unlike
            # async_track_point_in_utc_time / async_track_time_change which
            # pass `now`. A one-arg lambda would raise TypeError at fire time
            # and the schedule would silently never run, so supply it here.
            return track_fn(
                self.hass,
                lambda: self._execute_schedule(schedule, dt_util.utcnow()),
                datetime.timedelta(minutes=offset_minutes),
            )

        # Everything else — solar azimuth at any recurrence, or a sun-relative
        # bound on weekly/monthly — has no native HA tracker that can express
        # it, so it gets a resolver-driven, self-rescheduling one-shot.
        return await self._setup_resolved_one_shot(schedule, end)

    async def _setup_resolved_one_shot(self, schedule: dict[str, Any], end: str) -> Any:
        """One-shot tracker at ``end``'s next resolved+day-matched instant,
        that re-arms itself for the following occurrence after each fire."""
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        target = await self._next_governing_time(schedule, end)
        if target is None:
            _LOGGER.warning(
                "Schedule '%s': could not resolve its next %s occurrence",
                name,
                end,
            )
            return None

        def fire(now, s=schedule):
            self._execute_schedule(s, now)
            # Re-register for next occurrence — thread-safe wrapper required
            # because async_track_point_in_utc_time callbacks may fire outside
            # the event loop.
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task, self._reregister_tracker(s)
            )

        _LOGGER.info("Registered schedule '%s' (%s) at %s", name, end, target)
        return async_track_point_in_utc_time(self.hass, fire, target)

    # --- finish-governed: fires at (target − duration) -----------------------

    async def _setup_finish_tracker(
        self, schedule: dict[str, Any], *, fitted: bool
    ) -> Any:
        """Resolve the Finish bound, advance past an already-fired occurrence,
        then either arm the classic single-stage finish tracker or delegate to
        the two-stage arm — the resolution and advance logic is shared by
        both, since only one is ever wanted for a given schedule."""
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        sid = schedule[const.SCHEDULE_CONF_ID]
        target = await self._next_governing_time(schedule, const.SCHEDULE_ANCHOR_FINISH)
        if target is None:
            _LOGGER.warning(
                "Finish schedule '%s': could not determine next target time", name
            )
            return None

        # If we already fired this occurrence (the run just happened and we're
        # re-arming), advance to the NEXT occurrence. Without this the tracker
        # re-derives the same still-future target, recomputes a start that is now
        # in the past, and busy-loops the "run ASAP" branch every ~2s for the
        # whole start→finish window — re-firing irrigation thousands of times.
        if self._finish_last_target.get(sid) == target.isoformat():
            nxt = await self._next_governing_time(
                schedule, const.SCHEDULE_ANCHOR_FINISH, reference_utc=target
            )
            if nxt is None:
                _LOGGER.warning(
                    "Finish schedule '%s': could not determine next target after %s",
                    name,
                    target,
                )
                return None
            target = nxt

        if fitted:
            return await self._setup_fitted_tracker(schedule, target)

        duration = await self._estimate_duration(schedule)
        fire_time = target - datetime.timedelta(seconds=duration)
        now_utc = dt_util.utcnow()
        if fire_time <= now_utc:
            # Start moment already passed (e.g. HA restarted mid-window). Catch
            # up once, ASAP; firing records this target so the re-arm above then
            # advances to the next occurrence instead of looping.
            _LOGGER.warning(
                "Finish schedule '%s': start (%s = target %s − %ss) already passed; "
                "running as soon as possible",
                name,
                fire_time,
                target,
                duration,
            )
            fire_time = now_utc + datetime.timedelta(seconds=2)

        _LOGGER.info(
            "Finish schedule '%s': target %s, est. duration %ss → start %s",
            name,
            target,
            duration,
            fire_time,
        )

        def finish_callback(now, s=schedule, fired=target):
            # Remember which occurrence we fired so the re-arm advances past it.
            # Recorded at DISPATCH, not at completion, and synchronously here so
            # a re-arm racing the persistence task below still sees it. A run cut
            # short by a restart therefore does not re-fire: skipping a partial
            # run costs a night's watering, repeating one costs a double dose.
            self._finish_last_target[s[const.SCHEDULE_CONF_ID]] = fired.isoformat()
            self._execute_schedule(s, now)
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task,
                self._persist_fired_occurrences(dict(self._finish_last_target)),
            )
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task, self._reregister_tracker(s)
            )

        return async_track_point_in_utc_time(self.hass, finish_callback, fire_time)

    async def _persist_fired_occurrences(self, markers: dict[str, str]) -> None:
        """Write the fired-occurrence map to the config document.

        Takes a snapshot rather than reading ``self._finish_last_target`` when
        the task runs: a teardown between scheduling and running this would
        otherwise persist whatever the dict had become.

        ``async_update_config`` only schedules a delayed save, but the in-memory
        ``Config`` is evolved immediately and the ``Store`` is cached for the
        lifetime of ``hass``, so a config entry reload — which does not re-read
        from disk — sees the marker at once. The residual gap is an unclean
        shutdown inside ``SAVE_DELAY``; that is left open deliberately, since
        forcing an immediate save here would reserialise every reading buffer on
        every schedule fire, and the outcome in that case is only today's
        behaviour in a case that already involves a power cut.
        """
        await self.coordinator.store.async_update_config(
            {const.CONF_FIRED_OCCURRENCES: markers}
        )

    # --- both ends bounded: two-stage arm, pinned to either end --------------

    async def _setup_bounded_tracker(
        self, schedule: dict[str, Any], governing: str
    ) -> Any:
        """Both Start and Finish are bounded; dispatch on which one the run is
        pinned to."""
        if governing == const.SCHEDULE_ANCHOR_FINISH:
            return await self._setup_finish_tracker(schedule, fitted=True)
        return await self._setup_start_pinned_tracker(schedule)

    async def _setup_start_pinned_tracker(self, schedule: dict[str, Any]) -> Any:
        """Both ends bounded, pinned to Start: fire exactly at the resolved
        Start instant — a fixed, non-duration-dependent moment, so unlike the
        Finish-pinned arm there is no decision point to wait for — passing the
        resolved Finish through as a hard deadline so the run still stops
        there. Ranking/fitting happens at fire time (:meth:`_decide_and_run_start_pinned`)
        rather than ahead of it, because there is nothing duration-dependent
        to wait for here in the first place.
        """
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        sid = schedule[const.SCHEDULE_CONF_ID]
        target = await self._next_governing_time(schedule, const.SCHEDULE_ANCHOR_START)
        if target is None:
            _LOGGER.warning("Schedule '%s': could not resolve its Start bound", name)
            return None

        if self._finish_last_target.get(sid) == target.isoformat():
            nxt = await self._next_governing_time(
                schedule, const.SCHEDULE_ANCHOR_START, reference_utc=target
            )
            if nxt is None:
                _LOGGER.warning(
                    "Schedule '%s': could not resolve its Start bound after %s",
                    name,
                    target,
                )
                return None
            target = nxt

        finish = await self._paired_bound_time(
            schedule, const.SCHEDULE_ANCHOR_FINISH, target
        )

        _LOGGER.info(
            "Registered schedule '%s' (start, deadline %s) at %s", name, finish, target
        )

        def run_callback(now, s=schedule, fired=target, d=finish):
            self._finish_last_target[s[const.SCHEDULE_CONF_ID]] = fired.isoformat()
            # Ranking/fitting needs to await the plan, but a native HA time
            # tracker calls back synchronously — same thread-safe hop the
            # resolved one-shot and finish trackers use to reach async code
            # from here.
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task,
                self._decide_and_run_start_pinned(s, now, fired, d),
            )
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task,
                self._persist_fired_occurrences(dict(self._finish_last_target)),
            )
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task, self._reregister_tracker(s)
            )

        return self._store_tracker(
            sid, async_track_point_in_utc_time(self.hass, run_callback, target)
        )

    async def _decide_and_run_start_pinned(
        self, schedule: dict[str, Any], now, target, deadline
    ) -> None:
        """Both ends bounded, pinned to Start: rank, fit, and dispatch.

        The Start bound already fixed the fire time (see
        ``_setup_start_pinned_tracker``), so there is no separate decision
        point to read the demand ahead of the run — this runs the same
        rank/select sequence :meth:`_decide_and_arm` applies at ITS decision
        point, but at the moment the schedule actually fires. ``deadline`` is
        the paired Finish bound; when it could not be resolved (a degenerate
        pairing — see ``_paired_bound_time``) there is no window to fit
        against, so whatever is due runs unfitted, matching a single open end.
        """
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        sid = schedule[const.SCHEDULE_CONF_ID]
        zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")

        await self.coordinator.async_commit_pre_run_calculation(zones)

        plan = await self.coordinator.async_plan_zone_runs(zones, runnable_only=True)
        plan = [p for p in plan if p.duration > 0]

        order = None
        if plan and deadline is not None:
            sequencing, slot, absorption = self.coordinator.sequencing_timing()
            window = max(0.0, (deadline - now).total_seconds())
            selection = select(
                plan,
                window_seconds=window,
                sequencing=sequencing,
                max_slot_seconds=slot,
                min_absorption_seconds=absorption,
            )

            dropped = {p.zone_id for p in plan} - {p.zone_id for p in selection}
            # One announcement per decision — same guard _decide_and_arm uses,
            # keyed on the fixed Start occurrence rather than the Finish
            # target, since that is what identifies this run.
            new = self._decision_is_new(
                sid,
                (
                    target.isoformat(),
                    tuple(p.zone_id for p in selection),
                    tuple(sorted(dropped)),
                ),
            )
            if dropped:
                log = _LOGGER.warning if new else _LOGGER.debug
                log(
                    "Schedule '%s': zones %s are due but do not fit the window "
                    "before %s; they carry their deficit and lead the next run",
                    name,
                    sorted(dropped),
                    deadline,
                )
            order = [p.zone_id for p in selection]

        self._execute_schedule(
            schedule, now, order=order, deadline=deadline, pre_committed=True
        )

    async def _setup_fitted_tracker(self, schedule: dict[str, Any], target) -> Any:
        """Arm a schedule pinned to Finish with a bounded Start.

        Two stages, because the start time depends on a demand that is not
        known until close to the run. The single-stage tracker reads the
        estimate when it arms — on load, after each fire, and on every config
        change — which is typically hours before the run, and deficits grow
        all day after that. On seven zones at this scale that is around three
        hours of under-estimate: the run starts three hours late and overruns
        its finish.

        So the first stage arms on a moment that does NOT depend on the
        duration, and the second stage arms the real start once the demand has
        been read there:

            decision point = the paired Start bound

        Both ends being bounded is exactly the condition for reaching this
        method at all, so the decision point is always the resolved Start —
        the latest duration-independent moment — which is why a DAYTIME finish
        (syringing, seed and sod establishment, drip zones, frost protection)
        should bound its Start too: without one the decision would have no
        fixed point to arm on ahead of the run.
        """
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        floor = await self._paired_bound_time(
            schedule, const.SCHEDULE_ANCHOR_START, target
        )
        now_utc = dt_util.utcnow()

        if floor is not None:
            decision_point = floor
        else:
            bound = await self._duration_bound(schedule)
            decision_point = target - datetime.timedelta(seconds=bound)

        if decision_point > now_utc:

            def decide_callback(now, s=schedule, t=target, f=floor):
                self.hass.loop.call_soon_threadsafe(
                    self.hass.async_create_task,
                    self._decide_and_arm(s, t, f, commit=True),
                )

            _LOGGER.info(
                "Finish schedule '%s': target %s, deciding at %s (%s)",
                name,
                target,
                decision_point,
                "start bound" if floor is not None else "target - bound",
            )
            return async_track_point_in_utc_time(
                self.hass, decide_callback, decision_point
            )

        # Already past the decision point — a restart inside the window, or a
        # config change after the decision was made. Re-derive from the live
        # deficits and arm immediately, WITHOUT a second commit: the ledger for
        # this run was already committed at the decision point, and committing
        # again here would re-book the same window every time anything touches
        # the config.
        return await self._decide_and_arm(schedule, target, floor, commit=False)

    def _decision_is_new(self, sid: str, decision: tuple) -> bool:
        """Whether this arm decided something the log has not already said.

        The decision is the occurrence plus the zones: a start time that moved a
        few seconds because the re-arm happened a few seconds later is the same
        decision, and re-announcing it is what made a single armed run look like
        dozens. A zone appearing or being dropped is a real change and is
        announced. Records the decision as a side effect, so callers ask once.
        """
        if self._decision_logged.get(sid) == decision:
            return False
        self._decision_logged[sid] = decision
        return True

    async def _decide_and_arm(
        self, schedule: dict[str, Any], target, floor, *, commit: bool
    ) -> Any:
        """Read the demand, pick the zones, and arm the run's real start.

        Only reached when both ends are bounded (see ``_setup_bounded_tracker``),
        so the run is always fitted here — ranked by depletion, truncated to
        the window, with the target passed to the runner as a hard deadline.
        """
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        sid = schedule[const.SCHEDULE_CONF_ID]
        zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")

        if commit:
            await self.coordinator.async_commit_pre_run_calculation(zones)

        plan = await self.coordinator.async_plan_zone_runs(zones, runnable_only=True)
        plan = [p for p in plan if p.duration > 0]
        if not plan:
            log = (
                _LOGGER.info
                if self._decision_is_new(sid, (target.isoformat(), None))
                else _LOGGER.debug
            )
            log(
                "Finish schedule '%s': no zone is due at the decision point; "
                "the %s occurrence runs unfitted",
                name,
                target,
            )
            return self._arm_pass_through(schedule, target)

        now_utc = dt_util.utcnow()
        start_floor = max(now_utc, floor) if floor is not None else now_utc
        sequencing, slot, absorption = self.coordinator.sequencing_timing()

        window = (target - start_floor).total_seconds()
        selection = select(
            plan,
            window_seconds=window,
            sequencing=sequencing,
            max_slot_seconds=slot,
            min_absorption_seconds=absorption,
        )

        demand = simulate_wall_clock(
            selection,
            sequencing=sequencing,
            max_slot_seconds=slot,
            min_absorption_seconds=absorption,
        )
        # When everything fits, the slack sits BEFORE the start, which is where
        # it belongs; the run still ends on the target. Only when the demand
        # outruns the window is the start pinned to the floor and both ends of
        # the window fixed.
        fire_time = max(start_floor, target - datetime.timedelta(seconds=demand))
        if fire_time <= now_utc:
            fire_time = now_utc + datetime.timedelta(seconds=2)

        dropped = {p.zone_id for p in plan} - {p.zone_id for p in selection}
        # One announcement per decision. A re-arm that reaches the same zones
        # repeats itself at DEBUG instead, so the strings stay greppable without
        # the log implying an arm that did not happen.
        new = self._decision_is_new(
            sid,
            (
                target.isoformat(),
                tuple(p.zone_id for p in selection),
                tuple(sorted(dropped)),
            ),
        )
        if dropped:
            log = _LOGGER.warning if new else _LOGGER.debug
            log(
                "Finish schedule '%s': zones %s are due but do not fit the "
                "window before %s; they carry their deficit and lead the next "
                "run",
                name,
                sorted(dropped),
                target,
            )
        log = _LOGGER.info if new else _LOGGER.debug
        log(
            "Finish schedule '%s': target %s, %s zone(s) %s, demand %ss → start %s",
            name,
            target,
            len(selection),
            [p.zone_id for p in selection],
            round(demand),
            fire_time,
        )

        order = [p.zone_id for p in selection]
        deadline = target

        def run_callback(now, s=schedule, fired=target, o=order, d=deadline):
            # Recording the fired occurrence here rather than at the decision
            # point is what lets a config change inside the window re-derive the
            # start instead of skipping the night: until the run actually fires,
            # a re-arm still resolves to THIS occurrence.
            self._finish_last_target[s[const.SCHEDULE_CONF_ID]] = fired.isoformat()
            self._execute_schedule(s, now, order=o, deadline=d, pre_committed=True)
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task,
                self._persist_fired_occurrences(dict(self._finish_last_target)),
            )
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task, self._reregister_tracker(s)
            )

        return self._store_tracker(
            sid, async_track_point_in_utc_time(self.hass, run_callback, fire_time)
        )

    def _arm_pass_through(self, schedule: dict[str, Any], target) -> Any:
        """Arm the schedule's own action at ``target``, unfitted, and re-arm.

        A night the selection has nothing to say about still has to leave a live
        tracker behind. Simply returning None would arm nothing at all, and since
        a finish schedule only re-arms from its own fire callback, the schedule
        would go dormant until the next restart or config write.

        It also has to still run. An empty plan is not the same claim as "there
        is no water to deliver": ``async_plan_zone_runs`` excludes distributor
        members by construction, because a member waters through its
        distributor's shared inlet rather than through its own valve. A schedule
        whose targets are all members therefore plans nothing while still having
        a cycle to run, and ``_execute_schedule`` is that cycle's sole automatic
        driver. Every gate that decides whether anything actually happens - the
        skip conditions, the rain delay, per-member demand - lives inside it, so
        firing the action here costs a no-op pass on a genuinely empty night and
        keeps a members-only schedule watering exactly as it does with neither
        new control set. Nothing was fitted, so no order and no deadline.
        """
        sid = schedule[const.SCHEDULE_CONF_ID]

        def lapse_callback(now, s=schedule, fired=target):
            self._finish_last_target[s[const.SCHEDULE_CONF_ID]] = fired.isoformat()
            self._execute_schedule(
                s, now, order=None, deadline=None, pre_committed=True
            )
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task,
                self._persist_fired_occurrences(dict(self._finish_last_target)),
            )
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task, self._reregister_tracker(s)
            )

        return self._store_tracker(
            sid, async_track_point_in_utc_time(self.hass, lapse_callback, target)
        )

    def _store_tracker(self, schedule_id: str, tracker):
        """Register a tracker armed outside ``_setup_schedule_tracker``.

        The two-stage arm creates its second-stage tracker from a decision-point
        callback, so nothing further up is going to store the handle — and an
        unstored handle can never be cancelled by ``async_unload``, which is how
        a reload ends up with N surviving listeners all firing the same run.
        """
        old = self._schedule_trackers.get(schedule_id)
        if old and old is not tracker:
            old()
        self._schedule_trackers[schedule_id] = tracker
        return tracker

    async def _reregister_tracker(self, schedule: dict[str, Any]) -> None:
        """Cancel and rebuild a schedule's tracker (used by self-rescheduling
        finish/azimuth trackers and by the duration-change re-arm)."""
        schedule_id = schedule[const.SCHEDULE_CONF_ID]
        old = self._schedule_trackers.get(schedule_id)
        if old:
            old()
            self._schedule_trackers[schedule_id] = None
        await self._setup_schedule_tracker(schedule)

    async def _setup_interval_tracker(self, schedule: dict[str, Any]) -> Any:
        """Set up an interval-based schedule tracker.

        With a ``start_time`` anchor the interval is phase-locked to that clock
        time: it uses a one-shot, self-rescheduling point-in-time tracker (the
        same pattern as the resolved-bound trackers) so each fire re-arms on
        the next anchored occurrence. Without a start_time it free-runs every
        ``interval_hours`` from now — the original behaviour, unchanged.
        """
        if schedule.get(const.SCHEDULE_CONF_START_TIME):
            target = self._next_interval_target(schedule, dt_util.utcnow())
            if target is None:
                _LOGGER.warning(
                    "Could not calculate next interval time for schedule '%s'",
                    schedule.get(const.SCHEDULE_CONF_NAME),
                )
                return None

            def interval_callback(now, s=schedule):
                self._execute_schedule(s, now)
                # Re-register for the next occurrence — thread-safe wrapper
                # because async_track_point_in_utc_time callbacks may fire
                # outside the event loop (mirrors the resolved-bound trackers).
                self.hass.loop.call_soon_threadsafe(
                    self.hass.async_create_task,
                    self._reregister_tracker(s),
                )

            _LOGGER.info(
                "Registered interval schedule '%s' (start %s, every %sh) at %s",
                schedule.get(const.SCHEDULE_CONF_NAME),
                schedule.get(const.SCHEDULE_CONF_START_TIME),
                schedule.get(const.SCHEDULE_CONF_INTERVAL_HOURS, 24),
                target,
            )
            return async_track_point_in_utc_time(self.hass, interval_callback, target)

        interval_hours = schedule.get(const.SCHEDULE_CONF_INTERVAL_HOURS, 24)
        interval_delta = datetime.timedelta(hours=interval_hours)

        return async_track_time_interval(
            self.hass, lambda now: self._execute_schedule(schedule, now), interval_delta
        )

    async def _remove_schedule_tracker(self, schedule_id: str) -> None:
        """Remove a schedule tracker."""
        if schedule_id in self._schedule_trackers:
            tracker = self._schedule_trackers[schedule_id]
            if tracker:
                tracker()
            del self._schedule_trackers[schedule_id]

    @callback
    def _execute_schedule(
        self,
        schedule: dict[str, Any],
        now: datetime.datetime,
        *,
        order=None,
        deadline=None,
        pre_committed=False,
    ) -> None:
        """Execute a scheduled action.

        ``order`` and ``deadline`` are set only by a bounded run: the zone ids
        chosen at the decision point, in priority order (when a selection ran),
        and the finish target the runner must not water past. ``pre_committed``
        says a two-stage schedule already committed its pre-run calculation
        there.
        """
        # Check date range if specified
        start_date = schedule.get(const.SCHEDULE_CONF_START_DATE)
        end_date = schedule.get(const.SCHEDULE_CONF_END_DATE)

        if start_date:
            start_dt = datetime.datetime.fromisoformat(start_date)
            if start_dt.tzinfo is None:
                # Frontend stores a date-only value (e.g. "2026-06-19"), which
                # parses to a naive datetime at midnight. `now` is tz-aware UTC,
                # so localize before comparing to avoid a TypeError.
                start_dt = start_dt.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
            if now < start_dt:
                return

        if end_date:
            end_dt = datetime.datetime.fromisoformat(end_date)
            if end_dt.tzinfo is None:
                # Date-only end value: treat it as inclusive through end-of-day
                # in local time so the schedule still runs on the final day.
                end_dt = end_dt.replace(
                    hour=23, minute=59, second=59, tzinfo=dt_util.DEFAULT_TIME_ZONE
                )
            if now > end_dt:
                return

        action = schedule.get(const.SCHEDULE_CONF_ACTION, "calculate")
        zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")
        schedule_name = schedule.get(const.SCHEDULE_CONF_NAME, "Unnamed Schedule")

        _LOGGER.info(
            "Executing recurring schedule: %s (action: %s)", schedule_name, action
        )

        # Fire event
        self.hass.bus.fire(
            f"{const.DOMAIN}_{const.EVENT_RECURRING_SCHEDULE_TRIGGERED}",
            {
                "schedule_id": schedule[const.SCHEDULE_CONF_ID],
                "schedule_name": schedule_name,
                "action": action,
                "zones": zones,
                # Normalised to LOCAL. `now` reaches us from whichever tracker
                # armed this schedule, and they disagree: async_track_time_change
                # passes local, async_track_point_in_utc_time passes UTC, and the
                # sunrise/sunset paths pass dt_util.utcnow(). All are tz-aware, so
                # the offset was always carried and no consumer parsing this
                # properly was ever wrong — but two schedules firing at the same
                # wall-clock moment produced timestamps that looked hours apart,
                # which is the kind of thing people debug for an hour. Local
                # matches every other time the UI shows.
                "timestamp": dt_util.as_local(now).isoformat(),
            },
        )

        self.hass.loop.call_soon_threadsafe(
            self.hass.async_create_task,
            self._perform_schedule_action(
                action,
                zones,
                schedule_name,
                order=order,
                deadline=deadline,
                pre_committed=pre_committed,
            ),
        )

    async def _perform_schedule_action(
        self,
        action: str,
        zones: str | list[str],
        schedule_name: str,
        *,
        order=None,
        deadline=None,
        pre_committed=False,
    ) -> None:
        """Perform the scheduled action."""
        # None = every zone. Only the two loops below need this; the irrigate
        # branch passes `zones` through unchanged because each of its consumers
        # already accepts the raw "all"/list shape. See normalize_zone_selection
        # for why iterating the raw value is unsafe.
        selection = normalize_zone_selection(zones)
        try:
            if action == "calculate":
                if selection is None:
                    await self.coordinator._async_calculate_all()
                else:
                    # Per-zone calculate must aggregate the mapping's weather data
                    # first; route through async_update_zone_config (ATTR_CALCULATE),
                    # which does the aggregation + forecast fetch before calculating.
                    for zone_id in selection:
                        await self.coordinator.async_update_zone_config(
                            zone_id, {const.ATTR_CALCULATE: True}
                        )
            elif action == "update":
                if selection is None:
                    await self.coordinator._async_update_all()
                else:
                    for zone_id in selection:
                        await self.coordinator._async_update_zone(zone_id)
            elif action == "irrigate":
                # "Before each irrigation run" means when the run is PLANNED,
                # which is two different moments internally: a two-stage
                # schedule commits at its decision point, so the selection and
                # the start time are both computed on the fresh ledger;
                # everything else commits here, immediately before dispatch.
                if not pre_committed:
                    await self.coordinator.async_commit_pre_run_calculation(zones)
                # Check skip conditions (same as trigger-based irrigation)
                if await self.coordinator._check_skip_conditions():
                    _LOGGER.info(
                        "Schedule '%s': irrigation skipped due to conditions",
                        schedule_name,
                    )
                    evaluation = (
                        getattr(self.coordinator, "_last_skip_evaluation", None) or {}
                    )
                    reasons = [
                        c["id"]
                        for c in evaluation.get("checks", [])
                        if c.get("enabled") and c.get("would_skip")
                    ]
                    await self.coordinator._record_skipped_run(
                        zones, ",".join(reasons) if reasons else None
                    )
                    return
                # Fire irrigation event for backward compatibility
                event_data = {
                    "triggered_by": "recurring_schedule",
                    "schedule_name": schedule_name,
                    "zones": zones,
                }
                self.hass.bus.fire(
                    f"{const.DOMAIN}_{const.EVENT_IRRIGATE_START}", event_data
                )
                # Directly control linked entities (restricted to the schedule's
                # target zones), then reset counter
                watered = await self.coordinator._irrigate_linked_entities(
                    zones, order=order, deadline=deadline
                )
                # Plan G: also run distributor cycles for due member zones. Members
                # are excluded from _irrigate_linked_entities (irrigation.py:462), so
                # this is their sole automatic driver, and it runs even when no
                # non-member zone is due (that path early-returns at irrigation.py:476).
                watered_members = await self.coordinator._dispatch_distributor_cycles(
                    zones
                )
                # review finding A — days-since reset stranded zones dry on
                # rain-delay / all-vetoed / no-demand runs: both dispatch helpers
                # deliver NO water on those paths (rain delay, every zone soil-
                # vetoed, or nothing due), yet the reset used to fire
                # unconditionally, fooling the days_between_irrigation guard into
                # skipping the next due run. Only reset when water was actually
                # delivered.
                #
                # This resets the GLOBAL counter only. Per-zone counters are
                # reset as each zone's water is credited, because a fitted run
                # waters a prefix of the priority order and this call happens at
                # dispatch, long before a sequential or rotating run has
                # finished — so it cannot know which zones were reached.
                if watered or watered_members:
                    await self.coordinator._reset_days_since_irrigation()

            _LOGGER.info(
                "Successfully executed schedule action: %s for zones: %s", action, zones
            )

        except Exception as e:
            _LOGGER.error("Error executing schedule action %s: %s", action, e)
            raise

    async def _save_schedules(self) -> None:
        """Save schedules to configuration."""
        await self.coordinator.store.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: self._schedules}
        )
        # Let the next-irrigation sensors recompute their upcoming run.
        async_dispatcher_send(self.hass, const.DOMAIN + "_schedules_updated")

    def _validate_schedule_data(self, schedule_data: dict[str, Any]) -> None:
        """Validate schedule data.

        Schedules have no voluptuous schema (websocket_save_schedule hands the
        raw dict straight through), so this is the only gate on the shape.
        """
        required_fields = [const.SCHEDULE_CONF_NAME, const.SCHEDULE_CONF_RECURRENCE]
        for field in required_fields:
            if field not in schedule_data:
                raise ValueError(f"Missing required field: {field}")

        recurrence = schedule_data[const.SCHEDULE_CONF_RECURRENCE]
        if recurrence not in const.SCHEDULE_RECURRENCES:
            raise ValueError(f"Invalid recurrence: {recurrence}")

        # The store has never kept a non-irrigate schedule, so accepting one
        # here produced something that armed, ran, and vanished at the next
        # restart with nothing logged. Refuse it instead. Unreachable from the
        # panel and the setup wizard: neither offers an action control and both
        # send "irrigate", and the one-time removal runs before anything can
        # list a schedule, so no stored legacy row can reach the edit path
        # either.
        action = schedule_data.get(
            const.SCHEDULE_CONF_ACTION, const.SCHEDULE_ACTION_IRRIGATE
        )
        if action not in const.SCHEDULE_SUPPORTED_ACTIONS:
            raise ValueError(
                f"Invalid schedule action: {action}. Recurring schedules are "
                "irrigation-only; calculation and weather updates are driven by "
                "the daily settings"
            )

        # Interval's own optional clock anchor, shared with the Start bound's
        # "time" mode value but validated the same way regardless of which one
        # is in play.
        start_time_str = schedule_data.get(const.SCHEDULE_CONF_START_TIME)
        if start_time_str:
            try:
                datetime.datetime.strptime(start_time_str, "%H:%M")
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid start time format: {start_time_str}. Expected HH:MM"
                ) from e

        if recurrence == const.SCHEDULE_RECURRENCE_INTERVAL:
            # Interval has no time of day and therefore no window — Start and
            # Finish bounds do not apply.
            return

        start_mode = schedule_data.get(
            const.SCHEDULE_CONF_START_MODE, const.SCHEDULE_DEFAULT_BOUND_MODE
        )
        finish_mode = schedule_data.get(
            const.SCHEDULE_CONF_FINISH_MODE, const.SCHEDULE_DEFAULT_BOUND_MODE
        )
        for label, mode in (("start", start_mode), ("finish", finish_mode)):
            if mode not in const.SCHEDULE_BOUND_MODES:
                raise ValueError(
                    f"Invalid {label} mode: {mode}. Expected one of "
                    f"{const.SCHEDULE_BOUND_MODES}"
                )

        # A floor is the only thing that keeps a schedule watering at all — a
        # schedule with neither end bounded describes no time whatsoever.
        # Rejected here rather than shrugged off at arm time.
        if (
            start_mode == const.SCHEDULE_BOUND_MODE_NONE
            and finish_mode == const.SCHEDULE_BOUND_MODE_NONE
        ):
            raise ValueError(
                "A schedule needs a Start or a Finish bound; both are unbounded"
            )

        for end, mode, time_key, offset_key, azimuth_key in (
            ("start", start_mode, *_BOUND_FIELDS[const.SCHEDULE_ANCHOR_START][1:]),
            ("finish", finish_mode, *_BOUND_FIELDS[const.SCHEDULE_ANCHOR_FINISH][1:]),
        ):
            if mode == const.SCHEDULE_BOUND_MODE_TIME:
                time_val = schedule_data.get(time_key)
                try:
                    datetime.datetime.strptime(time_val, "%H:%M")
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Invalid {end} time: {time_val}. Expected HH:MM"
                    ) from e
            if mode in (
                const.SCHEDULE_BOUND_MODE_SUNRISE,
                const.SCHEDULE_BOUND_MODE_SUNSET,
                const.SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
            ):
                offset = schedule_data.get(offset_key, 0)
                try:
                    int(offset or 0)
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Invalid {end} offset: {offset}. Expected minutes"
                    ) from e
            if (
                mode == const.SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH
                and azimuth_key in schedule_data
            ):
                try:
                    float(schedule_data[azimuth_key])
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Invalid {end} azimuth: {schedule_data[azimuth_key]}. "
                        "Expected degrees"
                    ) from e

        if (
            start_mode != const.SCHEDULE_BOUND_MODE_NONE
            and finish_mode != const.SCHEDULE_BOUND_MODE_NONE
        ):
            anchor = schedule_data.get(const.SCHEDULE_CONF_ANCHOR)
            if anchor is not None and anchor not in const.SCHEDULE_ANCHORS:
                raise ValueError(
                    f"Invalid anchor: {anchor}. Expected one of {const.SCHEDULE_ANCHORS}"
                )

    def _generate_schedule_id(self) -> str:
        """Generate a unique schedule ID."""
        return f"schedule_{uuid.uuid4().hex[:8]}"

    def get_schedules(self) -> list[dict[str, Any]]:
        """Get all schedules."""
        return self._schedules.copy()
