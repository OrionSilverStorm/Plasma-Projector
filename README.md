# Plasma Projector: Quantum Simulation of Landau Damping

**Research question:** Can quantum computing offer a computational advantage over classical computing when simulating Landau damping in plasma, and what limits its use for fusion energy?

## Approach (Engel, Smith & Parker, 2019)
- Linearise the 1D1V Vlasov–Poisson equations for a single Fourier mode `k`.
- Discretise velocity on `N_v` grid points and rescale by `sqrt(F0)`, so the system becomes `dψ/dt = -iHψ` with Hermitian `H`.
- Encode `ψ = (E, f_1 … f_Nv)` in `n = ceil(log2(N_v + 1))` qubits.
- Evolve with a Trotterised circuit. `|E(t)|²` is the probability of measuring `|0…0⟩` and should decay at the Landau rate (γ ≈ -0.153 for k = 0.5).

## Layout
| Path | Purpose |
|---|---|
| `src/hamiltonian.py` | Build H, pad to 2^n, initial state, exact reference |
| `src/circuits.py` | State prep + time-evolution circuit |
| `src/simulate.py` | Run circuits, extract \|E(t)\|², fit damping rate |
| `src/resources.py` | Qubit / gate / depth estimates vs problem size |
| `src/main.py` | Runs everything, saves plots |
| `tests/` | Tests |
| `figures/` | Exported plots for slides |
