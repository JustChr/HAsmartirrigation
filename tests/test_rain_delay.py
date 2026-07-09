"""Tests for WS-5: rain delay / vacation hold.

A user-set, time-boxed pause of all AUTOMATIC/scheduled irrigation. The hold is
stored as an ISO datetime on the config; ``_irrigate_linked_entities`` (the
scheduled path) short-circuits while it is active and records a ``paused`` skip,
while explicit manual runs (``async_irrigate_now`` / ``async_run_zone``) bypass
it. Coordinators are built with ``__new__`` so only the touched attributes are
wired up.
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


class _FakeStore:
    """Minimal in-memory store exposing what the runner + hold helpers call."""

    def __init__(self, zones=None, config=None):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in (zones or [])}
        self.config = config or SimpleNamespace(
            rain_delay_until=None,
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        )
        self.updated_config = []

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_update_zone(self, zone_id, changes):
        self.zones.setdefault(int(zone_id), {const.ZONE_ID: int(zone_id)}).update(
            changes
        )
        return dict(self.zones[int(zone_id)])

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]

    async def async_get_distributors(self):
        # H3: async_irrigate_now now also dispatches distributor cycles, which
        # reads this collection. No distributors in the rain-delay fixtures.
        return []

    async def async_update_config(self, changes):
        self.updated_config.append(changes)
        for k, v in changes.items():
            setattr(self.config, k, v)
        return changes


def _coord(monkeypatch, zones=None, config=None, units=METRIC_SYSTEM):
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = units
    coord.hass = hass
    coord.store = _FakeStore(zones, config)
    return coord


def _eligible_zone():
    """A zone the scheduled runner would water (deficit below threshold)."""
    return {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Lawn",
        const.ZONE_LINKED_ENTITY: "switch.valve",
        const.ZONE_DURATION: 300,
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_BUCKET: -5.0,
        const.ZONE_BUCKET_THRESHOLD: 0.0,
        const.ZONE_RUN_LOG: [],
    }


# --------------------------------------------------------------------------- #
# _rain_delay_active / parsing
# --------------------------------------------------------------------------- #
def test_rain_delay_inactive_when_unset(monkeypatch):
    coord = _coord(monkeypatch)
    assert coord._rain_delay_active() is False
    assert coord._rain_delay_until_dt() is None


def test_rain_delay_active_when_future(monkeypatch):
    future = (dt_util.now() + timedelta(hours=12)).isoformat()
    coord = _coord(
        monkeypatch,
        config=SimpleNamespace(
            rain_delay_until=future,
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        ),
    )
    assert coord._rain_delay_active() is True
    assert coord._rain_delay_until_dt() is not None


def test_rain_delay_inactive_when_past(monkeypatch):
    past = (dt_util.now() - timedelta(hours=1)).isoformat()
    coord = _coord(
        monkeypatch,
        config=SimpleNamespace(
            rain_delay_until=past,
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        ),
    )
    assert coord._rain_delay_active() is False


def test_rain_delay_inactive_on_garbage(monkeypatch):
    coord = _coord(
        monkeypatch,
        config=SimpleNamespace(
            rain_delay_until="not-a-datetime",
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        ),
    )
    assert coord._rain_delay_active() is False


# --------------------------------------------------------------------------- #
# set / clear / delay-hours
# --------------------------------------------------------------------------- #
async def test_set_and_clear_rain_delay_roundtrip(monkeypatch):
    coord = _coord(monkeypatch)
    iso = (dt_util.now() + timedelta(days=2)).isoformat()
    await coord.async_set_rain_delay(iso)
    assert coord.store.config.rain_delay_until == iso
    assert coord._rain_delay_active() is True

    await coord.async_clear_rain_delay()
    assert coord.store.config.rain_delay_until is None
    assert coord._rain_delay_active() is False


async def test_delay_hours_sets_future_hold(monkeypatch):
    coord = _coord(monkeypatch)
    before = dt_util.now() + timedelta(hours=24)
    await coord.async_delay_hours(24)
    until = coord._rain_delay_until_dt()
    assert until is not None
    # within a minute of now+24h
    assert abs((until - before).total_seconds()) < 60


# --------------------------------------------------------------------------- #
# gate: scheduled path is held, records a "paused" skip
# --------------------------------------------------------------------------- #
async def test_irrigate_linked_entities_held_records_paused(monkeypatch):
    future = (dt_util.now() + timedelta(hours=6)).isoformat()
    coord = _coord(
        monkeypatch,
        zones=[_eligible_zone()],
        config=SimpleNamespace(
            rain_delay_until=future,
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        ),
    )
    # Must not reach the live-duration step or start any run while held.
    coord._apply_live_durations = AsyncMock(
        side_effect=AssertionError("should not run while held")
    )
    coord._irrigate_zones_parallel = AsyncMock(
        side_effect=AssertionError("should not run while held")
    )

    await coord._irrigate_linked_entities()

    log = coord.store.zones[1][const.ZONE_RUN_LOG]
    assert log and log[0]["result"] == const.RUN_RESULT_SKIPPED
    assert log[0]["detail"] == const.SKIP_REASON_PAUSED


async def test_irrigate_linked_entities_runs_when_not_held(monkeypatch):
    coord = _coord(monkeypatch, zones=[_eligible_zone()])
    coord._apply_live_durations = AsyncMock(side_effect=lambda zs: zs)
    coord._irrigate_zones_parallel = AsyncMock()

    await coord._irrigate_linked_entities()

    coord._irrigate_zones_parallel.assert_awaited_once()


# --------------------------------------------------------------------------- #
# manual bypass: async_irrigate_now ignores the hold
# --------------------------------------------------------------------------- #
async def test_irrigate_now_bypasses_hold(monkeypatch):
    future = (dt_util.now() + timedelta(hours=6)).isoformat()
    coord = _coord(
        monkeypatch,
        zones=[_eligible_zone()],
        config=SimpleNamespace(
            rain_delay_until=future,
            zone_sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL,
        ),
    )
    coord._irrigate_zones_parallel = AsyncMock()

    await coord.async_irrigate_now("1")

    coord._irrigate_zones_parallel.assert_awaited_once()
