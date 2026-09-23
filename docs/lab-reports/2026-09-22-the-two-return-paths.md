# The two return paths, and what a fed galaxy costs

**22 September 2026** · `gonex/internal/{econ,universe}` · follows
[a seat that sits still](2026-09-22-a-seat-that-sits-still.md)

The bottleneck detector found these two without being asked and they went to
the top of the list: **1.17 megatonnes of compost lying idle**, and **zero
tons of scrap made in two simulated years** against 2,966 t/d of breaker
capacity. Compost → biomass and scrap → steel are the only two places in this
economy where the flow goes back uphill. Neither had ever run.

Both now run. The results are not all in one direction and the report says
so.

| | before | after | |
| --- | ---: | ---: | --- |
| Compost processed | ~1,333 t/d | **4,673** | the loop |
| Biomass returned | 1,333 t/d | **2,720** | +104% |
| Scrap made | **0.0** | **552.4** | from nothing |
| **Steel** | 509.6 | **912.5** | **+79%** |
| **Rations** | 2,030.4 | **3,158.5** | **+56%** |
| Ore | 1,530.3 | 1,587.2 | +4% |
| Acid · Fluid | 628.9 · 503.1 | 641.1 · 512.9 | +2% |
| **Chips** | 189.0 | **132.1** | **−30%** |
| Rounds | 39.6 | 29.4 | −26% |
| Held population | 341.5 M | **479.2 M** | **+40%** |

Mass balances and the ledger balances. Seed 7 agrees on steel (+49%) and
disagrees on chips (96.4 → **107.0**, +11%), which matters and is discussed
in §4.

---

## 1. The scrap loop: nothing was making any

`Scrap` exists so that "winning a battle becomes a mining operation: the
loser's hulls are next week's plate." Its only source in the entire game was
`wreck()` — a hull destroyed in battle.

The war did not work until this morning. So in 730 days the galaxy produced
**zero tons of scrap**, and 218 breaker's yards with 2,966 t/d of capacity
between them had never processed a gram. Half the return path had never once
run, and nothing said so, because a plant with no input logs nothing.

**The fix is the one the population was always going to provide: a city
wears things out.**

```go
func (m Material) Durable() bool {
    switch m {
    case Steel, Ore, Chips:
        return true
    }
    return false
}
```

Structure and electronics only, and the list is short on purpose. Fuel is
burnt and leaves nothing — if fuel left scrap a city could run a reactor and
mine the ashes, and there is a test that says so. A round is fired. Medicine
and lumber are organic and compost.

`eat()` now mirrors its organic branch: 40% of a worn-out durable lands on
the pad as scrap, the rest goes to the sink as rust and landfill.

**The design rule survives, and that was the constraint.** `econ.go` states
it plainly — *"that split is what makes food renewable and steel not"* — so
the recovery had to be partial. A ton of steel a city uses comes back as
0.40 t of scrap, and a breaker turns that into 0.75 of a ton of steel: a
round trip of **30%**. A city recovers some of what it wears out. It cannot
live on it, and a test asserts the round trip stays below one.

Result: 552.4 t/d of scrap, and steel from 509.6 to **912.5 t/d**.

---

## 2. The compost loop: the plant was the right size for a city that no longer existed

This one was more interesting, because nothing was missing. **All 218
inhabited worlds had a composter. None of them was absent. None was broken.**
And the galaxy still had 1.17 Mt of compost piled on worlds that owned one.

The composter is sized in `standUpIndustry`, which runs when something
*decides* — a Works bought, a mandate changed, a world taken. That is right
for industry: what a world makes follows from its rock and its orders.

The civic path does not follow from its rock. It follows from its
**population**, which is the one quantity in this game that grows
continuously and without bound — a homeworld doubles in about eight weeks.

So Capella's composter was built for the eighteen million people it had on
day zero and was still exactly that size a simulated year later. Earth's was
96.1 t/d against a city that had outgrown it. The plant was not missing; it
was the right size for a city that no longer existed.

This is the same shape as the capital that would not sit still, one report
ago: something computed once, used against something that moves.

**The fix** splits `standUpCivic()` out of `standUpIndustry()` and re-runs it
on a different clock — from `grow()`, which is the only place population
changes, whenever the population has drifted 10% from what the plant was
sized against.

### The headroom and the threshold are one decision, not two

The first cut used a 20% drift threshold against the composter's existing
1.1 margin, and it only got two thirds of the way: idle compost fell from
1.17 Mt to 365 kt and stopped.

Between two re-sizings a city grows by up to `civicDrift`, and its *organic
appetite grows faster than that*, because medicine sits on the luxury
exponent and is superlinear in heads. With 20% of drift and 10% of headroom
the inflow outran the plant for the whole window, every window, for ever.

So the margin has to clear the appetite growth a full drift window produces:
`compostMargin = 1.30` against `civicDrift = 0.10`, which leaves the
composter ahead of its city at every point in the cycle and ahead by enough
to work off a backlog. There is a test asserting the relationship rather than
the two numbers, so changing one without the other fails.

