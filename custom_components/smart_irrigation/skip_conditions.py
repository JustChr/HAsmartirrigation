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
        """Structured days-between-irrigation guard (pure config math)."""
        days_between = config.get(
            const.CONF_DAYS_BETWEEN_IRRIGATION,
            const.CONF_DEFAULT_DAYS_BETWEEN_IRRIGATION,
        )
        days_since = config.get(
            const.CONF_DAYS_SINCE_LAST_IRRIGATION,
            const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
        )
        enabled = days_between > 0
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

        Two-track model, used to anchor "finish at time" schedules. Normal
        (non-member) zones and distributor sweeps run on separate tracks:

          * normal track — the linked-entity zones, reduced per zone_sequencing
            (parallel: max(duration); sequential/rotating: sum(duration)).
          * distributor track — one distributor_cycle_estimate per in-scope
            distributor (windows + n pauses + settle + buffer). Distributor
            cycles are dispatched strictly SEQUENTIALLY regardless of
            zone_sequencing, so their estimates always SUM (H2, review #12).
            Only distributors the executor would actually sweep are counted,
            via the shared _dist_eligible_for_run predicate (H2, review #11) —
            so the estimate no longer over-counts an unsynced / unconfirmed /
            mid-cycle distributor, or one whose members are not due.

        Normal zones run as background tasks concurrently with the awaited
        distributor dispatch, so the wall-clock is the LONGER of the two tracks
        (max). With no distributors this collapses to the original normal-track
        reduction, preserving backward-compatible anchor times.

        ``zone_ids`` is an iterable of zone ids to include, or None/"all" for
        every enabled (automatic/manual) zone. Only positive durations count.
        """
        zones = await self.store.async_get_zones()
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}

        normal = []
        for zone in zones:
            if zone.get(const.ZONE_STATE) not in (
                const.ZONE_STATE_AUTOMATIC,
                const.ZONE_STATE_MANUAL,
            ):
                continue
            if target is not None and int(zone.get(const.ZONE_ID)) not in target:
                continue
            if zone.get(const.ZONE_DISTRIBUTOR_ID) is not None:
                continue
            duration = zone.get(const.ZONE_DURATION, 0) or 0
            if duration > 0:
                normal.append(duration)

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

        if self.store.config.zone_sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL:
            normal_track = max(normal) if normal else 0
        else:
            normal_track = sum(normal)
        # normal zones run as background tasks concurrently with the awaited
        # distributor dispatch, so wall-clock is the longer of the two tracks.
        return int(max(normal_track, dist_track))

    async def _increment_days_since_irrigation(self):
        """Increment the counter for days since last irrigation."""
        config = await self.store.async_get_config()
        current_days = config.get(
            const.CONF_DAYS_SINCE_LAST_IRRIGATION,
            const.CONF_DEFAULT_DAYS_SINCE_LAST_IRRIGATION,
        )

        new_days = current_days + 1
        await self.store.async_update_config(
            {const.CONF_DAYS_SINCE_LAST_IRRIGATION: new_days}
        )

        _LOGGER.debug("Incremented days since last irrigation to %d", new_days)

    async def _reset_days_since_irrigation(self):
        """Reset the counter for days since last irrigation to 0."""
        await self.store.async_update_config({const.CONF_DAYS_SINCE_LAST_IRRIGATION: 0})

        _LOGGER.debug("Reset days since last irrigation to 0")
