# The lithium fuel cycle, and the transport bottleneck it exposed

**22 September 2026** · `gonex/internal/{econ,industry,universe,traffic,power,reentry}`

Fuel used to be a line on a board. `Fuel cells` cost 300 credits a ton, a
world with volatiles and copper made them, and nothing else in the game cared.
This report adds the other fuel — **radioactive heavy lithium**, in two forms
that are not interchangeable — and with it a five-stage industrial line, a
class of world that exists to run it, two new kinds of agent, a merchant fleet
that sizes itself to what the board is paying, a reactor ladder on the
outfitter's shelf, and a plasma-confinement ladder for the reentry pillow.

It also found **eleven faults**, most of them older than this work, and four
of them the kind that stop an entire tier of the economy dead without logging
a word. Section 9 is the useful half of this document.

The conservation law is untouched and still holds: mass balances and the
ledger balances at every checkpoint, on every seed, over two simulated years
of the full gazetteer.

---

## 1. The fiction, and why it has a shape

Heavy lithium is the only thing a hyperdrive will burn. It is not dug and it
is not refined in one step — it is **bred**, and breeding is a licensed
activity nobody will licence anywhere pleasant.

```
  Spodumene ──mill──▶ Lithex ──hot cell──▶ Lithium ──breeder──▶ Heavylith
  (crust)    +acid    (conc.)   radiant      (metal)  +volatiles  (fissile)
                                smelting                              │
                                                    ┌─────────────────┴──────────────┐
                                             press  │                                │  melt loop
                                            +steel  ▼                                ▼  +fluid
                                                 PELLETS                           MELT
                                            clad solid fuel              stable molten-salt fuel
                                          (thermal piles take it)     (fast loops circulate it)
```

Five stages, and not one can be skipped. Three of the five will only stand up
on a world with a dose rate nobody can live under. And the two things that
come out of the far end are **the same energy in different packaging**, with
no conversion anywhere outside a refinery — so the reactor a pilot bolts in
decides which half of the galaxy's refineries are their suppliers.

That is the whole design. Everything below is downstream of it.

### The seam *is* the dose

`econ.Dose(seed, stellar, pop)` and the spodumene endowment are **the same
draw**. A clean world has no spodumene at all, however rich it is in
everything else; a hot world's reserve scales with exactly how hot it is.
This is the one place in the game where two facts about a world are forced to
be the same fact, and it is what puts the fuel under the worlds nobody wants.

Two disqualifications, both hard rather than tapered:

- most worlds simply never draw a body (`hotChance` 0.22);
- a world above `habitablePop` is clean by definition — the city is the proof,
  and it is also where every capital is drawn from, so **a capital can never be
  randomly condemned**. A taper could not promise that, and a condemned capital
  is a colour deleted along with the trifecta's balance proof.

### What a hostile world *is*

Not a smaller version of a city — a different kind of place:

| | clean world | milling class | smelter class | breeder class |
| --- | --- | --- | --- | --- |
| dose | 0 | ≥ 0.10 | ≥ 0.35 | ≥ 0.55 |
| population ceiling | 32 M | ~1.35 M | ~975 k | ~675 k → 40 k floor |
| growth | full | taxed 94 % at full dose | | |
| licensed line | — | `Lithium milling` | `Radiant smelting` | `Fuel pellets` / `Fuel melt` |
| worked by | a workforce | machines (`autoCrew`, scaling with dose) | | |
| flag | a polity | **whoever is paying** | | |

That last row is the trading-zone rule and it is one line in `mine()`:
Konquest's neutrals do not produce, *except* a hostile world, which is not a
polity with a workforce that can strike but a licensed site with machines on
it. Nobody holds the hot worlds; everybody buys from them.

Which of the two finishing lines a licensed world pours **alternates on its
stellar ID**, so the map carries both fuels and a pilot with a fast loop has
to go and find a melt world rather than buying whatever the nearest refinery
happens to be pouring.

---

## 2. Matter: what was added

`econ.Material` went from 22 to 30, and the board from 6 commodities to 8.

| tier | added | why |
| --- | --- | --- |
| **board** | `Pellets` 860, `Melt` 1020 | the two fuel forms, priced above everything else on any board |
| **refined** | `Lithex` 185, `Lithium` 540, `Heavylith` 1650 | the line; `Heavylith` is the most valuable ton in the game |
| **refined** | `Acid` 160, `Fluid` 235 | the pure chemical liquids a hull and a mill are both made of |
| **crust** | `Spodumene` 130 | finite, and the only place any of it comes from |

