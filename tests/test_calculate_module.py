"""Characterization tests for SmartIrrigationCoordinator.calculate_module.

These pin the CURRENT behavior of the core ET/bucket math so the Phase C
refactor (extracting calc/ out of the coordinator God class) can be done
safely — if a refactor changes a number here, the test fails and we look.

They call the REAL calculate_module (not a replica). The coordinator is built
with __new__ to skip its heavy __init__ (timers, dispatchers, weather clients);
only the attributes calculate_module actually touches are wired up:
  - self.hass.config.units / .language
  - self.hass.async_add_executor_job (runs loadModules to find the real module)
  - self.store.get_module (returns a Passthrough module config)

Passthrough is used because its math is deterministic: delta = -et_data, so
every downstream number (bucket, drainage, duration) is hand-computable.
"""

from unittest.mock import Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


def _make_coordinator():
    """Build a coordinator with only what calculate_module needs."""
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)

    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"

    async def run_executor(func, *args):
        return func(*args)

    hass.async_add_executor_job = run_executor
    coord.hass = hass

    store = Mock()
    store.get_module = Mock(
        return_value={const.MODULE_NAME: "Passthrough", "description": "", "config": {}}
    )
    coord.store = store
    return coord


def _zone(**overrides):
    """A metric zone with sane defaults; override per test."""
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Garden",
        const.ZONE_MODULE: 10,
        const.ZONE_BUCKET: 0.0,
        const.ZONE_MAXIMUM_BUCKET: 10.0,
        const.ZONE_DRAINAGE_RATE: 0.0,
        const.ZONE_THROUGHPUT: 10.0,  # L/min (metric)
        const.ZONE_SIZE: 10.0,  # m^2 (metric)
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_MAXIMUM_DURATION: 3600,
        const.ZONE_LEAD_TIME: 0,
    }
    zone.update(overrides)
    return zone


def _weather(et, multiplier=1.0):
    return {
        const.MAPPING_EVAPOTRANSPIRATION: et,
        const.MAPPING_DATA_MULTIPLIER: multiplier,
    }


async def test_deficit_produces_negative_bucket_and_duration():
    """ET deficit drives the bucket negative and yields an irrigation duration.

    Passthrough delta = -et = -5. bucket 0 + (-5) = -5 (no drainage when <0).
    precipitation_rate = throughput*60/size = 10*60/10 = 60 mm/h.
    duration = abs(-5)/60*3600 = 300 s; *multiplier(1) = 300; +lead_time(0) = 300.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(), _weather(5.0), None)

    assert data[const.ZONE_DELTA] == pytest.approx(-5.0)
    assert data[const.ZONE_BUCKET] == pytest.approx(-5.0)
    assert data[const.ZONE_CURRENT_DRAINAGE] == pytest.approx(0.0)
    assert data[const.ZONE_DURATION] == 300


async def test_surplus_is_capped_at_maximum_bucket():
    """Positive delta above max_bucket is clamped; no irrigation needed.

    Passthrough delta = -et = +5 (et=-5). bucket 8 + 5 = 13, capped to max 10.
    drainage_rate 0 -> no drainage. bucket >= 0 -> duration 0.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(bucket=8.0), _weather(-5.0), None)

    assert data[const.ZONE_DELTA] == pytest.approx(5.0)
    assert data[const.ZONE_BUCKET] == pytest.approx(10.0)
    assert data[const.ZONE_DURATION] == 0


async def test_drainage_reduces_positive_bucket():
    """Drainage applies above field capacity with the gamma=2 (4th power) term.

    delta = -et = 0 (et=0). bucket 5 + 0 = 5 (<= max 10, no cap).
    drainage = drainage_rate(1) * hour_multiplier(1) * 24 * (5/10)^4
             = 24 * 0.0625 = 1.5.
    newbucket = max(0, 5 - 1.5) = 3.5. bucket >= 0 -> duration 0.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(
        _zone(bucket=5.0, drainage_rate=1.0), _weather(0.0), None
    )

    assert data[const.ZONE_CURRENT_DRAINAGE] == pytest.approx(1.5)
    assert data[const.ZONE_BUCKET] == pytest.approx(3.5)
    assert data[const.ZONE_DURATION] == 0


async def test_hour_multiplier_scales_delta():
    """delta is scaled by the data_multiplier (fractional-day interval)."""
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(), _weather(4.0, multiplier=0.5), None)

    # delta = -4 * 0.5 = -2.0
    assert data[const.ZONE_DELTA] == pytest.approx(-2.0)
    assert data[const.ZONE_BUCKET] == pytest.approx(-2.0)


async def test_maximum_duration_caps_irrigation():
    """duration is clamped to maximum_duration when it would exceed it.

    delta = -100 -> bucket -100. precip_rate 60. duration = 100/60*3600 = 6000 s,
    above maximum_duration 1800 -> clamped to 1800.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(
        _zone(maximum_duration=1800), _weather(100.0), None
    )

    assert data[const.ZONE_DURATION] == 1800


async def test_lead_time_is_added_to_duration():
    """lead_time is added after multiplier/maximum-duration, then rounded.

    delta = -5 -> duration 300; +lead_time 60 = 360.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(lead_time=60), _weather(5.0), None)

    assert data[const.ZONE_DURATION] == 360


async def test_unknown_module_returns_none():
    """A zone whose module is missing from the store yields no result."""
    coord = _make_coordinator()
    coord.store.get_module = Mock(return_value=None)

    data = await coord.calculate_module(_zone(), _weather(5.0), None)
    assert data is None
