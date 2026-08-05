"""Axis B: the intra-day live estimate fed from the zone's own sensor buffer.

The equation and the row builder are pinned elsewhere (test_et_hourly.py,
test_summed_hourly_eto.py). What can still go wrong lives here:

* a sensor-only install has no weather client, which is exactly what used to
  make the whole feature inert -- the orchestration gave up before reaching the
  buffer that holds the readings;
* ONE window anchor for both halves of the balance. Upstream issue #38 was ET
  measured from ``last_calculated`` while precipitation came from
  ``last_consumed_at``, and the two are equal on a healthy install, so the bug
  is invisible until a reset or a source change moves them apart;
* the completed-hour carry, which is what makes a minute-cadence refresh cost
  one partial hour instead of the whole window -- and which must produce the
  same number as re-reducing that window from scratch;
* the drainage figure, published as its own trace and therefore required to
  reconcile with the deficit it is plotted beside.

Every case supplies its own ``now``, so nothing here depends on the wall clock.
"""

import datetime
from datetime import timedelta
from types import SimpleNamespace

import pytest
from freezegun import freeze_time
from homeassistant.util.unit_system import METRIC_SYSTEM

import custom_components.smart_irrigation.et_estimate as ete
import custom_components.smart_irrigation.live_estimate as le
from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.et_estimate import eto_hourly_series
from custom_components.smart_irrigation.live_estimate import LiveEstimateMixin
from custom_components.smart_irrigation.weather_aggregate import (
    aggregate_window,
    build_hourly_rows,
)

LAT, LON, ELEV, TZ = 39.68987, -84.07865, 311.0, -4.0

# A calculation at 09:00 and readings through the morning, so the window is
# daylight and its ETo is a number worth asserting on.
ANCHOR = datetime.datetime(2026, 5, 22, 9, 0, 0)

# 1 W/m2 = 0.0864 MJ/day/m2, which is what the buffer stores.
W_TO_MJ_DAY = 0.0864

_PYETO_HOURLY = {
    const.MODULE_NAME: "PyETO",
    const.MODULE_CONFIG: {
        const.CONF_PYETO_SOLRAD_BEHAVIOR: "3",  # DontEstimate
        const.CONF_PYETO_FORECAST_DAYS: 0,
    },
}


def _readings(end, *, rain=None, step=10):
    """A dense buffer from the anchor to ``end``, as the poll path writes it.

    ``rain`` is ``{stamp: cumulative_mm}`` for a rain gauge (DELTA), added on
    top of the regular rows.
    """
    out = []
    stamp = ANCHOR
    while stamp <= end:
        hour = stamp.hour + stamp.minute / 60.0
        out.append(
            {
                const.RETRIEVED_AT: stamp,
                const.MAPPING_TEMPERATURE: 20.0,
                const.MAPPING_HUMIDITY: 55.0,
                const.MAPPING_WINDSPEED: 1.5,
                const.MAPPING_SOLRAD: 700.0 * W_TO_MJ_DAY * (hour - 5) / 8,
            }
        )
        stamp += timedelta(minutes=step)
    for at, mm in (rain or {}).items():
        out.append({const.RETRIEVED_AT: at, const.MAPPING_PRECIPITATION: mm})
    out.sort(key=lambda r: r[const.RETRIEVED_AT])
    return out


def _sparse(end, *, step=10, slow_fields=True):
    """A sparse buffer: one field per row, as continuous updates write it.

    Only solar moves; the other fields appear once (or not at all, when
    ``slow_fields`` is off and they have to arrive through the mapping's
    carry-forward instead). Same values as ``_readings``, so the two shapes must
    reduce to the same hourly rows.

    The slow fields sit just INSIDE the window rather than on the anchor:
    ``select_window`` keeps a single boundary row, so several rows stamped
    exactly at the watermark compete for that one slot and all but one are
    dropped. Held backwards to the window start by the row builder either way,
    so the values are unaffected.
    """
    out = []
    if slow_fields:
        first = ANCHOR + timedelta(minutes=1)
        out += [
            {const.RETRIEVED_AT: first, const.MAPPING_TEMPERATURE: 20.0},
            {const.RETRIEVED_AT: first, const.MAPPING_HUMIDITY: 55.0},
            {const.RETRIEVED_AT: first, const.MAPPING_WINDSPEED: 1.5},
        ]
    stamp = ANCHOR
    while stamp <= end:
        hour = stamp.hour + stamp.minute / 60.0
        out.append(
            {
                const.RETRIEVED_AT: stamp,
                const.MAPPING_SOLRAD: 700.0 * W_TO_MJ_DAY * (hour - 5) / 8,
            }
        )
        stamp += timedelta(minutes=step)
    return out


