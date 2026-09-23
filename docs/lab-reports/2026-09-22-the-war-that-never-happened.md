# The war that never happened, and the production math that was missing

**22 September 2026** · `gonex/internal/universe` · follows
[the bottleneck detector](2026-09-22-bottleneck-detector-and-the-resource-loop.md)

Three design documents were put forward for the governor menu: Strategic
Conquest's production and base-building loop, Konquest's production-math
strategy with its four AI types, and Konquest's interface. Reading them
against the running game produced a measurement nobody had taken.

**On the full gazetteer, over 730 simulated days, there were zero conquests
and zero hulls lost.** The map at day 730 was the map at genesis. Three
governments, 112 held worlds, 106 populated neutrals sitting there, 561
hulls, 49,853 tons of munitions manufactured — and not one attack, ever.

This is not a balance problem. An entire layer of the game was inert and no
test, report or screen had said so, because nothing was measuring the one
number that would have shown it.

Four causes, stacked. Three are now fixed and the war is live: **0 → 2
conquests, two worlds changing hands, one hull lost.** Mass balances, the
ledger balances, 162 tests pass.

---

## 1. Why nothing ever attacked

`expand()` is fifteen lines and every one of its gates was shut.

### Fault 14: no hull is ever idle at a capital

```go
idle := u.idleAt(cap, c)
if len(idle) < n+1 {
    return
}
```

`idleAt` counts a colour's hulls **berthed at that world** with nothing to
do. A flight leaves from somewhere and arms itself from that somewhere's
arsenal, so this is the right requirement.

But `arrive()` berths a courier wherever it last delivered — *"a trader's
home is wherever it last delivered"* — which is the right rule for trade and
fatal in combination. Measured: sixty-six hulls idle on an average day, and
**zero of them idle at a capital**. The first line of `expand()` returned
every time it was called, for two years, for all three colours.

This is the gap Strategic Conquest fills with its *Army Destination*
automation: set a place, and what you build walks there. gonex had no way to
gather a fleet at all.

**Fix: `rally()`.** Every governor cycle, a colour calls home enough idle
hulls to make up a flight, nearest first. It does not touch a hull that is
hauling or loading — trade is the point of the game — only ones standing
idle at somebody else's pad, and only as many as a flight needs.

### Fault 15: the attack gate compared the wrong two numbers

```go
if target == nil || targetR >= u.Rating(cap) {
    return
}
```

A world's `Rating` is gonex's inheritance of Konquest's **kill percent**, and
it is a measure of *defence*: garrison, bastions, and how many days of rounds
are in the magazine. Comparing a target's defence to **the capital's own
defence** is a category error — the capital's rating has nothing to do with
what the flight leaving it can do.

The consequence: a government whose own magazine was dry could never attack
anything, however weak. With rounds at 68 t/d galaxy-wide that was all three
of them, permanently. Red's capital sat at a rating of **0.00**, which by the
source game's own terms is the one thing no government should allow.

**Fix:** arm the flight first, then ask whether *the flight* can win, using
`flightRating` — which already existed and was only ever called inside the
battle itself.

### Fault 16: the AI was Konquest's *weak* AI, by Konquest's own taxonomy

The proposal's table is explicit:

| AI type | behaviour |
| --- | --- |
| Default (Weak) | neither aggressive nor defensive |
| **Becai (Balanced)** | **uses distance, kill %, and production optimally** |

gonex picked its target on kill percent alone, tie-broken by population.
Distance did not enter, and neither did what the world was worth. Measured
consequence, before the fix:

```
  Red   would take Darven, rated 0.55, 7 jumps away
  Green would take Darven, rated 0.55, 4 jumps away
  Blue  would take Darven, rated 0.55, 4 jumps away
```

All three colours scoring the identical world, one of them seven jumps out —
because 106 populated neutrals rate inside a narrow band, so kill percent
separates almost nothing and the population tie-break decides everything.

**Fix: `Targets()`, scoring all three terms.**

```
  score = produce / ((1 + rating) * (1 + jumps))
```

A world that produces nothing scores nothing however cheap it is, which stops
a colour walking its strike fleet to a barren rock. Cost and distance both
*divide* rather than subtract, so a target twice as far must be twice as
valuable to be worth the same — and neither term can drive a score negative,
which a subtractive form does as soon as a galaxy gets wide.

Distance was never missing data. gonex charts every lane length and the trade
board already divides by it; the number was sitting unused on the other side
of the package. The war simply never asked.

### Fault 17, unfixed: `Capital()` is whoever is biggest today

`Capital(c)` returns the colour's most populous world, recomputed every call.
Over 730 days each colour's capital *moved* — Blue's went from Sirius Station
to Ursa Minor Beta — which means the founding mandates (the arsenal, the
yard) stay with a world that is no longer the capital, while the revive plan
and the rally point address one that was never founded for it.

Not fixed in this pass because it is a design decision, not a bug: either a
capital is a seat that moves with population, in which case the mandates and
the arsenal should move with it, or it is a founding fact and `Capital()`
should return the world that was founded as one. Recorded for the next pass.

### The result

| | before | after |
| --- | ---: | ---: |
| Conquests in 730 days | **0** | **2** |
| Hulls lost | 0 | 1 |
| Red capital's kill rating | 0.00 | 0.89 |
| Green worlds | 52 | 50 |
| Blue worlds | 40 | 42 |
| Blue population | 145.3 M | 212.0 M |

And the targeting now behaves like the AI it was supposed to be — three
capitals, three different answers, distance doing visible work:

```
  Red   from Armstrong       → Sirgil III   rated 0.00 ·  6 jumps · 1079.6 t/d · score 154.23
  Green from Akio            → Sirgil III   rated 0.00 · 10 jumps · 1079.6 t/d · score  98.15
  Blue  from Ursa Minor Beta → Tiber II     rated 0.00 ·  2 jumps ·  379.1 t/d · score 126.36
```

Blue takes the small world two jumps away over the fat one ten jumps away.
That is the whole point of the third term.

The economy paid for it, correctly: rounds fell 68.3 → 51.7 t/d, because
munitions are now being *spent*, which is what an arsenal is for. Chips
156.8 → 146.6 and steel 531 → 488 as hulls leave the trade lanes to fly
flights. Rations rose 1,803 → 1,902. Hull plate rose 0.5 → 0.8.

---

## 2. What belongs in the governor menu

The desk is four tabs today — `WORLD`, `CHART`, `BOOKS`, `GOVERNMENT` — and
the `GOVERNMENT` tab already carries doctrine, policy, priority, standings
and seed. The three proposals map onto it cleanly, but not all at once, and
the ordering matters more than the content.

### Adopt now: a `WAR` tab, because the production math is invisible

The single strongest idea in the Konquest UI document is not a feature, it is
a stance: *"the game is essentially a spreadsheet with a colour grid — all
strategic depth comes from the numbers, not the interface."* gonex already
believes this. The desk's own report says every number on it is one the
console can print from the same seed.

So the gap is not that gonex needs a prettier war screen. It is that **the
production math is not on any screen at all**, which is precisely why a dead
war went unnoticed through four lab reports. A `WAR` tab showing what
`Targets()` now computes — for every world: owner, kill %, distance in jumps,
daily production, and the resulting score — would have made fault 16 visible
on sight, and fault 14 visible as a column of zeroes under "idle at capital".

Three Konquest tools transfer directly and are nearly free, because the data
already exists:

| Konquest | gonex |
| --- | --- |
| Hover a planet → name, owner, ships, production, kill % | `World.Name`, `Govt`, `Garrison()`, `produceOf()`, `Rating()` — all live |
| **Measure Distance** (click two planets, get turns) | `u.lane()` in megametres, `jumpsBetween()` in jumps — charted, and never shown to the player |
| **Fleet Overview** (origin, destination, count, turns remaining) | `Fleet.Hulls` with `From`, `To`, `Status`, `V`, `S` — the voyage state is all there |
| Turn-end news dialogs | `Journal.Logf`, already written to on every conquest |

"Measure Distance" deserves particular attention. Konquest calls it *the
primary planning tool* — it tells you how many turns the defender has to
reinforce. gonex computes that number for every pair of worlds on every
route scan and has never once shown it to the player.

### Adopt next, with a condition: production quotas

Strategic Conquest's *Production Quotas* — percentage sliders per unit type,
the AI allocating automatically — is the most direct answer to "put it in the
governor menu", and it is the right long-term shape. A colour's yards,
arsenals and missile works splitting their throughput by a slider the
governor sets is exactly the kind of lever this desk is for.

**It should not be built yet, and the reason is measured.** The yard tier
currently runs at a mean rate of **0.000** — `Shipyard` and `Ordnance` are
the two worst lines on the factory floor, waiting on chips, fuel cells and
acid. A slider that allocates a share of zero is theatre.

This is the same trap as the revive plan's first version in the last report:
a control surface over a tier that produces nothing looks like a feature and
changes nothing. The order is: fix the yard tier's inputs, *then* give the
governor a dial on its output.

### Adopt the anti-snowball term; it is the missing counterweight

Strategic Conquest scales production time with empire size — more cities,
longer builds for everything. gonex's `FleetCap` does the opposite: eight
hulls per world held, so the bigger a colour gets the faster it can grow.
There is no term anywhere that makes a large empire harder to run than a
small one.

This matters more now than it did this morning, because until today conquest
was impossible and a runaway leader could not exist. The moment the war works,
the absence of a diminishing return becomes live. A production-time (or
throughput) penalty scaling with worlds held is one line and should land
alongside the war, not after somebody measures a Blue galaxy.

### Do not adopt: the naval rock-paper-scissors

Strategic Conquest's counter table — destroyer beats submarine, submarine
beats transport, helicopter beats battleship — needs ten unit types with
detection rules, fuel rules, carrier capacity and aerial spotting. gonex has
**one** hull type, differentiated by what it is carrying and by
`govt.GunFactor`.

That is not an oversight to be corrected. gonex's combat is a rating
comparison because its interesting decisions are economic: whether the
magazine is full, whether the flight is worth arming, whether taking a world
two jumps away beats taking a rich one ten jumps out. A counter matrix moves
the interest to unit composition, which is a different game, and would
require a tactical layer this project has deliberately never built.

The *transferable* half is fuel and range, which gonex already has designed
and unbuilt: pellets and melt are traded and eaten but a hull's own jump does
not burn them. A fighter that spots a submarine and cannot get home crashes;
a gonex flight six jumps out with a fast-loop reactor and no melt should be
in the same trouble. That is the counter system worth having, and it is
already item 3 on the priority stack.

### Fog of war: partly there, and honest about it

Konquest's blind map and Strategic Conquest's black tiles both exist here in
skeleton — `prospect()`, `sendSurvey()`, `SurveyLift()`, `recordSurvey()` —
but they gate *prospecting*, not *knowledge*. Every colour's route board sees
every world's warehouse. Making the trade board respect what a colour has
actually surveyed would be a deep change to `refreshTradeMasks` and would
make the economy strictly worse before it made it better; it belongs behind
the money and energy work, not in front of it.

---

## 3. The lineage argument

It is worth stating plainly why these three documents are worth more to this
project than an equivalent amount of good advice from elsewhere.

gonex is the third generation of a line: ConEx (1997) → Konex → gonex, and
the codebase quotes Konquest by name in five places. `Rating` *is* kill
percent. `sendFlight` leaves one hull behind because *"a planet is held by
the ship that stays"* is Konquest's rule. `mine()` opens with *"Konquest's
neutrals do not produce"*. The restock convoy exists because *"Konquest's
planet with a zero kill percentage is the one thing no government should let
happen"* — and this report found Red's capital sitting at exactly that,
undetected, for two simulated years.

So the proposals are not foreign ideas being imported. They are the source
material, read back against a descendant that inherited three of the four
terms and dropped the one the source game calls decisive. The most valuable
thing in all three documents was one row of a table — *Becai: uses distance,
kill %, and production optimally* — because it named the missing term
precisely enough to test.

---

## 4. Where this leaves the list

Built this pass:

- `Targets()` — the production math, all three terms, ranked.
- `rally()` — Strategic Conquest's Army Destination: a government can gather
  a fleet.
- The attack gate now compares the flight to the target instead of the
  capital to the target.
- A permanent `THE PRODUCTION MATH` section in the balance rig, so a dead war
  cannot hide again.

Next, in order:

1. **The yard tier's inputs**, still — chips, fuel cells, acid. Everything
   military is downstream of it, and the production-quota dial is blocked
   behind it.
2. **An anti-snowball term**, now that conquest is possible.
3. **`Capital()` as a moving seat** (fault 17) — decide it, either way.
4. **The `WAR` tab**, showing `Targets()` and the idle-at-capital count.
5. **Measure Distance and Fleet Overview**, which are nearly free.

Unchanged from the last report and still ahead of all of this: the compost
and scrap loops, energy, and the money circulation fault.

---

## 5. Verification

```sh
GOTOOLCHAIN=auto go vet ./... && GOTOOLCHAIN=auto go test ./internal/...
GOTOOLCHAIN=auto GAZ=1 go test ./internal/universe -run TestGazetteer -v
```

The rig prints `THE PRODUCTION MATH` alongside the balance and bottleneck
tables: each capital's kill rating, its idle hulls, and the target it would
take next with all three terms shown.

---

*An entire layer of this game had been switched off since it was written, and
what found it was not a test or a screen but a table of AI types from the game
it descends from. The war was gated on a hull being idle somewhere no hull
ever was, on a comparison between two numbers that were never about each
other, and on a score missing the one term the source game calls decisive.*
