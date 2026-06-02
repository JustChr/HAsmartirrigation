"""Test Smart Irrigation weather modules."""

import datetime
import json
from unittest.mock import MagicMock, patch

import pytest

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
from custom_components.smart_irrigation.weathermodules.OWMClient import (
    OWMClient,
    _compute_dew_point,
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
            "custom_components.smart_irrigation.weathermodules.OWMClient.requests.get",
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
            "custom_components.smart_irrigation.weathermodules.OWMClient.requests.get",
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
            "custom_components.smart_irrigation.weathermodules.OWMClient.requests.get",
            return_value=_make_response(200, body),
        ):
            data = client.get_data()

        assert data[MAPPING_CURRENT_PRECIPITATION] == 0.0

    def test_http_error_raises(self):
        body = {"cod": 401, "message": "Invalid API key"}
        client = OWMClient(api_key="bad", latitude=52.0, longitude=5.0, elevation=0)
        with (
            patch(
                "custom_components.smart_irrigation.weathermodules.OWMClient.requests.get",
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

    @pytest.mark.skip(
        reason="datetime.datetime mock recurses (datetime.datetime.utcfromtimestamp "
        "self-references the patch); revive in Phase C (A6)"
    )
    def test_returns_daily_entries(self):
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with (
            patch(
                "custom_components.smart_irrigation.weathermodules.OWMClient.requests.get",
                return_value=_make_response(200, self._forecast_body()),
            ),
            patch(
                "custom_components.smart_irrigation.weathermodules.OWMClient.datetime.datetime"
            ) as mock_dt,
        ):
            mock_dt.utcnow.return_value = datetime.datetime(2024, 6, 1, 6, 0, 0)
            mock_dt.utcfromtimestamp.side_effect = datetime.datetime.utcfromtimestamp
            mock_dt.now.return_value = datetime.datetime(2024, 6, 1, 6, 0, 0)
            mock_dt.return_value = datetime.datetime(1900, 1, 1, 0, 0, 0)
            data = client.get_forecast_data()

        assert data is not None
        assert len(data) == 2
        assert data[0][MAPPING_TEMPERATURE] == pytest.approx(18.0)
        assert data[0][MAPPING_MIN_TEMP] == pytest.approx(14.0)
        assert data[0][MAPPING_MAX_TEMP] == pytest.approx(22.0)
        assert data[0][MAPPING_PRECIPITATION] == pytest.approx(1.2)

    @pytest.mark.skip(
        reason="datetime.datetime mock recurses (datetime.datetime.utcfromtimestamp "
        "self-references the patch); revive in Phase C (A6)"
    )
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
        with (
            patch(
                "custom_components.smart_irrigation.weathermodules.OWMClient.requests.get",
                return_value=_make_response(200, body),
            ),
            patch(
                "custom_components.smart_irrigation.weathermodules.OWMClient.datetime.datetime"
            ) as mock_dt,
        ):
            mock_dt.utcnow.return_value = datetime.datetime(2024, 6, 1, 6, 0, 0)
            mock_dt.utcfromtimestamp.side_effect = datetime.datetime.utcfromtimestamp
            mock_dt.now.return_value = datetime.datetime(2024, 6, 1, 6, 0, 0)
            mock_dt.return_value = datetime.datetime(1900, 1, 1, 0, 0, 0)
            data = client.get_forecast_data()

        assert data is not None
        assert len(data) == 1
        assert data[0][MAPPING_TEMPERATURE] == pytest.approx(18.0)

    def test_empty_list_returns_none(self):
        body = {"cod": "200", "list": []}
        client = OWMClient(api_key="k", latitude=52.0, longitude=5.0, elevation=0)
        with patch(
            "custom_components.smart_irrigation.weathermodules.OWMClient.requests.get",
            return_value=_make_response(200, body),
        ):
            assert client.get_forecast_data() is None
