"""Tests for WS-2: run history, run-log and the cumulative water-usage total.

Every completed run appends a bounded run-log entry and adds the delivered
volume to a monotonic ``water_used_total`` counter (litres) that backs the
``total_increasing`` usage sensor. Failed/skipped runs are logged too but never
add water. The total + log live in the store so they survive a restart.

Coordinator tests build the coordinator with ``__new__`` (like
test_valve_verification) so only the touched attributes are wired up.
"""

from unittest.mock import Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.store import SmartIrrigationStorage


class _FakeStore:
    """Minimal in-memory store exposing the methods the runner calls."""

    def __init__(self, zones=None):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(
            changes
        )
        return dict(self.zones[int(zone_id)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]


def _coord(monkeypatch, zones=None, units=METRIC_SYSTEM):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = units
    coord.hass = hass
    coord.store = _FakeStore(zones)
    return coord


# --------------------------------------------------------------------------- #
# _record_run: append + usage total
# --------------------------------------------------------------------------- #
async def test_record_run_appends_and_increments_total(monkeypatch):
    coord = _coord(
        monkeypatch,
        [{const.ZONE_ID: 1, const.ZONE_WATER_USED_TOTAL: 5.0, const.ZONE_RUN_LOG: []}],
    )
    await coord._record_run(
        1,
        result=const.RUN_RESULT_COMPLETED,
        volume_l=10.0,
        planned_s=60,
        actual_s=60,
        detail="why",
    )
    z = coord.store.zones[1]
    assert z[const.ZONE_WATER_USED_TOTAL] == pytest.approx(15.0)
    assert len(z[const.ZONE_RUN_LOG]) == 1
    entry = z[const.ZONE_RUN_LOG][0]
    assert entry["result"] == const.RUN_RESULT_COMPLETED
    assert entry["volume_l"] == pytest.approx(10.0)
    assert entry["planned_s"] == 60
    assert entry["detail"] == "why"
    assert "ts" in entry


async def test_failed_run_logs_but_does_not_add_water(monkeypatch):
    coord = _coord(
        monkeypatch,
        [{const.ZONE_ID: 1, const.ZONE_WATER_USED_TOTAL: 7.0, const.ZONE_RUN_LOG: []}],
    )
    await coord._record_run(
        1, result=const.RUN_RESULT_FAILED, detail=const.FAULT_VALVE_NO_RESPONSE
    )
    z = coord.store.zones[1]
    assert z[const.ZONE_WATER_USED_TOTAL] == pytest.approx(7.0)  # unchanged
    assert z[const.ZONE_RUN_LOG][0]["result"] == const.RUN_RESULT_FAILED
    assert z[const.ZONE_RUN_LOG][0]["volume_l"] == 0.0


async def test_run_log_is_newest_first_capped_and_total_monotonic(monkeypatch):
    coord = _coord(monkeypatch, [{const.ZONE_ID: 1}])
    n = const.RUN_LOG_MAX_ENTRIES + 5
    for i in range(n):
        await coord._record_run(
            1, result=const.RUN_RESULT_COMPLETED, volume_l=1.0, detail=str(i)
        )
    z = coord.store.zones[1]
    log = z[const.ZONE_RUN_LOG]
    # Capped at the max, newest entry first.
    assert len(log) == const.RUN_LOG_MAX_ENTRIES
    assert log[0]["detail"] == str(n - 1)
    # Every run counted toward the total even though older log rows were dropped.
    assert z[const.ZONE_WATER_USED_TOTAL] == pytest.approx(float(n))


# --------------------------------------------------------------------------- #
# Reset usage (per-zone "reset usage" button)
# --------------------------------------------------------------------------- #
async def test_reset_water_usage_clears_total_and_log(monkeypatch):
    coord = _coord(
        monkeypatch,
        [
            {
                const.ZONE_ID: 1,
                const.ZONE_WATER_USED_TOTAL: 10_521_286.1,
                const.ZONE_RUN_LOG: [{"ts": "t", "result": const.RUN_RESULT_COMPLETED}],
            }
        ],
    )
    await coord.async_reset_water_usage(1)
    z = coord.store.zones[1]
    assert z[const.ZONE_WATER_USED_TOTAL] == 0.0
    assert z[const.ZONE_RUN_LOG] == []


async def test_reset_water_usage_unknown_zone_is_noop(monkeypatch):
    coord = _coord(monkeypatch, [{const.ZONE_ID: 1}])
    # Should not raise for a missing zone.
    await coord.async_reset_water_usage(99)
    assert 99 not in coord.store.zones


# --------------------------------------------------------------------------- #
# Volume helpers
# --------------------------------------------------------------------------- #
def test_timed_volume_metric(monkeypatch):
    coord = _coord(monkeypatch)
    zone = {const.ZONE_THROUGHPUT: 12.0}  # 12 L/min
    assert coord._timed_volume_l(zone, 120) == pytest.approx(24.0)  # 2 min
    assert coord._timed_volume_l(zone, 0) == 0.0


def test_timed_volume_imperial_converts_gpm(monkeypatch):
    coord = _coord(monkeypatch, units=US_CUSTOMARY_SYSTEM)
    zone = {const.ZONE_THROUGHPUT: 1.0}  # 1 gal/min -> ~3.785 L/min
    assert coord._timed_volume_l(zone, 60) == pytest.approx(3.785411784, rel=1e-6)


# --------------------------------------------------------------------------- #
# Completed timed run records a log entry with delivered volume
# --------------------------------------------------------------------------- #
async def test_sequential_completed_run_records_history(monkeypatch):
    from unittest.mock import AsyncMock

    monkeypatch.setattr(const, "VALVE_CONFIRM_TIMEOUT", 0)
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord = _coord(monkeypatch)
    coord.hass.services.async_call = AsyncMock()
    coord.hass.states.get = lambda eid: Mock(state="on", attributes={})
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Garden",
        const.ZONE_LINKED_ENTITY: "switch.v",
        const.ZONE_FLOW_SENSOR: None,
        const.ZONE_DURATION: 60,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_IRRIGATION_TARGET_BUCKET: 0.0,
        const.ZONE_EXPLANATION: "needed 6 mm",
    }
    coord.store.zones[1] = dict(zone)

    await coord._irrigate_zones_sequential([zone])

    log = coord.store.zones[1][const.ZONE_RUN_LOG]
    assert log[0]["result"] == const.RUN_RESULT_COMPLETED
    assert log[0]["volume_l"] == pytest.approx(10.0)  # 1 min * 10 L/min
    assert log[0]["detail"] == "needed 6 mm"
    assert coord.store.zones[1][const.ZONE_WATER_USED_TOTAL] == pytest.approx(10.0)


