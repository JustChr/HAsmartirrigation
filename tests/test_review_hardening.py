"""Fixes from the deferred-findings burndown (2026-08-03).

Four unrelated latent defects, grouped because they were closed in one pass:
the zone-selection character-iteration trap, the Lovelace resource that
outlived an uninstall, `@callback` on a coroutine function, and `localize()`
returning None (that one lives in test_localize.py, next to its siblings).
"""

import inspect
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.exceptions import Unauthorized

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.helpers import normalize_zone_selection
from custom_components.irrigation_plus.irrigation import IrrigationRunnerMixin
from custom_components.irrigation_plus.panel import async_remove_card_resource


class TestNormalizeZoneSelection:
    """A schedule's `zones` is "all" or a list — never a bare id string."""

    def test_all_means_everything(self):
        assert normalize_zone_selection("all") is None

    def test_none_means_everything(self):
        assert normalize_zone_selection(None) is None

    def test_a_list_passes_through(self):
        assert normalize_zone_selection(["1", "2"]) == ["1", "2"]

    def test_a_bare_multi_digit_id_is_one_zone_not_two(self):
        """The bug: `for zone_id in "12"` targets zones 1 and 2, not zone 12.

        Single-digit ids work by coincidence, which is exactly why this
        survives casual testing — it only misfires once an install grows past
        zone 9, and then it waters the wrong ground silently.
        """
        assert normalize_zone_selection("12") == ["12"]

    def test_a_bare_single_digit_id_is_still_one_zone(self):
        assert normalize_zone_selection("3") == ["3"]

    def test_an_arbitrary_iterable_is_materialised(self):
        """Callers iterate the result more than once."""
        result = normalize_zone_selection(iter(["7", "8"]))
        assert result == ["7", "8"]
        assert result == ["7", "8"]


class TestIrrigateLinkedEntitiesIsNotACallback:
    """`@callback` on an `async def` is a latent silent-skip.

    It marks a SYNCHRONOUS function as safe to run directly in the event loop,
    and HA's job helpers read that flag to decide not to await. It was inert
    only because the one caller awaits directly — routing it through
    `async_add_job` would have dropped the coroutine and skipped every run.
    """

    def test_it_is_still_a_coroutine_function(self):
        assert inspect.iscoroutinefunction(
            IrrigationRunnerMixin._irrigate_linked_entities
        )

    def test_it_is_not_flagged_as_a_ha_callback(self):
        assert not getattr(
            IrrigationRunnerMixin._irrigate_linked_entities, "_hass_callback", False
        )


# The capability surfaces of the two real HA collections, pinned by
# TestLovelaceCollectionShape below. A bare Mock() auto-creates every attribute
# and would pass any duck-type check, so these doubles MUST be spec'd or they
# test nothing.
_STORAGE_API = [
    "async_items",
    "async_create_item",
    "async_update_item",
    "async_delete_item",
    "loaded",
    "async_load",
]
_YAML_API = ["async_items", "loaded"]


