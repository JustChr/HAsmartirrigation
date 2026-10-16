"""A pausing sensor group's commit in the hourly form of the calculation.

The hourly rows charge each hour only for its measured time, so the summed ET is
already the booked part; it is not scaled a second time. The share the
explanation names is the time in which every field of the form that ran was
measured -- temperature, humidity, wind and the sun for the hourly form, the
daily form's own fields when it runs instead. The replayed balance still runs
under a blocked rain rate.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util
import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus import calculation as calculation_module
from custom_components.irrigation_plus.calculation import required_sensor_fields
from custom_components.irrigation_plus.et_estimate import eto_hourly_series
from custom_components.irrigation_plus.store import SmartIrrigationStorage
from custom_components.irrigation_plus.weather_aggregate import (
    HOURLY_ROW_REQUIRED,
    build_hourly_rows,
)

T0 = datetime.datetime(2026, 6, 21, 0, 0, 0)
NOW = T0 + timedelta(hours=24)
H = timedelta(hours=1)
M = timedelta(minutes=1)
LAT, LON, ELEV = 39.68987, -84.07865, 311.0
T = const.MAPPING_TEMPERATURE
RH = const.MAPPING_HUMIDITY
SUN = const.MAPPING_SOLRAD
RAIN = const.MAPPING_PRECIPITATION
RATE = {RAIN: {const.MAPPING_CONF_AGGREGATE: const.MAPPING_CONF_AGGREGATE_RIEMANNSUM}}
HOURLY_SENTENCE = "sum of hourly FAO-56 et0"


def _offset_h():
    offset = dt_util.now().utcoffset()
    return offset.total_seconds() / 3600.0 if offset else 0.0


def _readings(*, rain=None):
    out = []
    stamp = T0
    while stamp < NOW:
        hour = stamp.hour + stamp.minute / 60
        row = {
            const.RETRIEVED_AT: stamp,
            T: 18.0 + 6 * (1 - abs(hour - 14) / 14),
            RH: 65.0,
            const.MAPPING_WINDSPEED: 2.0,
            SUN: max(0.0, 700.0 * (1 - abs(hour - 13) / 7)) * 0.0864,
            const.MAPPING_DEWPOINT: 10.0,
            const.MAPPING_PRESSURE: 1005.0,
        }
        if rain is not None:
            row[RAIN] = rain(stamp)
        out.append(row)
        stamp += 10 * M
    return out


@pytest.fixture
async def coordinator(hass):
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    c._effective_latitude = LAT
    c._effective_longitude = LON
    c._effective_elevation = ELEV
    await store.async_update_config(
        {const.CONF_CONTINUOUS_UPDATES: True, const.CONF_HOURLY_CALCULATION: True}
    )
    return c, store


async def _zone(c, store, readings, *, config=None, solrad="3", daily_et=5.0):
    mapping = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "Garden",
            const.MAPPING_MAPPINGS: config or {},
            const.MAPPING_DATA: readings,
        }
    )
    module = await store.async_create_module(
        {const.MODULE_NAME: "PyETO", "description": "", "config": {}}
    )
    instance = Mock()
    instance.calculate = Mock(return_value=-daily_et)
    instance._solrad_behavior = solrad
    instance.forecast_days = 0
    c.getModuleInstanceByID = AsyncMock(return_value=instance)
    return await store.async_create_zone(
        {
            const.ZONE_NAME: "Front",
            const.ZONE_MAPPING: mapping[const.MAPPING_ID],
            const.ZONE_MODULE: module[const.MODULE_ID],
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_BUCKET: 0.0,
            const.ZONE_MAXIMUM_BUCKET: 25.4,
            const.ZONE_DRAINAGE_RATE: 0.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_MAXIMUM_DURATION: 3600,
            const.ZONE_LEAD_TIME: 0,
            const.ZONE_LAST_CONSUMED: T0,
        }
    )


async def _commit(c, zone, blocked=None):
    weatherdata, _ = await c._aggregate_for_zone(zone, now=NOW, blocked=blocked)
    return await c.calculate_module(zone, weatherdata, None, now=NOW, blocked=blocked)


def _recording_substeps(monkeypatch):
    """The sub-steps each commit's replay is handed, one entry per commit."""
    seen = []
    real = calculation_module.build_substeps

    def recording(*args, **kwargs):
        steps = real(*args, **kwargs)
        seen.append(steps)
        return steps

    monkeypatch.setattr(calculation_module, "build_substeps", recording)
    return seen


def _inside(steps, lo, hi):
    """Indices of the steps lying inside ``[lo, hi)``, counted from ``T0``."""
    out, start = [], T0
    for i, step in enumerate(steps):
        end = start + timedelta(hours=step.dt_hours)
        if lo <= start and end <= hi:
            out.append(i)
        start = end
    return out


def _summed(readings, blocked, config=None):
    rows = build_hourly_rows(
        readings,
        T0,
        config or {},
        now=NOW,
        latitude=LAT,
        longitude=LON,
        elevation=ELEV,
        tz_offset_h=_offset_h(),
        tz=dt_util.DEFAULT_TIME_ZONE,
        blocked=blocked,
    )
    return sum(eto_hourly_series(rows, LAT, LON, _offset_h(), ELEV))


