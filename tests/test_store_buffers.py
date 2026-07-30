"""Sensor-reading buffers are persisted apart from the routine store write.

Every ``async_schedule_save()`` reserializes the WHOLE document and replaces the
file, so while the reading buffers lived on ``MappingEntry`` each ingested
reading dragged the entire configuration through a serialize+replace — and total
bytes written grew with the SQUARE of the readings per cycle. The buffers now
live in ``SmartIrrigationStorage.buffers``: an append costs nothing on disk, and
the rows reach the file on the flush timer, on any write somebody else triggers,
or at shutdown.

The invariant these tests protect: **a document is never written with the
``data`` key missing while unpersisted readings exist.** The routine payload
omits the buffer, so writing it while dirty would not lose the last few minutes
of readings — it would silently discard the whole buffer.
"""

import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.store import (
    BUFFER_FLUSH_INTERVAL,
    STORAGE_KEY,
    STORAGE_VERSION,
    SmartIrrigationStorage,
)

T0 = datetime.datetime(2026, 7, 30, 6, 0, 0)


def _reading(offset_h=0, temp=20.0):
    return {
        const.RETRIEVED_AT: (T0 + datetime.timedelta(hours=offset_h)).isoformat(),
        const.MAPPING_TEMPERATURE: temp,
    }


async def _store_with_mapping(hass):
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    mapping = await store.async_create_mapping(
        {const.MAPPING_NAME: "Group", const.MAPPING_MAPPINGS: {}}
    )
    return store, mapping[const.MAPPING_ID]


@pytest.mark.asyncio
async def test_routine_payload_omits_buffer_full_payload_carries_it(hass) -> None:
    store, mid = await _store_with_mapping(hass)
    store.append_mapping_reading(mid, _reading())

    routine = store._data_to_save()
    assert const.MAPPING_DATA not in routine["mappings"][0]

    full = store._data_to_save_full()
    assert full["mappings"][0][const.MAPPING_DATA] == [_reading()]
    # Everything else must be identical — this is one document, not two stores.
    assert full["config"] == routine["config"]
    assert full["zones"] == routine["zones"]


@pytest.mark.asyncio
async def test_append_schedules_no_write_but_marks_the_buffer_dirty(hass) -> None:
    """The whole point: ingestion does not touch the disk."""
    store, mid = await _store_with_mapping(hass)
    writes = []
    store._store.async_delay_save = lambda func, delay=0: writes.append(func)

    assert store.append_mapping_reading(mid, _reading()) is True
    assert writes == []
    assert store._buffers_dirty is True
    assert store.get_mapping_row_count(mid) == 1


@pytest.mark.asyncio
async def test_a_write_by_anyone_else_carries_the_buffer(hass) -> None:
    """The failure this guards: a zone write emitting the buffer-less payload
    while readings are unpersisted would discard every buffered row, not just
    the recent ones.
    """
    store, mid = await _store_with_mapping(hass)
    zone = await store.async_create_zone({const.ZONE_NAME: "z"})
    store.append_mapping_reading(mid, _reading())

    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)
    # Exactly what the ingestion follow-up does: stamp the zone's last_updated.
    await store.async_update_zone(zone[const.ZONE_ID], {const.ZONE_LAST_UPDATED: T0})

    assert pending, "a zone update must still schedule a write"
    payload = pending[-1]()
    assert payload["mappings"][0][const.MAPPING_DATA] == [_reading()]
    # Evaluating the payload is the moment the rows are on their way to the file.
    assert store._buffers_dirty is False
    assert const.MAPPING_DATA not in store._data_to_save_scheduled()["mappings"][0]


@pytest.mark.asyncio
async def test_flush_is_a_noop_until_something_is_buffered(hass) -> None:
    store, mid = await _store_with_mapping(hass)
    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)

    store.async_flush_buffers()
    assert pending == [], "a clean buffer must not add a write cadence of its own"

    store.append_mapping_reading(mid, _reading())
    store.async_flush_buffers()
    assert len(pending) == 1
    assert pending[0]()["mappings"][0][const.MAPPING_DATA] == [_reading()]


@pytest.mark.asyncio
async def test_shutdown_queues_the_buffer_for_has_final_write(hass) -> None:
    store, mid = await _store_with_mapping(hass)
    store.append_mapping_reading(mid, _reading())
    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)

    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()

    assert pending, "the buffer must be queued for the shutdown write"
    assert pending[-1]()["mappings"][0][const.MAPPING_DATA] == [_reading()]


