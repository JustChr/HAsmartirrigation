"""An optimistic timed credit may never leave a zone above its run target.

``duration_math.duration_from_deficit`` prices a run as ``lead_time + water_time``,
but every timed credit prices the WHOLE open window as delivered water
(``_timed_volume_l``). So a timed run always over-credits by the lead time's flow,
and the paths rely on clamping at the run's target to absorb it —
``_run_valve_metered`` does exactly that via ``_run_ceiling``.

The three dispatch modes that credit optimistically (self-closing, OpenSprinkler,
batch) clamped at ``maximum_bucket`` instead, which is the *live-estimate surplus*
allowance, not the run target. The surplus escaped and the zone settled above 0.

Field report: issue #88 (pnaklicki) — a batch zone left at +3 mm after a run that
watered for exactly its calculated time, unpaused. 90 s of lead time on a
10 L/min, 5 m2 zone is +3.000 mm exactly.

These tests drive the REAL credit arithmetic. Both mode suites mock
``_timed_volume_l``/``_credited_depth_native`` out, which is why a green suite
never saw this.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.duration_math import zone_run_duration
from custom_components.irrigation_plus.run_watch import run_credit_ceiling


def _coord(metric=True):
    """A coordinator with the credit arithmetic left REAL."""
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.hass.config.units = METRIC_SYSTEM if metric else US_CUSTOMARY_SYSTEM
    c.hass.services.async_call = AsyncMock()
    c.hass.bus.async_fire = Mock()
    c.store = Mock()
    c.store.async_get_config = AsyncMock(return_value={})
    c.store.async_update_zone = AsyncMock()
    c.store.async_update_config = AsyncMock()
    c._record_run = AsyncMock()
    c._sc_schedule_cleanup = Mock()
    c._confirm_valve_running = AsyncMock(return_value=True)
    return c


def _zone(**kw):
    """A zone whose duration is derived from its own deficit, as the calc does."""
    z = {
        const.ZONE_ID: 2,
        const.ZONE_NAME: "Beet",
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        const.ZONE_RUN_SERVICE: "script.irrigation_beet",
        const.ZONE_DURATION_FIELD: "dauer",
        const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
        const.ZONE_BUCKET: -8.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_SIZE: 5.0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_LEAD_TIME: 90,
        const.ZONE_MAXIMUM_DURATION: None,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
    }
    z.update(kw)
    z[const.ZONE_DURATION] = zone_run_duration(
        z, z[const.ZONE_BUCKET], kw.pop("_metric", True)
    )
    return z


def _bucket_written(c):
    """The last bucket level written to the store."""
    calls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert calls, "no bucket write happened"
    return calls[-1].args[1][const.ZONE_BUCKET]


# --- the arithmetic itself ------------------------------------------------


@pytest.mark.parametrize("lead", [0, 30, 60, 90, 180])
@pytest.mark.parametrize("mult", [1.0, 1.5, 2.0])
def test_timed_credit_over_delivers_by_exactly_the_lead_time(lead, mult):
    """Pin the leak the ceiling has to absorb, so it can never drift unseen.

    This is the BOTH-SIDES check: duration_from_deficit priced the run, and the
    credit helpers replay it. Their disagreement is the lead time's water, divided
    by the multiplier (the multiplier inflates duration, and the credit divides it
    back out).
    """
    c = _coord()
    zone = _zone(**{const.ZONE_LEAD_TIME: lead, const.ZONE_MULTIPLIER: mult})
    seconds = zone[const.ZONE_DURATION]

    depth = c._credited_depth_native(zone, c._timed_volume_l(zone, seconds))
    surplus = depth - abs(zone[const.ZONE_BUCKET])

    expected = lead * zone[const.ZONE_THROUGHPUT] / (60 * zone[const.ZONE_SIZE] * mult)
    assert surplus == pytest.approx(expected, abs=1e-6)
    if lead:
        assert surplus > 0, "a lead time must show up as an over-credit"


def test_run_ceiling_is_the_target_not_the_maximum_bucket():
    """The two ceilings are different numbers; a run must clamp at the target."""
    c = _coord()
    zone = _zone()
    assert c._run_ceiling(zone) == 0.0
    assert zone[const.ZONE_MAXIMUM_BUCKET] == 50.0


# --- the dispatch modes ----------------------------------------------------


async def test_self_closing_run_lands_at_target_not_above():
    c = _coord()
    zone = _zone()
    c.store.get_zone = Mock(return_value=zone)
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._note_si_valve = Mock()

    ok = await c.async_run_self_closing(zone, trigger="schedule")

    assert ok is True
    assert _bucket_written(c) == pytest.approx(0.0, abs=1e-9)


async def test_batch_dispatch_lands_at_target_not_above():
    c = _coord()
    zone = _zone()
    c.store.get_zone = Mock(return_value=zone)
    c._note_si_valve = Mock()
    c._sc_add_run = AsyncMock()
    c._sc_fire = Mock()
    c._watch_start = AsyncMock()

    await c._batch_record_run(zone, "switch.valve_front", zone[const.ZONE_DURATION])

    assert _bucket_written(c) == pytest.approx(0.0, abs=1e-9)


# --- the two behaviours the clamp must NOT break ---------------------------


async def test_live_estimate_run_may_still_credit_a_surplus():
    """``_run_ceiling``'s live-estimate branch is the reason surplus exists."""
    c = _coord()
    zone = _zone()
    c.store.get_zone = Mock(return_value=zone)
    c._live_run_zones = {2}
    c._note_si_valve = Mock()
    c._sc_add_run = AsyncMock()
    c._sc_fire = Mock()
    c._watch_start = AsyncMock()

    await c._batch_record_run(zone, "switch.valve_front", zone[const.ZONE_DURATION])

    # marked as a live-estimate run -> the surplus is allowed through, up to
    # maximum_bucket, exactly as _run_valve_metered would.
    assert _bucket_written(c) == pytest.approx(3.0, abs=1e-6)


