"""Self-closing valve mode (Phase 1)."""

import itertools
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.irrigation import SI_VALVE_SUPPRESS_MARGIN


def _coord():
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.hass.services.async_call = AsyncMock()
    c.hass.bus.async_fire = Mock()
    # A CONFIRMED service run now subscribes to its confirm_entity for the rest of
    # the run (issue #88), and HA's state tracker indexes into hass.data — which a
    # bare Mock is not. Same reason the distributor host gives it a real dict.
    c.hass.data = {}
    # No state machine in this host. `None` is the one answer the watcher reads as
    # "no information" and leaves the run alone; a bare Mock state is neither on
    # nor off, and would settle every confirmed run the instant it was armed.
    # Tests that need a real state (the flow sampler's) override this.
    c.hass.states.get = Mock(return_value=None)
    c.store = Mock()
    # The config STUB round-trips, so _sc_add_run -> _sc_find_run actually works.
    # A run that cannot be read back is not a smaller double, it is a different
    # program: _watch_policy resolves a run's mode from its record, so a record
    # that vanishes resolves to the fallback policy instead of the mode's own.
    c._cfg = {}
    c.store.async_get_config = AsyncMock(side_effect=lambda: dict(c._cfg))
    c.store.async_update_zone = AsyncMock()
    c.store.async_update_config = AsyncMock(side_effect=c._cfg.update)
    # isolate the run-log helper (its own behaviour is tested elsewhere)
    c._record_run = AsyncMock()
    # isolate the cleanup timer (thin wrapper around HA async_call_later)
    c._sc_schedule_cleanup = Mock()
    return c


def _zone(**kw):
    z = {
        const.ZONE_ID: 2,
        const.ZONE_NAME: "Beet",
        const.ZONE_DURATION: 600.0,  # seconds (matches _run_valve_metered)
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        const.ZONE_RUN_SERVICE: "script.irrigation_beet",
        const.ZONE_DURATION_FIELD: "dauer",
        const.ZONE_DURATION_UNIT: const.DURATION_UNIT_MINUTES,
    }
    z.update(kw)
    return z


_REPORT_EPOCH = datetime(2026, 9, 27, 10, 0, 0, tzinfo=timezone.utc)
_report_seq = itertools.count()


def _flow_state(value, unit="L", reported=None):
    """A fake HA state for a flow sensor: value, unit, and when it last REPORTED.

    ``last_reported`` advances for every state built here, because a sensor
    sending a value is exactly what makes HA write a new State. A test that keeps
    ONE object and hands it back on every poll therefore models a sensor that has
    gone quiet — which is a different thing from a sensor reporting zero, and the
    difference decides whether a run may be written off as dry.
    """
    st = Mock()
    st.state = str(value)
    st.attributes = {"unit_of_measurement": unit}
    st.last_reported = (
        _REPORT_EPOCH + timedelta(seconds=next(_report_seq))
        if reported is None
        else reported
    )
    return st


def test_convert_duration_minutes_rounds_up_sub_minute():
    c = _coord()
    assert c._sc_convert(600.0, const.DURATION_UNIT_SECONDS) == 600
    assert c._sc_convert(600.0, const.DURATION_UNIT_MINUTES) == 10
    # sub-minute rounds up to 1 on minute hardware
    assert c._sc_convert(15.0, const.DURATION_UNIT_MINUTES) == 1


async def test_open_calls_run_service_with_duration_field():
    c = _coord()
    await c._sc_dispatch_open(_zone())
    c.hass.services.async_call.assert_awaited_once()
    domain, service, data = c.hass.services.async_call.await_args.args
    assert (domain, service) == ("script", "irrigation_beet")
    assert data["dauer"] == 10  # 600 s -> 10 min
    assert data["zone_id"] == 2
    assert data["zone_name"] == "Beet"


async def test_run_credits_bucket_persists_and_fires_started():
    c = _coord()
    c._confirm_valve_running = AsyncMock(return_value=True)
    c._timed_volume_l = Mock(return_value=20.0)  # litres
    c._credited_depth_native = Mock(return_value=4.0)  # mm
    zone = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_MAXIMUM_BUCKET: 50.0})

    ok = await c.async_run_self_closing(zone, trigger="schedule")

    assert ok is True
    c.hass.services.async_call.assert_awaited()
    # bucket credited optimistically: -5 + 4 = -1
    bucket_calls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert bucket_calls and bucket_calls[-1].args[1][const.ZONE_BUCKET] == -1.0
    # in-flight run persisted with credited=True
    cfg = c.store.async_update_config.await_args.args[0]
    runs = cfg[const.CONF_ACTIVE_VALVE_RUNS]
    assert len(runs) == 1 and runs[0][const.RUN_CREDITED] is True
    assert runs[0][const.RUN_ZONE_ID] == 2
    # started event fired
    evt = [a.args[0] for a in c.hass.bus.async_fire.call_args_list]
    assert f"{const.DOMAIN}_{const.EVENT_IRRIGATE_STARTED}" in evt
    # cleanup scheduled for the planned duration
    c._sc_schedule_cleanup.assert_called_once_with(2, 600.0)


async def test_finish_records_usage_removes_run_and_fires_finished():
    c = _coord()
    existing = {const.RUN_ZONE_ID: 2, const.RUN_PLANNED_SECONDS: 600.0}
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [existing]}
    )
    zone = _zone(**{const.ZONE_BUCKET: -1.0})
    c.store.get_zone = Mock(return_value=zone)
    c._timed_volume_l = Mock(return_value=20.0)  # litres actually delivered

    await c._sc_finish_run(2)

    # run removed from persistence
    cfg = c.store.async_update_config.await_args.args[0]
    assert cfg[const.CONF_ACTIVE_VALVE_RUNS] == []
    # usage recorded at completion (actual delivery, counted once)
    c._record_run.assert_awaited_once()
    kwargs = c._record_run.await_args.kwargs
    assert kwargs["add_to_total"] is True
    assert kwargs["volume_l"] == 20.0
    # finished event fired with the zone
    fired = {a.args[0]: a.args[1] for a in c.hass.bus.async_fire.call_args_list}
    key = f"{const.DOMAIN}_{const.EVENT_IRRIGATE_FINISHED}"
    assert key in fired
    assert fired[key]["zones"][0]["zone_id"] == 2


async def test_finish_stamps_last_irrigation_and_zeroes_duration_when_satisfied():
    # HA-Prod repro (Kirschlorbeer/Beet): a completed self-closing run credits the
    # bucket and records history, but never stamped last_irrigation nor zeroed the
    # displayed duration. It bypasses _commit_run_progress (which stamps
    # last_irrigation for a driven/metered run), and the store's
    # "bucket == 0 -> duration 0" shortcut misses because a MEASURED run lands the
    # bucket slightly POSITIVE (measured overshoot), never exactly 0.
    c = _coord()
    store_zone = _zone(
        **{
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_BUCKET: -2.0,
            const.ZONE_MAXIMUM_BUCKET: 24.0,
            const.ZONE_DURATION: 1611,
        }
    )
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)

    async def _upd(zid, changes):
        store_zone.update(changes)

    c.store.async_update_zone = AsyncMock(side_effect=_upd)
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_PLANNED_SECONDS: 1611.0,
                    const.RUN_PRE_BUCKET: -2.0,
                }
            ]
        }
    )
    # A measured run that delivers slightly more than the deficit -> bucket +0.26.
    c._sc_finish_flow = Mock(return_value=(2.26, {}))  # (measured litres, end_changes)
    c._credited_depth_native = Mock(return_value=2.26)  # mm credited from the measure
    c._flow_calibration_check = AsyncMock()

    await c._sc_finish_run(2)

    # bucket credited to a small measured surplus, POSITIVE and NOT exactly 0 (so
    # the store's bucket==0 -> duration 0 shortcut can't help)
    assert store_zone[const.ZONE_BUCKET] > 0
    # the two fields that were stale on HA-Prod now update after the run:
    assert const.ZONE_LAST_IRRIGATION in store_zone
    assert store_zone[const.ZONE_DURATION] == 0


async def test_finish_is_idempotent_when_run_missing():
    c = _coord()
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: []}
    )

    await c._sc_finish_run(2)

    # nothing to finalise -> no usage record, no finished event (guards against
    # the cleanup timer firing after an early stop already removed the run)
    c._record_run.assert_not_awaited()
    c.hass.bus.async_fire.assert_not_called()


