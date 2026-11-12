# Archive: classical simulation (parked)

Dropped from the main demo for now, kept here so it's easy to bring back.

| File | Purpose |
|---|---|
| `classical_simulation.py` | `exact_evolution`: exact answer via linear algebra, used to measure the circuit's approximation error. `classical_solve`: timed standard ODE solver, for speed comparison. |
| `test_classical_simulation.py` | Classical solver matches exact; circuit's final state is >99% the same as exact. |

Last measured (5 qubits, wavenumber 0.5): exact damping rate −0.1539; largest circuit-vs-exact gap in field energy 0.00196; classical solve ~20 ms (a laptop easily wins at this size, see doc 4).

**To bring it back:** import from `archive.classical_simulation` in `src/main.py`, add the exact curve to `plots.plot_damping`, and run `python -m pytest archive`.
