#!/usr/bin/env python3
"""One picture of Saturday 21 November 2026, drawn from nothing but code.

This program paints a newspaper front page into a pixel buffer using
only the Python standard library. A 5x7 bitmap alphabet lives here as
integers (five bits per row), seven flat-colour pictograms illustrate
the stories, and a small PNG writer turns the buffer into bytes. The
stories are the day's biggest, checked against reporting published
on 21 November 2026 (AP, SCMP, The Times, Dawn, The Hindu, Straits
Times, Breitbart, Manila Times, Japan Times): Russian missiles came
down in Poland during the overnight assault on Ukraine, a magnitude
6.9 earthquake shook Peru's Andes at 00:09 UTC, EU leaders demanded
a seat at the Ukraine talks, the Houthis vowed more strikes on Saudi
Arabia, a US court jailed Nikhil Gupta for 19.5 years, a tanker was
hit a second time in the Strait of Hormuz, and Trump told Iran it
must make a "real deal". There is no network, no clock and no
randomness in here, so running the program twice produces the same
file byte for byte.

The page is 1024 by 1024: a masthead naming the day, a lead panel on
the missiles in Poland, six stories in a three-by-two grid, an "also
today" strip and a line naming the sources.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

INK = (22, 35, 58)
PAPER = (246, 241, 227)
TINTS = {
    "paper": PAPER, "ink": INK, "white": (255, 255, 255),
    "red": (179, 38, 30), "teal": (14, 110, 106),
    "navy": (29, 78, 137), "amber": (217, 142, 4),
    "green": (46, 125, 50), "purple": (91, 75, 138),
    "grey": (112, 116, 120), "cream": (232, 222, 196),
    "rose": (244, 214, 210), "mint": (205, 232, 228),
    "sky": (210, 224, 240), "sand": (248, 232, 196),
    "leaf": (214, 236, 214), "lilac": (226, 220, 240),
    "pine": (27, 94, 32), "dusk": (52, 58, 84),
}

# ------------------------------------------------------------------ alphabet
# 5x7 bitmap alphabet: every glyph is seven integers, one per row, with
# bit 4 as the left column. Capitals, digits and the punctuation the
# page needs.
GLYPHS = {
    'A': (14, 17, 17, 31, 17, 17, 17),
    'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (14, 17, 16, 16, 16, 17, 14),
    'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31),
    'F': (31, 16, 16, 30, 16, 16, 16),
    'G': (14, 17, 16, 23, 17, 17, 15),
    'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (14, 4, 4, 4, 4, 4, 14),
    'J': (7, 2, 2, 2, 2, 18, 12),
    'K': (17, 18, 20, 24, 20, 18, 17),
    'L': (16, 16, 16, 16, 16, 16, 31),
    'M': (17, 27, 21, 21, 17, 17, 17),
    'N': (17, 25, 21, 19, 17, 17, 17),
    'O': (14, 17, 17, 17, 17, 17, 14),
    'P': (30, 17, 17, 30, 16, 16, 16),
    'Q': (14, 17, 17, 17, 21, 18, 13),
    'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30),
    'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14),
    'V': (17, 17, 17, 17, 17, 10, 4),
    'W': (17, 17, 17, 21, 21, 21, 10),
    'X': (17, 17, 10, 4, 10, 17, 17),
    'Y': (17, 17, 10, 4, 4, 4, 4),
    'Z': (31, 1, 2, 4, 8, 16, 31),
    '0': (14, 17, 19, 21, 25, 17, 14),
    '1': (4, 12, 4, 4, 4, 4, 14),
    '2': (14, 17, 1, 6, 8, 16, 31),
    '3': (30, 1, 1, 14, 1, 1, 30),
    '4': (2, 6, 10, 18, 31, 2, 2),
    '5': (31, 16, 30, 1, 1, 17, 14),
    '6': (14, 16, 16, 30, 17, 17, 14),
    '7': (31, 1, 2, 4, 8, 8, 8),
    '8': (14, 17, 17, 14, 17, 17, 14),
    '9': (14, 17, 17, 15, 1, 1, 14),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 12, 12),
    ',': (0, 0, 0, 0, 12, 4, 8),
    ':': (0, 12, 12, 0, 12, 12, 0),
    ';': (0, 12, 12, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '-': (0, 0, 0, 14, 0, 0, 0),
    '/': (1, 2, 2, 4, 8, 8, 16),
    '%': (25, 26, 2, 4, 8, 11, 19),
    '$': (4, 15, 20, 14, 5, 30, 4),
    '+': (0, 4, 4, 31, 4, 4, 0),
    '(': (2, 4, 8, 8, 8, 4, 2),
    ')': (8, 4, 2, 2, 2, 4, 8),
    '!': (4, 4, 4, 4, 4, 0, 4),
    '?': (14, 17, 1, 6, 4, 0, 4),
    '&': (12, 18, 20, 8, 21, 18, 13),
    '=': (0, 0, 31, 0, 31, 0, 0),
    '"': (10, 10, 10, 0, 0, 0, 0),
}

# ------------------------------------------------------------------ canvas
class Canvas:
    """An RGB pixel buffer with a handful of drawing primitives."""

    def __init__(self, width, height, colour):
        self.w, self.h = width, height
        self.buf = bytearray(width * height * 3)
        self.fill(0, 0, width, height, colour)

    def px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            off = (y * self.w + x) * 3
            self.buf[off:off + 3] = bytes(colour)

    def fill(self, x, y, w, h, colour):
        xa, ya = max(0, x), max(0, y)
        xb, yb = min(self.w, x + w), min(self.h, y + h)
        row = bytes(colour) * (xb - xa)
        for yy in range(ya, yb):
            off = (yy * self.w + xa) * 3
            self.buf[off:off + len(row)] = row

    def hline(self, x, y, w, colour, thick=1):
        self.fill(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.fill(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill(x0, y0, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            span = r * r - (yy - cy) ** 2
            half = int(span ** 0.5) if span >= 0 else 0
            self.fill(cx - half, yy, half * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=3):
        for k in range(thick):
            rr = r - k
            for deg in range(0, 360, 2):
                rad = math.radians(deg)
                self.px(cx + int(rr * math.cos(rad)),
                        cy + int(rr * math.sin(rad)), colour)

    def triangle(self, corners, colour):
        (x0, y0), (x1, y1), (x2, y2) = corners
        edges = (((x0, y0), (x1, y1)), ((x1, y1), (x2, y2)),
                 ((x2, y2), (x0, y0)))
        for y in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
            hits = []
            for (ax, ay), (bx, by) in edges:
                if ay != by and min(ay, by) <= y < max(ay, by):
                    hits.append(ax + (y - ay) * (bx - ax) // (by - ay))
            if len(hits) >= 2:
                self.fill(min(hits), y, max(hits) - min(hits) + 1, 1, colour)

    # -- lettering ---------------------------------------------------
    def text(self, x, y, s, scale, colour, align="left"):
        s = s.upper()
        step = 6 * scale
        total = len(s) * step - scale
        if align == "center":
            x -= total // 2
        elif align == "right":
            x -= total
        for pos, ch in enumerate(s):
            rows = GLYPHS.get(ch, GLYPHS[' '])
            ox = x + pos * step
            for row in range(7):
                bits = rows[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.fill(ox + col * scale, y + row * scale,
                                  scale, scale, colour)
        return total

    def wrap(self, s, width):
        out, cur = [], ""
        for word in s.upper().split():
            if cur and len(cur) + 1 + len(word) > width:
                out.append(cur)
                cur = word
            else:
                cur = (cur + " " + word).strip()
        if cur:
            out.append(cur)
        return out


def encode_png(cv):
    """Encode the canvas as a PNG: signature, IHDR, one IDAT, IEND."""
    def chunk(tag, data):
        body = struct.pack(">I", len(data)) + tag + data
        return body + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    stride = cv.w * 3
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    blob = zlib.compress(bytes(raw), 6)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", blob) + chunk(b"IEND", b""))

# ------------------------------------------------------------------ pictures
def pic_missile(cv, x, y, w, h):
    """A cruise missile streaking down over a field at dusk."""
    cv.fill(x, y, w, h, TINTS["dusk"])
    for k in range(20):
        cv.px(x + 12 + (k * 97) % (w - 24), y + 6 + (k * 31) % 16,
              (150, 160, 200))
    cv.fill(x, y + h - 18, w, 18, (58, 48, 36))
    cx, cy = x + w // 2, y + h // 2 - 6
    cv.line(cx - 58, cy - 26, cx + 44, cy + 16, TINTS["amber"], 5)
    cv.triangle([(cx + 44, cy + 16), (cx + 62, cy + 26), (cx + 38, cy + 30)],
                TINTS["red"])
    cv.triangle([(cx - 58, cy - 26), (cx - 40, cy - 30), (cx - 44, cy - 12)],
                TINTS["white"])
    cv.circle(cx + 66, cy + 28, 9, (255, 180, 60))
    cv.circle(cx + 66, cy + 28, 4, TINTS["red"])
    cv.circle(cx - 66, cy - 34, 4, TINTS["white"])


def pic_quake(cv, x, y, w, h):
    """A cracked mountainside: the Andes shake."""
    cv.fill(x, y, w, h, TINTS["sand"])
    cx = x + w // 2
    cv.triangle([(x + 8, y + h - 22), (cx - 40, y + 22), (cx + 6, y + h - 22)],
                (120, 110, 88))
    cv.triangle([(cx - 6, y + h - 22), (cx + 44, y + 14), (x + w - 8, y + h - 22)],
                (96, 88, 70))
    cv.fill(x, y + h - 22, w, 22, (70, 60, 46))
    cv.line(cx - 30, y + h - 22, cx - 18, y + h - 8, INK, 3)
    cv.line(cx - 18, y + h - 8, cx + 2, y + h - 16, INK, 3)
    cv.line(cx + 2, y + h - 16, cx + 16, y + h - 6, INK, 3)
    cv.line(cx + 16, y + h - 6, cx + 34, y + h - 14, INK, 3)
    cv.fill(cx - 58, y + 30, 26, 34, TINTS["white"])
    cv.fill(cx - 52, y + 36, 5, 5, INK)
    cv.fill(cx - 42, y + 36, 5, 5, INK)
    cv.fill(cx - 52, y + 48, 5, 5, INK)
    cv.fill(cx + 34, y + 26, 24, 30, TINTS["white"])
    cv.line(cx + 34, y + 26, cx + 58, y + 56, TINTS["red"], 3)


def pic_summit(cv, x, y, w, h):
    """Three flags behind a table for the Berlin talks."""
    cv.fill(x, y, w, h, TINTS["navy"])
    cv.fill(x, y + h - 16, w, 16, (18, 52, 96))
    for k, colour in enumerate((TINTS["amber"], TINTS["white"], TINTS["red"])):
        pole = x + 66 + k * 84
        cv.vline(pole, y + 12, 52, TINTS["white"], 3)
        cv.triangle([(pole + 3, y + 12), (pole + 52, y + 24),
                     (pole + 3, y + 36)], colour)
    cv.fill(x + 40, y + h - 30, w - 80, 8, (210, 190, 150))
    cv.fill(x + 52, y + h - 22, 10, 8, (120, 90, 60))
    cv.fill(x + w - 62, y + h - 22, 10, 8, (120, 90, 60))


def pic_rocket(cv, x, y, w, h):
    """A rocket climbing over desert, met by an interceptor."""
    cv.fill(x, y, w, h, TINTS["sky"])
    cv.fill(x, y + h - 16, w, 16, (190, 160, 110))
    cx, cy = x + w // 2, y + h // 2
    cv.line(cx - 40, cy + 34, cx - 18, cy - 30, TINTS["white"], 4)
    cv.triangle([(cx - 18, cy - 30), (cx - 8, cy - 44), (cx + 2, cy - 28)],
                TINTS["red"])
    cv.triangle([(cx - 20, cy - 20), (cx - 34, cy - 2), (cx - 16, cy - 6)],
                TINTS["red"])
    cv.circle(cx - 44, cy + 38, 6, (255, 180, 60))
    cv.line(cx + 52, cy + 30, cx + 30, cy - 18, TINTS["amber"], 4)
    cv.circle(cx + 28, cy - 20, 5, TINTS["amber"])
    cv.circle(cx + 28, cy - 20, 2, TINTS["red"])


def pic_gavel(cv, x, y, w, h):
    """A judge's gavel for the US court sentence."""
    cv.fill(x, y, w, h, TINTS["lilac"])
    cx, cy = x + w // 2, y + h // 2
    cv.fill(cx - 58, cy - 34, 62, 20, (90, 66, 36))
    cv.fill(cx - 58, cy - 40, 62, 6, (120, 90, 50))
    cv.line(cx - 28, cy - 14, cx + 34, cy + 28, (120, 90, 50), 7)
    cv.fill(cx - 44, cy + 30, 92, 6, (70, 52, 28))