@pytest.mark.asyncio
async def test_buffer_round_trips_through_the_file(hass, hass_storage) -> None:
    store, mid = await _store_with_mapping(hass)
    store.append_mapping_reading(mid, _reading())
    await store.async_save()

    stored = hass_storage[STORAGE_KEY]["data"]["mappings"][0]
    assert stored[const.MAPPING_DATA] == [_reading()]

    reloaded = SmartIrrigationStorage(hass)
    await reloaded.async_load()
    assert reloaded.get_mapping_buffer(mid) == [_reading()]
    assert reloaded._buffers_dirty is False


@pytest.mark.asyncio
async def test_load_tolerates_a_document_written_without_a_buffer(
    hass, hass_storage
) -> None:
    """No migration needed: the routine payload's shape must load cleanly.

    Also covers the legacy attrs default, which was the *string* "[]".
    """
    hass_storage[STORAGE_KEY] = {
        "version": STORAGE_VERSION,
        "data": {
            "config": {},
            "zones": [],
            "modules": [],
            "mappings": [
                {const.MAPPING_ID: 0, const.MAPPING_NAME: "No data", "mappings": {}},
                {
                    const.MAPPING_ID: 1,
                    const.MAPPING_NAME: "Legacy",
                    "mappings": {},
                    const.MAPPING_DATA: "[]",
                },
            ],
        },
    }
    store = SmartIrrigationStorage(hass)
    await store.async_load()

    assert store.get_mapping_buffer(0) == []
    assert store.get_mapping_buffer(1) == []
    assert store.get_mapping_row_count(0) == 0
    # Unknown sensor group: distinguishable from "known but empty".
    assert store.get_mapping_row_count(99) is None
    assert store.append_mapping_reading(99, _reading()) is False


@pytest.mark.asyncio
async def test_coordinator_arms_and_cancels_the_flush_timer(hass) -> None:
    """Without this timer a quiet install would hold readings in memory only —
    nothing else writes, because appends deliberately do not.
    """
    store = AsyncMock()
    store.get_config = Mock(
        return_value={
            const.CONF_AUTO_UPDATE_ENABLED: False,
            const.CONF_AUTO_CALC_ENABLED: False,
            const.CONF_USE_WEATHER_SERVICE: False,
        }
    )
    store.async_flush_buffers = Mock()
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    entry = Mock(unique_id="t", data={}, options={})
    coordinator = SmartIrrigationCoordinator(hass, None, entry, store)
    assert coordinator._track_buffer_flush_unsub is None

    await coordinator.async_setup_timers()
    assert coordinator._track_buffer_flush_unsub is not None

    async_fire_time_changed(
        hass, dt_util.utcnow() + datetime.timedelta(seconds=BUFFER_FLUSH_INTERVAL + 1)
    )
    await hass.async_block_till_done()
    assert store.async_flush_buffers.called

    # A reloaded coordinator must not leave this ticking (it would ghost-write).
    store.async_flush_buffers.reset_mock()
    await coordinator.async_unload()
    assert coordinator._track_buffer_flush_unsub is None
    async_fire_time_changed(
        hass,
        dt_util.utcnow() + datetime.timedelta(seconds=2 * BUFFER_FLUSH_INTERVAL + 2),
    )
    await hass.async_block_till_done()
    assert not store.async_flush_buffers.called


@pytest.mark.asyncio
async def test_incoming_data_key_is_routed_to_the_buffer(hass) -> None:
    """``data`` arrives inside change dicts (stored records, the mapping API, the
    source-change invalidation), so create/update must accept it even though it
    is no longer a MappingEntry field.
    """
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    mapping = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "Group",
            const.MAPPING_MAPPINGS: {},
            const.MAPPING_DATA: [_reading(), _reading(1, 21.0)],
        }
    )
    mid = mapping[const.MAPPING_ID]
    assert const.MAPPING_DATA not in mapping
    assert store.get_mapping_row_count(mid) == 2

    await store.async_update_mapping(mid, {const.MAPPING_DATA: []})
    assert store.get_mapping_buffer(mid) == []

    # A deleted sensor group must not leave its buffer behind for the next
    # mapping that gets handed the same id.
    store.append_mapping_reading(mid, _reading())
    await store.async_delete_mapping(mid)
    assert store.buffers.get(mid) is None
    assert store.get_mapping_row_count(mid) is None
