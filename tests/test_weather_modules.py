"""Test Smart Irrigation weather modules."""

import datetime
import json
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from custom_components.smart_irrigation.const import (
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
from custom_components.smart_irrigation.weathermodules.MetOfficeClient import (
    MetOfficeClient,
)
from custom_components.smart_irrigation.weathermodules.OpenMeteoClient import (
    OpenMeteoClient,
)
from custom_components.smart_irrigation.weathermodules.OWMClient import (
    OWMClient,
    _compute_dew_point,
)

_OWM_PATCH = "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get"
_OPENMETEO_PATCH = (
    "custom_components.smart_irrigation.weathermodules.OpenMeteoClient._SESSION.get"
)
_MET_PATCH = (
    "custom_components.smart_irrigation.weathermodules.MetOfficeClient._SESSION.get"
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
            "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get",
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
            "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get",
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
            "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, body),
        ):
            data = client.get_data()

        assert data[MAPPING_CURRENT_PRECIPITATION] == 0.0

    def test_http_error_raises(self):
        body = {"cod": 401, "message": "Invalid API key"}
        client = OWMClient(api_key="bad", latitude=52.0, longitude=5.0, elevation=0)
        with (
            patch(
                "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get",
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
            "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get",
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
            "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get",
            return_value=_make_response(200, body),
        ):
            data = client.get_forecast_data()

        # the 06-01 slot is "today" and excluded; only the 06-02 slot remains
        assert data is not None
        assert len(data) == 1
        assert data[0][MAPPING_TEMPERATURE] == pytest.approx(18.0)

    def test_empty_list_returns_none(self):
        body = {"cod": "200", "list": []}
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.smart_irrigation.weathermodules.OWMClient._SESSION.get",
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
