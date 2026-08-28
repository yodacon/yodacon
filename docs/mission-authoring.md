# Authoring Missions for the Yodacon

Our interpretation of how a mission gets made — combining the lesson from the
plugin-editing video linked on the homepage with the field semantics documented
in `vendor/docs/Nova Bible.txt`.

> **Scope caveat, stated once and loudly.** The Bible is the **EV Nova** resource
> reference. ConEx is a **classic EV** plugin. The two are cousins, not twins:
> classic EV's `mïsn` is smaller, its bit logic is plain bit *numbers* rather than
> Nova's expression strings, and several Nova fields (`Flags2`, `AvailShipType`,
> `DispWeight`, the `Require`/`Contribute` pair) have no classic equivalent.
> Everything below marked **[NOVA]** is documented fact from the Bible.
> Everything marked **[VERIFY]** is our inference about classic EV and must be
> confirmed against bytes we extract from ConEx before we trust it.

---

## 1. The lesson from the video

The video's author is porting scenarios and comparing two editors:

- **EV Edit** (classic EV, 1990s) — graphical. Sprite previews in the ship editor,
  and *map views* for both stellars and star systems. Fast to work in.
- **EV Nova's editor** — all text and numbers. You hold resource IDs in your head
  or in a notepad beside the window. No sprite preview from the ship menu; no map
  for system editing. **ResEdit** is the alternative, and it just errors out for them.

The result is a working loop they describe with visible fatigue: change the
numbers, launch the game, check, change the numbers, check again. Something that
would take seconds with a map takes an evening without one.

**What we take from it.** The bottleneck was never the file format — it was the
*absence of resolution and preview*. Every ID is an unresolved pointer the human
has to dereference by memory. So the tooling we build in Phase 2 is judged on one
question: **does it let you write a mission without holding a single raw ID in your
head?** That means names not numbers, a map, sprite previews, and validation that
fails at author time instead of at play time. We are building the thing that
video wished existed.

---

## 2. What a mission actually is

A mission is one `mïsn` resource. The resource's **name** is the mission title the
player sees. Its fields fall into six groups. **[NOVA]** semantics:

### Availability — where and when it is offered
| Field | Meaning |
|---|---|
| `AvailStel` | Which stellar offers it. `-1` any inhabited; `128-2175` a specific stellar ID; banded ranges select by government (`9999-10255` a govt's stellars, `25000-25255` its enemies', etc.) |
| `AvailLoc` | `0` mission computer · `1` bar · `2` from a ship (needs a `përs`) · `3` spaceport · `4` trading · `5` shipyard · `6` outfitter |
| `AvailRecord` | Legal record threshold. Positive = at least this high, negative = at least this low. `-32000` = you have dominated that stellar |
| `AvailRating` | Combat rating floor; `-1` ignores it |
| `AvailRandom` | Percent of the time it is offered; recalculated on each warp in. `100` = always |
| `AvailBits` | **The chaining hook.** A boolean test expression; blank means true |

