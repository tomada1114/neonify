"""Mapping the palette onto a string, one frame at a time."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from .palette import RAINBOW, RESET, gradient

if TYPE_CHECKING:
    from .palette import Hue

SHINE_WIDTH: Final = 3
"""How many neighbouring characters the shine lights at once."""

REST_FRAMES: Final = 18
"""Frames the string sits fully at rest between one sweep and the next."""


@dataclass(frozen=True, slots=True)
class GlowStyle:
    """How the shine travels across the characters of a string.

    Attributes:
        palette: The colours the characters are painted in, stretched across
            the string so its ends take the ends of the palette.
        is_reversed: Sweep the shine right to left instead of left to right.
    """

    palette: tuple[Hue, ...] = RAINBOW
    is_reversed: bool = False

    def __post_init__(self) -> None:
        """Reject a palette with nothing to hand out.

        Raises:
            ValueError: If the palette is empty.
        """
        if not self.palette:
            msg = "A glow style needs at least one colour."
            raise ValueError(msg)


def _cycle_length(text_length: int) -> int:
    """Return how many frames one sweep takes, rest included.

    The shine only clears the string once its trailing edge is past the last
    character, which is ``SHINE_WIDTH - 1`` frames after its leading edge got
    there. Only the sweep grows with the text: the rest is a fixed number of
    frames, so a short string flashes and waits while a long one gets a shine
    that takes proportionally longer to cross.
    """
    return text_length + SHINE_WIDTH - 1 + REST_FRAMES


def render_frame(text: str, step: int, style: GlowStyle | None = None) -> str:
    """Return *text* with the ANSI colours of a single frame applied.

    Each character keeps one colour for the whole animation, taken from the
    palette stretched across the string: the first character gets the first
    entry, the last gets the last, and the positions between are blended from
    the two entries they fall between. What moves is the shine, a band of
    ``SHINE_WIDTH`` characters that advances one position per frame and lights
    whatever it covers.

    Whitespace is emitted uncoloured — painting it would be invisible anyway —
    but it still occupies a position, so the shine keeps travelling at an even
    rate across words.

    One cycle takes ``len(text) + SHINE_WIDTH - 1 + REST_FRAMES`` frames, which
    is the period *step* wraps over, and the ``frame_limit`` that renders
    exactly one of them.

    Args:
        text: The string to colour.
        step: The frame number. Any integer; it wraps over the cycle.
        style: The palette and sweep direction to use. Defaults to the rainbow
            shining left to right.

    Returns:
        The coloured string, terminated by a reset sequence when at least one
        colour was emitted.
    """
    style = style if style is not None else GlowStyle()
    lead = step % _cycle_length(len(text))
    last = len(text) - 1
    hues = gradient(style.palette, len(text))
    parts: list[str] = []
    has_color = False
    for position, character in enumerate(text):
        if character.isspace():
            parts.append(character)
            continue
        hue = hues[position]
        travelled = last - position if style.is_reversed else position
        is_lit = 0 <= lead - travelled < SHINE_WIDTH
        parts.append(f"{(hue.lit if is_lit else hue.base).foreground}{character}")
        has_color = True
    if has_color:
        parts.append(RESET)
    return "".join(parts)
