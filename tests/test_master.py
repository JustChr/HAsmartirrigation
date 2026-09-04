"""Master switch / pump control."""

import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from custom_components.irrigation_plus.master import MasterMixin
from custom_components.irrigation_plus.store import (
    STORAGE_VERSION,
    Config,
    async_get_registry,
)


class _MasterHost(MasterMixin):
    """Minimal host to unit-test the mixin in isolation."""


def _mcoord(**master_cfg):
    c = _MasterHost()
    c.hass = Mock()
    c.hass.services.async_call = AsyncMock()
    c.store = Mock()
    c.store.config = SimpleNamespace(
        master_entity=master_cfg.get("master_entity", "switch.pump"),
        master_settle_seconds=master_cfg.get("master_settle_seconds", 10),
        master_kick_enabled=master_cfg.get("master_kick_enabled", False),
        master_kick_pause_seconds=master_cfg.get("master_kick_pause_seconds", 1.0),
        master_off_after=master_cfg.get("master_off_after", False),
    )
    # Isolate the real sleep; record the requested delays instead.
    c._master_sleep = AsyncMock()
    return c


def test_storage_version_is_14():
    # v14 reshapes recurring schedules: the old `type` field is split into
    # `recurrence` plus independent Start/Finish bounds (see
    # tests/test_schedule_migration_v14.py).
    assert STORAGE_VERSION == 14


def test_config_has_master_defaults():
    c = Config()
    assert c.master_entity is None
    assert c.master_settle_seconds == 10
    assert c.master_kick_enabled is False
    assert c.master_kick_pause_seconds == 1.0
    assert c.master_off_after is False


async def test_migration_seeds_master_defaults(hass):
    reg = await async_get_registry(hass)
    data = {"config": {}, "zones": []}
    await reg._store._async_migrate_func(9, data)
    cfg = data["config"]
    assert cfg["master_entity"] is None
    assert cfg["master_settle_seconds"] == 10
    assert cfg["master_kick_enabled"] is False
    assert cfg["master_kick_pause_seconds"] == 1.0
    assert cfg["master_off_after"] is False


async def test_master_begin_turns_on_and_settles():
    c = _mcoord()
    await c.async_master_begin_cycle()
    c.hass.services.async_call.assert_awaited_once_with(
        "homeassistant", "turn_on", {"entity_id": "switch.pump"}
    )
    c._master_sleep.assert_awaited_once_with(10)
    assert c._master_on is True


async def test_master_kick_pulses_off_then_on():
    c = _mcoord(
        master_kick_enabled=True, master_kick_pause_seconds=1.0, master_settle_seconds=5
    )
    await c.async_master_begin_cycle()
    calls = [ck.args for ck in c.hass.services.async_call.await_args_list]
    assert calls[0] == ("homeassistant", "turn_off", {"entity_id": "switch.pump"})
    assert calls[1] == ("homeassistant", "turn_on", {"entity_id": "switch.pump"})
    sleeps = [s.args[0] for s in c._master_sleep.await_args_list]
    assert sleeps == [1.0, 5]  # kick pause, then settle


async def test_master_not_configured_is_noop():
    c = _mcoord(master_entity=None)
    await c.async_master_begin_cycle()
    c.hass.services.async_call.assert_not_awaited()


async def test_master_begin_idempotent_while_on():
    c = _mcoord()
    await c.async_master_begin_cycle()
    c.hass.services.async_call.reset_mock()
    c._master_sleep.reset_mock()
    await c.async_master_begin_cycle()  # already on
    c.hass.services.async_call.assert_not_awaited()
    c._master_sleep.assert_not_awaited()


def test_master_note_run_keeps_latest_deadline():
    c = _mcoord(master_off_after=True)
    t0 = datetime.datetime(2026, 7, 1, 8, 0, 0, tzinfo=datetime.timezone.utc)
    c._master_now = Mock(return_value=t0)
    c._master_note_run(60)
    c._master_note_run(600)
    c._master_note_run(120)  # shorter must not shrink the deadline
    assert c._master_off_deadline == t0 + datetime.timedelta(seconds=600)


async def test_master_valve_master_uses_open_close():
    c = _mcoord(master_entity="valve.main")
    await c.async_master_begin_cycle()
    c.hass.services.async_call.assert_awaited_once_with(
        "valve", "open_valve", {"entity_id": "valve.main"}
    )


