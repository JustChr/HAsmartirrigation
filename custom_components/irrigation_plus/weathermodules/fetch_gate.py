"""Rules the four weather clients share when they go to the network."""

import copy
import datetime
import email.utils
import logging
import threading
import time
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

_LOGGER = logging.getLogger(__name__)

# Floor for how long a fetched result is reused, even when the caller's configured
# cache window is shorter (e.g. auto-update disabled → 0s). Repeated weather
# lookups — skip-condition checks, the dashboard outlook, the intra-day estimate —
# would otherwise each hit the network (and a DNS lookup); this caps them to at
# most one call per method per minute.
MIN_CACHE_SECONDS = 60

# How long a fetch point stays shut after its first failed fetch. Every further
# failure in a row doubles it, up to the cache lifetime (see ``_pause_left``).
FIRST_PAUSE_SECONDS = 60

# Doublings after which the cache lifetime has won in any case; keeps ``2 ** n``
# small for a gate that has been failing for weeks.
_MAX_DOUBLINGS = 16

# The longest a ``Retry-After`` header can keep a fetch point shut: one day. The
# reasons are with the pause itself (``_pause_left``).
MAX_RETRY_AFTER_SECONDS = 86400

# Set on an exception the gate raises again in place of a fresh failure.
_REPLAY_ATTR = "_fetch_gate_replay"


def cache_lifetime(cache_seconds: float) -> float:
    """How long a fetched result is reused: the configured window, but at least the floor."""
    return max(cache_seconds, MIN_CACHE_SECONDS)


def is_fresh(
    fetched_at: datetime.datetime | None, cache_seconds: float, override_cache: bool
) -> bool:
    """Whether a result fetched at ``fetched_at`` may still be served cached."""
    if fetched_at is None or override_cache:
        return False
    return datetime.datetime.now() < fetched_at + datetime.timedelta(
        seconds=cache_lifetime(cache_seconds)
    )


def is_replay(exc: BaseException) -> bool:
    """Whether ``exc`` is a failure the gate replayed, not a fresh one."""
    return getattr(exc, _REPLAY_ATTR, False)


def failure_log_level(exc: BaseException) -> int:
    """The level to log a caught fetch failure at: DEBUG for a replay, else ERROR.

    An ERROR line of a weather client means a request was made and failed. A
    replay made none, and the gate has already logged it at DEBUG, so the
    accessor that catches it above the gate logs it at DEBUG too. The message
    stays the same; any other exception, including a failure to parse a good
    response, keeps ERROR.
    """
    return logging.DEBUG if is_replay(exc) else logging.ERROR


def retry_after_seconds(response: Any) -> float | None:
    """Seconds from now that ``response`` asks us to wait (``Retry-After``), or None.

    RFC 9110 section 10.2.3 allows a number of seconds or an HTTP date. A header
    that is missing, unreadable, not a string (a test double's attribute) or
    already due gives None. The value is returned as sent; the cap on how much of
    it counts is applied where the pause is worked out.
    """
    get = getattr(getattr(response, "headers", None), "get", None)
    if not callable(get):
        return None
    value = get("Retry-After")
    if not isinstance(value, str):
        return None
    value = value.strip()
    try:
        if value.isascii() and value.isdigit():
            seconds = float(int(value))
        else:
            when = email.utils.parsedate_to_datetime(value)
            if when.tzinfo is None:  # "-0000": a date without a zone is UTC
                when = when.replace(tzinfo=datetime.UTC)
            seconds = (when - datetime.datetime.now(datetime.UTC)).total_seconds()
    except (ValueError, TypeError, OverflowError):
        return None
    return seconds if seconds > 0 else None


def _copy_of(exc: Exception) -> Exception | None:
    """A copy of ``exc`` without traceback, or None where none can be made.

    ``copy.copy`` rebuilds an exception through its class with ``args``, which an
    exception whose constructor wants more than that refuses. A class whose
    ``__copy__`` hands back the instance itself gives no copy either: marking
    that "copy" would mark the real exception.

    None is the caller's cue to keep and raise the exception itself, unmarked
    (see ``_replay``). There is no second attempt that rebuilds the instance
    without its constructor: that would hand out an object its class never
    initialised, and giving up costs only a replay logged at ERROR.
    """
    try:
        again = copy.copy(exc)
    except Exception:  # noqa: BLE001 -- any exception class may refuse a copy
        return None
    return None if again is exc else again


def _replayable_copy(exc: Exception) -> Exception | None:
    """A copy of ``exc`` marked as a replay, or None where none can be made.

    A copy has no traceback of its own, so replaying it again and again does not
    grow one, and callers in several threads never share an instance. Only the
    copy is marked, never ``exc``: it may be the failure a first caller is about
    to log.
    """
    again = _copy_of(exc)
    if again is None:
        return None
    try:
        setattr(again, _REPLAY_ATTR, True)
    except Exception:  # noqa: BLE001 -- a class may refuse a new attribute
        return None
    return again


