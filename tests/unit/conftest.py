"""Local conftest for standalone unit tests.

Overrides the autouse fixture from tests/conftest.py that requires
pytest-homeassistant-custom-component (only available in CI).
"""

import pytest


@pytest.fixture
def enable_custom_integrations():
    """No-op override — not needed for standalone unit tests."""
    return None
