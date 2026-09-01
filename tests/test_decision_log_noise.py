"""One log line per decision, not one per recomputation.

A finish-anchored run's decision is recomputed constantly: the outlook prices
every zone on every estimate refresh, and every ``_config_updated`` re-arms the
schedule from scratch. All of it used to log at the same level, and with the
same wording, as the single real decision — which reads as the schedule arming
over and over when only one dispatch ever fires.

The messages themselves are unchanged (they are what a log reader greps for);
what changes is that a repeat of a decision already logged goes to DEBUG, and
that a read-only projection does not narrate a run it is not making.
"""

import datetime
import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest
from freezegun import freeze_time
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import (
    SmartIrrigationCoordinator,
    const,
    opensprinkler,
)
from custom_components.smart_irrigation.run_window import ZoneRun
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager

UTC = datetime.timezone.utc

NOT_WATERING = "hasn't crossed the threshold"


class _FakeStore:
    def __init__(self, zones, config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.config = config

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]


def _zone(zid=0):
    return {
        const.ZONE_ID: zid,
        const.ZONE_NAME: f"Z{zid}",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_LINKED_ENTITY: f"switch.z{zid}",
        const.ZONE_DURATION: 600,
        const.ZONE_SIZE: 100.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_LEAD_TIME: 0,
        const.ZONE_BUCKET: -1.0,
        const.ZONE_BUCKET_THRESHOLD: -0.9,
        const.ZONE_DISTRIBUTOR_ID: None,
    }


def _coord():
    """A coordinator whose one zone is NOT due on the live estimate."""
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    coord.hass = hass
    coord.store = _FakeStore([_zone()], Mock(live_estimate_enabled=True))
    # Above the -0.9 threshold: the zone does not water.
    estimates = {"0": {"live_deficit": -0.1}}
    coord.async_get_cached_zone_estimates = AsyncMock(return_value=estimates)
    coord.async_refresh_zone_estimates = AsyncMock(return_value=estimates)
    return coord


class _FakeState:
    def __init__(self, attributes, entity_id="switch.os"):
        self.state = "on"
        self.attributes = attributes
        self.entity_id = entity_id


def _station_coord(*, group=0, delay=5):
    """A coordinator whose two zones are OpenSprinkler stations that ARE due.

    ``group=None`` publishes a station carrying no group, which is what an
    unavailable controller and a firmware below v2.2.0(1) both look like.
    """
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM

    station = {
        const.OPENSPRINKLER_ATTR_TYPE: const.OPENSPRINKLER_TYPE_STATION,
        const.OPENSPRINKLER_ATTR_INDEX: 0,
    }
    if group is not None:
        station[const.OPENSPRINKLER_ATTR_GROUP] = group
    controller = {
        const.OPENSPRINKLER_ATTR_TYPE: const.OPENSPRINKLER_TYPE_CONTROLLER,
        const.OPENSPRINKLER_ATTR_STATION_DELAY: delay,
    }
    hass.states.get = lambda entity_id: _FakeState(station)
    hass.states.async_all = lambda domain: [_FakeState(controller)]
    coord.hass = hass

    zones = []
    for zid in (0, 1):
        zone = _zone(zid)
        zone[const.ZONE_WATERING_MODE] = const.WATERING_MODE_OPENSPRINKLER
        zone[const.ZONE_BUCKET] = -5.0
        zones.append(zone)
    coord.store = _FakeStore(zones, Mock(live_estimate_enabled=False))
    return coord


class TestStationGroupingIsSaidOnce:
    """Which of the two pricings the run got, without attaching a debugger."""

    @pytest.fixture(autouse=True)
    def _no_entity_registry(self, monkeypatch):
        """This harness has no registry, so every entity reads as unregistered.

        That is the single-controller path: with nothing to attribute the
        station to, every controller entity is a candidate for its delay.
        """
        monkeypatch.setattr(
            opensprinkler.er,
            "async_get",
            lambda hass: Mock(async_get=lambda entity_id: None),
        )

    async def test_grouping_applied_is_announced(self, caplog):
        caplog.set_level(logging.INFO)
        await _station_coord().async_plan_zone_runs()
        assert "from the controller's own station groups" in caplog.text

    async def test_grouping_unavailable_is_announced(self, caplog):
        caplog.set_level(logging.INFO)
        await _station_coord(group=None).async_plan_zone_runs()
        assert "station grouping is unavailable for 2 of 2" in caplog.text

    async def test_the_same_answer_twice_is_not_two_lines(self, caplog):
        # The plan is rebuilt on every estimate refresh and every re-arm; the
        # grouping is a property of the controller, so it says the same thing
        # every time and would otherwise be the loudest line in the log.
        coord = _station_coord()
        await coord.async_plan_zone_runs()
        caplog.clear()
        caplog.set_level(logging.DEBUG)
        await coord.async_plan_zone_runs()
        levels = [
            r.levelno for r in caplog.records if "station groups" in r.getMessage()
        ]
        assert levels == [logging.DEBUG]

    async def test_losing_the_controller_is_a_new_decision(self, caplog):
        # The transition is exactly what the INFO line exists for: the run
        # length changes underneath the user when the grouping goes away.
        coord = _station_coord()
        await coord.async_plan_zone_runs()
        coord.hass.states.get = lambda entity_id: _FakeState(
            {
                const.OPENSPRINKLER_ATTR_TYPE: const.OPENSPRINKLER_TYPE_STATION,
                const.OPENSPRINKLER_ATTR_INDEX: 0,
            }
        )
        caplog.clear()
        caplog.set_level(logging.INFO)
        await coord.async_plan_zone_runs()
        assert "station grouping is unavailable" in caplog.text

    async def test_a_run_with_no_stations_says_nothing(self, caplog):
        caplog.set_level(logging.DEBUG)
        await _coord().async_plan_zone_runs()
        assert "station" not in caplog.text.lower()


