"""
Plasma Wave Simulation: Quantum (Qiskit) vs. Classical Computer (Main Entry Point).

Author: Asad
How to run: python gemini_imp/plasma_simulation.py

Walks through five clear stages:
  [1/5] Separate Multi-Scenario Graphs (Quantum Circuit vs. Conventional Algorithm across 3 scenarios)
  [2/5] Baseline Direct Overlay (5-Qubit Fast Arrowhead Circuit vs. Sparse Classical RK45)
  [3/5] Parameter Sweeps (How Wavenumber k and Temperature T affect plasma wave fading)
  [4/5] 10% Wave Energy Threshold Heatmap (Reactor Controller Decision Map from Quantum Shots)
  [5/5] Efficiency & Viability Benchmark (Problem 2 FLOPs vs. QPU Time + Problem 3 Fast Arrowhead Fix)

For the plain-English project overview, physics guide, and graph-by-graph explanations, see README.md.
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
    plot_figure_4_stability_heatmap,
    plot_separate_scenario_graphs,
)
from simulation import run_classical_simulation, run_quantum_simulation  # noqa: E402


def main() -> None:
    """Run all benchmark stages, print beginner-friendly summary metrics, and save all 6 figures."""
    print("=" * 88)
    print("TOKAMAK PLASMA WAVE SIMULATION: QUANTUM CIRCUIT (QISKIT) VS. CONVENTIONAL COMPUTER")
    print("=" * 88)

    # 1. Separate Multi-Scenario Graphs (Quantum vs. Classical side by side across 3 scenarios)
    print("\n[1/5] Generating separate Quantum & Classical graphs across 3 Tokamak Scenarios...")
    fig1a_path, fig1b_path, scenario_results = plot_separate_scenario_graphs()
    for item in scenario_results:
        scen = item["scenario"]
        print(
            f"  -> {scen['short_label']:27s} | "
            f"Quantum Fade Rate: {item['q_rate']:.4f} | "
            f"Classical Fade Rate: {item['c_rate']:.4f}"
        )
    print(f"  -> Saved Quantum Scenarios Graph   : {fig1a_path}")
    print(f"  -> Saved Classical Scenarios Graph : {fig1b_path}")

    # 2. Baseline single-wave overlay (5 qubits, k = 0.5, T = 1.0)
    print("\n[2/5] Running baseline wave overlay (5-Qubit Fast Arrowhead vs. Classical Sparse RK45)...")
    q_res = run_quantum_simulation(DEFAULT_CONFIG, method="arrowhead")
    c_res = run_classical_simulation(DEFAULT_CONFIG)

    q_rate, q_env = measure_damping_rate(q_res["times"], q_res["energy"], DEFAULT_CONFIG)
    c_rate, _ = measure_damping_rate(c_res["times"], c_res["energy"], DEFAULT_CONFIG)

    print(
        f"  -> Classical Sparse Solver : Damping Rate = {c_rate:.4f} | "
        f"Work = {c_res['total_flops']:,} FLOPs ({c_res['rhs_evaluations']} evaluations)"
    )
    print(
        f"  -> Quantum Fast Arrowhead  : Damping Rate = {q_rate:.4f} | "
        f"Work = {q_res['cnots_per_step']} CNOTs/step ({q_res['total_circuit_cnots']:,} total CNOTs, "
        f"est. QPU 1-shot time = {q_res['estimated_qpu_single_shot_s']*1e3:.2f} ms)"
    )
    fig1_path = plot_figure_1_quantum_vs_classical(q_res, c_res, q_rate, q_env, DEFAULT_CONFIG)
    print(f"  -> Saved Baseline Overlay Graph    : {fig1_path}")

    # 3. Sweep physical factors (Wavenumber k and Temperature T)
    print("\n[3/5] Sweeping plasma factors (Wavenumber k & Electron Temperature T)...")
    fig2_path = plot_figure_2_factors_comparison()
    print(f"  -> Saved Factors Sweep Graph       : {fig2_path}")

    # 4. Generate 10% Wave Energy Threshold Heatmap (Reactor Controller Decision Map)
    print("\n[4/5] Building 10% Wave Energy Threshold Heatmap (Reactor Controller Decision Map)...")
    fig4_path, classifier_rows = plot_figure_4_stability_heatmap(threshold=0.10, window=3.0, check_time=8.0)
    for row in classifier_rows:
        status = "FADES ON ITS OWN (<10%)" if row["fades_safely"] else "NEEDS CONTROL (>10%)"
        print(
            f"  -> k = {row['wavenumber']:.2f} at t = 8.0: "
            f"measured {row['measured_ratio']:.3f} (true {row['true_ratio']:.3f}) -> {status} "
            f"[{row['total_shots_used']} shots]"
        )
    print(f"  -> Saved 10% Threshold Heatmap     : {fig4_path}")

    # 5. Evaluate Quantum vs. Classical scaling & circuit efficiency (Problem 2 & Problem 3 fixes)
    print("\n[5/5] Benchmarking Efficiency: Classical Sparse FLOPs vs. Naive Pauli vs. Fast Arrowhead...")
    fig3_path, gate_stats = plot_figure_3_quantum_vs_classical_viability()
    for row in gate_stats:
        print(
            f"  -> {row['n_qubits']} qubits ({row['velocity_buckets']:2d} velocities): "
            f"Naive Pauli = {row['naive_cnots_per_step']:4d} CNOTs/step | "
            f"Fast Arrowhead = {row['fast_cnots_per_step']:3d} CNOTs/step "
            f"({row['cnot_reduction_factor']:4.1f}x fewer!) | "
            f"Classical = {row['classical_flops']:,} FLOPs"
        )
    print(f"  -> Saved Scaling & Efficiency Graph: {fig3_path}")
    print("\nAll simulations finished! Check `gemini_imp/figures/` for your 6 graphs.")


if __name__ == "__main__":
    main()
