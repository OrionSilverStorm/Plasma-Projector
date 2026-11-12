"""
resources.py: how big do the quantum and classical computations get? (Viability + Advantage)

Two separate questions:
1. MEMORY. A classical grid with N points per dimension in d-dimensional phase space (d space plus
   d velocity dimensions) stores N^(2d) numbers. A quantum register stores the same amplitudes in
   2d * log2(N) qubits. This exponential compression is the core of the quantum argument.
2. GATES. How many operations does one Trotter step cost? We measure it by compiling ("transpiling")
   our circuit into hardware-style gates (CNOT, RZ, SX, X). Honest finding: our generic Pauli
   decomposition needs a number of terms that grows like 4^n, which is NOT scalable. The scalable
   route uses the structure of H (see docs/learn/04_advantage_and_limits.md).
"""
import numpy as np
from qiskit import transpile

from src.circuits import hamiltonian_to_paulis, trotter_step
from src.config import Params
from src.hamiltonian import build_hamiltonian

BASIS_GATES = ["cx", "rz", "sx", "x"]   # a typical superconducting-hardware gate set (e.g. IBM)


def circuit_costs(n_values: list[int], k: float = 0.5) -> list[dict]:
    """Compile one Trotter step for each qubit count n. Returns Pauli terms, CNOT count and depth."""
    rows = []
    for n in n_values:
        p = Params(k=k, n_qubits=n)
        H = build_hamiltonian(p)
        compiled = transpile(trotter_step(H, p.dt), basis_gates=BASIS_GATES, optimization_level=1)
        rows.append({
            "n_qubits": n,
            "grid_points": p.n_v,
            "pauli_terms": len(hamiltonian_to_paulis(H)),
            "cx_per_step": compiled.count_ops().get("cx", 0),
            "depth_per_step": compiled.depth(),
        })
    return rows


def memory_scaling(points_per_dim: np.ndarray, dims: int = 3) -> dict:
    """
    Classical numbers stored vs qubits needed for a dims-D space + dims-D velocity grid.
    dims=3 is a real reactor (3D3V). Our demo is dims=1 (1D1V).
    """
    classical_values = points_per_dim.astype(float) ** (2 * dims)
    qubits = 2 * dims * np.ceil(np.log2(points_per_dim))
    return {"N": points_per_dim, "classical_values": classical_values, "qubits": qubits}
