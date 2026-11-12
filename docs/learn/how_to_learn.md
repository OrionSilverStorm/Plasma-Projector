# How to learn this project

**Don't read the code top to bottom.** Follow the data through the program, one stage at a time:

> read a short doc section → read the matching code → run it and look at the actual numbers

Total time: about 3 hours. Do Passes 1–2 on day one and Passes 3–5 on day two.

---

## Pass 1: big picture (30 min)
- [ ] Run `python -m src.main` and keep the printed output open. You'll refer back to it.
- [ ] Read [00_reading_order.md](00_reading_order.md) (glossary) and [01_plasma_and_landau.md](01_plasma_and_landau.md) (physics only, no code).
- [ ] Open the 4 PNGs in `figures/`. For each one, say out loud in one sentence what it shows. If you can't, write that down; it's what to look for in Pass 2.

## Pass 2: follow the data (about 2 hours)
Do each row in order. Don't move on until you can answer the question in the last column.

| Read | Then open | Check yourself by answering |
|---|---|---|
| [doc 02](02_equation_to_qubits.md), steps 0–2 | `src/config.py` | Why is `n_v` equal to `2**n - 1` and not `2**n`? |
| [doc 02](02_equation_to_qubits.md), steps 3–7 | `src/hamiltonian.py` | Which 3 lines are the whole physics model? Why does row 0 have `+1j` and column 0 have `-1j`? |
| [doc 03](03_circuits_and_trotter.md), parts 1–3 | `src/circuits.py` | What would go wrong without `.decompose()`? |
| [doc 03](03_circuits_and_trotter.md), fit + classifier | `src/simulate.py` | Why do we fit the peaks and not every point? Why does the classifier measure across a window? |
| [doc 04](04_advantage_and_limits.md) | `src/resources.py`, `src/theory.py` | Where does 4ⁿ come from, and why is that a weakness rather than the advantage? |
| [doc 05](05_code_walkthrough.md) | `src/main.py` | Can you match each printed line to the function that produced it? |

## Pass 3: watch it run in the VS Code debugger (30 min)
This is the fastest way to *see* what's happening:
1. In `src/main.py`, click left of the line number on `quantum = field_energy(run_quantum(p))` to set a breakpoint (red dot).
2. Press **F5** and choose **Python File**.
3. Press **F11 (Step Into)** to enter `run_quantum`, then again to enter `build_hamiltonian`.
4. Once the variables exist, type these into the **Debug Console**:
   ```python
   H.shape                       # (32, 32): 5 qubits hold 32 numbers
   np.round(H[:4, :4], 3)        # the "arrowhead": diagonal + row 0 + column 0
   np.allclose(H, H.conj().T)    # True means Hermitian, so it can run on a quantum computer
   abs(psi)**2                   # probability of each qubit outcome; index 0 is |E|^2
   ```
5. Step past `U = Operator(...)` and check `U.shape`. That one 32×32 matrix *is* the circuit for one time step.

## Pass 4: break things on purpose (30 min)
Do the 4 experiments at the end of [doc 05](05_code_walkthrough.md).
- **Before** each one, write your prediction of what will change.
- Run it and compare. If you were wrong, re-read the linked doc section. That gap is exactly what you didn't understand yet.
- Undo each change afterwards with `git checkout -- <file>` (once the code is committed), or with Ctrl+Z.

## Pass 5: prove you've got it (15 min)
Explain each of these out loud without notes. They're also the questions judges are likely to ask.
- [ ] How does a plasma equation become a quantum state? Answer in 3 sentences.
- [ ] Why does |E|² equal the probability of measuring `|00000⟩`?
- [ ] Why must the starting state obey Gauss's law? What happens if it doesn't?
- [ ] Where does the quantum advantage come from, and what's the honest catch? (Memory vs gates vs readout.)
- [ ] What does the stability classifier do, and why is it our novel contribution?

<details>
<summary>Answers (check yours after trying)</summary>

1. We linearise the Vlasov equation for one wave, put velocity on a grid and rescale by √F0. That turns it into dψ/dt = −iHψ with a Hermitian H. The list ψ = (E, u₁…u₃₁) is stored as the 32 amplitudes of 5 qubits.
2. E is stored in entry 0 of ψ, which is the amplitude of the basis state |00000⟩. Measuring gives an outcome with probability |amplitude|², so P(|00000⟩) = |E|².
3. Gauss's law ties the field to the charge ripple. If you break it, the equations carry a constant field that never decays, so |E|² plateaus instead of damping (experiment 2 in doc 05).
4. Memory: N⁶ numbers classically vs about 6·log₂N qubits for a 3D3V reactor. The catches: our generic circuit costs about 4ⁿ gates (fixable using H's structure, which is roadmap work), and reading out the full state costs about 2ⁿ shots.
5. It answers a controller's yes/no question ("does this ripple fade before the magnets could react?") from a few measured probabilities. That avoids the full-readout bottleneck, so the cost doesn't depend on grid size.
</details>

---

## Tips
- **You don't need to derive everything.** For the pitch, know *why* each step exists. `theory.py` (the plasma dispersion function) can stay a black box: "the textbook answer".
- **Qiskit internals can stay a black box too.** Know what `SparsePauliOp`, `PauliEvolutionGate` and `StatePreparation` *do*, not how they work inside.
- **Stuck on a line?** Ask Claude Code something like "explain `fit_damping_rate` with the actual numbers" or "why √F0?".
