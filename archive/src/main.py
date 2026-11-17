"""
main.py: the full demo, step by step. Run it with either:
    python -m src.main             (from the project folder)
    VS Code "Run Python File"      (with this file open)

Each STEP prints its results and saves a figure into figures/ for the slides.
"""
import sys
from pathlib import Path

# Lets VS Code's "Run Python File" find the `src` package (that mode doesn't start in the project folder).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402

from src import plots  # noqa: E402
from src.config import Params, plasma_scales  # noqa: E402
from src.hamiltonian import field_energy  # noqa: E402
from src.resources import circuit_costs, memory_scaling  # noqa: E402
from src.simulate import classify_stability, envelope, fit_damping_rate, run_quantum  # noqa: E402
from src.theory import landau_prediction  # noqa: E402

FIT_START = 2.0   # skip the start-up wobble before fitting the decay


def fit_end(settings: Params) -> float:
    """End the decay fit safely before the fake revival (or at the end of the run, if that's sooner)."""
    return min(settings.end_time, 0.8 * settings.fake_revival_time)


def step1_single_run(settings: Params) -> None:
    """STEP 1: simulate one plasma wave on the quantum circuit and compare with the textbook formula."""
    print(f"\n=== STEP 1: one run, wavenumber = {settings.wavenumber}, {settings.n_qubits} qubits, "
          f"{settings.n_velocities} velocity points ===")
    quantum_energy = field_energy(run_quantum(settings))            # quantum circuit (Trotter)
    theory = landau_prediction(settings.wavenumber)                  # textbook dispersion relation

    print(f"  Fake revival time = {settings.fake_revival_time:.1f}; fit window [{FIT_START}, {fit_end(settings):.1f}]")
    print(f"  Landau theory:      oscillation rate = {theory.real:.4f},  damping rate = {theory.imag:.4f}")
    print(f"  Quantum circuit:    damping rate = "
          f"{fit_damping_rate(settings.times, quantum_energy, FIT_START, fit_end(settings)):.4f}")
    print(f"  Saved {plots.plot_damping(settings.times, quantum_energy, theory.imag, settings.wavenumber)}")


def step2_sweep_wavenumber(wavenumbers: np.ndarray, n_qubits: int) -> list:
    """STEP 2: repeat for several wavelengths. Shorter waves (larger wavenumber) should damp faster."""
    print("\n=== STEP 2: damping rate vs wavenumber ===")
    runs, quantum_rates, theory_rates = [], [], []
    for wavenumber in wavenumbers:
        settings = Params(wavenumber=wavenumber, n_qubits=n_qubits)
        energy = field_energy(run_quantum(settings))
        runs.append((settings, energy))
        quantum_rates.append(fit_damping_rate(settings.times, energy, FIT_START, fit_end(settings)))
        theory_rates.append(landau_prediction(wavenumber).imag)
        print(f"  wavenumber = {wavenumber:.2f}: quantum damping rate = {quantum_rates[-1]:.4f}   "
              f"theory damping rate = {theory_rates[-1]:.4f}")
    print(f"  Saved {plots.plot_damping_vs_wavenumber(wavenumbers, quantum_rates, theory_rates)}")
    return runs


def step3_stability(runs: list, threshold: float = 0.1, window: float = 3.0) -> None:
    """STEP 3 (novelty): the controller's yes/no question, answered from measurement shots."""
    print(f"\n=== STEP 3: stability classifier (threshold: {threshold:.0%} energy left) ===")
    check_time = 8.0
    for settings, energy in runs:
        result = classify_stability(settings.times, energy, check_time, threshold, window)
        verdict = "fades on its own" if result["damped"] else "CONTROLLER MUST ACT"
        print(f"  wavenumber = {settings.wavenumber:.2f}: measured {result['measured_ratio']:.3f} "
              f"(true {result['true_ratio']:.3f}) at t = {check_time} -> {verdict}  "
              f"[{result['circuit_runs']} circuit runs]")

    # Heat map: remaining-energy fraction for every (wavenumber, response time).
    times = runs[0][0].times                                         # every run shares the same time grid
    keep = times <= runs[0][0].end_time - window                     # envelope needs a full window ahead
    ratios = np.array([envelope(settings.times, energy, window)[keep] for settings, energy in runs])
    wavenumbers = np.array([settings.wavenumber for settings, _ in runs])
    # Blank out cells near the fake grid revival, so artefacts aren't mistaken for physics.
    last_trusted_time = np.array([[fit_end(settings) - window] for settings, _ in runs])
    ratios[times[keep][None, :] > last_trusted_time] = np.nan
    print(f"  Saved {plots.plot_stability_map(wavenumbers, times[keep], ratios, threshold)}")


def step4_resources(qubit_counts: list[int]) -> None:
    """STEP 4: how big are the circuits, and how does memory compare with classical?"""
    print("\n=== STEP 4: resource estimates ===")
    costs = circuit_costs(qubit_counts)
    for c in costs:
        print(f"  {c['n_qubits']} qubits ({c['grid_points']} grid points): {c['pauli_terms']} Pauli terms, "
              f"{c['cnots_per_step']} CNOTs/step, depth {c['depth_per_step']}/step")
    memory = memory_scaling(np.array([16, 32, 64, 128, 256, 512, 1024]))
    print("  3D3V reactor grid, 128 points per axis: "
          f"{memory['classical_values'][3]:.1e} numbers classically vs {memory['qubits'][3]:.0f} qubits")
    print(f"  Saved {plots.plot_resources(costs, memory)}")


def step5_real_units(damping_rate: float, wavenumber: float) -> None:
    """STEP 5: translate the normalised answer into seconds for real reactor conditions."""
    print("\n=== STEP 5: real-world units (tokamak core: 10 keV, 1e20 electrons per m^3) ===")
    scales = plasma_scales(temperature_ev=1e4, density_m3=1e20)
    wavelength_m = 2 * np.pi / wavenumber * scales["screening_length"]
    fade_time_s = 1 / (2 * abs(damping_rate) * scales["plasma_frequency"])   # time for energy to drop by a factor e
    print(f"  plasma frequency = {scales['plasma_frequency']:.2e} rad/s, "
          f"screening length = {scales['screening_length'] * 1e6:.0f} micrometres")
    print(f"  wavenumber = {wavenumber} means a wavelength of {wavelength_m * 1e3:.2f} mm")
    print(f"  energy fades by a factor e in {fade_time_s * 1e12:.1f} ps")


def main() -> None:
    settings = Params()                                  # defaults: wavenumber 0.5, 5 qubits
    step1_single_run(settings)
    runs = step2_sweep_wavenumber(np.round(np.linspace(0.3, 0.7, 9), 2), settings.n_qubits)
    step3_stability(runs)
    step4_resources([3, 4, 5, 6, 7])
    step5_real_units(landau_prediction(settings.wavenumber).imag, settings.wavenumber)
    print("\nDone. Figures are in figures/.")


if __name__ == "__main__":
    main()