async def test_stop_calls_stop_service_and_corrects_bucket():
    c = _coord()
    started = "2026-06-30T08:00:00+00:00"
    run = {
        const.RUN_ZONE_ID: 2,
        const.RUN_STARTED: started,
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_PLANNED_MM: 4.0,
        const.RUN_CREDITED: True,
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [run]}
    )
    zone = _zone(
        **{const.ZONE_BUCKET: -1.0, const.ZONE_STOP_SERVICE: "script.beet_off"}
    )
    c.store.get_zone = Mock(return_value=zone)
    # half the run elapsed -> deliver 50% -> remove 2 mm of the 4 mm credit
    c._sc_elapsed = Mock(return_value=300.0)
    c._timed_volume_l = Mock(return_value=10.0)  # litres actually delivered

    await c.async_stop_self_closing(2)

    # stop_service called
    domain, service, _ = c.hass.services.async_call.await_args.args
    assert (domain, service) == ("script", "beet_off")
    # bucket corrected down by the undelivered 2 mm: -1 - 2 = -3
    bcalls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert bcalls[-1].args[1][const.ZONE_BUCKET] == -3.0
    # run cleared
    cfg = c.store.async_update_config.await_args.args[0]
    assert cfg[const.CONF_ACTIVE_VALVE_RUNS] == []
    # usage recorded for the delivered portion only (not the planned amount)
    kwargs = c._record_run.await_args.kwargs
    assert kwargs["add_to_total"] is True
    assert kwargs["volume_l"] == 10.0


async def test_stop_sends_a_zero_duration_so_a_one_script_valve_closes():
    """The stop must carry duration 0 — reported by @pnaklicki on #83.

    The shipped blueprints run ONE script for both directions and branch on the
    duration, which the docs said was 0 for a stop; it was never actually sent.
    A script reading an unset variable raises rather than closing the valve, and
    the call is not blocking, so the run settled as stopped while the valve kept
    watering to the end of its hardware countdown.

    Sent under the zone's OWN duration field, not a hardcoded "duration" — a
    zone that renamed the key for its open would otherwise get a stop its
    script cannot read.
    """
    c = _coord()
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
                    const.RUN_PLANNED_SECONDS: 600.0,
                    const.RUN_PLANNED_MM: 4.0,
                    const.RUN_CREDITED: True,
                }
            ]
        }
    )
    c.store.get_zone = Mock(
        return_value=_zone(
            **{
                const.ZONE_BUCKET: -1.0,
                const.ZONE_STOP_SERVICE: "script.beet_off",
                const.ZONE_DURATION_FIELD: "sekunden",
            }
        )
    )
    c._sc_elapsed = Mock(return_value=300.0)
    c._timed_volume_l = Mock(return_value=10.0)

    await c.async_stop_self_closing(2)

    _, _, data = c.hass.services.async_call.await_args.args
    assert data["sekunden"] == 0
    assert data["zone_id"] == 2


async def test_stop_falls_back_to_the_default_duration_field():
    """An unset duration_field means "duration", exactly as the open path does."""
    c = _coord()
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
                    const.RUN_PLANNED_SECONDS: 600.0,
                    const.RUN_PLANNED_MM: 4.0,
                    const.RUN_CREDITED: True,
                }
            ]
        }
    )
    c.store.get_zone = Mock(
        return_value=_zone(
            **{
                const.ZONE_BUCKET: -1.0,
                const.ZONE_STOP_SERVICE: "script.beet_off",
                # The shared helper names a field; a blueprint zone leaves it
                # unset, which is the case this pins.
                const.ZONE_DURATION_FIELD: None,
            }
        )
    )
    c._sc_elapsed = Mock(return_value=300.0)
    c._timed_volume_l = Mock(return_value=10.0)

    await c.async_stop_self_closing(2)

    _, _, data = c.hass.services.async_call.await_args.args
    assert data["duration"] == 0


async def test_stop_without_stop_service_corrects_accounting_only():
    c = _coord()
    run = {
        const.RUN_ZONE_ID: 2,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_PLANNED_MM: 4.0,
        const.RUN_CREDITED: True,
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [run]}
    )
    zone = _zone(**{const.ZONE_BUCKET: -1.0})  # no stop_service configured
    c.store.get_zone = Mock(return_value=zone)
    c._sc_elapsed = Mock(return_value=300.0)
    c._timed_volume_l = Mock(return_value=10.0)

    await c.async_stop_self_closing(2)

    # no valve-close service can be called, but accounting is still corrected
    c.hass.services.async_call.assert_not_awaited()
    bcalls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert bcalls[-1].args[1][const.ZONE_BUCKET] == -3.0
    cfg = c.store.async_update_config.await_args.args[0]
    assert cfg[const.CONF_ACTIVE_VALVE_RUNS] == []


async def test_run_aborts_and_fires_problem_when_confirm_entity_stays_off():
    """A configured confirm_entity that never reports on = the valve did not
    open -> problem event + no credit. The problem names the confirm_entity."""
    c = _coord()
    c._confirm_valve_running = AsyncMock(return_value=False)  # never opened
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    zone = _zone(**{const.ZONE_CONFIRM_ENTITY: "valve.beet"})

    ok = await c.async_run_self_closing(zone, trigger="schedule")

    assert ok is False
    c.store.async_update_zone.assert_not_awaited()  # no credit
    c.store.async_update_config.assert_not_awaited()  # no persisted run
    fired = {a.args[0]: a.args[1] for a in c.hass.bus.async_fire.call_args_list}
    key = f"{const.DOMAIN}_{const.EVENT_ZONE_PROBLEM}"
    assert key in fired
    assert fired[key]["entity_id"] == "valve.beet"  # the confirm target


async def test_service_run_credits_without_confirm_entity():
    """No confirm_entity: the run is write-only, so credit optimistically and
    NEVER poll the momentary run_service script (JustChr #43 review regression:
    a fire-and-forget script returns to 'off' in ms, which must not misfire a
    zone_problem or skip the bucket credit)."""
    c = _coord()
    c._confirm_valve_running = AsyncMock()  # must NOT be called
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    zone = _zone(**{const.ZONE_BUCKET: -5.0, const.ZONE_MAXIMUM_BUCKET: 50.0})

    ok = await c.async_run_self_closing(zone, trigger="schedule")

    assert ok is True
    c._confirm_valve_running.assert_not_awaited()
    bucket_calls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert bucket_calls and bucket_calls[-1].args[1][const.ZONE_BUCKET] == -1.0
    evt = [a.args[0] for a in c.hass.bus.async_fire.call_args_list]
    assert f"{const.DOMAIN}_{const.EVENT_ZONE_PROBLEM}" not in evt


async def test_service_run_confirms_against_confirm_entity_poll_only():
    """With a confirm_entity, verify liveness against THAT entity — and poll-only
    (retry=False), so HA never re-actuates a self-closing valve mid-run (which
    would reset its hardware countdown)."""
    c = _coord()
    c._confirm_valve_running = AsyncMock(return_value=True)
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    zone = _zone(
        **{
            const.ZONE_CONFIRM_ENTITY: "valve.beet",
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )

    ok = await c.async_run_self_closing(zone, trigger="schedule")

    assert ok is True
    c._confirm_valve_running.assert_awaited_once_with(2, "valve.beet", retry=False)
    bucket_calls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert bucket_calls[-1].args[1][const.ZONE_BUCKET] == -1.0


async def test_service_run_credits_when_confirm_entity_unreadable():
    """An unreadable confirm_entity (None) must not penalise a write-only valve:
    credit optimistically, no problem event."""
    c = _coord()
    c._confirm_valve_running = AsyncMock(return_value=None)
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    zone = _zone(**{const.ZONE_CONFIRM_ENTITY: "valve.beet", const.ZONE_BUCKET: -5.0})

    ok = await c.async_run_self_closing(zone, trigger="schedule")

    assert ok is True
    bucket_calls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert bucket_calls  # credited despite an unreadable confirm entity
    evt = [a.args[0] for a in c.hass.bus.async_fire.call_args_list]
    assert f"{const.DOMAIN}_{const.EVENT_ZONE_PROBLEM}" not in evt


async def test_confirm_valve_running_poll_only_never_resends(monkeypatch):
    """`retry=False` polls the state but NEVER re-sends the open — critical for
    self-closing mode, where re-actuating would reset the hardware countdown.
    Drives the real _confirm_valve_running against a momentary/off entity."""
    c = _coord()
    off = Mock()
    off.state = "off"
    c.hass.states.get = Mock(return_value=off)
    monkeypatch.setattr(const, "VALVE_CONFIRM_TIMEOUT", 0.03)
    monkeypatch.setattr(const, "VALVE_CONFIRM_RETRY_AT", 0.01)
    monkeypatch.setattr(const, "VALVE_CONFIRM_POLL", 0.01)

    result = await c._confirm_valve_running(2, "valve.beet", retry=False)

    assert result is False
    c.hass.services.async_call.assert_not_awaited()  # poll-only: no re-send


async def test_resume_finalises_overdue_and_reschedules_partial():
    c = _coord()
    overdue = {
        const.RUN_ZONE_ID: 1,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 60.0,  # long past -> already closed
    }
    partial = {
        const.RUN_ZONE_ID: 2,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,  # may still be running
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [overdue, partial]}
    )
    c._sc_finish_run = AsyncMock()
    # zone 1 overdue (elapsed 10000 >= 60), zone 2 partial (elapsed 100 < 600).
    # The third value is zone 2's re-read after the master acquire (#152); this
    # coordinator's acquire does not sleep, so it reads the same instant and the
    # armed remainder below is unchanged.
    c._sc_elapsed = Mock(side_effect=[10000.0, 100.0, 100.0])

    await c.async_resume_self_closing_runs()

    c._sc_finish_run.assert_awaited_once_with(1)
    c._sc_schedule_cleanup.assert_called_once_with(2, 500.0)


