"""Re-arming a schedule must not disarm it.

``_reregister_tracker`` cancelled the existing tracker and only then asked
``_setup_schedule_tracker`` for a replacement. That call can decline to arm and
return normally -- an end whose bound no longer resolves, a recurrence the
governing-end builder has no native tracker for -- and it can raise. Either way
the slot was left empty with the old handle already cancelled, so a schedule
that had been firing simply stopped, until the next config write rebuilt every
tracker or the integration reloaded. The only trace was a warning.

The window is not a startup-only one: ``_reregister_tracker`` is what the
self-rescheduling finish/azimuth trackers and the duration-change re-arm call,
so it runs repeatedly during normal operation on the schedules with the most
moving parts.

These tests drive the real ``_setup_schedule_tracker`` rather than stubbing it,
so the "unarmable" cases are ones a stored schedule can actually reach.
"""

import datetime
import threading
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation import scheduler as scheduler_module
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager


def _manager():
    coordinator = create_autospec(SmartIrrigationCoordinator, instance=True)
    manager = RecurringScheduleManager(MagicMock(), coordinator)
    manager.coordinator = MagicMock()
    manager.coordinator.store.async_get_config = AsyncMock(return_value={})
    manager._persist_fired_occurrences = AsyncMock()
    return manager


def _daily(**kw):
    """A daily schedule anchored on a clock-time Start -- the plainest thing
    that arms, via ``async_track_time_change``."""
    s = {
        const.SCHEDULE_CONF_ID: "s1",
        const.SCHEDULE_CONF_NAME: "morning",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_ENABLED: True,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_START_TIME: "06:00",
        const.SCHEDULE_CONF_ZONES: "all",
    }
    s.update(kw)
    return s


def _unbounded(**kw):
    """Neither end bounded: ``_bounded_ends`` returns ``(None, None)`` and
    ``_setup_schedule_tracker`` warns and returns without arming."""
    return _daily(
        **{
            const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_NONE,
            const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_NONE,
            **kw,
        }
    )


class _Handle:
    """Stands in for a tracker's unsubscribe callable, and records the cancel."""

    def __init__(self):
        self.cancelled = False

    def __call__(self):
        self.cancelled = True


class TestAnUnarmableRebuildKeepsTheOldTracker:
    @pytest.mark.asyncio
    async def test_an_unbounded_schedule_keeps_its_existing_tracker(self):
        manager = _manager()
        armed = _Handle()
        manager._schedule_trackers["s1"] = armed

        await manager._reregister_tracker(_unbounded())

        assert manager._schedule_trackers["s1"] is armed
        assert not armed.cancelled

    @pytest.mark.asyncio
    async def test_a_bound_that_stops_resolving_keeps_its_existing_tracker(self):
        """The reachable-without-a-corrupt-store case: the governing end is
        bounded but no longer resolves, so the builder returns ``None``."""
        manager = _manager()
        armed = _Handle()
        manager._schedule_trackers["s1"] = armed

        await manager._reregister_tracker(
            _daily(**{const.SCHEDULE_CONF_START_TIME: "not a time"})
        )

        assert manager._schedule_trackers["s1"] is armed
        assert not armed.cancelled

    @pytest.mark.asyncio
    async def test_a_raising_rebuild_keeps_its_existing_tracker(self):
        """The exception path leaves the schedule armed too, and still
        propagates so the caller is not told the re-arm succeeded."""
        manager = _manager()
        armed = _Handle()
        manager._schedule_trackers["s1"] = armed
        boom = RuntimeError("resolver blew up")
        manager._setup_schedule_tracker = AsyncMock(side_effect=boom)

        with pytest.raises(RuntimeError):
            await manager._reregister_tracker(_daily())

        assert manager._schedule_trackers["s1"] is armed
        assert not armed.cancelled

    @pytest.mark.asyncio
    async def test_nothing_armed_and_nothing_rebuilt_leaves_nothing_armed(self):
        """The guard restores what was there, which for a schedule that never
        armed is still nothing."""
        manager = _manager()

        await manager._reregister_tracker(_unbounded())

        assert not manager._schedule_trackers.get("s1")


class TestAnOrdinaryRearmStillSwaps:
    @pytest.mark.asyncio
    async def test_a_successful_rebuild_replaces_and_cancels_the_old_tracker(self):
        """The guard must not turn the ordinary re-arm into a no-op: this is
        the path every finish/azimuth reschedule takes."""
        manager = _manager()
        stale = _Handle()
        manager._schedule_trackers["s1"] = stale

        await manager._reregister_tracker(_daily())

        replacement = manager._schedule_trackers["s1"]
        assert replacement is not None
        assert replacement is not stale
        assert stale.cancelled

    @pytest.mark.asyncio
    async def test_a_first_arm_with_no_predecessor_still_stores_the_tracker(self):
        manager = _manager()

        await manager._reregister_tracker(_daily())

        assert manager._schedule_trackers["s1"] is not None


