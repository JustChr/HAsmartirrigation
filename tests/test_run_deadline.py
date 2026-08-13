"""Deadline truncation and the per-zone days-between counter.

The selection decides WHICH zones run; the deadline only decides where a run
that overruns gets cut. These cover the second half — that a run stops at its
finish target instead of watering past sunrise, and that being cut short does
not tell the days-between guard the unwatered zones just watered.
"""

import datetime
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


class _FakeStore:
    def __init__(self, zones=None, config=None):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}
        self.config = config if config is not None else Mock(spec=[])
        self.config_dict = {}

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(
            changes
        )
        return dict(self.zones[int(zone_id)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_update_config(self, changes):
        self.config_dict.update(changes)


def _coord(zones=None, config=None):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    # A real dict, not a Mock: claiming the chain dispatches _config_updated, and
    # the dispatcher iterates hass.data's target list.
    hass.data = {}
    coord.hass = hass
    coord.store = _FakeStore(zones, config)
    return coord


def _zone(zid, duration=600, **kw):
    z = {
        const.ZONE_ID: zid,
        const.ZONE_NAME: f"Z{zid}",
        const.ZONE_DURATION: duration,
        const.ZONE_LINKED_ENTITY: f"switch.z{zid}",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
    }
    z.update(kw)
    return z


class TestSequentialDeadline:
    """A sequential chain stops at its finish target."""

    async def test_a_zone_is_cut_to_the_remaining_window(self):
        coord = _coord()
        coord.async_master_release = AsyncMock()
        coord._run_trigger = Mock(return_value="schedule")
        ran = []
        coord._run_valve_metered = AsyncMock(
            side_effect=lambda z, e, **kw: ran.append(
                (z[const.ZONE_ID], z[const.ZONE_DURATION])
            )
        )
        deadline = dt_util.utcnow() + datetime.timedelta(seconds=400)
        await coord._irrigate_zones_sequential([_zone(0, 600)], deadline=deadline)
        assert len(ran) == 1
        assert ran[0][0] == 0
        # 600 s of demand against ~400 s of window: watered for what is left,
        # and the residual carries rather than overrunning the target.
        assert 390 <= ran[0][1] <= 400

    async def test_zones_past_the_deadline_are_not_started(self):
        coord = _coord()
        coord.async_master_release = AsyncMock()
        coord._run_trigger = Mock(return_value="schedule")
        ran = []
        coord._run_valve_metered = AsyncMock(
            side_effect=lambda z, e, **kw: ran.append(z[const.ZONE_ID])
        )
        deadline = dt_util.utcnow() - datetime.timedelta(seconds=1)
        await coord._irrigate_zones_sequential(
            [_zone(0), _zone(1), _zone(2)], deadline=deadline
        )
        assert ran == []

    async def test_without_a_deadline_nothing_is_truncated(self):
        coord = _coord()
        coord.async_master_release = AsyncMock()
        coord._run_trigger = Mock(return_value="schedule")
        ran = []
        coord._run_valve_metered = AsyncMock(
            side_effect=lambda z, e, **kw: ran.append(
                (z[const.ZONE_ID], z[const.ZONE_DURATION])
            )
        )
        await coord._irrigate_zones_sequential([_zone(0, 600), _zone(1, 900)])
        assert ran == [(0, 600), (1, 900)]


class TestParallelDeadline:
    """Opening every zone at once is not a reason to water past the target.

    Parallel has no sequence to truncate, but the selection does not guarantee
    the set fits either: when nothing in the driest group fits, ``select``
    keeps the leader deliberately and leaves the deadline to cut it. Under
    sequential and rotating it does; parallel is the same run, held by the same
    task, and has to cut it too.
    """

    async def test_a_zone_is_cut_to_the_remaining_window(self):
        coord = _coord()
        coord.async_master_acquire = AsyncMock()
        coord._run_trigger = Mock(return_value="schedule")
        started = []
        coord.hass.async_create_task = Mock()
        coord._run_valve_metered = Mock(
            side_effect=lambda z, e, **kw: started.append(
                (z[const.ZONE_ID], z[const.ZONE_DURATION])
            )
        )
        deadline = dt_util.utcnow() + datetime.timedelta(seconds=400)
        await coord._irrigate_zones_parallel(
            [_zone(0, 600), _zone(1, 120)], deadline=deadline
        )
        assert [s[0] for s in started] == [0, 1]
        assert 390 <= started[0][1] <= 400  # cut
        assert started[1][1] == 120  # inside the window, untouched

    async def test_zones_past_the_deadline_are_not_started(self):
        coord = _coord()
        coord.async_master_acquire = AsyncMock()
        coord._run_trigger = Mock(return_value="schedule")
        started = []
        coord.hass.async_create_task = Mock()
        coord._run_valve_metered = Mock(
            side_effect=lambda z, e, **kw: started.append(z[const.ZONE_ID])
        )
        deadline = dt_util.utcnow() - datetime.timedelta(seconds=1)
        await coord._irrigate_zones_parallel([_zone(0), _zone(1)], deadline=deadline)
        assert started == []

    async def test_without_a_deadline_nothing_is_truncated(self):
        coord = _coord()
        coord.async_master_acquire = AsyncMock()
        coord._run_trigger = Mock(return_value="schedule")
        started = []
        coord.hass.async_create_task = Mock()
        coord._run_valve_metered = Mock(
            side_effect=lambda z, e, **kw: started.append(
                (z[const.ZONE_ID], z[const.ZONE_DURATION])
            )
        )
        await coord._irrigate_zones_parallel([_zone(0, 600), _zone(1, 900)])
        assert started == [(0, 600), (1, 900)]


class TestResizeQueuedZone:
    """Re-pricing a zone that has been waiting its turn."""

    async def test_no_live_gate_leaves_the_zone_alone(self):
        coord = _coord(config=Mock(live_estimate_enabled=False))
        zone = _zone(0, 600)
        assert await coord._resize_queued_zone(zone, True) is zone

    async def test_a_shrunken_deficit_shortens_the_zone(self):
        coord = _coord([_zone(0, 600)], config=Mock(live_estimate_enabled=True))
        coord.async_refresh_zone_estimates = AsyncMock(return_value={})
        coord._zone_run_decision = Mock(
            return_value=Mock(duration=120.0, deficit=-2.0, ratio=1.2, resized=True)
        )
        out = await coord._resize_queued_zone(_zone(0, 600), True)
        assert out[const.ZONE_DURATION] == 120.0

    async def test_a_grown_deficit_does_not_lengthen_the_zone(self):
        # The run was dispatched against a window; silently extending a zone
        # past the length the selection was sized on would push the chain out.
        coord = _coord([_zone(0, 600)], config=Mock(live_estimate_enabled=True))
        coord.async_refresh_zone_estimates = AsyncMock(return_value={})
        coord._zone_run_decision = Mock(
            return_value=Mock(duration=9000.0, deficit=-9.0, ratio=4.0, resized=True)
        )
        out = await coord._resize_queued_zone(_zone(0, 600), True)
        assert out[const.ZONE_DURATION] == 600

    async def test_a_satisfied_zone_is_dropped_and_releases_its_marker(self):
        coord = _coord([_zone(0, 600)], config=Mock(live_estimate_enabled=True))
        coord.async_refresh_zone_estimates = AsyncMock(return_value={})
        coord._zone_run_decision = Mock(return_value=None)
        coord._live_run_zones = {0}
        assert await coord._resize_queued_zone(_zone(0, 600), True) is None
        # The dispatch took a live-crediting marker for this zone; leaving it
        # behind would hand the next run a ceiling meant for a run that never
        # happened.
        assert coord._live_run_zones == set()

    async def test_an_unavailable_estimate_leaves_the_zone_unchanged(self):
        coord = _coord([_zone(0, 600)], config=Mock(live_estimate_enabled=True))
        coord.async_refresh_zone_estimates = AsyncMock(side_effect=RuntimeError("nope"))
        zone = _zone(0, 600)
        assert await coord._resize_queued_zone(zone, True) is zone


class TestPerZoneDaysSince:
    """A truncated run must not claim the zones it never reached."""

    async def test_credited_water_resets_that_zone_only(self, monkeypatch):
        # The reset rides the credit, not the dispatch: a sequential or rotating
        # run is a background task still watering hours after dispatch returns,
        # so a dispatch-time reset would clear the counter for zones a deadline
        # never reaches — the starvation the per-zone counter exists to stop.
        monkeypatch.setattr(
            "custom_components.smart_irrigation.irrigation.async_dispatcher_send",
            Mock(),
        )
        coord = _coord(
            [
                _zone(0, bucket=-5.0, days_since_irrigation=4),
                _zone(1, bucket=-5.0, days_since_irrigation=4),
            ]
        )
        await coord.async_write_watered_bucket(0, 0.0)
        zones = {int(z[const.ZONE_ID]): z for z in await coord.store.async_get_zones()}
        assert zones[0][const.ZONE_DAYS_SINCE_IRRIGATION] == 0
        # Zone 1 was never reached. Its wait keeps running.
        assert zones[1][const.ZONE_DAYS_SINCE_IRRIGATION] == 4

    async def test_a_write_that_moves_no_water_does_not_reset(self, monkeypatch):
        # A failed / never-started run still commits an unchanged bucket. It has
        # not watered, so it must not restart the wait.
        monkeypatch.setattr(
            "custom_components.smart_irrigation.irrigation.async_dispatcher_send",
            Mock(),
        )
        coord = _coord([_zone(0, bucket=-5.0, days_since_irrigation=4)])
        await coord.async_write_watered_bucket(0, -5.0)
        zones = await coord.store.async_get_zones()
        assert zones[0][const.ZONE_DAYS_SINCE_IRRIGATION] == 4

    async def test_the_global_reset_leaves_zone_counters_alone(self):
        coord = _coord([_zone(0, days_since_irrigation=3)])
        await coord._reset_days_since_irrigation()
        assert coord.store.config_dict[const.CONF_DAYS_SINCE_LAST_IRRIGATION] == 0
        zones = await coord.store.async_get_zones()
        assert zones[0][const.ZONE_DAYS_SINCE_IRRIGATION] == 3

    async def test_midnight_bumps_every_zone(self):
        coord = _coord([_zone(0, days_since_irrigation=1), _zone(1)])
        coord.store.config_dict = {}

        async def get_config():
            return {const.CONF_DAYS_SINCE_LAST_IRRIGATION: 1}

        coord.store.async_get_config = get_config
        await coord._increment_days_since_irrigation()
        zones = {int(z[const.ZONE_ID]): z for z in await coord.store.async_get_zones()}
        assert zones[0][const.ZONE_DAYS_SINCE_IRRIGATION] == 2
        # A zone with no counter yet starts from the default rather than raising.
        assert zones[1][const.ZONE_DAYS_SINCE_IRRIGATION] == 1
        assert coord.store.config_dict[const.CONF_DAYS_SINCE_LAST_IRRIGATION] == 2

    def test_the_guard_holds_a_zone_that_has_not_waited_long_enough(self):
        coord = _coord()
        assert coord._zone_days_between_blocked({const.ZONE_DAYS_SINCE_IRRIGATION: 1}, 3)
        assert not coord._zone_days_between_blocked(
            {const.ZONE_DAYS_SINCE_IRRIGATION: 3}, 3
        )

    def test_a_zone_with_no_counter_yet_is_never_held(self):
        # Erring towards watering is the safe direction for a guard whose whole
        # failure mode is stranding a dry zone.
        coord = _coord()
        assert not coord._zone_days_between_blocked({}, 3)

    def test_the_setting_reads_zero_when_unreadable(self):
        coord = _coord(config=Mock(spec=[]))
        assert coord._days_between_setting() == 0


class TestRotatingDeadline:
    """A rotation cut by the deadline still has to leave a run-log entry."""

    async def _rotating_coord(self, monkeypatch, clock):
        monkeypatch.setattr(
            "custom_components.smart_irrigation.irrigation.async_dispatcher_send",
            Mock(),
        )

        # The rotation's slot sleeps are mocked out, so no real time passes and
        # the deadline could never bite. Drive a clock the slots advance instead.
        class _Clock:
            @staticmethod
            def utcnow():
                return clock["t"]

            @staticmethod
            def now():
                return clock["t"]

        monkeypatch.setattr(
            "custom_components.smart_irrigation.irrigation.dt_util", _Clock
        )

        coord = _coord([_zone(0, 600, bucket=-5.0, bucket_threshold=-1.0)])
        coord.store.config = Mock(
            zone_sequencing="rotating",
            zone_sequencing_max_consecutive_duration=1,
            zone_sequencing_min_absorption_time=0,
            live_estimate_enabled=False,
        )

        async def _slot(zid, seconds):
            clock["t"] += datetime.timedelta(seconds=seconds)
            return False

        coord._register_active_run = Mock()
        coord._unregister_active_run = Mock()
        coord._run_stopped = Mock(return_value=False)
        coord._run_trigger = Mock(return_value="schedule")
        coord._note_si_valve = Mock()
        coord._confirm_valve_running = AsyncMock(return_value=True)
        coord._sleep_or_stopped = AsyncMock(side_effect=_slot)
        coord._clear_zone_fault = Mock()
        coord._commit_run_progress = AsyncMock()
        coord._timed_volume_l = Mock(return_value=12.0)
        coord._credited_depth_native = Mock(return_value=0.1)
        coord._run_ceiling = Mock(return_value=0.0)
        coord._record_run = AsyncMock()
        coord.hass.services.async_call = AsyncMock()
        return coord

    async def test_a_deadline_cut_rotation_is_still_recorded(self, monkeypatch):
        # The loop records a zone only when it finishes its whole duration or a
        # user stops it. The deadline is a third way out, and its water is
        # credited slot by slot — so without an explicit record the bucket, the
        # usage total and "last irrigation" all move while the run history shows
        # nothing. Caught on a live rotation, not by the suite.
        clock = {"t": datetime.datetime(2026, 8, 6, 12, 0, tzinfo=datetime.timezone.utc)}
        coord = await self._rotating_coord(monkeypatch, clock)
        deadline = clock["t"] + datetime.timedelta(seconds=150)
        await coord._run_rotation([dict(coord.store.get_zone(0))], deadline=deadline)
        assert coord._record_run.await_count == 1
        kwargs = coord._record_run.await_args.kwargs
        assert kwargs["result"] == const.RUN_RESULT_PARTIAL
        assert kwargs["detail"] == const.RUN_DETAIL_DEADLINE
        assert kwargs["volume_l"] > 0
        # 600 s of need, 150 s of window: it watered 150 s and carries the rest.
        assert kwargs["actual_s"] == 150

    async def test_a_zone_that_never_watered_is_not_recorded(self, monkeypatch):
        # Past the deadline before the first slot: nothing was delivered, so
        # there is no partial run to log.
        clock = {"t": datetime.datetime(2026, 8, 6, 12, 0, tzinfo=datetime.timezone.utc)}
        coord = await self._rotating_coord(monkeypatch, clock)
        deadline = clock["t"] - datetime.timedelta(seconds=1)
        await coord._run_rotation([dict(coord.store.get_zone(0))], deadline=deadline)
        coord._record_run.assert_not_awaited()

    async def test_a_rotation_that_finishes_records_completion_only_once(
        self, monkeypatch
    ):
        clock = {"t": datetime.datetime(2026, 8, 6, 12, 0, tzinfo=datetime.timezone.utc)}
        coord = await self._rotating_coord(monkeypatch, clock)
        await coord._run_rotation(
            [dict(coord.store.get_zone(0))],
            deadline=clock["t"] + datetime.timedelta(hours=2),
        )
        assert coord._record_run.await_count == 1
        assert coord._record_run.await_args.kwargs["result"] == const.RUN_RESULT_COMPLETED
