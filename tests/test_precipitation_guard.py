"""The precipitation skip guard examines the run's own date.

Rebuilt from the case reported in #137, in Europe/Berlin. Forecast: 2.15 mm on
the 13th, window 1 day, threshold 2 mm. The guard used to read the day AFTER the
run: it skipped the dry 12th for the 13th's rain and let the 13th water, because
by then it was looking at the 14th.

The zone is set by the ``berlin`` fixture, which each test requests by name. The
repo's autouse fixtures hand every test a ``hass`` that sets US/Pacific, and a
fixture running before it would be overwritten.
"""

import datetime
import logging
import zoneinfo
from types import SimpleNamespace
from unittest.mock import Mock, patch

import homeassistant.util.dt as dt_util
import pytest
import requests
from freezegun import freeze_time

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.skip_conditions import SKIP_PRECIPITATION
from custom_components.irrigation_plus.weathermodules import OWMClient as owm_module

UTC = datetime.timezone.utc
BERLIN = zoneinfo.ZoneInfo("Europe/Berlin")


@pytest.fixture
def berlin():
    original = dt_util.DEFAULT_TIME_ZONE
    dt_util.set_default_time_zone(BERLIN)
    try:
        yield
    finally:
        dt_util.set_default_time_zone(original)


def _local(*args):
    return datetime.datetime(*args, tzinfo=BERLIN).astimezone(UTC)


# The reported forecast's rain on the 13th, in the hour ending 14:00 local.
AFTERNOON = _local(2026, 9, 13, 14, 0)
# Rain in the first hour of the 13th: 00:00-01:00 local is 22:00-23:00 UTC on the
# 12th, so only Home Assistant's zone puts it on the run's date.
FIRST_LOCAL_HOUR = _local(2026, 9, 13, 1, 0)


def _forecast_days(rain_on):
    """UTC-day entries after today's UTC date, as OWM builds them."""
    today = dt_util.utcnow().date()
    out = []
    for d in (12, 13, 14, 15):
        start = datetime.datetime(2026, 9, d, tzinfo=UTC)
        if start.date() <= today:
            continue
        out.append(
            {
                const.FORECAST_DAY_START: start,
                const.FORECAST_DAY_END: start + datetime.timedelta(days=1),
                const.MAPPING_PRECIPITATION: 2.15 if start.date() == rain_on else 0.0,
            }
        )
    return out


def _hourly(rain_ending_at):
    """Hourly stamps from the local 12th to the local 15th, with one rainy hour."""
    first = _local(2026, 9, 12, 0, 0)
    out = []
    for h in range(1, 73):
        stamp = first + datetime.timedelta(hours=h)
        out.append((stamp, 2.15 if stamp == rain_ending_at else 0.0))
    return out


def _client(rain_ending_at=AFTERNOON):
    rain_on = (rain_ending_at - datetime.timedelta(hours=1)).date()
    return SimpleNamespace(
        get_forecast_data=lambda: _forecast_days(rain_on),
        get_hourly_precipitation_forecast=lambda: _hourly(rain_ending_at),
    )


def _daily_only_client():
    return SimpleNamespace(get_forecast_data=lambda: _forecast_days(AFTERNOON.date()))


def _coordinator(client):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()

    async def run_executor(func, *args):
        return func(*args)

    hass.async_add_executor_job = run_executor
    coord.hass = hass
    coord._WeatherServiceClient = client
    return coord


def _config(enabled=True, days=1):
    return {
        const.CONF_SKIP_IRRIGATION_ON_PRECIPITATION: enabled,
        const.CONF_PRECIPITATION_THRESHOLD_MM: 2,
        const.CONF_PRECIPITATION_FORECAST_DAYS: days,
        const.CONF_USE_WEATHER_SERVICE: True,
    }


async def test_the_dry_day_before_the_rain_is_not_skipped(berlin):
    with freeze_time(_local(2026, 9, 12, 6, 19)):
        result = await _coordinator(_client())._eval_precipitation(_config())
    assert result["id"] == SKIP_PRECIPITATION
    assert result["available"] is True
    assert result["observed"] == 0.0
    assert result["would_skip"] is False


async def test_the_rain_day_itself_is_skipped(berlin):
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        result = await _coordinator(_client())._eval_precipitation(_config())
    assert result["observed"] == 2.15
    assert result["would_skip"] is True


