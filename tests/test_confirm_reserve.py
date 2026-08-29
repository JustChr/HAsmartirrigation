"""The arm's confirm reserve, and pricing a flow zone at the rate it measured.

Two halves of one defect: `concurrent_wall_clock` prices water and nothing
else, while the runner also pays a valve-confirm poll per zone and a flow zone
delivers at whatever rate its plumbing has rather than at the rate it is
configured for. Once the finish is a hard deadline, both gaps come out of the
tail of a run the planner said would fit.
"""

import pytest
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.duration_math import calibrated_flow_seconds
from custom_components.smart_irrigation.run_window import (
    TRACK_CLASSIC,
    ZoneRun,
    concurrent_wall_clock,
    simulate_wall_clock,
)


def _run(zid, duration, **kw):
    kw.setdefault("track", TRACK_CLASSIC)
    return ZoneRun(zone_id=zid, duration=duration, depletion_ratio=1.0, **kw)


def _sim(runs, sequencing, **kw):
    kw.setdefault("max_slot_seconds", 300)
    kw.setdefault("min_absorption_seconds", 0)
    return simulate_wall_clock(runs, sequencing=sequencing, **kw)


class TestConfirmIsOffUnlessAskedFor:
    """Selection and the dial price the water alone.

    The confirm ceiling is a worst case. Charging it where zones are chosen
    would drop a zone every night on an install whose valves report back in a
    second, to save a tail cut that only bites on a tight window.
    """

    def test_the_default_ignores_confirm_seconds(self):
        runs = [_run(0, 600, confirm_seconds=30), _run(1, 600, confirm_seconds=30)]
        assert _sim(runs, const.CONF_ZONE_SEQUENCING_SEQUENTIAL) == 1200

    def test_a_zone_carrying_no_water_charges_no_confirm(self):
        """It is never opened, so nothing polls it."""
        runs = [_run(0, 600, confirm_seconds=30), _run(1, 0, confirm_seconds=30)]
        assert (
            _sim(
                runs,
                const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
                include_confirm=True,
            )
            == 630
        )


class TestConfirmAccumulatesBySequencing:
    def test_sequential_pays_it_once_per_zone(self):
        runs = [_run(i, 600, confirm_seconds=30) for i in range(3)]
        assert (
            _sim(runs, const.CONF_ZONE_SEQUENCING_SEQUENTIAL, include_confirm=True)
            == 1890
        )

    def test_parallel_pays_it_once(self):
        """Every zone opens at the same moment, so the polls overlap."""
        runs = [_run(i, 600, confirm_seconds=30) for i in range(3)]
        assert (
            _sim(runs, const.CONF_ZONE_SEQUENCING_PARALLEL, include_confirm=True) == 630
        )

    def test_rotating_pays_it_per_slot(self):
        """Every return to a zone re-opens its valve and polls again, so a
        rotation that visits a zone four times pays four polls for it."""
        runs = [_run(0, 1200, confirm_seconds=30)]
        # 1200 s in 300 s slots is four visits.
        assert (
            _sim(
                runs,
                const.CONF_ZONE_SEQUENCING_ROTATING,
                include_confirm=True,
                max_slot_seconds=300,
            )
            == 1320
        )


class TestConcurrentPassesTheFlagDown:
    def test_the_track_reduction_still_applies(self):
        runs = [_run(i, 600, confirm_seconds=30) for i in range(2)]
        plain = concurrent_wall_clock(
            runs,
            sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
        )
        reserved = concurrent_wall_clock(
            runs,
            sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
            include_confirm=True,
        )
        assert plain == 1200
        assert reserved == 1260


def _flow_zone(**over):
    z = {
        const.ZONE_ID: 1,
        const.ZONE_THROUGHPUT: 6.0,  # L/min configured
        const.ZONE_FLOW_SENSOR: "sensor.flow",
        const.ZONE_MAXIMUM_DURATION: 0,
        const.ZONE_LEAD_TIME: 0,
    }
    z.update(over)
    return z


