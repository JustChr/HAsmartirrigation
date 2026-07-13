"""Tests for continuous (metered) watering accounting.

The runner credits a zone's bucket and ``water_used_total`` *while the valve is
open* — synthesizing a constant ``throughput`` L/min rate for timed zones and
integrating the sensor for real-flow zones — instead of one binary write at the
end. End-state is identical to the old behaviour (same final bucket, same total
water); only the trajectory is gradual and a mid-run crash keeps partial
progress. These tests pin both the end-state and the two bug-class guards:
``water_used_total`` is never double-counted, and progress is persisted as it
accrues.

Coordinators are built with ``__new__`` so only the touched attributes are wired.
"""

import contextlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


class _FakeStore:
    """Minimal store that keeps zone dicts in memory (real read/write semantics)."""

    def __init__(self, zones):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.config = SimpleNamespace(
            zone_sequencing_max_consecutive_duration=5,
            zone_sequencing_min_absorption_time=0,
        )
        self.bucket_writes = []  # every bucket level persisted, in order

    def get_zone(self, zid):
        z = self.zones.get(int(zid))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zid, changes):
        if const.ZONE_BUCKET in changes:
            self.bucket_writes.append(changes[const.ZONE_BUCKET])
        self.zones.setdefault(int(zid), {const.ZONE_ID: int(zid)}).update(changes)
        return dict(self.zones[int(zid)])


def _coord(monkeypatch, zones, *, units=METRIC_SYSTEM, flow_rate=None, confirm=True):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = units
    hass.services = Mock()
    hass.services.async_call = AsyncMock()
    hass.states = Mock()
    if flow_rate is None:
        hass.states.get = Mock(return_value=None)
    else:
        state = Mock()
        state.state = str(flow_rate)
        state.attributes = {"unit_of_measurement": "L/min"}
        hass.states.get = Mock(return_value=state)
    coord.hass = hass
    coord.store = _FakeStore(zones)
    coord._confirm_valve_running = AsyncMock(return_value=confirm)
    return coord


def _zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_BUCKET: -5.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_THROUGHPUT: 10.0,  # 10 L/min over 10 m² == 1 mm/min
        const.ZONE_DURATION: 300,
        const.ZONE_MAXIMUM_DURATION: 36000,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


def _bucket(coord):
    return coord.store.zones[1].get(const.ZONE_BUCKET)


def _used(coord):
    return coord.store.zones[1].get(const.ZONE_WATER_USED_TOTAL, 0.0)


def _log(coord):
    return coord.store.zones[1].get(const.ZONE_RUN_LOG, [])


# --------------------------------------------------------------------------- #
# Synthetic (throughput-only) timed runs
# --------------------------------------------------------------------------- #
async def test_synthetic_run_lands_on_target(monkeypatch):
    """A normal timed run ends at its target (0) — same as the old binary write."""
    coord = _coord(monkeypatch, [_zone(**{const.ZONE_BUCKET: -5.0})])
    coord._live_run_zones = set()
    # 300 s @ 10 L/min = 50 L over 10 m² = 5 mm -> -5 + 5 = 0
    await coord._run_valve_metered(
        _zone(**{const.ZONE_BUCKET: -5.0}), "switch.v", real_flow=False
    )
    assert _bucket(coord) == pytest.approx(0.0)
    assert _used(coord) == pytest.approx(50.0)


async def test_water_used_not_double_counted(monkeypatch):
    """The streamed-in volume is counted once — the completion record adds nothing."""
    coord = _coord(monkeypatch, [_zone()])
    coord._live_run_zones = set()
    await coord._run_valve_metered(_zone(), "switch.v", real_flow=False)
    # exactly the delivered volume, NOT twice it
    assert _used(coord) == pytest.approx(50.0)
    log = _log(coord)
    assert len(log) == 1
    assert log[0]["result"] == const.RUN_RESULT_COMPLETED
    assert log[0]["volume_l"] == pytest.approx(50.0)  # shown for display


async def test_progress_committed_incrementally(monkeypatch):
    """A long run commits the bucket repeatedly so a crash keeps partial progress.

    Each commit is an absolute, idempotent write of the rising bucket level; the
    fact that there are several (not one binary write at the end) is what makes a
    mid-run restart keep the water already applied.
    """
    z = _zone(**{const.ZONE_BUCKET: -10.0, const.ZONE_DURATION: 600})
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    # 600 s @ 10 L/min = 100 L = 10 mm -> -10 + 10 = 0
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=False)

    writes = coord.store.bucket_writes
    assert len(writes) > 2  # committed on the coarse interval, not once at the end
    assert writes == sorted(writes)  # monotonically rising as water accrues
    assert writes[-1] == pytest.approx(0.0)
    assert _used(coord) == pytest.approx(100.0)


