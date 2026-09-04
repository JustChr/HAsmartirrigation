"""The live estimate and the calculation run the SAME water balance.

The intra-day estimate exists to show the path the stored bucket is taking, so
the curve has to arrive at the number the next calculation commits. It did not:
the calculation replayed the window at its own event times while the estimate
lumped it into one update -- ``bucket - et + precip``, capped, then a single
drainage pass over the whole window since the last commit.

That treats every mid-window event as though it had been present from the last
commit onward, and drainage is Brooks-Corey with ``n = 4``, so the error is
strongly non-linear and does not cancel over a window. On the live install's
zone parameters (``drainage_rate`` 1.3 in/h, ``maximum_bucket`` 1 in) a 12.7 mm
surplus drains 1.57 mm charged over the hour it actually fell and 6.94 mm
charged over a 20 h window: 5.37 mm, or 0.21 in against a 0.394 in
``bucket_threshold``.

Which WAY the error runs depends on when the rain fell, because lumping makes
two opposing mistakes. It over-drains rain, charging a late burst for hours of
drainage it never saw, and it under-drains the standing bucket, netting the
window's whole ET before draining anything so the surplus is drained from a
lower level than it ever sat at. A late burst therefore reads the zone drier
than it is and an early one reads it wetter. Both signs are pinned below; a
suite that only ever put the rain late would pass with the balance inverted over
half its input space. With ``live_estimate_enabled`` on that number both
triggers and sizes real runs, so it is not a dashboard cosmetic.

Irrigation credited part-way through the window has the same defect and the same
fix, already built for the calculation: a per-zone ledger of ``(when, mm)``. The
estimate reads it and must never consume it.

Which balance form a zone gets follows the commit's own condition, not the
estimate's evapotranspiration source: a zone whose commit replays gets a
replayed estimate whether that estimate priced the window from the buffer, from
a weather client's hourly series, or from the temperature-seeded proxy. The ET
sources themselves are a separate axis and are unchanged.

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

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.et_estimate import live_balance
from custom_components.irrigation_plus.sensor import (
    SmartIrrigationZoneLiveDeficitSensor,
)
from custom_components.irrigation_plus.store import SmartIrrigationStorage

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


async def _zone(
    c,
    store,
    bucket,
    *,
    rain_at=None,
    events=None,
    drainage=DRAINAGE_RATE,
    solrad="3",
    readings=None,
    mappings_config=None,
    module_name="PyETO",
):
    """A zone whose DAILY calculation sums hourly ETo, over a real buffer.

    The module instance reports the axis-A configuration the hourly form is
    gated on -- PyETO, DontEstimate, no forecast days -- because that is also
    what ``_hourly_form_applies`` reads on the estimate side. Anything else and
    the two would be comparing different equations.

    ``solrad`` is the one knob a case flips: "1" (EstimateFromTemp) is the
    configuration the hourly form declines, which is how a case reaches the
    weather-client source instead of the buffer one.

    ``module_name`` flips the other axis: a module that does not model rain is
    one the commit never replays, so its estimate must not either.
    """
    mapping = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "GW",
            const.MAPPING_MAPPINGS: mappings_config or {},
            const.MAPPING_DATA: _readings(rain_at) if readings is None else readings,
        }
    )
    module = await store.async_create_module(
        {
            const.MODULE_NAME: module_name,
            "description": "",
            "config": {
                const.CONF_PYETO_SOLRAD_BEHAVIOR: solrad,
                const.CONF_PYETO_FORECAST_DAYS: 0,
            },
        }
    )
    instance = Mock()
    instance._solrad_behavior = solrad
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

    async def test_rain_early_in_the_window_also_agrees(self, coordinator):
        """The other sign of the disagreement.

        Every other case here puts the rain late, where the over-drained rain
        dominates and the lumped form reads drier. Rain at hour 2 leaves it the
        WETTER of the two, because the mistake that dominates is the other one:
        lumping nets the window's whole ET before draining, so the standing
        surplus is drained from a lower level than it ever sat at. Agreement has
        to hold on both sides of that sign change.
        """
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={2: 14.0})

        est = c._intraday_for_zone(zone, _inputs())
        data = await _committed(c, zone)

        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_the_lumped_error_changes_sign_with_the_rains_timing(
        self, coordinator
    ):
        """Pins the sign flip itself, so neither direction can be assumed.

        ``test_the_lumped_form_would_have_disagreed`` guards the late-rain cases
        from being vacuous, and it does so with a one-sided comparison. Read on
        its own it invites the conclusion that lumping is always the drier form,
        which is what a compatibility note claiming runs get shorter would rest
        on. It is not: hold everything else equal and move the rain from hour 20
        to hour 2, and the gap reverses.
        """
        c, store = coordinator

        def _lumped(est):
            lumped, _drained = live_balance(
                2.0,
                est["et_since"],
                est["precip_since"],
                MAXIMUM_BUCKET,
                drainage_rate=DRAINAGE_RATE,
                elapsed_hours=24.0,
            )
            return lumped

        late = c._intraday_for_zone(
            await _zone(c, store, 2.0, rain_at={20: 14.0}), _inputs()
        )
        early = c._intraday_for_zone(
            await _zone(c, store, 2.0, rain_at={2: 14.0}), _inputs()
        )

        assert _lumped(late) < late["live_deficit"] - 2.0
        assert _lumped(early) > early["live_deficit"] + 2.0

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
        import custom_components.irrigation_plus.live_estimate as le

        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})
        monkeypatch.setattr(le, "build_substeps", lambda *a, **kw: None)

        est = c._intraday_for_zone(zone, _inputs())

        assert est["available"] is True
        assert est["method"] == "hourly_sensor"
        assert est["balance_form"] == "lumped"
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
        import custom_components.irrigation_plus.live_estimate as le

        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})
        monkeypatch.setattr(
            le.LiveEstimateMixin,
            "_observed_precip_since_mm",
            lambda self, zone, anchor: 99.0,
        )

        est = c._intraday_for_zone(zone, _inputs())

        assert est["available"] is True
        assert est["balance_form"] == "lumped"
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


def _provider_rows(precip_mm_per_row):
    """A weather client's OWN hourly series for the same day.

    A different set of observations of the same site, which is the point: the
    provider is made deliberately wetter than the gauge in the buffer so the two
    cannot be confused for each other.
    """
    return [
        {
            "time": (T0 + timedelta(hours=hour)).isoformat(),
            "hour": hour + 0.5,
            "doy": T0.timetuple().tm_yday,
            "temperature": 20.0,
            "humidity": 55.0,
            "wind_2m": 1.5,
            "solar_mj_h": 2.0 if 6 <= hour < 20 else 0.0,
            "precipitation": precip_mm_per_row,
        }
        for hour in range(24)
    ]


def _client_inputs(rows, now=NOW):
    """A weather-client install: an hourly series, and no forecast behind it."""
    return {
        "client": None,
        "rows": rows,
        "tz": 0.0,
        "forecast": None,
        "now": now,
        "tz_offset_h": 0.0,
        "site_tz": dt_util.DEFAULT_TIME_ZONE,
    }


def _rate_readings(rate_at):
    """The same day with precipitation as a weather-service RATE (mm/h).

    ``rate_at`` is ``{hour: mm/h}`` reported on every row inside that hour. The
    distinction matters: integrated over time an hour at 12 mm/h is 12 mm, while
    plain-summing the ten-minute rows that report it gives 72.
    """
    readings = []
    for hour in range(24):
        for minute in range(0, 60, 10):
            readings.append(
                {
                    const.RETRIEVED_AT: T0 + timedelta(hours=hour, minutes=minute),
                    const.MAPPING_TEMPERATURE: 20.0,
                    const.MAPPING_HUMIDITY: 55.0,
                    const.MAPPING_WINDSPEED: 1.5,
                    const.MAPPING_SOLRAD: (
                        700.0 * 0.0864 * (hour + minute / 60.0 - 6) / 8
                        if 6 <= hour < 20
                        else 0.0
                    ),
                    const.MAPPING_PRECIPITATION: rate_at.get(hour, 0.0),
                }
            )
    return readings


async def _committed_precip(c, zone, now=NOW):
    """The rain the daily calculation would book for this window, in mm."""
    weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
    return weatherdata[const.MAPPING_PRECIPITATION]


class TestTheWeatherClientPathBooksTheBuffersRain:
    """The estimate's rain comes from the reading buffer on EVERY path.

    The client path used to sum the provider's own hourly series, which nothing
    else in the integration reads: the commit always aggregates the buffer. So
    the total shown beside the live bucket was a total the ledger would never
    record, drawn from different observations, plain-summed rather than
    aggregated per source, and cut at whole-hour row boundaries rather than at
    the anchor.

    These zones estimate solar radiation, so the hourly form declines them and
    the weather client is the source -- which is exactly the configuration the
    defect was reachable from.
    """

    async def test_the_client_path_publishes_the_buffers_rain_not_the_providers(
        self, coordinator
    ):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")
        # 24 rows at 1 mm each: 24 mm of provider rain against 14 mm in the gauge.
        rows = _provider_rows(1.0)

        est = c._intraday_for_zone(zone, _client_inputs(rows))

        assert est["available"] is True
        assert est["method"] == "hourly"
        assert est["precip_since"] == pytest.approx(14.0, abs=0.01)
        assert est["precip_since"] != pytest.approx(
            sum(r["precipitation"] for r in rows)
        )

    async def test_the_published_rain_is_the_rain_the_commit_will_book(
        self, coordinator
    ):
        """The externally observable claim, against the real aggregation the
        calculation runs rather than against a number computed here."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(1.0)))
        booked = await _committed_precip(c, zone)

        assert booked == pytest.approx(14.0, abs=0.01)
        assert est["precip_since"] == pytest.approx(booked, abs=0.01)

    async def test_a_dry_provider_does_not_hide_rain_the_gauge_recorded(
        self, coordinator
    ):
        """The error runs both ways. A provider reporting nothing while the
        gauge filled would have shown a dry window against a commit that books
        the rain."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))

        assert est["precip_since"] == pytest.approx(14.0, abs=0.01)

    async def test_a_rate_source_is_integrated_over_time_not_summed(self, coordinator):
        """Aggregated the way the commit aggregates it. A weather-service precip
        source is a rate, so it is Riemann-integrated; the provider series it
        replaces was plain-summed, which over-counts sub-hourly rows by exactly
        the factor of their cadence."""
        c, store = coordinator
        readings = _rate_readings({20: 12.0})
        zone = await _zone(
            c,
            store,
            2.0,
            solrad="1",
            readings=readings,
            mappings_config={
                const.MAPPING_PRECIPITATION: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
                }
            },
        )

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        booked = await _committed_precip(c, zone)

        plain_sum = sum(r[const.MAPPING_PRECIPITATION] for r in readings)
        assert plain_sum == pytest.approx(72.0)
        assert est["precip_since"] == pytest.approx(booked, abs=0.01)
        assert est["precip_since"] == pytest.approx(12.0, abs=0.1)

    async def test_the_client_path_stays_read_only(self, coordinator):
        """Sourcing the buffer must not consume it: no watermark moved, no
        readings taken, no bucket written, no credit ledger cleared."""
        c, store = coordinator
        events = [{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}]
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1", events=events)
        before = dict(store.get_zone(zone[const.ZONE_ID]))
        rows_before = len(store.get_mapping_buffer(zone[const.ZONE_MAPPING]))

        for _ in range(3):
            c._intraday_for_zone(zone, _client_inputs(_provider_rows(1.0)))

        after = store.get_zone(zone[const.ZONE_ID])
        for field in (
            const.ZONE_BUCKET,
            const.ZONE_LAST_CONSUMED,
            const.ZONE_LAST_CALCULATED,
        ):
            assert after.get(field) == before.get(field)
        assert len(store.get_mapping_buffer(zone[const.ZONE_MAPPING])) == rows_before
        assert zone[const.ZONE_PENDING_BUCKET_EVENTS] == events

    async def test_both_halves_of_the_balance_measure_from_one_anchor(
        self, coordinator
    ):
        """A watermark ahead of the last calculation moves the rain window with
        the evapotranspiration one. The provider series was cut at
        ``last_calculated`` floored at the watermark too, so this is the property
        the change had to preserve rather than one it introduces."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")
        # A weather reset advanced the consume watermark past the burst; the
        # readings behind it no longer belong to this window.
        moved = dict(zone)
        moved[const.ZONE_LAST_CONSUMED] = T0 + timedelta(hours=22)

        est = c._intraday_for_zone(moved, _client_inputs(_provider_rows(1.0)))
        whole = c._intraday_for_zone(zone, _client_inputs(_provider_rows(1.0)))

        assert est["precip_since"] == pytest.approx(0.0, abs=0.01)
        assert est["et_since"] < whole["et_since"]


