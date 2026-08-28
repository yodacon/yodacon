# Plan: A Reproducible Mission Editor

**Working name:** `yodaed`

The editor exists to fix the specific failure documented on the homepage video:
authoring by holding raw resource IDs in your head, then verifying by launching
the game. Two design commitments follow from that, and everything else is
downstream of them.

> **1. Reproducible.** The source of truth is plain text in git. The `.rez`
> resource fork is a *build artifact*, never the thing you edit. Same input,
> same bytes out, every time, on any machine.
>
> **2. It tells you what you still need to create.** Every unresolved reference
> becomes an explicit question with a place to put the answer. The editor is not
> a form you fill in — it is a checklist that grows as you work and shrinks as
> you answer it.

---

## 1. The core idea: the open-questions queue

Authoring a mission generates references to things that may not exist yet. A
destination planet. A briefing text. A ship class for the ambush. A control bit
nobody has defined. Traditional editors let you type `412` into a field and find
out three weeks later that stellar 412 was never created.

`yodaed` treats every dangling reference as a **question** on a queue. The queue
is the primary interface. You never see a raw ID unless you ask for one.

```
$ yodaed check missions/pellet-run.yaml

  MISSION  Lithium Run to Exeon                            [4 open questions]

  ? travel_stellar: "Exeon"  — no stellar by that name
      → yodaed new stellar "Exeon" --system=<?>          [blocks: build]
  ? on_success sets bit "blockade_broken" — never tested by any mission
      → dead end. Intended follow-up mission not written? [warn]
  ? brief_text — not written
      → yodaed new text brief --mission=pellet-run        [blocks: build]
  ? ship_dude: "Militia Patrol" — no dude by that name
      → yodaed new dude "Militia Patrol" --ships=<?>      [blocks: build]

  2 warnings, 3 blocking. Not buildable.
```

Answering one question often reveals the next — creating the stellar `Exeon`
immediately asks which system holds it, and if that system does not exist, asks
for its coordinates and hyperlinks. The queue is a work-breakdown structure that
derives itself. **This is the feature.** Everything else is plumbing.

---

## 2. Source format

One YAML file per mission. Names throughout; IDs never typed by a human.

```yaml
mission: Lithium Run to Exeon
available:
  at: Conex                    # resolved against the gazetteer
  from: bar
  when:                        # named bits, not numbers
    set:   pellet_contract_signed
    clear: blockade_broken     # Override allows exactly one of each
  chance: 60
objective:
  travel_to: Exeon
  return_to: :accepted         # ReturnStel -4
cargo: {type: lithium_pellets, qty: 40, pickup: at_start, dropoff: at_travel}
ships:
  count: 3
  dude: Militia Patrol
  goal: chase_off
  system: :travel              # ShipSyst -3
reward: {credits: 25000, govt: Consolidated Express, record: 5}
text:
  brief: texts/pellet-run/brief.md
  complete: texts/pellet-run/complete.md
  fail: texts/pellet-run/fail.md
on:
  accept:  set blockade_run_begun     # StartBitSet
  success: set blockade_broken        # CompBitSet  (+ CompBitSet2 available)
  failure: set pellet_contract_burned # FailBitSet  (+ FailBitSet2 available)
  refuse:  set militia_suspicious     # RefuseBitSet
```

Mission prose lives in its own markdown files, so it is diffable, spell-checkable,
and reviewable as writing rather than as a field in a binary. Wildcards
(`<DST>`, `<PAY>`, …) and bit-conditional spans pass through and are *validated* —
an unknown wildcard or a conditional on an undefined bit is a build error.

---

## 3. Named IDs and the allocator

Humans write names. The build assigns numbers, deterministically.

- A lockfile, `ids.lock`, records every name → ID binding, committed to git.
- Once allocated, a binding **never changes** — pilot files in the wild store bits
  and mission IDs by number, so churn breaks saved games.
- New names get the next free ID in the correct range for their type
  (descs at 5000+, stellars 128-2175, and so on).
- Allocation is a pure function of `ids.lock` plus the sorted set of new names,
  so two people building the same commit get identical bytes.

The same discipline applies to control bits. `bits.yaml` is the registry:

```yaml
blockade_broken:
  bit: 412
  doc: Player ran the Exeon blockade successfully.
  set_by: [pellet-run]
  tested_by: [exeon-aftermath, militia-reprisal]
```

`set_by` and `tested_by` are **generated**, not hand-maintained — which is exactly
what makes the "bit set but never tested" and "bit tested but never set" lints
possible. Those two lints catch the most common way a campaign silently breaks.

---

## 4. Validation — everything the game would have told you, before you launch

Static checks, all of them cheap, run on every save:

**Referential** — every named stellar, system, government, dude, ship, outfit,
STR#, and desc resolves. Every allocated ID stays inside its legal range.

**Semantic**, straight from the Bible's own warnings and field tables — cargo
pickup and dropoff are not the same place; `AvailRandom` is 1-100; `AvailLoc` 2
has a matching `përs`; `ShipGoal` set implies `ShipCount` > 0; a `CompReward`
without a `CompGovt` is meaningless; escort and rescue goals need ships that can
plausibly be escorted or rescued.

**Chain integrity** — build the directed graph of missions over bits. Report
unreachable missions, bits tested but never set, bits set but never tested, cycles
that can deadlock a player, and any mission with no path from a game start.

**Text** — unknown wildcards, conditionals on undefined bits, desc IDs outside the
safe range, unbalanced `{}` spans.

**Round-trip** — parse the built fork back and compare to source. Any mismatch is
a parser bug and fails the build.

---

## 5. What answers the "where is planet 412" question

The editor cannot resolve names without a map, and ConEx references stellars we
have no record of. So `yodaed` sits on a **gazetteer**: `spöb` and `sÿst` extracted
from the base EV scenario *and* ConEx's additions, joined into one table of
name → ID → system → coordinates → government.

This is why gazetteer extraction (backlog Phase 1.5) blocks the editor. Until it
exists, `TravelStel: 412` is an unreadable number and no map can be drawn.

Given it, we get the thing the video's author actually missed: a **map view**,
where you place a mission's legs by clicking systems rather than by typing IDs,
and where the editor can show you the hyperspace route the player will fly.

---

## 6. Build pipeline

```
missions/*.yaml  ┐
texts/**/*.md    ├─→ resolve names ─→ allocate IDs ─→ validate ─┬─→ FAIL: questions
bits.yaml        │      (gazetteer)     (ids.lock)              │
ids.lock         ┘                                              └─→ emit resources
                                                                       │
                                    specs/*.yaml ────────────────────→ │  (struct defs)
                                                                       ↓
                                                          build/ConEx-Yodacon.rez
                                                                       │
                                                    round-trip verify ─┘
```

`specs/*.yaml` drives serialization *and* generates the ResEdit `TMPL`, so the
byte layout is defined exactly once.

---

## 7. Surfaces, in build order

1. **`yodaed check`** — the question queue as CLI output. Delivers the core value
   on its own; everything after this is ergonomics.
2. **`yodaed new <type>`** — scaffolds the file that answers a question, with the
   known fields pre-filled from context.
3. **`yodaed build`** — emit the fork, round-trip verified.
4. **`yodaed graph`** — render the mission chain (Graphviz/Mermaid) so a campaign
   can be read at a glance.
5. **Web editor** — HUD-styled, matching `index.html`: question queue down one
   side, map in the center, live validation. This is where the map view and sprite
   previews land.

Order matters: 1-3 make the format trustworthy, and only a trustworthy format is
worth building a GUI on top of.

---

## 8. Open questions for us

Honest list of what is undecided, and what would settle each:

- ~~**Classic EV bit storage.**~~ **RESOLVED** by the EV Bible's Override edition
  (`vendor/ev-bible-extracted/EVO/`). Override uses **256 mission bits** and
  **single integer fields** (`-1` ignored, `0-511` set, `1000-1511` clear) — no
  expression strings, no boolean algebra. The source format's `when:` is
  therefore a `set:`/`clear:` pair, and `specs/misn-evo.yaml` is now the spec
  that governs ConEx.

- **Bit budget.** 256 bits is a hard ceiling and a real design constraint, since
  conditions that Nova expresses inline cost extra bits under Override. The editor
  must track allocation against the ceiling. *Open:* do we reserve numbered
  ranges per campaign, or allocate freely and lint for collisions?

- **Conditions that will not compile.** An author can write a condition Override
  cannot express in one `AvailBitSet` + one `AvailBitClr`. *Open:* reject it, or
  auto-synthesize helper bits? *Leaning:* reject with a clear message first —
  silent synthesis spends a scarce resource behind the author's back.
- **Does `mïsn` field order match the Bible's presentation order?** *Settled by:*
  the offset-locking procedure in `mission-authoring.md` §6.
- **Do we target classic EV, EV Nova CE, or both?** Sharing missions across both
  means a lowest-common-denominator source format. *Settled by:* deciding who we
  want to be able to play it — which is a project question, not a technical one.
- **Fork or sidecar for output?** A real resource fork is authentic but fragile on
  modern filesystems and in git. `.rez`/AppleDouble sidecar is portable.
  *Leaning:* build the sidecar, and provide a separate step to install as a fork.
