"""Tests for the experimental live run-time duration feature (WS-3).

When ``live_duration_enabled`` is on, the scheduled runner recomputes each
timed zone's duration from the live intra-day deficit (instead of the frozen
daily ``ZONE_DURATION``) and credits the actually-delivered water back to the
bucket after the run — so the leftover deficit persists and the next daily calc
does not double-subtract the intra-day ET.

Coordinators are built with ``__new__`` (like test_experimental_features) so only
the attributes each method touches are wired up.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.calculation import duration_from_deficit


# --------------------------------------------------------------------------- #
# duration_from_deficit — the pure helper the runner reuses
# --------------------------------------------------------------------------- #
def test_duration_from_deficit_metric():
    """10 mm deficit at 60 mm/h precip rate == 600 s (matches calculate_module)."""
    # size 10 m², throughput 10 L/min -> precip rate = 10*60/10 = 60 mm/h
    assert duration_from_deficit(-10.0, 10.0, 10.0, 1.0, 36000, 0, metric=True) == 600


def test_duration_from_deficit_non_negative_is_zero():
    assert duration_from_deficit(0.0, 10.0, 10.0, 1.0, 36000, 0, metric=True) == 0
    assert duration_from_deficit(3.0, 10.0, 10.0, 1.0, 36000, 0, metric=True) == 0
    assert duration_from_deficit(None, 10.0, 10.0, 1.0, 36000, 0, metric=True) == 0


def test_duration_from_deficit_applies_multiplier_and_lead_time():
    # 600 s base * 1.5 multiplier = 900 s, + 30 s lead = 930 s
    assert duration_from_deficit(-10.0, 10.0, 10.0, 1.5, 36000, 30, metric=True) == 930


def test_duration_from_deficit_clamps_to_maximum():
    # base 600 s but max 120 s -> clamped; lead time still added after the clamp
    assert duration_from_deficit(-10.0, 10.0, 10.0, 1.0, 120, 5, metric=True) == 125


def test_duration_from_deficit_unit_invariant():
    """Seconds are unit-invariant: the imperial equivalent gives the same run."""
    metric = duration_from_deficit(-10.0, 10.0, 10.0, 1.0, 36000, 0, metric=True)
    # 10 mm = 0.393701 in; 10 L/min = 2.641722 gpm; 10 m² = 107.639 ft²
    imperial = duration_from_deficit(
        -0.393701, 2.641722, 107.639104, 1.0, 36000, 0, metric=False
    )
    assert imperial == pytest.approx(metric, abs=1)


async def test_duration_from_deficit_matches_calculate_module():
    """No-drift guard: the helper equals calculate_module's duration."""
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
    store.config = SimpleNamespace(forecast_weighting_enabled=False)
    coord.store = store
    coord.use_weather_service = False
    coord._WeatherServiceClient = None

    zone = {
        const.ZONE_ID: 1,
        const.ZONE_MODULE: 10,
        const.ZONE_BUCKET: 0.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_DRAINAGE_RATE: 0.0,
        const.ZONE_THROUGHPUT: 7.0,
        const.ZONE_SIZE: 13.0,
        const.ZONE_MULTIPLIER: 1.3,
        const.ZONE_MAXIMUM_DURATION: 36000,
        const.ZONE_LEAD_TIME: 12,
    }
    data = await coord.calculate_module(
        zone,
        {const.MAPPING_EVAPOTRANSPIRATION: 9.0, const.MAPPING_DATA_MULTIPLIER: 1.0},
        [],
    )
    # The daily calc subtracted 9 mm ET from a 0 bucket -> deficit -9 mm.
    helper = duration_from_deficit(
        data[const.ZONE_BUCKET], 7.0, 13.0, 1.3, 36000, 12, metric=True
    )
    assert helper == data[const.ZONE_DURATION]


# --------------------------------------------------------------------------- #
# _apply_live_durations
# --------------------------------------------------------------------------- #
def _live_coordinator(*, enabled=True, estimates=None, metric=True):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM if metric else US_CUSTOMARY_SYSTEM
    coord.hass = hass
    coord.store = Mock()
    coord.store.config = SimpleNamespace(live_duration_enabled=enabled)
    coord.async_refresh_zone_estimates = AsyncMock(return_value=estimates or {})
    return coord


