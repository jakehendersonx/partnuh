"""partnuh wrapping a smolagents ToolCallingAgent on OpenRouter.

    cp .env.template .env   # then add your OPENROUTER_API_KEY
    pip install "partnuh[smolagents]"
    python examples/smol.py

(No key handy? Run examples/fake.py instead — it needs none.)
"""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()  # picks up .env from the project root
except ImportError:
    pass

import partnuh
from smolagents import OpenAIServerModel, ToolCallingAgent, tool


@tool
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: first integer
        b: second integer
    """
    return a + b


model = OpenAIServerModel(
    model_id="openai/gpt-5.4-nano",
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

smol = ToolCallingAgent(tools=[add], model=model, stream_outputs=True, max_steps=4)

agent = partnuh.from_smolagents(smol, name="Private Caller")
partnuh.run(agent)
