"""
config.py: every simulation setting in one place, plus conversion to real-world units.

NORMALISED UNITS (used everywhere else in the code)
---------------------------------------------------
Plasma physics has natural "rulers". Measuring with them removes most constants:
    time      measured in "plasma ticks": 1 / plasma_frequency
              (plasma_frequency = how fast displaced electrons snap back and forth)
    length    measured in "screening lengths" (the Debye length: the distance over which
              the plasma hides, or "screens", an electric charge)
    velocity  measured in "thermal speeds" (the typical speed of a hot electron)
In these units, temperature and density disappear from the equations. The only physical
input left is the `wavenumber` (how tightly packed the wave crests are, measured per
screening length). Temperature and density come back only when we convert answers into
seconds and metres (see `plasma_scales`).
"""
from dataclasses import dataclass

import numpy as np

# --- Real-world (SI) constants, only needed for the unit conversion in `plasma_scales` ---
VACUUM_PERMITTIVITY = 8.854e-12   # how easily electric fields pass through empty space  [F/m]
ELECTRON_CHARGE = 1.602e-19       # charge of one electron (size only)                    [C]
ELECTRON_MASS = 9.109e-31         # mass of one electron                                  [kg]


@dataclass(frozen=True)
class Params:
    """All knobs of one simulation run. Frozen, so a run can't silently change its settings."""

    wavenumber: float = 0.5   # 2*pi / wavelength. Larger = shorter wave, which damps (fades) faster
    n_qubits: int = 5         # qubits in the register; it stores 2**n_qubits numbers
    max_velocity: float = 6.0 # velocity grid covers [-max_velocity, max_velocity] (6 thermal speeds is effectively everything)
    end_time: float = 20.0    # how long to simulate (in plasma ticks)
    n_steps: int = 200        # number of time steps (each step = one Trotter step on the circuit)

    @property
    def n_velocities(self) -> int:
        """Number of velocity grid points. Slot 0 of the state holds the electric field, so 2**n - 1 are left."""
        return 2 ** self.n_qubits - 1

    @property
    def velocities(self) -> np.ndarray:
        """Velocity grid. An odd number of points makes it symmetric and includes velocity 0."""
        return np.linspace(-self.max_velocity, self.max_velocity, self.n_velocities)

    @property
    def velocity_spacing(self) -> float:
        """Gap between neighbouring velocity grid points."""
        return 2 * self.max_velocity / (self.n_velocities - 1)

    @property
    def time_step(self) -> float:
        """Length of one time step."""
        return self.end_time / self.n_steps

    @property
    def times(self) -> np.ndarray:
        """All sample times, from 0 to end_time (n_steps + 1 values)."""
        return np.linspace(0.0, self.end_time, self.n_steps + 1)

    @property
    def fake_revival_time(self) -> float:
        """
        Time at which the velocity grid having gaps (not being continuous) makes the wave FAKE a
        comeback: 2*pi / (wavenumber * velocity_spacing). Results after this time are artefacts.
        (Physicists call this the "recurrence time".)
        """
        return 2 * np.pi / (self.wavenumber * self.velocity_spacing)


def plasma_scales(temperature_ev: float, density_m3: float) -> dict:
    """
    Convert real plasma conditions into the natural rulers used by the simulation.

    temperature_ev : electron temperature in electron-volts (a tokamak core is ~10,000 eV)
    density_m3     : electrons per cubic metre (a tokamak is ~1e20)

    Returns plasma_frequency [rad/s], screening_length [m] and thermal_speed [m/s].
    Divide a normalised time by plasma_frequency to get seconds, and multiply a normalised
    length by screening_length to get metres.
    """
    temperature_joules = temperature_ev * ELECTRON_CHARGE                  # eV -> joules
    plasma_frequency = np.sqrt(density_m3 * ELECTRON_CHARGE**2 / (VACUUM_PERMITTIVITY * ELECTRON_MASS))
    thermal_speed = np.sqrt(temperature_joules / ELECTRON_MASS)            # typical electron speed
    return {
        "plasma_frequency": plasma_frequency,
        "screening_length": thermal_speed / plasma_frequency,              # distance covered in one tick
        "thermal_speed": thermal_speed,
    }