async def test_forecast_weighted_target_is_respected():
    """A rain-covered remainder is the target, and the run stops there."""
    c = _coord()
    zone = _zone(**{const.ZONE_IRRIGATION_TARGET_BUCKET: -2.0})
    c.store.get_zone = Mock(return_value=zone)
    c._note_si_valve = Mock()
    c._sc_add_run = AsyncMock()
    c._sc_fire = Mock()
    c._watch_start = AsyncMock()

    await c._batch_record_run(zone, "switch.valve_front", zone[const.ZONE_DURATION])

    assert _bucket_written(c) == pytest.approx(-2.0, abs=1e-9)


async def test_a_short_run_still_credits_proportionally():
    """The clamp is a ceiling, not a reset: a cut-short run stays below target."""
    c = _coord()
    zone = _zone()
    c.store.get_zone = Mock(return_value=zone)
    c._note_si_valve = Mock()
    c._sc_add_run = AsyncMock()
    c._sc_fire = Mock()
    c._watch_start = AsyncMock()

    await c._batch_record_run(zone, "switch.valve_front", 60.0)

    # 60 s at 10 L/min over 5 m2 = 2 mm, against an 8 mm deficit
    assert _bucket_written(c) == pytest.approx(-6.0, abs=1e-9)


# --- the ceiling has to SURVIVE the run, not just be applied at dispatch ----
#
# The dispatch clamp above is only the first of up to three writes for one run.
# A zone with a flow sensor is reconciled again when it completes, and an early
# stop corrects the optimistic credit a third time. Both of those re-derived a
# ceiling of their own — ``maximum_bucket`` — and so put the lead time's surplus
# straight back on a zone the dispatch had just landed on its target. Only a
# zone with NO flow sensor, completing normally, ever saw the fix.
#
# _run_ceiling cannot simply be asked again: it CONSUMES the live-estimate
# marker. So the number is recorded once, at dispatch (const.RUN_CEILING), and
# read back by run_credit_ceiling.


