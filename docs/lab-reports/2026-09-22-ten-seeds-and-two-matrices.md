# Ten seeds, two matrices, and a correction to every number in this series

**22 September 2026** · `gonex/internal/{industry,universe}` · follows
[the two return paths](2026-09-22-the-two-return-paths.md)

The last report ended on an open question: chips fell 30% on one seed and
rose 11% on another, and one of those had to be wrong. Ten seeds later the
answer is that **neither was a measurement.**

| chips, t/d | over 10 seeds |
| --- | ---: |
| mean | 186.0 |
| median | 163.3 |
| min | 85.1 |
| max | 375.0 |
| **coefficient of variation** | **51%** |

A 4.4× spread between the best and worst map. Every single-seed before/after
figure in this series was measured against a background that moves by half
the quantity being measured. §1 says which of them survive and which do not.

With a method that works, two coefficient matrices were then adjusted and
measured properly — **paired, same seed before and after, so the map cancels**:

| | baseline | after | median | better on |
| --- | ---: | ---: | ---: | ---: |
| **Chips** | 186.0 | **204.1** | **+8.1%** | **8/10** |
| **Fuel** (pellets + melt) | 105.2 | **130.6** | **+22.8%** | **8/10** |
| Melt alone | 60.4 | 82.0 | +23.7% | 9/10 |
| Steel | 1,067.3 | 1,040.3 | −4.0% | 2/10 |
| Rounds | 63.5 | 52.2 | −3.2% | 4/10 |
| Rations | 2,848.9 | 2,861.6 | −0.2% | 4/10 |

The two metrics that were worst covered in the galaxy both rise on eight
seeds in ten. Steel, which the scrap loop had just raised 79%, pays four per
cent of it back. Mass and the ledger balance on every seed.

---

## 1. The variance, and what it invalidates

`TestSeedSweep` flies the full gazetteer on ten seeds and reports the
distribution instead of a number.

| | mean | median | min | max | CV |
| --- | ---: | ---: | ---: | ---: | ---: |
| Chips | 186.0 | 163.3 | 85.1 | 375.0 | **51%** |
| Steel | 1,067.3 | 1,021.1 | 362.8 | 1,682.9 | 36% |
| Rations | 2,848.9 | 3,001.6 | 1,979.3 | 4,113.0 | 21% |
| Copper | 658.2 | 658.8 | 449.8 | 842.1 | 19% |
| Ore | 1,531.5 | 1,505.1 | 841.0 | 2,184.7 | 27% |
| Rounds | 63.5 | 46.0 | 2.3 | 185.1 | **87%** |
| Pellets | 44.8 | 42.9 | 32.7 | 80.4 | 30% |
| Melt | 60.4 | 67.5 | 17.1 | 101.7 | 42% |
| Hull | 0.5 | 0.4 | 0.0 | 1.8 | **106%** |
| Population | 656 M | 656 M | 536 M | 806 M | 11% |

Population is the stable quantity at 11%. Everything industrial is not, and
the military tier is barely a distribution at all — rounds range from 2.3 to
185.1 t/d and hull plate from nothing to 1.8.

**This is itself the most important balance finding in the series**, ahead of
any of the deltas. A game in which the same rules produce 85 or 375 tons of
chips depending on which map you were dealt is not balanced, whatever its
mean is. The variance is the headline problem; §4 is honest about the fact
that this pass did not reduce it.

### Which earlier numbers survive

Being specific rather than vaguely contrite:

| claim | measured on | verdict |
| --- | --- | --- |
| Dig ration + stake: chips 65.4 → 157.6 (+141%) | 1 seed, +11% on a second | **survives.** Far outside one CV, and confirmed in sign on a second seed. |
| Seat as a founding fact: chips +29% | 1 seed | **unproven.** Inside the noise band. The mechanism is real and the argument for it does not rest on the number; the number does not stand alone. |
| Return paths: chips −30% | 1 seed, +11% on a second | **withdrawn.** It was noise, and the report said the sign was map-sensitive and unmeasured — which was right, and this is the measurement. |
| Return paths: steel +79% | 1 seed, +49% on a second | **survives** in direction. Both seeds large and same-signed. |
| The war: 0 conquests in 730 days | every seed | **survives.** Zero is not a distribution. |

The pattern: the big structural fixes — a loop that never ran, a war that
never happened, a fab that never got its turn at the pithead — clear the
noise easily, because they turn something off into something on. The tuning
deltas did not, and should not have been reported as though they had.

**Method, from here on: every balance claim is paired across the ten seeds,
and the honest summary is "better on N of 10", not a percentage.** A single
seed is now only good for finding a mechanism, never for sizing one.

---

## 2. The recipe matrix: two rows that did not agree

`recipes` is a coefficient matrix — inputs and outputs per unit of
throughput — and two of its rows contradicted each other.

```
  Furnace:  silicate 1.0            →  silicon 0.40
  Fab:      silicon 0.5 + copper 0.5 →  chips   0.45
```

A furnace hands its fab 0.40 tons of silicon per ton of throughput. The fab
asks for 0.50. `Compose` does exactly what it is documented to do and
throttles the whole downstream stage to `0.40/0.50`, so **every electronics
chain in the galaxy ran its fabricator at 72–96% of nameplate for ever**,
the spread being the owning government's yield.

That was never a shortage of anything. Both stages were fully supplied and
one of them could not use what the other made. It is the fault the very first
chip report went looking for and cleared — *"the recipe costs the chain 4% to
28% and the chain was running at 6%, so chasing it would have bought a
rounding error"* — which was the right call at the time and stopped being
right once the chain stopped running at 6%.

**The fix moves the fab, not the furnace.** 0.40 is close to the
stoichiometric ceiling for reducing silica (46.7% silicon by mass), so the
furnace is near physical truth and must not be inflated to paper over a
table error. Setting the fab's silicon port to 0.40 matches them exactly, and
is the truer picture besides: a chip is mostly package and interconnect, so a
fabricator eats more copper by mass than silicon.

Crust per ton of chips falls from **5.09 t to 4.53 t**.

| | median | better on |
| --- | ---: | ---: |
| **Chips** | **+11.3%** | **10/10 seeds** |
| Melt | +12.6% | 8/10 |
| Steel | +0.9% | 7/10 |
| Ore | +1.2% | 7/10 |
| Rounds | −11.4% | 3/10 |
| Copper | −0.8% | 4/10 |

Ten seeds out of ten. That is the first unanimous result in this series, and
it is unanimous because it removes a fixed structural loss rather than
shifting a balance of pressures around.

Rounds pay for it, and the mechanism is second-order: more chips drawn means
more copper drawn, and arsenals compete for the same dig budget downstream.

---

## 3. The price matrix: half of it is a dead letter

The resource-loop report applied the value-per-unit rule to this catalogue
and found two chains that destroy value at base prices:

```
  Lithium milling    −52.8 cr per ton of intake
  Radiant smelting   − 2.3
```

A mill turns 136 cr of spodumene and acid into 83 cr of concentrate. That is
arithmetically true and it was reported as a fault.

**Correcting it changed nothing. Not one metric, on one seed, by one ton.**

Lithex 185 → 370 and lithium 540 → 820, ten seeds, paired: zero across the
board. The reason is that neither material is ever traded. Lithium and
heavylith are `Hot()` — they ride in shielded casks that no ordinary courier
will take — and lithex is a hot cell's own feedstock, milled and smelted in
the same place. Their board prices price a transaction that does not happen.

So the finding in the previous report was **true and inert**: a real
arithmetic fault in a number nothing reads. It is a good reminder that a
coefficient is only a lever if something consults it, and that "this chain is
unprofitable on paper" says nothing about a chain whose product never goes to
market.

The corrected values are kept anyway, with the measurement recorded beside
them, because the moment an intermediate becomes haulable they stop being
inert.

### The finished fuels were a different matter

The same arithmetic on the stage that does sell:

```
  Press:  heavylith 0.78 + steel 0.22  →  pellets 0.86
          1,333 cr in                      740 cr out
```

A press turned 1,333 credits of clad heavylith and steel into 740 credits of
pellets — a finished fuel worth less than half its own feedstock. Pellets and
melt are board goods: ports post prices for them, couriers rank routes by
their margins, and populations buy them. Here the coefficient is read
constantly.

Pricing the two fuels above their feedstock — pellets 860 → 1,900, melt
1,020 → 1,400:

| | median | better on |
| --- | ---: | ---: |
| **Fuel (both)** | **+17.9 t/d mean** | **8/10 seeds** |
| Melt | +12.6% | 9/10 |
| Steel | −4.6% | 2/10 |
| Rations | −0.2% | 3/10 |
| Chips | −1.7% | 5/10 |

**This is a redistribution and the report will not call it anything else.**
The pithead is fixed; making fuel worth more pulls hauling and treasury
toward fuel and away from steel. It is kept because of *which* way it
redistributes: fuel cover was 6–14% of appetite, by a wide margin the worst
number in the economy, and steel had just been handed +79% by the scrap loop.
Spending four per cent of a windfall on the worst-covered good in the game is
a deliberate trade, not a free improvement.

---

## 4. What improvement to expect, and what not to

**Expect** the two weakest goods to be meaningfully less weak. Chips +8%
median on 8/10 seeds and fuel +23% median on 8/10 are the measured figures,
and the chip half of it is structural — a fabricator that can be fed keeps
being feedable regardless of what else changes, so that 11% should survive
future passes rather than being re-traded away.

**Expect nothing for the variance.** Chips CV went 51% → 46% and rounds 87% →
108%; hull is still a coin toss at 141%. Neither matrix touches the reason
the spread exists, which is that `Rank` gives a world the chains its rock can
back, and whether a colour's capital happens to sit on ferrite decides
whether it has a working arsenal at all. **That is now the top balance
problem in this economy**, ahead of any mean.

**Expect no help for the money fault.** Six of the ten worst bottlenecks
still read *no money at the pad*, and raising fuel prices arguably makes that
marginally worse for anyone buying fuel. The circulation fault is untouched
and remains the deepest thing on the list.

**Do not expect this to be the last word on the fuel prices.** Pellets at
2.2× is a large shock chosen to satisfy a per-stage break-even, not tuned.
A smaller multiplier was not swept, and the trade against steel would look
different at 1.5×.

---

## 5. Where this leaves the list

1. **The variance.** 51% on chips, 87% on rounds, 106% on hull. A rules set
   that produces 85 or 375 tons of chips depending on the deal is the
   balance problem; everything else is a mean being moved inside it.
2. **The money circulation fault** — a starved port posts the ceiling price
   and therefore affords the least.
3. **Energy**, which no industrial process consumes.
4. **Amortise the catch-up across frames**, now 15.5 s.
5. **Sweep the fuel multiplier** properly, per §4.

---

## 6. Verification

```sh
GOTOOLCHAIN=auto go vet ./... && GOTOOLCHAIN=auto go test ./internal/...

# the distribution, not a number — about four minutes
GOTOOLCHAIN=auto SEEDS=1 go test ./internal/universe -run TestSeedSweep -v -timeout 60m

# a narrower spread, or a shorter run
SEEDLIST=7,101,1997 SEEDDAYS=365 SEEDS=1 go test ./internal/universe -run TestSeedSweep -v
```

The sweep asserts mass and the ledger balance on every seed it flies, so it
is a conservation test as well as a balance rig.

---

*The useful result of this pass is not eight per cent more chips. It is that
a single seed was never enough to know that, and that four reports written
today quoted single-seed deltas as though it were. Two of those deltas
survive the ten-seed test, one is withdrawn, and one is unproven — and the
one unanimous improvement in the whole series turned out to be two rows of a
coefficient table that had simply never agreed with each other.*
