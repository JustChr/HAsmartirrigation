"""The sub-stepped water balance: rain, drainage and the clamp interleaved.

The shipped single-shot form lands a whole window's rain at the window start,
clamps it against ``maximum_bucket`` there, and drains whatever survives for the
full window. Both errors run one way: late rain is over-drained, and rain spread
through the day is over-clamped because the drainage that would have made room
between bursts never happens. Across 140 real rain days that booked 186 mm/year
as runoff that never occurred and cost up to 12.7 mm of bucket, which is 88
minutes of runtime on the slowest zone on this install.

These pin the properties that removal depends on: the ET total is conserved, the
precipitation the sub-steps see is the same water the aggregate reports, the
balance closes, and a dry deficit window is bit-for-bit what it was before.
"""

import datetime
import math
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.et_estimate import (
    drained_over_window,
    replay_water_balance,
)
from custom_components.smart_irrigation.store import SmartIrrigationStorage
from custom_components.smart_irrigation.weather_aggregate import (
    aggregate_window,
    build_substeps,
)

T0 = datetime.datetime(2026, 5, 22, 0, 0, 0)

# The live install's zone geometry, from the plan's water-balance matrix. The
# once-daily model pins every heavy rain day at exactly +5.57 mm with these,
# which is what identifies them.
MAXIMUM_BUCKET = 25.4
DRAINAGE_RATE = 33.02


def _day(rain_per_hour, *, solar=True, minutes=60, et=None):
    """A day of per-minute rows: a cumulative rain gauge plus a solar bell."""
    readings = []
    cumulative = 0.0
    for hour in range(24):
        for minute in range(minutes):
            cumulative += rain_per_hour.get(hour, 0.0) / minutes
            row = {
                const.RETRIEVED_AT: T0 + timedelta(hours=hour, minutes=minute),
                const.MAPPING_PRECIPITATION: cumulative,
            }
            if et is not None:
                row[const.MAPPING_EVAPOTRANSPIRATION] = et
            if solar:
                row[const.MAPPING_SOLRAD] = (
                    70.0 * math.sin(math.pi * (hour + minute / minutes - 6) / 14)
                    if 6 <= hour < 20
                    else 0.0
                )
            readings.append(row)
    return readings


def _single_shot(bucket, delta):
    """What the un-stepped form produces, for comparison."""
    new = bucket + delta
    runoff = max(0.0, new - MAXIMUM_BUCKET)
    new = min(new, MAXIMUM_BUCKET)
    drainage = drained_over_window(new, DRAINAGE_RATE, 24.0, MAXIMUM_BUCKET)
    return new - drainage, drainage, runoff


def _replay(readings, bucket, et_total):
    steps = build_substeps(readings, T0, {}, now=T0 + timedelta(hours=24))
    assert steps is not None
    return steps, replay_water_balance(
        bucket, et_total, steps, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
    )


class TestSubStepConstruction:
    def test_et_weights_sum_to_one(self):
        """However the window is cut, the same ET is charged.

        The weights are the only thing sub-stepping changes about ET, so if they
        did not sum to 1 the day's evapotranspiration would silently change.
        """
        steps = build_substeps(_day({14: 5.0}), T0, {}, now=T0 + timedelta(hours=24))
        assert sum(s.et_weight for s in steps) == pytest.approx(1.0, abs=1e-12)

    def test_et_is_solar_weighted_not_spread_flat(self):
        """ETo is ~93% radiation-driven here, so it follows the pyranometer.

        Charging it evenly by elapsed time would put a twelfth of the day's ET
        into the middle of the night, where FAO-56 hourly says it is essentially
        zero, and would leave a visible staircase for anything publishing the
        intra-day curve.
        """
        readings = _day({})
        steps = build_substeps(readings, T0, {}, now=T0 + timedelta(hours=24))
        # Steps are cut on wall-clock hours with no rain, so one per hour.
        assert len(steps) == 24
        night = [s.et_weight for h, s in enumerate(steps) if h < 6 or h >= 20]
        assert sum(night) == pytest.approx(0.0, abs=1e-12)
        # Solar peaks at 13:00 on this bell, and that hour carries the most ET.
        assert max(range(24), key=lambda h: steps[h].et_weight) == 13

    def test_falls_back_to_elapsed_time_when_there_is_no_radiation(self):
        """A window entirely after dark, or a group with no solar mapped.

        The weights would be all-zero and the window's ET would have nowhere to
        go, so it is spread flat instead.
        """
        steps = build_substeps(
            _day({}, solar=False), T0, {}, now=T0 + timedelta(hours=24)
        )
        assert sum(s.et_weight for s in steps) == pytest.approx(1.0)
        assert steps[0].et_weight == pytest.approx(steps[12].et_weight)

    def test_steps_are_cut_at_wall_clock_hours_even_with_no_events(self):
        """The hourly ceiling bounds how long a single step may run.

        Aligned to the clock rather than to the window start so the cuts
        coincide with the hour FAO-56 hourly ETo is defined on.
        """
        readings = [
            {
                const.RETRIEVED_AT: T0 + timedelta(hours=3, minutes=17),
                const.MAPPING_TEMPERATURE: 15.0,
            }
        ]
        start = T0 + timedelta(hours=2, minutes=30)
        steps = build_substeps(
            readings, start, {}, now=T0 + timedelta(hours=6, minutes=10)
        )
        # 02:30->03:00, 03:00->04:00, 04:00->05:00, 05:00->06:00, 06:00->06:10
        assert [s.dt_hours for s in steps] == pytest.approx([0.5, 1.0, 1.0, 1.0, 1 / 6])


