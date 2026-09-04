"""'Clear all weather data' must not leave the deadband holding a stale reference.

The deadband compares each reading against the last APPENDED value, which lives
on the coordinator rather than in the store — so emptying the buffers does not
touch it. On a pure-sensor group the interval poll is skipped, making the event
handler the only writer, and a suppressed reading does NOT advance the
reference. Left stale, the reset therefore blocks the very readings that would
refill the buffer it just emptied, until something moves further than the
threshold: minutes for temperature, a whole night for solar radiation.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.continuous_update import SENSOR_DEADBAND

from .test_continuous_update import _coord, _drain, _event, _FakeStore, _mapping

_TEMP_DEADBAND = SENSOR_DEADBAND[const.MAPPING_TEMPERATURE]


@pytest.fixture(autouse=True)
def _stub_hass_helpers(monkeypatch):
    """Same stubs test_continuous_update uses; autouse fixtures are per-module."""
    monkeypatch.setattr(
        "custom_components.irrigation_plus.continuous_update."
        "async_track_state_change_event",
        Mock(return_value=Mock()),
    )
    monkeypatch.setattr(
        "custom_components.irrigation_plus.continuous_update.async_call_later",
        Mock(side_effect=lambda *_args, **_kw: Mock()),
    )
    for module in (
        "custom_components.irrigation_plus.continuous_update",
        "custom_components.irrigation_plus",
        "custom_components.irrigation_plus.calculation",
    ):
        monkeypatch.setattr(f"{module}.async_dispatcher_send", Mock())


async def _reset_all_weatherdata(coord):
    coord.store.async_get_zones = AsyncMock(return_value=[])
    coord.store.async_update_zone = AsyncMock()
    await coord._async_clear_all_weatherdata()


@pytest.mark.asyncio
async def test_a_reading_inside_the_deadband_is_recorded_after_a_reset():
    store = _FakeStore([_mapping()])
    coord = _coord(store)
    await coord.async_setup_continuous_updates()

    coord._sensor_state_changed(_event("sensor.temp", "20.0"))
    await _drain(coord)
    assert len(store.buffers[1]) == 1

    await _reset_all_weatherdata(coord)
    assert store.buffers[1] == []

    # Well inside the deadband of the pre-reset 20.0: before the fix this was
    # dropped and the buffer stayed empty.
    nudge = 20.0 + _TEMP_DEADBAND / 2
    coord._sensor_state_changed(_event("sensor.temp", str(nudge)))
    await _drain(coord)

    assert (
        len(store.buffers[1]) == 1
    ), "the first reading after a reset must always be recorded"
    assert store.buffers[1][0][const.MAPPING_TEMPERATURE] == pytest.approx(nudge)


@pytest.mark.asyncio
async def test_the_reset_clears_the_deadband_reference_itself():
    store = _FakeStore([_mapping()])
    coord = _coord(store)
    await coord.async_setup_continuous_updates()
    coord._sensor_state_changed(_event("sensor.temp", "20.0"))
    await _drain(coord)
    assert coord._continuous_last_value

    await _reset_all_weatherdata(coord)

    assert coord._continuous_last_value == {}
    assert coord._continuous_flush_count == {}


@pytest.mark.asyncio
async def test_the_reset_keeps_the_subscription_alive():
    """Narrower than a teardown: the entity set did not change."""
    store = _FakeStore([_mapping()])
    coord = _coord(store)
    await coord.async_setup_continuous_updates()
    before = coord._continuous_entities

    await _reset_all_weatherdata(coord)

    assert coord._continuous_entities == before
    assert coord._continuous_unsub is not None
    # And it still ingests, without needing a resubscribe.
    coord._sensor_state_changed(_event("sensor.temp", "25.0"))
    await _drain(coord)
    assert len(store.buffers[1]) == 1


@pytest.mark.asyncio
async def test_deadband_still_suppresses_a_tiny_move_when_no_reset_happened():
    """Guards the fix from becoming 'the deadband never applies'."""
    store = _FakeStore([_mapping()])
    coord = _coord(store)
    await coord.async_setup_continuous_updates()

    coord._sensor_state_changed(_event("sensor.temp", "20.0"))
    await _drain(coord)
    coord._sensor_state_changed(_event("sensor.temp", str(20.0 + _TEMP_DEADBAND / 2)))
    await _drain(coord)

    assert len(store.buffers[1]) == 1
