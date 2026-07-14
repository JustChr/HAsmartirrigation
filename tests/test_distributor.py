"""Gardena distributor engine primitives (DistributorMixin)."""

import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.distributor import DistributorMixin
from custom_components.smart_irrigation.flow_metering import (
    flow_is_totalizer,
    flow_litres_from_total,
)
from custom_components.smart_irrigation.irrigation import IrrigationRunnerMixin
from custom_components.smart_irrigation.master import MasterMixin
from custom_components.smart_irrigation.skip_conditions import SkipConditionsMixin


class _DistHost(
    DistributorMixin, MasterMixin, SkipConditionsMixin, IrrigationRunnerMixin
):
    """Minimal host to unit-test the distributor mixin in isolation."""


def _host(**master_cfg):
    c = _DistHost()
    c.hass = Mock()
    # _dist_store_update now fires the real async_dispatcher_send; give hass.data a
    # real dict (no 'dispatcher' key) so the dispatcher short-circuits cleanly
    # instead of trying to iterate a Mock (I2: distributor entity signals).
    c.hass.data = {}
    c.hass.services.async_call = AsyncMock()
    c.hass.bus.async_fire = Mock()
    c.store = Mock()
    c.store.async_update_distributor = AsyncMock()
    c.store.config = SimpleNamespace(
        master_entity=master_cfg.get("master_entity", "switch.pump"),
        master_settle_seconds=master_cfg.get("master_settle_seconds", 10),
        master_kick_enabled=master_cfg.get("master_kick_enabled", False),
        master_kick_pause_seconds=master_cfg.get("master_kick_pause_seconds", 1.0),
        master_off_after=master_cfg.get("master_off_after", False),
    )
    c._master_sleep = AsyncMock()
    return c


def _dist(**kw):
    d = {
        "id": 0,
        "name": "Garten",
        "watering_mode": const.WATERING_MODE_CLASSIC,
        "inlet_entity": "switch.inlet",
        "run_service": "script.dist_inlet",
        "stop_service": None,
        "duration_field": "duration",
        "duration_unit": const.DURATION_UNIT_SECONDS,
        "pause_seconds": 120,
        "skip_pulse_seconds": 20,
        "current_outlet": 1,
        "position_state": const.POSITION_STATE_SYNCED,
        "notify_target": None,
        "use_master": True,
        "commissioning_confirmed": True,
    }
    d.update(kw)
    return d


async def test_domain_turn_switch_uses_turn_on_off():
    c = _host()
    await c._dist_domain_turn("switch.inlet", True)
    c.hass.services.async_call.assert_awaited_once_with(
        "homeassistant", "turn_on", {"entity_id": "switch.inlet"}
    )


async def test_domain_turn_valve_uses_open_close():
    c = _host()
    await c._dist_domain_turn("valve.inlet", False)
    c.hass.services.async_call.assert_awaited_once_with(
        "valve", "close_valve", {"entity_id": "valve.inlet"}
    )


async def test_open_inlet_classic_opens_entity():
    c = _host()
    await c._dist_open_inlet(_dist(), 30)
    c.hass.services.async_call.assert_awaited_once_with(
        "homeassistant", "turn_on", {"entity_id": "switch.inlet"}
    )


async def test_open_inlet_service_fires_run_service_with_converted_duration():
    c = _host()
    d = _dist(
        watering_mode=const.WATERING_MODE_SERVICE,
        duration_field="dauer",
        duration_unit=const.DURATION_UNIT_MINUTES,
    )
    await c._dist_open_inlet(d, 600)  # 600 s -> 10 min
    domain, service, data = c.hass.services.async_call.await_args.args
    assert (domain, service) == ("script", "dist_inlet")
    assert data["dauer"] == 10
    assert data["distributor_id"] == 0


async def test_close_inlet_classic_closes_entity():
    c = _host()
    await c._dist_close_inlet(_dist())
    c.hass.services.async_call.assert_awaited_once_with(
        "homeassistant", "turn_off", {"entity_id": "switch.inlet"}
    )


