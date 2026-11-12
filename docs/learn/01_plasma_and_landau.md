# 1. Plasma waves and Landau damping

## Why fusion needs this

A tokamak holds plasma at about 100 million °C inside a magnetic "doughnut". The plasma is never calm: it is full of waves and ripples. Some fade away harmlessly. Others grow, push plasma into the wall and cause a **disruption** (which can damage the machine). Magnet control systems need to know which is which, faster than the plasma changes. Predicting this needs simulation, and kinetic simulation (tracking the full velocity distribution) is among the most expensive calculations in physics.

## The simplest plasma wave

Push a slab of electrons sideways. The positive ions left behind pull the electrons back, the electrons overshoot, and they oscillate back and forth like a mass on a spring. That's a **plasma (Langmuir) wave**. How fast they oscillate is the **plasma frequency ω_p**. Shorter waves oscillate slightly faster (see the Bohm–Gross formula below).

## The plasma's own units (read this before anything else)

Every number in these docs and in the code is measured with the plasma's **own** clock, ruler and speedometer, not with seconds, metres and m/s. There are three units, and they are linked.

| Quantity | Unit | Symbol | Code name | Plain meaning |
|---|---|---|---|---|
| Time | 1 "plasma tick" | 1/ω_p | `end_time`, `times` | Time for the electron "spring" to turn through 1 radian of its oscillation |
| Speed | 1 "thermal speed" | v_th | `velocities`, `max_velocity` | The typical speed of an electron, i.e. the width of the bell curve |
| Length | 1 "screening length" (Debye length) | λ_D = v_th / ω_p | (via `wavenumber`) | How far a typical electron travels in one tick |

### Why time is measured in 1/ω_p

- **ω_p is the plasma's heartbeat.** Every event in this problem happens on that timescale: the wave oscillates at about ω_p, and it damps within a few tens of ticks. If we used seconds, every number would look like 0.000000000002, which is unreadable and easy to get wrong. In ticks, the numbers are around 1 to 20.
- **Why 1/ω_p and not one full oscillation?** ω_p is an *angular* frequency (radians per second). One full swing is 2π radians, so one full oscillation takes 2π/ω_p ≈ 6.3 ticks. A tick (1/ω_p) is the time to turn through 1 radian. It's chosen because it makes the formulas simplest: the wave then goes like e^{−i·1·t} instead of e^{−i·ω_p·t}.
- **Formula:** ω_p = √(n e² / ε₀ mₑ). Denser plasma means a stronger restoring pull, which means a faster spring and a shorter tick.

### Why speed is measured in v_th

- Landau damping (below) is a contest between the **wave's speed** and the **electrons' speeds**. The electrons' speeds form a bell curve, and v_th = √(T / mₑ) is its width. Measuring speeds in v_th directly tells you where you are on the bell curve: "speed 1" is a typical electron, and "speed 3" is out in the thin tail where few electrons are.
- In these units the bell curve (the Maxwellian) is always the same shape: F0(v) = e^{−v²/2} / √(2π). It doesn't matter how hot the plasma is. Only the conversion back to m/s depends on temperature.
- That's also why the velocity grid in the code runs from −6 to +6: beyond 6 thermal speeds there are essentially no electrons.

### Why length is measured in λ_D

- λ_D is **not a third independent choice**. Once you fix a clock (1/ω_p) and a speedometer (v_th), length is fixed too, because distance = speed × time: λ_D = v_th × (1/ω_p). It's how far a typical electron moves in one tick.
- Physically it's also the "screening" distance: beyond about λ_D, a charge is hidden by the cloud of opposite charges that gathers around it. Written out in full it's λ_D = √(ε₀ T / n e²).
- Because the three units are linked (λ_D = v_th/ω_p), **v_th is automatically 1 in our units**: 1 screening length per tick.

### Converting answers back to real units

| You have (normalised) | To get real units | Example (tokamak, below) |
|---|---|---|
| a time t (ticks) | divide by ω_p → seconds | t = 20 ticks → 20 / 5.6×10¹¹ ≈ 36 ps |
| a rate ω or γ (per tick) | multiply by ω_p → per second | γ = −0.1533 → −8.6×10¹⁰ s⁻¹ |
| a speed v (thermal speeds) | multiply by v_th → m/s | v = 1 → 4.2×10⁷ m/s |
| a length (screening lengths) | multiply by λ_D → metres | wavelength 2π/0.5 ≈ 12.6 → 0.93 mm |

