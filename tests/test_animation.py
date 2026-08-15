from __future__ import annotations

import pytest

from neonify import RAINBOW, Color, GlowStyle, render_frame

RESET = "\x1b[0m"


def _paint(index: int) -> str:
    return RAINBOW[index % len(RAINBOW)].foreground


def test_render_frame_gives_neighbouring_characters_consecutive_colors():
    assert render_frame("abc", 0) == f"{_paint(0)}a{_paint(1)}b{_paint(2)}c{RESET}"


def test_render_frame_advances_one_palette_step_per_frame():
    assert render_frame("a", 1) == f"{_paint(1)}a{RESET}"
    assert render_frame("a", 2) == f"{_paint(2)}a{RESET}"


def test_render_frame_wraps_around_the_end_of_the_palette():
    assert render_frame("a", len(RAINBOW)) == render_frame("a", 0)


def test_render_frame_accepts_a_negative_step():
    assert render_frame("a", -1) == f"{_paint(len(RAINBOW) - 1)}a{RESET}"


def test_render_frame_slides_colors_towards_the_start_of_the_string():
    """A colour shown on the second character reappears on the first next frame."""
    step = 3
    travelling = _paint(step + 1)
    assert f"{travelling}b" in render_frame("ab", step)
    assert f"{travelling}a" in render_frame("ab", step + 1)


def test_render_frame_reversed_slides_colors_towards_the_end_of_the_string():
    travelling = _paint(3)
    style = GlowStyle(is_reversed=True)
    assert f"{travelling}a" in render_frame("ab", 3, style)
    assert f"{travelling}b" in render_frame("ab", 4, style)


def test_render_frame_empty_text_returns_an_empty_string():
    assert render_frame("", 0) == ""


def test_render_frame_leaves_whitespace_uncolored_but_keeps_its_position():
    assert render_frame("a b", 0) == f"{_paint(0)}a {_paint(2)}b{RESET}"


def test_render_frame_all_whitespace_emits_no_escape_sequences():
    assert render_frame("   ", 0) == "   "


def test_render_frame_uses_a_custom_palette():
    only = Color(1, 2, 3)
    style = GlowStyle(palette=(only,))
    assert (
        render_frame("ab", 5, style) == f"{only.foreground}a{only.foreground}b{RESET}"
    )


def test_glow_style_rejects_an_empty_palette():
    with pytest.raises(ValueError, match="at least one colour"):
        GlowStyle(palette=())
