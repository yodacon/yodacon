# Plan: The Trade Economy

**Matter is conserved. Industry is composed. The three colours are provably
even.**

The [war economy](war-economy-plan.md) made territory a supply problem: a
fighter that must land to rearm has a home, and a home that must be supplied
has a supply line worth cutting. It left M5 open — *warehouse stock,
production and consumption, interstellar load and transit* — with a single
sentence of design behind it.

This is that layer, and it turned out to want a spine the war economy did not
need: **a conservation law**.

> Credits can be taxed into existence. Tons cannot. Every ton of ferrite in
> the game was put in the ground at genesis, and from then on it can only
> *move* — out of the crust, into a warehouse, across a lane in somebody's
> hold, through a factory that turns it into something worth more and weighing
> less, and finally into a mouth or a slag heap. It is never minted. A world
> that grows rich did so by taking mass off somebody. A world that is mined
> out is mined out forever.

Everything below is downstream of that one rule, because it is the only rule
here that can be *proved* rather than argued about.

---

## 1. What was built

Five packages, all pure simulation — no Ebitengine, no drawing, every number a
function of the universe seed.

| Package | What it owns |
| --- | --- |
| `internal/econ` | Materials, stock pools, the seeded endowment, and the auditor |
| `internal/industry` | Modules, the `Then` composition operator, the primitive catalogue |
| `internal/govt` | The trifecta: three colours, six axes, and the balance proof |
| `internal/traffic` | The universal hull census, lane physics, and the trade journal |
| `internal/universe` | Worlds, shops, routes, and the daily tick that ties it together |

Plus `internal/app/economy.go`, the seam: it seeds the universe from the same
gazetteer the flight view uses, advances it on the voyage's own clock, and puts
it on the console.

---

## 2. Matter: three tiers and a sink

`econ.Material` is seventeen substances in four groups. The ordering is
load-bearing in exactly one place — **the first six are `market.Commodities`,
in order** — so a planet's 6-wide `Stock` and a ship's 6-wide `Hold` are a
*prefix* of a full material vector and convert by copying. Nothing in the
existing game had to change.

```
crust     Ferrite  Cuprite  Silicate  Volatiles  Biomass     finite, seeded
refined   Steel    Copper   Silicon   Polymer    Grain       made, not sold
board     Lumber Ore Rations Medicine Chips "Fuel cells"     what a port prices
sink      Slag                                               where value dies
```

Only the crust tier is finite, and it is the only tier mining can produce. That
is what makes the economy zero-sum *in the long run* rather than merely
balanced tick to tick.

### The auditor

`econ.Books` records genesis tonnage and, forever after, answers one question.
`Audit` rolls **every** pool in the universe into one column — crusts,
warehouses, holds, the sink — and compares the total.

Two decisions worth recording:

- **The check is on the grand total, not per material.** Transformation is the
  entire point of industry: a smelter is *supposed* to destroy ferrite and
  create steel. What no process may do is change how many tons there are.
- **Transformation is confined to one function in the whole game**
  (`universe.produce`). Everywhere else mass moves without changing identity,
  which `econ.Transfer` guarantees structurally — it takes first and adds
  exactly what the take returned. Every leak found while building this was a
  place that added the amount it *meant* to move rather than the amount it
  *got*.

A pool left out of the `Audit` call reads exactly like a leak. That is the
correct failure: forgetting to count a warehouse **is** losing track of the
mass in it.

---

## 3. Seeding: why worlds are different

`econ.Endow(seed, stellar, pop, mineRate)` draws a world's genesis holdings
from a splitmix64 mixer. splitmix rather than `math/rand` for one property:
**adjacent seeds must produce unrelated output**, so worlds 133 and 134 are not
neighbours in wealth just because they are neighbours in the gazetteer.

The distribution is deliberately uneven:

- **Heavy-tailed** (Pareto, `tailPower` 3.5): most worlds have a little of
  everything, a few have an enormous amount of one thing.
- **Pocked with holes** (`barrenChance` 0.34): a third of the time a world
  simply has none of a material. Holes are what *force* trade — a world that
  has everything never sends a ship anywhere.
- **Two independent draws per material**, so a world has a *speciality* rather
  than just a size.

The surface warehouse is the centuries of digging that happened before the game
started, and it is **moved out of the reserve, not added to it**, so
`Endowment.Total()` is the number the books are opened with.

