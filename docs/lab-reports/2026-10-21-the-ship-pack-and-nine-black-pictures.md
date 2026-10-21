# The ship pack, and nine pictures that were never black

**21 October 2026** · extraction · follows
[ConEx resource extraction](2026-08-27-conex-resource-extraction.md)

The Yodacon Ship Pack (submodule `ship-pack/`, github.com/yodacon/yodacon-ship-pack,
served at yodacon.org/ship-pack/) puts Paul Richeson's ships into one
GPL-2.0-or-later release that other people's games can use: ten from ConEx 1.2
(shïp/spïn 166–175) and eleven from ConEx Override 1.0 (175–185). Each has its
sprite sheet, mask, sheet with alpha, 36 rotation frames, and target,
shipyard, comm and icon pictures. The pack builds itself from the original
`.sit.hqx` archives with its own pure-Python extractor (section 3); `make
ship-pack` runs its tests and rebuilds it.

Laying every picture out on one contact sheet turned up two decoder bugs that
had been in `vendor/paulricheson/tools/pict_decode.py` since August.

## 1. Device colour tables: nine pictures decoded solid black

The Small, Medium and Large Pin shipyard and comm portraits (PICT 5038–5040,
5338–5340), the Trident's shipyard and comm (5044, 5344) and the Tomaquad's
shipyard picture (5047) all decoded to a 100×100 field of pure black. Their
files are 4–6 KB, the same as their neighbours, so they had data in them.

All nine are 8-bit `PackBitsRect` pixmaps whose colour table has the high bit
of `ctFlags` set: a **device** table. In a device table QuickDraw ignores each
entry's `value` field and indexes the entries by position. The plugin's tables
leave every `value` at zero. The decoder keyed the palette on `value`, so all
256 entries landed on index 0, the last one (black) won, and every other index
fell through to the black default.

Fix: key on position when `ctFlags & 0x8000`. The nine pictures now decode to
the renders Paul made in 1997. The two readme pictures that used device tables
(2025, 2030) changed too.

## 2. 1-bit bitmaps were photographic negatives

QuickDraw paints a set bit **black**. The decoder wrote a set bit as 1, which
Pillow's `"1"` mode draws **white**. Every 1-bit PICT in the plugin is a sprite
mask, so the only visible symptom was that the eight 1-bit masks were negatives
of what the Mac showed. `convert_all.py` then inverted the mask again to get
alpha, which cancelled the error for those eight.

The cancelling broke for the three masks stored as 8-bit pictures: the Dart
(20607), the ConEx Defender (20609) and the Missile Repeater (211). Those decode
correctly, white ship on black, and the extra inversion made their composites
opaque everywhere except the ship. The Dart sprite in
`extracted/sprites/` was a grey box.

Fix: a set bit decodes black, and alpha is the mask itself for every mask, of
either depth. The eight 1-bit composites are pixel-identical to before; the
Dart, Defender and Missile Repeater composites are now correct.

## What changed in the tree

Only files whose **pixels** changed were kept. Pillow re-encodes every PNG with
slightly different bytes, so the other 113 regenerated files were restored to
their committed bytes.

| Files | Change |
| --- | --- |
| `png/ConEx1.2/5038 5039 5040 5044 5047 5338 5339 5340 5344` | black → the real picture |
| `png/ConEx-Readme-1.2/2025 2030` | device colour table now read |
| `png/ConEx1.2/20601 … 20620` (the 1-bit masks) | no longer negatives |
| `sprites/169_Dart 170_Defender 200_Missile Repeater` | alpha no longer inverted |

## 3. An extractor with no Mac and no unar

The August extraction depended on The Unarchiver (`unar`), which is not
installed here and is a closed loop for anyone wanting to know what it did.
The pack now carries its own, in `ship-pack/tools/`:

| Layer | Module | Check |
| --- | --- | --- |
| BinHex 4.0 | `binhex.py` | header, data and resource CRC-16/XMODEM |
| StuffIt 5 container | `stuffit.py` | folder-end markers (data length `0xFFFFFFFF`, header only) were the one surprise |
| StuffIt 5 method 15, Arsenic | `arsenic.py` | adaptive arithmetic coder, MTF with RUNA/RUNB zero runs, inverse BWT, bzip2-style RLE; CRC-32 |
| classic StuffIt, method 13 | `sit13.py` | LZ77 + canonical Huffman, codes sent under a fixed 37-symbol meta-code; per-fork CRC-16/ARC |
| resource fork, `TMPL` | `rfork.py`, `tmpl.py` | copied from `evutils/` |
| QuickDraw PICT | `pict.py` | this report's two fixes, plus state and vector opcodes stepped over, and QuickTime Photo-JPEG pictures |

The proof is the committed tree: every one of ConEx 1.2's 538 plugin
resources and 220 readme resources, as the new extractor produces them, is
byte-identical to `vendor/paulricheson/extracted/`. ConEx 1.2 decodes in 5.5 s;
ConEx Override's 3.3 MB of method-13 forks in under 2 s, both CRCs matching on
the first run. `make -C ship-pack test` keeps those checks.

## 4. ConEx Override, and where konex's cast came from

`2437_ConExOverride.sit.hqx` (Cythera Guides' EV Override catalogue, posted
1998-09-26) is the second plugin: a classic StuffIt archive holding
`ConEx Override 1.0` (type `Opïf`, 462 resources, modified 1998-07-10) and its
DOCMaker readme. Its readme credits Paul Richeson as creator. It has eleven
ships, with larger sprites than 1.2 (the Yodacon goes from 70 to 96 px), a
Callisto that 1.2 never had, no Medium Pin, and sixteen landing pictures,
thirteen of them distinct (the catalogue entry promised twelve new ones), one
a 640×480 QuickTime JPEG.

konex's ship list is exactly ConEx Override's ten named hulls plus Advisor and
Citrus. A pixel comparison settles the rest: konex's `yodacon/00.tga` has the
same 57×87 opaque footprint as Override's frame 0, and the Small Pin's 26×35
matches too. konex's cast is ConEx Override's art, padded to power-of-two
textures and in places rescaled, not a redraw. Gonex therefore already flies
both of Paul's editions: the 1997 originals as `<ship>97`, and the 1998 art
through konex.

## 5. Provenance of the rehosted archives

The Wayback Machine holds Ambrosia's own redirect `download.php?addon=792` →
`ambrosiasw.com/assets/files/addons/ev/ConEx12.sit.hqx`, captured 2013-04-13,
with SHA-1 `ZDTUBHW2GS3P3HGSW2S3BQQFL7K6Z56O`. That is the SHA-1 of the
Cythera copy committed in `vendor/paulricheson/release/`, so the rehosted
file is byte-identical to the one Ambrosia served. Cythera's numeric prefixes
(`792_`, `793_`, `2437_`) are Ambrosia's add-on IDs. Ambrosia's copies of the
updater and of ConEx Override were not archived. Dated screenshots of the
catalogue rows are in `ship-pack/sources/screenshots/`.

## Still to do

Gonex carries the bad decode. `data/export_ships.py` copied the black Pin,
Trident and Tomaquad pictures into `gonex/assets/data/ships/*97/`. The Dart
and Defender '97 frames have inverted alpha there too. `make export`
regenerates them, but it needs `unar` to expand the 1997 release first.
