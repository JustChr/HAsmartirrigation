"""`zone_sequencing` reaches service zones (issue #98).

`_dispatch_by_mode` used to fire every service-mode zone in a single loop. The
hardware owns each close, so nothing serialised them: they opened together
whatever the setting said, and `sequential` and `rotating` were both silently
dropped -- while the setting's own help text promised "Sequential mode waits for
each zone to finish before starting the next" without qualification. Worse than
the batch row of the same issue, where `sequential` is at least what a queue
does anyway: a user who chose `sequential` because their pump can only feed one
zone was getting all of them at once.

They now go through the shared chain in run_chain.py -- the engine OpenSprinkler
stations have used since v2026.07.x, extracted rather than reimplemented. The
OpenSprinkler suite remains the oracle for the engine itself; these tests are
about the service mode reaching it, and about the two chains staying apart.

The pricing in run_window.py mirrors this dispatch, and the mirror is the point:
a track priced as parallel while it runs sequentially anchors a finish-governed
run early. tests/test_run_window.py and tests/test_schedule_time_anchor.py drive
the other side of it.
"""

from unittest.mock import AsyncMock, Mock

from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const

PARALLEL = const.CONF_ZONE_SEQUENCING_PARALLEL
SEQUENTIAL = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
ROTATING = const.CONF_ZONE_SEQUENCING_ROTATING


def _coord(hass, sequencing=SEQUENTIAL, slot=5, absorb=0):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = hass
    c.store = Mock()
    c._cfg = {}
    c._zones = {}
    c.store.async_get_config = AsyncMock(side_effect=lambda: dict(c._cfg))
    c.store.async_update_config = AsyncMock(side_effect=c._cfg.update)
    c.store.async_update_zone = AsyncMock()
    c.store.get_zone = Mock(side_effect=lambda zid: c._zones.get(int(zid)))
    c.store.config = Mock(
        zone_sequencing=sequencing,
        zone_sequencing_max_consecutive_duration=slot,
        zone_sequencing_min_absorption_time=absorb,
        master_entity=None,
    )
    c._record_run = AsyncMock()
    c._set_zone_fault = Mock()
    c._fire_zone_problem = Mock()
    c._note_si_valve = Mock()
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c.async_run_deferred_calculation = AsyncMock()
    c.async_write_watered_bucket = AsyncMock()
    c._stamp_run_finalized = AsyncMock()
    c._timed_volume_l = Mock(return_value=100.0)
    c._credited_depth_native = Mock(return_value=20.0)
    c._flow_calibration_check = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._sc_schedule_cleanup = Mock()
    c._sc_cancel_cleanup = Mock()
    c._os_cancel_watch = Mock()
    async_mock_service(hass, "script", "irrigation")
    c._dispatched = []
    real = c.async_run_self_closing

    async def _spy(zone, **kw):
        c._dispatched.append(
            (int(zone[const.ZONE_ID]), float(zone.get(const.ZONE_DURATION) or 0))
        )
        return await real(zone, **kw)

    c.async_run_self_closing = _spy
    return c


def _zone(zone_id, duration=600):
    """A plain service zone: no confirm_entity, so the hardware owns the close."""
    return {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: f"Zone {zone_id}",
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        const.ZONE_RUN_SERVICE: "script.irrigation",
        const.ZONE_DURATION_FIELD: "dauer",
        const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
        const.ZONE_DURATION: duration,
        const.ZONE_BUCKET: -20.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
    }


def _register(c, *zones):
    for z in zones:
        c._zones[int(z[const.ZONE_ID])] = z
    return list(zones)


async def _dispatch(c, zones, trigger="schedule"):
    await c.async_dispatch_chained_zones(
        zones, mode=const.WATERING_MODE_SERVICE, trigger=trigger
    )


async def _finish(c, zone_id):
    """The hardware closed the valve and the cleanup timer finalised the run."""
    await c._sc_finish_run(zone_id)


def _ids(c):
    return [zid for zid, _ in c._dispatched]


class TestParallelIsUnchanged:
    async def test_every_zone_is_dispatched_at_once(self, hass):
        c = _coord(hass, PARALLEL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))

        await _dispatch(c, zones)

        assert _ids(c) == [1, 2, 3]

    async def test_no_chain_and_no_cycle_hold_is_taken(self, hass):
        """Nothing is held back, so there is nothing for a hold to cover."""
        c = _coord(hass, PARALLEL)
        await _dispatch(c, _register(c, _zone(1), _zone(2)))

        assert not c._chain_state(const.WATERING_MODE_SERVICE).zones
        held = [
            ck.args[0]
            for ck in c.async_master_acquire.await_args_list
            if str(ck.args[0]).startswith("service-chain:")
        ]
        assert held == []


