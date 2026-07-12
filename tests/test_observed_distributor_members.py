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


def _member(zid, outlet, state=const.ZONE_STATE_AUTOMATIC):
    return {
        const.ZONE_ID: zid,
        "distributor_id": 0,
        "outlet_number": outlet,
        const.ZONE_STATE: state,
    }


def _dist(**kw):
    d = {
        "id": 0,
        "watch_mode": const.DISTRIBUTOR_WATCH_MODE_COUNT,
        "inlet_entity": "switch.inlet",
        "skip_pulse_seconds": 30,
        "current_outlet": 2,
        "active_cycle": {},
    }
    d.update(kw)
    return d


def _pulse_host(dist, members, observed=True, open_time=100.0):
    c = _host(observed=observed)
    c.store.get_distributor = Mock(return_value=dist)
    c.store.async_get_zones = AsyncMock(return_value=members)
    c.hass.loop.time = Mock(return_value=open_time)
    return c


async def test_open_edge_stashes_preadvance_outlet_and_advances():
    dist = _dist(current_outlet=2)
    members = [_member(1, 1), _member(2, 2), _member(3, 3)]
    c = _pulse_host(dist, members, open_time=100.0)
    await c._dist_on_inlet_pulse(0)
    # Stash captured the PRE-advance ring index + open time.
    assert c._dist_observed_open_map()[0] == {"t": 100.0, "outlet": 2}
    # And the position still advanced exactly as before (2 -> 3 of 3 members).
    c.store.async_update_distributor.assert_awaited_once_with(0, {"current_outlet": 3})


async def test_open_edge_no_stash_when_observed_off():
    dist = _dist(current_outlet=2)
    members = [_member(1, 1), _member(2, 2), _member(3, 3)]
    c = _pulse_host(dist, members, observed=False)
    await c._dist_on_inlet_pulse(0)
    assert 0 not in c._dist_observed_open_map()
    c.store.async_update_distributor.assert_awaited_once()  # still advances


async def test_open_edge_no_stash_in_warn_mode():
    dist = _dist(watch_mode=const.DISTRIBUTOR_WATCH_MODE_WARN)
    members = [_member(1, 1), _member(2, 2)]
    c = _pulse_host(dist, members)
    c._dist_mark_uncertain = AsyncMock()
    await c._dist_on_inlet_pulse(0)
    assert 0 not in c._dist_observed_open_map()


def _close_host(
    dist, members, observed=True, close_time=None, stash_outlet=2, stash_t=100.0
):
    c = _host(observed=observed)
    c.store.get_distributor = Mock(return_value=dist)
    c.store.async_get_zones = AsyncMock(return_value=members)
    c._dist_credit_zone = AsyncMock()
    if close_time is not None:
        c.hass.loop.time = Mock(return_value=close_time)
    if stash_outlet is not None:
        c._dist_observed_open_map()[0] = {"t": stash_t, "outlet": stash_outlet}
    return c


async def test_close_credits_current_member_when_long():
    dist = _dist(skip_pulse_seconds=30)  # threshold = 60 s
    members = [_member(1, 1), _member(2, 2), _member(3, 3)]
    c = _close_host(dist, members, close_time=100.0 + 300, stash_outlet=2)
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_awaited_once()
    zone_arg, seconds_arg = c._dist_credit_zone.await_args.args
    assert zone_arg[const.ZONE_ID] == 2  # ring index 2 -> members[1] -> zone id 2
    assert seconds_arg == 300
    kwargs = c._dist_credit_zone.await_args.kwargs
    assert kwargs["result"] == const.RUN_RESULT_OBSERVED
    assert kwargs["trigger"] == const.RUN_TRIGGER_OBSERVED
    assert 0 not in c._dist_observed_open_map()  # stash consumed


async def test_close_ignores_short_advance_pulse():
    dist = _dist(skip_pulse_seconds=30)  # threshold = 60 s
    members = [_member(1, 1), _member(2, 2)]
    c = _close_host(dist, members, close_time=100.0 + 45, stash_outlet=1)
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_not_awaited()


async def test_close_race_guard_active_cycle():
    dist = _dist(active_cycle={"outlet": 2, "phase": "watering"})
    members = [_member(1, 1), _member(2, 2)]
    c = _close_host(dist, members, close_time=100.0 + 300, stash_outlet=1)
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_not_awaited()
    assert 0 not in c._dist_observed_open_map()  # popped-and-discarded, never leaked


