"""Self-closing valve mode (Phase 1)."""

from unittest.mock import AsyncMock, Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.irrigation import SI_VALVE_SUPPRESS_MARGIN


def _coord():
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.hass.services.async_call = AsyncMock()
    c.hass.bus.async_fire = Mock()
    c.store = Mock()
    c.store.async_get_config = AsyncMock(return_value={})
    c.store.async_update_zone = AsyncMock()
    c.store.async_update_config = AsyncMock()
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


def _flow_state(value, unit="L"):
    """A fake HA state for a flow sensor (value + unit_of_measurement)."""
    st = Mock()
    st.state = str(value)
    st.attributes = {"unit_of_measurement": unit}
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
    # zone 1 overdue (elapsed 10000 >= 60), zone 2 partial (elapsed 100 < 600)
    c._sc_elapsed = Mock(side_effect=[10000.0, 100.0])

    await c.async_resume_self_closing_runs()

    c._sc_finish_run.assert_awaited_once_with(1)
    c._sc_schedule_cleanup.assert_called_once_with(2, 500.0)


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
    import custom_components.smart_irrigation.self_closing as scmod

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
    import custom_components.smart_irrigation.self_closing as scmod

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
    import custom_components.smart_irrigation.self_closing as scmod

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
    import custom_components.smart_irrigation.self_closing as scmod

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


async def test_self_closing_measured_bucket_reconciles_from_pre_bucket(monkeypatch):
    """I-2 regression: when the optimistic TIME-based open credit CLAMPS at the ceiling
    but the MEASURED volume is smaller, the finish reconciles the bucket ABSOLUTELY from
    the stashed pre-run level — it must NOT over-empty via a delta correction.

    pre_bucket 0, maximum_bucket 20; time-based credit = 30 mm -> open clamps to 20;
    measured = 10 L -> bucket must land at min(20, 0 + 10) = 10, NOT the delta result
    20 + (10 - 30) = 0.
    """
    import custom_components.smart_irrigation.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    c._timed_volume_l = Mock(return_value=30.0)  # time-based open credit -> depth 30
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
    import custom_components.smart_irrigation.self_closing as scmod

    monkeypatch.setattr(scmod, "async_track_time_interval", Mock(return_value=Mock()))

    c = _coord()
    c._timed_volume_l = Mock(return_value=30.0)  # open credit depth 30 (identity depth)
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


async def test_self_closing_final_read_captures_last_climb(monkeypatch):
    """FM #3 regression: _sc_finish_flow takes ONE final reading at close, so a totalizer's
    last (up to a poll interval) of climb after the last periodic sample is not dropped.
    """
    import custom_components.smart_irrigation.self_closing as scmod

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
    # Measured 6 L in 60 s -> observed 6 L/min == +50% over the configured 4 L/min.
    for _ in range(const.FLOW_CAL_MIN_SAMPLES):
        await c._flow_calibration_check(zone, measured_l=6.0, seconds=60.0)
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
