# Plasma Projector: Quantum Simulation of Landau Damping

**Research question:** Can quantum computing offer a computational advantage over classical computing when simulating Landau damping in plasma, and what limits its use for fusion energy?

**New to the project? Start with [docs/learn/how_to_learn.md](docs/learn/how_to_learn.md).**

## Results (5 qubits, kλ_D = 0.5)
| | Damping rate γ |
|---|---|
| Landau theory (dispersion relation) | −0.1534 |
| **Quantum circuit (2nd-order Trotter)** | **−0.1538** |

The circuit tracks theory within 5% across kλ_D = 0.3–0.7 (`figures/2_damping_vs_wavenumber.png`).

**Novelty:** a stability classifier answers a reactor controller's yes/no question ("does this ripple fade before the magnets could react?") from a few measured probabilities. It never reads out the full quantum state, and that full readout is the bottleneck that limits most quantum PDE solvers.

## Approach (Engel, Smith & Parker, 2019)
1. Linearise the 1D1V Vlasov–Ampère equations for one Fourier mode `k`.
2. Rescale by `sqrt(F0)` and discretise velocity, so the system becomes `dψ/dt = −iHψ` with Hermitian `H`.
3. Encode `ψ = (E, u_1 … u_Nv)` in `n` qubits (`N_v = 2^n − 1`).
4. Evolve with a Suzuki–Trotter circuit. `|E(t)|²` is the probability of measuring `|0…0⟩`.

## Run (VS Code)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main        # prints results and writes figures/*.png (about 20 s)
python -m pytest          # 8 tests
```
Or open `src/main.py` and click **Run Python File**. Select the `.venv` interpreter first.

## Layout
| Path | Purpose |
|---|---|
| `src/config.py` | All parameters; conversion to SI units |
| `src/hamiltonian.py` | Build H and the Gauss-consistent initial state |
| `src/theory.py` | Textbook Landau damping rate (the answer we check against) |
| `src/circuits.py` | State preparation and Trotter-step circuits |
| `src/simulate.py` | Run circuits, fit γ, stability classifier |
| `src/resources.py` | Qubit, CNOT and depth counts; classical vs quantum memory |
| `src/plots.py` | All slide figures |
| `src/main.py` | The demo: runs every step in order |
| `tests/` | Physics and correctness tests |
| `archive/` | Parked classical simulation code (not used right now) |
| `docs/learn/` | Learning guide: physics, maths, code, Q&A |
| `figures/` | Exported plots for slides |
