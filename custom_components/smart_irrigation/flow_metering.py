"""Unified flow-measurement engine + cross-run learning for Smart Irrigation.

A ``FlowMeter`` measures delivered litres for one run of one flow sensor:

* **rate** sensor (unit contains ``/``) — integrate ``rate x dt`` (monotonic-safe on at);
* **per-run counter** (``counter_type='per_run'``) — resets toward 0 at valve-open then
  holds the run's accumulated volume: reseed the baseline **once**, on the first near-zero
  drop (the open reset), then keep-baseline; credits the run's climb from the reset floor;
* **lifetime totalizer** (``counter_type='lifetime'`` — also the safe default for anything
  else, incl. ``'auto'``) — pure keep-baseline: a rise credits ``litres-last``, a drop keeps
  ``last`` and credits nothing. NEVER over-credits (the CFV-3 invariant).

The engine takes an EXPLICIT ``per_run``/``lifetime`` type — it does not auto-detect the
counter kind, because a per-run reset and a lifetime totalizer glitching to near-zero then
partially recovering are indistinguishable within one run (adversarial verification proved
the single-run heuristic over-credits). The kind is learned ACROSS runs by the two pure
functions below (``flow_learn_next_streak`` / ``flow_learn_resolve``), whose state
(``flow_last_end`` / ``flow_reset_streak``) the coordinator persists per zone/distributor.
Pure Python (no Home Assistant imports) so it is unit-tested in isolation.
"""

from __future__ import annotations

import math

# Cross-run learning tunables (see flow_learn_next_streak / flow_learn_resolve).
FLOW_LEARN_RESET_FACTOR = 0.5  # start < FACTOR x prev_end at a run's open == a reset
FLOW_LEARN_MIN_PREV_END = 1.0  # a prior end at/below this is too small to judge a reset
FLOW_LEARN_RESET_STREAK_THRESHOLD = 2  # consecutive open-resets that classify per_run


def flow_rate_to_l_per_min(value: float, unit: str) -> float:
    """Convert an instantaneous flow-rate reading to L/min."""
    u = (unit or "").lower().strip()
    if u in ("l/h", "lph", "liter/h", "liter/hour", "liters/hour", "liters/h"):
        return value / 60.0
    if u in ("m³/h", "m3/h", "m³/hour", "m3/hour"):
        return value * 1000.0 / 60.0
    if u in ("m³/min", "m3/min"):
        return value * 1000.0
    if u in ("gal/min", "gpm", "gallon/min", "gallons/min"):
        return value * 3.785411784
    if u in ("gal/h", "gph", "gal/hour", "gallon/h", "gallons/h"):
        return value * 3.785411784 / 60.0
    return value  # assume L/min


def flow_is_totalizer(unit: str, state_class: str | None) -> bool:
    """True when a flow sensor is a cumulative counter (vs an instantaneous rate)."""
    if state_class == "total_increasing":
        return True
    u = (unit or "").strip()
    if not u or "/" in u:
        return False
    return u.lower() not in ("gpm", "lpm", "gph", "lph")


def flow_litres_from_total(value: float, unit: str) -> float:
    """Convert a cumulative counter reading to litres (m³x1000, galx3.785, else L)."""
    u = (unit or "").lower().strip()
    if u in ("m³", "m3", "cubic meter", "cubic meters"):
        return float(value) * 1000.0
    if u in ("gal", "gallon", "gallons"):
        return float(value) * 3.785411784
    return float(value)  # L / l / liter(s) / unknown -> assume litres


def flow_learn_next_streak(prev_end, start_litres: float, streak: int) -> int:
    """Update the consecutive-open-reset streak from one run's open observation.

    No usable prior (``prev_end`` None or <= FLOW_LEARN_MIN_PREV_END) -> unchanged; a reset
    (``start_litres < FLOW_LEARN_RESET_FACTOR x prev_end``) -> ``streak + 1``; a monotonic
    open (start >= that) -> 0. A per-run counter resets to ~0 each run (start << prev_end);
    a lifetime totalizer is monotonic (start >= prev_end)."""
    if prev_end is None or prev_end <= FLOW_LEARN_MIN_PREV_END:
        return streak
    if start_litres < FLOW_LEARN_RESET_FACTOR * prev_end:
        return streak + 1
    return 0


