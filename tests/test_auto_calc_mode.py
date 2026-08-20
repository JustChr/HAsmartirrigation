"""The automatic-calculation mode and the ledger-staleness floor.

The staleness check reads ``last_calculated`` straight off
``store.async_get_zones``, which returns ``attr.asdict`` of an entry hydrated
from JSON — so the stamps are ISO **strings**, not datetimes. Every fixture here
passes strings for that reason: treating them as datetimes raises inside a
midnight callback, where the exception is swallowed as an unretrieved task and
the guard silently never runs.
"""

import datetime
from unittest.mock import AsyncMock, Mock, patch

import homeassistant.util.dt as dt_util

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.auto_calc import AutoCalcMixin


class _Host(AutoCalcMixin):
    def __init__(
        self, zones=None, mode=const.CONF_AUTO_CALC_MODE_BEFORE_RUN, enabled=True
    ):
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
    return (
        dt_util.now().replace(tzinfo=None) - datetime.timedelta(hours=hours)
    ).isoformat()


class TestFixedTimeReArm:
    """set_up_auto_calc_time against a calctime nothing validates on the way in.

    The panel's time field is free text and the config endpoint accepts it as
    cv.string, so a typo reaches the store intact. Before calctime joined the
    re-arm gate, a save carrying only the time never reached this function and
    the armed tracker kept running; now it does reach it, so tearing the working
    schedule down before knowing the replacement is usable would leave NO
    calculation armed, traced only by a warning.
    """

    @staticmethod
    def _host(armed=True, mode=const.CONF_AUTO_CALC_MODE_FIXED_TIME):
        host = Mock()
        host._track_auto_calc_time_unsub = Mock() if armed else None
        host.store = Mock()
        host.store.config = Mock(autocalcmode=mode)
        # The disable branch persists through the store before returning.
        host.store.async_update_config = AsyncMock()
        host.hass = Mock()
        host._WeatherServiceClient = None
        return host

    @staticmethod
    async def _run(host, data):
        with patch(
            "custom_components.smart_irrigation.async_track_time_change"
        ) as track:
            await SmartIrrigationCoordinator.set_up_auto_calc_time(host, data)
        return track

    async def test_a_malformed_time_keeps_the_previous_schedule(self):
        host = self._host()
        previous = host._track_auto_calc_time_unsub
        await self._run(
            host,
            {
                const.CONF_AUTO_CALC_ENABLED: True,
                const.CONF_CALC_TIME: "not a time",
            },
        )
        previous.assert_not_called()
        assert host._track_auto_calc_time_unsub is previous

    async def test_a_valid_time_still_replaces_the_schedule(self):
        # The guard must not block the ordinary case it sits in front of.
        host = self._host()
        previous = host._track_auto_calc_time_unsub
        track = await self._run(
            host,
            {const.CONF_AUTO_CALC_ENABLED: True, const.CONF_CALC_TIME: "04:37"},
        )
        previous.assert_called_once()
        track.assert_called_once()
        assert host._track_auto_calc_time_unsub is track.return_value

    async def test_switching_to_before_run_is_not_blocked_by_a_bad_stored_time(self):
        """The mode switch must not be held hostage by an unrelated bad value.

        before_run does not read calctime at all, so validating it here would
        strand an install that has a typo stored: it could never leave the
        fixed-time mode to escape it.
        """
        host = self._host()
        previous = host._track_auto_calc_time_unsub
        await self._run(
            host,
            {
                const.CONF_AUTO_CALC_ENABLED: True,
                const.CONF_AUTO_CALC_MODE: const.CONF_AUTO_CALC_MODE_BEFORE_RUN,
                const.CONF_CALC_TIME: "not a time",
            },
        )
        previous.assert_called_once()
        assert host._track_auto_calc_time_unsub is None

    async def test_disabling_is_not_blocked_by_a_bad_stored_time(self):
        host = self._host()
        previous = host._track_auto_calc_time_unsub
        await self._run(
            host,
            {
                const.CONF_AUTO_CALC_ENABLED: False,
                const.CONF_CALC_TIME: "not a time",
            },
        )
        previous.assert_called_once()
        assert host._track_auto_calc_time_unsub is None


