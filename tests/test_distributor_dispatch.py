"""Plan G: scheduled distributor dispatch + shared-master coordination."""

import datetime
from unittest.mock import AsyncMock, Mock

from custom_components.smart_irrigation import const
from tests.test_distributor import _host, _dist


async def test_master_end_defers_to_pending_deadline_not_immediate_off():
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c.async_master_schedule_off = AsyncMock()
    # a concurrent normal-zone run has already claimed the master; its deadline is the
    # snapshot the sweep captured before it started noting (Bug 1, 2026-07-06).
    pre = c._master_now() + datetime.timedelta(seconds=120)
    c._master_off_deadline = pre
    await c._dist_master_end(_dist(), pre_deadline=pre)
    c.hass.services.async_call.assert_not_awaited()
    c.async_master_schedule_off.assert_awaited_once()


async def test_distributor_concurrent_true_for_parallel_or_pending_master():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c._master_off_deadline = None
    assert c._distributor_concurrent() is True  # parallel

    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    c._master_off_deadline = None
    assert c._distributor_concurrent() is False  # solo sequential

    # a normal-zone run already claimed the master -> keep master up
    c._master_off_deadline = c._master_now() + datetime.timedelta(seconds=60)
    assert c._distributor_concurrent() is True  # mixed run


async def test_dispatch_skips_unqualified_distributors():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    c.async_run_distributor_cycle = AsyncMock(return_value=False)
    c._rain_delay_active = Mock(return_value=False)
    c.store.async_get_distributors = AsyncMock(
        return_value=[
            _dist(id=0, position_state=const.POSITION_STATE_UNCERTAIN),
            _dist(id=1, commissioning_confirmed=False),
            _dist(id=2, active_cycle={"outlet": 1, "phase": "watering"}),
            _dist(id=3),  # synced+confirmed but no members
        ]
    )

    async def _members(did):
        return [] if did == 3 else [{"id": 99, "distributor_id": did}]

    c._dist_members = AsyncMock(side_effect=_members)
    c._dist_needs_water = Mock(return_value=True)
    await c._dispatch_distributor_cycles("all")
    c.async_run_distributor_cycle.assert_not_awaited()


async def test_dispatch_runs_due_distributor_with_derived_concurrency():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c._master_off_deadline = None
    c.async_run_distributor_cycle = AsyncMock(return_value=True)
    c._rain_delay_active = Mock(return_value=False)
    d = _dist(id=0)
    c.store.async_get_distributors = AsyncMock(return_value=[d])
    c._dist_members = AsyncMock(return_value=[{"id": 7, "distributor_id": 0}])
    c._dist_needs_water = Mock(return_value=True)
    await c._dispatch_distributor_cycles("all")
    c.async_run_distributor_cycle.assert_awaited_once()
    assert c.async_run_distributor_cycle.await_args.kwargs["concurrent"] is True


async def test_dispatch_respects_target_subset():
    c = _host()
    # zone_sequencing must be set — _dispatch_distributor_cycles calls
    # _distributor_concurrent(), which reads it.
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    c._master_off_deadline = None
    c.async_run_distributor_cycle = AsyncMock(return_value=True)
    c._rain_delay_active = Mock(return_value=False)
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0), _dist(id=1)])

    async def _members(did):
        return [{"id": 7 if did == 0 else 8, "distributor_id": did}]

    c._dist_members = AsyncMock(side_effect=_members)
    c._dist_needs_water = Mock(return_value=True)
    await c._dispatch_distributor_cycles([7])  # only distributor 0 owns zone 7
    assert c.async_run_distributor_cycle.await_count == 1
    assert c.async_run_distributor_cycle.await_args.args[0].get("id") == 0


async def test_dispatch_rain_delay_records_skip_and_runs_nothing():
    c = _host()
    c._rain_delay_active = Mock(return_value=True)
    c._record_skipped_run = AsyncMock()
    c.async_run_distributor_cycle = AsyncMock()
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=[{"id": 10, "distributor_id": 0}])
    await c._dispatch_distributor_cycles("all")
    c.async_run_distributor_cycle.assert_not_awaited()
    c._record_skipped_run.assert_awaited_once_with([10], const.SKIP_REASON_PAUSED)


async def test_dispatch_rain_delay_records_only_member_ids_on_mixed_target():
    c = _host()
    c._rain_delay_active = Mock(return_value=True)
    c._record_skipped_run = AsyncMock()
    c.async_run_distributor_cycle = AsyncMock()
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    # distributor 0 owns members 10 and 11; the schedule also targets normal zone 3
    c._dist_members = AsyncMock(
        return_value=[{"id": 10, "distributor_id": 0}, {"id": 11, "distributor_id": 0}]
    )
    await c._dispatch_distributor_cycles([3, 10, 11])
    c.async_run_distributor_cycle.assert_not_awaited()
    c._record_skipped_run.assert_awaited_once_with([10, 11], const.SKIP_REASON_PAUSED)


async def test_total_duration_uses_distributor_cycle_estimate_not_raw_sum():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 60,
            "state": "automatic",
        },
        {
            "id": 8,
            "distributor_id": 0,
            "outlet_number": 2,
            "duration": 0,
            "state": "automatic",
        },
        {
            "id": 9,
            "distributor_id": 0,
            "outlet_number": 3,
            "duration": 60,
            "state": "automatic",
        },
    ]
    normal = {"id": 1, "distributor_id": None, "duration": 120, "state": "automatic"}
    c.store.async_get_zones = AsyncMock(return_value=members + [normal])
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(return_value=True)  # keep the distributor eligible
    est = c.distributor_cycle_estimate(_dist(id=0), members)  # real formula
    total = await c.get_total_irrigation_duration("all")
    # H2 two-track model: distributor track (int(est) ~530) is dispatched
    # sequentially and the normal zone (120) runs concurrently, so wall-clock is
    # the longer track — here int(est), not 120 + est.
    assert total == max(120, int(est))
    assert total == int(est)  # the distributor track dominates the normal zone
    assert total != 120 + 60 + 0 + 60  # NOT the naive per-member sum


