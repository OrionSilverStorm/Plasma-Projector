# 3. Circuits, Trotter steps and measurement

Code: `src/circuits.py`, `src/simulate.py`.

```
|00000> --[ load starting state ]--[ step ]--[ step ]-- ... --[ step ]--[ measure ]
                                    \___ one per time_step, 200 total ___/
```

## 1. Load the starting state (`prep_circuit`)
Qiskit's `StatePreparation` finds rotations turning `[1, 0, …, 0]` into our vector. A general vector costs ~2ⁿ gates; bell-curve shapes like ours can be loaded far more cheaply (polynomial in n), which matters at scale (doc 4).

## 2. One time step (`trotter_step`)
Hardware can't apply an arbitrary matrix, so to apply `e^{−i · hamiltonian · time_step}`:

1. **Split into building blocks.** `hamiltonian = Σ cⱼ Pⱼ`, each `Pⱼ` a Pauli string like `XZIYZ` (`SparsePauliOp.from_operator`). Any matrix can be split this way, like a signal into sine waves. 5 qubits: 510 terms.
2. **Each block is easy:** basis-change gates, a CNOT chain computing the qubits' parity, one RZ rotation, then undo.
3. **Combine them (Trotterisation).** e^{A+B} = e^A·e^B only if `AB = BA`, and our blocks mostly don't commute. So we apply them one after another over a small step and accept a small error. Second-order Suzuki–Trotter (`order=2`: half-step forwards, half-step backwards) cancels the biggest error, leaving ~`time_step³` per step.

**Gotcha:** given `PauliEvolutionGate` as one block, Qiskit's simulator silently uses the *exact* exponential, hiding the Trotter error. `.decompose()` forces the real gate sequence (true error ~2×10⁻³ in field energy).

## 3. Measure
P(`00000`) = field energy. Hardware can't show a probability directly: you run many *shots* and count.

## How `run_quantum` is fast
Every step is the same circuit, so we get its 32×32 matrix once (`Operator(...)`, Trotter error included) and multiply the state by it 200 times. Identical results to gate-by-gate simulation, much faster.

## Fitting the damping rate (`fit_damping_rate`)
1. Find the energy curve's peaks (`find_peaks`); only peaks show how much wave is left.
2. Keep peaks after t = 2 (start-up settling) and before the fake revival.
3. Fit a line to `log(peak)` vs time. Slope = `2 · damping_rate`.

## Stability classifier (`classify_stability`): our contribution
A controller needs only yes/no: *by the time the magnets could react, is the ripple below 10% of its starting energy?*
- Estimate P(`00000`) at 4 times across about one wiggle (`window_indices`) and keep the largest, so a dip (energy briefly in the electrons) can't fake a "faded".
- 2,000 simulated shots each (`rng.binomial`), 8,000 runs total, accurate to ~0.01.
- Result at t = 8: wavenumber ≤ 0.40 → "controller must act"; ≥ 0.45 → "fades on its own".

**Why it matters:** reading a whole state takes ~2ⁿ measurements, killing any speed-up. One probability to accuracy ε takes ~1/ε² shots (~1/ε with *amplitude estimation*), **independent of grid size**.
