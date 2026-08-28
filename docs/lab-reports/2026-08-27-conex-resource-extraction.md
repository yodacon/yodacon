# Recovery of Sprite, Mission-Text, and PICT Resources from the 1997 *ConEx* Escape Velocity Plugin

**Yodacon Project Lab Report LR-2026-01** · docs/lab-reports · 2026-08-27
**P. Richeson** (Yodacon project) with Claude (Anthropic) as extraction tooling

---

**Abstract** — *ConEx 1.2* (1997) is an Escape Velocity plugin distributed as
a StuffIt 5 archive whose payload lives entirely in a Macintosh resource
fork — a container modern systems no longer read natively. We report the
complete recovery of its 538 resources, including all 92 QuickDraw PICT
images, 191 description texts, 36 mission records, and 24 ship definitions.
A four-stage pipeline (archive expansion, AppleDouble/resource-fork parsing,
QuickDraw PICT v2 decoding, sprite–mask compositing) converted every plugin
PICT to PNG (92/92) and composited 11 RGBA sprite sheets, including the
70×70×36-frame *Yodacon* rotation bank, which now ships as a playable ship in
the Gonex game (a 2026 Go port of the 2005 konex remake). File-system
timestamps preserved through the 29-year chain date the plugin's creation to
1997-11-09 and its release build to a single evening on 1997-11-28.

**Index Terms** — digital preservation, resource fork, QuickDraw PICT,
StuffIt, BinHex, Escape Velocity, sprite extraction, Macintosh.

---

## I. Introduction

The Yodacon project's founding artifact is a starship that first flew in
*ConEx*, an Escape Velocity (EV) plugin built in 1997. The only surviving
distribution is `ConEx 1.2.sit`, mirrored from the Cythera Guides EV archive
into `vendor/docs/`. The objectives of this experiment were:

1. expand the StuffIt archive on modern macOS without data loss;
2. enumerate and split every resource in the plugin's resource fork;
3. recover human-readable **mission and description text**;
4. decode the **PICT** image resources and composite sprite+mask pairs into
   transparent sprite sheets;
5. convert the recovered sprites into **game files usable by additional
   games** — concretely, a ship folder for Gonex;
6. record all creation/modification **dates** carried by the files.

## II. Background

EV plugins are classic Mac OS files of type `Mpïf` whose data fork is empty
(8 bytes here); everything — ship stats (`shïp`), sprite tables (`spïn`),
weapons (`wëap`), missions (`mïsn`), prose (`dësc`), strings (`STR `/`STR#`),
images (`PICT`), sounds (`snd `) — lives in the resource fork. The fork
format (Inside Macintosh, Vol. I) is a header, a data section of
length-prefixed blocks, and a map of typed reference lists. Sprites are
stored as pairs of PICTs: a color sheet and a 1-bit mask, tiled 6×6 for 36
rotation frames.

## III. Methodology

### A. Archive expansion

`lsar` identified the archive as **StuffIt 5** with "Arsenic" (arithmetic)
compression. The Unarchiver's `unar 1.10.8_7` (Homebrew) expanded it with
`-k visible`, emitting resource forks as AppleDouble files:

- `ConEx1.2` — data fork, 8 B
- `ConEx1.2.rsrc` — AppleDouble container, 1,523,020 B
- `ConEx Readme 1.2.rsrc` — AppleDouble container, 398,228 B

The fallback `.hqx` (BinHex 4.0) copy in `vendor/docs/archived/` was not
needed.

### B. Resource-fork parsing (`tools/rsrc_extract.py`)

The AppleDouble wrapper (magic `0x00051607`) was unwrapped by locating entry
ID 2 (resource fork) and entry ID 9 (Finder info, yielding the type/creator
codes in Table III). The fork itself was walked with a 90-line parser:
header → resource map → type list → reference lists → length-prefixed data
blocks. Each resource was written to
`vendor/paulricheson/extracted/<container>/<type>/<id>[_<name>].bin`. Resource names and type
codes were decoded as MacRoman (`dësc`, `shïp`, `spïn` …).