async def test_live_run_allows_surplus(monkeypatch):
    """A live-estimate run may credit past 0 up to maximum_bucket."""
    z = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_DURATION: 480})
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = {1}
    # 480 s @ 10 L/min = 80 L = 8 mm -> -5 + 8 = 3 (ceiling is maximum_bucket 50)
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=False)
    assert _bucket(coord) == pytest.approx(3.0)
    assert 1 not in coord._live_run_zones


async def test_timed_multiplier_lands_on_target(monkeypatch):
    """The zone multiplier inflates a timed run's duration as part of the need,
    so it is divided back out when crediting the bucket — a full run lands at the
    target for any multiplier, while water_used stays the gross litres delivered."""
    # multiplier 0.5: real duration would be base(300s)*0.5 = 150 s -> 25 L gross
    # = 2.5 mm physical, /0.5 = 5 mm credited -> -5 + 5 = 0 (target).
    z = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_DURATION: 150,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 0.5,
        }
    )
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=False)
    assert _bucket(coord) == pytest.approx(0.0)  # divided out -> lands at target
    assert _used(coord) == pytest.approx(25.0)  # gross litres, NOT divided


async def test_unconfirmed_valve_still_waters(monkeypatch):
    """An unconfirmed valve is NOT aborted: the run proceeds, credits the water
    and raises no fault — the valve may be open but just slow to report state."""
    coord = _coord(monkeypatch, [_zone()], confirm=False)
    coord._live_run_zones = set()
    await coord._run_valve_metered(_zone(), "switch.v", real_flow=False)
    assert coord.get_zone_fault(1) is None  # no fault raised
    assert _bucket(coord) == pytest.approx(0.0)  # watered to target
    assert _used(coord) == pytest.approx(50.0)  # 300 s @ 10 L/min
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED


# --------------------------------------------------------------------------- #
# Real flow-meter runs
# --------------------------------------------------------------------------- #
async def test_real_flow_credits_measured_volume(monkeypatch):
    """A flow run stops at its target volume and credits the measured litres."""
    z = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, [z], flow_rate=20)  # 20 L/min
    coord._live_run_zones = set()
    # target = 10 m² * 5 mm = 50 L; at 20 L/min that is 10 polls of 5 L
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    assert _bucket(coord) == pytest.approx(0.0)
    assert _used(coord) == pytest.approx(50.0)
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED


async def test_real_flow_ignores_live_marker_for_target(monkeypatch):
    """A flow zone marked live (e.g. a manual run_zone) tops up to the deficit
    floor, NOT to maximum_bucket — the live surplus ceiling must not balloon the
    flow target volume and overfill the zone."""
    z = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )
    coord = _coord(monkeypatch, [z], flow_rate=20)
    coord._live_run_zones = {1}  # manual run_zone marks every zone, incl. flow
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    # target = 10 m² * 5 mm (floor 0) = 50 L, NOT 10 * 55 = 550 L to maximum_bucket
    assert _bucket(coord) == pytest.approx(0.0)
    assert _used(coord) == pytest.approx(50.0)
    assert 1 not in coord._live_run_zones  # stray marker consumed


async def test_real_flow_never_started_faults(monkeypatch):
    """A flow valve that never registers flow faults and credits nothing."""
    z = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_MAXIMUM_DURATION: 30,  # short safety timeout
        }
    )
    coord = _coord(monkeypatch, [z], flow_rate=0)
    coord._live_run_zones = set()
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    assert coord.get_zone_fault(1)["reason"] == const.FAULT_FLOW_NEVER_STARTED
    assert _bucket(coord) == pytest.approx(-5.0)
    assert _used(coord) == 0.0
    assert _log(coord)[0]["result"] == const.RUN_RESULT_FAILED