---

## 4. Industry: modules that plug into modules

A module is a box with material ports in tons per industrial day. The one
operation that matters:

```go
func (m *Module) Then(next *Module) *Module
```

Plug `m`'s outputs into `next`'s inputs; get back a module whose ports are
whatever the pair could not satisfy internally. **Because the result is itself
a module, it plugs into a third the same way.** Composition is closed, so a
supermodule is not a special kind of thing with its own rules — it is a module
that remembers what it was built from. `Compose` is `Then` folded over a line.

Two properties, both tested:

1. **Mass balances.** Outputs never outweigh inputs; the difference is slag.
2. **The chain runs at its bottleneck.** A fabricator starved of copper does
   not run at full rate on silicon alone. The throttle and the material that
   caused it are recorded *at composition time* — that is the only moment the
   shortfall is visible, because once the downstream stage has been scaled to
   fit, its ports balance perfectly and the evidence is gone.

Sixteen primitives; every industry in the game is a **composition** of them.
Nobody wrote "chip industry" down anywhere — a world that can smelt and
fabricate has one.

### Unique industry, unauthored

`industry.Rank(reserve)` orders the chains a world *could* run by the tonnage
backing them, limited by the thinnest seam each depends on. `standUpIndustry`
builds the best two. That is the whole rule, and from one seed it produces:

```
ConEx (Red) pop 4.2M — Powercell; richest seam Volatiles 765kt
  Powercell: 92.4t Copper + 231.0t Volatiles ⇒ 135.1t Fuel cells (+181.3t slag)
Cenron (Blue) pop 4.1M — Electronics; richest seam Silicate 375kt
  Electronics: 108.2t Copper + 225.5t Silicate ⇒ 116.9t Chips  [bottleneck: Silicon at 96%]
Kestrel (Neutral) pop 1.2M — Timber; richest seam Biomass 75kt
  Foodstuffs: 66.0t Biomass ⇒ 44.5t Rations  [bottleneck: Grain at 75%]
```

Note what the electronics worlds *cannot* make: **copper**. The fabricator
needs it, no fab world mines it, and so a copper route exists because the
factory graph says so and not because anybody drew a trade lane on a map.

---

## 5. The trifecta

Three colours, six axes, one table — and it is **doubly balanced**:

|  | growth | extract | industry | shields | gunnery | logistics | **Σ** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Red** | 0.95 | 0.90 | 0.90 | 0.90 | **1.20** | **1.15** | 6.00 |
| **Green** | **1.20** | **1.15** | 0.90 | 0.95 | 0.85 | 0.95 | 6.00 |
| **Blue** | 0.85 | 0.95 | **1.20** | **1.15** | 0.95 | 0.90 | 6.00 |
| **Σ** | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | |

- **Every row sums to 6.00** — no colour was handed more total ability, so
  there is no strongest side.
- **Every column sums to 3.00** — no axis is globally inflated, so "shields"
  means the same amount of game across the table, and a buff to one colour is
  exactly a nerf to the others.

Both are asserted in `govt_test.go`. Change a value and two others must move to
pay for it, which is the entire point.

```
RED    the raider    best guns, best logistics, worst industry
                     wins early, cannot sustain a long war
GREEN  the grower    best growth, best extraction, worst guns
                     out-produces and out-mines; must not be rushed
BLUE   the fortress  best shields, best industry, worst growth
                     slow to start, terrible to grind down
```

A rock-paper-scissors in *tempo* rather than damage type: Red beats Green by
arriving before the growth compounds, Green beats Blue by out-massing a slow
starter, Blue beats Red by outlasting a side that runs out of factory.

**Every derived knob follows the table**, never an independent dial —
otherwise there is a second place to hide a buff and the proof above is
worthless. `MinFleet` falls out of Logistics as **Red 3, Green 4, Blue 5**;
growth, mine rate, factory yield, shield fraction, hold size and cruise speed
all likewise. Blue's industrial edge is visible on the factory floor above:
its electronics chain runs at 96% where Red's runs at 72%.

---

## 6. Traffic: the ships nobody is looking at

The census is **fixed**. A universe is created with N hulls and that is how
many there are; none is spawned to fill a scene or deleted when it leaves one.
A destroyed hull goes to `Lost` and is counted forever, because "how many hulls
has Red lost this war" is the question the whole economy is about.

