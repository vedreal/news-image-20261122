#!/usr/bin/env python3
"""News-image entry for make.fun competition news-image-20261122.

Sums up Sunday 22 November 2026's world news in one 1024x1024
image, drawn from scratch with the Python standard library only
(zlib PNG encoder + a built-in 5x7 bitmap font). No network, no
files read, no randomness: two runs write byte-identical output.

The news was gathered on 22 Nov 2026 from that day's reporting:

  * Mexican special forces captured drug kingpin Fausto Isidro
    Meza Flores, known as El Chapo Isidro, in a raid in Sinaloa;
    11 were killed in violence after the capture.
  * Russia launched 400 drones and 110 missiles at Ukraine in one
    of the war's largest attacks; at least two killed; a ballistic
    missile hit Zelensky's hometown; a Russian missile crashed in
    Poland, Warsaw flags provocation.
  * Drones hit a Russian cargo ship in the Gulf of Finland; the
    ship caught fire; Finland tightens security.
  * Iran struck a US air base in Kuwait and targeted Bahrain;
    tankers were hit off the Oman coast; Trump says he wants a
    permanent nuclear accord with Iran.
  * A magnitude 6.7-6.9 earthquake shook the Andes in central
    Peru; no immediate casualties or damage reported.
  * Also in the footer: COP31 deadlocked over fossil fuels; the
    FBI investigates an apparent hack of its criminal database;
    tech stocks slide as Anthropic shares fall; Eisenkot invites
    Netanyahu's Likud to coalition talks; Bolsonaro admitted to
    ICU with acute bowel obstruction; France's sixth Saturday of
    protests with lower turnout.

Layout: a newspaper front page with a clear hierarchy. Masthead
names the day; a full-width lead (the Sinaloa capture, biggest
headline) with a handcuffs drawing; a second full-width story
(Russia's massive attack) with a skyline-under-attack drawing; a
row of three mid stories with pictograms (Baltic ship, Gulf
escalation, Peru quake); and an "ALSO" footer carrying the rest
of the day.
"""

import hashlib, math, os, struct, zlib

W = H = 1024

