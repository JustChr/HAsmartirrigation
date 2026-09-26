"""The sequential chain delivers the run its cycle planned (Eifel-Joe#2).

``Chain.zones`` holds bare ids and ``_chain_advance`` re-reads the stored zone, so
everything the dispatching cycle decided about a queued zone — the live duration and
the live-estimate marker — used to be dropped between the two. A sibling
``Chain.planned`` now carries it, mirroring how ``Rotation.remaining`` already carries
the rotating half's own plan.

The fixtures come from test_service_chain.py, whose ``_coord`` spy records
``(zone_id, duration)`` for every dispatch.
"""

from custom_components.irrigation_plus import const

from .test_service_chain import (
    ROTATING,
    SEQUENTIAL,
    _coord,
    _dispatch,
    _finish,
    _register,
    _zone,
)


def _live(zone, duration):
    """What irrigation._apply_live_durations hands the dispatcher: a COPY.

    It hands the copy and nothing else, so a test that re-sizes a zone must also
    put the id into ``_live_run_zones`` itself. Those two go together in
    production and cannot come apart: ``_apply_live_durations`` appends the copy
    and adds the id on the same branch, the one ``decision.resized`` selects
    (``irrigation.py``), and a zone it does not re-size is passed through
    untouched. A copy without the marker is therefore not a state the integration
    can reach, and since the plan overlay is gated on the marker, a test built
    that way would assert against a fiction.
    """
    return {**zone, const.ZONE_DURATION: duration}


def _refuse(c, zone_id):
    """Make this one zone's dispatch return False, as a station refusal would."""
    spy = c.async_run_self_closing

    async def _maybe(zone, **kw):
        if int(zone[const.ZONE_ID]) == int(zone_id):
            return False
        return await spy(zone, **kw)

    c.async_run_self_closing = _maybe


def _ceiling_seen(c):
    """Record the ceiling _run_ceiling grants each dispatch, in order.

    _run_ceiling consumes the live marker as it answers, so asking it afterwards
    answers the wrong question; the only honest place to observe it is at
    dispatch time.
    """
    seen = []
    real = c._run_ceiling

    def _spy(zone, *args, **kwargs):
        value = real(zone, *args, **kwargs)
        seen.append((int(zone[const.ZONE_ID]), value))
        return value

    c._run_ceiling = _spy
    return seen


def _abandon_message(caplog):
    """The one line _chain_forfeit_queue writes, or raise if it wrote none."""
    return next(
        r.getMessage() for r in caplog.records if "abandoning" in r.getMessage()
    )


