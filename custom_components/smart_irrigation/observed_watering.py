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

import homeassistant.util.dt as dt_util
from homeassistant.core import Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .helpers import convert_between

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
                entity = zone.get(const.ZONE_LINKED_ENTITY)
                if entity:
                    entity_map[entity] = int(zone.get(const.ZONE_ID))

        entities = frozenset(entity_map)
        # Keep the entity→zone map fresh even on a no-op (a zone id could in
        # principle be reassigned to the same entity string).
        self._observed_zone_by_entity = entity_map
        if entities == self._observed_entities:
            return

        if self._observed_unsub is not None:
            self._observed_unsub()
            self._observed_unsub = None
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
            # the runner already credits the bucket for its own runs.
            if self.hass.loop.time() < self._si_driven_until.get(zone_id, 0.0):
                _LOGGER.debug(
                    "Observed watering: zone %s opened by Smart Irrigation — not tracking",
                    zone_id,
                )
                return
            self._observed_on_since[zone_id] = dt_util.utcnow()
            _LOGGER.debug("Observed watering: zone %s valve opened (external)", zone_id)
        elif old_on and not new_on:
            started = self._observed_on_since.pop(zone_id, None)
            if started is None:
                # We weren't tracking this run (SI-driven, or it was already on
                # when we subscribed).
                return
            seconds = (dt_util.utcnow() - started).total_seconds()
            self.hass.async_create_task(
                self._credit_observed_watering(zone_id, seconds)
            )

    async def _credit_observed_watering(self, zone_id: int, seconds: float) -> None:
        """Credit a zone's bucket for an externally-driven run of ``seconds``.

        Applied depth is estimated from run time × configured throughput, so it
        needs both a size and a throughput. The bucket can rise into surplus
        (capped at maximum_bucket) — unlike an SI run, external watering can
        legitimately overshoot the deficit.
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

        volume_l = tput_lpm * (seconds / 60.0)
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
            actual_s=round(seconds),
            trigger="observed",
            add_to_total=True,
        )
        await self.store.async_update_zone(
            zone_id,
            {
                const.ZONE_BUCKET: new_bucket,
                const.ZONE_LAST_IRRIGATION: dt_util.now(),
            },
        )
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
