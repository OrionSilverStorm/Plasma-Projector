# 5. Code walkthrough (in the order data flows)

```
config.Params ──> hamiltonian.build_hamiltonian ──> circuits.trotter_step ──> simulate.run_quantum
      │                 hamiltonian.initial_state ──> circuits.prep_circuit ──┘        │
      │                                                                               ▼
      │                         theory.landau_prediction ──(compare)──> simulate.fit_damping_rate
      │                                                                    simulate.classify_stability
      └──> resources.circuit_costs / memory_scaling ──> plots.* ──> figures/*.png
                                         (main.py calls all of the above in 5 steps)
```

| File | Key functions | What to look at |
|---|---|---|
| `config.py` | `Params`, `plasma_scales` | Every setting. Change `wavenumber` or `n_qubits` here. Derived values (`velocities`, `velocity_spacing`, `fake_revival_time`) are properties, so they can never go out of sync. |
| `hamiltonian.py` | `build_hamiltonian`, `initial_state`, `field_energy` | The 3 lines that fill `hamiltonian` are the whole physics model. |
| `theory.py` | `landau_prediction` | The textbook formula (root-finding with `newton`). The quantum γ is checked against it. |
| `circuits.py` | `hamiltonian_to_paulis`, `prep_circuit`, `trotter_step`, `full_circuit` | The Qiskit parts. Note the `.decompose()` in `trotter_step` (doc 3 explains why). `full_circuit` is the program you'd send to real hardware. |
| `simulate.py` | `run_quantum`, `fit_damping_rate`, `envelope`, `classify_stability` | Runs the circuit and turns probabilities into physics (γ) and decisions. |
| `resources.py` | `circuit_costs`, `memory_scaling` | Transpiles to hardware gates and counts them. Classical vs quantum memory. |
| `plots.py` | `plot_damping`, `plot_damping_vs_wavenumber`, `plot_resources`, `plot_stability_map` | One function per slide figure. |
| `main.py` | `step1_…` to `step5_…` | The demo script. Read its output top to bottom alongside these docs. |
| `tests/` | 8 tests | They prove H is Hermitian, Gauss's law holds, the circuit conserves energy and γ matches theory within 10%. |
| `archive/` | `exact_evolution`, `classical_solve` | Parked classical simulation and its 2 tests. Not run by default (`python -m pytest archive` runs them). |

## Running it
```
.venv\Scripts\activate            (VS Code usually does this automatically once the interpreter is selected)
python -m src.main                (about 20 s, prints results, writes 4 PNGs into figures/)
python -m pytest                  (about 5 s, all 8 tests should pass)
```

## Things to try (they build understanding fast)
1. Set `n_qubits=3` in `Params()` inside `main()`. The grid gets coarse, the recurrence arrives early and γ gets worse. Why? (Answer: doc 2, step 7.)
2. In `initial_state`, replace `field = ...` with `field = 1.0` and set `particles = 0 * particles`. The damping plot plateaus. Why? (Answer: Gauss's law, doc 2, step 5.)
3. Change `order=2` to `order=1` in `trotter_step`. The Trotter error grows. Compare the printed quantum γ with theory.
4. Raise `threshold` in `step3_stability` to 0.3. Which wavenumbers flip from "act" to "fades"?