Two new predicates carry the travel rules, and they exist because two quite
different arguments produce the same answer:

- `Hot()` — `Lithium` and `Heavylith` travel in a shielded cask or not at all.
  A cask that survives a jump costs more than the ton inside it, so **the
  finishing plant stands beside the breeder rather than beside the customer**.
- `Bulkable()` — `Steel`, `Lithex`, `Acid`, `Fluid` are refined but ship like
  goods. Steel because a city eats it; `Lithex` because the hostile worlds
  *import* concentrate and could not run a hot cell otherwise; the chemicals
  because every yard in the game buys them by the tanker.

### Ships are metal and chemical liquid

The yard recipe changed, and this is the coupling that makes the tanker trade
worth flying:

```
Yard:  0.55 Steel + 0.15 Chips + 0.08 Fuel cells + 0.10 Acid + 0.12 Fluid  ⇒  0.90 Hull
```

Plate and wiring, the acid that etched them, and the fluid in every actuator.
A yard with no chemical works within reach of a lane presses no plate.

---

## 3. Process and mass flow, in full

Every branch, with yields. Mass balances at every node; the remainder is slag.

```
FERRITE ─┬─ Crusher 0.92 ──────────────────────────▶ ORE ─────────▶ construction
         └─ Smelter 0.62 ─▶ STEEL ─┬─ Arsenal    ─▶ ROUNDS ─▶ garrisons, battle
                                   ├─ MissileWks ─▶ MISSILES
                                   ├─ Yard       ─▶ HULL ─────▶ the merchant fleet
                                   ├─ Press      ─▶ PELLETS
                                   └─ cities (2.4 t/d per Mpop)

CUPRITE ── Refinery 0.48 ─▶ COPPER ─┬─ Fab      ─▶ CHIPS
                                    └─ CellPlant ─▶ FUEL CELLS

SILICATE ─ Furnace 0.40 ─▶ SILICON ─── Fab

VOLATILES ┬ Cracker 0.70 ─▶ POLYMER ─┬─ CellPlant / Pharma / Arsenal
          ├ ChemWorks ─▶ ACID 0.30 ─┬─ OreMill (the leach)
          │             FLUID 0.24 ─┼─ MeltLoop (the carrier salt)
          │             POLYMER 0.22 └─ Yard
          └ Breeder (blanket)

BIOMASS ──┬ Mill 0.85 ─▶ LUMBER
          └ Thresher 0.75 ─▶ GRAIN ─┬─ Cannery 0.90 ─▶ RATIONS ─▶ growth
                                    └─ Pharma 0.55 ──▶ MEDICINE

SPODUMENE ─ OreMill 0.45 ─▶ LITHEX ─ HotCell 0.55 ─▶ LITHIUM ─ Breeder 0.62 ─▶ HEAVYLITH
                                                                                   │
                                                              Press 0.86 ◀─────────┴──────▶ MeltLoop 0.90
                                                             PELLETS                        MELT

RETURNS   consumption(organic) ─▶ COMPOST ─ Composter 0.60 ─▶ BIOMASS (surface only)
          dead hull            ─▶ SCRAP   ─ Breaker   0.75 ─▶ STEEL
SINK      everything else                 ─▶ SLAG (counted, worthless)
```

Two loops send the flow uphill — the composter and the breaker's yard — and
now a third does, **inside a hull**: see §5.

---

## 4. The agents

### The harvester (gatherer / minter)

The population-scaled mine was the one hard ceiling in the economy: a world
lifts tons in proportion to the people living on it, so **a rich rock with
nobody on it produced nothing, for ever**, and no amount of shipping could
help because there was nothing at the pithead to ship.

A harvester flies empty to a seam, lifts crust straight out of the ground into
its own hold against a royalty paid to whoever holds the rock, and carries it
to the nearest port that wants it. A hold at a time. It is extraction capacity
that is **mobile**, so it goes where the shortage is; and the royalty is how
the outer map earns the credits it buys food with.

Mass-conserving by construction: the tons come off a `Reserve`, which only ever
falls. Capped at a quarter of a colour's fleet — a merchant marine that turns
entirely into miners stops carrying anything, and the shortage it was sent to
fix gets worse.

### The survey (prospector / pioneer)

