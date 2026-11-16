"""Checks that the hamiltonian is a valid quantum Hamiltonian and that the starting state obeys physics."""
import numpy as np

from src.config import Params
from src.hamiltonian import background_distribution, build_hamiltonian, initial_state
from src.simulate import run_quantum

SETTINGS = Params(n_qubits=4)


def test_hamiltonian_is_hermitian_and_power_of_two():
    """Quantum evolution needs a Hermitian matrix (equal to its conjugate transpose), and n qubits hold exactly 2^n numbers."""
    hamiltonian = build_hamiltonian(SETTINGS)
    assert hamiltonian.shape == (2**SETTINGS.n_qubits, 2**SETTINGS.n_qubits)
    assert np.allclose(hamiltonian, hamiltonian.conj().T)


def test_initial_state_obeys_gauss_law():
    """i * wavenumber * field = -(sum of ripple * spacing): the field must match the density ripple we started with."""
    state = initial_state(SETTINGS)
    spacing = SETTINGS.velocity_spacing
    ripple = state[1:] * np.sqrt(background_distribution(SETTINGS.velocities) / spacing)   # undo the rescaling
    assert np.isclose(1j * SETTINGS.wavenumber * state[0], -np.sum(ripple * spacing))


def test_circuit_conserves_norm():
    """The circuit is unitary, so total probability stays 1 (physically: total energy is conserved)."""
    states = run_quantum(SETTINGS)
    assert np.allclose(np.linalg.norm(states, axis=1), 1.0)
