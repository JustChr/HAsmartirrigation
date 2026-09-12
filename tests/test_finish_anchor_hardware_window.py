"""The finish anchor prices a self-closing zone at the window its valve runs.

The series this closes moved the self-closing RUN onto ``hardware_window``: a
minutes-unit valve told "5 minutes" for a 263 s price really runs 300 s, and
``async_run_self_closing`` now books that 300 -- including the chain advance,
which is armed on exactly that number (``_sc_schedule_cleanup(zone_id,
planned_seconds)``, released by ``_sc_finish_run`` -> ``_chain_advance_for_run``,
with ``run_chain.async_dispatch_chained_zones`` holding the remaining zones
until then).

The finish anchor did not move with it. It prices through
``irrigation.async_plan_zone_runs`` and ``run_window.nominal_zone_duration``,
both of which stopped at the unrounded seconds, so the model and the run
disagreed by one rounding PER ZONE on every chained sequencing -- the anchor
said 526 s for a pair the chain really takes 600 s over. Under ``parallel`` the
track is a max rather than a sum, so the same disagreement costs one rounding
there, as it did before the series too.

Every number below is the real chain end, derived from the hardware window,
not from the priced seconds.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.run_window import (
    hardware_priced_seconds,
    nominal_zone_duration,
)
from tests.test_batch import _coord as _batch_coord
from tests.test_batch import _register as _batch_register
from tests.test_batch import _zone as _batch_zone
from tests.test_self_closing import _coord as _run_coord
from tests.test_self_closing import _zone as _run_zone


def _persisted_runs(c):
    """The in-flight runs as the store last saw them.

    ``async_run_self_closing`` writes its run record through the store, so this
    is where the number the run really booked can be read back rather than
    restated. Defined here rather than imported so this file adds no helper to
    the run path's own test module.
    """
    cfg = c.store.async_update_config.await_args.args[0]
    return cfg[const.CONF_ACTIVE_VALVE_RUNS]


SEQUENTIAL = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
PARALLEL = const.CONF_ZONE_SEQUENCING_PARALLEL
ROTATING = const.CONF_ZONE_SEQUENCING_ROTATING

# 263 s priced -> 5 whole minutes told -> 300 s the valve really runs. Chosen
# because the rounding is large (37 s) and 263 is a minute multiple in neither
# direction, so an accidental floor and an accidental ceil give different
# numbers and cannot both pass.
PRICED = 263.0
WINDOW = 300.0

# The same 263 s on SECONDS hardware, made fractional. A whole number makes the
# seconds branch a no-op (263 -> 263) and an assertion over it passes whether
# the conversion ran or not, so the batch pin below prices its seconds-unit case
# at .6: told 264, runs 264, and a site that skipped the rounding is 0.6 s out.
FRACTIONAL = 263.6
FRACTIONAL_WINDOW = 264.0


def _zone(zone_id, *, mode, unit=const.DURATION_UNIT_MINUTES, duration=PRICED):
    """A zone that is due and priced at ``duration`` seconds.

    No throughput/size, so ``_zone_run_decision`` falls through to the daily
    ledger and the decision duration IS ``ZONE_DURATION`` -- what is under test
    is the conversion applied to it, not the deficit math that produced it.

    No ``confirm_entity`` and no ``linked_entity``: both buy a zone 30 s of
    ``zone_confirm_seconds`` on top of its water, which is real but is not this
    fix, and would put a second moving part into every expected number.
    """
    return {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: f"Zone {zone_id}",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_WATERING_MODE: mode,
        const.ZONE_DURATION_UNIT: unit,
        const.ZONE_DURATION: duration,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_BUCKET_THRESHOLD: -1.0,
    }


def _nominal_zone(zone_id, *, mode, unit=const.DURATION_UNIT_MINUTES):
    """Same zone, configured so ``nominal_zone_duration`` prices it at 263 s.

    10 l/min over 10 m2 is 60 mm/h, so a threshold of -(263/3600)*60 mm prices
    to 263/3600*3600 = 263.0 s.
    """
    z = _zone(zone_id, mode=mode, unit=unit)
    z.update(
        {
            const.ZONE_BUCKET_THRESHOLD: -(PRICED / 3600.0) * 60.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_MAXIMUM_DURATION: 36000,
            const.ZONE_LEAD_TIME: 0,
        }
    )
    return z


def _coord(zones, *, sequencing=SEQUENTIAL, slot_minutes=5, absorption_minutes=0):
    """A coordinator built by ``__new__``, as test_nominal_demand_projection does.

    Not the real constructor: it arms ``async_track_time_change`` trackers that
    nothing here cancels, and the harness fails such a test in teardown on the
    lingering timer. Both methods under test are read-only projections and need
    nothing __init__ builds.
    """
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    # No station entity is registered, so station_facts answers "the controller
    # did not answer" and the station track is priced as a chain -- which is
    # all the OpenSprinkler guard below needs it to do.
    hass.states.get = Mock(return_value=None)
    hass.states.async_all = Mock(return_value=[])
    c.hass = hass
    c.store = Mock()
    c.store.config = SimpleNamespace(
        zone_sequencing=sequencing,
        # sequencing_timing reads both as MINUTES and returns seconds.
        zone_sequencing_max_consecutive_duration=slot_minutes,
        zone_sequencing_min_absorption_time=absorption_minutes,
        live_estimate_enabled=False,
    )
    c.store.async_get_zones = AsyncMock(side_effect=lambda: [dict(z) for z in zones])
    c.store.async_get_distributors = AsyncMock(return_value=[])
    return c


class TestTheAnchorCoversTheChain:
    """The test that matters: the anchor against the end the chain really has.

    All three sequencings are pinned, because the shortfall's SIZE is a
    property of the reduction: parallel takes a max and pays one rounding,
    sequential sums and pays one per zone, rotating replays the ring and pays
    one per zone too. The conversion itself is orthogonal to all of that — it
    is applied per zone in the two pricing functions, so what
    ``concurrent_wall_clock`` receives is already the effective budget and the
    reduction never sees the priced number. That is why the rotating case needs
    no separate argument about pauses: ``test_run_window.py`` owns the pause
    model, and this file only has to show the converted budget reaching it.
    """

    @pytest.mark.asyncio
    async def test_a_sequential_pair_of_minute_zones_is_anchored_at_the_real_end(
        self,
    ):
        # Two minutes-unit self-closing zones, each priced 263 s and each
        # really running 300 s. Under sequential the chain holds zone 2 until
        # zone 1's cleanup fires -- and that cleanup is armed on 300, not 263.
        # So the run ends 600 s after it starts.
        #
        # The anchor said 526 and started the run 74 s too late. Before the
        # series it also said 526, but against a real end of 563 (zone 1's
        # chain advance fired on the booked 263, zone 2 then really ran 300),
        # so it was 37 s late: ONE rounding, however many zones were chained.
        # Arming the chain on the effective number without moving the anchor
        # turned that single rounding into one PER ZONE -- 74 s for two, 111 s
        # for three, and so on -- which is the half of this bug the series
        # introduced itself.
        coord = _coord(
            [
                _zone(1, mode=const.WATERING_MODE_SERVICE),
                _zone(2, mode=const.WATERING_MODE_SERVICE),
            ],
            sequencing=SEQUENTIAL,
        )
        assert await coord.get_total_irrigation_duration() == 600

    @pytest.mark.asyncio
    async def test_parallel_pays_one_rounding_not_one_per_zone(self):
        # The guard on the REDUCTION: this fix re-prices each zone, it does not
        # turn a max into a sum. Both valves are opened together and both close
        # at +300, so the track is 300 -- never 526 and never 600.
        coord = _coord(
            [
                _zone(1, mode=const.WATERING_MODE_SERVICE),
                _zone(2, mode=const.WATERING_MODE_SERVICE),
            ],
            sequencing=PARALLEL,
        )
        assert await coord.get_total_irrigation_duration() == 300

    @pytest.mark.asyncio
    async def test_rotating_replays_the_ring_on_the_effective_budget(self):
        # The third reduction, and the other chained one.
        #
        # An absorption pause is configured on purpose. With absorption at 0
        # and no confirms the replay degenerates to sum(budgets) -- 600 at
        # every slot length, which is the number the sequential test above
        # already asserts by identical arithmetic, so such a pin would be blind
        # to both the slot and the replay. At 5 minutes of absorption the
        # pauses bite and the answer moves with the slot: 1020 at a 2-minute
        # slot, 780 at 3, 600 at 5 (one slot per zone, no pause charged).
        #
        # Hand-replayed from simulate_wall_clock's loop, slot 120 s,
        # absorption 300 s, budgets 300/300, confirms 0:
        #   A 0-120, B 120-240
        #   A waits to 420 (300 - 120 elapsed), runs to 540
        #   B needs no wait (300 elapsed exactly), runs to 660
        #   A waits to 840, runs its last 60 to 900
        #   B waits to 960, runs its last 60 to 1020.
        # Priced unconverted (263/263) the same replay gives 983.
        coord = _coord(
            [
                _zone(1, mode=const.WATERING_MODE_SERVICE),
                _zone(2, mode=const.WATERING_MODE_SERVICE),
            ],
            sequencing=ROTATING,
            slot_minutes=2,
            absorption_minutes=5,
        )
        assert await coord.get_total_irrigation_duration() == 1020


class TestThePlanPricesTheSameWindowTheRunBooks:
    """``async_plan_zone_runs`` is where the anchor's live durations are made."""

    async def _durations(self, zones):
        planned = await _coord(zones).async_plan_zone_runs()
        return [p.duration for p in planned]

    @pytest.mark.asyncio
    async def test_a_self_closing_minute_zone_is_planned_at_its_window(self):
        zones = [_zone(1, mode=const.WATERING_MODE_SERVICE)]
        assert await self._durations(zones) == [WINDOW]

    @pytest.mark.asyncio
    async def test_a_classic_zone_carrying_a_minutes_unit_is_not_converted(self):
        # Mode, not unit. A classic zone is timed by Irrigation Plus -- it
        # sleeps the priced seconds and closes the valve itself, whatever
        # duration_unit says -- and the field survives on a zone switched back
        # to classic. Keying on the unit would reserve 300 s for a 263 s run.
        zones = [_zone(1, mode=const.WATERING_MODE_CLASSIC)]
        assert await self._durations(zones) == [PRICED]

    @pytest.mark.asyncio
    async def test_an_opensprinkler_station_is_ceiled_not_rounded(self):
        # A station IS converted -- run_station takes whole seconds, so 263.4 is
        # dispatched and really run as 264. What it must NOT take is
        # hardware_window: the duration unit belongs to a user's own run_service
        # script rather than to that API, and the rules differ on exactly this
        # fraction (ceiling 264 against round-to-nearest 263).
        zones = [_zone(1, mode=const.WATERING_MODE_OPENSPRINKLER, duration=263.4)]
        assert await self._durations(zones) == [264.0]


