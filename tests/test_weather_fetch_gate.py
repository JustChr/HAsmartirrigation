"""The fetch gate the four weather clients share: freshness, single flight, pause."""

import contextlib
import datetime
import gc
import logging
import threading
import time
import weakref
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
import requests
from freezegun import freeze_time

from custom_components.irrigation_plus.weathermodules import fetch_gate
from custom_components.irrigation_plus.weathermodules.fetch_gate import (
    cache_lifetime,
    is_fresh,
    retry_after_seconds,
)


def test_cache_lifetime_has_a_floor_of_sixty_seconds():
    assert cache_lifetime(0) == 60
    assert cache_lifetime(59) == 60
    assert cache_lifetime(599) == 599


@freeze_time("2026-10-23 12:00:00")
def test_is_fresh_matches_the_clients_old_rule():
    now = datetime.datetime.now()
    assert is_fresh(None, 599, False) is False
    assert is_fresh(now, 599, True) is False  # override_cache
    assert is_fresh(now - timedelta(seconds=598), 599, False) is True
    assert is_fresh(now - timedelta(seconds=599), 599, False) is False
    assert is_fresh(now - timedelta(seconds=59), 0, False) is True  # floor


class _Owner:
    """What a gate needs from a client: the cache settings, a stamp, a fetch point."""

    def __init__(self):
        self.cache_seconds = 600
        self.override_cache = False
        self.stamp = None
        self.cached = None
        self.calls = 0  # requests that actually went out
        self.delay = 0.2  # how long ``fetch_ok`` takes
        self.error = lambda: ValueError("boom")  # what ``fetch_raise`` raises

    def _serve_cached(self):
        return fetch_gate.is_fresh(self.stamp, self.cache_seconds, self.override_cache)

    def fetch_ok(self):
        """Serve the cache while fresh, else make one slow request and keep it."""
        if self._serve_cached():
            return self.cached
        self.calls += 1
        time.sleep(self.delay)  # long enough for the other thread to arrive meanwhile
        self.cached = "document"
        self.stamp = datetime.datetime.now()
        return self.cached

    def fetch_none(self):
        """Like ``fetch_ok``, but the request yields nothing and nothing is kept."""
        if self._serve_cached():
            return self.cached
        self.calls += 1
        return None

    def fetch_raise(self):
        """Like ``fetch_ok``, but the request fails and nothing is kept."""
        if self._serve_cached():
            return self.cached
        self.calls += 1
        raise self.error()