PAPER, INK, NAVY = (247, 243, 232), (26, 26, 26), (22, 40, 63)
RED, GOLD, BLUE = (176, 42, 32), (201, 162, 39), (47, 93, 140)
GREEN, ORANGE, GREY = (46, 125, 74), (214, 106, 32), (120, 116, 104)
LIGHT = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. One glyph per line: the character, then its 7 rows
# of 5 characters ('#' = ink). The parser below turns each glyph into
# a list of ink-pixel (column, row) offsets, so the renderer stamps
# precomputed points instead of scanning rows.
FONT_SRC = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .###. #...# #.... #.... #.... #...# .###.
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .###. #...# #.... #.### #...# #...# .####
H #...# #...# #...# ##### #...# #...# #...#
I .###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.
J ..### ...#. ...#. ...#. ...#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #...# ##..# #.#.# #..## #...# #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# ##.## #...#
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
a ..... ..... .###. ....# .#### #...# .####
b #.... #.... ####. #...# #...# #...# ####.
c ..... ..... .###. #.... #.... #...# .###.
d ....# ....# .#### #...# #...# #...# .####
e ..... ..... .###. #...# ##### #.... .###.
f ..##. .#..# .#... ####. .#... .#... .#...
g ..... .#### #...# #...# .#### ....# .###.
h #.... #.... ####. #...# #...# #...# #...#
i ..#.. ..... .##.. ..#.. ..#.. ..#.. .###.
j ...#. ..... ..##. ...#. ...#. #..#. .##..
k #.... #.... #..#. #.#.. ##... #.#.. #..#.
l .##.. ..#.. ..#.. ..#.. ..#.. ..#.. .###.
m ..... ..... ##.#. #.#.# #.#.# #.#.# #.#.#
n ..... ..... ####. #...# #...# #...# #...#
o ..... ..... .###. #...# #...# #...# .###.
p ..... ..... ####. #...# ####. #.... #....
q ..... ..... .#### #...# .#### ....# ....#
r ..... ..... #.##. ##..# #.... #.... #....
s ..... ..... .#### #.... .###. ....# ####.
t .#... .#... ###.. .#... .#... .#.#. ..#..
u ..... ..... #...# #...# #...# #..## .##.#
v ..... ..... #...# #...# #...# .#.#. ..#..
w ..... ..... #...# #.#.# #.#.# #.#.# .#.#.
x ..... ..... #...# .#.#. ..#.. .#.#. #...#
y ..... ..... #...# #...# .#### ....# .###.
z ..... ..... ##### ...#. ..#.. .#... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ..##. .#... #.... #####
3 ##### ...#. ..#.. ...#. ....# #...# .###.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 ..##. .#... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ...#. .##..
. ..... ..... ..... ..... ..... .##.. .##..
, ..... ..... ..... ..... .##.. ..#.. .#...
: ..... .##.. .##.. ..... .##.. .##.. .....
; ..... .##.. .##.. ..... .##.. ..#.. .#...
! ..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..
? .###. #...# ....# ..##. ..#.. ..... ..#..
- ..... ..... ..... ##### ..... ..... .....
' ..#.. ..#.. .#... ..... ..... ..... .....
( ...#. ..#.. .#... .#... .#... ..#.. ...#.
) .#... ..#.. ...#. ...#. ...#. ..#.. .#...
% ##..# ##.#. ...#. ..#.. .#... #.##. #..##
$ ..#.. .#### #.#.. .###. ..#.# ####. ..#..
/ ....# ...#. ...#. ..#.. .#... .#... #....
+ ..... ..#.. ..#.. ##### ..#.. ..#.. .....
= ..... ..... ##### ..... ##### ..... .....
" .#.#. .#.#. ..... ..... ..... ..... .....
& .##.. #..#. #.#.. .#... #.#.# #..#. .##.#
* ..... .#.#. ..#.. ##### ..#.. .#.#. .....
_ ..... ..... ..... ..... ..... ..... #####
• ..... ..... .##.. .##.. ..... ..... .....
"""


def _parse_font(src):
    """Turn the FONT_SRC block into {character: [(col, row), ...]}."""
    font = {}
    for line in src.strip().split("\n"):
        parts = line.split()
        ch, rows = parts[0], parts[1:]
        font[ch] = [(c, r) for r, row in enumerate(rows)
                    for c, bit in enumerate(row) if bit == "#"]
    font[" "] = []
    return font


FONT = _parse_font(FONT_SRC)

BULLET = '•'

_CLEAN_TABLE = str.maketrans({
    "’": "'", "‘": "'", "—": "-", "–": "-", "€": "E",
})


def _clean(text):
    """Normalise to the glyphs the font holds."""
    return text.translate(_CLEAN_TABLE)


def text_width(text, scale):
    return (len(_clean(text)) * 6 - 1) * scale


def wrap(text, max_chars):
    """Greedy word wrap to lines of at most max_chars characters."""
    words = _clean(text).split(" ")
    lines = []
    line = ""
    for word in words:
        trial = word if not line else line + " " + word
        if line and len(trial) > max_chars:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


class Canvas:
    """An RGB raster with tiny vector helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return
        i = (y * self.w + x) * 3
        self.px[i] = color[0]
        self.px[i + 1] = color[1]
        self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = x if x > 0 else 0
        y0 = y if y > 0 else 0
        x1 = x + w if x + w < self.w else self.w
        y1 = y + h if y + h < self.h else self.h
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, t=2):
        for k in range(t):
            self.hline(x, y + k, w, color)
            self.hline(x, y + h - 1 - k, w, color)
            self.vline(x + k, y, h, color)
            self.vline(x + w - 1 - k, y, h, color)

    def hline(self, x, y, length, color, t=1):
        for k in range(t):
            self.fill_rect(x, y + k, length, 1, color)

    def vline(self, x, y, length, color, t=1):
        for k in range(t):
            self.fill_rect(x + k, y, 1, length, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line, t = thickness in pixels."""
        dx = x1 - x0
        dy = y1 - y0
        sx = 1 if dx >= 0 else -1
        sy = 1 if dy >= 0 else -1
        dx, dy = abs(dx), abs(dy)
        err = dx - dy
        while True:
            self._dot(x0, y0, color, t)
            if x0 == x1 and y0 == y1:
                return
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def _dot(self, x, y, color, t):
        for a in range(t):
            for b in range(t):
                self.set(x + a - t // 2, y + b - t // 2, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.set(cx + dx, cy + dy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via horizontal scanlines."""
        verts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = verts
        for y in range(ay, cy + 1):
            f_top = (y - ay) / (by - ay) if by > ay else 0
            f_all = (y - ay) / (cy - ay) if cy > ay else 0
            xa = ax + (bx - ax) * f_top
            xb = ax + (cx - ax) * f_all
            if y >= by:
                f_bot = (y - by) / (cy - by) if cy > by else 0
                xa = bx + (cx - bx) * f_bot
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            self.fill_rect(int(lo), y, int(hi - lo) + 1, 1, color)

    def text(self, x, y, s, scale, color):
        s = _clean(s)
        cx = x
        for ch in s:
            for dx, dy in FONT.get(ch, FONT["?"]):
                self.fill_rect(cx + dx * scale, y + dy * scale,
                               scale, scale, color)
            cx += 6 * scale
        return cx - x - scale

    def text_centred(self, cx, y, s, scale, color):
        half = text_width(s, scale) // 2
        return self.text(cx - half, y, s, scale, color)

    def paragraph(self, x, y, s, scale, color, max_chars, leading=None):
        step = leading if leading is not None else 9 * scale
        for i, line in enumerate(wrap(s, max_chars)):
            self.text(x, y + i * step, line, scale, color)


def to_png(c):
    """Encode the canvas as a PNG (zlib-compressed, no filters)."""
    def chunk(tag, data):
        crc = zlib.crc32(tag)
        crc = zlib.crc32(data, crc)
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc & 0xffffffff)

    raw = bytearray()
    for y in range(c.h):
        raw.append(0)
        raw.extend(c.px[y * c.w * 3:(y + 1) * c.w * 3])
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ------------------------------------------------------------- pictograms
def pic_capture(c, x, y, w, h):
    """Handcuffs: two gold rings joined by a chain, in a big box."""
    cx = x + w // 2
    cy = y + h // 2 + 6
    # chain links across the top of the rings
    for i in range(5):
        lx = cx - 56 + i * 28
        c.circle(lx, cy - 46, 7, NAVY)
        c.circle(lx, cy - 46, 3, GOLD)
    # the two rings
    for rx in (cx - 62, cx + 62):
        c.circle(rx, cy, 44, GOLD)
        c.circle(rx, cy, 30, PAPER)
        c.circle(rx, cy, 30, GOLD)  # re-ring: keeps the band thick
        c.circle(rx, cy, 22, PAPER)
        c.fill_rect(rx - 8, cy - 52, 16, 12, NAVY)  # cuff hinge
    # base bar
    c.fill_rect(cx - 118, cy + 52, 236, 8, NAVY)