def _timed_zone(**overrides):
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_SIZE: 10.0,  # precip rate 60 mm/h
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_MAXIMUM_DURATION: 36000,
        const.ZONE_LEAD_TIME: 0,
        const.ZONE_DURATION: 300,  # frozen daily duration
        const.ZONE_BUCKET: -5.0,
    }
    zone.update(overrides)
    return zone


async def test_apply_live_durations_off_is_passthrough():
    coord = _live_coordinator(enabled=False)
    zones = [_timed_zone()]
    out = await coord._apply_live_durations(zones)
    assert out is zones
    assert coord._live_run_zones == set()
    coord.async_refresh_zone_estimates.assert_not_awaited()


async def test_apply_live_durations_overrides_from_live_deficit():
    """Live deficit -8 mm -> 480 s, overriding the frozen 300 s; zone marked."""
    coord = _live_coordinator(estimates={"1": {"live_deficit": -8.0}})
    out = await coord._apply_live_durations([_timed_zone()])
    assert len(out) == 1
    assert out[0][const.ZONE_DURATION] == 480  # 8 mm / 60 mm/h * 3600
    assert coord._live_run_zones == {1}


async def test_apply_live_durations_drops_zone_no_longer_needing_water():
    """Intra-day rain filled it (live deficit >= 0) -> dropped from the run."""
    coord = _live_coordinator(estimates={"1": {"live_deficit": 2.0}})
    out = await coord._apply_live_durations([_timed_zone()])
    assert out == []
    assert coord._live_run_zones == set()


async def test_apply_live_durations_keeps_daily_when_no_estimate():
    """No live estimate for the zone -> keep the daily duration, not marked."""
    coord = _live_coordinator(estimates={})
    zone = _timed_zone()
    out = await coord._apply_live_durations([zone])
    assert out[0][const.ZONE_DURATION] == 300
    assert coord._live_run_zones == set()


async def test_apply_live_durations_leaves_flow_zones_untouched():
    """Flow-meter zones already credit measured volume — not recomputed."""
    coord = _live_coordinator(estimates={"1": {"live_deficit": -8.0}})
    zone = _timed_zone(**{const.ZONE_FLOW_SENSOR: "sensor.flow"})
    out = await coord._apply_live_durations([zone])
    assert out[0] is zone  # untouched
    assert coord._live_run_zones == set()


# --------------------------------------------------------------------------- #
# Crediting reset (the double-count guard)
# --------------------------------------------------------------------------- #
def _reset_coordinator(monkeypatch, *, metric=True):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM if metric else US_CUSTOMARY_SYSTEM
    coord.hass = hass
    coord.store = Mock()
    coord.store.async_update_zone = AsyncMock()
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send",
        Mock(),
    )
    return coord


def _last_bucket(coord):
    """The most recent bucket level written by the run (final commit)."""
    for call in reversed(coord.store.async_update_zone.await_args_list):
        changes = call.args[1]
        if const.ZONE_BUCKET in changes:
            return changes[const.ZONE_BUCKET]
    raise AssertionError("no bucket write recorded")


async def _drive_timed(coord, zone, monkeypatch):
    """Run a synthetic (throughput) metered run to completion, fast."""
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord.hass.services = Mock()
    coord.hass.services.async_call = AsyncMock()
    coord.hass.states = Mock()
    coord._confirm_valve_running = AsyncMock(return_value=True)
    await coord._run_valve_metered(zone, "switch.v", real_flow=False)


async def test_live_run_credits_delivered_not_zeroed(monkeypatch):
    """A live run credits the water actually delivered, not force-to-target."""
    coord = _reset_coordinator(monkeypatch)
    coord._live_run_zones = {1}
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_DURATION: 480,  # 480 s @ 10 L/min = 80 L = 8 mm
    }
    coord.store.get_zone = Mock(return_value=dict(zone))
    await _drive_timed(coord, dict(zone), monkeypatch)

    assert _last_bucket(coord) == pytest.approx(3.0)  # -5 + 8, NOT 0
    # The marker is consumed so a later non-live run resets normally.
    assert 1 not in coord._live_run_zones