# --------------------------------------------------------------------------- #
# Rotating strategy: per-slot accounting + closed FLOW run-log / fault gap
# --------------------------------------------------------------------------- #
async def test_rotating_flow_records_run_log(monkeypatch):
    """Rotating flow zones now get a run-log entry (was the WS-1/WS-2 gap)."""
    z = _zone(
        **{
            const.ZONE_BUCKET: -2.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_LINKED_ENTITY: "switch.valve",
        }
    )
    coord = _coord(monkeypatch, [z], flow_rate=20)
    coord._live_run_zones = set()
    await coord._irrigate_zones_rotating([dict(z)])
    log = _log(coord)
    assert log and log[0]["result"] == const.RUN_RESULT_COMPLETED
    assert _bucket(coord) == pytest.approx(0.0)  # -2 + 2 mm (20 L over 10 m²)
    assert _used(coord) == pytest.approx(20.0)


async def test_rotating_flow_never_started_faults(monkeypatch):
    """Rotating flow zones now fault when the sensor never registers flow."""
    z = _zone(
        **{
            const.ZONE_BUCKET: -2.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_MAXIMUM_DURATION: 30,
        }
    )
    coord = _coord(monkeypatch, [z], flow_rate=0)
    coord._live_run_zones = set()
    await coord._irrigate_zones_rotating([dict(z)])
    assert coord.get_zone_fault(1)["reason"] == const.FAULT_FLOW_NEVER_STARTED
    assert _log(coord)[0]["result"] == const.RUN_RESULT_FAILED


async def test_rotating_timed_credits_continuously(monkeypatch):
    """Rotating timed zones land on target with water counted once."""
    z = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_DURATION: 300})
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    await coord._irrigate_zones_rotating([dict(z)])
    assert _bucket(coord) == pytest.approx(0.0)
    assert _used(coord) == pytest.approx(50.0)
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED


# --------------------------------------------------------------------------- #
# Real flow-meter runs: TOTALIZER (cumulative counter) sensors
# --------------------------------------------------------------------------- #
def _totalizer_sensor(coord, values, *, unit="L", state_class="total_increasing"):
    """Wire ``hass.states.get`` to return a RISING cumulative counter.

    Each poll yields the next reading from ``values`` (holding the last once the
    list is exhausted), carrying a totalizer unit/state_class so the run loop
    must credit the DELTA between successive readings, not integrate the raw
    counter as a rate.
    """
    seq = iter(values)
    last = [values[-1]]

    def _get(_entity_id):
        with contextlib.suppress(StopIteration):
            last[0] = next(seq)
        state = Mock()
        state.state = str(last[0])
        state.attributes = {
            "unit_of_measurement": unit,
            "state_class": state_class,
        }
        return state

    coord.hass.states.get = Mock(side_effect=_get)


async def test_metered_zone_totalizer_credits_delta_and_early_stops(monkeypatch):
    """A totalizer credits the measured DELTA (not the raw counter) and early-stops.

    A counter climbing 1000 -> 1010 -> 1020 ... L delivers 10 L per step; the run
    must credit the summed deltas and stop once the 50 L target is reached — NOT
    integrate the ~1000 raw reading as a L/min rate (which would over-deliver).
    """
    z = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    # First read seeds the baseline (0 L), then +10 L per step. target = 50 L,
    # reached after 5 deltas -> summed deltas == 50, absolute counter is ~1050.
    _totalizer_sensor(
        coord,
        [1000.0, 1010.0, 1020.0, 1030.0, 1040.0, 1050.0, 1060.0, 1070.0],
    )
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    # Credited the summed DELTAS (50 L), NOT the absolute counter (~1050 L) and
    # NOT the counter integrated as a rate.
    assert _used(coord) == pytest.approx(50.0)
    assert _bucket(coord) == pytest.approx(0.0)
    # Early-stopped on the target volume, not the maximum_duration safety timeout.
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED


async def test_metered_zone_totalizer_reset_contributes_zero(monkeypatch):
    """A mid-run counter reset contributes 0 and HOLDS the prior baseline.

    The counter rolls back (1020 -> 500) partway through and climbs again but stays
    below the pre-reset 1020 baseline. Under the keep-baseline rule the reset step —
    and every below-baseline reading that follows — adds 0 L: only the real pre-reset
    deltas (1000 -> 1020 = 20 L) are credited. Never the absolute 500 counter, never a
    negative 500-1020 delta, and never an over-credited recovery from the low value. A
    genuine reset that never recovers above the baseline is a safe UNDER-credit: the
    run tops out at 20 L and ends on the safety timeout rather than the target volume.
    """
    z = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_MAXIMUM_DURATION: 150,  # bounded: never reaches target -> times out
        }
    )
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    # seed(1000)=0, +10, +10, then reset->500 and up: all below the held 1020 baseline
    # so each adds 0. Credited = 20 L (the pre-reset deltas only), target 50 unreached.
    _totalizer_sensor(
        coord,
        [1000.0, 1010.0, 1020.0, 500.0, 510.0, 520.0, 530.0, 540.0],
    )
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    # 20 L proves the reset + its below-baseline recovery each added 0 (not +500
    # absolute, not -520 negative, not an over-credited 510-500 recovery jump).
    assert _used(coord) == pytest.approx(20.0)
    assert _bucket(coord) == pytest.approx(-3.0)  # -5 + 2 mm (20 L over 10 m²)
    assert _log(coord)[0]["result"] == const.RUN_RESULT_PARTIAL


