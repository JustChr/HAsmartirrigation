"""The live estimate of a pausing sensor group leaves out the time the commit does.

The estimate exists to show the path the stored bucket takes, so it cuts the same
spans the commit will: computed once per refresh, from the estimate's own anchor
to its ``now``, and handed to every reader of the buffer. A group that keeps is
estimated exactly as before.
"""

from datetime import timedelta

import pytest

from custom_components.irrigation_plus import calculation as calculation_module
from custom_components.irrigation_plus import const
from custom_components.irrigation_plus import live_estimate as live_estimate_module
from custom_components.irrigation_plus.sensor_liveness import Outage
from tests.test_live_estimate_replayed_balance import (
    ANCHOR,
    NOW,
    T0,
    WINDOW_END,
    _client_inputs,
    _estimating_inputs,
    _estimating_zone,
    _hourly_forecast,
    _inputs,
    _provider_rows,
    _proxy_inputs,
    _rate_readings,
    _zone,
    make_coordinator,
)

H = timedelta(hours=1)
T = const.MAPPING_TEMPERATURE


@pytest.fixture
async def coordinator(hass):
    return await make_coordinator(hass)


def _record(start_h, end_h=None, fields=(T,)):
    return Outage(
        "sensor.t",
        "dev1",
        tuple(fields),
        T0 + start_h * H,
        None if end_h is None else T0 + end_h * H,
    ).to_store()


async def _silent(store, zone, *outages, setting=const.ON_SILENT_SENSOR_PAUSE):
    await store.async_update_mapping(
        zone[const.ZONE_MAPPING],
        {
            const.MAPPING_ON_SILENT_SENSOR: setting,
            const.MAPPING_SENSOR_OUTAGES: list(outages),
        },
    )


async def _committed(c, store, zone, now=NOW):
    """What the commit writes, through its own spans."""
    zone = store.get_zone(zone[const.ZONE_ID])
    blocked = c._blocked_spans_for_zone(zone, now=now)
    weatherdata, _ = await c._aggregate_for_zone(zone, now=now, blocked=blocked)
    return await c.calculate_module(zone, weatherdata, None, now=now, blocked=blocked)


def _recording_substeps(monkeypatch, module):
    """The sub-steps ``module`` hands its replay, one entry per call."""
    seen = []
    real = module.build_substeps

    def recording(*args, **kwargs):
        steps = real(*args, **kwargs)
        seen.append(steps)
        return steps

    monkeypatch.setattr(module, "build_substeps", recording)
    return seen


def _inside(steps, start, lo, hi):
    """Indices of the steps lying inside ``[lo, hi)``; the first begins at ``start``."""
    out = []
    for i, step in enumerate(steps):
        end = start + timedelta(hours=step.dt_hours)
        if lo <= start and end <= hi:
            out.append(i)
        start = end
    return out


class TestTheLiveCurveLandsOnTheCutBucket:
    async def test_the_hourly_source_agrees_with_the_commit(self, coordinator):
        """Temperature silent from 06:00 to 12:00: 09:00-12:00 is blocked."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 6.0})
        uncut = await _committed(c, store, zone)
        await _silent(store, zone, _record(6, 12))

        est = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        data = await _committed(c, store, zone)

        assert est["method"] == "hourly_sensor"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )
        assert data[const.ZONE_BUCKET] > uncut[const.ZONE_BUCKET] + 0.1
        assert est["balance_form"] == "replayed"

    async def test_an_open_outage_cuts_up_to_now(self, coordinator):
        """Open from 14:00, blocked from 17:00 to the estimate's now: both cut the
        same, and both cut something."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0)
        uncut = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        uncut_data = await _committed(c, store, zone)
        await _silent(store, zone, _record(14))
        est = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        data = await _committed(c, store, zone)
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )
        assert est["et_since"] < uncut["et_since"] - 0.1
        assert data[const.ZONE_BUCKET] > uncut_data[const.ZONE_BUCKET] + 0.1

    async def test_a_group_that_keeps_is_estimated_as_before(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 6.0})
        before = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        c._hourly_carry().clear()
        await _silent(store, zone, _record(6, 12), setting=const.ON_SILENT_SENSOR_KEEP)
        after = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        assert after == before


