"""Test the Irrigation Plus panel registration."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.irrigation_plus.const import (
    CARD_URL,
    DOMAIN,
    FULL_CARD_URL,
    LANG_URL,
    LEGACY_ALIAS_URL,
    LEGACY_CARD_URL,
    PANEL_ICON,
    PANEL_NAME,
    PANEL_TITLE,
    PANEL_URL,
)
from custom_components.irrigation_plus.panel import async_register_panel, remove_panel


async def _run_in_executor(func, *args):
    """Stand-in for hass.async_add_executor_job on a Mock hass.

    panel.async_register_panel resolves foreign_legacy_install through the
    executor (it stats a directory and reads a manifest, which Home Assistant
    reports as a blocking call on the event loop). A bare Mock returns a Mock,
    which cannot be awaited -- so the double has to model this or every panel
    test fails on the harness rather than on the code.
    """
    return func(*args)


class _FakeResources:
    """Writable Lovelace resource store double.

    Must satisfy the duck-type check in ``panel._writable_resource_store``
    (async_items / async_create_item / async_update_item / loaded) plus
    async_delete_item, which is what separates storage mode from YAML mode.
    """

    def __init__(self, items=None):
        self.loaded = True
        self.items = list(items or [])
        self.created = []
        self.updated = []
        self.deleted = []

    def async_items(self):
        return list(self.items)

    async def async_create_item(self, item):
        self.created.append(item)
        self.items.append({"id": f"new{len(self.items)}", **item})

    async def async_update_item(self, item_id, item):
        self.updated.append((item_id, item))

    async def async_delete_item(self, item_id):
        self.deleted.append(item_id)
        self.items = [i for i in self.items if i.get("id") != item_id]


class TestSmartIrrigationPanel:
    """Test Irrigation Plus panel registration."""

    @pytest.fixture
    def mock_hass(self):
        """Return a mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.config = Mock()
        hass.config.path = Mock(return_value="/config")
        hass.http = Mock()
        hass.http.async_register_static_paths = AsyncMock()
        hass.async_add_executor_job = _run_in_executor
        # No Lovelace store by default → card falls back to add_extra_js_url.
        hass.data = {}
        return hass

    async def test_async_register_panel(self, mock_hass):
        """Test panel registration."""
        with (
            patch(
                "custom_components.irrigation_plus.panel.panel_custom.async_register_panel"
            ) as mock_register,
            patch(
                "custom_components.irrigation_plus.panel.frontend.add_extra_js_url"
            ) as mock_extra_js,
        ):
            await async_register_panel(mock_hass)

            # Verify static path registration
            mock_hass.http.async_register_static_paths.assert_called_once()

            # No writable Lovelace resource store on the mock hass, so both the
            # card bundle and the pre-#120 compatibility shim fall back to
            # add_extra_js_url (each with a cache-bust query).
            urls = [c.args[1].split("?")[0] for c in mock_extra_js.call_args_list]
            assert urls == [CARD_URL, LEGACY_ALIAS_URL]
            assert all(c.args[0] is mock_hass for c in mock_extra_js.call_args_list)

            # Verify panel registration
            mock_register.assert_called_once()
            call_args = mock_register.call_args

            assert call_args[0][0] == mock_hass  # First positional arg is hass
            assert call_args[1]["webcomponent_name"] == PANEL_NAME
            assert call_args[1]["frontend_url_path"] == DOMAIN
            assert call_args[1]["module_url"].split("?")[0] == PANEL_URL
            assert call_args[1]["sidebar_title"] == PANEL_TITLE
            assert call_args[1]["sidebar_icon"] == PANEL_ICON
            assert call_args[1]["require_admin"] is True
            assert call_args[1]["config"] == {}

    async def test_card_registered_as_lovelace_resource(self, mock_hass):
        """Storage-mode dashboards get a real Lovelace resource (awaited by HA),
        not add_extra_js_url which races the card render."""

        # The code no longer checks the class NAME (a private-API detail that
        # would fail closed into the racy add_extra_js_url path if HA renamed
        # it) — it checks for the MUTATORS only the storage-backed collection
        # has. So this double must mirror that capability surface; see
        # test_review_hardening.TestLovelaceCollectionShape, which pins it
        # against the real HA classes.
        class ResourceStorageCollection:
            def __init__(self):
                self.loaded = True
                self.created = []
                self.updated = []

            def async_items(self):
                return []

            async def async_create_item(self, item):
                self.created.append(item)

            async def async_update_item(self, item_id, item):
                self.updated.append((item_id, item))

        resources = ResourceStorageCollection()
        mock_hass.data = {"lovelace": Mock(resources=resources)}

        with (
            patch(
                "custom_components.irrigation_plus.panel.panel_custom.async_register_panel"
            ),
            patch(
                "custom_components.irrigation_plus.panel.frontend.add_extra_js_url"
            ) as mock_extra_js,
        ):
            await async_register_panel(mock_hass)

            # The card and the pre-#120 compatibility shim are both registered
            # as module resources, deduped by base URL.
            by_url = {i["url"].split("?")[0]: i for i in resources.created}
            assert set(by_url) == {CARD_URL, LEGACY_ALIAS_URL}
            assert all(i["res_type"] == "module" for i in resources.created)
            # ...and the racy fallback is NOT used.
            mock_extra_js.assert_not_called()

    async def test_async_register_panel_static_path_config(self, mock_hass):
        """Test panel static paths: panel bundle, card stub, card impl, langs."""
        with (
            patch(
                "custom_components.irrigation_plus.panel.panel_custom.async_register_panel"
            ),
            patch("custom_components.irrigation_plus.panel.frontend.add_extra_js_url"),
        ):
            await async_register_panel(mock_hass)

            # The panel bundle, the tiny card stub, the lazy card impl and the
            # per-language translation JSON are all served.
            call_args = mock_hass.http.async_register_static_paths.call_args[0][0]
            assert len(call_args) == 5

            by_url = {c.url_path: c for c in call_args}
            assert set(by_url) == {
                PANEL_URL,
                CARD_URL,
                FULL_CARD_URL,
                LEGACY_ALIAS_URL,
                LANG_URL,
            }
            assert by_url[PANEL_URL].cache_headers is False
            assert "frontend/dist/irrigation-plus.js" in str(by_url[PANEL_URL].path)
            assert "frontend/dist/irrigation-plus-card.js" in str(by_url[CARD_URL].path)
            assert "frontend/dist/irrigation-plus-card-impl.js" in str(
                by_url[FULL_CARD_URL].path
            )
            assert "frontend/localize/languages" in str(by_url[LANG_URL].path)

    def test_remove_panel(self, mock_hass):
        """Test panel removal."""
        with patch(
            "custom_components.irrigation_plus.panel.frontend.async_remove_panel"
        ) as mock_remove:
            remove_panel(mock_hass)

            mock_remove.assert_called_once_with(mock_hass, DOMAIN)

    async def test_panel_path_construction(self, mock_hass):
        """Test that panel path is constructed correctly."""
        mock_hass.config.path.return_value = "/test/config"

        with (
            patch(
                "custom_components.irrigation_plus.panel.panel_custom.async_register_panel"
            ),
            patch("custom_components.irrigation_plus.panel.frontend.add_extra_js_url"),
        ):
            await async_register_panel(mock_hass)

            # Verify config.path was called with correct argument
            mock_hass.config.path.assert_called_with("custom_components")

            # Verify static path registration was called
            mock_hass.http.async_register_static_paths.assert_called_once()


