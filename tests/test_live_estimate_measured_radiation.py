"""A zone that measures solar radiation and blends forecast days.

Its commit runs the daily equation on the window's MEAN measured radiation,
averaged with the forecast days, so the hourly-summed buffer source does not
apply to it and nothing else priced the same quantity. Part-way through a window
the observed mean is the wrong input in either direction -- an all-daylight
window reads hot, a night-only one reads zero -- so the estimate composes the
window's radiation the way it composes its temperature extremes: observed so
far, plus the remaining hours from a calibrated forecast or the station's own
clearness, converging on the commit's mean as the window closes.

Every agreement here runs the real ``calculate_module`` over a real store with a
real PyETO instance, for the reason the sibling module gives.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.calcmodules.pyeto import PyETO, SOLRAD_behavior
from custom_components.irrigation_plus.calculation import (
    hourly_radiation_series,
    trailing_radiation_calibration,
)
from custom_components.irrigation_plus.sensor import (
    SmartIrrigationZoneLiveDeficitSensor,
)
from custom_components.irrigation_plus.store import SmartIrrigationStorage
from custom_components.irrigation_plus.weathermodules.OpenMeteoClient import (
    OpenMeteoClient,
)
from tests.test_live_estimate_replayed_balance import (
    ANCHOR,
    ELEV,
    LAT,
    T0,
    WINDOW_END,
    _committed_daily_et,
    _daily_forecast,
    _diurnal_readings,
    _estimating_inputs,
    _hourly_forecast,
    _observed_rows,
    _proxy_inputs,
    _zone,
    make_coordinator,
)


@pytest.fixture
async def coordinator(hass):
    return await make_coordinator(hass)


def _rate(hour):
    """The fixture's radiation in MJ m-2 day-1 through a clock hour.

    ``_diurnal_readings`` holds each clock hour's rate flat, so this is the
    truth a forecast is asked for -- and made wrong on purpose below.
    """
    clock = hour % 24
    return 700.0 * 0.0864 * (clock - 6) / 8 if 6 <= clock < 20 else 0.0


def _radiation_forecast(factor=1.0):
    """Interval-ending MJ m-2 h-1 across the window and past it."""
    return [
        (T0 + timedelta(hours=hour + 1), factor * _rate(hour) / 24.0)
        for hour in range(30)
    ]


def _dated_daily():
    """``_daily_forecast`` stamped the way a client stamps it, from the day after
    the commit. Undated rows are read as starting tomorrow from NOW, so the same
    undated list means different days at midday and at the close, and a
    convergence measured across the two would be measuring that instead."""
    utc = datetime.timezone.utc
    return [
        {
            **row,
            const.FORECAST_DAY_START: datetime.datetime(2026, 5, 24 + i, tzinfo=utc),
        }
        for i, row in enumerate(_daily_forecast())
    ]


async def _measuring_zone(c, store, bucket, *, rain_at=None, forecast_days=2):
    """PyETO on measured radiation, blending ``forecast_days``, hourly form on."""
    zone = await _zone(
        c,
        store,
        bucket,
        rain_at=rain_at,
        solrad=SOLRAD_behavior.DontEstimate.value,
        readings=_diurnal_readings(rain_at),
    )
    module = store.get_module(zone[const.ZONE_MODULE])
    await store.async_update_module(
        module[const.MODULE_ID],
        {
            const.MODULE_CONFIG: {
                const.CONF_PYETO_SOLRAD_BEHAVIOR: SOLRAD_behavior.DontEstimate.value,
                const.CONF_PYETO_FORECAST_DAYS: forecast_days,
            }
        },
    )
    zone = dict(zone)
    zone[const.ZONE_LAST_CONSUMED] = ANCHOR
    zone[const.ZONE_LAST_CALCULATED] = ANCHOR
    await store.async_update_zone(
        zone[const.ZONE_ID],
        {const.ZONE_LAST_CONSUMED: ANCHOR, const.ZONE_LAST_CALCULATED: ANCHOR},
    )
    instance = PyETO(
        c.hass,
        description="",
        config={
            const.CONF_PYETO_SOLRAD_BEHAVIOR: SOLRAD_behavior.DontEstimate.value,
            const.CONF_PYETO_FORECAST_DAYS: forecast_days,
        },
    )
    instance._latitude = LAT
    instance._elevation = ELEV
    # Local clock and solar clock on the same day; see ``_estimating_zone``.
    c._effective_longitude = 0.0
    c.getModuleInstanceByID = AsyncMock(return_value=instance)
    return zone, store.get_module(zone[const.ZONE_MODULE]), instance


async def _calibrate(store, zone, *, ratio=None, clearness=0.5):
    """Seed the two committed windows a ratio needs: ``ratio`` measured-to-forecast,
    if any."""
    measured, ceiling = 20.0, 20.0 / clearness
    forecast = None if ratio is None else measured / ratio
    await store.async_update_mapping(
        zone[const.ZONE_MAPPING],
        {
            const.MAPPING_RADIATION_CALIBRATION: [
                [day, measured, forecast, ceiling]
                for day in ("2026-05-20", "2026-05-21")
            ]
        },
    )


def _inputs_at(instance, module, now, *, radiation=None, daily=None):
    """The exact temperature forecast, so radiation is the only thing projected
    from anything less than the truth."""
    inputs = _estimating_inputs(
        instance, module, now=now, forecast=_hourly_forecast(), daily_forecast=daily
    )
    inputs["hourly_radiation_forecast"] = radiation
    return inputs


def _implied_daily(c, store, zone, instance, module, now, **kw):
    """The day total the estimate's projected inputs claim, and the estimate."""
    store.set_mapping_buffer(
        zone[const.ZONE_MAPPING], _observed_rows(_diurnal_readings(), now)
    )
    est = c._intraday_for_zone(zone, _inputs_at(instance, module, now, **kw))
    elapsed = (now - ANCHOR).total_seconds() / 3600.0
    return est["et_since"] / (elapsed / 24.0), est


