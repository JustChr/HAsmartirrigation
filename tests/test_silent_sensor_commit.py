"""A pausing sensor group's commit: the gate, the cut, the booking and its explanation."""

import datetime
from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util import dt as dt_util

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.sensor_liveness import Outage
from custom_components.irrigation_plus.store import SmartIrrigationStorage

W = datetime.datetime(2026, 7, 1, 0, 0, 0)  # the zone's watermark, naive on HA's clock
NOW = W + timedelta(hours=24)
H = timedelta(hours=1)
T = const.MAPPING_TEMPERATURE
PRECIP = const.MAPPING_PRECIPITATION


def _sensor(entity, aggregate=None):
    field = {
        const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
        const.MAPPING_CONF_SENSOR: entity,
    }
    if aggregate is not None:
        field[const.MAPPING_CONF_AGGREGATE] = aggregate
    return field


def _outage(start_h, end_h=None, fields=(T,)):
    return Outage(
        "sensor.t",
        "dev1",
        tuple(fields),
        W + start_h * H,
        None if end_h is None else W + end_h * H,
    ).to_store()


@pytest.fixture
async def coord(hass):
    """A real coordinator and store; the module is stubbed unless a test wires one."""
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    entry = Mock()
    entry.unique_id = "t"
    entry.data = {}
    entry.options = {}
    c = SmartIrrigationCoordinator(hass, None, entry, store)
    c.store = store
    c.calculate_module = AsyncMock(
        return_value={const.ZONE_BUCKET: -1.0, const.ZONE_DURATION: 0}
    )
    return c, store


async def _group(store, *, setting="pause", outages=(), mappings=None, readings=None):
    created = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "Garden",
            const.MAPPING_MAPPINGS: (
                mappings if mappings is not None else {T: _sensor("sensor.t")}
            ),
            const.MAPPING_DATA: (
                readings
                if readings is not None
                else [{const.RETRIEVED_AT: W + h * H, T: float(h)} for h in range(24)]
            ),
            const.MAPPING_ON_SILENT_SENSOR: setting,
            const.MAPPING_SENSOR_OUTAGES: list(outages),
        }
    )
    return created[const.MAPPING_ID]


async def _zone(store, mapping_id, *, module_id=1, watermark=W):
    created = await store.async_create_zone(
        {
            const.ZONE_NAME: "z",
            const.ZONE_MAPPING: mapping_id,
            const.ZONE_MODULE: module_id,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_BUCKET: 0.0,
            const.ZONE_MAXIMUM_BUCKET: 50.0,
            const.ZONE_DRAINAGE_RATE: 0.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_MAXIMUM_DURATION: 3600,
            const.ZONE_LEAD_TIME: 0,
            const.ZONE_LAST_CONSUMED: watermark,
        }
    )
    return created[const.ZONE_ID]


def _gate(c, store, zone_id):
    return c._blocked_spans_for_zone(store.get_zone(zone_id), now=NOW)