class TestPrecipitationReconciles:
    """The sub-steps and the aggregate must see the same water.

    ZONE_DELTA is published from the aggregate while the bucket is driven by the
    sub-step increments. If the two disagreed, the ledger would not add up, and
    ``_substeps_for_zone`` refuses the sub-stepped path rather than let that
    happen — so these guard the property that keeps it enabled.
    """

    def test_delta_gauge_increments_match_the_aggregate(self):
        readings = _day({3: 2.0, 14: 8.0, 22: 1.5})
        now = T0 + timedelta(hours=24)
        aggregated = aggregate_window(readings, T0, {}, now=now)
        steps = build_substeps(readings, T0, {}, now=now)
        assert sum(s.precip_mm for s in steps) == pytest.approx(
            aggregated[const.MAPPING_PRECIPITATION], abs=1e-9
        )

    def test_delta_gauge_midnight_reset_matches_the_aggregate(self):
        """A rain gauge that resets to 0 must not read as negative rain."""
        readings = [
            {
                const.RETRIEVED_AT: T0 + timedelta(hours=h),
                const.MAPPING_PRECIPITATION: v,
            }
            for h, v in enumerate([5.0, 7.0, 0.0, 2.0])
        ]
        now = T0 + timedelta(hours=4)
        aggregated = aggregate_window(readings, T0, {}, now=now)
        steps = build_substeps(readings, T0, {}, now=now)
        assert aggregated[const.MAPPING_PRECIPITATION] == 4.0
        assert sum(s.precip_mm for s in steps) == pytest.approx(4.0)

    def test_weather_service_rate_integrates_to_the_aggregate(self):
        config = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
            }
        }
        readings = [
            {
                const.RETRIEVED_AT: T0 + timedelta(hours=h),
                const.MAPPING_PRECIPITATION: v,
            }
            for h, v in enumerate([0.0, 2.0, 4.0, 0.0])
        ]
        now = T0 + timedelta(hours=4)
        aggregated = aggregate_window(readings, T0, config, now=now)
        steps = build_substeps(readings, T0, config, now=now)
        assert sum(s.precip_mm for s in steps) == pytest.approx(
            aggregated[const.MAPPING_PRECIPITATION], abs=1e-9
        )

    def test_no_time_structure_declines_to_sub_step(self):
        """A lone rate sample is reported verbatim; there is no interval for it.

        Returning None keeps the single-shot path, so the failure mode is
        today's behaviour rather than a fabricated series.
        """
        config = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
            }
        }
        readings = [{const.RETRIEVED_AT: T0, const.MAPPING_PRECIPITATION: 2.0}]
        assert (
            build_substeps(readings, None, config, now=T0 + timedelta(hours=1)) is None
        )

    def test_unstamped_rows_decline_to_sub_step(self):
        readings = [
            {const.RETRIEVED_AT: T0, const.MAPPING_PRECIPITATION: 0.0},
            {const.RETRIEVED_AT: None, const.MAPPING_PRECIPITATION: 5.0},
            {
                const.RETRIEVED_AT: T0 + timedelta(hours=2),
                const.MAPPING_PRECIPITATION: 6.0,
            },
        ]
        assert build_substeps(readings, None, {}, now=T0 + timedelta(hours=3)) is None


