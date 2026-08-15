"""The palette the shine travels over, and its 24-bit ANSI encoding.

Every colour here was measured pixel by pixel off the reference: the resting
colours and three of the lit ones from lossless screenshots, the rest from the
recording, corrected for the constant bias the codec showed on the colours that
appear in both. The lit colours are stored rather than derived, because no
single lightening rule reproduces them — mixing towards white in sRGB, in
linear light, in HSL and in Oklab each leave at least one channel thirteen steps
out of 255 adrift, however the mix is weighted. ``docs/measurements.md`` has the
fits.

The measured colours are anchors rather than a sequence that repeats:
``gradient`` spans them across a string of any length, blending between
neighbouring entries for the positions that fall between them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Sequence

RESET: Final = "\x1b[0m"
"""Escape sequence that clears every active text attribute."""

MIN_CHANNEL: Final = 0
MAX_CHANNEL: Final = 255


@dataclass(frozen=True, slots=True)
class Color:
    """A 24-bit RGB colour.

    Attributes:
        red: Red channel, 0-255.
        green: Green channel, 0-255.
        blue: Blue channel, 0-255.
    """

    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        """Reject channel values no terminal could render.

        Type checking alone would not catch this: a float reaches the escape
        sequence as ``38;2;1.5;0;0`` and a bool as ``38;2;True;0;0``, both of
        which terminals silently ignore. ``bool`` needs rejecting explicitly
        because it is a subclass of ``int``.

        Raises:
            ValueError: If any channel is not an integer in the 8-bit range.
        """
        channels = (("red", self.red), ("green", self.green), ("blue", self.blue))
        for name, value in channels:
            is_valid = (
                isinstance(value, int)
                and not isinstance(value, bool)
                and MIN_CHANNEL <= value <= MAX_CHANNEL
            )
            if not is_valid:
                msg = (
                    f"Channel {name} must be an integer between {MIN_CHANNEL} "
                    f"and {MAX_CHANNEL}, got {value!r}."
                )
                raise ValueError(msg)

    @property
    def foreground(self) -> str:
        """The escape sequence that paints subsequent text in this colour."""
        return f"\x1b[38;2;{self.red};{self.green};{self.blue}m"


@dataclass(frozen=True, slots=True)
class Hue:
    """One entry of the palette, in the two brightnesses a character takes.

    Attributes:
        base: The colour the character rests at.
        lit: The colour it takes while the shine is over it.
    """

    base: Color
    lit: Color


RAINBOW: Final[tuple[Hue, ...]] = (
    Hue(Color(232, 85, 77), Color(250, 144, 136)),  # hue 3
    Hue(Color(244, 128, 77), Color(254, 177, 126)),  # hue 18
    Hue(Color(249, 187, 84), Color(253, 221, 142)),  # hue 37
    Hue(Color(135, 192, 119), Color(176, 227, 171)),  # hue 107
    Hue(Color(118, 160, 215), Color(173, 199, 235)),  # hue 214
    Hue(Color(144, 119, 192), Color(186, 173, 226)),  # hue 260
    Hue(Color(193, 119, 171), Color(226, 171, 203)),  # hue 318
)
"""The seven colours the reference gives to consecutive characters, in order."""


def _blend(start: Color, end: Color, ratio: float) -> Color:
    """Return the colour *ratio* of the way from *start* to *end*.

    The mix is a straight sRGB one. It only ever runs between two neighbouring
    entries of a palette, which sit close enough in hue that the detours a
    linear-light or Oklab mix would avoid are not there to avoid.
    """
    return Color(
        round(start.red + (end.red - start.red) * ratio),
        round(start.green + (end.green - start.green) * ratio),
        round(start.blue + (end.blue - start.blue) * ratio),
    )


def _hue_at(palette: Sequence[Hue], spot: float) -> Hue:
    """Return the hue *spot* of the way along *palette*, indexed by entry.

    A spot landing between two entries blends both of their brightnesses by the
    same ratio, so the shine stays as continuous across the string as the
    resting colours do.
    """
    index = min(int(spot), len(palette) - 2)
    ratio = spot - index
    start, end = palette[index], palette[index + 1]
    return Hue(
        base=_blend(start.base, end.base, ratio),
        lit=_blend(start.lit, end.lit, ratio),
    )


def gradient(palette: Sequence[Hue], length: int) -> tuple[Hue, ...]:
    """Return *length* hues spanning *palette* from its first entry to its last.

    The palette is stretched over the positions rather than handed out one
    entry per position and started over: the ends of the string always get the
    ends of the palette, and everything in between is spaced evenly along it.
    A string shorter than the palette therefore skips entries, and a longer one
    fills the gaps with blends of the two entries each position falls between.

    Args:
        palette: The colours to span, in order.
        length: How many positions to cover.

    Returns:
        One hue per position, first to last.

    Raises:
        ValueError: If *palette* is empty or *length* is negative.
    """
    if not palette:
        msg = "A gradient needs at least one colour."
        raise ValueError(msg)
    if length < 0:
        msg = f"A gradient length cannot be negative, got {length}."
        raise ValueError(msg)
    last = len(palette) - 1
    if last == 0 or length <= 1:
        return (palette[0],) * length
    return tuple(
        _hue_at(palette, position * last / (length - 1)) for position in range(length)
    )
