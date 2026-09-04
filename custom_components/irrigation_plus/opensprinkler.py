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
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from . import const
from .run_chain import ChainPolicy, register_chain_policy
from .run_watch import (
    NO_INFO_STATES as _NO_INFO_STATES,
)
from .run_watch import (
    WatchPolicy,
    planned_seconds,
    queue_deadline_seconds,
    register_watch_policy,
)

if TYPE_CHECKING:
    from .run_window import StationFacts

_LOGGER = logging.getLogger(__name__)

# The station's observation lifecycle lives in run_watch.py, shared with the
# other modes that hand a run to a controller owning both queue and valve. This
# is what OpenSprinkler contributes to it: the controller acknowledges a queued
# run by putting a non-zero program id on the station, so a station that is off
# with no program id has been dropped rather than merely not reached yet.
WATCH_POLICY = WatchPolicy(
    mode=const.WATERING_MODE_OPENSPRINKLER,
    acknowledges=True,
    give_up_problem=const.PROBLEM_STATION_NEVER_RAN,
    accept_seconds=const.OPENSPRINKLER_ACCEPT_SECONDS,
    # A station that is ALREADY watering has nothing to give up on. Arming the
    # acceptance grace on the resume path was a real defect, not a timing choice:
    # only _watch_observed_start cancels that timer, and the resume path skips it
    # because the run already has an observed start. So any station with more
    # than the grace left when Home Assistant restarted was written off five
    # minutes later while it was still watering — settled as a partial, its
    # bucket credit reversed, and a station_never_ran fault raised against a zone
    # that was at that moment delivering water. Irrigation runs are routinely
    # longer than five minutes, so "restart during a cycle" was the whole
    # trigger. A resumed run is bounded by its cosmetic-finish backstop, which
    # _os_resume_run arms for the remaining time.
    arm_give_up_after_start=False,
)
register_watch_policy(WATCH_POLICY)

# The dispatch chain lives in run_chain.py. ``os-chain:`` is kept as this mode's
# master-hold token because its tests assert on it and its behaviour predates the
# extraction; a new mode has no such history and names its own.
CHAIN_POLICY = ChainPolicy(
    mode=const.WATERING_MODE_OPENSPRINKLER,
    label="OpenSprinkler",
    token_prefix="os-chain:",
)
register_chain_policy(CHAIN_POLICY)

# Re-exported: ``run_state`` and the tests import it from here, and it was this
# module's before the extraction.
__all__ = [
    "OpenSprinklerMixin",
    "entity_is_station",
    "is_opensprinkler_zone",
    "observed_start_iso",
    "queue_deadline_seconds",
    "resolve_running_sensor",
    "station_attributes",
    "zone_watch_entity",
]


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


def _same_config_entry(hass, source_entity_id: str):
    """Which controller ``source`` belongs to, and a predicate for its siblings.

    A second controller repeats every station index and numbers its groups from
    zero again, so the config entry is what makes any sibling lookup unique. An
    entity missing from the registry cannot be attributed to either controller
    and is rejected; an unregistered SOURCE has nothing to compare against, so
    every candidate passes and a single-controller install still resolves.
    """
    registry = er.async_get(hass)
    source = registry.async_get(source_entity_id)
    want_entry = source.config_entry_id if source is not None else None

    def matches(entity_id: str) -> bool:
        if want_entry is None:
            return True
        entry = registry.async_get(entity_id)
        return entry is not None and entry.config_entry_id == want_entry

    return want_entry, matches


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

    _, same_entry = _same_config_entry(hass, station_entity_id)
    for state in hass.states.async_all(BINARY_SENSOR_DOMAIN):
        candidate = state.attributes
        if candidate.get(const.OPENSPRINKLER_ATTR_TYPE) != (
            const.OPENSPRINKLER_TYPE_STATION
        ):
            continue
        if candidate.get(const.OPENSPRINKLER_ATTR_INDEX) != index:
            continue
        if not same_entry(state.entity_id):
            continue
        return state.entity_id
    return None


