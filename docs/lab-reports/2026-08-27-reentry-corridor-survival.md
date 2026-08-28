# Surviving the reentry corridor

*2026-08-27 — design considerations for the MHD Reentry Console, written before the
gameplay systems were implemented. The console lives at
`vendor/paulricheson/reentry-console.html`.*

**1 · The problem is energy, not fire.** A vehicle at orbital speed carries ½V² ≈ 30 MJ
of kinetic energy per kilogram — roughly seven times its own mass in TNT equivalent.
Every joule of it has to go somewhere before touchdown, and the only machine available
to dispose of it is the atmosphere itself. Reentry heating is not an obstacle on the
way home; it *is* the disposal process, seen from the wrong side. The design question
is never "how do we avoid the heat" but "how do we route the heat through the air
instead of through the ship." The console's power tab already makes the point
numerically: drag dissipates on the order of a gigawatt while the ship's own systems
draw megawatts. You do not fight that river. You steer it.

**2 · The corridor is a two-sided trap.** Entry survival is a targeting problem in the
flight-path-angle/velocity plane. Come in too steep and the density gradient wins:
deceleration and heat flux both scale up with sin γ (Allen–Eggers), and a few extra
degrees converts a survivable 4 g / 70 W/cm² profile into 20 g and a structural
failure. Come in too shallow and the atmosphere refuses you: lift and the centrifugal
term dominate, the flight path bends upward before enough energy is shed, and the
vehicle is **ejected back out of the atmosphere** on a new ellipse. Between the
undershoot and overshoot boundaries lies a corridor typically only one or two degrees
wide at the entry interface. Everything else in this document is about how to hit that
corridor, and what to do when you don't.

**3 · Skip-out is an orbit, not a death.** A vehicle that exits the atmosphere above
escape energy is gone — that is genuine orbital ejection, and the console should say
so. But the far more common case is a *bound* skip: the vehicle leaves the interface
with positive flight-path angle and sub-circular energy, which means it is simply on a
new elliptical orbit whose apoapsis is set by the exit state and whose periapsis is
still inside the atmosphere. It will come back. This is exactly aerocapture /
atmospheric flight-body capture flown deliberately: each pass through the upper air
bleeds energy, lowers the apoapsis, and lengthens the stay. The console's simulator
already detects the skip; what it should additionally report is the resulting orbit —
apoapsis, period, and the state of the next entry — so a skip reads as "you bought
time and another pass," not as an error.

