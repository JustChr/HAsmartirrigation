"""Tests for the #120 history / statistics / device-area migration (step 3b).

The mapping is the part that can silently be wrong: a zone renamed after its
entities were created keeps the ORIGINAL slug in its entity ids, while a fresh
install takes the CURRENT one. A naive prefix swap sends that zone's history to
an id nothing will ever produce.
"""

from types import SimpleNamespace

from homeassistant.util import slugify

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.migrate_domain import (
    _zone_id_from_unique_id,
    plan_device_area_moves,
    plan_entity_id_map,
)

L = const.LEGACY_DOMAIN
D = const.DOMAIN


def _ent(entity_id, unique_id, platform=L):
    return SimpleNamespace(entity_id=entity_id, unique_id=unique_id, platform=platform)


def _map(entries, zones=None):
    return plan_entity_id_map(entries, zones or {}, slugify)


class TestZoneIdParsing:
    def test_per_zone_unique_id(self):
        assert _zone_id_from_unique_id(f"{L}_3_bucket") == "3"

    def test_suffix_containing_underscores(self):
        assert _zone_id_from_unique_id(f"{L}_12_last_water_used") == "12"

    def test_hub_entity_has_no_zone(self):
        assert _zone_id_from_unique_id(f"{L}_irrigation_needed") is None
        assert _zone_id_from_unique_id(f"{L}_rain_delay_until") is None

    def test_foreign_unique_id(self):
        assert _zone_id_from_unique_id("something_else_1_bucket") is None


class TestEntityIdMap:
    def test_swaps_the_domain_prefix(self):
        m = _map([_ent(f"sensor.{L}_lawn_bucket", f"{L}_1_bucket")])
        assert m == {f"sensor.{L}_lawn_bucket": f"sensor.{D}_lawn_bucket"}

    def test_maps_hub_entities_too(self):
        entries = [
            _ent(f"binary_sensor.{L}_problem", f"{L}_problem"),
            _ent(f"datetime.{L}_rain_delay", f"{L}_rain_delay_until"),
        ]
        m = _map(entries)
        assert m[f"binary_sensor.{L}_problem"] == f"binary_sensor.{D}_problem"
        # entity_id and unique_id disagree for this one; the map keys off the
        # entity_id, so the mismatch must not matter.
        assert m[f"datetime.{L}_rain_delay"] == f"datetime.{D}_rain_delay"

    def test_a_renamed_zone_maps_onto_its_CURRENT_slug(self):
        """The case a naive prefix swap gets wrong.

        The zone was "Lawn" when its entities were created and is "Front
        Garden" now. Old ids still say `lawn`; our fresh entities will say
        `front_garden`.
        """
        entries = [
            _ent(f"sensor.{L}_lawn", f"{L}_1_duration"),
            _ent(f"sensor.{L}_lawn_bucket", f"{L}_1_bucket"),
            _ent(f"number.{L}_lawn_multiplier", f"{L}_1_multiplier"),
        ]
        m = _map(entries, {"1": {const.ZONE_NAME: "Front Garden"}})
        assert m[f"sensor.{L}_lawn"] == f"sensor.{D}_front_garden"
        assert m[f"sensor.{L}_lawn_bucket"] == f"sensor.{D}_front_garden_bucket"
        assert m[f"number.{L}_lawn_multiplier"] == f"number.{D}_front_garden_multiplier"

    def test_unrenamed_zone_is_unaffected_by_the_slug_logic(self):
        entries = [
            _ent(f"sensor.{L}_lawn", f"{L}_1_duration"),
            _ent(f"sensor.{L}_lawn_et", f"{L}_1_et"),
        ]
        m = _map(entries, {"1": {const.ZONE_NAME: "Lawn"}})
        assert m[f"sensor.{L}_lawn_et"] == f"sensor.{D}_lawn_et"

    def test_falls_back_to_prefix_swap_without_a_duration_entity(self):
        # No duration sensor => the original slug is unrecoverable, so the
        # prefix swap is the best available answer rather than a guess.
        m = _map(
            [_ent(f"sensor.{L}_lawn_bucket", f"{L}_1_bucket")],
            {"1": {const.ZONE_NAME: "Front Garden"}},
        )
        assert m[f"sensor.{L}_lawn_bucket"] == f"sensor.{D}_lawn_bucket"

    def test_user_renamed_entity_ids_are_skipped_not_guessed(self):
        entries = [
            _ent("sensor.my_own_name", f"{L}_1_bucket"),
            _ent(f"sensor.{L}_lawn_et", f"{L}_1_et"),
        ]
        m = _map(entries)
        assert "sensor.my_own_name" not in m
        assert f"sensor.{L}_lawn_et" in m

    def test_only_maps_the_legacy_platforms_entities(self):
        """Another integration can own an id that LOOKS like ours.

        A plain "does the object id start with the prefix" test is not enough:
        someone else's entity can be named that way, and renaming it would move
        history out from under a working integration. The platform is the only
        thing that actually says whose entity it is.
        """
        entries = [
            # Same shape as ours, different owner -- must not be touched.
            _ent(f"sensor.{L}_lawn_bucket", f"{L}_1_bucket", platform="other"),
            _ent(f"sensor.{L}_lawn_et", f"{L}_1_et"),
        ]
        assert list(_map(entries)) == [f"sensor.{L}_lawn_et"]

    def test_zone_lookup_tolerates_int_keys_and_attrs_objects(self):
        entries = [
            _ent(f"sensor.{L}_lawn", f"{L}_1_duration"),
            _ent(f"sensor.{L}_lawn_bucket", f"{L}_1_bucket"),
        ]
        # int-keyed dict (store.zones is keyed by int)
        m = _map(entries, {1: {const.ZONE_NAME: "Back"}})
        assert m[f"sensor.{L}_lawn_bucket"] == f"sensor.{D}_back_bucket"
        # attrs-style object rather than a dict
        m = _map(entries, {"1": SimpleNamespace(**{const.ZONE_NAME: "Back"})})
        assert m[f"sensor.{L}_lawn_bucket"] == f"sensor.{D}_back_bucket"

    def test_nothing_to_do_on_a_clean_install(self):
        assert _map([]) == {}


