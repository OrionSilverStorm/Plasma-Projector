"""
Section 4: Analysing Data (Measuring How Fast the Wave Fades & Stability Threshold).

Includes:
1. `measure_damping_rate`: Peak detection + log-linear regression to extract the Landau damping rate.
2. `compute_remaining_energy_envelope`: Sliding-window peak energy ratio (E(t) / E(0)) so oscillation
   troughs aren't mistaken for damping.
3. `classify_reactor_stability`: Answers the reactor controller's yes/no question ("Has the wave dropped
   below 10% energy by check_time?") from hardware measurement shots alone.

For the full explanation of exponential peak fitting, the discrete-grid fake revival cutoff,
and the 10% stability threshold heatmap, see README.md (Section 4).
"""

import numpy as np
from scipy.signal import find_peaks

from config import make_velocity_grid


def measure_damping_rate(times: np.ndarray, energy: np.ndarray, config: dict) -> tuple[float, np.ndarray]:
    """
    Find energy peaks before the discrete-grid revival time and fit a straight line
    to log(peak_energy) to extract the Landau damping rate. See README.md (Section 4).
    """
    _, dv = make_velocity_grid(config["n_qubits"], config["max_velocity"])
    fake_revival_time = 2.0 * np.pi / (config["wavenumber"] * dv)
    fit_start = 2.0
    fit_end = min(config["end_time"], 0.8 * fake_revival_time)

    peak_indices, _ = find_peaks(energy)
    valid_peaks = peak_indices[
        (times[peak_indices] >= fit_start)
        & (times[peak_indices] <= fit_end)
        & (energy[peak_indices] >= 1e-6)
    ]

    slope, intercept = np.polyfit(times[valid_peaks], np.log(energy[valid_peaks]), deg=1)

    # Energy ~ |Field|^2 ~ exp(2 * damping_rate * t), so divide slope by 2
    damping_rate = slope / 2.0
    fitted_envelope = np.exp(intercept + slope * times)
    return damping_rate, fitted_envelope


def _window_sample_indices(times: np.ndarray, check_time: float, window: float, n_samples: int) -> np.ndarray:
    """
    Pick `n_samples` time indices spread across [check_time, check_time + window].
    Because the electric field sloshes back and forth into particle motion, a single snapshot
    could land in a temporary trough (0 energy) even when the wave is still strong.
    Sampling across one oscillation bounce (`window = 3.0`) catches the true remaining peak.
    """
    targets = np.linspace(check_time, check_time + window, n_samples)
    return np.clip(np.searchsorted(times, targets), 0, len(times) - 1)


def compute_remaining_energy_envelope(times: np.ndarray, energy: np.ndarray, window: float = 3.0) -> np.ndarray:
    """
    Compute the fraction of wave energy left at every time t:
        max(energy in [t, t + window]) / energy[0]
    Used to draw the 10% energy threshold heatmap (`4_stability_threshold_heatmap.png`).
    """
    return np.array([
        energy[_window_sample_indices(times, float(t), window, 8)].max()
        for t in times
    ]) / energy[0]


def classify_reactor_stability(
    times: np.ndarray,
    energy: np.ndarray,
    check_time: float = 8.0,
    threshold: float = 0.10,
    window: float = 3.0,
    n_samples: int = 4,
    shots: int = 2000,
) -> dict:
    """
    Answer the tokamak controller's yes/no question from quantum hardware shots alone:
    "By `check_time`, has the wave's energy fallen below `threshold` (10%) of its starting value?"
    Avoids reading out the full 2^n quantum state by measuring only P(|00000>) at 4 points.
    """
    rng = np.random.default_rng(0)
    sample_idx = _window_sample_indices(times, check_time, window, n_samples)
    zeros_counted = rng.binomial(shots, energy[sample_idx])
    measured_ratio = float((zeros_counted / shots).max() / energy[0])
    true_ratio = float(energy[sample_idx].max() / energy[0])
    return {
        "measured_ratio": measured_ratio,
        "true_ratio": true_ratio,
        "fades_safely": bool(measured_ratio < threshold),
        "total_shots_used": n_samples * shots,
    }