async def test_metered_zone_totalizer_glitch_low_is_absorbed(monkeypatch):
    """A single transient glitch-low is absorbed; recovery credits the REAL delta.

    The counter climbs 1000 -> 1010 -> 1020, dips to 5 for one poll, then recovers
    1030 -> 1040. The dip step adds 0 and KEEPS the 1020 baseline, so the recovery
    credits 1030-1020 = 10 (the real forward delta), NOT 1030-5 = 1025 (the
    glitch-low over-credit bug). Summed forward deltas = 10+10+0+10+10 = 40 L.
    The 50 L target is above 40 L so the run does not early-stop mid-sequence.
    """
    z = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_MAXIMUM_DURATION: 150,  # bounded: drain the sequence then time out
        }
    )
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    _totalizer_sensor(
        coord,
        [1000.0, 1010.0, 1020.0, 5.0, 1030.0, 1040.0],
    )
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    # 40 L = the true forward-delta sum. The dip + its recovery contribute the
    # real 10, NOT the absolute 1025 counter jump (glitch-low over-credit).
    assert _used(coord) == pytest.approx(40.0)
    assert _bucket(coord) == pytest.approx(-1.0)  # -5 + 4 mm (40 L over 10 m²)


async def test_metered_zone_totalizer_m3_conversion(monkeypatch):
    """A totalizer reporting m³ is converted to litres (×1000) on the zone path.

    The counter advances 10.000 -> 10.020 m³ = 20 L; this verifies
    ``_flow_litres_from_total`` is applied to the zone totalizer delta (not treated
    as a raw 0.020 L advance). Target is 20 L (bucket -2 over 10 m²) so the run
    early-stops exactly on the measured volume.
    """
    z = _zone(**{const.ZONE_BUCKET: -2.0, const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    _totalizer_sensor(
        coord,
        [10.000, 10.010, 10.020, 10.030, 10.040],
        unit="m³",
    )
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    # 0.020 m³ × 1000 = 20 L (NOT 0.020 L); lands exactly on the 20 L target.
    assert _used(coord) == pytest.approx(20.0)
    assert _bucket(coord) == pytest.approx(0.0)
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED


async def test_metered_zone_per_run_counter_credits_climb_and_persists_end(monkeypatch):
    """A per_run counter reseeds at the valve-open reset, credits the run's climb, and
    persists its end value for cross-run learning.

    ``flow_counter_type='per_run'`` tells the FlowMeter this counter zeroes each run:
    the counter reads 62 at valve-open (seed), drops to 0 (the open reset -> reseed the
    baseline to 0, credit nothing) then climbs 10 -> 50. The run credits the measured
    climb (50 L, reached at the 50 L target) — NOT 0 L, which the over-credit-safe
    'lifetime' default would credit (every post-seed reading stays below the 62 seed, so
    a lifetime meter never rises and would fault FLOW_NEVER_STARTED). After the run the
    zone's ``flow_last_end`` holds the last counter value (50) for the next run's reset
    check.
    """
    z = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_FLOW_COUNTER_TYPE: "per_run",
        }
    )
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    # open seed 62, reset to 0, then climb; target = 10 m² * 5 mm = 50 L reached at 50.
    _totalizer_sensor(
        coord,
        [62.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0],
    )
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    # Credited the measured climb from the reset floor (50 L), not 0 (lifetime default).
    assert _used(coord) == pytest.approx(50.0)
    assert _bucket(coord) == pytest.approx(0.0)
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED
    # The run's end value is persisted for the next run's cross-run reset check.
    assert coord.store.get_zone(1)[const.ZONE_FLOW_LAST_END] == pytest.approx(50.0)