class TestTheReplayUnderTheHourlySwitch:
    """Estimated sun keeps the daily form under the hourly switch, and the balance
    of such a zone is still replayed -- by the commit and by the estimate alike,
    with the ET placed in the time the fields of the daily form were measured."""

    BLOCKED = (T0 + 9 * H, T0 + 16 * H)

    def _estimate(self, c, store, zone, instance, module):
        return c._intraday_for_zone(
            store.get_zone(zone[const.ZONE_ID]),
            _estimating_inputs(instance, module, forecast=_hourly_forecast()),
        )

    @pytest.mark.parametrize("sun", [True, False], ids=["with_sun", "without_sun"])
    async def test_a_daily_mirror_zone_replays_its_measured_time(
        self, coordinator, monkeypatch, sun
    ):
        """Temperature silent from 06:00 to 16:00 (blocked 09:00-16:00), without a
        sun sensor as well as with one."""
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        if not sun:
            store.set_mapping_buffer(
                zone[const.ZONE_MAPPING],
                [
                    {k: v for k, v in row.items() if k != const.MAPPING_SOLRAD}
                    for row in store.get_mapping_buffer(zone[const.ZONE_MAPPING])
                ],
            )
        await _silent(store, zone, _record(6, 16))
        live = _recording_substeps(monkeypatch, live_estimate_module)
        booked = _recording_substeps(monkeypatch, calculation_module)

        est = self._estimate(c, store, zone, instance, module)
        data = await _committed(c, store, zone, now=WINDOW_END)

        assert est["method"] == "daily_mirror"
        assert est["balance_form"] == "replayed"
        steps = live[-1]
        inside = _inside(steps, ANCHOR, *self.BLOCKED)
        assert inside
        assert all(steps[i].et_weight == 0.0 for i in inside)
        assert sum(step.et_weight for step in steps) == pytest.approx(1.0)
        assert steps == booked[-1]
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_a_field_the_daily_form_does_without_places_its_et_as_before(
        self, coordinator, monkeypatch
    ):
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        live = _recording_substeps(monkeypatch, live_estimate_module)
        plain = self._estimate(c, store, zone, instance, module)
        assert plain["balance_form"] == "replayed"
        await _silent(store, zone, _record(6, 16, fields=(const.MAPPING_HUMIDITY,)))
        self._estimate(c, store, zone, instance, module)
        assert live[-1] == live[0]


class TestTheRainItPublishes:
    async def test_a_blocked_rain_rate_is_published_as_the_commit_books_it(
        self, coordinator
    ):
        """A rate is integrated over its measured time only; a gauge never
        loses rain (the commit's rule, and the published trace is its rain)."""
        c, store = coordinator
        rate = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_AGGREGATE: const.MAPPING_CONF_AGGREGATE_RIEMANNSUM
            }
        }
        zone = await _zone(
            c,
            store,
            2.0,
            readings=_rate_readings({10: 2.0, 11: 2.0, 15: 1.0}),
            mappings_config=rate,
        )
        uncut = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        await _silent(
            store, zone, _record(6, 12, fields=(const.MAPPING_PRECIPITATION,))
        )
        est = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        zone = store.get_zone(zone[const.ZONE_ID])
        blocked = c._blocked_spans_for_zone(zone, now=NOW)
        weatherdata, _ = await c._aggregate_for_zone(zone, now=NOW, blocked=blocked)
        assert est["precip_since"] == pytest.approx(
            weatherdata[const.MAPPING_PRECIPITATION], abs=1e-3
        )
        assert est["precip_since"] < uncut["precip_since"] - 1.0
        # The replay reconciles its steps against the rain it publishes: handed
        # the uncut rate it would not, and the window would fall back to lumped.
        assert uncut["balance_form"] == "replayed"
        assert est["balance_form"] == "replayed"

    @pytest.mark.parametrize("source", ["hourly", "proxy"])
    async def test_a_blocked_rain_rate_is_cut_on_every_source(
        self, coordinator, source
    ):
        """A zone whose ET does not come from the buffer still publishes the rain
        its commit books: of a rate only the measured time, whichever source
        priced the ET (a client's hourly rows, or the forecast proxy)."""
        c, store = coordinator
        rate = {
            const.MAPPING_PRECIPITATION: {
                const.MAPPING_CONF_AGGREGATE: const.MAPPING_CONF_AGGREGATE_RIEMANNSUM
            }
        }
        zone = await _zone(
            c,
            store,
            2.0,
            readings=_rate_readings({10: 2.0, 11: 2.0, 15: 1.0}),
            mappings_config=rate,
            module_name="Passthrough",
        )
        inputs = (
            _client_inputs(_provider_rows(0.0))
            if source == "hourly"
            else _proxy_inputs()
        )
        uncut = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), inputs)
        await _silent(
            store, zone, _record(6, 12, fields=(const.MAPPING_PRECIPITATION,))
        )
        est = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), inputs)
        zone = store.get_zone(zone[const.ZONE_ID])
        blocked = c._blocked_spans_for_zone(zone, now=NOW)
        weatherdata, _ = await c._aggregate_for_zone(zone, now=NOW, blocked=blocked)

        assert est["method"] == uncut["method"] == source
        assert est["precip_since"] == pytest.approx(
            weatherdata[const.MAPPING_PRECIPITATION], abs=1e-3
        )
        assert est["precip_since"] < uncut["precip_since"] - 1.0


