# yodaed — the reproducible mission editor

The editor from [docs/mission-editor-plan.md](../docs/mission-editor-plan.md):
plain-text mission source in git, the resource fork as a build artifact, and
an open-questions queue that names every unresolved reference. Stdlib-only,
like the rest of the repo.

## Surfaces (in the plan's build order)

    python3 -m yodaed check campaign        # 1. the question queue
    python3 -m yodaed graph campaign        # 4. the chain as Mermaid
    python3 -m yodaed bits campaign --write # regenerate bits.yaml cross-refs

`check` exits nonzero when anything blocks a build, so it gates CI and
`make check`. Not yet built: `new` (scaffolding), `build` (ids.lock
allocation → resource fork, round-trip verified), and the web editor.

## What check knows

- **Referential** — stellar/system names against `data/gazetteer.yaml`,
  governments against the gazetteer's govt fields, düde names against the
  1997 plugin's own extracted resources, prose files on disk.
- **Semantic** — the EV Bible's Override rules (`specs/misn-evo.yaml`):
  one set-gate + one clear-gate max, AvailRandom 1-100, cargo never picked
  up and dropped off at the same place, ship goals need ships, a record
  change needs a government, per-hook bit capacity (2/2/1/1), wildcard
  vocabulary in prose.
- **Chain integrity** — over named bits: gates never set (blocking, unless
  the bit is `external: true` — owned by the 1997 chain), dead-end bits,
  missions unreachable from a game start (fixpoint over the chain graph),
  the 256-bit ceiling.

## Layout

    yamlite.py    strict YAML subset loader (the repo has no PyYAML, on purpose)
    campaign.py   campaign tree + world (gazetteer, dudes) loading
    check.py      the question queue
    graph.py      Mermaid chain renderer
    bits.py       bits.yaml cross-ref generator
    tests/        the suite; wired into `make test`
