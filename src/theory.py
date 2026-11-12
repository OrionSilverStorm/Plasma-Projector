"""
theory.py: the textbook answer that the quantum simulation is checked against.

This is a FORMULA, not a simulation. For a Maxwellian plasma, the wave frequency omega and
damping rate gamma solve the dispersion relation
     D(omega) = 1 + (1 + zeta * Z(zeta)) / k^2 = 0,      zeta = omega / (sqrt(2) k)
where Z is the "plasma dispersion function". Its root omega = omega_r + i*gamma is what our
quantum circuit should reproduce (k = 0.5 gives 1.4156 - 0.1533i).
"""
import numpy as np
from scipy.optimize import newton
from scipy.special import wofz


def plasma_z(zeta: complex) -> complex:
    """Plasma dispersion function Z(zeta) = i sqrt(pi) w(zeta), where w is the Faddeeva function."""
    return 1j * np.sqrt(np.pi) * wofz(zeta)


def landau_root(k: float) -> complex:
    """
    Solve D(omega) = 0 for the least-damped wave at wavenumber k.

    Returns omega = omega_r + i*gamma. A negative gamma means the wave damps; |E| ~ exp(gamma t).
    The starting guess is the Bohm-Gross frequency sqrt(1 + 3k^2), a good no-damping estimate.
    """
    def dispersion(omega):
        zeta = omega / (np.sqrt(2) * k)
        return 1 + (1 + zeta * plasma_z(zeta)) / k**2

    guess = np.sqrt(1 + 3 * k**2) - 0.1j
    return complex(newton(dispersion, guess, tol=1e-12, maxiter=200))