class TestHardwarePricedSeconds:
    """The shared rule, exercised directly."""

    def test_a_minutes_self_closing_zone_is_priced_at_its_window(self):
        zone = _zone(1, mode=const.WATERING_MODE_SERVICE)
        assert hardware_priced_seconds(zone, PRICED) == WINDOW

    def test_a_seconds_self_closing_zone_rounds_to_the_whole_second(self):
        zone = _zone(
            1, mode=const.WATERING_MODE_SERVICE, unit=const.DURATION_UNIT_SECONDS
        )
        assert hardware_priced_seconds(zone, 263.4) == 263.0

    def test_a_batch_zone_converts_too(self):
        # batch.py prices its queue entries through hardware_window as well
        # (8464b3b0), so the batch track has to be re-priced on the same terms.
        zone = _zone(1, mode=const.WATERING_MODE_BATCH)
        assert hardware_priced_seconds(zone, PRICED) == WINDOW

    def test_a_classic_zone_is_never_converted(self):
        zone = _zone(1, mode=const.WATERING_MODE_CLASSIC)
        assert hardware_priced_seconds(zone, PRICED) == PRICED

    def test_an_opensprinkler_zone_is_ceiled_not_rounded(self):
        # Priced fractionally on purpose: 263.4 is where the station ceiling
        # (264) and hardware_window's round-to-nearest (263) disagree, so a
        # whole number here would pass whichever rule ran. Reserved at 263 the
        # anchor would be short of the 264 s the station is told and runs.
        zone = _zone(1, mode=const.WATERING_MODE_OPENSPRINKLER)
        assert hardware_priced_seconds(zone, 263.4) == 264.0

    def test_nothing_is_conjured_out_of_a_zero(self):
        # A zone priced at 0 must reserve 0, never the one-minute floor of
        # hardware_window's minutes branch -- async_plan_zone_runs produces
        # such a zone on purpose under ignore_demand. hardware_window's own
        # non-positive clamp is what holds this; hardware_priced_seconds adds
        # no guard of its own, because one was added there and measured dead.
        # Pinned from this side anyway: the invariant belongs to the caller's
        # contract, whichever layer happens to hold it.
        zone = _zone(1, mode=const.WATERING_MODE_SERVICE)
        assert hardware_priced_seconds(zone, 0.0) == 0.0