async def test_metered_zone_auto_streak_advances_and_resolves_per_run(monkeypatch):
    """An 'auto' counter opening on a reset advances the cross-run streak, PERSISTS it,
    and — once the streak crosses the threshold — resolves to per_run and credits the climb.

    This pins the streak-learning WIRING that the per_run neighbour above bypasses (it
    overrides ``flow_counter_type`` and so never resolves a streak). Here the type is the
    default ``'auto'`` and the learning state is pre-seeded so THIS run is the one that
    crosses the threshold: ``flow_last_end=50`` / ``flow_reset_streak=1``. The valve-open
    read (0, well below the 0.5*50=25 reset bar) is a reset, so ``_flow_build_meter`` calls
    ``flow_learn_next_streak(50, 0, 1) -> 2`` and ``_run_valve_metered`` persists the new
    streak at run start. streak 2 hits the threshold, ``flow_learn_resolve('auto', 2)``
    resolves to per_run, and the meter credits the measured 0 -> 50 climb (target 50 L).
    """
    z = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_FLOW_SENSOR: "sensor.flow",
            const.ZONE_FLOW_COUNTER_TYPE: "auto",  # default; NOT the per_run override
            const.ZONE_FLOW_LAST_END: 50.0,  # pre-seed: prior run ended at 50 L
            const.ZONE_FLOW_RESET_STREAK: 1,  # pre-seed: one prior open-reset already
        }
    )
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    # open read 0 is a reset vs the pre-seeded 50 (0 < 0.5*50), then climb; target 50 L.
    _totalizer_sensor(coord, [0.0, 10.0, 30.0, 50.0])
    await coord._run_valve_metered(dict(z), "switch.v", real_flow=True)
    # WIRING under test: the streak advanced 1 -> 2 AND was persisted at run start
    # (``_flow_build_meter`` computed it, ``_run_valve_metered`` wrote start_changes).
    assert coord.store.get_zone(1)[const.ZONE_FLOW_RESET_STREAK] == 2
    # The run's end value is persisted for the next run's cross-run reset check.
    assert coord.store.get_zone(1)[const.ZONE_FLOW_LAST_END] == pytest.approx(50.0)
    # streak 2 -> flow_learn_resolve('auto', 2) == per_run; the meter measured the climb
    # (50 L, reached at the 50 L target) — NOT a fault / 0.
    assert _used(coord) == pytest.approx(50.0)
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED


async def test_rotating_flow_slot_measures_totalizer(monkeypatch):
    """FM-4: a single rotating slot measures its own totalizer window via a FlowMeter.

    Each rotating slot is its own valve-open window, so it gets its own fresh
    FlowMeter seeded at the open read. A lifetime totalizer climbing 0 -> 10 -> 30 L
    across the slot returns the slot's delta (30 L) — NOT 0 and NOT the raw counter.
    This also captures the slot's first interval, which the retired per-step
    increment seam lost. remaining_volume caps the slot exactly at 30 L.
    """
    z = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    # Seeded at open (0), then climbs to 10, then 30 — the slot delivers the 30 L delta.
    _totalizer_sensor(coord, [0.0, 10.0, 30.0])
    delivered = await coord._irrigate_zone_flow_slot(
        dict(z), "switch.valve", max_seconds=300.0, remaining_volume=30.0
    )
    assert delivered == pytest.approx(30.0)


async def test_rotating_totalizer_measures_slot_delta(monkeypatch):
    """Rotating (REGEL-8 sister path) credits only each slot's measured delta.

    FM-4: the per-slot fresh FlowMeter is seeded at that slot's open read, so a
    lifetime totalizer that reads ~1000 L at open credits only this run's climb
    (1000 -> 1050 = 50 L), never the whole absolute counter — no cross-run baseline
    can leak because each slot measures its own valve-open window.
    """
    z = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_FLOW_SENSOR: "sensor.flow"})
    coord = _coord(monkeypatch, [z])
    coord._live_run_zones = set()
    _totalizer_sensor(
        coord,
        [1000.0, 1010.0, 1020.0, 1030.0, 1040.0, 1050.0, 1060.0, 1070.0],
    )
    await coord._irrigate_zones_rotating([dict(z)])
    # Credited this slot's climb (50 L), NOT the absolute ~1050 counter.
    assert _used(coord) == pytest.approx(50.0)
    assert _bucket(coord) == pytest.approx(0.0)
    assert _log(coord)[0]["result"] == const.RUN_RESULT_COMPLETED
