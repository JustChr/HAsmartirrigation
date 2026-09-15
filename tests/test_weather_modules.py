"""Test Irrigation Plus weather modules."""

import datetime
import json
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from custom_components.irrigation_plus.const import (
    FORECAST_DAY_END,
    FORECAST_DAY_START,
    MAPPING_CURRENT_PRECIPITATION,
    MAPPING_DEWPOINT,
    MAPPING_HUMIDITY,
    MAPPING_MAX_TEMP,
    MAPPING_MIN_TEMP,
    MAPPING_PRECIPITATION,
    MAPPING_PRESSURE,
    MAPPING_TEMPERATURE,
    MAPPING_WINDSPEED,
    OBSERVATION_TIME,
)
from custom_components.irrigation_plus.weathermodules.MetOfficeClient import (
    MetOfficeClient,
)
from custom_components.irrigation_plus.weathermodules.OpenMeteoClient import (
    OpenMeteoClient,
)
from custom_components.irrigation_plus.weathermodules.OWMClient import (
    OWMClient,
    _compute_dew_point,
)

_OWM_PATCH = "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get"
_OPENMETEO_PATCH = (
    "custom_components.irrigation_plus.weathermodules.OpenMeteoClient._SESSION.get"
)
_MET_PATCH = (
    "custom_components.irrigation_plus.weathermodules.MetOfficeClient._SESSION.get"
)


def _make_response(status_code: int, body: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = json.dumps(body)
    return mock


class TestComputeDewPoint:
    def test_known_value(self):
        # 20 °C, 50 % RH → ~9.3 °C
        dp = _compute_dew_point(20.0, 50.0)
        assert 9.0 < dp < 10.0

    def test_saturation(self):
        # 100 % humidity → dew point == temperature
        dp = _compute_dew_point(15.0, 100.0)
        assert abs(dp - 15.0) < 0.1


class TestOWMClientInit:
    def test_defaults(self):
        client = OWMClient(api_key="mykey", latitude=52.0, longitude=5.0, elevation=10)
        assert client.api_key == "mykey"
        assert client.api_version == "2.5"
        assert client.latitude == 52.0
        assert client.elevation == 10

    def test_api_version_ignored(self):
        # Legacy callers may pass api_version; it must be silently ignored.
        client = OWMClient(api_key="k", api_version="3.0", latitude=1.0, longitude=1.0)
        assert client.api_version == "2.5"

    def test_strips_whitespace_from_key(self):
        client = OWMClient(api_key="  abc  ", latitude=0.0, longitude=0.0)
        assert client.api_key == "abc"


class TestOWMClientGetData:
    _CURRENT_BODY = {
        "cod": 200,
        "main": {"temp": 20.0, "humidity": 60, "pressure": 1013},
        "wind": {"speed": 5.0},
        "rain": {"1h": 0.5},
        "snow": {},
    }

    def test_success(self):
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, self._CURRENT_BODY),
        ):
            data = client.get_data()

        assert data[MAPPING_TEMPERATURE] == 20.0
        assert data[MAPPING_HUMIDITY] == 60
        assert data[MAPPING_CURRENT_PRECIPITATION] == pytest.approx(0.5)
        assert data[MAPPING_PRECIPITATION] == pytest.approx(0.5)
        assert MAPPING_DEWPOINT in data
        assert MAPPING_WINDSPEED in data

    def test_dew_point_computed(self):
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, self._CURRENT_BODY),
        ):
            data = client.get_data()

        expected_dp = _compute_dew_point(20.0, 60)
        assert data[MAPPING_DEWPOINT] == pytest.approx(expected_dp, abs=0.01)

    def test_no_rain_key(self):
        body = dict(self._CURRENT_BODY)
        body["rain"] = {}
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, body),
        ):
            data = client.get_data()

        assert data[MAPPING_CURRENT_PRECIPITATION] == 0.0

    def test_http_error_raises(self):
        body = {"cod": 401, "message": "Invalid API key"}
        client = OWMClient(api_key="bad", latitude=52.0, longitude=5.0, elevation=0)
        with (
            patch(
                "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get",
                return_value=_make_response(200, body),
            ),
            pytest.raises(OSError),
        ):
            client.get_data()


