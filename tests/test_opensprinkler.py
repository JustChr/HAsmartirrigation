"""OpenSprinkler station mode.

The station is queued, not opened, so almost every assertion here is about the
difference between *dispatched* and *watering*: nothing may be timed, sampled,
confirmed or finalised from the dispatch instant.

Driven against the real ``hass`` fixture rather than a double, because the mode
is built out of things a double replaces - state attributes, the entity
registry, and a state subscription that has to survive the gap between dispatch
and the station's turn.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock

from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.opensprinkler import (
    observed_start_iso,
    queue_deadline_seconds,
    resolve_running_sensor,
    zone_watch_entity,
)

STATION = "switch.front_south_station_enabled"
RUNNING = "binary_sensor.front_south_station_running"


def _attrs(index=0, is_master=False, program_id=0, **extra):
    a = {
        const.OPENSPRINKLER_ATTR_TYPE: const.OPENSPRINKLER_TYPE_STATION,
        const.OPENSPRINKLER_ATTR_INDEX: index,
        const.OPENSPRINKLER_ATTR_IS_MASTER: is_master,
        const.OPENSPRINKLER_ATTR_PROGRAM_ID: program_id,
    }
    a.update(extra)
    return a


def _publish(hass, *, running="off", program_id=0, station="on", index=0, extra=None):
    """Publish a controller state: the enabled switch plus its running sensor."""
    extra = extra or {}
    hass.states.async_set(
        STATION, station, _attrs(index=index, program_id=program_id, **extra)
    )
    hass.states.async_set(
        RUNNING, running, _attrs(index=index, program_id=program_id, **extra)
    )


async def _drive(hass, **kw):
    """Publish a controller state and let the subscription react to it."""
    _publish(hass, **kw)
    await hass.async_block_till_done()


def _coord(hass):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = hass
    c.store = Mock()
    c._runs = []
    c.store.async_get_config = AsyncMock(side_effect=lambda: {})
    c.store.async_update_zone = AsyncMock()
    c.store.async_update_config = AsyncMock()
    c.store.get_zone = Mock(return_value=None)
    c._record_run = AsyncMock()
    c._sc_schedule_cleanup = Mock()
    c._set_zone_fault = Mock()
    c._si_driven_until = {}
    c.async_master_acquire = AsyncMock()
    c.async_master_release = AsyncMock()
    c.async_run_deferred_calculation = AsyncMock()
    c._confirm_valve_running = AsyncMock(return_value=True)
    c._timed_volume_l = Mock(return_value=20.0)
    c._credited_depth_native = Mock(return_value=4.0)
    c._flow_calibration_check = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    # Keep the run list in memory so a whole lifecycle can be driven through.
    c._sc_active_runs = AsyncMock(side_effect=lambda: list(c._runs))

    c.store.config = Mock()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_PARALLEL
    c.store.config.active_valve_runs = c._runs

    async def _persist(runs):
        c._runs = list(runs)
        # zone_run_in_flight reads the config copy, so the chain only sees a run
        # clear when both do.
        c.store.config.active_valve_runs = c._runs

    c._sc_persist_runs = AsyncMock(side_effect=_persist)
    # Record the two controller services instead of calling a controller.
    c._os_calls = {
        "run": async_mock_service(hass, "opensprinkler", "run_station"),
        "stop": async_mock_service(hass, "opensprinkler", "stop"),
    }
    return c


def _zone(**kw):
    z = {
        const.ZONE_ID: 2,
        const.ZONE_NAME: "Front South",
        const.ZONE_DURATION: 600.0,
        const.ZONE_WATERING_MODE: const.WATERING_MODE_OPENSPRINKLER,
        const.ZONE_LINKED_ENTITY: STATION,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_MAXIMUM_BUCKET: 50.0,
    }
    z.update(kw)
    return z


def _buckets(coord):
    return [
        ck.args[1][const.ZONE_BUCKET]
        for ck in coord.store.async_update_zone.await_args_list
        if const.ZONE_BUCKET in ck.args[1]
    ]


# --------------------------------------------------------------------------- #
# Derivation from the station's attributes
# --------------------------------------------------------------------------- #
async def test_running_sensor_resolves_from_attributes_not_the_entity_id(hass):
    """A renamed running sensor still resolves: the match is index + type."""
    hass.states.async_set(STATION, "on", _attrs())
    hass.states.async_set("binary_sensor.renamed_by_the_user", "off", _attrs())
    assert resolve_running_sensor(hass, STATION) == "binary_sensor.renamed_by_the_user"


async def test_running_sensor_ignores_a_different_station_index(hass):
    hass.states.async_set(STATION, "on", _attrs(index=0))
    hass.states.async_set(RUNNING, "off", _attrs(index=5))
    assert resolve_running_sensor(hass, STATION) is None


async def test_running_sensor_is_none_when_there_is_no_sensor(hass):
    hass.states.async_set(STATION, "on", _attrs())
    assert resolve_running_sensor(hass, STATION) is None


async def test_running_sensor_is_none_when_the_controller_is_unreachable(hass):
    """An unavailable entity carries no attributes, so nothing is derivable."""
    _publish(hass)
    hass.states.async_set(STATION, "unavailable", {})
    assert resolve_running_sensor(hass, STATION) is None


async def test_watch_entity_is_the_running_sensor_not_the_enabled_switch(hass):
    """The station-enabled switch is on permanently, so a consumer that means
    "is water flowing" must never be pointed at it."""
    _publish(hass)
    assert zone_watch_entity(hass, _zone()) == RUNNING
    classic = _zone(
        **{
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
            const.ZONE_LINKED_ENTITY: "switch.plain",
        }
    )
    assert zone_watch_entity(hass, classic) == "switch.plain"


async def test_a_classic_zone_linked_to_a_station_still_watches_the_sensor(hass):
    """The misconfiguration is exactly where the mode cannot be trusted.

    Its run is refused, but pointing the zone's watering-now sensor at the
    enabled switch would leave it on for ever, and observed watering would read
    that as a valve nobody ever closes and credit against it. Live, the sensor
    sat on for a zone Smart Irrigation had just refused to run.
    """
    _publish(hass)
    mislinked = _zone(
        **{
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
            const.ZONE_LINKED_ENTITY: STATION,
        }
    )
    assert zone_watch_entity(hass, mislinked) == RUNNING


async def test_watch_entity_falls_back_while_the_controller_is_unknown(hass):
    """Before the OpenSprinkler integration publishes anything, a station entity
    is indistinguishable from any other switch. The linked entity is the only
    answer available; a dispatch re-signals once the station resolves."""
    assert zone_watch_entity(hass, _zone()) is None
    classic = _zone(
        **{
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
            const.ZONE_LINKED_ENTITY: STATION,
        }
    )
    assert zone_watch_entity(hass, classic) == STATION


# --------------------------------------------------------------------------- #
# Dispatch
# --------------------------------------------------------------------------- #
async def test_dispatch_payload_is_entity_targeted_run_station(hass):
    c = _coord(hass)
    await c._sc_dispatch_open(_zone())
    assert len(c._os_calls["run"]) == 1
    data = dict(c._os_calls["run"][0].data)
    assert data == {
        "entity_id": STATION,
        "run_seconds": 600,
        "queue_option": "append",
    }
    # cv.make_entity_service_schema rejects any extra key, so the zone_id /
    # zone_name the plain service adapter injects must not be here.
    assert "zone_id" not in data and "zone_name" not in data


async def test_dispatch_neither_confirms_nor_samples_nor_times_the_run(hass):
    """All three would measure the controller's queue rather than the run."""
    _publish(hass)
    c = _coord(hass)
    zone = _zone(**{const.ZONE_CONFIRM_ENTITY: "binary_sensor.someone_set_this"})
    assert await c.async_run_self_closing(zone) is True
    c._confirm_valve_running.assert_not_awaited()
    c._sc_start_flow_sampling.assert_not_awaited()
    c._sc_schedule_cleanup.assert_not_called()