async def test_master_off_disabled_arms_and_resets_without_turn_off(monkeypatch):
    c = _mcoord(master_off_after=False)
    captured = {}
    monkeypatch.setattr(
        "custom_components.irrigation_plus.master.async_call_later",
        lambda hass, delay, cb: captured.update(cb=cb) or Mock(),
    )
    t0 = datetime.datetime(2026, 7, 1, 8, 0, 0, tzinfo=datetime.timezone.utc)
    c._master_now = Mock(return_value=t0)
    c._master_on = True
    c._master_note_run(60)
    await c.async_master_schedule_off()
    assert "cb" in captured  # a cycle-end timer IS armed (to reset the flag)

    # Firing at the deadline resets the on-flag but never turns the master off.
    c._master_now = Mock(return_value=t0 + datetime.timedelta(seconds=61))
    await captured["cb"](None)
    off_calls = [
        ck
        for ck in c.hass.services.async_call.await_args_list
        if ck.args[1] in ("turn_off", "close_valve")
    ]
    assert off_calls == []
    assert c._master_on is False  # re-armed for the next cycle


async def test_master_off_enabled_arms_and_fires(monkeypatch):
    c = _mcoord(master_off_after=True)
    captured = {}

    def fake_later(hass, delay, cb):
        captured["delay"] = delay
        captured["cb"] = cb
        return Mock()

    monkeypatch.setattr(
        "custom_components.irrigation_plus.master.async_call_later", fake_later
    )
    t0 = datetime.datetime(2026, 7, 1, 8, 0, 0, tzinfo=datetime.timezone.utc)
    c._master_now = Mock(return_value=t0)
    c._master_on = True
    c._master_note_run(60)
    await c.async_master_schedule_off()
    assert 59 <= captured["delay"] <= 61

    # deadline passed -> firing turns the master off
    c._master_now = Mock(return_value=t0 + datetime.timedelta(seconds=61))
    await captured["cb"](None)
    c.hass.services.async_call.assert_awaited_with(
        "homeassistant", "turn_off", {"entity_id": "switch.pump"}
    )
    assert c._master_on is False


async def test_run_zone_self_closing_delegates_master_to_the_run():
    """A manual run_zone on a self-closing zone must still bring the master up —
    but the responsibility moved INTO async_run_self_closing, which takes a master
    hold for the whole fire-and-forget window and releases it when the run
    finalises. run_zone predicting the duration up front was the old model; the
    hardware, not run_zone, decides when a self-closing valve actually shuts.
    """
    from custom_components.irrigation_plus import SmartIrrigationCoordinator, const

    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    assert isinstance(c, MasterMixin)  # mixin is wired into the coordinator
    c.hass = Mock()
    zone = {
        const.ZONE_ID: 2,
        const.ZONE_NAME: "Beet",
        const.ZONE_STATE: "automatic",
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
    }
    c.store = Mock()
    c.store.get_zone = Mock(return_value=zone)
    c.async_run_self_closing = AsyncMock(return_value=True)
    c.async_master_begin_cycle = AsyncMock()
    c._master_note_run = Mock()
    c.async_master_schedule_off = AsyncMock()

    await c.async_run_zone(2, 5.0)  # 5 min -> 300 s

    # The run is dispatched with the requested duration...
    c.async_run_self_closing.assert_awaited_once()
    dispatched = c.async_run_self_closing.await_args.args[0]
    assert dispatched[const.ZONE_DURATION] == 300
    # ...and run_zone no longer predicts a master window of its own.
    c._master_note_run.assert_not_called()


async def test_self_closing_run_holds_the_master_across_its_window():
    """The hold spans the fire-and-forget window: taken before the valve opens and
    still held after dispatch returns, because the HARDWARE owns the close."""
    import types

    from custom_components.irrigation_plus import SmartIrrigationCoordinator, const

    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.hass.services = Mock()
    c.hass.services.async_call = AsyncMock()
    c.store = Mock()
    c.store.config = types.SimpleNamespace(
        master_entity="switch.pump",
        master_off_after=True,
        master_settle_seconds=0,
        master_kick_enabled=False,
        master_kick_pause_seconds=0,
    )
    c.store.get_zone = Mock(return_value={const.ZONE_ID: 7})
    c.store.async_update_zone = AsyncMock()
    c._sc_dispatch_open = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._confirm_valve_running = AsyncMock(return_value=None)
    c._sc_add_run = AsyncMock()
    c._sc_schedule_cleanup = Mock()
    c._sc_fire = Mock()
    c._note_si_valve = Mock()
    c._timed_volume_l = Mock(return_value=0.0)
    c._credited_depth_native = Mock(return_value=0.0)
    c.async_master_schedule_off = AsyncMock()  # no real event loop in this double

    zone = {
        const.ZONE_ID: 7,
        const.ZONE_NAME: "Beet",
        const.ZONE_DURATION: 300,
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
    }
    assert await c.async_run_self_closing(zone) is True

    # Master was powered up, and the hold is STILL held after dispatch returned.
    c.hass.services.async_call.assert_any_await(
        "homeassistant", "turn_on", {"entity_id": "switch.pump"}
    )
    assert c._sc_master_token(7) in c.master_holds()