class _Store:
    def __init__(
        self,
        readings,
        *,
        module=_PYETO_HOURLY,
        mappings_config=None,
        last_entry=None,
    ):
        self.readings = readings
        self.module = module
        # Two independent axes, both on here. ``hourlycalculation`` is what the
        # buffer source is gated on, because it is what the DAILY form reads;
        # ``continuousupdates`` only selects the precipitation aggregation, and
        # has to match what ``_aggregate_for_zone`` would do for the same window.
        self.config = SimpleNamespace(hourlycalculation=True, continuousupdates=True)
        self.mapping = {
            const.MAPPING_MAPPINGS: mappings_config or {},
            const.MAPPING_DATA_LAST_ENTRY: last_entry or {},
        }

    def get_module(self, _module_id):
        return self.module

    def get_mapping(self, _mapping_id):
        return self.mapping

    def get_mapping_buffer(self, _mapping_id):
        return self.readings

    def get_zones(self):
        return [_zone()]


class _Coord(LiveEstimateMixin):
    def __init__(self, store):
        self.hass = SimpleNamespace(config=SimpleNamespace(units=METRIC_SYSTEM))
        self.store = store
        self._effective_latitude = LAT
        self._effective_longitude = LON
        self._effective_elevation = ELEV


def _zone(**overrides):
    zone = {
        const.ZONE_ID: 1,
        const.ZONE_MAPPING: 1,
        const.ZONE_MODULE: 1,
        const.ZONE_BUCKET: -2.0,
        const.ZONE_MAXIMUM_BUCKET: 24.0,
        const.ZONE_DRAINAGE_RATE: 0.0,
        const.ZONE_LAST_CALCULATED: ANCHOR,
        const.ZONE_LAST_CONSUMED: ANCHOR,
    }
    zone.update(overrides)
    return zone


def _async_zones(zones):
    async def _get():
        return zones

    return _get


def _inputs(now):
    """A sensor-only install: no weather client, no hourly rows, no forecast."""
    return {
        "client": None,
        "rows": None,
        "tz": None,
        "forecast": None,
        "now": now,
        "tz_offset_h": TZ,
        # The site's own timezone, not Home Assistant's default, which under
        # pytest is UTC. A fixed offset rather than a named zone: these windows
        # are hours long and never straddle a transition, so this pins that the
        # per-row offset agrees with the scalar instead of quietly replacing it.
        "site_tz": datetime.timezone(timedelta(hours=TZ)),
    }


def _expected_et_mm(readings, watermark, now, mappings_config=None):
    """The reference total: the row builder, summed. No window-length scaling.

    ``hour_multiplier`` scales a DAILY et0 by the window's fraction of a day;
    summed hourly ETo has already integrated over the window, so applying it
    would scale the same window twice. Comparing against a plain sum is what
    pins that.
    """
    rows = build_hourly_rows(readings, watermark, mappings_config or {}, now=now)
    return sum(eto_hourly_series(rows, LAT, LON, TZ, ELEV))


