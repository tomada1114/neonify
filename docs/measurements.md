# Reference Measurements

Nothing in this animation was designed. Every colour, every distance and every
interval was measured off a reference: a 550×160 screen recording of
`ultrathink` glowing for 2.69 seconds, and two lossless PNG screenshots of the
same animation — one at rest, one mid-shine.

This page records those measurements so the constants in `neonify.palette` and
`neonify.animation` can be checked, challenged or re-derived rather than taken
on trust.

## Method

The recording is variable frame rate: a screen capture only emits a frame when
the screen changes, so its 19 frames are 19 distinct states rather than a fixed
cadence. Frames were extracted to raw RGB and read without any image library:

```bash
ffmpeg -i recording.mov -vsync 0 -pix_fmt rgb24 -f rawvideo frames.raw
ffprobe -select_streams v -show_entries frame=pts_time -of csv=p=0 recording.mov
```

For each frame, columns containing ink were grouped into contiguous spans —
which found exactly ten spans, one per character — and each span was reduced to
the modal colour of its solid core, ignoring the antialiased edges. Because a
terminal paints a whole cell in one colour, that modal colour *is* the colour
the animation asked for.

!!! note "Why the screenshots matter more than the recording"

    H.264 shifted every channel down by a roughly constant amount. Comparing
    the seven resting colours, which appear in both the recording and the
    lossless screenshots, put that bias at `(+1.5, +2, +1.6)`. Values taken
    from the screenshots are exact; values available only from the recording
    were corrected by that bias and are accurate to about ±2 per channel.

## The palette

Characters are coloured by position, and the palette starts over every seven
characters — which is why the `i` of `ultrathink` is the same red as its `u`.
Each entry has two brightnesses: the colour the character rests at, and the
colour it takes while the shine is over it.

| # | Hue | Resting | Lit | Source of the lit colour |
| --- | --- | --- | --- | --- |
| 1 | 3° | `#E8554D` | `#FA9088` | screenshot (exact) |
| 2 | 18° | `#F4804D` | `#FEB17E` | screenshot (exact) |
| 3 | 37° | `#F9BB54` | `#FDDD8E` | recording (corrected) |
| 4 | 107° | `#87C077` | `#B0E3AB` | recording (corrected) |
| 5 | 214° | `#76A0D7` | `#ADC7EB` | recording (corrected) |
| 6 | 260° | `#9077C0` | `#BAADE2` | recording (corrected) |
| 7 | 318° | `#C177AB` | `#E2ABCB` | screenshot (exact) |

The resting colours are all exact: every one of them appears in the at-rest
screenshot. Note how uneven their saturation is — the greens, purples and pinks
sit near 0.37 while the yellows reach 0.93. That is a property of the animation,
not of the capture; the lossless screenshot shows the same spread.

## The shine

The shine is a band of **three characters**, and it is flat: the three lit
characters are equally bright, and their neighbours are at exactly their
resting value, with no falloff between them.

Two independent checks establish that:

- In the lossless screenshot, `h`, `i` and `n` are lit while `t` and `k` either
  side measure their resting colours to the byte. A gradient would have left a
  partial value on at least one of them.
- A character measures the same lit colour whether it is at the leading or the
  trailing edge of the band. `l` reads `(252, 175, 124)` as the band arrives and
  `(254, 174, 123)` as it leaves — one codec's worth of noise apart.

The band advances one character per frame, leading edge first, and travels left
to right. Writing its leading edge as `lead`, a character at `position` is lit
when `0 <= lead - position < 3`.

## Timing

Each recorded frame was reduced to the set of lit positions, from which the
leading edge follows directly:

| Frame | Time (s) | Lit positions | Lead |
| --- | --- | --- | --- |
| 0 | 0.000 | 4, 5, 6 | 6 |
| 1 | 0.033 | 5, 6, 7 | 7 |
| 2 | 0.100 | 6, 7, 8 | 8 |
| 3 | 0.150 | 8, 9 | 10 |
| 4 | 0.205 | 9 | 11 |
| 5–7 | 0.272–0.817 | — | at rest |
| 8 | 1.167 | 0 | 0 |
| 9 | 1.233 | 0, 1 | 1 |
| 10 | 1.305 | 1, 2, 3 | 3 |
| 11 | 1.355 | 2, 3, 4 | 4 |
| 12 | 1.422 | 3, 4, 5 | 5 |
| 13 | 1.495 | 4, 5, 6 | 6 |
| 14 | 1.567 | 6, 7, 8 | 8 |
| 15 | 1.638 | 7, 8, 9 | 9 |
| 16 | 1.688 | 8, 9 | 10 |
| 17–18 | 1.738–2.295 | — | at rest |

