#!/usr/bin/env python3
"""Batch-convert extracted ConEx resources to modern formats.

- every PICT           -> extracted/png/PICT/<id>[_<name>].png
- every spïn sheet     -> extracted/sprites/<id>_<name>.png (RGBA, mask applied)
- dësc, STR , STR#, TEXT -> extracted/text/... (UTF-8, decoded from MacRoman)

Usage: convert_all.py <extracted-dir e.g. extracted/ConEx1.2> [readme-dir]
"""
import struct
import sys
from pathlib import Path

from PIL import Image
from pict_decode import decode_pict

FAILURES = []


def out_root(src_root: Path) -> Path:
    return src_root.parent


def convert_picts(src_root: Path):
    dst = out_root(src_root) / "png" / src_root.name
    dst.mkdir(parents=True, exist_ok=True)
    ok = 0
    for f in sorted((src_root / "PICT").glob("*.bin")):
        try:
            decode_pict(f.read_bytes()).save(dst / (f.stem + ".png"))
            ok += 1
        except Exception as e:  # record and continue; report failures at the end
            FAILURES.append((str(f), str(e)))
    print(f"PICT -> PNG: {ok} converted, {len(FAILURES)} failed, into {dst}")


def convert_sprites(src_root: Path):
    dst = out_root(src_root) / "sprites"
    dst.mkdir(parents=True, exist_ok=True)
    pict_dir = src_root / "PICT"
    picts = {int(p.stem.split("_")[0]): p for p in pict_dir.glob("*.bin")}
    ok = 0
    for f in sorted((src_root / "spïn").glob("*.bin")):
        sprite_id, mask_id, w, h, cols, rows = struct.unpack(">hhhhhh", f.read_bytes())
        if sprite_id not in picts or mask_id not in picts:
            FAILURES.append((str(f), f"missing PICT {sprite_id}/{mask_id}"))
            continue
        try:
            sheet = decode_pict(picts[sprite_id].read_bytes()).convert("RGBA")
            mask = decode_pict(picts[mask_id].read_bytes()).convert("L")
        except Exception as e:
            FAILURES.append((str(f), str(e)))
            continue
        # 1-bit masks decode with ship pixels black(0): alpha = inverted mask
        sheet.putalpha(mask.point(lambda v: 255 - v))
        sheet.save(dst / (f.stem + ".png"))
        ok += 1
    print(f"spïn sheets: {ok} composited into {dst}")


def dump_text(src_root: Path):
    dst = out_root(src_root) / "text" / src_root.name
    for sub in ("dësc", "TEXT"):
        d = src_root / sub
        if not d.is_dir():
            continue
        (dst / sub).mkdir(parents=True, exist_ok=True)
        for f in sorted(d.glob("*.bin")):
            text = f.read_bytes().rstrip(b"\x00").decode("mac_roman")
            (dst / sub / (f.stem + ".txt")).write_text(text.replace("\r", "\n"))
    for sub in ("STR#", "STR "):
        d = src_root / sub
        if not d.is_dir():
            continue
        (dst / sub.strip()).mkdir(parents=True, exist_ok=True)
        for f in sorted(d.glob("*.bin")):
            buf, lines = f.read_bytes(), []
            if sub == "STR#":
                (count,) = struct.unpack_from(">H", buf, 0)
                pos = 2
                for i in range(count):
                    n = buf[pos]
                    lines.append(f"{i}\t" + buf[pos + 1 : pos + 1 + n].decode("mac_roman"))
                    pos += 1 + n
            else:
                lines.append(buf[1 : 1 + buf[0]].decode("mac_roman"))
            (dst / sub.strip() / (f.stem + ".txt")).write_text("\n".join(lines))
    print(f"text dumped into {dst}")


def main():
    for arg in sys.argv[1:]:
        root = Path(arg)
        print(f"== {root} ==")
        if (root / "PICT").is_dir():
            convert_picts(root)
        if (root / "spïn").is_dir():
            convert_sprites(root)
        dump_text(root)
    if FAILURES:
        print("failures:")
        for f, e in FAILURES:
            print(f"  {f}: {e}")


if __name__ == "__main__":
    main()
