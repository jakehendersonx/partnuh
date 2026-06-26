"""Simplest partnuh usage: a streaming chat over OpenRouter, no tools.

    export OPENROUTER_API_KEY=sk-or-...
    python examples/chat.py
"""

import partnuh

agent = partnuh.AgentSpec(
    name="Private Caller",
    model="openai/gpt-5.4-nano",
    system_prompt="You are fast and concise.",
).build()

partnuh.run(agent)