async def test_dispatch_persists_the_watch_entity_and_no_observed_start(hass):
    _publish(hass)
    c = _coord(hass)
    assert await c.async_run_self_closing(_zone()) is True
    run = c._runs[0]
    assert run[const.RUN_WATCH_ENTITY] == RUNNING
    assert const.RUN_OBSERVED_START not in run
    assert run[const.RUN_MODE] == const.WATERING_MODE_OPENSPRINKLER
    assert run[const.RUN_PRE_BUCKET] == -5.0
    # The bucket is still credited at dispatch: a queued run lives in the
    # controller and is delivered whether or not HA stays up.
    assert _buckets(c) == [-1.0]


async def test_dispatch_is_refused_when_the_running_sensor_cannot_be_resolved(hass):
    """Without it nothing could ever end the run, so nothing is actuated."""
    hass.states.async_set(STATION, "on", _attrs())
    c = _coord(hass)
    assert await c.async_run_self_closing(_zone()) is False
    assert c._os_calls["run"] == []
    c._set_zone_fault.assert_called_once_with(2, const.PROBLEM_STATION_UNRESOLVED)
    assert c._runs == []


# --------------------------------------------------------------------------- #
# The queued lifecycle, driven through the real subscription
# --------------------------------------------------------------------------- #
async def test_a_queued_station_only_starts_the_run_when_it_actually_runs(hass):
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone())

    # Accepted by the controller, but three stations ahead of it.
    await _drive(hass, running="off", program_id=99)
    assert const.RUN_OBSERVED_START not in c._runs[0]
    c._sc_start_flow_sampling.assert_not_awaited()

    # Its turn comes round.
    await _drive(hass, running="on", program_id=99)
    assert c._runs[0][const.RUN_OBSERVED_START] is not None
    c._sc_start_flow_sampling.assert_awaited_once()
    c._sc_schedule_cleanup.assert_called_once_with(2, 600.0)


