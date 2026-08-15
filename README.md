# neonify

[![CI](https://github.com/tomada1114/neonify/actions/workflows/ci.yml/badge.svg)](https://github.com/tomada1114/neonify/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Make any string glow with a shine that sweeps across it in your terminal.

## Install

```bash
uv tool install git+https://github.com/tomada1114/neonify
# or
pip install git+https://github.com/tomada1114/neonify
```

## Usage

```bash
neonify                              # animates "ultrathink" until you press Ctrl-C
neonify "hello world" -i 30 -r       # any string, faster, sweeping the other way
```

| Option | Default | What it does |
| --- | --- | --- |
| `text` | `ultrathink` | The string to make glow |
| `-i`, `--interval MS` | `50` | Milliseconds between frames |
| `-r`, `--reverse` | off | Sweep the shine right to left instead |
| `--once` | off | Print a single frame and exit |

A seven-colour palette is stretched across the string, so the first character
takes the red at one end and the last takes the violet at the other, and a
three-character shine sweeps across them, repainting one line in place.

## Python API

```python
from neonify import AnimationConfig, animate, render_frame

render_frame("ultrathink", 0)                           # one frame as an ANSI string
animate("ultrathink", AnimationConfig(interval_ms=30))  # loops until interrupted
```

`GlowStyle` takes a custom palette, `gradient` exposes the stretch on its own,
and `AnimationConfig` carries the stream and the clock — see the
[API Reference](https://tomada1114.github.io/neonify/reference/).

## Documentation

- [How it works](https://tomada1114.github.io/neonify/#how-it-works) — the
  sweep, the fallbacks, and what `neonify` will not do
- [API Reference](https://tomada1114.github.io/neonify/reference/)
- [Reference Measurements](https://tomada1114.github.io/neonify/measurements/) —
  where the palette, the shine and the timings came from
- [CONTRIBUTING.md](https://github.com/tomada1114/neonify/blob/main/CONTRIBUTING.md)
  — development setup

## License

[MIT](LICENSE)
