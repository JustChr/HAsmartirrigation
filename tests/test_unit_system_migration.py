"""Changing HA's unit system must not silently reinterpret stored zone values.

Issue #67. Zone depths, size and throughput are stored in DISPLAY units, so a
flip between metric and US customary changes what every one of those numbers
MEANS — by 25.4, 10.764 and 3.785 — with nothing on disk recording which system
wrote them. The reporter's own reproduction used configuration.yaml plus a
restart, which fires no `core_config_updated` event at all, so the in-memory
`previous_unit_system` cannot see it either.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.irrigation_plus import (
    SmartIrrigationCoordinator,
    async_handle_core_config_change,
    const,
)
from custom_components.irrigation_plus.store import STORAGE_VERSION, MigratableStore
from custom_components.irrigation_plus.unit_system import (
    convert_zone_values,
    unit_system_name,
)

_MM_PER_INCH = 25.4


def _zone(zone_id=1, **overrides):
    """A metric zone: mm depths, m2 size, l/min throughput."""
    zone = {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: "Test Lawn",
        const.ZONE_BUCKET: -8.0,
        const.ZONE_MAXIMUM_BUCKET: 24.0,
        const.ZONE_DRAINAGE_RATE: 20.0,
        const.ZONE_BUCKET_THRESHOLD: -10.0,
        const.ZONE_IRRIGATION_TARGET_BUCKET: -2.0,
        const.ZONE_SIZE: 100.0,
        const.ZONE_THROUGHPUT: 30.0,
    }
    zone.update(overrides)
    return zone


class _FakeStore:
    def __init__(self, zones, stored_unit_system):
        self._zones = {z[const.ZONE_ID]: dict(z) for z in zones}
        self.config = SimpleNamespace(stored_unit_system=stored_unit_system)
        self.config_updates = []

    async def async_get_zones(self):
        return [dict(z) for z in self._zones.values()]

    async def async_update_zone(self, zone_id, changes):
        self._zones[zone_id].update(changes)

    async def async_update_config(self, changes):
        self.config_updates.append(changes)
        for key, value in changes.items():
            setattr(self.config, key, value)

    def zone(self, zone_id=1):
        return self._zones[zone_id]


def _coord(store, units):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.hass = Mock()
    coord.hass.config.units = units
    coord.store = store
    return coord


class TestConversionItself:
    """The pure conversion, independent of any detection."""

    def test_metric_to_imperial_converts_all_seven_fields(self):
        changes = convert_zone_values(_zone(), to_metric=False)
        assert set(changes) == {
            const.ZONE_BUCKET,
            const.ZONE_MAXIMUM_BUCKET,
            const.ZONE_DRAINAGE_RATE,
            const.ZONE_BUCKET_THRESHOLD,
            const.ZONE_IRRIGATION_TARGET_BUCKET,
            const.ZONE_SIZE,
            const.ZONE_THROUGHPUT,
        }

    def test_depths_are_divided_by_25_4(self):
        changes = convert_zone_values(_zone(), to_metric=False)
        assert changes[const.ZONE_MAXIMUM_BUCKET] == pytest.approx(24.0 / _MM_PER_INCH)
        assert changes[const.ZONE_BUCKET_THRESHOLD] == pytest.approx(
            -10.0 / _MM_PER_INCH
        )

    def test_round_trip_returns_the_original_values(self):
        """Repeated flips must not drift the numbers."""
        original = _zone()
        there = convert_zone_values(original, to_metric=False)
        back = convert_zone_values({**original, **there}, to_metric=True)
        for field, value in back.items():
            assert value == pytest.approx(original[field]), field

    def test_current_drainage_is_never_converted(self):
        """It is written in mm on BOTH systems; converting would corrupt it."""
        zone = _zone(**{const.ZONE_CURRENT_DRAINAGE: 5.0})
        assert const.ZONE_CURRENT_DRAINAGE not in convert_zone_values(
            zone, to_metric=False
        )

    def test_none_values_are_left_unset(self):
        """An unset maximum_bucket means 'no ceiling' — don't invent one."""
        zone = _zone(**{const.ZONE_MAXIMUM_BUCKET: None})
        assert const.ZONE_MAXIMUM_BUCKET not in convert_zone_values(
            zone, to_metric=False
        )

    def test_non_numeric_junk_is_skipped_not_crashed_on(self):
        zone = _zone(**{const.ZONE_SIZE: "not a number"})
        changes = convert_zone_values(zone, to_metric=False)
        assert const.ZONE_SIZE not in changes
        assert const.ZONE_BUCKET in changes  # the rest still converts