async def test_live_run_credit_capped_at_maximum_bucket(monkeypatch):
    coord = _reset_coordinator(monkeypatch)
    coord._live_run_zones = {1}
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_BUCKET: 0.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MAXIMUM_BUCKET: 5.0,
        const.ZONE_DURATION: 480,  # +8 -> capped at 5
    }
    coord.store.get_zone = Mock(return_value=dict(zone))
    await _drive_timed(coord, dict(zone), monkeypatch)
    assert _last_bucket(coord) == pytest.approx(5.0)


async def test_non_live_run_still_resets_to_target(monkeypatch):
    """A normal (non-live) run is unaffected: bucket goes to its target."""
    coord = _reset_coordinator(monkeypatch)
    coord._live_run_zones = set()
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_IRRIGATION_TARGET_BUCKET: -4.0,
        const.ZONE_BUCKET: -9.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_DURATION: 480,  # delivers 8 mm, but clamped at the -4 target
    }
    coord.store.get_zone = Mock(return_value=dict(zone))
    await _drive_timed(coord, dict(zone), monkeypatch)
    assert _last_bucket(coord) == pytest.approx(-4.0)


async def test_live_credit_then_daily_calc_no_double_subtraction(monkeypatch):
    """End-to-end: credit reset + next daily calc does NOT double-subtract ET.

    Monday's daily calc left bucket -5 mm. Overnight 3 mm ET accrued, so at
    Tuesday's run the live deficit is -8 mm and the live run delivers 8 mm. The
    credit reset leaves the bucket at +3 (the 3 mm of overnight water we applied
    beyond the daily deficit). When Tuesday's daily calc subtracts the day's
    full 8 mm ET, the +3 surplus cancels the overnight portion already watered,
    so the outstanding deficit is the true -5 carryover — not -8 (which is what
    force-to-zero would wrongly leave, double-counting the 3 mm).
    """
    # --- the credit reset ---
    coord = _reset_coordinator(monkeypatch)
    coord._live_run_zones = {1}
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_DURATION: 480,
    }
    coord.store.get_zone = Mock(return_value=dict(zone))
    await _drive_timed(coord, dict(zone), monkeypatch)
    credited_bucket = _last_bucket(coord)
    assert credited_bucket == pytest.approx(3.0)

    # --- the next daily calc over Tuesday's full 8 mm ET ---
    calc = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"

    async def run_executor(func, *args):
        return func(*args)

    hass.async_add_executor_job = run_executor
    calc.hass = hass
    store = Mock()
    store.get_module = Mock(
        return_value={const.MODULE_NAME: "Passthrough", "description": "", "config": {}}
    )
    store.config = SimpleNamespace(forecast_weighting_enabled=False)
    calc.store = store
    calc.use_weather_service = False
    calc._WeatherServiceClient = None

    def _zone(bucket):
        return {
            const.ZONE_ID: 1,
            const.ZONE_MODULE: 10,
            const.ZONE_BUCKET: bucket,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
            const.ZONE_DRAINAGE_RATE: 0.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_MAXIMUM_DURATION: 36000,
            const.ZONE_LEAD_TIME: 0,
        }

    weather = {
        const.MAPPING_EVAPOTRANSPIRATION: 8.0,
        const.MAPPING_DATA_MULTIPLIER: 1.0,
    }
    credited = await calc.calculate_module(_zone(credited_bucket), weather, [])
    zeroed = await calc.calculate_module(_zone(0.0), weather, [])

    # Credit model retains the true outstanding deficit; force-to-zero is 3 mm
    # too deep (it forgot the overnight water already delivered).
    assert credited[const.ZONE_BUCKET] == pytest.approx(-5.0)
    assert zeroed[const.ZONE_BUCKET] == pytest.approx(-8.0)
    assert credited[const.ZONE_BUCKET] - zeroed[const.ZONE_BUCKET] == pytest.approx(3.0)