class TestNominalZoneDuration:
    """The other anchor entry point: the steady projection the dial draws."""

    def test_a_minutes_self_closing_zone_prices_at_its_window(self):
        zone = _nominal_zone(1, mode=const.WATERING_MODE_SERVICE)
        assert nominal_zone_duration(zone, metric=True) == WINDOW

    def test_a_classic_zone_with_a_minutes_unit_prices_at_the_priced_seconds(self):
        zone = _nominal_zone(1, mode=const.WATERING_MODE_CLASSIC)
        assert nominal_zone_duration(zone, metric=True) == PRICED

    def test_an_opensprinkler_zone_prices_at_the_whole_second(self):
        # duration_from_deficit rounds its result, so this entry point hands the
        # station an integer and its ceiling has nothing left to do. That is a
        # property of the caller, not an exemption: the ceiling itself is pinned
        # on a fraction in TestHardwarePricedSeconds above.
        zone = _nominal_zone(1, mode=const.WATERING_MODE_OPENSPRINKLER)
        assert nominal_zone_duration(zone, metric=True) == PRICED

    def test_a_calibrated_flow_zone_is_converted_after_it_is_rescaled(self):
        """The ORDER, which both call sites forbid getting wrong and nothing
        else in the repo exercises: every other zone in this file has no
        calibration samples, so hoisting the conversion above the rescale
        leaves them all green.

        The zone measured 5 l/min where 10 is configured, so
        ``calibrated_flow_seconds`` doubles the watering. Convert LAST (right):
        263 * 2 = 526 s, which is 9 whole minutes of hardware time = 540.
        Convert FIRST (wrong): 263 -> 5 min = 300, then 300 * 2 = 600 -- a
        60 s over-reservation, and a number that is neither the priced
        duration nor any window the valve can actually be told.
        """
        zone = _nominal_zone(1, mode=const.WATERING_MODE_SERVICE)
        zone[const.ZONE_FLOW_SENSOR] = "sensor.flow"
        zone[const.ZONE_FLOW_CAL_SAMPLES] = [5.0] * const.FLOW_CAL_MIN_SAMPLES
        assert nominal_zone_duration(zone, metric=True) == 540.0


