#!/usr/bin/env python3
"""Composes the Hiking Horror soundtrack as MIDI (for FL Studio) and renders
placeholder Ogg files for the game.

Every piece is built from one 8-bar "trail motif" so the calm Day 1 tune can
slowly fall apart over the week.

Usage:  python3 compose.py            (MIDI only)
        python3 compose.py --render   (MIDI + rendered audio; needs fluidsynth,
                                       a General MIDI .sf2 and ffmpeg)
"""
import json, math, os, random, re, struct, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MIDI_DIR = os.path.join(ROOT, "Music", "MIDI")
OGG_DIR = os.path.join(ROOT, "Assets", "HikingHorror", "Resources", "Music")
PREVIEW_DIR = os.path.join(ROOT, "Music", "Preview")
SF2 = os.environ.get("SF2", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
TPB = 480  # ticks per beat
SR = 44100

# --------------------------------------------------------------------------- MIDI

def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


class Track:
    def __init__(self, name, ch, program, vol=100, pan=64, reverb=60, chorus=0,
                 fl="", rng=None):
        self.name, self.ch, self.program, self.fl = name, ch, program, fl
        self.ev = []  # (tick, order, bytes)
        self.rng = rng or random.Random(name)
        self._meta(0, 0x03, name.encode())
        if ch != 9:
            self.raw(0, bytes([0xC0 | ch, program]))
        for num, val in ((7, vol), (10, pan), (91, reverb), (93, chorus), (11, 127)):
            self.cc(0, num, val)

    def _meta(self, beat, kind, data):
        self.ev.append((int(beat * TPB), 1, b"\xff" + bytes([kind]) + vlq(len(data)) + data))

    def raw(self, beat, data, order=1):
        self.ev.append((max(0, int(round(beat * TPB))), order, data))

    def cc(self, beat, num, val):
        self.raw(beat, bytes([0xB0 | self.ch, num, max(0, min(127, int(val)))]))

    def bend(self, beat, semis, rng_semis=2.0):
        v = int(8192 + max(-1, min(1, semis / rng_semis)) * 8191)
        v = max(0, min(16383, v))
        self.raw(beat, bytes([0xE0 | self.ch, v & 0x7F, v >> 7]))

    def note(self, beat, dur, pitch, vel=80, human=True):
        if pitch is None:
            return
        if human:
            beat += self.rng.uniform(-0.012, 0.012)
            vel += self.rng.randint(-6, 6)
        beat = max(0.0, beat)
        vel = max(1, min(127, int(vel)))
        pitch = max(0, min(127, int(pitch)))
        self.raw(beat, bytes([0x90 | self.ch, pitch, vel]))
        self.raw(beat + max(0.05, dur), bytes([0x80 | self.ch, pitch, 0]), order=0)

    def chord(self, beat, dur, pitches, vel=70, spread=0.0):
        for i, p in enumerate(pitches):
            self.note(beat + i * spread, dur - i * spread, p, vel)

    def ramp(self, b0, b1, num, v0, v1, step=0.25, curve=None):
        n = max(1, int((b1 - b0) / step))
        for i in range(n + 1):
            t = i / n
            if curve:
                t = curve(t)
            self.cc(b0 + (b1 - b0) * i / n, num, v0 + (v1 - v0) * t)

    def end_beat(self):
        return max((t for t, _, _ in self.ev), default=0) / TPB

    def chunk(self):
        out, last = bytearray(), 0
        for tick, _, data in sorted(self.ev, key=lambda e: (e[0], e[1])):
            out += vlq(tick - last) + data
            last = tick
        out += vlq(0) + b"\xff\x2f\x00"
        return b"MTrk" + struct.pack(">I", len(out)) + bytes(out)


def write_midi(path, bpm, tracks, length_beats, ts=(4, 4)):
    tempo = Track.__new__(Track)
    tempo.ev = []
    us = int(60_000_000 / bpm)
    tempo.ev.append((0, 1, b"\xff\x51\x03" + us.to_bytes(3, "big")))
    tempo.ev.append((0, 1, b"\xff\x58\x04" + bytes([ts[0], int(math.log2(ts[1])), 24, 8])))
    tempo.ev.append((int(length_beats * TPB), 1, b"\xff\x01\x03end"))
    data = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks) + 1, TPB)
    data += Track.chunk(tempo)
    for t in tracks:
        # A silent controller at the end keeps every track (and the render) the same length.
        t.cc(length_beats, 11, 127) if t.ch != 9 else None
        data += t.chunk()
    with open(path, "wb") as f:
        f.write(data)

# --------------------------------------------------------------------------- music material

