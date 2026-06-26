"""partnuh — a streaming terminal REPL for any agent.

    import partnuh

    agent = partnuh.AgentSpec(name="Private Caller", model="openai/gpt-5.4-nano").build()
    partnuh.run(agent)

Or wrap an existing agent:

    from smolagents import ToolCallingAgent
    agent = partnuh.from_smolagents(my_smol_agent, name="Private Caller")
    partnuh.run(agent)
"""

from __future__ import annotations

from .adapt import adapt
from .adapters import from_callable, from_openai, from_smolagents
from .cli import Cli, run, run_interactive, run_once, wrap
from .config import CliConfig
from .events import Done, Error, Event, TextDelta, ToolCallStarted, ToolResult, normalize
from .protocol import CliAgent, ToolInfo
from .spec import AgentSpec

__version__ = "0.0.3"

__all__ = [
    "AgentSpec",
    "CliAgent",
    "CliConfig",
    "ToolInfo",
    "Event",
    "TextDelta",
    "ToolCallStarted",
    "ToolResult",
    "Error",
    "Done",
    "normalize",
    "wrap",
    "Cli",
    "run",
    "run_interactive",
    "run_once",
    "adapt",
    "from_openai",
    "from_smolagents",
    "from_callable",
    "__version__",
]