class TestDeviceAreas:
    def _dev(self, identifiers, area_id=None, device_id=None):
        return SimpleNamespace(
            identifiers=set(identifiers),
            area_id=area_id,
            id=device_id or str(identifiers),
        )

    def _run(self, devices):
        moves = plan_device_area_moves(devices)
        return len(moves), {k: {"area_id": v} for k, v in moves.items()}

    def test_carries_the_area_onto_the_replacement_device(self):
        # The identifier embeds the config entry's unique id, which the rename
        # changes too -- so matching must key on the trailing _zone_<id> only.
        old = self._dev(
            {(L, "Smart Irrigation_zone_1")}, area_id="garden", device_id="o"
        )
        new = self._dev({(D, "Irrigation Plus_zone_1")}, device_id="n")
        moved, updated = self._run([old, new])
        assert moved == 1
        assert updated["n"] == {"area_id": "garden"}

    def test_never_overwrites_an_area_the_user_already_set(self):
        old = self._dev({(L, "x_zone_1")}, area_id="garden", device_id="o")
        new = self._dev({(D, "y_zone_1")}, area_id="patio", device_id="n")
        moved, updated = self._run([old, new])
        assert moved == 0
        assert updated == {}

    def test_unmatched_zones_are_left_alone(self):
        old = self._dev({(L, "x_zone_1")}, area_id="garden", device_id="o")
        new = self._dev({(D, "y_zone_9")}, device_id="n")
        moved, _ = self._run([old, new])
        assert moved == 0

    def test_no_legacy_devices_is_a_no_op(self):
        new = self._dev({(D, "y_zone_1")}, device_id="n")
        moved, updated = self._run([new])
        assert (moved, updated) == (0, {})

    def test_legacy_device_without_an_area_contributes_nothing(self):
        old = self._dev({(L, "x_zone_1")}, device_id="o")
        new = self._dev({(D, "y_zone_1")}, device_id="n")
        moved, _ = self._run([old, new])
        assert moved == 0
