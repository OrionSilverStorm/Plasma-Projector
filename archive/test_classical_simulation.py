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
    p = Params(n_qubits=4)
    H, psi0 = build_hamiltonian(p), initial_state(p)
    states, _ = classical_solve(H, psi0, p.times)
    assert np.allclose(states, exact_evolution(H, psi0, p.times), atol=1e-6)


def test_quantum_circuit_matches_exact():
    """Trotter error is small: the circuit's final state overlaps the exact one with fidelity > 0.99."""
    p = Params()
    quantum = run_quantum(p)[-1]
    exact = exact_evolution(build_hamiltonian(p), initial_state(p), p.times)[-1]
    assert abs(np.vdot(exact, quantum)) ** 2 > 0.99
