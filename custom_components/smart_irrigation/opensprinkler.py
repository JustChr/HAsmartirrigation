"""OpenSprinkler station mode: dispatch a station run, observe when it waters.

A zone in ``WATERING_MODE_OPENSPRINKLER`` names an OpenSprinkler station switch
(``switch.<station>_station_enabled``) in its ``linked_entity``. Everything else
is derived from that entity's state attributes at dispatch time, so a controller
that was offline when the zone was configured still works later.

Why this is not just self-closing mode with a different service
---------------------------------------------------------------
A controller queues what it is given. Whether a station waits for the ones before
it or runs alongside them is a per-station flag in the controller's own
configuration, so ``queue_option: append`` can leave a zone watering immediately
or hours later, and the same four zones behave differently on two controllers.
Nothing about a run may therefore be measured from the moment it was dispatched:
a queued zone would finalise, credit its usage and release its accounting long
before its water flowed. The run is driven by the station's own running sensor
instead, and the dispatch time is used for exactly one thing — deciding when to
give up waiting.

That flag is also why ``zone_sequencing`` is applied here rather than left to the
hardware: the integration exposes no way to set it, so a controller whose
stations are flagged to run concurrently would ignore the setting entirely. See
``async_dispatch_opensprinkler_zones``.

Why the station switch must never be turned on
----------------------------------------------
``StationEnabledSwitch.async_turn_on`` calls ``station.enable()``, which rewrites
the station's *enabled* configuration flag on the controller and does not open the
valve. A zone that reached the classic runner with a station switch as its linked
entity would rewrite controller configuration, never irrigate, and still report a
confirmed run, because the switch does go ``on``. ``_sc_is_self_closing`` covers
this mode precisely so every path that would drive ``linked_entity`` directly
(the metered runner, the rotating/sequential/parallel dispatch, ``async_stop_zone``)
returns before it gets there.
"""

from __future__ import annotations

import logging
import uuid

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.core import Event, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util

from . import const

_LOGGER = logging.getLogger(__name__)

# States that carry no attributes: HA drops an entity's extra_state_attributes
# while it is unavailable, so a station's program id reads as absent rather than
# as 0. Never mistake "cannot see the controller" for "the controller dropped the
# run" — the first is transient, the second finalises the run.
_NO_INFO_STATES = ("unavailable", "unknown")
# The station's running sensor is a binary_sensor; these are its "watering" states.
_RUNNING_STATES = ("on", "open", "opening")


def is_opensprinkler_zone(zone: dict) -> bool:
    """True if this zone is driven by an OpenSprinkler station."""
    return (
        isinstance(zone, dict)
        and zone.get(const.ZONE_WATERING_MODE) == const.WATERING_MODE_OPENSPRINKLER
    )


def station_attributes(hass, entity_id: str) -> dict | None:
    """The station attributes of ``entity_id``, or None if it is not a station.

    None also covers an unavailable entity, whose attributes HA has dropped.
    """
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None or state.state in _NO_INFO_STATES:
        return None
    attributes = state.attributes
    if (
        attributes.get(const.OPENSPRINKLER_ATTR_TYPE)
        != const.OPENSPRINKLER_TYPE_STATION
    ):
        return None
    return dict(attributes)


def entity_is_station(hass, entity_id: str) -> bool:
    """True if ``entity_id`` is an OpenSprinkler station entity right now."""
    return station_attributes(hass, entity_id) is not None


def resolve_running_sensor(hass, station_entity_id: str) -> str | None:
    """The binary_sensor reporting whether this station is watering.

    Matched on ``opensprinkler_type`` + ``index`` within the same config entry
    rather than by rewriting the entity id, so a renamed station entity still
    resolves. Returns None when the controller is unreachable (its entities carry
    no attributes then) or the sensor is disabled — the caller treats that as a
    zone problem rather than falling back to something that might not be the
    right station.
    """
    attributes = station_attributes(hass, station_entity_id)
    if attributes is None:
        return None
    index = attributes.get(const.OPENSPRINKLER_ATTR_INDEX)
    if index is None:
        return None

    registry = er.async_get(hass)
    source = registry.async_get(station_entity_id)
    want_entry = source.config_entry_id if source is not None else None

    for state in hass.states.async_all(BINARY_SENSOR_DOMAIN):
        candidate = state.attributes
        if candidate.get(const.OPENSPRINKLER_ATTR_TYPE) != (
            const.OPENSPRINKLER_TYPE_STATION
        ):
            continue
        if candidate.get(const.OPENSPRINKLER_ATTR_INDEX) != index:
            continue
        if want_entry is not None:
            entry = registry.async_get(state.entity_id)
            # A second controller would repeat every station index, so the config
            # entry is what makes the match unique. An entity missing from the
            # registry cannot be attributed to either and is skipped.
            if entry is None or entry.config_entry_id != want_entry:
                continue
        return state.entity_id
    return None


