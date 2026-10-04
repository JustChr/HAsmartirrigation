"""Weather-sensor liveness: the pure rules, without a running Home Assistant."""

import json
import pathlib
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from homeassistant.util import dt as dt_util

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.calculation import BUFFER_RETENTION
from custom_components.irrigation_plus.sensor_liveness import (
    Evidence,
    Outage,
    Seen,
    advance_outages,
    first_report_after,
    last_sign_of_life,
    outage_event_payload,
    outages_of,
    sensor_fields_by_entity,
    stale_issue_placeholders,
)


def test_closed_outages_are_kept_as_long_as_the_buffer_may_keep_rows():
    """Closed outages are kept as long as the reading buffer may keep rows: the
    retention equals the buffer's cap."""
    assert (
        const.SENSOR_OUTAGE_RETENTION_DAYS * 86400 == BUFFER_RETENTION.total_seconds()
    )


def test_the_limits_are_the_documented_ones():
    """The docs name three hours and a check every five minutes; the startup grace
    is ten minutes."""
    assert const.SENSOR_STALE_AFTER_SECONDS == 3 * 3600
    assert const.SENSOR_LIVENESS_INTERVAL_SECONDS == 5 * 60
    assert const.SENSOR_LIVENESS_STARTUP_GRACE_SECONDS == 10 * 60


def _cfg(source, entity=None):
    cfg = {const.MAPPING_CONF_SOURCE: source}
    if entity is not None:
        cfg[const.MAPPING_CONF_SENSOR] = entity
    return cfg


def test_only_sensor_fields_with_an_entity_are_watched():
    mappings = {
        const.MAPPING_TEMPERATURE: _cfg(const.MAPPING_CONF_SOURCE_SENSOR, "sensor.t"),
        const.MAPPING_DEWPOINT: _cfg(const.MAPPING_CONF_SOURCE_SENSOR, "sensor.t"),
        # The panel clears the entity when a field's source changes; another
        # client can leave it behind.
        const.MAPPING_HUMIDITY: _cfg(
            const.MAPPING_CONF_SOURCE_WEATHER_SERVICE, "sensor.left_over"
        ),
        const.MAPPING_PRESSURE: _cfg(
            const.MAPPING_CONF_SOURCE_STATIC_VALUE, "sensor.left_over"
        ),
        const.MAPPING_EVAPOTRANSPIRATION: _cfg(
            const.MAPPING_CONF_SOURCE_NONE, "sensor.left_over"
        ),
        const.MAPPING_WINDSPEED: _cfg(const.MAPPING_CONF_SOURCE_SENSOR, ""),
        # The setup wizard stores a sensor field without an entity key.
        const.MAPPING_PRECIPITATION: _cfg(const.MAPPING_CONF_SOURCE_SENSOR),
        const.MAPPING_SOLRAD: "legacy bare string",
    }
    assert sensor_fields_by_entity(mappings) == {
        "sensor.t": (const.MAPPING_TEMPERATURE, const.MAPPING_DEWPOINT),
    }


def test_a_value_set_by_hand_is_never_watched():
    mappings = {
        const.MAPPING_PRESSURE: _cfg(
            const.MAPPING_CONF_SOURCE_SENSOR, "input_number.pressure"
        ),
        # Exempt is the input_number domain, not a name that merely contains it.
        const.MAPPING_HUMIDITY: _cfg(
            const.MAPPING_CONF_SOURCE_SENSOR, "sensor.input_number_mirror"
        ),
    }
    assert sensor_fields_by_entity(mappings) == {
        "sensor.input_number_mirror": (const.MAPPING_HUMIDITY,)
    }


T0 = datetime(2026, 7, 1, 12, 0, 0)


def _seen(entity_id="sensor.t", *, valid=True, reported=T0, changed=T0):
    return Seen(entity_id=entity_id, valid=valid, reported=reported, changed=changed)