class TestOWMClientGetForecastData:
    # Fake "today" so the test is deterministic
    _TODAY = datetime.date(2024, 6, 1)
    _TOMORROW_TS = int(
        datetime.datetime(
            2024, 6, 2, 12, 0, 0, tzinfo=datetime.timezone.utc
        ).timestamp()
    )
    _DAY2_TS = int(
        datetime.datetime(
            2024, 6, 3, 12, 0, 0, tzinfo=datetime.timezone.utc
        ).timestamp()
    )

    def _forecast_body(self):
        def slot(ts):
            return {
                "dt": ts,
                "main": {
                    "temp": 18.0,
                    "temp_min": 14.0,
                    "temp_max": 22.0,
                    "humidity": 65,
                    "pressure": 1010,
                },
                "wind": {"speed": 3.0},
                "rain": {"3h": 1.2},
                "snow": {},
            }

        return {
            "cod": "200",
            "list": [slot(self._TOMORROW_TS), slot(self._DAY2_TS)],
        }

    @freeze_time("2024-06-01 06:00:00")
    def test_returns_daily_entries(self):
        # "today" is frozen to 2024-06-01; the forecast slots are 06-02 and 06-03,
        # so both are future days and get returned. freeze_time leaves
        # utcfromtimestamp() working on the real slot timestamps.
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, self._forecast_body()),
        ):
            data = client.get_forecast_data()

        assert data is not None
        assert len(data) == 2
        assert data[0][MAPPING_TEMPERATURE] == pytest.approx(18.0)
        assert data[0][MAPPING_MIN_TEMP] == pytest.approx(14.0)
        assert data[0][MAPPING_MAX_TEMP] == pytest.approx(22.0)
        assert data[0][MAPPING_PRECIPITATION] == pytest.approx(1.2)

    @freeze_time("2024-06-01 06:00:00")
    def test_today_excluded(self):
        today_ts = int(
            datetime.datetime(
                2024, 6, 1, 9, 0, 0, tzinfo=datetime.timezone.utc
            ).timestamp()
        )
        body = {
            "cod": "200",
            "list": [
                {
                    "dt": today_ts,
                    "main": {
                        "temp": 25.0,
                        "temp_min": 20.0,
                        "temp_max": 30.0,
                        "humidity": 50,
                        "pressure": 1013,
                    },
                    "wind": {"speed": 2.0},
                },
                {
                    "dt": self._TOMORROW_TS,
                    "main": {
                        "temp": 18.0,
                        "temp_min": 14.0,
                        "temp_max": 22.0,
                        "humidity": 65,
                        "pressure": 1010,
                    },
                    "wind": {"speed": 3.0},
                },
            ],
        }
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, body),
        ):
            data = client.get_forecast_data()

        # the 06-01 slot is "today" and excluded; only the 06-02 slot remains
        assert data is not None
        assert len(data) == 1
        assert data[0][MAPPING_TEMPERATURE] == pytest.approx(18.0)

    @freeze_time("2024-06-01 06:00:00")
    def test_entries_carry_their_utc_day(self):
        # OWM buckets its three-hourly slots by UTC calendar date, so each entry
        # covers UTC midnight to the next UTC midnight. The slots skip 06-03: a
        # span counted from the entry's position would give the second entry
        # 06-03, only the bucket's own date gives 06-04.
        utc = datetime.timezone.utc
        body = self._forecast_body()
        body["list"][1]["dt"] = int(
            datetime.datetime(2024, 6, 4, 12, tzinfo=utc).timestamp()
        )
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(_OWM_PATCH, return_value=_make_response(200, body)):
            data = client.get_forecast_data()

        assert data[0][FORECAST_DAY_START] == datetime.datetime(2024, 6, 2, tzinfo=utc)
        assert data[0][FORECAST_DAY_END] == datetime.datetime(2024, 6, 3, tzinfo=utc)
        assert data[1][FORECAST_DAY_START] == datetime.datetime(2024, 6, 4, tzinfo=utc)
        assert data[1][FORECAST_DAY_END] == datetime.datetime(2024, 6, 5, tzinfo=utc)
        # UTC itself, not merely the same instant in another zone
        assert data[0][FORECAST_DAY_START].utcoffset() == datetime.timedelta(0)

    def test_empty_list_returns_none(self):
        body = {"cod": "200", "list": []}
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.irrigation_plus.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, body),
        ):
            assert client.get_forecast_data() is None


