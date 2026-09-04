"""Event-driven ingestion of sensor-sourced weather values (opt-in).

By default weather sensors are sampled by POLL: the auto-update timer fires
(hourly, by default) and ``build_sensor_values_for_mapping`` reads
``hass.states`` once. Everything that happened between ticks is never recorded,
so the daily min/max temperature come from ~24 spot samples rather than from the
day's real extremes, and every time-weighted mean is resolved only to the poll
interval. Both feed the daily FAO-56 inputs directly, so that is an ET
*accuracy* loss, not a cosmetic one.

When "continuous updates" is enabled (Setup → Experimental) this mixin instead
subscribes to the mapped sensor entities and appends a reading the moment the
entity changes. Rows are **sparse** — one key plus ``RETRIEVED_AT`` — which
``weather_aggregate`` handles natively (``_group_by_sensor`` builds per-key
parallel lists), and fields that saw no event inside a zone's window are backed
up by ``MAPPING_DATA_LAST_ENTRY`` (``aggregate_window(..., last_entry=...)``).

Three things keep event-driven ingestion from becoming a write amplifier:

1. **A deadband** (``SENSOR_DEADBAND``) drops changes too small to matter, which
   is the single biggest reduction for a jittery sensor.
2. **A per-sensor-group debounce** coalesces the follow-up work (zone
   ``last_updated`` / data-point counts, the frontend dispatch, pruning) into one
   pass per burst. The reading itself is appended immediately and never
   debounced — deferring it would let a calculation advance a zone's watermark
   past readings still sitting in a timer, silently dropping them from the
   window.
3. **The append never touches the disk.** Readings live in ``store.buffers``,
   outside the routine save payload, so ``append_mapping_reading`` schedules no
   write at all — they ride out on the flush timer, on a write somebody else
   triggers, or at shutdown. ``store.SAVE_DELAY`` then coalesces whatever writes
   do happen (the debounced bookkeeping below).
4. **A short row-coalescing window** collapses a station that reports its
   sensors one at a time (~10 ms apart) into one buffer row instead of a run
   of single-field ones: a field lands in the newest row, in place, when that
   row is fresh enough and does not already carry it — see
   ``store.merge_or_append_mapping_reading``. This is still a synchronous part
   of the append itself, not a timer, so it does not reopen the hazard in
   point 2 above. It only ever merges into a row no enabled zone has consumed
   yet (``store.get_min_enabled_watermark``); the row that is already a
   zone's boundary always gets a fresh append instead.

Deliberately unlike altmenorg (where this feature came from), the debounced
follow-up does **not** trigger zone calculations. justchr consumes the buffer
through per-zone ``last_consumed_at`` watermarks, and calculating on every
sensor burst would shred the daily window into seconds-long slices whose ET
(min/max temperature driven, non-linear) is not the sum of the day's. Intraday
demand is served by ``LiveEstimateMixin`` instead.

Methods live on a mixin the SmartIrrigationCoordinator inherits, so they use
``self`` to reach coordinator state (store, hass, buffer pruning).
"""

import logging
from datetime import datetime, timedelta
from functools import partial

from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util.unit_system import METRIC_SYSTEM

from . import const
from .helpers import (
    convert_mapping_to_metric,
    resolve_sensor_unit,
    solar_reading_is_rate,
    to_absolute_pressure,
)
from .weather_aggregate import effective_aggregate

_LOGGER = logging.getLogger(__name__)

# Minimum movement, in each field's INTERNAL METRIC unit, before a state change
# earns a buffer row. Compared against the last value actually APPENDED (not the
# last seen), so error stays bounded by the threshold instead of drifting.
#
# Chosen an order of magnitude below what changes an ET result: a 0.2 °C or 1 %RH
# step is far finer than the daily aggregation needs, while a sensor jittering in
# its last digit stops producing rows entirely.
#
# ⚠️ Precipitation is deliberately ABSENT (and so falls to the 0.0 default =
# never filtered). A rain gauge is aggregated by DELTA and rain rate by
# RIEMANNSUM; suppressing the small steps that make up a slow drizzle would
# under-report rainfall, and under-reported rain means OVER-watering.
SENSOR_DEADBAND_DEFAULT = 0.0
SENSOR_DEADBAND = {
    const.MAPPING_TEMPERATURE: 0.2,  # °C
    const.MAPPING_DEWPOINT: 0.2,  # °C
    const.MAPPING_HUMIDITY: 1.0,  # %
    const.MAPPING_PRESSURE: 0.5,  # hPa
    const.MAPPING_WINDSPEED: 0.3,  # m/s
    # Solar radiation is stored as MJ/day/m2, NOT W/m2: full sun ~1000 W/m2 is
    # ~86 MJ/day/m2, so 0.5 here is roughly a 6 W/m2 step.
    const.MAPPING_SOLRAD: 0.5,
}

