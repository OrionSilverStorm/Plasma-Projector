"""
Section 3: Running the Simulation (Quantum Qiskit Circuits vs. Classical Solver).

Implements:
1. `build_fast_arrowhead_step_circuit`: Problem 3 efficiency fix — exploits the
   arrowhead structure of H (O(n) RZ gates for diagonal + 2D subspace reflection for
   field coupling) instead of O(4^n) dense Pauli strings.
2. `build_naive_pauli_step_circuit`: Generic dense Pauli decomposition for comparison.
3. `run_quantum_simulation` & `run_classical_simulation`: Runs the simulation and tracks
   hardware-independent efficiency metrics (Problem 2 fix: sparse FLOPs vs. QPU gate operations).

For plain-English explanations of how the circuit takes factors, computes, and outputs, see README.md (Section 3).
"""

import time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import csr_matrix

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PauliEvolutionGate, StatePreparation
from qiskit.quantum_info import Operator, SparsePauliOp, Statevector
from qiskit.synthesis import SuzukiTrotter

from config import make_velocity_grid
from hamiltonian import (
    build_hamiltonian_matrix,
    create_initial_qubit_state,
    maxwellian_bell_curve,
)

# Typical superconducting QPU (e.g. IBM Heron/Eagle) average 2-qubit gate layer duration: ~50 ns
SUPERCONDUCTING_GATE_LAYER_SECONDS = 50e-9
HARDWARE_BASIS_GATES = ["cx", "rz", "sx", "x"]


def _add_zero_state_phase(qc: QuantumCircuit, phase: float) -> None:
    """Apply phase exp(i * phase) only to the electric-field slot |00...0>."""
    n = qc.num_qubits
    qc.x(range(n))
    qc.mcp(phase, list(range(n - 1)), n - 1)
    qc.x(range(n))


def build_diagonal_circuit(n_qubits: int, k: float, max_velocity: float, dt: float) -> QuantumCircuit:
    """
    Exact circuit for the diagonal electron-coasting term exp(-i * H_diag * dt).
    Because velocity v_j is linear in the binary index j, it requires only 1 single-qubit
    RZ gate per qubit (0 CNOTs!) plus a phase correction on slot |00...0>. See README.md (Section 3).
    """
    _, dv = make_velocity_grid(n_qubits, max_velocity)
    qc = QuantumCircuit(n_qubits, name="Diagonal_Coasting")

    for qubit_idx in range(n_qubits):
        qc.rz(-k * dv * (2 ** qubit_idx) * dt, qubit_idx)

    # Cancel the linear ramp phase on slot 0 (electric field has 0 diagonal energy)
    _add_zero_state_phase(qc, -k * dv * (2 ** (n_qubits - 1)) * dt)
    return qc


def build_arrow_circuit(n_qubits: int, coupling: np.ndarray, dt: float) -> QuantumCircuit:
    """
    Exact circuit for the field-particle coupling term exp(-i * H_arrow * dt).
    H_arrow only couples |00...0> to one normalized velocity state |phi>, forming a 2D
    subspace with eigenstates |psi_+> and |psi_-> = -R_0 |psi_+>. See README.md (Section 3).
    """
    norm_c = float(np.linalg.norm(coupling))
    psi_plus = np.concatenate(([1.0], -1j * coupling / norm_c)) / np.sqrt(2.0)
    prep = StatePreparation(psi_plus)
    inv_prep = prep.inverse()

    qc = QuantumCircuit(n_qubits, name="Arrow_Coupling")

    # Evolve eigenstate |psi_+> with phase -norm_c * dt
    qc.append(inv_prep, qc.qubits)
    _add_zero_state_phase(qc, -norm_c * dt)
    qc.append(prep, qc.qubits)

    # Flip |00...0> sign to map |psi_+> -> |psi_->, evolve with +norm_c * dt, and unflip
    _add_zero_state_phase(qc, np.pi)
    qc.append(inv_prep, qc.qubits)
    _add_zero_state_phase(qc, +norm_c * dt)
    qc.append(prep, qc.qubits)
    _add_zero_state_phase(qc, np.pi)
    return qc


