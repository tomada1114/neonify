# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `neonify` command that sweeps a shine across a string whose characters each
  hold one colour of a seven-colour palette, repainting one line in place until
  interrupted. The text defaults to `ultrathink`.
- `--interval`, `--reverse` and `--once` options. A single mid-sweep frame is
  printed instead of animating when stdout is not a terminal or the text is
  wider than the terminal, and `NO_COLOR` prints the bare text.
- Public API: `render_frame`, `animate`, `AnimationConfig`, `GlowStyle`,
  `Color`, `Hue`, the `RAINBOW` palette, and the `SHINE_WIDTH` and
  `REST_FRAMES` constants that shape the sweep.

[Unreleased]: https://github.com/tomada1114/neonify/commits/main
