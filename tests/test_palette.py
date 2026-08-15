from __future__ import annotations

import pytest

from neonify import RAINBOW, Color, Hue

PALETTE_SIZE = 7


def _lightness(color: Color) -> float:
    """The HSL lightness of *color*, on a 0-1 scale."""
    channels = (color.red, color.green, color.blue)
    return (max(channels) + min(channels)) / (2 * 255)


def test_color_foreground_emits_a_truecolor_escape():
    assert Color(242, 85, 85).foreground == "\x1b[38;2;242;85;85m"


@pytest.mark.parametrize(
    ("channels", "rejected"),
    [
        pytest.param((-1, 0, 0), "red", id="red-below-range"),
        pytest.param((0, 256, 0), "green", id="green-above-range"),
        pytest.param((0, 0, -5), "blue", id="blue-below-range"),
        pytest.param((1.5, 0, 0), "red", id="red-not-an-integer"),
        pytest.param((0, "12", 0), "green", id="green-not-an-integer"),
        pytest.param((True, 0, 0), "red", id="red-boolean-subclass-of-int"),
    ],
)
def test_color_rejects_a_channel_that_is_not_an_8bit_integer(channels, rejected):
    with pytest.raises(ValueError, match=rf"Channel {rejected} must be an integer"):
        Color(*channels)


@pytest.mark.parametrize(
    ("channels", "expected"),
    [
        pytest.param((0, 0, 0), "\x1b[38;2;0;0;0m", id="lower-boundary"),
        pytest.param((255, 255, 255), "\x1b[38;2;255;255;255m", id="upper-boundary"),
    ],
)
def test_color_accepts_the_range_boundaries(channels, expected):
    assert Color(*channels).foreground == expected


def test_color_is_immutable():
    with pytest.raises(AttributeError):
        RAINBOW[0].base.red = 0  # type: ignore[misc]


def test_hue_is_immutable():
    with pytest.raises(AttributeError):
        RAINBOW[0].base = Color(0, 0, 0)  # type: ignore[misc]


def test_hue_cannot_be_built_from_an_unrenderable_color():
    """A hue has no validation of its own; `Color` refuses before it is reached."""
    with pytest.raises(ValueError, match="Channel red must be an integer"):
        Hue(base=Color(300, 0, 0), lit=Color(0, 0, 0))


def test_rainbow_has_seven_distinct_hues():
    assert len(RAINBOW) == PALETTE_SIZE
    assert len(set(RAINBOW)) == PALETTE_SIZE


def test_rainbow_lit_colors_are_lighter_than_the_ones_they_replace():
    """The shine has to read as a shine on every hue, not just the bright ones."""
    assert all(_lightness(hue.lit) > _lightness(hue.base) for hue in RAINBOW)
