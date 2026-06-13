"""Tests for the WS-4 freeze guard (``SkipConditionsMixin._eval_freeze``).

The guard skips irrigation when frost is expected, comparing the current
temperature and the coming night's forecast minimum against a threshold. Built
with ``__new__`` so only the attributes ``_eval_freeze`` touches are wired up.
"""

from unittest.mock import Mock

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.skip_conditions import SKIP_FREEZE


def _make_coordinator(current=None, forecast_min=None, has_client=True):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)

    hass = Mock()

    async def run_executor(func, *args):
        return func(*args)

    hass.async_add_executor_job = run_executor
    coord.hass = hass

    if has_client:
        client = Mock()
        client.get_data = Mock(
            return_value=(
                {const.MAPPING_TEMPERATURE: current} if current is not None else {}
            )
        )
        client.get_forecast_data = Mock(
            return_value=(
                [{const.MAPPING_MIN_TEMP: forecast_min}]
                if forecast_min is not None
                else []
            )
        )
        coord._WeatherServiceClient = client
    else:
        coord._WeatherServiceClient = None
    return coord


def _config(enabled=True, threshold=1.0):
    return {
        const.CONF_SKIP_FREEZE_ENABLED: enabled,
        const.CONF_FREEZE_THRESHOLD: threshold,
    }


async def test_disabled_is_a_noop():
    coord = _make_coordinator(current=-5.0)
    result = await coord._eval_freeze(_config(enabled=False))
    assert result["id"] == SKIP_FREEZE
    assert result["enabled"] is False
    assert result["would_skip"] is False
    assert result["available"] is False


async def test_no_weather_client_unavailable():
    coord = _make_coordinator(current=-5.0, has_client=False)
    result = await coord._eval_freeze(_config())
    assert result["enabled"] is True
    assert result["available"] is False
    assert result["would_skip"] is False


async def test_current_below_threshold_skips():
    coord = _make_coordinator(current=-2.0, forecast_min=8.0)
    result = await coord._eval_freeze(_config(threshold=1.0))
    assert result["available"] is True
    # observed is the colder of current (-2) and forecast min (8)
    assert result["observed"] == -2.0
    assert result["would_skip"] is True


async def test_forecast_min_below_threshold_skips_when_currently_mild():
    """A clear sub-freezing night is caught even when it is mild right now."""
    coord = _make_coordinator(current=9.0, forecast_min=-1.0)
    result = await coord._eval_freeze(_config(threshold=1.0))
    assert result["observed"] == -1.0
    assert result["would_skip"] is True


async def test_both_above_threshold_does_not_skip():
    coord = _make_coordinator(current=6.0, forecast_min=3.0)
    result = await coord._eval_freeze(_config(threshold=1.0))
    assert result["observed"] == 3.0
    assert result["would_skip"] is False


async def test_uses_threshold_strictly_below():
    """At exactly the threshold it does not skip (strict <)."""
    coord = _make_coordinator(current=1.0, forecast_min=1.0)
    result = await coord._eval_freeze(_config(threshold=1.0))
    assert result["would_skip"] is False
