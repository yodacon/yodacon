# LR-2026-04 — The Landing Sequence: A Layered Rendering Architecture for a Plasma-Shielded Reentry

*Yodacon Engineering — release candidate 2 · build 2026-08-28 · gonex `672419d`*

**Abstract** — We describe the complete visual architecture of the Gonex
reentry sequence: a 24-layer painter's-order render stack over a
deterministic 3-DOF simulation, drawn with two batched primitive paths on
a shaderless 2D engine. The sequence carries one continuous camera
fiction from deorbit to a graded runway debrief, across three time
domains, with every effect layer keyed to physical state rather than
script. This report enumerates each layer, its physical driver, its
render path, and its ordering rationale, for the architect who has to
extend it.

**Index terms** — painter's algorithm, texture splats, additive blending,
particle systems, magnetohydrodynamics, flight director, batching,
Ebitengine.

---

## I. Introduction

The landing is the game's signature system, and its scene
(`internal/app/entrymode.go`, ~2000 lines) is the largest single view.
Three principles govern it:

1. **State, not script.** Every layer's intensity is a function of the
   simulation (`internal/reentry`): heat flux fraction q̂ = Q̇/TPS_limit,
   MHD gate g, aero authority a, altitude h, corridor error ε. Nothing
   fades on a timer; the physics *is* the animation curve.
2. **One camera fiction.** The ship is fixed at (512, 470); the world
   flies at the camera from a vanishing point on the horizon. Every
   moving element — inflow, clouds, ground dots, the city — obeys the
   same perspective, so closure rate and the speed tape can never
   disagree.
3. **Two primitive paths, never interleaved.** A 1×1 white texel for
   solid quads (`fastQuad/fastLine/fastDot`) and one 64×64 radial
   gradient for splats — additive (`glowDot`, BlendLighter: overlapping
   incandescence sums toward white) or source-over (`softDot`:
   absorptive smoke/dust). Hot loops render in passes per path, so the
   GPU sees a handful of batches, not thousands of pipeline flips.

## II. Temporal Architecture

The sequence crosses three time domains, stitched without cuts:

| Phase | Driver | Time scale |
| --- | --- | --- |
| Deorbit | `deorbit.go`, 3.2 s scripted swell | wall clock |
| Corridor (122 km → touchdown decision) | RK4 sim `Sim.Step` | **18×** (dt 0.3 s/frame) |
| ILS final (glideslope, flare, rollout) | kinematic, `finalTimeScale` | **20×** |
| Debrief | none (card) | wall clock |

Named events, in order: entry interface (122 km, super-circular), the
**Kármán call** (100 km — the world-wake threshold every surface tier
keys on), the deceleration pulse (55–95 km, peak q̂ and g), the **STEER
handoff** (plasma authority < aero authority: "in the pipe, five by
five"), terminal sink, glideslope capture, flare, touchdown (dust
burst), rollout, debrief fade-in.

The corridor→final seam is a scalar `seamT ∈ [0,1]` (velocity 650→300
m/s) that simultaneously lerps the horizon line, the ship's anchor and
scale, and dissolves the orbital ground into the final's terrain: the
handoff frame is pixel-continuous. Visual effects (fires, particles,
clouds) integrate at *wall* dt — motion reads at animation speed while
the trajectory runs 18×.

## III. The Render Stack

Painter's order, back to front, as executed by `drawEntry`:

| # | Layer | Function / site | Driver | Path |
| --- | --- | --- | --- | --- |
| 0 | Void fill + starfield | `app.Draw` | — | fill |
| 1 | Sky dome (64 bands, nebula, ionosphere ribbon) | `drawSky` | h, sun phase | cached offscreen |
| 2 | Ground bands (near-black above Kármán) | inline | wake(h), sun | fastLine |
| 3 | Seam terrain dissolve | inline | seamT | fastRect |
| 4 | Blue atmosphere band *beneath* the horizon | inline | h | stroked arcs |
| 5 | Limb line (blue-white → green) | inline | wake(h) | stroked arc |
| 6 | Surface tiers: shoreline, city-light network, ground dots, port, pad | inline + `drawPortScene` | log-decade fades vs Kármán | mixed |
| 7 | Heat veil (screen reddens) | inline | q̂, off-corridor | fastRect |
| 8 | Smoke blobs + contrails | inline | Stam–Fiume stage 3; aero | `softDot` (one batch) |
| 9 | Particle glow pass | inline | all ignited blobs | `glowDot` (one batch) |
| 10 | Particle cores: inflow streaks, flame licks | inline | flow state | fastLine/fastDot |
| 11 | Corona: sheath envelope, white bow kernel, off-pipe red flare | inline | q̂, standoff, ε | `glowDot` |
| 12 | Volumetric cloud layer (perspective blobs) | inline | q̂, aero, V | `glowDot` |
| 13 | Bow-wave fire (bent grid, 2-pass) | `drawBowFire` | fx.Fire ← q̂, feed, gate | glow+fast |
| 14 | Mirror shell arc + dark inner line | inline | standoff, roll lobe | stroked |
| 15 | Directed plasma pillows (lobe volumes) | `drawPlasmaPillows` | plasma authority, roll | `glowDot` |
| 16 | Dipole field lines (r = L·sin²θ, 4 lobes ×2 on boost) | `drawFieldLines` | authority | stroked |
| 17 | Hull fire glow (baked mask falloff) | inline | q̂ flicker | sprite |
| 18 | The ship | inline | seam anchor, slope squash | sprite |
| 19 | Hull incandescence (blackbody overlay + halo) | inline | gate≈0 ∨ cooling>85% ∨ scrubbing | sprite, BlendLighter |
| 20 | Shock puffs (supersonic pressure rings) | inline | Mach | fastLine |
| 21 | Shield band (baked mask ring) | inline | gate | sprite |
| 22 | Mach condensation collar (2-pass, cone-swept) | `drawMachCloud` | aero × Mach window | glow+fast |
| 23 | Sonic boom rings + town BOOOOMs | `drawBoom` | Mach>1.1 below 10 km | stroked |