def _proxy_inputs(now=NOW):
    """A weather service with no hourly series at all: the Hargreaves proxy.

    What a forecast-only provider leaves behind, and the third of the three
    evapotranspiration sources. Its window is priced from tomorrow's temperature
    extremes, which is as far from the buffer as an estimate gets.
    """
    return {
        "client": None,
        "rows": None,
        "tz": None,
        "forecast": [{const.MAPPING_MIN_TEMP: 12.0, const.MAPPING_MAX_TEMP: 26.0}],
        "now": now,
        "tz_offset_h": 0.0,
        "site_tz": dt_util.DEFAULT_TIME_ZONE,
    }


async def _committed_with_et(c, zone, et_mm, now=NOW):
    """What the daily calculation writes with its own ET pinned to ``et_mm``.

    The client and proxy sources price the window from data the commit never
    reads -- a provider's own hourly series, or a daily total seeded from
    temperature extremes -- and no configuration makes either agree with the
    daily equation. That divergence is *why* a zone is on one of those paths, so
    it cannot be configured away; pinning both sides to one evapotranspiration
    leaves the balance form as the only difference between them, which is the
    thing under test. The fixture zone has no crop coefficient, so Kc is 1.
    """
    weatherdata, _ = await c._aggregate_for_zone(zone, now=now)
    multiplier = weatherdata.get(const.MAPPING_DATA_MULTIPLIER) or 1.0
    instance = await c.getModuleInstanceByID(zone[const.ZONE_MODULE])
    instance.calculate = Mock(return_value=-et_mm / multiplier)
    return await c.calculate_module(zone, weatherdata, None, now=now)


