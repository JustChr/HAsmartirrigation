"""Device-registry calls across Home Assistant's 2026.8 change.

Home Assistant 2026.8 added ``via_device_id`` to the device info and
``async_get_device_by_identifier`` to the registry; ``via_device`` and
``async_get_device`` are deprecated and go in 2027.8. Before 2026.8 neither
replacement exists, and the declared floor is 2025.5. The integration asks the
registry which shape it has, so each shape is pinned here with stand-ins,
whichever Home Assistant the suite runs against.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from custom_components.irrigation_plus import (
    SmartIrrigationCoordinator,
    async_setup_entry,
    const,
)
from custom_components.irrigation_plus.entity import (
    distributor_device_info,
    find_device,
    hub_link,
    hub_link_for,
    zone_device_info,
)
from tests.test_distributor import _host

_HUB = "hub-device-id"
_ZONE = (const.DOMAIN, "cid_zone_1")


class _RegistryFrom2026_8:
    """The device registry's shape from Home Assistant 2026.9 on.

    ``via_device`` only reaches it through ``**kwargs``. The per-entry lookup is
    there since 2026.8; ``_RegistryOf2026_8_0`` has 2026.8.0's own signature.
    """

    def __init__(self, device=None):
        self.device = device
        self.calls = []

    def async_get_or_create(self, *, config_entry_id, via_device_id=None, **kwargs):
        self.calls.append(("get_or_create", config_entry_id))
        return SimpleNamespace(id=_HUB)

    def async_get_device_by_identifier(self, identifier, config_entry_id):
        self.calls.append(("by_identifier", identifier, config_entry_id))
        return self.device

    def async_get_device(self, identifiers=None, connections=None):
        self.calls.append(("get_device", identifiers))
        return self.device

    def async_remove_device(self, device_id):
        self.calls.append(("remove", device_id))


class _RegistryBefore2026_8:
    """The device registry's shape from the declared floor (2025.5) to 2026.7."""

    def __init__(self, device=None):
        self.device = device
        self.calls = []

    def async_get_or_create(self, *, config_entry_id, via_device=None):
        raise AssertionError("only the signature is read")

    def async_get_device(self, identifiers=None, connections=None):
        self.calls.append(("get_device", identifiers))
        return self.device

    def async_remove_device(self, device_id):
        self.calls.append(("remove", device_id))


class _RegistryOf2026_8_0:
    """2026.8.0 itself: both keys named, and no ``**kwargs`` yet."""

    def async_get_or_create(
        self, *, config_entry_id, via_device=None, via_device_id=None
    ):
        raise AssertionError("only the signature is read")


