"""
classical_simulation.py: ARCHIVED (not used by src/main.py right now).

The classical side of the comparison, parked here while the project focuses on the quantum side:
  - `exact_evolution`: exact answer psi(t) = exp(-i H t) psi0, used to measure Trotter error.
  - `classical_solve`: a standard classical ODE solver, timed, as a speed benchmark.

To bring it back: see archive/README.md.
"""
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import csr_matrix


def exact_evolution(H: np.ndarray, psi0: np.ndarray, times: np.ndarray) -> np.ndarray:
    """
    Exact reference answer psi(t) = exp(-i H t) psi0 at every time, computed classically.

    Method: diagonalise H once (H = V diag(w) V^dagger). Then exp(-i H t) = V diag(exp(-i w t)) V^dagger.
    Returns an array with one row per time and one column per state entry.
    """
    w, V = np.linalg.eigh(H)
    coeffs = V.conj().T @ psi0                      # psi0 written in H's eigenbasis
    phases = np.exp(-1j * np.outer(times, w))       # every eigenvector only rotates its phase
    return (phases * coeffs) @ V.T


def classical_solve(H: np.ndarray, psi0: np.ndarray, times: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Classical time-stepping of d psi/dt = -i H psi using SciPy's adaptive Runge-Kutta solver.

    H is stored as a sparse matrix (only the non-zero entries), which is how a real
    classical code would do it. Returns (states, seconds_taken).
    """
    H_sparse = csr_matrix(H)
    start = time.perf_counter()
    sol = solve_ivp(lambda t, y: -1j * (H_sparse @ y), (times[0], times[-1]), psi0,
                    t_eval=times, rtol=1e-8, atol=1e-10)
    seconds = time.perf_counter() - start
    return sol.y.T, seconds
