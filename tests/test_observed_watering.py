"""Observed watering extended to service/self-closing zones (Phase 1)."""

import attr

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.store import ZoneEntry


def test_zone_observed_entity_defaults_none():
    field = attr.fields_dict(ZoneEntry)["observed_entity"]
    assert field.default is None
    assert const.ZONE_OBSERVED_ENTITY == "observed_entity"


from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.smart_irrigation import SmartIrrigationCoordinator


@pytest.fixture(autouse=True)
def _stub_state_tracker(monkeypatch):
    # async_setup_observed_watering subscribes via async_track_state_change_event,
    # a real HA helper that needs a live hass.data. These unit tests build a Mock
    # hass, so stub the tracker to a no-op returning a Mock unsub — this exercises
    # the entity_map build (the code under test) without standing up HA core.
    monkeypatch.setattr(
        "custom_components.smart_irrigation.observed_watering."
        "async_track_state_change_event",
        Mock(return_value=Mock()),
    )


def _obs_coord(zones, enabled=True):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.hass = Mock()  # async_track_state_change_event returns a Mock
    coord.store = Mock()
    coord.store.config = SimpleNamespace(observed_watering_enabled=enabled)
    coord.store.async_get_zones = AsyncMock(return_value=zones)
    coord._observed_entities = frozenset()
    coord._observed_unsub = None
    coord._observed_on_since = {}
    coord._observed_zone_by_entity = {}
    return coord


async def test_setup_maps_observed_entity_for_service_zone():
    coord = _obs_coord([{const.ZONE_ID: 1, const.ZONE_OBSERVED_ENTITY: "switch.beet"}])
    await coord.async_setup_observed_watering()
    assert coord._observed_zone_by_entity == {"switch.beet": 1}


async def test_setup_prefers_linked_entity_over_observed():
    coord = _obs_coord([{const.ZONE_ID: 1, const.ZONE_LINKED_ENTITY: "switch.lawn",
                         const.ZONE_OBSERVED_ENTITY: "switch.other"}])
    await coord.async_setup_observed_watering()
    assert coord._observed_zone_by_entity == {"switch.lawn": 1}


async def test_setup_maps_nothing_when_feature_off():
    coord = _obs_coord([{const.ZONE_ID: 1, const.ZONE_OBSERVED_ENTITY: "switch.beet"}],
                       enabled=False)
    await coord.async_setup_observed_watering()
    assert coord._observed_zone_by_entity == {}