class TestTheHubLinkFollowsTheRegistry:
    """Which key names the hub as parent depends on what the registry takes."""

    def test_a_registry_taking_via_device_id_gets_the_hubs_registry_id(self):
        assert hub_link_for(_RegistryFrom2026_8(), _HUB, "cid") == {
            "via_device_id": _HUB
        }

    def test_a_registry_before_it_gets_the_hubs_identifier(self):
        assert hub_link_for(_RegistryBefore2026_8(), _HUB, "cid") == {
            "via_device": (const.DOMAIN, "cid")
        }

    def test_a_test_double_gets_the_identifier_form(self):
        assert hub_link_for(Mock(), _HUB, "cid") == {
            "via_device": (const.DOMAIN, "cid")
        }

    def test_zone_and_distributor_devices_carry_the_recorded_link(self):
        hass = SimpleNamespace(
            data={const.DOMAIN: {"hub_link": {"via_device_id": _HUB}}}
        )
        for info in (
            zone_device_info(hass, 1, "Lawn"),
            distributor_device_info(hass, 0, "Gardena1"),
        ):
            assert info["via_device_id"] == _HUB
            assert "via_device" not in info

    def test_without_a_record_the_identifier_form_stands(self):
        hass = SimpleNamespace(data={})
        assert hub_link(hass) == {"via_device": (const.DOMAIN, const.DOMAIN)}
        info = zone_device_info(hass, 1, "Lawn")
        assert info["via_device"] == (const.DOMAIN, const.DOMAIN)
        assert "via_device_id" not in info

    def test_a_registry_naming_both_keys_gets_the_hubs_registry_id(self):
        assert hub_link_for(_RegistryOf2026_8_0(), _HUB, "cid") == {
            "via_device_id": _HUB
        }

    def test_a_signature_that_cannot_be_read_leaves_the_identifier_form(self):
        class _Unreadable:
            """Reading it fails, as on Python 3.14 for an unbound annotation."""

            @property
            def __signature__(self):
                raise NameError("an annotation names what is not bound")

            def __call__(self, **kwargs):
                raise AssertionError("only the signature is read")

        class _Registry:
            async_get_or_create = _Unreadable()

        assert hub_link_for(_Registry(), _HUB, "cid") == {
            "via_device": (const.DOMAIN, "cid")
        }

    def test_anything_but_a_recorded_link_leaves_the_identifier_form(self):
        for hass in (
            SimpleNamespace(data={const.DOMAIN: {"hub_link": {}}}),
            SimpleNamespace(data={const.DOMAIN: {"hub_link": "via_device_id"}}),
            SimpleNamespace(),
        ):
            assert hub_link(hass) == {"via_device": (const.DOMAIN, const.DOMAIN)}
        assert set(hub_link(MagicMock())) == {"via_device"}

    def test_the_recorded_link_is_handed_out_as_a_copy(self):
        record = {"via_device_id": _HUB}
        hass = SimpleNamespace(data={const.DOMAIN: {"hub_link": record}})
        assert hub_link(hass) == record
        assert hub_link(hass) is not record


class TestADeviceIsFoundPerConfigEntryWhereOffered:
    """``find_device`` uses the per-entry lookup where the registry has it."""

    def test_the_per_entry_lookup_is_asked_with_the_entry(self):
        device = SimpleNamespace(id="dev")
        registry = _RegistryFrom2026_8(device)
        assert find_device(registry, _ZONE, "entry-1") is device
        assert registry.calls == [("by_identifier", _ZONE, "entry-1")]

    def test_a_registry_before_it_is_asked_the_old_way(self):
        device = SimpleNamespace(id="dev")
        registry = _RegistryBefore2026_8(device)
        assert find_device(registry, _ZONE, "entry-1") is device
        assert registry.calls == [("get_device", {_ZONE})]

    def test_a_test_double_is_asked_the_old_way(self):
        registry = Mock()
        registry.async_get_device.return_value = "dev"
        assert find_device(registry, _ZONE, "entry-1") == "dev"
        registry.async_get_device.assert_called_once_with(identifiers={_ZONE})
        registry.async_get_device_by_identifier.assert_not_called()

    def test_a_miss_is_none_and_never_asked_the_old_way(self):
        registry = _RegistryFrom2026_8(None)
        assert find_device(registry, _ZONE, "entry-1") is None
        assert find_device(registry, _ZONE, None) is None
        assert registry.calls == [
            ("by_identifier", _ZONE, "entry-1"),
            ("by_identifier", _ZONE, None),
        ]


async def _set_up(hass: HomeAssistant, entry, forward=None) -> bool:
    """Run async_setup_entry with store, session, panel and platforms stubbed.

    ``forward`` stands in for setting up the platforms, so a test can look at
    what setup has recorded by then.

    The stubbed session also keeps the run off aiodns, which needs a selector
    event loop on Windows; nothing here talks to the network.
    """
    entry.add_to_hass(hass)
    store = AsyncMock()
    store.async_get_config.return_value = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    store.get_config = Mock(
        return_value={
            const.CONF_AUTO_UPDATE_ENABLED: False,
            const.CONF_AUTO_CALC_ENABLED: False,
            const.CONF_USE_WEATHER_SERVICE: False,
        }
    )
    with (
        patch(
            "custom_components.irrigation_plus.async_get_registry",
            return_value=store,
        ),
        patch("custom_components.irrigation_plus.async_get_clientsession"),
        patch("custom_components.irrigation_plus.async_register_panel"),
        patch("custom_components.irrigation_plus.async_register_websockets"),
        patch("custom_components.irrigation_plus.async_register_services"),
        patch.object(
            hass.config_entries,
            "async_forward_entry_setups",
            new=forward or AsyncMock(),
        ),
    ):
        return await async_setup_entry(hass, entry)