# The trail motif: 8 bars of 4/4 in D major, (pitch, beats). None = rest.
MOTIF = [
    (69, 1), (66, .5), (69, .5), (71, 1), (69, 1),
    (66, 1), (64, .5), (62, .5), (64, 2),
    (69, 1), (66, .5), (69, .5), (74, 1), (73, .5), (71, .5),
    (69, 3), (None, 1),
    (71, 1), (69, .5), (66, .5), (67, 1), (66, 1),
    (64, 1), (62, .5), (64, .5), (66, 2),
    (64, 1), (62, .5), (59, .5), (57, 1), (62, 1),
    (62, 4),
]
assert abs(sum(d for _, d in MOTIF) - 32) < 1e-6

C = {
    "D": [50, 57, 62, 66], "Em7": [52, 59, 62, 67], "Bm": [47, 54, 59, 62],
    "Gadd9": [43, 50, 57, 59], "G": [43, 50, 55, 59], "Asus4": [45, 52, 57, 62],
    "A": [45, 52, 57, 61], "Dm": [50, 57, 62, 65], "Bb": [46, 53, 58, 62],
    "Gm": [43, 50, 55, 58], "Eb": [51, 58, 63, 67], "Bbmaj7": [46, 53, 57, 62],
    "A7b9": [45, 52, 55, 58, 61], "C": [48, 55, 60, 64], "F": [41, 48, 57, 65],
    "Em": [40, 47, 55, 59], "F#": [42, 49, 54, 58], "Gmaj7": [43, 50, 54, 59],
    "E": [40, 47, 56, 59], "F#m": [42, 49, 54, 57], "B": [47, 54, 59, 63],
    "C#m": [49, 56, 61, 64], "D5": [38, 45, 50, 57], "Bbm": [46, 53, 58, 61],
}
TRAIL_PROG = ["D", "Em7", "Bm", "Gadd9", "G", "D", "Asus4", "D"]
TRAIL_PROG_B = ["G", "D", "Bm", "Gadd9", "Em7", "Gadd9", "Asus4", "D"]
DARK_PROG = ["Dm", "Bb", "Gm", "Eb", "Gm", "Dm", "A7b9", "Dm"]


def minorize(m, root_pc=2):
    """Major -> minor around root: lower the 3rd, 6th and 7th degrees."""
    out = []
    for p, d in m:
        if p is not None and (p - root_pc) % 12 in (4, 9, 11):
            p -= 1
        out.append((p, d))
    return out


def transpose(m, n):
    return [(None if p is None else p + n, d) for p, d in m]


def stretch(m, k):
    return [(p, d * k) for p, d in m]


def corrupt(m, rng, wrong=0.35, drop=0.25):
    """Wrong notes and holes creep into the motif."""
    out = []
    for p, d in m:
        if p is not None:
            r = rng.random()
            if r < drop:
                p = None
            elif r < drop + wrong:
                p += rng.choice([-1, -1, 1, 6])
        out.append((p, d))
    return out


def play(track, m, start, vel=80, legato=0.95, octave=0):
    b = start
    for p, d in m:
        if p is not None:
            track.note(b, d * legato, p + 12 * octave, vel)
        b += d
    return b


def fingerpick(track, prog, start_bar, vel=66, pattern=(0, 2, 3, 2, 1, 2, 3, 2), ring=1.6):
    for i, name in enumerate(prog):
        v = C[name]
        for k, idx in enumerate(pattern):
            p = v[min(idx, len(v) - 1)]
            track.note((start_bar + i) * 4 + k * 0.5, ring, p, vel + (10 if k == 0 else 0))


def pads(track, prog, start_bar, vel=48, octave=0, bars_each=1):
    for i, name in enumerate(prog):
        b = (start_bar + i * bars_each) * 4
        track.chord(b, 4 * bars_each - 0.05, [p + 12 * octave for p in C[name]], vel)


def swell(track, start_bar, bars, lo=40, hi=110, period_bars=2):
    for i in range(int(bars * 4 / 0.25) + 1):
        b = start_bar * 4 + i * 0.25
        ph = (b - start_bar * 4) / (period_bars * 4)
        track.cc(b, 11, lo + (hi - lo) * (0.5 - 0.5 * math.cos(ph * 2 * math.pi)))


def warble(track, start, beats, base=-0.18, depth=0.12, rate=0.35):
    """Detuned, warped-tape pitch drift (music box)."""
    for i in range(int(beats / 0.25) + 1):
        b = start + i * 0.25
        track.bend(b, base + depth * math.sin(b * rate * 2 * math.pi) * math.sin(b * 0.13))

# --------------------------------------------------------------------------- pieces

PIECES = []