def _controller_of(hass, station_entity_id: str) -> tuple[str, float] | None:
    """The controller ``station_entity_id`` belongs to, and its station delay.

    None when the controller cannot be seen — it is unavailable (Home Assistant
    drops its attributes then), it is not registered, or the OpenSprinkler
    integration is too old to publish the delay. The caller treats that as "the
    controller did not answer" rather than substituting a delay of zero, which
    would price a chain shorter than the controller runs it.
    """
    entry_id, same_entry = _same_config_entry(hass, station_entity_id)
    for state in hass.states.async_all(SWITCH_DOMAIN):
        if state.attributes.get(const.OPENSPRINKLER_ATTR_TYPE) != (
            const.OPENSPRINKLER_TYPE_CONTROLLER
        ):
            continue
        if not same_entry(state.entity_id):
            continue
        delay = state.attributes.get(const.OPENSPRINKLER_ATTR_STATION_DELAY)
        if delay is None:
            continue
        try:
            return (entry_id or state.entity_id, float(delay))
        except (TypeError, ValueError):
            return None
    return None


def station_facts(hass, zone: dict) -> StationFacts | None:
    """What the controller says about ``zone``'s station, for the wall clock.

    Returns a :class:`run_window.StationFacts`, or None for a zone that is not
    an OpenSprinkler station at all, so a caller can ask about every zone it
    plans. For a station zone the answer is always facts, whose group is None
    when the controller did not fully answer — see there for why that is never
    rounded down to a real group id.

    Both halves have to be readable or neither is used. A group without its
    delay would partition the run correctly and then under-charge every boundary
    inside it, and an under-estimate is the direction that finishes after the
    deadline.

    Read per plan rather than cached, which is what makes a group changed in the
    controller's own interface take effect on the next run without a restart.
    """
    # Imported here, not at module scope: run_window imports this module for
    # is_opensprinkler_zone, so a top-level import back would be a cycle that
    # fails whenever run_window is the one imported first.
    from .run_window import StationFacts

    if not is_opensprinkler_zone(zone):
        return None
    entity_id = zone.get(const.ZONE_LINKED_ENTITY)
    attributes = station_attributes(hass, entity_id) or {}
    group = attributes.get(const.OPENSPRINKLER_ATTR_GROUP)
    try:
        group = int(group) if group is not None else None
    except (TypeError, ValueError):
        group = None
    controller = _controller_of(hass, entity_id) if group is not None else None
    if controller is None:
        _LOGGER.debug(
            "Station %s did not answer with a group and a station delay; "
            "pricing its dispatch track as a chain",
            entity_id,
        )
        return StationFacts()
    controller_id, delay = controller
    return StationFacts(group=group, delay_seconds=delay, controller_id=controller_id)


