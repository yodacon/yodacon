# Game mechanics: the whole machine, and what proves each part of it

**22 September 2026** · overview + verification · companion to
[the lithium fuel cycle](2026-09-22-lithium-fuel-cycle.md) and
[the transmutation core](2026-09-22-transmutation-core.md)

Three reports now describe pieces of this economy and none of them describes
the shape of it. This one is the map: every mechanic in the game, the one
rule that defines it, where it lives in the code, and **the test that would
fail if it stopped being true.**

It is written to be checkable. Section 12 is a verification table with 148
tests behind it, section 13 is what is *not* built, and everything claimed
here was re-derived from the source this afternoon rather than from the
previous reports.

```
go vet ./...                 clean
go test ./internal/...       15 packages, 148 tests, all pass
```

---

## 1. The spine: two conservation laws

Almost every rule below is a consequence of one of these, and neither is a
matter of taste.

### Mass

> Every ton in the game was put in the ground at genesis. From then on it can
> only **move** — out of the crust, into a warehouse, into a hold, across a
> lane, through a factory that changes what it is, and finally into a mouth
> or a slag heap. It is never minted.

`econ.Books.Audit` rolls **every** pool in the universe into one column —
crusts, warehouses, holds, hull structure, wreck fields, the sink, and the
externally-held pools the player stands in — and compares the total to
genesis. A pool left out of that call reads exactly like a leak, which is the
correct failure: forgetting to count a warehouse *is* losing track of the
mass in it.

The check is on the **grand total, not per material**, because transformation
is the entire point of industry. A smelter is supposed to destroy ferrite and
create steel. What no process may do is change how many tons there are.

### Credits

> Credits are minted at genesis and never again. Over hundreds of days of
> loading, delivering, tariffs, shore leave, subsidies, buildings and battles,
> every credit is still in some purse.

`econ.Pay` is the only mover, and `AuditCredits` proves the supply is
constant. A world's treasury running dry is therefore a *real event with a
real cause*, not a flag — a broke port quietly declines cargo and the courier
flies on.

**Verified:** `TestMassIsConservedOverALongRun`,
`TestCreditsAreConservedOverALongRun` (4 seeds × 400 days each),
`TestExternallyHeldMassIsAudited`, and the full-gazetteer rig at 730 days.

---

## 2. Matter — 30 materials in six tiers

`internal/econ`. The ordering is load-bearing in exactly one place: **the
first `BoardWidth` entries are `market.Commodities`, in order**, so a
planet's `Stock` and a ship's `Hold` are a *prefix* of a full material vector
and convert by copying rather than by lookup.

| tier | materials | rule |
| --- | --- | --- |
| **board** (8) | Lumber · Ore · Rations · Medicine · Chips · Fuel cells · **Pellets** · **Melt** | what a spaceport posts a price for, and what the player trades |
| **refined** (10) | Steel · Copper · Silicon · Polymer · Grain · Lithex · Lithium · Heavylith · Acid · Fluid | made, not sold; what a smelter hands a fabricator |
| **yard** (3) | Hull · Rounds · Missiles | what a fleet is made of and what it shoots |
| **returns** (2) | Compost · Scrap | the only two places the flow goes back uphill |
| **crust** (6) | Ferrite · Cuprite · Silicate · Volatiles · Biomass · **Spodumene** | finite; the only tier mining can produce |
| **sink** (1) | Slag | counted, and worthless — which is what makes the books balance |

Four predicates carry the travel and consumption rules:

- `Organic()` — eating it leaves Compost rather than Slag. This is the rule
  that decides which half of consumption is renewable.
- `Fuel()` — Pellets and Melt. Same energy, different packaging, no
  conversion outside a refinery.
- `Hot()` — Lithium and Heavylith travel in a shielded cask or not at all,
  because a cask that survives a jump costs more than the ton inside it.
  **This is what pins the finishing plant beside the breeder rather than
  beside the customer.**
- `Bulkable()` — Steel, Lithex, Acid and Fluid are refined but ship like
  goods, for two different reasons: a city eats steel, and the hot worlds
  *import* concentrate and chemicals or they run nothing.

---

## 3. Industry — modules that plug into modules

`internal/industry`. Seventeen chains built from twenty-three primitives, and
one operation that matters:

```go
func (m *Module) Then(next *Module) *Module
```

Plug `m`'s outputs into `next`'s inputs; get back a module whose ports are
whatever the pair could not satisfy internally. **Because the result is
itself a module, it plugs into a third the same way.** A supermodule is not a
special kind of thing with its own rules — it is a module that remembers what
it was built from.

