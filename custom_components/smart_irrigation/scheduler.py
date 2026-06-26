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
from homeassistant.helpers.sun import get_astral_event_next

from . import const
from .helpers import find_next_solar_azimuth_time, normalize_azimuth_angle

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
        self._finish_last_target: dict[str, str] = {}

    async def async_load_schedules(self) -> None:
        """Load recurring schedules from configuration."""
        config = await self.coordinator.store.async_get_config()
        self._schedules = config.get(const.CONF_RECURRING_SCHEDULES, [])
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

    @callback
    def _on_config_updated(self, *_args) -> None:
        """React to config/duration changes by re-arming finish schedules."""
        self.hass.async_create_task(self.async_rearm_finish_schedules())

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

        if stype == const.SCHEDULE_TYPE_SUNRISE:
            return get_astral_event_next(self.hass, "sunrise", now_utc) + offset
        if stype == const.SCHEDULE_TYPE_SUNSET:
            return get_astral_event_next(self.hass, "sunset", now_utc) + offset
        if stype == const.SCHEDULE_TYPE_SOLAR_AZIMUTH:
            ha_cfg = self.hass.config.as_dict()
            next_time = find_next_solar_azimuth_time(
                ha_cfg.get(CONF_LATITUDE, 45.0),
                ha_cfg.get(CONF_LONGITUDE, 0.0),
                normalize_azimuth_angle(
                    schedule.get(const.SCHEDULE_CONF_AZIMUTH_ANGLE, 90)
                ),
                dt_util.as_local(now_utc).replace(tzinfo=None),
            )
            if next_time is None:
                return None
            return dt_util.as_utc(next_time) + offset

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

        duration = await self._estimate_duration(schedule)

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
            self._finish_last_target[s[const.SCHEDULE_CONF_ID]] = fired.isoformat()
            self._execute_schedule(s, now)
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task, self._reregister_tracker(s)
            )

        return async_track_point_in_utc_time(self.hass, finish_callback, fire_time)

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
        return async_track_sunrise(
            self.hass,
            lambda now: self._execute_schedule(schedule, now),
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
        return async_track_sunset(
            self.hass,
            lambda now: self._execute_schedule(schedule, now),
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
        self, schedule: dict[str, Any], now: datetime.datetime
    ) -> None:
        """Execute a scheduled action."""
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
                "timestamp": now.isoformat(),
            },
        )

        self.hass.loop.call_soon_threadsafe(
            self.hass.async_create_task,
            self._perform_schedule_action(action, zones, schedule_name),
        )

    async def _perform_schedule_action(
        self, action: str, zones: str | list[str], schedule_name: str
    ) -> None:
        """Perform the scheduled action."""
        try:
            if action == "calculate":
                if zones == "all":
                    await self.coordinator._async_calculate_all()
                else:
                    # Per-zone calculate must aggregate the mapping's weather data
                    # first; route through async_update_zone_config (ATTR_CALCULATE),
                    # which does the aggregation + forecast fetch before calculating.
                    for zone_id in zones:
                        await self.coordinator.async_update_zone_config(
                            zone_id, {const.ATTR_CALCULATE: True}
                        )
            elif action == "update":
                if zones == "all":
                    await self.coordinator._async_update_all()
                else:
                    for zone_id in zones:
                        await self.coordinator._async_update_zone(zone_id)
            elif action == "irrigate":
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
                await self.coordinator._irrigate_linked_entities(zones)
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

    def _generate_schedule_id(self) -> str:
        """Generate a unique schedule ID."""
        return f"schedule_{uuid.uuid4().hex[:8]}"

    def get_schedules(self) -> list[dict[str, Any]]:
        """Get all schedules."""
        return self._schedules.copy()
