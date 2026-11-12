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
from src.theory import landau_root  # noqa: E402

FIT_START = 2.0   # skip the start-up transient before fitting the decay


def step1_single_run(p: Params) -> None:
    """STEP 1: simulate one plasma wave on the quantum circuit and compare with the textbook formula."""
    print(f"\n=== STEP 1: one run, k*lambda_D = {p.k}, {p.n_qubits} qubits, {p.n_v} velocity points ===")
    quantum = field_energy(run_quantum(p))                          # quantum circuit (Trotter)
    theory = landau_root(p.k)                                        # textbook dispersion relation

    t_end = min(p.t_max, 0.8 * p.recurrence_time)
    print(f"  Recurrence time (fake revival) T_R = {p.recurrence_time:.1f}; fit window [{FIT_START}, {t_end:.1f}]")
    print(f"  Landau theory:      omega = {theory.real:.4f},  gamma = {theory.imag:.4f}")
    print(f"  Quantum circuit:    gamma = {fit_damping_rate(p.times, quantum, FIT_START, t_end):.4f}")
    print(f"  Saved {plots.plot_damping(p.times, quantum, theory.imag, p.k)}")


def step2_sweep_k(ks: np.ndarray, n_qubits: int) -> list:
    """STEP 2: repeat for several wavelengths. Shorter waves (larger k) should damp faster."""
    print("\n=== STEP 2: damping rate vs k*lambda_D ===")
    runs, fitted, analytic = [], [], []
    for k in ks:
        p = Params(k=k, n_qubits=n_qubits)
        energy = field_energy(run_quantum(p))
        runs.append((p, energy))
        fitted.append(fit_damping_rate(p.times, energy, FIT_START, min(p.t_max, 0.8 * p.recurrence_time)))
        analytic.append(landau_root(k).imag)
        print(f"  k = {k:.2f}: quantum gamma = {fitted[-1]:.4f}   theory gamma = {analytic[-1]:.4f}")
    print(f"  Saved {plots.plot_gamma_vs_k(ks, fitted, analytic)}")
    return runs


def step3_stability(runs: list, threshold: float = 0.1, window: float = 3.0) -> None:
    """STEP 3 (novelty): the controller's yes/no question, answered from measurement shots."""
    print(f"\n=== STEP 3: stability classifier (threshold: {threshold:.0%} energy left) ===")
    t_check = 8.0
    for p, energy in runs:
        r = classify_stability(p.times, energy, t_check, threshold, window)
        verdict = "fades on its own" if r["damped"] else "CONTROLLER MUST ACT"
        print(f"  k = {p.k:.2f}: measured {r['measured_ratio']:.3f} (true {r['true_ratio']:.3f}) "
              f"at t = {t_check} -> {verdict}  [{r['circuit_runs']} circuit runs]")

    # Heat map: remaining-energy fraction for every (k, response time).
    p0 = runs[0][0]
    keep = p0.times <= p0.t_max - window                             # envelope needs a full window ahead
    ratios = np.array([envelope(p.times, e, window)[keep] for p, e in runs])
    ks = np.array([p.k for p, _ in runs])
    # Blank out cells near the fake grid "revival", so artefacts aren't mistaken for physics.
    recurrence = np.array([[0.8 * p.recurrence_time - window] for p, _ in runs])
    ratios[p0.times[keep][None, :] > recurrence] = np.nan
    print(f"  Saved {plots.plot_stability_map(ks, p0.times[keep], ratios, threshold)}")


def step4_resources(n_values: list[int]) -> None:
    """STEP 4: how big are the circuits, and how does memory compare with classical?"""
    print("\n=== STEP 4: resource estimates ===")
    costs = circuit_costs(n_values)
    for c in costs:
        print(f"  n = {c['n_qubits']} qubits ({c['grid_points']} grid points): {c['pauli_terms']} Pauli terms, "
              f"{c['cx_per_step']} CNOTs/step, depth {c['depth_per_step']}/step")
    memory = memory_scaling(np.array([16, 32, 64, 128, 256, 512, 1024]))
    print("  3D3V reactor grid, N = 128 per dimension: "
          f"{memory['classical_values'][3]:.1e} numbers classically vs {memory['qubits'][3]:.0f} qubits")
    print(f"  Saved {plots.plot_resources(costs, memory)}")


def step5_real_units(gamma: float) -> None:
    """STEP 5: translate the normalised answer into seconds for real reactor conditions."""
    print("\n=== STEP 5: real-world units (tokamak core: 10 keV, 1e20 m^-3) ===")
    s = plasma_scales(temperature_ev=1e4, density_m3=1e20)
    print(f"  plasma frequency = {s['omega_p']:.2e} rad/s, Debye length = {s['lambda_D'] * 1e6:.0f} micrometres")
    print(f"  k*lambda_D = 0.5 means a wavelength of {2 * np.pi / 0.5 * s['lambda_D'] * 1e3:.2f} mm")
    print(f"  energy e-folding time 1/(2|gamma|) = {1 / (2 * abs(gamma) * s['omega_p']) * 1e12:.1f} ps")


def main() -> None:
    p = Params()                                         # defaults: k = 0.5, 5 qubits
    step1_single_run(p)
    runs = step2_sweep_k(np.round(np.linspace(0.3, 0.7, 9), 2), p.n_qubits)
    step3_stability(runs)
    step4_resources([3, 4, 5, 6, 7])
    step5_real_units(landau_root(p.k).imag)
    print("\nDone. Figures are in figures/.")


if __name__ == "__main__":
    main()
