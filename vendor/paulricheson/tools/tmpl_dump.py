#!/usr/bin/env python3
"""Apply a ResEdit TMPL to a resource and print labeled fields.

Usage: tmpl_dump.py <tmpl.bin> <resource.bin>
Supports the field types ConEx's templates use: DWRD, DLNG, RECT (4 words), PSTR.
"""
import struct
import sys


def parse_tmpl(buf):
    fields, pos = [], 0
    while pos < len(buf):
        n = buf[pos]
        label = buf[pos + 1 : pos + 1 + n].decode("mac_roman")
        ftype = buf[pos + 1 + n : pos + 5 + n].decode("mac_roman")
        fields.append((label, ftype))
        pos += 5 + n
    return fields


def main():
    fields = parse_tmpl(open(sys.argv[1], "rb").read())
    data = open(sys.argv[2], "rb").read()
    pos = 0
    for label, ftype in fields:
        if ftype == "DWRD":
            (v,) = struct.unpack_from(">h", data, pos)
            pos += 2
        elif ftype == "DLNG":
            (v,) = struct.unpack_from(">i", data, pos)
            pos += 4
        elif ftype == "RECT":
            v = struct.unpack_from(">hhhh", data, pos)
            pos += 8
        elif ftype == "PSTR":
            n = data[pos]
            v = data[pos + 1 : pos + 1 + n].decode("mac_roman")
            pos += 1 + n
        else:
            print(f"(stopping: unsupported TMPL type {ftype!r})")
            break
        print(f"{label:14} {v}")


if __name__ == "__main__":
    main()