# --- The two carve-outs, held together -------------------------------------

# Every watering mode the integration has, read off ``const`` rather than
# listed here. A mode added later is carried into the pin by the next run
# instead of being silently exempt from it -- which is the failure mode a
# hand-written list has, and the one this whole pin exists to prevent.
WATERING_MODES = sorted(
    value
    for name, value in vars(const).items()
    if name.startswith("WATERING_MODE_") and isinstance(value, str)
)


async def _what_the_run_books(mode: str) -> float:
    """The seconds the RUN really books for a ``mode`` zone -- by running it.

    Not a restatement of the run path's rule: the number comes back out of
    ``async_run_self_closing``'s own run record (``RUN_PLANNED_SECONDS``), the
    field the credit, the backstop and the chain advance are all taken from.
    Change the rule inside that function and this value moves with it, which is
    precisely what makes comparing it to the anchor say something.

    The one thing supplied from here is REACHABILITY, because it is the half the
    run path expresses by absence rather than by a guard and no test can execute
    an absence. ``async_run_self_closing`` never sees a zone its dispatchers
    reject -- ``irrigation.async_run_zone`` branches into it on
    ``_sc_is_self_closing`` and falls through to the classic runner otherwise,
    and ``async_dispatch_due_zones`` splits the same way -- so a mode that
    predicate rejects is timed by Irrigation Plus itself, which sleeps the
    priced seconds and closes the valve. Nothing re-prices it. Note the trap
    this covers: fed a classic zone directly, ``async_run_self_closing`` books
    300 here too, since its only guard is the OpenSprinkler one. It is
    unreachability, not that guard, that keeps a classic zone on its 263.
    """
    coord = _run_coord()
    coord.hass.config.units = METRIC_SYSTEM
    # A station resolves its running sensor before anything is actuated; without
    # these the OpenSprinkler mode bails out before it reaches the carve-out.
    coord._os_resolve = Mock(
        return_value=("switch.station", "binary_sensor.station_running")
    )
    coord._os_start_watch = AsyncMock()
    zone = _run_zone(
        **{
            const.ZONE_WATERING_MODE: mode,
            # Minutes, and PRICED is the same 263 s the anchor is asked about
            # just below, so both sides provably answer about one zone. A
            # duration_unit that survives on modes which do not own their close
            # is the point: it is what a guard keyed on the unit instead of the
            # mode would trip over.
            const.ZONE_DURATION: PRICED,
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_MINUTES,
            const.ZONE_LINKED_ENTITY: "switch.station",
        }
    )
    if not coord._sc_is_self_closing(zone):
        return PRICED
    assert await coord.async_run_self_closing(zone) is True
    runs = _persisted_runs(coord)
    assert len(runs) == 1
    return runs[0][const.RUN_PLANNED_SECONDS]


