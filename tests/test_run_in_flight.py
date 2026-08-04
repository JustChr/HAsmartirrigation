"""One in-flight-run lookup, used by the calculation gate and the dispatch gate.

Two defects share the same missing primitive (see run_state.RunStateMixin):

* a calculation landing inside a run was erased, because every run path settles
  the bucket absolutely from an anchor captured before the valve opened;
* nothing refused to dispatch a zone that already had a run in flight.

The dispatch tests here deliberately hold the bucket BELOW ``bucket_threshold``
so the demand gate (``duration > 0 AND bucket < bucket_threshold``) cannot be
what rejects the second dispatch. Without that, the tests would pass whether or
not the guard exists.

Coordinators are built with ``__new__`` so only the touched attributes are wired.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


class _FakeStore:
    """Minimal store with real read/write semantics for zones + config."""

    def __init__(self, zones=None, distributors=None, **config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}
        self.distributors = {int(k): v for k, v in (distributors or {}).items()}
        self.config = SimpleNamespace(
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
            live_estimate_enabled=False,
            log_no_demand=False,
            **config,
        )

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    def get_distributor(self, distributor_id):
        d = self.distributors.get(int(distributor_id))
        return dict(d) if d is not None else None

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(
            changes
        )
        return dict(self.zones[int(zone_id)])


def _zone(**over):
    """A zone that is due: duration > 0 and bucket BELOW the threshold."""
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_BUCKET: -20.0,
        const.ZONE_BUCKET_THRESHOLD: -5.0,
        const.ZONE_DURATION: 300,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MAXIMUM_DURATION: 36000,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_MAPPING: 0,
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


def _coord(monkeypatch, zones=None, distributors=None, **config):
    for module in ("irrigation", "calculation"):
        monkeypatch.setattr(
            f"custom_components.smart_irrigation.{module}.async_dispatcher_send",
            Mock(),
        )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.services = Mock()
    hass.services.async_call = AsyncMock()
    hass.states = Mock()
    hass.states.get = Mock(return_value=None)
    hass.async_create_task = Mock()
    coord.hass = hass
    coord.store = _FakeStore(zones or [_zone()], distributors, **config)
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord.async_master_acquire = AsyncMock()
    coord.async_master_release = AsyncMock()
    coord._dispatch_distributor_cycles = AsyncMock(return_value=False)
    coord._apply_live_durations = AsyncMock(side_effect=lambda z: z)
    coord._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    coord._rain_delay_active = Mock(return_value=False)
    coord._dispatch_sequencing = AsyncMock()
    coord._irrigate_zones_parallel = AsyncMock()
    coord.async_update_zone_config = AsyncMock()
    return coord


def _sc_run(zone_id=1, planned=600, started=None):
    return {
        const.RUN_ZONE_ID: zone_id,
        const.RUN_PLANNED_SECONDS: planned,
        const.RUN_STARTED: (started or dt_util.utcnow()).isoformat(),
        const.RUN_PRE_BUCKET: -20.0,
    }


# --------------------------------------------------------------------------- #
# The lookup itself
# --------------------------------------------------------------------------- #
def test_no_run_anywhere_is_not_in_flight(monkeypatch):
    assert _coord(monkeypatch).zone_run_in_flight(1) is False


def test_classic_registry_counts(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}
    assert coord.zone_run_in_flight(1) is True
    assert coord.zone_run_in_flight(2) is False


def test_self_closing_record_inside_its_window_counts(monkeypatch):
    coord = _coord(monkeypatch)
    coord.store.config.active_valve_runs = [_sc_run()]
    assert coord.zone_run_in_flight(1) is True


def test_self_closing_record_past_its_window_does_not_count(monkeypatch):
    """The hardware owns the close, so an overdue record is a finaliser that has
    not run yet — not an open valve. Counting it would let one record that
    outlived its finaliser block the zone's runs forever."""
    coord = _coord(monkeypatch)
    stale = _sc_run(planned=60, started=dt_util.utcnow() - dt_util.dt.timedelta(hours=2))
    coord.store.config.active_valve_runs = [stale]
    assert coord.zone_run_in_flight(1) is False


def test_distributor_cycle_counts_for_its_members(monkeypatch):
    coord = _coord(
        monkeypatch,
        zones=[_zone(**{const.ZONE_DISTRIBUTOR_ID: 0})],
        distributors={0: {"id": 0, "active_cycle": {"outlet": 1, "phase": "watering"}}},
    )
    assert coord.zone_run_in_flight(1) is True
    coord.store.distributors[0]["active_cycle"] = {}
    assert coord.zone_run_in_flight(1) is False


# --------------------------------------------------------------------------- #
# The calculation gives way
# --------------------------------------------------------------------------- #
async def test_calculation_is_deferred_and_consumes_nothing(monkeypatch):
    """The gate must return BEFORE the window is aggregated: last_consumed_at is
    only advanced on the write path, so an untouched watermark is what makes the
    deferral lossless."""
    coord = _coord(monkeypatch)
    coord._aggregate_for_zone = AsyncMock()
    coord.calculate_module = AsyncMock()
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_calculate_zone(1)

    coord._aggregate_for_zone.assert_not_awaited()
    coord.calculate_module.assert_not_awaited()
    assert const.ZONE_LAST_CONSUMED not in coord.store.zones[1]
    assert coord.store.zones[1][const.ZONE_BUCKET] == -20.0
    assert coord._deferred_calc_zones == {1}


