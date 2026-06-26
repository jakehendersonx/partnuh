"""Basic partnuh example — a smolagents agent in a streaming terminal CLI.

partnuh is just the aesthetic layer. You build your agent the normal smolagents
way, then hand it to partnuh.run(). See README.md for setup.
"""

import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

import partnuh

load_dotenv()  # reads .env in this directory


# A tool the agent can weave in.
@tool
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: first integer
        b: second integer
    """
    return a + b


# Build the agent the normal smolagents way (OpenRouter via OpenAIServerModel).
model = OpenAIServerModel(
    model_id=os.environ.get("PARTNUH_MODEL", "openai/gpt-5.4-nano"),
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
agent = ToolCallingAgent(tools=[add], model=model, stream_outputs=True, max_steps=4)


# Hand it to partnuh — wrap it in a CLI, then run the streaming REPL.
if __name__ == "__main__":
    partnuh.wrap(agent, name="Basic Agent").run()
