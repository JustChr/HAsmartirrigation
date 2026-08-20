"""The automatic-calculation mode and the ledger-staleness floor.

The staleness check reads ``last_calculated`` straight off
``store.async_get_zones``, which returns ``attr.asdict`` of an entry hydrated
from JSON — so the stamps are ISO **strings**, not datetimes. Every fixture here
passes strings for that reason: treating them as datetimes raises inside a
midnight callback, where the exception is swallowed as an unretrieved task and
the guard silently never runs.
"""

import datetime
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.auto_calc import AutoCalcMixin


class _Host(AutoCalcMixin):
    def __init__(self, zones=None, mode=const.CONF_AUTO_CALC_MODE_BEFORE_RUN, enabled=True):
        self.store = Mock()
        self.store.config = Mock(autocalcmode=mode, autocalcenabled=enabled)
        self.store.async_get_zones = AsyncMock(return_value=zones or [])
        self._async_calculate_all = AsyncMock()
        self.async_update_zone_config = AsyncMock()


def _zone(zid, last_calculated, state=const.ZONE_STATE_AUTOMATIC):
    """A stored zone. ``state`` defaults to automatic because ZoneEntry.state
    does: a real zone always carries one, and the guard only considers the
    zones a calculation can actually advance."""
    return {
        const.ZONE_ID: zid,
        const.ZONE_LAST_CALCULATED: last_calculated,
        const.ZONE_STATE: state,
    }


def _ago(hours):
    """A stored stamp ``hours`` old, in the store's own format: a naive local ISO string."""
    return (dt_util.now().replace(tzinfo=None) - datetime.timedelta(hours=hours)).isoformat()


class TestReArmGating:
    """Which config payloads re-arm the fixed-time tracker.

    All three keys have to, and merged supplies the two a payload omits. The
    panel sends each of them alone: the time field on its own, the switch on
    its own, the mode selector on its own.
    """

    @staticmethod
    def _touches_auto_calc(data):
        """The condition in _config_updated, isolated from the coordinator."""
        return (
            const.CONF_AUTO_CALC_ENABLED in data
            or const.CONF_AUTO_CALC_MODE in data
            or const.CONF_CALC_TIME in data
        )

    def test_editing_only_the_time_re_arms(self):
        # The standing bug: this stored the new time and left the tracker on
        # the old one until a restart.
        assert self._touches_auto_calc({const.CONF_CALC_TIME: "04:00"})

    def test_editing_only_the_mode_re_arms(self):
        assert self._touches_auto_calc(
            {const.CONF_AUTO_CALC_MODE: const.CONF_AUTO_CALC_MODE_BEFORE_RUN}
        )

    def test_editing_only_the_switch_re_arms(self):
        assert self._touches_auto_calc({const.CONF_AUTO_CALC_ENABLED: False})

    def test_an_unrelated_save_does_not_re_arm(self):
        # A partial save from another tab must not disturb an armed tracker.
        assert not self._touches_auto_calc({"sensor_debounce": 30})


class TestLedgerStaleness:
    async def test_a_stale_string_stamp_triggers_a_calculation(self):
        # The regression: these arrive as strings. Calling .replace(tzinfo=...)
        # on one raises TypeError, the midnight task dies unretrieved, and the
        # ledger is left to rot until the replay window outruns the buffer.
        host = _Host([_zone(0, _ago(2)), _zone(1, _ago(30))])
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_awaited_once()

    async def test_a_disabled_zone_does_not_latch_the_guard(self):
        """A stale stamp on a zone the commit skips must not trigger one.

        _async_calculate_all only touches automatic zones, so a disabled zone's
        stamp never advances. Counting it as stale would fire the guard every
        midnight forever, turning the before-run mode into a midnight mode and
        leaving the guard unable to tell a rotting ledger from a parked zone.
        """
        host = _Host(
            [
                _zone(0, _ago(1)),
                _zone(1, None, state=const.ZONE_STATE_DISABLED),
            ]
        )
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_not_awaited()

    async def test_a_manual_zone_does_not_latch_the_guard(self):
        host = _Host(
            [
                _zone(0, _ago(1)),
                _zone(1, _ago(500), state=const.ZONE_STATE_MANUAL),
            ]
        )
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_not_awaited()

    async def test_a_stale_automatic_zone_still_triggers_one(self):
        """The filter must not swallow the case the guard exists for."""
        host = _Host(
            [
                _zone(0, _ago(1)),
                _zone(1, _ago(500)),
                _zone(2, None, state=const.ZONE_STATE_DISABLED),
            ]
        )
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_awaited_once()

    async def test_a_fresh_ledger_is_left_alone(self):
        host = _Host([_zone(0, _ago(1)), _zone(1, _ago(3))])
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_not_awaited()

    async def test_a_never_calculated_zone_counts_as_stale(self):
        host = _Host([_zone(0, None)])
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_awaited_once()

    async def test_an_unparseable_stamp_counts_as_stale(self):
        # Erring towards a needless calculation is harmless; erring the other
        # way is what silently freezes the ledger.
        host = _Host([_zone(0, "not a datetime")])
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_awaited_once()

    async def test_a_real_datetime_stamp_still_works(self):
        host = _Host([_zone(0, dt_util.now().replace(tzinfo=None) - datetime.timedelta(hours=30))])
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_awaited_once()

    async def test_the_fixed_time_mode_never_commits(self):
        host = _Host(
            [_zone(0, _ago(300))], mode=const.CONF_AUTO_CALC_MODE_FIXED_TIME
        )
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_not_awaited()

    async def test_disabled_auto_calc_never_commits(self):
        host = _Host([_zone(0, _ago(300))], enabled=False)
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_not_awaited()


class TestPreRunCommit:
    async def test_before_run_mode_calculates_every_zone(self):
        host = _Host()
        await host.async_commit_pre_run_calculation("all")
        host._async_calculate_all.assert_awaited_once()

    async def test_a_targeted_run_calculates_only_its_zones(self):
        host = _Host()
        await host.async_commit_pre_run_calculation([1, 2])
        assert host.async_update_zone_config.await_count == 2
        host._async_calculate_all.assert_not_awaited()

    async def test_the_fixed_time_mode_is_a_no_op(self):
        # calctime keeps its original meaning, so a run must not commit.
        host = _Host(mode=const.CONF_AUTO_CALC_MODE_FIXED_TIME)
        await host.async_commit_pre_run_calculation("all")
        host._async_calculate_all.assert_not_awaited()
        host.async_update_zone_config.assert_not_awaited()
