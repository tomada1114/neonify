--8<-- "README.md"

## How it works

`neonify` stretches a seven-colour palette across the string and leaves it
there: the first character takes the red at one end of the palette, the last
takes the violet at the other, and every character between is blended from the
two palette entries its position falls between — so the rainbow always runs end
to end, however long the text. What moves is the shine: a band three characters
wide that advances one character per frame, lighting whatever it covers. Once
it has left the string the text rests for 18 frames before the next shine
enters.

The palette — both the resting colours and the lit ones — the width of the
shine, and the default 50 ms frame interval were all measured off a reference
recording, in which `ultrathink` completes a cycle in 30 frames, or 1.5 seconds.
[Reference Measurements](measurements.md) records those measurements and how
they were taken.

Only the sweep scales with the text, since the rest is a fixed number of frames.
A short string therefore flashes and waits, and a long one gets a shine that
takes proportionally longer to cross.

The animation repaints one line in place, so it never scrolls the terminal, and
the cursor is always restored when you stop it. Each frame is scheduled against
a deadline, so the time spent drawing does not stretch the interval.

When stdout is not a terminal — or the text is wider than the terminal —
`neonify` prints a single coloured frame instead of animating, taken from the
middle of the sweep so the shine is on the string, and it honours
[`NO_COLOR`](https://no-color.org/) by printing the bare text.

## Custom palettes

A palette entry is a `Hue`, pairing the colour a character rests at with the one
it takes under the shine, so a custom palette supplies both:

```python
from neonify import Color, GlowStyle, Hue, render_frame

ice = GlowStyle(palette=(Hue(base=Color(90, 150, 200), lit=Color(190, 225, 245)),))
render_frame("ultrathink", 0, ice)
```

A custom palette is stretched the same way the default one is: two entries make
a two-colour gradient, one makes a single colour. `gradient` exposes that
stretch on its own, in case you want the colours a string would be painted in
without rendering a frame:

```python
from neonify import RAINBOW, gradient

gradient(RAINBOW, len("ultrathink"))  # ten hues, red at one end, violet at the other
```

`AnimationConfig` also takes `style`, `frame_limit`, the output stream and the
`sleep` function, so the loop can be driven without a clock or a terminal:

```python
from neonify import AnimationConfig, GlowStyle, animate

animate(
    "ultrathink",
    AnimationConfig(style=GlowStyle(is_reversed=True), frame_limit=10),
)
```

## Limitations

- The text has to fit on one line. Anything wider than the terminal, or
  containing a line break, is printed as a single frame instead — repainting in
  place cannot reach a line that has already wrapped or scrolled.
- 24-bit colour is required. Terminals without truecolor support show
  approximated colours, or none at all.
- Colours are assigned per code point, not per grapheme cluster. Plain text —
  including CJK — and standalone emoji are fine, but a ZWJ sequence such as
  `👨‍👩‍👧` is split into its parts and renders as separate emoji.
