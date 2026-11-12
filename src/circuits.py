"""
circuits.py: builds the actual quantum circuits (Qiskit).

A circuit for our problem has two parts:
  1. STATE PREPARATION: load the starting plasma state psi(0) into the qubits' amplitudes.
  2. TIME EVOLUTION: apply exp(-i H dt) once per time step.

How exp(-i H dt) becomes gates:
  - Write H as a weighted sum of "Pauli strings" (tensor products of I, X, Y, Z on each qubit),
    H = sum_j c_j P_j. Any 2^n x 2^n matrix can be written this way.
  - Each term exp(-i c_j P_j dt) is easy: a few CNOTs plus one RZ rotation.
  - The terms don't commute, so we can't apply them one after another exactly. TROTTERISATION
    applies them in sequence anyway and accepts a small error that shrinks as dt shrinks.
    Second-order Suzuki-Trotter (forwards half-step, then backwards half-step) gives error ~ dt^3 per step.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate, StatePreparation
from qiskit.quantum_info import SparsePauliOp
from qiskit.synthesis import SuzukiTrotter


def n_qubits_for(matrix_or_vector: np.ndarray) -> int:
    """Number of qubits needed to hold an object of size 2^n."""
    return int(np.log2(len(matrix_or_vector)))


def hamiltonian_to_paulis(H: np.ndarray) -> SparsePauliOp:
    """Decompose H into a weighted sum of Pauli strings, dropping numerically-zero terms."""
    return SparsePauliOp.from_operator(H, atol=1e-12)


def prep_circuit(psi0: np.ndarray) -> QuantumCircuit:
    """Circuit that turns |0...0> into psi0. Qiskit works out the rotation gates for us."""
    qc = QuantumCircuit(n_qubits_for(psi0), name="prep")
    qc.append(StatePreparation(psi0), qc.qubits)
    return qc


def trotter_step(H: np.ndarray, dt: float, order: int = 2) -> QuantumCircuit:
    """
    Circuit for ONE time step, approximately exp(-i H dt), built with Suzuki-Trotter.

    `.decompose()` matters. Without it, Qiskit treats PauliEvolutionGate as one block and
    simulates it with the EXACT exponential, which hides the Trotter error. Decomposing
    replaces it with the real sequence of CNOTs and rotations a quantum computer would run.
    """
    qc = QuantumCircuit(n_qubits_for(H), name="step")
    gate = PauliEvolutionGate(hamiltonian_to_paulis(H), time=dt, synthesis=SuzukiTrotter(order=order))
    qc.append(gate, qc.qubits)
    return qc.decompose()


def full_circuit(psi0: np.ndarray, H: np.ndarray, dt: float, n_steps: int) -> QuantumCircuit:
    """
    The complete program you would send to hardware: prepare, evolve n_steps times, measure.
    The probability of reading all zeros at the end equals |E(n_steps * dt)|^2.
    """
    qc = prep_circuit(psi0)
    step = trotter_step(H, dt)
    for _ in range(n_steps):
        qc.compose(step, inplace=True)
    qc.measure_all()
    return qc