async def test_close_inlet_service_without_stop_is_noop():
    c = _host()
    await c._dist_close_inlet(_dist(watering_mode=const.WATERING_MODE_SERVICE))
    c.hass.services.async_call.assert_not_awaited()


async def test_close_inlet_service_fires_stop_service():
    c = _host()
    d = _dist(watering_mode=const.WATERING_MODE_SERVICE, stop_service="script.dist_off")
    await c._dist_close_inlet(d)
    domain, service, _ = c.hass.services.async_call.await_args.args
    assert (domain, service) == ("script", "dist_off")


async def test_advance_increments_and_persists():
    c = _host()
    new = await c._dist_advance(0, current_outlet=1, outlet_count=3)
    assert new == 2
    c.store.async_update_distributor.assert_awaited_once_with(0, {"current_outlet": 2})


async def test_advance_wraps_to_one_at_ring_end():
    c = _host()
    new = await c._dist_advance(0, current_outlet=3, outlet_count=3)
    assert new == 1
    c.store.async_update_distributor.assert_awaited_once_with(0, {"current_outlet": 1})


async def test_notify_persistent_always_even_without_target():
    # FB4: a halt always surfaces in the Notifications panel, keyed per
    # distributor, regardless of whether a notify target is configured.
    c = _host()
    await c._dist_notify(_dist(id=3, notify_target=None), "boom")
    c.hass.services.async_call.assert_awaited_once()
    domain, service, data = c.hass.services.async_call.await_args.args
    assert (domain, service) == ("persistent_notification", "create")
    assert data["message"] == "boom"
    assert data["notification_id"] == f"{const.DOMAIN}_distributor_3"


async def test_notify_persistent_plus_optional_service():
    # FB4: a 'domain.service' target is an ADDITIONAL channel on top of the
    # unconditional persistent notification (panel first, then the service).
    c = _host()
    await c._dist_notify(_dist(notify_target="notify.mobile"), "boom")
    calls = c.hass.services.async_call.await_args_list
    assert len(calls) == 2
    assert calls[0].args[:2] == ("persistent_notification", "create")
    assert calls[1].args[:2] == ("notify", "mobile")
    assert calls[1].args[2]["message"] == "boom"


async def test_notify_bare_target_only_persistent():
    # A target that is not 'domain.service' adds no extra channel — just panel.
    c = _host()
    await c._dist_notify(_dist(notify_target="persistent_notification"), "boom")
    c.hass.services.async_call.assert_awaited_once()
    domain, service, _ = c.hass.services.async_call.await_args.args
    assert (domain, service) == ("persistent_notification", "create")


async def test_mark_uncertain_de_arms_persists_fires_and_notifies(monkeypatch):
    c = _host()

    # _dist_mark_uncertain now localizes its message via localize(); mock it so this
    # stays a pure unit test (no JSON file I/O) — the message text is asserted
    # separately in test_mark_uncertain_localizes_notification.
    async def _fake_localize(key, lang):
        return key

    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.localize", _fake_localize
    )
    d = _dist(notify_target="notify.mobile")
    await c._dist_mark_uncertain(d, reason="no_flow")

    # position uncertain AND commissioning de-armed, in one persist
    c.store.async_update_distributor.assert_awaited_once_with(
        0,
        {
            "position_state": const.POSITION_STATE_UNCERTAIN,
            "commissioning_confirmed": False,
        },
    )
    # halted event fired with the reason
    evt = c.hass.bus.async_fire.call_args.args
    assert evt[0] == f"{const.DOMAIN}_{const.EVENT_DISTRIBUTOR_HALTED}"
    assert evt[1]["reason"] == "no_flow"
    assert evt[1]["distributor_id"] == 0
    # user notified
    c.hass.services.async_call.assert_awaited()


async def test_master_start_engages_begin_cycle():
    c = _host()
    c.async_master_begin_cycle = AsyncMock()
    await c._dist_master_start(_dist())
    c.async_master_begin_cycle.assert_awaited_once()


