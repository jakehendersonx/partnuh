"""Adapters bridge concrete agent frameworks to the CliAgent protocol.

The smolagents import is lazy, so partnuh has no hard dependency on it: install
it with `partnuh[smolagents]` (or bring your own via from_callable).
"""

from __future__ import annotations

from typing import Callable, Iterator, Optional, Sequence, Union

from ..events import Event
from ..protocol import ToolInfo


def from_smolagents(agent, *, name: str, model: Optional[str] = None, reset_each_turn: bool = False):
    """Wrap a smolagents agent as a CliAgent."""
    from .smolagents_adapter import from_smolagents as _impl

    return _impl(agent, name=name, model=model, reset_each_turn=reset_each_turn)


def from_callable(
    fn: Callable[[str, str], Iterator[Union[Event, str]]],
    *,
    name: str,
    model: str = "custom",
    tools: Optional[Sequence[ToolInfo]] = None,
):
    """Wrap any ``fn(prompt, session_id) -> Iterator[Event|str]`` as a CliAgent."""

    class _CallableAgent:
        def __init__(self):
            self.name = name
            self.model = model
            self.tools = list(tools or [])

        def stream(self, prompt: str, session_id: str = "main_session"):
            return fn(prompt, session_id)

    return _CallableAgent()


__all__ = ["from_smolagents", "from_callable"]
