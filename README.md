# neonify

[![CI](https://github.com/tomada1114/neonify/actions/workflows/ci.yml/badge.svg)](https://github.com/tomada1114/neonify/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/neonify)](https://pypi.org/project/neonify/)
[![Python](https://img.shields.io/pypi/pyversions/neonify)](https://pypi.org/project/neonify/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Make any string glow with a flowing rainbow in your terminal.

## Quickstart

```bash
uv tool install neonify
# or
pip install neonify
```

```bash
neonify max                          # animates in place until you press Ctrl-C
neonify "hello world" -i 60 -r       # faster, flowing the other way
```

## How it works

`neonify` cycles a seven-colour palette across the characters of a string.
Neighbouring characters sit one colour apart, and every frame advances the whole
string by one step — so each colour appears to travel from right to left. The
palette and the default 95 ms frame interval were measured frame by frame off a
reference recording.

| Option | Default | What it does |
| --- | --- | --- |
| `-i`, `--interval MS` | `95` | Milliseconds between frames |
| `-r`, `--reverse` | off | Flow the colours left to right instead |
| `--once` | off | Print a single frame and exit |

The animation repaints one line in place, so it never scrolls the terminal, and
the cursor is always restored when you stop it. Each frame is scheduled against
a deadline, so the time spent drawing does not stretch the interval.

When stdout is not a terminal — or the text is wider than the terminal —
`neonify` prints a single coloured frame instead of animating, and it honours
[`NO_COLOR`](https://no-color.org/) by printing the bare text.

## Python API

```python
from neonify import AnimationConfig, GlowStyle, animate, render_frame

render_frame("max", 0)  # a single frame as an ANSI-coloured string

animate("max", AnimationConfig(interval_ms=60))  # loops until interrupted
animate("max", AnimationConfig(style=GlowStyle(is_reversed=True), frame_limit=10))
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

## License

[MIT](LICENSE)
