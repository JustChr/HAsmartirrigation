"""Tests for the Irrigation Plus binary sensor platform."""

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.binary_sensor import (
    SmartIrrigationZoneWateringNowSensor,
    _zone_needs_irrigation,
)


def _zone(**overrides):
    zone = {
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_DURATION: 600,
        const.ZONE_BUCKET: -12.0,
        const.ZONE_BUCKET_THRESHOLD: -10.0,
    }
    zone.update(overrides)
    return zone


def test_zone_needs_irrigation_when_gate_met():
    """Enabled + duration > 0 + bucket below threshold -> needed."""
    assert _zone_needs_irrigation(_zone()) is True


def test_zone_needs_irrigation_respects_disabled():
    assert _zone_needs_irrigation(_zone(state=const.ZONE_STATE_DISABLED)) is False


def test_zone_needs_irrigation_requires_duration():
    assert _zone_needs_irrigation(_zone(duration=0)) is False
    assert _zone_needs_irrigation(_zone(duration=None)) is False


def test_zone_needs_irrigation_requires_deficit_below_threshold():
    # -5 is above the -10 threshold: deficit not deep enough yet
    assert _zone_needs_irrigation(_zone(bucket=-5.0)) is False
    # exactly at the threshold is not "below"
    assert _zone_needs_irrigation(_zone(bucket=-10.0)) is False


def test_zone_needs_irrigation_handles_missing():
    assert _zone_needs_irrigation(None) is False
    assert _zone_needs_irrigation({}) is False


async def test_watering_now_sensor_without_linked_entity_does_not_crash(hass):
    """Regression: a service/self-closing zone has no linked_entity, so the
    watering_now sensor's _linked_entity was never initialised and _resubscribe()
    (called from async_added_to_hass) raised AttributeError on add."""
    zone = {const.ZONE_ID: 1, const.ZONE_NAME: "Beet"}
    sensor = SmartIrrigationZoneWateringNowSensor(
        hass, "binary_sensor.test_watering_now", zone
    )
    assert sensor._linked_entity is None
    sensor._resubscribe()  # called from async_added_to_hass; must not raise


class TestAServiceZoneShowsWhenItIsWatering:
    """A service/self-closing zone has no ``linked_entity``, and used to have no
    ``watering_now`` either.

    The sensor mirrors one entity and subscribes to it. It read only
    ``linked_entity``, which is null for a zone driven by ``run_service`` — so
    ``is_on`` returned False unconditionally and the sensor could never turn on. Not a
    stale state: structural, for every zone on that path.

    The integration was not missing the information. ``observed_entity`` carries exactly
    "the entity that is on while this zone waters", and ``observed_watering`` already
    falls back to it for this same case. This is that fallback, applied to the one
    consumer that lacked it.

    Measured on a production install on 2026-09-28: three zones watered in sequence and
    every run was recorded, while all three sensors stayed off with ``last_changed``
    frozen at the boot timestamp across four runs.
    """

    @staticmethod
    def _sensor(hass, **zone_fields):
        zone = {const.ZONE_ID: 1, const.ZONE_NAME: "Kirschbaum", **zone_fields}
        sensor = SmartIrrigationZoneWateringNowSensor(
            hass, "binary_sensor.test_watering_now", zone
        )
        # What the platform does on add. ``is_on`` reads ``self.hass``, which HA sets
        # then -- not the one passed to __init__ -- so a sensor built here and never
        # added would report False whatever it mirrors, and every assertion below
        # would pass for the wrong reason.
        sensor.hass = hass
        return sensor

    async def test_a_service_zone_mirrors_its_observed_entity(self, hass):
        hass.states.async_set("valve.wasser_hinten", "open")
        sensor = self._sensor(hass, observed_entity="valve.wasser_hinten")

        assert sensor._linked_entity == "valve.wasser_hinten"
        assert sensor.is_on is True

    async def test_it_follows_that_entity_closing(self, hass):
        hass.states.async_set("valve.wasser_hinten", "closed")
        sensor = self._sensor(hass, observed_entity="valve.wasser_hinten")

        assert sensor.is_on is False

    async def test_a_linked_entity_still_decides_when_both_are_set(self, hass):
        """No change for a classic zone: the linked entity is what it watches.

        Both fields set and disagreeing is the case that would expose a swapped
        precedence, so it is the one pinned.
        """
        hass.states.async_set("switch.classic", "off")
        hass.states.async_set("valve.observed", "open")
        sensor = self._sensor(
            hass,
            linked_entity="switch.classic",
            observed_entity="valve.observed",
        )

        assert sensor._linked_entity == "switch.classic"
        assert sensor.is_on is False

    async def test_a_zone_with_neither_still_stays_off(self, hass):
        """Unchanged, not fixed: there is nothing to mirror, so it reports nothing."""
        sensor = self._sensor(hass)

        assert sensor._linked_entity is None
        assert sensor.is_on is False
        sensor._resubscribe()  # must still not raise