async def test_total_duration_parallel_takes_max_over_distributor_and_zones():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 30,
            "state": "automatic",
        }
    ]
    normal = {"id": 1, "distributor_id": None, "duration": 5, "state": "automatic"}
    c.store.async_get_zones = AsyncMock(return_value=members + [normal])
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(return_value=True)  # keep the distributor eligible
    est = int(c.distributor_cycle_estimate(_dist(id=0), members))
    assert await c.get_total_irrigation_duration("all") == max(5, est)


async def test_member_zone_excluded_from_linked_entity_candidates():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c._rain_delay_active = Mock(return_value=False)
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    c._apply_live_durations = AsyncMock(side_effect=lambda z: z)
    c.async_master_begin_cycle = AsyncMock()
    c.async_master_schedule_off = AsyncMock()
    c._master_note_run = Mock()
    c._irrigate_zones_parallel = AsyncMock()
    c._sc_is_self_closing = Mock(return_value=False)
    member = {
        "id": 7,
        "distributor_id": 0,
        "outlet_number": 1,
        "duration": 30,
        "bucket": -1,
        "bucket_threshold": 0,
        "state": "automatic",
        "linked_entity": "switch.x",
    }
    normal = {
        "id": 1,
        "distributor_id": None,
        "duration": 30,
        "bucket": -1,
        "bucket_threshold": 0,
        "state": "automatic",
        "linked_entity": "switch.y",
    }
    c.store.async_get_zones = AsyncMock(return_value=[member, normal])
    await c._irrigate_linked_entities("all")
    passed = c._irrigate_zones_parallel.await_args.args[0]
    ids = {z["id"] for z in passed}
    assert 7 not in ids and 1 in ids  # member excluded, normal kept


async def test_cycle_notes_sweep_estimate_to_master_deadline():
    """H7: reconciled from H1. H1 asserted ONE upfront full-sweep estimate note;
    H7 replaced that with rolling per-outlet notes. The "a concurrent run's
    deadline covers the sweep" coverage this test guarded now lives in
    test_concurrent_long_window_extends_deadline (long window -> deadline
    extended past it); the "no over-run" behaviour lives in
    test_master_note_is_rolling_not_upfront_estimate. Here we keep a minimal
    end-to-end check that a concurrent run still ARMS the deadline (was None)."""
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c._master_off_deadline = None
    c._master_on = True
    _cycle_mocks(c)
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 600,
                "bucket": -1,
                "bucket_threshold": 0,
                "state": "automatic",
            },
        ]
    )
    c._dist_needs_water = Mock(return_value=True)
    # The real _master_note_run (a pure now+seconds computation) sets the
    # deadline; async_master_schedule_off only arms the HA timer against the
    # loop (covered separately) — stub it so this Mock-hass path can't hit
    # async_call_later, but keep the note-run assertion intact.
    c.async_master_schedule_off = AsyncMock()
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1), concurrent=True)
    # a rolling note armed the deadline during the sweep (the terminal
    # note_run(0) collapses it at the real end -> None-or-now afterwards)
    assert c.async_master_schedule_off.await_count >= 1


def _cycle_mocks(c):
    c._dist_persist_cycle = AsyncMock()
    c._dist_open_inlet = AsyncMock()
    c._dist_close_inlet = AsyncMock()
    c._dist_credit_zone = AsyncMock()
    c._dist_advance = AsyncMock(side_effect=lambda did, cur, n: (cur % n) + 1)
    c._dist_clear_cycle = AsyncMock()
    c._dist_sleep = AsyncMock()
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)


async def test_master_note_is_rolling_not_upfront_estimate():
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    _cycle_mocks(c)
    c._master_note_run = Mock()
    c.async_master_schedule_off = AsyncMock()
    c.distributor_cycle_estimate = Mock(wraps=c.distributor_cycle_estimate)
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 400,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
        {
            "id": 8,
            "distributor_id": 0,
            "outlet_number": 2,
            "duration": 0,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
        {
            "id": 9,
            "distributor_id": 0,
            "outlet_number": 3,
            "duration": 400,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(side_effect=lambda z: (z.get("duration") or 0) > 0)
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1), concurrent=True)
    # rolling: one note per outlet (+ the terminal note_run(0)), never the full-sweep estimate
    noted = [call.args[0] for call in c._master_note_run.call_args_list]
    assert len(noted) >= 3
    full_estimate = c.distributor_cycle_estimate(_dist(id=0), members)
    assert all(v < full_estimate for v in noted)  # no single note is the whole sweep
    # _dist(pause_seconds=120, skip_pulse_seconds=20); settle=10; note formula is
    # window + pause + settle + buffer -> worst note is a watering outlet:
    # 400 + 120 + 10 + BUFFER. (The plan's earlier "+15" bound omitted `pause`;
    # `pause` is REQUIRED so the deadline survives the inter-outlet pause until
    # the next outlet's note is made — see distributor.py rolling-note comment.)
    assert (
        max(noted) <= 400 + 120 + 10 + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS + 1
    )


async def test_concurrent_longer_normal_zone_deadline_wins():
    """User scenario: a parallel normal zone (600s) outlasts a short distributor
    sweep — the master must stay up until the ZONE ends, never cut short by the
    distributor's shorter rolling notes."""
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    _cycle_mocks(c)
    c._master_on = True
    # stub the HA-timer arming (Mock hass can't feed async_call_later a real
    # loop time); the real _master_note_run still runs, which is what we assert.
    c.async_master_schedule_off = AsyncMock()
    start = c._master_now()
    c._master_off_deadline = start + datetime.timedelta(
        seconds=600
    )  # normal zone pending
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 20,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
        {
            "id": 8,
            "distributor_id": 0,
            "outlet_number": 2,
            "duration": 0,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(side_effect=lambda z: (z.get("duration") or 0) > 0)
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1), concurrent=True)
    # the 600s normal-zone deadline is NOT shortened by the distributor's small notes
    remaining = (c._master_off_deadline - c._master_now()).total_seconds()
    assert remaining > 550  # still ~600s, master stays up for the whole zone run


