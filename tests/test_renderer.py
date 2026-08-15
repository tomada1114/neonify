from __future__ import annotations

import pytest

from neonify import AnimationConfig, animate, render_frame

HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"


class _FakeClock:
    """A clock that only moves when the code under test moves it.

    ``render_cost`` is charged on every reading, standing in for the time a
    real terminal spends drawing a frame.
    """

    def __init__(self, render_cost: float = 0.0) -> None:
        self.now = 0.0
        self.delays: list[float] = []
        self._render_cost = render_cost

    def time(self) -> float:
        self.now += self._render_cost
        return self.now

    def sleep(self, delay: float) -> None:
        self.delays.append(delay)
        self.now += delay


def _config(clock, **overrides):
    return AnimationConfig(sleep=clock.sleep, clock=clock.time, **overrides)


def test_animate_stops_at_the_frame_limit(make_terminal):
    clock = _FakeClock()
    config = _config(clock, frame_limit=3, stream=make_terminal())

    assert animate("ab", config) == 3
    assert len(clock.delays) == 3


def test_animate_repaints_the_same_line_for_every_frame(make_terminal):
    terminal = make_terminal()

    animate("ab", _config(_FakeClock(), frame_limit=2, stream=terminal))

    assert terminal.getvalue() == (
        f"{HIDE_CURSOR}"
        f"\r{render_frame('ab', 0)}"
        f"\r{render_frame('ab', 1)}"
        f"{SHOW_CURSOR}\n"
    )


def test_animate_converts_the_interval_to_seconds(make_terminal):
    clock = _FakeClock()

    animate("a", _config(clock, interval_ms=95, frame_limit=2, stream=make_terminal()))

    assert clock.delays == pytest.approx([0.095, 0.095])


def test_animate_subtracts_drawing_time_from_the_next_wait(make_terminal):
    """Drawing must not stretch the cadence beyond the requested interval."""
    clock = _FakeClock(render_cost=0.02)

    animate("a", _config(clock, interval_ms=95, frame_limit=3, stream=make_terminal()))

    assert clock.delays == pytest.approx([0.075, 0.075, 0.075])


def test_animate_resynchronises_when_drawing_outruns_the_interval(make_terminal):
    """A frame slower than the interval must not queue up catch-up frames."""
    clock = _FakeClock(render_cost=0.5)

    animate("a", _config(clock, interval_ms=95, frame_limit=3, stream=make_terminal()))

    assert clock.delays == []


def test_animate_restores_the_cursor_when_interrupted(make_terminal):
    # The first write is the hidden cursor; the second is the frame that Ctrl-C
    # lands on.
    terminal = make_terminal(interrupt_at=2)

    assert animate("a", _config(_FakeClock(), stream=terminal)) == 0
    assert terminal.getvalue() == f"{HIDE_CURSOR}{SHOW_CURSOR}\n"


def test_animate_zero_frame_limit_still_restores_the_cursor(make_terminal):
    terminal = make_terminal()

    assert animate("a", _config(_FakeClock(), frame_limit=0, stream=terminal)) == 0
    assert terminal.getvalue() == f"{HIDE_CURSOR}{SHOW_CURSOR}\n"


@pytest.mark.parametrize("interval", [0, -1])
def test_animation_config_rejects_a_non_positive_interval(interval):
    with pytest.raises(ValueError, match="interval_ms must be positive"):
        AnimationConfig(interval_ms=interval)


def test_animation_config_rejects_a_negative_frame_limit():
    with pytest.raises(ValueError, match="frame_limit must not be negative"):
        AnimationConfig(frame_limit=-1)
