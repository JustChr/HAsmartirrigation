"""Nothing we own may sit in a namespace the other project also claims (#120).

The rename exists so this integration and the upstream `smart_irrigation` one
can run on the same machine. That only holds if EVERY shared namespace is
namespaced, and the shared namespaces are not obvious from any one file:

* served HTTP paths and the panel URL   -- one aiohttp router
* WebSocket command types               -- one command registry
* event names                           -- one bus
* dispatcher signals                    -- one process
* storage keys                          -- one `.storage` directory
* device identifiers and unique_ids     -- one registry
* custom element tag names              -- ONE browser registry, and Home
  Assistant is a SPA, so opening our panel and then theirs loads both bundles
  into the same document

A collision in any of them is silent. `customElements.define` on a taken name
throws and the rest of the bundle never runs; a duplicate card type renders the
other project's code; a shared storage key means one integration reads a file
the other wrote. None of it produces a message a user would connect to the
cause, which is why this is a test and not a review checklist.

The rule everywhere is DERIVE, never restate -- see the four independent
hardcodings the rename found. These tests assert the derived result, so a future
literal is caught even if it happens to be correct on the day it is written.
"""

import re
from pathlib import Path

import pytest

from custom_components.irrigation_plus import const

_SRC = Path(__file__).resolve().parents[1] / "custom_components" / "irrigation_plus"
_FRONTEND_SRC = _SRC / "frontend" / "src"

# Names that legitimately hold the OLD namespace. Each is a historical fact --
# what pre-#120 releases wrote -- and deriving it from the current domain would
# send the code hunting for something that never existed.
_LEGACY_ALLOWED = {
    "LEGACY_DOMAIN",
    "LEGACY_NAME",
    "LEGACY_PANEL_SLUG",
    "LEGACY_CARD_STATIC_ROOT",
    "LEGACY_CARD_URL",
    # Points at our docs site, whose repo slug is deliberately NOT renamed yet
    # (one variable at a time; HACS tracks repos by id, so it is safe but
    # separate).
    "MIGRATION_GUIDE_URL",
}


def _string_constants():
    for name in dir(const):
        if name.startswith("_"):
            continue
        value = getattr(const, name)
        if isinstance(value, str):
            yield name, value


class TestNoConstantLeaksTheOldNamespace:
    def test_only_explicitly_historical_constants_mention_the_old_domain(self):
        leaked = {
            name: value
            for name, value in _string_constants()
            if name not in _LEGACY_ALLOWED
            and (const.LEGACY_DOMAIN in value or const.LEGACY_PANEL_SLUG in value)
        }
        assert not leaked, (
            f"{sorted(leaked)} still contain the old namespace. Either derive "
            f"them from DOMAIN, or add them to _LEGACY_ALLOWED with a reason "
            f"for why they describe what OLD releases wrote"
        )

    def test_the_allowlist_has_not_gone_stale(self):
        # An allowlist that names constants which no longer exist stops being a
        # decision and becomes clutter that hides the next real entry.
        names = {name for name, _ in _string_constants()}
        assert not _LEGACY_ALLOWED - names, (
            f"_LEGACY_ALLOWED names constants that no longer exist: "
            f"{sorted(_LEGACY_ALLOWED - names)}"
        )


class TestServedPathsAreOurs:
    """Every path we register with aiohttp lives under our own prefix."""

    @pytest.mark.parametrize(
        "name",
        [
            "PANEL_URL",
            "CARD_URL",
            "FULL_CARD_URL",
            "LEGACY_ALIAS_URL",
            "CARD_STATIC_ROOT",
            "LANG_URL",
        ],
    )
    def test_path_is_namespaced(self, name):
        value = getattr(const, name)
        assert const.DOMAIN in value or const.PANEL_SLUG in value, (
            f"{name} = {value} is not under our namespace, so it either "
            f"collides with the other project or serves from a path we do not own"
        )

    def test_the_legacy_alias_is_served_from_OUR_root(self):
        # The compatibility shim keeps pre-rename dashboards working, but it must
        # be served from our static root: /smart_irrigation_card belongs to the
        # other project the moment it is installed.
        assert const.LEGACY_ALIAS_URL.startswith(const.CARD_STATIC_ROOT)
        assert not const.LEGACY_ALIAS_URL.startswith(const.LEGACY_CARD_STATIC_ROOT)

    def test_the_legacy_card_path_is_never_registered(self):
        # It appears only where we CLEAN UP a stale resource a previous release
        # wrote, never where we serve one.
        panel = (_SRC / "panel.py").read_text(encoding="utf-8")
        for line in panel.splitlines():
            if "StaticPathConfig" in line:
                assert "LEGACY_CARD_URL" not in line, (
                    "panel.py registers the pre-rename static path, which the "
                    "other project owns once installed"
                )