async def test_concurrent_long_window_extends_deadline():
    """Distributor longer than any pending run: rolling notes extend the deadline
    to cover a long watering window (mid-sweep protection preserved). The
    terminal note_run(0) + instant mocked sleeps collapse the post-cycle
    deadline, so spy _master_note_run and assert the max note covered 600s."""
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    _cycle_mocks(c)
    c._master_on = True
    c._master_off_deadline = None
    c._master_note_run = Mock()
    c.async_master_schedule_off = AsyncMock()
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 600,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(return_value=True)
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1), concurrent=True)
    noted = [call.args[0] for call in c._master_note_run.call_args_list]
    assert max(noted) >= 600  # a note covering the full 600s window was made


async def test_solo_run_under_parallel_collapses_master_at_last_valve_close():
    # Bug 1 end-to-end (2026-07-06): a solo real cycle under zone_sequencing=parallel
    # with NO pre-existing external deadline must power the master OFF synchronously at
    # the last valve close (deadline -> None), NOT ride the sweep's rolling
    # over-estimate for ~80 s. Reproduces the live dead-head; the H7 tests miss it
    # because they only assert the rolling notes, not the terminal collapse.
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c._master_off_deadline = None
    c._master_on = True
    _cycle_mocks(c)
    # stub the HA-timer arming (Mock hass has no real loop for async_call_later); the
    # real rolling _master_note_run still runs, and the terminal solo branch is what we
    # assert.
    c.async_master_schedule_off = AsyncMock()
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 60,
                "bucket": -1,
                "bucket_threshold": 0,
                "state": "automatic",
            },
        ]
    )
    c._dist_needs_water = Mock(return_value=True)
    await c.async_run_distributor_cycle(
        _dist(id=0, current_outlet=1),
        concurrent=c._distributor_concurrent(),  # True under parallel — the old trap
    )
    # solo collapse: master physically powered off + deadline cleared
    c.hass.services.async_call.assert_any_await(
        "homeassistant", "turn_off", {"entity_id": "input_boolean.pump"}
    )
    assert c._master_off_deadline is None


async def test_solo_sweep_defers_to_manual_run_started_mid_sweep():
    # End-to-end hardening (2026-07-06, post-review): during a solo sweep a concurrent
    # manual normal-zone run notes a far-future master deadline; the sweep tracks its
    # OWN notes' ceiling (own_deadline) and the terminal must defer to the foreign
    # deadline, NOT hard-cut the manual run's pump.
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c._master_off_deadline = None
    c._master_on = True
    _cycle_mocks(c)
    c.async_master_schedule_off = AsyncMock()
    c._master_turn = AsyncMock()
    # a concurrent manual run claims the master mid-sweep (during the watering window):
    far = c._master_now() + datetime.timedelta(seconds=3600)

    def _sleep_then_foreign(_seconds):
        # sync side_effect (AsyncMock runs it) -> reliably sets the foreign deadline
        c._master_off_deadline = far

    c._dist_sleep = AsyncMock(side_effect=_sleep_then_foreign)
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 60,
                "bucket": -1,
                "bucket_threshold": 0,
                "state": "automatic",
            },
        ]
    )
    c._dist_needs_water = Mock(return_value=True)
    await c.async_run_distributor_cycle(
        _dist(id=0, current_outlet=1),
        concurrent=c._distributor_concurrent(),
    )
    # the foreign consumer's deadline is honored; the master is NOT hard-cut
    c._master_turn.assert_not_awaited()
    assert c._master_off_deadline == far


async def test_master_end_finalizes_synchronously_when_solo():
    # Bug 1 (2026-07-06): pre_deadline None -> no genuine concurrent consumer ->
    # synchronous shutdown at the last valve close, collapsing the sweep's inflated
    # rolling deadline to None. (Was the concurrent=False path; now keyed on the snapshot.)
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c._master_on = True
    c._master_off_deadline = c._master_now() + datetime.timedelta(seconds=999)
    c._master_turn = AsyncMock()
    await c._dist_master_end(_dist(id=0), pre_deadline=None)
    c._master_turn.assert_awaited_once_with(False)
    assert c._master_on is False
    assert c._master_off_deadline is None


async def test_master_end_defers_when_concurrent():
    # Bug 1 (2026-07-06): a real external deadline pre-existed the sweep (a concurrent
    # normal-zone run) -> defer, collapsing our inflated rolling note back to that
    # external floor (never powering the master off).
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c._master_on = True
    now = c._master_now()
    pre = now + datetime.timedelta(seconds=120)  # the external floor (snapshot)
    c._master_off_deadline = now + datetime.timedelta(seconds=300)  # inflated rolling
    c._master_turn = AsyncMock()
    c.async_master_schedule_off = AsyncMock()
    await c._dist_master_end(_dist(id=0), pre_deadline=pre)
    c._master_turn.assert_not_awaited()
    c.async_master_schedule_off.assert_awaited_once()
    assert c._master_on is True
    assert c._master_off_deadline == pre  # collapsed to the external floor


