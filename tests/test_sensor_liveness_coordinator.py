"""Weather-sensor liveness in the coordinator: states, registry, record, notice, event."""

import ast
import copy
import pathlib
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.irrigation_plus import (
    SmartIrrigationCoordinator,
    const,
    sensor_liveness,
)
from custom_components.irrigation_plus.sensor_liveness import (
    Outage,
    _entities_of_device,
    seen_from_state,
)

T0 = datetime(2026, 7, 1, 12, 0, 0)  # naive, on HA's clock


def _aware(local_naive):
    """A naive HA-local wall time as Home Assistant stamps states: aware, in UTC."""
    return dt_util.as_utc(local_naive.replace(tzinfo=dt_util.get_default_time_zone()))


def _state(entity_id, value, reported, changed=None):
    return SimpleNamespace(
        entity_id=entity_id,
        state=value,
        last_reported=_aware(reported),
        last_changed=_aware(changed if changed is not None else reported),
    )


class TestSeenFromState:
    def test_state_stamps_land_on_has_clock(self):
        # Tripwire: the scene only proves the conversion if UTC differs from HA's
        # zone here (the autouse hass fixture puts HA on US/Pacific).
        assert _aware(T0).replace(tzinfo=None) != T0
        seen = seen_from_state(
            _state("sensor.t", "21.5", T0, changed=T0 - timedelta(hours=1))
        )
        assert seen.reported == T0
        assert seen.changed == T0 - timedelta(hours=1)
        assert seen.valid is True

    @pytest.mark.parametrize("value", ["unavailable", "unknown"])
    def test_unavailable_and_unknown_are_not_valid(self, value):
        assert seen_from_state(_state("sensor.t", value, T0)).valid is False

    def test_no_state_is_no_snapshot(self):
        assert seen_from_state(None) is None


async def test_the_device_is_read_from_the_entity_registry(hass):
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={("test", "station")}
    )
    registry = er.async_get(hass)
    temp = registry.async_get_or_create(
        "sensor", "test", "temp", device_id=device.id, config_entry=entry
    )
    rain = registry.async_get_or_create(
        "sensor", "test", "rain", device_id=device.id, config_entry=entry
    )
    loose = registry.async_get_or_create("sensor", "test", "loose", config_entry=entry)

    assert _entities_of_device(hass, temp.entity_id) == (device.id, [rain.entity_id])
    assert _entities_of_device(hass, loose.entity_id) == (None, [])
    assert _entities_of_device(hass, "sensor.not_registered") == (None, [])


async def test_only_the_integrations_own_sensors_vouch(hass):
    """Helpers Home Assistant attaches to a device can write on their own
    schedule, and an update entity says nothing about the measurements; a
    helper that is mapped itself is vouched for by its device's sensors."""
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    helper = MockConfigEntry(domain="utility_meter")
    helper.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={("test", "station")},
        name="Station",
    )
    registry = er.async_get(hass)
    temp = registry.async_get_or_create(
        "sensor", "test", "temp", device_id=device.id, config_entry=entry
    )
    rain = registry.async_get_or_create(
        "binary_sensor", "test", "raining", device_id=device.id, config_entry=entry
    )
    meter = registry.async_get_or_create(
        "sensor",
        "utility_meter",
        "rain_today",
        device_id=device.id,
        config_entry=helper,
    )
    registry.async_get_or_create(
        "update", "test", "firmware", device_id=device.id, config_entry=entry
    )

    assert _entities_of_device(hass, temp.entity_id) == (device.id, [rain.entity_id])
    assert _entities_of_device(hass, meter.entity_id) == (
        device.id,
        [temp.entity_id, rain.entity_id],
    )


async def test_the_mapped_sensors_own_integration_vouches_on_a_shared_device(hass):
    """The device belongs to one integration, a sensor of another sits on it: that
    other integration's second sensor vouches for it, next to the owner's."""
    owner = MockConfigEntry(domain="test")
    owner.add_to_hass(hass)
    other = MockConfigEntry(domain="other")
    other.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=owner.entry_id,
        identifiers={("test", "station")},
        name="Station",
    )
    registry = er.async_get(hass)
    mapped = registry.async_get_or_create(
        "sensor", "other", "rain", device_id=device.id, config_entry=other
    )
    twin = registry.async_get_or_create(
        "sensor", "other", "wind", device_id=device.id, config_entry=other
    )
    station = registry.async_get_or_create(
        "sensor", "test", "temp", device_id=device.id, config_entry=owner
    )

    device_id, siblings = _entities_of_device(hass, mapped.entity_id)

    assert device_id == device.id
    assert sorted(siblings) == sorted([twin.entity_id, station.entity_id])