class TestProjectionIsQuiet:
    """The shared projection prices zones; it does not narrate a run."""

    async def test_planning_does_not_log_per_zone_demand(self, caplog):
        # async_plan_zone_runs feeds the outlook and the duration bound, both of
        # which recompute per zone on every estimate refresh. Narrating "not
        # watering this run" from there produced bursts of identical lines about
        # a run that was not happening.
        caplog.set_level(logging.DEBUG)
        assert await _coord().async_plan_zone_runs() == []
        assert NOT_WATERING not in caplog.text

    async def test_the_run_itself_still_logs_the_zone_it_drops(self, caplog):
        # The same line on the real path is the record of why a zone the
        # scheduler dispatched did not water. It stays.
        caplog.set_level(logging.DEBUG)
        coord = _coord()
        coord._live_run_zones = set()
        assert await coord._apply_live_durations([_zone()]) == []
        assert NOT_WATERING in caplog.text


def _schedule(**kw):
    base = {
        const.SCHEDULE_CONF_ID: "s1",
        const.SCHEDULE_CONF_NAME: "overnight",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_SUNRISE,
        const.SCHEDULE_CONF_ACTION: "irrigate",
        const.SCHEDULE_CONF_ZONES: "all",
    }
    base.update(kw)
    return base


def _manager(plan):
    mgr = RecurringScheduleManager(Mock(), Mock())
    mgr.coordinator.async_plan_zone_runs = AsyncMock(return_value=list(plan))
    mgr.coordinator.sequencing_timing = Mock(
        return_value=(const.CONF_ZONE_SEQUENCING_SEQUENTIAL, 300.0, 0.0)
    )
    mgr.coordinator.async_commit_pre_run_calculation = AsyncMock()
    return mgr


def _run(zone_id, duration, ratio=2.0):
    return ZoneRun(zone_id=zone_id, duration=duration, depletion_ratio=ratio)


async def _arm(mgr, target, floor=None):
    with patch(
        "custom_components.smart_irrigation.scheduler.async_track_point_in_utc_time"
    ):
        await mgr._decide_and_arm(_schedule(), target, floor, commit=False)


class TestArmLogsOncePerDecision:
    """A re-arm that decides the same thing is not a second decision."""

    @freeze_time("2026-06-20 22:00:00")
    async def test_an_unchanged_rearm_drops_to_debug(self, caplog):
        # Every config write re-arms the schedule, and past the decision point
        # that re-runs the whole selection. At ~8 of those a second while
        # estimates refresh, an INFO each made the log read as many arms when
        # only one dispatch fires.
        mgr = _manager([_run(0, 1800)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        caplog.set_level(logging.DEBUG)

        await _arm(mgr, target)
        await _arm(mgr, target)
        await _arm(mgr, target)

        armed = [r for r in caplog.records if "demand" in r.message]
        assert [r.levelno for r in armed] == [
            logging.INFO,
            logging.DEBUG,
            logging.DEBUG,
        ]

    @freeze_time("2026-06-20 22:00:00")
    async def test_a_changed_selection_is_a_new_decision(self, caplog):
        # Rain dropping a zone between re-arms is exactly what the INFO line is
        # for, so a decision that differs is logged as one.
        mgr = _manager([_run(0, 1800), _run(1, 1800)])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        caplog.set_level(logging.DEBUG)

        await _arm(mgr, target)
        mgr.coordinator.async_plan_zone_runs = AsyncMock(return_value=[_run(0, 1800)])
        await _arm(mgr, target)

        armed = [r for r in caplog.records if "demand" in r.message]
        assert [r.levelno for r in armed] == [logging.INFO, logging.INFO]

    @freeze_time("2026-06-20 22:00:00")
    async def test_the_does_not_fit_warning_follows_the_same_rule(self, caplog):
        # 2 h of window against 3 h of demand: zone 1 is dropped. The warning
        # matters once; repeated verbatim it is noise.
        mgr = _manager([_run(0, 7200, ratio=3.0), _run(1, 3600, ratio=1.1)])
        target = datetime.datetime(2026, 6, 21, 0, 0, tzinfo=UTC)
        floor = datetime.datetime(2026, 6, 20, 22, 0, tzinfo=UTC)
        caplog.set_level(logging.DEBUG)

        await _arm(mgr, target, floor)
        await _arm(mgr, target, floor)

        dropped = [r for r in caplog.records if "do not fit" in r.message]
        assert [r.levelno for r in dropped] == [logging.WARNING, logging.DEBUG]

    @freeze_time("2026-06-20 22:00:00")
    async def test_nothing_due_is_also_logged_once(self, caplog):
        mgr = _manager([])
        target = datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC)
        caplog.set_level(logging.DEBUG)

        await _arm(mgr, target)
        await _arm(mgr, target)

        idle = [r for r in caplog.records if "no zone is due" in r.message]
        assert [r.levelno for r in idle] == [logging.INFO, logging.DEBUG]

    @freeze_time("2026-06-20 22:00:00")
    async def test_the_next_occurrence_starts_fresh(self, caplog):
        # The memory is per occurrence: tomorrow's identical decision is still a
        # decision, and must not be swallowed by today's.
        mgr = _manager([_run(0, 1800)])
        caplog.set_level(logging.DEBUG)

        await _arm(mgr, datetime.datetime(2026, 6, 21, 6, 0, tzinfo=UTC))
        await _arm(mgr, datetime.datetime(2026, 6, 22, 6, 0, tzinfo=UTC))

        armed = [r for r in caplog.records if "demand" in r.message]
        assert [r.levelno for r in armed] == [logging.INFO, logging.INFO]
