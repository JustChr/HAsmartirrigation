"""PirateWeatherClient.get_forecast_data: each day carries the span it covers.

Pirate Weather stamps each daily block with the UNIX time its local day begins,
so the span is that instant up to the next block's. The loop drops the first
(today) and the last block, which guarantees a next block exists for every day
it returns. That convention is taken from the API and has not been measured
against a live response.
"""

import datetime
import json
import pathlib
import zoneinfo
from unittest.mock import MagicMock, patch

from custom_components.irrigation_plus.const import (
    FORECAST_DAY_END,
    FORECAST_DAY_START,
    MAPPING_PRECIPITATION,
    MAPPING_TEMPERATURE,
)
from custom_components.irrigation_plus.weathermodules.PirateWeatherClient import (
    PirateWeatherClient,
)

_PATCH = (
    "custom_components.irrigation_plus.weathermodules.PirateWeatherClient._SESSION.get"
)

# Recorded from the live Pirate Weather API on 2026-09-16 for Berlin
# (52.52/13.41, the site the tests above already use), requested with
# ``extend=hourly``. Trimmed to the ``hourly``/``daily``/``currently`` keys
# PirateWeatherClient actually reads -- see PirateWeatherClient.py for which
# those are -- so a human can scan the whole thing; the 168 hourly and 8 daily
# entry counts are kept exactly, since they are what the tests below check.
_FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "pirate_weather_berlin.json"


def _block(start, precip_cm):
    return {
        "time": int(start.timestamp()),
        "windSpeed": 3.0,
        "pressure": 1013.0,
        "humidity": 0.6,
        "temperatureMax": 22.0,
        "temperatureMin": 12.0,
        "dewPoint": 9.0,
        "precipAccumulation": precip_cm,
    }


def test_entries_carry_the_span_of_their_day():
    utc = datetime.timezone.utc
    # Local midnights of a UTC+2 site are 22:00 UTC the evening before.
    starts = [
        datetime.datetime(2024, 5, 31, 22, 0, tzinfo=utc) + datetime.timedelta(days=i)
        for i in range(4)
    ]
    doc = {"daily": {"data": [_block(s, 0.1 * (i + 1)) for i, s in enumerate(starts)]}}
    response = MagicMock(status_code=200, text=json.dumps(doc))
    client = PirateWeatherClient("key", "1", 52.0, 5.0, 0)

    with patch(_PATCH, return_value=response):
        data = client.get_forecast_data()

    # blocks 1 and 2 are returned (today and the last block are dropped)
    assert [round(d[MAPPING_PRECIPITATION], 6) for d in data] == [2.0, 3.0]
    assert data[0][FORECAST_DAY_START] == starts[1]
    assert data[0][FORECAST_DAY_END] == starts[2]
    assert data[1][FORECAST_DAY_START] == starts[2]
    assert data[1][FORECAST_DAY_END] == starts[3]
    # UTC itself, not merely the same instant in the site's zone
    assert data[0][FORECAST_DAY_START].utcoffset() == datetime.timedelta(0)
    assert data[0][FORECAST_DAY_END].utcoffset() == datetime.timedelta(0)


def test_a_dst_day_spans_its_real_length():
    # The blocks above are exactly 24 h apart, so start + 1 day would pass them
    # too. Real local midnights are not: in Berlin, 2024-10-27 has 25 hours (the
    # clocks go back from CEST to CET), so its span ends 25 h after it starts.
    berlin = zoneinfo.ZoneInfo("Europe/Berlin")
    starts = [datetime.datetime(2024, 10, d, tzinfo=berlin) for d in (26, 27, 28, 29)]
    doc = {"daily": {"data": [_block(s, 0.1) for s in starts]}}
    response = MagicMock(status_code=200, text=json.dumps(doc))
    client = PirateWeatherClient("key", "1", 52.52, 13.41, 0)

    with patch(_PATCH, return_value=response):
        data = client.get_forecast_data()

    day = data[0]  # 2024-10-27, the day the clocks go back
    assert day[FORECAST_DAY_START] == starts[1]
    assert day[FORECAST_DAY_END] == starts[2]
    assert day[FORECAST_DAY_END] - day[FORECAST_DAY_START] == datetime.timedelta(
        hours=25
    )


def test_the_hourly_block_reaches_past_two_days():
    """Characterises the fixture, not the request: the fixture already has 168
    hourly entries, so this passes whether or not the client asks for them.
    ``test_the_request_asks_for_the_long_hourly_block`` below is what is red
    before the URL carries ``extend=hourly`` and green after."""
    doc = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    client = PirateWeatherClient("key", "1", 52.52, 13.41, 0)
    client._cached_doc = doc

    series = client.get_hourly_precipitation_forecast()

    span = series[-1][0] - series[0][0]
    assert span > datetime.timedelta(hours=48)


def test_the_request_asks_for_the_long_hourly_block():
    """Without ``extend=hourly`` Pirate Weather's default hourly block is 48
    entries, reaching only floor(fetch) + 47 h -- not enough to keep covering a
    rolling 24-hour window once the cached document is about a day old. This is
    the test the fixture-based one above cannot be: it fails on the request the
    client builds, not on a recorded response."""
    client = PirateWeatherClient("key", "1", 52.52, 13.41, 0)

    assert "extend=hourly" in client.url


def test_the_daily_mean_is_the_mean_of_the_extremes():
    """``max + min / 2.0`` is not ``(max + min) / 2.0`` -- issue #142.

    The two expressions agree only where ``temperatureMax`` is 0, so a pair with
    a non-zero maximum is what separates them. ``_block``'s 22/12 gives 17.0 for
    the mean and 28.0 for the precedence bug.
    """
    utc = datetime.timezone.utc
    starts = [
        datetime.datetime(2024, 5, 31, 22, 0, tzinfo=utc) + datetime.timedelta(days=i)
        for i in range(4)
    ]
    doc = {"daily": {"data": [_block(s, 0.1) for s in starts]}}
    response = MagicMock(status_code=200, text=json.dumps(doc))
    client = PirateWeatherClient("key", "1", 52.0, 5.0, 0)

    with patch(_PATCH, return_value=response):
        data = client.get_forecast_data()

    assert [d[MAPPING_TEMPERATURE] for d in data] == [17.0, 17.0]
