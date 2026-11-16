"""
Section 2: Encoding Physics into Qubits & Building the Equation Matrix.

For the full explanation of the Maxwellian bell curve, Vlasov-Ampere equations,
Hermitian Hamiltonian matrix H, and Gauss's Law initial state, see README.md (Section 2).
"""

import numpy as np

from config import make_velocity_grid


def maxwellian_bell_curve(velocities: np.ndarray, temperature: float) -> np.ndarray:
    """Evaluate the Maxwellian background electron speed distribution f0(v). See README.md (Section 2)."""
    return np.exp(-(velocities ** 2) / (2.0 * temperature)) / np.sqrt(2.0 * np.pi * temperature)


def build_hamiltonian_matrix(config: dict) -> np.ndarray:
    """
    Build the (2^n x 2^n) Hermitian Hamiltonian matrix H encoding wavenumber,
    temperature, and density. See README.md (Section 2).
    """
    n_qubits = config["n_qubits"]
    k = config["wavenumber"]
    temperature = config["temperature"]
    density = config["density"]

    velocities, dv = make_velocity_grid(n_qubits, config["max_velocity"])
    f0 = maxwellian_bell_curve(velocities, temperature)
    coupling = np.sqrt(density) * velocities * np.sqrt(f0 * dv)

    matrix_size = 2 ** n_qubits
    H = np.zeros((matrix_size, matrix_size), dtype=complex)

    # Diagonal: electron coasting; Row 0 / Col 0: field-velocity coupling (see README.md -> Section 2)
    H[1:, 1:] = np.diag(k * velocities)
    H[0, 1:] = 1j * coupling
    H[1:, 0] = -1j * coupling

    return H


def create_initial_qubit_state(config: dict) -> np.ndarray:
    """
    Build the normalised 2^n starting state vector at t = 0 using Gauss's Law
    for slot 0 and the background ripple for slots 1..(2^n - 1). See README.md (Section 2).
    """
    velocities, dv = make_velocity_grid(config["n_qubits"], config["max_velocity"])
    f0 = maxwellian_bell_curve(velocities, config["temperature"])

    velocity_slots = np.sqrt(f0 * dv)
    electric_field_slot = 1j * np.sum(f0 * dv) / config["wavenumber"]

    raw_state = np.concatenate(([electric_field_slot], velocity_slots)).astype(complex)
    return raw_state / np.linalg.norm(raw_state)