async def test_resume_retakes_the_observed_suppression_window():
    """After a restart the marker has to end where a normal dispatch would have
    put it: start + planned + margin. The resume knows `elapsed`, so it re-takes
    with the REMAINDER — handing it the neighbouring cleanup's expression would
    overshoot by the finish grace, and adding the margin here would count it
    twice."""
    c = _coord()
    c._si_driven_until = {}
    c.hass.loop.time = Mock(return_value=1000.0)
    c._watch_start = AsyncMock()  # a confirmed record re-adopts its watcher
    run = {
        const.RUN_ZONE_ID: 2,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_MODE: const.WATERING_MODE_SERVICE,
        const.RUN_WATCH_ENTITY: "binary_sensor.confirm",
        const.RUN_LATENCY_MARGIN: 4,  # grace = settle 5 + 4 = 9
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [run]}
    )
    c._sc_elapsed = Mock(side_effect=[100.0, 100.0])

    await c.async_resume_self_closing_runs()

    assert c._si_driven_until[2] == pytest.approx(
        1000.0 + 500.0 + SI_VALVE_SUPPRESS_MARGIN
    )
    # The cleanup keeps its own expression, which carries the grace. The two
    # numbers differing by exactly the grace is the point.
    c._sc_schedule_cleanup.assert_called_once_with(2, 509.0)


async def test_resume_inside_the_grace_keeps_a_window_shorter_than_the_margin():
    """A run resumed past its plan but still inside its finish grace has a
    NEGATIVE remainder, and it has to be passed raw. Flooring it at 0 would
    stretch the window past what a normal dispatch gives and swallow a genuine
    external run afterwards — the mirror of what the two close-side re-notes in
    the metered runner prevent."""
    c = _coord()
    c._si_driven_until = {}
    c.hass.loop.time = Mock(return_value=1000.0)
    c._watch_start = AsyncMock()
    run = {
        const.RUN_ZONE_ID: 3,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_MODE: const.WATERING_MODE_SERVICE,
        const.RUN_WATCH_ENTITY: "binary_sensor.confirm",
        const.RUN_LATENCY_MARGIN: 4,
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [run]}
    )
    # 605 s in: past the plan, still inside the 9 s grace, so not finalised.
    c._sc_elapsed = Mock(side_effect=[605.0])

    await c.async_resume_self_closing_runs()

    assert c._si_driven_until[3] == pytest.approx(
        1000.0 - 5.0 + SI_VALVE_SUPPRESS_MARGIN
    )
    # Explicitly SHORTER than a bare margin: that is what a floor would destroy.
    assert c._si_driven_until[3] < 1000.0 + SI_VALVE_SUPPRESS_MARGIN


async def test_after_a_resume_the_observer_stays_silent_in_the_old_gap():
    """End to end for the defect this re-take exists for.

    Resume a still-running service run, then let its watched entity flap on
    inside the band the restart used to open: past ``planned + grace``, where
    ``zone_run_in_flight`` has already let go, but before ``planned + margin``,
    where a normal dispatch still holds the observer off. Before the re-take the
    observer armed here and the following close credited the bucket for water
    the run already accounts for.
    """
    c = _coord()
    c._si_driven_until = {}
    c._observed_on_since = {}
    c._observed_zone_by_entity = {"switch.valve": 2}
    c.store.get_zone = Mock(return_value={})
    c.hass.loop.time = Mock(return_value=1000.0)
    c._watch_start = AsyncMock()
    run = {
        const.RUN_ZONE_ID: 2,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_MODE: const.WATERING_MODE_SERVICE,
        const.RUN_WATCH_ENTITY: "binary_sensor.confirm",
        const.RUN_LATENCY_MARGIN: 4,  # grace = 9
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [run]}
    )
    c._sc_elapsed = Mock(side_effect=[100.0, 100.0])

    await c.async_resume_self_closing_runs()

    # Resume happened 100 s in, so loop time 1000 is start + 100. The band the
    # defect lived in is start + 609 .. start + 630, i.e. loop 1509 .. 1530.
    c.hass.loop.time = Mock(return_value=1520.0)
    # The record is long past its window by now, so the other half of the
    # suppression is already gone.
    c.zone_run_in_flight = Mock(return_value=False)
    state = lambda s: SimpleNamespace(state=s)
    c._observed_state_changed(
        SimpleNamespace(
            data={
                "entity_id": "switch.valve",
                "new_state": state("on"),
                "old_state": state("off"),
            }
        )
    )

    assert 2 not in c._observed_on_since


def test_is_self_closing_distinguishes_modes():
    c = _coord()
    classic = _zone(**{const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC})
    assert c._sc_is_self_closing(classic) is False
    assert c._sc_is_self_closing(_zone()) is True


async def test_maybe_stop_delegates_for_service_zone():
    c = _coord()
    c.store.get_zone = Mock(return_value=_zone())
    c.async_stop_self_closing = AsyncMock(return_value=True)
    handled = await c._sc_maybe_stop(2)
    assert handled is True
    c.async_stop_self_closing.assert_awaited_once_with(2)


async def test_maybe_stop_ignores_classic_zone():
    c = _coord()
    c.store.get_zone = Mock(
        return_value=_zone(**{const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC})
    )
    c.async_stop_self_closing = AsyncMock()
    handled = await c._sc_maybe_stop(2)
    assert handled is False
    c.async_stop_self_closing.assert_not_awaited()


async def test_run_zone_routes_service_zone_with_overridden_duration():
    c = _coord()
    c.store.get_zone = Mock(return_value=_zone())  # watering_mode == "service"
    c.async_run_self_closing = AsyncMock(return_value=True)

    await c.async_run_zone(2, 5.0)  # 5 minutes -> 300 s

    c.async_run_self_closing.assert_awaited_once()
    dispatched = c.async_run_self_closing.await_args.args[0]
    assert dispatched[const.ZONE_DURATION] == 300


async def test_service_open_defaults_duration_field_to_duration():
    """An empty duration_field must still pass the duration (under 'duration')."""
    c = _coord()
    zone = _zone()
    zone.pop(const.ZONE_DURATION_FIELD)  # not configured
    await c._sc_service_open(zone, 5)
    _, _, data = c.hass.services.async_call.await_args.args
    assert data["duration"] == 5


async def test_self_closing_run_marks_si_driven():
    c = _coord()
    c._si_driven_until = {}
    c.hass.loop.time = Mock(return_value=1000.0)
    c._confirm_valve_running = AsyncMock(return_value=True)
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    await c.async_run_self_closing(_zone(), trigger="schedule")
    assert 2 in c._si_driven_until  # zone id 2 marked so the observer skips it
    # window = loop.time + planned_seconds + margin, covering the whole run
    assert c._si_driven_until[2] == 1000.0 + 600.0 + SI_VALVE_SUPPRESS_MARGIN


