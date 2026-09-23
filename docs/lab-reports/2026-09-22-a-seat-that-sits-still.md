# A seat that sits still, and a price for being large

**22 September 2026** · `gonex/internal/universe` · follows
[the war that never happened](2026-09-22-the-war-that-never-happened.md)

Two items from the last report's list, both of which it had recorded as
design decisions rather than bugs: make the capital a founding fact, and add
an anti-snowball term.

The first turned out to be worth **+29% chips**, which is not what a
bookkeeping change about seats was supposed to buy.

---

## 1. Fault 17: a capital that would not sit still

`Capital(c)` returned *the most populous world this colour holds*, recomputed
on every call. There are fourteen callers.

Population grows. Over 730 days every colour's seat drifted — Blue's went
Sirius Station → Ursa Minor Beta → New Sahara — while everything that makes a
world a capital stayed exactly where it was put at genesis:

- two endowed `Works`, so the capital can run its mandates *and* a trade;
- an endowed `Bastion` and `Habitat`;
- the **Munitions** and **Shipyard** mandates, which are the only reason any
  hull plate or rounds get made on purpose anywhere in the galaxy.

So the government was at one world and its arsenal at another. Every
consequence compounds:

| caller | what it did with the drifted seat |
| --- | --- |
| `rally()` | called hulls home to a world with no magazine to arm them from |
| `expand()` | launched flights from a world with no arsenal |
| `restock()` | filed rounds convoys to a world that was not the one burning them |
| `revive()` | mandated new industry at a world with no spare `Works` to run it |
| `arm()` | drew from an empty warehouse |

**The fix.** The seat is elected once, at genesis, by population — that is
the founding fact — and recorded on the universe. `Capital()` is now a lookup
and has no opinion.

It moves exactly once more, and only if it is taken. `succeed()` elects the
most populous world still held and **the founding mandates go with it**,
because a capital without an arsenal is precisely the zero-kill-percentage
planet Konquest says no government should ever have. Endowed buildings do not
move: a Bastion is masonry and stays where it was built. A mandate is an
instruction, and an instruction belongs to whoever is giving it.

Succession runs inside `conquer()`, so there is no window in which a colour
has no seat. The seat is carried in the `Snapshot`; a save written before
seats existed restores as all-zero and is re-founded rather than coming back
with three governments that have no capital.

### What it bought

| | war report | seat fixed | |
| --- | ---: | ---: | --- |
| **Chips** | 146.6 | **189.0** | **+29%** |
| Acid | 562.7 | 628.9 | +12% |
| Fluid | 450.2 | 503.1 | +12% |
| Rations | 1,902.5 | 2,030.4 | +7% |
| Ore | 1,497.6 | 1,530.3 | +2% |
| Steel | 488.1 | 509.6 | +4% |
| Rounds | 51.7 | 39.6 | −23% |
| Melt | 49.2 | 38.2 | −22% |

Seed 7 agrees in direction: chips 86.5 → 96.4, and the war redistributes the
map (Green 52 → 54, Blue 40 → 38, Red 20 → 21). Mass balances and the ledger
balances on both seeds.

Rounds and melt fall, and that is the same story as last report rather than a
new one: munitions are being *spent* now that flights actually launch, and
hulls flying flights are hulls not hauling fuel. The trade is real and it is
the one the war was always supposed to make.

The 29% is worth being precise about, because it would be easy to claim too
much. It is not that a fixed seat is a clever optimisation. It is that four
separate subsystems had been addressing a world chosen by a rule none of them
knew about, and three of the four were built in the last two days — the
rally point, the revive plan and the bottleneck-driven subsidy all assume
"the capital" means one stable thing. Adding machinery that addresses a
moving target is how a drifting seat went from a curiosity to a 29% tax.

---

## 2. The span of control

Until this morning conquest was impossible, so no colour could run away and
the absence of a diminishing return could not matter. It matters now.

The shape of the absence: **every term in this game rewards size linearly and
none of them charges for it.** `FleetCap` is eight hulls per world held, so
twice the territory floats twice the merchant marine, flies twice the
flights, and takes twice the worlds. There was no opposing term anywhere.

Strategic Conquest's answer is adopted here — production time rises as the
empire grows — and it is a good answer because it is *not a cap*. A large
empire is still larger. It is simply worse per world than a compact one, so
conquest acquires a natural stopping point that is a judgement rather than a
wall.

```
  overhead(n) = 1                          for n <= span
              = (span / n) ^ 0.5           beyond it
```

Three places charge it, and they are the three legs of the snowball:

| leg | effect |
| --- | --- |
| the factory floor | every plant on the colour's worlds runs at `overhead` of its rate |
| the fleet ceiling | `FleetCap` grows sublinearly instead of linearly |
| the expansion clock | a stretched government looks for a target less often |

`span = 60` worlds, exponent `0.5`. At twice the span a government keeps 71%
of its capability, at four times 50%.

### It is deliberately inert today, and that is a claim I have to defend

The largest colour holds 52 worlds at genesis and reached 54 over the run.
Against a span of 60 the term never fired once, which is why **none of the
numbers in §1 are affected by it** — the +29% is the seat, measured clean.

A dormant balance term is indistinguishable from no term at all, so it is
unit-tested directly rather than through a run that never reaches the size:

- it charges nothing at or below the span, and nothing at all to neutral
  space, which is not a government;
- it is monotone and bounded on `(0, 1]` out to eight times the span;
- it keeps ~71% at 2× and ~50% at 4×, as designed;
- **total capability still rises with size.** Four times the territory yields
  strictly more than the span does. An empire that shrinks when it wins is a
  bug wearing a balance term's clothes, and the test says so in those words;
- `FleetCap` for 4× the worlds is more than 1× and less than 4×.

The alternative was to calibrate the span down to ~40 so it bit at genesis.
That was rejected: it would have taxed Green and Blue from day one for
territory they were *given* rather than took, which is a difficulty setting
dressed as a physical constraint, and it would have made §1's measurement
uninterpretable. The term should speak when somebody runs away, and until
somebody does it should be silent.

Two guards worth noting, both found by writing it:

- The overhead is refreshed once a day and cached, because counting a
  colour's worlds is a scan of the map and `produce()` would otherwise do it
  once per plant per world per tick.
- It is initialised in `New`. Before the first tick nothing has counted
  anybody's worlds, and an uninitialised zero reads as a government with no
  capability at all — a fleet cap of nought on day zero.

---

## 3. Where this leaves the list

Both items from the last report are done. Ahead of everything else, unchanged
and now three reports old:

1. **The compost and scrap loops.** 1.33 Mt of compost idle, zero scrap made
   against 2,966 t/d of breaker capacity. Both return paths broken.
2. **The yard tier's inputs**, which still gate every military thing in the
   game and the production-quota dial behind it.
3. **Energy**, which no industrial process consumes.
4. **The money circulation fault**, where a starved port posts the ceiling
   price and therefore affords the least.

New, and small: the span of control wants revisiting once a colour actually
passes 60 worlds, to check the exponent is doing what the unit test says it
does when a real economy is attached to it.

---

## 4. Verification

```sh
GOTOOLCHAIN=auto go vet ./... && GOTOOLCHAIN=auto go test ./internal/...
GOTOOLCHAIN=auto GAZ=1            go test ./internal/universe -run TestGazetteer -v
GOTOOLCHAIN=auto GAZ=1 GAZSEED=7  go test ./internal/universe -run TestGazetteer -v
```

Four new tests: the seat moves only when it is taken; a successor inherits
the mandates and the lost capital gives them up; the span charges nothing
inside itself and is gentle and monotone outside it; the fleet ceiling grows
sublinearly.

---

*A capital that was recomputed on every call had quietly become the thing
four different subsystems were aiming at, and none of them knew it could
move. Fixing where the government sits was worth more than anything done to
the factories.*