async def test_master_end_defers_to_foreign_mid_sweep_note_even_when_solo():
    # Hardening (2026-07-06, post-review): pre_deadline None (solo) BUT a foreign note
    # during the sweep pushed _master_off_deadline BEYOND our own notes' ceiling
    # (own_deadline) -> a concurrent manual run appeared mid-sweep; defer to it instead
    # of hard-cutting its pump.
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c._master_on = True
    now = c._master_now()
    own = now + datetime.timedelta(seconds=180)  # our own rolling-note ceiling
    foreign = now + datetime.timedelta(
        seconds=500
    )  # a manual run noted later mid-sweep
    c._master_off_deadline = foreign
    c._master_turn = AsyncMock()
    c.async_master_schedule_off = AsyncMock()
    await c._dist_master_end(_dist(id=0), pre_deadline=None, own_deadline=own)
    c._master_turn.assert_not_awaited()  # NOT hard-cut
    c.async_master_schedule_off.assert_awaited_once()
    assert c._master_off_deadline == foreign  # deferred to the foreign run's deadline
    assert c._master_on is True


async def test_master_end_collapses_when_deadline_is_only_our_own_notes():
    # Hardening: solo, no foreign consumer -> _master_off_deadline == our own ceiling
    # -> collapse synchronously (Bug 1 behaviour preserved, not a false defer).
    c = _host(master_entity="input_boolean.pump", master_off_after=True)
    c._master_on = True
    now = c._master_now()
    own = now + datetime.timedelta(seconds=180)
    c._master_off_deadline = own
    c._master_turn = AsyncMock()
    await c._dist_master_end(_dist(id=0), pre_deadline=None, own_deadline=own)
    c._master_turn.assert_awaited_once_with(False)
    assert c._master_off_deadline is None


async def test_dispatch_recomputes_concurrent_per_distributor():
    c = _host()
    c._rain_delay_active = Mock(return_value=False)
    seen = []

    async def _run(
        dist,
        *,
        concurrent=False,
        only_zone_ids=None,
        duration_override=None,
        force_water=False,
    ):
        seen.append(concurrent)
        return True

    c.async_run_distributor_cycle = AsyncMock(side_effect=_run)
    c._distributor_concurrent = Mock(side_effect=[True, False])
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0), _dist(id=1)])
    c._dist_members = AsyncMock(
        side_effect=lambda did: [{"id": 10 + did, "distributor_id": did}]
    )
    c._dist_needs_water = Mock(return_value=True)
    await c._dispatch_distributor_cycles("all")
    assert seen == [True, False]


async def test_estimate_skips_unsynced_distributor():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 60,
            "state": "automatic",
        }
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    c.store.async_get_distributors = AsyncMock(
        return_value=[_dist(id=0, position_state=const.POSITION_STATE_UNCERTAIN)]
    )
    c._dist_members = AsyncMock(return_value=members)
    c._dist_needs_water = Mock(return_value=True)
    assert await c.get_total_irrigation_duration("all") == 0


async def test_estimate_distributor_track_sums_even_in_parallel():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    m0 = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 30,
            "state": "automatic",
        }
    ]
    m1 = [
        {
            "id": 8,
            "distributor_id": 1,
            "outlet_number": 1,
            "duration": 30,
            "state": "automatic",
        }
    ]
    c.store.async_get_zones = AsyncMock(return_value=m0 + m1)
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0), _dist(id=1)])
    c._dist_members = AsyncMock(side_effect=lambda did: m0 if did == 0 else m1)
    c._dist_needs_water = Mock(return_value=True)
    e0 = int(c.distributor_cycle_estimate(_dist(id=0), m0))
    e1 = int(c.distributor_cycle_estimate(_dist(id=1), m1))
    assert await c.get_total_irrigation_duration("all") == e0 + e1


async def test_irrigate_now_dispatches_distributor_for_member_only():
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c._sc_is_self_closing = Mock(return_value=False)
    c._dispatch_distributor_cycles = AsyncMock()
    member = {
        "id": 7,
        "distributor_id": 0,
        "outlet_number": 1,
        "duration": 30,
        "bucket": -1,
        "bucket_threshold": 0,
        "state": "automatic",
    }
    c.store.async_get_zones = AsyncMock(return_value=[member])
    await c.async_irrigate_now()  # general "water all"
    c._dispatch_distributor_cycles.assert_awaited_once_with("all")


async def test_irrigate_now_member_not_driven_as_linked_entity():
    """A member with a stray linked_entity is NOT run directly (review #9)."""
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c._sc_is_self_closing = Mock(return_value=False)
    c._dispatch_distributor_cycles = AsyncMock()
    c._irrigate_zones_parallel = AsyncMock()
    c.async_master_begin_cycle = AsyncMock()
    c.async_master_schedule_off = AsyncMock()
    c._master_note_run = Mock()
    member = {
        "id": 7,
        "distributor_id": 0,
        "duration": 30,
        "state": "automatic",
        "linked_entity": "switch.stray",
    }
    c.store.async_get_zones = AsyncMock(return_value=[member])
    await c.async_irrigate_now()
    c._irrigate_zones_parallel.assert_not_awaited()  # excluded from direct drive
    c._dispatch_distributor_cycles.assert_awaited_once_with("all")


async def test_run_zone_routes_member_to_distributor():
    c = _host()
    c._dispatch_distributor_cycles = AsyncMock()
    c._sc_is_self_closing = Mock(return_value=False)
    member = {"id": 7, "distributor_id": 0, "duration": 30, "state": "automatic"}
    c.store.get_zone = Mock(return_value=member)  # SYNC lookup
    # M-BE: idle distributor -> the manual run is routed through the ring with the
    # requested custom duration passed as duration_override (2 min -> 120s), not the
    # member's stored 30s daily duration.
    c.store.get_distributor = Mock(return_value=_dist(id=0, active_cycle=None))
    await c.async_run_zone(7, 2)  # 2 minutes
    c._dispatch_distributor_cycles.assert_awaited_once_with(
        [7], duration_override=120.0
    )


