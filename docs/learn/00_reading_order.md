# Start here

**First, read [how_to_learn.md](how_to_learn.md)**: the study method and checklist for these docs.

Read these in order (about 1 to 1.5 hours total). Each file is short. Open the matching code file alongside it.

| # | File | You'll understand | Code it explains |
|---|---|---|---|
| 1 | [01_plasma_and_landau.md](01_plasma_and_landau.md) | What a plasma wave is and why it dies out without collisions | none (pure physics) |
| 2 | [02_equation_to_qubits.md](02_equation_to_qubits.md) | How a plasma equation becomes a list of qubit amplitudes | `config.py`, `hamiltonian.py` |
| 3 | [03_circuits_and_trotter.md](03_circuits_and_trotter.md) | How that list is evolved by gates, and how we read the answer | `circuits.py`, `simulate.py` |
| 4 | [04_advantage_and_limits.md](04_advantage_and_limits.md) | Where quantum wins, where it doesn't, and judge Q&A | `resources.py`, `theory.py` |
| 5 | [05_code_walkthrough.md](05_code_walkthrough.md) | The whole program, file by file, in run order | everything |
| 6 | [reading_list.md](reading_list.md) | Papers to cite and read deeper | none |

## Glossary (come back here whenever a word is unfamiliar)

| Term | Plain meaning |
|---|---|
| **Plasma** | Gas so hot that electrons are ripped off atoms, leaving a soup of charged particles. |
| **Plasma frequency ω_p** | How fast electrons oscillate if you shove them out of place. It sets the "tick" of our clock. |
| **Debye length λ_D** | Distance beyond which a charge is hidden by the cloud of opposite charges around it. It sets our "ruler". |
| **Thermal speed v_th** | Typical electron speed at a given temperature. v_th = λ_D·ω_p. |
| **Wavenumber k** | 2π / wavelength. Large k means a short wave. We always use the dimensionless **kλ_D**. |
| **Distribution function f(x, v, t)** | How many electrons are at position x with velocity v. The plasma "state". |
| **Maxwellian F0(v)** | The bell-curve velocity distribution of a plasma at rest and in equilibrium. |
| **Landau damping** | A wave dying out by handing its energy to particles that "surf" it. No collisions needed. |
| **Damping rate γ** | The wave amplitude shrinks like e^{γt}. Negative γ means it decays. |
| **Phase space** | Position and velocity together. 1D1V means 1 position axis and 1 velocity axis; a real reactor is 3D3V. |
| **Qubit / amplitude** | n qubits hold 2ⁿ complex numbers (amplitudes). Measuring gives outcome i with probability \|amplitude_i\|². |
| **Hamiltonian H** | The matrix that generates a quantum system's evolution: ψ(t) = e^{−iHt}ψ(0). |
| **Hermitian** | H equals its own conjugate transpose. This guarantees e^{−iHt} is a legal (unitary) quantum operation. |
| **Unitary** | An operation that preserves total probability (length 1). Every quantum gate is unitary. |
| **Pauli strings** | Products like X⊗Z⊗I. Any matrix is a weighted sum of them, and each one is easy to exponentiate in gates. |
| **Trotterisation** | Approximating e^{−i(A+B)t} by alternating small e^{−iA dt} and e^{−iB dt} steps. |
| **Recurrence time T_R** | When a discrete velocity grid makes the wave falsely "come back". Results after it are fake. |
| **Transpile** | Compile a circuit into the gate set real hardware supports (CNOT, RZ, SX, X). |
| **CNOT count / depth** | Main hardware cost measures. CNOTs are the noisy gates; depth is the number of sequential layers. |