class TestSensorOnlyInstall:
    def test_no_weather_client_still_produces_an_estimate(self):
        now = ANCHOR + timedelta(hours=3, minutes=30)
        coord = _Coord(_Store(_readings(now)))
        est = coord._intraday_for_zone(_zone(), _inputs(now))

        expected = _expected_et_mm(coord.store.readings, ANCHOR, now)
        assert expected > 0
        assert est["available"] is True
        assert est["method"] == "hourly_sensor"
        assert est["et_since"] == pytest.approx(round(expected, 4))
        assert est["live_deficit"] == pytest.approx(round(-2.0 - expected, 2))

    def test_the_accumulators_carry_finer_precision_than_the_shown_state(self):
        """They are graph inputs, and a dashboard differentiates them for a rate.

        At display precision an imperial install's ``et_since`` gains
        0.00026 in/min against a 0.001 in step at a midday ET of 0.4 mm/h, so it
        would move only every ~4 minutes and a per-minute derivative would
        alternate between zero and a spike. The state keeps display precision
        because, unlike the attributes, it is rendered.
        """
        now = ANCHOR + timedelta(hours=3, minutes=30)
        coord = _Coord(_Store(_readings(now)))
        est = coord._intraday_for_zone(_zone(), _inputs(now))
        expected = _expected_et_mm(coord.store.readings, ANCHOR, now)

        # Guards the fixture: an ET that happened to land on two decimals would
        # make the assertion below pass for the wrong reason.
        assert round(expected, 4) != round(expected, 2)
        assert est["et_since"] == pytest.approx(round(expected, 4))
        assert est["et_since"] != pytest.approx(round(expected, 2))
        # Rounded to display precision already, so this is a no-op unless the
        # state is ever given the accumulators' extra digits.
        assert est["live_deficit"] == round(est["live_deficit"], 2)

    def test_the_hourly_form_being_off_declines_the_buffer_source(self):
        """Gated on ``hourlycalculation``, in step with the daily calculation.

        If the daily calc runs the daily equation while this reports
        ``hourly_sensor``, the panel shows a live curve the stored bucket never
        meets, differing by the 12% that separates the two forms.
        """
        now = ANCHOR + timedelta(hours=3)
        store = _Store(_readings(now))
        store.config = SimpleNamespace(hourlycalculation=False, continuousupdates=True)
        coord = _Coord(store)
        assert coord._hourly_form_applies(_zone()) is False
        # Nothing else can supply a sensor-only install, so it offers no estimate
        # rather than falling to a source that disagrees with the ledger.
        assert coord._intraday_for_zone(_zone(), _inputs(now))["available"] is False

    def test_a_polling_install_with_the_hourly_form_on_still_gets_the_buffer(self):
        """The two axes are independent, and the gate follows the daily form only.

        ``_hourly_calculation_enabled`` blesses poll-only installs for the hourly
        form: measured against dense truth they run it within 8.4% and with no
        systematic bias. Reading ``continuousupdates`` here would refuse them the
        buffer source while the daily calculation was already summing hourly, so
        the live curve would sit against a ledger it does not match -- the same
        divergence the gate exists to prevent, in the other direction.
        """
        now = ANCHOR + timedelta(hours=3, minutes=30)
        store = _Store(_readings(now))
        store.config = SimpleNamespace(hourlycalculation=True, continuousupdates=False)
        coord = _Coord(store)
        assert coord._hourly_form_applies(_zone()) is True
        est = coord._intraday_for_zone(_zone(), _inputs(now))
        assert est["available"] is True
        assert est["method"] == "hourly_sensor"

    def test_a_module_that_is_not_pyeto_declines(self):
        """The fourth decline condition. The daily form is PyETO-only, so any
        other module leaves the ledger on the daily equation and the buffer
        source would put the 12% gap on the dashboard.
        """
        now = ANCHOR + timedelta(hours=3)
        other = {
            const.MODULE_NAME: "Hargreaves",
            const.MODULE_CONFIG: {const.CONF_PYETO_SOLRAD_BEHAVIOR: "3"},
        }
        coord = _Coord(_Store(_readings(now), module=other))
        assert coord._hourly_form_applies(_zone()) is False
        assert coord._intraday_for_zone(_zone(), _inputs(now))["available"] is False

    def test_a_module_that_estimates_radiation_keeps_its_own_source(self):
        """The daily calc would run the daily equation for such a zone, and the
        two forms differ by up to 12% by sky condition. Offering the hourly
        curve against a daily-aggregate ledger would put that on the dashboard.
        """
        now = ANCHOR + timedelta(hours=3)
        estimating = {
            const.MODULE_NAME: "PyETO",
            const.MODULE_CONFIG: {const.CONF_PYETO_SOLRAD_BEHAVIOR: "1"},
        }
        coord = _Coord(_Store(_readings(now), module=estimating))
        # Nothing else can supply this install, so declining means no estimate.
        assert coord._intraday_for_zone(_zone(), _inputs(now))["available"] is False

    def test_forecast_days_declines_too(self):
        now = ANCHOR + timedelta(hours=3)
        forecasting = {
            const.MODULE_NAME: "PyETO",
            const.MODULE_CONFIG: {
                const.CONF_PYETO_SOLRAD_BEHAVIOR: "3",
                const.CONF_PYETO_FORECAST_DAYS: 2,
            },
        }
        coord = _Coord(_Store(_readings(now), module=forecasting))
        assert coord._intraday_for_zone(_zone(), _inputs(now))["available"] is False

    def test_no_estimate_before_the_first_calculation(self):
        now = ANCHOR + timedelta(hours=3)
        coord = _Coord(_Store(_readings(now)))
        zone = _zone(**{const.ZONE_LAST_CALCULATED: None})
        assert coord._intraday_for_zone(zone, _inputs(now))["available"] is False

    def test_an_empty_buffer_declines_rather_than_reporting_zero_et(self):
        now = ANCHOR + timedelta(hours=3)
        coord = _Coord(_Store([]))
        assert coord._intraday_for_zone(_zone(), _inputs(now))["available"] is False


