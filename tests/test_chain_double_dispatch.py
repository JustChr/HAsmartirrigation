"""Repro: a second dispatch mid-chain re-waters every queued zone.

Sequential/rotating chains open one valve at a time, so ``_active_runs`` holds
exactly one zone. ``_drop_zones_already_running`` therefore protects only the
zone whose valve is currently open, and a colliding dispatch starts a second
chain over all the others.

The same registry drives the panel, so the tests below also pin the distinction
it now carries: every zone of a chain is in it, but only the one whose valve is
open reads as watering.
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


async def _start_chain(monkeypatch, sequencing):
    """Dispatch a 3-zone chain and return once it is holding inside zone 0.

    Returns ``(coord, gate, real_sleep)``; releasing ``gate`` lets the chain run
    to completion. ``irrigation``'s ``asyncio`` IS the stdlib module, so the
    sleep patch below is global — hence the real handle for the test's own
    yields.
    """
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
    return coord, gate, real_sleep


async def _finish(coord, gate, real_sleep):
    gate.set()
    for _ in range(200):
        await real_sleep(0)
        if coord._tasks and all(t.done() for t in coord._tasks):
            break
    await asyncio.gather(*coord._tasks)


async def _run(monkeypatch, sequencing):
    coord, gate, real_sleep = await _start_chain(monkeypatch, sequencing)

    # Second dispatch, arriving while zone 0's valve is open.
    await coord._irrigate_linked_entities()

    await _finish(coord, gate, real_sleep)
    return coord


async def test_sequential_second_dispatch_does_not_rewater(monkeypatch):
    coord = await _run(monkeypatch, const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
    opened = _turn_ons(coord)
    assert sorted(opened) == sorted(set(opened)), f"zones opened twice: {opened}"


async def test_rotating_second_dispatch_does_not_rewater(monkeypatch):
    coord = await _run(monkeypatch, const.CONF_ZONE_SEQUENCING_ROTATING)
    opened = _turn_ons(coord)
    assert sorted(opened) == sorted(set(opened)), f"zones opened twice: {opened}"


# The panel reads `active_runs` and renders any zone in it as watering. A chain
# claims every zone it will walk, so without the queued flag a seven-zone
# sequential chain shows seven zones watering the moment it starts. Both halves
# matter here: the guard must still see all three zones, AND only the open one
# may read as watering.
async def test_sequential_queued_zones_are_flagged_queued(monkeypatch):
    coord, gate, real_sleep = await _start_chain(
        monkeypatch, const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    )
    runs = coord.get_active_runs()
    assert set(runs) == {"0", "1", "2"}
    assert all(coord.zone_run_in_flight(zid) for zid in range(3))
    assert runs["0"]["queued"] is False, "the open valve must read as watering"
    assert runs["1"]["queued"] is True
    assert runs["2"]["queued"] is True
    await _finish(coord, gate, real_sleep)
    assert coord.get_active_runs() == {}


async def test_rotating_zone_outside_its_slot_is_flagged_queued(monkeypatch):
    coord, gate, real_sleep = await _start_chain(
        monkeypatch, const.CONF_ZONE_SEQUENCING_ROTATING
    )
    runs = coord.get_active_runs()
    assert set(runs) == {"0", "1", "2"}
    assert runs["0"]["queued"] is False
    assert runs["1"]["queued"] is True
    assert runs["2"]["queued"] is True
    await _finish(coord, gate, real_sleep)
    assert coord.get_active_runs() == {}


# A claimed zone defers its calculation. The chain's own teardown picks that up
# for a zone it reaches; a zone it never reaches (a stop, or an exception) has
# no teardown, and before the release ran them the deferral sat pending until
# that zone's next run finalised.
async def test_release_runs_the_calculation_a_claim_deferred(monkeypatch):
    coord = _coord(
        monkeypatch, [_zone(i) for i in range(3)], const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    )
    zones = [coord.store.get_zone(i) for i in range(3)]
    claimed = coord._claim_chain_zones(zones)
    for zid in claimed:
        assert coord.zone_run_in_flight(zid)
        coord.defer_zone_calculation(zid)

    await coord._release_chain_zones(claimed)

    assert coord.get_active_runs() == {}
    calculated = sorted(
        call.kwargs["zone_id"]
        for call in coord.async_update_zone_config.await_args_list
    )
    assert calculated == [0, 1, 2]
    assert not coord._deferred_calc_zones


async def test_release_without_a_deferral_calculates_nothing(monkeypatch):
    coord = _coord(
        monkeypatch, [_zone(i) for i in range(2)], const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    )
    claimed = coord._claim_chain_zones([coord.store.get_zone(i) for i in range(2)])
    await coord._release_chain_zones(claimed)
    coord.async_update_zone_config.assert_not_awaited()