Two properties, both tested: mass balances (outputs never outweigh inputs;
the difference is slag), and the chain runs at its bottleneck, recorded at
composition time because that is the only moment the shortfall is visible.

### A chain names its mines but does not contain them

The first real bug this economy had. A chain that *contained* its mine netted
the mine's output against the mill's intake internally, so the plant appeared
to need nothing and produce lumber out of thin air — while the world's own
mining moved the same tons a second time. Digging is the world's job; the
plant draws from the warehouse like any other input.

### Nobody authored a speciality

`industry.Rank(reserve, rad)` orders the chains a world *could* run by the
tonnage backing them, limited by the thinnest seam each depends on. The world
stands up the best two (plus one per `Works`). From one seed that produces
genuinely different ports out of one rule — and nobody wrote "chip industry"
down anywhere. A world that can smelt and fabricate has one.

### Four scheduling rules, all of them corrections

| rule | why | what it cost before |
| --- | --- | --- |
| **civic first** | the gardens eat before the timber mill does | a world exported lumber while it starved |
| **mandated next, in full** | a world told to keep an arsenal must not split its ferrite with the yard next door | 2 of 3 capitals rated zero |
| **the rest share proportionally** | two plants on one warehouse are rationed by what each asked for | 2,204 t/d of ore against **35 t/d of steel** |
| **the pithead cap** | ranked chains are sized against the dig budget, not the census | nameplate was 3–5× what the ground could ever feed |

The third is the most instructive. Serving plants in list order let the first
take the lot; the ore crusher stands first, asks for the whole day's ferrite,
and the steel mill beside it runs at zero for ever. `Describe()` printed both
plants at full rate and the bottleneck report showed nothing wrong.

---

## 4. Siting — the dose, and hostile worlds

The seam **is** the dose: `econ.Dose` and the spodumene endowment are the
same draw, so a clean world has no spodumene at all however rich it is
otherwise, and a hot world's reserve scales with exactly how hot it is. This
is the one place in the game where two facts about a world are forced to be
the same fact.

| | clean | milling ≥0.10 | smelting ≥0.35 | breeding ≥0.55 |
| --- | --- | --- | --- | --- |
| pop ceiling | 32 M | ~1.35 M | ~975 k | ~675 k → 40 k floor |
| growth | full | taxed up to 94 % | | |
| licensed line | — | Lithium milling | Radiant smelting | Fuel pellets / Fuel melt |
| worked by | a workforce | machines (`autoCrew`, scaling with dose) | | |
| flag | a polity | **whoever is paying** | | |

Four rules make a hostile world work, and each exists because its absence
broke something measurable:

1. **Mandate** — a licensed world is *founded* as a refinery, as a capital is
   founded with an arsenal. Which fuel it pours alternates on stellar ID, so
   the map carries both forms.
2. **`autoCrew`** — a dose that will not let a city grow will not stop a
   machine. Without it we had put every fuel seam in the universe under the
   only worlds with nobody to work them.
3. **The stake** — a refinery opens with working capital sized to its own
   line. Without it, the hot worlds sit in a trap with no exit from inside:
   no chemicals → no fuel → no revenue → no chemicals, at 9 % of nameplate
   for a simulated year, silently.
4. **Free ports** — Konquest's neutrals do not produce, *except* a hostile
   world, which is not a polity with a workforce that can strike but a
   licensed site with machines on it.

---

## 5. The market — price is a quantity, not a hash

`World.Reprice`, run every day. Price is **cover**: how many days of real
demand the warehouse holds, where demand is industrial appetite plus what the
population eats. Short worlds pay up to 3×; glutted ones as little as 0.35×.

Three steepenings, each with an argument:

- **Rations, ×7** — people will pay anything for the next meal, which turns a
  famine into the best-paying route on the board and gets it relieved without
  anybody scripting relief.
- **A mandated line's feedstock, ×5** — a refinery short of acid is not
  inconvenienced, it is *shut*. At the ordinary curve it could not outbid
  ordinary trade, and fifteen refineries wanting 525 t/day of reagent between
  them were served sixty.
- **A producer sells cheap** — that is what a producer *is*, and it is what
  gives a route a direction. An Exchange narrows the spread.

