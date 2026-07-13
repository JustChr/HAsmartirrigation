"""Tests for the experimental Setup features.

Covers the two opt-in features wired to the Experimental tab:
  * Forecast-weighted durations (calculation.calculate_module) — water less when
    rain is forecast, leaving the leftover deficit in ``irrigation_target_bucket``.
  * The runner crediting a completed run to that per-zone target instead of 0.
  * Observed-watering bucket crediting (ObservedWateringMixin) — credit external
    valve runs, suppress Smart Irrigation's own runs.

Like test_calculate_module, coordinators are built with ``__new__`` so only the
attributes each method actually touches are wired up.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util
import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


# --------------------------------------------------------------------------- #
# Forecast weighting (calculate_module)
# --------------------------------------------------------------------------- #
def _calc_coordinator(*, forecast_weighting=False, use_weather_service=False, days=1):
    """Coordinator wired for calculate_module with the experimental knobs."""
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
    store.config = SimpleNamespace(forecast_weighting_enabled=forecast_weighting)
    store.async_get_config = AsyncMock(
        return_value={const.CONF_PRECIPITATION_FORECAST_DAYS: days}
    )
    coord.store = store
    coord.use_weather_service = use_weather_service
    coord._WeatherServiceClient = None
    return coord


def _zone(**overrides):
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Garden",
        const.ZONE_MODULE: 10,
        const.ZONE_BUCKET: 0.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_DRAINAGE_RATE: 0.0,
        const.ZONE_THROUGHPUT: 10.0,  # L/min
        const.ZONE_SIZE: 10.0,  # m^2  -> precip rate 60 mm/h
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_MAXIMUM_DURATION: 36000,
        const.ZONE_LEAD_TIME: 0,
    }
    zone.update(overrides)
    return zone


def _weather(et, multiplier=1.0):
    return {
        const.MAPPING_EVAPOTRANSPIRATION: et,
        const.MAPPING_DATA_MULTIPLIER: multiplier,
    }


async def test_no_weighting_leaves_target_zero_and_full_duration():
    """Feature off: full deficit watered, target 0 (current behaviour)."""
    coord = _calc_coordinator(forecast_weighting=False, use_weather_service=True)
    data = await coord.calculate_module(
        _zone(), _weather(10.0), [{"precipitation": 4.0}]
    )

    assert data[const.ZONE_BUCKET] == pytest.approx(-10.0)
    assert data[const.ZONE_DURATION] == 600  # 10 mm / 60 mm/h * 3600
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)


async def test_forecast_weighting_reduces_duration_and_sets_target():
    """4 mm forecast trims a 10 mm deficit run to 6 mm; 4 mm left for the rain."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True)
    data = await coord.calculate_module(
        _zone(), _weather(10.0), [{const.MAPPING_PRECIPITATION: 4.0}]
    )

    # True deficit is unchanged in the bucket...
    assert data[const.ZONE_BUCKET] == pytest.approx(-10.0)
    # ...but the run only delivers the rain-adjusted 6 mm.
    assert data[const.ZONE_DURATION] == 360  # 6 mm / 60 mm/h * 3600
    # ...and the runner is told to stop at the 4 mm the forecast rain will fill.
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(-4.0)


async def test_forecast_covering_deficit_skips_run():
    """Forecast ≥ deficit: no run, bucket keeps the true deficit, target 0."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True)
    data = await coord.calculate_module(
        _zone(), _weather(10.0), [{const.MAPPING_PRECIPITATION: 12.0}]
    )

    assert data[const.ZONE_BUCKET] == pytest.approx(-10.0)
    assert data[const.ZONE_DURATION] == 0
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)


async def test_forecast_weighting_sums_lookahead_days():
    """Precip is summed over the configured look-ahead window."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=2)
    data = await coord.calculate_module(
        _zone(),
        _weather(10.0),
        [
            {const.MAPPING_PRECIPITATION: 2.0},
            {const.MAPPING_PRECIPITATION: 3.0},
            {const.MAPPING_PRECIPITATION: 9.0},  # beyond the 2-day window, ignored
        ],
    )
    # 5 mm over 2 days -> effective deficit 5 mm.
    assert data[const.ZONE_DURATION] == 300
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(-5.0)


