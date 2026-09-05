"""The next-irrigation sensor's cold-start population, and what it publishes.

The entity recomputes on ``irrigation_plus_schedules_updated`` and on
``irrigation_plus_estimates_updated``. Its own add-time refresh is its one other
chance, and during a cold start that lands before ``async_load_schedules`` has
put anything in the manager, so the value it reads is "no schedules" rather than
"no schedule yet". Nothing revisited it, and every zone's Next irrigation read
``unknown`` for the rest of the session.

Guarded here at both ends: the setup path announces the schedules once they are
loaded, and the entity answers that announcement.
"""

from unittest.mock import AsyncMock, Mock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

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


def _projection(zone_id=1, zones="all", estimated=True, will_water=True):
    return [
        {
            "schedule_id": "s1",
            "name": "overnight",
            "zones": zones,
            "target_utc": "2026-08-10T10:11:41.663862+00:00",
            "decision_point_utc": "2026-08-10T02:00:00+00:00",
            "start_utc": "2026-08-10T09:56:41.663862+00:00",
            "estimated": estimated,
            "skipped": False,
            "skip_reasons": [],
            "zone_runs": {
                str(zone_id): {
                    "will_water": will_water,
                    "duration_seconds": 900,
                    "bucket": -1.12,
                    "forecast_tier": "service",
                    "projected_rain": 0.0,
                    "projected_et": 0.12,
                }
            },
        }
    ]


class TestWhatTheEntityPublishes:
    """The attributes are the whole deliverable here: the state is a timestamp
    that existed before, and everything the projection adds is read off the
    attribute map."""

    async def test_it_publishes_the_projected_run(self, hass: HomeAssistant) -> None:
        coordinator = _coordinator(hass, _runs())
        coordinator.recurring_schedule_manager.async_get_next_run_projection = (
            AsyncMock(return_value=_projection())
        )
        sensor = SmartIrrigationZoneNextIrrigationSensor(hass, "sensor.x", ZONE)

        await sensor.async_update()
        attrs = sensor.extra_state_attributes

        assert attrs["projection_state"] == "projected"
        assert attrs["schedule_name"] == "overnight"
        assert attrs["will_water"] is True
        assert attrs["projected_duration_seconds"] == 900
        assert attrs["decision_point_bucket"] == -1.12
        assert attrs["decision_point_utc"] == "2026-08-10T02:00:00+00:00"
        assert attrs["forecast_tier"] == "service"

    async def test_an_armed_decision_is_not_reported_as_a_projection(
        self, hass: HomeAssistant
    ) -> None:
        coordinator = _coordinator(hass, _runs())
        coordinator.recurring_schedule_manager.async_get_next_run_projection = (
            AsyncMock(return_value=_projection(estimated=False))
        )
        sensor = SmartIrrigationZoneNextIrrigationSensor(hass, "sensor.x", ZONE)

        await sensor.async_update()

        assert sensor.extra_state_attributes["projection_state"] == "armed"

    async def test_a_schedule_that_does_not_reach_this_zone_publishes_none(
        self, hass: HomeAssistant
    ) -> None:
        """``none`` rather than another schedule's run: the attributes are
        per-zone, and a zone nothing waters must not inherit the numbers of one
        that does."""
        coordinator = _coordinator(hass, _runs())
        coordinator.recurring_schedule_manager.async_get_next_run_projection = (
            AsyncMock(return_value=_projection(zone_id=2, zones=[2]))
        )
        sensor = SmartIrrigationZoneNextIrrigationSensor(hass, "sensor.x", ZONE)

        await sensor.async_update()
        attrs = sensor.extra_state_attributes

        assert attrs["projection_state"] == "none"
        assert attrs["will_water"] is False
        assert attrs["projected_duration_seconds"] is None
        assert attrs["decision_point_bucket"] is None

    async def test_a_manager_too_old_to_project_still_publishes_the_time(
        self, hass: HomeAssistant
    ) -> None:
        """The state is the half that predates this. A projection that cannot be
        computed must not take the next-run time down with it."""
        coordinator = _coordinator(hass, _runs())
        coordinator.recurring_schedule_manager.async_get_next_run_projection = (
            AsyncMock(side_effect=RuntimeError("nope"))
        )
        sensor = SmartIrrigationZoneNextIrrigationSensor(hass, "sensor.x", ZONE)

        await sensor.async_update()

        assert sensor.native_value is not None
        assert sensor.extra_state_attributes["projection_state"] == "none"


class TestTheEntityAnswersAnEstimateRefresh:
    """The projection is sized from the live bucket, so it moves whenever the
    estimates do. Subscribed only to the schedule signal, the attributes would
    sit still between config writes -- minutes on a quiet install -- while the
    number they are sized from moved underneath them."""

    async def test_an_estimate_refresh_recomputes_the_entity(
        self, hass: HomeAssistant
    ) -> None:
        _coordinator(hass, _runs())
        sensor = SmartIrrigationZoneNextIrrigationSensor(hass, "sensor.x", ZONE)
        sensor.hass = hass
        with patch.object(sensor, "async_schedule_update_ha_state") as refresh:
            async_dispatcher_send(hass, const.DOMAIN + "_estimates_updated")
            await hass.async_block_till_done()

        assert refresh.called
        assert refresh.call_args.kwargs.get("force_refresh") is True
