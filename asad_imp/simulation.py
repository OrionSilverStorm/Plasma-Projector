"""
Section 3: Running the Simulation (Quantum Qiskit Circuit vs. Classical Solver).

For the full explanation of Pauli decomposition, 2nd-order Suzuki-Trotter steps,
measurement shots, and the SciPy RK45 classical benchmark, see README.md (Section 3).
"""

import time
import numpy as np
from scipy.integrate import solve_ivp

from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate, StatePreparation
from qiskit.quantum_info import Operator, SparsePauliOp, Statevector
from qiskit.synthesis import SuzukiTrotter

from hamiltonian import build_hamiltonian_matrix, create_initial_qubit_state


def build_qiskit_step_circuit(H: np.ndarray, dt: float, n_qubits: int) -> QuantumCircuit:
    """
    Decompose H into Pauli strings and build a 2nd-order Suzuki-Trotter circuit
    for a single time step dt. See README.md (Section 3).
    """
    pauli_hamiltonian = SparsePauliOp.from_operator(H, atol=1e-12)
    evolution_gate = PauliEvolutionGate(
        pauli_hamiltonian,
        time=dt,
        synthesis=SuzukiTrotter(order=2),
    )

    step_circuit = QuantumCircuit(n_qubits, name="Trotter_Step")
    step_circuit.append(evolution_gate, step_circuit.qubits)
    return step_circuit.decompose()


def run_quantum_simulation(config: dict) -> dict:
    """
    Evolve the plasma state using the Qiskit Trotter circuit and extract
    electric field energy P(|00000>) plus 2,000-shot readout estimates. See README.md (Section 3).
    """
    start_clock = time.perf_counter()

    n_qubits = config["n_qubits"]
    dt = config["end_time"] / config["n_steps"]
    times = np.linspace(0.0, config["end_time"], config["n_steps"] + 1)

    H = build_hamiltonian_matrix(config)
    init_array = create_initial_qubit_state(config)

    # Prepare |00000> into the initial plasma state
    prep_qc = QuantumCircuit(n_qubits, name="State_Prep")
    prep_qc.append(StatePreparation(init_array), prep_qc.qubits)
    current_state = Statevector(prep_qc).data

    # Extract the single-step Trotter operator and apply it n_steps times
    step_qc = build_qiskit_step_circuit(H, dt, n_qubits)
    step_unitary = Operator(step_qc).data

    all_states = [current_state]
    for _ in range(config["n_steps"]):
        current_state = step_unitary @ current_state
        all_states.append(current_state)
    all_states = np.array(all_states)

    # Slot 0 amplitude squared = P(measure |00000>) = Electric Field Energy (see README.md -> Section 3)
    exact_field_energy = np.abs(all_states[:, 0]) ** 2

    # Simulate finite-shot hardware readout noise (2,000 shots)
    rng = np.random.default_rng(seed=42)
    shots = 2000
    shot_counts_all_zeros = rng.binomial(n=shots, p=exact_field_energy)
    shot_estimated_energy = shot_counts_all_zeros / shots

    elapsed_s = time.perf_counter() - start_clock
    return {
        "times": times,
        "energy": exact_field_energy,
        "shot_energy": shot_estimated_energy,
        "runtime_s": elapsed_s,
    }


def run_classical_simulation(config: dict) -> dict:
    """
    Solve d(state)/dt = -i * H @ state directly using SciPy's RK45 ODE solver
    for side-by-side comparison with the quantum circuit. See README.md (Section 3).
    """
    start_clock = time.perf_counter()

    times = np.linspace(0.0, config["end_time"], config["n_steps"] + 1)
    H = build_hamiltonian_matrix(config)
    init_array = create_initial_qubit_state(config)

    solution = solve_ivp(
        fun=lambda t, state: -1j * (H @ state),
        t_span=(times[0], times[-1]),
        y0=init_array,
        t_eval=times,
        rtol=1e-8,
        atol=1e-10,
    )

    classical_states = solution.y.T
    classical_energy = np.abs(classical_states[:, 0]) ** 2

    elapsed_s = time.perf_counter() - start_clock
    return {
        "times": times,
        "energy": classical_energy,
        "runtime_s": elapsed_s,
    }
