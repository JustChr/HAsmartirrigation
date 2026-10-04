"""The sensor group's outage record and signs of life in the real store."""

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.store import STORAGE_KEY, SmartIrrigationStorage

OUTAGE = {
    "entity_id": "sensor.t",
    "device_id": "dev1",
    "fields": ["Temperature"],
    "start": "2026-07-01T08:00:00",
    "end": None,
}


async def _store_with_two_groups(hass):
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    a = await store.async_create_mapping(
        {const.MAPPING_NAME: "A", const.MAPPING_MAPPINGS: {}}
    )
    b = await store.async_create_mapping(
        {const.MAPPING_NAME: "B", const.MAPPING_MAPPINGS: {}}
    )
    return store, a[const.MAPPING_ID], b[const.MAPPING_ID]


@pytest.mark.asyncio
async def test_a_new_group_has_no_outages_and_no_signs(hass) -> None:
    store, a, _ = await _store_with_two_groups(hass)
    assert store.get_mapping(a)[const.MAPPING_SENSOR_OUTAGES] == []
    assert store.get_mapping(a)[const.MAPPING_SENSOR_LAST_SEEN] == {}


@pytest.mark.asyncio
async def test_signs_of_life_are_not_shared_between_groups(hass) -> None:
    store, a, b = await _store_with_two_groups(hass)
    store.set_mapping_sensor_last_seen(a, {"sensor.t": "2026-07-01T12:00:00"})
    assert store.get_mapping(b)[const.MAPPING_SENSOR_LAST_SEEN] == {}


@pytest.mark.asyncio
async def test_refreshing_the_signs_schedules_no_write(hass) -> None:
    """Refreshed at every check; a write each time would cost a whole document every
    few minutes for a value that only matters across a restart. It rides along."""
    store, a, _ = await _store_with_two_groups(hass)
    writes = []
    store._store.async_delay_save = lambda func, delay=0: writes.append(func)

    store.set_mapping_sensor_last_seen(a, {"sensor.t": "2026-07-01T12:00:00"})

    assert writes == []
    routine = store._data_to_save()["mappings"]
    assert routine[0][const.MAPPING_SENSOR_LAST_SEEN] == {
        "sensor.t": "2026-07-01T12:00:00"
    }


@pytest.mark.asyncio
async def test_outages_and_signs_survive_a_restart(hass, hass_storage) -> None:
    store, a, _ = await _store_with_two_groups(hass)
    await store.async_update_mapping(a, {const.MAPPING_SENSOR_OUTAGES: [OUTAGE]})
    store.set_mapping_sensor_last_seen(a, {"sensor.t": "2026-07-01T08:00:00"})
    await store.async_save()

    reloaded = SmartIrrigationStorage(hass)
    await reloaded.async_load()

    assert reloaded.get_mapping(a)[const.MAPPING_SENSOR_OUTAGES] == [OUTAGE]
    assert reloaded.get_mapping(a)[const.MAPPING_SENSOR_LAST_SEEN] == {
        "sensor.t": "2026-07-01T08:00:00"
    }


@pytest.mark.asyncio
async def test_a_document_written_before_these_fields_still_loads(
    hass, hass_storage
) -> None:
    store, a, _ = await _store_with_two_groups(hass)
    await store.async_save()
    for mapping in hass_storage[STORAGE_KEY]["data"]["mappings"]:
        mapping.pop(const.MAPPING_SENSOR_OUTAGES, None)
        mapping.pop(const.MAPPING_SENSOR_LAST_SEEN, None)

    reloaded = SmartIrrigationStorage(hass)
    await reloaded.async_load()

    assert reloaded.get_mapping(a)[const.MAPPING_SENSOR_OUTAGES] == []
    assert reloaded.get_mapping(a)[const.MAPPING_SENSOR_LAST_SEEN] == {}


@pytest.mark.asyncio
async def test_a_panel_save_leaves_the_outages_alone(hass) -> None:
    """The panel sends id, name and mappings only (view-mappings.ts), and the
    mapping view's schema admits no other key; what it omits must survive."""
    store, a, _ = await _store_with_two_groups(hass)
    await store.async_update_mapping(a, {const.MAPPING_SENSOR_OUTAGES: [OUTAGE]})

    await store.async_update_mapping(
        a, {const.MAPPING_NAME: "renamed", const.MAPPING_MAPPINGS: {}}
    )

    assert store.get_mapping(a)[const.MAPPING_SENSOR_OUTAGES] == [OUTAGE]


@pytest.mark.asyncio
async def test_a_clean_stop_writes_the_refreshed_signs(hass) -> None:
    """The signs change at every check and schedule no write; a clean restart
    must still keep them, because nothing else can rebuild them."""
    store, a, _ = await _store_with_two_groups(hass)
    await store.async_save()
    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)

    store.set_mapping_sensor_last_seen(a, {"sensor.t": "2026-07-01T12:00:00"})
    store.async_flush_buffers()
    assert pending == []  # still no write per check, nor per backstop tick

    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()

    assert pending, "a clean stop must queue the refreshed signs"
    assert pending[-1]()["mappings"][0][const.MAPPING_SENSOR_LAST_SEEN] == {
        "sensor.t": "2026-07-01T12:00:00"
    }


@pytest.mark.asyncio
async def test_unchanged_signs_queue_no_stop_write(hass) -> None:
    store, a, _ = await _store_with_two_groups(hass)
    store.set_mapping_sensor_last_seen(a, {"sensor.t": "2026-07-01T12:00:00"})
    await store.async_save()
    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)

    store.set_mapping_sensor_last_seen(a, {"sensor.t": "2026-07-01T12:00:00"})
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()

    assert pending == []


@pytest.mark.asyncio
async def test_a_deleted_config_is_not_written_back_for_the_signs(hass) -> None:
    store, a, _ = await _store_with_two_groups(hass)
    store.set_mapping_sensor_last_seen(a, {"sensor.t": "2026-07-01T12:00:00"})

    await store.async_delete()

    pending = []
    store._store.async_delay_save = lambda func, delay=0: pending.append(func)
    store.async_ensure_stop_listener()
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()
    assert pending == []


@pytest.mark.asyncio
async def test_signs_that_are_not_a_dict_load_as_none(hass, hass_storage) -> None:
    store, a, _ = await _store_with_two_groups(hass)
    await store.async_save()
    for mapping in hass_storage[STORAGE_KEY]["data"]["mappings"]:
        mapping[const.MAPPING_SENSOR_LAST_SEEN] = ["sensor.t"]

    reloaded = SmartIrrigationStorage(hass)
    await reloaded.async_load()

    assert reloaded.get_mapping(a)[const.MAPPING_SENSOR_LAST_SEEN] == {}
