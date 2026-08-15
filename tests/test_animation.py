from __future__ import annotations

import re

import pytest

from neonify import (
    RAINBOW,
    REST_FRAMES,
    SHINE_WIDTH,
    Color,
    GlowStyle,
    Hue,
    gradient,
    render_frame,
)

RESET = "\x1b[0m"
ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
TEXT = "ultrathink"
REFERENCE_CYCLE = 30
"""Frames one cycle takes for the reference string, measured off the recording."""


def _painted(text: str, step: int, style: GlowStyle | None = None) -> list[str]:
    """The escape sequence each character of *text* is painted with.

    Whitespace comes back as an empty string. Matching whole frames would tie
    the tests to the exact byte layout; matching substrings would confuse two
    characters that share a colour, which any string longer than the palette
    has.
    """
    frame = render_frame(text, step, style)
    colors: list[str] = []
    index = 0
    while index < len(frame):
        match = ESCAPE.match(frame, index)
        if match is None:
            colors.append("")
        else:
            index = match.end()
            if index == len(frame):
                break  # the trailing reset paints no character
            colors.append(match.group())
        index += 1
    return colors


def _lit_positions(text: str, step: int, style: GlowStyle | None = None) -> list[int]:
    """The positions painted in their lit colour on frame *step*."""
    hues = gradient((style if style is not None else GlowStyle()).palette, len(text))
    return [
        position
        for position, color in enumerate(_painted(text, step, style))
        if color == hues[position].lit.foreground
    ]


def _cycle(text: str) -> int:
    return len(text) + SHINE_WIDTH - 1 + REST_FRAMES


def _resting(text: str) -> int:
    """A frame number on which the shine is off the string entirely."""
    return _cycle(text) - 1


def test_render_frame_paints_the_ends_in_the_ends_of_the_palette():
    """However long the text, it runs from the first colour to the last."""
    painted = _painted(TEXT, _resting(TEXT))

    assert painted[0] == RAINBOW[0].base.foreground
    assert painted[-1] == RAINBOW[-1].base.foreground


def test_render_frame_stretches_a_short_string_over_the_whole_palette():
    """Three characters land on the two ends and the middle entry between them."""
    expected = [RAINBOW[index].base.foreground for index in (0, 3, 6)]

    assert _painted("abc", _resting("abc")) == expected


def test_render_frame_gives_a_long_string_a_distinct_color_per_position():
    """A string longer than the palette gets intermediate colours, not repeats."""
    text = "a" * (len(RAINBOW) + 2)
    painted = _painted(text, _resting(text))

    assert len(set(painted)) == len(text)


def test_render_frame_keeps_a_characters_color_from_frame_to_frame():
    """Only the shine moves, so an unlit character never changes colour."""
    unlit = [
        _painted(TEXT, step)[9]
        for step in range(_cycle(TEXT))
        if 9 not in _lit_positions(TEXT, step)
    ]

    assert set(unlit) == {gradient(RAINBOW, len(TEXT))[9].base.foreground}


def test_render_frame_lights_three_characters_at_once():
    assert _lit_positions(TEXT, SHINE_WIDTH - 1) == [0, 1, 2]


def test_render_frame_advances_the_shine_one_character_per_frame():
    assert _lit_positions(TEXT, 5) == [3, 4, 5]
    assert _lit_positions(TEXT, 6) == [4, 5, 6]


def test_render_frame_leads_the_shine_in_from_the_left():
    """The shine enters leading edge first, so frame zero lights one character."""
    assert _lit_positions(TEXT, 0) == [0]


def test_render_frame_trails_the_shine_out_to_the_right():
    last = len(TEXT) - 1

    assert _lit_positions(TEXT, last + SHINE_WIDTH - 1) == [last]


def test_render_frame_rests_with_nothing_lit_once_the_shine_has_left():
    swept = len(TEXT) + SHINE_WIDTH - 1
    rests = [_lit_positions(TEXT, swept + rest) for rest in range(REST_FRAMES)]

    assert rests == [[] for _ in range(REST_FRAMES)]


def test_render_frame_matches_the_reference_cycle_for_the_reference_string():
    assert _cycle(TEXT) == REFERENCE_CYCLE
    assert render_frame(TEXT, REFERENCE_CYCLE) == render_frame(TEXT, 0)


def test_render_frame_accepts_a_negative_step():
    assert render_frame(TEXT, -_cycle(TEXT)) == render_frame(TEXT, 0)


def test_render_frame_reversed_leads_the_shine_in_from_the_right():
    style = GlowStyle(is_reversed=True)
    last = len(TEXT) - 1

    assert _lit_positions(TEXT, 0, style) == [last]
    assert _lit_positions(TEXT, 1, style) == [last - 1, last]


def test_render_frame_reversed_keeps_the_colors_where_they_are():
    """Reversing sweeps the shine the other way; it does not reorder the palette."""
    style = GlowStyle(is_reversed=True)

    assert _painted("abc", _resting("abc"), style) == _painted("abc", _resting("abc"))


def test_render_frame_single_character_is_lit_for_the_width_of_the_shine():
    lit_steps = [step for step in range(_cycle("a")) if _lit_positions("a", step)]

    assert lit_steps == list(range(SHINE_WIDTH))


def test_render_frame_long_text_keeps_the_shine_three_characters_wide():
    text = "a" * 200
    lead = 100

    assert _lit_positions(text, lead) == [lead - 2, lead - 1, lead]


def test_render_frame_empty_text_returns_an_empty_string():
    assert render_frame("", 0) == ""


def test_render_frame_leaves_whitespace_uncolored_but_keeps_its_position():
    """A space costs the shine a frame, so words either side stay in step."""
    # On frame 3 the shine covers positions 1 to 3: the space has already taken
    # its turn, and "b" is lit as the third position rather than the second.
    assert _painted("a b", 3) == [
        RAINBOW[0].base.foreground,
        "",
        RAINBOW[6].lit.foreground,
    ]


def test_render_frame_all_whitespace_emits_no_escape_sequences():
    assert render_frame("   ", 0) == "   "


def test_render_frame_uses_a_custom_palette():
    only = Hue(base=Color(1, 2, 3), lit=Color(4, 5, 6))
    style = GlowStyle(palette=(only,))

    assert (
        render_frame("ab", 0, style)
        == f"{only.lit.foreground}a{only.base.foreground}b{RESET}"
    )


def test_glow_style_rejects_an_empty_palette():
    with pytest.raises(ValueError, match="at least one colour"):
        GlowStyle(palette=())
