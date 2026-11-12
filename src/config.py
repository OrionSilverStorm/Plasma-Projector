"""
config.py: every simulation setting in one place, plus conversion to real-world units.

NORMALISED UNITS (used everywhere else in the code)
---------------------------------------------------
Plasma physics has natural "rulers". Measuring with them removes most constants:
    time      in units of 1/omega_p   (omega_p = plasma frequency, how fast electrons snap back)
    length    in units of lambda_D    (Debye length, the distance over which charges get screened)
    velocity  in units of v_th        (thermal speed, = lambda_D * omega_p)
In these units, temperature and density disappear from the equations. The only physical
input left is the dimensionless wavenumber k*lambda_D (simply called `k` in this code).
Temperature and density come back only when we convert answers into seconds and metres
(see `plasma_scales`).
"""
from dataclasses import dataclass

import numpy as np

# --- SI constants (only needed for the real-world unit conversion) ---
EPS0 = 8.854e-12   # vacuum permittivity            [F/m]
Q_E = 1.602e-19    # elementary charge              [C]
M_E = 9.109e-31    # electron mass                  [kg]


@dataclass(frozen=True)
class Params:
    """All knobs of one simulation run. Frozen, so a run can't silently change its settings."""

    k: float = 0.5          # wavenumber k*lambda_D: larger means a shorter wave that damps faster
    n_qubits: int = 5       # qubits in the register; it stores 2**n_qubits numbers
    v_max: float = 6.0      # velocity grid covers [-v_max, v_max] (6 thermal speeds is effectively everything)
    t_max: float = 20.0     # how long to simulate (units of 1/omega_p)
    n_steps: int = 200      # number of time steps (each step = one Trotter step on the circuit)

    @property
    def n_v(self) -> int:
        """Number of velocity grid points. Index 0 of the state holds E, so 2**n - 1 are left for velocities."""
        return 2 ** self.n_qubits - 1

    @property
    def velocities(self) -> np.ndarray:
        """Velocity grid. An odd number of points makes it symmetric and includes v = 0."""
        return np.linspace(-self.v_max, self.v_max, self.n_v)

    @property
    def dv(self) -> float:
        """Spacing between neighbouring velocity grid points (Delta v)."""
        return 2 * self.v_max / (self.n_v - 1)

    @property
    def dt(self) -> float:
        """Length of one time step."""
        return self.t_max / self.n_steps

    @property
    def times(self) -> np.ndarray:
        """All sample times, from 0 to t_max (n_steps + 1 values)."""
        return np.linspace(0.0, self.t_max, self.n_steps + 1)

    @property
    def recurrence_time(self) -> float:
        """
        Time at which the discrete velocity grid causes a FAKE revival of the wave:
        T_R = 2*pi / (k * dv). Results after this time are numerical artefacts.
        """
        return 2 * np.pi / (self.k * self.dv)


def plasma_scales(temperature_ev: float, density_m3: float) -> dict:
    """
    Convert real plasma conditions into the natural rulers used by the simulation.

    temperature_ev : electron temperature in electron-volts (a tokamak core is ~10,000 eV)
    density_m3     : electron density in particles per cubic metre (a tokamak is ~1e20)

    Returns omega_p [rad/s], lambda_D [m] and v_th [m/s]. Multiply a normalised time by
    1/omega_p to get seconds, and a normalised length by lambda_D to get metres.
    """
    temperature_j = temperature_ev * Q_E                                  # eV -> joules
    omega_p = np.sqrt(density_m3 * Q_E**2 / (EPS0 * M_E))                # plasma frequency
    v_th = np.sqrt(temperature_j / M_E)                                   # thermal speed
    return {"omega_p": omega_p, "lambda_D": v_th / omega_p, "v_th": v_th}
