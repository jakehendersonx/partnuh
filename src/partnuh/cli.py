"""The REPL: read multi-line input, stream the agent's reply, loop.

`wrap(agent)` is the one-call entry point. It runs interactively, or one-shot if
command-line args (or an explicit prompt) are given.
"""

from __future__ import annotations

import itertools
import os
import shutil
import sys
from dataclasses import dataclass, replace
from typing import Callable, Dict, List, Optional

import rich.box as rich_box
from rich.console import Console
from rich.text import Text

from prompt_toolkit.completion import FuzzyCompleter, NestedCompleter
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style

from .adapt import adapt
from .config import CliConfig
from .keymap import build_key_bindings
from .pacer import Pacer
from .protocol import CliAgent

console = Console()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@dataclass
class CommandResult:
    handled: bool = False
    should_exit: bool = False
    should_process: bool = False


class CommandDispatcher:
    def __init__(self, agent: CliAgent, config: CliConfig, session_id: str):
        self.agent = agent
        self.config = config
        self.session_id = session_id
        self.commands: Dict[str, Callable] = {
            "help": self._help,
            "quit": self._quit,
            "exit": self._quit,
            "tools": self._tools,
            "clear": self._clear,
        }
        for name, fn in (config.commands or {}).items():
            self.commands[name.lstrip("/")] = fn

    def dispatch(self, text: str) -> CommandResult:
        text = text.strip()
        if not text:
            return CommandResult(handled=True)
        if text.lower() in {"quit", "q", "exit", "/quit", "/exit"}:
            return self._quit(self, [])
        if text in {"/help", "/?"}:
            return self._help(self, [])
        if text.startswith("/"):
            parts = text[1:].split()
            if not parts:
                return CommandResult(should_process=True)
            handler = self.commands.get(parts[0].lower())
            if handler:
                result = handler(self, parts[1:])
                return result if isinstance(result, CommandResult) else CommandResult(handled=True)
        return CommandResult(should_process=True)

    def _help(self, _disp, _args) -> CommandResult:
        a = self.config.accent_style
        console.print()
        console.print(f"[{a}]/tools[/{a}] — list available tools")
        console.print(f"[{a}]/clear[/{a}] — clear conversation history")
        for name in (self.config.commands or {}):
            console.print(f"[{a}]/{name.lstrip('/')}[/{a}] — (custom)")
        console.print(f"[{a}]/help[/{a}]  — show commands")
        console.print(f"[{a}]/quit[/{a}]  — exit")
        console.print()
        return CommandResult(handled=True)

    def _quit(self, _disp, _args) -> CommandResult:
        return CommandResult(handled=True, should_exit=True)

    def _clear(self, _disp, _args) -> CommandResult:
        reset = getattr(self.agent, "reset", None)
        if callable(reset):
            reset(self.session_id)
            console.print("[green]✓[/green] conversation cleared\n")
        else:
            console.print("[yellow]This agent can't clear its history.[/yellow]\n")
        return CommandResult(handled=True)

    def _tools(self, _disp, _args) -> CommandResult:
        tools = list(getattr(self.agent, "tools", []) or [])
        if not tools:
            console.print("[yellow]No tools configured (chat-only).[/yellow]\n")
            return CommandResult(handled=True)
        a = self.config.accent_style
        console.print(f"\n[bold {a}]Available Tools:[/bold {a}]\n")
        for tool in tools:
            name = getattr(tool, "name", None) or str(tool)
            desc = (getattr(tool, "description", "") or "").strip().split("\n\n", 1)[0]
            console.print(f"[bold]{name}[/bold]\n  {desc or 'No description.'}\n")
        return CommandResult(handled=True)

    def completions(self) -> Dict:
        return {f"/{name}": None for name in self.commands}


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

_BOXES = {
    "rounded": rich_box.ROUNDED,
    "square": rich_box.SQUARE,
    "double": rich_box.DOUBLE,
    "heavy": rich_box.HEAVY,
    "ascii": rich_box.ASCII,
    "minimal": rich_box.MINIMAL,
    "simple": rich_box.SIMPLE,
    "horizontals": rich_box.HORIZONTALS,
    "none": rich_box.MINIMAL,
}


def display_banner(agent: CliAgent, config: CliConfig) -> None:
    from rich.markup import escape
    from rich.panel import Panel

    tools = list(getattr(agent, "tools", []) or [])
    tool_names = ", ".join(getattr(t, "name", "?") for t in tools) if tools else "none (chat-only)"
    rows = [
        ("name", getattr(agent, "name", "agent")),
        ("model", getattr(agent, "model", "?")),
        ("tools", tool_names),
        ("directory", os.getcwd()),
    ]
    ls = config.banner_label_style
    content = "\n".join(f"[{ls}]{label}:[/{ls}] {escape(str(value))}" for label, value in rows)
    plain = "\n".join(f"{label}: {value}" for label, value in rows)
    width = min(max(max(len(line) for line in plain.splitlines()) + 4, 50), 120)
    box = _BOXES.get(config.banner_box, rich_box.ROUNDED)
    console.print()
    console.print(Panel(content, border_style=config.banner_border_style, box=box, width=width))


