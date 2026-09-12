"""The flow-calibration advisory rejects a sample too small for its meter to measure.

The advisory divides measured litres by minutes. A residential meter pulses at
about 1 L, so the error on any single reading is a whole pulse, and what matters
is not how LONG a run was but how MUCH it delivered: one pulse of error against
6 L is 17%, against 60 L it is 1.7%. The advisory's own band is 15%, so a sample
carrying more quantisation error than the band it is judged against cannot say
anything -- it is noise that fires (or silences) a notification telling the user
to change a working setting.

That was gated on DURATION, at a fixed 300 s, in exactly one of the three
callers. The derivation behind the number was always rate-dependent -- the
constant's own comment says "at 3.1 L/min a 1 L error is 15% of the reading only
once the run exceeds ~130 s" -- so a fixed second count is the wrong axis for it,
and the two callers that never had it accepted anything.

Measured on one zone, 37 runs, one valve and one meter with nothing varying but
run length: the spread of observed rates collapses about six-fold once a run is
long enough to deliver a real volume. Issue #133.
"""

import pathlib
from unittest.mock import AsyncMock, Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.distributor import DistributorMixin
from custom_components.irrigation_plus.irrigation import IrrigationRunnerMixin
from custom_components.irrigation_plus.master import MasterMixin
from custom_components.irrigation_plus.skip_conditions import SkipConditionsMixin


class _Host(DistributorMixin, MasterMixin, SkipConditionsMixin, IrrigationRunnerMixin):
    pass


def _host():
    c = _Host()
    c.hass = Mock()
    c.hass.config.units = METRIC_SYSTEM
    c.hass.services.async_call = AsyncMock()
    c.store = Mock()
    c.store.async_update_zone = AsyncMock()
    c._throughput_lpm = Mock(return_value=10.0)
    return c


def _zone(**kw):
    z = {
        const.ZONE_ID: 3,
        const.ZONE_NAME: "Beet",
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_FLOW_CAL_SAMPLES: [],
        const.ZONE_FLOW_CAL_ADVISED: False,
    }
    z.update(kw)
    return z


def _banked(c):
    """The samples written back to the store, or [] if nothing was written."""
    if not c.store.async_update_zone.await_args_list:
        return []
    return c.store.async_update_zone.await_args_list[-1].args[1][
        const.ZONE_FLOW_CAL_SAMPLES
    ]


def test_the_floor_is_the_meter_resolution_divided_by_the_band():
    """Derived, not chosen. The question the floor answers is "can one pulse of
    error stay inside the band this sample will be judged against", and that is
    resolution / band by construction. Pinned so the floor moves when the band
    does: widening FLOW_CAL_DEVIATION to 0.30 must halve the litres required,
    and a hand-typed constant would not follow."""
    assert (
        const.FLOW_CAL_MIN_SAMPLE_L
        == const.FLOW_CAL_METER_RESOLUTION_L / const.FLOW_CAL_DEVIATION
    )


async def test_a_sample_too_small_for_its_meter_is_not_banked():
    # 5 L on a 1 L meter carries 20% error against a 15% band. Rejected before
    # it reaches the sample list, so it cannot evict a good sample either -- the
    # window is only 5 deep, which is how three bad readings used to displace
    # every real one.
    c = _host()
    z = _zone()
    await c._flow_calibration_check(z, 5.0, 60.0)
    assert _banked(c) == []


async def test_a_sample_at_the_floor_is_accepted():
    # The boundary is inclusive: at exactly resolution / band the pulse error is
    # the band, not more than it.
    c = _host()
    z = _zone()
    await c._flow_calibration_check(z, const.FLOW_CAL_MIN_SAMPLE_L, 60.0)
    assert len(_banked(c)) == 1


async def test_duration_alone_never_rejects_a_sample():
    """The pin for the half of #133 that is a REMOVAL.

    A 30 s run delivering 10 L is a perfectly good rate sample: the volume is
    what bounds the error, and 30 s of a 20 L/min zone says more than 300 s of a
    trickle. The old gate rejected it, and only on the observed path.

    This fails if any caller regains a duration gate of its own, which is the
    shape the fix exists to remove -- one rule restated in three places, two of
    which never had it.
    """
    c = _host()
    z = _zone()
    await c._flow_calibration_check(z, 10.0, 30.0)
    assert _banked(c) == [20.0]


async def test_the_distributor_caller_inherits_the_floor():
    # The thin delegation is the point: a caller that forwards rather than
    # re-deciding cannot drift from the rule.
    c = _host()
    z = _zone()
    await c._dist_flow_calibration_check(z, measured_l=5.0, seconds=60.0)
    assert _banked(c) == []


def test_the_floor_is_applied_in_exactly_one_place():
    """A tripwire for the defect's own shape: the same decision made in more
    than one file. Fails when a caller starts consulting the floor itself --
    which would mean it can be consulted inconsistently -- and equally when the
    shared helper stops consulting it, because "nowhere at all" also satisfies
    "nowhere but the helper".

    Matched as ``const.FLOW_CAL_MIN_SAMPLE_L``, the qualified form every consumer
    in this package uses, so that naming the floor in a COMMENT -- which
    observed_watering.py does, to say where its own gate's other half went -- is
    not mistaken for consulting it.

    A tripwire, not a proof: a caller that re-derives the arithmetic without
    naming the constant, or that imports the bare name, walks straight past it.
    """
    src = pathlib.Path(__file__).parent.parent / "custom_components" / "irrigation_plus"
    frontend = src / "frontend"
    users = sorted(
        p.name
        for p in src.rglob("*.py")
        if not p.is_relative_to(frontend)
        and "const.FLOW_CAL_MIN_SAMPLE_L"
        in p.read_text(encoding="utf-8", errors="ignore")
    )
    assert users == ["irrigation.py"], (
        f"the floor is consulted in {users}; it belongs to the one shared helper "
        "in irrigation.py, which every caller passes through"
    )
    # And it must still BE somewhere: "nowhere at all" satisfies the assertion above.
    const_src = (src / "const.py").read_text(encoding="utf-8")
    assert "FLOW_CAL_MIN_SAMPLE_L = " in const_src
