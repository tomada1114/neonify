# Project Guide

## Overview

`neonify` is a terminal toy: every character of a string keeps one colour of a
seven-colour palette, and a three-character shine sweeps across them, repainting
one line in place. It is built with [uv](https://docs.astral.sh/uv/)
and [hatchling](https://hatch.pypa.io/), using a strict `src/` layout with
comprehensive type checking and linting.

## Quick Reference

```bash
just install   # Install dependencies and git hooks when .git/ is present
just setup     # Alias for just install (first-time setup)
just fmt       # Format code (ruff check --fix + ruff format)
just lint      # Lint (ruff check) + type check (mypy)
just test      # Run tests with coverage
just smoke     # Build and verify the wheel in a temp virtual environment
just check     # Run all checks: fmt → lint → test
just docs      # Serve docs locally
just build     # Build distribution packages
just clean     # Remove build artifacts and caches
```

Without Just: replace `just <cmd>` with the corresponding `uv run` commands
in the `justfile`. Run a single test with
`uv run pytest tests/test_<module>.py::test_<name>`.

## Architecture

```
src/neonify/
├── __init__.py    # Public API — export everything users need here
├── py.typed       # PEP 561 marker for typed package
├── palette.py     # The seven-colour palette and its 24-bit ANSI encoding
├── animation.py   # Pure frame composition: which character is which colour
├── renderer.py    # The render loop and its terminal side effects
└── cli.py         # The `neonify` command
```

The layers run one way: `cli` → `renderer` → `animation` → `palette`. Keeping
frame composition pure is what lets the tests cover the animation without a
clock or a terminal; `renderer` takes its stream and its `sleep` by injection
for the same reason.

- Keep the public API surface small — export via `__init__.py.__all__`
- `cli.py` imports `__version__` from the package, so `__init__.py` must never
  import `cli` back
- Internal modules can use a leading underscore (`_internal.py`)
- Separate concerns: one module per logical unit
- Update `docs/reference.md` and README examples whenever you change the public API

## Review Checklist

Before submitting a PR:

1. `just check` passes (format, lint, type check, tests)
2. New public APIs have type annotations and docstrings
3. Tests cover the new functionality
4. No unnecessary dependencies added

## Important Reminders

- All code, docs, commits, and PRs must be written in English
- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files unless explicitly requested
- Dependencies should always be added to the appropriate group in pyproject.toml
