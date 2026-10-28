"""Every fetch point of the four weather clients, one table, one door.

``CASES`` names each of the seven places where a client goes to the network:
how to build the client, which call reaches the fetch point, a body the fetch
point accepts, and the attribute that holds the time of the last good fetch.
The tests below run over that table.
"""

import dataclasses
import json
import logging
import pathlib
import threading
import time
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest
import requests
from freezegun import freeze_time

from custom_components.irrigation_plus.weathermodules.MetOfficeClient import (
    MetOfficeClient,
)
from custom_components.irrigation_plus.weathermodules.OpenMeteoClient import (
    OpenMeteoClient,
)
from custom_components.irrigation_plus.weathermodules.OWMClient import OWMClient
from custom_components.irrigation_plus.weathermodules.PirateWeatherClient import (
    PirateWeatherClient,
)

from . import test_weather_modules as twm

M = "custom_components.irrigation_plus.weathermodules."

_PIRATE_FIXTURE = (
    pathlib.Path(__file__).parent / "fixtures" / "pirate_weather_berlin.json"
)


@pytest.fixture(autouse=True)
def sleep():
    """Stand in for the pause Pirate Weather takes between its retries; yield it.

    Without it every failing Pirate Weather run in this file would wait three
    seconds for real. Only the client module's own name ``time`` is replaced:
    patching ``PirateWeatherClient.time.sleep`` would swap ``time.sleep`` for the
    whole process, and ``_five_callers_at_once`` relies on the real one.
    """
    with patch(M + "PirateWeatherClient.time") as fake_time:
        yield fake_time.sleep


@dataclasses.dataclass(frozen=True)
class GateCase:
    """One fetch point of one client."""

    id: str
    patch: str  # the session call the fetch point makes
    make: Callable[[], Any]  # a fresh client
    call: Callable[[Any], Any]  # the public call that reaches the fetch point
    ok_body: dict  # a body the fetch point accepts
    stamp: str  # attribute holding the time of the last good fetch
    failed_attempts: int  # requests one failed run makes with status 500


def _ok(body):
    """A 200 response carrying ``body``."""
    response = MagicMock()
    response.status_code = 200
    response.text = json.dumps(body)
    response.headers = {}
    return response


def _failing(status, headers=None):
    """A response with ``status`` whose ``raise_for_status`` raises ``HTTPError``."""
    response = MagicMock()
    response.status_code = status
    response.text = "{}"
    response.headers = {} if headers is None else headers
    response.raise_for_status.side_effect = requests.HTTPError(
        str(status), response=response
    )
    return response


def _owm():
    return OWMClient(api_key="k", latitude=1.0, longitude=2.0, elevation=0)


def _pirate():
    return PirateWeatherClient("key", "1", 52.0, 5.0, 0)


def _open_meteo():
    return OpenMeteoClient(latitude=1.0, longitude=2.0)


def _met_office():
    return MetOfficeClient(api_key="k", latitude=1.0, longitude=2.0)


_PIRATE_BODY = json.loads(_PIRATE_FIXTURE.read_text(encoding="utf-8"))