async def test_master_start_noop_when_use_master_false():
    c = _host()
    c.async_master_begin_cycle = AsyncMock()
    await c._dist_master_start(_dist(use_master=False))
    c.async_master_begin_cycle.assert_not_awaited()


async def test_window_off_powers_master_down_when_off_after_and_exclusive():
    c = _host(master_off_after=True)
    await c._dist_master_window_off(_dist(), concurrent=False)
    c.hass.services.async_call.assert_awaited_once_with(
        "homeassistant", "turn_off", {"entity_id": "switch.pump"}
    )


async def test_window_off_noop_when_not_off_after():
    c = _host(master_off_after=False)
    await c._dist_master_window_off(_dist(), concurrent=False)
    c.hass.services.async_call.assert_not_awaited()


async def test_window_off_noop_when_concurrent():
    c = _host(master_off_after=True)
    await c._dist_master_window_off(_dist(), concurrent=True)
    c.hass.services.async_call.assert_not_awaited()


async def test_window_on_powers_up_and_settles():
    c = _host(master_off_after=True, master_settle_seconds=7)
    await c._dist_master_window_on(_dist(), concurrent=False)
    c.hass.services.async_call.assert_awaited_once_with(
        "homeassistant", "turn_on", {"entity_id": "switch.pump"}
    )
    c._master_sleep.assert_awaited_once_with(7)


async def test_master_end_defers_to_overlap_safe_deadline_when_using_master():
    # G2/H1 -> Bug 1 (2026-07-06): the defer path is now keyed on a real pre-existing
    # external deadline (pre_deadline snapshot), not the static concurrent flag. On a
    # real overlap: no immediate off, deadline collapsed to the external floor, shutdown
    # handed to the overlap-safe scheduler. Solo (pre_deadline None) finalizes
    # synchronously instead (see test_master_end_finalizes_synchronously_when_solo).
    c = _host(master_off_after=True)
    c.async_master_schedule_off = AsyncMock()
    c._master_on = True
    pre = c._master_now() + datetime.timedelta(seconds=120)
    await c._dist_master_end(_dist(), pre_deadline=pre)
    c.hass.services.async_call.assert_not_awaited()
    c.async_master_schedule_off.assert_awaited_once()
    assert c._master_off_deadline == pre


async def test_master_end_clears_flag_immediately_when_not_using_master():
    # A distributor that does not use the master short-circuits: it powers
    # nothing off and clears the on-flag directly, without touching the shared
    # deadline mechanism.
    c = _host(master_off_after=True)
    c._master_note_run = Mock()
    c.async_master_schedule_off = AsyncMock()
    c._master_on = True
    await c._dist_master_end(_dist(use_master=False))
    c.hass.services.async_call.assert_not_awaited()
    c._master_note_run.assert_not_called()
    c.async_master_schedule_off.assert_not_awaited()
    assert c._master_on is False


def _zone(duration):
    return {const.ZONE_DURATION: duration}


def test_cycle_estimate_sums_windows_pauses_and_buffer():
    c = _host(master_off_after=False)
    d = _dist(pause_seconds=100, skip_pulse_seconds=20)
    # 3 outlets, current_outlet=1: two due (60 s, 40 s), the LAST is non-due (0).
    # E2 early-stop: the trailing non-due outlet is never visited, so the sweep
    # stops after outlet 2 (k=2) -- its 20 s skip-pulse is NOT counted.
    zones = [_zone(60), _zone(40), _zone(0)]
    est = c.distributor_cycle_estimate(d, zones)
    # windows 60+40=100, pauses (k-1)=1 * 100 = 100, buffer 30 -> 230 (no settle)
    assert est == 100 + 100 + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS


def test_cycle_estimate_adds_master_settle_when_cycling():
    c = _host(master_off_after=True, master_settle_seconds=10)
    d = _dist(pause_seconds=100, skip_pulse_seconds=20)
    zones = [_zone(60), _zone(40), _zone(0)]
    est = c.distributor_cycle_estimate(d, zones)
    # E2: sweep stops after outlet 2 (k=2); settle is per inter-outlet gap = (k-1).
    # windows 100 + pauses 1*100 + settle 1*10 + buffer 30 -> 240
    assert est == 100 + 100 + 1 * 10 + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS


def test_cycle_estimate_clamps_sub_floor_pause_and_pulse():
    c = _host(master_off_after=False)
    d = _dist(pause_seconds=5, skip_pulse_seconds=2)  # below the 10 s floor
    # E2: at least one outlet must be due or the sweep is empty (0.0) and the
    # floors are never reached. Outlet 1 non-due (skip-pulsed to reach the due
    # tail), outlet 2 due (5 s) -> k=2, both floors exercised.
    zones = [_zone(0), _zone(5)]
    est = c.distributor_cycle_estimate(d, zones)
    # skip clamped 2->10, pause clamped 5->10: windows 10(skip)+5=15,
    # pauses (k-1)=1 * 10 = 10, buffer 30 -> 55
    assert est == 15 + 10 + const.DISTRIBUTOR_CYCLE_SAFETY_BUFFER_SECONDS


def test_cycle_estimate_zero_for_no_members():
    c = _host()
    assert c.distributor_cycle_estimate(_dist(), []) == 0.0


async def test_cycle_persists_phase_constants_not_raw_strings():
    c = _host()
    # E1 (early-stop): the PAUSING persist only fires BETWEEN swept outlets. Use a
    # test-run over TWO outlets (test-run always sweeps every outlet) so the
    # pause-block transition after outlet 1 is exercised — a single-outlet run now
    # stops right after watering with no trailing PAUSING persist.
    c.store.async_get_zones = AsyncMock(
        return_value=[
            {
                "id": 7,
                "distributor_id": 0,
                "outlet_number": 1,
                "duration": 5,
                "bucket": -1,
                "bucket_threshold": 0,
                "state": "automatic",
            },
            {
                "id": 8,
                "distributor_id": 0,
                "outlet_number": 2,
                "duration": 5,
                "bucket": -1,
                "bucket_threshold": 0,
                "state": "automatic",
            },
        ]
    )
    c._dist_persist_cycle = AsyncMock()
    c._dist_sleep = AsyncMock()
    c._dist_open_inlet = AsyncMock()
    c._dist_close_inlet = AsyncMock()
    # G2: cycle end now defers the master shutdown to the shared overlap-safe
    # scheduler; stub it (bare-Mock hass has no real loop for async_call_later).
    c.async_master_schedule_off = AsyncMock()
    await c.async_run_distributor_cycle(_dist(current_outlet=1), test_run=True)
    phases = [call.args[2] for call in c._dist_persist_cycle.await_args_list]
    assert const.DISTRIBUTOR_PHASE_WATERING in phases
    assert const.DISTRIBUTOR_PHASE_PAUSING in phases


def test_watch_mode_derives_from_legacy_watch_inlet():
    c = _host()
    assert c._dist_watch_mode({"watch_mode": "warn", "watch_inlet": True}) == "warn"
    assert (
        c._dist_watch_mode({"watch_inlet": True}) == const.DISTRIBUTOR_WATCH_MODE_COUNT
    )
    assert (
        c._dist_watch_mode({"watch_inlet": False})
        == const.DISTRIBUTOR_WATCH_MODE_IGNORE
    )
    assert c._dist_watch_mode({}) == const.DISTRIBUTOR_WATCH_MODE_IGNORE


async def test_upsert_persists_watch_mode():
    # E4: a distributor config POST carrying watch_mode round-trips to the store
    # update (the attrs allowlist keeps it now that it is a DistributorEntry field).
    c = _host()
    c.store.get_distributor = Mock(return_value={"id": 0})
    c._dist_refresh_inlet_watch = Mock()
    await c.async_upsert_distributor({"id": 0, "watch_mode": "warn"})
    changes = c.store.async_update_distributor.await_args.args[1]
    assert changes.get("watch_mode") == "warn"


