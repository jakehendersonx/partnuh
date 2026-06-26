"""A basic agent on partnuh — a complete agent CLI in a few lines.

This is the whole app. Everything that used to be hand-written CLI/streaming
plumbing is now provided by partnuh:

    the multi-line streaming REPL   -> partnuh.run()
    the OpenRouter client + memory  -> AgentSpec(backend="openrouter")
    your only job                   -> describe the agent (persona + model)

So "how to run an agent" is: describe it, hand it to partnuh.

Setup / run locally:

    cd partnuh
    python3 -m venv .venv
    .venv/bin/pip install -e ".[openai,dotenv]"   # or ".[all]"
    cp .env.template .env                          # add your OPENROUTER_API_KEY
    .venv/bin/python examples/basic_agent.py            # interactive
    .venv/bin/python examples/basic_agent.py "hello"    # one-shot
"""

# --- env -------------------------------------------------------------------
try:
    from dotenv import load_dotenv

    load_dotenv()  # reads .env from the project root
except ImportError:
    pass

import partnuh

# --- the agent's persona ---------------------------------------------------
SYSTEM_PROMPT = """\
You are Private Caller, a fast and concise assistant.

Answer directly and briefly. Skip preamble and filler. When a question
has a short answer, give the short answer. You favor speed and clarity
over exhaustive detail."""

# --- describe the agent ----------------------------------------------------
agent = partnuh.AgentSpec(
    name="Private Caller",
    model="openai/gpt-5.4-nano",   # OpenRouter model id
    backend="openrouter",          # OpenAI SDK -> OpenRouter, uses $OPENROUTER_API_KEY
    system_prompt=SYSTEM_PROMPT,
    temperature=0.3,
).build()

# --- run it ----------------------------------------------------------------
if __name__ == "__main__":
    partnuh.run(agent, config=partnuh.CliConfig(stream_speed=0.0))