class TestTheGate:
    async def test_a_pausing_group_is_cut_where_its_outage_blocks(self, coord):
        c, store = coord
        zone = await _zone(store, await _group(store, outages=[_outage(2, 10)]))
        assert _gate(c, store, zone) == {T: ((W + 5 * H, W + 10 * H),)}

    async def test_an_open_outage_blocks_up_to_the_commits_now(self, coord):
        """Up to the ``now`` the commit is handed, the end of its window, not to
        the clock."""
        c, store = coord
        zone = await _zone(store, await _group(store, outages=[_outage(2)]))
        assert _gate(c, store, zone) == {T: ((W + 5 * H, NOW),)}

    async def test_a_group_that_keeps_is_not_cut(self, coord):
        c, store = coord
        mid = await _group(store, setting="keep", outages=[_outage(2, 10)])
        assert _gate(c, store, await _zone(store, mid)) is None

    async def test_the_hourly_calculation_is_cut_the_same(self, coord):
        c, store = coord
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: True})
        mid = await _group(store, outages=[_outage(2, 10)])
        assert _gate(c, store, await _zone(store, mid)) == {
            T: ((W + 5 * H, W + 10 * H),)
        }

    async def test_a_window_no_outage_reaches_is_not_cut(self, coord):
        c, store = coord
        mid = await _group(store, outages=[_outage(-30, -20), _outage(2, 4)])
        assert _gate(c, store, await _zone(store, mid)) is None

    async def test_a_zone_that_never_consumed_is_not_cut(self, coord):
        c, store = coord
        mid = await _group(store, outages=[_outage(2, 10)])
        assert _gate(c, store, await _zone(store, mid, watermark=None)) is None

    async def test_a_zone_without_its_group_is_not_cut(self, coord):
        c, store = coord
        assert _gate(c, store, await _zone(store, 99)) is None
        assert c._blocked_spans_for_zone({const.ZONE_MAPPING: None}, now=NOW) is None

    async def test_a_rain_gauge_is_never_cut_and_a_rain_rate_is(self, coord):
        c, store = coord
        both = (T, PRECIP)
        gauge = await _group(
            store,
            mappings={T: _sensor("sensor.t"), PRECIP: _sensor("sensor.rain")},
            outages=[_outage(2, 10, fields=both)],
        )
        rate = await _group(
            store,
            mappings={
                T: _sensor("sensor.t"),
                PRECIP: _sensor("sensor.rain", const.MAPPING_CONF_AGGREGATE_RIEMANNSUM),
            },
            outages=[_outage(2, 10, fields=both)],
        )
        assert set(_gate(c, store, await _zone(store, gauge))) == {T}
        assert set(_gate(c, store, await _zone(store, rate))) == {T, PRECIP}

    async def test_outage_stamps_with_an_offset_are_read_on_has_clock(self, coord):
        """A record edited by hand, or written by another build, may carry offsets."""
        c, store = coord
        local = W.replace(tzinfo=dt_util.get_default_time_zone())
        record = {
            "entity_id": "sensor.t",
            "device_id": "dev1",
            "fields": [T],
            "start": (local + 2 * H).isoformat(),
            "end": (local + 10 * H).isoformat(),
        }
        zone = await _zone(store, await _group(store, outages=[record]))
        assert _gate(c, store, zone) == {T: ((W + 5 * H, W + 10 * H),)}


class TestTheCommitCarriesTheSpans:
    async def test_the_aggregate_and_both_records_are_cut(self, coord):
        c, store = coord
        zone = await _zone(store, await _group(store, outages=[_outage(2, 10)]))
        c._record_window_amplitude = AsyncMock()
        c._record_window_radiation = AsyncMock()

        await c.async_calculate_zone(zone, now=NOW)

        expected = {T: ((W + 5 * H, W + 10 * H),)}
        assert c._record_window_amplitude.call_args.kwargs["blocked"] == expected
        assert c._record_window_radiation.call_args.kwargs["blocked"] == expected
        weatherdata = c.calculate_module.call_args.args[1]
        # 0..23 without the frozen rows of hours 5..9.
        assert weatherdata[T] == pytest.approx(
            (sum(range(24)) - sum(range(5, 10))) / 19
        )

    async def test_a_group_that_keeps_aggregates_as_before(self, coord):
        c, store = coord
        mid = await _group(store, setting="keep", outages=[_outage(2, 10)])
        c._record_window_amplitude = AsyncMock()

        await c.async_calculate_zone(await _zone(store, mid), now=NOW)

        assert c._record_window_amplitude.call_args.kwargs["blocked"] is None
        assert c.calculate_module.call_args.args[1][T] == 11.5