async def test_mark_uncertain_localizes_notification(monkeypatch):
    # The halt notification is built via localize() keyed on hass.config.language,
    # with the reason phrase resolved and {name}/{reason} filled by replace().
    c = _host()
    c.hass.config.language = "de"
    seen = []

    async def _fake_localize(key, lang):
        seen.append((key, lang))
        if key.endswith(".reason.valve_did_not_open"):
            return "Ventil hat nicht geöffnet"
        if key.endswith(".halted"):
            return "Verteiler '{name}' angehalten ({reason})."
        return key

    monkeypatch.setattr(
        "custom_components.smart_irrigation.distributor.localize", _fake_localize
    )
    captured = {}
    c._dist_notify = AsyncMock(side_effect=lambda d, m: captured.update(msg=m))
    await c._dist_mark_uncertain(
        _dist(name="Garten"), reason=const.PROBLEM_VALVE_DID_NOT_OPEN
    )
    assert (
        captured["msg"] == "Verteiler 'Garten' angehalten (Ventil hat nicht geöffnet)."
    )
    assert ("panels.distributors.notify.halted", "de") in seen
    assert (
        f"panels.distributors.notify.reason.{const.PROBLEM_VALVE_DID_NOT_OPEN}",
        "de",
    ) in seen


async def test_mark_uncertain_notification_real_localize_de_and_en():
    # End-to-end: the real localize() reads the shipped JSONs; DE yields the German
    # template + reason phrase, EN the English, keyed on hass.config.language.
    for lang, expected in (
        (
            "de",
            "Verteiler 'Garten' angehalten (Ventil hat nicht geöffnet). "
            "Neu synchronisieren und erneut bestätigen erforderlich.",
        ),
        (
            "en",
            "Distributor 'Garten' halted (valve did not open). "
            "Re-sync and re-confirm required.",
        ),
    ):
        c = _host()
        c.hass.config.language = lang
        captured = {}
        c._dist_notify = AsyncMock(
            side_effect=lambda d, m, cap=captured: cap.update(msg=m)
        )
        await c._dist_mark_uncertain(
            _dist(name="Garten"), reason=const.PROBLEM_VALVE_DID_NOT_OPEN
        )
        assert captured["msg"] == expected


# --- Phase 4 Part A: flow-metered window measurement ------------------------


def _flow_host(sensor="sensor.inlet_flow"):
    c = _host()
    c._dist_sleep = AsyncMock()
    d = _dist(watering_mode=const.WATERING_MODE_SERVICE, flow_sensor=sensor)
    return c, d


def _state(val, unit):
    s = Mock()
    s.state = str(val)
    s.attributes = {"unit_of_measurement": unit}
    return s


def test_flow_is_totalizer():
    # A rate unit (contains '/') is NOT a totalizer; a bare unit is.
    assert flow_is_totalizer("L/min", None) is False
    assert flow_is_totalizer("m³/h", None) is False
    assert flow_is_totalizer("L", None) is True
    assert flow_is_totalizer("m³", None) is True


def test_flow_litres_from_total_units():
    assert flow_litres_from_total(2.0, "L") == 2.0
    assert flow_litres_from_total(2.0, "m³") == 2000.0
    assert round(flow_litres_from_total(1.0, "gal"), 4) == 3.7854
    assert flow_litres_from_total(5.0, "weird") == 5.0


async def test_measure_window_cumulative_counter():
    # A totalizer flow sensor (bare unit, no '/') is metered by default — no flag.
    c, d = _flow_host()
    vals = iter([100.0, 102.0, 104.0, 106.0])
    c.hass.states.get = Mock(side_effect=lambda s: _state(next(vals), "L"))
    measured, actual, stopped = await c._dist_measure_window(d, 15)
    assert measured == 6.0
    assert actual == 15
    assert stopped is False


async def test_measure_window_rate_sensor():
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=_state(12.0, "L/min"))
    measured, actual, stopped = await c._dist_measure_window(d, 60)
    assert round(measured, 3) == 12.0
    assert actual == 60
    assert stopped is False