class TestReconciliation:
    @pytest.fixture(autouse=True)
    def _silence_dispatch(self, monkeypatch):
        """These assert on the STORE; the per-zone refresh has its own class."""
        monkeypatch.setattr(
            "custom_components.irrigation_plus.async_dispatcher_send",
            lambda *a, **kw: None,
        )

    async def test_the_reported_bug_metric_to_us_customary(self):
        """The issue's own reproduction: same digits, new meaning."""
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        coord = _coord(store, US_CUSTOMARY_SYSTEM)

        assert await coord.async_reconcile_stored_unit_system() == 1

        zone = store.zone()
        # -10 mm must become -0.394 in, NOT stay -10 (which would read as
        # -254 mm and suppress every deficit-gated run).
        assert zone[const.ZONE_BUCKET_THRESHOLD] == pytest.approx(-10.0 / _MM_PER_INCH)
        assert zone[const.ZONE_MAXIMUM_BUCKET] == pytest.approx(24.0 / _MM_PER_INCH)
        assert store.config.stored_unit_system == const.UNIT_SYSTEM_US_CUSTOMARY

    async def test_no_change_means_no_writes(self):
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        coord = _coord(store, METRIC_SYSTEM)
        before = dict(store.zone())

        assert await coord.async_reconcile_stored_unit_system() == 0

        assert store.zone() == before
        assert store.config_updates == []

    async def test_running_twice_converts_once(self):
        """Idempotent by construction: the guard is the persisted value."""
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        coord = _coord(store, US_CUSTOMARY_SYSTEM)

        await coord.async_reconcile_stored_unit_system()
        after_first = dict(store.zone())
        assert await coord.async_reconcile_stored_unit_system() == 0

        assert store.zone() == after_first

    async def test_flipping_back_restores_the_original_values(self):
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        original = dict(store.zone())

        await _coord(store, US_CUSTOMARY_SYSTEM).async_reconcile_stored_unit_system()
        await _coord(store, METRIC_SYSTEM).async_reconcile_stored_unit_system()

        for field, value in original.items():
            if isinstance(value, (int, float)):
                assert store.zone()[field] == pytest.approx(value), field

    async def test_a_store_with_no_recorded_system_is_seeded_not_converted(self):
        """Pre-v13 store: we don't know the old system, so guessing would be wrong."""
        store = _FakeStore([_zone()], None)
        coord = _coord(store, US_CUSTOMARY_SYSTEM)
        before = dict(store.zone())

        assert await coord.async_reconcile_stored_unit_system() == 0

        assert store.zone() == before
        assert store.config.stored_unit_system == const.UNIT_SYSTEM_US_CUSTOMARY

    async def test_every_zone_is_converted(self):
        store = _FakeStore([_zone(1), _zone(2), _zone(3)], const.UNIT_SYSTEM_METRIC)
        coord = _coord(store, US_CUSTOMARY_SYSTEM)

        assert await coord.async_reconcile_stored_unit_system() == 3

    async def test_the_bookkeeping_is_written_last(self):
        """A crash mid-conversion must retry, not claim the job is done."""
        store = _FakeStore([_zone(1), _zone(2)], const.UNIT_SYSTEM_METRIC)
        store.async_update_zone = AsyncMock(side_effect=RuntimeError("store died"))
        coord = _coord(store, US_CUSTOMARY_SYSTEM)

        with pytest.raises(RuntimeError):
            await coord.async_reconcile_stored_unit_system()

        assert store.config.stored_unit_system == const.UNIT_SYSTEM_METRIC


class TestTheUiPath:
    """`async_handle_unit_system_change` is the live-change half of the fix."""

    async def test_the_handler_converts_before_refreshing_anything(self, monkeypatch):
        """Order matters: refreshing first would publish the old digits."""
        sent = []
        monkeypatch.setattr(
            "custom_components.irrigation_plus.async_dispatcher_send",
            lambda _hass, signal, *a: sent.append((signal, dict(store.zone()))),
        )
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        coord = _coord(store, US_CUSTOMARY_SYSTEM)

        await coord.async_handle_unit_system_change()

        assert sent, "the handler must still notify entities and the panel"
        # Every dispatch saw the CONVERTED value, not the reinterpreted one.
        for _, zone_at_dispatch in sent:
            assert zone_at_dispatch[const.ZONE_BUCKET_THRESHOLD] == pytest.approx(
                -10.0 / _MM_PER_INCH
            )


