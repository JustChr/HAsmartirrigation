"""Sensor-reading buffers are persisted apart from the routine store write.

Every ``async_schedule_save()`` reserializes the WHOLE document and replaces the
file, so while the reading buffers lived on ``MappingEntry`` each ingested
reading dragged the entire configuration through a serialize+replace — and total
bytes written grew with the SQUARE of the readings per cycle. The buffers now
live in ``SmartIrrigationStorage.buffers``: an append costs nothing on disk, and
the rows reach the file on the flush timer, on any write somebody else triggers,
or at shutdown.

The invariant these tests protect: **a document is never written with the
``data`` key missing while ANY buffered readings exist** — not merely while
unpersisted ones do. Writing the routine payload does not omit the buffer, it
DELETES it from the stored document, so the loss is never "the last few minutes
of readings", it is always the whole buffer.

That distinction is the bug this file now guards: the check used to be "are there
unpersisted appends", which goes false the moment a full write lands, after which
the next unrelated write quietly erased everything.
"""

import datetime
from unittest.mock import AsyncMock, Mock

import attr
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
async def test_carry_forward_refresh_schedules_no_write_either(hass) -> None:
    """The companion to the append, and the subtler half of it.

    Continuous updates refresh ``data_last_entry`` on EVERY reading. It is a
    MappingEntry field, so evolving it through the normal ``async_update_mapping``
    would schedule a whole-document write per reading — reintroducing exactly the
    cost the buffer split removed, through the one field an append still touches.
    """
    store, mid = await _store_with_mapping(hass)
    writes = []
    store._store.async_delay_save = lambda func, delay=0: writes.append(func)

    store.set_mapping_last_entry_value(mid, const.MAPPING_TEMPERATURE, 21.5)

    assert writes == []
    assert store.get_mapping(mid)[const.MAPPING_DATA_LAST_ENTRY] == {
        const.MAPPING_TEMPERATURE: 21.5
    }


@pytest.mark.asyncio
async def test_carry_forward_rides_out_on_the_next_write(hass) -> None:
    """It needs no dirty flag: it is in the ROUTINE payload, so any write carries
    it. That is what makes losing it to a hard crash acceptable — and it is
    recoverable anyway, being just the newest value per field in the buffer.
    """
    store, mid = await _store_with_mapping(hass)
    store.set_mapping_last_entry_value(mid, const.MAPPING_TEMPERATURE, 21.5)

    routine = store._data_to_save()
    assert routine["mappings"][0][const.MAPPING_DATA_LAST_ENTRY] == {
        const.MAPPING_TEMPERATURE: 21.5
    }


@pytest.mark.asyncio
async def test_carry_forward_is_not_shared_between_sensor_groups(hass) -> None:
    """MappingEntry.data_last_entry's attrs default is ONE shared ``{}`` object.

    Mutating it in place would leak one sensor group's carry-forward into every
    other group that was created without an explicit value — a cross-contaminated
    ET input, silently.
    """
    store, first = await _store_with_mapping(hass)
    second = (
        await store.async_create_mapping(
            {const.MAPPING_NAME: "Other", const.MAPPING_MAPPINGS: {}}
        )
    )[const.MAPPING_ID]

    store.set_mapping_last_entry_value(first, const.MAPPING_TEMPERATURE, 21.5)

    assert store.get_mapping(second)[const.MAPPING_DATA_LAST_ENTRY] == {}


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
    # …and a SECOND write, with the flag now clean, must still carry them. This
    # line previously asserted the opposite and locked in a silent data loss:
    # writing the buffer-less payload deletes the rows from the document, so the
    # next clean restart came up with an empty buffer. See
    # test_routine_write_never_deletes_a_persisted_buffer.
    assert store._data_to_save_scheduled()["mappings"][0][const.MAPPING_DATA] == [
        _reading()
    ]


@pytest.mark.asyncio
async def test_routine_write_never_deletes_a_persisted_buffer(hass) -> None:
    """Regression: a clean restart used to come up with an empty buffer.

    Found by running the branch against a real config — 305 readings, a whole
    calculation window, gone. The sequence is entirely ordinary:

      1. load (or any full write) puts the buffer in the file and clears the flag
      2. ANY unrelated write — a zone's last_updated, a config change — then
         emitted the buffer-less payload, DELETING the rows from the document
      3. nothing marked them unpersisted again, so neither the flush timer nor the
         shutdown listener would restore them
      4. clean restart -> ``data`` key absent -> empty buffer, no error anywhere

    The failure surfaces as one silently under-watered day, not an exception,
    which is exactly why it needs a test rather than a comment.
    """
    store, mid = await _store_with_mapping(hass)
    zone = await store.async_create_zone({const.ZONE_NAME: "z"})
    store.append_mapping_reading(mid, _reading())

    # Step 1: a full write persists the rows and clears the dirty flag.
    assert store._data_to_save_full()["mappings"][0][const.MAPPING_DATA] == [_reading()]
    assert store._buffers_dirty is False

    # Step 2: an unrelated write, with nothing appended since. The payload it
    # emits is what lands on disk — it MUST still contain the readings.
    await store.async_update_zone(zone[const.ZONE_ID], {const.ZONE_LAST_UPDATED: T0})
    payload = store._data_to_save_scheduled()
    assert payload["mappings"][0][const.MAPPING_DATA] == [
        _reading()
    ], "an unrelated write erased the buffer from the stored document"


