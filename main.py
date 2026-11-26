#!/usr/bin/env python3
"""news-image-20261126 entrypoint: copy the entry image to the output dir.

The image (entry.png, next to this file) sums up Thursday 26 November 2026
world news in one picture. This program only copies it, after checking it is
a real PNG inside the size limit, so both runs write identical bytes.
Standard library only, no network.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def validate(data):
    """Check the image against the competition's shape rules.

    Fail loudly with a clear message and a non-zero exit instead of
    relying on bare asserts, which Python strips when run with -O.
    Returns the image's width and height in pixels.
    """
    if data[:8] != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG")
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png is over the 1 MiB limit")
    # PNG IHDR: width and height are the 4-byte big-endian values at
    # offsets 16 and 20; the image must be at most 1024 by 1024 pixels.
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width > 1024 or height > 1024:
        raise SystemExit("entry.png is %dx%d, over the 1024x1024 limit"
                         % (width, height))
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    with open(SRC, "rb") as f:
        data = f.read()
    width, height = validate(data)
    digest = hashlib.sha256(data).hexdigest()
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as f:
        f.write(data)
    with open(dest, "rb") as f:
        written = f.read()
    if written != data:
        print("written bytes differ from entry.png", file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, %dx%d, sha256 %s)"
          % (dest, len(data), width, height, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
