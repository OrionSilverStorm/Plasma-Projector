# Start here

Read in order (~1 hour), with the matching code open.

| # | Doc | Covers | Code |
|---|---|---|---|
| 1 | [01_plasma_and_landau.md](01_plasma_and_landau.md) | What a plasma wave is and why it fades | none |
| 2 | [02_equation_to_qubits.md](02_equation_to_qubits.md) | Equations → matrix → qubits | `config.py`, `hamiltonian.py` |
| 3 | [03_circuits_and_trotter.md](03_circuits_and_trotter.md) | Circuits, and reading the answer out | `circuits.py`, `simulate.py` |
| 4 | [04_advantage_and_limits.md](04_advantage_and_limits.md) | Where quantum wins and loses; judge Q&A | `resources.py`, `theory.py` |
| 5 | [05_code_walkthrough.md](05_code_walkthrough.md) | The program in run order, plus experiments | all |
| 6 | [reading_list.md](reading_list.md) | Papers | none |

## Maths toolkit
1. **Rate of change.** `dx/dt = −0.5·x` is an update rule: each small step `dt`, do `x += dt * (−0.5 * x)`. Looping it is a simulation.
2. **Complex numbers.** `a + bi` is a 2D point with a size (`abs(z)`) and an angle (*phase*). Multiplying by `e^{−iθ}` rotates it by θ without changing its size. Waves use complex numbers because they spin.
3. **Exponentials.** `e^{γt}` shrinks if γ < 0. On a log-scale plot it's a straight line with slope γ, which is how we measure the damping rate.
4. **Matrix update rule.** `dψ/dt = −iHψ`: every entry of vector ψ changes by a fixed mix of all entries, given by matrix H. The solution is `ψ(t) = e^{−iHt}ψ(0)`, where `e^{−iHt}` (the *matrix exponential*, `scipy.linalg.expm`) means "apply the rule in tiny steps until time t".
5. **Qubits.** n qubits hold 2ⁿ complex *amplitudes* (5 → 32). Measuring gives one bit-string; outcome i has probability `|amplitude_i|²`, so the vector always has length 1. Gates rotate the vector without changing its length.

## Glossary (code name / physics symbol)
| Term | Meaning |
|---|---|
| **Plasma** | Gas hot enough that electrons leave their atoms: a mix of free charged particles. |
| **Electric field** (`field` / E) | The push a charge feels. Clumps of electrons create it; it pushes other electrons. |
| **Plasma frequency** (`plasma_frequency` / ω_p) | How fast displaced electrons bounce back and forth. |
| **Plasma tick** (1/ω_p) | Our time unit. One full bounce ≈ 6.3 ticks; in a reactor 1 tick ≈ 1.8 ps. |
| **Thermal speed** (`thermal_speed` / v_th) | Typical electron speed. Our speed unit. |
| **Screening length** (`screening_length` / λ_D) | Distance beyond which a charge is hidden by charges crowding round it. Our length unit. |
| **Wavenumber** (`wavenumber` / kλ_D) | 2π ÷ wavelength, in screening lengths. Bigger = shorter wave. The only physics input. |
| **Background** (`background_distribution` / F0) | Bell-curve histogram of electron speeds in calm plasma. |
| **Ripple** (f₁) | Small disturbance on top of the background: the wave we simulate. |
| **Landau damping** | A wave fading by giving energy to electrons moving at about its speed. No collisions. |
| **Damping rate** (γ) | Wave size shrinks like e^{γt}; negative = fading. |
| **Oscillation rate** (ω) | How fast the wave wiggles, radians per tick. |
| **1D1V / 3D3V** | Position axes + velocity axes. Our demo: 1+1. A reactor: 3+3. |
| **Hamiltonian** (`hamiltonian` / H) | The matrix H in `dψ/dt = −iHψ`. |
| **Hermitian** | Equals its conjugate transpose. Guarantees `e^{−iHt}` keeps length, so a quantum computer can apply it. |
| **Unitary** | Length-preserving matrix. Every gate is one. |
| **Pauli strings** | Building-block matrices like `XZI`. Any matrix is a weighted sum of them, and each is easy to build from gates. |
| **Trotterisation** | Approximating "apply A and B together" by alternating tiny steps of each. |
| **Fake revival time** (`fake_revival_time` / T_R) | When the velocity grid makes the wave falsely reappear. Results after it are wrong. |
| **Transpile** | Compile a circuit to hardware gates (CNOT, RZ, SX, X). |
| **CNOT count / depth** | Hardware cost. CNOTs are the error-prone gates; depth is layers run in sequence. |
| **Shots** | Repeated runs of a circuit; probabilities are estimated by counting outcomes. |
