"""A basic agent on partnuh — bring your own agent, partnuh makes it a CLI.

partnuh is just the aesthetic layer: the streaming, multi-line terminal REPL.
You build your agent with its own dependencies (here, smolagents), and hand it
straight to partnuh. There's no partnuh-specific agent definition to learn —
partnuh.run() auto-wraps whatever you pass.

Setup / run locally:

    cd partnuh
    python3 -m venv .venv
    .venv/bin/pip install -e ".[smolagents,dotenv]"
    cp .env.template .env                            # add your OPENROUTER_API_KEY
    .venv/bin/python examples/basic_agent.py             # interactive
    .venv/bin/python examples/basic_agent.py "21 + 21?"  # one-shot
"""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()  # reads .env from the project root
except ImportError:
    pass

import partnuh
from smolagents import OpenAIServerModel, ToolCallingAgent, tool


# --- a tool the agent can weave in -----------------------------------------
@tool
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: first integer
        b: second integer
    """
    return a + b


# --- build YOUR agent, with YOUR deps. partnuh is not involved here. -------
model = OpenAIServerModel(
    model_id="openai/gpt-5.4-nano",
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
agent = ToolCallingAgent(tools=[add], model=model, stream_outputs=True, max_steps=4)


# --- hand it to partnuh. It just works (auto-wrapped). ---------------------
if __name__ == "__main__":
    partnuh.run(agent, name="Private Caller")