Carries nothing, sells nothing, earns nothing. It flies to a seam, reads it,
and leaves. For 90 days afterwards the world digs **+45 %** for the same
workforce, and every world one jump away digs **+20 %** — a survey reads a
formation, not a property line, and the brief is public. It is the only thing
in the game that raises extraction without raising population, and the only
thing a government does purely because the arithmetic says so.

Sent to the world with the widest gap between what its industry wants out of
the ground each day and what its workforce can lift.

### The merchant fleet sizes itself

The census is still honest — a hull nobody is looking at is a ship with a
position and a manifest. What was wrong was the **size**. Two rules now:

- **Opening**: hulls proportional to worlds held, because a trade network's
  size is a property of the map and not of a constant somebody typed once.
- **Growth**: every day each colour measures *berth pressure* — the credits of
  margin still sitting unserved on its board, per hull afloat — and presses
  plate above 90 k, breaks a ship up below 22 k. The gap between the two
  thresholds is deliberately wide: a fleet that commissions and lays up around
  a single threshold oscillates.

A route that pays better gets more ships pointed at it without anybody
deciding to point them. Nothing is minted: a commissioned hull is `Hull` tons
out of a yard's warehouse, a laid-up hull is the same tons put back on the same
shelf, and a new `LaidUp` status keeps the row so the same ship comes back
under the same name.

---

## 5. Ship reactors: reaching the fuel's potential

A ton of heavy lithium carries the same energy wherever it is loaded. What
decides how much of it a ship can *use* is the machine it is loaded into.

| class | takes | burnup | range | breeding | MW | mass |
| --- | --- | --- | --- | --- | --- | --- |
| **Thermal pile** — light-water moderated | Pellets | 5.5 % | ×1.0 | — | 3.0 | stock |
| **Sodium fast loop** — unmoderated, molten salt | Melt | 19.5 % | ×3.5 | — | 4.6 | +7 t |
| **Shipboard breeder** — fast loop + fertile blanket | Melt | 25.0 % | ×4.5 | 0.35 t/t | 5.8 | +16 t |

The breeder is the third uphill loop in the game: it burns its charge *and*
transmutes fertile `Lithium` from a blanket it is carrying into fresh
`Heavylith`. It does not mint fissile material — the tons come out of the
blanket pool — which is precisely the distinction the books care about.

These are the reason the fuel economy has a **player** in it rather than just
a price. Without the ladder, heavy lithium is a commodity with a number next to
it. With it, every rung is an argument about range, mass and which refineries
in the galaxy will sell to you.

---

## 6. Confining the reentry pillow

The envelope the Yodacon flies behind is a **magnetopause**: the coil's dipole
pushes out with `B²/2μ₀`, the flow pushes in with `ρV²`, and the stand-off is
where they balance. A dipole falls off as `r⁻³`, so its pressure falls as
`r⁻⁶`, and the model solves

```
r_mp / R_n  =  ( p_mag / p_flow ) ^ (1/6)
```

**Nobody is buying their way out of that exponent.** To stand a shock off twice
as far you need sixty-four times the magnetic pressure. What a yard *can* sell
is a fix for one of four distinct ways the balance goes wrong — and each is a
different piece of hardware because each is a different piece of physics.

| failure mode | outfit | the hook |
| --- | --- | --- |
| **the field is too weak** | HTS coil rewind, +0.45 T | stand-off ∝ B^⅓ — honest, expensive, diminishing |
| **the bottle leaks at the poles** | Multipole cusp ring | a bare dipole has two axial cusps where field lines run *into* the hull and flow funnels onto the nose. Plugging them raises usable `p_mag` — and cuts wake-loading drag by two thirds, which is where it actually earns its price |
| **the pillow is symmetric** | Phased steering array | drives current asymmetrically, leaning the magnetopause: +45 % commandable L/D, and MHD grip several km higher. Paid for on the power ledger, because it is driving current against a resistive plasma |
| **the air is too thin to grip** | Seed injection ring | MHD needs a conducting continuum; high up there is nothing to push against however hard you push. Put the mass there yourself — a puff of heavy seed ahead of the nose collapses the local Knudsen number. **Inertial** confinement: the pillow is held by momentum you brought with you |

Plus a cryoplant uprate (−35 % refrigeration, hold the field for the whole
corridor).