async def test_the_evening_outlook_for_tomorrow_looks_at_tomorrow(berlin):
    with freeze_time(_local(2026, 9, 12, 20, 0)):
        result = await _coordinator(_client())._eval_precipitation(
            _config(), _local(2026, 9, 13, 6, 20)
        )
    assert result["observed"] == 2.15
    assert result["would_skip"] is True


async def test_rain_in_the_first_local_hour_is_not_on_the_day_before(berlin):
    with freeze_time(_local(2026, 9, 12, 6, 19)):
        result = await _coordinator(_client(FIRST_LOCAL_HOUR))._eval_precipitation(
            _config()
        )
    assert (result["observed"], result["would_skip"]) == (0.0, False)


async def test_rain_in_the_first_local_hour_counts_for_the_run_date(berlin):
    with freeze_time(_local(2026, 9, 12, 20, 0)):
        result = await _coordinator(_client(FIRST_LOCAL_HOUR))._eval_precipitation(
            _config(), _local(2026, 9, 13, 6, 20)
        )
    assert (result["observed"], result["would_skip"]) == (2.15, True)


@pytest.mark.parametrize(
    ("days", "observed", "would_skip"), [(1, 0.0, False), (2, 2.15, True)]
)
async def test_an_evening_run_with_a_one_day_window_sees_only_the_rest_of_its_day(
    berlin, days, observed, would_skip
):
    # Chosen on #137: the window is the run's own date. A run starting at 21:00
    # sees three hours with one day and the next morning's rain only with two.
    # Pinned so that a change to it is deliberate.
    with freeze_time(_local(2026, 9, 13, 21, 0)):
        result = await _coordinator(
            _client(_local(2026, 9, 14, 6, 0))
        )._eval_precipitation(_config(days=days))
    assert (result["observed"], result["would_skip"]) == (observed, would_skip)


@pytest.mark.parametrize(
    ("rainy_hours", "rate", "threshold"), [(10, 0.2, 2), (1, 0.49, 0.49)]
)
async def test_rain_adding_up_to_the_threshold_skips_as_the_dashboard_shows_it(
    berlin, rainy_hours, rate, threshold
):
    # Integrated per second, ten hours of 0.2 mm come to 1.9999999999999998 and
    # one hour of 0.49 mm to 0.48999999999999994. The dashboard shows each as the
    # threshold itself, so the run has to skip.
    rainy = {_local(2026, 9, 13, 8 + h, 0) for h in range(rainy_hours)}
    series = [(stamp, rate if stamp in rainy else 0.0) for stamp, _ in _hourly(None)]
    client = SimpleNamespace(
        get_forecast_data=lambda: _forecast_days(None),
        get_hourly_precipitation_forecast=lambda: series,
    )
    config = _config() | {const.CONF_PRECIPITATION_THRESHOLD_MM: threshold}
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        result = await _coordinator(client)._eval_precipitation(config)
    assert (result["observed"], result["would_skip"]) == (threshold, True)


async def test_a_client_without_an_hourly_series_cannot_decide_the_run_date(berlin):
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        result = await _coordinator(_daily_only_client())._eval_precipitation(_config())
    assert result["available"] is False
    assert result["would_skip"] is False


async def test_a_failed_refresh_does_not_decide_on_the_last_documents_series(berlin):
    # Every client returns no daily forecast when its refresh fails but keeps the
    # document of its last success, and the hourly accessor reads that one.
    # Deciding on it would skip on a forecast of any age.
    client = SimpleNamespace(
        get_forecast_data=lambda: None,
        get_hourly_precipitation_forecast=lambda: _hourly(AFTERNOON),
    )
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        result = await _coordinator(client)._eval_precipitation(_config())
    assert result["available"] is False
    assert result["would_skip"] is False


