# The bottleneck detector, a revive plan that made things worse, and a resource loop read against the numbers

**22 September 2026** · `gonex/internal/{universe,industry}` · follows
[the chip famine](2026-09-22-the-chip-famine.md)

Three things happened in this pass, and only one of them is a success.

1. **The economy can now say what it is short of.** Strain counters record the
   work the galaxy tried to do and could not — intake a plant asked for and
   did not get, tonnage a pit had no budget to lift, cargo a port could not
   pay for — and a detector reads them back and attributes a *cause*. This is
   the first time the simulation has known its own bottleneck rather than
   waiting for somebody to read a year of logs.

2. **The core world revive plan, built the obvious way, made the economy
   worse.** Capitals that stand up the line the galaxy is short of cost
   62% of the galaxy's munitions and 26% of its rations and produced **not one
   extra ton of chips**. Rebuilt to answer in the currency of each fault, it
   stopped doing harm and still bought almost nothing — because the one
   lever it has for the dominant fault is an exchequer that cannot afford it
   by three orders of magnitude.

3. **A proposed resource loop was read against gonex's own numbers**, and
   applying its own value-per-unit rule to this catalogue finds two chains
   that *destroy* value and two more that barely clear the bar — including
   `Electronics`, the chain the last two reports were about.

Mass balances and the ledger balances throughout. 162 tests pass across 15
packages.

---

## 1. Strain: measuring refused work

Every balance pass on this economy so far has been archaeology. Print a year
of trade, stare at it, work backwards. That method found thirteen faults and
it is not wrong — but it only works while a person is doing it.

The instrument is three counters, accumulated over a rolling 30-day window:

| counter | recorded where | means |
| --- | --- | --- |
| `Unmet[m]` | `runPlant` | intake a stage demanded and could not draw |
| `Undug[m]` | `mine` | dig want the day's budget could not cover |
| `Refused[m]` / `Offered[m]` | the sale | cargo that reached a pad and the part of it the port could not pay for |

The design decision that matters: **these count refused work, not quantities.**
A warehouse already says how much of something there is. A material is only a
bottleneck if somebody *asked* for it and was turned down, which is why the
ranking key is blocked intake rather than scarcity. A material nobody wants
can be absent without being a problem; a material everybody wants is a
problem long before it runs out.

Attribution is five causes, and each one is a fault this project has actually
shipped:

```
  NoPlant  nothing in the galaxy makes it              the polymer fault
  NoTurn   the seam is there, the dig went elsewhere   the silicate fault
  NoMoney  it reached the pad and nobody could pay     the orbital fault
  NoLane   there is a heap of it three jumps away      the copper fault
  NoFeed   its own upstream is short                   not a fault; the chain working
```

The order of the tests is the order of blame: a thing nobody makes cannot be
a lane problem, and a thing that never left the pithead cannot be a money
problem.

### What it says, unprompted

Full gazetteer, seed 20260922, after 730 days:

| material | blocked | made | capacity / in the ground | idle | cause |
| --- | ---: | ---: | ---: | ---: | --- |
| Ferrite | 11,019 t/d | 2,964 | 30,017 kt in the ground | 302,729 t | no turn at the pithead |
| Spodumene | 7,967 | 555 | 13,912 kt | 0 t | upstream short |
| Volatiles | 7,111 | 2,691 | 28,793 kt | 363,377 t | no turn at the pithead |
| **Compost** | **5,452** | **0.0** | **0.0 nameplate** | **1,331,253 t** | **no plant** |
| Silicate | 5,434 | 784 | 30,903 kt | 322,074 t | no money at the pad |
| Biomass | 4,469 | 4,771 | 27,207 kt | 180,921 t | no money at the pad |
| Copper | 3,897 | 643 | 1,704 t/d nameplate | 248,401 t | no money at the pad |
| **Scrap** | **2,966** | **0.0** | **0.0 nameplate** | **0 t** | **no plant** |
| Cuprite | 2,510 | 1,695 | 30,616 kt | 336,368 t | no turn at the pithead |
| Acid | 2,224 | 543 | 1,070 t/d nameplate | 320,093 t | no money at the pad |