Every finished good has an appetite, and that is not decoration. The first
cut gave chips, ore and steel no consumer, so they piled up in warehouses
nobody would ever need them from and the whole network went quiet on day 104
with every hull idle. **A commodity with no sink stops being traded the
moment the first warehouse fills.** The intermediates deliberately have no
appetite — nobody eats copper; a fabricator does.

---

## 6. Traffic — every hull, including the ones nobody is looking at

`internal/traffic`. Off-sector hulls are stepped with a one-dimensional
momentum integrator along the lane they are flying:

```
F = thrust·cruise − drag·v²     a = F/m     v += a·dt     s += v·dt
```

where `m` is **hull plus cargo**. A full hauler genuinely accelerates worse
than an empty one and the return leg is genuinely faster. That is the reason
this is physics and not a countdown: *the economics of a route fall out of
the mass it carries.*

**Lanes have length.** 60 Mm in-system plus 180 Mm per jump, charted off the
real 1997 jump graph. Until `ChartLanes` existed every lane was the
registry's default, which meant the route ranking's margin-per-megametre was
margin divided by a constant — 109 ports, economically, all in the same place.

**"Local" means one jump.** The same-type rule says intermediates ride
in-system shuttles and cross a jump only on a chartered Lane. That is exactly
right for a map with several stellars per system; the recovered gazetteer has
**one stellar in each of its 109 systems**, so "same system" was never true
for any pair of worlds and copper, silicon, polymer and grain could not move
anywhere, ever.

**Statuses:** Idle · Loading · Hauling · Returning · Fighting · Resident ·
LaidUp · Lost. `Resident` is the player's seam — a hull inside the sector
being flown is owned by `internal/world` and the registry stops moving it.
`LaidUp` is the only status whose tons are somewhere else, which is why
`Structure()` must not count it.

---

## 7. Routing — routes are found, not authored

`FindRoutes` looks at what ports are *actually paying today*. Because prices
move with real warehouse levels, a route that paid last week can be gone this
week: the map of trade is a consequence of the simulation rather than a
fixture in it.

One restriction does the strategic work: **a hull trades with its own colour
and with neutrals, never with an enemy.** So taking a world does not just
deny it to the other side, it opens a market to you.

Ranked by margin per megametre — a fat spread across the galaxy is worth less
than a decent one next door, because the hull could have run the short one
three times — then doubled for a port in the same system and doubled again
for an ally.

**Dispatch asks its own doorstep first.** A hull only loads a parcel that
starts where it is standing, and on a 109-port map the odds that any of the
galaxy's twenty best runs begins at this particular berth are negligible.
Before `loadHere`, acid was made at 678 t/day and carried at 16.

---

## 8. The agents — five missions

| mission | what it does |
| --- | --- |
| **Courier** | free trade, routed by what pays today |
| **Convoy** | a standing order to carry a named material A → B |
| **Flight** | a standing order to move hulls; arriving hostile it fights, friendly it garrisons, at peace it turns back |
| **Harvester** | flies empty to a seam, lifts crust *straight out of the ground* into its own hold against a royalty, carries it to the nearest port that wants it |
| **Survey** | carries nothing, earns nothing; reads a seam and leaves. +45 % dig for 90 days where it lands, +20 % one jump out |

The last two exist because the population-scaled mine was the one hard
ceiling in the economy: a rich rock with nobody on it produced **nothing**,
for ever, and no amount of shipping could help because there was nothing at
the pithead to ship. A harvester is extraction capacity that is *mobile*. A
survey is the only thing in the game that raises extraction without raising
population — and the only thing a government does purely because the
arithmetic says so.

---

## 9. The merchant fleet sizes itself

The census is still honest — a hull nobody is looking at is a ship with a
position and a manifest. What was wrong was the **size**: sixteen hulls a
colour against 109 ports and ~4,000 live routes delivers about one and a half
cargoes per port per year.

- **Opening**: hulls proportional to worlds held. A trade network's size is a
  property of the map, not of a constant somebody typed once.
- **Growth**: *berth pressure* — the unserved margin still on the board per
  hull afloat — presses plate above 90 k cr/hull and breaks a ship up below
  22 k. The gap is deliberately wide; a fleet that commissions and lays up
  around one threshold oscillates.

Nothing is minted. A commissioned hull is `Hull` tons out of a yard's
warehouse; a laid-up hull is the same tons back on the same shelf. Growth
costs somebody a warehouse, which is exactly why the fleet is allowed to
breathe.

---

## 10. War, government, and the ship

