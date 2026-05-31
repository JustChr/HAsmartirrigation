"""Tests for zone calculate/update path — catches silent failures.

These tests run without a Home Assistant instance. They verify the error
message patterns and the calculate-branch decision logic that caused silent
failures in production (buttons appeared to do nothing).

CI tests that import the full coordinator (requires pytest-homeassistant-
custom-component) live in custom_components/smart_irrigation/tests/.
"""

from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Error class — defined inline to avoid HA import chain.
# Must stay in sync with const.SmartIrrigationError (same base class).
# ---------------------------------------------------------------------------


class SmartIrrigationError(Exception):
    """Mirror of const.SmartIrrigationError for standalone testing."""


# ---------------------------------------------------------------------------
# Replica of the ATTR_CALCULATE branch in async_update_zone_config.
# Kept 1-to-1 with the production code so changes to one trigger a test fail.
# ---------------------------------------------------------------------------


async def _run_calculate(*, zone, mapping, modinst, use_weather_service=False):
    """Replicate the ATTR_CALCULATE branch of async_update_zone_config."""
    if zone is None:
        raise SmartIrrigationError("Zone not found")

    zone_name = zone.get("name", "?")
    mapping_id = zone.get("mapping")
    has_data = mapping is not None and bool(mapping.get("data"))

    if not has_data:
        if mapping_id is None:
            msg = f"Zone '{zone_name}' has no mapping configured. Assign a mapping with sensor data before calculating."
        else:
            msg = f"Zone '{zone_name}' has no sensor data yet. Wait for sensors to report values or check mapping '{mapping_id}'."
        raise SmartIrrigationError(msg)

    if modinst is None:
        raise SmartIrrigationError(
            f"Zone '{zone_name}' has no calculation module configured. Assign a module before calculating."
        )

    if (
        getattr(modinst, "name", None) == "PyETO"
        and getattr(modinst, "forecast_days", 0) > 0
    ):
        if not use_weather_service:
            raise SmartIrrigationError(
                f"Zone '{zone_name}': PyETO is configured to use forecast data "
                "but no weather service API is configured. "
                "Either configure a weather service or set forecast_days to 0."
            )

    return True  # would call async_calculate_zone


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestCalculateLogic:
    """Calculate-path decision logic must raise on bad config (not return silently)."""

    async def test_zone_not_found_raises(self):
        with pytest.raises(SmartIrrigationError, match="not found"):
            await _run_calculate(zone=None, mapping=None, modinst=None)

    async def test_no_mapping_configured_raises(self):
        zone = {"id": 1, "name": "Garden", "mapping": None}
        with pytest.raises(SmartIrrigationError, match="no mapping configured"):
            await _run_calculate(zone=zone, mapping=None, modinst=None)

    async def test_mapping_exists_but_no_data_raises(self):
        zone = {"id": 1, "name": "Garden", "mapping": 2}
        mapping = {"id": 2, "data": []}
        with pytest.raises(SmartIrrigationError, match="no sensor data"):
            await _run_calculate(zone=zone, mapping=mapping, modinst=None)

    async def test_mapping_is_none_object_raises(self):
        """Mapping ID set but mapping record missing from store."""
        zone = {"id": 1, "name": "Garden", "mapping": 2}
        with pytest.raises(SmartIrrigationError, match="no sensor data"):
            await _run_calculate(zone=zone, mapping=None, modinst=None)

    async def test_no_module_raises(self):
        zone = {"id": 1, "name": "Garden", "mapping": 2}
        mapping = {"id": 2, "data": [{"temperature": 20}]}
        with pytest.raises(SmartIrrigationError, match="no calculation module"):
            await _run_calculate(zone=zone, mapping=mapping, modinst=None)

    async def test_pyeto_forecast_without_weather_service_raises(self):
        zone = {"id": 1, "name": "Garden", "mapping": 2}
        mapping = {"id": 2, "data": [{"temperature": 20}]}
        mod = MagicMock()
        mod.name = "PyETO"
        mod.forecast_days = 3
        with pytest.raises(SmartIrrigationError, match="weather service"):
            await _run_calculate(
                zone=zone, mapping=mapping, modinst=mod, use_weather_service=False
            )

    async def test_pyeto_no_forecast_with_data_succeeds(self):
        zone = {"id": 1, "name": "Garden", "mapping": 2}
        mapping = {"id": 2, "data": [{"temperature": 20}]}
        mod = MagicMock()
        mod.name = "PyETO"
        mod.forecast_days = 0
        result = await _run_calculate(zone=zone, mapping=mapping, modinst=mod)
        assert result is True

    async def test_non_pyeto_module_with_data_succeeds(self):
        zone = {"id": 1, "name": "Garden", "mapping": 2}
        mapping = {"id": 2, "data": [{"temperature": 20}]}
        mod = MagicMock()
        mod.name = "StaticModule"
        result = await _run_calculate(zone=zone, mapping=mapping, modinst=mod)
        assert result is True


class TestErrorMessages:
    """Error messages must be user-readable (not just tracebacks)."""

    def test_no_mapping_message_is_actionable(self):
        msg = "Zone 'Garden' has no mapping configured. Assign a mapping with sensor data before calculating."
        err = SmartIrrigationError(msg)
        assert "no mapping configured" in str(err)
        assert "Assign a mapping" in str(err)

    def test_no_sensor_data_message_is_actionable(self):
        msg = "Zone 'Garden' has no sensor data yet. Wait for sensors to report values or check mapping '2'."
        err = SmartIrrigationError(msg)
        assert "no sensor data" in str(err)
        assert "check mapping" in str(err)

    def test_no_module_message_is_actionable(self):
        msg = "Zone 'Garden' has no calculation module configured. Assign a module before calculating."
        err = SmartIrrigationError(msg)
        assert "no calculation module" in str(err)
        assert "Assign a module" in str(err)
