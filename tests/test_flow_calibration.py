"""Per-member flow calibration advisory (persistent notification).

The advisory keys on the OBSERVED FLOW RATE (measured_l / minutes) compared
against the configured throughput, NOT on a volume deviation. Observed rate is
immune to the zone multiplier, manual custom-duration overrides and the
maximum_duration clamp — a volume deviation absorbs all three and would raise
false advisories (see test_multiplier_does_not_false_trigger). The sample list
therefore holds OBSERVED-RATE floats (L/min), not {measured_l, target_l} dicts.
"""

from unittest.mock import AsyncMock, Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.distributor import DistributorMixin
from custom_components.smart_irrigation.irrigation import IrrigationRunnerMixin
from custom_components.smart_irrigation.master import MasterMixin
from custom_components.smart_irrigation.skip_conditions import SkipConditionsMixin


class _Host(DistributorMixin, MasterMixin, SkipConditionsMixin, IrrigationRunnerMixin):
    pass


def _host():
    c = _Host()
    c.hass = Mock()
    # Default to metric so the advisory message/recommendation is L/min. The
    # imperial branch is exercised by test_imperial_recommendation_uses_gpm.
    c.hass.config.units = METRIC_SYSTEM
    c.hass.services.async_call = AsyncMock()
    c.store = Mock()
    c.store.async_update_zone = AsyncMock()
    # Unit-focus: pin the configured throughput to 10 L/min so tests reason in
    # observed-rate terms only (prefer stubbing over wiring the real unit system).
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


async def test_no_notify_below_min_samples():
    c = _host()
    # 1 prior sample + 1 new = 2 total, below FLOW_CAL_MIN_SAMPLES (3).
    z = _zone(**{const.ZONE_FLOW_CAL_SAMPLES: [12.0]})
    await c._dist_flow_calibration_check(z, measured_l=13.0, seconds=60.0)
    c.hass.services.async_call.assert_not_awaited()


async def test_notify_when_observed_rate_over_threshold():
    c = _host()
    # Configured 10 L/min. Prior observed rates [13.0, 12.5]; new run measured
    # 13 L in 60 s -> observed 13 L/min. mean = 38.5/3 ~= 12.83 -> +28% > 15%.
    z = _zone(**{const.ZONE_FLOW_CAL_SAMPLES: [13.0, 12.5]})
    await c._dist_flow_calibration_check(z, measured_l=13.0, seconds=60.0)
    c.hass.services.async_call.assert_awaited()
    args = c.hass.services.async_call.await_args.args
    assert args[0] == "persistent_notification" and args[1] == "create"
    msg = args[2]["message"]
    assert "over" in msg  # over-watering direction wording
    changes = c.store.async_update_zone.await_args.args[1]
    assert changes[const.ZONE_FLOW_CAL_ADVISED] is True


async def test_within_band_dismisses_and_clears_advised():
    c = _host()
    # Already advised; observed rates back near the configured 10 L/min.
    z = _zone(
        **{const.ZONE_FLOW_CAL_ADVISED: True, const.ZONE_FLOW_CAL_SAMPLES: [10.1, 9.9]}
    )
    await c._dist_flow_calibration_check(z, measured_l=10.0, seconds=60.0)
    c.hass.services.async_call.assert_awaited()
    args = c.hass.services.async_call.await_args.args
    assert args[1] == "dismiss"
    changes = c.store.async_update_zone.await_args.args[1]
    assert changes[const.ZONE_FLOW_CAL_ADVISED] is False


async def test_samples_capped():
    c = _host()
    # 5 prior + 1 new -> stored list capped at FLOW_CAL_MAX_SAMPLES.
    z = _zone(**{const.ZONE_FLOW_CAL_SAMPLES: [10.0] * 5})
    await c._dist_flow_calibration_check(z, measured_l=10.0, seconds=60.0)
    changes = c.store.async_update_zone.await_args.args[1]
    assert len(changes[const.ZONE_FLOW_CAL_SAMPLES]) == const.FLOW_CAL_MAX_SAMPLES


async def test_multiplier_does_not_false_trigger():
    c = _host()
    # KEY regression: a correctly-calibrated member whose observed flow rate
    # always equals the configured 10 L/min. A volume model would compare
    # measured volume against a multiplier-inflated target and drift permanently;
    # the rate model must NOT notify across repeated runs.
    z = _zone()
    for _ in range(3):
        await c._dist_flow_calibration_check(z, measured_l=10.0, seconds=60.0)
        # Propagate the persisted sample list into the zone for the next run,
        # since the Mock store does not mutate the dict.
        changes = c.store.async_update_zone.await_args.args[1]
        z[const.ZONE_FLOW_CAL_SAMPLES] = changes[const.ZONE_FLOW_CAL_SAMPLES]
    c.hass.services.async_call.assert_not_awaited()