class TestLastSignOfLife:
    def test_the_device_vouches_for_a_quiet_field(self):
        rain = _seen("sensor.rain", reported=T0 - timedelta(hours=5))
        temp = _seen("sensor.temp", reported=T0 - timedelta(minutes=1))
        assert last_sign_of_life(rain, [temp], None) == T0 - timedelta(minutes=1)

    def test_without_a_device_the_entity_vouches_for_itself(self):
        own = _seen(reported=T0 - timedelta(hours=2))
        assert last_sign_of_life(own, [], None) == T0 - timedelta(hours=2)

    def test_an_unavailable_entity_is_silent_whatever_its_device_does(self):
        own = _seen(valid=False, reported=T0)
        sibling = _seen("sensor.temp", reported=T0)
        remembered = T0 - timedelta(hours=4)
        assert last_sign_of_life(own, [sibling], remembered) == remembered

    def test_an_unavailable_sibling_does_not_vouch(self):
        own = _seen(reported=T0 - timedelta(hours=5))
        sibling = _seen("sensor.temp", valid=False, reported=T0)
        assert last_sign_of_life(own, [sibling], None) == T0 - timedelta(hours=5)

    def test_a_missing_entity_with_nothing_remembered_has_no_sign(self):
        assert last_sign_of_life(None, [], None) is None

    def test_the_remembered_sign_never_moves_backwards(self):
        own = _seen(reported=T0 - timedelta(hours=1))
        assert last_sign_of_life(own, [], T0) == T0

    def test_a_missing_entity_is_silent_whatever_its_device_does(self):
        sibling = _seen("sensor.temp", reported=T0)
        remembered = T0 - timedelta(hours=4)
        assert last_sign_of_life(None, [sibling], remembered) == remembered
        assert last_sign_of_life(None, [sibling], None) is None


class TestFirstReportAfter:
    def test_the_fields_own_change_marks_its_return(self):
        """The device kept changing while the field was dead: its own return counts."""
        start = T0 - timedelta(hours=6)
        own = _seen(changed=T0 - timedelta(minutes=3))
        battery = _seen("sensor.battery", changed=start + timedelta(minutes=30))
        quiet = _seen("sensor.rain", changed=start - timedelta(hours=1))
        assert first_report_after(own, [battery, quiet], start) == T0 - timedelta(
            minutes=3
        )

    def test_a_quiet_field_takes_the_devices_earliest_change(self):
        """A rain gauge at zero does not change when its station returns."""
        start = T0 - timedelta(hours=6)
        own = _seen(changed=start - timedelta(hours=1))
        temp = _seen("sensor.temp", changed=T0 - timedelta(minutes=3))
        wind = _seen("sensor.wind", changed=T0 - timedelta(minutes=4))
        assert first_report_after(own, [temp, wind], start) == T0 - timedelta(minutes=4)

    def test_nothing_changed_since_the_start(self):
        start = T0 - timedelta(hours=6)
        own = _seen(changed=start - timedelta(minutes=1))
        assert first_report_after(own, [], start) is None

    def test_an_unavailable_state_is_not_a_return(self):
        start = T0 - timedelta(hours=6)
        own = _seen(valid=False, changed=T0)
        assert first_report_after(own, [], start) is None

    def test_an_unavailable_sibling_is_not_a_return(self):
        start = T0 - timedelta(hours=6)
        quiet = _seen(changed=start - timedelta(hours=1))
        gone = _seen("sensor.battery", valid=False, changed=start + timedelta(hours=2))
        alive = _seen("sensor.temp", changed=T0 - timedelta(minutes=4))
        assert first_report_after(quiet, [gone, alive], start) == T0 - timedelta(
            minutes=4
        )

    def test_a_change_at_the_start_itself_is_not_after_it(self):
        start = T0 - timedelta(hours=6)
        later = _seen("sensor.temp", changed=T0 - timedelta(minutes=3))
        # Neither the field's own change at the start nor a sibling's counts.
        at_start = _seen(changed=start)
        assert first_report_after(at_start, [later], start) == T0 - timedelta(minutes=3)
        quiet = _seen(changed=start - timedelta(hours=1))
        sibling_at_start = _seen("sensor.wind", changed=start)
        assert first_report_after(quiet, [sibling_at_start, later], start) == (
            T0 - timedelta(minutes=3)
        )

    def test_without_a_device_the_entity_marks_its_own_return(self):
        start = T0 - timedelta(hours=6)
        own = _seen(changed=T0 - timedelta(minutes=3))
        assert first_report_after(own, [], start) == T0 - timedelta(minutes=3)


