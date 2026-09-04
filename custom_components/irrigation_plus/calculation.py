"""Weather-data aggregation and ET/bucket calculation for Irrigation Plus.

Extracted from __init__.py (Phase C4). Methods live on a mixin the coordinator
inherits; bodies unchanged (still use ``self``). Covers the weather->calculation
pipeline: merging weather + sensor values, aggregating mapping data, loading the
calculation module, and computing the ET delta / bucket / duration per zone.
Protected by tests/test_calculate_module.py (calculate_module characterization).
"""

import logging
from datetime import datetime, timedelta

import homeassistant.util.dt as dt_util
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .calcmodules.pyeto import SOLRAD_behavior
from .duration_math import duration_from_deficit, zone_run_duration  # noqa: F401
from .et_estimate import (
    SiteGeometry,
    drained_over_window,
    hourly_eto_priced,
    replay_water_balance,
)
from .helpers import as_datetime as _as_datetime
from .helpers import convert_between, loadModules
from .localize import localize
from .weather_aggregate import (
    aggregate_window,
    build_substeps,
    merge_latest_per_field,
    select_window,
)

_LOGGER = logging.getLogger(__name__)

# How long a reading may linger in the shared mapping buffer before it is pruned
# regardless of zone watermarks (bounds storage if a zone stops consuming).
BUFFER_RETENTION = timedelta(days=7)


def pending_bucket_events(zone):
    """A zone's unconsumed mid-window bucket credits as ``[(naive_local, mm)]``.

    Stored aware (see ``IrrigationRunnerMixin.async_write_watered_bucket``) and
    flattened to naive local here, because the window these have to be placed on
    is built from naive ``datetime.now()`` stamps and mixing the two raises.
    Entries that will not parse are dropped rather than defaulted to a time: a
    credit placed at the wrong instant is worse than one placed at the window
    start, which is what dropping it falls back to.
    """
    out = []
    for entry in zone.get(const.ZONE_PENDING_BUCKET_EVENTS) or []:
        if not isinstance(entry, dict):
            continue
        stamp = _as_datetime(entry.get("ts"))
        if stamp is None:
            continue
        if stamp.tzinfo is not None:
            stamp = dt_util.as_local(stamp).replace(tzinfo=None)
        try:
            mm = float(entry.get("mm"))
        except (TypeError, ValueError):
            continue
        if mm:
            out.append((stamp, mm))
    return out


def hourly_calculation_enabled(store) -> bool:
    """Whether this install has opted into the hourly form of the calculation.

    Free function over the store rather than a method, so the commit and the live
    estimate read the switch through the same call: the estimate's mixin is
    instantiated on its own in its tests, where a cross-mixin call raises, and on
    that path an exception is indistinguishable from an estimate that simply has
    nothing to say.

    Strict identity check so a test double or an absent attribute reads as off,
    matching the poll-skip guard and the mixin's own setup.
    """
    return (
        getattr(getattr(store, "config", None), const.CONF_HOURLY_CALCULATION, False)
        is True
    )


def replayed_balance_applies(store, zone) -> bool:
    """Whether a zone's water balance is replayed rather than lumped.

    The one wording of the condition, read by the commit and by the live estimate
    alike. The estimate has to replay wherever the commit does, or it shows a
    curve the stored bucket does not take; asking the same question a second way
    on the estimate's side is how the two would drift apart as either changes.
    Both halves are answered here for that reason -- passing either in as an
    argument would leave that half to be restated per caller.

    Two conditions, for two different reasons:

    * the module has to model precipitation at all -- replaying a window for
      Static or Passthrough would introduce water the shipped model deliberately
      leaves out;
    * ``hourlycalculation`` has to be on. That one is blast radius rather than a
      technical limit: replaying moves the stored bucket on any install that maps
      precipitation, because rain that used to be booked at the window start
      (clamped there, and over-drained for the whole window afterwards) is now
      booked when it fell. A better number, but still a change to what an install
      that opted into nothing sees.

    Reads the STORED module rather than an instance: the estimate asks this every
    minute per zone, and instantiating a module re-scans the calc-module
    directory.
    """
    if not hourly_calculation_enabled(store):
        return False
    module = store.get_module(zone.get(const.ZONE_MODULE))
    return bool(module) and module.get(const.MODULE_NAME) == "PyETO"


