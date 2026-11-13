# Asad's Implementation (`gemini_imp`)

A modular Quantum (Qiskit) vs. Classical (SciPy) plasma wave simulation written for clarity, direct benchmarking, and presentation-ready explanations—no physics or quantum background required.

> **Navigation Tip:** Every Python file in `gemini_imp/` stays concise and focused on code. All long conceptual, physics, and math explanations live right here in this `README.md`, organized into **Sections 1–5** matching each module.

---

## Quick Navigation

- [Overview & Research Question](#overview--research-question)
- [File Map & Reading Order](#file-map--reading-order)
- [How to Run](#how-to-run)
- [Section 1: Physical Factors & Simulation Settings](#section-1-physical-factors--simulation-settings) (`config.py`)
- [Section 2: Encoding Physics into Qubits & Building the Matrix](#section-2-encoding-physics-into-qubits--building-the-matrix) (`hamiltonian.py`)
- [Section 3: Running the Simulation (Quantum vs. Classical)](#section-3-running-the-simulation-quantum-vs-classical) (`simulation.py`)
- [Section 4: Analysing Data (Measuring How Fast the Wave Fades)](#section-4-analysing-data-measuring-how-fast-the-wave-fades) (`analysis.py`)
- [Section 5: Plotting Data with Matplotlib](#section-5-plotting-data-with-matplotlib) (`plotting.py`)
- [Main Entry Point](#main-entry-point) (`plasma_simulation.py`)
- [Quick Glossary](#quick-glossary)

---

## Overview & Research Question

**Research Question:**
> *"How do various factors affect the movement of plasma in a nuclear fusion reactor, and would it be useful to simulate in a quantum computer vs. a conventional computer?"*

### What is happening in the physics?
In a nuclear fusion reactor (like a tokamak), super-hot charged gas called **plasma** is held inside a magnetic bottle. Ripples (electrostatic waves) constantly form in this plasma:
- **Safe case (Landau Damping):** Sometimes a ripple naturally gives its energy to moving electrons and fades away on its own without particle collisions.
- **Dangerous case:** Sometimes a ripple lingers or grows, crashing into the reactor wall and stopping fusion.

### What does this codebase do?
This folder simulates one plasma ripple and compares two ways of computing how it evolves over time:
1. **A Quantum Computer simulation** built with IBM's **Qiskit** library (Suzuki-Trotter quantum gates + simulated hardware measurement shots).
2. **A Conventional (Classical) Computer simulation** built with **SciPy**'s Runge-Kutta differential equation solver (`solve_ivp`), run side-by-side on every test.

### Key Differences from `src/`
- **Sweeps Multiple Physical Factors:** Explicitly includes **Wavenumber ($k$)**, **Electron Temperature ($T$)**, and **Density ($n_e$)** in the Hamiltonian matrix so you can plot how both $k$ and $T$ change plasma wave damping.
- **Direct Classical vs. Quantum Benchmark:** Runs a real classical ODE solver alongside the Qiskit Trotter circuit on every run rather than archiving the classical solver.

[Back to top](#quick-navigation)

---

## File Map & Reading Order

Read the files in **order 1 → 6** to follow the data from raw physics parameters all the way to finished charts:

| Step | Python File | README Section | What It Owns | Key Symbols |
|---|---|---|---|---|
| 1 | [config.py](config.py) | [Section 1](#section-1-physical-factors--simulation-settings) | Physical parameters & velocity grid | `DEFAULT_CONFIG`, `make_velocity_grid` |
| 2 | [hamiltonian.py](hamiltonian.py) | [Section 2](#section-2-encoding-physics-into-qubits--building-the-matrix) | Bell curve, Hamiltonian matrix $H$, initial state | `maxwellian_bell_curve`, `build_hamiltonian_matrix`, `create_initial_qubit_state` |
| 3 | [simulation.py](simulation.py) | [Section 3](#section-3-running-the-simulation-quantum-vs-classical) | Qiskit Trotter circuit & SciPy RK45 solver | `build_qiskit_step_circuit`, `run_quantum_simulation`, `run_classical_simulation` |
| 4 | [analysis.py](analysis.py) | [Section 4](#section-4-analysing-data-measuring-how-fast-the-wave-fades) | Peak detection & log-linear damping rate fit | `measure_damping_rate` |
| 5 | [plotting.py](plotting.py) | [Section 5](#section-5-plotting-data-with-matplotlib) | Generates 3 PNG charts in `gemini_imp/figures/` | `plot_figure_1_quantum_vs_classical`, `plot_figure_2_factors_comparison`, `plot_figure_3_quantum_vs_classical_viability` |
| 6 | [plasma_simulation.py](plasma_simulation.py) | [Main Entry Point](#main-entry-point) | Runs Steps 1–5 in sequence & prints summary | `main` |

> **Tip for reading code alongside this guide:** Open the Python file on one side of your editor and jump to the matching Section below to see *why* each formula and Qiskit call is written the way it is.

[Back to top](#quick-navigation)

---

## How to Run

From the **root of the repository** (with your virtual environment activated):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python gemini_imp/plasma_simulation.py
```

This prints comparison metrics and gate-scaling stats in the terminal and writes three PNG figures into `gemini_imp/figures/`:
- `1_quantum_vs_classical_wave.png` — Wave energy decay over time (Classical RK45 vs. Qiskit Statevector vs. 2,000 Quantum Hardware Shots).
- `2_factors_affecting_plasma.png` — Side-by-side comparison of how **Wavenumber ($k$)** and **Temperature ($T$)** change the wave's damping speed.
- `3_quantum_vs_classical_scaling.png` — 3D reactor memory compression ($N^6$ classical numbers vs. $6 \log_2 N$ qubits) alongside the $\sim 4^n$ CNOT gate bottleneck.

[Back to top](#quick-navigation)

---

## Section 1: Physical Factors & Simulation Settings

> **Code:** [config.py](config.py) (`DEFAULT_CONFIG`, `make_velocity_grid`)

### The Three Physical Factors
In a tokamak fusion reactor, three main physical factors control how a plasma wave behaves:

1. **Wavenumber ($k$):**
   Measures how tightly packed the wave crests are ($k = 2\pi / \text{wavelength}$).
   - Small $k$ = long, stretched-out wave.
   - Large $k$ = short, tightly packed wave (electrons surf it easily, so the wave fades faster).

2. **Temperature ($T$):**
   Controls the random "thermal speed" of electrons ($\text{thermal\_speed} = \sqrt{T}$).
   - Higher temperature = wider bell curve of electron speeds = more fast electrons available to absorb energy from the wave = the wave fades faster.

3. **Density ($n_e$):**
   How tightly packed the electrons are. Controls the "plasma frequency" ($\sqrt{n_e}$), which is how fast displaced electrons snap back and forth like a spring.

### Quantum Register Size & Velocity Grid (`make_velocity_grid`)
Alongside the physics factors, we choose our **quantum register size** (`n_qubits`):
- In quantum computing, $n$ qubits can hold an array of $2^n$ complex numbers all at once.
- With **5 qubits**, our quantum register holds $2^5 = 32$ numbers simultaneously (indices `0` to `31`).

**How we fit continuous velocity into a fixed number of qubits:**
- **Slot `0`** (binary `|00000⟩`) is reserved for the wave's **Electric Field ($E$)**.
- **Slots `1` to `2^n - 1`** (indices `1` to `31` for 5 qubits) hold buckets of electron **velocity**, evenly spaced from `-max_velocity` to `+max_velocity` using `np.linspace`.
- `dv = velocities[1] - velocities[0]` is the spacing (width) between two neighbouring velocity buckets.

*Next:* [Section 2 (`hamiltonian.py`)](#section-2-encoding-physics-into-qubits--building-the-matrix) | [Back to top](#quick-navigation)

---

## Section 2: Encoding Physics into Qubits & Building the Matrix

> **Code:** [hamiltonian.py](hamiltonian.py) (`maxwellian_bell_curve`, `build_hamiltonian_matrix`, `create_initial_qubit_state`)

How do physics equations manipulate qubits?

### Step A: The Bell Curve of Electron Speeds (`maxwellian_bell_curve`)
In a calm plasma at temperature $T$, most electrons move slowly (near $v = 0$) and very few move extremely fast. This follows a Gaussian **Maxwellian distribution**:

$$f_0(v) = \frac{1}{\sqrt{2 \pi T}} \exp\left(-\frac{v^2}{2T}\right)$$

Notice how `temperature` stretches this bell curve: higher temperature gives a wider spread of speeds.

### Step B: The Physics Equations (Linearised Vlasov-Ampère System)
When a small wave ripple disturbs the plasma, two rules govern how the state changes over time:
1. **Electron buckets (slots `1..31`):** Electrons coast at speed $v$ along the wave $k$, **and** get pushed by the electric field $E$.
2. **Electric field (slot `0`):** Moving electrons form an electric current, which changes the electric field $E$.

### Step C: Turning the Equations into a Quantum Matrix (`build_hamiltonian_matrix`)
Quantum computers can only apply **unitary** rotations of the form:

$$\text{new\_state} = \exp(-i \cdot H \cdot dt) \cdot \text{old\_state}$$

where $H$ is a symmetric (**Hermitian**) matrix of size $2^n \times 2^n$ (it equals its own conjugate transpose). By scaling each velocity bucket properly, the Vlasov-Ampère equations become a clean $32 \times 32$ "arrowhead" matrix:
- **Coupling term:** $\text{coupling}_j = \sqrt{n_e} \cdot v_j \cdot \sqrt{f_0(v_j) \cdot dv}$ (combines density $n_e$, velocity $v$, and temperature $T$ inside $f_0$).
- **Diagonal entries** `H[j, j] = k * v_j` — electrons coasting.
- **Top row** `H[0, j] = +i * coupling_j` — velocities changing the electric field.
- **Left column** `H[j, 0] = -i * coupling_j` — electric field pushing the velocities (negative conjugate mirror keeps $H$ Hermitian).

### Building the Starting State at $t = 0$ (`create_initial_qubit_state`)
Two rules must both be satisfied when building the initial array of $2^n$ amplitudes:
1. **Quantum Rule (Normalisation):** A quantum state vector **must** have total length (norm) `1.0`, because the squared magnitudes of its entries are measurement probabilities that must add up to 100%:
   $$|\text{state}[0]|^2 + |\text{state}[1]|^2 + \dots + |\text{state}[31]|^2 = 1.0$$
2. **Physics Rule (Gauss's Law):** Starting with a smooth density ripple in slots `1..31` ($\sqrt{f_0 \cdot dv}$) produces a matching initial electric field in slot `0`:
   $$E_{\text{initial}} = \frac{i}{k} \sum (f_0 \cdot dv)$$

The function concatenates `[E_initial, velocity_slots...]` and divides by `np.linalg.norm(raw_state)` to make it a valid quantum state.

*Previous:* [Section 1 (`config.py`)](#section-1-physical-factors--simulation-settings) | *Next:* [Section 3 (`simulation.py`)](#section-3-running-the-simulation-quantum-vs-classical) | [Back to top](#quick-navigation)

---

## Section 3: Running the Simulation (Quantum vs. Classical)

> **Code:** [simulation.py](simulation.py) (`build_qiskit_step_circuit`, `run_quantum_simulation`, `run_classical_simulation`)

Here we evolve our starting state forward in time from $t = 0$ to $t = 20$ using two completely different methods.

### Method 1: Quantum Simulation with Qiskit (`build_qiskit_step_circuit`, `run_quantum_simulation`)
A real quantum processor cannot multiply a $32 \times 32$ matrix directly. Instead:
1. **Pauli Decomposition:** `SparsePauliOp.from_operator(H, atol=1e-12)` breaks the matrix $H$ into a weighted sum of basic qubit flips and phase rotations called **Pauli strings** (combinations of `I`, `X`, `Y`, `Z` gates on the 5 qubits).
2. **Trotter Step Circuit:** `PauliEvolutionGate` with `SuzukiTrotter(order=2)` builds a quantum circuit for **one time step** ($dt = 0.1$) out of standard 1-qubit rotations and 2-qubit CNOT gates. Because the Pauli pieces do not commute (order matters), slicing time into steps introduces a small **Trotter approximation** error.
3. **Gate Decomposition:** `.decompose()` expands the `PauliEvolutionGate` block into actual quantum gates instead of treating it as a black-box matrix.
4. **State Preparation & Evolution:** `StatePreparation(init_array)` loads the starting plasma state into `|00000⟩`. Because every time step applies the exact same circuit gates, extracting `Operator(step_qc).data` once and multiplying it `n_steps` times gives the exact same statevector result as running a 200-step circuit.

**How outputs are extracted from qubits:**
- Slot `0` corresponds to the all-zeros qubit state `|00000⟩`.
- When you measure the qubits, the probability of getting `00000` is $|\text{state}[0]|^2$.
- Physically, $|\text{state}[0]|^2$ **is** the Electric Field Energy of the plasma wave.

**Simulating Quantum Hardware Shots:**
On real quantum hardware, you cannot read out exact probabilities directly—you run the circuit for a finite number of **shots** (here `2,000` runs). Each run outputs a single binary bitstring like `00000` or `01011`. Counting how many times `00000` appears out of 2,000 shots (`rng.binomial(n=2000, p=exact_field_energy) / 2000`) gives a realistic noisy estimate of the field energy.

### Method 2: Classical Simulation with SciPy (`run_classical_simulation`)
A conventional computer solves the differential equation directly in RAM:

$$\frac{d(\text{state})}{dt} = -i \cdot H \cdot \text{state}$$

using `scipy.integrate.solve_ivp` (an adaptive 4th/5th-order Runge-Kutta numerical integrator, `RK45`, with `rtol=1e-8`, `atol=1e-10`). Index `0` of each state gives the classical electric field energy $|\text{state}[0]|^2$ for direct accuracy and speed comparison.

*Previous:* [Section 2 (`hamiltonian.py`)](#section-2-encoding-physics-into-qubits--building-the-matrix) | *Next:* [Section 4 (`analysis.py`)](#section-4-analysing-data-measuring-how-fast-the-wave-fades) | [Back to top](#quick-navigation)

---

## Section 4: Analysing Data (Measuring How Fast the Wave Fades)

> **Code:** [analysis.py](analysis.py) (`measure_damping_rate`)

As the plasma wave sloshes back and forth, its electric field energy bounces up and down while the **peaks** shrink exponentially:

$$\text{Peak\_Energy}(t) \sim \exp(2 \gamma t)$$

### How `measure_damping_rate` extracts $\gamma$
1. **Avoid the Fake Mathematical Echo (`fake_revival_time`):** Because velocity is split into discrete buckets of spacing $dv$, after $t_{\text{revival}} = \frac{2\pi}{k \cdot dv}$ the grid creates a fake mathematical echo where energy bounces back up artificially. We restrict fitting to `[fit_start = 2.0, min(end_time, 0.8 * fake_revival_time)]`.
2. **Peak Detection:** `scipy.signal.find_peaks(energy)` locates the top of each oscillation bounce inside that valid window.
3. **Log-Linear Regression:** Taking the natural logarithm $\ln(\text{Peak\_Energy})$ turns an exponential decay curve into a **straight line**:
   $$\ln(\text{Peak\_Energy}) = \text{slope} \cdot t + \text{intercept}$$
   Fitting a degree-1 line with `np.polyfit` gives the slope.
4. **Divide Slope by 2:** Because Energy $= |\text{Field}|^2$, $\exp(2 \gamma t)$ has slope $2\gamma$, so `damping_rate = slope / 2.0` (a negative number means the wave is fading).

*Previous:* [Section 3 (`simulation.py`)](#section-3-running-the-simulation-quantum-vs-classical) | *Next:* [Section 5 (`plotting.py`)](#section-5-plotting-data-with-matplotlib) | [Back to top](#quick-navigation)

---

## Section 5: Plotting Data with Matplotlib

> **Code:** [plotting.py](plotting.py) (`plot_figure_1_quantum_vs_classical`, `plot_figure_2_factors_comparison`, `plot_figure_3_quantum_vs_classical_viability`)

Uses Matplotlib's non-interactive `Agg` backend so graphs save straight to PNG files in `gemini_imp/figures/` without blocking on pop-up windows. Together, the 3 figures answer both halves of the research question:

### Figure 1: `1_quantum_vs_classical_wave.png` (`plot_figure_1_quantum_vs_classical`)
- Uses `ax.semilogy()` so the Y-axis is on a logarithmic scale ($10^0, 10^{-1}, 10^{-2}, \dots$), turning exponential decay into a straight downward slope.
- Overlays the **Classical RK45 Solver** (black solid line), **Quantum Circuit Trotter Statevector** (blue dashed line), **2,000-Shot Hardware Readout** (orange dots, every 3rd step for readability), and the **Fitted Decay Slope** (orange dotted envelope).

### Figure 2: `2_factors_affecting_plasma.png` (`plot_figure_2_factors_comparison`)
- Sweeps physical parameters and plots a 1×2 side-by-side comparison of wave fade speed $|\gamma|$ for both solvers:
  - **Panel A (Wavenumber $k \in [0.3, 0.7]$):** Shorter wavelengths (higher $k$) damp faster.
  - **Panel B (Temperature $T \in [0.6, 1.6]$):** Hotter plasma (higher $T$) creates faster electrons that absorb energy faster, increasing damping.

### Figure 3: `3_quantum_vs_classical_scaling.png` (`plot_figure_3_quantum_vs_classical_viability`)
Directly answers *"Would it be useful to simulate on a quantum computer vs. a conventional computer?"*:
- **Left Panel (The Pro — 3D Reactor Memory Compression):** In a real 3D reactor (3 space axes + 3 velocity axes = 6 dimensions), a grid with $N$ points per axis requires $N^6$ numbers in classical RAM, versus only $6 \log_2 N$ qubits on a quantum register.
- **Right Panel (The Con — Current Gate-Count Bottleneck):** Transpiles a single Trotter time step for `n_qubits` $\in \{3, 4, 5, 6\}$ into standard IBM hardware gates (`cx`, `rz`, `sx`, `x`). Because generic dense Pauli decomposition scales as $\sim 4^n$ 2-qubit CNOT gates per step, today's noisy quantum hardware cannot run deep circuits yet without specialized sparse-matrix quantum algorithms.

*Previous:* [Section 4 (`analysis.py`)](#section-4-analysing-data-measuring-how-fast-the-wave-fades) | *Next:* [Main Entry Point (`plasma_simulation.py`)](#main-entry-point) | [Back to top](#quick-navigation)

---

## Main Entry Point

> **Code:** [plasma_simulation.py](plasma_simulation.py) (`main`)

`plasma_simulation.py` imports the functions from Sections 1–5 and runs the full workflow in three numbered steps:
1. **`[1/3]` Single-Wave Comparison:** Runs both `run_quantum_simulation` and `run_classical_simulation` on `DEFAULT_CONFIG`, computes damping rates and runtimes, and saves Figure 1.
2. **`[2/3]` Parameter Sweeps:** Calls `plot_figure_2_factors_comparison()` across wavenumbers and temperatures and saves Figure 2.
3. **`[3/3]` Scaling & Gate Costs:** Calls `plot_figure_3_quantum_vs_classical_viability()`, prints the CNOT count and circuit depth for 3–6 qubits, and saves Figure 3.

*Previous:* [Section 5 (`plotting.py`)](#section-5-plotting-data-with-matplotlib) | [Back to top](#quick-navigation)

---

## Quick Glossary

| Term | Plain-English Meaning | Where Used |
|---|---|---|
| **Landau Damping** | Collisionless fading of a plasma wave as resonant electrons absorb its energy | [Section 1](#section-1-physical-factors--simulation-settings), [Section 4](#section-4-analysing-data-measuring-how-fast-the-wave-fades) |
| **Wavenumber ($k$)** | $2\pi / \text{wavelength}$ — how tightly packed wave crests are | [config.py](config.py), [plotting.py](plotting.py) |
| **Maxwellian ($f_0$)** | Gaussian bell curve of electron speeds at temperature $T$ | [hamiltonian.py](hamiltonian.py) |
| **Hamiltonian ($H$)** | Hermitian $2^n \times 2^n$ matrix driving unitary time evolution $e^{-iHt}$ | [hamiltonian.py](hamiltonian.py) |
| **Pauli Strings** | Weighted sum of `I, X, Y, Z` tensor products representing $H$ for quantum gates | [simulation.py](simulation.py) |
| **Suzuki-Trotter** | Gate-based approximation of $e^{-i H \, dt}$ by slicing non-commuting Pauli terms | [simulation.py](simulation.py) |
| **Shots** | Repeated quantum circuit measurements used to estimate $P(\|00000\rangle)$ | [simulation.py](simulation.py) |
| **Fake Revival Time** | Time $2\pi / (k \, dv)$ when discrete velocity buckets cause an artificial wave echo | [analysis.py](analysis.py) |
| **CNOT / Depth** | 2-qubit entangling gate count and sequential circuit layers (hardware noise bottleneck) | [plotting.py](plotting.py) |

[Back to top](#quick-navigation)
