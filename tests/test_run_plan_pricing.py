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
