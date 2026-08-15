# neonify

[![CI](https://github.com/tomada1114/neonify/actions/workflows/ci.yml/badge.svg)](https://github.com/tomada1114/neonify/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/neonify)](https://pypi.org/project/neonify/)
[![Python](https://img.shields.io/pypi/pyversions/neonify)](https://pypi.org/project/neonify/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Make any string glow with a shine that sweeps across it in your terminal.

## Quickstart

```bash
uv tool install neonify
# or
pip install neonify
```

```bash
neonify                              # animates "ultrathink" until you press Ctrl-C
neonify "hello world" -i 30 -r       # any string, faster, sweeping the other way
```

## How it works

`neonify` hands every character a colour from a seven-colour palette by position
and leaves it there. What moves is the shine: a band three characters wide that
advances one character per frame, lighting whatever it covers. Once it has left
the string the text rests for 18 frames before the next shine enters.

The palette — both the resting colours and the lit ones — the width of the
shine, and the default 50 ms frame interval were all measured off a reference
recording, in which `ultrathink` completes a cycle in 30 frames, or 1.5 seconds.
[Reference Measurements](https://tomada1114.github.io/neonify/measurements/)
records those measurements and how they were taken.

Only the sweep scales with the text, since the rest is a fixed number of frames.
A short string therefore flashes and waits, and a long one gets a shine that
takes proportionally longer to cross.

| Option | Default | What it does |
| --- | --- | --- |
| `text` | `ultrathink` | The string to make glow |
| `-i`, `--interval MS` | `50` | Milliseconds between frames |
| `-r`, `--reverse` | off | Sweep the shine right to left instead |
| `--once` | off | Print a single frame and exit |

The animation repaints one line in place, so it never scrolls the terminal, and
the cursor is always restored when you stop it. Each frame is scheduled against
a deadline, so the time spent drawing does not stretch the interval.

When stdout is not a terminal — or the text is wider than the terminal —
`neonify` prints a single coloured frame instead of animating, taken from the
middle of the sweep so the shine is on the string, and it honours
[`NO_COLOR`](https://no-color.org/) by printing the bare text.

## Python API

```python
from neonify import AnimationConfig, GlowStyle, animate, render_frame

render_frame("ultrathink", 0)  # a single frame as an ANSI-coloured string

animate("ultrathink", AnimationConfig(interval_ms=30))  # loops until interrupted
animate(
    "ultrathink",
    AnimationConfig(style=GlowStyle(is_reversed=True), frame_limit=10),
)
```

A palette entry is a `Hue`, pairing the colour a character rests at with the one
it takes under the shine, so a custom palette supplies both:

```python
from neonify import Color, GlowStyle, Hue, render_frame

ice = GlowStyle(palette=(Hue(base=Color(90, 150, 200), lit=Color(190, 225, 245)),))
render_frame("ultrathink", 0, ice)
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

## Development

See [CONTRIBUTING.md](https://github.com/tomada1114/neonify/blob/main/CONTRIBUTING.md)
for full setup instructions.

```bash
uv sync --all-groups
# Optional but recommended when working in a Git checkout
uv run pre-commit install --install-hooks
just check
```

`just install` installs pre-commit hooks automatically when the project lives in
a Git repository, and skips that step otherwise.

For packaging verification, run `just smoke` (or `uv build && uv run python scripts/smoke_test.py`)
to install the freshly built wheel into a temporary virtual environment and
confirm the distribution imports from the wheel, not from `src/`.

## Documentation

- [API Reference](https://tomada1114.github.io/neonify/reference/)
- [Reference Measurements](https://tomada1114.github.io/neonify/measurements/) —
  where the palette, the shine and the timings came from

## License

[MIT](LICENSE)