def _finished_run(zone, *, ceiling=None, pre_bucket=-8.0, planned_mm=11.0):
    """The run record a dispatch persists, as the finish paths receive it."""
    run = {
        const.RUN_ZONE_ID: zone[const.ZONE_ID],
        const.RUN_ENTITY_ID: zone.get(const.ZONE_RUN_SERVICE),
        const.RUN_PLANNED_SECONDS: zone[const.ZONE_DURATION],
        const.RUN_PLANNED_MM: planned_mm,
        const.RUN_PRE_BUCKET: pre_bucket,
        const.RUN_MODE: const.WATERING_MODE_SERVICE,
    }
    if ceiling is not None:
        run[const.RUN_CEILING] = ceiling
    return run


def _finish_host(c, zone):
    c.store.get_zone = Mock(return_value=zone)
    c._sc_remove_run = AsyncMock()
    c._sc_cancel_cleanup = Mock()
    c._os_cancel_watch = Mock()
    c._stamp_run_finalized = AsyncMock()
    c._sc_fire = Mock()
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    return c


async def test_the_dispatch_records_the_ceiling_it_clamped_at():
    """Both sides of the round trip: what dispatch decided is what finish reads."""
    c = _coord()
    zone = _zone()
    c.store.get_zone = Mock(return_value=zone)
    c._note_si_valve = Mock()
    c._sc_add_run = AsyncMock()
    c._sc_fire = Mock()
    c._watch_start = AsyncMock()

    await c._batch_record_run(zone, "switch.valve_front", zone[const.ZONE_DURATION])

    record = c._sc_add_run.await_args.args[0]
    assert record[const.RUN_CEILING] == 0.0
    assert run_credit_ceiling(record, zone) == 0.0


async def test_a_measured_completion_does_not_put_the_surplus_back():
    """The flow-sensor half of #88: dispatch lands at 0, the finish kept it at 0."""
    c = _coord()
    zone = _zone()
    _finish_host(c, zone)
    seconds = zone[const.ZONE_DURATION]
    # the meter measured exactly what the timed estimate priced
    measured = c._timed_volume_l(zone, seconds)
    c._sc_finish_flow = Mock(return_value=(measured, {}))
    c._sc_find_run = AsyncMock(return_value=_finished_run(zone, ceiling=0.0))

    await c._sc_finish_run(zone[const.ZONE_ID])

    assert _bucket_written(c) == pytest.approx(0.0, abs=1e-9)


async def test_a_stop_at_the_full_window_does_not_put_the_surplus_back():
    """The other door: a run stopped at its planned end is still a full run."""
    c = _coord()
    zone = _zone()
    _finish_host(c, zone)
    seconds = zone[const.ZONE_DURATION]
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._sc_find_run = AsyncMock(return_value=_finished_run(zone, ceiling=0.0))
    c._sc_run_elapsed = Mock(return_value=seconds)

    await c.async_stop_self_closing(zone[const.ZONE_ID])

    assert _bucket_written(c) == pytest.approx(0.0, abs=1e-9)


async def test_a_measured_completion_of_a_LIVE_run_still_keeps_its_surplus():
    """The behaviour the clamp must not break, on the finish side too.

    A live-estimate run was dispatched with maximum_bucket as its ceiling, and
    reading it back is what keeps its water when the meter reconciles it.
    """
    c = _coord()
    zone = _zone()
    _finish_host(c, zone)
    measured = c._timed_volume_l(zone, zone[const.ZONE_DURATION])
    c._sc_finish_flow = Mock(return_value=(measured, {}))
    c._sc_find_run = AsyncMock(return_value=_finished_run(zone, ceiling=50.0))

    await c._sc_finish_run(zone[const.ZONE_ID])

    # 11 mm delivered onto a -8 mm bucket, and nothing clamps it back to 0
    assert _bucket_written(c) == pytest.approx(3.0, abs=1e-6)


