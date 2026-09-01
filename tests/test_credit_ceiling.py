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

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.duration_math import zone_run_duration


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