def piece(name, bpm, beats, loop, title, use, key, stems=None, ref=None, lufs=-24.0):
    def deco(fn):
        PIECES.append(dict(name=name, bpm=bpm, beats=beats, loop=loop, title=title, use=use,
                           key=key, fn=fn, stems=stems, ref=ref, lufs=lufs))
        return fn
    return deco


@piece("trail", 80, 128, True, "Trail Theme (layered)",
       "Days 1-6 while hiking. Layers fade in and out with the dread level.", "D major",
       stems=["guitar", "melody", "melody_wrong", "pad_dark", "drone"], ref=["guitar", "melody"])
def trail(rng):
    g = Track("guitar", 0, 24, 96, 54, 50, fl="FLEX or a nylon/acoustic guitar plugin, fingerpicked")
    m = Track("melody", 1, 73, 92, 70, 70, fl="Flute or soft whistle; light reverb")
    w = Track("melody_wrong", 2, 10, 90, 80, 90, fl="Music box, detuned and warbling (pitch automation)")
    pd = Track("pad_dark", 3, 94, 80, 60, 90, fl="Dark pad (Sytrus/FLEX) in D minor - clashes on purpose")
    dr = Track("drone", 4, 43, 100, 64, 70, fl="Contrabass / sub drone with slow swells + soft timpani")
    fingerpick(g, TRAIL_PROG * 3, 0)
    fingerpick(g, TRAIL_PROG_B, 24, vel=58, pattern=(0, 2, 1, 3, 2, 1, 3, 2))
    play(m, MOTIF, 8 * 4, 82)
    play(m, MOTIF[:-1] + [(66, 2), (62, 2)], 16 * 4, 78)
    play(m, stretch(MOTIF[:9], 2)[:5], 24 * 4, 64)
    warble(w, 0, 128)
    play(w, corrupt(MOTIF, rng), 8 * 4, 70, octave=1)
    play(w, corrupt(MOTIF, rng, wrong=0.45, drop=0.45), 16 * 4, 66, octave=1)
    play(w, corrupt(stretch(MOTIF[:9], 2)[:5], rng, wrong=0.6, drop=0.2), 24 * 4, 60, octave=1)
    pads(pd, DARK_PROG * 4, 0, vel=52)
    swell(pd, 0, 32, 50, 115, 4)
    for b in range(0, 32, 8):
        dr.note(b * 4, 32 - 0.1, 26, 90)
        dr.note(b * 4, 32 - 0.1, 33, 70)
    swell(dr, 0, 32, 30, 120, 8)
    return [g, m, w, pd, dr]


@piece("menu", 60, 96, True, "Main Menu", "Title screen.", "D major -> D minor")
def menu(rng):
    p = Track("piano", 0, 0, 100, 64, 80, fl="FL Keys (soft felt piano), lots of reverb")
    pd = Track("pad", 1, 89, 70, 64, 100, fl="Warm pad, very quiet")
    lo = Track("low_strings", 2, 49, 70, 64, 90, fl="Slow strings / cello section")
    play(p, MOTIF, 0, 70)
    play(p, minorize(MOTIF[:-1]) + [(62, 4)], 32, 64)
    play(p, corrupt(stretch(MOTIF[:10], 1.5), rng, 0.3, 0.3)[:8], 64, 55)
    pads(pd, TRAIL_PROG + DARK_PROG + ["Dm", "Bb", "Gm", "D5", "Dm", "Bb", "Gm", "D5"], 0, 40)
    for b in range(0, 24, 4):
        lo.note(b * 4, 16 - 0.1, 38, 60)
    swell(lo, 0, 24, 40, 100, 4)
    return [p, pd, lo]


@piece("night_tent", 56, 64, True, "Night - In the Tent",
       "When Ben goes to sleep. Quiet lullaby that is slightly wrong.", "D minor")