async def test_the_run_is_anchored_to_the_controllers_start_not_the_poll(hass):
    """The integration polls, so "on" arrives up to a poll interval late.

    Timing the run from that sighting shortens it by the lag, which is what made
    a full run record as an early stop on real hardware. The controller reports
    when the station really started; that is the anchor.
    """
    started = dt_util.utcnow() - timedelta(seconds=4)
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone())

    await _drive(
        hass,
        running="on",
        program_id=99,
        extra={const.OPENSPRINKLER_ATTR_START_TIME: started.isoformat()},
    )
    assert c._runs[0][const.RUN_OBSERVED_START] == started.isoformat()


async def test_a_full_run_completes_even_though_both_ends_were_seen_late(hass):
    """The regression this anchoring exists for.

    Poll lag at both ends used to leave the measured window short of planned, and
    the one-second slack in the completion test could not absorb it, so a run the
    controller finished in full settled as an early stop with its credit scaled
    down. Live, that hit two of four full 60 s runs.
    """
    planned = 60.0
    started = dt_util.utcnow() - timedelta(seconds=planned + 2)
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone(**{const.ZONE_DURATION: planned}))
    c.store.get_zone = Mock(return_value=_zone(**{const.ZONE_DURATION: planned}))

    await _drive(
        hass,
        running="on",
        program_id=99,
        extra={const.OPENSPRINKLER_ATTR_START_TIME: started.isoformat()},
    )
    c._sc_finish_run = AsyncMock()
    c.async_stop_self_closing = AsyncMock()
    await _drive(hass, running="off", program_id=0)

    c._sc_finish_run.assert_awaited_once()
    c.async_stop_self_closing.assert_not_awaited()


async def test_an_implausible_reported_start_falls_back_to_the_observation(hass):
    """It comes off the controller's clock via its timezone offset.

    A mis-set clock must not be able to claim a run began tomorrow, or long
    before it could have: that would mis-size every window measured from it.
    """
    _publish(hass, running="on", program_id=99)
    for raw in (
        (dt_util.utcnow() + timedelta(hours=3)).isoformat(),
        (dt_util.utcnow() - timedelta(hours=9)).isoformat(),
        "not a timestamp",
        None,
    ):
        hass.states.async_set(
            RUNNING, "on", _attrs(program_id=99, **{"start_time": raw})
        )
        got = observed_start_iso(hass, RUNNING, 600.0)
        assert abs((dt_util.parse_datetime(got) - dt_util.utcnow()).total_seconds()) < 5


# --------------------------------------------------------------------------- #
# Zone sequencing, which Smart Irrigation has to apply itself
# --------------------------------------------------------------------------- #
STATION_B = "switch.front_north_station_enabled"
RUNNING_B = "binary_sensor.front_north_station_running"


def _publish_b(hass, *, running="off", program_id=0):
    hass.states.async_set(STATION_B, "on", _attrs(index=1, program_id=program_id))
    hass.states.async_set(RUNNING_B, running, _attrs(index=1, program_id=program_id))