class TestRuntimeIdentifiersAreNamespaced:
    def test_storage_key(self):
        from custom_components.irrigation_plus.store import STORAGE_KEY

        assert STORAGE_KEY.startswith(const.DOMAIN)

    def test_migration_store_key(self):
        from custom_components.irrigation_plus.migrate_domain import (
            MIGRATION_STORE_KEY,
        )

        assert MIGRATION_STORE_KEY.startswith(const.DOMAIN)

    def test_the_legacy_backup_is_the_one_file_named_for_the_old_domain(self):
        # Deliberate: it is a copy OF the old file, kept for recovery, and the
        # .bak suffix keeps Home Assistant from loading it as a store.
        from types import SimpleNamespace

        from custom_components.irrigation_plus.migrate_domain import (
            legacy_backup_path,
        )

        hass = SimpleNamespace(
            config=SimpleNamespace(path=lambda *p: "/".join(("cfg",) + p))
        )
        name = legacy_backup_path(hass).name
        assert name.startswith(const.LEGACY_DOMAIN)
        assert name.endswith(".bak")

    def test_the_rename_report_is_namespaced(self):
        # It is written next to configuration.yaml, where every integration's
        # files share one directory.
        from custom_components.irrigation_plus.migrate_domain import (
            RENAME_REPORT_FILENAME,
        )

        assert RENAME_REPORT_FILENAME.startswith(const.DOMAIN)

    def test_blueprints_install_under_our_own_folder(self):
        init = (_SRC / "__init__.py").read_text(encoding="utf-8")
        assert 'hass.config.path("blueprints", "script", const.DOMAIN)' in init, (
            "the bundled blueprints must install to a DOMAIN-named folder, or "
            "they overwrite the other project's copies"
        )


class TestDerivedNotRestated:
    """The literals that caused the original collision must stay derived.

    Upstream's own rename shipped `PANEL_URL = "/api/panel_custom/smart-irrigation"`
    byte-identical to this project's, so their panel served OUR bundle from a
    path they no longer owned. A correct literal today is a wrong literal after
    the next rename.
    """

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("PANEL_SLUG", "irrigation-plus"),
            ("PANEL_URL", "/api/panel_custom/irrigation-plus"),
            ("CARD_STATIC_ROOT", "/irrigation_plus_card"),
            ("LANG_URL", "/irrigation_plus_static/languages"),
        ],
    )
    def test_value_follows_the_domain(self, name, expected):
        assert getattr(const, name) == expected

    def test_the_source_writes_no_literal_for_them(self):
        """Comments are exempt; a `# "irrigation-plus"` note next to the
        derivation is documentation, and the whole point is that the CODE
        computes the value."""
        code = "\n".join(
            line.split("#", 1)[0]
            for line in (_SRC / "const.py").read_text(encoding="utf-8").splitlines()
        )
        for literal in (
            '"/api/panel_custom/irrigation-plus"',
            '"irrigation-plus"',
            '"/irrigation_plus_card"',
        ):
            assert literal not in code, (
                f"const.py restates {literal} instead of deriving it from "
                f"DOMAIN; that is exactly the hardcoding #120 was caused by"
            )


class TestCustomElementTagsAreNamespaced:
    """The browser element registry is global and shared with the whole SPA.

    A `define` on a name another bundle already took throws, and everything
    after it in that bundle never runs -- so a single unnamespaced tag can take
    the entire panel down once both projects are installed.
    """

    _DEFINE = re.compile(
        r"""(?:@customElement\(\s*["']([^"']+)["']|customElements\.define\(\s*["']([^"']+)["'])"""
    )

    def _defined_tags(self):
        tags = set()
        for path in _FRONTEND_SRC.rglob("*.ts"):
            if path.name.endswith(".test.ts"):
                continue
            for match in self._DEFINE.finditer(path.read_text(encoding="utf-8")):
                tags.add(match.group(1) or match.group(2))
        return tags

    def test_every_literal_define_carries_our_prefix(self):
        stray = {
            tag
            for tag in self._defined_tags()
            if not tag.startswith(("ip-", f"{const.PANEL_SLUG}"))
        }
        assert not stray, (
            f"{sorted(stray)} are defined without our prefix. A generic tag "
            f"collides with another integration's bundle in the same document, "
            f"and the loser fails silently"
        )

    def test_the_defines_include_the_panel_and_the_card(self):
        # Guards the regex itself: a pattern that matched nothing would make
        # the test above vacuously pass.
        tags = self._defined_tags()
        assert const.PANEL_SLUG in tags
        assert f"{const.PANEL_SLUG}-zones-card" in tags
        assert len(tags) > 15

    def test_the_only_legacy_tag_is_the_gated_compatibility_shim(self):
        """One file may claim the old tag, and only defensively.

        It is served solely when no foreign `smart_irrigation` integration is
        installed (decided by the BACKEND in panel.py -- load order is not
        something either project can control), and it still refuses to overwrite
        an existing definition.
        """
        shim = _FRONTEND_SRC / "irrigation-plus-card-legacy.ts"
        source = shim.read_text(encoding="utf-8")
        assert f'"{const.LEGACY_PANEL_SLUG}-zones-card"' in source
        assert (
            "customElements.get(LEGACY_TAG)" in source
        ), "the shim must not claim the old tag unconditionally"

        others = [
            path
            for path in _FRONTEND_SRC.rglob("*.ts")
            if path != shim
            and not path.name.endswith(".test.ts")
            and const.LEGACY_PANEL_SLUG in path.read_text(encoding="utf-8")
        ]
        assert not others, (
            f"{[p.name for p in others]} reference the old element namespace; "
            f"only the gated shim may"
        )
