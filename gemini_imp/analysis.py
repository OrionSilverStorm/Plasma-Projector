"""
Section 4: Analysing Data (Measuring How Fast the Wave Fades).

For the full explanation of exponential peak fitting, log-linear regression,
and the discrete-grid fake revival cutoff, see README.md (Section 4).
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