def station_facts_by_zone(hass, zones: list) -> dict:
    """:func:`station_facts` for every station zone in ``zones``, by zone id.

    The wall-clock module cannot read an entity, so anything pricing a run from
    zone dicts alone gathers the controller's answers through here first.
    """
    facts = {}
    for zone in zones:
        answer = station_facts(hass, zone)
        if answer is not None:
            facts[int(zone.get(const.ZONE_ID))] = answer
    return facts


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
    here or they report the zone as watering forever.

    Gated on what the entity IS, not on the zone's watering mode, because the
    case that needs it most is the one where the mode is wrong: a zone left in
    classic mode with a station linked. Its run is refused, but the sensor would
    still mirror the enabled switch and sit on for ever, and observed watering
    would treat that as a valve nobody closes. Reading the station's real running
    sensor is the truthful answer either way — if something else runs that
    station, water really is flowing on that zone.
    """
    if not isinstance(zone, dict):
        return None
    linked = zone.get(const.ZONE_LINKED_ENTITY)
    if is_opensprinkler_zone(zone) or entity_is_station(hass, linked):
        return resolve_running_sensor(hass, linked)
    return linked


class OpenSprinklerMixin:
    """Dispatch to, and observe, OpenSprinkler stations.

    Mixed into SmartIrrigationCoordinator alongside SelfClosingMixin, whose run
    record, bucket crediting and restart contract this mode reuses wholesale.
    """

    # --- derivation ---------------------------------------------------------

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

    # The watcher registry, the subscription and the timer are the shared
    # engine's (run_watch.RunWatchMixin). These spellings stay because the rest
    # of this mode — and the self-closing lifecycle it reuses — call them by
    # name, and because "cancel this station's watch" reads better at those call
    # sites than the generic verb.

    def _os_watchers(self) -> dict:
        """Lazy {zone_id: watcher} of live station subscriptions.

        A watcher owns a state subscription and at most one timer, and is the
        only thing that ends a queued run — so it must be re-created on restart
        for every persisted record (see ``_os_resume_run``) or that record would
        block its zone until the deadline in the persisted list expires.
        """
        return self._watchers()

    def _os_cancel_watch(self, zone_id) -> None:
        """Cancel-and-pop a zone's subscription and timer (no-op if absent)."""
        self._watch_cancel(zone_id)

    async def async_abort_opensprinkler_runs(self, reason: str, *, settle=True) -> bool:
        """Stop every station this coordinator started, and settle its runs.

        Teardown otherwise reaches the tracker and never the controller. The
        controller owns the queue from the moment it is dispatched and steps
        through it on its own clock, so dropping the watchers leaves the water
        running with nothing supervising it — a station was seen starting 25
        minutes after the Home Assistant that queued it had been killed.

        Deliberately NOT called from a plain reload or a restart. Those are
        covered by ``_os_resume_run``, which re-adopts the run with its watcher,
        its master hold and its deadline intact, and cutting the run short there
        would waste water on every options change. This is for the cases where
        nothing will ever adopt the run: the integration being removed or
        disabled, and Home Assistant stopping for good.

        Works from the persisted run records rather than the in-memory chain, so
        it still finds the stations after ``async_teardown_opensprinkler_watchers``
        has run, and so it covers runs the controller has queued but not started.

        ``settle`` reconciles each run's optimistic bucket credit down to what
        was actually delivered. Skipped when the store is about to be deleted,
        where the write would be pointless.

        Returns True if anything was stopped. Never raises: a failure here must
        not be able to block an unload or a shutdown.
        """
        try:
            runs = await self._sc_active_runs()
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not read active runs to stop OpenSprinkler")
            return False

        targets = [
            r
            for r in runs
            if r.get(const.RUN_MODE) == const.WATERING_MODE_OPENSPRINKLER
            and r.get(const.RUN_ZONE_ID) is not None
        ]
        if not targets:
            return False

        # Before any stop, so a finalisation below cannot advance the chain and
        # dispatch the very next station on the way out.
        await self._os_chain_release()

        stopped = False
        for run in targets:
            zid = int(run.get(const.RUN_ZONE_ID))
            zone = self.store.get_zone(zid) or {}
            try:
                await self._os_dispatch_stop(zone)
                stopped = True
                _LOGGER.warning(
                    "Zone %s: stopping its OpenSprinkler station because %s. The "
                    "controller would otherwise have watered on unsupervised, "
                    "with nothing left to enforce the run's finish time",
                    zid,
                    reason,
                )
            except Exception:  # noqa: BLE001
                _LOGGER.exception(
                    "Zone %s: could not stop its OpenSprinkler station; it may "
                    "still be watering",
                    zid,
                )
            if not settle:
                continue
            try:
                # close_valve=False: the stop above already reached the
                # controller, and this path must not drive linked_entity, which
                # for this mode is the station's *enabled* switch.
                await self.async_stop_self_closing(zid, close_valve=False)
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Zone %s: could not settle its stopped run", zid)
        return stopped

    def async_teardown_opensprinkler_watchers(self) -> None:
        """Drop every station subscription and pending chain (called on unload)."""
        for zone_id in list(self._os_watchers()):
            self._os_cancel_watch(zone_id)
        # The chains live in memory only, so unload ends them. Every mode's, not
        # just this one's: unload is the coordinator going away, and a service
        # chain left armed would fire a timer into a torn-down coordinator.
        self._chain_teardown()

    # --- sequencing ---------------------------------------------------------
    #
    # The chain itself lives in run_chain.py, shared with every self-closing mode
    # whose queue Irrigation Plus owns. These are the spellings this mode was
    # written with, kept as delegates so its behaviour is unchanged and its tests
    # remain the oracle for the engine — including ``os-chain:``, the master-hold
    # token its tests assert on, which is why the prefix is a policy field.

    def _os_chain_state(self):
        """This mode's chain."""
        return self._chain_state(const.WATERING_MODE_OPENSPRINKLER)

    async def async_dispatch_opensprinkler_zones(self, zones: list, *, trigger) -> None:
        """Start OpenSprinkler zones under the configured zone sequencing.

        The controller decides for itself whether stations run one at a time or
        together — it is a per-station flag in its own configuration, and the
        integration exposes no way to set it — so ``parallel`` here means "hand
        the controller everything and let it schedule", which is what a station's
        own sequential-group setting then governs.

        ``sequential`` is the case Irrigation Plus has to enforce itself: it
        dispatches one station and holds the rest back until that run finalises,
        so the setting means the same thing on a controller whose stations are
        flagged to run concurrently as on one whose stations are not.
        """
        await self.async_dispatch_chained_zones(
            zones, mode=const.WATERING_MODE_OPENSPRINKLER, trigger=trigger
        )

    async def _os_chain_advance(self, finished_zone_id=None) -> None:
        """Start the next chained station or rotation slot, or end the cycle."""
        await self._chain_advance(const.WATERING_MODE_OPENSPRINKLER, finished_zone_id)

    def _os_drop_from_cycle(self, zone_id) -> None:
        """Take one zone out of the running cycle, leaving the others alone."""
        self._chain_drop_zone(zone_id)

    async def _os_chain_release(self) -> None:
        """Drop the chain and its master hold."""
        await self._chain_release(const.WATERING_MODE_OPENSPRINKLER)

    async def _os_start_rotation(self, zones: list, *, trigger) -> None:
        """Split every station's duration into slots and start the first one.

        The classic rotation (``irrigation._run_rotation``) is a loop that opens
        and closes ``linked_entity`` itself, which for a station switch would
        rewrite the controller's configuration and water nothing — see this
        module's header. So the same behaviour is built on top of the observation
        lifecycle instead; run_chain.py is that build.
        """
        await self._chain_start_rotation(
            zones, mode=const.WATERING_MODE_OPENSPRINKLER, trigger=trigger
        )

    def _os_rotation_next(self, rotation):
        """The station whose turn it is, or how long until one is due."""
        return self._chain_rotation_next(rotation)

    async def _os_rotation_advance(self) -> None:
        """Dispatch the next slot, wait out an absorption window, or finish."""
        await self._chain_rotation_advance(const.WATERING_MODE_OPENSPRINKLER)

    def _os_cancel_absorption(self) -> None:
        """Cancel-and-drop a pending absorption wait (no-op if none is armed)."""
        self._chain_cancel_absorption(const.WATERING_MODE_OPENSPRINKLER)

    def _os_arm_absorption(self, delay: float) -> None:
        """Wait ``delay`` before looking for the next slot."""
        self._chain_arm_absorption(const.WATERING_MODE_OPENSPRINKLER, delay)

    def _os_arm_timer(self, zone_id, delay: float, reason: str) -> None:
        """(Re)arm the watcher's single timer."""
        self._watch_arm_timer(zone_id, delay, reason)

    async def _os_start_watch(
        self, zone_id, running_entity: str, planned_seconds: float, *, accepted: bool
    ) -> None:
        """Watch a station for the run's start and end.

        ``accepted`` seeds the reconciliation state: False right after dispatch
        (the controller has not acknowledged the run yet), True when resuming a
        record whose station is already reporting a run.
        """
        await self._watch_start(
            zone_id, running_entity, planned_seconds, accepted=accepted
        )

    async def _os_evaluate(self, zone_id, state) -> None:
        """Advance a watched run from one observation of its station."""
        await self._watch_evaluate(zone_id, state)

    async def _watch_observed_start_iso(self, zone_id, run: dict, entity: str) -> str:
        """Prefer the controller's own reported start over the observation time.

        The one place this mode refines the shared engine's timing. See
        ``observed_start_iso`` for why the difference decides whether a full run
        is recorded as completed or as an early stop.

        Gated on the run's own mode rather than left to fall through harmlessly
        on the strength of a non-station entity carrying no ``start_time``. That
        is true today, but it is a property of the entities other modes happen to
        watch, not something this mode may assume of them.
        """
        if run.get(const.RUN_MODE) != const.WATERING_MODE_OPENSPRINKLER:
            return await super()._watch_observed_start_iso(zone_id, run, entity)
        return observed_start_iso(self.hass, entity, planned_seconds(run))

    async def _os_observed_start(self, zone_id, run: dict) -> None:
        """The station started watering: from here the run is a normal timed run."""
        await self._watch_observed_start(zone_id, run)

    async def _os_finish(self, zone_id, run: dict) -> None:
        """The station stopped. Settle the run against what it actually delivered."""
        await self._watch_finish(zone_id, run)

    async def _os_give_up(self, zone_id, reason: str) -> None:
        """End a run whose station never watered, and undo its optimistic credit."""
        await self._watch_give_up(zone_id, reason)

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
