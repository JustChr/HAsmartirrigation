"""Which zone the live estimate reads each kind of naive timestamp in.

Two kinds reach it and they need opposite answers:

- **stored** stamps (`last_calculated`, `last_updated`) were written by a bare
  ``datetime.now()``, so naive means the PROCESS's zone;
- **client** rows (the hourly forecast series) are site-local clock times off a
  weather API, so naive means HA's configured zone, and always did.

These tests are characterisation, not aspiration. They pin what the code does
**today**, including the half that is wrong, so that the change which inverts it is
visible as a decision rather than as drift. The wrong half is marked as such.
"""

import datetime
import zoneinfo

import pytest
from homeassistant.util import dt as dt_util

from custom_components.irrigation_plus import helpers, live_estimate

UTC = datetime.timezone.utc
BERLIN = zoneinfo.ZoneInfo("Europe/Berlin")


@pytest.fixture
def split_zones(monkeypatch):
    """Container at UTC, user at Europe/Berlin -- the case that separates the two.

    HA's own setter is used and the zone is restored to UTC rather than to whatever
    was found: the test plugin's cleanup asserts UTC at teardown.
    """
    monkeypatch.setattr(helpers, "_process_timezone", lambda: UTC)
    dt_util.set_default_time_zone(BERLIN)
    yield
    dt_util.set_default_time_zone(UTC)


def test_a_client_forecast_row_is_read_in_ha_local(split_zones):
    """An aware forecast row lands on HA's clock, which is correct and stays.

    A weather API answers in the site's own local time. 10:00 UTC is 12:00 for a user
    in Berlin, and 12:00 is the hour their zone is being priced for.
    """
    aware = datetime.datetime(2026, 9, 21, 10, 0, tzinfo=UTC)

    got = helpers.coerce_stamp(aware, helpers.STAMP_FROM_CLIENT)

    assert got == datetime.datetime(2026, 9, 21, 12, 0)


def test_a_stored_stamp_is_still_read_in_ha_local_today(split_zones):
    """⚠️ THE DEFECT, pinned deliberately.

    ``_parse_stored_as_ha_local`` applies the CLIENT rule to a STORED stamp: an aware
    value is converted with ``dt_util.as_local``, and a naive one is taken as HA-local
    by every consumer downstream. A stored stamp is process-local, so on a container
    without ``TZ=`` this reads it as the whole UTC offset away from the instant it
    marks.

    This test exists so that the change which inverts it cannot happen quietly. It is
    NOT asserting the right answer -- it is asserting the current one, and it is meant
    to be replaced, not preserved.
    """
    aware = datetime.datetime(2026, 9, 21, 10, 0, tzinfo=UTC)

    got = live_estimate._parse_stored_as_ha_local(aware)

    assert got == datetime.datetime(2026, 9, 21, 12, 0), "today's reading, not the right one"
    # What the store provenance would say, for the size of the error:
    assert helpers.coerce_stamp(aware, helpers.STAMP_FROM_STORE) == datetime.datetime(
        2026, 9, 21, 10, 0
    )


def test_a_naive_stored_stamp_passes_through_either_way(split_zones):
    """The reason the defect is invisible: today every stored stamp is naive.

    Both rules leave a naive value alone, so the two readings only diverge once the
    write side starts producing aware stamps -- which is why the reader change and the
    writer change cannot be split the other way round.
    """
    naive = datetime.datetime(2026, 9, 21, 10, 0)

    assert live_estimate._parse_stored_as_ha_local(naive) == naive
    assert helpers.coerce_stamp(naive, helpers.STAMP_FROM_STORE) == naive
    assert helpers.coerce_stamp(naive, helpers.STAMP_FROM_CLIENT) == naive
