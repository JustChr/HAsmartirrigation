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


def _linked_zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 0,          # no demand
        const.ZONE_BUCKET: 0.0,
        const.ZONE_BUCKET_THRESHOLD: 0.0,  # 0 < 0 is False -> not due
        const.ZONE_RUN_LOG: [],
    }
    z.update(over)
    return z


async def test_no_demand_zone_logged_via_scheduler(monkeypatch):
    coord = _coord(monkeypatch, [_linked_zone()])
    await coord._irrigate_linked_entities()
    log = coord.store.zones[1][const.ZONE_RUN_LOG]
    assert [e["detail"] for e in log] == [const.SKIP_REASON_NO_DEMAND]


async def test_no_demand_zone_not_logged_when_disabled(monkeypatch):
    coord = _coord(monkeypatch, [_linked_zone()], config=_cfg(log_no_demand=False))
    await coord._irrigate_linked_entities()
    assert coord.store.zones[1][const.ZONE_RUN_LOG] == []


def _member(zid, duration):
    # bucket 0 < threshold 10 so a duration-300 automatic member passes
    # _dist_needs_water's deficit gate (needs demand = True); a duration-0
    # member fails on duration alone (no demand = True).
    return {
        const.ZONE_ID: zid,
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: duration,
        const.ZONE_BUCKET: 0.0,
        const.ZONE_BUCKET_THRESHOLD: 10.0,
        const.ZONE_RUN_LOG: [],
    }


def test_dist_no_demand_members_selects_non_due(monkeypatch):
    coord = _coord(monkeypatch)
    members = [_member(1, 300), _member(2, 0), _member(3, 0)]  # 1 due, 2 & 3 not
    ids = coord._dist_no_demand_members(members, None)
    assert sorted(ids) == [2, 3]


def test_dist_no_demand_members_respects_allow(monkeypatch):
    coord = _coord(monkeypatch)
    members = [_member(1, 300), _member(2, 0), _member(3, 0)]
    ids = coord._dist_no_demand_members(members, {2})
    assert ids == [2]  # 3 is non-due but not in this cycle's target


def test_dist_no_demand_members_excludes_disabled(monkeypatch):
    coord = _coord(monkeypatch)
    disabled = _member(2, 0)
    disabled[const.ZONE_STATE] = const.ZONE_STATE_DISABLED
    members = [_member(1, 0), disabled]  # 1 = no-demand automatic, 2 = disabled
    ids = coord._dist_no_demand_members(members, None)
    assert ids == [1]  # disabled member 2 is not a demand evaluation
