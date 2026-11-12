"""Checks that the matrix H is a valid quantum Hamiltonian and that the starting state obeys physics."""
import numpy as np

from src.config import Params
from src.hamiltonian import build_hamiltonian, initial_state, maxwellian
from src.simulate import run_quantum

P = Params(n_qubits=4)


def test_hamiltonian_is_hermitian_and_power_of_two():
    """Quantum evolution needs H = H^dagger, and n qubits hold exactly 2^n numbers."""
    H = build_hamiltonian(P)
    assert H.shape == (2**P.n_qubits, 2**P.n_qubits)
    assert np.allclose(H, H.conj().T)


def test_initial_state_obeys_gauss_law():
    """i k E = -integral(f1 dv): the field must match the density ripple we started with."""
    psi = initial_state(P)
    f1 = psi[1:] * np.sqrt(maxwellian(P.velocities) / P.dv)       # undo the u_j rescaling
    assert np.isclose(1j * P.k * psi[0], -np.sum(f1 * P.dv))


def test_circuit_conserves_norm():
    """The circuit is unitary, so total probability stays 1 (physically: total energy is conserved)."""
    states = run_quantum(P)
    assert np.allclose(np.linalg.norm(states, axis=1), 1.0)
