#!/usr/bin/env python3
"""The Daily Ledger - one front page for Saturday 21 November 2026.

Pure standard library. A small 5x7 bitmap font and a minimal PNG
encoder draw a 1024x1024 newspaper front page and write entry.png
next to this file. The output is deterministic: fixed layout, fixed
zlib level, no timestamps, so two runs give byte-identical files.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (24, 22, 18)
GREY = (96, 91, 80)
RED = (150, 30, 24)
FAINT = (214, 207, 190)

# 5x7 glyphs, seven rows of five bits, '1' is ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

# Characters that reuse another glyph.
ALIASES = {
    "’": "'", "‘": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "·": ".", "•": ".",
}


def glyph(ch):
    ch = ALIASES.get(ch, ch)
    return FONT.get(ch, FONT["?"])


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set_px(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    cx = x
    for ch in text:
        rows = glyph(ch)
        for r in range(7):
            bits = rows[r]
            for c in range(5):
                if bits[c] == "1":
                    cv.rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(cv, y, text, scale, color):
    x = (cv.w - text_width(text, scale)) // 2
    draw_text(cv, x, y, text, scale, color)


def draw_right(cv, right, y, text, scale, color):
    draw_text(cv, right - text_width(text, scale), y, text, scale, color)


def wrap(text, scale, max_width):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(cv, x, y, text, scale, color, max_width, leading):
    for line in wrap(text, scale, max_width):
        draw_text(cv, x, y, line, scale, color)
        y += leading
    return y


def save_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


LEAD_BODY_LEFT = (
    "Russian missiles struck Polish territory, Warsaw confirmed, in "
    "the gravest spillover yet of the war in Ukraine onto NATO soil. "
    "Polish forces moved to high alert and the government called an "
    "emergency sitting."
)
LEAD_BODY_RIGHT = (
    "Alliance capitals weighed their response. Kyiv renewed its call "
    "for partners to shield Ukrainian skies, while Moscow denied "
    "targeting Poland. The alliance must now say where its own "
    "line sits."
)
QUAKE_BODY = (
    "A magnitude 6.9 earthquake struck Peru, shaking buildings and "
    "sending residents into the streets. Officials began damage "
    "assessments as aftershocks rolled on, with rescue teams sent "
    "to the worst-hit towns."
)
EU_BODY = (
    "European leaders secured a seat at the Ukraine peace talks "
    "after weeks of pressing to be heard, putting Brussels inside "
    "the room as settlement terms are drafted."
)
HOUTHI_BODY = (
    "Yemen's Houthi movement vowed further strikes against Saudi "
    "targets, raising fresh fears for shipping and energy supplies "
    "across the region."
)
HORMUZ_BODY = (
    "A second tanker was attacked in the Strait of Hormuz, the "
    "chokepoint carrying a fifth of the world's oil. Naval escorts "
    "along the route were stepped up."
)
GUPTA_BODY = (
    "Gupta was sentenced to nineteen years and six months in a "
    "fraud case prosecutors called one of the largest of its kind."
)
TRUMP_BODY = (
    "President Trump declared the emerging Iran agreement 'the "
    "real deal' as negotiators worked through the final sticking "
    "points."
)
GLANCE = (
    "- Poland: alliance meets",
    "- Peru: rescue teams move",
)


def story(cv, x, y, w, kicker, headline, scale, body, body_w=None):
    draw_text(cv, x, y, kicker, 2, RED)
    y += 22
    for line in wrap(headline, scale, w):
        draw_text(cv, x, y, line, scale, INK)
        y += 7 * scale + 6
    y += 4
    return draw_paragraph(cv, x, y, body, 2, INK, body_w or w, 20)


def build():
    cv = Canvas(W, H, PAPER)
    margin = 36
    right_edge = W - margin

    cv.hline(margin, 26, W - 2 * margin, INK, 2)
    draw_centered(cv, 42, "THE DAILY LEDGER", 9, INK)
    draw_text(cv, margin, 122, "SATURDAY, NOVEMBER 21, 2026", 2, GREY)
    draw_right(cv, right_edge, 122, "ONE IMAGE - ALL THE NEWS", 2, GREY)
    cv.hline(margin, 148, W - 2 * margin, INK, 4)
    cv.hline(margin, 155, W - 2 * margin, INK, 1)

    # Lead story, left of the rail.
    lead_w = 600
    draw_text(cv, margin, 172, "EUROPE - THE WAR WIDENS", 2, RED)
    y = 200
    for line in ("RUSSIAN MISSILES", "FALL ON POLAND"):
        draw_text(cv, margin, y, line, 6, INK)
        y += 48
    draw_text(cv, margin, y + 2, "FROM THE LEDGER WIRE DESK", 2, GREY)
    body_y = y + 30
    col_w = 292
    draw_paragraph(cv, margin, body_y, LEAD_BODY_LEFT, 2, INK, col_w, 20)
    draw_paragraph(cv, margin + col_w + 16, body_y, LEAD_BODY_RIGHT,
                   2, INK, col_w, 20)

    # Right rail: the earthquake, then at-a-glance lines.
    rail_x = 676
    rail_w = right_edge - rail_x
    cv.vline(rail_x - 20, 172, 360, FAINT, 2)
    ry = story(cv, rail_x, 172, rail_w, "EARTHQUAKE",
               "M6.9 QUAKE ROCKS PERU", 4, QUAKE_BODY)
    ry += 14
    cv.hline(rail_x, ry, rail_w, INK, 1)
    ry += 12
    draw_text(cv, rail_x, ry, "AT A GLANCE", 2, RED)
    ry += 24
    for item in GLANCE:
        draw_text(cv, rail_x, ry, item, 2, INK)
        ry += 21

    cv.hline(margin, 546, W - 2 * margin, INK, 2)

    # Middle band: three columns.
    mid_y = 562
    col1 = margin
    col2 = 356
    col3 = 676
    story(cv, col1, mid_y, 304, "DIPLOMACY",
          "EU WINS SEAT AT UKRAINE TALKS", 3, EU_BODY)
    story(cv, col2, mid_y, 304, "MIDDLE EAST",
          "HOUTHIS VOW MORE SAUDI STRIKES", 3, HOUTHI_BODY)
    story(cv, col3, mid_y, 312, "SHIPPING",
          "SECOND TANKER HIT IN HORMUZ", 3, HORMUZ_BODY)
    cv.vline(col2 - 18, mid_y, 228, FAINT, 2)
    cv.vline(col3 - 18, mid_y, 228, FAINT, 2)

    cv.hline(margin, 800, W - 2 * margin, INK, 2)

    # Bottom band: two halves.
    bot_y = 816
    half = (W - 2 * margin - 32) // 2
    story(cv, margin, bot_y, half, "THE COURTS",
          "GUPTA GETS 19.5 YEARS", 3, GUPTA_BODY)
    story(cv, margin + half + 32, bot_y, half, "WASHINGTON",
          "TRUMP HAILS IRAN DEAL", 3, TRUMP_BODY)

    cv.hline(margin, 984, W - 2 * margin, INK, 1)
    draw_centered(cv, 992, "ALSO TODAY - MARKETS MIXED - COASTAL STORM "
                           "WARNINGS - TITLE RACE TIGHTENS", 2, GREY)
    return cv


def main():
    cv = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    size = save_png(cv, out)
    print("wrote %s (%d bytes, %dx%d)" % (out, size, W, H))


if __name__ == "__main__":
    main()
