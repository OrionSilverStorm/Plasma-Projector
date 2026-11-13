"""
Plasma Wave Simulation: Quantum (Qiskit) vs. Classical Computer (Main Entry Point).

Author: Asad
How to run: python asad_imp/plasma_simulation.py

For the project overview, physics explanations, and a guided file-by-file
walkthrough of Sections 1-5, see README.md.
"""

import sys
from pathlib import Path

# Allow importing sibling section modules regardless of the current working directory
_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from analysis import measure_damping_rate  # noqa: E402
from config import DEFAULT_CONFIG  # noqa: E402
from plotting import (  # noqa: E402
    plot_figure_1_quantum_vs_classical,
    plot_figure_2_factors_comparison,
    plot_figure_3_quantum_vs_classical_viability,
)
from simulation import run_classical_simulation, run_quantum_simulation  # noqa: E402


def main() -> None:
    """Run all three benchmark steps, print summary metrics, and save figures. See README.md."""
    print("=" * 80)
    print("QUANTUM VS. CLASSICAL PLASMA SIMULATION")
    print("=" * 80)

    # 1. Baseline single-wave comparison (5 qubits, k = 0.5, T = 1.0)
    print("\n[1/3] Running single wave comparison (5 Qubits vs. Classical RK45 Solver)...")
    q_res = run_quantum_simulation(DEFAULT_CONFIG)
    c_res = run_classical_simulation(DEFAULT_CONFIG)

    q_rate, q_env = measure_damping_rate(q_res["times"], q_res["energy"], DEFAULT_CONFIG)
    c_rate, _ = measure_damping_rate(c_res["times"], c_res["energy"], DEFAULT_CONFIG)

    print(f"  -> Classical Solver Damping Rate : {c_rate:.4f}  (took {c_res['runtime_s']:.3f} s)")
    print(f"  -> Quantum Circuit Damping Rate  : {q_rate:.4f}  (took {q_res['runtime_s']:.3f} s)")
    fig1_path = plot_figure_1_quantum_vs_classical(q_res, c_res, q_rate, q_env, DEFAULT_CONFIG)
    print(f"  -> Saved Graph 1: {fig1_path}")

    # 2. Sweep physical factors (Wavenumber k and Temperature T)
    print("\n[2/3] Sweeping plasma factors (Wavenumber k & Electron Temperature T)...")
    fig2_path = plot_figure_2_factors_comparison()
    print(f"  -> Saved Graph 2: {fig2_path}")

    # 3. Evaluate Quantum vs. Classical scaling & circuit costs
    print("\n[3/3] Measuring Quantum Circuit gate scaling and 3D memory compression...")
    fig3_path, gate_stats = plot_figure_3_quantum_vs_classical_viability()
    for row in gate_stats:
        print(
            f"  -> {row['n_qubits']} qubits ({row['velocity_buckets']:2d} velocity buckets): "
            f"{row['cnot_gates_per_step']:4d} CNOT gates/step | depth {row['circuit_depth']:4d}"
        )
    print(f"  -> Saved Graph 3: {fig3_path}")
    print("\nAll simulations finished! Check `asad_imp/figures/` for your graphs.")


if __name__ == "__main__":
    main()
