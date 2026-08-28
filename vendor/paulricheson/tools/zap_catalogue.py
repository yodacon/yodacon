#!/usr/bin/env python3
"""Catalogue a ResCompare "ZAPS" self-applying patch (the ConEx 1.1→1.2 updater).

Usage: zap_catalogue.py <patch-app-rsrc> [<target-fork-rsrc>]

Parses the patch directory (`ZAP#`) that ResCompare 5.0 (Michael Hecht, 1996)
embeds in the patch application: one entry per changed resource, carrying the
post-patch ("new") and pre-patch ("old") attribute/size/checksum triplets and
the resource name. With a target fork given, verifies the target against the
new-state sizes — matching sizes on every entry shows the target is the
patch's output state. The per-resource diff payloads live in `ZAP ` resources
(new bytes) with `ZIS#`/`ZIL#` item lists (offsets/lengths); their raw hex is
printed for study. The 32-bit checksum algorithm is ResCompare's own and is
not implemented here.

The entry layout was recovered by inspection (see
docs/lab-reports/2026-08-27-conex-11-to-12-patch-catalogue.md):

    ZAP# : count:u16, then per entry:
      flags:u16  verb:u16  type:4s  id:s16
      new: attrs:u16 size:u32 check:u32
      old: attrs:u16 size:u32 check:u32
      name: pascal string, padded to even total length
    verb 0x0301/0x0300 = replace, 0x0101 = old-only (removed in new)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from evutils import rfork  # noqa: E402

VERBS = {0x0301: "replace", 0x0300: "replace", 0x0101: "remove"}


def parse_zapdir(buf):
    (n,) = struct.unpack_from(">H", buf, 0)
    pos, entries = 2, []
    for _ in range(n):
        flags, verb = struct.unpack_from(">HH", buf, pos)
        rtype = buf[pos + 4 : pos + 8].decode("mac_roman")
        (rid,) = struct.unpack_from(">h", buf, pos + 8)
        new = struct.unpack_from(">HII", buf, pos + 10)
        old = struct.unpack_from(">HII", buf, pos + 20)
        pos += 30
        nl = buf[pos]
        name = buf[pos + 1 : pos + 1 + nl].decode("mac_roman")
        pos += 1 + nl + ((1 + nl) % 2)
        entries.append((flags, verb, rtype, rid, new, old, name))
    if pos != len(buf):
        raise ValueError(f"ZAP# parse consumed {pos} of {len(buf)} bytes")
    return entries


def main():
    patch = rfork.parse(rfork.unwrap_appledouble(Path(sys.argv[1]).read_bytes()))
    target = None
    if len(sys.argv) > 2:
        fork = rfork.parse(rfork.unwrap_appledouble(Path(sys.argv[2]).read_bytes()))
        target = {(r.rtype, r.rid): r for r in fork.resources}

    zapdir = next(r for r in patch.resources if r.rtype == "ZAP#")
    print(f"Patch directory {zapdir.rid} targets file {zapdir.name!r}\n")
    diffs = {
        t: {r.rid: r for r in patch.resources if r.rtype == t}
        for t in ("ZAP ", "ZIS#", "ZIL#")
    }
    print(f"{'verb':8} {'type':6} {'id':>6} {'name':22} {'old size':>8} {'new size':>8}  target")
    zap_id = 1000
    for flags, verb, rtype, rid, new, old, name in parse_zapdir(zapdir.data):
        state = ""
        if target is not None:
            r = target.get((rtype, rid))
            if VERBS.get(verb) == "remove":
                state = "absent ✓" if r is None else "PRESENT ✗"
            elif r is None:
                state = "MISSING ✗"
            else:
                state = "size ✓" if len(r.data) == new[1] else f"size {len(r.data)} ✗"
        print(f"{VERBS.get(verb, hex(verb)):8} {rtype!r:6} {rid:6} {name!r:22} "
              f"{old[1]:8} {new[1]:8}  {state}")
        if VERBS.get(verb) != "remove":
            zap = diffs["ZAP "].get(zap_id)
            items = diffs["ZIS#"].get(zap_id) or diffs["ZIL#"].get(zap_id)
            if zap is not None:
                show = zap.data.hex() if len(zap.data) <= 16 else f"{len(zap.data)} bytes"
                print(f"{'':8} ZAP {zap_id}: new bytes {show}; "
                      f"items {items.data.hex() if items else '-'}")
            zap_id += 1


if __name__ == "__main__":
    main()
