"""
classical_simulation.py: ARCHIVED (not used by src/main.py right now).

The classical side of the comparison, parked here while the project focuses on the quantum side:
  - `exact_evolution`: exact answer exp(-i * hamiltonian * t) * start_state, used to measure Trotter error.
  - `classical_solve`: a standard classical ODE solver, timed, as a speed benchmark.

To bring it back: see archive/README.md.
"""
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import csr_matrix


def exact_evolution(hamiltonian: np.ndarray, start_state: np.ndarray, times: np.ndarray) -> np.ndarray:
    """
    Exact reference answer exp(-i * hamiltonian * t) * start_state at every time, computed classically.

    Method: find the hamiltonian's eigenvectors once ("special directions" that the matrix only
    stretches, by an amount called the eigenvalue). Along each of them, evolving in time just
    rotates a phase, exp(-i * eigenvalue * t), which is cheap to compute for any t.
    Returns an array with one row per time and one column per state entry.
    """
    eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
    coeffs = eigenvectors.conj().T @ start_state                  # start_state written in the eigenvector directions
    phases = np.exp(-1j * np.outer(times, eigenvalues))           # every eigenvector only rotates its phase
    return (phases * coeffs) @ eigenvectors.T


def classical_solve(hamiltonian: np.ndarray, start_state: np.ndarray,
                    times: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Classical time-stepping of (rate of change of state) = -i * hamiltonian * state, using
    SciPy's adaptive Runge-Kutta solver.

    The hamiltonian is stored as a sparse matrix (only the non-zero entries), which is how a real
    classical code would do it. Returns (states, seconds_taken).
    """
    sparse_hamiltonian = csr_matrix(hamiltonian)
    start = time.perf_counter()
    solution = solve_ivp(lambda t, state: -1j * (sparse_hamiltonian @ state), (times[0], times[-1]),
                         start_state, t_eval=times, rtol=1e-8, atol=1e-10)
    seconds = time.perf_counter() - start
    return solution.y.T, seconds
