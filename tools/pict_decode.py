#!/usr/bin/env python3
"""Decode QuickDraw PICT v2 resources (the subset Escape Velocity plugins use)
to PNG.

Handles:
  0x0090 BitsRect            uncompressed 1-bit bitmap
  0x0098/0x0099 PackBitsRect/Rgn   1-bit bitmap or 1/2/4/8-bit indexed pixmap
  0x009A/0x009B DirectBitsRect/Rgn 16-bit RGB555, packType 3

Usage: pict_decode.py <resource.bin> <out.png>   (or import decode_pict)
"""
import struct
import sys

from PIL import Image


class Reader:
    def __init__(self, buf, pos=0):
        self.buf = buf
        self.pos = pos

    def u8(self):
        v = self.buf[self.pos]
        self.pos += 1
        return v

    def u16(self):
        (v,) = struct.unpack_from(">H", self.buf, self.pos)
        self.pos += 2
        return v

    def s16(self):
        (v,) = struct.unpack_from(">h", self.buf, self.pos)
        self.pos += 2
        return v

    def u32(self):
        (v,) = struct.unpack_from(">I", self.buf, self.pos)
        self.pos += 4
        return v

    def rect(self):
        return struct.unpack_from(">hhhh", self.buf, self.pos), self.skip(8)

    def skip(self, n):
        self.pos += n

    def take(self, n):
        v = self.buf[self.pos : self.pos + n]
        self.pos += n
        return v

    def align(self):
        if self.pos & 1:
            self.pos += 1


def unpackbits_bytes(r: Reader, rowbytes: int) -> bytes:
    """One scanline of byte-oriented PackBits."""
    if rowbytes < 8:
        return r.take(rowbytes)
    count = r.u16() if rowbytes > 250 else r.u8()
    end = r.pos + count
    out = bytearray()
    while r.pos < end:
        flag = r.u8()
        if flag >= 128:
            out += bytes([r.u8()]) * (257 - flag)
        else:
            out += r.take(flag + 1)
    return bytes(out)


def unpackbits_words(r: Reader, rowbytes: int) -> bytes:
    """One scanline of word-oriented PackBits (packType 3, 16-bit pixels)."""
    count = r.u16() if rowbytes > 250 else r.u8()
    end = r.pos + count
    out = bytearray()
    while r.pos < end:
        flag = r.u8()
        if flag >= 128:
            out += r.take(2) * (257 - flag)
        else:
            out += r.take((flag + 1) * 2)
    return bytes(out)


def read_color_table(r: Reader):
    r.u32()  # ctSeed
    r.u16()  # ctFlags
    ct_size = r.u16()
    table = {}
    for _ in range(ct_size + 1):
        value = r.u16()
        red, green, blue = r.u16() >> 8, r.u16() >> 8, r.u16() >> 8
        table[value] = (red, green, blue)
    return [table.get(i, (0, 0, 0)) for i in range(256)]


def decode_pict(data: bytes) -> Image.Image:
    r = Reader(data)
    r.skip(2)  # picSize (meaningless for >32KB pictures)
    (top, left, bottom, right), _ = r.rect()
    width, height = right - left, bottom - top
    if r.u16() != 0x0011 or r.u16() != 0x02FF:
        raise ValueError("not a version 2 PICT")

    image = None
    while r.pos < len(data) - 1:
        r.align()
        op = r.u16()
        if op == 0x0000 or op == 0x001E:  # NOP / DefHilite
            continue
        elif op == 0x0C00:  # HeaderOp
            r.skip(24)
        elif op == 0x0001:  # Clip region
            r.skip(r.u16() - 2)
        elif op == 0x00A0:  # ShortComment
            r.skip(2)
        elif op == 0x00A1:  # LongComment
            r.u16()
            r.skip(r.u16())
        elif op == 0x00FF:  # OpEndPic
            break
        elif op in (0x0090, 0x0098, 0x0099, 0x009A, 0x009B):
            image = decode_bits(r, op)
        else:
            raise ValueError(f"unhandled PICT opcode 0x{op:04X} at {r.pos - 2}")

    if image is None:
        raise ValueError("PICT contained no raster data")
    if image.size != (width, height):
        image = image.crop((0, 0, width, height))
    return image


def decode_bits(r: Reader, op: int) -> Image.Image:
    packed_op = op in (0x0098, 0x0099)
    has_region = op in (0x0099, 0x009B)
    if op in (0x009A, 0x009B):
        r.u32()  # baseAddr
    rowbytes_raw = r.u16()
    is_pixmap = bool(rowbytes_raw & 0x8000)
    rowbytes = rowbytes_raw & 0x7FFF
    (top, left, bottom, right), _ = r.rect()
    width, height = right - left, bottom - top

    def skip_rects_mode():
        r.skip(8 + 8 + 2)  # srcRect, dstRect, mode
        if has_region:
            r.skip(r.u16() - 2)  # maskRgn (size word includes itself)

    if not is_pixmap:  # 1-bit BitMap
        skip_rects_mode()
        rows = []
        for _ in range(height):
            row = unpackbits_bytes(r, rowbytes) if packed_op else r.take(rowbytes)
            rows.append(row)
        image = Image.new("1", (width, height))
        px = image.load()
        for y, row in enumerate(rows):
            for x in range(width):
                px[x, y] = 1 if row[x // 8] & (0x80 >> (x % 8)) else 0
        return image

    r.u16()  # pmVersion
    pack_type = r.u16()
    r.skip(4 + 4 + 4 + 2)  # packSize, hRes, vRes, pixelType
    pixel_size = r.u16()
    r.skip(2 + 2 + 4 + 4 + 4)  # cmpCount, cmpSize, planeBytes, pmTable, reserved

    palette = read_color_table(r) if packed_op else None
    skip_rects_mode()

    if pixel_size in (1, 2, 4, 8):
        pixels_per_byte = 8 // pixel_size
        shift, mask = 8 - pixel_size, (1 << pixel_size) - 1
        image = Image.new("RGB", (width, height))
        px = image.load()
        for y in range(height):
            row = unpackbits_bytes(r, rowbytes)
            for x in range(width):
                b = row[x // pixels_per_byte]
                v = (b >> (shift - (x % pixels_per_byte) * pixel_size)) & mask
                px[x, y] = palette[v]
        return image
    if pixel_size == 16 and pack_type == 3:
        image = Image.new("RGB", (width, height))
        px = image.load()
        for y in range(height):
            row = unpackbits_words(r, rowbytes)
            for x in range(width):
                (v,) = struct.unpack_from(">H", row, x * 2)
                red = (v >> 10) & 0x1F
                green = (v >> 5) & 0x1F
                blue = v & 0x1F
                px[x, y] = (red << 3 | red >> 2, green << 3 | green >> 2, blue << 3 | blue >> 2)
        return image
    if pixel_size == 32 and pack_type == 4:  # planar byte-RLE, components per row
        image = Image.new("RGB", (width, height))
        px = image.load()
        for y in range(height):
            row = unpackbits_bytes(r, rowbytes)
            planes = len(row) // width  # 3 = RGB, 4 = ARGB (alpha plane first)
            base = width * (planes - 3)
            for x in range(width):
                px[x, y] = (row[base + x], row[base + width + x], row[base + 2 * width + x])
        return image
    raise ValueError(f"unhandled pixel format: {pixel_size}-bit packType {pack_type}")


if __name__ == "__main__":
    decode_pict(open(sys.argv[1], "rb").read()).save(sys.argv[2])
    print(f"wrote {sys.argv[2]}")