class TestOWMClientCaching:
    """Re-fetched results are reused within the cache window (flood guard)."""

    _CURRENT_BODY = {
        "cod": 200,
        "main": {"temp": 20.0, "humidity": 60, "pressure": 1013},
        "wind": {"speed": 5.0},
        "rain": {"1h": 0.5},
        "snow": {},
    }

    def test_second_call_within_window_serves_cache(self):
        client = OWMClient(api_key="k", latitude=1.0, longitude=2.0, elevation=0)
        mock_get = MagicMock(return_value=_make_response(200, self._CURRENT_BODY))
        with patch(_OWM_PATCH, mock_get):
            first = client.get_data()
            second = client.get_data()
        assert first == second
        assert mock_get.call_count == 1  # second served from cache

    def test_override_cache_always_fetches(self):
        client = OWMClient(
            api_key="k", latitude=1.0, longitude=2.0, override_cache=True
        )
        mock_get = MagicMock(return_value=_make_response(200, self._CURRENT_BODY))
        with patch(_OWM_PATCH, mock_get):
            client.get_data()
            client.get_data()
        assert mock_get.call_count == 2

    def test_refetch_after_ttl_expires(self):
        client = OWMClient(api_key="k", latitude=1.0, longitude=2.0, elevation=0)
        mock_get = MagicMock(return_value=_make_response(200, self._CURRENT_BODY))
        with freeze_time("2024-06-01 12:00:00") as frozen, patch(_OWM_PATCH, mock_get):
            client.get_data()
            frozen.tick(delta=datetime.timedelta(seconds=61))
            client.get_data()
        assert mock_get.call_count == 2


def _openmeteo_doc(site_today, utc_offset_seconds):
    """A document in the shape Open-Meteo returns for this client's request URL.

    Modelled on a live response (``timezone=auto``, ``forecast_days=7``,
    ``past_days=1``): ``daily.time`` starts YESTERDAY at the site and runs for
    eight dates, and the hourly series starts at yesterday's local midnight with
    192 rows of local wall-clock time. The values are markers rather than
    weather: a day's precipitation is its day of the month and an hour's
    temperature is its local hour, so an assertion can tell which row was read.
    """
    first_day = site_today - datetime.timedelta(days=1)
    days = [first_day + datetime.timedelta(days=i) for i in range(8)]
    midnight = datetime.datetime(first_day.year, first_day.month, first_day.day)
    hours = [midnight + datetime.timedelta(hours=i) for i in range(192)]
    n_days, n_hours = len(days), len(hours)
    return {
        "latitude": 52.52,
        "longitude": 13.419998,
        "generationtime_ms": 0.25,
        "utc_offset_seconds": utc_offset_seconds,
        "timezone": "Etc/Test",
        "timezone_abbreviation": f"GMT{utc_offset_seconds // 3600:+d}",
        "elevation": 38.0,
        "hourly_units": {
            "time": "iso8601",
            "temperature_2m": "°C",
            "relative_humidity_2m": "%",
            "dew_point_2m": "°C",
            "precipitation": "mm",
            "wind_speed_10m": "m/s",
            "shortwave_radiation": "W/m²",
            "pressure_msl": "hPa",
        },
        "hourly": {
            "time": [h.strftime("%Y-%m-%dT%H:%M") for h in hours],
            "temperature_2m": [float(h.hour) for h in hours],
            "relative_humidity_2m": [60] * n_hours,
            "dew_point_2m": [8.0] * n_hours,
            "precipitation": [0.0] * n_hours,
            "wind_speed_10m": [3.0] * n_hours,
            "shortwave_radiation": [100.0] * n_hours,
            "pressure_msl": [1013.0] * n_hours,
        },
        "daily_units": {
            "time": "iso8601",
            "temperature_2m_max": "°C",
            "temperature_2m_min": "°C",
            "precipitation_sum": "mm",
            "wind_speed_10m_max": "m/s",
            "shortwave_radiation_sum": "MJ/m²",
        },
        "daily": {
            "time": [day.isoformat() for day in days],
            "temperature_2m_max": [22.0] * n_days,
            "temperature_2m_min": [12.0] * n_days,
            "precipitation_sum": [float(day.day) for day in days],
            "wind_speed_10m_max": [4.0] * n_days,
            "shortwave_radiation_sum": [15.0] * n_days,
        },
    }