class TestTheAnchorAndTheRunSelectTheSameZones:
    """Which zones get converted is decided twice, and nothing else joins them.

    ``run_window`` imports ``self_closing``, so the two sites cannot share a
    predicate without a cycle, and they express the same selection differently:

    * the RUN, ``self_closing.async_run_self_closing``, guards only on
      ``if not is_opensprinkler`` -- its self-closing half is implicit, carried
      by the fact that no dispatcher routes any other mode into it;
    * the ANCHOR, ``run_window.hardware_priced_seconds``, has to say both out
      loud, and then say which of the two rounding rules each half gets.

    Two spellings of one decision, in modules that cannot be made to share it.
    Every other test in this file pins the anchor against numbers a human
    worked out; none of them would notice the two drifting apart, because both
    sites would still be internally consistent. Alter the OpenSprinkler test on
    one side, "simplify" either guard, or key one of them on ``duration_unit``,
    and the model and the run would disagree about WHICH zones convert while
    the suite stayed green -- the exact class of defect this branch exists to
    remove, reintroduced by the branch's own asymmetry.
    """

    def test_the_mode_roster_is_not_empty(self):
        # The parametrisation below reads its cases out of const, so a rename of
        # those constants would quietly reduce it to nothing and pytest would
        # report no failures. Guard the discovery itself, naming the two poles
        # by constant: without a converting mode and a non-converting one in the
        # roster, agreement between the two sites is free.
        assert const.WATERING_MODE_SERVICE in WATERING_MODES
        assert const.WATERING_MODE_OPENSPRINKLER in WATERING_MODES
        assert const.WATERING_MODE_CLASSIC in WATERING_MODES

    @pytest.mark.parametrize("mode", WATERING_MODES)
    @pytest.mark.asyncio
    async def test_the_anchor_reserves_what_the_run_books(self, mode):
        # One zone description, 263 s on minute hardware, asked of both sites.
        # The rounding is 37 s, so a site that converts when the other does not
        # cannot hide behind a number that happens to match.
        booked = await _what_the_run_books(mode)
        zone = _zone(1, mode=mode, unit=const.DURATION_UNIT_MINUTES)
        assert hardware_priced_seconds(zone, PRICED) == booked


