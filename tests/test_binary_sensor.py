"""Tests for the Smart Irrigation binary sensor platform."""

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.binary_sensor import _zone_needs_irrigation


def _zone(**overrides):
    zone = {
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 600,
        const.ZONE_BUCKET: -12.0,
        const.ZONE_BUCKET_THRESHOLD: -10.0,
    }
    zone.update(overrides)
    return zone


def test_zone_needs_irrigation_when_gate_met():
    """Enabled + duration > 0 + bucket below threshold -> needed."""
    assert _zone_needs_irrigation(_zone()) is True


def test_zone_needs_irrigation_respects_disabled():
    assert _zone_needs_irrigation(_zone(state=const.ZONE_STATE_DISABLED)) is False


def test_zone_needs_irrigation_requires_duration():
    assert _zone_needs_irrigation(_zone(duration=0)) is False
    assert _zone_needs_irrigation(_zone(duration=None)) is False


def test_zone_needs_irrigation_requires_deficit_below_threshold():
    # -5 is above the -10 threshold: deficit not deep enough yet
    assert _zone_needs_irrigation(_zone(bucket=-5.0)) is False
    # exactly at the threshold is not "below"
    assert _zone_needs_irrigation(_zone(bucket=-10.0)) is False


def test_zone_needs_irrigation_handles_missing():
    assert _zone_needs_irrigation(None) is False
    assert _zone_needs_irrigation({}) is False
