"""PirateWeatherClient.get_forecast_data: each day carries the span it covers.

Pirate Weather stamps each daily block with the UNIX time its local day begins,
so the span is that instant up to the next block's. The loop drops the first
(today) and the last block, which guarantees a next block exists for every day
it returns. That convention is taken from the API and has not been measured
against a live response.
"""

import datetime
import json
import zoneinfo
from unittest.mock import MagicMock, patch

from custom_components.irrigation_plus.const import (
    FORECAST_DAY_END,
    FORECAST_DAY_START,
    MAPPING_PRECIPITATION,
)
from custom_components.irrigation_plus.weathermodules.PirateWeatherClient import (
    PirateWeatherClient,
)

_PATCH = (
    "custom_components.irrigation_plus.weathermodules.PirateWeatherClient._SESSION.get"
)


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