def observed_start_iso(hass, running_entity: str, planned_seconds: float) -> str:
    """When the station started watering, ISO-8601 UTC, for RUN_OBSERVED_START.

    Prefers the controller's own ``start_time`` over the moment Home Assistant
    noticed the station was on. The integration polls (5 s by default), so both
    ends of a run are seen up to a poll late; a window measured between the two
    sightings is short as often as it is long, by up to a poll interval either
    way. One second of slack in the completion test cannot absorb that, so a run
    the controller finished in full is recorded as an early stop roughly half the
    time — and because the delivered fraction is clamped at 1.0 above but scaled
    down below, the error biases the bucket credit one way. Live against a real
    controller, two of four full 60 s runs came back as ``partial``.

    Anchoring to the controller's start makes the measured window at least the
    true one, so a full run always reads as complete and always credits 1.0.

    Falls back to now when the attribute is absent (an older firmware, a station
    whose payload lacks it) or implausible — it is built from the controller's
    clock and its configured timezone offset, and a wrong one there must not be
    able to claim a run began in the future or hours before it could have.
    """
    now = dt_util.utcnow()
    attributes = station_attributes(hass, running_entity) or {}
    raw = attributes.get(const.OPENSPRINKLER_ATTR_START_TIME)
    if raw:
        reported = dt_util.parse_datetime(str(raw))
        if reported is not None:
            slack = const.OPENSPRINKLER_START_TIME_SLACK_SECONDS
            age = (now - dt_util.as_utc(reported)).total_seconds()
            # The station is running as this is called, so a credible start lies
            # between "just now" and one planned window ago, plus clock slack.
            if -slack <= age <= max(0.0, planned_seconds) + slack:
                return dt_util.as_utc(reported).isoformat()
            _LOGGER.debug(
                "Station %s reported start %s is %.0fs from now, outside the "
                "plausible window for a %.0fs run; using the observation time",
                running_entity,
                raw,
                age,
                planned_seconds,
            )
    return now.isoformat()


def zone_watch_entity(hass, zone: dict) -> str | None:
    """The entity that is on while this zone is watering.

    ``linked_entity`` carries that invariant for every other mode, but an
    OpenSprinkler station switch reports whether the station is *enabled* — on
    permanently on a working install. Consumers that mean "is water flowing"
    (the zone's own running binary sensor, observed watering) must come through
    here or they report every OpenSprinkler zone as watering forever.
    """
    if not isinstance(zone, dict):
        return None
    if not is_opensprinkler_zone(zone):
        return zone.get(const.ZONE_LINKED_ENTITY)
    return resolve_running_sensor(hass, zone.get(const.ZONE_LINKED_ENTITY))


def queue_deadline_seconds(runs: list, run: dict) -> float:
    """Seconds after dispatch at which a run that never watered is written off.

    Derived rather than fixed, because what a queued run waits for is the runs
    ahead of it: a four-zone cycle on real deficits is around 288 minutes and a
    seven-zone one considerably longer, so any single constant is either far too
    short for a full cycle or far too long for one zone. The margin absorbs the
    controller's own inter-station delays (master on/off delays, its programs).

    This is only a backstop. A run the controller drops is seen within one poll,
    as the station's program id returning to 0; this bound is what ends a run
    whose station entity stopped reporting altogether.
    """
    planned = _planned_seconds(run)
    ahead = 0.0
    for other in runs or []:
        if not isinstance(other, dict) or other is run:
            continue
        if other.get(const.RUN_MODE) != const.WATERING_MODE_OPENSPRINKLER:
            continue
        if other.get(const.RUN_ZONE_ID) == run.get(const.RUN_ZONE_ID):
            continue
        ahead += _planned_seconds(other)
    return (
        const.OPENSPRINKLER_ACCEPT_SECONDS
        + ahead
        + planned
        + const.OPENSPRINKLER_QUEUE_MARGIN_SECONDS
    )


def _planned_seconds(run: dict) -> float:
    try:
        return max(0.0, float(run.get(const.RUN_PLANNED_SECONDS) or 0))
    except (TypeError, ValueError):
        return 0.0