def night_tent(rng):
    mb = Track("music_box", 0, 10, 85, 64, 100, fl="Music box, detuned, slow vibrato")
    pd = Track("pad", 1, 94, 70, 64, 110, fl="Halo pad, dark and wide")
    lo = Track("low", 2, 49, 60, 64, 90, fl="Very soft low strings")
    warble(mb, 0, 64, base=-0.25, depth=0.18, rate=0.2)
    play(mb, stretch(minorize(MOTIF), 2), 0, 62, octave=1, legato=0.6)
    pads(pd, ["Dm", "Bbmaj7", "Gm", "A7b9"] * 2, 0, 40, bars_each=2)
    swell(pd, 0, 16, 40, 100, 4)
    for b in range(0, 16, 2):
        lo.note(b * 4, 8 - 0.1, [38, 34, 31, 33][(b // 2) % 4], 50)
    return [mb, pd, lo]


@piece("night_dark", 96, 64, True, "Night - Into the Dark (layered)",
       "When Ben explores at night. 'tension' layer fades in as the monster gets close.",
       "D minor (Phrygian)", stems=["base", "tension"], ref=["base", "tension"])
def night_dark(rng):
    base = Track("base", 0, 45, 100, 64, 60, fl="Cello/contrabass staccato ostinato + timpani")
    timp = Track("timpani", 1, 47, 100, 64, 70, fl="Timpani / low drum")
    ten = Track("tension", 2, 44, 90, 64, 110, fl="High string tremolo cluster + reverse cymbal swells")
    rev = Track("revcym", 3, 119, 80, 64, 60)
    pat = [38, 38, 39, 38, 38, 38, 41, 39]
    for bar in range(16):
        for k, p in enumerate(pat):
            base.note(bar * 4 + k * 0.5, 0.3, p, 92 if k == 0 else 72)
        if bar % 2 == 0:
            timp.note(bar * 4, 2, 38, 100)
    for b in range(0, 16, 4):
        ten.chord(b * 4, 16 - 0.1, [86, 87, 81], 70)
        rev.note(b * 4 + 12, 4, 60, 90)
    swell(ten, 0, 16, 20, 120, 4)
    timp.stem, rev.stem = "base", "tension"
    return [base, timp, ten, rev]


def chase_common(rng, key=0, bpm_heavy=False):
    dm = Track("drums", 9, 0, 115, 64, 30, fl="FPC: taiko/toms, big kick, snare (or Fruity drum kit)")
    st = Track("low_strings", 0, 48, 105, 64, 40, fl="Low strings spiccato 16ths")
    br = Track("brass", 1, 61, 100, 64, 60, fl="Brass stabs / low horns")
    hi = Track("high_strings", 2, 48, 95, 64, 70, fl="High strings playing the motif in minor")
    ost = [38, 38, 50, 38, 41, 38, 39, 38, 38, 38, 50, 38, 48, 38, 46, 45]
    stabs = [["Dm"], ["Dm"], ["Bb"], ["A7b9"]]
    for bar in range(16):
        for k, p in enumerate(ost):
            st.note(bar * 4 + k * 0.25, 0.2, p + key, 100 if k % 4 == 0 else 78)
        ch = C[stabs[bar % 4][0]]
        for pos in (0, 1.5):
            br.chord(bar * 4 + pos, 0.4, [x + key for x in ch[:3]], 105)
        for k in (0, 6, 8, 11, 14):
            dm.note(bar * 4 + k * 0.25, 0.2, 41, 120 if k == 0 else 95)
        dm.note(bar * 4, 0.2, 36, 127)
        dm.note(bar * 4 + 2, 0.2, 36, 115)
        dm.note(bar * 4 + 1, 0.2, 38, 100)
        dm.note(bar * 4 + 3, 0.2, 38, 105)
        dm.note(bar * 4 + 0.75, 0.2, 43, 90)
        if bar % 4 == 3:
            for k in range(8):
                dm.note(bar * 4 + 2 + k * 0.25, 0.2, [50, 48, 47, 45, 43, 41, 43, 41][k], 110)
        if bar % 8 == 0:
            dm.note(bar * 4, 2, 49, 120)
    play(hi, transpose(minorize(MOTIF), 12 + key), 32, 100, legato=1.0)
    return [dm, st, br, hi]


@piece("chase_day7", 140, 64, True, "Chase - Day 7", "The run to the trailhead.", "D minor")
def chase7(rng):
    return chase_common(rng)


@piece("chase_day14", 152, 64, True, "Chase - Day 14", "The final run out. Bigger and worse.",
       "Eb minor")
def chase14(rng):
    tr = chase_common(rng, key=1)
    ch = Track("choir", 3, 52, 100, 64, 90, fl="Choir 'aah' - long dissonant notes")
    bs = Track("synth_bass", 4, 38, 100, 64, 20, fl="Distorted synth bass 8ths")
    for b in range(0, 16, 2):
        ch.chord(b * 4, 8 - 0.1, [63, 64, 70] if (b // 2) % 2 else [63, 66, 70], 90)
        for k in range(16):
            bs.note(b * 4 + k * 0.5, 0.4, 27 + (0 if k % 8 < 6 else 1), 110)
    return tr + [ch, bs]


@piece("week2", 66, 96, True, "Week 2 - Deep Woods", "Days 8-14: snow, burned forest.", "B minor")
def week2(rng):
    ce = Track("celesta", 0, 8, 90, 70, 100, fl="Celesta or glass bells, cold and distant")
    hp = Track("harp", 1, 46, 85, 50, 80, fl="Harp arpeggios")
    st = Track("strings", 2, 49, 80, 64, 100, fl="Slow strings, wide")
    prog = ["Bm", "G", "Em", "F#", "G", "D", "Em", "F#"]
    mot = [(None if p is None else (p - 3) - (1 if (p - 3) % 12 in (3, 8, 10) else 0), d)
           for p, d in MOTIF]
    play(ce, mot, 0, 70, octave=1, legato=0.8)
    play(ce, corrupt(mot, rng, 0.2, 0.35), 32, 62, octave=1, legato=0.8)
    play(ce, stretch(mot[:9], 2)[:6], 64, 55, octave=1)
    for i, name in enumerate(prog * 3):
        v = C[name]
        for k in range(8):
            hp.note(i * 4 + k * 0.5, 1.0, v[(0, 1, 2, 3, 2, 1, 2, 3)[k]] + 12, 58)
    pads(st, prog * 3, 0, 45)
    swell(st, 0, 24, 45, 110, 4)
    return [ce, hp, st]


@piece("ending1_early_exit", 72, 72, False, "Ending 1 - Early Exit",
       "Ben leaves after Day 7.", "D major (unresolved)")
def ending1(rng):
    g = Track("guitar", 0, 24, 96, 54, 60, fl="Acoustic guitar")
    m = Track("flute", 1, 73, 90, 70, 70, fl="Flute")
    mb = Track("music_box", 2, 10, 90, 80, 100, fl="Music box - the last wrong note")
    pd = Track("pad", 3, 94, 70, 64, 100, fl="Dark pad, enters at the very end")
    fingerpick(g, TRAIL_PROG + ["G", "D", "Bm", "Gadd9"], 0, vel=60)
    play(m, MOTIF[:-1], 0, 78)
    warble(mb, 56, 16, -0.3, 0.2)
    play(mb, [(69, 1), (66, 1), (65, 6)], 52, 70, octave=1)
    pads(pd, ["Dm", "Bb"], 14, 50, bars_each=2)
    return [g, m, mb, pd]


@piece("ending2_out_of_woods", 76, 108, False, "Ending 2 - Out of the Woods",
       "Ben makes it out after Day 14.", "D major -> D minor")
def ending2(rng):
    p = Track("piano", 0, 0, 100, 60, 80, fl="Piano")
    g = Track("guitar", 1, 25, 85, 44, 60, fl="Steel acoustic guitar")
    s = Track("strings", 2, 48, 90, 70, 90, fl="Warm string ensemble")
    fingerpick(g, TRAIL_PROG * 3, 0, vel=56)
    play(p, MOTIF, 0, 72)
    play(s, MOTIF, 32, 80, octave=1, legato=1.0)
    pads(s, TRAIL_PROG, 8, 60)
    pads(s, ["G", "D", "Bm", "Gadd9", "Em7", "Gadd9", "Asus4", "Dm", "Dm"], 16, 64)
    play(p, MOTIF[:-1] + [(None, 4)], 64, 66)
    p.chord(100, 8, [38, 50, 57, 62, 65], 70)
    return [p, g, s]


@piece("ending3_lost", 54, 64, False, "Ending 3 - Lost",
       "Ben is caught. A new hiker sees him far ahead.", "D minor")
def ending3(rng):
    ch = Track("choir", 0, 52, 95, 64, 110, fl="Choir 'aah', slow")
    lo = Track("low_strings", 1, 49, 90, 64, 100, fl="Low strings")
    mb = Track("music_box", 2, 10, 80, 70, 110, fl="Music box, slowing down")
    rev = list(reversed(minorize(MOTIF)))
    play(ch, stretch(rev[:12], 1.5), 0, 72, octave=-1)
    pads(lo, ["Dm", "Bbm", "Gm", "A7b9", "Dm", "Bbm", "Gm", "D5"], 0, 55, octave=-1, bars_each=2)
    warble(mb, 32, 32, -0.4, 0.3, 0.15)
    play(mb, stretch(corrupt(minorize(MOTIF[:9]), rng, 0.3, 0.2), 2)[:6], 32, 55, octave=1)
    lo.note(60, 4, 26, 70)
    return [ch, lo, mb]


@piece("ending4_truth", 70, 136, False, "Ending 4 - The Truth",
       "Ben finds every clue and ends it.", "D major -> E major")
def ending4(rng):
    s = Track("strings", 0, 48, 100, 64, 90, fl="Full string section")
    p = Track("piano", 1, 0, 90, 60, 80, fl="Piano")
    h = Track("horn", 2, 60, 90, 70, 80, fl="French horn")
    g = Track("guitar", 3, 24, 80, 50, 60, fl="Nylon guitar")
    fingerpick(g, TRAIL_PROG, 0, vel=56)
    play(p, MOTIF, 0, 70)
    pads(s, TRAIL_PROG, 8, 62)
    play(h, MOTIF, 32, 84, octave=-1, legato=1.0)
    up = transpose(MOTIF, 2)
    pads(s, [n for n in ["E", "F#m", "C#m", "A", "A", "E", "B", "E"]], 16, 70)
    play(s, up, 64, 92, octave=1, legato=1.0)
    play(p, up, 64, 76)
    s.chord(128, 8, [40, 52, 59, 64, 68, 71], 85)
    h.chord(128, 8, [52, 56, 59], 80)
    return [s, p, h, g]


@piece("sting_scare", 120, 8, False, "Stinger - Jump Scare",
       "Plays over everything at a jump scare.", "-", lufs=None)
def sting_scare(rng):
    a = Track("hit", 0, 48, 127, 64, 60, fl="Orchestral hit: low strings + brass + timpani")
    b = Track("brass", 1, 61, 127, 64, 60)
    c = Track("screech", 2, 44, 120, 64, 80, fl="High string screech bending upward")
    d = Track("drums", 9, 0, 127, 64, 60)
    a.chord(0, 3, [26, 38, 39, 45, 50, 51], 127)
    b.chord(0, 2.5, [38, 39, 44, 50], 127)
    c.chord(0, 4, [86, 87, 92], 120)
    for i in range(16):
        c.bend(i * 0.25, -1.5 + i * 0.22)
    d.note(0, 1, 49, 127); d.note(0, 1, 52, 127); d.note(0, 1, 36, 127)
    return [a, b, c, d]


@piece("sting_reveal", 70, 12, False, "Stinger - Photo Reveal",
       "When a photo shows something that was not there.", "-", lufs=None)
def sting_reveal(rng):
    a = Track("cluster", 0, 44, 110, 64, 100, fl="String tremolo cluster swelling up")
    t = Track("timpani", 1, 47, 120, 64, 80)
    a.chord(0, 7, [74, 75, 80, 81], 90)
    a.ramp(0, 7, 11, 10, 127, curve=lambda x: x * x)
    t.note(7, 3, 38, 127)
    t.note(7, 3, 26, 127)
    return [a, t]


@piece("sting_low", 90, 8, False, "Stinger - Low Boom",
       "Something is close. Footsteps stop. Twig snaps.", "-", lufs=None)
def sting_low(rng):
    a = Track("boom", 0, 116, 127, 64, 90, fl="Taiko / sub boom")
    b = Track("sub", 1, 43, 120, 64, 90, fl="Contrabass swell")
    a.note(0, 4, 36, 127)
    b.note(0, 6, 26, 120)
    b.ramp(0, 6, 11, 127, 0)
    return [a, b]

# --------------------------------------------------------------------------- rendering


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(cmd) + "\n" + r.stderr[-2000:])
    return r


def render_wav(mid, wav):
    run(["fluidsynth", "-ni", "-q", "-g", "0.45", "-r", str(SR), "-F", wav, SF2, mid])


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
             "loudnorm=print_format=json", "-f", "null", "-"])
    js = json.loads(re.search(r"\{[^{}]*\}", r.stderr[r.stderr.rfind("Parsed_loudnorm"):],
                              re.S).group(0))
    return float(js["input_i"]), float(js["input_tp"])


def stem_groups(pc, tracks):
    """Map stem name -> tracks. Tracks may carry .stem to join another stem."""
    groups = {}
    for t in tracks:
        key = getattr(t, "stem", t.name)
        groups.setdefault(key, []).append(t)
    return groups


def build(pc, render):
    rng = random.Random(pc["name"])
    tracks = [t for t in pc["fn"](rng) if t.ev]
    beats = pc["beats"]
    write_midi(os.path.join(MIDI_DIR, pc["name"] + ".mid"), pc["bpm"], tracks, beats)
    if not render:
        return []
    tmp = tempfile.mkdtemp()
    loop_len = int(round(beats * 60.0 / pc["bpm"] * SR))
    tail = 0 if pc["loop"] else 4.0

    def render_tracks(ts, out_wav):
        mid = os.path.join(tmp, "x.mid")
        if pc["loop"]:
            # Render twice and keep the second pass so the reverb tail wraps into the start.
            doubled = []
            for t in ts:
                d = Track.__new__(Track)
                d.__dict__.update(t.__dict__)
                d.ev = list(t.ev) + [(tick + beats * TPB, o, data) for tick, o, data in t.ev
                                     if not (data[0] == 0xFF and data[1] == 0x03)]
                doubled.append(d)
            write_midi(mid, pc["bpm"], doubled, beats * 2)
        else:
            write_midi(mid, pc["bpm"], ts, beats + tail * pc["bpm"] / 60.0)
        raw = os.path.join(tmp, "raw.wav")
        render_wav(mid, raw)
        if pc["loop"]:
            run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af",
                 f"atrim=start_sample={loop_len}:end_sample={2 * loop_len},asetpts=N/SR/TB",
                 out_wav])
        else:
            run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af", "areverse,silenceremove="
                 "start_periods=1:start_threshold=-70dB,areverse", out_wav])

    outputs = []  # (label, wav)
    if pc["stems"]:
        groups = stem_groups(pc, tracks)
        for s in pc["stems"]:
            w = os.path.join(tmp, f"{s}.wav")
            render_tracks(groups[s], w)
            outputs.append((f"{pc['name']}_{s}", w))
        ref = os.path.join(tmp, "ref.wav")
        render_tracks([t for s in pc["ref"] for t in groups[s]], ref)
    else:
        w = os.path.join(tmp, "full.wav")
        render_tracks(tracks, w)
        outputs.append((pc["name"], w))
        ref = w
    i, tp = loudness(ref)
    target = pc["lufs"]
    gain = (target - i) if target is not None else (-1.0 - tp)
    gain = min(gain, -1.0 - tp)  # keep true peak at or below -1 dBTP
    made = []
    for label, w in outputs:
        out = os.path.join(OGG_DIR, label + ".ogg")
        run(["ffmpeg", "-y", "-v", "error", "-i", w, "-af", f"volume={gain:.2f}dB",
             "-c:a", "libvorbis", "-q:a", "5", out])
        made.append(out)
    print(f"  {pc['name']:22s} {len(outputs)} file(s), ref {i:.1f} LUFS / {tp:.1f} dBTP, gain {gain:+.1f} dB")
    return made


