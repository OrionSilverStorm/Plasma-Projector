"""
simulate.py: runs the quantum circuits and turns the output into physics.

- `run_quantum`        simulate the circuit step by step and record |E(t)|^2
- `fit_damping_rate`   measure how fast |E|^2 decays, giving the Landau damping rate gamma
- `classify_stability` the "reactor controller" question: has this disturbance faded enough
                       by the time the magnets could react? Answered from measurement shots only.

How the circuit is simulated
----------------------------
One Trotter step is the same circuit every time. We convert that circuit ONCE into its 2^n x 2^n
unitary matrix U (exactly what the gates do, including Trotter error), then apply U repeatedly.
This gives exactly the same numbers as simulating gate by gate, but much faster.
"""
import numpy as np
from qiskit.quantum_info import Operator, Statevector
from scipy.signal import find_peaks

from src.circuits import prep_circuit, trotter_step
from src.config import Params
from src.hamiltonian import build_hamiltonian, field_energy, initial_state


def run_quantum(p: Params, order: int = 2) -> np.ndarray:
    """Evolve the plasma state with the Trotter circuit. Returns the state at every time in p.times."""
    H = build_hamiltonian(p)
    psi = Statevector(prep_circuit(initial_state(p))).data      # state produced by the prep circuit
    U = Operator(trotter_step(H, p.dt, order)).data              # unitary of one circuit step

    states = [psi]
    for _ in range(p.n_steps):
        psi = U @ psi                                             # one more time step
        states.append(psi)
    return np.array(states)


def fit_damping_rate(times: np.ndarray, energy: np.ndarray, t_start: float = 2.0,
                     t_end: float | None = None) -> float:
    """
    Estimate gamma from the decay of |E(t)|^2.

    |E|^2 oscillates (the wave sloshes back and forth) inside a shrinking envelope exp(2 gamma t).
    We take the oscillation PEAKS inside [t_start, t_end], fit a straight line to log(peak) against
    time, and halve the slope (the factor 2 appears because energy is amplitude squared).
    t_start skips the start-up transient; t_end should stay before the recurrence time.
    """
    t_end = times[-1] if t_end is None else t_end
    peaks, _ = find_peaks(energy)
    keep = peaks[(times[peaks] >= t_start) & (times[peaks] <= t_end)]
    if len(keep) < 2:
        raise ValueError("Not enough oscillation peaks in the fit window; extend t_max or n_steps.")
    slope, _ = np.polyfit(times[keep], np.log(energy[keep]), 1)
    return slope / 2


def window_indices(times: np.ndarray, t_check: float, window: float, n_samples: int) -> np.ndarray:
    """
    Pick `n_samples` time indices spread over [t_check, t_check + window].

    Why a window: |E|^2 oscillates, so a single snapshot might land in a trough (energy briefly
    stored in the particles) and look falsely "damped". Taking the largest value across about one
    oscillation (window ~ pi / omega ~ 2-3 time units) gives the wave's true remaining size.
    """
    targets = np.linspace(t_check, t_check + window, n_samples)
    return np.clip(np.searchsorted(times, targets), 0, len(times) - 1)


def envelope(times: np.ndarray, energy: np.ndarray, window: float = 3.0) -> np.ndarray:
    """Remaining-energy fraction at every time: max of |E|^2 over the next `window`, divided by |E(0)|^2."""
    return np.array([energy[window_indices(times, t, window, 8)].max() for t in times]) / energy[0]


def classify_stability(times: np.ndarray, energy: np.ndarray, t_check: float, threshold: float = 0.1,
                       window: float = 3.0, n_samples: int = 4, shots: int = 2000,
                       rng: np.random.Generator | None = None) -> dict:
    """
    Answer a controller's yes/no question from MEASUREMENTS only: "By time t_check, has the wave
    energy fallen below `threshold` times its starting value?"

    On hardware we never see |E|^2 directly. We run the circuit `shots` times and count how
    often all qubits read 0. Here those shots are drawn from the exact probability (a binomial
    draw). Real hardware would add noise on top. We do this at `n_samples` times across one
    oscillation (see `window_indices`) and keep the largest estimate.

    The point: this needs a FEW numbers (probabilities), not the whole quantum state.
    That sidesteps the readout bottleneck that limits most quantum PDE solvers.
    """
    rng = np.random.default_rng(0) if rng is None else rng
    idx = window_indices(times, t_check, window, n_samples)
    zeros_counted = rng.binomial(shots, energy[idx])             # simulated measurement outcomes
    measured_ratio = (zeros_counted / shots).max() / energy[0]   # estimated fraction of energy left
    return {
        "measured_ratio": measured_ratio,
        "true_ratio": energy[idx].max() / energy[0],
        "damped": bool(measured_ratio < threshold),              # True: safe to ignore. False: act.
        "circuit_runs": n_samples * shots,                       # total hardware cost of the answer
    }
