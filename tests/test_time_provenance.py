"""The two time provenances, named.

A naive timestamp on these paths means one of two different things, and nothing in
the code said which:

- a **stored** stamp was written by a bare ``datetime.now()``, so naive means the
  zone the PROCESS was in;
- a **client** row is a site-local clock time that came out of a weather API, so
  naive means HA's configured zone, and always did.

The two agree on HA OS and Supervised, which is why the seam went unnoticed. On
Docker or Core without ``TZ=`` they differ by the whole UTC offset.

These tests pin the vocabulary only. Coercion here normalises TO the naive form each
path already uses -- it does not make anything aware. Turning a stamp aware would
raise ``can't compare offset-naive and offset-aware`` inside a blanket ``except``,
i.e. silently disable the live estimate, which is the opposite of a fix.
"""

import datetime
import zoneinfo

import pytest
from homeassistant.util import dt as dt_util

from custom_components.irrigation_plus import helpers
from custom_components.irrigation_plus.helpers import (
    STAMP_FROM_CLIENT,
    STAMP_FROM_STORE,
    coerce_stamp,
)

UTC = datetime.timezone.utc
BERLIN = zoneinfo.ZoneInfo("Europe/Berlin")


@pytest.fixture
def split_zones(monkeypatch):
    """The container at UTC, the user at Europe/Berlin -- the case that separates them.

    HA's own setter is used for the zone, and it is restored to UTC rather than to
    whatever was found: the test plugin's cleanup check asserts UTC at teardown, and
    monkeypatch would faithfully put back a leaked value from an earlier test.
    """
    monkeypatch.setattr(helpers, "_process_timezone", lambda: UTC)
    dt_util.set_default_time_zone(BERLIN)
    yield
    dt_util.set_default_time_zone(UTC)


def test_the_same_instant_coerces_differently_per_provenance(split_zones):
    """One aware instant, two provenances, two naive results the UTC offset apart.

    This is the whole point of naming them: 10:00 UTC is 10:00 on the process clock
    and 12:00 on the user's, and a reader with one rule cannot be right about both.
    """
    instant = datetime.datetime(2026, 9, 21, 10, 0, tzinfo=UTC)

    stored = coerce_stamp(instant, STAMP_FROM_STORE)
    client = coerce_stamp(instant, STAMP_FROM_CLIENT)

    assert stored == datetime.datetime(2026, 9, 21, 10, 0)
    assert client == datetime.datetime(2026, 9, 21, 12, 0)
    assert client - stored == datetime.timedelta(hours=2)
    assert stored.tzinfo is None and client.tzinfo is None


def test_a_naive_value_is_returned_unchanged_under_either_provenance(split_zones):
    """What makes this change behaviour-preserving, so it is a test and not a claim.

    Every stamp on these paths is naive today, so if naive values passed through
    untouched then no number can move -- and that is exactly what must hold.
    """
    naive = datetime.datetime(2026, 9, 21, 12, 0)

    assert coerce_stamp(naive, STAMP_FROM_STORE) == naive
    assert coerce_stamp(naive, STAMP_FROM_CLIENT) == naive
    assert coerce_stamp("2026-09-21T12:00:00", STAMP_FROM_STORE) == naive
    assert coerce_stamp("2026-09-21T12:00:00", STAMP_FROM_CLIENT) == naive


def test_coercing_without_naming_a_provenance_is_an_error():
    """No default provenance, so a caller cannot stay silent about which kind it holds.

    That is the requirement this function exists to satisfy: a future reader must not
    be able to coerce a forecast row as if it were a buffer stamp.
    """
    with pytest.raises(TypeError):
        coerce_stamp(datetime.datetime(2026, 9, 21, 12, 0))


def test_an_unusable_value_is_no_stamp_rather_than_a_raise(split_zones):
    """None and junk give None.

    ``parse_datetime`` lets ``fromisoformat``'s ValueError out, and these call sites
    sit inside a blanket ``except`` that turns a raise into the live estimate quietly
    going unavailable with a plausible "last calculated" still on display. A value
    this cannot read is no stamp, and the caller keeps whatever fallback it has.
    """
    assert coerce_stamp(None, STAMP_FROM_STORE) is None
    assert coerce_stamp("not a date", STAMP_FROM_STORE) is None
    assert coerce_stamp("not a date", STAMP_FROM_CLIENT) is None
    assert coerce_stamp(object(), STAMP_FROM_STORE) is None


def test_the_two_provenances_are_distinct_values():
    """They are compared by identity in the coercion, so they must not collapse."""
    assert STAMP_FROM_STORE != STAMP_FROM_CLIENT


def test_an_unknown_provenance_is_refused(split_zones):
    """A typo'd provenance must not silently pick one of the two rules."""
    with pytest.raises(ValueError):
        coerce_stamp(datetime.datetime(2026, 9, 21, 10, 0, tzinfo=UTC), "site-local")
