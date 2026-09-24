"""A zone whose install leaves ``hourlycalculation`` off still gets a live bucket.

``hourlycalculation`` ships off. ``live_estimate_enabled`` is an independent
setting, so an operator could turn live-estimate watering on and have it do
nothing: ``_daily_form_applies`` asked ``replayed_balance_applies``, that
predicate answers False whenever the switch is off, and the mirrored daily
equation was refused to the whole shipped-default population. On a sensor-only
install there is no other source, so the estimate was simply absent and the
sensor read ``unknown`` with nothing saying why.

The two questions are on different axes and only one of them involves the switch:

* which EQUATION the zone's commit runs. For a PyETO zone estimating solar
  radiation from the day's temperature range that is the daily FAO-56 equation,
  and it is the daily equation whether ``hourlycalculation`` is on or off. So the
  mirror applies either way, which is what this module pins;
* which FORM the water balance takes, replayed or lumped. That one is the
  switch's own, deliberately, because replaying moves the stored bucket. It is
  untouched here, and pinned untouched: opening the ET source must not change a
  single number the commit writes.

Asserted against a run of the real ``calculate_module`` rather than a
hand-computed figure, for the reason the sibling module gives: a
reimplementation of the equation in the test would agree with itself however far
the two paths had drifted.
"""

from unittest.mock import Mock

import attr
import pytest
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.calcmodules.pyeto import SOLRAD_behavior
from custom_components.irrigation_plus.calculation import (
    hourly_calculation_enabled,
    zone_module_models_weather,
)
from custom_components.irrigation_plus.live_estimate import (
    REASON_FAILED,
    REASON_NEVER_CALCULATED,
    REASON_NO_BUCKET,
    REASON_NO_COORDINATES,
    REASON_NO_ET_SOURCE,
    REASON_NOT_COMPUTED,
)
from custom_components.irrigation_plus.sensor import (
    SmartIrrigationZoneLiveDeficitSensor,
)
from tests.test_live_estimate_replayed_balance import (
    WINDOW_END,
    _committed,
    _estimating_inputs,
    _estimating_zone,
    _hourly_forecast,
    _inputs,
    _zone,
    make_coordinator,
)


@pytest.fixture
async def coordinator(hass):
    """The shipped default: the hourly form left OFF.

    The sibling module's fixture opts it in, which is the one thing every case
    here varies, so this calls the shared builder rather than copying it.
    """
    return await make_coordinator(hass, hourly_calculation=False)


@pytest.fixture
async def imperial(hass):
    """The same install on inches, where the depth fields are stored in inches."""
    return await make_coordinator(
        hass, hourly_calculation=False, units=US_CUSTOMARY_SYSTEM
    )


class TestTheMirrorAppliesWithTheSwitchOff:
    """The claim: the commit's own equation, offered on the population that ships."""

    async def test_a_sensor_only_zone_gets_a_live_bucket_at_all(self, coordinator):
        """The bug, stated as the behaviour that was missing.

        No weather client and no forecast, which is the sensor-only install the
        feature was inert on: with the mirror refused there was no source left
        and the estimate was absent entirely.
        """
        c, store = coordinator
        zone, module, instance = await _estimating_zone(
            c, store, 2.0, rain_at={20: 14.0}
        )

        est = c._intraday_for_zone(zone, _estimating_inputs(instance, module))

        assert est["available"] is True
        assert est["method"] == "daily_mirror"
        assert est["unavailable_reason"] is None

    async def test_the_live_bucket_lands_on_the_committed_bucket(self, coordinator):
        """And the number is the right one, not merely present.

        The equality is the point of mirroring the equation: an estimate that
        appeared but disagreed with the ledger would be worse than none, because
        with ``live_estimate_enabled`` on it both triggers and sizes real runs.
        """
        c, store = coordinator
        zone, module, instance = await _estimating_zone(
            c, store, 2.0, rain_at={20: 14.0}
        )

        est = c._intraday_for_zone(
            zone, _estimating_inputs(instance, module, forecast=_hourly_forecast())
        )
        data = await _committed(c, zone, now=WINDOW_END)

        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 2), abs=0.01
        )

    async def test_the_switch_makes_no_difference_to_the_equation(self, coordinator):
        """Same zone, same window, both settings of the switch: one ET.

        The tightest statement of the axis separation. If the switch ever leaks
        back into the source gate this diverges, whatever else still passes.
        """
        c, store = coordinator
        zone, module, instance = await _estimating_zone(
            c, store, 2.0, rain_at={20: 14.0}
        )

        off = c._intraday_for_zone(zone, _estimating_inputs(instance, module))
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: True})
        on = c._intraday_for_zone(zone, _estimating_inputs(instance, module))

        assert off["method"] == on["method"] == "daily_mirror"
        assert off["et_since"] == pytest.approx(on["et_since"])

    async def test_a_module_that_does_not_model_weather_is_still_refused(
        self, coordinator
    ):
        """The half of the old gate that stays.

        Static and Passthrough hand back a number the install supplied, so there
        is no equation to mirror. Dropping the whole predicate rather than its
        ``hourlycalculation`` half would have offered them one.
        """
        c, store = coordinator
        zone = await _zone(
            c,
            store,
            2.0,
            solrad=SOLRAD_behavior.EstimateFromTemp.value,
            module_name="Static",
        )
        module = store.get_module(zone[const.ZONE_MODULE])
        instance = Mock()
        instance._solrad_behavior = SOLRAD_behavior.EstimateFromTemp.value
        instance.forecast_days = 0

        assert c._daily_form_applies(zone, instance) is False
        est = c._intraday_for_zone(zone, _estimating_inputs(instance, module))
        assert est["available"] is False