# --------------------------------------------------------------------------- #
# Runner crediting to the per-zone target
# --------------------------------------------------------------------------- #
def _runner_coordinator(monkeypatch):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    coord.hass = hass
    coord.store = Mock()
    coord.store.async_update_zone = AsyncMock()
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send",
        Mock(),
    )
    return coord


def test_zone_target_bucket_helper():
    assert SmartIrrigationCoordinator._zone_target_bucket({}) == 0.0
    assert (
        SmartIrrigationCoordinator._zone_target_bucket(
            {const.ZONE_IRRIGATION_TARGET_BUCKET: None}
        )
        == 0.0
    )
    assert (
        SmartIrrigationCoordinator._zone_target_bucket(
            {const.ZONE_IRRIGATION_TARGET_BUCKET: -4.0}
        )
        == -4.0
    )


def test_run_ceiling_uses_target(monkeypatch):
    """A completed timed run may credit only up to the zone's target floor."""
    coord = _runner_coordinator(monkeypatch)
    coord._live_run_zones = set()
    ceiling = coord._run_ceiling(
        {const.ZONE_ID: 1, const.ZONE_IRRIGATION_TARGET_BUCKET: -4.0}
    )
    assert ceiling == pytest.approx(-4.0)


def test_run_ceiling_defaults_to_zero(monkeypatch):
    """No target (feature off) preserves the original full-replenish to 0."""
    coord = _runner_coordinator(monkeypatch)
    coord._live_run_zones = set()
    assert coord._run_ceiling({const.ZONE_ID: 1}) == pytest.approx(0.0)


def test_run_ceiling_live_zone_allows_surplus(monkeypatch):
    """A live-estimate run may credit up to maximum_bucket (a surplus)."""
    coord = _runner_coordinator(monkeypatch)
    coord._live_run_zones = {1}
    ceiling = coord._run_ceiling({const.ZONE_ID: 1, const.ZONE_MAXIMUM_BUCKET: 5.0})
    assert ceiling == pytest.approx(5.0)
    # marker consumed
    assert 1 not in coord._live_run_zones


# --------------------------------------------------------------------------- #
# Observed watering
# --------------------------------------------------------------------------- #
def _observer_coordinator(monkeypatch, *, loop_time=1000.0):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.loop = Mock()
    hass.loop.time = Mock(return_value=loop_time)
    # Close the coroutine instead of running it, so we can assert it was
    # scheduled without leaking a "never awaited" warning.
    hass.async_create_task = Mock(side_effect=lambda coro: coro.close())
    coord.hass = hass
    coord.store = Mock()
    coord.store.async_update_zone = AsyncMock()
    coord._si_driven_until = {}
    coord._observed_on_since = {}
    coord._observed_zone_by_entity = {"switch.valve": 1}
    monkeypatch.setattr(
        "custom_components.smart_irrigation.observed_watering.async_dispatcher_send",
        Mock(),
    )
    # _credit_observed_watering now also calls _record_run (irrigation.py), which
    # dispatches from that module — stub it too so the Mock hass isn't iterated.
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send",
        Mock(),
    )
    return coord


def _event(entity_id, new, old):
    def _state(s):
        return None if s is None else SimpleNamespace(state=s)

    return SimpleNamespace(
        data={
            "entity_id": entity_id,
            "new_state": _state(new),
            "old_state": _state(old),
        }
    )