async def test_self_closing_credits_measured_flow(monkeypatch):
    """A self-closing zone with a flow_sensor records the MEASURED volume from the
    non-blocking sampler at finish — not the time-based estimate — and persists the
    totalizer end (flow_last_end) for cross-run learning."""
    import custom_components.irrigation_plus.self_closing as scmod

    # Isolate the interval timer: the test drives sampling via the _sc_sample_flow seam.
    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    # time-based estimate = 8 L (throughput 4 L/min x 120 s); measured will be 12 L
    c._timed_volume_l = Mock(return_value=8.0)
    c._credited_depth_native = Mock(side_effect=lambda z, litres: litres)

    zone = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
            const.ZONE_DURATION: 120.0,  # seconds
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
            const.ZONE_THROUGHPUT: 4.0,
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_PER_RUN,
        }
    )
    # Stateful store: async_update_zone merges into the dict get_zone returns, so the
    # flow_last_end persistence is observable through get_zone.
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)

    async def _update_zone(zid, changes):
        store_zone.update(changes)

    c.store.async_update_zone = AsyncMock(side_effect=_update_zone)
    # Stateful config: hold the in-flight run so _sc_finish_run finds it.
    active = []

    async def _get_config():
        return {const.CONF_ACTIVE_VALVE_RUNS: list(active)}

    async def _update_config(changes):
        if const.CONF_ACTIVE_VALVE_RUNS in changes:
            active[:] = changes[const.CONF_ACTIVE_VALVE_RUNS]

    c.store.async_get_config = AsyncMock(side_effect=_get_config)
    c.store.async_update_config = AsyncMock(side_effect=_update_config)

    # Sensor reads 0 at valve-open (the meter is seeded here).
    current = {"st": _flow_state(0)}
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    ok = await c.async_run_self_closing(zone, trigger="schedule")
    assert ok is True

    # Per-run totalizer climb 0 -> 6 -> 12 -> 12 (L), driven deterministically.
    for at, val in ((30.0, 6), (60.0, 12), (90.0, 12)):
        current["st"] = _flow_state(val)
        c._sc_sample_flow(2, at)

    await c._sc_finish_run(2)

    # Recorded volume is the MEASURED 12 L, not the 8 L time-based estimate.
    kwargs = c._record_run.await_args.kwargs
    assert kwargs["volume_l"] == 12.0
    assert kwargs["add_to_total"] is True
    # Totalizer end persisted for cross-run learning.
    assert c.store.get_zone(2)[const.ZONE_FLOW_LAST_END] == 12.0


async def test_self_closing_without_flow_sensor_uses_timed_volume(monkeypatch):
    """Regression guard: a self-closing zone with NO flow_sensor never registers
    interval sampling and records the time-based volume unchanged (the None path)."""
    import custom_components.irrigation_plus.self_closing as scmod

    track = Mock(return_value=Mock())
    monkeypatch.setattr(scmod, "async_track_time_interval", track)

    c = _coord()
    c._timed_volume_l = Mock(return_value=8.0)
    c._credited_depth_native = Mock(return_value=4.0)

    zone = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_DURATION: 120.0,
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
        }
    )  # no flow_sensor
    active = []

    async def _get_config():
        return {const.CONF_ACTIVE_VALVE_RUNS: list(active)}

    async def _update_config(changes):
        if const.CONF_ACTIVE_VALVE_RUNS in changes:
            active[:] = changes[const.CONF_ACTIVE_VALVE_RUNS]

    c.store.async_get_config = AsyncMock(side_effect=_get_config)
    c.store.async_update_config = AsyncMock(side_effect=_update_config)
    c.store.get_zone = Mock(return_value=zone)

    ok = await c.async_run_self_closing(zone, trigger="schedule")
    assert ok is True
    # No flow_sensor -> the interval sampler is never registered.
    track.assert_not_called()

    await c._sc_finish_run(2)

    # Time-based volume recorded unchanged; no totalizer end persisted.
    assert c._record_run.await_args.kwargs["volume_l"] == 8.0
    flow_end_calls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_FLOW_LAST_END in ck.args[1]
    ]
    assert not flow_end_calls


async def test_self_closing_sampling_interval_cancelled_on_finish(monkeypatch):
    """M-2: the 15 s interval sampler is cancelled exactly once at finish and its
    meter entry is popped from _sc_meters() — no timer leaks past the run."""
    import custom_components.irrigation_plus.self_closing as scmod

    cancel = Mock()
    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=cancel))

    c = _coord()
    c._timed_volume_l = Mock(return_value=8.0)
    c._credited_depth_native = Mock(side_effect=lambda z, litres: litres)

    zone = _zone(
        **{
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
            const.ZONE_DURATION: 120.0,
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
            const.ZONE_THROUGHPUT: 4.0,
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_PER_RUN,
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)

    async def _update_zone(zid, changes):
        store_zone.update(changes)

    c.store.async_update_zone = AsyncMock(side_effect=_update_zone)
    active = []

    async def _get_config():
        return {const.CONF_ACTIVE_VALVE_RUNS: list(active)}

    async def _update_config(changes):
        if const.CONF_ACTIVE_VALVE_RUNS in changes:
            active[:] = changes[const.CONF_ACTIVE_VALVE_RUNS]

    c.store.async_get_config = AsyncMock(side_effect=_get_config)
    c.store.async_update_config = AsyncMock(side_effect=_update_config)
    c.hass.states.get = Mock(return_value=_flow_state(0))

    ok = await c.async_run_self_closing(zone, trigger="schedule")
    assert ok is True
    assert 2 in c._sc_meters()  # sampler registered during the run

    await c._sc_finish_run(2)

    cancel.assert_called_once()  # interval cancelled exactly once
    assert 2 not in c._sc_meters()  # entry popped -> no leak


async def test_self_closing_overlap_cancels_prior_interval(monkeypatch):
    """I-1 regression: a second sampler for the same zone (e.g. a manual run fired
    during a scheduled one) cancels-and-pops the first interval — the prior 15 s timer
    is never orphaned, and exactly one meter entry remains."""
    import custom_components.irrigation_plus.self_closing as scmod

    cancel1, cancel2 = Mock(), Mock()
    monkeypatch.setattr(
        scmod, "async_track_time_interval", Mock(side_effect=[cancel1, cancel2])
    )

    c = _coord()
    c.hass.states.get = Mock(return_value=_flow_state(0))
    zone = _zone(**{const.ZONE_FLOW_SENSOR: "sensor.beet_flow"})
    c.store.get_zone = Mock(return_value=zone)

    await c._sc_start_flow_sampling(zone)
    assert c._sc_meters()[2][1] is cancel1  # first interval registered
    cancel1.assert_not_called()

    await c._sc_start_flow_sampling(zone)

    cancel1.assert_called_once()  # prior interval cancelled, not orphaned
    cancel2.assert_not_called()
    assert list(c._sc_meters()) == [2]  # exactly one entry remains
    assert c._sc_meters()[2][1] is cancel2  # and it is the new sampler


async def test_self_closing_overlap_cancels_prior_cleanup_timer(monkeypatch):
    """review finding D (sister of the I-1 interval overlap fix): a second run for the
    same zone (e.g. a manual run fired during a scheduled one) cancels-and-replaces the
    first run's cleanup timer — the prior cosmetic-finish timer is never orphaned, so it
    can't fire _sc_finish_run against the NEW run and finalize it early (false COMPLETED,
    actual_s=planned_s, dropped flow tail). Mirrors the interval-overlap guard above."""
    import custom_components.irrigation_plus.self_closing as scmod

    cancel1, cancel2 = Mock(), Mock()
    monkeypatch.setattr(scmod, "async_call_later", Mock(side_effect=[cancel1, cancel2]))

    c = _coord()
    del c._sc_schedule_cleanup  # restore the real method (the fixture stubs it out)

    c._sc_schedule_cleanup(2, 600.0)
    assert c._sc_cleanup_timers()[2] is cancel1  # first cleanup timer registered
    cancel1.assert_not_called()

    c._sc_schedule_cleanup(2, 600.0)

    cancel1.assert_called_once()  # prior cleanup timer cancelled, not orphaned
    cancel2.assert_not_called()
    assert list(c._sc_cleanup_timers()) == [2]  # exactly one entry remains
    assert c._sc_cleanup_timers()[2] is cancel2  # and it is the new timer


async def test_self_closing_cleanup_timer_popped_on_finish(monkeypatch):
    """review finding D: a run's cleanup timer is popped from _sc_cleanup_timers() when
    the run finalizes (_sc_finish_run), so a stale handle can't linger past the run."""
    import custom_components.irrigation_plus.self_closing as scmod

    cancel = Mock()
    monkeypatch.setattr(scmod, "async_call_later", Mock(return_value=cancel))

    c = _coord()
    del c._sc_schedule_cleanup  # restore the real method
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {const.RUN_ZONE_ID: 2, const.RUN_PLANNED_SECONDS: 600.0}
            ]
        }
    )
    c.store.get_zone = Mock(return_value=_zone(**{const.ZONE_BUCKET: -1.0}))
    c._timed_volume_l = Mock(return_value=20.0)

    c._sc_schedule_cleanup(2, 600.0)
    assert 2 in c._sc_cleanup_timers()

    await c._sc_finish_run(2)

    assert 2 not in c._sc_cleanup_timers()  # popped -> no stale handle lingers


