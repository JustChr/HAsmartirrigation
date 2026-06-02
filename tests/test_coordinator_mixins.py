"""Structural tests for the coordinator decomposition (Phase C).

The God-class extraction moves methods onto mixins the coordinator inherits.
These tests assert each mixin is inherited and its methods are present, so a
method accidentally dropped during a relocation is caught — important for the
irrigation runner (C2), which has no behavioral coverage yet.
"""

from custom_components.smart_irrigation import SmartIrrigationCoordinator
from custom_components.smart_irrigation.irrigation import IrrigationRunnerMixin
from custom_components.smart_irrigation.services import ServiceHandlersMixin
from custom_components.smart_irrigation.watering_calendar import WateringCalendarMixin


def test_coordinator_inherits_all_extracted_mixins():
    for mixin in (
        ServiceHandlersMixin,
        WateringCalendarMixin,
        IrrigationRunnerMixin,
    ):
        assert issubclass(SmartIrrigationCoordinator, mixin), mixin.__name__


def test_irrigation_runner_methods_present():
    expected = [
        "_irrigate_linked_entities",
        "_flow_rate_to_l_per_min",
        "_irrigate_zone_with_flow_meter",
        "_irrigate_zone_flow_slot",
        "_irrigate_zones_rotating",
        "_irrigate_zones_sequential",
        "_irrigate_zones_parallel",
        "async_irrigate_now",
    ]
    for name in expected:
        assert callable(getattr(IrrigationRunnerMixin, name)), name
        # and reachable through the coordinator (mixin actually inherited)
        assert hasattr(SmartIrrigationCoordinator, name), name


def test_reset_event_fired_today_stays_on_coordinator():
    """The midnight callback is not irrigation; it must NOT move to the mixin."""
    assert not hasattr(IrrigationRunnerMixin, "_reset_event_fired_today")
    assert hasattr(SmartIrrigationCoordinator, "_reset_event_fired_today")
