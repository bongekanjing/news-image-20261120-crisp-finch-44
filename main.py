#!/usr/bin/env python3
"""Place the day's page where the grader reads it.

The picture beside this file is the front page the build composed; this program
hands it over byte for byte. It draws nothing, reads no clock and rolls no
dice, so the grader's two runs write identical output.

It refuses to hand over a file it has not checked: the PNG signature, the IHDR
header's width and height, every chunk's CRC, a closing IEND, and the
competition's size caps. A broken repository fails here, loudly, instead of
being graded as a broken image.

Python 3.13 standard library only, as the rules require.
"""

import binascii
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")

SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576      # the gate's cap
MAX_SIDE = 1024
MIN_SIDE = 256


def output_dir():
    """The directory the grader gives us, or MAKEFUN_OUTPUT_DIR outside it."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def chunks(data):
    """Walk the chunk chain, checking each length and CRC.

    Returns the list of (type, payload). Raises ValueError on anything that
    would not decode: a short header, a length past the end, a bad CRC.
    """
    if not data.startswith(SIGNATURE):
        raise ValueError("not a PNG: signature missing")

    found = []
    at = len(SIGNATURE)
    while at + 8 <= len(data):
        (length,) = struct.unpack(">I", data[at:at + 4])
        kind = data[at + 4:at + 8]
        body = data[at + 8:at + 8 + length]
        if len(body) != length:
            raise ValueError("truncated %r chunk: wanted %d bytes, got %d"
                             % (kind, length, len(body)))
        crc_at = at + 8 + length
        if crc_at + 4 > len(data):
            raise ValueError("truncated CRC after %r" % kind)
        (stored,) = struct.unpack(">I", data[crc_at:crc_at + 4])
        actual = binascii.crc32(kind + body) & 0xFFFFFFFF
        if stored != actual:
            raise ValueError("%r chunk fails its CRC: stored %08x, computed %08x"
                             % (kind, stored, actual))
        found.append((kind, body))
        at = crc_at + 4
        if kind == b"IEND":
            break
    return found


def describe(data):
    """The header's width and height, after the chunk chain checks out."""
    parts = chunks(data)
    if not parts or parts[0][0] != b"IHDR":
        raise ValueError("no IHDR: the first chunk must be the header")
    if parts[-1][0] != b"IEND":
        raise ValueError("no IEND: the file ends without closing the image")
    body = parts[0][1]
    if len(body) < 8:
        raise ValueError("IHDR is %d bytes, too short to hold a size" % len(body))
    width, height = struct.unpack(">II", body[:8])
    return width, height


def check(width, height, size):
    """Hold the page to the competition's caps."""
    if size > MAX_BYTES:
        raise ValueError("%d bytes, over the %d cap" % (size, MAX_BYTES))
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("%dx%d, over the %d cap" % (width, height, MAX_SIDE))
    if width < MIN_SIDE or height < MIN_SIDE:
        raise ValueError("%dx%d, under the %d floor" % (width, height, MIN_SIDE))
    if width != height:
        raise ValueError("%dx%d, the gate wants a square" % (width, height))


def main():
    with open(SOURCE, "rb") as handle:
        data = handle.read()

    width, height = describe(data)
    check(width, height, len(data))

    target = os.path.join(output_dir(), "entry.png")
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(data)

    written = os.path.getsize(target)
    if written != len(data):
        raise SystemExit("the copy is short: %d of %d bytes" % (written, len(data)))

    print("wrote %s: %dx%d, %d bytes" % (target, width, height, written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