def pic_tanker(cv, x, y, w, h):
    """An LPG tanker burning in the Strait of Hormuz."""
    cv.fill(x, y, w, h, TINTS["sand"])
    cv.fill(x, y + h - 30, w, 30, TINTS["navy"])
    for k in range(5):
        cv.hline(x + 10 + k * 60, y + h - 22, 34, TINTS["white"], 2)
    cx, cy = x + w // 2, y + h // 2 - 4
    cv.fill(cx - 92, cy - 4, 184, 22, (120, 40, 30))
    cv.fill(cx + 52, cy - 26, 26, 24, (90, 30, 22))
    cv.vline(cx + 64, cy - 38, 14, INK, 3)
    cv.triangle([(cx - 30, cy - 4), (cx - 14, cy - 30), (cx + 2, cy - 4)],
                TINTS["amber"])
    cv.triangle([(cx + 6, cy - 4), (cx + 18, cy - 26), (cx + 32, cy - 4)],
                TINTS["red"])
    cv.circle(cx - 22, cy - 32, 5, (255, 180, 60))


def pic_ship(cv, x, y, w, h):
    """A warship on blockade patrol."""
    cv.fill(x, y, w, h, TINTS["mint"])
    cv.fill(x, y + h - 26, w, 26, TINTS["navy"])
    for k in range(5):
        cv.hline(x + 12 + k * 58, y + h - 18, 32, TINTS["white"], 2)
    cx, cy = x + w // 2, y + h // 2
    cv.fill(cx - 96, cy - 6, 192, 18, (70, 80, 96))
    cv.fill(cx - 60, cy - 30, 70, 24, (90, 100, 118))
    cv.vline(cx - 30, cy - 48, 20, INK, 3)
    cv.triangle([(cx - 30, cy - 48), (cx - 2, cy - 40), (cx - 30, cy - 32)],
                TINTS["red"])
    cv.fill(cx + 30, cy - 22, 14, 16, (50, 58, 72))
    cv.fill(cx + 78, cy - 14, 18, 8, (50, 58, 72))


