"""Headless smoke tests — exercise the REPL paths without a real terminal.

These drive the interactive loop via a prompt_toolkit pipe input, so a renamed
or mistyped config field (which only shows up on the interactive path) fails
here instead of in front of a user.

Run:  python tests/test_smoke.py      (or: pytest)
"""

from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

import partnuh
from partnuh import Box, CliConfig, Cursor, Separator, Spinner, TextDelta


def _fake(prompt, session_id):
    for word in ("hello ", "there"):
        yield TextDelta(word)


def _drive(config, keystrokes="hi\rmore\r/quit\r"):
    """Run an interactive session to completion against piped keystrokes."""
    with create_pipe_input() as inp:
        inp.send_text(keystrokes)
        with create_app_session(input=inp, output=DummyOutput()):
            partnuh.wrap(_fake, name="Smoke", config=config)


def test_interactive_defaults():
    _drive(CliConfig())


def test_interactive_fully_customized():
    _drive(CliConfig(
        prompt_sequence="~> ", prompt_style="fg:#00d7af", cursor=Cursor.BEAM,
        accent_style="magenta", banner_border_style="cyan", banner_box=Box.DOUBLE,
        separator=Separator.HEAVY, separator_style="cyan",
        thinking_spinner=Spinner.ARC, answering_spinner=Spinner.TOGGLE,
        stream_speed=0.0,
    ))


def test_one_shot():
    partnuh.wrap(_fake, name="Smoke", prompt="hi", config=CliConfig())


if __name__ == "__main__":
    test_interactive_defaults()
    test_interactive_fully_customized()
    test_one_shot()
    print("all smoke tests passed")