def _record(**changes):
    return {"entity_id": "sensor.t", "start": "2026-07-01T08:00:00"} | changes


class TestOutageInTheStore:
    def test_round_trip(self):
        outage = Outage(
            "sensor.t", "dev1", ("Temperature",), T0 - timedelta(hours=4), T0
        )
        assert outage.to_store() == {
            "entity_id": "sensor.t",
            "device_id": "dev1",
            "fields": ["Temperature"],
            "start": "2026-07-01T08:00:00",
            "end": "2026-07-01T12:00:00",
        }
        assert Outage.from_store(outage.to_store()) == outage

    def test_an_open_outage_has_no_end(self):
        outage = Outage("sensor.t", None, ("Temperature",), T0)
        assert outage.to_store()["end"] is None
        assert Outage.from_store(outage.to_store()) == outage

    @pytest.mark.parametrize(
        "raw",
        [
            None,
            "text",
            {},
            {"entity_id": "sensor.t"},
            {"entity_id": "sensor.t", "start": "garbage"},
            {"start": "2026-07-01T08:00:00"},
            _record(entity_id=""),
            _record(fields=5),
            _record(fields="Temperature"),
            _record(fields=[1]),
            _record(fields=["Temperature", 1]),
            _record(end="garbage"),
        ],
    )
    def test_an_unreadable_record_is_dropped_not_raised(self, raw):
        assert Outage.from_store(raw) is None

    @pytest.mark.parametrize(
        "raw", [_record(), _record(fields=None), _record(fields=[]), _record(fields="")]
    )
    def test_a_record_with_no_fields_and_no_device_still_reads(self, raw):
        assert Outage.from_store(raw) == Outage(
            "sensor.t", None, (), T0 - timedelta(hours=4)
        )


class TestOutagesOf:
    def test_it_keeps_what_is_readable_and_skips_the_rest(self):
        first = Outage("sensor.t", "dev1", ("Temperature",), T0 - timedelta(hours=6))
        last = Outage("sensor.w", None, ("Windspeed",), T0 - timedelta(hours=4), T0)
        stored = [first.to_store(), "junk", None, _record(fields=5), last.to_store()]
        assert outages_of({const.MAPPING_SENSOR_OUTAGES: stored}) == [first, last]

    @pytest.mark.parametrize(
        "mapping",
        [
            {},
            {const.MAPPING_SENSOR_OUTAGES: None},
            {const.MAPPING_SENSOR_OUTAGES: 5},
        ],
    )
    def test_a_group_without_an_outage_list_has_no_outages(self, mapping):
        assert outages_of(mapping) == []


STALE = timedelta(seconds=const.SENSOR_STALE_AFTER_SECONDS)


def _evidence(last, *, fields=("Temperature",), device="dev1", recovered=None):
    return Evidence(fields=fields, device_id=device, last=last, recovered=recovered)


