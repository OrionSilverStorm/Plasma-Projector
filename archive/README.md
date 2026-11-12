# Archive: classical simulation (parked, not deleted)

The team decided to drop classical simulation from the main demo for now. The code is kept here so it can come back.

| File | What it was used for |
|---|---|
| `classical_simulation.py` | `exact_evolution` (the exact answer, used to measure Trotter error) and `classical_solve` (timed ODE solver, as a speed benchmark) |
| `test_classical_simulation.py` | Classical solver matches exact; quantum circuit matches exact (fidelity > 0.99) |

Last measured (5 qubits, kλ_D = 0.5): exact γ = −0.1539, max |quantum − exact| in |E|² = 1.96×10⁻³, and the classical ODE solve took about 20 ms.

**To bring it back:** import from `archive.classical_simulation` in `src/main.py`. Add the exact curve back to `plots.plot_damping` as an extra line. Run `python -m pytest archive` to check it still works.