async def test_a_run_persisted_without_a_ceiling_falls_back_to_maximum_bucket():
    """An upgrade mid-run: the record predates RUN_CEILING.

    It has to settle under the clamp it was DISPATCHED with, which for those runs
    was maximum_bucket. Anything stricter would reverse credit the run had
    already been promised.
    """
    c = _coord()
    zone = _zone()
    _finish_host(c, zone)
    measured = c._timed_volume_l(zone, zone[const.ZONE_DURATION])
    c._sc_finish_flow = Mock(return_value=(measured, {}))
    c._sc_find_run = AsyncMock(return_value=_finished_run(zone, ceiling=None))

    await c._sc_finish_run(zone[const.ZONE_ID])

    assert _bucket_written(c) == pytest.approx(3.0, abs=1e-6)
    assert run_credit_ceiling({}, zone) == 50.0
    assert run_credit_ceiling({}, {}) == float("inf")
    # a record whose stored ceiling is unreadable must not clamp to nonsense
    assert run_credit_ceiling({const.RUN_CEILING: "n/a"}, zone) == float("inf")


async def test_a_short_run_is_still_corrected_down_by_the_stop():
    """The ceiling is a ceiling. A stop halfway still reverses half the credit."""
    c = _coord()
    zone = _zone()
    _finish_host(c, zone)
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._sc_find_run = AsyncMock(return_value=_finished_run(zone, ceiling=0.0))
    c._sc_run_elapsed = Mock(return_value=zone[const.ZONE_DURATION] / 2)

    await c.async_stop_self_closing(zone[const.ZONE_ID])

    # half of the 11 mm optimistic credit, from -8.0
    assert _bucket_written(c) == pytest.approx(-2.5, abs=1e-9)


# --- a MANUAL run is priced by the user, not by the bucket ------------------
#
# async_run_zone marks its zone in _live_run_zones so _run_ceiling grants the
# run its water: the duration came from the user, not from the daily deficit, so
# clamping the credit at the daily target is wrong. That marking sat BELOW the
# self-closing branch's early return, so a manual run of a service zone clamped
# at the target instead — crediting nothing from a bucket already at 0, and
# pulling a zone sitting ABOVE its target back down to it. Reported on #88.


def _manual_zone(bucket, **kw):
    """A zone with no lead time, so 10 min at 10 L/min over 5 m2 is exactly 20 mm."""
    z = _zone(**{const.ZONE_LEAD_TIME: 0, const.ZONE_BUCKET: bucket, **kw})
    z[const.ZONE_DURATION] = 600
    return z


@pytest.mark.parametrize(
    ("pre", "expected"),
    [(0.0, 20.0), (-2.0, 18.0), (3.0, 23.0), (-25.0, -5.0)],
)
async def test_a_manual_run_of_a_service_zone_credits_the_water_it_delivered(
    pre, expected
):
    c = _coord()
    zone = _manual_zone(pre)
    c.store.get_zone = Mock(return_value=zone)
    c.zone_run_in_flight = Mock(return_value=False)
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._note_si_valve = Mock()

    await c.async_run_zone(zone[const.ZONE_ID], 10)

    assert _bucket_written(c) == pytest.approx(expected, abs=1e-9)


async def test_a_manual_run_never_takes_credit_away():
    """The row that made this a defect rather than a missed opportunity.

    A zone at +3 mm, watered for ten minutes by hand, was written back to 0.0:
    the run REMOVED 3 mm of credit, leaving the next calculation to ask for
    water the zone had just been given.
    """
    c = _coord()
    zone = _manual_zone(3.0)
    c.store.get_zone = Mock(return_value=zone)
    c.zone_run_in_flight = Mock(return_value=False)
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._note_si_valve = Mock()

    await c.async_run_zone(zone[const.ZONE_ID], 10)

    assert _bucket_written(c) > 3.0


