"""Renders an Event stream to the terminal, with optional speed control."""

from __future__ import annotations

import sys
import time
from typing import Iterable, Optional, Union

from rich.text import Text

from .events import (
    Done,
    Error,
    Event,
    TextDelta,
    ToolCallStarted,
    ToolResult,
    normalize,
)


def _fmt_args(args: Optional[dict]) -> str:
    if not args:
        return ""
    return ", ".join(f"{k}={v!r}" for k, v in args.items())


class Pacer:
    """Consume an iterator of Events (or strings) and write to the terminal.

    `delay` is seconds-per-character: 0 flushes text as received; higher values
    drip characters out at a steady rate (a typewriter feel that also smooths
    bursty chunks).
    """

    def __init__(
        self,
        console,
        delay: float = 0.0,
        show_tool_calls: bool = True,
        tool_call_prefix: str = "⚙ ",
        tool_result_prefix: str = "→ ",
        tool_style: str = "dim",
    ):
        self.console = console
        self.delay = max(0.0, delay)
        self.show_tool_calls = show_tool_calls
        self.tool_call_prefix = tool_call_prefix
        self.tool_result_prefix = tool_result_prefix
        self.tool_style = tool_style

    def _write_text(self, text: str) -> None:
        if self.delay <= 0:
            sys.stdout.write(text)
            sys.stdout.flush()
            return
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(self.delay)

    def render(self, events: Iterable[Union[Event, str]]) -> bool:
        """Render the stream. Returns True if any text was printed."""
        printed = False
        st = self.tool_style
        for raw in events:
            ev = normalize(raw)
            if isinstance(ev, TextDelta):
                if ev.text:
                    printed = True
                    self._write_text(ev.text)
            elif isinstance(ev, ToolCallStarted):
                if self.show_tool_calls:
                    # Text (not markup) so prefixes/args containing [..] don't get
                    # parsed as rich tags.
                    self.console.print(Text(f"{self.tool_call_prefix}{ev.name}({_fmt_args(ev.args)})", style=st))
            elif isinstance(ev, ToolResult):
                if self.show_tool_calls:
                    out = str(ev.output)
                    if len(out) > 200:
                        out = out[:200] + "…"
                    self.console.print(Text(f"{self.tool_result_prefix}{out}", style=st))
            elif isinstance(ev, Error):
                self.console.print(Text(f"\nError: {ev.message}", style="red"))
            elif isinstance(ev, Done):
                pass
        return printed