### C. Text recovery (`tools/convert_all.py`, `tools/tmpl_dump.py`)

- **`dësc` (191 resources)**: null-terminated MacRoman prose — landing
  descriptions, shipyard blurbs, and mission text. Dumped to UTF-8 `.txt`.
- **`STR#`/`STR `**: Pascal-string lists (e.g., `STR#` 5006 "Ship Comm Short
  Names") dumped as numbered lines.
- **Readme**: a self-displaying DOCMaker application (creator `Dk@P`); its 14
  `TEXT` chapters were dumped directly, recovering the 1997 credits page
  (creator, five beta testers, the GeoCities URL).
- **`mïsn` (36 resources)**: fixed binary records; their prose lives in
  `dësc`, which is already recovered. Field-level decoding used the plugin's
  own ResEdit **`TMPL`** templates — the plugin documents its own binary
  formats — via a TMPL interpreter supporting `DWRD`, `DLNG`, `RECT`, `PSTR`.

### D. PICT v2 decoding (`tools/pict_decode.py`)

A ~200-line QuickDraw PICT v2 decoder was written against the observed
opcode inventory:

| Opcode | Meaning | Pixel formats handled |
|---|---|---|
| `0x0090` | BitsRect (raw) | 1-bit bitmap |
| `0x0098/0x0099` | PackBitsRect/Rgn | 1-bit bitmap; 1/2/4/8-bit indexed + color table |
| `0x009A/0x009B` | DirectBitsRect/Rgn | 16-bit RGB555 packType 3; 32-bit packType 4 (planar) |
| `0x0001/0x001E/0x0C00/0x00A0/0x00A1/0x00FF` | clip/state/header/comments/end | skipped |

Byte-oriented PackBits (≤8-bit), word-oriented PackBits (16-bit), and planar
byte-RLE (32-bit) row codecs were implemented; region-clipped variants skip
the trailing mask region. Output is PNG via Pillow.

### E. Sprite compositing and game-file conversion

For each `spïn` record — `(spriteID, maskID, w, h, cols, rows)` — the color
sheet and mask PICTs were decoded and composited into RGBA PNG
(alpha = inverted 1-bit mask, since QuickDraw 1-bits mark ink). The
**Yodacon** bank (`spïn` 174 → PICT 20617 sheet + 20618 mask, 70×70, 6×6)
was then sliced into 36 per-frame PNGs and installed as
`Gonex/assets/data/ships/yodacon97/{00..35}.png`, joined by its target
(PICT 3046), shipyard (5046) and comm (5346) pictures and a `specs.xml`
translated from the `shïp` 174 record. Gonex's asset loader accepts PNG
beside the original TGA art, so the 1997 renders are selectable in the 2026
shipyard unmodified.

## IV. Results

### A. Timestamps (objective 6)

HFS timestamps survived StuffIt → APFS extraction intact:

| File | Created | Modified |
|---|---|---|
| `ConEx1.2` (plugin) | **1997-11-09 15:32:18** | **1997-11-28 20:05:34** |
| `ConEx Readme 1.2` | 1997-11-28 20:13:43 | 1997-11-28 20:15:58 |
| Archive members (`lsar`) | — | 1997-11-28 20:05–20:15 |

The plugin was created on a Sunday, worked for ~19 days, and released in one
evening: final plugin save 20:05, readme finished 20:15, archive stuffed
immediately after. Full manifest with SHA-256 hashes:
`vendor/paulricheson/PROVENANCE.md`.

### B. Resource inventory

538 resources across 26 types in the plugin (selected):

| Type | Count | Bytes | Type | Count | Bytes |
|---|---|---|---|---|---|
| `PICT` | 92 | 1,271,710 | `sÿst` | 14 | 1,008 |
| `dësc` | 191 | 39,820 | `spöb` | 10 | 320 |
| `mïsn` | 36 | 2,952 | `oütf` | 10 | 180 |
| `spïn` | 31 | 372 | `snd ` | 6 | 176,649 |
| `shïp` | 24 | 1,776 | `wëap` | 3 | 90 |
| `TMPL` | 17 | 2,414 | `STR#`/`STR ` | 57 | 6,351 |

The readme contributed 220 further resources (14 `TEXT` chapters, 43 PICT).

### C. Conversion rates

| Stage | Result |
|---|---|
| Plugin PICT → PNG | **92 / 92** |
| Readme PICT → PNG | 32 / 44 (12 failures: one v1 PICT, eleven with unimplemented opcode `0x000C`) |
| `spïn` sheets composited | **11 / 31** — the other 20 reference sprite PICTs of the *base EV game* (IDs 1002–1049, 200–203, 2004–2045), absent from the plugin by design |
| `dësc`/`STR`/`TEXT` → UTF-8 | 100 % |
| Sprites → Gonex ship folder | 36 frames + 3 pictures + specs, playable in-game |

### D. Sample recoveries

- `shïp` 174 *Yodacon* (via its own TMPL): Shield 2000, Accel 560, Speed 300,
  Maneuver 3, Fuel 400, Armor 500, MaxGuns 5, MaxTurrets 5, Cost 2,800,000,
  Crew 217, Mass 350 t, Length 80 m.
- `dësc` 2146: *"The Caption of the Yodacon is willing to be your escort."*
- `dësc` 133: *"Consolidated Express bought Levo, and turned this peacefull
  planet into a Buisy World."* (1997 spelling preserved.)
- Readme `TEXT` 130: credits — Creator: Paul Richeson; five named beta
  testers; `http://www.geocities.com/SiliconValley/Way/9298`.

## V. Discussion

The pipeline's only irrecoverable-by-design gap is the 20 sprite banks that
point into the base Escape Velocity game's own resources — a plugin overlays
the game, so those sprites were never in this file. The readme's 12
undecoded PICTs are decorative page graphics inside a DOCMaker binary and
were not pursued. All decoding was performed with ~420 lines of Python and
zero proprietary tooling; `DeRez` was available but unnecessary. The 6 `snd `
resources remain raw Mac sound data (extraction done, format conversion
deferred).

## VI. Conclusion and Future Work

All six objectives were met. The 1997 plugin is now a diffable directory
tree (`vendor/paulricheson/extracted/`), its art is PNG, its prose is UTF-8, its dates are
recorded, and one recovered ship is flying again in a modern engine.
Future work (tracked in `backlog.md` Phase 1–2 and `Gonex/BACKLOG.md`):
decode `rlë8`-era formats for Nova plugins, convert `snd ` resources,
port the extractor to Go so Gonex can ingest plugin files directly, and
composite the remaining ConEx ships against a base-EV resource donor.

## References

[1] Apple Computer, *Inside Macintosh, Volume I* — Resource Manager, 1985.
[2] Apple Computer, *Inside Macintosh: Imaging with QuickDraw* — Picture
    Opcodes, 1994.
[3] AppleSingle/AppleDouble Formats for Foreign Files, RFC 1740, 1994.
[4] M. Burch, *Escape Velocity* (game and plugin format), Ambrosia Software,
    1996.
[5] *EV Nova Bible*, `vendor/docs/Nova Bible.txt` (rlë8/rlëD reference for
    future Nova-format work).
[6] J. B. Bussdieker, *konex*, GPL-2 source, 2005 (github.com/jbussdieker/konex).

## Appendix: Toolchain

`unar` 1.10.8_7 · Python 3.9.6 + Pillow · `tools/rsrc_extract.py` ·
`tools/pict_decode.py` · `tools/convert_all.py` · `tools/tmpl_dump.py` ·
outputs under `vendor/paulricheson/extracted/{ConEx1.2, ConEx-Readme-1.2, png, sprites, text}`.
