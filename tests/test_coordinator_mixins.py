"""Structural tests for the coordinator decomposition (Phase C).

The God-class extraction moves methods onto mixins the coordinator inherits.
These tests assert each mixin is inherited and its methods are present, so a
method accidentally dropped during a relocation is caught — important for the
irrigation runner (C2), which has no behavioral coverage yet.
"""

from custom_components.smart_irrigation import SmartIrrigationCoordinator
from custom_components.smart_irrigation.calculation import CalculationMixin
from custom_components.smart_irrigation.irrigation import IrrigationRunnerMixin
from custom_components.smart_irrigation.services import ServiceHandlersMixin
from custom_components.smart_irrigation.skip_conditions import SkipConditionsMixin
from custom_components.smart_irrigation.watering_calendar import WateringCalendarMixin


def test_coordinator_is_plain_not_dataupdatecoordinator():
    """C6: the coordinator uses none of DataUpdateCoordinator's API, so it no
    longer inherits it."""
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    assert not issubclass(SmartIrrigationCoordinator, DataUpdateCoordinator)


def test_coordinator_inherits_all_extracted_mixins():
    for mixin in (
        ServiceHandlersMixin,
        WateringCalendarMixin,
        IrrigationRunnerMixin,
        CalculationMixin,
        SkipConditionsMixin,
    ):
        assert issubclass(SmartIrrigationCoordinator, mixin), mixin.__name__


def test_calculation_and_skip_methods_present():
    for name in (
        "merge_weatherdata_and_sensor_values",
        "_aggregate_for_zone",
        "_prune_mapping_buffer",
        "async_calculate_zone",
        "getModuleInstanceByID",
        "calculate_module",
    ):
        assert hasattr(CalculationMixin, name), name
    for name in (
        "_check_skip_conditions",
        "async_evaluate_skip_conditions",
        "_eval_precipitation",
        "_eval_rain_sensor",
        "_reset_days_since_irrigation",
    ):
        assert hasattr(SkipConditionsMixin, name), name


def test_irrigation_runner_methods_present():
    expected = [
        "_irrigate_linked_entities",
        "_read_flow_sample",
        "_run_valve_metered",
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
