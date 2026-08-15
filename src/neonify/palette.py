"""The palette the shine travels over, and its 24-bit ANSI encoding.

Every colour here was measured pixel by pixel off the reference: the resting
colours and three of the lit ones from lossless screenshots, the rest from the
recording, corrected for the constant bias the codec showed on the colours that
appear in both. The lit colours are stored rather than derived, because no
single lightening rule reproduces them — mixing towards white in sRGB, in
linear light, in HSL and in Oklab each leave at least one channel thirteen steps
out of 255 adrift, however the mix is weighted. ``docs/measurements.md`` has the
fits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

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
