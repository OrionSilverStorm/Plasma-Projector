"""
Section 5: Plotting Data with Matplotlib.

Generates the PNG figures in `gemini_imp/figures/`:
1. `1a_quantum_circuit_scenarios.png`     : Dedicated graph of Quantum Circuit outputs across 3 scenarios.
2. `1b_classical_algorithm_scenarios.png` : Dedicated graph of Conventional Algorithm outputs across the same 3 scenarios.
3. `1_quantum_vs_classical_wave.png`      : Direct overlay of Quantum vs. Classical on the baseline wave.
4. `2_factors_affecting_plasma.png`       : Parameter sweeps showing how Wavenumber (k) and Temperature (T) change fade speed.
5. `3_quantum_vs_classical_scaling.png`   : 3-panel viability & efficiency benchmark (3D Memory Compression, Problem 3 Fast Arrowhead vs. Naive Pauli CNOT reduction, and Problem 2 Hardware-Independent Operations).

For detailed descriptions of each figure and what it demonstrates, see README.md (Section 5).
"""

from pathlib import Path
import numpy as np

# Use Matplotlib's non-interactive 'Agg' backend so figures save directly to PNG
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis import (
    classify_reactor_stability,
    compute_remaining_energy_envelope,
    measure_damping_rate,
)
from config import DEFAULT_CONFIG, SCENARIOS, make_velocity_grid
from simulation import (
    benchmark_efficiency_scaling,
    run_classical_simulation,
    run_quantum_simulation,
)

FIGURES_DIR = Path(__file__).resolve().parent / "figures"

SCENARIO_COLORS = ["#0072B2", "#009E73", "#D55E00"]