class TestBothBufferShapes:
    """The poll path writes every mapped field on every row; the continuous
    path writes ONE field per event. This install produces the sparse kind, and
    code that assumes dense rows silently drops most of such a buffer."""

    def test_sparse_and_dense_buffers_give_the_same_estimate(self):
        now = ANCHOR + timedelta(hours=3, minutes=30)
        dense = _Coord(_Store(_readings(now)))._intraday_for_zone(_zone(), _inputs(now))
        sparse = _Coord(_Store(_sparse(now)))._intraday_for_zone(_zone(), _inputs(now))

        assert sparse["available"] is True
        assert sparse["method"] == "hourly_sensor"
        assert sparse["et_since"] == pytest.approx(dense["et_since"])
        assert sparse["live_deficit"] == pytest.approx(dense["live_deficit"])

    def test_a_slow_field_reaches_the_estimate_through_the_carry_forward(self):
        """A field that moves rarely can have NO row inside the window at all.
        The mapping's last-seen value is what it was reading throughout, which
        is the same fallback the daily calculation uses."""
        now = ANCHOR + timedelta(hours=3, minutes=30)
        readings = _sparse(now, slow_fields=False)
        carried = {
            const.MAPPING_TEMPERATURE: 20.0,
            const.MAPPING_HUMIDITY: 55.0,
            const.MAPPING_WINDSPEED: 1.5,
        }
        est = _Coord(_Store(readings, last_entry=carried))._intraday_for_zone(
            _zone(), _inputs(now)
        )
        reference = _Coord(_Store(_sparse(now)))._intraday_for_zone(
            _zone(), _inputs(now)
        )

        assert est["available"] is True
        assert est["et_since"] == pytest.approx(reference["et_since"])

    def test_a_field_in_neither_the_window_nor_the_carry_forward_declines(self):
        """No radiation anywhere means no hourly ETo. Declining leaves the other
        sources in place rather than summing a fabricated series."""
        now = ANCHOR + timedelta(hours=3, minutes=30)
        readings = [r for r in _sparse(now) if const.MAPPING_SOLRAD not in r]
        coord = _Coord(_Store(readings))
        assert coord._intraday_for_zone(_zone(), _inputs(now))["available"] is False

    def test_a_sparse_rain_gauge_is_still_counted(self):
        """Precipitation arrives as its own rows on this path, never alongside
        the other fields."""
        now = ANCHOR + timedelta(hours=3)
        readings = _sparse(now)
        readings += [
            {
                const.RETRIEVED_AT: ANCHOR + timedelta(minutes=5),
                const.MAPPING_PRECIPITATION: 12.0,
            },
            {
                const.RETRIEVED_AT: ANCHOR + timedelta(hours=1, minutes=5),
                const.MAPPING_PRECIPITATION: 15.0,
            },
        ]
        readings.sort(key=lambda r: r[const.RETRIEVED_AT])
        est = _Coord(_Store(readings))._intraday_for_zone(_zone(), _inputs(now))

        # A cumulative gauge: the first reading is the baseline, so the window's
        # rain is the 3 mm step, not the 15 mm the counter reads.
        assert est["precip_since"] == pytest.approx(3.0)

    @freeze_time("2026-05-22 12:30:00")
    async def test_the_whole_orchestration_runs_without_a_weather_client(self):
        """End to end from the entry point the sensors and the run gate call.

        This is the shape of the original defect: with no client the inputs
        fetch returned None and every zone was dropped before the buffer was
        ever consulted, so the live-deficit sensor stayed empty and
        ``live_estimate_enabled`` gated nothing.
        """
        coord = _Coord(_Store(_readings(datetime.datetime(2026, 5, 22, 12, 30))))
        coord.store.async_get_zones = _async_zones([_zone()])
        assert not hasattr(coord, "_WeatherServiceClient")

        estimates = await coord.async_get_zone_estimates()
        assert set(estimates) == {"1"}
        assert estimates["1"]["method"] == "hourly_sensor"
        assert estimates["1"]["live_deficit"] < -2.0


