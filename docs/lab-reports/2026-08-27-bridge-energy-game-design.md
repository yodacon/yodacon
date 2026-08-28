# The bridge is a power grid: an energy-management game plan

*2026-08-27 — game design for a multi-console "spaceport bridge simulator" in the
yodacon universe, companion to the reentry writeup
(`2026-08-27-reentry-corridor-survival.md`). Implemented in Go in the `gonex/`
submodule: the `internal/power` package and its wiring into every game mode.*

## Premise

Artemis-style bridge simulators seat a crew at consoles — helm, engineering,
science, weapons — and make the fun out of *coordination under scarcity*. The
yodacon frame keeps the consoles and swaps the fantasy: you are not a warship, you
are a **courier**. The ship is a light freighter with a cargo hold, a reactor, and a
lithium habit, flying contracts between planets in a sandbox system. Raiders exist
the way weather exists — a hazard to be survived and outrun, not a score to be
farmed. Every console, in every mode, is ultimately operating one machine: **the
ship's energy economy**. That is the thesis of the whole design: there is exactly
one game here, energy management, wearing five different costumes.

## The single currency

Everything the ship does is a conversion between six stores of energy, and the
game's depth comes from the conversions being lossy, rate-limited, and mutually
exclusive:

| Store | What it is | Character |
| --- | --- | --- |
| **Kinetic** | orbital velocity, ½mV² | The biggest number on the ship by far. Free to spend into the atmosphere (aerobraking), brutally expensive to buy back (propellant). Momentum *is* a battery. |
| **Chemical** | propellant in the tanks | The only store that works everywhere, and the heaviest per joule. The Oberth effect makes *when* you spend it matter as much as how much. |
| **Electrical, deep** | batteries (GJ) | Slow, dense, steady. Runs the coil cryogenics, the pumps, life support. |
| **Electrical, fast** | capacitor bank (MJ) | Shallow and violent. The only thing fast enough to feed a shield taking a hit. Recharged from the reactor between volleys. |
| **Field** | energy stored in the coil and shield screens | Does no work but must be held; collapses (quench) if its supply is interrupted, and its collapse is itself a hazard. |
| **Thermal** | heat soaked into the structure | The *anti-store*. Every conversion above deposits into it, it must be rejected through radiators, and the radiators do not work everywhere. |

And one commodity that ties the economy to the lore: **lithium**, which is
simultaneously battery chemistry, plasma seed, and propellant. The courier's cargo
and the courier's survival draw on the same shelf.

## The consoles

Five stations. In crew play each is a person; in solo play the player *is* the mode
transition, hot-seating to whichever console the current phase makes urgent while
the others run on dumb holds.

1. **Helm** — trajectory, burns, entry corridor steering, the landing hoverslam.
   Spends kinetic and chemical energy.
2. **Engineering** — the reactor throttle and the power allocation bus: who gets
   the megawatts *right now*. The heart of the game; every other console is a
   client of this one.
3. **Screens** — shield emitters and point defense. Spends capacitor energy in
   bursts; negotiates with Engineering for recharge priority.
4. **Thermal** — radiators, heat sinks, coolant. Watches the one gauge that only
   ever goes up unless someone acts. Owns the TPS budget during entry.
5. **Quartermaster** — the spaceport console: contracts, cargo, and the shop.
   Buying **generators (sustained MW), batteries (GJ), capacitors (burst MW),
   radiators (rejection MW)** is explicit progression — the stated goal of getting
   rich is really the goal of building a grid that can survive richer contracts.

## The modes, and what each one asks of the grid

**Spaceport.** The strategy layer. Pick a contract (destination planet, cargo,
pay), then spend credits on the grid. The trap is mass: every generator, battery,
and radiator bought makes the ship heavier, which raises the ballistic coefficient,
which makes every future entry hotter and every landing burn thirstier. The shop is
therefore not a monotonic power curve — it is a loadout *choice*, and overbuying is
a real failure mode.

**Transit.** Long, quiet, and the only place heat is cheap: radiators work at full
rate in vacuum, so this is where you run the reactor hard, top the batteries, and
bank margin. The skill beat is the **Oberth window**: the departure and capture
burns have a marked periapsis interval where a second of burn buys visibly more
orbit-energy change than the same second spent elsewhere. Burning early because you
were nervous is the transit-mode mistake the game teaches out of you.

**Intercept.** A raider closes; the encounter is survived, not won — hold together
until you are outside their envelope. Now the grid inverts: demand is *peaky*, not
steady. Shield hits drain the capacitor bank in milliseconds; the reactor can only
refill it between volleys; point defense wants the same megawatts; and every
megawatt through the screens dumps waste heat you cannot fully reject because the
radiators are your biggest, most fragile target and fly retracted in a fight. So
battle energy management is a rhythm game on the capacitor: pre-charge before the
telegraphed volley, choose what eats the hit, vent heat in the gaps. Hull hits
don't kill you — they cost cargo, which costs payout, which is the courier's kind
of death.

