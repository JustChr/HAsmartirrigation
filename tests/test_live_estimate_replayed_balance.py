"""The live estimate and the calculation run the SAME water balance.

The intra-day estimate exists to show the path the stored bucket is taking, so
the curve has to arrive at the number the next calculation commits. It did not:
the calculation replayed the window at its own event times while the estimate
lumped it into one update -- ``bucket - et + precip``, capped, then a single
drainage pass over the whole window since the last commit.

That treats every mid-window event as though it had been present from the last
commit onward, and drainage is Brooks-Corey with ``n = 4``, so the error is
strongly non-linear and runs one way. On the live install's zone parameters
(``drainage_rate`` 1.3 in/h, ``maximum_bucket`` 1 in) a 12.7 mm surplus drains
1.57 mm charged over the hour it actually fell and 6.94 mm charged over a 20 h
window: 5.37 mm, or 0.21 in against a 0.394 in ``bucket_threshold``, always in
the direction that reads the zone drier than it is. With
``live_estimate_enabled`` on that number both triggers and sizes real runs, so
it is not a dashboard cosmetic.

Irrigation credited part-way through the window has the same defect and the same
fix, already built for the calculation: a per-zone ledger of ``(when, mm)``. The
estimate reads it and must never consume it.

The equality is the whole point, so it is asserted against a run of the real
``calculate_module`` over a real store rather than against a hand-computed
number -- a reimplementation of the balance in the test would agree with itself
however the two paths drift.
"""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import homeassistant.util.dt as dt_util
import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.et_estimate import live_balance
from custom_components.smart_irrigation.store import SmartIrrigationStorage

T0 = datetime.datetime(2026, 5, 22, 0, 0, 0)
NOW = T0 + timedelta(hours=24)

# The live install's zone geometry: maximum_bucket 1 in, drainage_rate 1.3 in/h.
# These are what make the lumped/replayed gap worth millimetres rather than
# rounding, and they are the numbers the module docstring's table is computed on.
MAXIMUM_BUCKET = 25.4
DRAINAGE_RATE = 33.02

LAT, LON, ELEV = 39.68987, -84.07865, 311.0


def _readings(rain_at=None):
    """A day of minute rows: a solar bell, steady air, and a cumulative gauge.

    ``rain_at`` is ``{hour: mm}`` delivered inside that hour. A cumulative gauge
    is what the DELTA aggregate reads, and it is the shape that lets rain land
    unevenly -- which is the case the two forms disagree on.
    """
    rain_at = rain_at or {}
    readings = []
    cumulative = 0.0
    for hour in range(24):
        for minute in range(0, 60, 10):
            cumulative += rain_at.get(hour, 0.0) / 6
            readings.append(
                {
                    const.RETRIEVED_AT: T0 + timedelta(hours=hour, minutes=minute),
                    const.MAPPING_TEMPERATURE: 20.0,
                    const.MAPPING_HUMIDITY: 55.0,
                    const.MAPPING_WINDSPEED: 1.5,
                    # W/m2 -> MJ/m2/day, which is what the buffer stores.
                    const.MAPPING_SOLRAD: (
                        700.0 * 0.0864 * (hour + minute / 60.0 - 6) / 8
                        if 6 <= hour < 20
                        else 0.0
                    ),
                    const.MAPPING_PRECIPITATION: cumulative,
                }
            )
    return readings


@pytest.fixture
async def coordinator(hass):
    """A real coordinator over a real in-memory store, hourly form opted in."""
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    await store.async_update_config(
        {const.CONF_CONTINUOUS_UPDATES: True, const.CONF_HOURLY_CALCULATION: True}
    )
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    # Both halves resolve the site from these, so pinning them here is what makes
    # the two priced windows comparable at all.
    c._effective_latitude = LAT
    c._effective_longitude = LON
    c._effective_elevation = ELEV
    return c, store