class TestTheConvertedValuesReachTheEntities:
    """Converting the store is only half the job — the entities cache.

    Reported by clarejor against v2026.08.02: after a live flip the store was
    correct but `sensor.<zone>_bucket` and the duration sensor's attributes
    still showed the PRE-conversion digits under the NEW unit label, which
    reads as a real value rather than as a display glitch. `async_update_zone`
    only schedules a save and dispatches nothing, and both entities answer
    `_unit_system_changed` with `async_schedule_update_ha_state(force_refresh)`
    — but neither class defines `async_update`, so the refresh re-renders the
    cached value. `_config_updated` carrying the zone id is the signal they
    already re-read the store on, so the reconcile loop has to send it.
    """

    @staticmethod
    def _capture(monkeypatch):
        sent = []
        monkeypatch.setattr(
            "custom_components.irrigation_plus.async_dispatcher_send",
            lambda _hass, signal, *args: sent.append((signal, args)),
        )
        return sent

    async def test_each_converted_zone_is_announced(self, monkeypatch):
        sent = self._capture(monkeypatch)
        store = _FakeStore([_zone(1), _zone(2), _zone(3)], const.UNIT_SYSTEM_METRIC)

        await _coord(store, US_CUSTOMARY_SYSTEM).async_reconcile_stored_unit_system()

        announced = [
            args[0] for signal, args in sent if signal.endswith("_config_updated")
        ]
        assert announced == [1, 2, 3]

    async def test_the_announcement_carries_the_converted_value(self, monkeypatch):
        """Dispatch AFTER the write, or the entity re-reads the old digits."""
        seen = []
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        monkeypatch.setattr(
            "custom_components.irrigation_plus.async_dispatcher_send",
            lambda _hass, signal, *args: seen.append(
                (signal, store.zone()[const.ZONE_BUCKET_THRESHOLD])
            ),
        )

        await _coord(store, US_CUSTOMARY_SYSTEM).async_reconcile_stored_unit_system()

        assert seen, "the conversion must announce itself"
        for _, threshold in seen:
            assert threshold == pytest.approx(-10.0 / _MM_PER_INCH)

    async def test_a_zone_with_nothing_to_convert_is_not_announced(self, monkeypatch):
        """No write, no refresh — an empty dispatch is just noise."""
        sent = self._capture(monkeypatch)
        blank = {
            const.ZONE_ID: 1,
            const.ZONE_NAME: "Empty",
            const.ZONE_BUCKET: None,
            const.ZONE_MAXIMUM_BUCKET: None,
            const.ZONE_DRAINAGE_RATE: None,
            const.ZONE_BUCKET_THRESHOLD: None,
            const.ZONE_IRRIGATION_TARGET_BUCKET: None,
            const.ZONE_SIZE: None,
            const.ZONE_THROUGHPUT: None,
        }
        store = _FakeStore([blank], const.UNIT_SYSTEM_METRIC)

        await _coord(store, US_CUSTOMARY_SYSTEM).async_reconcile_stored_unit_system()

        assert not [s for s, _ in sent if s.endswith("_config_updated")]

    async def test_no_flip_announces_nothing(self, monkeypatch):
        sent = self._capture(monkeypatch)
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)

        await _coord(store, METRIC_SYSTEM).async_reconcile_stored_unit_system()

        assert sent == []


