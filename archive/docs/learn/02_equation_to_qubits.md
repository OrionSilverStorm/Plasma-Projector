# 2. From the plasma equations to qubits

Code: `src/config.py`, `src/hamiltonian.py`. Method: Engel, Smith & Parker (2019).

Two equations go in; a 32×32 matrix and a 32-number vector (5 qubits) come out. Notation is in the toolkit in [doc 0](00_reading_order.md).

## Step 0: units (`config.py`)
In the plasma's own units (doc 1) every physical constant equals 1 and disappears, leaving only `wavenumber`. All numbers below are in ticks, thermal speeds and screening lengths.

## Step 1: the two rules
Electron speeds = bell-curve `background` + small `ripple`. Assuming the ripple is small (*linearising*) leaves:

```
d(ripple)/dt = −i · wavenumber · v · ripple  −  v · background(v) · field     (1)
d(field)/dt  = Σ over velocities of v · ripple · velocity_spacing              (2)
```

- **`−i · wavenumber · v · ripple`**: electrons coast. This only rotates the ripple's phase, faster at higher v. The velocities drift out of step and cancel out (*phase mixing*), which is what makes the wave fade.
- **`− v · background · field`**: the field pushes electrons, most where there are many.
- **Rule (2)**: moving electrons are a current, and current changes the field (Ampère's law).

## Step 2: velocity grid
Sample velocity at `n_velocities` evenly spaced points in [−6, 6] (`max_velocity`). The ripple becomes an array, and the integral a sum times `velocity_spacing`.

## Step 3: make it quantum-friendly
A quantum computer can only do `new = e^{−iHt} · old` with H **Hermitian**, which keeps the vector's length at 1. Rules (1)–(2) are lopsided: one link has a `background` factor, the other doesn't. Rescaling fixes it:

```
particle_j = sqrt(velocity_spacing) · ripple(v_j) / sqrt(background(v_j))
coupling_j = v_j · sqrt(background(v_j) · velocity_spacing)
```

Now the system is exactly `d(state)/dt = −i · hamiltonian · state` with `state = (field, particle_1, …, particle_N)` and

```
hamiltonian[j, j] = wavenumber · v_j     diagonal: coasting
hamiltonian[0, j] = +i · coupling_j      row 0: particles → field
hamiltonian[j, 0] = −i · coupling_j      column 0: field → particles (the conjugate, so Hermitian)
```

These are the three lines in `build_hamiltonian()`: the whole physics model.

**Why it works:** the vector's length squared, `|field|² + Σ|particle_j|²`, is the wave's total energy. Energy is conserved, so length is conserved, which is exactly what a quantum computer's updates do.

The matrix is an **arrowhead** (diagonal + row 0 + column 0, the rest zero). That structure matters in doc 4.

## Step 4: fit into qubits
n qubits hold 2ⁿ numbers, so `n_velocities = 2ⁿ − 1` leaves one slot for the field. 5 qubits: 31 velocities + field = 32. The field is index 0, the amplitude of `00000`. An odd point count also puts a grid point at v = 0.

## Step 5: obey Gauss's law (`initial_state`)
We start with a ripple shaped like the background. Gauss's law says that clump of charge fixes the field: `i · wavenumber · field = −Σ ripple · velocity_spacing`, so `field ≈ i / wavenumber`. Starting with a field and no ripple would break this and leave a constant fake field that never fades. `test_initial_state_obeys_gauss_law` checks it.

## Step 6: read the answer
P(measure `00000`) = `|field|²` = field energy (`field_energy()`). It goes up and down as energy sloshes between field and electrons, with peaks shrinking like `e^{2 · damping_rate · t}` (2 because energy is size squared).

## Step 7: the grid's fake echo
On an evenly spaced grid the drifting velocities all line up again at

```
fake_revival_time = 2π / (wavenumber · velocity_spacing)
```

and the wave falsely reappears. 5 qubits: spacing 12/30 = 0.4, so at wavenumber 0.5 that's ≈ 31 ticks. We stop at 20 (`end_time`). More qubits → finer grid → later revival.