class TestSetupRecordsTheLink:
    """``async_setup_entry`` records the link once the hub is registered."""

    async def test_on_a_2026_8_registry_it_is_the_registered_hubs_id(
        self, hass: HomeAssistant, mock_config_entry, monkeypatch
    ) -> None:
        registry = _RegistryFrom2026_8()
        monkeypatch.setattr(
            "custom_components.irrigation_plus.dr.async_get", lambda hass: registry
        )
        assert await _set_up(hass, mock_config_entry) is True
        assert hass.data[const.DOMAIN]["hub_link"] == {"via_device_id": _HUB}

    async def test_on_the_installed_registry_a_zone_device_hangs_off_the_hub(
        self, hass: HomeAssistant, mock_config_entry
    ) -> None:
        assert await _set_up(hass, mock_config_entry) is True
        registry = dr.async_get(hass)
        coordinator = hass.data[const.DOMAIN]["coordinator"]
        hub = find_device(
            registry, (const.DOMAIN, coordinator.id), mock_config_entry.entry_id
        )
        assert hass.data[const.DOMAIN]["hub_link"] == hub_link_for(
            registry, hub.id, coordinator.id
        )
        zone = registry.async_get_or_create(
            config_entry_id=mock_config_entry.entry_id,
            **zone_device_info(hass, 1, "Lawn"),
        )
        assert zone.via_device_id == hub.id

    async def test_the_link_is_recorded_afresh_before_the_platforms_load(
        self, hass: HomeAssistant, mock_config_entry, monkeypatch
    ) -> None:
        registry = _RegistryFrom2026_8()
        monkeypatch.setattr(
            "custom_components.irrigation_plus.dr.async_get", lambda _hass: registry
        )
        # hass.data[DOMAIN] outlives a reload, so an old link can still be there.
        hass.data.setdefault(const.DOMAIN, {})["hub_link"] = {"via_device_id": "old"}
        seen = []

        async def forward(entry, platforms):
            seen.append(dict(hass.data[const.DOMAIN]["hub_link"]))

        assert await _set_up(hass, mock_config_entry, forward) is True
        assert seen == [{"via_device_id": _HUB}]
        info = zone_device_info(hass, 1, "Lawn")
        assert info["via_device_id"] == _HUB
        assert "via_device" not in info


async def _delete_zone_1(monkeypatch, registry, **attrs):
    """Delete zone 1 on a coordinator built without ``__init__``.

    Only the device half of ``async_remove_entity`` does anything here: no
    entities are tracked, so the entity registry stand-in removes none.
    """
    monkeypatch.setattr(
        "custom_components.irrigation_plus.dr.async_get", lambda hass: registry
    )
    monkeypatch.setattr(
        "custom_components.irrigation_plus.er.async_get", lambda hass: Mock()
    )
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = SimpleNamespace(data={const.DOMAIN: {}})
    c.id = "cid"
    for name, value in attrs.items():
        setattr(c, name, value)
    # A test that passes no entry relies on the coordinator having none.
    assert "entry" in attrs or not hasattr(c, "entry")
    await c.async_remove_entity("1")


