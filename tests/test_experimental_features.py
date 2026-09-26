"""Tests for the experimental Setup features.

Covers the two opt-in features wired to the Experimental tab:
  * Forecast-weighted durations (calculation.calculate_module) — water less when
    rain is forecast, leaving the leftover deficit in ``irrigation_target_bucket``.
  * The runner crediting a completed run to that per-zone target instead of 0.
  * Observed-watering bucket crediting (ObservedWateringMixin) — credit external
    valve runs, suppress Irrigation Plus's own runs.

Like test_calculate_module, coordinators are built with ``__new__`` so only the
attributes each method actually touches are wired up.
"""

import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util
import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const


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
    coord.recurring_schedule_manager = SimpleNamespace(
        async_next_run_start_for_zone=AsyncMock(return_value=RUN_START)
    )
    return coord


UTC = datetime.timezone.utc
# Midnight of the first forecast day, so each 24-hour block from the run lines up
# with exactly one dated entry and these tests keep testing the weighting's
# ARITHMETIC rather than partial-day overlap. A run at 06:00 would make every
# block 18/24 of one entry plus 6/24 of the next, which is real behaviour and is
# tested in test_forecast_weighting_window.py -- but it would silently rewrite the
# numbers four tests here were written to assert.
RUN_START = datetime.datetime(2026, 9, 27, tzinfo=UTC)


def _days(*mm):
    """Dated daily entries, the shape every client has supplied since #145.

    Seven days minimum on this path: expected_rain reports first_24h_covered
    False when the entries do not span the run's whole 24-hour block, and the
    weighting then abstains -- which reads as the code being broken when it is
    the fixture being short. Measured: two days abstains, three and above cover.
    """
    entries = []
    for index in range(max(7, len(mm))):
        start = datetime.datetime(2026, 9, 27, tzinfo=UTC) + datetime.timedelta(
            days=index
        )
        entries.append(
            {
                const.MAPPING_PRECIPITATION: mm[index] if index < len(mm) else 0.0,
                const.FORECAST_DAY_START: start,
                const.FORECAST_DAY_END: start + datetime.timedelta(days=1),
            }
        )
    return entries


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
        _zone(), _weather(10.0), _days(4.0)
    )

    assert data[const.ZONE_BUCKET] == pytest.approx(-10.0)
    assert data[const.ZONE_DURATION] == 600  # 10 mm / 60 mm/h * 3600
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)


