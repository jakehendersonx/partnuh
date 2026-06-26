"""The REPL: read multi-line input, stream the agent's reply, loop.

`run(agent)` is the one-call entry point. It runs interactively, or one-shot if
command-line args (or an explicit prompt) are given.
"""

from __future__ import annotations

import itertools
import os
import shutil
import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from rich.console import Console

from prompt_toolkit.completion import FuzzyCompleter, NestedCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style

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
            "reset": self._reset,
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
        console.print()
        console.print("[#888888]/tools[/#888888] — list available tools")
        console.print("[#888888]/reset[/#888888] — clear conversation history")
        for name in (self.config.commands or {}):
            console.print(f"[#888888]/{name.lstrip('/')}[/#888888] — (custom)")
        console.print("[#888888]/help[/#888888]  — show commands")
        console.print("[#888888]/quit[/#888888]  — exit")
        console.print()
        return CommandResult(handled=True)

    def _quit(self, _disp, _args) -> CommandResult:
        return CommandResult(handled=True, should_exit=True)

    def _reset(self, _disp, _args) -> CommandResult:
        reset = getattr(self.agent, "reset", None)
        if callable(reset):
            reset(self.session_id)
            console.print("[green]✓[/green] conversation reset\n")
        else:
            console.print("[yellow]This agent doesn't support reset.[/yellow]\n")
        return CommandResult(handled=True)

    def _tools(self, _disp, _args) -> CommandResult:
        tools = list(getattr(self.agent, "tools", []) or [])
        if not tools:
            console.print("[yellow]No tools configured (chat-only).[/yellow]\n")
            return CommandResult(handled=True)
        console.print("\n[bold cyan]Available Tools:[/bold cyan]\n")
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

def display_banner(agent: CliAgent) -> None:
    from rich.panel import Panel

    n_tools = len(getattr(agent, "tools", []) or [])
    content = (
        f"[dim]agent:[/dim] {getattr(agent, 'name', 'agent')}\n"
        f"[dim]model:[/dim] {getattr(agent, 'model', '?')}\n"
        f"[dim]tools:[/dim] {n_tools or 'none (chat-only)'}\n"
        f"[dim]directory:[/dim] {os.getcwd()}"
    )
    visible = content.replace("[dim]", "").replace("[/dim]", "")
    width = min(max(max(len(l) for l in visible.splitlines()) + 4, 50), 120)
    console.print()
    console.print(Panel(content, border_style="dim", width=width))


def stream_response(agent: CliAgent, prompt: str, session_id: str, config: CliConfig) -> None:
    pacer = Pacer(console, stream_speed=config.stream_speed, show_tool_calls=config.show_tool_calls)
    try:
        events = agent.stream(prompt, session_id)
        first = None
        with console.status("[blue]Thinking...[/blue]", spinner="dots", spinner_style="dim"):
            for ev in events:
                first = ev
                break
        if first is None:
            console.print()
            return
        pacer.render(itertools.chain([first], events))
    except Exception as e:  # noqa: BLE001 - surface any adapter error to the user
        console.print(f"\n[red]Error: {e}[/red]")
        return
    console.print("\n")


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def run_interactive(agent: CliAgent, session_id: str = "main_session", config: Optional[CliConfig] = None) -> None:
    config = config or CliConfig()
    dispatcher = CommandDispatcher(agent, config, session_id)

    if config.banner:
        display_banner(agent)
    dispatcher._help(None, None)

    try:
        completer = FuzzyCompleter(NestedCompleter.from_nested_dict(dispatcher.completions()))
    except AttributeError:
        completer = FuzzyCompleter(NestedCompleter(dispatcher.completions()))

    style = Style.from_dict({"prompt": "fg:#888888"})
    prompt_tokens = [("class:prompt", config.prompt_str)]
    kb = build_key_bindings()
    session = PromptSession(style=style, completer=completer, key_bindings=kb)

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
                width = shutil.get_terminal_size(fallback=(80, 20)).columns
                rule = "[dim]" + "-" * min(width, 120) + "[/dim]"
                console.print(rule)
                stream_response(agent, text, session_id, config)
                console.print(rule)
    except KeyboardInterrupt:
        pass


def run_once(agent: CliAgent, prompt: str, session_id: str = "main_session", config: Optional[CliConfig] = None) -> None:
    stream_response(agent, prompt, session_id, config or CliConfig())


def run(agent: CliAgent, config: Optional[CliConfig] = None, args: Optional[List[str]] = None, prompt: Optional[str] = None) -> None:
    """Run the CLI. One-shot if `prompt`/`args` given, else interactive."""
    config = config or CliConfig()
    if args is None:
        args = sys.argv[1:]
    try:
        if prompt is not None:
            run_once(agent, prompt, config=config)
        elif args:
            run_once(agent, " ".join(args), config=config)
        else:
            run_interactive(agent, config=config)
    except KeyboardInterrupt:
        sys.exit(130)
