# 2. From the plasma equation to qubits

Code: `src/config.py`, `src/hamiltonian.py`. Method: Engel, Smith & Parker (2019).

## Step 0: normalised units (`config.py`)
We measure time in 1/ω_p, length in λ_D and speed in v_th. All constants (e, mₑ, ε₀) become 1. Only kλ_D is left. `plasma_scales()` converts back to SI. For a tokamak core (10 keV, 10²⁰ m⁻³): ω_p = 5.6×10¹¹ rad/s and λ_D = 74 µm, so our kλ_D = 0.5 wave is a 0.93 mm wave whose energy decays in about 6 picoseconds.

## Step 1: the linearised equations
Write the electron distribution as background plus a small ripple: f = F0(v) + f₁(v)·e^{ikx}. Keep only first-order terms:

```
df1/dt = -i k v f1  -  v F0(v) E      (1) particles stream; the field E pushes them
dE/dt  =  ∫ v f1 dv                   (2) moving electrons are a current that changes E (Ampère)
```
- Term `-ikv f1`: each velocity slice just rotates its phase. This is "phase mixing", the root of Landau damping.
- Term `-v F0 E`: the field reshapes the distribution (comes from −E·∂F0/∂v with ∂F0/∂v = −vF0).

## Step 2: discretise velocity
Put v on a grid of N_v points from −6 to +6 (beyond 6 v_th there are essentially no electrons). Now f₁ is just a list of N_v complex numbers, and the integral becomes a sum.

## Step 3: the trick that makes it quantum-friendly
Quantum computers can only do **unitary** evolution ψ(t) = e^{−iHt}ψ(0) with **Hermitian** H. Equations (1) and (2) aren't in that form yet, because the coupling terms aren't symmetric (one has F0 in it, the other doesn't). Fix it by rescaling:

```
g = f1 / sqrt(F0),     u_j = sqrt(dv) * g(v_j),     a_j = v_j * sqrt(F0(v_j) * dv)
```
Now both coupling terms carry the same factor a_j, and the system is exactly

```
dψ/dt = -i H ψ,    ψ = (E, u_1, ..., u_Nv)

H[j, j] = k v_j        (diagonal: streaming)
H[0, j] = +i a_j       (row 0: field <- particles)
H[j, 0] = -i a_j       (column 0: particles <- field), the complex conjugate, so H is Hermitian
```
**Why it works physically:** |E|² + Σ|u_j|² is the plasma's total wave energy (field plus "free energy" in the particles). Energy conservation means the length of ψ is conserved, and a length-preserving evolution is exactly what a unitary operation is. So the physics was quantum-shaped all along.

H is an **arrowhead matrix**: a diagonal plus one full row and one full column. Nearly all entries are zero. Remember this for doc 4.

## Step 4: pack it into qubits
ψ has N_v + 1 entries. Choose N_v = 2ⁿ − 1, so ψ fits exactly in **n qubits** (2ⁿ amplitudes). With 5 qubits we get 31 velocity points. Index 0 (the state |00000⟩) holds the electric field E.

## Step 5: the initial state must obey Gauss's law
We start with a density ripple f₁ = F0. Gauss's law (ikE = −∫f₁dv) then fixes E = i/k. If we started with only E (ψ = |0…0⟩), Gauss's law would be violated. The equations then carry a constant non-decaying field forever, and the plot would plateau instead of damping. `initial_state()` builds the correct state, and a test checks Gauss's law.

## Step 6: reading the answer
Measuring all qubits gives |0…0⟩ with probability |ψ₀|² = |E|². So **the electric field energy is a single measurement probability**. It oscillates (energy sloshes between field and particles) inside an envelope that decays like e^{2γt}.

## Step 7: the grid's fake echo
A discrete velocity grid has a finite smallest spacing Δv. After T_R = 2π/(kΔv), all the phase-mixed slices line up again and the wave falsely revives. With 5 qubits and k = 0.5, T_R ≈ 31, so we stop at t = 20. More qubits give a finer grid and a later recurrence.