class TestWebsocketAdminGating:
    """Deferred finding #7. The split is deliberate — see websockets.py.

    Gated: anything carrying weather-service API KEYS or the install's GPS
    COORDINATES, plus schedule writes. Ungated: everything the Lovelace card
    needs, because the card is explicitly for non-admin household members and
    supports an actions mode. Blanket-gating would have broken it silently.

    Tested by BEHAVIOUR: require_admin raises before delegating, so a non-admin
    connection never reaches the handler body and no coordinator is needed.
    """

    GATED = [
        "websocket_get_weather_config",
        "websocket_save_weather_config",
        "websocket_test_weather_config",
        "websocket_get_coordinates",
        "websocket_save_coordinates",
        "websocket_save_schedule",
        "websocket_delete_schedule",
    ]
    # The card's reads, then its actions mode. Every name here is resolved with
    # getattr, so a typo would make the test vacuous — test_every_name_resolves
    # guards that.
    UNGATED = [
        "websocket_get_config",
        "websocket_get_zones",
        "websocket_get_irrigation_outlook",
        "websocket_get_distributors",
        "websocket_irrigate_now",
        "websocket_run_zone",
        "websocket_stop_zone",
        "websocket_set_rain_delay",
        "websocket_clear_rain_delay",
    ]

    @staticmethod
    def _call(name, *, is_admin):
        from custom_components.irrigation_plus import websockets

        handler = getattr(websockets, name)
        connection = Mock(user=Mock(is_admin=is_admin))
        return handler(Mock(), connection, {"id": 1})

    @pytest.mark.parametrize("name", GATED)
    def test_a_non_admin_is_refused(self, name):
        with pytest.raises(Unauthorized):
            self._call(name, is_admin=False)

    @pytest.mark.parametrize("name", GATED)
    def test_an_anonymous_connection_is_refused(self, name):
        from custom_components.irrigation_plus import websockets

        handler = getattr(websockets, name)
        with pytest.raises(Unauthorized):
            handler(Mock(), Mock(user=None), {"id": 1})

    @staticmethod
    def _is_admin_gated(handler) -> bool:
        """require_admin returns a closure named `with_admin`.

        @wraps copies __name__ but never __code__, so the code object's name is
        the honest marker. Checked structurally rather than by calling, because
        an ungated handler would build a coroutine we would then have to throw
        away — and a stray un-awaited coroutine warning in the suite is exactly
        the kind of noise that trains people to ignore warnings.
        """
        return getattr(handler, "__code__", None) is not None and (
            handler.__code__.co_name == "with_admin"
        )

    @pytest.mark.parametrize("name", GATED + UNGATED)
    def test_every_name_resolves(self, name):
        """A typo'd handler name would make the gating tests pass vacuously.

        This is not hypothetical: the first draft listed
        `websocket_irrigation_outlook`, which does not exist, and the
        behavioural version of the ungated test swallowed the AttributeError
        and went green.
        """
        from custom_components.irrigation_plus import websockets

        assert callable(getattr(websockets, name, None)), name

    def test_the_marker_actually_detects_gating(self):
        """Proves the check above bites, so the UNGATED test is not vacuous."""
        from custom_components.irrigation_plus import websockets

        assert self._is_admin_gated(websockets.websocket_get_coordinates)

    @pytest.mark.parametrize("name", UNGATED)
    def test_the_card_surface_is_not_gated(self, name):
        from custom_components.irrigation_plus import websockets

        assert not self._is_admin_gated(getattr(websockets, name)), (
            f"{name} is admin-gated, which silently breaks the Lovelace card "
            "for non-admin users"
        )


def _resources(items):
    """A stand-in for Lovelace's storage-backed ResourceStorageCollection."""
    res = Mock(spec=_STORAGE_API)
    res.loaded = True
    res.async_items = Mock(return_value=list(items))
    res.async_delete_item = AsyncMock()
    return res


class TestFinishTargetMemoryIsPruned:
    """`_finish_last_target` was only cleared wholesale on unload."""

    @staticmethod
    def _manager(schedules):
        from custom_components.irrigation_plus.scheduler import (
            RecurringScheduleManager,
        )

        mgr = RecurringScheduleManager.__new__(RecurringScheduleManager)
        mgr.hass = Mock()
        mgr.coordinator = Mock()
        # Pruning now reaches the persisted copy of the map too.
        mgr.coordinator.store.async_update_config = AsyncMock()
        mgr._schedules = schedules
        mgr._schedule_trackers = {}
        mgr._finish_last_target = {}
        return mgr

    async def test_a_deleted_schedules_memory_is_dropped(self):
        mgr = self._manager([{const.SCHEDULE_CONF_ID: "keep"}])
        mgr._finish_last_target = {
            "keep": "2026-08-03T06:00:00",
            "deleted": "2026-08-03T06:00:00",
        }

        with patch.object(mgr, "_setup_schedule_tracker", new=AsyncMock()):
            await mgr._setup_schedule_trackers()

        assert set(mgr._finish_last_target) == {"keep"}

    async def test_a_live_schedules_memory_survives(self):
        """Pruning must not re-fire an occurrence that already ran."""
        mgr = self._manager([{const.SCHEDULE_CONF_ID: "keep"}])
        mgr._finish_last_target = {"keep": "2026-08-03T06:00:00"}

        with patch.object(mgr, "_setup_schedule_tracker", new=AsyncMock()):
            await mgr._setup_schedule_trackers()

        assert mgr._finish_last_target == {"keep": "2026-08-03T06:00:00"}

    async def test_a_reused_id_does_not_inherit_the_marker(self):
        """The reason this matters: a new schedule reusing a deleted id would
        otherwise skip its first occurrence."""
        mgr = self._manager([])
        mgr._finish_last_target = {"abc": "2026-08-03T06:00:00"}

        with patch.object(mgr, "_setup_schedule_tracker", new=AsyncMock()):
            await mgr._setup_schedule_trackers()  # "abc" deleted
            mgr._schedules = [{const.SCHEDULE_CONF_ID: "abc"}]  # recreated
            await mgr._setup_schedule_trackers()

        assert "abc" not in mgr._finish_last_target


