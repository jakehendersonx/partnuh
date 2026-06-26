"""partnuh — a streaming terminal REPL for any agent.

Build your agent however you like, then hand it to ``wrap`` — one line, you get
a full streaming CLI. partnuh is purely the aesthetic layer; it imports no agent
framework of its own.

    import partnuh
    from smolagents import ToolCallingAgent, OpenAIServerModel

    agent = ToolCallingAgent(tools=[...], model=OpenAIServerModel(...))
    partnuh.wrap(agent, name="Private Caller")

No API key handy? `partnuh.wrap(partnuh.demo_agent())` streams a canned reply
with no model or network.
"""

from __future__ import annotations

from .adapt import adapt
from .adapters import from_callable, from_smolagents
from .cli import Cli, wrap
from .demo import demo_agent
from .config import CliConfig
from .events import Done, Error, Event, TextDelta, ToolCallStarted, ToolResult, normalize
from .presets import Box, Cursor, Prompt, Separator, Spinner
from .protocol import CliAgent, ToolInfo

__version__ = "0.0.4"

__all__ = [
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
    "Prompt",
    "Cursor",
    "Spinner",
    "Box",
    "Separator",
    "adapt",
    "demo_agent",
    "from_smolagents",
    "from_callable",
    "__version__",
]
