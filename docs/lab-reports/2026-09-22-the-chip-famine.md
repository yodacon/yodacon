# The chip famine: a turn at the pithead, and a purse at the pad

**22 September 2026** · `gonex/internal/universe` · follows
[the game mechanics overview](2026-09-22-game-mechanics-overview.md)

The overview closed on a causal chain that ended in a frozen fleet, and named
its first link: *one world per system*. The triad fixed that link. Three
bodies per system now stand where one stood, there are **24 shipyards where
there were 3**, and the galaxy is founded with 2,045 t/day of chip plant
against 1,625 t/day of appetite — **1.26× cover, in nameplate**.

It made 65 t/day. Three per cent.

This report is the hunt for the missing 97%. The suspect on file was the Fab
recipe. It was not the Fab recipe. It was two faults that have nothing to do
with electronics, both of them versions of a rule this economy had already
written down and applied everywhere except the one place it was needed:

1. **The dig budget is served largest-first**, so a world wanting equal
   tonnages of ferrite and silicate digs ferrite in full and silicate at a
   ninth, for ever, because ferrite sorts first.
2. **The working-capital stake is gated on `Hostile()`**, so the 109 orbitals
   the triad minted — every one a finishing line whose entire input list
   arrives by ship — were founded with nothing to buy it with.

Chips went from **65.4 to 157.6 t/day** (seed 20260922) and **31.0 to 86.5**
(seed 7). The first hull plate in the project's history was pressed, and a
merchant hull was commissioned off it. Mass balances and the ledger balances
throughout.

Section 5 is the other useful half: **four expensive things that were
measured and are not the problem.**

---

## 1. The suspect, and its alibi

The recorded suspicion was that the Fab is ~80% internally bottlenecked by
construction. It is, and it does not matter.

`Electronics` is `MineSilicate → Furnace → Fab`. The furnace turns 1 t of
silicate into 0.40 t of silicon; the fab wants 0.5 t of silicon per 0.5 t of
copper. Composed, the fab can only ever run at `0.40 / 0.5` of the furnace it
stands on, and `Then` records the choke honestly:

| world | internal choke | ratio |
| --- | --- | ---: |
| New Providence (Blue) | Silicon | 0.96 |
| Perseus II (neutral) | Silicon | 0.80 |
| Endor (Green) | Silicon | 0.72 |

The spread is government yield — a Blue works keeps more of what it puts in —
and the neutral case is the 80% on file. So the recipe costs the chain
between 4% and 28% of its nameplate.

The chain runs at **6.0%** (§4). A 20% haircut is not the story when
nineteen twentieths of the plant is idle, and chasing the recipe would have
bought a rounding error. *The prime suspect is cleared.*

---

## 2. Fault 12: the same greedy allocation, one stage upstream

This is [fault 5 of the lithium
pass](2026-09-22-lithium-fuel-cycle.md) — "two plants on one warehouse, served
in list order" — moved from the factory floor to the pithead, where it
survived being fixed downstream.

`produce()` rations a contested warehouse in proportion to demand, and its
comment explains at length why serving the biggest want first is wrong.
`mine()` then allocated the dig budget by *sorting the wants and serving them
in order until the budget ran out*. The lithium pass had already caught this
once and patched it for two cases — the gardens eat first, a mandated line
digs first — but left the ranked chains racing.

New Providence, measured at founding:

```
  dig budget      272.6 t/d
  wants Ferrite   245.4 t/d   (Bulk ore)
  wants Silicate  245.4 t/d   (Electronics)
```

An exact tie, broken on material order, and `Ferrite` is material 97 against
`Silicate`'s 99. Ferrite took 245.4 t and silicate got the 27.2 t left over —
**11% of what the fab needed, every day, for ever.** Galaxy-wide:

| crust | wanted by industry | mined | cover |
| --- | ---: | ---: | ---: |
| Ferrite | 13,031.6 t/d | 3,058.8 t/d | 23% |
| Cuprite | 3,521.7 t/d | 1,761.0 t/d | 50% |
| **Silicate** | **5,600.3 t/d** | **516.2 t/d** | **9%** |