def preview(made_by_piece):
    """One MP3 to listen to on a phone: a short excerpt of each piece."""
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp()
    parts = []

    def excerpt(srcs, seconds, label, weights=None):
        out = os.path.join(tmp, f"{len(parts):02d}.wav")
        ins = sum((["-i", s] for s in srcs), [])
        mix = (f"amix=inputs={len(srcs)}:normalize=0:weights={' '.join(map(str, weights or [1]*len(srcs)))},"
               if len(srcs) > 1 else "")
        run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex",
             f"{mix}atrim=0:{seconds},afade=t=out:st={seconds - 2}:d=2,volume=8dB,"
             "apad=pad_dur=1.2", "-ar", str(SR), "-ac", "2", out])
        parts.append(out)
        print("  preview:", label)

    t = {os.path.basename(p)[:-4]: p for ps in made_by_piece.values() for p in ps}
    excerpt([t["trail_guitar"], t["trail_melody"]], 60, "trail calm (Days 1-2)")
    excerpt([t["trail_guitar"], t["trail_melody_wrong"], t["trail_pad_dark"]], 45,
            "trail uneasy (Days 3-5)", [0.6, 1, 1])
    excerpt([t["trail_melody_wrong"], t["trail_pad_dark"], t["trail_drone"]], 40,
            "trail broken (Day 6)")
    for n, s in [("menu", 40), ("night_tent", 40), ("night_dark_base", 0),
                 ("chase_day7", 35), ("chase_day14", 35), ("week2", 40),
                 ("ending1_early_exit", 60), ("ending2_out_of_woods", 60),
                 ("ending3_lost", 60), ("ending4_truth", 70), ("sting_scare", 4),
                 ("sting_reveal", 9), ("sting_low", 6)]:
        if n == "night_dark_base":
            excerpt([t["night_dark_base"], t["night_dark_tension"]], 35, "night dark")
        else:
            excerpt([t[n]], s, n)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    out = os.path.join(PREVIEW_DIR, "soundtrack_preview.mp3")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-af", "alimiter=limit=0.89", "-c:a", "libmp3lame", "-b:a", "128k", out])
    return out