class TestTheRecordsSkipABlockedWindow:
    async def test_no_amplitude_is_recorded_when_the_temperature_was_blocked(
        self, coord
    ):
        c, store = coord
        mid = await _group(store)
        zone = store.get_zone(await _zone(store, mid))
        data = {
            const.MAPPING_DATA_MULTIPLIER: 1.0,
            const.MAPPING_MIN_TEMP: 5.0,
            const.MAPPING_MAX_TEMP: 15.0,
        }

        await c._record_window_amplitude(
            zone, data, now=NOW, blocked={T: ((W, W + H),)}
        )
        assert store.get_mapping(mid)[const.MAPPING_TEMPERATURE_AMPLITUDES] == []

        other = {const.MAPPING_DEWPOINT: ((W, W + H),)}
        await c._record_window_amplitude(zone, data, now=NOW, blocked=other)
        assert store.get_mapping(mid)[const.MAPPING_TEMPERATURE_AMPLITUDES] == [
            [NOW.date().isoformat(), 10.0]
        ]

    async def test_no_radiation_pair_is_recorded_when_the_sun_was_blocked(self, coord):
        c, store = coord
        mid = await _group(store)
        zone = store.get_zone(await _zone(store, mid))
        c._effective_latitude = 40.0
        c._effective_longitude = 0.0
        data = {const.MAPPING_SOLRAD: 15.0}
        sun = {const.MAPPING_SOLRAD: ((W, W + H),)}

        await c._record_window_radiation(zone, data, now=NOW, blocked=sun)
        assert store.get_mapping(mid)[const.MAPPING_RADIATION_CALIBRATION] == []

        await c._record_window_radiation(
            zone, data, now=NOW, blocked={T: ((W, W + H),)}
        )
        assert len(store.get_mapping(mid)[const.MAPPING_RADIATION_CALIBRATION]) == 1


ET = const.MAPPING_EVAPOTRANSPIRATION
DEW = const.MAPPING_DEWPOINT
SUN = const.MAPPING_SOLRAD
WIND = const.MAPPING_WINDSPEED
PRESSURE = const.MAPPING_PRESSURE


async def _module(c, store, name, *, returns, forecast_days=0):
    """A module of this name whose instance is a stub returning ``returns``; from
    here on the coordinator runs its real calculate_module."""
    module = await store.async_create_module(
        {const.MODULE_NAME: name, "description": "", "config": {}}
    )
    instance = Mock()
    instance.calculate = Mock(return_value=returns)
    instance.forecast_days = forecast_days
    c.getModuleInstanceByID = AsyncMock(return_value=instance)
    if "calculate_module" in vars(c):
        del c.calculate_module
    return module[const.MODULE_ID], instance


def _hours(**fields):
    """24 hourly rows carrying ``fields`` (a value or a callable of the hour)."""
    return [
        {
            const.RETRIEVED_AT: W + h * H,
            **{k: (v(h) if callable(v) else v) for k, v in fields.items()},
        }
        for h in range(24)
    ]