Above the world, the instrument stack (Section V), then the deorbit
white-in flash, then the outcome card. The ILS final short-circuits to
`drawFinalApproach` + dials; the parked runway strips *everything* and
draws only the debrief.

## IV. Field-Coupled Particle Dynamics

The particle system is a Stam–Fiume loop with a two-field force model:

- **Emission** (the solid object): the hull's own alpha mask, dilated by
  a one-time BFS distance transform into contour points with outward
  normals, is the fuel map; the horizon's vanishing point is the second
  emitter, spawning the inflow river biased hard toward the horizon and
  aimed down the flight path.
- **Ignition**: neutral streaks that intersect the standoff ellipse or
  hull envelope reflect (the hardened steering lobe reflects harder) and
  become flame blobs on a six-stop position-in-flow color ramp.
- **Two fields**: each ignited blob feels the coil's dipole
  B ∝ [3(m̂·r̂)r̂ − m̂]/r³ and the ram flow radial from the vanishing
  point, mixed by the MHD gate as coupling coefficient. A coupled blob
  additionally receives a perpendicular sinusoidal term — it *twirls*
  helically along its field line. This is the shield's grip rendered
  literally; the captured population is also painted directly as the
  breathing, roll-directed pillow volumes (layer 15).
- **Cascade**: hot blobs in the bow wake shed children (budgeted), so
  the burn multiplies with intensity.
- **Decay**: expired flame blobs past blackbody spawn smoke (layer 8);
  every particle carries a depth-scaled downward draft
  (150 + 430·depth px/s²) — the slipstream draining past a camera bolted
  to a falling object.

Budgets: 3000 flame, 480 smoke, 320 contrail, ~50 cloud. All stochastic
draws come from the voyage RNG; the sim's own RNG is untouched by
visuals, so the nine corridor gates stay bit-deterministic.

## V. The Guidance Overlay

Instrumentation is layered in the same order every frame: gauge panel,
telemetry strip, per-ship dial cluster (ranges derived from the Vehicle:
g-max = 2.5·G_limit, wall redline = (Q̇_lim/σε)^¼, Mach max from entry
speed, LOAD = m/m_ref), orbit inset, **expected-profile h–V monitor**
(reference = the same seed's autoland flown headless at interface),
ILS box, green HUD frame, then three teaching layers:

1. **Trajectory projection** — `Sim.Predict` (frozen L/D, Euler 0.5 s,
   420 s horizon, refreshed at 4 Hz) plotted as dots at true depression
   angles, red outside the band, ending in a LAND ring; the PAD diamond
   at true bearing *and* depression, edge-pinned when off-axis; dashed
   PIPE rails at the reference band.
2. **Flight director** — a fly-toward bug (crossrange → lateral, γ
   error → vertical), marching STEER LEFT/RIGHT chevrons with distance,
   UP/DOWN tags, ON GUIDANCE when centered.
3. **Burn warnings** — smoothed hull-loss rate drives HULL BURNING with
   the live %/s, red edge vignettes, and an imperative cue (TOO STEEP /
   TOO SHALLOW / FEED THE SHIELD); the damage-control reflex announces
   EMERGENCY OVERRIDE — PULL UP! FLY THE PIPE! while it holds the stick.

## VI. Resource Discipline

Per frame: two splat batches + two solid batches cover ~90% of luminous
primitives; the sky re-renders only on quantized (h, sun) buckets; the
full-descent prediction runs at 4 Hz; `fx.Fire` grids tick at a fixed
30 Hz accumulator. One-time costs at entry start: shield mask BFS,
reference-profile autoland (~13k sim steps), port generation. The
recorder (`GONEX_REC`) dumps every Nth frame with the provenance caption
(`GONEX_REC_CAPTION`) burned in-band; `GONEX_BOOT=fxlab` is the
isolated tuning bench.

## VII. Conclusion

The stack reads as one continuous physical event because every layer is
driven by the same state vector and drawn in one perspective fiction,
and it stays cheap because primitives never change pipelines mid-loop.
Extension points, in order of leverage: a Kage heat-shimmer pass between
layers 13 and 14; audio keyed to the same state; per-stellar palette
tints entering at layers 1–6.

## References

[1] J. Stam and E. Fiume, "Depicting fire and other gaseous phenomena
using diffusion processes," SIGGRAPH 1995.
[2] S. King et al., "Fast volume rendering and animation of amorphous
phenomena," 2000; X. Wei et al., "Simulating fire with texture splats,"
IEEE Visualization 2002.
[3] D. Nguyen, R. Fedkiw, H. Jensen, "Physically based modeling and
animation of fire," SIGGRAPH 2002.
[4] Yodacon LR-2026-03, "The reentry particle stack," 2026.
[5] `vendor/docs/reentry-console.html`, the MHD envelope model the
gauges and the corridor are derived from.