async def test_self_closing_cleanup_timer_cancelled_on_stop(monkeypatch):
    """review finding D: an early stop cancels-and-pops the run's pending cleanup timer,
    so the original run's timer can't fire _sc_finish_run after the stop removed it."""
    import custom_components.irrigation_plus.self_closing as scmod

    cancel = Mock()
    monkeypatch.setattr(scmod, "async_call_later", Mock(return_value=cancel))

    c = _coord()
    del c._sc_schedule_cleanup  # restore the real method
    run = {
        const.RUN_ZONE_ID: 2,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_PLANNED_MM: 4.0,
        const.RUN_CREDITED: True,
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [run]}
    )
    zone = _zone(
        **{const.ZONE_BUCKET: -1.0, const.ZONE_STOP_SERVICE: "script.beet_off"}
    )
    c.store.get_zone = Mock(return_value=zone)
    c._sc_elapsed = Mock(return_value=300.0)
    c._timed_volume_l = Mock(return_value=10.0)

    c._sc_schedule_cleanup(2, 600.0)
    assert 2 in c._sc_cleanup_timers()

    await c.async_stop_self_closing(2)

    cancel.assert_called_once()  # pending cleanup timer cancelled on early stop
    assert 2 not in c._sc_cleanup_timers()  # and popped