PICS = {"missile": pic_missile, "quake": pic_quake, "summit": pic_summit,
        "rocket": pic_rocket, "gavel": pic_gavel, "tanker": pic_tanker,
        "ship": pic_ship}

# ------------------------------------------------------------------ stories
# Every story is one tuple: kicker, picture key, panel tint, headline
# lines (already wrapped, at most 12 characters each at scale 4) and a
# one-line summary the renderer wraps itself.
STORIES = [
    ("DISASTER - PERU", "quake", "sand",
     ("M6.9 QUAKE", "SHAKES PERU", "ANDES"),
     "00:09 UTC; FELT IN LIMA; NO CASUALTIES REPORTED"),
    ("DIPLOMACY - BERLIN", "summit", "sky",
     ("EU DEMANDS", "SEAT AT", "THE TALKS"),
     "UKRAINE TALKS; 1 BN EURO AID FOR KYIV"),
    ("CONFLICT - RIYADH", "rocket", "rose",
     ("HOUTHIS VOW", "MORE SAUDI", "STRIKES"),
     "TWO MISSILES DOWN OVER JAZAN; AIRLINES WARNED OFF"),
    ("US - NEW YORK", "gavel", "lilac",
     ("GUPTA JAILED", "19.5 YEARS", "IN PLOT"),
     "SENTENCED FOR MURDER PLOT AGAINST SIKH ACTIVIST"),
    ("GULF - HORMUZ", "tanker", "sand",
     ("2ND ATTACK", "ON LPG", "TANKER"),
     "TARA GAS HIT AGAIN; ONE INDIAN SEAFARER MISSING"),
    ("US - WASHINGTON", "ship", "mint",
     ("TRUMP: IRAN", "MUST MAKE A", "REAL DEAL"),
     "BLOCKADE HOLDS; NO RUSH ON NEW STRIKES"),
]

