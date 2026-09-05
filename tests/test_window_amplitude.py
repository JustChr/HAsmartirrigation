"""The sensor group remembers how wide its recent windows were.

A zone that estimates solar radiation from temperature needs the day's extremes
to price its window, and part-way through a window they are not observable. With
no forecast to fill the remaining hours the projection falls back to the site's
own solar geometry for the SHAPE and to this figure for the amplitude.

It cannot come from the reading buffer. That is pruned back to the oldest zone
watermark, so a daily-committing install holds roughly the current window and
nothing older -- there is no yesterday in it to measure.

Bounded by construction: one entry per window end date, seven at most, two
numbers each.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.calculation import (
    trailing_temperature_amplitude,
)
from custom_components.irrigation_plus.store import SmartIrrigationStorage

T0 = datetime.datetime(2026, 5, 22, 2, 0, 0)


@pytest.fixture
async def coordinator(hass):
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    return c, store


async def _mapping(store):
    return await store.async_create_mapping(
        {const.MAPPING_NAME: "GW", const.MAPPING_MAPPINGS: {}, const.MAPPING_DATA: []}
    )


def _weatherdata(low, high, multiplier=1.0):
    return {
        const.MAPPING_MIN_TEMP: low,
        const.MAPPING_MAX_TEMP: high,
        const.MAPPING_DATA_MULTIPLIER: multiplier,
    }


class TestRecordingAWindow:
    async def test_a_full_window_is_recorded_against_its_sensor_group(
        self, coordinator
    ):
        c, store = coordinator
        mapping = await _mapping(store)
        zone = {const.ZONE_MAPPING: mapping[const.MAPPING_ID]}

        await c._record_window_amplitude(zone, _weatherdata(11.0, 25.0), now=T0)

        stored = store.get_mapping(mapping[const.MAPPING_ID])
        assert stored[const.MAPPING_TEMPERATURE_AMPLITUDES] == [
            [T0.date().isoformat(), 14.0]
        ]

    async def test_a_part_day_window_is_not_a_day_s_amplitude(self, coordinator):
        """Recorded, it would drag the mean down exactly when the projection
        leans on it hardest."""
        c, store = coordinator
        mapping = await _mapping(store)
        zone = {const.ZONE_MAPPING: mapping[const.MAPPING_ID]}

        await c._record_window_amplitude(
            zone, _weatherdata(11.0, 25.0, multiplier=0.2), now=T0
        )

        stored = store.get_mapping(mapping[const.MAPPING_ID])
        assert stored[const.MAPPING_TEMPERATURE_AMPLITUDES] == []

    async def test_zones_sharing_a_group_do_not_each_add_an_entry(self, coordinator):
        """Seven zones on one sensor group commit seven windows the same
        evening. Appending each would fill the ring with one day's numbers and
        turn a week's mean into that day's."""
        c, store = coordinator
        mapping = await _mapping(store)

        for spread in (14.0, 13.8, 14.2):
            await c._record_window_amplitude(
                {const.ZONE_MAPPING: mapping[const.MAPPING_ID]},
                _weatherdata(11.0, 11.0 + spread),
                now=T0,
            )

        stored = store.get_mapping(mapping[const.MAPPING_ID])
        assert stored[const.MAPPING_TEMPERATURE_AMPLITUDES] == [
            [T0.date().isoformat(), 14.2]
        ]

    async def test_the_ring_keeps_the_most_recent_windows_only(self, coordinator):
        c, store = coordinator
        mapping = await _mapping(store)

        for day in range(12):
            await c._record_window_amplitude(
                {const.ZONE_MAPPING: mapping[const.MAPPING_ID]},
                _weatherdata(10.0, 10.0 + day),
                now=T0 + timedelta(days=day),
            )

        stored = store.get_mapping(mapping[const.MAPPING_ID])
        entries = stored[const.MAPPING_TEMPERATURE_AMPLITUDES]
        assert len(entries) == const.TEMPERATURE_AMPLITUDE_WINDOWS
        assert [amplitude for _date, amplitude in entries] == [5.0, 6, 7, 8, 9, 10, 11]


class TestReadingItBack:
    async def test_the_mean_of_the_recorded_windows_is_what_the_estimate_gets(
        self, coordinator
    ):
        c, store = coordinator
        mapping = await _mapping(store)
        for day, spread in enumerate((10.0, 12.0, 14.0)):
            await c._record_window_amplitude(
                {const.ZONE_MAPPING: mapping[const.MAPPING_ID]},
                _weatherdata(10.0, 10.0 + spread),
                now=T0 + timedelta(days=day),
            )

        assert trailing_temperature_amplitude(
            store, mapping[const.MAPPING_ID]
        ) == pytest.approx(12.0)

    async def test_a_group_that_has_never_committed_offers_nothing(self, coordinator):
        """A fresh install declines to the observed extremes and says so through
        its tier, rather than projecting from a number it does not have."""
        _c, store = coordinator
        mapping = await _mapping(store)

        assert trailing_temperature_amplitude(store, mapping[const.MAPPING_ID]) is None
        assert trailing_temperature_amplitude(store, None) is None
        assert trailing_temperature_amplitude(store, 999) is None

    async def test_a_malformed_entry_is_skipped_rather_than_raising(self, coordinator):
        """The estimate swallows every exception, so a bad row here would show
        as an estimate that is simply unavailable and nothing else."""
        _c, store = coordinator
        mapping = await _mapping(store)
        await store.async_update_mapping(
            mapping[const.MAPPING_ID],
            {
                const.MAPPING_TEMPERATURE_AMPLITUDES: [
                    ["2026-05-20", "nonsense"],
                    "not-a-pair",
                    ["2026-05-21", 12.0],
                ]
            },
        )

        assert trailing_temperature_amplitude(
            store, mapping[const.MAPPING_ID]
        ) == pytest.approx(12.0)


class TestItSurvivesAReload:
    async def test_a_document_written_before_the_field_existed_still_loads(self, hass):
        """Hydrated with a default rather than strict indexing, so an install
        upgrading into this does not fail to load its sensor groups."""
        store = SmartIrrigationStorage(hass)
        await store.async_load()
        mapping = await _mapping(store)
        stored = dict(store.get_mapping(mapping[const.MAPPING_ID]))
        stored.pop(const.MAPPING_TEMPERATURE_AMPLITUDES, None)

        reloaded = SmartIrrigationStorage(hass)
        reloaded._store = Mock()
        reloaded._store.async_load = AsyncMock(
            return_value={
                "config": {},
                "zones": [],
                "modules": [],
                "mappings": [stored],
            }
        )
        reloaded._store.async_delay_save = Mock()
        await reloaded.async_load()

        assert (
            reloaded.get_mapping(mapping[const.MAPPING_ID])[
                const.MAPPING_TEMPERATURE_AMPLITUDES
            ]
            == []
        )