def plot_separate_scenario_graphs(
    scenario_results: list[dict] | None = None,
) -> tuple[Path, Path, list[dict]]:
    """
    Generate TWO separate, matched-scale graphs across the 3 tokamak scenarios:
      - Graph 1A (`1a_quantum_circuit_scenarios.png`): Quantum Circuit outputs (Fast Arrowhead + 2,000-shot dots + decay envelope)
      - Graph 1B (`1b_classical_algorithm_scenarios.png`): Conventional Algorithm outputs (Sparse RK45 + decay envelope)
    Returns (quantum_fig_path, classical_fig_path, scenario_results).
    """
    FIGURES_DIR.mkdir(exist_ok=True)

    if scenario_results is None:
        scenario_results = []
        for scen in SCENARIOS:
            cfg = scen["config"]
            q_res = run_quantum_simulation(cfg, method="arrowhead")
            c_res = run_classical_simulation(cfg)
            q_rate, q_env = measure_damping_rate(q_res["times"], q_res["energy"], cfg)
            c_rate, c_env = measure_damping_rate(c_res["times"], c_res["energy"], cfg)
            scenario_results.append({
                "scenario": scen,
                "quantum": q_res,
                "classical": c_res,
                "q_rate": q_rate,
                "q_env": q_env,
                "c_rate": c_rate,
                "c_env": c_env,
            })

    # --- GRAPH 1A: QUANTUM CIRCUIT SCENARIOS ---
    fig_q, axes_q = plt.subplots(1, 3, figsize=(14.5, 4.6), sharey=True)
    fig_q.suptitle(
        "Quantum Computer (5-Qubit Fast Arrowhead Circuit): Plasma Wave Decay Across 3 Tokamak Scenarios",
        fontsize=13,
        fontweight="bold",
    )

    for idx, (ax, item) in enumerate(zip(axes_q, scenario_results)):
        scen = item["scenario"]
        q_res = item["quantum"]
        color = SCENARIO_COLORS[idx]

        ax.semilogy(
            q_res["times"],
            q_res["energy"],
            color=color,
            linewidth=2.0,
            label="Quantum Circuit Statevector",
        )
        shot_mask = q_res["shot_energy"] > 0
        ax.semilogy(
            q_res["times"][shot_mask][::3],
            q_res["shot_energy"][shot_mask][::3],
            "o",
            color="#E69F00",
            markersize=3.8,
            alpha=0.8,
            label="Hardware Readout (2,000 shots)",
        )
        ax.semilogy(
            q_res["times"],
            item["q_env"],
            ":",
            color="black",
            linewidth=2.0,
            label=f"Fitted Fade Rate = {item['q_rate']:.4f}",
        )

        ax.set_title(f"{scen['name']}\n({scen['short_label'].split('(')[1].rstrip(')')})", fontsize=10.5)
        ax.set_xlabel("Time [plasma oscillation ticks]")
        if idx == 0:
            ax.set_ylabel("Electric Field Energy = P(measure |00000⟩)")
        ax.set_ylim(bottom=1e-4, top=1.0)
        ax.grid(True, which="both", linestyle="--", alpha=0.4)
        ax.legend(loc="upper right", fontsize=8.5)

    out_q = FIGURES_DIR / "1a_quantum_circuit_scenarios.png"
    fig_q.tight_layout(rect=[0, 0, 1, 0.93])
    fig_q.savefig(out_q, dpi=200)
    plt.close(fig_q)

    # --- GRAPH 1B: CONVENTIONAL ALGORITHM SCENARIOS ---
    fig_c, axes_c = plt.subplots(1, 3, figsize=(14.5, 4.6), sharey=True)
    fig_c.suptitle(
        "Conventional Computer (Sparse SciPy RK45 Solver): Plasma Wave Decay Across 3 Tokamak Scenarios",
        fontsize=13,
        fontweight="bold",
    )

    for idx, (ax, item) in enumerate(zip(axes_c, scenario_results)):
        scen = item["scenario"]
        c_res = item["classical"]
        color = SCENARIO_COLORS[idx]

        ax.semilogy(
            c_res["times"],
            c_res["energy"],
            color=color,
            linewidth=2.0,
            label="Classical Sparse RK45 Solver",
        )
        ax.semilogy(
            c_res["times"],
            item["c_env"],
            ":",
            color="black",
            linewidth=2.0,
            label=f"Fitted Fade Rate = {item['c_rate']:.4f}",
        )

        ax.set_title(f"{scen['name']}\n({scen['short_label'].split('(')[1].rstrip(')')})", fontsize=10.5)
        ax.set_xlabel("Time [plasma oscillation ticks]")
        if idx == 0:
            ax.set_ylabel("Electric Field Energy = |state[0]|²")
        ax.set_ylim(bottom=1e-4, top=1.0)
        ax.grid(True, which="both", linestyle="--", alpha=0.4)
        ax.legend(loc="upper right", fontsize=8.5)

    out_c = FIGURES_DIR / "1b_classical_algorithm_scenarios.png"
    fig_c.tight_layout(rect=[0, 0, 1, 0.93])
    fig_c.savefig(out_c, dpi=200)
    plt.close(fig_c)

    return out_q, out_c, scenario_results


