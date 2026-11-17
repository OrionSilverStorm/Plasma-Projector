"""
resources.py: how big do the quantum and classical computations get? (Viability + Advantage)

Two separate questions:
1. MEMORY. A classical grid with `points_per_dim` points along each axis, in a space with `dims`
   position axes and `dims` velocity axes, stores points_per_dim^(2 * dims) numbers. A quantum
   register stores the same amplitudes in 2 * dims * log2(points_per_dim) qubits. This exponential
   compression is the core of the quantum argument.
2. GATES. How many operations does one Trotter step cost? We measure it by compiling ("transpiling")
   our circuit into hardware-style gates (CNOT, RZ, SX, X). Honest finding: our generic Pauli
   decomposition needs a number of terms that grows like 4^n, which is NOT scalable. The scalable
   route uses the arrowhead structure of the hamiltonian (see docs/learn/04_advantage_and_limits.md).
"""
import numpy as np
from qiskit import transpile

from src.circuits import hamiltonian_to_paulis, trotter_step
from src.config import Params
from src.hamiltonian import build_hamiltonian

HARDWARE_GATES = ["cx", "rz", "sx", "x"]   # a typical superconducting-hardware gate set (e.g. IBM); "cx" = CNOT


def circuit_costs(qubit_counts: list[int], wavenumber: float = 0.5) -> list[dict]:
    """Compile one Trotter step for each qubit count. Returns Pauli terms, CNOT count and depth."""
    rows = []
    for n_qubits in qubit_counts:
        settings = Params(wavenumber=wavenumber, n_qubits=n_qubits)
        hamiltonian = build_hamiltonian(settings)
        compiled = transpile(trotter_step(hamiltonian, settings.time_step),
                             basis_gates=HARDWARE_GATES, optimization_level=1)
        rows.append({
            "n_qubits": n_qubits,
            "grid_points": settings.n_velocities,
            "pauli_terms": len(hamiltonian_to_paulis(hamiltonian)),
            "cnots_per_step": compiled.count_ops().get("cx", 0),
            "depth_per_step": compiled.depth(),
        })
    return rows


def memory_scaling(points_per_dim: np.ndarray, dims: int = 3) -> dict:
    """
    Classical numbers stored vs qubits needed for a grid with `dims` position and `dims` velocity axes.
    dims=3 is a real reactor (3 position + 3 velocity axes, "3D3V"). Our demo is dims=1 ("1D1V").
    """
    classical_values = points_per_dim.astype(float) ** (2 * dims)
    qubits = 2 * dims * np.ceil(np.log2(points_per_dim))
    return {"points_per_dim": points_per_dim, "classical_values": classical_values, "qubits": qubits}
