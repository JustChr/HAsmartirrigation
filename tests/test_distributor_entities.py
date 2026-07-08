import asyncio
from unittest.mock import AsyncMock, Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.entity import distributor_device_info
from custom_components.smart_irrigation.distributor_entity import (
    outlet_reconcile_diff,
    used_outlets,
)
from tests.test_distributor import _dist, _host


def _hass_with_zones(zones):
    hass = Mock()
    coord = Mock()
    coord.id = "cid"
    coord.store.get_zone = lambda zid: next((z for z in zones if z["id"] == zid), None)
    coord.store.get_distributor = lambda did: None
    hass.data = {const.DOMAIN: {"coordinator": coord}}
    return hass


def test_distributor_device_info_identifiers_and_via_device():
    hass = _hass_with_zones([])
    info = distributor_device_info(hass, 0, "Gardena1")
    assert info["identifiers"] == {(const.DOMAIN, "cid_distributor_0")}
    assert info["name"] == "Gardena1"
    assert info["via_device"] == (const.DOMAIN, "cid")


def test_used_outlets_from_member_zones():
    zones = [
        {"id": 7, "distributor_id": 0, "outlet_number": 1, "name": "A"},
        {"id": 8, "distributor_id": 0, "outlet_number": 3, "name": "B"},
        {"id": 9, "distributor_id": 1, "outlet_number": 1, "name": "C"},
        {"id": 1, "distributor_id": None, "outlet_number": None, "name": "N"},
    ]
    hass = Mock()
    coord = Mock()
    coord.store.get_zones = lambda: zones
    hass.data = {const.DOMAIN: {"coordinator": coord}}
    assert used_outlets(hass, 0) == {1, 3}
    assert used_outlets(hass, 1) == {1}
    assert used_outlets(hass, 2) == set()


def test_outlet_reconcile_diff():
    assert outlet_reconcile_diff({1, 2, 3}, {1}) == ({2, 3}, set())
    assert outlet_reconcile_diff({1}, {1, 2, 3}) == (set(), {2, 3})
    assert outlet_reconcile_diff({1, 2}, {1, 2}) == (set(), set())


async def test_persist_cycle_fires_distributor_updated(monkeypatch):
    c = _host()
    sent = []
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.async_dispatcher_send",
        lambda hass, signal, *a: sent.append((signal, a)),
    )
    c.store.async_update_distributor = AsyncMock()
    await c._dist_persist_cycle(0, 2, "watering")
    assert (const.DOMAIN + "_distributor_updated", (0,)) in sent


async def test_dist_store_update_pings_frontend(monkeypatch):
    # A distributor state change (cycle start/end/advance) must also refresh the
    # panel: the views subscribe to _config_updated, fed by the _update_frontend
    # dispatcher signal. Without this ping the panel stays stale until F5.
    c = _host()
    sent = []
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.async_dispatcher_send",
        lambda hass, signal, *a: sent.append(signal),
    )
    c.store.async_update_distributor = AsyncMock()
    await c._dist_persist_cycle(0, 2, "watering")
    assert const.DOMAIN + "_distributor_updated" in sent  # HA entities
    assert const.DOMAIN + "_update_frontend" in sent  # panel re-fetch


async def test_upsert_create_fires_register(monkeypatch):
    c = _host()
    sent = []
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.async_dispatcher_send",
        lambda hass, signal, *a: sent.append((signal, a)),
    )
    c.store.get_distributor = Mock(return_value=None)
    c.store.async_create_distributor = AsyncMock(return_value={"id": 5, "name": "New"})
    await c.async_upsert_distributor({"name": "New"})
    assert sent[-1][0] == const.DOMAIN + "_distributor_register_entity"


