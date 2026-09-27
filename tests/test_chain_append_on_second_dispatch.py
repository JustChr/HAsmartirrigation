"""A second dispatch joins a live cycle rather than replacing it.

``async_dispatch_chained_zones`` overwrote ``state.zones`` unconditionally, so a
dispatch arriving mid-cycle destroyed the queue of the cycle already running and
opened a valve next to the one already open — under a sequencing setting whose whole
promise is that it will not. The zones it dropped were never mentioned anywhere.

Two dispatch shapes reach that code and both are ordinary:

- a second schedule, carrying several zones, which is the shape that loses a queue;
- Irrigate-now on ONE zone, which reaches the same place through
  ``async_irrigate_now`` --> ``_dispatch_by_mode``. Its single-zone list used to take
  an early return above the guard, so it opened the second valve without touching the
  queue. Measured on the previous commit: a cycle running zone 1 with ``[2, 3]``
  queued, then a single dispatch of zone 5, gave ``[(1, 600.0), (5, 600.0)]``.

``_drop_zones_already_running`` cannot prevent either: it asks ``zone_run_in_flight``
per zone, which knows nothing about another zone's live cycle.

A note on the fixture, because two tests here depend on it. ``zone_run_in_flight`` is
inert in ``_coord``: ``_self_closing_run_in_flight`` needs
``store.config.<CONF_ACTIVE_VALVE_RUNS>`` to be a real list, and ``_coord`` builds
``store.config`` as a ``Mock``, so the attribute is a ``Mock`` and the isinstance test
fails. Any test that needs a zone to count as watering has to say so itself, the way
the sibling module already does.
"""

from custom_components.irrigation_plus import const

from .test_service_chain import (
    PARALLEL,
    ROTATING,
    SEQUENTIAL,
    _coord,
    _dispatch,
    _finish,
    _register,
    _zone,
)


def _state(c):
    return c._chain_state(const.WATERING_MODE_SERVICE)