class TestSequentialActuallySerialisesThem:
    async def test_only_the_first_zone_is_dispatched(self, hass):
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2), _zone(3)))

        assert _ids(c) == [1]

    async def test_the_next_starts_when_the_one_before_it_finishes(self, hass):
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2), _zone(3)))

        await _finish(c, 1)
        assert _ids(c) == [1, 2]
        await _finish(c, 2)
        assert _ids(c) == [1, 2, 3]

    async def test_one_master_hold_covers_the_whole_cycle(self, hass):
        """The gaps between runs are part of the cycle.

        A per-run hold would drop the pump in each of them.
        """
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2)))

        taken = [
            ck.args[0]
            for ck in c.async_master_acquire.await_args_list
            if str(ck.args[0]).startswith("service-chain:")
        ]
        assert len(taken) == 1

        await _finish(c, 1)
        await _finish(c, 2)

        released = [
            ck.args[0]
            for ck in c.async_master_release.await_args_list
            if str(ck.args[0]).startswith("service-chain:")
        ]
        assert released == taken

    async def test_a_single_zone_takes_no_chain_at_all(self, hass):
        """The shortcut: with nothing to hold back there is nothing to chain."""
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1)))

        assert _ids(c) == [1]
        assert not c._chain_state(const.WATERING_MODE_SERVICE).zones
        assert c._chain_state(const.WATERING_MODE_SERVICE).token is None

    async def test_a_zone_deleted_mid_cycle_does_not_stall_the_chain(self, hass):
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2), _zone(3)))
        del c._zones[2]

        await _finish(c, 1)

        assert _ids(c) == [1, 3]

    async def test_a_zone_switched_to_another_mode_is_skipped(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones)
        c._zones[2][const.ZONE_WATERING_MODE] = const.WATERING_MODE_CLASSIC

        await _finish(c, 1)

        assert _ids(c) == [1, 3]


class TestRotatingSlicesThem:
    async def test_a_zone_is_dispatched_in_slots(self, hass):
        """Three minutes in one-minute slots is three dispatches, not one."""
        c = _coord(hass, ROTATING, slot=1)
        await _dispatch(c, _register(c, _zone(1, duration=180)))

        assert c._dispatched == [(1, 60)]
        await _finish(c, 1)
        await _finish(c, 1)
        assert c._dispatched == [(1, 60), (1, 60), (1, 60)]

    async def test_two_zones_take_turns(self, hass):
        c = _coord(hass, ROTATING, slot=1)
        await _dispatch(c, _register(c, _zone(1, duration=180), _zone(2, duration=180)))

        for _ in range(5):
            await _finish(c, _ids(c)[-1])

        assert _ids(c) == [1, 2, 1, 2, 1, 2]

    async def test_the_zones_stored_duration_is_left_alone(self, hass):
        """A slot is what THIS run is dispatched for, not a rewrite of the zone.

        The stored duration is what the panel shows and what the next rotation
        would be built from.
        """
        c = _coord(hass, ROTATING, slot=1)
        zones = _register(c, _zone(1, duration=180))
        await _dispatch(c, zones)

        assert zones[0][const.ZONE_DURATION] == 180

    async def test_the_last_slot_is_the_remainder_not_a_full_one(self, hass):
        """Slicing is a delivery schedule, not a discount."""
        c = _coord(hass, ROTATING, slot=1)
        await _dispatch(c, _register(c, _zone(1, duration=150)))

        await _finish(c, 1)
        await _finish(c, 1)

        assert c._dispatched == [(1, 60), (1, 60), (1, 30)]
        assert sum(seconds for _, seconds in c._dispatched) == 150

    async def test_the_rotation_ends_and_gives_its_hold_back(self, hass):
        c = _coord(hass, ROTATING, slot=1)
        await _dispatch(c, _register(c, _zone(1, duration=60)))

        await _finish(c, 1)

        assert c._chain_state(const.WATERING_MODE_SERVICE).rotation is None
        assert [
            ck.args[0]
            for ck in c.async_master_release.await_args_list
            if str(ck.args[0]).startswith("service-chain:")
        ]

    async def test_absorption_holds_a_zone_back_from_its_next_slot(self, hass):
        """With one zone due, interleaving alone gives no soak — the wait does."""
        c = _coord(hass, ROTATING, slot=1, absorb=10)
        await _dispatch(c, _register(c, _zone(1, duration=180)))

        await _finish(c, 1)

        # still absorbing: no second slot yet, and a timer armed instead
        assert c._dispatched == [(1, 60)]
        assert c._chain_state(const.WATERING_MODE_SERVICE).absorb is not None

    async def test_a_zone_still_absorbing_is_passed_over_not_waited_on(self, hass):
        c = _coord(hass, ROTATING, slot=1, absorb=10)
        await _dispatch(c, _register(c, _zone(1, duration=180), _zone(2, duration=180)))

        await _finish(c, 1)

        # zone 1 is absorbing, so zone 2 takes its turn rather than the whole
        # rotation stalling on it
        assert _ids(c) == [1, 2]