**War.** A dead hull's cargo is not scattered into the sink — it drops where
it died as a persistent wreck field, on the books, and the nearest holds with
room take what they can, nearest first. Winning a battle is a mining
operation: the loser's hulls are next week's plate. A planet with no Rounds
rates zero whatever it has built, so the supply line the war economy made
cuttable by guns is also cuttable by trade.

**Government.** Eight buildings on two shared cost ladders; the first
building at a world is its charter and the seat follows it. Every effect is a
change to a number the simulation already reads — `Works` re-stands industry
with one more slot, `Habitat` raises the ceiling and the luxury exponent,
`Exchange` narrows the producer discount, `Lane` charters a shuttle link, the
military three raise Rating and draw steel. **Nothing has a second dial.** An
upgrade buys a claim on flow, never a dividend, because that is the only
return a zero-sum game can honestly offer.

**The ship.** One power grid — reactor, battery, capacitors, radiators, heat
ceiling — operated by every game mode; flight, battle, warp, entry and the
pad differ only in which loads are screaming. On top of it, two ladders:

*Reactors* decide how much of a ton of fuel the hull can reach, **and which
of the two fuel forms it accepts** — so the reactor you bolt in decides which
refineries in the galaxy are your suppliers.

| class | takes | burnup | range | breeds |
| --- | --- | ---: | ---: | --- |
| Thermal pile | Pellets | 5.5 % | ×1.0 | — |
| Sodium fast loop | Melt | 19.5 % | ×3.5 | — |
| Shipboard breeder | Melt | 25.0 % | ×4.5 | 0.35 t/t from a fertile blanket |

*Confinement* holds the reentry pillow. The magnetopause stands off at
`(p_mag/p_flow)^⅙`, so doubling the field buys 12 % of radius and **nobody
buys their way out of that exponent.** What a yard sells is a fix for one of
four distinct failure modes: too little field (HTS rewind), a bottle that
leaks at the poles (multipole cusp ring), a pillow with no steering (phased
array), and air too thin to grip (seed injection ring — *inertial*
confinement, the only rung that works where the magnetic ones do not).

---

## 11. Where the player stands

The two places a ton could hide are exactly the two places a player stands,
so both are registered with the auditor: **the player's own deck**, and **the
holds of census hulls currently flying as ships in this sector**. A test
moves 25 t into an *unregistered* pool and asserts the audit calls it a leak
— a safety net is only worth having if forgetting to use it fails loudly.

The rule that keeps the handover honest: **a hull is in exactly one place.**
While it is `Resident` the registry stops integrating it and its cargo lives
in the world's manifest and *not* in its census row. Two copies of a cargo is
two copies of its mass, and the auditor finds it inside a day.

The player's purse is a purse. Everything paid at a counter or a pad lands in
a treasury; the ledger sees the player's money as one more place money can be.

---

## 12. Verification

Every mechanic above, and what fails if it stops being true.

