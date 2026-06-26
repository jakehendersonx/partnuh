"""`partnuh` console entry point — a ready-to-run chat over OpenRouter.

    export OPENROUTER_API_KEY=sk-or-...
    partnuh                       # interactive
    partnuh "what's 2+2?"         # one-shot
    PARTNUH_MODEL=openai/gpt-5-nano partnuh

This is a convenience demo of the library; for real use, import partnuh and
build your own agent/spec.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    # Optional .env convenience if python-dotenv is installed.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass

    from .cli import wrap

    if not os.environ.get("OPENROUTER_API_KEY"):
        # No key? Run the offline demo agent so `partnuh` still does something.
        print("No OPENROUTER_API_KEY set — running the offline demo agent.", file=sys.stderr)
        from .demo import demo_agent

        wrap(demo_agent(name="partnuh demo"))
        return

    from .spec import AgentSpec

    model = os.environ.get("PARTNUH_MODEL", "openai/gpt-5.4-nano")
    agent = AgentSpec(name="partnuh", model=model, backend="openrouter").build()
    wrap(agent)


if __name__ == "__main__":
    main()
