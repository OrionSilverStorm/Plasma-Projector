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
TIME_LABEL = "time  [plasma ticks]"                     # shared axis label (see config.py for the units)
WAVENUMBER_LABEL = "wavenumber  [per screening length]"


def _save(fig, name: str) -> Path:
    """Save a figure into figures/ and close it to free memory."""
    FIGURES.mkdir(exist_ok=True)
    path = FIGURES / name
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_damping(times, quantum_energy, theory_damping_rate, wavenumber) -> Path:
    """Figure 1: field energy from the quantum circuit vs the textbook fade rate."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(times, quantum_energy, color="C0", lw=1.5, label="Quantum circuit (Trotter)")
    theory_envelope = quantum_energy.max() * np.exp(2 * theory_damping_rate * times)   # energy ~ exp(2 * rate * t)
    ax.semilogy(times, theory_envelope, ":", color="C3",
                label=f"Landau theory, damping rate = {theory_damping_rate:.4f}")
    ax.set(xlabel=TIME_LABEL, ylabel="field energy = P(measure |0…0⟩)",
           title=f"Landau damping on a quantum circuit (wavenumber = {wavenumber})")
    ax.legend()
    return _save(fig, "1_damping_curve.png")


def plot_damping_vs_wavenumber(wavenumbers, quantum_rates, theory_rates) -> Path:
    """Figure 2: damping rate measured from the circuit vs the textbook dispersion relation."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(wavenumbers, -np.array(theory_rates), "-", color="0.4", label="Textbook (dispersion relation)")
    ax.plot(wavenumbers, -np.array(quantum_rates), "o", color="C0", label="Quantum circuit fit")
    ax.set(xlabel=f"{WAVENUMBER_LABEL}  (shorter waves →)", ylabel="how fast the wave fades  [per plasma tick]",
           title="Shorter waves damp faster")
    ax.legend()
    return _save(fig, "2_damping_vs_wavenumber.png")


def plot_resources(costs: list[dict], memory: dict) -> Path:
    """Figure 3: (left) memory, classical vs quantum; (right) measured gate cost of our circuit."""
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))

    left.loglog(memory["points_per_dim"], memory["classical_values"], "o-", color="C3", label="Classical: numbers stored")
    left.loglog(memory["points_per_dim"], memory["qubits"], "s-", color="C0", label="Quantum: qubits needed")
    left.set(xlabel="grid points per axis", ylabel="count",
             title="3D3V reactor model: memory needed")
    left.legend()

    qubit_counts = [c["n_qubits"] for c in costs]
    right.semilogy(qubit_counts, [c["pauli_terms"] for c in costs], "o-", label="Pauli terms in hamiltonian")
    right.semilogy(qubit_counts, [c["cnots_per_step"] for c in costs], "s-", label="CNOTs per Trotter step")
    right.semilogy(qubit_counts, [c["depth_per_step"] for c in costs], "^-", label="Circuit depth per step")
    right.set(xlabel="number of qubits", ylabel="count",
              title="Generic circuit cost (grows ~4ⁿ: needs structure)")
    right.legend()
    return _save(fig, "3_resources.png")


def plot_stability_map(wavenumbers, times, energy_ratio, threshold) -> Path:
    """
    Figure 4: the controller's decision map. Colour = fraction of wave energy left.
    The white line is the threshold: below/right of it the disturbance fades on its own.
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    mesh = ax.pcolormesh(times, wavenumbers, np.log10(energy_ratio), shading="auto", cmap="RdYlGn_r")
    ax.contour(times, wavenumbers, energy_ratio, levels=[threshold], colors="white", linewidths=2)
    fig.colorbar(mesh, ax=ax, label="log$_{10}$(energy left / start)")
    ax.set(xlabel="controller response time  [plasma ticks]", ylabel=WAVENUMBER_LABEL,
           title=f"Fades on its own (green) vs needs control (red), threshold {threshold:.0%}")
    return _save(fig, "4_stability_map.png")
