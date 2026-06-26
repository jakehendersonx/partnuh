"""The contract the CLI plugs into.

There is no universal in-process agent object shared across smolagents,
pydantic-ai, the OpenAI Agents SDK, LangGraph, etc. So partnuh defines its own
minimal structural type and ships adapters that wrap each framework into it.

Anything with ``name``, ``model``, ``tools`` and a ``stream()`` generator
satisfies ``CliAgent`` — including hand-rolled objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol, Sequence, Union, runtime_checkable

from .events import Event


@dataclass
class ToolInfo:
    """Display metadata for a tool (for the banner and /tools)."""
    name: str
    description: str = ""


@runtime_checkable
class CliAgent(Protocol):
    """Minimal interface the partnuh CLI needs from an agent."""

    name: str
    model: str
    tools: Sequence[ToolInfo]

    def stream(self, prompt: str, session_id: str) -> Iterator[Union[Event, str]]:
        """Yield Events (or bare strings) as the agent responds."""
        ...

    # Optional: agents may implement `reset(session_id)` to clear history.
    # The CLI duck-types it; it is not required by the protocol.
