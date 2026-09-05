"""The composed window: observed so far, extended over the hours still to come.

A zone whose module estimates solar radiation from the day's temperature range
commits with the DAILY FAO-56 equation, whose inputs are whole-window
quantities. Part-way through a window those quantities are not observable: at
mid-morning the extremes are the morning's, and ``sol_rad_from_t`` is
proportional to ``sqrt(Tmax - Tmin)``, so the shortfall is charged twice.

The construction here sidesteps that. The window's remaining hours
are filled from a forecast, the extremes are read off observed-plus-remainder,
and the remainder shrinks to nothing as the window closes -- so the inputs
converge on exactly what the commit will see, with no blend rule and no gate
times. Where no forecast exists the remainder comes from the site's own solar
geometry scaled by the amplitude of the windows already committed, which is a
weaker source and says so through the tier it publishes.
"""

import datetime

import pytest

from custom_components.smart_irrigation.day_projection import (
    TIER_OBSERVED,
    TIER_SELF_CONTAINED,
    TIER_SERVICE,
    compose_extremes,
    diurnal_fraction,
    diurnal_remainder,
    forecast_remainder,
    remainder_hours,
    solar_marks,
)
from custom_components.smart_irrigation.et_estimate import SiteGeometry

# The install's own coordinates, as every other test in this area uses.
GEO = SiteGeometry(39.68987, -84.07865, 311.0, -4.0, None)
# Midsummer, so sunrise and the peak are comfortably inside the day and the
# shape has room to be checked either side of them.
DAY = datetime.date(2026, 6, 21)


def _at(hour, day=DAY):
    return datetime.datetime.combine(day, datetime.time()) + datetime.timedelta(
        hours=hour
    )


class TestTheDiurnalShape:
    """A canonical curve, not a fit to today: 0 at the trough, 1 at the peak.

    It supplies only the SHAPE of the unobserved hours. Nothing about today's
    amplitude is inferred from a partial day, which is what made the fitted
    variant unusable at a late-evening anchor -- the observed part is all night
    and the amplitude comes out of a division by nearly nothing.
    """

    def test_the_trough_is_sunrise_and_the_peak_follows_solar_noon(self):
        sunrise, peak = solar_marks(GEO, DAY)

        # Sunrise at this latitude in midsummer is a little after 06:00 EDT and
        # solar noon a little after 13:30, so the peak lands mid-afternoon.
        assert 5.0 < sunrise < 7.0
        assert peak > sunrise
        assert 15.0 < peak < 17.0

    def test_it_runs_from_zero_at_the_trough_to_one_at_the_peak(self):
        sunrise, peak = solar_marks(GEO, DAY)

        assert diurnal_fraction(_at(sunrise), GEO) == pytest.approx(0.0, abs=1e-6)
        assert diurnal_fraction(_at(peak), GEO) == pytest.approx(1.0, abs=1e-6)

    def test_it_rises_through_the_morning_and_falls_through_the_night(self):
        sunrise, peak = solar_marks(GEO, DAY)
        morning = [
            diurnal_fraction(_at(sunrise + h), GEO)
            for h in range(int(peak - sunrise) + 1)
        ]
        evening = [diurnal_fraction(_at(peak + h), GEO) for h in range(1, 8)]

        assert morning == sorted(morning)
        assert evening == sorted(evening, reverse=True)
        assert all(0.0 <= f <= 1.0 for f in morning + evening)

    def test_the_curve_is_continuous_across_the_peak(self):
        _sunrise, peak = solar_marks(GEO, DAY)
        before = diurnal_fraction(_at(peak - 1 / 60), GEO)
        after = diurnal_fraction(_at(peak + 1 / 60), GEO)

        assert before == pytest.approx(1.0, abs=0.01)
        assert after == pytest.approx(1.0, abs=0.01)

    def test_the_small_hours_carry_the_previous_day_s_decay(self):
        """The window a night-anchored commit opens is mostly the falling limb,
        and it does not restart at midnight."""
        late = diurnal_fraction(_at(23.0), GEO)
        small = diurnal_fraction(_at(2.0), GEO)
        predawn = diurnal_fraction(_at(5.0), GEO)

        assert late > small > predawn >= 0.0


class TestTheHoursStillToCome:
    """The remainder covers the window's unobserved hours and nothing else."""

    def test_it_starts_after_now_and_stops_at_the_window_end(self):
        hours = remainder_hours(_at(9.5), _at(26.0))

        assert hours[0] > _at(9.5)
        assert hours[-1] <= _at(26.0)
        assert all(
            b - a == datetime.timedelta(hours=1)
            for a, b in zip(hours, hours[1:], strict=False)
        )

    def test_a_closed_window_has_no_remainder(self):
        """The property the whole construction rests on: once the window is
        over there is nothing left to project, so the composition is the
        observation and the estimate equals the commit exactly."""
        assert remainder_hours(_at(26.0), _at(26.0)) == []
        assert remainder_hours(_at(27.0), _at(26.0)) == []

    def test_the_post_midnight_tail_is_part_of_the_window(self):
        """A 02:00-anchored window runs to 02:00 the next day, so its coldest
        hours are usually on the following date. Dropping them would take the
        low from a daily forecast that never sees them."""
        hours = remainder_hours(_at(20.0), _at(26.0))
        dates = {h.date() for h in hours}

        assert DAY + datetime.timedelta(days=1) in dates


