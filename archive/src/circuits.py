"""
circuits.py: builds the actual quantum circuits (Qiskit).

A circuit for our problem has two parts:
  1. STATE PREPARATION: load the starting plasma state into the qubits' amplitudes.
  2. TIME EVOLUTION: apply exp(-i * hamiltonian * time_step) once per time step.

How exp(-i * hamiltonian * time_step) becomes gates:
  - Write the hamiltonian as a weighted sum of "Pauli strings" (one of I, X, Y, Z on each qubit,
    combined). Any 2^n x 2^n matrix can be written this way.
  - Each term on its own is easy to build: a few CNOTs plus one RZ rotation.
  - The terms don't commute (order matters), so applying them one after another is not exact.
    TROTTERISATION does it anyway and accepts a small error that shrinks as time_step shrinks.
    Second-order Suzuki-Trotter (half-step forwards, then half-step backwards) gives an error
    that scales like time_step^3 per step.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate, StatePreparation
from qiskit.quantum_info import SparsePauliOp
from qiskit.synthesis import SuzukiTrotter


def n_qubits_for(matrix_or_vector: np.ndarray) -> int:
    """Number of qubits needed to hold an object of size 2^n."""
    return int(np.log2(len(matrix_or_vector)))


def hamiltonian_to_paulis(hamiltonian: np.ndarray) -> SparsePauliOp:
    """Split the hamiltonian into a weighted sum of Pauli strings, dropping terms that are basically zero."""
    return SparsePauliOp.from_operator(hamiltonian, atol=1e-12)


def prep_circuit(start_state: np.ndarray) -> QuantumCircuit:
    """Circuit that turns |0...0> into start_state. Qiskit works out the rotation gates for us."""
    circuit = QuantumCircuit(n_qubits_for(start_state), name="prep")
    circuit.append(StatePreparation(start_state), circuit.qubits)
    return circuit


def trotter_step(hamiltonian: np.ndarray, time_step: float, order: int = 2) -> QuantumCircuit:
    """
    Circuit for ONE time step, approximately exp(-i * hamiltonian * time_step), built with Suzuki-Trotter.

    `.decompose()` matters. Without it, Qiskit treats PauliEvolutionGate as one block and
    simulates it with the EXACT exponential, which hides the Trotter error. Decomposing
    replaces it with the real sequence of CNOTs and rotations a quantum computer would run.
    """
    circuit = QuantumCircuit(n_qubits_for(hamiltonian), name="step")
    gate = PauliEvolutionGate(hamiltonian_to_paulis(hamiltonian), time=time_step,
                              synthesis=SuzukiTrotter(order=order))
    circuit.append(gate, circuit.qubits)
    return circuit.decompose()


def full_circuit(start_state: np.ndarray, hamiltonian: np.ndarray, time_step: float,
                 n_steps: int) -> QuantumCircuit:
    """
    The complete program you would send to hardware: prepare, evolve n_steps times, measure.
    The probability of reading all zeros at the end equals the field energy at time n_steps * time_step.
    """
    circuit = prep_circuit(start_state)
    step = trotter_step(hamiltonian, time_step)
    for _ in range(n_steps):
        circuit.compose(step, inplace=True)
    circuit.measure_all()
    return circuit