async def _reload(hass, stored_mapping):
    """A store loaded from a document holding only ``stored_mapping``."""
    reloaded = SmartIrrigationStorage(hass)
    reloaded._store = Mock()
    reloaded._store.async_load = AsyncMock(
        return_value={
            "config": {},
            "zones": [],
            "modules": [],
            "mappings": [stored_mapping],
        }
    )
    reloaded._store.async_delay_save = Mock()
    await reloaded.async_load()
    return reloaded


class TestTheLiveBucketRunsTheCommitsOwnEquation:
    async def test_the_live_bucket_lands_on_the_committed_bucket(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(
            c, store, 2.0, rain_at={20: 14.0}
        )
        daily = _daily_forecast()

        est = c._intraday_for_zone(
            zone, _inputs_at(instance, module, WINDOW_END, daily=daily)
        )
        weatherdata, _ = await c._aggregate_for_zone(zone, now=WINDOW_END)
        data = await c.calculate_module(zone, weatherdata, daily, now=WINDOW_END)

        assert est["method"] == "daily_mirror"
        assert est["radiation_tier"] == "observed"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_its_evapotranspiration_is_the_one_the_commit_books(
        self, coordinator
    ):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        daily = _daily_forecast()

        est = c._intraday_for_zone(
            zone, _inputs_at(instance, module, WINDOW_END, daily=daily)
        )
        booked = await _committed_daily_et(c, zone, forecast=daily)

        assert booked > 0.5
        assert est["et_since"] == pytest.approx(booked, abs=1e-4)

    async def test_the_proxy_would_have_disagreed(self, coordinator):
        """Guards the two above against being vacuous: with no module handed in
        the zone falls through to the Hargreaves proxy."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        daily = _daily_forecast()

        mirrored = c._intraday_for_zone(
            zone, _inputs_at(instance, module, WINDOW_END, daily=daily)
        )
        previous = c._intraday_for_zone(zone, _proxy_inputs(now=WINDOW_END))

        assert previous["method"] == "proxy"
        assert previous["et_since"] != pytest.approx(mirrored["et_since"], abs=0.1)

    async def test_a_group_without_a_solar_sensor_mirrors_the_commit_too(
        self, coordinator
    ):
        """No measured mean, so the commit estimates one from sun hours; the
        estimate must hand the equation the same absence rather than project
        a radiation nobody measured."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        daily = _daily_forecast()
        store.set_mapping_buffer(
            zone[const.ZONE_MAPPING],
            [
                {k: v for k, v in row.items() if k != const.MAPPING_SOLRAD}
                for row in _diurnal_readings()
            ],
        )

        est = c._intraday_for_zone(
            zone, _inputs_at(instance, module, WINDOW_END, daily=daily)
        )
        booked = await _committed_daily_et(c, zone, forecast=daily)

        assert est["method"] == "daily_mirror"
        assert est["radiation_tier"] is None
        assert est["et_since"] == pytest.approx(booked, abs=1e-4)

    async def test_hourly_calculation_off_gets_the_same_mirror(self, coordinator):
        """Forecast days aside, a measured zone with the switch off also commits
        through the daily equation, so it is mirrored the same way."""
        c, store = coordinator
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: False})
        zone, module, instance = await _measuring_zone(c, store, 2.0, forecast_days=0)

        est = c._intraday_for_zone(zone, _inputs_at(instance, module, WINDOW_END))
        booked = await _committed_daily_et(c, zone)

        assert est["method"] == "daily_mirror"
        assert est["et_since"] == pytest.approx(booked, abs=1e-4)

    async def test_with_the_hourly_form_on_it_keeps_the_buffer_source(
        self, coordinator
    ):
        """No forecast days and the switch on: the commit sums hourly ETo, so
        the mirror must stay out of the way."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0, forecast_days=0)

        est = c._intraday_for_zone(zone, _inputs_at(instance, module, WINDOW_END))

        assert est["method"] == "hourly_sensor"
        assert est["radiation_tier"] is None


class TestTheRadiationRemainder:
    async def test_a_calibrated_forecast_closes_on_the_commit(self, coordinator):
        """The forecast runs 20% dull and the trailing ratio corrects only half
        of it, so the remainder is wrong on purpose and the observation has to
        overtake it. Dull rather than bright: the fixture's day is near clear-sky
        already, and a bright error would be clipped by the equation's own clamp
        instead of closed by the observation."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        await _calibrate(store, zone, ratio=1.1)
        daily = _dated_daily()
        target = await _committed_daily_et(c, zone, forecast=daily)

        results = [
            _implied_daily(
                c,
                store,
                zone,
                instance,
                module,
                ANCHOR + timedelta(hours=h),
                radiation=_radiation_forecast(0.8),
                daily=daily,
            )
            for h in (6, 10, 14, 24)
        ]
        gaps = [abs(implied - target) for implied, _est in results]

        assert [est["radiation_tier"] for _i, est in results[:3]] == ["service"] * 3
        assert gaps[0] > gaps[1] > gaps[2]
        assert gaps[0] > 0.05
        assert gaps[-1] < 1e-3

    async def test_the_calibration_is_applied(self, coordinator):
        """The same hot forecast, priced with and without the ratio that undoes
        it. Calibrated lands nearer the commit."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        daily = _dated_daily()
        target = await _committed_daily_et(c, zone, forecast=daily)
        midday = ANCHOR + timedelta(hours=10)

        await _calibrate(store, zone, ratio=1.0)
        raw, _ = _implied_daily(
            c,
            store,
            zone,
            instance,
            module,
            midday,
            radiation=_radiation_forecast(1.4),
            daily=daily,
        )
        await _calibrate(store, zone, ratio=1 / 1.4)
        calibrated, _ = _implied_daily(
            c,
            store,
            zone,
            instance,
            module,
            midday,
            radiation=_radiation_forecast(1.4),
            daily=daily,
        )

        assert abs(calibrated - target) < abs(raw - target)

    async def test_an_uncalibrated_forecast_is_not_used(self, coordinator):
        """Before any window has paired the station against the forecast, the
        forecast stays out: uncalibrated it projects worse than the clearness."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)

        _implied, est = _implied_daily(
            c,
            store,
            zone,
            instance,
            module,
            ANCHOR + timedelta(hours=10),
            radiation=_radiation_forecast(),
            daily=_dated_daily(),
        )

        assert est["method"] == "daily_mirror"
        assert est["radiation_tier"] == "self_contained"

    async def test_a_service_without_a_radiation_forecast_uses_the_clearness(
        self, coordinator
    ):
        """Only Open-Meteo hands one over; any other client leaves the remainder to
        the station's own clearness, calibrated or not."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        await _calibrate(store, zone, ratio=1.0)
        client = Mock(spec=["get_forecast_data"])
        midday = ANCHOR + timedelta(hours=10)
        store.set_mapping_buffer(
            zone[const.ZONE_MAPPING], _observed_rows(_diurnal_readings(), midday)
        )
        inputs = _inputs_at(instance, module, midday, daily=_dated_daily())
        inputs["hourly_radiation_forecast"] = hourly_radiation_series(client)

        est = c._intraday_for_zone(zone, inputs)

        assert inputs["hourly_radiation_forecast"] is None
        assert est["radiation_tier"] == "self_contained"

    async def test_a_forecast_with_a_hole_is_refused(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        await _calibrate(store, zone, ratio=1.0)
        holed = [
            row
            for row in _radiation_forecast()
            if not T0 + timedelta(hours=16) < row[0] < T0 + timedelta(hours=21)
        ]

        _implied, est = _implied_daily(
            c,
            store,
            zone,
            instance,
            module,
            ANCHOR + timedelta(hours=10),
            radiation=holed,
            daily=_dated_daily(),
        )

        assert est["radiation_tier"] == "self_contained"

    async def test_the_clearness_tier_closes_on_the_commit(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        daily = _dated_daily()
        target = await _committed_daily_et(c, zone, forecast=daily)

        gaps = [
            abs(
                _implied_daily(
                    c,
                    store,
                    zone,
                    instance,
                    module,
                    ANCHOR + timedelta(hours=h),
                    daily=daily,
                )[0]
                - target
            )
            for h in (14, 24)
        ]

        assert gaps[-1] < 1e-3
        assert gaps[0] > gaps[-1]


class TestBeforeTheSunIsUp:
    """Overnight nothing about today's sky has been seen. A ratio of the energy
    observed so far to the ceiling so far is a ratio of two zeros."""

    async def test_with_no_history_it_declines(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)

        _implied, est = _implied_daily(
            c,
            store,
            zone,
            instance,
            module,
            ANCHOR + timedelta(hours=2),
            daily=_daily_forecast(),
        )

        # The proxy still prices it, so the zone is not left without an estimate.
        assert est["method"] == "proxy"
        assert est["radiation_tier"] is None

    async def test_once_enough_sun_is_seen_today_s_clearness_takes_over(
        self, coordinator
    ):
        """Past the observed share, the trailing clearness no longer moves the
        projection; before it, the trailing clearness is all there is."""
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        daily = _daily_forecast()

        def et_at(hours):
            return _implied_daily(
                c,
                store,
                zone,
                instance,
                module,
                ANCHOR + timedelta(hours=hours),
                daily=daily,
            )[1]["et_since"]

        await _calibrate(store, zone, clearness=0.3)
        noon_dim, early_dim = et_at(10), et_at(2)
        await _calibrate(store, zone, clearness=0.9)
        noon_bright, early_bright = et_at(10), et_at(2)

        assert noon_bright == pytest.approx(noon_dim, abs=1e-6)
        assert early_bright > early_dim

    async def test_with_history_it_uses_the_trailing_clearness(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        await _calibrate(store, zone, clearness=0.6)
        early = ANCHOR + timedelta(hours=2)

        _implied, est = _implied_daily(
            c, store, zone, instance, module, early, daily=_daily_forecast()
        )
        await _calibrate(store, zone, clearness=0.3)
        _dimmer, dim = _implied_daily(
            c, store, zone, instance, module, early, daily=_daily_forecast()
        )

        assert est["method"] == "daily_mirror"
        assert est["radiation_tier"] == "self_contained"
        # A clearer trailing week projects a brighter day, and more loss.
        assert est["et_since"] > dim["et_since"]


class TestTheCommitRecordsTheCalibration:
    async def test_a_window_is_paired_against_the_forecast(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)
        client = Mock()
        client.get_hourly_radiation_forecast = Mock(
            return_value=[(T0 + timedelta(hours=h), 0.5) for h in range(31)]
        )
        c._WeatherServiceClient = client

        await c._record_window_radiation(
            zone, {const.MAPPING_SOLRAD: 15.0}, now=WINDOW_END
        )

        [entry] = store.get_mapping(zone[const.ZONE_MAPPING])[
            const.MAPPING_RADIATION_CALIBRATION
        ]
        key, measured, forecast, ceiling = entry
        assert key == WINDOW_END.date().isoformat()
        # A 24 h window: the mean rate is the day's energy.
        assert measured == pytest.approx(15.0)
        assert forecast == pytest.approx(12.0)
        # FAO-56 Annex 2 Table 2.6: about 40 MJ m-2 day-1 at 40 N in late May.
        assert ceiling == pytest.approx(40.0, abs=1.5)

    async def test_without_a_forecast_the_clearness_is_still_recorded(
        self, coordinator
    ):
        """A sensor-only install has no forecast to pair, and still needs the
        trailing clearness for its mornings."""
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)

        await c._record_window_radiation(
            zone, {const.MAPPING_SOLRAD: 15.0}, now=WINDOW_END
        )

        ratio, clearness = trailing_radiation_calibration(
            store, zone[const.ZONE_MAPPING]
        )
        assert ratio is None
        assert clearness == pytest.approx(15.0 / 40.0, abs=0.02)

    async def test_a_part_day_window_does_not_replace_the_day_s_pair(self, coordinator):
        """A manual calculation soon after the nightly one closes a window of
        minutes. Recording it would overwrite the whole-day pair it follows."""
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)
        await c._record_window_radiation(
            zone, {const.MAPPING_SOLRAD: 15.0}, now=WINDOW_END
        )
        zone[const.ZONE_LAST_CONSUMED] = WINDOW_END

        await c._record_window_radiation(
            zone,
            {const.MAPPING_SOLRAD: 30.0},
            now=WINDOW_END + timedelta(hours=1),
        )

        entries = store.get_mapping(zone[const.ZONE_MAPPING])[
            const.MAPPING_RADIATION_CALIBRATION
        ]
        assert [entry[1] for entry in entries] == [pytest.approx(15.0)]

    @pytest.mark.parametrize(("hours", "recorded"), [(17.9, False), (18.0, True)])
    async def test_the_shortest_window_recorded_is_three_quarters_of_a_day(
        self, coordinator, hours, recorded
    ):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)

        await c._record_window_radiation(
            zone,
            {const.MAPPING_SOLRAD: 15.0},
            now=ANCHOR + timedelta(hours=hours),
        )

        entries = store.get_mapping(zone[const.ZONE_MAPPING]).get(
            const.MAPPING_RADIATION_CALIBRATION
        )
        assert bool(entries) is recorded

    async def test_a_group_without_a_solar_sensor_records_nothing(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)

        await c._record_window_radiation(
            zone, {const.MAPPING_MIN_TEMP: 10.0}, now=WINDOW_END
        )

        assert not store.get_mapping(zone[const.ZONE_MAPPING]).get(
            const.MAPPING_RADIATION_CALIBRATION
        )

    async def test_the_real_commit_records_it(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)

        await c.async_calculate_zone(
            zone[const.ZONE_ID], _daily_forecast(), now=WINDOW_END
        )

        entries = store.get_mapping(zone[const.ZONE_MAPPING])[
            const.MAPPING_RADIATION_CALIBRATION
        ]
        assert len(entries) == 1
        assert entries[0][1] > 0

    async def test_a_second_commit_the_same_day_replaces_the_first(self, coordinator):
        """Zones sharing a sensor group each commit the same window; keyed by
        date, the group keeps one pair for it."""
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)

        for mean in (15.0, 16.0):
            await c._record_window_radiation(
                zone, {const.MAPPING_SOLRAD: mean}, now=WINDOW_END
            )

        entries = store.get_mapping(zone[const.ZONE_MAPPING])[
            const.MAPPING_RADIATION_CALIBRATION
        ]
        assert [entry[1] for entry in entries] == [pytest.approx(16.0)]

    async def test_the_ring_keeps_the_most_recent_windows_only(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)

        for day in range(const.RADIATION_CALIBRATION_WINDOWS + 3):
            start = ANCHOR + timedelta(days=day)
            zone[const.ZONE_LAST_CONSUMED] = start
            await c._record_window_radiation(
                zone,
                {const.MAPPING_SOLRAD: 10.0 + day},
                now=start + timedelta(hours=24),
            )

        entries = store.get_mapping(zone[const.ZONE_MAPPING])[
            const.MAPPING_RADIATION_CALIBRATION
        ]
        assert len(entries) == const.RADIATION_CALIBRATION_WINDOWS
        assert entries[-1][1] == pytest.approx(
            10.0 + const.RADIATION_CALIBRATION_WINDOWS + 2
        )


class TestTheTrailingCalibration:
    async def test_energies_are_summed_not_averaged(self, coordinator):
        """A short window carries as little weight as the energy it saw."""
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)
        await store.async_update_mapping(
            zone[const.ZONE_MAPPING],
            {
                const.MAPPING_RADIATION_CALIBRATION: [
                    ["2026-05-20", 20.0, 25.0, 40.0],
                    ["2026-05-21", 1.0, 0.5, 4.0],
                    ["2026-05-22", 10.0, None, 40.0],
                ]
            },
        )

        ratio, clearness = trailing_radiation_calibration(
            store, zone[const.ZONE_MAPPING]
        )

        assert ratio == pytest.approx(21.0 / 25.5)
        assert clearness == pytest.approx(31.0 / 84.0)

    async def test_a_malformed_entry_is_skipped_rather_than_raising(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)
        await store.async_update_mapping(
            zone[const.ZONE_MAPPING],
            {
                const.MAPPING_RADIATION_CALIBRATION: [
                    ["2026-05-20", "x", 25.0, 40.0],
                    ["2026-05-21", 20.0],
                    None,
                    ["not a date", 20.0, 25.0, 40.0],
                    ["2026-05-22", 20.0, 25.0, 40.0],
                    ["2026-05-23", 20.0, 25.0, 40.0],
                ]
            },
        )

        assert trailing_radiation_calibration(
            store, zone[const.ZONE_MAPPING], today=datetime.date(2026, 5, 23)
        ) == (pytest.approx(0.8), pytest.approx(0.5))

    async def _seed(self, store, zone, entries):
        await store.async_update_mapping(
            zone[const.ZONE_MAPPING], {const.MAPPING_RADIATION_CALIBRATION: entries}
        )

    async def test_one_paired_window_is_not_yet_a_ratio(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)
        await self._seed(store, zone, [["2026-05-21", 20.0, 25.0, 40.0]])

        ratio, clearness = trailing_radiation_calibration(
            store, zone[const.ZONE_MAPPING]
        )

        assert ratio is None
        assert clearness == pytest.approx(0.5)

    async def test_entries_past_a_week_are_ignored(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)
        await self._seed(
            store,
            zone,
            [
                ["2026-05-13", 10.0, 40.0, 40.0],
                ["2026-05-14", 10.0, 40.0, 40.0],
                ["2026-05-21", 20.0, 25.0, 40.0],
                ["2026-05-22", 20.0, 25.0, 40.0],
            ],
        )

        ratio, clearness = trailing_radiation_calibration(
            store, zone[const.ZONE_MAPPING], today=datetime.date(2026, 5, 22)
        )

        assert ratio == pytest.approx(0.8)
        assert clearness == pytest.approx(0.5)

    @pytest.mark.parametrize(("measured", "expected"), [(1.0, 0.5), (90.0, 2.0)])
    async def test_a_runaway_ratio_is_held_inside_its_bounds(
        self, coordinator, measured, expected
    ):
        """A dead sensor books almost no energy; a forecast blacked out by a bad
        run books almost none either. Neither may scale a whole remainder."""
        c, store = coordinator
        zone, _module, _instance = await _measuring_zone(c, store, 2.0)
        await self._seed(
            store,
            zone,
            [[day, measured, 30.0, 40.0] for day in ("2026-05-21", "2026-05-22")],
        )

        ratio, _clearness = trailing_radiation_calibration(
            store, zone[const.ZONE_MAPPING]
        )

        assert ratio == pytest.approx(expected)

    async def test_a_document_written_before_the_field_existed_still_loads(self, hass):
        store = SmartIrrigationStorage(hass)
        await store.async_load()
        mapping = await store.async_create_mapping(
            {const.MAPPING_NAME: "GW", const.MAPPING_MAPPINGS: {}}
        )
        stored = dict(store.get_mapping(mapping[const.MAPPING_ID]))
        stored.pop(const.MAPPING_RADIATION_CALIBRATION, None)

        reloaded = await _reload(hass, stored)

        assert (
            reloaded.get_mapping(mapping[const.MAPPING_ID])[
                const.MAPPING_RADIATION_CALIBRATION
            ]
            == []
        )

    async def test_a_recorded_calibration_survives_a_reload(self, hass):
        store = SmartIrrigationStorage(hass)
        await store.async_load()
        mapping = await store.async_create_mapping(
            {const.MAPPING_NAME: "GW", const.MAPPING_MAPPINGS: {}}
        )
        entries = [["2026-05-22", 20.0, 25.0, 40.0]]
        await store.async_update_mapping(
            mapping[const.MAPPING_ID],
            {const.MAPPING_RADIATION_CALIBRATION: entries},
        )
        stored = dict(store.get_mapping(mapping[const.MAPPING_ID]))

        reloaded = await _reload(hass, stored)

        assert (
            reloaded.get_mapping(mapping[const.MAPPING_ID])[
                const.MAPPING_RADIATION_CALIBRATION
            ]
            == entries
        )


class TestOpenMeteoHandsOverItsRadiation:
    def test_the_hourly_mean_comes_back_as_energy_at_absolute_instants(self):
        client = OpenMeteoClient(latitude=39.7, longitude=-84.1, elevation=311)
        client._cached_doc = {
            "utc_offset_seconds": -4 * 3600,
            "hourly": {
                "time": ["2026-06-21T08:00", "2026-06-21T09:00", "2026-06-21T10:00"],
                "shortwave_radiation": [500.0, None, 250.0],
            },
        }

        utc = datetime.timezone.utc
        assert client.get_hourly_radiation_forecast() == [
            (datetime.datetime(2026, 6, 21, 12, tzinfo=utc), pytest.approx(1.8)),
            (datetime.datetime(2026, 6, 21, 14, tzinfo=utc), pytest.approx(0.9)),
        ]

    def test_nothing_fetched_yet_is_not_an_error(self):
        client = OpenMeteoClient(latitude=39.7, longitude=-84.1, elevation=311)
        client._cached_doc = {}

        assert client.get_hourly_radiation_forecast() is None

    def test_it_never_issues_a_request_of_its_own(self):
        """Read every refresh and at every commit: it must only ever read the
        document the client's own polling already holds."""
        client = OpenMeteoClient(latitude=39.7, longitude=-84.1, elevation=311)
        client._cached_doc = None
        client._fetch = Mock(side_effect=AssertionError("fetched"))

        assert client.get_hourly_radiation_forecast() is None
        client._fetch.assert_not_called()


