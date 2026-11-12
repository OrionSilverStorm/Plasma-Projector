# 3. Circuits, Trotter steps and measurement

Code: `src/circuits.py`, `src/simulate.py`.

## The circuit has three parts
```
|0...0> --[ StatePreparation(ψ0) ]--[ step ]--[ step ]-- ... --[ step ]--[ measure ]
                                     \_______ one per dt, 200 total ______/
```

### 1. State preparation (`prep_circuit`)
Qiskit's `StatePreparation` builds rotations that turn |0…0⟩ into any given vector ψ0. For general vectors this costs about 2ⁿ gates. Our ψ0 is a Gaussian-shaped vector, and Gaussians can be prepared with only poly(n) gates (Grover–Rudolph / Kitaev–Webb). This matters for scaling (doc 4).

### 2. Time evolution (`trotter_step`)
We need U = e^{−iH·dt}. Hardware can't apply an arbitrary matrix, so:
1. **Pauli decomposition:** write H = Σ c_j P_j, where each P_j is a string like `XZIYZ`. `SparsePauliOp.from_operator` does this. For 5 qubits our H needs 510 terms.
2. **Each term is easy.** e^{−i c P dt} = basis-change gates + a CNOT "ladder" that computes the parity + one RZ rotation + undo the ladder.
3. **Trotterisation:** the terms don't commute (AB ≠ BA), so e^{−i(A+B)dt} ≠ e^{−iA dt}e^{−iB dt} exactly. The error per step is about dt². **Second-order Suzuki–Trotter** (half-step forwards through the terms, half-step backwards) cancels the leading error, leaving about dt³ per step.

**Gotcha we hit and fixed:** if you hand Qiskit the `PauliEvolutionGate` as one block, its simulator quietly uses the **exact** exponential, which hides the Trotter error (we saw 4×10⁻¹⁵). `trotter_step` calls `.decompose()`, so we simulate the real gate sequence. The real Trotter error is about 2×10⁻³ in |E|². (We measured this against an exact classical answer; that code is now parked in `archive/`.)

### 3. Measurement
P(measure |0…0⟩) = |E(t)|². On hardware, you run the circuit many times ("shots") and count.

## How `run_quantum` simulates it efficiently
Every step is the same circuit. So we compute that circuit's 32×32 unitary once (`Operator(step)`) and multiply the state by it 200 times. This gives exactly what the gates do (Trotter error included), just faster than re-simulating about 2,500 CNOTs per step.

## Getting γ from the curve (`fit_damping_rate`)
1. Find the peaks of |E(t)|² (the tops of each oscillation).
2. Skip t < 2 (start-up transient), and stop before the recurrence time.
3. Fit a straight line to log(peak) against t. The slope is 2γ (energy is amplitude squared), so γ = slope/2.

## The stability classifier (`classify_stability`): our novelty
A reactor controller doesn't need the full plasma state. It needs a **yes/no** answer: *by the time my magnets could react, will this ripple have faded below 10% of its energy?*
- It measures P(|0…0⟩) at 4 times across one oscillation (so it can't be fooled by a trough where energy is temporarily in the particles) and takes the largest.
- With 2,000 shots each (8,000 runs total), the estimate is within about 0.01 of the truth.
- Result: kλ_D ≤ 0.40 means "controller must act"; kλ_D ≥ 0.45 means "fades on its own" (at t = 8/ω_p).
- **Why it matters:** extracting a whole quantum state costs about 2ⁿ measurements and kills any speedup. One probability costs about 1/ε² shots, or 1/ε with amplitude estimation, **independent of grid size**.