async def test_run_zone_member_rejected_when_distributor_busy():
    """M-BE single-flight: a manual member run is ignored while the distributor
    already has a cycle in progress (mutual exclusion on the shared inlet)."""
    c = _host()
    c._dispatch_distributor_cycles = AsyncMock()
    c._sc_is_self_closing = Mock(return_value=False)
    member = {"id": 7, "distributor_id": 0, "duration": 30, "state": "automatic"}
    c.store.get_zone = Mock(return_value=member)  # SYNC lookup
    c.store.get_distributor = Mock(
        return_value=_dist(id=0, active_cycle={"outlet": 1, "phase": "watering"})
    )
    await c.async_run_zone(7, 2)
    c._dispatch_distributor_cycles.assert_not_awaited()


async def test_cycle_only_zone_ids_waters_only_targeted_members():
    c = _host()
    c._dist_uses_master = Mock(return_value=False)  # bypass master entirely
    c._dist_persist_cycle = AsyncMock()
    c._dist_open_inlet = AsyncMock()
    c._dist_close_inlet = AsyncMock()
    c._dist_credit_zone = AsyncMock()
    c._dist_advance = AsyncMock(side_effect=lambda did, cur, n: (cur % n) + 1)
    c._dist_clear_cycle = AsyncMock()
    c._dist_sleep = AsyncMock()
    c._dist_needs_water = Mock(return_value=True)
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    members = [
        {
            "id": 10,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 30,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
        {
            "id": 11,
            "distributor_id": 0,
            "outlet_number": 2,
            "duration": 30,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
        {
            "id": 12,
            "distributor_id": 0,
            "outlet_number": 3,
            "duration": 30,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        },
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    ran = await c.async_run_distributor_cycle(
        _dist(id=0, current_outlet=1), only_zone_ids=[10]
    )
    assert ran is True
    credited = {call.args[0].get("id") for call in c._dist_credit_zone.await_args_list}
    assert credited == {10}  # only the targeted member watered


def _soil_members():
    return [
        {
            "id": 10 + i,
            "distributor_id": 0,
            "outlet_number": i + 1,
            "duration": 30,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        }
        for i in range(3)
    ]


def _soil_cycle_host():
    c = _host()
    c._dist_uses_master = Mock(return_value=False)  # bypass master entirely
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
    return c


async def test_soil_veto_scoped_to_target_subset():
    # Soil-veto scope (2026-07-06): a subset-targeted cycle must NOT pass a
    # non-targeted member to the veto — a wet member outside the target is left
    # untouched (re-anchored on its OWN cycle).
    c = _soil_cycle_host()
    c._dist_needs_water = Mock(return_value=True)  # all due
    seen = {}

    async def _veto(zs):
        seen["ids"] = [z.get("id") for z in zs]
        return zs  # dry -> all survive

    c._apply_soil_moisture_veto = _veto
    c.store.async_get_zones = AsyncMock(return_value=_soil_members())
    await c.async_run_distributor_cycle(
        _dist(id=0, current_outlet=1), only_zone_ids=[10]
    )
    assert seen["ids"] == [
        10
    ]  # only the targeted member reached the veto; 11,12 untouched


async def test_soil_veto_skips_non_due_members():
    # Non-due members are not passed to the veto (matching the normal-zone path,
    # which vetoes only due zones) -> a non-due wet member is not re-anchored.
    c = _soil_cycle_host()
    c._dist_needs_water = Mock(side_effect=lambda z: z.get("id") == 10)  # only 10 due
    seen = {}

    async def _veto(zs):
        seen["ids"] = [z.get("id") for z in zs]
        return zs

    c._apply_soil_moisture_veto = _veto
    c.store.async_get_zones = AsyncMock(return_value=_soil_members())
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1))
    assert seen["ids"] == [10]  # non-due members 11,12 never reach the veto


async def test_soil_veto_drops_wet_targeted_member():
    # A targeted+due+WET member is vetoed: the veto drops it, so it isn't watered
    # (behaviour preserved through the reorder).
    c = _soil_cycle_host()
    c._dist_needs_water = Mock(return_value=True)

    async def _veto(zs):
        return [z for z in zs if z.get("id") != 11]  # member 11 is wet -> dropped

    c._apply_soil_moisture_veto = _veto
    c.store.async_get_zones = AsyncMock(return_value=_soil_members())
    ran = await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1))
    assert ran is True
    credited = {call.args[0].get("id") for call in c._dist_credit_zone.await_args_list}
    assert 11 not in credited  # wet member not watered
    assert credited == {10, 12}  # the dry targeted members watered


async def test_dispatch_propagates_concurrent_false_for_solo_sequential():
    """H6 (review #13): the derived concurrent=False actually reaches the cycle.

    Distinct from test_dispatch_runs_due_distributor_with_derived_concurrency,
    which locks the PARALLEL->True direction. A solo sequential run (no pending
    master overlap) derives False; this proves that False is forwarded to
    async_run_distributor_cycle rather than defaulting/being dropped.
    """
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    c._master_off_deadline = None  # no pending overlap -> solo
    c._rain_delay_active = Mock(return_value=False)
    c.async_run_distributor_cycle = AsyncMock(return_value=True)
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=[{"id": 7, "distributor_id": 0}])
    c._dist_needs_water = Mock(return_value=True)
    await c._dispatch_distributor_cycles("all")
    c.async_run_distributor_cycle.assert_awaited_once()
    assert c.async_run_distributor_cycle.await_args.kwargs["concurrent"] is False