Silicate is not scarce — it is in the crust of 181 bodies, 31,475 kt of it,
and 28 of the 48 chip plants stand on a seam of their own. It was short of
its **turn**.

**The fix** is the one `produce()` already uses. Two passes: every seam gets
its proportional share of the budget, then a second pass spends what the thin
seams and the satisfied wants left behind, so a rationed budget is never an
idle one.

Silicate mining rose to 724.8 t/d (+40%), cuprite fell to 1,577.4 (−10%), and
**chips doubled to 133.0 t/day.** Hull plate was pressed for the first time.

---

## 3. Fault 13: a hundred and nine factories, founded broke

With the dig fixed, 84% of chip-plant-days were now short of copper — while
**229,082 t of copper sat in warehouses** doing nothing. Copper that has been
made, is surplus at its port, and is wanted three jumps away is supposed to be
the easiest route on the board.

The hunt for why ended in `routes.go`, in the sale itself:

```go
// The port buys what its treasury can pay for. The rest stays
// aboard; a broke world is a real event and the hold says so.
if price > 0 {
    tons = math.Min(tons, float64((dst.Credits-paid)/price))
}
```

Instrumenting that line for two simulated years:

| material | offered | afforded | share | sales clipped |
| --- | ---: | ---: | ---: | ---: |
| Copper | 2,141,318 t | 1,023,856 t | **48%** | 7,694 / 14,376 |
| Cuprite | 1,678,133 t | 877,626 t | 52% | 3,538 / 7,252 |
| Acid | 592,548 t | 303,218 t | 51% | 1,523 / 3,024 |
| Polymer | 208,692 t | 106,775 t | 51% | 793 / 1,522 |
| Rations | 25,089 t | 21,711 t | 87% | 72 / 357 |

**Half the galaxy's freight was being turned away at the pad for want of
credits**, and the ports turning it away were all of one kind:

```
  Earth Station          168,125 t of copper refused · treasury      300 cr
  Tau Ceti IV Station    106,409 t                   · treasury    1,486 cr
  Alkaid Station          81,201 t                   · treasury      214 cr
  Stardock Alpha Station  70,216 t                   · treasury      436 cr
```

Three hundred credits against a copper price of 1,139 a ton. Earth Station
could afford **not one ton.**

`stake()` exists for exactly this and was written during the lithium pass,
where its own comment describes the trap word for word: *"No chemicals, so no
fuel; no fuel, so no revenue; no revenue, so no chemicals. A port buys only
what its treasury covers, so a broke world does not send a distress signal —
it quietly declines the cargo and the courier flies on."* It sizes a world's
genesis purse to the daily bill for everything its plants must **buy** rather
than dig, at 2.2× markup for 45 days.

Its first line was `if !w.Hostile() { return }`.

That gate was correct when it was written, because hot worlds were then the
only factories in the galaxy with nothing of their own to sell. Then the triad
minted 109 orbitals, `stationLines` made every one of them a finishing chain —
`Electronics`, `Powercell`, `Pharmaceutical`, `Shipyard`, `Ordnance`, all
inputs by ship — and founded each on `pop × stationShare / 4` credits. A
hundred and nine factories that must buy everything, capitalised as though
they were villages.

**The fix is to delete the gate.** The rule needs no other change: it already
counts only non-crust inputs, so a world that digs what it processes computes a
stake of nearly nothing and keeps its ordinary purse. It capitalises exactly
the ports that cannot capitalise themselves.

Chips 133.0 → **157.6 t/day**. Copper refusals halved. And the rest of the
economy moved with it, because the orbitals were never only chip plants:

| | before the pass | after fault 12 | after fault 13 |
| --- | ---: | ---: | ---: |
| Chips | 65.4 | 133.0 | **157.6** |
| Pellets | 28.6 | 37.8 | **48.6** |
| Melt | 28.4 | 26.9 | **46.5** |
| Rounds | 68.0 | 49.5 | **77.4** |
| Hull plate | **0.0** | 0.16 | **0.6** |
| Merchant hulls | 560 | 560 | **561** |

---

## 4. The floor, and why fractions multiply

The whole factory floor, mean achieved rate over 730 days, worst first.
`Slag` in the last column means nothing specific was missing — the stage was
already throttled by its share of a contested warehouse:

| chain | mean rate | waiting for |
| --- | ---: | --- |
| Shipyard | 0.000 | Chips · Fuel cells · Acid |
| Ordnance | 0.002 | Chips · Polymer |
| Pharmaceutical | 0.021 | Polymer · Biomass |
| Fuel melt | 0.036 | Acid · Fluid |
| Fuel pellets | 0.036 | Acid · Steel |
| Powercell | 0.045 | (share) · Copper |
| Electronics | 0.060 | (share) · Copper · Silicate |
| Munitions | 0.069 | Polymer |
| Structural steel | 0.221 | (share) · Ferrite |
| Bulk ore | 0.321 | (share) |
| Conductor | 0.376 | (share) |
| Chemical works | 0.555 | (share) |
| Timber | 0.624 | (share) |
| Foodstuffs | 0.656 | (share) · Biomass |

Read it by depth rather than by name. One crust, one step — Timber, 0.62. Two
steps — Conductor, 0.38. Three steps and a bought input whose own supplier is
running at 0.38 — Electronics, 0.06. Three steps and **four** bought inputs —
Shipyard, zero.

Nobody is starving. Everybody is at a third, and thirds multiply. That is the
shape of this economy's remaining balance problem, and it is why the answer
was never going to be found inside the Fab.

---

## 5. Four things that are not the problem, measured

Each of these is the obvious next move, each costs real work, and each was
tested before it was believed. Recording them so nobody pays for them twice.

**More hulls do nothing.** Six times the merchant marine moves four times the
cuprite and makes no more chips. Stranded copper goes *up*.

| fleet | chips | copper | cuprite hauled | copper stranded |
| ---: | ---: | ---: | ---: | ---: |
| 560 | 133.0 | 573.4 | 1,202 t/d | 229 kt |
| 1,200 | 138.5 | 642.6 | 3,807 t/d | 270 kt |
| 3,600 | 136.0 | 634.2 | 5,019 t/d | 273 kt |

**A bigger pithead saturates, and costs the fuel trade.** Tripling `baseMine`
buys +84% chips and takes pellets down 58% and rounds down 81%, because the
extra dig goes to whoever is already biggest:

| `baseMine` | chips | copper | pellets | rounds | hull |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 133.0 | 573.4 | 37.8 | 49.5 | 0.16 |
| 63 | 194.1 | 943.0 | 28.9 | 30.8 | 0.00 |
| 84 | 212.1 | 1,164.2 | 16.3 | 10.7 | 0.00 |
| 126 | 244.9 | 1,435.4 | 15.7 | 9.6 | 0.00 |

**Sizing the factory to the dig does not help either.** Lowering
`importFactor` from 1.8, and capping mandated lines along with ranked ones,
shrinks nameplate and makes fewer chips, not more:

| `importFactor` | mandates capped | chips | of nameplate | rounds |
| ---: | --- | ---: | ---: | ---: |
| 1.8 | no | 133.0 | 2,045 | 49.5 |
| 1.4 | no | 126.4 | 1,759 | 56.0 |
| 1.0 | no | 119.8 | 1,387 | 45.8 |
| 1.0 | yes | 119.5 | 1,211 | 13.2 |
| 0.7 | yes | 98.9 | 848 | 7.2 |

**And it is not the amount of money.** Sixty-four times the genesis purse
buys +62% chips and takes the refusal rate from 43% to 25%. The refusals are
not a level problem:

