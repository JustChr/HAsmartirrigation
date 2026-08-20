"""Issue #81: the solar azimuth bore no relation to the bearing the user typed.

Two errors compounded. ``calculate_solar_azimuth`` SUBTRACTED the longitude
correction where east-positive longitude needs it ADDED, and
``scheduler._resolve_event_instant`` handed it naive LOCAL time while the
function documented (and read) UTC. The combined offset is
``tz_offset - 2*longitude/15`` hours of solar time, which is ~zero across
central Europe and hours away in the Americas and Australia — which is why it
survived so long in a project maintained from Germany.

Correcting the maths alone would move every existing schedule. So the repair
also rewrites each stored angle to the bearing the sun really holds at that
schedule's CURRENT fire time: the schedule keeps its time, and the number in
the UI starts meaning something.
"""

import datetime
import inspect
import math
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from homeassistant.util import dt as dt_util

from custom_components.smart_irrigation import (
    SmartIrrigationCoordinator,
    async_setup_entry,
    const,
)
from custom_components.smart_irrigation.helpers import (
    calculate_solar_azimuth,
    corrected_azimuth_bearing,
    find_next_solar_azimuth_time,
    legacy_solar_azimuth,
)

# --------------------------------------------------------------------------- #
# the maths
# --------------------------------------------------------------------------- #


def _reference_azimuth(lat, lon, utc_dt):
    """An independent re-implementation, written from the formula rather than
    from the code under test, so this is a real cross-check and not a restating
    of whatever helpers.py happens to do."""
    doy = utc_dt.timetuple().tm_yday
    dec = math.radians(23.45 * math.sin(math.radians(360 * (284 + doy) / 365)))
    hours = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    hour_angle = math.radians((hours + lon / 15.0 - 12) * 15)
    lat_r = math.radians(lat)
    a = math.atan2(
        math.sin(hour_angle),
        math.cos(hour_angle) * math.sin(lat_r) - math.tan(dec) * math.cos(lat_r),
    )
    return (math.degrees(a) + 180) % 360


def test_solar_noon_at_greenwich_is_due_south():
    at = datetime.datetime(2026, 6, 21, 12, tzinfo=datetime.UTC)
    assert calculate_solar_azimuth(45.0, 0.0, at) == pytest.approx(180.0, abs=0.5)


def test_solar_noon_one_hour_east_is_an_hour_earlier_in_utc():
    """The headline symptom from the issue: 15 deg east reaches solar noon at
    11:00 UTC. The old code answered ~121 deg there and put solar noon at 13:00,
    two hours late — the 2*longitude/15 signature."""
    at = datetime.datetime(2026, 6, 21, 11, tzinfo=datetime.UTC)
    assert calculate_solar_azimuth(45.0, 15.0, at) == pytest.approx(180.0, abs=0.5)


@pytest.mark.parametrize(
    ("lat", "lon"),
    [(52.5, 13.4), (33.45, -112.07), (-31.95, 115.86), (51.5, -0.1), (0.0, 0.0)],
)
def test_matches_an_independent_implementation_at_every_longitude(lat, lon):
    for hour in range(0, 24, 3):
        at = datetime.datetime(2026, 6, 21, hour, tzinfo=datetime.UTC)
        assert calculate_solar_azimuth(lat, lon, at) == pytest.approx(
            _reference_azimuth(lat, lon, at), abs=1e-6
        )


def test_an_aware_timestamp_is_converted_rather_than_read_as_utc():
    """The scheduler used to strip the zone and pass naive local time. Any
    aware value must now give the same answer as its UTC equivalent."""
    utc = datetime.datetime(2026, 6, 21, 18, tzinfo=datetime.UTC)
    other = utc.astimezone(datetime.timezone(datetime.timedelta(hours=-7)))
    assert calculate_solar_azimuth(33.45, -112.07, other) == pytest.approx(
        calculate_solar_azimuth(33.45, -112.07, utc)
    )


def test_the_legacy_helper_still_reproduces_the_reported_number():
    """Pinned so the repair below cannot silently stop reconstructing the old
    behaviour: the issue quotes 301.55 deg for Phoenix at noon local."""
    assert legacy_solar_azimuth(
        33.45, -112.07, datetime.datetime(2026, 6, 21, 12)
    ) == pytest.approx(301.55, abs=0.01)


# --------------------------------------------------------------------------- #
# the repair
# --------------------------------------------------------------------------- #


def test_corrected_bearing_is_the_true_bearing_at_the_old_fire_time():
    lat, lon = 33.45, -112.07
    reference = dt_util.utcnow()
    bearing, fire_time = corrected_azimuth_bearing(lat, lon, 90.0, reference)

    assert bearing is not None
    # The whole point: at the instant the schedule already fires, the corrected
    # bearing is what the sun is really doing.
    assert calculate_solar_azimuth(lat, lon, fire_time) == pytest.approx(
        bearing, abs=0.5
    )
    # ...and it is NOT the stored angle, or there would be nothing to repair.
    assert abs(bearing - 90.0) > 1.0


