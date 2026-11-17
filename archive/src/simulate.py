"""
simulate.py: runs the quantum circuits and turns the output into physics.

- `run_quantum`        simulate the circuit step by step and record the state at every time
- `fit_damping_rate`   measure how fast the field energy fades, giving the Landau damping rate
- `classify_stability` the "reactor controller" question: has this disturbance faded enough
                       by the time the magnets could react? Answered from measurement shots only.

How the circuit is simulated
----------------------------
One Trotter step is the same circuit every time. We convert that circuit ONCE into its 2^n x 2^n
unitary matrix (exactly what the gates do, including Trotter error), then apply it repeatedly.
This gives exactly the same numbers as simulating gate by gate, but much faster.
"""
import numpy as np
from qiskit.quantum_info import Operator, Statevector
from scipy.signal import find_peaks

from src.circuits import prep_circuit, trotter_step
from src.config import Params
from src.hamiltonian import build_hamiltonian, initial_state


def run_quantum(settings: Params, order: int = 2) -> np.ndarray:
    """Evolve the plasma state with the Trotter circuit. Returns the state at every time in settings.times."""
    hamiltonian = build_hamiltonian(settings)
    state = Statevector(prep_circuit(initial_state(settings))).data            # state produced by the prep circuit
    step_matrix = Operator(trotter_step(hamiltonian, settings.time_step, order)).data   # what one circuit step does

    states = [state]
    for _ in range(settings.n_steps):
        state = step_matrix @ state                                             # one more time step
        states.append(state)
    return np.array(states)


def fit_damping_rate(times: np.ndarray, energy: np.ndarray, fit_start: float = 2.0,
                     fit_end: float | None = None) -> float:
    """
    Estimate the damping rate from how the field energy fades.

    The energy oscillates (the wave sloshes back and forth) inside a shrinking envelope
    exp(2 * damping_rate * t). We take the oscillation PEAKS inside [fit_start, fit_end], fit a
    straight line to log(peak) against time, and halve the slope (the 2 appears because energy
    is field squared). fit_start skips the start-up wobble; fit_end should stay before the fake revival.
    """
    fit_end = times[-1] if fit_end is None else fit_end
    peaks, _ = find_peaks(energy)
    keep = peaks[(times[peaks] >= fit_start) & (times[peaks] <= fit_end)]
    if len(keep) < 2:
        raise ValueError("Not enough oscillation peaks in the fit window; extend end_time or n_steps.")
    slope, _ = np.polyfit(times[keep], np.log(energy[keep]), 1)
    return slope / 2


def window_indices(times: np.ndarray, check_time: float, window: float, n_samples: int) -> np.ndarray:
    """
    Pick `n_samples` time indices spread over [check_time, check_time + window].

    Why a window: the energy oscillates, so a single snapshot might land in a trough (energy
    briefly stored in the particles) and look falsely "damped". Taking the largest value across
    about one oscillation (window ~ 2-3 time units) gives the wave's true remaining size.
    """
    targets = np.linspace(check_time, check_time + window, n_samples)
    return np.clip(np.searchsorted(times, targets), 0, len(times) - 1)


def envelope(times: np.ndarray, energy: np.ndarray, window: float = 3.0) -> np.ndarray:
    """Fraction of energy left at every time: max energy over the next `window`, divided by the starting energy."""
    return np.array([energy[window_indices(times, t, window, 8)].max() for t in times]) / energy[0]


def classify_stability(times: np.ndarray, energy: np.ndarray, check_time: float, threshold: float = 0.1,
                       window: float = 3.0, n_samples: int = 4, shots: int = 2000,
                       rng: np.random.Generator | None = None) -> dict:
    """
    Answer a controller's yes/no question from MEASUREMENTS only: "By check_time, has the wave
    energy fallen below `threshold` times its starting value?"

    On hardware we never see the energy directly. We run the circuit `shots` times and count how
    often all qubits read 0. Here those shots are drawn from the exact probability (a binomial
    draw). Real hardware would add noise on top. We do this at `n_samples` times across one
    oscillation (see `window_indices`) and keep the largest estimate.

    The point: this needs a FEW numbers (probabilities), not the whole quantum state.
    That sidesteps the readout bottleneck that limits most quantum PDE solvers.
    """
    rng = np.random.default_rng(0) if rng is None else rng
    sample_indices = window_indices(times, check_time, window, n_samples)
    zeros_counted = rng.binomial(shots, energy[sample_indices])     # simulated measurement outcomes
    measured_ratio = (zeros_counted / shots).max() / energy[0]       # estimated fraction of energy left
    return {
        "measured_ratio": measured_ratio,
        "true_ratio": energy[sample_indices].max() / energy[0],
        "damped": bool(measured_ratio < threshold),                  # True: safe to ignore. False: act.
        "circuit_runs": n_samples * shots,                           # total hardware cost of the answer
    }