class TestLegacyCardAlias:
    """The pre-#120 card tag is only claimed where nobody else owns it.

    Claiming `smart-irrigation-zones-card` unconditionally would recreate the
    exact collision the rename removes: whichever bundle loads second silently
    loses, and a user's card renders the other project's code with no error.
    """

    @pytest.fixture
    def mock_hass(self):
        hass = Mock(spec=HomeAssistant)
        hass.config = Mock()
        hass.config.path = Mock(return_value="/config")
        hass.http = Mock()
        hass.http.async_register_static_paths = AsyncMock()
        hass.async_add_executor_job = _run_in_executor
        hass.data = {}
        return hass

    async def _register(self, mock_hass, *, foreign):
        resources = _FakeResources()
        mock_hass.data = {"lovelace": SimpleNamespace(resources=resources)}
        with (
            patch(
                "custom_components.irrigation_plus.panel.panel_custom.async_register_panel"
            ),
            patch("custom_components.irrigation_plus.panel.frontend.add_extra_js_url"),
            patch(
                "custom_components.irrigation_plus.panel.foreign_legacy_install",
                return_value=foreign,
            ),
        ):
            await async_register_panel(mock_hass)
        return resources

    async def test_alias_registered_when_nobody_else_owns_the_domain(self, mock_hass):
        resources = await self._register(mock_hass, foreign=False)
        urls = {i["url"].split("?")[0] for i in resources.created}
        assert LEGACY_ALIAS_URL in urls

    async def test_alias_withheld_when_another_project_owns_the_domain(self, mock_hass):
        resources = await self._register(mock_hass, foreign=True)
        urls = {i["url"].split("?")[0] for i in resources.created}
        assert LEGACY_ALIAS_URL not in urls
        # ...but our own card is still registered.
        assert CARD_URL in urls

    async def test_stale_legacy_resource_is_removed_only_when_safe(self, mock_hass):
        """A pre-#120 release left a resource pointing at its own static path.

        Nothing serves it after the rename, so it 404s on every dashboard load
        for ever -- but it must not be touched if another project now owns that
        path.
        """
        for foreign, expected in ((False, True), (True, False)):
            resources = _FakeResources(
                items=[{"id": "r1", "url": f"{LEGACY_CARD_URL}?v=1"}]
            )
            mock_hass.data = {"lovelace": SimpleNamespace(resources=resources)}
            with (
                patch(
                    "custom_components.irrigation_plus.panel.panel_custom.async_register_panel"
                ),
                patch(
                    "custom_components.irrigation_plus.panel.frontend.add_extra_js_url"
                ),
                patch(
                    "custom_components.irrigation_plus.panel.foreign_legacy_install",
                    return_value=foreign,
                ),
            ):
                await async_register_panel(mock_hass)
            assert ("r1" in resources.deleted) is expected
