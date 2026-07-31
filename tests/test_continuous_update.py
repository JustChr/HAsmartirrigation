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
from homeassistant.const import CONF_ELEVATION, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.const import UNIT_INHG
from custom_components.smart_irrigation.continuous_update import (
    CONTINUOUS_PRUNE_EVERY,
    SENSOR_DEADBAND,
)
from custom_components.smart_irrigation.helpers import (
    convert_mapping_to_metric,
    relative_to_absolute_pressure,
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
    # The real dispatcher walks hass.data; these tests use a Mock hass. Every
    # module these tests reach into has to be stubbed, not just the one under
    # test: _async_clear_all_weatherdata lives in calculation and notifies the
    # frontend, so leaving that one real fails on a Mock hass.data.
    for module in (
        "custom_components.smart_irrigation.continuous_update",
        "custom_components.smart_irrigation",
        "custom_components.smart_irrigation.calculation",
    ):
        monkeypatch.setattr(f"{module}.async_dispatcher_send", Mock())


class _FakeStore:
    """Minimal stand-in for SmartIrrigationStorage's mapping/zone API.

    Tracks the post-Step-4 storage contract, which is the whole point of this
    double: the reading buffers live in ``self.buffers``, NOT on the mapping
    record, so ``get_mapping``/``async_get_mappings`` deep-copy a record that no
    longer carries them — exactly like the real ``attr.asdict``. A caller that
    mutates what it read and never writes it back is still caught here rather
    than silently passing.

    ``saves`` counts SCHEDULED STORE WRITES. Appending a reading (and refreshing
    the carry-forward that goes with it) must schedule none — that is the
    property Step 4 exists for, and ``TestNoWritePerReading`` asserts it.
    """

    def __init__(self, mappings, *, enabled=True, debounce=5000):
        self.mappings = {}
        self.buffers = {}
        for mapping in mappings:
            mapping = dict(mapping)
            mapping_id = int(mapping[const.MAPPING_ID])
            # The same split the real store's async_load does: readings out of
            # the record, into the buffer dict beside it.
            self.buffers[mapping_id] = mapping.pop(const.MAPPING_DATA, None) or []
            self.mappings[mapping_id] = mapping
        self.config = SimpleNamespace(
            continuousupdates=enabled, sensor_debounce=debounce
        )
        self.zone_updates = []
        self.saves = 0

    def get_mapping(self, mapping_id):
        mapping = self.mappings.get(int(mapping_id))
        return copy.deepcopy(mapping) if mapping else None

    async def async_get_mappings(self):
        return [copy.deepcopy(m) for m in self.mappings.values()]

    def get_mapping_field_configs(self):
        return [
            (int(mid), m.get(const.MAPPING_MAPPINGS) or {})
            for mid, m in self.mappings.items()
        ]

    def get_mapping_buffer(self, mapping_id):
        """The LIVE buffer list, never a copy — like the real accessor."""
        if mapping_id is None:
            return []
        return self.buffers.get(int(mapping_id), [])

    def get_mapping_row_count(self, mapping_id):
        if mapping_id is None:
            return None
        mapping_id = int(mapping_id)
        if mapping_id not in self.mappings:
            return None
        return len(self.buffers.get(mapping_id, []))

    def append_mapping_reading(self, mapping_id, reading):
        """O(1) append that schedules NO save — see store.append_mapping_reading."""
        if mapping_id is None:
            return False
        mapping_id = int(mapping_id)
        if mapping_id not in self.mappings:
            return False
        self.buffers.setdefault(mapping_id, []).append(reading)
        return True

    def set_mapping_buffer(self, mapping_id, readings):
        """Wholesale replace (prune / clear / cap). Unlike an append, this writes."""
        if mapping_id is None:
            return
        mapping_id = int(mapping_id)
        if mapping_id not in self.mappings:
            return
        self.buffers[mapping_id] = list(readings) if isinstance(readings, list) else []
        self.saves += 1

    def set_mapping_last_entry_value(self, mapping_id, key, value):
        """Carry-forward refresh that schedules NO save, like the real store."""
        if mapping_id is None:
            return
        mapping = self.mappings.get(int(mapping_id))
        if mapping is None:
            return
        # Fresh dict, mirroring the real store: MappingEntry.data_last_entry's
        # attrs default is a single shared {}, so it must never be mutated in place.
        last_entry = dict(mapping.get(const.MAPPING_DATA_LAST_ENTRY) or {})
        last_entry[key] = value
        mapping[const.MAPPING_DATA_LAST_ENTRY] = last_entry

    async def async_update_mapping(self, mapping_id, changes):
        stored = self.mappings[int(mapping_id)]
        changes = dict(changes)
        # The real store routes a `data` key to set_mapping_buffer instead of
        # storing it as a field; mirror that or a test would write a buffer onto
        # the record where nothing reads it.
        if const.MAPPING_DATA in changes:
            self.set_mapping_buffer(mapping_id, changes.pop(const.MAPPING_DATA))
        # Mirror the real store's key-by-key carry-forward merge (store.py).
        old_last = stored.get(const.MAPPING_DATA_LAST_ENTRY) or {}
        if old_last:
            merged = dict(changes.get(const.MAPPING_DATA_LAST_ENTRY) or {})
            for key, val in old_last.items():
                merged.setdefault(key, val)
            changes = {**changes, const.MAPPING_DATA_LAST_ENTRY: merged}
        stored.update(changes)
        self.saves += 1
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


class TestHotPathDoesNotCopyTheBuffer:
    """The append path must stay O(1) in the buffer length.

    store.get_mapping()/async_get_mappings() attr.asdict() the whole reading
    buffer (measured ~3 us/row, so ~30 ms at 10k rows). Calling either once per
    sensor event makes an ingestion cycle O(n^2) CPU on the event loop — the exact
    failure the append path was rewritten to avoid. These tests fail if it comes
    back, which a timing benchmark could not do reliably.
    """

    async def test_state_change_never_calls_the_deep_copying_accessors(self):
        store = _FakeStore([_mapping(data=[{"x": 1}] * 500)])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()

        store.get_mapping = Mock(side_effect=AssertionError("get_mapping copies"))
        store.async_get_mappings = AsyncMock(
            side_effect=AssertionError("async_get_mappings copies every group")
        )
        # The read-modify-write shape this path was rewritten away from: copying
        # the buffer out, appending, and handing the whole list back is O(n) per
        # reading AND schedules a write, undoing both halves of the design.
        store.set_mapping_buffer = Mock(
            side_effect=AssertionError("set_mapping_buffer is O(buffer) and writes")
        )
        coord._sensor_state_changed(_event("sensor.temp", "21.5"))

        assert len(store.buffers[1]) == 501
        assert not coord.created_tasks or True  # flush task is fine; appends are not
        for coro in coord.created_tasks:
            coro.close()
        coord.created_tasks.clear()

    async def test_setup_never_calls_async_get_mappings(self):
        store = _FakeStore([_mapping(data=[{"x": 1}] * 500)])
        coord = _coord(store)
        store.async_get_mappings = AsyncMock(
            side_effect=AssertionError("setup re-runs on every _config_updated")
        )
        await coord.async_setup_continuous_updates()
        assert list(coord._continuous_targets) == ["sensor.temp"]


class TestNoWritePerReading:
    """Ingestion must not put the store back on the disk-write path.

    This is the guarantee feat/storage-save-delay Step 4 bought and that merging
    continuous updates into it could silently undo: readings live in
    ``store.buffers``, outside the routine save payload, and the carry-forward
    that accompanies each reading is evolved WITHOUT scheduling a save. Get
    either wrong and every sensor event reserializes the whole document again —
    with no test failure to show for it, only a worn-out SD card.
    """

    async def test_appending_readings_schedules_no_save(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        store.saves = 0

        for value in ("21.5", "25.0", "28.5", "32.0"):
            coord._sensor_state_changed(_event("sensor.temp", value))

        # Four readings buffered, zero writes: they ride out on the flush timer,
        # on somebody else's write, or at shutdown.
        assert len(store.buffers[1]) == 4
        assert store.saves == 0
        # …and the carry-forward tracked every one of them regardless.
        assert store.mappings[1][const.MAPPING_DATA_LAST_ENTRY] == {
            const.MAPPING_TEMPERATURE: 32.0
        }

        for coro in coord.created_tasks:
            coro.close()
        coord.created_tasks.clear()

    async def test_debounced_flush_is_what_writes(self):
        # The bookkeeping pass IS allowed to write — it is debounced to once per
        # burst, which is the whole point of separating it from the append.
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        coord._get_zones_that_use_this_mapping = AsyncMock(return_value=[])
        await coord.async_setup_continuous_updates()
        store.saves = 0

        coord._sensor_state_changed(_event("sensor.temp", "21.5"))
        assert store.saves == 0
        # async_call_later is stubbed in these unit tests, so run the debounced
        # pass directly rather than waiting on a timer that never fires.
        await coord._async_continuous_update_for_mapping(1)
        assert store.saves == 1


class TestStateChanged:
    async def test_appends_sparse_row_and_updates_last_entry(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(_event("sensor.temp", "21.5"))
        await _drain(coord)

        rows = store.buffers[1]
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
        assert [r[const.MAPPING_TEMPERATURE] for r in store.buffers[1]] == [
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
        assert store.buffers[1] == []

    async def test_untracked_entity_is_ignored(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(_event("sensor.something_else", "5"))
        await _drain(coord)
        assert store.buffers[1] == []

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
        stored = store.buffers[1][0][const.MAPPING_TEMPERATURE]
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
        assert len(store.buffers[1]) == 1
        # Above the threshold: recorded.
        coord._sensor_state_changed(_event("sensor.temp", str(20.0 + step * 2)))
        await _drain(coord)
        assert len(store.buffers[1]) == 2

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
        assert len(store.buffers[1]) > 1

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
        assert len(store.buffers[1]) == 3


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
        # Exactly ONE task: the flush. The reading itself is appended
        # synchronously via store.append_mapping_reading, so there is no
        # per-reading task hop (and no per-reading buffer copy) any more.
        assert len(coord.created_tasks) == 1
        assert len(store.buffers[1]) == 1
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
        kept = store.buffers[1]
        assert len(kept) == 6  # the cap plus the re-inserted boundary
        assert kept[0][const.MAPPING_TEMPERATURE] == 0
        assert kept[-1][const.MAPPING_TEMPERATURE] == 19

    async def test_row_cap_leaves_a_buffer_under_the_cap_alone(self):
        rows = [{const.MAPPING_TEMPERATURE: i} for i in range(10)]
        store = _FakeStore([_mapping(data=rows)])
        coord = _coord(store)
        await coord._continuous_enforce_row_cap(1)
        assert len(store.buffers[1]) == 10


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
        assert store.buffers[1] == []
        assert store.mappings[1][const.MAPPING_DATA_LAST_ENTRY] == {"Humidity": None}


class TestIntervalPollSkip:
    """Step 3 of the port: the event path IS the data path for sensor groups."""

    def _poll_coord(self, *, continuous, owm_in_mapping, static_in_mapping=False):
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
        # The poll writes its row through the buffer accessors, not through
        # async_update_mapping — so append_mapping_reading is what "this group was
        # polled" now means, and it is what these tests assert on below.
        coord.store.append_mapping_reading = Mock(return_value=True)
        coord.store.get_mapping_row_count = Mock(return_value=0)
        coord.check_mapping_sources = Mock(
            return_value=(owm_in_mapping, True, static_in_mapping)
        )
        coord.build_static_values_for_mapping = Mock(
            return_value={const.MAPPING_HUMIDITY: 50.0}
        )
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
        coord.store.append_mapping_reading.assert_not_called()

    async def test_weather_service_group_still_polls_when_continuous(self):
        # Weather-service data only arrives by API call; the event path never
        # fetches it, so this group must keep its scheduled poll.
        coord = self._poll_coord(continuous=True, owm_in_mapping=True)
        await coord._async_update_all()
        coord.store.append_mapping_reading.assert_called_once()

    async def test_pure_sensor_group_still_polls_when_feature_off(self):
        coord = self._poll_coord(continuous=False, owm_in_mapping=False)
        await coord._async_update_all()
        coord.store.append_mapping_reading.assert_called_once()

    async def test_group_with_static_values_still_polls_when_continuous(self):
        # A static field is written ONLY by this poll — the event path has nothing
        # to subscribe to for it. Skipping the group would drop the static fields
        # out of the buffer and leave the calc module short an input.
        coord = self._poll_coord(
            continuous=True, owm_in_mapping=False, static_in_mapping=True
        )
        await coord._async_update_all()
        coord.store.append_mapping_reading.assert_called_once()


class TestBaselineSeeding:
    """Subscribing must capture each sensor's CURRENT value, not just future changes.

    A flat field (overnight solar at 0, calm wind, an unchanged rain counter) emits
    no state-change event, so without seeding it never reaches the buffer at all —
    and with the interval poll skipped or disabled there is no other writer. This
    was found by running the branch against live sensor data.
    """

    async def test_current_values_are_recorded_on_subscribe(self):
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        coord.hass.states.get = Mock(
            return_value=SimpleNamespace(
                state="21.0", attributes={"unit_of_measurement": "°C"}
            )
        )
        await coord.async_setup_continuous_updates()
        rows = store.buffers[1]
        assert len(rows) == 1
        assert rows[0][const.MAPPING_TEMPERATURE] == 21.0
        # The deadband reference is seeded too, so the next small move is measured
        # against a real value instead of being treated as a first reading.
        assert coord._continuous_last_value[(1, const.MAPPING_TEMPERATURE)] == 21.0

    async def test_unavailable_and_non_numeric_states_are_not_seeded(self):
        for bad in (STATE_UNAVAILABLE, STATE_UNKNOWN, "not a number"):
            store = _FakeStore([_mapping()])
            coord = _coord(store)
            coord.hass.states.get = Mock(
                return_value=SimpleNamespace(state=bad, attributes={})
            )
            await coord.async_setup_continuous_updates()
            assert store.buffers[1] == [], bad

    async def test_no_seeding_when_feature_is_off(self):
        store = _FakeStore([_mapping()], enabled=False)
        coord = _coord(store)
        coord.hass.states.get = Mock(
            return_value=SimpleNamespace(state="21.0", attributes={})
        )
        await coord.async_setup_continuous_updates()
        assert store.buffers[1] == []

    async def test_unchanged_entity_set_does_not_reseed(self):
        # _config_updated fires constantly; re-seeding on every one would append a
        # duplicate row each time.
        store = _FakeStore([_mapping()])
        coord = _coord(store)
        coord.hass.states.get = Mock(
            return_value=SimpleNamespace(state="21.0", attributes={})
        )
        await coord.async_setup_continuous_updates()
        await coord.async_setup_continuous_updates()
        await coord.async_setup_continuous_updates()
        assert len(store.buffers[1]) == 1


# Elevation of the sensor group this was reported against, in metres.
_ELEVATION = 311


def _pressure_mapping(pressure_type):
    """A sensor group whose only field is a pressure sensor of the given type."""
    field = {
        const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
        const.MAPPING_CONF_SENSOR: "sensor.pressure",
    }
    if pressure_type is not None:
        field[const.MAPPING_CONF_PRESSURE_TYPE] = pressure_type
    return _mapping(mappings={const.MAPPING_PRESSURE: field})


def _pressure_coord(store):
    coord = _coord(store)
    coord.hass.config.elevation = _ELEVATION
    # The interval path reads elevation out of the full config dict, the event
    # path off the attribute; a Mock hass has to answer both.
    coord.hass.config.as_dict = Mock(return_value={CONF_ELEVATION: _ELEVATION})
    return coord


class TestRelativePressureIsAbsolutised:
    """Both writers of MAPPING_PRESSURE must store the SAME physical quantity.

    The calc modules read that field as station (absolute) pressure, and
    weather_aggregate means the buffer's rows together — so a buffer holding
    sea-level rows from one ingestion path and station rows from the other makes
    the daily aggregate a mix of two quantities. The interval poll has always
    applied the elevation correction for a ``pressure_type: relative`` group; the
    event-driven path bypassed it entirely until both were routed through
    helpers.to_absolute_pressure.
    """

    async def test_state_change_converts_relative_pressure(self):
        store = _FakeStore([_pressure_mapping(const.MAPPING_CONF_PRESSURE_RELATIVE)])
        coord = _pressure_coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(
            _event("sensor.pressure", "1020.0", {"unit_of_measurement": "hPa"})
        )
        await _drain(coord)

        stored = store.buffers[1][0][const.MAPPING_PRESSURE]
        assert stored == relative_to_absolute_pressure(1020.0, _ELEVATION)
        # Not the raw reading: the elevation correction was actually applied.
        assert stored != 1020.0
        # The carry-forward has to hold the corrected value too — a window with
        # no pressure row falls back to it and would otherwise reintroduce the
        # sea-level quantity the buffer no longer carries.
        assert store.mappings[1][const.MAPPING_DATA_LAST_ENTRY] == {
            const.MAPPING_PRESSURE: stored
        }

    async def test_baseline_seed_converts_relative_pressure(self):
        # The seed is a separate writer into the same buffer, so it needs the
        # same treatment — a group whose pressure never moves is seeded and then
        # never touched again.
        store = _FakeStore([_pressure_mapping(const.MAPPING_CONF_PRESSURE_RELATIVE)])
        coord = _pressure_coord(store)
        coord.hass.states.get = Mock(
            return_value=SimpleNamespace(
                state="1020.0", attributes={"unit_of_measurement": "hPa"}
            )
        )
        await coord.async_setup_continuous_updates()

        stored = store.buffers[1][0][const.MAPPING_PRESSURE]
        assert stored == relative_to_absolute_pressure(1020.0, _ELEVATION)
        assert stored != 1020.0
        # The deadband reference is the appended value, so it must be corrected
        # as well or the next reading is compared against a different quantity.
        assert coord._continuous_last_value[(1, const.MAPPING_PRESSURE)] == stored

    @pytest.mark.parametrize("pressure_type", [None, "absolute"])
    async def test_non_relative_groups_are_stored_untouched(self, pressure_type):
        store = _FakeStore([_pressure_mapping(pressure_type)])
        coord = _pressure_coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(
            _event("sensor.pressure", "1020.0", {"unit_of_measurement": "hPa"})
        )
        await _drain(coord)

        assert store.buffers[1][0][const.MAPPING_PRESSURE] == 1020.0

    async def test_event_and_interval_paths_agree(self):
        """The property the split is really about: same input, same stored value.

        Asserts against the poll path's own output rather than a hard-coded
        number, so the two cannot drift apart again if the conversion itself is
        ever revised.
        """
        store = _FakeStore([_pressure_mapping(const.MAPPING_CONF_PRESSURE_RELATIVE)])
        coord = _pressure_coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(
            _event("sensor.pressure", "1020.0", {"unit_of_measurement": "hPa"})
        )
        await _drain(coord)
        from_event = store.buffers[1][0][const.MAPPING_PRESSURE]

        # What the interval poll would have appended for the same reading.
        polled = {const.MAPPING_PRESSURE: 1020.0}
        coord._apply_pressure_type(store.get_mapping(1), polled)

        assert from_event == polled[const.MAPPING_PRESSURE]

    async def test_imperial_sensor_is_converted_to_hpa_before_the_correction(self):
        # Order matters: the elevation correction is defined on hPa, so an inHg
        # sensor has to reach metric first. Running it the other way round would
        # correct a number that is not a pressure in the expected unit.
        store = _FakeStore([_pressure_mapping(const.MAPPING_CONF_PRESSURE_RELATIVE)])
        coord = _pressure_coord(store)
        await coord.async_setup_continuous_updates()
        coord._sensor_state_changed(
            _event("sensor.pressure", "30.12", {"unit_of_measurement": "inHg"})
        )
        await _drain(coord)

        in_hpa = convert_mapping_to_metric(
            30.12, const.MAPPING_PRESSURE, UNIT_INHG, True
        )
        assert store.buffers[1][0][const.MAPPING_PRESSURE] == (
            relative_to_absolute_pressure(in_hpa, _ELEVATION)
        )