def _two_zones(hass, c, sequencing):
    """Two station zones on one controller, and the coordinator to run them."""
    _publish(hass)
    _publish_b(hass)
    c.store.config.zone_sequencing = sequencing
    zones = {
        2: _zone(**{const.ZONE_DURATION: 60.0}),
        3: _zone(
            **{
                const.ZONE_ID: 3,
                const.ZONE_DURATION: 60.0,
                const.ZONE_LINKED_ENTITY: STATION_B,
            }
        ),
    }
    c.store.get_zone = Mock(side_effect=lambda z: zones.get(int(z)))
    return list(zones.values())


def _dispatched(c):
    return [call.data["entity_id"] for call in c._os_calls["run"]]


async def test_parallel_hands_the_controller_every_station_at_once(hass):
    """Which is what lets its own per-station scheduling decide, and what keeps
    a whole cycle in its queue across a restart."""
    c = _coord(hass)
    zones = _two_zones(hass, c, const.CONF_ZONE_SEQUENCING_PARALLEL)
    await c.async_dispatch_opensprinkler_zones(zones, trigger="schedule")
    assert _dispatched(c) == [STATION, STATION_B]


async def test_sequential_holds_the_second_station_until_the_first_finishes(hass):
    """A controller may run stations concurrently, so 'sequential' only means
    anything if Smart Irrigation withholds the next dispatch itself."""
    c = _coord(hass)
    zones = _two_zones(hass, c, const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
    await c.async_dispatch_opensprinkler_zones(zones, trigger="schedule")
    assert _dispatched(c) == [STATION]

    # The first station waters and stops; only now does the second go out.
    await _drive(hass, running="on", program_id=99)
    assert _dispatched(c) == [STATION]
    await _drive(hass, running="off", program_id=0)
    assert _dispatched(c) == [STATION, STATION_B]


async def test_a_refused_zone_does_not_stall_the_chain(hass):
    """The second zone's station cannot be resolved, so its dispatch is refused.
    The third must still get its turn rather than the cycle stopping there."""
    c = _coord(hass)
    zones = _two_zones(hass, c, const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
    broken = _zone(
        **{
            const.ZONE_ID: 4,
            const.ZONE_DURATION: 60.0,
            const.ZONE_LINKED_ENTITY: "input_boolean.not_a_station",
        }
    )
    existing = c.store.get_zone.side_effect
    c.store.get_zone = Mock(side_effect=lambda z: broken if int(z) == 4 else existing(z))
    await c.async_dispatch_opensprinkler_zones(
        [zones[0], broken, zones[1]], trigger="schedule"
    )
    assert _dispatched(c) == [STATION]

    await _drive(hass, running="on", program_id=99)
    await _drive(hass, running="off", program_id=0)
    assert _dispatched(c) == [STATION, STATION_B]


async def test_the_chain_holds_one_master_token_for_the_whole_cycle(hass):
    """Per-run holds would drop the master in the gap between two stations."""
    c = _coord(hass)
    zones = _two_zones(hass, c, const.CONF_ZONE_SEQUENCING_SEQUENTIAL)
    await c.async_dispatch_opensprinkler_zones(zones, trigger="schedule")
    chain_tokens = {
        ck.args[0]
        for ck in c.async_master_acquire.await_args_list
        if str(ck.args[0]).startswith("os-chain:")
    }
    assert len(chain_tokens) == 1
    assert not [
        ck
        for ck in c.async_master_release.await_args_list
        if str(ck.args[0]).startswith("os-chain:")
    ]

    await _drive(hass, running="on", program_id=99)
    await _drive(hass, running="off", program_id=0)
    _publish_b(hass, running="on", program_id=99)
    await hass.async_block_till_done()
    _publish_b(hass, running="off", program_id=0)
    await hass.async_block_till_done()
    assert [
        ck.args[0]
        for ck in c.async_master_release.await_args_list
        if str(ck.args[0]).startswith("os-chain:")
    ] == list(chain_tokens)


async def test_a_station_the_controller_drops_is_written_off_immediately(hass):
    """A controller-side rain delay, a water level of 0 or a stop-all: the
    program id returns to 0 without the station ever having run."""
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone(**{const.ZONE_BUCKET: -1.0}))

    await _drive(hass, running="off", program_id=99)
    await _drive(hass, running="off", program_id=0)

    assert c._runs == []
    # The optimistic dispatch credit is unwound all the way back to pre_bucket:
    # nothing was delivered.
    assert _buckets(c)[-1] == -5.0
    assert c._record_run.await_args.kwargs["actual_s"] == 0.0
    assert (
        c._record_run.await_args.kwargs["detail"]
        == const.RUN_DETAIL_STATION_NEVER_RAN
    )
    c._set_zone_fault.assert_called_with(2, const.PROBLEM_STATION_NEVER_RAN)


async def test_a_program_id_of_zero_before_acceptance_is_not_a_drop(hass):
    """Straight after dispatch the controller has not answered yet, and reading
    that as a drop would abort every single run."""
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone())
    await _drive(hass, running="off", program_id=0)
    assert len(c._runs) == 1


