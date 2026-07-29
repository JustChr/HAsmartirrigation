"""Event-driven sensor ingestion (ContinuousUpdateMixin).

Mirrors tests/test_observed_watering.py: the state-change tracker is stubbed so
the subscription-building logic can be exercised against a Mock hass without
standing up HA core.
"""

import copy
import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.continuous_update import (
    CONTINUOUS_PRUNE_EVERY,
    SENSOR_DEADBAND,
)


@pytest.fixture(autouse=True)
def _stub_hass_helpers(monkeypatch):
    # async_track_state_change_event / async_call_later are real HA helpers that
    # need a live hass.data + event loop; stub both to no-ops returning Mock
    # unsubs so these unit tests exercise only the code under test.
    monkeypatch.setattr(
        "custom_components.smart_irrigation.continuous_update."
        "async_track_state_change_event",
        Mock(return_value=Mock()),
    )
    monkeypatch.setattr(
        "custom_components.smart_irrigation.continuous_update.async_call_later",
        Mock(side_effect=lambda *_args, **_kw: Mock()),
    )
    # The real dispatcher walks hass.data; these tests use a Mock hass.
    monkeypatch.setattr(
        "custom_components.smart_irrigation.continuous_update.async_dispatcher_send",
        Mock(),
    )
    monkeypatch.setattr(
        "custom_components.smart_irrigation.async_dispatcher_send", Mock()
    )


class _FakeStore:
    """Minimal stand-in for SmartIrrigationStorage's mapping/zone API.

    get_mapping deep-copies, exactly like the real ``attr.asdict`` return: the
    append path is only correct because it writes the buffer back rather than
    mutating what it read, and a shallow fake would hide that.
    """

    def __init__(self, mappings, *, enabled=True, debounce=5000):
        self.mappings = {int(m[const.MAPPING_ID]): m for m in mappings}
        self.config = SimpleNamespace(
            continuousupdates=enabled, sensor_debounce=debounce
        )
        self.zone_updates = []

    def get_mapping(self, mapping_id):
        mapping = self.mappings.get(int(mapping_id))
        return copy.deepcopy(mapping) if mapping else None

    async def async_get_mappings(self):
        return [copy.deepcopy(m) for m in self.mappings.values()]

    async def async_update_mapping(self, mapping_id, changes):
        stored = self.mappings[int(mapping_id)]
        # Mirror the real store's key-by-key carry-forward merge (store.py).
        old_last = stored.get(const.MAPPING_DATA_LAST_ENTRY) or {}
        if old_last:
            merged = dict(changes.get(const.MAPPING_DATA_LAST_ENTRY) or {})
            for key, val in old_last.items():
                merged.setdefault(key, val)
            changes = {**changes, const.MAPPING_DATA_LAST_ENTRY: merged}
        stored.update(changes)
        return stored

    async def async_update_zone(self, zone_id, changes):
        self.zone_updates.append((zone_id, changes))


def _mapping(mapping_id=1, mappings=None, data=None, last_entry=None):
    return {
        const.MAPPING_ID: mapping_id,
        const.MAPPING_NAME: f"group {mapping_id}",
        const.MAPPING_MAPPINGS: (
            mappings
            if mappings is not None
            else {
                const.MAPPING_TEMPERATURE: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.temp",
                }
            }
        ),
        const.MAPPING_DATA: [] if data is None else data,
        const.MAPPING_DATA_LAST_ENTRY: {} if last_entry is None else last_entry,
    }


def _coord(store):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.hass = Mock()
    coord.hass.config.units = METRIC_SYSTEM
    coord.store = store
    coord._continuous_unsub = None
    coord._continuous_entities = frozenset()
    coord._continuous_targets = {}
    coord._continuous_debounce_unsub = {}
    coord._continuous_last_value = {}
    coord._continuous_flush_count = {}
    # Capture the coroutines the @callback handler hands to the loop so the test
    # can await them deterministically.
    coord.created_tasks = []
    coord.hass.async_create_task = Mock(side_effect=coord.created_tasks.append)
    return coord