The fourth rung is the interesting one, and it is tested by the property that
justifies it: at 88 km, **the injection ring beats tripling the coil**, because
tripling a field that has nothing to grip buys nothing at all. Every rung is a
multiplier on a term that was already in `stateAt` — nothing here is a new
force, only four ways of being better at the one the model already has. The
zero value is exactly neutral, so a stock hull flies as it always did.

---

## 7. Prices are a consequence, not a table

Price was already scarcity — days of cover against real demand. Two things
changed.

**Lane lengths exist.** Until this pass every lane in the game was the
registry's default 260 Mm, which meant the route ranking's *margin per
megametre* was margin divided by a constant: 109 ports all equally far from
each other, and **geography with no effect on trade whatsoever**.
`ChartLanes` now writes the real hop count into every lane — 60 Mm in-system
plus 180 Mm per jump, so one hop is about a week and a five-jump haul is a
month and a decision.

**A sited world bids like a starving one for its own feedstock.** A world
already pays up to 7× for rations when it is hungry, because people will pay
anything for the next meal. A refinery short of acid is not inconvenienced, it
is *shut* — no other industry, no population worth the name, nothing else to
sell. At the ordinary 3× curve it could not outbid ordinary trade: acid tops
out at 3 × 160 while ore tops out at 3 × 220 two jumps nearer, so the couriers
went where the margin was, correctly, and fifteen refineries wanting 525 t of
reagent a day between them were served sixty. The scarcity curve was right and
the **steepness** was wrong: desperation is not the same shape for a cargo you
can do without as for one you cannot.

---

## 8. The numbers

Full gazetteer — 109 ports, real jump map, real populations — flown 730 days.
`GAZ=1 go test ./internal/universe -run TestGazetteer -v`

### The map as founded

| | seed 20260922 | seed 7 | seed 99 |
| --- | --- | --- | --- |
| ports, by flag | Red 10 · Green 26 · Blue 20 · neutral 53 | same | same |
| hostile worlds | 15 (14 %) | 19 (17 %) | 24 (22 %) |
| breeder / smelter class | 10 / 5 | 9 / 10 | 15 / 9 |
| refineries standing | 10 pellet · 9 melt | 8 · 8 | 15 · 12 |

### Steady state, projected at genesis vs. delivered after two years

| | nameplate | appetite | cover | **made** | **% of appetite** |
| --- | --- | --- | --- | --- | --- |
| Pellets | 359–609 t/d | 413–443 t/d | 0.84–1.47× | 5.7–10.2 t/d | **1–2 %** |
| Melt | 438–689 t/d | 267–286 t/d | 1.60–2.59× | 7.8–23.3 t/d | **3–8 %** |

The fuel industry is **designed to cover its own demand and delivers two per
cent of it.** That gap is the headline result of this pass, and §10 is about
why.

### The rest of the economy, seed 20260922, t/day

| | made | mined | hauled |
| --- | --- | --- | --- |
| Acid | 496.3 | — | 86.7 |
| Fluid | 397.1 | — | 33.9 |
| Spodumene | — | 218.0 | 0.0 |
| Steel | 529.7 | — | 37.3 |
| Chips | 60.7 | — | 11.2 |
| Ore | 1629.0 | — | 74.2 |
| Rations | 1776.5 | — | 19.4 |
| Rounds | 68.5 | — | 4.2 |
| **Hull** | **0.0** | — | 0.0 |

### The three prongs

| | worlds | pop | hulls / cap | delivered (lifetime) | berth pressure |
| --- | --- | --- | --- | --- | --- |
| Red | 10 | 75 M | 30 / 50 | 301.5 kt | 8 406 k cr/hull |
| Green | 26 | 123 M | 78 / 130 | 674.3 kt | 5 795 k cr/hull |
| Blue | 20 | 157 M | 60 / 100 | 577.8 kt | 6 583 k cr/hull |

Delivery parity is much better than it was: before the polity map was read,
the recorded asymmetry over 200 days was Red 6.6 kt against Green 15.7 kt.
It is now within a factor of 3 across three seeds (worst case Red 222.8 kt against Blue 655.9 kt), and the residual is Red's
ten worlds against Green's twenty-six — **the shape of the map, not the table**.

### Conservation

| | result |
| --- | --- |
| mass | **BALANCED** at every checkpoint, every seed, 730 days |
| credits | **BALANCED** — ~123 M cr in circulation, every one in a purse |
| reserves | monotonically falling, always |
| spodumene worked out in 2 years | 1.8 – 3.2 % |
| replay | identical from the same seed |