def build_fast_arrowhead_step_circuit(config: dict, dt: float) -> QuantumCircuit:
    """
    Problem 3 Efficiency Fix: 2nd-order Suzuki-Trotter step exploiting the arrowhead
    structure: Diagonal(dt/2) -> Arrow(dt) -> Diagonal(dt/2). See README.md (Section 3).
    """
    n_qubits = config["n_qubits"]
    k = config["wavenumber"]
    velocities, dv = make_velocity_grid(n_qubits, config["max_velocity"])
    f0 = maxwellian_bell_curve(velocities, config["temperature"])
    coupling = np.sqrt(config["density"]) * velocities * np.sqrt(f0 * dv)

    qc = QuantumCircuit(n_qubits, name="Fast_Arrowhead_Step")
    diag_half = build_diagonal_circuit(n_qubits, k, config["max_velocity"], dt / 2.0)
    arrow_full = build_arrow_circuit(n_qubits, coupling, dt)

    qc.compose(diag_half, inplace=True)
    qc.compose(arrow_full, inplace=True)
    qc.compose(diag_half, inplace=True)
    return qc


def build_naive_pauli_step_circuit(H: np.ndarray, dt: float, n_qubits: int) -> QuantumCircuit:
    """
    Baseline (unoptimized) step circuit: decomposes H into ~4^n dense Pauli strings
    and applies 2nd-order Suzuki-Trotter. Kept to benchmark the Problem 3 speedup.
    """
    pauli_hamiltonian = SparsePauliOp.from_operator(H, atol=1e-12)
    evolution_gate = PauliEvolutionGate(
        pauli_hamiltonian,
        time=dt,
        synthesis=SuzukiTrotter(order=2),
    )
    step_circuit = QuantumCircuit(n_qubits, name="Naive_Pauli_Step")
    step_circuit.append(evolution_gate, step_circuit.qubits)
    return step_circuit.decompose()


def build_qiskit_step_circuit(H: np.ndarray, dt: float, n_qubits: int,
                              config: dict | None = None, method: str = "arrowhead") -> QuantumCircuit:
    """Build one Trotter step circuit using either 'arrowhead' (fast) or 'naive_pauli'."""
    if method == "arrowhead" and config is not None:
        return build_fast_arrowhead_step_circuit(config, dt)
    return build_naive_pauli_step_circuit(H, dt, n_qubits)


def run_quantum_simulation(config: dict, method: str = "arrowhead") -> dict:
    """
    Evolve the plasma state on the Qiskit circuit, extract electric field energy
    P(|00000>) and 2,000-shot hardware estimates, and compute hardware-independent
    quantum gate/depth metrics (Problem 2 fix). See README.md (Section 3).
    """
    start_clock = time.perf_counter()

    n_qubits = config["n_qubits"]
    n_steps = config["n_steps"]
    dt = config["end_time"] / n_steps
    times = np.linspace(0.0, config["end_time"], n_steps + 1)

    H = build_hamiltonian_matrix(config)
    init_array = create_initial_qubit_state(config)

    # Step 1: Load initial plasma state into |00000>
    prep_qc = QuantumCircuit(n_qubits, name="State_Prep")
    prep_qc.append(StatePreparation(init_array), prep_qc.qubits)
    current_state = Statevector(prep_qc).data

    # Step 2: Build one Trotter time-step circuit and evolve n_steps times
    step_qc = build_qiskit_step_circuit(H, dt, n_qubits, config=config, method=method)
    step_unitary = Operator(step_qc).data

    all_states = [current_state]
    for _ in range(n_steps):
        current_state = step_unitary @ current_state
        all_states.append(current_state)
    all_states = np.array(all_states)

    # Step 3: Read out slot 0 probability P(|00000>) = Electric Field Energy
    exact_field_energy = np.abs(all_states[:, 0]) ** 2

    # Simulate realistic quantum hardware measurement shots (2,000 runs per time point)
    rng = np.random.default_rng(seed=42)
    shots = 2000
    shot_counts_all_zeros = rng.binomial(n=shots, p=exact_field_energy)
    shot_estimated_energy = shot_counts_all_zeros / shots

    sim_wall_seconds = time.perf_counter() - start_clock

    # Problem 2 Fix: Measure actual compiled quantum hardware gate counts & QPU execution time
    compiled_step = transpile(step_qc, basis_gates=HARDWARE_BASIS_GATES, optimization_level=1)
    cnots_per_step = compiled_step.count_ops().get("cx", 0)
    depth_per_step = compiled_step.depth()
    total_gates_per_step = sum(compiled_step.count_ops().values())
    estimated_qpu_single_shot_s = n_steps * depth_per_step * SUPERCONDUCTING_GATE_LAYER_SECONDS

    return {
        "times": times,
        "energy": exact_field_energy,
        "shot_energy": shot_estimated_energy,
        "runtime_s": sim_wall_seconds,
        "method": method,
        "cnots_per_step": cnots_per_step,
        "depth_per_step": depth_per_step,
        "total_gates_per_step": total_gates_per_step,
        "total_circuit_cnots": cnots_per_step * n_steps,
        "total_circuit_depth": depth_per_step * n_steps,
        "estimated_qpu_single_shot_s": estimated_qpu_single_shot_s,
    }