class TestTheQueueRemembersWhatTheCycleDecided:
    async def test_a_queued_zone_waters_the_live_duration_not_the_stored_one(
        self, hass
    ):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        await _finish(c, 1)
        assert c._dispatched == [(1, 300.0), (2, 300.0)]

    async def test_a_zone_stored_at_zero_still_waters_its_live_duration(self, hass):
        """The severe case: the daily calc said 0, the live estimate said 300.

        Reachable because the live gate drops the stored-duration pre-filter in
        ``_irrigate_linked_entities``' selection, so "stored 0, live 300" is an
        ordinary state. Before the plan existed, the re-read saw 0 and the zone
        was skipped in silence.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=0))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 600), _live(z2, 300)])
        await _finish(c, 1)
        assert c._dispatched == [(1, 600.0), (2, 300.0)]

    async def test_the_plan_records_whether_the_cycle_sized_the_zone_live(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2, z3 = _register(
            c, _zone(1, duration=600), _zone(2, duration=600), _zone(3, duration=600)
        )
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300), z3])
        planned = c._chain_state(const.WATERING_MODE_SERVICE).planned
        assert planned[2].live is True
        assert planned[3].live is False

    async def test_a_zone_with_no_plan_falls_back_to_the_stored_duration(self, hass):
        """Drift must degrade to today's behaviour, never to a dropped zone.

        Not reachable today — ``async_dispatch_chained_zones`` always builds
        ``planned`` and ``zones`` together — so the drift is built by hand here
        on purpose, as a safety net against a future edit that could separate
        them.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        state = c._chain_state(const.WATERING_MODE_SERVICE)
        state.planned.clear()  # simulate the two structures drifting apart
        await _finish(c, 1)
        assert c._dispatched == [(1, 600.0), (2, 600.0)]

    async def test_a_partial_plan_only_decides_the_zone_that_has_one(self, hass):
        """Partial drift is the realistic form: one entry goes, the others stay."""
        c = _coord(hass, SEQUENTIAL)
        z1, z2, z3 = _register(
            c, _zone(1, duration=600), _zone(2, duration=600), _zone(3, duration=600)
        )
        c._live_run_zones = {1, 2, 3}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300), _live(z3, 300)])
        c._chain_state(const.WATERING_MODE_SERVICE).planned.pop(3)
        await _finish(c, 1)
        await _finish(c, 2)
        assert c._dispatched == [(1, 300.0), (2, 300.0), (3, 600.0)]

    async def test_a_live_sized_queued_zone_keeps_its_plan_against_the_store(
        self, hass
    ):
        """A calculation landing mid-chain cannot shorten or delete a LIVE run.

        The live estimate made a decision that exists nowhere else, so the plan
        outranks whatever the store says by the time the turn comes -- here the
        severest form of it, a store rewritten to 0.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        c._zones[2] = {**c._zones[2], const.ZONE_DURATION: 0}
        await _finish(c, 1)
        assert c._dispatched == [(1, 300.0), (2, 300.0)]

    async def test_a_non_live_queued_zone_follows_a_shortened_store(self, hass):
        """Without the live estimate the store re-read is not a lost decision.

        It is the daily calculation re-pricing the zone at its turn, which is
        master's behaviour and stays master's behaviour: a mid-chain calculation
        can realistically only move a stored duration DOWN, so a zone rewritten
        while it waited is a zone that got rained on. Freezing it would water
        against a cycle-start bucket while ``pre_bucket`` is the fresh one.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        c._zones[2] = {**c._zones[2], const.ZONE_DURATION: 120}
        await _finish(c, 1)
        assert c._dispatched == [(1, 600.0), (2, 120.0)]

    async def test_a_non_live_zone_the_store_zeroed_is_dropped(self, hass):
        """Following the store includes following it to zero: the zone is dropped.

        Master dropped such a zone too, and silently. It is named now --
        ``TestEveryDropIsNarrated.test_a_zone_dropped_for_zero_duration_says_so``
        owns that wording, so this one only pins that the frozen 600 does not
        water.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        c._zones[2] = {**c._zones[2], const.ZONE_DURATION: 0}
        await _finish(c, 1)
        assert c._dispatched == [(1, 600.0)]


class TestThePlanIsDroppedWithTheQueue:
    async def test_stopping_a_queued_zone_drops_its_plan_too(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        c._chain_drop_zone(2)
        state = c._chain_state(const.WATERING_MODE_SERVICE)
        assert state.zones == []
        assert state.planned == {}

    async def test_releasing_the_chain_clears_the_plan(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        await c._chain_release(const.WATERING_MODE_SERVICE)
        assert c._chain_state(const.WATERING_MODE_SERVICE).planned == {}

    async def test_teardown_clears_the_plan(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        c._chain_teardown()
        assert c._chain_state(const.WATERING_MODE_SERVICE).planned == {}

    async def test_starting_a_rotation_clears_a_sequential_plan(self, hass):
        """The two geometries are exclusive; a leftover plan must not survive."""
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        await c._chain_start_rotation(
            [c._zones[1], c._zones[2]],
            mode=const.WATERING_MODE_SERVICE,
            trigger="schedule",
        )
        assert c._chain_state(const.WATERING_MODE_SERVICE).planned == {}


class TestTheLiveMarkerSurvivesTheQueue:
    async def test_a_queued_live_zone_keeps_its_ceiling_allowance(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        ceilings = _ceiling_seen(c)
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        c._live_run_zones = set()  # a second scheduled pass rebinds the set
        await _finish(c, 1)
        # 50.0 is _zone()'s ZONE_MAXIMUM_BUCKET: the live allowance, not the
        # max(target, pre_bucket) an ordinary run would be clamped to.
        assert ceilings == [(1, 50.0), (2, 50.0)]

    async def test_a_zone_the_cycle_did_not_mark_is_not_marked_later(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = set()
        ceilings = _ceiling_seen(c)
        await _dispatch(c, [z1, z2])
        await _finish(c, 1)
        # Asserting the ceiling, not the empty set, is what gives this test its
        # power — a marker wrongly re-armed here would be consumed by its own
        # dispatch and leave the set empty either way. 0.0 is the ordinary clamp
        # max(target 0.0, pre_bucket -20.0); 50.0 would be the live allowance.
        assert ceilings == [(1, 0.0), (2, 0.0)]
        assert c._live_run_zones == set()


class TestADroppedZoneHandsBackWhatItHolds:
    async def test_a_zone_dropped_for_a_mode_change_releases_its_marker(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        # The user moves zone 2 to another watering mode while it waits.
        c._zones[2] = {
            **c._zones[2],
            const.ZONE_WATERING_MODE: const.WATERING_MODE_OPENSPRINKLER,
        }
        await _finish(c, 1)
        assert c._dispatched == [(1, 300.0)]
        # No leftover allowance for the next run of zone 2.
        assert 2 not in c._live_run_zones

    async def test_a_zone_dropped_for_a_zero_duration_releases_its_marker(self, hass):
        """A plan of zero is not reachable from _apply_live_durations today —
        _zone_run_decision's own zero-duration guard returns None before it —
        so the state is built by hand to exercise the branch the guard protects.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 0)])
        await _finish(c, 1)
        assert c._dispatched == [(1, 300.0)]
        assert 2 not in c._live_run_zones

    async def test_a_zone_taken_over_while_it_waited_releases_its_marker(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        # Something else is watering zone 2 by the time its turn comes.
        c.zone_run_in_flight = lambda zid: int(zid) == 2
        await _finish(c, 1)
        assert c._dispatched == [(1, 300.0)]
        assert 2 not in c._live_run_zones

    async def test_a_refused_zone_releases_the_marker_it_was_just_given(self, hass):
        """The refusal path is the one that MUST drop: _mark_live_run armed the
        zone immediately before the dispatch, and nothing consumed it.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2, z3 = _register(
            c, _zone(1, duration=600), _zone(2, duration=600), _zone(3, duration=600)
        )
        c._live_run_zones = {1, 2, 3}
        _refuse(c, 2)
        await _dispatch(c, [_live(z1, 300), _live(z2, 300), _live(z3, 300)])
        await _finish(c, 1)
        assert c._dispatched == [(1, 300.0), (3, 300.0)]
        assert 2 not in c._live_run_zones

    async def test_the_cycles_first_zone_hands_its_marker_back_when_refused(self, hass):
        """async_run_self_closing only self-cleans on its confirm-false path, so
        a head zone refused for an unresolvable station or a zero window keeps
        its allowance unless the dispatcher takes it back. Every zone behind it
        already gets this from _chain_advance.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        _refuse(c, 1)
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        assert 1 not in c._live_run_zones

    async def test_stopping_a_queued_zone_releases_its_marker(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        c._chain_drop_zone(2)
        assert 2 not in c._live_run_zones

    async def test_stopping_a_zone_no_chain_queued_leaves_its_marker_alone(self, hass):
        """This method runs for every stop, including classic zones no chain
        ever queued. Their marker belongs to a run that is still finishing and
        is not ours to take.

        Zone 1 — the dispatched head — is not a usable stand-in here: its own
        marker is consumed by _run_ceiling at dispatch, the same instant this
        cycle starts (see TestTheLiveMarkerSurvivesTheQueue), so by the time
        _chain_drop_zone runs there is nothing left to prove the gate did the
        protecting. Zone 3 is never part of this dispatch at all — no chain's
        state.zones or rotation.remaining ever names it — so its marker can
        only survive because _chain_drop_zone found it unheld.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {2, 3}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        c._chain_drop_zone(3)
        assert 3 in c._live_run_zones


class TestEveryDropIsNarrated:
    async def test_a_zone_dropped_for_its_mode_says_so(self, hass, caplog):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        c._zones[2] = {
            **c._zones[2],
            const.ZONE_WATERING_MODE: const.WATERING_MODE_OPENSPRINKLER,
        }
        caplog.clear()
        await _finish(c, 1)
        assert any(
            "dropping zone 2 from the cycle" in r.getMessage()
            and "watering mode" in r.getMessage()
            for r in caplog.records
        ), caplog.text

    async def test_a_zone_dropped_for_zero_duration_says_so(self, hass, caplog):
        """Reached through the store, because a live plan of 0 does not exist.

        ``_zone_run_decision`` returns None at ``live <= 0``, so a zone the
        estimate prices at nothing never enters the queue at all and cannot be
        dropped out of it later. The reachable route is the other one: a zone
        queued at a real duration whose stored duration is rewritten to 0 while it
        waits, which after the live gating is what the advance actually reads.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        c._zones[2] = {**c._zones[2], const.ZONE_DURATION: 0}
        caplog.clear()
        await _finish(c, 1)
        assert any(
            "dropping zone 2 from the cycle" in r.getMessage()
            and "nothing left to water" in r.getMessage()
            for r in caplog.records
        ), caplog.text

    async def test_a_zone_taken_over_says_so(self, hass, caplog):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        c.zone_run_in_flight = lambda zid: int(zid) == 2
        caplog.clear()
        await _finish(c, 1)
        assert any(
            "dropping zone 2 from the cycle" in r.getMessage()
            and "took it over" in r.getMessage()
            for r in caplog.records
        ), caplog.text

    async def test_a_refused_zone_says_so_as_a_warning(self, hass, caplog):
        c = _coord(hass, SEQUENTIAL)
        z1, z2, z3 = _register(
            c, _zone(1, duration=600), _zone(2, duration=600), _zone(3, duration=600)
        )
        _refuse(c, 2)
        await _dispatch(c, [z1, z2, z3])
        caplog.clear()
        await _finish(c, 1)
        refusals = [
            r for r in caplog.records if "zone 2 refused its dispatch" in r.getMessage()
        ]
        assert refusals, caplog.text
        # A refusal is the one outcome here that is not an ordinary consequence
        # of the configuration moving under a running cycle.
        assert refusals[0].levelname == "WARNING"
        # and the cycle carries on rather than stopping at it
        assert c._dispatched == [(1, 600.0), (3, 600.0)]

    async def test_the_cycles_first_zone_says_so_when_it_refuses(self, hass, caplog):
        """The head zone is dispatched by async_dispatch_chained_zones, not by
        the advance loop, so it needs its own line — otherwise the one refusal
        cause that has no other signal anywhere is invisible for zone 1.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        _refuse(c, 1)
        caplog.clear()
        await _dispatch(c, [z1, z2])
        refusals = [
            r for r in caplog.records if "zone 1 refused its dispatch" in r.getMessage()
        ]
        assert refusals, caplog.text
        assert refusals[0].levelname == "WARNING"
        # and the cycle moves on to zone 2 rather than stalling
        assert c._dispatched == [(2, 600.0)]


class TestTheRotationNarratesItsWriteOffs:
    async def test_a_rotating_zone_whose_mode_changed_says_so(self, hass, caplog):
        c = _coord(hass, ROTATING, slot=5, absorb=0)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [z1, z2])
        c._zones[2] = {
            **c._zones[2],
            const.ZONE_WATERING_MODE: const.WATERING_MODE_OPENSPRINKLER,
        }
        caplog.clear()
        await _finish(c, 1)
        assert any(
            "writing off zone 2 and its remaining" in r.getMessage()
            and "watering mode" in r.getMessage()
            for r in caplog.records
        ), caplog.text
        assert 2 not in c._live_run_zones

    async def test_a_rotating_zone_taken_over_says_which_reason_fired(
        self, hass, caplog
    ):
        """The two reasons were one merged condition, so the log could not name
        which of them applied. They read identically to whoever is debugging.
        """
        c = _coord(hass, ROTATING, slot=5, absorb=0)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [z1, z2])
        c.zone_run_in_flight = lambda zid: int(zid) == 2
        caplog.clear()
        await _finish(c, 1)
        messages = [
            r.getMessage()
            for r in caplog.records
            if "writing off zone 2 and its remaining" in r.getMessage()
        ]
        assert any("took it over" in m for m in messages), messages
        assert not any("watering mode" in m for m in messages), messages
        assert 2 not in c._live_run_zones

    async def test_a_refused_rotating_zone_says_how_much_it_lost(self, hass, caplog):
        """900s zone, 300s slot: the two numbers differ on purpose, so the
        assertion can tell them apart. The zone loses both — the refused slot
        delivered nothing and the remainder is abandoned — and a warning-only
        log view shows this line and not the slot line above it.
        """
        c = _coord(hass, ROTATING, slot=5, absorb=0)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=900))
        c._live_run_zones = {1, 2}
        _refuse(c, 2)
        await _dispatch(c, [z1, z2])
        caplog.clear()
        await _finish(c, 1)
        refusals = [r for r in caplog.records if "zone 2 refused its" in r.getMessage()]
        assert refusals, caplog.text
        assert refusals[0].levelname == "WARNING"
        message = refusals[0].getMessage()
        # Verified empirically against the real code path, not assumed: the
        # first slot is min(300s, 900s) = 300s, and rotation.remaining[2] is
        # already decremented to 600s by the time this refusal fires.
        assert "300s slot" in message, message
        assert "remaining 600s" in message, message
        assert 2 not in c._live_run_zones


class TestAnAbandonedQueueIsReported:
    async def test_teardown_names_the_zones_it_abandons(self, hass, caplog):
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        c._live_run_zones = {1, 2, 3}
        await _dispatch(c, zones)
        caplog.clear()
        c._chain_teardown()
        message = _abandon_message(caplog)
        # Zone 1 was dispatched, not queued -- the rest of ITS cycle is
        # nothing, and it must not be named. Ids render as a bare comma list
        # ("zones 2, 3"), so neither "1" nor "zone 1" (singular) is a safe
        # check: both would still pass against a buggy "zones 1, 2, 3", since
        # that reads "zones 1..." not "zone 1...". Anchoring the exact
        # rendered list, both ends at once, is what actually proves zone 1's
        # absence as well as the right ids being present.
        assert "cycle for zones 2, 3 —" in message, caplog.text
        # and the allowances go back with them
        assert c._live_run_zones == set()

    async def test_teardown_of_an_idle_chain_says_nothing(self, hass, caplog):
        """Unload runs for every install, cycle or no cycle."""
        c = _coord(hass, SEQUENTIAL)
        _register(c, _zone(1))
        c._chain_state(const.WATERING_MODE_SERVICE)  # exists but never dispatched
        caplog.clear()
        c._chain_teardown()
        assert caplog.records == [], caplog.text

    async def test_a_release_that_abandons_a_queue_reports_it(self, hass, caplog):
        """The engine is shared with OpenSprinkler's own abort, which is pinned
        to the station mode -- the very reason the service chain has no abort
        path of its own to reach this from (see the commit this test belongs
        to). This pins the same behaviour on the service fixture instead, the
        only route left that ever exercises it.
        """
        c = _coord(hass, SEQUENTIAL)
        zones = _register(c, _zone(1), _zone(2), _zone(3))
        await _dispatch(c, zones)
        caplog.clear()
        await c._chain_release(const.WATERING_MODE_SERVICE)
        message = _abandon_message(caplog)
        assert "cycle for zones 2, 3 —" in message, caplog.text

    async def test_a_release_at_the_end_of_a_cycle_says_nothing(self, hass, caplog):
        """The ordinary path: the loop drained the queue before releasing."""
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1), _zone(2))
        await _dispatch(c, [z1, z2])
        await _finish(c, 1)
        caplog.clear()
        await _finish(c, 2)  # drains the queue, then releases
        assert not any(
            "abandoning" in r.getMessage() for r in caplog.records
        ), caplog.text

    async def test_a_rotating_cycle_names_the_zones_it_gives_up(self, hass, caplog):
        c = _coord(hass, ROTATING, slot=5, absorb=0)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [z1, z2])
        caplog.clear()
        c._chain_teardown()
        message = _abandon_message(caplog)
        # Zone 1 is mid-slot, not queued -- and belongs here anyway: its
        # remaining rotation credit is exactly as abandoned as zone 2's, which
        # never got a slot at all. The seconds are not repeated here; the
        # per-slot write-off already carries them.
        assert "cycle for zones 1, 2 —" in message, caplog.text
        assert c._live_run_zones == set()


class TestAZoneWateredWhileQueuedIsNotWateredAgain:
    async def test_a_manual_run_on_a_queued_zone_takes_it_out_of_the_cycle(
        self, hass, caplog
    ):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        # Irrigate-now on a zone that is merely QUEUED: both guards ask
        # zone_run_in_flight, which cannot see a queued zone, so it is accepted
        # and the valve opens next to zone 1's.
        await c.async_run_self_closing(z2, trigger="manual")
        assert c._dispatched == [(1, 600.0), (2, 600.0)]
        caplog.clear()
        await _finish(c, 2)
        await _finish(c, 1)
        # THE FIX: watered once by the manual run, not a second time by the chain.
        assert c._dispatched == [(1, 600.0), (2, 600.0)]
        assert any(
            "taking zone 2 out of the cycle" in r.getMessage()
            and "already watered" in r.getMessage()
            for r in caplog.records
        ), caplog.text

    async def test_the_cycles_own_zone_still_advances_normally(self, hass):
        """The zone the chain dispatched is already popped, so nothing changes."""
        c = _coord(hass, SEQUENTIAL)
        z1, z2, z3 = _register(
            c, _zone(1, duration=600), _zone(2, duration=600), _zone(3, duration=600)
        )
        await _dispatch(c, [z1, z2, z3])
        await _finish(c, 1)
        await _finish(c, 2)
        assert c._dispatched == [(1, 600.0), (2, 600.0), (3, 600.0)]

    async def test_a_rotating_cycle_is_untouched(self, hass):
        """A rotation keeps state.zones empty, so this fix cannot reach it.

        That is right for the rotation's OWN turns — they legitimately recur,
        so nothing here should write one off. It says nothing about a rotating
        zone taken over by something else (e.g. Irrigate-now) between its own
        turns: that case is left untouched because it is a separate, unfixed
        defect, not because it was considered and ruled safe.
        """
        c = _coord(hass, ROTATING, slot=5, absorb=0)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        before = dict(c._chain_state(const.WATERING_MODE_SERVICE).rotation.remaining)
        await _finish(c, 1)
        after = c._chain_state(const.WATERING_MODE_SERVICE).rotation.remaining
        assert set(before) == set(after), "no zone was written off by the drop"

    async def test_a_rotating_cycles_ordinary_turn_is_not_reported_as_a_takeover(
        self, hass, caplog
    ):
        """Guards the early return itself: without it, ``_chain_forget_finished``
        runs unconditionally and — because it does not know rotation never
        populates ``state.zones`` — logs zone 2's perfectly ordinary next slot
        as though something else had already watered it.
        """
        c = _coord(hass, ROTATING, slot=5, absorb=0)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [z1, z2])
        caplog.clear()
        await _finish(c, 1)
        assert not any(
            "already watered" in r.getMessage() for r in caplog.records
        ), caplog.text

    async def test_the_zone_also_loses_its_plan_and_its_marker(self, hass):
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        c._live_run_zones = {1, 2}
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        await c.async_run_self_closing(z2, trigger="manual")
        await _finish(c, 2)
        state = c._chain_state(const.WATERING_MODE_SERVICE)
        assert state.zones == []
        assert state.planned == {}

    async def test_forgetting_a_finished_zone_hands_its_marker_back(self, hass):
        """A direct pin: the staged manual run in the test above consumes the
        marker at its own dispatch, so that test cannot see this line at all.
        """
        c = _coord(hass, SEQUENTIAL)
        z1, z2 = _register(c, _zone(1, duration=600), _zone(2, duration=600))
        await _dispatch(c, [_live(z1, 300), _live(z2, 300)])
        # Queued and still marked: whatever took the zone over refused before
        # _run_ceiling, or never reached it.
        c._live_run_zones = {2}
        c._chain_forget_finished(const.WATERING_MODE_SERVICE, 2)
        assert 2 not in c._live_run_zones