### Throughput, before and after

| | voyages / deliveries |
| --- | --- |
| 11-world rig, pre-pass, 365 d | 642 voyages, 73.2 kt |
| gazetteer, 48 hulls, 730 d | 316 kt total |
| gazetteer, 168 hulls + per-berth dispatch + real lanes, 730 d | **1 554 kt total** (×4.9) |

---

## 9. Eleven faults, and what each one cost

Same method as every previous layer in this economy: **fly it and read it.**
Not one of these would have failed an assertion about a single function; all
eleven were obvious within seconds of printing a year of trade.

**1. The mandate sited the refinery but not the mine.**
Kestrel stood up as a melt refinery wanting 142 t/d of spodumene. Its second
chain — an ordinary copper line wanting 177 t/d of cuprite — took the whole
135 t/d dig budget every day, because the budget is allocated greedily by the
size of the want. **Zero tons of fuel in 365 days**, and nothing logged a
complaint. *Fix: a mandated line digs first, exactly as the gardens eat first.*

**2. A throttled plant strip-mines a finite seam into a heap.**
With the mine fixed, Kestrel lifted **81 540 t** of spodumene in a year to make
1 775 t of melt, because the mine dug against a want the imported chemicals
never let the plant satisfy. The reserve is the only finite thing in the game
and digging it to make a pile is the one irreversible mistake a world can
make. *Fix: `MineNeed` stops at 20 days of cover. Mining fell to 9 622 t;
output rose.*

**3. Acid and fluid competed for the same rank slot on the same seam.**
`Rank` breaks ties on catalogue order, so whichever came first was made in tens
of thousands of tons and the other in hundreds — acid 308 t/yr against fluid
39 786 t/yr, then exactly reversed when the order changed. Every yard and every
mill in the galaxy was throttled by whichever had lost. *Fix: one cracking
column, both streams.*

**4. …which then displaced the galaxy's only polymer source.**
Polymer has no chain of its own; it exists as the middle stage of a powercell
line and as that line's surplus. The moment the chemical works started winning
volatiles slots, polymer production fell to **227 t in a year against a single
capital's demand of 184 t a day**. Every arsenal fell silent and two of three
capitals rated zero. *Fix: the cracking column yields acid, fluid* and *polymer
— they are the same barrel cut at different points.*

**5. Two plants on one warehouse, served in list order.**
The ore crusher stands first in the list, asks for the whole day's ferrite and
gets it; the steel mill beside it runs at zero for ever. The world's own
`Describe()` printed both plants at full rate and the bottleneck report showed
nothing wrong. The galaxy made **2 204 t/d of ore against 35 t/d of steel** —
with an appetite for steel of nine hundred. *Fix: contested inputs rationed in
proportion to demand. Steel went to 427 t/d immediately.*

**6. Distance did not exist.**
Every lane was the default 260 Mm, so `Value()/Length` was `Value()/260`.
*Fix: `ChartLanes` off the real jump map.*

**7. The shuttle rule assumed a map the game does not have.**
"Intermediates move in-system; pay for a Lane otherwise" is exactly right for
a map with several stellars per system. The recovered gazetteer has **one
stellar in each of its 109 systems**, so "same system" was never true for any
pair of worlds, governors rarely bought Lanes, and copper, silicon, polymer,
grain and pure lithium **could not move anywhere, ever**. *Fix: "local" now
means within one jump, which keeps the point of the rule and makes it
expressible on the real map.*

**8. A hull only loaded from the galaxy's global top-N list.**
On a 109-port map the odds that any of the galaxy's twenty best runs begins at
this particular berth are negligible, so a hull standing at a port with a full
warehouse and a buyer two jumps away flew away empty. **Acid was made at
678 t/d and carried at 16.** *Fix: `loadHere` scans the hull's own doorstep
first — one origin costs a hundredth of scanning the map. Haulage went to
266 t/d, and then to 496 with prices fixed.*

**9. The fleet was sized for the test rig, not the map.**
Sixteen hulls a colour is right for the eleven-world balance rig and absurd for
109 ports and ~4 000 live routes: forty-eight ships deliver about one and a
half cargoes per port per year. *Fix: opening census proportional to worlds
held; growth driven by berth pressure.*

