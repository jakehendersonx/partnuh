"""Fast unit tests — no terminal, no network.

Covers the wiring that's easy to break: agent adaptation, config override
merging, presets, the pacer's event rendering, and the demo agent.

Run:  python tests/test_unit.py      (or: pytest)
"""

from contextlib import redirect_stdout
from io import StringIO

from rich.console import Console

import partnuh
from partnuh import (
    Box,
    Cli,
    CliConfig,
    Cursor,
    Prompt,
    Separator,
    Spinner,
    TextDelta,
    ToolCallStarted,
    ToolInfo,
    ToolResult,
)
from partnuh.adapt import adapt
from partnuh.cli import _separator_line
from partnuh.pacer import Pacer


def _fake(prompt, session_id):
    yield TextDelta("ok")


# --- adapt() ---------------------------------------------------------------

def test_adapt_callable():
    a = adapt(_fake, name="Fn")
    assert a.name == "Fn"
    assert callable(a.stream)


def test_adapt_passthrough():
    # An object that's already a CliAgent is returned unchanged.
    built = partnuh.from_callable(_fake, name="X", model="m")
    assert adapt(built) is built


def test_adapt_unknown_raises():
    try:
        adapt(42)
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError for an un-adaptable object")


# --- Cli / config merge ----------------------------------------------------

def test_config_override_merges():
    cli = Cli(_fake, name="X", prompt_sequence="~> ", stream_speed=0.5)
    assert cli.config.prompt_sequence == "~> "
    assert cli.config.stream_speed == 0.5
    # untouched fields keep defaults
    assert cli.config.banner is True


def test_config_unknown_field_raises():
    try:
        Cli(_fake, name="X", not_a_field=1)
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError for an unknown CliConfig field")


def test_resolved_token_delay():
    assert CliConfig(stream_speed=0.0).resolved_token_delay() == 0.0
    assert CliConfig(token_delay=0.01).resolved_token_delay() == 0.01
    # token_delay wins over stream_speed
    assert CliConfig(stream_speed=1.0, token_delay=0.0).resolved_token_delay() == 0.0


# --- presets ---------------------------------------------------------------

def test_presets_are_plain_strings():
    assert Prompt.BAR == "▌ "
    assert isinstance(Cursor.BEAM, str)
    assert isinstance(Spinner.DOTS, str)
    assert isinstance(Box.DOUBLE, str)
    assert isinstance(Separator.HEAVY, str)


# --- pacer rendering -------------------------------------------------------

def test_pacer_renders_text_and_tools():
    buf = StringIO()
    console = Console(file=buf, force_terminal=False, width=80)
    pacer = Pacer(console, delay=0.0, answering_spinner=None,
                  tool_call_prefix="⚙ ", tool_result_prefix="→ ")
    with redirect_stdout(buf):
        printed = pacer.render([
            ToolCallStarted("add", {"a": 1, "b": 2}),
            ToolResult("add", 3),
            TextDelta("answer"),
        ])
    out = buf.getvalue()
    assert printed is True
    assert "add(a=1, b=2)" in out
    assert "3" in out
    assert "answer" in out


def test_pacer_bracket_prefix_is_literal():
    # A prefix containing [..] must not be parsed as rich markup.
    buf = StringIO()
    console = Console(file=buf, force_terminal=False, width=80)
    pacer = Pacer(console, delay=0.0, answering_spinner=None, tool_call_prefix="[tool] ")
    pacer.render([ToolCallStarted("add", {"a": 1})])
    assert "[tool] add(a=1)" in buf.getvalue()


# --- separator -------------------------------------------------------------

def test_separator_line_uses_config_char():
    t = _separator_line(CliConfig(separator="━"))
    assert set(t.plain) == {"━"}
    assert len(t.plain) > 0


# --- banner ----------------------------------------------------------------

def test_banner_renders_with_custom_label_style():
    import partnuh.cli as climod

    buf = StringIO()
    old = climod.console
    climod.console = Console(file=buf, force_terminal=False, width=90)
    try:
        class A:
            name = "N"
            model = "m"
            tools = [ToolInfo("add", "x")]

        climod.display_banner(A(), CliConfig(banner_label_style="magenta"))
    finally:
        climod.console = old
    out = buf.getvalue()
    assert "name:" in out and "tools: add" in out and "directory:" in out


# --- demo agent ------------------------------------------------------------

def test_demo_agent_is_deterministic():
    agent = partnuh.demo_agent(name="Demo")
    out1 = "".join(e.text for e in agent.stream("anything", "s1"))
    out2 = "".join(e.text for e in agent.stream("something else", "s2"))
    assert out1 == out2                      # ignores the prompt — fully deterministic
    assert "To be, or not to be" in out1
    assert "\n" in out1                      # line breaks preserved


def test_demo_agent_custom_script_and_echo():
    agent = partnuh.demo_agent("hello world", name="Echo", echo_prompt=True)
    out = "".join(e.text for e in agent.stream("hi there", "s"))
    assert "You said: hi there" in out
    assert out.rstrip().endswith("hello world")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print(f"all {len(fns)} unit tests passed")