CASES: list[GateCase] = [
    GateCase(
        "owm_data",
        M + "OWMClient._SESSION.get",
        _owm,
        lambda c: c.get_data(),
        twm.TestOWMClientCaching._CURRENT_BODY,
        "_cached_data_at",
        1,
    ),
    GateCase(
        "owm_forecast",
        M + "OWMClient._SESSION.get",
        _owm,
        lambda c: c.get_forecast_data(),
        twm.TestOWMClientGetForecastData()._forecast_body(),
        "_cached_forecast_at",
        1,
    ),
    GateCase(
        "pirate_data",
        M + "PirateWeatherClient._SESSION.get",
        _pirate,
        lambda c: c.get_data(),
        _PIRATE_BODY,
        "_cached_data_at",
        3,
    ),
    GateCase(
        "pirate_forecast",
        M + "PirateWeatherClient._SESSION.get",
        _pirate,
        lambda c: c.get_forecast_data(),
        _PIRATE_BODY,
        "_cached_forecast_at",
        3,
    ),
    GateCase(
        "openmeteo_doc",
        M + "OpenMeteoClient._SESSION.get",
        _open_meteo,
        lambda c: c.get_forecast_data(),
        {"hourly": {"time": []}, "daily": {"time": []}},
        "_cached_doc_at",
        1,
    ),
    GateCase(
        "met_hourly",
        M + "MetOfficeClient._SESSION.get",
        _met_office,
        lambda c: c.get_data(),
        twm._met_doc([]),
        "_cached_hourly_at",
        1,
    ),
    GateCase(
        "met_three_hourly",
        M + "MetOfficeClient._SESSION.get",
        _met_office,
        lambda c: c.get_forecast_data(),
        twm._met_doc([]),
        "_cached_three_hourly_at",
        1,
    ),
]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_every_client_asks_the_shared_freshness_check(case):
    client = case.make()
    get = MagicMock(return_value=_ok(case.ok_body))
    with patch(case.patch, get), patch(M + "fetch_gate.is_fresh", return_value=False):
        case.call(client)
        case.call(client)
    # Without the shared check the second call is a cache hit.
    assert get.call_count == 2


def _five_callers_at_once(case, client, response):
    """Five threads call at once; the request is held back until all have arrived.

    Returns the session mock and what each caller returned or raised.
    """
    release = threading.Event()
    results: list = []

    def slow_get(*args, **kwargs):
        # Bounded wait: a gate that never opens must fail the test, not hang it.
        release.wait(timeout=5)
        return response

    get = MagicMock(side_effect=slow_get)

    def caller():
        try:
            results.append(case.call(client))
        except Exception as ex:
            results.append(ex)

    threads = [threading.Thread(target=caller, daemon=True) for _ in range(5)]
    with patch(case.patch, get):
        try:
            for thread in threads:
                thread.start()
            deadline = time.monotonic() + 5
            while get.call_count < 1 and time.monotonic() < deadline:
                time.sleep(0.01)
            time.sleep(0.2)  # time for the other four to reach the gate
        finally:
            release.set()
            for thread in threads:
                thread.join(timeout=5)

    assert not any(thread.is_alive() for thread in threads)
    return get, results


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_concurrent_callers_make_one_request(case):
    client = case.make()
    get, results = _five_callers_at_once(case, client, _ok(case.ok_body))

    assert get.call_count == 1
    assert getattr(client, case.stamp) is not None
    assert len(results) == 5
    assert len({repr(r) for r in results}) == 1  # everyone got the same answer


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_concurrent_callers_during_an_outage_share_one_failed_run(case):
    client = case.make()
    get, results = _five_callers_at_once(case, client, _failing(500))

    # The callers behind the failed run must not each make their own request:
    # they get the failure's outcome, the same one the first caller got.
    assert get.call_count == case.failed_attempts
    assert getattr(client, case.stamp) is None
    assert len(results) == 5
    assert len({repr(r) for r in results}) == 1


