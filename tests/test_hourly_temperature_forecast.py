"""Every weather client that carries hourly temperatures can hand them over.

The composed window fills a calculation window's remaining hours from the
configured service's own temperature series. Each client already fetches a
document that contains one; the accessor exposes it without a second call,
because the live estimate asks every minute per zone and that path adds no
external polling of its own.

The instant is what is handed back, not a wall-clock string: three of these four
products stamp in UTC and one in the site's local zone, and leaving each caller
to rediscover which would put a window's extremes hours out.
"""

import datetime

import pytest

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

UTC = datetime.timezone.utc
BASE = datetime.datetime(2026, 6, 21, 12, 0, tzinfo=UTC)


def _epoch(hours):
    return int((BASE + datetime.timedelta(hours=hours)).timestamp())


class TestOpenMeteo:
    def _client(self, doc):
        c = OpenMeteoClient(latitude=39.7, longitude=-84.1, elevation=311)
        c._cached_doc = doc
        return c

    def test_the_local_series_comes_back_as_absolute_instants(self):
        """Open-Meteo stamps in the site's own wall clock (``timezone=auto``).
        Read as UTC those rows land four or five hours out, which moves a
        window's peak into the wrong window entirely."""
        c = self._client(
            {
                "utc_offset_seconds": -4 * 3600,
                "hourly": {
                    "time": ["2026-06-21T08:00", "2026-06-21T09:00"],
                    "temperature_2m": [18.0, 20.0],
                },
            }
        )

        assert c.get_hourly_temperature_forecast() == [
            (datetime.datetime(2026, 6, 21, 12, tzinfo=UTC), 18.0),
            (datetime.datetime(2026, 6, 21, 13, tzinfo=UTC), 20.0),
        ]

    def test_a_missing_temperature_drops_only_its_own_row(self):
        c = self._client(
            {
                "utc_offset_seconds": 0,
                "hourly": {
                    "time": ["2026-06-21T08:00", "2026-06-21T09:00"],
                    "temperature_2m": [None, 20.0],
                },
            }
        )

        assert c.get_hourly_temperature_forecast() == [
            (datetime.datetime(2026, 6, 21, 9, tzinfo=UTC), 20.0)
        ]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client(None).get_hourly_temperature_forecast() is None


class TestMetOffice:
    def _client(self, hourly=None, three_hourly=None):
        c = MetOfficeClient(api_key="k", latitude=51.5, longitude=-0.1, elevation=10)
        c._cached_hourly = hourly
        c._cached_three_hourly = three_hourly
        return c

    def _doc(self, steps):
        return {"features": [{"properties": {"timeSeries": steps}}]}

    def test_the_hourly_product_is_read_in_order(self):
        c = self._client(
            hourly=self._doc(
                [
                    {"time": "2026-06-21T12:00Z", "screenTemperature": 17.5},
                    {"time": "2026-06-21T13:00Z", "screenTemperature": 18.5},
                ]
            )
        )

        assert c.get_hourly_temperature_forecast() == [
            (BASE, 17.5),
            (BASE + datetime.timedelta(hours=1), 18.5),
        ]

    def test_the_three_hourly_product_stands_in_when_it_is_all_there_is(self):
        """get_data populates the hourly document, but a configuration that has
        only ever asked for a forecast has the coarser one. Still far better at
        placing the window's extremes than reading them off the observation."""
        c = self._client(
            three_hourly=self._doc(
                [{"time": "2026-06-21T12:00Z", "screenTemperature": 17.5}]
            )
        )

        assert c.get_hourly_temperature_forecast() == [(BASE, 17.5)]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client().get_hourly_temperature_forecast() is None


class TestOpenWeatherMap:
    def _client(self, doc):
        c = OWMClient(api_key="k", latitude=39.7, longitude=-84.1, elevation=311)
        c._cached_forecast_doc = doc
        return c

    def test_the_three_hourly_entries_survive_the_daily_roll_up(self):
        """get_forecast_data folds these into calendar days, which loses the
        intra-day shape the composed window needs. The raw document is kept for
        exactly that reason."""
        c = self._client(
            {
                "list": [
                    {"dt": _epoch(0), "main": {"temp": 21.0}},
                    {"dt": _epoch(3), "main": {"temp": 24.0}},
                ]
            }
        )

        assert c.get_hourly_temperature_forecast() == [
            (BASE, 21.0),
            (BASE + datetime.timedelta(hours=3), 24.0),
        ]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client(None).get_hourly_temperature_forecast() is None


class TestPirateWeather:
    def _client(self, doc):
        c = PirateWeatherClient(
            api_key="k", api_version="1", latitude=39.7, longitude=-84.1, elevation=311
        )
        c._cached_doc = doc
        return c

    def test_the_hourly_block_is_read(self):
        c = self._client(
            {
                "hourly": {
                    "data": [
                        {"time": _epoch(0), "temperature": 21.0},
                        {"time": _epoch(1), "temperature": 22.0},
                    ]
                }
            }
        )

        assert c.get_hourly_temperature_forecast() == [
            (BASE, 21.0),
            (BASE + datetime.timedelta(hours=1), 22.0),
        ]

    def test_the_request_asks_for_the_hourly_block(self):
        """It was excluded outright, so there was nothing to read. A daily high
        and low cannot supply a window's remaining hours -- measured, that
        construction does not converge."""
        c = self._client(None)

        assert "hourly" not in c.url.split("exclude=")[1]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client(None).get_hourly_temperature_forecast() is None


@pytest.mark.parametrize(
    ("client", "attr"),
    [
        (OpenMeteoClient(latitude=1, longitude=1, elevation=0), "_cached_doc"),
        (
            PirateWeatherClient(
                api_key="k", api_version="1", latitude=1, longitude=1, elevation=0
            ),
            "_cached_doc",
        ),
        (
            OWMClient(api_key="k", latitude=1, longitude=1, elevation=0),
            "_cached_forecast_doc",
        ),
    ],
)
def test_an_empty_document_reports_nothing_rather_than_an_empty_series(client, attr):
    """The caller distinguishes "no source" from "a source that covers the
    window", and an empty list would read as the second."""
    setattr(client, attr, {})

    assert client.get_hourly_temperature_forecast() is None
