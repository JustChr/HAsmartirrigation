"""Which teardowns reach the OpenSprinkler controller, and which must not.

The controller keeps stepping through its queue without Home Assistant, so a
teardown that only drops the watchers leaves the water running. The distinction
that matters is whether anything will come back to adopt the run:

* a reload and a restart are adopted seconds later by
  ``async_resume_self_closing_runs``, so cutting the run short there would waste
  water on every options change;
* a disable, a removal and a real shutdown are not, so the stop has to go out.
"""

from unittest.mock import AsyncMock, Mock, patch

from homeassistant.config_entries import ConfigEntry, ConfigEntryDisabler
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, RESTART_EXIT_CODE
from homeassistant.core import HomeAssistant

from custom_components.irrigation_plus import (
    async_remove_entry,
    async_setup_entry,
    async_unload_entry,
    const,
)


def _sync_get_config():
    return {
        const.CONF_AUTO_UPDATE_ENABLED: False,
        const.CONF_AUTO_CALC_ENABLED: False,
        const.CONF_USE_WEATHER_SERVICE: False,
    }


async def _setup(hass, entry):
    """Run the real setup so the shutdown hook is armed as it is in production."""
    entry.add_to_hass(hass)
    with (
        patch("custom_components.irrigation_plus.async_get_registry") as mock_registry,
        patch("custom_components.irrigation_plus.async_register_panel"),
        patch("custom_components.irrigation_plus.async_register_websockets"),
        patch("custom_components.irrigation_plus.async_register_services"),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", new=AsyncMock()
        ),
    ):
        mock_store = AsyncMock()
        mock_store.async_get_config.return_value = {
            const.CONF_USE_WEATHER_SERVICE: False,
            const.CONF_WEATHER_SERVICE: None,
        }
        mock_store.get_config = Mock(return_value=_sync_get_config())
        mock_registry.return_value = mock_store
        assert await async_setup_entry(hass, entry) is True

    coordinator = hass.data[const.DOMAIN]["coordinator"]
    coordinator.async_abort_opensprinkler_runs = AsyncMock(return_value=True)
    return coordinator


class TestShutdown:
    """EVENT_HOMEASSISTANT_STOP covers both a restart and a real stop."""

    async def test_a_real_stop_stops_the_stations(
        self, hass: HomeAssistant, mock_config_entry: ConfigEntry
    ) -> None:
        """Nothing is coming back to supervise the queue, so it must not run on."""
        coordinator = await _setup(hass, mock_config_entry)

        hass.exit_code = 0
        hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
        await hass.async_block_till_done()

        coordinator.async_abort_opensprinkler_runs.assert_awaited_once()

    async def test_a_restart_leaves_the_run_to_be_re_adopted(
        self, hass: HomeAssistant, mock_config_entry: ConfigEntry
    ) -> None:
        """exit_code is assigned before the event fires, so a restart is visible.

        Stopping here would cut a legitimate run short every time Home Assistant
        is restarted, when the resume path re-attaches the deadline and the
        crediting within seconds.
        """
        coordinator = await _setup(hass, mock_config_entry)

        hass.exit_code = RESTART_EXIT_CODE
        hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
        await hass.async_block_till_done()

        coordinator.async_abort_opensprinkler_runs.assert_not_awaited()

    async def test_the_hook_does_not_outlive_its_coordinator(
        self, hass: HomeAssistant, mock_config_entry: ConfigEntry
    ) -> None:
        """A reload builds a new coordinator; the old hook must not still fire.

        Left armed it would, at the next real shutdown, stop stations through a
        dead coordinator while the live one believed its runs were in flight.
        """
        coordinator = await _setup(hass, mock_config_entry)
        await coordinator.async_unload()

        hass.exit_code = 0
        hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
        await hass.async_block_till_done()

        coordinator.async_abort_opensprinkler_runs.assert_not_awaited()


class TestUnloadAndRemove:
    """A reload is not a teardown; a disable and a removal are."""

    @staticmethod
    def _coordinator(hass):
        coordinator = AsyncMock()
        hass.data[const.DOMAIN] = {"coordinator": coordinator}
        return coordinator

    @staticmethod
    def _unload_patches(hass):
        return (
            patch("custom_components.irrigation_plus.remove_panel"),
            patch.object(
                hass.config_entries,
                "async_forward_entry_unload",
                new=AsyncMock(return_value=True),
            ),
        )

    async def test_a_reload_keeps_the_run(
        self, hass: HomeAssistant, mock_config_entry: ConfigEntry
    ) -> None:
        """The resume path adopts it, so stopping would only waste water."""
        coordinator = self._coordinator(hass)
        panel, forward = self._unload_patches(hass)
        with panel, forward:
            assert await async_unload_entry(hass, mock_config_entry) is True

        coordinator.async_abort_opensprinkler_runs.assert_not_awaited()
        coordinator.async_unload.assert_awaited_once()

    async def test_disabling_the_entry_stops_the_run(
        self, hass: HomeAssistant, mock_config_entry: ConfigEntry
    ) -> None:
        """Nothing resumes a disabled entry, so the queue would run on unwatched."""
        coordinator = self._coordinator(hass)
        mock_config_entry.disabled_by = ConfigEntryDisabler.USER
        panel, forward = self._unload_patches(hass)
        with panel, forward:
            assert await async_unload_entry(hass, mock_config_entry) is True

        coordinator.async_abort_opensprinkler_runs.assert_awaited_once()

    async def test_removing_the_entry_stops_the_run_without_settling(
        self, hass: HomeAssistant, mock_config_entry: ConfigEntry
    ) -> None:
        """The store is deleted immediately after, so the reconciliation is moot.

        The stop itself is not: it is the last moment anything knows these
        stations belonged to Smart Irrigation.
        """
        coordinator = self._coordinator(hass)
        with (
            patch("custom_components.irrigation_plus.remove_panel"),
            patch(
                "custom_components.irrigation_plus.async_remove_card_resource",
                new=AsyncMock(),
            ),
        ):
            await async_remove_entry(hass, mock_config_entry)

        coordinator.async_abort_opensprinkler_runs.assert_awaited_once()
        assert coordinator.async_abort_opensprinkler_runs.await_args.kwargs == {
            "settle": False
        }
        coordinator.async_delete_config.assert_awaited_once()