class TestOneAnchor:
    """ET and precipitation measured from the SAME instant (upstream #38)."""

    def test_both_halves_are_measured_from_the_last_calculation(self):
        now = ANCHOR + timedelta(hours=3)
        # A cumulative gauge that steps at 10:30, inside the window.
        rain = {
            ANCHOR + timedelta(minutes=30): 0.0,
            ANCHOR + timedelta(hours=1, minutes=30): 4.0,
        }
        readings = _readings(now, rain=rain)
        coord = _Coord(_Store(readings))
        est = coord._intraday_for_zone(_zone(), _inputs(now))

        expected_precip = aggregate_window(readings, ANCHOR, {}).get(
            const.MAPPING_PRECIPITATION
        )
        assert expected_precip == pytest.approx(4.0)
        assert est["precip_since"] == pytest.approx(4.0)
        assert est["et_since"] == pytest.approx(
            round(_expected_et_mm(readings, ANCHOR, now), 4)
        )

    def test_a_watermark_ahead_of_the_calculation_moves_both_halves(self):
        """A weather reset or a source change advances the consume watermark on
        its own and deletes the readings behind it. Anchoring at
        ``last_calculated`` then reaches over a stretch with no readings, and
        carry-forward answers by holding the CURRENT value across all of it --
        measured live, a midday reset charged 16.6 mm of ET for a day whose real
        total is a few mm. Both halves move to the watermark together, so the
        deficit stays the difference of ONE window.
        """
        now = ANCHOR + timedelta(hours=3)
        watermark = ANCHOR + timedelta(hours=2, minutes=30)
        rain = {
            ANCHOR + timedelta(minutes=30): 0.0,
            ANCHOR + timedelta(hours=1, minutes=30): 4.0,
        }
        readings = _readings(now, rain=rain)
        coord = _Coord(_Store(readings))
        zone = _zone(**{const.ZONE_LAST_CONSUMED: watermark})
        est = coord._intraday_for_zone(zone, _inputs(now))

        # The gauge's step is behind the watermark, so it is the baseline rather
        # than rain -- and the ET is the half-hour since, not three hours of it.
        assert est["precip_since"] == pytest.approx(0.0)
        assert est["et_since"] == pytest.approx(
            round(_expected_et_mm(readings, watermark, now), 4)
        )
        assert est["et_since"] < round(_expected_et_mm(readings, ANCHOR, now), 4)

    def test_the_deficit_reconciles_with_its_own_terms(self):
        now = ANCHOR + timedelta(hours=3)
        rain = {ANCHOR: 0.0, ANCHOR + timedelta(hours=1): 1.5}
        coord = _Coord(_Store(_readings(now, rain=rain)))
        est = coord._intraday_for_zone(_zone(), _inputs(now))

        assert est["live_deficit"] == pytest.approx(
            round(-2.0 - est["et_since"] + est["precip_since"], 2), abs=0.01
        )