async def test_measure_window_no_sensor_returns_none():
    c = _host()
    c._dist_sleep = AsyncMock()
    measured, actual, stopped = await c._dist_measure_window(
        _dist(flow_sensor=None), 30
    )
    assert measured is None
    assert actual == 30
    assert stopped is False
    c._dist_sleep.assert_awaited_once_with(30)


async def test_measure_window_unavailable_falls_back_none():
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=None)
    measured, actual, stopped = await c._dist_measure_window(d, 30)
    assert measured is None
    assert actual == 30
    c._dist_sleep.assert_awaited_once_with(30)


async def test_measure_window_counter_drop_keeps_baseline():
    # FM-6: the window now meters via the shared FlowMeter. The distributor defaults
    # auto -> lifetime (over-credit-safe keep-baseline), so a mid-window counter drop
    # (100 -> 102 -> 5 -> 7) credits ONLY the 100->102 rise (2 L) and never over-credits
    # the dip — measured 2.0, not None. This intentionally supersedes the OLD
    # "counter reset -> unreliable/None" expectation (a lifetime totalizer keeps its
    # baseline instead of flagging the whole run unreliable). See also the per_run test
    # below, where an explicit per_run override reseeds at the open reset.
    c, d = _flow_host()
    vals = iter([100.0, 102.0, 5.0, 7.0])
    c.hass.states.get = Mock(side_effect=lambda s: _state(next(vals), "L"))
    measured, _, _ = await c._dist_measure_window(d, 15)
    assert measured == 2.0


async def test_dist_measure_window_per_run_counter():
    # FM-6: an inlet counter that resets toward 0 at valve-open then holds the run's
    # accumulated volume. With an explicit per_run override the FlowMeter reseeds once at
    # the open reset (50 -> 0) then credits the climb (0 -> 4 -> 8), yielding 8 L —
    # MEASURED, not None as the old reset-as-unreliable path gave.
    c, d = _flow_host()
    d[const.ZONE_FLOW_COUNTER_TYPE] = "per_run"
    seq = [50.0, 0.0, 4.0, 8.0, 8.0]

    def _drive(_sensor):
        v = (
            seq.pop(0) if len(seq) > 1 else seq[0]
        )  # hold the last value after the climb
        return _state(v, "L")

    c.hass.states.get = Mock(side_effect=_drive)
    measured, actual, stopped = await c._dist_measure_window(d, 60.0)
    assert measured == 8.0
    assert stopped is False


async def test_measure_window_no_unit_falls_back_to_rate():
    # No unit and no total_increasing state_class -> metered as a RATE (the historical
    # zone default), so the window is measured rather than degraded to None.
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=_state(12.0, ""))
    measured, actual, stopped = await c._dist_measure_window(d, 30)
    assert measured is not None
    assert actual == 30
    assert stopped is False


async def test_measure_window_early_stops_at_target():
    # 60 L/min == 1 L/s; target 30 L reached at 30 s (< 60 s cap)
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=_state(60.0, "L/min"))
    measured, actual, stopped = await c._dist_measure_window(d, 60, target=30.0)
    assert stopped is True
    assert actual == 30
    assert round(measured, 3) == 30.0


async def test_measure_window_classic_extend_past_window():
    # 30 L/min == 0.5 L/s; target 30 L needs 60 s — past the 30 s window, within 120 s cap
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=_state(30.0, "L/min"))
    measured, actual, stopped = await c._dist_measure_window(
        d, 30, cap=120, target=30.0
    )
    assert stopped is True
    assert actual == 60  # ran past the 30 s window
    assert round(measured, 3) == 30.0


async def test_measure_window_target_not_reached_runs_to_cap():
    # 60 L/min for a 30 s cap delivers 30 L < 100 L target -> full cap, no early stop
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=_state(60.0, "L/min"))
    measured, actual, stopped = await c._dist_measure_window(d, 30, target=100.0)
    assert stopped is False
    assert actual == 30
    assert round(measured, 3) == 30.0