def pic_strike(c, x, y, w, h):
    """A city skyline under missile attack: buildings, a bridge,
    explosion starbursts and incoming missile streaks."""
    base = y + h - 8
    heights = [52, 78, 44, 96, 60, 88, 40, 70]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + 4 + i * bw
        c.fill_rect(bx, base - hh, bw - 3, hh, NAVY)
    # bridge deck across the lower middle, in front of the skyline
    c.fill_rect(x + 8, base - 26, w - 16, 5, INK)
    for px in (x + 30, x + w // 2 - 4, x + w - 38):
        c.fill_rect(px, base - 44, 8, 18, INK)
    # explosion starbursts above the skyline
    for (ex, ey, r) in ((x + w // 2 - 30, y + 30, 16),
                        (x + w - 46, y + 58, 12)):
        for k in range(8):
            a = math.radians(k * 45 + 12)
            c.line(ex, ey, int(ex + r * math.cos(a)),
                   int(ey + r * math.sin(a)), ORANGE, 3)
        c.circle(ex, ey, 8, RED)
        c.circle(ex, ey, 4, GOLD)
    # incoming missile streaks from the top right
    c.line(x + w - 8, y + 2, x + w // 2 - 24, y + 26, RED, 3)
    c.line(x + w - 30, y + 2, x + w - 52, y + 52, RED, 3)


def pic_ship(c, x, y, w, h):
    """A cargo ship on fire: hull, superstructure, smokestack with
    flames and smoke, drawn in a short (70px) box."""
    base = y + h - 6
    # hull: long navy body with a pointed bow
    c.fill_rect(x + 14, base - 16, w - 52, 16, NAVY)
    c.triangle(x + w - 38, base - 16, x + w - 6, base - 16,
               x + w - 6, base, NAVY)
    c.fill_rect(x + 14, base - 16, w - 52, 3, GOLD)
    # superstructure and smokestack
    c.fill_rect(x + 30, base - 30, 34, 14, LIGHT)
    c.rect(x + 30, base - 30, 34, 14, NAVY, 2)
    c.fill_rect(x + 96, base - 34, 12, 18, INK)
    # flames above the stack
    for k in range(6):
        a = math.radians(k * 60)
        c.line(x + 102, base - 34, int(x + 102 + 11 * math.cos(a)),
               int(base - 34 + 11 * math.sin(a)), ORANGE, 2)
    c.circle(x + 102, base - 34, 5, RED)
    c.circle(x + 102, base - 34, 2, GOLD)
    # smoke puffs drifting up
    c.circle(x + 116, base - 44, 5, GREY)
    c.circle(x + 128, base - 52, 4, GREY)
    # water line
    c.hline(x + 6, base + 2, w - 12, BLUE, 2)


def pic_tanker(c, x, y, w, h):
    """An oil tanker under attack: low hull, round storage tanks,
    a missile streak from the top right, drawn in a short box."""
    base = y + h - 6
    # hull
    c.fill_rect(x + 14, base - 14, w - 40, 14, NAVY)
    c.triangle(x + w - 26, base - 14, x + w - 6, base - 14,
               x + w - 6, base, NAVY)
    # three round storage tanks on deck
    for i in range(3):
        tx = x + 44 + i * 56
        c.circle(tx, base - 22, 13, LIGHT)
        c.circle(tx, base - 22, 13, NAVY)  # ring
        c.circle(tx, base - 22, 9, LIGHT)
    # small bridge tower at the stern
    c.fill_rect(x + 20, base - 30, 12, 16, INK)
    # missile streak from the top right with a burst at its head
    c.line(x + w - 6, y + 2, x + w - 74, y + 30, RED, 3)
    for k in range(6):
        a = math.radians(k * 60)
        c.line(x + w - 74, y + 30, int(x + w - 74 + 10 * math.cos(a)),
               int(y + 30 + 10 * math.sin(a)), ORANGE, 2)
    c.circle(x + w - 74, y + 30, 5, GOLD)
    # water line
    c.hline(x + 6, base + 2, w - 12, BLUE, 2)


def pic_quake(c, x, y, w, h):
    """Andes mountains split by a quake: two peaks, a red zigzag
    crack, tremor marks, drawn in a short box."""
    base = y + h - 6
    # two peaks
    c.triangle(x + 10, base, x + 90, y + 8, x + 170, base, NAVY)
    c.triangle(x + 110, base, x + 190, y + 2, x + 268, base, NAVY)
    # snow caps
    c.triangle(x + 78, y + 18, x + 90, y + 8, x + 102, y + 18, LIGHT)
    c.triangle(x + 178, y + 12, x + 190, y + 2, x + 202, y + 12, LIGHT)
    # jagged red crack down the middle peak
    pts = [(x + 150, y + 6), (x + 140, y + 20), (x + 156, y + 32),
           (x + 144, y + 44), (x + 154, y + 56), (x + 146, base - 4)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        c.line(ax, ay, bx, by, RED, 3)
    # tremor rings around the crack
    c.circle(x + 150, y + 26, 4, GOLD)
    c.circle(x + 148, y + 46, 3, GOLD)
    # ground line
    c.hline(x + 6, base, w - 12, INK, 2)


# ---------------------------------------------------------------- layout
def story_panel(c, x, y, w, h, kicker, headlines, body, pic):
    c.rect(x, y, w, h, INK, 2)
    inner = x + 16
    cursor = y + 14
    if pic is not None:
        pic(c, x + 14, y + 8, w - 28, 70)
        cursor = y + 84
    c.text(inner, cursor, kicker, 2, RED)
    cursor += 22
    for line in headlines:
        c.text(inner, cursor, line, 3, NAVY)
        cursor += 30
    c.paragraph(inner, cursor + 4, body, 2, INK, (w - 32) // 12, leading=16)


def draw():
    c = Canvas(W, H, PAPER)
    # masthead
    c.fill_rect(24, 24, 976, 134, NAVY)
    c.fill_rect(24, 24, 976, 5, GOLD)
    c.fill_rect(24, 153, 976, 5, GOLD)
    c.text_centred(512, 42, "THE WORLD IN ONE DAY", 5, LIGHT)
    c.text_centred(512, 94, "SUNDAY 22 NOVEMBER 2026", 3, GOLD)
    c.text_centred(512, 128, "THE DAY'S WORLD NEWS IN ONE IMAGE", 2, LIGHT)

    # lead story (full width): the Sinaloa capture, biggest headline
    c.rect(24, 170, 976, 214, INK, 3)
    c.fill_rect(24, 170, 976, 214, PAPER)
    c.rect(24, 170, 976, 214, INK, 3)
    pic_capture(c, 664, 182, 296, 190)
    c.vline(640, 186, 186, GREY, 2)
    c.text(40, 188, "MEXICO " + BULLET + " DRUGS", 2, RED)
    c.text(40, 214, "MEXICO CAPTURES", 5, NAVY)
    c.text(40, 254, "EL CHAPO ISIDRO", 5, NAVY)
    c.paragraph(40, 306, "Mexican special forces captured drug "
                 "kingpin Fausto Isidro Meza Flores, known as El "
                 "Chapo Isidro, in a raid in Sinaloa. Eleven were "
                 "killed in violence after the capture.", 2, INK, 48)

    # second story (full width): Russia's massive attack on Ukraine
    c.rect(24, 396, 976, 214, INK, 3)
    c.fill_rect(24, 396, 976, 214, PAPER)
    c.rect(24, 396, 976, 214, INK, 3)
    pic_strike(c, 40, 408, 250, 190)
    c.vline(306, 412, 182, GREY, 2)
    c.text(322, 414, "UKRAINE " + BULLET + " WAR", 2, RED)
    c.text(322, 442, "RUSSIA'S BIGGEST", 4, NAVY)
    c.text(322, 474, "ATTACK: 400 DRONES,", 4, NAVY)
    c.text(322, 506, "110 MISSILES", 4, NAVY)
    c.paragraph(322, 538, "Russia launched 400 drones and 110 "
                 "missiles in one of the war's largest attacks. At "
                 "least two were killed, and a missile hit "
                 "Zelensky's hometown. A Russian missile crashed "
                 "in Poland.", 2, INK, 52)

    # mid row: Baltic ship, Gulf escalation, Peru quake
    story_panel(c, 24, 622, 312, 248, "BALTIC " + BULLET + " SHIP",
                ["DRONES HIT", "RUSSIAN SHIP"],
                "Drones hit a Russian cargo ship in the Gulf of "
                "Finland. It caught fire.",
                pic_ship)
    story_panel(c, 356, 622, 312, 248, "GULF " + BULLET + " IRAN-US",
                ["IRAN HITS US", "BASE IN KUWAIT"],
                "Iran struck a US air base in Kuwait and targeted "
                "Bahrain. Tankers were hit off Oman.",
                pic_tanker)
    story_panel(c, 688, 622, 312, 248, "PERU " + BULLET + " QUAKE",
                ["6.7-6.9 QUAKE", "SHAKES ANDES"],
                "A 6.7-6.9 quake shook the Andes in central Peru. "
                "No casualties or damage reported.",
                pic_quake)

    # footer: the rest of the day
    c.hline(24, 882, 976, INK, 2)
    c.text_centred(512, 896,
                   "ALSO: COP31 deadlocked over fossil fuels  " + BULLET +
                   "  FBI probes criminal database hack", 2, INK)
    c.text_centred(512, 918,
                   "Tech stocks slide as Anthropic shares fall  " +
                   BULLET + "  Eisenkot invites Likud to talks", 2, INK)
    c.text_centred(512, 940,
                   "Bolsonaro in ICU with bowel obstruction  " + BULLET +
                   "  France's sixth protest Saturday", 2, INK)
    c.text_centred(512, 962,
                   "Trump seeks a permanent nuclear accord with Iran  " +
                   BULLET + "  French turnout lower", 2, INK)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    image = draw()
    data = to_png(image)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (path, len(data), digest))


if __name__ == "__main__":
    main()