class TestAStoppedZoneLeavesTheCycle:
    async def test_its_remaining_slots_are_dropped(self, hass):
        """A stop has to reach the cycle, not only the run in flight.

        What a zone has left lives in memory, so finalising only its run leaves
        the remainder there and the zone the user just stopped comes back round.
        """
        c = _coord(hass, ROTATING, slot=1)
        await _dispatch(c, _register(c, _zone(1, duration=180), _zone(2, duration=180)))

        c._chain_drop_zone(1)
        await _finish(c, 1)
        for _ in range(3):
            await _finish(c, _ids(c)[-1])

        assert _ids(c)[1:] == [2, 2, 2]

    async def test_the_others_keep_their_turns(self, hass):
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2), _zone(3)))

        c._chain_drop_zone(2)
        await _finish(c, 1)

        assert _ids(c) == [1, 3]


class TestTheTwoChainsStayApart:
    """One chain per mode, because the tracks are dispatched concurrently.

    `_dispatch_by_mode` starts the service chain and the station chain without
    awaiting either, so they run alongside each other and the irrigation lasts as
    long as the longer of them. Merging them into one chain would serialise the
    tracks and make every finish-anchored estimate too short — the bug class of
    `4d369eb`, which run_window.py prices around.
    """

    async def test_each_mode_gets_its_own_chain(self, hass):
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2)))

        service = c._chain_state(const.WATERING_MODE_SERVICE)
        station = c._chain_state(const.WATERING_MODE_OPENSPRINKLER)
        assert service is not station
        assert service.zones == [2]
        assert station.zones == []

    async def test_a_station_run_finishing_does_not_advance_the_service_chain(
        self, hass
    ):
        """Keyed on the RUN's mode. Otherwise one track drives the other's queue."""
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2)))

        await c._chain_advance_for_run(
            9, {const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER}
        )

        assert _ids(c) == [1]

    async def test_an_unknown_mode_advances_nothing(self, hass):
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2)))

        await c._chain_advance_for_run(9, {const.RUN_MODE: "something-else"})
        await c._chain_advance_for_run(9, {})

        assert _ids(c) == [1]

    async def test_teardown_drops_every_chain(self, hass):
        c = _coord(hass, ROTATING, slot=1, absorb=10)
        await _dispatch(c, _register(c, _zone(1, duration=180)))
        await _finish(c, 1)
        assert c._chain_state(const.WATERING_MODE_SERVICE).absorb is not None

        c._chain_teardown()

        state = c._chain_state(const.WATERING_MODE_SERVICE)
        assert state.absorb is None
        assert state.rotation is None
        assert state.token is None


class TestTheChainOnlyAdvancesOnceNothingIsInFlight:
    async def test_a_service_run_still_in_flight_holds_the_chain(self, hass):
        """Whichever finalisation fires first advances; the others no-op."""
        c = _coord(hass, SEQUENTIAL)
        await _dispatch(c, _register(c, _zone(1), _zone(2), _zone(3)))

        # zone 1's run is still persisted, so an advance must not start zone 2
        assert await c._sc_find_run(1) is not None
        await c._chain_advance(const.WATERING_MODE_SERVICE, 1)

        assert _ids(c) == [1]

    async def test_the_recorded_run_is_the_slot_not_the_zone_duration(self, hass):
        """Every slot is a run in its own right, with its own log line."""
        c = _coord(hass, ROTATING, slot=1)
        await _dispatch(c, _register(c, _zone(1, duration=120)))

        await _finish(c, 1)
        await _finish(c, 1)

        planned = [ck.kwargs["planned_s"] for ck in c._record_run.await_args_list]
        assert planned == [60, 60]


class TestTheDispatchActuallyRoutesThemThere:
    """The routing itself, not just the chain it routes to.

    Every test above calls ``async_dispatch_chained_zones`` directly, so all of
    them would still pass with ``_dispatch_by_mode`` looping over service zones
    exactly as it used to. This is the seam that changed.
    """

    async def test_dispatch_by_mode_holds_the_second_zone_back(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        c.async_dispatch_opensprinkler_zones = AsyncMock()
        c._dispatch_sequencing = AsyncMock()

        await c._dispatch_by_mode(zones, trigger="schedule")

        assert _ids(c) == [1]
        await _finish(c, 1)
        assert _ids(c) == [1, 2]

    async def test_dispatch_by_mode_still_opens_them_together_under_parallel(
        self, hass
    ):
        c = _coord(hass, PARALLEL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        c.async_dispatch_opensprinkler_zones = AsyncMock()
        c._dispatch_sequencing = AsyncMock()

        await c._dispatch_by_mode(zones, trigger="schedule")

        assert _ids(c) == [1, 2, 3]