# How close together two readings must land to collapse into one buffer row
# (see the module docstring, point 4). Deliberately an order of magnitude above
# the ~10 ms gap a station reporting its sensors one at a time actually produces,
# to comfortably absorb that jitter, while staying short enough that a merged
# field's RETRIEVED_AT (the FIRST reading's stamp — merging never rewrites it)
# is never more than this far from when it actually arrived.
CONTINUOUS_COALESCE_WINDOW = timedelta(milliseconds=100)

# Prune the sensor group's buffer every Nth debounced flush rather than every
# append: _prune_mapping_buffer walks every zone on the group and writes, so it
# is far too heavy to run per reading, and the buffer only needs bounding, not
# trimming to the row.
CONTINUOUS_PRUNE_EVERY = 20

# Absolute backstop on buffer length, applied ONLY AFTER the watermark-based
# prune has already run — never instead of it. _prune_mapping_buffer keeps
# everything a slow-consuming zone has not aggregated yet; a plain "keep the last
# K rows" cap would throw those readings away and surface as silent
# UNDER-watering. Reaching this cap therefore means the watermark rule could not
# free anything, i.e. a zone has stopped calculating — so the trim is logged as a
# warning, not a debug line. Generous: 7 days of readings at one per 30 s is
# ~20k rows, so this only bites on pathological churn.
CONTINUOUS_MAX_BUFFER_ROWS = 20000