class TestOpenMeteoClientGetForecastData:
    """The daily forecast starts tomorrow at the site, as the forecast contract says.

    The request asks for ``past_days=1`` so the intra-day estimate can reach
    back to the previous evening's calculation. That puts yesterday at index 0
    and today at index 1 of every daily array.
    """

    @freeze_time("2024-06-01 10:00:00")
    def test_the_first_forecast_day_is_tomorrow(self):
        client = OpenMeteoClient(latitude=52.52, longitude=13.41)
        doc = _openmeteo_doc(datetime.date(2024, 6, 1), 7200)
        with patch(_OPENMETEO_PATCH, return_value=_make_response(200, doc)):
            data = client.get_forecast_data()

        # The markers are days of the month: 05-31 and 06-01 are both left out.
        assert [d[MAPPING_PRECIPITATION] for d in data] == [
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
        ]

    @pytest.mark.parametrize(
        ("frozen_utc", "offset", "site_today", "tomorrow_marker"),
        [
            # 23:30 UTC is already 01:30 on the next day at UTC+2.
            ("2024-06-01 23:30:00", 7200, datetime.date(2024, 6, 2), 3.0),
            # 02:00 UTC is still 21:00 on the previous day at UTC-5.
            ("2024-06-02 02:00:00", -18000, datetime.date(2024, 6, 1), 2.0),
        ],
    )
    def test_today_is_the_date_at_the_site_not_in_utc(
        self, frozen_utc, offset, site_today, tomorrow_marker
    ):
        client = OpenMeteoClient(latitude=52.52, longitude=13.41)
        doc = _openmeteo_doc(site_today, offset)
        with (
            freeze_time(frozen_utc),
            patch(_OPENMETEO_PATCH, return_value=_make_response(200, doc)),
        ):
            data = client.get_forecast_data()

        assert data[0][MAPPING_PRECIPITATION] == tomorrow_marker

    def test_a_document_cached_past_the_site_midnight_still_starts_tomorrow(self):
        # Fetched late on 06-01 at the site and read at 00:30 on 06-02, so
        # daily.time now starts two days back. Only a filter on the date still
        # serves tomorrow first; skipping two positions would serve today.
        client = OpenMeteoClient(latitude=52.52, longitude=13.41)
        doc = _openmeteo_doc(datetime.date(2024, 6, 1), 7200)
        with (
            freeze_time("2024-06-01 22:30:00"),
            patch(_OPENMETEO_PATCH, return_value=_make_response(200, doc)),
        ):
            data = client.get_forecast_data()

        assert data[0][MAPPING_PRECIPITATION] == 3.0

    @pytest.mark.parametrize(
        ("offset", "day_start", "day_end"),
        [
            # 10:00 UTC is 12:00 on 06-01 at UTC+2, so tomorrow (06-02) starts
            # at 22:00 UTC the evening before.
            (
                7200,
                datetime.datetime(2024, 6, 1, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 6, 2, 22, tzinfo=datetime.timezone.utc),
            ),
            # 10:00 UTC is 05:00 on 06-01 at UTC-5, so tomorrow (06-02) starts
            # at 05:00 UTC that morning.
            (
                -18000,
                datetime.datetime(2024, 6, 2, 5, tzinfo=datetime.timezone.utc),
                datetime.datetime(2024, 6, 3, 5, tzinfo=datetime.timezone.utc),
            ),
        ],
    )
    def test_entries_carry_their_local_day(self, offset, day_start, day_end):
        # Open-Meteo reports daily values per LOCAL date (timezone=auto), so an
        # entry's day starts at local midnight, whose UTC instant depends on the
        # site's offset.
        client = OpenMeteoClient(latitude=52.52, longitude=13.41)
        doc = _openmeteo_doc(datetime.date(2024, 6, 1), offset)
        with (
            freeze_time("2024-06-01 10:00:00"),
            patch(_OPENMETEO_PATCH, return_value=_make_response(200, doc)),
        ):
            data = client.get_forecast_data()

        assert data[0][FORECAST_DAY_START] == day_start
        assert data[0][FORECAST_DAY_END] == day_end
        assert data[1][FORECAST_DAY_START] == data[0][FORECAST_DAY_END]
        # UTC itself, not merely the same instant in the site's zone
        assert data[0][FORECAST_DAY_START].utcoffset() == datetime.timedelta(0)

    def test_a_skipped_day_does_not_shift_the_next_span(self):
        # A day without wind is dropped. The entry after the gap still covers its
        # own date, so its span comes from that date, not from how many entries
        # were kept before it.
        client = OpenMeteoClient(latitude=52.52, longitude=13.41)
        doc = _openmeteo_doc(datetime.date(2024, 6, 1), 7200)
        # daily.time starts at 05-31, so index 3 is 06-03.
        doc["daily"]["wind_speed_10m_max"][3] = None
        with (
            freeze_time("2024-06-01 10:00:00"),
            patch(_OPENMETEO_PATCH, return_value=_make_response(200, doc)),
        ):
            data = client.get_forecast_data()

        # The markers are days of the month: 06-03 is gone.
        markers = [d[MAPPING_PRECIPITATION] for d in data]
        assert markers == [2.0, 4.0, 5.0, 6.0, 7.0]
        after_gap = data[markers.index(4.0)]
        # 06-04 starts at local midnight, 22:00 UTC the evening before at UTC+2.
        assert after_gap[FORECAST_DAY_START] == datetime.datetime(
            2024, 6, 3, 22, tzinfo=datetime.timezone.utc
        )
        assert after_gap[FORECAST_DAY_END] == datetime.datetime(
            2024, 6, 4, 22, tzinfo=datetime.timezone.utc
        )