async def test_estimate_member_raw_duration_never_counted_in_normal_track():
    """H6 (review #14): a member's raw duration must NOT land in the normal track.

    The plan's original "naive-sum guard on the parallel test" is INEFFECTIVE
    under H2's two-track model: the distributor estimate always dominates
    max(), so deleting skip_conditions.py's member-exclusion
    (``if zone.get(const.ZONE_DISTRIBUTOR_ID) is not None: continue``) is
    invisible to a parallel-max test AND to the existing sequential test. To
    ACTUALLY lock member-exclusion, use a SEQUENTIAL case with a LARGE normal
    zone so the normal track dominates; then the erroneously-added member raw
    duration would tip the total. This test FAILS if that ``continue`` is
    removed.
    """
    c = _host()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    big_normal = {
        "id": 1,
        "distributor_id": None,
        "duration": 10000,
        "state": "automatic",
    }
    member = {
        "id": 7,
        "distributor_id": 0,
        "outlet_number": 1,
        "duration": 30,
        "state": "automatic",
    }
    c.store.async_get_zones = AsyncMock(return_value=[big_normal, member])
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=[member])
    c._dist_needs_water = Mock(return_value=True)
    est = int(c.distributor_cycle_estimate(_dist(id=0), [member]))
    # normal track (10000) dominates the distributor track; the member's raw 30
    # must NOT be added to the normal track. total == max(10000, est) == 10000.
    total = await c.get_total_irrigation_duration("all")
    assert total == max(10000, est)
    assert total == 10000  # est << 10000; member raw 30 not double-counted


async def test_dispatch_passes_duration_override():
    c = _host()
    # _dispatch_distributor_cycles calls _distributor_concurrent(), which reads
    # zone_sequencing off store.config; stub it so the real dispatcher runs.
    c._distributor_concurrent = Mock(return_value=False)
    c._rain_delay_active = Mock(return_value=False)
    seen = {}

    async def _run(
        dist,
        *,
        concurrent=False,
        only_zone_ids=None,
        duration_override=None,
        force_water=False,
    ):
        seen["dur"] = duration_override
        seen["only"] = only_zone_ids
        seen["force"] = force_water
        return True

    c.async_run_distributor_cycle = AsyncMock(side_effect=_run)
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=[{"id": 7, "distributor_id": 0}])
    c._dist_needs_water = Mock(return_value=True)
    await c._dispatch_distributor_cycles([7], duration_override=120.0)
    assert seen["dur"] == 120.0 and seen["only"] == [7]
    # b10: a duration_override run is a manual run -> force_water propagates True.
    assert seen["force"] is True


async def test_cycle_duration_override_sets_target_window():
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
    windows = []
    c._dist_sleep = AsyncMock(side_effect=lambda s: windows.append(s))
    c._dist_needs_water = Mock(return_value=True)
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 30,
            "bucket": -1,
            "bucket_threshold": 0,
            "state": "automatic",
        }
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    await c.async_run_distributor_cycle(
        _dist(id=0, current_outlet=1), only_zone_ids=[7], duration_override=200.0
    )
    assert 200.0 in windows  # target outlet watered for the override, not 30


async def test_estimate_truncates_to_last_due_outlet():
    """E2: the finish-anchor estimate must follow the early-stop sweep (E1) — order
    members from current_outlet, count only THROUGH the last due outlet. Leading
    non-due outlets are skip-pulsed; trailing ones are never visited, so a fully-due
    ring costs strictly more than a sweep that stops early."""
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    # 6 members, only outlets 1 & 2 due (dur 30); 3-6 not due (dur 0)
    members = [
        {
            "id": 10 + i,
            "distributor_id": 0,
            "outlet_number": i + 1,
            "duration": 30 if i < 2 else 0,
        }
        for i in range(6)
    ]
    est = c.distributor_cycle_estimate(_dist(id=0, current_outlet=1), members)
    # _dist fixture: pause_seconds=120 (>= floor 10). Only outlets 1,2 swept:
    # windows 30+30, pauses = (k-1)=1, no settle (uses_master False), + buffer.
    pause = max(120, const.DISTRIBUTOR_MIN_PAUSE_SECONDS)  # == 120
    expected = 30 + 30 + 1 * pause + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS
    assert est == expected
    # and it must be strictly less than counting all 6 outlets (trailing skips + pauses)
    all_due = [{**m, "duration": 30} for m in members]
    assert est < c.distributor_cycle_estimate(_dist(id=0, current_outlet=1), all_due)


async def test_estimate_zero_when_none_due():
    """E2: no due outlet anywhere in the ring -> nothing is swept -> 0.0."""
    c = _host()
    members = [
        {"id": 10 + i, "distributor_id": 0, "outlet_number": i + 1, "duration": 0}
        for i in range(3)
    ]
    assert c.distributor_cycle_estimate(_dist(id=0, current_outlet=1), members) == 0.0


async def test_foreign_pulse_advances_when_idle():
    c = _host()
    c.store.get_distributor = Mock(
        return_value={
            "id": 0,
            "current_outlet": 2,
            "active_cycle": {},
            "position_state": "synced",
            "watch_mode": "count",
        }
    )
    c._dist_members = AsyncMock(return_value=[{"id": i} for i in range(6)])  # n=6
    c._dist_store_update = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    c._dist_store_update.assert_awaited_once()
    args = c._dist_store_update.await_args.args
    assert args[0] == 0 and args[1]["current_outlet"] == 3  # 2 -> 3


async def test_own_pulse_ignored_during_cycle():
    c = _host()
    c.store.get_distributor = Mock(
        return_value={
            "id": 0,
            "current_outlet": 2,
            "active_cycle": {"outlet": 2, "phase": "watering"},
        }
    )
    c._dist_store_update = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    c._dist_store_update.assert_not_awaited()


async def test_foreign_pulse_wraps_at_n():
    c = _host()
    c.store.get_distributor = Mock(
        return_value={
            "id": 0,
            "current_outlet": 6,
            "active_cycle": {},
            "position_state": "synced",
            "watch_mode": "count",
        }
    )
    c._dist_members = AsyncMock(return_value=[{"id": i} for i in range(6)])
    c._dist_store_update = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    assert c._dist_store_update.await_args.args[1]["current_outlet"] == 1  # 6 -> 1


async def test_foreign_pulse_ignored_no_members():
    c = _host()
    c.store.get_distributor = Mock(
        return_value={
            "id": 0,
            "current_outlet": 1,
            "active_cycle": {},
            "watch_mode": "count",
        }
    )
    c._dist_members = AsyncMock(return_value=[])
    c._dist_store_update = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    c._dist_store_update.assert_not_awaited()


