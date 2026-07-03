"""Per-zone soil-moisture wet-veto (skip condition)."""

from unittest.mock import AsyncMock, Mock

import attr

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.store import (
    SmartIrrigationStorage,
    ZoneEntry,
    async_get_registry,
)


# --- Task 1: storage -------------------------------------------------------

def test_zone_entry_has_soil_moisture_fields():
    z = ZoneEntry()
    assert z.soil_moisture_sensor is None
    assert z.soil_moisture_threshold is None


def test_constants_defined():
    assert const.ZONE_SOIL_MOISTURE_SENSOR == "soil_moisture_sensor"
    assert const.ZONE_SOIL_MOISTURE_THRESHOLD == "soil_moisture_threshold"
    assert const.EVENT_ZONE_SKIPPED == "zone_skipped"
    assert const.SKIP_REASON_SOIL_MOISTURE == "soil_moisture"


async def test_soil_moisture_fields_survive_reload(hass):
    reg = await async_get_registry(hass)
    created = await reg.async_create_zone(
        {
            "name": "Beet",
            "size": 10.0,
            "throughput": 5.0,
            "soil_moisture_sensor": "sensor.beet_soil",
            "soil_moisture_threshold": 50.0,
        }
    )
    assert created["soil_moisture_sensor"] == "sensor.beet_soil"
    assert created["soil_moisture_threshold"] == 50.0

    data = {
        "config": attr.asdict(reg.config),
        "zones": [attr.asdict(z) for z in reg.zones.values()],
        "modules": [],
        "mappings": [],
    }
    reg._store.async_load = AsyncMock(return_value=data)
    fresh = SmartIrrigationStorage(hass)
    fresh._store.async_load = AsyncMock(return_value=data)
    await fresh.async_load()
    zid = created["id"]
    reloaded = attr.asdict(fresh.zones[int(zid)])
    assert reloaded["soil_moisture_sensor"] == "sensor.beet_soil"
    assert reloaded["soil_moisture_threshold"] == 50.0


# --- Task 2: veto evaluation ----------------------------------------------

def _coord():
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    c.hass = Mock()
    c.hass.bus.async_fire = Mock()
    c.hass.states.get = Mock(return_value=None)
    c.async_update_zone_config = AsyncMock()
    c._record_run = AsyncMock()
    # isolate the frontend-refresh dispatch (tested via get_zone_skips instead)
    c._notify_skip_listeners = Mock()
    return c


def _zone(**kw):
    z = {
        const.ZONE_ID: 2,
        const.ZONE_NAME: "Beet",
        const.ZONE_DURATION: 600.0,
        const.ZONE_BUCKET: -5.0,
    }
    z.update(kw)
    return z


def _state(value):
    s = Mock()
    s.state = value
    return s


async def test_dry_zone_is_kept_untouched():
    c = _coord()
    c.hass.states.get = Mock(return_value=_state("40"))
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    out = await c._apply_soil_moisture_veto([z])
    assert out == [z]
    c.async_update_zone_config.assert_not_awaited()
    c.hass.bus.async_fire.assert_not_called()


async def test_wet_zone_is_vetoed_bucket_reset_event_and_skip_recorded():
    c = _coord()
    c.hass.states.get = Mock(return_value=_state("52"))
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    out = await c._apply_soil_moisture_veto([z])
    # dropped from the run
    assert out == []
    # bucket re-anchored to 0 via the existing reset mechanism
    c.async_update_zone_config.assert_awaited_once_with(
        zone_id=2,
        data={const.ATTR_SET_BUCKET: {}, const.ATTR_NEW_BUCKET_VALUE: 0},
    )
    # event fired with the details
    name, data = c.hass.bus.async_fire.call_args.args
    assert name == f"{const.DOMAIN}_{const.EVENT_ZONE_SKIPPED}"
    assert data["zone_id"] == 2
    assert data["zone"] == "Beet"
    assert data["entity_id"] == "sensor.s"
    assert data["reason"] == const.SKIP_REASON_SOIL_MOISTURE
    assert data["observed"] == 52.0
    assert data["threshold"] == 50.0
    # per-zone skip recorded for the dashboard
    skip = c.get_zone_skips()[2]
    assert skip["reason"] == const.SKIP_REASON_SOIL_MOISTURE
    assert skip["observed"] == 52.0
    assert skip["threshold"] == 50.0
    assert skip["entity_id"] == "sensor.s"


async def test_wet_zone_records_skipped_run_in_history():
    """A veto writes a persistent 'skipped' run-log entry (survives restarts)."""
    c = _coord()
    c.hass.states.get = Mock(return_value=_state("52"))
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    await c._apply_soil_moisture_veto([z])
    c._record_run.assert_awaited_once_with(
        2,
        result=const.RUN_RESULT_SKIPPED,
        detail=const.SKIP_REASON_SOIL_MOISTURE,
    )


async def test_boundary_equal_threshold_waters():
    c = _coord()
    c.hass.states.get = Mock(return_value=_state("50"))
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    out = await c._apply_soil_moisture_veto([z])
    assert out == [z]  # strict >, so == threshold still waters
    c.hass.bus.async_fire.assert_not_called()


