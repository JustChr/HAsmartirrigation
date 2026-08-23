"""What a schedule's run costs on a typical night, end to end.

``tests/test_run_window.py`` drives the arithmetic and
``tests/test_websocket_get_nominal_demand.py`` drives the command shell over a
stubbed coordinator. Neither can see the layer between them:
``async_nominal_demand_seconds`` is where the schedule's zone selection is
normalized, the sequencing settings are read, and the controller's station
grouping is gathered for a module that cannot read an entity itself. Every one
of those is invisible to a test that stubs the method out.

The registered schema is here for the same reason. A websocket command whose
schema does not match what the panel sends fails as an infinite "Loading data"
spinner with nothing a user can act on, and the schema is not reachable from
the handler function the other file calls directly.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import voluptuous as vol
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation import websockets as si_websockets

COMMAND = const.DOMAIN + "/schedule_nominal_demand"


def _zone(zone_id, threshold=-10.0, **kw):
    """A due-at-threshold zone: 10 mm over 1 m2 is 10 L, at 1 L/min = 600 s."""
    z = {
        const.ZONE_ID: zone_id,
        const.ZONE_NAME: f"Zone {zone_id}",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
        const.ZONE_LINKED_ENTITY: f"switch.valve_{zone_id}",
        const.ZONE_SIZE: 1.0,
        const.ZONE_THROUGHPUT: 1.0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_BUCKET: 0.0,
        const.ZONE_BUCKET_THRESHOLD: threshold,
    }
    z.update(kw)
    return z


def _coord(zones, *, sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL, metric=True):
    c = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM if metric else US_CUSTOMARY_SYSTEM
    # No OpenSprinkler station among these zones, so nothing reaches the state
    # machine; the station path has its own coverage in test_opensprinkler.py.
    hass.states.async_all = Mock(return_value=[])
    c.hass = hass
    c.store = Mock()
    c.store.config = SimpleNamespace(
        zone_sequencing=sequencing,
        zone_sequencing_max_consecutive_duration=5,
        zone_sequencing_min_absorption_time=0,
    )
    c.store.async_get_zones = AsyncMock(side_effect=lambda: [dict(z) for z in zones])
    return c


class TestTheProjection:
    """The coordinator method, driven for real rather than stubbed."""

    async def test_sums_the_selection_under_sequential(self):
        coord = _coord([_zone(1), _zone(2)])
        assert await coord.async_nominal_demand_seconds("all") == 1200.0

    async def test_a_zone_selection_restricts_the_total(self):
        coord = _coord([_zone(1), _zone(2)])
        assert await coord.async_nominal_demand_seconds(["1"]) == 600.0

    async def test_none_is_read_as_every_zone(self):
        """The schedule dicts store no ``zones`` key at all when they mean all
        of them, so None has to reach the same answer "all" does."""
        coord = _coord([_zone(1), _zone(2)])
        assert await coord.async_nominal_demand_seconds(None) == 1200.0

    async def test_the_sequencing_setting_reaches_the_reduction(self):
        zones = [_zone(1), _zone(2)]
        parallel = _coord(zones, sequencing=const.CONF_ZONE_SEQUENCING_PARALLEL)
        assert await parallel.async_nominal_demand_seconds("all") == 600.0

    async def test_a_disabled_zone_costs_the_schedule_nothing(self):
        zones = [_zone(1), _zone(2, **{const.ZONE_STATE: const.ZONE_STATE_DISABLED})]
        assert await _coord(zones).async_nominal_demand_seconds("all") == 600.0

    async def test_the_zones_maximum_duration_caps_its_share(self):
        coord = _coord([_zone(1, **{const.ZONE_MAXIMUM_DURATION: 120})])
        assert await coord.async_nominal_demand_seconds("all") == 120.0

    async def test_it_does_not_move_when_a_bucket_moves(self):
        """The property that separates this from demand. A schedule is a
        long-lived thing, so what it reserves must not follow tonight's
        weather."""
        dry = [_zone(1, **{const.ZONE_BUCKET: -50.0})]
        wet = [_zone(1, **{const.ZONE_BUCKET: 25.0})]
        assert await _coord(dry).async_nominal_demand_seconds("all") == await _coord(
            wet
        ).async_nominal_demand_seconds("all")

    async def test_the_threshold_is_read_in_the_installs_own_units(self):
        """Depth-valued zone fields are stored in display units, so a stored
        threshold of 10 is 10 mm metric and 10 INCHES imperial. Both values are
        hand-derived rather than merely asserted unequal, since a conversion
        applied backwards or applied twice is also unequal.

        Metric: 10 mm over 1 m2 is 10 L, at 1 L/min, so 600 s.
        Imperial: 10 in over 1 sq ft is 10/12 cu ft, which is 6.234 US gal, at
        1 gal/min, so 374 s."""
        metric = await _coord([_zone(1)], metric=True).async_nominal_demand_seconds(
            "all"
        )
        imperial = await _coord([_zone(1)], metric=False).async_nominal_demand_seconds(
            "all"
        )
        assert metric == 600.0
        assert imperial == pytest.approx(374.0, abs=0.5)

    async def test_a_zero_threshold_prices_at_zero(self):
        """Review follow-up. Pinned because the number is surprising and the
        reason is not in it.

        A threshold of 0 is the MOST eager setting there is — the gate is
        ``bucket < threshold``, so any deficit at all triggers the zone — yet
        it contributes nothing to what the schedule is said to reserve. That is
        the honest answer to "what does configuration alone reserve" (at 0 no
        depletion is banked, so no run length follows from configuration), but
        it is a floor, not a measurement, and a dial drawing it must not read
        it as "this zone waters for no time". Asserted next to a normal zone so
        the zero is visibly the threshold's doing and not a broken fixture.
        """
        assert (
            await _coord([_zone(1, threshold=0.0)]).async_nominal_demand_seconds("all")
            == 0.0
        )
        assert (
            await _coord([_zone(1, threshold=-10.0)]).async_nominal_demand_seconds(
                "all"
            )
            == 600.0
        )

    async def test_members_are_excluded_and_no_distributor_term_is_added(self):
        """Review follow-up: the known gap, pinned so it cannot be inherited
        silently by the PR that draws this number.

        ``skip_conditions.get_total_irrigation_duration`` answers
        ``max(zone_track, dist_track)`` and prices one whole
        ``distributor_cycle_estimate`` per in-scope distributor. This
        projection has no such term, so a schedule targeting ONLY distributor
        members publishes 0 while really reserving a full sweep. Closing it is
        a design decision (that estimate reads live ``ZONE_DURATION`` and
        ``current_outlet``, the very things this projection is independent of),
        so this test records the behaviour rather than blessing it.
        """
        members_only = [
            _zone(1, **{const.ZONE_DISTRIBUTOR_ID: "d1"}),
            _zone(2, **{const.ZONE_DISTRIBUTOR_ID: "d1"}),
        ]
        assert await _coord(members_only).async_nominal_demand_seconds("all") == 0.0
        # A direct zone alongside them is priced, and priced ALONE — the
        # members add nothing, not even a sweep the run really performs.
        mixed = members_only + [_zone(3)]
        assert await _coord(mixed).async_nominal_demand_seconds("all") == 600.0


class TestTheRegisteredCommand:
    """The schema, read off the registry the panel's calls are dispatched by."""

    @pytest.fixture
    async def schema(self, hass, monkeypatch):
        """The schema the integration hands to the registration API.

        Captured at the call rather than read back out of ``hass.data``: this
        suite installs a module-wide ``websocket_api`` double, so the real
        registry is never populated and reading it back would only ever measure
        the double.
        """
        registered = {}

        def _record(_hass, command_or_handler, handler=None, schema=None):
            # Mirrors the real signature's two forms: the decorator form passes
            # a handler alone, and only the explicit form names a command.
            if handler is not None:
                registered[command_or_handler] = schema

        monkeypatch.setattr(si_websockets, "async_register_command", _record)
        # Registration also installs the HTTP views, a separate surface with
        # nothing to do with the command schema under test.
        hass.http = Mock()
        await si_websockets.async_register_websockets(hass)
        assert COMMAND in registered, "the command is not registered at all"
        assert registered[COMMAND] is not None, "registered without a schema"
        return registered[COMMAND]

    def _msg(self, **kw):
        return {"id": 1, "type": COMMAND, **kw}

    def test_all_is_accepted(self, schema):
        assert schema(self._msg(zones="all"))["zones"] == "all"

    def test_a_list_of_ids_is_accepted(self, schema):
        assert schema(self._msg(zones=["1", "2"]))["zones"] == ["1", "2"]

    def test_zones_is_optional(self, schema):
        assert "zones" not in schema(self._msg())

    def test_a_bare_zone_id_string_is_rejected(self, schema):
        """Not pedantry: normalize_zone_selection iterates a bare string
        character by character, so "12" would silently become zones 1 and 2."""
        with pytest.raises(vol.Invalid):
            schema(self._msg(zones="12"))