class TestCalibratedFlowSeconds:
    def test_too_few_samples_leaves_the_estimate_alone(self):
        z = _flow_zone(**{const.ZONE_FLOW_CAL_SAMPLES: [3.5, 3.5]})
        assert calibrated_flow_seconds(z, 600, True) == 600

    def test_a_zone_plumbed_slower_than_its_setting_is_priced_longer(self):
        """6 L/min configured against ~3.5 measured: every run takes about 1.7x
        the estimate, on every run, in the same direction."""
        z = _flow_zone(**{const.ZONE_FLOW_CAL_SAMPLES: [3.5, 3.5, 3.5]})
        assert calibrated_flow_seconds(z, 600, True) == pytest.approx(600 * (6.0 / 3.5))

    def test_a_setting_that_matches_the_plumbing_does_not_move(self):
        z = _flow_zone(**{const.ZONE_FLOW_CAL_SAMPLES: [6.0, 6.0, 6.0]})
        assert calibrated_flow_seconds(z, 600, True) == pytest.approx(600)

    def test_lead_time_does_not_stretch_with_the_flow(self):
        """It is the fixed cost of opening the zone, not part of the water."""
        z = _flow_zone(
            **{const.ZONE_FLOW_CAL_SAMPLES: [3.0, 3.0, 3.0], const.ZONE_LEAD_TIME: 60}
        )
        # 660 s planned = 60 s lead + 600 s water; only the water doubles.
        assert calibrated_flow_seconds(z, 660, True) == pytest.approx(1260)

    def test_imperial_compares_like_with_like(self):
        """The samples are litres per minute whatever the install's units, so a
        gal/min setting has to be converted before the ratio is taken."""
        z = _flow_zone(**{const.ZONE_THROUGHPUT: 2.0})  # gal/min
        lpm = 2.0 * const.GALLON_TO_LITER_FACTOR
        z[const.ZONE_FLOW_CAL_SAMPLES] = [lpm / 2, lpm / 2, lpm / 2]
        # Measured at half the configured rate -> twice as long.
        assert calibrated_flow_seconds(z, 600, False) == pytest.approx(1200)

    def test_the_estimate_never_exceeds_the_runs_own_safety_timeout(self):
        z = _flow_zone(
            **{
                const.ZONE_FLOW_CAL_SAMPLES: [0.001, 0.001, 0.001],
                const.ZONE_MAXIMUM_DURATION: 900,
            }
        )
        assert calibrated_flow_seconds(z, 600, True) == 900

    def test_an_unset_maximum_clamps_at_the_flow_safety_timeout(self):
        z = _flow_zone(**{const.ZONE_FLOW_CAL_SAMPLES: [0.001, 0.001, 0.001]})
        assert calibrated_flow_seconds(z, 600, True) == const.FLOW_SAFETY_TIMEOUT

    def test_an_unreadable_rate_falls_back_to_the_configured_one(self):
        z = _flow_zone(
            **{const.ZONE_THROUGHPUT: 0, const.ZONE_FLOW_CAL_SAMPLES: [3.5, 3.5, 3.5]}
        )
        assert calibrated_flow_seconds(z, 600, True) == 600


class TestUnitsAreNotGuessed:
    """Pins the two unit systems against each other rather than against one
    hand-computed number, so a conversion dropped on one path shows up."""

    def test_the_same_physical_zone_prices_the_same_in_either_system(self):
        metric = _flow_zone(
            **{const.ZONE_THROUGHPUT: 6.0, const.ZONE_FLOW_CAL_SAMPLES: [3.0] * 3}
        )
        imperial = _flow_zone(
            **{
                const.ZONE_THROUGHPUT: 6.0 / const.GALLON_TO_LITER_FACTOR,
                const.ZONE_FLOW_CAL_SAMPLES: [3.0] * 3,
            }
        )
        assert METRIC_SYSTEM is not US_CUSTOMARY_SYSTEM
        assert calibrated_flow_seconds(metric, 600, True) == pytest.approx(
            calibrated_flow_seconds(imperial, 600, False)
        )


class TestZoneConfirmSeconds:
    """Which dispatches actually poll, priced from the runner's own branches."""

    @staticmethod
    def _coord():
        from custom_components.smart_irrigation import SmartIrrigationCoordinator

        return SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)

    def test_a_classic_zone_pays_the_poll(self):
        """_run_valve_metered confirms the linked entity unconditionally."""
        zone = {
            const.ZONE_LINKED_ENTITY: "switch.z",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
        }
        assert self._coord()._zone_confirm_seconds(zone) == const.VALVE_CONFIRM_TIMEOUT

    def test_a_zone_with_no_linked_entity_pays_nothing(self):
        zone = {const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC}
        assert self._coord()._zone_confirm_seconds(zone) == 0.0

    def test_a_station_pays_nothing(self):
        """The controller owns the open, and a queued station is not running at
        +30s anyway, which is why the runner never polls one."""
        zone = {
            const.ZONE_LINKED_ENTITY: "switch.s01",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_OPENSPRINKLER,
        }
        assert self._coord()._zone_confirm_seconds(zone) == 0.0

    def test_a_self_closing_zone_pays_only_with_a_confirm_entity(self):
        """With none it is credited optimistically and nothing polls."""
        base = {
            const.ZONE_LINKED_ENTITY: "switch.z",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        }
        assert self._coord()._zone_confirm_seconds(base) == 0.0
        with_confirm = {**base, const.ZONE_CONFIRM_ENTITY: "binary_sensor.flowing"}
        assert (
            self._coord()._zone_confirm_seconds(with_confirm)
            == const.VALVE_CONFIRM_TIMEOUT
        )
