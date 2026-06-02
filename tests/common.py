"""Common test utilities for Smart Irrigation tests."""

from homeassistant.data_entry_flow import FlowResultType

# Re-export the plugin's MockConfigEntry, which is kept in sync with Home
# Assistant's ConfigEntry signature. The previous hand-rolled subclass broke
# every time HA added a required kwarg (subentries_data, discovery_keys,
# minor_version, ...). Importing the canonical helper avoids that churn.
from pytest_homeassistant_custom_component.common import MockConfigEntry  # noqa: F401


def mock_flow_result(
    result_type: FlowResultType = FlowResultType.CREATE_ENTRY, **kwargs
):
    """Create a mock flow result."""
    return {
        "type": result_type,
        "title": kwargs.get("title", "Test"),
        "data": kwargs.get("data", {}),
        "errors": kwargs.get("errors", {}),
        "description_placeholders": kwargs.get("description_placeholders", {}),
    }