# --------------------------------------------------------------------------- #
# Skip logging
# --------------------------------------------------------------------------- #
async def test_record_skipped_logs_enabled_zones_only(monkeypatch):
    coord = _coord(
        monkeypatch,
        [
            {const.ZONE_ID: 1, const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC},
            {const.ZONE_ID: 2, const.ZONE_STATE: const.ZONE_STATE_DISABLED},
        ],
    )
    await coord._record_skipped_run("all", "precipitation")
    assert coord.store.zones[1][const.ZONE_RUN_LOG][0]["result"] == (
        const.RUN_RESULT_SKIPPED
    )
    assert coord.store.zones[1][const.ZONE_RUN_LOG][0]["detail"] == "precipitation"
    # Disabled zone was not logged.
    assert const.ZONE_RUN_LOG not in coord.store.zones[2]


async def test_record_skipped_respects_target_zone_subset(monkeypatch):
    coord = _coord(
        monkeypatch,
        [
            {const.ZONE_ID: 1, const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC},
            {const.ZONE_ID: 2, const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC},
        ],
    )
    await coord._record_skipped_run([2], None)
    assert const.ZONE_RUN_LOG not in coord.store.zones[1]
    assert coord.store.zones[2][const.ZONE_RUN_LOG][0]["result"] == (
        const.RUN_RESULT_SKIPPED
    )


# --------------------------------------------------------------------------- #
# Persistence: the total + log survive a restart (store roundtrip)
# --------------------------------------------------------------------------- #
async def test_usage_total_and_run_log_survive_restart(hass):
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    created = await store.async_create_zone(
        {const.ZONE_NAME: "Garden", const.ZONE_SIZE: 100.0}
    )
    zid = created["id"]
    await store.async_update_zone(
        zid,
        {
            const.ZONE_WATER_USED_TOTAL: 42.5,
            const.ZONE_RUN_LOG: [{"ts": "t", "result": const.RUN_RESULT_COMPLETED}],
        },
    )
    data = store._data_to_save()

    # Simulate a restart: a fresh storage loading the persisted blob.
    store2 = SmartIrrigationStorage(hass)
    store2._store.async_load = _async_returning(data)
    await store2.async_load()

    z = store2.get_zone(zid)
    assert z[const.ZONE_WATER_USED_TOTAL] == pytest.approx(42.5)
    assert z[const.ZONE_RUN_LOG][0]["result"] == const.RUN_RESULT_COMPLETED


async def test_pre_ws2_zone_defaults_usage_fields(hass):
    """A zone persisted before WS-2 (no usage fields) loads with safe defaults."""
    store = SmartIrrigationStorage(hass)
    legacy = {
        "config": {},
        "zones": [
            {
                const.ZONE_ID: 0,
                const.ZONE_NAME: "Old",
                const.ZONE_SIZE: 50.0,
                const.ZONE_THROUGHPUT: 10.0,
                const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
                const.ZONE_DELTA: 0,
                const.ZONE_BUCKET: 0,
                const.ZONE_DURATION: 0,
                const.ZONE_MODULE: 1,
                const.ZONE_MULTIPLIER: 1,
                const.ZONE_MAPPING: 0,
                const.ZONE_LEAD_TIME: 0,
            }
        ],
    }
    store._store.async_load = _async_returning(legacy)
    await store.async_load()
    z = store.get_zone(0)
    assert z[const.ZONE_WATER_USED_TOTAL] == 0.0
    assert z[const.ZONE_RUN_LOG] == []


def _async_returning(value):
    async def _f(*args, **kwargs):
        return value

    return _f
