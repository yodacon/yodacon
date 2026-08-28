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
- [ ] Publish to a remote (GitHub `yodacon/yodacon`) and point yodacon.org at it.

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

## Phase 1.5 — The gazetteer (BLOCKING: populate the map)

ConEx missions reference stellars and systems by bare ID (`TravelStel: 412`) and we
hold **no record of what those IDs are**. Until this is populated, mission data is
unreadable, no map can be drawn, and the editor cannot resolve a single name.
This blocks Phase 4 of the editor and all mission work.

- [ ] Extract `spob` (stellar objects: name, government, parent system, desc ID)
      from the base EV scenario data file.
- [ ] Extract `syst` (star systems: name, x/y coordinates, hyperspace links,
      government, contained stellars).
- [ ] Extract ConEx's own `spob`/`syst` additions and overrides — including
      **Conex, Exeon, and Cenron**, the three the 1999 release told players to land on.
- [ ] Join base + plugin into one gazetteer: `name <-> ID <-> system <-> coords <-> govt`.
      Plugin entries override base entries at the same ID.
- [ ] Reverse-resolve every ID referenced by ConEx's 35 missions. Report any ID
      that resolves to nothing — those are either our extraction bugs or genuine
      1999 bugs, and both are findings worth having.
- [ ] Publish as `data/gazetteer.yaml`, committed and diffable.
- [ ] Render the universe map (systems + hyperlinks) as SVG in the site HUD styling.

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

- [ ] `yodaed check` — the question queue. Highest value; ship first.
- [ ] YAML mission source format; prose in separate markdown files.
- [ ] `ids.lock` deterministic name -> ID allocator; bindings never change once made.
- [ ] `bits.yaml` control-bit registry with generated `set_by` / `tested_by`.
- [ ] Validation: referential, semantic, chain-integrity, text, round-trip.
- [ ] `yodaed new <type>` scaffolding from question context.
- [ ] `yodaed build` -> resource fork, round-trip verified byte-identical.
- [ ] `yodaed graph` -> mission chain as Mermaid/Graphviz.
- [ ] Web editor in the site's HUD styling: question queue, map view, sprite
      previews, live validation — the editor the linked video wished existed.

## Phase 3 — Fix up ConEx

- [ ] Catalogue the known 1.1→1.2 fixes from the updater (`ConEx12u`) and diff against 1.2.
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

- [ ] Extract the physics core (heat flux, ballistic coefficient, corridor limits)
      into a standalone module with tests.
- [ ] Model the pellet system: lithium-injected pellets cooked by lasers and X-ray
      emitters, producing the rotating glide pillow. Player controls = injection rate,
      emitter power, envelope rotation, angle of attack.
- [ ] Landing loop: reentry corridor → too steep burns you, too shallow skips you out.
      Fuel and shield state carry in from flight.
- [ ] Wire the HUD from the splash styling — shield/fuel meters, nav, target, credits.
- [ ] Failure states that cost the ship, not just the mission.

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

## Project documents

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