class TestReplay:
    def test_water_is_conserved(self):
        """bucket + ET + rain - drainage - runoff, exactly.

        Every published number comes off this identity, and it is what lets the
        explanation state the balance as one line.
        """
        readings = _day({16: 12.0, 17: 12.0, 18: 14.1})
        steps, (bucket, drainage, runoff) = _replay(readings, 2.97, -3.0)
        rain = sum(s.precip_mm for s in steps)
        assert bucket == pytest.approx(2.97 - 3.0 + rain - drainage - runoff, abs=1e-9)

    def test_spread_rain_stops_being_booked_as_runoff(self):
        """The headline effect, at the live install's real zone geometry.

        38.1 mm falling over an afternoon never exceeds field capacity, because
        the surplus drains between the hours. Applied in one lump at the window
        start it does exceed it, and the excess is discarded outright.
        """
        readings = _day({h: 38.10 / 6 for h in range(16, 22)})
        steps, (bucket, _drainage, runoff) = _replay(readings, 2.97, -3.0)
        rain = sum(s.precip_mm for s in steps)
        lumped, _, lumped_runoff = _single_shot(2.97, -3.0 + rain)

        assert lumped_runoff == pytest.approx(12.67, abs=0.01)
        assert runoff == 0.0
        # The discarded water is real: it is bucket the zone should have had.
        assert lumped == pytest.approx(5.57, abs=0.01)
        assert bucket > lumped + 5.0

    def test_intra_window_rain_timing_now_moves_the_bucket(self):
        """Late rain is no longer charged a full window of drainage.

        The single-shot form cannot see timing at all: both profiles carry the
        same total, so they give the identical answer. Sub-stepping resolves
        them, which is the whole point.
        """
        early = _day({5: 10.0})
        late = _day({22: 10.0})
        _, (bucket_early, _, _) = _replay(early, 20.0, -3.0)
        _, (bucket_late, _, _) = _replay(late, 20.0, -3.0)

        lumped_early = _single_shot(20.0, -3.0 + 10.0)[0]
        lumped_late = _single_shot(20.0, -3.0 + 10.0)[0]
        assert lumped_early == lumped_late

        assert bucket_late > bucket_early + 5.0

    def test_a_dry_deficit_window_is_unchanged(self):
        """No rain and a bucket below field capacity: nothing to interleave.

        Drainage acts only on surplus above field capacity, so this window has
        no drainage and no clamp, and the sub-stepped answer must be exactly the
        single-shot one. This install sits here for most of late summer.
        """
        readings = _day({})
        _steps, (bucket, drainage, runoff) = _replay(readings, -12.0, -3.5)
        lumped, lumped_drainage, lumped_runoff = _single_shot(-12.0, -3.5)
        assert bucket == pytest.approx(lumped, abs=1e-12)
        assert drainage == lumped_drainage == 0.0
        assert runoff == lumped_runoff == 0.0

    def test_a_zero_maximum_bucket_still_clamps_without_scaling_drainage(self):
        """maximum_bucket 0 clamps but has no field capacity to scale against.

        Brooks-Corey divides by it, so drainage falls back to a constant rate --
        the same split the single-shot path makes.
        """
        readings = _day({10: 5.0})
        steps = build_substeps(readings, T0, {}, now=T0 + timedelta(hours=24))
        bucket, _drainage, runoff = replay_water_balance(
            0.0, -1.0, steps, DRAINAGE_RATE, 0.0, None
        )
        assert bucket <= 0.0
        assert runoff > 0.0