async def test_upsert_delete_fires_removed(monkeypatch):
    c = _host()
    c.id = "cid"
    sent = []
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.async_dispatcher_send",
        lambda hass, signal, *a: sent.append((signal, a)),
    )
    c.store.get_distributor = Mock(return_value={"id": 3})
    c.store.async_delete_distributor = AsyncMock(return_value=True)
    # Plan I review: the delete branch now also removes the per-distributor
    # device via the REAL dr.async_get(self.hass). _host().hass is a Mock, so
    # patch dr.async_get to a registry with no device — the clean no-device
    # path — keeping this test focused on the dispatcher signal.
    fake_registry = Mock()
    fake_registry.async_get_device = Mock(return_value=None)
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.dr.async_get",
        lambda hass: fake_registry,
    )
    await c.async_upsert_distributor({"id": 3, "remove": True})
    assert (const.DOMAIN + "_distributor_removed", (3,)) in sent


from custom_components.smart_irrigation.sensor import (
    SmartIrrigationDistributorCurrentOutletSensor,
    SmartIrrigationDistributorOutletZoneSensor,
)


def _hass_full(zones, distributor):
    hass = Mock()
    coord = Mock()
    coord.id = "cid"
    coord.store.get_zones = lambda: zones
    coord.store.get_distributor = lambda did: (
        distributor if did == distributor["id"] else None
    )
    hass.data = {const.DOMAIN: {"coordinator": coord}}
    return hass


def test_current_outlet_sensor_value_and_attrs():
    dist = {
        "id": 0,
        "name": "G1",
        "current_outlet": 3,
        "position_state": "synced",
        "active_cycle": {"outlet": 3, "phase": "watering"},
    }
    hass = _hass_full([], dist)
    s = SmartIrrigationDistributorCurrentOutletSensor(
        hass, "sensor.g1_current_outlet", dist
    )
    assert s.native_value == 3
    assert s.extra_state_attributes["position_state"] == "synced"
    assert s.extra_state_attributes["phase"] == "watering"


def test_outlet_zone_sensor_resolves_zone_name():
    zones = [{"id": 7, "distributor_id": 0, "outlet_number": 2, "name": "Beet"}]
    dist = {"id": 0, "name": "G1", "current_outlet": 1, "active_cycle": {}}
    hass = _hass_full(zones, dist)
    s = SmartIrrigationDistributorOutletZoneSensor(
        hass, "sensor.g1_outlet_2_zone", dist, 2
    )
    assert s.native_value == "Beet"
    assert s.extra_state_attributes["zone_id"] == 7
    assert s.extra_state_attributes["outlet_number"] == 2
    assert s._attr_translation_placeholders == {"outlet": "2"}


from custom_components.smart_irrigation.binary_sensor import (
    SmartIrrigationDistributorCommissionedSensor,
    SmartIrrigationDistributorWateringNowSensor,
)


def test_commissioned_binary_sensor():
    dist = {"id": 0, "name": "G1", "commissioning_confirmed": True, "active_cycle": {}}
    hass = _hass_full([], dist)
    s = SmartIrrigationDistributorCommissionedSensor(
        hass, "binary_sensor.g1_commissioned", dist
    )
    assert s.is_on is True
    dist2 = {**dist, "commissioning_confirmed": False}
    s2 = SmartIrrigationDistributorCommissionedSensor(
        hass, "binary_sensor.g1_commissioned", dist2
    )
    assert s2.is_on is False


def test_watering_now_binary_sensor():
    dist = {
        "id": 0,
        "name": "G1",
        "commissioning_confirmed": True,
        "active_cycle": {"outlet": 2, "phase": "watering"},
    }
    hass = _hass_full([], dist)
    s = SmartIrrigationDistributorWateringNowSensor(
        hass, "binary_sensor.g1_watering_now", dist
    )
    assert s.is_on is True
    assert s.extra_state_attributes["phase"] == "watering"
    assert s.extra_state_attributes["outlet"] == 2
    idle = {**dist, "active_cycle": {}}
    s_idle = SmartIrrigationDistributorWateringNowSensor(
        hass, "binary_sensor.g1_watering_now", idle
    )
    assert s_idle.is_on is False


from custom_components.smart_irrigation.button import (
    SmartIrrigationDistributorTestRunButton,
)