def preview_trail(files):
    """The trail theme as it changes over the week: calm -> uneasy -> broken."""
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    t = {os.path.basename(p)[:-4]: p for p in files}
    order = ["trail_guitar", "trail_melody", "trail_melody_wrong", "trail_pad_dark", "trail_drone"]
    loop_s = 128 * 60 / 80
    # Volume of each layer over 3 passes of the loop (Day 1-2, Day 3-5, Day 6).
    plan = {"trail_guitar": (1, 0.55, 0), "trail_melody": (1, 0, 0),
            "trail_melody_wrong": (0, 0.9, 1), "trail_pad_dark": (0, 0.8, 1),
            "trail_drone": (0, 0.25, 1)}
    ins, chains = [], []
    for i, n in enumerate(order):
        ins += ["-stream_loop", "2", "-i", t[n]]
        a, b, c = plan[n]
        expr = (f"if(lt(t,{loop_s - 6}),{a},if(lt(t,{loop_s}),{a}+({b}-{a})*(t-{loop_s - 6})/6,"
                f"if(lt(t,{2 * loop_s - 6}),{b},if(lt(t,{2 * loop_s}),{b}+({c}-{b})*(t-{2 * loop_s - 6})/6,{c}))))")
        chains.append(f"[{i}]volume='{expr}':eval=frame[a{i}]")
    total = 3 * loop_s
    fc = ";".join(chains) + ";" + "".join(f"[a{i}]" for i in range(len(order))) + \
        f"amix=inputs={len(order)}:normalize=0,atrim=0:{total - 20},afade=t=out:st={total - 26}:d=6," \
        "volume=6dB,alimiter=limit=0.89"
    out = os.path.join(PREVIEW_DIR, "trail_theme_preview.mp3")
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-ar", str(SR),
         "-c:a", "libmp3lame", "-b:a", "160k", out])
    return out