class TestDrainageTrace:
    def test_drainage_is_reported_and_reconciles_with_the_deficit(self):
        now = ANCHOR + timedelta(hours=3)
        coord = _Coord(_Store(_readings(now)))
        # A wet bucket: the surplus above 0 drains over the window, which is the
        # third trace a dashboard plots beside the bucket and the ET.
        zone = _zone(
            **{
                const.ZONE_BUCKET: 10.0,
                const.ZONE_DRAINAGE_RATE: 20.0,
                const.ZONE_MAXIMUM_BUCKET: 24.0,
            }
        )
        est = coord._intraday_for_zone(zone, _inputs(now))

        assert est["drainage_since"] > 0
        assert est["live_deficit"] == pytest.approx(
            round(
                10.0 - est["et_since"] + est["precip_since"] - est["drainage_since"], 2
            ),
            abs=0.01,
        )

    def test_a_dry_bucket_drains_nothing(self):
        now = ANCHOR + timedelta(hours=3)
        coord = _Coord(_Store(_readings(now)))
        zone = _zone(**{const.ZONE_DRAINAGE_RATE: 20.0})
        assert coord._intraday_for_zone(zone, _inputs(now))["drainage_since"] == 0.0


class TestTheRowBuilderGetsTheSameGeometryAsTheDailyCalculation:
    """The estimate exists to track the bucket the nightly calculation lands on,
    so any solar-geometry argument the daily site passes and this one does not is
    a silent divergence: the two price a gapped window differently, nothing
    raises, and no other test notices.
    """

    def test_the_site_geometry_and_its_timezone_both_reach_the_row_builder(
        self, monkeypatch
    ):
        seen = {}
        # Patched where ``hourly_eto_priced`` resolves it, which is the single
        # call both this and the daily calculation now reach the row builder
        # through -- so a geometry argument can no longer be dropped on one side.
        original = ete.build_hourly_rows

        def spy(readings, watermark, config, **kwargs):
            seen.update(kwargs)
            return original(readings, watermark, config, **kwargs)

        monkeypatch.setattr(ete, "build_hourly_rows", spy)
        now = ANCHOR + timedelta(hours=3, minutes=30)
        coord = _Coord(_Store(_readings(now)))
        coord._intraday_for_zone(_zone(), _inputs(now))

        assert (seen["latitude"], seen["longitude"]) == (LAT, LON)
        assert seen["elevation"] == ELEV
        assert seen["tz_offset_h"] == TZ
        # The timezone travels with the offset it was measured from. Reading it
        # from dt_util here instead would be UTC under pytest and silently
        # override the scalar above, because a per-row offset wins over it.
        assert seen["tz"].utcoffset(now) == timedelta(hours=TZ)