class TestTheTierIsPublished:
    async def test_the_sensor_carries_the_radiation_tier(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        c.hass.data[const.DOMAIN]["coordinator"] = c
        _implied, est = _implied_daily(
            c,
            store,
            zone,
            instance,
            module,
            ANCHOR + timedelta(hours=10),
            daily=_daily_forecast(),
        )
        c._zone_estimates_cache = {str(zone[const.ZONE_ID]): est}

        sensor = SmartIrrigationZoneLiveDeficitSensor(
            c.hass, "sensor.ip_live_deficit", zone
        )

        assert sensor.extra_state_attributes["radiation_tier"] == "self_contained"


class TestTheNextRunIsPricedTheSameWay:
    async def test_the_projection_prices_the_remainder_with_the_zone_s_equation(
        self, coordinator
    ):
        c, store = coordinator
        zone, module, instance = await _measuring_zone(c, store, 2.0)
        midday = ANCHOR + timedelta(hours=10)
        store.set_mapping_buffer(
            zone[const.ZONE_MAPPING], _observed_rows(_diurnal_readings(), midday)
        )
        inputs = _inputs_at(instance, module, midday, daily=_daily_forecast())
        est = c._intraday_for_zone(zone, inputs)
        instance.calculate = Mock(wraps=instance.calculate)

        carried = c._carry_estimate_to(zone, est, inputs, midday + timedelta(hours=6))

        assert carried["carried_to_decision"] is True
        assert carried["projected_et"] > 0
        instance.calculate.assert_called()
