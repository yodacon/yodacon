# ConEx → konex → Gonex: One Game, Three Substrates, Twenty-Nine Years

**Yodacon Project Lab Report LR-2026-05** · docs/lab-reports · 2026-08-28
**P. Richeson** (Yodacon project) with Claude (Anthropic) as reading and analysis tooling

---

**Abstract** — We compare the three generations of the same small space
game: *ConEx 1.2* (1997, an Escape Velocity plugin — 538 resources in a
Macintosh resource fork), *konex* (2005, Joshua Bussdieker's standalone
C++/OpenGL remake, ~8,100 lines), and *Gonex* (2026, the Go/Ebitengine
port that became the reentry-trader). Reading all three side by side shows
a clean division of inheritance: **konex kept ConEx's cast and dropped its
game; Gonex kept konex's engine and restored ConEx's game** — then added
the layer neither ancestor had, a player-versus-environment economy in
which the scoring mechanic is the landing itself. We document the concrete
carriers of the lineage (names, art, constants, data files, and the 1997
in-fiction flight academy), and close with the design theory of the 2026
layer: arcade-score high/low risk decisions relocated from combat to
atmospheric entry and heat management.

**Index Terms** — software lineage, game preservation, Escape Velocity,
resource fork, remake, port, risk-reward design, PvE progression.

---

## I. The three artifacts

**1 · ConEx (1997) is data, not a program.** The plugin contains no code;
it is 538 resources interpreted by *Escape Velocity*'s engine: 24 `shïp`,
31 `spïn` sprite banks, 36 `mïsn`, 14 `sÿst`, 10 `spöb`, 5 `gövt`, 10
`oütf`, 3 `wëap`, 191 `dësc` texts (LR-2026-01 catalogues the recovery).
Its original contribution is a cast — Small/Medium/Large Pin, Dart,
Defender, Gryphon, Trident, Necromancer, Tomaquad, and `shïp 174: Yodacon`
with its 70×70×36-frame rotation bank — laid over base EV's galaxy, plus
an EV-shaped *life*: missions on a 512-bit control machine, trading,
outfits, landing screens ("their backgrounds will amaze you").

**2 · konex (2005) is an engine wearing ConEx's clothes.** The C++ tree
does not merely resemble ConEx — it *identifies* as it: `defs.h` declares
`SYS_APPNAME "Conex"`, and the splash screen is `data/logos/conex.tga`.
Its twelve ship folders are the ConEx roster redrawn (`dart`, `defender`,
`gryphon`, `necromancer`, `trident`, `tomaquad`, the pins, `yodacon`…),
and `ships.cpp` loads each as EV loaded a `spïn`: `for (i = 0; i < 36;
i++)` — thirty-six frames, ten degrees each. But the structure around the
cast is gone. Entities live in one 400-slot array with a type tag
(`ENTITY_PLAYER … ENTITY_ITEM`) and a `used` flag; `planets.cpp` is a
stub; there are no missions, no galaxy, no cargo. The menu offers exactly
two lives: "Team Deathmatch" and "Sunday Drive". konex is ConEx's art
flying in an arena that forgot why the art existed.

**3 · Gonex (2026) is both at once.** Two inheritances, separately
verifiable in the source:

*From konex, the engine — nearly cell for cell.* Every Go package names
its konex ancestor (`docs/ARCHITECTURE.md`: `vector.h`→`gmath`,
`ships.cpp`→`ship`, `entity/player`→`world`, `ai.cpp`→`ai`,
`view.cpp`→`camera`, `console.cpp`→`console`, `konex.cpp`→`app`). The
*data files are konex's own*, embedded verbatim: the same per-ship
`specs.xml`, the same `deathmatch.xml` and `sundaydrive.xml` scenes, the
same `config.xml` format — and the same `conex.tga` splash, so all three
generations open on the same word. The constants were carried faithfully
and check out against the C++: the 64-unit collision range (`entity.cpp:
(entity->pos - entities[i].pos).Length() < 64.0f`), the 0.2 s fire
cooldown (`player.cpp: firettl = 0.2f`), the menu captions word for word
(`menu.cpp: "Team Deathmatch" / "Sunday Drive" / "Return to Main Menu"`).