@pytest.mark.asyncio
async def test_buffer_survives_a_clean_restart_after_an_unrelated_write(
    hass, hass_storage
) -> None:
    """The same bug, end to end through the file: write, reload, rows still there.

    Mirrors what the live instance did — poll, unrelated config write, restart —
    with the reload standing in for the restart.
    """
    store, mid = await _store_with_mapping(hass)
    store.append_mapping_reading(mid, _reading())
    await store.async_save()  # rows reach the file; flag goes clean

    # An unrelated write lands while nothing new has been appended.
    store.config = attr.evolve(store.config, calctime="03:00")
    await store._store.async_save(store._data_to_save_scheduled())

    # "Restart": a fresh storage instance reading the same document.
    reloaded = SmartIrrigationStorage(hass)
    await reloaded.async_load()
    assert reloaded.get_mapping_buffer(mid) == [
        _reading()
    ], "the buffer did not survive a clean restart"


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

    # The constructor arms the local-midnight tracker (__init__.py, "set up
    # midnight tracking"). Disarm it before jumping the clock: the jumps below
    # cross local midnight whenever the real wall clock happens to sit within
    # BUFFER_FLUSH_INTERVAL of it, and _reset_event_fired_today would then fire
    # _increment_days_since_irrigation against this AsyncMock store, raising
    # `TypeError: coroutine + int` inside an HA job. The hass fixture re-raises
    # that at teardown, so the test errors purely as a function of the time of
    # day it is run at. Nothing here is about the midnight timer.
    coordinator._track_midnight_time_unsub()
    coordinator._track_midnight_time_unsub = None

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
async def test_deleting_the_config_does_not_let_the_buffer_resurrect_it(hass) -> None:
    """Store.async_remove cancels HA's own pending writes so a deleted document
    stays deleted. A dirty buffer plus our shutdown listener would undo that and
    write the just-deleted configuration back at the next shutdown.
    """
    store, mid = await _store_with_mapping(hass)
    store.append_mapping_reading(mid, _reading())

    await store.async_delete()
    assert store._buffers_dirty is False
    assert store.buffers == {}

    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()
    assert pending == []


@pytest.mark.asyncio
async def test_re_adding_the_integration_re_arms_the_shutdown_flush(hass) -> None:
    """Deleting the config entry unregisters the shutdown listener; re-adding the
    integration must get it back.

    The storage instance is cached in ``hass.data`` for the lifetime of hass, so
    ``async_load`` — which is where the listener is normally armed — runs exactly
    once. Without re-arming on setup, the sequence "remove the integration, add it
    again, don't restart HA" left the buffer with no shutdown flush for the rest of
    the session: a clean restart would then lose up to BUFFER_FLUSH_INTERVAL of
    readings instead of nothing, with no error to show for it.
    """
    from custom_components.smart_irrigation.store import (
        DATA_REGISTRY,
        async_get_registry,
    )

    store = await async_get_registry(hass)
    mapping = await store.async_create_mapping(
        {const.MAPPING_NAME: "Group", const.MAPPING_MAPPINGS: {}}
    )
    mid = mapping[const.MAPPING_ID]

    # Remove the config entry: the listener goes, so a stale buffer cannot write
    # the just-deleted document back at shutdown.
    await store.async_delete()
    assert store._unsub_stop is None

    # Re-add without restarting hass: same cached instance, no second async_load.
    again = await async_get_registry(hass)
    assert again is store, "precondition: the instance is cached for hass's lifetime"
    assert hass.data[DATA_REGISTRY] is not None

    # The shutdown flush must work again.
    store.append_mapping_reading(mid, _reading())
    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()

    assert pending, "re-adding the integration left the shutdown flush unarmed"
    assert pending[-1]()["mappings"][0][const.MAPPING_DATA] == [_reading()]


@pytest.mark.asyncio
async def test_ensure_stop_listener_does_not_stack_subscriptions(hass) -> None:
    """Repeated setups must not pile up duplicate one-shot listeners."""
    store, _mid = await _store_with_mapping(hass)
    first = store._unsub_stop
    assert first is not None

    store.async_ensure_stop_listener()
    store.async_ensure_stop_listener()

    assert store._unsub_stop is first


@pytest.mark.asyncio
async def test_panel_weather_records_still_see_the_buffer(hass) -> None:
    """The panel's Weather Records table reads the buffer through its own
    accessor now. Worth asserting: the handler catches every exception and
    returns [], so a broken read would show up as an empty table, not an error.
    """
    from custom_components.smart_irrigation.websockets import (
        websocket_get_weather_records,
    )

    store, mid = await _store_with_mapping(hass)
    store.append_mapping_reading(mid, _reading(0, 20.0))
    store.append_mapping_reading(mid, _reading(1, 21.0))
    hass.data[const.DOMAIN] = {"coordinator": Mock(store=store)}

    connection = Mock()
    await websocket_get_weather_records.__wrapped__(
        hass, connection, {"id": 1, "mapping_id": mid, "limit": 10}
    )
    records = connection.send_result.call_args.args[1]
    assert [r["temperature"] for r in records] == [21.0, 20.0]  # newest first


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
