#!/usr/bin/env python3
"""Generate PNG icons for the Hebrew Word of the Day PWA.

Pure-Python (zlib only) PNG encoder so the build needs no external image
libraries. Draws a stylized Torah scroll on a deep indigo gradient and
supersamples 4x for antialiasing.
"""
import os
import struct
import zlib

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "icons")
SS = 4  # supersample factor


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(round(lerp(c1[i], c2[i], t))) for i in range(3))


def draw(size, maskable=False):
    """Return an RGBA bytearray for an icon of the given pixel size."""
    S = size * SS
    px = bytearray(S * S * 4)

    # Colors
    bg_top = (49, 46, 129)      # indigo-900
    bg_bot = (30, 27, 75)       # deeper indigo
    gold = (234, 179, 8)        # roller / accent
    gold_dark = (161, 124, 12)
    parch = (250, 244, 224)     # parchment
    parch_shadow = (224, 214, 184)
    ink = (120, 90, 40)

    cx = cy = S / 2.0
    # On maskable icons keep art within the safe zone (~80%).
    art = 0.62 if maskable else 0.74
    R = S * art / 2.0

    # Scroll geometry
    roller_r = R * 0.18
    roller_gap = R * 0.72          # distance from center to each roller axis
    parch_half_w = roller_gap      # parchment spans between rollers
    parch_half_h = R * 0.46
    corner = S * 0.16              # background rounded-corner radius

    def rounded_in(x, y):
        # signed-ish test for rounded square background
        dx = abs(x - cx) - (S / 2.0 - corner)
        dy = abs(y - cy) - (S / 2.0 - corner)
        if dx <= 0 or dy <= 0:
            return True
        return (dx * dx + dy * dy) <= corner * corner

    for yy in range(S):
        y = yy + 0.5
        for xx in range(S):
            x = xx + 0.5
            i = (yy * S + xx) * 4

            if not maskable and not rounded_in(x, y):
                # transparent outside rounded square
                px[i + 3] = 0
                continue

            # vertical gradient background
            t = yy / (S - 1)
            r, g, b = mix(bg_top, bg_bot, t)
            a = 255

            # subtle vignette glow behind the scroll
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            glow = max(0.0, 1.0 - d / (R * 1.25))
            if glow > 0:
                r = int(lerp(r, 79, glow * 0.18))
                g = int(lerp(g, 70, glow * 0.18))
                b = int(lerp(b, 160, glow * 0.18))

            # parchment body
            if abs(x - cx) <= parch_half_w and abs(y - cy) <= parch_half_h:
                shade = 1.0 - 0.10 * ((y - cy) / parch_half_h)
                pc = mix(parch_shadow, parch, max(0.0, min(1.0, shade)))
                r, g, b = pc
                # a few ink "text" lines on the parchment
                rel = (y - (cy - parch_half_h)) / (2 * parch_half_h)
                for ln in (0.30, 0.45, 0.60, 0.75):
                    if abs(rel - ln) < 0.022 and abs(x - cx) < parch_half_w * 0.74:
                        r, g, b = ink

            # rollers (two vertical gold cylinders + knobs)
            for sgn in (-1, 1):
                ax = cx + sgn * roller_gap
                if abs(x - ax) <= roller_r and abs(y - cy) <= parch_half_h + roller_r * 1.4:
                    # cylinder shading across width
                    u = (x - ax) / roller_r
                    sh = 1.0 - 0.55 * abs(u)
                    rc = mix(gold_dark, gold, max(0.0, min(1.0, sh)))
                    r, g, b = rc
                # knobs at top & bottom of each roller
                for ky in (cy - parch_half_h - roller_r * 1.2,
                           cy + parch_half_h + roller_r * 1.2):
                    kd = ((x - ax) ** 2 + (y - ky) ** 2) ** 0.5
                    if kd <= roller_r * 1.05:
                        sh = 1.0 - 0.5 * (kd / (roller_r * 1.05))
                        rc = mix(gold_dark, gold, max(0.0, min(1.0, sh)))
                        r, g, b = rc

            px[i] = max(0, min(255, r))
            px[i + 1] = max(0, min(255, g))
            px[i + 2] = max(0, min(255, b))
            px[i + 3] = a

    return downsample(px, S, size)


def downsample(px, S, size):
    out = bytearray(size * size * 4)
    f = SS
    for y in range(size):
        for x in range(size):
            r = g = b = a = 0
            for dy in range(f):
                for dx in range(f):
                    si = ((y * f + dy) * S + (x * f + dx)) * 4
                    r += px[si]; g += px[si + 1]; b += px[si + 2]; a += px[si + 3]
            n = f * f
            oi = (y * size + x) * 4
            out[oi] = r // n
            out[oi + 1] = g // n
            out[oi + 2] = b // n
            out[oi + 3] = a // n
    return out


def write_png(path, rgba, size):
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        crc = zlib.crc32(typ + data) & 0xFFFFFFFF
        return c + struct.pack(">I", crc)

    raw = bytearray()
    stride = size * 4
    for y in range(size):
        raw.append(0)  # filter: none
        raw.extend(rgba[y * stride:(y + 1) * stride])

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as f:
        f.write(sig)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", idat))
        f.write(chunk(b"IEND", b""))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    targets = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-512.png", 512, True),
        ("apple-touch-icon.png", 180, True),
    ]
    for name, size, mask in targets:
        rgba = draw(size, maskable=mask)
        write_png(os.path.join(OUT_DIR, name), rgba, size)
        print("wrote", name)


if __name__ == "__main__":
    main()
