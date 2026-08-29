"""What the run plan hands the wall-clock model, and how a zone is priced.

``bound_wall_clock`` promises the longest wall clock a set of zones could
occupy, and a two-stage arm stands on that promise. It can only keep it if the
plan supplies what the promise needs: the lead time the duration math adds
after its clamp, and a ceiling for a zone the runner never caps at all.
"""

from types import SimpleNamespace
from unittest.mock import Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.duration_math import (
    duration_from_deficit,
    zone_run_duration,
)


class _FakeStore:
    def __init__(self, zones, config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.config = config

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_get_distributors(self):
        return []


def _cfg(**over):
    base = dict(
        zone_sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
        zone_sequencing_max_consecutive_duration=5,
        zone_sequencing_min_absorption_time=0,
        live_estimate_enabled=False,
    )
    base.update(over)
    return SimpleNamespace(**base)


def _zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 600,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_BUCKET_THRESHOLD: -1.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_SIZE: 10.0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_LEAD_TIME: 120,
        const.ZONE_MAXIMUM_DURATION: 600,
        const.ZONE_MAXIMUM_BUCKET: 24,
    }
    z.update(over)
    return z


def _coord(monkeypatch, zones, config=None):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    coord.hass = hass
    coord.store = _FakeStore(zones, config or _cfg())
    return coord


class TestThePlanCarriesWhatTheBoundNeeds:
    async def test_lead_time_reaches_the_run(self, monkeypatch):
        coord = _coord(monkeypatch, [_zone()])
        (plan,) = await coord.async_plan_zone_runs()
        assert plan.lead_time == 120

    async def test_the_plan_supplies_no_ceiling_of_its_own(self, monkeypatch):
        # Nothing here can derive one. maximum_bucket clamps the bucket's
        # surplus side, not the deficit that sizes a run, so a zone with no
        # maximum_duration is reported unbounded rather than given a number.
        coord = _coord(monkeypatch, [_zone(**{const.ZONE_MAXIMUM_DURATION: None})])
        (plan,) = await coord.async_plan_zone_runs()
        assert plan.ceiling is None

    async def test_a_flow_zone_is_marked_as_one(self, monkeypatch):
        coord = _coord(monkeypatch, [_zone(**{const.ZONE_FLOW_SENSOR: "sensor.flow"})])
        (plan,) = await coord.async_plan_zone_runs()
        assert plan.flow is True

    async def test_a_classic_zone_carries_its_confirm_cost(self, monkeypatch):
        coord = _coord(monkeypatch, [_zone(**{const.ZONE_LINKED_ENTITY: "switch.z"})])
        (plan,) = await coord.async_plan_zone_runs()
        assert plan.confirm_seconds == const.VALVE_CONFIRM_TIMEOUT

    async def test_a_flow_zone_is_priced_at_the_rate_its_runs_measured(
        self, monkeypatch
    ):
        """Nothing in the planner knows a zone is flow-metered, so its duration
        is derived from the CONFIGURED throughput while the run delivers at the
        rate the plumbing has. A zone plumbed at half its setting overruns that
        estimate on every single run."""
        coord = _coord(
            monkeypatch,
            [
                _zone(
                    **{
                        const.ZONE_FLOW_SENSOR: "sensor.flow",
                        const.ZONE_LEAD_TIME: 0,
                        const.ZONE_MAXIMUM_DURATION: 0,
                        const.ZONE_THROUGHPUT: 10.0,
                        const.ZONE_FLOW_CAL_SAMPLES: [5.0, 5.0, 5.0],
                    }
                )
            ],
        )
        (plan,) = await coord.async_plan_zone_runs()
        assert plan.duration == 1200  # the stored 600 s at half the rate

    async def test_a_timed_zone_is_never_re_priced(self, monkeypatch):
        """It delivers to a duration, so the configured throughput is not an
        assumption about it -- it is the thing the run obeys."""
        coord = _coord(
            monkeypatch,
            [_zone(**{const.ZONE_FLOW_CAL_SAMPLES: [5.0, 5.0, 5.0]})],
        )
        (plan,) = await coord.async_plan_zone_runs()
        assert plan.duration == 600


class TestDurationForDeficitGoesThroughTheSharedHelper:
    """``zone_run_duration`` exists to be the one place a zone dict is unpacked
    into the duration math. The runner's sizing has to actually use it, or the
    duplication it was written to prevent is sitting next to it."""

    def _coord(self, monkeypatch):
        c = _coord(monkeypatch, [])
        c._duration_clamp_warned = set()
        return c

    def test_matches_the_shared_helper_capped(self, monkeypatch):
        coord = self._coord(monkeypatch)
        zone = _zone()
        assert coord._duration_for_deficit(zone, -100.0, True) == zone_run_duration(
            zone, -100.0, True
        )

    def test_still_warns_once_when_the_cap_bites(self, monkeypatch):
        coord = self._coord(monkeypatch)
        zone = _zone(**{const.ZONE_MAXIMUM_DURATION: 60})
        warned = []
        monkeypatch.setattr(
            coord, "_warn_duration_clamped", lambda *a: warned.append(a)
        )
        capped = coord._duration_for_deficit(zone, -100.0, True)
        assert capped == zone_run_duration(zone, -100.0, True)
        assert len(warned) == 1
        # The warning reports the uncapped length, which is what the zone
        # actually needs and never receives.
        assert warned[0][2] == zone_run_duration(zone, -100.0, True, capped=False)

    def test_does_not_warn_when_the_cap_does_not_bite(self, monkeypatch):
        coord = self._coord(monkeypatch)
        zone = _zone(**{const.ZONE_MAXIMUM_DURATION: 36000})
        warned = []
        monkeypatch.setattr(
            coord, "_warn_duration_clamped", lambda *a: warned.append(a)
        )
        coord._duration_for_deficit(zone, -10.0, True)
        assert warned == []


class TestSequencingTimingFallsBackTheSafeWay:
    def test_an_unreadable_sequencing_falls_back_to_sequential(self, monkeypatch):
        # Only reachable with a corrupted stored value, but it is the one
        # branch that could contradict the module's own rule that an
        # under-estimate finishes the irrigation after the requested time.
        # Parallel is max(), the shortest reduction; sequential is the sum.
        coord = _coord(monkeypatch, [], config=_cfg(zone_sequencing="nonsense"))
        sequencing, _slot, _absorb = coord.sequencing_timing()
        assert sequencing == const.CONF_ZONE_SEQUENCING_SEQUENTIAL

    def test_a_valid_sequencing_is_left_alone(self, monkeypatch):
        for value in (
            const.CONF_ZONE_SEQUENCING_PARALLEL,
            const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
            const.CONF_ZONE_SEQUENCING_ROTATING,
        ):
            coord = _coord(monkeypatch, [], config=_cfg(zone_sequencing=value))
            assert coord.sequencing_timing()[0] == value


def test_the_duration_math_still_clamps_before_adding_lead_time():
    # The property the bound has to compensate for, pinned here so a change to
    # the ordering shows up as a failure in both places at once.
    assert duration_from_deficit(-100.0, 10, 10, 1, 600, 120, True) == 720