| purse/head | chips | hull | refused sales | money supply |
| ---: | ---: | ---: | ---: | ---: |
| 0.25 | 157.6 | 0.56 | 43% | 289 M |
| 1.00 | 182.0 | 0.89 | 40% | 575 M |
| 4.00 | 207.1 | 1.95 | 34% | 2,206 M |
| 16.00 | 255.4 | 2.87 | 25% | 8,733 M |

---

## 6. The numbers

Full gazetteer, 327 ports, 730 days, t/day made.

| | seed 20260922 | | seed 7 | |
| --- | ---: | ---: | ---: | ---: |
| | before | after | before | after |
| Chips | 65.4 | **157.6** | 31.0 | **86.5** |
| Pellets | 28.6 | **48.6** | 29.7 | **44.6** |
| Melt | 28.4 | **46.5** | 32.6 | **34.9** |
| Rounds | 68.0 | **77.4** | 1.2 | **2.9** |
| Hull plate | 0.0 | **0.6** | 0.0 | **0.1** |
| Steel | 525.2 | 524.2 | 1,063.6 | 1,030.6 |
| Ore | 1,641.1 | 1,567.1 | — | 2,019.2 |
| Rations | 1,798.0 | 1,820.6 | — | 1,317.4 |

Chips **2.4×** on one seed and **2.8×** on the other; fuel up on both; steel
and rations flat, which is what a redistribution of the same dig budget should
look like. Mass balances and the ledger balances on both seeds, before and
after. 148 tests pass, `go vet` clean.

---

## 7. What is still broken, and what it is

Chips at 157.6 t/day are **10% of the galaxy's appetite**, and the yard tier
is still at zero to three decimal places. The next fault is already located
and is not a tuning knob:

**A starved port posts the highest price and can therefore afford the least.**
Price is scarcity — correctly — so the world most desperate for copper prices
it at the 2,040 ceiling, which is precisely the price at which its few hundred
credits buy nothing. The stake breaks the deadlock at genesis and the world
falls back into it as soon as the stake is spent, because its income is its
output and its output is what it could not buy. Forty-three per cent of all
sales are still refused, and flooding the galaxy with money moves that to 25%
and no further (§5).

That is a **circulation** fault, not a level one, and the candidates are
design decisions rather than constants:

1. **Trade credit.** A port buys against the value of what its plant will make
   this week, not against the coins in the drawer. The ledger stays closed —
   a debt is a transfer with a delay.
2. **The seller takes what the buyer has.** A hull that has flown three jumps
   with copper nobody can pay for already discounts in reality; here it flies
   on with a full hold.
3. **Subsidy on the buying side.** The exchequer already subsidises a yard
   pressing plate. The same transfer aimed at a colour's starved finishing
   ports would be one line and is testable in an afternoon.

Recommendation: **(1), measured against (2)**, before anything else in the
economy is touched. Every remaining chain on the floor table above is
downstream of it.

---

## 8. Verification

```sh
GOTOOLCHAIN=auto go vet ./... && GOTOOLCHAIN=auto go test ./internal/...

# the numbers in this report
GOTOOLCHAIN=auto GAZ=1            go test ./internal/universe -run TestGazetteer -v
GOTOOLCHAIN=auto GAZ=1 GAZSEED=7  go test ./internal/universe -run TestGazetteer -v
```

The instrumentation behind §1–§5 — hooks in `runPlant` and in the sale, and
seven throwaway rigs sweeping fleet size, `baseMine`, `importFactor` and the
genesis purse — was temporary and has been removed. The two changes that
remain are the proportional dig in `universe.go:mine` and the deleted
`Hostile()` gate in `world.go:stake`.

---

*The Fab recipe was innocent. Silicate was not scarce, it was last in the
queue; the copper was not missing, it was sitting in a warehouse three jumps
from a factory that could not afford a single ton of it. Both faults were
rules this economy had already written and then failed to apply to the newest
hundred and nine worlds on its own map.*