Two rows in that table are not about chips at all, and neither was on
anybody's list: **1.33 megatonnes of compost is lying in warehouses while
composters that want 5,452 t/d of it cannot draw a ton, and the galaxy makes
no scrap whatsoever against 2,966 t/d of breaker capacity.** The two return
paths — the only two places in this economy where the flow goes back uphill —
are both broken, and they have been broken silently since they were written.

That is the detector earning its keep on its first run.

Writing it also cost two bugs of its own, both instructive:

- It scanned `w.Plant` and not `w.Civic`, so composters and breakers did not
  exist and every return material read as "nobody makes it".
- It reported a *nameplate* for crust, which is always zero — a pit has no
  capacity, it has a budget — so every material in the ground read as though
  nothing produced it. Crust now reports its reserve instead.

---

## 2. The core world revive plan

The three capitals are the only worlds in the game that can be told what to
make. Everywhere else industry falls out of the rock: `Rank` orders what a
world's seams can back and the best two stand up, which is what makes a
world's speciality an accident of geology. A capital is the exception, and a
revive plan is what the exception is for.

A mandated chain does not need the crust. `standUpIndustry` stands up its
processing stages alone and buys every input — which is exactly "convert and
process": a capital with no cuprite can still refine copper, it just has to
buy ore, and its people are the workforce that makes that pay.

### Version one: stand up the line that is short. It made things worse.

| | committed baseline | revive v1 |
| --- | ---: | ---: |
| Chips | 157.6 | 157.6 |
| Rounds | 77.4 | **29.2** |
| Rations | 1,820.6 | **1,354.4** |
| Ore | 1,567.1 | 1,342.7 |
| Pellets | 48.6 | 53.2 |
| Steel | 524.2 | 827.2 |

Not one extra ton of chips, a 62% cut in munitions and a 26% cut in the food
supply. Two mechanisms, both obvious in hindsight:

1. **A mandated line runs at `full` rate, uncapped by the pithead.** So a
   retooling capital adds nameplate it cannot feed. It does not add output —
   it adds `Unmet`, which is to say it makes the detector's own numbers
   worse.
2. **Mandates take the dig budget and the factory floor first**, so the
   capital's founding lines — the arsenal, the gardens — are crowded out by
   the new one.

The deeper error is that the previous report had already measured this and
written it down: *more plant does not make more chips.* Building a revive plan
that answers every shortage with more plant was repeating an experiment whose
result was on file. It is recorded here because a plan that fires and changes
nothing is the failure mode worth being able to see.

### Version two: answer in the currency of the fault

| cause | the capital's answer |
| --- | --- |
| `NoPlant` | stand up the line — the only case where capacity *is* the fault |
| `NoFeed` | stand up the line one level **upstream**: the thing the idle plant is waiting for |
| `NoMoney` | capitalise the ports that are refusing the cargo, from the exchequer |
| `NoLane` | file a standing order from the idle heap to the starved plant |
| `NoTurn` | nothing. A capital cannot reach another world's pithead, and the dig ration already fixed it galaxy-wide |

The harm stops. The headline numbers return to the committed baseline within
noise (chips 156.8, rounds 68.3, rations 1,803.4, melt 49.7, pellets 37.9,
hull 0.5), which is the correct outcome for a plan that now declines to act
on faults it cannot fix.

And then the interesting part. Over 730 days the plan fired **104 times
against `NoMoney` and 8 times against `NoLane`**, and moved the economy by
essentially nothing. The reason is arithmetic:

```
  a single station's six-day copper bill   117.8 t/d x 2,040 cr x 6  =  1,442,000 cr
  the whole Green exchequer, day 730                                =    240,119 cr
```

**One port's working capital for six days is six times the entire treasury of
the government subsidising it.** The exchequer is not a small lever for this
fault; it is the wrong order of magnitude.

---

## 3. The price feedback that makes the money fault self-sealing

