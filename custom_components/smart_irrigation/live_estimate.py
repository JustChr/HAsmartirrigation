"""Intra-day "live status" estimate orchestration.

Read-only: estimates how much each zone's bucket has drifted *since its last
calculation*. Three sources, in decreasing order of agreement with the stored
ledger:

* **the zone's own sensor-group buffer** — the same rows the daily calculation
  reduces, summed as FAO-56 hourly ETo by the same row builder and run through
  the same replayed water balance, so the live curve is the path the stored
  bucket takes and the two coincide at every calculation time;
* **the weather client's hourly series**, where one exposes solar radiation;
* a **Hargreaves-seeded proxy** distributed over the elapsed hours, for
  providers with neither.

Does NOT touch the stored bucket, the daily calculation, or irrigation — with
one exception the user opts into: with ``live_estimate_enabled`` on, the deficit
computed here both triggers and sizes runs (see ``irrigation.py``), which is why
the buffer path is gated to the configurations where it agrees with the daily
form rather than offered everywhere.

Window correctness: ONE anchor for ET and precipitation alike -- the zone's
``last_calculated``, floored at its consume watermark -- and NOT local midnight.
The daily calculation already folds today's ET into the bucket, so a
since-midnight window would double-count it once that calc has run; and two
different anchors for the two halves of the same balance is upstream issue #38,
where precipitation was aggregated from a window the ET was not.
"""

import datetime
import logging
import time
from typing import NamedTuple

import homeassistant.util.dt as dt_util
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .calcmodules.pyeto import SOLRAD_behavior
from .calculation import pending_bucket_events
from .et_estimate import (
    SiteGeometry,
    estimate_daily_et0_hargreaves,
    hourly_eto_priced,
    live_balance,
    proxy_et_since,
    replay_water_balance,
    rigorous_et_since,
)
from .helpers import convert_between
from .weather_aggregate import aggregate_window, build_substeps

_LOGGER = logging.getLogger(__name__)

# Floor on how often the event-driven ingestion path may refresh the estimates.
# The readings arrive per sensor change, which on this install is a burst every
# few seconds; the estimate is a minute-resolution quantity (ETo is defined on
# the hour) and every refresh writes an entity state, so a shorter floor buys
# nothing and costs recorder rows.
LIVE_ESTIMATE_MIN_REFRESH_SECONDS = 60


class _HourlyCarry(NamedTuple):
    """ETo already accumulated for a zone, up to a whole-hour boundary.

    A completed hour's ETo never changes once the hour closes, so only the
    current partial hour has to be re-reduced on a refresh — ~60 rows instead of
    the whole since-``last_calculated`` window. Purely in memory: losing it to a
    restart costs one full recomputation, not data, which is what makes it a
    different proposition from the persisted running state the daily path
    rejected.

    ``anchor`` is the ``last_calculated`` the total is measured FROM: a new
    calculation moves it, and the mismatch drops the entry without anyone having
    to remember to invalidate it.

    Carried per HOUR rather than as one running total, because the replayed
    balance needs an ET quantum for every hour of the window and the re-reduction
    only ever returns the hours from ``boundary`` on. A bare total would leave
    every earlier hour missing from ``build_substeps``' ``hourly_et``, which is a
    documented reason for it to refuse the window — so the estimate would fall
    back to the lumped form for as long as the carry was warm, i.e. always.
    """

    anchor: datetime.datetime
    boundary: datetime.datetime
    per_hour: dict


def _parse_local_naive(value):
    """Parse a stored last_calculated/last_updated to a NAIVE LOCAL datetime.

    The store writes these as naive *local* datetimes (``datetime.now()`` in
    ``calculation.py``); an aware value (shouldn't occur for these fields) is
    converted to local. Mirrors ``sensor._to_aware_datetime``'s convention
    (naive == local). Reading them as UTC shifts the intra-day window by the
    local UTC offset — on the proxy path that pushes the anchor onto the next
    calendar day, so a whole day's ET is spuriously subtracted right after the
    daily calc (until the next weather update "heals" it).
    """
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except ValueError:
            return None
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None:
            return dt_util.as_local(value).replace(tzinfo=None)
        return value
    return None