async def _drive_over_threshold(c, z):
    """Drive the advisory past FLOW_CAL_MIN_SAMPLES with an observed rate ~30%
    over the configured 10 L/min, propagating the persisted sample list between
    calls (the Mock store does not mutate the zone dict), so exactly ONE
    persistent_notification.create fires."""
    for _ in range(const.FLOW_CAL_MIN_SAMPLES):
        await c._dist_flow_calibration_check(z, measured_l=13.0, seconds=60.0)
        changes = c.store.async_update_zone.await_args.args[1]
        z[const.ZONE_FLOW_CAL_SAMPLES] = changes[const.ZONE_FLOW_CAL_SAMPLES]


def _create_call(c):
    """Return the single persistent_notification.create call's data payload."""
    creates = [
        call
        for call in c.hass.services.async_call.await_args_list
        if call.args[1] == "create"
    ]
    assert len(creates) == 1, f"expected exactly one create, got {len(creates)}"
    return creates[0].args[2]


async def test_flow_calibration_advisory_is_localized_and_links_zone():
    # --- German system: the advisory must be localized (not English) and
    #     deep-link the zone's settings (same target as the dashboard gear). ---
    c = _host()
    c.hass.config.language = "de"
    z = _zone()
    await _drive_over_threshold(c, z)
    msg = _create_call(c)["message"]
    # Deep-link to the zone's settings (path segments, not a ?query).
    assert f"/smart_irrigation/setup/zones/zone/{z[const.ZONE_ID]}" in msg
    # German, not the old hardcoded English.
    assert "Durchsatz" in msg
    assert "Zone" in msg
    assert "consider setting the throughput" not in msg
    # Every placeholder substituted — no stray braces left behind.
    assert "{" not in msg and "}" not in msg

    # --- English system: same wiring, but the English variant. ---
    c2 = _host()
    c2.hass.config.language = "en"
    z2 = _zone()
    await _drive_over_threshold(c2, z2)
    msg2 = _create_call(c2)["message"]
    assert "throughput" in msg2
    assert f"/smart_irrigation/setup/zones/zone/{z2[const.ZONE_ID]}" in msg2
    assert "{" not in msg2 and "}" not in msg2


async def test_readvises_while_out_of_band_after_dismiss():
    """The advisory must re-fire on a later out-of-band run even after it already
    advised once — the user may have dismissed the notification, and dismissing it
    does NOT re-arm the store latch. The old ``and not advised`` gate latched the
    advisory shut for as long as the zone stayed out of band, so a user who
    dismissed it while still miscalibrated was never reminded (live: Kirschlorbeer
    ~-40% off for many runs, no repeat notice)."""
    c = _host()
    z = _zone()
    # Drive past FLOW_CAL_MIN_SAMPLES so the advisory fires once (advised -> True).
    await _drive_over_threshold(c, z)
    # Reflect the persisted latch + the user dismissing the notification: advised
    # stays True in the store (dismiss touches only the UI, not the store field).
    z[const.ZONE_FLOW_CAL_ADVISED] = True
    # A further, still ~30%-over run must re-advise.
    await c._dist_flow_calibration_check(z, measured_l=13.0, seconds=60.0)
    creates = [
        call
        for call in c.hass.services.async_call.await_args_list
        if call.args[1] == "create"
    ]
    assert len(creates) == 2, f"expected a re-advise, got {len(creates)} create(s)"
    # Same notification_id -> HA updates the single notification in place; no
    # stacking / spam even though it re-fires each out-of-band run.
    assert (
        creates[1].args[2]["notification_id"] == creates[0].args[2]["notification_id"]
    )


async def test_imperial_recommendation_uses_gpm():
    c = _host()
    # Imperial display units: the recommendation must be gal/min, not L/min.
    c.hass.config.units = object()  # any non-METRIC sentinel -> imperial branch
    z = _zone(**{const.ZONE_FLOW_CAL_SAMPLES: [13.0, 12.5]})
    await c._dist_flow_calibration_check(z, measured_l=13.0, seconds=60.0)
    c.hass.services.async_call.assert_awaited()
    msg = c.hass.services.async_call.await_args.args[2]["message"]
    assert "gal/min" in msg
    assert "L/min" not in msg
