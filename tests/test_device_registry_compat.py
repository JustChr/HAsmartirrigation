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
