"""A zone's calculation explanation has to survive a restart.

The calculation writes it onto the zone and the zone settings view reads it
back from the store, but ``async_load`` rebuilds each ``ZoneEntry`` field by
field and ``explanation`` was not in that list. So every restart rebuilt the
zones without it and the next save wrote the emptied value over the file: the
one place the water balance shows its work was blank from the restart until the
next calculation.

Loaded through Home Assistant's real Store, as the neighbouring migration tests
do, since the load is where a field left out actually disappears.
"""

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.store import (
    STORAGE_KEY,
    STORAGE_VERSION,
    SmartIrrigationStorage,
)

EXPLANATION = "Module returned Evapotranspiration deficiency of -2.40 mm."


def _zone(**extra):
    zone = {
        const.ZONE_ID: 0,
        const.ZONE_NAME: "Lawn",
        const.ZONE_SIZE: 25.0,
        const.ZONE_THROUGHPUT: 12.0,
        const.ZONE_STATE: "automatic",
        const.ZONE_DELTA: -1.25,
        const.ZONE_BUCKET: -2.4,
        const.ZONE_DURATION: 600,
        const.ZONE_MODULE: 0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_MAPPING: 0,
        const.ZONE_LEAD_TIME: 0,
    }
    zone.update(extra)
    return zone


async def _load(hass, hass_storage, zone):
    hass_storage[STORAGE_KEY] = {
        "version": STORAGE_VERSION,
        "minor_version": 1,
        "key": STORAGE_KEY,
        "data": {"config": {}, "zones": [zone], "modules": [], "mappings": []},
    }
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    return store.zones[0]


@pytest.mark.asyncio
async def test_the_explanation_survives_a_restart(hass, hass_storage):
    zone = await _load(
        hass, hass_storage, _zone(**{const.ZONE_EXPLANATION: EXPLANATION})
    )

    assert zone.explanation == EXPLANATION


@pytest.mark.asyncio
async def test_a_zone_that_was_never_calculated_still_loads(hass, hass_storage):
    zone = await _load(hass, hass_storage, _zone())

    assert zone.explanation is None
    assert zone.name == "Lawn"
