"""
Section 1: Physical Factors & Simulation Settings.

For the full explanation of wavenumber (k), temperature (T), density (n_e),
qubit slots, and the discrete velocity grid, see README.md (Section 1).
"""

import numpy as np

# Default physical parameters and simulation grid settings (see README.md -> Section 1)
DEFAULT_CONFIG = {
    "n_qubits": 5,          # 5 qubits -> 2^5 = 32 state slots
    "wavenumber": 0.5,      # Factor 1: wave tightness (k)
    "temperature": 1.0,     # Factor 2: electron temperature (T, normalised)
    "density": 1.0,         # Factor 3: electron density (n_e, normalised)
    "max_velocity": 6.0,    # Velocity grid bounds [-max_velocity, +max_velocity]
    "end_time": 20.0,       # Total simulation time (plasma oscillation ticks)
    "n_steps": 200,         # Time steps (dt = end_time / n_steps = 0.1)
}


def make_velocity_grid(n_qubits: int, max_velocity: float) -> tuple[np.ndarray, float]:
    """
    Build evenly spaced velocity buckets for qubit slots 1..(2^n - 1).
    Slot 0 is reserved for the electric field. See README.md (Section 1).
    """
    n_velocity_buckets = (2 ** n_qubits) - 1
    velocities = np.linspace(-max_velocity, max_velocity, n_velocity_buckets)
    dv = velocities[1] - velocities[0]
    return velocities, dv