async def test_self_closing_release_on_confirm_failure_does_not_strand_the_pump():
    """A valve that never opens must not leave a hold behind — a leaked hold keeps
    the master on forever, which is the one failure refcounting could introduce."""
    import types

    from custom_components.irrigation_plus import SmartIrrigationCoordinator, const

    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.hass.services = Mock()
    c.hass.services.async_call = AsyncMock()
    c.hass.loop = Mock()
    c.hass.loop.time = Mock(return_value=0.0)
    c.store = Mock()
    c.store.config = types.SimpleNamespace(
        master_entity="switch.pump",
        master_off_after=True,
        master_settle_seconds=0,
        master_kick_enabled=False,
        master_kick_pause_seconds=0,
    )
    c._sc_dispatch_open = AsyncMock()
    c._sc_start_flow_sampling = AsyncMock()
    c._sc_finish_flow = Mock(return_value=(None, {}))
    c._confirm_valve_running = AsyncMock(return_value=False)  # never opened
    c._sc_fire = Mock()
    c._note_si_valve = Mock()
    c.async_master_schedule_off = AsyncMock()  # no real loop in this double

    zone = {
        const.ZONE_ID: 7,
        const.ZONE_NAME: "Beet",
        const.ZONE_DURATION: 300,
        const.ZONE_CONFIRM_ENTITY: "switch.valve",
        const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
    }
    assert await c.async_run_self_closing(zone) is False
    assert c.master_holds() == set(), "aborted run leaked a master hold"


async def test_reconcile_master_off_when_off_after_and_idle():
    # Bug 2 (2026-07-06): off_after enabled, master configured, nothing HASI-driven
    # still running -> defensively power the orphaned master off after a restart.
    c = _mcoord(master_off_after=True)
    c.store.async_get_distributors = AsyncMock(return_value=[])
    c._sc_active_runs = AsyncMock(return_value=[])
    c._master_on = True
    c._master_off_deadline = "stale"
    await c.async_reconcile_master_after_restart()
    c.hass.services.async_call.assert_awaited_once_with(
        "homeassistant", "turn_off", {"entity_id": "switch.pump"}
    )
    assert c._master_on is False
    assert c._master_off_deadline is None


async def test_reconcile_master_untouched_when_off_after_disabled():
    # off_after off -> HASI never auto-shuts the master, so it must not at boot either.
    c = _mcoord(master_off_after=False)
    c.store.async_get_distributors = AsyncMock(return_value=[])
    c._sc_active_runs = AsyncMock(return_value=[])
    await c.async_reconcile_master_after_restart()
    c.hass.services.async_call.assert_not_awaited()


async def test_reconcile_master_untouched_when_self_closing_active():
    # A self-closing run is still mid-window on hardware -> it legitimately needs the
    # master; defer (do not power off).
    c = _mcoord(master_off_after=True)
    c.store.async_get_distributors = AsyncMock(return_value=[])
    c._sc_active_runs = AsyncMock(return_value=[{"zone_id": 7}])
    await c.async_reconcile_master_after_restart()
    c.hass.services.async_call.assert_not_awaited()


async def test_reconcile_master_untouched_when_distributor_cycle_in_flight():
    # A distributor still has a persisted active_cycle -> something is (being) resumed;
    # do not force the master off.
    c = _mcoord(master_off_after=True)
    c.store.async_get_distributors = AsyncMock(
        return_value=[{"id": 0, "active_cycle": {"outlet": 1, "phase": "watering"}}]
    )
    c._sc_active_runs = AsyncMock(return_value=[])
    await c.async_reconcile_master_after_restart()
    c.hass.services.async_call.assert_not_awaited()


async def test_reconcile_noop_when_master_not_configured():
    c = _mcoord(master_entity=None)
    c.store.async_get_distributors = AsyncMock(return_value=[])
    c._sc_active_runs = AsyncMock(return_value=[])
    await c.async_reconcile_master_after_restart()
    c.hass.services.async_call.assert_not_awaited()