def _scheduling_hass(zones, dist):
    # A test-run sweeps every outlet (minutes of watering); the button must
    # fire-and-forget so the press does not block. Give hass a real scheduler so
    # the backgrounded coro actually runs when awaited.
    hass = _hass_full(zones, dist)
    scheduled = []
    hass.async_create_task = Mock(
        side_effect=lambda coro: scheduled.append(asyncio.ensure_future(coro))
    )
    return hass, scheduled


async def test_test_run_button_schedules_coordinator_without_blocking():
    dist = {"id": 0, "name": "G1"}
    hass, scheduled = _scheduling_hass([], dist)
    coord = hass.data[const.DOMAIN]["coordinator"]
    coord.async_run_distributor_test = AsyncMock()
    coord.store.get_distributor = lambda did: dist
    b = SmartIrrigationDistributorTestRunButton(hass, "button.g1_test_run", dist)
    await b.async_press()
    hass.async_create_task.assert_called_once()  # scheduled, not awaited inline
    await asyncio.gather(*scheduled)
    coord.async_run_distributor_test.assert_awaited_once()
    assert coord.async_run_distributor_test.await_args.args[0]["id"] == 0


async def test_test_run_button_blocked_when_commissioned():
    dist = {"id": 0, "name": "G1", "commissioning_confirmed": True}
    hass, scheduled = _scheduling_hass([], dist)
    coord = hass.data[const.DOMAIN]["coordinator"]
    coord.async_run_distributor_test = AsyncMock()
    coord.store.get_distributor = lambda did: dist
    b = SmartIrrigationDistributorTestRunButton(hass, "button.g1_test_run", dist)
    assert b.available is False  # greyed when commissioned
    await b.async_press()
    hass.async_create_task.assert_not_called()  # must NOT schedule a run
    coord.async_run_distributor_test.assert_not_called()  # must NOT trigger
    assert not scheduled


async def test_test_run_button_runs_when_not_commissioned():
    dist = {"id": 0, "name": "G1", "commissioning_confirmed": False}
    hass, scheduled = _scheduling_hass([], dist)
    coord = hass.data[const.DOMAIN]["coordinator"]
    coord.async_run_distributor_test = AsyncMock()
    coord.store.get_distributor = lambda did: dist
    b = SmartIrrigationDistributorTestRunButton(hass, "button.g1_test_run", dist)
    assert b.available is True
    await b.async_press()
    hass.async_create_task.assert_called_once()
    await asyncio.gather(*scheduled)
    coord.async_run_distributor_test.assert_awaited_once()


def test_zone_on_outlet_coerces_str_outlet_number():
    from custom_components.smart_irrigation.distributor_entity import zone_on_outlet

    zones = [{"id": 7, "distributor_id": 0, "outlet_number": "2", "name": "Beet"}]
    hass = Mock()
    coord = Mock()
    coord.store.get_zones = lambda: zones
    hass.data = {const.DOMAIN: {"coordinator": coord}}
    z = zone_on_outlet(hass, 0, 2)
    assert z is not None and z["id"] == 7


async def test_upsert_delete_removes_device(monkeypatch):
    c = _host()
    c.id = "cid"
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.async_dispatcher_send",
        lambda *a, **k: None,
    )
    c.store.get_distributor = Mock(return_value={"id": 3})
    c.store.async_delete_distributor = AsyncMock(return_value=True)
    removed = {}
    fake_device = Mock()
    fake_device.id = "dev123"
    fake_registry = Mock()
    fake_registry.async_get_device = Mock(return_value=fake_device)
    fake_registry.async_remove_device = Mock(
        side_effect=lambda did: removed.setdefault("id", did)
    )
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.dr.async_get",
        lambda hass: fake_registry,
    )
    await c.async_upsert_distributor({"id": 3, "remove": True})
    fake_registry.async_get_device.assert_called_once()
    # the distributor device identifier was looked up
    ident = fake_registry.async_get_device.call_args.kwargs["identifiers"]
    assert (const.DOMAIN, "cid_distributor_3") in ident
    assert removed.get("id") == "dev123"