**10. Nobody in the galaxy built ships.**
Five chains tie exactly on a ferrite seam, the yard is third in catalogue
order, and on the real map the governor never bought enough Works to reach it.
**Not one ton of hull plate was pressed anywhere in two simulated years** — so
no hull lost in battle could ever be replaced and no merchant fleet could ever
grow, however hard the board was paying. *Fix: capitals mandate a yard as they
already mandate an arsenal, and commissioning is gated on plate and a pilot's
stake rather than on an exchequer the auto-governor empties weekly. Still at
zero — see §10.*

**11. A laid-up hull could be sunk, and minted its own tonnage.**
`LaidUp` puts a hull's plate back on a yard's shelf. `wreck()` checked only for
`Lost`, so destroying a laid-up ship dropped the same tons a second time as
scrap. Five test casualties, three of them laid up, **minted 1 915 tons**.
*Fix: `Status.Gone()` guards both sites.*

And one measurement fault worth recording separately, because it made the
whole feature invisible for an afternoon: **`habitablePop` was read off the
wrong map.** Set at 1.5 M on the reasoning that a city that size proves a clean
seam, it looked right on the eleven-world rig. On the real gazetteer the city
generator grows no world smaller than 1.36 M and the median is 3.97 M, so
**109 worlds out of 109 were exempt and the entire fuel industry quietly failed
to exist.** A balance number has to be read off the map the game actually
seeds.

---

## 10. Where it stands

**Working, measured, and conserved.** The lithium line runs end to end. Hostile
worlds are sited, capitalised, worked unmanned and traded with by everybody.
Both fuel forms exist on the map. Harvesters lift crust off rocks nobody lives
on; surveys lift the seams for 90 days. The merchant fleet sizes itself to the
map. Mass and credits balance on every seed over two years.

**Not working, and I know why.** Fuel output is 1–8 % of appetite and hull
plate is zero. Both trace to the same place, and it is not the lithium line:

- **3 shipyards exist in the whole galaxy** (the three capitals). All three run
  at **100 % on ferrite, acid and fluid — and 0 % on chips**, which the market
  is pricing at 3 840 cr/t, six times base, screaming.
- **Chips: 28 plants, 1 660 t/d of nameplate, 1 757 t/d of demand, 54.6 t/d
  actually made.** Three per cent.
- Chips need copper. Copper is a one-jump good. On a map with **one world per
  system**, "one jump" is a thin neighbourhood and about half the electronics
  capacity in the galaxy has no cuprite neighbour at all.
- The refineries are in the same position one tier down: they need acid and
  fluid flown in, and 168 hulls moving 2 128 t/d across 109 ports cannot serve
  fifteen scattered refineries wanting 525 t/d of reagent *and* everything else.

So the bottleneck is exactly where the brief wanted it — **mining and
transport** — but it is currently tight enough to strangle rather than to
shape. Berth pressure is running at **58–107× the commissioning threshold**
and the fleet cannot grow, because growth needs plate, and plate needs chips,
and chips need a neighbour.

---

## 11. Next iteration, in priority order

**1. Three bodies per system.** This is the unlock, and it is the one thing in
the original brief I deliberately did not build this pass. Give every system
its planet, its station and its nebula / asteroid field. It is not decoration:
it is what makes "local" a real neighbourhood again, so copper and silicon can
move, so chips get made, so yards press plate, so the fleet can grow, so the
refineries get their reagents. Fault 7 and the chips famine both dissolve into
it. Every body landable, every body upgradeable — a nebula as an ice-crystal
cavern habitat with a gravity generator, a station as a habitat with no crust
at all (and therefore a pure customer, which the market badly needs).

**2. Fixed colour spawn positions.** Deferred with the map work, and it belongs
with it: three home systems placed symmetrically, each with its planet, station
and field, so the opening position is a designed one rather than whatever the
1997 gazetteer happened to put where.

**3. Chips and copper specifically.** Even with three bodies, `Fab` wanting
equal parts silicon and copper while the electronics chain makes its own
silicon at 0.40 yield is an 80 %-internal bottleneck by construction. Either
rebalance the fab or let a system's asteroid field be a reliable cuprite
source.

**4. The commodity screen.** The data is all there and none of it is on a
screen. Selecting a commodity should show: agents currently flying it and
where, prices at every port within N jumps, cover in days at each, and the
best-paying run from here with its margin and ETA off the real momentum
integrator. `RoutesFrom` already computes exactly this for the AI.

