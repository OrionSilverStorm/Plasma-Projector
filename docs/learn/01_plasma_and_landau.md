# 1. Plasma waves and Landau damping

## Why fusion needs this

A tokamak holds plasma at about 100 million °C inside a magnetic "doughnut". The plasma is never calm: it is full of waves and ripples. Some fade away harmlessly. Others grow, push plasma into the wall and cause a **disruption** (which can damage the machine). Magnet control systems need to know which is which, faster than the plasma changes. Predicting this needs simulation, and kinetic simulation (tracking the full velocity distribution) is among the most expensive calculations in physics.

## The simplest plasma wave

Push a slab of electrons sideways. The positive ions left behind pull the electrons back, the electrons overshoot, and they oscillate. That's a **plasma (Langmuir) wave**. Its frequency is about ω_p, slightly higher for shorter waves: ω² ≈ ω_p² + 3k²v_th² (Bohm–Gross).

## Landau damping: the surfer picture

Electrons have a spread of speeds (the Maxwellian bell curve). Look at the electrons moving at about the wave's speed (its phase velocity, ω/k):

- Slightly **slower** electrons get pushed forward by the wave. They take energy from it.
- Slightly **faster** electrons push the wave. They give it energy.
- In a bell curve there are always **more slower than faster** electrons near any speed on the downward slope. So the wave loses more energy than it gains, and it decays.

No collisions are involved. This was predicted by Lev Landau in 1946 and was controversial for years. It's a purely **kinetic** effect: fluid models (MHD) cannot see it. You need the full velocity distribution, which is why it's expensive to simulate.

**Why the solver takes one input instead of three**

The spec lists three inputs: wave size k, temperature T and density n. But the plasma has its own natural units: a clock, ω_p = √(n e² / ε₀ m), which is how fast electrons spring back when pushed together, and a ruler, the Debye length λ_D = √(ε₀ T / n e²), which is how far a typical electron travels in one clock tick. If we measure time in clock ticks and distance in Debye lengths, every n and T cancels out of the equations, like a price being the same in pounds or pence. The only thing left is the wave's size measured with the plasma's ruler, kλ_D. So the solver only needs kλ_D, and we multiply its answer by ω_p at the end to convert back to real seconds. Any two plasmas with the same kλ_D behave identically on their own clocks, so scanning one number covers every plasma. This holds because only electrons move; letting ions move would add two more ratios.

We check this against the standard benchmark for plasma codes. At kλ_D = 0.5, solving Landau's exact equation gives ω = 1.4156 ω_p and γ = −0.1533 ω_p (the minus sign means the wave is fading). Our quantum circuit gets γ = −0.1538, about 0.33% off, without ever being given the answer.

## What controls the damping

- **Shorter waves (larger kλ_D) damp much faster.** Their phase speed is lower, closer to the crowded middle of the bell curve, so more electrons can surf them. Our run reproduces this: γ = −0.013 at kλ_D = 0.3 and γ = −0.39 at kλ_D = 0.7, a 30× change.
- **Temperature and density** only matter through kλ_D (λ_D = √(ε₀T / n e²)) and through converting answers to seconds (via ω_p). Hotter plasma means a bigger λ_D, so a bigger kλ_D for the same physical wavelength, so faster damping. Denser plasma does the opposite.
- That's why the code has **one physics input, `k`**. The three parameters in the team PDF (k, T, n) reduce to this one number. That's a good point to make if judges ask.

## The benchmark number to remember

For kλ_D = 0.5: **ω = 1.4156 ω_p, γ = −0.1533 ω_p**. Every textbook and paper uses this case. Our quantum circuit gets γ = −0.1538, within 0.3%.

## Honest limits of our model (say these before judges do)

- **Linear:** small ripples only. No turbulence.
- **1D1V:** one space and one velocity dimension. Real reactors are 3D3V.
- **No collisions, no magnetic field.** This deliberately isolates Landau damping.
- **Maxwellian background:** waves always damp. Growing instabilities (e.g. bump-on-tail beams) need a non-Maxwellian F0. That breaks the Hermitian trick in doc 2, so it's future work.
