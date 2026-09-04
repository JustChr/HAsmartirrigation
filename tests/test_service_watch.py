"""A confirmed service valve is watched for the rest of its run (issue #88).

``confirm_entity`` used to be read exactly once, at open, and nothing subscribed
to it afterwards. So a valve that shut mid-run -- a Zigbee dropout, a hardware
fault, someone closing it by hand -- left the wall clock running: the run was
recorded as ``actual_s == planned_s``, ``completed``, with its full optimistic
credit standing, and the next calculation went on believing the zone had been
watered. Reported by Eifel-Joe, who runs three service zones on a cistern pump.

Batch mode already had this accounting, because it promotes the same entity to a
watch entity. Service mode now registers its own ``WatchPolicy`` on the shared
engine rather than growing a second copy of the lifecycle.

Driven against the real ``hass`` fixture, for the reason the batch and
OpenSprinkler suites are: the feature IS a state subscription, and a double
replaces exactly the thing under test.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const

VALVE = "binary_sensor.beet_valve"


def _coord(hass):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = hass
    c.store = Mock()
    c._cfg = {}
    c._zones = {}
    c.store.async_get_config = AsyncMock(side_effect=lambda: dict(c._cfg))
    c.store.async_update_config = AsyncMock(side_effect=c._cfg.update)
    c.store.async_update_zone = AsyncMock()
    c.store.get_zone = Mock(side_effect=lambda zid: c._zones.get(int(zid)))
    c.store.config = Mock()
    c.store.config.master_entity = None
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
    c._os_chain_advance = AsyncMock()
    async_mock_service(hass, "script", "irrigation_beet")
    async_mock_service(hass, "script", "stop_irrigation_beet")
    return c


def _zone(zone_id=2, confirm=VALVE, duration=600, **kw):
    z = {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: "Beet",
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        const.ZONE_RUN_SERVICE: "script.irrigation_beet",
        const.ZONE_STOP_SERVICE: "script.stop_irrigation_beet",
        const.ZONE_DURATION_FIELD: "dauer",
        const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
        const.ZONE_DURATION: duration,
        const.ZONE_BUCKET: -20.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
    }
    if confirm is not None:
        z[const.ZONE_CONFIRM_ENTITY] = confirm
    z.update(kw)
    return z


async def _set(hass, entity, state):
    hass.states.async_set(entity, state)
    await hass.async_block_till_done()


async def _settle(hass):
    """Run out the window a valve-off is held open in, in case it was a blip.

    Assertions about the end of a run are only meaningful once this has passed:
    before it, the run is un-settled whether the off was real or not.
    """
    async_fire_time_changed(
        hass,
        dt_util.utcnow() + timedelta(seconds=const.SERVICE_WATCH_SETTLE_SECONDS + 1),
    )
    await hass.async_block_till_done()


async def _off(hass):
    """The valve stops, and stays stopped."""
    await _set(hass, VALVE, "off")
    await _settle(hass)


async def _dispatch(hass, c, zone, *, valve_state="on"):
    c._zones[int(zone[const.ZONE_ID])] = zone
    if zone.get(const.ZONE_CONFIRM_ENTITY):
        await _set(hass, zone[const.ZONE_CONFIRM_ENTITY], valve_state)
    ok = await c.async_run_self_closing(zone, trigger="schedule")
    await hass.async_block_till_done()
    return ok


class TestAValveThatShutsMidRunEndsTheRun:
    async def test_the_run_is_recorded_for_what_it_actually_watered(self, hass):
        c = _coord(hass)
        started = dt_util.utcnow()
        await _dispatch(hass, c, _zone())

        # 100 s in, the valve drops out
        with freeze_time(started + timedelta(seconds=100)):
            await _off(hass)

        c._record_run.assert_awaited()
        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_PARTIAL
        assert kw["planned_s"] == 600
        assert 90 <= kw["actual_s"] <= 110  # not the full window

    async def test_the_optimistic_credit_is_reconciled_down(self, hass):
        c = _coord(hass)
        started = dt_util.utcnow()
        await _dispatch(hass, c, _zone())

        with freeze_time(started + timedelta(seconds=300)):
            await _off(hass)

        # 20 mm was credited at dispatch from a -20 mm bucket; half the window ran,
        # so half of it has to come back off.
        written = [ck.args[1] for ck in c.async_write_watered_bucket.await_args_list]
        # approx: the elapsed is real wall clock, so the dispatch's own microseconds
        # are in it. The point is the half, not the millisecond.
        assert written[-1] == pytest.approx(-10.0, abs=0.01)

    async def test_the_run_no_longer_holds_the_zone(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        assert await c._sc_find_run(2) is not None

        await _off(hass)

        assert await c._sc_find_run(2) is None

    async def test_the_master_hold_is_dropped_with_it(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c.async_master_release.reset_mock()

        await _off(hass)

        c.async_master_release.assert_awaited()


class TestAFullRunIsStillAFullRun:
    async def test_a_valve_off_at_the_planned_end_completes(self, hass):
        c = _coord(hass)
        started = dt_util.utcnow()
        await _dispatch(hass, c, _zone())

        with freeze_time(started + timedelta(seconds=600)):
            await _off(hass)

        kw = c._record_run.await_args.kwargs
        assert kw["result"] == const.RUN_RESULT_COMPLETED
        assert kw["actual_s"] == kw["planned_s"] == 600

    async def test_the_observed_start_is_the_dispatch_instant(self, hass):
        """Not the moment the observation arrived.

        The confirm poll runs BEFORE the watcher is armed, so anchoring the run to
        when the subscription first saw the valve would shorten every run by that
        poll -- and settle a full one as a partial, with its credit reversed.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        run = await c._sc_find_run(2)
        assert run[const.RUN_OBSERVED_START] == run[const.RUN_STARTED]

    async def test_the_flow_meter_is_not_re_seeded_by_the_observation(self, hass):
        """It was started at dispatch, for the window that actually began.

        Re-seeding it at the observed start would throw away everything sampled
        since. The engine does that because a QUEUED run's dispatch precedes its
        water by hours -- which is not true of a valve that opens as it is told.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        c._sc_start_flow_sampling.assert_awaited_once()

    async def test_the_finish_backstop_is_armed_once(self, hass):
        """Re-arming it from the observation would push it past the real close."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        assert c._sc_schedule_cleanup.call_count == 1
        assert c._sc_schedule_cleanup.call_args.args == (2, 600)


