from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


class FakeTerminal(io.StringIO):
    """An in-memory stream that reports itself as a terminal.

    Passing ``interrupt_at`` makes the nth write raise ``KeyboardInterrupt``,
    which is how a test stands in for the user pressing Ctrl-C mid-animation
    without needing a real clock or a real terminal.
    """

    def __init__(self, interrupt_at: int | None = None) -> None:
        super().__init__()
        self._interrupt_at = interrupt_at
        self.write_count = 0

    def isatty(self) -> bool:
        return True

    def write(self, s: str) -> int:
        self.write_count += 1
        if self.write_count == self._interrupt_at:
            raise KeyboardInterrupt
        return super().write(s)


@pytest.fixture
def make_terminal() -> Callable[..., FakeTerminal]:
    def _make(interrupt_at: int | None = None) -> FakeTerminal:
        return FakeTerminal(interrupt_at)

    return _make
