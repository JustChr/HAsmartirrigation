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


class RecurringScheduleManager:
    """Manages recurring schedules for Smart Irrigation."""

    def __init__(self, hass: HomeAssistant, coordinator) -> None:
        """Initialize the recurring schedule manager."""
        self.hass = hass
        self.coordinator = coordinator
        self._schedule_trackers = {}
        self._schedules = []
        self._unsub_rearm = None
        # Per finish-anchored schedule, the target occurrence we last fired for
        # (ISO string). Lets the self-rescheduling finish tracker advance past an
        # occurrence it already ran instead of busy-looping its start→finish
        # window (which re-fired irrigation every ~2s). Keyed by schedule id.
        #
        # Mirrored to const.CONF_FIRED_OCCURRENCES in the config document and
        # rehydrated in async_load_schedules. Holding it only here made the
        # tracker's own catch-up branch unsound: a config entry reload builds a
        # new manager, so a reload inside the start→finish window left the fresh
        # manager unable to tell "never ran this occurrence" from "ran it eleven
        # minutes ago", and it watered the occurrence a second time in full.
        # This dict stays the authority while the manager lives; the stored copy
        # only has to be right by the time a NEW manager reads it.
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

        # Re-arm finish-anchored schedules whenever durations may have changed
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
        """Recompute and re-arm start times for finish-anchored schedules."""
        for schedule in self._schedules:
            if not schedule.get(const.SCHEDULE_CONF_ENABLED, True):
                continue
            if self._time_anchor(schedule) != const.SCHEDULE_TIME_ANCHOR_FINISH:
                continue
            if schedule[const.SCHEDULE_CONF_TYPE] == const.SCHEDULE_TYPE_INTERVAL:
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

        # Drop fired-occurrence markers for schedules that no longer exist. The
        # key is the schedule id: if an id is ever reused, a NEW finish-anchored
        # schedule would inherit the old one's "already fired" marker and skip
        # its first occurrence, silently and once only — the worst kind of bug
        # to reproduce. Now that the map is persisted, pruning must reach the
        # store too, or a stale marker outlives every restart.
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
        """Set up a tracker for a single schedule."""
        if not schedule.get(const.SCHEDULE_CONF_ENABLED, True):
            return

        schedule_id = schedule[const.SCHEDULE_CONF_ID]
        schedule_type = schedule[const.SCHEDULE_CONF_TYPE]

        # "Finish at time" needs a dynamic start (target − duration), so it uses
        # a one-shot, self-rescheduling tracker. Only meaningful for an irrigate
        # action (calculate/update have no run to finish) and for types with a
        # fixed target time (not interval).
        if (
            self._time_anchor(schedule) == const.SCHEDULE_TIME_ANCHOR_FINISH
            and schedule_type != const.SCHEDULE_TYPE_INTERVAL
            and schedule.get(const.SCHEDULE_CONF_ACTION) == "irrigate"
        ):
            tracker = await self._setup_finish_tracker(schedule)
        elif schedule_type == const.SCHEDULE_TYPE_DAILY:
            tracker = await self._setup_daily_tracker(schedule)
        elif schedule_type == const.SCHEDULE_TYPE_WEEKLY:
            tracker = await self._setup_weekly_tracker(schedule)
        elif schedule_type == const.SCHEDULE_TYPE_MONTHLY:
            tracker = await self._setup_monthly_tracker(schedule)
        elif schedule_type == const.SCHEDULE_TYPE_INTERVAL:
            tracker = await self._setup_interval_tracker(schedule)
        elif schedule_type == const.SCHEDULE_TYPE_SUNRISE:
            tracker = await self._setup_sunrise_tracker(schedule)
        elif schedule_type == const.SCHEDULE_TYPE_SUNSET:
            tracker = await self._setup_sunset_tracker(schedule)
        elif schedule_type == const.SCHEDULE_TYPE_SOLAR_AZIMUTH:
            tracker = await self._setup_azimuth_tracker(schedule)
        else:
            _LOGGER.warning("Unknown schedule type: %s", schedule_type)
            return

        self._schedule_trackers[schedule_id] = tracker

    # --- "finish at time" anchoring -----------------------------------------

    @staticmethod
    def _time_anchor(schedule: dict[str, Any]) -> str:
        """Resolve a schedule's time anchor ('start' | 'finish').

        Falls back to the legacy ``account_for_duration`` flag, which only ever
        affected solar schedules.
        """
        anchor = schedule.get(const.SCHEDULE_CONF_TIME_ANCHOR)
        if anchor in (
            const.SCHEDULE_TIME_ANCHOR_START,
            const.SCHEDULE_TIME_ANCHOR_FINISH,
        ):
            return anchor
        if schedule.get(const.SCHEDULE_CONF_TYPE) in (
            const.SCHEDULE_TYPE_SUNRISE,
            const.SCHEDULE_TYPE_SUNSET,
            const.SCHEDULE_TYPE_SOLAR_AZIMUTH,
        ) and schedule.get(const.SCHEDULE_CONF_ACCOUNT_FOR_DURATION, True):
            return const.SCHEDULE_TIME_ANCHOR_FINISH
        return const.SCHEDULE_TIME_ANCHOR_START

    async def _estimate_duration(self, schedule: dict[str, Any]) -> int:
        """Estimated wall-clock run length (seconds) for the schedule's zones."""
        zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")
        return await self.coordinator.get_total_irrigation_duration(zones)

    # --- earliest start, decision point, fitting ----------------------------

    @staticmethod
    def _fit_to_window(schedule: dict[str, Any]) -> bool:
        """Whether this schedule fits its run to the available window."""
        return bool(
            schedule.get(
                const.SCHEDULE_CONF_FIT_TO_WINDOW,
                const.SCHEDULE_DEFAULT_FIT_TO_WINDOW,
            )
        )

    @staticmethod
    def _earliest_start_mode(schedule: dict[str, Any]) -> str:
        mode = schedule.get(const.SCHEDULE_CONF_EARLIEST_START_MODE)
        if mode in const.SCHEDULE_EARLIEST_START_MODES:
            return mode
        return const.SCHEDULE_DEFAULT_EARLIEST_START_MODE

    def _uses_two_stage_arm(self, schedule: dict[str, Any]) -> bool:
        """Whether this schedule needs a decision point before its start.

        Both new controls need one: fitting has to know the live deficits to
        select zones, and an earliest start has to bound a start it can only
        compute once the demand is known. Neither set means the schedule keeps
        the single-stage arm it has always had, byte for byte.
        """
        return (
            self._fit_to_window(schedule)
            or self._earliest_start_mode(schedule) != const.SCHEDULE_EARLIEST_START_NONE
        )

    async def _earliest_start(self, schedule: dict[str, Any], target):
        """The UTC moment before which this occurrence's run must not begin.

        Resolved against ``target`` — the run's finish — not against "now", so
        an occurrence armed days ahead still floors on the right night's sunset.
        Returns None when no floor is configured, or when one cannot be resolved
        (polar sunset, unparseable time); a schedule with an unusable floor
        behaves as it did before the floor existed rather than not running.
        """
        mode = self._earliest_start_mode(schedule)
        if mode == const.SCHEDULE_EARLIEST_START_NONE:
            return None

        floor = None
        if mode == const.SCHEDULE_EARLIEST_START_TIME:
            raw = schedule.get(const.SCHEDULE_CONF_EARLIEST_START_TIME)
            try:
                hour, minute = (int(x) for x in str(raw).split(":"))
            except (ValueError, TypeError, AttributeError):
                _LOGGER.warning(
                    "Schedule '%s': earliest start time '%s' is not HH:MM; "
                    "ignoring the floor",
                    schedule.get(const.SCHEDULE_CONF_NAME),
                    raw,
                )
                return None
            local_target = dt_util.as_local(target)
            candidate = local_target.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            # The latest occurrence of that clock time at or before the target,
            # so an overnight window (floor 22:00, target 06:00) floors on the
            # PREVIOUS evening rather than jumping forward a whole day.
            if candidate > local_target:
                candidate -= datetime.timedelta(days=1)
            floor = dt_util.as_utc(candidate)
        elif mode == const.SCHEDULE_EARLIEST_START_SUNSET:
            offset = datetime.timedelta(
                minutes=schedule.get(const.SCHEDULE_CONF_EARLIEST_START_OFFSET, 0) or 0
            )
            local_date = dt_util.as_local(target).date()
            for back in (0, 1):
                event = get_astral_event_date(
                    self.hass, "sunset", local_date - datetime.timedelta(days=back)
                )
                if event is None:
                    continue
                candidate = dt_util.as_utc(event) + offset
                if candidate <= target:
                    floor = candidate
                    break
            if floor is None:
                _LOGGER.warning(
                    "Schedule '%s': no sunset before the target %s to floor the "
                    "start on; ignoring the floor",
                    schedule.get(const.SCHEDULE_CONF_NAME),
                    target,
                )
                return None

        if floor is not None and floor >= target:
            # A floor at or after the finish leaves no window at all. Honour the
            # finish time and log it, rather than silently never running.
            _LOGGER.warning(
                "Schedule '%s': earliest start %s is not before its finish "
                "target %s; ignoring the floor",
                schedule.get(const.SCHEDULE_CONF_NAME),
                floor,
                target,
            )
            return None
        return floor

    async def _duration_bound(self, schedule: dict[str, Any]) -> float:
        """Longest wall clock the schedule's zones could occupy, in seconds.

        Priced from each zone's configured ``maximum_duration``, so it is a
        function of configuration alone. That is the whole point: it gives
        ``target − bound`` a fixed point to arm on days ahead, before any
        deficit is known, when no earliest start supplies one.
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

    @staticmethod
    def _clock_day_matches(schedule: dict[str, Any], dt_local) -> bool:
        """Whether a clock-type schedule should run on dt_local's day."""
        stype = schedule[const.SCHEDULE_CONF_TYPE]
        if stype == const.SCHEDULE_TYPE_DAILY:
            return True
        if stype == const.SCHEDULE_TYPE_WEEKLY:
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
        if stype == const.SCHEDULE_TYPE_MONTHLY:
            return dt_local.day == schedule.get(const.SCHEDULE_CONF_DAY_OF_MONTH, 1)
        return False

    async def _next_target_time(self, schedule: dict[str, Any], reference_utc=None):
        """Next UTC datetime the schedule's configured time occurs.

        This is the anchor-agnostic *target* (e.g. sunrise, or 06:00 on a
        matching day) plus any configured offset. Returns None if it can't be
        determined.

        ``reference_utc`` is the moment the "next" occurrence must fall strictly
        after; it defaults to now. Pass a prior target to get the occurrence
        *after* it (used by the finish tracker to advance past an occurrence it
        already fired instead of re-deriving the same one).
        """
        stype = schedule[const.SCHEDULE_CONF_TYPE]
        offset = datetime.timedelta(
            minutes=schedule.get(const.SCHEDULE_CONF_OFFSET_MINUTES, 0)
        )
        now_utc = reference_utc or dt_util.utcnow()

        if stype in (const.SCHEDULE_TYPE_SUNRISE, const.SCHEDULE_TYPE_SUNSET):
            event = "sunrise" if stype == const.SCHEDULE_TYPE_SUNRISE else "sunset"
            ev = get_astral_event_next(self.hass, event, now_utc)
            candidate = ev + offset
            # A NEGATIVE offset shifts the target *before* its sun event, so the
            # offset-adjusted target can land on/before the reference while the
            # raw event is still in the future (the |offset|-wide window between
            # target and the event). Advance to the following event until the
            # shifted target is strictly after the reference. Without this the
            # finish tracker — which re-arms with reference_utc=target to skip the
            # occurrence it just fired — re-derives the SAME target (the next
            # event after target is that same event, because target < event) and
            # busy-loops the "run ASAP" (now+2s) branch for the whole offset
            # window (live 2026-07-04: ~2s skips for ~30 min). Bounded so a
            # pathological offset can't spin. See test_schedule_time_anchor::
            # TestFinishTrackerAdvance::test_rearm_advances_for_negative_offset_sunrise.
            guard = 0
            while candidate <= now_utc and guard < 8:
                ev = get_astral_event_next(self.hass, event, ev)
                candidate = ev + offset
                guard += 1
            return candidate
        if stype == const.SCHEDULE_TYPE_SOLAR_AZIMUTH:
            ha_cfg = self.hass.config.as_dict()
            lat = ha_cfg.get(CONF_LATITUDE, 45.0)
            lon = ha_cfg.get(CONF_LONGITUDE, 0.0)
            angle = normalize_azimuth_angle(
                schedule.get(const.SCHEDULE_CONF_AZIMUTH_ANGLE, 90)
            )
            # UTC, aware, end to end. This used to hand over naive LOCAL time
            # while calculate_solar_azimuth documented (and read) UTC, so the
            # zone offset landed on top of the sign error the helper already
            # had — see issue #81. dt_util.as_utc on an already-UTC value below
            # is a no-op, so the surrounding offset arithmetic is unchanged.
            ref = now_utc
            # Same negative-offset advance as sunrise/sunset above: step past the
            # found occurrence until the offset-shifted target is strictly after
            # the reference, so the finish tracker doesn't busy-loop.
            guard = 0
            while True:
                next_time = find_next_solar_azimuth_time(lat, lon, angle, ref)
                if next_time is None:
                    return None
                candidate = dt_util.as_utc(next_time) + offset
                if candidate > now_utc or guard >= 8:
                    return candidate
                # find_next_solar_azimuth_time samples in 15-min steps, so a tiny
                # step re-detects the SAME crossing (the azimuth is still within a
                # sample of the target a moment later). Step past a full search
                # interval so the next search lands on the following crossing.
                ref = next_time + datetime.timedelta(minutes=16)
                guard += 1

        if stype == const.SCHEDULE_TYPE_INTERVAL:
            # Only an interval with an explicit start_time has a fixed clock
            # target; an un-anchored interval free-runs from HA start and has no
            # derivable next time (returns None, handled by the caller).
            return self._next_interval_target(schedule, now_utc)

        # Clock types: next local HH:MM that falls on a matching day.
        hour, minute = map(
            int, schedule.get(const.SCHEDULE_CONF_TIME, "06:00").split(":")
        )
        local_now = dt_util.as_local(now_utc)
        candidate = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        for _ in range(367):
            if candidate > local_now and self._clock_day_matches(schedule, candidate):
                return dt_util.as_utc(candidate)
            candidate += datetime.timedelta(days=1)
        return None

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

        Reuses the same target/anchor math the trackers use:
          - start anchor → next_run = target
          - finish anchor (irrigate only) → next_run = target − estimated duration
        Interval schedules with a ``start_time`` report the next anchored clock
        target; un-anchored intervals have no fixed target (phase depends on when
        HA started), so they report ``next_run_utc=None`` plus ``interval_hours``.
        Sorted soonest-first; entries that can't be resolved are dropped.
        """
        runs: list[dict[str, Any]] = []
        for schedule in self._schedules:
            if not schedule.get(const.SCHEDULE_CONF_ENABLED, True):
                continue
            stype = schedule[const.SCHEDULE_CONF_TYPE]
            action = schedule.get(const.SCHEDULE_CONF_ACTION, "calculate")
            zones = schedule.get(const.SCHEDULE_CONF_ZONES, "all")
            anchor = self._time_anchor(schedule)

            entry = {
                "schedule_id": schedule[const.SCHEDULE_CONF_ID],
                "name": schedule.get(const.SCHEDULE_CONF_NAME),
                "action": action,
                "zones": zones,
                "type": stype,
                "time_anchor": anchor,
                "next_run_utc": None,
                "target_utc": None,
                "duration_seconds": 0,
                # Whether the start above is a projection rather than an armed
                # moment. A two-stage schedule does not know its real start
                # until its decision point, so before then this number moves as
                # deficits grow through the day — which reads as a defect unless
                # the UI can say it is an estimate.
                "estimated": False,
                "earliest_start_utc": None,
                "fit_to_window": self._fit_to_window(schedule),
            }

            if stype == const.SCHEDULE_TYPE_INTERVAL:
                entry["interval_hours"] = schedule.get(
                    const.SCHEDULE_CONF_INTERVAL_HOURS, 24
                )
                # A start_time anchor gives a real clock target; without one the
                # interval free-runs and stays next_run_utc=None.
                target = self._next_interval_target(schedule, dt_util.utcnow())
                if target is not None:
                    entry["next_run_utc"] = target.isoformat()
                    entry["target_utc"] = target.isoformat()
                runs.append(entry)
                continue

            target = await self._next_target_time(schedule)
            if target is None:
                continue

            next_run = target
            if anchor == const.SCHEDULE_TIME_ANCHOR_FINISH and action == "irrigate":
                duration = await self._estimate_duration(schedule)
                entry["duration_seconds"] = int(duration)
                next_run = target - datetime.timedelta(seconds=duration)
                if self._uses_two_stage_arm(schedule):
                    floor = await self._earliest_start(schedule, target)
                    if floor is not None:
                        entry["earliest_start_utc"] = floor.isoformat()
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

            entry["next_run_utc"] = next_run.isoformat()
            entry["target_utc"] = target.isoformat()
            runs.append(entry)

        runs.sort(key=lambda r: r["next_run_utc"] or "9999")
        return runs

    async def _setup_finish_tracker(self, schedule: dict[str, Any]) -> Any:
        """One-shot tracker that fires at (target − duration) so the run ends at
        the configured time. Re-arms itself for the next occurrence."""
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        sid = schedule[const.SCHEDULE_CONF_ID]
        target = await self._next_target_time(schedule)
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
            nxt = await self._next_target_time(schedule, reference_utc=target)
            if nxt is None:
                _LOGGER.warning(
                    "Finish schedule '%s': could not determine next target after %s",
                    name,
                    target,
                )
                return None
            target = nxt

        if self._uses_two_stage_arm(schedule):
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

    # --- two-stage arm: decide late, then start ------------------------------

    async def _setup_fitted_tracker(self, schedule: dict[str, Any], target) -> Any:
        """Arm a schedule that has an earliest start and/or fits its window.

        Two stages, because the start time depends on a demand that is not known
        until close to the run. The single-stage tracker reads the estimate when
        it arms — on load, after each fire, and on every config change — which is
        typically hours before the run, and deficits grow all day after that. On
        seven zones at this scale that is around three hours of under-estimate:
        the run starts three hours late and overruns its finish.

        So the first stage arms on a moment that does NOT depend on the
        duration, and the second stage arms the real start once the demand has
        been read there:

            decision point = earliest start, if one is configured
                             target − bound, otherwise

        ``bound`` prices every zone at its configured ``maximum_duration``, so
        both forms are knowable in advance and the arm always has a fixed point.
        Deciding at the floor is the more accurate of the two — it is the latest
        duration-independent moment — which is why a DAYTIME finish anchor
        (syringing, seed and sod establishment, drip zones, frost protection)
        should set one: without it the decision sits a whole run-length earlier
        and an eight-hour daylight gap accrues real ET in between.
        """
        name = schedule.get(const.SCHEDULE_CONF_NAME)
        floor = await self._earliest_start(schedule, target)
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
                "earliest start" if floor is not None else "target - bound",
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
        """Read the demand, pick the zones, and arm the run's real start."""
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

        if self._fit_to_window(schedule):
            window = (target - start_floor).total_seconds()
            selection = select(
                plan,
                window_seconds=window,
                sequencing=sequencing,
                max_slot_seconds=slot,
                min_absorption_seconds=absorption,
            )
        else:
            # Floor only: no selection, no ordering, no deadline — the floor
            # bounds the start and everything due still runs, exactly as it
            # would without the floor.
            selection = plan

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

        order = (
            [p.zone_id for p in selection] if self._fit_to_window(schedule) else None
        )
        deadline = target if self._fit_to_window(schedule) else None

        def run_callback(now, s=schedule, fired=target, o=order, d=deadline):
            # Recording the fired occurrence here rather than at the decision
            # point is what lets a config change inside the window re-derive the
            # start instead of skipping the night: until the run actually fires,
            # a re-arm still resolves to THIS occurrence.
            self._finish_last_target[s[const.SCHEDULE_CONF_ID]] = fired.isoformat()
            self._execute_schedule(s, now, order=o, deadline=d, pre_committed=True)
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

    async def _setup_daily_tracker(self, schedule: dict[str, Any]) -> Any:
        """Set up a daily schedule tracker."""
        time_str = schedule[const.SCHEDULE_CONF_TIME]
        hour, minute = map(int, time_str.split(":"))

        return async_track_time_change(
            self.hass,
            lambda now: self._execute_schedule(schedule, now),
            hour=hour,
            minute=minute,
            second=0,
        )

    async def _setup_weekly_tracker(self, schedule: dict[str, Any]) -> Any:
        """Set up a weekly schedule tracker."""
        time_str = schedule[const.SCHEDULE_CONF_TIME]
        hour, minute = map(int, time_str.split(":"))
        days_of_week = schedule.get(const.SCHEDULE_CONF_DAYS_OF_WEEK, [])

        # Convert day names to numbers (0=Monday, 6=Sunday)
        day_mapping = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        def check_and_execute(now):
            current_weekday = now.weekday()
            day_names = [day.lower() for day in days_of_week]
            if any(
                day_mapping.get(day_name) == current_weekday for day_name in day_names
            ):
                self._execute_schedule(schedule, now)

        return async_track_time_change(
            self.hass, check_and_execute, hour=hour, minute=minute, second=0
        )

    async def _setup_monthly_tracker(self, schedule: dict[str, Any]) -> Any:
        """Set up a monthly schedule tracker."""
        time_str = schedule[const.SCHEDULE_CONF_TIME]
        hour, minute = map(int, time_str.split(":"))
        day_of_month = schedule.get(const.SCHEDULE_CONF_DAY_OF_MONTH, 1)

        def check_and_execute(now):
            if now.day == day_of_month:
                self._execute_schedule(schedule, now)

        return async_track_time_change(
            self.hass, check_and_execute, hour=hour, minute=minute, second=0
        )

    async def _setup_interval_tracker(self, schedule: dict[str, Any]) -> Any:
        """Set up an interval-based schedule tracker.

        With a ``start_time`` anchor the interval is phase-locked to that clock
        time: it uses a one-shot, self-rescheduling point-in-time tracker (the
        same pattern as the azimuth/finish trackers) so each fire re-arms on the
        next anchored occurrence. Without a start_time it free-runs every
        ``interval_hours`` from now — the original behaviour, unchanged.
        """
        if schedule.get(const.SCHEDULE_CONF_START_TIME):
            target = await self._next_target_time(schedule)
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
                # outside the event loop (mirrors the azimuth tracker).
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

    async def _setup_sunrise_tracker(self, schedule: dict[str, Any]) -> Any:
        """Sunrise schedule tracker (start anchor). Finish anchor goes through
        _setup_finish_tracker."""
        offset_minutes = schedule.get(const.SCHEDULE_CONF_OFFSET_MINUTES, 0)
        _LOGGER.info(
            "Registered sunrise schedule '%s' (start, offset %s min)",
            schedule.get(const.SCHEDULE_CONF_NAME),
            offset_minutes,
        )
        # HA invokes the sunrise/sunset callback with NO arguments
        # (async_run_hass_job on a Callable[[], None]), unlike
        # async_track_point_in_utc_time / async_track_time_change which pass
        # `now`. A one-arg lambda would raise TypeError at fire time and the
        # schedule would silently never run, so supply the fire time ourselves.
        return async_track_sunrise(
            self.hass,
            lambda: self._execute_schedule(schedule, dt_util.utcnow()),
            datetime.timedelta(minutes=offset_minutes),
        )

    async def _setup_sunset_tracker(self, schedule: dict[str, Any]) -> Any:
        """Sunset schedule tracker (start anchor). Finish anchor goes through
        _setup_finish_tracker."""
        offset_minutes = schedule.get(const.SCHEDULE_CONF_OFFSET_MINUTES, 0)
        _LOGGER.info(
            "Registered sunset schedule '%s' (start, offset %s min)",
            schedule.get(const.SCHEDULE_CONF_NAME),
            offset_minutes,
        )
        # See _setup_sunrise_tracker: HA calls this callback with no arguments,
        # so a one-arg lambda would raise and the schedule would never run.
        return async_track_sunset(
            self.hass,
            lambda: self._execute_schedule(schedule, dt_util.utcnow()),
            datetime.timedelta(minutes=offset_minutes),
        )

    async def _setup_azimuth_tracker(self, schedule: dict[str, Any]) -> Any:
        """Solar azimuth schedule tracker (start anchor; one-shot, self-rescheduling).
        Finish anchor goes through _setup_finish_tracker."""
        target = await self._next_target_time(schedule)
        if target is None:
            _LOGGER.warning(
                "Could not calculate next azimuth time for schedule '%s'",
                schedule.get(const.SCHEDULE_CONF_NAME),
            )
            return None

        def azimuth_callback(now, s=schedule):
            self._execute_schedule(s, now)
            # Re-register for next occurrence — thread-safe wrapper required because
            # async_track_point_in_utc_time callbacks may fire outside the event loop
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task,
                self._reregister_tracker(s),
            )

        _LOGGER.info(
            "Registered azimuth schedule '%s' (start) at %s",
            schedule.get(const.SCHEDULE_CONF_NAME),
            target,
        )
        return async_track_point_in_utc_time(self.hass, azimuth_callback, target)

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

        ``order`` and ``deadline`` are set only by a fitted run's second stage:
        the zone ids chosen at the decision point, in priority order, and the
        finish target the runner must not water past. ``pre_committed`` says a
        two-stage schedule already committed its pre-run calculation there.
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
        """Validate schedule data."""
        required_fields = [const.SCHEDULE_CONF_NAME, const.SCHEDULE_CONF_TYPE]
        for field in required_fields:
            if field not in schedule_data:
                raise ValueError(f"Missing required field: {field}")

        schedule_type = schedule_data[const.SCHEDULE_CONF_TYPE]
        if schedule_type not in const.SCHEDULE_TYPES:
            raise ValueError(f"Invalid schedule type: {schedule_type}")

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

        # Validate time format if provided
        if const.SCHEDULE_CONF_TIME in schedule_data:
            time_str = schedule_data[const.SCHEDULE_CONF_TIME]
            try:
                datetime.datetime.strptime(time_str, "%H:%M")
            except ValueError as e:
                raise ValueError(
                    f"Invalid time format: {time_str}. Expected HH:MM"
                ) from e

        # Validate the optional interval start_time anchor the same way.
        start_time_str = schedule_data.get(const.SCHEDULE_CONF_START_TIME)
        if start_time_str:
            try:
                datetime.datetime.strptime(start_time_str, "%H:%M")
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid start time format: {start_time_str}. Expected HH:MM"
                ) from e

        # Earliest start. Rejected here rather than shrugged off at arm time: a
        # floor is the only thing keeping a long run out of the evening, so a
        # typo that silently disables it would show up as watering at sunset.
        mode = schedule_data.get(const.SCHEDULE_CONF_EARLIEST_START_MODE)
        if mode is not None and mode not in const.SCHEDULE_EARLIEST_START_MODES:
            raise ValueError(
                f"Invalid earliest start mode: {mode}. Expected one of "
                f"{const.SCHEDULE_EARLIEST_START_MODES}"
            )
        if mode == const.SCHEDULE_EARLIEST_START_TIME:
            earliest = schedule_data.get(const.SCHEDULE_CONF_EARLIEST_START_TIME)
            try:
                datetime.datetime.strptime(earliest, "%H:%M")
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid earliest start time: {earliest}. Expected HH:MM"
                ) from e
        if mode == const.SCHEDULE_EARLIEST_START_SUNSET:
            offset = schedule_data.get(const.SCHEDULE_CONF_EARLIEST_START_OFFSET, 0)
            try:
                int(offset or 0)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid earliest start offset: {offset}. Expected minutes"
                ) from e

        # Schedules have no voluptuous schema (websocket_save_schedule hands the
        # raw dict straight through), so this is the only gate on the type. A
        # string "false" would otherwise read truthy and silently turn fitting
        # on, which changes both the zone set and the run's deadline.
        if const.SCHEDULE_CONF_FIT_TO_WINDOW in schedule_data and not isinstance(
            schedule_data[const.SCHEDULE_CONF_FIT_TO_WINDOW], bool
        ):
            raise ValueError(
                "Invalid fit to window: "
                f"{schedule_data[const.SCHEDULE_CONF_FIT_TO_WINDOW]}. Expected a boolean"
            )

    def _generate_schedule_id(self) -> str:
        """Generate a unique schedule ID."""
        return f"schedule_{uuid.uuid4().hex[:8]}"

    def get_schedules(self) -> list[dict[str, Any]]:
        """Get all schedules."""
        return self._schedules.copy()