class TestTheStoredBucketIsUntouched:
    """The blast radius the switch guards is the BALANCE FORM, and it is unmoved."""

    @pytest.mark.parametrize("hourly_calculation", [False, True])
    async def test_the_balance_form_still_follows_the_switch(
        self, coordinator, hourly_calculation
    ):
        c, store = coordinator
        await store.async_update_config(
            {const.CONF_HOURLY_CALCULATION: hourly_calculation}
        )
        zone, module, instance = await _estimating_zone(
            c, store, 2.0, rain_at={20: 14.0}
        )

        before = attr.asdict(store.zones[zone[const.ZONE_ID]])

        est = c._intraday_for_zone(zone, _estimating_inputs(instance, module))
        # The commit's OWN precipitation total, not the estimate's: the sub-step
        # gate refuses a window whose rain does not reconcile, so feeding it the
        # estimate's figure would answer a question about the estimate.
        weatherdata, _ = await c._aggregate_for_zone(zone, now=WINDOW_END)
        booked = weatherdata.get(const.MAPPING_PRECIPITATION) or 0.0
        commit_replays = c._substeps_for_zone(zone, booked, now=WINDOW_END) is not None

        assert est["available"] is True
        assert (est["balance_form"] == "replayed") is commit_replays
        assert commit_replays is hourly_calculation
        # The estimate is read-only, and the widened source gate does not change
        # that. Nothing about the zone moved.
        assert attr.asdict(store.zones[zone[const.ZONE_ID]]) == before

    async def test_the_commit_still_runs_the_daily_form_and_lumps(self, coordinator):
        """The blast radius the switch guards, stated at the commit itself.

        Both of the commit's own gates are asked directly: no summed-hourly ET,
        no sub-stepped balance. That is what a switch-off install had before the
        source gate widened, and it is what it has after.
        """
        c, store = coordinator
        zone, module, instance = await _estimating_zone(
            c, store, 2.0, rain_at={20: 14.0}
        )

        modinst = await c.getModuleInstanceByID(zone[const.ZONE_MODULE])
        weatherdata, _ = await c._aggregate_for_zone(zone, now=WINDOW_END)
        booked = weatherdata.get(const.MAPPING_PRECIPITATION) or 0.0

        assert c._hourly_et_for_zone(zone, modinst, now=WINDOW_END) is None
        assert c._substeps_for_zone(zone, booked, now=WINDOW_END) is None