class TestTheWatcherNeverWritesAWateringRunOff:
    async def test_an_unavailable_valve_does_not_end_the_run(self, hass):
        """No information is not "the run stopped"."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _set(hass, VALVE, "unavailable")

        assert await c._sc_find_run(2) is not None
        c._record_run.assert_not_awaited()

    async def test_no_give_up_clock_is_armed(self, hass):
        """A service run has no queue to wait behind -- nothing to give up on.

        A give-up clock here could only ever fire against a run that IS watering,
        reversing its credit and raising a fault while the water flowed. That is
        the defect ``arm_give_up_after_start`` documents, reached by a different
        door.
        """
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        await _set(hass, VALVE, "unavailable")

        async_fire_time_changed(
            hass,
            dt_util.utcnow()
            + timedelta(seconds=const.SERVICE_WATCH_GIVE_UP_SECONDS + 30),
        )
        await hass.async_block_till_done()

        assert await c._sc_find_run(2) is not None
        c._set_zone_fault.assert_not_called()


class TestOneOffSampleIsNotEvidenceTheWaterStopped:
    """These are the valves ``_confirm_valve_running`` is written around.

    Its own docstring: sleepy Zigbee/Tuya timers "actuate but report their new
    state back slowly, or silently drop the first command". Ending a run on the
    first `off` would settle those as partials and reverse the credit for water
    that never stopped flowing — trading the defect this feature fixes for a
    worse one on the same hardware.
    """

    async def test_a_valve_that_blips_off_and_back_on_keeps_its_run(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _set(hass, VALVE, "off")
        await _set(hass, VALVE, "on")  # back before the window is out
        await _settle(hass)

        assert await c._sc_find_run(2) is not None
        c._record_run.assert_not_awaited()

    async def test_the_run_is_not_settled_before_the_window_is_out(self, hass):
        """Held open, not finished — the decision is genuinely deferred."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _set(hass, VALVE, "off")

        assert await c._sc_find_run(2) is not None
        c._record_run.assert_not_awaited()

    async def test_a_valve_that_stays_off_still_ends_the_run(self, hass):
        """The debounce is a debounce, not a licence to ignore the valve."""
        c = _coord(hass)
        await _dispatch(hass, c, _zone())

        await _off(hass)

        assert await c._sc_find_run(2) is None


class TestAWriteOnlyValveIsUntouched:
    async def test_a_zone_with_no_confirm_entity_is_not_watched(self, hass):
        """Nothing to subscribe to, and the hardware still owns the close."""
        c = _coord(hass)

        await _dispatch(hass, c, _zone(confirm=None))

        run = await c._sc_find_run(2)
        assert const.RUN_WATCH_ENTITY not in run
        assert const.RUN_OBSERVED_START not in run
        assert not c._watchers()

    async def test_an_unreadable_confirm_entity_is_not_watched(self, hass):
        """``None`` from the confirm poll means "cannot verify", not "confirmed"."""
        c = _coord(hass)

        await _dispatch(hass, c, _zone(), valve_state="unavailable")

        run = await c._sc_find_run(2)
        assert const.RUN_WATCH_ENTITY not in run
        assert not c._watchers()


class TestTheSubscriptionSurvivesARestart:
    async def test_a_run_still_inside_its_window_is_re_adopted(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c._run_watchers = {}  # the subscription lived in memory only

        await c.async_resume_self_closing_runs()
        await hass.async_block_till_done()

        assert 2 in c._watchers()

    async def test_and_it_still_ends_the_run_on_a_valve_off(self, hass):
        c = _coord(hass)
        await _dispatch(hass, c, _zone())
        c._run_watchers = {}
        await c.async_resume_self_closing_runs()
        await hass.async_block_till_done()

        await _off(hass)

        assert await c._sc_find_run(2) is None
