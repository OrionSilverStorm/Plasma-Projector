"""
theory.py: the textbook answer that the quantum simulation is checked against.

This is a FORMULA, not a simulation. A plasma wave is described by ONE complex number:
    complex_frequency = oscillation_rate + i * damping_rate
    - oscillation_rate (real part): how fast the wave wiggles
    - damping_rate (imaginary part): how fast it fades; negative = shrinking, |field| ~ exp(damping_rate * t)
For a plasma with a bell-curve (thermal) spread of electron speeds, that number is the value that
makes the "dispersion relation" equal zero:
    1 + (1 + scaled * Z(scaled)) / wavenumber^2 = 0,     scaled = complex_frequency / (sqrt(2) * wavenumber)
where Z is a known special function (the "plasma dispersion function"). For wavenumber 0.5 the
answer is 1.4156 - 0.1533i, and our quantum circuit should reproduce it.
"""
import numpy as np
from scipy.optimize import newton
from scipy.special import wofz


def plasma_dispersion_function(scaled_frequency: complex) -> complex:
    """The special function Z = i * sqrt(pi) * w(scaled_frequency). SciPy provides w (the "Faddeeva function")."""
    return 1j * np.sqrt(np.pi) * wofz(scaled_frequency)


def landau_prediction(wavenumber: float) -> complex:
    """
    Solve the dispersion relation for the slowest-fading wave at this wavenumber.

    Returns oscillation_rate + i * damping_rate (read them with `.real` and `.imag`).
    Newton's method needs a starting guess: sqrt(1 + 3 * wavenumber^2) is the well-known
    no-damping estimate (the "Bohm-Gross frequency"), nudged slightly towards damping.
    """
    def dispersion_relation(complex_frequency):
        scaled = complex_frequency / (np.sqrt(2) * wavenumber)
        return 1 + (1 + scaled * plasma_dispersion_function(scaled)) / wavenumber**2

    guess = np.sqrt(1 + 3 * wavenumber**2) - 0.1j
    return complex(newton(dispersion_relation, guess, tol=1e-12, maxiter=200))
