"""private-caller, rebuilt on partnuh — the whole app, minus the partnuh parts.

This is a complete agent CLI. Compare it to the original private-caller, which
was four files:

    main.py            -> the bottom of this file (load env, build, run)
    cli.py             -> GONE. partnuh.run() is the multi-line streaming REPL.
    agent.py           -> GONE. AgentSpec(backend="openrouter") is the OpenRouter
                          client + streaming + session memory.
    system_prompt.txt  -> SYSTEM_PROMPT below (the only truly app-specific bit).

So "how to run an agent" is: describe the agent, hand it to partnuh.

Setup / run locally:

    cd partnuh
    python3 -m venv .venv
    .venv/bin/pip install -e ".[openai,dotenv]"   # or ".[all]"
    cp .env.template .env                          # add your OPENROUTER_API_KEY
    .venv/bin/python examples/private_caller.py            # interactive
    .venv/bin/python examples/private_caller.py "hello"    # one-shot
"""

# --- env (was main.py's load_dotenv) ---------------------------------------
try:
    from dotenv import load_dotenv

    load_dotenv()  # reads .env from the project root
except ImportError:
    pass

import partnuh

# --- the agent's persona (was system_prompt.txt) ---------------------------
SYSTEM_PROMPT = """\
You are Private Caller, a fast and concise assistant.

Answer directly and briefly. Skip preamble and filler. When a question
has a short answer, give the short answer. You favor speed and clarity
over exhaustive detail."""

# --- describe the agent (was all of agent.py) ------------------------------
agent = partnuh.AgentSpec(
    name="Private Caller",
    model="openai/gpt-5.4-nano",   # OpenRouter model id
    backend="openrouter",          # OpenAI SDK -> OpenRouter, uses $OPENROUTER_API_KEY
    system_prompt=SYSTEM_PROMPT,
    temperature=0.3,
).build()

# --- run it (was all of cli.py + main.py's entry) --------------------------
if __name__ == "__main__":
    partnuh.run(agent, config=partnuh.CliConfig(stream_speed=0.0))
