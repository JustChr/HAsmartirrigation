"""Irrigation credited part-way through a calculation window.

The replayed water balance reads the stored bucket as the level the window
OPENED at. Every credit path writes ``pre_bucket + depth`` clamped only at
``maximum_bucket`` -- the deficit is not an input -- so a run that delivers more
than the deficit called for (a manual run at a chosen duration, a multiplier
above 1, an externally observed run, a metered volume above the planned depth)
leaves a surplus behind. Drainage only bites on a surplus, so folding that
surplus into the window-start level charges it every hour of the window instead
of the hours it was really in the soil, and the zone reads drier than it is:
a bias toward watering again sooner.

These cover the ledger that fixes it end to end -- written by the credit paths,
carried through the store, consumed by the calculation.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.calculation import pending_bucket_events
from custom_components.smart_irrigation.store import SmartIrrigationStorage

T0 = datetime.datetime(2026, 5, 22, 0, 0, 0)
MAXIMUM_BUCKET = 25.4
DRAINAGE_RATE = 33.02


def _writer(bucket, *, metric=True, events=None, maximum_bucket=None):
    """A coordinator stub carrying only what the bucket writer touches."""
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.hass.config.units = METRIC_SYSTEM if metric else US_CUSTOMARY_SYSTEM
    zone = {const.ZONE_BUCKET: bucket}
    if events is not None:
        zone[const.ZONE_PENDING_BUCKET_EVENTS] = events
    if maximum_bucket is not None:
        zone[const.ZONE_MAXIMUM_BUCKET] = maximum_bucket
    c.store = Mock()
    c.store.get_zone = Mock(return_value=zone)
    c.store.async_update_zone = AsyncMock()
    return c


def _written(c):
    return c.store.async_update_zone.await_args.args[1]


class TestBookingACredit:
    async def test_the_water_that_entered_the_bucket_is_booked(self):
        c = _writer(-5.0)
        await c.async_write_watered_bucket(1, -1.0)
        changes = _written(c)
        assert changes[const.ZONE_BUCKET] == -1.0
        events = changes[const.ZONE_PENDING_BUCKET_EVENTS]
        assert [e["mm"] for e in events] == pytest.approx([4.0])

    async def test_a_credit_that_clamped_books_only_what_fitted(self):
        """Credits write absolutely and clamp at the ceiling.

        Booking the offered depth rather than the accepted one would leave
        ``bucket - credited`` below the real pre-run level, and the replay would
        start the window from a bucket the zone never had.
        """
        c = _writer(-5.0, maximum_bucket=10.0)
        await c.async_write_watered_bucket(1, 10.0)
        assert _written(c)[const.ZONE_PENDING_BUCKET_EVENTS][0]["mm"] == pytest.approx(
            15.0
        )

    async def test_a_reconcile_downwards_is_booked_as_a_negative(self):
        """Open credits optimistically, finish reconciles absolutely from B0.

        Each write books its own movement, so the two sum to the water actually
        delivered without either needing to know about the other.
        """
        c = _writer(3.0, events=[{"ts": T0.isoformat(), "mm": 8.0}])
        await c.async_write_watered_bucket(1, 1.5)
        events = _written(c)[const.ZONE_PENDING_BUCKET_EVENTS]
        assert [e["mm"] for e in events] == pytest.approx([8.0, -1.5])

    async def test_an_unchanged_bucket_books_nothing(self):
        """A run that never started still commits its bucket."""
        c = _writer(-5.0)
        await c.async_write_watered_bucket(1, -5.0)
        assert const.ZONE_PENDING_BUCKET_EVENTS not in _written(c)

    async def test_imperial_credits_are_booked_in_millimetres(self):
        """The bucket is in display units; the ledger is always mm.

        A list cannot be listed in unit_system.ZONE_DEPTH_FIELDS, so anything
        stored in display units here would be silently reinterpreted by a
        metric/imperial flip instead of converted with the bucket it describes.
        """
        c = _writer(-0.2, metric=False)
        await c.async_write_watered_bucket(1, 0.0)
        assert _written(c)[const.ZONE_PENDING_BUCKET_EVENTS][0]["mm"] == pytest.approx(
            5.08, abs=1e-6
        )

    async def test_extra_changes_ride_along_with_the_bucket(self):
        """One write, so a run cannot record its usage and lose its credit."""
        c = _writer(-5.0)
        await c.async_write_watered_bucket(1, -1.0, {const.ZONE_WATER_USED_TOTAL: 9.0})
        assert _written(c)[const.ZONE_WATER_USED_TOTAL] == 9.0

    async def test_the_ledger_is_bounded(self):
        """Only calculation drains it, so a long calculation outage must not
        grow the store without limit."""
        events = [
            {"ts": T0.isoformat(), "mm": 1.0}
            for _ in range(const.PENDING_BUCKET_EVENTS_MAX)
        ]
        c = _writer(0.0, events=events)
        await c.async_write_watered_bucket(1, 2.0)
        assert (
            len(_written(c)[const.ZONE_PENDING_BUCKET_EVENTS])
            == const.PENDING_BUCKET_EVENTS_MAX
        )


class TestReadingTheLedger:
    def test_aware_stamps_are_flattened_to_naive_local(self):
        """The window they are placed on is built from naive datetime.now(),
        and comparing the two raises rather than misplacing anything."""
        aware = "2026-05-22T10:00:00+00:00"
        ((stamp, mm),) = pending_bucket_events(
            {const.ZONE_PENDING_BUCKET_EVENTS: [{"ts": aware, "mm": 4.0}]}
        )
        assert stamp.tzinfo is None
        assert mm == 4.0

    def test_unusable_entries_are_dropped(self):
        assert (
            pending_bucket_events(
                {
                    const.ZONE_PENDING_BUCKET_EVENTS: [
                        {"ts": None, "mm": 4.0},
                        {"ts": T0.isoformat(), "mm": None},
                        {"ts": T0.isoformat(), "mm": 0.0},
                        "not a dict",
                    ]
                }
            )
            == []
        )

    def test_a_zone_that_never_watered_has_none(self):
        assert pending_bucket_events({}) == []


async def test_the_ledger_survives_a_store_round_trip(hass, hass_storage):
    """Persisted per zone, so a credit is not lost to a restart before the
    next calculation can place it."""
    hass.config.units = METRIC_SYSTEM
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    zone = await store.async_create_zone({const.ZONE_NAME: "Front"})
    events = [{"ts": T0.isoformat(), "mm": 6.5}]
    await store.async_update_zone(
        zone[const.ZONE_ID], {const.ZONE_PENDING_BUCKET_EVENTS: events}
    )
    await store.async_save()

    reloaded = SmartIrrigationStorage(hass)
    await reloaded.async_load()
    assert (
        reloaded.get_zone(zone[const.ZONE_ID])[const.ZONE_PENDING_BUCKET_EVENTS]
        == events
    )


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


async def _zone(c, store, bucket, *, et, events=None):
    """A dry solar day with a stubbed ET, so every number is hand-checkable."""
    readings = []
    for hour in range(24):
        readings.append(
            {
                const.RETRIEVED_AT: T0 + timedelta(hours=hour),
                const.MAPPING_PRECIPITATION: 0.0,
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
            const.ZONE_BUCKET: bucket,
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
    if events is not None:
        zone = dict(zone)
        zone[const.ZONE_PENDING_BUCKET_EVENTS] = events
    return zone


class TestThroughCalculateModule:
    """The halves are wired through different objects, so only a run of the
    real method proves the credit is removed from the start level and put back
    at its own step."""

    async def test_a_late_credit_keeps_more_bucket_than_one_at_the_window_start(
        self, coordinator
    ):
        c, store = coordinator
        now = T0 + timedelta(hours=24)
        credit = [{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}]

        booked = await _zone(c, store, 10.0, et=4.0, events=credit)
        weatherdata, _ = await c._aggregate_for_zone(booked, now=now)
        late = await c.calculate_module(booked, weatherdata, None, now=now)

        folded = await _zone(c, store, 10.0, et=4.0)
        weatherdata, _ = await c._aggregate_for_zone(folded, now=now)
        at_start = await c.calculate_module(folded, weatherdata, None, now=now)

        assert late[const.ZONE_BUCKET] > at_start[const.ZONE_BUCKET] + 1.0
        # The whole difference is drainage that never should have been charged.
        assert late[const.ZONE_CURRENT_DRAINAGE] < at_start[const.ZONE_CURRENT_DRAINAGE]

    async def test_the_balance_still_closes_over_the_stored_bucket(self, coordinator):
        """The credit is taken out of the start level and put back inside the
        window, so the published identity is unchanged."""
        c, store = coordinator
        now = T0 + timedelta(hours=24)
        zone = await _zone(
            c,
            store,
            8.0,
            et=3.0,
            events=[{"ts": (T0 + timedelta(hours=12)).isoformat(), "mm": 8.0}],
        )
        weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
        data = await c.calculate_module(zone, weatherdata, None, now=now)
        assert data[const.ZONE_BUCKET] == pytest.approx(
            8.0 + data[const.ZONE_DELTA] - data[const.ZONE_CURRENT_DRAINAGE], abs=1e-6
        )

    async def test_the_ledger_is_consumed(self, coordinator):
        c, store = coordinator
        now = T0 + timedelta(hours=24)
        zone = await _zone(
            c,
            store,
            8.0,
            et=3.0,
            events=[{"ts": (T0 + timedelta(hours=12)).isoformat(), "mm": 8.0}],
        )
        weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
        data = await c.calculate_module(zone, weatherdata, None, now=now)
        assert data[const.ZONE_PENDING_BUCKET_EVENTS] == []

    async def test_the_ledger_is_consumed_on_the_single_shot_path_too(
        self, coordinator
    ):
        """A zone with no sensor group cannot replay. Carrying its credits into
        a later window would place them further from where they belong, not
        closer."""
        c, store = coordinator
        module = await store.async_create_module(
            {const.MODULE_NAME: "PyETO", "description": "", "config": {}}
        )
        instance = Mock()
        instance.calculate = Mock(return_value=-5.0)
        c.getModuleInstanceByID = AsyncMock(return_value=instance)
        zone = await store.async_create_zone(
            {
                const.ZONE_NAME: "Orphan",
                const.ZONE_MODULE: module[const.MODULE_ID],
                const.ZONE_BUCKET: 0.0,
                const.ZONE_MAXIMUM_BUCKET: MAXIMUM_BUCKET,
                const.ZONE_DRAINAGE_RATE: 0.0,
                const.ZONE_THROUGHPUT: 10.0,
                const.ZONE_SIZE: 10.0,
                const.ZONE_MULTIPLIER: 1.0,
                const.ZONE_MAXIMUM_DURATION: 3600,
                const.ZONE_LEAD_TIME: 0,
            }
        )
        zone = dict(zone)
        zone[const.ZONE_PENDING_BUCKET_EVENTS] = [{"ts": T0.isoformat(), "mm": 4.0}]
        data = await c.calculate_module(
            zone, {const.MAPPING_DATA_MULTIPLIER: 1.0}, None
        )
        assert data[const.ZONE_PENDING_BUCKET_EVENTS] == []
        # ... and the bucket is untouched by them: the stored level already
        # holds the water, and the single-shot form has nowhere to put it.
        assert data[const.ZONE_BUCKET] == pytest.approx(-5.0)