| mechanic | code | test |
| --- | --- | --- |
| mass conserved, long run | `econ/audit.go` | `TestMassIsConservedOverALongRun` |
| credits conserved, long run | `econ/ledger.go` | `TestCreditsAreConservedOverALongRun` |
| pools outside the package are counted | `universe.Account` | `TestExternallyHeldMassIsAudited` |
| no primitive creates mass | `industry/module.go` | `TestNoPrimitiveCreatesMass` |
| composition is closed and conserves | `Module.Then` | `TestCompositionIsClosedAndConserves` |
| a chain runs at its bottleneck | `Compose` | `TestTheChainRunsAtItsBottleneck` |
| an impossible recipe scales back | `Module` | `TestAnImpossibleRecipeIsScaledBackNotHonoured` |
| speciality follows the crust | `industry.Rank` | `TestRankFollowsTheCrust` |
| contested inputs are rationed | `universe.produce` | `TestContestedInputsAreRationed` |
| a mandated line is dug for first | `universe.mine` | `TestAMandatedLineIsDugForFirst` |
| only hot worlds refine fuel | `Chain.MinRad` | `TestOnlyHotWorldsRefineFuel` |
| the seam is the dose; capitals safe | `econ.Dose` | `TestTheSeamIsTheDose` |
| a refinery is capitalised | `World.stake` | `TestARefineryIsCapitalised` |
| the lithium line runs and balances | `industry/catalog.go` | `TestTheLithiumLineRunsAndBalances` |
| hostile worlds are worked unmanned | `World.autoCrew` | `TestHostileWorldsAreWorkedUnmanned` |
| hot cargo stays local; concentrate travels | `shuttleOnly` | `TestCaskCargoStaysLocal` |
| prices respond to scarcity | `World.Reprice` | `TestPricesRespondToScarcity` |
| growth is made of rations | `universe.grow` | `TestGrowthIsMadeOfRations` |
| a starved world stops growing | `universe.grow` | `TestAStarvedWorldStopsGrowing` |
| the organic loop closes | `industry.Civic` | `TestTheOrganicLoopCloses` |
| intermediates need a shuttle link | `shuttleLink` | `TestIntermediatesMoveOnlyByShuttle` |
| the census never shrinks | `traffic.Registry` | `TestTheShipCensusIsFixed`, `TestLossesShowUpInTheBooksAndTheCensus` |
| wreck cargo is never lost | `universe.wreck` | `TestWreckCargoIsNeverLost`, `TestDestroyingALadenHullConservesItsCargo` |
| nearest hold scoops first | `Registry.Salvage` | `TestNearestHoldScoopsFirst` |
| yards replace losses from plate | `replaceHulls` | `TestYardsReplaceLostHulls` |
| fleet sized by map and board | `merchantfleet.go` | `TestFleetIsSizedByTheMapAndTheBoard` |
| harvester lifts from the ground | `prospect.go` | `TestHarvesterLiftsFromTheGroundAndBalances` |
| a survey lifts the seam and expires | `prospect.go` | `TestASurveyLiftsTheSeamAndExpires` |
| battle conserves; undefended worlds fall | `universe/battle.go` | `TestEngageConservesAndTakesAnUndefendedWorld` |
| a fortress spends rounds, leaves scrap | `universe/battle.go` | `TestADefendedWorldSpendsRoundsAndLeavesScrap` |
| no rounds ⇒ rating zero | `universe.Rating` | `TestRatingIsZeroWithoutRounds` |
| standing orders die with their government | `orders.go` | `TestStandingOrderRunsAndCancelsOnConquest` |
| shared ladder; seat follows the charter | `buildings.go` | `TestLadderIsSharedAndSeatFollowsCharter` |
| doctrine, tax and priority spend | `policy.go` | `TestDoctrinesDiffer`, `TestTaxFundsUpgradesByDoctrine`, `TestPriorityWorldIsUpgradedFirst` |
| the trifecta is doubly balanced | `govt/govt.go` | `TestEveryAxisIsZeroSumAcrossTheColours`, `TestEveryColourLeadsAndTrailsSomething` |
| capitals keep a magazine | `universe/policy.go` | `TestCapitalsKeepAMagazine` |
| the handover cannot duplicate cargo | `app/resident.go` | `TestHandoverDoesNotDuplicateCargo` |
| planet stock mirrors the warehouse | `app/economy.go` | `TestPlanetStockMirrorsTheWarehouse` |
| **three packages agree on the board** | `econ`/`market`/`world` | **`TestTheThreePackagesAgreeOnTheBoard`** |
| **the game is seeded from the real map** | `app.seedUniverse` | **`TestTheGameIsSeededFromTheRealMap`** |
| **the outfitter reaches the flight model** | `power.Catalog` → `Vehicle.Conf` | **`TestTheOutfitterReachesTheFlightModel`** |
| the shield cuts heat flux | `reentry/physics.go` | `TestShieldReducesHeatFlux` |
| stand-off obeys the sixth root | `confinement.go` | `TestCoilBoostObeysTheSixthRoot` |
| cusp seal is worth more in drag | `confinement.go` | `TestCuspSealIsWorthMoreInDragThanInStandoff` |
| the array buys authority and costs power | `confinement.go` | `TestSteeringArrayBuysAuthorityAndCostsPower` |
| the ring works where field does not | `confinement.go` | `TestInjectionRingWorksWhereFieldDoesNot` |
| a stock hull is unchanged | `confinement.go` | `TestStockHullIsUnchanged` |
| entry is deterministic and replayable | `reentry/sim.go` | `TestDeterminism`, `TestAutolandAcrossProfiles` |

### Three seams that had no test until today

The bolded rows are new, and they were the three places where two packages
had to agree about a number and nothing would have failed loudly if they
stopped:

1. **The board width.** `econ.go` has claimed since it was written that "the
   app's tests assert all three against each other." Nothing did. Widening
   the board from six to eight for the lithium fuels is precisely the change
   that would have silently desynced `econ.BoardWidth`,
   `len(market.Commodities)` and `world.CommodityCount` — and a hold one
   entry short does not crash, it just loses the cargo. The test also pins
   the fuels to the *last two* slots, which is what lets a pre-lithium
   six-wide save still read correctly.