class TestTheReplayFollowsTheCommitNotTheEtSource:
    """A zone whose commit replays gets an estimate that replays, whichever
    source priced its evapotranspiration.

    These zones estimate solar radiation rather than measuring it, so the buffer
    source declines them and the weather client or the proxy is what is left --
    while their commit, which needs no measured radiation, replays the window
    all the same. That pairing is the whole gap: a replayed commit read through
    a lumped estimate, always in the direction that reads the zone drier.
    """

    async def test_late_rain_lands_on_the_committed_bucket(self, coordinator):
        c, store = coordinator
        # A dry morning, a burst at 20:00. Booked at the window start it is
        # charged 20 hours of drainage it never saw.
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        data = await _committed_with_et(c, zone, est["et_since"])

        assert est["method"] == "hourly"
        assert est["balance_form"] == "replayed"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_rain_spread_through_the_day_also_agrees(self, coordinator):
        """The other half of the lumped form's error: spread-out rain is
        over-clamped, because the drainage that would have made room between
        bursts never happens."""
        c, store = coordinator
        zone = await _zone(
            c, store, 0.0, rain_at=dict.fromkeys(range(6, 20), 2.0), solrad="1"
        )

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        data = await _committed_with_et(c, zone, est["et_since"])

        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_the_lumped_form_would_have_disagreed(self, coordinator):
        """Guards the equalities above against being vacuous. This is the gap
        the client path was showing."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        lumped, _drained = live_balance(
            2.0,
            est["et_since"],
            est["precip_since"],
            MAXIMUM_BUCKET,
            drainage_rate=DRAINAGE_RATE,
            elapsed_hours=24.0,
        )

        assert lumped < est["live_deficit"] - 2.0

    async def test_the_drainage_trace_matches_the_committed_drainage(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        data = await _committed_with_et(c, zone, est["et_since"])

        assert est["drainage_since"] == pytest.approx(
            data[const.ZONE_CURRENT_DRAINAGE], abs=0.01
        )

    async def test_the_proxy_path_replays_too(self, coordinator):
        """The furthest source from the buffer still gets the buffer's rain
        timing, because rain timing is the buffer's to state on every path."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")

        est = c._intraday_for_zone(zone, _proxy_inputs())
        data = await _committed_with_et(c, zone, est["et_since"])

        assert est["method"] == "proxy"
        assert est["balance_form"] == "replayed"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_a_mid_window_credit_is_placed_on_the_step_it_landed_on(
        self, coordinator
    ):
        """The stored bucket already holds the credit, so the replay starts from
        the level before it. Charged from the window start instead, it pays the
        whole window's drainage on water it had not yet received."""
        c, store = coordinator
        events = [{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}]
        late = await _zone(c, store, 10.0, solrad="1", events=events)
        folded = await _zone(c, store, 10.0, solrad="1")

        with_ledger = c._intraday_for_zone(late, _client_inputs(_provider_rows(0.0)))
        without = c._intraday_for_zone(folded, _client_inputs(_provider_rows(0.0)))

        assert with_ledger["live_deficit"] > without["live_deficit"] + 1.0
        assert with_ledger["drainage_since"] < without["drainage_since"]

    async def test_a_credited_window_lands_on_the_committed_bucket(self, coordinator):
        c, store = coordinator
        events = [{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}]
        zone = await _zone(c, store, 10.0, solrad="1", events=events)

        # calculate_module consumes the ledger, so it has to run second: the
        # estimate must see the same credits the commit will.
        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        data = await _committed_with_et(c, zone, est["et_since"])

        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_the_widened_replay_stays_read_only(self, coordinator):
        """Reducing the buffer into sub-steps must not consume it: no watermark
        moved, no readings taken, no bucket written, no credit ledger cleared."""
        c, store = coordinator
        events = [{"ts": (T0 + timedelta(hours=20)).isoformat(), "mm": 10.0}]
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1", events=events)
        before = dict(store.get_zone(zone[const.ZONE_ID]))
        rows_before = len(store.get_mapping_buffer(zone[const.ZONE_MAPPING]))

        for _ in range(3):
            c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
            c._intraday_for_zone(zone, _proxy_inputs())

        after = store.get_zone(zone[const.ZONE_ID])
        for field in (
            const.ZONE_BUCKET,
            const.ZONE_LAST_CONSUMED,
            const.ZONE_LAST_CALCULATED,
        ):
            assert after.get(field) == before.get(field)
        assert len(store.get_mapping_buffer(zone[const.ZONE_MAPPING])) == rows_before
        assert zone[const.ZONE_PENDING_BUCKET_EVENTS] == events


