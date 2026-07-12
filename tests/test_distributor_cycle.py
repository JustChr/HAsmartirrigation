"""Gardena distributor cycle loop + recovery (DistributorMixin orchestration)."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.distributor import DistributorMixin
from custom_components.smart_irrigation.master import MasterMixin
from tests.test_distributor import _dist, _host


class _CycleHost(DistributorMixin, MasterMixin):
    """Minimal host to unit-test the cycle orchestration in isolation."""


def _mem(zid, outlet, **kw):
    z = {
        const.ZONE_ID: zid,
        const.ZONE_NAME: f"Z{zid}",
        "distributor_id": 0,
        "outlet_number": outlet,
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 60.0,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_BUCKET_THRESHOLD: 0.0,
    }
    z.update(kw)
    return z


def test_needs_water_true_for_due_zone():
    c = _CycleHost()
    assert c._dist_needs_water(_mem(1, 1)) is True


def test_needs_water_false_when_disabled():
    c = _CycleHost()
    assert (
        c._dist_needs_water(_mem(1, 1, **{const.ZONE_STATE: const.ZONE_STATE_DISABLED}))
        is False
    )


def test_needs_water_false_when_duration_zero():
    c = _CycleHost()
    assert c._dist_needs_water(_mem(1, 1, **{const.ZONE_DURATION: 0})) is False


def test_needs_water_false_when_bucket_above_threshold():
    c = _CycleHost()
    assert c._dist_needs_water(_mem(1, 1, **{const.ZONE_BUCKET: 5.0})) is False


async def test_members_sorted_by_outlet():
    c = _CycleHost()
    c.store = Mock()
    c.store.async_get_zones = AsyncMock(
        return_value=[
            _mem(1, 3),
            {const.ZONE_ID: 9, "distributor_id": 1, "outlet_number": 1},  # other dist
            _mem(2, 1),
            _mem(3, 2),
        ]
    )
    members = await c._dist_members(0)
    assert [m[const.ZONE_ID] for m in members] == [2, 3, 1]


async def test_persist_and_clear_cycle():
    c = _CycleHost()
    c.hass = Mock()
    c.hass.data = {}  # I2: _dist_store_update fires the real dispatcher; short-circuit
    c.store = Mock()
    c.store.async_update_distributor = AsyncMock()
    await c._dist_persist_cycle(0, 2, "watering")
    c.store.async_update_distributor.assert_awaited_with(
        0, {"active_cycle": {"outlet": 2, "phase": "watering"}}
    )
    await c._dist_clear_cycle(0)
    c.store.async_update_distributor.assert_awaited_with(0, {"active_cycle": {}})


def _credit_host():
    c = _CycleHost()
    c.store = Mock()
    c.store.async_update_zone = AsyncMock()
    c._timed_volume_l = Mock(return_value=20.0)  # litres
    c._credited_depth_native = Mock(return_value=4.0)  # mm
    c._record_run = AsyncMock()
    return c


async def test_credit_zone_credits_bucket_and_records_run():
    c = _credit_host()
    z = _mem(2, 1, **{const.ZONE_BUCKET: -5.0, const.ZONE_MAXIMUM_BUCKET: 50.0})
    await c._dist_credit_zone(z, 60.0)
    # bucket -5 + 4 = -1
    c.store.async_update_zone.assert_awaited_once_with(2, {const.ZONE_BUCKET: -1.0})
    kwargs = c._record_run.await_args.kwargs
    assert kwargs["result"] == const.RUN_RESULT_COMPLETED
    assert kwargs["volume_l"] == 20.0
    assert kwargs["trigger"] == const.RUN_TRIGGER_DISTRIBUTOR
    assert kwargs["add_to_total"] is True


async def test_credit_zone_caps_at_maximum_bucket():
    c = _credit_host()
    c._credited_depth_native = Mock(return_value=100.0)
    z = _mem(2, 1, **{const.ZONE_BUCKET: -5.0, const.ZONE_MAXIMUM_BUCKET: 10.0})
    await c._dist_credit_zone(z, 60.0)
    c.store.async_update_zone.assert_awaited_once_with(2, {const.ZONE_BUCKET: 10.0})


def _dist_cfg(**kw):
    d = {
        "id": 0,
        "name": "Garten",
        "pause_seconds": 60,
        "skip_pulse_seconds": 20,
        "current_outlet": 1,
        "position_state": const.POSITION_STATE_SYNCED,
        "commissioning_confirmed": True,
        "confirm_entity": None,
        "use_master": True,
    }
    d.update(kw)
    return d


def _loop_host(members, **cfg_over):
    c = _CycleHost()
    c.hass = Mock()
    c.hass.services.async_call = AsyncMock()
    c.store = Mock()
    c.store.async_update_distributor = AsyncMock()
    # isolate the loop: mock the primitives + coordinator helpers
    c._dist_members = AsyncMock(return_value=members)
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda zs: list(zs))
    c._rain_delay_active = Mock(return_value=False)
    c._dist_master_start = AsyncMock()
    c._dist_master_end = AsyncMock()
    c._dist_master_window_off = AsyncMock()
    c._dist_master_window_on = AsyncMock()
    c._dist_open_inlet = AsyncMock()
    c._dist_close_inlet = AsyncMock()
    c._dist_sleep = AsyncMock()
    c._dist_credit_zone = AsyncMock()
    c._dist_mark_uncertain = AsyncMock()
    c._dist_persist_cycle = AsyncMock()
    c._dist_clear_cycle = AsyncMock()
    c._confirm_valve_running = AsyncMock(return_value=None)
    c._dist_advance = AsyncMock(side_effect=lambda did, cur, n: (cur % n) + 1)
    # Part B (early stop): _CycleHost mixes in only DistributorMixin + MasterMixin,
    # not IrrigationRunnerMixin (where _metered_target_volume/_zone_target_bucket
    # live) -- the real SmartIrrigationCoordinator has both. Stub a zero target so
    # the sweep's derivation (tv > 0) is False on every _loop_host test here: no
    # target, cap == window, identical to pre-Part-B behaviour. Flow-volume itself
    # is covered in test_distributor_dispatch.py's sweep tests.
    c._metered_target_volume = Mock(return_value=0.0)
    c._zone_target_bucket = Mock(return_value=0.0)
    return c


async def test_cycle_blocked_when_not_confirmed():
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    ran = await c.async_run_distributor_cycle(_dist_cfg(commissioning_confirmed=False))
    assert ran is False
    c._dist_master_start.assert_not_awaited()


async def test_cycle_blocked_when_uncertain():
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    ran = await c.async_run_distributor_cycle(
        _dist_cfg(position_state=const.POSITION_STATE_UNCERTAIN)
    )
    assert ran is False
    c._dist_master_start.assert_not_awaited()


async def test_cycle_rule_b_when_rain_delay():
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    c._rain_delay_active = Mock(return_value=True)
    ran = await c.async_run_distributor_cycle(_dist_cfg())
    assert ran is False
    c._dist_open_inlet.assert_not_awaited()  # no switching, no advance


async def test_cycle_rule_b_when_nothing_due():
    c = _loop_host(
        [_mem(1, 1, **{const.ZONE_DURATION: 0}), _mem(2, 2, **{const.ZONE_BUCKET: 5.0})]
    )
    ran = await c.async_run_distributor_cycle(_dist_cfg())
    assert ran is False
    c._dist_open_inlet.assert_not_awaited()


async def test_cycle_full_sweep_waters_due_and_pulses_rest():
    # 3 outlets: outlet 1 & 3 due, outlet 2 not due. Outlet 3 is the LAST due
    # outlet, so the sweep covers all 3 (outlet 2 skip-pulsed to reach 3),
    # 3 windows, credits only for 1 & 3. b12 (physical-position fix): every valve
    # ON->OFF pulse advances the mechanism by one INCLUDING the last outlet's own
    # pulse, so a full-ring sweep books 3 advances (1->2->3->1) and the ring
    # returns home to outlet 1 — matching real hardware, which indexes on the
    # valve OFF edge and thus can never rest on the outlet it just watered.
    members = [
        _mem(1, 1),
        _mem(2, 2, **{const.ZONE_DURATION: 0}),  # not due
        _mem(3, 3),
    ]
    c = _loop_host(members)
    ran = await c.async_run_distributor_cycle(_dist_cfg())
    assert ran is True
    assert c._dist_open_inlet.await_count == 3  # every outlet gets a window
    assert c._dist_advance.await_count == 3  # 1->2->3->1, terminal pulse advances too
    assert c._dist_credit_zone.await_count == 2  # only the two due zones
    # window durations: due -> 60 (ZONE_DURATION), not-due -> 20 (skip pulse)
    windows = [ck.args[1] for ck in c._dist_open_inlet.await_args_list]
    assert windows == [60.0, 20, 60.0]
    c._dist_master_start.assert_awaited_once()
    c._dist_master_end.assert_awaited_once()
    c._dist_clear_cycle.assert_awaited()


async def test_cycle_safety_halt_on_no_flow():
    members = [_mem(1, 1), _mem(2, 2)]
    c = _loop_host(members, confirm_entity="binary_sensor.flow")
    # loop passes confirm_entity from the distributor dict
    c._confirm_valve_running = AsyncMock(return_value=False)  # no flow
    ran = await c.async_run_distributor_cycle(
        _dist_cfg(confirm_entity="binary_sensor.flow")
    )
    assert ran is False
    c._dist_close_inlet.assert_awaited()  # inlet closed defensively
    c._dist_mark_uncertain.assert_awaited_once()  # de-armed + halted
    # halted on the FIRST outlet -> only one window opened
    assert c._dist_open_inlet.await_count == 1


async def test_cycle_starts_at_current_outlet_when_not_home():
    # current_outlet=2 on a 3-outlet ring: physical order is z2, z3, z1.
    members = [_mem(1, 1), _mem(2, 2), _mem(3, 3)]
    c = _loop_host(members)
    ran = await c.async_run_distributor_cycle(_dist_cfg(current_outlet=2))
    assert ran is True
    watered = [ck.args[0][const.ZONE_ID] for ck in c._dist_credit_zone.await_args_list]
    assert watered == [2, 3, 1]  # physical order starting at outlet 2, wrapping
    # the first WATERING persist records the physical start outlet (2), not 1
    # (the very first persist is now the b14 "starting" busy marker; filter to the
    # watering ones).
    watering = [
        ck for ck in c._dist_persist_cycle.await_args_list if ck.args[2] == "watering"
    ]
    assert watering[0].args == (0, 2, "watering")


# --- b14: synchronous single-flight lock + early "starting" busy marker --------


async def test_publishes_starting_marker_first_and_releases_lock():
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    ran = await c.async_run_distributor_cycle(_dist_cfg(current_outlet=2))
    assert ran is True
    # The FIRST persisted marker is the "starting" busy state at the current outlet,
    # published before any watering so the panel gates the other members at once.
    first = c._dist_persist_cycle.await_args_list[0]
    assert first.args == (0, 2, const.DISTRIBUTOR_PHASE_STARTING)
    # lock released after a normal completion
    assert 0 not in c._dist_inflight_ids()


async def test_second_concurrent_cycle_rejected_by_single_flight_lock():
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    started = asyncio.Event()
    release = asyncio.Event()

    async def blocking_members(did):
        started.set()
        await release.wait()  # hold the first cycle mid-run so it keeps the lock
        return [_mem(1, 1), _mem(2, 2)]

    c._dist_members = blocking_members
    t1 = asyncio.ensure_future(c.async_run_distributor_cycle(_dist_cfg()))
    await started.wait()  # first cycle has claimed the distributor
    # A second run scheduled while the first is in-flight must be rejected — no
    # colliding sweep on the shared inlet + position counter.
    ran2 = await c.async_run_distributor_cycle(_dist_cfg())
    assert ran2 is False
    release.set()
    assert await t1 is True
    assert 0 not in c._dist_inflight_ids()  # lock released after completion


async def test_lock_released_when_cycle_returns_early():
    # nothing due -> the sweep returns False, but the lock AND the starting marker
    # must be cleaned up so the distributor is not left stuck "busy".
    c = _loop_host(
        [_mem(1, 1, **{const.ZONE_DURATION: 0}), _mem(2, 2, **{const.ZONE_BUCKET: 5.0})]
    )
    ran = await c.async_run_distributor_cycle(_dist_cfg())
    assert ran is False
    assert 0 not in c._dist_inflight_ids()
    c._dist_clear_cycle.assert_awaited()  # marker cleared on the early return


async def test_cancelled_cycle_preserves_active_cycle_marker():
    # HA shutdown / integration reload cancels the awaited cycle task. The active_cycle
    # marker must be PRESERVED (not cleared) so async_resume_distributor_cycles can act
    # on the interrupted phase on the next setup. The old finally always cleared it,
    # making the boot reconcile a no-op on every graceful restart.
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    c._dist_run_sweep = AsyncMock(side_effect=asyncio.CancelledError())
    with pytest.raises(asyncio.CancelledError):
        await c.async_run_distributor_cycle(_dist_cfg())
    c._dist_clear_cycle.assert_not_awaited()  # marker kept for the boot reconcile
    assert 0 not in c._dist_inflight_ids()  # in-memory single-flight lock released


async def test_normal_cycle_clears_active_cycle_marker():
    # Unchanged: a cycle that completes normally still clears the marker.
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    c._dist_run_sweep = AsyncMock(return_value=True)
    ran = await c.async_run_distributor_cycle(_dist_cfg())
    assert ran is True
    c._dist_clear_cycle.assert_awaited_once_with(0)


async def test_cycle_claim_drops_stale_observed_open_stash():
    # Final-review Issue 1 (2026-07-12): claiming a distributor for an SI cycle must
    # deterministically drop any lingering FOREIGN observed-watering open stash, so a
    # later inlet close edge cannot credit a member off pre-cycle state. Structural
    # guarantee, independent of whether the close-edge race guard wins loop scheduling.
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    c._dist_run_sweep = AsyncMock(return_value=True)
    c._dist_observed_open_map()[0] = {"t": 100.0, "outlet": 1}  # stale foreign stash
    await c.async_run_distributor_cycle(_dist_cfg())
    assert 0 not in c._dist_observed_open_map()


async def test_errored_cycle_clears_active_cycle_marker():
    # Unchanged: an in-process (non-cancel) error still clears the marker -- HA keeps
    # running, so there is no restart to reconcile.
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    c._dist_run_sweep = AsyncMock(side_effect=RuntimeError("boom"))
    with pytest.raises(RuntimeError):
        await c.async_run_distributor_cycle(_dist_cfg())
    c._dist_clear_cycle.assert_awaited_once_with(0)


async def test_cycle_survives_none_pause_and_skip():
    # A distributor persisted with None timings must not crash the cycle.
    members = [_mem(1, 1), _mem(2, 2)]
    c = _loop_host(members)
    ran = await c.async_run_distributor_cycle(
        _dist_cfg(pause_seconds=None, skip_pulse_seconds=None)
    )
    assert ran is True
    c._dist_master_end.assert_awaited_once()  # completed + master cleaned up


async def test_test_run_sweeps_all_outlets_fixed_and_bypasses_confirm_gate():
    members = [_mem(1, 1), _mem(2, 2, **{const.ZONE_DURATION: 0}), _mem(3, 3)]
    # not confirmed, but synced -> a test-run is allowed
    c = _loop_host(members)
    ran = await c.async_run_distributor_test(_dist_cfg(commissioning_confirmed=False))
    assert ran is True
    assert c._dist_open_inlet.await_count == 3  # every outlet
    # b12 (physical-position fix): the sweep visits all 3 outlets AND the last
    # outlet's own pulse advances the ring too, so a full test-run returns home
    # to outlet 1 -> 3 advances (1->2->3->1).
    assert c._dist_advance.await_count == 3
    c._dist_credit_zone.assert_not_awaited()  # test-run never credits
    windows = [ck.args[1] for ck in c._dist_open_inlet.await_args_list]
    assert windows == [const.DISTRIBUTOR_TEST_RUN_SECONDS] * 3


async def test_test_run_still_requires_synced():
    c = _loop_host([_mem(1, 1), _mem(2, 2)])
    ran = await c.async_run_distributor_test(
        _dist_cfg(position_state=const.POSITION_STATE_UNCERTAIN)
    )
    assert ran is False
    c._dist_master_start.assert_not_awaited()


async def test_set_outlet_sets_position_synced():
    c = _CycleHost()
    c.hass = Mock()
    c.hass.data = {}  # I2: _dist_store_update fires the real dispatcher; short-circuit
    c.store = Mock()
    c.store.async_update_distributor = AsyncMock()
    await c.async_distributor_set_outlet(0, 3)
    c.store.async_update_distributor.assert_awaited_once_with(
        0, {"current_outlet": 3, "position_state": const.POSITION_STATE_SYNCED}
    )


async def test_resync_home_sets_outlet_one():
    c = _CycleHost()
    c.hass = Mock()
    c.hass.data = {}  # I2: _dist_store_update fires the real dispatcher; short-circuit
    c.store = Mock()
    c.store.async_update_distributor = AsyncMock()
    await c.async_distributor_resync_home(0)
    c.store.async_update_distributor.assert_awaited_once_with(
        0, {"current_outlet": 1, "position_state": const.POSITION_STATE_SYNCED}
    )


def _recon_host(distributors):
    c = _CycleHost()
    c.store = Mock()
    c.store.async_get_distributors = AsyncMock(return_value=distributors)
    c.store.async_update_distributor = AsyncMock()
    c._dist_close_inlet = AsyncMock()
    c._dist_clear_cycle = AsyncMock()
    c._dist_mark_uncertain = AsyncMock()
    return c


async def test_resume_no_active_cycle_is_noop():
    c = _recon_host([_dist_cfg(**{"active_cycle": {}})])
    await c.async_resume_distributor_cycles()
    c._dist_close_inlet.assert_not_awaited()
    c._dist_mark_uncertain.assert_not_awaited()


async def test_resume_mid_watering_stays_synced_closes_inlet():
    d = _dist_cfg(**{"active_cycle": {"outlet": 2, "phase": "watering"}})
    c = _recon_host([d])
    await c.async_resume_distributor_cycles()
    c._dist_close_inlet.assert_awaited_once()  # defensive close
    c._dist_clear_cycle.assert_awaited_once_with(0)
    c._dist_mark_uncertain.assert_not_awaited()  # position still known


async def test_resume_mid_pausing_marks_uncertain():
    d = _dist_cfg(**{"active_cycle": {"outlet": 2, "phase": "pausing"}})
    c = _recon_host([d])
    await c.async_resume_distributor_cycles()
    c._dist_close_inlet.assert_awaited_once()
    c._dist_clear_cycle.assert_awaited_once_with(0)
    c._dist_mark_uncertain.assert_awaited_once()  # advance completion unknown


# --- E1: early-stop after the last due outlet -----------------------------


async def test_cycle_stops_after_last_due_outlet():
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    for m in (
        "_dist_persist_cycle",
        "_dist_open_inlet",
        "_dist_close_inlet",
        "_dist_credit_zone",
        "_dist_clear_cycle",
    ):
        setattr(c, m, AsyncMock())
    advanced = []
    c._dist_advance = AsyncMock(
        side_effect=lambda did, cur, n: advanced.append((cur % n) + 1)
        or ((cur % n) + 1)
    )
    c._dist_sleep = AsyncMock()
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    members = [
        {
            "id": 10 + i,
            "distributor_id": 0,
            "outlet_number": i + 1,
            "duration": 30 if i < 2 else 0,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        }
        for i in range(6)
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(side_effect=lambda z: (z.get("duration") or 0) > 0)
    credited = []
    c._dist_credit_zone = AsyncMock(
        side_effect=lambda z, w, measured_l=None, planned_seconds=None: credited.append(
            z["outlet_number"]
        )
    )
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1))
    assert credited == [1, 2]
    # b12 (physical-position fix): outlet 2 is the last DUE outlet, so the sweep
    # stops after it (outlets 3-6 never visited), but outlet 2's own pulse still
    # advances the mechanism -> ring ends on outlet 3 (one PAST the last watered
    # outlet), never re-watering 2. Advances: 1->2 (between outlets) then the
    # terminal 2->3 (outlet 2's own OFF-edge step). This is the reported bug: the
    # ring must NOT stay on the just-watered outlet.
    assert advanced == [2, 3]
    assert c._dist_open_inlet.await_count == 2  # only outlets 1,2 visited


async def test_manual_single_target_advances_past_watered_outlet():
    # Live repro (2026-07-05): a manual "irrigate now (X min)" on a member sitting
    # at the CURRENT outlet ran exactly one pulse but left current_outlet unchanged,
    # so the panel + tracked position stayed on the just-watered outlet while the
    # physical ring had already advanced. A single-target force run waters exactly
    # one outlet; that outlet's own OFF-edge advances the mechanism, so the ring
    # must end ONE PAST it (here: water outlet 2 -> ring rests on outlet 3).
    members = [_mem(i + 1, i + 1) for i in range(6)]
    c = _loop_host(members)
    ran = await c.async_run_distributor_cycle(
        _dist_cfg(current_outlet=2),
        force_water=True,
        only_zone_ids=[2],
        duration_override=120.0,
    )
    assert ran is True
    assert c._dist_open_inlet.await_count == 1  # exactly one pulse (outlet 2)
    assert c._dist_open_inlet.await_args.args[1] == 120.0  # custom duration honoured
    # the single terminal advance books outlet 2's own OFF-edge step: 2 -> 3
    assert c._dist_advance.await_count == 1
    assert c._dist_advance.await_args.args == (0, 2, 6)


async def test_cycle_leading_skip_to_reach_later_due():
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    for m in (
        "_dist_persist_cycle",
        "_dist_open_inlet",
        "_dist_close_inlet",
        "_dist_credit_zone",
        "_dist_clear_cycle",
    ):
        setattr(c, m, AsyncMock())
    c._dist_advance = AsyncMock(side_effect=lambda did, cur, n: (cur % n) + 1)
    c._dist_sleep = AsyncMock()
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    members = [
        {
            "id": 10 + i,
            "distributor_id": 0,
            "outlet_number": i + 1,
            "duration": 30 if i == 2 else 0,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        }
        for i in range(6)
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(side_effect=lambda z: (z.get("duration") or 0) > 0)
    credited = []
    c._dist_credit_zone = AsyncMock(
        side_effect=lambda z, w, measured_l=None, planned_seconds=None: credited.append(
            z["outlet_number"]
        )
    )
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1))
    assert credited == [3]
    assert c._dist_open_inlet.await_count == 3  # 1,2 skip-pulsed + 3 watered, then stop


async def test_test_run_still_sweeps_all_outlets():
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    for m in (
        "_dist_persist_cycle",
        "_dist_open_inlet",
        "_dist_close_inlet",
        "_dist_credit_zone",
        "_dist_clear_cycle",
    ):
        setattr(c, m, AsyncMock())
    c._dist_advance = AsyncMock(side_effect=lambda did, cur, n: (cur % n) + 1)
    c._dist_sleep = AsyncMock()
    members = [
        {
            "id": 10 + i,
            "distributor_id": 0,
            "outlet_number": i + 1,
            "duration": 0,
            "state": "automatic",
        }
        for i in range(6)
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1), test_run=True)
    assert c._dist_open_inlet.await_count == 6
