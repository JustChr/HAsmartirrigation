"""Every weather client must reduce sea-level pressure the same way.

`MAPPING_PRESSURE` has to hold one physical quantity: the calc modules read it
as station pressure (FAO-56 takes the psychrometric constant from it). Before
this was shared, four clients carried four copies of the conversion and two of
them were still the dimensionally-broken near-identity — so the same location
produced a different pressure depending on which weather service was selected.

These tests fail if any client grows its own copy again.
"""

import pytest

from custom_components.irrigation_plus.pressure import relative_to_absolute_pressure
from custom_components.irrigation_plus.weathermodules.MetOfficeClient import (
    MetOfficeClient,
)
from custom_components.irrigation_plus.weathermodules.OpenMeteoClient import (
    OpenMeteoClient,
)

_ELEVATION = 311.0
_SEA_LEVEL_HPA = 1020.0


def test_openmeteo_matches_the_shared_conversion():
    client = OpenMeteoClient(latitude=0.0, longitude=0.0, elevation=_ELEVATION)
    assert client._abs_pressure(_SEA_LEVEL_HPA) == pytest.approx(
        relative_to_absolute_pressure(_SEA_LEVEL_HPA, _ELEVATION)
    )


def test_metoffice_matches_the_shared_conversion():
    """Met Office reports mslp in Pa, so it converts to hPa first."""
    client = MetOfficeClient("key", latitude=0.0, longitude=0.0, elevation=_ELEVATION)
    assert client._abs_pressure_from_pa(_SEA_LEVEL_HPA * 100.0) == pytest.approx(
        relative_to_absolute_pressure(_SEA_LEVEL_HPA, _ELEVATION)
    )


@pytest.mark.parametrize(
    ("name", "call"),
    [
        (
            "openmeteo",
            lambda: OpenMeteoClient(
                latitude=0.0, longitude=0.0, elevation=_ELEVATION
            )._abs_pressure(_SEA_LEVEL_HPA),
        ),
        (
            "metoffice",
            lambda: MetOfficeClient(
                "key", latitude=0.0, longitude=0.0, elevation=_ELEVATION
            )._abs_pressure_from_pa(_SEA_LEVEL_HPA * 100.0),
        ),
    ],
)
def test_correction_is_not_a_near_identity(name, call):
    """The old formula moved 1020 hPa by 1.6e-5. The real correction is ~37 hPa."""
    corrected = call()
    assert corrected < _SEA_LEVEL_HPA - 30.0, f"{name} barely moved the pressure"
    assert corrected == pytest.approx(982.9, abs=0.5)


def test_zero_elevation_is_a_no_op():
    """Installs that never set an elevation must be unaffected by the correction."""
    client = OpenMeteoClient(latitude=0.0, longitude=0.0, elevation=0)
    assert client._abs_pressure(_SEA_LEVEL_HPA) == pytest.approx(_SEA_LEVEL_HPA)