def _separator_line(config: CliConfig) -> Text:
    """The divider drawn around a response, filled with config.separator."""
    width = min(shutil.get_terminal_size(fallback=(80, 20)).columns, 120)
    unit = config.separator or "-"
    line = (unit * (width // len(unit) + 1))[:width]
    return Text(line, style=config.separator_style)


def stream_response(agent: CliAgent, prompt: str, session_id: str, config: CliConfig) -> None:
    pacer = Pacer(
        console,
        delay=config.resolved_token_delay(),
        show_tool_calls=config.show_tool_calls,
        tool_call_prefix=config.tool_call_prefix,
        tool_result_prefix=config.tool_result_prefix,
        tool_style=config.tool_style,
        answering_spinner=config.answering_spinner,
        answering_text=config.answering_text,
        spinner_style=config.spinner_style,
    )
    try:
        events = agent.stream(prompt, session_id)
        first = None
        with console.status(config.thinking_text, spinner=config.thinking_spinner,
                            spinner_style=config.spinner_style):
            for ev in events:
                first = ev
                break
        if first is None:
            console.print()
            return
        pacer.render(itertools.chain([first], events))
    except Exception as e:  # noqa: BLE001 - surface any adapter error to the user
        console.print(Text(f"\nError: {e}", style="red"))
        return
    console.print("\n")


# ---------------------------------------------------------------------------
# The wrapped CLI
# ---------------------------------------------------------------------------

_CURSOR_SHAPES = {
    "block": CursorShape.BLOCK,
    "beam": CursorShape.BEAM,
    "underline": CursorShape.UNDERLINE,
    "blinking-block": CursorShape.BLINKING_BLOCK,
    "blinking-beam": CursorShape.BLINKING_BEAM,
    "blinking-underline": CursorShape.BLINKING_UNDERLINE,
}


def _interactive(agent, config: CliConfig, session_id: str) -> None:
    """The REPL loop. `agent` is assumed already adapted to a CliAgent."""
    dispatcher = CommandDispatcher(agent, config, session_id)

    if config.banner:
        display_banner(agent, config)
    dispatcher._help(None, None)

    try:
        completer = FuzzyCompleter(NestedCompleter.from_nested_dict(dispatcher.completions()))
    except AttributeError:
        completer = FuzzyCompleter(NestedCompleter(dispatcher.completions()))

    style = Style.from_dict({"prompt": config.prompt_style})
    prompt_tokens = [("class:prompt", config.prompt_sequence)]
    kb = build_key_bindings(config.newline_keys)
    cursor = _CURSOR_SHAPES.get(config.cursor) if config.cursor else None
    session = PromptSession(style=style, completer=completer, key_bindings=kb, cursor=cursor)

    try:
        while True:
            with patch_stdout():
                try:
                    text = session.prompt(
                        prompt_tokens,
                        multiline=config.multiline,
                        prompt_continuation=lambda w, l, s: prompt_tokens,
                        complete_while_typing=True,
                        reserve_space_for_menu=6,
                    )
                except EOFError:
                    break

            if not text:
                continue
            result = dispatcher.dispatch(text)
            if result.should_exit:
                break
            if result.handled and not result.should_process:
                continue
            if result.should_process:
                rule = _separator_line(config) if config.show_dividers else None
                if rule is not None:
                    console.print(rule)
                stream_response(agent, text, session_id, config)
                if rule is not None:
                    console.print(rule)
    except KeyboardInterrupt:
        pass


class Cli:
    """A partnuh CLI wrapped around an agent.

    Most of the time you don't build this directly — `partnuh.wrap(agent)` does
    it and launches. Construct a Cli yourself when you want the object without
    launching (e.g. to embed or test), then call `.start()`.

        cli = partnuh.Cli(agent, prompt_sequence="❯ ", stream_speed=0.3)
        cli.start()

    Accepts a `config=CliConfig(...)` and/or individual CliConfig fields as
    keyword overrides.
    """

    def __init__(self, agent, *, name: Optional[str] = None, model: Optional[str] = None,
                 config: Optional[CliConfig] = None, **overrides):
        self.agent = adapt(agent, name=name, model=model)
        base = config or CliConfig()
        self.config = replace(base, **overrides) if overrides else base

    def interactive(self, session_id: str = "main_session") -> "Cli":
        _interactive(self.agent, self.config, session_id)
        return self

    def once(self, prompt: str, session_id: str = "main_session") -> "Cli":
        stream_response(self.agent, prompt, session_id, self.config)
        return self

    def start(self, args: Optional[List[str]] = None, prompt: Optional[str] = None,
              session_id: str = "main_session") -> "Cli":
        """Launch: one-shot if `prompt`/`args` given, else interactive."""
        if args is None:
            args = sys.argv[1:]
        try:
            if prompt is not None:
                self.once(prompt, session_id)
            elif args:
                self.once(" ".join(args), session_id)
            else:
                self.interactive(session_id)
        except KeyboardInterrupt:
            sys.exit(130)
        return self


def wrap(agent, *, name: Optional[str] = None, model: Optional[str] = None,
         config: Optional[CliConfig] = None, args: Optional[List[str]] = None,
         prompt: Optional[str] = None, **overrides) -> Cli:
    """Wrap any agent in a partnuh CLI and launch it. One line, done.

        partnuh.wrap(agent)                                  # interactive REPL
        partnuh.wrap(agent, name="Private Caller")           # labelled banner
        partnuh.wrap(agent, prompt_sequence="❯ ", stream_speed=0.3)

    The agent is auto-wrapped (an existing CliAgent, a smolagents agent, or a
    stream function). One-shot if a `prompt` (or command-line args) is present,
    otherwise an interactive REPL. Any CliConfig field can be passed as a keyword
    override. Returns the Cli once it exits.
    """
    cli = Cli(agent, name=name, model=model, config=config, **overrides)
    cli.start(args=args, prompt=prompt)
    return cli