ALSO = [
    "COP31: CRUNCH TIME, NO AGREEMENT IN SIGHT",
    "DENMARK CHARGES TWO OVER RUSSIAN PLOT TO KILL UKRAINIAN",
    "BOLSONARO IN HOSPITAL WITH ABDOMINAL PAIN",
    "HONDA RECALLS 810,000 US CARS OVER TAKATA AIR BAGS",
]

# ------------------------------------------------------------------ page
def border(cv, x, y, w, h):
    """A double-ruled ink border around a panel."""
    for t in range(2):
        cv.hline(x, y + t, w, INK)
        cv.hline(x, y + h - 1 - t, w, INK)
        cv.vline(x + t, y, h, INK)
        cv.vline(x + w - 1 - t, y, h, INK)


def lead_panel(cv, x, y, w, h):
    cv.fill(x, y, w, h, TINTS["sky"])
    border(cv, x, y, w, h)
    pic_missile(cv, x + 2, y + 2, 220, h - 4)
    tx = x + 242
    cv.text(tx, y + 14, "EUROPE - POLAND", 2, TINTS["red"])
    cv.text(tx, y + 38, "RUSSIAN MISSILES", 5, INK)
    cv.text(tx, y + 80, "LAND IN POLAND", 5, TINTS["red"])
    cv.text(tx, y + 128, "TUSK: DELIBERATE PROVOCATION; NATO: GRAVE", 2, INK)
    cv.text(tx, y + 148, "VIOLATION; KH-101 DOWN 50 KM FROM BORDER", 2, INK)