def write_guide():
    lines = ["# Soundtrack", "",
             "Every piece is built from the same 8-bar **trail motif** (D major). As the week goes on,",
             "the motif comes back minor, detuned, broken into fragments, and finally reversed.", "",
             "* `MIDI/` - one `.mid` per piece, one MIDI track per instrument. Drag a file into FL Studio",
             "  (or **File > Import > MIDI file**), tick *Start new project*, then load the suggested",
             "  instrument on each channel.",
             "* `Preview/soundtrack_preview.mp3` - a quick listen of every piece (rough General MIDI sounds).",
             "* The game plays `Assets/HikingHorror/Resources/Music/<name>.ogg`. Export your FL Studio",
             "  version with the **same file name** (WAV or OGG) and it replaces the placeholder.", "",
             "## Rules for the game versions", "",
             "* **Loops** (marked below) must loop seamlessly: export exactly the listed length, and in FL",
             "  Studio's export dialog choose *Leave remainder: Wrap remainder* so the reverb tail wraps",
             "  into the start.",
             "* **Layered pieces** (`trail`, `night_dark`): export each layer as its own file at the same",
             "  length (FL Studio: *Split mixer tracks*). The game plays them together and fades layers.",
             "* Loudness: about **-24 LUFS** integrated with true peak at or below **-1 dBTP**. Stingers just",
             "  peak at -1 dBTP. Voices sit on top of this, so do not master the music loud.", "",
             "| File | Piece | Tempo | Key | Length | Loop | Where it plays |",
             "|---|---|---|---|---|---|---|"]
    for pc in PIECES:
        secs = pc["beats"] * 60 / pc["bpm"]
        files = (", ".join(f"`{pc['name']}_{s}`" for s in pc["stems"]) if pc["stems"]
                 else f"`{pc['name']}`")
        lines.append(f"| {files} | {pc['title']} | {pc['bpm']} BPM | {pc['key']} | "
                     f"{int(secs // 60)}:{int(secs % 60):02d} ({pc['beats'] // 4} bars) | "
                     f"{'yes' if pc['loop'] else 'no'} | {pc['use']} |")
    lines += ["", "## Instruments per piece (suggestions)", ""]
    for pc in PIECES:
        rng = random.Random(pc["name"])
        tracks = [t for t in pc["fn"](rng) if t.ev and t.fl]
        lines.append(f"**{pc['title']}** (`{pc['name']}.mid`)")
        lines += [f"- *{t.name}*: {t.fl}" for t in tracks]
        lines.append("")
    lines += ["Plugin names are FL Studio stock suggestions (FL Keys, FPC, FLEX, Sytrus, Fruity Reeverb 2).",
              "Any instrument you like works - the MIDI is the composition, the sound is yours.", ""]
    with open(os.path.join(ROOT, "Music", "README.md"), "w") as f:
        f.write("\n".join(lines))


def main():
    render = "--render" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(OGG_DIR, exist_ok=True)
    made = {}
    for pc in PIECES:
        if only is None or pc["name"] in only:
            made[pc["name"]] = build(pc, render)
    if only is None:
        write_guide()
    if render and only is None:
        print("preview ->", preview(made))
    elif render and "trail" in made:
        print("preview ->", preview_trail(made["trail"]))


if __name__ == "__main__":
    main()