Individual gaps in that table are not trustworthy — the capture timestamps
jitter badly enough to show two-position jumps and one-position steps at the
same 72 ms spacing. Long baselines are trustworthy, so both sweeps were fitted
together as one line with a shared slope and a one-period offset:

- **Frame interval: 50 ms.** The pooled least-squares slope is 50.1 ms per
  position.
- **Cycle: 1.50 s.** The offset between the two sweeps is 1.497 s, matching the
  three single-position estimates (1.467 s, 1.495 s and 1.538 s) taken from the
  frames where the same lead recurs.

That makes the cycle **30 frames**, which for a ten-character string splits into
12 frames of travel — ten positions plus the two the trailing edge needs to
clear the end — and **18 frames at rest**.

As a sanity check, the third sweep should then begin at 2.667 s. The recording
ends at 2.690 s having never shown it, and its final frame at 2.295 s shows
nothing lit.

## Why the lit colours are stored rather than computed

A single lightening rule would be tidier than a second set of seven colours, so
several were fitted against all seven measured pairs. None of them fits:

| Model | Best parameter | RMS error | Worst channel |
| --- | --- | --- | --- |
| Mix towards white, sRGB | 36.7% | 7.0 | 16.3 |
| Mix towards white, Oklab | 35.8% | 7.2 | 17.5 |
| Mix towards white, linear light | 24.8% | 10.9 | 23.7 |
| HSL lightness `+0.138` | — | 7.3 | 17.3 |
| HSL lightness set to `0.762` | — | 7.9 | 14.7 |
| HSV value `×1.25` | — | 28.6 | 56.0 |
| Oklch lightness `+0.125`, chroma `×0.817` | — | 6.6 | 12.4 |
| HSL lightness `+0.146`, saturation `×1.15` | — | 5.4 | 14.5 |
| HSL lightness lerp `0.39`, saturation `×1.18` | — | 4.8 | 13.7 |

Errors are in channel steps out of 255, taken over all 21 channels of the seven
pairs, and each parameter is the one that minimises the RMS — so the numbers
above recompute from `RAINBOW` alone.

The three white-mix rows and the two HSL-lightness rows share one failure: every
one of them under-predicts the dominant channel of all seven colours. The
reference brightens a hue without washing it out, and lightening alone cannot do
both. Letting saturation rise as well — the last two rows — cuts the RMS by
about a third and still leaves one channel 14 steps out; refitting those two to
minimise the worst channel rather than the RMS only brings it down to 9.

!!! info "Mixing with white is HSL lightness interpolation"

    The sRGB row is not a separate family from the HSL rows: mixing a colour
    with white in sRGB *is* lerping its HSL lightness towards 1 with the
    saturation left alone. Mixing scales chroma by `1 - w` and closes the gap to
    full lightness by the same `w`, and those two effects cancel exactly in the
    HSL saturation formula — a lerp of `0.367` with saturation untouched
    reproduces the sRGB row's 7.0 to the digit, which is why it has no row of
    its own. The `+0.138` row is a genuinely different operation: an additive
    shift moves every colour by the same amount, where the lerp moves the dark
    ones further and the light ones less.

So the reference almost certainly picks its lit colours by hand, and `neonify`
stores them the same way, in `Hue.lit`.

## What the reference does not settle

The recording only ever shows one string, of one length, so two behaviours had
to be chosen rather than measured:

- **The rest is a fixed 18 frames, and only the sweep grows with the text.** A
  one-character string therefore flashes for three frames and waits, and a long
  one gets a shine that takes proportionally longer to cross. The alternative —
  holding the 1.5 s cycle for every length — would make the band jump several
  characters per frame on long strings.
- **Reversing the sweep leaves the colours where they are.** `--reverse` sends
  the shine right to left; it does not reorder the palette.

## Reproducing the check

The strongest available test is that step 8 of the animation should reproduce
the mid-shine screenshot exactly, since that screenshot is lossless. The step is
`render_frame`'s own frame counter, which starts where the shine enters — the
recording reaches that state at its frame 14:

```python
import re

from neonify import render_frame

escape = re.compile(r"\x1b\[38;2;(\d+);(\d+);(\d+)m")
frame = render_frame("ultrathink", 8)
measured = [
    (232, 85, 77), (244, 128, 77), (249, 187, 84), (135, 192, 119),
    (118, 160, 215), (144, 119, 192),
    (226, 171, 203), (250, 144, 136), (254, 177, 126),  # the lit three
    (249, 187, 84),
]

assert [tuple(map(int, m.groups())) for m in escape.finditer(frame)] == measured
```

All ten characters match, lit and resting alike.
