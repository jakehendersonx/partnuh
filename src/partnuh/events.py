"""The universal streaming port.

Every adapter, whatever framework it wraps, translates its native stream into
this small set of events. The CLI/Pacer only ever has to understand these.
A bare ``str`` yielded by an adapter is treated as a ``TextDelta``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union


@dataclass
class TextDelta:
    """A chunk of assistant text to print (token, sentence, whatever size)."""
    text: str


@dataclass
class ToolCallStarted:
    """The agent decided to call a tool."""
    name: str
    args: Optional[Dict[str, Any]] = None


@dataclass
class ToolResult:
    """A tool returned a result."""
    name: str
    output: Any = None


@dataclass
class Error:
    """Something went wrong mid-stream."""
    message: str


@dataclass
class Done:
    """End of the response (optional; the stream ending also signals done)."""
    pass


Event = Union[TextDelta, ToolCallStarted, ToolResult, Error, Done]


def normalize(item: Union[Event, str]) -> Event:
    """Coerce a raw yielded item into an Event (str -> TextDelta)."""
    if isinstance(item, str):
        return TextDelta(item)
    return item