This is the mechanism the last report ended on, now named precisely.

`Reprice` is scarcity pricing and it is correct: a world short of a material
pays up to 3× base for it, and a world running a line it was *sited* for pays
up to **6×**, because a refinery short of acid is not inconvenienced, it is
shut. That steepness was added deliberately, and it worked — it let
refineries outbid ordinary trade for reagents.

But a bid and a price are not the same thing, and here they are the same
number. The multiplier does two jobs at once:

- it **attracts** the courier, which is what it was for; and
- it **empties the buyer's treasury faster**, which is not.

A fab station mandated to `Electronics`, desperate for copper, posts
`340 × 6 = 2,040 cr/t` — and with 228 credits in the drawer it can afford
0.1 tons. The more desperate it is, the higher the price it must pay with
money it does not have. The feedback loop closes on itself:

```
  short of copper ──▶ prices copper at the ceiling ──▶ affords less copper
        ▲                                                      │
        └──────────────────────────────────────────────────────┘
```

This is why 64× the money supply only moved refusals from 43% to 25%, and why
a subsidy sized in days of cover cannot catch up: the thing being subsidised
inflates as you subsidise it.

**Any fix for "stable prices" has to break the identity between the bid and
the price paid.** The candidates, unchanged from the last report but now with
a mechanism to aim at: trade credit (the port buys against next week's
output); seller-side discounting (a hull three jumps out with copper nobody
can pay for takes what is offered); or separating the desperation multiplier
into a *routing weight* that attracts hulls without raising the invoice.

---

## 4. The proposed resource loop, read against these numbers

A nine-part elaboration of the resource loop was put forward: extraction with
per-system mineral profiles, refining gated on energy, fabrication measured
by value-per-unit, quality tiers, component modding with exponential value
growth, merchant AI with mood and a reservation margin, station layout and
adjacency, a reactor endgame that makes refining free, and the closed loop of
sources, sinks, transformers and feedback.

Read honestly, most of it describes gonex as it already stands, one part of
it is the most valuable unbuilt thing on the list, and one part of it would
break the model this economy is built on.

### What gonex already has

| the elaboration | gonex |
| --- | --- |
| per-system mineral composition | `econ.Endow(seed, stellar, …)` — six crust materials, finite reserve, drawn from the seed |
| refining as the first value-adding step | `Smelter`, `Refinery`, `Furnace`, `Cracker`, `Thresher`, each with a mass yield |
| fabrication: ingots → goods | `Fab`, `CellPlant`, `Cannery`, `Pharma`, `Yard`, `Arsenal`, `MissileWorks` |
| dual-yield deposits (silver → silver + lead) | `ChemWorks`: one volatiles column, three streams — and it was a *fix*, for a ranking collision that silenced every arsenal in the galaxy |
| alloy shortcut that skips a stage | `Chain` composition is closed under `Then`, so a shallow line and a deep one are the same kind of object |
| cargo capacity as the hard constraint | hull `Dry`/`Wet`, and `Route.Value() = Margin × Tons` |
| keep storage adjacent to processing | `rankOf` weights a port in the same system 2× |
| production queues / conditional triggers | `StandingOrder`, filed by the governor and now by the revive plan |
| prices shift on supply and demand | `Reprice`, derived from warehouse cover — never authored |
| sources · sinks · transformers · feedback | exactly the shape of `econ.Books`: genesis, crust, warehouse, afloat, sink, audited to zero every tick |

The convergence is worth stating plainly: the elaboration and this codebase
arrived at the same structure independently, and where they differ it is
usually because gonex measured something.

### The one thing that is missing, and it is the big one

**Energy is not in this economy at all.** The elaboration makes it the
refining bottleneck — `2 raw ore + 1 fuel cell → 4 refined ingots`, with a
reactor unlock that turns refining from fuel-constrained into
throughput-constrained. gonex has three fuels (`FuelCells`, `Pellets`,
`Melt`), prices all three, ships all three, and **feeds them exclusively to
populations**. Not one industrial process in the catalogue consumes energy.

