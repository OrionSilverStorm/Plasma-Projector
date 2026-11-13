"""
Section 5: Plotting Data with Matplotlib.

Generates the 3 PNG figures in `asad_imp/figures/`.
For detailed descriptions of each figure and what it demonstrates, see README.md (Section 5).
"""

from pathlib import Path
import numpy as np

# Use Matplotlib's non-interactive 'Agg' backend so figures save directly to PNG
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qiskit import transpile

from analysis import measure_damping_rate
from config import DEFAULT_CONFIG
from hamiltonian import build_hamiltonian_matrix
from simulation import build_qiskit_step_circuit, run_classical_simulation, run_quantum_simulation

FIGURES_DIR = Path(__file__).resolve().parent / "figures"


def plot_figure_1_quantum_vs_classical(q_res: dict, c_res: dict, damping_rate: float,
                                       envelope: np.ndarray, config: dict) -> Path:
    """
    Save Figure 1: semi-log wave energy decay comparing Classical RK45,
    Quantum Trotter Statevector, and 2,000-shot readout. See README.md (Section 5).
    """
    FIGURES_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))

    ax.semilogy(c_res["times"], c_res["energy"], color="black", linewidth=2.0,
                label="Classical Computer (SciPy RK45 Solver)")
    ax.semilogy(q_res["times"], q_res["energy"], "--", color="#0072B2", linewidth=2.0,
                label="Quantum Circuit (Qiskit 5-Qubit Trotter)")

    shot_mask = q_res["shot_energy"] > 0
    ax.semilogy(q_res["times"][shot_mask][::3], q_res["shot_energy"][shot_mask][::3],
                "o", color="#E69F00", markersize=4, alpha=0.8,
                label="Quantum Hardware Readout (2,000 shots)")

    ax.semilogy(q_res["times"], envelope, ":", color="#D55E00", linewidth=2.0,
                label=f"Fitted Decay Slope (rate = {damping_rate:.4f})")

    ax.set_title(
        f"Plasma Wave Energy Decay: Quantum vs. Classical "
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
        q_sim = run_quantum_simulation(cfg)
        c_sim = run_classical_simulation(cfg)
        q_rates_k.append(abs(measure_damping_rate(q_sim["times"], q_sim["energy"], cfg)[0]))
        c_rates_k.append(abs(measure_damping_rate(c_sim["times"], c_sim["energy"], cfg)[0]))

    ax_k.plot(wavenumbers, c_rates_k, "s-", color="black", label="Classical Solver")
    ax_k.plot(wavenumbers, q_rates_k, "o--", color="#0072B2", label="Quantum Circuit (5 Qubits)")
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
        q_sim = run_quantum_simulation(cfg)
        c_sim = run_classical_simulation(cfg)
        q_rates_t.append(abs(measure_damping_rate(q_sim["times"], q_sim["energy"], cfg)[0]))
        c_rates_t.append(abs(measure_damping_rate(c_sim["times"], c_sim["energy"], cfg)[0]))

    ax_t.plot(temperatures, c_rates_t, "s-", color="black", label="Classical Solver")
    ax_t.plot(temperatures, q_rates_t, "o--", color="#D55E00", label="Quantum Circuit (5 Qubits)")
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


def plot_figure_3_quantum_vs_classical_viability() -> tuple[Path, list[dict]]:
    """
    Save Figure 3: 3D reactor memory compression (N^6 vs 6 log2 N) and
    Qiskit CNOT gate-count scaling (~4^n). See README.md (Section 5).
    """
    FIGURES_DIR.mkdir(exist_ok=True)
    fig, (ax_mem, ax_gates) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Left Panel: 3D reactor memory scaling
    grid_points_per_axis = np.array([8, 16, 32, 64, 128, 256], dtype=float)
    classical_floats_3d3v = grid_points_per_axis ** 6
    quantum_qubits_3d3v = 6 * np.log2(grid_points_per_axis)

    ax_mem.loglog(grid_points_per_axis, classical_floats_3d3v, "s-", color="#D55E00", linewidth=2,
                  label="Classical RAM: State numbers (N⁶)")
    ax_mem.loglog(grid_points_per_axis, quantum_qubits_3d3v, "o-", color="#0072B2", linewidth=2,
                  label="Quantum Register: Qubits needed (6 log₂ N)")
    ax_mem.set_title("Why Quantum? 3D Reactor Memory Compression")
    ax_mem.set_xlabel("Grid Resolution per Axis (N)")
    ax_mem.set_ylabel("Count (Log Scale)")
    ax_mem.grid(True, which="both", linestyle="--", alpha=0.4)
    ax_mem.legend()

    # Right Panel: Transpiled CNOT gate count and circuit depth across n = 3..6 qubits
    qubit_list = [3, 4, 5, 6]
    stats = []
    dt = DEFAULT_CONFIG["end_time"] / DEFAULT_CONFIG["n_steps"]

    for n_q in qubit_list:
        cfg = {**DEFAULT_CONFIG, "n_qubits": n_q}
        H = build_hamiltonian_matrix(cfg)
        step_qc = build_qiskit_step_circuit(H, dt, n_q)
        compiled_qc = transpile(step_qc, basis_gates=["cx", "rz", "sx", "x"], optimization_level=1)
        cnot_count = compiled_qc.count_ops().get("cx", 0)
        stats.append({
            "n_qubits": n_q,
            "velocity_buckets": (2 ** n_q) - 1,
            "cnot_gates_per_step": cnot_count,
            "circuit_depth": compiled_qc.depth(),
        })

    ax_gates.semilogy([s["n_qubits"] for s in stats],
                      [s["cnot_gates_per_step"] for s in stats],
                      "o-", color="#CC79A7", linewidth=2, label="2-Qubit CNOT Gates per Step")
    ax_gates.semilogy([s["n_qubits"] for s in stats],
                      [s["circuit_depth"] for s in stats],
                      "^-", color="#009E73", linewidth=2, label="Circuit Depth per Step")
    ax_gates.set_title("Current Limit: Gate Cost per Time Step (~4ⁿ)")
    ax_gates.set_xlabel("Number of Qubits (n)")
    ax_gates.set_ylabel("Gate / Depth Count (Log Scale)")
    ax_gates.set_xticks(qubit_list)
    ax_gates.grid(True, which="both", linestyle="--", alpha=0.4)
    ax_gates.legend()

    out_path = FIGURES_DIR / "3_quantum_vs_classical_scaling.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path, stats
