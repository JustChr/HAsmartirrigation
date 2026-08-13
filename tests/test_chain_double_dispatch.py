"""Repro: a second dispatch mid-chain re-waters every queued zone (GL #39).

Sequential/rotating chains open one valve at a time, so ``_active_runs`` holds
exactly one zone. ``_drop_zones_already_running`` therefore protects only the
zone whose valve is currently open, and a colliding dispatch starts a second
chain over all the others.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


class _FakeStore:
    def __init__(self, zones, **config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.distributors = {}
        self.config = SimpleNamespace(
            live_estimate_enabled=False,
            log_no_demand=False,
            zone_sequencing_max_consecutive_duration=5,
            zone_sequencing_min_absorption_time=0,
            **config,
        )

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    def get_distributor(self, distributor_id):
        return None

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(
            changes
        )
        return dict(self.zones[int(zone_id)])


def _zone(zone_id):
    return {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: f"Zone {zone_id}",
        const.ZONE_LINKED_ENTITY: f"switch.valve{zone_id}",
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


def _coord(monkeypatch, zones, sequencing):
    for module in ("irrigation", "calculation"):
        monkeypatch.setattr(
            f"custom_components.smart_irrigation.{module}.async_dispatcher_send", Mock()
        )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.services = Mock()
    hass.services.async_call = AsyncMock()
    hass.states = Mock()
    hass.states.get = Mock(return_value=None)

    tasks = []

    def _create_task(coro, *a, **k):
        tasks.append(asyncio.ensure_future(coro))

    hass.async_create_task = Mock(side_effect=_create_task)
    coord.hass = hass
    coord._tasks = tasks
    coord.store = _FakeStore(zones, zone_sequencing=sequencing)
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord.async_master_acquire = AsyncMock()
    coord.async_master_release = AsyncMock()
    coord._dispatch_distributor_cycles = AsyncMock(return_value=False)
    coord._apply_live_durations = AsyncMock(side_effect=lambda z: z)
    coord._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    coord._rain_delay_active = Mock(return_value=False)
    coord.async_update_zone_config = AsyncMock()
    coord._record_run = AsyncMock()
    coord._note_si_valve = Mock()
    coord._live_run_zones = set()
    return coord


def _turn_ons(coord):
    """Ordered list of entity_ids the runner opened."""
    out = []
    for call in coord.hass.services.async_call.await_args_list:
        if len(call.args) >= 2 and call.args[1] == "turn_on":
            out.append(call.args[2]["entity_id"])
    return out


async def _run(monkeypatch, sequencing):
    # irrigation's ``asyncio`` IS the stdlib module, so the patch below is global;
    # keep a real handle for the test's own yields.
    real_sleep = asyncio.sleep
    zones = [_zone(i) for i in range(3)]
    coord = _coord(monkeypatch, zones, sequencing)

    gate = asyncio.Event()
    seen = []

    real_sleep_or_stopped = coord._sleep_or_stopped

    async def _tick(zone_id, seconds):
        seen.append(int(zone_id))
        # Hold the chain open inside its FIRST zone, which is exactly the state a
        # colliding occurrence arrives in.
        if not gate.is_set():
            await gate.wait()
        return await real_sleep_or_stopped(zone_id, seconds)

    coord._sleep_or_stopped = _tick
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )

    assert await coord._irrigate_linked_entities() is True
    while not seen:
        await real_sleep(0)

    # Second dispatch, arriving while zone 0's valve is open.
    await coord._irrigate_linked_entities()

    gate.set()
    for _ in range(200):
        await real_sleep(0)
        if coord._tasks and all(t.done() for t in coord._tasks):
            break
    await asyncio.gather(*coord._tasks)
    return coord


async def test_sequential_second_dispatch_does_not_rewater(monkeypatch):
    coord = await _run(monkeypatch, const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
    opened = _turn_ons(coord)
    assert sorted(opened) == sorted(set(opened)), f"zones opened twice: {opened}"


async def test_rotating_second_dispatch_does_not_rewater(monkeypatch):
    coord = await _run(monkeypatch, const.CONF_ZONE_SEQUENCING_ROTATING)
    opened = _turn_ons(coord)
    assert sorted(opened) == sorted(set(opened)), f"zones opened twice: {opened}"