def test_the_repaired_schedule_fires_at_the_same_time_as_before():
    """End to end: search with the legacy maths for the OLD angle, and with the
    corrected maths for the NEW one, and land at the same instant."""
    lat, lon = 33.45, -112.07
    reference = dt_util.utcnow()
    old_fire = find_next_solar_azimuth_time(
        lat,
        lon,
        90.0,
        dt_util.as_local(reference).replace(tzinfo=None),
        azimuth_fn=legacy_solar_azimuth,
    )
    bearing, _ = corrected_azimuth_bearing(lat, lon, 90.0, reference)

    new_fire = find_next_solar_azimuth_time(lat, lon, round(bearing), reference)

    assert new_fire is not None
    drift = abs((dt_util.as_utc(old_fire) - new_fire).total_seconds())
    assert drift <= 15 * 60, f"fire time moved by {drift / 60:.1f} min"


# --------------------------------------------------------------------------- #
# the one-shot latch
# --------------------------------------------------------------------------- #


class _Store:
    def __init__(self, schedules, corrected=False):
        self._config = {
            const.CONF_RECURRING_SCHEDULES: schedules,
            const.CONF_AZIMUTH_BEARING_CORRECTED: corrected,
        }
        self.updates = []

    async def async_get_config(self):
        return dict(self._config)

    async def async_update_config(self, changes):
        self.updates.append(dict(changes))
        self._config.update(changes)


def _coord(schedules, corrected=False, lat=33.45, lon=-112.07):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.hass = Mock()
    coord.hass.config = SimpleNamespace(latitude=lat, longitude=lon)
    coord.store = _Store(schedules, corrected)
    return coord


def _schedule(**over):
    # A schedule carries a mode per BOUND, so the repair runs per bound rather
    # than per schedule. This one is azimuth-bounded at its Start.
    s = {
        const.SCHEDULE_CONF_NAME: "Morning",
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_SOLAR_AZIMUTH,
        const.SCHEDULE_CONF_START_AZIMUTH: 90,
    }
    s.update(over)
    return s


async def test_the_stored_angle_is_rewritten_and_latched():
    schedules = [_schedule()]
    coord = _coord(schedules)

    await coord.async_correct_solar_azimuth_bearings()

    assert schedules[0][const.SCHEDULE_CONF_START_AZIMUTH] != 90
    written = coord.store.updates[-1]
    assert written[const.CONF_AZIMUTH_BEARING_CORRECTED] is True
    assert written[const.CONF_RECURRING_SCHEDULES] is schedules


async def test_it_runs_only_once():
    schedules = [_schedule()]
    coord = _coord(schedules, corrected=True)

    await coord.async_correct_solar_azimuth_bearings()

    assert schedules[0][const.SCHEDULE_CONF_START_AZIMUTH] == 90
    assert coord.store.updates == []


async def test_non_azimuth_schedules_are_untouched():
    other = {
        const.SCHEDULE_CONF_NAME: "Daily",
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_START_TIME: "06:00",
    }
    schedules = [dict(other)]
    coord = _coord(schedules)

    await coord.async_correct_solar_azimuth_bearings()

    assert schedules[0] == other
    # Still latched, so it never runs again.
    assert coord.store.updates[-1][const.CONF_AZIMUTH_BEARING_CORRECTED] is True
    assert const.CONF_RECURRING_SCHEDULES not in coord.store.updates[-1]


async def test_a_greenwich_utc_install_sees_no_change():
    """Where the two errors cancel there is nothing to repair, and the user must
    not be told their schedule moved when it did not."""
    schedules = [_schedule()]
    coord = _coord(schedules, lat=51.5, lon=0.0)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(dt_util, "DEFAULT_TIME_ZONE", datetime.UTC)
        await coord.async_correct_solar_azimuth_bearings()

    assert schedules[0][const.SCHEDULE_CONF_START_AZIMUTH] == 90
    assert const.CONF_RECURRING_SCHEDULES not in coord.store.updates[-1]


def test_setup_runs_the_repair_before_schedules_are_loaded():
    """Ordering matters: RecurringScheduleManager caches what it loads, so a
    repair running afterwards would leave the in-memory copy on the old angles
    until something else reloaded them.

    Asserted against the real source of async_setup_entry rather than by driving
    two mocks in the order we want to see — that would only restate the call
    order the test itself chose.
    """
    source = inspect.getsource(async_setup_entry)
    repair = source.index("async_correct_solar_azimuth_bearings")
    load = source.index("async_load_schedules")
    assert repair < load