async def test_unavailable_sensor_fails_open():
    c = _coord()
    c.hass.states.get = Mock(return_value=_state("unavailable"))
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    out = await c._apply_soil_moisture_veto([z])
    assert out == [z]
    c.async_update_zone_config.assert_not_awaited()
    c.hass.bus.async_fire.assert_not_called()


async def test_missing_state_fails_open():
    c = _coord()
    c.hass.states.get = Mock(return_value=None)
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    assert await c._apply_soil_moisture_veto([z]) == [z]


async def test_non_numeric_sensor_fails_open():
    c = _coord()
    c.hass.states.get = Mock(return_value=_state("wet-ish"))
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    assert await c._apply_soil_moisture_veto([z]) == [z]


async def test_feature_off_when_no_sensor_or_threshold():
    c = _coord()
    c.hass.states.get = Mock(return_value=_state("99"))
    # no sensor
    z1 = _zone(soil_moisture_threshold=50.0)
    # no threshold
    z2 = _zone(soil_moisture_sensor="sensor.s")
    assert await c._apply_soil_moisture_veto([z1, z2]) == [z1, z2]
    c.hass.bus.async_fire.assert_not_called()


async def test_multi_zone_only_wet_dropped():
    c = _coord()

    def pick(entity):
        return _state("60") if entity == "sensor.wet" else _state("30")

    c.hass.states.get = Mock(side_effect=pick)
    wet = _zone(
        **{const.ZONE_ID: 1},
        soil_moisture_sensor="sensor.wet",
        soil_moisture_threshold=50.0,
    )
    dry = _zone(
        **{const.ZONE_ID: 2},
        soil_moisture_sensor="sensor.dry",
        soil_moisture_threshold=50.0,
    )
    out = await c._apply_soil_moisture_veto([wet, dry])
    assert out == [dry]
    assert 1 in c.get_zone_skips() and 2 not in c.get_zone_skips()


async def test_irrigate_linked_entities_applies_veto(monkeypatch):
    """The automatic path calls the veto filter between rain-delay and live-durations."""
    c = _coord()
    # linked_entity so the zone passes the candidate filter and reaches the veto
    wet = _zone(
        linked_entity="switch.beet",
        soil_moisture_sensor="sensor.s",
        soil_moisture_threshold=50.0,
    )
    c.store = Mock()
    c.store.async_get_zones = AsyncMock(return_value=[wet])
    c.store.config = Mock(zone_sequencing="sequential", live_estimate_enabled=False)
    c._sc_is_self_closing = Mock(return_value=False)
    c._rain_delay_active = Mock(return_value=False)
    c.hass.states.get = Mock(return_value=_state("60"))  # wet -> veto
    # These must NOT be reached once the only zone is vetoed:
    c.async_master_begin_cycle = AsyncMock()
    c._apply_live_durations = AsyncMock(side_effect=AssertionError("must not run"))

    await c._irrigate_linked_entities("all")

    # zone was vetoed, so the run short-circuits before master/live-durations
    c.async_master_begin_cycle.assert_not_awaited()
    assert 2 in c.get_zone_skips()


async def test_non_finite_sensor_fails_open():
    """A broken sensor reporting inf/nan must water (fail-open), never veto forever."""
    c = _coord()
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    for val in ("inf", "-inf", "nan"):
        c.hass.states.get = Mock(return_value=_state(val))
        assert await c._apply_soil_moisture_veto([z]) == [z]
    c.async_update_zone_config.assert_not_awaited()
    c.hass.bus.async_fire.assert_not_called()


async def test_previously_recorded_skip_cleared_on_dry_run():
    """A stale skip chip is cleared once the zone reads dry again."""
    c = _coord()
    c._set_zone_skip(2, "sensor.s", 60.0, 50.0)
    assert 2 in c.get_zone_skips()
    c.hass.states.get = Mock(return_value=_state("30"))  # now dry
    z = _zone(soil_moisture_sensor="sensor.s", soil_moisture_threshold=50.0)
    out = await c._apply_soil_moisture_veto([z])
    assert out == [z]
    assert 2 not in c.get_zone_skips()


# --- Task 3: outlook exposure ---------------------------------------------

async def test_outlook_includes_zone_skips():
    c = _coord()
    # record a skip
    c._set_zone_skip(2, "sensor.s", 52.0, 50.0)
    # stub the heavy outlook dependencies
    c.store = Mock()
    c.store.async_get_config = AsyncMock(return_value={})
    c.async_evaluate_skip_conditions = AsyncMock(return_value={"checks": []})
    c.recurring_schedule_manager = Mock()
    c.recurring_schedule_manager.async_get_upcoming_runs = AsyncMock(return_value=[])
    c._project_days_between_to_next_run = Mock()
    c.async_get_cached_zone_estimates = AsyncMock(return_value={})
    c.get_zone_faults = Mock(return_value={})
    c.get_active_runs = Mock(return_value={})

    outlook = await c.async_get_irrigation_outlook()

    assert outlook["zone_skips"] == {
        "2": {
            "reason": const.SKIP_REASON_SOIL_MOISTURE,
            "observed": 52.0,
            "threshold": 50.0,
            "entity_id": "sensor.s",
            "timestamp": c.get_zone_skips()[2]["timestamp"],
        }
    }