async def test_self_closing_measured_bucket_reconciles_from_pre_bucket(monkeypatch):
    """I-2 regression: when the optimistic TIME-based open credit CLAMPS at the ceiling
    but the MEASURED volume is smaller, the finish reconciles the bucket ABSOLUTELY from
    the stashed pre-run level — it must NOT over-empty via a delta correction.

    pre_bucket 0, maximum_bucket 20; time-based credit = 30 mm -> open clamps to 20;
    measured = 10 L -> bucket must land at min(20, 0 + 10) = 10, NOT the delta result
    20 + (10 - 30) = 0.
    """
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    c._timed_volume_l = Mock(return_value=30.0)  # time-based open credit -> depth 30
    # A credit that lands ABOVE the run target only happens on a live-estimate
    # run, whose intra-day deficit can exceed the stored daily bucket — that is
    # the one case _run_ceiling allows a surplus (up to maximum_bucket) for. An
    # ordinary run clamps at the target; see tests/test_credit_ceiling.py.
    c._live_run_zones = {2}
    c._credited_depth_native = Mock(side_effect=lambda z, litres: litres)  # identity

    zone = _zone(
        **{
            const.ZONE_BUCKET: 0.0,
            const.ZONE_MAXIMUM_BUCKET: 20.0,
            const.ZONE_DURATION: 120.0,
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
            const.ZONE_THROUGHPUT: 4.0,
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_PER_RUN,
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)

    async def _update_zone(zid, changes):
        store_zone.update(changes)

    c.store.async_update_zone = AsyncMock(side_effect=_update_zone)
    active = []

    async def _get_config():
        return {const.CONF_ACTIVE_VALVE_RUNS: list(active)}

    async def _update_config(changes):
        if const.CONF_ACTIVE_VALVE_RUNS in changes:
            active[:] = changes[const.CONF_ACTIVE_VALVE_RUNS]

    c.store.async_get_config = AsyncMock(side_effect=_get_config)
    c.store.async_update_config = AsyncMock(side_effect=_update_config)

    current = {"st": _flow_state(0)}
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    ok = await c.async_run_self_closing(zone, trigger="schedule")
    assert ok is True
    # Open credit clamped optimistically at the ceiling (0 + 30 -> 20).
    assert store_zone[const.ZONE_BUCKET] == 20.0
    # The persisted run stashed the pre-run bucket for the absolute reconcile.
    assert active[0][const.RUN_PRE_BUCKET] == 0.0

    # Per-run totalizer climbs 0 -> 5 -> 10 L (measured 10 L < the 30 mm timed credit).
    for at, val in ((60.0, 5), (120.0, 10)):
        current["st"] = _flow_state(val)
        c._sc_sample_flow(2, at)

    await c._sc_finish_run(2)

    # Bucket reconciled ABSOLUTELY from pre_bucket: min(20, 0 + 10) = 10 — NOT the
    # over-corrected delta result (20 + (10 - 30) = 0).
    expected = min(20.0, 0.0 + 10.0)
    assert store_zone[const.ZONE_BUCKET] == expected == 10.0
    bucket_calls = [
        ck
        for ck in c.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]
    assert bucket_calls[-1].args[1][const.ZONE_BUCKET] == 10.0
    assert bucket_calls[-1].args[1][const.ZONE_BUCKET] > 0.0  # not over-emptied
    # Recorded usage is the measured 10 L.
    assert c._record_run.await_args.kwargs["volume_l"] == 10.0


async def test_self_closing_early_stop_bucket_reconciles_from_pre_bucket(monkeypatch):
    """FM #2 regression: an EARLY stop reconciles the bucket ABSOLUTELY from the stashed
    pre-run level, exactly like the full-completion path. When the optimistic time-based
    open credit CLAMPED at the ceiling, the old delta subtraction (bucket - undelivered_mm)
    over-emptied; reconciling pre_bucket + delivered is correct in every quadrant.

    pre_bucket 0, maximum_bucket 20, open credit depth 30 -> clamps to 20. Stop at 50%:
    absolute = min(20, 0 + 30*0.5) = 15, NOT the delta result 20 - (30*0.5) = 5.
    """
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    c._timed_volume_l = Mock(return_value=30.0)  # open credit depth 30 (identity depth)
    # A credit that lands ABOVE the run target only happens on a live-estimate
    # run, whose intra-day deficit can exceed the stored daily bucket — that is
    # the one case _run_ceiling allows a surplus (up to maximum_bucket) for. An
    # ordinary run clamps at the target; see tests/test_credit_ceiling.py.
    c._live_run_zones = {2}
    c._credited_depth_native = Mock(side_effect=lambda z, litres: litres)

    zone = _zone(
        **{
            const.ZONE_BUCKET: 0.0,
            const.ZONE_MAXIMUM_BUCKET: 20.0,
            const.ZONE_DURATION: 120.0,
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
            const.ZONE_THROUGHPUT: 4.0,
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_STOP_SERVICE: "switch.turn_off",
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)

    async def _update_zone(zid, changes):
        store_zone.update(changes)

    c.store.async_update_zone = AsyncMock(side_effect=_update_zone)
    active = []

    async def _get_config():
        return {const.CONF_ACTIVE_VALVE_RUNS: list(active)}

    async def _update_config(changes):
        if const.CONF_ACTIVE_VALVE_RUNS in changes:
            active[:] = changes[const.CONF_ACTIVE_VALVE_RUNS]

    c.store.async_get_config = AsyncMock(side_effect=_get_config)
    c.store.async_update_config = AsyncMock(side_effect=_update_config)
    c.hass.states.get = Mock(return_value=_flow_state(0))  # no measurable flow

    ok = await c.async_run_self_closing(zone, trigger="schedule")
    assert ok is True
    assert store_zone[const.ZONE_BUCKET] == 20.0  # open credit clamped at the ceiling
    assert active[0][const.RUN_PRE_BUCKET] == 0.0

    c._sc_elapsed = Mock(return_value=60.0)  # stop at 50% of the 120 s window
    await c.async_stop_self_closing(2)

    # Absolute reconcile from pre_bucket: min(20, 0 + 30*0.5) = 15, NOT the delta 20-15=5.
    assert store_zone[const.ZONE_BUCKET] == 15.0


async def test_self_closing_early_stop_credits_measured_over_timed(monkeypatch):
    """review finding F: an EARLY stop with a valid flow MEASUREMENT reconciles the bucket
    from pre_bucket + credited_depth(measured) — matching the completion twin _sc_finish_run
    — NOT the time-based planned_mm * delivered_frac partial. Under a miscalibrated
    throughput the time-based partial over-/under-credits the bucket; the measured value is
    ground truth. The no-measurement sibling test above keeps the time-based fallback.

    pre_bucket 0, open credit depth 30 (time-based); stop at 50% -> the time-based partial
    would be 30*0.5 = 15. Measured = 10 L -> bucket must land at 0 + 10 = 10, NOT 15.
    """
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    c._timed_volume_l = Mock(return_value=30.0)  # open credit depth 30 (identity depth)
    # A credit that lands ABOVE the run target only happens on a live-estimate
    # run, whose intra-day deficit can exceed the stored daily bucket — that is
    # the one case _run_ceiling allows a surplus (up to maximum_bucket) for. An
    # ordinary run clamps at the target; see tests/test_credit_ceiling.py.
    c._live_run_zones = {2}
    c._credited_depth_native = Mock(side_effect=lambda z, litres: litres)

    zone = _zone(
        **{
            const.ZONE_BUCKET: 0.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,  # high -> no clamp masks the reconcile
            const.ZONE_DURATION: 120.0,
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
            const.ZONE_THROUGHPUT: 4.0,
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_PER_RUN,
            const.ZONE_STOP_SERVICE: "switch.turn_off",
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)

    async def _update_zone(zid, changes):
        store_zone.update(changes)

    c.store.async_update_zone = AsyncMock(side_effect=_update_zone)
    active = []

    async def _get_config():
        return {const.CONF_ACTIVE_VALVE_RUNS: list(active)}

    async def _update_config(changes):
        if const.CONF_ACTIVE_VALVE_RUNS in changes:
            active[:] = changes[const.CONF_ACTIVE_VALVE_RUNS]

    c.store.async_get_config = AsyncMock(side_effect=_get_config)
    c.store.async_update_config = AsyncMock(side_effect=_update_config)

    current = {"st": _flow_state(0)}
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    ok = await c.async_run_self_closing(zone, trigger="schedule")
    assert ok is True
    assert (
        store_zone[const.ZONE_BUCKET] == 30.0
    )  # optimistic open credit (below ceiling)

    # Per-run totalizer climbs 0 -> 5 -> 10 L (measured 10 L != the 15 time-based partial).
    for at, val in ((30.0, 5), (60.0, 10)):
        current["st"] = _flow_state(val)
        c._sc_sample_flow(2, at)

    c._sc_elapsed = Mock(return_value=60.0)  # stop at 50% of the 120 s window
    await c.async_stop_self_closing(2)

    # Measured reconcile from pre_bucket: 0 + 10 = 10, NOT the time-based partial 30*0.5=15.
    assert store_zone[const.ZONE_BUCKET] == 10.0
    # Recorded usage is the measured 10 L.
    assert c._record_run.await_args.kwargs["volume_l"] == 10.0


async def test_self_closing_final_read_captures_last_climb(monkeypatch):
    """FM #3 regression: _sc_finish_flow takes ONE final reading at close, so a totalizer's
    last (up to a poll interval) of climb after the last periodic sample is not dropped.
    """
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    zone = _zone(
        **{
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_LIFETIME,
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)
    current = {"st": _flow_state(0)}
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    await c._sc_start_flow_sampling(zone)
    # Periodic samples reach 10 L...
    for at, val in ((15.0, 5), (30.0, 10)):
        current["st"] = _flow_state(val)
        c._sc_sample_flow(2, at)
    # ...then the counter climbs to 18 L in the final (sub-poll) stretch before close.
    current["st"] = _flow_state(18)

    measured, _end = c._sc_finish_flow(2)
    # The final read captured the last 8 L — measured is 18, not the last periodic 10.
    assert measured == 18.0


async def test_self_closing_advisory_after_repeated_off_rate():
    """A self-closing (can't-stop) service zone whose MEASURED flow rate is
    consistently >15% off its configured throughput raises exactly ONE flow-
    calibration advisory once >= FLOW_CAL_MIN_SAMPLES runs are collected — via the
    shared base helper _flow_calibration_check (FM-7), the same advisory a can't-stop
    distributor member gets."""
    c = _coord()
    c.hass.config.units = METRIC_SYSTEM  # metric -> recommendation reads in L/min
    zone = _zone(
        **{
            const.ZONE_THROUGHPUT: 4.0,  # configured 4 L/min
            const.ZONE_FLOW_CAL_SAMPLES: [],
            const.ZONE_FLOW_CAL_ADVISED: False,
        }
    )
    # Measured 12 L in 120 s -> observed 6 L/min == +50% over the configured 4 L/min.
    # The window is 120 s rather than 60 because the rate is what this test is about
    # and the VOLUME is what the advisory's quantisation floor judges: 6 L on a 1 L
    # meter carries more error than the 15% band it would be measured against, so it
    # is no longer a sample at all (FLOW_CAL_MIN_SAMPLE_L, #133). Same rate, same
    # deviation, a run big enough to mean it.
    for _ in range(const.FLOW_CAL_MIN_SAMPLES):
        await c._flow_calibration_check(zone, measured_l=12.0, seconds=120.0)
        # The Mock store does not mutate the dict; carry the persisted state forward so
        # the samples accumulate across runs (mirrors the distributor advisory test).
        changes = c.store.async_update_zone.await_args.args[1]
        zone[const.ZONE_FLOW_CAL_SAMPLES] = changes[const.ZONE_FLOW_CAL_SAMPLES]
        if const.ZONE_FLOW_CAL_ADVISED in changes:
            zone[const.ZONE_FLOW_CAL_ADVISED] = changes[const.ZONE_FLOW_CAL_ADVISED]

    create_calls = [
        ck
        for ck in c.hass.services.async_call.await_args_list
        if ck.args[:2] == ("persistent_notification", "create")
    ]
    assert len(create_calls) == 1  # exactly ONE advisory across the threshold
    msg = create_calls[0].args[2]["message"]
    assert "flow" in msg and "throughput" in msg  # advisory names the flow/throughput
    assert "over" in msg  # +50% -> over-watering direction


# --- The hardware window vs the planned window (#88, Eifel-Joe) ----------------
#
# A minute-unit controller cannot be told a partial minute, so _sc_convert rounds
# UP. Everything downstream of the dispatch used to price the UN-rounded plan, so
# a 263 s run opened the valve for 300 s while the record, the credit, the flow
# sample and the backstop all said 263. Measured against the recorder on real
# hardware: 502 -> 540, 265 -> 300, 263 -> 300.
#
# Every pre-existing test in this file missed it because the fixture's duration is
# 600.0 s — a whole multiple of 60, the one case where the ceil does not bite.


def test_effective_seconds_prices_the_rounded_up_window():
    c = _coord()
    # seconds hardware: what we ask for is what it runs
    assert c._sc_effective_seconds(263.0, const.DURATION_UNIT_SECONDS) == 263.0
    # minute hardware: 263 s is sent as 5 min, so the valve is open 300 s
    assert c._sc_convert(263.0, const.DURATION_UNIT_MINUTES) == 5
    assert c._sc_effective_seconds(263.0, const.DURATION_UNIT_MINUTES) == 300.0
    # the three windows Eifel-Joe measured against the recorder
    assert c._sc_effective_seconds(502.0, const.DURATION_UNIT_MINUTES) == 540.0
    assert c._sc_effective_seconds(265.0, const.DURATION_UNIT_MINUTES) == 300.0
    # a whole multiple of 60 is untouched — this is why the defect stayed hidden
    assert c._sc_effective_seconds(600.0, const.DURATION_UNIT_MINUTES) == 600.0


async def test_a_rounded_up_minute_run_is_recorded_and_backstopped_at_the_real_window():
    """The run must be booked for the 300 s the valve is open, not the 263 s planned.

    The backstop half is what made _watch_finish unreachable on Eifel-Joe's Beet
    zone: armed on the short window, it settled the run 36-40 s BEFORE the valve
    actually closed, so no partial could ever be observed there.
    """
    c = _coord()
    c._confirm_valve_running = AsyncMock(return_value=True)
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    zone = _zone(
        **{
            const.ZONE_DURATION: 263.0,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )

    ok = await c.async_run_self_closing(zone, trigger="schedule")
    assert ok is True

    # the controller was told 5 minutes
    _d, _s, data = c.hass.services.async_call.await_args.args
    assert data["dauer"] == 5

    # and the run is priced at the 300 s that buys, not the 263 s asked for
    c._sc_schedule_cleanup.assert_called_once_with(2, 300.0)
    cfg = c.store.async_update_config.await_args.args[0]
    run = cfg[const.CONF_ACTIVE_VALVE_RUNS][0]
    assert run[const.RUN_PLANNED_SECONDS] == 300.0
    # the volume credited is the volume that window actually delivers
    assert c._timed_volume_l.call_args.args[1] == 300.0


async def test_a_seconds_unit_zone_is_untouched():
    """Regression guard: the fix must move nothing on second-unit hardware."""
    c = _coord()
    c._confirm_valve_running = AsyncMock(return_value=True)
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    zone = _zone(
        **{
            const.ZONE_DURATION_UNIT: const.DURATION_UNIT_SECONDS,
            const.ZONE_DURATION: 263.0,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )

    assert await c.async_run_self_closing(zone, trigger="schedule") is True
    _d, _s, data = c.hass.services.async_call.await_args.args
    assert data["dauer"] == 263
    c._sc_schedule_cleanup.assert_called_once_with(2, 263.0)


async def test_the_flow_sample_divides_by_the_window_the_meter_actually_saw():
    """#133's false-advisory path: the self-closing caller has NO duration gate, so
    a short minute-unit run fed the advisory a rate inflated by the rounding.

    70 s is sent as 2 min. Metering 6 L over that 120 s open is 3.0 L/min; dividing
    the same 6 L by the un-rounded 70 s reads 5.14 L/min, +71% on a zone whose
    throughput is exactly right.
    """
    c = _coord()
    c._confirm_valve_running = AsyncMock(return_value=True)
    c._timed_volume_l = Mock(return_value=6.0)
    c._credited_depth_native = Mock(return_value=1.0)
    zone = _zone(
        **{
            const.ZONE_DURATION: 70.0,
            const.ZONE_BUCKET: -5.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
        }
    )
    await c.async_run_self_closing(zone, trigger="schedule")
    cfg = c.store.async_update_config.await_args.args[0]
    planned = cfg[const.CONF_ACTIVE_VALVE_RUNS][0][const.RUN_PLANNED_SECONDS]
    assert planned == 120.0

    # _sc_finish_run hands the advisory the run record's planned window
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {const.RUN_ZONE_ID: 2, const.RUN_PLANNED_SECONDS: planned}
            ]
        }
    )
    c.store.get_zone = Mock(return_value=zone)
    c._sc_finish_flow = Mock(return_value=(6.0, {}))
    c._flow_calibration_check = AsyncMock()

    await c._sc_finish_run(2)

    c._flow_calibration_check.assert_awaited_once()
    _zone_arg, measured, seconds = c._flow_calibration_check.await_args.args
    assert (measured, seconds) == (6.0, 120.0)
    assert measured / (seconds / 60.0) == 3.0  # not the 5.14 the old window read


async def test_a_valve_that_never_opened_also_raises_the_zone_fault():
    """The confirm poll saw the valve stay off. The bus event was already fired
    here, the fault was not - the only unpaired site of the seven that announce
    a zone problem. An automation bound to the bus heard it; the problem sensor
    and the dashboard chip, which read the fault, stayed dark."""
    c = _coord()
    c._set_zone_fault = Mock()
    c._confirm_valve_running = AsyncMock(return_value=False)  # never opened
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    zone = _zone(**{const.ZONE_CONFIRM_ENTITY: "valve.beet"})

    ok = await c.async_run_self_closing(zone, trigger="schedule")

    assert ok is False
    c._set_zone_fault.assert_called_once_with(2, const.PROBLEM_VALVE_DID_NOT_OPEN)


async def test_a_completed_run_clears_the_zone_fault():
    """_clear_zone_fault had five callers, all of them on the classic metered or
    rotating path in irrigation.py. A self-closing, batch or OpenSprinkler zone
    could therefore raise a fault and never end one: _zone_faults lives in
    memory, so the problem sensor stayed on until HA was restarted."""
    c = _coord()
    c._clear_zone_fault = Mock()
    store_zone = _zone(**{const.ZONE_BUCKET: -2.0, const.ZONE_MAXIMUM_BUCKET: 24.0})
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_PLANNED_SECONDS: 600.0,
                    const.RUN_PRE_BUCKET: -2.0,
                }
            ]
        }
    )
    c._sc_finish_flow = Mock(return_value=(2.26, {}))
    c._credited_depth_native = Mock(return_value=2.26)
    c._flow_calibration_check = AsyncMock()

    await c._sc_finish_run(2)

    c._clear_zone_fault.assert_called_once_with(2)


