"""The rainbow palette and its 24-bit ANSI encoding.

The seven hues are taken verbatim from a frame-by-frame measurement of the
reference recording. Saturation and value are normalised across the palette
instead: the recording's chroma subsampling washed out the darker half of the
wheel, so its measured saturation is a property of the capture rather than of
the animation.
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


RAINBOW: Final[tuple[Color, ...]] = (
    Color(242, 85, 85),  # hue 0
    Color(242, 132, 85),  # hue 18
    Color(242, 182, 85),  # hue 37
    Color(122, 242, 85),  # hue 106
    Color(85, 148, 242),  # hue 216
    Color(148, 85, 242),  # hue 264
    Color(242, 85, 198),  # hue 317
)
"""The seven colours the reference animation cycles through, in order."""