async def test_measure_window_dead_sensor_sleeps_window_not_cap():
    # A classic-extend call passes cap=1200 but a dead sensor must sleep only the
    # window (30) so a dead meter never extends the run.
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=None)
    measured, actual, stopped = await c._dist_measure_window(
        d, 30, cap=1200, target=50.0
    )
    assert measured is None
    assert actual == 30
    c._dist_sleep.assert_awaited_once_with(30)


async def test_measure_window_zero_flow_healthy_sensor_is_unreliable():
    # A live meter reading 0 the whole window (dry pipe / stuck valve) is unreliable
    # -> None (fall back to time-based crediting), NOT a credited 0 L. Part B fail-safe.
    c, d = _flow_host()
    c.hass.states.get = Mock(return_value=_state(0.0, "L/min"))
    measured, actual, stopped = await c._dist_measure_window(d, 30)
    assert measured is None
    assert actual == 30
    assert stopped is False


# --- Phase 4 Part A: crediting the measured flow volume ---------------------


async def test_credit_zone_uses_measured_volume_when_given():
    c = _host()
    c.store.async_update_zone = AsyncMock()
    c._record_run = AsyncMock()
    c._depth_from_volume_native = Mock(return_value=1.0)  # measured -> GROSS depth
    c._credited_depth_native = Mock(return_value=999.0)  # must NOT be used
    c._timed_volume_l = Mock(return_value=999.0)  # must NOT be used
    z = {const.ZONE_ID: 7, const.ZONE_BUCKET: -5.0}
    await c._dist_credit_zone(z, 120, measured_l=8.0)
    c._timed_volume_l.assert_not_called()
    c._credited_depth_native.assert_not_called()
    c._depth_from_volume_native.assert_called_once_with(z, 8.0)
    assert c._record_run.await_args.kwargs["volume_l"] == 8.0


async def test_credit_zone_falls_back_to_timed_when_measured_none():
    c = _host()
    c.store.async_update_zone = AsyncMock()
    c._record_run = AsyncMock()
    c._credited_depth_native = Mock(return_value=1.0)  # timed -> multiplier-divided
    c._depth_from_volume_native = Mock(return_value=999.0)  # must NOT be used here
    c._timed_volume_l = Mock(return_value=4.0)
    z = {const.ZONE_ID: 7, const.ZONE_BUCKET: -5.0}
    await c._dist_credit_zone(z, 120, measured_l=None)
    c._timed_volume_l.assert_called_once()
    c._credited_depth_native.assert_called_once_with(z, 4.0)
    assert c._record_run.await_args.kwargs["volume_l"] == 4.0


async def test_credit_zone_records_planned_vs_actual_seconds():
    c = _host()
    c.store.async_update_zone = AsyncMock()
    c._record_run = AsyncMock()
    c._depth_from_volume_native = Mock(return_value=1.0)
    z = {const.ZONE_ID: 7, const.ZONE_BUCKET: -5.0}
    await c._dist_credit_zone(z, 45, measured_l=5.0, planned_seconds=120)
    kw = c._record_run.await_args.kwargs
    assert kw["planned_s"] == 120  # the plan was the full window
    assert kw["actual_s"] == 45  # early stop ran 45 s


async def test_credit_zone_timed_fallback_uses_planned_seconds():
    # An unreliable meter that ran past the window (classic extend, 900 s) must credit
    # the PLANNED window's worth time-based, not the extended elapsed seconds — else a
    # dry-but-alive meter would book hours of water that never flowed.
    c = _host()
    c.store.async_update_zone = AsyncMock()
    c._record_run = AsyncMock()
    c._credited_depth_native = Mock(return_value=1.0)
    c._timed_volume_l = Mock(return_value=4.0)
    z = {const.ZONE_ID: 7, const.ZONE_BUCKET: -5.0}
    await c._dist_credit_zone(z, 900, measured_l=None, planned_seconds=60)
    c._timed_volume_l.assert_called_once_with(z, 60)  # planned window, not 900
    kw = c._record_run.await_args.kwargs
    assert kw["actual_s"] == 900  # log stays truthful about the real elapsed time
    assert kw["planned_s"] == 60