class OpenSprinklerMixin:
    """Dispatch to, and observe, OpenSprinkler stations.

    Mixed into SmartIrrigationCoordinator alongside SelfClosingMixin, whose run
    record, bucket crediting and restart contract this mode reuses wholesale.
    """

    # --- derivation ---------------------------------------------------------

    @staticmethod
    def _os_is_opensprinkler(zone: dict) -> bool:
        return is_opensprinkler_zone(zone)

    def _os_resolve(self, zone: dict) -> tuple[str | None, str | None]:
        """(station entity, running sensor) for this zone, (None, None) on failure.

        Resolved at dispatch, never at config time, so a controller that was
        offline when the zone was set up still works once it comes back.
        """
        station = zone.get(const.ZONE_LINKED_ENTITY)
        if not station:
            return None, None
        running = resolve_running_sensor(self.hass, station)
        if running is None:
            return station, None
        return station, running

    def _os_zone_watch_entity(self, zone: dict) -> str | None:
        """Coordinator-side accessor for :func:`zone_watch_entity`."""
        return zone_watch_entity(self.hass, zone)

    # --- actuation ----------------------------------------------------------

    async def _os_dispatch_open(self, zone: dict, seconds: int) -> None:
        """Queue the station run on the controller.

        ``entity_id`` addresses the station; ``run_station``'s schema is built
        with ``cv.make_entity_service_schema``, so any extra key (the zone_id /
        zone_name the plain service adapter injects) is rejected before the call
        reaches the controller.
        """
        await self.hass.services.async_call(
            const.OPENSPRINKLER_DOMAIN,
            const.OPENSPRINKLER_SERVICE_RUN_STATION,
            {
                "entity_id": zone.get(const.ZONE_LINKED_ENTITY),
                const.OPENSPRINKLER_FIELD_RUN_SECONDS: seconds,
                const.OPENSPRINKLER_FIELD_QUEUE_OPTION: (
                    const.OPENSPRINKLER_QUEUE_APPEND
                ),
            },
        )

    async def _os_dispatch_stop(self, zone: dict) -> None:
        """Stop this station on the controller."""
        await self.hass.services.async_call(
            const.OPENSPRINKLER_DOMAIN,
            const.OPENSPRINKLER_SERVICE_STOP,
            {"entity_id": zone.get(const.ZONE_LINKED_ENTITY)},
        )

    # --- observation --------------------------------------------------------

    def _os_watchers(self) -> dict:
        """Lazy {zone_id: watcher} of live station subscriptions.

        A watcher owns a state subscription and at most one timer, and is the
        only thing that ends a queued run — so it must be re-created on restart
        for every persisted record (see ``_os_resume_run``) or that record would
        block its zone until the deadline in the persisted list expires.
        """
        watchers = getattr(self, "_os_station_watchers", None)
        if watchers is None:
            watchers = self._os_station_watchers = {}
        return watchers

    def _os_cancel_watch(self, zone_id) -> None:
        """Cancel-and-pop a zone's subscription and timer (no-op if absent)."""
        watcher = self._os_watchers().pop(int(zone_id), None)
        if watcher is None:
            return
        unsub = watcher.get("unsub")
        if unsub is not None:
            unsub()
        cancel = watcher.get("cancel")
        if cancel is not None:
            cancel()

    def async_teardown_opensprinkler_watchers(self) -> None:
        """Drop every station subscription and pending chain (called on unload)."""
        for zone_id in list(self._os_watchers()):
            self._os_cancel_watch(zone_id)
        # The chain lives in memory only, so unload ends it. The master hold goes
        # with the coordinator; there is nothing left that could release it.
        chain = self._os_chain_state()
        chain["zones"], chain["trigger"], chain["token"] = [], None, None

    # --- sequencing ---------------------------------------------------------

    def _os_chain_state(self) -> dict:
        """Lazy dispatch chain: zones still to start, and the cycle's master hold.

        In memory only, deliberately. Persisting it would mean re-dispatching
        after a restart, and this mode's contract is that Smart Irrigation never
        actuates a station on the way back up — see ``_os_resume_run``. The cost
        is that a restart mid-cycle abandons whatever had not been dispatched
        yet, which is the trade sequential sequencing makes: under ``parallel``
        the whole cycle sits in the controller's queue and survives a crash,
        under ``sequential`` only the run that already started does.
        """
        state = getattr(self, "_os_pending_chain", None)
        if state is None:
            state = self._os_pending_chain = {
                "zones": [],
                "trigger": None,
                "token": None,
            }
        return state

    async def async_dispatch_opensprinkler_zones(self, zones: list, *, trigger) -> None:
        """Start OpenSprinkler zones under the configured zone sequencing.

        The controller decides for itself whether stations run one at a time or
        together — it is a per-station flag in its own configuration, and the
        integration exposes no way to set it — so ``parallel`` here means "hand
        the controller everything and let it schedule", which is what a station's
        own sequential-group setting then governs.

        ``sequential`` is the case Smart Irrigation has to enforce itself: it
        dispatches one station and holds the rest back until that run finalises,
        so the setting means the same thing on a controller whose stations are
        flagged to run concurrently as on one whose stations are not.
        """
        zones = [z for z in zones if self._os_is_opensprinkler(z)]
        if not zones:
            return
        sequencing = self.store.config.zone_sequencing
        if sequencing == const.CONF_ZONE_SEQUENCING_PARALLEL or len(zones) == 1:
            for zone in zones:
                await self.async_run_self_closing(zone, trigger=trigger)
            return
        if sequencing == const.CONF_ZONE_SEQUENCING_ROTATING:
            # Rotating splits each zone's duration into slots with absorption
            # waits between turns. That is a different dispatch shape, not a
            # chain, and is not implemented for stations yet — say so rather than
            # let it look like it was honoured.
            _LOGGER.warning(
                "Zone sequencing '%s' is not implemented for OpenSprinkler "
                "stations; running the %s station zones sequentially instead",
                const.CONF_ZONE_SEQUENCING_ROTATING,
                len(zones),
            )

        state = self._os_chain_state()
        state["zones"] = [int(z.get(const.ZONE_ID)) for z in zones[1:]]
        state["trigger"] = trigger
        if state["token"] is None:
            # One hold for the whole chain, as the classic sequential path does:
            # the gaps between runs are part of the cycle, and a per-run hold
            # would drop the master in each of them.
            state["token"] = f"os-chain:{uuid.uuid4().hex[:8]}"
            await self.async_master_acquire(state["token"])
        _LOGGER.info(
            "OpenSprinkler: dispatching zone %s, %s more chained behind it",
            zones[0].get(const.ZONE_ID),
            len(state["zones"]),
        )
        if not await self.async_run_self_closing(zones[0], trigger=trigger):
            # Refused (an unresolvable station); the chain must not stall on it.
            await self._os_chain_advance()

    async def _os_chain_advance(self) -> None:
        """Start the next chained zone, or end the chain.

        Safe to call from every finalisation path: it returns while any station
        run is still in flight, so whichever of them fires first advances once.
        """
        state = self._os_chain_state()
        if not state["zones"] and state["token"] is None:
            return
        for run in await self._sc_active_runs():
            if run.get(const.RUN_MODE) == const.WATERING_MODE_OPENSPRINKLER:
                return
        while state["zones"]:
            zone_id = state["zones"].pop(0)
            zone = self.store.get_zone(zone_id) or {}
            if not is_opensprinkler_zone(zone):
                continue
            if (zone.get(const.ZONE_DURATION) or 0) <= 0:
                continue
            if self.zone_run_in_flight(zone_id):
                continue
            if await self.async_run_self_closing(zone, trigger=state["trigger"]):
                return
            # Refused: fall through to the next rather than stalling the chain.
        await self._os_chain_release()

    async def _os_chain_release(self) -> None:
        """Drop the chain and its master hold."""
        state = self._os_chain_state()
        state["zones"], state["trigger"] = [], None
        token, state["token"] = state["token"], None
        if token:
            await self.async_master_release(token)

    def _os_arm_timer(self, zone_id, delay: float, reason: str) -> None:
        """(Re)arm the watcher's single timer."""
        watcher = self._os_watchers().get(int(zone_id))
        if watcher is None:
            return
        cancel = watcher.get("cancel")
        if cancel is not None:
            cancel()

        async def _expired(_now):
            await self._os_give_up(zone_id, reason)

        watcher["cancel"] = async_call_later(self.hass, max(0.0, delay), _expired)

    async def _os_start_watch(
        self, zone_id, running_entity: str, planned_seconds: float, *, accepted: bool
    ) -> None:
        """Watch a station for the run's start and end.

        ``accepted`` seeds the reconciliation state: False right after dispatch
        (the controller has not acknowledged the run yet), True when resuming a
        record whose station is already reporting a run.
        """
        zid = int(zone_id)
        self._os_cancel_watch(zid)
        watcher = {
            "entity": running_entity,
            "planned": float(planned_seconds or 0),
            "accepted": bool(accepted),
            "unsub": None,
            "cancel": None,
        }
        self._os_watchers()[zid] = watcher
        watcher["unsub"] = async_track_state_change_event(
            self.hass, [running_entity], self._os_state_changed
        )
        self._os_arm_timer(
            zid, const.OPENSPRINKLER_ACCEPT_SECONDS, const.PROBLEM_STATION_NEVER_RAN
        )
        # The zone's own running sensor and the observed-watering map both derive
        # this same entity, and both may have been built before the OpenSprinkler
        # integration published it. Nudge them now that it is known to resolve.
        async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zid)
        # The controller refreshes as soon as run_station returns, so the station
        # may already be queued (or even running, on an empty queue) before the
        # subscription above exists. Evaluate the current state once so that run
        # is not missed entirely.
        await self._os_evaluate(zid, self.hass.states.get(running_entity))

    @callback
    def _os_state_changed(self, event: Event) -> None:
        """A watched station changed state."""
        entity_id = event.data.get("entity_id")
        for zone_id, watcher in list(self._os_watchers().items()):
            if watcher.get("entity") != entity_id:
                continue
            self.hass.async_create_task(
                self._os_evaluate(zone_id, event.data.get("new_state"))
            )

    async def _os_evaluate(self, zone_id, state) -> None:
        """Advance a watched run from one observation of its station."""
        zid = int(zone_id)
        watcher = self._os_watchers().get(zid)
        if watcher is None:
            return
        run = await self._sc_find_run(zid)
        if run is None:
            # The run was finalised by another path (a user stop, a restart
            # reconcile). Nothing left to observe.
            self._os_cancel_watch(zid)
            return

        if state is None or state.state in _NO_INFO_STATES:
            # No information: the controller is unreachable or the sensor has not
            # been created yet. Never read this as "the run was dropped" — the
            # deadline timer is what ends a run whose station stops reporting.
            return

        running = state.state in _RUNNING_STATES
        program_id = state.attributes.get(const.OPENSPRINKLER_ATTR_PROGRAM_ID)
        observed_start = run.get(const.RUN_OBSERVED_START)

        if running:
            if observed_start is None:
                await self._os_observed_start(zid, run)
            return

        if observed_start is not None:
            # The station stopped. The controller ended the run, on time or
            # early; either way it is over now.
            await self._os_finish(zid, run)
            return

        if not watcher["accepted"]:
            if program_id:
                # The controller has acknowledged the run. From here on its
                # program id going back to 0 is meaningful.
                watcher["accepted"] = True
                runs = await self._sc_active_runs()
                self._os_arm_timer(
                    zid,
                    queue_deadline_seconds(runs, run)
                    - self._sc_elapsed(run.get(const.RUN_STARTED)),
                    const.PROBLEM_STATION_NEVER_RAN,
                )
            return

        if not program_id:
            # Acknowledged, then dropped without ever watering: a controller-side
            # rain delay, a water level of 0, or a stop-all. The zone was credited
            # optimistically at dispatch, so this has to unwind that credit rather
            # than wait the deadline out.
            await self._os_give_up(zid, const.PROBLEM_STATION_NEVER_RAN)

    async def _os_observed_start(self, zone_id, run: dict) -> None:
        """The station started watering: from here the run is a normal timed run."""
        zid = int(zone_id)
        watcher = self._os_watchers().get(zid)
        planned = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
        zone = self.store.get_zone(zid) or {}

        # The controller's own start, not the moment this observation arrived —
        # see observed_start_iso for why the difference decides whether a full
        # run is recorded as completed or as an early stop.
        started = observed_start_iso(
            self.hass,
            (watcher or {}).get("entity") or run.get(const.RUN_WATCH_ENTITY),
            planned,
        )
        runs = [
            (
                dict(r, **{const.RUN_OBSERVED_START: started})
                if r.get(const.RUN_ZONE_ID) == run.get(const.RUN_ZONE_ID)
                else r
            )
            for r in await self._sc_active_runs()
        ]
        await self._sc_persist_runs(runs)

        # The suppression window taken at dispatch is measured from dispatch, so
        # for a queued run it has already expired — and observed watering is now
        # pointed at this very sensor (zone_watch_entity). Re-take it for the real
        # run window so the zone's own run is not also credited as external.
        self._note_si_valve(zid, planned)
        # Flow sampling deliberately starts HERE, not at dispatch: a meter seeded
        # while the zone was still queued would sample a window that mostly
        # precedes the water.
        await self._sc_start_flow_sampling(zone)
        if watcher is not None:
            cancel = watcher.get("cancel")
            if cancel is not None:
                cancel()
            watcher["cancel"] = None
        # Backstop only. The station going off is the primary finish signal; this
        # covers a missed transition.
        self._sc_schedule_cleanup(zid, planned)
        _LOGGER.info(
            "Zone %s: OpenSprinkler station started watering (planned %.0fs)",
            zid,
            planned,
        )

    async def _os_finish(self, zone_id, run: dict) -> None:
        """The station stopped. Settle the run against what it actually delivered."""
        zid = int(zone_id)
        self._os_cancel_watch(zid)
        planned = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
        elapsed = self._sc_elapsed(run.get(const.RUN_OBSERVED_START))
        # A station that ran its full window is a completed run; one the
        # controller cut short settles like an early stop, which reconciles the
        # optimistic credit down to what was delivered. One second of slack keeps
        # a run that ended exactly on time out of the partial path.
        if elapsed + 1 >= planned:
            await self._sc_finish_run(zid)
        else:
            await self.async_stop_self_closing(zid, close_valve=False)

    async def _os_give_up(self, zone_id, reason: str) -> None:
        """End a run whose station never watered, and undo its optimistic credit."""
        zid = int(zone_id)
        self._os_cancel_watch(zid)
        run = await self._sc_find_run(zid)
        if run is None:
            return
        zone = self.store.get_zone(zid) or {}
        # elapsed is 0 for a run with no observed start, so this reconciles the
        # bucket all the way back to RUN_PRE_BUCKET and logs a run that delivered
        # nothing. No stop is sent: the station never opened, and stopping would
        # only affect whatever the controller is running right now.
        await self.async_stop_self_closing(
            zid, close_valve=False, detail=const.RUN_DETAIL_STATION_NEVER_RAN
        )
        self._set_zone_fault(zid, reason)
        self._sc_fire(
            const.EVENT_ZONE_PROBLEM,
            {
                "zone_id": zid,
                "zone": zone.get(const.ZONE_NAME),
                "entity_id": zone.get(const.ZONE_LINKED_ENTITY),
                "reason": reason,
            },
        )
        _LOGGER.warning(
            "Zone %s: OpenSprinkler station never watered (%s); the run was "
            "written off and its bucket credit reversed",
            zid,
            reason,
        )

    # --- restart ------------------------------------------------------------

    async def _os_resume_run(self, run: dict) -> None:
        """Re-arm the observation for one persisted run after a restart.

        Never re-opens: the controller owns both the queue and the valve, so an
        interrupted run is either still in its queue, still watering, or gone —
        and all three are observations, not actions.
        """
        zone_id = run.get(const.RUN_ZONE_ID)
        planned = float(run.get(const.RUN_PLANNED_SECONDS) or 0)
        watch_entity = run.get(const.RUN_WATCH_ENTITY)
        observed_start = run.get(const.RUN_OBSERVED_START)

        if not watch_entity:
            # Written before this field existed, or dispatched by a build that
            # could not resolve the sensor. Re-derive; give up only if the zone
            # is gone too.
            zone = self.store.get_zone(zone_id) or {}
            watch_entity = zone_watch_entity(self.hass, zone)
        if not watch_entity:
            await self._os_give_up(zone_id, const.PROBLEM_STATION_UNRESOLVED)
            return

        if observed_start is not None:
            elapsed = self._sc_elapsed(observed_start)
            if elapsed >= planned:
                await self._sc_finish_run(zone_id)
                return
            # Still inside the window the station is watering for. The master hold
            # lived in memory only, so re-take it for the remainder.
            await self.async_master_acquire(self._sc_master_token(zone_id))
            await self._os_start_watch(zone_id, watch_entity, planned, accepted=True)
            self._sc_schedule_cleanup(zone_id, planned - elapsed)
            return

        # Never observed a start. The acceptance grace restarts from now rather
        # than from dispatch: the OpenSprinkler integration may not have finished
        # loading yet, and its station would then read as "no run" purely because
        # nothing has published it.
        await self.async_master_acquire(self._sc_master_token(zone_id))
        await self._os_start_watch(zone_id, watch_entity, planned, accepted=False)
