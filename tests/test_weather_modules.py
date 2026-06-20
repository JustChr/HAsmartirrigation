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
    MAPPING_TEMPERATURE,
    MAPPING_WINDSPEED,
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
