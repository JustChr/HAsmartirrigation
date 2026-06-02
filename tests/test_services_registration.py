"""Tests for the service registration extracted into services.py (Phase C1).

These validate the *wiring* (the main risk of moving handlers onto a mixin and
relocating async_register_services): every HA service must register to a handler
that actually exists on the coordinator. Using MagicMock(spec=...) makes the
registration raise AttributeError if a handler went missing in the move.
"""

from unittest.mock import MagicMock

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.services import (
    ServiceHandlersMixin,
    async_register_services,
)


def test_coordinator_inherits_service_mixin():
    """The coordinator must inherit the extracted handler mixin."""
    assert issubclass(SmartIrrigationCoordinator, ServiceHandlersMixin)


def test_register_services_wires_all_handlers_to_real_methods():
    """async_register_services registers every service to an existing handler.

    coordinator is spec'd against the real class, so referencing a handler that
    no longer exists (e.g. dropped during the extraction) raises AttributeError.
    """
    coordinator = MagicMock(spec=SmartIrrigationCoordinator)
    hass = MagicMock()
    calls = []
    hass.services.async_register = lambda domain, service, handler: calls.append(
        (domain, service, handler)
    )
    hass.data = {const.DOMAIN: {"coordinator": coordinator}}

    async_register_services(hass)

    # 20 unique handlers, a few services share handle_set_zone -> >= 20 registrations.
    assert len(calls) >= 20
    # every registration is for our domain
    assert all(domain == const.DOMAIN for domain, _service, _handler in calls)
    # no duplicate (domain, service) registrations
    services = [service for _domain, service, _handler in calls]
    assert len(services) == len(set(services))


def test_all_handler_methods_present_on_mixin():
    """Every handler referenced by the registration exists on the mixin."""
    expected_handlers = [
        "handle_calculate_all_zones",
        "handle_calculate_zone",
        "handle_update_all_zones",
        "handle_update_zone",
        "handle_reset_bucket",
        "handle_reset_all_buckets",
        "handle_set_all_buckets",
        "handle_set_zone",
        "handle_set_all_multipliers",
        "handle_clear_weatherdata",
        "handle_generate_watering_calendar",
        "handle_create_recurring_schedule",
        "handle_update_recurring_schedule",
        "handle_delete_recurring_schedule",
        "handle_create_seasonal_adjustment",
        "handle_update_seasonal_adjustment",
        "handle_delete_seasonal_adjustment",
        "handle_sync_with_irrigation_unlimited",
        "handle_send_zone_data_to_iu",
        "handle_get_iu_schedule_status",
    ]
    for name in expected_handlers:
        assert callable(getattr(ServiceHandlersMixin, name)), name
