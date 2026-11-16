"""
ARCHIVED tests for the classical simulation. They're not run by default (pytest.ini only looks in tests/).
Run them explicitly with:  python -m pytest archive
"""
import numpy as np

from archive.classical_simulation import classical_solve, exact_evolution
from src.config import Params
from src.hamiltonian import build_hamiltonian, initial_state
from src.simulate import run_quantum


def test_classical_solver_matches_exact():
    """The classical ODE solver and the exact matrix exponential must agree."""
    settings = Params(n_qubits=4)
    hamiltonian, start_state = build_hamiltonian(settings), initial_state(settings)
    states, _ = classical_solve(hamiltonian, start_state, settings.times)
    assert np.allclose(states, exact_evolution(hamiltonian, start_state, settings.times), atol=1e-6)


def test_quantum_circuit_matches_exact():
    """Trotter error is small: the circuit's final state overlaps the exact one with fidelity > 0.99."""
    settings = Params()
    quantum = run_quantum(settings)[-1]
    exact = exact_evolution(build_hamiltonian(settings), initial_state(settings), settings.times)[-1]
    assert abs(np.vdot(exact, quantum)) ** 2 > 0.99
