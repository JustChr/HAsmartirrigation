"""Convert stored zone values when Home Assistant's unit system changes.

Zone numbers are stored in the user's DISPLAY units, not canonically: the
calculation converts them to mm/m2/l-per-minute on the way in and back on the
way out (see ``calculation.calculate_module``). That is a deliberate, long-
standing convention — but it means the stored digits only mean anything
alongside the unit system they were written under, and nothing on disk records
which one that was.

So flipping HA between metric and US customary silently reinterprets every one
of those numbers by its conversion factor: 25.4 for depths, 10.764 for area,
3.785 for flow. A ``bucket_threshold`` of -10 written as mm becomes -10 inches,
a deficit no bucket ever reaches, and every deficit-gated run stops. Nothing
logs, nothing errors, and the panel shows the same digits it always did.

This module is the conversion half of the fix; ``coordinator
.async_reconcile_stored_unit_system`` is the detection half. Kept as a leaf
module (no package imports beyond const/helpers) so it can be unit-tested
without standing up a coordinator.

Reported as issue #67.
"""

from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .helpers import convert_between


def unit_system_name(units) -> str:
    """Return a loggable name for a Home Assistant ``UnitSystem``.

    ``UnitSystem`` has no public ``name`` — only a private ``_name`` — so the
    obvious ``units.name`` raises ``AttributeError``. That is not hypothetical:
    it was live in the ``core_config_updated`` handler and killed it before it
    could dispatch anything, so a unit flip made in the UI did nothing at all
    (reported by clarejor while verifying issue #67).
    """
    if units is None:
        return "unknown"
    return (
        const.UNIT_SYSTEM_METRIC
        if units is METRIC_SYSTEM
        else const.UNIT_SYSTEM_US_CUSTOMARY
    )


# Depth-valued zone fields, stored in mm (metric) or inches (imperial).
#
# ``irrigation_target_bucket`` belongs here and is easy to miss: it is written
# by the same imperial branch that writes ``bucket`` (calculation.py), and the
# runner applies it directly as a leftover depth.
ZONE_DEPTH_FIELDS = (
    const.ZONE_BUCKET,
    const.ZONE_MAXIMUM_BUCKET,
    const.ZONE_DRAINAGE_RATE,
    const.ZONE_BUCKET_THRESHOLD,
    const.ZONE_IRRIGATION_TARGET_BUCKET,
)

# Area and flow are just as exposed as the depths, and are the ones most easily
# forgotten because the bug is usually described in terms of the bucket. Both
# feed `precipitation_rate = (throughput * 60) / size`, so misreading them
# changes run DURATION directly.
ZONE_AREA_FIELDS = (const.ZONE_SIZE,)
ZONE_FLOW_FIELDS = (const.ZONE_THROUGHPUT,)

# DELIBERATELY NOT CONVERTED — do not "fix" this by adding it.
#
# ``current_drainage`` is computed in the mm domain and written straight out
# without the inch conversion its own source field (`drainage_rate`) gets
# (calculation.py, `data[ZONE_CURRENT_DRAINAGE] = drainage`). It is therefore
# already in mm on an imperial install. It is a read-only diagnostic surfaced as
# a sensor attribute and is overwritten by the next calculation, so the
# inconsistency is cosmetic — but converting it here would corrupt it.
_NEVER_CONVERTED = (const.ZONE_CURRENT_DRAINAGE,)

_UNIT_PAIRS = (
    (ZONE_DEPTH_FIELDS, const.UNIT_MM, const.UNIT_INCH),
    (ZONE_AREA_FIELDS, const.UNIT_M2, const.UNIT_SQ_FT),
    (ZONE_FLOW_FIELDS, const.UNIT_LPM, const.UNIT_GPM),
)


def convert_zone_values(zone: dict, *, to_metric: bool) -> dict:
    """Return only the zone keys whose stored value changes with the flip.

    ``to_metric`` is the direction being moved TO, so imperial->metric converts
    inches to mm. Returns a changes dict suitable for ``async_update_zone``;
    empty when the zone holds nothing convertible, so a caller can skip the
    write entirely.

    None values are left alone rather than defaulted: an unset ``maximum_bucket``
    means "no ceiling", and inventing one here would cap a zone that never had a
    cap. Non-numeric junk is skipped for the same reason — a unit flip is not the
    place to start repairing unrelated corruption.
    """
    changes = {}
    for fields, metric_unit, imperial_unit in _UNIT_PAIRS:
        from_unit, to_unit = (
            (imperial_unit, metric_unit) if to_metric else (metric_unit, imperial_unit)
        )
        for field in fields:
            value = zone.get(field)
            if value is None:
                continue
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue
            converted = convert_between(from_unit, to_unit, value)
            if converted is not None:
                changes[field] = converted
    return changes
