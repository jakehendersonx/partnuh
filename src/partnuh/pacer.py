"""Renders an Event stream to the terminal, with optional speed control."""

from __future__ import annotations

import sys
import time
from typing import Any, Iterable, Optional, Union

from .events import (
    Done,
    Error,
    Event,
    TextDelta,
    ToolCallStarted,
    ToolResult,
    normalize,
)

# Seconds-per-character at stream_speed = 1.0 (slowest typewriter).
MAX_DELAY = 0.04


def _fmt_args(args: Optional[dict]) -> str:
    if not args:
        return ""
    return ", ".join(f"{k}={v!r}" for k, v in args.items())


class Pacer:
    """Consume an iterator of Events (or strings) and write to the terminal.

    stream_speed in [0.0, 1.0]: 0.0 flushes text as received; higher values
    drip characters out at a steady rate (a typewriter feel that also smooths
    bursty chunks).
    """

    def __init__(self, console, stream_speed: float = 0.0, show_tool_calls: bool = True):
        self.console = console
        self.delay = max(0.0, min(1.0, stream_speed)) * MAX_DELAY
        self.show_tool_calls = show_tool_calls

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
        for raw in events:
            ev = normalize(raw)
            if isinstance(ev, TextDelta):
                if ev.text:
                    printed = True
                    self._write_text(ev.text)
            elif isinstance(ev, ToolCallStarted):
                if self.show_tool_calls:
                    self.console.print(f"[dim]⚙ {ev.name}({_fmt_args(ev.args)})[/dim]")
            elif isinstance(ev, ToolResult):
                if self.show_tool_calls:
                    out = str(ev.output)
                    if len(out) > 200:
                        out = out[:200] + "…"
                    self.console.print(f"[dim]→ {out}[/dim]")
            elif isinstance(ev, Error):
                self.console.print(f"\n[red]Error: {ev.message}[/red]")
            elif isinstance(ev, Done):
                pass
        return printed