class TestAdvanceOutages:
    def test_silence_up_to_the_limit_is_bridged(self):
        assert advance_outages([], {"sensor.t": _evidence(T0 - STALE)}, T0) == (
            [],
            [],
            [],
        )

    def test_silence_past_the_limit_opens_an_outage_at_the_last_sign(self):
        last = T0 - STALE - timedelta(seconds=1)
        expected = Outage("sensor.t", "dev1", ("Temperature",), last)
        assert advance_outages([], {"sensor.t": _evidence(last)}, T0) == (
            [expected],
            [expected],
            [],
        )

    def test_an_open_outage_is_not_opened_twice(self):
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.t", "dev1", ("Temperature",), start)
        assert advance_outages([open_], {"sensor.t": _evidence(start)}, T0) == (
            [open_],
            [],
            [],
        )

    def test_a_new_sign_closes_it_at_the_first_report(self):
        start = T0 - timedelta(hours=5)
        back = T0 - timedelta(minutes=4)
        open_ = Outage("sensor.t", "dev1", ("Temperature",), start)
        ended = Outage("sensor.t", "dev1", ("Temperature",), start, back)
        assert advance_outages(
            [open_], {"sensor.t": _evidence(T0, recovered=back)}, T0
        ) == ([ended], [], [ended])

    def test_without_a_recorded_change_the_newest_report_ends_it(self):
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.t", "dev1", ("Temperature",), start)
        _, _, closed = advance_outages(
            [open_], {"sensor.t": _evidence(T0 - timedelta(minutes=1))}, T0
        )
        assert closed[0].end == T0 - timedelta(minutes=1)

    def test_an_outage_of_an_entity_no_longer_watched_ends_now(self):
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.gone", "dev1", ("Temperature",), start)
        ended = Outage("sensor.gone", "dev1", ("Temperature",), start, T0)
        assert advance_outages([open_], {}, T0) == ([ended], [], [ended])

    def test_no_evidence_opens_nothing(self):
        assert advance_outages([], {"sensor.t": _evidence(None)}, T0) == ([], [], [])

    def test_closed_outages_older_than_the_retention_are_dropped(self):
        edge = T0 - timedelta(days=const.SENSOR_OUTAGE_RETENTION_DAYS)
        old = Outage(
            "sensor.a",
            None,
            ("Temperature",),
            edge - timedelta(hours=5),
            edge - timedelta(seconds=1),
        )
        kept = Outage(
            "sensor.b", None, ("Temperature",), edge - timedelta(hours=5), edge
        )
        still_open = Outage("sensor.c", None, ("Temperature",), T0 - timedelta(days=30))
        evidence = {"sensor.c": _evidence(T0 - timedelta(days=30), device=None)}
        assert advance_outages([old, kept, still_open], evidence, T0) == (
            [kept, still_open],
            [],
            [],
        )

    def test_a_sensor_that_recovered_can_fall_silent_again(self):
        """A closed record neither blocks the next outage nor is reported again."""
        earlier = Outage(
            "sensor.t",
            "dev1",
            ("Temperature",),
            T0 - timedelta(days=2),
            T0 - timedelta(days=1),
        )
        last = T0 - STALE - timedelta(seconds=1)
        again = Outage("sensor.t", "dev1", ("Temperature",), last)
        assert advance_outages([earlier], {"sensor.t": _evidence(last)}, T0) == (
            [earlier, again],
            [again],
            [],
        )

    def test_a_change_elsewhere_on_the_device_does_not_end_a_silent_field(self):
        """No sign newer than the start: a dated return alone ends nothing."""
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.t", "dev1", ("Temperature",), start)
        evidence = {"sensor.t": _evidence(start, recovered=T0 - timedelta(minutes=4))}
        assert advance_outages([open_], evidence, T0) == ([open_], [], [])

    def test_a_late_check_closes_and_reopens_in_one_go(self):
        """A sign after the start, but older than the limit: the outage ends at that
        sign and a new one starts there."""
        start = T0 - timedelta(hours=10)
        newest = T0 - STALE - timedelta(hours=1)
        open_ = Outage("sensor.t", "dev1", ("Temperature",), start)
        ended = Outage("sensor.t", "dev1", ("Temperature",), start, newest)
        again = Outage("sensor.t", "dev1", ("Temperature",), newest)
        assert advance_outages([open_], {"sensor.t": _evidence(newest)}, T0) == (
            [ended, again],
            [again],
            [ended],
        )


