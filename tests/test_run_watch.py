"""The shared hardware-run observation engine (run_watch.py).

Extracted from opensprinkler.py for issue #88, whose batch/queue mode needs the
same lifecycle with a different dispatch and a different watch entity. The 93
tests in test_opensprinkler.py / test_opensprinkler_teardown.py are the oracle
for "that mode still behaves exactly as it did"; this file pins the things those
tests cannot see — that there is now ONE implementation rather than two, and the
policy switches that keep OpenSprinkler on its original timings.
"""

from unittest.mock import Mock

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.opensprinkler import OpenSprinklerMixin
from custom_components.irrigation_plus.run_watch import (
    RunWatchMixin,
    WatchPolicy,
    queue_deadline_seconds,
    watch_policy_for,
)


class TestTheModeDelegatesRatherThanDuplicating:
    """The point of the extraction: one lifecycle, reached by two spellings.

    Without these, someone could re-implement the observation half inside
    OpenSprinklerMixin and every existing test would still pass — which is
    exactly the duplication #88 set out to avoid.
    """

    def test_the_station_watcher_registry_is_the_shared_one(self):
        class _Host(OpenSprinklerMixin, RunWatchMixin):
            pass

        host = _Host()
        registry = host._os_watchers()
        registry["sentinel"] = object()
        assert host._watchers() is registry

    def test_opensprinkler_does_not_carry_its_own_copy_of_the_lifecycle(self):
        """Each ``_os_*`` observation method must be a delegate, not a body.

        A delegate is short by construction; the originals were 20-60 lines. A
        re-implementation would blow past this and fail here.
        """
        import inspect

        for name in (
            "_os_evaluate",
            "_os_observed_start",
            "_os_finish",
            "_os_give_up",
            "_os_arm_timer",
        ):
            body = inspect.getsource(getattr(OpenSprinklerMixin, name))
            # Signature + docstring + one delegating call.
            assert len(body.splitlines()) <= 8, f"{name} looks re-implemented"
            assert "self._watch" in body, f"{name} does not reach the shared engine"


class TestThePolicyKeepsOpenSprinklerOnItsOriginalTimings:
    def test_opensprinkler_acknowledges(self):
        """Its program id is what distinguishes 'queued' from 'silently dropped'."""
        policy = watch_policy_for(const.WATERING_MODE_OPENSPRINKLER)
        assert policy.acknowledges is True
        assert policy.accept_seconds == const.OPENSPRINKLER_ACCEPT_SECONDS

    def test_a_queued_station_waits_the_acceptance_grace_not_the_queue(self):
        """A station with no observed start yet uses the SHORT grace.

        This is a genuine timing choice and is preserved from before the
        extraction: the controller acknowledges a queued run within a poll, so
        the grace only has to absorb a transient communication failure. Once the
        acknowledgement arrives, ``_watch_evaluate`` re-arms to the long
        queue-derived deadline.
        """
        assert (
            watch_policy_for(const.WATERING_MODE_OPENSPRINKLER).queue_deadline_at_start
            is False
        )

    def test_a_station_that_is_already_watering_is_not_given_up_on(self):
        """The one thing here that was a defect rather than a timing choice.

        ``_os_start_watch`` armed the acceptance grace unconditionally, including
        on the resume path — where the run already has an observed start, so
        ``_watch_observed_start`` (the only thing that cancels that timer) never
        runs. Any station with more than the grace left when Home Assistant
        restarted was therefore written off five minutes later while it was
        still watering: settled as a partial, its bucket credit reversed, and a
        station_never_ran fault raised against a zone that was delivering water
        at that moment.

        Reproduced against the pre-extraction code (2026-08-12) and deliberately
        preserved through the #88 extraction so the 93 existing OpenSprinkler
        tests stayed a byte-identical oracle for that refactor. Fixed once that
        work was done. ``test_the_resume_path_does_not_arm_a_give_up_timer``
        below is the behavioural half of this.
        """
        assert (
            watch_policy_for(const.WATERING_MODE_OPENSPRINKLER).arm_give_up_after_start
            is False
        )

    def test_an_unknown_mode_falls_back_to_the_conservative_policy(self):
        """A run persisted under a mode this build no longer knows still has to be
        observed to an end, and waiting for a signal beats assuming it is live."""
        policy = watch_policy_for("a-mode-from-the-future")
        assert policy.acknowledges is True