# --- The third site, and the one the roster above cannot reach ---------------


async def _what_the_batch_queue_books(hass, *, unit: str, priced: float) -> float:
    """The seconds the BATCH dispatch really books for one zone -- by dispatching it.

    Same principle as :func:`_what_the_run_books`, and deliberately the same
    observation point: ``RUN_PLANNED_SECONDS``, read off the run record
    production itself wrote. ``_batch_record_run``'s ``seconds`` argument is the
    other candidate and is the worse one. It is an internal argument rather than
    an outcome, reading it needs a wrapper around a production method, and it
    answers wrongly in both directions: move the conversion INTO
    ``_batch_record_run`` -- a refactor that changes no behaviour -- and the
    wrapper goes red; leave the dispatch site converting but write some other
    number into the record, and it stays green while every consumer of that
    field is wrong. The record is where the credit ceiling, the watch deadline,
    the observed-watering suppression window and the finish settlement all read
    their duration, so it is the number that has to agree with the anchor. It is
    also the field :func:`_what_the_run_books` reads, so the two pins compare
    like with like.

    REACHABILITY is what is supplied from here, for the same reason it is for
    the run: it is the half ``batch.py`` expresses by absence, and no test can
    execute an absence. ``async_dispatch_due_zones`` filters on
    ``is_batch_zone`` and splits those zones off to
    ``async_dispatch_batch_zones``, so no other mode ever arrives there -- and
    handing this dispatcher a non-batch zone to see what it does would be
    exercising a path production does not take, which is the very defect this
    pin exists to close. The subject is therefore batch-mode zones and no other.

    The zone keeps the ``confirm_entity`` ``_batch_zone`` gives it by default.
    Batch mode promotes that field from optional confirmation to required -- the
    valve switch IS how the run is observed -- and a zone without one is refused
    rather than dispatched, which would leave no run record to read back at all.
    """
    coord = _batch_coord(hass)
    zones = _batch_register(
        coord,
        _batch_zone(1, duration=priced, **{const.ZONE_DURATION_UNIT: unit}),
    )
    await coord.async_dispatch_batch_zones(zones, trigger="schedule")
    runs = coord._runs
    assert len(runs) == 1, "the zone was refused, so nothing was booked to compare"
    return runs[0][const.RUN_PLANNED_SECONDS]