async def _drain(coord):
    """Await every coroutine the handler scheduled, in creation order.

    The list is cleared in place, not rebound: the Mock's side_effect holds a
    reference to this exact list object.
    """
    tasks = list(coord.created_tasks)
    coord.created_tasks.clear()
    for coro in tasks:
        await coro


def _event(entity_id, state, attributes=None):
    return SimpleNamespace(
        data={
            "entity_id": entity_id,
            "new_state": SimpleNamespace(state=state, attributes=attributes or {}),
        }
    )


class TestSetup:
    async def test_targets_built_from_sensor_sourced_fields(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        assert list(coord._continuous_targets) == ["sensor.temp"]
        mapping_id, key, _cfg = coord._continuous_targets["sensor.temp"][0]
        assert (mapping_id, key) == (1, const.MAPPING_TEMPERATURE)
        assert coord._continuous_unsub is not None

    async def test_nothing_tracked_when_feature_off(self):
        store = _FakeStore([_mapping()], enabled=False)
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        assert coord._continuous_targets == {}
        assert coord._continuous_unsub is None

    async def test_non_sensor_sources_and_blank_entities_are_skipped(self):
        store = _FakeStore(
            [
                _mapping(
                    mappings={
                        const.MAPPING_TEMPERATURE: {
                            const.MAPPING_CONF_SOURCE: (
                                const.MAPPING_CONF_SOURCE_WEATHER_SERVICE
                            ),
                        },
                        const.MAPPING_HUMIDITY: {
                            const.MAPPING_CONF_SOURCE: (
                                const.MAPPING_CONF_SOURCE_STATIC_VALUE
                            ),
                            const.MAPPING_CONF_STATIC_VALUE: 50,
                        },
                        # Sensor source but no entity chosen yet.
                        const.MAPPING_PRESSURE: {
                            const.MAPPING_CONF_SOURCE: (
                                const.MAPPING_CONF_SOURCE_SENSOR
                            ),
                            const.MAPPING_CONF_SENSOR: "",
                        },
                        # Legacy stored shape: a bare string, not a config dict.
                        const.MAPPING_WINDSPEED: "sensor.legacy",
                    }
                )
            ]
        )
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        assert coord._continuous_targets == {}

    async def test_one_entity_can_feed_several_groups(self):
        shared = {
            const.MAPPING_TEMPERATURE: {
                const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                const.MAPPING_CONF_SENSOR: "sensor.temp",
            }
        }
        store = _FakeStore(
            [_mapping(1, mappings=shared), _mapping(2, mappings=copy.deepcopy(shared))]
        )
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        assert {t[0] for t in coord._continuous_targets["sensor.temp"]} == {1, 2}

    async def test_unchanged_entity_set_does_not_resubscribe(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        first = coord._continuous_unsub
        await coord.async_setup_continuous_updates()
        assert coord._continuous_unsub is first

    async def test_teardown_cancels_subscription_and_debounce_timers(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        unsub = coord._continuous_unsub
        pending = Mock()
        coord._continuous_debounce_unsub[1] = pending
        coord.async_teardown_continuous_updates()
        unsub.assert_called_once()
        pending.assert_called_once()
        assert coord._continuous_unsub is None
        assert coord._continuous_debounce_unsub == {}


class TestStateChanged:
    async def test_appends_sparse_row_and_updates_last_entry(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(_event("sensor.temp", "21.5"))
        await _drain(coord)

        rows = store.mappings[1][const.MAPPING_DATA]
        assert len(rows) == 1
        # Sparse: exactly the changed key plus the timestamp, nothing else.
        assert set(rows[0]) == {const.MAPPING_TEMPERATURE, const.RETRIEVED_AT}
        assert rows[0][const.MAPPING_TEMPERATURE] == 21.5
        assert isinstance(rows[0][const.RETRIEVED_AT], datetime.datetime)
        # Naive local, like the poll path — aggregate_window compares it against
        # a naive watermark and would raise on an aware value.
        assert rows[0][const.RETRIEVED_AT].tzinfo is None
        assert store.mappings[1][const.MAPPING_DATA_LAST_ENTRY] == {
            const.MAPPING_TEMPERATURE: 21.5
        }

    async def test_consecutive_changes_both_land_in_the_buffer(self):
        # Regression guard: reading the buffer in the callback and writing it back
        # from the task would make the second write clobber the first row.
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(_event("sensor.temp", "10"))
        coord._sensor_state_changed(_event("sensor.temp", "30"))
        await _drain(coord)
        assert [
            r[const.MAPPING_TEMPERATURE] for r in store.mappings[1][const.MAPPING_DATA]
        ] == [
            10.0,
            30.0,
        ]

    @pytest.mark.parametrize("state", [STATE_UNKNOWN, STATE_UNAVAILABLE, None, "abc"])
    async def test_non_numeric_states_are_ignored(self, state):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(_event("sensor.temp", state))
        await _drain(coord)
        assert store.mappings[1][const.MAPPING_DATA] == []

    async def test_untracked_entity_is_ignored(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(_event("sensor.something_else", "5"))
        await _drain(coord)
        assert store.mappings[1][const.MAPPING_DATA] == []

    async def test_value_is_converted_using_the_entity_reported_unit(self):
        # Configured °C but the entity says °F: HA's unit wins, so the stored
        # value must be metric (68 °F -> 20 °C), not 68.
        store = _FakeStore(
            [
                _mapping(
                    mappings={
                        const.MAPPING_TEMPERATURE: {
                            const.MAPPING_CONF_SOURCE: (
                                const.MAPPING_CONF_SOURCE_SENSOR
                            ),
                            const.MAPPING_CONF_SENSOR: "sensor.temp",
                            const.MAPPING_CONF_UNIT: "°C",
                        }
                    }
                )
            ]
        )
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(
            _event("sensor.temp", "68", {"unit_of_measurement": "°F"})
        )
        await _drain(coord)
        stored = store.mappings[1][const.MAPPING_DATA][0][const.MAPPING_TEMPERATURE]
        assert stored == pytest.approx(20.0, abs=0.01)


class TestDeadband:
    async def test_small_move_is_dropped_and_large_move_is_kept(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        step = SENSOR_DEADBAND[const.MAPPING_TEMPERATURE]

        coord._sensor_state_changed(_event("sensor.temp", "20.0"))
        await _drain(coord)
        # Below the threshold: jitter, not information.
        coord._sensor_state_changed(_event("sensor.temp", str(20.0 + step / 2)))
        await _drain(coord)
        assert len(store.mappings[1][const.MAPPING_DATA]) == 1
        # Above the threshold: recorded.
        coord._sensor_state_changed(_event("sensor.temp", str(20.0 + step * 2)))
        await _drain(coord)
        assert len(store.mappings[1][const.MAPPING_DATA]) == 2

    async def test_reference_is_the_last_appended_value_so_drift_still_lands(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        step = SENSOR_DEADBAND[const.MAPPING_TEMPERATURE]
        # A slow monotonic climb in sub-threshold steps must eventually be
        # recorded — comparing against the last SEEN value would suppress it
        # forever and lose a whole day's temperature rise.
        for i in range(1, 6):
            coord._sensor_state_changed(
                _event("sensor.temp", str(20.0 + i * step * 0.6))
            )
            await _drain(coord)
        assert len(store.mappings[1][const.MAPPING_DATA]) > 1

    async def test_precipitation_is_never_deadbanded(self):
        store = _FakeStore(
            [
                _mapping(
                    mappings={
                        const.MAPPING_PRECIPITATION: {
                            const.MAPPING_CONF_SOURCE: (
                                const.MAPPING_CONF_SOURCE_SENSOR
                            ),
                            const.MAPPING_CONF_SENSOR: "sensor.rain",
                        }
                    }
                )
            ]
        )
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        # A drizzle ticking a cumulative gauge in 0.1 mm steps: dropping these
        # would under-report rain, and under-reported rain OVER-waters.
        for value in ("0.1", "0.2", "0.3"):
            coord._sensor_state_changed(_event("sensor.rain", value))
            await _drain(coord)
        assert len(store.mappings[1][const.MAPPING_DATA]) == 3


class TestDebounce:
    async def test_burst_reschedules_one_timer_per_sensor_group(self, monkeypatch):
        cancels = []

        def _fake_call_later(_hass, _delay, _action):
            unsub = Mock()
            cancels.append(unsub)
            return unsub

        monkeypatch.setattr(
            "custom_components.smart_irrigation.continuous_update.async_call_later",
            _fake_call_later,
        )
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()

        coord._sensor_state_changed(_event("sensor.temp", "10"))
        coord._sensor_state_changed(_event("sensor.temp", "30"))
        coord._sensor_state_changed(_event("sensor.temp", "50"))
        # One live timer for the group, and each earlier one cancelled.
        assert len(cancels) == 3
        assert [c.called for c in cancels] == [True, True, False]
        assert set(coord._continuous_debounce_unsub) == {1}
        for coro in coord.created_tasks:
            coro.close()  # the appends aren't under test here
        coord.created_tasks.clear()

    async def test_zero_debounce_flushes_immediately(self, monkeypatch):
        called = Mock()
        monkeypatch.setattr(
            "custom_components.smart_irrigation.continuous_update.async_call_later",
            called,
        )
        store = _FakeStore([_mapping()], debounce=0)
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(_event("sensor.temp", "10"))
        called.assert_not_called()
        # The append task plus the flush task, in that order.
        assert len(coord.created_tasks) == 2
        for coro in coord.created_tasks:
            coro.close()  # never scheduled here; closing avoids a warning
        coord.created_tasks.clear()

    async def test_debounce_falls_back_to_default_on_a_bad_value(self):
        store = _FakeStore([_mapping()], debounce="not a number")
        coord = _coord(store)
        assert coord._continuous_debounce_ms() == const.CONF_DEFAULT_SENSOR_DEBOUNCE


class TestFlush:
    async def test_flush_publishes_zone_bookkeeping_and_prunes_every_nth(self):
        store = _FakeStore([_mapping(data=[{const.MAPPING_TEMPERATURE: 1}] * 3)])
        coord = _coord(store)
        coord._get_zones_that_use_this_mapping = AsyncMock(return_value=[7])
        coord._prune_mapping_buffer = AsyncMock()
        coord._continuous_enforce_row_cap = AsyncMock()

        for _ in range(CONTINUOUS_PRUNE_EVERY - 1):
            await coord._async_continuous_update_for_mapping(1)
        coord._prune_mapping_buffer.assert_not_called()
        # Pruning writes, so it runs once per N flushes, not per reading.
        await coord._async_continuous_update_for_mapping(1)
        coord._prune_mapping_buffer.assert_called_once()
        coord._continuous_enforce_row_cap.assert_called_once()

        zone_id, changes = store.zone_updates[0]
        assert zone_id == 7
        # Same count convention as the poll path: the oldest row is the
        # carried-forward boundary, not a new reading.
        assert changes[const.ZONE_NUMBER_OF_DATA_POINTS] == 2

    async def test_flush_on_a_deleted_sensor_group_is_a_no_op(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        coord._get_zones_that_use_this_mapping = AsyncMock(return_value=[])
        await coord._async_continuous_update_for_mapping(99)
        assert store.zone_updates == []

    async def test_row_cap_keeps_the_boundary_row(self, monkeypatch):
        # The cap is a last-resort memory bound layered ON TOP of the watermark
        # prune; the oldest surviving row must stay as the DELTA/RIEMANNSUM
        # baseline select_window expects.
        monkeypatch.setattr(
            "custom_components.smart_irrigation.continuous_update."
            "CONTINUOUS_MAX_BUFFER_ROWS",
            5,
        )
        rows = [{const.MAPPING_TEMPERATURE: i} for i in range(20)]
        store = _FakeStore([_mapping(data=rows)])
        coord = _coord(store)
        await coord._continuous_enforce_row_cap(1)
        kept = store.mappings[1][const.MAPPING_DATA]
        assert len(kept) == 6  # the cap plus the re-inserted boundary
        assert kept[0][const.MAPPING_TEMPERATURE] == 0
        assert kept[-1][const.MAPPING_TEMPERATURE] == 19

    async def test_row_cap_leaves_a_buffer_under_the_cap_alone(self):
        rows = [{const.MAPPING_TEMPERATURE: i} for i in range(10)]
        store = _FakeStore([_mapping(data=rows)])
        coord = _coord(store)
        await coord._continuous_enforce_row_cap(1)
        assert len(store.mappings[1][const.MAPPING_DATA]) == 10


class TestClearWeatherData:
    async def test_clear_all_also_neutralises_carry_forwards(self):
        """ "Reset all weather data" must not leave a backfill behind.

        aggregate_window falls back to MAPPING_DATA_LAST_ENTRY, so leaving it
        populated would make the reset look like it did nothing for a
        continuous-update sensor group.
        """
        store = _FakeStore(
            [
                _mapping(
                    data=[{const.MAPPING_TEMPERATURE: 5}], last_entry={"Humidity": 42}
                )
            ]
        )
        coord = _coord(store)
        coord.store.async_get_zones = AsyncMock(return_value=[])
        await coord._async_clear_all_weatherdata()
        assert store.mappings[1][const.MAPPING_DATA] == []
        assert store.mappings[1][const.MAPPING_DATA_LAST_ENTRY] == {"Humidity": None}


class TestIntervalPollSkip:
    """Step 3 of the port: the event path IS the data path for sensor groups."""

    def _poll_coord(self, *, continuous, owm_in_mapping):
        coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
        coord.hass = Mock()
        coord.hass.config.units = METRIC_SYSTEM
        coord.store = Mock()
        coord.store.config = SimpleNamespace(continuousupdates=continuous)
        coord.store.async_get_zones = AsyncMock(
            return_value=[
                {const.ZONE_ID: 1, const.ZONE_MAPPING: 1, const.ZONE_STATE: "automatic"}
            ]
        )
        coord.store.async_update_mapping = AsyncMock()
        coord.store.async_update_zone = AsyncMock()
        coord.store.get_mapping = Mock(return_value=_mapping())
        coord.check_mapping_sources = Mock(return_value=(owm_in_mapping, True, False))
        coord.build_sensor_values_for_mapping = Mock(
            return_value={const.MAPPING_TEMPERATURE: 20.0}
        )
        coord.merge_weatherdata_and_sensor_values = AsyncMock(
            side_effect=lambda wd, sv: {**(wd or {}), **(sv or {})}
        )
        coord._get_zones_that_use_this_mapping = AsyncMock(return_value=[1])
        coord.async_refresh_zone_estimates = AsyncMock()
        coord.use_weather_service = False
        return coord

    async def test_pure_sensor_group_is_skipped_when_continuous(self):
        coord = self._poll_coord(continuous=True, owm_in_mapping=False)
        await coord._async_update_all()
        coord.store.async_update_mapping.assert_not_called()

    async def test_weather_service_group_still_polls_when_continuous(self):
        # Weather-service data only arrives by API call; the event path never
        # fetches it, so this group must keep its scheduled poll.
        coord = self._poll_coord(continuous=True, owm_in_mapping=True)
        await coord._async_update_all()
        coord.store.async_update_mapping.assert_called_once()

    async def test_pure_sensor_group_still_polls_when_feature_off(self):
        coord = self._poll_coord(continuous=False, owm_in_mapping=False)
        await coord._async_update_all()
        coord.store.async_update_mapping.assert_called_once()