class TestComposingTheExtremes:
    def test_the_remainder_can_only_widen_the_observed_extremes(self):
        assert compose_extremes(12.0, 20.0, [15.0, 24.0, 8.0]) == (8.0, 24.0)
        assert compose_extremes(12.0, 20.0, [15.0, 16.0]) == (12.0, 20.0)

    def test_an_empty_remainder_leaves_the_observation_untouched(self):
        assert compose_extremes(12.0, 20.0, []) == (12.0, 20.0)


class TestTheForecastRemainder:
    def test_it_takes_the_forecast_s_own_temperatures_over_the_remaining_span(self):
        hourly = [(_at(h), 10.0 + h) for h in range(20, 30)]

        rem = forecast_remainder(hourly, _at(25.5), _at(28.0))

        assert rem == [10.0 + 26, 10.0 + 27, 10.0 + 28]

    def test_a_three_hourly_product_still_composes(self):
        """OpenWeatherMap's free forecast is three-hourly. The extremes are read
        off the samples rather than off an hourly grid, so a coarser series
        places them without anything being interpolated into existence."""
        three_hourly = [(_at(h), 10.0 + h) for h in range(18, 33, 3)]

        rem = forecast_remainder(three_hourly, _at(20.0), _at(26.0))

        assert rem == [10.0 + 21, 10.0 + 24]

    def test_a_forecast_that_does_not_reach_the_window_end_is_refused(self):
        """A partial remainder is worse than none: it would read the extremes
        off a window with a hole in it and call that the commit's."""
        hourly = [(_at(h), 10.0 + h) for h in range(24, 27)]

        assert forecast_remainder(hourly, _at(25.5), _at(30.0)) is None

    def test_a_hole_in_the_middle_is_refused(self):
        hourly = [(_at(h), 10.0 + h) for h in (20, 21, 22, 27, 28, 29, 30)]

        assert forecast_remainder(hourly, _at(20.5), _at(29.0)) is None

    def test_a_daily_forecast_is_refused(self):
        """Taking the window's post-midnight low from a daily forecast was
        refused: that low usually falls after the window closes, so the
        construction imports an extreme the commit never sees and never lets go
        of it. The gap guard is what keeps a daily series out."""
        daily = [(_at(12.0 + 24 * d), 20.0 + d) for d in range(4)]

        assert forecast_remainder(daily, _at(14.0), _at(26.0)) is None

    def test_no_forecast_at_all_is_refused(self):
        assert forecast_remainder(None, _at(9.0), _at(20.0)) is None
        assert forecast_remainder([], _at(9.0), _at(20.0)) is None


class TestTheSelfContainedRemainder:
    def test_it_passes_through_the_latest_observation(self):
        """Anchored on what the sensor is reading now, so it re-anchors every
        refresh instead of holding a projection made hours ago."""
        now = _at(9.0)
        rem = diurnal_remainder(now, 18.0, 12.0, GEO, _at(26.0))

        first = rem[0]
        # One hour on from 09:00 the curve has risen, but only by its own share
        # of the amplitude -- not to the amplitude itself.
        assert 18.0 < first < 18.0 + 12.0

    def test_it_reaches_a_peak_near_the_committed_amplitude_above_the_trough(self):
        rem = diurnal_remainder(_at(6.5), 14.0, 12.0, GEO, _at(30.0))

        # Started essentially at the trough, so the projected peak is the
        # amplitude above it, give or take the shape's own resolution.
        assert max(rem) == pytest.approx(26.0, abs=1.5)

    def test_without_an_amplitude_there_is_nothing_to_project(self):
        assert diurnal_remainder(_at(9.0), 18.0, None, GEO, _at(26.0)) is None
        assert diurnal_remainder(_at(9.0), 18.0, 0.0, GEO, _at(26.0)) is None

    def test_a_closed_window_projects_nothing(self):
        assert diurnal_remainder(_at(26.0), 18.0, 12.0, GEO, _at(26.0)) == []


class TestTheTierVocabulary:
    def test_the_tiers_are_distinct_and_stable(self):
        """Published as an entity attribute, so these strings are part of what
        a dashboard template reads."""
        assert len({TIER_SERVICE, TIER_SELF_CONTAINED, TIER_OBSERVED}) == 3