class TestStaleIssuePlaceholders:
    def test_no_open_outage_means_no_notice(self):
        closed = Outage("sensor.t", None, ("Temperature",), T0 - timedelta(hours=5), T0)
        assert stale_issue_placeholders("Garden", [closed]) is None

    def test_the_notice_names_every_silent_entity_and_the_earliest_start(self):
        temp = Outage(
            "sensor.temp", "dev1", ("Temperature", "Dewpoint"), T0 - timedelta(hours=4)
        )
        wind = Outage("sensor.wind", "dev1", ("Windspeed",), T0 - timedelta(hours=6))
        assert stale_issue_placeholders("Garden", [temp, wind]) == {
            "group": "Garden",
            "entities": "sensor.wind (Windspeed), sensor.temp (Temperature, Dewpoint)",
            "since": "2026-07-01 06:00",
        }

    def test_closed_outages_do_not_shape_the_notice(self):
        gone_temp = Outage(
            "sensor.temp",
            "dev1",
            ("Temperature",),
            T0 - timedelta(hours=48),
            T0 - timedelta(hours=43),
        )
        gone_wind = Outage(
            "sensor.wind",
            None,
            ("Windspeed",),
            T0 - timedelta(hours=24),
            T0 - timedelta(hours=20),
        )
        silent = Outage(
            "sensor.temp", "dev1", ("Temperature",), T0 - timedelta(hours=4)
        )
        assert stale_issue_placeholders("Garden", [gone_temp, gone_wind, silent]) == {
            "group": "Garden",
            "entities": "sensor.temp (Temperature)",
            "since": "2026-07-01 08:00",
        }

    def test_entities_that_fell_silent_together_are_listed_by_entity_id(self):
        start = T0 - timedelta(hours=4)
        wind = Outage("sensor.wind", "dev1", ("Windspeed",), start)
        temp = Outage("sensor.temp", "dev1", ("Temperature",), start)
        assert stale_issue_placeholders("Garden", [wind, temp])["entities"] == (
            "sensor.temp (Temperature), sensor.wind (Windspeed)"
        )


class TestOutageEventPayload:
    @pytest.fixture(autouse=True)
    def _berlin(self):
        """Pin HA's zone: the offsets below must not follow the suite's zone."""
        before = dt_util.get_default_time_zone()
        dt_util.set_default_time_zone(ZoneInfo("Europe/Berlin"))
        yield
        dt_util.set_default_time_zone(before)

    def test_an_outage_starting(self):
        outage = Outage("sensor.t", "dev1", ("Temperature",), T0 - timedelta(hours=4))
        assert outage_event_payload(3, "Garden", outage) == {
            "mapping_id": 3,
            "mapping": "Garden",
            "entity_id": "sensor.t",
            "device_id": "dev1",
            "fields": ["Temperature"],
            "since": "2026-07-01T08:00:00+02:00",
            "until": None,
            "stale": True,
        }

    def test_an_outage_ending(self):
        outage = Outage("sensor.t", None, ("Temperature",), T0 - timedelta(hours=4), T0)
        assert outage_event_payload(3, "Garden", outage) == {
            "mapping_id": 3,
            "mapping": "Garden",
            "entity_id": "sensor.t",
            "device_id": None,
            "fields": ["Temperature"],
            "since": "2026-07-01T08:00:00+02:00",
            "until": "2026-07-01T12:00:00+02:00",
            "stale": False,
        }


TRANSLATIONS = (
    pathlib.Path(__file__).parent.parent
    / "custom_components"
    / "irrigation_plus"
    / "translations"
)


@pytest.mark.parametrize("lang", ["de", "en", "es", "fr", "it", "nl", "no", "sk"])
def test_the_stale_notice_has_texts_with_their_placeholders(lang):
    issues = json.loads((TRANSLATIONS / f"{lang}.json").read_text(encoding="utf-8"))[
        "issues"
    ]
    notice = issues[const.ISSUE_WEATHER_SENSOR_STALE]
    # Not fixable, so a description and no fix_flow (Home Assistant allows one).
    assert set(notice) == {"title", "description"}
    assert "{group}" in notice["title"]
    assert "{entities}" in notice["description"]
    assert "{since}" in notice["description"]
    # No other placeholder: the notice supplies only these three.
    for text in notice.values():
        assert set(re.findall(r"\{(\w+)\}", text)) <= {"group", "entities", "since"}
        # An ASCII apostrophe before a brace quotes it in ICU, and a lone brace
        # breaks the message: either would leave a placeholder unfilled.
        assert not re.search(r"'[{}<>]", text)
        assert text.count("{") == text.count("}") == len(re.findall(r"\{\w+\}", text))