def _outcome(case, client):
    """What a caller sees: the value it got, or the type and message it was thrown."""
    try:
        return ("returned", case.call(client))
    except Exception as ex:
        return ("raised", type(ex), str(ex))


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_a_failed_fetch_pauses_its_gate(case):
    client = case.make()
    get = MagicMock(return_value=_failing(500))
    with freeze_time("2026-10-23 12:00:00") as frozen, patch(case.patch, get):
        first = _outcome(case, client)
        assert get.call_count == case.failed_attempts
        assert getattr(client, case.stamp) is None  # a failure leaves no timestamp

        frozen.tick(30)
        assert _outcome(case, client) == first  # same result, no request
        assert get.call_count == case.failed_attempts

        frozen.tick(31)
        _outcome(case, client)
        assert get.call_count == 2 * case.failed_attempts


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_retry_after_reaches_the_gate(case):
    # OWM and Pirate Weather do not expose the response of a bad status (an
    # OSError, a None); Open-Meteo and Met Office raise an HTTPError that
    # carries it. The pause must honour the header on all seven paths.
    client = case.make()
    get = MagicMock(return_value=_failing(429, {"Retry-After": "900"}))
    with freeze_time("2026-10-23 12:00:00") as frozen, patch(case.patch, get):
        _outcome(case, client)
        asked = get.call_count
        assert asked >= 1  # how many requests one run makes is not this test's business

        frozen.tick(600)
        _outcome(case, client)
        assert get.call_count == asked  # the backoff alone (60 s) would be over

        frozen.tick(301)
        _outcome(case, client)
        assert get.call_count > asked


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_a_replayed_failure_logs_nothing_above_debug(case, caplog):
    # An ERROR line of a weather client means a real request was made and failed.
    # A failure the gate replays during its pause made no request, so Open-Meteo's
    # and Met Office's accessors, which log the exception above the gate, must log
    # it at DEBUG. OWM and Pirate Weather catch inside the gate body, which does
    # not run in the pause.
    client = case.make()
    get = MagicMock(return_value=_failing(500))
    caplog.set_level(logging.DEBUG, logger="custom_components.irrigation_plus")
    with freeze_time("2026-10-23 12:00:00") as frozen, patch(case.patch, get):
        # No assertion on the first call's log: OWM's forecast lets its OSError out
        # unlogged, and the others log the real failure at ERROR.
        first = _outcome(case, client)
        assert get.call_count == case.failed_attempts
        caplog.clear()

        frozen.tick(30)
        assert _outcome(case, client) == first  # the outcome is the same as before
        assert get.call_count == case.failed_attempts  # and it was a replay

    ours = [
        r
        for r in caplog.records
        if r.name.startswith("custom_components.irrigation_plus.weathermodules")
    ]
    assert [r for r in ours if r.levelno > logging.DEBUG] == []
    assert any("replaying the last outcome" in r.getMessage() for r in ours)


@pytest.mark.parametrize("call", ["get_data", "get_forecast_data", "get_hourly_data"])
def test_every_open_meteo_accessor_logs_a_replay_at_debug(call, caplog):
    # The table above reaches one Open-Meteo accessor; all three read the one
    # document behind one gate and each has its own log line.
    client = _open_meteo()
    get = MagicMock(return_value=_failing(500))
    caplog.set_level(logging.DEBUG, logger="custom_components.irrigation_plus")

    def levels():
        return [r.levelno for r in caplog.records if r.name.endswith("OpenMeteoClient")]

    with freeze_time("2026-10-23 12:00:00") as frozen, patch(
        M + "OpenMeteoClient._SESSION.get", get
    ):
        getattr(client, call)()  # the real failure: still an ERROR line
        assert get.call_count == 1
        assert levels() == [logging.ERROR]
        caplog.clear()

        frozen.tick(30)
        getattr(client, call)()
        assert get.call_count == 1  # a replay: no request
        assert [level for level in levels() if level > logging.DEBUG] == []


@pytest.mark.parametrize("call", ["get_data", "get_forecast_data"])
def test_every_met_office_accessor_logs_its_first_failure_at_error(call, caplog):
    # Both accessors log the failure above the gate with ``failure_log_level``.
    # The table's replay test says nothing about the first call, and Open-Meteo's
    # twin above is not Met Office's code: a hard-coded DEBUG at either Met Office
    # site would pass both and hide every outage of that service from the log.
    client = _met_office()
    get = MagicMock(return_value=_failing(500))
    caplog.set_level(logging.DEBUG, logger="custom_components.irrigation_plus")
    prefix = "custom_components.irrigation_plus.weathermodules"

    def ours():
        return [r for r in caplog.records if r.name.startswith(prefix)]

    with freeze_time("2026-10-23 12:00:00") as frozen, patch(
        M + "MetOfficeClient._SESSION.get", get
    ):
        getattr(client, call)()  # the real failure
        assert get.call_count == 1
        assert [r.levelno for r in ours()].count(logging.ERROR) == 1
        caplog.clear()

        frozen.tick(30)
        getattr(client, call)()
        assert get.call_count == 1  # a replay: no request
        assert [r for r in ours() if r.levelno > logging.DEBUG] == []