EVENT = f"{const.DOMAIN}_{const.EVENT_WEATHER_STALE}"
STALE = timedelta(seconds=const.SENSOR_STALE_AFTER_SECONDS)


class _FakeStore:
    def __init__(self, *mappings):
        self.mappings = {int(m[const.MAPPING_ID]): copy.deepcopy(m) for m in mappings}
        self.updates = []

    def get_mapping(self, mapping_id):
        mapping = self.mappings.get(int(mapping_id))
        return copy.deepcopy(mapping) if mapping else None

    async def async_get_mappings(self):
        return [copy.deepcopy(m) for m in self.mappings.values()]

    async def async_update_mapping(self, mapping_id, changes):
        self.updates.append((int(mapping_id), copy.deepcopy(changes)))
        self.mappings[int(mapping_id)].update(copy.deepcopy(changes))

    def set_mapping_sensor_last_seen(self, mapping_id, seen):
        self.mappings[int(mapping_id)][const.MAPPING_SENSOR_LAST_SEEN] = dict(seen)

    def set_mapping_buffer(self, mapping_id, readings):
        pass

    async def async_get_zones(self):
        return []

    async def async_update_zone(self, zone_id, changes):
        pass


class _FakeIssues:
    IssueSeverity = SimpleNamespace(WARNING="warning")

    def __init__(self):
        self.open = {}

    def async_create_issue(self, hass, domain, issue_id, **kwargs):
        self.open[issue_id] = kwargs

    def async_delete_issue(self, hass, domain, issue_id):
        self.open.pop(issue_id, None)


def _group(mapping_id=1, name="Garden", fields=None, outages=None, last_seen=None):
    return {
        const.MAPPING_ID: mapping_id,
        const.MAPPING_NAME: name,
        const.MAPPING_MAPPINGS: {
            field: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                const.MAPPING_CONF_SENSOR: entity,
            }
            for field, entity in (fields or {}).items()
        },
        const.MAPPING_SENSOR_OUTAGES: outages or [],
        const.MAPPING_SENSOR_LAST_SEEN: last_seen or {},
    }


def _coord(monkeypatch, groups, states, devices):
    """A coordinator over a fake store, fake states and a fake device map."""
    store = _FakeStore(*groups)
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.hass = Mock()
    coord.hass.states.get = Mock(side_effect=states.get)
    coord.hass.bus.async_fire = Mock()
    coord.store = store
    device_of = {e: d for d, entities in devices.items() for e in entities}

    def entities_of_device(hass, entity_id):
        device_id = device_of.get(entity_id)
        siblings = [e for e in devices.get(device_id, []) if e != entity_id]
        return device_id, siblings

    monkeypatch.setattr(sensor_liveness, "_entities_of_device", entities_of_device)
    issues = _FakeIssues()
    monkeypatch.setattr(sensor_liveness, "_issue_registry", lambda: issues)
    return coord, store, issues


def _events(coord):
    return [c.args for c in coord.hass.bus.async_fire.call_args_list]