class TestOpenMeteoClientGetData:
    """Current conditions come from the current hour at the site.

    The hourly series is local wall-clock time (``timezone=auto``), so the
    current hour can only be found with the document's own UTC offset.
    """

    @pytest.mark.parametrize(
        ("frozen_utc", "offset", "local_hour", "observed_utc"),
        [
            # 10:30 UTC is 12:30 at UTC+2; that hour's row began at 10:00 UTC.
            (
                "2024-06-01 10:30:00",
                7200,
                12.0,
                datetime.datetime(2024, 6, 1, 10, 0, tzinfo=datetime.timezone.utc),
            ),
            # 15:30 UTC is 10:30 at UTC-5; that hour's row began at 15:00 UTC.
            (
                "2024-06-01 15:30:00",
                -18000,
                10.0,
                datetime.datetime(2024, 6, 1, 15, 0, tzinfo=datetime.timezone.utc),
            ),
        ],
    )
    def test_reads_the_current_local_hour(
        self, frozen_utc, offset, local_hour, observed_utc
    ):
        client = OpenMeteoClient(latitude=52.52, longitude=13.41)
        doc = _openmeteo_doc(datetime.date(2024, 6, 1), offset)
        with (
            freeze_time(frozen_utc),
            patch(_OPENMETEO_PATCH, return_value=_make_response(200, doc)),
        ):
            data = client.get_data()

        # The marker is the row's local hour.
        assert data[MAPPING_TEMPERATURE] == local_hour
        assert data[OBSERVATION_TIME] == observed_utc

    def test_before_the_first_row_the_first_row_is_read(self):
        # With no row at or before now at the site, the earliest row is the
        # nearest one; the last row would be a week ahead.
        client = OpenMeteoClient(latitude=52.52, longitude=13.41)
        doc = _openmeteo_doc(datetime.date(2024, 6, 1), 7200)
        with (
            freeze_time("2024-05-30 12:00:00"),
            patch(_OPENMETEO_PATCH, return_value=_make_response(200, doc)),
        ):
            data = client.get_data()

        # Row 0 is 00:00 on 05-31 at UTC+2, which is 22:00 UTC on 05-30.
        assert data[MAPPING_TEMPERATURE] == 0.0
        assert data[OBSERVATION_TIME] == datetime.datetime(
            2024, 5, 30, 22, 0, tzinfo=datetime.timezone.utc
        )


class TestOpenMeteoClientCaching:
    """The single shared document serves every accessor from one fetch."""

    _DOC = {"hourly": {"time": []}, "daily": {"time": []}}

    def test_one_fetch_serves_all_accessors(self):
        client = OpenMeteoClient(latitude=1.0, longitude=2.0)
        mock_get = MagicMock(return_value=_make_response(200, self._DOC))
        with patch(_OPENMETEO_PATCH, mock_get):
            client.get_data()
            client.get_forecast_data()
            client.get_hourly_data()
        # current + forecast + hourly all come from one cached response
        assert mock_get.call_count == 1


def _met_doc(time_series):
    """Wrap a list of timeSeries steps in a Global Spot GeoJSON document."""
    return {
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [5.0, 52.0, 0]},
                "properties": {"timeSeries": time_series},
            }
        ]
    }