async def test_a_manual_run_still_stops_at_maximum_bucket():
    """The surplus is allowed, but it is not unbounded."""
    c = _coord()
    zone = _manual_zone(0.0, **{const.ZONE_MAXIMUM_BUCKET: 5.0})
    c.store.get_zone = Mock(return_value=zone)
    c.zone_run_in_flight = Mock(return_value=False)
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._note_si_valve = Mock()

    await c.async_run_zone(zone[const.ZONE_ID], 10)

    assert _bucket_written(c) == pytest.approx(5.0, abs=1e-9)


async def test_a_refused_manual_run_leaves_no_marker_for_the_next_one():
    """The marker is set per dispatch, so a rejection must not arm the next run.

    A live marker left behind is not inert: the next run of that zone consumes
    it and is handed a ceiling meant for a run that never watered.
    """
    c = _coord()
    zone = _manual_zone(0.0)
    c.store.get_zone = Mock(return_value=zone)
    c.zone_run_in_flight = Mock(return_value=True)  # a run already holds the valve

    await c.async_run_zone(zone[const.ZONE_ID], 10)

    assert not getattr(c, "_live_run_zones", set())
    assert c._run_ceiling(zone) == 0.0


async def test_a_valve_that_never_opened_hands_the_marker_back():
    """The abort path credits nothing, so its ceiling must not be inherited."""
    c = _coord()
    zone = _manual_zone(0.0)
    c.store.get_zone = Mock(return_value=zone)
    c.zone_run_in_flight = Mock(return_value=False)
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._note_si_valve = Mock()
    c._set_zone_fault = Mock()
    c._fire_zone_problem = Mock()
    # the valve reports it never opened
    zone[const.ZONE_CONFIRM_ENTITY] = "binary_sensor.beet_valve"
    c._confirm_valve_running = AsyncMock(return_value=False)

    await c.async_run_zone(zone[const.ZONE_ID], 10)

    assert zone[const.ZONE_ID] not in getattr(c, "_live_run_zones", set())
    assert c._run_ceiling(zone) == 0.0


# --- the fourth mode: a distributor member ---------------------------------
#
# 6b5f716 fixed "the three modes that credit optimistically at dispatch". A
# distributor member credits at the END of its outlet's window instead, which is
# why it was not one of them — but its window is priced by the same
# duration_from_deficit, so it carries the same lead time and over-credited by
# exactly the same amount. It clamped at maximum_bucket too.
#
# It has no run record to carry a ceiling and no live-estimate marker to consume
# (members are filtered out of the dispatch that sets them), so the sweep decides
# the ceiling directly. duration_override is its manual signal: a user-set window
# is not a price read off the bucket, exactly like a manual run_zone.


async def test_a_distributor_sweep_lands_its_member_at_the_target():
    c = _coord()
    zone = _zone()
    c.store.get_zone = Mock(return_value=zone)
    c._stamp_run_finalized = AsyncMock()

    await c._dist_credit_zone(
        zone, zone[const.ZONE_DURATION], ceiling=c._zone_target_bucket(zone)
    )

    assert _bucket_written(c) == pytest.approx(0.0, abs=1e-9)


async def test_a_distributor_run_with_a_custom_duration_keeps_its_water():
    """``ceiling=None`` is the surplus allowance — a manual run, or an observed one."""
    c = _coord()
    zone = _zone()
    c.store.get_zone = Mock(return_value=zone)
    c._stamp_run_finalized = AsyncMock()

    await c._dist_credit_zone(zone, zone[const.ZONE_DURATION], ceiling=None)

    assert _bucket_written(c) == pytest.approx(3.0, abs=1e-6)


async def test_a_distributor_member_still_stops_at_maximum_bucket():
    c = _coord()
    zone = _zone(**{const.ZONE_BUCKET: 0.0, const.ZONE_MAXIMUM_BUCKET: 2.0})
    c.store.get_zone = Mock(return_value=zone)
    c._stamp_run_finalized = AsyncMock()

    await c._dist_credit_zone(zone, 600, ceiling=None)

    assert _bucket_written(c) == pytest.approx(2.0, abs=1e-9)
