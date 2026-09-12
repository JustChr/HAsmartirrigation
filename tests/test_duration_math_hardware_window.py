"""hardware_window: one duration, two answers — what the hardware is told,
and what that instruction actually means in seconds."""

import pathlib

from custom_components.irrigation_plus import const
from custom_components.irrigation_plus.duration_math import hardware_window


def test_seconds_hardware_is_told_the_rounded_seconds_and_means_them():
    assert hardware_window(263.0, const.DURATION_UNIT_SECONDS) == (263, 263.0)


def test_minutes_hardware_is_told_whole_minutes_and_means_more_seconds():
    # 263 s -> 5 minutes of hardware time, which IS 300 s of watering.
    assert hardware_window(263.0, const.DURATION_UNIT_MINUTES) == (5, 300.0)


def test_minutes_exact_multiple_is_unchanged():
    assert hardware_window(300.0, const.DURATION_UNIT_MINUTES) == (5, 300.0)


def test_minutes_sub_minute_still_rounds_up_to_one():
    # The operating principle: rather slightly too much than too little.
    assert hardware_window(15.0, const.DURATION_UNIT_MINUTES) == (1, 60.0)


def test_zero_and_none_water_nothing():
    assert hardware_window(0.0, const.DURATION_UNIT_MINUTES) == (0, 0.0)
    assert hardware_window(None, const.DURATION_UNIT_MINUTES) == (0, 0.0)
    assert hardware_window(0.0, const.DURATION_UNIT_SECONDS) == (0, 0.0)
    assert hardware_window(None, const.DURATION_UNIT_SECONDS) == (0, 0.0)


def test_unknown_unit_falls_back_to_seconds():
    assert hardware_window(263.0, "fortnights") == (263, 263.0)


def test_hardware_value_is_an_int_the_meaning_is_a_float():
    """The first value lands in a service-call duration field; 5.0 is not 5.
    Seconds is the DEFAULT unit (self_closing.py:120), so pin every branch,
    the non-positive clamp included -- CI has no type checker, this is the
    only thing holding the annotation to its word."""
    for unit in (
        const.DURATION_UNIT_MINUTES,
        const.DURATION_UNIT_SECONDS,
        "fortnights",
    ):
        told, means = hardware_window(263.0, unit)
        assert isinstance(told, int), unit
        assert isinstance(means, float), unit
    told, means = hardware_window(0.0, const.DURATION_UNIT_SECONDS)
    assert isinstance(told, int) and isinstance(means, float)


def test_negative_seconds_command_nothing_in_either_unit():
    """The old seconds path passed a negative straight through. Nothing can
    reach here with one -- all three live sources (self_closing, batch,
    distributor) refuse a non-positive duration before they call -- and a
    negative duration is not something to hand a valve."""
    assert hardware_window(-90.0, const.DURATION_UNIT_SECONDS) == (0, 0.0)
    assert hardware_window(-90.0, const.DURATION_UNIT_MINUTES) == (0, 0.0)


def test_the_rounding_rule_exists_exactly_once():
    """The bug this fixes was one rounding rule living in two files that had to
    be changed together. Fail loudly if a third copy appears -- and just as
    loudly if the canonical one disappears, because "nowhere at all" also
    satisfies "nowhere outside duration_math", and a pin that counts copies
    would call that success.

    rglob, not glob: a copy under calcmodules/ or weathermodules/ is a copy.

    A tripwire, not a proof: the rule is matched as a literal, so a copy spelled
    ``math.ceil(secs / 60)`` walks straight past it. It catches the copy-paste
    that actually caused this bug, not every possible re-derivation.
    """
    rule = "math.ceil(seconds / 60"
    src = pathlib.Path(__file__).parent.parent / "custom_components" / "irrigation_plus"
    canonical = src / "duration_math.py"
    # Our Python never lives under the panel build, and everything below it is
    # third-party (node_modules) -- state the boundary positively rather than
    # deny-listing directory names as they appear.
    frontend = src / "frontend"
    offenders = [
        str(p.relative_to(src))
        for p in src.rglob("*.py")
        if p != canonical and not p.is_relative_to(frontend)
        # errors="ignore": an undecodable byte cannot be part of an ASCII rule,
        # and this pin must report copies, never raise on a stray file.
        and rule in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert offenders == [], f"unit conversion copied back into: {offenders}"
    assert rule in canonical.read_text(encoding="utf-8"), (
        f"the rounding rule is gone from {canonical.name}: this pin asserts the "
        "absence of copies, so it must assert the presence of the original too"
    )