async def test_an_unavailable_station_is_not_a_drop(hass):
    """HA drops an entity's attributes while it is unavailable, so the program
    id reads as absent rather than as 0."""
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone())
    await _drive(hass, running="off", program_id=99)
    hass.states.async_set(RUNNING, "unavailable", {})
    await hass.async_block_till_done()
    assert len(c._runs) == 1


async def test_a_station_stopping_short_settles_as_a_partial_run(hass):
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone())
    await _drive(hass, running="on", program_id=99)
    await _drive(hass, running="off", program_id=0)

    assert c._runs == []
    assert c._record_run.await_args.kwargs["result"] == const.RUN_RESULT_PARTIAL
    # Elapsed is measured from the OBSERVED start, so it is ~0 here rather than
    # the whole time since the run was dispatched.
    assert c._record_run.await_args.kwargs["actual_s"] < 5


async def test_the_station_is_not_watched_after_the_run_ends(hass):
    """A surviving subscription would observe the NEXT run's station."""
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone())
    await _drive(hass, running="on", program_id=99)
    await _drive(hass, running="off", program_id=0)
    assert c._os_watchers() == {}


async def test_stopping_a_zone_sends_the_entity_targeted_stop(hass):
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    c.store.get_zone = Mock(return_value=_zone())

    await c.async_stop_self_closing(2)

    assert len(c._os_calls["stop"]) == 1
    assert dict(c._os_calls["stop"][0].data) == {"entity_id": STATION}


async def test_a_second_dispatch_on_a_queued_zone_is_refused(hass):
    """Re-queueing a cycle the controller has already accepted would water it
    twice: it honours both."""
    _publish(hass)
    c = _coord(hass)
    await c.async_run_self_closing(_zone())
    await _drive(hass, running="off", program_id=99)
    c.store.config = Mock()
    c.store.config.active_valve_runs = c._runs

    assert await c.async_run_self_closing(_zone()) is False
    assert len(c._runs) == 1


# --------------------------------------------------------------------------- #
# In-flight bounds
# --------------------------------------------------------------------------- #
def _run(zone_id=2, planned=600.0, started="2026-08-04T10:00:00+00:00", **kw):
    run = {
        const.RUN_ZONE_ID: zone_id,
        const.RUN_PLANNED_SECONDS: planned,
        const.RUN_STARTED: started,
        const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER,
    }
    run.update(kw)
    return run


def test_the_deadline_scales_with_what_the_run_is_queued_behind():
    runs = [_run(zone_id=1, planned=5700.0), _run(zone_id=2, planned=600.0)]
    alone = queue_deadline_seconds([runs[1]], runs[1])
    behind = queue_deadline_seconds(runs, runs[1])
    assert behind - alone == 5700.0
    assert alone == (
        const.OPENSPRINKLER_ACCEPT_SECONDS
        + 600.0
        + const.OPENSPRINKLER_QUEUE_MARGIN_SECONDS
    )


async def test_a_queued_run_stays_in_flight_past_its_own_planned_window(
    hass, freezer
):
    """The defect this mode has to avoid: a zone queued behind three others
    would otherwise stop counting as in flight while its station is still shut,
    dropping both the duplicate-dispatch guard and the calculation deferral in
    the middle of the queue."""
    c = _coord(hass)
    c.store.config = Mock()
    c.store.config.active_valve_runs = [
        _run(zone_id=1, planned=5700.0),
        _run(zone_id=2, planned=600.0),
    ]

    freezer.move_to("2026-08-04T10:30:00+00:00")  # 30 min after dispatch
    assert c.zone_run_in_flight(2) is True

    freezer.move_to("2026-08-04T14:00:00+00:00")  # past the whole queue
    assert c.zone_run_in_flight(2) is False


