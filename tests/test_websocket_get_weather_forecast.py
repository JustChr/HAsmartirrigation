"""The panel labels each forecast day with the day the client says it covers.

It used to compute today + i + 1 on the assumption that every client starts
at tomorrow and returns consecutive days. The entry now carries its own span, so
the label no longer depends on position.
"""

import datetime
import json
from types import SimpleNamespace
from unittest.mock import Mock

import homeassistant.util.dt as dt_util
import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.websockets import (
    websocket_get_weather_forecast,
)


def _env(entries):
    client = SimpleNamespace(get_forecast_data=lambda: entries)

    async def run_executor(func, *args):
        return func(*args)

    hass = SimpleNamespace(
        data={
            const.DOMAIN: {
                const.CONF_USE_WEATHER_SERVICE: True,
                "coordinator": SimpleNamespace(_WeatherServiceClient=client),
            }
        },
        async_add_executor_job=run_executor,
    )
    connection = Mock()
    sent = {}
    connection.send_result = Mock(
        side_effect=lambda mid, payload: sent.update(result=payload)
    )
    return hass, connection, sent


def _span_entry(start, end):
    return {
        const.FORECAST_DAY_START: start,
        const.FORECAST_DAY_END: end,
        const.MAPPING_MIN_TEMP: 10.0,
        const.MAPPING_MAX_TEMP: 20.0,
        const.MAPPING_PRECIPITATION: 1.0,
        const.MAPPING_WINDSPEED: 2.0,
    }


def _local_day_entry(day):
    # Open-Meteo and Pirate Weather: the span is the site's local day.
    start = dt_util.start_of_local_day(day)
    return _span_entry(
        dt_util.as_utc(start), dt_util.as_utc(start + datetime.timedelta(days=1))
    )


def _utc_day_entry(day):
    # OWM and Met Office: the span is the UTC day.
    start = datetime.datetime(
        day.year, day.month, day.day, tzinfo=datetime.timezone.utc
    )
    return _span_entry(start, start + datetime.timedelta(days=1))


async def _result(entries):
    hass, connection, sent = _env(entries)
    await websocket_get_weather_forecast.__wrapped__(hass, connection, {"id": 1})
    return sent["result"]


async def _labels(entries):
    result = await _result(entries)
    assert result["available"] is True
    return [d["date"] for d in result["days"]]


async def test_each_day_is_labelled_with_the_day_it_covers():
    today = dt_util.now().date()
    # Deliberately not "tomorrow, then the day after": a positional label would
    # say today+1 and today+2.
    days = [today + datetime.timedelta(days=2), today + datetime.timedelta(days=5)]

    result = await _result([_local_day_entry(d) for d in days])

    assert [d["date"] for d in result["days"]] == [d.isoformat() for d in days]
    # The span only picks the label. It stays out of the payload, which keeps
    # its five keys and plain JSON values (the stdlib encoder rejects datetimes).
    json.dumps(result)
    keys = {"date", "temp_min", "temp_max", "precipitation", "windspeed"}
    assert [set(d) for d in result["days"]] == [keys, keys]


@pytest.mark.parametrize("zone", ["America/Los_Angeles", "Europe/Berlin"])
async def test_a_utc_day_keeps_its_own_date_on_both_sides_of_utc(zone):
    # Most of a UTC day is the local day of the same date, and that is the label.
    # West of UTC, 00:00 UTC is the previous evening, so the local date of the
    # start would be a day early. East of UTC, the next 00:00 UTC is already the
    # next local day, so the local date of the end would be a day late.
    original = dt_util.DEFAULT_TIME_ZONE
    dt_util.set_default_time_zone(dt_util.get_time_zone(zone))
    try:
        today = dt_util.now().date()
        days = [today + datetime.timedelta(days=2), today + datetime.timedelta(days=5)]

        labels = await _labels([_utc_day_entry(d) for d in days])
    finally:
        dt_util.set_default_time_zone(original)

    assert labels == [d.isoformat() for d in days]


async def test_at_exactly_utc_plus_12_a_utc_day_takes_the_later_date():
    # A UTC day's middle, 12:00 UTC, is local midnight at UTC+12, so the span
    # splits evenly between two local dates. The later one is the label.
    # POSIX names invert the sign: Etc/GMT-12 is UTC+12.
    zone = dt_util.get_time_zone("Etc/GMT-12")
    original = dt_util.DEFAULT_TIME_ZONE
    dt_util.set_default_time_zone(zone)
    try:
        day = dt_util.now().date() + datetime.timedelta(days=2)
        entry = _utc_day_entry(day)
        start = entry[const.FORECAST_DAY_START]
        assert start.astimezone(zone).utcoffset() == datetime.timedelta(hours=12)

        labels = await _labels([entry])
    finally:
        dt_util.set_default_time_zone(original)

    assert labels == [(day + datetime.timedelta(days=1)).isoformat()]


async def test_the_label_is_the_local_date_not_the_utc_date():
    # At UTC+14 local noon is still the previous day in UTC, so the UTC date of
    # a local day's middle is one day early. The label has to be the local date.
    original = dt_util.DEFAULT_TIME_ZONE
    dt_util.set_default_time_zone(dt_util.get_time_zone("Pacific/Kiritimati"))
    try:
        today = dt_util.now().date()
        days = [today + datetime.timedelta(days=2), today + datetime.timedelta(days=5)]

        labels = await _labels([_local_day_entry(d) for d in days])
    finally:
        dt_util.set_default_time_zone(original)

    assert labels == [d.isoformat() for d in days]


@pytest.mark.parametrize("missing", [const.FORECAST_DAY_END, const.FORECAST_DAY_START])
async def test_an_entry_with_half_a_span_keeps_the_positional_label(missing):
    # Half a span is no span. Labelling a start alone by its local date would put
    # a UTC day a day early west of UTC (the test time zone), so the entry falls
    # back to its position like an entry without any span.
    today = dt_util.now().date()
    entry = _utc_day_entry(today + datetime.timedelta(days=3))
    del entry[missing]

    assert await _labels([entry]) == [(today + datetime.timedelta(days=1)).isoformat()]


async def test_an_entry_without_a_span_keeps_the_positional_label():
    entry = _local_day_entry(dt_util.now().date())
    del entry[const.FORECAST_DAY_START]
    del entry[const.FORECAST_DAY_END]
    today = dt_util.now().date()

    assert await _labels([entry, dict(entry)]) == [
        (today + datetime.timedelta(days=1)).isoformat(),
        (today + datetime.timedelta(days=2)).isoformat(),
    ]


@pytest.mark.parametrize("broken", ["reversed", "naive"])
async def test_an_entry_whose_span_cannot_be_placed_keeps_the_positional_label(
    broken,
):
    # The panel and the skip guard read the span through the same helper, so an
    # entry the guard refuses is refused here too. A naive start used to reach
    # the subtraction below and raise, taking the whole forecast card down.
    today = dt_util.now().date()
    entry = _utc_day_entry(today + datetime.timedelta(days=3))
    if broken == "reversed":
        entry[const.FORECAST_DAY_START], entry[const.FORECAST_DAY_END] = (
            entry[const.FORECAST_DAY_END],
            entry[const.FORECAST_DAY_START],
        )
    else:
        entry[const.FORECAST_DAY_START] = entry[const.FORECAST_DAY_START].replace(
            tzinfo=None
        )

    assert await _labels([entry]) == [(today + datetime.timedelta(days=1)).isoformat()]