**4 · Flux and load are different enemies.** Sutton–Graves convective heating goes as
√ρ·V³ — cubic in velocity, only square-root in density — so peak *flux* happens high
and fast, long before peak dynamic pressure. Integrated heat *load* is what sizes the
shield thickness, and it grows with time spent in the air. These pull the design in
opposite directions: a steep entry has brutal peak flux but a short soak; a shallow
entry has gentle flux applied for so long that the total load is worse. The KSP
community discovered this empirically on Eve — a deeper periapsis "burns less ablator"
because the pass is shorter. Any thermal-management gameplay must therefore track
*both* an instantaneous overheat meter (flux against the TPS limit) and a cumulative
soak meter (load against the shield's capacity), because a pilot can lose to either.

**5 · Energy management is trajectory management.** Since the atmosphere is the brake,
control authority over the trajectory *is* the throttle. Lift is the primary tool:
rolling the lift vector modulates how quickly the vehicle descends into denser air,
which sets the deceleration schedule, which sets flux, load, and downrange all at
once. This is why the corridor plot (h–V plane) is the pilot's primary display, and
why the game's setup screen should let the player choose the entry state deliberately
— orbit, deorbit burn, and entry angle — rather than starting mid-fall. The choice of
where to spend Δv is the first move of the game, made before the atmosphere is even
touched.

**6 · The Oberth effect prices the deorbit burn.** A burn's energy effect is Δε = v·Δv:
the same propellant removes the most orbital energy where the vehicle is moving
fastest, at periapsis. A retrograde burn at *apoapsis*, where the ship is slow, is
cheap per metre-per-second but weak per joule — which is exactly why it is the right
place to lower a periapsis gently into the entry corridor, while a periapsis burn is
the right place to shed gross energy. The setup screen should expose this: a burn-point
angle selector around the orbit, a Δv slider, and a live readout of the resulting
interface velocity and flight-path angle, so the player can *feel* that 100 m/s spent
at one true anomaly buys a different entry than 100 m/s spent at another.

**7 · The MHD window closes at the top…** The plasma shield's steering authority is not
available everywhere, and the reasons are physical, not tuning. Above roughly 95 km
the mean free path exceeds a tenth of the nose scale (Kn > 0.1): there is no
continuum shock layer, only individual molecules arriving ballistically. The Lorentz
force acts on charged particles and reaches the *neutral* stream only through
collisions — no collisions, no coupling, no matter how strong the coil. The air up
there is too thin to be a working fluid at all. Magnetic braking and magnetic steering
are simply not on the menu above the continuum limit, and the console grays its
interaction-parameter trace there for that reason.

**8 · …and at the bottom, where plasma becomes mere gas.** Descending, velocity bleeds
off, stagnation enthalpy falls, and the shock-layer temperature drops out of the
ionisation regime. Saha's exponential does the rest: the ionised fraction collapses
through six decades even while absolute density climbs. Below roughly 50 km the layer
in front of the ship is no longer an electrically conducting plasma the field can
grip — it is ordinary dense gas, and the magnetic "containment" degenerates into
nothing. The air still cushions — drag is stronger than ever — but it cushions as
*gas*, aerodynamically, through pressure on the body, not through the field. Steering
authority must hand over from the magnetopause to conventional aerodynamic lift
exactly here. The playable MHD corridor, ~55–95 km, is an output of the physics, and
the game should show the handover, not hide it.

**9 · The lithium heat shield is also the rudder.** Seeding the shock layer with
lithium (ionisation potential 5.39 eV against nitrogen's 13.6) multiplies
conductivity by orders of magnitude, which is what gives the coil its grip — but it
does double duty. The seed cloud absorbs radiative flux and re-emits roughly half of
it outward, a genuine (factor-of-two, not factor-of-ten) heat-shield effect; and
because the standoff distance depends on local field strength as B^1/3, biasing the
toroid asymmetrically moves the magnetopause off-axis and generates a steering moment
with a lever arm of several metres. Lithium is thus shield, seed, battery chemistry
and propellant in one commodity — navigation by heat shield is the honest description,
and it is the loop the console's closure table already prices.

**10 · Toroid curls and particle containment.** What the shield cross-section should
show, and the current console does not, is the *mechanism*: the coil's dipole field
lines curling from pole to pole, seeded ions gyrating along them, and the ram plasma
reflected at the magnetopause — an energy reflector in the literal sense, a pressure
balance surface where the field turns the flow. Containment quality is readable from
two numbers the model already computes: the coupling gate g (is the flow gripped at
all?) and the Hall parameter (are electrons completing gyro-orbits between
collisions?). The visualization should render three regimes honestly — free-molecular
particles streaming straight through the curls untouched; the coupled corridor with
ions turned and channeled around the bubble; and the low-altitude collapse where the
curls persist but nothing charged remains to ride them and the neutral gas simply
piles up against the body.

**11 · What the Kerbal players already know — the Eve syllabus.** Eve is KSP's Venus
analogue and its reentry final exam, and the community guides converge on numbers
worth stealing. Atmosphere top ≈ 90 km; aerocapture periapsis 55–70 km depending on
arrival energy, and never below ~70 km on the first interplanetary pass or an
unshielded ship is obliterated; hold retrograde behind the shield until below
~1500 m/s because bare parts (crew cabins especially) have low temperature limits; fly
shields wider than the body so aerodynamics *forces* the safe attitude. Translated to
our console: the interface at 122 km, a corridor selector on the setup screen, an
overheat model that punishes exposed operation above the TPS limit, and a magnetic
bubble that is, literally, a shield wider than the body whose width the player buys
with field and seed.

**12 · Overheat as a game mechanic.** KSP's thermal gauges work because they give a
*rate* the player can trade against: parts heat toward destruction while flux exceeds
what they can shed, and cool when it doesn't. The console should adopt this: an
overheat meter that integrates (q̇ − limit) when the TPS is over its rated flux and
relaxes when under, with destruction when it saturates — alongside the cumulative
soak meter from ¶4. This converts the static "peak flux vs limit" verdict into a
survivable-if-brief dynamic, which is the true physics of ablators and the actual
skill of corridor flying: you may cross the red line, but you must be decelerating
fast enough to come back out of it before the meter fills.

**13 · Power management closes the loop.** The shield is not free: cryogenics for the
coil, seed conditioning, the phased array — megawatts, drawn exactly when the vehicle
is busiest. The game should carry a finite battery (the console's own closure table
sizes it at a few GJ) and a finite lithium tank shared between seed and stored energy,
and it should enforce the consequence: battery empty → coil quenches → the magnetic
parachute vanishes mid-corridor and the bare-body trajectory and heating resume.
Power management then becomes the third gauge the pilot flies — spend seed early to
fatten the drag bubble and shorten the soak, or hoard it for steering authority at the
handover? That is a real trade with no dominant strategy, which is what makes it a
game.

**14 · The target landing indicator.** Borrowed from KSP's Trajectories mod: at every
instant, draw two futures from the current state under the same conditions. The
*ballistic* projection propagates the vehicle with drag switched off — a pure conic
falling to the surface — and the *atmospheric* projection runs the full model,
drag, bubble and all, to touchdown. The gap between the two impact points is a live
measurement of how much work the atmosphere (and the shield) is still going to do,
and watching the atmospheric marker walk toward the ballistic one as energy is spent
is the clearest possible display of energy management. Both belong on the orbit view,
as vectors from the ship, with downrange numbers.

**15 · What gets implemented, in order.** From this writeup, the console gains: (a) an
orbit setup panel — apoapsis, periapsis, burn-point angle selector, deorbit Δv, with
the Oberth readout and the derived interface state; (b) an orbit-view instrument
showing Earth, the orbits before and after the burn, the entry arc, skip-out ellipses,
and the two landing projections; (c) skip-out reported as an orbit with apoapsis,
period and next-pass state — and escape reported as ejection; (d) overheat and
heat-soak meters with destruction outcomes, per ¶12; (e) battery and lithium tanks
with in-flight depletion consequences, per ¶13; (f) a gauge cluster — g-load, flux
fraction, wall temperature, soak, charge, seed — because pilots read dials, not
tables; and (g) the shield cross-section: toroid curls, particle containment, and the
three honest regimes of ¶10. The physics core already knows all of these truths; the
work is making the instrument panel confess them.

## Sources

- [KSP Wiki — Tutorial: How to get to Eve](https://wiki.kerbalspaceprogram.com/wiki/Tutorial:How_to_get_to_Eve)
- [KSP Wiki — Aerobraking](https://wiki.kerbalspaceprogram.com/wiki/Aerobraking)
- [KSP Fandom — Reentry](https://kerbalspaceprogram.fandom.com/wiki/Reentry)
- [Steam Community — how to survive re-entry](https://steamcommunity.com/app/220200/discussions/0/364040166692118402/)
- [Steam Community — Early game: Surviving re-entry tips](https://steamcommunity.com/app/220200/discussions/0/618460171329295548/)
- [KSP Forums — How to land at Eve](https://forum.kerbalspaceprogram.com/topic/200554-how-to-land-at-eve/)