class CalculationMixin:
    """Aggregation + ET/bucket calculation for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    async def merge_weatherdata_and_sensor_values(self, wd, sv):
        """Merge weather data and sensor values dictionaries, giving precedence to sensor values.

        Args:
            wd: The weather data dictionary or None.
            sv: The sensor values dictionary or None.

        Returns:
            dict: A merged dictionary with sensor values overriding weather data where keys overlap.

        """
        if wd is None:
            return sv
        if sv is None:
            return wd
        retval = wd
        for key, val in sv.items():
            if key in retval:
                _LOGGER.debug(
                    "merge_weatherdata_and_sensor_values, overriding %s value %s from OWM with %s from sensors",
                    key,
                    retval[key],
                    val,
                )
            else:
                _LOGGER.debug(
                    "merge_weatherdata_and_sensor_values, adding %s value %s from sensors",
                    key,
                    val,
                )
            retval[key] = val

        return retval

    async def _async_clear_all_weatherdata(self, *args):
        """Wipe every mapping's weather buffer and re-anchor zone watermarks.

        The manual "reset all weather data" action. Resetting each zone's
        last_consumed_at to now keeps the per-zone watermarks consistent with the
        now-empty buffer (otherwise a zone would try to consume a window that no
        longer exists).
        """
        _LOGGER.info("Clearing all weatherdata")
        now = datetime.now()
        # The deadband's reference values are not part of the store, so emptying
        # the buffers above does not touch them; left stale they suppress the
        # readings that would refill those buffers. See
        # ContinuousUpdateMixin.clear_continuous_deadband_state.
        self.clear_continuous_deadband_state()
        # The intraday estimate carries completed hours' ETo in memory, keyed on
        # the zone's last_calculated — which this does not move. Without dropping
        # it the live deficit would keep reporting ET computed from readings the
        # user just deleted.
        self.invalidate_live_estimate_carry()
        mappings = await self.store.async_get_mappings()
        for mapping in mappings:
            self.store.set_mapping_buffer(mapping.get(const.MAPPING_ID), [])
            await self.store.async_update_mapping(
                mapping.get(const.MAPPING_ID),
                {
                    # "Reset all weather data" must also drop the continuous-update
                    # carry-forwards, or aggregate_window would keep backfilling
                    # from them and the reset would look like it did nothing. They
                    # are set to None rather than removed because
                    # async_update_mapping merges any omitted key back in, and
                    # aggregate_window skips None values.
                    const.MAPPING_DATA_LAST_ENTRY: dict.fromkeys(
                        mapping.get(const.MAPPING_DATA_LAST_ENTRY) or {}
                    ),
                },
            )
        for zone in await self.store.async_get_zones():
            zone_id = zone.get(const.ZONE_ID)
            await self.store.async_update_zone(
                zone_id,
                {
                    const.ZONE_LAST_CONSUMED: now,
                    # Derived from the buffer we just emptied, so it has to be
                    # reset with it — otherwise the zone's "Weather data points"
                    # sensor keeps reporting the pre-reset count until the next
                    # poll or calculation happens to overwrite it, which reads as
                    # "reset all weather data didn't work".
                    const.ZONE_NUMBER_OF_DATA_POINTS: 0,
                },
            )
            # Writing the store is not enough: the zone sensors hold their values
            # in memory and only re-read on this signal, so without it the entity
            # attribute keeps showing the old count until an unrelated update or a
            # restart. Every other writer of the count already dispatches; this
            # path was the one that did not.
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")

    async def _aggregate_for_zone(self, zone, *, now):
        """Aggregate this zone's window of its mapping's shared buffer.

        Returns ``(weatherdata, n_points)`` where ``n_points`` is the number of
        new readings in the zone's window, or ``(None, 0)`` when there is nothing
        to consume (no mapping/data).
        """
        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is None:
            return None, 0
        mapping = self.store.get_mapping(mapping_id)
        if not mapping:
            return None, 0
        readings = self.store.get_mapping_buffer(mapping_id)
        watermark = _as_datetime(zone.get(const.ZONE_LAST_CONSUMED))
        _, window = select_window(readings, watermark)
        weatherdata = aggregate_window(
            readings,
            watermark,
            mapping.get(const.MAPPING_MAPPINGS) or {},
            now=now,
            # Carry-forward for continuous-update sensor groups: their rows are
            # sparse (one field per event), so a slow-moving field can have no
            # row at all inside this zone's window. Without the fallback the calc
            # module would be handed a missing field and either refuse to
            # calculate or substitute a default — both wrong. Never overrides a
            # field the window does contain (see aggregate_window).
            last_entry=mapping.get(const.MAPPING_DATA_LAST_ENTRY),
            # Time-weighted AVERAGE only for the sparse buffers the event path
            # writes. Strict identity check so a test double or an absent
            # attribute is a safe "off", matching the poll-skip guard and the
            # mixin's own setup.
            time_weighted=(
                getattr(
                    getattr(self.store, "config", None),
                    const.CONF_CONTINUOUS_UPDATES,
                    False,
                )
                is True
            ),
        )
        return weatherdata, len(window)

    async def _prune_mapping_buffer(self, mapping_id, *, now=None):
        """Drop buffer readings no enabled zone needs any more.

        Keeps everything after the oldest enabled-zone watermark (so no zone
        loses unconsumed data) plus, PER FIELD, the boundary reading just before
        it (each field's delta/Riemann baseline), and hard-drops anything older
        than the retention cap. Disabled zones do not hold the buffer.

        The boundary is per field because the event path writes sparse rows —
        one field per event — so a single kept row only preserves the baseline
        of whichever field moved last before the cutoff. Dropping a cumulative
        rain gauge's last pre-cutoff row silently uncounted a gauge rise that
        straddled the calculation. Polled full rows degenerate to the single
        newest row, as before. Bounded by the mapping's field count, so the
        buffer stays capped.
        """
        if mapping_id is None:
            return
        if now is None:
            now = datetime.now()
        mapping = self.store.get_mapping(mapping_id)
        if not mapping:
            return
        readings = self.store.get_mapping_buffer(mapping_id)
        if not readings:
            return

        cap_cutoff = now - BUFFER_RETENTION
        watermarks, any_unconsumed = self.store.get_enabled_zone_watermarks(mapping_id)
        if any_unconsumed or not watermarks:
            cutoff = cap_cutoff
        else:
            cutoff = max(cap_cutoff, min(watermarks))

        kept = []
        boundaries = {}  # field -> (rt, row): latest pre-cutoff row per field
        for r in readings:
            rt = (
                _as_datetime(r.get(const.RETRIEVED_AT)) if isinstance(r, dict) else None
            )
            if rt is None or rt > cutoff:
                kept.append(r)
            else:
                merge_latest_per_field(boundaries, rt, r, keep_row=True)
        # One row can be the boundary of several fields; keep each once, in
        # chronological order ahead of the surviving window.
        boundary_rows = []
        for rt, row in sorted(boundaries.values(), key=lambda p: p[0]):
            if not any(row is seen for _, seen in boundary_rows):
                boundary_rows.append((rt, row))
        kept[:0] = [row for _, row in boundary_rows]
        if len(kept) != len(readings):
            _LOGGER.debug(
                "[_prune_mapping_buffer] mapping %s: %s -> %s readings (cutoff %s)",
                mapping_id,
                len(readings),
                len(kept),
                cutoff,
            )
            self.store.set_mapping_buffer(mapping_id, kept)

    async def _async_calculate_all(self, *args):
        """Calculate every automatic zone, each over its own consumption window.

        Each zone consumes ``(last_consumed_at, now]`` of its mapping's shared
        buffer and advances its own watermark; the buffer is pruned once per
        touched mapping at the end (never cleared wholesale, so zones sharing a
        mapping keep their independent history).
        """
        _LOGGER.info("Calculating all automatic zones")
        zones = await self.store.async_get_zones()

        now = datetime.now()
        forecastdata = None
        touched_mappings = set()
        for zone in zones:
            if zone.get(const.ZONE_STATE) != const.ZONE_STATE_AUTOMATIC:
                continue
            # fetch forecast once if any PyETO-with-forecast zone needs it
            modinst = await self.getModuleInstanceByID(zone.get(const.ZONE_MODULE))
            if modinst and modinst.name == "PyETO" and modinst.forecast_days > 0:
                if self.use_weather_service:
                    if forecastdata is None:
                        forecastdata = await self.hass.async_add_executor_job(
                            self._WeatherServiceClient.get_forecast_data
                        )
                else:
                    _LOGGER.error(
                        "Error calculating zone %s: forecasting configured but no weather service API is set",
                        zone.get(const.ZONE_NAME),
                    )
                    continue
            try:
                await self.async_calculate_zone(
                    zone.get(const.ZONE_ID), forecastdata, now=now, prune=False
                )
            except Exception:  # noqa: BLE001
                # Isolate one zone's calculation failure so it can't abort the daily
                # calc for EVERY other zone (audit #8). The zone keeps its previous
                # duration/bucket; the rest still recompute.
                _LOGGER.exception(
                    "Error calculating zone %s; skipping it and continuing with the "
                    "remaining zones",
                    zone.get(const.ZONE_ID),
                )
                continue
            touched_mappings.add(zone.get(const.ZONE_MAPPING))

        # Prune each touched mapping once all its zones have advanced.
        for mapping_id in touched_mappings:
            await self._prune_mapping_buffer(mapping_id, now=now)

        # Buckets just changed → the cached intraday estimates are stale
        # (they are anchored to last_calculated). Refresh once for everyone.
        await self.async_refresh_zone_estimates()

    async def async_calculate_zone(
        self, zone_id, forecastdata=None, *, now=None, prune=True
    ):
        """Calculate one zone from its own window of the shared mapping buffer.

        The zone consumes ``(last_consumed_at, now]`` of its mapping's readings
        and advances its watermark. The shared buffer is NOT cleared here (other
        zones may still need it) — it is pruned by ``_prune_mapping_buffer``.

        Args:
            zone_id: the zone to calculate.
            forecastdata: optional pre-fetched forecast for PyETO-with-forecast.
            now: shared "now" so the watermark and multiplier agree (calc-all).
            prune: prune the buffer afterwards (False for calc-all, which prunes
                once at the end).
        """
        _LOGGER.debug("async_calculate_zone: Calculating zone %s", zone_id)
        if now is None:
            now = datetime.now()
        zone = self.store.get_zone(zone_id)
        if zone is None:
            return

        # Every run path settles the bucket from an anchor captured before the
        # valve opened, so a calculation landing mid-run is overwritten within a
        # commit interval and that window's ET is lost. Give way and return
        # BEFORE anything is consumed: last_consumed_at is only advanced on the
        # write path below, so the readings stay in the buffer and the deferred
        # calculation (run at the end of the run, see RunStateMixin) folds in the
        # whole window. See tests/test_run_in_flight.py.
        if self.zone_run_in_flight(zone_id):
            self.defer_zone_calculation(zone_id)
            _LOGGER.info(
                "Zone %s is being watered; deferring its calculation until the "
                "run finishes (no weather data is consumed in the meantime)",
                zone_id,
            )
            return

        weatherdata, n_points = await self._aggregate_for_zone(zone, now=now)
        if weatherdata is None:
            _LOGGER.debug(
                "async_calculate_zone: no weather data to consume for zone %s",
                zone_id,
            )
            return

        calc_data = await self.calculate_module(
            zone, weatherdata, forecastdata, now=now
        )
        if calc_data is None:
            _LOGGER.error(
                "async_calculate_zone: calculation returned no result for zone %s "
                "(module missing or not configured?)",
                zone_id,
            )
            return

        calc_data[const.ZONE_LAST_CALCULATED] = now
        calc_data[const.ZONE_LAST_UPDATED] = now
        # Advance this zone's watermark so it never re-consumes this window.
        calc_data[const.ZONE_LAST_CONSUMED] = now
        calc_data[const.ZONE_NUMBER_OF_DATA_POINTS] = n_points

        await self.store.async_update_zone(zone.get(const.ZONE_ID), calc_data)
        if prune:
            await self._prune_mapping_buffer(zone.get(const.ZONE_MAPPING), now=now)
        async_dispatcher_send(
            self.hass,
            const.DOMAIN + "_config_updated",
            zone.get(const.ZONE_ID),
        )
        async_dispatcher_send(self.hass, const.DOMAIN + "_update_frontend")

    def _module_instances(self) -> dict:
        """The resolved calc-module instances by module id, created on first use.

        Lazily built rather than set up in the coordinator's ``__init__`` so a
        partially constructed coordinator (and every test double that never runs
        that constructor) still resolves modules.
        """
        cache = getattr(self, "_module_instance_by_id", None)
        if cache is None:
            cache = self._module_instance_by_id = {}
        return cache

    @callback
    def invalidate_module_instances(self, *args) -> None:
        """Drop cached calc-module instances the stored configuration outran.

        Wired to the existing ``_config_updated`` fan-out, which is what a module
        edit dispatches (``async_update_module_config``). That signal also
        carries every zone and mapping write, so this re-evaluates idempotently
        instead of clearing: comparing each cached snapshot against the store is
        a couple of dict compares, whereas clearing would throw the cache away on
        a signal that fires per zone per ingestion flush and hand back the
        directory scan the cache exists to remove.

        Also collects instances for modules that have since been deleted —
        deletion is the one module write that dispatches nothing of its own.
        """
        cache = getattr(self, "_module_instance_by_id", None)
        if not cache:
            return
        for module_id, (record, _) in list(cache.items()):
            current = self.store.get_module(module_id)
            if current is None or current != record:
                cache.pop(module_id, None)

    async def getModuleInstanceByID(self, module_id):
        """Retrieve and instantiate a module by its ID.

        Resolved once per module and reused. ``loadModules`` re-scans the
        calc-module directory and re-imports every package it finds, over an
        executor hop; that is affordable for a once-a-day calculation but not for
        the live estimate, which resolves a zone's module every minute.

        Args:
            module_id: The ID of the module to retrieve.

        Returns:
            The instantiated module object, or None if not found.

        """
        m = self.store.get_module(module_id)
        if m is None:
            return None
        cache = self._module_instances()
        key = int(module_id)
        cached = cache.get(key)
        # The stored record is compared, not merely trusted to have been
        # invalidated: the dispatcher signal is the release mechanism, but a
        # module whose config changed without one reaching us (a direct store
        # write, a migration rewrite) must still not be served stale.
        if cached is not None and cached[0] == m:
            return cached[1]
        # load the module dynamically
        mods = await self.hass.async_add_executor_job(loadModules, const.MODULE_DIR)
        modinst = None
        for mod in mods:
            if mods[mod]["class"] == m[const.MODULE_NAME]:
                themod = getattr(mods[mod]["module"], mods[mod]["class"])
                modinst = themod(
                    self.hass, description=m["description"], config=m["config"]
                )
                break
        # Honor manually-configured coordinates. Calc modules that derive solar
        # radiation from latitude/elevation (e.g. PyETO) build those from
        # hass.config at construction; override with the integration's effective
        # coordinates so manual coordinates are respected here too — previously
        # they only reached the weather client, not the PyETO solar-radiation math.
        if modinst is not None:
            eff_lat = getattr(self, "_effective_latitude", None)
            eff_elev = getattr(self, "_effective_elevation", None)
            if eff_lat is not None and hasattr(modinst, "_latitude"):
                modinst._latitude = eff_lat
            if eff_elev is not None and hasattr(modinst, "_elevation"):
                modinst._elevation = eff_elev
            # Only a resolved instance is cached; a module name with no matching
            # package on disk must keep re-scanning, since the next scan is what
            # would pick it up after an integration update dropped it in.
            cache[key] = (m, modinst)
        else:
            cache.pop(key, None)
        return modinst

    def _hourly_calculation_enabled(self) -> bool:
        """Whether this install has opted into the hourly form of the calculation.

        The single gate for both halves of the feature, so they cannot drift
        apart: the summed-hourly ET form and the replayed water balance each
        move the numbers an existing install already sees, and neither should
        arrive without the user turning something on.

        Deliberately its OWN switch and not ``continuousupdates``. Reading the
        ingestion flag would have handed a 12%-scale ET change to every install
        that had opted into denser ingestion and nothing else, while withholding
        it from hourly-polled installs, which measure within 8.4% of dense truth
        on this form with no systematic bias. The two axes are independent.
        """
        return hourly_calculation_enabled(self.store)

    def _hourly_et_for_zone(self, zone, modinst, *, now):
        """Summed FAO-56 hourly ETo over this zone's window, or None to use the daily form.

        The daily FAO-56 equation run on window-mean weather is systematically
        biased by cloudiness: fed one identical Open-Meteo hourly series over 362
        days it runs 1.144x the reference on overcast days and 0.925x on clear
        ones, while the same series summed hour by hour sits flat at 1.02-1.04
        across every sky band (mean absolute daily error 0.099 mm against
        0.254 mm). The bias is in the aggregation, not the sensors, so summing
        hourly removes it.

        Returns ``(total_mm, {hour_start: mm})`` — the second so the water-balance
        sub-steps can charge each hour its own ET rather than shaping one daily
        number. Returns None whenever the hourly form cannot be applied honestly:

        * ``hourlycalculation`` is off. This one is a blast-radius decision
          rather than a technical limit: the hourly form moves the daily number
          by up to 12% structured by cloudiness, and an install that has opted
          into nothing should not have its watering change under it. It is NOT
          gated on ingestion density -- measured against dense truth on real
          recorded days, an hourly-polled install runs this form within 8.4% and
          with no systematic bias, so a poll-only install may turn it on;
        * the module estimates solar radiation rather than measuring it, so the
          measured series is not what it would have used;
        * forecast days are configured, which averages today with days that have
          no hourly series at all;
        * the site has no coordinates;
        * the window cannot be reduced to hourly rows (see build_hourly_rows).

        In every case the caller keeps the daily path, so the fallback is today's
        behaviour rather than a fabricated series.
        """
        if not self._hourly_calculation_enabled():
            return None
        if str(getattr(modinst, "_solrad_behavior", "")) != str(
            SOLRAD_behavior.DontEstimate.value
        ):
            return None
        if getattr(modinst, "forecast_days", 0):
            return None
        latitude = getattr(self, "_effective_latitude", None)
        longitude = getattr(self, "_effective_longitude", None)
        if latitude is None or longitude is None:
            return None
        elevation = getattr(self, "_effective_elevation", None) or 0

        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is None:
            return None
        mapping = self.store.get_mapping(mapping_id)
        if not isinstance(mapping, dict):
            return None
        readings = self.store.get_mapping_buffer(mapping_id)
        mappings_config = mapping.get(const.MAPPING_MAPPINGS)
        if not isinstance(readings, list) or not isinstance(mappings_config, dict):
            return None

        # Buffer stamps are naive LOCAL times, so the solar-time correction wants
        # the local UTC offset. The site timezone is passed alongside so each row
        # resolves the offset from its OWN stamp: a window reaches seven days and
        # can straddle a DST transition, and one offset for the whole window puts
        # the rows past it an hour out in solar time. That is only 0.26-0.74% on
        # daily ETo, but +23.5% / -16.0% on the radiation the clearness-ratio
        # hold refills, where Rso is a denominator. The scalar remains the
        # fallback for rows that carry no offset of their own.
        tz = dt_util.DEFAULT_TIME_ZONE
        offset = dt_util.now().utcoffset()
        tz_offset_h = offset.total_seconds() / 3600.0 if offset else 0.0

        priced = hourly_eto_priced(
            readings,
            _as_datetime(zone.get(const.ZONE_LAST_CONSUMED)),
            mappings_config,
            now=now,
            last_entry=mapping.get(const.MAPPING_DATA_LAST_ENTRY),
            # An hour that saw no solar reading is refilled from the held
            # clearness ratio rather than the last absolute value, which needs
            # the site's own solar geometry.
            geometry=SiteGeometry(latitude, longitude, elevation, tz_offset_h, tz),
        )
        if priced is None:
            return None
        rows, series = priced

        per_hour = {}
        for row, eto in zip(rows, series, strict=True):
            per_hour[row["hour_start"]] = per_hour.get(row["hour_start"], 0.0) + eto
        total = sum(series)
        _LOGGER.debug(
            "[calculate-module]: summed hourly ETo for zone %s: %s mm over %s hours",
            zone.get(const.ZONE_ID),
            total,
            len(rows),
        )
        return total, per_hour

    def _substeps_for_zone(
        self, zone, precip_total, *, now, hourly_et=None, applied=None
    ):
        """Water-balance sub-steps for this zone's window, or None to lump.

        Reconciled against the aggregate's precipitation total before being
        trusted. ZONE_DELTA is published from the aggregate while the bucket is
        driven by these increments, so the two have to be the same water; they
        are derived from the same rows by the same rule, and a disagreement means
        an assumption has broken. Falling back then costs the sub-stepping but
        keeps the ledger self-consistent, which is the more important property.

        Gated by ``replayed_balance_applies``, which is also what the live
        estimate reads: the estimate exists to show the path this bucket takes,
        so the two have to replay for exactly the same zones. Answering that
        question here rather than at the call site is what lets the estimate ask
        it of a zone without reproducing the conditions.
        """
        if not replayed_balance_applies(self.store, zone):
            return None
        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is None:
            return None
        mapping = self.store.get_mapping(mapping_id)
        if not isinstance(mapping, dict):
            return None
        readings = self.store.get_mapping_buffer(mapping_id)
        mappings_config = mapping.get(const.MAPPING_MAPPINGS)
        if not isinstance(readings, list) or not isinstance(mappings_config, dict):
            return None
        steps = build_substeps(
            readings,
            _as_datetime(zone.get(const.ZONE_LAST_CONSUMED)),
            mappings_config,
            now=now,
            hourly_et=hourly_et,
            applied=applied,
        )
        if not steps:
            return None
        stepped = sum(s.precip_mm for s in steps)
        if abs(stepped - precip_total) > max(1e-6, abs(precip_total) * 1e-6):
            _LOGGER.debug(
                "[calculate-module]: sub-step precipitation %s does not reconcile "
                "with the aggregated %s for zone %s; using the single-shot balance",
                stepped,
                precip_total,
                zone.get(const.ZONE_ID),
            )
            return None
        return steps

    async def calculate_module(self, zone, weatherdata, forecastdata, *, now=None):
        """Calculate irrigation values for a zone using the specified weather and forecast data.

        Args:
            zone: The zone dictionary containing configuration and state.
            weatherdata: Aggregated weather data for the calculation.
            forecastdata: Forecast data if required by the module.

        Returns:
            dict: Updated zone data including calculation results and explanation.

        """
        _LOGGER.debug("calculate_module for zone: %s", zone)
        # _LOGGER.debug("[calculate_module] for zone: %s, weatherdata: %s, forecastdata: %s", zone, weatherdata, forecastdata)
        mod_id = zone.get(const.ZONE_MODULE)
        m = self.store.get_module(mod_id)
        if m is None:
            return None
        modinst = await self.getModuleInstanceByID(mod_id)
        if not modinst:
            _LOGGER.error("Unknown module for zone %s", zone.get(const.ZONE_NAME))
            return None
        # Resolved ONCE. The hourly ETo rows and the water-balance sub-steps are
        # two reductions of the same window that have to agree on where the hour
        # boundaries fall, so reading the clock separately for each would let a
        # window end land in different hours and silently drop the calculation
        # back to the single-shot path.
        if now is None:
            now = datetime.now()
        # precip = 0
        ha_config_is_metric = self.hass.config.units is METRIC_SYSTEM
        bucket = zone.get(const.ZONE_BUCKET)
        maximum_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
        if not ha_config_is_metric:
            bucket = convert_between(const.UNIT_INCH, const.UNIT_MM, bucket)
            if zone.get(const.ZONE_MAXIMUM_BUCKET) is not None:
                maximum_bucket = convert_between(
                    const.UNIT_INCH, const.UNIT_MM, zone.get(const.ZONE_MAXIMUM_BUCKET)
                )
        data = {}
        old_bucket = bucket
        explanation = ""

        precip = 0
        # Only PyETO folds precipitation into the deficit, and it is the only
        # module the summed-hourly form of the equation exists for.
        module_uses_precipitation = m[const.MODULE_NAME] == "PyETO"
        # Resolved BEFORE the daily equation runs, so that equation is skipped
        # entirely when its answer would be discarded. It is not just wasted work:
        # PyETO clamps the window's mean radiation against a DAILY clear-sky
        # maximum, and a window that is all daylight legitimately exceeds that, so
        # it would warn the user to check a sensor whose reading the calculation
        # never used. A clamp warning has to mean something.
        hourly = (
            self._hourly_et_for_zone(zone, modinst, now=now)
            if module_uses_precipitation
            else None
        )
        delta = 0.0
        if m[const.MODULE_NAME] == "PyETO":
            if hourly is None:
                # pyeto expects pressure in hpa, solar radiation in mj/m2/day and wind speed in m/s
                delta = modinst.calculate(
                    weather_data=weatherdata, forecast_data=forecastdata
                )
            # only PyETO uses precipitation
            precip = weatherdata.get(const.MAPPING_PRECIPITATION, 0)
            _LOGGER.debug("[calculate-module]: precip: %s", precip)
        elif m[const.MODULE_NAME] == "Static":
            delta = modinst.calculate()
        elif m[const.MODULE_NAME] == "Passthrough":
            if const.MAPPING_EVAPOTRANSPIRATION in weatherdata:
                delta = 0 - modinst.calculate(
                    et_data=weatherdata[const.MAPPING_EVAPOTRANSPIRATION]
                )
            else:
                _LOGGER.error(
                    "No evapotranspiration value provided for Passthrough module for zone %s",
                    zone.get(const.ZONE_NAME),
                )
                return None
        # Scale module ET value by interval (hour_multiplier = fractional days)
        _LOGGER.debug("[calculate-module]: retrieved from module: %s", delta)
        # Crop coefficient (WS-4): scale the ET0 (reference-grass) term ONLY by the
        # zone's Kc — real plants use a fraction/multiple of reference ET. Precip is
        # NOT scaled. Default Kc 1.0 ⇒ behaviour identical to reference ET.
        kc = zone.get(const.ZONE_KC, const.CONF_DEFAULT_KC)
        if kc is None:
            kc = const.CONF_DEFAULT_KC
        hour_multiplier = weatherdata.get(const.MAPPING_DATA_MULTIPLIER, 1.0)
        _LOGGER.debug("[calculate-module]: hour_multiplier: %s", hour_multiplier)
        hourly_et = None
        if hourly is not None:
            hourly_total, hourly_et = hourly
            # hour_multiplier scales a DAILY et0 by the window's fraction of a
            # day. Summing hourly ETo has already integrated over the window, so
            # applying it here as well would scale the same window twice. It is
            # still needed for elapsed_hours below, which is a drainage duration
            # rather than an ET scale.
            et_term = -hourly_total
            et_delta = et_term * kc
        else:
            et_term = delta
            et_delta = delta * kc * hour_multiplier
        delta = et_delta + precip
        data[const.ZONE_DELTA] = delta
        _LOGGER.debug("[calculate-module]: new delta: %s", delta)

        # take drainage rate into account
        drainage_rate = zone.get(const.ZONE_DRAINAGE_RATE, 0.0)
        if drainage_rate is None:
            drainage_rate = 0.0
        if not ha_config_is_metric:
            # drainage_rate is in inch/h since HA is not in metric, so we need to adjust those first!
            # using inch and mm here since both are per hour
            drainage_rate = convert_between(
                const.UNIT_INCH, const.UNIT_MM, drainage_rate
            )
        _LOGGER.debug("[calculate-module]: drainage_rate: %s", drainage_rate)
        elapsed_hours = hour_multiplier * 24
        # A maximum bucket of 0 still clamps, but there is no field capacity to
        # scale Brooks-Corey against, so drainage falls back to a constant rate.
        drain_maximum = (
            maximum_bucket if maximum_bucket and maximum_bucket > 0 else None
        )

        # The single-shot form of what follows lands the window's whole
        # precipitation at the window START, clamps it against maximum_bucket
        # there, and drains whatever survives for the entire window. Both errors
        # run one way: late rain is over-drained and spread-out rain is
        # over-clamped, because the drainage that would have made room between
        # bursts never happens. Replaying the window at its own event times
        # removes both without changing the ledger — still one calculation, one
        # bucket write, one delta, one explanation. See ``build_substeps``.
        #
        # Irrigation credited part-way through this window. The stored bucket
        # already holds it, so the replay starts from the level BEFORE it and the
        # credit goes back in at the step it happened on. Without that it is
        # charged the whole window's drainage — up to ~2.5 mm of bucket on a run
        # that overshoots into surplus, always reading the zone drier than it is,
        # and it does not wash out: once the zone is back in deficit drainage
        # stops acting and the gap is frozen in.
        applied = pending_bucket_events(zone)
        steps = self._substeps_for_zone(
            zone, precip, now=now, hourly_et=hourly_et, applied=applied
        )
        # Consumed whether or not the replay ran: the single-shot path cannot
        # place them, and carrying them into a later window would put them
        # further from where they belong, not closer.
        data[const.ZONE_PENDING_BUCKET_EVENTS] = []
        runoff = 0.0
        # Kept for the explanation in both paths: it is the number the reader
        # recognises as "bucket plus delta, capped", and it is what selects the
        # no-drainage wording.
        bucket_plus_delta_capped = bucket + delta
        if maximum_bucket is not None and bucket_plus_delta_capped > maximum_bucket:
            bucket_plus_delta_capped = float(maximum_bucket)
        if steps is not None:
            applied_total = sum(s.applied_mm for s in steps)
            newbucket, drainage, runoff = replay_water_balance(
                bucket - applied_total,
                et_delta,
                steps,
                drainage_rate,
                maximum_bucket,
                drain_maximum,
            )
            _LOGGER.debug(
                "[calculate-module]: sub-stepped water balance over %s steps: "
                "drainage %s, runoff %s, irrigation replayed %s mm",
                len(steps),
                drainage,
                runoff,
                applied_total,
            )
        else:
            newbucket = bucket_plus_delta_capped
            # Drainage only acts on water above field capacity (surplus > 0) and
            # is integrated analytically over the elapsed window (see
            # ``drained_over_window``). This replaces the previous single
            # explicit-Euler step, which over-drained because the rate was sampled
            # once at the end-of-window surplus and charged for the whole window.
            drainage = drained_over_window(
                bucket_plus_delta_capped,
                drainage_rate,
                elapsed_hours,
                drain_maximum,
            )
            newbucket = bucket_plus_delta_capped - drainage
        _LOGGER.debug("[calculate-module]: current_drainage: %s", drainage)

        data[const.ZONE_CURRENT_DRAINAGE] = drainage
        _LOGGER.debug("[calculate-module]: newbucket: %s", newbucket)

        # Experimental forecast weighting: when rain is forecast, water LESS by
        # folding the look-ahead precipitation into the deficit used for the
        # *duration* — but keep the true deficit in the bucket so the real rain
        # fills the rest (folding it into the bucket itself would double-count
        # the forecasted rain once it is actually collected). ``effective_bucket``
        # drives the duration; ``newbucket`` (unchanged) stays the persisted
        # bucket. ``irrigation_target_bucket`` carries the leftover deficit for
        # the runner so a completed run leaves the zone at that level, not 0.
        effective_bucket = newbucket
        if (
            newbucket < 0
            and getattr(self, "use_weather_service", False)
            and self.store.config.forecast_weighting_enabled
        ):
            fd = forecastdata
            if fd is None and self._WeatherServiceClient is not None:
                fd = await self.hass.async_add_executor_job(
                    self._WeatherServiceClient.get_forecast_data
                )
            if fd:
                config = await self.store.async_get_config()
                days = max(
                    1,
                    config.get(
                        const.CONF_PRECIPITATION_FORECAST_DAYS,
                        const.CONF_DEFAULT_PRECIPITATION_FORECAST_DAYS,
                    ),
                )
                forecast_precip = sum(
                    day_data.get(const.MAPPING_PRECIPITATION, 0.0)
                    for day_data in fd[:days]
                )
                if forecast_precip > 0:
                    effective_bucket = min(0.0, newbucket + forecast_precip)
                    _LOGGER.debug(
                        "[calculate-module]: forecast weighting %.2f mm rain → "
                        "effective bucket %.2f (true %.2f)",
                        forecast_precip,
                        effective_bucket,
                        newbucket,
                    )

        explanation = (
            await localize(
                # Which ET form produced this number. The two differ by up to
                # ~12% on identical inputs, so a day that switches forms shows a
                # step in the ET series that is otherwise unexplainable.
                (
                    "module.calculation.explanation.module-returned-evapotranspiration-deficiency-hourly"
                    if hourly is not None
                    else "module.calculation.explanation.module-returned-evapotranspiration-deficiency"
                ),
                self.hass.config.language,
            )
            + f" {data[const.ZONE_DELTA]:.2f}."
        )
        # Surface the crop-coefficient scaling when a non-default Kc is in effect.
        if kc != const.CONF_DEFAULT_KC:
            explanation += (
                " "
                + await localize(
                    "module.calculation.explanation.crop-coefficient-applied",
                    self.hass.config.language,
                )
                + f" (Kc {kc:.2f} &times; {et_term:.2f})."
            )
        explanation += (
            await localize(
                "module.calculation.explanation.bucket-was", self.hass.config.language
            )
            + f" {old_bucket:.2f}"
        )
        explanation += (
            ".<br/>"
            + await localize(
                "module.calculation.explanation.maximum-bucket-is",
                self.hass.config.language,
            )
            # maximum_bucket is legitimately None ("no ceiling") if the user cleared
            # the field (guarded everywhere else, e.g. line ~613), so float(None) here
            # would raise TypeError and abort this zone's calc — render a dash instead.
            + (f" {float(maximum_bucket):.1f}" if maximum_bucket is not None else " -")
        )
        explanation += (
            ".<br/>"
            + await localize(
                "module.calculation.explanation.drainage-rate-is",
                self.hass.config.language,
            )
            + f" {float(drainage_rate):.1f}.<br/>"
        )

        # Define some localized strings here for cleaner code below
        hours_loc = await localize(
            "module.calculation.explanation.hours", self.hass.config.language
        )
        drainage_loc = await localize(
            "module.calculation.explanation.drainage", self.hass.config.language
        )
        drainage_rate_loc = await localize(
            "module.calculation.explanation.drainage-rate", self.hass.config.language
        )
        delta_loc = await localize(
            "module.calculation.explanation.delta", self.hass.config.language
        )
        old_bucket_loc = await localize(
            "module.calculation.explanation.old-bucket-variable",
            self.hass.config.language,
        )
        max_bucket_loc = await localize(
            "module.calculation.explanation.max-bucket-variable",
            self.hass.config.language,
        )

        if steps is not None:
            # The single-shot formulas below would not add up here: the balance
            # was replayed, so rain, drainage and the clamp were applied at the
            # times they happened. Report what the replay actually did instead.
            runoff_loc = await localize(
                "module.calculation.explanation.runoff-variable",
                self.hass.config.language,
            )
            explanation += (
                await localize(
                    "module.calculation.explanation.water-balance-substepped",
                    self.hass.config.language,
                )
                + f" {len(steps)}.<br/>"
                + await localize(
                    "module.calculation.explanation.current-drainage-is",
                    self.hass.config.language,
                )
                + f" {drainage:.2f}"
            )
            if runoff > 0:
                explanation += (
                    ".<br/>"
                    + await localize(
                        "module.calculation.explanation.runoff-is",
                        self.hass.config.language,
                    )
                    + f" {runoff:.2f}"
                )
        elif bucket_plus_delta_capped <= 0:
            explanation += (
                await localize(
                    "module.calculation.explanation.no-drainage",
                    self.hass.config.language,
                )
                + f" [{old_bucket_loc}] + [{delta_loc}] <= 0 ({old_bucket:.2f}{data[const.ZONE_DELTA]:+.2f} = {bucket_plus_delta_capped:.2f})"
            )
        else:
            explanation += await localize(
                "module.calculation.explanation.current-drainage-is",
                self.hass.config.language,
            )
            if maximum_bucket is None or maximum_bucket <= 0:
                # constant-rate drainage, capped at the available surplus
                explanation += f" min([{old_bucket_loc}] + [{delta_loc}], [{drainage_rate_loc}] * [{hours_loc}]) = min({bucket_plus_delta_capped:.2f}, {drainage_rate:.1f} * {elapsed_hours:.2f}) = {drainage:.2f}"
            else:
                # closed-form Brooks-Corey decay integrated over the window;
                # report the surplus before/after and the water actually drained
                explanation += await localize(
                    "module.calculation.explanation.drainage-integrated",
                    self.hass.config.language,
                )
                explanation += f" ([{drainage_rate_loc}] * (W/[{max_bucket_loc}])^4, {elapsed_hours:.2f} [{hours_loc}]): W = {bucket_plus_delta_capped:.2f} &rarr; {newbucket:.2f}, [{drainage_loc}] = {drainage:.2f}"
        explanation += ".<br/>" + await localize(
            "module.calculation.explanation.new-bucket-values-is",
            self.hass.config.language,
        )

        if steps is not None:
            # Water in minus water out, and it balances exactly: every sub-step
            # adds its ET share and its rain and removes its drainage and its
            # runoff, so the totals telescope back to this one line.
            explanation += (
                f" [{old_bucket_loc}] + [{delta_loc}] - [{drainage_loc}]"
                f" - [{runoff_loc}] = {old_bucket:.2f}{data[const.ZONE_DELTA]:+.2f}"
                f" - {drainage:.2f} - {runoff:.2f} = {newbucket:.2f}.<br/>"
            )
        elif maximum_bucket is not None and maximum_bucket > 0:
            explanation += f" min([{old_bucket_loc}] + [{delta_loc}], {max_bucket_loc}) - [{drainage_loc}] = min({old_bucket:.2f}{data[const.ZONE_DELTA]:+.2f}, {maximum_bucket:.1f}) - {drainage:.2f} = {newbucket:.2f}.<br/>"
        else:
            explanation += f" [{old_bucket_loc}] + [{delta_loc}] - [{drainage_loc}] = {old_bucket:.2f} + {data[const.ZONE_DELTA]:.2f} - {drainage:.2f} = {newbucket:.2f}.<br/>"

        if effective_bucket < 0:
            # calculate duration (from the effective deficit — equal to the true
            # bucket unless forecast weighting trimmed it for expected rain)

            tput = zone.get(const.ZONE_THROUGHPUT)
            sz = zone.get(const.ZONE_SIZE)
            if not tput or not sz:
                # Guard a misconfigured zone (size or throughput 0/unset): there is no
                # valid precipitation rate, so no duration. Without this the
                # (tput * 60) / sz below raises ZeroDivisionError (or TypeError on None)
                # and — because the calc-all loop had no per-zone guard — aborted the
                # calculation for every LATER zone too. Mirrors duration_from_deficit.
                precipitation_rate = 0.0
                duration = 0.0
                tput = tput or 0
                sz = sz or 0
            else:
                if not ha_config_is_metric:
                    # throughput is in gpm and size is in sq ft since HA is not in metric, so we need to adjust those first!
                    tput = convert_between(const.UNIT_GPM, const.UNIT_LPM, tput)
                    sz = convert_between(const.UNIT_SQ_FT, const.UNIT_M2, sz)
                precipitation_rate = (tput * 60) / sz
                duration = abs(effective_bucket) / precipitation_rate * 3600
            if effective_bucket != newbucket:
                explanation += (
                    await localize(
                        "module.calculation.explanation.forecast-weighting-applied",
                        self.hass.config.language,
                    )
                    + f" ({newbucket:.2f} &rarr; {effective_bucket:.2f}).<br/>"
                )
            explanation += (
                await localize(
                    "module.calculation.explanation.bucket-less-than-zero-irrigation-necessary",
                    self.hass.config.language,
                )
                + ".<br/>"
                + await localize(
                    "module.calculation.explanation.steps-taken-to-calculate-duration",
                    self.hass.config.language,
                )
                + ":<br/>"
            )
            explanation += (
                "<ol><li>"
                + await localize(
                    "module.calculation.explanation.precipitation-rate-defined-as",
                    self.hass.config.language,
                )
                + " ["
                + await localize(
                    "common.attributes.throughput", self.hass.config.language
                )
                + "] * 60 / ["
                + await localize("common.attributes.size", self.hass.config.language)
                + f"] = {tput:.1f} * 60 / {sz:.1f} = {precipitation_rate:.1f}.</li>"
            )
            explanation += (
                "<li>"
                + await localize(
                    "module.calculation.explanation.duration-is-calculated-as",
                    self.hass.config.language,
                )
                + " abs(["
                + await localize(
                    "module.calculation.explanation.bucket", self.hass.config.language
                )
                + "]) / ["
                + await localize(
                    "module.calculation.explanation.precipitation-rate-variable",
                    self.hass.config.language,
                )
                + f"] * 3600 = {abs(effective_bucket):.2f} / {precipitation_rate:.1f} * 3600 = {duration:.0f}.</li>"
            )
            duration = zone.get(const.ZONE_MULTIPLIER) * duration
            explanation += (
                "<li>"
                + await localize(
                    "module.calculation.explanation.multiplier-is-applied",
                    self.hass.config.language,
                )
                + f" {zone.get(const.ZONE_MULTIPLIER)}, "
            )
            explanation += (
                await localize(
                    "module.calculation.explanation.duration-after-multiplier-is",
                    self.hass.config.language,
                )
                + f" {round(duration)}.</li>"
            )

            # get maximum duration if set and >=0 and override duration if it's higher than maximum duration
            explanation += (
                "<li>"
                + await localize(
                    "module.calculation.explanation.maximum-duration-is-applied",
                    self.hass.config.language,
                )
                + f" {zone.get(const.ZONE_MAXIMUM_DURATION):.0f}"
            )
            if (
                zone.get(const.ZONE_MAXIMUM_DURATION) is not None
                and zone.get(const.ZONE_MAXIMUM_DURATION) >= 0
                and duration > zone.get(const.ZONE_MAXIMUM_DURATION)
            ):
                # The clamp emits nothing on its own: the shortfall is simply
                # never watered, so deepening bucket_threshold past what the cap
                # can deliver is silently ignored and the zone drifts drier
                # every cycle. The explanation below says so, but nobody reads a
                # zone's explanation until something is already wrong.
                self._warn_duration_clamped(
                    zone, zone.get(const.ZONE_MAXIMUM_DURATION), duration
                )
                duration = zone.get(const.ZONE_MAXIMUM_DURATION)
                explanation += (
                    ", "
                    + await localize(
                        "module.calculation.explanation.duration-after-maximum-duration-is",
                        self.hass.config.language,
                    )
                    + f" {duration:.0f}"
                )
            explanation += ".</li>"

            # add the lead time but only if duration is > 0 at this point
            if duration > 0.0:
                duration = round(zone.get(const.ZONE_LEAD_TIME) + duration)
                explanation += (
                    "<li>"
                    + await localize(
                        "module.calculation.explanation.lead-time-is-applied",
                        self.hass.config.language,
                    )
                    + f" {zone.get(const.ZONE_LEAD_TIME)}, "
                )
                explanation += (
                    await localize(
                        "module.calculation.explanation.duration-after-lead-time-is",
                        self.hass.config.language,
                    )
                    + f" {duration}</li></ol>"
                )
                explanation += (
                    await localize(
                        "module.calculation.explanation.duration-after-lead-time-is",
                        self.hass.config.language,
                    )
                    + f" {duration}.</li></ol>"
                )

                # _LOGGER.debug("[calculate-module]: explanation: %s", explanation)
        else:
            # no need to irrigate, set duration to 0
            duration = 0
            explanation += (
                await localize(
                    "module.calculation.explanation.bucket-larger-than-or-equal-to-zero-no-irrigation-necessary",
                    self.hass.config.language,
                )
                + f" {duration}"
            )

        data[const.ZONE_BUCKET] = newbucket
        # Leftover deficit a completed run should stop at: 0.0 normally (run
        # replenishes the full deficit), or the rain-covered remainder when
        # forecast weighting trimmed this run. Stored in display units like the
        # bucket so the runner can apply it directly. No irrigation ⇒ no target.
        target_bucket = (newbucket - effective_bucket) if duration else 0.0
        data[const.ZONE_IRRIGATION_TARGET_BUCKET] = target_bucket
        if not ha_config_is_metric:
            data[const.ZONE_BUCKET] = convert_between(
                const.UNIT_MM, const.UNIT_INCH, data[const.ZONE_BUCKET]
            )
            data[const.ZONE_IRRIGATION_TARGET_BUCKET] = convert_between(
                const.UNIT_MM, const.UNIT_INCH, target_bucket
            )
        data[const.ZONE_DURATION] = duration
        data[const.ZONE_EXPLANATION] = explanation
        return data