async def test_a_stopped_run_clears_the_zone_fault_as_the_classic_runner_does():
    """The classic runner clears on a partial as well as a completion
    (_record_rotating_stop, irrigation.py:1777): a run that was stopped still
    watered, so it is evidence the valve works."""
    c = _coord()
    c._clear_zone_fault = Mock()
    store_zone = _zone(**{const.ZONE_BUCKET: -1.0})
    c.store.get_zone = Mock(return_value=store_zone)
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
                    const.RUN_PLANNED_SECONDS: 600.0,
                    const.RUN_PLANNED_MM: 4.0,
                    const.RUN_PRE_BUCKET: -5.0,
                    const.RUN_CREDITED: True,
                }
            ]
        }
    )
    c._sc_elapsed = Mock(return_value=300.0)
    c._timed_volume_l = Mock(return_value=10.0)

    await c.async_stop_self_closing(2)

    c._clear_zone_fault.assert_called_once_with(2)


async def test_a_live_but_dry_meter_reports_zero_not_nothing(monkeypatch):
    """A counter that never moves over a whole run is not a missing
    measurement: the meter was alive and integrated nothing - a dry cistern, a
    closed main, a blocked filter. Collapsing that to None made the caller fall
    back to the time-based volume and credit a zone that received nothing."""
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    zone = _zone(
        **{
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_LIFETIME,
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)
    current = {"st": _flow_state(0)}
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    await c._sc_start_flow_sampling(zone)
    for at in (15.0, 30.0, 45.0):
        # The counter never moves, but it keeps REPORTING that it has not moved -
        # a fresh State object per poll, which is what HA writes when a sensor
        # sends a value. Re-using one object instead would model a sensor that
        # has gone quiet, and a quiet sensor has measured nothing at all.
        current["st"] = _flow_state(0)
        c._sc_sample_flow(2, at)

    measured, _end = c._sc_finish_flow(2)

    assert measured == 0.0, "a live meter that integrated nothing must say 0.0"


async def test_an_early_stop_with_a_dry_meter_still_credits_time_based():
    """A run stopped five seconds in reads 0.0 L because the water has not
    reached the sensor yet, not because the cistern is empty. The completion
    path treats a 0.0 as a failure; this one must not - the same reason the
    classic runner gates its dry branch on `not stopped` (irrigation.py:1580)."""
    c = _coord()
    run = {
        const.RUN_ZONE_ID: 2,
        const.RUN_STARTED: "2026-06-30T08:00:00+00:00",
        const.RUN_PLANNED_SECONDS: 600.0,
        const.RUN_PLANNED_MM: 4.0,
        const.RUN_PRE_BUCKET: -5.0,
        const.RUN_CREDITED: True,
    }
    c.store.async_get_config = AsyncMock(
        return_value={const.CONF_ACTIVE_VALVE_RUNS: [run]}
    )
    c.store.get_zone = Mock(return_value=_zone(**{const.ZONE_BUCKET: -1.0}))
    c._sc_finish_flow = Mock(return_value=(0.0, {}))
    c._sc_elapsed = Mock(return_value=300.0)
    c._timed_volume_l = Mock(return_value=10.0)
    # Consulted only by the measured branch, which a stop must not take here.
    c._credited_depth_native = Mock(return_value=99.0)

    await c.async_stop_self_closing(2)

    assert c._record_run.await_args.kwargs["volume_l"] == 10.0
    c._credited_depth_native.assert_not_called()


def _dry_finish_coord():
    """A self-closing run about to finalise with a live meter that read 0.0."""
    c = _coord()
    c._set_zone_fault = Mock()
    c._clear_zone_fault = Mock()
    c.async_write_watered_bucket = AsyncMock()
    c._flow_calibration_check = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(0.0, {}))
    c._credited_depth_native = Mock(return_value=0.0)
    c._timed_volume_l = Mock(return_value=20.0)  # must NOT reach the record
    c.store.get_zone = Mock(
        return_value=_zone(
            **{
                const.ZONE_BUCKET: 0.0,  # the optimistic open credit, satisfied
                const.ZONE_MAXIMUM_BUCKET: 24.0,
                const.ZONE_LINKED_ENTITY: "valve.beet",
            }
        )
    )
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_PLANNED_SECONDS: 600.0,
                    const.RUN_PRE_BUCKET: -2.0,
                }
            ]
        }
    )
    return c


async def test_a_dry_run_is_recorded_as_a_failure_and_raises_the_fault():
    """The leading case for this change: a dry cistern behind a live sensor. The
    run was credited optimistically at open and measured nothing, so it is a
    failed run - the same verdict and the same constant the classic metered
    runner reaches for this state (irrigation.py:1586)."""
    c = _dry_finish_coord()

    await c._sc_finish_run(2)

    kwargs = c._record_run.await_args.kwargs
    assert kwargs["result"] == const.RUN_RESULT_FAILED
    assert kwargs["detail"] == const.FAULT_FLOW_NEVER_STARTED
    assert kwargs["volume_l"] == 0.0
    c._set_zone_fault.assert_called_once_with(2, const.FAULT_FLOW_NEVER_STARTED)
    # The optimistic credit is reversed to the level the run started from, so
    # the deficit survives and the zone comes due again.
    c.async_write_watered_bucket.assert_awaited_once_with(2, -2.0)


async def test_a_dry_run_does_not_clear_the_zone_fault_it_just_raised():
    """The one line this change shares with the fault-lifecycle fix underneath it:
    a completed run clears the fault, and a dry one must not - it would put out
    the lamp it just lit.
    The chain and the deferred calculation still run: _sc_finish_run is a link,
    unlike the classic runner, and returning early here strands the cycle."""
    c = _dry_finish_coord()
    c._chain_advance_for_run = AsyncMock()
    c.async_run_deferred_calculation = AsyncMock()

    await c._sc_finish_run(2)

    c._clear_zone_fault.assert_not_called()
    c._chain_advance_for_run.assert_awaited_once()
    c.async_run_deferred_calculation.assert_awaited_once()