### Objective — where the player goes
`TravelStel` (the "go here" leg) and `ReturnStel` (the "come back here to get
paid" leg). Both accept a specific ID, `-1` for none, `-2`/`-3` for a random
inhabited/uninhabited stellar, and the same government bands. `ReturnStel = -4`
means *the stellar where the mission was accepted* — the single most useful value
for a simple round trip.

### Cargo
`CargoType`, `CargoQty` (negative = that magnitude ±50%), `PickupMode`,
`DropOffMode`, and `ScanMask` — which governments' scanners treat the load as
contraband. The Bible warns explicitly: do not set pickup and dropoff to the same
place, the game behaves strangely.

### Special ships
`ShipCount`, `ShipSyst`, `ShipDude` (which `dude` class supplies the ship types),
`ShipBehav`, `ShipNameID`, `ShipStart`, and the one that defines the mission's
verb — **`ShipGoal`**: `0` destroy · `1` disable · `2` board · `3` escort ·
`4` observe · `5` rescue · `6` chase off.

### Reward
`PayVal` in credits, or negative bands that clean your record with a government
instead of paying you, or take a percentage of your cash. `CompGovt` +
`CompReward` raise your standing. Note the asymmetry worth designing around: fail
a mission that has a `CompReward` and that government drops your record by *half*
that amount — the Bible's suggested use is missions some faction considers vital.

### Text — seven slots
`BriefText`, `QuickBrief`, `LoadCargText`, `DumpCargoText`, `CompText`,
`FailText`, `ShipDoneText`. Each holds a `dësc` resource ID, or `-1` for none.
Plus `RefuseText`, `AcceptButton`, `RefuseButton`.

---

## 3. Text references — how the words attach

Mission prose lives in **`dësc`** resources, not in the mission. The `mïsn` only
holds ID numbers. Reserved `dësc` ID ranges **[NOVA]**:

```
128-2175     stellar descriptions (shown on landing)
3000-3511    outfit descriptions
4000-4999    mission descriptions
13000-13767  ship class descriptions
14000-14767  hire-escort pilot descriptions
```

The Bible advises putting mission briefing descs at **5000 and up** to stay clear
of the reserved blocks. Ship names and subtitles come from `STR#` resources
instead (`ShipNameID`, `ShipSubtitle`).

Two mechanisms make this text dynamic, and both matter for us:

**Wildcards.** Nova substitutes at display time: `<DST>`/`<DSY>` destination
stellar and system, `<RST>`/`<RSY>` return stellar and system, `<CT>`/`<CQ>` cargo
type and quantity, `<DL>` deadline, `<PAY>` pay, `<PN>`/`<PNN>` player name and
nickname, `<PSN>`/`<PST>` ship name and type, `<PRK>`/`<SRK>` rank. This is why a
briefing can be written once and reused for a randomized destination.

**Bit-conditional text.** A `dësc` can branch inline on a control bit using
`{bXXX "text if set" "text if clear"}` — optionally negated with `!`. No compound
tests; one bit per substitution. The Bible's own illustration is a sentence whose
adjective flips depending on whether bit 1 is set. For us this is how a single
briefing acknowledges what the player did three missions ago.

---

## 4. Chaining — the actual mechanism

This is the part worth internalizing, because it is the whole architecture of a
campaign. **[NOVA]**

Missions do not link to each other. There are no "next mission" pointers. Instead
there is one global array of **control bits** — `b0` through `b9999` — saved in
the pilot file. Missions *read* bits to decide whether to appear, and *write* bits
when something happens to them. The chain is emergent.

**Test expressions** (`AvailBits`) support `Bxxx` bit lookup, `Oxxx` player owns
outfit, `Exxx` player has explored system, `G` gender, `Pxxx` registration, with
`&` `|` `!` and parentheses. The Bible warns the evaluator is primitive —
**always parenthesize**, never rely on operator precedence. A blank test is *true*.

**Set expressions** (`OnAccept`, `OnRefuse`, `OnSuccess`, `OnFailure`, `OnAbort`,
`OnShipDone`) are a bare list: `b1` sets, `!b3` clears, `^b4` toggles. No
parentheses. And `R(<op1> <op2>)` picks one of two operations *at random*, which
is how you build a string that branches unpredictably. `Axxx` aborts active
mission `xxx`.

So a three-mission chain is:

```
Mission A   AvailBits: (blank — always offered)
            OnSuccess: b100

Mission B   AvailBits: b100 & !b101
            OnSuccess: b101
            OnFailure: b199          ← the failure branch is just another bit

Mission C   AvailBits: b101
            OnSuccess: b102 R(b150 b151)   ← randomly forks the ending
```

**Consequences for our tooling.** The bit array is a global namespace with no
built-in documentation. A campaign is only comprehensible if the bits are named.
Therefore `evutils` must carry a **bit registry** — a project-level file mapping
each bit to a name, a description, the missions that set it, and the missions that
test it — and must be able to render the chain as a graph. Unreferenced bits, bits
tested but never set (a dead mission), and bits set but never tested (a no-op) are
all lint errors we can catch statically. That is the single highest-value thing we
can build, and no 1990s editor had it.

---

## 5. The authoring flow

```
 1. INTENT        One sentence. "Run lithium pellets to a station under blockade."

 2. WORLD         Which systems and stellars? Resolve by NAME.
                  If the target does not exist yet, author the spöb/sÿst FIRST.
                  → unknown IDs are the blocking problem; see §7

 3. BITS          Reserve bit numbers in the registry before writing fields.
                  Declare: what must be true to offer this (AvailBits),
                  what becomes true on each outcome (On* set expressions).

 4. SHAPE         Pick the verb: cargo run, or ShipGoal 0-6, or both.
                  Fill availability, objective, cargo, ships, reward.

 5. TEXT          Write the dësc resources. Allocate IDs 5000+.
                  Use wildcards so randomized destinations read correctly.
                  Use {bXXX "..." "..."} to acknowledge prior chain state.

 6. WIRE          Point the seven text fields at those desc IDs.

 7. VALIDATE      Static checks, before the game ever runs:
                  · every referenced ID exists (desc, STR#, dude, spöb, syst)
                  · every tested bit is set by something reachable
                  · every set bit is tested by something
                  · pickup mode != dropoff location
                  · reward and CompGovt are consistent
                  · the chain graph has no orphan nodes

 8. BUILD         evutils build → resource fork → drop into the plugin

 9. PLAY          The check the video's author had to do for everything.
                  We want it to be the last step, not every other step.
```

Steps 1-7 must be possible without launching the game. That is the whole design goal.

---

## 6. TMPL, ResEdit, and getting at the bytes

A ResEdit **`TMPL`** resource is a template that tells ResEdit how to display an
arbitrary resource type as labelled fields instead of raw hex. It is a list of
`(label, type-code)` pairs read in order against the resource's bytes. The common
type codes:

| Code | Meaning |
|---|---|
| `DBYT` `DWRD` `DLNG` | signed 8 / 16 / 32-bit integer |
| `UBYT` `UWRD` `ULNG` | unsigned 8 / 16 / 32-bit |
| `HBYT` `HWRD` `HLNG` | same widths, displayed as hex (use for flag fields) |
| `PSTR` | Pascal string, length-prefixed |
| `Cnnn` | fixed-length C string of `nnn` bytes |
| `OCNT`/`LSTC`…`LSTE` | counted list, for repeating groups |
| `AWRD` `ALNG` | align to 2 / 4-byte boundary |

Two facts that govern everything: classic Mac resources are **big-endian**, and
these structs are **fixed-layout with no padding beyond explicit alignment** —
field order *is* the byte order. So a correct TMPL and a correct parser are the
same document expressed twice.

Our approach: keep **one** machine-readable struct spec per resource type in
`specs/`, and generate both sides from it —

```
specs/misn.yaml ──┬──> evutils parser/serializer  (Python)
                  └──> TMPL resource               (for ResEdit, if it runs)
```

A first draft lives at `specs/misn.yaml`. It is **[VERIFY]** throughout: the field
*order* is taken from the Bible's presentation order, which is not guaranteed to
be the on-disk order, and classic EV's field set differs from Nova's. The
verification procedure is mechanical and must be done before the spec is trusted:

1. Extract one known `mïsn` from ConEx as raw bytes.
2. Read its values in-game or in EV Edit.
3. Locate those values in the hex by their known magnitudes (stellar IDs land in
   128-2175, `AvailRandom` in 1-100, `-1` shows as `FF FF`).
4. Lock each offset, then check the spec against *every* mission in the file —
   the total resource length must come out exact.

A spec that parses all 35 ConEx missions to sane values, re-serializes them
byte-identically, and produces the right length is a spec we can build on.

---

## 7. The unknown-ID problem

The Bible gives us ID *ranges* and their meanings, but not the contents of any
universe. When a ConEx mission says `TravelStel: 412`, nothing on disk tells us
what 412 is called or where it sits — that lives in the `spöb` and `sÿst`
resources of the data file the plugin was written against.

For missions referring to stellars and systems we hold no record of, we must build
the map first: extract `spöb` (stellar objects — the planets, their names, their
government, which system they belong to) and `sÿst` (star systems — names,
coordinates, hyperspace links) from the base EV scenario *and* from ConEx's own
additions, then join them into a single resolvable gazetteer. Only then does
`TravelStel: 412` become *"Exeon, in the Cenron system"*, and only then can a
mission be read by a human or drawn on a map.

This is tracked as **Phase 1.5** in `backlog.md` and it blocks the mission work.