class FetchGate:
    """The door in front of one fetch point: one caller at a time goes through.

    ``owner`` is the client and ``stamp_attr`` the name of the attribute that holds
    the time of its last good fetch at this point. After a failed fetch the door
    stays shut for a while and hands the callers behind it that failure's outcome
    instead of asking the service again.
    """

    def __init__(self, owner: Any, stamp_attr: str) -> None:
        """Init."""
        self._owner = owner
        self._stamp_attr = stamp_attr
        self._lock = threading.Lock()
        self._failures = 0  # failed runs in a row
        # time.monotonic() at which the latest one began
        self._failed_at: float | None = None
        # (raised, value) of it; an exception is kept as a copy without traceback
        self._outcome: tuple[bool, Any] | None = None
        # time.monotonic() before which its response asked us not to come back
        self._asked_until: float | None = None
        # time.monotonic() at which it ended; a caller that arrived earlier waited
        # through it
        self._settled_at: float | None = None
        self._response: Any = None  # latest response of the run in progress

    def note_response(self, response: Any) -> None:
        """Remember ``response``, the answer to the request the fetch has just made.

        For a fetch body that does not let the response out when the status is bad
        (it returns None or raises an error that does not carry it): the pause
        then still finds its ``Retry-After``. Called from inside ``fetch``, so
        under the lock and in the thread that runs it; the latest call wins.
        """
        self._response = response

    def run(self, fetch: Callable[[], T]) -> T:
        """Run ``fetch`` with every other caller of this gate held back."""
        # Wurzel: the clients are called from several executor threads at once --
        #   every sensor refresh, skip check and outlook asks for the same
        #   document. Each caller checked the cache, found it empty and went to
        #   the network itself: measured on one live install (Pirate Weather,
        #   9 zones × 2 schedules), 1 get_data and 18 get_forecast_data requests
        #   left within 0.6 s, on a metered key.
        # Fix-Logik: one lock per fetch point. ``fetch`` begins with its own
        #   freshness check, and that check now runs inside the lock, so a caller
        #   that waited finds the entry the first one stored and is served from
        #   it -- one request per document. A caller that waited behind a failed
        #   fetch is handed that failure's outcome, so a failure is not retried
        #   once per waiter either: it notes when it arrived, before taking the
        #   lock, and a failure that ended after that is one it waited through
        #   (``_waited_through_failure``) -- whether or not the pause is over.
        # NOT-TO-DO: no ``asyncio`` lock -- every path that reaches a gate runs
        #   in an executor thread, and an ``asyncio`` lock does not hold threads
        #   back. The hourly accessors that run on the event loop only read
        #   stored documents and must never reach a gate. No lock around the
        #   request alone either: the parse and the timestamp come after it, so
        #   the waiters would wake to a cache that is still empty and fetch again.
        # siehe test_weather_clients_fetch_gate.py::test_concurrent_callers_make_one_request
        #   und ::test_concurrent_callers_during_an_outage_share_one_failed_run
        arrived = time.monotonic()
        with self._lock:
            owner = self._owner
            before = getattr(owner, self._stamp_attr)
            was_fresh = is_fresh(before, owner.cache_seconds, owner.override_cache)
            # ``override_cache`` means "hand out nothing stored", and a stored
            # failure is stored too: it asks the service every time.
            if not was_fresh and not owner.override_cache:
                seconds_left = self._pause_left()
                if seconds_left > 0 or self._waited_through_failure(arrived):
                    return self._replay(seconds_left)
            self._response = None
            started = time.monotonic()
            try:
                result = fetch()
            except Exception as exc:
                self._settle(before, was_fresh, started, raised=True, value=exc)
                raise
            self._settle(before, was_fresh, started, raised=False, value=result)
            return result

    def _settle(
        self, before: Any, was_fresh: bool, started: float, raised: bool, value: Any
    ) -> None:
        """Note how the run that has just ended went: a good fetch or a failure."""
        # Wurzel: the fetch points fail in three different ways -- an exception, a
        #   None after a non-200 status, a None after an incomplete document --
        #   and only the exception says so. What they have in common is that none
        #   of them leaves a new timestamp.
        # Fix-Logik: a run that went to the network (the entry was not fresh when
        #   it began) and left no new timestamp is a failure; a new timestamp is a
        #   success and clears the count. A run served from the cache -- a caller
        #   that waited for the one that fetched -- is neither.
        # NOT-TO-DO: no list of status codes and exception types. It would have to
        #   be kept per client, and it would miss exactly the quiet None branches
        #   that today's code already treats as "nothing fetched".
        # siehe test_weather_clients_fetch_gate.py::test_a_failed_fetch_pauses_its_gate
        #   und test_weather_fetch_gate.py::test_waiters_served_from_cache_do_not_count_as_failures
        response, self._response = self._response, None  # not kept past this run
        if getattr(self._owner, self._stamp_attr) != before:
            self._failures = 0
            self._failed_at = None
            self._outcome = None
            self._asked_until = None
            self._settled_at = None
        elif not was_fresh:
            self._failures += 1
            # Wurzel: the pause measures a duration, not a time of day. A wall
            #   clock jumps when the clocks go back or the system time is set.
            #   And cycles come one cache window apart, start to start, while a
            #   failed run can take its time: Pirate Weather's three tries, 1 s
            #   and 2 s apart, took a good 3 s on a live install, so a pause
            #   counted from the end of the run still had 2 s to go when the next
            #   cycle came, and a capped gate asked only every second cycle.
            # Fix-Logik: ``time.monotonic()``, read at the moment it is needed (in
            #   ``run``, here and in ``_pause_left``); the backoff counts from the
            #   start of the failed run, like the cycle does. What a response
            #   asked for counts from that response (``_asked_until``), and the
            #   callers that waited through the run are told by its end
            #   (``_settled_at``), not by the pause.
            # NOT-TO-DO: not ``datetime.datetime.now()`` -- the freshness check
            #   keeps it because the success path must not change; two clocks in
            #   one module is the price. And never bind ``time.monotonic`` to a
            #   name or a default argument: freezegun moves it with ``tick()``
            #   only when the call goes through the ``time`` module. Do not count
            #   ``Retry-After`` from the start as well: it would ask a service
            #   that named a wait again as many seconds too early as the run took.
            # siehe test_weather_fetch_gate.py::test_the_pause_runs_on_the_monotonic_clock,
            #   ::test_the_backoff_counts_from_the_start_of_the_failed_run,
            #   ::test_retry_after_counts_from_the_answer
            #   und ::test_waiters_behind_a_slow_failure_share_it
            self._failed_at = started
            ended = time.monotonic()
            self._settled_at = ended
            # What the response of this failure asked for; see ``_pause_left``.
            asked = self._asked_wait(response, raised, value)
            self._asked_until = (
                ended + min(asked, MAX_RETRY_AFTER_SECONDS) if asked > 0 else None
            )
            # Wurzel: the exception that failed the run carries its traceback, and
            #   that holds every frame of the fetch and what was in them (a
            #   response body, a parsed document) for as long as the outcome is
            #   kept -- until the next fetch, up to a whole cache window. The first
            #   caller also still holds the real exception and logs it; a replay
            #   that marked that very instance would turn a real failure into a
            #   DEBUG line.
            # Fix-Logik: keep a copy, made now; each replay raises a fresh copy of it
            #   (see ``_replay``). The copy has no traceback of its own, which lets
            #   go of the fetch's frames. The real exception goes to the first
            #   caller untouched. Where no copy can be made it is kept as it is.
            # Limit: exceptions chained inside the copy keep their tracebacks.
            #   ``requests`` wraps urllib3's ``MaxRetryError`` in ``args[0]``, and
            #   that traceback holds the failed fetch's frames until the next fetch
            #   at this gate replaces the outcome. Bounded -- one chain per gate --
            #   and deliberate: the inner exception is shared with the real one
            #   the first caller holds (its ``__context__``), so stripping its
            #   traceback would cut one that caller is still using.
            # NOT-TO-DO: do not keep the original "for the traceback" -- nobody reads
            #   a replayed failure's traceback, it points into the gate. Do not
            #   strip the traceback of a chained exception either (Limit).
            # siehe test_weather_fetch_gate.py::test_a_failure_keeps_no_traceback_alive_after_its_caller_is_done
            if raised:
                kept = _copy_of(value)
                if kept is not None:
                    value = kept
            self._outcome = (raised, value)

    @staticmethod
    def _asked_wait(response: Any, raised: bool, value: Any) -> float:
        """Seconds the failed run's response asked us to wait; 0 where it did not."""
        asked = [retry_after_seconds(response)]  # noted by a body that hides it
        if raised:  # an HTTPError carries its response
            asked.append(retry_after_seconds(getattr(value, "response", None)))
        return max((seconds for seconds in asked if seconds is not None), default=0.0)

    def _waited_through_failure(self, arrived: float) -> bool:
        """Whether a caller that arrived at ``arrived`` waited through the latest failure."""
        # Wurzel: the backoff counts from the start of the failed run, and a run
        #   can outlast it -- a 60 s timeout, and Pirate Weather tries three
        #   times. Its pause is then over the moment it ends, and every caller
        #   that waited on the lock meanwhile would go to the network in turn.
        # Fix-Logik: a caller that arrived before the failure ended was one of
        #   those waiting for it, and is handed its outcome like the others.
        # NOT-TO-DO: no margin added to the pause after the run's end: a guess at
        #   how quickly the waiters wake, where their arrival is known exactly.
        # siehe test_weather_fetch_gate.py::test_waiters_behind_a_slow_failure_share_it
        return self._settled_at is not None and arrived < self._settled_at

    def _pause_left(self) -> float:
        """Seconds the pause after the latest failure still runs; 0 where there is none."""
        if self._failed_at is None:
            return 0.0
        # Wurzel: callers come every few seconds (6-7 lookups every 10-30 s,
        #   measured on one live install: OpenWeatherMap, 3 zones × 1 schedule).
        #   A pause of a fixed 60 s asks 1440 times a day in an outage, ten times
        #   the 144 of normal operation at 10 min; Met Office's free tier allows
        #   360 calls a day and has two gates.
        # Fix-Logik: 60 s, doubled with every further failure in a row, capped at
        #   the cache lifetime -- the failure path never asks more often than
        #   normal operation does. It is worked out at every check from the
        #   owner's current ``cache_seconds`` instead of being stored as a
        #   deadline, so a changed update interval takes effect at once.
        # NOT-TO-DO: no fixed 60 s (above). No pause of a whole cache window from
        #   the first failure either: one blip would then cost a full window, a
        #   whole day with daily updates.
        # siehe test_weather_fetch_gate.py::test_consecutive_failures_double_the_pause_up_to_the_cache_lifetime
        #   und ::test_a_shorter_update_interval_shortens_a_running_pause
        backoff = min(
            FIRST_PAUSE_SECONDS * 2 ** min(self._failures - 1, _MAX_DOUBLINGS),
            cache_lifetime(self._owner.cache_seconds),
        )
        # Wurzel: a service that answers 429 or 503 may say when it wants to be asked
        #   again (``Retry-After``). None of the four documents the header, so this
        #   is a safeguard for whatever sits in front of them -- a gateway, a proxy
        #   -- but a request before that moment is likely to be refused again.
        # Fix-Logik: the pause ends at the later of the backoff's end and the time
        #   the latest failure's response asked for, the latter at most
        #   MAX_RETRY_AFTER_SECONDS after that response. "Honour" means not
        #   earlier; asking later is allowed, so the header is a lower bound and
        #   never shortens the backoff (10 s asked, 60 s paused).
        # NOT-TO-DO: not the header alone as the pause -- a short value would have
        #   an outage asked about more often than the backoff allows. Not uncapped
        #   either: an absurd or misread value (a date years ahead, seconds taken
        #   for milliseconds) would shut the gate for good; at the cap it asks once
        #   a day. The cache lifetime does not cap it: the service decides here.
        # siehe test_weather_fetch_gate.py::test_a_longer_retry_after_wins_over_the_backoff,
        #   ::test_a_shorter_retry_after_keeps_the_backoff, ::test_retry_after_is_capped_at_a_day
        ends = self._failed_at + backoff
        if self._asked_until is not None:
            ends = max(ends, self._asked_until)
        return max(0.0, ends - time.monotonic())

    def _replay(self, seconds_left: float) -> Any:
        """Hand back the outcome of the failure that began the pause: no request."""
        raised, value = self._outcome
        if seconds_left > 0:
            _LOGGER.debug(
                "%s %s: %d failed fetch(es) in a row, no request for another %.0f s;"
                " replaying the last outcome",
                type(self._owner).__name__,
                self._stamp_attr,
                self._failures,
                seconds_left,
            )
        else:  # a caller that waited through the failure (_waited_through_failure)
            _LOGGER.debug(
                "%s %s: waited through the latest of %d failed fetch(es) in a row;"
                " replaying the last outcome",
                type(self._owner).__name__,
                self._stamp_attr,
                self._failures,
            )
        if not raised:
            return value
        # ``value`` is the copy made when the failure was recorded; raise a fresh
        # copy of it, so no two callers ever share an instance.
        replayed = _replayable_copy(value)
        if replayed is None:
            # Wurzel: an exception that cannot be copied (``_copy_of``), or whose
            #   copy refuses the mark.
            # Fix-Logik: raise the kept instance itself, unmarked. Its replay is
            #   then logged at ERROR like a fresh failure: a line too many, never
            #   a real failure silenced.
            # NOT-TO-DO: never mark it. Where nothing could be copied it is the
            #   real exception, which the first caller may be about to log, and a
            #   mark would have that logged at DEBUG. No ``with_traceback(None)``
            #   either: it would cut the traceback the first caller is still
            #   building. The price is that every replay adds frames to the
            #   traceback of that one shared instance, so it grows for as long as
            #   the pause lasts; none of the seven fetch points can reach this,
            #   their exception types all copy.
            # siehe test_weather_fetch_gate.py::test_an_exception_that_cannot_be_copied_is_raised_again_unmarked
            raise value
        raise replayed