class TestMetOfficeClientInit:
    def test_strips_whitespace_from_key(self):
        client = MetOfficeClient(api_key="  ab cd  ", latitude=1.0, longitude=2.0)
        assert client.api_key == "abcd"

    def test_handles_none_key(self):
        # validate flow may construct with an empty/None key
        client = MetOfficeClient(api_key=None, latitude=1.0, longitude=2.0)
        assert client.api_key == ""


class TestMetOfficeClientGetData:
    _HOURLY = _met_doc(
        [
            {
                "time": "2024-06-01T11:00Z",
                "screenTemperature": 14.0,
                "screenDewPointTemperature": 9.0,
                "screenRelativeHumidity": 70.0,
                "windSpeed10m": 4.0,
                "mslp": 101000,
                "totalPrecipAmount": 0.0,
            },
            {
                "time": "2024-06-01T12:00Z",
                "screenTemperature": 18.0,
                "screenDewPointTemperature": 10.0,
                "screenRelativeHumidity": 60.0,
                "windSpeed10m": 5.0,
                "mslp": 101000,
                "totalPrecipAmount": 0.4,
            },
            {
                "time": "2024-06-01T13:00Z",
                "screenTemperature": 20.0,
                "screenDewPointTemperature": 11.0,
                "screenRelativeHumidity": 55.0,
                "windSpeed10m": 6.0,
                "mslp": 101000,
                "totalPrecipAmount": 0.0,
            },
        ]
    )

    @freeze_time("2024-06-01 12:30:00")
    def test_picks_current_hour(self):
        client = MetOfficeClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(_MET_PATCH, return_value=_make_response(200, self._HOURLY)):
            data = client.get_data()
        # most recent step at or before 12:30 is the 12:00 step
        assert data[MAPPING_TEMPERATURE] == 18.0
        assert data[MAPPING_DEWPOINT] == 10.0
        assert data[MAPPING_HUMIDITY] == 60.0
        assert data[MAPPING_CURRENT_PRECIPITATION] == pytest.approx(0.4)
        assert data[MAPPING_PRECIPITATION] == pytest.approx(0.4)
        # 10 m wind corrected down to 2 m
        assert data[MAPPING_WINDSPEED] < 5.0
        # mslp 101000 Pa at sea level → 1010 hPa
        assert data[MAPPING_PRESSURE] == pytest.approx(1010.0, abs=0.1)
        assert data[OBSERVATION_TIME].tzinfo is not None

    @freeze_time("2024-06-01 12:30:00")
    def test_missing_required_value_returns_none(self):
        bad = _met_doc(
            [
                {
                    "time": "2024-06-01T12:00Z",
                    "screenTemperature": 18.0,
                    # no dew point, humidity, wind, pressure
                }
            ]
        )
        client = MetOfficeClient(api_key="k", latitude=52.0, longitude=5.0)
        with patch(_MET_PATCH, return_value=_make_response(200, bad)):
            assert client.get_data() is None

    def test_empty_features_returns_none(self):
        client = MetOfficeClient(api_key="k", latitude=52.0, longitude=5.0)
        with patch(_MET_PATCH, return_value=_make_response(200, {"features": []})):
            assert client.get_data() is None


