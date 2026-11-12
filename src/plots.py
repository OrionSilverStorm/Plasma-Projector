"""
plots.py: every figure for the slides. Each function draws one figure and saves it as a PNG.
Keeping all plotting here keeps the physics modules free of matplotlib clutter.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")            # draw straight to files (no pop-up windows)
import matplotlib.pyplot as plt  # noqa: E402  (must come after choosing the backend)
import numpy as np               # noqa: E402

FIGURES = Path(__file__).resolve().parent.parent / "figures"


def _save(fig, name: str) -> Path:
    """Save a figure into figures/ and close it to free memory."""
    FIGURES.mkdir(exist_ok=True)
    path = FIGURES / name
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_damping(times, quantum, gamma_analytic, k) -> Path:
    """Figure 1: |E(t)|^2 from the quantum circuit vs the textbook decay rate."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(times, quantum, color="C0", lw=1.5, label="Quantum circuit (Trotter)")
    envelope = quantum.max() * np.exp(2 * gamma_analytic * times)   # energy ~ exp(2 gamma t)
    ax.semilogy(times, envelope, ":", color="C3", label=f"Landau theory, $\\gamma$={gamma_analytic:.4f}")
    ax.set(xlabel="time  [1/$\\omega_p$]", ylabel="field energy $|E|^2$ = P(|0…0⟩)",
           title=f"Landau damping on a quantum circuit (k$\\lambda_D$ = {k})")
    ax.legend()
    return _save(fig, "1_damping_curve.png")


def plot_gamma_vs_k(ks, gamma_quantum, gamma_analytic) -> Path:
    """Figure 2: damping rate measured from the circuit vs the analytic dispersion relation."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(ks, -np.array(gamma_analytic), "-", color="0.4", label="Analytic (dispersion relation)")
    ax.plot(ks, -np.array(gamma_quantum), "o", color="C0", label="Quantum circuit fit")
    ax.set(xlabel="k$\\lambda_D$ (shorter waves →)", ylabel="damping rate $-\\gamma$  [$\\omega_p$]",
           title="Shorter waves damp faster")
    ax.legend()
    return _save(fig, "2_gamma_vs_k.png")


def plot_resources(costs: list[dict], memory: dict) -> Path:
    """Figure 3: (left) memory, classical vs quantum; (right) measured gate cost of our circuit."""
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))

    left.loglog(memory["N"], memory["classical_values"], "o-", color="C3", label="Classical: numbers stored")
    left.loglog(memory["N"], memory["qubits"], "s-", color="C0", label="Quantum: qubits needed")
    left.set(xlabel="grid points per dimension N", ylabel="count",
             title="3D3V reactor model: memory needed")
    left.legend()

    n = [c["n_qubits"] for c in costs]
    right.semilogy(n, [c["pauli_terms"] for c in costs], "o-", label="Pauli terms in H")
    right.semilogy(n, [c["cx_per_step"] for c in costs], "s-", label="CNOTs per Trotter step")
    right.semilogy(n, [c["depth_per_step"] for c in costs], "^-", label="Circuit depth per step")
    right.set(xlabel="qubits n", ylabel="count",
              title="Generic circuit cost (grows ~4ⁿ: needs structure)")
    right.legend()
    return _save(fig, "3_resources.png")


def plot_stability_map(ks, times, energy_ratio, threshold) -> Path:
    """
    Figure 4: the controller's decision map. Colour = fraction of wave energy left.
    The white line is the threshold: below/right of it the disturbance fades on its own.
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    mesh = ax.pcolormesh(times, ks, np.log10(energy_ratio), shading="auto", cmap="RdYlGn_r")
    ax.contour(times, ks, energy_ratio, levels=[threshold], colors="white", linewidths=2)
    fig.colorbar(mesh, ax=ax, label="log$_{10}$(energy left / start)")
    ax.set(xlabel="controller response time  [1/$\\omega_p$]", ylabel="k$\\lambda_D$",
           title=f"Fades on its own (green) vs needs control (red), threshold {threshold:.0%}")
    return _save(fig, "4_stability_map.png")