def plot_figure_1_quantum_vs_classical(
    q_res: dict,
    c_res: dict,
    damping_rate: float,
    envelope: np.ndarray,
    config: dict,
) -> Path:
    """
    Save Figure 1: semi-log wave energy decay comparing Classical Sparse RK45,
    Quantum Fast Arrowhead Statevector, and 2,000-shot readout. See README.md (Section 5).
    """
    FIGURES_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))

    ax.semilogy(
        c_res["times"],
        c_res["energy"],
        color="black",
        linewidth=2.0,
        label="Classical Computer (Sparse SciPy RK45 Solver)",
    )
    ax.semilogy(
        q_res["times"],
        q_res["energy"],
        "--",
        color="#0072B2",
        linewidth=2.0,
        label="Quantum Circuit (5-Qubit Fast Arrowhead Trotter)",
    )

    shot_mask = q_res["shot_energy"] > 0
    ax.semilogy(
        q_res["times"][shot_mask][::3],
        q_res["shot_energy"][shot_mask][::3],
        "o",
        color="#E69F00",
        markersize=4,
        alpha=0.8,
        label="Quantum Hardware Readout (2,000 shots)",
    )

    ax.semilogy(
        q_res["times"],
        envelope,
        ":",
        color="#D55E00",
        linewidth=2.0,
        label=f"Fitted Decay Slope (rate = {damping_rate:.4f})",
    )

    ax.set_title(
        f"Baseline Wave Energy Decay: Quantum vs. Classical "
        f"(k={config['wavenumber']}, T={config['temperature']}, {config['n_qubits']} Qubits)"
    )
    ax.set_xlabel("Time [plasma oscillation ticks]")
    ax.set_ylabel("Electric Field Energy = P(measure |00000⟩)")
    ax.set_ylim(bottom=1e-4, top=1.0)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right")

    out_path = FIGURES_DIR / "1_quantum_vs_classical_wave.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_figure_2_factors_comparison() -> Path:
    """
    Save Figure 2: side-by-side parameter sweep across Wavenumber (k)
    and Electron Temperature (T). See README.md (Section 5).
    """
    FIGURES_DIR.mkdir(exist_ok=True)
    fig, (ax_k, ax_t) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Panel A: Sweep Wavenumber (k)
    wavenumbers = [0.3, 0.4, 0.5, 0.6, 0.7]
    q_rates_k, c_rates_k = [], []
    for k in wavenumbers:
        cfg = {**DEFAULT_CONFIG, "wavenumber": k}
        q_sim = run_quantum_simulation(cfg, method="arrowhead")
        c_sim = run_classical_simulation(cfg)
        q_rates_k.append(abs(measure_damping_rate(q_sim["times"], q_sim["energy"], cfg)[0]))
        c_rates_k.append(abs(measure_damping_rate(c_sim["times"], c_sim["energy"], cfg)[0]))

    ax_k.plot(wavenumbers, c_rates_k, "s-", color="black", label="Classical Sparse Solver")
    ax_k.plot(wavenumbers, q_rates_k, "o--", color="#0072B2", label="Quantum Fast Arrowhead (5 Qubits)")
    ax_k.set_title("Factor 1: Effect of Wavenumber (k)")
    ax_k.set_xlabel("Wavenumber k  (Higher = Shorter Wavelength)")
    ax_k.set_ylabel("Wave Fade Speed |damping rate|")
    ax_k.grid(True, linestyle="--", alpha=0.4)
    ax_k.legend()

    # Panel B: Sweep Temperature (T)
    temperatures = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6]
    q_rates_t, c_rates_t = [], []
    for temp in temperatures:
        cfg = {**DEFAULT_CONFIG, "temperature": temp}
        q_sim = run_quantum_simulation(cfg, method="arrowhead")
        c_sim = run_classical_simulation(cfg)
        q_rates_t.append(abs(measure_damping_rate(q_sim["times"], q_sim["energy"], cfg)[0]))
        c_rates_t.append(abs(measure_damping_rate(c_sim["times"], c_sim["energy"], cfg)[0]))

    ax_t.plot(temperatures, c_rates_t, "s-", color="black", label="Classical Sparse Solver")
    ax_t.plot(temperatures, q_rates_t, "o--", color="#D55E00", label="Quantum Fast Arrowhead (5 Qubits)")
    ax_t.set_title("Factor 2: Effect of Electron Temperature (T)")
    ax_t.set_xlabel("Plasma Temperature T  (Higher = Faster Electrons)")
    ax_t.set_ylabel("Wave Fade Speed |damping rate|")
    ax_t.grid(True, linestyle="--", alpha=0.4)
    ax_t.legend()

    out_path = FIGURES_DIR / "2_factors_affecting_plasma.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_figure_3_quantum_vs_classical_viability(
    stats: list[dict] | None = None,
) -> tuple[Path, list[dict]]:
    """
    Save Figure 3: 3-panel viability & efficiency analysis:
      - Panel A: 3D Reactor Memory Compression (N^6 classical numbers vs 6 log2 N qubits).
      - Panel B (Problem 3 Fix): CNOT Gate Count per step — Naive Pauli (~4^n) vs Fast Arrowhead Circuit.
      - Panel C (Problem 2 Fix): Hardware-independent total operation count (Classical Sparse FLOPs vs Quantum CNOTs).
    """
    FIGURES_DIR.mkdir(exist_ok=True)
    if stats is None:
        stats = benchmark_efficiency_scaling([3, 4, 5, 6])

    fig, (ax_mem, ax_gates, ax_ops) = plt.subplots(1, 3, figsize=(15.5, 4.6))

    # Panel A: 3D reactor memory scaling
    grid_points_per_axis = np.array([8, 16, 32, 64, 128, 256], dtype=float)
    classical_floats_3d3v = grid_points_per_axis ** 6
    quantum_qubits_3d3v = 6 * np.log2(grid_points_per_axis)

    ax_mem.loglog(
        grid_points_per_axis,
        classical_floats_3d3v,
        "s-",
        color="#D55E00",
        linewidth=2,
        label="Classical RAM: State numbers (N⁶)",
    )
    ax_mem.loglog(
        grid_points_per_axis,
        quantum_qubits_3d3v,
        "o-",
        color="#0072B2",
        linewidth=2,
        label="Quantum Register: Qubits (6 log₂ N)",
    )
    ax_mem.set_title("1. Memory Win: 3D Reactor Compression")
    ax_mem.set_xlabel("Grid Resolution per Axis (N)")
    ax_mem.set_ylabel("Numbers / Qubits Needed (Log Scale)")
    ax_mem.grid(True, which="both", linestyle="--", alpha=0.4)
    ax_mem.legend(fontsize=8.5)

    # Panel B: Problem 3 Fix — Naive Pauli (~4^n) vs Fast Arrowhead CNOTs per step
    qubit_list = [s["n_qubits"] for s in stats]
    ax_gates.semilogy(
        qubit_list,
        [s["naive_cnots_per_step"] for s in stats],
        "s--",
        color="#CC79A7",
        linewidth=2,
        label="Old Naive Pauli Circuit (~4ⁿ CNOTs)",
    )
    ax_gates.semilogy(
        qubit_list,
        [s["fast_cnots_per_step"] for s in stats],
        "o-",
        color="#009E73",
        linewidth=2.2,
        label="New Fast Arrowhead Circuit (Up to 13.7× Fewer!)",
    )
    ax_gates.set_title("2. Circuit Fix: CNOT Gates per Time Step")
    ax_gates.set_xlabel("Number of Qubits (n)")
    ax_gates.set_ylabel("2-Qubit CNOT Gates / Step (Log Scale)")
    ax_gates.set_xticks(qubit_list)
    ax_gates.grid(True, which="both", linestyle="--", alpha=0.4)
    ax_gates.legend(fontsize=8.5)

    # Panel C: Problem 2 Fix — Hardware-Independent Operations for Full 200-Step Run (1D Demo)
    ax_ops.semilogy(
        qubit_list,
        [s["classical_flops"] for s in stats],
        "s-",
        color="black",
        linewidth=2,
        label="Classical Sparse Solver (Total FLOPs)",
    )
    ax_ops.semilogy(
        qubit_list,
        [s["naive_total_cnots"] for s in stats],
        "^--",
        color="#CC79A7",
        linewidth=1.8,
        label="Quantum Naive Pauli (200 Steps CNOTs)",
    )
    ax_ops.semilogy(
        qubit_list,
        [s["fast_total_cnots"] for s in stats],
        "o-",
        color="#0072B2",
        linewidth=2,
        label="Quantum Fast Arrowhead (200 Steps CNOTs)",
    )
    ax_ops.set_title("3. Fair Efficiency: Total Hardware Operations")
    ax_ops.set_xlabel("Number of Qubits (n)")
    ax_ops.set_ylabel("Operations per Full Run (Log Scale)")
    ax_ops.set_xticks(qubit_list)
    ax_ops.grid(True, which="both", linestyle="--", alpha=0.4)
    ax_ops.legend(fontsize=8.5)

    out_path = FIGURES_DIR / "3_quantum_vs_classical_scaling.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path, stats