Off-sector hulls are stepped with a one-dimensional momentum integrator:

```
F = thrust·cruise − drag·v²      a = F/m      v += a·dt      s += v·dt
```

where `m` is **hull plus cargo**. A full hauler genuinely accelerates worse
than an empty one and the return leg is genuinely faster. That is the reason
this is physics and not a countdown timer: *the economics of a route fall out
of the mass it carries.*

Statuses are `Idle · Loading · Hauling · Returning · Fighting · Resident ·
Lost`. `Resident` is the seam — a hull inside the sector the player is flying
is owned by `internal/world`, and the registry simply stops moving it.

Everything is written to the **journal**, which is the audit trail and the news
feed at once:

```
d357  Green 08 loads 34t Lumber at Kestrel for ConEx (+3570 cr)
d363  Red 04 delivers 34t at Kestrel for 3993 cr (margin 1518)
d201  Exeon Deep: the Silicate is worked out
```

---

## 7. Routes are found, not authored

`FindRoutes` looks at what ports are *actually paying today*. Prices come from
real scarcity — days of cover against real demand — so a route that paid last
week can be gone this week. The map of trade is a consequence of the simulation
rather than a fixture in it.

One restriction does the strategic work: **a hull will trade with its own
colour and with neutrals, never with an enemy.** So taking a world does not
just deny it to the other side, it *opens a market to you*.

---

## 8. What building this taught us

Four bugs, and the auditor caught three of them on day one of simulated time.

1. **Chains contained their own mines.** The composed plant netted the mine's
   output against the mill's intake internally, so it appeared to need nothing
   and produce lumber out of thin air — while the world's own mining moved the
   same tons a *second* time. Mass was created every tick. Fix: a chain
   **names** its mines (so `Needs` and `Rank` know what must be in the ground)
   but does not **contain** them. Digging is the world's job; the plant draws
   from the warehouse like any other input.

2. **The auditor was too strict before it was strict enough.** Checking each
   material independently flagged every smelter as a leak. Total mass is the
   invariant; per-material is evidence.

3. **`arrive` left `From` pointing at the old origin.** `dispatch`, seeing
   `From != Home`, sent the hull "home" on a leg it had already flown. Twenty-
   six of thirty-six hulls were permanently `RETURNING` down a phantom lane
   and nothing on the board was being carried.

4. **Chips, ore and steel had no consumer.** They piled up in warehouses
   nobody would ever need them from, no destination ever showed demand, and
   the whole trade network went quiet on day 104 with every hull idle. **A
   commodity with no sink stops being traded the moment the first warehouse
   fills.** Every finished good now has an appetite; the intermediates
   deliberately do not, because nobody eats copper — a fabricator does.

The lesson the war economy already recorded, confirmed again: **a simulation
this size has to be run to be tested.** None of the four would have failed an
assertion about a single module. All four were obvious within seconds of
printing a year of trade.

---

## 9. Where it stands

Over 800 simulated days, four seeds, an eleven-world universe:

```
mass                   BALANCED at every checkpoint
trade rate             ~100 voyages per 100 days, flat — no decay
colour parity          Red 6.4kt · Green 8.3kt · Blue 7.4kt delivered
replay                 identical from the same seed
reserves               monotonically falling, always
```

**Known tuning, not correctness:** warehouses grow slowly over a very long run
(65kt → 465kt across 800 days) — production modestly outpaces consumption.
Population growth closes the gap but is capped. The knobs are `chainRate`,
`appetite`, and `govt.baseMine`, all in one place each.

---

## 10. Not yet wired

The simulation is complete and observable; what remains is surfacing it.

| | Slice |
| --- | --- |
| **T1** | The dock's trade screen prices from `universe.World.Shop` rather than `market.Price`, so the board the player buys on is the board the AI trades on |
| **T2** | `Resident` handover — hulls entering the player's system become `world.Ship`s and hand back on exit |
| **T3** | Warehouse stock feeds `Planet.Stock`, closing the loop with the war economy's supply lines |
| **T4** | A trade-journal view in the spaceport: routes, arrivals, and what your rivals are moving |
| **T5** | Combat losses call `universe.Lose`, so the war shows up in the books |

Console commands available today: `economy`, `trifecta`, `journal [n]`,
`routes`, `world [id]`. `GONEX_CMD="economy;routes"` runs them headlessly.
