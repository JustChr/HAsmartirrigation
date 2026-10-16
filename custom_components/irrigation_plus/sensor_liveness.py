"""When a weather sensor stops reporting: liveness, the outage record, the notice.

A sensor group carries a field's last value forward while nothing new arrives (the
per-field boundary row, ``last_entry``). That is right for a value that is merely
steady and wrong for a sensor that died. This module tells the two apart by the
sensor's HA *device* -- at a living station some value reports or changes within
``SENSOR_STALE_AFTER_SECONDS``, a quiet rain gauge included -- records every outage
longer than that on the sensor group, and tells the user: a repair issue per group
while an outage is open, and a bus event when one starts and when it ends (#188).

The outage record says when a sensor fell silent and the notice tells the user. A
group that keeps a silent sensor's last value calculates as before; for a group
that pauses it, ``zone_blocked_spans`` turns the record into the time its
calculation and its live estimate do not book.

The rules are plain functions, testable without a running Home Assistant; the
``SensorLivenessMixin`` at the end is the coordinator glue.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from . import const
from .helpers import STAMP_FROM_STORE, coerce_stamp, local_naive_now
from .weather_aggregate import effective_aggregate

_LOGGER = logging.getLogger(__name__)

STALE_AFTER = timedelta(seconds=const.SENSOR_STALE_AFTER_SECONDS)
RETENTION = timedelta(days=const.SENSOR_OUTAGE_RETENTION_DAYS)


def sensor_fields_by_entity(mappings_config: dict) -> dict[str, tuple[str, ...]]:
    """``{entity_id: fields}`` for every field this sensor group reads from an entity.

    Weather-service and static fields have no device to fall silent; a legacy bare
    string is not a field config. ``input_number`` is a value set by hand, which
    never reports on its own, so it is exempt.
    """
    found: dict[str, list[str]] = {}
    for field_name, cfg in mappings_config.items():
        if not isinstance(cfg, dict):
            continue
        if cfg.get(const.MAPPING_CONF_SOURCE) != const.MAPPING_CONF_SOURCE_SENSOR:
            continue
        entity_id = cfg.get(const.MAPPING_CONF_SENSOR)
        if not entity_id:
            continue
        if entity_id.split(".", 1)[0] in const.SENSOR_LIVENESS_EXEMPT_DOMAINS:
            continue
        found.setdefault(entity_id, []).append(field_name)
    return {entity_id: tuple(fields) for entity_id, fields in found.items()}


@dataclass(frozen=True)
class Seen:
    """One entity's state as liveness reads it, stamps naive on HA's clock."""

    entity_id: str
    valid: bool  # not unavailable/unknown
    reported: datetime  # State.last_reported
    changed: datetime  # State.last_changed


def last_sign_of_life(
    own: Seen | None, siblings: list[Seen], remembered: datetime | None
) -> datetime | None:
    """The newest report that vouches for a field, or None when there is none.

    ``own`` is the field's entity (None when it does not exist). While it is
    missing, unavailable or unknown the field is silent whatever its device does,
    so only the remembered sign counts. Otherwise its device vouches for it: at a
    living station some value reports or changes within the limit, while a quiet
    rain gauge on the same device may not change for days. ``remembered`` is the
    sign stored at the previous check, so an outage that spans a restart keeps its
    start; a sign never moves backwards.
    """
    candidates = [remembered] if remembered is not None else []
    if own is not None and own.valid:
        candidates.append(own.reported)
        candidates.extend(s.reported for s in siblings if s.valid)
    return max(candidates) if candidates else None


def first_report_after(
    own: Seen | None, siblings: list[Seen], start: datetime
) -> datetime | None:
    """When the field spoke again after ``start``.

    Its own entity's change marks its return when there is one: a return from
    unavailable is a change, and the device's other entities may have changed
    while this one was dead. A quiet field whose value did not change on return
    (a rain gauge at zero) has none, so the device's earliest change since then
    stands in -- a returning device's first report changes most of its values.
    Unavailable or unknown states do not count. None when nothing changed since
    ``start``. This only dates a return; whether the outage has ended,
    ``advance_outages`` decides from the field's last sign of life.
    """
    if own is not None and own.valid and own.changed > start:
        return own.changed
    stamps = [s.changed for s in siblings if s.valid and s.changed > start]
    return min(stamps) if stamps else None


@dataclass(frozen=True)
class Outage:
    """One stretch in which a sensor entity stayed silent for longer than the limit.

    ``start`` is its last sign of life, ``end`` its first report afterwards, or
    the moment its group stopped reading it (None while it is still silent).
    Stored as ISO strings on HA's clock: the frame the reading buffer's row
    stamps are in.
    """

    entity_id: str
    device_id: str | None
    fields: tuple[str, ...]
    start: datetime
    end: datetime | None = None

    def to_store(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "device_id": self.device_id,
            "fields": list(self.fields),
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end is not None else None,
        }

    @classmethod
    def from_store(cls, raw) -> Outage | None:
        """Read one stored record; anything unreadable is dropped, never raised.

        Unreadable: not a dict, no entity id, no readable start, an end that is
        present but no stamp, ``fields`` that is not a list of strings (a missing
        or falsy value means none).
        NOT-TO-DO: do not let this raise. The outage record is read in the setup and
        in the configuration paths; a file edited by hand, or written by another
        build of this integration, must cost one entry, not the integration.
        """
        if not isinstance(raw, dict) or not raw.get("entity_id"):
            return None
        fields = raw.get("fields") or []
        if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
            return None
        start = coerce_stamp(raw.get("start"), STAMP_FROM_STORE)
        if start is None:
            return None
        end = coerce_stamp(raw.get("end"), STAMP_FROM_STORE)
        if end is None and raw.get("end") is not None:
            return None  # a closed record must not come back open
        return cls(
            entity_id=str(raw["entity_id"]),
            device_id=raw.get("device_id"),
            fields=tuple(fields),
            start=start,
            end=end,
        )


def outages_of(mapping: dict) -> list[Outage]:
    """The readable outages stored on a sensor group; never raises."""
    stored = mapping.get(const.MAPPING_SENSOR_OUTAGES)
    if not isinstance(stored, list):
        return []
    return [outage for raw in stored if (outage := Outage.from_store(raw)) is not None]


def group_pauses(mapping: dict) -> bool:
    """Whether a sensor group pauses a silent sensor rather than keep its last value.

    Anything but a stored ``pause`` keeps: a group written before the setting
    existed, a test double without it, or a value edited by hand.
    """
    return mapping.get(const.MAPPING_ON_SILENT_SENSOR) == const.ON_SILENT_SENSOR_PAUSE


def cuts_field(field: str, mappings_config: dict) -> bool:
    """Whether a pausing group leaves this field's silent time out of its booking.

    Every field but a cumulative rain gauge (aggregate ``delta``): what a gauge
    shows after its return is rain it measured, only delivered late, so its
    silent time is not cut. ``zone_blocked_spans``, the one gate of the commit
    and the live estimate, and the notice both ask here, so the notice says a
    value is no longer used only where the calculation cuts it.
    """
    return (
        effective_aggregate(field, mappings_config)
        != const.MAPPING_CONF_AGGREGATE_DELTA
    )


def blocked_spans(
    outages: list[Outage], start: datetime, end: datetime
) -> dict[str, tuple[tuple[datetime, datetime], ...]]:
    """Each field's blocked time inside ``[start, end)``: where it is not measured.

    An outage blocks from its start plus ``STALE_AFTER`` -- the first hours are
    bridged with the last value, as they are for the notice -- up to its end,
    half-open so that the reading of the return counts. An open outage blocks up
    to ``end``. A field's spans are merged and cut to the window; a field left
    without a span is not listed, and only the fields an outage recorded are.
    """
    found: dict[str, list[tuple[datetime, datetime]]] = {}
    for outage in outages:
        lo = max(outage.start + STALE_AFTER, start)
        hi = min(outage.end if outage.end is not None else end, end)
        if hi <= lo:
            continue
        for field in outage.fields:
            found.setdefault(field, []).append((lo, hi))
    return {field: _merged(spans) for field, spans in found.items()}


def valid_share(blocked: dict, fields, start: datetime, end: datetime) -> float:
    """The part of ``[start, end)`` in which all ``fields`` are unblocked at once.

    The intersection of their valid times, not the smallest single share: two
    fields silent at different hours leave less than either alone. A field
    without spans is valid throughout; an empty window has nothing to cut.
    """
    length = (end - start).total_seconds()
    if length <= 0:
        return 1.0
    spans = _merged([span for field in fields for span in blocked.get(field, ())])
    gone = sum((hi - lo).total_seconds() for lo, hi in spans)
    return max(0.0, (length - gone) / length)


def zone_blocked_spans(store, zone: dict, start, end) -> dict | None:
    """A pausing group's blocked time in one zone's window ``[start, end)``, or None.

    The one place the commit and the live estimate take their spans from, so both
    leave out the same time. A free function over the store rather than a method:
    the live estimate's mixin runs on its own in its tests, where a cross-mixin
    call raises and is swallowed as a failed estimate. ``start`` is the caller's
    -- the commit's watermark, the estimate's anchor -- and ``end`` its ``now``,
    which also ends an open outage.

    None leaves a window exactly as it always was: a group that keeps, a zone
    without a group or a start, an empty window, or one no outage reaches. Which
    fields are cut, ``cuts_field`` says: never a cumulative rain gauge.
    """
    mapping_id = zone.get(const.ZONE_MAPPING)
    if mapping_id is None:
        return None
    mapping = store.get_mapping(mapping_id)
    if not mapping or not group_pauses(mapping):
        return None
    start = coerce_stamp(start, STAMP_FROM_STORE)
    end = coerce_stamp(end, STAMP_FROM_STORE)
    if start is None or end is None:
        return None
    config = mapping.get(const.MAPPING_MAPPINGS) or {}
    blocked = {
        field: spans
        for field, spans in blocked_spans(outages_of(mapping), start, end).items()
        if cuts_field(field, config)
    }
    return blocked or None


def _merged(spans) -> tuple[tuple[datetime, datetime], ...]:
    """Sorted spans with every overlap or touch joined into one."""
    merged: list[tuple[datetime, datetime]] = []
    for lo, hi in sorted(spans):
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return tuple(merged)


@dataclass(frozen=True)
class Evidence:
    """What one check learned about one sensor-mapped entity."""

    fields: tuple[str, ...]
    device_id: str | None
    last: datetime | None  # its last sign of life; None: no evidence at all
    recovered: datetime | None = None  # first report after an open outage began


def advance_outages(
    outages: list[Outage],
    evidence: dict[str, Evidence],
    now: datetime,
    *,
    stale_after: timedelta = STALE_AFTER,
    retention: timedelta = RETENTION,
) -> tuple[list[Outage], list[Outage], list[Outage]]:
    """One check over one sensor group's outage record: ``(outages, opened, closed)``.

    Closes an open outage once a sign newer than its start appears: at the
    field's return when that is known (``Evidence.recovered``: its own change,
    else its device's earliest), else at that sign.
    Ends one whose entity the group no longer reads (its sensor was replaced or
    unmapped by a path that did not empty the record) at ``now``, so it does not
    stay open. Then, for each entity left without an open outage, opens one if
    its last sign is older than ``stale_after`` (strictly: a silence of exactly
    the limit is still bridged), starting AT that sign. Drops closed outages
    that ended more than ``retention`` ago; open ones stay whatever their age.
    """
    kept: list[Outage] = []
    opened: list[Outage] = []
    closed: list[Outage] = []
    still_open: set[str] = set()
    for outage in outages:
        if outage.end is not None:
            if now - outage.end <= retention:
                kept.append(outage)
            continue
        seen = evidence.get(outage.entity_id)
        if seen is None:
            ended = replace(outage, end=now)
            kept.append(ended)
            closed.append(ended)
            continue
        if seen.last is not None and seen.last > outage.start:
            back = seen.recovered
            end = back if back is not None and back > outage.start else seen.last
            ended = replace(outage, end=end)
            kept.append(ended)
            closed.append(ended)
            continue
        kept.append(outage)
        still_open.add(outage.entity_id)
    for entity_id, seen in evidence.items():
        if entity_id in still_open or seen.last is None:
            continue
        if now - seen.last > stale_after:
            outage = Outage(entity_id, seen.device_id, seen.fields, seen.last)
            kept.append(outage)
            opened.append(outage)
    return kept, opened, closed


def stale_issue_placeholders(group_name: str, outages: list[Outage]) -> dict | None:
    """The repair issue's placeholders for a group's OPEN outages, or None."""
    silent = sorted(
        (o for o in outages if o.end is None), key=lambda o: (o.start, o.entity_id)
    )
    if not silent:
        return None
    return {
        "group": group_name,
        "entities": ", ".join(f"{o.entity_id} ({', '.join(o.fields)})" for o in silent),
        "since": silent[0].start.strftime("%Y-%m-%d %H:%M"),
    }


def outage_event_payload(mapping_id, group_name: str, outage: Outage) -> dict:
    """The bus event's data for an outage starting (no end yet) or ending.

    Its stamps carry Home Assistant's offset: a consumer may read a naive one in
    the process's zone, which need not be Home Assistant's.
    """
    return {
        "mapping_id": mapping_id,
        "mapping": group_name,
        "entity_id": outage.entity_id,
        "device_id": outage.device_id,
        "fields": list(outage.fields),
        "since": dt_util.as_local(outage.start).isoformat(),
        "until": (
            dt_util.as_local(outage.end).isoformat() if outage.end is not None else None
        ),
        "stale": outage.end is None,
    }


def _on_has_clock(stamp: datetime) -> datetime:
    """An HA state stamp (aware, UTC) in the buffer's frame: HA's wall time, naive."""
    return dt_util.as_local(stamp).replace(tzinfo=None)


def seen_from_state(state) -> Seen | None:
    """A liveness snapshot of one HA state, or None when the entity has no state."""
    if state is None:
        return None
    return Seen(
        entity_id=state.entity_id,
        valid=state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN),
        reported=_on_has_clock(state.last_reported),
        changed=_on_has_clock(state.last_changed),
    )


def _entities_of_device(hass, entity_id: str) -> tuple[str | None, list[str]]:
    """The entity's HA device and the other enabled sensors on it that vouch for it.

    Home Assistant attaches helpers to devices: a utility meter or Riemann
    integral to its source's device, a template sensor to the one picked for it.
    They can write on a schedule of their own, and an update entity of the
    device's integration can too; neither says anything about the
    measurements. So only sensors and binary sensors vouch, and only those of the
    integration entry that owns the device -- which lets a station vouch for a
    helper mapped from it -- or of the mapped entity's own entry, which still counts
    where the device is shared and another integration owns it, or no owner is
    recorded. Reached through this one function so the tests can stand in for it:
    conftest may replace ``homeassistant.helpers`` with a mock (see repairs.py),
    hence the imports inside.
    """
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    entry = registry.async_get(entity_id)
    device_id = entry.device_id if entry is not None else None
    if not device_id:
        return None, []
    device = dr.async_get(hass).async_get(device_id)
    # The integration entry that owns the device: config_entry_id in newer Home
    # Assistant, primary_config_entry before. A helper's link changes neither.
    owner = getattr(device, "config_entry_id", None) or getattr(
        device, "primary_config_entry", None
    )
    vouching = {entry.config_entry_id, owner} - {None}
    return device_id, [
        sibling.entity_id
        for sibling in er.async_entries_for_device(registry, device_id)
        if sibling.entity_id != entity_id
        and sibling.config_entry_id in vouching
        and sibling.entity_id.split(".", 1)[0] in const.SENSOR_LIVENESS_SIBLING_DOMAINS
    ]


def _issue_registry():
    """Home Assistant's issue registry module.

    Reached through this one function so the tests can stand in for it: conftest
    may replace ``homeassistant.helpers`` with a mock (see repairs.py).
    """
    from homeassistant.helpers import issue_registry as ir

    return ir


class SensorLivenessMixin:
    """Coordinator glue: the periodic check, the record, the notice and the event."""

    async def async_setup_sensor_liveness(self) -> None:
        """Arm the periodic check; show at once what the record still holds open.

        The first checks wait out a grace after setup so integrations can create
        their entities first; an outage that was open before a restart is shown
        straight away, because the record already says the sensor is silent.
        """
        self.async_teardown_sensor_liveness()
        self._sensor_liveness_armed_at = local_naive_now() + timedelta(
            seconds=const.SENSOR_LIVENESS_STARTUP_GRACE_SECONDS
        )
        for mapping in await self.store.async_get_mappings():
            try:
                outages = outages_of(mapping)
                if not any(o.end is None for o in outages):
                    continue  # nothing to show: a notice exists only for an open outage
                mapping_id = mapping[const.MAPPING_ID]
                self._sync_stale_issue(
                    mapping_id,
                    mapping.get(const.MAPPING_NAME) or str(mapping_id),
                    outages,
                )
            except Exception:
                # Only a notice: it must not keep the integration from setting up.
                _LOGGER.exception(
                    "Could not show the open outages of sensor group %s",
                    mapping.get(const.MAPPING_ID),
                )
        self._sensor_liveness_unsub = async_track_time_interval(
            self.hass,
            self._async_sensor_liveness_tick,
            timedelta(seconds=const.SENSOR_LIVENESS_INTERVAL_SECONDS),
        )

    @callback
    def async_teardown_sensor_liveness(self) -> None:
        """Cancel the periodic check (unload, reload)."""
        unsub = getattr(self, "_sensor_liveness_unsub", None)
        if unsub is not None:
            unsub()
        self._sensor_liveness_unsub = None

    async def _async_sensor_liveness_tick(self, _now=None) -> None:
        armed_at = getattr(self, "_sensor_liveness_armed_at", None)
        if armed_at is not None and local_naive_now() < armed_at:
            return
        await self.async_check_sensor_liveness()

    async def async_check_sensor_liveness(self, *, now: datetime | None = None) -> None:
        """Check every sensor group once.

        NOT-TO-DO: do not let anything between reading a group and writing its
        outages back yield to the event loop (the store calls here do not). A
        source change in between would have its emptied record overwritten with
        this check's stale copy, and the outages and their events would return.
        """
        now = now if now is not None else local_naive_now()
        cut_changed = False
        for mapping in await self.store.async_get_mappings():
            try:
                if await self._async_check_mapping_liveness(mapping, now):
                    cut_changed = True
            except Exception:
                # A periodic check: one broken group must not stop the others,
                # every five minutes, for good.
                _LOGGER.exception(
                    "Sensor liveness check failed for sensor group %s",
                    mapping.get(const.MAPPING_ID),
                )
        if cut_changed:
            await self._refresh_estimates_after_outage_change()

    async def _refresh_estimates_after_outage_change(self) -> None:
        """Recompute the live estimates once a pausing group's cut has moved.

        Nothing else would: a silent station writes no rows, so the ingestion
        that normally refreshes them stays quiet until the next poll, commit or
        run. Not the throttled refresh -- a reading in the last minute would
        swallow it, and this check comes round only every five minutes.
        """
        refresh = getattr(self, "async_refresh_zone_estimates", None)
        if refresh is None:
            return
        try:
            await refresh()
        except Exception:  # noqa: BLE001 — an estimate must not break the check
            _LOGGER.debug("Live estimate refresh after an outage failed", exc_info=True)

    async def _async_check_mapping_liveness(self, mapping: dict, now: datetime) -> bool:
        """Check one sensor group; whether an outage of a pausing one opened or closed."""
        mapping_id = mapping[const.MAPPING_ID]
        name = mapping.get(const.MAPPING_NAME) or str(mapping_id)
        outages = outages_of(mapping)
        open_start = {o.entity_id: o.start for o in outages if o.end is None}
        remembered = mapping.get(const.MAPPING_SENSOR_LAST_SEEN) or {}
        evidence: dict[str, Evidence] = {}
        fields_by_entity = sensor_fields_by_entity(
            mapping.get(const.MAPPING_MAPPINGS) or {}
        )
        for entity_id, fields in fields_by_entity.items():
            own, siblings, device_id = self._sensor_liveness_snapshot(entity_id)
            last = last_sign_of_life(
                own, siblings, coerce_stamp(remembered.get(entity_id), STAMP_FROM_STORE)
            )
            if last is None:
                # Never seen and nothing remembered: an open outage keeps its start;
                # otherwise count the limit from this first look, not from never.
                last = open_start.get(entity_id, now)
            recovered = None
            if entity_id in open_start:
                recovered = first_report_after(own, siblings, open_start[entity_id])
            evidence[entity_id] = Evidence(fields, device_id, last, recovered)

        kept, opened, closed = advance_outages(outages, evidence, now)
        self.store.set_mapping_sensor_last_seen(
            mapping_id, {e: ev.last.isoformat() for e, ev in evidence.items()}
        )
        if kept != outages:
            await self.store.async_update_mapping(
                mapping_id,
                {const.MAPPING_SENSOR_OUTAGES: [o.to_store() for o in kept]},
            )
        # Ends first: a late check can end an outage and start the next one of the
        # same sensor, and the last event must say what is true now.
        for outage in closed:
            _LOGGER.info(
                "Sensor group %s: the outage of %s is over (silent from %s to %s)",
                name,
                outage.entity_id,
                outage.start,
                outage.end,
            )
            self._fire_weather_stale(mapping_id, name, outage)
        cuts = self._group_cuts(mapping) if opened else False
        config = mapping.get(const.MAPPING_MAPPINGS) or {}
        for outage in opened:
            _LOGGER.warning(
                (
                    "Sensor group %s: %s (%s) has not reported since %s; its values "
                    "are no longer used, and where the calculation cannot do without "
                    "them no evapotranspiration is booked while it is silent"
                    if cuts and any(cuts_field(f, config) for f in outage.fields)
                    else "Sensor group %s: %s (%s) has not reported since %s; its last "
                    "value is still used"
                ),
                name,
                outage.entity_id,
                ", ".join(outage.fields),
                outage.start,
            )
            self._fire_weather_stale(mapping_id, name, outage)
        if opened or closed:
            self._sync_stale_issue(mapping_id, name, kept)
        return bool(opened or closed) and group_pauses(mapping)

    def _sensor_liveness_snapshot(self, entity_id: str):
        """``(own, siblings, device_id)`` for one sensor-mapped entity."""
        device_id, sibling_ids = _entities_of_device(self.hass, entity_id)
        own = seen_from_state(self.hass.states.get(entity_id))
        siblings = [
            seen
            for sibling_id in sibling_ids
            if (seen := seen_from_state(self.hass.states.get(sibling_id))) is not None
        ]
        return own, siblings, device_id

    def _fire_weather_stale(self, mapping_id, name: str, outage: Outage) -> None:
        self.hass.bus.async_fire(
            f"{const.DOMAIN}_{const.EVENT_WEATHER_STALE}",
            outage_event_payload(mapping_id, name, outage),
        )

    def _sync_stale_issue(self, mapping_id, name: str, outages: list[Outage]) -> None:
        """Raise, update or clear the group's repair issue from its outages."""
        ir = _issue_registry()
        issue_id = f"{const.ISSUE_WEATHER_SENSOR_STALE}_{mapping_id}"
        placeholders = stale_issue_placeholders(name, outages)
        if placeholders is None:
            ir.async_delete_issue(self.hass, const.DOMAIN, issue_id)
            return
        ir.async_create_issue(
            self.hass,
            const.DOMAIN,
            issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=self._stale_issue_key(mapping_id, outages),
            translation_placeholders=placeholders,
        )

    def _group_cuts(self, mapping: dict) -> bool:
        """Whether this group's calculation leaves a silent sensor's time out.

        A pausing group, in every form of the calculation (``zone_blocked_spans``);
        every other group still uses the last value. Which fields it leaves out,
        ``cuts_field`` says.
        """
        return group_pauses(mapping)

    def _stale_issue_key(self, mapping_id, outages: list[Outage]) -> str:
        """The notice's text: the paused one where the group's values are cut.

        That takes a group that cuts and an open outage with a field it cuts; a
        silent rain gauge alone keeps the plain text.
        """
        mapping = self.store.get_mapping(mapping_id) or {}
        config = mapping.get(const.MAPPING_MAPPINGS) or {}
        if self._group_cuts(mapping) and any(
            cuts_field(field, config)
            for outage in outages
            if outage.end is None
            for field in outage.fields
        ):
            return const.ISSUE_WEATHER_SENSOR_STALE_PAUSED
        return const.ISSUE_WEATHER_SENSOR_STALE

    def async_resync_stale_issue(self, mapping: dict | None) -> None:
        """Bring a group's open notice in line with its setting and its fields.

        Called when either changes; otherwise the notice is touched only when an
        outage opens or closes. A group without an open outage has no notice.
        """
        if not mapping:
            return
        outages = outages_of(mapping)
        if not any(o.end is None for o in outages):
            return
        mapping_id = mapping[const.MAPPING_ID]
        self._sync_stale_issue(
            mapping_id, mapping.get(const.MAPPING_NAME) or str(mapping_id), outages
        )

    def _retire_outages(self, mapping: dict | None) -> None:
        """End a group's open outages because its outage record is being emptied.

        A source change (a sensor replaced), deleting the group or resetting the
        weather data empties the record. Every open outage still gets its end
        event, so an automation that reacted to the start hears that the outage
        is no longer tracked, and the group's notice goes; a sensor the group
        still reads that is still silent starts a new outage at the next check.
        Without an open outage there is no notice -- it is raised from the record
        and, being non-persistent, does not outlive a restart -- so the issue
        registry is not asked.
        """
        silent = [o for o in outages_of(mapping or {}) if o.end is None]
        if not silent:
            return
        now = local_naive_now()
        mapping_id = mapping[const.MAPPING_ID]
        name = mapping.get(const.MAPPING_NAME) or str(mapping_id)
        for outage in silent:
            _LOGGER.info(
                "Sensor group %s: the outage of %s ends with a change to the group "
                "(silent since %s)",
                name,
                outage.entity_id,
                outage.start,
            )
            self._fire_weather_stale(mapping_id, name, replace(outage, end=now))
        _issue_registry().async_delete_issue(
            self.hass, const.DOMAIN, f"{const.ISSUE_WEATHER_SENSOR_STALE}_{mapping_id}"
        )