async def test_close_noop_when_observed_disabled():
    dist = _dist()
    members = [_member(1, 1), _member(2, 2)]
    c = _close_host(
        dist, members, observed=False, close_time=100.0 + 300, stash_outlet=1
    )
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_not_awaited()


async def test_close_noop_without_stash():
    dist = _dist()
    members = [_member(1, 1), _member(2, 2)]
    c = _close_host(dist, members, close_time=100.0 + 300, stash_outlet=None)
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_not_awaited()


async def test_close_skips_disabled_member():
    dist = _dist(skip_pulse_seconds=30)
    members = [
        _member(1, 1),
        _member(2, 2, state=const.ZONE_STATE_DISABLED),
        _member(3, 3),
    ]
    c = _close_host(dist, members, close_time=100.0 + 300, stash_outlet=2)
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_not_awaited()


def _evt(old, new):
    return SimpleNamespace(
        data={
            "old_state": SimpleNamespace(state=old),
            "new_state": SimpleNamespace(state=new),
        }
    )


def _handler_host():
    c = _host()
    c.hass.async_create_task = Mock()
    return c


def test_handler_open_edge_calls_pulse():
    c = _handler_host()
    c._dist_on_inlet_pulse = Mock(return_value="pulse_coro")
    c._dist_on_inlet_close = Mock(return_value="close_coro")
    handler = c._dist_inlet_state_handler(0)
    handler(_evt("off", "on"))
    c.hass.async_create_task.assert_called_once_with("pulse_coro")


def test_handler_close_edge_calls_close():
    c = _handler_host()
    c._dist_on_inlet_pulse = Mock(return_value="pulse_coro")
    c._dist_on_inlet_close = Mock(return_value="close_coro")
    handler = c._dist_inlet_state_handler(0)
    handler(_evt("on", "off"))
    c.hass.async_create_task.assert_called_once_with("close_coro")


def test_handler_ignores_unrelated_transition():
    c = _handler_host()
    handler = c._dist_inlet_state_handler(0)
    handler(_evt("on", "on"))
    c.hass.async_create_task.assert_not_called()


async def test_close_credits_at_exact_threshold():
    # duration == 2*skip (60 s) must credit: the guard is `< threshold`, not `<=`.
    dist = _dist(skip_pulse_seconds=30)
    members = [_member(1, 1), _member(2, 2)]
    c = _close_host(dist, members, close_time=100.0 + 60, stash_outlet=1)
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_awaited_once()


async def test_close_wraps_outlet_index_when_out_of_range():
    # A stashed outlet larger than the current member count wraps via `% n`
    # (member removed between open and close) instead of raising IndexError.
    dist = _dist(skip_pulse_seconds=30)
    members = [_member(1, 1), _member(2, 2), _member(3, 3)]
    c = _close_host(dist, members, close_time=100.0 + 300, stash_outlet=5)
    await c._dist_on_inlet_close(0)
    zone_arg, _ = c._dist_credit_zone.await_args.args
    assert zone_arg[const.ZONE_ID] == 2  # (5-1) % 3 == 1 -> members[1] -> zone id 2


async def test_close_min_skip_pulse_clamp_bites():
    # skip_pulse_seconds below the MIN (10) clamps up, so threshold = 2*10 = 20 s.
    # A 15 s open is below the clamped threshold -> NOT credited (proves the max()
    # is not dead: without the clamp threshold would be 2*5 = 10 and 15 would credit).
    dist = _dist(skip_pulse_seconds=5)
    members = [_member(1, 1), _member(2, 2)]
    c = _close_host(dist, members, close_time=100.0 + 15, stash_outlet=1)
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_not_awaited()


async def test_close_discards_stash_without_timestamp():
    # Defensive (M2): a stash missing "t" must fail safe (discard) rather than
    # treat a missing timestamp as 0 and book a huge spurious duration.
    dist = _dist(skip_pulse_seconds=30)
    members = [_member(1, 1), _member(2, 2)]
    c = _close_host(dist, members, close_time=100.0 + 300, stash_outlet=None)
    c._dist_observed_open_map()[0] = {"outlet": 1}  # no "t"
    await c._dist_on_inlet_close(0)
    c._dist_credit_zone.assert_not_awaited()
