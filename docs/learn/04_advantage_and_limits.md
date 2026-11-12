# 4. Quantum advantage: the honest version

Code: `src/resources.py`, `src/theory.py`. Figure: `figures/3_resources.png`.

## Where the advantage comes from: memory
A kinetic simulation stores f on a phase-space grid. With N points per axis:

| Model | Classical numbers stored | Qubits |
|---|---|---|
| 1D1V (our demo), N = 32 | 32² ≈ 10³ | 10 (we use 5, because only 1 Fourier mode is needed in x) |
| 3D3V reactor, N = 128 | 128⁶ ≈ **4×10¹²** (≈ 70 TB of complex numbers) | **42** |
| 3D3V, N = 1024 | 10¹⁸ (more than any supercomputer) | 60 |

Classical memory is **exponential in the number of qubits'-worth of information**, and quantum memory is linear. This is the "memory wall" the pitch talks about.

## Where it's harder: gates (be upfront about this)
Our generic circuit decomposes H into Pauli strings. We measured (one Trotter step, transpiled to CNOT/RZ/SX/X):

| qubits | Pauli terms | CNOTs/step | depth/step |
|---|---|---|---|
| 3 | 30 | 124 | 272 |
| 5 | 510 | 2,516 | 5,099 |
| 7 | 7,422 | 37,480 | 75,172 |

This grows like **4ⁿ**, which would wipe out the advantage. It's the honest weakness of the generic approach, but it's **fixable because H has structure**:
- **Diagonal part k·v_j:** v_j is evenly spaced, so it's linear in the basis-state index j = Σ 2ᵐ bₘ. That means it's a sum of single-qubit Z terms: about **n RZ gates**, plus one multi-controlled phase to zero out the E slot.
- **Coupling row/column:** this is a rank-2 operator, a rotation between |0…0⟩ and the Gaussian-shaped vector |a⟩. You implement it with one Gaussian state preparation (poly(n) gates) and its inverse.
- **Total:** poly(n) gates per step instead of 4ⁿ. Engel et al. (2019) show this sparse-Hamiltonian scaling formally. Implementing it is our roadmap item.

## Where it's hardest: readout
Amplitudes can't be read directly. Reading the full state (to see f(v)) needs about 2ⁿ shots, which destroys the speedup. **This is why our stability classifier asks for one probability only.** The cost is then:
- Plain sampling: O(1/ε²) shots for precision ε, independent of grid size.
- Amplitude estimation: O(1/ε). This is the quadratic improvement over sampling.

## Putting it together (for Susan's scaling slide)
- **Classical** explicit 3D3V kinetic solver: O(N⁶) memory and O(N⁶) work per step.
- **Quantum (structured):** O(log N) qubits, poly(log N) gates per step, and O(1/ε) repetitions for a yes/no answer.
- This is an exponential separation in memory and gates **for this specific query**, not for "simulate everything".
- **Caveat:** quantum advantage claims for linear PDEs are an active research area. Classical tricks (reduced models, low-rank tensor methods) can also compress phase space. Say this; judges respect it.

## Viability (hardware reality check)
- Today's best devices: about 100–1,000 noisy qubits, and about 10³–10⁴ CNOTs before noise dominates.
- Our 5-qubit demo needs about 2,500 CNOTs **per step** × 200 steps, so it's not runnable on today's hardware. Even the structured version needs error correction for reactor-scale runs.
- Realistic timeline: early fault-tolerant machines (about 2030+). This is why the field focuses on resource estimates now.

## Classical benchmark (currently parked in `archive/`)
- `src/theory.py` → `landau_root`: the exact textbook answer from the plasma dispersion function, which we use to validate. This is a formula, not a simulation, so it stays.
- `archive/classical_simulation.py` → `classical_solve`: a normal ODE solver. It took about 20 ms for our 1D1V problem. **Classical computers win easily at this size.** The demo is a correctness proof of the quantum algorithm, not a speed race. The advantage only appears at 3D3V reactor scale, where classical memory explodes.

## Likely judge questions
| Question | Answer |
|---|---|
| "Isn't 1D Landau damping trivial classically?" | Yes. It's our validation case with a known exact answer. The scaling argument targets 3D3V. |
| "Your gate count grows 4ⁿ." | That's the generic Pauli decomposition. H is an arrowhead with a linear diagonal, so the structured circuit is poly(n). That's on the roadmap. |
| "How do you read the answer?" | We don't read the state. We ask one yes/no question, which costs O(1/ε) with amplitude estimation, independent of grid size. |
| "What about instabilities that grow?" | A non-Maxwellian F0 makes H non-Hermitian. Methods exist for this (Schrödingerisation, linear combination of Hamiltonian simulations), and they're the next step. |
| "Why Ampère instead of Poisson for E?" | Ampère gives a time-evolution equation for E, which makes the whole system a single dψ/dt = −iHψ. Gauss's law is then preserved automatically if the initial state satisfies it. |
| "Noise?" | Current devices can't run it. We give resource estimates for fault-tolerant hardware instead of claiming a demo on noisy qubits. |
