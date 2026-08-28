# Provenance & Dates — ConEx 1.2 extraction

Every date the archive still carries, recorded before anything else touches it.
Extraction performed 2026-08-27 on macOS (Darwin 25.5.0).

## Source archives (as mirrored into `vendor/docs/`)

| File | SHA-256 | Format |
|---|---|---|
| `ConEx 1.2.sit` | `593d8c50e11cc3d405e06eb3736671afeba76c82527bbd13fd21748ca8032d58` | StuffIt 5, "Arsenic" arithmetic coder |
| `archived/792_ConEx12.sit.hqx` | `ded5fc0c7d9412ae174bd28a690d683fef65a571b809731ab626a31589aa4627` | BinHex 4.0 wrapping the same .sit |

Mirrored 2026-08-27 from the Cythera Guides EV archive
(`cytheraguides.com/archives/ambrosia_addons/ev/`).

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

## Resource inventory (from `tools/rsrc_extract.py`)

- `ConEx1.2.rsrc`: **538 resources / 26 types** — 92 `PICT` (1,271,710 B), 191 `dësc`,
  36 `mïsn`, 31 `spïn`, 24 `shïp`, 14 `sÿst`, 10 `spöb`, 10 `oütf`, 17 `düde`,
  17 `TMPL`, 7 `STR#`, 50 `STR `, 6 `snd `, 5 `gövt`, 3 `wëap`, 2 `përs`,
  1 each `flët`/`öops`/`vers`, plus icon families.
- `ConEx Readme 1.2.rsrc`: 220 resources / 38 types — 14 `TEXT`+`styl` chapters,
  43 `PICT`, plus the DOCMaker viewer's own `CODE`/UI resources.

## Extraction toolchain

- `unar` 1.10.8_7 (Homebrew bottle), `-k visible` → AppleDouble `.rsrc` files
- `tools/rsrc_extract.py` — AppleDouble unwrap + resource-fork walk (Python 3.9.6)
- `tools/pict_decode.py` — QuickDraw PICT v2 subset → PNG (Pillow)
- `tools/convert_all.py` — batch PICT/spïn/text conversion
- `tools/tmpl_dump.py` — applies the plugin's own ResEdit `TMPL`s to its resources
