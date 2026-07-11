"""No-demand run-log transparency (opt-in).

When ``Config.log_no_demand`` is on, a scheduled run that skips a zone/member
purely because it has no water demand records one ``skipped`` / ``no_demand``
run-log entry (deduped per zone per calendar day, suppressed under rain delay).
Coordinators are built with ``__new__`` like the other runner tests.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import attr
import homeassistant.util.dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.store import Config


def test_config_defaults_log_no_demand_off():
    assert const.CONF_DEFAULT_LOG_NO_DEMAND is False
    field = attr.fields_dict(Config)["log_no_demand"]
    assert field.default == const.CONF_DEFAULT_LOG_NO_DEMAND


class _FakeStore:
    def __init__(self, zones=None, config=None):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}
        self.config = config

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(changes)
        return dict(self.zones[int(zone_id)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]


def _cfg(**over):
    base = dict(
        rain_delay_until=None,
        zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        live_estimate_enabled=False,
        log_no_demand=True,
    )
    base.update(over)
    return SimpleNamespace(**base)


def _coord(monkeypatch, zones=None, config=None, units=METRIC_SYSTEM):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = units
    coord.hass = hass
    coord.store = _FakeStore(zones, config or _cfg())
    return coord


def _zone(**over):
    z = {const.ZONE_ID: 1, const.ZONE_RUN_LOG: []}
    z.update(over)
    return z


async def test_helper_records_when_enabled(monkeypatch):
    coord = _coord(monkeypatch, [_zone()])
    await coord._record_no_demand_skips([1])
    log = coord.store.zones[1][const.ZONE_RUN_LOG]
    assert len(log) == 1
    assert log[0]["result"] == const.RUN_RESULT_SKIPPED
    assert log[0]["detail"] == const.SKIP_REASON_NO_DEMAND
    assert log[0]["volume_l"] == 0.0


async def test_helper_noop_when_disabled(monkeypatch):
    coord = _coord(monkeypatch, [_zone()], config=_cfg(log_no_demand=False))
    await coord._record_no_demand_skips([1])
    assert coord.store.zones[1][const.ZONE_RUN_LOG] == []


async def test_helper_suppressed_under_rain_delay(monkeypatch):
    future = (dt_util.now() + dt_util.dt.timedelta(hours=2)).isoformat()
    coord = _coord(monkeypatch, [_zone()], config=_cfg(rain_delay_until=future))
    await coord._record_no_demand_skips([1])
    assert coord.store.zones[1][const.ZONE_RUN_LOG] == []


async def test_helper_dedups_same_day(monkeypatch):
    today_entry = {
        "ts": dt_util.now().isoformat(),
        "result": const.RUN_RESULT_SKIPPED,
        "detail": const.SKIP_REASON_NO_DEMAND,
        "volume_l": 0.0,
    }
    coord = _coord(monkeypatch, [_zone(run_log=[today_entry])])
    await coord._record_no_demand_skips([1])
    assert len(coord.store.zones[1][const.ZONE_RUN_LOG]) == 1  # unchanged