def story_panel(cv, x, y, w, h, story):
    kicker, pic, tint, head, summary = story
    cv.fill(x, y, w, h, TINTS[tint])
    border(cv, x, y, w, h)
    PICS[pic](cv, x + 2, y + 2, w - 4, 88)
    cv.text(x + 14, y + 98, kicker, 2, TINTS["red"])
    yy = y + 120
    for line in head:
        cv.text(x + 14, yy, line, 4, INK)
        yy += 32
    for line in cv.wrap(summary, 24):
        cv.text(x + 14, yy, line, 2, INK)
        yy += 15


def build_page():
    cv = Canvas(W, H, PAPER)
    grey, amber = TINTS["grey"], TINTS["amber"]
    cv.text(W // 2, 26, "THE WORLD IN ONE DAY", 3, grey, "center")
    cv.text(W // 2, 56, "SATURDAY, 21 NOVEMBER 2026", 6, INK, "center")
    cv.hline(28, 116, W - 56, INK, 4)
    cv.hline(28, 124, W - 56, INK)

    lead_panel(cv, 28, 134, W - 56, 176)

    cw, ch, gap = 312, 268, 15
    for n, story in enumerate(STORIES):
        px = 28 + (n % 3) * (cw + gap)
        py = 322 + (n // 3) * (ch + 8)
        story_panel(cv, px, py, cw, ch, story)

    ty = 878
    cv.fill(28, ty, W - 56, 112, INK)
    cv.text(48, ty + 12, "ALSO TODAY", 3, amber)
    for k, item in enumerate(ALSO):
        ix = 48 + (k % 2) * 484
        iy = ty + 44 + (k // 2) * 34
        cv.fill(ix, iy + 3, 10, 10, amber)
        for j, line in enumerate(cv.wrap(item, 36)[:2]):
            cv.text(ix + 18, iy + j * 15, line, 2, TINTS["white"])

    cv.hline(28, 1000, W - 56, INK)
    cv.text(W // 2, 1008,
            "REPORTED ON 21 NOVEMBER 2026 - AP, SCMP, THE TIMES, "
            "DAWN, THE HINDU",
            2, grey, "center")
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "entry.png"), "wb") as fh:
        fh.write(encode_png(build_page()))


if __name__ == "__main__":
    main()