class TestStaticPathsRegisterOnce:
    """HA appends to the aiohttp router with no dedup, and routes cannot be
    removed — so re-registering on every reload leaked four dead routes each
    time, for the life of the process."""

    @staticmethod
    def _hass():
        hass = Mock()
        hass.data = {}
        hass.http.async_register_static_paths = AsyncMock()
        hass.config.path = Mock(return_value="/config/custom_components")

        async def _executor(func, *args):
            return func(*args)

        hass.async_add_executor_job = _executor
        return hass

    async def _register(self, hass):
        from custom_components.irrigation_plus.panel import async_register_panel

        with (
            patch(
                "custom_components.irrigation_plus.panel.panel_custom.async_register_panel",
                new=AsyncMock(),
            ),
            patch("custom_components.irrigation_plus.panel.frontend.add_extra_js_url"),
        ):
            await async_register_panel(hass)

    async def test_a_reload_does_not_re_register(self):
        hass = self._hass()

        await self._register(hass)
        await self._register(hass)
        await self._register(hass)

        hass.http.async_register_static_paths.assert_awaited_once()

    async def test_the_flag_survives_the_domain_data_being_wiped(self):
        """async_remove_entry deletes hass.data[DOMAIN]; the routes outlive it,
        so a reinstall in the same process must NOT register them again."""
        hass = self._hass()
        await self._register(hass)

        hass.data.pop(const.DOMAIN, None)  # what async_remove_entry does
        await self._register(hass)

        hass.http.async_register_static_paths.assert_awaited_once()


class TestLovelaceCollectionShape:
    """Pin the duck-type the panel relies on instead of the class NAME.

    panel.py used to sniff `type(resources).__name__`. A rename would have made
    it fail closed into the racy add_extra_js_url path — the recurring "custom
    element doesn't exist" card error. It now asks for mutators instead, which
    only the storage-backed collection has. If HA ever gives the YAML
    collection write methods, this test fails and the check needs rethinking.
    """

    def test_storage_collection_is_writable(self):
        from homeassistant.components.lovelace.resources import (
            ResourceStorageCollection,
        )

        for attr in ("async_items", "async_create_item", "async_update_item"):
            assert hasattr(ResourceStorageCollection, attr), attr

    def test_yaml_collection_has_no_mutators(self):
        from homeassistant.components.lovelace.resources import ResourceYAMLCollection

        assert hasattr(ResourceYAMLCollection, "async_items")
        for attr in ("async_create_item", "async_update_item", "async_delete_item"):
            assert not hasattr(ResourceYAMLCollection, attr), attr


def _hass_with(resources):
    hass = Mock()
    hass.data = {"lovelace": Mock(resources=resources)}
    return hass


class TestRemoveCardResource:
    """Uninstall used to leave a resource pointing at a 404 forever."""

    async def test_our_resource_is_deleted(self):
        resources = _resources([{"id": "a", "url": f"{const.CARD_URL}?v=123"}])

        assert await async_remove_card_resource(_hass_with(resources)) is True

        resources.async_delete_item.assert_awaited_once_with("a")

    async def test_a_foreign_resource_is_left_alone(self):
        """Never touch a resource the user added pointing somewhere else."""
        resources = _resources([{"id": "b", "url": "/local/my-own-card.js"}])

        assert await async_remove_card_resource(_hass_with(resources)) is False

        resources.async_delete_item.assert_not_awaited()

    async def test_duplicates_are_all_removed(self):
        """Older builds could leave more than one cache-busted entry."""
        resources = _resources(
            [
                {"id": "a", "url": f"{const.CARD_URL}?v=1"},
                {"id": "b", "url": "/local/other.js"},
                {"id": "c", "url": f"{const.CARD_URL}?v=2"},
            ]
        )

        assert await async_remove_card_resource(_hass_with(resources)) is True

        assert [c.args[0] for c in resources.async_delete_item.await_args_list] == [
            "a",
            "c",
        ]

    async def test_yaml_mode_lovelace_is_a_no_op(self):
        """No writable resource store — must not raise, must not try."""
        resources = Mock(spec=_YAML_API)

        assert await async_remove_card_resource(_hass_with(resources)) is False

    async def test_no_lovelace_at_all_is_a_no_op(self):
        hass = Mock()
        hass.data = {}
        assert await async_remove_card_resource(hass) is False

    async def test_an_unloaded_collection_is_loaded_first(self):
        resources = _resources([{"id": "a", "url": const.CARD_URL}])
        resources.loaded = False
        resources.async_load = AsyncMock()

        await async_remove_card_resource(_hass_with(resources))

        resources.async_load.assert_awaited_once()