class TestTheAnchorAndTheBatchQueueBookTheSameSeconds:
    """The third site that converts, and the second to decide WHICH by absence.

    ``batch.py``'s dispatch converts UNCONDITIONALLY: one
    ``hardware_window(seconds, unit)`` per queue entry, with no mode guard at
    all. Its "which zones" half is carried entirely by REACHABILITY, exactly as
    ``async_run_self_closing``'s is -- ``async_dispatch_due_zones`` filters on
    ``is_batch_zone`` and hands that set to ``async_dispatch_batch_zones``, so
    nothing else can arrive. The ANCHOR has to name the same selection out loud:
    ``hardware_priced_seconds``'s ``not is_self_closing_zone(zone)``, which lets
    a batch zone through only because ``is_self_closing_zone`` happens to list
    ``WATERING_MODE_BATCH``. Two
    spellings of one decision again, and again in modules that cannot be made to
    share it: ``run_window`` imports ``is_batch_zone`` from ``batch``, so
    ``batch`` importing back would be a cycle.

    ``TestTheAnchorAndTheRunSelectTheSameZones`` above HAS a ``batch`` row, and
    it does not cover this. That row asks ``async_run_self_closing`` what it
    books for a batch zone -- a path production never sends one down, because
    the dispatcher splits it away first. The row is green on a path batch does
    not take, and green because the two functions happen to agree on the number;
    nothing in it observes ``async_dispatch_batch_zones`` at all.

    Nor did anything else. ``test_batch.py::
    TestThePlanAndTheBooksNameTheSameDuration`` compares batch's plan entry
    against batch's own run record: internally consistent by construction, and
    blind to the anchor. ``hardware_priced_seconds`` appears in no test file but
    this one. So the batch track could be anchored at 263 s for a queue the
    controller really runs 300 s of -- a finish-governed night started 37 s per
    zone too late -- with every test in both files green.
    """

    def test_both_durations_are_ones_the_conversion_actually_moves(self):
        """Guard the CASES, the way the roster test above guards its discovery.

        Both assertions below compare two numbers; neither says the conversion
        happened. Pick a duration the rounding leaves alone -- 300 s on minutes,
        or a whole number on seconds -- and both sites return the input, the
        comparison holds, and the pin is worth nothing. Named here so a later
        edit to the constants cannot quietly empty it out.
        """
        minutes = _zone(
            1, mode=const.WATERING_MODE_BATCH, unit=const.DURATION_UNIT_MINUTES
        )
        seconds = _zone(
            1, mode=const.WATERING_MODE_BATCH, unit=const.DURATION_UNIT_SECONDS
        )
        assert hardware_priced_seconds(minutes, PRICED) == WINDOW
        assert WINDOW != PRICED
        assert hardware_priced_seconds(seconds, FRACTIONAL) == FRACTIONAL_WINDOW
        assert FRACTIONAL_WINDOW != FRACTIONAL

    async def test_a_minutes_unit_batch_zone_is_anchored_at_what_the_queue_books(
        self, hass
    ):
        # One zone description -- batch mode, minutes hardware, 263 priced
        # seconds -- put to both sites, so they provably answer about the same
        # valve. The rounding is 37 s, far too large for a site that skipped it
        # to hide behind a number that happens to match.
        booked = await _what_the_batch_queue_books(
            hass, unit=const.DURATION_UNIT_MINUTES, priced=PRICED
        )
        zone = _zone(
            1, mode=const.WATERING_MODE_BATCH, unit=const.DURATION_UNIT_MINUTES
        )
        assert hardware_priced_seconds(zone, PRICED) == booked

    async def test_a_fractional_seconds_batch_zone_is_anchored_at_what_it_books(
        self, hass
    ):
        # The seconds branch, which the minutes case cannot speak for: it rounds
        # to the NEAREST whole second rather than up, and a site keyed on
        # ``duration_unit == minutes`` instead of on the mode would skip it
        # entirely while staying green above. 0.6 s is a small disagreement and
        # a real one -- it is the same one rounding per zone, on hardware where
        # the anchor otherwise looks exact.
        booked = await _what_the_batch_queue_books(
            hass, unit=const.DURATION_UNIT_SECONDS, priced=FRACTIONAL
        )
        zone = _zone(
            1, mode=const.WATERING_MODE_BATCH, unit=const.DURATION_UNIT_SECONDS
        )
        assert hardware_priced_seconds(zone, FRACTIONAL) == booked