**5. Icons and stand-in art.** Commodity icons for all eight board goods,
outfit icons for the reactor and confinement ladders, and a generic animation
set. The two fuels especially need to be visually distinct at a glance, since
the whole reactor decision hangs on telling them apart.

**6. Fuel as an actual consumable.** Right now `Pellets` and `Melt` are traded
and eaten by populations, but a hull's own jump does not burn them and the
reactor ladder's burnup is not yet wired to the voyage's range. Closing that
loop turns the fuel trade from a commodity into a constraint the player feels
every jump — and makes the breeder's shipboard transmutation matter.

**7. Performance.** `FindRoutes` is O(W² × M) — 309 k iterations per colour per
day. Two simulated years of the gazetteer takes ~20 s, and `stepUniverse`
catches up 400 days in one frame. An incremental index keyed on repriced worlds
would cut it by an order of magnitude before the map triples in size.

**8. Balance, once the map is right.** Re-measure `importFactor` (1.8),
`autoCrew` (3.6), `hotChance` (0.22) and the commission thresholds against a
327-body map. Every one of them was tuned against a map with a structural
famine in it, so every one of them is probably wrong.

---

## 12. Verification

```
go vet ./...                                    clean
go test ./internal/...                          all packages pass
GAZ=1 go test ./internal/universe -run TestGazetteer -v
GAZ=1 GAZSEED=7   … · GAZ=1 GAZSEED=99  …       mass + ledger balanced, 730 d
```

New tests, all passing:

| test | what it holds |
| --- | --- |
| `TestOnlyHotWorldsRefineFuel` | a clean world cannot stand up any licensed line; the dose ladder is a ladder; both fuel forms exist on the map |
| `TestTheSeamIsTheDose` | no spodumene without a dose, no dose without spodumene, no world above the habitable line ever condemned |
| `TestARefineryIsCapitalised` | a hot world opens with ≥ 14 days of its own intake in the treasury |
| `TestTheLithiumLineRunsAndBalances` | 40 days of the five-stage line: fuel made, seam falls, books balance, output < input |
| `TestCaskCargoStaysLocal` | hot material cannot ride a courier; concentrate and chemicals can; both fuels are on the board |
| `TestHostileWorldsAreWorkedUnmanned` | a dose-0.9 world is a camp, digs anyway, and never exceeds its ceiling |
| `TestAMandatedLineIsDugForFirst` | fault 1: the refinery gets ore even beside a far richer cuprite seam |
| `TestContestedInputsAreRationed` | fault 5: neither ferrite chain starves the other out |
| `TestFleetIsSizedByTheMapAndTheBoard` | opening census scales with worlds; commissioning draws exactly the hull's tonnage; lay-up returns it; books and ledger balance across both |
| `TestHarvesterLiftsFromTheGroundAndBalances` | crust leaves a reserve, royalty balances the ledger |
| `TestASurveyLiftsTheSeamAndExpires` | the world and its neighbours lift, the neighbour lifts less, the reading expires |
| `TestCoilBoostObeysTheSixthRoot` | doubling B does not double stand-off |
| `TestCuspSealIsWorthMoreInDragThanInStandoff` | the multipole ring's value is in leak, not radius |
| `TestSteeringArrayBuysAuthorityAndCostsPower` | driven current raises Q and the ledger, and buys L/D |
| `TestInjectionRingWorksWhereFieldDoesNot` | at 88 km the ring beats tripling the coil |
| `TestStockHullIsUnchanged` | the zero-value confinement changes no number anywhere |

Two existing tests were amended rather than relaxed, both with the reason
recorded in the test:

- `TestLossesShowUpInTheBooksAndTheCensus` — the census may now **grow**; what
  it must never do is shrink, because "how many hulls has Red lost this war" is
  the question the whole economy is about.
- `TestPriorityWorldIsUpgradedFirst` — now stocks the steel a battery needs.
  Once capitals were mandated to run a yard *alongside* their arsenal there was
  no loose steel anywhere in Red space, so the governor bought nothing and the
  test failed for a reason unrelated to what it tests. **Whether a colour can
  afford a planetary battery is now a real open balance question** — see §11.8.

---

*Mass is conserved. Credits are conserved. The fuel is radioactive, the worlds
that make it are uninhabitable, and the ships that carry it are made of metal,
acid and hydraulic fluid. What is missing is somewhere for the copper to go.*