async def test_forecast_weighting_reduces_duration_and_sets_target():
    """4 mm forecast trims a 10 mm deficit run to 6 mm; 4 mm left for the rain."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True)
    data = await coord.calculate_module(
        _zone(), _weather(10.0), _days(4.0)
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
        _zone(), _weather(10.0), _days(12.0)
    )

    assert data[const.ZONE_BUCKET] == pytest.approx(-10.0)
    assert data[const.ZONE_DURATION] == 0
    assert data[const.ZONE_IRRIGATION_TARGET_BUCKET] == pytest.approx(0.0)


async def test_forecast_weighting_sums_lookahead_days():
    """Precip is summed over the configured look-ahead window."""
    coord = _calc_coordinator(forecast_weighting=True, use_weather_service=True, days=2)
    data = await coord.calculate_module(
        _zone(), _weather(10.0), _days(2.0, 3.0, 9.0)
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
        "custom_components.irrigation_plus.irrigation.async_dispatcher_send",
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
    # Default to a real (flow-sensor-less) zone dict: the open edge now reads
    # store.get_zone to decide whether to start the flow sampler, so an auto-Mock
    # would look like a zone with a flow sensor. Credit tests override this.
    coord.store.get_zone = Mock(return_value={})
    coord._si_driven_until = {}
    coord._observed_on_since = {}
    coord._observed_zone_by_entity = {"switch.valve": 1}
    monkeypatch.setattr(
        "custom_components.irrigation_plus.observed_watering.async_dispatcher_send",
        Mock(),
    )
    # _credit_observed_watering now also calls _record_run (irrigation.py), which
    # dispatches from that module — stub it too so the Mock hass isn't iterated.
    monkeypatch.setattr(
        "custom_components.irrigation_plus.irrigation.async_dispatcher_send",
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


def test_si_dispatch_onto_an_already_open_valve_drops_the_external_window(monkeypatch):
    """SI dispatching onto a valve a hand already opened leaves nothing for the
    close edge to credit — the runner accounts for its own run.

    The open edge is the observer's only gate, and it never fires here: the
    entity is already "on", so there is no state transition to judge.
    """
    coord = _observer_coordinator(monkeypatch, loop_time=1000.0)
    # The user opens the tap by hand: no SI run in flight, no suppression window.
    coord._observed_state_changed(_event("switch.valve", "on", "off"))
    assert 1 in coord._observed_on_since

    # Hours later SI dispatches its own 10-minute run on the same valve.
    coord._note_si_valve(1, 600)

    # The valve finally goes off.
    coord._observed_state_changed(_event("switch.valve", "off", "on"))

    coord.hass.async_create_task.assert_not_called()


def test_a_flap_after_the_takeover_credits_nothing(monkeypatch):
    """`unavailable` is a CLOSE edge, so a Zigbee dropout mid-run would credit
    the stretch since the external open — a partial double credit that needs no
    particular ordering of the run's end and the valve's close."""
    coord = _observer_coordinator(monkeypatch, loop_time=1000.0)
    coord._observed_state_changed(_event("switch.valve", "on", "off"))
    coord._note_si_valve(1, 600)

    coord._observed_state_changed(_event("switch.valve", "unavailable", "on"))

    coord.hass.async_create_task.assert_not_called()


def test_the_takeover_drops_the_marker_for_a_string_zone_id(monkeypatch):
    """Both marker dicts are keyed by int, and not every caller of
    _note_si_valve normalises its id (irrigation.py does not, batch.py does).
    A raw-key drop would silently miss."""
    coord = _observer_coordinator(monkeypatch, loop_time=1000.0)
    coord._observed_state_changed(_event("switch.valve", "on", "off"))
    assert 1 in coord._observed_on_since

    coord._note_si_valve("1", 600)

    assert 1 not in coord._observed_on_since


def test_the_takeover_does_not_outlive_the_tightened_window(monkeypatch):
    """Regression pin for the unconditional drop. The two close-side re-notes
    (_run_valve_metered, _irrigate_zone_flow_slot) call _note_si_valve with
    run_seconds=0 to SHRINK the window so a genuine external open after the run
    is tracked again. Dropping the marker there must not turn that into a
    permanent block."""
    coord = _observer_coordinator(monkeypatch, loop_time=1000.0)
    coord._note_si_valve(1, 0)  # run end: window = now + SI_VALVE_SUPPRESS_MARGIN
    assert coord._si_driven_until[1] == pytest.approx(1030.0)

    coord.hass.loop.time = Mock(return_value=1031.0)
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


async def test_observed_credit_zeroes_duration_when_satisfied(monkeypatch):
    """REGEL-8 sibling of _stamp_run_finalized: an observed run that leaves an
    AUTOMATIC zone satisfied (bucket back to >= 0) must also reset the displayed
    Duration. External water overshoots the deficit, so the bucket lands POSITIVE
    (not exactly 0) and the store's bucket==0 -> duration 0 shortcut alone would
    miss it, leaving a stale Duration the way self-closing/distributor runs did."""
    coord = _observer_coordinator(monkeypatch)
    coord.store.get_zone = Mock(
        return_value={
            const.ZONE_ID: 1,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_BUCKET: -0.5,
            const.ZONE_DURATION: 300,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )

    await coord._credit_observed_watering(1, 60)  # +1 mm -> bucket = +0.5 (positive)

    bucket_calls = [
        c
        for c in coord.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in c.args[1]
    ]
    assert bucket_calls, "observed credit should write the bucket"
    changes = bucket_calls[-1].args[1]
    assert changes[const.ZONE_BUCKET] == pytest.approx(0.5)
    assert changes[const.ZONE_BUCKET] > 0  # overshoot: not exactly 0
    assert const.ZONE_LAST_IRRIGATION in changes
    assert changes[const.ZONE_DURATION] == 0


async def test_observed_credit_leaves_duration_for_non_automatic_zone(monkeypatch):
    """The duration reset is gated on an AUTOMATIC zone (mirrors the store
    shortcut + _stamp_run_finalized); a manual zone's Duration is left untouched."""
    coord = _observer_coordinator(monkeypatch)
    coord.store.get_zone = Mock(
        return_value={
            const.ZONE_ID: 1,
            const.ZONE_STATE: const.ZONE_STATE_MANUAL,
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_BUCKET: -0.5,
            const.ZONE_DURATION: 300,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )

    await coord._credit_observed_watering(1, 60)

    bucket_calls = [
        c
        for c in coord.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in c.args[1]
    ]
    changes = bucket_calls[-1].args[1]
    assert const.ZONE_DURATION not in changes
