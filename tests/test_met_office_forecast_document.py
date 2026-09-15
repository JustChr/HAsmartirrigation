"""Met Office's hourly accessors read the more current of its two documents.

The client holds the hourly product, refreshed only by ``get_data``, and the
three-hourly one, refreshed by ``get_forecast_data``. The accessors preferred the
hourly document whenever one existed, however old. The precipitation skip guard
runs before any ``get_data`` of a dispatch, so on an install whose sensors take
nothing from Met Office it decided on the hourly forecast of an earlier run while
a fresh three-hourly one sat beside it.

The hourly document keeps its preference for one cache lifetime, at most three
hours: on a daily auto-update the lifetime is a day, and an hourly series fetched
that long before a fresh three-hourly one can end before the run's date does.
"""

import datetime

import pytest

from custom_components.irrigation_plus.weathermodules.MetOfficeClient import (
    MetOfficeClient,
)

UTC = datetime.timezone.utc
# The client stamps its fetches with naive local time.
FETCHED = datetime.datetime(2026, 9, 13, 6, 20)

HOURLY_SERIES = [(datetime.datetime(2026, 9, 12, 7, tzinfo=UTC), 0.0)]
THREE_HOURLY_SERIES = [(datetime.datetime(2026, 9, 13, 7, tzinfo=UTC), 3.0)]

# An hourly auto-update: the cache lives one hour less a second.
HOURLY_UPDATE = 3599
# A daily auto-update.
DAILY_UPDATE = 86399


def _doc(time, amount, temperature):
    return {
        "features": [
            {
                "properties": {
                    "timeSeries": [
                        {
                            "time": time,
                            "totalPrecipAmount": amount,
                            "screenTemperature": temperature,
                        }
                    ]
                }
            }
        ]
    }


def _client(hourly_age, cache_seconds=HOURLY_UPDATE):
    c = MetOfficeClient(api_key="k", latitude=51.5, longitude=-0.1, elevation=10)
    c.cache_seconds = cache_seconds
    c._cached_hourly = _doc("2026-09-12T06:00Z", 0.0, 11.0)
    c._cached_hourly_at = FETCHED - hourly_age
    c._cached_three_hourly = _doc("2026-09-13T06:00Z", 3.0, 17.0)
    c._cached_three_hourly_at = FETCHED
    return c


def test_a_day_old_hourly_document_gives_way_to_a_fresh_three_hourly_one():
    series = _client(datetime.timedelta(days=1)).get_hourly_precipitation_forecast()
    assert series == THREE_HOURLY_SERIES


def test_an_hourly_document_within_one_cache_lifetime_is_still_preferred():
    # Fetched half an hour before the three-hourly one: as current as the cache
    # allows, and the finer product. The calculation's forecast fetch follows an
    # update cycle by minutes; it must not swap the hourly series out.
    series = _client(datetime.timedelta(minutes=30)).get_hourly_precipitation_forecast()
    assert series == HOURLY_SERIES


def test_the_temperature_accessor_follows_the_same_rule():
    series = _client(datetime.timedelta(days=1)).get_hourly_temperature_forecast()
    assert series == [(datetime.datetime(2026, 9, 13, 6, tzinfo=UTC), 17.0)]


def test_documents_without_a_fetch_time_keep_the_hourly_preference():
    c = _client(datetime.timedelta(days=1))
    c._cached_hourly_at = None
    assert c.get_hourly_precipitation_forecast() == HOURLY_SERIES


def test_a_three_hourly_document_without_a_fetch_time_keeps_the_hourly_preference():
    c = _client(datetime.timedelta(days=1))
    c._cached_three_hourly_at = None
    assert c.get_hourly_precipitation_forecast() == HOURLY_SERIES


def test_on_a_daily_update_a_fresh_three_hourly_document_replaces_last_evening_hourly():
    # The daily-schedule case: hourly fetched 20:30 UTC on the 13th, three-hourly
    # 19:00 UTC on the 14th, a day-long cache. Within one lifetime of each other,
    # but the hourly series (T..T+48 h) may end before the next run's local date
    # does, so the guard would find the run date uncovered.
    age = datetime.timedelta(hours=22, minutes=30)
    series = _client(age, DAILY_UPDATE).get_hourly_precipitation_forecast()
    assert series == THREE_HOURLY_SERIES


@pytest.mark.parametrize(
    ("cache_seconds", "hourly_age", "expected"),
    [
        # A day-long lifetime is capped at three hours, the strict '>' kept.
        pytest.param(DAILY_UPDATE, 2 * 3600, HOURLY_SERIES, id="daily-2h"),
        pytest.param(DAILY_UPDATE, 3 * 3600, HOURLY_SERIES, id="daily-exactly-3h"),
        pytest.param(
            DAILY_UPDATE, 3 * 3600 + 1, THREE_HOURLY_SERIES, id="daily-3h-plus-1s"
        ),
        # A lifetime below the cap is the tolerance itself.
        pytest.param(HOURLY_UPDATE, 3599, HOURLY_SERIES, id="hourly-exactly-lifetime"),
        pytest.param(HOURLY_UPDATE, 3600, THREE_HOURLY_SERIES, id="hourly-lifetime+1s"),
        # Auto-update disabled: the 60 s cache floor is the lifetime.
        pytest.param(0, 30, HOURLY_SERIES, id="disabled-30s"),
        pytest.param(0, 90, THREE_HOURLY_SERIES, id="disabled-90s"),
    ],
)
def test_the_tolerance_is_one_cache_lifetime_at_most_three_hours(
    cache_seconds, hourly_age, expected
):
    c = _client(datetime.timedelta(seconds=hourly_age), cache_seconds)
    assert c.get_hourly_precipitation_forecast() == expected


def test_an_hourly_document_fetched_after_the_three_hourly_one_is_preferred():
    c = _client(datetime.timedelta(days=-1), DAILY_UPDATE)
    assert c.get_hourly_precipitation_forecast() == HOURLY_SERIES
