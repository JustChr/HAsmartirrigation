"""Shared flow-sensor unit classification (rate vs totalizer) + total→litres."""

from custom_components.smart_irrigation import SmartIrrigationCoordinator as C


def test_rate_units_are_not_totalizer():
    assert C._flow_is_totalizer("l/min", None) is False
    assert C._flow_is_totalizer("m³/h", "measurement") is False


def test_totalizer_by_unit_without_slash():
    assert C._flow_is_totalizer("m³", None) is True
    assert C._flow_is_totalizer("L", "measurement") is True


def test_totalizer_by_state_class_overrides():
    # a total_increasing counter is a totalizer even with an odd/empty unit
    assert C._flow_is_totalizer("", "total_increasing") is True
    assert C._flow_is_totalizer("l/min", "total_increasing") is True


def test_no_unit_no_total_class_is_rate_fallback():
    assert C._flow_is_totalizer("", None) is False
    assert C._flow_is_totalizer(None, None) is False


def test_abbreviated_rate_units_are_not_totalizer():
    assert C._flow_is_totalizer("gpm", None) is False
    assert C._flow_is_totalizer("lpm", None) is False
    assert C._flow_is_totalizer("gph", None) is False


def test_litres_from_total_conversions():
    assert C._flow_litres_from_total(2.0, "m³") == 2000.0
    assert round(C._flow_litres_from_total(1.0, "gal"), 6) == 3.785412
    assert C._flow_litres_from_total(5.0, "L") == 5.0
