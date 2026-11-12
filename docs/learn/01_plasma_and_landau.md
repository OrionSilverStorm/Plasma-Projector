# 1. Plasma waves and Landau damping

Physics only, no code. Unfamiliar words are in the glossary in [doc 0](00_reading_order.md).

## Why fusion cares
A tokamak (doughnut-shaped fusion reactor) holds ~100 million °C plasma with magnets. Ripples pass through it constantly. Most fade; some grow, hit the wall and cause a *disruption* that can damage the machine. The control system must tell them apart fast, which needs *kinetic* simulation (tracking every electron's speed), one of the most expensive calculations in physics.

## The simplest plasma wave
Shove some electrons sideways. The positive ions left behind pull them back, they overshoot, get pulled back again: a mass on a spring. That's a **plasma wave**, and its bounce rate is the **plasma frequency**. Denser plasma pulls harder and bounces faster.

## The plasma's own units (the key to reading the code)
All numbers are in units set by the plasma, not seconds and metres:

| Quantity | Unit | Meaning |
|---|---|---|
| Time | **plasma tick** (1/ω_p) | Time to turn 1 radian of a bounce; a full bounce is 2π ≈ 6.3 ticks |
| Speed | **thermal speed** (v_th) | Typical electron speed (width of the speed bell curve) |
| Length | **screening length** (λ_D) | Distance a typical electron covers in one tick |

- **Ticks** keep numbers readable (1–20, not 0.000000000002) and remove 2π from formulas.
- **Thermal speeds** show where you are on the bell curve: speed 1 is ordinary, speed 3 is the rare fast tail. The curve then has the same shape for every plasma, `e^{−v²/2}/√(2π)` (`background_distribution()`). Beyond ±6 there are essentially no electrons, so the velocity grid stops there.
- **Screening length** isn't a free choice: distance = speed × time. Physically, beyond it a charge is hidden by the opposite charges crowding round it.

Converting back (tokamak core: 10,000 eV, 10²⁰ electrons/m³, from `plasma_scales()`; plasma frequency 5.6×10¹¹ rad/s, thermal speed 4.2×10⁷ m/s, screening length 74 µm):

| Have | Do | Example |
|---|---|---|
| time (ticks) | ÷ plasma frequency | 20 ticks ≈ 36 ps |
| rate (per tick) | × plasma frequency | −0.1533 ≈ −8.6×10¹⁰ /s |
| length (screening lengths) | × screening length | wavelength 2π/0.5 ≈ 12.6 → 0.93 mm |

## Landau damping: the surfer picture
The wave travels at its own speed. Electrons moving at about that speed are like surfers:
- slightly **slower** ones get pushed along, taking energy from the wave;
- slightly **faster** ones push the wave, giving it energy;
- the bell curve slopes down, so there are always **more slow than fast** surfers. The wave loses net energy and fades.

No collisions are involved. Fluid models, which only track average speed, can't see this; you need the whole speed histogram, which is why it's expensive.

Example: at wavenumber 0.5 the wave wiggles at 1.4156 rad/tick, so it moves at 1.4156/0.5 ≈ 2.8 thermal speeds, out in the sparse tail. Few surfers, so moderate damping.

## Why one input, not three
The brief lists wavenumber, temperature and density. Temperature and density only appear inside the three units above, which are all 1 in our units, so they drop out (like a price being the same in pounds or pence). Only `wavenumber` (kλ_D) remains. They return only when converting ticks to seconds. So any two plasmas with the same wavenumber behave identically on their own clocks, and scanning one number covers every plasma (assuming only electrons move).

## What controls the damping
- **Shorter waves fade much faster.** They move slower, nearer the crowded middle of the bell curve, so more electrons surf them: −0.013 per tick at wavenumber 0.3 vs −0.39 at 0.7 (30×).
- **Temperature and density** act only through the wavenumber (hotter → bigger screening length → bigger wavenumber → faster fade) and the tick-to-seconds conversion.

## Benchmark to remember
Wavenumber 0.5: oscillation rate **1.4156**, damping rate **−0.1533** per tick (the standard textbook case). Our circuit gets −0.1538 (0.33% off) without being told the answer. In a tokamak: a 0.93 mm wave whose energy drops by a factor e every ~6 ps.

## Honest limits
- **Small ripples only** (equations linearised): no turbulence.
- **1D1V**, not a reactor's 3D3V.
- **No collisions or magnetic field**, deliberately, to isolate Landau damping.
- **Bell-curve background only**, so waves always fade. Growing waves need a different background, which breaks the trick in doc 2 step 3. Future work.