*From ConEx, the game — restored after a 29-year gap.* Gonex is the first
program since Escape Velocity itself to execute ConEx's data:
`missions.json` is the 36 `mïsn` records running on the real EV bit
machine (GIVEN/SETS clauses, the −4 and 10000+n stellar codes, govt 128);
`galaxy.json` is the `sÿst`/`spöb` overlay with the recovered Con1–Con16
hyperlinks; the nine 1997 sprite banks are byte-decoded into the `*-97`
ship folders (`yodacon97` from PICT 20617 + mask 20618); the `spöb`
landing views hang behind the dock screen; the `spöb` records seed the
per-planet reentry profiles.

## II. The academy: a curriculum that survived three engines

The strongest single proof that this is one game and not three is the
mission chain. ConEx's `mïsn` 250–281 is an in-fiction flight school at
stellar 133 (ConEx), chained on control bits 121→152:

    250 Flight Practice          → 251 Start Freight Training
    252 Shipping 101/202         → 254 Trading 101/202
    256 Start Combat Training    → 258 Combat 101 … 281 Final Training 4

with a parallel lumber-transport arc (282–285, bits 160–162) that is,
recognizably, the ancestor of the 2026 commodity game. In 1997 the
curriculum taught EV's verbs: fly, jump, haul, fight. In 2026 the same
chain runs unmodified in Gonex's spaceport bar — and the project now
extends it with a branch the 1997 engine could not express: an *Approach
School* teaching the reentry corridor, heat management, and the
commodity-ship doctrine (see `gonex/docs/FLIGHT-SCHOOL.md`), forked from
bit 126 — after Trading 202, *instead of* Start Combat Training. That
fork point is the design thesis in one line.

## III. The theory of the 2026 layer: the score is the landing

konex's only economy was the deathmatch scoreboard. Gonex relocates the
arcade score into the environment, on three principles:

**1 · High/low risk as a per-landing wager.** Every descent is a
press-your-luck round with a legible pot. The *pad bonus* pays in full
inside 2 km of the line and halves inside 10; the corridor is a two-sided
trap (LR-2026-04) whose edges charge hull; staying supersonic below 10 km
buys time but triggers the sonic-boom fine, scaling with Mach². Lithium
feed, coil boosts, and RCS are a finite stack of chips: spend them to
smooth the ride, hoard them to bank the margin, and an empty tank on final
is a mushy stick precisely when the wager settles. The dial cluster is the
odds board — every needle is a live price on risk.

**2 · Heat as the reward mechanic, not the obstacle.** Following the
reentry console's argument (LR-2026-04: "you do not fight that river, you
steer it"), heat is the currency the atmosphere charges for arriving.
Repairs, spoiled cargo (clamps), degraded flight computers, and the
guardian dumping seed reserves are all denominated in it. Advancement —
richer contracts, heavier outfits, bigger hulls — raises the ballistic
coefficient and therefore the entry price, so the progression system and
the difficulty curve are the same number read twice.

**3 · Rags to riches, player versus environment.** The trader campaign
starts on margin (8,000 cr) in an armed world, but the opponent that
matters is atmospheric physics; combat is weather you route around (the
chart is the way out of a fight, not the guns). The ship procession *is*
the story arc: courier → pins → hauler → escort wing → the 350-tonne
Yodacon, each hull's `specs.xml` numbers (velocity, turn, acceleration,
mass) mapping to the cargo class it serves and the entry it must survive.
Death is DED, and DED resumes from the last berth save: the world is open,
the run is roguelike, the ledger is the score.

## IV. Conclusion

The similarity between ConEx, konex, and Gonex is not stylistic; it is
material. The same name (Con→kon→gon), the same splash bitmap, the same
36-frame sprite convention, the same roster, the same constants, the same
scene files, and — uniquely in Gonex — the same 1997 mission bits ticking
over again. Each generation preserved the identity and changed the
substrate; the third reunited what the second had split, and then finished
the sentence the 1997 lumber arc started: a commodity-trading game whose
landing sequence is real reentry physics, where the risk you manage on the
way down is the score you keep on the ground.
