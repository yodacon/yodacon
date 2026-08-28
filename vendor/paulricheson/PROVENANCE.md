# Provenance & Dates — ConEx 1.2 extraction

Every date the archive still carries, recorded before anything else touches it.
Extraction performed 2026-08-27 on macOS (Darwin 25.5.0).

## Source archives (as mirrored into `vendor/docs/`)

| File | SHA-256 | Format |
|---|---|---|
| `ConEx 1.2.sit` | `593d8c50e11cc3d405e06eb3736671afeba76c82527bbd13fd21748ca8032d58` | StuffIt 5, "Arsenic" arithmetic coder |
| `release/792_ConEx12.sit.hqx` | `ded5fc0c7d9412ae174bd28a690d683fef65a571b809731ab626a31589aa4627` | BinHex 4.0 wrapping the same .sit |

Mirrored 2026-08-27 from the Cythera Guides EV archive
(`cytheraguides.com/archives/ambrosia_addons/ev/`).

## The 1.1→1.2 updater (`release/ConEx12u.sit.hqx`)

| File | SHA-256 | Format |
|---|---|---|
| `release/ConEx12u.sit.hqx` | `733635f8be2db77e5c6d5c3c0ead8549ea5e3199d01fdfa19fcf7690c5982940` | BinHex 4.0 |
| `ConEx 1.2 Patches.sit` (inner) | `84d1f09a2ede7583bb7100105e37dce71f7e5e9f1c2273554d28e857ca8667e1` | StuffIt 5, Arsenic |

Recovered 2026-08-27 from the Internet Archive item
*EscapeVelocityPluginCollection* (`EV.zip` → `EV/Plugins/ConEx12u.sit.hqx`,
mirrored in full in `vendorignored/`), together with the 1999 download-site
description texts (`release/ConEx12.sit.txt`, `release/ConEx12u.sit.txt`).

Member timestamps inside the inner `.sit` (per `lsar -l`):

| Member | Archive date/time | Notes |
|---|---|---|
| `ConEx 1.2 Patches/` (folder) | 1997-11-28 20:55 | |
| `ConEx Readme 1.2 patch` (rsrc, 64,360 B) | 1997-11-28 20:18 | ResCompare 5.0 patch app, `APPL`/`ZAPS` |
| `ConEx1.2 patch` (rsrc, 165,980 B) | 1997-11-28 20:54 | ResCompare 5.0 patch app, `APPL`/`ZAPS` |

These extend the release-evening timeline below: plugin 20:05, readme 20:15,
readme patch 20:18, plugin patch 20:54, patch folder stuffed 20:55. The
patch contents are catalogued in
`docs/lab-reports/2026-08-27-conex-11-to-12-patch-catalogue.md`; every
post-patch resource size matches the shipped 1.2 plugin.

## Base game (for cross-reference, not part of the ConEx release)

| File | SHA-256 | Format |
|---|---|---|
| `Escape_Velocity_1.0.4.sit` | `e8ce310768b12ebbc937753663fa6ba383593ec04f4f5ee96999c00675c0fb86` | StuffIt, pre-installed game |

Downloaded 2026-08-27 from Macintosh Garden
(`macintoshgarden.org/games/escape-velocity`, `old.mac.gdn` mirror), kept in
`vendorignored/` and expanded to `vendor/expanded/` — Ambrosia's scenario is
**not committed**; only factual cross-reference data derived from it
(system/stellar names, IDs, coordinates, links) is, in `data/gazetteer.yaml`.
Its `EV Data` file parses with `evutils`: 108 `sÿst`, 107 `spöb`, 116 `mïsn`,
644 `dësc`, unencrypted, with the same 17 `TMPL`s ConEx carries. Base
`sÿst` 128 is **Levo** — the system ConEx 1.2 overrides with the ConEx home
system, matching the mission-text fix in the 1.1→1.2 catalogue.

## Member timestamps inside the .sit (per `lsar -l`)

| Member | Archive date/time | Notes |
|---|---|---|
| `ConEx 1.2/` (folder) | 1997-11-28 20:13 | |
| `ConEx Readme 1.2` (rsrc, 398,146 B) | 1997-11-28 20:15 | Arsenic, 59.0% |
| `ConEx1.2` (rsrc, 1,522,938 B) | 1997-11-28 20:05 | Arsenic, 59.3% |
| `ConEx1.2` (data, 8 B) | 1997-11-28 20:05 | uncompressed |

## HFS timestamps preserved through extraction (per `stat`, on files in `vendor/expanded/`)

| File | Created (birth) | Modified |
|---|---|---|
| `ConEx1.2` + fork | **1997-11-09 15:32:18** | 1997-11-28 20:05:34 |
| `ConEx Readme 1.2` fork | 1997-11-28 20:13:43 | 1997-11-28 20:15:58 |

Reading: the plugin file was created Sunday 1997-11-09, worked on for ~19 days,
last saved 1997-11-28 (the Friday after Thanksgiving) at 20:05, the readme
finished eleven minutes later at 20:15(:58), and the archive was stuffed
immediately after — the whole release ritual fits inside one evening.

## Finder metadata

| File | Type | Creator | Meaning |
|---|---|---|---|
| `ConEx1.2` | `Mpïf` | `Mërc` | Escape Velocity plugin, opened by EV ("Mërc" = Matt Burch's creator code) |
| `ConEx Readme 1.2` | `APPL` | `Dk@P` | Self-displaying DOCMaker document application |

## Resource inventory (from `vendor/paulricheson/tools/rsrc_extract.py`)

- `ConEx1.2.rsrc`: **538 resources / 26 types** — 92 `PICT` (1,271,710 B), 191 `dësc`,
  36 `mïsn`, 31 `spïn`, 24 `shïp`, 14 `sÿst`, 10 `spöb`, 10 `oütf`, 17 `düde`,
  17 `TMPL`, 7 `STR#`, 50 `STR `, 6 `snd `, 5 `gövt`, 3 `wëap`, 2 `përs`,
  1 each `flët`/`öops`/`vers`, plus icon families.
- `ConEx Readme 1.2.rsrc`: 220 resources / 38 types — 14 `TEXT`+`styl` chapters,
  43 `PICT`, plus the DOCMaker viewer's own `CODE`/UI resources.

## Extraction toolchain

- `unar` 1.10.8_7 (Homebrew bottle), `-k visible` → AppleDouble `.rsrc` files
- `vendor/paulricheson/tools/rsrc_extract.py` — AppleDouble unwrap + resource-fork walk (Python 3.9.6)
- `vendor/paulricheson/tools/pict_decode.py` — QuickDraw PICT v2 subset → PNG (Pillow)
- `vendor/paulricheson/tools/convert_all.py` — batch PICT/spïn/text conversion
- `vendor/paulricheson/tools/tmpl_dump.py` — applies the plugin's own ResEdit `TMPL`s to its resources
