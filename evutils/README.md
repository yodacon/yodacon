# evutils

Dump a classic *Escape Velocity* plugin's resource fork to an editable tree of
JSON and binary files, and build it back — **byte-identically**. This is the
Phase 2 tool from `backlog.md`: no edit to ConEx is trusted until the unedited
round-trip reproduces the original fork exactly.

```sh
python3 -m evutils dump  "vendor/expanded/ConEx 1.2/ConEx1.2.rsrc" work/conex
python3 -m evutils build work/conex work/ConEx1.3.rsrc
python3 -m evutils verify "vendor/expanded/ConEx 1.2/ConEx1.2.rsrc"
```

Input may be a raw resource fork or an AppleDouble container (what
`unar -k visible` writes). Output of `build` is a raw fork.

## What a dump looks like

- `manifest.json` — fork-level structure: type order, per-resource id / name /
  attributes, and the preserved byte ranges described below.
- `<type>/<id>_<name>.json` — resources whose type has a ResEdit `TMPL` in the
  fork, decoded to labeled fields. ConEx documents its own binary formats: it
  carries a TMPL named for each EV game type (`shïp`, `mïsn`, `sÿst`, …), so
  ship stats, missions, systems, and descriptions all dump as JSON.
- `<type>/<id>_<name>.bin` — everything else (`PICT`, `snd `, icons), plus any
  resource whose TMPL decode fails to re-encode identically (none in ConEx 1.2).

A JSON dump is only ever written after proving it re-encodes to the original
bytes, so a dump followed by an unedited build is exact by construction.

## Why byte-identity needs care

The 1997 Resource Manager wrote live memory garbage to disk: 45 nonzero bytes
in the "reserved" gap after the header, a stale in-memory header copy and
handle fields in the map, per-resource attribute bytes, and 4 reserved bytes
per reference entry. Data blocks and names are also stored in insertion order,
not ref-list order. `evutils` preserves all of it (`reserved`, `map_header`,
`handle`, `data_order`, `name_order` in the manifest), which is what lets the
round-trip gate assert SHA-256 equality with the fork Paul Richeson saved on
1997-11-28.

## Tests

```sh
python3 -m unittest discover -s evutils/tests
```

The suite round-trips both forks from `ConEx 1.2.sit` (plugin and DOCMaker
readme), using `vendor/expanded/` when present or expanding the committed
`.sit` with `unar`. CI runs the same suite (`.github/workflows/ci.yml`).
