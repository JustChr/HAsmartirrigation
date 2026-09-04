"""Rotation re-pricing: what a mid-run live estimate may change, and when.

The rotation re-prices every zone at every return to it. That is what lets rain
part-way through a multi-hour ring shorten — or drop — the zones it has made
unnecessary. Two properties of that re-price, both wrong on a live rotation and
both invisible to a run that never repeats a zone:

- **A started zone is gated on capacity, not on the trigger threshold.** The
  rotation commits every slot's water, so a zone's own credits lift its live
  deficit. Applying the trigger there refills the zone to its threshold instead
  of to capacity and ends the run part-done. Sequential never showed this: a
  zone it starts runs to completion.
- **The re-price runs again after the absorption wait.** The pre-wait re-price
  exists so the deadline check is not slept out; on its own it means rain
  landing *during* a zone's pause is not seen until that zone's next lap.
"""

import datetime
from unittest.mock import AsyncMock, Mock

from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const

UTC = datetime.timezone.utc

# Zone geometry chosen so the arithmetic is readable: 10 L/min over 100 m² is a
# precipitation rate of 6 mm/h, so 1.0 mm of deficit is exactly 600 s of run and
# every duration below is a plain fraction of that.
MM_PER_SECOND = 1.0 / 600.0


class _FakeStore:
    def __init__(self, zones, config):
        self.zones = {int(z[const.ZONE_ID]): dict(z) for z in zones}
        self.config = config

    def get_zone(self, zone_id):
        z = self.zones.get(int(zone_id))
        return dict(z) if z is not None else None

    async def async_get_zones(self):
        return [dict(z) for z in self.zones.values()]


def _zone(zid=0, **kw):
    z = {
        const.ZONE_ID: zid,
        const.ZONE_NAME: f"Z{zid}",
        const.ZONE_DURATION: 600,
        const.ZONE_LINKED_ENTITY: f"switch.z{zid}",
        const.ZONE_STATE: const.ZONE_STATE_AUTOMATIC,
        const.ZONE_SIZE: 100.0,
        const.ZONE_THROUGHPUT: 10.0,
        const.ZONE_MULTIPLIER: 1.0,
        const.ZONE_LEAD_TIME: 0,
        const.ZONE_MAXIMUM_DURATION: None,
        const.ZONE_BUCKET: -1.0,
        const.ZONE_BUCKET_THRESHOLD: -0.9,
    }
    z.update(kw)
    return z


class _Rig:
    """A one-zone rotation driven by a fake clock and a scripted estimate.

    ``deficit`` starts at the zone's bucket and rises with the water the
    rotation actually delivers, exactly as the live estimate does once
    ``_commit_run_progress`` books each slot. ``rain`` is the test's lever.
    """

    def __init__(self, coord, state, slots):
        self.coord = coord
        self.state = state
        self.slots = slots

    @property
    def watered(self):
        return sum(self.slots)


def _rig(
    monkeypatch,
    zone=None,
    *,
    absorption_minutes=0,
    rain_at_slot=None,
    rain_during_wait=None,
    rain_up_front=0.0,
):
    """Build a rotating coordinator over one timed zone under the live gate."""
    monkeypatch.setattr(
        "custom_components.irrigation_plus.irrigation.async_dispatcher_send", Mock()
    )
    zone = zone if zone is not None else _zone()
    clock = {"t": datetime.datetime(2026, 8, 7, 4, 0, tzinfo=UTC)}

    # The rotation's slot sleeps are mocked out, so no real time passes; drive a
    # clock the slots advance instead (see test_run_deadline.TestRotatingDeadline).
    class _Clock:
        @staticmethod
        def utcnow():
            return clock["t"]

        @staticmethod
        def now():
            return clock["t"]

    monkeypatch.setattr("custom_components.irrigation_plus.irrigation.dt_util", _Clock)

    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    hass = Mock()
    hass.config = Mock()
    hass.config.units = METRIC_SYSTEM
    hass.services.async_call = AsyncMock()
    coord.hass = hass
    coord.store = _FakeStore(
        [zone],
        Mock(
            zone_sequencing="rotating",
            zone_sequencing_max_consecutive_duration=5,  # 300 s slots
            zone_sequencing_min_absorption_time=absorption_minutes,
            live_estimate_enabled=True,
        ),
    )

    state = {"delivered_s": 0.0, "rain_mm": rain_up_front}
    slots = []

    async def _estimates():
        deficit = (
            (zone[const.ZONE_BUCKET] or 0.0)
            + state["delivered_s"] * MM_PER_SECOND
            + state["rain_mm"]
        )
        return {str(zone[const.ZONE_ID]): {"live_deficit": deficit}}

    async def _slot(zid, seconds):
        slots.append(seconds)
        clock["t"] += datetime.timedelta(seconds=seconds)
        state["delivered_s"] += seconds
        if rain_at_slot and len(slots) in rain_at_slot:
            state["rain_mm"] += rain_at_slot[len(slots)]
        return False

    async def _sleep(seconds):
        if rain_during_wait is not None:
            state["rain_mm"] += rain_during_wait

    monkeypatch.setattr(
        "custom_components.irrigation_plus.irrigation.asyncio.sleep", _sleep
    )

    coord.async_refresh_zone_estimates = _estimates
    coord._register_active_run = Mock()
    coord._unregister_active_run = Mock()
    coord._run_stopped = Mock(return_value=False)
    coord._run_trigger = Mock(return_value="schedule")
    coord._note_si_valve = Mock()
    coord._confirm_valve_running = AsyncMock(return_value=True)
    coord._sleep_or_stopped = AsyncMock(side_effect=_slot)
    coord._clear_zone_fault = Mock()
    coord._commit_run_progress = AsyncMock()
    coord._timed_volume_l = Mock(return_value=12.0)
    coord._credited_depth_native = Mock(return_value=0.1)
    coord._run_ceiling = Mock(return_value=0.0)
    coord._record_run = AsyncMock()
    return _Rig(coord, state, slots)


