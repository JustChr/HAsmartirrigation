"""Every weather client that carries hourly precipitation can hand it over.

The next-run projection subtracts the rain a run's decision point will already
have seen. Each client fetches a document that carries it; the accessor exposes
it without a second call, for the same reason the temperature one does.

The value handed back is a RATE in mm/h over the interval ENDING at each stamp,
not an accumulation. The four products report over different periods -- an hour,
three hours, the period following the step -- and normalising to a rate at the
client is what lets one consumer integrate all of them without knowing which it
is looking at.
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
        Read as UTC those rows land four or five hours out, so rain would be
        subtracted from a window it never fell in."""
        c = self._client(
            {
                "utc_offset_seconds": -4 * 3600,
                "hourly": {
                    "time": ["2026-06-21T08:00", "2026-06-21T09:00"],
                    "precipitation": [0.0, 1.4],
                },
            }
        )

        assert c.get_hourly_precipitation_forecast() == [
            (datetime.datetime(2026, 6, 21, 12, tzinfo=UTC), 0.0),
            (datetime.datetime(2026, 6, 21, 13, tzinfo=UTC), 1.4),
        ]

    def test_a_missing_amount_drops_only_its_own_row(self):
        c = self._client(
            {
                "utc_offset_seconds": 0,
                "hourly": {
                    "time": ["2026-06-21T08:00", "2026-06-21T09:00"],
                    "precipitation": [None, 1.4],
                },
            }
        )

        assert c.get_hourly_precipitation_forecast() == [
            (datetime.datetime(2026, 6, 21, 9, tzinfo=UTC), 1.4)
        ]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client(None).get_hourly_precipitation_forecast() is None


class TestMetOffice:
    def _client(self, hourly=None, three_hourly=None):
        c = MetOfficeClient(api_key="k", latitude=51.5, longitude=-0.1, elevation=10)
        c._cached_hourly = hourly
        c._cached_three_hourly = three_hourly
        return c

    def _doc(self, steps):
        return {"features": [{"properties": {"timeSeries": steps}}]}

    def test_the_total_is_stamped_at_the_end_of_the_period_it_covers(self):
        """``totalPrecipAmount`` covers the period FOLLOWING its step, and every
        other client reports over the period ending at its stamp. Left as-is the
        series would be an hour early against the rest."""
        c = self._client(
            hourly=self._doc(
                [
                    {"time": "2026-06-21T12:00Z", "totalPrecipAmount": 0.6},
                    {"time": "2026-06-21T13:00Z", "totalPrecipAmount": 1.2},
                ]
            )
        )

        assert c.get_hourly_precipitation_forecast() == [
            (BASE + datetime.timedelta(hours=1), 0.6),
            (BASE + datetime.timedelta(hours=2), 1.2),
        ]

    def test_the_three_hourly_product_is_divided_back_to_a_rate(self):
        """Counted as an hour's worth it would treble the water a coarser
        product predicts."""
        c = self._client(
            three_hourly=self._doc(
                [
                    {"time": "2026-06-21T12:00Z", "totalPrecipAmount": 3.0},
                    {"time": "2026-06-21T15:00Z", "totalPrecipAmount": 6.0},
                ]
            )
        )

        assert c.get_hourly_precipitation_forecast() == [
            (BASE + datetime.timedelta(hours=3), 1.0),
            (BASE + datetime.timedelta(hours=6), 2.0),
        ]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client().get_hourly_precipitation_forecast() is None


class TestOpenWeatherMap:
    def _client(self, doc):
        c = OWMClient(api_key="k", latitude=39.7, longitude=-84.1, elevation=311)
        c._cached_forecast_doc = doc
        return c

    def test_the_three_hour_accumulation_is_divided_back_to_a_rate(self):
        c = self._client(
            {
                "list": [
                    {"dt": _epoch(0), "rain": {"3h": 3.0}},
                    {"dt": _epoch(3), "rain": {"3h": 6.0}},
                ]
            }
        )

        assert c.get_hourly_precipitation_forecast() == [
            (BASE, 1.0),
            (BASE + datetime.timedelta(hours=3), 2.0),
        ]

    def test_snow_counts_as_water(self):
        c = self._client({"list": [{"dt": _epoch(0), "snow": {"3h": 3.0}}]})

        assert c.get_hourly_precipitation_forecast() == [(BASE, 1.0)]

    def test_a_dry_entry_is_coverage_rather_than_a_hole(self):
        """OWM omits the key entirely when nothing fell. Dropping the row would
        leave a gap the consumer refuses the whole series over."""
        c = self._client({"list": [{"dt": _epoch(0)}, {"dt": _epoch(3)}]})

        assert c.get_hourly_precipitation_forecast() == [
            (BASE, 0.0),
            (BASE + datetime.timedelta(hours=3), 0.0),
        ]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client(None).get_hourly_precipitation_forecast() is None


class TestPirateWeather:
    def _client(self, doc):
        c = PirateWeatherClient(
            api_key="k", api_version="1", latitude=39.7, longitude=-84.1, elevation=311
        )
        c._cached_doc = doc
        return c

    def test_the_intensity_is_already_a_rate(self):
        c = self._client(
            {
                "hourly": {
                    "data": [
                        {"time": _epoch(0), "precipIntensity": 0.0},
                        {"time": _epoch(1), "precipIntensity": 2.5},
                    ]
                }
            }
        )

        assert c.get_hourly_precipitation_forecast() == [
            (BASE, 0.0),
            (BASE + datetime.timedelta(hours=1), 2.5),
        ]

    def test_nothing_fetched_yet_is_not_an_error(self):
        assert self._client(None).get_hourly_precipitation_forecast() is None


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
    """The caller distinguishes "no forecast" from "a forecast that covers the
    span", and an empty list would read as the second."""
    setattr(client, attr, {})

    assert client.get_hourly_precipitation_forecast() is None