class TestReArmGating:
    """Which config payloads re-arm the fixed-time tracker.

    Driven through async_update_config rather than by restating its condition,
    because a test that re-implements the check it is guarding passes happily
    while the real one is deleted. This is that test rewritten after a mutation
    of the real condition survived the whole suite.
    """

    @staticmethod
    def _host():
        host = Mock()
        host.store = Mock()
        host.store.async_update_config = AsyncMock()
        host.store.config = Mock(
            autocalcenabled=True,
            autocalcmode=const.CONF_AUTO_CALC_MODE_FIXED_TIME,
            calctime="02:00",
        )
        host.set_up_auto_calc_time = AsyncMock()
        host.set_up_auto_update_time = AsyncMock()
        host.hass = Mock()
        return host

    @classmethod
    async def _save(cls, data):
        host = cls._host()
        with patch("custom_components.smart_irrigation.async_dispatcher_send"):
            await SmartIrrigationCoordinator.async_update_config(host, data)
        return host

    async def test_editing_only_the_time_re_arms(self):
        # The standing bug: this stored the new time and left the tracker armed
        # on the old one until a restart.
        host = await self._save({const.CONF_CALC_TIME: "04:00"})
        host.set_up_auto_calc_time.assert_awaited_once()

    async def test_editing_only_the_mode_re_arms(self):
        host = await self._save(
            {const.CONF_AUTO_CALC_MODE: const.CONF_AUTO_CALC_MODE_BEFORE_RUN}
        )
        host.set_up_auto_calc_time.assert_awaited_once()

    async def test_editing_only_the_switch_re_arms(self):
        host = await self._save({const.CONF_AUTO_CALC_ENABLED: False})
        host.set_up_auto_calc_time.assert_awaited_once()

    async def test_an_unrelated_save_does_not_re_arm(self):
        # A partial save from another tab must not disturb an armed tracker.
        host = await self._save({const.CONF_SENSOR_DEBOUNCE: 30})
        host.set_up_auto_calc_time.assert_not_awaited()

    async def test_the_merged_payload_carries_all_three_keys(self):
        """Whichever key the payload omits is supplied from the stored config.

        Without this, set_up_auto_calc_time reads data[CONF_AUTO_CALC_ENABLED]
        on a payload that never carried it.
        """
        host = await self._save({const.CONF_CALC_TIME: "04:00"})
        merged = host.set_up_auto_calc_time.await_args.args[0]
        assert merged[const.CONF_CALC_TIME] == "04:00"
        assert merged[const.CONF_AUTO_CALC_ENABLED] is True


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
        host = _Host(
            [
                _zone(
                    0, dt_util.now().replace(tzinfo=None) - datetime.timedelta(hours=30)
                )
            ]
        )
        await host.async_guard_ledger_staleness()
        host._async_calculate_all.assert_awaited_once()

    async def test_the_fixed_time_mode_never_commits(self):
        host = _Host([_zone(0, _ago(300))], mode=const.CONF_AUTO_CALC_MODE_FIXED_TIME)
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


class TestTheScheduleActuallyCommitsBeforeItRuns:
    """The wiring, not the helper.

    ``async_commit_pre_run_calculation`` is exercised directly above, but
    nothing asserted that a scheduled irrigation calls it — which is the
    feature's only production call site. Deleting that line left the whole
    suite green, so it is pinned here, and pinned BEFORE the skip-conditions
    check: the point of the mode is that the deficit deciding the run is
    minutes old rather than hours, and a commit after the veto is evaluated
    would be too late to affect it.
    """

    @staticmethod
    def _manager(hass, skip=False):
        from custom_components.smart_irrigation.scheduler import (
            RecurringScheduleManager,
        )

        mgr = RecurringScheduleManager(hass, Mock())
        calls = []
        mgr.coordinator.async_commit_pre_run_calculation = AsyncMock(
            side_effect=lambda *a, **k: calls.append("commit")
        )
        mgr.coordinator._check_skip_conditions = AsyncMock(
            side_effect=lambda *a, **k: calls.append("skip_check") or skip
        )
        mgr.coordinator._last_skip_evaluation = {"checks": []}
        mgr.coordinator._record_skipped_run = AsyncMock()
        mgr.coordinator._irrigate_linked_entities = AsyncMock(return_value=True)
        mgr.coordinator._dispatch_distributor_cycles = AsyncMock(return_value=False)
        mgr.coordinator._reset_days_since_irrigation = AsyncMock()
        return mgr, calls

    async def test_a_scheduled_run_commits_a_calculation_first(self, hass):
        mgr, calls = self._manager(hass)
        await mgr._perform_scheduled_irrigation("all", "Morning")
        mgr.coordinator.async_commit_pre_run_calculation.assert_awaited_once_with("all")
        assert calls[:2] == ["commit", "skip_check"]

    async def test_the_commit_happens_even_when_the_run_is_vetoed(self, hass):
        # The bucket is still worth updating on a skipped run: the veto is a
        # decision about watering, not a reason to leave the ledger stale.
        mgr, calls = self._manager(hass, skip=True)
        await mgr._perform_scheduled_irrigation([1, 2], "Morning")
        mgr.coordinator.async_commit_pre_run_calculation.assert_awaited_once_with(
            [1, 2]
        )
        mgr.coordinator._irrigate_linked_entities.assert_not_awaited()
