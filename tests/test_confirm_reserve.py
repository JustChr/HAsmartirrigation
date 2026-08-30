"""The valve-confirm charge, and pricing a flow zone at the rate it measured.

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
    TRACK_BATCH,
    TRACK_CLASSIC,
    TRACK_SELF_CLOSING,
    TRACK_STATION,
    ZoneRun,
    concurrent_wall_clock,
    nominal_demand_seconds,
    simulate_wall_clock,
    zone_confirm_seconds,
)


def _run(zid, duration, **kw):
    kw.setdefault("track", TRACK_CLASSIC)
    return ZoneRun(zone_id=zid, duration=duration, depletion_ratio=1.0, **kw)


def _sim(runs, sequencing, **kw):
    kw.setdefault("max_slot_seconds", 300)
    kw.setdefault("min_absorption_seconds", 0)
    return simulate_wall_clock(runs, sequencing=sequencing, **kw)


class TestEveryReductionChargesIt:
    """One answer, not two.

    Pricing selection on the water alone while the arm reserves the poll does
    not close the gap, it relocates it: a selection fitted to the window at the
    wrong price still overruns, and in that case the start is already pinned to
    the floor so there is nowhere for the reserve to move to. The deadline then
    cuts the tail exactly as before.
    """

    def test_confirm_is_charged_without_being_asked_for(self):
        runs = [_run(0, 600, confirm_seconds=30), _run(1, 600, confirm_seconds=30)]
        assert _sim(runs, const.CONF_ZONE_SEQUENCING_SEQUENTIAL) == 1260

    def test_a_zone_carrying_no_water_charges_no_confirm(self):
        """It is never opened, so nothing polls it."""
        runs = [_run(0, 600, confirm_seconds=30), _run(1, 0, confirm_seconds=30)]
        assert _sim(runs, const.CONF_ZONE_SEQUENCING_SEQUENTIAL) == 630


class TestConfirmAccumulatesBySequencing:
    def test_sequential_pays_it_once_per_zone(self):
        runs = [_run(i, 600, confirm_seconds=30) for i in range(3)]
        assert _sim(runs, const.CONF_ZONE_SEQUENCING_SEQUENTIAL) == 1890

    def test_parallel_pays_it_once(self):
        """Every zone opens at the same moment, so the polls overlap."""
        runs = [_run(i, 600, confirm_seconds=30) for i in range(3)]
        assert _sim(runs, const.CONF_ZONE_SEQUENCING_PARALLEL) == 630

    def test_rotating_pays_it_per_slot(self):
        """Every return to a zone re-opens its valve and polls again, so a
        rotation that visits a zone four times pays four polls for it."""
        runs = [_run(0, 1200, confirm_seconds=30)]
        # 1200 s in 300 s slots is four visits.
        assert (
            _sim(runs, const.CONF_ZONE_SEQUENCING_ROTATING, max_slot_seconds=300)
            == 1320
        )


class TestTheTrackReductionStillApplies:
    def test_each_track_charges_its_own_members(self):
        """A station never polls, so the two tracks are priced apart: the
        classic pair carries its confirms and the station chain does not."""
        runs = [
            _run(0, 600, confirm_seconds=30),
            _run(1, 600, confirm_seconds=30),
            _run(2, 1800, track=TRACK_STATION),
        ]
        assert (
            concurrent_wall_clock(
                runs,
                sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
                max_slot_seconds=300,
                min_absorption_seconds=0,
            )
            == 1800  # the station track is the longer of the two
        )


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
    """Which dispatches actually poll, read off the runner's own branches."""

    def test_a_classic_zone_pays_the_poll(self):
        """_run_valve_metered confirms the linked entity unconditionally."""
        zone = {
            const.ZONE_LINKED_ENTITY: "switch.z",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
        }
        assert zone_confirm_seconds(zone) == const.VALVE_CONFIRM_TIMEOUT

    def test_a_zone_with_no_linked_entity_pays_nothing(self):
        zone = {const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC}
        assert zone_confirm_seconds(zone) == 0.0

    def test_a_station_pays_nothing(self):
        """The controller owns the open, and a queued station is not running at
        +30s anyway, which is why the runner never polls one."""
        zone = {
            const.ZONE_LINKED_ENTITY: "switch.s01",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_OPENSPRINKLER,
        }
        assert zone_confirm_seconds(zone) == 0.0

    def test_a_self_closing_zone_pays_only_with_a_confirm_entity(self):
        """With none it is credited optimistically and nothing polls."""
        base = {
            const.ZONE_LINKED_ENTITY: "switch.z",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_SERVICE,
        }
        assert zone_confirm_seconds(base) == 0.0
        assert (
            zone_confirm_seconds(
                {**base, const.ZONE_CONFIRM_ENTITY: "binary_sensor.flowing"}
            )
            == const.VALVE_CONFIRM_TIMEOUT
        )

    def test_every_track_has_an_answer(self):
        """A track added later without a branch here would silently price at
        the classic ceiling, which is the over-reserving direction but still a
        wrong one."""
        assert {TRACK_CLASSIC, TRACK_SELF_CLOSING, TRACK_STATION, TRACK_BATCH}


class TestTheDialAgreesWithTheArm:
    """The dial draws the window a user designs against. Pricing it on a
    different model than the one the run is fitted to means the schedule they
    drew is not the schedule they get."""

    @staticmethod
    def _zone(**over):
        z = {
            const.ZONE_ID: 1,
            const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
            const.ZONE_BUCKET_THRESHOLD: -10.0,
            const.ZONE_THROUGHPUT: 10.0,
            const.ZONE_SIZE: 10.0,
            const.ZONE_MULTIPLIER: 1.0,
            const.ZONE_LEAD_TIME: 0,
            # None, not 0: duration_from_deficit treats a maximum_duration of 0
            # as a real clamp and prices every zone at zero seconds.
            const.ZONE_MAXIMUM_DURATION: None,
            const.ZONE_LINKED_ENTITY: "switch.z",
            const.ZONE_WATERING_MODE: const.WATERING_MODE_CLASSIC,
        }
        z.update(over)
        return z

    def _nominal(self, zones):
        return nominal_demand_seconds(
            zones,
            sequencing=const.CONF_ZONE_SEQUENCING_SEQUENTIAL,
            max_slot_seconds=300,
            min_absorption_seconds=0,
            metric=True,
        )

    def test_the_dial_carries_the_confirm_too(self):
        one = self._nominal([self._zone()])
        assert one == 600 + const.VALVE_CONFIRM_TIMEOUT

    def test_the_dial_prices_a_flow_zone_at_the_measured_rate(self):
        measured = self._nominal(
            [
                self._zone(
                    **{
                        const.ZONE_FLOW_SENSOR: "sensor.flow",
                        const.ZONE_FLOW_CAL_SAMPLES: [5.0, 5.0, 5.0],
                    }
                )
            ]
        )
        # 600 s of water at half the configured rate, plus the one poll.
        assert measured == 1200 + const.VALVE_CONFIRM_TIMEOUT