class TestASecondDispatchJoinsTheQueue:
    async def test_the_first_cycles_zones_are_kept(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(4), _zone(5))
        await _dispatch(c, zones[:3])
        await _dispatch(c, zones[3:])
        assert _state(c).zones == [2, 3, 4, 5]

    async def test_no_second_valve_is_opened(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(4))
        await _dispatch(c, zones[:2])
        await _dispatch(c, zones[2:])
        assert c._dispatched == [(1, 600.0)]

    async def test_the_joined_zones_are_planned_like_the_first_cycles(self, hass):
        """Joining builds the plan too, or the new zones water a stale duration."""
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3, duration=300))
        await _dispatch(c, zones[:2])
        await _dispatch(c, zones[2:])
        assert _state(c).planned[3].seconds == 300.0

    async def test_a_zone_already_queued_is_not_queued_twice(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones[:3])
        await _dispatch(c, [zones[1], zones[2]])
        assert _state(c).zones == [2, 3]

    async def test_a_zone_already_queued_keeps_the_plan_it_was_queued_with(self, hass):
        """The running cycle decided it first; a later dispatch does not re-price.

        Re-pricing a waiting zone from a second dispatch is its own question, and
        doing it here by accident would re-introduce the defect this series began
        with -- a queued zone watering a duration its own cycle never decided --
        only with the sign flipped.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        await _dispatch(c, [{**z2, const.ZONE_DURATION: 120}])
        assert _state(c).planned[2].seconds == 600.0

    async def test_the_join_names_the_zones_it_added(self, hass, caplog):
        """Naming them, not merely saying "joining".

        The two log branches here both contain that word -- the other one says
        "joining nothing" -- so a substring test on it cannot tell a real join from
        a dispatch that added nothing. A mutant that appended the zones but
        reported none survived exactly that test.
        """
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(4))
        await _dispatch(c, zones[:2])
        caplog.clear()
        await _dispatch(c, zones[2:])
        message = next(
            (
                r.getMessage()
                for r in caplog.records
                if "joining zone(s)" in r.getMessage()
            ),
            None,
        )
        assert message is not None, caplog.text
        assert "3, 4" in message, message
        assert "3 waiting now" in message, message

    async def test_a_dispatch_that_adds_nothing_says_so_instead(self, hass, caplog):
        """The other branch, pinned apart from the one above."""
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones[:3])
        caplog.clear()
        await _dispatch(c, [zones[1], zones[2]])
        assert any(
            "already accounted for" in r.getMessage() for r in caplog.records
        ), caplog.text
        assert not any(
            "joining zone(s)" in r.getMessage() for r in caplog.records
        ), caplog.text

    async def test_the_join_rides_the_first_cycles_master_hold(self, hass):
        """One cycle, one hold. The old overwrite left the second cycle riding a
        token it would lose when the FIRST cycle released it."""
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones[:2])
        token = _state(c).token
        # Counted from here, not from zero: the first dispatch legitimately takes
        # two holds -- the cycle's, and the one async_run_self_closing takes for
        # zone 1's own run. What matters is that joining takes none.
        before = c.async_master_acquire.await_count
        await _dispatch(c, zones[2:])
        assert _state(c).token == token
        assert c.async_master_acquire.await_count == before

    async def test_a_dispatch_onto_the_last_zone_of_a_cycle_still_joins(self, hass):
        """The queue is empty while the last zone waters, so the token decides.

        A cycle dispatches its final zone with nothing left queued. Testing
        liveness by the queue alone would start a second cycle here, under the
        first one's master hold.
        """
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones[:2])
        await _finish(c, 1)
        assert _state(c).zones == [] and _state(c).token is not None
        await _dispatch(c, zones[2:])
        assert c._dispatched == [(1, 600.0), (2, 600.0)]
        assert _state(c).zones == [3]

    async def test_a_queue_without_a_hold_still_counts_as_live(self, hass):
        """The queue half of the liveness test, which the token half hides.

        Built by hand, because the two always travel together today: a cycle takes
        its hold at dispatch and ``_chain_release`` drops queue and token in one
        step, so no reachable state has zones without a token. That makes the
        ``bool(state.zones)`` clause redundant right now -- and unkillable by
        mutation unless something pins it, which is what this does. It stays in the
        code because a queue nobody is holding the master for is the one state where
        replacing it would strand real zones.
        """
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(4))
        await _dispatch(c, zones[:2])
        state = _state(c)
        state.token = None  # drift: a queue with no hold behind it
        await _dispatch(c, zones[2:])
        assert state.zones == [2, 3, 4], "joined, not replaced"

    async def test_a_rotation_without_a_hold_still_counts_as_live(self, hass):
        """The rotation half of the liveness test, hidden the same way.

        ``_chain_take_hold`` sets the token whether or not a master entity exists,
        so a live rotation always has one and the ``state.rotation is not None``
        clause is redundant today -- and survived its mutation for exactly that
        reason, which is how this test came to exist. It stays in the code for the
        same reason the queue clause does: a rotation nobody is holding the master
        for is still a running cycle, and starting a sequential one over it is the
        refusal this change added.
        """
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2))
        state = _state(c)
        state.rotation = object()  # drift: a rotation with no hold and no queue
        state.zones, state.token = [], None
        await _dispatch(c, zones)
        assert state.zones == [], "refused: the rotation was left alone"

    async def test_a_finished_cycle_starts_a_fresh_one(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(4))
        await _dispatch(c, zones[:2])
        await _finish(c, 1)
        await _finish(c, 2)
        assert _state(c).zones == [] and _state(c).token is None
        await _dispatch(c, zones[2:])
        assert _state(c).zones == [4]
        assert c._dispatched == [(1, 600.0), (2, 600.0), (3, 600.0)]


class TestASingleZoneJoinsToo:
    """Irrigate-now on one zone is the commonest form of a second dispatch."""

    async def test_a_single_foreign_zone_joins_instead_of_opening_a_valve(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(5))
        await _dispatch(c, zones[:3])
        await _dispatch(c, [zones[3]], trigger="manual")
        assert c._dispatched == [(1, 600.0)]
        assert _state(c).zones == [2, 3, 5]

    async def test_the_running_zone_is_not_queued_behind_itself(self, hass):
        """Irrigate-now on the zone whose valve is open right now.

        ``zone_run_in_flight`` is the only thing that can tell: the cycle popped
        this zone before dispatching it, so the queue no longer mentions it. The
        fixture cannot answer that question on its own -- see the module docstring
        -- so the test answers it.
        """
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2))
        await _dispatch(c, zones)
        c.zone_run_in_flight = lambda zid: int(zid) == 1
        await _dispatch(c, [zones[0]], trigger="manual")
        assert _state(c).zones == [2]

    async def test_a_single_zone_with_no_live_cycle_dispatches_at_once(self, hass):
        """Unchanged from master: one zone and no cycle is not a chain."""
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1))
        await _dispatch(c, zones, trigger="manual")
        assert c._dispatched == [(1, 600.0)]
        assert _state(c).zones == [] and _state(c).token is None


class TestTheTwoGeometriesDoNotMerge:
    """A rotation prices slots from a total captured at its own start; a
    sequential queue has no slots at all. There is no defined merge, so the live
    cycle is left alone and the refusal is warned about."""

    async def test_a_rotating_dispatch_onto_a_live_sequential_queue_is_refused(
        self, hass, caplog
    ):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones[:2])
        c.store.config.zone_sequencing = ROTATING
        caplog.clear()
        await _dispatch(c, zones[2:])
        assert _state(c).rotation is None, "the live sequential cycle is intact"
        assert _state(c).zones == [2]
        assert any(
            "sequencing changed" in r.getMessage() for r in caplog.records
        ), caplog.text

    async def test_a_sequential_dispatch_onto_a_live_rotation_is_refused(
        self, hass, caplog
    ):
        """The mirror. Refused at the other end of the same fork."""
        c = _coord(hass, ROTATING, slot=5)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(4))
        await _dispatch(c, zones[:2])
        assert _state(c).rotation is not None
        c.store.config.zone_sequencing = SEQUENTIAL
        caplog.clear()
        await _dispatch(c, zones[2:])
        assert _state(c).rotation is not None, "the live rotation is intact"
        assert _state(c).zones == [], "no sequential queue was grafted onto it"
        assert any(
            "sequencing changed" in r.getMessage() for r in caplog.records
        ), caplog.text

    async def test_the_refusal_dispatches_nothing(self, hass):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones[:2])
        c.store.config.zone_sequencing = ROTATING
        await _dispatch(c, zones[2:])
        assert c._dispatched == [(1, 600.0)]


class TestParallelIsUntouched:
    async def test_a_parallel_dispatch_is_not_affected(self, hass):
        """The guard must sit below the parallel return, not above it."""
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3), _zone(4))
        await _dispatch(c, zones[:2])
        c.store.config.zone_sequencing = PARALLEL
        await _dispatch(c, zones[2:])
        assert (3, 600.0) in c._dispatched and (4, 600.0) in c._dispatched

    async def test_a_parallel_dispatch_does_not_create_a_chain(self, hass):
        """The second placement trap, pinned.

        ``_chain_state`` CREATES the Chain. Hoisting that call above the parallel
        return would put the mode into ``_chains()``, and
        ``_chain_advance_for_run`` -- which returns early on ``mode not in
        self._chains()`` -- would start running for parallel-mode runs that today
        return before it.
        """
        c = _coord(hass, PARALLEL)
        zones = _register(c, _zone(1), _zone(2))
        await _dispatch(c, zones)
        assert const.WATERING_MODE_SERVICE not in c._chains()
        assert c._dispatched == [(1, 600.0), (2, 600.0)]