async def test_inlet_watch_registers_listener_unless_ignore(monkeypatch):
    # watch_mode != ignore + inlet_entity set -> a listener is registered (both modes).
    c = _host()
    calls = []
    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.async_track_state_change_event",
        lambda hass, entities, handler: calls.append(entities) or (lambda: None),
    )
    c._dist_refresh_inlet_watch(
        _dist(id=0, inlet_entity="switch.inlet", watch_mode="count")
    )
    c._dist_refresh_inlet_watch(
        _dist(
            id=1,
            watering_mode=const.WATERING_MODE_SERVICE,
            inlet_entity="switch.ring",
            watch_mode="warn",
        )
    )
    c._dist_refresh_inlet_watch(
        _dist(id=2, inlet_entity="switch.inlet", watch_mode="ignore")
    )
    assert calls == [["switch.inlet"], ["switch.ring"]]


async def test_inlet_pulse_count_advances_position():
    c = _host()
    c.store.get_distributor = Mock(
        return_value=_dist(id=0, current_outlet=1, watch_mode="count")
    )
    c._dist_members = AsyncMock(return_value=[{"id": 1}, {"id": 2}, {"id": 3}])
    c._dist_store_update = AsyncMock()
    c._dist_mark_uncertain = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    c._dist_store_update.assert_awaited_once_with(0, {"current_outlet": 2})
    c._dist_mark_uncertain.assert_not_awaited()


async def test_inlet_pulse_warn_marks_uncertain_without_advancing():
    c = _host()
    d = _dist(id=0, current_outlet=1, watch_mode="warn")
    c.store.get_distributor = Mock(return_value=d)
    c._dist_members = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
    c._dist_store_update = AsyncMock()
    c._dist_mark_uncertain = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    c._dist_mark_uncertain.assert_awaited_once()
    assert (
        c._dist_mark_uncertain.await_args.kwargs.get("reason")
        == const.DISTRIBUTOR_REASON_FOREIGN_PULSE
    )
    c._dist_store_update.assert_not_awaited()


async def test_inlet_pulse_ignored_during_active_cycle():
    c = _host()
    c.store.get_distributor = Mock(
        return_value=_dist(id=0, watch_mode="warn", active_cycle={"outlet": 1})
    )
    c._dist_store_update = AsyncMock()
    c._dist_mark_uncertain = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    c._dist_store_update.assert_not_awaited()
    c._dist_mark_uncertain.assert_not_awaited()


async def test_estimate_models_full_ring_for_subset_target():
    """Review I-1: a schedule targeting only a LATE outlet must estimate the full
    physical sweep the cycle actually runs — the leading non-targeted outlets are
    skip-pulsed to reach the target, with a pause after each. Passing a
    target-compacted subset to the estimate (as before) dropped those skips+pauses
    and under-estimated the sweep, pushing a finish-anchored start too late."""
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    # 4 outlets, current=1, target ONLY outlet 4 (id 13). Real sweep skip-pulses
    # outlets 1,2,3 to reach 4 -> 3*skip + window(outlet4) + 3 pauses + buffer.
    members = [
        {"id": 10 + i, "distributor_id": 0, "outlet_number": i + 1, "duration": 30}
        for i in range(4)
    ]
    est = c.distributor_cycle_estimate(
        _dist(id=0, current_outlet=1), members, only_zone_ids=[13]
    )  # outlet 4 = id 13
    skip = 20
    pause = 120
    expected = 3 * skip + 30 + 3 * pause + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS
    assert est == expected


async def test_estimate_full_ring_all_targets_unchanged():
    """Review I-1: the no-only_zone_ids path (all due outlets, full ring) must be
    unchanged from E2 — early-stop after the last due outlet, no extra pauses."""
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    members = [
        {
            "id": 10 + i,
            "distributor_id": 0,
            "outlet_number": i + 1,
            "duration": 30 if i < 2 else 0,
        }
        for i in range(4)
    ]
    # no target -> early-stop after last due (outlet 2): same as before E6
    est = c.distributor_cycle_estimate(_dist(id=0, current_outlet=1), members)
    pause = 120
    assert est == 30 + 30 + 1 * pause + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS


async def test_manual_run_waters_non_due_member():
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
    c._dist_needs_water = Mock(return_value=False)  # NOT due
    c._apply_soil_moisture_veto = AsyncMock(side_effect=lambda z: z)
    members = [
        {
            "id": 7,
            "distributor_id": 0,
            "outlet_number": 1,
            "duration": 0,
            "bucket": 5,
            "bucket_threshold": 0,
            "state": "automatic",
        }
    ]
    c.store.async_get_zones = AsyncMock(return_value=members)
    credited = []
    c._dist_credit_zone = AsyncMock(
        side_effect=lambda z, w, measured_l=None, planned_seconds=None: credited.append(
            z["id"]
        )
    )
    ran = await c.async_run_distributor_cycle(
        _dist(id=0, current_outlet=1),
        only_zone_ids=[7],
        duration_override=60.0,
        force_water=True,
    )
    assert ran is True
    assert c._dist_open_inlet.await_count == 1  # the outlet actually opened
    assert credited == [7]  # watered despite not being due


async def test_dispatch_manual_bypasses_due_gate():
    c = _host()
    # _dispatch_distributor_cycles computes concurrent=self._distributor_concurrent(),
    # which reads store.config.zone_sequencing (sibling dispatch tests set it too).
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    c._master_off_deadline = None
    c._rain_delay_active = Mock(return_value=False)
    seen = {}

    async def _run(
        dist,
        *,
        concurrent=False,
        only_zone_ids=None,
        duration_override=None,
        force_water=False,
    ):
        seen["force"] = force_water
        return True

    c.async_run_distributor_cycle = AsyncMock(side_effect=_run)
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=[{"id": 7, "distributor_id": 0}])
    c._dist_needs_water = Mock(return_value=False)  # NOTHING due
    await c._dispatch_distributor_cycles([7], duration_override=60.0)
    c.async_run_distributor_cycle.assert_awaited_once()  # dispatched anyway (manual)
    assert seen["force"] is True


