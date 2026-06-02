"""Fixtures for testing."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add the repository root to Python path so custom component imports work
repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


# Patch problematic Home Assistant modules before any imports
def patch_homeassistant_modules():
    """Patch Home Assistant modules that cause import issues."""
    # Create mock modules for problematic HA components
    mock_modules = [
        "homeassistant.helpers",
        "homeassistant.helpers.device_registry",
        "homeassistant.helpers.entity_registry",
        "homeassistant.components.frontend",
        "homeassistant.components.websocket_api",
        "homeassistant.components.http",
        "homeassistant.components.logger",
        "homeassistant.components.system_log",
    ]

    for module_name in mock_modules:
        if module_name not in sys.modules:
            sys.modules[module_name] = MagicMock()


# Apply patches early
patch_homeassistant_modules()


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_hass():
    """Return a mock Home Assistant instance."""
    hass = Mock()
    hass.config = Mock()
    hass.config.config_dir = "/tmp/test_config"
    hass.config.latitude = 52.379189
    hass.config.longitude = 4.899431
    hass.config.elevation = 0
    hass.config.units = Mock()
    hass.config.time_zone = "UTC"

    hass.data = {}
    hass.states = Mock()
    hass.states.async_set = AsyncMock()
    hass.states.get = Mock(return_value=None)

    hass.services = Mock()
    hass.services.async_call = AsyncMock()

    hass.bus = Mock()
    hass.bus.async_listen = Mock()
    hass.bus.async_fire = AsyncMock()

    hass.async_add_executor_job = AsyncMock()
    hass.async_create_task = AsyncMock()

    return hass


@pytest.fixture
def mock_entry():
    """Return a mock config entry."""
    from homeassistant.const import CONF_ELEVATION, CONF_LATITUDE, CONF_LONGITUDE

    from custom_components.smart_irrigation import const
    from tests.common import MockConfigEntry

    return MockConfigEntry(
        domain=const.DOMAIN,
        title=const.NAME,
        data={
            const.CONF_INSTANCE_NAME: "Test Smart Irrigation",
            const.CONF_USE_WEATHER_SERVICE: False,
            CONF_LATITUDE: 52.379189,
            CONF_LONGITUDE: 4.899431,
            CONF_ELEVATION: 0,
        },
        entry_id="test_entry_id",
        unique_id="test_unique_id",
    )


@pytest.fixture
def mock_store():
    """Return a mock store."""
    from custom_components.smart_irrigation import const

    store = Mock()
    store.async_get_config = AsyncMock(return_value={})
    store.async_get_all_zones = AsyncMock(return_value=[])
    store.async_get_zone = AsyncMock(return_value=None)
    store.async_save_zone = AsyncMock()
    store.async_delete_zone = AsyncMock()
    store.set_up_factory_defaults = AsyncMock()
    store.get_mappings = Mock(return_value={})
    store.get_modules = Mock(return_value={})
    store.get_zones = Mock(return_value={})
    # Add get_config method that returns a sync dict - not a coroutine.
    # The coordinator __init__ indexes all three auto-*-enabled keys directly,
    # so they must all be present or construction raises KeyError.
    default_config = {
        const.CONF_AUTO_UPDATE_ENABLED: False,
        const.CONF_AUTO_CALC_ENABLED: False,
        const.CONF_AUTO_CLEAR_ENABLED: False,
        const.CONF_USE_WEATHER_SERVICE: False,
    }
    store.get_config = Mock(return_value=default_config)
    return store


@pytest.fixture
def mock_session():
    """Return a mock aiohttp client session.

    The coordinator takes a session argument; it is not used during __init__
    (weather clients are built from API keys), so a bare AsyncMock suffices.
    """
    return AsyncMock()


@pytest.fixture
def mock_coordinator(mock_store):
    """Return a mock coordinator."""
    coordinator = Mock()
    coordinator.id = "test_coordinator_id"
    coordinator.store = mock_store
    coordinator.use_weather_service = False
    coordinator.update_subscriptions = AsyncMock()
    coordinator.async_unload = AsyncMock()
    coordinator.async_delete_config = AsyncMock()
    coordinator.setup_SmartIrrigation_entities = AsyncMock()

    # Mock service handlers
    coordinator.handle_reset_bucket = AsyncMock()
    coordinator.handle_reset_all_buckets = AsyncMock()

    # Mock unsubscribe methods
    coordinator.unsubscribe_calc_updates = Mock()
    coordinator.unsubscribe_hourly_updates = Mock()
    coordinator.unsubscribe_minutely_updates = Mock()
    coordinator.unsubscribe_daily_updates = Mock()
    coordinator.unsubscribe_sun_updates = Mock()

    return coordinator


# ---------------------------------------------------------------------------
# Fixtures merged from the former custom_components/smart_irrigation/tests
# conftest during the test-tree consolidation. Imports are kept lazy (inside
# the fixtures) so that importing this conftest never requires the
# pytest-homeassistant-custom-component plugin at collection time — that keeps
# the standalone tests/unit suite runnable without the full HA test stack.
# ---------------------------------------------------------------------------


@pytest.fixture
def snapshot(snapshot):
    """Return snapshot assertion fixture with the Home Assistant extension."""
    from pytest_homeassistant_custom_component.syrupy import (
        HomeAssistantSnapshotExtension,
    )

    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture
def mock_setup_entry():
    """Override async_setup_entry."""
    with patch(
        "custom_components.smart_irrigation.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    from homeassistant.const import CONF_ELEVATION, CONF_LATITUDE, CONF_LONGITUDE

    from custom_components.smart_irrigation import const
    from tests.common import MockConfigEntry

    return MockConfigEntry(
        domain=const.DOMAIN,
        title=const.NAME,
        data={
            const.CONF_INSTANCE_NAME: "Test Smart Irrigation",
            const.CONF_USE_WEATHER_SERVICE: False,
            CONF_LATITUDE: 52.379189,
            CONF_LONGITUDE: 4.899431,
            CONF_ELEVATION: 0,
        },
        entry_id="test_entry_id",
        unique_id="test_unique_id",
    )


@pytest.fixture
def mock_config_entry_with_weather():
    """Return a mock config entry with weather service enabled."""
    from homeassistant.const import CONF_ELEVATION, CONF_LATITUDE, CONF_LONGITUDE

    from custom_components.smart_irrigation import const
    from tests.common import MockConfigEntry

    return MockConfigEntry(
        domain=const.DOMAIN,
        title=const.NAME,
        data={
            const.CONF_INSTANCE_NAME: "Test Smart Irrigation",
            const.CONF_USE_WEATHER_SERVICE: True,
            const.CONF_WEATHER_SERVICE: const.CONF_WEATHER_SERVICE_OWM,
            const.CONF_WEATHER_SERVICE_API_KEY: "validate_api_key",
            CONF_LATITUDE: 52.379189,
            CONF_LONGITUDE: 4.899431,
            CONF_ELEVATION: 0,
        },
        entry_id="test_entry_id",
        unique_id="test_unique_id",
    )


# Alias kept for tests that request the longer fixture name.
@pytest.fixture
def mock_weather_config_entry(mock_config_entry_with_weather):
    """Return a mock config entry with weather service enabled."""
    return mock_config_entry_with_weather


@pytest.fixture
def mock_zone_config():
    """Return a sample zone configuration."""
    return {
        "name": "Test Zone",
        "bucket": 10.5,
        "state": "normal",
        "multiplier": 1.0,
        "switched": False,
        "enabled": True,
        "zone_size": 100,
        "throughput": 15,
        "lead_time": 0,
        "maximum_duration": 3600,
        "ignore_sensors": False,
        "show_units": True,
        "run_freq": 1,
        "calculated_seconds": 0,
        "calculated_minutes": 0,
        "delta": 0,
        "description": "Test zone description",
        "old_bucket": 10.0,
        "sensors": [],
        "bucket_throughput": 0,
        "expiry": None,
        "slope": 1,
        "base": 0,
        "peak": 100,
        "rainblock": False,
        "rainblock_start": None,
        "rainblock_end": None,
        "last_modified": None,
        "zone_mapping": {},
        "reference_evapotranspiration": 0,
        "evapotranspiration": 0,
        "precipitation": 0,
    }