class TestMetOfficeClientGetForecastData:
    _THREE_HOURLY = _met_doc(
        [
            # today — must be skipped
            {
                "time": "2024-06-01T12:00Z",
                "maxScreenAirTemp": 19.0,
                "minScreenAirTemp": 12.0,
                "windSpeed10m": 5.0,
                "mslp": 101000,
                "screenRelativeHumidity": 60.0,
                "totalPrecipAmount": 0.2,
            },
            # tomorrow — two 3-hourly steps, aggregated into one day
            {
                "time": "2024-06-02T09:00Z",
                "maxScreenAirTemp": 21.0,
                "minScreenAirTemp": 13.0,
                "windSpeed10m": 4.0,
                "mslp": 101000,
                "screenRelativeHumidity": 65.0,
                "totalPrecipAmount": 1.0,
            },
            {
                "time": "2024-06-02T12:00Z",
                "maxScreenAirTemp": 24.0,
                "minScreenAirTemp": 15.0,
                "windSpeed10m": 6.0,
                "mslp": 101000,
                "screenRelativeHumidity": 55.0,
                "totalPrecipAmount": 0.5,
            },
        ]
    )

    @freeze_time("2024-06-01 12:30:00")
    def test_aggregates_to_daily_and_skips_today(self):
        client = MetOfficeClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(_MET_PATCH, return_value=_make_response(200, self._THREE_HOURLY)):
            fc = client.get_forecast_data()
        assert len(fc) == 1  # only 2024-06-02
        day = fc[0]
        assert day[MAPPING_MAX_TEMP] == 24.0  # max across the day's steps
        assert day[MAPPING_MIN_TEMP] == 13.0  # min across the day's steps
        assert day[MAPPING_TEMPERATURE] == pytest.approx((24.0 + 13.0) / 2.0)
        assert day[MAPPING_PRECIPITATION] == pytest.approx(1.5)  # summed
        # dew point derived from mean temp + mean humidity (Magnus)
        assert MAPPING_DEWPOINT in day
        assert day[MAPPING_DEWPOINT] < day[MAPPING_TEMPERATURE]
        assert MAPPING_PRESSURE in day

    @freeze_time("2024-06-01 12:30:00")
    def test_entries_carry_their_utc_day(self):
        # Met Office groups its three-hourly steps by UTC date, like OWM.
        client = MetOfficeClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(_MET_PATCH, return_value=_make_response(200, self._THREE_HOURLY)):
            fc = client.get_forecast_data()

        utc = datetime.timezone.utc
        assert fc[0][FORECAST_DAY_START] == datetime.datetime(2024, 6, 2, tzinfo=utc)
        assert fc[0][FORECAST_DAY_END] == datetime.datetime(2024, 6, 3, tzinfo=utc)

    @freeze_time("2024-06-01 12:30:00")
    def test_a_skipped_day_does_not_shift_the_next_entry(self):
        # A day without wind is skipped, so 06-04 becomes the second entry. A
        # span counted from the entry's position would give it 06-03; only the
        # grouped date gives 06-04.
        def step(time, **fields):
            base = {
                "time": time,
                "maxScreenAirTemp": 21.0,
                "minScreenAirTemp": 13.0,
                "windSpeed10m": 4.0,
                "totalPrecipAmount": 0.5,
            }
            base.update(fields)
            return {k: v for k, v in base.items() if v is not None}

        doc = _met_doc(
            [
                step("2024-06-02T12:00Z"),
                step("2024-06-03T12:00Z", windSpeed10m=None),
                step("2024-06-04T12:00Z"),
            ]
        )
        client = MetOfficeClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(_MET_PATCH, return_value=_make_response(200, doc)):
            fc = client.get_forecast_data()

        utc = datetime.timezone.utc
        assert len(fc) == 2
        assert fc[1][FORECAST_DAY_START] == datetime.datetime(2024, 6, 4, tzinfo=utc)
        assert fc[1][FORECAST_DAY_END] == datetime.datetime(2024, 6, 5, tzinfo=utc)
        # UTC itself, not merely the same instant in another zone
        assert fc[1][FORECAST_DAY_START].utcoffset() == datetime.timedelta(0)

    def test_empty_features_returns_none(self):
        client = MetOfficeClient(api_key="k", latitude=52.0, longitude=5.0)
        with patch(_MET_PATCH, return_value=_make_response(200, {"features": []})):
            assert client.get_forecast_data() is None


class TestMetOfficeClientValidateKey:
    def test_403_raises_oserror(self):
        client = MetOfficeClient(api_key="bad", latitude=1.0, longitude=2.0)
        with patch(_MET_PATCH, return_value=_make_response(403, {})), pytest.raises(
            OSError
        ):
            client.validate_key()

    def test_200_passes(self):
        client = MetOfficeClient(api_key="good", latitude=1.0, longitude=2.0)
        with patch(_MET_PATCH, return_value=_make_response(200, {})):
            client.validate_key()  # must not raise


class TestMetOfficeClientCaching:
    @freeze_time("2024-06-01 12:30:00")
    def test_separate_cache_per_endpoint(self):
        client = MetOfficeClient(api_key="k", latitude=1.0, longitude=2.0)
        mock_get = MagicMock(return_value=_make_response(200, _met_doc([])))
        with patch(_MET_PATCH, mock_get):
            client.get_data()  # hourly fetch
            client.get_data()  # served from hourly cache
            client.get_forecast_data()  # three-hourly fetch
            client.get_forecast_data()  # served from three-hourly cache
        # one call per distinct endpoint
        assert mock_get.call_count == 2