async def test_scheduled_run_still_due_gated():
    c = _host()
    c._rain_delay_active = Mock(return_value=False)
    c.async_run_distributor_cycle = AsyncMock(return_value=True)
    c.store.async_get_distributors = AsyncMock(return_value=[_dist(id=0)])
    c._dist_members = AsyncMock(return_value=[{"id": 7, "distributor_id": 0}])
    c._dist_needs_water = Mock(return_value=False)  # nothing due
    await c._dispatch_distributor_cycles("all")  # scheduled (no override)
    c.async_run_distributor_cycle.assert_not_awaited()  # still skipped


async def test_sweep_credits_measured_flow_volume():
    """Phase 4 Part A wiring: the sweep's per-outlet window measurement
    (_dist_measure_window) must reach _dist_credit_zone as measured_l, so a
    flow-metered distributor credits real litres instead of the time estimate."""
    c = _host()
    c._dist_uses_master = Mock(return_value=False)  # bypass master entirely
    _cycle_mocks(c)
    c._dist_needs_water = Mock(return_value=True)
    # measure returns 9.0 L for the single watered outlet
    c._dist_measure_window = AsyncMock(return_value=(9.0, 60, False))
    credited = {}
    c._dist_credit_zone = AsyncMock(
        side_effect=lambda z, s, measured_l=None, planned_seconds=None: credited.update(
            v=measured_l
        )
    )
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 60,
                "bucket": -1,
                "bucket_threshold": 0,
                "state": "automatic",
            }
        ]
    )
    await c.async_run_distributor_cycle(_dist(id=0, current_outlet=1))
    assert credited["v"] == 9.0  # the measured volume reached crediting


async def test_sweep_classic_passes_target_and_extend_cap():
    """Phase 4 Part B wiring: a classic outlet with a positive volume target gets
    the target passed through to _dist_measure_window AND an extend cap == the
    zone's safety maximum_duration (classic may run past the nominal window to
    reach the target); crediting books the actual elapsed seconds against the
    planned window."""
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    _cycle_mocks(c)
    c._dist_needs_water = Mock(return_value=True)
    c._zone_target_bucket = Mock(return_value=0.0)
    c._metered_target_volume = Mock(return_value=12.0)  # positive target
    seen = {}

    async def _fake_measure(distributor, window, *, cap=None, target=None):
        seen["window"] = window
        seen["cap"] = cap
        seen["target"] = target
        return 12.0, window, True

    c._dist_measure_window = _fake_measure
    credited = {}
    c._dist_credit_zone = AsyncMock(
        side_effect=lambda z, s, measured_l=None, planned_seconds=None: credited.update(
            seconds=s, measured=measured_l, planned=planned_seconds
        )
    )
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 60,
                "maximum_duration": 900,
                "bucket": -3,
                "bucket_threshold": 0,
                "state": "automatic",
            }
        ]
    )
    await c.async_run_distributor_cycle(
        _dist(
            id=0,
            current_outlet=1,
            watering_mode=const.WATERING_MODE_CLASSIC,
            flow_sensor="sensor.inlet_flow",
        )
    )
    assert seen["target"] == 12.0
    assert seen["cap"] == 900  # classic extend cap == maximum_duration
    assert credited["measured"] == 12.0
    assert credited["planned"] == 60  # planned == the window


async def test_sweep_self_closing_target_no_extend():
    """A self-closing (service) outlet with a stop_service still gets a volume
    target, but the cap stays at the window — extension past the nominal window
    is impossible on a self-closing valve."""
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    _cycle_mocks(c)
    c._dist_needs_water = Mock(return_value=True)
    c._zone_target_bucket = Mock(return_value=0.0)
    c._metered_target_volume = Mock(return_value=8.0)
    seen = {}

    async def _fake_measure(distributor, window, *, cap=None, target=None):
        seen["cap"] = cap
        seen["target"] = target
        return 8.0, window, True

    c._dist_measure_window = _fake_measure
    c._dist_credit_zone = AsyncMock()
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 60,
                "maximum_duration": 900,
                "bucket": -3,
                "bucket_threshold": 0,
                "state": "automatic",
            }
        ]
    )
    await c.async_run_distributor_cycle(
        _dist(
            id=0,
            current_outlet=1,
            watering_mode=const.WATERING_MODE_SERVICE,
            stop_service="script.off",
            flow_sensor="sensor.inlet_flow",
        )
    )
    assert seen["target"] == 8.0
    assert seen["cap"] == 60  # self-closing: no extension, cap == window


async def test_sweep_no_flow_sensor_no_target():
    """No flow_sensor configured -> no metering -> no early stop; target stays
    None and cap stays at the window regardless of watering mode."""
    c = _host()
    c._dist_uses_master = Mock(return_value=False)
    _cycle_mocks(c)
    c._dist_needs_water = Mock(return_value=True)
    c._zone_target_bucket = Mock(return_value=0.0)
    c._metered_target_volume = Mock(return_value=8.0)
    seen = {}

    async def _fake_measure(distributor, window, *, cap=None, target=None):
        seen["cap"] = cap
        seen["target"] = target
        return None, window, False

    c._dist_measure_window = _fake_measure
    c._dist_credit_zone = AsyncMock()
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 60,
                "maximum_duration": 900,
                "bucket": -3,
                "bucket_threshold": 0,
                "state": "automatic",
            }
        ]
    )
    await c.async_run_distributor_cycle(
        _dist(
            id=0,
            current_outlet=1,
            watering_mode=const.WATERING_MODE_CLASSIC,
            flow_sensor=None,
        )
    )
    assert seen["target"] is None  # no meter -> no early stop
    assert seen["cap"] == 60  # cap == window
