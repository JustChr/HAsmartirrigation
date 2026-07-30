"""Barometric conversion between sea-level and station pressure.

A leaf module on purpose: it imports nothing from the package, so the weather
clients can share it. They cannot import ``helpers`` for this, because
``helpers`` imports the clients at module level and the cycle breaks whichever
one is loaded first.
"""

# International Standard Atmosphere, troposphere layer. The barometric formula
#     P_station = P_sealevel * (1 - L*h/T0) ** (g*M/(R*L))
# collapses to these three numbers: L is the lapse rate, T0 the sea-level
# temperature, and the exponent g*M/(R*L) is dimensionless (~5.255 for
# g = 9.80665 m/s^2, M = 0.0289644 kg/mol, R = 8.31447 J/(mol*K)).
ISA_LAPSE_RATE = 0.0065  # K/m
ISA_SEA_LEVEL_TEMPERATURE = 288.15  # K
ISA_BAROMETRIC_EXPONENT = 5.255


def relative_to_absolute_pressure(pressure, height):
    """Convert sea-level ("relative") pressure in hPa to station pressure at height m.

    Station pressure is always LOWER than the sea-level value a station reduces
    its reading to, and the gap is large: at 311 m, 1020 hPa is really ~983 hPa.
    The calc modules read ``MAPPING_PRESSURE`` as station pressure (FAO-56 takes
    the psychrometric constant from it), so leaving a relative-typed reading
    uncorrected biases ET upward.

    Cross-check on the model: this agrees with ``helpers.altitudeToPressure``
    (same atmosphere, solved for pressure instead of altitude) to within
    0.01 hPa at 311 m.
    """
    return (
        pressure
        * (1 - ISA_LAPSE_RATE * float(height) / ISA_SEA_LEVEL_TEMPERATURE)
        ** ISA_BAROMETRIC_EXPONENT
    )