class TestTheCoreConfigEventPath:
    """`async_handle_core_config_change` — the UI half, end to end.

    Every test here would have passed against a handler that never ran, which
    is exactly what shipped: the handler logged `previous_unit_system.name`,
    `UnitSystem` has no public `name`, and the AttributeError killed it one
    line before the dispatch. It went unnoticed because the handler was a
    nested closure inside `async_setup_entry` and the only test covering it was
    skipped as "not importable". So assert on the EFFECT, not on the call.
    """

    @staticmethod
    def _wire(store, previous_units, current_units):
        """A coordinator reachable the way the event handler reaches it."""
        coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
        coord.store = store
        coord.previous_unit_system = previous_units
        hass = Mock()
        hass.config.units = current_units
        hass.data = {const.DOMAIN: {"coordinator": coord}}
        coord.hass = hass
        return coord, hass

    @staticmethod
    def _event():
        return Mock(data={"unit_system": "us_customary"})

    @pytest.fixture(autouse=True)
    def _silence_dispatch(self, monkeypatch):
        monkeypatch.setattr(
            "custom_components.irrigation_plus.async_dispatcher_send",
            lambda *a, **kw: None,
        )

    async def test_a_ui_flip_converts_the_stored_values(self):
        """The regression: this raised AttributeError before reaching any of it."""
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        _coord_obj, hass = self._wire(store, METRIC_SYSTEM, US_CUSTOMARY_SYSTEM)

        await async_handle_core_config_change(hass, self._event())

        assert store.zone()[const.ZONE_BUCKET_THRESHOLD] == pytest.approx(
            -10.0 / _MM_PER_INCH
        )
        assert store.config.stored_unit_system == const.UNIT_SYSTEM_US_CUSTOMARY

    async def test_the_cached_system_advances_so_it_fires_once(self):
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        coord, hass = self._wire(store, METRIC_SYSTEM, US_CUSTOMARY_SYSTEM)

        await async_handle_core_config_change(hass, self._event())

        assert coord.previous_unit_system is US_CUSTOMARY_SYSTEM

    async def test_an_unrelated_core_config_change_converts_nothing(self):
        """`core_config_updated` also fires for location, currency, name..."""
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        _coord_obj, hass = self._wire(store, METRIC_SYSTEM, METRIC_SYSTEM)
        before = dict(store.zone())

        await async_handle_core_config_change(hass, Mock(data={"currency": "EUR"}))

        assert store.zone() == before
        assert store.config_updates == []

    async def test_it_no_ops_before_the_coordinator_exists(self):
        hass = Mock()
        hass.data = {}
        await async_handle_core_config_change(hass, self._event())

        hass.data = {const.DOMAIN: {}}
        await async_handle_core_config_change(hass, self._event())

    async def test_a_missing_cached_system_still_reconciles(self):
        """Degrades to the persisted guard rather than crashing on the log line."""
        store = _FakeStore([_zone()], const.UNIT_SYSTEM_METRIC)
        coord, hass = self._wire(store, METRIC_SYSTEM, US_CUSTOMARY_SYSTEM)
        del coord.previous_unit_system

        await async_handle_core_config_change(hass, self._event())

        assert store.config.stored_unit_system == const.UNIT_SYSTEM_US_CUSTOMARY


class TestUnitSystemName:
    """`UnitSystem.name` does not exist — this helper is why we stopped using it."""

    def test_the_private_attribute_is_still_the_only_one(self):
        """Pins the assumption. If HA ever adds a public `name`, revisit."""
        assert not hasattr(METRIC_SYSTEM, "name")

    def test_both_systems_get_a_loggable_name(self):
        assert unit_system_name(METRIC_SYSTEM) == const.UNIT_SYSTEM_METRIC
        assert unit_system_name(US_CUSTOMARY_SYSTEM) == const.UNIT_SYSTEM_US_CUSTOMARY

    def test_none_does_not_masquerade_as_a_real_system(self):
        assert unit_system_name(None) == "unknown"


class TestV13Migration:
    """The bump only starts the bookkeeping — it must convert nothing."""

    def _store(self, hass):
        return MigratableStore(hass, STORAGE_VERSION, "smart_irrigation.storage")

    def _v12_data(self):
        return {
            "config": {"calctime": "23:00", "autocalcenabled": True},
            "zones": [_zone()],
            "mappings": [],
            "modules": [],
        }

    async def test_seeds_from_the_current_system(self, hass):
        hass.config.units = METRIC_SYSTEM
        data = await self._store(hass)._async_migrate_func(12, self._v12_data())
        assert data["config"][const.CONF_STORED_UNIT_SYSTEM] == const.UNIT_SYSTEM_METRIC

    async def test_seeds_us_customary_on_an_imperial_install(self, hass):
        hass.config.units = US_CUSTOMARY_SYSTEM
        data = await self._store(hass)._async_migrate_func(12, self._v12_data())
        assert (
            data["config"][const.CONF_STORED_UNIT_SYSTEM]
            == const.UNIT_SYSTEM_US_CUSTOMARY
        )

    async def test_zone_values_are_untouched_by_the_migration(self, hass):
        """Seeding is correct by construction precisely BECAUSE nothing moves."""
        hass.config.units = US_CUSTOMARY_SYSTEM
        before = _zone()
        data = await self._store(hass)._async_migrate_func(12, self._v12_data())
        assert data["zones"][0] == before

    async def test_an_existing_recorded_system_is_not_overwritten(self, hass):
        """Re-running the migration must not relabel already-converted data."""
        hass.config.units = US_CUSTOMARY_SYSTEM
        old = self._v12_data()
        old["config"][const.CONF_STORED_UNIT_SYSTEM] = const.UNIT_SYSTEM_METRIC

        data = await self._store(hass)._async_migrate_func(12, old)

        assert data["config"][const.CONF_STORED_UNIT_SYSTEM] == const.UNIT_SYSTEM_METRIC

    async def test_existing_config_survives_the_bump(self, hass):
        hass.config.units = METRIC_SYSTEM
        data = await self._store(hass)._async_migrate_func(12, self._v12_data())
        assert data["config"]["calctime"] == "23:00"
        assert data["config"]["autocalcenabled"] is True
