"""Mapping the palette onto a string, one frame at a time."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .palette import RAINBOW, RESET

if TYPE_CHECKING:
    from .palette import Color


@dataclass(frozen=True, slots=True)
class GlowStyle:
    """How the palette travels across the characters of a string.

    Attributes:
        palette: The colours to cycle through, in the order they appear.
        is_reversed: Flow the colours left to right instead of right to left.
    """

    palette: tuple[Color, ...] = RAINBOW
    is_reversed: bool = False

    def __post_init__(self) -> None:
        """Reject a palette with nothing to cycle through.

        Raises:
            ValueError: If the palette is empty.
        """
        if not self.palette:
            msg = "A glow style needs at least one colour."
            raise ValueError(msg)


def _color_for(position: int, step: int, style: GlowStyle) -> Color:
    """Return the colour of the character at *position* on frame *step*.

    Neighbouring characters sit one entry apart in the palette, so advancing
    *step* slides every colour one position towards the start of the string.
    """
    offset = -position if style.is_reversed else position
    return style.palette[(step + offset) % len(style.palette)]


def render_frame(text: str, step: int, style: GlowStyle | None = None) -> str:
    """Return *text* with the ANSI colours of a single frame applied.

    Whitespace is emitted uncoloured — painting it would be invisible anyway —
    but it still occupies a position, so the rainbow keeps flowing at an even
    rate across words.

    Args:
        text: The string to colour.
        step: The frame number. Any integer; it wraps over the palette.
        style: The palette and direction to use. Defaults to the rainbow
            flowing right to left.

    Returns:
        The coloured string, terminated by a reset sequence when at least one
        colour was emitted.
    """
    style = style if style is not None else GlowStyle()
    parts: list[str] = []
    has_color = False
    for position, character in enumerate(text):
        if character.isspace():
            parts.append(character)
            continue
        parts.append(f"{_color_for(position, step, style).foreground}{character}")
        has_color = True
    if has_color:
        parts.append(RESET)
    return "".join(parts)
