"""The live estimate's daily mirror of a pausing sensor group books what the commit does.

A zone whose commit runs the daily equation is estimated by that same equation
over the elapsed window. For a pausing group the commit books only the share of
the window in which every field of the daily form was measured, so the mirror
books that share too. A field silent for the whole window leaves nothing to book
-- which is an answer, not a reason to price the window from a weather service.
"""

from datetime import timedelta

import pytest

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus import live_estimate as live_estimate_module
from custom_components.irrigation_plus.sensor_liveness import Outage
from tests.test_live_estimate_replayed_balance import (
    ANCHOR,
    WINDOW_END,
    _estimating_inputs,
    _estimating_zone,
    _hourly_forecast,
    _provider_rows,
    make_coordinator,
)

H = timedelta(hours=1)
T = const.MAPPING_TEMPERATURE


@pytest.fixture
async def coordinator(hass):
    """The shipped default: the hourly calculation off, the daily form runs."""
    return await make_coordinator(hass, hourly_calculation=False)


async def _silent(store, zone, start_h, end_h=None, fields=(T,)):
    await store.async_update_mapping(
        zone[const.ZONE_MAPPING],
        {
            const.MAPPING_ON_SILENT_SENSOR: const.ON_SILENT_SENSOR_PAUSE,
            const.MAPPING_SENSOR_OUTAGES: [
                Outage(
                    "sensor.t",
                    "dev1",
                    tuple(fields),
                    ANCHOR + start_h * H,
                    None if end_h is None else ANCHOR + end_h * H,
                ).to_store()
            ],
        },
    )


async def _committed(c, store, zone, now=WINDOW_END):
    zone = store.get_zone(zone[const.ZONE_ID])
    blocked = c._blocked_spans_for_zone(zone, now=now)
    weatherdata, _ = await c._aggregate_for_zone(zone, now=now, blocked=blocked)
    return await c.calculate_module(zone, weatherdata, None, now=now, blocked=blocked)


def _estimate(c, store, zone, instance, module, **inputs_kw):
    inputs = _estimating_inputs(instance, module, forecast=_hourly_forecast())
    inputs.update(inputs_kw)
    return c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), inputs)


class TestTheMirrorBooksTheShare:
    async def test_it_lands_on_the_cut_bucket(self, coordinator):
        """Temperature silent from 4 h to 12 h after the anchor, frozen at 40 °C
        and stamped fresh by the poll: 7-12 h blocked."""
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        store.set_mapping_buffer(
            zone[const.ZONE_MAPPING],
            [
                (
                    {**row, T: 40.0}
                    if ANCHOR + 7 * H <= row[const.RETRIEVED_AT] < ANCHOR + 12 * H
                    else row
                )
                for row in store.get_mapping_buffer(zone[const.ZONE_MAPPING])
            ],
        )
        uncut = await _committed(c, store, zone)
        await _silent(store, zone, 4, 12)

        est = _estimate(c, store, zone, instance, module)
        data = await _committed(c, store, zone)

        assert est["method"] == "daily_mirror"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )
        assert data[const.ZONE_BUCKET] > uncut[const.ZONE_BUCKET] + 0.3

    async def test_a_field_the_daily_form_does_without_changes_nothing(
        self, coordinator
    ):
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        plain = _estimate(c, store, zone, instance, module)
        await _silent(store, zone, 4, 12, fields=(const.MAPPING_HUMIDITY,))
        assert _estimate(c, store, zone, instance, module) == plain


class TestNothingMeasuredIsNothingBooked:
    async def test_it_does_not_fall_back_to_a_weather_service(self, coordinator):
        """A client's hourly series is at hand, and would be the next source."""
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        rows = _provider_rows(0.0)
        await _silent(store, zone, -4)

        est = _estimate(c, store, zone, instance, module, rows=rows, tz=0.0)
        data = await _committed(c, store, zone)

        assert est["method"] == "daily_mirror"
        assert est["et_since"] == 0.0
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_a_zone_that_averages_forecast_days_in_needs_no_forecast_for_it(
        self, coordinator
    ):
        """The commit books 0 whatever the forecast, so the mirror needs none for it."""
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        instance.forecast_days = 2
        rows = _provider_rows(0.0)
        await _silent(store, zone, -4)

        est = _estimate(c, store, zone, instance, module, rows=rows, tz=0.0)
        data = await _committed(c, store, zone)

        assert est["method"] == "daily_mirror"
        assert est["et_since"] == 0.0
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )


class TestTheProjectionToTheDecisionPoint:
    """The projection books nothing, but it is priced off the window's observed
    part -- which for a pausing group is the part that was measured."""

    MID = ANCHOR + 14 * H
    UNTIL = ANCHOR + 20 * H

    async def _frozen_zone(self, c, store, *, service_forecast=True):
        """From 7 h after the anchor the sensor is frozen at 40 °C, a poll
        stamping it fresh. A test that opens the outage 4 h after the anchor
        (``_silent(.., 4)``) has the temperature silent from then and blocked
        from 7 h, the first three hours being bridged. The reading at ``MID``
        itself is a measurement: an open span ends at the refresh's "now",
        half-open.

        ``service_forecast`` hands the weather service's hourly series in; without
        it the rest of the day is drawn from the sensor group alone."""
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        readings = [
            (
                {**row, T: 40.0}
                if ANCHOR + 7 * H <= row[const.RETRIEVED_AT] < self.MID
                else row
            )
            for row in store.get_mapping_buffer(zone[const.ZONE_MAPPING])
            if row[const.RETRIEVED_AT] <= self.MID
        ]
        store.set_mapping_buffer(zone[const.ZONE_MAPPING], readings)
        inputs = _estimating_inputs(
            instance,
            module,
            now=self.MID,
            forecast=_hourly_forecast() if service_forecast else None,
        )
        return zone, inputs

    def _projected(self, c, store, zone, inputs):
        zone = store.get_zone(zone[const.ZONE_ID])
        estimate = c._intraday_for_zone(zone, inputs)
        return c._carry_estimate_to(zone, estimate, inputs, self.UNTIL)

    async def test_it_is_priced_from_the_cut_window(self, coordinator):
        c, store = coordinator
        zone, inputs = await self._frozen_zone(c, store)
        kept = self._projected(c, store, zone, inputs)
        await _silent(store, zone, 4)
        paused = self._projected(c, store, zone, inputs)
        assert kept["carried_to_decision"] is True
        assert paused["carried_to_decision"] is True
        assert paused["projected_et"] < kept["projected_et"]

    async def test_a_temperature_silent_now_anchors_no_remainder(self, coordinator):
        """With no forecast the rest of the day is drawn from the group's own
        trailing amplitude, held to the temperature it reads now. A temperature
        silent now reads nothing: the sensor's frozen value anchors no remainder,
        and the tier says the day was not projected -- in the estimate and in
        its carry to the decision point alike."""
        c, store = coordinator
        zone, inputs = await self._frozen_zone(c, store, service_forecast=False)
        await store.async_update_mapping(
            zone[const.ZONE_MAPPING],
            {const.MAPPING_TEMPERATURE_AMPLITUDES: [["2026-05-21", 14.0]]},
        )
        kept = self._projected(c, store, zone, inputs)
        assert kept["forecast_tier"] == "self_contained"
        assert kept["projection_tier"] == "self_contained"

        await _silent(store, zone, 4)
        paused = self._projected(c, store, zone, inputs)
        assert paused["forecast_tier"] == "observed"
        assert paused["projection_tier"] == "observed"

    async def test_it_asks_for_its_spans_once(self, coordinator, monkeypatch):
        c, store = coordinator
        zone, inputs = await self._frozen_zone(c, store)
        await _silent(store, zone, 4)
        estimate = c._intraday_for_zone(store.get_zone(zone[const.ZONE_ID]), inputs)
        calls = []
        real = live_estimate_module.zone_blocked_spans

        def counting(*args, **kwargs):
            calls.append(args)
            return real(*args, **kwargs)

        monkeypatch.setattr(live_estimate_module, "zone_blocked_spans", counting)
        c._carry_estimate_to(
            store.get_zone(zone[const.ZONE_ID]), estimate, inputs, self.UNTIL
        )
        assert len(calls) == 1
        assert calls[0][2:] == (ANCHOR, self.MID)
