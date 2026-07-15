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


async def test_zero_size_zone_does_not_crash_and_yields_zero_duration():
    """Audit #8: a misconfigured zone (size 0) with a deficit must NOT raise
    ZeroDivisionError. Pre-fix the (throughput*60)/size division blew up and — with
    no per-zone guard in the calc-all loop — aborted calculation for every later
    zone. Now the precipitation rate/duration degrade to 0."""
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(size=0.0), _weather(5.0), None)

    assert data[const.ZONE_DELTA] == pytest.approx(-5.0)
    assert data[const.ZONE_BUCKET] == pytest.approx(-5.0)
    assert data[const.ZONE_DURATION] == 0


async def test_none_maximum_bucket_does_not_crash():
    """Audit #8: a zone whose maximum_bucket was cleared (None) must not raise a
    TypeError from float(None) while building the explanation string."""
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(maximum_bucket=None), _weather(5.0), None)

    assert data[const.ZONE_BUCKET] == pytest.approx(-5.0)
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
    """Drainage applies above field capacity, integrated over the window.

    delta = -et = 0 (et=0). bucket 5 + 0 = 5 (<= max 10, no cap).
    Brooks-Corey closed form (n=4) over elapsed_hours = mult(1)*24 = 24h:
      denom = 1 + 3*rate(1)*24*W0(5)^3/max(10)^4 = 1 + 9000/10000 = 1.9
      W_end = 5 / 1.9^(1/3) = 4.0369
      drainage = 5 - 4.0369 = 0.9631
    bucket >= 0 -> duration 0.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(
        _zone(bucket=5.0, drainage_rate=1.0), _weather(0.0), None
    )

    assert data[const.ZONE_CURRENT_DRAINAGE] == pytest.approx(0.96306, abs=1e-4)
    assert data[const.ZONE_BUCKET] == pytest.approx(4.03694, abs=1e-4)
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


# --- WS-4: crop coefficient (Kc) scaling of the ET term ----------------------


async def test_kc_default_one_is_behaviour_identical():
    """An absent / 1.0 Kc reproduces the reference-ET delta exactly.

    Passthrough delta = -et = -5; Kc 1.0 leaves it unchanged.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(kc=1.0), _weather(5.0), None)
    assert data[const.ZONE_DELTA] == pytest.approx(-5.0)
    assert data[const.ZONE_BUCKET] == pytest.approx(-5.0)


async def test_kc_scales_only_the_et_term():
    """Kc multiplies the ET term before the interval scaling.

    delta = (-5 * Kc 0.5) * multiplier 1 = -2.5. Duration follows the smaller
    deficit: 2.5/60*3600 = 150 s.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(kc=0.5), _weather(5.0), None)
    assert data[const.ZONE_DELTA] == pytest.approx(-2.5)
    assert data[const.ZONE_BUCKET] == pytest.approx(-2.5)
    assert data[const.ZONE_DURATION] == 150


async def test_kc_above_one_increases_deficit():
    """A thirsty-crop Kc > 1 deepens the deficit proportionally.

    delta = -4 * 1.25 = -5.0.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(kc=1.25), _weather(4.0), None)
    assert data[const.ZONE_DELTA] == pytest.approx(-5.0)


async def test_kc_does_not_scale_precipitation():
    """Kc scales ET only; precipitation passes through untouched.

    Static modules add precip separately; here Passthrough has no precip, so we
    assert the math is purely on the ET term: a None Kc falls back to 1.0.
    """
    coord = _make_coordinator()
    data = await coord.calculate_module(_zone(kc=None), _weather(5.0), None)
    assert data[const.ZONE_DELTA] == pytest.approx(-5.0)