async def test_a_dry_run_is_not_a_calibration_sample():
    """_flow_calibration_check short-circuits on `measured_l is None`, so until
    the collapse was removed a dry run never reached it. A 0.0 walks past that
    guard and would be banked as an observed rate of 0 L/min - dragging the
    mean down until the advisory recommends a throughput the hardware never
    had."""
    c = _dry_finish_coord()

    await c._sc_finish_run(2)

    c._flow_calibration_check.assert_not_awaited()


async def test_a_run_resumed_after_a_restart_is_never_called_dry():
    """A marker that the sampler ran for the whole run was considered and is
    not built, and this is why: _sc_meters is in-memory only, and
    async_resume_self_closing_runs re-arms the cleanup, the master hold and the
    valve watcher but never _sc_start_flow_sampling. So the pop in
    _sc_finish_flow finds nothing and the function is out before `d` is read -
    a resumed run cannot be dry.

    The marker would be needed if the verdict were taken at the caller on
    `measured is None`. Mutate `dry` to `not measured` and this test goes red,
    which is the whole argument in one assertion. If it ever fails for another
    reason, build the marker."""
    c = _coord()
    c._set_zone_fault = Mock()
    c._flow_calibration_check = AsyncMock()
    c._timed_volume_l = Mock(return_value=20.0)
    c.store.get_zone = Mock(
        return_value=_zone(
            **{const.ZONE_FLOW_SENSOR: "sensor.beet_flow", const.ZONE_BUCKET: -2.0}
        )
    )
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_PLANNED_SECONDS: 600.0,
                    const.RUN_PRE_BUCKET: -2.0,
                }
            ]
        }
    )
    # The restart: a fresh process has an empty meter map, and nothing on the
    # resume path refills it. _sc_finish_flow is NOT stubbed here - the real one
    # is the thing under test.
    assert c._sc_meters() == {}

    await c._sc_finish_run(2)

    c._set_zone_fault.assert_not_called()
    assert c._record_run.await_args.kwargs["result"] == const.RUN_RESULT_COMPLETED


async def test_a_sensor_that_died_after_the_open_read_is_not_a_dry_run(monkeypatch):
    """_flow_build_meter feeds the valve-open reading INTO the meter, so
    `_have_reading` is true from the first second and `delivered()` never returns
    None again - however dead the sensor goes afterwards. Without this the dry
    verdict cannot tell "watched the whole run, saw no water" from "answered once
    at the open and was never heard from again", and writes the second one off."""
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    zone = _zone(
        **{
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_LIFETIME,
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)
    current = {"st": _flow_state(0)}  # readable at the open...
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    await c._sc_start_flow_sampling(zone)
    current["st"] = None  # ...and unavailable from then on, close included
    for at in (15.0, 30.0, 45.0):
        c._sc_sample_flow(2, at)

    measured, _end = c._sc_finish_flow(2)

    assert measured is None, "a meter that only ever read at the open measured nothing"


async def test_a_totalizer_that_reset_mid_run_is_not_a_dry_run(monkeypatch):
    """A hold-until-reset counter on a zone whose type is still being learned
    resolves to the over-credit-safe 'lifetime', which KEEPS the pre-reset
    baseline - so the post-reset climb never rises above it and measures 0.0
    while real water flowed.

    The classic runner diverts exactly this case to a time-based credit before
    its dry branch can see it (irrigation.py:1536), and pins it with
    test_metered_run.py::test_metered_zone_auto_hold_until_reset_credits_timed_not_fault.
    This path mirrored that dry branch without its precondition."""
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    # No counter-type override and no learned streak -> flow_learn_resolve gives
    # 'lifetime', the state a per-run counter sits in until the streak converges.
    zone = _zone(**{const.ZONE_FLOW_SENSOR: "sensor.beet_flow"})
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)
    current = {"st": _flow_state(1000)}  # still holding the previous run's total
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    await c._sc_start_flow_sampling(zone)
    current["st"] = _flow_state(0)  # the counter resets just after the open
    c._sc_sample_flow(2, 15.0)
    current["st"] = _flow_state(45)  # and then climbs: 45 L really delivered
    c._sc_sample_flow(2, 30.0)

    meter = c._sc_meters()[2][0]
    assert meter.delivered() == 0.0, "precondition: the baseline hides the climb"
    assert meter.saw_reset() is True, "precondition: the reset was observed"

    measured, _end = c._sc_finish_flow(2)

    assert measured is None, "a reset the meter cannot price is a gap, not a dry run"


def test_the_flow_read_carries_the_states_report_time():
    """hass.states.get hands back the SAME State object while the sensor stays
    quiet, so a read alone cannot say whether the value is fresh. The read
    carries State.last_reported so the meter can tell."""
    c = _coord()
    st = _flow_state(0, reported=_REPORT_EPOCH)
    c.hass.states.get = Mock(return_value=st)
    assert c._read_flow_sample("sensor.flow")[3] == _REPORT_EPOCH


async def test_a_run_whose_sensor_never_reported_keeps_its_time_based_credit(
    monkeypatch,
):
    """A sensor that updates less often than the run lasts - a cloud-polled
    controller, a utility meter reporting every few minutes, a counter that
    reports only after the valve closes - is read on every poll and reports on
    none of them. Writing that run off as dry reverses a credit the zone earned,
    raises a fault that stays on and waters the zone again at the next
    opportunity. master credits it by time, and so must this: without a report
    after the open the meter has measured nothing.

    Note what the harness does NOT do: it hands back one State object, exactly
    as hass.states.get does while a sensor stays quiet."""
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    c._set_zone_fault = Mock()
    c._clear_zone_fault = Mock()
    c.async_write_watered_bucket = AsyncMock()
    c._flow_calibration_check = AsyncMock()
    c._credited_depth_native = Mock(return_value=10.0)
    c._timed_volume_l = Mock(return_value=20.0)
    zone = _zone(
        **{
            const.ZONE_FLOW_SENSOR: "sensor.beet_flow",
            const.ZONE_FLOW_COUNTER_TYPE: const.FLOW_COUNTER_LIFETIME,
            const.ZONE_BUCKET: 0.0,
            const.ZONE_MAXIMUM_BUCKET: 24.0,
        }
    )
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)
    c.store.async_get_config = AsyncMock(
        return_value={
            const.CONF_ACTIVE_VALVE_RUNS: [
                {
                    const.RUN_ZONE_ID: 2,
                    const.RUN_PLANNED_SECONDS: 600.0,
                    const.RUN_PRE_BUCKET: -2.0,
                }
            ]
        }
    )
    quiet = _flow_state(0)  # ONE state, its report older than the open
    c.hass.states.get = Mock(return_value=quiet)

    await c._sc_start_flow_sampling(zone)
    for at in (15.0, 30.0, 45.0):
        c._sc_sample_flow(2, at)

    await c._sc_finish_run(2)

    kwargs = c._record_run.await_args.kwargs
    assert kwargs["result"] == const.RUN_RESULT_COMPLETED
    assert kwargs["volume_l"] == 20.0, "the time-based volume, as master credits it"
    c._set_zone_fault.assert_not_called()
    c._clear_zone_fault.assert_called_once_with(2)


async def test_a_negative_resting_offset_is_not_a_measurement_either(monkeypatch):
    """A rate sensor with a small negative resting offset measures BELOW zero on
    a run it did not account for, so the guard has to test `<= 0` and not
    `== 0`: at `== 0` a -0.2 L walks past it and is written off as dry, which
    is the regression this guard exists to prevent.

    The run is unmeasured for the usual reason - two intervals priced, then a
    gap the meter refuses to integrate across, and 12 L/min flowing in it."""
    import custom_components.irrigation_plus.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    zone = _zone(**{const.ZONE_FLOW_SENSOR: "sensor.beet_flow"})
    store_zone = dict(zone)
    c.store.get_zone = Mock(side_effect=lambda zid: store_zone)
    current = {"st": _flow_state(-0.4, unit="L/min")}
    c.hass.states.get = Mock(side_effect=lambda eid: current["st"])

    await c._sc_start_flow_sampling(zone)
    for at in (15.0, 30.0):
        current["st"] = _flow_state(-0.4, unit="L/min")
        c._sc_sample_flow(2, at)
    current["st"] = _flow_state(12.0, unit="L/min")  # live again after a 90 s gap
    c._sc_sample_flow(2, 120.0)

    meter = c._sc_meters()[2][0]
    assert meter.delivered() < 0, "precondition: the resting offset integrates negative"

    measured, _end = c._sc_finish_flow(2)

    assert measured is None, "a negative reading is no more measured than a zero"