One more trigger was needed: **a Habitat raises the luxury exponent without
moving the population one head.** `resizeCivic` watches population and would
never have noticed, so the composter would be undersized from the day the
habitat opened. `Build` now re-stands civic on `Habitat` as it does industry
on `Works`.

Idle compost: 1.17 Mt → **8.9 kt**.

---

## 3. Three bugs in the detector, found by trusting it

The detector was two days old and pointing at these two materials. Reading
its own output carefully found that all three of the things it said about
them were wrong.

**It said "no plant".** Compost and scrap have no plant and never will — one
is made by eating and the other by wearing things out or losing them in
battle. The detector read that absence as *nobody makes it*, which was the
one thing it was not. `attribute` now exempts return materials.

**It said 172,817 t were idle.** `Wants()` deliberately excludes the civic
modules for anything but crust, because *a composter's want for compost is
not import demand and must not price as such* — which is correct for pricing
and wrong for asking whether a heap is misplaced. A world with a working
composter reported `Wants(Compost) == 0`, so every pile on every world that
could eat it counted as stranded. A new `consumes()` asks the question
`Wants()` deliberately does not answer. Idle compost now reads 8,946 t.

**It reported a nameplate of 0.0 for crust** — a pit has a budget, not a
capacity — so everything in the ground read as though nothing produced it.
Crust now reports its reserve.

With all three fixed, both return paths now diagnose as **"upstream short"**:
the composters have 8,282 t/d of capacity against 4,673 t/d of compost, and
the breakers 2,705 t/d against 552 t/d of scrap. The consumer is the larger
side, which is the safe direction to be wrong in.

---

## 4. What a fed galaxy costs: chips −30%, and an honest account of it

Chips fell from 189.0 to 132.1 t/d. That is a real number and it needs an
explanation rather than a footnote.

**It is not the scrap loop.** A clean A/B with `junkShare` at 0 and 0.40 and
everything else identical:

| | chips | steel | rations | scrap |
| --- | ---: | ---: | ---: | ---: |
| scrap loop off | 137.9 | 547.0 | 3,114.2 | 0.0 |
| scrap loop on | 132.1 | **912.5** | 3,158.5 | 552.4 |

The scrap loop costs **4% of chips and buys 67% more steel**. That trade is
not close.

**It is the compost loop, through population.** A working food loop feeds
people, fed people multiply, and the held population went from 341.5 M to
479.2 M — up 40% — with rations up 56%. Chip *appetite* is on the luxury
exponent and is superlinear in heads, so demand rose faster than that, while
chip supply is gated on copper and silicate, which rose 28% and 8%.

So the galaxy is much larger, much better fed, and poorer per head in
electronics. That is a Malthusian result and it is arguably the economy
finally behaving like one — but it is a regression in a headline number and
it should not be dressed up as anything else.

**Seed 7 goes the other way on chips**: 96.4 → **107.0**, +11%, with steel
+49%. Two seeds disagreeing in sign on one metric while agreeing strongly on
another means the chip number is sensitive to map details rather than a
clean consequence of the change, and that one seed is not enough to call it.
Recorded as a thing to measure across more seeds rather than a thing now
known.

---

## 5. Cost, and where this leaves the list

The gazetteer tick is now **38.6 ms/day**, up from 34 — a 400-day catch-up is
15.5 s where it was 14. That is the strain counters, the overhead refresh and
the civic re-sizing, and it makes item 2 on the priority stack more pressing
rather than less.

Both return paths are closed. Ahead of everything else, unchanged:

1. **Energy**, which no industrial process consumes, and which would give
   the three fuels an industrial sink for the first time.
2. **The money circulation fault** — a starved port posts the ceiling price
   and therefore affords the least. Six of the ten worst bottlenecks still
   read *no money at the pad*.
3. **Amortise the catch-up across frames**, now 15.5 s.
4. **The yard tier's inputs**, which still gate everything military.

New, from §4: **chips need measuring across more seeds** before anyone treats
−30% or +11% as the real effect.

---

## 6. Verification

```sh
GOTOOLCHAIN=auto go vet ./... && GOTOOLCHAIN=auto go test ./internal/...
GOTOOLCHAIN=auto GAZ=1            go test ./internal/universe -run TestGazetteer -v
GOTOOLCHAIN=auto GAZ=1 GAZSEED=7  go test ./internal/universe -run TestGazetteer -v
```

Four new tests: wearing out durables leaves scrap and conserves mass; burnt
fuel leaves nothing; the composter grows with its city; and the headroom
covers the drift window — that last one asserts the *relationship* between
the two constants, so neither can be tuned alone.

---

*Both return paths had been broken since they were written, and in opposite
ways. One had no source at all because the war it depended on did not work.
The other had a plant on every inhabited world in the galaxy, all of them
running, all of them the right size for cities that had long since outgrown
them.*
