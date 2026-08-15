"""The terminal render loop."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

from .animation import GlowStyle, render_frame

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TextIO

DEFAULT_INTERVAL_MS: Final = 95
"""Frame interval measured off the reference recording."""

MS_PER_SECOND: Final = 1000
HIDE_CURSOR: Final = "\x1b[?25l"
SHOW_CURSOR: Final = "\x1b[?25h"
LINE_START: Final = "\r"


def _default_stream() -> TextIO:
    """Return the stream frames go to when the caller configures none.

    Read when the config is built rather than captured at import time, so a
    ``sys.stdout`` redirected after import is still honoured.
    """
    return sys.stdout


@dataclass(frozen=True, slots=True)
class AnimationConfig:
    """Everything the render loop needs besides the text itself.

    Attributes:
        style: The palette and direction to animate with.
        interval_ms: Milliseconds between frames.
        frame_limit: Stop after this many frames. ``None`` loops until
            interrupted.
        stream: Where frames are written.
        sleep: The delay function, injectable so tests need no real clock.
        clock: The monotonic clock the cadence is measured against, injectable
            for the same reason.
    """

    style: GlowStyle = field(default_factory=GlowStyle)
    interval_ms: int = DEFAULT_INTERVAL_MS
    frame_limit: int | None = None
    stream: TextIO = field(default_factory=_default_stream)
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic

    def __post_init__(self) -> None:
        """Reject timings the loop could not honour.

        Raises:
            ValueError: If the interval is not positive, or the frame limit is
                negative.
        """
        if self.interval_ms <= 0:
            msg = f"interval_ms must be positive, got {self.interval_ms}."
            raise ValueError(msg)
        if self.frame_limit is not None and self.frame_limit < 0:
            msg = f"frame_limit must not be negative, got {self.frame_limit}."
            raise ValueError(msg)


def animate(text: str, config: AnimationConfig | None = None) -> int:
    """Loop the glow over *text* until interrupted or the frame limit is hit.

    The cursor is hidden for the duration and the line is repainted in place,
    so the animation never scrolls the terminal. The cursor is always restored
    and the line closed, even when the loop is interrupted.

    Each frame is scheduled against a deadline rather than slept on for the
    full interval, so the time spent drawing does not stretch the cadence.

    Args:
        text: The string to animate.
        config: Timing, styling and output settings. Defaults to the reference
            95 ms rainbow on stdout.

    Returns:
        The number of frames written.
    """
    config = config if config is not None else AnimationConfig()
    stream = config.stream
    delay = config.interval_ms / MS_PER_SECOND
    frames = 0

    stream.write(HIDE_CURSOR)
    try:
        deadline = config.clock()
        while config.frame_limit is None or frames < config.frame_limit:
            stream.write(LINE_START + render_frame(text, frames, config.style))
            stream.flush()
            frames += 1
            deadline += delay
            remaining = deadline - config.clock()
            if remaining > 0:
                config.sleep(remaining)
            else:
                # Drawing fell behind the cadence. Resynchronise instead of
                # firing a burst of catch-up frames.
                deadline = config.clock()
    except KeyboardInterrupt:
        # Ctrl-C is how this animation is meant to end, not a failure.
        pass
    finally:
        stream.write(SHOW_CURSOR + "\n")
        stream.flush()
    return frames