async def _zone(c, store, bucket, *, rain_at=None, events=None, drainage=DRAINAGE_RATE):
    """A zone whose DAILY calculation sums hourly ETo, over a real buffer.

    The module instance reports the axis-A configuration the hourly form is
    gated on -- PyETO, DontEstimate, no forecast days -- because that is also
    what ``_hourly_form_applies`` reads on the estimate side. Anything else and
    the two would be comparing different equations.
    """
    mapping = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "GW",
            const.MAPPING_MAPPINGS: {},
            const.MAPPING_DATA: _readings(rain_at),
        }
    )
    module = await store.async_create_module(
        {
            const.MODULE_NAME: "PyETO",
            "description": "",
            "config": {
                const.CONF_PYETO_SOLRAD_BEHAVIOR: "3",  # DontEstimate
                const.CONF_PYETO_FORECAST_DAYS: 0,
            },
        }
    )
    instance = Mock()
    instance._solrad_behavior = "3"
    instance.forecast_days = 0
    instance.calculate = Mock(return_value=0.0)
    c.getModuleInstanceByID = AsyncMock(return_value=instance)
    zone = await store.async_create_zone(
        {
            const.ZONE_NAME: "Front",
            const.ZONE_MAPPING: mapping[const.MAPPING_ID],
            const.ZONE_MODULE: module[const.MODULE_ID],
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_BUCKET: bucket,
            const.ZONE_MAXIMUM_BUCKET: MAXIMUM_BUCKET,
            const.ZONE_DRAINAGE_RATE: drainage,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_MAXIMUM_DURATION: 3600,
            const.ZONE_LEAD_TIME: 0,
            # One anchor: the estimate floors last_calculated at the consume
            # watermark, and on a healthy install the daily calc writes both from
            # one ``now``. Equal here for the same reason.
            const.ZONE_LAST_CONSUMED: T0,
            const.ZONE_LAST_CALCULATED: T0,
        }
    )
    zone = dict(zone)
    if events is not None:
        zone[const.ZONE_PENDING_BUCKET_EVENTS] = events
    return zone


def _inputs(now=NOW):
    """A sensor-only install: no weather client, so the buffer is the source.

    The geometry matches what ``_hourly_et_for_zone`` resolves for itself, which
    under pytest is a UTC site. A different offset on one side would price the
    same window differently and the comparison would be meaningless.
    """
    return {
        "client": None,
        "rows": None,
        "tz": None,
        "forecast": None,
        "now": now,
        "tz_offset_h": 0.0,
        "site_tz": dt_util.DEFAULT_TIME_ZONE,
    }


async def _committed(c, zone, now=NOW):
    """What the daily calculation would write for this zone, in mm."""
    weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
    data = await c.calculate_module(zone, weatherdata, None, now=now)
    return data