async def test_a_deleted_zones_device_is_found_per_entry_and_removed(monkeypatch):
    """Deleting a zone finds its device per config entry and removes it."""
    registry = _RegistryFrom2026_8(SimpleNamespace(id="dev"))
    await _delete_zone_1(
        monkeypatch, registry, entry=SimpleNamespace(entry_id="entry-1")
    )
    assert registry.calls == [
        ("by_identifier", (const.DOMAIN, "cid_zone_1"), "entry-1"),
        ("remove", "dev"),
    ]


async def test_a_zone_without_a_device_removes_nothing(monkeypatch):
    """A miss removes nothing and is not asked again the old way."""
    registry = _RegistryFrom2026_8(None)
    await _delete_zone_1(
        monkeypatch, registry, entry=SimpleNamespace(entry_id="entry-1")
    )
    assert registry.calls == [
        ("by_identifier", (const.DOMAIN, "cid_zone_1"), "entry-1"),
    ]


async def test_before_2026_8_a_zone_is_deleted_without_an_entry(monkeypatch):
    """The old lookup needs no entry, so a coordinator without one deletes."""
    registry = _RegistryBefore2026_8(SimpleNamespace(id="dev"))
    await _delete_zone_1(monkeypatch, registry)
    assert registry.calls == [
        ("get_device", {(const.DOMAIN, "cid_zone_1")}),
        ("remove", "dev"),
    ]


async def _delete_distributor_3(monkeypatch, registry, **attrs):
    """Delete distributor 3 on a host built without the coordinator's ``__init__``.

    The dispatcher is silenced; the registry and the inlet watch take part.
    """
    monkeypatch.setattr(
        "custom_components.irrigation_plus.distributor.dr.async_get",
        lambda hass: registry,
    )
    monkeypatch.setattr(
        "custom_components.irrigation_plus.distributor.async_dispatcher_send",
        lambda *a, **k: None,
    )
    c = _host()
    c.id = "cid"
    for name, value in attrs.items():
        setattr(c, name, value)
    # A test that passes no entry relies on the host having none.
    assert "entry" in attrs or not hasattr(c, "entry")
    c.store.get_distributor = Mock(return_value={"id": 3})
    c.store.async_delete_distributor = AsyncMock(return_value=True)
    return await c.async_upsert_distributor({"id": 3, "remove": True})


async def test_a_deleted_distributors_device_is_found_per_entry_and_removed(
    monkeypatch,
):
    """Deleting a distributor finds its device per config entry and removes it."""
    registry = _RegistryFrom2026_8(SimpleNamespace(id="dev123"))
    unsubscribe = Mock()
    await _delete_distributor_3(
        monkeypatch,
        registry,
        entry=SimpleNamespace(entry_id="entry-1"),
        _dist_inlet_watchers={3: unsubscribe},
    )
    assert registry.calls == [
        ("by_identifier", (const.DOMAIN, "cid_distributor_3"), "entry-1"),
        ("remove", "dev123"),
    ]
    unsubscribe.assert_called_once_with()


async def test_a_distributor_without_a_device_removes_nothing(monkeypatch):
    """A miss removes nothing, is not asked the old way, and the delete goes on."""
    registry = _RegistryFrom2026_8(None)
    unsubscribe = Mock()
    result = await _delete_distributor_3(
        monkeypatch,
        registry,
        entry=SimpleNamespace(entry_id="entry-1"),
        _dist_inlet_watchers={3: unsubscribe},
    )
    assert registry.calls == [
        ("by_identifier", (const.DOMAIN, "cid_distributor_3"), "entry-1"),
    ]
    unsubscribe.assert_called_once_with()
    assert result is True


async def test_before_2026_8_a_distributor_is_deleted_without_an_entry(monkeypatch):
    """The old lookup needs no entry, so a host without one deletes."""
    registry = _RegistryBefore2026_8(SimpleNamespace(id="dev"))
    await _delete_distributor_3(monkeypatch, registry)
    assert registry.calls == [
        ("get_device", {(const.DOMAIN, "cid_distributor_3")}),
        ("remove", "dev"),
    ]