class TestTheCheck:
    async def test_a_silent_station_opens_its_outages_fires_and_raises_the_notice(
        self, monkeypatch
    ):
        last = T0 - STALE - timedelta(seconds=1)
        coord, store, issues = _coord(
            monkeypatch,
            [_group(fields={"Temperature": "sensor.temp", "Windspeed": "sensor.wind"})],
            {
                "sensor.temp": _state("sensor.temp", "21.5", last),
                "sensor.wind": _state("sensor.wind", "2.0", last),
                "sensor.battery": _state("sensor.battery", "80", last),
            },
            {"dev1": ["sensor.temp", "sensor.wind", "sensor.battery"]},
        )

        await coord.async_check_sensor_liveness(now=T0)

        temp = Outage("sensor.temp", "dev1", ("Temperature",), last)
        wind = Outage("sensor.wind", "dev1", ("Windspeed",), last)
        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [
            temp.to_store(),
            wind.to_store(),
        ]
        assert [args[0] for args in _events(coord)] == [EVENT, EVENT]
        assert [args[1]["stale"] for args in _events(coord)] == [True, True]
        notice = issues.open["weather_sensor_stale_1"]
        assert notice["translation_key"] == const.ISSUE_WEATHER_SENSOR_STALE
        assert notice["is_fixable"] is False
        assert notice["translation_placeholders"]["entities"] == (
            "sensor.temp (Temperature), sensor.wind (Windspeed)"
        )

    async def test_a_steady_rain_gauge_on_a_living_station_stays_quiet(
        self, monkeypatch
    ):
        coord, store, issues = _coord(
            monkeypatch,
            [_group(fields={"Precipitation": "sensor.rain"})],
            {
                "sensor.rain": _state("sensor.rain", "0.0", T0 - timedelta(hours=10)),
                "sensor.temp": _state("sensor.temp", "14.2", T0 - timedelta(minutes=1)),
            },
            {"dev1": ["sensor.rain", "sensor.temp"]},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == []
        assert _events(coord) == []
        assert issues.open == {}

    async def test_the_return_closes_the_outage_at_the_first_report(self, monkeypatch):
        start = T0 - timedelta(hours=6)
        back = T0 - timedelta(minutes=4)
        open_ = Outage("sensor.temp", "dev1", ("Temperature",), start)
        coord, store, issues = _coord(
            monkeypatch,
            [
                _group(
                    fields={"Temperature": "sensor.temp"},
                    outages=[open_.to_store()],
                )
            ],
            {
                "sensor.temp": _state(
                    "sensor.temp", "18.0", T0 - timedelta(seconds=10), changed=back
                )
            },
            {"dev1": ["sensor.temp"]},
        )
        issues.open["weather_sensor_stale_1"] = {}

        await coord.async_check_sensor_liveness(now=T0)

        ended = Outage("sensor.temp", "dev1", ("Temperature",), start, back)
        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [ended.to_store()]
        assert _events(coord)[0][1]["stale"] is False
        assert _events(coord)[0][1]["until"] == dt_util.as_local(back).isoformat()
        assert issues.open == {}

    async def test_the_signs_of_life_ride_along_without_a_write(self, monkeypatch):
        coord, store, _ = _coord(
            monkeypatch,
            [_group(fields={"Temperature": "sensor.temp"})],
            {"sensor.temp": _state("sensor.temp", "18.0", T0 - timedelta(minutes=1))},
            {"dev1": ["sensor.temp"]},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert store.updates == []
        assert store.mappings[1][const.MAPPING_SENSOR_LAST_SEEN] == {
            "sensor.temp": (T0 - timedelta(minutes=1)).isoformat()
        }

    async def test_an_outage_spanning_a_restart_keeps_its_start(self, monkeypatch):
        before = T0 - timedelta(hours=5)
        coord, store, _ = _coord(
            monkeypatch,
            [
                _group(
                    fields={"Temperature": "sensor.temp"},
                    last_seen={"sensor.temp": before.isoformat()},
                )
            ],
            {
                # Restored as unavailable at the restart; its device's battery
                # entity reports again, which must not vouch for the dead one.
                "sensor.temp": _state(
                    "sensor.temp", "unavailable", T0 - timedelta(minutes=2)
                ),
                "sensor.battery": _state(
                    "sensor.battery", "80", T0 - timedelta(minutes=1)
                ),
            },
            {"dev1": ["sensor.temp", "sensor.battery"]},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [
            Outage("sensor.temp", "dev1", ("Temperature",), before).to_store()
        ]

    async def test_home_assistants_own_downtime_is_not_an_outage(self, monkeypatch):
        """Down for four hours, the station pushes again right after the start: its
        fresh report vouches for it before the first check, so nothing opens."""
        coord, store, issues = _coord(
            monkeypatch,
            [
                _group(
                    fields={"Temperature": "sensor.temp"},
                    last_seen={"sensor.temp": (T0 - timedelta(hours=4)).isoformat()},
                )
            ],
            {"sensor.temp": _state("sensor.temp", "16.0", T0 - timedelta(minutes=8))},
            {"dev1": ["sensor.temp"]},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == []
        assert _events(coord) == []
        assert issues.open == {}

    async def test_a_value_set_by_hand_never_goes_stale(self, monkeypatch):
        coord, store, issues = _coord(
            monkeypatch,
            [_group(fields={"Pressure": "input_number.pressure"})],
            {
                "input_number.pressure": _state(
                    "input_number.pressure", "1013", T0 - timedelta(days=30)
                )
            },
            {},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == []
        assert store.mappings[1][const.MAPPING_SENSOR_LAST_SEEN] == {}
        assert issues.open == {}

    async def test_an_entity_never_seen_starts_its_bridge_at_the_first_look(
        self, monkeypatch
    ):
        coord, store, _ = _coord(
            monkeypatch, [_group(fields={"Temperature": "sensor.ghost"})], {}, {}
        )

        await coord.async_check_sensor_liveness(now=T0)
        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == []
        assert store.mappings[1][const.MAPPING_SENSOR_LAST_SEEN] == {
            "sensor.ghost": T0.isoformat()
        }

        await coord.async_check_sensor_liveness(now=T0 + STALE + timedelta(seconds=1))
        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [
            Outage("sensor.ghost", None, ("Temperature",), T0).to_store()
        ]

    async def test_one_broken_group_does_not_stop_the_others(self, monkeypatch, caplog):
        last = T0 - STALE - timedelta(seconds=1)
        coord, store, _ = _coord(
            monkeypatch,
            [
                _group(1, "Broken", fields={"Temperature": "sensor.bad"}),
                _group(2, "Fine", fields={"Temperature": "sensor.t"}),
            ],
            {"sensor.t": _state("sensor.t", "18.0", last)},
            {},
        )
        real = sensor_liveness._entities_of_device

        def boom(hass, entity_id):
            if entity_id == "sensor.bad":
                raise RuntimeError("registry exploded")
            return real(hass, entity_id)

        monkeypatch.setattr(sensor_liveness, "_entities_of_device", boom)

        await coord.async_check_sensor_liveness(now=T0)

        assert len(store.mappings[2][const.MAPPING_SENSOR_OUTAGES]) == 1
        # The broken group is left as it was, and its failure is logged once.
        assert store.mappings[1][const.MAPPING_SENSOR_LAST_SEEN] == {}
        assert [mapping_id for mapping_id, _ in store.updates] == [2]
        failures = [r for r in caplog.records if r.levelname == "ERROR"]
        assert len(failures) == 1
        assert "sensor group 1" in failures[0].getMessage()

    async def test_an_open_outage_without_a_remembered_sign_stays_open(
        self, monkeypatch
    ):
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.temp", "dev1", ("Temperature",), start)
        coord, store, _ = _coord(
            monkeypatch,
            [_group(fields={"Temperature": "sensor.temp"}, outages=[open_.to_store()])],
            {},
            {},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [open_.to_store()]
        assert _events(coord) == []

    async def test_a_late_check_ends_the_old_outage_before_it_starts_the_new(
        self, monkeypatch
    ):
        start = T0 - timedelta(hours=10)
        newest = T0 - STALE - timedelta(hours=1)
        open_ = Outage("sensor.temp", "dev1", ("Temperature",), start)
        coord, _, _ = _coord(
            monkeypatch,
            [_group(fields={"Temperature": "sensor.temp"}, outages=[open_.to_store()])],
            {"sensor.temp": _state("sensor.temp", "18.0", newest)},
            {"dev1": ["sensor.temp"]},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert [args[1]["stale"] for args in _events(coord)] == [False, True]

    async def test_a_group_left_without_sensor_fields_ends_its_outage(
        self, monkeypatch
    ):
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.gone", "dev1", ("Temperature",), start)
        coord, store, issues = _coord(
            monkeypatch,
            [_group(fields={"Pressure": "input_number.p"}, outages=[open_.to_store()])],
            {},
            {},
        )
        issues.open["weather_sensor_stale_1"] = {}

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [
            Outage("sensor.gone", "dev1", ("Temperature",), start, T0).to_store()
        ]
        assert issues.open == {}


class TestAReplacedDevice:
    async def test_a_new_device_under_the_same_entity_ids_closes_the_outage(
        self, monkeypatch
    ):
        """The old station died; the new one took over its entity ids. The entity
        now belongs to the new device, which reports: the outage ends there."""
        start = T0 - timedelta(hours=6)
        back = T0 - timedelta(minutes=2)
        open_ = Outage("sensor.temp", "old-station", ("Temperature",), start)
        coord, store, issues = _coord(
            monkeypatch,
            [_group(fields={"Temperature": "sensor.temp"}, outages=[open_.to_store()])],
            {
                "sensor.temp": _state(
                    "sensor.temp", "17.0", T0 - timedelta(seconds=30), changed=back
                ),
                "sensor.wind": _state("sensor.wind", "1.0", T0 - timedelta(seconds=30)),
            },
            {"new-station": ["sensor.temp", "sensor.wind"]},
        )
        issues.open["weather_sensor_stale_1"] = {}

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [
            Outage(
                "sensor.temp", "old-station", ("Temperature",), start, back
            ).to_store()
        ]
        assert issues.open == {}

    async def test_an_entity_deleted_with_the_old_device_raises_the_notice(
        self, monkeypatch
    ):
        """The sensor group still names an entity that no longer exists: no data
        arrives, so after the limit the notice asks for the new entities."""
        coord, store, issues = _coord(
            monkeypatch,
            [
                _group(
                    fields={"Temperature": "sensor.gone"},
                    last_seen={
                        "sensor.gone": (T0 - STALE - timedelta(seconds=1)).isoformat()
                    },
                )
            ],
            {},
            {},
        )

        await coord.async_check_sensor_liveness(now=T0)

        assert len(store.mappings[1][const.MAPPING_SENSOR_OUTAGES]) == 1
        assert "weather_sensor_stale_1" in issues.open

    async def test_an_outage_left_by_another_path_ends_with_its_event(
        self, monkeypatch
    ):
        """The outage record still holds an outage for an entity the group no
        longer reads (its mapping changed without emptying the record): it ends
        now, with its end event, and the notice goes."""
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.gone", "dev1", ("Temperature",), start)
        coord, store, issues = _coord(
            monkeypatch,
            [_group(fields={"Temperature": "sensor.new"}, outages=[open_.to_store()])],
            {"sensor.new": _state("sensor.new", "16.0", T0 - timedelta(minutes=1))},
            {"dev2": ["sensor.new"]},
        )
        issues.open["weather_sensor_stale_1"] = {}

        await coord.async_check_sensor_liveness(now=T0)

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [
            Outage("sensor.gone", "dev1", ("Temperature",), start, T0).to_store()
        ]
        assert [(a[1]["entity_id"], a[1]["stale"]) for a in _events(coord)] == [
            ("sensor.gone", False)
        ]
        assert issues.open == {}


class TestTimer:
    async def test_setup_shows_a_still_open_outage_at_once(self, monkeypatch):
        open_ = Outage("sensor.temp", "dev1", ("Temperature",), T0 - timedelta(hours=5))
        coord, _, issues = _coord(
            monkeypatch,
            [_group(fields={"Temperature": "sensor.temp"}, outages=[open_.to_store()])],
            {},
            {},
        )
        unsub = Mock()
        monkeypatch.setattr(
            sensor_liveness, "async_track_time_interval", Mock(return_value=unsub)
        )

        await coord.async_setup_sensor_liveness()

        assert "weather_sensor_stale_1" in issues.open
        assert coord._sensor_liveness_unsub is unsub

    async def test_the_check_waits_out_the_startup_grace(self, monkeypatch):
        coord, _, _ = _coord(monkeypatch, [], {}, {})
        coord.async_check_sensor_liveness = AsyncMock()
        coord._sensor_liveness_armed_at = T0
        clock = {"now": T0 - timedelta(seconds=1)}
        monkeypatch.setattr(sensor_liveness, "local_naive_now", lambda: clock["now"])

        await coord._async_sensor_liveness_tick()
        coord.async_check_sensor_liveness.assert_not_awaited()

        clock["now"] = T0
        await coord._async_sensor_liveness_tick()
        coord.async_check_sensor_liveness.assert_awaited_once()

    def test_teardown_cancels_the_timer(self, monkeypatch):
        coord, _, _ = _coord(monkeypatch, [], {}, {})
        unsub = Mock()
        coord._sensor_liveness_unsub = unsub

        coord.async_teardown_sensor_liveness()

        unsub.assert_called_once()
        assert coord._sensor_liveness_unsub is None

    async def test_one_broken_group_does_not_stop_the_setup(self, monkeypatch):
        open_ = Outage("sensor.temp", "dev1", ("Temperature",), T0 - timedelta(hours=5))
        coord, _, issues = _coord(
            monkeypatch,
            [
                _group(1, "Broken", outages=[open_.to_store()]),
                _group(2, "Fine", outages=[open_.to_store()]),
            ],
            {},
            {},
        )
        real = coord._sync_stale_issue

        def boom(mapping_id, name, outages):
            if mapping_id == 1:
                raise RuntimeError("issue registry exploded")
            real(mapping_id, name, outages)

        coord._sync_stale_issue = boom
        unsub = Mock()
        monkeypatch.setattr(
            sensor_liveness, "async_track_time_interval", Mock(return_value=unsub)
        )

        await coord.async_setup_sensor_liveness()

        assert "weather_sensor_stale_2" in issues.open
        assert coord._sensor_liveness_unsub is unsub

    async def test_the_timer_runs_the_tick_and_the_tick_waits_out_the_grace(
        self, monkeypatch
    ):
        coord, _, _ = _coord(monkeypatch, [], {}, {})
        track = Mock(return_value=Mock())
        monkeypatch.setattr(sensor_liveness, "async_track_time_interval", track)
        clock = {"now": T0}
        monkeypatch.setattr(sensor_liveness, "local_naive_now", lambda: clock["now"])

        await coord.async_setup_sensor_liveness()

        hass, action, interval = track.call_args.args
        assert hass is coord.hass
        assert interval == timedelta(seconds=const.SENSOR_LIVENESS_INTERVAL_SECONDS)
        coord.async_check_sensor_liveness = AsyncMock()
        grace = timedelta(seconds=const.SENSOR_LIVENESS_STARTUP_GRACE_SECONDS)

        # Home Assistant calls the action with its own, aware UTC time. The check
        # works on the outage record's naive clock, so that time must not reach it.
        clock["now"] = T0 + grace - timedelta(seconds=1)
        await action(dt_util.utcnow())
        coord.async_check_sensor_liveness.assert_not_awaited()

        clock["now"] = T0 + grace
        await action(dt_util.utcnow())
        coord.async_check_sensor_liveness.assert_awaited_once_with()

    async def test_a_second_setup_cancels_the_first_timer(self, monkeypatch):
        coord, _, _ = _coord(monkeypatch, [], {}, {})
        first, second = Mock(), Mock()
        monkeypatch.setattr(
            sensor_liveness,
            "async_track_time_interval",
            Mock(side_effect=[first, second]),
        )

        await coord.async_setup_sensor_liveness()
        await coord.async_setup_sensor_liveness()

        first.assert_called_once()
        second.assert_not_called()
        assert coord._sensor_liveness_unsub is second


INIT = (
    pathlib.Path(__file__).parent.parent
    / "custom_components"
    / "irrigation_plus"
    / "__init__.py"
)


def _own_statements_of(function_name):
    """``(name, awaited)`` of each ``self.<name>(...)`` that is a statement of the
    function's own body: not inside an ``if``, a loop, a ``try`` or a nested def."""
    tree = ast.parse(INIT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            found = set()
            for statement in node.body:
                if not isinstance(statement, ast.Expr):
                    continue
                call, awaited = statement.value, False
                if isinstance(call, ast.Await):
                    call, awaited = call.value, True
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == "self"
                ):
                    found.add((call.func.attr, awaited))
            return found
    raise AssertionError(f"{function_name} not found in __init__.py")


def test_setup_arms_the_check_and_unload_disarms_it():
    assert ("async_setup_sensor_liveness", True) in _own_statements_of(
        "async_setup_timers"
    )
    assert ("async_teardown_sensor_liveness", False) in _own_statements_of(
        "async_unload"
    )


OPEN_RECORD = Outage(
    "sensor.old", "dev1", ("Temperature",), T0 - timedelta(hours=5)
).to_store()


CLOSED_RECORD = Outage(
    "sensor.old",
    "dev1",
    ("Temperature",),
    T0 - timedelta(days=2),
    T0 - timedelta(days=1),
).to_store()


def _mock_store_coord(monkeypatch, mapping):
    """The harness of tests/test_mapping_source_change.py: a Mock store."""
    store = Mock()
    store.get_mapping = Mock(return_value=mapping)
    store.async_update_mapping = AsyncMock()
    store.async_update_zone = AsyncMock()
    store.async_delete_mapping = AsyncMock(return_value=True)
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.store = store
    coord.hass = Mock()
    coord._get_zones_that_use_this_mapping = AsyncMock(return_value=[])
    issues = _FakeIssues()
    issues.open["weather_sensor_stale_0"] = {}
    monkeypatch.setattr(sensor_liveness, "_issue_registry", lambda: issues)
    return coord, store, issues


def _sensor_group_zero(entity):
    group = _group(
        0,
        fields={"Temperature": entity},
        outages=[OPEN_RECORD],
        last_seen={"sensor.old": T0.isoformat()},
    )
    group[const.MAPPING_DATA_LAST_ENTRY] = {}
    return group


class TestTheOutageRecordFollowsTheConfiguration:
    async def test_a_source_change_empties_the_record_and_drops_the_notice(
        self, monkeypatch
    ):
        coord, store, issues = _mock_store_coord(
            monkeypatch, _sensor_group_zero("sensor.old")
        )
        new = {
            const.MAPPING_MAPPINGS: {
                "Temperature": {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.new",
                }
            }
        }
        with patch("custom_components.irrigation_plus.async_dispatcher_send"):
            await coord.async_update_mapping_config(0, new)

        args, _ = store.async_update_mapping.call_args
        assert args[1][const.MAPPING_SENSOR_OUTAGES] == []
        assert const.MAPPING_SENSOR_LAST_SEEN not in args[1]
        assert "weather_sensor_stale_0" not in issues.open
        # The replaced sensor's outage still ends, so an automation hears it.
        fired = [c.args for c in coord.hass.bus.async_fire.call_args_list]
        assert [(a[0], a[1]["entity_id"], a[1]["stale"]) for a in fired] == [
            (EVENT, "sensor.old", False)
        ]
        assert fired[0][1]["until"] is not None

    async def test_a_group_without_an_open_outage_leaves_the_registry_alone(
        self, monkeypatch
    ):
        """No open outage, no notice to clear: the issue registry is not asked."""
        group = _sensor_group_zero("sensor.old")
        group[const.MAPPING_SENSOR_OUTAGES] = []
        coord, _, _ = _mock_store_coord(monkeypatch, group)
        monkeypatch.setattr(
            sensor_liveness,
            "_issue_registry",
            Mock(side_effect=AssertionError("issue registry asked")),
        )
        new = {
            const.MAPPING_MAPPINGS: {
                "Temperature": {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.new",
                }
            }
        }
        with patch("custom_components.irrigation_plus.async_dispatcher_send"):
            await coord.async_update_mapping_config(0, new)
        await coord.async_update_mapping_config(0, {const.ATTR_REMOVE: True})
        coord.hass.bus.async_fire.assert_not_called()

    async def test_a_rename_keeps_the_record_and_the_notice(self, monkeypatch):
        coord, store, issues = _mock_store_coord(
            monkeypatch, _sensor_group_zero("sensor.old")
        )
        with patch("custom_components.irrigation_plus.async_dispatcher_send"):
            await coord.async_update_mapping_config(0, {const.MAPPING_NAME: "renamed"})

        args, _ = store.async_update_mapping.call_args
        assert const.MAPPING_SENSOR_OUTAGES not in args[1]
        assert "weather_sensor_stale_0" in issues.open

    async def test_deleting_a_group_drops_its_notice(self, monkeypatch):
        coord, store, issues = _mock_store_coord(
            monkeypatch, _sensor_group_zero("sensor.old")
        )
        await coord.async_update_mapping_config(0, {const.ATTR_REMOVE: True})

        store.async_delete_mapping.assert_awaited_once()
        assert "weather_sensor_stale_0" not in issues.open
        fired = [c.args for c in coord.hass.bus.async_fire.call_args_list]
        assert [(a[0], a[1]["stale"]) for a in fired] == [(EVENT, False)]

    async def test_reset_all_weather_data_empties_the_record(self, monkeypatch):
        other = Outage(
            "sensor.other", None, ("Temperature",), T0 - timedelta(hours=4)
        ).to_store()
        coord, store, issues = _coord(
            monkeypatch,
            [
                _group(
                    fields={"Temperature": "sensor.old"},
                    outages=[OPEN_RECORD],
                    last_seen={"sensor.old": T0.isoformat()},
                ),
                _group(
                    2,
                    "Orchard",
                    fields={"Temperature": "sensor.other"},
                    outages=[other],
                ),
            ],
            {},
            {},
        )
        issues.open["weather_sensor_stale_1"] = {}
        issues.open["weather_sensor_stale_2"] = {}
        coord.clear_continuous_deadband_state = Mock()
        coord.invalidate_live_estimate_carry = Mock()
        monkeypatch.setattr(
            "custom_components.irrigation_plus.calculation.async_dispatcher_send",
            Mock(),
        )

        await coord._async_clear_all_weatherdata()

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == []
        assert store.mappings[2][const.MAPPING_SENSOR_OUTAGES] == []
        assert store.mappings[1][const.MAPPING_SENSOR_LAST_SEEN] == {
            "sensor.old": T0.isoformat()
        }
        assert issues.open == {}
        assert [(a[1]["entity_id"], a[1]["stale"]) for a in _events(coord)] == [
            ("sensor.old", False),
            ("sensor.other", False),
        ]

    async def test_a_sensor_still_silent_after_a_reset_is_reported_again(
        self, monkeypatch
    ):
        """The reset empties the outage record, not the signs of life: the next
        check opens the outage again, from the silence's real start."""
        start = T0 - timedelta(hours=5)
        open_ = Outage("sensor.old", "dev1", ("Temperature",), start)
        coord, store, issues = _coord(
            monkeypatch,
            [
                _group(
                    fields={"Temperature": "sensor.old"},
                    outages=[open_.to_store()],
                    last_seen={"sensor.old": start.isoformat()},
                )
            ],
            {"sensor.old": _state("sensor.old", "unavailable", start)},
            {"dev1": ["sensor.old"]},
        )
        coord.clear_continuous_deadband_state = Mock()
        coord.invalidate_live_estimate_carry = Mock()
        monkeypatch.setattr(
            "custom_components.irrigation_plus.calculation.async_dispatcher_send",
            Mock(),
        )

        await coord._async_clear_all_weatherdata()
        await coord.async_check_sensor_liveness(now=T0 + timedelta(minutes=5))

        assert store.mappings[1][const.MAPPING_SENSOR_OUTAGES] == [open_.to_store()]
        assert "weather_sensor_stale_1" in issues.open
        assert [(a[1]["entity_id"], a[1]["stale"]) for a in _events(coord)] == [
            ("sensor.old", False),
            ("sensor.old", True),
        ]

    async def test_only_open_outages_are_ended(self, monkeypatch):
        group = _sensor_group_zero("sensor.old")
        group[const.MAPPING_SENSOR_OUTAGES] = [CLOSED_RECORD, OPEN_RECORD]
        coord, _, _ = _mock_store_coord(monkeypatch, group)

        await coord.async_update_mapping_config(0, {const.ATTR_REMOVE: True})

        fired = [c.args[1] for c in coord.hass.bus.async_fire.call_args_list]
        assert [(p["since"], p["stale"]) for p in fired] == [
            (dt_util.as_local(T0 - timedelta(hours=5)).isoformat(), False)
        ]

    async def test_closed_outages_alone_end_nothing(self, monkeypatch):
        group = _sensor_group_zero("sensor.old")
        group[const.MAPPING_SENSOR_OUTAGES] = [CLOSED_RECORD]
        coord, _, _ = _mock_store_coord(monkeypatch, group)
        monkeypatch.setattr(
            sensor_liveness,
            "_issue_registry",
            Mock(side_effect=AssertionError("issue registry asked")),
        )

        await coord.async_update_mapping_config(0, {const.ATTR_REMOVE: True})

        coord.hass.bus.async_fire.assert_not_called()
