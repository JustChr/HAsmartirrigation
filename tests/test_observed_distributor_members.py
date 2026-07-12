"""Observed watering Phase 2: crediting distributor member zones on an external
inlet open->close. Backend-only; hosts are built like the other distributor unit
tests (mixin composite + Mock hass/store)."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.distributor import DistributorMixin
from custom_components.smart_irrigation.irrigation import IrrigationRunnerMixin
from custom_components.smart_irrigation.master import MasterMixin
from custom_components.smart_irrigation.skip_conditions import SkipConditionsMixin


class _Host(DistributorMixin, MasterMixin, SkipConditionsMixin, IrrigationRunnerMixin):
    """Minimal host to unit-test the distributor mixin in isolation."""


def _host(observed=True):
    c = _Host()
    c.hass = Mock()
    c.hass.data = {}
    c.store = Mock()
    c.store.async_update_distributor = AsyncMock()
    c.store.config = SimpleNamespace(observed_watering_enabled=observed)
    return c


def test_run_trigger_observed_const():
    assert const.RUN_TRIGGER_OBSERVED == "observed"