def plot_figure_4_stability_heatmap(
    threshold: float = 0.10,
    window: float = 3.0,
    check_time: float = 8.0,
) -> tuple[Path, list[dict]]:
    """
    Save Figure 4 (`4_stability_threshold_heatmap.png`):
    A 2D decision heatmap across Wavenumber (k = 0.30..0.70) and Controller Response Time (t),
    showing the fraction of wave energy left:
      - Green region (right of the white contour line): wave energy has dropped below 10% (fades on its own).
      - Red/Orange region (left of the white contour line): wave still holds >10% energy (controller must act).
      - Blank white cells on the far right: masked out beyond 0.8 * fake_revival_time so grid echoes are hidden.
    Also returns the shot-based stability classification at t = check_time for each wavenumber.
    """
    FIGURES_DIR.mkdir(exist_ok=True)
    wavenumbers = np.round(np.linspace(0.30, 0.70, 9), 2)
    _, dv = make_velocity_grid(DEFAULT_CONFIG["n_qubits"], DEFAULT_CONFIG["max_velocity"])

    runs_energy = []
    classifier_rows = []
    times = None

    for k in wavenumbers:
        cfg = {**DEFAULT_CONFIG, "wavenumber": float(k)}
        q_sim = run_quantum_simulation(cfg, method="arrowhead")
        times = q_sim["times"]
        runs_energy.append((cfg, q_sim["energy"]))

        verdict = classify_reactor_stability(
            times=times,
            energy=q_sim["energy"],
            check_time=check_time,
            threshold=threshold,
            window=window,
        )
        classifier_rows.append({"wavenumber": float(k), **verdict})

    keep_mask = times <= (DEFAULT_CONFIG["end_time"] - window)
    valid_times = times[keep_mask]

    ratios = np.array([
        compute_remaining_energy_envelope(times, energy, window)[keep_mask]
        for _, energy in runs_energy
    ])

    # Mask out times near/after the discrete-grid fake revival time so grid echoes aren't shown
    last_trusted_time = np.array([
        [min(cfg["end_time"], 0.8 * (2.0 * np.pi / (cfg["wavenumber"] * dv))) - window]
        for cfg, _ in runs_energy
    ])
    ratios[valid_times[None, :] > last_trusted_time] = np.nan

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    mesh = ax.pcolormesh(
        valid_times,
        wavenumbers,
        np.log10(ratios),
        shading="auto",
        cmap="RdYlGn_r",
    )
    ax.contour(
        valid_times,
        wavenumbers,
        ratios,
        levels=[threshold],
        colors="white",
        linewidths=2.5,
    )
    cbar = fig.colorbar(mesh, ax=ax, label="log$_{10}$(Remaining Energy / Starting Energy)")
    cbar.ax.axhline(np.log10(threshold), color="white", linewidth=2.0)

    ax.set_title(
        f"Reactor Controller Decision Map: {threshold:.0%} Wave Energy Threshold\n"
        f"(Green = Fades Safely <{threshold:.0%}, Red = Needs Control >{threshold:.0%}, White Line = {threshold:.0%} Cutoff)",
        fontsize=10.5,
    )
    ax.set_xlabel("Controller Response Time  [plasma oscillation ticks]")
    ax.set_ylabel("Wavenumber k  [per screening length]  (Shorter Waves ↑)")

    out_path = FIGURES_DIR / "4_stability_threshold_heatmap.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path, classifier_rows