class TestTheLiveCurveLandsOnTheCommittedBucket:
    """The property the whole feature rests on. Rain that falls unevenly is the
    case the two forms disagree on, because the lumped one books all of it at
    the window start and then drains it for the entire window."""

    async def test_uneven_rain_gives_the_same_bucket_as_the_calculation(
        self, coordinator
    ):
        c, store = coordinator
        # A dry morning, a burst at 20:00. Booked at the window start it is
        # charged 20 hours of drainage it never saw.
        rain = {20: 14.0}
        zone = await _zone(c, store, 2.0, rain_at=rain)

        est = c._intraday_for_zone(zone, _inputs())
        data = await _committed(c, zone)

        assert est["available"] is True
        assert est["method"] == "hourly_sensor"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_the_drainage_trace_matches_the_committed_drainage(self, coordinator):
        """Published as its own trace, so it has to be the same water the
        calculation books -- not merely a figure that happens to close the
        identity against a differently-derived deficit."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})

        est = c._intraday_for_zone(zone, _inputs())
        data = await _committed(c, zone)

        assert est["drainage_since"] == pytest.approx(
            data[const.ZONE_CURRENT_DRAINAGE], abs=0.01
        )

    async def test_rain_spread_through_the_day_also_agrees(self, coordinator):
        """The other half of the lumped form's error: spread-out rain is
        over-clamped, because the drainage that would have made room between
        bursts never happens."""
        c, store = coordinator
        zone = await _zone(c, store, 0.0, rain_at=dict.fromkeys(range(6, 20), 2.0))

        est = c._intraday_for_zone(zone, _inputs())
        data = await _committed(c, zone)

        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_the_lumped_form_would_have_disagreed(self, coordinator):
        """Guards the two tests above against being vacuous.

        If the lumped and replayed forms landed on the same number, the equality
        would hold no matter which one the estimate ran and these tests would
        pin nothing. This is the gap that was on the dashboard.
        """
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})

        est = c._intraday_for_zone(zone, _inputs())
        lumped, _drained = live_balance(
            2.0,
            est["et_since"],
            est["precip_since"],
            MAXIMUM_BUCKET,
            drainage_rate=DRAINAGE_RATE,
            elapsed_hours=24.0,
        )

        # Over-drains, so the lumped bucket is the drier one. The gap measures
        # 2.9 mm on this window -- 0.11 in against the live install's 0.394 in
        # bucket_threshold, and it sizes the run as well as triggering it.
        assert lumped < est["live_deficit"] - 2.0

    async def test_a_dry_deficit_window_is_unchanged(self, coordinator):
        """No rain and a bucket below zero: drainage never acts, so replaying
        must return bit-for-bit what lumping did. The change is meant to move
        only the cases where the interleaving matters."""
        c, store = coordinator
        zone = await _zone(c, store, -5.0)

        est = c._intraday_for_zone(zone, _inputs())
        lumped, _drained = live_balance(
            -5.0,
            est["et_since"],
            est["precip_since"],
            MAXIMUM_BUCKET,
            drainage_rate=DRAINAGE_RATE,
            elapsed_hours=24.0,
        )

        assert est["drainage_since"] == 0.0
        assert est["live_deficit"] == pytest.approx(round(lumped, 2), abs=0.01)


class TestTheCreditLedger:
    """Irrigation credited part-way through the window, read from the ledger the
    calculation writes and consumes."""

    async def test_a_late_credit_keeps_more_bucket_than_one_at_the_window_start(
        self, coordinator
    ):
        c, store = coordinator
        late = await _zone(
            c,
            store,
            10.0,
            events=[{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}],
        )
        folded = await _zone(c, store, 10.0)

        with_ledger = c._intraday_for_zone(late, _inputs())
        without = c._intraday_for_zone(folded, _inputs())

        assert with_ledger["live_deficit"] > without["live_deficit"] + 1.0
        # The whole difference is drainage that was never owed.
        assert with_ledger["drainage_since"] < without["drainage_since"]

    async def test_a_credited_window_lands_on_the_committed_bucket(self, coordinator):
        c, store = coordinator
        events = [{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}]
        zone = await _zone(c, store, 10.0, events=events)

        est = c._intraday_for_zone(zone, _inputs())
        # calculate_module consumes the ledger, so it has to run second: the
        # estimate must see the same credits the commit will.
        data = await _committed(c, zone)

        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_the_estimate_does_not_consume_the_ledger(self, coordinator):
        """Read-only. Consuming here would delete credits the calculation has
        not applied yet, and the water would simply vanish from the balance."""
        c, store = coordinator
        events = [{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}]
        zone = await _zone(c, store, 10.0, events=events)

        for _ in range(3):
            c._intraday_for_zone(zone, _inputs())

        assert zone[const.ZONE_PENDING_BUCKET_EVENTS] == events
        stored = store.get_zone(zone[const.ZONE_ID])
        assert stored.get(const.ZONE_PENDING_BUCKET_EVENTS) in ([], None, events)

    async def test_the_estimate_advances_no_watermark_and_writes_no_bucket(
        self, coordinator
    ):
        c, store = coordinator
        zone = await _zone(c, store, 10.0, rain_at={20: 14.0})
        before = dict(store.get_zone(zone[const.ZONE_ID]))

        c._intraday_for_zone(zone, _inputs())

        after = store.get_zone(zone[const.ZONE_ID])
        for field in (
            const.ZONE_BUCKET,
            const.ZONE_LAST_CONSUMED,
            const.ZONE_LAST_CALCULATED,
        ):
            assert after.get(field) == before.get(field)


class TestFallingBackToTheLumpedForm:
    """Every refusal has to leave the estimate available and lumped, which is
    the behaviour that preceded this -- never absent, never a fabricated curve."""

    async def test_a_window_that_cannot_be_sub_stepped_still_produces_an_estimate(
        self, coordinator, monkeypatch
    ):
        import custom_components.smart_irrigation.live_estimate as le

        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})
        monkeypatch.setattr(le, "build_substeps", lambda *a, **kw: None)

        est = c._intraday_for_zone(zone, _inputs())

        assert est["available"] is True
        assert est["method"] == "hourly_sensor"
        lumped, drained = live_balance(
            2.0,
            est["et_since"],
            est["precip_since"],
            MAXIMUM_BUCKET,
            drainage_rate=DRAINAGE_RATE,
            elapsed_hours=24.0,
        )
        assert est["live_deficit"] == pytest.approx(round(lumped, 2), abs=0.01)

    async def test_precipitation_that_does_not_reconcile_falls_back(
        self, coordinator, monkeypatch
    ):
        """The rain in the balance and the rain published beside it are the same
        water. A disagreement means an assumption broke, and lumping is the
        self-consistent answer."""
        import custom_components.smart_irrigation.live_estimate as le

        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})
        monkeypatch.setattr(
            le.LiveEstimateMixin,
            "_observed_precip_since_mm",
            lambda self, zone, anchor: 99.0,
        )

        est = c._intraday_for_zone(zone, _inputs())

        assert est["available"] is True
        lumped, _drained = live_balance(
            2.0,
            est["et_since"],
            99.0,
            MAXIMUM_BUCKET,
            drainage_rate=DRAINAGE_RATE,
            elapsed_hours=24.0,
        )
        assert est["live_deficit"] == pytest.approx(round(lumped, 2), abs=0.01)


class TestTheCompletedHourCarryFeedsTheReplay:
    """The carry is what keeps a minute-cadence refresh cheap, and the replay
    needs an ET quantum for EVERY hour of the window. Carrying a bare total
    would leave the earlier hours missing from ``build_substeps``' ``hourly_et``,
    which is a documented reason for it to refuse -- so the estimate would
    silently fall back to the lumped form for as long as the carry stayed warm,
    which on a live install is always."""

    async def test_a_warm_carry_still_replays_and_agrees_with_a_cold_one(
        self, coordinator
    ):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})

        # Walk one instance through the window an hour at a time, so every
        # refresh but the first is served from the carry.
        for hour in range(1, 25):
            warm = c._intraday_for_zone(zone, _inputs(T0 + timedelta(hours=hour)))

        cold_coordinator = SmartIrrigationCoordinator.__new__(
            SmartIrrigationCoordinator
        )
        cold_coordinator.hass = c.hass
        cold_coordinator.store = store
        cold_coordinator._effective_latitude = LAT
        cold_coordinator._effective_longitude = LON
        cold_coordinator._effective_elevation = ELEV
        cold = cold_coordinator._intraday_for_zone(zone, _inputs())

        assert warm["et_since"] == pytest.approx(cold["et_since"], abs=1e-6)
        assert warm["live_deficit"] == pytest.approx(cold["live_deficit"], abs=0.01)

    async def test_a_warm_carry_still_lands_on_the_committed_bucket(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})

        for hour in range(1, 25):
            est = c._intraday_for_zone(zone, _inputs(T0 + timedelta(hours=hour)))
        data = await _committed(c, zone)

        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )
