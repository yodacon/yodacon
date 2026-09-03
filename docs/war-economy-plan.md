# Plan: The War Economy

**Every ship is a trader. Every trader is a soldier. Territory is a supply
problem.**

Today the deathmatch is a closed box: twelve AI per team charge each other
forever, ammunition is infinite, death is a teleport back to a spawn point, and
the three planet clusters are scenery with a sprite ID. Meanwhile the campaign
next door has a real commodity market (`internal/market`), a real star map
(`internal/galaxy`), a real power plant (`internal/power`) and real cities
(`internal/city`) — and the battle knows about none of it.

This plan wires them into one machine. The argument in one paragraph:

> A fighter that must **land to rearm** is a fighter with a home. A home that
> must be **supplied** is a home with a supply line. A supply line that can be
> **cut** is territory. And because every hull in the game has a cargo hold —
> even the interceptors — the supply line is not a separate fleet of trucks to
> babysit. It is the same pilots, flying the same sorties, with a second job.

The territorial fight is therefore decided by *logistics*, not by frags. You do
not lose a planet because your ships died. You lose it because it ran out of
bullets.

---

## 0. What already exists, and what it costs to reuse

| Have | Where | Reused as |
| --- | --- | --- |
| Commodity board, station price bias, day walk, news events | `internal/market` | Which planet produces what — the bias *is* the production table |
| Systems, stellars, jump links, routing | `internal/galaxy` | Where a shipment comes from, and the leg it flies |
| Reactor / battery / capacitor / heat grid | `internal/power` | Every ship's energy budget, not just the player's |
| Procedural spaceport, per stellar | `internal/city` | Population → industrial capacity |
| Player hold, credits, repair damage, crew | `app.Voyage` | The player's row in the same economy |
| Planets, spawn points, items, proximity sweep | `internal/world` | The battlefield objects that gain economic state |

Almost nothing here is new invention. It is mostly **connecting two halves of a
game that were built to the same specification and never introduced.**

### Step zero: a bug that is also the first feature

`internal/scene/scene.go` parses `team` on every `<planet>` and drops it on the
floor — `placement` has a `Team` field, `world.Planet` does not:

```go
for _, p := range doc.Planets {
    w.Add(&world.Planet{
        Body:     world.Body{P: gmath.V(p.X, p.Y)},
        SpriteID: p.Sprite,          // p.Team goes nowhere
    })
}
```

`triforce.xml` has always declared four planets per team spawn area, correctly
teamed, and the game has never known it. Give `Planet` a `Team` and the map is
already a territorial map.

---

## 1. The ship becomes a vehicle with a manifest

Three new budgets on `world.Ship`, all derived from things a ship already has —
`Crew` (1–50, rolled in `NewShip`) and `spec.Mass`:

```go
type Ship struct {
    // ...existing...
    Rounds    int          // bullets aboard
    RoundsMax int          // magazine — crew to serve it, tonnage to stow it
    Hold      []int        // tons per market commodity, same index as market.Commodities
    Junk      float64      // tons of salvage aboard, sold on landing
    HoldMax   float64      // tons
    Grid      *power.Grid  // generator + batteries, scaled from the hull
    Role      Role         // Warship | Hauler — a bias, never an exclusion
}
```

**Magazine.** `RoundsMax = 40 + 6*Crew + Mass/100`. Crew is the gun crew;
tonnage is the shot locker. A 50-hand heavy runs ~400 rounds, a lone
interceptor ~90. `Fire()` gains one line — no round, no shot — and a pilot
checks the magazine before it commits to a pass. *(Shipped: konex's `Rabies`
and `Siege` turned out to differ only in whether they brake at close range,
which is now the per-pilot `Standoff` tuning. Both fold into one doctrine.)*

**Hold.** `HoldMax = Mass/50 * roleFactor`, `roleFactor` 1.5 for a hauler, 0.35
for a warship. The Yodacon's 100-ton deck in `dockmode.go` is exactly `Mass/50`,
so the player's existing hold is the neutral case and needs no special-casing.
The warship factor is deliberately *not zero*: **a fighter with eight tons is a
fighter that will detour for salvage**, and that detour is the whole design.

**Energy.** `power.For(spec)` scales `power.Stock()` by mass. NPCs do not need
the player's per-frame fidelity — step their grid at 4 Hz with a coarse `Load`
(engines from throttle, screens from recent damage, hotel flat). Thrust scales
with `Flow.Served`, so a browned-out ship is visibly *slow*, which is the tell
a pilot reads across the map. Firing spends capacitor charge, generalizing the
`FireGate` hook that today only serves `MainPlayer`.

Energy is cheap and comes back at any friendly planet. **Bullets are bought.**
That asymmetry is the entire economy: a ship can always limp home, and can never
fight its way out of an empty magazine.

---

## 2. The planet becomes an industrial actor

```go
type Planet struct {
    Body
    SpriteID  int
    StellarID int
    Team      Team

    Pop     int       // from the city that grows on it
    IP      float64   // industrial points in the buffer
    IPMax   float64   // buffer ceiling
    Credits int       // the planet's treasury
    Stock   []int     // tons per commodity in the warehouse
    Scrap   float64   // tons of spacejunk in the yard
    Pad     []*Ship   // ships currently turning around
}
```

**Population comes from the city.** `internal/city` already grows a full
spaceport per stellar — streets, blocks, lots, buildings with floor counts.
Sum building volume into `city.Population(stellarID)` and the metropolis the
player lands in *is* the industrial number that supplies the fleet. No new data
file, no balance table: the skyline is the stat.

**Industrial points** regenerate at `Pop/40000` per day (a day being 120 battle
seconds) and cap at two days of it. Everything the fleet needs spends them:

| Service | Credits | IP | Notes |
| --- | --- | --- | --- |
| Energy top-up | 0.05/MJ | **none** | a utility, never refused — see below |
| Rounds | 3 each | 1 per 20 | the throttle on the war |
| Hull repair | 4/point | 0.4/point | first thing to go dark |
| Replace a lost hull | — | 60 | offset by `Scrap`, see §5 |

A planet under pressure spends its buffer faster than it earns it. When `IP`
hits zero the pad starts refusing services **in reverse priority order** —
repairs first, then rounds. A fleet flying out of a starving planet is fully
charged, dented, and carrying eleven bullets.

**Power turned out to belong outside the IP economy entirely.** Metering it per
megajoule against a 2,600 MJ battery made it by far the most capacity-expensive
line on the receipt, so a squeezed planet refused *power* first — the exact
inverse of the intent. It is a utility, not manufacturing: billed in credits as
far as the treasury goes, and put on the connector regardless. That is what
makes "a ship can always limp home and get back up" true rather than aspirational.

**Production and consumption need no new table either.** `market.Price` already
derives a fixed per-station bias from `hash(stellar*31 + c*7)`. Read it in
reverse: bias below 0.9 means the station is *long* that commodity — it produces
it; bias above 1.15 means it is *short* — it consumes it, and its industry
stalls without it. The market's geography and the war's geography become the
same geography, for free.

---

## 3. Orders: the tape every pilot flies

The point is not smarter AI. The point is **legible** AI — a player watching the
map should be able to read what a ship is doing and why. So orders are an
explicit, printable tape, not an emergent behavior.

```go
type Order struct {
    Kind      OrderKind // Load, Transit, Defend, Land, Engage, Salvage
    Commodity int
    Stellar   int
    Planet    *world.Planet
}
```

Each ship holds a **duty** (the current order) and a **rider** (a standing
secondary that can interrupt it). The rider is the dual task, and it is what
makes this a fleet rather than two fleets:

- A **hauler's** rider is *defend*: enemy inside 1500 units of its escort charge
  and it fights, hold still full.
- A **warship's** rider is *salvage*: debris inside 800 units and free space in
  the hold, and it detours to scoop.

The canonical hauler tape — the loop as described, verbatim in code order:

```
LOAD    Ore at Cenron          (a system that produces it)
TRANSIT Cenron → ConEx          (3 days, 100 fuel, the rider may fire en route)
DEFEND  ConEx Prime             (arrive hot; you are cargo and you are a gun)
LAND    ConEx Prime             (4.0 s on the pad)
          ↳ unload 84 t Ore into Stock       +11,760 cr to the pilot
          ↳ auto-sell 12 t scrap             planet Scrap +12
          ↳ rearm 310 rounds, repair 22 hull, top up 2600 MJ
LAUNCH  clean — weapons and fuel, hold empty
ENGAGE  until rounds < 15% or health < 30%
        ↳ back to LAND
```

Every transition prints one line through `w.Notify`:

```
RED 4  (Trident, hauler)  LOAD 84t Ore — Cenron
RED 4  DEFEND ConEx Prime — 2 hostiles inbound
RED 4  LAND ConEx Prime — 84t Ore, 12t scrap, rearm 310
RED 4  LAUNCH clean — engaging
```

That console tape is the feature. A battle you can *read* is a battle you can
form intentions about.

---

## 4. The turnaround

Landing is not instantaneous and not free. A ship inside `CollisionRange` of a
friendly planet with a `Land` order enters the pad for **4 seconds** (scaled by
how much work it asked for, capped at 8). While on the pad it is removed from
collision and combat — and it is *not* shooting, which is the cost. A planet's
pad has finite berths (`1 + Pop/40000`), so a fleet that all comes home at once
queues, and a queue under fire is a massacre.

This is also where the player's existing landing already lives: `L` near a
planet runs the full reentry corridor and the spaceport screen. The AI's
4-second pad is the same transaction with the minigame elided — one
`planet.Service(ship)` call that both paths share, so the numbers can never
drift apart.

---

## 5. Salvage: the battlefield feeds the shipyard

**A dead ship is not deleted, it is scattered.** `die()` currently spawns an
explosion and rolls a 1-in-5 item drop. It gains a debris drop:

```go
type Debris struct {
    Body
    Mass float64  // tons
    Mix  []int    // what it was carrying, by commodity
}
```

with `Mass = hold tonnage + junk aboard + spec.Mass/500` hull scrap. Debris
drifts on the dead ship's velocity, slowly, and **does not expire** — it is a
pile, not a pickup.

**The hard cap is a hundred, and it is enforced by merging, never by deleting.**
`world.Salvage` keeps the field:

1. On a new drop, find a cluster within 300 units — if one exists, add mass to
   it and fold the mix in.
2. Otherwise create one.
3. If the field is at `maxDebris = 96`, merge the two nearest clusters first.

Mass is conserved across every merge, so the battlefield's total wealth is a
number you can assert on in a test. Ninety-six piles is well under a hundred
floating objects for the whole system and keeps the O(n²) proximity sweep
honest.

**Any ship auto-collects**, exactly like `Item` does today — proximity, no
input, up to free hold space, partial scoops leaving the remainder floating.
Cargo commodities go to `Hold`, hull scrap goes to `Junk`.

**Junk is auto-sold on landing** at a scrap price, and this is where the loop
closes: the planet's `Scrap` pile discounts hull replacement, one ton off one
IP. A team that wins the salvage fight **builds ships faster than its economy
should allow** — and a team that wins the *battle* but leaves the wrecks
floating hands its enemy a shipyard. Contesting a debris field becomes a real
tactical objective, on ground the fight has already chosen for you.

---

## 6. Losing a planet

Territory falls out of the above rather than being a separate capture mechanic:

1. Supply line cut → warehouse `Stock` drains → industry stalls.
2. `IP` buffer empties → the pad stops repairing, then stops rearming.
3. Its squadrons fly dry sorties and stop winning engagements.
4. Once `IP == 0` and munitions stock is 0 for a continuous **60 seconds**, the
   planet goes `TeamNone`, and its `SpawnPoint` deactivates.
5. A neutral planet with only one team's ships within 2000 units for 30 seconds
   flips to that team, at zero `IP` — captured, and useless until resupplied.

Because the spawn points on `triforce.xml` sit *on* the team planets, losing
planets shrinks the area you respawn into. Lose the cluster, lose the corner.
The map we already have is the map this needs.

---

## 7. Milestones

Each one is playable and observable on its own — none is a big-bang merge.

| # | Slice | Observable when done |
| --- | --- | --- |
| **M0** ✅ | `Planet.Team` wired through `applyMap`; planet economy struct; `city.Population` | `planets` lists teamed worlds with a population and an IP number; team rings on the map and minimap |
| **M1** ✅ | Magazines and per-ship grids; `Fire()` checks rounds; brownout slows thrust | Pilots run dry, turn for home, and come back loaded — the `fleet` roster shows who is on what orders |
| **M2** ◐ | `planet.Service`, the pad queue, the `Land` order — **landed early, with M1** | Ships stream home, sit 2–8 s, come back shooting. Battle sustains itself indefinitely. |
| **M3** | Debris, the 96-cluster merge field, auto-collect, scrap sold on landing | Wrecks accumulate; ships detour; `Scrap` climbs at the yard |
| **M4** | The order tape, roles, riders; the console log | You can read the fleet's intentions off the console |
| **M5** | Warehouse stock, production/consumption from market bias, interstellar `Load`/`Transit` | Shipments arrive from named systems; cutting a lane starves a planet |
| **M6** | Control loss and capture; spawn deactivation | A corner of `triforce.xml` can actually fall |

M0–M3 is the whole feel of it; M4–M6 is the strategy layer on top.

---

## 7b. What building M0–M2 actually taught us

Four bugs, none of which any unit test would have found, and all four stopped
the game dead without logging a thing:

1. **`Grid.SpendCap` deducted a partial charge and then reported failure.** A
   ship holding the trigger at frame rate swallowed every joule that trickled
   into the bank and never once reached the price of a shot. The whole fleet
   was permanently gun-cold with charging capacitors. Predates this work — the
   player had it too. A gun needs an all-or-nothing draw (`TrySpendCap`); a
   shield is the one thing that legitimately takes what it can get.
2. **The return-condition switch asked "must I go home?" before "may I leave?"**
   Since a committed pilot always answers yes to the first, the release branch
   was unreachable and all thirty-six pilots latched into a permanent hold over
   their own pads with full magazines.
3. **`bingo` tested the battery and `resupplied` did not.** The two disagreed
   about one gauge, so a flat battery flipped a pilot between orders every
   single frame. Any pair of enter/leave conditions must cover exactly the same
   gauges, with a margin between them.
4. **`enterSystem` deleted every planet the scene had loaded** and replaced them
   with a ring of gazetteer stellars, so the territorial map never survived into
   the running game. Every pilot reported `RTB no port` under a sky full of
   planets it did not own. Held worlds are not scenery.

The lesson worth keeping: **a simulation this size has to be flown to be
tested.** All four were found by running a headless 15-minute battle and
printing what the fleet was doing; none would have failed an assertion about a
single ship. `TestTheWarSustainsItself` now flies exactly that, across four
seeds, and asserts the war is still going at the end.

---

## 8. Risks, and where this gets away from us

- **`ForEachNear` is O(n²) over every entity.** Today: ~36 ships, some missiles.
  After M3: ships, missiles, explosions and up to 96 debris clusters, each
  sweeping the full list. This needs a uniform grid before M3 lands, not after.
- **Determinism.** `world.Rand` is seeded and the market is a pure hash of
  `(station, commodity, day)`. Keep it that way — every economy number must be
  reproducible from the seed, or none of this is testable and balance work
  becomes folklore.
- ~~**The dry-battle failure.**~~ **Resolved by landing M1 and M2 together**, as
  the risk itself suggested. Finite ammo does not break the deathmatch, it
  converts it: with the turnaround in place the same scene becomes a
  three-colour supply war that runs indefinitely instead of a brawl that runs
  until everyone is bored. Nothing was ever unplayable in between.
- **Save format.** `save.State` grows ship manifests and planet ledgers. It is
  already versioned and tolerant of a short `Cargo` slice (`voyage.go` pads it);
  extend that same forgiveness rather than bumping and invalidating berths.
- **Two landing paths drifting.** The player's reentry minigame and the AI's
  4-second pad must call one `Service` function. If rearm ever costs the player
  something different than it costs an NPC, the economy stops being a single
  system and becomes two arguing ones.

---

## 9. Files this touches

```
gonex/internal/world/ship.go          Rounds, Hold, Junk, Grid, Role; Fire() gate
gonex/internal/world/spawnables.go    Planet economy fields; Debris
gonex/internal/world/salvage.go       NEW — the merge field and its cap
gonex/internal/world/planet.go        NEW — Service(), IP accounting, control flips
gonex/internal/ai/doctrine.go         NEW — the order tape, stances, per-pilot tunings
gonex/internal/ai/ai.go               Rabies/Siege check rounds before committing
gonex/internal/scene/scene.go         carry planet team through applyMap
gonex/internal/city/city.go           Population(stellar)
gonex/internal/power/power.go         For(spec) — scale the stock plant by hull
gonex/internal/market/market.go       Produces(stellar, c) / Consumes(stellar, c)
gonex/internal/app/dockmode.go        the player's landing calls the same Service
gonex/assets/data/maps/triforce.xml   pop/role attributes per planet
```