class TestMidWindowIrrigationCredits:
    """Water put in the bucket part-way through the window, not at its start.

    The replay reads the stored bucket as the level the window OPENED at, and a
    run that overshoots the deficit leaves a surplus behind (every credit path
    writes ``pre_bucket + depth``, clamped only at ``maximum_bucket`` -- the
    deficit is not an input). Drainage only bites on a surplus, so that surplus
    is then charged the whole window instead of the hours it was really there,
    and the zone reads drier than it is. It does not wash out either: once the
    zone is back in deficit drainage stops acting and the gap is frozen in.
    """

    def test_a_credit_is_booked_on_the_step_it_landed_in(self):
        readings = _day({})
        steps = build_substeps(
            readings,
            T0,
            {},
            now=T0 + timedelta(hours=24),
            applied=[(T0 + timedelta(hours=20, minutes=30), 8.0)],
        )
        assert sum(s.applied_mm for s in steps) == pytest.approx(8.0)
        # Its time earns a cut, so the credit ends the step that contains it and
        # nothing before 20:30 has seen the water.
        elapsed = 0.0
        for step in steps:
            elapsed += step.dt_hours
            if step.applied_mm:
                assert elapsed == pytest.approx(20.5)

    def test_a_credit_stamped_outside_the_window_is_still_applied(self):
        """The stored bucket already holds it, so dropping it deletes water."""
        readings = _day({})
        for stamp in (T0 - timedelta(hours=3), T0 + timedelta(hours=30)):
            steps = build_substeps(
                readings, T0, {}, now=T0 + timedelta(hours=24), applied=[(stamp, 4.0)]
            )
            assert sum(s.applied_mm for s in steps) == pytest.approx(4.0)

    def test_credits_do_not_disturb_the_precipitation_ledger(self):
        """ZONE_DELTA is published from the aggregate, the bucket from these.

        Folding irrigation into ``precip_mm`` would make the two disagree and
        drop the whole zone back to the single-shot path.
        """
        readings = _day({16: 6.0})
        steps = build_substeps(
            readings,
            T0,
            {},
            now=T0 + timedelta(hours=24),
            applied=[(T0 + timedelta(hours=9), 5.0)],
        )
        assert sum(s.precip_mm for s in steps) == pytest.approx(6.0)

    def test_water_is_conserved_with_a_credit(self):
        readings = _day({})
        steps = build_substeps(
            readings,
            T0,
            {},
            now=T0 + timedelta(hours=24),
            applied=[(T0 + timedelta(hours=10), 9.0)],
        )
        applied = sum(s.applied_mm for s in steps)
        bucket, drainage, runoff = replay_water_balance(
            0.0, -3.0, steps, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
        )
        assert bucket == pytest.approx(
            0.0 - 3.0 + applied - drainage - runoff, abs=1e-9
        )

    def test_the_credit_is_not_charged_the_hours_before_it_was_applied(self):
        """The defect, stated as the difference the fix makes.

        Same water, same window, same total: one run replays it from the window
        start (what a stored bucket carrying the credit does), the other books it
        at 20:00. The second keeps materially more bucket, and the first is the
        one that reads drier and waters again sooner.
        """
        readings = _day({})
        late = build_substeps(
            readings,
            T0,
            {},
            now=T0 + timedelta(hours=24),
            applied=[(T0 + timedelta(hours=20), 10.0)],
        )
        at_start = build_substeps(readings, T0, {}, now=T0 + timedelta(hours=24))
        booked_late = replay_water_balance(
            0.0, -4.0, late, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
        )[0]
        folded_in = replay_water_balance(
            10.0, -4.0, at_start, DRAINAGE_RATE, MAXIMUM_BUCKET, MAXIMUM_BUCKET
        )[0]
        assert booked_late > folded_in + 1.0


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
    # The replay is gated behind hourlycalculation, so the tests that exercise it
    # have to opt in the way a user does. TestTheHourlyCalculationGate below pins
    # what happens without it. continuousupdates is on as well because it still
    # selects the time-weighted window aggregate these numbers were taken against.
    await store.async_update_config(
        {const.CONF_CONTINUOUS_UPDATES: True, const.CONF_HOURLY_CALCULATION: True}
    )
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    return c, store


