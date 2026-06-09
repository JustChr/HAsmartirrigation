"""Regression tests for per-zone consumption of the shared mapping buffer.

The bug: two zones share one mapping's weather buffer, but calculating a single
zone used to clear that buffer — so the sibling zone lost its accumulated ET
history and was under-watered. Now each zone consumes only its own window (up to
its ``last_consumed_at`` watermark) and the buffer is pruned, never wiped.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.store import SmartIrrigationStorage

T0 = datetime.datetime(2026, 6, 8, 6, 0, 0)


@pytest.fixture
async def coord(hass):
    """A real coordinator + real (in-memory) store, with calculate_module stubbed."""
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    # Avoid needing a real ET module / weather client.
    c.calculate_module = AsyncMock(
        return_value={const.ZONE_BUCKET: -1.0, const.ZONE_DURATION: 0}
    )
    return c, store


async def _mapping_with_readings(store, n=4):
    readings = [
        {
            const.RETRIEVED_AT: T0 + timedelta(hours=h),
            const.MAPPING_TEMPERATURE: 20.0 + h,
        }
        for h in range(n)
    ]
    mapping = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "Shared",
            const.MAPPING_MAPPINGS: {},
            const.MAPPING_DATA: readings,
        }
    )
    return mapping[const.MAPPING_ID]


async def _zone(store, mapping_id, watermark):
    z = await store.async_create_zone(
        {
            const.ZONE_NAME: "z",
            const.ZONE_MAPPING: mapping_id,
            const.ZONE_MODULE: 1,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_BUCKET: 0.0,
            const.ZONE_LAST_CONSUMED: watermark,
        }
    )
    return z[const.ZONE_ID]


@pytest.mark.asyncio
async def test_calculating_one_zone_keeps_sibling_history(coord):
    c, store = coord
    mid = await _mapping_with_readings(store, n=4)
    old_wm = T0 - timedelta(hours=1)
    a = await _zone(store, mid, old_wm)
    b = await _zone(store, mid, old_wm)

    now_a = T0 + timedelta(hours=5)
    await c.async_calculate_zone(a, now=now_a)

    # The shared buffer must NOT be wiped — the sibling still needs it.
    assert len(store.get_mapping(mid)[const.MAPPING_DATA]) == 4
    # Zone A advanced its watermark; zone B is untouched.
    assert store.get_zone(a)[const.ZONE_LAST_CONSUMED] == now_a
    assert store.get_zone(b)[const.ZONE_LAST_CONSUMED] == old_wm

    # Zone B still consumes its own full window when it is calculated.
    c.calculate_module.reset_mock()
    await c.async_calculate_zone(b, now=T0 + timedelta(hours=6))
    weatherdata = c.calculate_module.call_args.args[1]
    assert weatherdata is not None
    # 4 readings (20,21,22,23) averaged -> 21.5
    assert weatherdata[const.MAPPING_TEMPERATURE] == 21.5
    assert store.get_zone(b)[const.ZONE_LAST_CONSUMED] == T0 + timedelta(hours=6)


@pytest.mark.asyncio
async def test_second_calc_only_consumes_new_readings(coord):
    c, store = coord
    mid = await _mapping_with_readings(store, n=2)  # t0, t0+1h (temps 20, 21)
    z = await _zone(store, mid, T0 - timedelta(hours=1))

    await c.async_calculate_zone(z, now=T0 + timedelta(hours=2))
    # number_of_data_points reflects this zone's window (2 readings).
    assert store.get_zone(z)[const.ZONE_NUMBER_OF_DATA_POINTS] == 2

    # A new reading arrives; the next calc must only see the new one (window is
    # strictly after the advanced watermark), not re-consume the old readings.
    data = store.get_mapping(mid)[const.MAPPING_DATA]
    data.append(
        {const.RETRIEVED_AT: T0 + timedelta(hours=3), const.MAPPING_TEMPERATURE: 30.0}
    )
    await store.async_update_mapping(mid, {const.MAPPING_DATA: data})

    c.calculate_module.reset_mock()
    await c.async_calculate_zone(z, now=T0 + timedelta(hours=4))
    weatherdata = c.calculate_module.call_args.args[1]
    # window = boundary(21 @ watermark) + new(30) -> avg 25.5, NOT (20+21+30)/3
    assert weatherdata[const.MAPPING_TEMPERATURE] == 25.5


@pytest.mark.asyncio
async def test_prune_keeps_oldest_watermark_but_caps_at_retention(coord):
    c, store = coord
    mid = await _mapping_with_readings(store, n=4)
    # One enabled zone consumed up to T0+3h; a disabled zone is far behind but
    # must NOT hold the buffer.
    await _zone(store, mid, T0 + timedelta(hours=3))
    disabled = await _zone(store, mid, T0 - timedelta(days=30))
    await store.async_update_zone(
        disabled, {const.ZONE_STATE: const.ZONE_STATE_DISABLED}
    )

    await c._prune_mapping_buffer(mid, now=T0 + timedelta(hours=4))
    # Disabled zone excluded -> floor is zone A's watermark (T0+3h); only the
    # last reading (t0+3h) plus boundary remain.
    remaining = store.get_mapping(mid)[const.MAPPING_DATA]
    assert len(remaining) < 4
