"""Intra-day "live status" estimate orchestration.

Read-only: estimates how much each zone's bucket has drifted *since its last
calculation*. Four sources, in decreasing order of agreement with the stored
ledger:

* **the zone's own sensor-group buffer** — the same rows the daily calculation
  reduces, summed as FAO-56 hourly ETo by the same row builder and run through
  the same replayed water balance, so the live curve is the path the stored
  bucket takes and the two coincide at every calculation time;
* **the zone's own daily equation over the composed window**, for the zones the
  hourly form declines because their module estimates solar radiation from the
  day's temperature range. Those cannot agree with their commit however the
  balance is combined, because the two were computing different quantities. The
  window's observed part is reduced by the call the commit will use, its
  day-level extremes are extended over the hours still to come (see
  ``day_projection``), and the module instance the commit uses prices the
  result — so the inputs converge on exactly what the commit will see;
* **the weather client's hourly series**, where one exposes solar radiation;
* a **Hargreaves-seeded proxy** distributed over the elapsed hours, for
  providers with neither.

Those four choose the EVAPOTRANSPIRATION only. Precipitation comes from the
reading buffer on every one of them, because that is the only source the daily
calculation ever books rain from: a total taken from anywhere else is a total
the ledger will never record.

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
from .calculation import (
    pending_bucket_events,
    replayed_balance_applies,
    trailing_temperature_amplitude,
)
from .day_projection import (
    TIER_OBSERVED,
    TIER_SELF_CONTAINED,
    TIER_SERVICE,
    compose_extremes,
    diurnal_remainder,
    forecast_remainder,
)
from .duration_math import zone_run_duration
from .et_estimate import (
    SiteGeometry,
    estimate_daily_et0_hargreaves,
    hourly_eto_priced,
    lumped_water_balance,
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
        inputs["hourly_forecast"] = self._hourly_forecast_temperatures(client)
        return inputs

    @staticmethod
    def _hourly_forecast_temperatures(client):
        """``[(naive local datetime, temperature C)]`` from the configured service.

        Fills the hours a calculation window has not reached yet, so the day-level
        extremes the commit's equation consumes can be read off the whole window
        rather than off its observed part. The clients hand back absolute
        instants, because three of the four products stamp in UTC and one in the
        site's own zone; they are localised once here, since everything the
        estimate compares them against is naive local.

        The accessor reads an already-fetched document and never issues a request
        of its own, so the estimate path adds no external polling. ``None``
        where the service has no hourly series
        or nothing has been fetched yet; the caller then falls to the
        self-contained tier and publishes that it did.
        """
        if client is None or not hasattr(client, "get_hourly_temperature_forecast"):
            return None
        try:
            series = client.get_hourly_temperature_forecast()
        except Exception as e:  # noqa: BLE001 — estimate must never raise
            _LOGGER.debug("intraday: get_hourly_temperature_forecast failed: %s", e)
            return None
        if not series:
            return None
        out = []
        for when, temp in series:
            if when is None or temp is None:
                continue
            if when.tzinfo is not None:
                when = dt_util.as_local(when).replace(tzinfo=None)
            out.append((when, float(temp)))
        return out or None

    async def _resolve_zone_modules(self, zones):
        """``{module_id: instance}`` for the zones about to be estimated.

        Resolved HERE rather than inside ``_intraday_for_zone`` because the
        resolver lives on the calculation mixin, and the estimate's mixin is
        instantiated on its own in its tests -- a cross-mixin call raises there,
        and on this path an exception is indistinguishable from an estimate that
        simply has nothing to say. Handing the instances in through ``inputs``
        keeps the per-zone reduction free of that dependency, and a caller that
        supplies none simply gets the sources that came before this one.

        Affordable only because the resolver caches: it re-scans the calc-module
        directory over an executor hop on a miss, which is fine once a day and
        not once a minute per zone.
        """
        resolver = getattr(self, "getModuleInstanceByID", None)
        if resolver is None:
            return {}
        out = {}
        for zone in zones:
            module_id = zone.get(const.ZONE_MODULE)
            if module_id is None or module_id in out:
                continue
            try:
                out[module_id] = await resolver(module_id)
            except Exception as e:  # noqa: BLE001 — estimate must never raise
                _LOGGER.debug("intraday: could not resolve module %s: %s", module_id, e)
        return out

    def _aggregate_live_window(self, zone, anchor, *, now=None):
        """The zone's elapsed window, reduced exactly as ``_aggregate_for_zone`` will.

        One reduction serving both halves of the estimate: the precipitation
        trace, and the day-level inputs the mirrored daily equation consumes. The
        commit runs this same call over the whole window when it closes, so the
        two agree by construction rather than by two hand-maintained argument
        lists happening to match -- which is how they drifted before.
        """
        mapping_id = zone.get(const.ZONE_MAPPING)
        if mapping_id is None:
            return None
        mapping = self.store.get_mapping(mapping_id)
        if not mapping:
            return None
        readings = self.store.get_mapping_buffer(mapping_id)
        if not readings:
            return None
        return aggregate_window(
            readings,
            anchor,
            mapping.get(const.MAPPING_MAPPINGS) or {},
            now=now,
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
        agg = self._aggregate_live_window(zone, anchor)
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

        Strictly narrower than the balance form's condition, and structurally so:
        it starts from that same predicate and adds the two configurations a
        buffer-summed ETo cannot reproduce. A zone refused here still has its
        window replayed — the sources are one axis and the balance form is
        another.

        The opt-in read is ``hourlycalculation`` — the switch the commit itself
        reads — and NOT ``continuousupdates``. The two are independent axes, so
        reading the ingestion flag broke the mirror in both directions: dense
        ingestion alone put an hourly live curve against a ledger still running
        the daily equation, which is the 12% gap this gate exists to prevent,
        while a poll-only install that had turned the hourly form on was refused
        the buffer source the commit was already using. Note this gates only the
        BUFFER source — a weather-service install keeps the client and proxy
        estimates it already had, which is why the check is here rather than in
        ``_intraday_for_zone``.
        """
        if not replayed_balance_applies(self.store, zone):
            return False
        module = self.store.get_module(zone.get(const.ZONE_MODULE))
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

    def _daily_form_applies(self, zone, modinst) -> bool:
        """Whether this zone's commit runs the DAILY equation on estimated radiation.

        The complement of :meth:`_hourly_form_applies` on the source axis, and the
        largest population there is: estimating solar radiation from the day's
        temperature range is the shipped default. Their commit replays the window
        and prices it with the daily equation, while their estimate priced it from
        a weather client's own hourly series or a temperature-seeded proxy -- a
        different quantity, which no amount of fixing the balance form closes.

        Read from the module INSTANCE rather than the stored config, unlike the
        hourly gate, because the instance is needed anyway to run the equation and
        it is the same object the commit reads.

        Forecast days are excluded: with them the commit averages today with days
        that need a projection of their own, which is a separate construction.
        """
        if modinst is None:
            return False
        if not replayed_balance_applies(self.store, zone):
            return False
        if str(getattr(modinst, "_solrad_behavior", "")) == str(
            SOLRAD_behavior.DontEstimate.value
        ):
            return False
        return not getattr(modinst, "forecast_days", 0)

    def _latest_temperature(self, zone, agg):
        """The temperature the sensor group is reading now, or None.

        The self-contained projection is held to pass through this, so it
        re-anchors on every refresh instead of freezing a curve drawn hours ago.
        The mapping's last-seen entry is preferred over the window mean because
        it is the CURRENT reading; the window's mean is the fallback for a group
        that has no last entry at all.
        """
        mapping = self.store.get_mapping(zone.get(const.ZONE_MAPPING))
        if mapping:
            latest = (mapping.get(const.MAPPING_DATA_LAST_ENTRY) or {}).get(
                const.MAPPING_TEMPERATURE
            )
            if latest is not None:
                try:
                    return float(latest)
                except (TypeError, ValueError):
                    pass
        value = (agg or {}).get(const.MAPPING_TEMPERATURE)
        return None if value is None else float(value)

    def _projected_extremes(self, zone, agg, inputs, *, now, window_end, geometry):
        """``(tmin, tmax, tier)`` for the whole window, read off the composition.

        Observed so far, extended over the hours the window has not reached, with
        the extremes taken from the two together. The remainder shrinks to
        nothing as the window closes, so the inputs converge on exactly what the
        commit will see -- no blend rule, no gate times, and no residual left
        standing at the moment of commit.

        Tiers are tried in a fixed order. A Home Assistant weather entity sits
        between these two and is not built yet; its absence shows up
        as the self-contained tier being published, never as a wrong number
        presented as a good one.
        """
        low = agg.get(const.MAPPING_MIN_TEMP)
        high = agg.get(const.MAPPING_MAX_TEMP)
        if low is None or high is None:
            return None, None, None

        remainder = forecast_remainder(inputs.get("hourly_forecast"), now, window_end)
        tier = TIER_SERVICE
        if remainder is None:
            remainder = diurnal_remainder(
                now,
                self._latest_temperature(zone, agg),
                trailing_temperature_amplitude(
                    self.store, zone.get(const.ZONE_MAPPING)
                ),
                geometry,
                window_end,
            )
            tier = TIER_SELF_CONTAINED
        if not remainder:
            # Either no source could fill the remaining hours, or there are none
            # left to fill. Both publish the observed tier: the attribute answers
            # which source supplied the unobserved part of the window, and at the
            # moment of commit nothing did, because there was nothing to supply.
            # Reporting a forecast tier there would claim a contribution that was
            # not made, on exactly the reading a user checks the two figures
            # against each other with.
            remainder, tier = [], TIER_OBSERVED
        low, high = compose_extremes(float(low), float(high), remainder)
        return low, high, tier

    def _daily_mirror_et(self, zone, agg, inputs, *, anchor, now, geometry):
        """``(et_mm, tier)`` from the zone's OWN daily equation, or None.

        The whole point: a zone that estimates solar radiation gets a live
        bucket computed with the equation its commit runs, rather than one
        computed with a different equation and then compared against it.

        The elapsed window is reduced by the same call the commit reduces the
        whole window with, its day-level extremes are replaced by the composed
        ones, and the zone's own module instance prices the result. The window's
        share is ``MAPPING_DATA_MULTIPLIER`` -- the commit's own ``hour_multiplier``
        out of the same aggregate -- so the estimate charges the elapsed hours at
        the rate the projected day total sets, and never charges past now.

        The crop coefficient is deliberately NOT applied here; the caller applies
        it to whichever source produced the window total, exactly as the commit
        applies it to the ET term alone.

        The clamp warning is suppressed explicitly. The calculation avoids it
        structurally by never running the daily equation when it will not use the
        answer; this path runs it every minute per zone and would otherwise warn
        about a sensor on every refresh -- and, sharing the cached instance, would
        consume the once-only flag the commit's own warning depends on.
        """
        modinst = (inputs.get("modules") or {}).get(zone.get(const.ZONE_MODULE))
        if not self._daily_form_applies(zone, modinst):
            return None
        if not agg:
            return None
        low, high, tier = self._projected_extremes(
            zone,
            agg,
            inputs,
            now=now,
            # The window is a day from its anchor: that is what the commit's own
            # equation is defined over, and it is where the remainder has to run
            # out for the two to meet. Anchor-agnostic on purpose -- a fixed calc
            # time and a schedule's decision point are both just an anchor.
            #
            # A day is an assumption, and it is a good one under both commit
            # modes. The fixed-time mode makes it exact: the anchor IS calctime.
            # The before-run mode commits at a schedule's decision point, which
            # is either a configured earliest start -- a clock time, so exact
            # again -- or the solar target minus a bound priced from
            # configuration alone. Only the solar target moves night to night,
            # by at most 1.75 minutes at this latitude, so consecutive windows
            # are a day apart to within a couple of minutes either way.
            #
            # What does break it is a SKIPPED commit, which the before-run mode
            # allows whenever a night produces no run. Then the real window is
            # longer than a day and this runs out early, so both extremes fall
            # back to the observation -- the conservative direction, and the
            # published tier says ``observed`` rather than claiming a forecast
            # supplied something. ``async_guard_ledger_staleness`` caps that
            # stretch at a day, so the window never exceeds about two.
            window_end=anchor + datetime.timedelta(hours=24),
            geometry=geometry,
        )
        if low is None:
            return None
        projected = {
            **agg,
            const.MAPPING_MIN_TEMP: low,
            const.MAPPING_MAX_TEMP: high,
        }
        delta = modinst.calculate(
            weather_data=projected, forecast_data=None, warn_on_clamp=False
        )
        if delta is None:
            return None
        multiplier = agg.get(const.MAPPING_DATA_MULTIPLIER)
        if multiplier is None:
            return None
        # ``delta`` is the daily equation's own sign convention: negative for a
        # loss. The estimate carries evapotranspiration as a positive quantity.
        return max(0.0, -float(delta)) * float(multiplier), tier

    def _buffer_water_steps(
        self, zone, anchor, *, now, hourly_et, precip_total, applied
    ):
        """Water-balance sub-steps over the live window, or None to lump.

        The live twin of ``CalculationMixin._substeps_for_zone``, cut from the
        same rows by the same builder but over the live estimate's own anchor
        rather than the consume watermark. The two are the same instant on a
        healthy install, which is what makes the replayed curve land on the
        bucket the next calculation commits.

        No gate of its own: the caller has already asked
        ``replayed_balance_applies``, which is the commit's own predicate. Adding
        a second, separately-worded gate here is how the two would drift.

        The rows are the buffer's on every path, including the two whose
        evapotranspiration came from a weather client instead. That is not a
        coupling of two sources: the buffer is the only place the commit ever
        books rain from, so it is the only place a replay can honestly take rain
        TIMING from either. ``hourly_et`` is None on those paths, which spreads
        their window total across the steps by measured radiation — exactly what
        the commit does with its own daily total.

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
            "live_duration": None,
            "as_of": None,
            # Which form of the balance produced the number above. Published
            # because nothing else makes the difference visible from outside the
            # process: a replayed estimate and a lumped one that happens to land
            # close are the same reading, and the gap between them is exactly
            # what an operator would be diagnosing.
            "balance_form": None,
            # Which source filled in the hours the window has not reached, where
            # the evapotranspiration came from the commit's own daily equation.
            # None on every other source, which needs no projection at all. The
            # tiers differ by a factor of three on the input they supply, so a
            # figure alone never says which one produced it.
            "forecast_tier": None,
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
            geometry = SiteGeometry(lat, lon, elevation, tz_offset_h, site_tz)
            buffer_et = self._buffer_hourly_et(
                zone,
                anchor,
                now=now_local,
                geometry=geometry,
            )
            hourly_et = None
            forecast_tier = None
            # Reduced once and shared: the mirrored daily equation reads its
            # day-level inputs from this, and the precipitation trace is the same
            # window's rain. Two reductions of one window is a needless second
            # pass on a path that runs every minute per zone.
            agg = self._aggregate_live_window(zone, anchor, now=now_local)
            mirrored = (
                None
                if buffer_et is not None
                else self._daily_mirror_et(
                    zone,
                    agg,
                    inputs,
                    anchor=anchor,
                    now=now_local,
                    geometry=geometry,
                )
            )
            if buffer_et is not None:
                et_mm, hourly_et = buffer_et
                # Same anchor as the ET, aggregated the way the daily calc does
                # (rate -> Riemann, cumulative gauge -> delta).
                precip_mm = self._observed_precip_since_mm(zone, anchor)
                method = "hourly_sensor"
                # The buffer is current to now, not to the last closed hour.
                as_of = now_local.isoformat()
            elif mirrored is not None:
                # A zone whose module estimates solar radiation from the day's
                # temperature range. Its commit runs the daily equation, so the
                # estimate runs the same one over the composed window rather than
                # a different equation whose answer is then compared against it.
                et_mm, forecast_tier = mirrored
                precip_mm = (agg or {}).get(const.MAPPING_PRECIPITATION, 0.0) or 0.0
                method = "daily_mirror"
                as_of = now_local.isoformat()
            elif rows:
                tz = inputs["tz"] or 0.0
                window = self._rows_since(rows, anchor)
                et_mm = rigorous_et_since(window, lat, lon, tz, elevation)
                # Rain from the BUFFER, not from the provider's own hourly
                # series, even though the ET on this path comes from that
                # series. The buffer is the only place the daily calculation
                # ever books rain from, so summing the provider's series
                # published a total the ledger will never record: a different
                # set of observations for the same site, plain-summed rather
                # than aggregated per source, and cut at whole-hour row
                # boundaries instead of at the anchor. Same anchor as the ET, so
                # the balance is still the difference of one window.
                precip_mm = self._observed_precip_since_mm(zone, anchor)
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
            # Replayed wherever the zone's OWN commit replays, asked through the
            # commit's own predicate. That is a wider set than the zones offered
            # the buffer-summed ET: a zone that estimates solar radiation, or
            # folds forecast days into its ET, is refused that source and still
            # has its window replayed when it commits. Those zones were the ones
            # being read through the lumped form against a replayed ledger. The
            # buffer path is included by the same condition rather than by a
            # source check — ``_hourly_form_applies`` is strictly narrower.
            steps = None
            if replayed_balance_applies(self.store, zone):
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
                # Lumped, but still with the drainage integral cut at the credit
                # times, because the commit's lumped arm cuts it there too. Both
                # arms are gated by the same predicate, so this is the same
                # population -- reading it through an uncut integral is exactly
                # the "lumped form against a replayed ledger" gap described
                # above, in the one place it would not be visible as one.
                live_mm, drained_mm, _runoff, _segments = lumped_water_balance(
                    bucket_mm,
                    precip_mm - et_mm,
                    [
                        ((stamp - anchor).total_seconds() / 3600.0, mm)
                        for stamp, mm in pending_bucket_events(zone)
                    ],
                    elapsed_hours,
                    drainage_rate_mm,
                    max_bucket_mm,
                    max_bucket_mm if max_bucket_mm and max_bucket_mm > 0 else None,
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
            # The sensor's own state, which IS displayed. Kept at display
            # precision so the entity does not show five decimals.
            live_display = round(from_mm(live_mm), ndigits)
            result.update(
                available=True,
                method=method,
                et_since=round(from_mm(et_mm), trace_digits),
                precip_since=round(from_mm(precip_mm), trace_digits),
                drainage_since=round(from_mm(drained_mm), trace_digits),
                live_deficit=live_display,
                live_duration=self._live_run_duration(zone, live_display, metric),
                as_of=as_of,
                balance_form="replayed" if steps is not None else "lumped",
                forecast_tier=forecast_tier,
            )
        except Exception as e:  # noqa: BLE001 — estimate must never raise
            _LOGGER.debug("intraday estimate failed for a zone: %s", e)
        return result

    @staticmethod
    def _live_run_duration(zone, deficit, metric):
        """Seconds a live-estimate run would water this zone for, or ``None``.

        Published so the panel can show the duration the run will actually use
        rather than the last commit's frozen one. It is the *same packing of
        the same number* the runner's ``_zone_run_decision`` sizes with —
        :func:`zone_run_duration` on the published (rounded) deficit — so the
        screen and the run cannot state different durations for one run; a
        second formula on the frontend is exactly how they would drift apart.

        ``None`` where the runner does not size the zone from the live deficit:
        flow-metered zones deliver to a measured volume and deliberately keep
        the daily gate, so the panel has to fall back to the committed figures
        for them the way the runner does. Independent of
        ``live_estimate_enabled``: with the feature off the runner ignores this
        number entirely, and so does the panel.
        """
        if zone.get(const.ZONE_FLOW_SENSOR):
            return None
        return zone_run_duration(zone, deficit, metric)

    async def async_get_zone_estimates(self) -> dict:
        """Return ``{zone_id: estimate}`` for every zone with an available value."""
        inputs = await self._fetch_intraday_inputs()
        zones = await self.store.async_get_zones()
        inputs["modules"] = await self._resolve_zone_modules(zones)
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
