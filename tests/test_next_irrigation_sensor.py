"""The next-irrigation sensor's cold-start population.

The entity recomputes only on ``smart_irrigation_schedules_updated``. Its own
add-time refresh is its one other chance, and during a cold start that lands
before ``async_load_schedules`` has put anything in the manager, so the value it
reads is "no schedules" rather than "no schedule yet". Nothing revisited it, and
every zone's Next irrigation read ``unknown`` for the rest of the session.

Guarded here at both ends: the setup path announces the schedules once they are
loaded, and the entity answers that announcement.
"""

from unittest.mock import AsyncMock, Mock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.irrigation_plus import async_setup_entry, const
from custom_components.irrigation_plus.scheduler import RecurringScheduleManager
from custom_components.irrigation_plus.sensor import (
    SmartIrrigationZoneNextIrrigationSensor,
)

ZONE = {const.ZONE_ID: 1, const.ZONE_NAME: "Front"}
RUN_AT = "2026-08-10T10:11:41.663862+00:00"


def _runs(zones="all", action="irrigate", when=RUN_AT):
    return [{"action": action, "zones": zones, "next_run_utc": when}]


def _coordinator(hass, runs):
    """Put a coordinator in hass.data whose manager returns ``runs``."""
    coordinator = Mock()
    coordinator.recurring_schedule_manager = Mock()
    coordinator.recurring_schedule_manager.async_get_upcoming_runs = AsyncMock(
        return_value=runs
    )
    hass.data.setdefault(const.DOMAIN, {})["coordinator"] = coordinator
    return coordinator


class TestSetupAnnouncesSchedules:
    """The signal the entity depends on is sent, and sent late enough."""

    @staticmethod
    def _sync_get_config():
        return {
            const.CONF_AUTO_UPDATE_ENABLED: False,
            const.CONF_AUTO_CALC_ENABLED: False,
            const.CONF_USE_WEATHER_SERVICE: False,
        }

    async def test_setup_entry_announces_after_loading_schedules(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
    ) -> None:
        """The announcement lands after the manager has its schedules.

        Order is the whole fix: fired before the load it would tell every entity
        to recompute against the same empty list that caused the bug.
        """
        mock_config_entry.add_to_hass(hass)
        seen: list[str] = []

        async_dispatcher_connect(
            hass,
            const.DOMAIN + "_schedules_updated",
            lambda *_: seen.append("announced"),
        )

        async def _load(_self):
            seen.append("loaded")

        with (
            patch(
                "custom_components.irrigation_plus.async_get_registry"
            ) as mock_registry,
            patch("custom_components.irrigation_plus.async_register_panel"),
            patch("custom_components.irrigation_plus.async_register_websockets"),
            patch("custom_components.irrigation_plus.async_register_services"),
            patch.object(
                hass.config_entries, "async_forward_entry_setups", new=AsyncMock()
            ),
            patch.object(RecurringScheduleManager, "async_load_schedules", _load),
        ):
            mock_store = AsyncMock()
            mock_store.async_get_config.return_value = {
                const.CONF_USE_WEATHER_SERVICE: False,
                const.CONF_WEATHER_SERVICE: None,
            }
            mock_store.get_config = Mock(return_value=self._sync_get_config())
            mock_registry.return_value = mock_store

            assert await async_setup_entry(hass, mock_config_entry) is True

        await hass.async_block_till_done()
        assert seen == ["loaded", "announced"]


class TestNextIrrigationSensor:
    """The entity's response to the announcement."""

    async def test_populates_when_schedules_arrive(self, hass: HomeAssistant) -> None:
        """An entity that read an empty manager picks the run up afterwards."""
        _coordinator(hass, [])
        sensor = SmartIrrigationZoneNextIrrigationSensor(
            hass, "sensor.si_front_next_irrigation", ZONE
        )

        # The cold-start reading: schedules are not loaded yet.
        await sensor.async_update()
        assert sensor.native_value is None

        _coordinator(hass, _runs())
        await sensor.async_update()
        assert sensor.native_value is not None
        assert sensor.native_value.isoformat() == RUN_AT

    async def test_targeted_zone_list_is_honoured(self, hass: HomeAssistant) -> None:
        """A run naming other zones does not populate this one."""
        _coordinator(hass, _runs(zones=[2, 3]))
        sensor = SmartIrrigationZoneNextIrrigationSensor(
            hass, "sensor.si_front_next_irrigation", ZONE
        )

        await sensor.async_update()
        assert sensor.native_value is None

    async def test_empty_rather_than_stale_when_the_schedule_goes_away(
        self, hass: HomeAssistant
    ) -> None:
        """Losing the last targeting schedule clears the value.

        The recompute assigns unconditionally rather than only on a hit, so a
        disabled or deleted schedule leaves the entity empty instead of showing
        a run that will never happen.
        """
        _coordinator(hass, _runs())
        sensor = SmartIrrigationZoneNextIrrigationSensor(
            hass, "sensor.si_front_next_irrigation", ZONE
        )
        await sensor.async_update()
        assert sensor.native_value is not None

        _coordinator(hass, [])
        await sensor.async_update()
        assert sensor.native_value is None

    async def test_calculate_actions_are_ignored(self, hass: HomeAssistant) -> None:
        """Only irrigate runs are irrigation."""
        _coordinator(hass, _runs(action="calculate"))
        sensor = SmartIrrigationZoneNextIrrigationSensor(
            hass, "sensor.si_front_next_irrigation", ZONE
        )

        await sensor.async_update()
        assert sensor.native_value is None
