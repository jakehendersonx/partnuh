"""Run partnuh with a made-up agent — NO API key, NO network, NO framework.

    python examples/fake.py

This is the fastest way to try the interface itself: it streams a canned reply
(and fakes a tool call) so you can see the multi-line REPL, token streaming, the
stream-speed pacing, and the tool-call markers without any credentials.

It works by handing partnuh.from_callable() a plain generator that yields
Events. That generator IS the agent, as far as the CLI is concerned.
"""

import partnuh
from partnuh import TextDelta, ToolCallStarted, ToolResult, ToolInfo


def fake_agent(prompt: str, session_id: str):
    """A stand-in agent: pretend to call a tool, then answer word by word."""
    # Show that tool-call markers render, even with no real tools.
    yield ToolCallStarted("echo", {"text": prompt})
    yield ToolResult("echo", prompt)

    reply = (
        f"You said: {prompt!r}.\n\n"
        "I'm a made-up agent — no model, no key, no network. "
        "Swap me for AgentSpec(...).build() or from_smolagents(...) when you're "
        "ready for a real one."
    )
    for word in reply.split(" "):
        yield TextDelta(word + " ")


agent = partnuh.from_callable(
    fake_agent,
    name="Make-Believe",
    model="pretend-1",
    tools=[ToolInfo("echo", "Echoes your input back.")],
)

# stream_speed > 0 gives a visible typewriter effect (the canned text arrives
# instantly, so this is purely cosmetic pacing — try 0.0 vs 1.0).
partnuh.run(agent, config=partnuh.CliConfig(stream_speed=0.4))
