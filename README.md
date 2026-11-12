# Plasma Projector: simulating a fading plasma wave on a quantum computer

**Question:** can a quantum computer simulate *Landau damping* (a plasma wave fading without collisions) more efficiently than a normal computer, and what stops it helping fusion reactors today?

**New here?** Read [docs/learn/00_reading_order.md](docs/learn/00_reading_order.md). No physics background needed.

## The idea
Fusion plasma is full of ripples. Some fade, some grow and damage the reactor. We turn the equations for one ripple into a matrix, store its state in 5 qubits, and step it forward with a quantum circuit. The probability of measuring `00000` is the wave's energy, so watching it shows the wave fade. We check the fade rate against the textbook.

## Results (5 qubits, wavenumber 0.5)
| Source | Damping rate (per plasma tick; negative = fading) |
|---|---|
| Textbook formula | −0.1534 |
| **Quantum circuit** | **−0.1538** |

Within 5% across wavenumbers 0.3–0.7 (`figures/2_damping_vs_wavenumber.png`).

**What's new:** a *stability classifier* that answers a reactor controller's yes/no question ("will this ripple fade before the magnets could react?") from a few measured probabilities, avoiding the slow full readout of the quantum state.

## Run (VS Code, Windows)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main        # prints results, writes figures/*.png (~20 s)
python -m pytest          # 8 tests
```

## Layout
| Path | Purpose |
|---|---|
| `src/config.py` | All settings; conversion to real units |
| `src/hamiltonian.py` | The matrix that drives the simulation, and the starting state |
| `src/theory.py` | Textbook damping rate we check against |
| `src/circuits.py` | Quantum circuits (load state, one time step) |
| `src/simulate.py` | Run circuits, fit the damping rate, stability classifier |
| `src/resources.py` | Gate counts; classical vs quantum memory |
| `src/plots.py` | Slide figures |
| `src/main.py` | The demo, runs everything in order |
| `tests/` | Correctness and physics checks |
| `archive/` | Parked classical simulation |
| `docs/learn/` | Learning guide |