class TestAZoneWithNoEstimateSaysWhy:
    """The other half: what an operator reads when there is still nothing to show.

    Every exit names its own missing precondition, so an empty sensor is a
    diagnosis rather than a guess between six of them.
    """

    async def test_a_never_calculated_zone_names_that(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        zone = dict(zone)
        zone[const.ZONE_LAST_CALCULATED] = None

        est = c._intraday_for_zone(zone, _estimating_inputs(instance, module))

        assert est["available"] is False
        assert est["unavailable_reason"] == REASON_NEVER_CALCULATED

    async def test_a_zone_with_no_source_left_names_that(self, coordinator):
        """A measured-radiation zone on a sensor-only install with the switch off.

        Both forms decline: the hourly one because the commit is not summing
        hourly ETo, the daily mirror because the commit is not estimating
        radiation either. That zone is still outside this change's population,
        and now it says so instead of publishing nothing.
        """
        c, store = coordinator
        zone = await _zone(
            c, store, 2.0, solrad=SOLRAD_behavior.DontEstimate.value, rain_at={20: 14.0}
        )

        est = c._intraday_for_zone(zone, _inputs())

        assert est["available"] is False
        assert est["unavailable_reason"] == REASON_NO_ET_SOURCE

    async def test_the_reason_reaches_the_coordinator_and_clears(self, coordinator):
        """Published from a cache of its own, so the payload the panel and the
        runner read still holds only zones that carry a number."""
        c, store = coordinator
        zone = await _zone(
            c, store, 2.0, solrad=SOLRAD_behavior.DontEstimate.value, rain_at={20: 14.0}
        )
        c._fetch_intraday_inputs = _returns(_inputs())
        c._resolve_zone_modules = _returns({})

        estimates = await c.async_get_zone_estimates()
        zone_id = str(zone[const.ZONE_ID])

        assert zone_id not in estimates
        assert c._zone_estimate_reasons[zone_id] == REASON_NO_ET_SOURCE

    async def test_the_warning_is_only_for_an_install_that_waters_on_it(
        self, coordinator, caplog
    ):
        """With the feature off the absence costs nothing -- the runner was never
        going to read the estimate -- so warning about it would be noise on every
        install that has never turned it on.
        """
        c, store = coordinator
        await _zone(
            c, store, 2.0, solrad=SOLRAD_behavior.DontEstimate.value, rain_at={20: 14.0}
        )
        c._fetch_intraday_inputs = _returns(_inputs())
        c._resolve_zone_modules = _returns({})

        caplog.clear()
        await c.async_get_zone_estimates()
        assert "no live estimate" not in caplog.text

        await store.async_update_config({const.CONF_LIVE_ESTIMATE_ENABLED: True})
        caplog.clear()
        await c.async_get_zone_estimates()
        assert REASON_NO_ET_SOURCE in caplog.text

        # Same reason on the next cycle: said once, not once a minute forever.
        caplog.clear()
        await c.async_get_zone_estimates()
        assert "no live estimate" not in caplog.text


def _returns(value):
    """An async stand-in for one of the estimate's input fetches."""

    async def _fetch(*args, **kwargs):
        return dict(value) if isinstance(value, dict) else value

    return _fetch


class TestTheImperialInstall:
    """The population this change serves is every shipped-default install, and
    the depth fields on half of them are stored in inches. The estimate converts
    to millimetres for the maths and back before publishing, so a unit bug here
    reads as a plausible number rather than as an error."""

    async def test_the_live_bucket_lands_on_the_committed_bucket(self, imperial):
        c, store = imperial
        zone, module, instance = await _estimating_zone(
            c, store, 0.08, rain_at={20: 14.0}
        )

        est = c._intraday_for_zone(
            zone, _estimating_inputs(instance, module, forecast=_hourly_forecast())
        )
        data = await _committed(c, zone, now=WINDOW_END)

        assert est["method"] == "daily_mirror"
        assert est["live_deficit"] == pytest.approx(
            round(data[const.ZONE_BUCKET], 3), abs=0.001
        )


class TestTheConditionsThatStillRefuseTheMirror:
    """Widening the gate changed WHO reaches the checks below it. They were
    unreachable on a switch-off install before, so they are pinned here."""

    async def test_forecast_days_without_a_forecast_refuse_it(self, coordinator):
        """A zone with forecast days passes the equation gate, and a missing
        forecast is what refuses it. A sensor-only install has none, and its
        commit skips the zone."""
        c, store = coordinator
        zone, module, instance = await _estimating_zone(
            c, store, 2.0, rain_at={20: 14.0}
        )
        instance.forecast_days = 2

        assert c._daily_form_applies(zone, instance) is True
        est = c._intraday_for_zone(zone, _estimating_inputs(instance, module))
        assert est.get("method") != "daily_mirror"

    async def test_a_measured_radiation_zone_is_still_refused(self, coordinator):
        """The deferred case, pinned as deferred.

        With the switch off this zone's commit runs the daily equation too, so
        the argument for the mirror applies to it as well. It stays out because
        composing its window needs a projected day total for RADIATION and not
        only for the temperature extremes, which is a construction this does not
        have. Asserted so the limit is a decision the suite holds rather than an
        absence anyone could close by accident.
        """
        c, store = coordinator
        zone = await _zone(c, store, 2.0, solrad=SOLRAD_behavior.DontEstimate.value)
        instance = Mock()
        instance._solrad_behavior = SOLRAD_behavior.DontEstimate.value
        instance.forecast_days = 0

        assert c._daily_form_applies(zone, instance) is False
        # And not by the module half, which is the same half an estimated-solar
        # zone passes: this refusal is the solar-behavior check alone.
        assert zone_module_models_weather(store, zone) is True

    async def test_a_module_instance_that_never_resolved_refuses_it(self, coordinator):
        c, store = coordinator
        zone, _module, _instance = await _estimating_zone(c, store, 2.0)

        assert c._daily_form_applies(zone, None) is False


class TestTheSensorPublishesTheReason:
    """The user-visible half. An operator reads this off the entity, not the log."""

    async def test_a_zone_with_no_estimate_yet_says_so(self, coordinator):
        """What every zone reads immediately after a restart, before the first
        refresh cycle. None there would say a value exists."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, solrad=SOLRAD_behavior.DontEstimate.value)
        c.hass.data[const.DOMAIN]["coordinator"] = c

        sensor = SmartIrrigationZoneLiveDeficitSensor(
            c.hass, "sensor.ip_live_deficit", zone
        )

        assert sensor.native_value is None
        assert (
            sensor.extra_state_attributes["unavailable_reason"] == REASON_NOT_COMPUTED
        )

    async def test_a_zone_that_declined_publishes_the_reason_it_declined_for(
        self, coordinator
    ):
        c, store = coordinator
        zone = await _zone(c, store, 2.0, solrad=SOLRAD_behavior.DontEstimate.value)
        c.hass.data[const.DOMAIN]["coordinator"] = c
        c._fetch_intraday_inputs = _returns(_inputs())
        c._resolve_zone_modules = _returns({})
        await c.async_get_zone_estimates()

        sensor = SmartIrrigationZoneLiveDeficitSensor(
            c.hass, "sensor.ip_live_deficit", zone
        )

        assert (
            sensor.extra_state_attributes["unavailable_reason"] == REASON_NO_ET_SOURCE
        )

    async def test_a_zone_with_a_value_publishes_no_reason(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        c.hass.data[const.DOMAIN]["coordinator"] = c
        c._zone_estimates_cache = {
            str(zone[const.ZONE_ID]): c._intraday_for_zone(
                zone, _estimating_inputs(instance, module)
            )
        }

        sensor = SmartIrrigationZoneLiveDeficitSensor(
            c.hass, "sensor.ip_live_deficit", zone
        )

        assert sensor.native_value is not None
        assert sensor.extra_state_attributes["unavailable_reason"] is None

    async def test_the_reasons_are_rebuilt_each_cycle_not_accumulated(
        self, coordinator
    ):
        """A zone that stops declining stops publishing a stale diagnosis."""
        c, store = coordinator
        zone = await _zone(c, store, 2.0, solrad=SOLRAD_behavior.DontEstimate.value)
        zone_id = str(zone[const.ZONE_ID])
        c._fetch_intraday_inputs = _returns(_inputs())
        c._resolve_zone_modules = _returns({})

        await c.async_get_zone_estimates()
        assert c._zone_estimate_reasons[zone_id] == REASON_NO_ET_SOURCE

        await store.async_delete_zone(zone[const.ZONE_ID])
        await c.async_get_zone_estimates()

        assert zone_id not in c._zone_estimate_reasons


class TestThePremiseTheChangeRestsOn:
    """The whole argument is that the switch does not decide the equation.

    Everything else here would still pass if the commit quietly summed hourly ETo
    for an estimated-solar zone, because the estimate would simply be mirroring a
    different thing consistently. This is the assertion that makes the mirror
    meaningful, and it has to be made with the switch ON, where the commit's
    hourly gate is actually reached.
    """

    async def test_the_hourly_form_declines_on_the_solar_check_with_the_switch_on(
        self, coordinator
    ):
        c, store = coordinator
        await store.async_update_config({const.CONF_HOURLY_CALCULATION: True})
        zone, _module, _instance = await _estimating_zone(c, store, 2.0)
        modinst = await c.getModuleInstanceByID(zone[const.ZONE_MODULE])

        # The switch is on, so the first gate passes and the refusal below can
        # only be the solar-behavior check.
        assert hourly_calculation_enabled(store) is True
        assert c._hourly_et_for_zone(zone, modinst, now=WINDOW_END) is None


class TestTheRemainingReasons:
    """The reason strings are published as an interface, so each one is driven.

    Three of them are reachable only through a malformed or half-built zone,
    which is exactly the state a reader of the attribute is trying to diagnose.
    """

    async def test_a_site_with_no_coordinates_says_so(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        c._effective_latitude = None
        c._effective_longitude = None
        inputs = _estimating_inputs(instance, module)
        inputs["client"] = None

        est = c._intraday_for_zone(zone, inputs)

        assert est["available"] is False
        assert est["unavailable_reason"] == REASON_NO_COORDINATES

    async def test_a_zone_with_no_bucket_says_so(self, coordinator):
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        zone = dict(zone)
        zone[const.ZONE_BUCKET] = None

        est = c._intraday_for_zone(zone, _estimating_inputs(instance, module))

        assert est["available"] is False
        assert est["unavailable_reason"] == REASON_NO_BUCKET

    async def test_a_reduction_that_raises_says_so(self, coordinator):
        """The estimate swallows exceptions by design, so without this the
        attribute would read as an answer while the reduction was failing."""
        c, store = coordinator
        zone, module, instance = await _estimating_zone(c, store, 2.0)
        c._aggregate_live_window = Mock(side_effect=RuntimeError("boom"))

        est = c._intraday_for_zone(zone, _estimating_inputs(instance, module))

        assert est["available"] is False
        assert est["unavailable_reason"] == REASON_FAILED
