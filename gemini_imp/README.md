# Tokamak Plasma Wave Simulation: Quantum Circuit vs. Conventional Computer (`gemini_imp`)

A beginner-friendly, modular **Quantum (Qiskit)** vs. **Conventional (SciPy)** plasma wave simulation built so anyone—**with zero physics or quantum computing background**—can immediately see:
1. **What the problem is** (keeping a nuclear fusion reactor stable).
2. **What the quantum circuit is doing** (taking physical factors $\rightarrow$ encoding them into qubits $\rightarrow$ evolving them with quantum gates $\rightarrow$ reading out probabilities $\rightarrow$ graphing the wave).
3. **Whether a quantum computer is genuinely better than a regular computer** (comparing memory compression, hardware-independent operation counts, and our **Fast Arrowhead Circuit** optimization).

---

## Quick Navigation

- [1. What Is the Problem? (Plain-English Physics)](#1-what-is-the-problem-plain-english-physics)
- [2. What Is the Quantum Circuit Doing? (Input Factors $\rightarrow$ Qubits $\rightarrow$ Output Graphs)](#2-what-is-the-quantum-circuit-doing-input-factors--qubits--output-graphs)
- [3. Is the Quantum Circuit Actually Better Than a Regular Computer?](#3-is-the-quantum-circuit-actually-better-than-a-regular-computer)
- [4. Visual Guide to the 5 Generated Graphs](#4-visual-guide-to-the-5-generated-graphs)
- [5. File Map & Code Walkthrough (Sections 1–5)](#5-file-map--code-walkthrough-sections-15)
  - [Section 1: Physical Factors & Scenarios (`config.py`)](#section-1-physical-factors--scenarios-configpy)
  - [Section 2: Encoding Physics into Qubits & the Arrowhead Matrix (`hamiltonian.py`)](#section-2-encoding-physics-into-qubits--the-arrowhead-matrix-hamiltonianpy)
  - [Section 3: Running the Quantum Circuit vs. Classical Algorithm (`simulation.py`)](#section-3-running-the-quantum-circuit-vs-classical-algorithm-simulationpy)
  - [Section 4: Measuring How Fast the Wave Fades (`analysis.py`)](#section-4-measuring-how-fast-the-wave-fades-analysispy)
  - [Section 5: Graphing the Results (`plotting.py`)](#section-5-graphing-the-results-plottingpy)
- [6. How to Run](#6-how-to-run)
- [7. Plain-English Glossary](#7-plain-english-glossary)

---

## 1. What Is the Problem? (Plain-English Physics)

In a **tokamak** nuclear fusion reactor, we trap super-hot charged gas (**plasma**) inside a magnetic bottle at over 100 million degrees. Because electrons are negatively charged, whenever a crowd of electrons bunches up in one spot, they push each other apart via an **electric field**, overshoot like a stretched spring, and slosh back and forth. This sloshing is a **plasma wave** (an electric ripple).

When a ripple forms inside a fusion reactor, one of two things happens:
- **Dangerous Case (Instability):** The ripple grows larger and throws hot plasma into the reactor walls, shutting down fusion.
- **Safe Case (Landau Damping):** The ripple naturally fades away on its own, *even when electrons never collide with each other*.

### Why Does the Wave Fade Without Collisions? (The Surfer Analogy)
Imagine ocean waves and surfers paddling at different speeds:
- A surfer moving **slightly slower** than a wave gets caught and pushed forward—**stealing energy from the wave**.
- A surfer moving **slightly faster** than a wave pushes against the back of the wave—**giving energy to the wave**.
- In a warm plasma, electron speeds follow a **bell curve** (many slow electrons, fewer fast ones). That means at the wave's speed, there are always **more slightly-slower electrons than slightly-faster ones**. Net result: the electrons absorb the wave's electric field energy, and the ripple fades away (**Landau damping**).

---

## 2. What Is the Quantum Circuit Doing? (Input Factors $\rightarrow$ Qubits $\rightarrow$ Output Graphs)

```mermaid
flowchart LR
    A["1. Input Factors\n- Wavenumber (k)\n- Temperature (T)\n- Density (n_e)"] --> B["2. Load 5 Qubits (32 Slots)\n- Slot 0 (|00000⟩): Electric Field\n- Slots 1..31: Velocity Buckets"]
    B --> C["3. Fast Arrowhead Circuit\n- Diagonal: 5 RZ Gates (0 CNOTs)\n- Arrow: Field-Velocity Coupling\n- Repeat for 200 Time Steps"]
    C --> D["4. Read Out Qubits\n- Measure P(|00000⟩)\n- 2,000 Hardware Shots\n- Fit Wave Decay Rate"]
    D --> E["5. Output Graphs\n- 1a: Quantum Scenarios\n- 1b: Classical Scenarios\n- 1, 2, 3: Comparisons"]
```

### Step-by-Step Pipeline:
1. **Takes 3 Physical Factors (`config.py`):**
   - **Wavenumber ($k$):** How tightly packed the wave crests are ($k = 2\pi / \text{wavelength}$). Higher $k$ = shorter wave = more electrons can surf it = **fades faster**.
   - **Temperature ($T$):** How hot/fast the electrons are. Higher $T$ = wider bell curve of speeds = more fast electrons available to steal wave energy = **fades faster**.
   - **Density ($n_e$):** How tightly packed the electrons are (controls how fast the electric field and electrons push each other).
2. **Stores the Plasma in 5 Qubits (`hamiltonian.py`):**
   - While 5 regular bits can only hold *one* number from `0` to `31` at a time, **5 qubits** in superposition hold **$2^5 = 32$ complex numbers simultaneously**:
     - **Slot `0` (binary `|00000⟩`):** Holds the wave's **Electric Field ($E$)**.
     - **Slots `1` to `31` (`|00001⟩` to `|11111⟩`):** Hold **31 electron velocity buckets** evenly spaced from `-6` to `+6`.
3. **Computes Time Evolution Using Our Fast Arrowhead Circuit (`simulation.py`):**
   - Physics rules say that in each small time step ($\Delta t = 0.1$), two things happen:
     1. **Electrons coast at their own speed** (diagonal of the matrix $H$).
     2. **The electric field and electrons push each other** (top row and left column of $H$, making an **"arrowhead" matrix**).
   - Our quantum circuit applies those two rules 200 times (`n_steps = 200`) using quantum gates (`RZ` rotations and `CNOT` entangling gates).
4. **Reads Out the Answer & Graphs It (`analysis.py` & `plotting.py`):**
   - When you measure the qubits at the end of a run, the probability of all 5 qubits reading zero (`00000`) equals $|\text{state}[0]|^2$, which is the **Electric Field Energy** of the wave!
   - Running the circuit **2,000 times ("shots")** and counting how often `00000` appears gives the realistic hardware measurement.
   - Tracking the peaks of that energy over time gives the **damping rate** (how fast the wave fades).

---

## 3. Is the Quantum Circuit Actually Better Than a Regular Computer?

To answer the research question honestly and scientifically, we solved two major benchmarking problems in `simulation.py`:

### Fix 1 (Problem 2): Fair Hardware-Independent Efficiency Comparison
Why can't you just compare Python runtime (`time.perf_counter()`) between Qiskit and SciPy on a laptop? Because **your laptop is a classical CPU pretending to be a quantum computer**! Simulating qubits on a regular CPU takes exponentially more work than running on real quantum hardware.
- **How we fixed it:** Instead of comparing laptop wall-clock seconds, `simulation.py` counts **hardware-independent operations**:
  - **Conventional Computer Cost:** Uses a **sparse matrix (`scipy.sparse.csr_matrix`)**—which skips all the zeros in the arrowhead matrix just like a real high-performance classical solver—and counts exact **Floating-Point Operations (`FLOPs`)** performed by the Runge-Kutta (`RK45`) solver.
  - **Quantum Computer Cost:** Compiles the circuit into real superconducting hardware gates (`cx`, `rz`, `sx`, `x`), counts **2-Qubit `CNOT` Gates** and **Sequential Circuit Depth**, and estimates real **Quantum Processor (QPU) execution time** (at ~50 nanoseconds per gate layer).

### Fix 2 (Problem 3): The Fast Arrowhead Quantum Circuit (Up to 13.7× Fewer CNOT Gates!)
Originally, converting the $2^n \times 2^n$ Hamiltonian matrix $H$ into quantum gates using Qiskit's generic `SparsePauliOp.from_operator(H)` treated $H$ like a dense block of numbers. That required $\sim 4^n$ CNOT gates per step (`2,516` CNOTs/step at 5 qubits; `9,882` CNOTs/step at 6 qubits!), which would ruin any quantum advantage.
- **How we fixed it (`build_fast_arrowhead_step_circuit` in `simulation.py`):**
  We exploited the **Arrowhead structure** of $H = H_{\text{diag}} + H_{\text{arrow}}$:
  1. **Diagonal Coasting ($H_{\text{diag}}$):** Because velocity $v_j$ is evenly spaced, each qubit $m$ simply rotates by angle $-k \, \Delta v \, 2^m \Delta t$ using **one single-qubit `RZ` gate** (**zero CNOTs** for the velocity ramp!) plus a phase correction on `|00000⟩`.
  2. **Field-Velocity Coupling ($H_{\text{arrow}}$):** Since slot `0` only talks to one combined velocity wave $\lvert\phi\rangle$, evolution happens inside a simple **2D subspace** ($\lvert\psi_+\rangle, \lvert\psi_-\rangle$), requiring only two state-preparation reflections per step instead of $4^n$ Pauli strings.

| Qubits ($n$) | Velocity Buckets | Old Naive Pauli CNOTs/Step | **New Fast Arrowhead CNOTs/Step** | **Gate Reduction** | Classical Sparse Solver Work |
|---:|---:|---:|---:|---:|---:|
| **3 qubits** | 7 | 124 | **52** | **2.4× fewer** | 317,376 FLOPs |
| **4 qubits** | 15 | 598 | **164** | **3.6× fewer** | 732,480 FLOPs |
| **5 qubits** | 31 | 2,516 | **368** | **6.8× fewer** | 1,522,080 FLOPs |
| **6 qubits** | 63 | 9,882 | **720** | **13.7× fewer** | 3,038,496 FLOPs |

### The Final Verdict: When Should You Use a Quantum Computer?
1. **For a 1D Wave (Our 5-Qubit Demo): Regular Computer Wins.**
   In 1D, the state vector only has 32 numbers. A classical sparse solver finishes the entire 200-step simulation in under **1 million FLOPs** (~2 milliseconds on a laptop), whereas even our optimized quantum circuit needs `368 × 200 = 73,600` CNOT gates across 200 steps.
2. **For a Full 3D Fusion Reactor (`3D3V`): Quantum Computer Has a Massive Memory Advantage.**
   A real tokamak has **3 space axes $(x,y,z)$ + 3 velocity axes $(v_x,v_y,v_z)$ = 6 dimensions**.
   - At a modest grid resolution of $N = 128$ points per axis, a conventional computer must store $128^6 \approx \mathbf{4.4 \times 10^{12}}$ **numbers** (~70 Terabytes of RAM). At $N = 1024$, it needs $10^{18}$ numbers (impossible on any supercomputer).
   - A quantum computer stores the exact same $128^6$ grid in just **$6 \log_2(128) = \mathbf{42\text{ qubits}}$**!
   - **Bottom line:** Quantum computing is not needed for 1D waves today, and current quantum hardware is still too noisy for deep circuits—but once fault-tolerant quantum hardware arrives, structured arrowhead circuits make full 3D fusion simulations possible in dozens of qubits instead of petabytes of classical RAM.

---

## 4. Visual Guide to the 5 Generated Graphs

Running `python gemini_imp/plasma_simulation.py` saves five high-resolution PNG graphs in `gemini_imp/figures/`:

| Graph File | What It Shows | Why It Matters for Your Presentation |
|---|---|---|
| **`1a_quantum_circuit_scenarios.png`** | **Quantum Circuit Outputs Across 3 Tokamak Scenarios** (Scenario A: Gentle Wave $k=0.35, T=0.8$; Scenario B: Baseline $k=0.50, T=1.0$; Scenario C: Short Wave in Hot Plasma $k=0.65, T=1.3$). | Shows the quantum circuit (blue/green/orange curves + 2,000-shot hardware dots) accurately capturing slow, medium, and fast wave damping. |
| **`1b_classical_algorithm_scenarios.png`** | **Conventional Algorithm Outputs Across the Same 3 Scenarios** on the exact same vertical & horizontal scales as `1a`. | Placing `1a` and `1b` side-by-side lets anyone visually verify that the 5-qubit quantum circuit reproduces the conventional solver across different reactor conditions! |
| **`1_quantum_vs_classical_wave.png`** | **Direct Overlay on the Baseline Wave** (Classical Sparse RK45 vs. 5-Qubit Fast Arrowhead Circuit vs. 2,000 Hardware Shots). | Proves that the quantum curve lies right on top of the classical curve (both give damping rate $\gamma \approx -0.154$). |
| **`2_factors_affecting_plasma.png`** | **How Physical Factors Change Damping Speed:** Sweeps Wavenumber ($k \in [0.3, 0.7]$) in Panel A and Temperature ($T \in [0.6, 1.6]$) in Panel B. | Visually answers the first half of the research question: shorter waves (higher $k$) and hotter plasmas (higher $T$) both cause the wave to fade faster. |
| **`3_quantum_vs_classical_scaling.png`** | **3-Panel Efficiency & Viability Benchmark:** (1) 3D Reactor Memory Compression ($N^6$ vs. $6\log_2 N$), (2) Problem 3 Fix (Fast Arrowhead vs. Naive Pauli CNOTs), (3) Problem 2 Fair Operations Count (Classical FLOPs vs. Quantum CNOTs). | Directly answers the second half of the research question with quantitative proof. |

---

## 5. File Map & Code Walkthrough (Sections 1–5)

| Step | Python File | What It Owns | Key Functions / Constants |
|---|---|---|---|
| **1** | [`config.py`](config.py) | Physical parameters, 3 tokamak scenarios, velocity grid | `DEFAULT_CONFIG`, `SCENARIOS`, `make_velocity_grid` |
| **2** | [`hamiltonian.py`](hamiltonian.py) | Maxwellian bell curve, Arrowhead matrix $H$, Gauss's law start state | `maxwellian_bell_curve`, `build_hamiltonian_matrix`, `create_initial_qubit_state` |
| **3** | [`simulation.py`](simulation.py) | Fast Arrowhead circuit, Naive Pauli circuit, Sparse RK45 solver, FLOPs/gate benchmarks | `build_fast_arrowhead_step_circuit`, `run_quantum_simulation`, `run_classical_simulation`, `benchmark_efficiency_scaling` |
| **4** | [`analysis.py`](analysis.py) | Peak detection & log-linear damping rate fit before fake revival | `measure_damping_rate` |
| **5** | [`plotting.py`](plotting.py) | Generates all 5 PNG charts in `gemini_imp/figures/` | `plot_separate_scenario_graphs`, `plot_figure_1_quantum_vs_classical`, `plot_figure_2_factors_comparison`, `plot_figure_3_quantum_vs_classical_viability` |
| **6** | [`plasma_simulation.py`](plasma_simulation.py) | Main script that runs Steps 1–4 and prints clear terminal output | `main` |

---

### Section 1: Physical Factors & Scenarios (`config.py`)
- Defines `DEFAULT_CONFIG` (`n_qubits = 5`, `wavenumber = 0.5`, `temperature = 1.0`, `density = 1.0`, `max_velocity = 6.0`, `end_time = 20.0`, `n_steps = 200`).
- Defines `SCENARIOS` (Scenarios A, B, and C) so we can test the quantum circuit and classical solver across slow, moderate, and fast damping conditions.
- `make_velocity_grid(n_qubits, max_velocity)` reserves Slot `0` for the electric field and splits `[-6.0, +6.0]` into $2^n - 1 = 31$ evenly spaced velocity buckets (`dv` is the gap between buckets).

### Section 2: Encoding Physics into Qubits & the Arrowhead Matrix (`hamiltonian.py`)
- **`maxwellian_bell_curve(velocities, temperature)`:** Computes the bell-curve spread of electron speeds:
  $$f_0(v) = \frac{1}{\sqrt{2\pi T}} \exp\left(-\frac{v^2}{2T}\right)$$
- **`build_hamiltonian_matrix(config)`:** Quantum gates can only apply **unitary** updates $\text{new\_state} = \exp(-i H \Delta t)\,\text{old\_state}$ where $H$ is a symmetric (**Hermitian**) matrix. Rescaling the velocity buckets turns the plasma equations into a $32 \times 32$ **Arrowhead Matrix**:
  - **Diagonal `H[j, j] = k * v_j`:** Electrons coasting at velocity $v_j$.
  - **Top Row `H[0, j] = +i * coupling_j`:** Moving electrons generating current that updates the electric field in Slot `0`.
  - **Left Column `H[j, 0] = -i * coupling_j`:** Electric field pushing velocity bucket $j$, where $\text{coupling}_j = \sqrt{n_e}\, v_j \sqrt{f_0(v_j)\,\Delta v}$.
- **`create_initial_qubit_state(config)`:** Builds the starting state at $t=0$ obeying **Gauss's Law** ($E_0 = \frac{i}{k}\sum f_0(v_j)\Delta v$) and divides by `np.linalg.norm` so the squared qubit amplitudes sum to `1.0` (100% probability).

### Section 3: Running the Quantum Circuit vs. Classical Algorithm (`simulation.py`)
- **`build_diagonal_circuit` & `build_arrow_circuit` (Problem 3 Fix):**
  - Instead of decomposing $H$ into $\sim 4^n$ Pauli strings, `build_fast_arrowhead_step_circuit` uses a 2nd-order Suzuki-Trotter split:
    $$\exp(-i H \Delta t) \approx \exp\left(-i H_{\text{diag}} \frac{\Delta t}{2}\right) \exp(-i H_{\text{arrow}} \Delta t) \exp\left(-i H_{\text{diag}} \frac{\Delta t}{2}\right)$$
  - Because $v_j$ is linear in the binary bits of index $j$, $\exp(-i H_{\text{diag}} \Delta t/2)$ takes just **1 single-qubit `RZ` gate per qubit** plus a zero-state phase correction.
  - Because $H_{\text{arrow}}$ only couples Slot `0` to a single collective velocity state $\lvert\phi\rangle$, $\exp(-i H_{\text{arrow}} \Delta t)$ is implemented exactly in the 2D subspace spanned by its two eigenstates $\lvert\psi_\pm\rangle = (\lvert 0\rangle \mp i\lvert\phi\rangle)/\sqrt{2}$.
- **`run_quantum_simulation(config)`:** Prepares the initial state with Qiskit's `StatePreparation`, evolves 200 steps, reads out Slot `0` probability $|\text{state}[0]|^2$, simulates `2,000` hardware measurement shots via a binomial draw, and records transpiled `CNOT` gate counts, circuit depth, and estimated superconducting QPU time.
- **`run_classical_simulation(config)`:** Converts $H$ into a sparse `csr_matrix`, solves $\frac{d(\text{state})}{dt} = -i H \cdot \text{state}$ with `scipy.integrate.solve_ivp` (`RK45`), and computes exact classical floating-point operations (`total_flops = rhs_evaluations * nnz * 8`).

### Section 4: Measuring How Fast the Wave Fades (`analysis.py`)
- Because velocity is split into discrete buckets of width $\Delta v$, after the **fake revival time** $t_{\text{revival}} = \frac{2\pi}{k \cdot \Delta v}$ the discrete buckets drift back into phase and create an artificial echo.
- `measure_damping_rate` finds oscillation peaks safely before $0.8 \times t_{\text{revival}}$, fits a straight line to $\ln(\text{Peak Energy})$ vs. time $t$, and divides the slope by `2` (since $\text{Energy} = |E|^2 \propto e^{2\gamma t}$) to get the Landau damping rate $\gamma$.

### Section 5: Graphing the Results (`plotting.py`)
- Generates all 5 figures (`1a`, `1b`, `1`, `2`, `3`) using Matplotlib's `Agg` backend so it runs cleanly from any terminal without popping up blocking windows.

---

## 6. How to Run

From the repository root:

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python gemini_imp/plasma_simulation.py

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python gemini_imp/plasma_simulation.py
```

---

## 7. Plain-English Glossary

| Term | Plain-English Meaning |
|---|---|
| **Tokamak** | A donut-shaped magnetic bottle used to trap hot plasma for nuclear fusion. |
| **Landau Damping** | When a plasma wave fades away on its own because slightly-slower electrons "surf" the wave and steal its energy—without any particle collisions. |
| **Wavenumber ($k$)** | $2\pi / \text{wavelength}$ — how tightly packed the wave crests are. Higher $k$ = shorter wave = fades faster. |
| **Qubit Superposition** | $n$ qubits hold $2^n$ complex numbers (amplitudes) at once. 5 qubits hold 32 slots (`00000` to `11111`). |
| **Arrowhead Matrix ($H$)** | Our $32 \times 32$ physics matrix that only has numbers on the diagonal (coasting electrons) plus Row 0 and Column 0 (electric field coupling), with zeros everywhere else. |
| **Suzuki-Trotter Step** | Splitting a combined physics update into alternating simpler gate steps ($\text{Diag}(\Delta t/2) \rightarrow \text{Arrow}(\Delta t) \rightarrow \text{Diag}(\Delta t/2)$). |
| **Hardware Shots** | Running the quantum circuit 2,000 times and counting how often `00000` is measured to estimate the wave's electric field energy. |
| **FLOPs vs. CNOTs** | Fair, hardware-independent ways to count work: Floating-Point Operations (`FLOPs`) on a regular computer vs. 2-qubit entangling gates (`CNOTs`) on a quantum computer. |