async def test_observed_credit_estimates_from_runtime(monkeypatch):
    """1 min at 10 L/min over 10 m² == 1 mm credited to the bucket."""
    coord = _observer_coordinator(monkeypatch)
    coord.store.get_zone = Mock(
        return_value={
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )

    await coord._credit_observed_watering(1, 60)

    _, changes = coord.store.async_update_zone.await_args.args
    assert changes[const.ZONE_BUCKET] == pytest.approx(-4.0)


async def test_observed_credit_capped_at_maximum_bucket(monkeypatch):
    coord = _observer_coordinator(monkeypatch)
    coord.store.get_zone = Mock(
        return_value={
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_BUCKET: 9.5,
            const.ZONE_MAXIMUM_BUCKET: 10.0,
        }
    )

    await coord._credit_observed_watering(1, 60)  # +1 mm -> 10.5, capped to 10

    _, changes = coord.store.async_update_zone.await_args.args
    assert changes[const.ZONE_BUCKET] == pytest.approx(10.0)


async def test_observed_credit_needs_size_and_throughput(monkeypatch):
    coord = _observer_coordinator(monkeypatch)
    coord.store.get_zone = Mock(
        return_value={const.ZONE_SIZE: 0.0, const.ZONE_THROUGHPUT: 10.0}
    )

    await coord._credit_observed_watering(1, 60)

    coord.store.async_update_zone.assert_not_awaited()


def test_observed_external_run_is_tracked(monkeypatch):
    """A valve opening that SI did not drive starts a tracked run."""
    coord = _observer_coordinator(monkeypatch)
    coord._observed_state_changed(_event("switch.valve", "on", "off"))
    assert 1 in coord._observed_on_since


def test_observed_si_driven_run_is_suppressed(monkeypatch):
    """A valve SI just opened is ignored (suppress window in the future)."""
    coord = _observer_coordinator(monkeypatch, loop_time=1000.0)
    coord._si_driven_until = {1: 1030.0}  # still suppressed at t=1000
    coord._observed_state_changed(_event("switch.valve", "on", "off"))
    assert 1 not in coord._observed_on_since


def test_observed_long_run_flap_stays_suppressed(monkeypatch):
    """A mid-run valve flap (re-open long after the fixed 30s grace) is still
    suppressed, because the window spans the whole run length, not just 30s."""
    coord = _observer_coordinator(monkeypatch, loop_time=1000.0)
    # 1h56 run: window = now + 6960 + 30s grace = 7990.
    coord._note_si_valve(1, 6960)
    assert coord._si_driven_until[1] == pytest.approx(7990.0)

    # ~10 min in, the valve flaps unavailable → on again (would have re-opened
    # past the old 30s window). Must NOT be tracked as external watering.
    coord.hass.loop.time = Mock(return_value=1600.0)
    coord._observed_state_changed(_event("switch.valve", "on", "unavailable"))
    assert 1 not in coord._observed_on_since

    # Once the run window + grace has elapsed, a genuine external open is tracked.
    coord.hass.loop.time = Mock(return_value=8000.0)
    coord._observed_state_changed(_event("switch.valve", "on", "off"))
    assert 1 in coord._observed_on_since


def test_observed_close_schedules_credit(monkeypatch):
    """Closing a tracked valve schedules a bucket credit."""
    coord = _observer_coordinator(monkeypatch)
    coord._observed_on_since = {1: dt_util.utcnow()}
    coord._observed_state_changed(_event("switch.valve", "off", "on"))
    assert coord.hass.async_create_task.called
    assert 1 not in coord._observed_on_since


async def test_observed_credit_writes_run_log_and_total(monkeypatch):
    """An observed credit also appends a persistent `observed` run-log entry
    and adds the estimated volume to the usage total."""
    coord = _observer_coordinator(monkeypatch)
    coord.store.get_zone = Mock(
        return_value={
            const.ZONE_ID: 1,
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )

    await coord._credit_observed_watering(1, 60)  # 1 min @ 10 L/min = 10 L

    log_calls = [
        c
        for c in coord.store.async_update_zone.await_args_list
        if const.ZONE_RUN_LOG in c.args[1]
    ]
    assert log_calls, "observed credit should append a run-log entry"
    changes = log_calls[-1].args[1]
    entry = changes[const.ZONE_RUN_LOG][0]
    assert entry["result"] == const.RUN_RESULT_OBSERVED
    assert entry["volume_l"] == pytest.approx(10.0)
    assert changes[const.ZONE_WATER_USED_TOTAL] == pytest.approx(10.0)