class TestTheFieldsEachFormNeeds:
    def test_the_hourly_form_needs_temperature_humidity_wind_and_sun(self):
        assert required_sensor_fields("PyETO", hourly=True) == HOURLY_ROW_REQUIRED

    def test_the_daily_form_and_passthrough_keep_theirs(self):
        assert set(required_sensor_fields("PyETO")) == {
            const.MAPPING_DEWPOINT,
            T,
            const.MAPPING_WINDSPEED,
            const.MAPPING_PRESSURE,
        }
        assert required_sensor_fields("Passthrough") == (
            const.MAPPING_EVAPOTRANSPIRATION,
        )
        assert required_sensor_fields("Passthrough", hourly=True) == (
            const.MAPPING_EVAPOTRANSPIRATION,
        )
        assert required_sensor_fields("Static") is None


class TestTheHourlyForm:
    async def test_it_books_the_rows_once_and_names_the_share(self, coordinator):
        c, store = coordinator
        readings = _readings()
        zone = await _zone(c, store, readings)
        blocked = {T: ((T0 + 10 * H, T0 + 12 * H),)}
        data = await _commit(c, zone, blocked)
        expected = _summed(readings, blocked)
        assert expected < _summed(readings, None)
        assert data[const.ZONE_DELTA] == pytest.approx(-expected, abs=1e-9)
        explanation = data[const.ZONE_EXPLANATION]
        assert HOURLY_SENTENCE in explanation
        assert "Evapotranspiration booked for 92 % of the period." in explanation

    async def test_a_required_field_silent_throughout_books_nothing(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, _readings())
        data = await _commit(c, zone, {SUN: ((T0, NOW),)})
        assert data[const.ZONE_DELTA] == 0.0
        assert HOURLY_SENTENCE in data[const.ZONE_EXPLANATION]
        assert "booked for 0 % of the period" in data[const.ZONE_EXPLANATION]

    async def test_humidity_counts_in_the_hourly_form(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, _readings())
        data = await _commit(c, zone, {RH: ((T0 + 10 * H, T0 + 12 * H),)})
        assert "booked for 92 % of the period" in data[const.ZONE_EXPLANATION]

    async def test_dewpoint_does_not(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, _readings())
        plain = await _commit(c, zone)
        data = await _commit(
            c, zone, {const.MAPPING_DEWPOINT: ((T0 + 10 * H, T0 + 12 * H),)}
        )
        assert data[const.ZONE_DELTA] == plain[const.ZONE_DELTA]
        assert "booked for" not in data[const.ZONE_EXPLANATION]


class TestTheDailyFormUnderTheHourlySwitch:
    """Estimated sun keeps the daily form; its own fields decide the share."""

    async def test_humidity_does_not_count_there(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, _readings(), solrad="1")
        data = await _commit(c, zone, {RH: ((T0 + 10 * H, T0 + 12 * H),)})
        assert HOURLY_SENTENCE not in data[const.ZONE_EXPLANATION]
        assert data[const.ZONE_DELTA] == pytest.approx(-5.0)
        assert "booked for" not in data[const.ZONE_EXPLANATION]

    async def test_temperature_does(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, _readings(), solrad="1")
        data = await _commit(c, zone, {T: ((T0 + 10 * H, T0 + 12 * H),)})
        assert data[const.ZONE_DELTA] == pytest.approx(-5.0 * 22 / 24)
        assert "booked for 92 % of the period" in data[const.ZONE_EXPLANATION]


class TestTheReplayedBalance:
    async def test_the_daily_form_places_no_et_in_silent_time(
        self, coordinator, monkeypatch
    ):
        """Estimated sun and no sun sensor: the daily form runs under the hourly
        switch and its balance is replayed. The fields of the daily form decide
        where its ET is placed, as they decide the share it books."""
        c, store = coordinator
        readings = [{k: v for k, v in row.items() if k != SUN} for row in _readings()]
        zone = await _zone(c, store, readings, solrad="1")
        seen = _recording_substeps(monkeypatch)
        span = (T0 + 10 * H, T0 + 12 * H)

        plain = await _commit(c, zone)
        assert "Number of steps:" in plain[const.ZONE_EXPLANATION]
        plain_steps = seen[-1]
        assert plain_steps

        # Humidity is not a field of the daily form: nothing moves.
        await _commit(c, zone, {RH: (span,)})
        assert seen[-1] == plain_steps

        # Temperature is: no ET is placed in the hours it was silent.
        cut = await _commit(c, zone, {T: (span,)})
        steps = seen[-1]
        inside = _inside(steps, *span)
        assert inside
        assert all(steps[i].et_weight == 0.0 for i in inside)
        assert sum(step.et_weight for step in steps) == pytest.approx(1.0)
        assert "Number of steps:" in cut[const.ZONE_EXPLANATION]

    async def test_it_still_replays_under_a_blocked_rain_rate(self, coordinator):
        c, store = coordinator
        readings = _readings(
            rain=lambda stamp: 1.0 if stamp.hour in (9, 10, 11, 15) else 0.0
        )
        zone = await _zone(c, store, readings, config=RATE)
        blocked = {RAIN: ((T0 + 10 * H, T0 + 12 * H),)}
        data = await _commit(c, zone, blocked)
        assert "Number of steps:" in data[const.ZONE_EXPLANATION]

    async def test_it_still_replays_under_a_blocked_required_field(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, _readings(rain=lambda stamp: 1.0), config=RATE)
        data = await _commit(c, zone, {T: ((T0 + 10 * H, T0 + 12 * H),)})
        assert "Number of steps:" in data[const.ZONE_EXPLANATION]