That is why the fuel trade reads the way it does: pellets at 7–9% of appetite
and melt at 11–14%, with the entire demand side being municipal heating. A
fuel with no industrial sink is a commodity with nowhere to go, which is
precisely the fault the transmutation report diagnosed for copper a report
ago and named *lesson four running backwards*.

Adding an energy port to every refining and fabricating primitive is a small
change — one `Port` per `recipe` — and it would do three things at once:
give fuel an industrial demand curve, make the reactor/solar unlock a real
economic progression rather than a shop label, and put a second conserved
quantity next to mass for the auditor to hold.

**With one warning, and it is measured.** Every chain in this galaxy already
runs between zero and 67% of nameplate. Adding a *new required input* to a
stage that is already short will reduce output, not increase it — exactly as
the revive plan's version one did. The energy economy has to land with its
own supply, which means the zero-energy unlock is not an endgame reward, it is
part of the same change.

### Value per unit: the elaboration's own rule, applied here

The elaboration's golden rule is that anything returning more than 5 cr per
ingot is a value-adding fabrication. gonex prices in credits per *ton*, so the
same question is: what does a chain add per ton of everything it takes in?

| chain | in t/d | out t/d | cr added per ton of intake |
| --- | ---: | ---: | ---: |
| Ordnance | 150.0 | 97.0 | 646.8 |
| Shipyard | 145.0 | 97.0 | 414.1 |
| Munitions | 140.0 | 92.0 | 355.9 |
| Breeding | 110.6 | 21.9 | 197.3 |
| Bulk ore | 100.0 | 92.0 | 142.4 |
| Fuel melt | 128.5 | 35.9 | 140.3 |
| Pharmaceutical | 140.0 | 70.0 | 113.2 |
| Timber | 100.0 | 85.0 | 79.0 |
| Chemical works | 100.0 | 76.0 | 76.2 |
| Structural steel | 100.0 | 62.0 | 70.2 |
| Conductor | 100.0 | 48.0 | 68.2 |
| Fuel pellets | 116.8 | 24.2 | 44.1 |
| Foodstuffs | 100.0 | 67.5 | 20.8 |
| **Electronics** | 140.0 | 36.0 | **10.3** |
| **Powercell** | 140.0 | 75.0 | **5.7** |
| **Radiant smelting** | 100.0 | 24.8 | **−2.3** |
| **Lithium milling** | 100.0 | 45.0 | **−52.8** |

Four rows at the bottom of that table are a finding.

**`Lithium milling` and `Radiant smelting` destroy value at base prices.** A
mill takes 100 t of spodumene and acid worth 13,600 cr and hands back 45 t of
concentrate worth 8,325. That is the design working as intended in mass terms
— four fifths of the rock is tailings, and it is deliberately the cheapest
stage to stand up so that what crosses a lane is concentrate rather than ore
— but it means the first two stages of the fuel line are only worth running
because of what the *fifth* stage sells for. Any world that mills and cannot
sell onward is running at a loss, and those are exactly the worlds measured
at 5.7% and 18.8% of nameplate.

**`Electronics` adds 10.3 cr per ton, third-worst in the catalogue.** The
chain two reports have now been written about is, at base prices, barely
worth running. Silicate at 80 cr/t and copper at 340 go in; chips at 640 come
out, but only 36 tons of them per 140 tons in. The scarcity multiplier is
what makes it pay in practice, which is another way of saying the electronics
industry is only profitable when chips are short — and it stops being
profitable exactly when it succeeds.

That is a price-table fault, not a recipe fault, and it is now on the list.

### What would break the model

**Quality tiers and component modding.** A 1×/1.5×/2×/3×/4–5× condition
ladder, and crystals whose marginal value grows exponentially with each one
added, are *authored value*. Everything priced in gonex is derived: a base
value per ton, multiplied by a scarcity factor computed from warehouse cover.
No item anywhere has a price of its own.

Three specific problems:

1. **It mints value with no mass behind it.** The credit ledger would still
   balance — credits only ever transfer — but the relationship between the
   mass books and the money books, which is the thing that makes a gonex
   price *mean* something, would come apart. A ton would no longer be a ton.
2. **Exponential value growth is the opposite of stable prices**, which was
   the stated goal of the same request. A mechanic whose whole appeal is that
   marginal value increases without bound cannot coexist with a price system
   whose job is to converge.
3. **gonex already has the good half of this idea.** `govt.Yield` is a quality
   multiplier that bites on *mass* — a Blue works keeps more of what it puts
   in and the difference falls out as slag. Quality that changes yield is
   conserved; quality that changes price is not.

Recommendation: take quality as a yield multiplier (already present, could be
extended per-world rather than per-government) and leave encrustation alone.
If a value-explosion mechanic is wanted later, it belongs to the player's own
outfitting, not to the commodity economy.

**Merchant mood and a reservation margin**, on the other hand, are worth
having and are not in conflict with anything. gonex's couriers take any
positive margin, ranked by margin per megametre. A minimum acceptable margin
that starts high and relaxes as a counterparty's disposition improves is a
real behavioural lever — and it is the same shape as tracking per-hull
profitability, which is the prerequisite for any learning rule over routes.

---

## 5. Where this leaves the list

Built and measured this pass:

- The strain counters and the bottleneck detector, with a permanent section
  in the balance rig. `Bottlenecks()` is the instrument every future balance
  pass should start from instead of re-deriving it by eye.
- The core world revive plan, cause-directed, with `NoPlant`, `NoFeed`,
  `NoMoney` and `NoLane` answers.
- `industry.Makes` and `industry.Inputs`, so a chain can be walked backwards.

Found, not yet built — and the detector found the first two without being
asked:

1. **The compost loop is broken.** 1.33 Mt idle, 5,452 t/d of composter intake
   unmet. This is the population-consumption half of the loop: people eat,
   compost accumulates, and it is not getting back to the soil.
2. **The scrap loop never starts.** 2,966 t/d of breaker capacity, zero tons
   of scrap made. A hull lost in battle is supposed to become next week's
   plate. Nothing is producing scrap at all — population consumption of
   durables produces slag, which is a grave, rather than junk, which is a
   resource.
3. **Energy**, per §4 — the largest genuinely missing piece, to land together
   with its own supply.
4. **The price table**, per the value-per-ton finding: two chains at negative
   value-add and `Electronics` at 10.3.
5. **Per-hull profitability**, without which no reward signal for a learning
   router can exist. Hulls already carry `Purse`, `Tons`, `Bought` and
   `Voyages`; what is missing is realised margin per voyage, kept.

The order matters and it is not the order above. **(1) and (2) are cheap,
they close loops that are already written, and they make mass circulate
rather than accumulate** — which is the same fault as the copper heaps, one
tier down. They come first.

---

## 6. Verification

```sh
GOTOOLCHAIN=auto go vet ./... && GOTOOLCHAIN=auto go test ./internal/...
GOTOOLCHAIN=auto GAZ=1 go test ./internal/universe -run TestGazetteer -v
```

The rig now prints `WHAT THE ECONOMY COULD NOT DO` and `WHAT THE CAPITALS DID
ABOUT IT` alongside the balance tables.

One existing test changed, and it deserves calling out rather than burying.
`TestTheShipCensusIsFixed` asserted that the hull census never changes, and it
passed for the life of the project — not because hulls are never added, but
because no yard had ever pressed a ton of hull plate, so `commission()` could
never reach its last line. The revive plan made the eleven-world rig solvent
enough to press some, a hull was commissioned, and the assertion failed on the
day the economy started working. It is now
`TestTheShipCensusOnlyGrowsAgainstPlate`, which holds what `merchantfleet.go`
actually promises: never shrinks, never exceeds the cap, and never grows
without plate.

---

*The economy can now tell you what it is short of, which is new. What it says
is that it is short of money it cannot spend, rock it cannot get a turn at,
and two return paths nobody noticed were broken — and that the answer to
almost none of it is more factory.*