class TestTheBooking:
    async def test_the_module_is_handed_the_spans(self, coord):
        c, store = coord
        zone = await _zone(store, await _group(store, outages=[_outage(2, 10)]))

        await c.async_calculate_zone(zone, now=NOW)

        assert c.calculate_module.call_args.kwargs["blocked"] == {
            T: ((W + 5 * H, W + 10 * H),)
        }

    def test_pyeto_needs_dewpoint_temperature_wind_and_pressure(self):
        from custom_components.irrigation_plus.calculation import (
            _REQUIRED_SENSOR_FIELDS,
        )

        assert _REQUIRED_SENSOR_FIELDS["PyETO"] == (
            DEW,
            T,
            const.MAPPING_WINDSPEED,
            const.MAPPING_PRESSURE,
        )
        assert _REQUIRED_SENSOR_FIELDS["Passthrough"] == (ET,)

    async def test_pyeto_books_the_share_in_which_its_fields_were_measured(self, coord):
        c, store = coord
        module_id, instance = await _module(c, store, "PyETO", returns=-4.0)
        mid = await _group(store, outages=[_outage(2, 10)])
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        instance.calculate.assert_called_once()
        assert store.get_zone(zone)[const.ZONE_DELTA] == pytest.approx(-4.0 * 19 / 24)

    async def test_with_forecast_days_the_whole_mean_is_scaled(self, coord):
        """The module returns the mean of the weather day and its forecast days; the
        blocked time books none of it, the forecast part included."""
        c, store = coord
        module_id, _ = await _module(c, store, "PyETO", returns=-4.0, forecast_days=2)
        mid = await _group(store, outages=[_outage(2, 10)])
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        assert store.get_zone(zone)[const.ZONE_DELTA] == pytest.approx(-4.0 * 19 / 24)

    async def test_a_field_pyeto_does_without_does_not_reduce_the_share(self, coord):
        c, store = coord
        module_id, _ = await _module(c, store, "PyETO", returns=-4.0)
        mid = await _group(
            store,
            mappings={T: _sensor("sensor.t"), SUN: _sensor("sensor.sun")},
            readings=_hours(**{T: 20.0, SUN: 10.0}),
            outages=[_outage(2, 10, fields=(SUN,))],
        )
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        assert store.get_zone(zone)[const.ZONE_DELTA] == -4.0

    async def test_pyeto_without_a_measured_required_field_books_the_rain_only(
        self, coord
    ):
        c, store = coord
        module_id, instance = await _module(c, store, "PyETO", returns=-4.0)
        mid = await _group(
            store,
            mappings={
                T: _sensor("sensor.t"),
                DEW: _sensor("sensor.dew"),
                PRECIP: _sensor("sensor.rain"),
            },
            readings=_hours(**{T: 20.0, PRECIP: lambda h: 0.0 if h < 12 else 3.0}),
            outages=[_outage(-10, fields=(DEW,))],
        )
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        instance.calculate.assert_not_called()
        assert store.get_zone(zone)[const.ZONE_DELTA] == pytest.approx(3.0)
        assert store.get_zone(zone)[const.ZONE_LAST_CONSUMED] == NOW

    async def test_passthrough_books_the_measured_share_of_its_et(self, coord):
        c, store = coord
        module_id, _ = await _module(c, store, "Passthrough", returns=4.0)
        mid = await _group(
            store,
            mappings={ET: _sensor("sensor.et")},
            readings=_hours(**{ET: 4.0}),
            outages=[_outage(2, 10, fields=(ET,))],
        )
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        assert store.get_zone(zone)[const.ZONE_DELTA] == pytest.approx(-4.0 * 19 / 24)

    async def test_passthrough_with_its_et_blocked_throughout_consumes_quietly(
        self, coord, caplog
    ):
        c, store = coord
        module_id, instance = await _module(c, store, "Passthrough", returns=4.0)
        mid = await _group(
            store,
            mappings={ET: _sensor("sensor.et")},
            readings=_hours(**{ET: 4.0}),
            outages=[_outage(-10, fields=(ET,))],
        )
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        instance.calculate.assert_not_called()
        assert store.get_zone(zone)[const.ZONE_DELTA] == 0.0
        assert store.get_zone(zone)[const.ZONE_LAST_CONSUMED] == NOW
        assert "No evapotranspiration value provided" not in caplog.text
        assert "calculation returned no result" not in caplog.text

    async def test_passthrough_without_its_et_for_another_reason_still_says_so(
        self, coord, caplog
    ):
        """Not a silent ET sensor: the field never arrived. Today's error, and the
        window stays where it was."""
        c, store = coord
        module_id, _ = await _module(c, store, "Passthrough", returns=4.0)
        mid = await _group(
            store,
            mappings={ET: _sensor("sensor.et")},
            readings=_hours(**{T: 1.0}),
            outages=[_outage(2, 10)],
        )
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        assert "No evapotranspiration value provided" in caplog.text
        assert store.get_zone(zone)[const.ZONE_LAST_CONSUMED] == W

    async def test_a_static_zone_in_a_pausing_group_books_as_before(self, coord):
        c, store = coord
        module_id, _ = await _module(c, store, "Static", returns=-2.0)
        mid = await _group(store, outages=[_outage(2, 10)])
        zone = await _zone(store, mid, module_id=module_id)

        await c.async_calculate_zone(zone, now=NOW)

        assert store.get_zone(zone)[const.ZONE_DELTA] == -2.0


_RESULT_FIELDS = (
    const.ZONE_DELTA,
    const.ZONE_BUCKET,
    const.ZONE_DURATION,
    const.ZONE_EXPLANATION,
)


async def _results(c, store, module_id, *groups):
    """What one commit writes for a zone on each of the sensor groups."""
    zones = [await _zone(store, mid, module_id=module_id) for mid in groups]
    for zone in zones:
        await c.async_calculate_zone(zone, now=NOW)
    return [{f: store.get_zone(zone)[f] for f in _RESULT_FIELDS} for zone in zones]