class TestTheSpansAreComputedOnce:
    async def test_one_refresh_asks_once(self, coordinator, monkeypatch):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, rain_at={20: 6.0})
        await _silent(store, zone, _record(6, 12))
        calls = []
        real = live_estimate_module.zone_blocked_spans

        def counting(*args, **kwargs):
            calls.append(args)
            return real(*args, **kwargs)

        monkeypatch.setattr(live_estimate_module, "zone_blocked_spans", counting)
        est = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), _inputs())
        assert est["available"] is True
        assert len(calls) == 1
        _store, _zone_arg, start, end = calls[0]
        assert (start, end) == (T0, NOW)


class TestTheCarryFollowsTheOutages:
    """At 23:30 the hours up to 23:00 are carried. A change of the outage record
    or of the setting must price them again rather than reuse them."""

    LATE = NOW - timedelta(minutes=30)

    def _est(self, c, store, zone):
        return c._intraday_for_zone(
            store.get_zone(zone[const.ZONE_ID]), _inputs(now=self.LATE)
        )

    async def test_an_outage_that_closes_drops_the_carried_hours(self, coordinator):
        """Carried while the outage was open, hours 09-23 were blocked; it
        closed at 12:00, so 12-23 count again."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0)
        await _silent(store, zone, _record(6))
        open_est = self._est(c, store, zone)
        assert c._hourly_carry()

        await _silent(store, zone, _record(6, 12))
        warm = self._est(c, store, zone)
        c._hourly_carry().clear()
        cold = self._est(c, store, zone)
        assert warm == cold
        assert warm["et_since"] > open_est["et_since"]

    async def test_an_open_outage_keeps_the_carried_hours_from_one_minute_to_the_next(
        self, coordinator, monkeypatch
    ):
        """The key is the outage's record, not the spans cut from it: an open
        span ends at "now" and would change every minute, and the whole window
        would be priced again each time."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0)
        await _silent(store, zone, _record(6))
        self._est(c, store, zone)
        carried = c._hourly_carry()[zone[const.ZONE_ID]]
        assert carried.boundary == NOW - H

        priced_from = []
        real = live_estimate_module.hourly_eto_priced

        def recording(readings, watermark, *args, **kwargs):
            priced_from.append(watermark)
            return real(readings, watermark, *args, **kwargs)

        monkeypatch.setattr(live_estimate_module, "hourly_eto_priced", recording)
        c._intraday_for_zone(
            store.get_zone(zone[const.ZONE_ID]),
            _inputs(now=self.LATE + timedelta(minutes=2)),
        )

        assert priced_from == [carried.boundary]
        assert c._hourly_carry()[zone[const.ZONE_ID]].outages == carried.outages

    async def test_switching_the_setting_drops_the_carried_hours(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, 2.0)
        await _silent(store, zone, _record(6, 12))
        paused = self._est(c, store, zone)

        await _silent(store, zone, _record(6, 12), setting=const.ON_SILENT_SENSOR_KEEP)
        warm = self._est(c, store, zone)
        c._hourly_carry().clear()
        cold = self._est(c, store, zone)
        assert warm == cold
        assert warm["et_since"] > paused["et_since"]


class TestTheCurrentTemperature:
    async def test_a_silent_temperature_is_not_read_as_current(self, coordinator):
        c, store = coordinator
        zone = await _zone(c, store, 2.0)
        await store.async_update_mapping(
            zone[const.ZONE_MAPPING], {const.MAPPING_DATA_LAST_ENTRY: {T: 25.0}}
        )
        zone = store.get_zone(zone[const.ZONE_ID])
        assert c._latest_temperature(zone, {}) == 25.0
        silent = {T: ((NOW - 2 * H, NOW),)}
        assert c._latest_temperature(zone, {}, blocked=silent, now=NOW) is None
        earlier = {T: ((NOW - 5 * H, NOW - 2 * H),)}
        assert c._latest_temperature(zone, {}, blocked=earlier, now=NOW) == 25.0