def flow_learn_resolve(override, streak: int) -> str:
    """Resolve a sensor's counter type: an explicit ``per_run``/``lifetime`` override wins;
    else (``auto``/unknown) ``per_run`` once the streak reaches the threshold, else the
    over-credit-safe ``lifetime``."""
    o = (override or "auto").lower()
    if o in ("per_run", "lifetime"):
        return o
    return "per_run" if streak >= FLOW_LEARN_RESET_STREAK_THRESHOLD else "lifetime"


class FlowMeter:
    """Stateful per-run flow accumulator. See the module docstring."""

    def __init__(
        self,
        counter_type: str = "lifetime",
        *,
        near_zero_frac: float = 0.1,
        near_zero_floor: float = 1.0,
    ) -> None:
        # per_run reseeds once at the open reset; anything else (lifetime/auto/unknown)
        # never reseeds (keep-baseline, over-credit-safe).
        self._per_run = (counter_type or "").lower() == "per_run"
        self._near_zero_frac = float(near_zero_frac)
        self._near_zero_floor = float(near_zero_floor)
        self._is_totalizer: bool | None = None
        self._last_at: float | None = None  # rate: previous sample time
        self._last: float | None = None  # totalizer: previous litres baseline
        self._delivered = 0.0
        self._have_reading = False
        self._reset_done = False  # per_run: the one-time open reset already consumed

    def sample(self, value, unit: str, state_class: str | None, at: float) -> None:
        """Feed one poll reading. ``value`` may be None/non-numeric/NaN (ignored). ``at``
        is monotonic seconds since run start (the first sample defines t0)."""
        if value is None:
            return
        try:
            raw = float(value)
        except (ValueError, TypeError):
            return
        if not math.isfinite(raw):
            return  # NaN/inf: treat like an unavailable tick (ignore, don't poison)
        self._have_reading = True
        if self._is_totalizer is None:
            self._is_totalizer = flow_is_totalizer(unit, state_class)
        if self._is_totalizer:
            self._sample_totalizer(raw, unit)
        else:
            self._sample_rate(raw, unit, at)

    def _sample_rate(self, raw: float, unit: str, at: float) -> None:
        if self._last_at is not None and at > self._last_at:
            self._delivered += (
                flow_rate_to_l_per_min(raw, unit) * (at - self._last_at) / 60.0
            )
        if self._last_at is None or at > self._last_at:
            self._last_at = at

    def _sample_totalizer(self, raw: float, unit: str) -> None:
        litres = flow_litres_from_total(raw, unit)
        if self._last is None:  # seed the baseline
            self._last = litres
            return
        if litres >= self._last:  # rising: credit the true climb
            self._delivered += litres - self._last
            self._last = litres
            return
        # a drop: the one-time per-run open reset, else a glitch (keep baseline). The
        # open reset only ever happens BEFORE the counter accumulates any volume (a
        # per-run counter resets at valve-open, then climbs). Gating on
        # _delivered == 0.0 means a mid-run near-zero glitch (AFTER volume is credited)
        # is a glitch, not a reset — so per_run cannot over-credit a genuine per-run
        # counter even when the meter is seeded at the post-reset value (0). See
        # test_per_run_post_reset_seed_midrun_glitch_no_over_credit.
        if (
            self._per_run
            and not self._reset_done
            and self._delivered == 0.0
            and litres <= self._near_zero()
        ):
            self._last = litres  # reseed to the reset floor (credit nothing)
            self._reset_done = True
        # else glitch (or lifetime): keep _last, add nothing (never over-credit a dip)

    def _near_zero(self) -> float:
        return max(self._near_zero_floor, self._near_zero_frac * (self._last or 0.0))

    def delivered(self) -> float | None:
        """Measured litres this run, or None if no numeric reading was ever seen (the
        caller falls back to time-based). A live-but-dry meter returns 0.0."""
        if not self._have_reading:
            return None
        return self._delivered

    def last_total(self) -> float | None:
        """The last totalizer litres seen (the run's end value, for cross-run learning),
        or None for a rate sensor / no totalizer reading."""
        return self._last if self._is_totalizer else None
