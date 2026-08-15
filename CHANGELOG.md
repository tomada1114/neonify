# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `neonify` command that animates a flowing seven-colour rainbow across any
  string, repainting one line in place until interrupted.
- `--interval`, `--reverse` and `--once` options. A single frame is printed
  instead of animating when stdout is not a terminal or the text is wider than
  the terminal, and `NO_COLOR` prints the bare text.
- Public API: `render_frame`, `animate`, `AnimationConfig`, `GlowStyle`,
  `Color` and the `RAINBOW` palette.