class TestADisabledScheduleIsStillDisarmed:
    """``_setup_schedule_tracker`` returns early for a disabled schedule. That
    is the intended outcome, not a failed rebuild, so the keep-the-old-handle
    guard must not resurrect a tracker the user has just switched off."""

    @pytest.mark.asyncio
    async def test_disabling_a_schedule_cancels_and_clears_its_tracker(self):
        manager = _manager()
        armed = _Handle()
        manager._schedule_trackers["s1"] = armed

        await manager._reregister_tracker(
            _daily(**{const.SCHEDULE_CONF_ENABLED: False})
        )

        assert not manager._schedule_trackers.get("s1")
        assert armed.cancelled

    @pytest.mark.asyncio
    async def test_a_disabled_schedule_with_no_tracker_stays_unarmed(self):
        manager = _manager()

        await manager._reregister_tracker(
            _daily(**{const.SCHEDULE_CONF_ENABLED: False})
        )

        assert not manager._schedule_trackers.get("s1")


class TestTheTrackerKeptIsTheOneTheManagerArmed:
    """The assertions above plant a handle in the slot, so on their own they
    would pass against a fix that only preserved a dict entry. Here the handle
    is the object the real arm path produced, and the same object has to still
    be in the slot afterwards -- uncancelled, so HA is still holding it.
    """

    @pytest.mark.asyncio
    async def test_the_real_armed_handle_survives_an_unarmable_rearm(self, monkeypatch):
        manager = _manager()
        handles = []

        def _track(hass, action, **kw):
            handle = _Handle()
            handles.append(handle)
            return handle

        monkeypatch.setattr(scheduler_module, "async_track_time_change", _track)

        schedule = _daily()
        await manager._setup_schedule_tracker(schedule)
        assert len(handles) == 1
        armed = handles[0]
        assert manager._schedule_trackers["s1"] is armed

        # The stored bound stops resolving, and the self-reschedule runs.
        schedule[const.SCHEDULE_CONF_START_TIME] = "not a time"
        await manager._reregister_tracker(schedule)

        assert handles == [armed], "the rebuild must not have armed anything"
        assert manager._schedule_trackers["s1"] is armed
        assert not armed.cancelled


class TestTheKeptTrackerStillFires:
    """Every other test here reads the tracker slot, which is the same dict the
    implementation writes. This one asks Home Assistant instead: it arms a real
    ``async_track_time_change``, puts an unarmable re-arm through it, advances
    the clock to the schedule's own time, and asserts the schedule executes. A
    fix that kept a handle Home Assistant had already forgotten would fail here
    and pass everywhere else.

    Two things make this awkward to write, and both are properties of the
    scheduler rather than of the test:

    ``_setup_governing_tracker`` tracks a plain lambda, so Home Assistant types
    the job ``HassJobType.Executor`` and runs the action in a worker thread.
    ``async_block_till_done`` does not join that thread -- the assertion runs
    first and the list is still empty -- which is why the action signals a
    ``threading.Event`` and the test waits on it. Anything else asserting that a
    schedule fired needs the same wait.

    The time-change listener re-checks the clock when it runs and reschedules if
    the instant has not arrived, so ``async_fire_time_changed`` alone does
    nothing: the frozen clock has to be moved to the target as well.
    """

    @pytest.mark.asyncio
    async def test_a_schedule_survives_an_unarmable_rearm_and_still_executes(
        self, hass, freezer
    ):
        start = datetime.datetime(2026, 9, 1, 12, 0, tzinfo=datetime.timezone.utc)
        freezer.move_to(start)

        coordinator = create_autospec(SmartIrrigationCoordinator, instance=True)
        manager = RecurringScheduleManager(hass, coordinator)
        manager._persist_fired_occurrences = AsyncMock()

        target = start + datetime.timedelta(minutes=2)
        local = dt_util.as_local(target)
        schedule = _daily(
            **{const.SCHEDULE_CONF_START_TIME: f"{local.hour:02d}:{local.minute:02d}"}
        )

        fired = []
        executed = threading.Event()

        def _record(s, now, **kw):
            fired.append(now)
            executed.set()

        manager._execute_schedule = _record

        await manager._setup_schedule_tracker(schedule)
        assert manager._schedule_trackers["s1"] is not None

        # The stored bound stops resolving, and a self-reschedule runs. This is
        # the call that used to disarm the schedule for good.
        schedule[const.SCHEDULE_CONF_START_TIME] = "not a time"
        await manager._reregister_tracker(schedule)

        due = target + datetime.timedelta(seconds=1)
        freezer.move_to(due)
        async_fire_time_changed(hass, due)
        await hass.async_block_till_done()
        assert await hass.async_add_executor_job(
            executed.wait, 5
        ), "the schedule did not execute at its own time after the re-arm"
        assert len(fired) == 1

        await manager.async_unload()
