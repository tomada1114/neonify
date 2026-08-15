"""The ``neonify`` command."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import unicodedata
from typing import TYPE_CHECKING

from . import __version__
from .animation import GlowStyle, render_frame
from .renderer import DEFAULT_INTERVAL_MS, AnimationConfig, animate

if TYPE_CHECKING:
    from collections.abc import Sequence

WIDE_EAST_ASIAN_CLASSES = frozenset({"W", "F"})
LINE_BREAKS = frozenset("\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029")
"""Every character ``str.splitlines`` treats as ending a line."""


def _display_width(text: str) -> int:
    """Return how many terminal columns *text* occupies."""
    return sum(
        2 if unicodedata.east_asian_width(character) in WIDE_EAST_ASIAN_CLASSES else 1
        for character in text
    )


def _unanimatable_reason(text: str) -> str | None:
    """Return why *text* cannot be repainted in place, or ``None`` if it can.

    Repainting relies on a carriage return, which only reaches the start of the
    current line — so any text that occupies more than one line would scroll a
    fresh copy of itself into the terminal on every frame.
    """
    if LINE_BREAKS.intersection(text):
        return "the text spans more than one line"
    if _display_width(text) >= shutil.get_terminal_size().columns:
        return "the text is wider than the terminal"
    return None


def _build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the ``neonify`` command."""
    parser = argparse.ArgumentParser(
        prog="neonify",
        description="Make any string glow with a flowing rainbow in your terminal.",
        epilog="Press Ctrl-C to stop the animation.",
    )
    parser.add_argument("text", help="the string to make glow")
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_MS,
        metavar="MS",
        help="milliseconds between frames (default: %(default)s)",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="flow the colours left to right instead of right to left",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="print a single frame and exit instead of animating",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``neonify`` command.

    Animating only makes sense on a terminal that stays put, so a redirected
    stdout gets a single coloured frame and ``NO_COLOR`` gets the bare text.
    Text that cannot stay on one line — because it is wider than the terminal,
    or because it contains a line break — is treated the same way: repainting
    in place cannot reach a line that has scrolled.

    Args:
        argv: Command-line arguments, defaulting to ``sys.argv[1:]``.

    Returns:
        The process exit code.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.interval <= 0:
        parser.error("--interval must be a positive number of milliseconds")

    stream = sys.stdout
    if os.environ.get("NO_COLOR"):
        stream.write(f"{args.text}\n")
        return 0

    style = GlowStyle(is_reversed=args.reverse)
    single_frame = f"{render_frame(args.text, 0, style)}\n"
    if args.once or not stream.isatty():
        stream.write(single_frame)
        return 0

    reason = _unanimatable_reason(args.text)
    if reason is not None:
        sys.stderr.write(
            f"neonify: {reason}, so it cannot be animated in place; "
            "printing a single frame instead\n"
        )
        stream.write(single_frame)
        return 0

    animate(
        args.text,
        AnimationConfig(style=style, interval_ms=args.interval, stream=stream),
    )
    return 0