class TestAGroupThatIsNotCutCalculatesAsBefore:
    async def test_keep_with_outages_and_pause_without_one_match_a_plain_group(
        self, coord
    ):
        c, store = coord
        module_id, _ = await _module(c, store, "PyETO", returns=-4.0)
        plain, keep, quiet = await _results(
            c,
            store,
            module_id,
            await _group(store, setting="keep"),
            await _group(store, setting="keep", outages=[_outage(2, 10)]),
            await _group(store, outages=[_outage(-30, -20)]),
        )
        assert keep == plain
        assert quiet == plain


class TestTheHourlySwitchDoesNotDecide:
    """A pausing group is cut under the hourly calculation as it is without it."""

    async def test_a_pausing_group_under_the_hourly_switch_is_cut_too(self, coord):
        """The stub keeps the daily form (no measured sun), so the daily fields
        decide: temperature blocked 05:00-10:00 leaves 19 of 24 hours."""
        c, store = coord
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: True})
        module_id, _ = await _module(c, store, "PyETO", returns=-4.0)
        plain, paused = await _results(
            c,
            store,
            module_id,
            await _group(store, setting="keep"),
            await _group(store, outages=[_outage(2, 10)]),
        )
        assert plain[const.ZONE_DELTA] == pytest.approx(-4.0)
        assert paused[const.ZONE_DELTA] == pytest.approx(-4.0 * 19 / 24)
        assert "booked for 79 % of the period" in paused[const.ZONE_EXPLANATION]


