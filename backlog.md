# Yodacon — Plan & Backlog

The Yodacon lost a middle-school naming vote in an Alaskan portable classroom and
became a 3D-rendered starship anyway. This backlog is how the ship gets flown again.

**Outcome we are steering toward:** a repaired, documented ConEx plugin that
[systemless.org](https://systemless.org/escape-velocity-override/) can host on its
emulator page, plus *Team Yodacon* — a commodity-trading game whose landing
sequence is real reentry physics.

---

## Phase 0 — Ground station (done / near done)

- [x] `index.html` — EV splash-screen homepage: chrome rails, checkered green CRT
      panels, plasma-shifting spheres, center pilot-file readout driven by panel hover.
- [x] Organization lore written into the page.
- [x] MIT `LICENSE`, `README.md`, git repo initialized.
- [x] Publish to a remote — pushed to `yodacon/yodacon`; the game is its own repo
      `yodacon/gonex`, vendored back here as the `gonex/` submodule, with the root
      `Makefile` as the center that compiles it all. (yodacon.org DNS still pending.)

## Phase 1 — Crack the archive

Source: `vendor/paulricheson/release/ConEx 1.2.sit` and `vendor/paulricheson/release/792_ConEx12.sit.hqx`
(mirrored from the [Cythera Guides EV archive](http://www.cytheraguides.com/archives/ambrosia_addons/ev/)).

**Status 2026-08-27: DONE.** Full write-up:
[docs/lab-reports/2026-08-27-conex-resource-extraction.md](docs/lab-reports/2026-08-27-conex-resource-extraction.md);
dates & hashes in `vendor/paulricheson/PROVENANCE.md`.

- [x] Get a StuffIt/BinHex extractor working — `brew install unar` handled the
      StuffIt 5 "Arsenic" archive directly; the `.hqx` path was never needed.
      (`unar -k visible` emits AppleDouble `.rsrc` files.)
- [x] Split the resource fork into individual files under `vendor/paulricheson/extracted/` —
      `vendor/paulricheson/tools/rsrc_extract.py`: 538 resources / 26 types from the plugin, 220 more
      from the DOCMaker readme.
- [x] ~~Decode `rlë8`/`rlëD`~~ ConEx is classic EV, so sprites are `spïn`+`PICT`
      pairs, not Nova `rlë8`. Wrote a QuickDraw PICT v2 decoder instead
      (`vendor/paulricheson/tools/pict_decode.py`): 92/92 plugin PICTs → PNG, 11 sprite sheets
      composited with mask transparency. (`rlë8` still matters for Nova plugins —
      keep for evutils.)
- [x] Recover the **Yodacon ship**: `shïp` 174 stats (via the plugin's own TMPLs),
      `spïn` 174 → 70×70×36 sprite bank (PICT 20617/20618), target/yard/comm PICTs,
      dësc 2146 — and it is **playable again** as ship 13 ("Yodacon '97") in
      `~/code/Gonex`, the new Go port of konex.
- [x] Commit `vendor/paulricheson/extracted/` as the readable, diffable, version-controlled form of ConEx.

## Phase 1.4 — The EV Bible (done)

- [x] Found `vendor/EV Bible.app` — a PPC-era Mac app that is really a text
      document. It does not need to run: topics are plain RTF inside the bundle.
- [x] `tools/extract-ev-bible.sh` converts it to UTF-8 text, no PowerPC needed.
- [x] Vendored the result at `vendor/ev-bible-extracted/` — per-topic files plus
      one combined file per edition (**EVO** 22 topics, **EVN** 30 topics).
- [x] EVO (Override) is classic EV's direct descendant and therefore the correct
      reference for ConEx; `specs/misn-evo.yaml` written from it.
- [ ] Mine the remaining EVO topics (`Spob`, `Syst`, `Govt`, `Desc`, `STR#`) for
      the Phase 1.5 gazetteer field layouts.

## Phase 1.5 — The gazetteer (BLOCKING: populate the map)

ConEx missions reference stellars and systems by bare ID (`TravelStel: 412`) and we
hold **no record of what those IDs are**. Until this is populated, mission data is
unreadable, no map can be drawn, and the editor cannot resolve a single name.
This blocks Phase 4 of the editor and all mission work.

**Status 2026-08-27: DONE.** Base scenario: Escape Velocity 1.0.4 (Macintosh
Garden; hash in `vendor/paulricheson/PROVENANCE.md`, scenario data local-only in
`vendor/expanded/`, never committed). Generator: `data/build_gazetteer.py`.

- [x] Extract `spob` from the base EV scenario data file — `EV Data` parses with
      evutils, unencrypted, 107 spöb with the same TMPLs ConEx carries.
- [x] Extract `syst` — 108 base systems with coords, links, govt, nav lists.
- [x] Extract ConEx's own `spob`/`syst` additions and overrides — 10 spöb + 14 sÿst,
      including **ConEx station** (which overrides the planet *Levo* — base sÿst 128
      IS Levo, so the plugin renames home), **Exeon**, and **Cenron**.
- [x] Join base + plugin into one gazetteer — 109 systems, 109 stellars, with
      `source: base | conex | conex-override` and `replaces:` on overrides.
- [x] Reverse-resolve every ID referenced by ConEx's 36 missions — **all resolve**;
      the -4/-6/10000 values are documented EV special codes (per the Phase 1.4 EV
      Bible), annotated inline. Three referential bugs found, all on Exeon
      (self-link, dangling spöb 237, invalid Nav 0) → `findings:` section.
- [x] Published as `data/gazetteer.yaml`, committed and diffable.
- [x] Universe map rendered as `data/universe-map.svg` (`data/build_map.py`) —
      Phase 6 tokens, ConEx territory in accent over the phosphor base galaxy.

## Phase 2 — evutils (EV, not Nova)

[`vasi/evnova-utils`](https://github.com/vasi/evnova-utils) does this job for EV Nova.
Classic EV's resources are close cousins — same shapes, smaller structs.

**Status 2026-08-27: DONE.** Lives in `evutils/` (see its README). Both forks from
`ConEx 1.2.sit` verify: `python3 -m evutils verify …` → SHA-256 identical.

- [x] ~~Port~~ classic EV field layouts come from the plugin's **own ResEdit TMPLs**
      (`evutils/tmpl.py`) — ConEx carries a template named for every EV type it uses,
      so the 1997 file documents its own structs. No Nova porting needed.
- [x] `evutils dump` — resource fork → JSON tree (345 of 538 ConEx resources decode
      to labeled JSON; PICT/snd/icons stay `.bin`).
- [x] `evutils build` — JSON tree → resource fork; every JSON dump is written only
      after proving it re-encodes byte-identically, so unedited round-trips are
      exact by construction (including the Resource Manager's on-disk memory garbage —
      see `evutils/README.md`).
- [x] Round-trip test on unmodified ConEx 1.2 as the CI gate —
      `evutils/tests/test_roundtrip.py`, wired into `.github/workflows/ci.yml` for
      when the repo is published.

## Phase 2.5 — `yodaed`, the reproducible mission editor

Full plan: [`docs/mission-editor-plan.md`](docs/mission-editor-plan.md).
Design premise: plain-text source in git, resource fork as build artifact, and an
**open-questions queue** that names every unresolved reference and tells you what
you still need to create.

**Status 2026-08-28: check/graph/bits SHIPPED** — `yodaed/` (stdlib-only,
tests in `make test`) over the new `campaign/` source tree, which carries the
pellet-run starter chain (3 missions, prose in `campaign/texts/`). `make check`
runs the queue.

- [x] `yodaed check` — the question queue. Highest value; ship first.
- [x] YAML mission source format; prose in separate markdown files.
- [ ] `ids.lock` deterministic name -> ID allocator; bindings never change once
      made. (File and range notes exist; `yodaed build` will do the allocating.)
- [x] `bits.yaml` control-bit registry with generated `set_by` / `tested_by`
      (`yodaed bits --write`; `external: true` marks bits the 1997 chain owns).
- [x] Validation: referential (gazetteer + extracted düde names), semantic
      (EV Bible rules), chain-integrity (never-set gates, dead ends,
      reachability, 256-bit ceiling), text (wildcard vocabulary).
      Round-trip validation lands with `build`.
- [x] `yodaed new <type>` scaffolding — `new mission <slug>` writes an
      annotated mission source plus its brief stub; `new text <relpath>`
      answers a missing-prose question directly.
- [ ] `yodaed build` -> resource fork, round-trip verified byte-identical.
- [x] `yodaed graph` -> mission chain as Mermaid.
- [ ] Web editor in the site's HUD styling: question queue, map view, sprite
      previews, live validation — the editor the linked video wished existed.

## Phase 3 — Fix up ConEx

- [x] Catalogue the known 1.1→1.2 fixes from the updater (`ConEx12u`) and diff against 1.2 —
      [docs/lab-reports/2026-08-27-conex-11-to-12-patch-catalogue.md](docs/lab-reports/2026-08-27-conex-11-to-12-patch-catalogue.md):
      15 changes recovered from the ResCompare patch directory, all consistent with
      shipped 1.2. Leads for the play-through: Exeon's self-referencing hyperspace
      link, and the shipped "Sorry about the bug" landing-bug workaround string.
- [ ] Play through the 35 linked missions; log every broken bit, dead spöb, and
      bad mission-bit chain.
- [ ] Repair with `evutils`; keep every change as a reviewable commit.
- [ ] Verify under [EV Nova CE](https://github.com/andrews05/EV-Nova-CE/releases) and
      the emulator path from [escape-velocity.games/tools](https://download.escape-velocity.games/vendor/paulricheson/tools/).
- [ ] Package `ConEx 1.3 (Yodacon Restoration)` with a changelog crediting Paul Richeson.
- [ ] Contact systemless.org and offer the fixed plugin for hosting.

## Phase 4 — Team Yodacon: the reentry landing

Prototype lives at `vendor/docs/reentry-console.html`
(*MHD Reentry Console — Steerable Plasma Shield Envelope Model*).

**Status 2026-08-27: core DONE, in `~/code/Gonex`.** Design dossier: the
*Yodacon Flight Manual* artifact (quest graphs, corridor, gauges, controls,
damage economy). Game data flows from here via `data/export_gonex.py`
(gazetteer + 36 missions with 1997 briefs → `Gonex/assets/data/conex/`).

- [x] Physics core extracted into `Gonex/internal/reentry` with a headless test
      suite as the corridor gate: nominal autoland lands clean, dives burn,
      floats trip the skip meter, same seed → same flight.
- [x] Pellet system modeled: lithium feed rate `[ ]`, coil boost `B`, envelope
      rotation `← →`, angle of attack `↑ ↓`, emergency pellet burst `Space` —
      Saha-seeded conductivity driving magnetopause standoff and steering grip.
- [x] Landing loop: super-circular interface, corridor needle vs. narrowing band,
      too steep burns (q̇²- and g²-scaled damage), too shallow skips out (fuel and
      a day lost); lithium and damage carry between flight and entries.
- [x] HUD: gauge cluster (needle, crossrange, q̇/g, grip, Li, power, hull, AUTO
      lamp) + the volumetric plasma pillow in the three emission-line colors with
      the one-way-mirror shell arc. Splash-token restyle still open for Phase 6.
- [x] Failure states cost the ship: hull to zero in the plasma ends the voyage;
      over-g rolls damage the flight computer and cargo clamps (spoiled missions).
- [ ] Escort/combat mission objectives during the flight phase (academy dudes
      spawning in-system) — currently auto-resolved on arrival.

## Phase 4.5 — One pilot, one ship: flight-mode unification

The corridor is one game and the vacuum is still another — konex's 1997
deathmatch stitched to the reentry-trader. Full plan with file-level
grounding: [`gonex/docs/ROADMAP.md`](gonex/docs/ROADMAP.md). Milestones:

- [ ] **A — One Pilot:** merge the two player models (Voyage vs world
      Ship), courier HUD replacing the deathmatch scoreboard, nav-target
      cycling with the IFF color language on every bracket and map dot.
- [ ] **B — Someone Out There:** per-system traffic from govt data,
      mission ships actually spawned (ShipCount/ShipDude/ShipGoal),
      disposition (hostile/wary/neutral/friendly) from govt relations +
      the player's legal record, scan events, flight death that costs.
- [ ] **C — The Instruments:** minimap layers and a real system map,
      govt/fuel/known-space shading on the jump chart, approach assist.
- [ ] **D — The Yard:** outfit families feeding both the flight model
      and entryVehicleFor, turrets, escort orders.

## Phase 5 — Station life

- [ ] Dock, refuel, repair.
- [ ] Outfitters + ship dealer (dream about the upgrade you can't afford yet).
- [ ] The bar: rumors, mission offers, distraction while queuing for mini-games.
- [ ] Mini-games leveling **charisma** — including a Royal Finkel table.
- [ ] Commodity trading economy across systems.
- [ ] Implement the **winners process** as specified in `vendor/docs/Nova Bible.txt`.

## Phase 6 — Style system

The whole site and game share one look, taken from the EV splash and in-flight HUD:

| Token | Value | Use |
|---|---|---|
| void | `#05070a` | space background + starfield |
| crt / crt-lit | `#0d3d12` / `#1d7a24` | panel rest / hover |
| phosphor | `#5cff5c` | all text |
| chrome | `#dfe4e6` → `#4c5457` | bezels, rails, rounded readout frame |
| accent | `#c26bd8` | telemetry numerals, pull-quotes |

- [ ] Extract the CSS into `assets/hud.css` once a second page exists.
- [ ] Reusable components: `.panel` (glass HUD button), `.orb` (plasma sphere),
      `.readout-wrap` (chrome-bezel CRT), `.status` (right-side flight HUD).
- [ ] Real bitmap font instead of Courier fallback.
- [ ] Ship the extracted ConEx sprites as page art once Phase 1 lands.

---

## Phase 6 — The resource cycle and the Governor's Desk (4 Sep 2026)

- [x] Zero-sum in credits as well as tons: `econ.Ledger`, every payment a
      `Pay`, the player's stake out of the home treasury.
- [x] Hull, Rounds, Missiles as tons; yards, arsenals, composters, breakers;
      civic gardens; growth made of rations.
- [x] Wreck cargo persists and is scooped nearest-hold-first; hull mass on
      the books.
- [x] Konquest's battle, garrison flip, standing orders, yards recommissioning
      lost hulls; the colour AI expands.
- [x] OpenFront's buildings on a shared ladder; the seat is the first
      building; the universe saves.
- [x] The Governor's Desk — `G` at any dock. Design: LR-2026-07.
- [x] Second round (evening): genesis infrastructure, tax-funded auto-governor
      with doctrines per colour, priority world, policy and focus, seed and
      tuning knobs, the in-sector wreck field (M3), the desk split into four
      tabs. Plan §12.
- [ ] Balance pass: capitals running out of rounds by day 120, deadheading on
      the full map, the famine curve. Then tag **v0.1a4**.

## Project documents

- [`docs/resource-cycle-plan.md`](docs/resource-cycle-plan.md) — tons and credits
  conserved, the water cycle, Konquest and OpenFront folded in; §11 is what shipped.
- [`docs/lab-reports/2026-09-04-governor-desk-screen.md`](docs/lab-reports/2026-09-04-governor-desk-screen.md) —
  LR-2026-07, the Governor's Desk.

- [`docs/mission-authoring.md`](docs/mission-authoring.md) — how a mission is built:
  `misn` fields, `desc`/`STR#` text references, control-bit chaining, TMPL/byte layout.
- [`docs/mission-editor-plan.md`](docs/mission-editor-plan.md) — plan for `yodaed`.
- [`specs/misn.yaml`](specs/misn.yaml) — mission struct spec (draft, unverified).

## Resources

- [Cythera Guides — Ambrosia EV add-ons](http://www.cytheraguides.com/archives/ambrosia_addons/ev/)
- [vasi/evnova-utils](https://github.com/vasi/evnova-utils)
- [andrews05/EV-Nova-CE releases](https://github.com/andrews05/EV-Nova-CE/releases)
- [escape-velocity.games tools](https://download.escape-velocity.games/vendor/paulricheson/tools/)
- [Nova Bible](https://download.escape-velocity.games/vendor/paulricheson/tools/EV%20Nova/Documentation/Nova%20Bible.txt) — also at `vendor/docs/Nova Bible.txt`
- [systemless.org — Escape Velocity Override](https://systemless.org/escape-velocity-override/)
- [r/evnova — Ambrosia and registration](https://www.reddit.com/r/evnova/comments/g3ie3x/ambrosia_and_registration/)
- [Building an EV Nova ship plugin (video)](https://www.youtube.com/watch?v=XTzUsw34FRw) — mirrored article in `vendor/docs/`

### ConEx archive listing (as published)

```
ConEx12.sit  (1.10 MB)  Plugins  Anonymous  1999/12/04  4.00  4 votes  3400 downloads
ConEx12u.sit (143.00 kB) Plugins Anonymous  1999/12/04  0.00  0 votes  1610 downloads
```