def _in_threads(*calls):
    """Run each call in its own thread; return what each one returned or raised."""
    results = [None] * len(calls)

    def worker(index, call):
        try:
            results[index] = call()
        except Exception as ex:
            results[index] = ex

    # daemon: a call that never returns must fail the test, not hang the run
    threads = [
        threading.Thread(target=worker, args=(index, call), daemon=True)
        for index, call in enumerate(calls)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    assert not any(thread.is_alive() for thread in threads)
    return results


def test_run_serialises_two_threads_onto_one_fetch():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    results = _in_threads(
        lambda: gate.run(owner.fetch_ok), lambda: gate.run(owner.fetch_ok)
    )
    assert owner.calls == 1
    assert results == ["document", "document"]


def test_run_hands_back_what_the_fetch_returned():
    # One gate each: after a failed fetch a gate pauses, and this is not about that.
    owner = _Owner()
    assert fetch_gate.FetchGate(owner, "stamp").run(owner.fetch_none) is None
    assert fetch_gate.FetchGate(owner, "stamp").run(owner.fetch_ok) == "document"


def test_run_lets_an_exception_through_and_lets_the_next_caller_in():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    with pytest.raises(ValueError, match="boom"):
        gate.run(owner.fetch_raise)
    owner.override_cache = True  # the pause after the failure is not what this is about
    # A lock left held by the failed run would hang this call.
    assert _in_threads(lambda: gate.run(owner.fetch_ok)) == ["document"]


def test_two_gates_do_not_wait_for_each_other():
    owner = _Owner()
    first = fetch_gate.FetchGate(owner, "stamp")
    second = fetch_gate.FetchGate(owner, "stamp")
    inside = threading.Event()
    release = threading.Event()

    def hold():
        inside.set()
        release.wait(timeout=5)
        return "held"

    holder = threading.Thread(target=lambda: first.run(hold))
    holder.start()
    try:
        assert inside.wait(timeout=5)
        assert _in_threads(lambda: second.run(lambda: "free")) == ["free"]
    finally:
        release.set()
        holder.join(timeout=5)
    assert not holder.is_alive()


def _gaps(gate, owner, fetch, frozen, wanted):
    """Seconds between the real requests when a caller asks once a second."""
    moments = []
    for second in range(5000):
        before = owner.calls
        gate.run(fetch)
        if owner.calls > before:
            moments.append(second)
            if len(moments) == wanted:
                break
        frozen.tick(1)
    assert len(moments) == wanted
    return [
        later - earlier for earlier, later in zip(moments, moments[1:], strict=False)
    ]


def test_a_failure_is_replayed_without_a_fetch_during_the_pause():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        assert gate.run(owner.fetch_none) is None
        assert owner.calls == 1
        frozen.tick(59)
        assert gate.run(owner.fetch_none) is None
        assert owner.calls == 1
        frozen.tick(2)
        assert gate.run(owner.fetch_none) is None
        assert owner.calls == 2


def test_a_raised_failure_is_replayed_with_its_type_and_message():
    owner = _Owner()
    owner.error = lambda: OSError("down")
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        with pytest.raises(OSError, match="down") as real:
            gate.run(owner.fetch_raise)
        frozen.tick(30)
        with pytest.raises(OSError, match="down") as replayed:
            gate.run(owner.fetch_raise)
        with pytest.raises(OSError, match="down") as replayed_again:
            gate.run(owner.fetch_raise)
    assert owner.calls == 1
    assert fetch_gate.is_replay(replayed.value)
    assert not fetch_gate.is_replay(real.value)  # the real failure is not marked
    assert replayed.value is not real.value
    assert replayed_again.value is not replayed.value  # no traceback piling up


class _Picky(Exception):
    """An exception ``copy.copy`` cannot copy: its constructor wants a keyword."""

    def __init__(self, text, *, code):
        super().__init__(text)
        self.code = code


class _SelfCopy(Exception):
    """An exception whose ``__copy__`` hands back the instance itself."""

    code = 7

    def __copy__(self):
        return self


@pytest.mark.parametrize(
    "error",
    [lambda: _Picky("odd", code=7), lambda: _SelfCopy("odd")],
    ids=["constructor_refuses_a_copy", "copy_is_the_instance_itself"],
)
def test_an_exception_that_cannot_be_copied_is_raised_again_unmarked(error):
    owner = _Owner()
    owner.error = error
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        with pytest.raises((_Picky, _SelfCopy), match="odd") as real:
            gate.run(owner.fetch_raise)
        frozen.tick(30)
        with pytest.raises((_Picky, _SelfCopy), match="odd") as replayed:
            gate.run(owner.fetch_raise)
    assert owner.calls == 1  # replayed, not asked again
    # Fail loud: there is nothing to copy, so the stored instance itself comes
    # back, and it is not marked, so the accessor logs it at ERROR. A real
    # failure is never silenced; the worst case is one more ERROR line. The
    # instance is the first caller's: marking it would have that caller's
    # accessor log a real failure at DEBUG.
    assert type(replayed.value) is type(real.value)
    assert replayed.value is real.value
    assert not fetch_gate.is_replay(real.value)
    assert not fetch_gate.is_replay(replayed.value)
    assert replayed.value.code == 7


def test_a_failure_keeps_no_traceback_alive_after_its_caller_is_done():
    # The outcome kept for the pause is a copy without traceback. The original
    # exception carries its traceback, and that holds every frame of the failed
    # fetch and the locals in them (a response body, a parsed document) until
    # the next fetch.
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    sentinels = []

    class _Local:
        """Stands for what a failed fetch leaves in its frame."""

    def fetch():
        local = _Local()
        sentinels.append(weakref.ref(local))
        raise ValueError("boom")

    with freeze_time("2026-10-23 12:00:00") as frozen:
        with contextlib.suppress(ValueError):
            gate.run(fetch)
        gc.collect()
        assert sentinels[0]() is None
        frozen.tick(30)
        with pytest.raises(ValueError, match="boom"):  # still replayed
            gate.run(fetch)
    assert len(sentinels) == 1


def test_a_fresh_entry_is_served_even_during_a_pause():
    # Freshness comes before the pause. Lengthening the update interval during
    # an outage raises ``cache_seconds`` (__init__.py, ``track_update_time``; it
    # changes only when the user edits the update settings), which brings an old
    # stamp back into the window; the entry is fresh again and is served, not
    # replaced by the replay of the failure that began the pause.
    owner = _Owner()
    owner.cache_seconds = 600
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00"):
        owner.cached = "document"
        owner.stamp = datetime.datetime.now() - timedelta(seconds=700)  # stale
        assert gate.run(owner.fetch_none) is None  # the failure: the pause begins
        assert owner.calls == 1
        assert gate.run(owner.fetch_none) is None  # shut: replayed, no request
        assert owner.calls == 1

        owner.cache_seconds = 3599  # 700 s old is inside the window again
        assert gate.run(owner.fetch_none) == "document"
        assert owner.calls == 1


def test_consecutive_failures_double_the_pause_up_to_the_cache_lifetime():
    owner = _Owner()
    owner.cache_seconds = 599
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gaps = _gaps(gate, owner, owner.fetch_none, frozen, wanted=7)
    assert gaps == [60, 120, 240, 480, 599, 599]


def test_without_auto_update_the_pause_stays_at_sixty_seconds():
    owner = _Owner()
    owner.cache_seconds = 0
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gaps = _gaps(gate, owner, owner.fetch_none, frozen, wanted=4)
    assert gaps == [60, 60, 60]


def test_a_success_resets_the_backoff():
    owner = _Owner()
    owner.delay = 0
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gate.run(owner.fetch_none)  # failure 1: pause 60
        frozen.tick(60)
        gate.run(owner.fetch_none)  # failure 2: pause 120
        frozen.tick(120)
        assert gate.run(owner.fetch_ok) == "document"  # success
        frozen.tick(601)  # the entry has aged out
        calls = owner.calls
        gate.run(owner.fetch_none)  # one failure again, not the third in a row
        frozen.tick(59)
        gate.run(owner.fetch_none)
        assert owner.calls == calls + 1
        frozen.tick(2)
        gate.run(owner.fetch_none)
        assert owner.calls == calls + 2


def test_override_cache_bypasses_the_pause():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00"):
        gate.run(owner.fetch_none)
        gate.run(owner.fetch_none)
        assert owner.calls == 1  # paused
        owner.override_cache = True
        gate.run(owner.fetch_none)
        gate.run(owner.fetch_none)
        assert owner.calls == 3


def test_waiters_served_from_cache_do_not_count_as_failures():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    results = _in_threads(
        lambda: gate.run(owner.fetch_ok), lambda: gate.run(owner.fetch_ok)
    )
    assert results == ["document", "document"]
    assert owner.calls == 1
    assert gate._failed_at is None
    assert gate._failures == 0


def test_a_shorter_update_interval_shortens_a_running_pause():
    owner = _Owner()
    owner.cache_seconds = 3599
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gate.run(owner.fetch_none)
        frozen.tick(60)
        gate.run(owner.fetch_none)
        frozen.tick(120)
        gate.run(owner.fetch_none)  # the third failure: pause 240
        assert owner.calls == 3
        owner.cache_seconds = 0  # auto-update switched off: the pause is 60 now
        frozen.tick(61)
        gate.run(owner.fetch_none)
        assert owner.calls == 4


def test_the_pause_runs_on_the_monotonic_clock():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    clock = [5000.0]
    # No freezegun here: only ``time.monotonic`` moves, the wall clock does not.
    with patch.object(time, "monotonic", lambda: clock[0]):
        gate.run(owner.fetch_none)
        clock[0] += 59
        gate.run(owner.fetch_none)
        assert owner.calls == 1
        clock[0] += 2
        gate.run(owner.fetch_none)
        assert owner.calls == 2


def _slow_failure(owner, clock, seconds, gate=None, retry_after=None):
    """A fetch point that fails after ``seconds``, as Pirate Weather does over its retries."""

    def fetch():
        owner.calls += 1
        clock[0] += seconds
        if retry_after is not None:
            gate.note_response(_resp({"Retry-After": retry_after}))
        return None

    return fetch


def test_the_backoff_counts_from_the_start_of_the_failed_run():
    # Cycles come one cache window apart, start to start. A failed run that takes
    # its time (Pirate Weather: three tries, 1 s and 2 s apart) must not carry the
    # pause past the next cycle; on a live install the pause, counted from the end
    # of such a run, still had 2 s to go when the next cycle came.
    owner = _Owner()
    owner.cache_seconds = 0  # the pause is 60 s every time: the cap is the floor
    gate = fetch_gate.FetchGate(owner, "stamp")
    clock = [5000.0]
    fetch = _slow_failure(owner, clock, 3)
    with patch.object(time, "monotonic", lambda: clock[0]):
        gate.run(fetch)  # begins at 5000, fails at 5003
        clock[0] = 5000 + 59
        gate.run(fetch)
        assert owner.calls == 1
        clock[0] = 5000 + 60.5  # 60 s after the start, 57.5 s after the end
        gate.run(fetch)
        assert owner.calls == 2


def test_waiters_behind_a_slow_failure_share_it(caplog):
    # A failed run can outlast its own backoff (a 60 s timeout, three tries); with
    # the backoff counted from its start the pause is over when it ends. The
    # callers that waited on the lock meanwhile are handed its outcome all the
    # same: each of them would otherwise go to the network in turn.
    owner = _Owner()
    owner.cache_seconds = 599
    gate = fetch_gate.FetchGate(owner, "stamp")
    clock = [5000.0]
    began, release, waiter_arrived = (threading.Event() for _ in range(3))

    def slow_failure():
        owner.calls += 1
        began.set()
        release.wait(timeout=5)
        clock[0] += 61  # longer than the first backoff of 60 s
        return None

    def monotonic():
        # The waiter's first reading is its arrival; the failure may only end
        # after it, which this handshake makes certain rather than likely. The
        # value is read before the signal, so the clock cannot move in between.
        now = clock[0]
        if threading.current_thread() is waiter:
            waiter_arrived.set()
        return now

    first = threading.Thread(target=gate.run, args=(slow_failure,), daemon=True)
    waiter = threading.Thread(target=gate.run, args=(slow_failure,), daemon=True)
    with (
        patch.object(time, "monotonic", monotonic),
        caplog.at_level(logging.DEBUG, logger=fetch_gate.__name__),
    ):
        try:
            first.start()
            assert began.wait(timeout=5)
            waiter.start()  # arrives while the failure is still running
            assert waiter_arrived.wait(timeout=5)
        finally:
            release.set()
            first.join(timeout=5)
            waiter.join(timeout=5)
        assert not first.is_alive() and not waiter.is_alive()
    assert owner.calls == 1
    replays = [r.getMessage() for r in caplog.records if r.name == fetch_gate.__name__]
    assert len(replays) == 1
    assert "waited through" in replays[0]  # not "no request for another 0 s"


def test_retry_after_counts_from_the_answer():
    # "Not before" is measured from the response that asked for it, not from the
    # start of the run that got it.
    owner = _Owner()
    owner.cache_seconds = 0
    gate = fetch_gate.FetchGate(owner, "stamp")
    clock = [5000.0]
    fetch = _slow_failure(owner, clock, 3, gate=gate, retry_after="100")
    with patch.object(time, "monotonic", lambda: clock[0]):
        gate.run(fetch)  # begins at 5000, answered at 5003
        clock[0] = 5000 + 101  # 101 s after the start, 98 s after the answer
        gate.run(fetch)
        assert owner.calls == 1
        clock[0] = 5003 + 101
        gate.run(fetch)
        assert owner.calls == 2


def test_a_replay_logs_one_debug_line_and_nothing_louder(caplog):
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    with (
        freeze_time("2026-10-23 12:00:00") as frozen,
        caplog.at_level(logging.DEBUG, logger=fetch_gate.__name__),
    ):
        gate.run(owner.fetch_none)  # the real failure: the client logs it
        frozen.tick(30)
        gate.run(owner.fetch_none)  # the replay
    records = [r for r in caplog.records if r.name == fetch_gate.__name__]
    assert [r.levelno for r in records] == [logging.DEBUG]
    text = records[0].getMessage()
    assert "_Owner" in text and "stamp" in text and "30" in text


def test_failure_log_level_is_debug_for_a_replay_and_error_otherwise():
    owner = _Owner()
    owner.error = lambda: OSError("down")
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        with pytest.raises(OSError) as real:
            gate.run(owner.fetch_raise)
        frozen.tick(30)
        with pytest.raises(OSError) as replayed:
            gate.run(owner.fetch_raise)
    assert fetch_gate.failure_log_level(real.value) == logging.ERROR
    assert fetch_gate.failure_log_level(replayed.value) == logging.DEBUG
    # an exception that never went through the gate, e.g. a parse error
    assert fetch_gate.failure_log_level(ValueError("bad body")) == logging.ERROR


def _resp(headers):
    """A response carrying ``headers``."""
    response = MagicMock()
    response.headers = headers
    return response


@freeze_time("2026-10-23 12:00:00")
def test_retry_after_is_read_as_seconds_or_http_date():
    assert retry_after_seconds(_resp({"Retry-After": "120"})) == 120
    assert (
        retry_after_seconds(_resp({"Retry-After": "Fri, 23 Oct 2026 12:05:00 GMT"}))
        == 300
    )
    for bad in ("", "soon", "-5", "Fri, 23 Oct 2026 11:00:00 GMT"):
        assert retry_after_seconds(_resp({"Retry-After": bad})) is None
    assert retry_after_seconds(_resp({})) is None
    assert retry_after_seconds(MagicMock()) is None  # non-str header value


@freeze_time("2026-10-23 12:00:00")
def test_retry_after_tolerates_what_a_response_may_look_like():
    assert retry_after_seconds(None) is None  # e.g. ConnectionError.response
    assert retry_after_seconds(_resp(None)) is None
    assert retry_after_seconds(_resp({"Retry-After": 120})) is None  # not a str
    assert retry_after_seconds(_resp({"Retry-After": " 90 "})) == 90
    assert retry_after_seconds(_resp({"Retry-After": "0"})) is None  # nothing to wait
    superscript_two = chr(0xB2)  # str.isdigit() is true for it, int() refuses it
    assert retry_after_seconds(_resp({"Retry-After": superscript_two})) is None
    assert retry_after_seconds(_resp({"Retry-After": "9" * 5000})) is None
    # a date without a zone is read as UTC
    zoneless = "Fri, 23 Oct 2026 12:05:00 -0000"
    assert retry_after_seconds(_resp({"Retry-After": zoneless})) == 300


def test_an_http_date_is_measured_against_the_utc_clock():
    # ``freeze_time(..., tz_offset=...)`` shifts ``now(tz)`` along with ``now()``,
    # so under it the UTC clock and a naive local one agree and a mix-up of the
    # two goes unseen. This stand-in reads two hours ahead only without a zone,
    # as a clock does in UTC+2; with a zone it is right.
    utc_now = datetime.datetime(2026, 10, 23, 12, 0, tzinfo=datetime.UTC)
    local_now = utc_now.replace(tzinfo=None) + timedelta(hours=2)
    clock = MagicMock()
    clock.UTC = datetime.UTC
    clock.timedelta = datetime.timedelta
    clock.datetime.now.side_effect = lambda tz=None: (
        local_now if tz is None else utc_now.astimezone(tz)
    )
    with patch.object(fetch_gate, "datetime", clock):
        dated = "Fri, 23 Oct 2026 12:05:00 GMT"
        assert retry_after_seconds(_resp({"Retry-After": dated})) == 300
        zoneless = "Fri, 23 Oct 2026 12:05:00 -0000"  # read as UTC
        assert retry_after_seconds(_resp({"Retry-After": zoneless})) == 300


def _throttled(owner, gate, retry_after):
    """A fetch point that fails with a 429 whose ``Retry-After`` is ``retry_after``."""

    def fetch():
        owner.calls += 1
        gate.note_response(_resp({"Retry-After": retry_after}))
        return None

    return fetch


def test_a_longer_retry_after_wins_over_the_backoff():
    owner = _Owner()
    owner.cache_seconds = 599
    gate = fetch_gate.FetchGate(owner, "stamp")
    fetch = _throttled(owner, gate, "900")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gate.run(fetch)
        assert owner.calls == 1
        frozen.tick(899)
        gate.run(fetch)
        assert owner.calls == 1  # the backoff alone (60 s) would be over long ago
        frozen.tick(2)
        gate.run(fetch)
        assert owner.calls == 2


def test_a_shorter_retry_after_keeps_the_backoff():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    fetch = _throttled(owner, gate, "10")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gate.run(fetch)
        frozen.tick(30)
        gate.run(fetch)
        assert owner.calls == 1  # Retry-After is a lower bound, not the pause
        frozen.tick(31)
        gate.run(fetch)
        assert owner.calls == 2


def test_retry_after_is_capped_at_a_day():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    fetch = _throttled(owner, gate, "999999")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gate.run(fetch)
        frozen.tick(86399)
        gate.run(fetch)
        assert owner.calls == 1
        frozen.tick(2)
        gate.run(fetch)
        assert owner.calls == 2


def test_retry_after_is_read_from_a_raised_http_error():
    owner = _Owner()
    owner.error = lambda: requests.HTTPError(
        "429", response=_resp({"Retry-After": "900"})
    )
    gate = fetch_gate.FetchGate(owner, "stamp")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        with pytest.raises(requests.HTTPError):
            gate.run(owner.fetch_raise)
        frozen.tick(899)
        with pytest.raises(requests.HTTPError):
            gate.run(owner.fetch_raise)
        assert owner.calls == 1
        frozen.tick(2)
        with pytest.raises(requests.HTTPError):
            gate.run(owner.fetch_raise)
        assert owner.calls == 2


def test_retry_after_binds_only_the_failure_that_carried_it():
    owner = _Owner()
    owner.cache_seconds = 599
    gate = fetch_gate.FetchGate(owner, "stamp")
    throttled = _throttled(owner, gate, "900")
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gate.run(throttled)
        frozen.tick(901)
        gate.run(owner.fetch_none)  # the second failure says nothing
        assert owner.calls == 2
        frozen.tick(119)
        gate.run(owner.fetch_none)
        assert owner.calls == 2  # the backoff of the second failure: 120 s
        frozen.tick(2)
        gate.run(owner.fetch_none)
        assert owner.calls == 3


def test_a_response_noted_by_one_run_does_not_reach_the_next():
    owner = _Owner()
    gate = fetch_gate.FetchGate(owner, "stamp")
    gate.note_response(_resp({"Retry-After": "900"}))  # before any run
    with freeze_time("2026-10-23 12:00:00") as frozen:
        gate.run(owner.fetch_none)  # a failure that noted nothing itself
        frozen.tick(61)
        gate.run(owner.fetch_none)
        assert owner.calls == 2