class TestTheExplanation:
    async def _explain(self, c, store, module="PyETO", **group):
        module_id, _ = await _module(c, store, module, returns=-2.0)
        zone = await _zone(store, await _group(store, **group), module_id=module_id)
        await c.async_calculate_zone(zone, now=NOW)
        return store.get_zone(zone)[const.ZONE_EXPLANATION]

    async def test_it_names_the_silent_time_and_the_share_booked(self, coord):
        c, store = coord
        text = await self._explain(
            c,
            store,
            mappings={T: _sensor("sensor.t"), DEW: _sensor("sensor.dew")},
            outages=[_outage(2, 10, fields=(T, DEW))],
        )
        assert (
            "No values from Dewpoint, Temperature from 2026-07-01 05:00 to "
            "2026-07-01 10:00 (sensor silent)." in text
        )
        assert "Evapotranspiration booked for 79 % of the period." in text
        assert text.index("(sensor silent)") < text.index("Bucket was")

    async def test_a_share_that_would_round_to_100_reads_99(self, coord):
        """Two minutes silent in a day: right after the sentence naming them, the
        share must not read as all of the period."""
        c, store = coord
        text = await self._explain(c, store, outages=[_outage(2, 5 + 2 / 60)])
        assert "from 2026-07-01 05:00 to 2026-07-01 05:02 (sensor silent)." in text
        assert "Evapotranspiration booked for 99 % of the period." in text

    async def test_a_share_that_would_round_to_0_reads_1(self, coord):
        """Two minutes measured in a day: something was booked, so not 0 %."""
        c, store = coord
        text = await self._explain(c, store, outages=[_outage(-3, 24 - 2 / 60)])
        assert "Evapotranspiration booked for 1 % of the period." in text

    async def test_a_field_blocked_throughout_books_0_percent(self, coord):
        c, store = coord
        text = await self._explain(
            c,
            store,
            mappings={T: _sensor("sensor.t"), DEW: _sensor("sensor.dew")},
            outages=[_outage(-10, fields=(DEW,))],
        )
        assert "Evapotranspiration booked for 0 % of the period." in text

    async def test_each_span_gets_its_own_sentence(self, coord):
        c, store = coord
        text = await self._explain(c, store, outages=[_outage(0, 5), _outage(10, 16)])
        assert text.count("(sensor silent)") == 2
        assert "2026-07-01 13:00 to 2026-07-01 16:00" in text

    async def test_fields_back_milliseconds_apart_share_one_sentence(self, coord):
        """A station reports its fields one by one, so each field's outage ends at
        its own instant, milliseconds after the last. At the minute the sentence
        shows that is one silence, and one sentence names all the fields."""
        c, store = coord
        fields = (T, DEW, WIND, PRESSURE)
        text = await self._explain(
            c,
            store,
            mappings={field: _sensor(f"sensor.{field.lower()}") for field in fields},
            outages=[
                Outage(
                    f"sensor.{field.lower()}",
                    "dev1",
                    (field,),
                    W + 2 * H,
                    W + 10 * H + timedelta(milliseconds=6 * n),
                ).to_store()
                for n, field in enumerate(fields)
            ],
        )
        assert text.count("(sensor silent)") == 1
        assert (
            "No values from Dewpoint, Pressure, Temperature, Wind speed from "
            "2026-07-01 05:00 to 2026-07-01 10:00 (sensor silent)." in text
        )

    async def test_a_field_twice_in_one_shown_minute_is_named_once(self, coord):
        """A replaced sensor: the old and the new entity of one field each record
        their own outage, so the field has two spans that begin and end in the
        same minute the sentence shows. One sentence, the field named once."""
        c, store = coord
        text = await self._explain(
            c,
            store,
            outages=[
                Outage(
                    "sensor.t_old",
                    "dev1",
                    (T,),
                    W + 2 * H + timedelta(seconds=5),
                    W + 5 * H + timedelta(seconds=10),
                ).to_store(),
                Outage(
                    "sensor.t_new",
                    "dev2",
                    (T,),
                    W + 2 * H + timedelta(seconds=20),
                    W + 5 * H + timedelta(seconds=40),
                ).to_store(),
            ],
        )
        assert text.count("(sensor silent)") == 1
        assert (
            "No values from Temperature from 2026-07-01 05:00 to "
            "2026-07-01 05:00 (sensor silent)." in text
        )

    async def test_a_field_back_an_hour_later_gets_its_own_sentence(self, coord):
        """The same beginning, but one field returns in another minute: the spans
        differ as the sentences show them, so each gets a sentence."""
        c, store = coord
        text = await self._explain(
            c,
            store,
            mappings={T: _sensor("sensor.t"), DEW: _sensor("sensor.dew")},
            outages=[
                _outage(2, 10, fields=(T,)),
                _outage(2, 11, fields=(DEW,)),
            ],
        )
        assert text.count("(sensor silent)") == 2
        assert (
            "No values from Temperature from 2026-07-01 05:00 to "
            "2026-07-01 10:00 (sensor silent)." in text
        )
        assert (
            "No values from Dewpoint from 2026-07-01 05:00 to "
            "2026-07-01 11:00 (sensor silent)." in text
        )

    async def test_sentences_follow_the_time_of_their_spans(self, coord):
        """The field recorded first has the later span, yet its sentence comes
        second: the sentences are in the order of the time they name."""
        c, store = coord
        text = await self._explain(
            c,
            store,
            mappings={T: _sensor("sensor.t"), DEW: _sensor("sensor.dew")},
            outages=[
                _outage(10, 16, fields=(T,)),
                _outage(0, 5, fields=(DEW,)),
            ],
        )
        earlier = (
            "No values from Dewpoint from 2026-07-01 03:00 to "
            "2026-07-01 05:00 (sensor silent)."
        )
        later = (
            "No values from Temperature from 2026-07-01 13:00 to "
            "2026-07-01 16:00 (sensor silent)."
        )
        assert earlier in text
        assert later in text
        assert text.index(earlier) < text.index(later)

    async def test_a_field_the_module_does_without_gets_no_share_sentence(self, coord):
        c, store = coord
        text = await self._explain(
            c,
            store,
            mappings={T: _sensor("sensor.t"), SUN: _sensor("sensor.sun")},
            readings=_hours(**{T: 20.0, SUN: 10.0}),
            outages=[_outage(2, 10, fields=(SUN,))],
        )
        assert "No values from Solar radiation" in text
        assert "% of the period" not in text

    async def test_a_static_zone_names_the_time_but_no_share(self, coord):
        c, store = coord
        text = await self._explain(c, store, module="Static", outages=[_outage(2, 10)])
        assert "(sensor silent)" in text
        assert "% of the period" not in text

    async def test_a_group_that_keeps_gets_no_sentence(self, coord):
        c, store = coord
        text = await self._explain(c, store, setting="keep", outages=[_outage(2, 10)])
        assert "(sensor silent)" not in text
