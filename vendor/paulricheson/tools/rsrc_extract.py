#!/usr/bin/env python3
"""Split a raw Macintosh resource fork into one file per resource.

Usage: rsrc_extract.py <fork-file> <out-dir>

Writes <out-dir>/<type>/<id>[_<name>].bin and prints a survey of the fork.
Type codes are MacRoman (e.g. b'sh\xefp' -> 'shïp'); the on-disk directory
name keeps the MacRoman spelling, which APFS handles fine.
"""
import struct
import sys
import unicodedata
from pathlib import Path


def sanitize(text: str) -> str:
    keep = []
    for ch in text:
        if ch.isalnum() or ch in " ._-#'":
            keep.append(ch)
        else:
            keep.append("_")
    out = "".join(keep).strip().rstrip(".")
    return out or "_"


def unwrap_appledouble(raw: bytes) -> bytes:
    """Return the resource fork, unwrapping an AppleSingle/AppleDouble container
    (as written by `unar -k visible`) if present. Prints Finder info when found."""
    magic = struct.unpack_from(">I", raw, 0)[0]
    if magic not in (0x00051600, 0x00051607):
        return raw
    (num_entries,) = struct.unpack_from(">H", raw, 24)
    fork = None
    for i in range(num_entries):
        eid, off, length = struct.unpack_from(">III", raw, 26 + i * 12)
        if eid == 2:
            fork = raw[off : off + length]
        elif eid == 9:
            ftype = raw[off : off + 4].decode("mac_roman")
            creator = raw[off + 4 : off + 8].decode("mac_roman")
            print(f"Finder info: type {ftype!r} creator {creator!r}")
    if fork is None:
        raise SystemExit("AppleDouble container has no resource-fork entry")
    return fork


def parse(fork: bytes):
    data_off, map_off, data_len, map_len = struct.unpack_from(">IIII", fork, 0)
    type_list_off, name_list_off = struct.unpack_from(">HH", fork, map_off + 24)
    tl = map_off + type_list_off
    (num_types_m1,) = struct.unpack_from(">H", fork, tl)
    resources = []
    for t in range(num_types_m1 + 1):
        rtype, count_m1, ref_off = struct.unpack_from(">4sHH", fork, tl + 2 + t * 8)
        for r in range(count_m1 + 1):
            ref = tl + ref_off + r * 12
            rid, name_off = struct.unpack_from(">hH", fork, ref)
            (packed,) = struct.unpack_from(">I", fork, ref + 4)
            res_data_off = packed & 0xFFFFFF
            name = ""
            if name_off != 0xFFFF:
                noff = map_off + name_list_off + name_off
                nlen = fork[noff]
                name = fork[noff + 1 : noff + 1 + nlen].decode("mac_roman")
            (rlen,) = struct.unpack_from(">I", fork, data_off + res_data_off)
            payload = fork[data_off + res_data_off + 4 : data_off + res_data_off + 4 + rlen]
            resources.append((rtype.decode("mac_roman"), rid, name, payload))
    return resources


def main():
    fork_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    fork = unwrap_appledouble(fork_path.read_bytes())
    resources = parse(fork)

    survey = {}
    for rtype, rid, name, payload in resources:
        survey.setdefault(rtype, []).append((rid, name, len(payload)))
        tdir = out_dir / sanitize(rtype)
        tdir.mkdir(parents=True, exist_ok=True)
        fname = f"{rid}" + (f"_{sanitize(name)}" if name else "") + ".bin"
        (tdir / fname).write_bytes(payload)

    total = 0
    for rtype in sorted(survey, key=lambda t: unicodedata.normalize("NFD", t)):
        entries = survey[rtype]
        total += len(entries)
        size = sum(e[2] for e in entries)
        ids = sorted(e[0] for e in entries)
        print(f"{rtype!r:10} {len(entries):4d} resources {size:9d} bytes  ids {ids[0]}..{ids[-1]}")
    print(f"TOTAL      {total:4d} resources from {fork_path.name}")


if __name__ == "__main__":
    main()
