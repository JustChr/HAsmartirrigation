"""Observed-watering bucket crediting (experimental, opt-in).

When enabled (Setup → Experimental), the coordinator watches each zone's linked
valve/switch and credits the zone's bucket whenever water is applied OUTSIDE
Smart Irrigation's own runner — a manual tap, an automation, anything that opens
the valve. The applied depth is estimated from the run time and the zone's
configured throughput (volume = minutes × throughput; depth_mm = volume_L /
size_m2), which keeps the soil-moisture model honest when you water by other
means.

SI's own runs are NOT credited here (the runner already accounts for them); they
are suppressed via the per-zone marker set by
``IrrigationRunnerMixin._note_si_valve``.

Methods live on a mixin the SmartIrrigationCoordinator inherits, so they use
``self`` to reach coordinator state (store, hass, the SI-driven marker).
"""

import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.core import Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .helpers import convert_between
from .opensprinkler import zone_watch_entity

_LOGGER = logging.getLogger(__name__)

# Valve/switch states that count as "water flowing".
_ON_STATES = ("on", "open", "opening")


class ObservedWateringMixin:
    """Credit the bucket for externally-driven watering of linked valves."""

    async def async_setup_observed_watering(self) -> None:
        """(Re)subscribe to linked-valve state changes per the current config.

        Idempotent: rebuilds the subscription only when the tracked entity set
        actually changes, so it is cheap to call on startup and on every config
        update. When the feature is off (or no zone has a linked valve) it tears
        any existing subscription down.
        """
        # Strict identity check: only an explicit True opts in. This also keeps
        # the method a safe no-op when the store config is a test double.
        enabled = self.store.config.observed_watering_enabled is True
        entity_map: dict[str, int] = {}
        if enabled:
            for zone in await self.store.async_get_zones():
                # linked_entity for classic zones; else the opt-in observed_entity
                # for service/self-closing zones (no linked valve of their own).
                # Through the accessor, because an OpenSprinkler zone's
                # linked_entity is its station-ENABLED switch, which is on
                # permanently — watching it would report the zone as watering for
                # ever and credit a bucket on every restart. The accessor hands
                # back the station's running sensor instead.
                entity = zone_watch_entity(self.hass, zone) or zone.get(
                    const.ZONE_OBSERVED_ENTITY
                )
                if entity:
                    entity_map[entity] = int(zone.get(const.ZONE_ID))

        entities = frozenset(entity_map)
        # Keep the entity→zone map fresh even on a no-op (a zone id could in
        # principle be reassigned to the same entity string).
        self._observed_zone_by_entity = entity_map
        if entities == self._observed_entities:
            # Known, accepted edge case: if a zone id is remapped to the SAME entity
            # string while an external run is in flight, this no-op path skips the
            # meter-cancel below and the meter stays keyed under the old zone id (a
            # leaked 15-s timer + one uncredited run). It self-heals on the next
            # entity-set change, the zone's next external open (single-flight cancel),
            # or teardown; the trigger (a set-preserving remap during an active run) is
            # exotic, so it is left unhandled rather than complicate the hot path.
            return

        if self._observed_unsub is not None:
            self._observed_unsub()
            self._observed_unsub = None
        # Never leak an in-flight flow sampler across a subscription rebuild.
        for zone_id in list(self._observed_meters()):
            self._observed_cancel_meter(zone_id)
        self._observed_on_since = {}
        self._observed_entities = entities

        if not entities:
            _LOGGER.debug("Observed watering: disabled or no linked valves")
            return

        self._observed_unsub = async_track_state_change_event(
            self.hass, list(entities), self._observed_state_changed
        )
        _LOGGER.info("Observed watering: tracking %d linked valve(s)", len(entities))

    def async_teardown_observed_watering(self) -> None:
        """Cancel the linked-valve subscription (called on unload)."""
        if getattr(self, "_observed_unsub", None) is not None:
            self._observed_unsub()
            self._observed_unsub = None
        # Cancel any in-flight flow samplers so a reload/unload can't leak a timer.
        for zone_id in list(self._observed_meters()):
            self._observed_cancel_meter(zone_id)
        self._observed_on_since = {}
        self._observed_entities = frozenset()

    @callback
    def _observed_state_changed(self, event: Event) -> None:
        """Track a linked valve opening/closing and credit external runs."""
        entity_id = event.data.get("entity_id")
        zone_id = self._observed_zone_by_entity.get(entity_id)
        if zone_id is None:
            return
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")
        new_on = new_state is not None and new_state.state in _ON_STATES
        old_on = old_state is not None and old_state.state in _ON_STATES

        if new_on and not old_on:
            # Valve just opened. Ignore if Smart Irrigation itself opened it —
            # the runner already credits the bucket for its own runs. The marker
            # window is taken when the run is dispatched, which for a queued
            # OpenSprinkler station is well before the water; the in-flight lookup
            # covers that gap because the run record exists from dispatch.
            #
            # Checked for every mode rather than only for stations, because it
            # costs nothing to: everywhere else the marker is taken with the run's
            # own length (_note_si_valve run_seconds + margin) and so already
            # spans the whole run, and _active_runs / the distributor's
            # active_cycle are live for exactly that window too.
            if self.zone_run_in_flight(zone_id) or self.hass.loop.time() < (
                self._si_driven_until.get(zone_id, 0.0)
            ):
                _LOGGER.debug(
                    "Observed watering: zone %s opened by Smart Irrigation — not tracking",
                    zone_id,
                )
                return
            self._observed_on_since[zone_id] = dt_util.utcnow()
            _LOGGER.debug("Observed watering: zone %s valve opened (external)", zone_id)
            # Flow-sensor zones: start measuring the external run's real flow so the
            # close edge credits the MEASURED volume, not time × throughput (which a
            # valve stuck reporting open inflates without bound).
            zone = self.store.get_zone(zone_id) or {}
            if zone.get(const.ZONE_FLOW_SENSOR):
                # Start the sampler SYNCHRONOUSLY (its body is non-blocking) so a
                # rapid open->close flap can't close before a scheduled start ran,
                # which would leak a meter+timer and miss the measured credit.
                self._observed_start_flow_sampling(zone)
        elif old_on and not new_on:
            started = self._observed_on_since.pop(zone_id, None)
            # Finalise the sampler BEFORE the started-None early return so an
            # untracked close (SI-driven, or on-at-subscribe) can never leak an
            # in-flight sampler. Returns (None, False) when there was none.
            measured, sensor_present = self._observed_finish_flow(zone_id)
            if started is None:
                # We weren't tracking this run (SI-driven, or it was already on
                # when we subscribed).
                return
            seconds = (dt_util.utcnow() - started).total_seconds()
            self.hass.async_create_task(
                self._credit_observed_watering(
                    zone_id, seconds, measured_l=measured, sensor_present=sensor_present
                )
            )

    # --- Measured-flow sampling (mirror of the self-closing sampler) --------

    def _observed_meters(self) -> dict:
        """Per-zone in-flight flow meters: {zone_id: (meter, cancel, open_l, started)}."""
        m = getattr(self, "_observed_meters_state", None)
        if m is None:
            m = self._observed_meters_state = {}
        return m

    def _observed_cancel_meter(self, zone_id) -> None:
        """Cancel and drop a zone's in-flight flow sampler, if any (else a no-op)."""
        entry = self._observed_meters().pop(zone_id, None)
        if entry is not None:
            entry[1]()  # the cancel handle

    def _observed_start_flow_sampling(self, zone: dict) -> None:
        """Start NON-blocking interval sampling of an external run's flow_sensor.

        Mirrors :meth:`_sc_start_flow_sampling`: build a per-zone FlowMeter (counter
        type resolved from the stored streak), seed it at the valve-open reading and
        poll every ``FLOW_POLL_INTERVAL`` seconds; :meth:`_observed_finish_flow`
        finalises it on close. No-op when the zone has no flow_sensor. Single-flight:
        a re-open cancels a prior in-flight sampler for the same zone first.

        Synchronous (its body only reads state and installs a timer): the open-edge
        callback calls it directly, so it cannot race a same-batch close. Unlike
        self-closing's sampler this is not a coroutine — it is never awaited.
        """
        sensor = zone.get(const.ZONE_FLOW_SENSOR)
        if not sensor:
            return
        zone_id = zone.get(const.ZONE_ID)
        self._observed_cancel_meter(zone_id)  # single-flight: drop any prior sampler
        sample = self._read_flow_sample(sensor)
        meter, open_start_l = self._flow_build_meter(zone, sample)  # seeds at open
        started = dt_util.utcnow()

        async def _tick(now):
            self._observed_sample_flow(zone_id, (now - started).total_seconds())

        cancel = async_track_time_interval(
            self.hass, _tick, timedelta(seconds=const.FLOW_POLL_INTERVAL)
        )
        self._observed_meters()[zone_id] = (meter, cancel, open_start_l, started)

    def _observed_sample_flow(self, zone_id, at: float) -> None:
        """Feed the in-flight meter one reading at monotonic ``at`` (also the test seam)."""
        entry = self._observed_meters().get(zone_id)
        if not entry:
            return
        meter = entry[0]
        zone = self.store.get_zone(zone_id) or {}
        sample = self._read_flow_sample(zone.get(const.ZONE_FLOW_SENSOR))
        if sample is not None:
            meter.sample(*sample, at=at)

    def _observed_finish_flow(self, zone_id):
        """Cancel sampling; return ``(measured_l | None, sensor_present)``.

        Unlike self-closing (:meth:`_sc_finish_flow`, which collapses a ``0.0``
        live-but-dry meter to ``None`` so the caller keeps its time-based volume),
        observed returns ``0.0`` AS ``0.0`` — a valve that reported ``open`` but
        delivered no measurable flow must credit ZERO, not fall back to a time
        estimate (the phantom-open incident). ``None`` means the sensor produced no
        numeric reading at all (dead/misconfigured) → the caller falls back to the
        capped time estimate and flags the sensor.

        observed deliberately does NOT persist cross-run learning (``flow_last_end`` /
        ``flow_reset_streak``): interleaved external opens would poison the SI
        runner's clean-sequence convergence. It only CONSUMES the learned counter
        type via :meth:`_flow_build_meter`. (Distributor precedent, irrigation.py.)
        """
        entry = self._observed_meters().pop(zone_id, None)
        if not entry:
            return None, False
        meter, cancel, _open_start_l, started = entry
        cancel()
        zone = self.store.get_zone(zone_id) or {}
        sensor = zone.get(const.ZONE_FLOW_SENSOR)
        final = self._read_flow_sample(sensor)
        if final is not None:
            meter.sample(*final, at=(dt_util.utcnow() - started).total_seconds())
        d = meter.delivered()
        # 0.0 AND a mid-run reset observed = a hold-until-reset (per_run) counter that
        # was resolved as ``lifetime`` (observed never persists the learned streak), so
        # the reset read like a glitch and nothing was credited despite real flow.
        # Report it as ``None`` (dead/unusable measurement) so the caller falls back to
        # the capped time estimate, NOT as 0.0 (which credits zero). A genuine
        # phantom-open dry valve never trips saw_reset, so the phantom-open fix stands.
        if d == 0.0 and meter.saw_reset():
            return None, bool(sensor)
        return d, bool(sensor)

    def _observed_flag_dead_sensor(self, zone_id, sensor) -> None:
        """Surface a flow-sensor zone with no usable measurement on an external run.

        Reached when :meth:`_observed_finish_flow` returns ``None`` — either the sensor
        gave no numeric reading (dead/misconfigured) or it reset mid-run as a mis-typed
        per_run counter. Mirrors the self-closing dead-sensor handling
        (:meth:`_sc_finish_flow`): the 15-s polls are DEBUG, so this would otherwise
        silently degrade an observed run to the time-based estimate. Warn ONCE per run
        so it is visible. Log-only by design — a zone has no per-run transient problem
        flag, and self-closing does the same.
        """
        _LOGGER.warning(
            "Observed watering: zone %s flow sensor '%s' produced no usable "
            "measurement this external run; credited the capped time-based estimate "
            "instead",
            zone_id,
            sensor,
        )

    def _observed_capped_seconds(self, zone: dict, seconds: float) -> float:
        """Bound external-run seconds at maximum_duration + margin.

        An external open can be as long as a stuck-open valve is willing to
        report; SI would never run this valve longer than its maximum_duration,
        so an observed run credits no more than that (plus a small margin for a
        legitimate run finishing just past the cap). See OBSERVED_CAP_MARGIN_SECONDS.
        """
        max_dur = zone.get(const.ZONE_MAXIMUM_DURATION)
        # `< 0` as well as falsy: a negative maximum_duration (hand-edited store) would
        # otherwise yield a NEGATIVE cap -> negative volume -> a credit that DRAINS the
        # bucket. Treat it as unset, mirroring the SI calc path (calculation.py).
        if not max_dur or max_dur < 0:
            max_dur = const.CONF_DEFAULT_MAXIMUM_DURATION
        return min(float(seconds), float(max_dur) + const.OBSERVED_CAP_MARGIN_SECONDS)

    async def _credit_observed_watering(
        self,
        zone_id: int,
        seconds: float,
        measured_l: float | None = None,
        sensor_present: bool = False,
    ) -> None:
        """Credit a zone's bucket for an externally-driven run of ``seconds``.

        Needs a size and a throughput. On a flow-sensor zone the applied depth
        comes from the MEASURED volume (``measured_l``, from the open/close flow
        sampler; ``sensor_present`` says the zone has a sensor); otherwise, and
        when the sensor gave no reading, it is estimated from run time × configured
        throughput. Either way the counted seconds are capped at the zone's
        maximum_duration + margin (:meth:`_observed_capped_seconds`) so a valve
        stuck reporting ``open`` cannot book unbounded water, and the measured
        volume is itself capped at that time ceiling. The credited depth is the
        actual applied depth (litres / m²), NOT divided by the zone multiplier:
        external water genuinely raised soil moisture by that depth, unlike an SI
        timed run whose duration is inflated by the multiplier. The bucket can rise
        into surplus (capped at maximum_bucket) — unlike an SI run, external
        watering can legitimately overshoot the deficit.
        """
        if seconds <= 0:
            return
        zone = self.store.get_zone(zone_id)
        if zone is None:
            return
        size = zone.get(const.ZONE_SIZE) or 0.0
        throughput = zone.get(const.ZONE_THROUGHPUT) or 0.0
        if size <= 0 or throughput <= 0:
            _LOGGER.debug(
                "Observed watering: zone %s missing size/throughput — skipped", zone_id
            )
            return

        ha_metric = self.hass.config.units is METRIC_SYSTEM
        size_m2 = (
            size
            if ha_metric
            else convert_between(const.UNIT_SQ_FT, const.UNIT_M2, size)
        )
        tput_lpm = (
            throughput
            if ha_metric
            else convert_between(const.UNIT_GPM, const.UNIT_LPM, throughput)
        )

        # Cap the counted seconds: an external run credits no more than SI itself
        # would run this valve (see OBSERVED_CAP_MARGIN_SECONDS). Bounds the
        # time-based volume AND is the sanity ceiling on measured flow.
        capped_s = self._observed_capped_seconds(zone, seconds)
        time_volume_l = tput_lpm * (capped_s / 60.0)

        # Route the credit:
        #  * flow sensor + a reading  -> the MEASURED volume, floored at 0 and capped
        #    at the time ceiling. measured may be 0.0 (a valve that reported open but
        #    delivered nothing — the phantom-open incident) -> credit ZERO. The floor
        #    stops a net-negative rate reading (backflow/sign glitch) DRAINING the
        #    bucket; the ceiling stops a sensor stuck at a constant nonzero reading
        #    booking more than a nameplate run for the same (capped) window.
        #  * flow sensor + NO usable measurement -> dead sensor, or a reset counter we
        #    could not measure; fall back to the capped time estimate and surface it.
        #  * no flow sensor           -> the capped time estimate.
        if sensor_present and measured_l is not None:
            volume_l = min(max(0.0, float(measured_l)), time_volume_l)
        elif sensor_present and measured_l is None:
            volume_l = time_volume_l
            self._observed_flag_dead_sensor(zone_id, zone.get(const.ZONE_FLOW_SENSOR))
        else:
            volume_l = time_volume_l
        applied_mm = volume_l / size_m2  # litres / m² == mm
        applied_native = (
            applied_mm
            if ha_metric
            else convert_between(const.UNIT_MM, const.UNIT_INCH, applied_mm)
        )

        old_bucket = zone.get(const.ZONE_BUCKET) or 0.0
        new_bucket = old_bucket + applied_native
        max_bucket = zone.get(const.ZONE_MAXIMUM_BUCKET)
        if max_bucket is not None and new_bucket > max_bucket:
            new_bucket = float(max_bucket)

        # Persistent, visible record of the external run (survives later bucket
        # changes, unlike the bucket credit). add_to_total credits the estimated
        # litres into the zone's usage total. Placed before the bucket update so
        # the bucket write stays the method's final async_update_zone call.
        await self._record_run(
            zone_id,
            result=const.RUN_RESULT_OBSERVED,
            volume_l=volume_l,
            actual_s=round(capped_s),
            trigger=const.RUN_TRIGGER_OBSERVED,
            add_to_total=True,
        )
        extra = {const.ZONE_LAST_IRRIGATION: dt_util.now()}
        # REGEL-8 sibling of irrigation.py::_stamp_run_finalized (self-closing +
        # distributor): an observed run that leaves an AUTOMATIC zone satisfied
        # (bucket back to >= 0) must also reset the displayed Duration, matching
        # the store's bucket==0 -> duration 0 shortcut. External water usually
        # overshoots the deficit, so new_bucket lands POSITIVE (not exactly 0) and
        # the store shortcut alone would miss it — the same stale-"Duration" the
        # self-closing/distributor paths had. Gated on automatic to leave a manual
        # zone's Duration untouched, exactly like the shortcut and the helper.
        # Folded into async_write_watered_bucket's extra_changes so the credit is
        # still booked at its own timestamp (v08.06 mid-window replay, #77).
        # siehe test_experimental_features.py::test_observed_credit_zeroes_duration_when_satisfied
        if zone.get(const.ZONE_STATE) == const.ZONE_STATE_AUTOMATIC and new_bucket >= 0:
            extra[const.ZONE_DURATION] = 0
        await self.async_write_watered_bucket(zone_id, new_bucket, extra)
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
        _LOGGER.info(
            "Observed watering: zone %s ran %.0fs externally → +%.2f mm, "
            "bucket %.3f → %.3f",
            zone_id,
            seconds,
            applied_mm,
            old_bucket,
            new_bucket,
        )
