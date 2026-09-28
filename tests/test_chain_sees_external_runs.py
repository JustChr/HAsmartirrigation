"""A zone watered from outside the integration, while a cycle holds it.

Observed watering credits such a run at its close and registers nothing while it is
open, so both halves of the cycle's defence were blind to it: the guard at the zone's
turn asks whether a run is in flight and got False from an open valve, and the
write-off that catches a zone watered elsewhere runs off a finalisation an external
run never reaches.

Two windows, therefore two groups of tests below: the run still open when the turn
comes, and the run already closed. The counter-case matters as much as the two -- a
few seconds of hand-testing at the tap must NOT cost a zone its turn.
"""

from datetime import timedelta
from types import SimpleNamespace

from homeassistant.util import dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import const

from tests.test_observed_watering import _state_event
from tests.test_service_chain import (
    ROTATING,
    SEQUENTIAL,
    _coord,
    _dispatch,
    _finish,
    _ids,
    _register,
    _zone,
)


def _observed_zone(zone_id, duration=600):
    """A service zone with an observed entity, a size and a throughput.

    The plain chain zone has no size or throughput, and without them the credit path
    returns before it books anything -- the tests would then pass on a code path that
    never ran.
    """
    z = _zone(zone_id, duration=duration)
    z[const.ZONE_OBSERVED_ENTITY] = f"switch.external_{zone_id}"
    z[const.ZONE_SIZE] = 5.0
    z[const.ZONE_THROUGHPUT] = 3.1
    z[const.ZONE_MAXIMUM_DURATION] = 3600
    z[const.ZONE_FLOW_SENSOR] = None
    z[const.ZONE_BUCKET] = -20.0
    return z


def _observer(hass, sequencing, slot=5):
    """A chain coordinator that also watches its zones' valves."""
    c = _coord(hass, sequencing, slot=slot)
    c.hass.config = SimpleNamespace(units=METRIC_SYSTEM)
    c._observed_on_since = {}
    c._si_driven_until = {}
    c._observed_zone_by_entity = {f"switch.external_{zid}": zid for zid in (1, 2, 3)}
    return c


def _external_open(c, zone_id):
    c._observed_state_changed(
        _state_event(f"switch.external_{zone_id}", old="closed", new="open")
    )


async def _external_close(c, hass, zone_id, after_seconds):
    """Close the valve as if it had been open for ``after_seconds``."""
    c._observed_on_since[zone_id] = dt_util.utcnow() - timedelta(seconds=after_seconds)
    c._observed_state_changed(
        _state_event(f"switch.external_{zone_id}", old="open", new="closed")
    )
    await hass.async_block_till_done()  # the credit runs as a task


async def test_a_sequential_cycle_skips_a_zone_whose_valve_is_open_externally(hass):
    c = _observer(hass, SEQUENTIAL)
    z1, z2 = _register(c, _observed_zone(1), _observed_zone(2))
    await _dispatch(c, [z1, z2])
    assert _ids(c) == [1]

    _external_open(c, 2)
    assert c._observed_on_since.get(2) is not None  # the open edge tracked it
    assert c.zone_run_in_flight(2) is True

    await _finish(c, 1)

    assert 2 not in _ids(c), f"zone 2 was watered on top of an open valve: {c._dispatched}"


async def test_a_rotation_writes_off_a_zone_whose_valve_is_open_externally(hass):
    c = _observer(hass, ROTATING, slot=300)
    # A third zone: writing off zone 2 while only zones 1 and 2 are in the rotation
    # would exhaust it in the same call (nothing left with time remaining), and
    # release nils the rotation object before its remainder can be read. Zone 3
    # gives the rotation somewhere left to go, so the write-off stays observable.
    z1, z2, z3 = _register(c, _observed_zone(1), _observed_zone(2), _observed_zone(3))
    await _dispatch(c, [z1, z2, z3])
    assert _ids(c) == [1]

    _external_open(c, 2)
    await _finish(c, 1)

    assert 2 not in _ids(c), f"zone 2 got a slot on top of an open valve: {c._dispatched}"
    rotation = c._chain_state(const.WATERING_MODE_SERVICE).rotation
    assert rotation.remaining[2] == 0.0
