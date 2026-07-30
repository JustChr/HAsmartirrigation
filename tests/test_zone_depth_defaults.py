"""Depth-valued zone defaults must land in the units the zone is STORED in.

`bucket`, `maximum_bucket`, `drainage_rate` and `bucket_threshold` are stored in the
user's display units (mm metric / inches imperial); `calculate_module` converts them to
mm for the maths and back, and the zone UI labels each with
`output_unit(config, ZONE_BUCKET)`. Their default CONSTANTS are authored in millimetres,
so handing a raw constant to an imperial zone stores inches: 24 -> 610 mm,
20 -> 508 mm/h, -10 -> -254 mm.

The last one is damaging rather than merely wrong: irrigation gates on
`bucket < bucket_threshold`, so no realistic bucket passes and every deficit-gated run
is silently suppressed.
"""

from unittest.mock import MagicMock

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.helpers import zone_depth_default
from custom_components.smart_irrigation.store import MigratableStore

MM_PER_INCH = 25.4


class TestZoneDepthDefault:
    def test_metric_passes_the_mm_constant_through(self):
        assert zone_depth_default(24, True) == 24
        assert zone_depth_default(-10.0, True) == -10.0

    def test_imperial_converts_mm_to_inches(self):
        assert zone_depth_default(25.4, False) == pytest.approx(1.0)
        assert zone_depth_default(-10.0, False) == pytest.approx(-10.0 / MM_PER_INCH)

    def test_none_is_preserved(self):
        # drainage_rate is legitimately None ("no drainage") on older zones.
        assert zone_depth_default(None, False) is None

    def test_imperial_threshold_no_longer_blocks_a_realistic_deficit(self):
        # The whole point. A thirsty imperial zone sits near -0.6 in; the raw mm
        # constant as inches (-10) gates that out, the converted default does not.
        thirsty_inches = -0.6
        assert not (thirsty_inches < const.CONF_DEFAULT_BUCKET_THRESHOLD)  # the bug
        assert thirsty_inches < zone_depth_default(
            const.CONF_DEFAULT_BUCKET_THRESHOLD, False
        )  # fixed

    def test_metric_threshold_keeps_its_10mm_gate(self):
        # The fix must not quietly disable the gate for metric users.
        assert -15.0 < zone_depth_default(const.CONF_DEFAULT_BUCKET_THRESHOLD, True)
        assert not (
            -5.0 < zone_depth_default(const.CONF_DEFAULT_BUCKET_THRESHOLD, True)
        )


def _store(metric: bool) -> MigratableStore:
    hass = MagicMock()
    hass.config.units = METRIC_SYSTEM if metric else US_CUSTOMARY_SYSTEM
    return MigratableStore(hass, 12, "test.storage")


def _zones(**overrides):
    zone = {
        const.ZONE_ID: 0,
        const.ZONE_MAXIMUM_BUCKET: const.CONF_DEFAULT_MAXIMUM_BUCKET,
        const.ZONE_DRAINAGE_RATE: const.CONF_DEFAULT_DRAINAGE_RATE,
        const.ZONE_BUCKET_THRESHOLD: const.CONF_DEFAULT_BUCKET_THRESHOLD,
    }
    zone.update(overrides)
    return {"config": {}, "zones": [zone]}


class TestMigrationV12:
    """The migration is the part that fixes anyone.

    These fields were absent before they shipped; hydration seeded them from the raw
    constants and the whole store was written back, so every existing install already
    has the wrong numbers persisted. Repairing only the default helps nobody.
    """

    async def test_imperial_unconverted_defaults_are_repaired(self):
        out = await _store(metric=False)._async_migrate_func(11, _zones())
        z = out["zones"][0]
        assert z[const.ZONE_MAXIMUM_BUCKET] == pytest.approx(24 / MM_PER_INCH)
        assert z[const.ZONE_DRAINAGE_RATE] == pytest.approx(20.0 / MM_PER_INCH)
        assert z[const.ZONE_BUCKET_THRESHOLD] == pytest.approx(-10.0 / MM_PER_INCH)

    async def test_metric_is_untouched(self):
        # Metric stores mm, so the constants are already correct there.
        out = await _store(metric=True)._async_migrate_func(11, _zones())
        z = out["zones"][0]
        assert z[const.ZONE_MAXIMUM_BUCKET] == const.CONF_DEFAULT_MAXIMUM_BUCKET
        assert z[const.ZONE_BUCKET_THRESHOLD] == const.CONF_DEFAULT_BUCKET_THRESHOLD

    async def test_deliberate_values_are_untouched(self):
        # Only an EXACT match with the raw constant is treated as unconverted.
        out = await _store(metric=False)._async_migrate_func(
            11,
            _zones(
                **{
                    const.ZONE_MAXIMUM_BUCKET: 1.0,
                    const.ZONE_BUCKET_THRESHOLD: -0.6,
                    const.ZONE_DRAINAGE_RATE: 1.3,
                }
            ),
        )
        z = out["zones"][0]
        assert z[const.ZONE_MAXIMUM_BUCKET] == 1.0
        assert z[const.ZONE_BUCKET_THRESHOLD] == -0.6
        assert z[const.ZONE_DRAINAGE_RATE] == 1.3

    async def test_is_idempotent(self):
        store = _store(metric=False)
        once = await store._async_migrate_func(11, _zones())
        twice = await store._async_migrate_func(11, once)
        assert twice["zones"][0] == once["zones"][0]