class ContinuousUpdateMixin:
    """Append sensor readings on state change instead of on the poll timer."""

    async def async_setup_continuous_updates(self) -> None:
        """(Re)subscribe to the mapped weather sensors per the current config.

        Idempotent: rebuilds the subscription only when the tracked entity set
        actually changes, so it is cheap to call on startup and on every config
        update. When the feature is off (or no sensor group maps a sensor) it
        tears any existing subscription down.
        """
        # Strict identity check: only an explicit True opts in. This also keeps
        # the method a safe no-op when the store config is a test double.
        enabled = self.store.config.continuousupdates is True
        # entity_id -> [(mapping_id, mapping key, that key's config), ...]. One
        # entity can feed several fields and several sensor groups, so every
        # target of a change must be visited, not just the first match.
        targets: dict[str, list[tuple[int, str, dict]]] = {}
        if enabled:
            # get_mapping_field_configs(), NOT async_get_mappings(): the latter
            # attr.asdict()s every sensor group, and this method re-runs on every
            # _config_updated signal — which the ingestion flush itself emits, so
            # it is effectively on the ingestion path and must not copy anything
            # it does not need.
            for mapping_id, field_configs in self.store.get_mapping_field_configs():
                for key, the_map in field_configs.items():
                    # Legacy stored shape: a bare string instead of a config dict.
                    if isinstance(the_map, str):
                        continue
                    if (
                        the_map.get(const.MAPPING_CONF_SOURCE)
                        != const.MAPPING_CONF_SOURCE_SENSOR
                    ):
                        continue
                    sensor_id = the_map.get(const.MAPPING_CONF_SENSOR)
                    if not sensor_id:
                        continue
                    targets.setdefault(sensor_id, []).append(
                        (int(mapping_id), key, the_map)
                    )

        entities = frozenset(targets)
        # Refresh the target map even when the entity set is unchanged: the
        # per-field config inside it (notably the configured unit) can be edited
        # without adding or removing an entity, and a stale unit here would
        # convert every subsequent reading wrongly.
        self._continuous_targets = targets
        if entities == self._continuous_entities:
            return

        self.async_teardown_continuous_updates()
        self._continuous_targets = targets

        if not entities:
            _LOGGER.debug("Continuous updates: disabled or no sensor-mapped fields")
            return

        self._continuous_unsub = async_track_state_change_event(
            self.hass, list(entities), self._sensor_state_changed
        )
        # Recorded only once the subscription exists. The early return above
        # diffs against this set, so recording it first and then failing to
        # subscribe would leave ingestion off with nothing to retry it.
        self._continuous_entities = entities
        _LOGGER.info(
            "Continuous updates: tracking %d weather sensor(s), debounce %d ms",
            len(entities),
            self._continuous_debounce_ms(),
        )
        self._continuous_seed_baseline(entities)

    def _continuous_metric_value(
        self,
        raw_value,
        key: str,
        the_map: dict,
        ha_unit,
        entity_id: str,
        system_is_metric: bool,
    ):
        """Turn a raw sensor state into the value that goes in the buffer.

        Both event-driven writers (the baseline seed and the state-change
        handler) go through here so they cannot drift apart: the buffer is shared
        with the interval poll, and a field written by one path in a different
        quantity than the other makes the aggregate a mix of the two. Pressure is
        exactly that case — it is corrected to absolute here, matching
        ``_apply_pressure_type`` on the poll side. Solar radiation is the other:
        a reading that is an instantaneous rate is ceilinged at clear sky here,
        matching ``build_sensor_values_for_mapping`` on the poll side. Both
        clamps sit right after the conversion because that is where the
        reading's resolved unit is in hand.
        """
        unit = resolve_sensor_unit(
            key, the_map.get(const.MAPPING_CONF_UNIT), ha_unit, entity_id
        )
        value = convert_mapping_to_metric(raw_value, key, unit, system_is_metric)
        value = to_absolute_pressure(value, key, the_map, self.hass.config.elevation)
        if key == const.MAPPING_SOLRAD and solar_reading_is_rate(unit):
            value = self._clamp_solar_reading(value)
        return value

    @callback
    def _continuous_seed_baseline(self, entities) -> None:
        """Record each tracked sensor's CURRENT value right after subscribing.

        Subscribing only sees *future* changes, so a field whose value is genuinely
        flat is never recorded at all: overnight solar radiation sits at 0, a calm
        night's wind at 0, a cumulative rain gauge unchanged for days. After a
        restart those fields would be missing from the buffer entirely, and the
        aggregation would fall back to ``MAPPING_DATA_LAST_ENTRY`` — or, on a first
        run, to nothing, leaving the calc module short an input.

        The interval poll used to paper over this by writing every field on every
        tick. With continuous updates on, a pure-sensor group has no poll (and an
        install can disable auto-update entirely), so the baseline has to come from
        here.

        Deliberately reuses the normal append path, so the deadband reference is
        seeded too and the very next real change is measured against a true value
        rather than against nothing. Only runs when a subscription is actually
        (re)created — the entity-set diff above makes that rare, so this cannot
        append duplicate rows on every ``_config_updated``.
        """
        timestamp = datetime.now()
        coalesce_before = timestamp - CONTINUOUS_COALESCE_WINDOW
        system_is_metric = self.hass.config.units is METRIC_SYSTEM
        seeded = 0
        # Every field seeded here shares the exact same timestamp (captured once,
        # above), so within one mapping they are always eligible to coalesce —
        # this is the same merge the live path uses, applied to what would
        # otherwise be N single-field rows all stamped identically.
        watermark_cache: dict[int, object] = {}
        for entity_id in entities:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
                continue
            try:
                raw_value = float(state.state)
            except (TypeError, ValueError):
                continue
            ha_unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
            for mapping_id, key, the_map in self._continuous_targets.get(entity_id, []):
                value = self._continuous_metric_value(
                    raw_value, key, the_map, ha_unit, entity_id, system_is_metric
                )
                if value is None:
                    continue
                if mapping_id not in watermark_cache:
                    watermark_cache[mapping_id] = self.store.get_min_enabled_watermark(
                        mapping_id
                    )
                if self.store.merge_or_append_mapping_reading(
                    mapping_id,
                    {key: value, const.RETRIEVED_AT: timestamp},
                    coalesce_before=coalesce_before,
                    min_watermark=watermark_cache[mapping_id],
                ):
                    # Carry-forward too, exactly like the live path — both are
                    # save-free, so the seed costs no write either.
                    self.store.set_mapping_last_entry_value(mapping_id, key, value)
                    self._continuous_last_value[(mapping_id, key)] = value
                    seeded += 1
        if seeded:
            _LOGGER.info(
                "Continuous updates: seeded %d baseline reading(s) from current state",
                seeded,
            )

    def async_teardown_continuous_updates(self) -> None:
        """Cancel the sensor subscription and any pending debounce timers.

        Called on unload and before every resubscribe. The debounce timers MUST
        go too: an ``async_call_later`` that survives a reload fires against the
        old coordinator and ghost-writes to the store.
        """
        if getattr(self, "_continuous_unsub", None) is not None:
            self._continuous_unsub()
            self._continuous_unsub = None
        for unsub in getattr(self, "_continuous_debounce_unsub", {}).values():
            unsub()
        self._continuous_debounce_unsub = {}
        self._continuous_entities = frozenset()
        self._continuous_targets = {}
        # Drop the deadband references: after a re-subscribe the first reading of
        # each field must always be recorded, however little it moved while we
        # were not listening.
        self._continuous_last_value = {}
        self._continuous_flush_count = {}

    def clear_continuous_deadband_state(self) -> None:
        """Forget every field's last-appended value, keeping the subscription.

        "Reset all weather data" empties the buffer and the carry-forwards, but
        the deadband compares against the last APPENDED value, which lives here
        and survives that wipe. On a pure-sensor group the poll is skipped, so
        the event handler is the only writer — and it drops every reading within
        the deadband of the pre-reset reference WITHOUT advancing it. The buffer
        then stays empty until a reading happens to move further than the
        threshold: minutes for temperature, but hours for pressure or humidity
        and a whole night for solar radiation, during which the zone cannot
        aggregate and looks like the reset broke it.

        Deliberately narrower than ``async_teardown_continuous_updates``: the
        entity set has not changed, so the subscription and its debounce timers
        stay exactly as they are.
        """
        self._continuous_last_value = {}
        self._continuous_flush_count = {}

    def _continuous_debounce_ms(self) -> int:
        """Configured debounce in milliseconds (0 = flush on every change)."""
        raw = getattr(self.store.config, const.CONF_SENSOR_DEBOUNCE, None)
        try:
            return max(int(raw), 0)
        except (TypeError, ValueError):
            # A test double or an old string-typed stored value; the default is
            # always safe (it only delays follow-up work, never a reading).
            return const.CONF_DEFAULT_SENSOR_DEBOUNCE

    @callback
    def _sensor_state_changed(self, event: Event) -> None:
        """Record a mapped sensor's new value in its sensor group's buffer."""
        entity_id = event.data.get("entity_id")
        targets = self._continuous_targets.get(entity_id)
        if not targets:
            return
        new_state = event.data.get("new_state")
        if new_state is None:
            return
        if new_state.state in (None, STATE_UNKNOWN, STATE_UNAVAILABLE):
            _LOGGER.debug(
                "Continuous updates: %s is %s — ignoring",
                entity_id,
                new_state.state,
            )
            return
        try:
            raw_value = float(new_state.state)
        except (TypeError, ValueError):
            _LOGGER.debug(
                "Continuous updates: %s state %r is not numeric — ignoring",
                entity_id,
                new_state.state,
            )
            return

        # Naive local, exactly like the interval path's RETRIEVED_AT — the two
        # write into the SAME buffer and aggregate_window compares the stamps
        # against a naive-local watermark, so a tz-aware value here would raise.
        timestamp = datetime.now()
        ha_unit = new_state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        system_is_metric = self.hass.config.units is METRIC_SYSTEM

        touched: set[int] = set()
        for mapping_id, key, the_map in targets:
            value = self._continuous_metric_value(
                raw_value, key, the_map, ha_unit, entity_id, system_is_metric
            )
            if value is None:
                continue
            if self._continuous_in_deadband(mapping_id, key, value):
                continue
            previous = self._continuous_last_value.get((mapping_id, key))
            if (
                previous is not None
                and value < previous
                and value != 0
                and effective_aggregate(key, {key: the_map})
                == const.MAPPING_CONF_AGGREGATE_DELTA
            ):
                # The delta aggregate treats an exact zero as a legitimate
                # counter rollover; any other decrease re-bases at the lower
                # value, so the climb back to the old level will be counted as
                # NEW accumulation. One glitch costs one dip's worth of phantom
                # rain; an oscillating value (a failing gauge, two writers on
                # one entity) accumulates it without bound and nothing else in
                # the pipeline can tell. Warned here, once per stored reading,
                # rather than in the aggregation — the pure engine runs every
                # minute per zone via the live estimate, which would turn one
                # bad reading into thousands of log lines.
                _LOGGER.warning(
                    "Continuous updates: cumulative %s on sensor group %s "
                    "decreased (%s -> %s) without resetting to zero; the rise "
                    "back will be counted as new accumulation - check the "
                    "sensor for glitches or a second writer",
                    key,
                    mapping_id,
                    previous,
                    value,
                )
            self._continuous_last_value[(mapping_id, key)] = value
            # Synchronous, O(1), and no task hop: store.merge_or_append_mapping_
            # reading writes straight into the live buffer in store.buffers and
            # schedules NO write. The previous shape — read a get_mapping() copy
            # in a task, mutate, write it back — was both a lost-update race (two
            # events for one group could each read the pre-append snapshot) and
            # O(buffer) per reading, because get_mapping() attr.asdict()s what it
            # returns. Merging (module docstring, point 4) collapses a station
            # reporting its sensors one at a time into a single row, gated on the
            # newest row not already being a zone's consumed boundary.
            if not self.store.merge_or_append_mapping_reading(
                mapping_id,
                {key: value, const.RETRIEVED_AT: timestamp},
                coalesce_before=timestamp - CONTINUOUS_COALESCE_WINDOW,
                min_watermark=self.store.get_min_enabled_watermark(mapping_id),
            ):
                continue
            # Carry-forward for aggregate_window(last_entry=...): a zone window
            # containing no row for this field falls back to this value rather
            # than feeding the calc module nothing at all. Save-free for the same
            # reason the append is — see store.set_mapping_last_entry_value.
            self.store.set_mapping_last_entry_value(mapping_id, key, value)
            _LOGGER.debug(
                "Continuous updates: sensor group %s %s = %s at %s",
                mapping_id,
                key,
                value,
                timestamp,
            )
            touched.add(mapping_id)

        for mapping_id in touched:
            self._schedule_continuous_flush(mapping_id)

    def _continuous_in_deadband(self, mapping_id: int, key: str, value: float) -> bool:
        """True when ``value`` has not moved enough to be worth storing.

        Deadband (storage-write-amplification plan, Step 3): a sensor jittering
        in its last digit would otherwise append a row — and eventually a full
        store rewrite — per report. Compared against the last APPENDED value so
        a slow monotonic drift still gets recorded once it exceeds the threshold.
        """
        previous = self._continuous_last_value.get((mapping_id, key))
        if previous is None:
            return False
        threshold = SENSOR_DEADBAND.get(key, SENSOR_DEADBAND_DEFAULT)
        if threshold <= 0:
            return False
        return abs(value - previous) < threshold

    @callback
    def _schedule_continuous_flush(self, mapping_id: int) -> None:
        """(Re)arm this sensor group's debounce so a burst yields one flush.

        Cancel-and-reschedule, keyed by sensor group: while a chatty sensor keeps
        changing, the follow-up work is postponed rather than repeated. Only the
        bookkeeping waits — the readings themselves are already in the buffer.
        """
        unsub = self._continuous_debounce_unsub.pop(mapping_id, None)
        if unsub is not None:
            unsub()
        debounce_ms = self._continuous_debounce_ms()
        if debounce_ms <= 0:
            self.hass.async_create_task(
                self._async_continuous_update_for_mapping(mapping_id)
            )
            return
        self._continuous_debounce_unsub[mapping_id] = async_call_later(
            self.hass,
            timedelta(milliseconds=debounce_ms),
            partial(self._continuous_debounce_fired, mapping_id),
        )

    @callback
    def _continuous_debounce_fired(self, mapping_id: int, _now) -> None:
        """Debounce expiry: forget the cancel handle, then run the flush once."""
        self._continuous_debounce_unsub.pop(mapping_id, None)
        self.hass.async_create_task(
            self._async_continuous_update_for_mapping(mapping_id)
        )

    async def _async_continuous_update_for_mapping(self, mapping_id: int) -> None:
        """One post-burst pass over a sensor group: zone bookkeeping + pruning.

        Deliberately does NOT calculate any zone (see the module docstring): it
        publishes what the panel and the zone entities show (last updated, number
        of data points) and keeps the buffer bounded.
        """
        # Row count via the cheap accessor, not get_mapping(): see
        # store.get_mapping_field_configs for why the buffer must not be copied on
        # a per-burst path. Doubles as the existence check.
        row_count = self.store.get_mapping_row_count(mapping_id)
        if row_count is None:
            return
        now = datetime.now()
        await self.store.async_update_mapping(
            mapping_id, {const.MAPPING_DATA_LAST_UPDATED: now}
        )

        # Match the interval path's count: it stores len(data) - 1 because the
        # oldest row is the carried-forward boundary, not a new reading. Re-read
        # after the await above — an append can land in between, and a count taken
        # from a pre-await snapshot would under-report the buffer.
        row_count = self.store.get_mapping_row_count(mapping_id) or 0
        changes_to_zone = {
            const.ZONE_LAST_UPDATED: now,
            const.ZONE_NUMBER_OF_DATA_POINTS: max(row_count - 1, 0),
        }
        for zone_id in await self._get_zones_that_use_this_mapping(mapping_id):
            await self.store.async_update_zone(zone_id, changes_to_zone)
            async_dispatcher_send(self.hass, const.DOMAIN + "_config_updated", zone_id)

        count = self._continuous_flush_count.get(mapping_id, 0) + 1
        self._continuous_flush_count[mapping_id] = count
        if count % CONTINUOUS_PRUNE_EVERY == 0:
            # Watermark-safe pruning (never drops a reading an enabled zone has
            # not consumed); the row cap below only ever runs on what survives it.
            await self._prune_mapping_buffer(mapping_id, now=now)
            await self._continuous_enforce_row_cap(mapping_id)

        # Last, so the estimate is published against the buffer's final state for
        # this burst and nothing above depends on it. Event ingestion is the only
        # thing feeding a sensor-only install, so without this the intraday
        # estimate would move only on the poll timer (hourly by default) or at
        # calculation time. Throttled because this runs once per burst; the
        # per-zone completed-hour carry is what keeps each refresh to the current
        # partial hour rather than the whole window.
        await self.async_refresh_zone_estimates_throttled()

    async def _continuous_enforce_row_cap(self, mapping_id: int) -> None:
        """Backstop trim once the watermark prune has left too many rows.

        Runs strictly AFTER ``_prune_mapping_buffer``, so anything still here is
        data an enabled zone has not aggregated yet. Dropping it costs ET that no
        zone will ever see — silent under-watering — so this is a last-resort
        memory bound and it says so in the log. The oldest surviving row is kept
        as the DELTA / RIEMANNSUM baseline that ``select_window`` expects.
        """
        # get_mapping_row_count doubles as the existence check (None = unknown
        # group) and never materializes the buffer, so this runs on every prune
        # cycle for the cost of a len().
        row_count = self.store.get_mapping_row_count(mapping_id)
        if row_count is None or row_count <= CONTINUOUS_MAX_BUFFER_ROWS:
            return
        data = self.store.get_mapping_buffer(mapping_id)
        keep = data[-CONTINUOUS_MAX_BUFFER_ROWS:]
        keep.insert(0, data[0])
        _LOGGER.warning(
            "Continuous updates: sensor group %s buffer hit the %d-row cap after "
            "pruning (%d rows) — dropping the oldest UNCONSUMED readings. A zone "
            "using this sensor group has probably stopped calculating; check its "
            "state and the auto-calculate schedule",
            mapping_id,
            CONTINUOUS_MAX_BUFFER_ROWS,
            len(data),
        )
        self.store.set_mapping_buffer(mapping_id, keep)
        # Rows an enabled zone had not consumed are gone, so any completed-hour
        # ETo the intraday estimate carried for those zones was computed from
        # readings that no longer exist.
        self.invalidate_live_estimate_carry(mapping_id)
