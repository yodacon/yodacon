# LR-2026-03 — The reentry particle stack: how the fire is drawn

**Date:** 2026-08-28 · **Scope:** `gonex/internal/fx`, `gonex/internal/app`
(entrymode, bowfx, fastdraw) · **References:** Stam & Fiume 1995, the
texture-splat literature (King 2000 / Wei 2002), the PSX-Doom fire, the
1997 plugin's emission palette, and the vendored MHD console
(`vendor/docs/reentry-console.html`).

The entry scene draws several thousand luminous primitives per frame on a
2D immediate-mode renderer with no shaders. This report records the
techniques that make it read as volumetric fire rather than confetti, and
what each one costs.

## 1. Two render paths, both batched

Everything visual funnels through two primitives:

- **`fastQuad`** — one shared 1×1 white texel, `DrawTriangles` with vertex
  colors. Dots are squares; lines are rotated quads. No tessellation, no
  per-call lock, and Ebitengine folds consecutive calls on the same
  texture into a handful of GPU draws.
- **`glowDot` / `softDot`** — one shared 64×64 radial-gradient texture
  (premultiplied white, quadratic falloff), splatted with vertex-color
  tint. `glowDot` draws it with `BlendLighter`: overlapping splats *sum*
  toward white, which is exactly how overlapping incandescent gas reads.
  `softDot` draws the same texture source-over: absorptive, for smoke and
  dust. This is the literature's Gaussian texture splat, reduced to one
  texture and a blend mode.

The discipline that makes it fast: **never interleave the paths**. Every
hot loop renders in passes — all glow splats (one texture, one blend, one
batch), then all cores. The fire looked identical interleaved; it just
cost thousands of pipeline flips per frame.

## 2. The fire grid, bent (fx.Fire)

The classic intensity-propagation fire — every cell re-averages the cells
one row nearer the ignition front, sheds heat, flickers; the front row
re-rolls from fuel — is simulated in its own (u, v) space, decoupled from
the screen. The renderer then lays the grid onto any curve:

- the **plasma bow wave**: row 0 burns on the magnetopause arc, and each
  row outward drifts aft and outboard quadratically, bending every column
  like the streamline it rides;
- the **Mach collar**: rows sweep back along the cone, cotangent-scaled
  by √(M²−1), rendered in white glow — condensation, not combustion.

`Sweep` skews the sampling window so the whole flame leans with the
steering lobe; `FuelProfile` shapes the front (stagnation-weighted,
inflated on the pushing side). Rendering quantizes intensity into hard
emission-line bands — white core, combustion yellow, Li 670.8 nm red,
N₂ first-positive violet rim — the marching-squares contour idea reduced
to its visible half. A slow sinusoidal wobble rides the whole sheet so it
breathes. Cost: ~600 cells × 2 passes, all batched.

## 3. The Stam–Fiume loop over the scene

The particle system follows the 1995 staging exactly:

1. **Solid object** — the hull. Its "fuel map" is the sprite's own alpha
   mask (a one-time BFS distance transform bakes contour points with
   outward normals) plus the sheath heat fraction. Flame blobs are born
   on the mask and at the bow.
2. **Flame blobs** — temperature is the `phase` walked along a six-stop
   position-in-flow ramp (bow blue → shell yellow → shoulder blue → pink
   → white → recombination red). Hot blobs in the bow wake *shed
   children* — the cascade that makes the burn visibly multiply — capped
   by the global particle budget.
3. **Smoke blobs** — a flame blob expiring past blackbody generates soot:
   `softDot` splats that diffuse (radius grows), thin, and ride the wash
   down-screen. Contrails and touchdown dust reuse the same struct and
   the same batch.

## 4. Two fields fighting over every blob

An ignited blob is pulled by two vector fields at once:

- the **dipole** B ∝ [3(m̂·r̂)r̂ − m̂]/r³ — the shield, its moment tilted
  by the steering cone, its lobes the classic r = L·sin²θ;
- the **ram flow** — radial out of the horizon's vanishing point, the
  perspective river the whole scene drifts on.

The MHD gate (from the same state evaluation the gauges read) is the
coupling coefficient: uncoupled blobs blow downstream, coupled blobs lock
onto field lines — and a coupled blob also receives a perpendicular
sinusoidal component, so it *twirls* helically along its lobe. That grip
made visible is the point of the whole shield.

The captured plasma is also painted directly: the **pillows** — glow
splats laid along the two dipole lobes, cyan inner and violet outer,
breathing on the sim clock, inflated on the side opposite the roll
command and starved on the other. Steering reads as light before it
reads as motion.

## 5. The perspective river and the volumetric layer

Everything obeys one camera fiction: the ship is fixed, the world flies
at it from the vanishing point. Inflow particles are born hard against
the horizon and accelerate with (0.25 + f); a **cloud layer** of large
glow blobs rides the same sightlines with perspective acceleration
(f̈ ∝ 0.22 + 1.7f), swelling with the viewport angle and then swept
violently below the camera — pale condensation low, plasma-lit when the
sheath is hot. Every particle also carries a depth-scaled downward draft
(150 + 430·depth px/s²), so the whole flow drains past the ship the way
a camera bolted to a falling object would see it.

## 6. Budgets and determinism

- Particle cap 3000 (cascade included), smoke 480, contrails 320,
  clouds ≈ 50; every spawn count scales with heat/density so the scene
  starts sparse and crescendos.
- The full-descent trajectory prediction (Euler, 0.5 s step, 420 s
  horizon) refreshes at 4 Hz, not per frame.
- The sky dome renders to an offscreen re-keyed only on quantized
  altitude/sun buckets; placement (bank, horizon) is a per-frame GeoM.
- `fx.Fire` runs a fixed 30 Hz accumulator, frame-rate independent, and
  every stochastic system is seeded from the voyage RNG — the corridor
  gates in `internal/reentry` stay bit-deterministic because the sim
  never reads the visual RNG.

## 7. The bench

`GONEX_BOOT=fxlab` boots a black stage with the ship, both fire grids,
and every input the entry feeds them on a key. All tuning in this report
was iterated there, in seconds per change, and verified in-flight with
`GONEX_SHOT` frame dumps.