async def test_calculation_runs_normally_with_no_run_in_flight(monkeypatch):
    coord = _coord(monkeypatch)
    coord._aggregate_for_zone = AsyncMock(return_value=({"x": 1}, 3))
    coord.calculate_module = AsyncMock(return_value={const.ZONE_BUCKET: -1.0})
    coord._prune_mapping_buffer = AsyncMock()

    await coord.async_calculate_zone(1)

    coord.calculate_module.assert_awaited_once()
    assert coord.store.zones[1][const.ZONE_BUCKET] == -1.0
    assert not getattr(coord, "_deferred_calc_zones", set())


async def test_deferred_calculation_runs_once_the_run_ends(monkeypatch):
    coord = _coord(monkeypatch)
    coord.defer_zone_calculation(1)

    await coord.async_run_deferred_calculation(1)

    coord.async_update_zone_config.assert_awaited_once()
    kwargs = coord.async_update_zone_config.await_args.kwargs
    assert kwargs["zone_id"] == 1
    assert kwargs["data"] == {const.ATTR_CALCULATE: True}
    assert coord._deferred_calc_zones == set()


async def test_deferred_calculation_stays_deferred_under_a_new_run(monkeypatch):
    coord = _coord(monkeypatch)
    coord.defer_zone_calculation(1)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_run_deferred_calculation(1)

    coord.async_update_zone_config.assert_not_awaited()
    assert coord._deferred_calc_zones == {1}


async def test_deferred_calculation_is_a_noop_when_nothing_was_deferred(monkeypatch):
    coord = _coord(monkeypatch)
    await coord.async_run_deferred_calculation(1)
    coord.async_update_zone_config.assert_not_awaited()


async def test_a_failing_deferred_calculation_is_swallowed_and_re_queued(monkeypatch):
    """It is called from run teardown (including a ``finally``); a zone whose
    mapping has no data raises. The window is still unconsumed either way."""
    coord = _coord(monkeypatch)
    coord.async_update_zone_config = AsyncMock(side_effect=RuntimeError("no data"))
    coord.defer_zone_calculation(1)

    await coord.async_run_deferred_calculation(1)

    assert coord._deferred_calc_zones == {1}


async def test_classic_run_defers_the_calculation_and_runs_it_at_the_end(monkeypatch):
    """End to end on the path that reproduced the erasure: a calculation fired
    mid-run leaves the bucket alone, and lands after the run's final commit."""
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord = _coord(monkeypatch)
    coord._live_run_zones = set()
    coord._aggregate_for_zone = AsyncMock()
    coord._record_run = AsyncMock()
    calls = []

    real_sleep_or_stopped = coord._sleep_or_stopped

    async def _tick(zone_id, seconds):
        calls.append(seconds)
        if len(calls) == 1:
            await coord.async_calculate_zone(1)  # the daily calc lands mid-run
        return await real_sleep_or_stopped(zone_id, seconds)

    coord._sleep_or_stopped = _tick

    await coord._run_valve_metered(_zone(), "switch.valve", real_flow=False)

    # nothing was consumed while the valve was open ...
    coord._aggregate_for_zone.assert_not_awaited()
    # ... the run settled the bucket on its own (300 s @ 10 L/min over 10 m²) ...
    assert coord.store.zones[1][const.ZONE_BUCKET] == pytest.approx(-15.0)
    # ... and the displaced calculation ran once the run finalised.
    coord.async_update_zone_config.assert_awaited_once()
    assert coord.async_update_zone_config.await_args.kwargs["data"] == {
        const.ATTR_CALCULATE: True
    }


# --------------------------------------------------------------------------- #
# Nothing dispatches a zone that is already running
# --------------------------------------------------------------------------- #
async def test_scheduled_dispatch_skips_a_running_zone(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    watered = await coord._irrigate_linked_entities()

    assert watered is False
    coord._dispatch_sequencing.assert_not_awaited()


async def test_scheduled_dispatch_still_runs_an_idle_zone(monkeypatch):
    """The guard must not be what makes the previous test pass."""
    coord = _coord(monkeypatch)

    watered = await coord._irrigate_linked_entities()

    assert watered is True
    coord._dispatch_sequencing.assert_awaited_once()


async def test_irrigate_now_skips_a_running_zone(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_irrigate_now("1")

    coord._dispatch_sequencing.assert_not_awaited()


async def test_irrigate_now_still_runs_an_idle_zone(monkeypatch):
    coord = _coord(monkeypatch)
    await coord.async_irrigate_now("1")
    coord._dispatch_sequencing.assert_awaited_once()


async def test_run_zone_rejects_a_running_zone(monkeypatch):
    coord = _coord(monkeypatch)
    coord._active_runs = {1: {"stop": Mock(), "started_at": "x", "ends_at": None}}

    await coord.async_run_zone(1, 5)

    coord._irrigate_zones_parallel.assert_not_awaited()


async def test_run_zone_still_runs_an_idle_zone(monkeypatch):
    coord = _coord(monkeypatch)
    await coord.async_run_zone(1, 5)
    coord._irrigate_zones_parallel.assert_awaited_once()


async def test_self_closing_dispatch_rejects_a_second_run(monkeypatch):
    """Backstop for _sc_add_run, which REPLACES an existing record for the same
    zone rather than rejecting — so a second dispatch reaching it would open the
    valve again, credit the bucket twice and orphan the first run."""
    zone = _zone(
        **{
            const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
            const.ZONE_RUN_SERVICE: "script.valve",
            const.ZONE_LINKED_ENTITY: None,
        }
    )
    coord = _coord(monkeypatch, zones=[zone])
    coord._note_si_valve = Mock()
    coord.store.config.active_valve_runs = [_sc_run()]

    started = await coord.async_run_self_closing(zone)

    assert started is False
    coord.hass.services.async_call.assert_not_awaited()
