from __future__ import annotations

import pytest

from neonify import RAINBOW, Color, Hue, gradient

PALETTE_SIZE = 7

DARK = Hue(base=Color(0, 0, 0), lit=Color(10, 10, 10))
BRIGHT = Hue(base=Color(100, 200, 40), lit=Color(150, 250, 90))
TWO_TONE = (DARK, BRIGHT)


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


def test_gradient_ends_on_the_first_and_last_palette_colors():
    """Whatever the length, the red and the violet stay pinned to the ends."""
    stretched = gradient(RAINBOW, 40)

    assert stretched[0] == RAINBOW[0]
    assert stretched[-1] == RAINBOW[-1]


def test_gradient_returns_one_hue_per_position():
    assert len(gradient(RAINBOW, 40)) == 40


def test_gradient_reproduces_the_palette_when_the_lengths_line_up():
    assert gradient(RAINBOW, PALETTE_SIZE) == RAINBOW


def test_gradient_blends_the_hues_a_position_falls_between():
    """Halfway between two entries is the average of both their brightnesses."""
    assert gradient(TWO_TONE, 3)[1] == Hue(
        base=Color(50, 100, 20), lit=Color(80, 130, 50)
    )


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        pytest.param(1, Color(25, 50, 10), id="quarter"),
        pytest.param(2, Color(50, 100, 20), id="half"),
        pytest.param(3, Color(75, 150, 30), id="three-quarters"),
    ],
)
def test_gradient_moves_evenly_from_one_end_to_the_other(position, expected):
    assert gradient(TWO_TONE, 5)[position].base == expected


def test_gradient_gives_a_lone_character_the_first_color():
    """One character cannot span the palette; it takes the end it starts from."""
    assert gradient(RAINBOW, 1) == (RAINBOW[0],)


def test_gradient_of_no_positions_is_empty():
    assert gradient(RAINBOW, 0) == ()


def test_gradient_of_a_single_color_palette_paints_every_position_alike():
    assert gradient((DARK,), 4) == (DARK,) * 4


def test_gradient_rejects_an_empty_palette():
    with pytest.raises(ValueError, match="at least one colour"):
        gradient((), 4)


def test_gradient_rejects_a_negative_length():
    with pytest.raises(ValueError, match="cannot be negative"):
        gradient(RAINBOW, -1)