**Entry.** The reentry console's physics, inherited whole (see the companion
report): the plasma brake works only in its corridor (~55–95 km), the overheat
meter and TPS soak both hunt you, and the handover to aerodynamic steering is
mandatory because below the corridor the shock layer is neutral gas the coil cannot
grip. The grid inverts again: demand is *steady and non-negotiable* (coil
cryogenics, seed conditioning), radiators are useless inside a plasma sheath, so
the whole phase runs on the batteries filled during transit while heat climbs on a
one-way meter. Entry is the bill for how well you flew every previous mode: excess
arrival velocity you failed to shed at the Oberth window arrives here as extra
megajoules per square metre.

**Landing.** The endgame of the energy ledger. Whatever velocity survives entry
must be killed by the engines — chemical energy, the expensive kind — with battery
enough left to run the pumps. A hoverslam with a dry battery is the game's signature
loss. Touch down under 5 m/s with cargo intact and the ledger closes.

## Transitions are the game

The modes are not levels; they are one continuous state vector — velocity, mass,
battery, capacitor, seed, propellant, heat, hull, cargo — re-weighted five times.
Nothing resets at a phase boundary, which is exactly why the phases feel different:
the *same* battery gauge is a luxury in transit, a war chest in intercept, a
lifeline in entry, and a verdict in landing. Transitions are telegraphed (a raider
contact alarm, an entry-interface countdown) so the player's job at each boundary
is a deliberate **grid reconfiguration**: retract radiators and pre-charge caps
before the intercept; dump heat and top batteries before the interface; reserve
the landing budget before committing to the corridor. Getting caught in the wrong
configuration is the punishment loop; learning the handovers is mastery.

## Scoring: the margin is the score

Per the reentry report's conclusion, this is "a game of saving fuel and reentry
resources." Payout = contract value × cargo fraction, plus explicit bonuses for
**resources landed with**: propellant, battery charge, seed lithium, TPS margin.
That makes efficiency the profit motive rather than a style grade, closes the loop
back to the shop, and quietly implements the lore: a courier's reputation is
margins, not victories.

## Sandbox planets

Destinations vary the physics, not just the scenery, so each one re-prices the
energy stores against each other:

- **Vella Point** (airless moon): no atmosphere, no plasma brake, no entry heating —
  and no aerobraking either. Kinetic energy must be paid down entirely in
  propellant. Low pay, teaches the landing burn.
- **Kestrel** (thin, Mars-like): aerobraking exists but is weak; entries are cool
  but nearly ballistic, and the landing burn is still substantial.
- **Homefall** (Earth-like): the baseline corridor game.
- **Brackwater** (thick, Venus-like — the Eve of this system): capture is nearly
  free and the landing burn trivial, but entry flux is brutal and the TPS budget is
  the whole contract. Highest pay in the book.

## What is implemented, in Go, in gonex

Gonex already had the mode skeleton — flight, warp, deorbit, entry, docked — and a
`Voyage` carrying credits, fuel, lithium and damage between them. This design adds
the missing spine, `internal/power`:

- **`power.Grid`** — reactor (MW), deep battery (MJ), capacitor bank (MJ, the only
  store fast enough for a hit), radiators (vacuum-only rejection), a heat pool with
  a ceiling, and the outfit mass ledger. `Step` resolves a frame's load against the
  plant (brownout below 1.0), banks reactor surplus caps-first, and accrues heat;
  `SpendCap` is the burst path for shots, shield hits, and coil overdrives.
- **Flight/battle** (`engineering.go`, world hooks): the E key cycles Artemis-style
  allocation presets — BALANCED / FLANK SPEED / SCREENS / CHARGE STORES — trading
  thrust scale against capacitor recharge. The player's gun fires only if 6 MJ of
  capacitor clears (`World.FireGate`); incoming missile damage is eaten by the
  screens at 2 MJ per point before it touches hull (`World.ShieldFilter`). An
  always-on ENG strip draws CAP/BATT/HEAT.
- **Warp/cruise**: the same grid steps with radiators live — transit is where the
  stores refill, exactly as ¶Transit argued.
- **Entry** (`entrymode.go`, `reentry.Sim.Supply`): the coil's ~4 MW draw drains
  the battery in real time with the radiators blind; a flat battery collapses
  plasma authority to near-bare-body (`authority × (0.35 + 0.65·Supply)`); the coil
  overdrive (B) costs 30 MJ of capacitor up front; grid overheat cooks the flight
  computer. The cockpit gained BATT and HEAT bars beside the lithium gauges.
- **Spaceport** (`dockmode.go`): shore power walks the stores back up on the pad,
  and the new **Outfitter** (O) sells the five power outfits — auxiliary generator,
  deep battery bank, capacitor array, radiator wing, thermal mass sink — each
  priced in credits *and tonnes*, and `startEntry` adds `Grid.OutfitKg` to the
  entry vehicle's mass, so the mass spiral of ¶Spaceport is enforced by the same
  RK4 integrator that flies the corridor.

## Future work

Point defense as a separate capacitor client; per-planet raider encounter tables
from the gazetteer; the Oberth window as a playable beat in the deorbit sequence
(the burn is currently scripted); splitting consoles across machines for actual
crew play (the grid state is small enough to sync at 10 Hz); and letting the trade
center deal in the lithium commodity itself, closing the last loop between the
ship's economy and the setting's.
