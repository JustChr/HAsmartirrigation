"""A bucket asserted by hand is a statement about NOW, not about the window start.

``ZONE_BUCKET`` is the level as of the present moment. The water balance
reconstructs the level the unconsumed weather window OPENED at by subtracting the
ledger: ``replay_water_balance(bucket - applied_total, ...)``. That is why every
writer which moves the bucket part-way through a window books a
``pending_bucket_events`` entry carrying its own timestamp -- see
``async_write_watered_bucket`` and test_mid_window_bucket_credit.py.

The manual paths book nothing. ``set_bucket`` / ``reset_bucket`` and the panel's
zone save both land on the generic branch of ``async_update_zone_config``, which
writes the field straight through ``store.async_update_zone``. With no ledger
entry the asserted level is taken for the window-OPENING level, and the whole
unconsumed window is applied on top of it -- including rain that fell before the
user made the statement.

That rain has already been accounted for by the person making the assertion: they
looked at wet ground and said "field capacity", or looked at dry ground and said
"-2". Applying it again contradicts them.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.store import SmartIrrigationStorage

T0 = datetime.datetime(2026, 5, 22, 0, 0, 0)
MAXIMUM_BUCKET = 25.4
DRAINAGE_RATE = 33.02

# When the user states the level, and how much rain fell BEFORE they did.
ASSERTED_AT_HOUR = 12
ASSERTED_LEVEL = -2.0
RAIN_MM = 8.0
RAIN_AT_HOUR = 4


@pytest.fixture
async def coordinator(hass):
    """A real coordinator over a real in-memory store, hourly form opted in."""
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    await store.async_update_config(
        {const.CONF_CONTINUOUS_UPDATES: True, const.CONF_HOURLY_CALCULATION: True}
    )
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    return c, store


async def _zone(c, store, *, rain_mm, et=1.0):
    """A solar day with a stubbed ET, optionally with rain at RAIN_AT_HOUR.

    Modelled on test_mid_window_bucket_credit.py so the two read alike. The
    watermark sits at T0, so the whole 24 h day is one unconsumed window.
    """
    readings = []
    for hour in range(24):
        readings.append(
            {
                const.RETRIEVED_AT: T0 + timedelta(hours=hour),
                const.MAPPING_PRECIPITATION: (rain_mm if hour == RAIN_AT_HOUR else 0.0),
                const.MAPPING_SOLRAD: 300.0 if 6 <= hour < 20 else 0.0,
            }
        )
    mapping = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "GW",
            const.MAPPING_MAPPINGS: {},
            const.MAPPING_DATA: readings,
        }
    )
    module = await store.async_create_module(
        {const.MODULE_NAME: "PyETO", "description": "", "config": {}}
    )
    instance = Mock()
    instance.calculate = Mock(return_value=-et)
    c.getModuleInstanceByID = AsyncMock(return_value=instance)
    zone = await store.async_create_zone(
        {
            const.ZONE_NAME: "Front",
            const.ZONE_MAPPING: mapping[const.MAPPING_ID],
            const.ZONE_MODULE: module[const.MODULE_ID],
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_BUCKET: 0.0,
            const.ZONE_MAXIMUM_BUCKET: MAXIMUM_BUCKET,
            const.ZONE_DRAINAGE_RATE: DRAINAGE_RATE,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_MAXIMUM_DURATION: 3600,
            const.ZONE_LEAD_TIME: 0,
            const.ZONE_LAST_CONSUMED: T0,
        }
    )
    return zone


async def _assert_level_by_hand(c, store, zone):
    """Set the bucket the way a user does: the service / panel path.

    Both ``set_bucket`` and the panel's zone save land on the generic branch of
    ``async_update_zone_config``; nothing between them and the store inspects the
    bucket. Driving that method is therefore the same write either of them makes.
    """
    # Frozen, because the write stamps the moment of the assertion from the
    # clock and the rest of this test lives in a constructed day.
    with freeze_time(T0 + timedelta(hours=ASSERTED_AT_HOUR)):
        await c.async_update_zone_config(
            zone_id=zone[const.ZONE_ID], data={const.ZONE_BUCKET: ASSERTED_LEVEL}
        )
    return store.get_zone(zone[const.ZONE_ID])


async def _bucket_after_a_full_day(c, store, *, rain_mm):
    zone = await _zone(c, store, rain_mm=rain_mm)
    zone = await _assert_level_by_hand(c, store, zone)
    now = T0 + timedelta(hours=24)
    weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
    data = await c.calculate_module(zone, weatherdata, None, now=now)
    return data[const.ZONE_BUCKET]


async def test_rain_from_before_the_assertion_does_not_move_the_bucket(coordinator):
    """The test that matters, stated as an equivalence rather than a number.

    Two identical days. In one, 8 mm fell at hour 4; in the other it never
    rained. In both the user states the level at hour 12, AFTER that rain would
    have fallen. Whatever the day's ET and drainage work out to, the two must
    land on the same bucket: rain the user had already seen cannot move a level
    they set afterwards.

    Comparing the two removes every number that is not the defect -- the ET
    stub, the solar shape, the drainage integral -- so a failure can only be the
    rain being applied twice.
    """
    c, store = coordinator
    with_rain = await _bucket_after_a_full_day(c, store, rain_mm=RAIN_MM)
    without_rain = await _bucket_after_a_full_day(c, store, rain_mm=0.0)
    assert with_rain == pytest.approx(without_rain, abs=1e-6), (
        f"{RAIN_MM} mm that fell {ASSERTED_AT_HOUR - RAIN_AT_HOUR} h BEFORE the "
        f"user set the bucket to {ASSERTED_LEVEL} was applied on top of it: "
        f"{with_rain:.2f} against {without_rain:.2f}"
    )


async def test_the_rain_is_what_moves_it(coordinator):
    """Guard the case above: it only says something while the rain is visible.

    If some unrelated change made the precipitation never reach the balance at
    all, the equivalence above would pass for the wrong reason. Here the level is
    NOT asserted, so the same rain must move the bucket by its full amount -- the
    ordinary behaviour, and the thing the assertion is supposed to shield.
    """
    c, store = coordinator
    now = T0 + timedelta(hours=24)

    wet = await _zone(c, store, rain_mm=RAIN_MM)
    weatherdata, _ = await c._aggregate_for_zone(wet, now=now)
    wet_data = await c.calculate_module(wet, weatherdata, None, now=now)

    dry = await _zone(c, store, rain_mm=0.0)
    weatherdata, _ = await c._aggregate_for_zone(dry, now=now)
    dry_data = await c.calculate_module(dry, weatherdata, None, now=now)

    assert wet_data[const.ZONE_BUCKET] > dry_data[const.ZONE_BUCKET] + 1.0


async def test_the_mid_window_ledger_is_dropped_with_it(coordinator):
    """The other half of the same statement, and the half the day-long test
    above cannot see because nothing credited that zone.

    A credit booked before the assertion is water the person was looking at when
    they stated the level. Left on the ledger it would be replayed inside the new
    window -- at a timestamp now BEFORE the window even opens -- and added to a
    number that already carries it.
    """
    c, store = coordinator
    zone = await _zone(c, store, rain_mm=0.0)
    await store.async_update_zone(
        zone[const.ZONE_ID],
        {
            const.ZONE_PENDING_BUCKET_EVENTS: [
                {"ts": (T0 + timedelta(hours=6)).isoformat(), "mm": 5.0}
            ]
        },
    )
    zone = await _assert_level_by_hand(c, store, zone)
    assert zone.get(const.ZONE_PENDING_BUCKET_EVENTS) == []


async def test_a_save_that_leaves_the_bucket_alone_moves_nothing(coordinator):
    """The panel POSTs the WHOLE zone on every settings save, bucket included.

    Editing a throughput must not restart the weather window: the level was not
    stated, it merely rode along unchanged. Without this the watermark would jump
    on any save and the day's ET would be silently discarded.
    """
    c, store = coordinator
    zone = await _zone(c, store, rain_mm=0.0)
    before = store.get_zone(zone[const.ZONE_ID]).get(const.ZONE_LAST_CONSUMED)
    with freeze_time(T0 + timedelta(hours=ASSERTED_AT_HOUR)):
        await c.async_update_zone_config(
            zone_id=zone[const.ZONE_ID],
            data={
                const.ZONE_BUCKET: zone.get(const.ZONE_BUCKET),
                const.ZONE_THROUGHPUT: 12.0,
            },
        )
    after = store.get_zone(zone[const.ZONE_ID])
    assert after.get(const.ZONE_LAST_CONSUMED) == before
    assert after.get(const.ZONE_THROUGHPUT) == 12.0
