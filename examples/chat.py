"""Simplest real usage: a streaming chat over OpenRouter, no tools.

    cp .env.template .env   # then add your OPENROUTER_API_KEY
    python examples/chat.py

(No key handy? Run examples/fake.py instead — it needs none.)
"""

try:
    from dotenv import load_dotenv

    load_dotenv()  # picks up .env from the project root
except ImportError:
    pass

import partnuh

agent = partnuh.AgentSpec(
    name="Private Caller",
    model="openai/gpt-5.4-nano",
    system_prompt="You are fast and concise.",
).build()

partnuh.run(agent)
