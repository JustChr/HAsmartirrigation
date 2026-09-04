"""Regression tests: pruning must not destroy a sparse field's delta baseline.

The bug: the event-driven ingestion path writes SPARSE rows (one field per
event), but ``_prune_mapping_buffer`` kept a single boundary row for the whole
mapping — whichever field happened to produce the last pre-cutoff row. Every
other field lost the reading its DELTA/RIEMANN aggregation uses as a baseline.
Observed live: a cumulative rain gauge rose 1.15 -> 1.50 in straight after a
calculation's prune, and both the live estimate's ``precip_since`` and the next
daily aggregation read 0.0 for it — the rise was silently uncounted, in the
direction that over-waters.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.store import SmartIrrigationStorage
from custom_components.irrigation_plus.weather_aggregate import (
    aggregate_window,
    build_substeps,
)

T0 = datetime.datetime(2026, 6, 8, 6, 0, 0)

PRECIP_DELTA_CONFIG = {
    const.MAPPING_PRECIPITATION: {
        const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
        const.MAPPING_CONF_AGGREGATE: const.MAPPING_CONF_AGGREGATE_DELTA,
    }
}


@pytest.fixture
async def coord(hass):
    """A real coordinator + real (in-memory) store, calculate_module stubbed."""
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
    c.calculate_module = AsyncMock(
        return_value={const.ZONE_BUCKET: -1.0, const.ZONE_DURATION: 0}
    )
    return c, store


async def _sparse_mapping(store):
    """A sparse buffer: the rain gauge's last pre-cutoff row is NOT the
    mapping's last pre-cutoff row (a temperature event came after it)."""
    readings = [
        {const.RETRIEVED_AT: T0, const.MAPPING_PRECIPITATION: 25.0},
        {const.RETRIEVED_AT: T0 + timedelta(hours=1), const.MAPPING_TEMPERATURE: 20.0},
    ]
    mapping = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "Sparse",
            const.MAPPING_MAPPINGS: PRECIP_DELTA_CONFIG,
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
async def test_gauge_rise_straddling_a_prune_is_counted(coord):
    c, store = coord
    mid = await _sparse_mapping(store)
    watermark = T0 + timedelta(hours=2)
    await _zone(store, mid, watermark)

    # The calculation's prune: every row is at-or-before the watermark.
    await c._prune_mapping_buffer(mid, now=watermark)

    # The gauge rises after the prune — one new row inside the next window.
    store.append_mapping_reading(
        mid,
        {
            const.RETRIEVED_AT: T0 + timedelta(hours=3),
            const.MAPPING_PRECIPITATION: 30.0,
        },
    )

    agg = aggregate_window(
        store.get_mapping_buffer(mid),
        watermark,
        PRECIP_DELTA_CONFIG,
        now=T0 + timedelta(hours=4),
    )
    # The rise is 5.0 mm. Losing the 25.0 baseline reads it as 0.0.
    assert agg[const.MAPPING_PRECIPITATION] == pytest.approx(5.0)


def test_delta_baseline_survives_a_later_row_of_another_field():
    """No prune involved: the sparse buffer is intact, but the gauge's last
    pre-watermark row is displaced as THE boundary by a later temperature event.
    The straddling rise must still count."""
    watermark = T0 + timedelta(hours=2)
    buf = [
        {const.RETRIEVED_AT: T0, const.MAPPING_PRECIPITATION: 25.0},
        {const.RETRIEVED_AT: T0 + timedelta(hours=1), const.MAPPING_TEMPERATURE: 20.0},
        {
            const.RETRIEVED_AT: T0 + timedelta(hours=3),
            const.MAPPING_PRECIPITATION: 30.0,
        },
    ]
    agg = aggregate_window(
        buf, watermark, PRECIP_DELTA_CONFIG, now=T0 + timedelta(hours=4)
    )
    assert agg[const.MAPPING_PRECIPITATION] == pytest.approx(5.0)


def test_substeps_agree_with_the_aggregate_across_the_baseline():
    """The replayed balance cuts its steps from the same rows: its per-step
    precipitation must reconcile with the aggregate's total (the live estimate
    lumps the window when they disagree)."""
    watermark = T0 + timedelta(hours=2)
    buf = [
        {const.RETRIEVED_AT: T0, const.MAPPING_PRECIPITATION: 25.0},
        {const.RETRIEVED_AT: T0 + timedelta(hours=1), const.MAPPING_TEMPERATURE: 20.0},
        {
            const.RETRIEVED_AT: T0 + timedelta(hours=3),
            const.MAPPING_PRECIPITATION: 30.0,
        },
    ]
    steps = build_substeps(
        buf, watermark, PRECIP_DELTA_CONFIG, now=T0 + timedelta(hours=4)
    )
    assert steps
    assert sum(s.precip_mm for s in steps) == pytest.approx(5.0)


def test_poll_style_full_rows_are_unchanged():
    """The poll path writes full rows, so the latest pre-watermark row carries
    every field and the merged boundary must equal it exactly — existing
    installs' aggregation does not move."""
    watermark = T0 + timedelta(hours=2)
    buf = [
        {
            const.RETRIEVED_AT: T0 + timedelta(hours=h),
            const.MAPPING_TEMPERATURE: 20.0 + h,
            const.MAPPING_PRECIPITATION: 25.0 + h,
        }
        for h in range(4)
    ]
    agg = aggregate_window(
        buf, watermark, PRECIP_DELTA_CONFIG, now=T0 + timedelta(hours=4)
    )
    # Boundary is the h=2 row (temp 22, rain 27); window is the h=3 row.
    assert agg[const.MAPPING_PRECIPITATION] == pytest.approx(1.0)
    assert agg[const.MAPPING_TEMPERATURE] == pytest.approx(22.5)
    assert agg[const.MAPPING_MAX_TEMP] == 23.0
    assert agg[const.MAPPING_MIN_TEMP] == 22.0
