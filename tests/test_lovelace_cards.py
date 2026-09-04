"""Tests for finding and repointing pre-#120 zones cards (#120 step 4)."""

from types import SimpleNamespace

from custom_components.irrigation_plus.lovelace_cards import (
    CARD_TYPE,
    LEGACY_CARD_TYPE,
    async_count_legacy_cards,
    async_rewrite_legacy_cards,
    count_legacy_cards,
    rewrite_legacy_cards,
)


def _view(*cards):
    return {"views": [{"title": "Home", "cards": list(cards)}]}


class _Dashboard:
    """Storage-mode dashboard double."""

    def __init__(self, config, writable=True):
        self.config = config
        self.writable = writable
        self.saved = None

    async def async_load(self, force):
        if self.config is None:
            raise RuntimeError("ConfigNotFound")
        return self.config

    async def async_save(self, config):
        if not self.writable:
            raise RuntimeError("Not supported")  # what YAML mode does
        self.saved = config


def _hass(dashboards):
    return SimpleNamespace(
        data={"lovelace": SimpleNamespace(dashboards=dashboards)},
    )


class TestCounting:
    def test_finds_a_top_level_card(self):
        assert count_legacy_cards(_view({"type": LEGACY_CARD_TYPE})) == 1

    def test_finds_cards_nested_in_stacks_and_conditionals(self):
        # A dashboard is under no obligation to be shallow; cards nest inside
        # stacks, grids and conditionals.
        config = _view(
            {
                "type": "vertical-stack",
                "cards": [
                    {"type": "horizontal-stack", "cards": [{"type": LEGACY_CARD_TYPE}]},
                    {"type": "conditional", "card": {"type": LEGACY_CARD_TYPE}},
                ],
            }
        )
        assert count_legacy_cards(config) == 2

    def test_ignores_the_current_card_type(self):
        assert count_legacy_cards(_view({"type": CARD_TYPE})) == 0

    def test_ignores_other_cards(self):
        assert count_legacy_cards(_view({"type": "custom:something-else"})) == 0

    def test_empty_config(self):
        assert count_legacy_cards({}) == 0


class TestRewriting:
    def test_repoints_the_type_and_leaves_everything_else(self):
        config = _view({"type": LEGACY_CARD_TYPE, "title": "Zones", "columns": 2})
        new, count = rewrite_legacy_cards(config)
        card = new["views"][0]["cards"][0]
        assert (count, card["type"]) == (1, CARD_TYPE)
        assert card["title"] == "Zones" and card["columns"] == 2

    def test_does_not_mutate_the_original(self):
        # async_load may hand back Lovelace's own cached object; editing it in
        # place would change what other consumers see even if the save fails.
        config = _view({"type": LEGACY_CARD_TYPE})
        rewrite_legacy_cards(config)
        assert config["views"][0]["cards"][0]["type"] == LEGACY_CARD_TYPE

    def test_only_rewrites_the_type_key(self):
        # A card whose *title* happens to be the legacy type must be left alone.
        config = _view({"type": "markdown", "title": LEGACY_CARD_TYPE})
        new, count = rewrite_legacy_cards(config)
        assert count == 0
        assert new["views"][0]["cards"][0]["title"] == LEGACY_CARD_TYPE


class TestAcrossDashboards:
    async def test_counts_every_dashboard(self):
        hass = _hass(
            {
                None: _Dashboard(_view({"type": LEGACY_CARD_TYPE})),
                "garden": _Dashboard(
                    _view({"type": LEGACY_CARD_TYPE}, {"type": LEGACY_CARD_TYPE})
                ),
            }
        )
        assert await async_count_legacy_cards(hass) == 3

    async def test_an_unloadable_dashboard_is_skipped(self):
        hass = _hass(
            {None: _Dashboard(None), "b": _Dashboard(_view({"type": LEGACY_CARD_TYPE}))}
        )
        assert await async_count_legacy_cards(hass) == 1

    async def test_rewrites_and_saves_only_affected_dashboards(self):
        touched = _Dashboard(_view({"type": LEGACY_CARD_TYPE}))
        untouched = _Dashboard(_view({"type": CARD_TYPE}))
        hass = _hass({None: touched, "other": untouched})

        changed, skipped = await async_rewrite_legacy_cards(hass)
        assert (changed, skipped) == (1, [])
        assert touched.saved["views"][0]["cards"][0]["type"] == CARD_TYPE
        # A dashboard with nothing to change is never written at all.
        assert untouched.saved is None

    async def test_yaml_dashboards_are_reported_not_silently_dropped(self):
        """YAML mode raises on save; claiming a clean sweep would be a lie."""
        yaml_mode = _Dashboard(_view({"type": LEGACY_CARD_TYPE}), writable=False)
        storage = _Dashboard(_view({"type": LEGACY_CARD_TYPE}))
        hass = _hass({"yaml": yaml_mode, None: storage})

        changed, skipped = await async_rewrite_legacy_cards(hass)
        assert changed == 1
        assert skipped == ["yaml"]

    async def test_no_lovelace_data_is_a_no_op(self):
        hass = SimpleNamespace(data={})
        assert await async_count_legacy_cards(hass) == 0
        assert await async_rewrite_legacy_cards(hass) == (0, [])
