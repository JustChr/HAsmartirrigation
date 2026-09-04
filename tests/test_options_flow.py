"""Test the Irrigation Plus options flow.

Weather + location config moved to the integration's panel (single source of
truth), so the options flow no longer configures anything — it just points the
user to the panel via an abort.
"""

from unittest.mock import Mock

from homeassistant.data_entry_flow import FlowResultType

from custom_components.irrigation_plus.options_flow import (
    SmartIrrigationOptionsFlowHandler,
)
from tests.common import MockConfigEntry


def _make_flow():
    entry = MockConfigEntry(
        domain="irrigation_plus",
        title="Irrigation Plus",
        data={},
        options={},
        entry_id="test_entry_id",
    )
    flow = SmartIrrigationOptionsFlowHandler(entry)
    flow.hass = Mock()
    return flow


async def test_options_flow_aborts_to_panel():
    """The options flow points the user to the panel instead of configuring."""
    flow = _make_flow()

    result = await flow.async_step_init()

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "configure_in_panel"


async def test_options_flow_aborts_with_user_input_too():
    """Even if input is somehow supplied, the step still aborts to the panel."""
    flow = _make_flow()

    result = await flow.async_step_init({"anything": True})

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "configure_in_panel"