class TestCompletedHourCarry:
    """Only the current partial hour may be re-reduced, and the total must not
    change because of it."""

    @staticmethod
    def _recording(monkeypatch):
        calls = []
        original = ete.build_hourly_rows

        def spy(readings, watermark, config, **kwargs):
            rows = original(readings, watermark, config, **kwargs)
            calls.append((watermark, len(rows or [])))
            return rows

        monkeypatch.setattr(ete, "build_hourly_rows", spy)
        return calls

    def test_the_second_refresh_only_rebuilds_the_open_hour(self, monkeypatch):
        calls = self._recording(monkeypatch)
        store = _Store(_readings(ANCHOR + timedelta(hours=3, minutes=50)))
        coord = _Coord(store)

        first = ANCHOR + timedelta(hours=3, minutes=30)
        coord._intraday_for_zone(_zone(), _inputs(first))
        second = ANCHOR + timedelta(hours=3, minutes=50)
        coord._intraday_for_zone(_zone(), _inputs(second))

        # 09:00 -> 12:00 the first time (four hours touched), then only the open
        # 12:00 hour, whose ETo is the only part that can still change.
        assert calls[0][0] == ANCHOR
        assert calls[0][1] == 4
        assert calls[1][0] == ANCHOR.replace(hour=12, minute=0)
        assert calls[1][1] == 1

    def test_the_carried_total_equals_re_reducing_the_whole_window(self):
        readings = _readings(ANCHOR + timedelta(hours=3, minutes=50))
        carried = _Coord(_Store(readings))
        fresh = _Coord(_Store(readings))

        # Walk the carried instance through every hour boundary; the fresh one
        # only sees the end state, so it reduces the window in one pass.
        for minutes in (30, 75, 130, 190, 230):
            carried._intraday_for_zone(
                _zone(), _inputs(ANCHOR + timedelta(minutes=minutes))
            )
        end = ANCHOR + timedelta(minutes=230)
        assert carried._intraday_for_zone(_zone(), _inputs(end))[
            "et_since"
        ] == pytest.approx(fresh._intraday_for_zone(_zone(), _inputs(end))["et_since"])

    def test_a_new_calculation_drops_the_carry(self, monkeypatch):
        calls = self._recording(monkeypatch)
        store = _Store(_readings(ANCHOR + timedelta(hours=4)))
        coord = _Coord(store)

        coord._intraday_for_zone(
            _zone(), _inputs(ANCHOR + timedelta(hours=3, minutes=30))
        )
        # The daily calc ran at 12:00: the anchor moves, and a total measured
        # from the old one is no longer this zone's intra-day drift.
        moved = ANCHOR.replace(hour=12)
        zone = _zone(
            **{const.ZONE_LAST_CALCULATED: moved, const.ZONE_LAST_CONSUMED: moved}
        )
        coord._intraday_for_zone(zone, _inputs(ANCHOR + timedelta(hours=3, minutes=40)))
        assert calls[1][0] == moved

    def test_invalidation_drops_the_carry_when_the_buffer_changes(self, monkeypatch):
        calls = self._recording(monkeypatch)
        store = _Store(_readings(ANCHOR + timedelta(hours=4)))
        coord = _Coord(store)

        coord._intraday_for_zone(
            _zone(), _inputs(ANCHOR + timedelta(hours=3, minutes=30))
        )
        # A weather-data reset / source change / row-cap trim rewrites the rows
        # without moving last_calculated, so nothing else would notice.
        coord.invalidate_live_estimate_carry(1)
        coord._intraday_for_zone(
            _zone(), _inputs(ANCHOR + timedelta(hours=3, minutes=40))
        )
        assert calls[1][0] == ANCHOR

    def test_invalidation_leaves_other_sensor_groups_alone(self, monkeypatch):
        calls = self._recording(monkeypatch)
        coord = _Coord(_Store(_readings(ANCHOR + timedelta(hours=4))))

        coord._intraday_for_zone(
            _zone(), _inputs(ANCHOR + timedelta(hours=3, minutes=30))
        )
        coord.invalidate_live_estimate_carry(99)
        coord._intraday_for_zone(
            _zone(), _inputs(ANCHOR + timedelta(hours=3, minutes=40))
        )
        assert calls[1][0] == ANCHOR.replace(hour=12, minute=0)


class TestRefreshThrottle:
    async def test_event_driven_refreshes_are_throttled(self, monkeypatch):
        coord = _Coord(_Store([]))
        clock = {"t": 1000.0}
        monkeypatch.setattr(le.time, "monotonic", lambda: clock["t"])
        computed = {"n": 0}

        async def counted():
            computed["n"] += 1
            return {}

        coord.async_get_zone_estimates = counted
        monkeypatch.setattr(le, "async_dispatcher_send", lambda *args: None)

        await coord.async_refresh_zone_estimates_throttled()
        await coord.async_refresh_zone_estimates_throttled()
        assert computed["n"] == 1

        clock["t"] += le.LIVE_ESTIMATE_MIN_REFRESH_SECONDS
        await coord.async_refresh_zone_estimates_throttled()
        assert computed["n"] == 2

    async def test_an_explicit_refresh_is_never_throttled(self, monkeypatch):
        coord = _Coord(_Store([]))
        monkeypatch.setattr(le.time, "monotonic", lambda: 1000.0)
        computed = {"n": 0}

        async def counted():
            computed["n"] += 1
            return {}

        coord.async_get_zone_estimates = counted
        monkeypatch.setattr(le, "async_dispatcher_send", lambda *args: None)

        # The daily calculation and the live-estimate run gate call this
        # directly and must always see the current number.
        await coord.async_refresh_zone_estimates()
        await coord.async_refresh_zone_estimates()
        assert computed["n"] == 2