_CASE_BY_ID = {case.id: case for case in CASES}


@pytest.mark.parametrize(
    "paused_id, free_id",
    [("owm_forecast", "owm_data"), ("met_three_hourly", "met_hourly")],
)
def test_a_paused_forecast_does_not_hold_up_current_conditions(paused_id, free_id):
    paused, free = _CASE_BY_ID[paused_id], _CASE_BY_ID[free_id]
    client = paused.make()
    get = MagicMock(return_value=_failing(500))
    with freeze_time("2026-10-23 12:00:00"), patch(paused.patch, get):
        _outcome(paused, client)
        assert get.call_count == paused.failed_attempts

        get.return_value = _ok(free.ok_body)
        free.call(client)
        assert get.call_count == paused.failed_attempts + 1  # the other door is open
        assert getattr(client, free.stamp) is not None

        get.return_value = _failing(500)
        _outcome(paused, client)
        assert get.call_count == paused.failed_attempts + 1  # this one is still shut


def test_validate_key_ignores_a_running_pause():
    case = _CASE_BY_ID["owm_data"]
    client = case.make()
    get = MagicMock(return_value=_failing(500))
    with freeze_time("2026-10-23 12:00:00"), patch(case.patch, get):
        _outcome(case, client)
        assert get.call_count == 1
        _outcome(case, client)
        assert get.call_count == 1  # paused

        get.return_value = _ok({"cod": 200})
        client.validate_key()
        assert get.call_count == 2  # the key check always asks


_PIRATE_CASES = [case for case in CASES if case.id.startswith("pirate_")]
# Renaming a case id would empty this list and the four tests below would
# collect no case at all, passing by not running.
assert len(_PIRATE_CASES) == 2


@pytest.mark.parametrize("case", _PIRATE_CASES, ids=lambda c: c.id)
def test_pirate_pauses_one_then_two_seconds_between_retries(case, sleep):
    client = case.make()
    get = MagicMock(return_value=_failing(500))
    with patch(case.patch, get):
        _outcome(case, client)

    assert get.call_count == 3
    # Two pauses between three attempts, none after the last.
    assert sleep.call_args_list == [call(1), call(2)]


@pytest.mark.parametrize("case", _PIRATE_CASES, ids=lambda c: c.id)
def test_pirate_stops_retrying_on_429(case, sleep):
    # At Pirate Weather a 429 means the monthly quota is used up: a second
    # request a second or two later cannot succeed.
    client = case.make()
    get = MagicMock(return_value=_failing(429))
    with patch(case.patch, get):
        _outcome(case, client)

    assert get.call_count == 1
    sleep.assert_not_called()


@pytest.mark.parametrize("case", _PIRATE_CASES, ids=lambda c: c.id)
def test_pirate_stops_retrying_when_told_when_to_come_back(case, sleep):
    # The service named the time; a retry after one second would ignore it.
    client = case.make()
    get = MagicMock(return_value=_failing(503, {"Retry-After": "120"}))
    with patch(case.patch, get):
        _outcome(case, client)

    assert get.call_count == 1
    sleep.assert_not_called()


@pytest.mark.parametrize("case", _PIRATE_CASES, ids=lambda c: c.id)
def test_pirate_does_not_retry_a_network_error(case, sleep):
    client = case.make()
    get = MagicMock(side_effect=requests.ConnectionError)
    with patch(case.patch, get):
        _outcome(case, client)

    assert get.call_count == 1
    sleep.assert_not_called()
