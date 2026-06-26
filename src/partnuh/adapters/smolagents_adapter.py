"""Adapter: wrap a smolagents agent as a partnuh CliAgent.

Verified against smolagents 1.26 with a ToolCallingAgent on OpenRouter. Two
things this adapter owns:

1. Silencing smolagents' own console. With ``stream_outputs=True`` it drives a
   rich Live display that writes straight to its logger's console, independent
   of ``verbosity_level``. We hand it a logger whose console points at a null
   sink so partnuh fully owns the terminal.
2. Translating smolagents' event stream into partnuh Events:
       ChatMessageStreamDelta.content -> TextDelta
       ToolCall                       -> ToolCallStarted
       ToolOutput (non-final)         -> ToolResult
       FinalAnswerStep.output         -> TextDelta (only if nothing streamed)

smolagents' own ``name`` must be a Python identifier (it's for managed-agent
routing), so the display name is supplied here, not read off the agent.
"""

from __future__ import annotations

import os
from typing import Iterator, Optional, Sequence

from ..events import Error, Event, TextDelta, ToolCallStarted, ToolResult
from ..protocol import ToolInfo


class SmolagentsAgent:
    """A CliAgent that drives a smolagents agent's streaming run."""

    def __init__(self, agent, *, name: str, model: Optional[str] = None, reset_each_turn: bool = False):
        self._agent = agent
        self.name = name
        self.model = model or getattr(getattr(agent, "model", None), "model_id", "unknown")
        raw_tools = getattr(agent, "tools", {}) or {}
        self.tools: Sequence[ToolInfo] = [
            ToolInfo(n, getattr(t, "description", "") or "")
            for n, t in raw_tools.items()
            if n != "final_answer"
        ]
        self._reset = reset_each_turn
        self._silence()

    def _silence(self) -> None:
        """Point smolagents' console at /dev/null so partnuh owns output.

        We must replace the logger on BOTH the agent and its monitor — the
        monitor caches the logger from construction and is what prints the
        per-step "[Step N: Duration ...]" telemetry lines.
        """
        try:
            from rich.console import Console
            from smolagents import AgentLogger, LogLevel

            null_logger = AgentLogger(level=LogLevel.OFF, console=Console(file=open(os.devnull, "w")))
            self._agent.logger = null_logger
            monitor = getattr(self._agent, "monitor", None)
            if monitor is not None and hasattr(monitor, "logger"):
                monitor.logger = null_logger
        except Exception:
            pass

    def reset(self, session_id: str = "main_session") -> None:
        # smolagents resets memory per run via reset=True; nothing persistent to clear.
        pass

    def stream(self, prompt: str, session_id: str = "main_session") -> Iterator[Event]:
        try:
            from smolagents import ChatMessageStreamDelta, FinalAnswerStep
        except Exception as e:  # pragma: no cover
            yield Error(f"smolagents not installed: {e}")
            return

        streamed_text = False
        final_output = None
        try:
            for ev in self._agent.run(prompt, stream=True, reset=self._reset):
                cls = type(ev).__name__
                if isinstance(ev, ChatMessageStreamDelta):
                    if ev.content:
                        streamed_text = True
                        yield TextDelta(ev.content)
                elif cls == "ToolCall":
                    # final_answer is smolagents' return mechanism, not a real tool.
                    if getattr(ev, "name", "") != "final_answer":
                        yield ToolCallStarted(getattr(ev, "name", ""), getattr(ev, "arguments", None))
                elif cls == "ToolOutput":
                    if not getattr(ev, "is_final_answer", False):
                        tc = getattr(ev, "tool_call", None)
                        tool_name = getattr(tc, "name", "") if tc else ""
                        yield ToolResult(tool_name, getattr(ev, "output", None))
                elif isinstance(ev, FinalAnswerStep):
                    final_output = ev.output
        except Exception as e:  # noqa: BLE001
            yield Error(str(e))
            return

        # If the agent routed its answer through final_answer (ToolCallingAgent),
        # no text deltas streamed — surface the final answer now.
        if not streamed_text and final_output is not None:
            yield TextDelta(str(final_output))


def from_smolagents(agent, *, name: str, model: Optional[str] = None, reset_each_turn: bool = False) -> SmolagentsAgent:
    """Wrap a smolagents agent (CodeAgent/ToolCallingAgent) as a CliAgent."""
    return SmolagentsAgent(agent, name=name, model=model, reset_each_turn=reset_each_turn)