2. **The map.** That the game seeds from the real gazetteer, under the real
   polities, with lanes charted off the real jump graph — and then runs a
   year of it with both books balanced and the lithium cycle actually
   turning. It asserts lanes *differ*, which is the thing that was silently
   false for the whole life of the project.
3. **The shelf.** That buying a reactor changes which fuel the hull can burn
   (not just its megawatts), that a swap *replaces* rather than stacking its
   mass, and that confinement outfits reach `reentry.Vehicle.Conf` and move
   the flight numbers.

### Reproducing the measurements

```sh
go vet ./... && go test ./internal/...            # 15 packages, 148 tests

REPORT=1 go test ./internal/universe -run TestUniverseReport -v   # 11-world rig
GAZ=1    go test ./internal/universe -run TestGazetteer      -v   # the real map
GAZ=1 GAZSEED=7 GAZDAYS=1200 go test ./internal/universe -run TestGazetteer -v
```

In a running game, the developer console carries `economy`, `trifecta`,
`routes`, `journal [n]`, `world [id]`, `day [n]`, `standings`, `govern`,
`doctrine`, `priority`, `policy`, `tune` and `seed`. `GONEX_CMD="day 200;economy"`
runs them at boot; `GONEX_SEED` reproduces a universe.

---

## 13. What is designed but **not** implemented

Stated plainly, because an overview that blurs this is worse than no overview.

| | status |
| --- | --- |
| **The transmutation core** — the nuclide chart as a price list, the barium line, capture and photodisintegration, lithium as a charged battery | **design only.** No code. See the companion report. |
| **The energy economy** — star classes, insolation, collectors, a per-world energy budget | **design only.** The gazetteer carries no stellar data at all. |
| **Mass–energy conservation** — energy as a tonnes-equivalent pool in the auditor | **design only.** The current law is mass alone, which is exact because no current process converts matter to energy. |
| **Three bodies per system** — one planet, one station, one nebula; every body landable and upgradeable | **not built.** This is the #1 item and most of the economy's measured faults trace to its absence. |
| **Fixed colour spawn positions** | **not built.** Belongs with the map work. |
| **Fuel as a jump consumable** — burnup wired to voyage range | **not built.** Pellets and Melt are traded and eaten by populations, but a hull's own jump does not burn them, so the reactor ladder's range multiplier is currently a shop label rather than a constraint the player feels. |
| **The commodity detail screen** — agents on mission, nearby prices, best path | **not built.** `RoutesFrom` already computes exactly this for the AI. |
| **Icons and stand-in art** for the new commodities and both outfit ladders | **not built.** The two fuels especially need to be distinguishable at a glance, since the reactor decision hangs on it. |

---

## 14. Known broken, and measured

The mechanics work. The **balance** does not, and the numbers say exactly
where. Full gazetteer, 109 ports, 730 days, seed 20260922:

| | measured | should be |
| --- | ---: | --- |
| Pellets made | 7.6 t/d | 443 t/d of appetite — **2 %** |
| Melt made | 23.3 t/d | 286 t/d of appetite — **8 %** |
| Chips made | 60.7 t/d | ~815 t/d of appetite |
| **Hull plate pressed** | **0.0 t/d** | enough to replace losses |
| Shipyards in the galaxy | 3 | more than 3 |
| Berth pressure | 5,795–8,406 k cr/hull | commissioning threshold is 90 k — **64–93× over, and it cannot fire** |

One causal chain explains all six rows:

```
one world per system  →  copper is a one-jump good with nowhere to go
                      →  chips at 7% of demand
                      →  shipyards at 0% (chips are 15% of the yard recipe)
                      →  no hull plate
                      →  the fleet cannot grow however hard the board pays
                      →  not enough hulls to fly acid to 15 scattered refineries
                      →  fuel at 2% of demand
```

Everything downstream of the first line is a symptom. **Three bodies per
system is not a content item; it is the fix for the economy's only structural
fault.** The transmutation core is the second answer to the same fault —
different cargo instead of a better road — and the two are complementary
rather than alternatives.

Mass and credits balance throughout. Nothing here is a correctness bug; it is
a map that cannot support the economy standing on it.

---

*Two conservation laws, seventeen chains, five missions, eight buildings,
thirty materials, 148 tests. The rules are consequences; the numbers are
measurements; and the one thing the galaxy is short of is somewhere for the
copper to go.*