class LiveEstimateMixin:
    """Per-zone intra-day ET estimate for the dashboard (read-only)."""

    async def _fetch_intraday_inputs(self):
        """Fetch the shared hourly (and forecast) inputs once for all zones.

        Always returns a dict, ``client`` possibly None: a sensor-only install
        has no weather client at all, and returning None here is precisely what
        made the whole feature inert on one — ``async_get_zone_estimates`` gave
        up before ever looking at the buffer that does hold the readings.
        """
        now = dt_util.now()
        offset = now.utcoffset()
        inputs = {
            "client": None,
            "rows": None,
            "tz": None,
            "forecast": None,
            # Resolved ONCE for the whole refresh. Every zone's window end, hour
            # boundary and carry-forward boundary have to agree, and re-reading
            # the clock per zone lets one zone's partial hour close while the
            # next zone's has not.
            "now": now.replace(tzinfo=None),
            "tz_offset_h": offset.total_seconds() / 3600.0 if offset else 0.0,
            # Carried alongside the offset it was measured from, so the hourly
            # rows can resolve a per-row offset across a DST transition without
            # a second, unrelated timezone overriding the scalar above.
            "site_tz": dt_util.DEFAULT_TIME_ZONE,
        }
        client = getattr(self, "_WeatherServiceClient", None)
        if client is None:
            return inputs
        inputs["client"] = client
        rows = tz = None
        if hasattr(client, "get_hourly_data"):
            try:
                rows, tz = await self.hass.async_add_executor_job(
                    client.get_hourly_data
                )
            except Exception as e:  # noqa: BLE001 — estimate must never raise
                _LOGGER.debug("intraday: get_hourly_data failed: %s", e)
        forecast = None
        if not rows:
            try:
                forecast = await self.hass.async_add_executor_job(
                    client.get_forecast_data
                )
            except Exception as e:  # noqa: BLE001
                _LOGGER.debug("intraday: get_forecast_data failed: %s", e)
        inputs["rows"] = rows
        inputs["tz"] = tz
        inputs["forecast"] = forecast
        return inputs

    def _observed_precip_since_mm(self, zone, anchor):
        """Observed precipitation (mm) collected for the zone's sensor group
        since ``anchor`` (its last calculation).

        Delegates to the same ``aggregate_window`` the daily calc uses, so
        precipitation is aggregated correctly per source: weather-service precip
        is a rate (mm/h) integrated by RIEMANN sum (time-weighted), and a
        cumulative rain-gauge sensor is summed by DELTA. A plain sum would
        over-count sub-hourly rate readings. Read-only — never advances the
        consume watermark. Includes snow as water-equivalent.

        The anchor is the caller's, and every caller passes the one the ET is
        measured from: aggregating the rain half over a different window makes
        the deficit the difference of two windows, which is upstream issue #38.
        The candidates are equal on a healthy install — the daily calc writes
        both watermarks from one ``now`` — which is exactly why a divergence
        only shows up after a weather-data reset or a source change and then
        looks like anything but a window bug.
        """
        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is None:
            return 0.0
        mapping = self.store.get_mapping(mapping_id)
        if not mapping:
            return 0.0
        readings = self.store.get_mapping_buffer(mapping_id)
        if not readings:
            return 0.0
        agg = aggregate_window(
            readings,
            anchor,
            mapping.get(const.MAPPING_MAPPINGS) or {},
            # Same carry-forward the daily calc uses, so the live estimate and the
            # daily calculation aggregate the identical window — a difference here
            # would show up as the "Live bucket" sensor disagreeing with the
            # bucket the nightly calc produces.
            last_entry=mapping.get(const.MAPPING_DATA_LAST_ENTRY),
            # Must match _aggregate_for_zone exactly: a different aggregation
            # here would show up as the "Live bucket" sensor disagreeing with
            # the bucket the nightly calc produces.
            time_weighted=(
                getattr(
                    getattr(self.store, "config", None),
                    const.CONF_CONTINUOUS_UPDATES,
                    False,
                )
                is True
            ),
        )
        if not agg:
            return 0.0
        return agg.get(const.MAPPING_PRECIPITATION, 0.0) or 0.0

    def _hourly_form_applies(self, zone) -> bool:
        """Whether this zone's DAILY calculation sums hourly ETo (axis A).

        The buffer estimate is only offered where the answer is yes, because the
        two forms of the FAO-56 equation disagree by up to 12% structured by sky
        condition — the daily form runs 1.144x reference on overcast days and
        0.925x on clear ones. Showing an hourly live curve against a
        daily-aggregate ledger would put that difference on the dashboard as an
        unexplainable gap, and with ``live_estimate_enabled`` on it would size
        real runs from a number the ledger does not agree with.

        Mirrors the conditions in ``CalculationMixin._hourly_et_for_zone``, read
        from the stored module config rather than an instance: instantiating a
        module re-scans the calc-module directory, which is far too heavy for a
        path that runs every minute per zone.

        The opt-in read here is ``hourlycalculation`` — the switch the daily
        form itself reads, via ``_hourly_calculation_enabled`` — and NOT
        ``continuousupdates``. The two are independent axes, so reading the
        ingestion flag broke the mirror in both directions: dense ingestion
        alone put an hourly live curve against a ledger still running the daily
        equation, which is the 12% gap this gate exists to prevent, while a
        poll-only install that had turned the hourly form on was refused the
        buffer source the daily calculation was already using. Note this gates
        only the BUFFER source — a weather-service install keeps the client and
        proxy estimates it already had, which is why the check is here rather
        than in ``_intraday_for_zone``.

        Strict identity check, matching ``_hourly_calculation_enabled``, so a
        test double or an absent attribute reads as off.
        """
        if (
            getattr(
                getattr(self.store, "config", None),
                const.CONF_HOURLY_CALCULATION,
                False,
            )
            is not True
        ):
            return False
        module = self.store.get_module(zone.get(const.ZONE_MODULE))
        if not module or module.get(const.MODULE_NAME) != "PyETO":
            return False
        config = module.get(const.MODULE_CONFIG) or {}
        # Stored either as the enum or as its bare value, depending on whether
        # the config went through the voluptuous schema on the way in.
        solrad = config.get(const.CONF_PYETO_SOLRAD_BEHAVIOR)
        if str(getattr(solrad, "value", solrad)) != SOLRAD_behavior.DontEstimate.value:
            return False
        try:
            forecast_days = int(config.get(const.CONF_PYETO_FORECAST_DAYS) or 0)
        except (TypeError, ValueError):
            return False
        return forecast_days == 0

    def _buffer_hourly_et(self, zone, anchor, *, now, geometry):
        """``(total_mm, {hour_start: eto_mm})`` since ``anchor`` from the buffer.

        Summed FAO-56 hourly ETo, in the same shape ``_hourly_et_for_zone``
        hands the daily calculation: the total is what the balance charges, and
        the per-hour series is what shapes it across the window's sub-steps.

        Returns None when the hourly form does not apply to this zone or the
        window cannot be reduced to hourly rows (``build_hourly_rows`` decides
        that: no readings, a required field missing from both the window and the
        carry-forward, a window longer than the buffer's retention). The caller
        then falls back exactly as it did before, so the failure mode is today's
        behaviour rather than a fabricated series.

        Cheap by construction: completed hours are carried in
        ``_hourly_carry`` and only the current partial hour is re-reduced.
        """
        if not self._hourly_form_applies(zone):
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

        zone_id = zone.get(const.ZONE_ID)
        carry = self._hourly_carry().get(zone_id)
        watermark, base = anchor, {}
        if carry is not None and carry.anchor == anchor and anchor <= carry.boundary:
            if carry.boundary <= now:
                watermark, base = carry.boundary, carry.per_hour
            # A boundary in the future means the clock went backwards; recompute
            # the whole window rather than trust a total measured past "now".

        # The same reduction the daily calculation runs, geometry and all: an
        # hour with no solar reading is refilled from the held clearness ratio
        # rather than a flat hold, and each row resolves its own UTC offset. A
        # window priced any other way drifts from the bucket the nightly calc
        # lands on, which is the one thing this estimate exists to track.
        priced = hourly_eto_priced(
            readings,
            watermark,
            mappings_config,
            now=now,
            last_entry=mapping.get(const.MAPPING_DATA_LAST_ENTRY),
            geometry=geometry,
        )
        if priced is None:
            return None
        rows, series = priced

        # Fold every hour that has closed into the carry. The rows already carry
        # each end's partial coverage through ``coverage_h``, so the anchor hour
        # is folded at its real share and never re-charged as a whole one.
        #
        # ``base`` and the freshly priced hours cannot collide: the carry holds
        # only hours strictly before its boundary, and the re-reduction starts AT
        # that boundary, which is a whole hour.
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        per_hour = dict(base)
        closed = {}
        for row, eto in zip(rows, series, strict=True):
            hour = row["hour_start"]
            per_hour[hour] = per_hour.get(hour, 0.0) + eto
            if hour < current_hour:
                closed[hour] = closed.get(hour, 0.0) + eto
        if current_hour > watermark and closed:
            self._hourly_carry()[zone_id] = _HourlyCarry(
                anchor, current_hour, {**base, **closed}
            )
        return sum(per_hour.values()), per_hour

    def _buffer_water_steps(
        self, zone, anchor, *, now, hourly_et, precip_total, applied
    ):
        """Water-balance sub-steps over the live window, or None to lump.

        The live twin of ``CalculationMixin._substeps_for_zone``, cut from the
        same rows by the same builder but over the live estimate's own anchor
        rather than the consume watermark. The two are the same instant on a
        healthy install, which is what makes the replayed curve land on the
        bucket the next calculation commits.

        No gate of its own. The caller reaches this only on the buffer path,
        which ``_hourly_form_applies`` has already restricted to PyETO zones on
        an install with ``hourlycalculation`` on — exactly the pair of conditions
        (``module_uses_precipitation`` and ``_hourly_calculation_enabled``) the
        daily side replays under. Adding a second, separately-worded gate here is
        how the two would drift.

        Reconciled against the same precipitation total the estimate publishes as
        its own trace, for the reason the daily side reconciles against ZONE_DELTA:
        the rain in the balance and the rain on the dashboard have to be the same
        water. They are derived from the same rows by the same rule, so a
        disagreement means an assumption has broken, and lumping the window is the
        self-consistent answer.
        """
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
            anchor,
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
                "intraday: sub-step precipitation %s does not reconcile with the "
                "aggregated %s for zone %s; using the lumped balance",
                stepped,
                precip_total,
                zone.get(const.ZONE_ID),
            )
            return None
        return steps

    def _hourly_carry(self) -> dict:
        """The per-zone completed-hour ETo carry, created on first use."""
        carry = getattr(self, "_hourly_carry_by_zone", None)
        if carry is None:
            carry = self._hourly_carry_by_zone = {}
        return carry

    def invalidate_live_estimate_carry(self, mapping_id=None) -> None:
        """Drop the completed-hour ETo carry after the buffer under it changed.

        A new calculation needs no call here — the carry is keyed on the zone's
        ``last_calculated`` and a moved anchor discards it. This is for the
        changes that rewrite the readings WITHOUT moving that anchor: a weather
        data reset, a sensor-group source change, the continuous-update row cap
        dropping unconsumed rows. The carried hours were computed from rows that
        no longer exist, and nothing else would ever notice.
        """
        carry = getattr(self, "_hourly_carry_by_zone", None)
        if not carry:
            return
        if mapping_id is None:
            carry.clear()
            return
        try:
            mapping_id = int(mapping_id)
        except (TypeError, ValueError):
            carry.clear()
            return
        for zone in self.store.get_zones() or []:
            zone_mapping = zone.get(const.ZONE_MAPPING)
            if zone_mapping is not None and int(zone_mapping) == mapping_id:
                carry.pop(zone.get(const.ZONE_ID), None)

    @staticmethod
    def _rows_since(rows, last_calc_local):
        """Hourly rows whose hour ends after ``last_calc`` (window = since calc).

        Both ``rows`` (their ``time``) and ``last_calc_local`` are local clock
        time, so they compare directly — no tz offset is applied (the anchor is
        already local; see :func:`_parse_local_naive`).
        """
        if not last_calc_local:
            return rows
        out = []
        for r in rows:
            try:
                rdt = datetime.datetime.fromisoformat(r["time"])
            except (ValueError, KeyError):
                continue
            if rdt + datetime.timedelta(hours=1) > last_calc_local:
                out.append(r)
        return out

    def _intraday_for_zone(self, zone, inputs) -> dict:
        """Compute one zone's estimate from pre-fetched inputs (sync, defensive)."""
        result = {
            "available": False,
            "method": None,
            "et_since": None,
            "precip_since": None,
            "drainage_since": None,
            "live_deficit": None,
            "as_of": None,
        }
        try:
            client = inputs["client"]
            # The integration's effective coordinates first: they honour manually
            # configured ones and exist with no weather client at all, which is
            # the whole point here. The client's own are the fallback so a
            # configuration that only ever reached the client still resolves.
            lat = getattr(self, "_effective_latitude", None)
            lon = getattr(self, "_effective_longitude", None)
            elevation = getattr(self, "_effective_elevation", None)
            if lat is None or lon is None:
                lat = getattr(client, "latitude", None)
                lon = getattr(client, "longitude", None)
                elevation = getattr(client, "elevation", 0)
            elevation = elevation or 0
            if lat is None or lon is None:
                return result
            bucket = zone.get(const.ZONE_BUCKET)
            if bucket is None:
                return result
            max_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
            metric = self.hass.config.units is METRIC_SYSTEM

            def to_mm(v):
                if v is None:
                    return None
                return (
                    v if metric else convert_between(const.UNIT_INCH, const.UNIT_MM, v)
                )

            def from_mm(v):
                return (
                    v if metric else convert_between(const.UNIT_MM, const.UNIT_INCH, v)
                )

            bucket_mm = to_mm(bucket)
            max_bucket_mm = to_mm(max_bucket)
            drainage_rate_mm = to_mm(zone.get(const.ZONE_DRAINAGE_RATE)) or 0.0
            last_calc = _parse_local_naive(zone.get(const.ZONE_LAST_CALCULATED))
            # A never-calculated zone has no anchor for the "since calc" window;
            # showing a whole-day estimate would be misleading (and looks like a
            # shared, un-anchored value). Offer no estimate until the first calc.
            if last_calc is None:
                return result
            # ONE anchor for both halves of the balance, but not earlier than the
            # consume watermark. The two are equal in normal operation; a weather
            # data reset or a sensor-group source change advances the watermark
            # alone, deleting the readings behind it. Anchoring at
            # last_calculated then reaches back over a stretch with no readings,
            # and carry-forward answers by holding the CURRENT value across all
            # of it: measured live, a reset at midday charged 16.6 mm of ET for a
            # day whose real total is a few mm, because a bright midday
            # pyranometer reading was held backwards through the night. Starting
            # at the watermark instead omits the deleted stretch, which is the
            # honest answer for data that no longer exists, and it is also the
            # floor the buffer is pruned to.
            last_consumed = _parse_local_naive(zone.get(const.ZONE_LAST_CONSUMED))
            anchor = max(last_calc, last_consumed) if last_consumed else last_calc

            now_local = inputs.get("now") or dt_util.now().replace(tzinfo=None)
            tz_offset_h = inputs.get("tz_offset_h")
            site_tz = inputs.get("site_tz")
            if tz_offset_h is None:
                offset = dt_util.now().utcoffset()
                tz_offset_h = offset.total_seconds() / 3600.0 if offset else 0.0
                site_tz = dt_util.DEFAULT_TIME_ZONE

            rows = inputs["rows"]
            # The buffer FIRST, ahead of any weather client's own hourly series.
            # The buffer is what the daily calculation reduces, whatever fills it
            # — sensors here, the weather poll elsewhere — so summing it with the
            # same row builder is the only source that coincides with the stored
            # bucket at each calculation. A client's series is a different set of
            # observations for the same site and drifts from the ledger.
            buffer_et = self._buffer_hourly_et(
                zone,
                anchor,
                now=now_local,
                geometry=SiteGeometry(lat, lon, elevation, tz_offset_h, site_tz),
            )
            hourly_et = None
            if buffer_et is not None:
                et_mm, hourly_et = buffer_et
                # Same anchor as the ET, aggregated the way the daily calc does
                # (rate -> Riemann, cumulative gauge -> delta).
                precip_mm = self._observed_precip_since_mm(zone, anchor)
                method = "hourly_sensor"
                # The buffer is current to now, not to the last closed hour.
                as_of = now_local.isoformat()
            elif rows:
                tz = inputs["tz"] or 0.0
                window = self._rows_since(rows, anchor)
                et_mm = rigorous_et_since(window, lat, lon, tz, elevation)
                precip_mm = sum(r.get("precipitation", 0.0) for r in window)
                method = "hourly"
                as_of = window[-1]["time"] if window else None
            else:
                forecast = inputs["forecast"]
                if not forecast:
                    return result
                day0 = forecast[0]
                tmin = day0.get(const.MAPPING_MIN_TEMP)
                tmax = day0.get(const.MAPPING_MAX_TEMP)
                if tmin is None or tmax is None:
                    return result
                local = now_local
                tz = tz_offset_h
                doy = local.timetuple().tm_yday
                # Window = elapsed hours since the last daily calc, anchored to
                # its LOCAL wall-clock time (the anchor is naive local). When the
                # calc was on a previous day the window spans midnight, so
                # accumulate the remaining hours of the calc day plus today's
                # elapsed hours rather than resetting to 00:00 — the two days'
                # daily ET0 are ~equal over a <=24 h window (today's is used).
                days_ago = (local.date() - anchor.date()).days
                if days_ago <= 0:
                    elapsed = [h + 0.5 for h in range(anchor.hour, local.hour + 1)]
                elif days_ago == 1:
                    elapsed = [h + 0.5 for h in range(anchor.hour, 24)] + [
                        h + 0.5 for h in range(0, local.hour + 1)
                    ]
                else:
                    # Stale calc (>1 day old) — fall back to today's elapsed only.
                    elapsed = [h + 0.5 for h in range(0, local.hour + 1)]
                daily = estimate_daily_et0_hargreaves(tmin, tmax, lat, doy)
                et_mm = proxy_et_since(daily, lat, lon, doy, tz, elapsed)
                # No hourly precip series on this source — use the precipitation
                # actually collected into the sensor group since the last calc,
                # aggregated the same way the daily calc does (rate->Riemann /
                # gauge->delta), so it's time-weighted. 0 when nothing collected.
                precip_mm = self._observed_precip_since_mm(zone, anchor)
                method = "proxy"
                as_of = local.isoformat()

            # Hours elapsed since the last daily calc — the same window the ET
            # and precip deltas cover — so any surplus above field capacity is
            # drained over exactly that window (mirrors the daily calc's
            # capacity cap + drainage, integrated analytically). Compared in
            # local time since the anchor is naive local (see _parse_local_naive).
            # Used by the LUMPED balance only; the replay takes each step's own
            # dt_hours, which is the whole point of it.
            elapsed_hours = max(0.0, (now_local - anchor).total_seconds() / 3600.0)
            # Crop coefficient (WS-4): scale the intraday ET0 term by the zone's Kc
            # so the live deficit stays consistent with the daily calc (which also
            # applies Kc to the ET term only). Precip is NOT scaled. Default 1.0.
            kc = zone.get(const.ZONE_KC, const.CONF_DEFAULT_KC)
            if kc is None:
                kc = const.CONF_DEFAULT_KC
            et_mm = et_mm * kc
            # Replay the window at its own event times, exactly as the daily
            # calculation does, rather than lumping it into one update. The
            # lumped form treats every mid-window event as present from the last
            # commit onward, and drainage is Brooks-Corey with n = 4, so the
            # error is strongly non-linear and runs one way: on this install's
            # zone parameters a 12.7 mm surplus drains 1.57 mm charged over the
            # hour it actually fell and 6.94 mm charged over a 20 h window. That
            # 5.37 mm is 0.21 in against a 0.394 in bucket_threshold, always in
            # the direction that reads the zone drier than it is, and with
            # live_estimate_enabled on it both triggers and sizes real runs.
            #
            # Only the buffer path can be replayed: it is the only one with the
            # rows the sub-steps are cut from. The client and proxy paths keep
            # the lumped form, which is also what the daily side does when it
            # cannot sub-step.
            steps = None
            if hourly_et is not None:
                steps = self._buffer_water_steps(
                    zone,
                    anchor,
                    now=now_local,
                    hourly_et=hourly_et,
                    precip_total=precip_mm,
                    # Irrigation credited part-way through this window. Read
                    # ONLY: the ledger is the daily calculation's to consume, and
                    # the estimate is a projection from the last commit rather
                    # than a commit of its own.
                    applied=pending_bucket_events(zone),
                )
            # Drainage comes back alongside the deficit rather than being
            # re-derived: it is a trace of its own on the dashboard (bucket,
            # drainage and ET are plotted separately), and a second computation
            # of the same closed form is a second thing to keep in step.
            if steps is not None:
                # The stored bucket already contains these credits, so the replay
                # starts from the level BEFORE them and each goes back in at the
                # step it landed on. Mirrors calculate_module.
                applied_total = sum(s.applied_mm for s in steps)
                live_mm, drained_mm, _runoff = replay_water_balance(
                    bucket_mm - applied_total,
                    -et_mm,
                    steps,
                    drainage_rate_mm,
                    max_bucket_mm,
                    # A maximum bucket of 0 still clamps, but there is no field
                    # capacity to scale Brooks-Corey against.
                    max_bucket_mm if max_bucket_mm and max_bucket_mm > 0 else None,
                )
            else:
                live_mm, drained_mm = live_balance(
                    bucket_mm,
                    et_mm,
                    precip_mm,
                    max_bucket_mm,
                    drainage_rate=drainage_rate_mm,
                    elapsed_hours=elapsed_hours,
                )
            ndigits = 2 if metric else 3
            # The three accumulators are graph inputs rather than display
            # strings: they run since the last calculation, so a dashboard
            # differentiates them to recover a rate. Display precision is too
            # coarse for that. At a midday ET of 0.4 mm/h an imperial install
            # gains 0.00026 in/min against a 0.001 in step, so the value would
            # only move every ~4 minutes and a per-minute derivative would
            # alternate between zero and a spike instead of tracing a rate.
            # Nothing renders these — the panel chip formats live_deficit alone
            # — so the extra digits cost only bytes.
            trace_digits = ndigits + 2
            result.update(
                available=True,
                method=method,
                et_since=round(from_mm(et_mm), trace_digits),
                precip_since=round(from_mm(precip_mm), trace_digits),
                drainage_since=round(from_mm(drained_mm), trace_digits),
                # The sensor's own state, which IS displayed. Kept at display
                # precision so the entity does not show five decimals.
                live_deficit=round(from_mm(live_mm), ndigits),
                as_of=as_of,
            )
        except Exception as e:  # noqa: BLE001 — estimate must never raise
            _LOGGER.debug("intraday estimate failed for a zone: %s", e)
        return result

    async def async_get_zone_estimates(self) -> dict:
        """Return ``{zone_id: estimate}`` for every zone with an available value."""
        inputs = await self._fetch_intraday_inputs()
        zones = await self.store.async_get_zones()
        out = {}
        for zone in zones:
            est = self._intraday_for_zone(zone, inputs)
            if est["available"]:
                out[str(zone.get(const.ZONE_ID))] = est
        return out

    async def async_refresh_zone_estimates(self) -> dict:
        """Recompute the estimates, cache them, and notify the live sensors.

        Called from the existing weather-update, sensor-ingestion and
        daily-calculation cycles — deliberately NOT a separate timer. Both the
        per-zone live-deficit sensors and the panel outlook are served from this
        one cache so the weather client is only hit once per cycle.
        """
        self._zone_estimates_refreshed_at = time.monotonic()
        estimates = await self.async_get_zone_estimates()
        self._zone_estimates_cache = estimates
        async_dispatcher_send(self.hass, const.DOMAIN + "_estimates_updated")
        return estimates

    async def async_refresh_zone_estimates_throttled(self) -> None:
        """Refresh at most once per ``LIVE_ESTIMATE_MIN_REFRESH_SECONDS``.

        For callers driven by sensor events rather than by a schedule: event
        ingestion fires in bursts and would otherwise re-publish every zone's
        estimate several times a minute. Monotonic, so a clock adjustment cannot
        stall the refresh until the wall clock catches up.
        """
        last = getattr(self, "_zone_estimates_refreshed_at", None)
        if (
            last is not None
            and time.monotonic() - last < LIVE_ESTIMATE_MIN_REFRESH_SECONDS
        ):
            return
        await self.async_refresh_zone_estimates()

    async def async_get_cached_zone_estimates(self) -> dict:
        """Serve the cached estimates, computing them once if not cached yet."""
        cache = getattr(self, "_zone_estimates_cache", None)
        if cache is None:
            return await self.async_refresh_zone_estimates()
        return cache