def run_classical_simulation(config: dict) -> dict:
    """
    Solve d(state)/dt = -i * H @ state using SciPy's RK45 ODE solver with a sparse
    CSR matrix (how a real classical code exploits the arrowhead zeros) and count
    exact floating-point operations (FLOPs) for Problem 2. See README.md (Section 3).
    """
    start_clock = time.perf_counter()

    times = np.linspace(0.0, config["end_time"], config["n_steps"] + 1)
    H = build_hamiltonian_matrix(config)
    sparse_H = csr_matrix(H)
    init_array = create_initial_qubit_state(config)

    solution = solve_ivp(
        fun=lambda t, state: -1j * (sparse_H @ state),
        t_span=(times[0], times[-1]),
        y0=init_array,
        t_eval=times,
        rtol=1e-8,
        atol=1e-10,
    )

    classical_states = solution.y.T
    classical_energy = np.abs(classical_states[:, 0]) ** 2
    elapsed_s = time.perf_counter() - start_clock

    # Problem 2 Fix: Count hardware-independent classical work (sparse matrix-vector FLOPs)
    # Each complex multiply-add costs 8 real FLOPs; solution.nfev is the exact number of RHS calls
    nnz = int(sparse_H.nnz)
    rhs_evaluations = int(solution.nfev)
    total_flops = rhs_evaluations * nnz * 8

    return {
        "times": times,
        "energy": classical_energy,
        "runtime_s": elapsed_s,
        "nonzeros": nnz,
        "rhs_evaluations": rhs_evaluations,
        "total_flops": total_flops,
    }


def benchmark_efficiency_scaling(qubit_list: list[int] | None = None) -> list[dict]:
    """
    Problem 2 & 3 Benchmark: Compare Classical Sparse ODE (FLOPs), Naive Pauli Quantum
    Circuit (~4^n CNOTs), and Fast Arrowhead Quantum Circuit (structured CNOTs) across qubit counts.
    """
    from config import DEFAULT_CONFIG

    if qubit_list is None:
        qubit_list = [3, 4, 5, 6]

    rows = []
    dt = DEFAULT_CONFIG["end_time"] / DEFAULT_CONFIG["n_steps"]
    n_steps = DEFAULT_CONFIG["n_steps"]

    for n_q in qubit_list:
        cfg = {**DEFAULT_CONFIG, "n_qubits": n_q}
        H = build_hamiltonian_matrix(cfg)

        # 1. Classical sparse solver metrics
        c_res = run_classical_simulation(cfg)

        # 2. Naive Pauli quantum step metrics
        naive_qc = build_naive_pauli_step_circuit(H, dt, n_q)
        compiled_naive = transpile(naive_qc, basis_gates=HARDWARE_BASIS_GATES, optimization_level=1)
        naive_cnots = compiled_naive.count_ops().get("cx", 0)
        naive_depth = compiled_naive.depth()

        # 3. Fast Arrowhead quantum step metrics (Problem 3 fix)
        fast_qc = build_fast_arrowhead_step_circuit(cfg, dt)
        compiled_fast = transpile(fast_qc, basis_gates=HARDWARE_BASIS_GATES, optimization_level=1)
        fast_cnots = compiled_fast.count_ops().get("cx", 0)
        fast_depth = compiled_fast.depth()

        rows.append({
            "n_qubits": n_q,
            "velocity_buckets": (2 ** n_q) - 1,
            "classical_flops": c_res["total_flops"],
            "classical_rhs_evals": c_res["rhs_evaluations"],
            "naive_cnots_per_step": naive_cnots,
            "naive_depth_per_step": naive_depth,
            "naive_total_cnots": naive_cnots * n_steps,
            "fast_cnots_per_step": fast_cnots,
            "fast_depth_per_step": fast_depth,
            "fast_total_cnots": fast_cnots * n_steps,
            "cnot_reduction_factor": naive_cnots / max(fast_cnots, 1),
            "fast_qpu_time_ms": n_steps * fast_depth * SUPERCONDUCTING_GATE_LAYER_SECONDS * 1e3,
        })

    return rows