async def _run(rig):
    await rig.coord._run_rotation([dict(rig.coord.store.get_zone(0))])


class TestStartedZoneRefillsToCapacity:
    """A zone the rotation has already watered is gated on capacity."""

    async def test_its_own_credits_do_not_end_a_started_zone(self, monkeypatch):
        # The defect this class exists for. 600 s of need at a threshold of
        # -0.9 mm: one 300 s slot delivers 0.5 mm and lifts the live deficit to
        # -0.5, above the trigger. Applying the trigger to a started zone ends
        # it there with half its water undelivered — a refill to the threshold,
        # which the design explicitly rejected.
        rig = _rig(monkeypatch)
        await _run(rig)
        assert rig.watered == 600
        assert rig.coord._record_run.await_count == 1
        assert (
            rig.coord._record_run.await_args.kwargs["result"]
            == const.RUN_RESULT_COMPLETED
        )

    async def test_rain_still_shortens_a_started_zone(self, monkeypatch):
        # Sizing survives; only the trigger gate is dropped. 0.25 mm of rain
        # after the first slot leaves -0.25 mm owed = 150 s, so the second slot
        # is half length instead of full.
        rig = _rig(monkeypatch, rain_at_slot={1: 0.25})
        await _run(rig)
        assert rig.slots == [300, 150]

    async def test_a_started_zone_is_dropped_once_it_reaches_capacity(
        self, monkeypatch
    ):
        # 0.6 mm of rain on top of the 0.5 mm delivered puts the zone at +0.1:
        # nothing is owed, the re-priced duration is 0, and the zone ends with
        # the water it has.
        rig = _rig(monkeypatch, rain_at_slot={1: 0.6})
        await _run(rig)
        assert rig.slots == [300]
        kwargs = rig.coord._record_run.await_args.kwargs
        assert kwargs["result"] == const.RUN_RESULT_PARTIAL
        assert kwargs["detail"] == const.SKIP_REASON_NO_DEMAND
        assert kwargs["actual_s"] == 300

    async def test_a_zone_that_has_not_watered_is_still_dropped_by_the_trigger(
        self, monkeypatch
    ):
        # The trigger still owns zones the run has not reached: rain before the
        # first slot leaves -0.5 mm, short of the -0.9 threshold, so the zone
        # never opens its valve even though it is not yet at capacity.
        rig = _rig(monkeypatch, rain_up_front=0.5)
        await _run(rig)
        assert rig.slots == []
        rig.coord._sleep_or_stopped.assert_not_awaited()


class TestRepriceAfterTheAbsorptionWait:
    """Rain during a zone's pause is seen when the pause ends."""

    async def test_rain_during_the_wait_is_seen_at_the_end_of_it(self, monkeypatch):
        # Turn 1 waters a 300 s slot. Turn 2 re-prices (pre-wait, so a deadline
        # is never slept out), then sleeps its absorption pause — and the rain
        # lands inside that sleep. Without a second re-price the zone waters a
        # whole further slot on a soil profile that is already full, and only
        # drops one lap later.
        rig = _rig(monkeypatch, absorption_minutes=10, rain_during_wait=0.6)
        await _run(rig)
        assert rig.slots == [300]
        kwargs = rig.coord._record_run.await_args.kwargs
        assert kwargs["result"] == const.RUN_RESULT_PARTIAL
        assert kwargs["detail"] == const.SKIP_REASON_NO_DEMAND

    async def test_a_flow_zone_is_not_repriced_across_its_wait(self, monkeypatch):
        # The re-price is for timed zones only — a flow zone delivers to a
        # volume fixed in litres at dispatch and has no entry in the timed
        # bookkeeping at all. Re-pricing one across its absorption pause
        # therefore does not merely mis-size it: it raises, and a raise inside
        # the rotation strands the ring.
        rig = _rig(monkeypatch, absorption_minutes=10)
        flow = _zone(
            1,
            **{
                const.ZONE_FLOW_SENSOR: "sensor.flow1",
                const.ZONE_MAXIMUM_DURATION: 600,
                const.ZONE_BUCKET: -1.0,
            },
        )
        rig.coord.store.zones[1] = flow
        rig.coord._irrigate_zone_flow_slot = AsyncMock(return_value=0.0)
        rig.coord._depth_from_volume_native = Mock(return_value=0.0)
        rig.coord._set_zone_fault = Mock()

        await rig.coord._run_rotation([dict(rig.coord.store.get_zone(0)), dict(flow)])

        # Two slots against a 600 s safety cap, and the ring came back for the
        # second one across a pause rather than dying in it.
        assert rig.coord._irrigate_zone_flow_slot.await_count == 2

    async def test_an_uneventful_wait_still_finishes_the_zone(self, monkeypatch):
        # The second re-price must not become a second gate: with nothing
        # changing across the pause the zone still runs to capacity.
        rig = _rig(monkeypatch, absorption_minutes=10)
        await _run(rig)
        assert rig.watered == 600
        assert (
            rig.coord._record_run.await_args.kwargs["result"]
            == const.RUN_RESULT_COMPLETED
        )