class TestTheResumePathDoesNotWriteOffAStationThatIsWatering:
    """The behavioural half of the policy assertion above.

    Driven through ``_watch_start`` rather than by reading the policy, because
    the defect was never in the policy — it was that the arming branch did not
    consult the run at all. A test that only pinned a flag would go green against
    an arming branch that ignored it.
    """

    def _host(self, run):
        class _Host(OpenSprinklerMixin, RunWatchMixin):
            def __init__(self):
                self.armed = []
                self.hass = Mock()
                self.hass.states.get = Mock(return_value=None)

            def _watch_arm_timer(self, zone_id, delay, reason):
                self.armed.append((int(zone_id), delay, reason))

            async def _sc_find_run(self, zone_id):
                return run

            async def _sc_active_runs(self):
                return [run] if run else []

        host = _Host()
        # The subscription and the dispatcher are HA plumbing, not the subject.
        host._watch_cancel = Mock()
        host._watchers = Mock(return_value={})
        return host

    async def _arm(self, monkeypatch, run):
        monkeypatch.setattr(
            "custom_components.irrigation_plus.run_watch."
            "async_track_state_change_event",
            Mock(return_value=Mock()),
        )
        monkeypatch.setattr(
            "custom_components.irrigation_plus.run_watch.async_dispatcher_send", Mock()
        )
        host = self._host(run)
        # _watchers is stubbed, so the trailing evaluation finds no watcher and
        # returns immediately — the arming decision is all this exercises.
        await host._watch_start(1, "binary_sensor.s", 3600, accepted=True)
        return host

    async def test_a_resumed_station_still_watering_is_left_alone(self, monkeypatch):
        """An hour-long run restarted into must not be written off in five minutes."""
        run = {
            const.RUN_ZONE_ID: 1,
            const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER,
            const.RUN_PLANNED_SECONDS: 3600,
            const.RUN_STARTED: "2026-08-17T09:00:00+00:00",
            const.RUN_OBSERVED_START: "2026-08-17T09:00:05+00:00",
        }
        host = await self._arm(monkeypatch, run)
        assert host.armed == [], (
            "a give-up timer was armed for a station that is already watering; "
            f"nothing cancels it, so the run dies in {host.armed[0][1]}s"
        )

    async def test_a_station_still_waiting_its_turn_keeps_its_grace(self, monkeypatch):
        """The counterfactual: the acceptance grace is untouched for a queued run."""
        run = {
            const.RUN_ZONE_ID: 1,
            const.RUN_MODE: const.WATERING_MODE_OPENSPRINKLER,
            const.RUN_PLANNED_SECONDS: 3600,
            const.RUN_STARTED: "2026-08-17T09:00:00+00:00",
        }
        host = await self._arm(monkeypatch, run)
        assert host.armed == [
            (1, const.OPENSPRINKLER_ACCEPT_SECONDS, const.PROBLEM_STATION_NEVER_RAN)
        ]


class TestTheGiveUpDeadlineCountsTheRightRunsAhead:
    @staticmethod
    def _run(zone_id, seconds, mode=const.WATERING_MODE_OPENSPRINKLER):
        return {
            const.RUN_ZONE_ID: zone_id,
            const.RUN_PLANNED_SECONDS: seconds,
            const.RUN_MODE: mode,
        }

    def _base(self, planned):
        return (
            const.OPENSPRINKLER_ACCEPT_SECONDS
            + planned
            + const.OPENSPRINKLER_QUEUE_MARGIN_SECONDS
        )

    def test_a_lone_run_waits_only_for_itself(self):
        run = self._run(1, 600)
        assert queue_deadline_seconds([run], run) == self._base(600)

    def test_the_zones_queued_ahead_extend_it(self):
        run = self._run(1, 600)
        others = [self._run(2, 300), self._run(3, 900)]
        assert queue_deadline_seconds([run, *others], run) == self._base(600) + 1200

    def test_a_run_on_a_different_controller_does_not_extend_it(self):
        """The zones ahead of this one are the ones sharing its queue.

        Before the extraction the mode was hardcoded to OpenSprinkler, so a batch
        run would have counted stations on a completely separate controller.
        """
        run = self._run(1, 600)
        other = self._run(2, 9999, mode=const.WATERING_MODE_SERVICE)
        assert queue_deadline_seconds([run, other], run) == self._base(600)

    def test_the_mode_can_be_named_explicitly(self):
        run = self._run(1, 600, mode=const.WATERING_MODE_SERVICE)
        ahead = self._run(2, 300, mode=const.WATERING_MODE_SERVICE)
        assert queue_deadline_seconds(
            [run, ahead], run, mode=const.WATERING_MODE_SERVICE
        ) == (self._base(600) + 300)

    def test_junk_in_the_run_list_cannot_raise(self):
        """The list comes off disk and is walked on every observation."""
        run = self._run(1, 600)
        assert queue_deadline_seconds(
            [run, None, "nonsense", {const.RUN_PLANNED_SECONDS: "abc"}], run
        ) == self._base(600)


class TestAPolicyIsSelfDescribing:
    def test_a_non_acknowledging_mode_must_arm_the_queue_deadline_at_once(self):
        """There is no second signal to re-arm on, so the first timer is the only
        backstop and must cover the zones queued ahead."""
        policy = WatchPolicy(
            mode="batch", acknowledges=False, queue_deadline_at_start=True
        )
        assert policy.acknowledges is False
        assert policy.queue_deadline_at_start is True