Worked example, tokamak core (T = 10 keV, n = 10²⁰ m⁻³), computed by `plasma_scales()` in `config.py`:
ω_p = 5.6×10¹¹ rad/s (so 1 tick ≈ 1.8 ps), v_th = 4.2×10⁷ m/s, λ_D = v_th/ω_p = 74 µm.

## Landau damping: the surfer picture

Electrons have a spread of speeds (the Maxwellian bell curve, width v_th). Look at the electrons moving at about the wave's speed, its **phase velocity** ω/k:

- Slightly **slower** electrons get pushed forward by the wave. They take energy from it.
- Slightly **faster** electrons push the wave. They give it energy.
- In a bell curve there are always **more slower than faster** electrons near any speed on the downward slope. So the wave loses more energy than it gains, and it decays.

**Units make this concrete.** At kλ_D = 0.5 the wave has ω = 1.4156 (per tick), so its phase velocity is ω/k = 1.4156 / 0.5 ≈ **2.8 v_th**. That's out in the tail of the bell curve, where only a few electrons can surf, so the damping is moderate.

No collisions are involved. This was predicted by Lev Landau in 1946 and was controversial for years. It's a purely **kinetic** effect: fluid models (MHD) cannot see it. You need the full velocity distribution, which is why it's expensive to simulate.

## Why the solver takes one input instead of three

The spec lists three inputs: wavenumber k, temperature T and density n. When everything is measured in ticks, thermal speeds and screening lengths:

1. n and T only ever appear inside ω_p, v_th and λ_D, and those are now all exactly 1. So n and T vanish from the equations. It's like a price being the same whether you write it in pounds or pence.
2. The only number left is the wave's size **measured with the plasma's ruler**: kλ_D (the code's `wavenumber`). Writing "k = 0.5" anywhere in these docs means kλ_D = 0.5.
3. The solver therefore returns ω and γ **per tick**. T and n come back only at the very end, when we convert ticks to seconds (divide times / multiply rates by ω_p).

Any two plasmas with the same kλ_D behave identically on their own clocks, so scanning one number covers every plasma. (This holds because only electrons move. Letting ions move would add two more ratios.)

Even the wave frequency shows this. In real units, Bohm–Gross says ω² ≈ ω_p² + 3k²v_th². In our units ω_p = v_th = 1, so it becomes ω² ≈ 1 + 3k², where k means kλ_D. At k = 0.5 that gives ω ≈ 1.32 per tick (the exact answer, 1.4156, is a bit higher because Bohm–Gross is only an approximation).

## What controls the damping

- **Shorter waves (larger kλ_D) damp much faster.** Their phase speed ω/k is lower (closer to 1 v_th), nearer the crowded middle of the bell curve, so more electrons can surf them. Our run reproduces this: γ = −0.013 per tick at kλ_D = 0.3 and γ = −0.39 per tick at kλ_D = 0.7, a 30× change.
- **Temperature and density** act in exactly two places:
  - *Inside kλ_D.* Hotter plasma has a bigger λ_D, so the same physical wave has a bigger kλ_D and damps faster. Denser plasma has a smaller λ_D, so it does the opposite.
  - *In the conversion to seconds (via ω_p).* Denser plasma ticks faster, so the same number of ticks is fewer seconds.
- That's why the code has **one physics input, `wavenumber`**. The three parameters in the team PDF (k, T, n) reduce to this one number. That's a good point to make if judges ask.

## The benchmark number to remember

For kλ_D = 0.5, solving Landau's exact equation gives **ω = 1.4156, γ = −0.1533** (both per tick, i.e. in units of ω_p; the minus sign means the wave is fading). Every textbook and paper uses this case. Our quantum circuit gets γ = −0.1538, within 0.33%, without ever being given the answer.

In a tokamak core this means a 0.93 mm wave whose amplitude falls by a factor e every 1/0.1533 ≈ 6.5 ticks ≈ 12 ps. Its energy (amplitude squared) falls twice as fast, by e every ≈ 6 ps.

## Honest limits of our model (say these before judges do)

- **Linear:** small ripples only. No turbulence.
- **1D1V:** one space and one velocity dimension. Real reactors are 3D3V.
- **No collisions, no magnetic field.** This deliberately isolates Landau damping.
- **Maxwellian background:** waves always damp. Growing instabilities (e.g. bump-on-tail beams) need a non-Maxwellian F0. That breaks the Hermitian trick in doc 2, so it's future work.
