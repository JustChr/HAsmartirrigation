"""The daily bucket's ET sourced from summed hourly FAO-56 ETo.

Running the daily FAO-56 equation on window-mean weather is biased by cloudiness:
fed one identical hourly series over 362 days it comes out 1.144x a reference
implementation on overcast days and 0.925x on clear ones, while the same series
summed hour by hour sits flat at 1.02-1.04 across every sky band (mean absolute
daily error 0.099 mm against 0.254 mm). The equation itself is already pinned
against FAO-56 Example 19 in test_et_hourly.py, so everything that can still go
wrong lives in the inputs handed to it -- which is what these cover:

* the MJ/day/m2 -> MJ/m2/h conversion, hand-computed, because omitting it hands
  the equation about 12x the solar constant;
* the two buffer shapes, since the continuous-update path writes one field per
  event and a builder that assumes dense rows drops most of that buffer;
* carry-forward for hours with no readings, and partial-hour coverage;
* that ``hour_multiplier`` is NOT applied on top of a summed-hourly total, which
  would scale the same window twice;
* that every path which cannot support hourly rows falls back to the daily form
  rather than to a fabricated series.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util
import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.et_estimate import eto_hourly_series
from custom_components.smart_irrigation.et_hourly import eto_hourly
from custom_components.smart_irrigation.store import SmartIrrigationStorage
from custom_components.smart_irrigation.weather_aggregate import (
    build_hourly_rows,
    build_substeps,
)

T0 = datetime.datetime(2026, 5, 22, 0, 0, 0)
LAT, LON, ELEV = 39.68987, -84.07865, 311.0

# 1 W/m2 = 0.0864 MJ/day/m2, which is what the buffer stores.
W_TO_MJ_DAY = 0.0864


def _row(stamp, fields):
    return {const.RETRIEVED_AT: stamp, **fields}


def _local_tz_offset_h():
    """The offset the calculation derives, so expectations track the code."""
    offset = dt_util.now().utcoffset()
    return offset.total_seconds() / 3600.0 if offset else 0.0


def _bell(peak=800.0):
    """Daylight solar in W/m2, flat within each hour so hourly means are exact."""

    def f(hour):
        if not 6 <= hour < 20:
            return 0.0
        return peak * (1 - abs(hour + 0.5 - 13) / 7)

    return f


def _dense(solar_w, *, hours=24, temp=20.0, rh=60.0, wind=1.0, pressure=None, step=10):
    """A dense buffer: every mapped field on every row, as the poll path writes."""
    readings = []
    for hour in range(hours):
        for minute in range(0, 60, step):
            fields = {
                const.MAPPING_TEMPERATURE: temp,
                const.MAPPING_HUMIDITY: rh,
                const.MAPPING_WINDSPEED: wind,
                const.MAPPING_SOLRAD: solar_w(hour) * W_TO_MJ_DAY,
            }
            if pressure is not None:
                fields[const.MAPPING_PRESSURE] = pressure
            readings.append(_row(T0 + timedelta(hours=hour, minutes=minute), fields))
    return readings


def _sparse(solar_w, *, hours=24, temp=20.0, rh=60.0, wind=1.0, step=10):
    """A sparse buffer: one field per row, as the continuous-update path writes.

    Only solar moves here, so the other fields appear once -- exactly the shape a
    dense-row assumption drops most of. They sit just inside the window because
    ``select_window`` keeps a single boundary row: a sparse field whose last
    reading predates the watermark reaches the calculation through the mapping's
    carry-forward instead, which is a different path.
    """
    readings = [
        _row(T0 + timedelta(minutes=1), {const.MAPPING_TEMPERATURE: temp}),
        _row(T0 + timedelta(minutes=1), {const.MAPPING_HUMIDITY: rh}),
        _row(T0 + timedelta(minutes=1), {const.MAPPING_WINDSPEED: wind}),
    ]
    for hour in range(hours):
        for minute in range(0, 60, step):
            readings.append(
                _row(
                    T0 + timedelta(hours=hour, minutes=minute),
                    {const.MAPPING_SOLRAD: solar_w(hour) * W_TO_MJ_DAY},
                )
            )
    return readings


def _upto(readings, end):
    """Trim to readings at or before ``end``.

    The window end is ``max(now, last reading)``, so a fixture holding readings
    from the future would silently stretch the window past the ``now`` under test.
    """
    return [r for r in readings if r[const.RETRIEVED_AT] <= end]


class TestRowBuilder:
    """The row-builder is the new code; the equation behind it is already pinned."""

    def test_solar_is_divided_by_24(self):
        """Hand-computed: 800 W/m2 -> 69.12 MJ/day/m2 stored -> 2.88 MJ/m2/h.

        The buffer holds a DAILY rate and FAO-56 hourly wants an HOURLY one. Skip
        the divide and the equation is handed 16.3 kW/m2, about 12x the solar
        constant, and the day's ET goes with it.
        """
        readings = _dense(lambda h: 800.0)
        assert readings[0][const.MAPPING_SOLRAD] == pytest.approx(69.12)
        rows = build_hourly_rows(readings, T0, {}, now=T0 + timedelta(hours=24))
        assert rows is not None
        assert all(r["solar_mj_h"] == pytest.approx(2.88) for r in rows)

    def test_one_row_per_clock_hour_with_the_hour_midpoint(self):
        rows = build_hourly_rows(_dense(_bell()), T0, {}, now=T0 + timedelta(hours=24))
        assert len(rows) == 24
        assert [r["hour"] for r in rows] == [h + 0.5 for h in range(24)]
        assert {r["doy"] for r in rows} == {T0.timetuple().tm_yday}
        assert all(r["coverage_h"] == pytest.approx(1.0) for r in rows)
        assert rows[0]["hour_start"] == T0

    def test_partial_hours_at_both_ends_are_charged_their_real_share(self):
        """A window that starts and ends mid-hour must not book two whole hours."""
        start = T0 + timedelta(hours=6, minutes=30)
        end = T0 + timedelta(hours=9, minutes=15)
        rows = build_hourly_rows(_upto(_dense(_bell()), end), start, {}, now=end)
        assert [r["coverage_h"] for r in rows] == pytest.approx([0.5, 1.0, 1.0, 0.25])

    def test_sparse_and_dense_buffers_agree(self):
        """The continuous-update buffer is the shape this install actually writes."""
        now = T0 + timedelta(hours=24)
        dense = build_hourly_rows(_dense(_bell()), T0, {}, now=now)
        sparse = build_hourly_rows(_sparse(_bell()), T0, {}, now=now)
        assert sparse is not None
        assert len(sparse) == len(dense) == 24
        for a, b in zip(dense, sparse, strict=True):
            for key in ("temperature", "humidity", "wind_2m", "solar_mj_h"):
                assert a[key] == pytest.approx(b[key])

    def test_an_hour_with_no_readings_carries_the_last_value_forward(self):
        """Missing-hour policy. Solar emits no rows overnight, so this is the norm."""
        base = {
            const.MAPPING_HUMIDITY: 50.0,
            const.MAPPING_WINDSPEED: 1.0,
            const.MAPPING_SOLRAD: 0.0,
        }
        readings = [
            _row(T0 + timedelta(hours=1), {**base, const.MAPPING_TEMPERATURE: 10.0}),
            _row(T0 + timedelta(hours=5), {**base, const.MAPPING_TEMPERATURE: 20.0}),
        ]
        rows = build_hourly_rows(readings, T0, {}, now=T0 + timedelta(hours=6))
        assert len(rows) == 6
        # Held backwards to the window start, forwards over the silent hours 2-4,
        # and forwards again past the last reading.
        assert [r["temperature"] for r in rows] == pytest.approx(
            [10.0, 10.0, 10.0, 10.0, 10.0, 20.0]
        )

    def test_the_measured_barometer_is_passed_through_in_kpa(self):
        rows = build_hourly_rows(
            _dense(_bell(), pressure=983.0), T0, {}, now=T0 + timedelta(hours=24)
        )
        assert all(r["pressure_kpa"] == pytest.approx(98.3) for r in rows)

    def test_no_barometer_means_no_key_so_the_helper_derives_it(self):
        rows = build_hourly_rows(_dense(_bell()), T0, {}, now=T0 + timedelta(hours=24))
        assert all("pressure_kpa" not in r for r in rows)

    def test_a_missing_required_field_falls_back(self):
        """No radiation anywhere means no hourly ETo; the daily form still runs."""
        readings = [
            _row(
                T0 + timedelta(hours=1),
                {
                    const.MAPPING_TEMPERATURE: 20.0,
                    const.MAPPING_HUMIDITY: 50.0,
                    const.MAPPING_WINDSPEED: 1.0,
                },
            )
        ]
        assert build_hourly_rows(readings, T0, {}, now=T0 + timedelta(hours=6)) is None

    def test_a_field_only_in_the_carry_forward_is_still_usable(self):
        """A sparse buffer can hold no row at all for a slow-moving field."""
        readings = [
            _row(
                T0 + timedelta(hours=1),
                {
                    const.MAPPING_TEMPERATURE: 20.0,
                    const.MAPPING_WINDSPEED: 1.0,
                    const.MAPPING_SOLRAD: 0.0,
                },
            )
        ]
        now = T0 + timedelta(hours=6)
        assert build_hourly_rows(readings, T0, {}, now=now) is None
        rows = build_hourly_rows(
            readings, T0, {}, now=now, last_entry={const.MAPPING_HUMIDITY: 55.0}
        )
        assert all(r["humidity"] == pytest.approx(55.0) for r in rows)

    def test_an_absurdly_long_window_falls_back(self):
        """Past the buffer retention every extra hour is pure carry-forward."""
        readings = _dense(_bell(), step=30)
        assert build_hourly_rows(readings, T0, {}, now=T0 + timedelta(days=8)) is None

    def test_precipitation_is_bucketed_by_hour_when_it_has_time_structure(self):
        readings = []
        cumulative = 0.0
        for hour in range(4):
            cumulative += 2.0 if hour in (1, 2) else 0.0
            readings.append(
                _row(
                    T0 + timedelta(hours=hour, minutes=30),
                    {
                        const.MAPPING_TEMPERATURE: 20.0,
                        const.MAPPING_HUMIDITY: 50.0,
                        const.MAPPING_WINDSPEED: 1.0,
                        const.MAPPING_SOLRAD: 0.0,
                        const.MAPPING_PRECIPITATION: cumulative,
                    },
                )
            )
        rows = build_hourly_rows(readings, T0, {}, now=T0 + timedelta(hours=4))
        assert [r["precipitation"] for r in rows] == pytest.approx([0.0, 2.0, 2.0, 0.0])


class TestSeries:
    """``eto_hourly_series`` adds coverage scaling and the barometer to the equation."""

    def _r(self, **over):
        base = {
            "temperature": 25.0,
            "humidity": 55.0,
            "wind_2m": 1.2,
            "solar_mj_h": 2.0,
            "hour": 13.5,
            "doy": 142,
        }
        base.update(over)
        return base

    def test_coverage_scales_the_hour(self):
        full = eto_hourly_series([self._r()], LAT, LON, -4.0, ELEV)[0]
        half = eto_hourly_series([self._r(coverage_h=0.5)], LAT, LON, -4.0, ELEV)[0]
        assert full > 0
        assert half == pytest.approx(full / 2)

    def test_the_barometer_is_used_when_present(self):
        measured = eto_hourly_series([self._r(pressure_kpa=98.3)], LAT, LON, -4.0, ELEV)
        assert measured[0] == pytest.approx(
            eto_hourly(
                t_c=25.0,
                rh_pct=55.0,
                wind_2m=1.2,
                solar_rad_hr=2.0,
                latitude_deg=LAT,
                longitude_deg=LON,
                doy=142,
                hour_mid=13.5,
                tz_offset_h=-4.0,
                elevation_m=ELEV,
                pressure_kpa=98.3,
            )
        )
        # And it matters: the psychrometric constant is linear in pressure.
        assert measured[0] != pytest.approx(
            eto_hourly_series([self._r()], LAT, LON, -4.0, ELEV)[0]
        )


class TestPerHourQuantum:
    """Axis D's sub-steps carry each hour's OWN ET, not a share of one total."""

    def _readings(self, hours=4, rain_at=None):
        readings = []
        cumulative = 0.0
        for hour in range(hours):
            for minute in (0, 30):
                if rain_at == (hour, minute):
                    cumulative += 3.0
                readings.append(
                    _row(
                        T0 + timedelta(hours=hour, minutes=minute),
                        {
                            const.MAPPING_TEMPERATURE: 20.0,
                            const.MAPPING_HUMIDITY: 50.0,
                            const.MAPPING_WINDSPEED: 1.0,
                            const.MAPPING_SOLRAD: 10.0,
                            const.MAPPING_PRECIPITATION: cumulative,
                        },
                    )
                )
        return readings

    def test_weights_track_the_hourly_series_not_the_solar_shape(self):
        hourly = {
            T0 + timedelta(hours=h): et for h, et in enumerate([0.1, 0.4, 0.4, 0.1])
        }
        steps = build_substeps(
            self._readings(), T0, {}, now=T0 + timedelta(hours=4), hourly_et=hourly
        )
        assert steps is not None and len(steps) == 4
        assert sum(s.et_weight for s in steps) == pytest.approx(1.0)
        # Solar is flat across the window, so without the hourly series the four
        # steps would be 0.25 each. With it they follow the ETo series.
        assert [s.et_weight for s in steps] == pytest.approx([0.1, 0.4, 0.4, 0.1])

    def test_a_rain_cut_splits_its_hour_without_moving_et_between_hours(self):
        """Sub-hour cuts redistribute inside an hour only. That is the quantum."""
        hourly = {T0: 0.3, T0 + timedelta(hours=1): 0.7}
        steps = build_substeps(
            self._readings(hours=2, rain_at=(0, 30)),
            T0,
            {},
            now=T0 + timedelta(hours=2),
            hourly_et=hourly,
        )
        # Hour 0 was cut at :30 by the rain; its two pieces still sum to 0.3.
        assert len(steps) == 3
        assert steps[0].et_weight + steps[1].et_weight == pytest.approx(0.3)
        assert steps[2].et_weight == pytest.approx(0.7)

    def test_an_hour_missing_from_the_series_falls_back(self):
        """The two are derived from the same window; a gap means an assumption broke."""
        steps = build_substeps(
            self._readings(), T0, {}, now=T0 + timedelta(hours=4), hourly_et={T0: 1.0}
        )
        assert steps is None


@pytest.fixture
async def coordinator(hass):
    """A real coordinator over a real in-memory store."""
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
    # hourlycalculation is the gate; continuousupdates is on as well because it
    # still selects the time-weighted window aggregate these numbers were taken
    # against. The two axes are pinned apart in TestTheGateIsItsOwnAxis.
    await store.async_update_config(
        {const.CONF_CONTINUOUS_UPDATES: True, const.CONF_HOURLY_CALCULATION: True}
    )
    return c, store


class TestThroughCalculateModule:
    """The integration point, because the one real trap lives exactly there."""

    async def _zone(self, c, store, readings, *, daily_et=5.0, solrad="3", days=0):
        mapping = await store.async_create_mapping(
            {
                const.MAPPING_NAME: "GW",
                const.MAPPING_MAPPINGS: {},
                const.MAPPING_DATA: readings,
            }
        )
        module = await store.async_create_module(
            {const.MODULE_NAME: "PyETO", "description": "", "config": {}}
        )
        instance = Mock()
        instance.calculate = Mock(return_value=-daily_et)
        instance._solrad_behavior = solrad
        instance.forecast_days = days
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

    async def _run(self, c, zone, now):
        weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
        return await c.calculate_module(zone, weatherdata, None, now=now)

    async def test_the_delta_is_the_summed_hourly_total_untouched_by_hour_multiplier(
        self, coordinator
    ):
        """The one real trap: summing hourly already integrates over the window.

        Applying ``hour_multiplier`` on top would scale the same window twice. The
        window here is half a day, so the two answers differ by a factor of two.
        """
        c, store = coordinator
        now = T0 + timedelta(hours=12)
        readings = _dense(_bell(), hours=12)
        zone = await self._zone(c, store, readings)
        data = await self._run(c, zone, now)

        rows = build_hourly_rows(readings, T0, {}, now=now)
        assert len(rows) == 12
        expected = sum(eto_hourly_series(rows, LAT, LON, _local_tz_offset_h(), ELEV))
        assert expected > 0
        assert data[const.ZONE_DELTA] == pytest.approx(-expected, abs=1e-9)
        # hour_multiplier is 0.5 over this window, and the daily form would have
        # produced -2.5 from the stubbed -5.0 mm/day. Neither is what ran.
        assert data[const.ZONE_DELTA] != pytest.approx(-expected * 0.5)
        assert data[const.ZONE_DELTA] != pytest.approx(-2.5)
        assert "sum of hourly FAO-56 et0" in data[const.ZONE_EXPLANATION]

    async def test_the_crop_coefficient_still_scales_only_the_et_term(
        self, coordinator
    ):
        c, store = coordinator
        now = T0 + timedelta(hours=12)
        zone = await self._zone(c, store, _dense(_bell(), hours=12))
        plain = await self._run(c, zone, now)

        await store.async_update_zone(zone[const.ZONE_ID], {const.ZONE_KC: 0.75})
        scaled = await self._run(c, store.get_zone(zone[const.ZONE_ID]), now)
        assert scaled[const.ZONE_DELTA] == pytest.approx(plain[const.ZONE_DELTA] * 0.75)

    async def test_the_flag_off_keeps_the_daily_form(self, coordinator):
        """The gate is a blast-radius decision, not a technical limit.

        Measured against dense truth on real recorded days the hourly form runs
        within 8.4% on an hourly-polled install with no systematic bias, so it
        is not withheld from polling. It is gated because the form moves the
        daily number by up to 12% structured by cloudiness, and an install that
        opted into nothing should not have its watering change underneath it.
        """
        c, store = coordinator
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: False})
        now = T0 + timedelta(hours=12)
        zone = await self._zone(c, store, _dense(_bell(), hours=12))
        data = await self._run(c, zone, now)
        assert data[const.ZONE_DELTA] == pytest.approx(-2.5)
        assert "hour_multiplier" in data[const.ZONE_EXPLANATION]

    async def test_estimated_solar_radiation_keeps_the_daily_form(self, coordinator):
        """The measured series is not what the module would have used."""
        c, store = coordinator
        now = T0 + timedelta(hours=12)
        zone = await self._zone(c, store, _dense(_bell(), hours=12), solrad="1")
        data = await self._run(c, zone, now)
        assert data[const.ZONE_DELTA] == pytest.approx(-2.5)
        assert "hour_multiplier" in data[const.ZONE_EXPLANATION]

    async def test_forecast_days_keep_the_daily_form(self, coordinator):
        """Forecast days average in days that have no hourly series at all."""
        c, store = coordinator
        now = T0 + timedelta(hours=12)
        zone = await self._zone(c, store, _dense(_bell(), hours=12), days=2)
        data = await self._run(c, zone, now)
        assert data[const.ZONE_DELTA] == pytest.approx(-2.5)
        assert "hour_multiplier" in data[const.ZONE_EXPLANATION]

    async def test_a_buffer_without_radiation_keeps_the_daily_form(self, coordinator):
        c, store = coordinator
        now = T0 + timedelta(hours=12)
        readings = [
            _row(
                T0 + timedelta(minutes=m),
                {
                    const.MAPPING_TEMPERATURE: 20.0,
                    const.MAPPING_HUMIDITY: 50.0,
                    const.MAPPING_WINDSPEED: 1.0,
                },
            )
            for m in (10, 400)
        ]
        zone = await self._zone(c, store, readings)
        data = await self._run(c, zone, now)
        assert data[const.ZONE_DELTA] == pytest.approx(-2.5)
        assert "hour_multiplier" in data[const.ZONE_EXPLANATION]


class TestTheGateIsItsOwnAxis:
    """hourlycalculation and continuousupdates are independent switches.

    They were one switch, which was wrong in both directions: an install that
    had enabled continuous ingestion would have received a 12%-scale change to
    its ET with no further opt-in, and a poll-only install could not have the
    hourly form at all despite running it within 8.4% of dense truth with no
    systematic bias. The four combinations are asserted together because a
    regression here is a silent change to how much water a zone gets.
    """

    async def _delta(self, c, store, *, continuous, hourly):
        await store.async_update_config(
            {
                const.CONF_CONTINUOUS_UPDATES: continuous,
                const.CONF_HOURLY_CALCULATION: hourly,
            }
        )
        now = T0 + timedelta(hours=12)
        zone = await TestThroughCalculateModule()._zone(
            c, store, _dense(_bell(), hours=12)
        )
        data = await TestThroughCalculateModule()._run(c, zone, now)
        return data[const.ZONE_DELTA], data[const.ZONE_EXPLANATION]

    # The daily form's answer with this fixture: the stubbed -5.0 mm/day scaled
    # by an hour_multiplier of 0.5 over the half-day window.
    DAILY = -2.5

    async def test_neither_flag_runs_the_daily_form(self, coordinator):
        c, store = coordinator
        delta, explanation = await self._delta(c, store, continuous=False, hourly=False)
        assert delta == pytest.approx(self.DAILY)
        assert "hour_multiplier" in explanation

    async def test_continuous_updates_alone_still_runs_the_daily_form(
        self, coordinator
    ):
        """The case that decided the split: denser ingestion is not consent."""
        c, store = coordinator
        delta, explanation = await self._delta(c, store, continuous=True, hourly=False)
        assert delta == pytest.approx(self.DAILY)
        assert "hour_multiplier" in explanation

    async def test_the_flag_alone_runs_the_hourly_form_on_a_polled_buffer(
        self, coordinator
    ):
        """The case the split unlocks: no event-driven ingestion anywhere here."""
        c, store = coordinator
        delta, explanation = await self._delta(c, store, continuous=False, hourly=True)
        assert delta != pytest.approx(self.DAILY)
        assert "sum of hourly FAO-56 et0" in explanation

    async def test_both_flags_run_the_hourly_form(self, coordinator):
        c, store = coordinator
        delta, explanation = await self._delta(c, store, continuous=True, hourly=True)
        assert delta != pytest.approx(self.DAILY)
        assert "sum of hourly FAO-56 et0" in explanation
