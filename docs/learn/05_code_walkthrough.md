# 5. Code walkthrough

```
config.Params ──> hamiltonian.build_hamiltonian ──> circuits.trotter_step ──> simulate.run_quantum
      │                 hamiltonian.initial_state ──> circuits.prep_circuit ──┘        │
      │                                                                               ▼
      │                         theory.landau_prediction ──(compare)──> simulate.fit_damping_rate
      │                                                                    simulate.classify_stability
      └──> resources.circuit_costs / memory_scaling ──> plots.* ──> figures/*.png
```

Settings define the matrix and start state → those become circuits → running them gives field energy over time → we fit the damping rate and answer the stability question → separately, we count circuit size → everything is printed and plotted.

| File | Look at |
|---|---|
| `config.py` | All settings (`wavenumber`, `n_qubits`). Derived values are `@property`s so they never go stale; `frozen=True` stops settings changing mid-run. |
| `hamiltonian.py` | The 3 lines filling `hamiltonian`: the whole physics model. |
| `theory.py` | Textbook answer via `newton` root-finding. |
| `circuits.py` | The `.decompose()` in `trotter_step` (doc 3). `full_circuit` is what you'd send to hardware. |
| `simulate.py` | Turns probabilities into a damping rate and yes/no decisions. |
| `resources.py` | Gate counts and memory comparison. |
| `plots.py` | One function per figure; no physics. |
| `main.py` | Five steps, below. |
| `tests/` | 8 tests: Hermitian matrix, Gauss's law, length stays 1, damping within 10% of textbook. |

## What `main.py` does
1. **`step1_single_run`**: wavenumber 0.5, circuit vs textbook. Figure 1.
2. **`step2_sweep_wavenumber`**: 9 wavenumbers, 0.3–0.7. Figure 2.
3. **`step3_stability`**: classifier per wavenumber + heat map. Figure 4.
4. **`step4_resources`**: gate costs for 3–7 qubits, memory comparison. Figure 3.
5. **`step5_real_units`**: answer in mm and ps for a real tokamak.

## Experiments
Predict the result first; undo each change after.

1. **Coarse grid:** in `main()`, use `Params(n_qubits=3)`. The fake revival now comes at ~6 ticks, so step 1 fits it and prints a *positive* damping rate (~+0.8), and step 2 stops with "Not enough oscillation peaks". (Doc 2, step 7.)
2. **Break Gauss's law:** in `initial_state`, add `field = 1.0` and `particles = 0 * particles` before `state = ...`. Figure 1 flattens instead of falling. (Doc 2, step 5.)
3. **Cruder steps:** in `simulate.py`, set `order: int = 1` in `run_quantum` (not `trotter_step`, which receives `run_quantum`'s value). The damping rate drifts from the textbook.
4. **Stricter controller:** raise `threshold` in `step3_stability` to 0.3. Which wavenumbers flip to "fades on its own"?