async def test_once_watering_the_window_is_measured_from_the_observed_start(
    hass, freezer
):
    c = _coord(hass)
    c.store.config = Mock()
    c.store.config.active_valve_runs = [
        _run(planned=600.0, observed_start="2026-08-04T12:00:00+00:00")
    ]
    freezer.move_to("2026-08-04T12:05:00+00:00")
    assert c.zone_run_in_flight(2) is True
    freezer.move_to("2026-08-04T12:15:00+00:00")
    assert c.zone_run_in_flight(2) is False


# --------------------------------------------------------------------------- #
# Restart reconciliation, in each of the three states
# --------------------------------------------------------------------------- #
async def test_restart_while_still_queued_keeps_waiting(hass, freezer):
    freezer.move_to("2026-08-04T10:05:00+00:00")
    _publish(hass, running="off", program_id=99)
    c = _coord(hass)
    c._runs = [_run(**{const.RUN_WATCH_ENTITY: RUNNING})]
    c.store.get_zone = Mock(return_value=_zone())

    await c.async_resume_self_closing_runs()

    assert len(c._runs) == 1
    assert 2 in c._os_watchers()
    c._sc_schedule_cleanup.assert_not_called()
    assert c._os_calls["run"] == [] and c._os_calls["stop"] == []


async def test_restart_mid_run_reschedules_only_the_remainder(hass, freezer):
    freezer.move_to("2026-08-04T12:03:00+00:00")
    _publish(hass, running="on", program_id=99)
    c = _coord(hass)
    c._runs = [
        _run(
            planned=600.0,
            observed_start="2026-08-04T12:00:00+00:00",
            **{const.RUN_WATCH_ENTITY: RUNNING},
        )
    ]
    c.store.get_zone = Mock(return_value=_zone())

    await c.async_resume_self_closing_runs()

    assert len(c._runs) == 1
    zone_id, remaining = c._sc_schedule_cleanup.call_args.args
    assert zone_id == 2 and 415 < remaining < 425
    # Never re-opened: the controller owns the valve, and an interrupted run is
    # an observation, not an action.
    assert c._os_calls["run"] == [] and c._os_calls["stop"] == []


async def test_restart_after_the_run_finished_finalises_it(hass, freezer):
    freezer.move_to("2026-08-04T12:20:00+00:00")
    _publish(hass, running="off", program_id=0)
    c = _coord(hass)
    c._runs = [
        _run(
            planned=600.0,
            observed_start="2026-08-04T12:00:00+00:00",
            **{const.RUN_WATCH_ENTITY: RUNNING},
        )
    ]
    c.store.get_zone = Mock(return_value=_zone())

    await c.async_resume_self_closing_runs()

    assert c._runs == []
    assert c._record_run.await_args.kwargs["result"] == const.RUN_RESULT_COMPLETED
    assert c._os_calls["run"] == [] and c._os_calls["stop"] == []


async def test_a_queued_run_resumed_after_a_restart_still_finishes(hass, freezer):
    """The whole point of persisting the watch entity: reconciliation must not
    depend on re-deriving it from an integration that may not have loaded yet."""
    freezer.move_to("2026-08-04T10:05:00+00:00")
    c = _coord(hass)
    c._runs = [_run(**{const.RUN_WATCH_ENTITY: RUNNING})]
    c.store.get_zone = Mock(return_value=_zone())

    # No OpenSprinkler entity exists yet at reconcile time.
    await c.async_resume_self_closing_runs()
    assert len(c._runs) == 1

    await _drive(hass, running="on", program_id=99)
    assert c._runs[0][const.RUN_OBSERVED_START] is not None


# --------------------------------------------------------------------------- #
# The classic path must never drive a station
# --------------------------------------------------------------------------- #
async def test_a_classic_zone_pointed_at_a_station_is_refused(hass):
    """turn_on on a station switch calls station.enable(): it rewrites the
    controller's configuration and waters nothing, while still reporting on."""
    _publish(hass)
    c = _coord(hass)
    c.store.config = Mock()
    c.store.config.zone_sequencing = const.CONF_ZONE_SEQUENCING_SEQUENTIAL
    hass.async_create_task = Mock()
    zone = _zone(**{const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC})

    await c._dispatch_sequencing([zone])

    hass.async_create_task.assert_not_called()
    c._set_zone_fault.assert_called_once_with(2, const.PROBLEM_STATION_WRONG_MODE)


def test_an_opensprinkler_zone_is_kept_off_every_classic_path():
    assert SmartIrrigationCoordinator._sc_is_self_closing(_zone()) is True
