"""Cached calc-module resolution (CalculationMixin.getModuleInstanceByID).

Resolving a module scans and re-imports the calc-module directory over an
executor hop. The live estimate resolves a zone's module every minute for every
zone, so the resolved instance is cached.

The cache itself is internal, but "a module whose configuration changed is not
served stale" is an externally observable claim and is pinned here — together
with the release path (the existing ``_config_updated`` fan-out) and the promise
that a repeat call does not re-scan.
"""

from unittest.mock import Mock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const


def _make_coordinator(module_record):
    """A coordinator with only what getModuleInstanceByID touches.

    ``__new__`` skips the heavy __init__ (timers, dispatchers, weather clients),
    as the other calculation tests do. ``scans`` counts executor jobs, which is
    one per directory scan.
    """
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)

    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.config.language = "en"

    scans = []

    async def run_executor(func, *args):
        scans.append(func.__name__)
        return func(*args)

    hass.async_add_executor_job = run_executor
    coord.hass = hass

    store = Mock()
    # The store hands out a fresh dict per call (attr.asdict), so the cache can
    # never be holding a reference the caller mutates underneath it.
    store.get_module = Mock(side_effect=lambda _id: dict(module_record))
    coord.store = store
    coord.scans = scans
    return coord


def _passthrough(**overrides):
    record = {const.MODULE_NAME: "Passthrough", "description": "", "config": {}}
    record.update(overrides)
    return record


def _static(delta):
    """Static is the module whose one config value is directly readable back."""
    return {const.MODULE_NAME: "Static", "description": "", "config": {"delta": delta}}


async def test_resolved_once_and_reused():
    """Repeat calls hand back the same instance without re-scanning."""
    coord = _make_coordinator(_passthrough())

    first = await coord.getModuleInstanceByID(10)
    second = await coord.getModuleInstanceByID(10)
    third = await coord.getModuleInstanceByID(10)

    assert first is not None
    assert second is first
    assert third is first
    assert coord.scans == ["loadModules"]


async def test_changed_module_config_is_not_served_stale():
    """A config edit is reflected even if no invalidation signal reached us.

    ``async_update_module_config`` does dispatch ``_config_updated``, but a
    direct store write or a migration rewrite does not, and a module serving the
    previous configuration silently changes what the zone waters with.
    """
    record = _static(1.0)
    coord = _make_coordinator(record)

    first = await coord.getModuleInstanceByID(10)
    assert first.calculate() == 1.0

    record["config"] = {"delta": 2.0}
    second = await coord.getModuleInstanceByID(10)

    assert second is not first
    assert second.calculate() == 2.0
    assert coord.scans == ["loadModules", "loadModules"]


async def test_changed_module_name_is_not_served_stale():
    """Pointing the same module id at a different algorithm rebuilds it."""
    record = _static(1.0)
    coord = _make_coordinator(record)

    first = await coord.getModuleInstanceByID(10)
    assert first.name == "Static"

    record.update(_passthrough())
    second = await coord.getModuleInstanceByID(10)

    assert second.name == "Passthrough"


async def test_config_updated_releases_a_changed_module():
    """The dispatcher handler drops the entry whose stored record moved on."""
    record = _static(1.0)
    coord = _make_coordinator(record)

    first = await coord.getModuleInstanceByID(10)
    assert coord._module_instance_by_id  # noqa: SLF001

    record["config"] = {"delta": 2.0}
    coord.invalidate_module_instances(10)

    assert not coord._module_instance_by_id  # noqa: SLF001
    second = await coord.getModuleInstanceByID(10)
    assert second is not first


async def test_config_updated_keeps_an_unchanged_module():
    """The signal also carries zone and mapping writes, which fire constantly.

    Clearing on every one of those would hand the live estimate back the
    directory scan the cache exists to remove, so an unrelated write must be a
    no-op.
    """
    coord = _make_coordinator(_passthrough())

    first = await coord.getModuleInstanceByID(10)
    coord.invalidate_module_instances(3)  # a zone id, not this module

    assert await coord.getModuleInstanceByID(10) is first
    assert coord.scans == ["loadModules"]


async def test_deleted_module_is_dropped_not_served():
    """Deleting a module dispatches nothing, so the cache must not outlive it."""
    coord = _make_coordinator(_passthrough())

    await coord.getModuleInstanceByID(10)
    coord.store.get_module = Mock(return_value=None)

    assert await coord.getModuleInstanceByID(10) is None
    coord.invalidate_module_instances()
    assert not coord._module_instance_by_id  # noqa: SLF001


async def test_unknown_module_name_is_not_cached():
    """A name with no package on disk keeps re-scanning.

    The next scan is what would pick it up after an integration update landed
    the missing package, so caching the miss would make it permanent.
    """
    coord = _make_coordinator(_passthrough(**{const.MODULE_NAME: "NoSuchModule"}))

    assert await coord.getModuleInstanceByID(10) is None
    assert await coord.getModuleInstanceByID(10) is None
    assert coord.scans == ["loadModules", "loadModules"]


async def test_effective_coordinates_are_applied_to_the_cached_instance():
    """The manual-coordinate override survives caching."""
    coord = _make_coordinator(_passthrough(**{const.MODULE_NAME: "PyETO"}))
    coord._effective_latitude = 12.5  # noqa: SLF001
    coord._effective_elevation = 340  # noqa: SLF001

    first = await coord.getModuleInstanceByID(10)
    assert first._latitude == 12.5  # noqa: SLF001
    assert first._elevation == 340  # noqa: SLF001
    assert (await coord.getModuleInstanceByID(10))._latitude == 12.5  # noqa: SLF001


def test_invalidation_is_wired_to_config_updated():
    """The coordinator subscribes on construction and tears down on unload.

    Anything that subscribes has to unsubscribe, or a reloaded coordinator
    leaves the previous one wired to the dispatcher.
    """
    import inspect

    from custom_components.smart_irrigation import CalculationMixin

    source = inspect.getsource(SmartIrrigationCoordinator.__init__)
    assert "invalidate_module_instances" in source
    assert "self._subscriptions.append" in source
    # async_unload drains _subscriptions, so appending is the teardown.
    unload = inspect.getsource(SmartIrrigationCoordinator.async_unload)
    assert "while self._subscriptions" in unload
    assert hasattr(CalculationMixin, "invalidate_module_instances")


if __name__ == "__main__":
    pytest.main([__file__])
