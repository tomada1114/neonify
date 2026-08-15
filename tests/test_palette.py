from __future__ import annotations

import pytest

from neonify import RAINBOW, Color

PALETTE_SIZE = 7


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
        RAINBOW[0].red = 0  # type: ignore[misc]


def test_rainbow_has_seven_distinct_colors():
    assert len(RAINBOW) == PALETTE_SIZE
    assert len(set(RAINBOW)) == PALETTE_SIZE