class TestThroughCalculateModule:
    """End to end, because the two halves are wired through different objects.

    The precipitation total reaches ZONE_DELTA through ``aggregate_window`` and
    the bucket through ``build_substeps``. Only a run of the real method proves
    they meet.
    """

    async def _zone_with_a_rain_day(self, c, store, rain_per_hour, bucket, *, et):
        mapping = await store.async_create_mapping(
            {
                const.MAPPING_NAME: "GW",
                const.MAPPING_MAPPINGS: {},
                const.MAPPING_DATA: _day(rain_per_hour, minutes=6),
            }
        )
        # PyETO, because it is the only module that folds precipitation into the
        # deficit, and rain is what the sub-stepping exists for. Its ET is stubbed
        # so every other number in the test is hand-computable.
        module = await store.async_create_module(
            {const.MODULE_NAME: "PyETO", "description": "", "config": {}}
        )
        instance = Mock()
        instance.calculate = Mock(return_value=-et)
        c.getModuleInstanceByID = AsyncMock(return_value=instance)
        zone = await store.async_create_zone(
            {
                const.ZONE_NAME: "Front",
                const.ZONE_MAPPING: mapping[const.MAPPING_ID],
                const.ZONE_MODULE: module[const.MODULE_ID],
                const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
                const.ZONE_BUCKET: bucket,
                const.ZONE_MAXIMUM_BUCKET: MAXIMUM_BUCKET,
                const.ZONE_DRAINAGE_RATE: DRAINAGE_RATE,
                const.ZONE_THROUGHPUT: 10.0,
                const.ZONE_SIZE: 10.0,
                const.ZONE_MULTIPLIER: 1.0,
                const.ZONE_MAXIMUM_DURATION: 3600,
                const.ZONE_LEAD_TIME: 0,
                const.ZONE_LAST_CONSUMED: T0,
            }
        )
        return zone

    async def test_the_ledger_balances_and_no_runoff_is_invented(self, coordinator):
        c, store = coordinator
        zone = await self._zone_with_a_rain_day(
            c, store, {h: 38.10 / 6 for h in range(16, 22)}, 2.97, et=3.0
        )
        now = T0 + timedelta(hours=24)
        weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
        data = await c.calculate_module(zone, weatherdata, None, now=now)

        delta = data[const.ZONE_DELTA]
        drainage = data[const.ZONE_CURRENT_DRAINAGE]
        new_bucket = data[const.ZONE_BUCKET]
        # The explanation states this identity as one line, so it has to hold.
        # Runoff is the only term not stored, and it is 0 on this day.
        assert new_bucket == pytest.approx(2.97 + delta - drainage, abs=1e-6)
        # Lumping the same rain would have clamped and discarded ~12.7 mm.
        assert new_bucket > _single_shot(2.97, delta)[0] + 5.0
        assert "replayed across the window" in data[const.ZONE_EXPLANATION]

    async def test_a_zone_with_no_sensor_group_keeps_the_single_shot_path(
        self, coordinator
    ):
        """No mapping means no buffer to replay; the old arithmetic still runs."""
        c, store = coordinator
        module = await store.async_create_module(
            {const.MODULE_NAME: "PyETO", "description": "", "config": {}}
        )
        instance = Mock()
        instance.calculate = Mock(return_value=-5.0)
        c.getModuleInstanceByID = AsyncMock(return_value=instance)
        zone = await store.async_create_zone(
            {
                const.ZONE_NAME: "Orphan",
                const.ZONE_MODULE: module[const.MODULE_ID],
                const.ZONE_BUCKET: 0.0,
                const.ZONE_MAXIMUM_BUCKET: MAXIMUM_BUCKET,
                const.ZONE_DRAINAGE_RATE: 0.0,
                const.ZONE_THROUGHPUT: 10.0,
                const.ZONE_SIZE: 10.0,
                const.ZONE_MULTIPLIER: 1.0,
                const.ZONE_MAXIMUM_DURATION: 3600,
                const.ZONE_LEAD_TIME: 0,
            }
        )
        data = await c.calculate_module(
            zone, {const.MAPPING_DATA_MULTIPLIER: 1.0}, None
        )
        assert data[const.ZONE_BUCKET] == pytest.approx(-5.0)
        assert "replayed across the window" not in data[const.ZONE_EXPLANATION]


class TestTheHourlyCalculationGate:
    """Polling keeps the single-shot balance, byte for byte.

    The replay is a better number on the same data, but it moves the stored
    bucket on any install that maps precipitation, so it does not arrive
    unrequested. An install that has opted into nothing keeps the arithmetic it
    already had.
    """

    async def test_the_flag_off_keeps_the_single_shot_balance(self, coordinator):
        c, store = coordinator
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: False})
        zone = await TestThroughCalculateModule()._zone_with_a_rain_day(
            c, store, {h: 38.10 / 6 for h in range(16, 22)}, 2.97, et=3.0
        )
        now = T0 + timedelta(hours=24)
        weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
        data = await c.calculate_module(zone, weatherdata, None, now=now)

        expected, drainage, _runoff = _single_shot(2.97, data[const.ZONE_DELTA])
        assert data[const.ZONE_BUCKET] == pytest.approx(expected, abs=1e-6)
        assert data[const.ZONE_CURRENT_DRAINAGE] == pytest.approx(drainage, abs=1e-6)
        assert "replayed across the window" not in data[const.ZONE_EXPLANATION]

    async def test_the_same_window_replays_once_the_flag_is_on(self, coordinator):
        """The gate is the only difference, so the same day must move the bucket."""
        c, store = coordinator
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: False})
        zone = await TestThroughCalculateModule()._zone_with_a_rain_day(
            c, store, {h: 38.10 / 6 for h in range(16, 22)}, 2.97, et=3.0
        )
        now = T0 + timedelta(hours=24)
        weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
        polled = await c.calculate_module(zone, weatherdata, None, now=now)

        await store.async_update_config({const.CONF_HOURLY_CALCULATION: True})
        zone = store.get_zone(zone[const.ZONE_ID])
        zone[const.ZONE_BUCKET] = 2.97
        zone[const.ZONE_LAST_CONSUMED] = T0
        weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
        replayed = await c.calculate_module(zone, weatherdata, None, now=now)

        # Lumping the same rain clamps it against maximum_bucket at the window
        # start and discards the excess; replaying it keeps that water.
        assert replayed[const.ZONE_BUCKET] > polled[const.ZONE_BUCKET] + 5.0
        assert "replayed across the window" in replayed[const.ZONE_EXPLANATION]
