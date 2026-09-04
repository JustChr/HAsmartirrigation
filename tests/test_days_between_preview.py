"""Tests for the days-between skip preview projection (#32 follow-up).

``SkipConditionsMixin._project_days_between_to_next_run`` advances the live
"as of now" days-between check to the next scheduled irrigate run's date, so the
dashboard outlook isn't pessimistically showing a skip right after a run (when
the day counter is still 0 but will have incremented by the next run). The
run-time gate in ``_eval_days_between`` is untouched — only this preview shifts.
"""

import datetime

import homeassistant.util.dt as dt_util
from freezegun import freeze_time

from custom_components.irrigation_plus.skip_conditions import (
    SKIP_DAYS_BETWEEN,
    SkipConditionsMixin,
)

project = SkipConditionsMixin._project_days_between_to_next_run


def _preview(days_since, days_between, enabled=True):
    return {
        "checks": [
            {
                "id": SKIP_DAYS_BETWEEN,
                "enabled": enabled,
                "would_skip": enabled and days_since < days_between,
                "available": True,
                "observed": days_since,
                "threshold": days_between,
            }
        ]
    }


def _check(preview):
    return next(c for c in preview["checks"] if c["id"] == SKIP_DAYS_BETWEEN)


def _run(days_ahead, action="irrigate"):
    """An upcoming-run entry whose next_run_utc is N local days from now."""
    when = dt_util.now() + datetime.timedelta(days=days_ahead)
    return {"action": action, "next_run_utc": when.isoformat()}


@freeze_time("2026-06-21 23:30:00")
def test_projects_forward_clears_false_skip():
    """Just watered (0 days) + run tomorrow → counter will be 1, no skip."""
    preview = _preview(days_since=0, days_between=1)
    project(preview, [_run(1)])
    check = _check(preview)
    assert check["observed"] == 1
    assert check["would_skip"] is False


@freeze_time("2026-06-21 23:30:00")
def test_still_skips_when_run_too_soon():
    """3-day rule, run tomorrow after watering today → 1 < 3, still skips."""
    preview = _preview(days_since=0, days_between=3)
    project(preview, [_run(1)])
    check = _check(preview)
    assert check["observed"] == 1
    assert check["would_skip"] is True


@freeze_time("2026-06-21 23:30:00")
def test_same_day_run_no_projection():
    """A run later today (offset 0) leaves the live evaluation untouched."""
    preview = _preview(days_since=0, days_between=1)
    project(preview, [_run(0)])
    check = _check(preview)
    assert check["observed"] == 0
    assert check["would_skip"] is True


@freeze_time("2026-06-21 23:30:00")
def test_disabled_guard_untouched():
    preview = _preview(days_since=0, days_between=0, enabled=False)
    project(preview, [_run(1)])
    check = _check(preview)
    assert check["observed"] == 0


@freeze_time("2026-06-21 23:30:00")
def test_no_irrigate_run_untouched():
    """Only non-irrigate runs scheduled → nothing to project to."""
    preview = _preview(days_since=0, days_between=1)
    project(preview, [_run(2, action="calculate")])
    check = _check(preview)
    assert check["observed"] == 0
    assert check["would_skip"] is True


@freeze_time("2026-06-21 23:30:00")
def test_picks_soonest_irrigate_run():
    """First irrigate entry (list is soonest-first) drives the offset."""
    preview = _preview(days_since=0, days_between=2)
    project(preview, [_run(1), _run(5)])
    check = _check(preview)
    assert check["observed"] == 1
    assert check["would_skip"] is True