class TestZonesWhoseCommitLumps:
    """The mirror has to hold in the other direction too. A zone the commit
    never replays must not be shown a replayed curve, or the estimate would be
    the one inventing the timing."""

    @pytest.mark.parametrize(
        ("hourly_calculation", "module_name"),
        [(True, "PyETO"), (False, "PyETO"), (True, "Static")],
    )
    async def test_the_estimate_replays_exactly_when_the_calculation_does(
        self, coordinator, hourly_calculation, module_name
    ):
        """Asserted against the calculation's own gate rather than against a
        restatement of its conditions, which is the only way the two cannot
        drift apart as either changes."""
        c, store = coordinator
        await store.async_update_config(
            {const.CONF_HOURLY_CALCULATION: hourly_calculation}
        )
        zone = await _zone(
            c, store, 2.0, rain_at={20: 14.0}, solrad="1", module_name=module_name
        )

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        booked = await _committed_precip(c, zone)
        commit_replays = c._substeps_for_zone(zone, booked, now=NOW) is not None

        # Every configuration still produces an estimate, or the equivalence
        # below would hold by both sides being absent.
        assert est["available"] is True
        assert (est["balance_form"] == "replayed") is commit_replays

    async def test_an_install_without_the_hourly_form_still_agrees_lumped(
        self, coordinator
    ):
        """Both sides lump, and the two still land on the same bucket -- so the
        pairing is a mirror rather than merely two paths that both refuse."""
        c, store = coordinator
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: False})
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))
        data = await _committed_with_et(c, zone, est["et_since"])

        assert est["balance_form"] == "lumped"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_a_client_window_that_cannot_be_sub_stepped_still_estimates(
        self, coordinator, monkeypatch
    ):
        """Never absent, never a fabricated curve: a window that will not reduce
        falls back to the form that preceded this."""
        import custom_components.irrigation_plus.live_estimate as le

        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0}, solrad="1")
        monkeypatch.setattr(le, "build_substeps", lambda *a, **kw: None)

        est = c._intraday_for_zone(zone, _client_inputs(_provider_rows(0.0)))

        assert est["available"] is True
        assert est["method"] == "hourly"
        assert est["balance_form"] == "lumped"
        lumped, _drained = live_balance(
            2.0,
            est["et_since"],
            est["precip_since"],
            MAXIMUM_BUCKET,
            drainage_rate=DRAINAGE_RATE,
            elapsed_hours=24.0,
        )
        assert est["live_deficit"] == pytest.approx(round(lumped, 2), abs=0.01)


class TestTheBalanceFormIsVisibleFromOutside:
    """Whether the replay ran is otherwise invisible from outside the process,
    so a replayed estimate and a lumped one that happens to land close cannot be
    told apart -- by an operator diagnosing a gap or by a live check."""

    async def test_the_buffer_path_reports_replayed(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})

        est = c._intraday_for_zone(zone, _inputs())

        assert est["method"] == "hourly_sensor"
        assert est["balance_form"] == "replayed"

    async def test_the_sensor_publishes_the_balance_form(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 14.0})
        c.hass.data[const.DOMAIN]["coordinator"] = c
        c._zone_estimates_cache = {
            str(zone[const.ZONE_ID]): c._intraday_for_zone(zone, _inputs())
        }

        sensor = SmartIrrigationZoneLiveDeficitSensor(
            c.hass, "sensor.si_live_deficit", zone
        )

        assert sensor.extra_state_attributes["balance_form"] == "replayed"
