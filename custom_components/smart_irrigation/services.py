"""Service registration and handlers for the Smart Irrigation integration.

Extracted from __init__.py (Phase C1). The handlers live on a mixin that the
SmartIrrigationCoordinator inherits, so their bodies are unchanged — they still
use ``self`` to reach coordinator state (store, hass, calc/update helpers, the
schedule/IU managers). ``async_register_services`` wires each HA service
to the matching handler.
"""

import logging
import re
from datetime import datetime

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send

from . import const
from .const import SmartIrrigationError

_LOGGER = logging.getLogger(__name__)


class ServiceHandlersMixin:
    """Service-call handlers for SmartIrrigationCoordinator.

    Mixed into the coordinator; methods use ``self`` to reach coordinator state.
    """

    async def handle_calculate_all_zones(self, call):
        """Calculate all zones."""
        _LOGGER.info("Calculate all zones service called")
        await self._async_calculate_all()

    async def handle_calculate_zone(self, call):
        """Calculate specific zone."""
        if const.SERVICE_ENTITY_ID in call.data:
            for entity in call.data[const.SERVICE_ENTITY_ID]:
                _LOGGER.info("Calculate zone service called for zone %s", entity)
                # find entity zone id and call calculate on the zone
                state = self.hass.states.get(entity)
                if state:
                    # find zone_id for zone with name
                    zone_id = state.attributes.get(const.ZONE_ID)
                    if zone_id is not None:
                        data = {const.ATTR_CALCULATE: const.ATTR_CALCULATE}
                        await self.async_update_zone_config(zone_id=zone_id, data=data)

    async def handle_update_all_zones(self, call):
        """Update all zones."""
        _LOGGER.info("Update all zones service called")
        await self._async_update_all()

    async def handle_update_zone(self, call):
        """Update specific zone."""
        if const.SERVICE_ENTITY_ID in call.data:
            for entity in call.data[const.SERVICE_ENTITY_ID]:
                _LOGGER.info("Update zone service called for zone %s", entity)
                # find entity zone id and call update on the zone
                state = self.hass.states.get(entity)
                if state:
                    # find zone_id for zone with name
                    zone_id = state.attributes.get(const.ZONE_ID)
                    if zone_id is not None:
                        data = {}
                        data[const.ATTR_UPDATE] = const.ATTR_UPDATE
                        await self.async_update_zone_config(zone_id=zone_id, data=data)

    async def handle_reset_bucket(self, call):
        """Reset a specific zone bucket to 0."""
        if const.SERVICE_ENTITY_ID in call.data:
            eid = call.data[const.SERVICE_ENTITY_ID]
            if not isinstance(eid, list):
                eid = [call.data[const.SERVICE_ENTITY_ID]]
            for entity in eid:
                _LOGGER.info("Reset bucket service called for zone %s", entity)
                # find entity zone id and call calculate on the zone
                state = self.hass.states.get(entity)
                if state:
                    # find zone_id for zone with name
                    zone_id = state.attributes.get(const.ZONE_ID)
                    if zone_id is not None:
                        data = {}
                        data[const.ATTR_SET_BUCKET] = {}
                        data[const.ATTR_NEW_BUCKET_VALUE] = 0
                        await self.async_update_zone_config(zone_id=zone_id, data=data)

    async def handle_reset_all_buckets(self, call):
        """Reset all buckets to 0."""
        _LOGGER.info("Reset all buckets service called")
        await self._async_set_all_buckets(0)

    async def handle_set_all_buckets(self, call):
        """Reset all buckets to new value."""
        if const.ATTR_NEW_BUCKET_VALUE in call.data:
            new_value = call.data[const.ATTR_NEW_BUCKET_VALUE]
            _LOGGER.info("Set all buckets service called, new value: %s", new_value)
            await self._async_set_all_buckets(new_value)

    async def handle_set_zone(self, call):
        """Reset a specific zone state to new value."""
        if const.SERVICE_ENTITY_ID not in call.data:
            return

        eid = call.data[const.SERVICE_ENTITY_ID]
        if not isinstance(eid, list):
            eid = [call.data[const.SERVICE_ENTITY_ID]]

        data = call.data.copy()
        data.pop(const.SERVICE_ENTITY_ID)

        for entity in eid:
            _LOGGER.info("Set zone data service called with zone %s", entity)

            # find entity zone id and call calculate on the zone
            state = self.hass.states.get(entity)
            if not state:
                raise SmartIrrigationError(f"No state found for entity {entity}")

            # find zone_id for zone with name
            zone_id = state.attributes.get(const.ZONE_ID)
            if zone_id is None:
                raise SmartIrrigationError("No zone_id found in state attributes.")

            zone = self.store.get_zone(zone_id)
            zone_data = {}
            count = 0
            for v in data:
                if (
                    v not in const.LIST_SET_ZONE_ALLOWED_ARGS
                    and v != const.SERVICE_ENTITY_ID
                ):
                    raise SmartIrrigationError(f"Argument ({v}) is not allowed")

                if (
                    v == const.ATTR_NEW_DURATION_VALUE
                    and zone.get(const.ZONE_STATE) != const.ZONE_STATE_MANUAL
                ):
                    raise SmartIrrigationError(
                        "Can only set duration if zone state is set to manual."
                    )
                if v == const.ATTR_NEW_BUCKET_VALUE and data[v] > zone.get(
                    const.ZONE_MAXIMUM_BUCKET
                ):
                    raise SmartIrrigationError(
                        "Bucket size is above maximmum bucket allowed value."
                    )
                if v == const.ATTR_NEW_STATE_VALUE and data[v] in const.ZONE_STATE:
                    raise SmartIrrigationError(
                        f"Invalid value ({data[v]}) for zone state."
                    )

                m = re.match("^new_(.+)_value$", v)
                if m:
                    zone_data[m.group(1)] = data[v]
                    _LOGGER.info("Setting value for %s", m.group(1))
                    count += 1

            if count == 0:
                raise SmartIrrigationError("No valid parameter provided")

            if count > 0:
                await self.store.async_update_zone(zone_id, zone_data)
                async_dispatcher_send(
                    self.hass,
                    const.DOMAIN + "_config_updated",
                    zone_id,
                )

    async def handle_set_all_multipliers(self, call):
        """Reset all multipliers to new value."""
        if const.ATTR_NEW_MULTIPLIER_VALUE in call.data:
            new_value = call.data[const.ATTR_NEW_MULTIPLIER_VALUE]
            _LOGGER.info("Set all multipliers service called, new value: %s", new_value)
            await self._async_set_all_multipliers(new_value)

    async def handle_clear_weatherdata(self, call):
        """Clear all collected weatherdata."""
        await self._async_clear_all_weatherdata()

    async def handle_generate_watering_calendar(self, call):
        """Generate watering calendar service handler."""
        zone_id = call.data.get("zone_id")

        if zone_id is not None:
            zone_id = int(zone_id)

        _LOGGER.info("Generate watering calendar service called for zone %s", zone_id)

        try:
            calendar_data = await self.async_generate_watering_calendar(zone_id)

            # Store the result in hass.data for retrieval by automation
            if "watering_calendars" not in self.hass.data[const.DOMAIN]:
                self.hass.data[const.DOMAIN]["watering_calendars"] = {}

            self.hass.data[const.DOMAIN]["watering_calendars"][
                "last_generated"
            ] = calendar_data

            # Fire an event with the calendar data
            self.hass.bus.fire(
                f"{const.DOMAIN}_watering_calendar_generated",
                {
                    "zone_id": zone_id,
                    "calendar_data": calendar_data,
                    "generated_at": datetime.now().isoformat(),
                },
            )

            _LOGGER.info(
                "Watering calendar generated successfully for %s zones",
                len(calendar_data),
            )

        except Exception as e:
            _LOGGER.error("Failed to generate watering calendar: %s", e)
            self.hass.bus.fire(
                f"{const.DOMAIN}_watering_calendar_error",
                {
                    "zone_id": zone_id,
                    "error": str(e),
                    "generated_at": datetime.now().isoformat(),
                },
            )

    # Operational controls (WS-5)
    async def handle_set_rain_delay(self, call):
        """Pause automatic irrigation until a datetime (or for N hours)."""
        until = call.data.get(const.ATTR_RAIN_DELAY_UNTIL)
        hours = call.data.get(const.ATTR_RAIN_DELAY_HOURS)
        if until is not None:
            # call.data may carry a datetime (cv.datetime) — normalise to ISO.
            iso = until.isoformat() if hasattr(until, "isoformat") else str(until)
            await self.async_set_rain_delay(iso)
        elif hours is not None:
            await self.async_delay_hours(float(hours))
        else:
            raise SmartIrrigationError(
                "set_rain_delay requires either 'until' or 'hours'"
            )

    async def handle_clear_rain_delay(self, call):
        """Resume automatic irrigation (clear any active hold)."""
        await self.async_clear_rain_delay()

    async def handle_run_zone(self, call):
        """Run a zone for an explicit duration (minutes), bypassing the calc."""
        if const.SERVICE_ENTITY_ID not in call.data:
            return
        duration = call.data.get(const.ATTR_DURATION_MINUTES)
        if duration is None:
            raise SmartIrrigationError("run_zone requires a 'duration' (minutes)")
        eid = call.data[const.SERVICE_ENTITY_ID]
        if not isinstance(eid, list):
            eid = [eid]
        for entity in eid:
            _LOGGER.info("Run zone service called for %s (%s min)", entity, duration)
            state = self.hass.states.get(entity)
            if not state:
                raise SmartIrrigationError(f"No state found for entity {entity}")
            # The main zone sensor exposes the zone id as "id"; the per-zone
            # button / binary_sensor entities expose it as "zone_id". Accept
            # either so any of a zone's entities can be used as the target.
            zone_id = state.attributes.get(const.ZONE_ID)
            if zone_id is None:
                zone_id = state.attributes.get("zone_id")
            if zone_id is None:
                raise SmartIrrigationError(
                    f"Entity {entity} is not a Smart Irrigation zone entity "
                    "(no zone id in its attributes)."
                )
            await self.async_run_zone(zone_id, float(duration))

    async def handle_stop_zone(self, call):
        """Stop an in-progress run for a zone (and turn its valve off)."""
        if const.SERVICE_ENTITY_ID not in call.data:
            return
        eid = call.data[const.SERVICE_ENTITY_ID]
        if not isinstance(eid, list):
            eid = [eid]
        for entity in eid:
            _LOGGER.info("Stop zone service called for %s", entity)
            state = self.hass.states.get(entity)
            if not state:
                raise SmartIrrigationError(f"No state found for entity {entity}")
            # Accept either the main zone sensor ("id") or a per-zone
            # button / binary_sensor ("zone_id"), like run_zone.
            zone_id = state.attributes.get(const.ZONE_ID)
            if zone_id is None:
                zone_id = state.attributes.get("zone_id")
            if zone_id is None:
                raise SmartIrrigationError(
                    f"Entity {entity} is not a Smart Irrigation zone entity "
                    "(no zone id in its attributes)."
                )
            await self.async_stop_zone(zone_id)

    # Enhanced Scheduling Service Handlers
    async def handle_create_recurring_schedule(self, call):
        """Create recurring schedule service handler."""
        schedule_data = dict(call.data)
        _LOGGER.info(
            "Create recurring schedule service called: %s",
            schedule_data.get("name", "Unnamed"),
        )

        try:
            await self.recurring_schedule_manager.async_create_schedule(schedule_data)
            _LOGGER.info("Successfully created recurring schedule")
        except Exception as e:
            _LOGGER.error("Failed to create recurring schedule: %s", e)
            raise

    async def handle_update_recurring_schedule(self, call):
        """Update recurring schedule service handler."""
        schedule_id = call.data.get("schedule_id")
        schedule_data = dict(call.data)
        schedule_data.pop("schedule_id", None)

        _LOGGER.info("Update recurring schedule service called for ID: %s", schedule_id)

        try:
            await self.recurring_schedule_manager.async_update_schedule(
                schedule_id, schedule_data
            )
            _LOGGER.info("Successfully updated recurring schedule")
        except Exception as e:
            _LOGGER.error("Failed to update recurring schedule: %s", e)
            raise

    async def handle_delete_recurring_schedule(self, call):
        """Delete recurring schedule service handler."""
        schedule_id = call.data.get("schedule_id")

        _LOGGER.info("Delete recurring schedule service called for ID: %s", schedule_id)

        try:
            await self.recurring_schedule_manager.async_delete_schedule(schedule_id)
            _LOGGER.info("Successfully deleted recurring schedule")
        except Exception as e:
            _LOGGER.error("Failed to delete recurring schedule: %s", e)
            raise


@callback
def async_register_services(hass: HomeAssistant):
    """Register services used by Smart Irrigation integration."""

    coordinator = hass.data[const.DOMAIN]["coordinator"]

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_CALCULATE_ALL_ZONES,
        coordinator.handle_calculate_all_zones,
    )
    hass.services.async_register(
        const.DOMAIN, const.SERVICE_CALCULATE_ZONE, coordinator.handle_calculate_zone
    )

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_UPDATE_ALL_ZONES,
        coordinator.handle_update_all_zones,
    )
    hass.services.async_register(
        const.DOMAIN, const.SERVICE_UPDATE_ZONE, coordinator.handle_update_zone
    )
    hass.services.async_register(
        const.DOMAIN, const.SERVICE_RESET_BUCKET, coordinator.handle_reset_bucket
    )

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_RESET_ALL_BUCKETS,
        coordinator.handle_reset_all_buckets,
    )

    hass.services.async_register(
        const.DOMAIN, const.SERVICE_SET_BUCKET, coordinator.handle_set_zone
    )

    hass.services.async_register(
        const.DOMAIN, const.SERVICE_SET_ALL_BUCKETS, coordinator.handle_set_all_buckets
    )

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_CLEAR_WEATHERDATA,
        coordinator.handle_clear_weatherdata,
    )

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_SET_ALL_MULTIPLIERS,
        coordinator.handle_set_all_multipliers,
    )

    hass.services.async_register(
        const.DOMAIN, const.SERVICE_SET_MULTIPLIER, coordinator.handle_set_zone
    )

    hass.services.async_register(
        const.DOMAIN, const.SERVICE_SET_ZONE, coordinator.handle_set_zone
    )

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_GENERATE_WATERING_CALENDAR,
        coordinator.handle_generate_watering_calendar,
    )

    # Operational controls (WS-5)
    hass.services.async_register(
        const.DOMAIN, const.SERVICE_SET_RAIN_DELAY, coordinator.handle_set_rain_delay
    )
    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_CLEAR_RAIN_DELAY,
        coordinator.handle_clear_rain_delay,
    )
    hass.services.async_register(
        const.DOMAIN, const.SERVICE_RUN_ZONE, coordinator.handle_run_zone
    )
    hass.services.async_register(
        const.DOMAIN, const.SERVICE_STOP_ZONE, coordinator.handle_stop_zone
    )

    # Enhanced scheduling services
    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_CREATE_RECURRING_SCHEDULE,
        coordinator.handle_create_recurring_schedule,
    )

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_UPDATE_RECURRING_SCHEDULE,
        coordinator.handle_update_recurring_schedule,
    )

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_DELETE_RECURRING_SCHEDULE,
        coordinator.handle_delete_recurring_schedule,
    )

    # Distributor services (Gardena water distributor, Plan D)
    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_DISTRIBUTOR_SET_OUTLET,
        coordinator.handle_distributor_set_outlet,
    )
    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_DISTRIBUTOR_RESYNC_HOME,
        coordinator.handle_distributor_resync_home,
    )
    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_DISTRIBUTOR_TEST_RUN,
        coordinator.handle_distributor_test_run,
    )
    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_DISTRIBUTOR_RUN_NOW,
        coordinator.handle_distributor_run_now,
    )
