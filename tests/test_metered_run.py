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


async def test_valve_no_response_faults_no_credit(monkeypatch):
    """An unconfirmed valve faults and credits nothing (unchanged semantics)."""
    coord = _coord(monkeypatch, [_zone()], confirm=False)
    coord._live_run_zones = set()
    await coord._run_valve_metered(_zone(), "switch.v", real_flow=False)
    assert coord.get_zone_fault(1)["reason"] == const.FAULT_VALVE_NO_RESPONSE
    assert _bucket(coord) == pytest.approx(-5.0)  # untouched
    assert _used(coord) == 0.0
    assert _log(coord)[0]["result"] == const.RUN_RESULT_FAILED


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
