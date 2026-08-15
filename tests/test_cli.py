from __future__ import annotations

import os
import sys

import pytest

from neonify import render_frame
from neonify.cli import DEFAULT_TEXT, main

HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
USAGE_ERROR = 2


@pytest.fixture(autouse=True)
def _without_no_color(monkeypatch):
    # The animation is the whole point of the tool, so the suite must not
    # inherit a NO_COLOR that silently disables it.
    monkeypatch.delenv("NO_COLOR", raising=False)


@pytest.fixture
def set_terminal_width(monkeypatch):
    # The real width would otherwise decide whether the animation runs.
    def _set(columns):
        monkeypatch.setattr(
            "shutil.get_terminal_size", lambda *_: os.terminal_size((columns, 24))
        )

    return _set


def test_main_help_exits_successfully(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    assert exit_info.value.code == 0
    assert "glow" in capsys.readouterr().out


def test_main_version_reports_the_package_version(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.startswith("neonify ")


def test_main_prints_a_single_frame_when_stdout_is_not_a_terminal(capsys):
    assert main(["ultrathink"]) == 0
    assert capsys.readouterr().out == f"{render_frame('ultrathink', 0)}\n"


def test_main_once_prints_a_single_frame(capsys):
    assert main(["--once", "ultrathink"]) == 0
    assert capsys.readouterr().out == f"{render_frame('ultrathink', 0)}\n"


def test_main_without_text_falls_back_to_the_default_string(capsys):
    assert main(["--once"]) == 0
    assert capsys.readouterr().out == f"{render_frame(DEFAULT_TEXT, 0)}\n"


def test_main_no_color_prints_plain_text(capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")

    assert main(["ultrathink"]) == 0
    assert capsys.readouterr().out == "ultrathink\n"


def test_main_reverse_changes_the_direction(capsys):
    main(["--once", "--reverse", "ab"])
    reversed_output = capsys.readouterr().out
    main(["--once", "ab"])
    forward_output = capsys.readouterr().out

    assert reversed_output != forward_output


@pytest.mark.parametrize("interval", ["0", "-5"])
def test_main_rejects_a_non_positive_interval(interval, capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--interval", interval, "ultrathink"])

    assert exit_info.value.code == USAGE_ERROR
    assert "positive" in capsys.readouterr().err


def test_main_animates_when_stdout_is_a_terminal(
    monkeypatch, make_terminal, set_terminal_width
):
    # The second write is the first frame; interrupting there stands in for
    # the user pressing Ctrl-C.
    terminal = make_terminal(interrupt_at=2)
    monkeypatch.setattr(sys, "stdout", terminal)
    set_terminal_width(80)

    assert main(["ultrathink"]) == 0
    assert terminal.getvalue().endswith(f"{SHOW_CURSOR}\n")


def test_main_prints_one_frame_when_the_text_is_wider_than_the_terminal(
    monkeypatch, make_terminal, set_terminal_width, capsys
):
    terminal = make_terminal()
    monkeypatch.setattr(sys, "stdout", terminal)
    set_terminal_width(4)

    assert main(["a-string-far-too-long"]) == 0
    assert HIDE_CURSOR not in terminal.getvalue()
    assert "wider than the terminal" in capsys.readouterr().err


def test_main_prints_one_frame_when_the_text_contains_a_line_break(
    monkeypatch, make_terminal, set_terminal_width, capsys
):
    # A carriage return only reaches the start of the last line, so animating
    # multi-line text would scroll a fresh copy in on every frame.
    terminal = make_terminal()
    monkeypatch.setattr(sys, "stdout", terminal)
    set_terminal_width(80)

    assert main(["a\nb"]) == 0
    assert HIDE_CURSOR not in terminal.getvalue()
    assert "spans more than one line" in capsys.readouterr().err


def test_main_counts_east_asian_characters_as_two_columns(
    monkeypatch, make_terminal, set_terminal_width, capsys
):
    terminal = make_terminal()
    monkeypatch.setattr(sys, "stdout", terminal)
    set_terminal_width(6)  # "こんにちは" is 5 code points but 10 columns wide

    assert main(["こんにちは"]) == 0
    assert "wider than the terminal" in capsys.readouterr().err
