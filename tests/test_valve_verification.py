"""Tests for WS-1: valve-run verification + per-zone fault state.

The runner confirms a freshly-opened linked entity actually reports an on-state.
A valve that does not confirm is NOT aborted any more (it may be open but slow to
report, as sleepy Zigbee/Tuya timers are): the run proceeds and the unconfirmed
state is only logged. The open is also re-sent once partway through the window to
recover a dropped command. Flow zones that never register any flow still fault
(no water actually moved).

Coordinators are built with ``__new__`` (like test_experimental_features) so only
the attributes each method touches are wired up.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


def _runner(monkeypatch, states, *, confirm_timeout=0):
    """Runner coordinator with a fake hass whose state machine is ``states``.

    ``confirm_timeout=0`` makes ``_confirm_valve_running`` decide on the first
    check (no real sleeping) — the valve is judged purely on its current state.
    """
    monkeypatch.setattr(const, "VALVE_CONFIRM_TIMEOUT", confirm_timeout)
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.async_dispatcher_send", Mock()
    )

    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.services.async_call = AsyncMock()
    hass.states.get = lambda eid: states.get(eid)
    coord.hass = hass
    coord.store = Mock()
    coord.store.async_update_zone = AsyncMock()
    coord.store.get_zone = Mock(return_value={})
    return coord


def _st(state):
    return SimpleNamespace(state=state, attributes={})


def _bucket_change(mock):
    """Return the changes dict of the *final* async_update_zone call that set the
    bucket.

    Since WS-2 the runner also writes a run-log entry via async_update_zone, and
    metered runs now commit the bucket several times as the water accrues, so a
    completed run touches the store more than once; the post-run bucket level is
    the *last* call carrying ZONE_BUCKET.
    """
    for call in reversed(mock.await_args_list):
        _, changes = call.args
        if const.ZONE_BUCKET in changes:
            return changes
    return None


def _no_bucket_replenished(mock):
    """True when no async_update_zone call replenished the bucket."""
    return _bucket_change(mock) is None


# --------------------------------------------------------------------------- #
# _confirm_valve_running
# --------------------------------------------------------------------------- #
async def test_confirm_returns_true_when_on(monkeypatch):
    coord = _runner(monkeypatch, {"switch.v": _st("on")})
    assert await coord._confirm_valve_running(1, "switch.v") is True


async def test_confirm_returns_false_when_stays_off(monkeypatch):
    coord = _runner(monkeypatch, {"switch.v": _st("off")})
    assert await coord._confirm_valve_running(1, "switch.v") is False


async def test_confirm_returns_none_when_unverifiable(monkeypatch):
    # Missing entity and unavailable both mean "can't verify" -> None (not a fault).
    coord = _runner(monkeypatch, {})
    assert await coord._confirm_valve_running(1, "switch.v") is None
    coord = _runner(monkeypatch, {"switch.v": _st("unavailable")})
    assert await coord._confirm_valve_running(1, "switch.v") is None


async def test_confirm_retries_open_then_confirms(monkeypatch):
    """A valve still off at the retry mark gets the open re-sent once; if it then
    reports on it is confirmed True."""
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    monkeypatch.setattr(const, "VALVE_CONFIRM_RETRY_AT", 2)
    state = _st("off")
    coord = _runner(monkeypatch, {"switch.v": state}, confirm_timeout=4)

    async def _flip_on(domain, service, data):
        if service == "turn_on":
            state.state = "on"  # the re-sent open finally takes effect

    coord.hass.services.async_call = AsyncMock(side_effect=_flip_on)

    assert await coord._confirm_valve_running(1, "switch.v") is True
    # The open was re-sent exactly once (the retry).
    assert coord.hass.services.async_call.await_count == 1


# --------------------------------------------------------------------------- #
# Fault state accessors
# --------------------------------------------------------------------------- #
def test_fault_set_get_clear(monkeypatch):
    coord = _runner(monkeypatch, {})
    assert coord.get_zone_fault(1) is None
    coord._set_zone_fault(1, const.FAULT_VALVE_NO_RESPONSE)
    fault = coord.get_zone_fault(1)
    assert fault["reason"] == const.FAULT_VALVE_NO_RESPONSE
    assert "timestamp" in fault
    assert coord.get_zone_faults() == {1: fault}
    coord._clear_zone_fault(1)
    assert coord.get_zone_fault(1) is None
    assert coord.get_zone_faults() == {}


# --------------------------------------------------------------------------- #
# Sequential timed path gating
# --------------------------------------------------------------------------- #
def _timed_zone(**overrides):
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_NAME: "Garden",
        const.ZONE_LINKED_ENTITY: "switch.v",
        const.ZONE_FLOW_SENSOR: None,
        const.ZONE_DURATION: 0,  # sleep(0) -> instant
        const.ZONE_IRRIGATION_TARGET_BUCKET: 0.0,
    }
    zone.update(overrides)
    return zone


async def test_sequential_unconfirmed_valve_still_waters(monkeypatch):
    """Valve never reports on -> the run is NOT aborted: it proceeds, credits the
    bucket and raises no fault (the valve may be open but slow to report)."""
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord = _runner(monkeypatch, {"switch.v": _st("off")})

    # 30 s @ 20 L/min over 10 m² = 1 mm -> bucket -1 climbs to its 0.0 target.
    zone = _timed_zone(
        **{
            const.ZONE_DURATION: 30,
            const.ZONE_BUCKET: -1.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 20.0,
        }
    )
    await coord._irrigate_zones_sequential([zone])

    changes = _bucket_change(coord.store.async_update_zone)
    assert changes is not None
    assert changes[const.ZONE_BUCKET] == pytest.approx(0.0)  # it watered
    assert coord.get_zone_fault(1) is None  # no fault raised


async def test_sequential_success_resets_bucket_and_clears_fault(monkeypatch):
    """Valve confirms on -> bucket replenished, fault cleared."""
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord = _runner(monkeypatch, {"switch.v": _st("on")})
    coord._set_zone_fault(1, const.FAULT_VALVE_NO_RESPONSE)  # pre-existing fault

    # A real run shorter than the commit interval (one commit at turn-off):
    # 30 s @ 20 L/min over 10 m² = 1 mm -> bucket -1 climbs to 0.
    zone = _timed_zone(
        **{
            const.ZONE_DURATION: 30,
            const.ZONE_BUCKET: -1.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_THROUGHPUT: 20.0,
        }
    )
    await coord._irrigate_zones_sequential([zone])

    changes = _bucket_change(coord.store.async_update_zone)
    assert changes is not None
    assert changes[const.ZONE_BUCKET] == pytest.approx(0.0)
    assert const.ZONE_LAST_IRRIGATION in changes
    assert coord.get_zone_fault(1) is None


async def test_sequential_unverifiable_valve_still_runs(monkeypatch):
    """Write-only valve (no readable state) is never penalised — runs normally."""
    coord = _runner(monkeypatch, {})  # entity not in the state machine

    await coord._irrigate_zones_sequential([_timed_zone()])

    coord.store.async_update_zone.assert_awaited()
    assert coord.get_zone_fault(1) is None


# --------------------------------------------------------------------------- #
# Flow-meter path gating
# --------------------------------------------------------------------------- #
def _flow_zone(**overrides):
    zone = {
        const.ZONE_ID: 2,
        const.ZONE_NAME: "Beds",
        const.ZONE_LINKED_ENTITY: "switch.f",
        const.ZONE_FLOW_SENSOR: "sensor.flow",
        const.ZONE_SIZE: 10.0,
        const.ZONE_BUCKET: -5.0,  # deficit -> target volume 50 L
        const.ZONE_MAXIMUM_DURATION: 3600,
        const.ZONE_IRRIGATION_TARGET_BUCKET: 0.0,
    }
    zone.update(overrides)
    return zone


async def test_flow_never_started_faults_and_skips_credit(monkeypatch):
    # Since FM-3 the metered run reads the flow sensor through the FlowMeter (the old
    # per-step increment seam is retired); a rate sensor stuck at 0 L/min delivers nothing.
    coord = _runner(monkeypatch, {"sensor.flow": _st("0")})
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord._live_run_zones = set()

    await coord._run_valve_metered(
        _flow_zone(**{const.ZONE_MAXIMUM_DURATION: 30}), "switch.f", real_flow=True
    )

    assert _no_bucket_replenished(coord.store.async_update_zone)
    assert coord.get_zone_fault(2)["reason"] == const.FAULT_FLOW_NEVER_STARTED


async def test_flow_delivered_credits_bucket_and_clears_fault(monkeypatch):
    # Since FM-3 flow is fed through the FlowMeter from the sensor state: a rate sensor
    # at 12 L/min over the 150 s safety window integrates to 30 L (a partial run).
    coord = _runner(monkeypatch, {"sensor.flow": _st("12")})
    monkeypatch.setattr(
        "custom_components.smart_irrigation.irrigation.asyncio.sleep", AsyncMock()
    )
    coord._set_zone_fault(2, const.FAULT_FLOW_NEVER_STARTED)
    coord._live_run_zones = set()

    await coord._run_valve_metered(
        _flow_zone(**{const.ZONE_MAXIMUM_DURATION: 150}), "switch.f", real_flow=True
    )

    changes = _bucket_change(coord.store.async_update_zone)
    assert changes is not None
    # 30 L over 10 m^2 = 3 mm; bucket -5 + 3 = -2 (capped at the 0.0 floor).
    assert changes[const.ZONE_BUCKET] == pytest.approx(-2.0)
    assert coord.get_zone_fault(2) is None