async def test_a_real_client_whose_refresh_fails_leaves_the_guard_undecided(berlin):
    # The premise of the test above, with OWM itself: the failed request yields no
    # daily forecast, while the hourly accessor still reads the old document,
    # which forecasts 30 mm over the run's late morning.
    client = owm_module.OWMClient(api_key="k", latitude=50.0, longitude=7.0)
    first = datetime.datetime(2026, 9, 12, 0, 0, tzinfo=UTC)
    client._cached_forecast_doc = {
        "cod": "200",
        "list": [
            {"dt": int((first + datetime.timedelta(hours=3 * k)).timestamp())}
            | ({"rain": {"3h": 30.0}} if k == 12 else {})
            for k in range(17)
        ],
    }
    offline = requests.ConnectionError("offline")
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        with patch.object(owm_module._SESSION, "get", side_effect=offline):
            assert client.get_forecast_data() is None
            assert client.get_hourly_precipitation_forecast()
            result = await _coordinator(client)._eval_precipitation(_config())
    assert result["available"] is False
    assert result["would_skip"] is False


async def test_at_dispatch_an_uncovered_run_date_is_logged_at_info(berlin, caplog):
    # The guard then sits the run out, and nothing in the dashboard shows it.
    caplog.set_level(
        logging.DEBUG, logger="custom_components.irrigation_plus.skip_conditions"
    )
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        await _coordinator(_daily_only_client())._eval_precipitation(_config())
    levels = [
        r.levelno
        for r in caplog.records
        if "does not cover the run's date" in r.getMessage()
    ]
    assert levels == [logging.INFO]


async def test_a_preview_logs_an_uncovered_run_date_at_debug(berlin, caplog):
    # A preview names its run and repeats on every refresh, so the same gap would
    # fill the log at info.
    caplog.set_level(
        logging.DEBUG, logger="custom_components.irrigation_plus.skip_conditions"
    )
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        await _coordinator(_daily_only_client())._eval_precipitation(
            _config(), _local(2026, 9, 13, 6, 20)
        )
    levels = [
        r.levelno
        for r in caplog.records
        if "does not cover the run's date" in r.getMessage()
    ]
    assert levels == [logging.DEBUG]


async def test_a_window_whose_later_days_are_partly_covered_still_decides(
    berlin, caplog
):
    # Only an uncovered run date stops the decision. A window reaching past the
    # forecast decides on the rain it has and says so at debug.
    caplog.set_level(
        logging.DEBUG, logger="custom_components.irrigation_plus.skip_conditions"
    )
    # 36 dry hours from local 13th 00:00 (12th 22:00Z): the 13th and the first
    # twelve hours of the local 14th.
    first = _local(2026, 9, 13, 0, 0)
    series = [(first + datetime.timedelta(hours=h), 0.0) for h in range(1, 37)]
    assert series[-1][0] == datetime.datetime(2026, 9, 14, 10, 0, tzinfo=UTC)

    def utc_day(day, mm):
        start = datetime.datetime(2026, 9, day, tzinfo=UTC)
        return {
            const.FORECAST_DAY_START: start,
            const.FORECAST_DAY_END: start + datetime.timedelta(days=1),
            const.MAPPING_PRECIPITATION: mm,
        }

    # Days filed by UTC date, as OWM files them. The 14th starts at 00:00Z, before
    # the series ends at 10:00Z, and is left out; the 15th starts after it.
    client = SimpleNamespace(
        get_forecast_data=lambda: [utc_day(14, 0.0), utc_day(15, 5.0)],
        get_hourly_precipitation_forecast=lambda: series,
    )
    with freeze_time(_local(2026, 9, 13, 6, 20)):
        result = await _coordinator(client)._eval_precipitation(_config(days=3))
    # The UTC 15th spans 15th 00:00Z-16th 00:00Z, the local 15th 14th 22:00Z-15th
    # 22:00Z. They share 22 of the entry's 24 hours: 5 mm * 22 / 24 = 4.5833 mm,
    # shown as 4.58. The local 14th ends at 14th 22:00Z and gets none of it.
    assert result["available"] is True
    assert result["would_skip"] is True
    assert result["observed"] == 4.58
    levels = [
        r.levelno for r in caplog.records if "covers only part of the" in r.getMessage()
    ]
    assert levels == [logging.DEBUG]


async def test_disabled_is_a_noop():
    result = await _coordinator(_client())._eval_precipitation(_config(enabled=False))
    assert result["enabled"] is False
    assert result["available"] is False
    assert result["would_skip"] is False


async def test_no_weather_client_is_unavailable():
    result = await _coordinator(None)._eval_precipitation(_config())
    assert result["available"] is False
    assert result["would_skip"] is False
