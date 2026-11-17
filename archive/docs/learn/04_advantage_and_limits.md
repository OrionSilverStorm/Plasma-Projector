# 4. Quantum advantage: the honest version

Code: `src/resources.py`, `src/theory.py`. Figure: `figures/3_resources.png`.

Three resources: quantum clearly wins on **memory**, currently loses (fixably) on **gates**, and must be careful on **readout**.

**One-sentence pitch:** we reproduce Engel, Smith & Parker's quantum algorithm for Landau damping in Qiskit, validate it against the textbook across wavenumbers, and add a stability classifier that answers a reactor-control question from a few measurements, avoiding full-state readout.

The problem it gets around

The 5 qubits hold the whole state of the plasma wave, which is 32 numbers at once (2⁵). The catch is that you can't just read those numbers out. Measuring a qubit gives a random 0 or 1, and the measurement destroys the state. To rebuild all 32 numbers you'd have to run the circuit a huge number of times and measure in many different ways. This is called full-state readout (or "tomography"), and the work grows exponentially with the number of qubits. That would cancel out any speed advantage the quantum computer had.

What the classifier does instead

A reactor controller doesn't need all 32 numbers. It needs one answer:

▎ "Will this ripple fade on its own before the magnets could react, or do we need to step in?"

## Memory: quantum wins

With N grid points per axis (`memory_scaling()`):

| Model                   | Classical numbers                | Qubits                                                              |
| ----------------------- | -------------------------------- | ------------------------------------------------------------------- |
| 1D1V, N = 32 (our demo) | 32² ≈ 1,000                      | 10 (we use 5: one wave shape in space needs only the velocity axis) |
| 3D3V reactor, N = 128   | 128⁶ ≈ **4×10¹²** (~70 TB)       | **42**                                                              |
| 3D3V, N = 1024          | ~10¹⁸ (beyond any supercomputer) | 60                                                                  |

Classical needs N⁶ numbers; qubits need 6·log₂N, since each qubit doubles capacity. Doubling N multiplies classical memory by 64 but adds only 6 qubits.

## Gates: the weak point

One compiled time step (CNOT, RZ, SX, X):

| Qubits | Pauli terms | CNOTs/step | Depth/step |
| ------ | ----------- | ---------- | ---------- |
| 3      | 30          | 124        | 272        |
| 5      | 510         | 2,516      | 5,099      |
| 7      | 7,422       | 37,480     | 75,172     |

Cost grows ~**4ⁿ**, which would cancel the memory win. It's fixable using the arrowhead structure:

- **Diagonal:** velocities are evenly spaced, so `v_j` is linear in index `j`. Written in binary, that's a sum over individual bits: ~n single-qubit rotations.
- **Row/column:** a rotation between index 0 and one bell-shaped vector, built from one cheap bell-curve loading circuit and its reverse.
- **Total:** polynomial in n per step instead of 4ⁿ (shown formally by Engel et al.). On our roadmap.

## Readout: be careful

Full state readout costs ~2ⁿ shots and destroys the speed-up. Hence the classifier asks for one probability: ~1/ε² shots, or ~1/ε with amplitude estimation, whatever the grid size.

## Scaling summary

- **Classical 3D3V:** memory and work per step ~N⁶.
- **Quantum (structured):** ~log N qubits, gates polynomial in log N, ~1/ε repeats for a yes/no answer.
- Exponential gap **for this specific question**, not "simulate everything".
- **Caveat:** quantum advantage for such equations is still debated; classical compression tricks exist too. Say so.

## Hardware today

- Best machines: ~100–1,000 noisy qubits; errors swamp results after ~1,000–10,000 CNOTs.
- Our demo needs ~2,500 CNOTs × 200 steps: not runnable now. Reactor scale needs error-corrected machines (~2030+), which is why the field focuses on resource estimates.

## Classical comparison

- `theory.py` → `landau_prediction`: the textbook answer, found by Newton's root-finding on the textbook equation. A formula, not a simulation; treat it as a black box.
- `archive/classical_solve`: ~20 ms for our 1D1V problem. **A laptop wins at this size.** The demo proves correctness; the advantage only appears at 3D3V.

## Likely judge questions

| Question                                | Answer                                                                                                                                         |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| "Isn't 1D easy classically?"            | Yes; it's our test case because the answer is known. The scaling argument is about 3D3V.                                                       |
| "Gates grow like 4ⁿ."                   | That's the general Pauli method. The arrowhead structure allows polynomial cost; it's on the roadmap.                                          |
| "How do you read the answer?"           | We don't read the state; one yes/no probability costs ~1/ε shots, independent of grid size.                                                    |
| "Growing waves?"                        | They make the matrix non-Hermitian. Known fixes (Schrödingerisation, linear combination of Hamiltonian simulations) are next.                  |
| "Why Ampère, not Gauss, for the field?" | Ampère gives the field a rate of change, so everything fits one update rule. Gauss's law then holds automatically if the start state obeys it. |
| "Noise?"                                | Today's devices can't run it; we give resource estimates for error-corrected hardware instead.                                                 |
