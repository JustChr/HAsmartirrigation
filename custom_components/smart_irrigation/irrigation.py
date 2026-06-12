"""Irrigation execution for the Smart Irrigation integration.

Extracted from __init__.py (Phase C2). The runner methods live on a mixin the
SmartIrrigationCoordinator inherits, so their bodies are unchanged — they still
use ``self`` to reach coordinator state (store, hass, skip-condition checks,
duration helpers). ``async_irrigate_now`` is the entry point that dispatches to
the rotating / sequential / parallel strategies based on config.
"""

import asyncio
import logging

import homeassistant.util.dt as dt_util
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .helpers import convert_between

_LOGGER = logging.getLogger(__name__)

# How long (seconds) a zone stays flagged as "Smart Irrigation is driving this
# valve" after the runner opens it, so the experimental observed-watering
# observer does not also credit the bucket for a run SI already accounts for.
SI_VALVE_SUPPRESS_WINDOW = 30


class IrrigationRunnerMixin:
    """Irrigation execution strategies for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    def _note_si_valve(self, zone_id) -> None:
        """Flag that SI itself is opening this zone's valve.

        The observed-watering observer (ObservedWateringMixin) checks this so it
        only credits the bucket for runs SI did NOT start (manual taps,
        automations). No-op unless that experimental feature is wired up.
        """
        until = getattr(self, "_si_driven_until", None)
        if until is not None:
            until[int(zone_id)] = self.hass.loop.time() + SI_VALVE_SUPPRESS_WINDOW

    @staticmethod
    def _zone_target_bucket(zone: dict) -> float:
        """Bucket level (display units) a completed run should leave the zone at.

        0.0 normally (full replenish); the rain-covered remainder when the
        experimental forecast-weighting feature trimmed the last calculation.
        """
        return zone.get(const.ZONE_IRRIGATION_TARGET_BUCKET) or 0.0

    @callback
    async def _irrigate_linked_entities(self, zone_ids=None):
        """Directly control linked valve/switch entities for zones needing irrigation.

        ``zone_ids`` optionally restricts to a schedule's target zones (an
        iterable of ids, or None/"all" for every eligible zone).
        """
        zones = await self.store.async_get_zones()
        sequencing = self.store.config.zone_sequencing
        want_all = zone_ids is None or zone_ids == "all"
        target = None if want_all else {int(z) for z in zone_ids}

        zones_to_irrigate = [
            z
            for z in zones
            if z.get(const.ZONE_LINKED_ENTITY)
            and (z.get(const.ZONE_DURATION) or 0) > 0
            and z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
            and (z.get(const.ZONE_BUCKET) or 0)
            < (z.get(const.ZONE_BUCKET_THRESHOLD) or 0)
            and (target is None or int(z.get(const.ZONE_ID)) in target)
        ]

        if not zones_to_irrigate:
            _LOGGER.debug(
                "No zones with linked entities and duration > 0 to irrigate directly"
            )
            return

        if sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL:
            asyncio.create_task(self._irrigate_zones_sequential(zones_to_irrigate))
        elif sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            asyncio.create_task(self._irrigate_zones_rotating(zones_to_irrigate))
        else:
            await self._irrigate_zones_parallel(zones_to_irrigate)

    @staticmethod
    def _flow_rate_to_l_per_min(value: float, unit: str) -> float:
        """Convert a flow sensor reading to L/min for volume accumulation."""
        u = (unit or "").lower().strip()
        if u in ("l/h", "liter/h", "liter/hour", "liters/hour", "liters/h"):
            return value / 60.0
        if u in ("m³/h", "m3/h", "m³/hour", "m3/hour"):
            return value * 1000.0 / 60.0
        if u in ("m³/min", "m3/min"):
            return value * 1000.0
        if u in ("gal/min", "gpm", "gallon/min", "gallons/min"):
            return value * 3.785411784
        if u in ("gal/h", "gal/hour", "gallon/h", "gallons/h"):
            return value * 3.785411784 / 60.0
        return value  # assume L/min

    async def _irrigate_zone_with_flow_meter(self, zone: dict, entity_id: str) -> None:
        """Irrigate a zone using a flow sensor: stop when target volume is delivered."""
        zone_id = zone[const.ZONE_ID]
        size = zone.get(const.ZONE_SIZE) or 0.0
        bucket = zone.get(const.ZONE_BUCKET) or 0.0

        # Post-run target (display units, normally 0). Forecast weighting can set
        # a rain-covered remainder; we then deliver only down to that floor.
        floor_display = self._zone_target_bucket(zone)
        floor_mm = floor_display

        ha_config_is_metric = self.hass.config.units is METRIC_SYSTEM
        if not ha_config_is_metric:
            size = convert_between(const.UNIT_SQ_FT, const.UNIT_M2, size)
            bucket = convert_between(const.UNIT_INCH, const.UNIT_MM, bucket)
            floor_mm = convert_between(const.UNIT_INCH, const.UNIT_MM, floor_display)

        target_volume = size * max(0.0, floor_mm - bucket)
        safety_timeout = zone.get(const.ZONE_MAXIMUM_DURATION) or 14400

        _LOGGER.info(
            "Flow meter irrigation: zone %s target %.1f L (sensor: %s)",
            zone_id,
            target_volume,
            zone[const.ZONE_FLOW_SENSOR],
        )

        accumulated = await self._irrigate_zone_flow_slot(
            zone, entity_id, safety_timeout, target_volume
        )
        timed_out = accumulated < target_volume

        if timed_out:
            _LOGGER.warning(
                "Zone %s: safety timeout %ss reached (%.2f / %.1f L delivered)",
                zone_id,
                safety_timeout,
                accumulated,
                target_volume,
            )
        else:
            _LOGGER.info(
                "Zone %s: target %.1f L reached (%.2f L delivered)",
                zone_id,
                target_volume,
                accumulated,
            )

        if size > 0:
            actual_mm = accumulated / size
            if not ha_config_is_metric:
                actual_mm = convert_between(const.UNIT_MM, const.UNIT_INCH, actual_mm)
            original_bucket = zone.get(const.ZONE_BUCKET) or 0.0
            new_bucket = min(floor_display, original_bucket + actual_mm)
            await self.store.async_update_zone(
                zone_id,
                {
                    const.ZONE_BUCKET: new_bucket,
                    const.ZONE_LAST_IRRIGATION: dt_util.now(),
                },
            )
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
            _LOGGER.info(
                "Zone %s: bucket updated %.3f → %.3f (%s%.2f mm delivered%s)",
                zone_id,
                original_bucket,
                new_bucket,
                "" if not timed_out else "partial, ",
                actual_mm,
                "" if not timed_out else " — timeout",
            )

    async def _irrigate_zone_flow_slot(
        self,
        zone: dict,
        entity_id: str,
        max_seconds: float,
        remaining_volume: float,
    ) -> float:
        """Open a flow-meter zone for up to max_seconds or until remaining_volume is reached.

        Returns litres delivered during this slot.
        """
        flow_sensor = zone[const.ZONE_FLOW_SENSOR]
        zone_id = zone[const.ZONE_ID]
        domain = entity_id.split(".")[0]

        self._note_si_valve(zone_id)
        await self.hass.services.async_call(domain, "turn_on", {"entity_id": entity_id})

        accumulated = 0.0
        elapsed = 0.0

        while elapsed < max_seconds and accumulated < remaining_volume:
            await asyncio.sleep(const.FLOW_POLL_INTERVAL)
            elapsed += const.FLOW_POLL_INTERVAL

            state = self.hass.states.get(flow_sensor)
            if state is None or state.state in ("unavailable", "unknown"):
                _LOGGER.warning(
                    "Flow sensor '%s' unavailable during rotating slot of zone %s",
                    flow_sensor,
                    zone_id,
                )
                continue
            try:
                raw = float(state.state)
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "Flow sensor '%s' non-numeric state '%s'", flow_sensor, state.state
                )
                continue

            unit = state.attributes.get("unit_of_measurement", "L/min")
            rate = self._flow_rate_to_l_per_min(raw, unit)
            accumulated += rate * const.FLOW_POLL_INTERVAL / 60.0
            _LOGGER.debug(
                "Zone %s slot: %.2f L/min → %.2f / %.2f L",
                zone_id,
                rate,
                accumulated,
                remaining_volume,
            )

        await self.hass.services.async_call(
            domain, "turn_off", {"entity_id": entity_id}
        )
        return accumulated

    async def _irrigate_zones_rotating(self, zones: list):
        """Irrigate all zones (timed and flow-meter) in a unified rotation.

        Each zone gets at most max_consecutive_duration per turn.
        When min_absorption_time > 0, the loop waits before returning to a zone.
        """
        max_slot = (
            max(1, (self.store.config.zone_sequencing_max_consecutive_duration or 5))
            * 60
        )
        min_absorption = (
            self.store.config.zone_sequencing_min_absorption_time or 0
        ) * 60

        timed_zones = [z for z in zones if not z.get(const.ZONE_FLOW_SENSOR)]
        flow_zones = [z for z in zones if z.get(const.ZONE_FLOW_SENSOR)]

        timed_remaining = {
            z[const.ZONE_ID]: float(z[const.ZONE_DURATION]) for z in timed_zones
        }
        timed_by_id = {z[const.ZONE_ID]: z for z in timed_zones}

        ha_metric = self.hass.config.units is METRIC_SYSTEM
        flow_target: dict = {}
        flow_delivered: dict = {}
        flow_elapsed: dict = {}
        flow_size_m2: dict = {}
        flow_bucket: dict = {}
        flow_floor: dict = {}
        flow_by_id: dict = {}

        for z in flow_zones:
            zid = z[const.ZONE_ID]
            raw_size = z.get(const.ZONE_SIZE) or 0.0
            raw_bucket = z.get(const.ZONE_BUCKET) or 0.0
            raw_floor = self._zone_target_bucket(z)
            s_m2 = (
                raw_size
                if ha_metric
                else convert_between(const.UNIT_SQ_FT, const.UNIT_M2, raw_size)
            )
            b_mm = (
                raw_bucket
                if ha_metric
                else convert_between(const.UNIT_INCH, const.UNIT_MM, raw_bucket)
            )
            floor_mm = (
                raw_floor
                if ha_metric
                else convert_between(const.UNIT_INCH, const.UNIT_MM, raw_floor)
            )
            flow_target[zid] = s_m2 * max(0.0, floor_mm - b_mm)
            flow_delivered[zid] = 0.0
            flow_elapsed[zid] = 0.0
            flow_size_m2[zid] = s_m2
            flow_bucket[zid] = raw_bucket
            flow_floor[zid] = raw_floor
            flow_by_id[zid] = z
            _LOGGER.info(
                "Rotating irrigation: flow zone %s target %.1f L", zid, flow_target[zid]
            )

        zone_order = [z[const.ZONE_ID] for z in timed_zones + flow_zones]
        last_finish: dict = {}
        loop = asyncio.get_running_loop()

        def _timed_done(zid):
            return timed_remaining.get(zid, 0) <= 0

        def _flow_done(zid):
            safety = flow_by_id[zid].get(const.ZONE_MAXIMUM_DURATION) or 14400
            return (
                flow_delivered[zid] >= flow_target[zid] or flow_elapsed[zid] >= safety
            )

        def _all_done():
            return all(_timed_done(z) for z in timed_by_id) and all(
                _flow_done(z) for z in flow_by_id
            )

        while not _all_done():
            for zid in zone_order:
                is_flow = zid in flow_by_id
                if is_flow and _flow_done(zid):
                    continue
                if not is_flow and _timed_done(zid):
                    continue

                if min_absorption > 0 and zid in last_finish:
                    wait = min_absorption - (loop.time() - last_finish[zid])
                    if wait > 0:
                        _LOGGER.info(
                            "Rotating irrigation: zone %s absorbing, waiting %.0fs",
                            zid,
                            wait,
                        )
                        await asyncio.sleep(wait)

                if is_flow:
                    z = flow_by_id[zid]
                    entity_id = z[const.ZONE_LINKED_ENTITY]
                    safety = z.get(const.ZONE_MAXIMUM_DURATION) or 14400
                    slot = min(max_slot, safety - flow_elapsed[zid])
                    rem_vol = flow_target[zid] - flow_delivered[zid]
                    _LOGGER.info(
                        "Rotating irrigation: flow zone %s slot %.0fs (%.1f/%.1f L)",
                        zid,
                        slot,
                        flow_delivered[zid],
                        flow_target[zid],
                    )
                    delivered = await self._irrigate_zone_flow_slot(
                        z, entity_id, slot, rem_vol
                    )
                    flow_delivered[zid] += delivered
                    flow_elapsed[zid] += slot
                    _LOGGER.info(
                        "Rotating irrigation: flow zone %s slot done — %.1f/%.1f L total",
                        zid,
                        flow_delivered[zid],
                        flow_target[zid],
                    )
                    if flow_size_m2[zid] > 0:
                        slot_mm = delivered / flow_size_m2[zid]
                        slot_native = (
                            slot_mm
                            if ha_metric
                            else convert_between(
                                const.UNIT_MM, const.UNIT_INCH, slot_mm
                            )
                        )
                        prev_bucket = flow_bucket[zid]
                        new_bucket = min(flow_floor[zid], prev_bucket + slot_native)
                        flow_bucket[zid] = new_bucket
                        await self.store.async_update_zone(
                            zid, {const.ZONE_BUCKET: new_bucket}
                        )
                        _LOGGER.info(
                            "Rotating irrigation: flow zone %s bucket %.3f → %.3f"
                            " (%.2f L this slot)",
                            zid,
                            prev_bucket,
                            new_bucket,
                            delivered,
                        )
                else:
                    z = timed_by_id[zid]
                    entity_id = z[const.ZONE_LINKED_ENTITY]
                    domain = entity_id.split(".")[0]
                    rem = timed_remaining[zid]
                    slot = min(rem, max_slot)
                    _LOGGER.info(
                        "Rotating irrigation: %s for %.0fs (%.0fs remaining after slot)",
                        entity_id,
                        slot,
                        rem - slot,
                    )
                    self._note_si_valve(zid)
                    await self.hass.services.async_call(
                        domain, "turn_on", {"entity_id": entity_id}
                    )
                    await asyncio.sleep(slot)
                    await self.hass.services.async_call(
                        domain, "turn_off", {"entity_id": entity_id}
                    )
                    timed_remaining[zid] -= slot
                    _LOGGER.info("Rotating irrigation: finished slot for %s", entity_id)
                    if timed_remaining[zid] <= 0:
                        # Zone fully irrigated across its slots — replenish bucket.
                        await self._reset_zone_bucket_after_run(zid)

                last_finish[zid] = loop.time()

    async def _reset_zone_bucket_after_run(self, zone_id) -> None:
        """Set a zone's bucket to its post-run target after a completed timed run.

        The duration was computed to deliver exactly the accumulated deficit
        (|bucket|), so once the valve has run for the full duration the deficit
        is replenished and the bucket returns to its target — normally 0, or the
        rain-covered remainder when forecast weighting trimmed this run. The
        flow-meter path does the equivalent based on measured volume; this is the
        timed-run counterpart.
        """
        zone = self.store.get_zone(zone_id) or {}
        target = self._zone_target_bucket(zone)
        await self.store.async_update_zone(
            zone_id,
            {const.ZONE_BUCKET: target, const.ZONE_LAST_IRRIGATION: dt_util.now()},
        )
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)
        _LOGGER.info(
            "Zone %s: bucket set to %.3f after irrigation run", zone_id, target
        )

    async def _irrigate_zones_sequential(self, zones: list):
        """Irrigate zones one after another, skipping zones with no duration."""
        for zone in zones:
            entity_id = zone[const.ZONE_LINKED_ENTITY]
            domain = entity_id.split(".")[0]
            if zone.get(const.ZONE_FLOW_SENSOR):
                _LOGGER.info(
                    "Sequential irrigation: zone %s using flow meter",
                    zone[const.ZONE_ID],
                )
                await self._irrigate_zone_with_flow_meter(zone, entity_id)
            else:
                duration = zone[const.ZONE_DURATION]
                _LOGGER.info(
                    "Sequential irrigation: turning on %s for %s seconds",
                    entity_id,
                    duration,
                )
                self._note_si_valve(zone[const.ZONE_ID])
                await self.hass.services.async_call(
                    domain, "turn_on", {"entity_id": entity_id}
                )
                await asyncio.sleep(duration)
                await self.hass.services.async_call(
                    domain, "turn_off", {"entity_id": entity_id}
                )
                await self._reset_zone_bucket_after_run(zone[const.ZONE_ID])
            _LOGGER.info("Sequential irrigation: finished %s", entity_id)

    async def _irrigate_zones_parallel(self, zones: list):
        """Start all zone entities simultaneously, each turning off after its own duration."""
        for zone in zones:
            entity_id = zone[const.ZONE_LINKED_ENTITY]
            domain = entity_id.split(".")[0]
            if zone.get(const.ZONE_FLOW_SENSOR):
                _LOGGER.info(
                    "Parallel irrigation: zone %s using flow meter", zone[const.ZONE_ID]
                )
                asyncio.create_task(
                    self._irrigate_zone_with_flow_meter(zone, entity_id)
                )
            else:
                duration = zone[const.ZONE_DURATION]
                _LOGGER.info(
                    "Parallel irrigation: turning on %s for %s seconds",
                    entity_id,
                    duration,
                )
                self._note_si_valve(zone[const.ZONE_ID])
                await self.hass.services.async_call(
                    domain, "turn_on", {"entity_id": entity_id}
                )

                async def _turn_off(
                    eid=entity_id, dom=domain, dur=duration, zid=zone[const.ZONE_ID]
                ):
                    await asyncio.sleep(dur)
                    await self.hass.services.async_call(
                        dom, "turn_off", {"entity_id": eid}
                    )
                    _LOGGER.info("Parallel irrigation: turned off %s", eid)
                    await self._reset_zone_bucket_after_run(zid)

                asyncio.create_task(_turn_off())

    async def async_irrigate_now(self, zone_id: str | None = None):
        """Immediately irrigate — bypasses all skip conditions.

        If zone_id is provided, only irrigate that zone.
        Otherwise irrigate all zones that have a linked entity and duration > 0.
        """
        zones = await self.store.async_get_zones()

        if zone_id is not None:
            zones = [z for z in zones if str(z.get(const.ZONE_ID)) == str(zone_id)]

        zones_to_irrigate = [
            z
            for z in zones
            if z.get(const.ZONE_LINKED_ENTITY)
            and (z.get(const.ZONE_DURATION) or 0) > 0
            and z.get(const.ZONE_STATE) != const.ZONE_STATE_DISABLED
        ]

        if not zones_to_irrigate:
            _LOGGER.info("irrigate_now: no zones with linked entity and duration > 0")
            return

        sequencing = self.store.config.zone_sequencing
        if sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL:
            asyncio.create_task(self._irrigate_zones_sequential(zones_to_irrigate))
        elif sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            asyncio.create_task(self._irrigate_zones_rotating(zones_to_irrigate))
        else:
            await self._irrigate_zones_parallel(zones_to_irrigate)
