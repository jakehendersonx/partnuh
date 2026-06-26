"""Auto-wrap whatever you hand to partnuh into a CliAgent.

This is what lets ``partnuh.run(smol)`` "just work": you build your agent with
its own dependencies and pass it straight in. partnuh stays purely aesthetic and
imports no framework — detection is by module name and duck-typing only.

Resolution order:
  1. Already a CliAgent (has a callable ``stream`` + name/model/tools) -> as-is.
  2. A smolagents agent (its class lives in the ``smolagents`` package) -> wrap.
  3. A plain ``fn(prompt, session_id) -> Iterator[Event|str]`` -> wrap.
  4. Otherwise: a clear error telling you how to wrap it yourself.
"""

from __future__ import annotations

from typing import Optional


def _is_cli_agent(obj) -> bool:
    return (
        callable(getattr(obj, "stream", None))
        and hasattr(obj, "name")
        and hasattr(obj, "model")
        and hasattr(obj, "tools")
    )


def _root_module(obj) -> str:
    return (type(obj).__module__ or "").split(".")[0]


def adapt(agent, *, name: Optional[str] = None, model: Optional[str] = None):
    """Return a CliAgent for ``agent``, wrapping a known framework if needed."""
    if _is_cli_agent(agent):
        return agent

    root = _root_module(agent)

    if root == "smolagents":
        from .adapters import from_smolagents

        display_name = name or getattr(agent, "name", None) or "agent"
        return from_smolagents(agent, name=display_name, model=model)

    if callable(agent):
        from .adapters import from_callable

        return from_callable(agent, name=name or "agent", model=model or "custom")

    raise TypeError(
        f"partnuh doesn't know how to run a "
        f"{type(agent).__module__}.{type(agent).__name__}. Pass a CliAgent, a "
        "smolagents agent, or a stream function fn(prompt, session_id) — or wrap "
        "it yourself with partnuh.from_callable()."
    )
