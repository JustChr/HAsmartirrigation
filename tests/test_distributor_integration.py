"""Distributor integration: coordinator wiring, zone exclusion, services."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.distributor import DistributorMixin


def test_coordinator_inherits_distributor_mixin():
    assert issubclass(SmartIrrigationCoordinator, DistributorMixin)
    # the restart-reconciliation entry point is reachable on the coordinator
    assert hasattr(SmartIrrigationCoordinator, "async_resume_distributor_cycles")


def _irrigation_coord(zones):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.store = Mock()
    c.store.async_get_zones = AsyncMock(return_value=zones)
    c.store.config = SimpleNamespace(
        zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        live_estimate_enabled=False,
    )
    c._sc_is_self_closing = Mock(return_value=False)
    c._rain_delay_active = Mock(return_value=False)
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda zs: zs)
    c._apply_live_durations = AsyncMock(side_effect=lambda zs: zs)
    c.async_master_begin_cycle = AsyncMock()
    c._master_note_run = Mock()
    c.async_master_schedule_off = AsyncMock()
    c._irrigate_zones_parallel = AsyncMock()
    return c


async def test_member_zone_excluded_from_normal_watering():
    # A member zone (distributor_id set, incl. 0!) with a STRAY linked entity
    # must NOT be watered by the normal path — the distributor owns it.
    normal = {
        const.ZONE_ID: 1,
        const.ZONE_LINKED_ENTITY: "switch.z1",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 60,
        const.ZONE_BUCKET: -5,
        const.ZONE_BUCKET_THRESHOLD: 0,
        const.ZONE_DISTRIBUTOR_ID: None,
    }
    member = {
        const.ZONE_ID: 2,
        const.ZONE_LINKED_ENTITY: "switch.z2",  # stray/leftover
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 60,
        const.ZONE_BUCKET: -5,
        const.ZONE_BUCKET_THRESHOLD: 0,
        const.ZONE_DISTRIBUTOR_ID: 0,  # member of distributor 0 (note: id 0!)
    }
    c = _irrigation_coord([normal, member])
    await c._irrigate_linked_entities()
    dispatched = c._irrigate_zones_parallel.await_args.args[0]
    ids = {z[const.ZONE_ID] for z in dispatched}
    assert ids == {1}  # only the normal zone; member 0 excluded


def _svc_coord(distributor):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.store = Mock()
    c.store.get_distributor = Mock(return_value=distributor)
    c.async_distributor_set_outlet = AsyncMock()
    c.async_distributor_resync_home = AsyncMock()
    c.async_run_distributor_test = AsyncMock()
    c.async_run_distributor_cycle = AsyncMock()
    return c


def _call(**data):
    call = MagicMock()
    call.data = data
    return call


async def test_handle_set_outlet_calls_method():
    c = _svc_coord({"id": 0, "active_cycle": {}})
    await c.handle_distributor_set_outlet(
        _call(**{const.ATTR_DISTRIBUTOR_ID: 0, const.ATTR_OUTLET: 3})
    )
    c.async_distributor_set_outlet.assert_awaited_once_with(0, 3)


async def test_handle_resync_home_calls_method():
    c = _svc_coord({"id": 0, "active_cycle": {}})
    await c.handle_distributor_resync_home(_call(**{const.ATTR_DISTRIBUTOR_ID: 0}))
    c.async_distributor_resync_home.assert_awaited_once_with(0)


async def test_handle_test_run_calls_method():
    dist = {"id": 0, "active_cycle": {}}
    c = _svc_coord(dist)
    await c.handle_distributor_test_run(_call(**{const.ATTR_DISTRIBUTOR_ID: 0}))
    c.async_run_distributor_test.assert_awaited_once_with(dist)


async def test_handle_run_now_calls_cycle():
    dist = {"id": 0, "active_cycle": {}}
    c = _svc_coord(dist)
    await c.handle_distributor_run_now(_call(**{const.ATTR_DISTRIBUTOR_ID: 0}))
    c.async_run_distributor_cycle.assert_awaited_once_with(dist, concurrent=False)


async def test_handle_run_now_rejects_when_cycle_active():
    dist = {"id": 0, "active_cycle": {"outlet": 1, "phase": "watering"}}
    c = _svc_coord(dist)
    try:
        await c.handle_distributor_run_now(_call(**{const.ATTR_DISTRIBUTOR_ID: 0}))
        raised = False
    except const.SmartIrrigationError:
        raised = True
    assert raised is True
    c.async_run_distributor_cycle.assert_not_awaited()


async def test_handle_unknown_distributor_raises():
    c = _svc_coord(None)  # store.get_distributor returns None
    try:
        await c.handle_distributor_test_run(_call(**{const.ATTR_DISTRIBUTOR_ID: 99}))
        raised = False
    except const.SmartIrrigationError:
        raised = True
    assert raised is True


def test_distributor_services_are_registered():
    from custom_components.smart_irrigation.services import async_register_services

    coordinator = MagicMock(spec=SmartIrrigationCoordinator)
    hass = MagicMock()
    registered = []
    hass.services.async_register = lambda domain, service, handler: registered.append(
        service
    )
    hass.data = {const.DOMAIN: {"coordinator": coordinator}}

    async_register_services(hass)

    for svc in (
        const.SERVICE_DISTRIBUTOR_SET_OUTLET,
        const.SERVICE_DISTRIBUTOR_RESYNC_HOME,
        const.SERVICE_DISTRIBUTOR_TEST_RUN,
        const.SERVICE_DISTRIBUTOR_RUN_NOW,
    ):
        assert svc in registered


def _upsert_coord():
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    # I2: async_upsert_distributor now fires register/updated/removed signals via
    # the real async_dispatcher_send; a real hass.data dict (no 'dispatcher' key)
    # makes it short-circuit cleanly instead of iterating a Mock.
    c.hass = Mock()
    c.hass.data = {}
    c.id = "cid"
    c.store = Mock()
    # get_distributor (sync) returns a truthy dict by default = "exists".
    c.store.get_distributor = Mock(return_value={"id": 0})
    c.store.async_create_distributor = AsyncMock(return_value={"id": 0})
    c.store.async_update_distributor = AsyncMock(return_value={"id": 5})
    c.store.async_delete_distributor = AsyncMock(return_value=True)
    return c


async def test_upsert_creates_when_no_id():
    c = _upsert_coord()
    await c.async_upsert_distributor({"name": "Garten"})
    c.store.async_create_distributor.assert_awaited_once_with({"name": "Garten"})
    c.store.async_update_distributor.assert_not_awaited()


async def test_upsert_updates_when_id_present_including_zero():
    c = _upsert_coord()
    # id 0 is a valid distributor id — must UPDATE, not create.
    await c.async_upsert_distributor({"id": 0, "name": "Garten", "pause_seconds": 120})
    c.store.async_update_distributor.assert_awaited_once_with(
        0, {"name": "Garten", "pause_seconds": 120}
    )
    c.store.async_create_distributor.assert_not_awaited()


async def test_upsert_deletes_when_remove_flag(monkeypatch):
    c = _upsert_coord()
    # Plan I review: the delete branch now removes the per-distributor device via
    # the REAL dr.async_get(self.hass); c.hass is a Mock, so patch it to a
    # no-device registry (the clean no-device path) to keep this test focused on
    # the store-delete routing.
    fake_registry = Mock()
    fake_registry.async_get_device = Mock(return_value=None)
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.dr.async_get",
        lambda hass: fake_registry,
    )
    await c.async_upsert_distributor({"id": 3, const.ATTR_REMOVE: True})
    c.store.async_delete_distributor.assert_awaited_once_with(3)
    c.store.async_update_distributor.assert_not_awaited()
    c.store.async_create_distributor.assert_not_awaited()


async def test_upsert_update_missing_id_raises_clean_error():
    # a stale form posting an id that no longer exists must fail gracefully
    # (SmartIrrigationError -> 400), NOT surface the store's KeyError as a 500.
    c = _upsert_coord()
    c.store.get_distributor = Mock(return_value=None)
    raised = False
    try:
        await c.async_upsert_distributor({"id": 99, "name": "X"})
    except const.SmartIrrigationError:
        raised = True
    assert raised is True
    c.store.async_update_distributor.assert_not_awaited()


async def test_upsert_delete_missing_id_raises_clean_error():
    c = _upsert_coord()
    c.store.get_distributor = Mock(return_value=None)
    raised = False
    try:
        await c.async_upsert_distributor({"id": 99, const.ATTR_REMOVE: True})
    except const.SmartIrrigationError:
        raised = True
    assert raised is True
    c.store.async_delete_distributor.assert_not_awaited()


async def test_upsert_remove_without_id_raises_clean_error():
    c = _upsert_coord()
    raised = False
    try:
        await c.async_upsert_distributor({const.ATTR_REMOVE: True})
    except const.SmartIrrigationError:
        raised = True
    assert raised is True
    c.store.async_delete_distributor.assert_not_awaited()


def test_distributor_view_url():
    from custom_components.smart_irrigation.websockets import (
        SmartIrrigationDistributorView,
    )

    assert (
        SmartIrrigationDistributorView.url == "/api/" + const.DOMAIN + "/distributors"
    )


async def test_distributor_view_post_upserts_and_dispatches():
    from unittest.mock import patch

    from custom_components.smart_irrigation.websockets import (
        SmartIrrigationDistributorView,
    )

    coordinator = AsyncMock()
    hass = SimpleNamespace(data={const.DOMAIN: {"coordinator": coordinator}})
    request = MagicMock()
    request.app = {"hass": hass}
    data = {"name": "Garten", "pause_seconds": 120}
    # RequestDataValidator reads the body via request.json(), validates against the
    # view's schema, then calls the inner post(view, request, validated_data).
    request.json = AsyncMock(return_value=data)

    view = SmartIrrigationDistributorView()
    view.json = MagicMock(return_value="OK")

    with patch(
        "custom_components.smart_irrigation.websockets.async_dispatcher_send"
    ) as disp:
        result = await view.post(request)  # decorated: exercises the real validator

    coordinator.async_upsert_distributor.assert_awaited_once()
    passed = coordinator.async_upsert_distributor.await_args.args[0]
    assert passed["name"] == "Garten"
    assert passed["pause_seconds"] == 120
    disp.assert_called_once_with(hass, const.DOMAIN + "_update_frontend")
    assert result == "OK"
    view.json.assert_called_once_with({"success": True})


async def test_zone_view_accepts_membership_fields():
    from unittest.mock import patch

    from custom_components.smart_irrigation.websockets import SmartIrrigationZoneView

    coordinator = AsyncMock()
    hass = SimpleNamespace(data={const.DOMAIN: {"coordinator": coordinator}})
    request = MagicMock()
    request.app = {"hass": hass}
    # a zone-to-outlet mapping update carries distributor_id + outlet_number
    data = {const.ZONE_ID: 2, "distributor_id": 0, "outlet_number": 3}
    request.json = AsyncMock(return_value=data)

    view = SmartIrrigationZoneView()
    view.json = MagicMock(return_value="OK")

    with patch("custom_components.smart_irrigation.websockets.async_dispatcher_send"):
        # decorated: the schema must ACCEPT the membership fields, else the
        # validator short-circuits and the inner handler never runs.
        await view.post(request)

    coordinator.async_update_zone_config.assert_awaited_once()
    called = coordinator.async_update_zone_config.await_args
    forwarded = called.args[1] if len(called.args) > 1 else called.kwargs.get("data")
    assert forwarded["distributor_id"] == 0
    assert forwarded["outlet_number"] == 3
