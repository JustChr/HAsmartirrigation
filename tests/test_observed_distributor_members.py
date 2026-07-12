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


def _credit_host():
    c = _host()
    c.store.async_update_zone = AsyncMock()
    c._record_run = AsyncMock()
    c._timed_volume_l = Mock(return_value=12.0)
    c._credited_depth_native = Mock(return_value=3.0)
    return c


async def test_credit_zone_defaults_completed_distributor():
    c = _credit_host()
    zone = {const.ZONE_ID: 5, const.ZONE_BUCKET: 0.0}
    await c._dist_credit_zone(zone, 300)
    kwargs = c._record_run.await_args.kwargs
    assert kwargs["result"] == const.RUN_RESULT_COMPLETED
    assert kwargs["trigger"] == const.RUN_TRIGGER_DISTRIBUTOR


async def test_credit_zone_observed_result_trigger():
    c = _credit_host()
    zone = {const.ZONE_ID: 5, const.ZONE_BUCKET: 0.0}
    await c._dist_credit_zone(
        zone, 300, result=const.RUN_RESULT_OBSERVED, trigger=const.RUN_TRIGGER_OBSERVED
    )
    kwargs = c._record_run.await_args.kwargs
    assert kwargs["result"] == const.RUN_RESULT_OBSERVED
    assert kwargs["trigger"] == const.RUN_TRIGGER_OBSERVED
    assert kwargs["add_to_total"] is True
