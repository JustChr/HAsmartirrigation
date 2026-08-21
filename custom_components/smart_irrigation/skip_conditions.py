"""Irrigation skip-condition checks and days-between tracking.

Extracted from __init__.py (Phase C5). Methods live on a mixin the coordinator
inherits; bodies unchanged (still use ``self``). Covers the pre-irrigation
decision logic: skip on precipitation forecast / temperature / wind / rain
sensor, the days-between-irrigation counter, and the total-duration query used
by the scheduler and websockets.
"""

import logging

import homeassistant.util.dt as dt_util

from . import const
from .helpers import normalize_zone_selection
from .run_window import concurrent_wall_clock

_LOGGER = logging.getLogger(__name__)

# Stable ids for each skip guard; mirrored by the frontend localization keys.
SKIP_PRECIPITATION = "precipitation"
SKIP_DAYS_BETWEEN = "days_between"
SKIP_TEMPERATURE = "temperature"
SKIP_WIND = "wind"
SKIP_FREEZE = "freeze"
SKIP_RAIN_SENSOR = "rain_sensor"


class SkipConditionsMixin:
    """Skip-condition checks for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    async def _check_skip_conditions(self) -> bool:
        """Return True if irrigation should be skipped (any condition is met).

        Evaluates every guard (rather than short-circuiting) so the result can be
        persisted as the dashboard's "last run" explanation; the return value is
        unchanged (skip if any enabled guard is met).
        """
        evaluation = await self.async_evaluate_skip_conditions()
        self._last_skip_evaluation = {
            "timestamp": dt_util.utcnow().isoformat(),
            "would_skip": evaluation["would_skip"],
            "checks": evaluation["checks"],
        }
        if evaluation["would_skip"]:
            reasons = [
                c["id"]
                for c in evaluation["checks"]
                if c["enabled"] and c["would_skip"]
            ]
            _LOGGER.info("Irrigation skipped due to conditions: %s", ", ".join(reasons))
        return evaluation["would_skip"]

    # --- structured (no-side-effect) evaluation for the dashboard outlook ----

    async def async_evaluate_skip_conditions(self) -> dict:
        """Evaluate every skip guard and return structured results.

        Unlike the boolean ``_check_*`` helpers this does not log skip decisions;
        it is safe to call for a live preview. Each check is a dict with keys
        ``id``, ``enabled``, ``would_skip``, ``available`` (could it be
        evaluated), ``observed`` and ``threshold``. Precipitation/temperature/
        wind reuse the in-memory weather-client cache, so this is normally cheap.
        """
        config = await self.store.async_get_config()
        checks = [
            await self._eval_precipitation(config),
            await self._eval_days_between(config),
            await self._eval_temp(config),
            await self._eval_wind(config),
            await self._eval_freeze(config),
            await self._eval_rain_sensor(config),
        ]
        would_skip = any(c["enabled"] and c["would_skip"] for c in checks)
        return {"would_skip": would_skip, "checks": checks}

    async def async_get_irrigation_outlook(self) -> dict:
        """Assemble the dashboard outlook: next runs + skip preview + last run.

        ``skip_preview`` is evaluated live (as of now — forecasts may change
        before the run). ``last_skip_evaluation`` is the persisted result of the
        most recent real scheduled-irrigate decision (None until one has run, or
        after a restart).
        """
        config = await self.store.async_get_config()
        skip_preview = await self.async_evaluate_skip_conditions()
        upcoming = await self.recurring_schedule_manager.async_get_upcoming_runs()
        # The days-between guard is a day counter bumped at local midnight, so a
        # live "as of now" evaluation is pessimistic right after a run (counter
        # 0). Project it to the next scheduled irrigate run so the preview shows
        # what the run-time decision will actually be.
        self._project_days_between_to_next_run(skip_preview, upcoming)
        try:
            # Served from the cache maintained by the update/calc cycles
            # (computed once on demand if no cycle has run yet).
            zone_estimates = await self.async_get_cached_zone_estimates()
        except Exception as e:  # noqa: BLE001 — outlook must not fail on the estimate
            _LOGGER.debug("Intra-day estimates unavailable: %s", e)
            zone_estimates = {}
        # Per-zone run faults (WS-1): keyed by zone id (string) so the dashboard
        # can flag a zone whose last run failed (e.g. the valve never opened).
        faults = {str(zid): f for zid, f in self.get_zone_faults().items()}
        # Per-zone soil-moisture skips (soil-veto): keyed by zone id (string) so
        # the dashboard can flag *why* a zone did not water on the last run.
        skips = {str(zid): s for zid, s in self.get_zone_skips().items()}
        return {
            "weather_service_enabled": bool(
                config.get(
                    const.CONF_USE_WEATHER_SERVICE,
                    const.CONF_DEFAULT_USE_WEATHER_SERVICE,
                )
            ),
            "skip_preview": skip_preview,
            "last_skip_evaluation": getattr(self, "_last_skip_evaluation", None),
            "upcoming_runs": upcoming,
            "zone_estimates": zone_estimates,
            "zone_faults": faults,
            "zone_skips": skips,
            # In-progress runs keyed by zone id (string): {started_at, ends_at}.
            # ends_at is null for flow-metered (volume-bounded) runs. Lets the
            # dashboard show a Stop control + a live countdown while a zone waters.
            "active_runs": self.get_active_runs(),
            # Rain delay / vacation hold (WS-5): ISO datetime the automatic
            # irrigation resumes, or None when no hold is active.
            "rain_delay_until": config.get(const.CONF_RAIN_DELAY_UNTIL),
        }

    async def _eval_precipitation(self, config) -> dict:
        """Structured precipitation-forecast guard (today+tomorrow vs threshold)."""
        threshold = config.get(
            const.CONF_PRECIPITATION_THRESHOLD_MM,
            const.CONF_DEFAULT_PRECIPITATION_THRESHOLD_MM,
        )
        result = {
            "id": SKIP_PRECIPITATION,
            "enabled": bool(
                config.get(
                    const.CONF_SKIP_IRRIGATION_ON_PRECIPITATION,
                    const.CONF_DEFAULT_SKIP_IRRIGATION_ON_PRECIPITATION,
                )
            ),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": threshold,
        }
        if not result["enabled"]:
            return result
        use_weather_service = config.get(
            const.CONF_USE_WEATHER_SERVICE, const.CONF_DEFAULT_USE_WEATHER_SERVICE
        )
        if not use_weather_service or self._WeatherServiceClient is None:
            return result
        try:
            forecast_data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_forecast_data
            )
            if not forecast_data:
                return result
            days = max(
                1,
                config.get(
                    const.CONF_PRECIPITATION_FORECAST_DAYS,
                    const.CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS,
                ),
            )
            total = 0.0
            for day_data in forecast_data[:days]:
                if const.MAPPING_PRECIPITATION in day_data:
                    total += day_data[const.MAPPING_PRECIPITATION]
            result["available"] = True
            result["observed"] = round(total, 2)
            result["would_skip"] = total >= threshold
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: precipitation eval failed: %s", e)
        return result

    async def _eval_days_between(self, config) -> dict:
        """Structured days-between-irrigation guard.

        The counter is per zone, so this whole-run guard reports the zone that
        has waited LONGEST and skips only when no zone has waited long enough.
        Reporting the global counter instead would skip the entire run whenever
        the most recently watered zone was still in its wait, which is exactly
        how a truncated run used to starve the tail of the priority order. The
        per-zone decision is made in ``_zone_days_between_blocked``, applied as a
        filter by the runner.
        """
        days_between = config.get(
            const.CONF_DAYS_BETWEEN_IRRIGATION,
            const.CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
        )
        global_days = config.get(
            const.CONF_DAYS_SINCE_LAST_IRRIGATION,
            const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
        )
        enabled = days_between > 0
        days_since = global_days
        if enabled:
            try:
                per_zone = [
                    z.get(const.ZONE_DAYS_SINCE_IRRIGATION)
                    for z in await self.store.async_get_zones()
                    if z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
                    and z.get(const.ZONE_DAYS_SINCE_IRRIGATION) is not None
                ]
            except Exception as e:  # noqa: BLE001 — preview must never raise
                _LOGGER.debug("Skip preview: days-between eval failed: %s", e)
                per_zone = []
            if per_zone:
                days_since = max(per_zone)
        return {
            "id": SKIP_DAYS_BETWEEN,
            "enabled": enabled,
            "would_skip": enabled and days_since < days_between,
            "available": True,
            "observed": days_since,
            "threshold": days_between,
        }

    @staticmethod
    def _project_days_between_to_next_run(skip_preview: dict, upcoming: list) -> None:
        """Advance the days-between preview to the next irrigate run's date.

        The counter increments once per local midnight (see
        ``_increment_days_since_irrigation``), so the value at the next run is
        ``days_since + (next_run_date − today)``. Mutates the days-between check
        in ``skip_preview`` in place; no-op when the guard is disabled, the
        counter can't be projected, or no future irrigate run is scheduled.
        Preview-only — the real run-time gate in ``_eval_days_between`` is
        untouched (it fires on the run day, where the offset is 0).
        """
        check = next(
            (c for c in skip_preview["checks"] if c["id"] == SKIP_DAYS_BETWEEN),
            None,
        )
        if check is None or not check["enabled"]:
            return
        next_run = next(
            (
                r["next_run_utc"]
                for r in upcoming
                if r.get("action") == "irrigate" and r.get("next_run_utc")
            ),
            None,
        )
        if not next_run:
            return
        run_dt = dt_util.parse_datetime(next_run)
        if run_dt is None:
            return
        offset = (dt_util.as_local(run_dt).date() - dt_util.now().date()).days
        if offset <= 0:
            return
        projected = check["observed"] + offset
        check["observed"] = projected
        check["would_skip"] = projected < check["threshold"]

    async def _eval_temp(self, config) -> dict:
        """Structured low-temperature guard (current conditions)."""
        threshold = config.get(
            const.CONF_TEMP_THRESHOLD, const.CONF_DEFAULT_TEMP_THRESHOLD
        )
        result = {
            "id": SKIP_TEMPERATURE,
            "enabled": bool(
                config.get(
                    const.CONF_SKIP_TEMP_ENABLED, const.CONF_DEFAULT_SKIP_TEMP_ENABLED
                )
            ),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": threshold,
        }
        if not result["enabled"] or self._WeatherServiceClient is None:
            return result
        try:
            data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_data
            )
            temp = (data or {}).get(const.MAPPING_TEMPERATURE)
            if temp is not None:
                result["available"] = True
                result["observed"] = round(temp, 1)
                result["would_skip"] = temp < threshold
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: temperature eval failed: %s", e)
        return result

    async def _eval_wind(self, config) -> dict:
        """Structured high-wind guard (current conditions)."""
        threshold = config.get(
            const.CONF_WIND_THRESHOLD, const.CONF_DEFAULT_WIND_THRESHOLD
        )
        result = {
            "id": SKIP_WIND,
            "enabled": bool(
                config.get(
                    const.CONF_SKIP_WIND_ENABLED, const.CONF_DEFAULT_SKIP_WIND_ENABLED
                )
            ),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": threshold,
        }
        if not result["enabled"] or self._WeatherServiceClient is None:
            return result
        try:
            data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_data
            )
            wind = (data or {}).get(const.MAPPING_WINDSPEED)
            if wind is not None:
                result["available"] = True
                result["observed"] = round(wind, 2)
                result["would_skip"] = wind > threshold
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: wind eval failed: %s", e)
        return result

    async def _eval_freeze(self, config) -> dict:
        """Structured freeze guard (frost expected → skip to protect pipes/plants).

        Frost-specific and distinct from the low-temperature guard: it watches the
        *minimum* of the current reading and the next forecast day's minimum (the
        coming night, which the daily forecast covers since clients exclude today),
        so a clear sub-freezing night is caught even when it is mild right now.
        """
        threshold = config.get(
            const.CONF_FREEZE_THRESHOLD, const.CONF_DEFAULT_FREEZE_THRESHOLD
        )
        result = {
            "id": SKIP_FREEZE,
            "enabled": bool(
                config.get(
                    const.CONF_SKIP_FREEZE_ENABLED,
                    const.CONF_DEFAULT_SKIP_FREEZE_ENABLED,
                )
            ),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": threshold,
        }
        if not result["enabled"] or self._WeatherServiceClient is None:
            return result
        candidates = []
        try:
            data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_data
            )
            temp = (data or {}).get(const.MAPPING_TEMPERATURE)
            if temp is not None:
                candidates.append(temp)
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: freeze (current) eval failed: %s", e)
        try:
            forecast_data = await self.hass.async_add_executor_job(
                self._WeatherServiceClient.get_forecast_data
            )
            if forecast_data:
                tmin = forecast_data[0].get(const.MAPPING_MIN_TEMP)
                if tmin is not None:
                    candidates.append(tmin)
        except Exception as e:  # noqa: BLE001 — preview must never raise
            _LOGGER.debug("Skip preview: freeze (forecast) eval failed: %s", e)
        if candidates:
            observed = min(candidates)
            result["available"] = True
            result["observed"] = round(observed, 1)
            result["would_skip"] = observed < threshold
        return result

    async def _eval_rain_sensor(self, config) -> dict:
        """Structured rain-sensor guard (live HA entity state)."""
        sensor = config.get(const.CONF_RAIN_SENSOR, const.CONF_DEFAULT_RAIN_SENSOR)
        result = {
            "id": SKIP_RAIN_SENSOR,
            "enabled": bool(sensor),
            "would_skip": False,
            "available": False,
            "observed": None,
            "threshold": None,
            "entity_id": sensor or None,
        }
        if not sensor:
            return result
        state = self.hass.states.get(sensor)
        if state is None:
            return result
        result["available"] = True
        result["observed"] = state.state
        result["would_skip"] = state.state == "on"
        return result

    async def get_total_irrigation_duration(self, zone_ids=None) -> int:
        """Estimate the wall-clock irrigation time (seconds) for the given zones.

        Multi-track model, used to anchor "finish at time" schedules. Each track
        is a set of zones that runs as one unit, and the tracks run CONCURRENTLY
        with one another — ``_dispatch_by_mode`` starts each of them and returns
        without waiting, so the wall-clock is the LONGEST track, not their sum:

          * classic track — the linked-entity zones, reduced per zone_sequencing.
          * self-closing track — ``service``-mode zones, always max(duration).
            zone_sequencing does NOT reach them: ``_dispatch_by_mode`` fires
            every one of them in a single loop and the hardware owns each close,
            so they open together whatever the setting says. Summing them
            over-estimated the cycle and started a finish-anchored schedule too
            early on any install that had chosen sequential or rotating.
          * station track — OpenSprinkler zones, always sum(duration). Under
            sequential/rotating Smart Irrigation chains them itself; under
            parallel it hands the controller everything at once, and whether a
            station then waits for the ones before it is a flag in the
            CONTROLLER's own configuration which this integration cannot read
            (see opensprinkler.py's header). Serialised is the longer of the two
            possibilities, and only an over-estimate is safe here — an
            under-estimate finishes the irrigation after the anchor.
          * batch track — batch/queue zones, always sum(duration). The whole
            irrigation is handed over as one queue and a queue waters one valve
            at a time, so unlike the station track there is no ambiguity to
            hedge: the serialisation is a property of the mode itself.

            All four come from the shared :meth:`async_plan_zone_runs`
            projection and are reduced through
            :func:`run_window.concurrent_wall_clock`, which owns the per-track
            sequencing.
          * distributor track — one distributor_cycle_estimate per in-scope
            distributor (windows + n pauses + settle + buffer). Distributor
            cycles are dispatched strictly SEQUENTIALLY regardless of
            zone_sequencing, so their estimates always SUM (H2, review #12).
            Only distributors the executor would actually sweep are counted,
            via the shared _dist_eligible_for_run predicate (H2, review #11) —
            so the estimate no longer over-counts an unsynced / unconfirmed /
            mid-cycle distributor, or one whose members are not due.

        An install whose zones are all classic — the default, and every install
        that predates the self-closing modes — has one zone track and collapses
        to the plain sequencing reduction.

        Two further things the reduction has to get right, both of which moved
        the anchor when it did not:

        * The zone set and the durations are the run's own, not the stored daily
          ``ZONE_DURATION``. Under the live-estimate gate the run sizes from the
          intra-day deficit — which can exceed the stored bucket — over a
          different zone set, so reading the stored value was wrong in both
          directions at once. Pricing the projection prices what the run does.
        * Rotating is not a sum. The sum is watering time; the absorption pauses
          between a zone's slots are wall clock too, and the rotating runner's
          own docstring records a predicted deadline having cut the pump
          mid-rotation for want of them.

        ``zone_ids`` is an iterable of zone ids to include, or None/"all" for
        every enabled (automatic/manual) zone. Only positive durations count.
        """
        planned = await self.async_plan_zone_runs(zone_ids)
        selection = normalize_zone_selection(zone_ids)
        target = None if selection is None else {int(z) for z in selection}

        dist_track = 0
        for dist in await self.store.async_get_distributors():
            members = await self._dist_members(dist.get("id"))
            in_scope = [
                m
                for m in members
                if target is None or int(m.get(const.ZONE_ID)) in target
            ]
            if not in_scope:
                continue
            if not self._dist_eligible_for_run(dist, members):
                continue
            # Review I-1: pass the FULL member ring + the target (only_zone_ids), NOT
            # the target-compacted `in_scope`. The real cycle sweeps the whole
            # physical ring, skip-pulsing every non-targeted outlet up to the last
            # targeted one; compacting to `in_scope` dropped those leading skips +
            # pauses and under-counted a subset-targeted sweep, so a finish-anchored
            # schedule started too late. `in_scope` still gates WHETHER to count this
            # distributor (any targeted member present). distributor cycles are
            # dispatched strictly sequentially regardless of zone_sequencing, so
            # their estimates always sum.
            only = (
                None
                if target is None
                else [int(m.get(const.ZONE_ID)) for m in in_scope]
            )
            dist_track += int(
                self.distributor_cycle_estimate(dist, members, only_zone_ids=only)
            )

        sequencing, slot_seconds, absorption_seconds = self.sequencing_timing()
        zone_track = concurrent_wall_clock(
            planned,
            sequencing=sequencing,
            max_slot_seconds=slot_seconds,
            min_absorption_seconds=absorption_seconds,
        )
        # The zone tracks run as background tasks concurrently with the awaited
        # distributor dispatch, so wall-clock is the longest track of all.
        return int(max(zone_track, dist_track))

    async def _increment_days_since_irrigation(self):
        """Bump the days-since-irrigation counters (global and per zone)."""
        config = await self.store.async_get_config()
        current_days = config.get(
            const.CONF_DAYS_SINCE_LAST_IRRIGATION,
            const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
        )

        new_days = current_days + 1
        await self.store.async_update_config(
            {const.CONF_DAYS_SINCE_LAST_IRRIGATION: new_days}
        )
        for zone in await self.store.async_get_zones():
            days = zone.get(
                const.ZONE_DAYS_SINCE_IRRIGATION,
                const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
            )
            await self.store.async_update_zone(
                zone.get(const.ZONE_ID),
                {const.ZONE_DAYS_SINCE_IRRIGATION: (days or 0) + 1},
            )

        _LOGGER.debug("Incremented days since last irrigation to %d", new_days)

    async def _reset_days_since_irrigation(self):
        """Reset the GLOBAL days-since-irrigation counter to 0.

        Global only. Each zone's own counter is reset by
        ``async_write_watered_bucket``, in the same write as the water it is
        recording — the only place that knows which zones actually got water. A
        sequential or rotating run is a background task that can still be
        watering hours after this returns, so resetting per-zone counters here
        would clear them for zones a deadline or a mid-run re-price never
        reaches, which is exactly the starvation the per-zone counter exists to
        prevent. The global value survives for the dashboard preview.
        """
        await self.store.async_update_config({const.CONF_DAYS_SINCE_LAST_IRRIGATION: 0})

        _LOGGER.debug("Reset days since last irrigation to 0")

    def _days_between_setting(self) -> int:
        """The configured days-between-irrigation wait, 0 when off.

        Read from the in-memory config off the runner's hot path, and coerced,
        because an unreadable value here must leave the guard OFF rather than
        raise inside a dispatch and cancel the night's watering.
        """
        try:
            value = getattr(
                self.store.config,
                "days_between_irrigation",
                const.CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
            )
            return max(0, int(value))
        except (AttributeError, TypeError, ValueError):
            return 0

    def _zone_days_between_blocked(self, zone: dict, days_between: int) -> bool:
        """Whether the days-between guard still holds this zone back.

        A zone with no per-zone counter yet (hydrated before the counter
        existed, and not through a midnight since) reads as never watered, so it
        is not held: erring towards watering is the safe direction for a guard
        whose whole failure mode is stranding a dry zone.
        """
        days_since = zone.get(const.ZONE_DAYS_SINCE_IRRIGATION)
        if days_since is None:
            return False
        try:
            return int(days_since) < days_between
        except (TypeError, ValueError):
            return False
