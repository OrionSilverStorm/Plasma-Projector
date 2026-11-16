"""
Section 1: Physical Factors & Simulation Settings.

Defines the default plasma wave parameters, three distinct tokamak scenarios
(Gentle Wave, Short Wave, and Hot Plasma) for side-by-side comparison, and the
discrete velocity grid stored in the qubits. See README.md (Section 1).
"""

import numpy as np

# Default physical parameters and simulation grid settings (see README.md -> Section 1)
DEFAULT_CONFIG = {
    "n_qubits": 5,          # 5 qubits -> 2^5 = 32 state slots (1 electric field + 31 velocities)
    "wavenumber": 0.5,      # Factor 1: wave tightness (k = 2*pi / wavelength)
    "temperature": 1.0,     # Factor 2: electron temperature (T, normalised thermal spread)
    "density": 1.0,         # Factor 3: electron density (n_e, normalised plasma density)
    "max_velocity": 6.0,    # Velocity grid bounds [-max_velocity, +max_velocity]
    "end_time": 20.0,       # Total simulation time (in plasma oscillation ticks)
    "n_steps": 200,         # Time steps (dt = end_time / n_steps = 0.1)
}

# Named physics scenarios used to compare Quantum vs. Classical wave behavior side by side
SCENARIOS = [
    {
        "name": "Scenario A: Long, Gentle Wave (Slow Fade)",
        "short_label": "Scenario A (k=0.35, T=0.8)",
        "description": "Stretched-out wave in cooler plasma -> few electrons surf the wave -> fades slowly",
        "config": {**DEFAULT_CONFIG, "wavenumber": 0.35, "temperature": 0.8},
    },
    {
        "name": "Scenario B: Baseline Tokamak Ripple",
        "short_label": "Scenario B (k=0.50, T=1.0)",
        "description": "Standard wavelength and temperature -> moderate Landau damping",
        "config": {**DEFAULT_CONFIG, "wavenumber": 0.50, "temperature": 1.0},
    },
    {
        "name": "Scenario C: Tight Wave in Hotter Plasma (Fast Fade)",
        "short_label": "Scenario C (k=0.65, T=1.3)",
        "description": "Short wave + faster electrons -> strong energy absorption -> fades rapidly",
        "config": {**DEFAULT_CONFIG, "wavenumber": 0.65, "temperature": 1.3},
    },
]


def make_velocity_grid(n_qubits: int, max_velocity: float) -> tuple[np.ndarray, float]:
    """
    Build evenly spaced velocity buckets for qubit slots 1..(2^n - 1).
    Slot 0 is reserved for the electric field. See README.md (Section 1).
    """
    n_velocity_buckets = (2 ** n_qubits) - 1
    velocities = np.linspace(-max_velocity, max_velocity, n_velocity_buckets)
    dv = velocities[1] - velocities[0]
    return velocities, dv
